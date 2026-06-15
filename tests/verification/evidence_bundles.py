from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _bundle(*refs: str) -> tuple[str, ...]:
    return refs


PITCH_BUNDLES: dict[str, tuple[str, ...]] = {
    "federation_lifecycle": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_matrix",
    ),
    "federation_listing": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_federation_listing_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_listing_matrix",
    ),
    "fom_module_visibility": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_module_visibility_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_module_visibility_matrix",
    ),
    "synchronization": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
    ),
    "failed_federate_synchronization": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_failed_federate_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_failed_federate_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_failed_federate_synchronization_matrix",
    ),
    "federation_lifecycle_negative": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_federation_lifecycle_negative_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_negative_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_negative_matrix",
    ),
    "scheduled_save_restore_time_state": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_scheduled_save_restore_time_state_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_scheduled_save_restore_time_state_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_scheduled_save_restore_time_state_matrix",
    ),
    "save_restore": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
    ),
    "save_abort": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_abort_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_abort_matrix",
    ),
    "save_failure": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_failure_matrix",
    ),
    "save_status_exception": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_status_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_status_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_status_exception_matrix",
    ),
    "save_request_precondition": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_request_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_request_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_request_precondition_matrix",
    ),
    "restore_request_precondition": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_request_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_precondition_matrix",
    ),
    "save_participant_exception": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_participant_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_participant_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_participant_exception_matrix",
    ),
    "abort_save_exception": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_abort_save_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_abort_save_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_abort_save_exception_matrix",
    ),
    "restore_request_failure": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_request_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_failure_matrix",
    ),
    "restore_failure": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_failure_matrix",
    ),
    "restore_participant_exception": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_participant_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_participant_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_participant_exception_matrix",
    ),
    "restore_abort": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_abort_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_matrix",
    ),
    "restore_abort_exception": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_abort_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_exception_matrix",
    ),
    "resigned_federate_callback_silence": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_resigned_federate_callback_silence_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resigned_federate_callback_silence_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resigned_federate_callback_silence_matrix",
    ),
    "resign_precondition": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_resign.py::run_resign_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_precondition_matrix",
    ),
    "resign_mom_cleanup": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_resign.py::run_resign_mom_cleanup_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_mom_cleanup_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_mom_cleanup_matrix",
    ),
    "disconnect_mom_cleanup": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_resign.py::run_disconnect_mom_cleanup_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_disconnect_mom_cleanup_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_disconnect_mom_cleanup_matrix",
    ),
    "join_precondition": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_join.py::run_join_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_join_precondition_matrix",
    ),
    "multi_participation": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_multi_participation_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_participation_matrix",
    ),
    "fom_integrity_negative": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_integrity_negative_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_integrity_negative_matrix",
    ),
    "multi_module_fom_visibility": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_module_fom_visibility_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_module_fom_visibility_matrix",
    ),
    "federation_lifecycle_with_mim": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_with_mim_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix",
    ),
    "connection_lost": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_connection_lost.py::run_connection_lost_callback_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_connection_lost_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_connection_lost_callback_matrix",
    ),
    "synchronization_registration_failure": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_registration_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
    ),
    "late_join_synchronization": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_late_join_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_late_join_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_late_join_synchronization_matrix",
    ),
    "multiple_synchronization_points": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_multiple_synchronization_points_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_multiple_synchronization_points_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multiple_synchronization_points_matrix",
    ),
    "name_reservation": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_name_reservation.py::run_name_reservation_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_name_reservation_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_name_reservation_matrix",
    ),
    "exchange": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix",
    ),
    "discovery_metadata": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_discovery_metadata.py::run_discovery_metadata_callback_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_metadata_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_metadata_callback_matrix",
    ),
    "update_advisory": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_advisory_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_advisory_callback_matrix",
    ),
    "local_delete": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_local_delete.py::run_local_delete_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_local_delete_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_local_delete_matrix",
    ),
    "requestAttributeValueUpdate": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix",
    ),
    "transportation_type": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix",
    ),
    "transportation_type_restore_persistence": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix",
    ),
    "ownership": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_matrix",
    ),
    "ownership_unavailable": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_unavailable_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix",
    ),
    "ownership_query_callback": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_query_callback_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_attribute_ownership_query_callback_matrix",
    ),
    "release_request_ownership": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_release_request_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_request_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_release_request_owned_attribute_probe",
    ),
    "release_denied_ownership": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_release_request_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_release_denied_ownership_matrix",
    ),
    "non_owner_update_rejection": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_non_owner_update_rejection_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_non_owner_update_rejection_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_non_owner_update_rejection_matrix",
    ),
    "negotiated_divesting_offer_probe": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::probe_negotiated_attribute_ownership_offer",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe",
    ),
    "negotiated_ownership": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_negotiated_attribute_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_negotiated_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix",
    ),
    "ddm_suite": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/two_federate_suite_scenarios.py::run_suite_ddm_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix",
    ),
    "ddm_object_region_lifecycle": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_object_region_lifecycle_matrix",
    ),
    "ddm_passive_region_subscription": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_passive_region_subscription_matrix",
    ),
    "ddm_declaration_gating": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ddm_object_regions.py::run_ddm_declaration_gating_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_declaration_gating_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_declaration_gating_matrix",
    ),
    "section8_state_services": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_state_services_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_services_matrix",
    ),
    "section8_logical_time_query": _bundle(
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_logical_time_query",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_logical_time_query_matrix",
    ),
    "section8_state_toggle_services": _bundle(
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_toggle_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_toggle_services_matrix",
    ),
    "section8_ordering_and_queries": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_ordering_and_query_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix",
    ),
    "section8_time_bound_queries": _bundle(
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_time_bound_queries",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix",
    ),
    "section8_available_and_flush": _bundle(
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_flush_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_flush_matrix",
    ),
    "section8_order_override": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_order_override_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_order_override_services_matrix",
    ),
    "section8_early_timestamp_send": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_early_timestamp_send_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_early_timestamp_send_rejection",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_early_timestamp_send_rejection_matrix",
    ),
    "section8_available_and_retraction": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_available_and_retraction_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_retraction",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_retraction_matrix",
    ),
    "section8_request_retraction": _bundle(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_request_retraction_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_request_retraction_callback",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_request_retraction_callback_matrix",
    ),
    "lookahead": _bundle(
        "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_state_services",
        "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_blocks_early_timestamped_send",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lookahead_matrix",
    ),
}


def bundle(name: str) -> tuple[str, ...]:
    return PITCH_BUNDLES[name]
