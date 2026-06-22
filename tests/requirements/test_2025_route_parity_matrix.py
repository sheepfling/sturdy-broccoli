from __future__ import annotations

from pathlib import Path
import json

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

    for route in ROUTE_IDS_2025:
        for scenario in {row.scenario for row in SPEC2025_ROUTE_PARITY_ROWS if row.route == route}:
            row = rows[(scenario, route)]
            assert row.runtime_provider == "python2025"
            assert row.implementation_lane == "hla-backend-python2025"
            assert row.counts_as_python_2025_rti is route.startswith("python-2025")
            assert row.wrapper_only is False

    assert rows[("object_exchange", "python-2025-inprocess")].status == PARITY_COVERED
    assert rows[("object_exchange", "python-2025-inprocess")].evidence_scope == "scenario-parity"
    assert rows[("object_exchange", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("object_exchange", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert rows[("federation_lifecycle", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("federation_lifecycle", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "createFederationExecutionWithMIM" in rows[("federation_lifecycle", "python-2025-inprocess")].notes
    assert "explicit single-FOM and createFederationExecutionWithMIM transport-command routing" in rows[
        ("federation_lifecycle", "python-2025-fedpro-grpc")
    ].notes
    assert "direct ambassador, hosted server, and hosted client all identify python2025 / hla-backend-python2025 as the primary 2025 Python RTI implementation lane" in rows[
        ("federation_lifecycle", "python-2025-fedpro-grpc")
    ].notes
    assert rows[("time_management", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("time_management", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "TAR/TARA/NMR/NMRA/FQR grants" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "queued TSO delivery" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "logical time/GALT/LITS/lookahead query evidence" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "main python2025-backed FedPro route" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of the package-owned future-exclusion, output-delivery, consumer-order, integrated lookahead-processing-window gauntlet, and restore-state scenario adapter paths" in rows[
        ("time_management", "python-2025-fedpro-grpc")
    ].notes
    assert "Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "save-restore lookahead rollback with queued-TSO redelivery" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "oracle-rejection guards" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of MOM federation-management save/restore service interactions" in rows[
        ("mom", "python-2025-fedpro-grpc")
    ].notes
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of the shared support factory/decode scenario plus automatic-resign get/set, multiple-name reservation callbacks, object-instance name lookup, and queued reflection release on re-enabled callbacks" in rows[
        ("support_services", "python-2025-fedpro-grpc")
    ].notes
    assert "future-exclusion blocking until GALT/LITS reach the window end" in rows[("time_management", "python-2025-inprocess")].notes
    assert "oracle-rejection guards" in rows[("time_management", "python-2025-inprocess")].notes
    assert rows[("time_management", "python-2025-inprocess")].evidence_tests == (
        "tests/test_rti1516_2025_spec_and_shim.py",
        "tests/scenarios/test_python_route_parity.py",
    )
    assert rows[("time_management", "python-2025-fedpro-grpc")].evidence_tests == (
        "tests/transport/test_grpc_transport_2025.py",
        "tests/scenarios/test_python_route_parity.py",
    )
    assert rows[("time_management", "python-2025-fedpro-grpc")].evidence_artifacts == (
        "tests/transport/test_grpc_transport_2025.py",
        "docs/plans/spec2025_finish_line_snapshot.json",
    )
    assert rows[("ownership", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("ownership", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "in-flight ownership negotiation state" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "owner-visibility callbacks" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "direct 2025 ambassador surface" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "smoke save/restore ownership rollback gauntlet" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "negotiated divestiture" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "resign-time divest/delete/cancel ownership policies" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "in-flight acquisition/divestiture state" in rows[("ownership", "python-2025-inprocess")].notes
    assert "owner-visibility recovery" in rows[("ownership", "python-2025-inprocess")].notes
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
    assert rows[("support_services", "python-2025-inprocess")].status == PARITY_COVERED
    assert rows[("support_services", "python-2025-inprocess")].evidence_scope == "scenario-parity"
    assert "FOM handle/name round trips" in rows[("support_services", "python-2025-inprocess")].notes
    assert "raw support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in rows[
        ("support_services", "python-2025-inprocess")
    ].notes
    assert "snake-case alias acceptance on the primary direct-runtime surface" in rows[
        ("support_services", "python-2025-inprocess")
    ].notes
    assert "transportation/order lookups" in rows[("support_services", "python-2025-inprocess")].notes
    assert "automatic resign directive get/set round trips" in rows[("support_services", "python-2025-inprocess")].notes
    assert "raw callback-delivery enable/disable and evoke callback control with queued discovery/reflection release" in rows[
        ("support_services", "python-2025-inprocess")
    ].notes
    assert "single/multiple object-instance name reservation/release callback flow" in rows[
        ("support_services", "python-2025-inprocess")
    ].notes
    assert "2025 switch get/set plus read-only switch inquiry services" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert "logical-time query" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert "reconnect-safe discard of a disconnected peer's disabled callback backlog before later reconnect" in rows[
        ("support_services", "python-2025-fedpro-grpc")
    ].notes
    assert "single and multiple object-instance name reservation/release callback flow" in rows[
        ("support_services", "python-2025-fedpro-grpc")
    ].notes
    assert "turnUpdatesOn/turnUpdatesOff advisory callback flow" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert "automatic resign directive get/set" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert rows[("save_restore", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("save_restore", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "status callbacks" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "object registry rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "logical-time rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "time/switch-control rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "restore precondition/failure/abort plus restore participant/status exception control flow" in rows[
        ("save_restore", "python-2025-fedpro-grpc")
    ].notes
    assert "local-delete object-known-state recovery" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "transportation-type restore persistence" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "queued-TSO redelivery after restore" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "factory-hosted create_rti_ambassador('python2025', transport=...) execution of the package-owned restore-state, restore-output-resume, and pipeline-resume scenario adapter paths" in rows[
        ("save_restore", "python-2025-fedpro-grpc")
    ].notes
    assert "bounded radar-window state rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "plain object/interaction subscriber-routing rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "directed DDM subscriber-routing rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "callback-delivery runtime-policy preservation" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "plain object/interaction subscriber-routing rollback" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "saved lookahead recovery" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "transportation-type restore persistence" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "restore failure/abort plus restore-precondition/participant/status negative control flow" in rows[
        ("save_restore", "python-2025-inprocess")
    ].notes
    assert "local-delete object-known-state recovery" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "exact status-clear transitions back to NO_SAVE_IN_PROGRESS/NO_RESTORE_IN_PROGRESS" in rows[("save_restore", "python-2025-inprocess")].notes
    assert "full initiate/save/restore callback contracts" in rows[("save_restore", "python-2025-inprocess")].notes
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
    assert "primary python2025 runtime lane in hla-backend-python2025" in java_lifecycle.notes

    assert cpp_lifecycle.status == PARITY_COVERED
    assert cpp_lifecycle.evidence_scope == "scenario-parity"
    assert cpp_lifecycle.evidence_tests == ("tests/backends/test_standard_shim_artifacts.py",)
    assert "connect, create, join" in cpp_lifecycle.notes
    assert "packages limited to compatibility and API adaptation" in cpp_lifecycle.notes
    assert "binding/adaptation-seam evidence over the main hla-backend-python2025 runtime" in cpp_lifecycle.notes

    hosted_lifecycle = rows[("federation_lifecycle", "python-2025-fedpro-grpc")]
    assert "transport-seam evidence over hla-backend-python2025" in hosted_lifecycle.notes


def test_2025_route_parity_matrix_never_credits_shim_as_a_2025_route_runtime_owner() -> None:
    for row in SPEC2025_ROUTE_PARITY_ROWS:
        assert row.runtime_provider != "shim"
        assert row.implementation_lane != "hla-backend-shim"
        if row.route in ROUTE_IDS_2025:
            assert row.wrapper_only is False

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
        runtime_provider="python2025",
        implementation_lane="hla-backend-python2025",
        counts_as_python_2025_rti=False,
        wrapper_only=False,
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
        runtime_provider="python2025",
        implementation_lane="hla-backend-python2025",
        counts_as_python_2025_rti=False,
        wrapper_only=False,
    )

    assert validate_spec2025_route_parity_evidence(ROOT, (bad_row,)) == [
        "object_exchange/cpp-standard-2025-grpc: missing rows must not carry evidence artifacts"
    ]


def test_2025_route_parity_matrix_rejects_trace_without_python2025_runtime_identity(tmp_path) -> None:
    trace_path = tmp_path / "docs" / "evidence" / "shim_routes" / "route_traces" / "java-standard-2025-jpype.json"
    trace_path.parent.mkdir(parents=True)
    trace_path.write_text(
        json.dumps(
            {
                "route": "java-standard-2025-jpype",
                "edition": "2025",
                "scenario": "lifecycle-core",
                "status": "lifecycle-green",
                "trace": [
                    {
                        "event": "routeSelected",
                        "backend": "java-standard-2025-jpype",
                        "spec": "rti1516_2025",
                        "standardBacked": True,
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    bad_row = Spec2025RouteParityRow(
        scenario="federation_lifecycle",
        route="java-standard-2025-jpype",
        status=PARTIAL,
        requirements=("HLA2025-BND-001",),
        evidence_tests=("tests/backends/test_standard_shim_artifacts.py",),
        notes="Bad fixture: trace omits backing runtime identity.",
        evidence_scope="lifecycle-trace",
        evidence_artifacts=("docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",),
        runtime_provider="python2025",
        implementation_lane="hla-backend-python2025",
        counts_as_python_2025_rti=False,
        wrapper_only=False,
    )

    assert validate_spec2025_route_parity_evidence(tmp_path, (bad_row,)) == [
        "federation_lifecycle/java-standard-2025-jpype: route trace must record runtimeProvider=python2025 in docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",
        "federation_lifecycle/java-standard-2025-jpype: route trace must record implementationLane=hla-backend-python2025 in docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",
        "federation_lifecycle/java-standard-2025-jpype: route trace must record countsAsPython2025Rti=false in docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",
        "federation_lifecycle/java-standard-2025-jpype: route trace must record wrapperOnly=false in docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json",
    ]


def test_2025_route_parity_matrix_rejects_aggregate_report_without_python2025_runtime_identity(tmp_path) -> None:
    report_path = tmp_path / "docs" / "evidence" / "shim_routes" / "java-standard-2025.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
        json.dumps(
            {
                "scenario_evidence": {
                    "status": "scenario-parity-green",
                    "scope": "bounded scenario-parity evidence, not full Java RTI conformance",
                    "tests": [],
                    "scenarios": [],
                },
                "routes": {
                    "java-standard-2025-jpype": {
                        "status": "trace-green",
                        "surface": "official Java 2025 API",
                        "scenario": "runtime-capability",
                        "parity_scope": "bounded scenario-parity evidence",
                        "requirements_exercised": ["HLA2025-BND-001"],
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    bad_row = Spec2025RouteParityRow(
        scenario="federation_lifecycle",
        route="java-standard-2025-jpype",
        status=PARTIAL,
        requirements=("HLA2025-BND-001",),
        evidence_tests=("tests/backends/test_standard_shim_artifacts.py",),
        notes="Bad fixture: aggregate report omits backing runtime identity.",
        evidence_scope="runtime-capability",
        evidence_artifacts=("docs/evidence/shim_routes/java-standard-2025.json",),
        runtime_provider="python2025",
        implementation_lane="hla-backend-python2025",
        counts_as_python_2025_rti=False,
        wrapper_only=False,
    )

    assert validate_spec2025_route_parity_evidence(tmp_path, (bad_row,)) == [
        "federation_lifecycle/java-standard-2025-jpype: Java aggregate route evidence must record runtime_provider=python2025",
        "federation_lifecycle/java-standard-2025-jpype: Java aggregate route evidence must record implementation_lane=hla-backend-python2025",
        "federation_lifecycle/java-standard-2025-jpype: Java aggregate route evidence must record wrapper_only=false",
        "federation_lifecycle/java-standard-2025-jpype: Java aggregate route evidence must record counts_as_python_2025_rti=false",
        "federation_lifecycle/java-standard-2025-jpype: Java route evidence must record runtime_provider=python2025",
        "federation_lifecycle/java-standard-2025-jpype: Java route evidence must record implementation_lane=hla-backend-python2025",
        "federation_lifecycle/java-standard-2025-jpype: Java route evidence must record wrapper_only=false",
        "federation_lifecycle/java-standard-2025-jpype: Java route evidence must record counts_as_python_2025_rti=false",
    ]


def test_2025_route_parity_summary_and_artifacts_are_reviewable(tmp_path) -> None:
    summary = summarize_spec2025_route_parity()

    assert summary["routes"] == ROUTE_IDS_2025
    assert summary["scenario_count"] >= 8
    assert summary["by_status"][PARITY_COVERED] > 0
    assert summary["by_status"][PARTIAL] == 0
    assert summary["by_status"][MISSING] == 0
    assert summary["primary_runtime_lane"] == {
        "runtime_provider": "python2025",
        "implementation_lane": "hla-backend-python2025",
        "counts_as_python_2025_rti": True,
        "wrapper_only": False,
    }
    assert summary["compatibility_wrapper_lane"] == {
        "backend_package": "hla-backend-shim",
        "status": "compatibility-maintained",
        "role": "compatibility-wrapper",
        "counts_as_python_2025_rti": False,
        "delegates_runtime_semantics_to": "hla-backend-python2025",
    }
    assert summary["by_route"]["java-standard-2025-jpype"][PARITY_COVERED] == 8
    assert summary["by_route"]["cpp-standard-2025-grpc"][PARITY_COVERED] == 8

    csv_path, md_path = write_spec2025_route_parity_matrix(tmp_path)
    assert csv_path.exists()
    assert md_path.exists()
    csv_text = csv_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    assert (
        "scenario,route,status,evidence_scope,requirements,evidence_tests,evidence_artifacts,"
        "runtime_provider,implementation_lane,counts_as_python_2025_rti,wrapper_only,notes"
    ) in csv_text
    assert "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity" in csv_text
    assert "save_restore,python-2025-fedpro-grpc,parity-covered,scenario-parity" in csv_text
    assert "docs/plans/spec2025_finish_line_snapshot.json" in csv_text
    assert "# IEEE 1516-2025 Route Parity Matrix" in md_text
    assert "This matrix is not a conformance claim" in md_text
    assert "`hla-backend-shim` is a compatibility-maintained wrapper package that delegates runtime semantics to `hla-backend-python2025`" in md_text
    assert "Java/C++ standard routes are binding/adaptation-seam evidence over that same runtime" in md_text
    assert "Hosted FedPro rows are transport-seam evidence over that same runtime" in md_text
    assert "For the main-implementation claim, read the scenario rows as a proof-family ledger too:" in md_text
    assert "the Python-owned rows below are the main route-parity proof families for federation, object, ownership, DDM, time, save/restore, MOM, and support-services behavior" in md_text
    assert "Java/C++ rows show binding/adaptation seam coverage without transferring implementation ownership away from `hla-backend-python2025`" in md_text
    assert "hosted FedPro rows show transport-seam replay of those same runtime families rather than a different 2025 RTI owner" in md_text
    assert "| Scenario | Route | Status | Evidence scope | Requirements | Evidence tests | Evidence artifacts | Runtime provider | Implementation lane | Counts as primary Python 2025 RTI | Wrapper only | Notes |" in md_text
    assert "direct ambassador, hosted server, and hosted client all identify python2025 / hla-backend-python2025 as the primary 2025 Python RTI implementation lane" in md_text
    assert "Treat remaining hosted FedPro proof here as transport-seam evidence over hla-backend-python2025" in md_text
    assert "Treat Java/C++ route parity here as binding/adaptation-seam evidence over the main hla-backend-python2025 runtime" in md_text


def test_2025_checked_in_route_parity_plan_artifacts_preserve_python2025_identity() -> None:
    csv_text = (ROOT / "docs" / "plans" / "spec2025_route_parity_matrix.csv").read_text(encoding="utf-8")
    md_text = (ROOT / "docs" / "plans" / "spec2025_route_parity_matrix.md").read_text(encoding="utf-8")

    assert (
        "scenario,route,status,evidence_scope,requirements,evidence_tests,evidence_artifacts,"
        "runtime_provider,implementation_lane,counts_as_python_2025_rti,wrapper_only,notes"
    ) in csv_text
    assert "federation_lifecycle,python-2025-inprocess,parity-covered,scenario-parity" in csv_text
    assert "time_management,python-2025-fedpro-grpc,parity-covered,scenario-parity" in csv_text
    assert ",python2025,hla-backend-python2025,true,false," in csv_text
    assert "docs/plans/spec2025_finish_line_snapshot.json" in csv_text

    assert "| Scenario | Route | Status | Evidence scope | Requirements | Evidence tests | Evidence artifacts | Runtime provider | Implementation lane | Counts as primary Python 2025 RTI | Wrapper only | Notes |" in md_text
    assert "`hla-backend-shim` is a compatibility-maintained wrapper package that delegates runtime semantics to `hla-backend-python2025`" in md_text
    assert "Java/C++ standard routes are binding/adaptation-seam evidence over that same runtime" in md_text
    assert "Hosted FedPro rows are transport-seam evidence over that same runtime" in md_text
    assert "For the main-implementation claim, read the scenario rows as a proof-family ledger too:" in md_text
    assert "the Python-owned rows below are the main route-parity proof families for federation, object, ownership, DDM, time, save/restore, MOM, and support-services behavior" in md_text
    assert "Java/C++ rows show binding/adaptation seam coverage without transferring implementation ownership away from `hla-backend-python2025`" in md_text
    assert "hosted FedPro rows show transport-seam replay of those same runtime families rather than a different 2025 RTI owner" in md_text
    assert "| federation_lifecycle | python-2025-inprocess | parity-covered | scenario-parity |" in md_text
    assert "| time_management | python-2025-fedpro-grpc | parity-covered | scenario-parity |" in md_text
    assert "| python2025 | hla-backend-python2025 | true | false |" in md_text
    assert "direct ambassador, hosted server, and hosted client all identify python2025 / hla-backend-python2025 as the primary 2025 Python RTI implementation lane" in md_text
    assert "Treat remaining hosted FedPro proof here as transport-seam evidence over hla-backend-python2025" in md_text
    assert "Treat Java/C++ route parity here as binding/adaptation-seam evidence over the main hla-backend-python2025 runtime" in md_text


def test_2025_checked_in_route_parity_artifacts_match_live_writer(tmp_path) -> None:
    csv_path, md_path = write_spec2025_route_parity_matrix(tmp_path)
    checked_in_dir = ROOT / "docs" / "plans"

    generated_csv_text = csv_path.read_text(encoding="utf-8")
    generated_md_text = md_path.read_text(encoding="utf-8")
    checked_in_csv_text = (checked_in_dir / "spec2025_route_parity_matrix.csv").read_text(encoding="utf-8")
    checked_in_md_text = (checked_in_dir / "spec2025_route_parity_matrix.md").read_text(encoding="utf-8")

    assert generated_csv_text == checked_in_csv_text, "checked-in generated artifact drifted: spec2025_route_parity_matrix.csv"
    assert generated_md_text == checked_in_md_text, "checked-in generated artifact drifted: spec2025_route_parity_matrix.md"


def test_2025_route_parity_matrix_rejects_python_route_rows_without_main_runtime_identity() -> None:
    bad_row = Spec2025RouteParityRow(
        scenario="time_management",
        route="python-2025-fedpro-grpc",
        status=PARITY_COVERED,
        requirements=("HLA2025-FR-010",),
        evidence_tests=("tests/transport/test_grpc_transport_2025.py",),
        notes="Bad fixture: python route row should not regress to shim identity.",
        evidence_scope="scenario-parity",
        evidence_artifacts=("tests/transport/test_grpc_transport_2025.py",),
        runtime_provider="shim",
        implementation_lane="hla-backend-shim",
        counts_as_python_2025_rti=False,
        wrapper_only=True,
    )

    assert validate_spec2025_route_parity_evidence(ROOT, (bad_row,)) == [
        "time_management/python-2025-fedpro-grpc: parity row must record runtime_provider=python2025",
        "time_management/python-2025-fedpro-grpc: parity row must record implementation_lane=hla-backend-python2025",
        "time_management/python-2025-fedpro-grpc: parity row must record counts_as_python_2025_rti=true",
        "time_management/python-2025-fedpro-grpc: parity row must record wrapper_only=false",
    ]
