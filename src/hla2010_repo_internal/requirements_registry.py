from __future__ import annotations

from typing import Any


def _load_source_of_truth() -> dict[str, Any]:
    from hla2010_repo_internal.requirements_source import load_source_of_truth

    return load_source_of_truth()


def edition_qualified_requirement_document_title(base_title: str, edition_year: int | str) -> str:
    normalized_title = str(base_title).strip()
    normalized_year = str(edition_year).strip()
    return f"{normalized_title} ({normalized_year} edition)" if normalized_title and normalized_year else normalized_title


def requirement_spec_registry(source: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = _load_source_of_truth() if source is None else source
    registry = data.get("requirement_id_registry")
    if not isinstance(registry, dict):
        return []
    specs = registry.get("specs")
    return list(specs) if isinstance(specs, list) else []


def requirement_active_bindings(source: dict[str, Any] | None = None) -> dict[str, str]:
    data = _load_source_of_truth() if source is None else source
    registry = data.get("requirement_id_registry")
    if not isinstance(registry, dict):
        return {}
    bindings = registry.get("active_bindings")
    if not isinstance(bindings, dict):
        return {}
    return {str(key): str(value) for key, value in bindings.items() if str(key).strip() and str(value).strip()}


def requirement_spec_by_alias(alias: str, source: dict[str, Any] | None = None) -> dict[str, Any] | None:
    candidate = str(alias).strip()
    if not candidate:
        return None
    for spec in requirement_spec_registry(source):
        if not isinstance(spec, dict):
            continue
        spec_id = str(spec.get("spec_id", "")).strip()
        legacy = str(spec.get("legacy_requirement_prefix", "")).strip()
        if candidate in {spec_id, legacy}:
            return dict(spec)
    return None


def requirement_active_binding_specs(source: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    bindings = requirement_active_bindings(source)
    resolved: dict[str, dict[str, Any]] = {}
    for binding_name, alias in bindings.items():
        spec = requirement_spec_by_alias(alias, source)
        if spec is not None:
            resolved[binding_name] = spec
    return resolved


def requirement_active_binding_editions(source: dict[str, Any] | None = None) -> dict[str, int]:
    editions: dict[str, int] = {}
    for binding_name, spec in requirement_active_binding_specs(source).items():
        edition_year = spec.get("edition_year")
        if isinstance(edition_year, int):
            editions[binding_name] = edition_year
    return editions


def requirement_selected_editions(source: dict[str, Any] | None = None) -> tuple[str, ...]:
    editions = {str(year) for year in requirement_active_binding_editions(source).values()}
    return tuple(sorted(editions))


def requirement_document_title_for_alias(alias: str, source: dict[str, Any] | None = None) -> str:
    spec = requirement_spec_by_alias(alias, source)
    if spec is not None:
        title = str(spec.get("document_title", "")).strip()
        if title:
            return title
    return str(alias).strip()


def requirement_document_title_for_binding(binding: str, source: dict[str, Any] | None = None) -> str:
    bindings = requirement_active_bindings(source)
    alias = bindings.get(str(binding).strip(), "").strip()
    if not alias:
        return str(binding).strip()
    return requirement_document_title_for_alias(alias, source)


def requirement_document_matches_alias(document: str, alias: str, source: dict[str, Any] | None = None) -> bool:
    return str(document).strip() == requirement_document_title_for_alias(alias, source)


def requirement_document_matches_binding(document: str, binding: str, source: dict[str, Any] | None = None) -> bool:
    return str(document).strip() == requirement_document_title_for_binding(binding, source)


def _requirement_document_title_aliases(spec: dict[str, Any]) -> tuple[str, ...]:
    title = str(spec.get("document_title", "")).strip()
    if not title:
        return ()
    edition_year = spec.get("edition_year")
    edition_suffix = f" ({edition_year} edition)" if isinstance(edition_year, int) else ""
    base_title = title.removesuffix(edition_suffix).strip() if edition_suffix else title
    aliases = {title, base_title}
    if base_title.startswith("IEEE "):
        aliases.add(base_title.removeprefix("IEEE ").strip())
    return tuple(sorted((alias for alias in aliases if alias), key=len, reverse=True))


def format_requirement_section_ref(document: str, section: str) -> str:
    normalized_document = str(document).strip()
    normalized_section = str(section).strip()
    if not normalized_section:
        return "unmapped"
    return f"{normalized_document} §{normalized_section}" if normalized_document else normalized_section


def normalize_requirement_section_ref(
    section_ref: str,
    *,
    default_document: str = "",
    source: dict[str, Any] | None = None,
) -> str:
    normalized = str(section_ref).strip()
    if not normalized:
        return normalized
    for spec in requirement_spec_registry(source):
        if not isinstance(spec, dict):
            continue
        title = str(spec.get("document_title", "")).strip()
        if not title:
            continue
        for alias in _requirement_document_title_aliases(spec):
            if normalized == alias:
                return title
            if normalized.startswith(alias):
                return f"{title}{normalized[len(alias):]}"
    if default_document and "§" in normalized:
        return format_requirement_section_ref(default_document, normalized.split("§", 1)[1].strip())
    return normalized


def format_requirement_clause_key(document: str, clause_root: str) -> str:
    normalized_document = str(document).strip()
    normalized_root = str(clause_root).strip()
    if normalized_root.lower() == "unknown" or not normalized_root:
        return f"{normalized_document} unknown" if normalized_document else "unknown"
    return format_requirement_section_ref(normalized_document, normalized_root)


def match_requirement_spec_prefix(value: str, source: dict[str, Any] | None = None) -> tuple[str, str] | None:
    aliases: list[str] = []
    for spec in requirement_spec_registry(source):
        if not isinstance(spec, dict):
            continue
        spec_id = str(spec.get("spec_id", "")).strip()
        legacy = str(spec.get("legacy_requirement_prefix", "")).strip()
        if spec_id:
            aliases.append(spec_id)
        if legacy:
            aliases.append(legacy)
    for alias in sorted(set(aliases), key=len, reverse=True):
        prefix = f"{alias}-"
        if not value.startswith(prefix):
            continue
        remainder = value[len(prefix) :]
        if "-" not in remainder:
            continue
        candidate_prefix = remainder.split("-", 1)[0].strip()
        if candidate_prefix:
            return alias, candidate_prefix
    return None


def validate_requirement_document_registry(source: dict[str, Any] | None = None) -> list[str]:
    data = _load_source_of_truth() if source is None else source
    errors: list[str] = []
    specs_by_id: dict[str, dict[str, Any]] = {}
    for spec in requirement_spec_registry(data):
        if not isinstance(spec, dict):
            errors.append("requirements source of truth requirement_id_registry.specs entries must be objects")
            continue
        spec_id = str(spec.get("spec_id", "")).strip()
        title = str(spec.get("document_title", "")).strip()
        edition_year = spec.get("edition_year")
        if not spec_id:
            errors.append("requirements source of truth requirement_id_registry.specs entries must define spec_id")
            continue
        specs_by_id[spec_id] = spec
        if not isinstance(edition_year, int):
            errors.append(
                f"requirements source of truth requirement_id_registry spec {spec_id} must define edition_year as an int"
            )
            continue
        if not spec_id.endswith(f"-{edition_year}"):
            errors.append(
                f"requirements source of truth requirement_id_registry spec {spec_id} must end with -{edition_year}"
            )
        base_title = title.removesuffix(f" ({edition_year} edition)").strip()
        expected_title = edition_qualified_requirement_document_title(base_title, edition_year)
        if title != expected_title:
            errors.append(
                f"requirements source of truth requirement_id_registry spec {spec_id} document_title must be {expected_title!r}"
            )
    registry = data.get("requirement_id_registry")
    sources = registry.get("sources", []) if isinstance(registry, dict) else []
    for source_row in sources:
        if not isinstance(source_row, dict):
            errors.append("requirements source of truth requirement_id_registry.sources entries must be objects")
            continue
        source_id = str(source_row.get("source_id", "")).strip()
        title = str(source_row.get("title", "")).strip()
        spec = specs_by_id.get(f"{source_id}-2010")
        if spec is None:
            continue
        expected_title = str(spec.get("document_title", "")).strip()
        if title != expected_title:
            errors.append(
                f"requirements source of truth requirement_id_registry source {source_id} title must match spec title {expected_title!r}"
            )
    return errors


__all__ = [
    "edition_qualified_requirement_document_title",
    "format_requirement_clause_key",
    "format_requirement_section_ref",
    "match_requirement_spec_prefix",
    "normalize_requirement_section_ref",
    "requirement_active_binding_editions",
    "requirement_active_binding_specs",
    "requirement_active_bindings",
    "requirement_document_matches_alias",
    "requirement_document_matches_binding",
    "requirement_document_title_for_alias",
    "requirement_document_title_for_binding",
    "requirement_selected_editions",
    "requirement_spec_by_alias",
    "requirement_spec_registry",
    "validate_requirement_document_registry",
]
