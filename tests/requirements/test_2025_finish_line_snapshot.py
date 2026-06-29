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


def _assert_contains_all(text: str, snippets: list[str]) -> None:
    for snippet in snippets:
        assert snippet in text


def _assert_any_contains(items: list[str], snippets: list[str]) -> None:
    for snippet in snippets:
        assert any(snippet in item for item in items)


def _assert_anchor_row(
    pytest_rows: dict[str, dict[str, object]],
    requirement_id: str,
    min_count: int,
    snippets: list[str],
) -> None:
    row = pytest_rows[requirement_id]
    assert row["pytest_anchor_count"] >= min_count
    _assert_any_contains(row["pytest_anchors"], snippets)  # type: ignore[arg-type]


def _assert_item_list_contains(items: list[str], snippets: list[str]) -> None:
    _assert_any_contains(items, snippets)


def _assert_live_test_anchor(anchor: str) -> None:
    file_part, test_name = anchor.split("::", 1)
    file_path = ROOT / file_part
    assert file_path.exists(), anchor
    assert f"def {test_name}(" in file_path.read_text(encoding="utf-8"), anchor


def _assert_live_relative_path(path_text: str) -> None:
    assert (ROOT / path_text).exists(), path_text


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

    assert snapshot["scope"] == "IEEE 1516-2025 requirements closeout-reporting inventory, not a conformance claim"
    assert snapshot["registry"]["initial_tranche_requirements"] == 28
    assert "hla-2025-executable-test-requirements-v3" in snapshot["registry"]["imported_packets"]

    executable = snapshot["executable_test_backlog"]
    assert executable["row_count"] > 0
    assert executable["source_rows"] > 0
    assert executable["row_count"] >= executable["source_rows"]
    assert sum(executable["by_test_kind"].values()) == executable["row_count"]

    depth = snapshot["requirement_depth_expansion"]
    assert depth["status"] == "imported-harmonization-candidate"
    assert depth["row_count"] == depth["row_count_from_csv"]
    assert sum(depth["by_area"].values()) == depth["row_count"]
    assert sum(depth["by_delta_type"].values()) == depth["row_count"]

    disposition = snapshot["requirement_coverage_disposition"]
    assert disposition["status"] == "repo-reconciled-disposition"
    assert disposition["row_count"] == disposition["row_count_from_csv"]
    assert sum(disposition["by_disposition"].values()) == disposition["row_count"]
    assert sum(disposition["by_priority"].values()) == disposition["row_count"]
    assert sum(disposition["by_closure_wave"].values()) == disposition["row_count"]
    assert disposition["covered_row_count"] == disposition["by_disposition"]["covered"]

    backlog = snapshot["completion_backlog"]
    assert backlog["row_count"] > 0
    assert sum(backlog["by_bucket"].values()) == backlog["row_count"]
    assert sum(backlog["by_current_status"].values()) == backlog["row_count"]
    assert backlog["by_current_status"].get("partial", 0) == 0
    assert "planned" not in backlog["by_current_status"]
    assert backlog["high_priority_open_count"] == 0
    assert {row["id"] for row in backlog["high_priority_open"]} == set()

    matrix = snapshot["verification_matrix"]
    assert matrix["row_count"] == backlog["row_count"]
    assert matrix["high_priority_missing_anchor_count"] == 0
    assert matrix["high_priority_missing_anchors"] == []

    pytest_anchor_audit = snapshot["requirement_pytest_anchor_audit"]
    assert pytest_anchor_audit["row_count"] == pytest_anchor_audit["anchored_requirement_count"]
    assert "direct pytest-function anchors" in pytest_anchor_audit["current_assessment"]
    pytest_rows = {row["requirement_id"]: row for row in pytest_anchor_audit["rows"]}
    _assert_anchor_row(pytest_rows, "HLA2025-FI-SVC-001", 2, ["test_2025_provider_is_first_green_runtime_path"])
    _assert_anchor_row(
        pytest_rows,
        "HLA2025-FI-SVC-005",
        10,
        [
            "test_2025_provider_rejects_duplicate_federation_and_federate_names",
            "test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema",
        ],
    )
    _assert_anchor_row(
        pytest_rows,
        "HLA2025-FI-SVC-083",
        9,
        [
            "test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks",
            "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema",
        ],
    )
    _assert_anchor_row(
        pytest_rows,
        "HLA2025-BND-003",
        1,
        ["test_2025_fedpro_transport_replaces_wsdl_without_cross_wiring_legacy_binding"],
    )
    _assert_anchor_row(
        pytest_rows,
        "HLA2025-OMT-COMP-001",
        1,
        ["test_2025_parser_round_trips_extended_omt_supported_subset"],
    )
    _assert_anchor_row(
        pytest_rows,
        "HLA2025-NEW-007",
        1,
        ["test_2025_differentials_capture_replacement_policy_and_mom_switch_surface"],
    )

    assert snapshot["unanchored_requirement_audit"]["row_count"] == 0

    route_rows = {
        (row["scenario"], row["route"]): row
        for row in snapshot["route_parity_matrix"]["rows"]
    }
    for key in (
        ("federation_lifecycle", "python1516_2025"),
        ("time_management", "python1516_2025-fedpro-grpc"),
    ):
        row = route_rows[key]
        assert row["status"] == "parity-covered"
        assert row["runtime_provider"] == "python1516_2025"
        assert row["implementation_lane"] == "hla-backend-python1516-2025"
        assert row["counts_as_python_2025_rti"] is True
        assert row["wrapper_only"] is False

    fi_service_audit = snapshot["fi_service_proof_audit"]
    assert fi_service_audit["row_count"] == disposition["fi_binding_surface"]["fi_rows"]
    assert fi_service_audit["fully_traceable_service_count"] == fi_service_audit["row_count"]
    assert fi_service_audit["ready_for_per_service_runtime_traceability_claim"] is True

    delta_audit = snapshot["delta_requirement_proof_audit"]
    assert delta_audit["fully_traceable_requirement_count"] == delta_audit["row_count"]
    assert delta_audit["ready_for_delta_traceability_claim"] is True

    binding_audit = snapshot["binding_requirement_proof_audit"]
    assert binding_audit["fully_traceable_requirement_count"] == binding_audit["row_count"]
    assert binding_audit["ready_for_binding_traceability_claim"] is True

    omt_audit = snapshot["omt_requirement_proof_audit"]
    assert omt_audit["traceable_requirement_count"] == omt_audit["row_count"]
    assert omt_audit["ready_for_omt_traceability_claim"] is False

    claim_audit = snapshot["completion_claim_audit"]
    assert claim_audit["claim_shape"] == "bounded-working-surface-with-explicit-boundaries"
    assert claim_audit["ready_for_supported-boundary_statement"] is True
    assert claim_audit["ready_for_full_2025_conformance_claim"] is False
    assert "supported-boundary statement" in claim_audit["current_assessment"]

    requirement_audit = snapshot["requirement_by_requirement_audit"]
    assert requirement_audit["audit_status"] == "row-level-requirement-disposition-audit-captured"
    assert requirement_audit["ready_for_row_level_requirement_audit_claim"] is True
    assert requirement_audit["ready_for_full_2025_conformance_claim"] is False

    boundary_statement = snapshot["supported_boundary_statement"]
    assert boundary_statement["statement_status"] == "supported-boundary-statement"
    assert boundary_statement["ready"] is True
    assert "bounded working surface" in boundary_statement["statement"]

    full_claim_partition = snapshot["full_claim_blocker_partition_audit"]
    assert full_claim_partition["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True

    closeout_partition = snapshot["closeout_blocker_partition_audit"]
    assert closeout_partition["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True

    closeout = snapshot["closeout_readiness"]
    assert closeout["ready_for_slice_closeout"] is True
    assert closeout["ready_for_full_completion_claim"] is False


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}
    python2025_backend_path = (
        ROOT / "packages" / "hla-backend-python1516-2025" / "src" / "hla" / "backends" / "python1516_2025" / "backend.py"
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
    assert "direct execution of the shared two-federate save/restore suite on the main python1516_2025 runtime plus hosted replay over the FedPro route" in slices["2025-save-restore-lifecycle"]["supported_scope"]
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
    assert "region-scoped requestAttributeValueUpdate callbacks across the live python1516_2025 runtime lane and hosted FedPro route" in slices["2025-object-attribute-update-request-callbacks"]["supported_scope"]

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
    assert "bounded Python 2025 closeout gates explicit" in slices["2025-python-rti-milestone-ledger"]["supported_scope"]

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
    concentration_audit = snapshot["implementation_concentration_audit"]
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    markdown = "\n".join(build_spec2025_finish_line_markdown(ROOT))
    _assert_contains_all(
        markdown,
        [
            "HLA conformance",
            "Closeout Readiness",
            "Promotion Vs Split Audit",
            "Pytest Anchor Audit",
                "Anchored requirements: 731",
            "Unanchored Requirement Audit",
            "Unanchored ledger requirements: 0",
            "FI Service Proof Audit",
            "Service rows: 196",
            "Ready for per-service runtime traceability claim: True",
            "Delta Requirement Proof Audit",
            "Delta rows: 20",
            "Binding Requirement Proof Audit",
            "Binding rows: 3",
            "OMT Requirement Proof Audit",
            "OMT rows: 461",
            "Callback Proof Audit",
            "Callback Route Parity Audit",
            "Callback rows: 55",
            "Hosted/direct route-backed callbacks: 55",
            "Callback-helper-only rows: 0",
            "Ready for full Python-lane callback route parity claim: True",
            "Ready for callback surface traceability claim: True",
            "Ready for callback-by-callback working-surface claim: True",
            "Support-Service Proof Audit",
            "Support-service rows: 64",
            "Complete negative-path rows: 61",
            "Ready for support-service traceability claim: True",
            "Python RTI Milestone Audit",
            "Audit status: bounded-python-rti-milestones",
            "Milestones per route: 6",
            "python1516_2025",
            "python1516_2025-fedpro-grpc",
            "Best-attempt Python RTI 2025 working surface: bounded-working-slice",
            "Message exchange and routing: covered-routing-slice",
            "Time synchronization and advance flow: covered-time-advance-slice",
            "GALT and LITS behavior: bounded-query-evidence",
            "Lookahead handling and windows: bounded-lookahead-evidence",
            "future-exclusion, output-delivery, consumer-order, pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline resume, and time-window proof",
            "negative-oracle guards rejecting mismatched LITS boundaries, premature output, reversed consumer order, cross-window contamination, and dirty post-restore replay",
            "save-restore lookahead rollback with queued-TSO redelivery",
            "Requirement-By-Requirement Audit",
            "Audit status: row-level-requirement-disposition-audit-captured",
            "Ready for row-level audit claim: True",
        ],
    )
    _assert_contains_all(
        markdown,
        [
            "Duplicate Umbrella Mapping Audit",
            "Framework doc path: docs/requirements/ieee-1516-2025/framework_rules.md",
            "Delta doc path: docs/requirements/ieee-1516-2025/callback_binding_deltas.md",
            "Ready for duplicate umbrella mapping claim: True",
            "framework-umbrella: 10 rows",
            "delta-umbrella: 12 rows",
            "Retired Legacy Mapping Audit",
            "Doc path: docs/requirements/ieee-1516-2025/retired_legacy_mapping.md",
            "Ready for retired legacy mapping claim: True",
            "Federate Interface legacy API: 11 rows",
            "OMT legacy schema: 13 rows",
            "Save/Restore Bounded Proof Audit",
            "Doc path: docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md",
            "Ready for save/restore bounded proof claim: True",
            "Callback Bounded Proof Audit",
            "Doc path: docs/requirements/ieee-1516-2025/callback_bounded_proof.md",
            "Ready for callback bounded proof claim: True",
            "Python2025 Exclusion Boundaries Audit",
            "Finish-line source path: packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py",
            "Direct compat anchor count: 0",
            "Ready for python1516_2025 exclusion boundaries claim: True",
            "Lookahead Window Bounded Proof Audit",
            "Doc path: docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md",
            "Ready for lookahead window bounded proof claim: True",
            "Pitch probe routes: ./tools/pitch time-window-probe, ./tools/pitch time-window-restore-state-probe",
            "Requirement-by-requirement area closure:",
            "Completion Claim Audit",
            "Ready for supported-boundary statement: True",
            "Ready for full 2025 conformance claim: False",
            "Covered rows: 645",
            "Supported Boundary Statement",
            "Status: supported-boundary-statement",
            "Ready: True",
        ],
    )
    assert "Implementation Concentration Audit" in markdown
    assert f"Runtime backend-backed slices: {concentration_audit['runtime_backend_slice_count']}" in markdown
    assert f"Runtime backend slice share: {concentration_audit['runtime_backend_slice_share']}" in markdown
    assert "Semantic concentration is material: False" in markdown
    assert "Leading extracted runtime owners:" in markdown
    assert "- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/hosted_fedpro.py:" in markdown
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
    assert "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/attribute_policy.py: object-attribute-runtime" in markdown
    assert (
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py: "
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
    assert "HLA2025-FI-SVC-005, HLA2025-FI-SVC-008, HLA2025-FI-SVC-010, and HLA2025-FI-SVC-011" in markdown
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
    assert "Family count: 23" in markdown
    assert "All families route-backed across current Python lanes: True" in markdown
    assert "Wrapper-Boundary Family Asymmetry Audit" in markdown
    assert "Balanced families: 22" in markdown
    assert "Direct-heavier families: 1" in markdown
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
    assert "Evidence basis: omt_requirement_proof_audit.ready_for_omt_traceability_claim=false" in markdown
    assert "Evidence basis: route_summary.scenario_count=8" in markdown
    assert "support_services_decomposition.slice_id=2025-support-services-proof-families" in markdown
    assert "callback_decomposition.slice_id=2025-callback-proof-families" in markdown
    assert "binding_route_decomposition.slice_id=2025-binding-route-proof-families" in markdown
    assert "Implementation Lane Audit" in markdown
    assert "Current 2025 backend package: hla-backend-python1516-2025" in markdown
    assert "Compatibility wrapper package: hla-backend-shim" in markdown
    assert "Compatibility wrapper status: compatibility-maintained" in markdown
    assert "Compatibility wrapper role: compatibility-wrapper" in markdown
    assert "Compatibility wrapper delegates runtime semantics to: hla-backend-python1516-2025" in markdown
    assert "Python2025 Proof-Lane Audit" in markdown
    assert "Ready for main-implementation operator-lane claim: True" in markdown
    assert "Direct lane: ./tools/python verify-main-2025" in markdown
    assert "Hosted extension lane: ./tools/python verify-routes-2025" in markdown
    assert "Current operator runs:" in markdown
    assert "python1516_2025-main / ./tools/python verify-main-2025: 324 passed across wrapper subcommands plus Target/Radar example" in markdown
    assert "python1516_2025-routes / ./tools/python verify-routes-2025: 434 passed across direct-plus-hosted wrapper subcommands plus closeout bundle and Target/Radar example" in markdown
    assert "Evidence anchors: testing/test_surface_manifest.json, tools/python, docs/test_surface.md, README.md" in markdown
    assert "Reference 2010 backend package: hla-backend-python1516e" in markdown
    assert "Backend packages discovered: 6" in markdown
    assert "Dedicated 2025 candidates cleanly separated: True" in markdown
    assert "Dedicated 2025 legacy-package delegation violations: 0" in markdown
    assert "hla-backend-cpp-shim" in markdown
    assert "shim (shim): hla-backend-shim supports rti1516_2025" not in markdown
    assert "Dedicated 2025 backend package present: True" in markdown
    assert "python1516_2025-fedpro-grpc: hosted-transport-route" in markdown
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
    assert "Future backend package target: hla-backend-python1516-2025" in markdown
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
    assert "Target import root: hla.backends.python1516_2025" in markdown
    assert "Target backend name: python1516_2025" in markdown
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
    assert payload["requirement_pytest_anchor_audit"]["row_count"] == 731
    assert payload["unanchored_requirement_audit"]["row_count"] == 0
    assert payload["route_parity_matrix"]["by_status"]["missing"] == 0
    payload_route_rows = {
        (row["scenario"], row["route"]): row
        for row in payload["route_parity_matrix"]["rows"]
    }
    assert {
        key: payload_route_rows[("federation_lifecycle", "python1516_2025")][key]
        for key in ("runtime_provider", "implementation_lane", "counts_as_python_2025_rti", "wrapper_only")
    } == {
        "runtime_provider": "python1516_2025",
        "implementation_lane": "hla-backend-python1516-2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }
    assert {
        key: payload_route_rows[("time_management", "python1516_2025-fedpro-grpc")][key]
        for key in ("runtime_provider", "implementation_lane", "counts_as_python_2025_rti", "wrapper_only")
    } == {
        "runtime_provider": "python1516_2025",
        "implementation_lane": "hla-backend-python1516-2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }
    assert {
        "fi_service_proof_audit": {
            "row_count": payload["fi_service_proof_audit"]["row_count"],
            "ready": payload["fi_service_proof_audit"]["ready_for_per_service_runtime_traceability_claim"],
        },
        "delta_requirement_proof_audit": {
            "row_count": payload["delta_requirement_proof_audit"]["row_count"],
            "ready": payload["delta_requirement_proof_audit"]["ready_for_delta_traceability_claim"],
        },
        "binding_requirement_proof_audit": {
            "row_count": payload["binding_requirement_proof_audit"]["row_count"],
            "ready": payload["binding_requirement_proof_audit"]["ready_for_binding_traceability_claim"],
        },
        "omt_requirement_proof_audit": {
            "row_count": payload["omt_requirement_proof_audit"]["row_count"],
            "ready": payload["omt_requirement_proof_audit"]["ready_for_omt_traceability_claim"],
        },
    } == {
        "fi_service_proof_audit": {"row_count": 196, "ready": True},
        "delta_requirement_proof_audit": {"row_count": 20, "ready": True},
        "binding_requirement_proof_audit": {"row_count": 3, "ready": True},
        "omt_requirement_proof_audit": {"row_count": 461, "ready": False},
    }
    assert {
        "audit_status": payload["python_rti_milestone_audit"]["audit_status"],
        "milestone_count": payload["python_rti_milestone_audit"]["milestone_count"],
        "row_count": payload["python_rti_milestone_audit"]["row_count"],
        "hosted_all_route_parity_covered": payload["python_rti_milestone_audit"]["by_route"]["python1516_2025-fedpro-grpc"][
            "all_route_parity_covered"
        ],
    } == {
        "audit_status": "bounded-python-rti-milestones",
        "milestone_count": 6,
        "row_count": 12,
        "hosted_all_route_parity_covered": True,
    }
    assert {
        "audit_status": payload["requirement_by_requirement_audit"]["audit_status"],
        "ready": payload["requirement_by_requirement_audit"]["ready_for_row_level_requirement_audit_claim"],
    } == {
        "audit_status": "row-level-requirement-disposition-audit-captured",
        "ready": True,
    }
    assert {
        "ready_for_supported-boundary_statement": payload["completion_claim_audit"]["ready_for_supported-boundary_statement"],
        "ready_for_full_2025_conformance_claim": payload["completion_claim_audit"]["ready_for_full_2025_conformance_claim"],
    } == {
        "ready_for_supported-boundary_statement": True,
        "ready_for_full_2025_conformance_claim": False,
    }
    assert {
        "statement_status": payload["supported_boundary_statement"]["statement_status"],
        "ready": payload["supported_boundary_statement"]["ready"],
    } == {
        "statement_status": "supported-boundary-statement",
        "ready": True,
    }
    assert {
        "audit_status": payload["implementation_lane_audit"]["audit_status"],
        "current_2025_backend_package": payload["implementation_lane_audit"]["current_2025_lane"]["backend_package"],
        "reference_2010_backend_package": payload["implementation_lane_audit"]["reference_2010_lane"]["backend_package"],
        "dedicated_2025_backend_package_present": payload["implementation_lane_audit"]["dedicated_2025_backend_package_present"],
        "hosted_route": payload["implementation_lane_audit"]["python_2025_routes"][1]["route"],
        "hosted_identity_route": payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"]["route"],
        "hosted_factory_boundary_audit_status": payload["implementation_lane_audit"]["hosted_factory_boundary_evidence"][
            "audit_status"
        ],
        "hosted_client_implementation_lane": payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"][
            "hosted_client_report"
        ]["implementation_lane"],
        "hosted_server_transport_kind": payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"][
            "hosted_server_report"
        ]["transport_kind"],
        "direct_runtime_backend_kind": payload["implementation_lane_audit"]["hosted_runtime_identity_evidence"][
            "direct_runtime_report"
        ]["backend_kind"],
    } == {
        "audit_status": "current-lane-architecture-captured",
        "current_2025_backend_package": "hla-backend-python1516-2025",
        "reference_2010_backend_package": "hla-backend-python1516e",
        "dedicated_2025_backend_package_present": True,
        "hosted_route": "python1516_2025-fedpro-grpc",
        "hosted_identity_route": "python1516_2025-fedpro-grpc",
        "hosted_factory_boundary_audit_status": "factory-boundary-explicit",
        "hosted_client_implementation_lane": "hla-backend-python1516-2025",
        "hosted_server_transport_kind": "grpc",
        "direct_runtime_backend_kind": "python/2025",
    }
    assert {
        "ready_for_current_lane_promotion_as_working_surface": payload["promotion_split_audit"][
            "ready_for_current_lane_promotion_as_working_surface"
        ],
        "ready_for_permanent_no-split_decision": payload["promotion_split_audit"]["ready_for_permanent_no-split_decision"],
    } == {
        "ready_for_current_lane_promotion_as_working_surface": True,
        "ready_for_permanent_no-split_decision": False,
    }
    assert {
        "ready_for_bounded_working_surface_claim": payload["objective_dimension_audit"]["ready_for_bounded_working_surface_claim"],
        "ready_for_full_2025_completion_claim": payload["objective_dimension_audit"]["ready_for_full_2025_completion_claim"],
    } == {
        "ready_for_bounded_working_surface_claim": True,
        "ready_for_full_2025_completion_claim": False,
    }
    assert {
        "ready_for_main_python2025_implementation_claim": payload["main_python2025_implementation_claim_audit"][
            "ready_for_main_python2025_implementation_claim"
        ],
        "ready_for_full_2025_conformance_claim": payload["main_python2025_implementation_claim_audit"][
            "ready_for_full_2025_conformance_claim"
        ],
    } == {
        "ready_for_main_python2025_implementation_claim": True,
        "ready_for_full_2025_conformance_claim": False,
    }
    main_impl_claim = payload["main_python2025_implementation_claim_audit"]
    route_rows = payload_route_rows
    assert {
        "all_current_full_claim_blockers_are_external_to_main_python2025_runtime": payload["full_claim_blocker_partition_audit"][
            "all_current_full_claim_blockers_are_external_to_main_python2025_runtime"
        ],
        "all_current_closeout_blockers_are_external_to_main_python2025_runtime": payload["closeout_blocker_partition_audit"][
            "all_current_closeout_blockers_are_external_to_main_python2025_runtime"
        ],
        "ready_for_slice_closeout": payload["closeout_readiness"]["ready_for_slice_closeout"],
        "ready_for_full_completion_claim": payload["closeout_readiness"]["ready_for_full_completion_claim"],
    } == {
        "all_current_full_claim_blockers_are_external_to_main_python2025_runtime": True,
        "all_current_closeout_blockers_are_external_to_main_python2025_runtime": True,
        "ready_for_slice_closeout": True,
        "ready_for_full_completion_claim": False,
    }

    markdown = paths["markdown"].read_text(encoding="utf-8")
    legacy_markdown = paths["legacy_markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert legacy_markdown == markdown
    _assert_contains_all(
        markdown,
        [
            "Imported requirement-depth rows: 691",
            "Imported provisional disposition rows: 691",
            "Closeout Readiness",
            "Closeout Blocker Partition Audit",
            "Pytest Anchor Audit",
            "Unanchored Requirement Audit",
            "FI Service Proof Audit",
            "Delta Requirement Proof Audit",
            "Binding Requirement Proof Audit",
            "OMT Requirement Proof Audit",
            "Python RTI Milestone Audit",
            "Requirement-By-Requirement Audit",
            "Completion Claim Audit",
            "Supported Boundary Statement",
            "Main Python2025 Implementation Claim Audit",
            "Full-Claim Blocker Partition Audit",
            "Objective Audit",
            "Implemented Evidence Slices",
            "| Slice | Slice disposition | Backend or route scope | Requirements | Evidence |",
            "These are slice-level implementation readings, not canonical requirement-status rows.",
            "| ID | Area | Priority | Canonical backlog disposition | Backend or binding scope | Verification work |",
        ],
    )
    matrix = paths["verification_matrix"].read_text(encoding="utf-8")
    assert "HLA2025-VER-001" in matrix
    assert "2025-verification-anchor-matrix" in matrix
    assert "HLA2025-MIL-001" in matrix
    assert "2025-python-rti-milestone-ledger" in matrix
    route_matrix = paths["route_parity_matrix"].read_text(encoding="utf-8")
    route_matrix_markdown = paths["route_parity_markdown"].read_text(encoding="utf-8")
    _assert_contains_all(
        route_matrix,
        [
            "scenario,route,parity_status,evidence_scope,requirements,evidence_tests,evidence_artifacts,"
            "runtime_provider,implementation_lane,counts_as_python_2025_rti,wrapper_only,notes",
            "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity",
            "federation_lifecycle,java-standard-2025-jpype,parity-covered,scenario-parity",
            "federation_lifecycle,cpp-standard-2025-grpc,parity-covered,scenario-parity",
            "federation_lifecycle,python1516_2025,parity-covered,scenario-parity",
            ",python1516_2025,hla-backend-python1516-2025,true,false,",
            "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper",
            "snake-case alias acceptance on the primary direct-runtime surface",
            "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python1516-2025 lane",
        ],
    )
    assert route_matrix_markdown.startswith("# IEEE 1516-2025 Route Parity Matrix")
    _assert_contains_all(
        route_matrix_markdown,
        [
            "python1516_2025` and `python1516_2025-fedpro-grpc` are the Python-owned runtime evidence lanes over `hla-backend-python1516-2025`",
            "Java/C++ standard routes are binding/adaptation-seam evidence over that same runtime, not alternate Python RTI implementations.",
            "Use `Parity status` as a route-evidence reading only. It is not the canonical requirement disposition.",
            "For the main-implementation claim, read the scenario rows as a proof-family ledger too:",
            "the Python-owned rows below are the main route-parity proof families for federation, object, ownership, DDM, time, save/restore, MOM, and support-services behavior",
            "those Python-owned rows are parity evidence over the extracted `hla-backend-python1516-2025` runtime/state/surface modules",
            "hosted FedPro rows show transport-seam replay of those same runtime families rather than a different 2025 RTI owner",
            "| federation_lifecycle | python1516_2025-fedpro-grpc | parity-covered | scenario-parity |",
            "| time_management | python1516_2025-fedpro-grpc | parity-covered | scenario-parity |",
            "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper",
            "snake-case alias acceptance on the primary direct-runtime surface",
            "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python1516-2025 lane",
        ],
    )

    assert main_impl_claim["implementation_owner"] == "hla-backend-python1516-2025"
    assert "hla-backend-python1516-2025 is the implementation owner for the real executable 2025 Python RTI surface" in main_impl_claim["claim"]
    assert "main python1516_2025 RTI implementation claim is ready" in main_impl_claim["current_assessment"]
    blocker_partition = payload["full_claim_blocker_partition_audit"]
    assert {
        "all_current_full_claim_blockers_are_external_to_main_python2025_runtime": blocker_partition[
            "all_current_full_claim_blockers_are_external_to_main_python2025_runtime"
        ],
        "direct_runtime_incompleteness_blocker_count": blocker_partition[
            "direct_runtime_incompleteness_blocker_count"
        ],
    } == {
        "all_current_full_claim_blockers_are_external_to_main_python2025_runtime": True,
        "direct_runtime_incompleteness_blocker_count": 0,
    }
    assert "all sit outside direct main-lane python1516_2025 runtime completeness" in blocker_partition["current_assessment"]
    closeout_partition = payload["closeout_blocker_partition_audit"]
    assert {
        "all_current_closeout_blockers_are_external_to_main_python2025_runtime": closeout_partition[
            "all_current_closeout_blockers_are_external_to_main_python2025_runtime"
        ],
        "direct_runtime_incompleteness_blocker_count": closeout_partition[
            "direct_runtime_incompleteness_blocker_count"
        ],
    } == {
        "all_current_closeout_blockers_are_external_to_main_python2025_runtime": True,
        "direct_runtime_incompleteness_blocker_count": 0,
    }
    assert "all describe requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits" in closeout_partition["current_assessment"]

    assert {
        key: route_rows[("federation_lifecycle", "python1516_2025")][key]
        for key in ("runtime_provider", "implementation_lane", "counts_as_python_2025_rti", "wrapper_only")
    } == {
        "runtime_provider": "python1516_2025",
        "implementation_lane": "hla-backend-python1516-2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }
    assert {
        key: route_rows[("time_management", "python1516_2025-fedpro-grpc")][key]
        for key in ("runtime_provider", "implementation_lane", "counts_as_python_2025_rti", "wrapper_only")
    } == {
        "runtime_provider": "python1516_2025",
        "implementation_lane": "hla-backend-python1516-2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }


@pytest.mark.requirements("HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_finish_line_snapshot_uses_live_traceability_artifacts() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    route_rows = snapshot["route_parity_matrix"]["rows"]
    route_row_map = {(row["scenario"], row["route"]): row for row in route_rows}
    python_rows = [row for row in route_rows if row["route"] in {"python1516_2025", "python1516_2025-fedpro-grpc"}]
    hosted_fedpro_rows = [row for row in route_rows if row["route"] == "python1516_2025-fedpro-grpc"]
    compatibility_rows = [
        row for row in route_rows if row["route"].startswith(("java-standard-2025", "cpp-standard-2025"))
    ]
    assert python_rows
    assert all(row["runtime_provider"] == "python1516_2025" for row in python_rows)
    assert all(row["implementation_lane"] == "hla-backend-python1516-2025" for row in python_rows)
    assert all(row["counts_as_python_2025_rti"] is True for row in python_rows)
    assert all(row["wrapper_only"] is False for row in python_rows)
    assert all(row["evidence_tests"] for row in python_rows)
    for row in python_rows:
        for evidence_path in row["evidence_tests"]:
            _assert_live_relative_path(evidence_path)
        for artifact_path in row["evidence_artifacts"]:
            _assert_live_relative_path(artifact_path)

    standard_rows = compatibility_rows
    assert standard_rows
    assert all(row["runtime_provider"] == "python1516_2025" for row in standard_rows)
    assert all(row["implementation_lane"] == "hla-backend-python1516-2025" for row in standard_rows)
    assert all(row["counts_as_python_2025_rti"] is False for row in standard_rows)

    pytest_rows = {
        row["requirement_id"]: row
        for row in snapshot["requirement_pytest_anchor_audit"]["rows"]
    }
    assert pytest_rows
    for row in pytest_rows.values():
        assert row["pytest_anchor_count"] == len(row["pytest_anchors"])
        for anchor in row["pytest_anchors"]:
            _assert_live_test_anchor(anchor)

    proof_lane_audit = snapshot["python2025_proof_lane_audit"]
    for lane in (proof_lane_audit["default_direct_lane"], proof_lane_audit["hosted_extension_lane"]):
        for doc_path in lane["docs"]:
            _assert_live_relative_path(doc_path)
    for anchor_path in proof_lane_audit["evidence_anchors"]:
        _assert_live_relative_path(anchor_path)

    for row in snapshot["full_claim_blocker_partition_audit"]["blocker_rows"]:
        assert row["counts_against_main_python2025_runtime_completeness"] is False
        assert row["evidence_basis"].strip()
    for row in snapshot["closeout_blocker_partition_audit"]["blocker_rows"]:
        assert row["counts_against_main_python2025_runtime_completeness"] is False
        assert row["evidence_basis"].strip()
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in route_row_map[
        ("support_services", "python1516_2025")
    ]["notes"]
    assert "snake-case alias acceptance on the primary direct-runtime surface" in route_row_map[
        ("support_services", "python1516_2025")
    ]["notes"]
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release on the main hla-backend-python1516-2025 lane" in route_row_map[
        ("support_services", "python1516_2025")
    ]["notes"]
    lane_audit = snapshot["implementation_lane_audit"]
    hosted_identity = lane_audit["hosted_runtime_identity_evidence"]
    assert hosted_identity["audit_status"] == "direct-server-client-identity-aligned"
    assert hosted_identity["route"] == "python1516_2025-fedpro-grpc"
    assert hosted_identity["hosted_client_report"]["counts_as_python_2025_rti"] is True
    assert hosted_identity["hosted_client_report"]["wrapper_only"] is False
    assert hosted_identity["hosted_client_report"]["transport_kind"] == "grpc"
    assert hosted_identity["hosted_client_report"]["route_family"] == "fedpro"

    hosted_factory_boundary = lane_audit["hosted_factory_boundary_evidence"]
    assert hosted_factory_boundary["audit_status"] == "factory-boundary-explicit"
    assert hosted_factory_boundary["unsupported_factory_surfaces"] == [
        "create_rti_ambassador(backend='shim', transport=...)",
    ]
    assert hosted_factory_boundary["evidence_tests"]
    for anchor in hosted_factory_boundary["evidence_tests"]:
        _assert_live_test_anchor(anchor)

    shared_scenario = lane_audit["package_owned_shared_scenario_evidence"]
    assert shared_scenario["audit_status"] == "package-owned-target-radar-2025-path-captured"
    assert shared_scenario["shared_route"] == "target-radar-shared-scenario"
    assert shared_scenario["python2025_runtime_report"]["counts_as_python_2025_rti"] is True
    assert shared_scenario["shim_runtime_report"]["counts_as_python_2025_rti"] is False
    assert shared_scenario["evidence_tests"]
    for anchor in shared_scenario["evidence_tests"]:
        _assert_live_test_anchor(anchor)

    assert lane_audit["evidence_anchors"]
    for evidence_path in lane_audit["evidence_anchors"]:
        _assert_live_relative_path(evidence_path)

    assert all(
        "transport-seam evidence over hla-backend-python1516-2025" in str(row["notes"])
        and "counts_as_python_2025_rti=true" in str(row["notes"])
        and "wrapper_only=false" in str(row["notes"])
        for row in hosted_fedpro_rows
    )
    assert all(
        "executed over the primary python1516_2025 runtime lane in hla-backend-python1516-2025" in str(row["notes"])
        and "binding/adaptation-seam evidence over the main hla-backend-python1516-2025 runtime" in str(row["notes"])
        and "not as alternate ownership of core 2025 RTI semantics" in str(row["notes"])
        for row in compatibility_rows
    )


def test_2025_backend_plugin_scan_detects_future_dedicated_python_2025_backend(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "packages" / "hla-backend-python1516-2025" / "src" / "hla" / "backends" / "python1516_2025"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        '''"""Synthetic dedicated Python 2025 backend plugin for scanner regression tests."""
from hla.rti.plugin_api import RTIBackendPlugin


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python1516_2025",
        aliases=("python-1516-2025",),
        family="python-rti-1516-2025",
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

    assert scan["backend_package_dirs"] == ["hla-backend-python1516-2025", "hla-backend-shim"]
    assert scan["backend_package_count"] == 2
    assert {
        (record["package"], record["name"], record["family"])
        for record in scan["rti1516_2025_plugin_records"]
    } == {
        ("hla-backend-python1516-2025", "python1516_2025", "python-rti-1516-2025"),
    }
    assert scan["dedicated_python_2025_backend_candidates"] == [
        {
            "package": "hla-backend-python1516-2025",
            "plugin_path": "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py",
            "name": "python1516_2025",
            "family": "python-rti-1516-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert scan["dedicated_python_2025_legacy_package_delegation_violations"] == []
    assert scan["dedicated_python_2025_candidates_cleanly_separated"] is True


def test_2025_backend_plugin_scan_rejects_shim_delegating_python_2025_candidate(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "packages" / "hla-backend-python1516-2025" / "src" / "hla" / "backends" / "python1516_2025"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        '''"""Synthetic invalid Python 2025 backend that delegates to the shim."""
from hla.backends.shim.backend import create_shim_backend
from hla.rti.plugin_api import RTIBackendPlugin


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python1516_2025",
        aliases=("python-1516-2025",),
        family="python-rti-1516-2025",
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
            "package": "hla-backend-python1516-2025",
            "plugin_path": "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py",
            "name": "python1516_2025",
            "family": "python-rti-1516-2025",
            "supports": ["rti1516_2025"],
        }
    ]
    assert scan["dedicated_python_2025_candidates_cleanly_separated"] is False
    assert scan["dedicated_python_2025_legacy_package_delegation_violations"] == [
        {
            "package": "hla-backend-python1516-2025",
            "path": "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py",
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
