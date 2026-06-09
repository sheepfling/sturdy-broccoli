from __future__ import annotations

import ast
import csv
from pathlib import Path

from time_management_requirements import TIME_REQUIREMENTS


ROOT = Path(__file__).resolve().parents[1]
MATRIX_CSV = ROOT / "reports/time_management_compliance_matrix.csv"
BACKEND_CSV = ROOT / "reports/time_management_backend_comparison.csv"
TEST_PATHS = [
    ROOT / "tests/time/test_galt.py",
    ROOT / "tests/time/test_lits.py",
    ROOT / "tests/time/test_tso_queue.py",
    ROOT / "tests/time/test_grant_decision.py",
    ROOT / "tests/time/test_time_api.py",
    ROOT / "tests/scenarios/test_time_management_federation.py",
]


def _has_skip_marker(function: ast.FunctionDef) -> bool:
    for decorator in function.decorator_list:
        node = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(node, ast.Attribute) and node.attr in {"skip", "skipif"}:
            return True
    return False


def _requirement_markers(function: ast.FunctionDef) -> list[str]:
    markers: list[str] = []
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        func = decorator.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "requirements"
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "mark"
        ):
            continue
        for arg in decorator.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                markers.append(arg.value)
    return markers


def _scan_tests() -> tuple[set[str], list[str]]:
    covered: set[str] = set()
    failures: list[str] = []
    for path in TEST_PATHS:
        if not path.exists():
            failures.append(f"missing test file: {path.relative_to(ROOT)}")
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            markers = _requirement_markers(node)
            if not markers:
                failures.append(f"test has no requirement marker: {path.relative_to(ROOT)}::{node.name}")
            if markers and _has_skip_marker(node):
                failures.append(f"required test is skipped: {path.relative_to(ROOT)}::{node.name}")
            covered.update(markers)
    return covered, failures


def _scan_matrix() -> list[str]:
    failures: list[str] = []
    if not MATRIX_CSV.exists():
        return [f"missing matrix: {MATRIX_CSV.relative_to(ROOT)}"]
    rows = list(csv.DictReader(MATRIX_CSV.open()))
    for requirement in TIME_REQUIREMENTS:
        matching = [row for row in rows if row["requirement_id"] == requirement.requirement_id]
        if not matching:
            failures.append(f"requirement absent from matrix: {requirement.requirement_id}")
        if any(row["result"] == "UNTESTED" for row in matching):
            failures.append(f"requirement untested in matrix: {requirement.requirement_id}")
    if not BACKEND_CSV.exists():
        failures.append(f"missing backend comparison: {BACKEND_CSV.relative_to(ROOT)}")
    return failures


def main() -> int:
    covered, failures = _scan_tests()
    required = {requirement.requirement_id for requirement in TIME_REQUIREMENTS if requirement.required}
    for requirement_id in sorted(required - covered):
        failures.append(f"required behavior has no test marker: {requirement_id}")
    failures.extend(_scan_matrix())
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("time-management compliance coverage ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

