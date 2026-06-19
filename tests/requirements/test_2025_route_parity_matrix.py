from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.verification.spec2025_route_parity_matrix import (
    MISSING,
    PARITY_COVERED,
    PARTIAL,
    ROUTE_IDS_2025,
    SPEC2025_ROUTE_PARITY_ROWS,
    Spec2025RouteParityRow,
    summarize_spec2025_route_parity,
    validate_spec2025_route_parity_evidence,
    write_spec2025_route_parity_matrix,
)

ROOT = Path(__file__).resolve().parents[2]


def test_2025_route_parity_matrix_enumerates_every_required_route_per_scenario() -> None:
    scenarios = {row.scenario for row in SPEC2025_ROUTE_PARITY_ROWS}

    assert {
        "federation_lifecycle",
        "object_exchange",
        "ownership",
        "ddm",
        "time_management",
        "save_restore",
        "mom",
        "support_services",
    } <= scenarios
    for scenario in scenarios:
        assert {row.route for row in SPEC2025_ROUTE_PARITY_ROWS if row.scenario == scenario} == set(ROUTE_IDS_2025)


def test_2025_route_parity_matrix_keeps_java_and_cpp_behavior_unpromoted() -> None:
    rows = {(row.scenario, row.route): row for row in SPEC2025_ROUTE_PARITY_ROWS}

    assert rows[("object_exchange", "python-2025-inprocess")].status == PARITY_COVERED
    assert rows[("object_exchange", "python-2025-inprocess")].evidence_scope == "scenario-parity"
    assert rows[("object_exchange", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("object_exchange", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert rows[("time_management", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("time_management", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "TAR/TARA/NMR/NMRA/FQR grants" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "queued TSO delivery" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "logical time/GALT/LITS/lookahead query evidence" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, save-restore-output-resume, and save-restore-pipeline-resume proofs" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert rows[("time_management", "python-2025-inprocess")].evidence_tests == (
        "tests/test_rti1516_2025_spec_and_shim.py",
        "tests/scenarios/test_python_route_parity.py",
    )
    assert rows[("time_management", "python-2025-fedpro-grpc")].evidence_tests == (
        "tests/transport/test_grpc_transport_2025.py",
        "tests/scenarios/test_python_route_parity.py",
    )
    assert rows[("ownership", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("ownership", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "negotiated divestiture" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "resign-time divest/delete/cancel ownership policies" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert rows[("ddm", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("ddm", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "interaction class, and directed interaction region-overlap filtering" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert "conveyed region evidence" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert "delete-region cleanup" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert rows[("mom", "python-2025-inprocess")].status == PARITY_COVERED
    assert rows[("mom", "python-2025-inprocess")].evidence_scope == "scenario-parity"
    assert "routes MIM data, FOM module data" in rows[("mom", "python-2025-inprocess")].notes
    assert "synchronization point MOM request/report interactions" in rows[("mom", "python-2025-inprocess")].notes
    assert "service/exception reporting MOM adjust interactions" in rows[("mom", "python-2025-inprocess")].notes
    assert "exposed HLAsetSwitches adjust interactions" in rows[("mom", "python-2025-inprocess")].notes
    assert "HLAsetTiming/HLAmodifyAttributeState adjust interactions" in rows[("mom", "python-2025-inprocess")].notes
    assert "federate-level FOM module data, publication/subscription, and object-instance information MOM reports" in rows[
        ("mom", "python-2025-inprocess")
    ].notes
    assert "declaration-management MOM service actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "federation-management MOM service actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "supported time-management MOM service actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "disable/asynchronous/TARA/NMR/NMRA" in rows[("mom", "python-2025-inprocess")].notes
    assert "supported object-management MOM service actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "transportation/order-type changes" in rows[("mom", "python-2025-inprocess")].notes
    assert "supported ownership MOM service actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "activity/count MOM reports" in rows[("mom", "python-2025-inprocess")].notes
    assert "MOM exception reports for failed routed MOM actions" in rows[("mom", "python-2025-inprocess")].notes
    assert "every non-report manager command leaf in the bundled MIM is declared routed" in rows[
        ("mom", "python-2025-inprocess")
    ].notes
    assert rows[("mom", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("mom", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "round-trips 2025 switch services" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "routes all hosted MOM manager adjust/service command leaves" in rows[
        ("mom", "python-2025-fedpro-grpc")
    ].notes
    assert "reports MIM data for HLArequestMIMdata" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports FOM module data for HLArequestFOMmoduleData" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports object publication/subscription state" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports object instance information" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "object-instance counts" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports activity counts for updates/reflections/interactions" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports synchronization points/status" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert rows[("support_services", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("support_services", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "2025 switch get/set plus read-only switch inquiry services" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert "logical-time query" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert rows[("save_restore", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("save_restore", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "status callbacks" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "object registry rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "logical-time rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "bounded radar-window state rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes

    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        assert rows[("object_exchange", route)].status == PARITY_COVERED
        assert rows[("object_exchange", route)].evidence_scope == "scenario-parity"
        assert rows[("object_exchange", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "two-federate object exchange trace" in rows[("object_exchange", route)].notes

    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        assert rows[("ownership", route)].status == PARITY_COVERED
        assert rows[("ownership", route)].evidence_scope == "scenario-parity"
        assert rows[("ownership", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "ownership runtime trace" in rows[("ownership", route)].notes
        assert "unavailable acquisition while owned" in rows[("ownership", route)].notes
        assert rows[("ddm", route)].status == PARITY_COVERED
        assert rows[("ddm", route)].evidence_scope == "scenario-parity"
        assert rows[("ddm", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "DDM region runtime trace" in rows[("ddm", route)].notes
        assert "outside-region suppression" in rows[("ddm", route)].notes
        assert rows[("time_management", route)].status == PARITY_COVERED
        assert rows[("time_management", route)].evidence_scope == "scenario-parity"
        assert rows[("time_management", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "logical-time runtime trace" in rows[("time_management", route)].notes
        assert rows[("support_services", route)].status == PARITY_COVERED
        assert rows[("support_services", route)].evidence_scope == "scenario-parity"
        assert rows[("support_services", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "support-services runtime trace" in rows[("support_services", route)].notes
        assert "2025 switch round trips" in rows[("support_services", route)].notes
        assert rows[("save_restore", route)].status == PARITY_COVERED
        assert rows[("save_restore", route)].evidence_scope == "scenario-parity"
        assert rows[("save_restore", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "save/restore runtime trace" in rows[("save_restore", route)].notes
        assert "logical-time rollback" in rows[("save_restore", route)].notes
        assert rows[("mom", route)].status == PARITY_COVERED
        assert rows[("mom", route)].evidence_scope == "scenario-parity"
        assert rows[("mom", route)].evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
        assert "MOM runtime trace" in rows[("mom", route)].notes
        assert "MIM data report" in rows[("mom", route)].notes


def test_2025_route_parity_matrix_records_evidence_scope_without_flattening_java_cpp() -> None:
    rows = {(row.scenario, row.route): row for row in SPEC2025_ROUTE_PARITY_ROWS}

    java_lifecycle = rows[("federation_lifecycle", "java-standard-2025-jpype")]
    cpp_lifecycle = rows[("federation_lifecycle", "cpp-standard-2025-grpc")]

    assert java_lifecycle.status == PARITY_COVERED
    assert java_lifecycle.evidence_scope == "scenario-parity"
    assert java_lifecycle.evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
    assert "official API compile artifact gate" in java_lifecycle.notes

    assert cpp_lifecycle.status == PARITY_COVERED
    assert cpp_lifecycle.evidence_scope == "scenario-parity"
    assert cpp_lifecycle.evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
    assert "connect, create, join" in cpp_lifecycle.notes

    for row in SPEC2025_ROUTE_PARITY_ROWS:
        if row.evidence_scope == "gap-record":
            assert row.status == MISSING
            assert row.evidence_artifacts == ()
        if row.evidence_artifacts:
            for artifact in row.evidence_artifacts:
                if artifact.startswith("docs/"):
                    assert (ROOT / artifact).exists(), artifact


def test_2025_route_parity_matrix_validates_machine_readable_evidence_scope() -> None:
    assert validate_spec2025_route_parity_evidence(ROOT) == []


def test_2025_route_parity_matrix_rejects_runtime_claim_without_runtime_artifact() -> None:
    bad_row = Spec2025RouteParityRow(
        scenario="federation_lifecycle",
        route="java-standard-2025-jpype",
        status=PARTIAL,
        requirements=("HLA2025-BND-001",),
        evidence_tests=("tests/backends/test_shim_route_trace_evidence.py",),
        notes="Bad fixture: lifecycle trace alone is not runtime capability evidence.",
        evidence_scope="runtime-capability",
        evidence_artifacts=("docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",),
    )

    errors = validate_spec2025_route_parity_evidence(ROOT, (bad_row,))

    assert errors == [
        "federation_lifecycle/java-standard-2025-jpype: runtime-capability rows require aggregate Java route evidence"
    ]


def test_2025_route_parity_matrix_rejects_missing_rows_with_artifacts() -> None:
    bad_row = Spec2025RouteParityRow(
        scenario="object_exchange",
        route="cpp-standard-2025-grpc",
        status=MISSING,
        requirements=("HLA2025-BND-002",),
        evidence_tests=("tests/requirements/test_2025_finish_line_snapshot.py",),
        notes="Bad fixture: a missing row cannot imply supporting evidence.",
        evidence_scope="gap-record",
        evidence_artifacts=("docs/evidence/shim_routes/route_traces/cpp-standard-2025-grpc.json",),
    )

    assert validate_spec2025_route_parity_evidence(ROOT, (bad_row,)) == [
        "object_exchange/cpp-standard-2025-grpc: missing rows must not carry evidence artifacts"
    ]


def test_2025_route_parity_summary_and_artifacts_are_reviewable(tmp_path) -> None:
    summary = summarize_spec2025_route_parity()

    assert summary["routes"] == ROUTE_IDS_2025
    assert summary["scenario_count"] >= 8
    assert summary["by_status"][PARITY_COVERED] > 0
    assert summary["by_status"][PARTIAL] == 0
    assert summary["by_status"][MISSING] == 0
    assert summary["by_route"]["java-standard-2025-jpype"][PARITY_COVERED] == 8
    assert summary["by_route"]["cpp-standard-2025-grpc"][PARITY_COVERED] == 8

    csv_path, md_path = write_spec2025_route_parity_matrix(tmp_path)
    assert csv_path.exists()
    assert md_path.exists()
    csv_text = csv_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    assert "scenario,route,status,evidence_scope,requirements,evidence_tests,evidence_artifacts,notes" in csv_text
    assert "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity" in csv_text
    assert "save_restore,python-2025-fedpro-grpc,parity-covered,scenario-parity" in csv_text
    assert "# IEEE 1516-2025 Route Parity Matrix" in md_text
    assert "This matrix is not a conformance claim" in md_text
    assert "| Scenario | Route | Status | Evidence scope |" in md_text
