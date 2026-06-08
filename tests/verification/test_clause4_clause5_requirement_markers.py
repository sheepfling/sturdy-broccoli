from __future__ import annotations

import inspect

from tests.backends import test_python_backend_federation_extended as federation_tests
from tests.backends import test_python_backend_object_ownership_extended as declaration_tests


def _marked_requirement_ids(module) -> dict[str, set[str]]:
    marked: dict[str, set[str]] = {}
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue
        requirement_ids: set[str] = set()
        for mark in getattr(func, "pytestmark", []):
            if getattr(mark, "name", "") != "requirements":
                continue
            requirement_ids.update(str(arg) for arg in mark.args if str(arg).strip())
        if requirement_ids:
            marked[name] = requirement_ids
    return marked


def test_clause4_lifecycle_services_have_explicit_requirement_markers():
    marked = _marked_requirement_ids(federation_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-FM-4.2-001",
        "HLA1516.1-FM-4.5-001",
        "HLA1516.1-FM-4.6-001",
        "HLA1516.1-FM-4.10-001",
    } <= covered
    assert "test_connect_establishes_callback_delivery_model_for_follow_on_reports" in marked
    assert "test_create_federation_execution_rejects_duplicate_name" in marked
    assert "test_destroy_federation_execution_requires_no_joined_federates" in marked
    assert "test_resign_federation_execution_rejects_not_connected_and_not_joined" in marked


def test_clause5_service_group_has_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-DM-5.2-001",
        "HLA1516.1-DM-5.3-001",
        "HLA1516.1-DM-5.4-001",
        "HLA1516.1-DM-5.5-001",
        "HLA1516.1-DM-5.6-001",
        "HLA1516.1-DM-5.7-001",
        "HLA1516.1-DM-5.8-001",
        "HLA1516.1-DM-5.9-001",
        "HLA1516.1-DM-5.10-001",
        "HLA1516.1-DM-5.11-001",
        "HLA1516.1-DM-5.12-001",
        "HLA1516.1-DM-5.13-001",
    } <= covered
    assert "test_declaration_services_reject_not_connected_not_joined_and_save_restore" in marked
    assert "test_publish_unpublish_and_unsubscribe_interaction_tail_reject_not_connected_not_joined_and_save_restore" in marked
    assert "test_start_and_stop_registration_callbacks_are_delivered" in marked
    assert "test_turn_interactions_on_and_off_callbacks_are_delivered" in marked


def test_clause6_object_management_witness_tests_have_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-OM-6.2-001",
        "HLA1516.1-OM-6.3-001",
        "HLA1516.1-OM-6.20-001",
        "HLA1516.1-OM-6.23-002",
        "HLA1516.1-OM-6.30-002",
    } <= covered
    assert "test_clause_6_federate_initiated_services_are_observable_through_mom_service_invocation_reporting" in marked
    assert "test_clause_6_callback_activity_is_visible_in_mom_summary" in marked


def test_clause7_ownership_witness_tests_have_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-OWN-7.2-001",
        "HLA1516.1-OWN-7.4-001",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.18-001",
        "HLA1516.1-OWN-7.19-001",
    } <= covered
    assert "test_clause_7_services_are_observable_through_mom_service_invocation_reporting" in marked
    assert "test_ownership_callback_sequences_and_payloads_are_exact_for_negotiated_and_cancellation_flows" in marked
    assert "test_ownership_unavailable_and_query_callbacks_are_isolated_and_exact" in marked


def test_clause8_time_management_witness_tests_have_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-TM-8.2-001",
        "HLA1516.1-TM-8.2-002",
        "HLA1516.1-TM-8.5-002",
        "HLA1516.1-TM-8.21-001",
        "HLA1516.1-TM-8_22-REQUESTRETRACTION-CB-001",
    } <= covered
    assert "test_clause_8_services_are_observable_through_mom_service_invocation_reporting" in marked
    assert "test_clause_8_enable_and_grant_callbacks_arrive_in_expected_order" in marked
    assert "test_clause_8_request_retraction_callback_arrives_after_delivered_interaction" in marked


def test_clause9_ddm_witness_tests_have_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-DDM-9.2-001",
        "HLA1516.1-DDM-9.5-001",
        "HLA1516.1-DDM-9.10-001",
        "HLA1516.1-DDM-9.13-001",
    } <= covered
    assert "test_clause_9_services_are_observable_through_mom_service_invocation_reporting" in marked


def test_clause10_support_witness_test_has_explicit_requirement_markers():
    marked = _marked_requirement_ids(declaration_tests)
    covered = set().union(*marked.values())

    assert {
        "HLA1516.1-SUP-10.2-001",
        "HLA1516.1-SUP-10.11-001",
        "HLA1516.1-SUP-10.29-001",
        "HLA1516.1-SUP-10.44-001",
    } <= covered
    assert "test_clause_10_services_are_observable_through_mom_service_invocation_reporting" in marked
