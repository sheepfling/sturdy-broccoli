from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_fm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md"


def test_federation_management_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {}


def test_federation_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "2010 Federation-Management Bounded Family" in text
    assert "## Final State" in text
    assert "## Reopen Condition" in text
    assert "CAP-FM" in text
    assert "`./tools/test-focus run execution-membership`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text
    assert "Execution-membership guard coverage is also part of the current 2010 bounded reading" in normalized
    assert "`NotConnected` or `FederateNotExecutionMember`" in text
    assert "`FederatesCurrentlyJoined`" in text
    assert "`FederationExecutionDoesNotExist`" in text
    assert "[`object_management_bounded_family.md`](object_management_bounded_family.md)" in text
    assert "Current exact execution-membership evidence anchors for this 2010 reading:" in text
    assert "test_destroy_federation_execution_requires_no_joined_federates" in text
    assert "test_resign_federation_execution_rejects_not_connected_and_not_joined" in text
    assert "test_disconnect_requires_resign_and_marks_backend_not_connected" in text
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in text
    assert "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore" in text
    assert "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "test_python_backend_join_precondition_matrix" in text
    assert "test_python_backend_resign_precondition_matrix" in text
    assert "test_force_federate_loss_delivers_connection_lost_and_clears_execution_membership" in text
    assert "test_force_federate_loss_requires_joined_live_victim_and_honors_callback_model" in text
    assert "test_force_federate_loss_honors_cancel_delete_divest_automatic_resign_cleanup" in text
    assert "test_force_federate_loss_honors_unconditional_divest_automatic_resign_cleanup" in text
    assert "test_federation_management_lifecycle_states_cover_connected_joined_resigned_and_disconnected" in text
    assert "test_create_federation_execution_maintains_current_fdd_modules_and_standard_mim" in text
    assert "test_create_federation_execution_defaults_to_hlafloat64_time_when_logical_time_is_omitted" in text
    assert "test_create_federation_execution_accepts_explicit_logical_time_implementation" in text
    assert "test_connection_lost_and_report_federation_executions_wrap_callback_failures_as_federate_internal_error" in text
    assert "test_list_federation_executions_is_observable_through_mom_service_invocation_reporting" in text
    assert "test_list_federation_executions_surfaces_rti_internal_error_for_corrupt_runtime_state" in text
    assert "test_request_federation_save_latest_scheduled_request_supersedes_prior_requested_save" in text
    assert "test_resign_canceling_directives_clear_pending_acquisition_requests" in text
    assert "requirements/2010/hla1516_1_fm_detailed_reconciliation.csv" in text
    assert "requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv" in text
    assert "requirements/2010/traceability_matrix.csv" in text
    assert "requirement_compliance_exports.md" in text
    assert "../../plans/requirements_gap_register.md" not in text
