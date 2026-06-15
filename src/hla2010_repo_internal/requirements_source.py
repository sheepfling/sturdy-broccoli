from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from hla2010_repo_internal.requirements_registry import (
    edition_qualified_requirement_document_title,
    format_requirement_clause_key,
    format_requirement_section_ref,
    match_requirement_spec_prefix,
    requirement_active_bindings,
    requirement_document_matches_alias,
    requirement_document_matches_binding,
    requirement_document_title_for_alias,
    requirement_document_title_for_binding,
    requirement_spec_by_alias,
    requirement_spec_registry,
    validate_requirement_document_registry,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE_OF_TRUTH_PATH = ROOT / "requirements" / "source_of_truth.json"
SURFACE_MANIFEST_PATH = ROOT / "requirements" / "surface_manifest.json"
TRACEABILITY_MATRIX_PATH = ROOT / "requirements" / "traceability_matrix.csv"
ACTIVE_SERVICE_ROWS_PATH = ROOT / "requirements" / "active_service_rows.csv"
FAMILY_SEED_ROWS_PATH = ROOT / "requirements" / "family_seed_rows.csv"
REQUIREMENT_ID_REGISTRY_PATH = ROOT / "requirements" / "requirement_id_registry.yaml"
REQUIREMENTS_README_PATH = ROOT / "requirements" / "README.md"
REQUIREMENTS_CRUD_DOC_PATH = ROOT / "docs" / "requirements_crud.md"
REQUIREMENTS_EDIT_ONE_ROW_DOC_PATH = ROOT / "docs" / "requirements_edit_one_row.md"
REQUIREMENTS_TRACE_ONE_METHOD_DOC_PATH = ROOT / "docs" / "requirements_trace_one_method.md"
REQUIREMENTS_TRACEABILITY_DOC_PATH = ROOT / "docs" / "requirements_traceability.md"
REQUIREMENTS_AUTHORING_MAP_DOC_PATH = ROOT / "docs" / "requirements_authoring_map.md"

SURFACE_GROUP_KEYS = (
    "active_authored",
    "generated",
    "reference_provenance",
    "packet_entrypoints",
)
TRACEABILITY_FIELDNAMES = (
    "requirement_id",
    "source_document",
    "clause",
    "canonical_topic",
    "current_artifact_id",
    "implementation_refs",
    "test_refs",
    "artifact_refs",
    "status",
    "notes",
)

def load_source_of_truth() -> dict[str, Any]:
    return json.loads(SOURCE_OF_TRUTH_PATH.read_text(encoding="utf-8"))


def traceability_row_schema(source: dict[str, Any] | None = None) -> dict[str, Any]:
    data = load_source_of_truth() if source is None else source
    schema = data.get("traceability_row_schema")
    return dict(schema) if isinstance(schema, dict) else {}


def requirements_doc_projections(source: dict[str, Any] | None = None) -> dict[str, list[str]]:
    data = load_source_of_truth() if source is None else source
    projections = data.get("doc_projections")
    return dict(projections) if isinstance(projections, dict) else {}


def requirements_operator_projections(source: dict[str, Any] | None = None) -> dict[str, Any]:
    data = load_source_of_truth() if source is None else source
    projections = data.get("operator_projections")
    return dict(projections) if isinstance(projections, dict) else {}


def trace_examples(source: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = load_source_of_truth() if source is None else source
    examples = data.get("trace_examples")
    return list(examples) if isinstance(examples, list) else []

def validate_authored_requirement_row_documents(source: dict[str, Any] | None = None) -> list[str]:
    data = load_source_of_truth() if source is None else source
    errors: list[str] = []
    for path in (ACTIVE_SERVICE_ROWS_PATH, FAMILY_SEED_ROWS_PATH):
        for index, row in enumerate(_load_csv_rows(path), start=2):
            requirement_id = str(row.get("requirement_id", "")).strip()
            source_document = str(row.get("source_document", "")).strip()
            match = match_requirement_spec_prefix(requirement_id, data)
            if match is None:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}:{index}: requirement_id {requirement_id!r} does not resolve to a registered spec prefix"
                )
                continue
            alias, _ = match
            expected_document = requirement_document_title_for_alias(alias, data)
            if source_document != expected_document:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}:{index}: source_document for {requirement_id} must be {expected_document!r}, got {source_document!r}"
                )
    return errors


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def merged_traceability_rows() -> list[dict[str, str]]:
    active_rows = _load_csv_rows(ACTIVE_SERVICE_ROWS_PATH)
    family_rows = _load_csv_rows(FAMILY_SEED_ROWS_PATH)
    return [*family_rows, *active_rows]


def surface_manifest_projection(source: dict[str, Any]) -> dict[str, Any]:
    projection = {
        "version": int(source["version"]),
        "generated_from": SOURCE_OF_TRUTH_PATH.relative_to(ROOT).as_posix(),
    }
    for key in SURFACE_GROUP_KEYS:
        projection[key] = list(source[key])
    return projection


def validate_source_of_truth(source: dict[str, Any] | None = None) -> list[str]:
    data = load_source_of_truth() if source is None else source
    errors: list[str] = []
    if data.get("version") != 1:
        errors.append("requirements source of truth version must be 1")

    for key in SURFACE_GROUP_KEYS:
        entries = data.get(key)
        if not isinstance(entries, list) or not all(isinstance(item, str) for item in entries):
            errors.append(f"requirements source of truth {key!r} must be a list of strings")
            continue
        if not entries:
            errors.append(f"requirements source of truth {key!r} must not be empty")
            continue
        for rel_path in entries:
            if not (ROOT / rel_path).exists():
                errors.append(f"requirements source of truth missing path: {rel_path}")

    if data.get("normal_authoring_lane") != "active_service":
        errors.append("requirements source of truth normal_authoring_lane must be 'active_service'")

    if "requirements/active_service_rows.csv" not in data.get("active_authored", []):
        errors.append(
            "requirements source of truth must include requirements/active_service_rows.csv as active_authored"
        )
    if "requirements/family_seed_rows.csv" not in data.get("active_authored", []):
        errors.append(
            "requirements source of truth must include requirements/family_seed_rows.csv as active_authored"
        )
    if "requirements/source_of_truth.json" not in data.get("active_authored", []):
        errors.append(
            "requirements source of truth must include requirements/source_of_truth.json as active_authored"
        )

    registry = data.get("requirement_id_registry")
    if not isinstance(registry, dict):
        errors.append("requirements source of truth must contain requirement_id_registry")
        return errors

    sources = registry.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("requirements source of truth requirement_id_registry.sources must be a non-empty list")
    specs = registry.get("specs")
    if not isinstance(specs, list) or not specs:
        errors.append("requirements source of truth requirement_id_registry.specs must be a non-empty list")
    active_bindings = registry.get("active_bindings")
    if not isinstance(active_bindings, dict) or not active_bindings:
        errors.append("requirements source of truth requirement_id_registry.active_bindings must be a non-empty object")
    else:
        required_binding_keys = {"framework_rules", "federate_interface", "omt"}
        missing_bindings = sorted(required_binding_keys.difference(active_bindings))
        if missing_bindings:
            errors.append(
                "requirements source of truth requirement_id_registry.active_bindings is missing: "
                + ", ".join(missing_bindings)
            )
    id_format = registry.get("id_format")
    if not isinstance(id_format, dict):
        errors.append("requirements source of truth requirement_id_registry.id_format must be an object")
    errors.extend(validate_requirement_document_registry(data))

    schema = traceability_row_schema(data)
    if not schema:
        errors.append("requirements source of truth must contain traceability_row_schema")
        return errors

    field_order = schema.get("field_order")
    if list(field_order or []) != list(TRACEABILITY_FIELDNAMES):
        errors.append("requirements source of truth traceability_row_schema.field_order must match TRACEABILITY_FIELDNAMES")
    important_columns = schema.get("important_columns")
    if not isinstance(important_columns, list) or not important_columns:
        errors.append(
            "requirements source of truth traceability_row_schema.important_columns must be a non-empty list"
        )
    status_rules = schema.get("status_rules")
    if not isinstance(status_rules, list) or not status_rules:
        errors.append(
            "requirements source of truth traceability_row_schema.status_rules must be a non-empty list"
        )
    doc_projections = requirements_doc_projections(data)
    required_projection_keys = (
        "readme_start_here",
        "normal_edit_loop",
        "operator_surface_commands",
        "edit_one_row_discovery_commands",
        "edit_one_row_loop",
        "trace_loop_commands",
        "authoring_map_loop",
        "trace_intro_commands",
        "trace_stateful_commands",
        "crud_doc_actions",
        "traceability_operator_commands",
        "traceability_primary_surfaces",
        "traceability_edit_rule",
    )
    for key in required_projection_keys:
        entries = doc_projections.get(key)
        if not isinstance(entries, list) or not entries or not all(isinstance(item, str) for item in entries):
            errors.append(f"requirements source of truth doc_projections.{key} must be a non-empty list of strings")
    operator_projections = requirements_operator_projections(data)
    flow_sections = operator_projections.get("requirements_flow_sections")
    if not isinstance(flow_sections, list) or not flow_sections:
        errors.append(
            "requirements source of truth operator_projections.requirements_flow_sections must be a non-empty list"
        )
    source_sections = operator_projections.get("requirements_source_sections")
    if not isinstance(source_sections, list) or not source_sections:
        errors.append(
            "requirements source of truth operator_projections.requirements_source_sections must be a non-empty list"
        )
    examples = trace_examples(data)
    if len(examples) < 2:
        errors.append("requirements source of truth trace_examples must contain at least two examples")
    crud_actions = data.get("crud_actions")
    if not isinstance(crud_actions, list) or len(crud_actions) != 4:
        errors.append("requirements source of truth crud_actions must contain four action definitions")
    errors.extend(validate_authored_requirement_row_documents(data))
    return errors


def write_surface_manifest_from_source(source: dict[str, Any] | None = None) -> Path:
    data = load_source_of_truth() if source is None else source
    projection = surface_manifest_projection(data)
    SURFACE_MANIFEST_PATH.write_text(json.dumps(projection, indent=2) + "\n", encoding="utf-8")
    return SURFACE_MANIFEST_PATH


def validate_generated_traceability_matrix() -> list[str]:
    expected = merged_traceability_rows()
    current = _load_csv_rows(TRACEABILITY_MATRIX_PATH)
    if current != expected:
        return [
            "requirements traceability matrix is stale; run ./tools/human-editability generate-requirements-source"
        ]
    return []


def write_traceability_matrix_from_sources() -> Path:
    rows = merged_traceability_rows()
    with TRACEABILITY_MATRIX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACEABILITY_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in TRACEABILITY_FIELDNAMES})
    return TRACEABILITY_MATRIX_PATH


def _render_registry_yaml(source: dict[str, Any]) -> str:
    registry = dict(source["requirement_id_registry"])
    description = str(registry.get("description", "")).strip()
    lines: list[str] = [f"version: {registry['version']}"]
    if description:
        lines.append("description: >")
        for part in description.splitlines():
            lines.append(f"  {part.strip()}")
    lines.append("")
    lines.append("active_bindings:")
    for key, value in dict(registry.get("active_bindings", {})).items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append("specs:")
    for spec_row in registry.get("specs", []):
        lines.append(f"  - spec_id: {spec_row['spec_id']}")
        lines.append(f"    legacy_requirement_prefix: {spec_row['legacy_requirement_prefix']}")
        lines.append(f"    document_title: {spec_row['document_title']}")
        lines.append(f"    edition_year: {spec_row['edition_year']}")
        lines.append(f"    purpose: {spec_row['purpose']}")
    lines.append("")
    lines.append("sources:")
    for source_row in registry.get("sources", []):
        lines.append(f"  - source_id: {source_row['source_id']}")
        lines.append(f"    title: {source_row['title']}")
        lines.append(f"    purpose: {source_row['purpose']}")
        lines.append("    prefixes:")
        for prefix in source_row.get("prefixes", []):
            lines.append(f"      - prefix: {prefix['prefix']}")
            lines.append(f"        meaning: {prefix['meaning']}")
    lines.append("")
    lines.append("id_format:")
    lines.append(f"  pattern: \"{registry['id_format']['pattern']}\"")
    lines.append("  examples:")
    for example in registry["id_format"].get("examples", []):
        lines.append(f"    - {example}")
    return "\n".join(lines) + "\n"


def write_requirement_id_registry_from_source(source: dict[str, Any] | None = None) -> Path:
    data = load_source_of_truth() if source is None else source
    REQUIREMENT_ID_REGISTRY_PATH.write_text(_render_registry_yaml(data), encoding="utf-8")
    return REQUIREMENT_ID_REGISTRY_PATH


def _render_numbered_list(entries: list[str]) -> str:
    return "\n".join(f"{index}. {entry}" for index, entry in enumerate(entries, start=1))


def _render_bash_block(entries: list[str]) -> str:
    return "```bash\n" + "\n".join(entries) + "\n```"


def _replace_generated_block(text: str, block_id: str, content: str) -> str:
    start = f"<!-- GENERATED:{block_id}:START -->"
    end = f"<!-- GENERATED:{block_id}:END -->"
    start_index = text.find(start)
    end_index = text.find(end)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise ValueError(f"missing generated block markers for {block_id}")
    start_index += len(start)
    return text[:start_index] + "\n" + content.rstrip() + "\n" + text[end_index:]


def _render_crud_actions(actions: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        title = str(action.get("action", "")).strip().title()
        goal = str(action.get("goal", "")).strip()
        lines.append(f"## {title}")
        if goal:
            lines.append(goal + ".")
        edit_surface = str(action.get("edit_surface", "")).strip()
        if edit_surface and edit_surface != "none":
            lines.append("")
            lines.append(f"Edit here: `{edit_surface}`")
        commands = [str(item) for item in action.get("commands", [])]
        if commands:
            lines.append("")
            lines.append("Commands:")
            lines.append("")
            lines.append(_render_bash_block(commands))
        notes = action.get("notes", [])
        if isinstance(notes, list) and notes:
            lines.append("")
            lines.append("Notes:")
            for note in notes:
                lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_requirements_docs(source: dict[str, Any]) -> dict[Path, str]:
    projections = requirements_doc_projections(source)
    schema = traceability_row_schema(source)
    examples = trace_examples(source)
    crud_actions = source.get("crud_actions", [])
    rendered: dict[Path, str] = {}

    crud_text = REQUIREMENTS_CRUD_DOC_PATH.read_text(encoding="utf-8")
    crud_text = _replace_generated_block(
        crud_text,
        "CRUD_ACTIONS",
        _render_crud_actions(list(crud_actions) if isinstance(crud_actions, list) else []),
    )
    rendered[REQUIREMENTS_CRUD_DOC_PATH] = crud_text

    readme_text = REQUIREMENTS_README_PATH.read_text(encoding="utf-8")
    readme_text = _replace_generated_block(
        readme_text,
        "README_START_HERE",
        _render_numbered_list(list(projections["readme_start_here"])),
    )
    readme_text = _replace_generated_block(
        readme_text,
        "README_NORMAL_EDIT_LOOP",
        _render_numbered_list(list(projections["normal_edit_loop"])),
    )
    readme_text = _replace_generated_block(
        readme_text,
        "README_OPERATOR_COMMANDS",
        _render_bash_block(list(projections["operator_surface_commands"])),
    )
    rendered[REQUIREMENTS_README_PATH] = readme_text

    edit_text = REQUIREMENTS_EDIT_ONE_ROW_DOC_PATH.read_text(encoding="utf-8")
    edit_text = _replace_generated_block(
        edit_text,
        "EDIT_ONE_ROW_DISCOVERY_COMMANDS",
        _render_bash_block(list(projections["edit_one_row_discovery_commands"])),
    )
    edit_text = _replace_generated_block(
        edit_text,
        "EDIT_ONE_ROW_IMPORTANT_COLUMNS",
        "\n".join(f"- `{column}`" for column in schema.get("important_columns", [])),
    )
    edit_text = _replace_generated_block(
        edit_text,
        "EDIT_ONE_ROW_LOOP",
        _render_numbered_list(list(projections["edit_one_row_loop"])),
    )
    rendered[REQUIREMENTS_EDIT_ONE_ROW_DOC_PATH] = edit_text

    trace_text = REQUIREMENTS_TRACE_ONE_METHOD_DOC_PATH.read_text(encoding="utf-8")
    trace_text = _replace_generated_block(
        trace_text,
        "TRACE_ONE_METHOD_INTRO_COMMANDS",
        _render_bash_block(list(projections["trace_intro_commands"])),
    )
    if examples:
        first = examples[0]
        why_lines = "\n".join(f"- {entry}" for entry in first.get("why", []))
        open_lines = _render_numbered_list(list(first.get("open_paths", [])))
        content = "\n".join(
            [
                str(first.get("lead", "")).strip(),
                "",
                "It is the smallest requirement-to-code path because it:",
                "",
                why_lines,
                "",
                "Run:",
                "",
                _render_bash_block(list(first.get("commands", []))),
                "",
                "Then open:",
                "",
                open_lines,
            ]
        )
        trace_text = _replace_generated_block(trace_text, "TRACE_ONE_METHOD_FIRST_EXAMPLE", content)
    if len(examples) > 1:
        second = examples[1]
        content = "\n".join(
            [
                str(second.get("lead", "")).strip(),
                "",
                "Run:",
                "",
                _render_bash_block(list(second.get("commands", []))),
                "",
                "Then open:",
                "",
                _render_numbered_list(list(second.get("open_paths", []))),
            ]
        )
        trace_text = _replace_generated_block(trace_text, "TRACE_ONE_METHOD_STATEFUL_EXAMPLE", content)
    trace_text = _replace_generated_block(
        trace_text,
        "TRACE_ONE_METHOD_LOOP_COMMANDS",
        _render_bash_block(list(projections["trace_loop_commands"])),
    )
    rendered[REQUIREMENTS_TRACE_ONE_METHOD_DOC_PATH] = trace_text

    authoring_text = REQUIREMENTS_AUTHORING_MAP_DOC_PATH.read_text(encoding="utf-8")
    authoring_text = _replace_generated_block(
        authoring_text,
        "AUTHORING_MAP_LOOP",
        _render_numbered_list(list(projections["authoring_map_loop"])),
    )
    rendered[REQUIREMENTS_AUTHORING_MAP_DOC_PATH] = authoring_text

    traceability_text = REQUIREMENTS_TRACEABILITY_DOC_PATH.read_text(encoding="utf-8")
    traceability_text = _replace_generated_block(
        traceability_text,
        "TRACEABILITY_OPERATOR_COMMANDS",
        _render_bash_block(list(projections["traceability_operator_commands"])),
    )
    traceability_text = _replace_generated_block(
        traceability_text,
        "TRACEABILITY_PRIMARY_SURFACES",
        "\n".join(f"- {entry}" for entry in projections["traceability_primary_surfaces"]),
    )
    traceability_text = _replace_generated_block(
        traceability_text,
        "TRACEABILITY_EDIT_RULE",
        "\n".join(f"- {entry}" for entry in projections["traceability_edit_rule"]),
    )
    rendered[REQUIREMENTS_TRACEABILITY_DOC_PATH] = traceability_text
    return rendered


def write_requirements_docs_from_source(source: dict[str, Any] | None = None) -> tuple[Path, ...]:
    data = load_source_of_truth() if source is None else source
    rendered = _render_requirements_docs(data)
    for path, text in rendered.items():
        path.write_text(text, encoding="utf-8")
    return tuple(rendered)


def validate_generated_requirements_docs(source: dict[str, Any] | None = None) -> list[str]:
    data = load_source_of_truth() if source is None else source
    rendered = _render_requirements_docs(data)
    errors: list[str] = []
    for path, expected_text in rendered.items():
        current_text = path.read_text(encoding="utf-8")
        if current_text != expected_text:
            errors.append(
                f"{path.relative_to(ROOT).as_posix()} is stale; run ./tools/human-editability generate-requirements-source"
            )
    return errors


def write_requirements_generated_views(source: dict[str, Any] | None = None) -> tuple[Path, Path, Path, tuple[Path, ...]]:
    manifest_path = write_surface_manifest_from_source(source)
    traceability_path = write_traceability_matrix_from_sources()
    registry_path = write_requirement_id_registry_from_source(source)
    doc_paths = write_requirements_docs_from_source(source)
    return manifest_path, traceability_path, registry_path, doc_paths


__all__ = [
    "ACTIVE_SERVICE_ROWS_PATH",
    "FAMILY_SEED_ROWS_PATH",
    "REQUIREMENT_ID_REGISTRY_PATH",
    "ROOT",
    "SOURCE_OF_TRUTH_PATH",
    "SURFACE_GROUP_KEYS",
    "SURFACE_MANIFEST_PATH",
    "TRACEABILITY_FIELDNAMES",
    "TRACEABILITY_MATRIX_PATH",
    "edition_qualified_requirement_document_title",
    "load_source_of_truth",
    "format_requirement_section_ref",
    "format_requirement_clause_key",
    "merged_traceability_rows",
    "requirement_active_bindings",
    "requirement_document_matches_alias",
    "requirement_document_matches_binding",
    "requirement_document_title_for_alias",
    "requirement_document_title_for_binding",
    "requirement_spec_by_alias",
    "match_requirement_spec_prefix",
    "requirement_spec_registry",
    "requirements_doc_projections",
    "requirements_operator_projections",
    "surface_manifest_projection",
    "trace_examples",
    "traceability_row_schema",
    "validate_authored_requirement_row_documents",
    "validate_requirement_document_registry",
    "validate_generated_requirements_docs",
    "validate_generated_traceability_matrix",
    "validate_source_of_truth",
    "write_requirements_docs_from_source",
    "write_requirement_id_registry_from_source",
    "write_requirements_generated_views",
    "write_surface_manifest_from_source",
    "write_traceability_matrix_from_sources",
]
