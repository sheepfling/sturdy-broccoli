from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_1_ddm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_ddm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 223
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 223})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_ddm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-DDM-OVERVIEW-012"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-OVERVIEW-012"]["reconciliation_kind"] == "OVW"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"]["reconciliation_kind"] == "SIG"
    assert rows["HLA1516.1-DDM-9_5-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_5-001"]["reconciliation_kind"] == "SVC"
    assert rows["HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_5-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_8-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"]["reconciliation_kind"] == "TEST"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"]["reconciliation_kind"] == "RET"


def test_ddm_region_lifecycle_exception_rows_are_now_directly_mapped() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

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


def test_ddm_execution_membership_pre_promotions_are_recorded() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    send_row = rows["HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001"]
    update_row = rows["HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001"]

    assert send_row["current_status"] == "mapped"
    assert (
        "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in send_row["current_test_id"]
    )
    assert "publication-state" in send_row["notes"]
    assert "invalid-logical-time" in send_row["notes"]

    assert update_row["current_status"] == "mapped"
    assert (
        "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in update_row["current_test_id"]
    )
    assert "class-handle and attribute-definition validation" in update_row["notes"]
    assert "invalid-region" in update_row["notes"]


def test_ddm_subscription_and_region_association_pre_promotions_are_recorded() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    promoted = {
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "attribute-definition validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }

    for requirement_id, phrase in promoted.items():
        row = rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert "applicable precondition surface" in row["notes"]
        assert phrase in row["notes"]


def test_ddm_register_object_instance_with_regions_pre_promotion_is_recorded() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-PRE-001"]

    assert row["current_status"] == "mapped"
    assert "test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region" in row["current_test_id"]
    assert "test_strict_publication_gates_registration_update_and_interaction_sends" in row["current_test_id"]
    assert "publication-state" in row["notes"]
    assert "duplicate-name" in row["notes"]


def test_ddm_create_commit_and_unsubscribe_interaction_pre_promotions_are_recorded() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    promoted = {
        "HLA1516.1-DDM-9_2-CREATEREGION-PRE-001": "invalid-dimension",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-PRE-001": "invalid-region",
        "HLA1516.1-DDM-9_4-DELETEREGION-PRE-001": "region-in-use",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }
    for requirement_id, phrase in promoted.items():
        row = rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert "applicable precondition surface" in row["notes"]
        assert phrase in row["notes"]
