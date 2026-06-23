from __future__ import annotations

import ast
import inspect
from pathlib import Path
import re
import warnings

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
    IMPLEMENTED_EVIDENCE_SLICES,
    SHIM_BACKEND_EVIDENCE_PATH,
    build_spec2025_finish_line_snapshot,
)

ROOT = Path(__file__).resolve().parents[2]

_SHIM_HELPER_RUNTIME_MODULES = {
    "attribute_policy": (
        "hla.backends.python2025.attribute_policy",
        "hla.backends.python2025.ddm_default_attribute_policy",
    ),
    "attribute_scope": ("hla.backends.python2025.attribute_scope_runtime",),
    "callback_runtime": ("hla.backends.python2025.callback_runtime",),
    "catalog_runtime": ("hla.backends.python2025.catalog_runtime",),
    "declaration_management": ("hla.backends.python2025.declaration_management_runtime",),
    "directed_interaction": ("hla.backends.python2025.directed_interaction_boundary",),
    "federation_management": ("hla.backends.python2025.federation_management_runtime",),
    "interaction_policy": ("hla.backends.python2025.interaction_policy_runtime",),
    "interaction_runtime": ("hla.backends.python2025.interaction_runtime",),
    "mom_codec": ("hla.backends.python2025.mom_codec",),
    "mom_runtime": ("hla.backends.python2025.mom_runtime",),
    "object_instance_runtime": ("hla.backends.python2025.object_instance_runtime",),
    "object_model": ("hla.backends.python2025.object_model_runtime",),
    "object_reflection": ("hla.backends.python2025.object_reflection_runtime",),
    "object_region_runtime": ("hla.backends.python2025.object_region_runtime",),
    "ownership_runtime": ("hla.backends.python2025.ownership_runtime",),
    "save_restore": ("hla.backends.python2025.save_restore_lifecycle",),
    "support_lookup": ("hla.backends.python2025.support_lookup_runtime",),
    "support_policy": ("hla.backends.python2025.support_policy_runtime",),
    "time_management": ("hla.backends.python2025.time_management_runtime",),
    "update_rate": ("hla.backends.python2025.update_rate_runtime",),
}

_SHIM_HELPER_COMPAT_TESTS = {
    "attribute_policy": "test_2025_compatibility_wrapper_consumes_extracted_python2025_ddm_default_policy_semantics",
    "attribute_scope": "test_2025_compatibility_wrapper_consumes_extracted_python2025_attribute_scope_semantics",
    "callback_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_callback_semantics",
    "catalog_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_catalog_semantics",
    "declaration_management": "test_2025_compatibility_wrapper_consumes_extracted_python2025_declaration_management_semantics",
    "directed_interaction": "test_2025_compatibility_wrapper_consumes_extracted_python2025_directed_interaction_semantics",
    "federation_management": "test_2025_compatibility_wrapper_consumes_extracted_python2025_federation_management_semantics",
    "interaction_policy": "test_2025_compatibility_wrapper_consumes_extracted_python2025_interaction_policy_semantics",
    "interaction_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_interaction_runtime_semantics",
    "mom_codec": "test_2025_compatibility_wrapper_consumes_extracted_python2025_mom_codec_semantics",
    "mom_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_mom_runtime_semantics",
    "object_instance_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_object_instance_semantics",
    "object_model": "test_2025_compatibility_wrapper_consumes_extracted_python2025_object_model_semantics",
    "object_reflection": "test_2025_compatibility_wrapper_consumes_extracted_python2025_object_reflection_semantics",
    "object_region_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_object_region_semantics",
    "ownership_runtime": "test_2025_compatibility_wrapper_consumes_extracted_python2025_ownership_semantics",
    "save_restore": "test_2025_compatibility_wrapper_consumes_extracted_python2025_save_restore_semantics",
    "support_lookup": "test_2025_compatibility_wrapper_consumes_extracted_python2025_support_lookup_semantics",
    "support_policy": "test_2025_compatibility_wrapper_consumes_extracted_python2025_support_policy_semantics",
    "time_management": "test_2025_compatibility_wrapper_consumes_extracted_python2025_time_management_semantics",
    "update_rate": "test_2025_compatibility_wrapper_consumes_extracted_python2025_update_rate_semantics",
}

_SHIM_LEGACY_ALIAS_TESTS = {
    "runtime_aliases": "test_2025_legacy_shim_runtime_alias_module_exports_python2025_symbols_as_real_runtime_aliases",
}

_SHIM_MULTI_TEST_ALLOWED_IMPORTS = {
    "hla.backends.shim.object_region_runtime": {
        "test_2025_compatibility_wrapper_consumes_extracted_python2025_ddm_default_policy_semantics",
        "test_2025_compatibility_wrapper_consumes_extracted_python2025_object_region_semantics",
    }
}


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
    "HLA2025-MIL-004",
    "HLA2025-MIL-005",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_stays_aligned_with_finish_line_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    audit_path = ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md"
    audit_text = audit_path.read_text(encoding="utf-8")
    normalized_audit_text = " ".join(audit_text.split())
    normalized_audit_text_lower = normalized_audit_text.lower()

    promotion_split = snapshot["promotion_split_audit"]
    claim_audit = snapshot["completion_claim_audit"]
    blocker_partition = snapshot["full_claim_blocker_partition_audit"]
    closeout_blocker_partition = snapshot["closeout_blocker_partition_audit"]
    requirement_audit = snapshot["requirement_by_requirement_audit"]
    implementation_lane = snapshot["implementation_lane_audit"]
    current_lane_statement = snapshot["current_lane_working_surface_statement"]
    supported_boundary = snapshot["supported_boundary_statement"]
    coherence = snapshot["current_lane_coherence_audit"]
    milestone_audit = snapshot["python_rti_milestone_audit"]
    objective_audit = snapshot["objective_dimension_audit"]
    hosted_shared = snapshot["hosted_shared_scenario_coverage_audit"]
    dimensions = {item["id"]: item for item in snapshot["objective_dimension_audit"]["dimensions"]}
    vendor_time_audit = snapshot["time_window_vendor_parity_audit"]
    proof_lane_audit = snapshot["python2025_proof_lane_audit"]

    assert audit_path.exists()
    assert implementation_lane["current_2025_lane"]["backend_package"] == "hla-backend-python2025"
    assert implementation_lane["current_2025_lane"]["role"] == (
        "main full Python 2025 RTI implementation lane (owned by hla-backend-python2025 with "
        "hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support)"
    )
    assert implementation_lane["compatibility_wrapper_lane"] == {
        "backend_package": "hla-backend-shim",
        "status": "compatibility-maintained",
        "role": "compatibility-wrapper",
        "counts_as_python_2025_rti": False,
        "delegates_runtime_semantics_to": "hla-backend-python2025",
    }
    assert implementation_lane["dedicated_2025_backend_package_present"] is True
    assert implementation_lane["clean_extraction_still_optional"] is True
    assert implementation_lane["hosted_runtime_identity_evidence"]["audit_status"] == "direct-server-client-identity-aligned"
    assert implementation_lane["hosted_runtime_identity_evidence"]["route"] == "python-2025-fedpro-grpc"
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_client_report"]["implementation_lane"] == (
        "hla-backend-python2025"
    )
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_client_report"]["counts_as_python_2025_rti"] is True
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_server_report"]["transport_kind"] == "grpc"
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_server_report"]["counts_as_python_2025_rti"] is True
    assert implementation_lane["hosted_runtime_identity_evidence"]["direct_runtime_report"]["backend_kind"] == "python/2025"
    assert implementation_lane["hosted_runtime_identity_evidence"]["direct_runtime_report"]["counts_as_python_2025_rti"] is True
    shared_scenario = implementation_lane["package_owned_shared_scenario_evidence"]
    assert shared_scenario["audit_status"] == "package-owned-target-radar-2025-path-captured"
    assert shared_scenario["scenario_package"] == "hla-fom-target-radar"
    assert shared_scenario["shared_route"] == "target-radar-shared-scenario"
    assert shared_scenario["example_entrypoint"] == "python examples/target_radar_simulation.py --backend python2025 --steps 5"
    assert shared_scenario["adapter_class"] == (
        "hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter"
    )
    assert shared_scenario["supported_backend_names"] == [
        "python2025",
        "python-2025",
        "python-2025-backend",
    ]
    assert shared_scenario["python2025_runtime_report"] == {
        "backend_kind": "python/2025",
        "implementation_lane": "hla-backend-python2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }
    assert shared_scenario["shim_runtime_report"] == {
        "backend_kind": "shim/2025",
        "implementation_lane": "hla-backend-python2025",
        "counts_as_python_2025_rti": False,
        "wrapper_only": True,
    }
    assert "one package-owned compatibility adapter wraps the primary python2025 backend lane" in shared_scenario[
        "claim"
    ]
    assert "README-advertised Target/Radar python2025 example path is now executable under package-owned 2025 adapter coverage" in shared_scenario[
        "current_assessment"
    ]
    assert "factory-hosted python2025 FedPro route can execute the shared Target/Radar example scenario plus the shared future-exclusion" in shared_scenario[
        "current_assessment"
    ]
    assert shared_scenario["evidence_tests"] == [
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
    ]
    assert implementation_lane["non_python_2025_binding_lanes"] == [
        {
            "backend_package": "hla-bridge-java-common",
            "family": "standard/java",
            "role": "Java 2025 binding surface and artifact/intake evidence lane",
            "counts_as_python_2025_rti": False,
        },
        {
            "backend_package": "hla-backend-cpp-shim",
            "family": "cpp-shim",
            "role": "C++ 2025 binding surface and artifact/runtime-capability evidence lane",
            "counts_as_python_2025_rti": False,
        },
    ]
    backend_scan = implementation_lane["backend_package_scan"]
    rti2025_plugin_records = backend_scan["rti1516_2025_plugin_records"]
    assert {
        (record["package"], record["family"])
        for record in rti2025_plugin_records
    } == {
        ("hla-backend-cpp-shim", "cpp-shim"),
        ("hla-backend-cpp-shim", "standard/cpp"),
        ("hla-backend-cpp-shim", "intake/cpp"),
        ("hla-backend-python2025", "python-rti-2025"),
    }
    assert backend_scan["dedicated_python_2025_backend_candidates"] == [
        {
            "package": "hla-backend-python2025",
            "plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "name": "python2025",
            "family": "python-rti-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert all(
        record["package"] != "hla-backend-cpp-shim"
        for record in backend_scan["dedicated_python_2025_backend_candidates"]
    )
    assert all(
        record["package"] != "hla-backend-shim"
        for record in backend_scan["dedicated_python_2025_backend_candidates"]
    )
    assert promotion_split["ready_for_current_lane_promotion_as_working_surface"] is True
    assert promotion_split["ready_for_permanent_no-split_decision"] is False
    evidence_runs = {run["name"]: run for run in promotion_split["current_evidence_runs"]}
    assert evidence_runs["python2025-split-package-surface"]["result"] == "71 passed in 0.67s"
    assert "dedicated hla-backend-python2025 package surface plus local factory composition" in evidence_runs["python2025-split-package-surface"]["scope"]
    assert evidence_runs["python2025-import-boundary-guardrails"]["result"] == "163 passed in 40.34s"
    assert "explicit no-backflow proof" in evidence_runs["python2025-import-boundary-guardrails"]["scope"]
    assert (
        evidence_runs["combined-2025-verification-slice"]["result"]
        == "targeted finish-line/backend-owner audit slice ran green on current tree"
    )
    assert (
        evidence_runs["hosted-2025-fedpro-transport-suite"]["result"]
        == "252 passed in current-tree hosted FedPro transport suite"
    )
    assert "strict local FOM/MIM resolution" in evidence_runs["hosted-2025-fedpro-transport-suite"]["scope"]
    assert "directed TSO stale-queue cleanup" in evidence_runs["hosted-2025-fedpro-transport-suite"]["scope"]
    assert milestone_audit["audit_status"] == "bounded-python-rti-milestones"
    assert milestone_audit["routes"] == ["python-2025-inprocess", "python-2025-fedpro-grpc"]
    assert milestone_audit["milestone_count"] == 6
    assert milestone_audit["by_route"]["python-2025-inprocess"]["all_route_parity_covered"] is True
    assert milestone_audit["by_route"]["python-2025-fedpro-grpc"]["all_route_parity_covered"] is True
    milestone_rows = {(row["route"], row["milestone_id"]): row for row in milestone_audit["rows"]}
    assert milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["status"] == "bounded-working-slice"
    assert milestone_rows[("python-2025-fedpro-grpc", "best_attempt_working_surface")]["status"] == "bounded-working-slice"
    assert "full-fledged RTI" in milestone_rows[("python-2025-inprocess", "best_attempt_working_surface")]["boundary"]
    assert milestone_rows[("python-2025-fedpro-grpc", "best_attempt_working_surface")]["boundary"] == (
        "This milestone remains explicitly bounded to the hosted FedPro runtime slice."
    )
    assert objective_audit["surface_claim"] == "bounded-working-surface"
    assert objective_audit["ready_for_bounded_working_surface_claim"] is True
    assert objective_audit["ready_for_full_2025_completion_claim"] is False
    assert blocker_partition["audit_status"] == "full-claim-blocker-partition-captured"
    assert blocker_partition["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True
    assert blocker_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert blocker_partition["boundary_only_blocker_count"] == 4
    assert any(
        row["blocker"] == "hosted_fedpro_full_conformance_gap"
        and row["classification"] == "external-hosted-boundary"
        and row["counts_against_main_python2025_runtime_completeness"] is False
        for row in blocker_partition["blocker_rows"]
    )
    assert any(
        row["blocker"] == "standard_java_cpp_binding_behavior_gap"
        and row["classification"] == "external-binding-boundary"
        for row in blocker_partition["blocker_rows"]
    )
    assert "all sit outside direct main-lane python2025 runtime completeness" in blocker_partition["current_assessment"]
    assert closeout_blocker_partition["audit_status"] == "closeout-blocker-partition-captured"
    assert closeout_blocker_partition["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True
    assert closeout_blocker_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert closeout_blocker_partition["boundary_only_blocker_count"] == 6
    assert any(
        row["blocker"] == "implemented_slice_requirement_granularity_gap"
        and row["classification"] == "requirement-granularity-boundary"
        for row in closeout_blocker_partition["blocker_rows"]
    )
    assert any(
        row["blocker"] == "legacy_only_explicit_exclusion"
        and row["classification"] == "legacy-exclusion-boundary"
        for row in closeout_blocker_partition["blocker_rows"]
    )
    assert "all describe requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits" in closeout_blocker_partition["current_assessment"]
    assert "Canonical operator proof lanes also ran green on the current tree" in audit_text
    assert all(
        f"`{run['command']}`" in audit_text and f"`{run['result']}`" in audit_text
        for run in proof_lane_audit["current_operator_runs"]
    )
    assert "The newer finish-line partition audits make one more thing explicit" in audit_text
    assert "remaining full-claim blockers are now partitioned as external ownership boundaries" in normalized_audit_text_lower
    assert "broader closeout blockers are also partitioned as requirement-granularity, hosted-route, cross-binding, omt-extension-scope, or legacy-exclusion limits" in normalized_audit_text_lower
    assert "the main `python2025` lane is no longer being held back by vague blocker language" in normalized_audit_text_lower
    assert claim_audit["ready_for_supported-boundary_statement"] is True
    assert claim_audit["ready_for_full_2025_conformance_claim"] is False
    assert claim_audit["requirement_universe"] == {
        "total_rows": 691,
        "covered_rows": 645,
        "unsupported_boundary_rows": 0,
        "retired_or_legacy_only_rows": 24,
        "duplicate_or_umbrella_rows": 22,
    }
    assert any(
        "artifact/runtime-capability" in blocker
        for blocker in claim_audit["full_claim_blockers"]
    )
    assert any(
        "FedPro route remains a bounded runtime slice" in blocker
        for blocker in claim_audit["full_claim_blockers"]
    )
    assert requirement_audit["rows_with_complete_review_metadata"] == 691
    assert requirement_audit["covered_rows_with_evidence_paths"] == 645
    assert requirement_audit["unsupported_rows_with_explicit_boundary_flag"] == 0
    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in requirement_audit[
        "current_assessment"
    ]
    assert any(
        "third-party extension execution semantics" in blocker
        for blocker in requirement_audit["full_claim_blockers"]
    )
    assert supported_boundary["statement_status"] == "supported-boundary-statement"
    assert supported_boundary["ready"] is True
    assert "bounded working surface" in supported_boundary["statement"]
    assert "explicit legacy-only, bounded-extension, and artifact-gated boundaries" in supported_boundary["statement"]
    assert "Python 2025 in-process runtime behavior is executable and parity-covered" in supported_boundary["supported_scope"][0]
    assert any("196 catalog rows" in item for item in supported_boundary["supported_scope"])
    assert any(
        "Foreign OMT xs:any extension payloads are preserved for XML round-trip" in item
        for item in supported_boundary["explicit_boundaries"]
    )
    assert any(
        "Retired or legacy-only rows remain excluded from the supported 2025 working surface." in item
        for item in supported_boundary["explicit_boundaries"]
    )
    assert any(
        "Java and C++ bindings remain artifact/runtime-capability bounded" in item
        for item in supported_boundary["explicit_boundaries"]
    )
    assert any(
        "FedPro remains a hosted runtime slice rather than a full RTI semantics or exhaustive cross-binding conformance pass" in item
        for item in supported_boundary["explicit_boundaries"]
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
    assert any(
        "row-level requirement-by-requirement disposition audit across all 2025 rows" in blocker
        for blocker in closeout["conformance_blockers"]
    )
    assert any(
        "requirement-closeout limit rather than evidence that the main python2025 runtime lane is behaviorally incomplete"
        in blocker
        for blocker in closeout["conformance_blockers"]
    )
    assert any(
        "Java and C++ standard-route evidence" in blocker
        for blocker in closeout["conformance_blockers"]
    )
    assert any(
        "hosted FedPro route is verified as a runtime slice" in blocker
        for blocker in closeout["conformance_blockers"]
    )
    assert any(
        "hosted/cross-binding proof limit rather than evidence that the direct python2025 runtime lane lacks those semantics"
        in blocker
        for blocker in closeout["conformance_blockers"]
    )
    assert hosted_shared["audit_status"] == "hosted-shared-fedpro-scenarios-accounted-for"
    assert hosted_shared["shared_scenario_count"] == 36
    assert hosted_shared["represented_in_conformance_evidence_count"] == 36
    assert hosted_shared["zero_count_shared_scenarios"] == []
    assert hosted_shared["ready_for_full_shared_scenario_representation_claim"] is True
    assert "main python2025 runtime surface" in hosted_shared["current_assessment"]
    assert snapshot["finish_rule"] == (
        "Each future or reopened row needs a positive test, a negative unsupported-boundary test, "
        "or an explicit supported-subset/unsupported-boundary disposition before it can be counted as closed."
    )
    assert current_lane_statement["ready"] is True
    assert supported_boundary["ready"] is True
    assert coherence["ready_for_current_lane_coherent_working_surface_claim"] is True
    assert coherence["ready_for_permanent_no-split_architecture_claim"] is False
    assert dimensions["omt_handling"]["bounded_working_surface_ready"] is True
    assert dimensions["omt_handling"]["ready_for_full_claim"] is False
    assert dimensions["omt_handling"]["evidence_level"] == "decomposed-bounded-slice"
    assert tuple(dimensions["omt_handling"]["route_scenarios"]) == ()
    assert dimensions["omt_handling"]["evidence_basis"] == [
        "omt_requirement_proof_audit.ready_for_omt_traceability_claim=true",
        "omt_requirement_proof_audit.row_count=454",
        "omt_requirement_proof_audit.by_proof_status=supported-subset-traceable:454",
        "omt_decomposition.slice_ids=2025-service-utilization-crosscheck,2025-omt-extended-supported-subset,2025-omt-xs-any-extension-tolerance,2025-omt-schema-constraint-validation",
        "omt_decomposition.family_counts=service-utilization:10,extended-subset:5,xs-any:5,schema-constraint:4",
    ]
    assert "2025-omt-schema-constraint-validation" in dimensions["omt_handling"]["implemented_slice_ids"]
    assert "2025-omt-xs-any-extension-tolerance" in dimensions["omt_handling"]["implemented_slice_ids"]
    assert "named decomposition audits for the extended supported subset" in dimensions["omt_handling"]["current_assessment"]
    assert any(
        "decomposed bounded OMT working surface" in blocker or "third-party extension execution semantics" in blocker
        for blocker in dimensions["omt_handling"]["residual_blockers"]
    )
    assert dimensions["binding_routes"]["bounded_working_surface_ready"] is True
    assert dimensions["binding_routes"]["ready_for_full_claim"] is False
    assert any(
        "hosted FedPro route remains a bounded working slice" in blocker
        for blocker in dimensions["binding_routes"]["residual_blockers"]
    )

    for route in implementation_lane["python_2025_routes"]:
        assert route["is_separate_rti_family"] is False
        assert route["all_route_parity_covered"] is True

    assert vendor_time_audit["trial_pitch_safe_route_ids"] == [
        "time-window-future-exclusion",
        "time-window-restore-state",
    ]
    assert vendor_time_audit["current_trial_candidate"]["scenario_id"] == "time-window-future-exclusion"
    assert vendor_time_audit["current_trial_candidate"]["federate_count"] == 2
    assert vendor_time_audit["current_trial_candidate"]["recommended_pitch_operator_route"] == "./tools/pitch time-window-probe"

    assert "real executable python 2025 rti surface" in normalized_audit_text_lower
    assert "the main full python 2025 rti implementation now runs from `hla-backend-python2025`" in normalized_audit_text_lower
    assert "`hla-backend-shim` remains only as temporary import-compatibility scaffolding" in normalized_audit_text_lower
    assert "the repo does have a working python 2025 rti lane" in normalized_audit_text_lower
    assert "the public shell now fronts extracted runtime/state/surface modules" in normalized_audit_text_lower
    assert "`backend_factory_runtime.py`" in normalized_audit_text_lower
    assert "`runtime_state.py`" in normalized_audit_text_lower
    assert "`federation_management_runtime.py`" in normalized_audit_text_lower
    assert "`time_management_runtime.py`" in normalized_audit_text_lower
    assert "`support_services_runtime.py`" in normalized_audit_text_lower
    assert "`*_surface_mixin.py`" in normalized_audit_text_lower
    assert "the operator-facing 2025 proof contract should now be read as a named proof-family contract for the main `hla-backend-python2025` lane" in normalized_audit_text_lower
    assert "package-boundary and runtime-identity guards that keep `python2025` as the owned rti lane and `shim` as wrapper-only" in normalized_audit_text_lower
    assert "federation, object, and ddm runtime proofs across lifecycle, listing, exchange, region gating, scope relevance, and directed routing" in normalized_audit_text_lower
    assert "support-service, callback-control, ownership, and mom runtime proofs" in normalized_audit_text_lower
    assert "target/radar time-window and lookahead proofs, including future-exclusion, output ordering, pipeline, and restore-window ladders" in normalized_audit_text_lower
    assert "save/restore lifecycle, rollback, replay-guard, and gauntlet proofs" in normalized_audit_text_lower
    assert "omt validation/parsing evidence" in normalized_audit_text_lower
    assert "the main `hla-backend-python2025` runtime clears those named proof families across direct and hosted python 2025 routes" in normalized_audit_text_lower
    assert "`hla-backend-shim` remains a compatibility wrapper and should not be treated as an implementation-owner proof bucket" in normalized_audit_text_lower
    assert "java/c++ and other wrapper lanes remain supporting seam evidence over the main python 2025 runtime rather than alternate owners of the core 2025 rti" in normalized_audit_text_lower
    assert "best-attempt bounded working surface" in normalized_audit_text_lower
    assert "full-fledged rti" in normalized_audit_text_lower
    assert "java and c++ are segregated supporting binding lanes, not alternate python 2025 rtis" in normalized_audit_text_lower
    assert "bounded working-surface claim" in normalized_audit_text_lower
    assert "not a full unqualified ieee 1516.1-2025 conformance claim" in normalized_audit_text_lower
    assert "omt parsing, validation, and explicit unsupported-boundary handling" in normalized_audit_text_lower
    assert "bounded omt working surface" in normalized_audit_text_lower
    assert "third-party extension execution semantics" in normalized_audit_text_lower
    assert "row-level requirement-by-requirement disposition audit" in normalized_audit_text_lower
    assert "691 tracked 2025 rows" in normalized_audit_text_lower
    assert "covered rows with evidence paths" in normalized_audit_text_lower
    assert "unsupported, retired, and legacy-only rows are named boundaries" in normalized_audit_text_lower
    assert "future or reopened row needs a positive test" in normalized_audit_text_lower
    assert "negative unsupported-boundary test" in normalized_audit_text_lower
    assert "hosted fedpro is still a bounded runtime slice" in normalized_audit_text_lower
    assert "252 passed in current-tree hosted fedpro transport suite" in normalized_audit_text_lower
    assert "strict local fom/mim resolution" in normalized_audit_text_lower
    assert "path now executes through a package-owned `hla-fom-target-radar` compatibility adapter" in normalized_audit_text_lower
    assert "readme-advertised `python examples/target_radar_simulation.py --backend python2025 --steps 5` path now executes" in normalized_audit_text_lower
    assert "shared target/radar adapter wraps both `python2025` and the wrapper-only `shim` alias" in normalized_audit_text_lower
    assert "hosted shared-scenario coverage audit" in normalized_audit_text_lower
    assert "shared hosted fedpro scenarios: 36" in normalized_audit_text_lower
    assert "shared hosted scenarios represented in conformance evidence: 36" in normalized_audit_text_lower
    assert "ready for full shared-scenario representation claim: true" in normalized_audit_text_lower
    assert "directed tso stale-queue cleanup on restore" in normalized_audit_text_lower
    assert "partial-delivery tso retraction proof on the main `python2025` lane" in normalized_audit_text_lower
    assert "a lagging subscriber later granted to the same logical time does not receive the retracted interaction" in normalized_audit_text_lower
    assert "the hosted fedpro route replays that partial-delivery retraction invariant too" in normalized_audit_text_lower
    assert "a delivered subscriber receives `request_retraction`" in normalized_audit_text_lower
    assert "if an already-delivered target is disconnected before retraction" in normalized_audit_text_lower
    assert "does not emit a stale `requestretraction` callback afterward" in normalized_audit_text_lower
    assert "the hosted fedpro route replays that disconnect-before-retraction invariant too" in normalized_audit_text_lower
    assert "plain timestamped retraction fanout across multiple already-delivered subscribers" in normalized_audit_text_lower
    assert "callback fanout for that invariant is anchored to the direct `hla-backend-python2025` lane too" in normalized_audit_text_lower
    assert "the hosted fedpro route also replays that post-delivery retraction fanout invariant" in normalized_audit_text_lower
    assert "stale timed-remove cleanup across restore" in normalized_audit_text_lower
    assert "pre-restore timestamped delete callbacks do not leak into the restored branch" in normalized_audit_text_lower
    assert "the hosted fedpro route replays that stale timed-remove restore invariant too" in normalized_audit_text_lower
    assert "the pre-restore timed remove is cleared from queued and delivered retraction bookkeeping after restore" in normalized_audit_text_lower
    assert "restore recovers locally deleted object-known-state" in normalized_audit_text_lower
    assert "fresh post-restore reflections resume against that restored object handle" in normalized_audit_text_lower
    assert "the hosted fedpro route now replays the same local-delete restore invariant" in normalized_audit_text_lower
    assert "a fresh post-restore `reflect` callback resumes on the restored handle" in normalized_audit_text_lower
    assert "stale plain-callback cleanup across restore" in normalized_audit_text_lower
    assert "dirty post-save plain interaction callbacks do not replay after restore" in normalized_audit_text_lower
    assert "the hosted fedpro route replays that callback-policy restore invariant as well" in normalized_audit_text_lower
    assert "a fresh post-restore plain callback still routes once callback delivery is re-enabled" in normalized_audit_text_lower
    assert "reconnect-safe queued-callback cleanup over the transport seam" in normalized_audit_text_lower
    assert "a disconnected peer's disabled callback backlog is discarded before a later reconnecting federate joins" in normalized_audit_text_lower
    assert "per-federate time-state restore and flush-queue grant targeting" in normalized_audit_text_lower
    assert "restored logical times and lookaheads snap back to the saved per-federate values" in normalized_audit_text_lower
    assert "the hosted fedpro route now replays that time-state restore surface too" in normalized_audit_text_lower
    assert "the fedpro flush-queue restore path keeps grants targeted to the requesting federate" in normalized_audit_text_lower
    assert "restore-control negative paths too" in normalized_audit_text_lower
    assert "missing save-label failure, restore abort, restore precondition rejection" in normalized_audit_text_lower
    assert "the hosted fedpro route now replays that restore-control negative surface too" in normalized_audit_text_lower
    assert "participant-exception, and status-exception control flow" in normalized_audit_text_lower
    assert "transportation-type restore persistence too" in normalized_audit_text_lower
    assert "transport/order metadata restoration is not just a direct-lane claim" in normalized_audit_text_lower
    assert "ownership-specific restore recovery" in normalized_audit_text_lower
    assert "the hosted fedpro route now replays that ownership restore surface too" in normalized_audit_text_lower
    assert "cross-federate owner-visibility queries return the restored ownership graph" in normalized_audit_text_lower
    assert "cross-federate owner-visibility queries reflect the restored ownership graph" in normalized_audit_text_lower
    assert "instead of leaving that behavior proven only on the hosted fedpro route" in normalized_audit_text_lower
    assert "java and c++ binding evidence remains artifact/runtime-capability bounded" in normalized_audit_text_lower
    assert "the same boundary applies to the remaining non-python binding evidence too" in normalized_audit_text_lower
    assert "java and c++ route work is binding/adaptation-seam proof" in normalized_audit_text_lower
    assert "it is not evidence that the main python 2025 runtime is still missing core rti semantics" in normalized_audit_text_lower
    assert "python2025_direct_bounded_proof.md" in audit_text
    assert "compact excluded-area inventory behind this bounded claim" in normalized_audit_text_lower
    assert "forcing readers to mine the full generated finish-line bundle" in normalized_audit_text_lower
    assert "fom_backed_scenario_bounded_proof.md" in audit_text
    assert "save_restore_bounded_proof.md" in audit_text
    assert "callback_bounded_proof.md" in audit_text
    assert "lookahead_window_bounded_proof.md" in audit_text
    assert "tracked example/fom-backed scenario boundary behind the same bounded claim" in normalized_audit_text_lower
    assert "without implying that every possible example fom composition is proven" in normalized_audit_text_lower
    assert "explicit save/restore rollback families behind the same bounded claim" in normalized_audit_text_lower
    assert "lifecycle-control, rollback, routing/policy, ownership, and time-window/time-state recovery families auditable" in normalized_audit_text_lower
    assert "explicit callback families behind the same bounded claim" in normalized_audit_text_lower
    assert "declaration advisories, object delivery, ownership callbacks, time/retraction callbacks, and callback-control hygiene auditable" in normalized_audit_text_lower
    assert "explicit target/radar lookahead ladder behind the same bounded claim" in normalized_audit_text_lower
    assert "closure, future-exclusion, output-delivery, consumer-order, pipeline, negative-oracle, and pitch-safe vendor-credence boundaries auditable" in normalized_audit_text_lower
    assert "promoting the current lane as the working python 2025 rti surface" in normalized_audit_text_lower
    assert "the architecture should still preserve a clean enough seam" in normalized_audit_text_lower
    assert "the repo is not building two duplicate python 2025 rtis" in normalized_audit_text_lower
    assert "keep narrowing the shim only if" in normalized_audit_text_lower
    assert "it owns directed-interaction target-selection, save/restore lifecycle, and ddm/default-policy semantics" in normalized_audit_text_lower
    assert "it is now executable as the standalone promoted rti backend package" in normalized_audit_text_lower
    assert "it does not delegate back to `hla.backends.shim.backend.create_shim_backend`" in normalized_audit_text_lower
    assert "bounded disposition evidence" in normalized_audit_text_lower
    assert "not merely polishing a fake adapter" in normalized_audit_text_lower
    assert "pitch trial compatibility" in normalized_audit_text_lower
    assert "time-window-future-exclusion" in normalized_audit_text_lower
    assert "two-federate constraint" in normalized_audit_text_lower
    assert "no available prti federate seats" in normalized_audit_text_lower
    assert "vendor/runtime seat availability" in normalized_audit_text_lower
    assert "this does not upgrade java or c++ bindings into exhaustive behavior-conformance lanes" in normalized_audit_text_lower
    assert "this does not turn the hosted fedpro route into a full rti semantics or mom action/request conformance pass" in normalized_audit_text_lower


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_snapshot_block_matches_live_finish_line_state() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    implementation_lane = snapshot["implementation_lane_audit"]
    promotion_split = snapshot["promotion_split_audit"]
    hosted_shared = snapshot["hosted_shared_scenario_coverage_audit"]
    vendor_time_audit = snapshot["time_window_vendor_parity_audit"]
    audit_path = ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md"
    markdown = audit_path.read_text(encoding="utf-8")

    expected_lines = [
        f"- Main 2025 RTI package: `{implementation_lane['current_2025_lane']['backend_package']}`",
        "- Wrapper-only compatibility package: `hla-backend-shim`",
        f"- 2010 pure Python RTI package: `{implementation_lane['reference_2010_lane']['backend_package']}`",
        f"- Python 2025 route count: `{len(implementation_lane['python_2025_routes'])}`",
        f"- Hosted Python 2025 route: `{implementation_lane['hosted_runtime_identity_evidence']['route']}`",
        f"- Non-Python binding lanes kept segregated: `{len(implementation_lane['non_python_2025_binding_lanes'])}`",
        f"- Recent combined 2025 verification slice: `{next(run['result'] for run in promotion_split['current_evidence_runs'] if run['name'] == 'combined-2025-verification-slice')}`",
        f"- Recent hosted 2025 FedPro transport suite: `{next(run['result'] for run in promotion_split['current_evidence_runs'] if run['name'] == 'hosted-2025-fedpro-transport-suite')}`",
        f"- Shared hosted FedPro scenarios represented: `{hosted_shared['represented_in_conformance_evidence_count']} / {hosted_shared['shared_scenario_count']}`",
        f"- Trial Pitch-safe time-window routes: `{vendor_time_audit['trial_pitch_safe_route_count']}`",
    ]
    for line in expected_lines:
        assert line in markdown

    def extract_int(label: str) -> int:
        match = re.search(rf"- {re.escape(label)}: `(\d+)`", markdown)
        assert match, label
        return int(match.group(1))

    def extract_ratio(label: str) -> tuple[int, int]:
        match = re.search(rf"- {re.escape(label)}: `(\d+) / (\d+)`", markdown)
        assert match, label
        return int(match.group(1)), int(match.group(2))

    assert extract_int("Python 2025 route count") == len(implementation_lane["python_2025_routes"])
    assert extract_int("Non-Python binding lanes kept segregated") == len(
        implementation_lane["non_python_2025_binding_lanes"]
    )
    assert extract_ratio("Shared hosted FedPro scenarios represented") == (
        hosted_shared["represented_in_conformance_evidence_count"],
        hosted_shared["shared_scenario_count"],
    )
    assert extract_int("Trial Pitch-safe time-window routes") == vendor_time_audit["trial_pitch_safe_route_count"]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_main_runtime_suite_free_of_shim_named_tests() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    spec_test_text = spec_test_path.read_text(encoding="utf-8")
    normalized_spec_text = " ".join(spec_test_text.split()).lower()
    shim_named_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_test_text, re.M)
        if name.startswith("test_2025_shim_")
    )

    assert "main executable 2025 spec suite for the primary python2025 runtime lane" in normalized_spec_text
    assert "the substantive runtime under test is ``hla-backend-python2025`` / ``hla.backends.python2025``" in normalized_spec_text
    assert "explicit shim coverage in this module is limited to wrapper-specific compatibility behavior and re-export consumption checks" in normalized_spec_text
    assert shim_named_tests == []


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_main_validation_suite_free_of_shim_named_tests() -> None:
    validation_test_path = ROOT / "tests" / "test_rti1516_2025_validation.py"
    validation_test_text = validation_test_path.read_text(encoding="utf-8")
    shim_named_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", validation_test_text, re.M)
        if name.startswith("test_2025_shim_")
    )

    assert shim_named_tests == []


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_prevents_fake_dual_provider_tests_with_hardcoded_runtime_selection() -> None:
    audited_paths = (
        ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py",
        ROOT / "tests" / "test_python_api_spec.py",
        ROOT / "tests" / "test_hla_factory_composition.py",
        ROOT / "tests" / "test_rti1516_2025_encoding_auth_contexts.py",
    )
    violations: list[str] = []
    parameterized_names = {"backend_name", "provider"}

    for path in audited_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            decorator_lines = [
                ast.get_source_segment(path.read_text(encoding="utf-8"), decorator) or ""
                for decorator in node.decorator_list
            ]
            dual_provider_parametrized = any(
                "pytest.mark.parametrize" in line
                and "python2025" in line
                and "shim" in line
                and any(name in line for name in parameterized_names)
                for line in decorator_lines
            )
            if not dual_provider_parametrized:
                continue

            parameter_names = {arg.arg for arg in node.args.args}
            if not (parameter_names & parameterized_names):
                continue

            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                for keyword in child.keywords:
                    if keyword.arg not in {"backend", "provider"}:
                        continue
                    if not isinstance(keyword.value, ast.Constant) or not isinstance(keyword.value.value, str):
                        continue
                    if keyword.value.value not in {"python2025", "shim"}:
                        continue
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}:{node.name}:{keyword.arg}={keyword.value.value!r}"
                    )

    assert violations == []


@pytest.mark.requirements(
    "HLA2025-MIL-004",
    "HLA2025-MIL-005",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_keeps_time_window_proof_ladder_negative_oracle_guards() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    spec_test_text = spec_test_path.read_text(encoding="utf-8")
    negative_oracle_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_test_text, re.M)
        if "_oracle_rejects_" in name
    )

    assert negative_oracle_tests == [
        "test_2025_consumer_order_oracle_rejects_reversed_delivery_order",
        "test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary",
        "test_2025_output_delivery_oracle_rejects_output_before_window_close",
        "test_2025_pipeline_oracle_rejects_cross_window_payload_contamination",
        "test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay",
        "test_2025_receive_order_poison_oracle_rejects_closed_window_mutation",
        "test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore",
        "test_2025_restore_window_state_oracle_rejects_dirty_post_close_callback_leak",
    ]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_backend_module_thin_and_wrapper_only() -> None:
    shim_backend_path = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "backend.py"
    tree = ast.parse(shim_backend_path.read_text(encoding="utf-8"))
    top_level = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]

    assert len(shim_backend_path.read_text(encoding="utf-8").splitlines()) <= 50
    assert [type(node).__name__ for node in top_level] == [
        "ImportFrom",
        "ImportFrom",
        "ImportFrom",
        "Assign",
    ]
    import_from_nodes = [node for node in top_level if isinstance(node, ast.ImportFrom)]
    assert [node.module for node in import_from_nodes] == [
        "__future__",
        "hla.backends.python2025.backend",
        "hla.backends.python2025.compatibility_wrapper",
    ]
    runtime_import = import_from_nodes[1]
    assert sorted(alias.name for alias in runtime_import.names) == [
        "MOM_2025_FEDERATE_ADJUST_LEAVES",
        "MOM_2025_FEDERATE_REQUEST_LEAVES",
        "MOM_2025_FEDERATE_SERVICE_LEAVES",
        "MOM_2025_FEDERATION_ADJUST_LEAVES",
        "MOM_2025_FEDERATION_REQUEST_LEAVES",
        "MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES",
    ]
    wrapper_import = import_from_nodes[2]
    assert sorted(alias.name for alias in wrapper_import.names) == [
        "Shim2025Backend",
        "Shim2025RTIAmbassador",
        "create_shim_backend",
    ]
    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree))

    runtime_alias_path = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "runtime_aliases.py"
    runtime_alias_tree = ast.parse(runtime_alias_path.read_text(encoding="utf-8"), filename=str(runtime_alias_path))
    runtime_alias_top_level = [
        node
        for node in runtime_alias_tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    assert [type(node).__name__ for node in runtime_alias_top_level] == ["ImportFrom", "ImportFrom", "Assign"]
    runtime_alias_imports = [node for node in runtime_alias_top_level if isinstance(node, ast.ImportFrom)]
    assert [node.module for node in runtime_alias_imports] == ["__future__", "hla.backends.python2025.backend"]
    assert sorted(alias.name for alias in runtime_alias_imports[1].names) == [
        "Python2025Backend",
        "Python2025BackendInfo",
        "Python2025BackendScaffold",
        "Python2025RTIAmbassador",
        "create_python2025_backend",
    ]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_compatibility_modules_as_thin_forwarders() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    forwarder_modules = sorted(
        path
        for path in shim_dir.glob("*.py")
        if path.name not in {"__init__.py", "backend.py", "plugin.py", "runtime_aliases.py"}
    )

    assert forwarder_modules

    for path in forwarder_modules:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        top_level = [
            node
            for node in tree.body
            if not (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
        ]

        assert len(source.splitlines()) <= 80, path.name
        assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree)), path.name

        import_from_nodes = [node for node in top_level if isinstance(node, ast.ImportFrom)]
        assign_nodes = [node for node in top_level if isinstance(node, ast.Assign)]
        other_nodes = [node for node in top_level if not isinstance(node, (ast.ImportFrom, ast.Assign))]

        assert other_nodes == [], path.name
        assert [node.module for node in import_from_nodes][0] == "__future__", path.name
        assert all(
            node.module is not None and node.module.startswith("hla.backends.python2025.")
            for node in import_from_nodes[1:]
        ), path.name
        assert all(
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
            for node in assign_nodes
        ), path.name


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_plugin_discovery_split_between_runtime_and_wrapper() -> None:
    from hla.backends.python2025.plugin import plugin as python2025_plugin
    from hla.backends.shim.plugin import plugin as shim_plugin
    from hla.rti.plugin_api import RTIBackendDiscovery

    runtime_plugin = python2025_plugin()
    wrapper_plugin = shim_plugin()
    wrapper_discovery = wrapper_plugin.discover()

    assert runtime_plugin.name == "python2025"
    assert runtime_plugin.family == "python-rti-2025"
    assert runtime_plugin.supports == ("rti1516_2025",)
    assert runtime_plugin.aliases == ("python-2025", "python-2025-backend")
    assert runtime_plugin.description == "Primary Python 2025 RTI implementation package."
    assert runtime_plugin.create_backend.__module__ == "hla.backends.python2025.backend"
    assert runtime_plugin.create_backend.__name__ == "create_python2025_backend"
    runtime_discovery = runtime_plugin.discover()
    assert isinstance(runtime_discovery, RTIBackendDiscovery)
    assert runtime_discovery.name == "python2025"
    assert runtime_discovery.family == "python-rti-2025"
    assert runtime_discovery.supports == ("rti1516_2025",)
    assert runtime_discovery.available is True
    assert runtime_discovery.info.kind == "python/2025"
    assert runtime_discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert runtime_discovery.info.details["counts_as_python_2025_rti"] is True

    assert wrapper_plugin.name == "shim"
    assert wrapper_plugin.family == "compatibility-wrapper-2025"
    assert wrapper_plugin.supports == ("rti1516_2025",)
    assert wrapper_plugin.aliases == ()
    assert "Deprecated compatibility-wrapper alias" in wrapper_plugin.description
    assert wrapper_plugin.create_backend.__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert wrapper_plugin.create_backend.__name__ == "create_shim_backend"
    assert wrapper_plugin.create_backend is not runtime_plugin.create_backend
    assert isinstance(wrapper_discovery, RTIBackendDiscovery)
    assert wrapper_discovery.name == "shim"
    assert wrapper_discovery.family == "compatibility-wrapper-2025"
    assert wrapper_discovery.supports == ("rti1516_2025",)
    assert wrapper_discovery.available is True
    assert wrapper_discovery.info.kind == "shim/2025"
    assert wrapper_discovery.info.details["counts_as_python_2025_rti"] is False
    assert wrapper_discovery.info.details["wrapper_only"] is True
    assert "deprecated compatibility-wrapper alias" in wrapper_discovery.description.lower()


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_marks_java_and_cpp_2025_routes_as_non_primary_binding_lanes() -> None:
    from hla.bridges.java.common.java_shim_2025 import JavaRouteShim2025Backend
    from hla.bridges.java.common.java_standard_2025 import discover_java_standard_2025
    from hla.backends.cpp_shim.backend_2025 import CppRouteShim2025Backend
    from hla.backends.cpp_shim.standard import discover_cpp_standard
    from hla.rti.plugin_api import BackendRequest
    from hla.rti1516_2025.plugin import plugin as spec_plugin

    request = BackendRequest(spec=spec_plugin().spec)

    java_route = JavaRouteShim2025Backend("jpype", request)
    cpp_route = CppRouteShim2025Backend("pybind", request)
    java_standard = discover_java_standard_2025("jpype")
    cpp_standard = discover_cpp_standard("pybind", "2025")

    for details in (
        java_route.info.details,
        cpp_route.info.details,
        java_standard.details,
        cpp_standard.details,
    ):
        assert details["runtime_provider"] == "python2025"
        assert details["implementation_lane"] == "hla-backend-python2025"
        assert details["counts_as_python_2025_rti"] is False


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary() -> None:
    backend_doc = (ROOT / "docs" / "python_rti_backend.md").read_text(encoding="utf-8")
    route_inventory_doc = (ROOT / "docs" / "backend_route_inventory.md").read_text(encoding="utf-8")
    route_inventory_routes_doc = (ROOT / "docs" / "backend_route_inventory_routes.md").read_text(encoding="utf-8")
    route_inventory_remote_doc = (ROOT / "docs" / "backend_route_inventory_remote.md").read_text(encoding="utf-8")
    route_inventory_commands_doc = (ROOT / "docs" / "backend_route_inventory_commands.md").read_text(encoding="utf-8")
    networked_doc = (ROOT / "docs" / "networked_rti_python.md").read_text(encoding="utf-8")
    shim_routes_doc = (ROOT / "docs" / "language_shim_routes.md").read_text(encoding="utf-8")
    time_model_doc = (ROOT / "docs" / "verification" / "time_model_compliance.md").read_text(encoding="utf-8")
    architecture_doc = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    options_matrix_doc = (ROOT / "docs" / "rti_options_and_test_matrix.md").read_text(encoding="utf-8")
    verification_plan_doc = (ROOT / "docs" / "verification" / "verification_plan.md").read_text(encoding="utf-8")
    validation_plan_doc = (ROOT / "docs" / "verification" / "validation_plan.md").read_text(encoding="utf-8")
    requirements_hierarchy_doc = (ROOT / "docs" / "verification" / "requirements_hierarchy.md").read_text(encoding="utf-8")
    conformance_matrix_doc = (ROOT / "docs" / "backend_conformance_matrix.md").read_text(encoding="utf-8")
    test_surface_doc = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    top_to_bottom_green_doc = (ROOT / "docs" / "top_to_bottom_green.md").read_text(encoding="utf-8")
    compliance_discovery_doc = (ROOT / "docs" / "backend_compliance_discovery.md").read_text(encoding="utf-8")
    python_environment_doc = (ROOT / "docs" / "python_environment.md").read_text(encoding="utf-8")
    two_federate_doc = (ROOT / "docs" / "two_federate_quickstart.md").read_text(encoding="utf-8")
    install_matrix_doc = (ROOT / "docs" / "install_matrix.md").read_text(encoding="utf-8")
    agent_runbook_doc = (ROOT / "docs" / "agent_runbook.md").read_text(encoding="utf-8")
    local_verification_commands_doc = (ROOT / "docs" / "local_verification_commands.md").read_text(encoding="utf-8")
    documentation_hierarchy_doc = (ROOT / "docs" / "documentation_hierarchy.md").read_text(encoding="utf-8")
    vendor_runtime_runner_guide_doc = (ROOT / "docs" / "vendor_runtime_runner_guide.md").read_text(encoding="utf-8")
    codex_runner_authorization_doc = (ROOT / "docs" / "codex_runner_authorization.md").read_text(encoding="utf-8")
    capability_doc = (ROOT / "docs" / "backend_capability_matrix.md").read_text(encoding="utf-8")
    factory_map_doc = (ROOT / "docs" / "rti_factory_reading_map.md").read_text(encoding="utf-8")
    python_rti_map_doc = (ROOT / "docs" / "python_rti_reading_map.md").read_text(encoding="utf-8")
    requirements_index_doc = (ROOT / "docs" / "requirements" / "ieee-1516-2025" / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    first_run_doc = (ROOT / "docs" / "first_run.md").read_text(encoding="utf-8")
    tests_readme = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    tools_readme = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
    tools_python = (ROOT / "tools" / "python").read_text(encoding="utf-8")
    scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    package_layout_doc = (ROOT / "docs" / "package_layout.md").read_text(encoding="utf-8")
    workspace_layout_doc = (ROOT / "docs" / "workspace_layout.md").read_text(encoding="utf-8")
    dependency_tree_doc = (ROOT / "docs" / "package_dependency_tree.md").read_text(encoding="utf-8")
    hierarchy_doc = (ROOT / "docs" / "package_hierarchy_and_versioning.md").read_text(encoding="utf-8")
    python2025_readme = (ROOT / "packages" / "hla-backend-python2025" / "README.md").read_text(encoding="utf-8")
    python2025_pyproject = (ROOT / "packages" / "hla-backend-python2025" / "pyproject.toml").read_text(encoding="utf-8")
    shim_readme = (ROOT / "packages" / "hla-backend-shim" / "README.md").read_text(encoding="utf-8")
    shim_pyproject = (ROOT / "packages" / "hla-backend-shim" / "pyproject.toml").read_text(encoding="utf-8")
    migration_doc = (ROOT / "packages" / "hla-backend-shim" / "MIGRATION.md").read_text(encoding="utf-8")
    shim_docs_readme = (ROOT / "packages" / "hla-backend-shim" / "docs" / "README.md").read_text(encoding="utf-8")
    grpc_readme = (ROOT / "packages" / "hla-transport-grpc" / "README.md").read_text(encoding="utf-8")
    packages_readme = (ROOT / "packages" / "README.md").read_text(encoding="utf-8")

    normalized_backend = " ".join(backend_doc.split()).lower()
    normalized_route_inventory = " ".join(route_inventory_doc.split()).lower()
    normalized_route_inventory_routes = " ".join(route_inventory_routes_doc.split()).lower()
    normalized_route_inventory_remote = " ".join(route_inventory_remote_doc.split()).lower()
    normalized_route_inventory_commands = " ".join(route_inventory_commands_doc.split()).lower()
    normalized_networked = " ".join(networked_doc.split()).lower()
    normalized_shim_routes = " ".join(shim_routes_doc.split()).lower()
    normalized_time_model = " ".join(time_model_doc.split()).lower()
    normalized_architecture = " ".join(architecture_doc.split()).lower()
    normalized_options_matrix = " ".join(options_matrix_doc.split()).lower()
    normalized_verification_plan = " ".join(verification_plan_doc.split()).lower()
    normalized_validation_plan = " ".join(validation_plan_doc.split()).lower()
    normalized_requirements_hierarchy = " ".join(requirements_hierarchy_doc.split()).lower()
    normalized_conformance_matrix = " ".join(conformance_matrix_doc.split()).lower()
    normalized_test_surface = " ".join(test_surface_doc.split()).lower()
    normalized_top_to_bottom_green = " ".join(top_to_bottom_green_doc.split()).lower()
    normalized_compliance_discovery = " ".join(compliance_discovery_doc.split()).lower()
    normalized_python_environment = " ".join(python_environment_doc.split()).lower()
    normalized_two_federate = " ".join(two_federate_doc.split()).lower()
    normalized_install_matrix = " ".join(install_matrix_doc.split()).lower()
    normalized_agent_runbook = " ".join(agent_runbook_doc.split()).lower()
    normalized_local_verification_commands = " ".join(local_verification_commands_doc.split()).lower()
    normalized_documentation_hierarchy = " ".join(documentation_hierarchy_doc.split()).lower()
    normalized_vendor_runtime_runner_guide = " ".join(vendor_runtime_runner_guide_doc.split()).lower()
    normalized_codex_runner_authorization = " ".join(codex_runner_authorization_doc.split()).lower()
    normalized_capability = " ".join(capability_doc.split()).lower()
    normalized_factory_map = " ".join(factory_map_doc.split()).lower()
    normalized_python_rti_map = " ".join(python_rti_map_doc.split()).lower()
    normalized_requirements_index = " ".join(requirements_index_doc.split()).lower()
    normalized_docs_index = " ".join(docs_index.split()).lower()
    normalized_first_run = " ".join(first_run_doc.split()).lower()
    normalized_tests_readme = " ".join(tests_readme.split()).lower()
    normalized_tools_readme = " ".join(tools_readme.split()).lower()
    normalized_tools_python = " ".join(tools_python.split()).lower()
    normalized_scripts_readme = " ".join(scripts_readme.split()).lower()
    normalized_root_readme = " ".join(root_readme.split()).lower()
    normalized_package_layout = " ".join(package_layout_doc.split()).lower()
    normalized_workspace_layout = " ".join(workspace_layout_doc.split()).lower()
    normalized_dependency_tree = " ".join(dependency_tree_doc.split()).lower()
    normalized_hierarchy = " ".join(hierarchy_doc.split()).lower()
    normalized_python2025_readme = " ".join(python2025_readme.split()).lower()
    normalized_python2025_pyproject = " ".join(python2025_pyproject.split()).lower()
    normalized_shim_readme = " ".join(shim_readme.split()).lower()
    normalized_shim_pyproject = " ".join(shim_pyproject.split()).lower()
    normalized_migration = " ".join(migration_doc.split()).lower()
    normalized_shim_docs_readme = " ".join(shim_docs_readme.split()).lower()
    normalized_grpc_readme = " ".join(grpc_readme.split()).lower()
    normalized_packages = " ".join(packages_readme.split()).lower()

    assert "the main full runtime now executes from `hla-backend-python2025`" in normalized_backend
    assert "sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_backend
    assert 'use `backend="python2025"`' in normalized_backend
    assert "preserving legacy shim import paths" in normalized_backend
    assert "carrying only thin compatibility indirection while the executable runtime stays in `hla-backend-python2025`" in normalized_backend
    assert "support services, callbacks, omt handling, and binding and hosted routes" in normalized_backend
    assert "partial-delivery retraction against lagging subscribers" in normalized_backend
    assert "disconnected-target retraction cleanup" in normalized_backend
    assert "post-delivery plain retraction fanout" in normalized_backend
    assert "stale timed-remove cleanup across restore" in normalized_backend
    assert "stale plain-callback cleanup across restore" in normalized_backend
    assert "per-federate time-state restore" in normalized_backend
    assert "flush-queue grant targeting" in normalized_backend
    assert "restore recovery of in-flight ownership negotiations" in normalized_backend
    assert "cross-federate owner-visibility state" in normalized_backend
    assert "the direct in-process 2025 suite now explicitly proves partial-delivery tso retraction semantics on the main `python2025` lane" in normalized_backend
    assert 'main 2025 runtime selection should use `backend="python2025"`' in normalized_python_rti_map
    assert 'the legacy `shim` spelling is intentionally rejected on the public factory surface' in normalized_factory_map
    assert "retracted, and withheld from a lagging subscriber that later advances to the same timestamp" in normalized_backend
    assert "the hosted fedpro route now replays that partial-delivery retraction invariant too" in normalized_backend
    assert "retraction callbacks are dropped for a delivered target that disconnects before the publisher retracts the interaction" in normalized_backend
    assert "the hosted fedpro route now replays that disconnect-before-retraction invariant too" in normalized_backend
    assert "plain timestamped post-delivery retraction fanout" in normalized_backend
    assert "a later retract fans out `requestretraction` coherently to each delivered subscriber" in normalized_backend
    assert "the hosted fedpro route now replays that post-delivery retraction fanout invariant too" in normalized_backend
    assert "a pre-restore timestamped delete consumed on one branch does not leak into the restored branch" in normalized_backend
    assert "a fresh post-restore timed remove is still routed correctly" in normalized_backend
    assert "the hosted fedpro route now replays that stale timed-remove restore invariant too" in normalized_backend
    assert "the pre-restore timed remove is cleared from queued and delivered retraction bookkeeping after restore" in normalized_backend
    assert "restore recovers locally deleted object-known-state" in normalized_backend
    assert "fresh post-restore reflections route again against that restored handle" in normalized_backend
    assert "the hosted fedpro route now replays that same local-delete restore invariant" in normalized_backend
    assert "a fresh post-restore `reflect` callback routes again on the restored handle" in normalized_backend
    assert "dirty post-save plain interaction callbacks do not replay after restore" in normalized_backend
    assert "fresh post-restore plain callbacks still route under the restored callback policy" in normalized_backend
    assert "the hosted fedpro route now replays that callback-policy restore invariant too" in normalized_backend
    assert "a fresh post-restore plain callback still routes once callback delivery is re-enabled" in normalized_backend
    assert "the hosted fedpro route now also proves reconnect-safe callback backlog hygiene" in normalized_backend
    assert "that stale backlog is discarded before a later reconnecting federate joins" in normalized_backend
    assert "logical time, lookahead, and galt/lits bounds recover correctly after restore" in normalized_backend
    assert "flush grants remain targeted to the federate that issued the flush request" in normalized_backend
    assert "the hosted fedpro route now replays that time-state restore surface too" in normalized_backend
    assert "the fedpro flush-queue restore path keeps grants targeted to the requesting federate" in normalized_backend
    assert "restore-control negative paths too" in normalized_backend
    assert "the hosted fedpro route now replays that restore-control negative surface too" in normalized_backend
    assert "transportation-type restore persistence too" in normalized_backend
    assert "transport/order metadata restoration is proven over the fedpro route, not just in-process" in normalized_backend
    assert "in-flight ownership negotiations resume from the saved state" in normalized_backend
    assert "the hosted fedpro route now replays that ownership restore surface too" in normalized_backend
    assert "cross-federate owner-visibility queries reflect the restored ownership graph" in normalized_backend
    assert "hosted fedpro gaps are mostly transport-seam proof gaps" in normalized_backend
    assert "`hla-backend-python2025` lacks the underlying runtime semantics" in normalized_backend
    assert "java/c++ gaps are binding/adaptation proof gaps" in normalized_backend

    assert "the main full 2025 python rti centered on `hla-backend-python2025`" in normalized_route_inventory
    assert "`hla-backend-python2025` is the main `rti1516_2025` implementation lane" in normalized_route_inventory
    assert "`hla-backend-shim` is only a compatibility-wrapper package over that lane" in normalized_route_inventory
    assert "`hla.backends.shim.runtime_aliases` as the explicit runtime-alias hatch" in normalized_route_inventory
    assert "the other `hla.backends.shim.*` helper modules are retained only as thin legacy forwarders into `hla.backends.python2025.*`" in normalized_route_inventory
    assert "java/c++ binding routes are route surfaces, not separate python rtis" in normalized_route_inventory
    assert "`python-2025-inprocess`: direct executable evidence over the main `hla-backend-python2025` rti lane" in normalized_route_inventory
    assert "`python-2025-fedpro-grpc`: bounded hosted route evidence over that same rti lane, not a separate 2025 runtime family" in normalized_route_inventory

    assert "| python rti 2025 |" in normalized_route_inventory_routes
    assert "main full `rti1516_2025` implementation lane in `hla-backend-python2025`" in normalized_route_inventory_routes
    assert "`test_rti1516_2025_python2025_runtime.py` is the main in-process `python2025` proof suite" in normalized_route_inventory_routes
    assert "`hla-backend-shim` remains compatibility-wrapper/import-level support rather than a separate rti" in normalized_route_inventory_routes
    assert "| python rti 2025 hosted |" in normalized_route_inventory_routes
    assert "`start_2025_grpc_server(...)`, `grpctransport(..., schema=\"rti1516_2025\")`, `create_rti_ambassador(\"python2025\", transport={\"kind\": \"grpc\", ...})`" in normalized_route_inventory_routes
    assert "`create_rti_ambassador(\"python2025\", transport={\"kind\": \"grpc\", ...})`" in normalized_route_inventory_routes
    assert "factory-level `create_rti_ambassador(\"python2025\", transport=...)` now resolves onto the main `python2025` lane" in normalized_route_inventory_routes
    assert "hosted fedpro route over the main full `hla-backend-python2025` runtime" in normalized_route_inventory_routes
    assert "bounded runtime slice, not a separate rti family" in normalized_route_inventory_routes

    assert "transport route over the main full `hla-backend-python2025` runtime lane" in normalized_route_inventory_remote
    assert "`hla-backend-shim` retained only as temporary import-compatibility scaffolding and compatibility-wrapper/import-level code" in normalized_route_inventory_remote
    assert "transport-seam proof over `hla-backend-python2025`" in normalized_route_inventory_remote
    assert "not ownership of separate core rti semantics" in normalized_route_inventory_remote

    assert "the bounded 2025 hosted fedpro grpc route over the repo's main full 2025 python rti lane" in normalized_networked
    assert "the current transport-hosted fedpro route over the main full `python2025` python rti lane" in normalized_networked
    assert "now exposes this hosted 2025 path through `create_rti_ambassador(\"python2025\", transport=...)`" in normalized_networked
    assert "they are transport-seam proof over that runtime, not evidence that the main 2025 python rti lane still lacks the underlying semantics" in normalized_networked
    assert "direct `python2025` time-window, save/restore, ownership, callback, support-service, and mom proof selectors" in normalized_networked

    assert "most shim helper modules are intentionally thin re-exports of `hla.backends.python2025.*` runtime modules" in normalized_migration
    assert "not part of the repo-owned implementation claim" in normalized_migration
    assert "the shim package should not regain ownership of core rti semantics" in normalized_migration
    assert "retained only for explicit legacy import compatibility coverage and temporary scaffolding" in normalized_migration
    assert "use `hla.backends.shim` only when you need the temporary import-compatibility scaffolding or legacy compatibility-wrapper imports" in normalized_migration

    assert "java and c++ standard-surface binding routes" in normalized_shim_routes
    assert "those routes execute over the primary `hla-backend-python2025` runtime lane" in normalized_shim_routes
    assert "not separate rtis" in normalized_shim_routes
    assert "`runtimeprovider = python2025`" in normalized_shim_routes
    assert "`implementationlane = hla-backend-python2025`" in normalized_shim_routes
    assert "`wrapperonly = false`" in normalized_shim_routes

    assert "current `hla-backend-python2025` runtime also carries an explicit target/radar lookahead proof ladder" in normalized_time_model
    assert "`time-window-core`" in normalized_time_model
    assert "`time-window-future-exclusion`" in normalized_time_model
    assert "`time-window-output-delivery`" in normalized_time_model
    assert "`time-window-consumer-order`" in normalized_time_model
    assert "`time-window-pipeline-two-scans`" in normalized_time_model
    assert "`time-window-receive-order-poison`" in normalized_time_model
    assert "`lookahead-processing-window-certified`" in normalized_time_model
    assert "the same proof ladder is replayed over the hosted `python-2025-fedpro-grpc` route" in normalized_time_model
    assert "matching negative-oracle tests reject premature closure, mismatched lits boundaries, premature output, reversed consumer order, cross-window contamination, closed-window mutation, and dirty post-restore replay" in normalized_time_model
    assert "[`../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md)" in normalized_time_model
    assert "direct in-process `python2025` time-management services plus the target/radar time-window proof ladder and negative-oracle guards" in normalized_time_model
    assert "`hla.backends.python2025.time_management_runtime`" in normalized_time_model
    assert "`hla.backends.python2025.federation_time_surface_mixin`" in normalized_time_model
    assert "`hla.backends.python2025.runtime_state`" in normalized_time_model
    assert "the current 2025 time claim is not just an abstract route claim" in normalized_time_model
    assert "anchored to the extracted `hla-backend-python2025` runtime modules" in normalized_time_model
    assert "for pitch specifically, the current trial-safe candidate is the two-federate `time-window-future-exclusion` route" in normalized_time_model
    assert "`./tools/pitch time-window-probe`" in normalized_time_model
    assert "`./tools/pitch time-window-restore-state-probe`" in normalized_time_model
    assert "use those only as narrow real-runtime probes for the two-federate closure and restore-state routes" in normalized_time_model
    assert "they do not turn pitch into the implementation owner for the 2025 lane" in normalized_time_model

    assert "`hla-backend-python2025` is the main full python-owned ieee 1516.1-2025 rti implementation package" in normalized_architecture
    assert "`hla-backend-shim` is only an import-level compatibility-wrapper package over that runtime" in normalized_architecture
    assert "java/c++ 2025 binding routes remain segregated non-python binding/capability lanes" in normalized_architecture
    assert "should not be counted as alternate python rtis" in normalized_architecture
    assert "implementation-owner proof for the main python 2025 lane" in normalized_architecture
    assert "`packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py`: main full python 2025 backend plugin and discovery surface." in normalized_architecture
    assert "`packages/hla-backend-shim/src/hla/backends/shim/plugin.py`: wrapper-only compatibility plugin for legacy shim imports around the 2025 lane." in normalized_architecture
    assert "for ieee 1516.1-2025 specifically, the main executable python rti lane is `hla-backend-python2025`" in normalized_architecture
    assert "`hla-backend-shim` remains only as compatibility-wrapper/import-level code" in normalized_architecture

    assert '`hla.rti1516_2025.create_rti_ambassador("python2025")`' in normalized_options_matrix
    assert "| python rti 2025 | in-process python rti implemented in python for ieee 1516.1-2025 | `python2025`, `python-2025`, `python-2025-backend` | main executable 2025 python rti lane in this repo |" in normalized_options_matrix
    assert "### python rti 2025" in normalized_options_matrix
    assert "| python rti 2025 | `python2025`, `python-2025`, `python-2025-backend` |" in normalized_options_matrix
    assert "| python rti 2025 | none | none | yes | yes | yes | yes | yes | no |" in normalized_options_matrix
    assert "### python rti 2025" in normalized_options_matrix
    assert "[test_rti1516_2025_python2025_runtime.py](../tests/test_rti1516_2025_python2025_runtime.py)" in normalized_options_matrix

    assert "this page is 2010-specific. for the current ieee 1516.1-2025 python rti lane, do not treat this file as the main conformance plan." in normalized_verification_plan
    assert "[`../python_rti_backend.md`](../python_rti_backend.md)" in normalized_verification_plan
    assert "[`../verification/time_model_compliance.md`](time_model_compliance.md)" in normalized_verification_plan
    assert "[`../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_verification_plan
    assert "[`../plans/2025_python_rti_backend_audit.md`](../plans/2025_python_rti_backend_audit.md)" in normalized_verification_plan
    assert "[`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)" in normalized_verification_plan
    assert "[`../plans/spec2025_route_parity_matrix.md`](../plans/spec2025_route_parity_matrix.md)" in normalized_verification_plan
    assert "explicit non-claim boundary around the bounded 2025 working-surface statement" in normalized_verification_plan
    assert "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_verification_plan
    assert "this page is 2010-specific. for the current ieee 1516.1-2025 python rti lane, do not treat this file as the main operational proof ledger." in normalized_validation_plan
    assert "[`../python_rti_backend.md`](../python_rti_backend.md)" in normalized_validation_plan
    assert "[`../verification/time_model_compliance.md`](time_model_compliance.md)" in normalized_validation_plan
    assert "[`../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_validation_plan
    assert "[`../plans/2025_python_rti_backend_audit.md`](../plans/2025_python_rti_backend_audit.md)" in normalized_validation_plan
    assert "[`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)" in normalized_validation_plan
    assert "explicit non-claim boundary around the bounded 2025 direct and hosted `python2025` validation story" in normalized_validation_plan
    assert "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_validation_plan
    assert "this page is primarily a 2010 hierarchy view. for the current ieee 1516.1-2025 python rti lane, do not treat it as the main clause/proof ledger." in normalized_requirements_hierarchy
    assert "[`../python_rti_backend.md`](../python_rti_backend.md)" in normalized_requirements_hierarchy
    assert "[`../requirements/ieee-1516-2025/readme.md`](../requirements/ieee-1516-2025/readme.md)" in normalized_requirements_hierarchy
    assert "[`../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_requirements_hierarchy
    assert "bounded direct/hosted `python2025` executable-behavior claim plus the explicit excluded-area map" in normalized_requirements_hierarchy
    assert "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_requirements_hierarchy

    assert "this page is 2010-specific. it is not the primary clause/proof ledger for the current ieee 1516.1-2025 python rti lane." in normalized_conformance_matrix
    assert "[python_rti_backend.md](python_rti_backend.md)" in normalized_conformance_matrix
    assert "[backend_route_inventory.md](backend_route_inventory.md)" in normalized_conformance_matrix
    assert "[verification/time_model_compliance.md](verification/time_model_compliance.md)" in normalized_conformance_matrix
    assert "[plans/2025_python_rti_backend_audit.md](plans/2025_python_rti_backend_audit.md)" in normalized_conformance_matrix
    assert "[plans/2025_requirements_finish_line.md](plans/2025_requirements_finish_line.md)" in normalized_conformance_matrix
    assert "[plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)" in normalized_conformance_matrix

    assert "| `python-main-2025` | `./tools/python verify-main-2025` | primary `python2025` main-surface proof lane for package-boundary guards, raw support/decode plus callback-control proofs on the direct runtime surface, explicit federation/object/ddm runtime proofs, explicit support/ownership/mom runtime proofs, the explicit target/radar time-window gauntlet and restore-window ladder, the explicit save/restore gauntlet and rollback ladder, broader direct runtime slices, and omt evidence |" in normalized_test_surface
    assert "| `python-routes-2025` | `./tools/python verify-routes-2025` | bounded `python2025` plus hosted fedpro 2025 route checks, explicit hosted federation/object/ddm runtime proofs, explicit hosted support/ownership/mom runtime proofs, explicit hosted target/radar time-window ladder replay, explicit hosted save/restore gauntlet and rollback replay, direct time-window, save/restore, ownership, callback, support-service, and mom proofs, the checked-in 2025 finish-line bundle, and the readme-advertised `python2025` target/radar example path |" in normalized_test_surface
    assert "| `matrix` | `./tools/test-surface run matrix` | regenerate compliance artifacts, refresh the checked-in 2025 finish-line bundle, and rerun matrix gates |" in normalized_test_surface
    assert "use `./tools/python verify-main-2025` as the normal main-implementation lane when you change:" in normalized_test_surface
    assert "it is the shortest operator path that combines the direct `python2025` runtime slices, the package/runtime boundary guardrails that keep `shim` wrapper-only, the requirement-facing bounded proof-note registry, and the dedicated omt evidence surface" in normalized_test_surface
    assert "support-service handle-factory and decode-helper behavior without routing through the compatibility wrapper" in normalized_test_surface
    assert "snake-case alias acceptance on the direct `python2025` runtime surface" in normalized_test_surface
    assert "`disablecallbacks`, `enablecallbacks`, `evokecallback`, and `evokemultiplecallbacks`" in normalized_test_surface
    assert "for the 2025 lane specifically, use `./tools/python verify-routes-2025` as the normal route-level hygiene lane for the main `python2025` rti plus the bounded `python-2025-fedpro-grpc` route" in normalized_test_surface
    assert "that lane covers the hosted 2025 transport suite, explicit in-process `python2025` time-window, save/restore, ownership, callback, support-service, and mom proof selectors" in normalized_test_surface
    assert "the checked-in 2025 route-parity ledger, the 2025 requirements-registry/bounded-proof-note surface, regeneration of the checked-in 2025 finish-line bundle (including the route-parity artifacts), and the readme-advertised `python2025` target/radar example path" in normalized_test_surface
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_test_surface
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_test_surface
    assert "[`requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_test_surface
    assert "[`plans/spec2025_route_parity_matrix.md`](plans/spec2025_route_parity_matrix.md)" in normalized_test_surface
    assert "operator-facing non-claim map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics around the main `python2025` lane" in normalized_test_surface

    assert "the pure python 2010 backend runs" in normalized_top_to_bottom_green
    assert "the main full python 2025 rti lane runs from `hla-backend-python2025`" in normalized_top_to_bottom_green
    assert "`hla-backend-shim` remains only a compatibility-wrapper/import-compatibility package" in normalized_top_to_bottom_green
    assert "python examples/target_radar_simulation.py --backend python2025 --steps 5" in normalized_top_to_bottom_green
    assert "for ieee 1516.1-2025 specifically, treat `python2025` as the main executable runtime lane" in normalized_top_to_bottom_green
    assert "do not treat `shim` as a separate rti family" in normalized_top_to_bottom_green
    assert "./tools/python verify-main-2025" in normalized_top_to_bottom_green
    assert "./tools/python verify-routes-2025" in normalized_top_to_bottom_green
    assert "use `verify-main-2025` as the default direct `python2025` proof lane" in normalized_top_to_bottom_green
    assert "use `verify-routes-2025` when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane" in normalized_top_to_bottom_green
    assert "the direct and hosted `python2025` route evidence remains aligned with the main 2025 python rti lane" in normalized_top_to_bottom_green
    assert "for the 2025 lane, that answer should be grounded in the audited `hla-backend-python2025` runtime plus its bounded hosted route evidence" in normalized_top_to_bottom_green

    assert "this page is centered on the generated 2010/vendor compliance packet" in normalized_compliance_discovery
    assert "it is not the main discovery surface for the current ieee 1516.1-2025 python rti closeout" in normalized_compliance_discovery
    assert "[python_rti_backend.md](python_rti_backend.md)" in normalized_compliance_discovery
    assert "[verification/time_model_compliance.md](verification/time_model_compliance.md)" in normalized_compliance_discovery
    assert "[requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_compliance_discovery
    assert "[plans/2025_python_rti_backend_audit.md](plans/2025_python_rti_backend_audit.md)" in normalized_compliance_discovery
    assert "[plans/spec2025_finish_line.md](plans/spec2025_finish_line.md)" in normalized_compliance_discovery
    assert "[plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)" in normalized_compliance_discovery
    assert "for 2025 readers, treat those context sources as bounded reference surfaces, not as the main proof ledger for `hla-backend-python2025`" in normalized_compliance_discovery
    assert "explicit non-claim boundary around the bounded `python2025` working-surface statement" in normalized_compliance_discovery
    assert "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_compliance_discovery

    assert "this page covers the shared python bootstrap contract for both editions" in normalized_python_environment
    assert "the main executable backend remains `hla-backend-python2025`, while `hla-backend-shim` stays only as compatibility-wrapper/import-compatibility code" in normalized_python_environment
    assert "[`python_rti_backend.md`](python_rti_backend.md) for the current runtime ownership and wrapper boundary" in normalized_python_environment
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest edit path through `hla-backend-python2025`" in normalized_python_environment
    assert "[`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted `python-2025-fedpro-grpc` route" in normalized_python_environment
    assert "`python2025` is the main in-process rti lane" in normalized_python_environment
    assert "`hla-backend-shim` stays only as compatibility-wrapper/import-compatibility code" in normalized_python_environment
    assert "the hosted grpc path is a bounded route variant, not a separate rti family" in normalized_python_environment
    assert "./tools/python verify-main-2025" in normalized_python_environment
    assert "treat `./tools/python verify-main-2025` as the normal main-surface proof lane for the real 2025 python rti" in normalized_python_environment
    assert "use `./tools/python verify-routes-2025` only when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane" in normalized_python_environment

    assert "for ieee 1516.1-2025 specifically, treat `hla-backend-python2025` as the main runtime lane after bootstrap" in normalized_install_matrix
    assert "`hla-backend-shim` remains only as a compatibility-wrapper/import-compatibility package" in normalized_install_matrix
    assert "the hosted fedpro route remains a bounded route variant rather than a separate rti family" in normalized_install_matrix
    assert "for the primary 2025 python rti lane, read [`python_rti_backend.md`](python_rti_backend.md) after bootstrap" in normalized_install_matrix
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_install_matrix
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_install_matrix

    assert "for ieee 1516.1-2025 work, also keep this boundary explicit:" in normalized_agent_runbook
    assert "`hla-backend-python2025` is the main executable 2025 rti lane" in normalized_agent_runbook
    assert "`hla-backend-shim` is only a compatibility-wrapper/import-compatibility package over that runtime" in normalized_agent_runbook
    assert "hosted 2025 fedpro work is a bounded route variant, not a separate rti family" in normalized_agent_runbook
    assert "`packages/hla-backend-python2025/src/hla/backends/python2025/` owns the main full ieee 1516.1-2025 python rti runtime" in normalized_agent_runbook
    assert "`packages/hla-backend-shim/src/hla/backends/shim/` is a wrapper-only compatibility surface over that runtime" in normalized_agent_runbook
    assert "for 2025 runtime work after base bootstrap, send the reader to:" in normalized_agent_runbook
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_agent_runbook
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_agent_runbook
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_agent_runbook
    assert "for 2025-specific runtime ownership and proof status, point them instead to:" in normalized_agent_runbook

    assert "for the primary 2025 python rti lane, interpret these commands through the audited `hla-backend-python2025` runtime" in normalized_local_verification_commands
    assert "`hla-backend-shim` is only temporary import-compatibility scaffolding plus compatibility-wrapper/import-compatibility code" in normalized_local_verification_commands
    assert "the hosted 2025 grpc route is a bounded route variant rather than a separate rti family" in normalized_local_verification_commands
    assert "./tools/python verify-main-2025" in normalized_local_verification_commands
    assert "is the regular main-surface lane for the current `python2025` backend claim" in normalized_local_verification_commands
    assert "it runs the direct in-process runtime proof selectors, the package/runtime boundary guardrails that keep `shim` compatibility-only, the 2025 requirements-registry and bounded proof-note surface, plus the dedicated omt validation/parsing evidence surface" in normalized_local_verification_commands
    assert "the explicit raw `python2025` proofs for support-service handle-factory/decode behavior, snake-case direct-surface aliases, and callback-control services on `hla-backend-python2025` itself" in normalized_local_verification_commands
    assert "it also names the target/radar time-window ladder explicitly" in normalized_local_verification_commands
    assert "integrated lookahead-processing-window gauntlet" in normalized_local_verification_commands
    assert "restore-state / restore-output / pipeline-restore legs" in normalized_local_verification_commands
    assert "it now also names the save/restore proof family explicitly" in normalized_local_verification_commands
    assert "example-fom save/restore gauntlet" in normalized_local_verification_commands
    assert "dirty-lookahead rollback with pre-save queued-tso redelivery path" in normalized_local_verification_commands
    assert "it now also names the service-heavy proof family explicitly" in normalized_local_verification_commands
    assert "callback-control over live object reflection" in normalized_local_verification_commands
    assert "direct mom report/control/action routing on the `python2025` surface" in normalized_local_verification_commands
    assert "it now also names the federation/object/ddm proof family explicitly" in normalized_local_verification_commands
    assert "object-and-interaction exchange" in normalized_local_verification_commands
    assert "region/ddm lifecycle and declaration gating" in normalized_local_verification_commands
    assert "./tools/python verify-routes-2025" in normalized_local_verification_commands
    assert "the in-process target/radar time-window proof ladder" in normalized_local_verification_commands
    assert "direct `python2025` save/restore, ownership, callback, support-service, or mom proofs" in normalized_local_verification_commands
    assert "the 2025 requirements-registry and bounded proof-note surface" in normalized_local_verification_commands
    assert "it also names the hosted target/radar time-window family explicitly" in normalized_local_verification_commands
    assert "factory-hosted and shared fedpro target/radar example, future-exclusion, output-delivery, consumer-order, integrated-gauntlet, receive-order-poison, restore-output, and pipeline-restore scenario routes" in normalized_local_verification_commands
    assert "it now also names the hosted save/restore family explicitly" in normalized_local_verification_commands
    assert "shared fedpro save/restore route, queued-callback and scheduled time-state restore routes" in normalized_local_verification_commands
    assert "example-fom and smoke ownership gauntlets" in normalized_local_verification_commands
    assert "it now also names the hosted service-heavy family explicitly" in normalized_local_verification_commands
    assert "fedpro support-service and switch round trips" in normalized_local_verification_commands
    assert "hosted mom manager/service/control/exception routing" in normalized_local_verification_commands
    assert "it now also names the hosted federation/object/ddm family explicitly" in normalized_local_verification_commands
    assert "shared fedpro lifecycle/listing routes" in normalized_local_verification_commands
    assert "hosted object-scope relevance, and hosted directed-routing checks" in normalized_local_verification_commands
    assert "for 2025 runtime ownership and proof status behind those commands, use:" in normalized_local_verification_commands
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_local_verification_commands
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_local_verification_commands
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_local_verification_commands

    assert "this page is scenario-first, not edition-neutral architecture guidance" in normalized_two_federate
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_two_federate
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_two_federate
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_two_federate
    assert "the scenario may run over the main full `python2025` lane or bounded hosted route variants" in normalized_two_federate
    assert "`hla-backend-python2025` remains the main runtime" in normalized_two_federate
    assert "`shim` does not count as a separate rti family" in normalized_two_federate

    assert "for the current 2025 python rti closeout path, the most important reference surfaces are:" in normalized_documentation_hierarchy
    assert "[docs/python_rti_backend.md](python_rti_backend.md)" in normalized_documentation_hierarchy
    assert "[docs/python_rti_reading_map.md](python_rti_reading_map.md)" in normalized_documentation_hierarchy
    assert "`./tools/python verify-main-2025`: normal direct `python2025` proof lane for the main implementation surface" in normalized_documentation_hierarchy
    assert "[docs/verification/time_model_compliance.md](verification/time_model_compliance.md)" in normalized_documentation_hierarchy
    assert "[docs/requirements/ieee-1516-2025/readme.md](requirements/ieee-1516-2025/readme.md)" in normalized_documentation_hierarchy
    assert "[docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_documentation_hierarchy
    assert "`./tools/python verify-routes-2025`: bounded hosted `python-2025-fedpro-grpc` hygiene lane over that same runtime" in normalized_documentation_hierarchy
    assert "[docs/plans/spec2025_finish_line.md](plans/spec2025_finish_line.md)" in normalized_documentation_hierarchy
    assert "[docs/plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)" in normalized_documentation_hierarchy
    assert "- python rti 2010" in normalized_documentation_hierarchy
    assert "- python rti 2025" in normalized_documentation_hierarchy
    assert "`backend_conformance_matrix.md` and `verification/verification_plan.md` are 2010-specific reference surfaces" in normalized_documentation_hierarchy
    assert "the current `python2025` rti evidence path runs through the 2025 finish-line, route-parity, backend-audit, and time-model documents listed above" in normalized_documentation_hierarchy
    assert "explicit excluded-area map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_documentation_hierarchy

    assert "./tools/python verify-routes-2025" in normalized_vendor_runtime_runner_guide
    assert "hosted-route meaning in this guide:" in normalized_vendor_runtime_runner_guide
    assert "`./tools/python verify-routes` is the hosted 2010 python direct-vs-grpc lane" in normalized_vendor_runtime_runner_guide
    assert "`./tools/python verify-routes-2025` is the bounded hosted `python2025` plus `python-2025-fedpro-grpc` lane" in normalized_vendor_runtime_runner_guide
    assert "only the second one is the current ieee 1516.1-2025 hosted-route hygiene lane" in normalized_vendor_runtime_runner_guide
    assert "python3 -m pytest -q tests/transport/test_grpc_transport_2025.py" in normalized_vendor_runtime_runner_guide

    assert "./tools/python verify-routes-2025" in normalized_codex_runner_authorization
    assert "route split:" in normalized_codex_runner_authorization
    assert "`./tools/python verify-routes` is the older 2010 hosted python parity lane" in normalized_codex_runner_authorization
    assert "`./tools/python verify-routes-2025` is the bounded hosted ieee 1516.1-2025 lane over the main `hla-backend-python2025` runtime" in normalized_codex_runner_authorization
    assert "python3 -m pytest -q tests/transport/test_grpc_transport_2025.py" in normalized_codex_runner_authorization
    assert "the bounded `python-2025-fedpro-grpc` route passes the same hosted-route identity and parity assertions as the direct `python2025` lane" in normalized_codex_runner_authorization

    assert "bounded working-surface evidence for the current `hla-backend-python2025` 2025 lane" in normalized_capability
    assert "`hla-backend-shim` remains only as compatibility-wrapper/import-level code" in normalized_capability
    assert "| `python2025` | yes | yes | yes | yes | no |" in capability_doc
    assert "| `python-2025-fedpro-grpc` | yes | yes | yes | yes | no |" in capability_doc
    assert "transport-hosted pure-python 2010 rti server, and through the bounded `python-2025-fedpro-grpc` route over `hla-backend-python2025`" in normalized_capability
    assert "the current 2025 hosted proof treated as transport-seam evidence over `hla-backend-python2025` rather than as a separate runtime family" in normalized_capability
    assert "`python2025` is a first-class operator-facing runtime family in this repo" in normalized_capability
    assert "`hla-backend-shim` remains only as compatibility-wrapper/import-level code around `python2025`" in normalized_capability
    assert "`python-2025-fedpro-grpc` is the bounded hosted route over the same `hla-backend-python2025` runtime lane" in normalized_capability
    assert "[test_rti1516_2025_python2025_runtime.py](../tests/test_rti1516_2025_python2025_runtime.py)" in capability_doc
    assert "[test_2025_route_parity_matrix.py](../tests/requirements/test_2025_route_parity_matrix.py)" in capability_doc
    assert "[test_2025_finish_line_snapshot.py](../tests/requirements/test_2025_finish_line_snapshot.py)" in capability_doc
    assert "[test_grpc_transport_2025.py](../tests/transport/test_grpc_transport_2025.py)" in capability_doc

    assert "./tools/python verify-routes-2025" in normalized_route_inventory_commands
    assert "for ieee 1516.1-2025 specifically, `./tools/python verify-routes-2025` is the normal route-level hygiene lane for the direct `python2025` runtime plus the bounded hosted `python-2025-fedpro-grpc` route over `hla-backend-python2025`." in normalized_route_inventory_commands

    assert "`packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py`" in normalized_factory_map
    assert "`python2025` is the main full executable backend lane for `rti1516_2025`" in normalized_factory_map
    assert "`hla.backends.shim` is import-level compatibility code over that runtime rather than the implementation owner" in normalized_factory_map
    assert "`tests/test_rti1516_2025_python2025_runtime.py` (main in-process `python2025` proof suite)" in normalized_factory_map
    assert "proof first and only then inspect the wrapper alias" in normalized_factory_map
    assert "should expect to land on the `hla-backend-python2025` lane by default" in normalized_factory_map
    assert "the main `python2025` factory path now does accept hosted 2025 creation through `transport=...`" in normalized_factory_map
    assert "the legacy shim provider spelling is no longer part of the supported public factory surface" in normalized_factory_map
    assert "create_rti_ambassador(backend=\"python2025\", transport=...)" in normalized_factory_map
    assert "`./tools/python verify-main-2025` is the normal proof command for that direct factory-selection path" in normalized_factory_map
    assert "`./tools/python verify-routes-2025` is the follow-on lane when hosted factory transport ownership must stay green" in normalized_factory_map

    assert "[../packages/hla-backend-python2025/readme.md]" in normalized_python_rti_map
    assert "`hla-backend-python2025` is the main full 2025 python rti implementation lane" in normalized_python_rti_map
    assert "`hla-backend-shim` is a wrapper-only compatibility alias over that runtime" in normalized_python_rti_map
    assert "[requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized_python_rti_map
    assert "architecture to the current 2025 runtime proof and its explicit non-claim boundary with minimal detours" in normalized_python_rti_map
    assert "item 8 is the main in-process executable proof suite" in normalized_python_rti_map
    assert "item 8 is the main in-process executable proof suite for `hla-backend-python2025`" in normalized_python_rti_map
    assert "main in-process `python2025` runtime suite" in normalized_python_rti_map
    assert "`tests/test_rti1516_2025_python2025_runtime.py` (main `python2025` proof suite)" in normalized_python_rti_map
    assert "use the shim readme only when you are checking legacy provider spelling" in normalized_python_rti_map
    assert "`./tools/python verify-main-2025` for the normal direct `python2025` main-surface proof lane" in normalized_python_rti_map
    assert "`./tools/python verify-routes-2025` when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane" in normalized_python_rti_map
    assert "`verification/time_model_compliance.md` and `tests/test_rti1516_2025_python2025_runtime.py` as the main proof front doors" in normalized_python_rti_map
    assert "explicit excluded-area map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_python_rti_map
    assert "start in [../packages/hla-backend-python2025/src/hla/backends/python2025/backend.py]" in normalized_python_rti_map
    assert "wrapper-only compatibility behavior" in normalized_python_rti_map
    assert "run `./tools/python verify-main-2025` as the default proof command after changes in that path" in normalized_python_rti_map
    assert "run `./tools/python verify-routes-2025` when the change must stay aligned with the bounded hosted `python-2025-fedpro-grpc` route" in normalized_python_rti_map
    assert "`docs/requirements/ieee-1516-2025/python2025_direct_bounded_proof.md`" in normalized_backend
    assert "`docs/requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md`" in normalized_backend
    assert "`docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md`" in normalized_backend
    assert "`docs/requirements/ieee-1516-2025/callback_bounded_proof.md`" in normalized_backend
    assert "`docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`" in normalized_backend
    assert "main executable bounded proof surface for the current 2025 python rti" in normalized_backend
    assert "`docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`" in normalized_backend
    assert "explicit non-claim map around that bounded working-surface statement" in normalized_backend
    assert "captures exactly which repo-owned proto2025 and target/radar example/fom-backed scenarios are part of the bounded claim" in normalized_backend
    assert "captures the current rollback-family contract for lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time state rollback" in normalized_backend
    assert "captures the current callback-family contract for declaration advisories, object delivery, ownership callbacks, time/retraction callbacks, and callback-control hygiene" in normalized_backend
    assert "captures the explicit target/radar closure, future-exclusion, output-delivery, consumer-order, pipeline, negative-oracle, and bounded restore-window ladder" in normalized_backend

    assert "read [`first_run.md`](first_run.md) for the 2010 pure-python bootstrap lane" in normalized_docs_index
    assert "read [`python_rti_backend.md`](python_rti_backend.md) for the main 2025 python rti lane in `hla-backend-python2025`" in normalized_docs_index
    assert "use `./tools/python verify-main-2025` as the normal direct `python2025` proof lane" in normalized_docs_index
    assert "read [`networked_rti_python.md`](networked_rti_python.md) only if you need the bounded hosted 2025 route or its parity/hygiene lane" in normalized_docs_index
    assert "use `./tools/python verify-routes-2025` when you need the bounded hosted `python-2025-fedpro-grpc` hygiene lane" in normalized_docs_index
    assert "read [`verification/time_model_compliance.md`](verification/time_model_compliance.md) when the question is time, lookahead, galt/lits, or save/restore window proof" in normalized_docs_index
    assert "[python_rti_backend.md](python_rti_backend.md): main 2025 python rti lane, wrapper boundary, and bounded working-surface claim" in normalized_docs_index
    assert "[python_rti_reading_map.md](python_rti_reading_map.md): shortest editing path for the main `python2025` rti lane" in normalized_docs_index
    assert "[../tools/python](../tools/python): operator entrypoint for `verify-main-2025` and `verify-routes-2025`" in normalized_docs_index
    assert "[verification/time_model_compliance.md](verification/time_model_compliance.md): time-management, lookahead, galt/lits, and radar-window proof front door for the primary 2025 python rti lane" in normalized_docs_index
    assert "[../tools/pitch](../tools/pitch): narrow vendor-runtime operator path when you need the pitch-safe two-federate `time-window-probe` or `time-window-restore-state-probe` bounded credence routes without widening the main `python2025` claim" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/readme.md](requirements/ieee-1516-2025/readme.md): 2025 requirements index, bounded proof notes, and requirement-facing evidence map for the main `python2025` lane" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md](requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md): tracked proto2025 and target/radar example/fom-backed scenario boundary for the bounded `python2025` claim" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/save_restore_bounded_proof.md](requirements/ieee-1516-2025/save_restore_bounded_proof.md): explicit save/restore rollback-family boundary for lifecycle control, routing/policy rollback, ownership rollback, and time-window rollback on the bounded `python2025` claim" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/callback_bounded_proof.md](requirements/ieee-1516-2025/callback_bounded_proof.md): explicit callback-delivery family boundary for direct/hosted `python2025` callback proofs, callback-control hygiene, and callback surface limits on the bounded `python2025` claim" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/lookahead_window_bounded_proof.md](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md): explicit target/radar lookahead-window proof ladder, negative-oracle guards, and pitch-safe vendor-credence boundary for the bounded `python2025` claim" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/python2025_direct_bounded_proof.md](requirements/ieee-1516-2025/python2025_direct_bounded_proof.md)" in normalized_docs_index
    assert "[requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md): explicit non-claim map for shim aliases, java/c++ bindings, hosted-route boundaries, umbrella rows, retired rows, and omt extension semantics around the main `python2025` lane" in normalized_docs_index
    assert "java/c++ standard-surface binding routes and evidence contract" in normalized_docs_index
    assert "the main requirement-backed semantics now live across package-owned modules such as:" in normalized_requirements_index
    assert "`backend_factory_runtime.py`" in requirements_index_doc
    assert "`runtime_state.py`" in requirements_index_doc
    assert "`federation_management_runtime.py`" in requirements_index_doc
    assert "`time_management_runtime.py`" in requirements_index_doc
    assert "`support_services_runtime.py`" in requirements_index_doc
    assert "`*_surface_mixin.py`" in requirements_index_doc
    assert "that is the implementation lane this requirement index is describing" in normalized_requirements_index

    assert "this page is the 2010 pure-python bootstrap path" in normalized_first_run
    assert "it is not the main entry point for the ieee 1516.1-2025 runtime lane" in normalized_first_run
    assert "the pure-python 2010 backend" in normalized_first_run
    assert "[`python_rti_backend.md`](python_rti_backend.md) for the main `hla-backend-python2025` runtime lane" in normalized_first_run
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest edit path through that runtime" in normalized_first_run
    assert "[`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted `python-2025-fedpro-grpc` route" in normalized_first_run
    assert "`python2025` is the main ieee 1516.1-2025 rti lane" in normalized_first_run
    assert "`hla-backend-shim` is only a compatibility-wrapper/import-compatibility package over that runtime" in normalized_first_run
    assert "`hla-backend-python2025` as the main 2025 runtime behind those tests" in normalized_tests_readme
    assert "`hla-backend-shim` only as a compatibility-wrapper/import-compatibility package" in normalized_tests_readme
    assert "for the 2025 lane specifically, the first architecture/proof surfaces to read after bootstrap are:" in normalized_tests_readme
    assert "docs/python_rti_backend.md" in normalized_tests_readme
    assert "docs/python_rti_reading_map.md" in normalized_tests_readme
    assert "docs/verification/time_model_compliance.md" in normalized_tests_readme
    assert "`./tools/python verify-main-2025` for the normal direct `python2025` main-surface proof lane" in normalized_tests_readme
    assert "`./tools/python verify-routes-2025` when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane" in normalized_tests_readme
    assert "`tests/requirements/`: 2025 finish-line, route-parity, backend-audit, and wording-boundary checks for the main `python2025` rti lane." in normalized_tests_readme

    assert "for ieee 1516.1-2025 specifically, interpret the operator surface through `hla-backend-python2025` as the main runtime lane" in normalized_tools_readme
    assert "`hla-backend-shim` remains only as compatibility-wrapper/import-compatibility code" in normalized_tools_readme
    assert "hosted fedpro routes are bounded route variants rather than separate rti families" in normalized_tools_readme
    assert "./tools/examples" not in normalized_tools_readme
    assert "./tools/human-editability" not in normalized_tools_readme
    assert "./tools/new-fom-package" not in normalized_tools_readme
    assert "./tools/rti-factories" not in normalized_tools_readme
    assert "python examples/target_radar_simulation.py --backend python --steps 5" in normalized_tools_readme
    assert "python examples/target_radar_simulation.py --backend python2025 --steps 5" in normalized_tools_readme
    assert "./tools/python verify-main-2025" in normalized_tools_readme
    assert "including package-boundary guards plus raw support/decode and callback-control proofs on the direct `python2025` surface" in normalized_tools_readme
    assert "./tools/python verify-routes-2025" in normalized_tools_readme
    assert "python3 scripts/run_spec2025_finish_line.py" in normalized_tools_readme
    assert "regenerate the checked-in 2025 finish-line and route-parity evidence bundle after proof-lane changes" in normalized_tools_readme
    assert "for 2025 runtime ownership and proof status behind those commands, read:" in normalized_tools_readme
    assert "docs/python_rti_backend.md" in normalized_tools_readme
    assert "docs/python_rti_reading_map.md" in normalized_tools_readme
    assert "docs/verification/time_model_compliance.md" in normalized_tools_readme

    assert "for ieee 1516.1-2025 specifically, the runtime owner behind the supported operator flows is `hla-backend-python2025`" in normalized_scripts_readme
    assert "`hla-backend-shim` remains wrapper-only compatibility code" in normalized_scripts_readme
    assert "hosted 2025 fedpro routes remain bounded route variants rather than separate rti families" in normalized_scripts_readme
    assert "when a script or wrapper touches the 2025 runtime lane, interpret that work through these surfaces first:" in normalized_scripts_readme
    assert "`run_spec2025_finish_line.py`: checked-in ieee 1516.1-2025 finish-line, verification-matrix, and route-parity artifact refresh" in normalized_scripts_readme
    assert "[../docs/python_rti_backend.md](../docs/python_rti_backend.md)" in normalized_scripts_readme
    assert "[../docs/python_rti_reading_map.md](../docs/python_rti_reading_map.md)" in normalized_scripts_readme
    assert "[../docs/verification/time_model_compliance.md](../docs/verification/time_model_compliance.md)" in normalized_scripts_readme

    assert "`hla.backends.python2025` for the main python rti backend for ieee 1516.1-2025" in normalized_root_readme
    assert "`hla-backend-python2025` is the main full executable python rti implementation lane" in normalized_root_readme
    assert "`hla-backend-shim` is a compatibility-wrapper package over that runtime, not a separate rti family" in normalized_root_readme
    assert "java and c++ 2025 binding routes are supporting route surfaces over the python 2025 lane, not alternate python rtis" in normalized_root_readme
    assert "python examples/target_radar_simulation.py --backend python2025 --steps 5" in normalized_root_readme
    assert "`hla-backend-shim` remains only as compatibility-wrapper/import-compatibility code around that runtime" in normalized_root_readme
    assert "./tools/python verify-main-2025" in normalized_root_readme
    assert "./tools/python verify-routes-2025" in normalized_root_readme
    assert "use `verify-main-2025` as the default direct `python2025` proof lane" in normalized_root_readme
    assert "use `verify-routes-2025` when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane over `hla-backend-python2025`" in normalized_root_readme
    assert "`python2025`, `python-2025`, `python-2025-backend`" in normalized_root_readme
    assert "`python2025` is the main python rti implementation lane for ieee 1516.1-2025" in normalized_root_readme
    assert "`hla.backends.shim` is compatibility-wrapper/import-compatibility code over `python2025`" in normalized_root_readme

    assert "`packages/hla-rti1516-2025/src/hla/rti1516_2025/`: strict ieee 1516.1-2025 api surface" in normalized_package_layout
    assert "`packages/hla-backend-python2025/src/hla/backends/python2025/`: main python rti backend for ieee 1516.1-2025" in normalized_package_layout
    assert "`packages/hla-backend-shim/src/hla/backends/shim/`: wrapper-only compatibility alias over the main 2025 backend lane" in normalized_package_layout
    assert "`packages/hla-backend-python2025/src/hla/backends/python2025/`: main full python-owned ieee 1516.1-2025 rti implementation package" in normalized_package_layout
    assert "`packages/hla-backend-shim/src/hla/backends/shim/`: maintained compatibility-wrapper package that delegates runtime semantics to `hla-backend-python2025`" in normalized_package_layout
    assert "`hla-rti1516-2025`: strict ieee 1516.1-2025 spec surface, value types, fom helpers, and 2025-local factory surface" in normalized_package_layout
    assert "`hla-backend-python2025`: main full executable python rti backend for ieee 1516.1-2025" in normalized_package_layout
    assert "`hla-backend-shim`: wrapper-only compatibility alias over `hla-backend-python2025`" in normalized_package_layout
    assert "`hla-backend-python2025` | backend | `hla-rti1516-2025`, `hla-backend-common`, `hla-rti-core` | shim backflow, vendor, transport, leaf packages |" in normalized_package_layout
    assert "`hla-backend-shim` | compatibility-wrapper | `hla-rti1516-2025`, `hla-rti-core`, `hla-backend-python2025` | any path that would re-own core 2025 runtime semantics, plus vendor, transport, leaf packages |" in normalized_package_layout
    assert "`hla-fom-target-radar` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-rti-core` | concrete backend, vendor, transport packages |" in normalized_package_layout

    assert "`packages/hla-rti1516-2025/src/hla/rti1516_2025/`: ieee 1516.1-2025 api scaffold." in normalized_workspace_layout
    assert "keep the main full ieee 1516.1-2025 runtime semantics under `hla.backends.python2025`" in normalized_workspace_layout
    assert "keep `hla.backends.shim` narrow and wrapper-only; it should not re-own the 2025 runtime" in normalized_workspace_layout

    assert "`hla-backend-python2025` is the sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_dependency_tree
    assert "`hla-backend-shim` is temporary import-compatibility scaffolding plus a legacy compatibility wrapper that depends on it rather than a peer rti lane or part of the implementation claim" in normalized_dependency_tree
    assert "`hla-transport-grpc` already carries the bounded 2025 fedpro transport/client/server surface" in normalized_dependency_tree
    assert "| `hla-fom-target-radar` | `hla-rti1516e, hla-rti1516-2025, hla-rti-core` | `-` |" in normalized_dependency_tree
    assert "the operator-facing hosted 2025 lane is `python2025`" in normalized_route_inventory_remote
    assert "do not describe legacy wrapper aliases as the hosted runtime owner" in normalized_route_inventory_remote
    assert "use `python2025` when naming the hosted 2025 route" in normalized_networked
    assert "treat `hla.backends.shim` as compatibility-wrapper code, not as the hosted runtime lane" in normalized_networked
    assert "the maintained 2025 transport-hosted lane is named and evidenced as `python2025`" in normalized_backend

    assert "the bounded hosted 2025 fedpro route is a route variant over `hla-backend-python2025`, not a separate python rti family" in normalized_packages
    assert "java and c++ 2025 binding lanes are supporting adaptation surfaces; they do not count as alternate python 2025 rtis" in normalized_packages

    assert "hla-rti1516-2025 └── hla-rti-core" in normalized_hierarchy
    assert "hla-backend-python2025" in normalized_hierarchy
    assert "hla-backend-shim (deprecated compatibility scaffolding over hla-backend-python2025)" in normalized_hierarchy
    assert "hla-fom-target-radar" in normalized_hierarchy
    assert "hla-transport-grpc (bounded fedpro 2025 hosted route)" in normalized_hierarchy
    assert "layer 1: `hla-backend-common`, `hla-fom-target-radar`, `hla-rti1516-2025`" in normalized_hierarchy
    assert "layer 2: `hla-backend-inmemory`, `hla-backend-python2025`, `hla-bridge-java-common`, `hla-transport-common`" in normalized_hierarchy

    assert "main full python rti backend package for ieee 1516.1-2025" in normalized_python2025_readme
    assert "this package now owns the main full python 2025 rti runtime" in normalized_python2025_readme
    assert "sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_python2025_readme
    assert "public `hla.backends.python2025.backend` shell now fronts a split package layout" in normalized_python2025_readme
    assert "`backend_factory_runtime.py`" in python2025_readme
    assert "`runtime_state.py`" in python2025_readme
    assert "`federation_management_runtime.py`" in python2025_readme
    assert "`time_management_runtime.py`" in python2025_readme
    assert "`*_surface_mixin.py`" in python2025_readme
    assert "`hla-backend-shim` package is deprecated compatibility scaffolding for older route and provider names that should be removed after migration" in normalized_python2025_readme
    assert "must not delegate back to `hla.backends.shim.backend.create_shim_backend`" in normalized_python2025_readme
    assert "not part of the repo-owned 2025 python rti implementation claim" in normalized_shim_readme
    assert "the architectural split that matters is already in place: `hla-backend-python2025` is the real 2025 rti runtime owner and the sole repo-owned 2025 python rti lane" in normalized_shim_readme
    assert "kept only as temporary, test-backed import-compatibility scaffolding" in normalized_shim_readme
    assert "they should be removed once no callers depend on the legacy import paths" in normalized_shim_readme
    assert "the other `hla.backends.shim.*` modules outside the package root: they are forwarders, not implementation owners" in normalized_shim_readme
    assert "future work here is boundary cleanup and removal, not deciding whether a dedicated python 2025 backend should exist" in normalized_shim_readme
    assert 'description = "main full python rti backend package for hla 1516.1-2025"' in normalized_python2025_pyproject
    assert 'backend_names = ["python2025"]' in normalized_python2025_pyproject
    assert 'backend_aliases = ["python-2025", "python-2025-backend"]' in normalized_python2025_pyproject
    assert 'role = "rti-backend"' in normalized_python2025_pyproject
    assert 'status = "implementation-owned"' in normalized_python2025_pyproject

    assert "legacy-named `hla-backend-shim` package is deprecated temporary import-compatibility scaffolding and a compatibility wrapper over the main full python 2025 rti lane" in normalized_shim_docs_readme
    assert "not part of the repo-owned 2025 python rti implementation claim" in normalized_shim_docs_readme
    assert "the executable runtime now lives in `hla-backend-python2025`, which is the sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_shim_docs_readme
    assert "only the `shim2025*` names represent the wrapper-only lane" in normalized_shim_docs_readme
    assert "test-backed legacy compatibility surface" in normalized_shim_docs_readme
    assert "deprecated and should be removed after migration" in normalized_shim_docs_readme
    assert "the real python 2025 rti backend already lives in `hla-backend-python2025`; this package is the wrapper-only compatibility lane" in normalized_shim_docs_readme
    assert "the other `hla.backends.shim.*` helper modules are intentionally thin forwarders into `hla.backends.python2025.*`" in normalized_shim_docs_readme
    assert "future work is about keeping that wrapper narrow, not about deciding whether a dedicated 2025 backend should exist, and the package should be removed after migration" in normalized_shim_docs_readme
    assert "later be split into a narrower shim plus a dedicated 2025 backend" not in normalized_shim_docs_readme
    assert "future dedicated 2025 rti backend becomes the better design" not in normalized_backend
    assert "the dedicated runtime already exists" in normalized_backend
    assert "the remaining architectural question is how narrow the compatibility wrapper should be" in normalized_backend
    assert "in repo terms, `python2025` is the rti lane. `shim` is not." in normalized_backend
    assert "## routine proof commands" in normalized_backend
    assert "`./tools/python verify-main-2025` for the direct main-surface `python2025` proof lane over `hla-backend-python2025`" in normalized_backend
    assert "`./tools/python verify-routes-2025` when you also need the bounded hosted `python-2025-fedpro-grpc` hygiene lane over that same runtime" in normalized_backend
    assert "treat `verify-main-2025` as the default 2025 proof path" in normalized_backend
    assert "reach for `verify-routes-2025` when the change touches hosted transport behavior, route-parity alignment, or the shared direct-plus-hosted target/radar proof surfaces" in normalized_backend
    assert "those two commands now name the current proof families explicitly instead of leaving them buried inside broad keyword slices" in normalized_backend
    assert "package-boundary and runtime-identity guards that keep `python2025` as the owned rti lane and `shim` as wrapper-only" in normalized_backend
    assert "federation, object, and ddm runtime proofs across lifecycle, listing, exchange, region gating, scope relevance, and directed routing" in normalized_backend
    assert "support-service, callback-control, ownership, and mom runtime proofs" in normalized_backend
    assert "target/radar time-window and lookahead proofs, including future-exclusion, output ordering, pipeline, and restore-window ladders" in normalized_backend
    assert "save/restore lifecycle, rollback, replay-guard, and gauntlet proofs" in normalized_backend
    assert "omt validation/parsing evidence" in normalized_backend
    assert "the operator-facing 2025 proof contract is now organized around those families" in normalized_backend
    assert "promotion and boundary discipline" in normalized_backend
    assert "narrow or extract more later if" in normalized_backend
    assert "not to create the real backend from scratch; that part is already done in `hla-backend-python2025`" in normalized_backend
    assert "stop using shim language for the primary 2025 runtime lane" in normalized_backend
    assert "`tests/test_rti1516_2025_python2025_runtime.py` (main in-process python2025 proof suite)" in normalized_backend
    assert "this is the main executable in-process proof suite for `hla-backend-python2025`" in normalized_backend
    assert "`examples/target_radar_simulation.py`" in normalized_backend
    assert "`tests/scenarios/test_target_radar_scenario.py`" in normalized_backend
    assert "`tests/test_fom_target_radar_split_package.py`" in normalized_backend
    assert "target/radar example route as a package-owned shared scenario path" in normalized_backend
    assert "now runs through `hla.foms.target_radar._internal.targetradar2025rtiadapter`" in normalized_backend
    assert "owned by `hla-fom-target-radar` and wraps both `python2025` and the wrapper-only `shim` alias" in normalized_backend
    assert "the same package-owned adapter now also runs the shared target/radar example path plus the shared future-exclusion time-window proof and restore-state save/restore proof over the factory-hosted `create_rti_ambassador(\"python2025\", transport=...)` fedpro route" in normalized_backend
    assert "the factory-hosted `create_rti_ambassador(\"python2025\", transport=...)` route now also proves direct mom federation-management save/restore service interactions" in normalized_backend
    assert "the hosted fedpro 2025 ambassador now accepts camelcase 2025 api entrypoints as aliases over its snake_case transport implementation methods" in normalized_backend
    assert "that same factory-hosted route now also proves a direct support-service slice on the hosted 2025 ambassador surface" in normalized_backend
    assert "raw `python2025` support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in normalized_backend
    assert "snake-case alias acceptance on the primary direct `python2025` runtime surface" in normalized_backend
    assert "`disablecallbacks`, `enablecallbacks`, `evokecallback`, and `evokemultiplecallbacks` execute against `hla-backend-python2025` itself" in normalized_backend
    assert "primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter" in normalized_tools_python
    assert "primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface" in normalized_tools_python
    assert "primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter" in normalized_tools_python
    assert "test_target_radar_example_supports_2025_backends" in normalized_tools_python
    assert "test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter" in normalized_tools_python
    assert "test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface" in normalized_tools_python
    assert "primary_python_rti_runs_name_reservation_scenario_without_wrapper_adapter" in normalized_tools_python
    assert "test_2025_provider_runs_federation_lifecycle_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_federation_listing_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_two_federate_object_and_interaction_exchange" in normalized_tools_python
    assert "test_2025_provider_runs_ddm_object_region_lifecycle_scenario_via_compat_adapter" in normalized_tools_python
    assert "test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers" in normalized_tools_python
    assert "test_2025_provider_round_trips_automatic_resign_directive_support_service" in normalized_tools_python
    assert "test_2025_provider_runs_callback_control_route_with_object_reflection_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_attribute_ownership_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter" in normalized_tools_python
    assert "test_2025_provider_routes_mom_time_management_service_interactions" in normalized_tools_python
    assert "test_2025_provider_routes_mom_object_and_ownership_service_interactions" in normalized_tools_python
    assert "test_2025_provider_runs_integrated_time_window_gauntlet_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_output_delivery_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_consumer_order_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_pipeline_restore_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_receive_order_poison_oracle_rejects_closed_window_mutation" in normalized_tools_python
    assert "test_2025_provider_runs_backend_neutral_save_restore_scenario_via_compat_adapter" in normalized_tools_python
    assert "test_2025_provider_runs_example_fom_save_restore_gauntlet" in normalized_tools_python
    assert "test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet" in normalized_tools_python
    assert "test_2025_provider_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso" in normalized_tools_python
    assert "test_2025_provider_restores_closed_window_output_resume_without_dirty_replay" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_time_window_gauntlet_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_restore_state_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_round_trips_support_services_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_round_trips_2025_switch_services_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_federation_lifecycle_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_federation_listing_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_ddm_object_region_lifecycle_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_reports_failed_mom_service_actions_as_mom_exception_interactions" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_example_fom_save_restore_gauntlet_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_restores_closed_window_output_resume_without_dirty_replay_over_fedpro_schema" in normalized_tools_python
    assert 'description = "temporary import-compatibility scaffolding package for the main full python 2025 rti"' in normalized_shim_pyproject
    assert 'backend_names = []' in normalized_shim_pyproject
    assert 'backend_aliases = []' in normalized_shim_pyproject
    assert 'role = "compatibility-wrapper"' in normalized_shim_pyproject
    assert 'status = "compatibility-maintained"' in normalized_shim_pyproject

    assert "bounded ieee 1516.1-2025 fedpro hosted route variant" in normalized_grpc_readme
    assert "that 2025 server is a bounded hosted route variant over the current python 2025 lane" in normalized_grpc_readme
    assert "not a separate rti family and not the main in-process implementation lane" in normalized_grpc_readme
    assert "`packages/hla-backend-python2025` for the main executable 2025 python rti lane" in normalized_networked
    assert "do not refer to the primary 2025 runtime lane itself as a shim" in normalized_networked
    assert "run the primary 2025 python rti main-surface proof lane (python2025)" in normalized_tools_python
    assert "run 2025 python rti / fedpro hosted-route checks" in normalized_tools_python

    assert "`hla-backend-python2025` is the main full python 2025 rti backend" in normalized_packages
    assert "`hla-backend-shim` is deprecated temporary import-compatibility scaffolding" in normalized_packages
    assert "helper modules should remain wrapper-only compatibility aliases over `hla.backends.python2025.*`" in normalized_packages
    assert "should be removed after migration" in normalized_packages


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_keeps_finish_line_documents_off_stale_shim_runtime_language() -> None:
    finish_line_docs = (
        ROOT / "docs" / "plans" / "spec2025_finish_line.md",
        ROOT / "docs" / "plans" / "2025_requirements_finish_line.md",
    )

    for path in finish_line_docs:
        text = " ".join(path.read_text(encoding="utf-8").split()).lower()
        assert "hla-backend-shim implementation package" not in text
        assert "implementation concentration in hla-backend-shim/backend.py remains material" not in text
        assert "create a dedicated rti1516_2025 python backend plugin and make the backend scan detect it" not in text
        assert "the dedicated backend is still absent" not in text
        assert "main full python 2025 rti implementation now runs from hla-backend-python2025" in text
        assert "the public hla-backend-python2025/backend.py shell is now thin" in text
        assert "extracted runtime/state/surface split still needs continued discipline" in text

    legacy_finish_line = " ".join(
        (ROOT / "docs" / "plans" / "2025_requirements_finish_line.md").read_text(encoding="utf-8").split()
    ).lower()
    assert "hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support" in legacy_finish_line
    assert "hosted runtime identity evidence" in legacy_finish_line
    assert "direct ambassador: python2025-rti / python/2025 / python2025 / hla-backend-python2025" in legacy_finish_line
    assert "evidence basis: route_summary.scenario_count=2" in legacy_finish_line
    assert "federation_management_decomposition.slice_id=2025-federation-management-proof-families" in legacy_finish_line
    assert "object_management_decomposition.slice_id=2025-object-management-proof-families" in legacy_finish_line
    assert "ownership_decomposition.slice_id=2025-ownership-proof-families" in legacy_finish_line
    assert "time_management_decomposition.slice_id=2025-time-management-proof-families" in legacy_finish_line
    assert "support_services_decomposition.slice_id=2025-support-services-proof-families" in legacy_finish_line
    assert "callback_decomposition.slice_id=2025-callback-proof-families" in legacy_finish_line
    assert "evidence basis: omt_requirement_proof_audit.ready_for_omt_traceability_claim=true" in legacy_finish_line
    assert "evidence basis: route_summary.scenario_count=8" in legacy_finish_line
    assert "binding_route_decomposition.slice_id=2025-binding-route-proof-families" in legacy_finish_line


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_public_2025_factory_defaults_and_discovery_order_python2025_first() -> None:
    from hla.rti import discover_rti_backends
    from hla.rti import factory as runtime_factory
    from hla.rti1516_2025.factory import create_hla_factory, create_rti_ambassador

    rti_signature = inspect.signature(create_rti_ambassador)
    factory_signature = inspect.signature(create_hla_factory)

    assert rti_signature.parameters["backend"].default == "python2025"
    assert factory_signature.parameters["provider"].default == "python2025"

    plugin_modules = runtime_factory._SOURCE_CHECKOUT_PLUGIN_MODULES
    assert "hla.backends.python2025.plugin" in plugin_modules
    assert "hla.backends.shim.plugin" not in plugin_modules

    registered_2025_backends = [row.name for row in discover_rti_backends(spec="2025")]
    assert "python2025" in registered_2025_backends
    assert "shim" not in registered_2025_backends


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_normalizes_primary_runtime_evidence_away_from_shim_backend_path() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    runtime_backend_path = "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py"

    implemented_slices = snapshot["implemented_evidence_slices"]
    assert any(runtime_backend_path in row["evidence"] for row in implemented_slices)
    assert all(shim_backend_path not in row["evidence"] for row in implemented_slices)

    fi_rows = snapshot["fi_service_proof_audit"]["rows"]
    assert all(runtime_backend_path not in row["evidence_artifacts"] for row in fi_rows)
    assert any(
        "packages/hla-backend-python2025/src/hla/backends/python2025/federation_management_runtime.py"
        in row["evidence_artifacts"]
        for row in fi_rows
    )
    assert any(
        "packages/hla-backend-python2025/src/hla/backends/python2025/time_management_runtime.py"
        in row["evidence_artifacts"]
        for row in fi_rows
    )
    assert all(shim_backend_path not in row["evidence_artifacts"] for row in fi_rows)

    delta_rows = snapshot["delta_requirement_proof_audit"]["rows"]
    assert all(runtime_backend_path not in row["evidence_artifacts"] for row in delta_rows)
    assert any(
        "packages/hla-backend-python2025/src/hla/backends/python2025/ownership_runtime.py"
        in row["evidence_artifacts"]
        for row in delta_rows
    )
    assert any(
        "packages/hla-backend-python2025/src/hla/backends/python2025/time_management_runtime.py"
        in row["evidence_artifacts"]
        for row in delta_rows
    )
    assert all(shim_backend_path not in row["evidence_artifacts"] for row in delta_rows)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_raw_primary_runtime_evidence_on_python2025_path() -> None:
    runtime_backend_path = "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py"

    raw_runtime_backed_slices = [
        row for row in IMPLEMENTED_EVIDENCE_SLICES if runtime_backend_path in row.get("evidence", ())
    ]
    assert raw_runtime_backed_slices
    assert all(SHIM_BACKEND_EVIDENCE_PATH not in row.get("evidence", ()) for row in IMPLEMENTED_EVIDENCE_SLICES)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_named_raw_python2025_support_and_callback_proofs() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    audit_path = ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md"
    spec_text = spec_test_path.read_text(encoding="utf-8")
    normalized_audit_text = " ".join(audit_path.read_text(encoding="utf-8").split()).lower()

    expected_tests = {
        "test_2025_primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter",
        "test_2025_primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface",
        "test_2025_primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter",
    }

    defined_test_names = set(re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_text, re.M))
    assert expected_tests.issubset(defined_test_names)
    assert "support-service handle factories and decode helpers without routing through the compatibility wrapper" in normalized_audit_text
    assert "raw `python2025` runtime accepts the snake-case aliases" in normalized_audit_text
    assert "raw callback-control services on the main lane" in normalized_audit_text


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_helper_modules_as_pure_python2025_re_exports() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    helper_paths = sorted(
        path
        for path in shim_dir.glob("*.py")
        if path.name not in {"__init__.py", "backend.py", "plugin.py", "runtime_aliases.py"}
    )

    assert helper_paths, "expected wrapper helper modules to audit"
    for helper_path in helper_paths:
        source = helper_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        top_level = [
            node
            for node in tree.body
            if not (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
        ]
        assert len(source.splitlines()) <= 50, helper_path.name
        assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree)), helper_path.name
        import_from_nodes = [node for node in top_level if isinstance(node, ast.ImportFrom)]
        assert import_from_nodes, helper_path.name
        assert [node.module for node in import_from_nodes[:1]] == ["__future__"], helper_path.name
        runtime_import_modules = [node.module for node in import_from_nodes[1:]]
        assert runtime_import_modules, helper_path.name
        assert all(
            module is not None and module.startswith("hla.backends.python2025.")
            for module in runtime_import_modules
        ), (helper_path.name, runtime_import_modules)
        non_import_nodes = [node for node in top_level if not isinstance(node, (ast.ImportFrom, ast.Assign))]
        assert not non_import_nodes, helper_path.name


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_helper_modules_mapped_to_declared_runtime_sources() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    helper_paths = sorted(
        path
        for path in shim_dir.glob("*.py")
        if path.name not in {"__init__.py", "backend.py", "plugin.py", "runtime_aliases.py"}
    )

    assert {path.stem for path in helper_paths} == set(_SHIM_HELPER_RUNTIME_MODULES)

    for helper_path in helper_paths:
        tree = ast.parse(helper_path.read_text(encoding="utf-8"))
        import_from_nodes = [
            node for node in tree.body if isinstance(node, ast.ImportFrom) and (node.module or "") != "__future__"
        ]
        observed_modules = tuple(node.module for node in import_from_nodes)
        assert observed_modules == _SHIM_HELPER_RUNTIME_MODULES[helper_path.stem], (
            helper_path.name,
            observed_modules,
        )


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-MIL-002")
def test_verification_run_sequence_keeps_pitch_time_window_probe_boundary_explicit() -> None:
    text = (ROOT / "docs" / "verification" / "run_sequence.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split()).lower()

    assert "the trial-safe time-window future-exclusion and restore-state proof legs" in normalized
    assert "`./tools/pitch time-window-probe`" in text
    assert "`./tools/pitch time-window-restore-state-probe`" in text
    assert "bounded vendor credence for the two-federate 2025 future-exclusion and restore-state routes" in normalized
    assert "they do not replace the direct `python2025` proof lane or the hosted `python-2025-fedpro-grpc` replay" in normalized


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-MIL-001")
def test_verification_readme_indexes_2025_exclusion_boundary() -> None:
    text = (ROOT / "docs" / "verification" / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split()).lower()

    assert "[../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)" in normalized
    assert "explicit 2025 non-claim map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_confines_shim_helper_imports_to_explicit_wrapper_proofs() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    spec_text = spec_test_path.read_text(encoding="utf-8")
    tree = ast.parse(spec_text)

    compatibility_functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and "compatibility_wrapper_consumes_extracted_python2025" in node.name
    }
    assert len(compatibility_functions) >= 10

    shim_helper_import_locations: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.ImportFrom):
                continue
            module = child.module or ""
            if not module.startswith("hla.backends.shim."):
                continue
            if module in {"hla.backends.shim.backend", "hla.backends.shim.plugin"}:
                continue
            shim_helper_import_locations.append((node.name, module))

    assert shim_helper_import_locations
    expected_import_tests = {
        **{f"hla.backends.shim.{module}": test_name for module, test_name in _SHIM_HELPER_COMPAT_TESTS.items()},
        **{f"hla.backends.shim.{module}": test_name for module, test_name in _SHIM_LEGACY_ALIAS_TESTS.items()},
    }
    assert all(
        name in _SHIM_MULTI_TEST_ALLOWED_IMPORTS.get(module, {expected_import_tests.get(module)})
        for name, module in shim_helper_import_locations
    )
    assert set(module.rsplit(".", 1)[-1] for _name, module in shim_helper_import_locations) == (
        set(_SHIM_HELPER_COMPAT_TESTS) | set(_SHIM_LEGACY_ALIAS_TESTS)
    )


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_every_shim_helper_under_an_explicit_wrapper_consumption_test() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    spec_text = spec_test_path.read_text(encoding="utf-8")
    defined_test_names = set(re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_text, re.M))

    assert set(_SHIM_HELPER_COMPAT_TESTS) == set(_SHIM_HELPER_RUNTIME_MODULES)
    assert set(_SHIM_HELPER_COMPAT_TESTS.values()).issubset(defined_test_names)
    assert set(_SHIM_LEGACY_ALIAS_TESTS.values()).issubset(defined_test_names)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_helper_modules_out_of_repo_runtime_import_paths() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    helper_module_names = {
        path.stem
        for path in shim_dir.glob("*.py")
        if path.name not in {"__init__.py", "backend.py", "plugin.py"}
    }
    allowed_import_path = ROOT / "tests" / "test_rti1516_2025_python2025_runtime.py"
    unexpected_locations: list[tuple[str, str]] = []

    for path in ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            module = node.module or ""
            if not module.startswith("hla.backends.shim."):
                continue
            leaf = module.rsplit(".", 1)[-1]
            if leaf not in helper_module_names:
                continue
            if path != allowed_import_path:
                unexpected_locations.append((str(path.relative_to(ROOT)), module))

    assert unexpected_locations == []
