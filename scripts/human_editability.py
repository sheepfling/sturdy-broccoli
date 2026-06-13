from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from hla2010_repo_internal.traceability import (
    SERVICE_TRACE_INDEX_JSON_PATH,
    validate_active_traceability,
)


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "analysis" / "human_editability" / "smell_inventory.json"
LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
TRACEABILITY_PATH = ROOT / "requirements" / "traceability_matrix.csv"
SMELL_DOC_PATH = ROOT / "docs" / "plans" / "human_editability_smell_inventory.md"
PYTHON_RTI_SERVICE_MAP_JSON_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.json"


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
    print("traceability_validation: passed")
    print(f"remaining_open_smells: {len(open_checks)}")
    for check in open_checks:
        print(_format_open_smell(check))
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
            row.get("current_artifact_id", ""),
            row.get("canonical_topic", ""),
            row.get("implementation_refs", ""),
            row.get("notes", ""),
        )
        if any(normalized in value.casefold() for value in haystacks if value):
            matches.append(row)
    return matches


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


def cmd_trace(args: argparse.Namespace) -> int:
    query = args.method
    if SERVICE_TRACE_INDEX_JSON_PATH.exists():
        payload = json.loads(SERVICE_TRACE_INDEX_JSON_PATH.read_text(encoding="utf-8"))
        indexed_rows = payload.get("rows", [])
        if isinstance(indexed_rows, list):
            ledger_matches = [
                row
                for row in indexed_rows
                if isinstance(row, dict)
                and query.casefold()
                in " ".join(
                    str(row.get(key, ""))
                    for key in ("requirement_id", "hla_method", "python_name")
                ).casefold()
            ]
        else:
            ledger_matches = _ledger_matches(query)
    else:
        ledger_matches = _ledger_matches(query)
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

    trace_parser = subparsers.add_parser("trace", help="print the current ledger-backed trace for a service or method")
    trace_parser.add_argument("method", help="HLA method, Python method, or requirement id")
    trace_parser.set_defaults(func=cmd_trace)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
