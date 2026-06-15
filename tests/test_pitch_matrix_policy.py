from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from conftest import REPO_ROOT, load_compliance_json, load_compliance_text
from tests.compliance_row_models import RequirementDispositionRow, VendorBacklogRow
from tests.pitch_clause4_policy_helpers import (
    PITCH_CLAUSE4_ALLOWED_EVIDENCE_PREFIXES,
    PITCH_CLAUSE4_BACKLOG_FRONTIER,
    PITCH_CLAUSE4_BLOCKED_FAMILY_REFS,
    PITCH_CLAUSE4_BLOCKED_JPYPE_REFS,
    PITCH_CLAUSE4_BLOCKED_NOTES_FRAGMENTS,
    PITCH_CLAUSE4_BLOCKED_PY4J_REFS,
    PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS,
    PITCH_CLAUSE4_RESIDUAL_FRONTIER,
    load_requirement_rows as load_pitch_requirement_rows,
    load_vendor_backlog_rows as load_pitch_vendor_backlog_rows,
    pitch_clause_rows,
)
from tests.pitch_matrix_policy_helpers import PITCH_MATRIX_POLICY
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
    return load_pitch_requirement_rows(filename)


def _load_vendor_backlog_rows(filename: str) -> list[VendorBacklogRow]:
    return load_pitch_vendor_backlog_rows(filename)


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
    return pitch_clause_rows(filename, clause_root)


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
    target_clauses = PITCH_MATRIX_POLICY.tranche_clauses_no_not_yet_tested

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

    policy = PITCH_MATRIX_POLICY.vendor_divergence_cases["6"]
    assert {row.requirement_id for row in rows} == policy.expected_ids

    for row in rows:
        refs = set(row.evidence_refs)
        for ref in policy.shared_refs:
            assert ref in refs
        for group in policy.groups.values():
            if row.requirement_id in group.ids:
                for ref in group.refs:
                    assert ref in refs


def test_clause7_pitch_vendor_divergent_rows_stay_explicit_negotiated_ownership_policy() -> None:
    rows = _clause7_pitch_vendor_divergent_rows()
    assert rows

    policy = PITCH_MATRIX_POLICY.vendor_divergence_cases["7"]
    assert {row.requirement_id for row in rows} == policy.expected_ids

    for row in rows:
        refs = set(row.evidence_refs)
        for ref in policy.shared_refs:
            assert ref in refs
        for group in policy.groups.values():
            if row.requirement_id in group.ids:
                for ref in group.refs:
                    assert ref in refs


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

    policy = PITCH_MATRIX_POLICY.vendor_divergence_cases["8"]
    assert {row.requirement_id for row in rows} == policy.expected_ids

    for row in rows:
        refs = set(row.evidence_refs)
        for ref in policy.shared_refs:
            assert ref in refs
        for group in policy.groups.values():
            if row.requirement_id in group.ids:
                for ref in group.refs:
                    assert ref in refs


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
        if row.requirement_id in PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS
    }
    assert set(rows) == PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS

    for requirement_id, row in rows.items():
        assert row.pitch_disposition == "blocked", requirement_id
        assert row.pitch_jpype_disposition == "blocked", requirement_id
        assert row.pitch_py4j_disposition == "blocked", requirement_id
        for fragment in PITCH_CLAUSE4_BLOCKED_NOTES_FRAGMENTS:
            assert fragment in row.notes, requirement_id

        family_refs = set(row.evidence_refs)
        jpype_refs = set(row.pitch_jpype_evidence_refs)
        py4j_refs = set(row.pitch_py4j_evidence_refs)

        assert PITCH_CLAUSE4_BLOCKED_FAMILY_REFS.issubset(family_refs)
        assert PITCH_CLAUSE4_BLOCKED_JPYPE_REFS.issubset(jpype_refs)
        assert PITCH_CLAUSE4_BLOCKED_PY4J_REFS.issubset(py4j_refs)


def test_clause4_pitch_lost_federate_rows_keep_exact_backlog_frontier_shape() -> None:
    target_ids = PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS

    rows_by_requirement: dict[str, list[VendorBacklogRow]] = {}
    for row in _load_vendor_backlog_rows("vendor_discovery_backlog.json"):
        requirement_id = row.requirement_id
        if requirement_id in target_ids:
            rows_by_requirement.setdefault(requirement_id, []).append(row)

    assert set(rows_by_requirement) == target_ids

    for requirement_id, rows in rows_by_requirement.items():
        assert {
            (
                row.backend_id,
                row.current_status,
                row.row_kind,
            )
            for row in rows
        } == PITCH_CLAUSE4_BACKLOG_FRONTIER, requirement_id

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
    family_rows = {
        row.identifier: row.pitch_disposition
        for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4")
        if row.pitch_disposition != "verified"
    }
    assert family_rows == PITCH_CLAUSE4_RESIDUAL_FRONTIER

    for filename in ("pitch-jpype_requirement_disposition.json", "pitch-py4j_requirement_disposition.json"):
        profile_rows = {
            row.identifier: row.runtime_disposition
            for row in _pitch_clause_rows(filename, "4")
            if row.runtime_disposition != "verified"
        }
        assert profile_rows == PITCH_CLAUSE4_RESIDUAL_FRONTIER, filename


def test_clause4_pitch_family_and_profiles_keep_exact_summary_counts() -> None:
    payload = load_compliance_json("pitch_requirement_disposition.json")

    expected = PITCH_MATRIX_POLICY.clause4_summary_counts
    section_ref = federate_interface_section_ref("4")
    assert payload["summary"]["clause_summary"][section_ref] == expected
    assert payload["summary"]["profile_clause_summary"]["pitch-jpype"][section_ref] == expected
    assert payload["summary"]["profile_clause_summary"]["pitch-py4j"][section_ref] == expected


def test_clause4_pitch_family_and_profile_evidence_stays_on_allowed_surfaces() -> None:
    for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4"):
        for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
            refs = row.evidence_refs_for(field)
            assert all(ref.startswith(PITCH_CLAUSE4_ALLOWED_EVIDENCE_PREFIXES) for ref in refs), (
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
