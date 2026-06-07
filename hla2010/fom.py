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
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote, unquote, urlparse, urlunparse


class FOMResolutionError(ValueError):
    """Raised when a FOM/MIM module designator cannot be resolved or parsed."""


class FOMMergeError(ValueError):
    """Raised when FOM modules cannot be merged into a single FDD catalog."""


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
    object_classes: tuple[ObjectClassSpec, ...] = ()
    interaction_classes: tuple[InteractionClassSpec, ...] = ()
    dimensions: tuple[str, ...] = ()
    inferred_time_implementation: str | None = None
    notes: tuple[str, ...] = ()
    is_mim: bool = False

    @property
    def parsed(self) -> bool:
        return bool(self.object_classes or self.interaction_classes or self.dimensions)


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
            "object_classes": sorted(self.object_classes),
            "interaction_classes": sorted(self.interaction_classes),
            "dimensions": sorted(self.dimensions),
            "logical_time_implementation": self.logical_time_implementation,
        }


_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_STANDARD_TIME_BY_DATATYPE_HINT = {
    "HLAfloat64BE": "HLAfloat64Time",
    "HLAfloat64LE": "HLAfloat64Time",
    "HLAinteger64BE": "HLAinteger64Time",
    "HLAinteger64LE": "HLAinteger64Time",
}
_STANDARD_MIM_NAME = "HLAstandardMIM"


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

    try:
        package_root = resources.files("hla2010")
        fom_root = package_root.joinpath("resources", "foms")
        package_path = Path(str(package_root))
        return (Path(str(fom_root)), package_path, package_path.parent)
    except Exception:
        return ()


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


def _walk_object_class(
    element: ET.Element,
    parent: str = "",
    inherited_attributes: tuple[str, ...] = (),
    inherited_datatypes: Mapping[str, str] | None = None,
) -> list[ObjectClassSpec]:
    name = _child_text(element, "name")
    if not name:
        return []
    inherited_datatypes = dict(inherited_datatypes or {})
    full_name = _append_path(parent, name)
    declared_names: list[str] = []
    declared_datatypes: dict[str, str] = {}
    for attr in _direct_children(element, "attribute"):
        attr_name = (_child_text(attr, "name") or "").strip()
        if not attr_name:
            continue
        declared_names.append(attr_name)
        data_type = (_child_text(attr, "dataType") or "").strip()
        if data_type:
            declared_datatypes[attr_name] = data_type
    declared = tuple(declared_names)
    available = _stable_union(inherited_attributes, declared)
    datatypes = _stable_mapping_union(inherited_datatypes, declared_datatypes)
    result = [ObjectClassSpec(full_name, available, parent or None, declared, datatypes)]
    for child in _direct_children(element, "objectClass"):
        result.extend(_walk_object_class(child, full_name, available, datatypes))
    return result


def _walk_interaction_class(
    element: ET.Element,
    parent: str = "",
    inherited_parameters: tuple[str, ...] = (),
    inherited_datatypes: Mapping[str, str] | None = None,
) -> list[InteractionClassSpec]:
    name = _child_text(element, "name")
    if not name:
        return []
    inherited_datatypes = dict(inherited_datatypes or {})
    full_name = _append_path(parent, name)
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
    result = [InteractionClassSpec(full_name, available, parent or None, declared, datatypes)]
    for child in _direct_children(element, "interactionClass"):
        result.extend(_walk_interaction_class(child, full_name, available, datatypes))
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


def parse_fom_xml(path: str | os.PathLike[str], *, source: Any | None = None, uri: str | None = None) -> FOMModule:
    """Parse the useful name-bearing subset of an IEEE 1516.2 object model."""

    path = Path(path)
    try:
        root = ET.parse(path).getroot()
    except FileNotFoundError as exc:
        raise FOMResolutionError(f"FOM module not found: {path}") from exc
    except ET.ParseError as exc:
        raise FOMResolutionError(f"Could not parse FOM XML {path}: {exc}") from exc

    if _local_name(root.tag) != "objectModel":
        raise FOMResolutionError(f"{path} does not look like an HLA objectModel document")

    model_identification = next((child for child in list(root) if _local_name(child.tag) == "modelIdentification"), None)
    model_name = _child_text(model_identification, "name")
    model_type = _child_text(model_identification, "type")

    objects_section = next((child for child in list(root) if _local_name(child.tag) == "objects"), None)
    object_classes: list[ObjectClassSpec] = []
    if objects_section is not None:
        for object_class in _direct_children(objects_section, "objectClass"):
            object_classes.extend(_walk_object_class(object_class))

    interactions_section = next((child for child in list(root) if _local_name(child.tag) == "interactions"), None)
    interaction_classes: list[InteractionClassSpec] = []
    if interactions_section is not None:
        for interaction_class in _direct_children(interactions_section, "interactionClass"):
            interaction_classes.extend(_walk_interaction_class(interaction_class))

    dimension_names: set[str] = set()
    dimensions_section = next((child for child in list(root) if _local_name(child.tag) == "dimensions"), None)
    if dimensions_section is not None:
        for dimension in _direct_children(dimensions_section, "dimension"):
            name = _child_text(dimension, "name")
            if name:
                dimension_names.add(name)

    for element in root.iter():
        if _local_name(element.tag) == "dimension" and element.text and not _direct_children(element, "name"):
            text = element.text.strip()
            if text:
                dimension_names.add(text)

    resolved_uri = uri or _path_to_file_uri(path)
    lower_type = (model_type or "").lower()
    lower_name = (model_name or "").lower()
    return FOMModule(
        source=source if source is not None else path,
        uri=resolved_uri,
        path=path,
        name=model_name,
        model_type=model_type,
        object_classes=tuple(object_classes),
        interaction_classes=tuple(interaction_classes),
        dimensions=tuple(sorted(dimension_names)),
        inferred_time_implementation=_infer_time_implementation(root),
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
    time_impls: list[str] = []

    for module in all_modules:
        if module.inferred_time_implementation:
            time_impls.append(module.inferred_time_implementation)
        dimensions.update(module.dimensions)

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
        logical_time_implementation=next(iter(unique_time_impls), None),
    )


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
            raise FOMResolutionError(f"FOM module does not exist: {path}")
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
    "FOMMergeError",
    "FOMResolutionError",
    "ObjectClassSpec",
    "InteractionClassSpec",
    "FOMModule",
    "FOMResolver",
    "default_fom_search_paths",
    "merge_fom_modules",
    "normalize_module_uri",
    "module_uri",
    "parse_fom_xml",
    "standard_mim_module",
]
