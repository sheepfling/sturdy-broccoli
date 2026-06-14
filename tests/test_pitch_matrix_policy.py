from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from conftest import REPO_ROOT, load_compliance_json, load_compliance_text
from tests.compliance_row_models import RequirementDispositionRow, VendorBacklogRow
from tests.requirement_label_helpers import (
    federate_interface_document_title,
    federate_interface_section_ref,
    framework_document_title,
    omt_document_title,
)

ROOT = REPO_ROOT
FEDERATE_INTERFACE_DOCUMENT = federate_interface_document_title()
FRAMEWORK_DOCUMENT = framework_document_title()
OMT_DOCUMENT = omt_document_title()
PITCH_MATRIX_PATH = ROOT / "tests" / "vendors" / "test_pitch_real_backend_matrix.py"
PITCH_TRANSPORT_DIVERGENCE_NOTE = (
    "packages/hla2010-rti-pitch-common/docs/evidence/"
    "pitch_transport_subset_vendor_divergence_2026-06-11.md"
)
PITCH_NEGOTIATED_OWNERSHIP_VENDOR_BUG_NOTE = (
    "packages/hla2010-rti-pitch-common/docs/evidence/"
    "pitch_negotiated_ownership_vendor_bug_2026-06-07.md"
)
PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_NOTE = (
    "packages/hla2010-rti-pitch-common/docs/evidence/"
    "pitch_section8_time_management_vendor_divergence_2026-06-11.md"
)
PITCH_LOST_FEDERATE_GAP_NOTE = (
    "packages/hla2010-rti-pitch-common/docs/evidence/"
    "pitch_clause4_lost_federate_gap_2026-06-11.md"
)
TARGET_FUNCTIONS = {
    "test_pitch_backend_connection_lost_callback_matrix": "run_connection_lost_callback_scenario",
    "test_pitch_backend_federation_lifecycle_matrix": "run_federation_lifecycle_scenario",
    "test_pitch_backend_federation_lifecycle_with_mim_matrix": "run_federation_lifecycle_scenario",
    "test_pitch_backend_federation_listing_matrix": "run_federation_listing_scenario",
    "test_pitch_backend_federation_lifecycle_negative_matrix": "run_federation_lifecycle_negative_scenario",
    "test_pitch_backend_fom_module_visibility_matrix": "run_fom_module_visibility_scenario",
    "test_pitch_backend_multi_participation_matrix": "run_multi_participation_scenario",
    "test_pitch_backend_fom_integrity_negative_matrix": "run_fom_integrity_negative_scenario",
    "test_pitch_backend_multi_module_fom_visibility_matrix": "run_multi_module_fom_visibility_scenario",
    "test_pitch_backend_late_join_synchronization_matrix": "run_late_join_synchronization_scenario",
    "test_pitch_backend_multiple_synchronization_points_matrix": "run_multiple_synchronization_points_scenario",
    "test_pitch_backend_synchronization_matrix": "run_synchronization_scenario",
    "test_pitch_backend_synchronization_registration_failure_matrix": "run_synchronization_registration_failure_scenario",
    "test_pitch_backend_failed_federate_synchronization_matrix": "run_failed_federate_synchronization_scenario",
    "test_pitch_backend_restore_abort_exception_matrix": "run_restore_abort_exception_scenario",
    "test_pitch_backend_save_status_exception_matrix": "run_save_status_exception_scenario",
    "test_pitch_backend_restore_status_exception_matrix": "run_restore_status_exception_scenario",
    "test_pitch_backend_save_request_precondition_matrix": "run_save_request_precondition_scenario",
    "test_pitch_backend_restore_request_precondition_matrix": "run_restore_request_precondition_scenario",
    "test_pitch_backend_save_participant_exception_matrix": "run_save_participant_exception_scenario",
    "test_pitch_backend_abort_save_exception_matrix": "run_abort_save_exception_scenario",
    "test_pitch_backend_restore_participant_exception_matrix": "run_restore_participant_exception_scenario",
    "test_pitch_backend_resigned_federate_callback_silence_matrix": "run_resigned_federate_callback_silence_scenario",
    "test_pitch_backend_resign_precondition_matrix": "run_resign_precondition_scenario",
    "test_pitch_backend_resign_mom_cleanup_matrix": "run_resign_mom_cleanup_scenario",
    "test_pitch_backend_disconnect_mom_cleanup_matrix": "run_disconnect_mom_cleanup_scenario",
    "test_pitch_backend_join_precondition_matrix": "run_join_precondition_scenario",
    "test_pitch_backend_save_restore_matrix": "run_save_restore_scenario",
    "test_pitch_backend_save_restore_queued_callback_matrix": "run_save_restore_queued_callback_scenario",
    "test_pitch_backend_scheduled_save_restore_time_state_matrix": "run_scheduled_save_restore_time_state_scenario",
    "test_pitch_backend_restore_object_state_matrix": "run_restore_object_state_scenario",
    "test_pitch_backend_restore_federate_local_state_matrix": "run_restore_federate_local_state_scenario",
    "test_pitch_backend_save_failure_matrix": "run_save_failure_scenario",
    "test_pitch_backend_restore_request_failure_matrix": "run_restore_request_failure_scenario",
    "test_pitch_backend_restore_failure_matrix": "run_restore_failure_scenario",
    "test_pitch_backend_save_abort_matrix": "run_save_abort_scenario",
    "test_pitch_backend_restore_abort_matrix": "run_restore_abort_scenario",
}
CLAUSE6_TARGET_FUNCTIONS = {
    "test_pitch_backend_name_reservation_matrix": "run_name_reservation_scenario",
    "test_pitch_backend_discovery_metadata_callback_matrix": "run_discovery_metadata_callback_scenario",
    "test_pitch_backend_discovery_class_matrix": "run_discovery_class_scenario",
    "test_pitch_backend_update_advisory_callback_matrix": "run_update_advisory_callback_scenario",
    "test_pitch_backend_object_scope_relevance_matrix": "run_object_scope_relevance_scenario",
    "test_pitch_backend_transportation_type_matrix": "run_transportation_type_scenario",
    "test_pitch_backend_transportation_type_restore_persistence_matrix": "run_transportation_type_restore_persistence_scenario",
    "test_pitch_backend_transportation_type_rejection_matrix": "run_transportation_type_rejection_scenario",
    "test_pitch_backend_update_rate_matrix": "run_update_rate_scenario",
    "test_pitch_backend_request_attribute_value_update_matrix": "run_request_attribute_value_update_scenario",
    "test_pitch_backend_request_attribute_value_update_routing_matrix": "run_request_attribute_value_update_routing_scenario",
    "test_pitch_backend_orphan_object_lifecycle_matrix": "run_orphan_object_lifecycle_scenario",
    "test_pitch_backend_timed_delete_matrix": "run_timed_delete_scenario",
    "test_pitch_backend_local_delete_matrix": "run_local_delete_scenario",
    "test_pitch_backend_exchange_matrix": "run_two_federate_exchange_scenario",
}
CLAUSE7_TARGET_FUNCTIONS = {
    "test_pitch_backend_ownership_matrix": "run_attribute_ownership_scenario",
    "test_pitch_backend_negotiated_ownership_matrix": "run_negotiated_attribute_ownership_scenario",
    "test_pitch_negotiated_divesting_offer_probe": "probe_negotiated_attribute_ownership_offer",
    "test_pitch_release_request_owned_attribute_probe": "run_release_request_ownership_scenario",
    "test_pitch_backend_ownership_unavailable_matrix": "run_attribute_ownership_unavailable_scenario",
    "test_pitch_backend_release_denied_ownership_matrix": "run_release_request_ownership_scenario",
    "test_pitch_backend_non_owner_update_rejection_matrix": "run_non_owner_update_rejection_scenario",
}
CLAUSE8_TARGET_FUNCTIONS = {
    "test_pitch_backend_lookahead_matrix": "run_section8_early_timestamp_send_case",
    "test_pitch_section8_logical_time_query_matrix": "run_section8_state_services_case",
    "test_pitch_section8_state_toggle_services_matrix": "run_section8_state_services_case",
    "test_pitch_section8_time_bound_query_matrix": "run_section8_time_bound_query_case",
    "test_pitch_section8_available_and_flush_matrix": "run_section8_available_and_flush_case",
    "test_pitch_section8_early_timestamp_send_rejection_matrix": "run_section8_early_timestamp_send_case",
    "test_pitch_section8_state_services_matrix": "run_section8_state_services_case",
    "test_pitch_section8_ordering_and_queries_matrix": "run_section8_ordering_and_query_case",
    "test_pitch_section8_available_and_retraction_matrix": "run_section8_available_and_retraction_case",
    "test_pitch_section8_order_override_services_matrix": "run_section8_order_override_case",
    "test_pitch_section8_request_retraction_callback_matrix": "run_section8_request_retraction_case",
}
CLAUSE9_TARGET_FUNCTIONS = {
    "test_pitch_backend_ddm_matrix": "run_suite_ddm_scenario",
    "test_pitch_backend_ddm_declaration_gating_matrix": "run_ddm_declaration_gating_scenario",
    "test_pitch_backend_ddm_object_region_lifecycle_matrix": "run_ddm_object_region_lifecycle_scenario",
    "test_pitch_backend_ddm_passive_region_subscription_matrix": "run_ddm_passive_region_subscription_scenario",
}
PITCH_PROFILE_MARKDOWN_CASES = (
    ("pitch-jpype_requirement_disposition.md", "pitch-jpype"),
    ("pitch-py4j_requirement_disposition.md", "pitch-py4j"),
)
PITCH_PROFILE_INHERITANCE_CASES = (
    ("pitch-jpype_requirement_disposition.json", "pitch_jpype_disposition", "pitch_jpype_evidence_refs"),
    ("pitch-py4j_requirement_disposition.json", "pitch_py4j_disposition", "pitch_py4j_evidence_refs"),
)
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|federate|observer|publisher|subscriber|sender|receiver|r1|r2)\.[A-Za-z_][A-Za-z0-9_]*\("
)
CLAUSE7_DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:owner|acquirer|requester|rival|late)\.[A-Za-z_][A-Za-z0-9_]*\("
)
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")


def _pitch_matrix_function_sources() -> dict[str, str]:
    source = PITCH_MATRIX_PATH.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(PITCH_MATRIX_PATH))
    target_names = (
        set(TARGET_FUNCTIONS)
        | set(CLAUSE6_TARGET_FUNCTIONS)
        | set(CLAUSE7_TARGET_FUNCTIONS)
        | set(CLAUSE8_TARGET_FUNCTIONS)
        | set(CLAUSE9_TARGET_FUNCTIONS)
    )
    functions: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            functions[node.name] = segment
    return functions


def _function_source(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            return segment
    raise KeyError(function_name)


def _scenario_entrypoints(source: str) -> list[str]:
    return SCENARIO_ENTRYPOINT_RE.findall(source)


def _load_requirement_rows(filename: str) -> list[RequirementDispositionRow]:
    payload = load_compliance_json(filename)
    return [RequirementDispositionRow.from_mapping(row) for row in payload["rows"]]


def _load_vendor_backlog_rows(filename: str) -> list[VendorBacklogRow]:
    payload = load_compliance_json(filename)
    return [VendorBacklogRow.from_mapping(row) for row in payload["rows"]]


def _clause6_pitch_compliance_wrapper_refs() -> set[str]:
    return {
        ref.split("::", 1)[1]
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.document == FEDERATE_INTERFACE_DOCUMENT and row.clause_root == "6"
        for ref in row.evidence_refs
        if ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::")
    }


def _clause6_pitch_vendor_divergent_rows() -> list[RequirementDispositionRow]:
    return [
        row
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.document == FEDERATE_INTERFACE_DOCUMENT
        and row.clause_root == "6"
        and row.pitch_disposition == "vendor-divergent"
    ]


def _clause7_pitch_vendor_divergent_rows() -> list[RequirementDispositionRow]:
    return [
        row
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.document == FEDERATE_INTERFACE_DOCUMENT
        and row.clause_root == "7"
        and row.pitch_disposition == "vendor-divergent"
    ]


def _clause8_pitch_vendor_divergent_rows() -> list[RequirementDispositionRow]:
    return [
        row
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.document == FEDERATE_INTERFACE_DOCUMENT
        and row.clause_root == "8"
        and row.pitch_disposition == "vendor-divergent"
    ]


def _pitch_classification_required_rows() -> list[RequirementDispositionRow]:
    return [
        row
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.pitch_disposition == "classification-required"
    ]


def _pitch_backlog_classification_required_rows() -> list[VendorBacklogRow]:
    return [
        row
        for row in _load_vendor_backlog_rows("vendor_discovery_backlog.json")
        if row.backend_id == "pitch-requirements" and row.current_status == "classification-required"
    ]


def _pitch_rows(filename: str) -> list[RequirementDispositionRow]:
    return [
        row
        for row in _load_requirement_rows(filename)
        if row.document in {FEDERATE_INTERFACE_DOCUMENT, FRAMEWORK_DOCUMENT, OMT_DOCUMENT, "multi-section"}
    ]


def _pitch_clause_rows(filename: str, clause_root: str) -> list[RequirementDispositionRow]:
    return [
        row
        for row in _pitch_rows(filename)
        if row.document == FEDERATE_INTERFACE_DOCUMENT and row.clause_root == clause_root
    ]


def _assert_wrapper_functions_follow_policy(
    target_functions: dict[str, str],
    *,
    shared_runner_check,
    direct_call_pattern: re.Pattern[str],
) -> None:
    sources = _pitch_matrix_function_sources()
    assert set(target_functions).issubset(sources)

    for function_name, runner_name in target_functions.items():
        source = sources[function_name]
        assert shared_runner_check(source, runner_name), function_name
        assert not direct_call_pattern.search(source), function_name


def _assert_pitch_profile_inheritance(
    family_filename: str,
    profile_filename: str,
    disposition_field: str,
    evidence_field: str,
) -> None:
    family_rows = _pitch_rows(family_filename)
    assert family_rows
    family_index = {row.requirement_id: row for row in family_rows}

    profile_rows = _pitch_rows(profile_filename)
    assert {row.requirement_id for row in profile_rows} == set(family_index), profile_filename

    for row in profile_rows:
        requirement_id = row.requirement_id
        family_row = family_index[requirement_id]
        assert row.runtime_disposition == family_row.disposition_for(disposition_field), (
            profile_filename,
            requirement_id,
        )
        assert row.evidence_refs == family_row.evidence_refs_for(evidence_field), (
            profile_filename,
            requirement_id,
        )
        assert row.notes == family_row.notes, (
            profile_filename,
            requirement_id,
        )


def _clause4_pitch_compliance_wrapper_refs() -> set[str]:
    return {
        ref.split("::", 1)[1]
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.document == "IEEE 1516.1-2010 (2010 edition)" and row.clause_root == "4"
        for ref in row.evidence_refs
        if ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::")
    }


def _uses_shared_runner(source: str, runner_name: str) -> bool:
    if _scenario_entrypoints(source) == [runner_name]:
        return True
    return "_run_pitch_section8_pair(" in source and source.count(runner_name) == 1


def test_clause4_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    _assert_wrapper_functions_follow_policy(
        TARGET_FUNCTIONS,
        shared_runner_check=lambda source, runner_name: (
            f"{runner_name}(" in source and _scenario_entrypoints(source) == [runner_name]
        ),
        direct_call_pattern=DIRECT_BACKEND_CALL_RE,
    )


def test_clause4_pitch_compliance_wrappers_are_all_guarded_by_policy() -> None:
    sources = _pitch_matrix_function_sources()
    guarded_functions = set(TARGET_FUNCTIONS) | {"test_pitch_backend_lost_federate_mom_matrix"}
    assert _clause4_pitch_compliance_wrapper_refs().issubset(guarded_functions)
    assert _clause4_pitch_compliance_wrapper_refs().issubset(set(sources) | {"test_pitch_backend_lost_federate_mom_matrix"})


def test_pitch_classification_required_rows_do_not_claim_blank_dispositions() -> None:
    rows = _pitch_classification_required_rows()
    assert rows

    for row in rows:
        assert "explicitly generated as classification-required" in row.notes
        assert "disposition is blank" not in row.notes


def test_generated_pitch_profile_requirement_disposition_markdown_keeps_inheritance_note_explicit() -> None:
    for filename, profile in PITCH_PROFILE_MARKDOWN_CASES:
        text = load_compliance_text(filename)
        assert f"every row has an explicit generated `{profile}` disposition." in text
        assert "inherits the Pitch family-level requirement disposition" in text


def test_pitch_profile_requirement_disposition_artifacts_inherit_family_rows() -> None:
    for filename, disposition_field, evidence_field in PITCH_PROFILE_INHERITANCE_CASES:
        _assert_pitch_profile_inheritance(
            "pitch_requirement_disposition.json",
            filename,
            disposition_field,
            evidence_field,
        )


def test_pitch_tranche_clauses_4_6_7_8_9_have_no_not_yet_tested_rows_in_family_or_profiles() -> None:
    target_clauses = ("4", "6", "7", "8", "9")

    family_rows = _pitch_rows("pitch_requirement_disposition.json")
    for clause_root in target_clauses:
        clause_rows = [
            row
            for row in family_rows
            if row.document == "IEEE 1516.1-2010 (2010 edition)" and row.clause_root == clause_root
        ]
        assert clause_rows, clause_root
        for disposition_key in ("pitch_disposition", "pitch_jpype_disposition", "pitch_py4j_disposition"):
            assert not {
                row.requirement_id
                for row in clause_rows
                if row.disposition_for(disposition_key) == "not-yet-tested"
            }, (clause_root, disposition_key)

    for filename in ("pitch-jpype_requirement_disposition.json", "pitch-py4j_requirement_disposition.json"):
        for clause_root in target_clauses:
            clause_rows = _pitch_clause_rows(filename, clause_root)
            assert clause_rows, (filename, clause_root)
            assert not {
                row.requirement_id
                for row in clause_rows
                if row.runtime_disposition == "not-yet-tested"
            }, (filename, clause_root)


def test_pitch_vendor_backlog_classification_required_rows_track_explicit_state() -> None:
    rows = _pitch_backlog_classification_required_rows()
    assert rows

    for row in rows:
        assert "explicitly generated as classification-required" in row.rationale
        assert "disposition is blank" not in row.rationale


def test_clause6_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    _assert_wrapper_functions_follow_policy(
        CLAUSE6_TARGET_FUNCTIONS,
        shared_runner_check=lambda source, runner_name: (
            f"{runner_name}(" in source and _scenario_entrypoints(source) == [runner_name]
        ),
        direct_call_pattern=DIRECT_BACKEND_CALL_RE,
    )


def test_clause6_pitch_compliance_wrappers_are_all_guarded_by_policy() -> None:
    sources = _pitch_matrix_function_sources()
    guarded_functions = set(CLAUSE6_TARGET_FUNCTIONS)
    assert _clause6_pitch_compliance_wrapper_refs().issubset(guarded_functions)
    assert _clause6_pitch_compliance_wrapper_refs().issubset(sources)


def test_clause6_pitch_vendor_divergent_rows_stay_explicit_transport_subset_policy() -> None:
    rows = _clause6_pitch_vendor_divergent_rows()
    assert rows

    expected_ids = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.27-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    }
    assert {row.requirement_id for row in rows} == expected_ids

    for row in rows:
        refs = set(row.evidence_refs)
        assert PITCH_TRANSPORT_DIVERGENCE_NOTE in refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_transportation_type.py::run_transportation_type_scenario"
        ) in refs
        assert (
            "tests/scenarios/test_object_management_backend_matrix.py::"
            "test_python_transportation_type_matrix"
        ) in refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::"
            "test_pitch_backend_transportation_type_matrix"
        ) in refs

    restore_subset_ids = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.27-001",
    }
    for row in rows:
        refs = set(row.evidence_refs)
        if row.requirement_id in restore_subset_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario"
            ) in refs
            assert (
                "tests/scenarios/test_object_management_backend_matrix.py::"
                "test_python_transportation_type_restore_persistence_matrix"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_backend_transportation_type_restore_persistence_matrix"
            ) in refs


def test_clause7_pitch_vendor_divergent_rows_stay_explicit_negotiated_ownership_policy() -> None:
    rows = _clause7_pitch_vendor_divergent_rows()
    assert rows

    expected_ids = {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
    }
    assert {row.requirement_id for row in rows} == expected_ids

    offer_probe_ids = {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }
    full_negotiated_ids = expected_ids - offer_probe_ids

    for row in rows:
        refs = set(row.evidence_refs)
        assert PITCH_NEGOTIATED_OWNERSHIP_VENDOR_BUG_NOTE in refs
        if row.requirement_id in offer_probe_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "scenario_ownership.py::probe_negotiated_attribute_ownership_offer"
            ) in refs
            assert (
                "tests/scenarios/test_ownership_management_backend_matrix.py::"
                "test_python_negotiated_divesting_offer_probe_matrix"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_negotiated_divesting_offer_probe"
            ) in refs
        else:
            assert row.requirement_id in full_negotiated_ids
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
            ) in refs
            assert (
                "tests/scenarios/test_ownership_management_backend_matrix.py::"
                "test_python_backend_negotiated_ownership_matrix"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_backend_negotiated_ownership_matrix"
            ) in refs


def test_clause7_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    _assert_wrapper_functions_follow_policy(
        CLAUSE7_TARGET_FUNCTIONS,
        shared_runner_check=lambda source, runner_name: (
            f"{runner_name}(" in source and _scenario_entrypoints(source) == [runner_name]
        ),
        direct_call_pattern=CLAUSE7_DIRECT_BACKEND_CALL_RE,
    )


def test_clause8_pitch_vendor_divergent_rows_stay_explicit_shared_harness_policy() -> None:
    rows = _clause8_pitch_vendor_divergent_rows()
    assert rows

    expected_ids = {
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
        "REQ-RTI-TM-8_21-retract",
        "REQ-FED-TM-8_22-requestRetraction",
        "HLA1516.1-TM-8.1-001",
        "HLA1516.1-TM-8.1-002",
        "HLA1516.1-TM-8.1.1-001",
        "HLA1516.1-TM-8.1.2-001",
        "HLA1516.1-TM-8.1.2-002",
        "HLA1516.1-TM-8.1.2-003",
        "HLA1516.1-TM-8.1.2-004",
        "HLA1516.1-TM-8.1.3-002",
        "HLA1516.1-TM-8.1.3-003",
        "HLA1516.1-TM-8.1.5-001",
        "HLA1516.1-TM-8.1.6-001",
        "HLA1516.1-TM-8.1.7-001",
        "HLA1516.1-TM-8.10-001",
        "HLA1516.1-TM-8.21-001",
    }
    assert {row.requirement_id for row in rows} == expected_ids

    ordering_and_query_ids = {
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "HLA1516.1-TM-8.1-002",
        "HLA1516.1-TM-8.1.1-001",
        "HLA1516.1-TM-8.1.2-004",
        "HLA1516.1-TM-8.1.3-002",
        "HLA1516.1-TM-8.1.3-003",
        "HLA1516.1-TM-8.1.5-001",
        "HLA1516.1-TM-8.1.6-001",
        "HLA1516.1-TM-8.1.7-001",
        "HLA1516.1-TM-8.10-001",
    }
    available_and_retraction_ids = {
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
        "REQ-RTI-TM-8_21-retract",
        "HLA1516.1-TM-8.21-001",
    }
    request_retraction_ids = {"REQ-FED-TM-8_22-requestRetraction"}
    state_services_ids = {"HLA1516.1-TM-8.1-001"}
    order_override_ids = {
        "HLA1516.1-TM-8.1.2-001",
        "HLA1516.1-TM-8.1.2-002",
        "HLA1516.1-TM-8.1.2-003",
    }

    for row in rows:
        requirement_id = row.requirement_id
        refs = set(row.evidence_refs)
        assert PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_NOTE in refs
        if requirement_id in ordering_and_query_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "section8_matrix.py::run_section8_ordering_and_query_case"
            ) in refs
            assert (
                "tests/time/test_section8_backend_matrix.py::"
                "test_section8_backend_matrix_ordering_and_queries"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_section8_ordering_and_queries_matrix"
            ) in refs
        elif requirement_id in available_and_retraction_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "section8_matrix.py::run_section8_available_and_retraction_case"
            ) in refs
            assert (
                "tests/time/test_section8_backend_matrix.py::"
                "test_section8_backend_matrix_available_and_retraction"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_section8_available_and_retraction_matrix"
            ) in refs
        elif requirement_id in request_retraction_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "section8_matrix.py::run_section8_request_retraction_case"
            ) in refs
            assert (
                "tests/time/test_section8_backend_matrix.py::"
                "test_section8_backend_matrix_request_retraction_callback"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_section8_request_retraction_callback_matrix"
            ) in refs
        elif requirement_id in state_services_ids:
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "section8_matrix.py::run_section8_state_services_case"
            ) in refs
            assert (
                "tests/time/test_section8_backend_matrix.py::"
                "test_section8_backend_matrix_state_services"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_section8_state_services_matrix"
            ) in refs
        else:
            assert requirement_id in order_override_ids
            assert (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
                "section8_matrix.py::run_section8_order_override_case"
            ) in refs
            assert (
                "tests/time/test_section8_backend_matrix.py::"
                "test_section8_backend_matrix_order_override_services"
            ) in refs
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_section8_order_override_services_matrix"
            ) in refs


def test_clause8_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    _assert_wrapper_functions_follow_policy(
        CLAUSE8_TARGET_FUNCTIONS,
        shared_runner_check=_uses_shared_runner,
        direct_call_pattern=DIRECT_BACKEND_CALL_RE,
    )


def test_clause9_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    _assert_wrapper_functions_follow_policy(
        CLAUSE9_TARGET_FUNCTIONS,
        shared_runner_check=lambda source, runner_name: _scenario_entrypoints(source) == [runner_name],
        direct_call_pattern=DIRECT_BACKEND_CALL_RE,
    )


def test_clause4_pitch_lost_federate_wrapper_stays_shared_harness_driven() -> None:
    source = _function_source(PITCH_MATRIX_PATH, "test_pitch_backend_lost_federate_mom_matrix")

    assert "run_lost_federate_mom_scenario(" in source
    assert "run_external_lost_federate_observer_scenario(" in source
    assert "_terminate_pitch_py4j_gateway_process(victim)" in source
    assert "launch_victim=_launch_pitch_jpype_lost_federate_session" in source
    assert "observer.backend" not in source
    assert "victim.backend" not in source

    scenario_entrypoints = set(_scenario_entrypoints(source))
    assert scenario_entrypoints == {
        "run_lost_federate_mom_scenario",
        "run_external_lost_federate_observer_scenario",
    }


def test_clause4_pitch_lost_federate_rows_keep_family_and_profile_blocked_evidence_explicit() -> None:
    rows = {
        row.requirement_id: row
        for row in _load_requirement_rows("pitch_requirement_disposition.json")
        if row.requirement_id in {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}
    }
    assert set(rows) == {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}

    for requirement_id, row in rows.items():
        assert row.pitch_disposition == "blocked", requirement_id
        assert row.pitch_jpype_disposition == "blocked", requirement_id
        assert row.pitch_py4j_disposition == "blocked", requirement_id

        family_refs = set(row.evidence_refs)
        jpype_refs = set(row.pitch_jpype_evidence_refs)
        py4j_refs = set(row.pitch_py4j_evidence_refs)

        assert PITCH_LOST_FEDERATE_GAP_NOTE in family_refs
        assert "analysis/preflight_artifacts/pitch-preflight.json" in family_refs
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/"
            "vendor_runtime_status_summary.json"
        ) in family_refs
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/"
            "vendor_runtime_status_report.md"
        ) in family_refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_connection_lost.py::run_connection_lost_callback_scenario"
        ) in family_refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_resign.py::run_disconnect_mom_cleanup_scenario"
        ) in family_refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_lost_federate.py::run_lost_federate_mom_scenario"
        ) in family_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in family_refs

        assert PITCH_LOST_FEDERATE_GAP_NOTE in jpype_refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_lost_federate.py::run_external_lost_federate_observer_scenario"
        ) in jpype_refs
        assert (
            "tests/test_rti_pitch_split_packages.py::"
            "test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process"
        ) in jpype_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in jpype_refs
        assert "analysis/preflight_artifacts/pitch-preflight.json" in jpype_refs

        assert PITCH_LOST_FEDERATE_GAP_NOTE in py4j_refs
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/"
            "scenario_lost_federate.py::run_lost_federate_mom_scenario"
        ) in py4j_refs
        assert (
            "tests/test_rti_pitch_split_packages.py::"
            "test_pitch_py4j_factory_attaches_gateway_process"
        ) in py4j_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in py4j_refs
        assert "analysis/preflight_artifacts/pitch-preflight.json" in py4j_refs


def test_clause4_pitch_lost_federate_rows_keep_exact_backlog_frontier_shape() -> None:
    target_ids = {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}

    rows_by_requirement: dict[str, list[VendorBacklogRow]] = {}
    for row in _load_vendor_backlog_rows("vendor_discovery_backlog.json"):
        requirement_id = row.requirement_id
        if requirement_id in target_ids:
            rows_by_requirement.setdefault(requirement_id, []).append(row)

    assert set(rows_by_requirement) == target_ids

    expected_surface = {
        ("pitch-requirements", "blocked", "pitch-requirement-disposition-row"),
        ("pitch-jpype", "blocked", "pitch-requirement-profile-row"),
        ("pitch-py4j", "blocked", "pitch-requirement-profile-row"),
    }

    for requirement_id, rows in rows_by_requirement.items():
        assert {
            (
                row.backend_id,
                row.current_status,
                row.row_kind,
            )
            for row in rows
        } == expected_surface, requirement_id

        for row in rows:
            assert row.priority == "P2", requirement_id
            assert (
                row.recommended_next_action
                == "unblock capability or document the hard backend limitation"
            ), requirement_id
            assert (
                row.source_artifact == "analysis/compliance/pitch_requirement_disposition.json"
            ), requirement_id


def test_clause4_pitch_family_and_profiles_keep_exact_residual_frontier() -> None:
    expected = {
        "AREA-1516.1-4": "not-applicable",
        "HLA1516.1-FM-001": "not-applicable",
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": "vendor-divergent",
        "HLA1516.1-FM-4.1.5-001": "blocked",
        "HLA1516.1-FM-4.1.5-002": "blocked",
        "HLA1516.1-FM-4.5-EXC-001": "vendor-divergent",
        "HLA1516.1-FM-4.9-EXC-001": "vendor-divergent",
    }

    family_rows = {
        row.identifier: row.pitch_disposition
        for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4")
        if row.pitch_disposition != "verified"
    }
    assert family_rows == expected

    for filename in ("pitch-jpype_requirement_disposition.json", "pitch-py4j_requirement_disposition.json"):
        profile_rows = {
            row.identifier: row.runtime_disposition
            for row in _pitch_clause_rows(filename, "4")
            if row.runtime_disposition != "verified"
        }
        assert profile_rows == expected, filename


def test_clause4_pitch_family_and_profiles_keep_exact_summary_counts() -> None:
    payload = load_compliance_json("pitch_requirement_disposition.json")

    expected = {
        "blocked": 2,
        "not-applicable": 2,
        "total": 281,
        "vendor-divergent": 3,
        "verified": 274,
    }
    section_ref = federate_interface_section_ref("4")
    assert payload["summary"]["clause_summary"][section_ref] == expected
    assert payload["summary"]["profile_clause_summary"]["pitch-jpype"][section_ref] == expected
    assert payload["summary"]["profile_clause_summary"]["pitch-py4j"][section_ref] == expected


def test_clause4_pitch_family_and_profile_evidence_stays_on_allowed_surfaces() -> None:
    allowed_prefixes = (
        "packages/hla2010-verification-harness/",
        "tests/scenarios/",
        "tests/vendors/",
        "packages/hla2010-rti-pitch-common/docs/evidence/",
        "analysis/preflight_artifacts/",
        "analysis/vendor_runtime_status/",
        "tests/test_rti_pitch_split_packages.py::",
    )

    for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4"):
        for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
            refs = row.evidence_refs_for(field)
            assert all(ref.startswith(allowed_prefixes) for ref in refs), (
                row.identifier,
                field,
                refs,
            )
            assert not any(ref.startswith("tests/backends/") for ref in refs), (
                row.identifier,
                field,
            )
            assert not any(ref.startswith("tests/verification/") for ref in refs), (
                row.identifier,
                field,
            )
