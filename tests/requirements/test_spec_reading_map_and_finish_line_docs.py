from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC_MAP = ROOT / "docs" / "spec_reading_map.md"
FINISH_LINE = ROOT / "docs" / "plans" / "requirements_finish_line.md"


def test_spec_reading_map_points_2010_partial_bucket_readers_to_execution_companion() -> None:
    text = SPEC_MAP.read_text(encoding="utf-8")

    assert "plans/2010_python_rti_bounded_family_execution_worklist.md" in text
    assert "what is the canonical 2010 owner for a partial or mixed-backend bucket?" in text
    assert "stay bounded or tighten into narrower" in text


def test_spec_reading_map_points_honest_2025_closeout_questions_to_the_worklist() -> None:
    text = SPEC_MAP.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "what blocks an honest `100%` outcome for the `2025` Python RTI lane?" in text
    assert "plans/2025_python_rti_100_percent_worklist.md" in text
    assert "plans/PLN-004_python_rti_100_percent_compliance_plan.md" in text
    assert "which exact rows still sit outside the active direct-support denominator" in normalized


def test_spec_reading_map_points_execution_guard_reruns_to_test_surface_and_view_registry() -> None:
    text = SPEC_MAP.read_text(encoding="utf-8")

    assert "how do I rerun create, join, resign, destroy, and not-joined execution guards?" in text
    assert "what proves create, join, resign/disconnect, destroy, and joined-versus-not-joined update/delete rules?" in text
    assert "where is the single cross-edition owner note for create/join/destroy/update/not-joined execution rules?" in text
    assert "[`requirements/execution_membership_rules.md`](requirements/execution_membership_rules.md)" in text
    assert "[`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md)" in text
    assert "[`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)" in text
    assert "requirements/ieee-1516-2025/federation_management_bounded_proof.md" in text
    assert "requirements/ieee-1516-2010/federation_management_bounded_family.md" in text
    assert "requirements/ieee-1516-2010/object_management_bounded_family.md" in text
    assert "requirements/ieee-1516-2010/data_distribution_management_bounded_family.md" in text
    assert "requirements/ieee-1516-2025/object_management_bounded_proof.md" in text
    assert "requirements/ieee-1516-2025/ddm_bounded_proof.md" in text
    assert "./tools/test-focus run execution-membership" in text
    assert "[`test_surface.md`](test_surface.md)" in text
    assert "[`verification/view_registry.md`](verification/view_registry.md)" in text
    assert "[`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)" in text


def test_execution_membership_rules_doc_collects_cross_edition_owner_rows_and_tests() -> None:
    text = (ROOT / "docs" / "requirements" / "execution_membership_rules.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(text.split())

    assert "# Execution-Membership Rules" in text
    assert "both editions already carry explicit owner rows and executable anchors" in normalized
    assert 'canonical "have we joined yet?" owner note' in text
    assert "where do create, join, resign, destroy, update, delete, query, and" in text
    assert "`NotConnected` before connect or after disconnect" in text
    assert "`FederateNotExecutionMember` before join and again after resign" in text
    assert "`FederatesCurrentlyJoined` when destroy is attempted while federates are still joined" in normalized
    assert "`FederationExecutionDoesNotExist` after destroy succeeds" in normalized
    assert "The lifecycle services at the center of this state machine are:" in text
    assert "`createFederationExecution`" in text
    assert "`joinFederationExecution`" in text
    assert "`resignFederationExecution`" in text
    assert "`destroyFederationExecution`" in text
    assert "create must happen before join on the exercised execution path" in normalized
    assert "Concrete execution-affecting calls that are part of this rule set include:" in text
    assert "`updateAttributeValues`" in text
    assert "`requestAttributeValueUpdate`" in text
    assert "`sendInteractionWithRegions`" in text
    assert "`requestAttributeValueUpdateWithRegions`" in text
    assert "before join, these calls reject the caller as `FederateNotExecutionMember`" in text
    assert "after resign, the same calls still reject the caller as no longer joined" in text
    assert "while federates remain joined, destroy rejects with" in text
    assert "`FederatesCurrentlyJoined`" in text
    assert "later destroy or join attempts reject with" in text
    assert "HLA1516.1-FM-4_6-RTIAPI-001-EXC" in text
    assert "HLA1516.1-FM-4_9-RTIAPI-001-EXC" in text
    assert "HLA1516.1-FM-4_10-RTIAPI-001-EXC" in text
    assert "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001" in text
    assert "HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001" in text
    assert "HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001" in text
    assert "HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001" in text
    assert "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001" in text
    assert "HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001" in text
    assert "HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001" in text
    assert "HLA2025-FI-SVC-005" in text
    assert "HLA2025-FI-SVC-008" in text
    assert "HLA2025-FI-SVC-010" in text
    assert "HLA2025-FI-SVC-011" in text
    assert "HLA2025-FI-SVC-051" in text
    assert "HLA2025-FI-SVC-057" in text
    assert "HLA2025-FI-SVC-059" in text
    assert "HLA2025-FI-SVC-061" in text
    assert "HLA2025-FI-SVC-065" in text
    assert "HLA2025-FI-SVC-067" in text
    assert "HLA2025-FI-SVC-136" in text
    assert "HLA2025-FI-SVC-137" in text
    assert "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore" in text
    assert "test_destroy_federation_execution_requires_no_joined_federates" in text
    assert "test_resign_federation_execution_rejects_not_connected_and_not_joined" in text
    assert "test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time" in text
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in text
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore" in text
    assert "test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route" in text
    assert "test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route" in text
    assert "test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route" in text
    assert "test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario" in text
    assert "test_2025_rest_transport_server_runs_shared_join_precondition_scenario" in text
    assert "test_2025_rest_transport_server_runs_shared_resign_precondition_scenario" in text
    assert "./tools/test-focus run execution-membership" in text


def test_spec_reading_map_points_save_restore_time_and_ownership_boundaries_to_named_focus_targets() -> None:
    text = SPEC_MAP.read_text(encoding="utf-8")

    assert "./tools/test-focus run python-2025-save-restore" in text
    assert "./tools/test-focus run python-2025-time" in text
    assert "./tools/test-focus run python-2025-ddm" in text
    assert "./tools/test-focus run python-2025-ownership" in text


def test_requirements_finish_line_points_to_2010_and_2025_execution_companions() -> None:
    text = FINISH_LINE.read_text(encoding="utf-8")

    assert "2010_python_rti_bounded_family_execution_worklist.md" in text
    assert "2025_python_rti_umbrella_decomposition_worklist.md" in text
    assert "execution companions now exist for the remaining `2010` bounded-family class" in text
    assert "no longer has active top-level `planned` bucket inventory" in text
    assert "`2025` `duplicate/umbrella` rows that intentionally stay non-standalone" in text
    assert "For the current honest bounded-closeout program" in text
