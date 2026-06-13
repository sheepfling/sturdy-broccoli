"""OMT XML serialization helpers for ``hla2010.fom``."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from typing import Any, Callable

from ._fom_models import (
    ArrayDatatypeSpec,
    BasicDatatypeSpec,
    EnumeratedDatatypeSpec,
    FixedRecordDatatypeSpec,
    FOMModule,
    InteractionClassSpec,
    ObjectClassSpec,
    SimpleDatatypeSpec,
    VariantRecordDatatypeSpec,
)

_IEEE_1516_2010_NAMESPACE = "http://standards.ieee.org/IEEE1516-2010"
_XML_SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
_DEFAULT_OMT_SCHEMA_LOCATION = (
    f"{_IEEE_1516_2010_NAMESPACE} "
    "http://standards.ieee.org/downloads/1516/1516.2-2010/IEEE1516-OMT-2010.xsd"
)
_DEFAULT_SWITCH_SETTINGS = {
    "autoProvide": "false",
    "conveyRegionDesignatorSets": "false",
    "conveyProducingFederate": "false",
    "serviceReporting": "false",
    "exceptionReporting": "true",
    "delaySubscriptionEvaluation": "false",
    "automaticResignAction": "DeleteObjects",
}
_STRICT_OMT_TRANSPORTATION_RELIABILITY = {
    "HLAreliable": "Yes",
    "HLAbestEffort": "No",
}
_NA_DATATYPE_MARKERS = {"", "NA", "N/A"}


def _today_iso_date() -> str:
    return date.today().isoformat()


def _serializer_referenced_datatype_names(module: FOMModule) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()

    def register(name: str | None) -> None:
        value = (name or "").strip()
        if not value or value in _NA_DATATYPE_MARKERS or value in seen:
            return
        seen.add(value)
        names.append(value)

    for name in module.datatype_names:
        register(name)
    register(module.time_stamp_datatype)
    register(module.lookahead_datatype)
    for metadata in module.tag_representations.values():
        register(metadata.get("datatype"))
    for metadata in module.synchronization_points.values():
        register(metadata.get("tag_datatype"))
    for spec in module.simple_datatypes.values():
        register(spec.name)
        register(spec.representation)
    for spec in module.enumerated_datatypes.values():
        register(spec.name)
        register(spec.representation)
    for spec in module.array_datatypes.values():
        register(spec.name)
        register(spec.data_type)
    for spec in module.fixed_record_datatypes.values():
        register(spec.name)
        for field in spec.fields:
            register(field.data_type)
    for spec in module.variant_record_datatypes.values():
        register(spec.name)
        register(spec.data_type)
        for alternative in spec.alternatives:
            register(alternative.data_type)
    return tuple(names)


def _serializer_datatype_sections(
    module: FOMModule,
    *,
    standard_catalog: dict[str, Any],
) -> tuple[
    dict[str, BasicDatatypeSpec],
    dict[str, SimpleDatatypeSpec],
    dict[str, EnumeratedDatatypeSpec],
    dict[str, ArrayDatatypeSpec],
    dict[str, FixedRecordDatatypeSpec],
    dict[str, VariantRecordDatatypeSpec],
]:
    local_catalog: dict[str, Any] = {
        **dict(module.basic_datatypes),
        **dict(module.simple_datatypes),
        **dict(module.enumerated_datatypes),
        **dict(module.array_datatypes),
        **dict(module.fixed_record_datatypes),
        **dict(module.variant_record_datatypes),
    }

    basics: dict[str, BasicDatatypeSpec] = dict(module.basic_datatypes)
    simples: dict[str, SimpleDatatypeSpec] = dict(module.simple_datatypes)
    enumerateds: dict[str, EnumeratedDatatypeSpec] = dict(module.enumerated_datatypes)
    arrays: dict[str, ArrayDatatypeSpec] = dict(module.array_datatypes)
    fixed_records: dict[str, FixedRecordDatatypeSpec] = dict(module.fixed_record_datatypes)
    variant_records: dict[str, VariantRecordDatatypeSpec] = dict(module.variant_record_datatypes)

    pending = list(_serializer_referenced_datatype_names(module))
    while pending:
        datatype_name = pending.pop(0)
        if not datatype_name:
            continue
        spec = local_catalog.get(datatype_name, standard_catalog.get(datatype_name))
        if spec is None:
            if datatype_name not in simples:
                simples[datatype_name] = SimpleDatatypeSpec(
                    name=datatype_name,
                    representation="HLAinteger32BE",
                    semantics="Serializer placeholder for unresolved datatype reference.",
                )
                pending.append("HLAinteger32BE")
            continue
        if isinstance(spec, BasicDatatypeSpec):
            if spec.name not in basics:
                basics[spec.name] = spec
            continue
        if isinstance(spec, SimpleDatatypeSpec):
            if spec.name in simples:
                continue
            simples[spec.name] = spec
            pending.append(spec.representation or "")
            continue
        if isinstance(spec, EnumeratedDatatypeSpec):
            if spec.name in enumerateds:
                continue
            enumerateds[spec.name] = spec
            pending.append(spec.representation or "")
            continue
        if isinstance(spec, ArrayDatatypeSpec):
            if spec.name in arrays:
                continue
            arrays[spec.name] = spec
            pending.append(spec.data_type or "")
            continue
        if isinstance(spec, FixedRecordDatatypeSpec):
            if spec.name in fixed_records:
                continue
            fixed_records[spec.name] = spec
            pending.extend(field.data_type or "" for field in spec.fields)
            continue
        if isinstance(spec, VariantRecordDatatypeSpec):
            if spec.name in variant_records:
                continue
            variant_records[spec.name] = spec
            pending.append(spec.data_type or "")
            pending.extend(alt.data_type or "" for alt in spec.alternatives)

    return basics, simples, enumerateds, arrays, fixed_records, variant_records


def _serialize_object_class_tree(parent: ET.Element, specs: tuple[ObjectClassSpec, ...]) -> None:
    specs_by_name = {spec.full_name: spec for spec in specs}
    children_by_parent: dict[str | None, list[ObjectClassSpec]] = {}
    for spec in specs:
        children_by_parent.setdefault(spec.parent_name, []).append(spec)

    root_spec = specs_by_name.get("HLAobjectRoot")
    if root_spec is None:
        root_spec = ObjectClassSpec("HLAobjectRoot")

    def emit(spec: ObjectClassSpec, parent_element: ET.Element) -> None:
        element = ET.SubElement(parent_element, f"{{{_IEEE_1516_2010_NAMESPACE}}}objectClass")
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.full_name.rsplit(".", 1)[-1]
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}sharing").text = "Neither"
        for attribute_name in spec.declared_attributes:
            attribute = ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}attribute")
            ET.SubElement(attribute, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = attribute_name
            datatype = dict(spec.attribute_datatypes).get(attribute_name)
            if datatype:
                ET.SubElement(attribute, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = datatype
            transportation = dict(spec.attribute_transportations).get(attribute_name)
            if transportation:
                ET.SubElement(attribute, f"{{{_IEEE_1516_2010_NAMESPACE}}}transportation").text = transportation
        for child_spec in sorted(children_by_parent.get(spec.full_name, []), key=lambda item: item.full_name):
            emit(child_spec, element)

    emit(root_spec, parent)


def _serialize_interaction_class_tree(parent: ET.Element, specs: tuple[InteractionClassSpec, ...]) -> None:
    specs_by_name = {spec.full_name: spec for spec in specs}
    children_by_parent: dict[str | None, list[InteractionClassSpec]] = {}
    for spec in specs:
        children_by_parent.setdefault(spec.parent_name, []).append(spec)

    root_spec = specs_by_name.get("HLAinteractionRoot")
    if root_spec is None:
        root_spec = InteractionClassSpec("HLAinteractionRoot")

    def emit(spec: InteractionClassSpec, parent_element: ET.Element) -> None:
        element = ET.SubElement(parent_element, f"{{{_IEEE_1516_2010_NAMESPACE}}}interactionClass")
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.full_name.rsplit(".", 1)[-1]
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}sharing").text = "Neither"
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}transportation").text = spec.transportation or "HLAreliable"
        ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}order").text = "Receive"
        for parameter_name in spec.declared_parameters:
            parameter = ET.SubElement(element, f"{{{_IEEE_1516_2010_NAMESPACE}}}parameter")
            ET.SubElement(parameter, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = parameter_name
            datatype = dict(spec.parameter_datatypes).get(parameter_name)
            if datatype:
                ET.SubElement(parameter, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = datatype
        for child_spec in sorted(children_by_parent.get(spec.full_name, []), key=lambda item: item.full_name):
            emit(child_spec, element)

    emit(root_spec, parent)


def serialize_fom_module(
    module: FOMModule,
    *,
    standard_catalog_factory: Callable[[], dict[str, Any]],
) -> str:
    """Serialize the implemented metadata subset of a FOM module to strict OMT XML."""

    ET.register_namespace("", _IEEE_1516_2010_NAMESPACE)
    ET.register_namespace("xsi", _XML_SCHEMA_INSTANCE_NAMESPACE)
    root = ET.Element(
        f"{{{_IEEE_1516_2010_NAMESPACE}}}objectModel",
        {
            f"{{{_XML_SCHEMA_INSTANCE_NAMESPACE}}}schemaLocation": _DEFAULT_OMT_SCHEMA_LOCATION,
        },
    )
    model_identification = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}modelIdentification")
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = module.name or "Generated OMT Module"
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}type").text = module.model_type or "FOM"
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}version").text = "1.0"
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}modificationDate").text = _today_iso_date()
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}securityClassification").text = "Unclassified"
    ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}description").text = (
        f"Serialized OMT module generated by hla2010 for {module.name or 'an unnamed module'}."
    )
    poc = ET.SubElement(model_identification, f"{{{_IEEE_1516_2010_NAMESPACE}}}poc")
    ET.SubElement(poc, f"{{{_IEEE_1516_2010_NAMESPACE}}}pocType").text = "Sponsor"
    ET.SubElement(poc, f"{{{_IEEE_1516_2010_NAMESPACE}}}pocName").text = "hla2010"

    if module.service_utilization:
        service_utilization = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}serviceUtilization")
        for service_name, attrs in dict(module.service_utilization).items():
            ET.SubElement(service_utilization, f"{{{_IEEE_1516_2010_NAMESPACE}}}{service_name}", dict(attrs))

    objects = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}objects")
    _serialize_object_class_tree(objects, module.object_classes)

    interactions = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}interactions")
    _serialize_interaction_class_tree(interactions, module.interaction_classes)

    dimensions = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}dimensions")
    for name in module.dimensions:
        dimension = ET.SubElement(dimensions, f"{{{_IEEE_1516_2010_NAMESPACE}}}dimension")
        ET.SubElement(dimension, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = name

    if module.time_stamp_datatype or module.lookahead_datatype:
        time = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}time")
        if module.time_stamp_datatype:
            time_stamp = ET.SubElement(time, f"{{{_IEEE_1516_2010_NAMESPACE}}}timeStamp")
            ET.SubElement(time_stamp, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = module.time_stamp_datatype
        if module.lookahead_datatype:
            lookahead = ET.SubElement(time, f"{{{_IEEE_1516_2010_NAMESPACE}}}lookahead")
            ET.SubElement(lookahead, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = module.lookahead_datatype

    if module.tag_representations:
        tags = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}tags")
        for category, metadata in dict(module.tag_representations).items():
            tag = ET.SubElement(tags, f"{{{_IEEE_1516_2010_NAMESPACE}}}{category}")
            if metadata.get("datatype"):
                ET.SubElement(tag, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = metadata["datatype"]
            if metadata.get("semantics"):
                ET.SubElement(tag, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = metadata["semantics"]

    if module.synchronization_points:
        synchronizations = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}synchronizations")
        for label, metadata in dict(module.synchronization_points).items():
            synchronization = ET.SubElement(synchronizations, f"{{{_IEEE_1516_2010_NAMESPACE}}}synchronizationPoint")
            ET.SubElement(synchronization, f"{{{_IEEE_1516_2010_NAMESPACE}}}label").text = label
            if metadata.get("tag_datatype"):
                ET.SubElement(synchronization, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = metadata["tag_datatype"]
            if metadata.get("capability"):
                ET.SubElement(synchronization, f"{{{_IEEE_1516_2010_NAMESPACE}}}capability").text = metadata["capability"]
            if metadata.get("semantics"):
                ET.SubElement(synchronization, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = metadata["semantics"]

    transportations = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}transportations")
    declared_transportations: list[str] = ["HLAreliable", "HLAbestEffort"]
    for name in module.transportation_names:
        if name not in declared_transportations:
            declared_transportations.append(name)
    for name in declared_transportations:
        transportation = ET.SubElement(transportations, f"{{{_IEEE_1516_2010_NAMESPACE}}}transportation")
        ET.SubElement(transportation, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = name
        ET.SubElement(transportation, f"{{{_IEEE_1516_2010_NAMESPACE}}}reliable").text = _STRICT_OMT_TRANSPORTATION_RELIABILITY.get(name, "Yes")

    switches = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}switches")
    merged_switches = dict(_DEFAULT_SWITCH_SETTINGS)
    merged_switches.update(dict(module.switch_settings))
    for name, value in merged_switches.items():
        attrs = {"isEnabled": value}
        if name == "automaticResignAction":
            attrs = {"resignAction": value}
        ET.SubElement(switches, f"{{{_IEEE_1516_2010_NAMESPACE}}}{name}", attrs)

    if module.update_rates:
        update_rates = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}updateRates")
        for name, value in dict(module.update_rates).items():
            update_rate = ET.SubElement(update_rates, f"{{{_IEEE_1516_2010_NAMESPACE}}}updateRate")
            ET.SubElement(update_rate, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = name
            ET.SubElement(update_rate, f"{{{_IEEE_1516_2010_NAMESPACE}}}rate").text = value

    (
        serializer_basic_datatypes,
        serializer_simple_datatypes,
        serializer_enumerated_datatypes,
        serializer_array_datatypes,
        serializer_fixed_record_datatypes,
        serializer_variant_record_datatypes,
    ) = _serializer_datatype_sections(module, standard_catalog=standard_catalog_factory())
    data_types = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataTypes")
    basic_data_representations = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}basicDataRepresentations")
    for spec in serializer_basic_datatypes.values():
        basic = ET.SubElement(basic_data_representations, f"{{{_IEEE_1516_2010_NAMESPACE}}}basicData")
        ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.size:
            ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}size").text = spec.size
        if spec.interpretation:
            ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}interpretation").text = spec.interpretation
        if spec.endian:
            ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}endian").text = spec.endian
        if spec.encoding:
            ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}encoding").text = spec.encoding
        if spec.semantics:
            ET.SubElement(basic, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics

    simple_data_types = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}simpleDataTypes")
    for spec in serializer_simple_datatypes.values():
        simple_data = ET.SubElement(simple_data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}simpleData")
        ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.representation:
            ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}representation").text = spec.representation
        if spec.units:
            ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}units").text = spec.units
        if spec.resolution:
            ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}resolution").text = spec.resolution
        if spec.accuracy:
            ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}accuracy").text = spec.accuracy
        if spec.semantics:
            ET.SubElement(simple_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics

    enumerated_data_types = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}enumeratedDataTypes")
    for spec in serializer_enumerated_datatypes.values():
        enumerated = ET.SubElement(enumerated_data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}enumeratedData")
        ET.SubElement(enumerated, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.representation:
            ET.SubElement(enumerated, f"{{{_IEEE_1516_2010_NAMESPACE}}}representation").text = spec.representation
        if spec.semantics:
            ET.SubElement(enumerated, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics
        for enumerator_spec in spec.enumerators:
            enumerator = ET.SubElement(enumerated, f"{{{_IEEE_1516_2010_NAMESPACE}}}enumerator")
            ET.SubElement(enumerator, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = enumerator_spec.name
            for value in enumerator_spec.values:
                ET.SubElement(enumerator, f"{{{_IEEE_1516_2010_NAMESPACE}}}value").text = value

    array_data_types = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}arrayDataTypes")
    for spec in serializer_array_datatypes.values():
        array_data = ET.SubElement(array_data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}arrayData")
        ET.SubElement(array_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.data_type:
            ET.SubElement(array_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = spec.data_type
        if spec.cardinality:
            ET.SubElement(array_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}cardinality").text = spec.cardinality
        if spec.encoding:
            ET.SubElement(array_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}encoding").text = spec.encoding
        if spec.semantics:
            ET.SubElement(array_data, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics

    fixed_record_data_types = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}fixedRecordDataTypes")
    for spec in serializer_fixed_record_datatypes.values():
        fixed_record = ET.SubElement(fixed_record_data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}fixedRecordData")
        ET.SubElement(fixed_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.encoding:
            ET.SubElement(fixed_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}encoding").text = spec.encoding
        if spec.semantics:
            ET.SubElement(fixed_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics
        for field_spec in spec.fields:
            field = ET.SubElement(fixed_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}field")
            ET.SubElement(field, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = field_spec.name
            if field_spec.data_type:
                ET.SubElement(field, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = field_spec.data_type
            if field_spec.semantics:
                ET.SubElement(field, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = field_spec.semantics

    variant_record_data_types = ET.SubElement(data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}variantRecordDataTypes")
    for spec in serializer_variant_record_datatypes.values():
        variant_record = ET.SubElement(variant_record_data_types, f"{{{_IEEE_1516_2010_NAMESPACE}}}variantRecordData")
        ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = spec.name
        if spec.discriminant:
            ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}discriminant").text = spec.discriminant
        if spec.data_type:
            ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = spec.data_type
        for alt_spec in spec.alternatives:
            alternative = ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}alternative")
            ET.SubElement(alternative, f"{{{_IEEE_1516_2010_NAMESPACE}}}enumerator").text = alt_spec.enumerator
            if alt_spec.name:
                ET.SubElement(alternative, f"{{{_IEEE_1516_2010_NAMESPACE}}}name").text = alt_spec.name
            if alt_spec.data_type:
                ET.SubElement(alternative, f"{{{_IEEE_1516_2010_NAMESPACE}}}dataType").text = alt_spec.data_type
            if alt_spec.semantics:
                ET.SubElement(alternative, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = alt_spec.semantics
        if spec.encoding:
            ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}encoding").text = spec.encoding
        if spec.semantics:
            ET.SubElement(variant_record, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = spec.semantics

    if module.notes:
        notes = ET.SubElement(root, f"{{{_IEEE_1516_2010_NAMESPACE}}}notes")
        for note_text in module.notes:
            note = ET.SubElement(notes, f"{{{_IEEE_1516_2010_NAMESPACE}}}note")
            label, separator, semantics = note_text.partition(": ")
            if separator:
                ET.SubElement(note, f"{{{_IEEE_1516_2010_NAMESPACE}}}label").text = label
                ET.SubElement(note, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = semantics
            else:
                ET.SubElement(note, f"{{{_IEEE_1516_2010_NAMESPACE}}}semantics").text = note_text

    return ET.tostring(root, encoding="unicode", xml_declaration=True)


__all__ = ["serialize_fom_module"]
