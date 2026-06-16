from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from compliance_helpers import is_1516_1_2010_row

ROOT = Path(__file__).resolve().parents[1]
CERTI_NEGOTIATED_OWNERSHIP_FINDINGS = "packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md"
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|owner|acquirer|publisher|subscriber|sender|receiver|left|right|regulator|constrained|rti)\.[A-Za-z_][A-Za-z0-9_]*\("
)

FILE_FUNCTIONS: dict[Path, dict[str, str]] = {
    ROOT / "tests" / "vendors" / "test_certi_real_backend_exchange_matrix.py": {
        "test_certi_backend_exchange_matrix": "run_two_federate_exchange_scenario",
        "test_certi_backend_synchronization_matrix": "run_synchronization_scenario",
        "test_certi_backend_support_factory_and_decode_matrix": "run_support_factory_and_decode_scenario",
    },
    ROOT / "tests" / "vendors" / "test_certi_real_backend_ownership_matrix.py": {
        "test_certi_backend_ownership_matrix": "run_attribute_ownership_scenario",
        "test_certi_backend_negotiated_ownership_matrix": "run_negotiated_attribute_ownership_scenario",
    },
    ROOT / "tests" / "vendors" / "test_certi_real_backend_time_matrix.py": {
        "test_certi_backend_section8_state_services_matrix": "run_section8_state_services_case",
        "test_certi_backend_section8_logical_time_query_matrix": "run_section8_state_services_case",
        "test_certi_backend_section8_state_toggle_services_matrix": "run_section8_state_services_case",
        "test_certi_backend_section8_time_bound_query_matrix": "run_section8_time_bound_query_case",
        "test_certi_backend_section8_ordering_and_query_matrix": "run_section8_ordering_and_query_case",
        "test_certi_backend_section8_available_and_flush_matrix": "run_section8_available_and_flush_case",
        "test_certi_backend_section8_available_and_retraction_matrix": "run_section8_available_and_retraction_case",
        "test_certi_backend_section8_order_override_matrix": "run_section8_order_override_case",
        "test_certi_backend_section8_request_retraction_matrix": "run_section8_request_retraction_case",
        "test_certi_backend_section8_duplicate_enable_rejection_matrix": "run_section8_duplicate_enable_rejection_case",
        "test_certi_backend_section8_tar_galt_boundary_matrix": "run_section8_tar_galt_boundary_case",
    },
}


def _function_sources(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    target_names = set(FILE_FUNCTIONS[path])
    functions: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            functions[node.name] = segment
    return functions


def _scenario_entrypoints(source: str) -> list[str]:
    return SCENARIO_ENTRYPOINT_RE.findall(source)


def _uses_shared_runner(source: str, runner_name: str) -> bool:
    if _scenario_entrypoints(source) == [runner_name]:
        return True
    return "_run_certi_section8_pair(" in source and source.count(runner_name) == 1


def _clause7_certi_vendor_divergent_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row)
        and row.get("clause_root") == "7"
        and row.get("runtime_disposition") == "vendor-divergent"
    ]


def _certi_rows(filename: str) -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row) or row.get("document") == "IEEE 1516-2010"
    ]


def test_certi_matrix_wrappers_stay_shared_harness_driven() -> None:
    for path, expected_functions in FILE_FUNCTIONS.items():
        sources = _function_sources(path)
        assert set(expected_functions).issubset(sources), path
        for function_name, runner_name in expected_functions.items():
            source = sources[function_name]
            assert _uses_shared_runner(source, runner_name), function_name
            assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def test_certi_clause7_vendor_divergent_rows_stay_explicit_negotiated_ownership_policy() -> None:
    rows = _clause7_certi_vendor_divergent_rows()
    assert rows

    expected_ids = {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
        "HLA1516.1-OWN-7.10-001",
        "REQ-FED-OWN-7_10-attributeOwnershipUnavailable",
    }
    assert {str(row["requirement_id"]) for row in rows} == expected_ids

    explicit_negotiated_ids = expected_ids - {"REQ-FED-OWN-7_10-attributeOwnershipUnavailable"}
    for row in rows:
        requirement_id = str(row["requirement_id"])
        refs = set(row.get("evidence_refs", []))
        if requirement_id in explicit_negotiated_ids:
            assert CERTI_NEGOTIATED_OWNERSHIP_FINDINGS in refs
            assert (
                "packages/hla-verification/src/hla.verification/"
                "scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
            ) in refs
            assert (
                "tests/vendors/test_certi_real_backend_ownership_matrix.py::"
                "test_certi_backend_negotiated_ownership_matrix"
            ) in refs
        else:
            assert requirement_id == "REQ-FED-OWN-7_10-attributeOwnershipUnavailable"
            assert not refs


def test_generated_certi_profile_requirement_disposition_markdown_keeps_inheritance_note_explicit() -> None:
    for filename, profile in (
        ("certi-native_requirement_disposition.md", "certi-native"),
        ("certi-jpype_requirement_disposition.md", "certi-jpype"),
        ("certi-py4j_requirement_disposition.md", "certi-py4j"),
    ):
        text = (ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8")
        assert f"every row has an explicit generated `{profile}` disposition." in text
        assert "inherits the CERTI family-level requirement disposition" in text


def test_certi_profile_requirement_disposition_artifacts_currently_inherit_family_rows() -> None:
    family_rows = _certi_rows("certi_requirement_disposition.json")
    assert family_rows

    family_index = {str(row["requirement_id"]): row for row in family_rows}

    for filename in (
        "certi-native_requirement_disposition.json",
        "certi-jpype_requirement_disposition.json",
        "certi-py4j_requirement_disposition.json",
    ):
        profile_rows = _certi_rows(filename)
        assert {str(row["requirement_id"]) for row in profile_rows} == set(family_index), filename

        for row in profile_rows:
            requirement_id = str(row["requirement_id"])
            family_row = family_index[requirement_id]
            assert row.get("runtime_disposition") == family_row.get("runtime_disposition"), (
                filename,
                requirement_id,
            )
            assert tuple(row.get("evidence_refs", ())) == tuple(family_row.get("evidence_refs", ())), (
                filename,
                requirement_id,
            )
            assert str(row.get("notes", "")) == str(family_row.get("notes", "")), (
                filename,
                requirement_id,
            )
