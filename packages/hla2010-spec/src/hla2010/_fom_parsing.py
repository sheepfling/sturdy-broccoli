from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from ._fom_errors import FOMResolutionError
from ._fom_models import (
    ArrayDatatypeSpec,
    BasicDatatypeSpec,
    DimensionSpec,
    EnumeratedDatatypeSpec,
    EnumeratorSpec,
    FixedRecordDatatypeSpec,
    FixedRecordFieldSpec,
    FOMModule,
    InteractionClassSpec,
    ObjectClassSpec,
    SimpleDatatypeSpec,
    VariantAlternativeSpec,
    VariantRecordDatatypeSpec,
)

try:
    from lxml import etree as LET
except ModuleNotFoundError:  # pragma: no cover - exercised via lazy runtime paths
    LET = None

_STANDARD_TIME_BY_DATATYPE_HINT = {
    "HLAfloat64BE": "HLAfloat64Time",
    "HLAfloat64LE": "HLAfloat64Time",
    "HLAinteger64BE": "HLAinteger64Time",
    "HLAinteger64LE": "HLAinteger64Time",
}
_IEEE_1516_2010_NAMESPACE = "http://standards.ieee.org/IEEE1516-2010"
_SISO_1516_2010_NAMESPACE = "http://www.sisostds.org/schemas/IEEE1516-2010"
_XML_SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
_ALLOWED_OMT_NAMESPACES = {_IEEE_1516_2010_NAMESPACE, _SISO_1516_2010_NAMESPACE}
_STANDARD_TRANSPORTATION_TYPES = {"HLAreliable", "HLAbestEffort"}
_STANDARD_UPDATE_RATE_DESIGNATORS = {"HLAdefault", "default"}
_KNOWN_SWITCH_NAMES = {
    "autoProvide",
    "conveyRegionDesignatorSets",
    "conveyProducingFederate",
    "attributeScopeAdvisory",
    "attributeRelevanceAdvisory",
    "objectClassRelevanceAdvisory",
    "interactionRelevanceAdvisory",
    "serviceReporting",
    "exceptionReporting",
    "delaySubscriptionEvaluation",
    "automaticResignAction",
}
_NA_DATATYPE_MARKERS = {"", "NA", "N/A"}
_CARDINALITY_RE = re.compile(r"(Dynamic|(\d)+|(\[(\d)+\.\.(\d)+\]))(,(Dynamic|(\d)+|(\[(\d)+\.\.(\d)+\])))*$")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _direct_children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == name]


def _child_text(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    for child in list(element):
        if _local_name(child.tag) == name:
            return (child.text or "").strip()
    return None


def _append_path(parent: str, name: str) -> str:
    if not parent:
        return name
    if name.startswith(parent + "."):
        return name
    return f"{parent}.{name}"


def _stable_union(*groups: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value and value not in seen:
                result.append(value)
                seen.add(value)
    return tuple(result)


def _stable_mapping_union(*groups: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for group in groups:
        for key, value in dict(group).items():
            if key and value and key not in result:
                result[key] = value
    return result


def _require_unique_name(container: dict[str, Any], name: str, kind: str, *, path: Path) -> None:
    if name in container:
        raise FOMResolutionError(f"Duplicate {kind} definition {name!r} in {path}", kind="read")


def _namespace_uri(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return ""


def _walk_object_class(
    element: ET.Element,
    parent: str = "",
    inherited_attributes: tuple[str, ...] = (),
    inherited_datatypes: Mapping[str, str] | None = None,
    inherited_transportations: Mapping[str, str] | None = None,
    inherited_update_rates: Mapping[str, str] | None = None,
    path: Path | None = None,
) -> list[ObjectClassSpec]:
    name = _child_text(element, "name")
    if not name:
        return []
    inherited_datatypes = dict(inherited_datatypes or {})
    inherited_transportations = dict(inherited_transportations or {})
    inherited_update_rates = dict(inherited_update_rates or {})
    full_name = _append_path(parent, name)
    declared_names: list[str] = []
    declared_datatypes: dict[str, str] = {}
    declared_transportations: dict[str, str] = {}
    declared_update_rates: dict[str, str] = {}
    for attr in _direct_children(element, "attribute"):
        attr_name = (_child_text(attr, "name") or "").strip()
        if not attr_name:
            continue
        declared_names.append(attr_name)
        data_type = (_child_text(attr, "dataType") or "").strip()
        if data_type:
            declared_datatypes[attr_name] = data_type
        transportation = (_child_text(attr, "transportation") or _child_text(attr, "transportationType") or "").strip()
        if transportation:
            declared_transportations[attr_name] = transportation
        update_rate = (
            _child_text(attr, "updateRate")
            or _child_text(attr, "updateRateDesignator")
            or _child_text(attr, "rateDesignator")
            or ""
        ).strip()
        if update_rate:
            declared_update_rates[attr_name] = update_rate
    declared = tuple(declared_names)
    available = _stable_union(inherited_attributes, declared)
    datatypes = _stable_mapping_union(inherited_datatypes, declared_datatypes)
    transportations = _stable_mapping_union(inherited_transportations, declared_transportations)
    update_rates = _stable_mapping_union(inherited_update_rates, declared_update_rates)
    result = [ObjectClassSpec(full_name, available, parent or None, declared, datatypes, transportations, update_rates)]
    child_names: dict[str, bool] = {}
    for child in _direct_children(element, "objectClass"):
        child_name = (_child_text(child, "name") or "").strip()
        if child_name and path is not None:
            _require_unique_name(child_names, child_name, "object class", path=path)
            child_names[child_name] = True
        result.extend(
            _walk_object_class(
                child,
                full_name,
                available,
                datatypes,
                transportations,
                update_rates,
                path=path,
            )
        )
    return result


def _walk_interaction_class(
    element: ET.Element,
    parent: str = "",
    inherited_parameters: tuple[str, ...] = (),
    inherited_datatypes: Mapping[str, str] | None = None,
    inherited_transportation: str | None = None,
    path: Path | None = None,
) -> list[InteractionClassSpec]:
    name = _child_text(element, "name")
    if not name:
        return []
    inherited_datatypes = dict(inherited_datatypes or {})
    full_name = _append_path(parent, name)
    transportation = (
        (_child_text(element, "transportation") or _child_text(element, "transportationType") or "").strip()
        or inherited_transportation
    )
    declared_names: list[str] = []
    declared_datatypes: dict[str, str] = {}
    for param in _direct_children(element, "parameter"):
        param_name = (_child_text(param, "name") or "").strip()
        if not param_name:
            continue
        declared_names.append(param_name)
        data_type = (_child_text(param, "dataType") or "").strip()
        if data_type:
            declared_datatypes[param_name] = data_type
    declared = tuple(declared_names)
    available = _stable_union(inherited_parameters, declared)
    datatypes = _stable_mapping_union(inherited_datatypes, declared_datatypes)
    result = [InteractionClassSpec(full_name, available, parent or None, declared, datatypes, transportation or None)]
    child_names: dict[str, bool] = {}
    for child in _direct_children(element, "interactionClass"):
        child_name = (_child_text(child, "name") or "").strip()
        if child_name and path is not None:
            _require_unique_name(child_names, child_name, "interaction class", path=path)
            child_names[child_name] = True
        result.extend(_walk_interaction_class(child, full_name, available, datatypes, transportation or None, path=path))
    return result


def _infer_time_implementation(root: ET.Element) -> str | None:
    time_section = next((child for child in list(root) if _local_name(child.tag) == "time"), None)
    if time_section is None:
        return None
    hints: list[str] = []
    for container in _direct_children(time_section, "timeStamp") + _direct_children(time_section, "lookahead"):
        data_type = _child_text(container, "dataType")
        if data_type:
            hints.append(data_type)
    for hint in hints:
        for token, implementation in _STANDARD_TIME_BY_DATATYPE_HINT.items():
            if token.lower() in hint.lower():
                return implementation
    return None


def _extract_time_datatypes(root: ET.Element) -> tuple[str | None, str | None]:
    time_section = next((child for child in list(root) if _local_name(child.tag) == "time"), None)
    if time_section is None:
        return None, None
    time_stamp = next(iter(_direct_children(time_section, "timeStamp")), None)
    lookahead = next(iter(_direct_children(time_section, "lookahead")), None)
    return _child_text(time_stamp, "dataType"), _child_text(lookahead, "dataType")


def _extract_transportation_names(root: ET.Element, *, path: Path) -> tuple[str, ...]:
    names: list[str] = []
    seen: dict[str, bool] = {}
    transportations_section = next((child for child in list(root) if _local_name(child.tag) == "transportations"), None)
    if transportations_section is None:
        return ()
    for transportation in _direct_children(transportations_section, "transportation"):
        name = _child_text(transportation, "name")
        if name:
            _require_unique_name(seen, name, "transportation type", path=path)
            seen[name] = True
            names.append(name)
    return _stable_union(names)


def _extract_update_rates(root: ET.Element, *, path: Path) -> dict[str, str]:
    rates: dict[str, str] = {}
    update_rates_section = next((child for child in list(root) if _local_name(child.tag) == "updateRates"), None)
    if update_rates_section is None:
        return rates
    for update_rate in _direct_children(update_rates_section, "updateRate"):
        name = _child_text(update_rate, "name")
        if not name:
            continue
        _require_unique_name(rates, name, "update rate", path=path)
        max_rate = (
            _child_text(update_rate, "rate")
            or _child_text(update_rate, "updateRate")
            or _child_text(update_rate, "maximumUpdateRate")
            or ""
        )
        rates[name] = max_rate
    return rates


_DATATYPE_ENTRY_TAGS = {
    "simpleData",
    "enumeratedData",
    "arrayData",
    "fixedRecordData",
    "variantRecordData",
}


def _extract_datatype_names(root: ET.Element, *, path: Path) -> tuple[str, ...]:
    names: list[str] = []
    seen: dict[str, bool] = {}
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return ()
    for container in list(data_types_section):
        for child in list(container):
            if _local_name(child.tag) == "basicData":
                name = _child_text(child, "name") or (child.attrib.get("representation") or "").strip()
                if name:
                    _require_unique_name(seen, name, "datatype", path=path)
                    seen[name] = True
                    names.append(name)
                continue
            if _local_name(child.tag) not in _DATATYPE_ENTRY_TAGS:
                continue
            name = _child_text(child, "name")
            if name:
                _require_unique_name(seen, name, "datatype", path=path)
                seen[name] = True
                names.append(name)
    return _stable_union(names)


def _extract_basic_datatypes(root: ET.Element, *, path: Path) -> dict[str, BasicDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "basicDataRepresentations"), None)
    if container is None:
        return {}
    basics: dict[str, BasicDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "basicData":
            continue
        name = (_child_text(child, "name") or child.attrib.get("representation") or "").strip()
        if not name:
            continue
        _require_unique_name(basics, name, "basic datatype", path=path)
        basics[name] = BasicDatatypeSpec(
            name=name,
            size=(_child_text(child, "size") or "").strip() or None,
            interpretation=(_child_text(child, "interpretation") or "").strip() or None,
            endian=(_child_text(child, "endian") or "").strip() or None,
            encoding=(_child_text(child, "encoding") or "").strip() or None,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
        )
    return basics


def _extract_simple_datatypes(root: ET.Element, *, path: Path) -> dict[str, SimpleDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "simpleDataTypes"), None)
    if container is None:
        return {}
    simple_types: dict[str, SimpleDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "simpleData":
            continue
        name = (_child_text(child, "name") or "").strip()
        if not name:
            continue
        _require_unique_name(simple_types, name, "simple datatype", path=path)
        simple_types[name] = SimpleDatatypeSpec(
            name=name,
            representation=(_child_text(child, "representation") or "").strip() or None,
            units=(_child_text(child, "units") or "").strip() or None,
            resolution=(_child_text(child, "resolution") or "").strip() or None,
            accuracy=(_child_text(child, "accuracy") or "").strip() or None,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
        )
    return simple_types


def _extract_enumerated_datatypes(root: ET.Element, *, path: Path) -> dict[str, EnumeratedDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "enumeratedDataTypes"), None)
    if container is None:
        return {}
    enumerated_types: dict[str, EnumeratedDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "enumeratedData":
            continue
        name = (_child_text(child, "name") or "").strip()
        if not name:
            continue
        _require_unique_name(enumerated_types, name, "enumerated datatype", path=path)
        seen_names: dict[str, bool] = {}
        seen_values: dict[str, bool] = {}
        enumerators: list[EnumeratorSpec] = []
        for enumerator in _direct_children(child, "enumerator"):
            enum_name = (_child_text(enumerator, "name") or "").strip()
            if enum_name:
                _require_unique_name(seen_names, enum_name, "enumeration name", path=path)
                seen_names[enum_name] = True
            values = tuple(value.text.strip() for value in _direct_children(enumerator, "value") if value.text and value.text.strip())
            for value in values:
                _require_unique_name(seen_values, value, "enumeration value", path=path)
                seen_values[value] = True
            if enum_name:
                enumerators.append(EnumeratorSpec(enum_name, values))
        enumerated_types[name] = EnumeratedDatatypeSpec(
            name=name,
            representation=(_child_text(child, "representation") or "").strip() or None,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
            enumerators=tuple(enumerators),
        )
    return enumerated_types


def _extract_array_datatypes(root: ET.Element, *, path: Path) -> dict[str, ArrayDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "arrayDataTypes"), None)
    if container is None:
        return {}
    array_types: dict[str, ArrayDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "arrayData":
            continue
        name = (_child_text(child, "name") or "").strip()
        if not name:
            continue
        _require_unique_name(array_types, name, "array datatype", path=path)
        cardinality = (_child_text(child, "cardinality") or "").strip() or None
        encoding = (_child_text(child, "encoding") or "").strip() or None
        if cardinality is not None and not _CARDINALITY_RE.fullmatch(cardinality):
            raise FOMResolutionError(f"Array datatype {name!r} has invalid cardinality {cardinality!r} in {path}", kind="read")
        if encoding == "HLAfixedArray" and cardinality == "Dynamic":
            raise FOMResolutionError(f"Array datatype {name!r} cannot use Dynamic cardinality with HLAfixedArray in {path}", kind="read")
        array_types[name] = ArrayDatatypeSpec(
            name=name,
            data_type=(_child_text(child, "dataType") or "").strip() or None,
            cardinality=cardinality,
            encoding=encoding,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
        )
    return array_types


def _extract_fixed_record_datatypes(root: ET.Element, *, path: Path) -> dict[str, FixedRecordDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "fixedRecordDataTypes"), None)
    if container is None:
        return {}
    fixed_records: dict[str, FixedRecordDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "fixedRecordData":
            continue
        name = (_child_text(child, "name") or "").strip()
        if not name:
            continue
        _require_unique_name(fixed_records, name, "fixed record datatype", path=path)
        fields: list[FixedRecordFieldSpec] = []
        for field in _direct_children(child, "field"):
            field_name = (_child_text(field, "name") or "").strip()
            if not field_name:
                continue
            fields.append(
                FixedRecordFieldSpec(
                    name=field_name,
                    data_type=(_child_text(field, "dataType") or "").strip() or None,
                    semantics=(_child_text(field, "semantics") or "").strip() or None,
                )
            )
        fixed_records[name] = FixedRecordDatatypeSpec(
            name=name,
            encoding=(_child_text(child, "encoding") or "").strip() or None,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
            fields=tuple(fields),
        )
    return fixed_records


def _extract_variant_record_datatypes(root: ET.Element, *, path: Path) -> dict[str, VariantRecordDatatypeSpec]:
    data_types_section = next((child for child in list(root) if _local_name(child.tag) == "dataTypes"), None)
    if data_types_section is None:
        return {}
    container = next((child for child in list(data_types_section) if _local_name(child.tag) == "variantRecordDataTypes"), None)
    if container is None:
        return {}
    variant_records: dict[str, VariantRecordDatatypeSpec] = {}
    for child in list(container):
        if _local_name(child.tag) != "variantRecordData":
            continue
        name = (_child_text(child, "name") or "").strip()
        if not name:
            continue
        _require_unique_name(variant_records, name, "variant record datatype", path=path)
        seen_alternatives: dict[str, bool] = {}
        alternatives: list[VariantAlternativeSpec] = []
        for alternative in _direct_children(child, "alternative"):
            enumerator = (_child_text(alternative, "enumerator") or "").strip()
            if enumerator:
                _require_unique_name(seen_alternatives, enumerator, "discriminant alternative", path=path)
                seen_alternatives[enumerator] = True
            alternatives.append(
                VariantAlternativeSpec(
                    enumerator=enumerator,
                    name=(_child_text(alternative, "name") or "").strip() or None,
                    data_type=(_child_text(alternative, "dataType") or "").strip() or None,
                    semantics=(_child_text(alternative, "semantics") or "").strip() or None,
                )
            )
        variant_records[name] = VariantRecordDatatypeSpec(
            name=name,
            discriminant=(_child_text(child, "discriminant") or "").strip() or None,
            data_type=(_child_text(child, "dataType") or "").strip() or None,
            encoding=(_child_text(child, "encoding") or "").strip() or None,
            semantics=(_child_text(child, "semantics") or "").strip() or None,
            alternatives=tuple(alternatives),
        )
    return variant_records


def _extract_notes(root: ET.Element) -> tuple[str, ...]:
    notes_section = next((child for child in list(root) if _local_name(child.tag) == "notes"), None)
    if notes_section is None:
        return ()
    notes: list[str] = []
    for note in _direct_children(notes_section, "note"):
        label = (_child_text(note, "label") or "").strip()
        semantics = (_child_text(note, "semantics") or "").strip()
        if label and semantics:
            notes.append(f"{label}: {semantics}")
        elif semantics:
            notes.append(semantics)
        elif label:
            notes.append(label)
    return tuple(notes)


def _extract_model_identification(root: ET.Element, *, path: Path) -> dict[str, Any]:
    model_identification = next((child for child in list(root) if _local_name(child.tag) == "modelIdentification"), None)
    if model_identification is None:
        raise FOMResolutionError(f"Object model {path} is missing required modelIdentification", kind="read")

    metadata: dict[str, Any] = {}
    keywords: list[str] = []
    pocs: list[dict[str, str]] = []
    for child in list(model_identification):
        name = _local_name(child.tag)
        if name == "keyword":
            if child.text and child.text.strip():
                keywords.append(child.text.strip())
            continue
        if name == "poc":
            poc = {
                _local_name(grandchild.tag): grandchild.text.strip()
                for grandchild in list(child)
                if grandchild.text and grandchild.text.strip()
            }
            if poc:
                pocs.append(poc)
            continue
        text = (child.text or "").strip()
        if text:
            metadata[name] = text
    if keywords:
        metadata["keywords"] = tuple(keywords)
    if pocs:
        metadata["pocs"] = tuple(pocs)
    return metadata


def _extract_service_utilization(root: ET.Element) -> dict[str, dict[str, str]]:
    service_utilization = next((child for child in list(root) if _local_name(child.tag) == "serviceUtilization"), None)
    if service_utilization is None:
        return {}
    services: dict[str, dict[str, str]] = {}
    for child in list(service_utilization):
        name = _local_name(child.tag)
        if not name:
            continue
        services[name] = {key: value for key, value in child.attrib.items() if value is not None}
    return services


def _extract_tag_representations(root: ET.Element, *, path: Path) -> dict[str, dict[str, str]]:
    tags_section = next((child for child in list(root) if _local_name(child.tag) == "tags"), None)
    if tags_section is None:
        return {}
    tags: dict[str, dict[str, str]] = {}
    for tag in list(tags_section):
        category = _local_name(tag.tag)
        if not category:
            continue
        _require_unique_name(tags, category, "tag category", path=path)
        metadata = {
            "datatype": (_child_text(tag, "dataType") or "").strip(),
            "semantics": (_child_text(tag, "semantics") or "").strip(),
        }
        tags[category] = {key: value for key, value in metadata.items() if value}
    return tags


def _extract_switch_settings(root: ET.Element) -> dict[str, str]:
    switches_section = next((child for child in list(root) if _local_name(child.tag) == "switches"), None)
    if switches_section is None:
        return {}
    settings: dict[str, str] = {}
    for switch in list(switches_section):
        name = _local_name(switch.tag)
        if not name:
            continue
        value = (
            (switch.attrib.get("isEnabled") or "").strip()
            or (switch.attrib.get("resignAction") or "").strip()
            or (switch.text or "").strip()
        )
        if value:
            settings[name] = value
    return settings


def _validate_xml_namespace_usage(root: ET.Element, *, path: Path) -> None:
    root_namespace = _namespace_uri(root.tag)
    if root_namespace and root_namespace not in _ALLOWED_OMT_NAMESPACES:
        raise FOMResolutionError(f"Unsupported objectModel namespace {root_namespace!r} in {path}", kind="read")
    for element in root.iter():
        namespace = _namespace_uri(element.tag)
        if namespace and namespace not in _ALLOWED_OMT_NAMESPACES and namespace != _XML_SCHEMA_INSTANCE_NAMESPACE:
            raise FOMResolutionError(f"Unsupported XML namespace {namespace!r} in {path}", kind="read")


def _validate_transportation_references(
    object_classes: Iterable[ObjectClassSpec],
    interaction_classes: Iterable[InteractionClassSpec],
    transportation_names: Iterable[str],
    *,
    path: Path,
) -> None:
    valid_names = set(transportation_names) | _STANDARD_TRANSPORTATION_TYPES
    for spec in object_classes:
        for attribute_name, transportation in dict(spec.attribute_transportations).items():
            if transportation not in valid_names:
                raise FOMResolutionError(
                    f"Attribute {spec.full_name}.{attribute_name} references undefined transportation type {transportation!r} in {path}",
                    kind="read",
                )
    for spec in interaction_classes:
        if spec.transportation and spec.transportation not in valid_names:
            raise FOMResolutionError(
                f"Interaction class {spec.full_name} references undefined transportation type {spec.transportation!r} in {path}",
                kind="read",
            )


def _validate_update_rate_references(object_classes: Iterable[ObjectClassSpec], update_rates: Mapping[str, str], *, path: Path) -> None:
    valid_names = set(dict(update_rates)) | _STANDARD_UPDATE_RATE_DESIGNATORS
    for spec in object_classes:
        for attribute_name, designator in dict(spec.attribute_update_rates).items():
            if designator not in valid_names:
                raise FOMResolutionError(
                    f"Attribute {spec.full_name}.{attribute_name} references undefined update rate designator {designator!r} in {path}",
                    kind="read",
                )


def _validate_switch_settings(switch_settings: Mapping[str, str], *, path: Path) -> None:
    for name in dict(switch_settings):
        if name not in _KNOWN_SWITCH_NAMES:
            raise FOMResolutionError(f"Unknown switch definition {name!r} in {path}", kind="read")


def _validate_top_level_hierarchy(
    classes: list[ET.Element],
    *,
    root_name: str,
    kind: str,
    path: Path,
) -> None:
    if not classes:
        return
    if len(classes) != 1:
        raise FOMResolutionError(
            f"{kind.capitalize()} hierarchy in {path} must declare exactly one top-level {root_name} class",
            kind="read",
        )
    declared_name = (_child_text(classes[0], "name") or "").strip()
    if declared_name != root_name:
        raise FOMResolutionError(
            f"{kind.capitalize()} hierarchy in {path} must begin at {root_name}",
            kind="read",
        )


def _validate_datatype_references(
    object_classes: Iterable[ObjectClassSpec],
    interaction_classes: Iterable[InteractionClassSpec],
    datatype_names: Iterable[str],
    simple_datatypes: Mapping[str, SimpleDatatypeSpec],
    enumerated_datatypes: Mapping[str, EnumeratedDatatypeSpec],
    array_datatypes: Mapping[str, ArrayDatatypeSpec],
    fixed_record_datatypes: Mapping[str, FixedRecordDatatypeSpec],
    variant_record_datatypes: Mapping[str, VariantRecordDatatypeSpec],
    tag_representations: Mapping[str, Mapping[str, str]],
    synchronization_points: Mapping[str, Mapping[str, str]],
    time_stamp_datatype: str | None,
    lookahead_datatype: str | None,
    *,
    path: Path,
    standard_datatype_names_factory: Callable[[], frozenset[str]],
) -> None:
    valid_names = set(datatype_names) | set(standard_datatype_names_factory())

    def require_valid(name: str | None, context: str) -> None:
        if name is None:
            return
        candidate = str(name).strip()
        if candidate in _NA_DATATYPE_MARKERS:
            return
        if candidate not in valid_names:
            raise FOMResolutionError(f"{context} references undefined datatype {candidate!r} in {path}", kind="read")

    for spec in object_classes:
        for attribute_name, datatype in dict(spec.attribute_datatypes).items():
            require_valid(datatype, f"Attribute {spec.full_name}.{attribute_name}")
    for spec in interaction_classes:
        for parameter_name, datatype in dict(spec.parameter_datatypes).items():
            require_valid(datatype, f"Interaction parameter {spec.full_name}.{parameter_name}")
    for category, metadata in dict(tag_representations).items():
        require_valid(metadata.get("datatype"), f"Tag category {category}")
    for label, metadata in dict(synchronization_points).items():
        require_valid(metadata.get("tag_datatype"), f"Synchronization point {label}")
    require_valid(time_stamp_datatype, "TimeStamp")
    require_valid(lookahead_datatype, "Lookahead")
    for name, spec in dict(simple_datatypes).items():
        require_valid(spec.representation, f"Simple datatype {name}")
    for name, spec in dict(enumerated_datatypes).items():
        require_valid(spec.representation, f"Enumerated datatype {name}")
    for name, spec in dict(array_datatypes).items():
        require_valid(spec.data_type, f"Array datatype {name}")
    for name, spec in dict(fixed_record_datatypes).items():
        for field in spec.fields:
            require_valid(field.data_type, f"Fixed record field {name}.{field.name}")
    for name, spec in dict(variant_record_datatypes).items():
        if spec.discriminant and not spec.data_type:
            raise FOMResolutionError(f"Variant record datatype {name!r} defines a discriminant without a datatype in {path}", kind="read")
        require_valid(spec.data_type, f"Variant record discriminant {name}")
        for alternative in spec.alternatives:
            require_valid(alternative.data_type, f"Variant record alternative {name}.{alternative.enumerator or '<unnamed>'}")


def _require_lxml() -> Any:
    if LET is None:
        raise FOMResolutionError(
            "Schema validation requires the optional 'lxml' dependency, which is not installed",
            kind="read",
        )
    return LET


@lru_cache(maxsize=2)
def _xml_schema(profile: str) -> Any:
    normalized = str(profile).strip().lower()
    if normalized not in {"dif", "omt"}:
        raise ValueError(f"Unsupported XML schema profile {profile!r}")
    filename = "IEEE1516-OMT-2010.xsd" if normalized == "omt" else "IEEE1516-DIF-2010.xsd"
    schema_path = Path("CERTI/xml/ieee1516-2010/1516_2-2010") / filename
    lxml_etree = _require_lxml()
    return lxml_etree.XMLSchema(lxml_etree.parse(str(schema_path)))


def validate_fom_xml_schema(path: str | os.PathLike[str], *, profile: str = "dif") -> None:
    lxml_etree = _require_lxml()
    document = lxml_etree.parse(str(path))
    schema = _xml_schema(profile)
    if not schema.validate(document):
        error = schema.error_log.last_error
        detail = error.message if error is not None else "schema validation failed"
        raise FOMResolutionError(f"Schema-invalid {profile.upper()} XML {path}: {detail}", kind="read")


def _extract_synchronization_points(root: ET.Element, *, path: Path) -> dict[str, dict[str, str]]:
    synchronization_section = next(
        (child for child in list(root) if _local_name(child.tag) == "synchronizations"),
        None,
    )
    if synchronization_section is None:
        synchronization_section = next(
            (child for child in list(root) if _local_name(child.tag) == "synchronizationPoints"),
            None,
        )
    if synchronization_section is None:
        return {}
    points: dict[str, dict[str, str]] = {}
    for point in list(synchronization_section):
        if _local_name(point.tag) not in {"synchronization", "synchronizationPoint"}:
            continue
        label = (_child_text(point, "label") or _child_text(point, "name") or "").strip()
        if not label:
            continue
        _require_unique_name(points, label, "synchronization point", path=path)
        metadata = {
            "tag_datatype": (_child_text(point, "tagDatatype") or _child_text(point, "dataType") or "").strip(),
            "capability": (_child_text(point, "capability") or "").strip(),
            "semantics": (_child_text(point, "semantics") or "").strip(),
        }
        points[label] = {key: value for key, value in metadata.items() if value}
    return points


def parse_fom_xml(
    path: str | os.PathLike[str],
    *,
    source: Any | None = None,
    uri: str | None = None,
    validate_schema: str | bool = False,
    default_uri_builder: Callable[[Path], str],
    standard_datatype_names_factory: Callable[[], frozenset[str]],
) -> FOMModule:
    """Parse the useful name-bearing subset of an IEEE 1516.2 object model."""

    path = Path(path)
    try:
        root = ET.parse(path).getroot()
    except FileNotFoundError as exc:
        raise FOMResolutionError(f"FOM module not found: {path}", kind="open") from exc
    except ET.ParseError as exc:
        raise FOMResolutionError(f"Could not parse FOM XML {path}: {exc}", kind="read") from exc

    if _local_name(root.tag) != "objectModel":
        raise FOMResolutionError(
            f"{path} does not look like an HLA objectModel document",
            kind="read",
        )
    _validate_xml_namespace_usage(root, path=path)
    if validate_schema:
        profile = "dif" if validate_schema is True else str(validate_schema)
        validate_fom_xml_schema(path, profile=profile)

    identification_metadata = _extract_model_identification(root, path=path)
    model_name = str(identification_metadata.get("name") or "").strip() or None
    model_type = str(identification_metadata.get("type") or "").strip() or None
    service_utilization = _extract_service_utilization(root)

    objects_section = next((child for child in list(root) if _local_name(child.tag) == "objects"), None)
    object_classes: list[ObjectClassSpec] = []
    if objects_section is not None:
        top_level_object_classes = _direct_children(objects_section, "objectClass")
        _validate_top_level_hierarchy(
            top_level_object_classes,
            root_name="HLAobjectRoot",
            kind="object class",
            path=path,
        )
        root_object_names: dict[str, bool] = {}
        for object_class in top_level_object_classes:
            object_name = (_child_text(object_class, "name") or "").strip()
            if object_name:
                _require_unique_name(root_object_names, object_name, "object class", path=path)
                root_object_names[object_name] = True
            object_classes.extend(_walk_object_class(object_class, path=path))

    interactions_section = next((child for child in list(root) if _local_name(child.tag) == "interactions"), None)
    interaction_classes: list[InteractionClassSpec] = []
    if interactions_section is not None:
        top_level_interaction_classes = _direct_children(interactions_section, "interactionClass")
        _validate_top_level_hierarchy(
            top_level_interaction_classes,
            root_name="HLAinteractionRoot",
            kind="interaction class",
            path=path,
        )
        root_interaction_names: dict[str, bool] = {}
        for interaction_class in top_level_interaction_classes:
            interaction_name = (_child_text(interaction_class, "name") or "").strip()
            if interaction_name:
                _require_unique_name(root_interaction_names, interaction_name, "interaction class", path=path)
                root_interaction_names[interaction_name] = True
            interaction_classes.extend(_walk_interaction_class(interaction_class, path=path))

    dimension_names: set[str] = set()
    dimension_specs: dict[str, DimensionSpec] = {}
    declared_dimension_names: dict[str, bool] = {}
    dimensions_section = next((child for child in list(root) if _local_name(child.tag) == "dimensions"), None)
    if dimensions_section is not None:
        for dimension in _direct_children(dimensions_section, "dimension"):
            name = _child_text(dimension, "name")
            if name:
                _require_unique_name(declared_dimension_names, name, "dimension", path=path)
                declared_dimension_names[name] = True
                dimension_names.add(name)
                dimension_specs[name] = DimensionSpec(
                    name=name,
                    data_type=_child_text(dimension, "dataType"),
                    upper_bound=_child_text(dimension, "upperBound"),
                    normalization=_child_text(dimension, "normalization"),
                    semantics=_child_text(dimension, "semantics"),
                )

    for element in root.iter():
        if _local_name(element.tag) == "dimension" and element.text and not _direct_children(element, "name"):
            text = element.text.strip()
            if text:
                dimension_names.add(text)

    resolved_uri = uri or default_uri_builder(path)
    lower_type = (model_type or "").lower()
    lower_name = (model_name or "").lower()
    time_stamp_datatype, lookahead_datatype = _extract_time_datatypes(root)
    datatype_names = _extract_datatype_names(root, path=path)
    basic_datatypes = _extract_basic_datatypes(root, path=path)
    simple_datatypes = _extract_simple_datatypes(root, path=path)
    enumerated_datatypes = _extract_enumerated_datatypes(root, path=path)
    array_datatypes = _extract_array_datatypes(root, path=path)
    fixed_record_datatypes = _extract_fixed_record_datatypes(root, path=path)
    variant_record_datatypes = _extract_variant_record_datatypes(root, path=path)
    tag_representations = _extract_tag_representations(root, path=path)
    transportation_names = _extract_transportation_names(root, path=path)
    update_rates = _extract_update_rates(root, path=path)
    synchronization_points = _extract_synchronization_points(root, path=path)
    switch_settings = _extract_switch_settings(root)
    _validate_transportation_references(object_classes, interaction_classes, transportation_names, path=path)
    _validate_update_rate_references(object_classes, update_rates, path=path)
    _validate_switch_settings(switch_settings, path=path)
    _validate_datatype_references(
        object_classes,
        interaction_classes,
        datatype_names,
        simple_datatypes,
        enumerated_datatypes,
        array_datatypes,
        fixed_record_datatypes,
        variant_record_datatypes,
        tag_representations,
        synchronization_points,
        time_stamp_datatype,
        lookahead_datatype,
        path=path,
        standard_datatype_names_factory=standard_datatype_names_factory,
    )
    return FOMModule(
        source=source if source is not None else path,
        uri=resolved_uri,
        path=path,
        name=model_name,
        model_type=model_type,
        model_identification=identification_metadata,
        service_utilization=service_utilization,
        object_classes=tuple(object_classes),
        interaction_classes=tuple(interaction_classes),
        dimensions=tuple(sorted(dimension_names)),
        dimension_specs=dimension_specs,
        datatype_names=datatype_names,
        basic_datatypes=basic_datatypes,
        simple_datatypes=simple_datatypes,
        enumerated_datatypes=enumerated_datatypes,
        array_datatypes=array_datatypes,
        fixed_record_datatypes=fixed_record_datatypes,
        variant_record_datatypes=variant_record_datatypes,
        tag_representations=tag_representations,
        transportation_names=transportation_names,
        update_rates=update_rates,
        synchronization_points=synchronization_points,
        switch_settings=switch_settings,
        time_stamp_datatype=time_stamp_datatype,
        lookahead_datatype=lookahead_datatype,
        inferred_time_implementation=_infer_time_implementation(root),
        notes=_extract_notes(root),
        is_mim=("mim" in lower_type or "mim" in lower_name or "initialization module" in lower_name),
    )
