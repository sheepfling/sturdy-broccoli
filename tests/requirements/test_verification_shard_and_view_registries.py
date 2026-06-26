from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHARD_DOC = ROOT / "docs" / "verification" / "shard_registry.md"
VIEW_DOC = ROOT / "docs" / "verification" / "view_registry.md"
FOCUS_MANIFEST = ROOT / "testing" / "test_focus_manifest.json"


def test_shard_registry_lists_repo_green_gating_and_unit_shards() -> None:
    text = SHARD_DOC.read_text(encoding="utf-8")

    assert "## Repo-Green Gating Model" in text
    assert "`repo-green` is the default local green claim" in text
    assert "`repo-green-units` is the composite shard sweep" in text
    for shard_id in (
        "unit-foundation",
        "unit-python-core",
        "unit-federate-examples",
        "unit-vendor-onboarding",
        "unit-shim-tooling",
        "unit-fom-tooling",
        "unit-python-2025-core",
        "unit-transport-local",
        "unit-scenarios-light",
    ):
        assert f"`{shard_id}`" in text


def test_view_registry_lists_overlapping_focused_targets_and_rules() -> None:
    text = VIEW_DOC.read_text(encoding="utf-8")

    assert "1. views may overlap freely" in text
    assert "3. views do not replace canonical shard ownership" in text
    assert "4. views do not define repo-green by themselves" in text
    assert "hosted 2025 gRPC/FedPro route or the REST-hosted Python route?" in text
    assert "Use `transport` instead when the question is generic REST parity or transport plumbing." in text
    assert "did save/restore or rollback behavior drift on the direct lane or hosted 2025 gRPC/FedPro route?" in text
    assert "did ownership behavior drift on the direct lane or hosted 2025 gRPC/FedPro route?" in text
    assert "did DDM region-routing, overlap filtering, passive aliases, or restore cleanup drift on the direct lane or hosted 2025 gRPC/FedPro route?" in text
    assert "did MOM, callback, or support-service behavior drift on the direct lane or hosted 2025 gRPC/FedPro route?" in text
    for view_id in (
        "execution-membership",
        "python-2025-time",
        "python-2025-ddm",
        "python-2025-save-restore",
        "python-2025-ownership",
        "python-2025-mom-callbacks",
        "routes-2025",
        "requirements-2025",
        "verification",
    ):
        assert f"`{view_id}`" in text


def test_top_level_testing_and_verification_surfaces_link_to_registries() -> None:
    expectations = {
        ROOT / "README.md": (
            "docs/verification/shard_registry.md",
            "docs/verification/view_registry.md",
        ),
        ROOT / "docs" / "README.md": (
            "verification/shard_registry.md",
            "verification/view_registry.md",
        ),
        ROOT / "docs" / "test_surface.md": (
            "verification/shard_registry.md",
            "verification/view_registry.md",
        ),
        ROOT / "docs" / "verification" / "README.md": (
            "shard_registry.md",
            "view_registry.md",
        ),
        ROOT / "docs" / "junior_test_diagnosis_runbook.md": (
            "verification/shard_registry.md",
            "verification/view_registry.md",
        ),
        ROOT / "tests" / "README.md": (
            "../docs/verification/shard_registry.md",
            "../docs/verification/view_registry.md",
        ),
    }

    for path, refs in expectations.items():
        text = path.read_text(encoding="utf-8")
        for ref in refs:
            assert ref in text, f"{path.relative_to(ROOT)} missing {ref}"


def test_docs_front_door_routes_execution_rule_questions_to_requirements_and_shard() -> None:
    text = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "- `Execution rules`:" in text
    assert "use `Execution rules` when the question is join, resign, destroy, disconnect, or not-joined reserve/register/update/send/query behavior" in normalized
    assert "verify the basic execution-state rules for 2010 or 2025, including join, destroy, and not-joined update/send/query guards" in normalized
    assert "requirements/ieee-1516-2010/README.md" in text
    assert "requirements/ieee-1516-2025/README.md" in text
    assert "test_surface.md" in text


def test_execution_membership_operator_docs_keep_hosted_route_boundary_honest() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    repo_green_quickstart = (ROOT / "docs" / "repo_green_quickstart.md").read_text(encoding="utf-8")
    test_surface = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    top_to_bottom_green = (ROOT / "docs" / "top_to_bottom_green.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "junior_test_diagnosis_runbook.md").read_text(encoding="utf-8")
    verification_readme = (ROOT / "docs" / "verification" / "README.md").read_text(encoding="utf-8")
    tests_readme = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    normalized_root_readme = " ".join(root_readme.split())
    normalized_repo_green_quickstart = " ".join(repo_green_quickstart.split())
    normalized_test_surface = " ".join(test_surface.split())
    normalized_top_to_bottom_green = " ".join(top_to_bottom_green.split())
    normalized_tests_readme = " ".join(tests_readme.split())
    normalized_runbook = " ".join(runbook.split())

    assert "hosted 2025 gRPC/FedPro route evidence plus the REST-hosted Python execution-membership slice" in normalized_test_surface
    assert "it does not by itself claim every other hosted transport or wrapper variant beyond those explicit route families" in normalized_test_surface
    assert "./tools/test-focus run transport" in test_surface
    assert "this focused target includes the direct lanes plus the hosted 2025" in runbook
    assert "gRPC/FedPro and REST-hosted execution-membership proof" in runbook
    assert "it is not the generic transport lane" in runbook
    assert "./tools/test-focus run transport" in runbook
    assert "current hosted 2025 proof here is the gRPC/FedPro route slice plus the REST-hosted Python route" in verification_readme
    assert "Current exact membership of `execution-membership`:" in test_surface
    assert 'Treat this as the focused proof for "have we joined yet?" behavior on the exercised lifecycle and execution-affecting calls:' in normalized_test_surface
    assert "`createFederationExecution`" in test_surface
    assert "`joinFederationExecution`" in test_surface
    assert "`resignFederationExecution`" in test_surface
    assert "`destroyFederationExecution`" in test_surface
    assert "`updateAttributeValues`" in test_surface
    assert "`requestAttributeValueUpdateWithRegions`" in test_surface
    assert "test_destroy_federation_execution_requires_no_joined_federates" in test_surface
    assert "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore" in test_surface
    assert "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore" in test_surface
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in test_surface
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in test_surface
    assert "test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time" in test_surface
    assert "test_python_backend_join_precondition_matrix" in test_surface
    assert "test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end" in test_surface
    assert "test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route" in test_surface
    assert "test_2025_rest_transport_server_runs_shared_join_precondition_scenario" in test_surface
    assert "Current exact membership of `execution-membership`:" in runbook
    assert "Use that target specifically for the exercised execution-affecting calls:" in normalized_runbook
    assert "`updateAttributeValues`" in runbook
    assert "`requestAttributeValueUpdateWithRegions`" in runbook
    assert "test_destroy_federation_execution_requires_no_joined_federates" in runbook
    assert "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore" in runbook
    assert "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore" in runbook
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in runbook
    assert "test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time" in runbook
    assert "test_python_backend_join_precondition_matrix" in runbook
    assert "test_2025_provider_reports_federation_executions_and_members" in runbook
    assert "test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route" in runbook
    assert "test_2025_rest_transport_server_runs_shared_resign_precondition_scenario" in runbook
    assert "./tools/test-focus run execution-membership" in root_readme
    assert "join, resign, destroy, disconnect-without-resign, and not-joined reserve/register/release/delete/update/send/query/DDM guards" in normalized_root_readme
    assert "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001" in root_readme
    assert "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001" in root_readme
    assert "HLA1516.1-FM-4_6-RTIAPI-001-EXC" in root_readme
    assert "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001" in root_readme
    assert "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001" in root_readme
    assert "HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001" in root_readme
    assert "HLA2025-FI-SVC-051" in root_readme
    assert "HLA2025-FI-SVC-053" in root_readme
    assert "HLA2025-FI-SVC-077" in root_readme
    assert "HLA2025-FI-SVC-057" in root_readme
    assert "HLA2025-FI-SVC-065" in root_readme
    assert "broader transport lane only when the question is generic REST/gRPC plumbing" in normalized_root_readme
    assert "./tools/test-focus run execution-membership" in repo_green_quickstart
    assert "join, resign, destroy, disconnect-without-resign, and not-joined reserve/register/release/delete/update/send/query/DDM guards" in normalized_repo_green_quickstart
    assert "HLA2025-FI-SVC-005" in repo_green_quickstart
    assert "HLA2025-FI-SVC-051" in repo_green_quickstart
    assert "HLA2025-FI-SVC-053" in repo_green_quickstart
    assert "HLA2025-FI-SVC-077" in repo_green_quickstart
    assert "HLA2025-FI-SVC-057" in repo_green_quickstart
    assert "HLA2025-FI-SVC-065" in repo_green_quickstart
    assert "./tools/test-focus run execution-membership" in top_to_bottom_green
    assert "start with:" in top_to_bottom_green
    assert "join, resign, destroy, disconnect-without-resign, and not-joined reserve/register/release/delete/update/send/query/DDM guards" in normalized_top_to_bottom_green
    assert "HLA2025-FI-SVC-005" in top_to_bottom_green
    assert "HLA2025-FI-SVC-051" in top_to_bottom_green
    assert "HLA2025-FI-SVC-053" in top_to_bottom_green
    assert "HLA2025-FI-SVC-077" in top_to_bottom_green
    assert "HLA2025-FI-SVC-057" in top_to_bottom_green
    assert "HLA2025-FI-SVC-065" in top_to_bottom_green
    assert "./tools/test-focus run execution-membership" in tests_readme
    assert "did we break join, resign, destroy, or not-joined guard behavior?" in normalized_tests_readme
    assert "HLA1516.1-FM-4_6-RTIAPI-001-EXC" in tests_readme
    assert "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001" in tests_readme
    assert "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001" in tests_readme
    assert "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001" in tests_readme
    assert "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001" in tests_readme
    assert "HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001" in tests_readme
    assert "HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001" in tests_readme
    assert "HLA2025-FI-SVC-005" in tests_readme
    assert "HLA2025-FI-SVC-051" in tests_readme
    assert "HLA2025-FI-SVC-053" in tests_readme
    assert "HLA2025-FI-SVC-057" in tests_readme
    assert "HLA2025-FI-SVC-059" in tests_readme
    assert "HLA2025-FI-SVC-065" in tests_readme
    assert "../docs/requirements/ieee-1516-2010/README.md" in tests_readme
    assert "../docs/requirements/ieee-1516-2025/README.md" in tests_readme
    assert "Current primary requirement owners behind `execution-membership`:" in runbook
    assert "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001" in runbook
    assert "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001" in runbook
    assert "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001" in runbook
    assert "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001" in runbook
    assert "HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001" in runbook
    assert "HLA2025-FI-SVC-051" in runbook
    assert "HLA2025-FI-SVC-053" in runbook
    assert "HLA2025-FI-SVC-057" in runbook
    assert "HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001" in runbook
    assert "HLA2025-FI-SVC-065" in runbook
    assert "HLA2025-FI-SVC-077" in runbook


def test_execution_membership_docs_cover_every_manifest_test_entry() -> None:
    manifest = json.loads(FOCUS_MANIFEST.read_text(encoding="utf-8"))
    execution_membership = next(
        row for row in manifest["targets"] if row["id"] == "execution-membership"
    )
    test_entries = [
        arg
        for step in execution_membership["commands"]
        for arg in step
        if isinstance(arg, str) and arg.startswith("tests/")
    ]
    test_surface = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "junior_test_diagnosis_runbook.md").read_text(encoding="utf-8")

    for entry in test_entries:
        short_name = entry.split("::", 1)[1]
        assert short_name in test_surface, short_name
        assert short_name in runbook, short_name


def test_top_level_requirement_surfaces_link_to_closeout_program_docs() -> None:
    expectations = {
        ROOT / "README.md": (
            "docs/plans/requirements_completion_audit.md",
            "docs/plans/2025_python_rti_100_percent_worklist.md",
            "docs/plans/2010_python_rti_bounded_family_execution_worklist.md",
            "docs/plans/PLN-004_python_rti_100_percent_compliance_plan.md",
        ),
        ROOT / "docs" / "README.md": (
            "plans/requirements_completion_audit.md",
            "plans/2025_python_rti_100_percent_worklist.md",
            "plans/2010_python_rti_bounded_family_execution_worklist.md",
            "plans/PLN-004_python_rti_100_percent_compliance_plan.md",
        ),
        ROOT / "docs" / "verification" / "README.md": (
            "../plans/2025_python_rti_100_percent_worklist.md",
            "../plans/PLN-004_python_rti_100_percent_compliance_plan.md",
        ),
    }

    for path, refs in expectations.items():
        text = path.read_text(encoding="utf-8")
        for ref in refs:
            assert ref in text, f"{path.relative_to(ROOT)} missing {ref}"
