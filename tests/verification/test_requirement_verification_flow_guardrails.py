from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_TEST_DIR = ROOT / "tests" / "requirements"
VERIFICATION_TEST_DIR = ROOT / "tests" / "verification"
TOP_LEVEL_TEST_DIR = ROOT / "tests"

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

_FORBIDDEN_REQUIREMENT_TEST_NAMES = {
    "test_spec2025_traceability_checked_in_artifact_stays_in_sync_with_generated_structure",
    "test_spec2025_traceability_matrix_writer_matches_checked_in_artifact",
}

_SELECTED_VERIFICATION_FILES = {
    "test_backend_compliance_discovery.py",
    "test_requirements_matrix_2010_v013.py",
    "test_requirements_ledger_v013.py",
}

_SELECTED_TOP_LEVEL_POLICY_FILES = {
    "test_backend_compliance_discovery_policy.py",
    "test_generated_requirement_dispositions.py",
}

_SELECTED_REQUIREMENT_FLOW_FILES = {
    "test_2025_traceability.py",
}

_ALLOWED_2025_HARMONIZATION_REQUIREMENT_TEST_FILES = {
    "test_2025_imported_packets.py",
}

_FORBIDDEN_2025_HARMONIZATION_EXPR_SNIPPETS = (
    "ROOT/'requirements'/'2025'/'harmonization'",
    "ROOT/'requirements'/'2025'/'harmonization'/",
    "requirements/2025/harmonization",
)

_SINGLE_SOURCE_SCRIPT_FILES = {
    "generate_requirement_compliance_spreadsheets.py",
    "generate_normalized_requirement_artifacts.py",
}

_FORBIDDEN_SINGLE_SOURCE_SCRIPT_SNIPPETS = (
    "analysis/compliance/requirements_matrix_2010.csv",
    "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv",
    "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv",
)

_REQUIREMENT_ENTRYPOINT_DOC_EXPECTATIONS = {
    "docs/requirements/ieee-1516-2010/README.md": (
        "requirements/2010/canonical_requirements.json",
        "requirements/2010/backend_resolution.json",
        "generated or legacy",
    ),
    "docs/requirements/ieee-1516-2025/README.md": (
        "requirements/2025/canonical_requirements.json",
        "requirements/2025/backend_resolution.json",
        "generated legacy projection",
    ),
    "requirements/2010/README.md": (
        "canonical_requirements.json",
        "backend_resolution.json",
        "generated or legacy",
    ),
    "requirements/2025/README.md": (
        "canonical_requirements.json",
        "backend_resolution.json",
        "generated or legacy",
    ),
    "requirements/README.md": (
        "2010/canonical_requirements.json",
        "2025/canonical_requirements.json",
        "generated or legacy projections",
    ),
    "scripts/README.md": (
        "requirements/2010/canonical_requirements.json",
        "requirements/2025/backend_resolution.json",
        "generated whole-spec 2010 matrix",
    ),
    "docs/networked_rti_python.md": (
        "requirements/2025/canonical_requirements.json",
        "requirements/2025/backend_resolution.json",
        "downstream audit view",
    ),
    "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md": (
        "requirements/2025/backend_resolution.json",
        "downstream projections",
        "generated grouped projection",
    ),
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
    "test_committed_vendor_backlog_markdown_matches_json_packet",
    "test_generated_requirement_disposition_markdown_summary_tables_match_json_packets",
    "test_generated_requirement_disposition_markdown_row_tables_match_json_packets",
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


def test_2025_finish_line_requirement_test_is_explicitly_downstream_reporting() -> None:
    text = (ROOT / "tests" / "verification" / "test_2025_finish_line_reporting.py").read_text(encoding="utf-8")
    assert "Downstream closeout-reporting verification for the 2025 lane." in text
    assert "not itself a\nrequirement-truth owner surface" in text


def test_closeout_docs_demote_themselves_beneath_canonical_requirement_truth() -> None:
    audit_text = (ROOT / "docs" / "plans" / "requirements_completion_audit.md").read_text(encoding="utf-8")
    closure_text = (ROOT / "docs" / "plans" / "requirements_remaining_closure.md").read_text(encoding="utf-8")
    gap_register_text = (ROOT / "docs" / "plans" / "requirements_gap_register.md").read_text(encoding="utf-8")
    export_text = (ROOT / "docs" / "verification" / "requirement_compliance_exports.md").read_text(encoding="utf-8")
    structure_packet_text = (ROOT / "docs" / "verification" / "requirements_structure_packet.md").read_text(encoding="utf-8")
    view_registry_text = (ROOT / "docs" / "verification" / "view_registry.md").read_text(encoding="utf-8")
    execution_queue_text = (ROOT / "docs" / "plans" / "requirements_execution_queue.md").read_text(encoding="utf-8")
    harmonization_readme_text = (ROOT / "requirements" / "2025" / "harmonization" / "README.md").read_text(encoding="utf-8")
    harmonization_worklist_text = (ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_harmonization_worklist.csv").read_text(encoding="utf-8")
    harmonization_review_queue_text = (ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_review_queue.csv").read_text(encoding="utf-8")
    harmonization_disposition_csv_text = (
        ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_disposition_ledger.csv"
    ).read_text(encoding="utf-8")
    harmonization_disposition_json_text = (
        ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_disposition_ledger.json"
    ).read_text(encoding="utf-8")
    harmonization_closure_report_text = (
        ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_coverage_closure_report.md"
    ).read_text(encoding="utf-8")
    normalized_execution_queue_text = " ".join(execution_queue_text.split())

    assert "canonical requirement catalog and backend-resolution companion" in audit_text
    assert "not themselves requirement-truth owner surfaces" in audit_text
    assert "canonical requirement and\nbackend-resolution catalogs as requirement truth" in closure_text
    assert "downstream closeout-program\nprojection inputs" in closure_text
    assert "requirements/2025/canonical_requirements.json" in gap_register_text
    assert "requirements/2025/backend_resolution.json" in gap_register_text
    assert "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv" not in export_text
    assert "requirements/2025/canonical_requirements.json" in export_text
    assert "requirements/2025/backend_resolution.json" in export_text
    assert "generated 2025 grouped closeout projection" in structure_packet_text
    assert "grouped closeout projection is now fully dispositioned" in structure_packet_text
    assert "does not replace the canonical requirement catalog or backend-resolution\n  companion" in structure_packet_text
    assert "canonical requirement catalog, backend-resolution companion" in view_registry_text
    assert "canonical requirement catalog, or backend-resolution companion has gone stale" in normalized_execution_queue_text
    assert "generated 2025 harmonization projections" in harmonization_readme_text
    assert "only row-level requirement\n  truth" in harmonization_readme_text
    assert "only backend- and route-resolution\n  truth" in harmonization_readme_text
    assert "downstream grouped, row-shaped, or\n  review-sequencing projection" in harmonization_readme_text
    assert "synchronized grouped projection over the canonical requirement\n  catalog and backend-resolution companion" in harmonization_readme_text
    assert "keep per-service truth in the harmonization ledger" not in harmonization_worklist_text
    assert "behavior closure stays row-level" not in harmonization_worklist_text
    assert "keep exact closure in the row-level ledger" not in harmonization_worklist_text
    assert "canonical requirement catalog" in harmonization_worklist_text
    assert "backend-resolution companion" in harmonization_worklist_text
    assert "Keep the harmonization row linked" not in harmonization_review_queue_text
    assert "generated projection row linked to its canonical owner doc" in harmonization_review_queue_text
    assert "Keep the harmonization row linked" not in harmonization_disposition_csv_text
    assert "Keep the harmonization row linked" not in harmonization_disposition_json_text
    assert "generated projection row linked to its canonical owner doc" in harmonization_disposition_csv_text
    assert "generated projection row linked to the canonical owner surface" in harmonization_disposition_json_text
    assert "Under the current ledger state" not in harmonization_closure_report_text
    assert "Under the current generated closeout projection" in harmonization_closure_report_text


def test_high_traffic_plan_and_verification_entrypoints_route_through_canonical_surfaces() -> None:
    plans_readme = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    verification_plan = (ROOT / "docs" / "verification" / "verification_plan.md").read_text(encoding="utf-8")
    verification_readme = (ROOT / "docs" / "verification" / "README.md").read_text(encoding="utf-8")
    backend_audit = (ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md").read_text(encoding="utf-8")
    row_audit = (ROOT / "docs" / "plans" / "2025_requirement_by_requirement_audit.md").read_text(encoding="utf-8")
    umbrella_worklist = (
        ROOT / "docs" / "plans" / "2025_python_rti_umbrella_decomposition_worklist.md"
    ).read_text(encoding="utf-8")
    completion_worklist = (
        ROOT / "docs" / "plans" / "2025_python_rti_100_percent_worklist.md"
    ).read_text(encoding="utf-8")
    compliance_plan = (
        ROOT / "docs" / "plans" / "PLN-004_python_rti_100_percent_compliance_plan.md"
    ).read_text(encoding="utf-8")
    shard_view_plan = (
        ROOT / "docs" / "plans" / "PLN-005_requirements_shards_views_and_verification_plan.md"
    ).read_text(encoding="utf-8")
    normalized_row_plan = (
        ROOT / "docs" / "plans" / "PLN-006_normalized_requirement_row_model_execution_plan.md"
    ).read_text(encoding="utf-8")
    finish_line = (ROOT / "docs" / "plans" / "requirements_finish_line.md").read_text(encoding="utf-8")
    normalized_row_plan_normalized = " ".join(normalized_row_plan.split())

    assert "canonical requirement catalog and backend-resolution companion" in plans_readme
    assert "downstream reporting and sequencing\nsurfaces" in plans_readme
    assert "requirements/2025/canonical_requirements.json" in verification_plan
    assert "requirements/2025/backend_resolution.json" in verification_plan
    assert "source-side canonical requirement row or backend-resolution row" in verification_readme
    assert "requirements/2025/canonical_requirements.json" in backend_audit
    assert "requirements/2025/backend_resolution.json" in backend_audit
    assert "not\nowner surfaces for 2025 requirement status or backend truth" in backend_audit
    assert "requirements/2025/canonical_requirements.json" in row_audit
    assert "requirements/2025/backend_resolution.json" in row_audit
    assert "not the primary requirement-truth surface" in row_audit
    assert "canonical 2025 requirement catalog" in umbrella_worklist
    assert "canonical 2025 requirement catalog counts" in completion_worklist
    assert "canonical requirement catalog" in compliance_plan
    assert "backend-resolution companion" in compliance_plan
    assert "generated grouped projections and canonical row catalogs linked, but not conflated" in shard_view_plan
    assert "canonical requirement catalog, grouped closeout projections" in normalized_row_plan_normalized
    assert "canonical-to-generated projection synchronization" in finish_line


def test_2025_boundary_owner_docs_require_canonical_or_backend_resolution_for_claim_widening() -> None:
    owner_docs = [
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "framework_rules.md",
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "callback_binding_deltas.md",
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "binding_and_hosted_route_boundaries.md",
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "retired_legacy_mapping.md",
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "omt_xs_any_extension_tolerance.md",
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "pitch_202x_bounded_comparison.md",
    ]

    for path in owner_docs:
        text = path.read_text(encoding="utf-8")
        assert "canonical requirement rows or the" in text, path
        assert "backend-resolution companion" in text, path
        assert "downstream reporting views" in text, path
        assert "no generated packet, audit note, or grouped worklist reclassifies" not in text, path


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


def test_2025_requirement_tests_do_not_read_harmonization_sidecars_as_primary_truth() -> None:
    violations: list[str] = []

    for path in sorted(REQUIREMENTS_TEST_DIR.glob("test_2025_*.py")):
        if path.name in _ALLOWED_2025_HARMONIZATION_REQUIREMENT_TEST_FILES:
            continue
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
                if any(snippet in expr_text for snippet in _FORBIDDEN_2025_HARMONIZATION_EXPR_SNIPPETS):
                    violations.append(f"{path.relative_to(ROOT)}::{node.name} -> {expr_text}")

    assert violations == []


def test_selected_requirement_flow_tests_do_not_police_checked_in_packets() -> None:
    violations: list[str] = []

    for path in sorted(REQUIREMENTS_TEST_DIR.glob("test_*.py")):
        if path.name not in _SELECTED_REQUIREMENT_FLOW_FILES:
            continue
        module = ast.parse(path.read_text(encoding="utf-8"))

        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name in _FORBIDDEN_REQUIREMENT_TEST_NAMES:
                violations.append(f"{path.relative_to(ROOT)}::{node.name}")

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


def test_selected_top_level_policy_tests_do_not_reintroduce_packet_policing_names() -> None:
    violations: list[str] = []

    for path in sorted(TOP_LEVEL_TEST_DIR.glob("test_*.py")):
        if path.name not in _SELECTED_TOP_LEVEL_POLICY_FILES:
            continue
        module = ast.parse(path.read_text(encoding="utf-8"))

        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name in _FORBIDDEN_VERIFICATION_TEST_NAMES:
                violations.append(f"{path.relative_to(ROOT)}::{node.name}")

    assert violations == []


def test_selected_scripts_use_canonical_requirement_and_backend_json_surfaces() -> None:
    violations: list[str] = []

    scripts_dir = ROOT / "scripts"
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name not in _SINGLE_SOURCE_SCRIPT_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in _FORBIDDEN_SINGLE_SOURCE_SCRIPT_SNIPPETS:
            if snippet in text:
                violations.append(f"{path.relative_to(ROOT)} -> {snippet}")

    assert violations == []


def test_requirement_entrypoint_docs_keep_canonical_json_surfaces_primary() -> None:
    violations: list[str] = []

    for relative_path, snippets in _REQUIREMENT_ENTRYPOINT_DOC_EXPECTATIONS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                violations.append(f"{relative_path} -> missing {snippet}")

    assert violations == []
