from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_om_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/object_management_bounded_family.md"


def test_object_management_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 76
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "EFF": 12,
        "CB_ORD": 25,
        "EXC_API": 8,
        "CB_ORDER": 17,
        "EXC": 7,
        "FED_CB": 6,
        "OVW": 1,
    }


def test_object_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "2010 Object-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-OM`" in text
    assert "`315 mapped`" in text
    assert "`76 partial`" in text
    assert "`12 EFF`" in text
    assert "`25 CB_ORD`" in text
    assert "`8 EXC_API`" in text
    assert "`17 CB_ORDER`" in text
    assert "`7 EXC`" in text
    assert "`./tools/test-focus run execution-membership`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text
    assert "`updateAttributeValues` exception rows no longer live in this partial tail" in normalized
    assert "`updateAttributeValues` precondition row no longer lives in this partial tail" in normalized
    assert "`updateAttributeValues` effect rows no longer live in this partial tail" in normalized
    assert "`reserveObjectInstanceName` precondition row no longer lives in this partial tail" in normalized
    assert "`localDeleteObjectInstance` precondition row no longer lives in this partial tail" in normalized
    assert "multiple-name reservation and release precondition rows no longer live in this partial tail" in normalized
    assert "object-instance overload exception row for `requestAttributeValueUpdate` no longer lives in this partial tail" in normalized
    assert "`registerObjectInstance` precondition row no longer lives in this partial tail" in normalized
    assert "`registerObjectInstance` effect and exception rows no longer live in this partial tail" in normalized
    assert "`releaseObjectInstanceName` precondition row no longer lives in this partial tail" in normalized
    assert "`releaseObjectInstanceName` effect and exception rows no longer live in this partial tail" in normalized
    assert "`deleteObjectInstance` precondition row no longer lives in this partial tail" in normalized
    assert "`deleteObjectInstance` effect and exception rows no longer live in this partial tail" in normalized
    assert "`sendInteraction` precondition row no longer lives in this partial tail" in normalized
    assert "`requestAttributeValueUpdate` precondition row no longer lives in this partial tail" in normalized
    assert "class-wide `requestAttributeValueUpdate` exception rows no longer live in this partial tail" in normalized
    assert "`localDeleteObjectInstance` effect and exception rows no longer live in this partial tail" in normalized
    assert "`releaseMultipleObjectInstanceName` effect and exception rows no longer live in this partial tail" in normalized
    assert "`HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`" in text
    assert "`HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001`" in text
    assert "`HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`" in text
    assert "`HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`" in text


def test_update_attribute_values_exception_rows_are_now_directly_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_10-RTIAPI-001-EXC",
        "HLA1516.1-OM-6_10-RTIAPI-002-EXC",
        "HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"

    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in rows[
        "HLA1516.1-OM-6_10-RTIAPI-001-EXC"
    ]["current_test_id"]
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in rows[
        "HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001"
    ]["current_test_id"]
    assert "test_strict_publication_and_invalid_logical_time_guards_block_object_and_interaction_delivery" in rows[
        "HLA1516.1-OM-6_10-RTIAPI-002-EXC"
    ]["current_test_id"]


def test_update_attribute_values_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in row["current_test_id"]
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "`updateAttributeValues` overloads" in row["notes"]


def test_update_attribute_values_effect_rows_are_now_mapped_to_the_supported_routing_slice() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_10-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EFF-001",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"
        assert "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions" in rows[requirement_id][
            "current_test_id"
        ]
        assert "direct routing witness" in rows[requirement_id]["notes"]


def test_local_delete_object_instance_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "ownership-state" in row["notes"]


def test_register_object_instance_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in row["current_test_id"]
    assert "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "`registerObjectInstance` overloads" in row["notes"]


def test_register_object_instance_effect_and_exception_rows_are_now_mapped_to_supported_surfaces() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EFF-001",
        "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001",
        "HLA1516.1-OM-6_8-RTIAPI-001-EXC",
        "HLA1516.1-OM-6_8-RTIAPI-002-EXC",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"

    assert "test_two_python_federates_share_in_memory_rti" in rows[
        "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EFF-001"
    ]["current_test_id"]
    assert "ObjectClassNotPublished" in rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001"]["requirement_text"]
    assert "ObjectClassNotDefined" in rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001"]["requirement_text"]
    assert "ObjectInstanceNameNotReserved" not in rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001"]["requirement_text"]


def test_release_object_instance_name_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "`releaseObjectInstanceName`" in row["notes"]


def test_release_name_effect_and_exception_rows_are_now_mapped_to_supported_surfaces() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EFF-001",
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EXC-001",
        "HLA1516.1-OM-6_4-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_4-RTIAPI-001-EXC",
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EFF-001",
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EXC-001",
        "HLA1516.1-OM-6_7-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_7-RTIAPI-001-EXC",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"

    assert "test_name_reservation_and_release_effects_manage_state_without_creating_objects" in rows[
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EFF-001"
    ]["current_test_id"]
    assert "ObjectInstanceNameNotReserved" not in rows[
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EXC-001"
    ]["requirement_text"]
    assert "SaveInProgress" in rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EXC-001"]["requirement_text"]
    assert "test_name_reservation_and_release_effects_manage_state_without_creating_objects" in rows[
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EFF-001"
    ]["current_test_id"]
    assert "ObjectInstanceNameNotReserved" not in rows[
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EXC-001"
    ]["requirement_text"]


def test_reserve_object_instance_name_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "`reserveObjectInstanceName`" in row["notes"]


def test_delete_object_instance_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "delete-privilege" in row["notes"]


def test_delete_and_local_delete_effect_and_exception_rows_are_now_mapped_to_supported_surfaces() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EFF-001",
        "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EXC-001",
        "HLA1516.1-OM-6_14-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_14-RTIAPI-001-EXC",
        "HLA1516.1-OM-6_14-RTIAPI-002-EXC",
        "HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EFF-001",
        "HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EXC-001",
        "HLA1516.1-OM-6_16-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_16-RTIAPI-001-EXC",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"

    assert "test_delete_object_instance_notifies_known_federates_with_remove_object_instance" in rows[
        "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EFF-001"
    ]["current_test_id"]
    assert "InvalidLogicalTime" in rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EXC-001"]["requirement_text"]
    assert "RTIinternalError" not in rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EXC-001"]["requirement_text"]
    assert "test_local_delete_clears_only_local_knowledge_and_object_can_be_rediscovered" in rows[
        "HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EFF-001"
    ]["current_test_id"]
    assert "OwnershipAcquisitionPending" in rows["HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EXC-001"]["requirement_text"]
    assert "RTIinternalError" not in rows["HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EXC-001"]["requirement_text"]


def test_send_interaction_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in row["current_test_id"]
    assert "test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "`sendInteraction` overloads" in row["notes"]


def test_multiple_name_reservation_and_release_precondition_rows_are_now_mapped() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    reserve_row = rows["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-PRE-001"]
    release_row = rows["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-PRE-001"]

    assert reserve_row["current_status"] == "mapped"
    assert "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore" in reserve_row["current_test_id"]
    assert "applicable precondition surface" in reserve_row["notes"]

    assert release_row["current_status"] == "mapped"
    assert "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore" in release_row["current_test_id"]
    assert "applicable precondition surface" in release_row["notes"]


def test_request_attribute_value_update_exception_rows_split_object_instance_and_class_wide_claims_honestly() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    assert rows["HLA1516.1-OM-6_19-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_19-RTIAPI-002-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-EXC-001"]["current_status"] == "mapped"
    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in rows[
        "HLA1516.1-OM-6_19-RTIAPI-001-EXC"
    ]["current_test_id"]
    assert "ObjectClassNotDefined" in rows["HLA1516.1-OM-6_19-RTIAPI-002-EXC"]["notes"]


def test_request_attribute_value_update_precondition_row_is_now_mapped_to_the_applicable_guard_surface() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    row = rows["HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001"]
    assert row["current_status"] == "mapped"
    assert "test_clause_6_federate_initiated_services_validate_core_argument_shapes" in row["current_test_id"]
    assert "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore" in row["current_test_id"]
    assert "applicable precondition surface" in row["notes"]
    assert "class-wide `requestAttributeValueUpdate` overloads" in row["notes"]
