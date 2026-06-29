from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_om_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/object_management_bounded_family.md"


def test_object_management_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    assert Counter(row["current_status"] for row in rows) == {"mapped": 391}


def test_object_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "2010 Object-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-OM`" in text
    assert "`391 mapped`" in text
    assert "`0 partial`" in text
    assert "`requirements/2010/canonical_requirements.json`" in text
    assert "`requirements/2010/backend_resolution.json`" in text
    assert "`requirements/2010/hla1516_1_om_detailed_reconciliation.csv`" in text
    assert "`requirements/2010/traceability_matrix.csv`" in text
    assert "generated projection bridge" in text
    assert "`docs/verification/requirement_compliance_exports.md`" in text
    assert "`./tools/test-focus run execution-membership`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text
    assert "owner ledger no longer carries any remaining OM `partial` rows" in normalized
    assert "time-managed delete behavior is mapped only because the current witness directly proves deferred removal until grant" in normalized
    assert "`HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`" in text
    assert "`HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001`" in text
    assert "`HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`" in text
    assert "`HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`" in text
    assert "../../plans/requirements_gap_register.md" not in text


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
    assert "test_strict_publication_gates_registration_update_and_interaction_sends" in rows[
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


def test_reserve_name_effect_and_exception_rows_are_now_mapped_to_supported_surfaces() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    for requirement_id in (
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EFF-001",
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EXC-001",
        "HLA1516.1-OM-6_2-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_2-RTIAPI-001-EXC",
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EFF-001",
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EXC-001",
        "HLA1516.1-OM-6_5-RTIAPI-001-EFF",
        "HLA1516.1-OM-6_5-RTIAPI-001-EXC",
    ):
        assert rows[requirement_id]["current_status"] == "mapped"

    assert "test_name_reservation_and_release_effects_manage_state_without_creating_objects" in rows[
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EFF-001"
    ]["current_test_id"]
    assert "IllegalName" not in rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EXC-001"]["requirement_text"]
    assert "SaveInProgress" in rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EXC-001"]["requirement_text"]
    assert "test_name_reservation_and_release_effects_manage_state_without_creating_objects" in rows[
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EFF-001"
    ]["current_test_id"]
    assert "NameSetWasEmpty" not in rows[
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EXC-001"
    ]["requirement_text"]


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
