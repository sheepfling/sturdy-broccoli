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

    assert len(partial_rows) == 79
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "ARG": 43,
        "CB_ORD": 17,
        "EFF": 4,
        "EXC": 4,
        "OVW": 3,
        "CB": 2,
        "FED_CB": 1,
        "MOM": 1,
        "PRE": 1,
        "SVC": 1,
        "EXC_API": 1,
        "MOM_TRACE": 1,
    }


def test_federation_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "2010 Federation-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-FM`" in text
    assert "`529 mapped`" in text
    assert "`79 partial`" in text
    assert "`43 ARG`" in text
    assert "`17 CB_ORD`" in text
    assert "`4 EFF`" in text
    assert "`4 EXC`" in text
    assert "`3 OVW`" in text
    assert "`2 CB`" in text
    assert "`1 FED_CB`" in text
    assert "`1 PRE`" in text
    assert "`1 EXC_API`" in text
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
    assert "Lost-connection callback/fault-surface tail" in text
    assert "List/report federation breadth tail" in text
    assert "argument-harmonization tail" in text
    assert "requirements/2010/hla1516_1_fm_detailed_reconciliation.csv" in text
    assert "requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv" in text
    assert "requirements/2010/traceability_matrix.csv" in text
    assert "requirement_compliance_exports.md" in text
    assert "../../plans/requirements_gap_register.md" not in text
