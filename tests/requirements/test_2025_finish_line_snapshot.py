from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
    _discover_backend_plugin_records,
    build_spec2025_finish_line_markdown,
    build_spec2025_finish_line_snapshot,
    write_spec2025_finish_line,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements(
    "HLA2025-REQ-001",
    "HLA2025-TRACE-001",
    "HLA2025-TRACE-002",
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
    "HLA2025-MIL-004",
    "HLA2025-MIL-005",
    "HLA2025-MIL-006",
)
def test_2025_finish_line_snapshot_keeps_scope_counts_and_open_work_honest() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    assert snapshot["scope"] == "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim"
    assert snapshot["registry"]["initial_tranche_requirements"] == 28
    assert "hla-2025-executable-test-requirements-v3" in snapshot["registry"]["imported_packets"]

    executable = snapshot["executable_test_backlog"]
    assert executable["row_count"] == 1117
    assert executable["source_rows"] == 398
    assert executable["by_test_kind"]["surface_contract"] == 196
    assert executable["by_test_kind"]["validator_positive_fixture"] == 158
    assert executable["by_test_kind"]["validator_negative_fixture"] == 158
    depth = snapshot["requirement_depth_expansion"]
    assert depth["status"] == "imported-harmonization-candidate"
    assert depth["row_count"] == 691
    assert depth["row_count_from_csv"] == 691
    assert depth["by_area"]["Federate Interface service catalog"] == 196
    assert depth["by_area"]["SOM/FOM service-usage requirements"] == 196
    assert depth["by_area"]["OMT component-level conformance"] == 224
    assert depth["by_area"]["OMT validator-negative conformance"] == 29
    assert depth["by_delta_type"]["carry-forward"] == 328
    assert depth["by_delta_type"]["modified"] == 237
    assert depth["by_delta_type"]["new"] == 71
    assert depth["by_delta_type"]["retired"] == 24
    disposition = snapshot["requirement_coverage_disposition"]
    assert disposition["status"] == "repo-reconciled-disposition"
    assert disposition["row_count"] == 691
    assert disposition["row_count_from_csv"] == 691
    assert disposition["covered_row_count"] == 645
    assert disposition["by_disposition"] == {
        "duplicate/umbrella": 22,
        "covered": 645,
        "retired/legacy-only": 24,
    }
    assert disposition["by_priority"] == {"P0": 89, "P1": 430, "P2": 172}
    assert disposition["by_closure_wave"]["1-fi-service-and-binding-disposition"] == 208
    assert disposition["by_closure_wave"]["2-omt-field-and-validator-fixtures"] == 253
    assert disposition["fi_binding_surface"]["fi_rows"] == 196
    assert disposition["fi_binding_surface"]["java_present"] == 196
    assert disposition["fi_binding_surface"]["cpp_present"] == 196
    assert disposition["fi_binding_surface"]["fedpro_route_boundary_or_missing_review"] == 4

    backlog = snapshot["completion_backlog"]
    assert backlog["by_bucket"]["new-2025-requirements"] == 7
    assert backlog["by_current_status"]["implemented-slice"] >= 20
    assert backlog["by_current_status"].get("partial", 0) == 0
    assert "planned" not in backlog["by_current_status"]
    assert backlog["by_current_status"].get("unsupported-boundary", 0) == 0
    assert backlog["by_current_status"]["legacy-only"] == 1
    assert backlog["high_priority_open_count"] == 0

    open_ids = {row["id"] for row in backlog["high_priority_open"]}
    assert not open_ids
    for row_id in (
        "HLA2025-BLG-001",
        "HLA2025-BLG-002",
        "HLA2025-BND-001",
        "HLA2025-BND-002",
        "HLA2025-BND-003",
        "HLA2025-MOD-005",
        "HLA2025-MOD-007",
        "HLA2025-MOD-009",
        "HLA2025-MOD-010",
        "HLA2025-NEW-004",
        "HLA2025-NEW-007",
        "HLA2025-RET-003",
    ):
        assert row_id not in open_ids
    assert "HLA2025-NEW-001" not in open_ids
    assert "HLA2025-NEW-002" not in open_ids
    assert "HLA2025-NEW-005" not in open_ids
    assert "HLA2025-NEW-006" not in open_ids
    assert "HLA2025-MOD-004" not in open_ids
    assert "HLA2025-MOD-008" not in open_ids
    assert "HLA2025-RET-001" not in open_ids
    assert "HLA2025-MOD-002" not in open_ids
    assert "HLA2025-MOD-003" not in open_ids
    assert "HLA2025-MOD-006" not in open_ids

    matrix = snapshot["verification_matrix"]
    assert matrix["row_count"] == backlog["row_count"]
    assert matrix["high_priority_missing_anchor_count"] == 0
    assert matrix["high_priority_missing_anchors"] == []
    pytest_anchor_audit = snapshot["requirement_pytest_anchor_audit"]
    assert pytest_anchor_audit["row_count"] == 718
    assert pytest_anchor_audit["anchored_requirement_count"] == 718
    assert "direct pytest-function anchors" in pytest_anchor_audit["current_assessment"]
    pytest_rows = {row["requirement_id"]: row for row in pytest_anchor_audit["rows"]}
    fi_single_anchor_rows = [
        row["requirement_id"]
        for row in pytest_anchor_audit["rows"]
        if row["requirement_id"].startswith("HLA2025-FI-")
        and not row["requirement_id"].startswith("HLA2025-FI-CB-")
        and row["pytest_anchor_count"] == 1
    ]
    assert fi_single_anchor_rows == []
    callback_single_anchor_rows = [
        row["requirement_id"]
        for row in pytest_anchor_audit["rows"]
        if row["requirement_id"].startswith("HLA2025-FI-CB-")
        and row["pytest_anchor_count"] == 1
    ]
    assert callback_single_anchor_rows == ["HLA2025-FI-CB-005", "HLA2025-FI-CB-008"]
    for prefix in ("HLA2025-BND-", "HLA2025-MOD-", "HLA2025-NEW-", "HLA2025-FR-"):
        single_anchor_rows = [
            row["requirement_id"]
            for row in pytest_anchor_audit["rows"]
            if row["requirement_id"].startswith(prefix) and row["pytest_anchor_count"] == 1
        ]
        assert single_anchor_rows == []
    assert pytest_rows["HLA2025-FI-SVC-001"]["pytest_anchor_count"] == 2
    assert any("test_2025_provider_is_first_green_runtime_path" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchor_count"] == 10
    assert any("test_2025_provider_rejects_duplicate_federation_and_federate_names" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_directed_ddm_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_disconnected_peer_callback_backlog_before_reconnect_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchor_count"] == 6
    assert any("test_2025_provider_routes_mom_synchronization_point_reports_through_interactions" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_fans_out_mom_sync_status_reports_only_to_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-035"]["pytest_anchor_count"] == 3
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-035"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-035"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchor_count"] >= 9
    assert any("test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_transport_and_ownership_actions_to_observable_runtime_effects_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restores_cross_federate_attribute_owner_visibility"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-100"]["pytest_anchor_count"] == 3
    assert any("test_2025_provider_applies_resign_time_ownership_policies" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-100"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-048"]["pytest_anchor_count"] == 2
    assert any("test_start_and_stop_registration_callbacks_are_delivered" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-048"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-050"]["pytest_anchor_count"] == 4
    assert any("test_turn_interactions_on_and_off_callbacks_are_delivered" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-050"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-050"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_attribute_scope_advisories_only_to_overlapping_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-050"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchor_count"] >= 7
    assert any("test_2025_provider_routes_mom_time_management_service_interactions" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"])
    assert any("test_2025_provider_uses_selected_logical_time_factory_for_queries_and_grants" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchor_count"] >= 14
    assert any("test_2025_provider_queues_timestamped_messages_and_supports_retraction" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_reports_lits_from_queued_tso_for_target_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_retracts_partially_delivered_tso_without_releasing_lagging_targets_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_retraction_callbacks_for_disconnected_delivered_targets_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchor_count"] >= 10
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_reports_lits_from_queued_tso_for_target_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchor_count"] >= 7
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_reflect_and_interaction_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_delivers_timestamped_updates_and_interactions_to_all_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_queued_plain_tso_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"]
    )

    hosted_shared = snapshot["hosted_shared_scenario_coverage_audit"]
    assert hosted_shared["audit_status"] == "hosted-shared-fedpro-scenarios-accounted-for"
    assert hosted_shared["shared_scenario_count"] == 36
    assert hosted_shared["represented_in_conformance_evidence_count"] == 36
    assert hosted_shared["zero_count_shared_scenarios"] == []
    assert hosted_shared["ready_for_full_shared_scenario_representation_claim"] is True
    assert "Every shared hosted FedPro 2025 scenario is now represented" in hosted_shared["current_assessment"]
    assert any(
        "test_2025_transport_server_holds_tso_for_lagging_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-058"]["pytest_anchor_count"] >= 2
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-058"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-059"]["pytest_anchor_count"] >= 2
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-059"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchor_count"] >= 13
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"])
    assert any(
        "test_2025_provider_restore_recovers_plain_interaction_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_reflect_and_interaction_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_delivers_timestamped_updates_and_interactions_to_all_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_local_delete_to_requester_local_known_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_queued_plain_tso_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_reports_lits_from_queued_tso_for_target_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_holds_tso_for_lagging_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_retracts_partially_delivered_tso_without_releasing_lagging_targets_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchor_count"] >= 4
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_delete_remove_only_to_discovered_observers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchor_count"] >= 4
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_delete_remove_only_to_discovered_observers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchor_count"] >= 13
    assert any("test_2025_provider_implements_fom_backed_ddm_lookup_and_default_attribute_policy" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"])
    assert any("test_2025_provider_filters_object_reflections_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-128"]["pytest_anchor_count"] == 6
    assert any("test_clause_9_services_are_observable_through_mom_service_invocation_reporting" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-128"]["pytest_anchors"])
    assert any(
        "test_2025_primary_python_rti_runs_ddm_passive_region_subscription_scenario_without_wrapper_adapter"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-128"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchor_count"] == 11
    assert any("test_2025_provider_filters_interactions_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"])
    assert any("test_2025_provider_filters_directed_interactions_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"])
    assert any(
        "test_2025_primary_python_rti_runs_ddm_object_region_lifecycle_scenario_without_wrapper_adapter"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"]
    )
    assert any(
        "test_2025_primary_python_rti_runs_ddm_declaration_gating_scenario_without_wrapper_adapter"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_plain_interaction_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-137"]["pytest_anchor_count"] == 6
    assert any("test_clause_9_services_are_observable_through_mom_service_invocation_reporting" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-137"]["pytest_anchors"])
    assert any(
        "test_2025_primary_python_rti_runs_ddm_passive_region_subscription_scenario_without_wrapper_adapter"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-137"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchor_count"] == 8
    assert any("test_support_lookups_round_trip_class_handle_and_name" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"])
    assert any(
        "test_2025_primary_python_rti_runs_ddm_passive_region_subscription_scenario_without_wrapper_adapter"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_keeps_decode_support_helpers_available_while_joined_identity_queries_stop_after_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchor_count"] == 5
    assert any("test_support_dimension_and_update_rate_helpers" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"])
    assert any(
        "test_2025_provider_accepts_support_lookup_aliases_and_rejects_invalid_values"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_rejects_invalid_support_lookup_values_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_keeps_decode_support_helpers_available_while_joined_identity_queries_stop_after_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-162"]["pytest_anchor_count"] == 2
    assert any("test_2025_provider_implements_fom_backed_ddm_lookup_and_default_attribute_policy" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-162"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchor_count"] == 4
    assert any("test_2025_provider_normalizes_typed_handles_and_rejects_wrong_handle_family" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-OMT-COMP-001"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-223"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-223"]["pytest_anchors"])
    for requirement_id in (
        "HLA2025-OMT-COMP-011",
        "HLA2025-OMT-COMP-012",
        "HLA2025-OMT-COMP-014",
        "HLA2025-OMT-COMP-015",
        "HLA2025-OMT-COMP-017",
        "HLA2025-OMT-COMP-018",
    ):
        assert pytest_rows[requirement_id]["pytest_anchor_count"] == 1
        assert any("test_2025_attribute_metadata_round_trips" in anchor for anchor in pytest_rows[requirement_id]["pytest_anchors"])
    for requirement_id in (
        "HLA2025-OMT-COMP-037",
        "HLA2025-OMT-COMP-038",
        "HLA2025-OMT-COMP-040",
        "HLA2025-OMT-COMP-043",
        "HLA2025-OMT-COMP-044",
    ):
        assert pytest_rows[requirement_id]["pytest_anchor_count"] == 1
        assert any(
            "test_2025_dimension_specific_children_round_trip" in anchor
            for anchor in pytest_rows[requirement_id]["pytest_anchors"]
        )
    assert pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchor_count"] == 1
    assert any("test_dimension_metadata_round_trips_through_parser_and_serializer" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-200"]["pytest_anchor_count"] == 2
    assert any("test_2025_parser_intentionally_narrows_unmodeled_omt_fields" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-200"]["pytest_anchors"])
    assert any("test_2025_transportation_and_update_rate_metadata_round_trips" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-200"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-201"]["pytest_anchor_count"] == 2
    assert any("test_2025_transportation_and_update_rate_metadata_round_trips" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-201"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-207"]["pytest_anchor_count"] == 1
    assert any("test_2025_transportation_and_update_rate_metadata_round_trips" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-207"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-SU-001"]["pytest_anchor_count"] == 1
    assert any(
        "test_2025_renumbered_service_utilization_rows_preserve_behavior_and_update_references" in anchor
        for anchor in pytest_rows["HLA2025-OMT-SU-001"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-OMT-SU-196"]["pytest_anchor_count"] == 1
    assert any(
        "test_2025_renumbered_service_utilization_rows_preserve_behavior_and_update_references" in anchor
        for anchor in pytest_rows["HLA2025-OMT-SU-196"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchor_count"] == 4
    assert any("test_2025_parser_accepts_isolates_and_preserves_foreign_namespace_extension_points" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchors"])
    assert any("test_omt_xs_any_markdown_keeps_bounded_payload_preservation_claim_explicit" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchors"])
    assert any("test_harmonization_packets_keep_xs_any_rows_on_bounded_omt_tolerance_evidence" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchors"])
    assert any("test_omt_xs_any_bounded_proof_doc_enumerates_all_tracked_rows" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchors"])
    for row_id in (
        "HLA2025-OMT-COMP-166",
        "HLA2025-OMT-COMP-168",
        "HLA2025-OMT-COMP-169",
        "HLA2025-OMT-COMP-170",
    ):
        assert pytest_rows[row_id]["pytest_anchor_count"] == 1
        assert any(
            "test_2025_parser_round_trips_additional_switch_metadata" in anchor
            for anchor in pytest_rows[row_id]["pytest_anchors"]
        )
    assert pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchor_count"] == 4
    assert any("test_2025_parser_accepts_isolates_and_preserves_foreign_namespace_extension_points" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchors"])
    assert any("test_omt_xs_any_markdown_keeps_bounded_payload_preservation_claim_explicit" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchors"])
    assert any("test_harmonization_packets_keep_xs_any_rows_on_bounded_omt_tolerance_evidence" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchors"])
    assert any("test_omt_xs_any_bounded_proof_doc_enumerates_all_tracked_rows" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchor_count"] >= 48
    assert any("test_2025_provider_runs_federation_save_restore_lifecycle" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"])
    assert any(
        "test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_time_and_switch_control_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_per_federate_time_state_and_flush_grant_targeting_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_callback_delivery_policy"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_plain_object_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_plain_interaction_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_inflight_ownership_state"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restores_cross_federate_attribute_owner_visibility"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_provider_restore_recovers_directed_ddm_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-007"]["pytest_anchor_count"] == 2
    assert any("test_each_proto2025_2025_scenario_fom_set_merges_with_standard_mim" in anchor for anchor in pytest_rows["HLA2025-FI-007"]["pytest_anchors"])
    assert any("test_proto2025_2025_example_foms_drive_two_federate_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-007"]["pytest_anchors"])
    assert pytest_rows["HLA2025-BND-001"]["pytest_anchor_count"] == 6
    assert any("test_standard_2025_routes_pass_runtime_capability_when_built" in anchor for anchor in pytest_rows["HLA2025-BND-001"]["pytest_anchors"])
    assert any("test_standard_binding_runtime_capability_markdown_keeps_bounded_binding_claim_explicit" in anchor for anchor in pytest_rows["HLA2025-BND-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-BND-002"]["pytest_anchor_count"] == 6
    assert any("test_standard_2025_routes_pass_runtime_capability_when_built" in anchor for anchor in pytest_rows["HLA2025-BND-002"]["pytest_anchors"])
    assert any("test_standard_binding_runtime_capability_markdown_keeps_bounded_binding_claim_explicit" in anchor for anchor in pytest_rows["HLA2025-BND-002"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-001"]["pytest_anchor_count"] == 2
    assert any("test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms" in anchor for anchor in pytest_rows["HLA2025-MOD-001"]["pytest_anchors"])
    assert any("test_2025_provider_validates_callback_model_and_credentials_at_connect" in anchor for anchor in pytest_rows["HLA2025-MOD-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-003"]["pytest_anchor_count"] == 4
    assert any("test_2025_provider_distinguishes_fom_mim_open_read_invalid_and_merge_errors" in anchor for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"])
    assert any("test_2025_provider_rejects_invalid_join_fom_modules_and_destroy_while_joined" in anchor for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_create_with_mim_requests_over_fedpro_schema" in anchor
        for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_distinguishes_fom_mim_open_read_invalid_and_merge_errors_over_fedpro_schema" in anchor
        for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-MOD-004"]["pytest_anchor_count"] == 2
    assert any("test_2025_callback_surface_uses_direct_context_parameters_not_supplemental_helpers" in anchor for anchor in pytest_rows["HLA2025-MOD-004"]["pytest_anchors"])
    assert any("test_2025_provider_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-MOD-004"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-009"]["pytest_anchor_count"] == 2
    assert any("test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms" in anchor for anchor in pytest_rows["HLA2025-MOD-009"]["pytest_anchors"])
    assert any("test_2025_provider_validates_callback_model_and_credentials_at_connect" in anchor for anchor in pytest_rows["HLA2025-MOD-009"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-010"]["pytest_anchor_count"] == 4
    assert any("test_2025_parser_round_trips_logical_time_xml_names" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert any("test_2025_parser_round_trips_metadata_switches_transport_and_time_subset" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert pytest_rows["HLA2025-NEW-002"]["pytest_anchor_count"] == 5
    assert any("test_2025_provider_reports_federation_executions_and_members" in anchor for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"])
    assert any(
        "test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"]
    )
    assert any("test_2025_transport_server_decodes_extended_callback_routes_over_fedpro_schema" in anchor for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_isolates_requester_and_disabled_callbacks_per_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-NEW-003"]["pytest_anchor_count"] == 4
    assert any("test_2025_provider_reports_federate_resigned_callback_with_reason_context" in anchor for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"])
    assert any(
        "test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"]
    )
    assert any("test_2025_transport_server_decodes_extended_callback_routes_over_fedpro_schema" in anchor for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-NEW-005"]["pytest_anchor_count"] == 4
    assert any("test_2025_provider_normalizes_typed_handles_and_rejects_wrong_handle_family" in anchor for anchor in pytest_rows["HLA2025-NEW-005"]["pytest_anchors"])
    assert any("test_2025_transport_server_round_trips_support_services_over_fedpro_schema" in anchor for anchor in pytest_rows["HLA2025-NEW-005"]["pytest_anchors"])
    assert pytest_rows["HLA2025-NEW-007"]["pytest_anchor_count"] >= 10
    assert pytest_rows["HLA2025-BND-003"]["pytest_anchor_count"] >= 230
    assert any(
        "test_2025_transport_client_explicitly_registers_single_fom_create_commands" in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_client_explicitly_registers_federation_list_commands" in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_single_fom_create_request_variants_over_fedpro_schema" in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_orders_timestamped_interactions_across_two_federates_over_fedpro_schema" in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_time_control_actions_to_named_federate_runtime_effects_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_exception_reporting_adjust_to_targeted_switch_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_exception_reports_only_to_federates_with_reporting_enabled_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_rejects_invalid_support_lookup_values_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_isolates_requester_and_disabled_callbacks_per_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_retraction_callbacks_for_disconnected_delivered_targets_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_pending_ownership_requester_after_disconnect_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_attribute_value_update_requests_for_disconnected_owner_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_releases_owned_attributes_when_owner_disconnects_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_clears_offered_ownership_state_when_owner_disconnects_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_per_federate_time_state_and_flush_grant_targeting_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_fans_out_mom_sync_status_reports_only_to_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_save_restore_completion_callbacks_only_to_reporting_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_mom_delete_remove_only_to_discovered_observers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_removes_disconnected_directed_ddm_subscriber_from_delivery_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_queued_directed_tso_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_queued_plain_tso_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_attribute_ownership_query_callbacks_only_to_requester_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_attribute_value_update_requests_only_to_owner_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_isolates_name_reservation_callbacks_per_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_reflect_and_interaction_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_delivers_timestamped_updates_and_interactions_to_all_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_fans_out_post_delivery_retraction_to_all_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_directed_interactions_only_to_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_delivers_and_retracts_timestamped_directed_interactions_for_all_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_time_and_switch_control_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_proves_time_window_core_progression_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_ignores_receive_order_poison_after_window_close_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-BND-003"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-OMT-002"]["pytest_anchor_count"] >= 6
    unanchored_audit = snapshot["unanchored_requirement_audit"]
    assert unanchored_audit["row_count"] == 0
    assert unanchored_audit["by_family"] == {}
    assert "broader evidence-slice ledgers and direct requirement markers are aligned" in unanchored_audit["current_assessment"]
    assert unanchored_audit["sample_requirement_ids"] == []
    route_matrix = snapshot["route_parity_matrix"]
    assert route_matrix["scenario_count"] >= 8
    assert "python-2025-fedpro-grpc" in route_matrix["routes"]
    assert route_matrix["by_route"]["java-standard-2025-jpype"]["parity-covered"] == 8
    assert route_matrix["by_route"]["cpp-standard-2025-grpc"]["parity-covered"] == 8
    route_rows = {(row["scenario"], row["route"]): row for row in route_matrix["rows"]}
    for route in ("python-2025-inprocess", "python-2025-fedpro-grpc"):
        for scenario in {row["scenario"] for row in route_matrix["rows"] if row["route"] == route}:
            row = route_rows[(scenario, route)]
            assert row["runtime_provider"] == "python2025"
            assert row["implementation_lane"] == "hla-backend-python2025"
            assert row["counts_as_python_2025_rti"] is True
            assert row["wrapper_only"] is False
    assert "lookahead query/modify" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "GALT/LITS/logical-time queries" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "time-window core, output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "oracle-rejection guards" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "bounded logical time/GALT/LITS/lookahead query evidence" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of the package-owned shared Target/Radar example scenario plus the package-owned future-exclusion, output-delivery, consumer-order, integrated lookahead-processing-window gauntlet, and restore-state scenario adapter paths" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of MOM federation-management save/restore service interactions plus MOM time-management service interactions through the direct 2025 ambassador surface" in route_rows[("mom", "python-2025-fedpro-grpc")]["notes"]
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of the shared support factory/decode scenario plus automatic-resign get/set, multiple-name reservation callbacks, object-instance name lookup, and queued reflection release on re-enabled callbacks" in route_rows[("support_services", "python-2025-fedpro-grpc")]["notes"]
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert "snake-case alias acceptance on the primary direct-runtime surface" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python2025 lane" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "oracle-rejection guards" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    fi_service_audit = snapshot["fi_service_proof_audit"]
    assert fi_service_audit["row_count"] == 196
    assert fi_service_audit["fully_traceable_service_count"] == 196
    assert fi_service_audit["ready_for_per_service_runtime_traceability_claim"] is True
    assert fi_service_audit["ready_for_full_fi_service_conformance_claim"] is False
    assert fi_service_audit["by_family"] == {
        "callback_control": 4,
        "ddm": 12,
        "declaration_management": 12,
        "federation_management": 17,
        "name_reservation": 6,
        "object_class_relevance": 4,
        "object_management": 26,
        "ownership_management": 18,
        "save_restore": 17,
        "support_services": 55,
        "time_management": 25,
    }
    assert "runtime evidence rows" in fi_service_audit["current_assessment"]
    fi_rows = {row["requirement_id"]: row for row in fi_service_audit["rows"]}
    assert fi_rows["HLA2025-FI-SVC-001"]["family"] == "federation_management"
    assert "2025-connect-and-federation-catalog-services" in fi_rows["HLA2025-FI-SVC-001"]["supporting_slice_ids"]
    assert "tests/test_rti1516_2025_python2025_runtime.py" in fi_rows["HLA2025-FI-SVC-001"]["evidence_tests"]
    assert fi_rows["HLA2025-FI-SVC-018"]["family"] == "save_restore"
    assert "2025-save-restore-lifecycle" in fi_rows["HLA2025-FI-SVC-018"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-057"]["family"] == "object_management"
    assert "2025-basic-object-exchange" in fi_rows["HLA2025-FI-SVC-057"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-083"]["family"] == "ownership_management"
    assert "2025-ownership-divestiture-confirmation-flows" in fi_rows["HLA2025-FI-SVC-083"]["supporting_slice_ids"]
    assert "2025-ownership-release-and-if-wanted-flows" in fi_rows["HLA2025-FI-SVC-092"]["supporting_slice_ids"]
    assert "2025-ownership-acquisition-assumption-flows" in fi_rows["HLA2025-FI-SVC-089"]["supporting_slice_ids"]
    assert "2025-ownership-acquisition-availability-cancellation-flows" in fi_rows["HLA2025-FI-SVC-090"]["supporting_slice_ids"]
    assert "2025-ownership-query-and-resign-policies" in fi_rows["HLA2025-FI-SVC-098"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-112"]["family"] == "time_management"
    assert "2025-time-grant-and-async-delivery" in fi_rows["HLA2025-FI-SVC-112"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-126"]["family"] == "ddm"
    assert "2025-ddm-default-attribute-policy" in fi_rows["HLA2025-FI-SVC-126"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-138"]["family"] == "support_services"
    assert "2025-support-federate-and-object-identity-lookups" in fi_rows["HLA2025-FI-SVC-138"]["supporting_slice_ids"]
    assert "2025-support-attribute-interaction-catalog-lookups" in fi_rows["HLA2025-FI-SVC-145"]["supporting_slice_ids"]
    assert "2025-support-handle-normalization-and-region-introspection" in fi_rows["HLA2025-FI-SVC-162"]["supporting_slice_ids"]
    assert "2025-support-advisory-and-reporting-state-inquiries" in fi_rows["HLA2025-FI-SVC-170"]["supporting_slice_ids"]
    assert "2025-support-advisory-and-reporting-state-controls" in fi_rows["HLA2025-FI-SVC-171"]["supporting_slice_ids"]
    assert fi_rows["HLA2025-FI-SVC-193"]["family"] == "callback_control"
    assert "2025-callback-control-services" in fi_rows["HLA2025-FI-SVC-193"]["supporting_slice_ids"]
    delta_audit = snapshot["delta_requirement_proof_audit"]
    assert delta_audit["row_count"] == 20
    assert delta_audit["fully_traceable_requirement_count"] == 20
    assert delta_audit["ready_for_delta_traceability_claim"] is True
    assert delta_audit["ready_for_full_delta_conformance_claim"] is False
    assert delta_audit["by_category"] == {
        "modified-existing": 10,
        "new-2025-requirement": 7,
        "retired-mapped-2010": 3,
    }
    delta_rows = {row["requirement_id"]: row for row in delta_audit["rows"]}
    assert "2025-auth-connect" in delta_rows["HLA2025-MOD-001"]["supporting_slice_ids"]
    assert "2025-fom-mim-error-taxonomy" in delta_rows["HLA2025-MOD-002"]["supporting_slice_ids"]
    assert {
        "2025-callback-context-object-delivery",
        "2025-callback-context-interaction-delivery",
    } <= set(delta_rows["HLA2025-MOD-004"]["supporting_slice_ids"])
    assert "2025-lookahead-window-proofs" in delta_rows["HLA2025-MOD-006"]["supporting_slice_ids"]
    assert "2025-switch-set-get-model" in delta_rows["HLA2025-MOD-008"]["supporting_slice_ids"]
    assert "2025-retired-advisory-switch-enable-disable-mapping" in delta_rows["HLA2025-RET-001"]["supporting_slice_ids"]
    assert "2025-directed-interaction-boundary" in delta_rows["HLA2025-NEW-001"]["supporting_slice_ids"]
    assert "2025-lifecycle-and-members" in delta_rows["HLA2025-NEW-002"]["supporting_slice_ids"]
    assert "2025-omt-reference-value-required" in delta_rows["HLA2025-NEW-006"]["supporting_slice_ids"]
    assert "2025-wsdl-legacy-only" in delta_rows["HLA2025-RET-003"]["supporting_slice_ids"]
    binding_audit = snapshot["binding_requirement_proof_audit"]
    assert binding_audit["row_count"] == 3
    assert binding_audit["fully_traceable_requirement_count"] == 3
    assert binding_audit["ready_for_binding_traceability_claim"] is True
    assert binding_audit["ready_for_full_binding_conformance_claim"] is False
    assert "adapter or transport seam evidence boundaries over the main hla-backend-python2025 runtime" in binding_audit["current_assessment"]
    assert "not alternate ownership lanes for core 2025 RTI semantics" in binding_audit["current_assessment"]
    binding_rows = {row["requirement_id"]: row for row in binding_audit["rows"]}
    assert set(binding_rows["HLA2025-BND-001"]["routes"]) == {"java-standard-2025-jpype", "java-standard-2025-py4j"}
    assert binding_rows["HLA2025-BND-001"]["route_parity_counts"]["parity-covered"] == 16
    assert "2025-java-binding-source-trace" in binding_rows["HLA2025-BND-001"]["supporting_slice_ids"]
    assert set(binding_rows["HLA2025-BND-002"]["routes"]) == {"cpp-standard-2025-pybind", "cpp-standard-2025-grpc"}
    assert binding_rows["HLA2025-BND-002"]["route_parity_counts"]["parity-covered"] == 16
    assert "2025-cpp-binding-source-trace" in binding_rows["HLA2025-BND-002"]["supporting_slice_ids"]
    assert binding_rows["HLA2025-BND-003"]["routes"] == ["python-2025-fedpro-grpc"]
    assert binding_rows["HLA2025-BND-003"]["route_parity_counts"]["parity-covered"] == 8
    assert "2025-fedpro-typed-transport-surface" in binding_rows["HLA2025-BND-003"]["supporting_slice_ids"]
    assert "2025-fedpro-hosted-runtime-core" in binding_rows["HLA2025-BND-003"]["supporting_slice_ids"]
    assert "2025-fedpro-hosted-runtime-extended-state" in binding_rows["HLA2025-BND-003"]["supporting_slice_ids"]
    omt_audit = snapshot["omt_requirement_proof_audit"]
    assert omt_audit["row_count"] == 454
    assert omt_audit["traceable_requirement_count"] == 454
    assert omt_audit["ready_for_omt_traceability_claim"] is True
    assert omt_audit["ready_for_full_omt_conformance_claim"] is False
    assert omt_audit["by_category"] == {
        "component": 224,
        "core-omt": 5,
        "service-utilization": 196,
        "validator-negative": 29,
    }
    assert omt_audit["by_proof_status"] == {
        "supported-subset-traceable": 454,
    }
    assert "foreign xs:any extension tolerance" in omt_audit["current_assessment"]
    omt_pytest_rows = [
        row
        for row in pytest_anchor_audit["rows"]
        if row["requirement_id"].startswith(("HLA2025-OMT-", "HLA2025-OMT-COMP-", "HLA2025-OMT-CV-", "HLA2025-OMT-SU-"))
    ]
    assert len(omt_pytest_rows) == omt_audit["row_count"]
    omt_single_anchor_rows = [row["requirement_id"] for row in omt_pytest_rows if row["pytest_anchor_count"] == 1]
    omt_multi_anchor_rows = [row["requirement_id"] for row in omt_pytest_rows if row["pytest_anchor_count"] > 1]
    assert len(omt_single_anchor_rows) == 444
    assert sorted(omt_multi_anchor_rows) == [
        "HLA2025-OMT-001",
        "HLA2025-OMT-002",
        "HLA2025-OMT-005",
        "HLA2025-OMT-006",
        "HLA2025-OMT-007",
        "HLA2025-OMT-COMP-006",
        "HLA2025-OMT-COMP-039",
        "HLA2025-OMT-COMP-200",
        "HLA2025-OMT-COMP-201",
        "HLA2025-OMT-COMP-224",
    ]
    omt_rows = {row["requirement_id"]: row for row in omt_audit["rows"]}
    assert omt_rows["HLA2025-OMT-001"]["proof_status"] == "supported-subset-traceable"
    assert "2025-fom-validation" in omt_rows["HLA2025-OMT-001"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-002"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-reference-value-required" in omt_rows["HLA2025-OMT-002"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-004"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-component-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-004"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-037"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-dimension-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-037"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-041"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-dimension-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-041"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-048"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-association-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-048"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-075"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-association-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-075"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-110"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-association-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-110"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-006"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-xs-any-extension-tolerance" in omt_rows["HLA2025-OMT-COMP-006"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-CV-001"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-schema-constraint-validation" in omt_rows["HLA2025-OMT-CV-001"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-SU-001"]["proof_status"] == "supported-subset-traceable"
    assert "2025-service-utilization-crosscheck" in omt_rows["HLA2025-OMT-SU-001"]["supporting_slice_ids"]
    milestone_audit = snapshot["python_rti_milestone_audit"]
    assert milestone_audit["audit_status"] == "bounded-python-rti-milestones"
    assert milestone_audit["milestone_count"] == 6
    assert milestone_audit["row_count"] == 12
    assert milestone_audit["routes"] == ["python-2025-inprocess", "python-2025-fedpro-grpc"]
    assert "bounded-evidence milestones" in milestone_audit["current_assessment"]
    assert "negative-oracle rejection guards" in milestone_audit["current_assessment"]
    assert milestone_audit["by_route"]["python-2025-inprocess"]["milestone_count"] == 6
    assert milestone_audit["by_route"]["python-2025-fedpro-grpc"]["milestone_count"] == 6
    assert milestone_audit["by_route"]["python-2025-inprocess"]["all_route_parity_covered"] is True
    assert milestone_audit["by_route"]["python-2025-fedpro-grpc"]["all_route_parity_covered"] is True
    assert milestone_audit["by_route"]["python-2025-inprocess"]["status_counts"] == {
        "bounded-lookahead-evidence": 1,
        "bounded-query-evidence": 1,
        "bounded-working-slice": 1,
        "covered-routing-slice": 1,
        "covered-scenario-slice": 1,
        "covered-time-advance-slice": 1,
    }
    milestone_rows = {(row["route"], row["milestone_id"]): row for row in milestone_audit["rows"]}
    assert {row["milestone_id"] for row in milestone_audit["rows"]} == {
        "best_attempt_working_surface",
        "example_fom_scenarios",
        "messaging_and_routing",
        "time_sync_and_advances",
        "galt_lits_queries",
        "lookahead_windows",
    }
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["status"] == "bounded-working-slice"
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["milestone_label"] == (
        "Best-attempt Python RTI 2025 working surface"
    )
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["scenario_count"] == 8
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_parity_statuses"] == {"parity-covered": 8}
    assert "best-attempt bounded working surface" in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["summary"]
    assert "full-fledged RTI" in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["boundary"]
    assert "Current Python 2025 RTI covers connect, create, createFederationExecutionWithMIM, join, resign, destroy, disconnect, evoked callback polling, and direct inline immediate callback delivery." in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_notes"]
    assert "Current Python 2025 RTI covers logical-time factories, regulation/constrained mode, lookahead query/modify, advance and flush grants, queued TSO delivery, GALT/LITS/logical-time queries" in " ".join(milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_notes"])
    assert "save-restore lookahead rollback with queued-TSO redelivery" in " ".join(milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_notes"])
    assert "MOM switch/report serialization slices" in " ".join(milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_notes"])
    assert milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["status"] == "covered-scenario-slice"
    assert "tracked FOM-backed runtime scenarios" in milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["summary"]
    assert tuple(milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["supporting_scenarios"]) == (
        "object_exchange",
        "save_restore",
        "mom",
    )
    assert "2025-fom-showcase" in milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["supporting_slice_ids"]
    assert milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["boundary"] == (
        "This is scenario-suite evidence, not a universal claim for every possible FOM composition."
    )
    assert milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["status"] == "covered-routing-slice"
    assert "typed transport surface" in milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["summary"]
    assert tuple(milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["supporting_scenarios"]) == (
        "object_exchange",
        "ddm",
        "mom",
    )
    assert "2025-directed-interaction-boundary" in milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["supporting_slice_ids"]
    assert "2025-ddm-default-attribute-policy" in milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["supporting_slice_ids"]
    assert milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["status"] == "covered-time-advance-slice"
    assert "restore rollback of logical time" in milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["summary"]
    assert tuple(milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["supporting_scenarios"]) == (
        "time_management",
        "save_restore",
    )
    assert "2025-time-advance-request-modes" in milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["supporting_slice_ids"]
    assert "2025-save-restore-lifecycle" in milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["supporting_slice_ids"]
    assert milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["status"] == "bounded-query-evidence"
    assert "not strong enough to claim a fully proven or universally correct GALT/LITS algorithm" in milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["boundary"]
    assert "negative-oracle guards rejecting mismatched LITS boundaries" in milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["summary"]
    assert "lookahead query/modify, advance and flush grants, queued TSO delivery, GALT/LITS/logical-time queries" in " ".join(
        milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["route_notes"]
    )
    assert "future-exclusion proof" in milestone_rows[("python-2025-fedpro-grpc", "galt_lits_queries")]["summary"]
    assert "negative-oracle guards rejecting mismatched LITS boundaries" in milestone_rows[("python-2025-fedpro-grpc", "galt_lits_queries")]["summary"]
    assert milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["status"] == "bounded-lookahead-evidence"
    assert "future-message exclusion" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["boundary"]
    assert "output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["summary"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["summary"]
    assert "negative-oracle guards" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["summary"]
    assert tuple(milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["supporting_scenarios"]) == (
        "time_management",
    )
    assert "2025-lookahead-window-proofs" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["supporting_slice_ids"]
    assert "tests/test_rti1516_2025_python2025_runtime.py" in milestone_rows[("python-2025-inprocess", "lookahead_windows")]["evidence_tests"]
    assert "tests/scenarios/test_python_route_parity.py" in milestone_rows[("python-2025-inprocess", "lookahead_windows")]["evidence_tests"]
    assert "tests/transport/test_grpc_transport_2025.py" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["evidence_tests"]
    assert "tests/scenarios/test_python_route_parity.py" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["evidence_tests"]
    assert pytest_rows["HLA2025-OMT-001"]["pytest_anchor_count"] == 5
    assert pytest_rows["HLA2025-OMT-002"]["pytest_anchor_count"] >= 6
    assert pytest_rows["HLA2025-OMT-005"]["pytest_anchor_count"] == 4
    assert pytest_rows["HLA2025-OMT-006"]["pytest_anchor_count"] == 10
    assert pytest_rows["HLA2025-OMT-007"]["pytest_anchor_count"] >= 8
    assert pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchor_count"] == 1
    assert pytest_rows["HLA2025-OMT-COMP-004"]["pytest_anchor_count"] == 1
    assert pytest_rows["HLA2025-OMT-COMP-037"]["pytest_anchor_count"] == 1
    assert pytest_rows["HLA2025-OMT-CV-001"]["pytest_anchor_count"] == 1
    assert pytest_rows["HLA2025-OMT-SU-001"]["pytest_anchor_count"] == 1
    claim_audit = snapshot["completion_claim_audit"]
    assert claim_audit["claim_shape"] == "bounded-working-surface-with-explicit-boundaries"
    assert claim_audit["ready_for_supported-boundary_statement"] is True
    assert claim_audit["ready_for_full_2025_conformance_claim"] is False
    assert claim_audit["requirement_universe"] == {
        "total_rows": 691,
        "covered_rows": 645,
        "unsupported_boundary_rows": 0,
        "retired_or_legacy_only_rows": 24,
        "duplicate_or_umbrella_rows": 22,
    }
    assert claim_audit["backlog_closure"] == {
        "row_count": 33,
        "implemented_slice_rows": 32,
        "legacy_only_rows": 1,
        "high_priority_open_count": 0,
        "fully_closed": True,
    }
    assert claim_audit["traceability_ledgers"] == {
        "fi_service_rows": 196,
        "delta_rows": 20,
        "binding_rows": 3,
        "omt_rows": 454,
    }
    assert "supported-boundary statement" in claim_audit["current_assessment"]
    assert any("artifact/runtime-capability" in blocker for blocker in claim_audit["full_claim_blockers"])
    assert any("FedPro route remains a bounded runtime slice" in blocker for blocker in claim_audit["full_claim_blockers"])
    requirement_audit = snapshot["requirement_by_requirement_audit"]
    assert requirement_audit["audit_status"] == "row-level-requirement-disposition-audit-captured"
    assert requirement_audit["ready_for_row_level_requirement_audit_claim"] is True
    assert requirement_audit["ready_for_full_2025_conformance_claim"] is False
    assert requirement_audit["row_count"] == 691
    assert requirement_audit["disposition_counts"] == {
        "covered": 645,
        "duplicate/umbrella": 22,
        "retired/legacy-only": 24,
    }
    assert requirement_audit["rows_with_complete_review_metadata"] == 691
    assert requirement_audit["covered_rows_with_evidence_paths"] == 645
    assert requirement_audit["unsupported_rows_with_explicit_boundary_flag"] == 0
    assert requirement_audit["duplicate_umbrella_rows_by_role"] == {
        "delta-umbrella": [
            "HLA2025-BIND-FEDPRO-001",
            "HLA2025-BIND-JAVA-CPP-001",
            "HLA2025-FI-AUTH-001",
            "HLA2025-FI-CB-001",
            "HLA2025-FI-CB-002",
            "HLA2025-FI-CB-003",
            "HLA2025-FI-CB-004",
            "HLA2025-FI-CB-005",
            "HLA2025-FI-CB-006",
            "HLA2025-FI-CB-007",
            "HLA2025-FI-CB-008",
            "HLA2025-FI-CFG-001",
        ],
        "framework-umbrella": [
            "HLA2025-FR-001",
            "HLA2025-FR-002",
            "HLA2025-FR-003",
            "HLA2025-FR-004",
            "HLA2025-FR-005",
            "HLA2025-FR-006",
            "HLA2025-FR-007",
            "HLA2025-FR-008",
            "HLA2025-FR-009",
            "HLA2025-FR-010",
        ],
    }
    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in requirement_audit["current_assessment"]
    assert "strengthens the bounded main-implementation claim for hla-backend-python2025" in requirement_audit["current_assessment"]
    assert "hla-backend-shim in a wrapper-only compatibility role" in requirement_audit["current_assessment"]
    assert any("third-party extension execution semantics" in blocker for blocker in requirement_audit["full_claim_blockers"])
    assert any("framework-rule umbrellas and callback/configuration/binding delta umbrellas" in blocker for blocker in requirement_audit["full_claim_blockers"])
    duplicate_umbrella_audit = snapshot["duplicate_umbrella_mapping_audit"]
    assert duplicate_umbrella_audit["audit_status"] == "duplicate-umbrella-mapping-captured"
    assert duplicate_umbrella_audit["row_count"] == 22
    assert duplicate_umbrella_audit["framework_doc_path"] == "docs/requirements/ieee-1516-2025/framework_rules.md"
    assert duplicate_umbrella_audit["delta_doc_path"] == "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
    assert duplicate_umbrella_audit["framework_row_count"] == 10
    assert duplicate_umbrella_audit["delta_row_count"] == 12
    assert duplicate_umbrella_audit["framework_missing_doc_anchor"] == []
    assert duplicate_umbrella_audit["delta_missing_doc_anchor"] == []
    assert duplicate_umbrella_audit["framework_missing_from_doc"] == []
    assert duplicate_umbrella_audit["delta_missing_from_doc"] == []
    assert duplicate_umbrella_audit["framework_missing_child_links"] == []
    assert duplicate_umbrella_audit["delta_missing_child_links"] == []
    assert duplicate_umbrella_audit["framework_unknown_child_ids"] == {}
    assert duplicate_umbrella_audit["delta_unknown_child_ids"] == {}
    assert duplicate_umbrella_audit["framework_rows_without_concrete_child"] == []
    assert duplicate_umbrella_audit["delta_rows_without_concrete_child"] == []
    assert duplicate_umbrella_audit["framework_child_links"]["HLA2025-FR-001"] == [
        "HLA2025-OMT-001",
        "HLA2025-OMT-005",
        "HLA2025-OMT-006",
        "HLA2025-REQ-001",
    ]
    assert duplicate_umbrella_audit["framework_child_links"]["HLA2025-FR-010"] == [
        "HLA2025-FI-009",
        "HLA2025-FI-SVC-101",
        "HLA2025-FI-SVC-107",
        "HLA2025-FI-SVC-112",
        "HLA2025-FI-SVC-121",
        "HLA2025-MOD-006",
    ]
    assert duplicate_umbrella_audit["delta_child_links"]["HLA2025-FI-CB-007"] == [
        "HLA2025-BND-003",
        "HLA2025-FI-SVC-063",
        "HLA2025-FI-SVC-064",
    ]
    assert duplicate_umbrella_audit["delta_child_links"]["HLA2025-BIND-JAVA-CPP-001"] == [
        "HLA2025-BND-001",
        "HLA2025-BND-002",
        "HLA2025-FI-003",
        "HLA2025-FI-004",
    ]
    assert duplicate_umbrella_audit["by_row_role"] == requirement_audit["duplicate_umbrella_rows_by_role"]
    assert duplicate_umbrella_audit["ready_for_duplicate_umbrella_mapping_claim"] is True
    assert "anchored to, enumerated by, and child-linked from those notes" in duplicate_umbrella_audit["current_assessment"]
    assert "does not change their status into standalone one-row conformance claims" in duplicate_umbrella_audit["residual_boundary"]
    retired_mapping_audit = snapshot["retired_legacy_mapping_audit"]
    assert retired_mapping_audit["audit_status"] == "retired-legacy-mapping-captured"
    assert retired_mapping_audit["doc_path"] == "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
    assert retired_mapping_audit["row_count"] == 24
    assert retired_mapping_audit["doc_exists"] is True
    assert retired_mapping_audit["rows_with_doc_anchor_count"] == 24
    assert retired_mapping_audit["rows_missing_doc_anchor"] == []
    assert retired_mapping_audit["rows_mentioned_in_doc_count"] == 24
    assert retired_mapping_audit["rows_missing_from_doc"] == []
    assert retired_mapping_audit["rows_with_candidate_replacement_note_count"] == 24
    assert retired_mapping_audit["rows_missing_candidate_replacement_note"] == []
    assert retired_mapping_audit["by_service_group"] == {
        "Federate Interface legacy API": [
            "HLA2025-FI-RET-001",
            "HLA2025-FI-RET-002",
            "HLA2025-FI-RET-003",
            "HLA2025-FI-RET-004",
            "HLA2025-FI-RET-005",
            "HLA2025-FI-RET-006",
            "HLA2025-FI-RET-007",
            "HLA2025-FI-RET-008",
            "HLA2025-FI-RET-009",
            "HLA2025-FI-RET-010",
            "HLA2025-FI-RET-011",
        ],
        "OMT legacy schema": [
            "HLA2025-OMT-RET-001",
            "HLA2025-OMT-RET-002",
            "HLA2025-OMT-RET-003",
            "HLA2025-OMT-RET-004",
            "HLA2025-OMT-RET-005",
            "HLA2025-OMT-RET-006",
            "HLA2025-OMT-RET-007",
            "HLA2025-OMT-RET-008",
            "HLA2025-OMT-RET-009",
            "HLA2025-OMT-RET-010",
            "HLA2025-OMT-RET-011",
            "HLA2025-OMT-RET-012",
            "HLA2025-OMT-RET-013",
        ],
    }
    assert retired_mapping_audit["ready_for_retired_legacy_mapping_claim"] is True
    assert "explicit mapping note that enumerates every retired row" in retired_mapping_audit["current_assessment"]
    assert "does not convert those legacy-only rows into active 2025 support obligations" in retired_mapping_audit["residual_boundary"]
    omt_xs_any_mapping_audit = snapshot["omt_xs_any_mapping_audit"]
    assert omt_xs_any_mapping_audit["audit_status"] == "omt-xs-any-mapping-captured"
    assert omt_xs_any_mapping_audit["doc_path"] == "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md"
    assert omt_xs_any_mapping_audit["row_count"] == 45
    assert omt_xs_any_mapping_audit["doc_exists"] is True
    assert omt_xs_any_mapping_audit["rows_with_doc_anchor_count"] == 45
    assert omt_xs_any_mapping_audit["rows_missing_doc_anchor"] == []
    assert omt_xs_any_mapping_audit["rows_mentioned_in_doc_count"] == 45
    assert omt_xs_any_mapping_audit["rows_missing_from_doc"] == []
    assert omt_xs_any_mapping_audit["family_count"] == 5
    assert omt_xs_any_mapping_audit["family_headings_ready"] is True
    assert omt_xs_any_mapping_audit["by_family"] == {
        "object-model-root-and-identity": [
            "HLA2025-OMT-COMP-006",
            "HLA2025-OMT-COMP-008",
        ],
        "object-class-and-attribute-extension-points": [
            "HLA2025-OMT-COMP-019",
            "HLA2025-OMT-COMP-021",
            "HLA2025-OMT-COMP-027",
            "HLA2025-OMT-COMP-035",
            "HLA2025-OMT-COMP-039",
            "HLA2025-OMT-COMP-045",
            "HLA2025-OMT-COMP-047",
            "HLA2025-OMT-COMP-056",
            "HLA2025-OMT-COMP-057",
            "HLA2025-OMT-COMP-059",
            "HLA2025-OMT-COMP-067",
            "HLA2025-OMT-COMP-068",
            "HLA2025-OMT-COMP-070",
            "HLA2025-OMT-COMP-077",
            "HLA2025-OMT-COMP-081",
            "HLA2025-OMT-COMP-082",
        ],
        "interaction-class-and-parameter-extension-points": [
            "HLA2025-OMT-COMP-102",
            "HLA2025-OMT-COMP-106",
            "HLA2025-OMT-COMP-107",
            "HLA2025-OMT-COMP-113",
            "HLA2025-OMT-COMP-115",
            "HLA2025-OMT-COMP-129",
            "HLA2025-OMT-COMP-130",
            "HLA2025-OMT-COMP-134",
        ],
        "datatype-and-encoding-extension-points": [
            "HLA2025-OMT-COMP-145",
            "HLA2025-OMT-COMP-147",
            "HLA2025-OMT-COMP-154",
            "HLA2025-OMT-COMP-156",
            "HLA2025-OMT-COMP-171",
            "HLA2025-OMT-COMP-176",
            "HLA2025-OMT-COMP-178",
            "HLA2025-OMT-COMP-181",
            "HLA2025-OMT-COMP-189",
            "HLA2025-OMT-COMP-193",
            "HLA2025-OMT-COMP-197",
            "HLA2025-OMT-COMP-198",
        ],
        "container-table-and-reference-extension-points": [
            "HLA2025-OMT-COMP-202",
            "HLA2025-OMT-COMP-204",
            "HLA2025-OMT-COMP-208",
            "HLA2025-OMT-COMP-210",
            "HLA2025-OMT-COMP-219",
            "HLA2025-OMT-COMP-222",
            "HLA2025-OMT-COMP-224",
        ],
    }
    assert omt_xs_any_mapping_audit["test_path"] == "tests/test_rti1516_2025_validation.py"
    assert omt_xs_any_mapping_audit["implementation_path"] == "packages/hla-rti1516e/src/hla/rti1516e/fom.py"
    assert omt_xs_any_mapping_audit["ready_for_omt_xs_any_mapping_claim"] is True
    assert omt_xs_any_mapping_audit["executable_anchor_ready"] is True
    assert omt_xs_any_mapping_audit["implementation_anchor_ready"] is True
    assert "concrete parser round-trip test for foreign namespace payload preservation" in omt_xs_any_mapping_audit["current_assessment"]
    assert "does not convert foreign extension payload tolerance into arbitrary third-party extension execution semantics" in omt_xs_any_mapping_audit["residual_boundary"]
    binding_boundary_audit = snapshot["binding_boundary_mapping_audit"]
    assert binding_boundary_audit["audit_status"] == "binding-boundary-mapping-captured"
    assert binding_boundary_audit["doc_path"] == "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md"
    assert binding_boundary_audit["row_count"] == 3
    assert binding_boundary_audit["doc_exists"] is True
    assert binding_boundary_audit["rows_with_doc_anchor_count"] == 3
    assert binding_boundary_audit["rows_missing_doc_anchor"] == []
    assert binding_boundary_audit["rows_mentioned_in_doc_count"] == 3
    assert binding_boundary_audit["rows_missing_from_doc"] == []
    assert binding_boundary_audit["boundary_narrative_ready"] is True
    assert binding_boundary_audit["by_boundary_role"] == {
        "java-binding": ["HLA2025-BND-001"],
        "cpp-binding": ["HLA2025-BND-002"],
        "hosted-fedpro": ["HLA2025-BND-003"],
    }
    assert binding_boundary_audit["ready_for_binding_boundary_mapping_claim"] is True
    assert "explicit boundary note that enumerates all three rows" in binding_boundary_audit["current_assessment"]
    assert "does not promote the Java/C++ rows into exhaustive cross-binding behavior conformance" in binding_boundary_audit["residual_boundary"]
    direct_bounded_audit = snapshot["python2025_direct_bounded_proof_audit"]
    assert direct_bounded_audit["audit_status"] == "python2025-direct-bounded-proof-captured"
    assert direct_bounded_audit["doc_path"] == "docs/requirements/ieee-1516-2025/python2025_direct_bounded_proof.md"
    assert direct_bounded_audit["doc_exists"] is True
    assert direct_bounded_audit["route"] == "python-2025-inprocess"
    assert direct_bounded_audit["scenario_count"] == 8
    assert direct_bounded_audit["scenarios"] == [
        "ddm",
        "federation_lifecycle",
        "mom",
        "object_exchange",
        "ownership",
        "save_restore",
        "support_services",
        "time_management",
    ]
    assert direct_bounded_audit["expected_scenarios"] == direct_bounded_audit["scenarios"]
    assert direct_bounded_audit["missing_family_labels"] == []
    assert direct_bounded_audit["missing_evidence_markers"] == []
    assert direct_bounded_audit["all_rows_parity_covered"] is True
    assert direct_bounded_audit["identity_ready"] is True
    assert direct_bounded_audit["rows_missing_identity_note"] == []
    assert direct_bounded_audit["rows_missing_direct_note"] == []
    assert direct_bounded_audit["doc_narrative_ready"] is True
    assert direct_bounded_audit["ready_for_python2025_direct_bounded_proof_claim"] is True
    assert "paired hosted companion note" in direct_bounded_audit["current_assessment"]
    assert "does not convert the direct lane into a full clause-by-clause 2025 conformance statement" in direct_bounded_audit["residual_boundary"]
    exclusion_boundaries_audit = snapshot["python2025_exclusion_boundaries_audit"]
    assert exclusion_boundaries_audit["audit_status"] == "python2025-exclusion-boundaries-captured"
    assert exclusion_boundaries_audit["doc_path"] == "docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md"
    assert exclusion_boundaries_audit["doc_exists"] is True
    assert exclusion_boundaries_audit["required_area_labels"] == [
        "Legacy aliases and shim imports",
        "Java/C++ bindings",
        "Hosted transport boundaries",
        "Duplicate/umbrella rows",
        "Retired/legacy-only rows",
        "OMT extension semantics",
    ]
    assert exclusion_boundaries_audit["missing_area_labels"] == []
    assert exclusion_boundaries_audit["missing_doc_markers"] == []
    assert exclusion_boundaries_audit["duplicate_umbrella_row_count"] == 22
    assert exclusion_boundaries_audit["retired_row_count"] == 24
    assert exclusion_boundaries_audit["doc_narrative_ready"] is True
    assert exclusion_boundaries_audit["ready_for_python2025_exclusion_boundaries_claim"] is True
    assert "explicit requirement-facing boundary note" in exclusion_boundaries_audit["current_assessment"]
    assert "does not by itself prove the underlying direct or hosted runtime behavior" in exclusion_boundaries_audit["residual_boundary"]
    hosted_fedpro_audit = snapshot["hosted_fedpro_bounded_proof_audit"]
    assert hosted_fedpro_audit["audit_status"] == "hosted-fedpro-bounded-proof-captured"
    assert hosted_fedpro_audit["doc_path"] == "docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md"
    assert hosted_fedpro_audit["doc_exists"] is True
    assert hosted_fedpro_audit["route"] == "python-2025-fedpro-grpc"
    assert hosted_fedpro_audit["scenario_count"] == 8
    assert hosted_fedpro_audit["scenarios"] == [
        "ddm",
        "federation_lifecycle",
        "mom",
        "object_exchange",
        "ownership",
        "save_restore",
        "support_services",
        "time_management",
    ]
    assert hosted_fedpro_audit["expected_scenarios"] == hosted_fedpro_audit["scenarios"]
    assert hosted_fedpro_audit["required_evidence_tests"] == [
        "tests/transport/test_grpc_transport_2025.py",
        "tests/scenarios/test_python_route_parity.py",
    ]
    assert hosted_fedpro_audit["all_rows_parity_covered"] is True
    assert hosted_fedpro_audit["identity_ready"] is True
    assert hosted_fedpro_audit["rows_missing_required_evidence_tests"] == {}
    assert hosted_fedpro_audit["rows_missing_identity_note"] == []
    assert hosted_fedpro_audit["rows_missing_transport_seam_note"] == []
    assert hosted_fedpro_audit["doc_narrative_ready"] is True
    assert hosted_fedpro_audit["ready_for_hosted_fedpro_bounded_proof_claim"] is True
    assert "per-scenario transport-plus-parity test anchors" in hosted_fedpro_audit["current_assessment"]
    assert "does not promote the hosted FedPro lane into full remote-RTI semantics" in hosted_fedpro_audit["residual_boundary"]
    save_restore_bounded_audit = snapshot["save_restore_bounded_proof_audit"]
    assert save_restore_bounded_audit["audit_status"] == "save-restore-bounded-proof-captured"
    assert save_restore_bounded_audit["doc_path"] == "docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md"
    assert save_restore_bounded_audit["doc_exists"] is True
    assert save_restore_bounded_audit["proof_family_count"] == 5
    assert save_restore_bounded_audit["requirement_family_count"] == 5
    assert save_restore_bounded_audit["required_family_labels"] == [
        "Lifecycle control",
        "Shared scenario rollback",
        "Routing and policy rollback",
        "Ownership rollback",
        "Time-window and time-state rollback",
    ]
    assert save_restore_bounded_audit["missing_family_labels"] == []
    assert save_restore_bounded_audit["missing_row_markers"] == []
    assert save_restore_bounded_audit["missing_test_markers"] == []
    assert save_restore_bounded_audit["doc_narrative_ready"] is True
    assert save_restore_bounded_audit["ready_for_save_restore_bounded_proof_claim"] is True
    assert "save/restore surface is no longer only captured as one generated decomposition plus family-map pair" in save_restore_bounded_audit["current_assessment"]
    assert "does not turn every save/restore requirement into its own standalone clause-by-clause conformance proof" in save_restore_bounded_audit["residual_boundary"]
    callback_bounded_audit = snapshot["callback_bounded_proof_audit"]
    assert callback_bounded_audit["audit_status"] == "callback-bounded-proof-captured"
    assert callback_bounded_audit["doc_path"] == "docs/requirements/ieee-1516-2025/callback_bounded_proof.md"
    assert callback_bounded_audit["doc_exists"] is True
    assert callback_bounded_audit["proof_family_count"] == 8
    assert callback_bounded_audit["callback_row_count"] == 55
    assert callback_bounded_audit["hosted_route_backed_callback_count"] == 55
    assert callback_bounded_audit["required_family_labels"] == [
        "Declaration relevance and interest advisories",
        "Federation sync, save/restore, and reporting callbacks",
        "Object discovery, delivery, and removal",
        "Object advisory, transport, and name-reservation callbacks",
        "Supplemental callback context and region metadata",
        "Ownership negotiation and query callbacks",
        "Time grant, regulation, and retraction callbacks",
        "Callback control and backlog hygiene",
    ]
    assert callback_bounded_audit["missing_family_labels"] == []
    assert callback_bounded_audit["missing_test_markers"] == []
    assert callback_bounded_audit["doc_narrative_ready"] is True
    assert callback_bounded_audit["ready_for_callback_bounded_proof_claim"] is True
    assert "callback surface is no longer only captured as a callback ledger plus decomposition audit" in callback_bounded_audit["current_assessment"]
    assert "does not turn the repo into an exhaustive callback signature/ordering equivalence proof across every binding" in callback_bounded_audit["residual_boundary"]
    lookahead_window_audit = snapshot["lookahead_window_bounded_proof_audit"]
    assert lookahead_window_audit["audit_status"] == "lookahead-window-bounded-proof-captured"
    assert lookahead_window_audit["doc_path"] == "docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md"
    assert lookahead_window_audit["doc_exists"] is True
    assert lookahead_window_audit["proof_level_count"] == 10
    assert lookahead_window_audit["required_proof_levels"] == [
        "time-window-core",
        "time-window-future-exclusion",
        "time-window-output-delivery",
        "time-window-consumer-order",
        "time-window-pipeline-two-scans",
        "time-window-receive-order-poison",
        "time-window-save-restore-window-state",
        "time-window-save-restore-output-resume",
        "time-window-save-restore-pipeline-resume",
        "lookahead-processing-window-certified",
    ]
    assert lookahead_window_audit["missing_proof_levels"] == []
    assert lookahead_window_audit["route_row_count"] == 4
    assert lookahead_window_audit["routes"] == [
        "save_restore:python-2025-fedpro-grpc",
        "save_restore:python-2025-inprocess",
        "time_management:python-2025-fedpro-grpc",
        "time_management:python-2025-inprocess",
    ]
    assert lookahead_window_audit["required_evidence_tests"] == {
        "time_management:python-2025-fedpro-grpc": [
            "tests/scenarios/test_python_route_parity.py",
            "tests/transport/test_grpc_transport_2025.py",
        ],
        "time_management:python-2025-inprocess": [
            "tests/scenarios/test_python_route_parity.py",
            "tests/test_rti1516_2025_python2025_runtime.py",
        ],
    }
    assert lookahead_window_audit["missing_evidence_tests"] == {}
    assert lookahead_window_audit["route_note_checks_ready"] is True
    assert lookahead_window_audit["doc_narrative_ready"] is True
    assert lookahead_window_audit["pitch_probe_routes"] == [
        "./tools/pitch time-window-probe",
        "./tools/pitch time-window-restore-state-probe",
    ]
    assert lookahead_window_audit["ready_for_lookahead_window_bounded_proof_claim"] is True
    assert "Target/Radar lookahead ladder is no longer only embedded in the generic time-management and milestone wording" in lookahead_window_audit["current_assessment"]
    assert "does not convert the bounded ladder into an unconditional clause-by-clause 2025 time-policy conformance pass" in lookahead_window_audit["residual_boundary"]
    standard_binding_audit = snapshot["standard_binding_runtime_capability_audit"]
    assert standard_binding_audit["audit_status"] == "standard-binding-runtime-capability-captured"
    assert standard_binding_audit["doc_path"] == "docs/requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md"
    assert standard_binding_audit["doc_exists"] is True
    assert standard_binding_audit["row_count"] == 32
    assert standard_binding_audit["required_evidence_test"] == "tests/backends/test_standard_shim_artifacts.py"
    assert standard_binding_audit["identity_ready"] is True
    assert standard_binding_audit["rows_missing_required_evidence_test"] == []
    assert standard_binding_audit["rows_missing_route_trace_artifact"] == []
    assert standard_binding_audit["rows_missing_binding_aggregate_artifact"] == []
    assert standard_binding_audit["rows_missing_backing_note"] == []
    assert standard_binding_audit["rows_missing_seam_note"] == []
    assert standard_binding_audit["doc_narrative_ready"] is True
    assert standard_binding_audit["by_binding_requirement"] == {
        "HLA2025-BND-001": {
            "routes": ["java-standard-2025-jpype", "java-standard-2025-py4j"],
            "parity_covered_row_count": 16,
            "non_covered_row_count": 0,
        },
        "HLA2025-BND-002": {
            "routes": ["cpp-standard-2025-grpc", "cpp-standard-2025-pybind"],
            "parity_covered_row_count": 16,
            "non_covered_row_count": 0,
        },
    }
    assert standard_binding_audit["ready_for_standard_binding_runtime_capability_claim"] is True
    assert "per-row executable plus artifact anchors" in standard_binding_audit["current_assessment"]
    assert "does not promote standard-route traces into exhaustive cross-binding behavior equivalence" in standard_binding_audit["residual_boundary"]
    boundary_statement = snapshot["supported_boundary_statement"]
    assert boundary_statement["statement_status"] == "supported-boundary-statement"
    assert boundary_statement["ready"] is True
    assert "bounded working surface" in boundary_statement["statement"]
    assert "binding and hosted routes" in boundary_statement["statement"]
    assert "explicit legacy-only, bounded-extension, and artifact-gated boundaries" in boundary_statement["statement"]
    assert len(boundary_statement["supported_scope"]) == 4
    assert any("196 catalog rows" in item for item in boundary_statement["supported_scope"])
    assert any("FedPro 2025 transport behavior is executable as a bounded runtime slice" in item for item in boundary_statement["supported_scope"])
    assert any("transport-seam evidence over hla-backend-python2025" in item for item in boundary_statement["supported_scope"])
    assert len(boundary_statement["explicit_boundaries"]) == 4
    assert any("Foreign OMT xs:any extension payloads are preserved for XML round-trip" in item for item in boundary_statement["explicit_boundaries"])
    assert any("Java and C++ bindings remain artifact/runtime-capability bounded as binding/adaptation-seam proof" in item for item in boundary_statement["explicit_boundaries"])
    assert any("transport-seam proof gaps rather than evidence that hla-backend-python2025 lacks the underlying semantics" in item for item in boundary_statement["explicit_boundaries"])
    assert boundary_statement["evidence_summary"] == {
        "bounded_ready_dimensions": 8,
        "dimension_count": 8,
        "route_parity_missing_count": 0,
        "route_parity_partial_count": 0,
        "covered_rows": 645,
        "unsupported_boundary_rows": 0,
        "retired_or_legacy_only_rows": 24,
    }
    callback_audit = snapshot["callback_proof_audit"]
    assert callback_audit["row_count"] == 55
    assert callback_audit["helper_backed_callback_count"] == callback_audit["row_count"]
    assert callback_audit["focused_executable_callback_count"] == callback_audit["row_count"]
    assert callback_audit["helper_covered_callback_count"] == 0
    assert callback_audit["rows_with_known_gaps"] == 0
    assert callback_audit["ready_for_callback_surface_traceability_claim"] is True
    assert callback_audit["ready_for_callback_by_callback_working_surface_claim"] is True
    assert callback_audit["by_verification_status"] == {"focused-executable-tests": 55}
    assert "callback-by-callback ledger" in callback_audit["current_assessment"]
    assert "focused executable evidence" in callback_audit["current_assessment"]
    assert "full callback conformance claim" in callback_audit["current_assessment"]
    assert "reconnect-safe callback backlog cleanup across disconnect/reconnect" in callback_audit["current_assessment"]
    callback_rows = {row["method_name"]: row for row in callback_audit["rows"]}
    assert callback_rows["receiveInteraction"]["implementation_status"] == "callback-helper"
    assert callback_rows["reflectAttributeValues"]["implementation_status"] == "callback-helper"
    assert callback_rows["timeAdvanceGrant"]["implementation_status"] == "callback-helper"
    assert callback_rows["receiveInteraction"]["positive_test_refs"]
    assert callback_rows["reflectAttributeValues"]["positive_test_refs"]
    assert callback_rows["timeAdvanceGrant"]["positive_test_refs"]
    callback_route_parity_audit = snapshot["callback_route_parity_audit"]
    assert callback_route_parity_audit["row_count"] == 55
    assert callback_route_parity_audit["hosted_or_route_backed_callback_count"] == 55
    assert callback_route_parity_audit["callback_helper_only_count"] == 0
    assert callback_route_parity_audit["ready_for_full_python_lane_callback_route_parity_claim"] is True
    assert callback_route_parity_audit["ready_for_exhaustive_cross_binding_callback_parity_claim"] is False
    assert "fully route-backed across the current Python 2025 lanes" in callback_route_parity_audit["current_assessment"]
    assert "signature and ordering equivalence" in callback_route_parity_audit["current_assessment"]
    assert callback_route_parity_audit["hosted_or_route_backed_callbacks"] == [
        "announceSynchronizationPoint",
        "attributeIsNotOwned",
        "attributeIsOwnedByRTI",
        "attributeOwnershipAcquisitionNotification",
        "attributeOwnershipUnavailable",
        "attributesInScope",
        "attributesOutOfScope",
        "confirmAttributeOwnershipAcquisitionCancellation",
        "confirmAttributeTransportationTypeChange",
        "confirmInteractionTransportationTypeChange",
        "connectionLost",
        "discoverObjectInstance",
        "federationNotRestored",
        "federationNotSaved",
        "federationRestoreBegun",
        "federationRestoreStatusResponse",
        "federationRestored",
        "federationSaveStatusResponse",
        "federationSaved",
        "federationSynchronized",
        "getProducingFederate",
        "getSentRegions",
        "hasProducingFederate",
        "hasSentRegions",
        "informAttributeOwnership",
        "initiateFederateRestore",
        "initiateFederateSave",
        "multipleObjectInstanceNameReservationFailed",
        "multipleObjectInstanceNameReservationSucceeded",
        "objectInstanceNameReservationFailed",
        "objectInstanceNameReservationSucceeded",
        "provideAttributeValueUpdate",
        "receiveInteraction",
        "reflectAttributeValues",
        "removeObjectInstance",
        "reportAttributeTransportationType",
        "reportFederationExecutions",
        "reportInteractionTransportationType",
        "requestAttributeOwnershipAssumption",
        "requestAttributeOwnershipRelease",
        "requestDivestitureConfirmation",
        "requestFederationRestoreFailed",
        "requestFederationRestoreSucceeded",
        "requestRetraction",
        "startRegistrationForObjectClass",
        "stopRegistrationForObjectClass",
        "synchronizationPointRegistrationFailed",
        "synchronizationPointRegistrationSucceeded",
        "timeAdvanceGrant",
        "timeConstrainedEnabled",
        "timeRegulationEnabled",
        "turnInteractionsOff",
        "turnInteractionsOn",
        "turnUpdatesOffForObjectInstance",
        "turnUpdatesOnForObjectInstance",
    ]
    assert callback_route_parity_audit["sample_callback_helper_only_rows"] == []
    callback_decomposition_audit = snapshot["callback_decomposition_audit"]
    assert callback_decomposition_audit["audit_status"] == "callback-decomposition-captured"
    assert callback_decomposition_audit["slice_id"] == "2025-callback-proof-families"
    assert callback_decomposition_audit["slice_ids"] == [
        "2025-callback-context-object-delivery",
        "2025-callback-context-interaction-delivery",
        "2025-connection-lifecycle-services",
        "2025-connect-and-federation-catalog-services",
        "2025-federate-membership-and-resign-services",
        "2025-synchronization-point-services",
        "2025-object-delete-remove-flows",
        "2025-object-attribute-update-request-callbacks",
        "2025-object-scope-advisory-callbacks",
        "2025-object-update-rate-advisory-callbacks",
        "2025-object-attribute-transport-callbacks",
        "2025-object-interaction-transport-callbacks",
        "2025-single-name-reservation-services",
        "2025-multi-name-reservation-services",
        "2025-save-restore-lifecycle",
        "2025-fedpro-hosted-runtime-core",
        "2025-fedpro-hosted-runtime-extended-state",
    ]
    assert callback_decomposition_audit["requirement_count"] == 66
    assert callback_decomposition_audit["proof_family_count"] == 8
    assert callback_decomposition_audit["direct_family_count"] == 8
    assert callback_decomposition_audit["hosted_family_count"] == 8
    assert [family["family"] for family in callback_decomposition_audit["proof_families"]] == [
        "declaration-relevance-and-interest-advisories",
        "federation-sync-save-restore-and-reporting",
        "object-discovery-delivery-and-removal",
        "object-advisory-transport-and-name-reservation-callbacks",
        "supplemental-context-and-region-introspection",
        "ownership-negotiation-and-query-callbacks",
        "time-grant-regulation-and-retraction",
        "callback-control-and-backlog-hygiene",
    ]
    assert "no longer just a flat ledger plus one route-backed count" in callback_decomposition_audit["current_assessment"]
    assert "declaration advisories, federation sync/save-restore/reporting" in callback_decomposition_audit["current_assessment"]
    assert callback_decomposition_audit["proof_families"][0]["hosted_tests"][-1].endswith(
        "test_2025_transport_server_runs_shared_time_managed_declaration_independence_scenario_over_fedpro_route"
    )
    assert callback_decomposition_audit["proof_families"][4]["direct_tests"] == [
        "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_preserves_direct_callback_context_for_timed_region_delivery",
    ]
    assert callback_decomposition_audit["proof_families"][-1]["hosted_tests"][-1].endswith(
        "test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing"
    )
    time_management_decomposition_audit = snapshot["time_management_decomposition_audit"]
    assert time_management_decomposition_audit["audit_status"] == "time-management-decomposition-captured"
    assert time_management_decomposition_audit["slice_id"] == "2025-time-management-proof-families"
    assert time_management_decomposition_audit["slice_ids"] == [
        "2025-time-mode-enable-disable",
        "2025-time-advance-request-modes",
        "2025-time-grant-and-async-delivery",
        "2025-time-query-and-lookahead-control",
        "2025-time-queries-retraction-and-order",
        "2025-lookahead-window-proofs",
        "2025-save-restore-lifecycle",
    ]
    assert time_management_decomposition_audit["requirement_count"] == 48
    assert time_management_decomposition_audit["proof_family_count"] == 5
    assert time_management_decomposition_audit["direct_family_count"] == 5
    assert time_management_decomposition_audit["hosted_family_count"] == 5
    assert [family["family"] for family in time_management_decomposition_audit["proof_families"]] == [
        "factory-mode-enable-and-request-primitives",
        "galt-lits-query-and-lookahead-observability",
        "timestamped-delivery-retraction-and-ordering",
        "lookahead-window-proof-ladder",
        "save-restore-time-state-and-lookahead-rollback",
    ]
    assert "no longer just one bounded query/window bucket" in time_management_decomposition_audit["current_assessment"]
    assert "GALT/LITS and lookahead observability" in time_management_decomposition_audit["current_assessment"]
    assert time_management_decomposition_audit["proof_families"][0]["hosted_tests"][-1].endswith(
        "test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions"
    )
    assert time_management_decomposition_audit["proof_families"][3]["direct_tests"][-1].endswith(
        "test_2025_provider_runs_integrated_time_window_gauntlet_end_to_end"
    )
    assert time_management_decomposition_audit["proof_families"][-1]["hosted_tests"][-1].endswith(
        "test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_route"
    )
    binding_route_decomposition_audit = snapshot["binding_route_decomposition_audit"]
    assert binding_route_decomposition_audit["audit_status"] == "binding-route-decomposition-captured"
    assert binding_route_decomposition_audit["slice_id"] == "2025-binding-route-proof-families"
    assert binding_route_decomposition_audit["slice_ids"] == [
        "2025-java-binding-source-trace",
        "2025-cpp-binding-source-trace",
        "2025-standard-route-runtime-capability",
        "2025-fedpro-typed-transport-surface",
        "2025-fedpro-hosted-runtime-core",
        "2025-fedpro-hosted-runtime-extended-state",
    ]
    assert binding_route_decomposition_audit["requirement_count"] == 16
    assert binding_route_decomposition_audit["proof_family_count"] == 6
    assert binding_route_decomposition_audit["route_group_coverage_count"] == 16
    assert [family["family"] for family in binding_route_decomposition_audit["proof_families"]] == [
        "java-binding-source-and-intake-evidence",
        "cpp-binding-source-and-intake-evidence",
        "standard-java-cpp-runtime-capability-traces",
        "fedpro-typed-transport-and-schema-surface",
        "fedpro-hosted-runtime-core-and-extended-state",
        "cross-route-scenario-parity-ledger",
    ]
    assert "named binding and hosted-route families" in binding_route_decomposition_audit["current_assessment"]
    assert "bounded adapter evidence and the main python2025 runtime owner explicit" in binding_route_decomposition_audit["current_assessment"]
    assert binding_route_decomposition_audit["proof_families"][2]["route_groups"] == [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ]
    assert binding_route_decomposition_audit["proof_families"][4]["evidence_tests"][0] == (
        "tests/transport/test_grpc_transport_2025.py"
    )
    support_service_audit = snapshot["support_service_proof_audit"]
    assert support_service_audit["row_count"] == 62
    assert support_service_audit["focused_executable_row_count"] == 62
    assert support_service_audit["rows_with_known_gaps"] == 0
    assert support_service_audit["complete_negative_path_row_count"] == 61
    assert support_service_audit["partial_negative_path_row_count"] == 0
    assert support_service_audit["mapped_not_exhaustive_negative_path_row_count"] == 0
    assert support_service_audit["ready_for_support_service_traceability_claim"] is True
    assert support_service_audit["ready_for_support_service_full_conformance_claim"] is True
    assert support_service_audit["by_verification_status"] == {"focused-executable-tests": 62}
    assert support_service_audit["by_negative_path_status"] == {
        "complete": 61,
        "not-applicable": 1,
    }
    assert "explicit support-service ledger" in support_service_audit["current_assessment"]
    assert "Negative-path coverage is now complete for all 61 actionable support-service rows" in support_service_audit["current_assessment"]
    assert "ready for a requirement-level full conformance claim within this audit slice" in (
        support_service_audit["current_assessment"]
    )
    assert "reconnect-safe discard of a disconnected peer's disabled callback backlog before later reconnect" in support_service_audit["current_assessment"]
    support_rows = {row["method_name"]: row for row in support_service_audit["rows"]}
    assert support_rows["enableCallbacks"]["positive_test_refs"]
    assert support_rows["disableCallbacks"]["positive_test_refs"]
    assert support_rows["evokeCallback"]["positive_test_refs"]
    assert support_rows["getObjectInstanceName"]["positive_test_refs"]
    assert support_rows["getUpdateRateValue"]["negative_path_status"] == "complete"
    assert support_rows["getUpdateRateValueForAttribute"]["negative_path_status"] == "complete"
    assert support_rows["setRangeBounds"]["negative_path_status"] == "complete"
    assert support_rows["getTransportationType"]["negative_path_status"] == "complete"
    assert support_rows["getAttributeHandleFactory"]["negative_path_status"] == "complete"
    assert support_rows["getObjectInstanceName"]["known_gaps"] == []
    promotion_split_audit = snapshot["promotion_split_audit"]
    assert snapshot["promotion_vs_split_audit"] == promotion_split_audit
    assert snapshot["route_parity_audit"] == snapshot["route_parity_matrix"]
    assert promotion_split_audit["decision_shape"] == "promote-current-lane-or-split-later-based-on-evidence"
    assert promotion_split_audit["current_lane"] == {
        "package": "hla-backend-python2025",
        "role": "main full Python 2025 RTI implementation lane (owned by hla-backend-python2025 with hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support)",
        "spec_package": "hla-rti1516-2025",
    }
    assert promotion_split_audit["current_recommendation"] == "promote-current-lane-as-working-surface-and-keep-split-optional"
    assert promotion_split_audit["ready_for_current_lane_promotion_as_working_surface"] is True
    assert promotion_split_audit["ready_for_permanent_no-split_decision"] is False
    assert len(promotion_split_audit["promotion_basis"]) == 8
    assert any("main in-process suite" in item for item in promotion_split_audit["promotion_basis"])
    assert any("bounded working-surface milestones" in item for item in promotion_split_audit["promotion_basis"])
    assert any("direct split-package proof" in item for item in promotion_split_audit["promotion_basis"])
    assert any("import-boundary guardrails" in item for item in promotion_split_audit["promotion_basis"])
    assert any("fully route-backed across the current Python 2025 lanes" in item for item in promotion_split_audit["promotion_basis"])
    assert any("main current-package pressure families" in item for item in promotion_split_audit["promotion_basis"])
    evidence_runs = {run["name"]: run for run in promotion_split_audit["current_evidence_runs"]}
    assert "target-radar-time-window-proof-ladder" in evidence_runs
    assert evidence_runs["target-radar-time-window-proof-ladder"]["result"] == "26 passed, 8 deselected in 4.78s"
    assert "future-exclusion" in evidence_runs["target-radar-time-window-proof-ladder"]["scope"]
    assert "save/restore time-window proofs" in evidence_runs["target-radar-time-window-proof-ladder"]["scope"]
    assert evidence_runs["python2025-split-package-surface"]["result"] == "71 passed in 0.67s"
    assert "dedicated hla-backend-python2025 package surface plus local factory composition" in evidence_runs["python2025-split-package-surface"]["scope"]
    assert evidence_runs["python2025-import-boundary-guardrails"]["result"] == "163 passed in 40.34s"
    assert "explicit no-backflow proof" in evidence_runs["python2025-import-boundary-guardrails"]["scope"]
    assert (
        evidence_runs["combined-2025-verification-slice"]["result"]
        == "targeted finish-line/backend-owner audit slice ran green on current tree"
    )
    assert "finish-line and backend-owner audit pair" in evidence_runs["combined-2025-verification-slice"]["scope"]
    assert (
        evidence_runs["hosted-2025-fedpro-transport-suite"]["result"]
        == "252 passed in current-tree hosted FedPro transport suite"
    )
    assert "object/ownership/save-restore coverage" in evidence_runs["hosted-2025-fedpro-transport-suite"]["scope"]
    assert len(promotion_split_audit["split_triggers"]) == 4
    assert any("obscure or distort core RTI semantics" in item for item in promotion_split_audit["split_triggers"])
    assert any("route normalization grows more complex" in item for item in promotion_split_audit["split_triggers"])
    assert len(promotion_split_audit["permanent_decision_blockers"]) == 4
    assert any("row-level requirement-by-requirement audit" in item for item in promotion_split_audit["permanent_decision_blockers"])
    assert any("Hosted FedPro remains a bounded runtime slice" in item for item in promotion_split_audit["permanent_decision_blockers"])
    assert "real Python 2025 RTI implementation now owned by hla-backend-python2025" in promotion_split_audit["current_assessment"]
    assert "hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in promotion_split_audit["current_assessment"]
    assert "main current-package pressure families" in promotion_split_audit["current_assessment"]
    concentration_audit = snapshot["implementation_concentration_audit"]
    assert concentration_audit["audit_status"] == "implementation-concentration-captured"
    assert concentration_audit["implemented_slice_count"] == 76
    assert concentration_audit["runtime_backend_path"] == "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py"
    assert concentration_audit["runtime_backend_slice_count"] == 42
    assert concentration_audit["runtime_backend_slice_share"] == 0.553
    assert concentration_audit["spec_package_slice_count"] == 12
    assert concentration_audit["transport_slice_count"] == 11
    assert concentration_audit["semantic_concentration_is_material"] is False
    assert concentration_audit["runtime_ambassador_method_line_count"] == snapshot["python2025_source_responsibility_audit"]["ambassador_method_line_count"]
    assert concentration_audit["extracted_runtime_module_line_count"] >= 10000
    assert concentration_audit["backend_shell_ratio"] < 0.05
    assert "semantic concentration is no longer material there" in concentration_audit["current_assessment"]
    assert "ambassador shell is thin" in concentration_audit["current_assessment"]
    assert "wrapper-only compatibility logic should keep shrinking" in concentration_audit["extraction_pressure_boundary"]
    assert concentration_audit["top_evidence_anchors"][:5] == [
        {"path": "tests/transport/test_grpc_transport_2025.py", "slice_count": 53},
        {"path": "tests/test_rti1516_2025_python2025_runtime.py", "slice_count": 49},
        {"path": "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py", "slice_count": 42},
        {"path": "tests/test_rti1516_2025_validation.py", "slice_count": 12},
        {"path": "packages/hla-rti1516e/src/hla/rti1516e/fom.py", "slice_count": 12},
    ]
    leading_runtime_modules = concentration_audit["leading_extracted_runtime_modules"]
    assert len(leading_runtime_modules) == 5
    assert leading_runtime_modules == sorted(
        leading_runtime_modules,
        key=lambda module: (-int(module["line_count"]), str(module["path"])),
    )
    leading_paths = {module["path"] for module in leading_runtime_modules}
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/hosted_fedpro.py" in leading_paths
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/runtime_helper_surface_mixin.py" in leading_paths
    python2025_source_audit = snapshot["python2025_source_responsibility_audit"]
    python2025_backend_path = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025" / "backend.py"
    current_python2025_line_count = sum(1 for _ in python2025_backend_path.open(encoding="utf-8"))
    assert python2025_source_audit["audit_status"] == "python2025-source-responsibility-captured"
    assert python2025_source_audit["source_path"] == "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py"
    assert python2025_source_audit["source_line_count"] == current_python2025_line_count
    assert python2025_source_audit["shim_wrapper_path"] == (
        "packages/hla-backend-python2025/src/hla/backends/python2025/compatibility_wrapper.py"
    )
    assert python2025_source_audit["shim_wrapper_line_count"] == 63
    assert python2025_source_audit["extracted_runtime_module_count"] >= 34
    extracted_paths = {module["path"] for module in python2025_source_audit["extracted_runtime_modules"]}
    extracted_runtime_line_count = 0
    for relative_path in extracted_paths:
        with (ROOT / relative_path).open(encoding="utf-8") as handle:
            extracted_runtime_line_count += sum(1 for _ in handle)
    assert python2025_source_audit["extracted_runtime_module_line_count"] == extracted_runtime_line_count
    assert concentration_audit["extracted_runtime_module_line_count"] == extracted_runtime_line_count
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/attribute_policy.py" in extracted_paths
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/save_restore_lifecycle.py" in extracted_paths
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/support_services_runtime.py" in extracted_paths
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/time_management_runtime.py" in extracted_paths
    assert python2025_source_audit["ambassador_class"] == "Python2025RTIAmbassador"
    assert python2025_source_audit["ambassador_line_count"] <= 24
    assert python2025_source_audit["ambassador_method_count"] == 0
    assert python2025_source_audit["ambassador_method_line_count"] == 0
    assert python2025_source_audit["shim_wrapper_ambassador_class"] == "Shim2025RTIAmbassador"
    assert python2025_source_audit["shim_wrapper_ambassador_line_count"] == 2
    assert python2025_source_audit["family_count"] >= 5
    assert python2025_source_audit["largest_family"] in {"misc-support", "object-attribute-runtime"}
    assert python2025_source_audit["largest_family_line_count"] >= 70
    shim_families = {family["family"]: family for family in python2025_source_audit["families"]}
    assert shim_families["object-attribute-runtime"]["method_count"] >= 1
    assert shim_families["object-attribute-runtime"]["line_count"] >= 2
    assert shim_families["federation-management-runtime"]["method_count"] >= 2
    assert shim_families["federation-management-runtime"]["line_count"] >= 4
    assert shim_families["time-management-runtime"]["method_count"] >= 1
    assert shim_families["time-management-runtime"]["line_count"] >= 2
    assert shim_families["misc-support"]["method_count"] >= 7
    assert shim_families["misc-support"]["line_count"] >= 70
    assert "thin ambassador shell in hla-backend-python2025" in python2025_source_audit["current_assessment"]
    assert "catalog access, object lifecycle/update handling, attribute policy/scope, and callback delivery" in python2025_source_audit["current_assessment"]
    assert "shrink hla-backend-shim toward temporary import-compatibility scaffolding and wrapper-only responsibilities" in python2025_source_audit["extraction_use"]
    aggregation_audit = snapshot["slice_aggregation_pressure_audit"]
    assert aggregation_audit["audit_status"] == "slice-aggregation-pressure-captured"
    assert aggregation_audit["implemented_slice_count"] == 74
    assert aggregation_audit["aggregated_slice_count_ge_10_requirements"] == 10
    assert aggregation_audit["aggregated_slice_count_ge_10_requirements_runtime_backed"] == 3
    assert aggregation_audit["aggregated_slice_count_ge_20_requirements"] == 7
    assert aggregation_audit["aggregated_slice_count_ge_20_requirements_runtime_backed"] == 2
    assert aggregation_audit["largest_implemented_slices"][:5] == [
        {"slice_id": "2025-service-utilization-crosscheck", "requirement_count": 196, "runtime_backend_backed": False},
        {"slice_id": "2025-omt-extended-supported-subset", "requirement_count": 110, "runtime_backend_backed": False},
        {"slice_id": "2025-omt-xs-any-extension-tolerance", "requirement_count": 45, "runtime_backend_backed": False},
        {"slice_id": "2025-omt-schema-constraint-validation", "requirement_count": 29, "runtime_backend_backed": False},
        {"slice_id": "2025-omt-component-metadata-roundtrip", "requirement_count": 24, "runtime_backend_backed": False},
    ]
    assert aggregation_audit["largest_runtime_backed_aggregated_slices"] == [
        {"slice_id": "2025-ddm-default-attribute-policy", "requirement_count": 23, "runtime_backend_backed": True},
        {"slice_id": "2025-save-restore-lifecycle", "requirement_count": 20, "runtime_backend_backed": True},
        {"slice_id": "2025-directed-interaction-boundary", "requirement_count": 11, "runtime_backend_backed": True},
    ]
    assert "DDM/default-policy, save/restore, and directed-interaction slices now have explicit requirement-family maps" in aggregation_audit["current_assessment"]
    assert "leaf-level implemented slices" in aggregation_audit["current_assessment"]
    service_utilization_audit = snapshot["service_utilization_decomposition_audit"]
    assert service_utilization_audit["audit_status"] == "service-utilization-decomposition-captured"
    assert service_utilization_audit["slice_id"] == "2025-service-utilization-crosscheck"
    assert service_utilization_audit["requirement_count"] == 196
    assert service_utilization_audit["family_count"] == 11
    assert service_utilization_audit["all_service_utilization_rows_family_mapped"] is True
    assert service_utilization_audit["all_backing_fi_rows_traceable"] is True
    service_families = {family["family"]: family for family in service_utilization_audit["families"]}
    assert service_families["federation_management"]["service_count"] == 17
    assert service_families["federation_management"]["service_number_min"] == 1
    assert service_families["federation_management"]["service_number_max"] == 17
    assert service_families["save_restore"]["service_count"] == 17
    assert service_families["save_restore"]["service_number_min"] == 18
    assert service_families["save_restore"]["service_number_max"] == 34
    assert service_families["time_management"]["service_count"] == 25
    assert service_families["time_management"]["service_number_min"] == 101
    assert service_families["time_management"]["service_number_max"] == 125
    assert service_families["support_services"]["service_count"] == 55
    assert service_families["support_services"]["service_number_min"] == 138
    assert service_families["support_services"]["service_number_max"] == 192
    assert "HLA2025-OMT-SU-001" in service_families["federation_management"]["omt_requirement_ids"]
    assert "HLA2025-FI-SVC-001" in service_families["federation_management"]["fi_requirement_ids"]
    assert "2025-connect-and-federation-catalog-services" in service_families["federation_management"]["supporting_slice_ids"]
    assert "same Federate Interface service families used by the runtime proof audit" in service_utilization_audit["current_assessment"]
    omt_extended_audit = snapshot["omt_extended_subset_decomposition_audit"]
    assert omt_extended_audit["audit_status"] == "omt-extended-subset-decomposition-captured"
    assert omt_extended_audit["slice_id"] == "2025-omt-extended-supported-subset"
    assert omt_extended_audit["requirement_count"] == 110
    assert omt_extended_audit["family_count"] == 5
    assert omt_extended_audit["all_extended_subset_rows_family_mapped"] is True
    assert omt_extended_audit["unmapped_requirement_ids"] == []
    assert omt_extended_audit["unexpected_requirement_ids"] == []
    omt_families = {family["family"]: family for family in omt_extended_audit["families"]}
    assert omt_families["model-identification-and-taxonomy"]["requirement_count"] == 8
    assert omt_families["object-attribute-and-class-metadata"]["requirement_count"] == 33
    assert omt_families["interaction-parameter-and-routing-metadata"]["requirement_count"] == 36
    assert omt_families["datatype-table-roundtrip"]["requirement_count"] == 18
    assert omt_families["container-reference-and-table-sections"]["requirement_count"] == 15
    assert "HLA2025-OMT-COMP-001" in omt_families["model-identification-and-taxonomy"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-073" in omt_families["object-attribute-and-class-metadata"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-139" in omt_families["interaction-parameter-and-routing-metadata"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-188" in omt_families["datatype-table-roundtrip"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-223" in omt_families["container-reference-and-table-sections"]["requirement_ids"]
    assert all(family["all_requirements_in_slice"] is True for family in omt_extended_audit["families"])
    assert "one opaque requirement bundle" in omt_extended_audit["current_assessment"]
    omt_xs_any_audit = snapshot["omt_xs_any_extension_decomposition_audit"]
    assert omt_xs_any_audit["audit_status"] == "omt-xs-any-extension-decomposition-captured"
    assert omt_xs_any_audit["slice_id"] == "2025-omt-xs-any-extension-tolerance"
    assert omt_xs_any_audit["requirement_count"] == 45
    assert omt_xs_any_audit["family_count"] == 5
    assert omt_xs_any_audit["all_xs_any_extension_rows_family_mapped"] is True
    assert omt_xs_any_audit["unmapped_requirement_ids"] == []
    assert omt_xs_any_audit["unexpected_requirement_ids"] == []
    xs_any_families = {family["family"]: family for family in omt_xs_any_audit["families"]}
    assert xs_any_families["object-model-root-and-identity"]["requirement_count"] == 2
    assert xs_any_families["object-class-and-attribute-extension-points"]["requirement_count"] == 16
    assert xs_any_families["interaction-class-and-parameter-extension-points"]["requirement_count"] == 8
    assert xs_any_families["datatype-and-encoding-extension-points"]["requirement_count"] == 12
    assert xs_any_families["container-table-and-reference-extension-points"]["requirement_count"] == 7
    assert "HLA2025-OMT-COMP-006" in xs_any_families["object-model-root-and-identity"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-082" in xs_any_families["object-class-and-attribute-extension-points"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-134" in xs_any_families["interaction-class-and-parameter-extension-points"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-198" in xs_any_families["datatype-and-encoding-extension-points"]["requirement_ids"]
    assert "HLA2025-OMT-COMP-224" in xs_any_families["container-table-and-reference-extension-points"]["requirement_ids"]
    assert all(family["all_requirements_in_slice"] is True for family in omt_xs_any_audit["families"])
    assert "payload-preservation claim" in omt_xs_any_audit["current_assessment"]
    omt_schema_audit = snapshot["omt_schema_constraint_decomposition_audit"]
    assert omt_schema_audit["audit_status"] == "omt-schema-constraint-decomposition-captured"
    assert omt_schema_audit["slice_id"] == "2025-omt-schema-constraint-validation"
    assert omt_schema_audit["requirement_count"] == 29
    assert omt_schema_audit["family_count"] == 4
    assert omt_schema_audit["all_schema_constraint_rows_family_mapped"] is True
    assert omt_schema_audit["unmapped_requirement_ids"] == []
    assert omt_schema_audit["unexpected_requirement_ids"] == []
    schema_families = {family["family"]: family for family in omt_schema_audit["families"]}
    assert schema_families["xsd-key-constraints"]["requirement_count"] == 5
    assert schema_families["xsd-keyref-constraints"]["requirement_count"] == 5
    assert schema_families["xsd-unique-constraints"]["requirement_count"] == 4
    assert schema_families["enumeration-and-union-domain-constraints"]["requirement_count"] == 15
    assert "HLA2025-OMT-CV-001" in schema_families["xsd-key-constraints"]["requirement_ids"]
    assert "HLA2025-OMT-CV-010" in schema_families["xsd-keyref-constraints"]["requirement_ids"]
    assert "HLA2025-OMT-CV-014" in schema_families["xsd-unique-constraints"]["requirement_ids"]
    assert "HLA2025-OMT-CV-029" in schema_families["enumeration-and-union-domain-constraints"]["requirement_ids"]
    assert all(family["all_requirements_in_slice"] is True for family in omt_schema_audit["families"])
    assert "negative validator coverage" in omt_schema_audit["current_assessment"]
    save_restore_audit = snapshot["save_restore_decomposition_audit"]
    assert save_restore_audit["audit_status"] == "save-restore-decomposition-captured"
    assert save_restore_audit["slice_id"] == "2025-save-restore-lifecycle"
    assert save_restore_audit["requirement_count"] == 20
    assert save_restore_audit["proof_family_count"] == 5
    assert save_restore_audit["direct_family_count"] == 5
    assert save_restore_audit["hosted_family_count"] == 5
    assert [family["family"] for family in save_restore_audit["proof_families"]] == [
        "lifecycle-control",
        "shared-scenario-rollback",
        "routing-policy-rollback",
        "ownership-rollback",
        "time-window-and-time-state-rollback",
    ]
    assert save_restore_audit["proof_families"][0]["direct_tests"][0].endswith(
        "test_2025_provider_runs_federation_save_restore_lifecycle"
    )
    assert save_restore_audit["proof_families"][0]["direct_tests"][-1].endswith(
        "test_2025_provider_runs_restore_status_exception_scenario_via_compat_adapter"
    )
    assert save_restore_audit["proof_families"][0]["hosted_tests"][-1].endswith(
        "test_2025_transport_server_runs_restore_status_exception_scenario_over_fedpro_route"
    )
    assert save_restore_audit["proof_families"][1]["direct_tests"][0].endswith(
        "test_2025_primary_python_rti_runs_two_federate_suite_save_restore_scenario_without_wrapper_adapter"
    )
    assert save_restore_audit["proof_families"][1]["hosted_tests"][0].endswith(
        "test_2025_transport_server_runs_two_federate_suite_save_restore_scenario_over_fedpro_route"
    )
    assert save_restore_audit["proof_families"][2]["direct_tests"][2].endswith(
        "test_2025_provider_runs_transportation_type_restore_persistence_scenario_via_compat_adapter"
    )
    assert save_restore_audit["proof_families"][2]["hosted_tests"][2].endswith(
        "test_2025_transport_server_runs_transportation_type_restore_persistence_scenario_over_fedpro_route"
    )
    assert "lifecycle control, shared rollback scenarios, routing/policy rollback, ownership rollback" in save_restore_audit["current_assessment"]
    federation_management_audit = snapshot["federation_management_decomposition_audit"]
    assert federation_management_audit["audit_status"] == "federation-management-decomposition-captured"
    assert federation_management_audit["slice_id"] == "2025-federation-management-proof-families"
    assert federation_management_audit["slice_ids"] == [
        "2025-lifecycle-and-members",
        "2025-connection-lifecycle-services",
        "2025-connect-and-federation-catalog-services",
        "2025-federate-membership-and-resign-services",
        "2025-synchronization-point-services",
        "2025-save-restore-lifecycle",
    ]
    assert federation_management_audit["requirement_count"] == 40
    assert federation_management_audit["proof_family_count"] == 6
    assert federation_management_audit["direct_family_count"] == 6
    assert federation_management_audit["hosted_family_count"] == 6
    assert [family["family"] for family in federation_management_audit["proof_families"]] == [
        "connect-create-destroy-and-catalog-control",
        "join-membership-and-name-preconditions",
        "resign-disconnect-loss-and-member-cleanup",
        "synchronization-barriers-and-targeted-callbacks",
        "save-restore-lifecycle-control",
        "save-restore-participant-recovery-and-branching",
    ]
    assert federation_management_audit["proof_families"][0]["direct_tests"][-1].endswith(
        "test_2025_provider_rejects_invalid_join_fom_modules_and_destroy_while_joined"
    )
    assert federation_management_audit["proof_families"][2]["hosted_tests"][4].endswith(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
    )
    assert federation_management_audit["proof_families"][3]["hosted_tests"][-1].endswith(
        "test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema"
    )
    assert federation_management_audit["proof_families"][4]["direct_tests"][1].endswith(
        "test_2025_primary_python_rti_runs_two_federate_suite_save_restore_scenario_without_wrapper_adapter"
    )
    assert federation_management_audit["proof_families"][4]["direct_tests"][3].endswith(
        "test_2025_primary_python_rti_runs_save_restore_queued_callback_scenario_without_wrapper_adapter"
    )
    assert federation_management_audit["proof_families"][4]["direct_tests"][4].endswith(
        "test_2025_primary_python_rti_runs_scheduled_save_restore_time_state_scenario_without_wrapper_adapter"
    )
    assert federation_management_audit["proof_families"][4]["hosted_tests"][1].endswith(
        "test_2025_transport_server_runs_two_federate_suite_save_restore_scenario_over_fedpro_route"
    )
    assert federation_management_audit["proof_families"][5]["hosted_tests"][1].endswith(
        "test_2025_transport_server_completes_restore_after_peer_disconnect_over_fedpro_schema"
    )
    assert "connect/create/catalog control, join or membership reporting" in federation_management_audit["current_assessment"]
    support_services_audit = snapshot["support_services_decomposition_audit"]
    assert support_services_audit["audit_status"] == "support-services-decomposition-captured"
    assert support_services_audit["slice_id"] == "2025-support-services-proof-families"
    assert support_services_audit["slice_ids"] == [
        "2025-switch-set-get-model",
        "2025-single-name-reservation-services",
        "2025-multi-name-reservation-services",
        "2025-support-federate-and-object-identity-lookups",
        "2025-support-attribute-interaction-catalog-lookups",
        "2025-support-policy-update-and-transport-lookups",
        "2025-support-interaction-dimension-and-range-lookups",
        "2025-support-handle-normalization-and-region-introspection",
        "2025-support-advisory-and-reporting-state-inquiries",
        "2025-support-runtime-policy-state-inquiries",
        "2025-support-advisory-and-reporting-state-controls",
        "2025-support-runtime-policy-state-controls",
    ]
    assert support_services_audit["requirement_count"] == 59
    assert support_services_audit["proof_family_count"] == 5
    assert support_services_audit["direct_family_count"] == 5
    assert support_services_audit["hosted_family_count"] == 5
    assert [family["family"] for family in support_services_audit["proof_families"]] == [
        "name-reservation-and-release-flows",
        "identity-catalog-and-handle-normalization-lookups",
        "transport-order-update-dimension-and-range-lookups",
        "switch-inquiry-and-control-model",
        "factory-decode-and-hosted-support-seam",
    ]
    assert support_services_audit["proof_families"][0]["hosted_tests"][2].endswith(
        "test_2025_transport_server_runs_shared_name_reservation_scenario_over_fedpro_route"
    )
    assert support_services_audit["proof_families"][1]["direct_tests"][1].endswith(
        "test_2025_provider_accepts_support_lookup_aliases_and_rejects_invalid_values"
    )
    assert support_services_audit["proof_families"][3]["direct_tests"][0].endswith(
        "test_2025_provider_supports_explicit_switch_inquiry_and_control_model"
    )
    assert support_services_audit["proof_families"][4]["hosted_tests"][-1].endswith(
        "test_2025_transport_server_drains_multiple_callbacks_in_order_over_fedpro_schema"
    )
    assert "name reservation and release flows, identity/catalog normalization lookups" in support_services_audit["current_assessment"]
    object_management_audit = snapshot["object_management_decomposition_audit"]
    assert object_management_audit["audit_status"] == "object-management-decomposition-captured"
    assert object_management_audit["slice_id"] == "2025-object-management-proof-families"
    assert object_management_audit["slice_ids"] == [
        "2025-basic-object-exchange",
        "2025-declaration-publication-services",
        "2025-declaration-subscription-services",
        "2025-declaration-relevance-advisory-callbacks",
        "2025-object-delete-remove-flows",
        "2025-object-attribute-update-request-callbacks",
        "2025-object-scope-advisory-callbacks",
        "2025-object-update-rate-advisory-callbacks",
        "2025-object-attribute-transport-callbacks",
        "2025-object-interaction-transport-callbacks",
        "2025-directed-interaction-boundary",
        "2025-ddm-default-attribute-policy",
    ]
    assert object_management_audit["requirement_count"] == 67
    assert object_management_audit["proof_family_count"] == 7
    assert object_management_audit["direct_family_count"] == 7
    assert object_management_audit["hosted_family_count"] == 7
    assert [family["family"] for family in object_management_audit["proof_families"]] == [
        "declaration-and-basic-exchange-gating",
        "deletion-and-local-known-state-lifecycle",
        "attribute-value-update-request-routing",
        "advisory-and-update-rate-callbacks",
        "transportation-query-and-policy-state",
        "object-region-scope-and-passive-alias-routing",
        "directed-and-directed-ddm-interaction-routing",
    ]
    assert object_management_audit["proof_families"][0]["direct_tests"][-1].endswith(
        "test_2025_primary_python_rti_runs_passive_full_declaration_scenario_without_wrapper_adapter"
    )
    assert object_management_audit["proof_families"][1]["hosted_tests"][4].endswith(
        "test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema"
    )
    assert object_management_audit["proof_families"][4]["direct_tests"][3].endswith(
        "test_2025_provider_restores_transportation_type_state_via_compat_adapter"
    )
    assert object_management_audit["proof_families"][6]["hosted_tests"][1].endswith(
        "test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice"
    )
    assert "declaration/exchange gating, deletion and local-known-state lifecycle" in object_management_audit["current_assessment"]
    ownership_audit = snapshot["ownership_decomposition_audit"]
    assert ownership_audit["audit_status"] == "ownership-decomposition-captured"
    assert ownership_audit["slice_id"] == "2025-ownership-proof-families"
    assert ownership_audit["slice_ids"] == [
        "2025-ownership-divestiture-confirmation-flows",
        "2025-ownership-release-and-if-wanted-flows",
        "2025-ownership-acquisition-assumption-flows",
        "2025-ownership-acquisition-availability-cancellation-flows",
        "2025-ownership-query-and-resign-policies",
        "2025-save-restore-lifecycle",
    ]
    assert ownership_audit["requirement_count"] == 18
    assert ownership_audit["proof_family_count"] == 6
    assert ownership_audit["direct_family_count"] == 6
    assert ownership_audit["hosted_family_count"] == 6
    assert [family["family"] for family in ownership_audit["proof_families"]] == [
        "divestiture-and-confirmation-flows",
        "release-and-if-wanted-flows",
        "acquisition-assumption-and-notification",
        "acquisition-availability-and-cancellation",
        "query-visibility-and-resign-policies",
        "rollback-and-restore-state",
    ]
    assert ownership_audit["proof_families"][0]["direct_tests"][1].endswith(
        "test_2025_provider_runs_negotiated_attribute_ownership_scenario_via_compat_adapter"
    )
    assert ownership_audit["proof_families"][1]["hosted_tests"][2].endswith(
        "test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route"
    )
    assert ownership_audit["proof_families"][2]["hosted_tests"][2].endswith(
        "test_2025_transport_server_routes_mom_transport_and_ownership_actions_to_observable_runtime_effects_over_fedpro_schema"
    )
    assert ownership_audit["proof_families"][5]["direct_tests"][-1].endswith(
        "test_2025_primary_runtime_factory_restores_cross_federate_attribute_owner_visibility"
    )
    assert "divestiture/confirmation, release/if-wanted, acquisition/assumption" in ownership_audit["current_assessment"]
    directed_audit = snapshot["directed_interaction_decomposition_audit"]
    assert directed_audit["audit_status"] == "directed-interaction-decomposition-captured"
    assert directed_audit["slice_id"] == "2025-directed-interaction-boundary"
    assert directed_audit["requirement_count"] == 11
    assert directed_audit["proof_family_count"] == 5
    assert directed_audit["direct_family_count"] == 5
    assert directed_audit["hosted_family_count"] == 5
    assert [family["family"] for family in directed_audit["proof_families"]] == [
        "base-routing-and-callback-delivery",
        "timestamped-delivery-and-retraction",
        "ddm-overlap-filtering",
        "selective-set-and-publication-isolation",
        "restore-routing-and-stale-queue-cleanup",
    ]
    assert directed_audit["proof_families"][0]["direct_tests"] == [
        "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_to_object_class_subscribers",
        "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_only_to_subscribers",
    ]
    assert directed_audit["proof_families"][4]["hosted_tests"][1].endswith(
        "test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema"
    )
    assert "base routing/callback delivery, timestamped delivery and retraction, DDM overlap filtering" in directed_audit["current_assessment"]
    directed_requirement_audit = snapshot["directed_interaction_requirement_family_audit"]
    assert directed_requirement_audit["audit_status"] == "directed-interaction-requirement-family-map-captured"
    assert directed_requirement_audit["slice_id"] == "2025-directed-interaction-boundary"
    assert directed_requirement_audit["requirement_count"] == 11
    assert directed_requirement_audit["family_count"] == 5
    assert directed_requirement_audit["all_directed_interaction_rows_family_mapped"] is True
    assert directed_requirement_audit["unmapped_requirement_ids"] == []
    assert directed_requirement_audit["unexpected_requirement_ids"] == []
    directed_families = {family["family"]: family for family in directed_requirement_audit["families"]}
    assert directed_families["declaration-publication-control"]["requirement_ids"] == [
        "HLA2025-FI-SVC-039",
        "HLA2025-FI-SVC-040",
    ]
    assert directed_families["declaration-subscription-control"]["requirement_ids"] == [
        "HLA2025-FI-SVC-045",
        "HLA2025-FI-SVC-046",
    ]
    assert directed_families["send-receive-routing-and-hla-surface"]["requirement_ids"] == [
        "HLA2025-FI-SVC-063",
        "HLA2025-FI-SVC-064",
        "HLA2025-FR-003",
        "HLA2025-FR-004",
    ]
    assert directed_families["directed-interaction-delta-rows"]["requirement_ids"] == [
        "HLA2025-MOD-007",
        "HLA2025-NEW-001",
    ]
    assert directed_families["service-group-matrix-traceability"]["requirement_ids"] == ["HLA2025-FI-001"]
    assert all(family["all_requirements_in_slice"] is True for family in directed_requirement_audit["families"])
    assert "explicit requirement-family map" in directed_requirement_audit["current_assessment"]
    assert "standalone implemented-evidence slice" in directed_requirement_audit["residual_boundary"]
    ddm_audit = snapshot["ddm_default_policy_decomposition_audit"]
    assert ddm_audit["audit_status"] == "ddm-default-policy-decomposition-captured"
    assert ddm_audit["slice_id"] == "2025-ddm-default-attribute-policy"
    assert ddm_audit["requirement_count"] == 23
    assert ddm_audit["proof_family_count"] == 6
    assert ddm_audit["direct_family_count"] == 6
    assert ddm_audit["hosted_family_count"] == 6
    assert [family["family"] for family in ddm_audit["proof_families"]] == [
        "lookup-and-default-policy-control",
        "object-region-routing-and-scope-advisories",
        "interaction-region-routing",
        "directed-ddm-routing",
        "passive-alias-and-compat-scenarios",
        "ddm-restore-and-disconnect-cleanup",
    ]
    assert ddm_audit["proof_families"][0]["direct_tests"] == [
        "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_fom_backed_ddm_lookup_and_default_attribute_policy",
    ]
    assert ddm_audit["proof_families"][4]["direct_tests"][0].endswith(
        "test_2025_primary_python_rti_runs_two_federate_suite_ddm_scenario_without_wrapper_adapter"
    )
    assert ddm_audit["proof_families"][5]["hosted_tests"][1].endswith(
        "test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema"
    )
    assert "lookup/default-policy control, object-region routing and scope advisories" in ddm_audit["current_assessment"]
    route_backing_audit = snapshot["wrapper_boundary_family_route_backing_audit"]
    assert snapshot["shim_pressure_family_route_backing_audit"] == route_backing_audit
    assert route_backing_audit["audit_status"] == "wrapper-boundary-family-route-backing-captured"
    assert route_backing_audit["family_count"] == 22
    assert route_backing_audit["fully_route_backed_family_count"] == 22
    assert route_backing_audit["all_families_route_backed_across_current_python_lanes"] is True
    assert route_backing_audit["families"][:4] == [
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "lifecycle-control",
            "direct_test_count": 9,
            "hosted_test_count": 9,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "shared-scenario-rollback",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "routing-policy-rollback",
            "direct_test_count": 7,
            "hosted_test_count": 7,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "ownership-rollback",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
        },
    ]
    assert route_backing_audit["families"][5:11] == [
        {
            "slice_id": "2025-ownership-proof-families",
            "family": "divestiture-and-confirmation-flows",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-ownership-proof-families",
            "family": "release-and-if-wanted-flows",
            "direct_test_count": 3,
            "hosted_test_count": 3,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-ownership-proof-families",
            "family": "acquisition-assumption-and-notification",
            "direct_test_count": 3,
            "hosted_test_count": 3,
            "route_backed_across_current_python_lanes": True,
        },
            {
                "slice_id": "2025-ownership-proof-families",
                "family": "acquisition-availability-and-cancellation",
                "direct_test_count": 3,
                "hosted_test_count": 3,
                "route_backed_across_current_python_lanes": True,
            },
        {
            "slice_id": "2025-ownership-proof-families",
            "family": "query-visibility-and-resign-policies",
            "direct_test_count": 3,
            "hosted_test_count": 3,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-ownership-proof-families",
            "family": "rollback-and-restore-state",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
        },
    ]
    assert "Every currently named family across save/restore, ownership, directed interaction, and DDM/default-policy has both direct python2025 proof and hosted FedPro proof" in route_backing_audit["current_assessment"]
    asymmetry_audit = snapshot["wrapper_boundary_family_asymmetry_audit"]
    assert snapshot["shim_pressure_family_asymmetry_audit"] == asymmetry_audit
    assert asymmetry_audit["audit_status"] == "wrapper-boundary-family-asymmetry-captured"
    assert asymmetry_audit["family_count"] == 22
    assert asymmetry_audit["by_balance"] == {
        "balanced": 22,
    }
    assert asymmetry_audit["families"][:5] == [
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "lifecycle-control",
            "direct_test_count": 9,
            "hosted_test_count": 9,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "shared-scenario-rollback",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "routing-policy-rollback",
            "direct_test_count": 7,
            "hosted_test_count": 7,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "ownership-rollback",
            "direct_test_count": 4,
            "hosted_test_count": 4,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "time-window-and-time-state-rollback",
            "direct_test_count": 5,
            "hosted_test_count": 5,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
    ]
    assert all(family["balance"] == "balanced" for family in asymmetry_audit["families"])
    assert "are now symmetric at the named proof-family level" in asymmetry_audit["current_assessment"]
    assert "remaining work is no longer family-count parity" in asymmetry_audit["current_assessment"]
    assert "deeper behavioral expansion, stronger evidence quality, and architectural judgment" in asymmetry_audit["current_assessment"]
    assert "current-package pressure families" in asymmetry_audit["current_assessment"]
    assert "remain wrapper-fronted" not in asymmetry_audit["current_assessment"]
    assert "remaining compatibility-wrapper seam" in asymmetry_audit["current_assessment"]
    coherence_audit = snapshot["current_lane_coherence_audit"]
    assert coherence_audit["audit_status"] == "current-lane-coherence-captured"
    assert coherence_audit["coherence_claim"] == "bounded-working-RTI-surface"
    assert coherence_audit["ready_for_current_lane_coherent_working_surface_claim"] is True
    assert coherence_audit["ready_for_permanent_no-split_architecture_claim"] is False
    assert coherence_audit["major_pressure_slice_count"] == 3
    assert coherence_audit["major_pressure_slices"] == [
        "2025-ddm-default-attribute-policy",
        "2025-directed-interaction-boundary",
        "2025-save-restore-lifecycle",
    ]
    assert coherence_audit["python2025_backend_concentration_is_material"] is False
    assert coherence_audit["shim_backend_concentration_is_material"] is False
    assert coherence_audit["all_pressure_families_route_backed_across_current_python_lanes"] is True
    assert "defensible coherence story" in coherence_audit["current_assessment"]
    assert "primary 2025 Python RTI lane" in coherence_audit["current_assessment"]
    assert any("public hla-backend-python2025/backend.py shell is now thin" in item for item in coherence_audit["residual_blockers"])
    assert any("extracted runtime/state/surface split still needs continued discipline" in item for item in coherence_audit["residual_blockers"])
    current_lane_statement = snapshot["current_lane_working_surface_statement"]
    assert current_lane_statement["statement_status"] == "current-lane-working-surface-statement"
    assert current_lane_statement["ready"] is True
    assert "coherent bounded working Python RTI surface" in current_lane_statement["statement"]
    assert "primary 2025 Python RTI lane" in current_lane_statement["statement"]
    assert "main full Python 2025 RTI implementation now runs from hla-backend-python2025 while hla-backend-shim is retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in current_lane_statement["statement"]
    assert "route-parity matrix now serves as the scenario-family ledger for federation, object, ownership, DDM, time, save/restore, MOM, and support-services evidence" in current_lane_statement["statement"]
    assert "Java and C++ shim/binding packages remain segregated supporting lanes rather than alternate Python RTIs" in current_lane_statement["statement"]
    assert "main current-package pressure families are route-backed" in current_lane_statement["statement"]
    assert "primary 2025 Python RTI lane" in current_lane_statement["current_assessment"]
    assert "treat it as the main full implementation rather than as a mere adapter layer" in current_lane_statement["current_assessment"]
    assert "use the route-parity matrix as the scenario-family ledger behind that claim" in current_lane_statement["current_assessment"]
    assert len(current_lane_statement["non_claims"]) == 4
    assert any("full requirement-by-requirement IEEE 1516.1-2025 conformance claim" in item for item in current_lane_statement["non_claims"])
    main_impl_claim = snapshot["main_python2025_implementation_claim_audit"]
    assert main_impl_claim["audit_status"] == "main-python2025-implementation-claim-captured"
    assert main_impl_claim["claim_shape"] == "bounded-main-python2025-rti-implementation"
    assert main_impl_claim["ready_for_main_python2025_implementation_claim"] is True
    assert main_impl_claim["ready_for_full_2025_conformance_claim"] is False
    assert main_impl_claim["implementation_owner"] == "hla-backend-python2025"
    assert main_impl_claim["compatibility_wrapper"] == "hla-backend-shim"
    assert main_impl_claim["default_operator_lane"] == "python-main-2025"
    assert main_impl_claim["hosted_extension_lane"] == "python-routes-2025"
    assert "hla-backend-python2025 is the implementation owner for the real executable 2025 Python RTI surface" in main_impl_claim["claim"]
    assert "direct plus hosted Python 2025 proof lanes are sufficiently green" in main_impl_claim["claim"]
    assert len(main_impl_claim["promotion_basis"]) == 5
    assert any("verify-main-2025" in item for item in main_impl_claim["promotion_basis"])
    assert any("All tracked objective dimensions are bounded-ready" in item for item in main_impl_claim["promotion_basis"])
    assert len(main_impl_claim["non_claims"]) == 4
    assert any("not a full IEEE 1516.1-2025 conformance claim" in item for item in main_impl_claim["non_claims"])
    assert any("hosted FedPro route into a second full RTI implementation owner" in item for item in main_impl_claim["non_claims"])
    assert any("artifact/runtime-capability evidence" in item for item in main_impl_claim["full_conformance_blockers"])
    assert any("hosted FedPro route remains a bounded runtime slice" in item for item in main_impl_claim["full_conformance_blockers"])
    assert "separates the two judgments cleanly" in main_impl_claim["current_assessment"]
    assert "main python2025 RTI implementation claim is ready" in main_impl_claim["current_assessment"]
    blocker_partition = snapshot["full_claim_blocker_partition_audit"]
    assert blocker_partition["audit_status"] == "full-claim-blocker-partition-captured"
    assert blocker_partition["full_claim_blocker_count"] == 4
    assert blocker_partition["partitioned_blocker_count"] == 4
    assert blocker_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert blocker_partition["boundary_only_blocker_count"] == 4
    assert blocker_partition["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True
    assert blocker_partition["blocker_rows"] == [
        {
            "blocker": "omt_xs_any_extension_boundary",
            "classification": "external-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "bounded OMT extension-payload preservation rather than arbitrary third-party extension execution semantics"
            ),
        },
        {
            "blocker": "standard_java_cpp_binding_behavior_gap",
            "classification": "external-binding-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "Java/C++ rows remain artifact/runtime-capability binding evidence rather than exhaustive behavior conformance"
            ),
        },
        {
            "blocker": "hosted_fedpro_full_conformance_gap",
            "classification": "external-hosted-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or cross-binding pass"
            ),
        },
        {
            "blocker": "duplicate_umbrella_row_granularity_gap",
            "classification": "row-granularity-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "duplicate/umbrella rows remain normalization aids instead of direct one-row conformance assertions"
            ),
        },
    ]
    assert "all sit outside direct main-lane python2025 runtime completeness" in blocker_partition["current_assessment"]
    assert "missing core executable behavior in hla-backend-python2025" in blocker_partition["current_assessment"]
    assert "does not convert those external boundaries into a full 2025 conformance pass" in blocker_partition["residual_boundary"]
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    assert implementation_lane_audit["audit_status"] == "current-lane-architecture-captured"
    assert implementation_lane_audit["current_2025_lane"] == {
        "backend_package": "hla-backend-python2025",
        "plugin_family": "python-rti-2025",
        "supports": ["rti1516_2025"],
        "role": "main full Python 2025 RTI implementation lane (owned by hla-backend-python2025 with hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support)",
        "spec_package": "hla-rti1516-2025",
    }
    assert implementation_lane_audit["compatibility_wrapper_lane"] == {
        "backend_package": "hla-backend-shim",
        "status": "compatibility-maintained",
        "role": "compatibility-wrapper",
        "counts_as_python_2025_rti": False,
        "delegates_runtime_semantics_to": "hla-backend-python2025",
    }
    assert implementation_lane_audit["reference_2010_lane"] == {
        "backend_package": "hla-backend-inmemory",
        "plugin_family": "inmemory",
        "supports": ["rti1516e"],
        "role": "2010 pure Python RTI backend",
    }
    assert implementation_lane_audit["dedicated_2025_backend_package_present"] is True
    assert implementation_lane_audit["ready_for_current_lane_promotion_as_working_surface"] is True
    assert implementation_lane_audit["ready_for_permanent_no-split_decision"] is False
    assert implementation_lane_audit["clean_extraction_still_optional"] is True
    backend_scan = implementation_lane_audit["backend_package_scan"]
    assert backend_scan["backend_package_dirs"] == [
        "hla-backend-certi",
        "hla-backend-common",
        "hla-backend-cpp-shim",
        "hla-backend-inmemory",
        "hla-backend-python2025",
        "hla-backend-shim",
    ]
    assert backend_scan["backend_package_count"] == 6
    assert backend_scan["dedicated_python_2025_backend_candidates"] == [
        {
            "package": "hla-backend-python2025",
            "plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "name": "python2025",
            "family": "python-rti-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert backend_scan["dedicated_python_2025_legacy_package_delegation_violations"] == []
    assert backend_scan["dedicated_python_2025_candidates_cleanly_separated"] is True
    rti2025_plugins = {
        (record["package"], record["name"], record["family"])
        for record in backend_scan["rti1516_2025_plugin_records"]
    }
    assert ("hla-backend-python2025", "python2025", "python-rti-2025") in rti2025_plugins
    assert ("hla-backend-shim", "shim", "shim") not in rti2025_plugins
    assert ("hla-backend-cpp-shim", "cpp-standard-2025-pybind", "standard/cpp") in rti2025_plugins
    assert ("hla-backend-inmemory", "inmemory", "inmemory") not in rti2025_plugins
    hosted_identity = implementation_lane_audit["hosted_runtime_identity_evidence"]
    assert hosted_identity == {
        "audit_status": "direct-server-client-identity-aligned",
        "route": "python-2025-fedpro-grpc",
        "claim": (
            "The hosted 2025 FedPro route is explicitly evidenced as a route variant over "
            "hla-backend-python2025 rather than a separate shim or RTI family."
        ),
        "evidence_tests": [
            "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_reports_python2025_main_lane_identity",
            "tests/test_rti1516_2025_python2025_runtime.py::test_dedicated_python2025_backend_is_discoverable_and_executable",
        ],
        "direct_runtime_report": {
            "backend_name": "python2025-rti",
            "backend_kind": "python/2025",
            "runtime_provider": "python2025",
            "implementation_lane": "hla-backend-python2025",
            "counts_as_python_2025_rti": True,
        },
        "hosted_server_report": {
            "runtime_provider": "python2025",
            "implementation_lane": "hla-backend-python2025",
            "counts_as_python_2025_rti": True,
            "wrapper_only": False,
            "spec": "rti1516_2025",
            "transport_kind": "grpc",
        },
        "hosted_client_report": {
            "runtime_provider": "python2025",
            "implementation_lane": "hla-backend-python2025",
            "counts_as_python_2025_rti": True,
            "wrapper_only": False,
            "spec": "rti1516_2025",
            "transport_kind": "grpc",
            "route_family": "fedpro",
        },
        "current_assessment": (
            "Hosted-client and hosted-server capability surfaces now agree with the direct 2025 ambassador "
            "that python-2025-fedpro-grpc is a route variant over the primary python2025 RTI lane in "
            "hla-backend-python2025 rather than a wrapper-defined implementation family."
        ),
    }
    hosted_factory_boundary = implementation_lane_audit["hosted_factory_boundary_evidence"]
    assert hosted_factory_boundary["audit_status"] == "factory-boundary-explicit"
    assert hosted_factory_boundary["supported_hosted_creation_surface"] == (
        "start_2025_grpc_server(...) plus GrpcTransport(..., schema='rti1516_2025') plus "
        "create_rti_ambassador(backend='python2025'|'python-2025'|'python-2025-backend', "
        "transport={'kind': 'grpc', ...})"
    )
    assert hosted_factory_boundary["unsupported_factory_surfaces"] == [
        "create_rti_ambassador(backend='shim', transport=...)",
    ]
    assert "supported runtime aliases now accept transport=..." in hosted_factory_boundary["current_policy"]
    assert "legacy shim provider spelling is no longer part of the supported public backend-selection surface" in hosted_factory_boundary["current_policy"]
    assert "direct federation listing/member-report slice" in hosted_factory_boundary["current_policy"]
    assert "direct MOM request/report slice" in hosted_factory_boundary["current_policy"]
    assert "direct MOM object/ownership service slice" in hosted_factory_boundary["current_policy"]
    assert "direct timestamped delivery/retraction slice" in hosted_factory_boundary["current_policy"]
    assert "direct directed-interaction slice" in hosted_factory_boundary["current_policy"]
    assert "direct callback-backlog disconnect/rejoin slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore-control negative slice" in hosted_factory_boundary["current_policy"]
    assert "direct local-delete restore slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-callback restore cleanup slice" in hosted_factory_boundary["current_policy"]
    assert "direct timed-remove restore cleanup slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-object restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-interaction restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct directed-DDM restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore time/switch-control slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore lookahead/queued-TSO slice" in hosted_factory_boundary["current_policy"]
    assert "direct object-exchange slice" in hosted_factory_boundary["current_policy"]
    assert "direct ownership slice" in hosted_factory_boundary["current_policy"]
    assert hosted_factory_boundary["evidence_tests"] == [
        "tests/test_python_api_spec.py::test_runtime_backend_listing_exposes_python2025_as_primary_2025_lane",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_python2025_aliases_and_keeps_primary_identity",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_legacy_shim_provider_name",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_hosted_transport_on_python2025_aliases",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_hosted_transport_on_legacy_shim_provider",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_accepts_hosted_transport_creation_on_python2025_lane",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_legacy_shim_provider_name",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_transport_route_creates_hosted_python2025_ambassador",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_restore_control_negative_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_local_delete_restore_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_timed_remove_and_preserves_post_restore_remove_routing",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_object_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_interaction_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_directed_ddm_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_time_and_switch_control_state_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_lookahead_and_redelivers_presave_queued_tso",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_federation_management_service_interactions",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_request_report_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_object_and_ownership_service_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_shared_support_factory_and_decode_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_drops_disconnected_callback_backlog_before_reconnect",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_object_exchange_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_timestamped_delivery_and_retraction_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_ownership_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_inflight_ownership_state",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_cross_federate_attribute_owner_visibility",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_unknown_backend_specific_options",
        "tests/test_hla_factory_composition.py::test_hla_factory_registry_strips_composition_only_options_before_2025_backend_creation",
        "tests/test_hla_factory_composition.py::test_2025_direct_factory_rejects_composition_only_options_without_hla_factory_layer",
        "tests/requirements/test_2025_python_rti_backend_audit.py::test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary",
    ]
    assert implementation_lane_audit["package_owned_shared_scenario_evidence"] == {
        "adapter_class": "hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter",
        "audit_status": "package-owned-target-radar-2025-path-captured",
        "claim": (
            "The shared Target/Radar 2025 execution seam is now owned by the hla-fom-target-radar package, "
            "where one package-owned compatibility adapter wraps the primary python2025 backend lane without "
            "moving implementation ownership back into hla-backend-shim."
        ),
        "current_assessment": (
            "The README-advertised Target/Radar python2025 example path is now executable under package-owned "
            "2025 adapter coverage. The legacy shim package is no longer treated as a backend-selection route, "
            "and the same package-owned adapter now also proves that the factory-hosted python2025 FedPro route can execute "
            "the shared Target/Radar example scenario plus the shared future-exclusion, output-delivery, "
            "consumer-order, integrated lookahead-processing-window gauntlet, restore-state, restore-output-resume, "
            "and pipeline-resume scenarios without falling back to shim-owned semantics or raw transport-only wrappers."
        ),
        "evidence_tests": [
            "tests/scenarios/test_target_radar_scenario.py::test_target_radar_example_supports_2025_backends",
            "tests/test_fom_target_radar_split_package.py::test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter",
            "tests/test_fom_target_radar_split_package.py::test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_target_radar_shared_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
        ],
        "example_entrypoint": "python examples/target_radar_simulation.py --backend python2025 --steps 5",
        "python2025_runtime_report": {
            "backend_kind": "python/2025",
            "counts_as_python_2025_rti": True,
            "implementation_lane": "hla-backend-python2025",
            "wrapper_only": False,
        },
        "scenario_package": "hla-fom-target-radar",
        "shared_route": "target-radar-shared-scenario",
        "shim_runtime_report": {
            "backend_kind": "shim/2025",
            "counts_as_python_2025_rti": False,
            "implementation_lane": "hla-backend-python2025",
            "wrapper_only": True,
        },
        "supported_backend_names": [
            "python2025",
            "python-2025",
            "python-2025-backend",
        ],
    }
    assert "hosted FedPro route is a route variant" in implementation_lane_audit["current_assessment"]
    assert "main full Python 2025 RTI implementation now runs from hla-backend-python2025" in implementation_lane_audit["current_assessment"]
    assert "hla-backend-shim remains as a compatibility wrapper over that runtime" not in implementation_lane_audit["current_assessment"]
    assert "temporary import-compatibility scaffolding" in implementation_lane_audit["current_assessment"]
    assert "continuing to narrow hla-backend-shim toward temporary import-compatibility scaffolding and wrapper-only responsibilities" in implementation_lane_audit["extraction_boundary"]
    assert implementation_lane_audit["evidence_anchors"] == [
        "README.md",
        "docs/architecture.md",
        "docs/documentation_hierarchy.md",
        "docs/package_layout.md",
        "docs/test_surface.md",
        "docs/workspace_layout.md",
        "docs/rti_options_and_test_matrix.md",
        "docs/verification/time_model_compliance.md",
        "docs/verification/verification_plan.md",
        "docs/backend_route_inventory.md",
        "docs/backend_route_inventory_remote.md",
        "packages/hla-backend-python2025/pyproject.toml",
        "packages/hla-backend-python2025/README.md",
        "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
        "packages/hla-backend-shim/pyproject.toml",
        "packages/hla-backend-shim/README.md",
        "packages/hla-backend-shim/src/hla/backends/shim/plugin.py",
        "packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py",
        "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_factory.py",
        "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_2025_adapter.py",
        "examples/target_radar_simulation.py",
        "docs/plans/2025_python_rti_backend_audit.md",
        "docs/python_rti_backend.md",
    ]
    proof_lane_audit = snapshot["python2025_proof_lane_audit"]
    assert proof_lane_audit["audit_status"] == "python2025-proof-lanes-captured"
    assert proof_lane_audit["ready_for_main_implementation_operator_lane_claim"] is True
    assert proof_lane_audit["default_direct_lane"] == {
        "lane_id": "python-main-2025",
        "title": "Python 2025 main-surface lane",
        "owner_command": ["./tools/python", "verify-main-2025"],
        "estimated_cost": "medium",
        "docs": [
            "docs/python_rti_backend.md",
            "docs/test_surface.md",
            "docs/local_verification_commands.md",
            "docs/python_rti_reading_map.md",
        ],
        "preflight_kind": "always-ready",
        "description": (
            "Primary python2025 main-surface verification lane for direct runtime proofs across time, save/restore, "
            "ownership, callbacks, support services, MOM behavior, and OMT validation/parsing evidence."
        ),
    }
    assert proof_lane_audit["hosted_extension_lane"] == {
        "lane_id": "python-routes-2025",
        "title": "Hosted Python 2025 route lane",
        "owner_command": ["./tools/python", "verify-routes-2025"],
        "estimated_cost": "medium",
        "docs": [
            "docs/networked_rti_python.md",
            "docs/test_surface.md",
            "docs/local_verification_commands.md",
            "docs/plans/spec2025_route_parity_matrix.md",
        ],
        "preflight_kind": "aggregate",
        "description": (
            "python2025 plus bounded FedPro 2025 hosted-route verification lane for direct time-window, save/restore, "
            "ownership, callback, support-service, and MOM proofs, transport-route behavior, route-parity artifacts, "
            "and the package-owned Target/Radar example path."
        ),
    }
    assert "./tools/python verify-main-2025 as the default direct proof lane" in proof_lane_audit["shared_claim"]
    assert "./tools/python verify-routes-2025 as the bounded hosted FedPro extension" in proof_lane_audit["shared_claim"]
    assert proof_lane_audit["current_operator_runs"] == [
        {
            "lane_id": "python-main-2025",
            "command": "./tools/python verify-main-2025",
            "result": "324 passed across wrapper subcommands plus Target/Radar example",
            "scope": (
                "current-tree direct python2025 package-boundary, federation/object/DDM, support/ownership/MOM, "
                "time-window, save/restore, callback, OMT, and example-scenario proof lane"
            ),
        },
        {
            "lane_id": "python-routes-2025",
            "command": "./tools/python verify-routes-2025",
            "result": "434 passed across direct-plus-hosted wrapper subcommands plus finish-line bundle and Target/Radar example",
            "scope": (
                "current-tree direct python2025 plus bounded hosted FedPro route verification lane, including "
                "transport suite, route-parity bundle, finish-line artifact generation, and package-owned example replay"
            ),
        },
    ]
    assert proof_lane_audit["evidence_anchors"] == [
        "testing/test_surface_manifest.json",
        "tools/python",
        "docs/test_surface.md",
        "README.md",
    ]
    assert "one current-tree green execution of both canonical wrapper commands" in proof_lane_audit["residual_boundary"]
    assert "does not replace the need to keep those proof lanes green as the tree changes" in proof_lane_audit["residual_boundary"]
    vendor_time_audit = snapshot["time_window_vendor_parity_audit"]
    assert vendor_time_audit["audit_status"] == "time-window-vendor-parity-captured"
    assert vendor_time_audit["route_count"] == 3
    assert vendor_time_audit["trial_pitch_safe_route_count"] == 2
    assert vendor_time_audit["trial_pitch_safe_route_ids"] == [
        "time-window-future-exclusion",
        "time-window-restore-state",
    ]
    assert vendor_time_audit["trial_pitch_unsafe_route_ids"] == ["time-window-restore-output"]
    assert vendor_time_audit["current_trial_candidate"] == {
        "scenario_id": "time-window-future-exclusion",
        "federate_count": 2,
        "pitch_vendor_test": (
            "tests/vendors/test_pitch_real_backend_matrix.py::"
            "test_pitch_time_window_future_exclusion_matrix"
        ),
        "recommended_pitch_operator_route": "./tools/pitch time-window-probe",
        "why_selected": (
            "This is the smallest lookahead-window proof that still exercises future-message exclusion. It keeps "
            "the topology to two federates, so a successful Pitch run would add meaningful vendor credence "
            "without depending on the larger multi-federate gauntlet."
        ),
    }
    vendor_rows = {row["scenario_id"]: row for row in vendor_time_audit["routes"]}
    assert vendor_rows["time-window-future-exclusion"]["federate_count"] == 2
    assert vendor_rows["time-window-future-exclusion"]["trial_pitch_safe"] is True
    assert vendor_rows["time-window-future-exclusion"]["recommended_pitch_operator_route"] == "./tools/pitch time-window-probe"
    assert vendor_rows["time-window-future-exclusion"]["current_pitch_runtime_boundary"] == "seat-availability"
    assert "two-federate future-exclusion proof" in vendor_rows["time-window-future-exclusion"]["current_pitch_runtime_boundary_evidence"]
    assert vendor_rows["time-window-restore-state"]["federate_count"] == 2
    assert vendor_rows["time-window-restore-state"]["trial_pitch_safe"] is True
    assert vendor_rows["time-window-restore-output"]["federate_count"] == 3
    assert vendor_rows["time-window-restore-output"]["trial_pitch_safe"] is False
    assert vendor_rows["time-window-restore-output"]["current_pitch_runtime_boundary"] == "trial-federate-limit-and-seat-availability"
    assert "explicit vendor-parity shape audit" in vendor_time_audit["current_assessment"]
    assert "runtime seat availability, not an overgrown scenario topology" in vendor_time_audit["current_assessment"]
    assert "would add vendor credence" in vendor_time_audit["residual_boundary"]
    extraction_audit = snapshot["extraction_readiness_audit"]
    assert extraction_audit["audit_status"] == "extraction-readiness-map-captured"
    assert extraction_audit["extraction_needed_now"] is False
    assert extraction_audit["dedicated_python_2025_backend_present"] is True
    assert extraction_audit["recommended_current_action"] == "promote-python2025-as-live-lane-and-keep-shim-wrapper-narrowing-map"
    assert extraction_audit["future_backend_package_target"] == "hla-backend-python2025"
    assert extraction_audit["future_backend_plugin_family"] == "python-rti-2025"
    assert extraction_audit["extraction_package_contract"] == {
        "current_package_state": "live-runtime-present",
        "target_distribution": "hla-backend-python2025",
        "target_import_root": "hla.backends.python2025",
        "target_plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
        "target_backend_name": "python2025",
        "target_plugin_family": "python-rti-2025",
        "target_supports": ["rti1516_2025"],
        "must_not_delegate_to": ["hla.backends.shim.backend.create_shim_backend"],
        "scanner_regression_test": (
            "tests/requirements/test_2025_finish_line_snapshot.py::"
            "test_2025_backend_plugin_scan_detects_future_dedicated_python_2025_backend"
        ),
        "package_creation_rule": (
            "Keep this package as the promoted live backend only while the direct and hosted proof families stay "
            "green and hla-backend-shim continues narrowing toward temporary import-compatibility scaffolding and wrapper-only responsibilities."
        ),
    }
    assert extraction_audit["extraction_cutover_invariants"] == [
        "python-2025-inprocess and python-2025-fedpro-grpc parity rows remain green for every migrated slice",
        "hla-backend-shim keeps only route normalization, compatibility aliases, and binding bridge behavior",
        "the dedicated python2025 plugin owns core RTI state for migrated save/restore, directed interaction, DDM, and time semantics",
        "backend plugin discovery reports hla-backend-python2025 as a dedicated rti1516_2025 candidate before any promotion claim changes",
    ]
    assert extraction_audit["runtime_semantics_to_extract_first_count"] == 4
    assert extraction_audit["route_backed_runtime_semantics_count"] == 4
    assert extraction_audit["all_candidate_runtime_semantics_route_backed"] is True
    migrated_runtime_modules = extraction_audit["migrated_runtime_modules"]
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/attribute_scope_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/callback_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/catalog_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/ddm_default_attribute_policy.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/declaration_management_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/directed_interaction_boundary.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/federation_management_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/interaction_policy_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/interaction_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/mom_codec.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/mom_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/object_instance_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/object_model_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/object_reflection_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/object_region_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/ownership_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/save_restore_lifecycle.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/support_lookup_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/support_policy_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/support_services_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/time_management_runtime.py" in migrated_runtime_modules
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/update_rate_runtime.py" in migrated_runtime_modules
    assert extraction_audit["shim_responsibilities_after_extraction"] == [
        "standard-route adaptation and compatibility aliases",
        "transport-facing normalization that is not core RTI state",
        "binding/package bridge behavior for standard Java/C++/hosted routes",
    ]
    assert extraction_audit["runtime_semantics_to_extract_first"] == [
        {
            "slice_id": "2025-save-restore-lifecycle",
            "proof_family_count": 5,
            "proof_families": [
                "lifecycle-control",
                "shared-scenario-rollback",
                "routing-policy-rollback",
                "ownership-rollback",
                "time-window-and-time-state-rollback",
            ],
            "direct_test_count": 29,
            "hosted_test_count": 29,
            "route_backed": True,
            "candidate_runtime_module": "packages/hla-backend-python2025/src/hla/backends/python2025/save_restore_lifecycle.py",
        },
        {
            "slice_id": "2025-ownership-proof-families",
            "proof_family_count": 6,
            "proof_families": [
                "divestiture-and-confirmation-flows",
                "release-and-if-wanted-flows",
                "acquisition-assumption-and-notification",
                "acquisition-availability-and-cancellation",
                "query-visibility-and-resign-policies",
                "rollback-and-restore-state",
            ],
            "direct_test_count": 20,
            "hosted_test_count": 20,
            "route_backed": True,
            "candidate_runtime_module": "packages/hla-backend-python2025/src/hla/backends/python2025/ownership_runtime.py",
        },
        {
            "slice_id": "2025-directed-interaction-boundary",
            "proof_family_count": 5,
            "proof_families": [
                "base-routing-and-callback-delivery",
                "timestamped-delivery-and-retraction",
                "ddm-overlap-filtering",
                "selective-set-and-publication-isolation",
                "restore-routing-and-stale-queue-cleanup",
            ],
            "direct_test_count": 12,
            "hosted_test_count": 12,
            "route_backed": True,
            "candidate_runtime_module": "packages/hla-backend-python2025/src/hla/backends/python2025/directed_interaction_boundary.py",
        },
        {
            "slice_id": "2025-ddm-default-attribute-policy",
            "proof_family_count": 6,
            "proof_families": [
                "lookup-and-default-policy-control",
                "object-region-routing-and-scope-advisories",
                "interaction-region-routing",
                "directed-ddm-routing",
                "passive-alias-and-compat-scenarios",
                "ddm-restore-and-disconnect-cleanup",
            ],
            "direct_test_count": 14,
            "hosted_test_count": 14,
            "route_backed": True,
            "candidate_runtime_module": "packages/hla-backend-python2025/src/hla/backends/python2025/ddm_default_attribute_policy.py",
        },
    ]
    assert extraction_audit["pressure_signal"] == {
        "runtime_backend_slice_share": 0.553,
        "semantic_concentration_is_material": False,
        "pressure_family_count": 22,
        "fully_route_backed_pressure_family_count": 22,
    }
    assert "The extraction cutover is materially underway" in extraction_audit["current_assessment"]
    assert "hla-backend-python2025 now owns the live backend" in extraction_audit["current_assessment"]
    assert "hla-backend-shim remains only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in extraction_audit["current_assessment"]
    assert "concrete migration map for continuing to narrow those scaffolding responsibilities while preserving the direct and hosted proof families" in extraction_audit["current_assessment"]
    assert (
        "a future all-covered requirement audit needs cleaner service-by-service runtime ownership than the remaining compatibility-wrapper layer can provide"
        in extraction_audit["extraction_trigger_signals"]
    )
    assert extraction_audit["pre_extraction_gates"][0] == "keep the dedicated rti1516_2025 Python backend plugin discoverable and keep the backend scan detecting it"
    extraction_impact_audit = snapshot["extraction_impact_audit"]
    assert extraction_impact_audit["audit_status"] == "extraction-impact-map-captured"
    assert extraction_impact_audit["slice_count"] == 4
    assert extraction_impact_audit["all_candidate_slices_have_source_family_map"] is True
    assert extraction_impact_audit["all_candidate_slices_route_backed"] is True
    assert extraction_impact_audit["largest_current_source_baseline"] in {
        "2025-save-restore-lifecycle",
        "2025-ddm-default-attribute-policy",
    }
    impact_rows = {row["slice_id"]: row for row in extraction_impact_audit["rows"]}
    assert impact_rows["2025-save-restore-lifecycle"]["source_family_count"] == 4
    assert "measurable current source families" in extraction_impact_audit["current_assessment"]
    assert "remaining adapter pressure and runtime line baselines" in extraction_impact_audit["current_assessment"]
    assert "dedicated backend is present" in extraction_impact_audit["non_claim"]
    assert impact_rows["2025-save-restore-lifecycle"]["current_source_line_baseline"] >= 2
    assert impact_rows["2025-save-restore-lifecycle"]["current_source_method_baseline"] >= 1
    assert [family["family"] for family in impact_rows["2025-save-restore-lifecycle"]["source_families"]] == [
        "save-restore-runtime",
        "time-management-runtime",
        "ownership-runtime",
        "callback-delivery-and-control",
    ]
    assert impact_rows["2025-ownership-proof-families"]["source_family_count"] == 3
    assert impact_rows["2025-ownership-proof-families"]["current_source_line_baseline"] >= 0
    assert impact_rows["2025-ownership-proof-families"]["current_source_method_baseline"] >= 0
    assert [family["family"] for family in impact_rows["2025-ownership-proof-families"]["source_families"]] == [
        "ownership-runtime",
        "save-restore-runtime",
        "callback-delivery-and-control",
    ]
    assert impact_rows["2025-directed-interaction-boundary"]["source_family_count"] == 3
    assert impact_rows["2025-directed-interaction-boundary"]["current_source_line_baseline"] >= 0
    assert impact_rows["2025-directed-interaction-boundary"]["current_source_method_baseline"] >= 0
    assert impact_rows["2025-ddm-default-attribute-policy"]["source_family_count"] == 4
    assert impact_rows["2025-ddm-default-attribute-policy"]["current_source_line_baseline"] >= 2
    assert impact_rows["2025-ddm-default-attribute-policy"]["current_source_method_baseline"] >= 1
    assert "line baselines are intentionally overlapping" in extraction_impact_audit["non_claim"]
    assert implementation_lane_audit["python_2025_routes"] == [
        {
            "route": "python-2025-inprocess",
            "kind": "in-process-backend-route",
            "is_separate_rti_family": False,
            "all_route_parity_covered": True,
        },
        {
            "route": "python-2025-fedpro-grpc",
            "kind": "hosted-transport-route",
            "is_separate_rti_family": False,
            "all_route_parity_covered": True,
        },
    ]
    objective_audit = snapshot["objective_dimension_audit"]
    assert (
        objective_audit["goal_shape"]
        == "Convert the clean 2025 requirement closeout into deeper runtime proof across federation management, "
        "object management, time management, support services, callbacks, OMT handling, and binding and hosted routes."
    )
    assert objective_audit["surface_claim"] == "bounded-working-surface"
    assert objective_audit["ready_for_bounded_working_surface_claim"] is True
    assert objective_audit["ready_for_full_2025_completion_claim"] is False
    assert objective_audit["dimension_count"] == 8
    assert objective_audit["bounded_ready_dimension_count"] == 8
    dimensions = {row["id"]: row for row in objective_audit["dimensions"]}
    assert set(dimensions) == {
        "federation_management",
        "object_management",
        "time_management",
        "support_services",
        "ownership_management",
        "callbacks",
        "omt_handling",
        "binding_routes",
    }
    assert {row["name"] for row in dimensions.values()} == {
        "Federation Management",
        "Object Management",
        "Time Management",
        "Support Services",
        "Ownership Management",
        "Callbacks",
        "OMT Handling",
        "Binding Routes",
    }
    assert all(row["ready_for_full_claim"] is False for row in dimensions.values())
    assert all(row["requirements_count"] > 0 for row in dimensions.values())
    assert all(row["evidence_tests"] for row in dimensions.values())
    assert all(
        row["evidence_basis"]
        for row in dimensions.values()
        if row["bounded_working_surface_ready"]
    )
    route_backed_dimensions = [
        row for row in dimensions.values() if row["route_scenarios"]
    ]
    assert all(row["route_summary"]["by_status"].get("missing", 0) == 0 for row in route_backed_dimensions)
    assert all(row["route_summary"]["by_status"].get("partial", 0) == 0 for row in route_backed_dimensions)

    assert dimensions["federation_management"]["evidence_level"] == "decomposed-strong-slice"
    assert dimensions["federation_management"]["bounded_working_surface_ready"] is True
    assert "2025-connect-and-federation-catalog-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert "2025-federate-membership-and-resign-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert "2025-synchronization-point-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert tuple(dimensions["federation_management"]["route_scenarios"]) == ("federation_lifecycle", "save_restore")
    assert dimensions["federation_management"]["route_summary"]["by_status"]["parity-covered"] == 12
    assert "tests/transport/test_grpc_transport_2025.py" in dimensions["federation_management"]["route_artifacts"]
    assert dimensions["federation_management"]["evidence_basis"] == [
        "route_summary.scenario_count=2",
        "route_summary.row_count=12",
        "route_summary.routes_with_full_parity=6",
        "federation_management_decomposition.slice_id=2025-federation-management-proof-families",
        "federation_management_decomposition.proof_family_count=6",
    ]
    assert "finish-line now separates that proof into named families" in dimensions["federation_management"]["current_assessment"]
    assert "connect/create/catalog control, join or membership reporting" in dimensions["federation_management"]["current_assessment"]
    assert dimensions["object_management"]["evidence_level"] == "decomposed-strong-slice"
    assert dimensions["object_management"]["route_summary"]["by_status"]["parity-covered"] == 18
    assert dimensions["object_management"]["route_summary"]["scenario_count"] == 3
    assert dimensions["object_management"]["evidence_basis"] == [
        "route_summary.scenario_count=3",
        "route_summary.row_count=18",
        "route_summary.scenarios=ddm,object_exchange,ownership",
        "object_management_decomposition.slice_id=2025-object-management-proof-families",
        "object_management_decomposition.proof_family_count=7",
    ]
    assert "2025-declaration-publication-services" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-declaration-subscription-services" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-declaration-relevance-advisory-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-delete-remove-flows" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-attribute-update-request-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-attribute-transport-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-interaction-transport-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "finish-line now separates that proof into named families" in dimensions["object_management"]["current_assessment"]
    assert "declaration and exchange gating, delete/local-known-state lifecycle" in dimensions["object_management"]["current_assessment"]
    assert "Hosted FedPro replay now also covers rollback-sensitive object state" in dimensions["object_management"]["current_assessment"]
    assert "stale timed-remove cleanup" in dimensions["object_management"]["current_assessment"]
    assert "restored local-known-state after local delete" in dimensions["object_management"]["current_assessment"]
    assert dimensions["ownership_management"]["evidence_level"] == "decomposed-strong-slice"
    assert "2025-ownership-divestiture-confirmation-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-release-and-if-wanted-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-acquisition-assumption-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-acquisition-availability-cancellation-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-query-and-resign-policies" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert tuple(dimensions["ownership_management"]["route_scenarios"]) == ("ownership", "save_restore")
    assert dimensions["ownership_management"]["evidence_basis"] == [
        "route_summary.scenario_count=2",
        "route_summary.row_count=12",
        "route_summary.scenarios=ownership,save_restore",
        "ownership_decomposition.slice_id=2025-ownership-proof-families",
        "ownership_decomposition.proof_family_count=6",
    ]
    assert "finish-line now separates that proof into named ownership families" in dimensions["ownership_management"]["current_assessment"]
    assert dimensions["time_management"]["route_summary"]["by_status"]["parity-covered"] == 12
    assert "tests/test_rti1516_2025_python2025_runtime.py" in dimensions["time_management"]["evidence_tests"]
    assert dimensions["time_management"]["evidence_level"] == "decomposed-query-and-window-proof-backed"
    assert dimensions["time_management"]["evidence_basis"] == [
        "python_rti_milestone_audit bounded time rows=python-2025-fedpro-grpc:bounded-lookahead-evidence,python-2025-fedpro-grpc:bounded-query-evidence,python-2025-inprocess:bounded-lookahead-evidence,python-2025-inprocess:bounded-query-evidence",
        "time_window_vendor_parity_audit.audit_status=time-window-vendor-parity-captured",
        "time_window_vendor_parity_audit.current_trial_candidate.scenario_id=time-window-future-exclusion",
        "time_management_decomposition.slice_id=2025-time-management-proof-families",
        "time_management_decomposition.proof_family_count=5",
    ]
    assert "2025-time-mode-enable-disable" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-advance-request-modes" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-grant-and-async-delivery" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-query-and-lookahead-control" in dimensions["time_management"]["implemented_slice_ids"]
    assert "Target/Radar lookahead-window proof ladder" in dimensions["time_management"]["current_assessment"]
    assert "negative-oracle guards" in dimensions["time_management"]["current_assessment"]
    assert "named runtime proof families instead of one flat bounded time bucket" in dimensions["time_management"]["current_assessment"]
    assert "The closeout now separates time proof into named runtime families" in dimensions["time_management"]["residual_blockers"][0]
    assert dimensions["support_services"]["route_summary"]["by_status"]["parity-covered"] == 6
    assert "2025-support-federate-and-object-identity-lookups" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-attribute-interaction-catalog-lookups" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-policy-update-and-transport-lookups" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-interaction-dimension-and-range-lookups" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-handle-normalization-and-region-introspection" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-advisory-and-reporting-state-inquiries" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-runtime-policy-state-inquiries" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-advisory-and-reporting-state-controls" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-support-runtime-policy-state-controls" in dimensions["support_services"]["implemented_slice_ids"]
    assert "2025-standard-route-runtime-capability" in dimensions["support_services"]["implemented_slice_ids"]
    assert dimensions["support_services"]["evidence_level"] == "decomposed-per-service-runtime-traceable"
    assert dimensions["omt_handling"]["evidence_basis"] == [
        "omt_requirement_proof_audit.ready_for_omt_traceability_claim=true",
        "omt_requirement_proof_audit.row_count=454",
        "omt_requirement_proof_audit.by_proof_status=supported-subset-traceable:454",
        "omt_decomposition.slice_ids=2025-service-utilization-crosscheck,2025-omt-extended-supported-subset,2025-omt-xs-any-extension-tolerance,2025-omt-schema-constraint-validation",
        "omt_decomposition.family_counts=service-utilization:10,extended-subset:5,xs-any:5,schema-constraint:4",
    ]
    assert dimensions["binding_routes"]["evidence_basis"] == [
        "route_summary.scenario_count=8",
        "route_summary.row_count=48",
        "route_summary.routes_with_full_parity=6",
        "binding_route_decomposition.slice_id=2025-binding-route-proof-families",
        "binding_route_decomposition.proof_family_count=6",
    ]
    assert dimensions["support_services"]["evidence_basis"] == [
        "support_service_proof_audit.ready_for_support_service_traceability_claim=true",
        "support_service_proof_audit.focused_executable_row_count=62",
        "support_service_proof_audit.complete_negative_path_row_count=61",
        "support_services_decomposition.slice_id=2025-support-services-proof-families",
        "support_services_decomposition.proof_family_count=5",
    ]
    assert "it now separates that proof into named families" in dimensions["support_services"]["current_assessment"]
    assert "tracked binding and hosted routes" in dimensions["support_services"]["current_assessment"]
    assert "reservation/release flows, lookup and normalization surfaces" in dimensions["support_services"]["current_assessment"]
    assert "per-service runtime traceability plus complete actionable negative-path coverage inside the Python routes" in dimensions["support_services"]["residual_blockers"][0]
    assert "hosted FedPro route remains a bounded runtime slice rather than a full support-service conformance route" in dimensions["support_services"]["residual_blockers"][1]
    assert dimensions["callbacks"]["evidence_level"] == "decomposed-callback-ledger-route-backed"
    assert dimensions["callbacks"]["evidence_basis"] == [
        "callback_proof_audit.ready_for_callback_by_callback_working_surface_claim=true",
        "callback_route_parity_audit.ready_for_full_python_lane_callback_route_parity_claim=true",
        "callback_route_parity_audit.hosted_or_route_backed_callback_count=55",
        "callback_decomposition.slice_id=2025-callback-proof-families",
        "callback_decomposition.proof_family_count=8",
    ]
    assert tuple(dimensions["callbacks"]["route_scenarios"]) == (
        "federation_lifecycle",
        "object_exchange",
        "ownership",
        "time_management",
        "save_restore",
        "mom",
        "support_services",
    )
    assert dimensions["callbacks"]["route_summary"]["by_status"]["parity-covered"] == 42
    assert "fully route-backed across the current Python 2025 lanes" in dimensions["callbacks"]["current_assessment"]
    assert "named runtime families instead of leaving it as a flat ledger" in dimensions["callbacks"]["current_assessment"]
    assert "2025-fedpro-hosted-runtime-core" in dimensions["callbacks"]["implemented_slice_ids"]
    assert "2025-fedpro-hosted-runtime-extended-state" in dimensions["callbacks"]["implemented_slice_ids"]
    assert "The callback proof is now decomposed into named runtime families" in dimensions["callbacks"]["residual_blockers"][0]
    assert "Binding-route callback parity is tracked at the scenario level" in dimensions["callbacks"]["residual_blockers"][1]
    assert "Hosted FedPro replay now also proves restored in-flight ownership negotiation state" in dimensions["ownership_management"]["current_assessment"]
    assert "restored cross-federate owner-visibility queries" in dimensions["ownership_management"]["current_assessment"]
    assert dimensions["omt_handling"]["route_summary"]["row_count"] == 0
    assert tuple(dimensions["omt_handling"]["route_scenarios"]) == ()
    assert dimensions["omt_handling"]["bounded_working_surface_ready"] is True
    assert "extension payload preservation" in dimensions["omt_handling"]["current_assessment"]
    assert "named decomposition audits for the extended supported subset" in dimensions["omt_handling"]["current_assessment"]
    assert dimensions["omt_handling"]["evidence_level"] == "decomposed-bounded-slice"
    assert "The OMT proof is now decomposed into named subset and validator families" in dimensions["omt_handling"]["residual_blockers"][0]
    assert "2025-omt-schema-constraint-validation" in dimensions["omt_handling"]["implemented_slice_ids"]
    assert "2025-omt-xs-any-extension-tolerance" in dimensions["omt_handling"]["implemented_slice_ids"]
    assert dimensions["binding_routes"]["route_summary"]["by_status"]["parity-covered"] == 48
    assert dimensions["binding_routes"]["evidence_level"] == "decomposed-bounded-slice"
    assert dimensions["binding_routes"]["bounded_working_surface_ready"] is True
    assert dimensions["binding_routes"]["ready_for_full_claim"] is False
    assert "2025-standard-route-runtime-capability" in dimensions["binding_routes"]["implemented_slice_ids"]
    assert "2025-fedpro-typed-transport-surface" in dimensions["binding_routes"]["implemented_slice_ids"]
    assert "2025-fedpro-hosted-runtime-core" in dimensions["binding_routes"]["implemented_slice_ids"]
    assert "2025-fedpro-hosted-runtime-extended-state" in dimensions["binding_routes"]["implemented_slice_ids"]
    assert "named binding and hosted-route families instead of one flat bounded bucket" in dimensions["binding_routes"]["current_assessment"]
    assert any("artifact/runtime-capability" in blocker or "artifact/runtime" in blocker for blocker in dimensions["binding_routes"]["residual_blockers"])
    assert "The route evidence is now decomposed into named families" in dimensions["binding_routes"]["residual_blockers"][0]
    assert any(
        "hosted FedPro route remains a bounded working slice" in blocker
        for blocker in dimensions["binding_routes"]["residual_blockers"]
    )
    closeout = snapshot["closeout_readiness"]
    assert closeout["implemented_slice_count"] >= 20
    assert closeout["high_priority_open_count"] == 0
    assert closeout["route_parity_partial_count"] == 0
    assert closeout["route_parity_missing_count"] == 0
    assert closeout["ready_for_slice_closeout"] is True
    assert closeout["ready_for_full_completion_claim"] is False
    assert "FI per-service runtime traceability" in closeout["current_assessment"]
    assert "outside the already-green primary python2025 runtime lane" in closeout["current_assessment"]
    assert len(closeout["conformance_blockers"]) >= 4
    assert any("row-level requirement-by-requirement disposition audit across all 2025 rows" in blocker for blocker in closeout["conformance_blockers"])
    assert any("requirement-closeout limit rather than evidence that the main python2025 runtime lane is behaviorally incomplete" in blocker for blocker in closeout["conformance_blockers"])
    assert any("Java and C++ standard-route evidence" in blocker for blocker in closeout["conformance_blockers"])
    assert any("hosted FedPro route is verified as a runtime slice" in blocker for blocker in closeout["conformance_blockers"])
    assert any("hosted/cross-binding proof limit rather than evidence that the direct python2025 runtime lane lacks those semantics" in blocker for blocker in closeout["conformance_blockers"])
    closeout_partition = snapshot["closeout_blocker_partition_audit"]
    assert closeout_partition["audit_status"] == "closeout-blocker-partition-captured"
    assert closeout_partition["closeout_blocker_count"] == 6
    assert closeout_partition["partitioned_blocker_count"] == 6
    assert closeout_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert closeout_partition["boundary_only_blocker_count"] == 6
    assert closeout_partition["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True
    assert closeout_partition["blocker_rows"] == [
        {
            "blocker": "row_level_requirement_closeout_limit",
            "classification": "requirement-closeout-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "row-level disposition still includes retired, umbrella, and bounded-scope rows rather than an unconditional conformance pass"
            ),
        },
        {
            "blocker": "implemented_slice_requirement_granularity_gap",
            "classification": "requirement-granularity-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "many implemented slices still aggregate multiple requirements under bounded supported-scope language"
            ),
        },
        {
            "blocker": "standard_java_cpp_cross_binding_gap",
            "classification": "external-binding-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "Java/C++ standard-route evidence remains artifact-gated/runtime-capability proof rather than full cross-binding behavior conformance"
            ),
        },
        {
            "blocker": "hosted_fedpro_cross_binding_gap",
            "classification": "external-hosted-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "hosted FedPro supported-scope rows stop short of full RTI semantics and full cross-binding conformance"
            ),
        },
        {
            "blocker": "omt_extension_execution_scope_gap",
            "classification": "external-omt-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "OMT xs:any coverage preserves foreign extension payloads but leaves arbitrary third-party extension execution semantics out of scope"
            ),
        },
        {
            "blocker": "legacy_only_explicit_exclusion",
            "classification": "legacy-exclusion-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "legacy-only rows remain explicit exclusions from an unconditional 2025 completion claim"
            ),
        },
    ]
    assert "all describe requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits" in closeout_partition["current_assessment"]
    assert "missing core executable behavior in the main hla-backend-python2025 runtime lane" in closeout_partition["current_assessment"]
    assert "without treating the main python2025 runtime as behaviorally unfinished" in closeout_partition["residual_boundary"]


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}
    python2025_backend_path = (
        ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025" / "backend.py"
    )
    current_python2025_line_count = sum(1 for _ in python2025_backend_path.open(encoding="utf-8"))

    assert slices["2025-auth-connect"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-001" in slices["2025-auth-connect"]["requirements"]
    assert any(path.endswith("test_rti1516_2025_encoding_auth_contexts.py") for path in slices["2025-auth-connect"]["evidence"])

    assert slices["2025-time-mode-enable-disable"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-101" in slices["2025-time-mode-enable-disable"]["requirements"]
    assert "HLA2025-FI-SVC-106" in slices["2025-time-mode-enable-disable"]["requirements"]
    assert "timeRegulationEnabled callback delivery" in slices["2025-time-mode-enable-disable"]["supported_scope"]
    assert "timeConstrainedEnabled callback delivery" in slices["2025-time-mode-enable-disable"]["supported_scope"]

    assert slices["2025-time-advance-request-modes"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-107" in slices["2025-time-advance-request-modes"]["requirements"]
    assert "HLA2025-FI-SVC-111" in slices["2025-time-advance-request-modes"]["requirements"]
    assert "flushQueueRequest" in slices["2025-time-advance-request-modes"]["supported_scope"]
    assert "queued timestamp-order delivery" in slices["2025-time-advance-request-modes"]["supported_scope"]

    assert slices["2025-time-grant-and-async-delivery"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-112" in slices["2025-time-grant-and-async-delivery"]["requirements"]
    assert "HLA2025-FI-SVC-115" in slices["2025-time-grant-and-async-delivery"]["requirements"]
    assert "timeAdvanceGrant callbacks" in slices["2025-time-grant-and-async-delivery"]["supported_scope"]
    assert "enable/disable asynchronous delivery" in slices["2025-time-grant-and-async-delivery"]["supported_scope"]

    assert slices["2025-time-query-and-lookahead-control"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-116" in slices["2025-time-query-and-lookahead-control"]["requirements"]
    assert "HLA2025-FI-SVC-120" in slices["2025-time-query-and-lookahead-control"]["requirements"]
    assert "queryGALT" in slices["2025-time-query-and-lookahead-control"]["supported_scope"]
    assert "modifyLookahead" in slices["2025-time-query-and-lookahead-control"]["supported_scope"]

    assert slices["2025-time-queries-retraction-and-order"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-122" in slices["2025-time-queries-retraction-and-order"]["requirements"]
    assert "HLA2025-FI-SVC-125" in slices["2025-time-queries-retraction-and-order"]["requirements"]
    assert "queued timestamped object updates/interactions" in slices["2025-time-queries-retraction-and-order"]["supported_scope"]
    assert "message retraction before delivery" in slices["2025-time-queries-retraction-and-order"]["supported_scope"]

    assert slices["2025-lookahead-window-proofs"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-006" in slices["2025-lookahead-window-proofs"]["requirements"]
    assert "future-exclusion proof ladder" in slices["2025-lookahead-window-proofs"]["supported_scope"]
    assert "negative-oracle guards" in slices["2025-lookahead-window-proofs"]["supported_scope"]
    assert "Cross-binding parity" in slices["2025-lookahead-window-proofs"]["supported_scope"]
    assert slices["2025-save-restore-lifecycle"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-018" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "HLA2025-FI-SVC-034" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "federation save/restore lifecycle callbacks" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "direct execution of the shared two-federate save/restore suite on the main python2025 runtime plus hosted replay over the FedPro route" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "requestFederationSave and requestFederationRestore" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "object registry rollback" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "joined-federate logical-time rollback" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert slices["2025-switch-set-get-model"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-008" in slices["2025-switch-set-get-model"]["requirements"]
    assert "set/get switch model replaces the old enable/disable pattern" in slices["2025-switch-set-get-model"]["supported_scope"]
    assert slices["2025-retired-advisory-switch-enable-disable-mapping"]["status"] == "legacy-only"
    assert slices["2025-retired-advisory-switch-enable-disable-mapping"]["requirements"] == ("HLA2025-RET-001",)
    assert "retired or replacement-mapped items" in slices["2025-retired-advisory-switch-enable-disable-mapping"]["supported_scope"]
    assert "rejects those legacy method spellings as unsupported 2025 services" in slices["2025-retired-advisory-switch-enable-disable-mapping"]["supported_scope"]
    assert slices["2025-handle-normalization"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-005" in slices["2025-handle-normalization"]["requirements"]
    assert "wrong-family rejection" in slices["2025-handle-normalization"]["supported_scope"]
    assert "service-group and object-instance normalization requests across the 2025 transport surface" in slices["2025-handle-normalization"]["supported_scope"]
    assert slices["2025-fom-mim-error-taxonomy"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-003" in slices["2025-fom-mim-error-taxonomy"]["requirements"]
    assert "create-time FOM/MIM taxonomy proof" in slices["2025-fom-mim-error-taxonomy"]["supported_scope"]
    assert "createFederationExecutionWithMIM and createFederationExecutionWithMIMAndTime" in slices["2025-fom-mim-error-taxonomy"]["supported_scope"]
    assert "2025 transport command surface" in slices["2025-fom-mim-error-taxonomy"]["supported_scope"]
    assert "CouldNotOpen, ErrorReading, Invalid, and Inconsistent FOM/MIM failures" in slices["2025-fom-mim-error-taxonomy"]["supported_scope"]
    assert slices["2025-callback-context-object-delivery"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-004" in slices["2025-callback-context-object-delivery"]["requirements"]
    assert "discoverObjectInstance" in slices["2025-callback-context-object-delivery"]["supported_scope"]
    assert "removeObjectInstance" in slices["2025-callback-context-object-delivery"]["supported_scope"]
    assert slices["2025-callback-context-interaction-delivery"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-004" in slices["2025-callback-context-interaction-delivery"]["requirements"]
    assert "receiveInteraction" in slices["2025-callback-context-interaction-delivery"]["supported_scope"]
    assert "receiveDirectedInteraction" in slices["2025-callback-context-interaction-delivery"]["supported_scope"]
    assert slices["2025-directed-interaction-boundary"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-001" in slices["2025-directed-interaction-boundary"]["requirements"]
    assert {
        "HLA2025-FI-SVC-039",
        "HLA2025-FI-SVC-040",
        "HLA2025-FI-SVC-045",
        "HLA2025-FI-SVC-046",
        "HLA2025-FI-SVC-063",
        "HLA2025-FI-SVC-064",
    } <= set(slices["2025-directed-interaction-boundary"]["requirements"])
    assert "receiveDirectedInteraction callback delivery" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert "Current Python 2025 RTI plus the hosted FedPro route support" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert "Java/C++ parity remains later behavior work" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert slices["2025-omt-reference-value-required"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-006" in slices["2025-omt-reference-value-required"]["requirements"]
    assert slices["2025-omt-component-metadata-roundtrip"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-004" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "HLA2025-OMT-COMP-215" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "array encodings" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert "logicalTime/logicalTimeInterval names" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert "semantics text" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-switch-and-transport-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-078" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-166" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-167" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-170" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-200" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-201" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-207" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "nonRegulatedGrant" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert "sendServiceReportsToFile" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert "transportation reliable/semantics metadata" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert "update-rate semantics metadata" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert "conveyProducingFederate default" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert slices["2025-omt-extended-supported-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-001" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-083" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-223" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "reference/POC/keyword taxonomy metadata subset" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert "supported basic/simple/enumerated/array/fixed-record/variant-record datatype tables" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert slices["2025-omt-dimension-metadata-roundtrip"]["status"] == "implemented-slice"
    assert slices["2025-omt-dimension-metadata-roundtrip"]["requirements"] == (
        "HLA2025-OMT-COMP-037",
        "HLA2025-OMT-COMP-038",
        "HLA2025-OMT-COMP-040",
        "HLA2025-OMT-COMP-041",
        "HLA2025-OMT-COMP-042",
        "HLA2025-OMT-COMP-043",
        "HLA2025-OMT-COMP-044",
    )
    assert "inputDataTypes" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert "upperBound" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert "normalization metadata text" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert "outputDataSemantics" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-attribute-metadata-roundtrip"]["status"] == "implemented-slice"
    assert slices["2025-omt-attribute-metadata-roundtrip"]["requirements"] == (
        "HLA2025-OMT-COMP-011",
        "HLA2025-OMT-COMP-012",
        "HLA2025-OMT-COMP-014",
        "HLA2025-OMT-COMP-015",
        "HLA2025-OMT-COMP-017",
        "HLA2025-OMT-COMP-018",
    )
    assert "attribute updateType" in slices["2025-omt-attribute-metadata-roundtrip"]["supported_scope"]
    assert "does not claim" in slices["2025-omt-attribute-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-class-parameter-metadata-roundtrip"]["status"] == "implemented-slice"
    assert slices["2025-omt-class-parameter-metadata-roundtrip"]["requirements"] == (
        "HLA2025-OMT-COMP-074",
        "HLA2025-OMT-COMP-079",
        "HLA2025-OMT-COMP-080",
        "HLA2025-OMT-COMP-109",
        "HLA2025-OMT-COMP-114",
        "HLA2025-OMT-COMP-133",
    )
    assert "object-class sharing/semantics" in slices["2025-omt-class-parameter-metadata-roundtrip"]["supported_scope"]
    assert "parameter semantics metadata" in slices["2025-omt-class-parameter-metadata-roundtrip"]["supported_scope"]
    assert "HLA2025-OMT-COMP-037" in slices["2025-omt-dimension-metadata-roundtrip"]["requirements"]
    assert "HLA2025-OMT-COMP-044" in slices["2025-omt-dimension-metadata-roundtrip"]["requirements"]
    assert "inputDataTypes" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert "outputDataSemantics" in slices["2025-omt-dimension-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-association-metadata-roundtrip"]["status"] == "implemented-slice"
    assert slices["2025-omt-association-metadata-roundtrip"]["requirements"] == (
        "HLA2025-OMT-COMP-048",
        "HLA2025-OMT-COMP-049",
        "HLA2025-OMT-COMP-075",
        "HLA2025-OMT-COMP-076",
        "HLA2025-OMT-COMP-110",
        "HLA2025-OMT-COMP-111",
        "HLA2025-OMT-COMP-112",
    )
    assert "directedInteraction name/sharing" in slices["2025-omt-association-metadata-roundtrip"]["supported_scope"]
    assert "dimension association references" in slices["2025-omt-association-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-xs-any-extension-tolerance"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-006" in slices["2025-omt-xs-any-extension-tolerance"]["requirements"]
    assert "HLA2025-OMT-COMP-039" in slices["2025-omt-xs-any-extension-tolerance"]["requirements"]
    assert "HLA2025-OMT-COMP-197" in slices["2025-omt-xs-any-extension-tolerance"]["requirements"]
    assert "HLA2025-OMT-COMP-224" in slices["2025-omt-xs-any-extension-tolerance"]["requirements"]
    assert "foreign-namespace xs:any extension elements" in slices["2025-omt-xs-any-extension-tolerance"]["supported_scope"]
    assert "preserves text/attribute/nested XML payloads for serializer round-trip" in slices["2025-omt-xs-any-extension-tolerance"]["supported_scope"]
    assert "not a claim to execute arbitrary third-party extension semantics" in slices["2025-omt-xs-any-extension-tolerance"]["supported_scope"]
    assert slices["2025-carry-forward-cleanup"]["status"] == "implemented-slice"
    assert "HLA2025-BLG-001" in slices["2025-carry-forward-cleanup"]["requirements"]
    assert slices["2025-service-utilization-crosscheck"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-SU-001" in slices["2025-service-utilization-crosscheck"]["requirements"]
    assert "HLA2025-OMT-SU-196" in slices["2025-service-utilization-crosscheck"]["requirements"]
    assert "optional serviceUtilization tables from SOM, FOM, and MIM modules" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert "treats table absence as an empty mapping" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert "preserves service-usage attributes through parse/serialize roundtrip" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert slices["2025-exception-and-logical-time-deltas"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-010" in slices["2025-exception-and-logical-time-deltas"]["requirements"]
    assert slices["2025-java-binding-source-trace"]["status"] == "implemented-slice"
    assert "full Java behavior conformance" in slices["2025-java-binding-source-trace"]["supported_scope"]
    assert slices["2025-cpp-binding-source-trace"]["status"] == "implemented-slice"
    assert "full C++ RTI behavior pass" in slices["2025-cpp-binding-source-trace"]["supported_scope"]
    assert slices["2025-standard-route-runtime-capability"]["status"] == "implemented-slice"
    assert "HLA2025-BND-001" in slices["2025-standard-route-runtime-capability"]["requirements"]
    assert "HLA2025-BND-002" in slices["2025-standard-route-runtime-capability"]["requirements"]
    assert "C++ artifacts exercise this locally" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert "Java runtime evidence runs when the Java 2025 standard-route jar is built" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert "not full Java/C++ behavior conformance or object exchange" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert slices["2025-fedpro-typed-transport-surface"]["status"] == "implemented-slice"
    assert "typed RTI request oneofs" in slices["2025-fedpro-typed-transport-surface"]["supported_scope"]
    assert "typed callback oneofs" in slices["2025-fedpro-typed-transport-surface"]["supported_scope"]
    assert "explicit federation-list plus single-FOM and create-with-MIM transport commands" in slices["2025-fedpro-typed-transport-surface"]["supported_scope"]
    assert "checked-in 2025 FedPro surface is executable" in slices["2025-fedpro-typed-transport-surface"]["supported_scope"]

    assert slices["2025-fedpro-hosted-runtime-core"]["status"] == "implemented-slice"
    assert "hosted loopback runtime core" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "explicit single-FOM and create-with-MIM federation creation" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "explicit federation-execution/member listing" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "callback-control enable/disable routing" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "object discovery, attribute reflection, interaction receipt" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "object-class-attribute unpublish gating" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "instance/class/region-scoped attribute value update requests" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "single and multiple object instance name reservation/release callback flow" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "transportation change/query callbacks" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert "not a full FedPro RTI conformance claim" in slices["2025-fedpro-hosted-runtime-core"]["supported_scope"]
    assert slices["2025-fedpro-hosted-runtime-extended-state"]["status"] == "implemented-slice"
    assert "hosted extended-state runtime slice" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "basic ownership divest/acquire callbacks" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "time-regulation/time-constrained/time-advance callbacks" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "queued timestamped attribute reflection/interaction receipt" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "pre-delivery retract" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "basic DDM region-overlap" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "save/restore lifecycle callbacks including timed initiateFederateSave" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "MOM service-invocation report callbacks over FedPro" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "synchronization point/status MOM reports over FedPro" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "targeted transport/ownership/time save-restore manager actions" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert "full RTI semantics remain outside this slice" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
    assert slices["2025-basic-object-exchange"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-057" in slices["2025-basic-object-exchange"]["requirements"]
    assert "HLA2025-FI-SVC-062" in slices["2025-basic-object-exchange"]["requirements"]
    assert "discoverObjectInstance delivery" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert "interaction publication gating" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert "per-instance order policy changes for reflected attributes" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert "interaction order policy changes" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert slices["2025-ddm-default-attribute-policy"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-007" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-076" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-124" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-126" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-136" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-157" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-128" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-129" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-131" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-133" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-137" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-159" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-164" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "createRegion/commitRegionModifications/deleteRegion/setRangeBounds" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "registerObjectInstanceWithRegions/subscribeObjectClassAttributesWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "unassociateRegionsForUpdates/requestAttributeValueUpdateWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "subscribeInteractionClassWithRegions/unsubscribeInteractionClassWithRegions/sendInteractionWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "Attribute scope advisory callbacks" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "in-scope and out-of-scope transitions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert slices["2025-omt-schema-constraint-validation"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-CV-001" in slices["2025-omt-schema-constraint-validation"]["requirements"]
    assert "HLA2025-OMT-CV-029" in slices["2025-omt-schema-constraint-validation"]["requirements"]
    assert "lxml-backed IEEE1516-OMT-2025 XML Schema validation path" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert "strict domain checks" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert "union-backed fields" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert slices["2025-object-delete-remove-flows"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-065" in slices["2025-object-delete-remove-flows"]["requirements"]
    assert "HLA2025-FI-SVC-067" in slices["2025-object-delete-remove-flows"]["requirements"]
    assert "HLA2025-FI-SVC-070" not in slices["2025-object-delete-remove-flows"]["requirements"]
    assert "deleteObjectInstance and removeObjectInstance callbacks" in slices["2025-object-delete-remove-flows"]["supported_scope"]
    assert "localDeleteObjectInstance validation" in slices["2025-object-delete-remove-flows"]["supported_scope"]
    assert slices["2025-object-attribute-update-request-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-070" in slices["2025-object-attribute-update-request-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-071" in slices["2025-object-attribute-update-request-callbacks"]["requirements"]
    assert "requestAttributeValueUpdate by object instance and object class" in slices["2025-object-attribute-update-request-callbacks"]["supported_scope"]
    assert "provideAttributeValueUpdate callback delivery" in slices["2025-object-attribute-update-request-callbacks"]["supported_scope"]
    assert "region-scoped requestAttributeValueUpdate callbacks across the live python2025 runtime lane and hosted FedPro route" in slices["2025-object-attribute-update-request-callbacks"]["supported_scope"]

    assert slices["2025-object-scope-advisory-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-068" in slices["2025-object-scope-advisory-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-069" in slices["2025-object-scope-advisory-callbacks"]["requirements"]
    assert "attributesInScope and attributesOutOfScope transitions" in slices["2025-object-scope-advisory-callbacks"]["supported_scope"]
    assert slices["2025-object-update-rate-advisory-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-072" in slices["2025-object-update-rate-advisory-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-073" in slices["2025-object-update-rate-advisory-callbacks"]["requirements"]
    assert "update-rate designator context" in slices["2025-object-update-rate-advisory-callbacks"]["supported_scope"]
    assert slices["2025-object-attribute-transport-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-074" in slices["2025-object-attribute-transport-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-078" in slices["2025-object-attribute-transport-callbacks"]["requirements"]
    assert "requestAttributeTransportationTypeChange" in slices["2025-object-attribute-transport-callbacks"]["supported_scope"]
    assert "callback-field preservation for attribute transportation callbacks" in slices["2025-object-attribute-transport-callbacks"]["supported_scope"]
    assert slices["2025-object-interaction-transport-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-079" in slices["2025-object-interaction-transport-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-082" in slices["2025-object-interaction-transport-callbacks"]["requirements"]
    assert "requestInteractionTransportationTypeChange" in slices["2025-object-interaction-transport-callbacks"]["supported_scope"]
    assert "callback-field preservation for interaction transportation callbacks" in slices["2025-object-interaction-transport-callbacks"]["supported_scope"]
    assert slices["2025-single-name-reservation-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-051" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-052" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-053" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "single-name reservation success and failure callbacks" in slices["2025-single-name-reservation-services"]["supported_scope"]
    assert "ObjectInstanceNameNotReserved on invalid single-name release" in slices["2025-single-name-reservation-services"]["supported_scope"]
    assert slices["2025-multi-name-reservation-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-054" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-055" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-056" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "set-wide success/failure callbacks" in slices["2025-multi-name-reservation-services"]["supported_scope"]
    assert "reservation preservation through save/restore snapshots" in slices["2025-multi-name-reservation-services"]["supported_scope"]
    assert slices["2025-connection-lifecycle-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-002" in slices["2025-connection-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-003" in slices["2025-connection-lifecycle-services"]["requirements"]
    assert "orderly disconnect state teardown" in slices["2025-connection-lifecycle-services"]["supported_scope"]
    assert "connectionLost callback" in slices["2025-connection-lifecycle-services"]["supported_scope"]
    assert slices["2025-connect-and-federation-catalog-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-001" in slices["2025-connect-and-federation-catalog-services"]["requirements"]
    assert "HLA2025-FI-SVC-004" in slices["2025-connect-and-federation-catalog-services"]["requirements"]
    assert "HLA2025-FI-SVC-007" in slices["2025-connect-and-federation-catalog-services"]["requirements"]
    assert "creates federation executions with resolved FOM modules" in slices["2025-connect-and-federation-catalog-services"]["supported_scope"]
    assert "lists existing federation executions" in slices["2025-connect-and-federation-catalog-services"]["supported_scope"]
    assert "destroys federation executions once they are empty" in slices["2025-connect-and-federation-catalog-services"]["supported_scope"]
    assert slices["2025-federate-membership-and-resign-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-008" in slices["2025-federate-membership-and-resign-services"]["requirements"]
    assert "HLA2025-FI-SVC-010" in slices["2025-federate-membership-and-resign-services"]["requirements"]
    assert "HLA2025-FI-SVC-012" in slices["2025-federate-membership-and-resign-services"]["requirements"]
    assert "list/report federation execution members" in slices["2025-federate-membership-and-resign-services"]["supported_scope"]
    assert "resignFederationExecution" in slices["2025-federate-membership-and-resign-services"]["supported_scope"]
    assert "federateResigned callback delivery" in slices["2025-federate-membership-and-resign-services"]["supported_scope"]
    assert slices["2025-synchronization-point-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-013" in slices["2025-synchronization-point-services"]["requirements"]
    assert "HLA2025-FI-SVC-017" in slices["2025-synchronization-point-services"]["requirements"]
    assert "announceSynchronizationPoint delivery" in slices["2025-synchronization-point-services"]["supported_scope"]
    assert "federationSynchronized callback flow" in slices["2025-synchronization-point-services"]["supported_scope"]
    assert slices["2025-declaration-publication-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-035" in slices["2025-declaration-publication-services"]["requirements"]
    assert "HLA2025-FI-SVC-038" in slices["2025-declaration-publication-services"]["requirements"]
    assert "publish and unpublish for object class attributes and interaction classes" in slices["2025-declaration-publication-services"]["supported_scope"]
    assert "sendInteraction delivery" in slices["2025-declaration-publication-services"]["supported_scope"]
    assert slices["2025-declaration-subscription-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-041" in slices["2025-declaration-subscription-services"]["requirements"]
    assert "HLA2025-FI-SVC-044" in slices["2025-declaration-subscription-services"]["requirements"]
    assert "subscribe and unsubscribe for object class attributes and interaction classes" in slices["2025-declaration-subscription-services"]["supported_scope"]
    assert "unsubscribe state stopping subsequent" in slices["2025-declaration-subscription-services"]["supported_scope"]
    assert slices["2025-declaration-relevance-advisory-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-047" in slices["2025-declaration-relevance-advisory-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-050" in slices["2025-declaration-relevance-advisory-callbacks"]["requirements"]
    assert "startRegistrationForObjectClass" in slices["2025-declaration-relevance-advisory-callbacks"]["supported_scope"]
    assert "turnInteractionsOff" in slices["2025-declaration-relevance-advisory-callbacks"]["supported_scope"]
    assert slices["2025-support-handle-normalization-and-region-introspection"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-162" in slices["2025-support-handle-normalization-and-region-introspection"]["requirements"]
    assert "HLA2025-FI-SVC-165" in slices["2025-support-handle-normalization-and-region-introspection"]["requirements"]
    assert "HLA2025-FI-SVC-169" in slices["2025-support-handle-normalization-and-region-introspection"]["requirements"]
    assert "normalizes service groups" in slices["2025-support-handle-normalization-and-region-introspection"]["supported_scope"]
    assert "wrong-family rejection" in slices["2025-support-handle-normalization-and-region-introspection"]["supported_scope"]
    assert "dimension handle sets for joined regions" in slices["2025-support-handle-normalization-and-region-introspection"]["supported_scope"]
    assert slices["2025-support-advisory-and-reporting-state-inquiries"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-170" in slices["2025-support-advisory-and-reporting-state-inquiries"]["requirements"]
    assert "HLA2025-FI-SVC-186" in slices["2025-support-advisory-and-reporting-state-inquiries"]["requirements"]
    assert "advisory and reporting-state inquiry switches" in slices["2025-support-advisory-and-reporting-state-inquiries"]["supported_scope"]
    assert slices["2025-support-runtime-policy-state-inquiries"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-180" in slices["2025-support-runtime-policy-state-inquiries"]["requirements"]
    assert "HLA2025-FI-SVC-192" in slices["2025-support-runtime-policy-state-inquiries"]["requirements"]
    assert "automatic resign directive, auto-provide, delay-subscription-evaluation" in slices["2025-support-runtime-policy-state-inquiries"]["supported_scope"]
    assert slices["2025-support-advisory-and-reporting-state-controls"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-171" in slices["2025-support-advisory-and-reporting-state-controls"]["requirements"]
    assert "HLA2025-FI-SVC-183" in slices["2025-support-advisory-and-reporting-state-controls"]["requirements"]
    assert "HLA2025-FI-SVC-187" in slices["2025-support-advisory-and-reporting-state-controls"]["requirements"]
    assert "service reporting" in slices["2025-support-advisory-and-reporting-state-controls"]["supported_scope"]
    assert "send-service-reports-to-file" in slices["2025-support-advisory-and-reporting-state-controls"]["supported_scope"]
    assert "bool validation" in slices["2025-support-advisory-and-reporting-state-controls"]["supported_scope"]
    assert slices["2025-support-runtime-policy-state-controls"]["status"] == "implemented-slice"
    assert slices["2025-support-runtime-policy-state-controls"]["requirements"] == ("HLA2025-FI-SVC-181",)
    assert "automatic resign" in slices["2025-support-runtime-policy-state-controls"]["supported_scope"]
    assert "ResignAction validation" in slices["2025-support-runtime-policy-state-controls"]["supported_scope"]
    assert slices["2025-callback-control-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-193" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-194" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-195" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-196" in slices["2025-callback-control-services"]["requirements"]
    assert "disableCallbacks queues local and target federate callbacks" in slices["2025-callback-control-services"]["supported_scope"]
    assert "hosted FedPro 2025 route now carries explicit enableCallbacks/disableCallbacks transport calls" in slices["2025-callback-control-services"]["supported_scope"]
    assert "evokeMultipleCallbacks drains the pending callback queue" in slices["2025-callback-control-services"]["supported_scope"]
    assert slices["2025-ownership-divestiture-confirmation-flows"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-083" in slices["2025-ownership-divestiture-confirmation-flows"]["requirements"]
    assert "HLA2025-FI-SVC-087" in slices["2025-ownership-divestiture-confirmation-flows"]["requirements"]
    assert "HLA2025-FI-SVC-095" in slices["2025-ownership-divestiture-confirmation-flows"]["requirements"]
    assert "HLA2025-MOD-005" in slices["2025-ownership-divestiture-confirmation-flows"]["requirements"]
    assert "confirmDivestiture transfer" in slices["2025-ownership-divestiture-confirmation-flows"]["supported_scope"]
    assert "cancelNegotiatedAttributeOwnershipDivestiture" in slices["2025-ownership-divestiture-confirmation-flows"]["supported_scope"]
    assert slices["2025-ownership-release-and-if-wanted-flows"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-092" in slices["2025-ownership-release-and-if-wanted-flows"]["requirements"]
    assert "HLA2025-FI-SVC-094" in slices["2025-ownership-release-and-if-wanted-flows"]["requirements"]
    assert "HLA2025-MOD-005" in slices["2025-ownership-release-and-if-wanted-flows"]["requirements"]
    assert "requestAttributeOwnershipRelease" in slices["2025-ownership-release-and-if-wanted-flows"]["supported_scope"]
    assert "divestiture-if-wanted transfer" in slices["2025-ownership-release-and-if-wanted-flows"]["supported_scope"]
    assert slices["2025-ownership-acquisition-assumption-flows"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-085" in slices["2025-ownership-acquisition-assumption-flows"]["requirements"]
    assert "HLA2025-FI-SVC-089" in slices["2025-ownership-acquisition-assumption-flows"]["requirements"]
    assert "HLA2025-MOD-005" in slices["2025-ownership-acquisition-assumption-flows"]["requirements"]
    assert "requestAttributeOwnershipAssumption" in slices["2025-ownership-acquisition-assumption-flows"]["supported_scope"]
    assert "attributeOwnershipAcquisition" in slices["2025-ownership-acquisition-assumption-flows"]["supported_scope"]
    assert "ownership acquisition notification" in slices["2025-ownership-acquisition-assumption-flows"]["supported_scope"]
    assert slices["2025-ownership-acquisition-availability-cancellation-flows"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-090" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["requirements"]
    assert "HLA2025-FI-SVC-097" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["requirements"]
    assert "HLA2025-MOD-005" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["requirements"]
    assert "attributeOwnershipAcquisitionIfAvailable" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["supported_scope"]
    assert "confirmAttributeOwnershipAcquisitionCancellation" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["supported_scope"]
    assert "ownership-unavailable callbacks" in slices["2025-ownership-acquisition-availability-cancellation-flows"]["supported_scope"]
    assert slices["2025-ownership-query-and-resign-policies"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-098" in slices["2025-ownership-query-and-resign-policies"]["requirements"]
    assert "HLA2025-FI-SVC-100" in slices["2025-ownership-query-and-resign-policies"]["requirements"]
    assert "queryAttributeOwnership" in slices["2025-ownership-query-and-resign-policies"]["supported_scope"]
    assert "resign-time ownership policies" in slices["2025-ownership-query-and-resign-policies"]["supported_scope"]
    assert "divest/transfer owned attributes" in slices["2025-ownership-query-and-resign-policies"]["supported_scope"]
    assert slices["2025-support-federate-and-object-identity-lookups"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-138" in slices["2025-support-federate-and-object-identity-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-144" in slices["2025-support-federate-and-object-identity-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-140" in slices["2025-support-federate-and-object-identity-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-142" in slices["2025-support-federate-and-object-identity-lookups"]["requirements"]
    assert "federate, object-class, known-object-class, and object-instance" in slices["2025-support-federate-and-object-identity-lookups"]["supported_scope"]
    assert "joined-member identity lookup stops after resign" in slices["2025-support-federate-and-object-identity-lookups"]["supported_scope"]
    assert "decode-oriented object/class/instance catalog lookups remain available" in slices["2025-support-federate-and-object-identity-lookups"]["supported_scope"]
    assert slices["2025-support-attribute-interaction-catalog-lookups"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-145" in slices["2025-support-attribute-interaction-catalog-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-152" in slices["2025-support-attribute-interaction-catalog-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-149" in slices["2025-support-attribute-interaction-catalog-lookups"]["requirements"]
    assert "attribute, interaction-class, and parameter handle/name lookups" in slices["2025-support-attribute-interaction-catalog-lookups"]["supported_scope"]
    assert slices["2025-support-policy-update-and-transport-lookups"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-147" in slices["2025-support-policy-update-and-transport-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-154" in slices["2025-support-policy-update-and-transport-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-156" in slices["2025-support-policy-update-and-transport-lookups"]["requirements"]
    assert "order-type, update-rate, and transportation lookups" in slices["2025-support-policy-update-and-transport-lookups"]["supported_scope"]
    assert slices["2025-support-interaction-dimension-and-range-lookups"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-158" in slices["2025-support-interaction-dimension-and-range-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-163" in slices["2025-support-interaction-dimension-and-range-lookups"]["requirements"]
    assert "interaction available-dimension lookup and joined-region range-bounds" in slices["2025-support-interaction-dimension-and-range-lookups"]["supported_scope"]
    assert slices["2025-support-advisory-and-reporting-state-inquiries"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-170" in slices["2025-support-advisory-and-reporting-state-inquiries"]["requirements"]
    assert "HLA2025-FI-SVC-186" in slices["2025-support-advisory-and-reporting-state-inquiries"]["requirements"]
    assert "advisory and reporting-state inquiry switches" in slices["2025-support-advisory-and-reporting-state-inquiries"]["supported_scope"]
    assert slices["2025-support-runtime-policy-state-inquiries"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-180" in slices["2025-support-runtime-policy-state-inquiries"]["requirements"]
    assert "HLA2025-FI-SVC-192" in slices["2025-support-runtime-policy-state-inquiries"]["requirements"]
    assert "automatic resign directive, auto-provide, delay-subscription-evaluation" in slices["2025-support-runtime-policy-state-inquiries"]["supported_scope"]
    assert slices["2025-mom-service-report-records"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-007" in slices["2025-mom-service-report-records"]["requirements"]
    assert "service-report callback delivery" in slices["2025-mom-service-report-records"]["supported_scope"]
    assert "JSON-safe arguments and returned values" in slices["2025-mom-service-report-records"]["supported_scope"]
    assert slices["2025-mom-manager-action-routing"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-007" in slices["2025-mom-manager-action-routing"]["requirements"]
    assert "service/exception reporting adjust interactions" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "HLAsetSwitches, HLAsetTiming, and HLAmodifyAttributeState" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "declaration-management MOM service actions" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "federation-management MOM service actions" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "supported time-management MOM service actions" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "disable, asynchronous-delivery, TARA, NMR, and NMRA paths" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "supported object-management and ownership MOM service actions" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "order-type-change" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "HLAreportMOMexception" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert "not full MOM manager action routing" in slices["2025-mom-manager-action-routing"]["supported_scope"]
    assert slices["2025-mom-manager-query-and-report-routing"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-007" in slices["2025-mom-manager-query-and-report-routing"]["requirements"]
    assert "MIM data, FOM module data, and synchronization point/status" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "federate-level FOM module data, publication/subscription, object-instance information, and activity/count MOM reports" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "reports standard MIM data for HLArequestMIMdata" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "FOM module data for HLArequestFOMmoduleData" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "object publication/subscription state" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "object instance information for HLArequestObjectInstanceInformation" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "object-instance counts for deletable/updated/reflected objects" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "activity counts for updates, reflections, interactions sent" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "synchronization point/status reports" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert "not full MOM manager query/report routing" in slices["2025-mom-manager-query-and-report-routing"]["supported_scope"]
    assert slices["2025-wsdl-legacy-only"]["status"] == "legacy-only"
    assert "HLA2025-RET-003" in slices["2025-wsdl-legacy-only"]["requirements"]
    assert slices["2025-verification-anchor-matrix"]["status"] == "implemented-slice"
    assert "HLA2025-VER-001" in slices["2025-verification-anchor-matrix"]["requirements"]
    assert slices["2025-python-rti-milestone-ledger"]["status"] == "implemented-slice"
    assert "HLA2025-MIL-001" in slices["2025-python-rti-milestone-ledger"]["requirements"]
    assert "HLA2025-MIL-006" in slices["2025-python-rti-milestone-ledger"]["requirements"]
    assert "bounded Python 2025 finish-line gates explicit" in slices["2025-python-rti-milestone-ledger"]["supported_scope"]

    matrix_rows = {row["id"]: row for row in snapshot["verification_matrix"]["rows"]}
    assert matrix_rows["HLA2025-NEW-001"]["explicit_disposition_anchor"] is False
    assert "2025-directed-interaction-boundary" in matrix_rows["HLA2025-NEW-001"]["evidence_slices"]
    assert matrix_rows["HLA2025-RET-003"]["explicit_disposition_anchor"] is True
    assert "2025-verification-anchor-matrix" in matrix_rows["HLA2025-VER-001"]["evidence_slices"]
    assert "2025-python-rti-milestone-ledger" in matrix_rows["HLA2025-MIL-001"]["evidence_slices"]
    assert "2025-python-rti-milestone-ledger" in matrix_rows["HLA2025-MIL-006"]["evidence_slices"]

    python2025_source_audit = snapshot["python2025_source_responsibility_audit"]
    shim_families = {family["family"]: family for family in python2025_source_audit["families"]}
    impact_rows = {row["slice_id"]: row for row in snapshot["extraction_impact_audit"]["rows"]}
    extraction_readiness = snapshot["extraction_readiness_audit"]
    time_window_vendor_parity = snapshot["time_window_vendor_parity_audit"]
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    markdown = "\n".join(build_spec2025_finish_line_markdown(ROOT))
    assert "HLA conformance" in markdown
    assert "Closeout Readiness" in markdown
    assert "Promotion Vs Split Audit" in markdown
    assert "Pytest Anchor Audit" in markdown
    assert "Anchored requirements: 718" in markdown
    assert "Unanchored Requirement Audit" in markdown
    assert "Unanchored ledger requirements: 0" in markdown
    assert "FI Service Proof Audit" in markdown
    assert "Service rows: 196" in markdown
    assert "Ready for per-service runtime traceability claim: True" in markdown
    assert "Delta Requirement Proof Audit" in markdown
    assert "Delta rows: 20" in markdown
    assert "Binding Requirement Proof Audit" in markdown
    assert "Binding rows: 3" in markdown
    assert "OMT Requirement Proof Audit" in markdown
    assert "OMT rows: 454" in markdown
    assert "Callback Proof Audit" in markdown
    assert "Callback Route Parity Audit" in markdown
    assert "Callback rows: 55" in markdown
    assert "Hosted/direct route-backed callbacks: 55" in markdown
    assert "Callback-helper-only rows: 0" in markdown
    assert "Ready for full Python-lane callback route parity claim: True" in markdown
    assert "Ready for callback surface traceability claim: True" in markdown
    assert "Ready for callback-by-callback working-surface claim: True" in markdown
    assert "Support-Service Proof Audit" in markdown
    assert "Support-service rows: 62" in markdown
    assert "Complete negative-path rows: 61" in markdown
    assert "Ready for support-service traceability claim: True" in markdown
    assert "Python RTI Milestone Audit" in markdown
    assert "Audit status: bounded-python-rti-milestones" in markdown
    assert "Milestones per route: 6" in markdown
    assert "python-2025-inprocess" in markdown
    assert "python-2025-fedpro-grpc" in markdown
    assert "Best-attempt Python RTI 2025 working surface: bounded-working-slice" in markdown
    assert "Message exchange and routing: covered-routing-slice" in markdown
    assert "Time synchronization and advance flow: covered-time-advance-slice" in markdown
    assert "GALT and LITS behavior: bounded-query-evidence" in markdown
    assert "Lookahead handling and windows: bounded-lookahead-evidence" in markdown
    assert "future-exclusion, output-delivery, consumer-order, pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline resume, and time-window proof" in markdown
    assert "negative-oracle guards rejecting mismatched LITS boundaries, premature output, reversed consumer order, cross-window contamination, and dirty post-restore replay" in markdown
    assert "save-restore lookahead rollback with queued-TSO redelivery" in markdown
    assert "Requirement-By-Requirement Audit" in markdown
    assert "Audit status: row-level-requirement-disposition-audit-captured" in markdown
    assert "Ready for row-level audit claim: True" in markdown
    assert "Duplicate Umbrella Mapping Audit" in markdown
    assert "Framework doc path: docs/requirements/ieee-1516-2025/framework_rules.md" in markdown
    assert "Delta doc path: docs/requirements/ieee-1516-2025/callback_binding_deltas.md" in markdown
    assert "Ready for duplicate umbrella mapping claim: True" in markdown
    assert "framework-umbrella: 10 rows" in markdown
    assert "delta-umbrella: 12 rows" in markdown
    assert "Retired Legacy Mapping Audit" in markdown
    assert "Doc path: docs/requirements/ieee-1516-2025/retired_legacy_mapping.md" in markdown
    assert "Ready for retired legacy mapping claim: True" in markdown
    assert "Federate Interface legacy API: 11 rows" in markdown
    assert "OMT legacy schema: 13 rows" in markdown
    assert "Save/Restore Bounded Proof Audit" in markdown
    assert "Doc path: docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md" in markdown
    assert "Ready for save/restore bounded proof claim: True" in markdown
    assert "Callback Bounded Proof Audit" in markdown
    assert "Doc path: docs/requirements/ieee-1516-2025/callback_bounded_proof.md" in markdown
    assert "Ready for callback bounded proof claim: True" in markdown
    assert "Lookahead Window Bounded Proof Audit" in markdown
    assert "Doc path: docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md" in markdown
    assert "Ready for lookahead window bounded proof claim: True" in markdown
    assert "Pitch probe routes: ./tools/pitch time-window-probe, ./tools/pitch time-window-restore-state-probe" in markdown
    assert "Requirement-by-requirement area closure:" in markdown
    assert "Completion Claim Audit" in markdown
    assert "Ready for supported-boundary statement: True" in markdown
    assert "Ready for full 2025 conformance claim: False" in markdown
    assert "Covered rows: 645" in markdown
    assert "Supported Boundary Statement" in markdown
    assert "Status: supported-boundary-statement" in markdown
    assert "Ready: True" in markdown
    assert "Implementation Concentration Audit" in markdown
    assert "Runtime backend-backed slices: 42" in markdown
    assert "Runtime backend slice share: 0.553" in markdown
    assert "Semantic concentration is material: False" in markdown
    assert "Leading extracted runtime owners:" in markdown
    assert "- packages/hla-backend-python2025/src/hla/backends/python2025/hosted_fedpro.py:" in markdown
    assert "Python 2025 Source Responsibility Audit" in markdown
    assert f"Source line count: {current_python2025_line_count}" in markdown
    assert (
        f"Extracted runtime helper modules: {python2025_source_audit['extracted_runtime_module_count']}" in markdown
    )
    assert (
        f"Extracted runtime helper lines: {python2025_source_audit['extracted_runtime_module_line_count']}" in markdown
    )
    assert f"Runtime ambassador methods: {python2025_source_audit['ambassador_method_count']}" in markdown
    assert (
        f"Largest family: {python2025_source_audit['largest_family']} "
        f"({python2025_source_audit['largest_family_line_count']} lines)"
    ) in markdown
    assert (
        f"object-attribute-runtime: {shim_families['object-attribute-runtime']['method_count']} methods, "
        f"{shim_families['object-attribute-runtime']['line_count']} lines"
    ) in markdown
    assert (
        f"federation-management-runtime: {shim_families['federation-management-runtime']['method_count']} methods, "
        f"{shim_families['federation-management-runtime']['line_count']} lines"
    ) in markdown
    if "time-management-runtime" in shim_families:
        assert (
            f"time-management-runtime: {shim_families['time-management-runtime']['method_count']} methods, "
            f"{shim_families['time-management-runtime']['line_count']} lines"
        ) in markdown
    if "mom-and-switch-services" in shim_families:
        assert (
            f"mom-and-switch-services: {shim_families['mom-and-switch-services']['method_count']} methods, "
            f"{shim_families['mom-and-switch-services']['line_count']} lines"
        ) in markdown
    if "interaction-routing-runtime" in shim_families:
        assert (
            f"interaction-routing-runtime: {shim_families['interaction-routing-runtime']['method_count']} methods, "
            f"{shim_families['interaction-routing-runtime']['line_count']} lines"
        ) in markdown
    if "ownership-runtime" in shim_families:
        assert (
            f"ownership-runtime: {shim_families['ownership-runtime']['method_count']} methods, "
            f"{shim_families['ownership-runtime']['line_count']} lines"
        ) in markdown
    if "save-restore-runtime" in shim_families:
        assert (
            f"save-restore-runtime: {shim_families['save-restore-runtime']['method_count']} methods, "
            f"{shim_families['save-restore-runtime']['line_count']} lines"
        ) in markdown
    assert (
        f"time-management-runtime: {shim_families['time-management-runtime']['method_count']} methods, "
        f"{shim_families['time-management-runtime']['line_count']} lines"
    ) in markdown
    assert "packages/hla-backend-python2025/src/hla/backends/python2025/attribute_policy.py: object-attribute-runtime" in markdown
    assert (
        "packages/hla-backend-python2025/src/hla/backends/python2025/support_services_runtime.py: "
        "object-attribute-runtime, 28 functions"
    ) in markdown
    assert "Slice Aggregation Pressure Audit" in markdown
    assert "Aggregated slices >=10 requirements: 10" in markdown
    assert "Aggregated slices >=20 requirements and runtime-backed: 2" in markdown
    assert "2025-omt-xs-any-extension-tolerance: 45 requirements" in markdown
    assert "2025-ddm-default-attribute-policy: 23 requirements" in markdown
    assert "Service Utilization Decomposition Audit" in markdown
    assert "Slice id: 2025-service-utilization-crosscheck" in markdown
    assert "Family count: 11" in markdown
    assert "All service-utilization rows family-mapped: True" in markdown
    assert "federation_management: 17 services (1..17), traceable=True" in markdown
    assert "support_services: 55 services (138..192), traceable=True" in markdown
    assert "OMT Extended Subset Decomposition Audit" in markdown
    assert "Slice id: 2025-omt-extended-supported-subset" in markdown
    assert "All extended-subset rows family-mapped: True" in markdown
    assert "model-identification-and-taxonomy: 8 requirements (1..83), in-slice=True" in markdown
    assert "object-attribute-and-class-metadata: 33 requirements (16..73), in-slice=True" in markdown
    assert "interaction-parameter-and-routing-metadata: 36 requirements (86..139), in-slice=True" in markdown
    assert "datatype-table-roundtrip: 18 requirements (148..188), in-slice=True" in markdown
    assert "container-reference-and-table-sections: 15 requirements (199..223), in-slice=True" in markdown
    assert "OMT xs:any Extension Decomposition Audit" in markdown
    assert "Slice id: 2025-omt-xs-any-extension-tolerance" in markdown
    assert "All xs:any extension rows family-mapped: True" in markdown
    assert "object-model-root-and-identity: 2 requirements (6..8), in-slice=True" in markdown
    assert "object-class-and-attribute-extension-points: 16 requirements (19..82), in-slice=True" in markdown
    assert "interaction-class-and-parameter-extension-points: 8 requirements (102..134), in-slice=True" in markdown
    assert "datatype-and-encoding-extension-points: 12 requirements (145..198), in-slice=True" in markdown
    assert "container-table-and-reference-extension-points: 7 requirements (202..224), in-slice=True" in markdown
    assert "OMT Schema Constraint Decomposition Audit" in markdown
    assert "Slice id: 2025-omt-schema-constraint-validation" in markdown
    assert "All schema-constraint rows family-mapped: True" in markdown
    assert "xsd-key-constraints: 5 requirements (1..9), in-slice=True" in markdown
    assert "xsd-keyref-constraints: 5 requirements (2..10), in-slice=True" in markdown
    assert "xsd-unique-constraints: 4 requirements (11..14), in-slice=True" in markdown
    assert "enumeration-and-union-domain-constraints: 15 requirements (15..29), in-slice=True" in markdown
    assert "Save/Restore Decomposition Audit" in markdown
    assert "Slice id: 2025-save-restore-lifecycle" in markdown
    assert "Proof families: 5" in markdown
    assert "save-restore/time-window-and-time-state-rollback" in markdown
    assert "Save/Restore Requirement-Family Audit" in markdown
    assert "Family count: 5" in markdown
    assert "All save/restore rows family-mapped: True" in markdown
    assert "lifecycle-control: 13 requirements, in-slice=True" in markdown
    assert "shared-scenario-rollback: 1 requirements, in-slice=True" in markdown
    assert "routing-policy-rollback: 4 requirements, in-slice=True" in markdown
    assert "ownership-rollback: 1 requirements, in-slice=True" in markdown
    assert "time-window-and-time-state-rollback: 1 requirements, in-slice=True" in markdown
    assert "Federation-Management Decomposition Audit" in markdown
    assert "Slice id: 2025-federation-management-proof-families" in markdown
    assert "Proof families: 6" in markdown
    assert "federation-management/connect-create-destroy-and-catalog-control" in markdown
    assert "federation-management/save-restore-participant-recovery-and-branching" in markdown
    assert "Callback Decomposition Audit" in markdown
    assert "Slice id: 2025-callback-proof-families" in markdown
    assert "Proof families: 8" in markdown
    assert "callbacks/declaration-relevance-and-interest-advisories" in markdown
    assert "callbacks/callback-control-and-backlog-hygiene" in markdown
    assert "Time-Management Decomposition Audit" in markdown
    assert "Slice id: 2025-time-management-proof-families" in markdown
    assert "Proof families: 5" in markdown
    assert "time-management/factory-mode-enable-and-request-primitives" in markdown
    assert "time-management/save-restore-time-state-and-lookahead-rollback" in markdown
    assert "Binding-Route Decomposition Audit" in markdown
    assert "Slice id: 2025-binding-route-proof-families" in markdown
    assert "Proof families: 6" in markdown
    assert "binding-routes/java-binding-source-and-intake-evidence" in markdown
    assert "binding-routes/cross-route-scenario-parity-ledger" in markdown
    assert "Support-Services Decomposition Audit" in markdown
    assert "Slice id: 2025-support-services-proof-families" in markdown
    assert "Proof families: 5" in markdown
    assert "support-services/name-reservation-and-release-flows" in markdown
    assert "support-services/factory-decode-and-hosted-support-seam" in markdown
    assert "Object-Management Decomposition Audit" in markdown
    assert "Slice id: 2025-object-management-proof-families" in markdown
    assert "Proof families: 7" in markdown
    assert "object-management/declaration-and-basic-exchange-gating" in markdown
    assert "object-management/object-region-scope-and-passive-alias-routing" in markdown
    assert "Directed Interaction Decomposition Audit" in markdown
    assert "Slice id: 2025-directed-interaction-boundary" in markdown
    assert "directed-interaction/ddm-overlap-filtering" in markdown
    assert "Directed Interaction Requirement-Family Audit" in markdown
    assert "All directed-interaction rows family-mapped: True" in markdown
    assert "declaration-publication-control: 2 requirements, in-slice=True" in markdown
    assert "declaration-subscription-control: 2 requirements, in-slice=True" in markdown
    assert "send-receive-routing-and-hla-surface: 4 requirements, in-slice=True" in markdown
    assert "directed-interaction-delta-rows: 2 requirements, in-slice=True" in markdown
    assert "service-group-matrix-traceability: 1 requirements, in-slice=True" in markdown
    assert "DDM Default-Policy Decomposition Audit" in markdown
    assert "Slice id: 2025-ddm-default-attribute-policy" in markdown
    assert "ddm-default-policy/object-region-routing-and-scope-advisories" in markdown
    assert "Wrapper-Boundary Family Route-Backing Audit" in markdown
    assert "Family count: 22" in markdown
    assert "All families route-backed across current Python lanes: True" in markdown
    assert "Wrapper-Boundary Family Asymmetry Audit" in markdown
    assert "Balanced families: 22" in markdown
    assert "Direct-heavier families: 0" in markdown
    assert "Hosted-heavier families: 0" in markdown
    assert "Current Lane Coherence Audit" in markdown
    assert "Ready for current-lane coherent working-surface claim: True" in markdown
    assert "Major pressure slice count: 3" in markdown
    assert "Python2025 backend concentration is material: False" in markdown
    assert "Current Lane Working-Surface Statement" in markdown
    assert "Status: current-lane-working-surface-statement" in markdown
    assert "Ready: True" in markdown
    assert "Evidence basis: route_summary.scenario_count=2" in markdown
    assert "federation_management_decomposition.slice_id=2025-federation-management-proof-families" in markdown
    assert "object_management_decomposition.slice_id=2025-object-management-proof-families" in markdown
    assert "Evidence basis: route_summary.scenarios=ddm,object_exchange,ownership" in markdown
    assert "Evidence basis: route_summary.scenarios=ownership,save_restore" in markdown
    assert "ownership_decomposition.slice_id=2025-ownership-proof-families" in markdown
    assert "time_management_decomposition.slice_id=2025-time-management-proof-families" in markdown
    assert "Evidence basis: omt_requirement_proof_audit.ready_for_omt_traceability_claim=true" in markdown
    assert "Evidence basis: route_summary.scenario_count=8" in markdown
    assert "support_services_decomposition.slice_id=2025-support-services-proof-families" in markdown
    assert "callback_decomposition.slice_id=2025-callback-proof-families" in markdown
    assert "binding_route_decomposition.slice_id=2025-binding-route-proof-families" in markdown
    assert "Implementation Lane Audit" in markdown
    assert "Current 2025 backend package: hla-backend-python2025" in markdown
    assert "Compatibility wrapper package: hla-backend-shim" in markdown
    assert "Compatibility wrapper status: compatibility-maintained" in markdown
    assert "Compatibility wrapper role: compatibility-wrapper" in markdown
    assert "Compatibility wrapper delegates runtime semantics to: hla-backend-python2025" in markdown
    assert "Python2025 Proof-Lane Audit" in markdown
    assert "Ready for main-implementation operator-lane claim: True" in markdown
    assert "Direct lane: ./tools/python verify-main-2025" in markdown
    assert "Hosted extension lane: ./tools/python verify-routes-2025" in markdown
    assert "Current operator runs:" in markdown
    assert "python-main-2025 / ./tools/python verify-main-2025: 324 passed across wrapper subcommands plus Target/Radar example" in markdown
    assert "python-routes-2025 / ./tools/python verify-routes-2025: 434 passed across direct-plus-hosted wrapper subcommands plus finish-line bundle and Target/Radar example" in markdown
    assert "Evidence anchors: testing/test_surface_manifest.json, tools/python, docs/test_surface.md, README.md" in markdown
    assert "Reference 2010 backend package: hla-backend-inmemory" in markdown
    assert "Backend packages discovered: 6" in markdown
    assert "Dedicated 2025 candidates cleanly separated: True" in markdown
    assert "Dedicated 2025 legacy-package delegation violations: 0" in markdown
    assert "hla-backend-cpp-shim" in markdown
    assert "shim (shim): hla-backend-shim supports rti1516_2025" not in markdown
    assert "Dedicated 2025 backend package present: True" in markdown
    assert "python-2025-fedpro-grpc: hosted-transport-route" in markdown
    assert "Time-Window Vendor Parity Audit" in markdown
    assert (
        "Trial-Pitch-safe routes: "
        f"{', '.join(time_window_vendor_parity['trial_pitch_safe_route_ids'])}"
    ) in markdown
    assert (
        "Current trial candidate: "
        f"{time_window_vendor_parity['current_trial_candidate']['scenario_id']} "
        f"({time_window_vendor_parity['current_trial_candidate']['federate_count']} federates)"
    ) in markdown
    for route in time_window_vendor_parity["routes"]:
        assert (
            f"{route['scenario_id']}: federates={route['federate_count']}, "
            f"trial-pitch-safe={route['trial_pitch_safe']}, "
            f"boundary={route['current_pitch_runtime_boundary']}"
        ) in markdown
    assert "Extraction Readiness Audit" in markdown
    assert "Future backend package target: hla-backend-python2025" in markdown
    assert (
        "Runtime semantics to extract first: "
        f"{extraction_readiness['runtime_semantics_to_extract_first_count']}"
    ) in markdown
    for row in extraction_readiness["runtime_semantics_to_extract_first"]:
        assert (
            f"{row['slice_id']}: {row['proof_family_count']} proof families, "
            f"direct={row['direct_test_count']}, hosted={row['hosted_test_count']}, "
            f"route-backed={row['route_backed']}"
        ) in markdown
    assert extraction_readiness["shim_responsibilities_after_extraction"][0] in markdown
    assert extraction_readiness["pre_extraction_gates"][0] in markdown
    assert "Extraction package contract:" in markdown
    assert "Current package state: live-runtime-present" in markdown
    assert "Target import root: hla.backends.python2025" in markdown
    assert "Target backend name: python2025" in markdown
    assert "Must not delegate to: hla.backends.shim.backend.create_shim_backend" in markdown
    assert "Extraction cutover invariants:" in markdown
    assert "hla-backend-shim keeps only route normalization, compatibility aliases, and binding bridge behavior" in markdown
    assert "Extraction Impact Audit" in markdown
    assert f"Candidate slices: {snapshot['extraction_impact_audit']['slice_count']}" in markdown
    assert (
        f"Largest current source baseline: {snapshot['extraction_impact_audit']['largest_current_source_baseline']}"
        in markdown
    )
    assert (
        f"2025-save-restore-lifecycle: source families=4, baseline="
        f"{impact_rows['2025-save-restore-lifecycle']['current_source_line_baseline']} lines/"
        f"{impact_rows['2025-save-restore-lifecycle']['current_source_method_baseline']} methods"
    ) in markdown
    assert (
        f"2025-directed-interaction-boundary: source families=3, baseline="
        f"{impact_rows['2025-directed-interaction-boundary']['current_source_line_baseline']} lines/"
        f"{impact_rows['2025-directed-interaction-boundary']['current_source_method_baseline']} methods"
    ) in markdown
    assert (
        f"2025-ddm-default-attribute-policy: source families=4, baseline="
        f"{impact_rows['2025-ddm-default-attribute-policy']['current_source_line_baseline']} lines/"
        f"{impact_rows['2025-ddm-default-attribute-policy']['current_source_method_baseline']} methods"
    ) in markdown
    assert "line baselines are intentionally overlapping" in markdown
    assert "Objective Audit" in markdown
    assert "Surface claim: bounded-working-surface" in markdown
    assert "Bounded-ready dimensions: 8 / 8" in markdown
    assert "Federation Management" in markdown
    assert "OMT Handling" in markdown
    assert "per-service runtime traceability plus complete actionable negative-path coverage" in markdown
    assert "Ready for slice closeout: True" in markdown
    assert "Ready for full completion claim: False" in markdown
    assert "Conformance blockers:" in markdown
    assert "Requirement-by-requirement duplicate/umbrella breakdown:" in markdown
    assert "delta-umbrella: 12 rows" in markdown
    assert "framework-umbrella: 10 rows" in markdown
    assert "Highest-Priority Open Work" in markdown
    assert "2025-wsdl-legacy-only" in markdown
    assert "Do not promote `partial` rows" in markdown


@pytest.mark.requirements("HLA2025-TRACE-001")
def test_2025_finish_line_writer_emits_reviewable_json_and_markdown(tmp_path: Path) -> None:
    paths = write_spec2025_finish_line(tmp_path, ROOT)

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["executable_test_backlog"]["row_count"] == 1117
    assert payload["requirement_depth_expansion"]["row_count"] == 691
    assert payload["requirement_coverage_disposition"]["covered_row_count"] == 645
    assert payload["verification_matrix"]["high_priority_missing_anchor_count"] == 0
    assert payload["requirement_pytest_anchor_audit"]["row_count"] == 718
    assert payload["unanchored_requirement_audit"]["row_count"] == 0
    assert payload["route_parity_matrix"]["by_status"]["missing"] == 0
    payload_route_rows = {
        (row["scenario"], row["route"]): row
        for row in payload["route_parity_matrix"]["rows"]
    }
    assert payload_route_rows[("federation_lifecycle", "python-2025-inprocess")]["runtime_provider"] == "python2025"
    assert payload_route_rows[("federation_lifecycle", "python-2025-inprocess")]["implementation_lane"] == "hla-backend-python2025"
    assert payload_route_rows[("federation_lifecycle", "python-2025-inprocess")]["counts_as_python_2025_rti"] is True
    assert payload_route_rows[("federation_lifecycle", "python-2025-inprocess")]["wrapper_only"] is False
    assert payload_route_rows[("time_management", "python-2025-fedpro-grpc")]["runtime_provider"] == "python2025"
    assert payload_route_rows[("time_management", "python-2025-fedpro-grpc")]["implementation_lane"] == "hla-backend-python2025"
    assert payload_route_rows[("time_management", "python-2025-fedpro-grpc")]["counts_as_python_2025_rti"] is True
    assert payload_route_rows[("time_management", "python-2025-fedpro-grpc")]["wrapper_only"] is False
    assert payload["fi_service_proof_audit"]["row_count"] == 196
    assert payload["fi_service_proof_audit"]["ready_for_per_service_runtime_traceability_claim"] is True
    assert payload["delta_requirement_proof_audit"]["row_count"] == 20
    assert payload["delta_requirement_proof_audit"]["ready_for_delta_traceability_claim"] is True
    assert payload["binding_requirement_proof_audit"]["row_count"] == 3
    assert payload["binding_requirement_proof_audit"]["ready_for_binding_traceability_claim"] is True
    assert payload["omt_requirement_proof_audit"]["row_count"] == 454
    assert payload["omt_requirement_proof_audit"]["ready_for_omt_traceability_claim"] is True
    assert payload["python_rti_milestone_audit"]["audit_status"] == "bounded-python-rti-milestones"
    assert payload["python_rti_milestone_audit"]["milestone_count"] == 6
    assert payload["python_rti_milestone_audit"]["row_count"] == 12
    assert payload["python_rti_milestone_audit"]["by_route"]["python-2025-fedpro-grpc"]["all_route_parity_covered"] is True
    assert payload["requirement_by_requirement_audit"]["audit_status"] == "row-level-requirement-disposition-audit-captured"
    assert payload["requirement_by_requirement_audit"]["ready_for_row_level_requirement_audit_claim"] is True
    assert payload["completion_claim_audit"]["ready_for_supported-boundary_statement"] is True
    assert payload["completion_claim_audit"]["ready_for_full_2025_conformance_claim"] is False
    assert payload["supported_boundary_statement"]["ready"] is True
    assert payload["implementation_lane_audit"]["audit_status"] == "current-lane-architecture-captured"
    assert payload["implementation_lane_audit"]["current_2025_lane"]["backend_package"] == "hla-backend-python2025"
    assert payload["implementation_lane_audit"]["reference_2010_lane"]["backend_package"] == "hla-backend-inmemory"
    assert payload["implementation_lane_audit"]["dedicated_2025_backend_package_present"] is True
    assert payload["implementation_lane_audit"]["python_2025_routes"][1]["route"] == "python-2025-fedpro-grpc"
    assert payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["route"] == "python-2025-fedpro-grpc"
    assert payload["implementation_lane_audit"]["hosted_factory_boundary_evidence"]["audit_status"] == (
        "factory-boundary-explicit"
    )
    assert (
        payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["hosted_client_report"]["implementation_lane"]
        == "hla-backend-python2025"
    )
    assert (
        payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["hosted_server_report"]["transport_kind"]
        == "grpc"
    )
    assert (
        payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["direct_runtime_report"]["backend_kind"]
        == "python/2025"
    )
    assert payload["supported_boundary_statement"]["statement_status"] == "supported-boundary-statement"
    assert payload["promotion_split_audit"]["ready_for_current_lane_promotion_as_working_surface"] is True
    assert payload["promotion_split_audit"]["ready_for_permanent_no-split_decision"] is False
    assert payload["objective_dimension_audit"]["ready_for_bounded_working_surface_claim"] is True
    assert payload["objective_dimension_audit"]["ready_for_full_2025_completion_claim"] is False
    assert payload["main_python2025_implementation_claim_audit"]["ready_for_main_python2025_implementation_claim"] is True
    assert payload["main_python2025_implementation_claim_audit"]["ready_for_full_2025_conformance_claim"] is False
    assert payload["full_claim_blocker_partition_audit"]["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True
    assert payload["closeout_blocker_partition_audit"]["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True
    assert payload["closeout_readiness"]["ready_for_slice_closeout"] is True
    assert payload["closeout_readiness"]["ready_for_full_completion_claim"] is False

    markdown = paths["markdown"].read_text(encoding="utf-8")
    legacy_markdown = paths["legacy_markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert legacy_markdown == markdown
    assert "Imported requirement-depth rows: 691" in markdown
    assert "Imported provisional disposition rows: 691" in markdown
    assert "Closeout Readiness" in markdown
    assert "Closeout Blocker Partition Audit" in markdown
    assert "Pytest Anchor Audit" in markdown
    assert "Unanchored Requirement Audit" in markdown
    assert "FI Service Proof Audit" in markdown
    assert "Delta Requirement Proof Audit" in markdown
    assert "Binding Requirement Proof Audit" in markdown
    assert "OMT Requirement Proof Audit" in markdown
    assert "Python RTI Milestone Audit" in markdown
    assert "Requirement-By-Requirement Audit" in markdown
    assert "Completion Claim Audit" in markdown
    assert "Supported Boundary Statement" in markdown
    assert "Main Python2025 Implementation Claim Audit" in markdown
    assert "Full-Claim Blocker Partition Audit" in markdown
    assert "Objective Audit" in markdown
    assert "Implemented Evidence Slices" in markdown
    matrix = paths["verification_matrix"].read_text(encoding="utf-8")
    assert "HLA2025-VER-001" in matrix
    assert "2025-verification-anchor-matrix" in matrix
    assert "HLA2025-MIL-001" in matrix
    assert "2025-python-rti-milestone-ledger" in matrix
    route_matrix = paths["route_parity_matrix"].read_text(encoding="utf-8")
    route_matrix_markdown = paths["route_parity_markdown"].read_text(encoding="utf-8")
    assert (
        "scenario,route,status,evidence_scope,requirements,evidence_tests,evidence_artifacts,"
        "runtime_provider,implementation_lane,counts_as_python_2025_rti,wrapper_only,notes"
    ) in route_matrix
    assert "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,cpp-standard-2025-grpc,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,python-2025-inprocess,parity-covered,scenario-parity" in route_matrix
    assert ",python2025,hla-backend-python2025,true,false," in route_matrix
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in route_matrix
    assert "snake-case alias acceptance on the primary direct-runtime surface" in route_matrix
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python2025 lane" in route_matrix
    assert route_matrix_markdown.startswith("# IEEE 1516-2025 Route Parity Matrix")
    assert "python-2025-inprocess` and `python-2025-fedpro-grpc` are the Python-owned runtime evidence lanes over `hla-backend-python2025`" in route_matrix_markdown
    assert "Java/C++ standard routes are binding/adaptation-seam evidence over that same runtime, not alternate Python RTI implementations." in route_matrix_markdown
    assert "For the main-implementation claim, read the scenario rows as a proof-family ledger too:" in route_matrix_markdown
    assert "the Python-owned rows below are the main route-parity proof families for federation, object, ownership, DDM, time, save/restore, MOM, and support-services behavior" in route_matrix_markdown
    assert "those Python-owned rows are parity evidence over the extracted `hla-backend-python2025` runtime/state/surface modules" in route_matrix_markdown
    assert "hosted FedPro rows show transport-seam replay of those same runtime families rather than a different 2025 RTI owner" in route_matrix_markdown
    assert "| federation_lifecycle | python-2025-fedpro-grpc | parity-covered | scenario-parity |" in route_matrix_markdown
    assert "| time_management | python-2025-fedpro-grpc | parity-covered | scenario-parity |" in route_matrix_markdown
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in route_matrix_markdown
    assert "snake-case alias acceptance on the primary direct-runtime surface" in route_matrix_markdown
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python2025 lane" in route_matrix_markdown


@pytest.mark.requirements("HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_checked_in_generated_finish_line_artifacts_match_live_writers(tmp_path: Path) -> None:
    paths = write_spec2025_finish_line(tmp_path, ROOT)
    checked_in_dir = ROOT / "docs" / "plans"

    expected_files = {
        "json": "spec2025_finish_line_snapshot.json",
        "markdown": "spec2025_finish_line.md",
        "legacy_markdown": "2025_requirements_finish_line.md",
        "verification_matrix": "spec2025_verification_matrix.csv",
        "route_parity_matrix": "spec2025_route_parity_matrix.csv",
        "route_parity_markdown": "spec2025_route_parity_matrix.md",
    }

    for key, filename in expected_files.items():
        generated_text = paths[key].read_text(encoding="utf-8")
        checked_in_text = (checked_in_dir / filename).read_text(encoding="utf-8")
        assert generated_text == checked_in_text, f"checked-in generated artifact drifted: {filename}"


def test_2025_checked_in_finish_line_snapshot_contains_only_live_pytest_anchors() -> None:
    payload = (ROOT / "docs" / "plans" / "spec2025_finish_line_snapshot.json").read_text(encoding="utf-8")
    anchors = sorted(set(re.findall(r"tests/[^\"]+\\.py::test_[A-Za-z0-9_]+", payload)))
    missing: list[str] = []
    for anchor in anchors:
        file_part, test_name = anchor.split("::", 1)
        file_path = ROOT / file_part
        if not file_path.exists():
            missing.append(anchor)
            continue
        if f"def {test_name}(" not in file_path.read_text(encoding="utf-8"):
            missing.append(anchor)
    assert missing == []


def test_2025_checked_in_plan_artifacts_keep_live_pytest_anchors() -> None:
    plan_artifacts = (
        ROOT / "docs" / "plans" / "spec2025_finish_line_snapshot.json",
        ROOT / "docs" / "plans" / "spec2025_finish_line.md",
        ROOT / "docs" / "plans" / "2025_requirements_finish_line.md",
        ROOT / "docs" / "plans" / "spec2025_route_parity_matrix.md",
        ROOT / "docs" / "plans" / "spec2025_route_parity_matrix.csv",
        ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md",
    )
    pattern = re.compile(r"tests/[^\"]+\\.py::test_[A-Za-z0-9_]+")
    missing: list[str] = []
    for artifact_path in plan_artifacts:
        text = artifact_path.read_text(encoding="utf-8")
        for anchor in sorted(set(pattern.findall(text))):
            file_part, test_name = anchor.split("::", 1)
            file_path = ROOT / file_part
            if not file_path.exists():
                missing.append(f"{artifact_path.name}: {anchor}")
                continue
            if f"def {test_name}(" not in file_path.read_text(encoding="utf-8"):
                missing.append(f"{artifact_path.name}: {anchor}")
    assert missing == []


def test_2025_checked_in_finish_line_artifacts_preserve_python2025_route_identity() -> None:
    payload = json.loads((ROOT / "docs" / "plans" / "spec2025_finish_line_snapshot.json").read_text(encoding="utf-8"))
    markdown = (ROOT / "docs" / "plans" / "spec2025_finish_line.md").read_text(encoding="utf-8")
    legacy_markdown = (ROOT / "docs" / "plans" / "2025_requirements_finish_line.md").read_text(encoding="utf-8")
    current_lane_statement = payload["current_lane_working_surface_statement"]
    main_impl_claim = payload["main_python2025_implementation_claim_audit"]
    route_rows = {
        (row["scenario"], row["route"]): row
        for row in payload["route_parity_matrix"]["rows"]
    }

    assert current_lane_statement["statement_status"] == "current-lane-working-surface-statement"
    assert current_lane_statement["ready"] is True
    assert "main full Python 2025 RTI implementation now runs from hla-backend-python2025 while hla-backend-shim is retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in current_lane_statement["statement"]
    assert "route-parity matrix now serves as the scenario-family ledger for federation, object, ownership, DDM, time, save/restore, MOM, and support-services evidence" in current_lane_statement["statement"]
    assert "use the route-parity matrix as the scenario-family ledger behind that claim" in current_lane_statement["current_assessment"]
    assert main_impl_claim["ready_for_main_python2025_implementation_claim"] is True
    assert main_impl_claim["ready_for_full_2025_conformance_claim"] is False
    assert main_impl_claim["implementation_owner"] == "hla-backend-python2025"
    assert "hla-backend-python2025 is the implementation owner for the real executable 2025 Python RTI surface" in main_impl_claim["claim"]
    assert "main python2025 RTI implementation claim is ready" in main_impl_claim["current_assessment"]
    blocker_partition = payload["full_claim_blocker_partition_audit"]
    assert blocker_partition["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True
    assert blocker_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert "all sit outside direct main-lane python2025 runtime completeness" in blocker_partition["current_assessment"]
    closeout_partition = payload["closeout_blocker_partition_audit"]
    assert closeout_partition["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True
    assert closeout_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert "all describe requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits" in closeout_partition["current_assessment"]

    assert route_rows[("federation_lifecycle", "python-2025-inprocess")]["runtime_provider"] == "python2025"
    assert route_rows[("federation_lifecycle", "python-2025-inprocess")]["implementation_lane"] == "hla-backend-python2025"
    assert route_rows[("federation_lifecycle", "python-2025-inprocess")]["counts_as_python_2025_rti"] is True
    assert route_rows[("federation_lifecycle", "python-2025-inprocess")]["wrapper_only"] is False
    assert route_rows[("time_management", "python-2025-fedpro-grpc")]["runtime_provider"] == "python2025"
    assert route_rows[("time_management", "python-2025-fedpro-grpc")]["implementation_lane"] == "hla-backend-python2025"
    assert route_rows[("time_management", "python-2025-fedpro-grpc")]["counts_as_python_2025_rti"] is True
    assert route_rows[("time_management", "python-2025-fedpro-grpc")]["wrapper_only"] is False
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert "snake-case alias acceptance on the primary direct-runtime surface" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python2025 lane" in route_rows[
        ("support_services", "python-2025-inprocess")
    ]["notes"]
    assert payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["audit_status"] == (
        "direct-server-client-identity-aligned"
    )
    hosted_factory_boundary = payload["implementation_lane_audit"]["hosted_factory_boundary_evidence"]
    assert hosted_factory_boundary["audit_status"] == "factory-boundary-explicit"
    assert hosted_factory_boundary["supported_hosted_creation_surface"] == (
        "start_2025_grpc_server(...) plus GrpcTransport(..., schema='rti1516_2025') plus "
        "create_rti_ambassador(backend='python2025'|'python-2025'|'python-2025-backend', "
        "transport={'kind': 'grpc', ...})"
    )
    assert hosted_factory_boundary["unsupported_factory_surfaces"] == [
        "create_rti_ambassador(backend='shim', transport=...)",
    ]
    assert "supported runtime aliases now accept transport=..." in hosted_factory_boundary["current_policy"]
    assert "legacy shim provider spelling is no longer part of the supported public backend-selection surface" in hosted_factory_boundary["current_policy"]
    assert "direct federation listing/member-report slice" in hosted_factory_boundary["current_policy"]
    assert "direct MOM request/report slice" in hosted_factory_boundary["current_policy"]
    assert "direct MOM object/ownership service slice" in hosted_factory_boundary["current_policy"]
    assert "direct timestamped delivery/retraction slice" in hosted_factory_boundary["current_policy"]
    assert "direct directed-interaction slice" in hosted_factory_boundary["current_policy"]
    assert "direct callback-backlog disconnect/rejoin slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore-control negative slice" in hosted_factory_boundary["current_policy"]
    assert "direct local-delete restore slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-callback restore cleanup slice" in hosted_factory_boundary["current_policy"]
    assert "direct timed-remove restore cleanup slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-object restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct plain-interaction restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct directed-DDM restore routing slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore time/switch-control slice" in hosted_factory_boundary["current_policy"]
    assert "direct restore lookahead/queued-TSO slice" in hosted_factory_boundary["current_policy"]
    assert "direct object-exchange slice" in hosted_factory_boundary["current_policy"]
    assert "direct ownership slice" in hosted_factory_boundary["current_policy"]
    assert hosted_factory_boundary["evidence_tests"] == [
        "tests/test_python_api_spec.py::test_runtime_backend_listing_exposes_python2025_as_primary_2025_lane",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_python2025_aliases_and_keeps_primary_identity",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_legacy_shim_provider_name",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_hosted_transport_on_python2025_aliases",
        "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_hosted_transport_on_legacy_shim_provider",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_accepts_hosted_transport_creation_on_python2025_lane",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_legacy_shim_provider_name",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_transport_route_creates_hosted_python2025_ambassador",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_restore_control_negative_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_local_delete_restore_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_timed_remove_and_preserves_post_restore_remove_routing",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_object_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_interaction_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_directed_ddm_subscriber_routing_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_time_and_switch_control_state_after_restore",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_lookahead_and_redelivers_presave_queued_tso",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_federation_management_service_interactions",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_request_report_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_object_and_ownership_service_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_shared_support_factory_and_decode_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_drops_disconnected_callback_backlog_before_reconnect",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_object_exchange_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_timestamped_delivery_and_retraction_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_ownership_slice",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_inflight_ownership_state",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_cross_federate_attribute_owner_visibility",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
        "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
        "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_unknown_backend_specific_options",
        "tests/test_hla_factory_composition.py::test_hla_factory_registry_strips_composition_only_options_before_2025_backend_creation",
        "tests/test_hla_factory_composition.py::test_2025_direct_factory_rejects_composition_only_options_without_hla_factory_layer",
        "tests/requirements/test_2025_python_rti_backend_audit.py::test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary",
    ]
    assert payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["hosted_client_report"] == {
        "runtime_provider": "python2025",
        "implementation_lane": "hla-backend-python2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
        "spec": "rti1516_2025",
        "transport_kind": "grpc",
        "route_family": "fedpro",
    }
    assert payload["implementation_lane_audit"]["package_owned_shared_scenario_evidence"] == {
        "adapter_class": "hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter",
        "audit_status": "package-owned-target-radar-2025-path-captured",
        "claim": (
            "The shared Target/Radar 2025 execution seam is now owned by the hla-fom-target-radar package, "
            "where one package-owned compatibility adapter wraps the primary python2025 backend lane without "
            "moving implementation ownership back into hla-backend-shim."
        ),
        "current_assessment": (
            "The README-advertised Target/Radar python2025 example path is now executable under package-owned "
            "2025 adapter coverage. The legacy shim package is no longer treated as a backend-selection route, "
            "and the same package-owned adapter now also proves that the factory-hosted python2025 FedPro route can execute "
            "the shared Target/Radar example scenario plus the shared future-exclusion, output-delivery, "
            "consumer-order, integrated lookahead-processing-window gauntlet, restore-state, restore-output-resume, "
            "and pipeline-resume scenarios without falling back to shim-owned semantics or raw transport-only wrappers."
        ),
        "evidence_tests": [
            "tests/scenarios/test_target_radar_scenario.py::test_target_radar_example_supports_2025_backends",
            "tests/test_fom_target_radar_split_package.py::test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter",
            "tests/test_fom_target_radar_split_package.py::test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_target_radar_shared_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
            "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
        ],
        "example_entrypoint": "python examples/target_radar_simulation.py --backend python2025 --steps 5",
        "python2025_runtime_report": {
            "backend_kind": "python/2025",
            "counts_as_python_2025_rti": True,
            "implementation_lane": "hla-backend-python2025",
            "wrapper_only": False,
        },
        "scenario_package": "hla-fom-target-radar",
        "shared_route": "target-radar-shared-scenario",
        "shim_runtime_report": {
            "backend_kind": "shim/2025",
            "counts_as_python_2025_rti": False,
            "implementation_lane": "hla-backend-python2025",
            "wrapper_only": True,
        },
        "supported_backend_names": [
            "python2025",
            "python-2025",
            "python-2025-backend",
        ],
    }
    assert payload["implementation_lane_audit"]["evidence_anchors"] == [
        "README.md",
        "docs/architecture.md",
        "docs/documentation_hierarchy.md",
        "docs/package_layout.md",
        "docs/test_surface.md",
        "docs/workspace_layout.md",
        "docs/rti_options_and_test_matrix.md",
        "docs/verification/time_model_compliance.md",
        "docs/verification/verification_plan.md",
        "docs/backend_route_inventory.md",
        "docs/backend_route_inventory_remote.md",
        "packages/hla-backend-python2025/pyproject.toml",
        "packages/hla-backend-python2025/README.md",
        "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
        "packages/hla-backend-shim/pyproject.toml",
        "packages/hla-backend-shim/README.md",
        "packages/hla-backend-shim/src/hla/backends/shim/plugin.py",
        "packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py",
        "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_factory.py",
        "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_2025_adapter.py",
        "examples/target_radar_simulation.py",
        "docs/plans/2025_python_rti_backend_audit.md",
        "docs/python_rti_backend.md",
    ]

    assert "python-2025-inprocess: in-process-backend-route" in markdown
    assert "python-2025-fedpro-grpc: hosted-transport-route" in markdown
    assert "main full Python 2025 RTI implementation now runs from hla-backend-python2025 while hla-backend-shim is retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in markdown
    assert "route-parity matrix now serves as the scenario-family ledger for federation, object, ownership, DDM, time, save/restore, MOM, and support-services evidence" in markdown
    assert "disciplined ownership across the extracted hla-backend-python2025 runtime/state/surface modules" in markdown
    assert "transport-seam evidence over hla-backend-python2025 rather than missing core runtime ownership" in markdown
    assert "binding/adaptation-seam proof over the main python2025 runtime" in markdown
    assert "Hosted runtime identity evidence:" in markdown
    assert "Hosted factory boundary evidence:" in markdown
    assert "Package-owned shared scenario evidence:" in markdown
    assert "Scenario package: hla-fom-target-radar" in markdown
    assert "Example entrypoint: python examples/target_radar_simulation.py --backend python2025 --steps 5" in markdown
    assert "Adapter class: hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter" in markdown
    assert "python2025: python/2025 / hla-backend-python2025 / counts_as_python_2025_rti=True / wrapper_only=False" in markdown
    assert "shim: shim/2025 / hla-backend-python2025 / counts_as_python_2025_rti=False / wrapper_only=True" in markdown
    assert "test_target_radar_example_supports_2025_backends" in markdown
    assert (
        "Unsupported factory surfaces: create_rti_ambassador(backend='shim', transport=...)"
        in markdown
    )
    assert "test_2025_version_local_factory_accepts_hosted_transport_creation_on_python2025_lane" in markdown
    assert "test_2025_version_local_factory_rejects_legacy_shim_provider_name" in markdown
    assert "Direct ambassador: python2025-rti / python/2025 / python2025 / hla-backend-python2025 / counts_as_python_2025_rti=True" in markdown
    assert "Hosted client: python2025 / hla-backend-python2025 / counts_as_python_2025_rti=True / wrapper_only=False / rti1516_2025 / grpc / fedpro" in markdown
    assert "test_2025_transport_server_reports_python2025_main_lane_identity" in markdown
    assert "::test_2025_shim_" not in json.dumps(payload, sort_keys=True)
    assert "test_2025_shim_" not in markdown
    assert "test_rti1516_2025_spec_and_shim.py" not in json.dumps(payload, sort_keys=True)
    assert "test_rti1516_2025_spec_and_shim.py" not in markdown
    assert legacy_markdown == markdown


def test_2025_backend_plugin_scan_detects_future_dedicated_python_2025_backend(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        '''"""Synthetic dedicated Python 2025 backend plugin for scanner regression tests."""
from hla.rti.plugin_api import RTIBackendPlugin


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python2025",
        aliases=("python-2025",),
        family="python-rti-2025",
        supports=("rti1516_2025",),
        description="Dedicated Python 2025 RTI backend.",
        create_backend=lambda request: request,
    )
''',
        encoding="utf-8",
    )
    shim_dir = tmp_path / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    shim_dir.mkdir(parents=True)
    (shim_dir / "plugin.py").write_text(
        '''"""Synthetic shim plugin that should not count as a dedicated backend."""
from hla.rti.plugin_api import RTIBackendPlugin


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="shim",
        aliases=(),
        family="compatibility-wrapper-2025",
        supports=("rti1516_2025",),
        description="Deprecated compatibility-wrapper alias over the live IEEE 1516.1-2025 Python RTI backend; slated for removal.",
        create_backend=lambda request: request,
    )
''',
        encoding="utf-8",
    )

    scan = _discover_backend_plugin_records(tmp_path)

    assert scan["backend_package_dirs"] == ["hla-backend-python2025", "hla-backend-shim"]
    assert scan["backend_package_count"] == 2
    assert {
        (record["package"], record["name"], record["family"])
        for record in scan["rti1516_2025_plugin_records"]
    } == {
        ("hla-backend-python2025", "python2025", "python-rti-2025"),
    }
    assert scan["dedicated_python_2025_backend_candidates"] == [
        {
            "package": "hla-backend-python2025",
            "plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "name": "python2025",
            "family": "python-rti-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert scan["dedicated_python_2025_legacy_package_delegation_violations"] == []
    assert scan["dedicated_python_2025_candidates_cleanly_separated"] is True


def test_2025_backend_plugin_scan_rejects_shim_delegating_python_2025_candidate(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        '''"""Synthetic invalid Python 2025 backend that delegates to the shim."""
from hla.backends.shim.backend import create_shim_backend
from hla.rti.plugin_api import RTIBackendPlugin


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python2025",
        aliases=("python-2025",),
        family="python-rti-2025",
        supports=("rti1516_2025",),
        description="Invalid shim-delegating Python 2025 RTI backend.",
        create_backend=create_shim_backend,
    )
''',
        encoding="utf-8",
    )

    scan = _discover_backend_plugin_records(tmp_path)

    assert scan["dedicated_python_2025_backend_candidates"] == [
        {
            "package": "hla-backend-python2025",
            "plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "name": "python2025",
            "family": "python-rti-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert scan["dedicated_python_2025_candidates_cleanly_separated"] is False
    assert scan["dedicated_python_2025_legacy_package_delegation_violations"] == [
        {
            "package": "hla-backend-python2025",
            "path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "kind": "forbidden-import",
            "target": "hla.backends.shim.backend.create_shim_backend",
        }
    ]


def test_2025_ddm_default_policy_requirement_family_audit_maps_all_rows() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    audit = snapshot["ddm_default_policy_requirement_family_audit"]

    assert audit["audit_status"] == "ddm-default-policy-requirement-family-map-captured"
    assert audit["slice_id"] == "2025-ddm-default-attribute-policy"
    assert audit["requirement_count"] == 23
    assert audit["family_count"] == 6
    assert audit["all_ddm_rows_family_mapped"] is True
    assert audit["unmapped_requirement_ids"] == []
    assert audit["unexpected_requirement_ids"] == []
    families = {family["family"]: family for family in audit["families"]}
    assert families["lookup-and-default-policy-control"]["requirement_ids"] == [
        "HLA2025-NEW-004",
        "HLA2025-FI-SVC-076",
        "HLA2025-FI-SVC-124",
        "HLA2025-FI-SVC-157",
        "HLA2025-FI-SVC-159",
        "HLA2025-FI-SVC-160",
        "HLA2025-FI-SVC-161",
        "HLA2025-FI-SVC-164",
    ]
    assert families["object-region-routing-and-scope-advisories"]["requirement_ids"] == [
        "HLA2025-FI-SVC-126",
        "HLA2025-FI-SVC-127",
        "HLA2025-FI-SVC-128",
        "HLA2025-FI-SVC-129",
        "HLA2025-FI-SVC-130",
        "HLA2025-FI-SVC-131",
        "HLA2025-FI-SVC-132",
        "HLA2025-FI-SVC-133",
        "HLA2025-FI-SVC-137",
    ]
    assert families["interaction-region-routing"]["requirement_ids"] == [
        "HLA2025-FI-SVC-134",
        "HLA2025-FI-SVC-135",
        "HLA2025-FI-SVC-136",
    ]
    assert families["directed-ddm-routing"]["requirement_ids"] == ["HLA2025-MOD-007"]
    assert families["passive-alias-and-compat-scenarios"]["requirement_ids"] == ["HLA2025-FI-005"]
    assert families["ddm-restore-and-disconnect-cleanup"]["requirement_ids"] == ["HLA2025-FI-001"]
    assert all(family["all_requirements_in_slice"] is True for family in audit["families"])
    assert "explicit requirement-family map" in audit["current_assessment"]
    assert "standalone implemented-evidence slice" in audit["residual_boundary"]


def test_2025_save_restore_requirement_family_audit_maps_all_rows() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    audit = snapshot["save_restore_requirement_family_audit"]

    assert audit["audit_status"] == "save-restore-requirement-family-map-captured"
    assert audit["slice_id"] == "2025-save-restore-lifecycle"
    assert audit["requirement_count"] == 20
    assert audit["family_count"] == 5
    assert audit["all_save_restore_rows_family_mapped"] is True
    assert audit["unmapped_requirement_ids"] == []
    assert audit["unexpected_requirement_ids"] == []
    families = {family["family"]: family for family in audit["families"]}
    assert families["lifecycle-control"]["requirement_ids"] == [
        "HLA2025-FI-SVC-018",
        "HLA2025-FI-SVC-019",
        "HLA2025-FI-SVC-020",
        "HLA2025-FI-SVC-021",
        "HLA2025-FI-SVC-022",
        "HLA2025-FI-SVC-023",
        "HLA2025-FI-SVC-026",
        "HLA2025-FI-SVC-027",
        "HLA2025-FI-SVC-028",
        "HLA2025-FI-SVC-029",
        "HLA2025-FI-SVC-030",
        "HLA2025-FI-SVC-031",
        "HLA2025-FI-SVC-032",
    ]
    assert families["shared-scenario-rollback"]["requirement_ids"] == ["HLA2025-REQ-002"]
    assert families["routing-policy-rollback"]["requirement_ids"] == [
        "HLA2025-FI-SVC-024",
        "HLA2025-FI-SVC-025",
        "HLA2025-FI-SVC-033",
        "HLA2025-FI-SVC-034",
    ]
    assert families["ownership-rollback"]["requirement_ids"] == ["HLA2025-FI-005"]
    assert families["time-window-and-time-state-rollback"]["requirement_ids"] == ["HLA2025-FI-001"]
    assert all(family["all_requirements_in_slice"] is True for family in audit["families"])
    assert "explicit requirement-family map" in audit["current_assessment"]
    assert "standalone implemented-evidence slice" in audit["residual_boundary"]
