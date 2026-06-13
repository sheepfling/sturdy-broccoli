"""FOM/MIM resolution, merge, and public parser entrypoints."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote, unquote, urlparse, urlunparse

from ._fom_datatypes import validate_encoded_datatype_value as _validate_encoded_datatype_value
from ._fom_errors import FOMMergeError, FOMResolutionError
from ._fom_merge import merge_fom_modules
from . import _fom_parsing as _fom_parsing_module
from ._fom_models import (
    BasicDatatypeSpec,
    FOMCatalog,
    FOMModule,
    InteractionClassSpec,
    ObjectClassSpec,
    OMTConformanceAssessment,
    SimpleDatatypeSpec,
    datatype_summary,
)
from ._fom_parsing import parse_fom_xml as _parse_fom_xml
from ._fom_parsing import validate_fom_xml_schema as _validate_fom_xml_schema
from ._fom_serialization import serialize_fom_module as _serialize_fom_module

_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_STANDARD_MIM_NAME = "HLAstandardMIM"
LET = _fom_parsing_module.LET
_xml_schema = _fom_parsing_module._xml_schema


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
    """Return the built-in standard MIM/MOM development catalog."""

    path = _bundled_standard_mim_path()
    return parse_fom_xml(path, source=_STANDARD_MIM_NAME, uri=_path_to_file_uri(path))


def normalize_module_uri(source: Any, *, base_paths: Iterable[str | os.PathLike[str]] = ()) -> tuple[str, Path | None]:
    """Normalize a FOM/MIM source into ``(uri, local_path_or_none)``."""

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


def validate_fom_xml_schema(path: str | os.PathLike[str], *, profile: str = "dif") -> None:
    _fom_parsing_module.LET = LET
    _validate_fom_xml_schema(path, profile=profile)


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


@lru_cache(maxsize=1)
def _standard_mim_datatype_names() -> frozenset[str]:
    module = standard_mim_module()
    return frozenset(module.datatype_names)


@lru_cache(maxsize=1)
def _standard_mim_datatype_catalog() -> dict[str, Any]:
    module = standard_mim_module()
    return {
        **dict(module.basic_datatypes),
        **dict(module.simple_datatypes),
        **dict(module.enumerated_datatypes),
        **dict(module.array_datatypes),
        **dict(module.fixed_record_datatypes),
        **dict(module.variant_record_datatypes),
    }


def validate_encoded_datatype_value(payload: bytes, datatype_name: str, catalog: FOMCatalog | Mapping[str, Any] | None = None) -> None:
    _validate_encoded_datatype_value(
        payload,
        datatype_name,
        catalog,
        standard_catalog_factory=_standard_mim_datatype_catalog,
    )


def parse_fom_xml(
    path: str | os.PathLike[str],
    *,
    source: Any | None = None,
    uri: str | None = None,
    validate_schema: str | bool = False,
) -> FOMModule:
    _fom_parsing_module.LET = LET
    standard_datatype_names_factory = _standard_mim_datatype_names
    path_obj = Path(path)
    if source == _STANDARD_MIM_NAME or path_obj.name == "HLAstandardMIM.xml":
        standard_datatype_names_factory = lambda: frozenset()
    return _parse_fom_xml(
        path,
        source=source,
        uri=uri,
        validate_schema=validate_schema,
        default_uri_builder=_path_to_file_uri,
        standard_datatype_names_factory=standard_datatype_names_factory,
    )


def serialize_fom_module(module: FOMModule) -> str:
    """Serialize the implemented metadata subset of a FOM module to strict OMT XML."""

    return _serialize_fom_module(module, standard_catalog_factory=_standard_mim_datatype_catalog)


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
