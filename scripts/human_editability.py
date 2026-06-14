from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.traceability import (
    ACTIVE_SERVICE_INDEX_JSON_PATH,
    REQUIREMENTS_AUTHORING_INDEX_JSON_PATH,
    SERVICE_TRACE_INDEX_JSON_PATH,
    validate_active_traceability,
    write_active_service_index,
    write_requirements_authoring_index,
)
from hla2010_repo_internal.requirements_source import (
    ACTIVE_SERVICE_ROWS_PATH,
    FAMILY_SEED_ROWS_PATH,
    REQUIREMENT_ID_REGISTRY_PATH,
    SOURCE_OF_TRUTH_PATH as REQUIREMENTS_SOURCE_OF_TRUTH_PATH,
    SURFACE_MANIFEST_PATH as REQUIREMENTS_SURFACE_MANIFEST_PATH,
    TRACEABILITY_FIELDNAMES,
    load_source_of_truth,
    match_requirement_spec_prefix,
    requirement_active_bindings,
    requirement_document_title_for_binding,
    requirement_spec_registry,
    requirements_operator_projections,
    surface_manifest_projection,
    traceability_row_schema,
    validate_generated_requirements_docs,
    validate_generated_traceability_matrix,
    validate_source_of_truth,
    write_requirements_generated_views,
)


ROOT = SCRIPT_REPO_ROOT
INVENTORY_PATH = ROOT / "analysis" / "human_editability" / "smell_inventory.json"
LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
TRACEABILITY_PATH = ROOT / "requirements" / "traceability_matrix.csv"
SMELL_DOC_PATH = ROOT / "docs" / "plans" / "human_editability_smell_inventory.md"
PYTHON_RTI_SERVICE_MAP_JSON_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.json"
ARTIFACT_ID_PREFIX = "REQ-"
FRONT_DOORS: dict[str, dict[str, Any]] = {
    "spec": {
        "title": "Spec front door",
        "doc": ROOT / "docs" / "spec_reading_map.md",
        "goal": "Find the abstract/public HLA interfaces and spec metadata source.",
        "files": (
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec" / "__init__.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "runtime_api.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "ambassadors.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_inventory.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_refs.py",
            ROOT / "specs" / "hla2010_api.json",
        ),
    },
    "fom": {
        "title": "FOM front door",
        "doc": ROOT / "docs" / "fom_reading_map.md",
        "goal": "Find the parsing, merge, datatype-validation, and serialization edit surface for FOM behavior.",
        "files": (
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "fom.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "_fom_parsing.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "_fom_merge.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "_fom_datatypes.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "_fom_serialization.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "_fom_models.py",
            ROOT / "tests" / "factories" / "test_fom_omt_parsing.py",
        ),
    },
    "python-rti": {
        "title": "Python RTI front door",
        "doc": ROOT / "docs" / "python_rti_reading_map.md",
        "goal": "Find the main Python RTI edit loop and the exact service implementation surface.",
        "files": (
            ROOT / "docs" / "python_rti_backend.md",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "backend.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "service_registry.py",
            ROOT / "analysis" / "traceability" / "python_rti_service_map.md",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "time_public_services.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "state.py",
        ),
    },
    "python-rti-service": {
        "title": "Python RTI service-edit front door",
        "doc": ROOT / "docs" / "python_rti_edit_one_service.md",
        "goal": "Change one Python RTI service end to end without reading the whole backend family first.",
        "files": (
            ROOT / "docs" / "python_rti_edit_one_service.md",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "runtime_api.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "backend.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "service_registry.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "support_lookup.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "time_public_services.py",
            ROOT / "tests" / "backends" / "test_python_rti_service_registry.py",
            ROOT / "analysis" / "traceability" / "python_rti_service_map.md",
        ),
    },
    "rti-factories": {
        "title": "RTI factory front door",
        "doc": ROOT / "docs" / "rti_factory_reading_map.md",
        "goal": "List installed RTI factories, inspect selectable names, choose one, and instantiate it cleanly.",
        "files": (
            ROOT / "tools" / "rti-factories",
            ROOT / "scripts" / "rti_factories.py",
            ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "rti.py",
            ROOT / "packages" / "hla2010-rti-runtime-common" / "src" / "hla2010_rti_runtime_common" / "factory.py",
            ROOT / "packages" / "hla2010-rti-backend-common" / "src" / "hla2010_rti_backend_common" / "plugin_api.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "plugin.py",
        ),
    },
    "requirements": {
        "title": "Requirements front door",
        "doc": ROOT / "docs" / "requirements_crud.md",
        "goal": "Create, read, update, or delete one active requirement row without reading the whole traceability system first.",
        "files": (
            ROOT / "docs" / "requirements_crud.md",
            ROOT / "docs" / "requirements_trace_one_method.md",
            ROOT / "docs" / "requirements_edit_one_row.md",
            ROOT / "requirements" / "README.md",
            ROOT / "requirements" / "surface_manifest.json",
            ROOT / "requirements" / "traceability_matrix.csv",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "support_lookup.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "time_public_services.py",
            ROOT / "tests" / "scenarios" / "test_support_services_backend_matrix.py",
            ROOT / "tests" / "time" / "test_mom_mim_time_v10.py",
            ROOT / "docs" / "requirements_traceability.md",
            ROOT / "analysis" / "compliance" / "requirements_ledger.csv",
            ROOT / "analysis" / "traceability" / "service_trace_index.md",
            ROOT / "scripts" / "validate_traceability_paths.py",
            ROOT / "src" / "hla2010_repo_internal" / "traceability.py",
        ),
    },
    "requirements-trace": {
        "title": "Requirements front door",
        "doc": ROOT / "docs" / "requirements_trace_one_method.md",
        "goal": "Trace one method from requirement row to implementation and test evidence without reading the whole artifact stack first.",
        "files": (
            ROOT / "docs" / "requirements_trace_one_method.md",
            ROOT / "docs" / "requirements_edit_one_row.md",
            ROOT / "requirements" / "traceability_matrix.csv",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "support_lookup.py",
            ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "time_public_services.py",
            ROOT / "tests" / "scenarios" / "test_support_services_backend_matrix.py",
            ROOT / "tests" / "time" / "test_mom_mim_time_v10.py",
            ROOT / "analysis" / "traceability" / "service_trace_index.md",
        ),
    },
}


def _load_inventory() -> dict[str, Any]:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _split_refs(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def _inventory_checks() -> list[dict[str, Any]]:
    data = _load_inventory()
    checks = data.get("checks")
    if not isinstance(checks, list):
        raise ValueError("smell inventory must contain a 'checks' list")
    return checks


def _load_requirements_surface_manifest() -> dict[str, Any]:
    return json.loads(REQUIREMENTS_SURFACE_MANIFEST_PATH.read_text(encoding="utf-8"))


def _validate_requirements_surface_manifest() -> list[str]:
    errors: list[str] = []
    source = load_source_of_truth()
    manifest = _load_requirements_surface_manifest()
    errors.extend(validate_source_of_truth(source))
    errors.extend(validate_generated_traceability_matrix())
    errors.extend(validate_generated_requirements_docs(source))
    expected_manifest = surface_manifest_projection(source)
    if manifest != expected_manifest:
        errors.append(
            "requirements surface manifest is stale; run ./tools/human-editability generate-requirements-source"
        )
    return errors


def _validate_inventory() -> list[str]:
    errors: list[str] = []
    data = _load_inventory()
    if data.get("version") != 1:
        errors.append("smell inventory version must be 1")

    for index, check in enumerate(_inventory_checks(), start=1):
        prefix = f"check[{index}]"
        check_id = str(check.get("id", "")).strip()
        status = str(check.get("status", "")).strip()
        remediation = str(check.get("remediation_workstream", "")).strip()
        verification = check.get("verification", [])
        if not check_id:
            errors.append(f"{prefix}: missing id")
        if status not in {"open", "closed"}:
            errors.append(f"{prefix} {check_id or '<missing>'}: invalid status {status!r}")
        if status == "open" and not remediation:
            errors.append(f"{prefix} {check_id}: open smell missing remediation_workstream")
        if status == "closed":
            if not isinstance(verification, list) or not any(str(item).strip() for item in verification):
                errors.append(f"{prefix} {check_id}: closed smell missing verification commands")
    return errors


def _format_open_smell(check: dict[str, Any]) -> str:
    return (
        f"- {check['id']} [{check['owner_area']}] -> {check['remediation_workstream']}: "
        f"{check['title']} ({check['remediation_target']})"
    )


def cmd_inventory(_: argparse.Namespace) -> int:
    checks = _inventory_checks()
    open_checks = [check for check in checks if check.get("status") == "open"]
    closed_checks = [check for check in checks if check.get("status") == "closed"]

    print("Human editability smell inventory")
    print(f"source: {INVENTORY_PATH.relative_to(ROOT).as_posix()}")
    print(f"doc: {SMELL_DOC_PATH.relative_to(ROOT).as_posix()}")
    print(f"open: {len(open_checks)}")
    print(f"closed: {len(closed_checks)}")
    print("")
    print("Open smells:")
    for check in open_checks:
        print(_format_open_smell(check))
    if closed_checks:
        print("")
        print("Closed smells with guards:")
        for check in closed_checks:
            verification = ", ".join(check.get("verification", []))
            print(f"- {check['id']} [{check['owner_area']}] -> {verification}")
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    errors = _validate_inventory()
    errors.extend(_validate_requirements_surface_manifest())
    if errors:
        print("Human editability check failed")
        for error in errors:
            print(f"- {error}")
        return 1

    traceability_errors = validate_active_traceability()
    if traceability_errors:
        print("Human editability check failed")
        for error in traceability_errors:
            print(
                f"- {error.source}:{error.row_id}:{error.field}: {error.message}: {error.ref}"
            )
        return 1

    checks = _inventory_checks()
    open_checks = [check for check in checks if check.get("status") == "open"]
    print("Human editability check passed")
    print(f"inventory: {INVENTORY_PATH.relative_to(ROOT).as_posix()}")
    print(f"requirements_source: {REQUIREMENTS_SOURCE_OF_TRUTH_PATH.relative_to(ROOT).as_posix()}")
    print(f"requirements_surfaces: {REQUIREMENTS_SURFACE_MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print("requirements_surface_validation: passed")
    print("traceability_validation: passed")
    print(f"remaining_open_smells: {len(open_checks)}")
    for check in open_checks:
        print(_format_open_smell(check))
    return 0


def _print_front_door(name: str) -> None:
    front_door = FRONT_DOORS[name]
    print(f"{front_door['title']}:")
    print(f"goal: {front_door['goal']}")
    doc_path = Path(front_door["doc"])
    print(f"doc: {doc_path.relative_to(ROOT).as_posix()}")
    print("read in order:")
    for index, path in enumerate(front_door["files"], start=1):
        rel = Path(path).relative_to(ROOT).as_posix()
        print(f"  {index}. {rel}")
    print("")


def cmd_front_doors(args: argparse.Namespace) -> int:
    topic = args.topic
    ordered_topics = ("spec", "fom", "python-rti", "python-rti-service", "rti-factories", "requirements")
    print("Human editability front doors")
    print(f"onboarding: {(ROOT / 'docs' / 'onboarding.md').relative_to(ROOT).as_posix()}")
    print("")
    if topic == "all":
        for name in ordered_topics:
            _print_front_door(name)
        return 0
    alias = "requirements" if topic == "requirements-trace" else topic
    _print_front_door(alias)
    return 0


def _print_surface_group(title: str, entries: list[str]) -> None:
    print(f"{title}:")
    for entry in entries:
        print(f"  - {entry}")
    print("")


def _print_surface_examples(title: str, entries: list[str], *, examples: int = 5) -> None:
    print(f"{title}:")
    print(f"  count: {len(entries)}")
    print("  examples:")
    for entry in entries[:examples]:
        print(f"    - {entry}")
    remaining = len(entries) - min(len(entries), examples)
    if remaining > 0:
        print(f"  more: {remaining} additional paths")
        print("  see_all: ./tools/human-editability requirements-surfaces --verbose")
    print("")


def _print_operator_projection_section(index: int, section: dict[str, Any]) -> None:
    title = str(section.get("title", "")).strip() or f"Section {index}"
    print(f"{index}. {title}")
    items = section.get("items", [])
    if not isinstance(items, list):
        print("")
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "")).strip() or "item"
        value = str(item.get("value", "")).strip()
        if value:
            print(f"   {kind}: {value}")
    print("")


def cmd_requirements_surfaces(args: argparse.Namespace) -> int:
    data = load_source_of_truth()
    print("Human editability requirements surfaces")
    print(f"source_of_truth: {REQUIREMENTS_SOURCE_OF_TRUTH_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_manifest: {REQUIREMENTS_SURFACE_MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print("normal_flow: trace one method -> edit one row only if needed -> validate -> regenerate outputs")
    print("start_here: docs/requirements_trace_one_method.md")
    print("")
    _print_surface_group("Active authored", list(data["active_authored"]))
    _print_surface_group("Generated", list(data["generated"]))
    if args.verbose:
        _print_surface_group("Reference / provenance", list(data["reference_provenance"]))
    else:
        _print_surface_examples("Reference / provenance", list(data["reference_provenance"]))
    _print_surface_group("Packet entrypoints", list(data["packet_entrypoints"]))
    return 0


def cmd_requirements_flow(_: argparse.Namespace) -> int:
    projections = requirements_operator_projections()
    sections = projections.get("requirements_flow_sections", [])
    print("Human editability requirements flow")
    print("goal: trace one method first, then edit only the active mapping row if the trace is wrong")
    print("")
    if isinstance(sections, list):
        for index, section in enumerate(sections, start=1):
            if isinstance(section, dict):
                _print_operator_projection_section(index, section)
    return 0


def cmd_requirements_crud(_: argparse.Namespace) -> int:
    data = load_source_of_truth()
    actions = data.get("crud_actions", [])
    print("Human editability requirements CRUD")
    print("goal: make create, read, update, and delete of one active requirement row obvious")
    print("doc: docs/requirements_crud.md")
    print("edit_surface: requirements/active_service_rows.csv")
    print("")
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            name = str(action.get("action", "")).strip().upper()
            goal = str(action.get("goal", "")).strip()
            print(f"{name}: {goal}")
            for command in action.get("commands", []):
                print(f"  command: {command}")
            for note in action.get("notes", []):
                print(f"  note: {note}")
            print("")
    return 0


def cmd_requirements_create(args: argparse.Namespace) -> int:
    print("Human editability requirements create")
    print("goal: add one missing active requirement row")
    print("edit_surface: requirements/active_service_rows.csv")
    print("")
    return cmd_requirement_template(argparse.Namespace(row_id=args.row_id))


def cmd_requirements_read(args: argparse.Namespace) -> int:
    target = args.target
    print("Human editability requirements read")
    print("goal: read one requirement or one traced method without guessing")
    print("")
    parts = _requirement_id_parts(target)
    if target.startswith(ARTIFACT_ID_PREFIX) or parts is not None:
        print(f"mode: requirement")
        print("")
        return cmd_requirement(argparse.Namespace(requirement_id=target))
    print("mode: trace-summary")
    print("")
    return cmd_trace_summary(argparse.Namespace(method=target))


def cmd_requirements_update(args: argparse.Namespace) -> int:
    requirement_id = args.requirement_id
    print("Human editability requirements update")
    print("goal: change one existing active requirement row")
    print("edit_surface: requirements/active_service_rows.csv")
    print("")
    result = cmd_requirement(argparse.Namespace(requirement_id=requirement_id))
    print("")
    print("Next steps:")
    print("1. Edit requirements/active_service_rows.csv.")
    print("2. Run ./tools/human-editability check.")
    print("3. Run ./tools/human-editability generate-requirements-source.")
    print("4. Run ./tools/human-editability generate-trace-index.")
    return result


def cmd_requirements_delete(args: argparse.Namespace) -> int:
    requirement_id = args.requirement_id
    print("Human editability requirements delete")
    print("goal: remove one wrong or obsolete active requirement row")
    print("edit_surface: requirements/active_service_rows.csv")
    print("")
    result = cmd_requirement(argparse.Namespace(requirement_id=requirement_id))
    print("")
    print("Delete steps:")
    print("1. Remove the row from requirements/active_service_rows.csv.")
    print("2. Do not edit generated outputs directly.")
    print("3. Run ./tools/human-editability check.")
    print("4. Run ./tools/human-editability generate-requirements-source.")
    print("5. Run ./tools/human-editability generate-trace-index.")
    print("6. Re-run ./tools/human-editability trace-summary <MethodName> if the row was method-linked.")
    return result


def cmd_requirements_source(_: argparse.Namespace) -> int:
    data = load_source_of_truth()
    schema = traceability_row_schema(data)
    projections = requirements_operator_projections(data)
    specs = requirement_spec_registry(data)
    print("Human editability requirements source of truth")
    print(f"source: {REQUIREMENTS_SOURCE_OF_TRUTH_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_manifest: {REQUIREMENTS_SURFACE_MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_merge: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_registry: {REQUIREMENT_ID_REGISTRY_PATH.relative_to(ROOT).as_posix()}")
    print(f"normal_authoring_lane: {data.get('normal_authoring_lane', '')}")
    print("")
    sections = projections.get("requirements_source_sections", [])
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, dict):
                continue
            title = str(section.get("title", "")).strip()
            source_key = str(section.get("source_key", "")).strip()
            values = section.get("values")
            if not title:
                continue
            print(f"{title}:")
            if source_key:
                for entry in data.get(source_key, []):
                    print(f"  - {entry}")
            elif isinstance(values, list):
                for entry in values:
                    print(f"  - {entry}")
            print("")
    print("Policies:")
    for key, value in dict(data.get("policies", {})).items():
        print(f"  - {key}: {value}")
    print("")
    print("Supported spec editions:")
    for spec in specs:
        if not isinstance(spec, dict):
            continue
        spec_id = str(spec.get("spec_id", "")).strip()
        legacy = str(spec.get("legacy_requirement_prefix", "")).strip()
        title = str(spec.get("document_title", "")).strip()
        if spec_id:
            if legacy:
                print(f"  - {spec_id} (legacy prefix: {legacy}) -> {title}")
            else:
                print(f"  - {spec_id} -> {title}")
    print("")
    print("Active spec bindings:")
    for binding, spec_id in requirement_active_bindings(data).items():
        print(f"  - {binding}: {spec_id} -> {requirement_document_title_for_binding(binding, data)}")
    print("")
    print("Traceability row schema:")
    print("  - field_order: " + ", ".join(str(item) for item in schema.get("field_order", [])))
    print("  - important_columns: " + ", ".join(str(item) for item in schema.get("important_columns", [])))
    return 0


def _load_requirement_id_registry() -> tuple[dict[str, str], dict[str, str]]:
    source_titles: dict[str, str] = {}
    prefixes: dict[str, str] = {}
    data = load_source_of_truth()
    registry = dict(data.get("requirement_id_registry", {}))
    source_prefix_rows: dict[str, list[dict[str, Any]]] = {}
    for source_row in registry.get("sources", []):
        if not isinstance(source_row, dict):
            continue
        source_id = str(source_row.get("source_id", "")).strip()
        if source_id:
            source_prefix_rows[source_id] = list(source_row.get("prefixes", []))
    spec_title_by_alias: dict[str, str] = {}
    spec_base_source_by_alias: dict[str, str] = {}
    for spec in requirement_spec_registry(data):
        if not isinstance(spec, dict):
            continue
        spec_id = str(spec.get("spec_id", "")).strip()
        legacy = str(spec.get("legacy_requirement_prefix", "")).strip()
        title = str(spec.get("document_title", "")).strip()
        if spec_id:
            spec_title_by_alias[spec_id] = title or spec_id
        if legacy:
            spec_title_by_alias[legacy] = title or legacy
        if legacy:
            spec_base_source_by_alias[legacy] = legacy
        if spec_id and legacy:
            spec_base_source_by_alias[spec_id] = legacy
    for source_row in registry.get("sources", []):
        if not isinstance(source_row, dict):
            continue
        source_id = str(source_row.get("source_id", "")).strip()
        title = spec_title_by_alias.get(source_id, "").strip() or str(source_row.get("title", "")).strip()
        if not source_id:
            continue
        source_titles[source_id] = title or source_id
        for prefix_row in source_row.get("prefixes", []):
            if not isinstance(prefix_row, dict):
                continue
            prefix = str(prefix_row.get("prefix", "")).strip()
            if prefix:
                prefixes[f"{source_id}:{prefix}"] = source_titles[source_id]
    for alias, title in spec_title_by_alias.items():
        source_titles.setdefault(alias, title)
        base_source = spec_base_source_by_alias.get(alias, "")
        for prefix_row in source_prefix_rows.get(base_source, []):
            if not isinstance(prefix_row, dict):
                continue
            prefix = str(prefix_row.get("prefix", "")).strip()
            if prefix:
                prefixes[f"{alias}:{prefix}"] = title
    return source_titles, prefixes


def _requirement_id_parts(value: str) -> tuple[str, str] | None:
    return match_requirement_spec_prefix(value, load_source_of_truth())


def _render_csv_row(fields: dict[str, str]) -> str:
    return ",".join(fields[name] for name in TRACEABILITY_FIELDNAMES)


def cmd_requirement_template(args: argparse.Namespace) -> int:
    row_id = args.row_id
    source_titles, prefixes = _load_requirement_id_registry()
    schema = traceability_row_schema()
    status_rules = schema.get("status_rules", [])

    requirement_id = "<requirement_id>"
    current_artifact_id = "<current_artifact_id>"
    registry_message = "edit only if you need a new source/prefix family"
    source_document = "<source_document>"
    clause = "<clause>"

    if row_id:
        if row_id.startswith(ARTIFACT_ID_PREFIX):
            current_artifact_id = row_id
            registry_message = (
                "artifact id detected; keep this in current_artifact_id and use a standards-row requirement_id"
            )
        else:
            requirement_id = row_id
            parts = _requirement_id_parts(row_id)
            if parts is not None:
                source_id, prefix = parts
                source_document = source_titles.get(source_id, "<source_document>")
                if f"{source_id}:{prefix}" in prefixes:
                    registry_message = f"no registry edit needed; {source_id}/{prefix} already exists"
                else:
                    registry_message = f"add {source_id}/{prefix} to requirements/source_of_truth.json first"
                prefix_head = f"{source_id}-{prefix}-"
                if row_id.startswith(prefix_head):
                    remainder = row_id[len(prefix_head) :]
                    clause = remainder.rsplit("-", 1)[0].replace("_", ".")
            else:
                registry_message = (
                    "unrecognized requirement-id family; use a standards-row id here and put REQ-* values in current_artifact_id"
                )

    row = {
        "requirement_id": requirement_id,
        "source_document": source_document,
        "clause": clause,
        "canonical_topic": "<canonical_topic>",
        "current_artifact_id": current_artifact_id,
        "implementation_refs": "<implementation_refs>",
        "test_refs": "<test_refs>",
        "artifact_refs": "<artifact_refs>",
        "status": "planned",
        "notes": "<notes>",
    }

    print("Human editability requirement template")
    print("goal: add one active requirement row without guessing the CSV shape")
    print(f"active_authored_surface: {ACTIVE_SERVICE_ROWS_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_merge: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"registry_source: {REQUIREMENTS_SOURCE_OF_TRUTH_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_registry: {REQUIREMENT_ID_REGISTRY_PATH.relative_to(ROOT).as_posix()}")
    if row_id:
        print(f"input: {row_id}")
    print(f"registry_action: {registry_message}")
    print("")
    print("CSV header:")
    print(",".join(str(name) for name in schema.get("field_order", TRACEABILITY_FIELDNAMES)))
    print("")
    print("CSV row template:")
    print(_render_csv_row(row))
    print("")
    print("Status rules:")
    for entry in status_rules:
        if not isinstance(entry, dict):
            continue
        print(f"- {entry.get('status', '')}: {entry.get('meaning', '')}")
    print("")
    print("Normal lane:")
    print("1. Paste the row into requirements/active_service_rows.csv")
    print("2. Edit implementation_refs, test_refs, artifact_refs, status, and notes")
    print("3. Run ./tools/human-editability check")
    print("4. Run ./tools/human-editability generate-trace-index")
    print("5. Run ./tools/human-editability requirement <RequirementId>")
    return 0


def _load_requirements_authoring_index() -> dict[str, Any]:
    if not REQUIREMENTS_AUTHORING_INDEX_JSON_PATH.exists():
        write_requirements_authoring_index()
    return json.loads(REQUIREMENTS_AUTHORING_INDEX_JSON_PATH.read_text(encoding="utf-8"))


def cmd_requirements_lanes(_: argparse.Namespace) -> int:
    payload = _load_requirements_authoring_index()
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    active_rows = [row for row in rows if isinstance(row, dict) and row.get("lane") == "active_service"]
    family_rows = [row for row in rows if isinstance(row, dict) and row.get("lane") == "family_seed"]

    print("Human editability requirements lanes")
    print(f"active_authored_surface: {ACTIVE_SERVICE_ROWS_PATH.relative_to(ROOT).as_posix()}")
    print(f"family_seed_surface: {FAMILY_SEED_ROWS_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_merge: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_index: {REQUIREMENTS_AUTHORING_INDEX_JSON_PATH.relative_to(ROOT).as_posix()}")
    print("normal_authoring_lane: active_service")
    print("")
    print(f"active_service_count: {len(active_rows)}")
    print(f"family_seed_count: {len(family_rows)}")
    print("")
    print("Family seed rows:")
    for row in family_rows:
        print(
            f"- {row.get('requirement_id', '')}: {row.get('clause', '')} [{row.get('status', '')}] "
            f"-> {row.get('lane_reason', '')}"
        )
    print("")
    print("Active service examples:")
    for row in active_rows[:8]:
        print(
            f"- {row.get('requirement_id', '')}: {row.get('clause', '')} "
            f"({row.get('canonical_topic', '')})"
        )
    print("")
    print("Normal lane:")
    print("1. Trace one method with ./tools/human-editability trace-summary <MethodName>")
    print("2. Print a row shape with ./tools/human-editability requirement-template <RequirementIdOrArtifactId>")
    print("3. Edit requirements/active_service_rows.csv only for active_service rows")
    print("4. Leave family_seed rows alone unless you are doing deliberate clause-family harmonization")
    return 0


def _load_active_service_index() -> dict[str, Any]:
    if not ACTIVE_SERVICE_INDEX_JSON_PATH.exists():
        write_active_service_index()
    return json.loads(ACTIVE_SERVICE_INDEX_JSON_PATH.read_text(encoding="utf-8"))


def cmd_requirements_active(args: argparse.Namespace) -> int:
    payload = _load_active_service_index()
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        rows = []

    query = (args.query or "").casefold().strip()
    if query:
        rows = [
            row
            for row in rows
            if isinstance(row, dict)
            and query
            in " ".join(
                str(row.get(key, ""))
                for key in (
                    "requirement_id",
                    "clause",
                    "canonical_topic",
                    "current_artifact_id",
                    "implementation_refs",
                )
            ).casefold()
        ]
        if not rows:
            trace_rows = _normalized_trace_matches(args.query or "")
            linked_ids = {
                str(row.get("requirement_id", "")).strip()
                for row in trace_rows
                if isinstance(row, dict) and str(row.get("requirement_id", "")).strip()
            }
            linked_sections = {
                str(row.get("section", "")).strip().split("§", 1)[-1].strip()
                for row in trace_rows
                if isinstance(row, dict) and str(row.get("section", "")).strip()
            }
            if linked_ids:
                rows = [
                    row
                    for row in payload.get("rows", [])
                    if isinstance(row, dict)
                    and (
                        str(row.get("requirement_id", "")).strip() in linked_ids
                        or str(row.get("current_artifact_id", "")).strip() in linked_ids
                    )
                ]
            if not rows and linked_sections:
                rows = [
                    row
                    for row in payload.get("rows", [])
                    if isinstance(row, dict)
                    and str(row.get("clause", "")).strip() in linked_sections
                ]

    print("Human editability active service requirements")
    print(f"active_authored_surface: {ACTIVE_SERVICE_ROWS_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_merge: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_index: {ACTIVE_SERVICE_INDEX_JSON_PATH.relative_to(ROOT).as_posix()}")
    if query:
        print(f"query: {args.query}")
    print(f"match_count: {len(rows)}")
    print("")
    for row in rows[:25]:
        print(f"requirement_id: {row.get('requirement_id', '')}")
        print(f"clause: {row.get('clause', '')}")
        print(f"canonical_topic: {row.get('canonical_topic', '')}")
        print(f"current_artifact_id: {row.get('current_artifact_id', '') or '-'}")
        print(f"status: {row.get('status', '')}")
        print(f"implementation_refs: {row.get('implementation_refs', '') or '-'}")
        print(f"test_refs: {row.get('test_refs', '') or '-'}")
        print("")
    if len(rows) > 25:
        print(f"more: {len(rows) - 25} additional active_service rows")
    print("normal_use: search here first before opening requirements/active_service_rows.csv")
    return 0


def _ledger_matches(query: str) -> list[dict[str, str]]:
    normalized = query.casefold()
    matches: list[dict[str, str]] = []
    for row in _load_csv(LEDGER_PATH):
        for key in ("method", "python_name", "requirement_id"):
            value = row.get(key, "")
            if value and value.casefold() == normalized:
                matches.append(row)
                break
        else:
            method = row.get("method", "")
            python_name = row.get("python_name", "")
            if normalized in method.casefold() or normalized in python_name.casefold():
                matches.append(row)
    return matches


def _traceability_matches(query: str) -> list[dict[str, str]]:
    normalized = query.casefold()
    matches: list[dict[str, str]] = []
    for row in _load_csv(TRACEABILITY_PATH):
        haystacks = (
            row.get("source_document", ""),
            row.get("clause", ""),
            row.get("current_artifact_id", ""),
            row.get("canonical_topic", ""),
            row.get("implementation_refs", ""),
            row.get("notes", ""),
        )
        if any(normalized in value.casefold() for value in haystacks if value):
            matches.append(row)
    return matches


def _traceability_requirement_rows(requirement_id: str) -> list[dict[str, str]]:
    normalized = requirement_id.casefold()
    return [
        row
        for row in _load_csv(TRACEABILITY_PATH)
        if row.get("requirement_id", "").casefold() == normalized
        or row.get("current_artifact_id", "").casefold() == normalized
    ]


def _service_trace_index_rows() -> list[dict[str, Any]]:
    if not SERVICE_TRACE_INDEX_JSON_PATH.exists():
        return []
    payload = json.loads(SERVICE_TRACE_INDEX_JSON_PATH.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    return rows if isinstance(rows, list) else []


def _ledger_requirement_rows(requirement_id: str) -> list[dict[str, str]]:
    normalized = requirement_id.casefold()
    ledger_rows = [
        row
        for row in _load_csv(LEDGER_PATH)
        if row.get("requirement_id", "").casefold() == normalized
    ]
    if ledger_rows:
        return ledger_rows
    indexed_rows = [
        row
        for row in _service_trace_index_rows()
        if isinstance(row, dict) and str(row.get("requirement_id", "")).casefold() == normalized
    ]
    return [{str(key): str(value) for key, value in row.items()} for row in indexed_rows]


def _print_active_requirement_row(row: dict[str, str]) -> None:
    print(f"requirement_id: {row.get('requirement_id', '')}")
    print(f"source_document: {row.get('source_document', '')}")
    print(f"clause: {row.get('clause', '')}")
    print(f"canonical_topic: {row.get('canonical_topic', '')}")
    print(f"current_artifact_id: {row.get('current_artifact_id', '')}")
    print(f"implementation_refs: {row.get('implementation_refs', '') or '-'}")
    print(f"test_refs: {row.get('test_refs', '') or '-'}")
    print(f"artifact_refs: {row.get('artifact_refs', '') or '-'}")
    print(f"status: {row.get('status', '')}")
    print(f"notes: {row.get('notes', '') or '-'}")


def _python_rti_service_map_match(method_name: str, python_name: str) -> dict[str, str] | None:
    if not PYTHON_RTI_SERVICE_MAP_JSON_PATH.exists():
        return None
    payload = json.loads(PYTHON_RTI_SERVICE_MAP_JSON_PATH.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("hla_method") == method_name or row.get("python_name") == python_name:
            return {str(key): str(value) for key, value in row.items()}
    return None


def _print_trace_row(row: dict[str, str]) -> None:
    positive_tests = _split_refs(row.get("positive_test_refs", ""))
    negative_tests = _split_refs(row.get("negative_test_refs", ""))
    artifact_refs = _split_refs(row.get("artifact_refs", ""))
    implementation_refs = _split_refs(row.get("implementation_refs", ""))
    service_map_row = _python_rti_service_map_match(row.get("method", ""), row.get("python_name", ""))
    if service_map_row is not None:
        implementation_refs = [
            service_map_row.get("implementation_symbol", ""),
            service_map_row.get("implementation_module", ""),
        ]
    print(f"requirement_id: {row.get('requirement_id', '')}")
    print(f"section: {row.get('section', '')}")
    print(f"service_group: {row.get('service_group', '')}")
    print(f"hla_method: {row.get('method', '')}")
    print(f"python_name: {row.get('python_name', '')}")
    print(f"implementation_refs: {'; '.join(implementation_refs) if implementation_refs else '-'}")
    print(f"positive_test_refs: {'; '.join(positive_tests) if positive_tests else '-'}")
    print(f"negative_test_refs: {'; '.join(negative_tests) if negative_tests else '-'}")
    print(f"artifact_refs: {'; '.join(artifact_refs) if artifact_refs else '-'}")
    print(f"status: {row.get('outcome', '')}")
    print(f"verification_asset_id: {row.get('verification_asset_id', '')}")
    if service_map_row is not None:
        print(f"python_rti_service_map: {PYTHON_RTI_SERVICE_MAP_JSON_PATH.relative_to(ROOT).as_posix()}")


def _normalized_trace_matches(query: str) -> list[dict[str, str]]:
    normalized = query.casefold()
    if SERVICE_TRACE_INDEX_JSON_PATH.exists():
        payload = json.loads(SERVICE_TRACE_INDEX_JSON_PATH.read_text(encoding="utf-8"))
        indexed_rows = payload.get("rows", [])
        if isinstance(indexed_rows, list):
            exact_matches = [
                {str(key): str(value) for key, value in row.items()}
                for row in indexed_rows
                if isinstance(row, dict)
                and any(
                    str(row.get(key, "")).casefold() == normalized
                    for key in ("requirement_id", "hla_method", "python_name")
                )
            ]
            if exact_matches:
                return exact_matches
            partial_matches = [
                {str(key): str(value) for key, value in row.items()}
                for row in indexed_rows
                if isinstance(row, dict)
                and normalized
                in " ".join(
                    str(row.get(key, ""))
                    for key in ("requirement_id", "hla_method", "python_name")
                ).casefold()
            ]
            if partial_matches:
                return partial_matches
    return _ledger_matches(query)


def _trace_summary_fields(row: dict[str, str]) -> dict[str, str]:
    if "method" in row:
        method_name = row.get("method", "")
        python_name = row.get("python_name", "")
        positive_test_refs = row.get("positive_test_refs", "")
        artifact_refs = row.get("artifact_refs", "")
        status = row.get("outcome", "")
        verification_asset_id = row.get("verification_asset_id", "")
        requirement_id = row.get("requirement_id", "")
        section = row.get("section", "")
    else:
        method_name = row.get("hla_method", "")
        python_name = row.get("python_name", "")
        positive_test_refs = row.get("test_refs", "")
        artifact_refs = row.get("artifact_refs", "")
        status = row.get("status", "")
        verification_asset_id = row.get("verification_asset_id", "")
        requirement_id = row.get("requirement_id", "")
        section = row.get("section", "")

    service_map_row = _python_rti_service_map_match(method_name, python_name)
    implementation_symbol = row.get("implementation_ref", "")
    implementation_file = ""
    if service_map_row is not None:
        implementation_symbol = service_map_row.get("implementation_symbol", "")
        implementation_file = service_map_row.get("implementation_module", "")
    else:
        implementation_refs = _split_refs(row.get("implementation_refs", ""))
        if implementation_refs:
            implementation_symbol = implementation_refs[0]
        for ref in implementation_refs:
            if ref.endswith(".py"):
                implementation_file = ref
                break

    first_positive_test = _split_refs(positive_test_refs)
    first_artifact_ref = _split_refs(artifact_refs)
    return {
        "requirement_id": requirement_id,
        "section": section,
        "hla_method": method_name,
        "python_name": python_name,
        "implementation_symbol": implementation_symbol or "-",
        "implementation_file": implementation_file or "-",
        "positive_test_ref": first_positive_test[0] if first_positive_test else "-",
        "artifact_ref": first_artifact_ref[0] if first_artifact_ref else "-",
        "status": status or "-",
        "verification_asset_id": verification_asset_id or "-",
    }


def cmd_trace_summary(args: argparse.Namespace) -> int:
    query = args.method
    matches = _normalized_trace_matches(query)
    if not matches:
        print(f"error: no human-editability trace rows found for {query!r}", file=sys.stderr)
        return 2

    print(f"Human editability trace summary for {query}")
    print("workflow: trace first -> edit active row only if needed -> regenerate outputs")
    print("")
    for row in matches:
        summary = _trace_summary_fields(row)
        print(f"requirement_id: {summary['requirement_id']}")
        print(f"section: {summary['section']}")
        print(f"hla_method: {summary['hla_method']}")
        print(f"python_name: {summary['python_name']}")
        print(f"implementation_symbol: {summary['implementation_symbol']}")
        print(f"implementation_file: {summary['implementation_file']}")
        print(f"positive_test_ref: {summary['positive_test_ref']}")
        print(f"artifact_ref: {summary['artifact_ref']}")
        print(f"status: {summary['status']}")
        print(f"verification_asset_id: {summary['verification_asset_id']}")
        print("")
    print(f"active_authored_surface: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_trace_index: {SERVICE_TRACE_INDEX_JSON_PATH.relative_to(ROOT).as_posix()}")
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    query = args.method
    ledger_matches = _normalized_trace_matches(query)
    if not ledger_matches:
        print(f"error: no human-editability trace rows found for {query!r}", file=sys.stderr)
        return 2

    print(f"Human editability trace for {query}")
    print(f"ledger: {LEDGER_PATH.relative_to(ROOT).as_posix()}")
    print(f"traceability_matrix: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print("")
    for row in ledger_matches:
        if "method" in row:
            _print_trace_row(row)
            trace_rows = _traceability_matches(row.get("method", "") or query)
        else:
            service_map_row = _python_rti_service_map_match(row.get("hla_method", ""), row.get("python_name", ""))
            implementation_refs = row.get("implementation_ref", "")
            if service_map_row is not None:
                implementation_refs = "; ".join(
                    part
                    for part in (
                        service_map_row.get("implementation_symbol", ""),
                        service_map_row.get("implementation_module", ""),
                    )
                    if part
                )
            print(f"requirement_id: {row.get('requirement_id', '')}")
            print(f"section: {row.get('section', '')}")
            print(f"service_group: {row.get('service_group', '')}")
            print(f"hla_method: {row.get('hla_method', '')}")
            print(f"python_name: {row.get('python_name', '')}")
            print(f"implementation_refs: {implementation_refs}")
            print(f"positive_test_refs: {row.get('test_refs', '') or '-'}")
            print("negative_test_refs: -")
            print(f"artifact_refs: {row.get('artifact_refs', '') or '-'}")
            print(f"status: {row.get('status', '')}")
            print("verification_asset_id: -")
            if service_map_row is not None:
                print(f"python_rti_service_map: {PYTHON_RTI_SERVICE_MAP_JSON_PATH.relative_to(ROOT).as_posix()}")
            trace_rows = _traceability_matches(row.get("hla_method", "") or query)
        if trace_rows:
            first = trace_rows[0]
            print(f"traceability_requirement_id: {first.get('requirement_id', '')}")
            print(f"traceability_clause: {first.get('clause', '')}")
            print(f"traceability_status: {first.get('status', '')}")
        print("")
    return 0


def cmd_requirement(args: argparse.Namespace) -> int:
    requirement_id = args.requirement_id
    traceability_rows = _traceability_requirement_rows(requirement_id)
    ledger_rows = _ledger_requirement_rows(requirement_id)
    if not traceability_rows and ledger_rows:
        first = ledger_rows[0]
        for candidate in (
            first.get("method", ""),
            first.get("hla_method", ""),
            first.get("python_name", ""),
            first.get("title", "").removesuffix(" service"),
            first.get("section", ""),
        ):
            if candidate:
                traceability_rows = _traceability_matches(candidate)
                if traceability_rows:
                    break
    if not traceability_rows and not ledger_rows:
        print(
            f"error: no human-editability requirement rows found for {requirement_id!r}",
            file=sys.stderr,
        )
        return 2

    print(f"Human editability requirement for {requirement_id}")
    print(f"active_authored_surface: {TRACEABILITY_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_ledger: {LEDGER_PATH.relative_to(ROOT).as_posix()}")
    print(f"generated_trace_index: {SERVICE_TRACE_INDEX_JSON_PATH.relative_to(ROOT).as_posix()}")
    print("")
    if traceability_rows:
        print("Active requirement row:")
        for row in traceability_rows:
            _print_active_requirement_row(row)
            print("")
    if ledger_rows:
        print("Generated trace row:")
        for row in ledger_rows:
            if "method" in row:
                _print_trace_row(row)
            else:
                service_map_row = _python_rti_service_map_match(row.get("hla_method", ""), row.get("python_name", ""))
                implementation_refs = row.get("implementation_ref", "")
                if service_map_row is not None:
                    implementation_refs = "; ".join(
                        part
                        for part in (
                            service_map_row.get("implementation_symbol", ""),
                            service_map_row.get("implementation_module", ""),
                        )
                        if part
                    )
                print(f"requirement_id: {row.get('requirement_id', '')}")
                print(f"section: {row.get('section', '')}")
                print(f"service_group: {row.get('service_group', '')}")
                print(f"hla_method: {row.get('hla_method', '')}")
                print(f"python_name: {row.get('python_name', '')}")
                print(f"implementation_refs: {implementation_refs}")
                print(f"positive_test_refs: {row.get('test_refs', '') or '-'}")
                print("negative_test_refs: -")
                print(f"artifact_refs: {row.get('artifact_refs', '') or '-'}")
                print(f"status: {row.get('status', '')}")
                print("verification_asset_id: -")
            print("")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./tools/human-editability",
        description="Human-facing human-editability inventory, check, and early trace lookup wrapper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="print the baseline smell inventory")
    inventory_parser.set_defaults(func=cmd_inventory)

    check_parser = subparsers.add_parser("check", help="validate the smell inventory and print remaining open smells")
    check_parser.set_defaults(func=cmd_check)

    front_doors_parser = subparsers.add_parser(
        "front-doors",
        help="print the smallest practical reading/editing surfaces for spec, fom, python-rti, python-rti-service, rti-factories, requirements, and requirements-trace work",
    )
    front_doors_parser.add_argument(
        "topic",
        nargs="?",
        choices=("all", "spec", "fom", "python-rti", "python-rti-service", "rti-factories", "requirements", "requirements-trace"),
        default="all",
        help="which contributor surface to print",
    )
    front_doors_parser.set_defaults(func=cmd_front_doors)

    requirements_surfaces_parser = subparsers.add_parser(
        "requirements-surfaces",
        help="print the single-source classification of active, generated, and reference requirement surfaces",
    )
    requirements_surfaces_parser.add_argument(
        "--verbose",
        action="store_true",
        help="print every reference/provenance path instead of a compact summary",
    )
    requirements_surfaces_parser.set_defaults(func=cmd_requirements_surfaces)

    requirements_source_parser = subparsers.add_parser(
        "requirements-source",
        help="print the canonical requirements source-of-truth file and its key policies",
    )
    requirements_source_parser.set_defaults(func=cmd_requirements_source)

    requirements_crud_parser = subparsers.add_parser(
        "requirements-crud",
        help="print the smallest create/read/update/delete workflow for one active requirement row",
    )
    requirements_crud_parser.set_defaults(func=cmd_requirements_crud)

    requirements_create_parser = subparsers.add_parser(
        "requirements-create",
        help="start the create path for one active requirement row",
    )
    requirements_create_parser.add_argument(
        "row_id",
        nargs="?",
        help="optional standards-row requirement id or REQ-* artifact id",
    )
    requirements_create_parser.set_defaults(func=cmd_requirements_create)

    requirements_read_parser = subparsers.add_parser(
        "requirements-read",
        help="read one requirement row or one traced method with minimal branching",
    )
    requirements_read_parser.add_argument("target", help="method name or requirement id")
    requirements_read_parser.set_defaults(func=cmd_requirements_read)

    requirements_update_parser = subparsers.add_parser(
        "requirements-update",
        help="start the update path for one active requirement row",
    )
    requirements_update_parser.add_argument("requirement_id", help="Requirement id to update")
    requirements_update_parser.set_defaults(func=cmd_requirements_update)

    requirements_delete_parser = subparsers.add_parser(
        "requirements-delete",
        help="start the delete path for one active requirement row",
    )
    requirements_delete_parser.add_argument("requirement_id", help="Requirement id to delete")
    requirements_delete_parser.set_defaults(func=cmd_requirements_delete)

    requirements_lanes_parser = subparsers.add_parser(
        "requirements-lanes",
        help="print the normal active-service lane versus family-seed rows inside requirements/traceability_matrix.csv",
    )
    requirements_lanes_parser.set_defaults(func=cmd_requirements_lanes)

    requirements_active_parser = subparsers.add_parser(
        "requirements-active",
        help="print or search the generated active_service requirement rows only",
    )
    requirements_active_parser.add_argument(
        "query",
        nargs="?",
        help="optional substring search over requirement_id, clause, topic, artifact id, and implementation refs",
    )
    requirements_active_parser.set_defaults(func=cmd_requirements_active)

    requirements_flow_parser = subparsers.add_parser(
        "requirements-flow",
        help="print the compact human-editable requirements workflow",
    )
    requirements_flow_parser.set_defaults(func=cmd_requirements_flow)

    requirement_template_parser = subparsers.add_parser(
        "requirement-template",
        help="print a valid active-row template for requirements/traceability_matrix.csv",
    )
    requirement_template_parser.add_argument(
        "row_id",
        nargs="?",
        help="optional standards-row requirement id or REQ-* artifact id",
    )
    requirement_template_parser.set_defaults(func=cmd_requirement_template)

    trace_summary_parser = subparsers.add_parser(
        "trace-summary",
        help="print the compact human trace answer for a service or method",
    )
    trace_summary_parser.add_argument("method", help="HLA method, Python method, or requirement id")
    trace_summary_parser.set_defaults(func=cmd_trace_summary)

    trace_parser = subparsers.add_parser("trace", help="print the current ledger-backed trace for a service or method")
    trace_parser.add_argument("method", help="HLA method, Python method, or requirement id")
    trace_parser.set_defaults(func=cmd_trace)

    requirement_parser = subparsers.add_parser(
        "requirement",
        help="print one active requirement row plus its generated trace view by requirement id",
    )
    requirement_parser.add_argument("requirement_id", help="Requirement id such as REQ-RTI-TM-8_8-timeAdvanceRequest")
    requirement_parser.set_defaults(func=cmd_requirement)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
