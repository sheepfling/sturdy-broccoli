from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / "requirements"
REFERENCE_DIR = REQUIREMENTS_DIR / "2010"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_requirement_seed_files_exist_and_have_seed_rows():
    files = {
        "framework": REFERENCE_DIR / "hla1516_framework_rules.csv",
        "framework_clause12": REFERENCE_DIR / "hla1516_clause_12_save_restore.csv",
        "interface": REFERENCE_DIR / "hla1516_1_federate_interface.csv",
        "priority_1516_1": REFERENCE_DIR / "hla1516_1_priority_clauses_4_8_11.csv",
        "clause5_1516_1": REFERENCE_DIR / "hla1516_1_clause_5_declaration_management.csv",
        "clause6_1516_1": REFERENCE_DIR / "hla1516_1_clause_6_object_management.csv",
        "omt": REFERENCE_DIR / "hla1516_2_omt.csv",
        "priority_1516_2": REFERENCE_DIR / "hla1516_2_priority_omt.csv",
        "traceability": REFERENCE_DIR / "traceability_matrix.csv",
    }
    for path in files.values():
        assert path.exists(), path

    framework_rows = _rows(files["framework"])
    framework_clause12_rows = _rows(files["framework_clause12"])
    interface_rows = _rows(files["interface"])
    priority_rows = _rows(files["priority_1516_1"])
    clause5_rows = _rows(files["clause5_1516_1"])
    clause6_rows = _rows(files["clause6_1516_1"])
    omt_rows = _rows(files["omt"])
    priority_omt_rows = _rows(files["priority_1516_2"])
    trace_rows = _rows(files["traceability"])

    assert any(row["requirement_id"] == "HLA1516-RULE-001" for row in framework_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-12.1-001" for row in framework_clause12_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-12.2-003" for row in framework_clause12_rows)
    assert any(row["requirement_id"] == "HLA1516.1-FM-001" for row in interface_rows)
    assert any(row["requirement_id"] == "HLA1516.1-FM-4.2-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-TM-8.18-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-MOM-11.5-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-DM-5.2-001" for row in clause5_rows)
    assert any(row["requirement_id"] == "HLA1516.1-DM-5.8-001" for row in clause5_rows)
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.8-001" for row in clause6_rows)
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.19-002" for row in clause6_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OC-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-XML-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OC-4.2-001" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-4.9-001" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-DT-4.13-054" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-7.0-008" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-XML-ANNEX-005" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OMT-E-001" for row in priority_omt_rows)
    assert any(row["current_artifact_id"] == "REQ-MOM-OBSERVER-001" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.1-MOM-11.5-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OMT-7-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-4.9-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-7.0-008" and row["status"] == "mapped" for row in trace_rows)


def test_requirement_registry_declares_three_standard_sources():
    registry = (REFERENCE_DIR / "requirement_id_registry.yaml").read_text(encoding="utf-8")
    assert "source_id: HLA1516" in registry
    assert "source_id: HLA1516.1" in registry
    assert "source_id: HLA1516.2" in registry
    assert "HLA1516.1-FM-001" in registry


def test_coarse_2010_seed_ledgers_do_not_keep_stale_partial_rows_for_closed_clause5_clause6_and_framework_entries():
    framework_rows = {row["requirement_id"]: row for row in _rows(REFERENCE_DIR / "hla1516_framework_rules.csv")}
    clause5_rows = {row["requirement_id"]: row for row in _rows(REFERENCE_DIR / "hla1516_1_clause_5_declaration_management.csv")}
    clause6_rows = {row["requirement_id"]: row for row in _rows(REFERENCE_DIR / "hla1516_1_clause_6_object_management.csv")}
    trace_rows = {row["requirement_id"]: row for row in _rows(REFERENCE_DIR / "traceability_matrix.csv")}

    assert framework_rows["HLA1516-RULE-001"]["status"] == "pass"

    for requirement_id in (
        "HLA1516.1-DM-5.1-004",
        "HLA1516.1-DM-5.10-001",
        "HLA1516.1-DM-5.11-001",
        "HLA1516.1-DM-5.12-001",
        "HLA1516.1-DM-5.13-001",
    ):
        assert clause5_rows[requirement_id]["status"] == "pass"
        assert trace_rows[requirement_id]["status"] == "pass"

    for requirement_id in (
        "HLA1516.1-OM-6.1.5-001",
        "HLA1516.1-OM-6.1.6-001",
        "HLA1516.1-OM-6.11-002",
        "HLA1516.1-OM-6.12-004",
        "HLA1516.1-OM-6.14-002",
    ):
        assert clause6_rows[requirement_id]["status"] == "pass"

    assert trace_rows["HLA1516.1-OM-6.1.6-001"]["status"] == "pass"


def test_clause_6_packet_reconciliation_does_not_keep_stale_partial_preconditions_for_rows_closed_by_the_canonical_owner_surface():
    packet_rows = {
        row["packet_requirement_id"]: row
        for row in _rows(REFERENCE_DIR / "hla1516_1_clause_6_om_detailed_reconciliation.csv")
    }

    expected = {
        "HLA1516.1-OM-6_2-ARG-003": "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_2-PRE-004": "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_2-EFF-005": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_2-EXC-006": "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_3-ARG-003": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_3-PRE-004": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_3-EXC-006": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_4-ARG-003": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_4-PRE-004": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_4-EFF-005": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_4-EXC-006": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_5-ARG-003": "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_5-PRE-004": "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_5-EFF-005": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_5-EXC-006": "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_6-ARG-003": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_6-PRE-004": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_6-EXC-006": "test_name_reservation_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_7-ARG-003": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_7-PRE-004": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_7-EFF-005": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_7-EXC-006": "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_8-PRE-004": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore",
        "HLA1516.1-OM-6_8-EFF-005": "test_two_python_federates_share_in_memory_rti",
        "HLA1516.1-OM-6_8-EXC-006": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore;tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_gates_registration_update_and_interaction_sends",
        "HLA1516.1-OM-6_9-ARG-003": "test_discovery_callback_validates_payload_context_and_wraps_callback_failures",
        "HLA1516.1-OM-6_9-PRE-004": "test_discovery_callback_validates_payload_context_and_wraps_callback_failures",
        "HLA1516.1-OM-6_9-EXC-006": "test_discovery_callback_validates_payload_context_and_wraps_callback_failures",
        "HLA1516.1-OM-6_10-EFF-005": "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions",
        "HLA1516.1-OM-6_10-PRE-004": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore",
        "HLA1516.1-OM-6_10-EXC-006": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore;tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_and_invalid_logical_time_guards_block_object_and_interaction_delivery",
        "HLA1516.1-OM-6_12-PRE-004": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time",
        "HLA1516.1-OM-6_14-PRE-004": "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_14-EFF-005": "test_delete_object_instance_notifies_known_federates_with_remove_object_instance;test_orphan_object_lifecycle_supports_late_discovery_local_delete_and_global_remove",
        "HLA1516.1-OM-6_14-EXC-006": "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_16-PRE-004": "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_16-EFF-005": "test_local_delete_clears_only_local_knowledge_and_object_can_be_rediscovered",
        "HLA1516.1-OM-6_16-EXC-006": "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_17-ARG-003": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_17-PRE-004": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_17-EXC-006": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_18-ARG-003": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_18-PRE-004": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_18-EXC-006": "test_attributes_in_scope_and_out_of_scope_callbacks_validate_payload_context_and_wrap_callback_failures",
        "HLA1516.1-OM-6_19-EXC-006": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_19-PRE-004": "test_clause_6_federate_initiated_services_validate_core_argument_shapes;test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore",
    }

    for requirement_id, current_test_id in expected.items():
        row = packet_rows[requirement_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == current_test_id
