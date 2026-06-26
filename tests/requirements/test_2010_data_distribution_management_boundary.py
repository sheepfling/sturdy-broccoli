from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md"


def test_ddm_partial_tail_is_only_pre_exc_and_exc_api() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 16
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "EXC_API": 10,
        "EXC": 6,
    }


def test_ddm_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "2010 Data-Distribution-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-DDM`" in text
    assert "`207 mapped`" in text
    assert "`16 partial`" in text
    assert "`10 EXC_API`" in text
    assert "`6 EXC`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-focus run time`" in text
    assert "Execution-membership reading for this family:" in text
    assert "before a federate joins, after it resigns, or after it disconnects" in normalized
    assert "region-gated interaction and request-update services are expected to reject the caller as not connected or not joined" in normalized
    assert "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001`" in text
    assert "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001`" in text
    assert "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001`" in text
    assert "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001`" in text
    assert "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "`./tools/test-focus run execution-membership`" in text


def test_ddm_execution_membership_pre_rows_are_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    send_row = rows["HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001"]
    update_row = rows["HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001"]

    assert send_row["current_status"] == "mapped"
    assert (
        "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in send_row["current_test_id"]
    )
    assert "applicable precondition surface" in send_row["notes"]
    assert "execution-membership" in send_row["notes"]

    assert update_row["current_status"] == "mapped"
    assert (
        "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in update_row["current_test_id"]
    )
    assert "applicable precondition surface" in update_row["notes"]
    assert "execution-membership" in update_row["notes"]


def test_ddm_subscription_and_region_association_pre_rows_are_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    expected = {
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "attribute-definition validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }

    for requirement_id, phrase in expected.items():
        row = rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert "applicable precondition surface" in row["notes"]
        assert phrase in row["notes"]


def test_ddm_register_object_instance_with_regions_pre_row_is_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }
    row = rows["HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-PRE-001"]

    assert row["current_status"] == "mapped"
    assert "test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region" in row["current_test_id"]
    assert "test_strict_publication_gates_registration_update_and_interaction_sends" in row["current_test_id"]
    assert "publication-state" in row["notes"]
    assert "duplicate-name" in row["notes"]


def test_ddm_create_commit_and_unsubscribe_interaction_pre_rows_are_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    expected = {
        "HLA1516.1-DDM-9_2-CREATEREGION-PRE-001": "invalid-dimension",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-PRE-001": "invalid-region",
        "HLA1516.1-DDM-9_4-DELETEREGION-PRE-001": "region-in-use",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }
    for requirement_id, phrase in expected.items():
        row = rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert "applicable precondition surface" in row["notes"]
        assert phrase in row["notes"]


def test_ddm_region_lifecycle_exception_rows_are_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    expected = {
        "HLA1516.1-DDM-9_2-CREATEREGION-EXC-001": "invalid-dimension",
        "HLA1516.1-DDM-9_2-RTIAPI-001-EXC": "invalid-dimension",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-EXC-001": "foreign-region ownership",
        "HLA1516.1-DDM-9_3-RTIAPI-001-EXC": "foreign-region ownership",
        "HLA1516.1-DDM-9_4-DELETEREGION-EXC-001": "region-in-use",
        "HLA1516.1-DDM-9_4-RTIAPI-001-EXC": "region-in-use",
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-EXC-001": "invalid-region-context",
        "HLA1516.1-DDM-9_6-RTIAPI-001-EXC": "invalid-region-context",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-EXC-001": "object-knownness",
        "HLA1516.1-DDM-9_7-RTIAPI-001-EXC": "object-knownness",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-EXC-001": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-RTIAPI-001-EXC": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-RTIAPI-001-EXC-DUP02": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001": "interaction-class-not-defined",
        "HLA1516.1-DDM-9_11-RTIAPI-001-EXC": "interaction-class-not-defined",
    }

    for requirement_id, phrase in expected.items():
        row = rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert phrase in row["notes"]
