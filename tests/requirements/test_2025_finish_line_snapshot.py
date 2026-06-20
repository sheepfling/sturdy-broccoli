from __future__ import annotations

import json
from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
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
    assert disposition["covered_row_count"] == 564
    assert disposition["by_disposition"] == {
        "duplicate/umbrella": 22,
        "covered": 564,
        "retired/legacy-only": 24,
        "unsupported-boundary": 81,
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
    assert pytest_anchor_audit["row_count"] == 711
    assert pytest_anchor_audit["anchored_requirement_count"] == 711
    assert "direct pytest-function anchors" in pytest_anchor_audit["current_assessment"]
    pytest_rows = {row["requirement_id"]: row for row in pytest_anchor_audit["rows"]}
    for prefix in ("HLA2025-FI-", "HLA2025-BND-", "HLA2025-MOD-", "HLA2025-NEW-", "HLA2025-FR-"):
        single_anchor_rows = [
            row["requirement_id"]
            for row in pytest_anchor_audit["rows"]
            if row["requirement_id"].startswith(prefix) and row["pytest_anchor_count"] == 1
        ]
        assert single_anchor_rows == []
    assert pytest_rows["HLA2025-FI-SVC-001"]["pytest_anchor_count"] == 2
    assert any("test_2025_shim_is_first_green_runtime_path" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchor_count"] == 8
    assert any("test_2025_shim_rejects_duplicate_federation_and_federate_names" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-005"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchor_count"] == 5
    assert any("test_2025_shim_routes_mom_synchronization_point_reports_through_interactions" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-013"]["pytest_anchors"])
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
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-035"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-035"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchor_count"] == 9
    assert any("test_2025_shim_implements_basic_ownership_divest_acquire_and_query_callbacks" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_transport_and_ownership_actions_to_observable_runtime_effects_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restores_cross_federate_attribute_owner_visibility"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-083"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_runs_smoke_fom_save_restore_ownership_gauntlet"
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
    assert any("test_2025_shim_applies_resign_time_ownership_policies" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-100"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchor_count"] == 7
    assert any("test_2025_shim_routes_mom_time_management_service_interactions" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"])
    assert any("test_2025_shim_uses_selected_logical_time_factory_for_queries_and_grants" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-101"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchor_count"] == 10
    assert any("test_2025_shim_queues_timestamped_messages_and_supports_retraction" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-121"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchor_count"] == 10
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_reports_lits_from_queued_tso_for_target_federate_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-123"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchor_count"] == 7
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"])
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
    assert any(
        "test_2025_transport_server_holds_tso_for_lagging_subscribers_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-057"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-058"]["pytest_anchor_count"] == 2
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-058"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-059"]["pytest_anchor_count"] == 2
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-059"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchor_count"] == 13
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-060"]["pytest_anchors"])
    assert any(
        "test_2025_shim_restore_recovers_plain_interaction_subscriber_routing"
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
    assert pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchor_count"] == 4
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-061"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchor_count"] == 4
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-062"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchor_count"] == 13
    assert any("test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"])
    assert any("test_2025_shim_filters_object_reflections_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-126"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-128"]["pytest_anchor_count"] == 4
    assert any("test_clause_9_services_are_observable_through_mom_service_invocation_reporting" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-128"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchor_count"] == 8
    assert any("test_2025_shim_filters_interactions_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"])
    assert any("test_2025_shim_filters_directed_interactions_by_ddm_region_overlap" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-134"]["pytest_anchors"])
    assert any(
        "test_2025_shim_restore_recovers_plain_interaction_subscriber_routing"
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
    assert pytest_rows["HLA2025-FI-SVC-137"]["pytest_anchor_count"] == 4
    assert any("test_clause_9_services_are_observable_through_mom_service_invocation_reporting" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-137"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchor_count"] == 5
    assert any("test_support_lookups_round_trip_class_handle_and_name" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-138"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchor_count"] == 4
    assert any("test_support_dimension_and_update_rate_helpers" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"])
    assert any(
        "test_2025_shim_accepts_support_lookup_aliases_and_rejects_invalid_values"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"]
    )
    assert any(
        "test_2025_transport_server_rejects_invalid_support_lookup_values_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-147"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-SVC-162"]["pytest_anchor_count"] == 2
    assert any("test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-162"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchor_count"] == 4
    assert any("test_2025_shim_normalizes_typed_handles_and_rejects_wrong_handle_family" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-165"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-OMT-COMP-001"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-223"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-223"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-011"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_intentionally_narrows_unmodeled_omt_fields" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-011"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-037"]["pytest_anchor_count"] == 1
    assert any("test_dimension_metadata_round_trip_is_still_intentionally_lossy" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-037"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchor_count"] == 2
    assert any("test_dimension_metadata_round_trip_is_still_intentionally_lossy" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchors"])
    assert any("test_2025_parser_intentionally_narrows_unmodeled_omt_fields" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-200"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_intentionally_narrows_unmodeled_omt_fields" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-200"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_rejects_foreign_namespace_extension_points" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-006"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-015"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_flattens_or_drops_unmodeled_structural_omt_fields" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-015"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-166"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_rejects_unknown_2025_switch_definitions" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-166"]["pytest_anchors"])
    assert pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchor_count"] == 1
    assert any("test_2025_parser_rejects_foreign_namespace_extension_points" in anchor for anchor in pytest_rows["HLA2025-OMT-COMP-224"]["pytest_anchors"])
    assert pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchor_count"] == 48
    assert any("test_2025_shim_runs_federation_save_restore_lifecycle" in anchor for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"])
    assert any(
        "test_2025_shim_runs_smoke_fom_save_restore_ownership_gauntlet"
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
        "test_2025_shim_restore_recovers_callback_delivery_policy"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restore_recovers_plain_object_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restore_recovers_plain_interaction_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restore_recovers_inflight_ownership_state"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restores_cross_federate_attribute_owner_visibility"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert any(
        "test_2025_shim_restore_recovers_directed_ddm_subscriber_routing"
        in anchor
        for anchor in pytest_rows["HLA2025-FI-SVC-018"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-FI-007"]["pytest_anchor_count"] == 2
    assert any("test_each_proto2025_2025_scenario_fom_set_merges_with_standard_mim" in anchor for anchor in pytest_rows["HLA2025-FI-007"]["pytest_anchors"])
    assert any("test_proto2025_2025_example_foms_drive_two_federate_exchange" in anchor for anchor in pytest_rows["HLA2025-FI-007"]["pytest_anchors"])
    assert pytest_rows["HLA2025-BND-001"]["pytest_anchor_count"] == 2
    assert any("test_standard_2025_routes_pass_runtime_capability_when_built" in anchor for anchor in pytest_rows["HLA2025-BND-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-BND-002"]["pytest_anchor_count"] == 2
    assert any("test_standard_2025_routes_pass_runtime_capability_when_built" in anchor for anchor in pytest_rows["HLA2025-BND-002"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-001"]["pytest_anchor_count"] == 2
    assert any("test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms" in anchor for anchor in pytest_rows["HLA2025-MOD-001"]["pytest_anchors"])
    assert any("test_2025_shim_validates_callback_model_and_credentials_at_connect" in anchor for anchor in pytest_rows["HLA2025-MOD-001"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-003"]["pytest_anchor_count"] == 4
    assert any("test_2025_shim_distinguishes_fom_mim_open_read_invalid_and_merge_errors" in anchor for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"])
    assert any("test_2025_shim_rejects_invalid_join_fom_modules_and_destroy_while_joined" in anchor for anchor in pytest_rows["HLA2025-MOD-003"]["pytest_anchors"])
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
    assert any("test_2025_shim_runs_two_federate_object_and_interaction_exchange" in anchor for anchor in pytest_rows["HLA2025-MOD-004"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-009"]["pytest_anchor_count"] == 2
    assert any("test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms" in anchor for anchor in pytest_rows["HLA2025-MOD-009"]["pytest_anchors"])
    assert any("test_2025_shim_validates_callback_model_and_credentials_at_connect" in anchor for anchor in pytest_rows["HLA2025-MOD-009"]["pytest_anchors"])
    assert pytest_rows["HLA2025-MOD-010"]["pytest_anchor_count"] == 3
    assert any("test_2025_parser_round_trips_logical_time_xml_names" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert any("test_2025_parser_round_trips_metadata_switches_transport_and_time_subset" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert any("test_2025_parser_round_trips_extended_omt_supported_subset" in anchor for anchor in pytest_rows["HLA2025-MOD-010"]["pytest_anchors"])
    assert pytest_rows["HLA2025-NEW-002"]["pytest_anchor_count"] == 4
    assert any("test_2025_shim_reports_federation_executions_and_members" in anchor for anchor in pytest_rows["HLA2025-NEW-002"]["pytest_anchors"])
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
    assert pytest_rows["HLA2025-NEW-003"]["pytest_anchor_count"] == 3
    assert any("test_2025_shim_reports_federate_resigned_callback_with_reason_context" in anchor for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"])
    assert any("test_2025_transport_server_decodes_extended_callback_routes_over_fedpro_schema" in anchor for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"])
    assert any(
        "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema"
        in anchor
        for anchor in pytest_rows["HLA2025-NEW-003"]["pytest_anchors"]
    )
    assert pytest_rows["HLA2025-NEW-005"]["pytest_anchor_count"] == 3
    assert any("test_2025_shim_normalizes_typed_handles_and_rejects_wrong_handle_family" in anchor for anchor in pytest_rows["HLA2025-NEW-005"]["pytest_anchors"])
    assert any("test_2025_transport_server_round_trips_support_services_over_fedpro_schema" in anchor for anchor in pytest_rows["HLA2025-NEW-005"]["pytest_anchors"])
    assert pytest_rows["HLA2025-NEW-007"]["pytest_anchor_count"] >= 10
    assert pytest_rows["HLA2025-BND-003"]["pytest_anchor_count"] == 146
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
    assert "lookahead query/modify" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "GALT/LITS/logical-time queries" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "time-window core, output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in route_rows[("time_management", "python-2025-inprocess")]["notes"]
    assert "bounded logical time/GALT/LITS/lookahead query evidence" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in route_rows[("time_management", "python-2025-fedpro-grpc")]["notes"]
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
    assert "tests/test_rti1516_2025_spec_and_shim.py" in fi_rows["HLA2025-FI-SVC-001"]["evidence_tests"]
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
        "supported-subset-traceable": 373,
        "unsupported-boundary-traceable": 81,
    }
    assert "supported-subset proof separated from unsupported-boundary proof" in omt_audit["current_assessment"]
    omt_pytest_rows = [
        row
        for row in pytest_anchor_audit["rows"]
        if row["requirement_id"].startswith(("HLA2025-OMT-", "HLA2025-OMT-COMP-", "HLA2025-OMT-CV-", "HLA2025-OMT-SU-"))
    ]
    assert len(omt_pytest_rows) == omt_audit["row_count"]
    omt_single_anchor_rows = [row["requirement_id"] for row in omt_pytest_rows if row["pytest_anchor_count"] == 1]
    omt_multi_anchor_rows = [row["requirement_id"] for row in omt_pytest_rows if row["pytest_anchor_count"] > 1]
    assert len(omt_single_anchor_rows) == 448
    assert sorted(omt_multi_anchor_rows) == [
        "HLA2025-OMT-001",
        "HLA2025-OMT-002",
        "HLA2025-OMT-005",
        "HLA2025-OMT-006",
        "HLA2025-OMT-007",
        "HLA2025-OMT-COMP-041",
    ]
    omt_rows = {row["requirement_id"]: row for row in omt_audit["rows"]}
    assert omt_rows["HLA2025-OMT-001"]["proof_status"] == "supported-subset-traceable"
    assert "2025-fom-validation" in omt_rows["HLA2025-OMT-001"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-002"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-reference-value-required" in omt_rows["HLA2025-OMT-002"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-004"]["proof_status"] == "supported-subset-traceable"
    assert "2025-omt-component-metadata-roundtrip" in omt_rows["HLA2025-OMT-COMP-004"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-037"]["proof_status"] == "unsupported-boundary-traceable"
    assert "2025-omt-unsupported-component-boundaries" in omt_rows["HLA2025-OMT-COMP-037"]["supporting_slice_ids"]
    assert omt_rows["HLA2025-OMT-COMP-006"]["proof_status"] == "unsupported-boundary-traceable"
    assert "2025-omt-unmodeled-component-boundaries-expanded" in omt_rows["HLA2025-OMT-COMP-006"]["supporting_slice_ids"]
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
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["status"] == "bounded-working-slice"
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["scenario_count"] == 8
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["route_parity_statuses"] == {"parity-covered": 8}
    assert "best-attempt bounded working surface" in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["summary"]
    assert "full-fledged RTI" in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["boundary"]
    assert milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["status"] == "covered-scenario-slice"
    assert "tracked FOM-backed runtime scenarios" in milestone_rows[("python-2025-fedpro-grpc", "example_fom_scenarios")]["summary"]
    assert milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["status"] == "covered-routing-slice"
    assert "typed transport surface" in milestone_rows[("python-2025-fedpro-grpc", "messaging_and_routing")]["summary"]
    assert milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["status"] == "covered-time-advance-slice"
    assert "restore rollback of logical time" in milestone_rows[("python-2025-inprocess", "time_sync_and_advances")]["summary"]
    assert milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["status"] == "bounded-query-evidence"
    assert "not strong enough to claim a fully proven or universally correct GALT/LITS algorithm" in milestone_rows[("python-2025-inprocess", "galt_lits_queries")]["boundary"]
    assert "future-exclusion proof" in milestone_rows[("python-2025-fedpro-grpc", "galt_lits_queries")]["summary"]
    assert milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["status"] == "bounded-lookahead-evidence"
    assert "future-message exclusion" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["boundary"]
    assert "output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["summary"]
    assert "save-restore lookahead rollback with queued-TSO redelivery" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["summary"]
    assert "tests/test_rti1516_2025_spec_and_shim.py" in milestone_rows[("python-2025-inprocess", "lookahead_windows")]["evidence_tests"]
    assert "tests/scenarios/test_python_route_parity.py" in milestone_rows[("python-2025-inprocess", "lookahead_windows")]["evidence_tests"]
    assert "tests/transport/test_grpc_transport_2025.py" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["evidence_tests"]
    assert "tests/scenarios/test_python_route_parity.py" in milestone_rows[("python-2025-fedpro-grpc", "lookahead_windows")]["evidence_tests"]
    assert pytest_rows["HLA2025-OMT-001"]["pytest_anchor_count"] == 4
    assert pytest_rows["HLA2025-OMT-002"]["pytest_anchor_count"] >= 6
    assert pytest_rows["HLA2025-OMT-005"]["pytest_anchor_count"] == 4
    assert pytest_rows["HLA2025-OMT-006"]["pytest_anchor_count"] == 10
    assert pytest_rows["HLA2025-OMT-007"]["pytest_anchor_count"] == 8
    assert pytest_rows["HLA2025-OMT-COMP-041"]["pytest_anchor_count"] == 2
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
        "covered_rows": 564,
        "unsupported_boundary_rows": 81,
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
        "covered": 564,
        "duplicate/umbrella": 22,
        "retired/legacy-only": 24,
        "unsupported-boundary": 81,
    }
    assert requirement_audit["rows_with_complete_review_metadata"] == 691
    assert requirement_audit["covered_rows_with_evidence_paths"] == 564
    assert requirement_audit["unsupported_rows_with_explicit_boundary_flag"] == 81
    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in requirement_audit["current_assessment"]
    assert any("unsupported-boundary decisions" in blocker for blocker in requirement_audit["full_claim_blockers"])
    boundary_statement = snapshot["supported_boundary_statement"]
    assert boundary_statement["statement_status"] == "supported-boundary-statement"
    assert boundary_statement["ready"] is True
    assert "bounded working surface" in boundary_statement["statement"]
    assert "explicit unsupported, legacy-only, and artifact-gated boundaries" in boundary_statement["statement"]
    assert len(boundary_statement["supported_scope"]) == 4
    assert any("196 catalog rows" in item for item in boundary_statement["supported_scope"])
    assert any("FedPro 2025 transport behavior is executable as a bounded runtime slice" in item for item in boundary_statement["supported_scope"])
    assert len(boundary_statement["explicit_boundaries"]) == 4
    assert any("Unsupported OMT component rows remain unsupported-boundary entries" in item for item in boundary_statement["explicit_boundaries"])
    assert any("Java and C++ bindings remain artifact/runtime-capability bounded" in item for item in boundary_statement["explicit_boundaries"])
    assert boundary_statement["evidence_summary"] == {
        "bounded_ready_dimensions": 8,
        "dimension_count": 8,
        "route_parity_missing_count": 0,
        "route_parity_partial_count": 0,
        "covered_rows": 564,
        "unsupported_boundary_rows": 81,
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
    support_service_audit = snapshot["support_service_proof_audit"]
    assert support_service_audit["row_count"] == 62
    assert support_service_audit["focused_executable_row_count"] == 62
    assert support_service_audit["rows_with_known_gaps"] == 61
    assert support_service_audit["complete_negative_path_row_count"] == 61
    assert support_service_audit["partial_negative_path_row_count"] == 0
    assert support_service_audit["mapped_not_exhaustive_negative_path_row_count"] == 0
    assert support_service_audit["ready_for_support_service_traceability_claim"] is True
    assert support_service_audit["ready_for_support_service_full_conformance_claim"] is False
    assert support_service_audit["by_verification_status"] == {"focused-executable-tests": 62}
    assert support_service_audit["by_negative_path_status"] == {
        "complete": 61,
        "not-applicable": 1,
    }
    assert "explicit support-service ledger" in support_service_audit["current_assessment"]
    assert "Negative-path coverage is now complete for all 61 actionable support-service rows" in support_service_audit["current_assessment"]
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
    assert "Declared exception matrix is identified from source metadata; exhaustive negative execution remains incomplete." in support_rows["getObjectInstanceName"]["known_gaps"]
    promotion_split_audit = snapshot["promotion_split_audit"]
    assert snapshot["promotion_vs_split_audit"] == promotion_split_audit
    assert snapshot["route_parity_audit"] == snapshot["route_parity_matrix"]
    assert promotion_split_audit["decision_shape"] == "promote-current-lane-or-split-later-based-on-evidence"
    assert promotion_split_audit["current_lane"] == {
        "package": "hla-backend-shim",
        "role": "current executable Python 2025 RTI lane",
        "spec_package": "hla-rti1516-2025",
    }
    assert promotion_split_audit["current_recommendation"] == "promote-current-lane-as-working-surface-and-keep-split-optional"
    assert promotion_split_audit["ready_for_current_lane_promotion_as_working_surface"] is True
    assert promotion_split_audit["ready_for_permanent_no-split_decision"] is False
    assert len(promotion_split_audit["promotion_basis"]) == 6
    assert any("main in-process suite" in item for item in promotion_split_audit["promotion_basis"])
    assert any("bounded working-surface milestones" in item for item in promotion_split_audit["promotion_basis"])
    assert any("fully route-backed across the current Python 2025 lanes" in item for item in promotion_split_audit["promotion_basis"])
    assert any("main shim-backed pressure families" in item for item in promotion_split_audit["promotion_basis"])
    assert len(promotion_split_audit["split_triggers"]) == 4
    assert any("obscure or distort core RTI semantics" in item for item in promotion_split_audit["split_triggers"])
    assert any("route normalization grows more complex" in item for item in promotion_split_audit["split_triggers"])
    assert len(promotion_split_audit["permanent_decision_blockers"]) == 4
    assert any("row-level requirement-by-requirement audit" in item for item in promotion_split_audit["permanent_decision_blockers"])
    assert any("Hosted FedPro remains a bounded runtime slice" in item for item in promotion_split_audit["permanent_decision_blockers"])
    assert "live Python 2025 RTI lane" in promotion_split_audit["current_assessment"]
    assert "including across the main shim-backed pressure families" in promotion_split_audit["current_assessment"]
    concentration_audit = snapshot["implementation_concentration_audit"]
    assert concentration_audit["audit_status"] == "implementation-concentration-captured"
    assert concentration_audit["implemented_slice_count"] == 73
    assert concentration_audit["shim_backend_path"] == "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    assert concentration_audit["shim_backend_slice_count"] == 42
    assert concentration_audit["shim_backend_slice_share"] == 0.575
    assert concentration_audit["spec_package_slice_count"] == 12
    assert concentration_audit["transport_slice_count"] == 11
    assert concentration_audit["semantic_concentration_is_material"] is True
    assert "materially concentrated in hla-backend-shim/backend.py" in concentration_audit["current_assessment"]
    assert "keep accumulating primarily in the shim backend implementation" in concentration_audit["extraction_pressure_boundary"]
    assert concentration_audit["top_evidence_anchors"][:5] == [
        {"path": "tests/transport/test_grpc_transport_2025.py", "slice_count": 52},
        {"path": "tests/test_rti1516_2025_spec_and_shim.py", "slice_count": 49},
        {"path": "packages/hla-backend-shim/src/hla/backends/shim/backend.py", "slice_count": 42},
        {"path": "tests/test_rti1516_2025_validation.py", "slice_count": 9},
        {"path": "tests/requirements/test_2025_tail_backlog_evidence.py", "slice_count": 9},
    ]
    aggregation_audit = snapshot["slice_aggregation_pressure_audit"]
    assert aggregation_audit["audit_status"] == "slice-aggregation-pressure-captured"
    assert aggregation_audit["implemented_slice_count"] == 69
    assert aggregation_audit["aggregated_slice_count_ge_10_requirements"] == 9
    assert aggregation_audit["aggregated_slice_count_ge_10_requirements_shim_backed"] == 3
    assert aggregation_audit["aggregated_slice_count_ge_20_requirements"] == 6
    assert aggregation_audit["aggregated_slice_count_ge_20_requirements_shim_backed"] == 2
    assert aggregation_audit["largest_implemented_slices"][:5] == [
        {"slice_id": "2025-service-utilization-crosscheck", "requirement_count": 196, "shim_backend_backed": False},
        {"slice_id": "2025-omt-extended-supported-subset", "requirement_count": 109, "shim_backend_backed": False},
        {"slice_id": "2025-omt-schema-constraint-validation", "requirement_count": 29, "shim_backend_backed": False},
        {"slice_id": "2025-ddm-default-attribute-policy", "requirement_count": 23, "shim_backend_backed": True},
        {"slice_id": "2025-omt-component-metadata-roundtrip", "requirement_count": 22, "shim_backend_backed": False},
    ]
    assert aggregation_audit["largest_shim_backed_aggregated_slices"] == [
        {"slice_id": "2025-ddm-default-attribute-policy", "requirement_count": 23, "shim_backend_backed": True},
        {"slice_id": "2025-save-restore-lifecycle", "requirement_count": 20, "shim_backend_backed": True},
        {"slice_id": "2025-directed-interaction-boundary", "requirement_count": 11, "shim_backend_backed": True},
    ]
    assert "ddm-default-attribute-policy, save-restore-lifecycle, and directed-interaction-boundary" in aggregation_audit["current_assessment"]
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
        "test_2025_shim_runs_federation_save_restore_lifecycle"
    )
    assert save_restore_audit["proof_families"][1]["hosted_tests"][0].endswith(
        "test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route"
    )
    assert "lifecycle control, shared rollback scenarios, routing/policy rollback, ownership rollback" in save_restore_audit["current_assessment"]
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
        "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_interactions_to_object_class_subscribers",
        "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_interactions_only_to_subscribers",
    ]
    assert directed_audit["proof_families"][4]["hosted_tests"][1].endswith(
        "test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema"
    )
    assert "base routing/callback delivery, timestamped delivery and retraction, DDM overlap filtering" in directed_audit["current_assessment"]
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
        "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy",
    ]
    assert ddm_audit["proof_families"][5]["hosted_tests"][1].endswith(
        "test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema"
    )
    assert "lookup/default-policy control, object-region routing and scope advisories" in ddm_audit["current_assessment"]
    route_backing_audit = snapshot["shim_pressure_family_route_backing_audit"]
    assert route_backing_audit["audit_status"] == "shim-pressure-family-route-backing-captured"
    assert route_backing_audit["family_count"] == 16
    assert route_backing_audit["fully_route_backed_family_count"] == 16
    assert route_backing_audit["all_families_route_backed_across_current_python_lanes"] is True
    assert route_backing_audit["families"][:4] == [
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "lifecycle-control",
            "direct_test_count": 4,
            "hosted_test_count": 4,
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
            "direct_test_count": 6,
            "hosted_test_count": 6,
            "route_backed_across_current_python_lanes": True,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "ownership-rollback",
            "direct_test_count": 3,
            "hosted_test_count": 3,
            "route_backed_across_current_python_lanes": True,
        },
    ]
    assert "Every currently named family across save/restore, directed interaction, and DDM/default-policy has both direct shim proof and hosted FedPro proof" in route_backing_audit["current_assessment"]
    asymmetry_audit = snapshot["shim_pressure_family_asymmetry_audit"]
    assert asymmetry_audit["audit_status"] == "shim-pressure-family-asymmetry-captured"
    assert asymmetry_audit["family_count"] == 16
    assert asymmetry_audit["by_balance"] == {
        "balanced": 16,
    }
    assert asymmetry_audit["families"][:5] == [
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "lifecycle-control",
            "direct_test_count": 4,
            "hosted_test_count": 4,
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
            "direct_test_count": 6,
            "hosted_test_count": 6,
            "route_backed_across_current_python_lanes": True,
            "balance": "balanced",
            "count_delta": 0,
        },
        {
            "slice_id": "2025-save-restore-lifecycle",
            "family": "ownership-rollback",
            "direct_test_count": 3,
            "hosted_test_count": 3,
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
    assert "symmetric at the named proof-family level" in asymmetry_audit["current_assessment"]
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
    assert coherence_audit["shim_backend_concentration_is_material"] is True
    assert coherence_audit["all_pressure_families_route_backed_across_current_python_lanes"] is True
    assert "defensible coherence story" in coherence_audit["current_assessment"]
    assert any("Implementation concentration in hla-backend-shim/backend.py remains material" in item for item in coherence_audit["residual_blockers"])
    current_lane_statement = snapshot["current_lane_working_surface_statement"]
    assert current_lane_statement["statement_status"] == "current-lane-working-surface-statement"
    assert current_lane_statement["ready"] is True
    assert "coherent bounded working Python RTI surface" in current_lane_statement["statement"]
    assert "hla-backend-shim is the live Python 2025 RTI lane" in current_lane_statement["statement"]
    assert "promote it as the bounded working Python 2025 RTI surface" in current_lane_statement["current_assessment"]
    assert len(current_lane_statement["non_claims"]) == 4
    assert any("full requirement-by-requirement IEEE 1516.1-2025 conformance claim" in item for item in current_lane_statement["non_claims"])
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    assert implementation_lane_audit["audit_status"] == "current-lane-architecture-captured"
    assert implementation_lane_audit["current_2025_lane"] == {
        "backend_package": "hla-backend-shim",
        "plugin_family": "shim",
        "supports": ["rti1516_2025"],
        "role": "current executable Python 2025 RTI lane",
        "spec_package": "hla-rti1516-2025",
    }
    assert implementation_lane_audit["reference_2010_lane"] == {
        "backend_package": "hla-backend-inmemory",
        "plugin_family": "inmemory",
        "supports": ["rti1516e"],
        "role": "2010 pure Python RTI backend",
    }
    assert implementation_lane_audit["dedicated_2025_backend_package_present"] is False
    assert implementation_lane_audit["ready_for_current_lane_promotion_as_working_surface"] is True
    assert implementation_lane_audit["ready_for_permanent_no-split_decision"] is False
    assert implementation_lane_audit["clean_extraction_still_optional"] is True
    assert "hosted FedPro route is a route variant" in implementation_lane_audit["current_assessment"]
    assert "extracting a dedicated 2025 backend" in implementation_lane_audit["extraction_boundary"]
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
    assert objective_audit["surface_claim"] == "bounded-working-surface"
    assert objective_audit["ready_for_bounded_working_surface_claim"] is True
    assert objective_audit["ready_for_full_2025_completion_claim"] is False
    assert objective_audit["dimension_count"] == 8
    assert objective_audit["bounded_ready_dimension_count"] == 8
    dimensions = {row["id"]: row for row in objective_audit["dimensions"]}
    assert dimensions["federation_management"]["evidence_level"] == "strong-slice"
    assert dimensions["federation_management"]["bounded_working_surface_ready"] is True
    assert "2025-connect-and-federation-catalog-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert "2025-federate-membership-and-resign-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert "2025-synchronization-point-services" in dimensions["federation_management"]["implemented_slice_ids"]
    assert tuple(dimensions["federation_management"]["route_scenarios"]) == ("federation_lifecycle", "save_restore")
    assert dimensions["federation_management"]["route_summary"]["by_status"]["parity-covered"] == 12
    assert "tests/transport/test_grpc_transport_2025.py" in dimensions["federation_management"]["route_artifacts"]
    assert dimensions["object_management"]["route_summary"]["by_status"]["parity-covered"] == 18
    assert dimensions["object_management"]["route_summary"]["scenario_count"] == 3
    assert "2025-declaration-publication-services" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-declaration-subscription-services" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-declaration-relevance-advisory-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-delete-remove-flows" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-attribute-update-request-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-attribute-transport-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert "2025-object-interaction-transport-callbacks" in dimensions["object_management"]["implemented_slice_ids"]
    assert dimensions["ownership_management"]["evidence_level"] == "strong-slice"
    assert "2025-ownership-divestiture-confirmation-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-release-and-if-wanted-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-acquisition-assumption-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-acquisition-availability-cancellation-flows" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert "2025-ownership-query-and-resign-policies" in dimensions["ownership_management"]["implemented_slice_ids"]
    assert tuple(dimensions["ownership_management"]["route_scenarios"]) == ("ownership", "save_restore")
    assert dimensions["time_management"]["route_summary"]["by_status"]["parity-covered"] == 12
    assert "tests/test_rti1516_2025_spec_and_shim.py" in dimensions["time_management"]["evidence_tests"]
    assert "2025-time-mode-enable-disable" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-advance-request-modes" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-grant-and-async-delivery" in dimensions["time_management"]["implemented_slice_ids"]
    assert "2025-time-query-and-lookahead-control" in dimensions["time_management"]["implemented_slice_ids"]
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
    assert "negative-path complete inside the Python routes" in dimensions["support_services"]["residual_blockers"][0]
    assert dimensions["callbacks"]["evidence_level"] == "strong-slice"
    assert dimensions["callbacks"]["route_summary"]["by_status"]["parity-covered"] == 42
    assert "fully route-backed across the current Python 2025 lanes" in dimensions["callbacks"]["current_assessment"]
    assert dimensions["omt_handling"]["route_summary"]["row_count"] == 0
    assert dimensions["omt_handling"]["bounded_working_surface_ready"] is True
    assert "unsupported boundaries" in dimensions["omt_handling"]["current_assessment"]
    assert dimensions["omt_handling"]["evidence_level"] == "bounded-slice"
    assert dimensions["binding_routes"]["route_summary"]["by_status"]["parity-covered"] == 48
    assert dimensions["binding_routes"]["evidence_level"] == "bounded-slice"
    assert any("artifact/runtime-capability" in blocker or "artifact/runtime" in blocker for blocker in dimensions["binding_routes"]["residual_blockers"])
    closeout = snapshot["closeout_readiness"]
    assert closeout["implemented_slice_count"] >= 20
    assert closeout["high_priority_open_count"] == 0
    assert closeout["route_parity_partial_count"] == 0
    assert closeout["route_parity_missing_count"] == 0
    assert closeout["ready_for_slice_closeout"] is True
    assert closeout["ready_for_full_completion_claim"] is False
    assert "FI per-service runtime traceability" in closeout["current_assessment"]
    assert len(closeout["conformance_blockers"]) >= 4
    assert any("row-level requirement-by-requirement disposition audit across all 2025 rows" in blocker for blocker in closeout["conformance_blockers"])
    assert any("Java and C++ standard-route evidence" in blocker for blocker in closeout["conformance_blockers"])
    assert any("hosted FedPro route is verified as a runtime slice" in blocker for blocker in closeout["conformance_blockers"])


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}

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
    assert "Cross-binding parity" in slices["2025-lookahead-window-proofs"]["supported_scope"]
    assert slices["2025-save-restore-lifecycle"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-018" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "HLA2025-FI-SVC-034" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "federation save/restore lifecycle callbacks" in slices["2025-save-restore-lifecycle"]["supported_scope"]
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
    assert "Python 2025 shim plus the hosted FedPro route support" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert "Java/C++ parity remains later behavior work" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert slices["2025-omt-reference-value-required"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-006" in slices["2025-omt-reference-value-required"]["requirements"]
    assert slices["2025-omt-component-metadata-roundtrip"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-004" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "HLA2025-OMT-COMP-215" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "array encodings" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert "logicalTime/logicalTimeInterval names and dataType bindings" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-switch-and-transport-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-078" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-167" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "conveyProducingFederate default" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert slices["2025-omt-extended-supported-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-001" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-223" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "supported model-identification scalar and reference/POC metadata subset" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert "supported basic/simple/enumerated/array/fixed-record/variant-record datatype tables" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert slices["2025-omt-unsupported-component-boundaries"]["status"] == "unsupported-boundary"
    assert "HLA2025-OMT-COMP-037" in slices["2025-omt-unsupported-component-boundaries"]["requirements"]
    assert "HLA2025-OMT-COMP-197" in slices["2025-omt-unsupported-component-boundaries"]["requirements"]
    assert "not modeled in the shared parser/serializer surface" in slices["2025-omt-unsupported-component-boundaries"]["supported_scope"]
    assert slices["2025-omt-unmodeled-component-boundaries-expanded"]["status"] == "unsupported-boundary"
    assert "HLA2025-OMT-COMP-006" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["requirements"]
    assert "HLA2025-OMT-COMP-224" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["requirements"]
    assert "keyword taxonomy attributes" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["supported_scope"]
    assert "transportation reliable/semantics detail rows" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["supported_scope"]
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
    assert "Java runtime evidence runs when the Java 2025 shim jar is built" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
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
    assert "Full MOM action/request routing" in slices["2025-fedpro-hosted-runtime-extended-state"]["supported_scope"]
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
    assert "region-scoped requestAttributeValueUpdate callbacks" in slices["2025-object-attribute-update-request-callbacks"]["supported_scope"]

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

    markdown = "\n".join(build_spec2025_finish_line_markdown(ROOT))
    assert "HLA conformance" in markdown
    assert "Closeout Readiness" in markdown
    assert "Promotion Vs Split Audit" in markdown
    assert "Pytest Anchor Audit" in markdown
    assert "Anchored requirements: 711" in markdown
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
    assert "GALT and LITS behavior: bounded-query-evidence" in markdown
    assert "Lookahead handling and windows: bounded-lookahead-evidence" in markdown
    assert "future-exclusion, output-delivery, consumer-order, pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline resume, and time-window proof" in markdown
    assert "Requirement-By-Requirement Audit" in markdown
    assert "Audit status: row-level-requirement-disposition-audit-captured" in markdown
    assert "Ready for row-level audit claim: True" in markdown
    assert "Requirement-by-requirement area closure:" in markdown
    assert "Completion Claim Audit" in markdown
    assert "Ready for supported-boundary statement: True" in markdown
    assert "Ready for full 2025 conformance claim: False" in markdown
    assert "Covered rows: 564" in markdown
    assert "Supported Boundary Statement" in markdown
    assert "Status: supported-boundary-statement" in markdown
    assert "Ready: True" in markdown
    assert "Implementation Concentration Audit" in markdown
    assert "Shim backend-backed slices: 42" in markdown
    assert "Shim backend slice share: 0.575" in markdown
    assert "Semantic concentration is material: True" in markdown
    assert "Slice Aggregation Pressure Audit" in markdown
    assert "Aggregated slices >=10 requirements: 9" in markdown
    assert "Aggregated slices >=20 requirements and shim-backed: 2" in markdown
    assert "2025-ddm-default-attribute-policy: 23 requirements" in markdown
    assert "Save/Restore Decomposition Audit" in markdown
    assert "Slice id: 2025-save-restore-lifecycle" in markdown
    assert "Proof families: 5" in markdown
    assert "save-restore/time-window-and-time-state-rollback" in markdown
    assert "Directed Interaction Decomposition Audit" in markdown
    assert "Slice id: 2025-directed-interaction-boundary" in markdown
    assert "directed-interaction/ddm-overlap-filtering" in markdown
    assert "DDM Default-Policy Decomposition Audit" in markdown
    assert "Slice id: 2025-ddm-default-attribute-policy" in markdown
    assert "ddm-default-policy/object-region-routing-and-scope-advisories" in markdown
    assert "Shim Pressure Family Route-Backing Audit" in markdown
    assert "Family count: 16" in markdown
    assert "All families route-backed across current Python lanes: True" in markdown
    assert "Shim Pressure Family Asymmetry Audit" in markdown
    assert "Balanced families: 16" in markdown
    assert "Direct-heavier families: 0" in markdown
    assert "Hosted-heavier families: 0" in markdown
    assert "Current Lane Coherence Audit" in markdown
    assert "Ready for current-lane coherent working-surface claim: True" in markdown
    assert "Major pressure slice count: 3" in markdown
    assert "Current Lane Working-Surface Statement" in markdown
    assert "Status: current-lane-working-surface-statement" in markdown
    assert "Ready: True" in markdown
    assert "Implementation Lane Audit" in markdown
    assert "Current 2025 backend package: hla-backend-shim" in markdown
    assert "Reference 2010 backend package: hla-backend-inmemory" in markdown
    assert "Dedicated 2025 backend package present: False" in markdown
    assert "python-2025-fedpro-grpc: hosted-transport-route" in markdown
    assert "Objective Audit" in markdown
    assert "Surface claim: bounded-working-surface" in markdown
    assert "Bounded-ready dimensions: 8 / 8" in markdown
    assert "Federation Management" in markdown
    assert "OMT Handling" in markdown
    assert "negative-path complete inside the Python routes" in markdown
    assert "Ready for slice closeout: True" in markdown
    assert "Ready for full completion claim: False" in markdown
    assert "Conformance blockers:" in markdown
    assert "Highest-Priority Open Work" in markdown
    assert "2025-wsdl-legacy-only" in markdown
    assert "Do not promote `partial` rows" in markdown


@pytest.mark.requirements("HLA2025-TRACE-001")
def test_2025_finish_line_writer_emits_reviewable_json_and_markdown(tmp_path: Path) -> None:
    paths = write_spec2025_finish_line(tmp_path, ROOT)

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["executable_test_backlog"]["row_count"] == 1117
    assert payload["requirement_depth_expansion"]["row_count"] == 691
    assert payload["requirement_coverage_disposition"]["covered_row_count"] == 564
    assert payload["verification_matrix"]["high_priority_missing_anchor_count"] == 0
    assert payload["requirement_pytest_anchor_audit"]["row_count"] == 711
    assert payload["unanchored_requirement_audit"]["row_count"] == 0
    assert payload["route_parity_matrix"]["by_status"]["missing"] == 0
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
    assert payload["implementation_lane_audit"]["current_2025_lane"]["backend_package"] == "hla-backend-shim"
    assert payload["implementation_lane_audit"]["reference_2010_lane"]["backend_package"] == "hla-backend-inmemory"
    assert payload["implementation_lane_audit"]["dedicated_2025_backend_package_present"] is False
    assert payload["implementation_lane_audit"]["python_2025_routes"][1]["route"] == "python-2025-fedpro-grpc"
    assert payload["supported_boundary_statement"]["statement_status"] == "supported-boundary-statement"
    assert payload["promotion_split_audit"]["ready_for_current_lane_promotion_as_working_surface"] is True
    assert payload["promotion_split_audit"]["ready_for_permanent_no-split_decision"] is False
    assert payload["objective_dimension_audit"]["ready_for_bounded_working_surface_claim"] is True
    assert payload["objective_dimension_audit"]["ready_for_full_2025_completion_claim"] is False
    assert payload["closeout_readiness"]["ready_for_slice_closeout"] is True
    assert payload["closeout_readiness"]["ready_for_full_completion_claim"] is False

    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert "Imported requirement-depth rows: 691" in markdown
    assert "Imported provisional disposition rows: 691" in markdown
    assert "Closeout Readiness" in markdown
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
    assert "Objective Audit" in markdown
    assert "Implemented Evidence Slices" in markdown
    matrix = paths["verification_matrix"].read_text(encoding="utf-8")
    assert "HLA2025-VER-001" in matrix
    assert "2025-verification-anchor-matrix" in matrix
    assert "HLA2025-MIL-001" in matrix
    assert "2025-python-rti-milestone-ledger" in matrix
    route_matrix = paths["route_parity_matrix"].read_text(encoding="utf-8")
    assert "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,cpp-standard-2025-grpc,parity-covered,scenario-parity" in route_matrix
