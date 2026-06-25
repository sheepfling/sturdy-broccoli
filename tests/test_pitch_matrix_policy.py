from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from compliance_helpers import (
    IEEE_1516_1_2010,
    clause_summary_counts,
    is_1516_1_2010_clause,
    is_1516_1_2010_row,
    is_1516_2_2010_row,
)

ROOT = Path(__file__).resolve().parents[1]
PITCH_MATRIX_PATH = ROOT / "tests" / "vendors" / "test_pitch_real_backend_matrix.py"
PITCH_TRANSPORT_DIVERGENCE_NOTE = (
    "packages/hla-vendor-pitch/docs/evidence/"
    "pitch_transport_subset_vendor_divergence_2026-06-11.md"
)
PITCH_NEGOTIATED_OWNERSHIP_VENDOR_BUG_NOTE = (
    "packages/hla-vendor-pitch/docs/evidence/"
    "pitch_negotiated_ownership_vendor_bug_2026-06-07.md"
)
PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_NOTE = (
    "packages/hla-vendor-pitch/docs/evidence/"
    "pitch_section8_time_management_vendor_divergence_2026-06-11.md"
)
PITCH_LOST_FEDERATE_GAP_NOTE = (
    "packages/hla-vendor-pitch/docs/evidence/"
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


def _clause6_pitch_compliance_wrapper_refs() -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref.split("::", 1)[1]
        for row in payload["rows"]
        if is_1516_1_2010_clause(row, "6")
        for ref in row["evidence_refs"]
        if ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::")
    }


def _clause6_pitch_vendor_divergent_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row)
        and row.get("clause_root") == "6"
        and row.get("pitch_disposition") == "vendor-divergent"
    ]


def _clause7_pitch_vendor_divergent_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row)
        and row.get("clause_root") == "7"
        and row.get("pitch_disposition") == "vendor-divergent"
    ]


def _clause8_pitch_vendor_divergent_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row)
        and row.get("clause_root") == "8"
        and row.get("pitch_disposition") == "vendor-divergent"
    ]


def _pitch_classification_required_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if row.get("pitch_disposition") == "classification-required"
    ]


def _pitch_backlog_classification_required_rows() -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json").read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if row.get("backend_id") == "pitch-requirements" and row.get("current_status") == "classification-required"
    ]


def _pitch_rows(filename: str) -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row) or is_1516_2_2010_row(row) or row.get("document") in {"IEEE 1516-2010", "multi-section"}
    ]


def _pitch_clause_rows(filename: str, clause_root: str) -> list[dict[str, object]]:
    return [
        row
        for row in _pitch_rows(filename)
        if is_1516_1_2010_clause(row, clause_root)
    ]


def _clause4_pitch_compliance_wrapper_refs() -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref.split("::", 1)[1]
        for row in payload["rows"]
        if is_1516_1_2010_clause(row, "4")
        for ref in row["evidence_refs"]
        if ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::")
    }


def _uses_shared_runner(source: str, runner_name: str) -> bool:
    if _scenario_entrypoints(source) == [runner_name]:
        return True
    return "_run_pitch_section8_pair(" in source and source.count(runner_name) == 1


def test_clause4_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    sources = _pitch_matrix_function_sources()
    assert set(TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert f"{runner_name}(" in source, function_name
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def test_clause4_pitch_compliance_wrappers_are_all_guarded_by_policy() -> None:
    sources = _pitch_matrix_function_sources()
    guarded_functions = set(TARGET_FUNCTIONS) | {"test_pitch_backend_lost_federate_mom_matrix"}
    assert _clause4_pitch_compliance_wrapper_refs().issubset(guarded_functions)
    assert _clause4_pitch_compliance_wrapper_refs().issubset(set(sources) | {"test_pitch_backend_lost_federate_mom_matrix"})


def test_pitch_classification_required_rows_do_not_claim_blank_dispositions() -> None:
    rows = _pitch_classification_required_rows()
    assert rows

    for row in rows:
        note = str(row.get("notes", ""))
        assert "explicitly generated as classification-required" in note
        assert "disposition is blank" not in note


def test_generated_pitch_profile_requirement_disposition_markdown_keeps_inheritance_note_explicit() -> None:
    for filename, profile in (
        ("pitch-jpype_requirement_disposition.md", "pitch-jpype"),
        ("pitch-py4j_requirement_disposition.md", "pitch-py4j"),
    ):
        text = (ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8")
        assert f"every row has an explicit generated `{profile}` disposition." in text
        assert "inherits the Pitch family-level requirement disposition" in text


def test_pitch_profile_requirement_disposition_artifacts_inherit_family_rows() -> None:
    family_rows = _pitch_rows("pitch_requirement_disposition.json")
    assert family_rows

    family_index = {str(row["requirement_id"]): row for row in family_rows}

    for filename, disposition_field, evidence_field in (
        ("pitch-jpype_requirement_disposition.json", "pitch_jpype_disposition", "pitch_jpype_evidence_refs"),
        ("pitch-py4j_requirement_disposition.json", "pitch_py4j_disposition", "pitch_py4j_evidence_refs"),
    ):
        profile_rows = _pitch_rows(filename)
        assert {str(row["requirement_id"]) for row in profile_rows} == set(family_index), filename

        for row in profile_rows:
            requirement_id = str(row["requirement_id"])
            family_row = family_index[requirement_id]
            assert row.get("runtime_disposition") == family_row.get(disposition_field), (
                filename,
                requirement_id,
            )
            assert tuple(row.get("evidence_refs", ())) == tuple(family_row.get(evidence_field, ())), (
                filename,
                requirement_id,
            )
            assert str(row.get("notes", "")) == str(family_row.get("notes", "")), (
                filename,
                requirement_id,
            )


def test_pitch_tranche_clauses_4_6_7_8_9_have_no_not_yet_tested_rows_in_family_or_profiles() -> None:
    target_clauses = ("4", "6", "7", "8", "9")

    family_rows = _pitch_rows("pitch_requirement_disposition.json")
    for clause_root in target_clauses:
        clause_rows = [
            row
            for row in family_rows
            if is_1516_1_2010_clause(row, clause_root)
        ]
        assert clause_rows, clause_root
        for disposition_key in ("pitch_disposition", "pitch_jpype_disposition", "pitch_py4j_disposition"):
            assert not {
                str(row["requirement_id"])
                for row in clause_rows
                if row.get(disposition_key) == "not-yet-tested"
            }, (clause_root, disposition_key)

    for filename in ("pitch-jpype_requirement_disposition.json", "pitch-py4j_requirement_disposition.json"):
        for clause_root in target_clauses:
            clause_rows = _pitch_clause_rows(filename, clause_root)
            assert clause_rows, (filename, clause_root)
            assert not {
                str(row["requirement_id"])
                for row in clause_rows
                if row.get("runtime_disposition") == "not-yet-tested"
            }, (filename, clause_root)


def test_pitch_vendor_backlog_classification_required_rows_track_explicit_state() -> None:
    rows = _pitch_backlog_classification_required_rows()
    assert rows

    for row in rows:
        rationale = str(row.get("rationale", ""))
        assert "explicitly generated as classification-required" in rationale
        assert "disposition is blank" not in rationale


def test_clause6_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    sources = _pitch_matrix_function_sources()
    assert set(CLAUSE6_TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in CLAUSE6_TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert f"{runner_name}(" in source, function_name
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


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
    assert {str(row["requirement_id"]) for row in rows} == expected_ids

    for row in rows:
        refs = set(row["evidence_refs"])
        assert PITCH_TRANSPORT_DIVERGENCE_NOTE in refs
        assert (
            "packages/hla-verification/src/hla.verification/"
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
        refs = set(row["evidence_refs"])
        if str(row["requirement_id"]) in restore_subset_ids:
            assert (
                "packages/hla-verification/src/hla.verification/"
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
    assert {str(row["requirement_id"]) for row in rows} == expected_ids

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
        refs = set(row["evidence_refs"])
        assert PITCH_NEGOTIATED_OWNERSHIP_VENDOR_BUG_NOTE in refs
        if str(row["requirement_id"]) in offer_probe_ids:
            assert (
                "packages/hla-verification/src/hla.verification/"
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
            assert str(row["requirement_id"]) in full_negotiated_ids
            assert (
                "packages/hla-verification/src/hla.verification/"
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
    sources = _pitch_matrix_function_sources()
    assert set(CLAUSE7_TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in CLAUSE7_TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert f"{runner_name}(" in source, function_name
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not CLAUSE7_DIRECT_BACKEND_CALL_RE.search(source), function_name


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
    assert {str(row["requirement_id"]) for row in rows} == expected_ids

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
        requirement_id = str(row["requirement_id"])
        refs = set(row["evidence_refs"])
        assert PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_NOTE in refs
        if requirement_id in ordering_and_query_ids:
            assert (
                "packages/hla-verification/src/hla.verification/"
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
                "packages/hla-verification/src/hla.verification/"
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
                "packages/hla-verification/src/hla.verification/"
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
                "packages/hla-verification/src/hla.verification/"
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
                "packages/hla-verification/src/hla.verification/"
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
    sources = _pitch_matrix_function_sources()
    assert set(CLAUSE8_TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in CLAUSE8_TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert _uses_shared_runner(source, runner_name), function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def test_clause9_pitch_backend_matrix_functions_stay_shared_harness_wrappers() -> None:
    sources = _pitch_matrix_function_sources()
    assert set(CLAUSE9_TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in CLAUSE9_TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


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
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {
        str(row["requirement_id"]): row
        for row in payload["rows"]
        if str(row.get("requirement_id")) in {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}
    }
    assert set(rows) == {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}

    for requirement_id, row in rows.items():
        assert row.get("pitch_disposition") == "blocked", requirement_id
        assert row.get("pitch_jpype_disposition") == "blocked", requirement_id
        assert row.get("pitch_py4j_disposition") == "blocked", requirement_id

        family_refs = set(row.get("evidence_refs", ()))
        jpype_refs = set(row.get("pitch_jpype_evidence_refs", ()))
        py4j_refs = set(row.get("pitch_py4j_evidence_refs", ()))

        assert PITCH_LOST_FEDERATE_GAP_NOTE in family_refs
        assert "artifacts/preflight_artifacts/pitch-preflight.json" in family_refs
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/"
            "vendor_runtime_status_summary.json"
        ) in family_refs
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/"
            "vendor_runtime_status_report.md"
        ) in family_refs
        assert (
            "packages/hla-verification/src/hla.verification/"
            "scenario_connection_lost.py::run_connection_lost_callback_scenario"
        ) in family_refs
        assert (
            "packages/hla-verification/src/hla.verification/"
            "scenario_resign.py::run_disconnect_mom_cleanup_scenario"
        ) in family_refs
        assert (
            "packages/hla-verification/src/hla.verification/"
            "scenario_lost_federate.py::run_lost_federate_mom_scenario"
        ) in family_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in family_refs

        assert PITCH_LOST_FEDERATE_GAP_NOTE in jpype_refs
        assert (
            "packages/hla-verification/src/hla.verification/"
            "scenario_lost_federate.py::run_external_lost_federate_observer_scenario"
        ) in jpype_refs
        assert (
            "tests/test_rti_pitch_split_packages.py::"
            "test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process"
        ) in jpype_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in jpype_refs
        assert "artifacts/preflight_artifacts/pitch-preflight.json" in jpype_refs

        assert PITCH_LOST_FEDERATE_GAP_NOTE in py4j_refs
        assert (
            "packages/hla-verification/src/hla.verification/"
            "scenario_lost_federate.py::run_lost_federate_mom_scenario"
        ) in py4j_refs
        assert (
            "tests/test_rti_pitch_split_packages.py::"
            "test_pitch_py4j_factory_attaches_gateway_process"
        ) in py4j_refs
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix"
        ) in py4j_refs
        assert "artifacts/preflight_artifacts/pitch-preflight.json" in py4j_refs


def test_clause4_pitch_lost_federate_rows_keep_exact_backlog_frontier_shape() -> None:
    payload = json.loads((ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json").read_text(encoding="utf-8"))
    target_ids = {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}

    rows_by_requirement: dict[str, list[dict[str, object]]] = {}
    for row in payload["rows"]:
        requirement_id = str(row.get("requirement_id", ""))
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
                str(row.get("backend_id", "")),
                str(row.get("current_status", "")),
                str(row.get("row_kind", "")),
            )
            for row in rows
        } == expected_surface, requirement_id

        for row in rows:
            assert str(row.get("priority", "")) == "P2", requirement_id
            assert (
                str(row.get("recommended_next_action", ""))
                == "unblock capability or document the hard backend limitation"
            ), requirement_id
            assert (
                str(row.get("source_artifact", "")) == "analysis/compliance/pitch_requirement_disposition.json"
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
        str(row.get("requirement_id") or row.get("matrix_id")): str(row.get("pitch_disposition"))
        for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4")
        if row.get("pitch_disposition") != "verified"
    }
    assert family_rows == expected

    for filename in ("pitch-jpype_requirement_disposition.json", "pitch-py4j_requirement_disposition.json"):
        profile_rows = {
            str(row.get("requirement_id") or row.get("matrix_id")): str(row.get("runtime_disposition"))
            for row in _pitch_clause_rows(filename, "4")
            if row.get("runtime_disposition") != "verified"
        }
        assert profile_rows == expected, filename


def test_clause4_pitch_family_and_profiles_keep_exact_summary_counts() -> None:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))

    expected = {
        "blocked": 2,
        "not-applicable": 2,
        "total": 281,
        "vendor-divergent": 3,
        "verified": 274,
    }
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "4") == expected
    assert clause_summary_counts(payload["summary"]["profile_clause_summary"]["pitch-jpype"], IEEE_1516_1_2010, "4") == expected
    assert clause_summary_counts(payload["summary"]["profile_clause_summary"]["pitch-py4j"], IEEE_1516_1_2010, "4") == expected


def test_clause4_pitch_family_and_profile_evidence_stays_on_allowed_surfaces() -> None:
    allowed_prefixes = (
        "packages/hla-verification/",
        "tests/scenarios/",
        "tests/vendors/",
        "packages/hla-vendor-pitch/docs/evidence/",
        "artifacts/preflight_artifacts/",
        "artifacts/vendor_runtime_status/",
        "tests/test_rti_pitch_split_packages.py::",
    )

    for row in _pitch_clause_rows("pitch_requirement_disposition.json", "4"):
        for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
            refs = tuple(str(ref) for ref in row.get(field, ()))
            assert all(ref.startswith(allowed_prefixes) for ref in refs), (
                str(row.get("requirement_id") or row.get("matrix_id")),
                field,
                refs,
            )
            assert not any(ref.startswith("tests/backends/") for ref in refs), (
                str(row.get("requirement_id") or row.get("matrix_id")),
                field,
            )
            assert not any(ref.startswith("tests/verification/") for ref in refs), (
                str(row.get("requirement_id") or row.get("matrix_id")),
                field,
            )
