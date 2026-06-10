"""FOM/MIM URL handling and lightweight IEEE 1516.2-2010 OMT XML parsing.

This module deliberately keeps validation small and deterministic while preserving
traceability to the HLA standards:

* IEEE 1516.1-2010 §4.5 - Create Federation Execution loads the MIM before FOMs.
* IEEE 1516.1-2010 §4.9 - Join Federation Execution may extend the FDD with
  additional FOM modules.
* IEEE 1516.2-2010 §4.2/§4.3 - object and interaction class hierarchy handling.
* IEEE 1516.2-2010 §7 - FOM module/SOM module merging rules.

The parser is not a full schema validator. It extracts the name-bearing subset
needed by the pure Python RTI and normalizes module designators for Java RTIs.
"""
from __future__ import annotations

import os
import re
import struct
import xml.etree.ElementTree as ET
from functools import lru_cache
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote, unquote, urlparse, urlunparse

from .exceptions import CouldNotDecode

from lxml import etree as LET


class FOMResolutionError(ValueError):
    """Raised when a FOM/MIM module designator cannot be resolved or parsed.

    ``kind`` distinguishes open-vs-read failures so the RTI layer can map them
    to the corresponding HLA exception family instead of collapsing both cases
    into a single generic resolution error.
    """

    def __init__(self, message: str, *, kind: str = "open"):
        super().__init__(message)
        self.kind = kind


class FOMMergeError(ValueError):
    """Raised when FOM modules cannot be merged into a single FDD catalog."""


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
    """Object class extracted from an OMT module.

    ``attributes`` are the available attributes for the class: declared
    attributes plus inherited attributes from superclasses. ``declared`` keeps
    the local declaration for trace/debugging. ``attribute_datatypes`` records
    the OMT ``dataType`` designator for attributes when it is present so MOM
    validation can be driven from the active MIM/FOM catalog instead of a
    handwritten parameter table.
    """

    full_name: str
    attributes: tuple[str, ...] = ()
    parent_name: str | None = None
    declared_attributes: tuple[str, ...] = ()
    attribute_datatypes: Mapping[str, str] = field(default_factory=dict)
    attribute_transportations: Mapping[str, str] = field(default_factory=dict)
    attribute_update_rates: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionClassSpec:
    """Interaction class extracted from an OMT module.

    ``parameters`` are the available parameters for the class: declared
    parameters plus inherited parameters from superclasses. ``parameter_datatypes``
    records OMT ``dataType`` designators where available.
    """

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
    """Resolved FOM/MIM module.

    ``source`` is the user-provided designator. ``uri`` is the normalized URL
    string suitable for Java RTIs. ``path`` is populated for local files that
    the Python RTI can parse.
    """

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
    """Merged federation object model catalog installed by the RTI.

    The catalog is name-based. The pure Python RTI turns these names into HLA
    handles after the MIM and FOM modules have been merged.
    """

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
            "basic_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.basic_datatypes.items())},
            "simple_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.simple_datatypes.items())},
            "enumerated_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.enumerated_datatypes.items())},
            "array_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.array_datatypes.items())},
            "fixed_record_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.fixed_record_datatypes.items())},
            "variant_record_datatypes": {key: _datatype_summary(spec) for key, spec in sorted(self.variant_record_datatypes.items())},
            "tag_representations": {
                key: dict(sorted(value.items()))
                for key, value in sorted(self.tag_representations.items())
            },
            "transportation_names": sorted(self.transportation_names),
            "update_rates": dict(sorted(self.update_rates.items())),
            "synchronization_points": {
                key: dict(sorted(value.items()))
                for key, value in sorted(self.synchronization_points.items())
            },
            "switch_settings": dict(sorted(self.switch_settings.items())),
            "time_stamp_datatype": self.time_stamp_datatype,
            "lookahead_datatype": self.lookahead_datatype,
            "notes": list(self.notes),
            "logical_time_implementation": self.logical_time_implementation,
        }


def _datatype_summary(spec: Any) -> dict[str, Any]:
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
            "fields": [
                {"name": field.name, "data_type": field.data_type, "semantics": field.semantics}
                for field in spec.fields
            ],
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


def _today_iso_date() -> str:
    from datetime import date

    return date.today().isoformat()


_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_STANDARD_TIME_BY_DATATYPE_HINT = {
    "HLAfloat64BE": "HLAfloat64Time",
    "HLAfloat64LE": "HLAfloat64Time",
    "HLAinteger64BE": "HLAinteger64Time",
    "HLAinteger64LE": "HLAinteger64Time",
}
_IEEE_1516_2010_NAMESPACE = "http://standards.ieee.org/IEEE1516-2010"
_SISO_1516_2010_NAMESPACE = "http://www.sisostds.org/schemas/IEEE1516-2010"
_XML_SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
_DEFAULT_SCHEMA_LOCATION = (
    f"{_IEEE_1516_2010_NAMESPACE} "
    "http://standards.ieee.org/downloads/1516/1516.2-2010/IEEE1516-DIF-2010.xsd"
)
_DEFAULT_OMT_SCHEMA_LOCATION = (
    f"{_IEEE_1516_2010_NAMESPACE} "
    "http://standards.ieee.org/downloads/1516/1516.2-2010/IEEE1516-OMT-2010.xsd"
)
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
_DEFAULT_SWITCH_SETTINGS = {
    "autoProvide": "false",
    "conveyRegionDesignatorSets": "false",
    "conveyProducingFederate": "false",
    "attributeScopeAdvisory": "false",
    "attributeRelevanceAdvisory": "false",
    "objectClassRelevanceAdvisory": "false",
    "interactionRelevanceAdvisory": "false",
    "serviceReporting": "false",
    "exceptionReporting": "false",
    "delaySubscriptionEvaluation": "false",
    "automaticResignAction": "NoAction",
}
_STRICT_OMT_TRANSPORTATION_RELIABILITY = {
    "HLAreliable": "Yes",
    "HLAbestEffort": "No",
}
_NA_DATATYPE_MARKERS = {"", "NA", "N/A"}
_STANDARD_MIM_NAME = "HLAstandardMIM"
_CARDINALITY_RE = re.compile(r"(Dynamic|(\d)+|(\[(\d)+\.\.(\d)+\]))(,(Dynamic|(\d)+|(\[(\d)+\.\.(\d)+\])))*$")


def _is_url_like(text: str) -> bool:
    return bool(_URI_SCHEME_RE.match(text))


def _path_to_file_uri(path: Path) -> str:
    absolute = path.expanduser().resolve()
    try:
        return absolute.as_uri()
    except ValueError:
        return urlunparse(("file", "", quote(str(absolute)), "", "", ""))


def default_fom_search_paths() -> tuple[Path, ...]:
    """Return bundled package FOM search paths."""

    candidates: list[Path] = []
    try:
        package_root = resources.files("hla2010")
        fom_root = package_root.joinpath("resources", "foms")
        package_path = Path(str(package_root))
        candidates.extend((Path(str(fom_root)), package_path, package_path.parent))
    except Exception:
        pass

    module_root = Path(__file__).resolve().parent
    candidates.extend((module_root / "resources" / "foms", module_root, module_root.parent))

    existing: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        existing.append(resolved)
    return tuple(existing)


def _bundled_standard_mim_path() -> Path:
    for base in default_fom_search_paths():
        candidate = base / "HLAstandardMIM.xml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("bundled HLAstandardMIM.xml not found in default FOM search paths")


def standard_mim_module() -> FOMModule:
    """Return the built-in standard MIM/MOM development catalog.

    The implementation is delegated to :mod:`hla2010.mom` to keep the Annex G /
    Clause 11 MOM names centralized.  The local catalog exposes the standard
    MOM object classes, interaction classes, attributes, parameters, and default
    dimensions needed by the pure Python RTI.
    """

    from .mom import create_standard_mim_module

    return create_standard_mim_module()

def normalize_module_uri(source: Any, *, base_paths: Iterable[str | os.PathLike[str]] = ()) -> tuple[str, Path | None]:
    """Normalize a FOM/MIM source into ``(uri, local_path_or_none)``.

    Accepted values include ``pathlib.Path``, local path strings, ``file:`` URLs,
    ``http(s):`` URLs, already resolved :class:`FOMModule` instances, and Java URL
    objects whose string representation is a URL. The resolver searches both
    user-provided base paths and bundled package FOM resources.
    """

    if isinstance(source, FOMModule):
        return source.uri, source.path

    text = str(source)
    if text == _STANDARD_MIM_NAME:
        return "builtin:HLAstandardMIM", None

    if isinstance(source, os.PathLike):
        path = Path(source).expanduser()
        if not path.is_absolute():
            path = path.resolve()
        return _path_to_file_uri(path), path

    parsed = urlparse(text)

    if parsed.scheme in {"hla2010", "resource"}:
        resource_name = unquote(parsed.path.lstrip("/")) or unquote(parsed.netloc) or unquote(text.split(":", 1)[1])
        search_roots = tuple(Path(base).expanduser() for base in base_paths) + default_fom_search_paths()
        for base in search_roots:
            candidate = Path(base).expanduser() / resource_name
            if candidate.exists():
                return _path_to_file_uri(candidate), candidate.resolve()
        missing_root = search_roots[0] if search_roots else Path.cwd()
        missing = Path(missing_root) / resource_name
        return _path_to_file_uri(missing), missing

    if parsed.scheme == "file":
        path = Path(unquote(parsed.path)).expanduser()
        return text, path

    if parsed.scheme in {"http", "https", "jar", "builtin"}:
        return text, None

    if _is_url_like(text):
        return text, None

    candidates = [Path(text).expanduser()]
    for base in tuple(base_paths) + default_fom_search_paths():
        candidates.append(Path(base).expanduser() / text)

    for candidate in candidates:
        if candidate.exists():
            return _path_to_file_uri(candidate), candidate.resolve()

    candidate = candidates[0]
    if not candidate.is_absolute():
        candidate = candidate.resolve()
    return _path_to_file_uri(candidate), candidate


def module_uri(source: Any, *, base_paths: Iterable[str | os.PathLike[str]] = ()) -> str:
    return normalize_module_uri(source, base_paths=base_paths)[0]


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


def _stable_spec_union(existing: Mapping[str, Any], incoming: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    result = dict(existing)
    for name, spec in dict(incoming).items():
        if name in result and result[name] != spec:
            raise FOMMergeError(f"Conflicting {kind} definition {name!r} across FOM modules")
        result.setdefault(name, spec)
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


@lru_cache(maxsize=1)
def _standard_mim_datatype_names() -> frozenset[str]:
    path = _bundled_standard_mim_path()
    root = ET.parse(path).getroot()
    return frozenset(_extract_datatype_names(root, path=path))


@lru_cache(maxsize=1)
def _standard_mim_datatype_catalog() -> dict[str, Any]:
    path = _bundled_standard_mim_path()
    root = ET.parse(path).getroot()
    return {
        **_extract_basic_datatypes(root, path=path),
        **_extract_simple_datatypes(root, path=path),
        **_extract_enumerated_datatypes(root, path=path),
        **_extract_array_datatypes(root, path=path),
        **_extract_fixed_record_datatypes(root, path=path),
        **_extract_variant_record_datatypes(root, path=path),
    }


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
    root: ET.Element,
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
) -> None:
    valid_names = set(datatype_names) | set(_standard_mim_datatype_names())

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


@lru_cache(maxsize=2)
def _xml_schema(profile: str) -> LET.XMLSchema:
    normalized = str(profile).strip().lower()
    if normalized not in {"dif", "omt"}:
        raise ValueError(f"Unsupported XML schema profile {profile!r}")
    filename = "IEEE1516-OMT-2010.xsd" if normalized == "omt" else "IEEE1516-DIF-2010.xsd"
    schema_path = Path("CERTI/xml/ieee1516-2010/1516_2-2010") / filename
    return LET.XMLSchema(LET.parse(str(schema_path)))


def validate_fom_xml_schema(path: str | os.PathLike[str], *, profile: str = "dif") -> None:
    document = LET.parse(str(path))
    schema = _xml_schema(profile)
    if not schema.validate(document):
        error = schema.error_log.last_error
        detail = error.message if error is not None else "schema validation failed"
        raise FOMResolutionError(f"Schema-invalid {profile.upper()} XML {path}: {detail}", kind="read")


def _uses_runtime_normalization_subset(normalization: str | None) -> bool:
    if normalization is None:
        return False
    normalized = normalization.strip().lower()
    return normalized not in {"", "none", "identity"}


def assess_omt_conformance(
    source: str | os.PathLike[str],
    *,
    validate_schema: bool = True,
    profile: str = "omt",
) -> OMTConformanceAssessment:
    """Classify one OMT/FDD/DIF document using the current repo-native validator criteria."""

    try:
        module = parse_fom_xml(source, validate_schema=validate_schema)
    except FOMResolutionError as exc:
        schema_valid = False
        if validate_schema:
            try:
                validate_fom_xml_schema(source, profile=profile)
            except FOMResolutionError:
                schema_valid = False
            else:
                schema_valid = True
        return OMTConformanceAssessment(
            label="nonconforming",
            schema_valid=schema_valid,
            parsed=False,
            unsupported_features=(str(exc),),
            rationale="The document fails current schema or semantic validation and is therefore nonconforming on the repo-native OMT validator path.",
        )

    unsupported_features: list[str] = []
    if any(
        _uses_runtime_normalization_subset(spec.normalization)
        for spec in dict(module.dimension_specs).values()
    ):
        unsupported_features.append(
            "Dimension normalization metadata is parsed and preserved, but runtime DDM normalization semantics are not yet executed."
        )

    if validate_schema:
        validate_fom_xml_schema(source, profile=profile)

    if unsupported_features:
        return OMTConformanceAssessment(
            label="partially conforming",
            schema_valid=True,
            parsed=True,
            module_name=module.name,
            unsupported_features=tuple(unsupported_features),
            rationale="The document satisfies current schema and parser validation, but it uses features that the repo still treats as a narrower supported subset.",
        )

    return OMTConformanceAssessment(
        label="conforming",
        schema_valid=True,
        parsed=True,
        module_name=module.name,
        rationale="The document satisfies current repo-native schema and parser validation with no known unsupported OMT subset feature detected.",
    )


def _datatype_spec_lookup(name: str, catalog: FOMCatalog | Mapping[str, Any] | None) -> Any | None:
    if not name:
        return None
    if isinstance(catalog, FOMCatalog):
        for mapping in (
            catalog.basic_datatypes,
            catalog.simple_datatypes,
            catalog.enumerated_datatypes,
            catalog.array_datatypes,
            catalog.fixed_record_datatypes,
            catalog.variant_record_datatypes,
        ):
            if name in mapping:
                return mapping[name]
    elif catalog is not None and name in dict(catalog):
        return dict(catalog)[name]
    return _standard_mim_datatype_catalog().get(name)


def _decode_primitive_datatype(name: str, payload: bytes) -> tuple[int, Any]:
    from . import encoding as hla_encoding

    cls = getattr(hla_encoding, name, None)
    if cls is None:
        raise CouldNotDecode(f"Unsupported primitive datatype {name!r}")
    element = cls()
    try:
        element.decode(payload)
        return element.encoded_length(), getattr(element, "value", None)
    except Exception as exc:  # pragma: no cover - specific message is asserted at call sites
        raise CouldNotDecode(f"Could not decode payload as {name}") from exc


def _consume_runtime_builtin(payload: bytes, datatype_name: str) -> int | None:
    if datatype_name == "HLAopaqueData":
        return len(payload)
    if datatype_name == "HLAASCIIstring":
        try:
            _decode_primitive_datatype(datatype_name, payload)
            return len(payload)
        except CouldNotDecode:
            try:
                payload.decode("ascii")
                return len(payload)
            except Exception:
                return None
    if datatype_name == "HLAunicodeString":
        try:
            _decode_primitive_datatype(datatype_name, payload)
            return len(payload)
        except CouldNotDecode:
            try:
                payload.decode("utf-8")
                return len(payload)
            except Exception:
                return None
    try:
        consumed, _value = _decode_primitive_datatype(datatype_name, payload)
        return consumed
    except CouldNotDecode:
        return None


def _enum_name_for_decoded_value(spec: EnumeratedDatatypeSpec, decoded_value: Any) -> str | None:
    token = str(decoded_value)
    for enumerator in spec.enumerators:
        if token in enumerator.values:
            return enumerator.name
    return None


def _cardinality_extent(token: str) -> int | None:
    text = token.strip()
    if not text or text == "Dynamic":
        return None
    if text.isdigit():
        return int(text)
    if text.startswith("[") and text.endswith("]") and ".." in text:
        lower, upper = text[1:-1].split("..", 1)
        if lower.isdigit() and upper.isdigit():
            return max(0, int(upper) - int(lower) + 1)
    raise CouldNotDecode(f"Unsupported array cardinality component {token!r}")


def _cardinality_count(cardinality: str | None) -> int | None:
    if not cardinality:
        return None
    extents = [_cardinality_extent(token) for token in cardinality.split(",")]
    if any(extent is None for extent in extents):
        return None
    count = 1
    for extent in extents:
        assert extent is not None
        count *= extent
    return count


def _alternative_matches(enumerator_token: str, decoded_name: str | None, enum_order: Mapping[str, int]) -> bool:
    token = enumerator_token.strip()
    if not token or token == "HLAother":
        return False
    decoded = decoded_name or ""
    for part in [item.strip() for item in token.split(",") if item.strip()]:
        if part == decoded:
            return True
        if part.startswith("[") and part.endswith("]") and ".." in part:
            lower, upper = [item.strip() for item in part[1:-1].split("..", 1)]
            if decoded in enum_order and lower in enum_order and upper in enum_order:
                if enum_order[lower] <= enum_order[decoded] <= enum_order[upper]:
                    return True
    return False


def _consume_datatype_value(payload: bytes, datatype_name: str, catalog: FOMCatalog | Mapping[str, Any] | None) -> int:
    if datatype_name in _NA_DATATYPE_MARKERS:
        return len(payload)
    builtin_consumed = _consume_runtime_builtin(payload, datatype_name)
    if builtin_consumed is not None:
        return builtin_consumed
    spec = _datatype_spec_lookup(datatype_name, catalog)
    if spec is None:
        consumed, _value = _decode_primitive_datatype(datatype_name, payload)
        return consumed
    if isinstance(spec, BasicDatatypeSpec):
        consumed, _value = _decode_primitive_datatype(spec.name, payload)
        return consumed
    if isinstance(spec, SimpleDatatypeSpec):
        if not spec.representation:
            raise CouldNotDecode(f"Simple datatype {spec.name!r} has no representation")
        return _consume_datatype_value(payload, spec.representation, catalog)
    if isinstance(spec, EnumeratedDatatypeSpec):
        if not spec.representation:
            raise CouldNotDecode(f"Enumerated datatype {spec.name!r} has no representation")
        consumed, value = _decode_primitive_datatype(spec.representation, payload)
        allowed = {member_value for enumerator in spec.enumerators for member_value in enumerator.values}
        if allowed and str(value) not in allowed:
            raise CouldNotDecode(f"Decoded value {value!r} is not valid for enumeration {spec.name!r}")
        return consumed
    if isinstance(spec, ArrayDatatypeSpec):
        if not spec.data_type:
            raise CouldNotDecode(f"Array datatype {spec.name!r} has no element datatype")
        encoding = spec.encoding or ""
        offset = 0
        if encoding == "HLAfixedArray":
            count = _cardinality_count(spec.cardinality)
            if count is None:
                raise CouldNotDecode(f"Fixed array datatype {spec.name!r} requires fixed cardinality")
            for _ in range(count):
                offset += _consume_datatype_value(payload[offset:], spec.data_type, catalog)
            return offset
        if encoding == "HLAvariableArray":
            if len(payload) < 4:
                raise CouldNotDecode(f"Variable array datatype {spec.name!r} is missing its element count")
            count = struct.unpack(">I", payload[:4])[0]
            offset = 4
            for _ in range(count):
                offset += _consume_datatype_value(payload[offset:], spec.data_type, catalog)
            return offset
        raise CouldNotDecode(f"Unsupported array encoding {encoding!r} for datatype {spec.name!r}")
    if isinstance(spec, FixedRecordDatatypeSpec):
        offset = 0
        for field in spec.fields:
            if not field.data_type:
                raise CouldNotDecode(f"Fixed record field {spec.name}.{field.name} has no datatype")
            offset += _consume_datatype_value(payload[offset:], field.data_type, catalog)
        return offset
    if isinstance(spec, VariantRecordDatatypeSpec):
        if not spec.data_type:
            raise CouldNotDecode(f"Variant record datatype {spec.name!r} has no discriminant datatype")
        discriminant_consumed = _consume_datatype_value(payload, spec.data_type, catalog)
        discriminant_spec = _datatype_spec_lookup(spec.data_type, catalog)
        decoded_name: str | None = None
        if isinstance(discriminant_spec, EnumeratedDatatypeSpec) and discriminant_spec.representation:
            _, discriminant_value = _decode_primitive_datatype(discriminant_spec.representation, payload)
            decoded_name = _enum_name_for_decoded_value(discriminant_spec, discriminant_value)
            enum_order = {enumerator.name: index for index, enumerator in enumerate(discriminant_spec.enumerators)}
        else:
            enum_order = {}
        remainder = payload[discriminant_consumed:]
        for alternative in spec.alternatives:
            if _alternative_matches(alternative.enumerator, decoded_name, enum_order):
                if not alternative.data_type:
                    return discriminant_consumed
                return discriminant_consumed + _consume_datatype_value(remainder, alternative.data_type, catalog)
        for alternative in spec.alternatives:
            if alternative.enumerator.strip() == "HLAother":
                if not alternative.data_type:
                    return discriminant_consumed
                return discriminant_consumed + _consume_datatype_value(remainder, alternative.data_type, catalog)
        return discriminant_consumed
    raise CouldNotDecode(f"Unsupported datatype declaration for {datatype_name!r}")


def validate_encoded_datatype_value(payload: bytes, datatype_name: str, catalog: FOMCatalog | Mapping[str, Any] | None = None) -> None:
    consumed = _consume_datatype_value(bytes(payload), datatype_name, catalog)
    if consumed != len(payload):
        raise CouldNotDecode(f"Decoded {consumed} bytes for datatype {datatype_name!r}, trailing payload remains")


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

    resolved_uri = uri or _path_to_file_uri(path)
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
        root,
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


def merge_fom_modules(modules: Iterable[FOMModule], *, mim_module: FOMModule | None = None) -> FOMCatalog:
    """Merge a MIM and FOM modules into a name catalog.

    The merge policy follows the subset of IEEE 1516.2-2010 §7 modeled by this
    project: object classes, interaction classes, dimensions, and time
    representations are merged; duplicate class definitions accumulate
    attributes/parameters; conflicting time implementations are rejected.
    """

    ordered_modules = tuple(module for module in modules if module is not None)
    all_modules = tuple([mim_module] if mim_module is not None else ()) + ordered_modules

    objects: dict[str, ObjectClassSpec] = {}
    interactions: dict[str, InteractionClassSpec] = {}
    dimensions: set[str] = set()
    datatype_names: set[str] = set()
    basic_datatypes: dict[str, BasicDatatypeSpec] = {}
    simple_datatypes: dict[str, SimpleDatatypeSpec] = {}
    enumerated_datatypes: dict[str, EnumeratedDatatypeSpec] = {}
    array_datatypes: dict[str, ArrayDatatypeSpec] = {}
    fixed_record_datatypes: dict[str, FixedRecordDatatypeSpec] = {}
    variant_record_datatypes: dict[str, VariantRecordDatatypeSpec] = {}
    tag_representations: dict[str, dict[str, str]] = {}
    transportation_names: set[str] = set()
    update_rates: dict[str, str] = {}
    synchronization_points: dict[str, dict[str, str]] = {}
    switch_settings: dict[str, str] = {}
    notes: list[str] = []
    time_impls: list[str] = []

    for module in all_modules:
        if module.inferred_time_implementation:
            time_impls.append(module.inferred_time_implementation)
        dimensions.update(module.dimensions)
        datatype_names.update(module.datatype_names)
        basic_datatypes = _stable_spec_union(basic_datatypes, module.basic_datatypes, kind="basic datatype")
        simple_datatypes = _stable_spec_union(simple_datatypes, module.simple_datatypes, kind="simple datatype")
        enumerated_datatypes = _stable_spec_union(enumerated_datatypes, module.enumerated_datatypes, kind="enumerated datatype")
        array_datatypes = _stable_spec_union(array_datatypes, module.array_datatypes, kind="array datatype")
        fixed_record_datatypes = _stable_spec_union(fixed_record_datatypes, module.fixed_record_datatypes, kind="fixed record datatype")
        variant_record_datatypes = _stable_spec_union(variant_record_datatypes, module.variant_record_datatypes, kind="variant record datatype")
        for category, metadata in dict(module.tag_representations).items():
            tag_representations.setdefault(category, dict(metadata))
        transportation_names.update(module.transportation_names)
        for name, value in dict(module.update_rates).items():
            update_rates.setdefault(name, value)
        for label, metadata in dict(module.synchronization_points).items():
            synchronization_points.setdefault(label, dict(metadata))
        for name, value in dict(module.switch_settings).items():
            switch_settings.setdefault(name, value)
        for note in module.notes:
            if note and note not in notes:
                notes.append(note)

        for spec in module.object_classes:
            existing = objects.get(spec.full_name)
            if existing is None:
                objects[spec.full_name] = spec
            else:
                if existing.parent_name and spec.parent_name and existing.parent_name != spec.parent_name:
                    raise FOMMergeError(
                        f"Object class {spec.full_name!r} has conflicting superclasses: {existing.parent_name!r} vs {spec.parent_name!r}"
                    )
                objects[spec.full_name] = ObjectClassSpec(
                    spec.full_name,
                    _stable_union(existing.attributes, spec.attributes),
                    existing.parent_name or spec.parent_name,
                    _stable_union(existing.declared_attributes, spec.declared_attributes),
                    _stable_mapping_union(existing.attribute_datatypes, spec.attribute_datatypes),
                    _stable_mapping_union(existing.attribute_transportations, spec.attribute_transportations),
                    _stable_mapping_union(existing.attribute_update_rates, spec.attribute_update_rates),
                )

        for spec in module.interaction_classes:
            existing = interactions.get(spec.full_name)
            if existing is None:
                interactions[spec.full_name] = spec
            else:
                if existing.parent_name and spec.parent_name and existing.parent_name != spec.parent_name:
                    raise FOMMergeError(
                        f"Interaction class {spec.full_name!r} has conflicting superclasses: {existing.parent_name!r} vs {spec.parent_name!r}"
                    )
                interactions[spec.full_name] = InteractionClassSpec(
                    spec.full_name,
                    _stable_union(existing.parameters, spec.parameters),
                    existing.parent_name or spec.parent_name,
                    _stable_union(existing.declared_parameters, spec.declared_parameters),
                    _stable_mapping_union(existing.parameter_datatypes, spec.parameter_datatypes),
                    existing.transportation or spec.transportation,
                )

    unique_time_impls = {name for name in time_impls if name}
    if len(unique_time_impls) > 1:
        raise FOMMergeError(f"Conflicting logical time implementations in FOM modules: {sorted(unique_time_impls)}")

    return FOMCatalog(
        modules=ordered_modules,
        mim_module=mim_module,
        object_classes=dict(sorted(objects.items())),
        interaction_classes=dict(sorted(interactions.items())),
        dimensions=frozenset(dimensions),
        datatype_names=frozenset(datatype_names),
        basic_datatypes=dict(sorted(basic_datatypes.items())),
        simple_datatypes=dict(sorted(simple_datatypes.items())),
        enumerated_datatypes=dict(sorted(enumerated_datatypes.items())),
        array_datatypes=dict(sorted(array_datatypes.items())),
        fixed_record_datatypes=dict(sorted(fixed_record_datatypes.items())),
        variant_record_datatypes=dict(sorted(variant_record_datatypes.items())),
        tag_representations={key: dict(sorted(value.items())) for key, value in sorted(tag_representations.items())},
        transportation_names=frozenset(transportation_names),
        update_rates=dict(sorted(update_rates.items())),
        synchronization_points={key: dict(sorted(value.items())) for key, value in sorted(synchronization_points.items())},
        switch_settings=dict(sorted(switch_settings.items())),
        notes=tuple(notes),
        logical_time_implementation=next(iter(unique_time_impls), None),
    )


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
    standard_catalog = _standard_mim_datatype_catalog()

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


def serialize_fom_module(module: FOMModule) -> str:
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
        ET.SubElement(transportation, f"{{{_IEEE_1516_2010_NAMESPACE}}}reliable").text = (
            _STRICT_OMT_TRANSPORTATION_RELIABILITY.get(name, "Yes")
        )

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
    ) = _serializer_datatype_sections(module)
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


@dataclass
class FOMResolver:
    """Resolve user FOM designators for Python and Java backends."""

    base_paths: tuple[str | os.PathLike[str], ...] = field(default_factory=tuple)
    parse_local_xml: bool = True
    require_local_parse: bool = False

    def resolve(self, source: Any) -> FOMModule:
        if isinstance(source, FOMModule):
            return source
        if str(source) == _STANDARD_MIM_NAME:
            return standard_mim_module()
        uri, path = normalize_module_uri(source, base_paths=self.base_paths)
        if path is not None and self.parse_local_xml and path.exists() and path.suffix.lower() in {".xml", ".fdd", ".fom"}:
            return parse_fom_xml(path, source=source, uri=uri)
        if self.require_local_parse and path is not None and not path.exists():
            raise FOMResolutionError(f"FOM module does not exist: {path}", kind="open")
        return FOMModule(source=source, uri=uri, path=path if path and path.exists() else None)

    def resolve_many(self, sources: Iterable[Any] | Any | None) -> tuple[FOMModule, ...]:
        if sources is None:
            return ()
        if isinstance(sources, FOMModule):
            return (sources,)
        if isinstance(sources, (str, bytes, os.PathLike)):
            return (self.resolve(sources),)
        try:
            return tuple(self.resolve(source) for source in sources)
        except TypeError:
            return (self.resolve(sources),)

    def merge(self, sources: Iterable[Any] | Any | None, *, mim_source: Any | None = None, include_standard_mim: bool = True) -> FOMCatalog:
        mim = self.resolve(mim_source) if mim_source is not None else (standard_mim_module() if include_standard_mim else None)
        return merge_fom_modules(self.resolve_many(sources), mim_module=mim)


__all__ = [
    "FOMCatalog",
    "OMTConformanceAssessment",
    "FOMMergeError",
    "FOMResolutionError",
    "ObjectClassSpec",
    "InteractionClassSpec",
    "FOMModule",
    "FOMResolver",
    "assess_omt_conformance",
    "default_fom_search_paths",
    "merge_fom_modules",
    "normalize_module_uri",
    "module_uri",
    "parse_fom_xml",
    "standard_mim_module",
]
