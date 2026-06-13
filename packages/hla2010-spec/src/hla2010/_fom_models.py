"""Public FOM/MIM model dataclasses used by ``hla2010.fom``."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class OMTConformanceAssessment:
    """Current repo-native OMT conformance assessment for one object-model document."""

    label: str
    schema_valid: bool
    parsed: bool
    module_name: str | None = None
    unsupported_features: tuple[str, ...] = ()
    rationale: str = ""


@dataclass(frozen=True)
class ObjectClassSpec:
    """Object class extracted from an OMT module."""

    full_name: str
    attributes: tuple[str, ...] = ()
    parent_name: str | None = None
    declared_attributes: tuple[str, ...] = ()
    attribute_datatypes: Mapping[str, str] = field(default_factory=dict)
    attribute_transportations: Mapping[str, str] = field(default_factory=dict)
    attribute_update_rates: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionClassSpec:
    """Interaction class extracted from an OMT module."""

    full_name: str
    parameters: tuple[str, ...] = ()
    parent_name: str | None = None
    declared_parameters: tuple[str, ...] = ()
    parameter_datatypes: Mapping[str, str] = field(default_factory=dict)
    transportation: str | None = None


@dataclass(frozen=True)
class BasicDatatypeSpec:
    name: str
    size: str | None = None
    interpretation: str | None = None
    endian: str | None = None
    encoding: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class SimpleDatatypeSpec:
    name: str
    representation: str | None = None
    units: str | None = None
    resolution: str | None = None
    accuracy: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class EnumeratorSpec:
    name: str
    values: tuple[str, ...] = ()


@dataclass(frozen=True)
class EnumeratedDatatypeSpec:
    name: str
    representation: str | None = None
    semantics: str | None = None
    enumerators: tuple[EnumeratorSpec, ...] = ()


@dataclass(frozen=True)
class ArrayDatatypeSpec:
    name: str
    data_type: str | None = None
    cardinality: str | None = None
    encoding: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class FixedRecordFieldSpec:
    name: str
    data_type: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class FixedRecordDatatypeSpec:
    name: str
    encoding: str | None = None
    semantics: str | None = None
    fields: tuple[FixedRecordFieldSpec, ...] = ()


@dataclass(frozen=True)
class VariantAlternativeSpec:
    enumerator: str
    name: str | None = None
    data_type: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class VariantRecordDatatypeSpec:
    name: str
    discriminant: str | None = None
    data_type: str | None = None
    encoding: str | None = None
    semantics: str | None = None
    alternatives: tuple[VariantAlternativeSpec, ...] = ()


@dataclass(frozen=True)
class DimensionSpec:
    name: str
    data_type: str | None = None
    upper_bound: str | None = None
    normalization: str | None = None
    semantics: str | None = None


@dataclass(frozen=True)
class FOMModule:
    """Resolved FOM/MIM module."""

    source: Any
    uri: str
    path: Path | None = None
    name: str | None = None
    model_type: str | None = None
    model_identification: Mapping[str, Any] = field(default_factory=dict)
    service_utilization: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    object_classes: tuple[ObjectClassSpec, ...] = ()
    interaction_classes: tuple[InteractionClassSpec, ...] = ()
    dimensions: tuple[str, ...] = ()
    dimension_specs: Mapping[str, DimensionSpec] = field(default_factory=dict)
    datatype_names: tuple[str, ...] = ()
    basic_datatypes: Mapping[str, BasicDatatypeSpec] = field(default_factory=dict)
    simple_datatypes: Mapping[str, SimpleDatatypeSpec] = field(default_factory=dict)
    enumerated_datatypes: Mapping[str, EnumeratedDatatypeSpec] = field(default_factory=dict)
    array_datatypes: Mapping[str, ArrayDatatypeSpec] = field(default_factory=dict)
    fixed_record_datatypes: Mapping[str, FixedRecordDatatypeSpec] = field(default_factory=dict)
    variant_record_datatypes: Mapping[str, VariantRecordDatatypeSpec] = field(default_factory=dict)
    tag_representations: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    transportation_names: tuple[str, ...] = ()
    update_rates: Mapping[str, str] = field(default_factory=dict)
    synchronization_points: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    switch_settings: Mapping[str, str] = field(default_factory=dict)
    time_stamp_datatype: str | None = None
    lookahead_datatype: str | None = None
    inferred_time_implementation: str | None = None
    notes: tuple[str, ...] = ()
    is_mim: bool = False

    @property
    def parsed(self) -> bool:
        return bool(
            self.object_classes
            or self.interaction_classes
            or self.model_identification
            or self.service_utilization
            or self.dimensions
            or self.dimension_specs
            or self.datatype_names
            or self.basic_datatypes
            or self.simple_datatypes
            or self.enumerated_datatypes
            or self.array_datatypes
            or self.fixed_record_datatypes
            or self.variant_record_datatypes
            or self.tag_representations
            or self.transportation_names
            or self.update_rates
            or self.synchronization_points
            or self.switch_settings
            or self.time_stamp_datatype
            or self.lookahead_datatype
            or self.notes
        )


@dataclass(frozen=True)
class FOMCatalog:
    """Merged federation object model catalog installed by the RTI."""

    modules: tuple[FOMModule, ...] = ()
    mim_module: FOMModule | None = None
    object_classes: Mapping[str, ObjectClassSpec] = field(default_factory=dict)
    interaction_classes: Mapping[str, InteractionClassSpec] = field(default_factory=dict)
    dimensions: frozenset[str] = field(default_factory=frozenset)
    datatype_names: frozenset[str] = field(default_factory=frozenset)
    basic_datatypes: Mapping[str, BasicDatatypeSpec] = field(default_factory=dict)
    simple_datatypes: Mapping[str, SimpleDatatypeSpec] = field(default_factory=dict)
    enumerated_datatypes: Mapping[str, EnumeratedDatatypeSpec] = field(default_factory=dict)
    array_datatypes: Mapping[str, ArrayDatatypeSpec] = field(default_factory=dict)
    fixed_record_datatypes: Mapping[str, FixedRecordDatatypeSpec] = field(default_factory=dict)
    variant_record_datatypes: Mapping[str, VariantRecordDatatypeSpec] = field(default_factory=dict)
    tag_representations: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    transportation_names: frozenset[str] = field(default_factory=frozenset)
    update_rates: Mapping[str, str] = field(default_factory=dict)
    synchronization_points: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    switch_settings: Mapping[str, str] = field(default_factory=dict)
    time_stamp_datatype: str | None = None
    lookahead_datatype: str | None = None
    notes: tuple[str, ...] = ()
    logical_time_implementation: str | None = None

    def has_object_class(self, name: str) -> bool:
        return str(name) in self.object_classes

    def has_interaction_class(self, name: str) -> bool:
        return str(name) in self.interaction_classes

    def attributes_for_object_class(self, name: str) -> tuple[str, ...]:
        return self.object_classes[str(name)].attributes

    def parameters_for_interaction_class(self, name: str) -> tuple[str, ...]:
        return self.interaction_classes[str(name)].parameters

    def as_summary(self) -> dict[str, Any]:
        return {
            "mim": self.mim_module.name if self.mim_module else None,
            "mim_uri": self.mim_module.uri if self.mim_module else None,
            "modules": [module.name or str(module.source) for module in self.modules],
            "module_uris": [module.uri for module in self.modules],
            "model_identification": {
                key: list(value) if isinstance(value, tuple) else value
                for key, value in sorted(getattr(self.mim_module, "model_identification", {}).items())
            }
            if self.mim_module
            else {},
            "object_classes": sorted(self.object_classes),
            "interaction_classes": sorted(self.interaction_classes),
            "dimensions": sorted(self.dimensions),
            "datatype_names": sorted(self.datatype_names),
            "basic_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.basic_datatypes.items())},
            "simple_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.simple_datatypes.items())},
            "enumerated_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.enumerated_datatypes.items())},
            "array_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.array_datatypes.items())},
            "fixed_record_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.fixed_record_datatypes.items())},
            "variant_record_datatypes": {key: datatype_summary(spec) for key, spec in sorted(self.variant_record_datatypes.items())},
            "tag_representations": {key: dict(sorted(value.items())) for key, value in sorted(self.tag_representations.items())},
            "transportation_names": sorted(self.transportation_names),
            "update_rates": dict(sorted(self.update_rates.items())),
            "synchronization_points": {key: dict(sorted(value.items())) for key, value in sorted(self.synchronization_points.items())},
            "switch_settings": dict(sorted(self.switch_settings.items())),
            "time_stamp_datatype": self.time_stamp_datatype,
            "lookahead_datatype": self.lookahead_datatype,
            "notes": list(self.notes),
            "logical_time_implementation": self.logical_time_implementation,
        }


def datatype_summary(spec: Any) -> dict[str, Any]:
    if isinstance(spec, BasicDatatypeSpec):
        return {
            "size": spec.size,
            "interpretation": spec.interpretation,
            "endian": spec.endian,
            "encoding": spec.encoding,
            "semantics": spec.semantics,
        }
    if isinstance(spec, SimpleDatatypeSpec):
        return {
            "representation": spec.representation,
            "units": spec.units,
            "resolution": spec.resolution,
            "accuracy": spec.accuracy,
            "semantics": spec.semantics,
        }
    if isinstance(spec, EnumeratedDatatypeSpec):
        return {
            "representation": spec.representation,
            "semantics": spec.semantics,
            "enumerators": [{"name": item.name, "values": list(item.values)} for item in spec.enumerators],
        }
    if isinstance(spec, ArrayDatatypeSpec):
        return {
            "data_type": spec.data_type,
            "cardinality": spec.cardinality,
            "encoding": spec.encoding,
            "semantics": spec.semantics,
        }
    if isinstance(spec, FixedRecordDatatypeSpec):
        return {
            "encoding": spec.encoding,
            "semantics": spec.semantics,
            "fields": [{"name": field.name, "data_type": field.data_type, "semantics": field.semantics} for field in spec.fields],
        }
    if isinstance(spec, VariantRecordDatatypeSpec):
        return {
            "discriminant": spec.discriminant,
            "data_type": spec.data_type,
            "encoding": spec.encoding,
            "semantics": spec.semantics,
            "alternatives": [
                {
                    "enumerator": alt.enumerator,
                    "name": alt.name,
                    "data_type": alt.data_type,
                    "semantics": alt.semantics,
                }
                for alt in spec.alternatives
            ],
        }
    return {}


__all__ = [
    "ArrayDatatypeSpec",
    "BasicDatatypeSpec",
    "DimensionSpec",
    "EnumeratedDatatypeSpec",
    "EnumeratorSpec",
    "FixedRecordDatatypeSpec",
    "FixedRecordFieldSpec",
    "FOMCatalog",
    "FOMModule",
    "InteractionClassSpec",
    "ObjectClassSpec",
    "OMTConformanceAssessment",
    "SimpleDatatypeSpec",
    "VariantAlternativeSpec",
    "VariantRecordDatatypeSpec",
    "datatype_summary",
]
