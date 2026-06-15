from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from conftest import REPO_ROOT, load_compliance_json, load_compliance_text
from tests.compliance_row_models import RequirementDispositionRow
from tests.requirement_label_helpers import federate_interface_document_title, framework_document_title

ROOT = REPO_ROOT
FEDERATE_INTERFACE_DOCUMENT = federate_interface_document_title()
FRAMEWORK_DOCUMENT = framework_document_title()
CERTI_NEGOTIATED_OWNERSHIP_FINDINGS = "packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md"
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|owner|acquirer|publisher|subscriber|sender|receiver|left|right|regulator|constrained|rti)\.[A-Za-z_][A-Za-z0-9_]*\("
)
CERTI_PROFILE_MARKDOWN_CASES = (
    ("certi-native_requirement_disposition.md", "certi-native"),
    ("certi-jpype_requirement_disposition.md", "certi-jpype"),
    ("certi-py4j_requirement_disposition.md", "certi-py4j"),
)
CERTI_PROFILE_JSON_CASES = (
    "certi-native_requirement_disposition.json",
    "certi-jpype_requirement_disposition.json",
    "certi-py4j_requirement_disposition.json",
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


def _certi_requirement_rows(filename: str) -> list[RequirementDispositionRow]:
    payload = load_compliance_json(filename)
    return [RequirementDispositionRow.from_mapping(row) for row in payload["rows"]]


def _clause7_certi_vendor_divergent_rows() -> list[RequirementDispositionRow]:
    return [
        row
        for row in _certi_requirement_rows("certi_requirement_disposition.json")
        if row.document in {FEDERATE_INTERFACE_DOCUMENT, f"{FEDERATE_INTERFACE_DOCUMENT} (2010 edition)"}
        and row.clause_root == "7"
        and row.runtime_disposition == "vendor-divergent"
    ]


def _certi_rows(filename: str) -> list[RequirementDispositionRow]:
    return [
        row
        for row in _certi_requirement_rows(filename)
        if row.document in {FEDERATE_INTERFACE_DOCUMENT, FRAMEWORK_DOCUMENT}
    ]


def _assert_matrix_wrappers_follow_policy(
    *,
    file_functions: dict[Path, dict[str, str]],
    direct_call_pattern: re.Pattern[str],
) -> None:
    for path, expected_functions in file_functions.items():
        sources = _function_sources(path)
        assert set(expected_functions).issubset(sources), path
        for function_name, runner_name in expected_functions.items():
            source = sources[function_name]
            assert _uses_shared_runner(source, runner_name), function_name
            assert not direct_call_pattern.search(source), function_name


def _assert_profile_rows_inherit_family_rows(family_filename: str, profile_filename: str) -> None:
    family_rows = _certi_rows(family_filename)
    assert family_rows
    family_index = {row.requirement_id: row for row in family_rows}

    profile_rows = _certi_rows(profile_filename)
    assert {row.requirement_id for row in profile_rows} == set(family_index), profile_filename

    for row in profile_rows:
        requirement_id = row.requirement_id
        family_row = family_index[requirement_id]
        assert row.runtime_disposition == family_row.runtime_disposition, (
            profile_filename,
            requirement_id,
        )
        assert row.evidence_refs == family_row.evidence_refs, (
            profile_filename,
            requirement_id,
        )
        assert row.notes == family_row.notes, (
            profile_filename,
            requirement_id,
        )


def _assert_profile_markdown_contains_inheritance_note(
    cases: tuple[tuple[str, str], ...],
    *,
    family_name: str,
    extra_fragments: tuple[str, ...] = (),
) -> None:
    for filename, profile in cases:
        text = load_compliance_text(filename)
        for fragment in (
            f"every row has an explicit generated `{profile}` disposition.",
            f"inherits the {family_name} family-level requirement disposition",
            *extra_fragments,
        ):
            assert fragment in text


def test_certi_matrix_wrappers_stay_shared_harness_driven() -> None:
    _assert_matrix_wrappers_follow_policy(
        file_functions=FILE_FUNCTIONS,
        direct_call_pattern=DIRECT_BACKEND_CALL_RE,
    )


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
    }
    assert {row.requirement_id for row in rows} == expected_ids

    for row in rows:
        refs = set(row.evidence_refs)
        assert CERTI_NEGOTIATED_OWNERSHIP_FINDINGS in refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
        ) in refs
        assert (
            "tests/vendors/test_certi_real_backend_ownership_matrix.py::"
            "test_certi_backend_negotiated_ownership_matrix"
        ) in refs


def test_generated_certi_profile_requirement_disposition_markdown_keeps_inheritance_note_explicit() -> None:
    _assert_profile_markdown_contains_inheritance_note(
        CERTI_PROFILE_MARKDOWN_CASES,
        family_name="CERTI",
    )


def test_certi_profile_requirement_disposition_artifacts_currently_inherit_family_rows() -> None:
    for filename in CERTI_PROFILE_JSON_CASES:
        _assert_profile_rows_inherit_family_rows("certi_requirement_disposition.json", filename)
