from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|late|shadow|owner|acquirer|publisher|subscriber|sender|receiver|left|right|rti|observer|requester|rival|r1|r2)\.[A-Za-z_][A-Za-z0-9_]*\("
)

FILE_FUNCTIONS: dict[Path, dict[str, str]] = {
    ROOT / "tests" / "scenarios" / "test_federation_lifecycle_backend_matrix.py": {
        "test_python_backend_federation_lifecycle_matrix": "run_federation_lifecycle_scenario",
        "test_python_backend_federation_lifecycle_with_mim_matrix": "run_federation_lifecycle_scenario",
        "test_python_backend_federation_listing_matrix": "run_federation_listing_scenario",
        "test_python_backend_fom_module_visibility_matrix": "run_fom_module_visibility_scenario",
        "test_python_backend_federation_lifecycle_negative_matrix": "run_federation_lifecycle_negative_scenario",
        "test_python_backend_multi_participation_matrix": "run_multi_participation_scenario",
        "test_python_backend_fom_integrity_negative_matrix": "run_fom_integrity_negative_scenario",
        "test_python_backend_multi_module_fom_visibility_matrix": "run_multi_module_fom_visibility_scenario",
    },
    ROOT / "tests" / "scenarios" / "test_federation_management_backend_matrix.py": {
        "test_python_backend_synchronization_matrix": "run_synchronization_scenario",
        "test_python_connection_lost_callback_matrix": "run_connection_lost_callback_scenario",
        "test_python_backend_synchronization_registration_failure_matrix": "run_synchronization_registration_failure_scenario",
        "test_python_backend_failed_federate_synchronization_matrix": "run_failed_federate_synchronization_scenario",
        "test_python_backend_late_join_synchronization_matrix": "run_late_join_synchronization_scenario",
        "test_python_backend_multiple_synchronization_points_matrix": "run_multiple_synchronization_points_scenario",
        "test_python_backend_save_restore_matrix": "run_save_restore_scenario",
        "test_python_backend_save_restore_queued_callback_matrix": "run_save_restore_queued_callback_scenario",
        "test_python_backend_scheduled_save_restore_time_state_matrix": "run_scheduled_save_restore_time_state_scenario",
        "test_python_backend_restore_object_state_matrix": "run_restore_object_state_scenario",
        "test_python_backend_restore_federate_local_state_matrix": "run_restore_federate_local_state_scenario",
        "test_python_backend_save_failure_matrix": "run_save_failure_scenario",
        "test_python_backend_restore_request_failure_matrix": "run_restore_request_failure_scenario",
        "test_python_backend_restore_failure_matrix": "run_restore_failure_scenario",
        "test_python_backend_save_abort_matrix": "run_save_abort_scenario",
        "test_python_backend_restore_abort_matrix": "run_restore_abort_scenario",
        "test_python_backend_restore_abort_exception_matrix": "run_restore_abort_exception_scenario",
        "test_python_backend_save_status_exception_matrix": "run_save_status_exception_scenario",
        "test_python_backend_restore_status_exception_matrix": "run_restore_status_exception_scenario",
        "test_python_backend_save_request_precondition_matrix": "run_save_request_precondition_scenario",
        "test_python_backend_restore_request_precondition_matrix": "run_restore_request_precondition_scenario",
        "test_python_backend_save_participant_exception_matrix": "run_save_participant_exception_scenario",
        "test_python_backend_abort_save_exception_matrix": "run_abort_save_exception_scenario",
        "test_python_backend_restore_participant_exception_matrix": "run_restore_participant_exception_scenario",
        "test_python_backend_resigned_federate_callback_silence_matrix": "run_resigned_federate_callback_silence_scenario",
        "test_python_backend_resign_precondition_matrix": "run_resign_precondition_scenario",
        "test_python_backend_resign_mom_cleanup_matrix": "run_resign_mom_cleanup_scenario",
        "test_python_backend_disconnect_mom_cleanup_matrix": "run_disconnect_mom_cleanup_scenario",
        "test_python_backend_join_precondition_matrix": "run_join_precondition_scenario",
    },
    ROOT / "tests" / "scenarios" / "test_object_management_backend_matrix.py": {
        "test_python_backend_exchange_matrix": "run_two_federate_exchange_scenario",
        "test_python_discovery_metadata_callback_matrix": "run_discovery_metadata_callback_scenario",
        "test_python_discovery_class_matrix": "run_discovery_class_scenario",
        "test_python_name_reservation_matrix": "run_name_reservation_scenario",
        "test_python_backend_declaration_management_matrix": "run_declaration_management_scenario",
        "test_python_backend_declaration_management_overload_matrix": "run_declaration_management_scenario",
        "test_python_backend_declaration_invalid_attribute_publication_matrix": "run_declaration_invalid_attribute_publication_scenario",
        "test_python_backend_time_managed_declaration_independence_matrix": "run_time_managed_declaration_independence_scenario",
        "test_python_backend_declaration_unpublish_rejection_matrix": "run_declaration_unpublish_rejection_scenario",
        "test_python_update_advisory_callback_matrix": "run_update_advisory_callback_scenario",
        "test_python_object_scope_relevance_matrix": "run_object_scope_relevance_scenario",
        "test_python_transportation_type_matrix": "run_transportation_type_scenario",
        "test_python_transportation_type_restore_persistence_matrix": "run_transportation_type_restore_persistence_scenario",
        "test_python_transportation_type_rejection_matrix": "run_transportation_type_rejection_scenario",
        "test_python_request_attribute_value_update_matrix": "run_request_attribute_value_update_scenario",
        "test_python_request_attribute_value_update_routing_matrix": "run_request_attribute_value_update_routing_scenario",
        "test_python_orphan_object_lifecycle_matrix": "run_orphan_object_lifecycle_scenario",
        "test_python_timed_delete_matrix": "run_timed_delete_scenario",
        "test_python_local_delete_matrix": "run_local_delete_scenario",
        "test_python_update_rate_matrix": "run_update_rate_scenario",
    },
    ROOT / "tests" / "scenarios" / "test_ownership_management_backend_matrix.py": {
        "test_python_backend_ownership_matrix": "run_attribute_ownership_scenario",
        "test_python_backend_negotiated_ownership_matrix": "run_negotiated_attribute_ownership_scenario",
        "test_python_backend_release_request_ownership_matrix": "run_release_request_ownership_scenario",
        "test_python_backend_ownership_unavailable_matrix": "run_attribute_ownership_unavailable_scenario",
        "test_python_backend_release_denied_ownership_matrix": "run_release_request_ownership_scenario",
        "test_python_backend_non_owner_update_rejection_matrix": "run_non_owner_update_rejection_scenario",
    },
    ROOT / "tests" / "time" / "test_section8_backend_matrix.py": {
        "test_section8_backend_matrix_state_services": "run_section8_state_services_case",
        "test_section8_backend_matrix_logical_time_query": "run_section8_state_services_case",
        "test_section8_backend_matrix_state_toggle_services": "run_section8_state_services_case",
        "test_section8_backend_matrix_time_bound_queries": "run_section8_time_bound_query_case",
        "test_section8_backend_matrix_ordering_and_queries": "run_section8_ordering_and_query_case",
        "test_section8_backend_matrix_available_and_flush_services": "run_section8_available_and_flush_case",
        "test_section8_backend_matrix_early_timestamp_send_rejection": "run_section8_early_timestamp_send_case",
        "test_section8_backend_matrix_available_and_retraction": "run_section8_available_and_retraction_case",
        "test_section8_backend_matrix_order_override_services": "run_section8_order_override_case",
        "test_section8_backend_matrix_request_retraction_callback": "run_section8_request_retraction_case",
        "test_section8_backend_matrix_duplicate_enable_rejection": "run_section8_duplicate_enable_rejection_case",
        "test_section8_backend_matrix_tar_galt_boundary": "run_section8_tar_galt_boundary_case",
    },
    ROOT / "tests" / "time" / "test_lookahead_backend_matrix.py": {
        "test_lookahead_backend_matrix_state_services": "run_section8_state_services_case",
        "test_lookahead_backend_matrix_blocks_early_timestamped_send": "run_section8_early_timestamp_send_case",
    },
    ROOT / "tests" / "scenarios" / "test_ddm_backend_matrix.py": {
        "test_python_backend_ddm_matrix": "run_suite_ddm_scenario",
        "test_python_backend_ddm_object_region_lifecycle_matrix": "run_ddm_object_region_lifecycle_scenario",
        "test_python_backend_ddm_declaration_gating_matrix": "run_ddm_declaration_gating_scenario",
        "test_python_backend_ddm_passive_region_subscription_matrix": "run_ddm_passive_region_subscription_scenario",
    },
}


def _function_sources(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    target_names = set(FILE_FUNCTIONS[path])
    functions: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            functions[node.name] = segment
    return functions


def _function_source(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            return segment
    raise KeyError(function_name)


def _scenario_entrypoints(source: str) -> list[str]:
    return SCENARIO_ENTRYPOINT_RE.findall(source)


def _clause6_python_compliance_wrapper_refs() -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "python_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref.split("::", 1)[1]
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010" and row.get("clause_root") == "6"
        for ref in row["evidence_refs"]
        if ref.startswith("tests/scenarios/test_object_management_backend_matrix.py::")
    }


def _clause4_python_compliance_wrapper_refs() -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "python_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref.split("::", 1)[1]
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010" and row.get("clause_root") == "4"
        for ref in row["evidence_refs"]
        if ref.startswith("tests/scenarios/test_federation_lifecycle_backend_matrix.py::")
        or ref.startswith("tests/scenarios/test_federation_management_backend_matrix.py::")
    }


def test_python_matrix_wrappers_stay_shared_harness_driven() -> None:
    for path, expected_functions in FILE_FUNCTIONS.items():
        sources = _function_sources(path)
        assert set(expected_functions).issubset(sources), path
        for function_name, runner_name in expected_functions.items():
            source = sources[function_name]
            assert _scenario_entrypoints(source) == [runner_name], function_name
            assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def test_python_clause4_compliance_wrappers_are_all_guarded_by_policy() -> None:
    guarded_functions = set(FILE_FUNCTIONS[ROOT / "tests" / "scenarios" / "test_federation_lifecycle_backend_matrix.py"]) | set(
        FILE_FUNCTIONS[ROOT / "tests" / "scenarios" / "test_federation_management_backend_matrix.py"]
    )
    assert _clause4_python_compliance_wrapper_refs().issubset(guarded_functions | {"test_python_backend_lost_federate_mom_matrix"})


def test_python_clause6_compliance_wrappers_are_all_guarded_by_policy() -> None:
    path = ROOT / "tests" / "scenarios" / "test_object_management_backend_matrix.py"
    sources = _function_sources(path)
    guarded_functions = set(FILE_FUNCTIONS[path])
    assert _clause6_python_compliance_wrapper_refs().issubset(guarded_functions)
    assert _clause6_python_compliance_wrapper_refs().issubset(sources)


def test_python_lost_federate_wrapper_stays_shared_harness_driven() -> None:
    path = ROOT / "tests" / "scenarios" / "test_federation_management_backend_matrix.py"
    source = _function_source(path, "test_python_backend_lost_federate_mom_matrix")

    assert _scenario_entrypoints(source) == ["run_lost_federate_mom_scenario"]
    assert "induce_loss=observer.backend.force_federate_loss" in source
    assert "victim.backend" not in source
