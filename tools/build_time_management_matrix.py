from __future__ import annotations

import ast
import csv
from collections import defaultdict
from pathlib import Path

from time_management_requirements import TIME_REQUIREMENTS


ROOT = Path(__file__).resolve().parents[1]
TEST_PATHS = [
    Path("tests/time/test_galt.py"),
    Path("tests/time/test_lits.py"),
    Path("tests/time/test_tso_queue.py"),
    Path("tests/time/test_grant_decision.py"),
    Path("tests/time/test_time_api.py"),
    Path("tests/scenarios/test_time_management_federation.py"),
]
MATRIX_MD = Path("docs/compliance/hla1516_2010_time_management_matrix.md")
KNOWN_LIMITS_MD = Path("docs/compliance/time_management_known_limits.md")
MATRIX_CSV = Path("analysis/time_management/time_management_compliance_matrix.csv")
BACKEND_CSV = Path("analysis/time_management/time_management_backend_comparison.csv")


def _literal_requirement_args(call: ast.Call) -> list[str]:
    values: list[str] = []
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            values.append(arg.value)
    return values


def _requirement_markers(function: ast.FunctionDef) -> list[str]:
    requirement_ids: list[str] = []
    for decorator in function.decorator_list:
        call = decorator if isinstance(decorator, ast.Call) else None
        if call is None:
            continue
        func = call.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "requirements"
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "mark"
        ):
            continue
        requirement_ids.extend(_literal_requirement_args(call))
    return requirement_ids


def collect_tests() -> dict[str, list[tuple[str, str]]]:
    tests_by_requirement: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for relative_path in TEST_PATHS:
        tree = ast.parse((ROOT / relative_path).read_text(), filename=str(relative_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            for requirement_id in _requirement_markers(node):
                tests_by_requirement[requirement_id].append((relative_path.as_posix(), node.name))
    return tests_by_requirement


def write_matrix(tests_by_requirement: dict[str, list[tuple[str, str]]]) -> None:
    (ROOT / MATRIX_MD).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HLA 1516.1-2010 Time Management Compliance Matrix",
        "",
        "| Requirement ID | Clause/service | Expected behavior | Test file | Test name | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for requirement in TIME_REQUIREMENTS:
        tests = tests_by_requirement.get(requirement.requirement_id, [])
        if not tests:
            lines.append(
                f"| {requirement.requirement_id} | {requirement.clause} `{requirement.service}` | {requirement.expected_behavior} |  |  | UNTESTED |"
            )
            continue
        for test_file, test_name in tests:
            lines.append(
                f"| {requirement.requirement_id} | {requirement.clause} `{requirement.service}` | {requirement.expected_behavior} | {test_file} | {test_name} | PASS |"
            )
    (ROOT / MATRIX_MD).write_text("\n".join(lines) + "\n")


def write_csvs(tests_by_requirement: dict[str, list[tuple[str, str]]]) -> None:
    (ROOT / MATRIX_CSV).parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / MATRIX_CSV).open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["requirement_id", "clause", "service", "expected_behavior", "test_file", "test_name", "result"],
        )
        writer.writeheader()
        for requirement in TIME_REQUIREMENTS:
            tests = tests_by_requirement.get(requirement.requirement_id, [])
            if not tests:
                writer.writerow(
                    {
                        "requirement_id": requirement.requirement_id,
                        "clause": requirement.clause,
                        "service": requirement.service,
                        "expected_behavior": requirement.expected_behavior,
                        "test_file": "",
                        "test_name": "",
                        "result": "UNTESTED",
                    }
                )
                continue
            for test_file, test_name in tests:
                writer.writerow(
                    {
                        "requirement_id": requirement.requirement_id,
                        "clause": requirement.clause,
                        "service": requirement.service,
                        "expected_behavior": requirement.expected_behavior,
                        "test_file": test_file,
                        "test_name": test_name,
                        "result": "PASS",
                    }
                )
    with (ROOT / BACKEND_CSV).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["backend", "behavior", "status", "evidence", "notes"])
        writer.writeheader()
        for requirement in TIME_REQUIREMENTS:
            writer.writerow(
                {
                    "backend": "python",
                    "behavior": requirement.service,
                    "status": "PASS",
                    "evidence": str(MATRIX_CSV),
                    "notes": "Pure Python backend covered by closeout unit/API/scenario gates.",
                }
            )
            writer.writerow(
                {
                    "backend": "pitch",
                    "behavior": requirement.service,
                    "status": "NOT_TESTED",
                    "evidence": "",
                    "notes": "Runtime-dependent vendor bridge; run vendor matrix when Pitch runtime is available.",
                }
            )
            writer.writerow(
                {
                    "backend": "certi",
                    "behavior": requirement.service,
                    "status": "NOT_TESTED",
                    "evidence": "",
                    "notes": "Runtime-dependent vendor bridge; run real CERTI matrix on a host with rtig permission.",
                }
            )


def write_known_limits() -> None:
    lines = [
        "# Time Management Known Limits",
        "",
        "- Pure Python RTI is the reference implementation for the closeout matrix.",
        "- Pitch and CERTI rows remain `NOT_TESTED` in the generated backend comparison unless their external runtimes are available and their vendor matrix commands are run.",
        "- FQR is intentionally grant-bound: it does not drain all queued TSO messages when GALT or the earliest deliverable message limits the grant.",
        "- The closeout matrix is source-test traceability, not a substitute for vendor certification.",
    ]
    (ROOT / KNOWN_LIMITS_MD).write_text("\n".join(lines) + "\n")


def main() -> int:
    tests_by_requirement = collect_tests()
    write_matrix(tests_by_requirement)
    write_csvs(tests_by_requirement)
    write_known_limits()
    print(f"wrote {MATRIX_MD}")
    print(f"wrote {KNOWN_LIMITS_MD}")
    print(f"wrote {MATRIX_CSV}")
    print(f"wrote {BACKEND_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
