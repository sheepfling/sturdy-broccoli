from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_TEST_DIR = ROOT / "tests" / "requirements"
VERIFICATION_TEST_DIR = ROOT / "tests" / "verification"

_READ_METHODS = {"read_text", "read_bytes", "open"}
_FORBIDDEN_EXPR_SNIPPETS = (
    "ROOT/'docs'/'plans'",
    "ROOT/'docs'/'plans'/",
    "ROOT/'analysis'/'compliance'/'presentation_packets'",
    "ROOT/'analysis'/'compliance'/'python_final_requirements_report.md'",
    "ROOT/'analysis'/'compliance'/'python_boss_capability_brief.md'",
    "requirements_completion_audit.md",
    "2025_python_rti_100_percent_worklist.md",
    "2025_python_rti_umbrella_decomposition_worklist.md",
    "2010_python_rti_bounded_family_execution_worklist.md",
    "PLN-004_python_rti_100_percent_compliance_plan.md",
)

_FORBIDDEN_REQUIREMENT_ASSERT_TEXT_SNIPPETS = (
    "python_final_requirements_report.md",
    "python_boss_capability_brief.md",
    "requirements_completion_audit.md",
    "2025_python_rti_100_percent_worklist.md",
    "2025_python_rti_umbrella_decomposition_worklist.md",
    "2010_python_rti_bounded_family_execution_worklist.md",
    "PLN-004_python_rti_100_percent_compliance_plan.md",
)

_SELECTED_VERIFICATION_FILES = {
    "test_backend_compliance_discovery.py",
    "test_requirements_matrix_2010_v013.py",
    "test_requirements_ledger_v013.py",
}

_FORBIDDEN_VERIFICATION_EXPR_SNIPPETS = (
    "ROOT/'analysis'/'compliance'/'requirements_matrix_2010.csv'",
    "project_root/'analysis'/'compliance'/'requirements_matrix_2010.csv'",
    "ROOT/'analysis'/'compliance'/'defended_partials_index.md'",
    "project_root/'analysis'/'compliance'/'defended_partials_index.md'",
    "ROOT/'analysis'/'compliance'/'supported_subset_policy.md'",
    "project_root/'analysis'/'compliance'/'supported_subset_policy.md'",
)

_FORBIDDEN_VERIFICATION_TEST_NAMES = {
    "test_backend_compliance_catalog_mirrors_generated_requirement_disposition_packet_summaries",
}


def _normalized_unparse(node: ast.AST) -> str:
    return ast.unparse(node).replace('"', "'").replace(" ", "")


def _assignment_map(nodes: list[ast.stmt]) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        assignments[node.targets[0].id] = _normalized_unparse(node.value)
    return assignments


def _resolve_expr(expr: ast.AST, assignments: dict[str, str]) -> str:
    text = _normalized_unparse(expr)
    if isinstance(expr, ast.Name) and expr.id in assignments:
        return assignments[expr.id]
    return text


def test_requirement_verification_flow_doc_is_indexed() -> None:
    policy_doc = ROOT / "docs" / "verification" / "requirements_verification_flow.md"
    assert policy_doc.exists()

    verification_readme = (ROOT / "docs" / "verification" / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert "requirements_verification_flow.md" in verification_readme
    assert "verification/requirements_verification_flow.md" in docs_readme


def test_requirement_tests_do_not_read_plan_or_closeout_docs_as_truth_sources() -> None:
    violations: list[str] = []

    for path in sorted(REQUIREMENTS_TEST_DIR.glob("test_*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        module_assignments = _assignment_map(module.body)

        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            local_assignments = dict(module_assignments)
            local_assignments.update(_assignment_map(node.body))
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                if not isinstance(child.func, ast.Attribute) or child.func.attr not in _READ_METHODS:
                    continue
                expr_text = _resolve_expr(child.func.value, local_assignments)
                if any(snippet in expr_text for snippet in _FORBIDDEN_EXPR_SNIPPETS):
                    violations.append(f"{path.relative_to(ROOT)}::{node.name} -> {expr_text}")

    assert violations == []


def test_requirement_tests_do_not_assert_closeout_plan_filenames_in_doc_text() -> None:
    violations: list[str] = []

    for path in sorted(REQUIREMENTS_TEST_DIR.glob("test_*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))

        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            for child in ast.walk(node):
                if not isinstance(child, ast.Assert):
                    continue
                for grandchild in ast.walk(child):
                    if not isinstance(grandchild, ast.Constant) or not isinstance(grandchild.value, str):
                        continue
                    text = grandchild.value
                    if any(snippet in text for snippet in _FORBIDDEN_REQUIREMENT_ASSERT_TEXT_SNIPPETS):
                        violations.append(f"{path.relative_to(ROOT)}::{node.name} -> {text}")

    assert violations == []


def test_selected_verification_tests_do_not_police_checked_in_closeout_packets() -> None:
    violations: list[str] = []

    for path in sorted(VERIFICATION_TEST_DIR.glob("test_*.py")):
        if path.name not in _SELECTED_VERIFICATION_FILES:
            continue
        module = ast.parse(path.read_text(encoding="utf-8"))
        module_assignments = _assignment_map(module.body)

        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name in _FORBIDDEN_VERIFICATION_TEST_NAMES:
                violations.append(f"{path.relative_to(ROOT)}::{node.name}")
            local_assignments = dict(module_assignments)
            local_assignments.update(_assignment_map(node.body))
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                if not isinstance(child.func, ast.Attribute) or child.func.attr not in _READ_METHODS:
                    continue
                expr_text = _resolve_expr(child.func.value, local_assignments)
                if any(snippet in expr_text for snippet in _FORBIDDEN_VERIFICATION_EXPR_SNIPPETS):
                    violations.append(f"{path.relative_to(ROOT)}::{node.name} -> {expr_text}")

    assert violations == []
