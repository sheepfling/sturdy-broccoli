"""Repo-internal curated direct requirement evidence overrides.
"""
from __future__ import annotations

from typing import Any


_CURATED_REQUIREMENT_DIRECT_REFS: dict[str, dict[str, tuple[str, ...]]] = {
    "HLA1516.1-FM-4.15-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/federation_sync.py",),
        "positive_test_refs": (
            "tests/scenarios/test_startup_sync_fom_java_translation_v09.py::test_whole_federation_synchronization_announces_late_joiner_before_completion",
            "tests/verification/test_compliance_slice_v011.py::test_core_time_and_sync_compliance_smoke_covers_late_join_sync_and_time_controls",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.15-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/federation_sync.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/verification/test_compliance_slice_v011.py::test_core_time_and_sync_compliance_smoke_covers_late_join_sync_and_time_controls",
        ),
    },
    "HLA1516.1-FM-4.17-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (
            "tests/verification/test_compliance_slice_v011.py::test_scheduled_save_waits_for_time_and_restore_reinstates_time_state",
        ),
    },
    "HLA1516.1-FM-4.20-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_save_reports_aborted_and_clears_status",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.23-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_save_reports_aborted_and_clears_status",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.25-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.26-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.27-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.29-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_mom_federate_objects_persist_across_restore_cycles",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-MOM-11.1-005": {
        "implementation_refs": (
            "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_catalog.py",
            "src/hla2010/mom.py",
        ),
        "positive_test_refs": (
            "tests/factories/test_fom_omt_parsing.py::test_merge_with_standard_mim_preserves_standard_mom_definitions_and_catalog_metadata",
            "tests/factories/test_fom_omt_parsing.py::test_merge_with_standard_mim_preserves_mom_table_definitions_without_alteration",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.31-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_query_federation_restore_status_rejects_not_connected_and_not_joined",
        ),
    },
    "HLA1516.1-SUP-10.18-001": {
        "implementation_refs": (
            "packages/hla-backend-inmemory/src/hla.backends.inmemory/support_control.py",
            "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom.py",
        ),
        "positive_test_refs": (
            "tests/backends/test_python_backend_support_services.py::test_support_advisory_switches_toggle_and_reject_duplicates",
            "tests/backends/test_python_backend_object_ownership_extended.py::test_clause_10_services_are_observable_through_mom_service_invocation_reporting",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.32-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-MOM-11.3-003": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_reporting.py",),
        "positive_test_refs": (
            "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_mim_request_report_exchange",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
        ),
    },
    "HLA1516.1-MOM-11.3-004": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_reporting.py",),
        "positive_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_mom_report_payload_uses_exact_mim_catalog_parameters",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
        ),
    },
    "HLA1516.1-MOM-11.3-006": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_actions.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_reporting.py"),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
            "tests/mom/test_mom_catalog_validation_v012.py::test_strict_mom_rejects_federate_sent_report_interaction",
        ),
    },
    "HLA1516.1-MOM-11.5-001": {
        "implementation_refs": ("hla2010/service_reporting.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_reporting.py"),
        "positive_test_refs": (
            "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_service_invocation_reporting",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
        ),
    },
    "HLA1516.1-MOM-11.5-003": {
        "implementation_refs": ("hla2010/service_reporting.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_actions.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/mom_reporting.py"),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
        ),
    },
    "HLA1516.1-OWN-7.7-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/ownership.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_python_rti_release_denied_preserves_owner_and_no_acquisition_grant",
        ),
    },
    "HLA1516.1-OWN-7.9-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/ownership.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_python_rti_acquisition_if_available_reports_unavailable_without_transfer",
        ),
    },
    "HLA1516.1-TM-8.2-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_enable_time_regulation_rejects_not_connected_not_joined_invalid_lookahead_duplicate_save_restore_and_time_advancing",
        ),
    },
    "HLA1516.1-TM-8.2-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.2-003": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_time_enable_callbacks_are_not_emitted_on_failed_requests",
        ),
    },
    "HLA1516.1-TM-8.5-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths",
        ),
    },
    "HLA1516.1-TM-8.5-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.5-003": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_time_enable_callbacks_are_not_emitted_on_failed_requests",
        ),
    },
    "HLA1516.1-TM-8.8-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.8-002": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.8-003": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_time_advance_request_waits_at_galt_boundary_but_available_request_can_grant_equal_galt",
        ),
    },
    "HLA1516.1-TM-8.10-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.12-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py"),
        "positive_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_flush_queue_request_delivers_only_grant_bound_tso_messages_and_grants_earliest_tso",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.16-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.17-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.18-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.19-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_state_services",
        ),
        "negative_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_query_lookahead_requires_time_regulation_and_modify_lookahead_rejects_pending_advance",
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_negative_lookahead_is_rejected_for_regulation_and_modification",
        ),
    },
    "HLA1516.1-TM-8.21-001": {
        "implementation_refs": ("packages/hla-backend-inmemory/src/hla.backends.inmemory/time_services.py", "packages/hla-backend-inmemory/src/hla.backends.inmemory/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_management_v010.py::test_tso_message_retraction_prevents_later_delivery",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths",
        ),
    },
}


def get_curated_requirement_direct_refs() -> dict[str, dict[str, tuple[str, ...]]]:
    return _CURATED_REQUIREMENT_DIRECT_REFS


__all__ = ["get_curated_requirement_direct_refs"]
