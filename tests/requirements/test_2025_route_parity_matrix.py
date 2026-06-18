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
    assert "logical time/GALT/LITS/lookahead queries" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert rows[("ownership", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("ownership", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "negotiated divestiture" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "resign-time divest/delete/cancel ownership policies" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert rows[("ddm", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("ddm", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "interaction class region-overlap filtering" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert "conveyed region evidence" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert "delete-region cleanup" in rows[("ddm", "python-2025-fedpro-grpc")].notes
    assert rows[("mom", "python-2025-fedpro-grpc")].status == PARTIAL
    assert "round-trips 2025 switch services" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports MIM data for HLArequestMIMdata" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports object publication/subscription state" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "reports activity counts for updates/reflections/interactions" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert "not full MOM manager object/interaction routing" in rows[("mom", "python-2025-fedpro-grpc")].notes
    assert rows[("support_services", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("support_services", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "2025 switch get/set services" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert "logical-time query" in rows[("support_services", "python-2025-fedpro-grpc")].notes
    assert rows[("save_restore", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("save_restore", "python-2025-fedpro-grpc")].evidence_scope == "scenario-parity"
    assert "status callbacks" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "object registry rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "logical-time rollback" in rows[("save_restore", "python-2025-fedpro-grpc")].notes

    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        assert rows[("object_exchange", route)].status == MISSING
        assert rows[("object_exchange", route)].evidence_scope == "gap-record"
        assert rows[("object_exchange", route)].evidence_artifacts == ()
        assert rows[("ownership", route)].status == MISSING
        assert rows[("ddm", route)].status == MISSING
        assert rows[("time_management", route)].status == MISSING


def test_2025_route_parity_matrix_records_evidence_scope_without_flattening_java_cpp() -> None:
    rows = {(row.scenario, row.route): row for row in SPEC2025_ROUTE_PARITY_ROWS}

    java_lifecycle = rows[("federation_lifecycle", "java-standard-2025-jpype")]
    cpp_lifecycle = rows[("federation_lifecycle", "cpp-standard-2025-grpc")]

    assert java_lifecycle.status == PARTIAL
    assert java_lifecycle.evidence_scope == "runtime-capability"
    assert "docs/evidence/shim_routes/java-standard-2025.json" in java_lifecycle.evidence_artifacts
    assert "docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json" in java_lifecycle.evidence_artifacts

    assert cpp_lifecycle.status == PARTIAL
    assert cpp_lifecycle.evidence_scope == "lifecycle-trace"
    assert "docs/evidence/shim_routes/cpp-standard-2025.json" in cpp_lifecycle.evidence_artifacts
    assert "docs/evidence/shim_routes/route_traces/cpp-standard-2025-grpc.json" in cpp_lifecycle.evidence_artifacts

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
    assert summary["by_status"][PARTIAL] > 0
    assert summary["by_status"][MISSING] > 0
    assert summary["by_route"]["java-standard-2025-jpype"][PARITY_COVERED] == 0
    assert summary["by_route"]["cpp-standard-2025-grpc"][PARITY_COVERED] == 0

    csv_path, md_path = write_spec2025_route_parity_matrix(tmp_path)
    assert csv_path.exists()
    assert md_path.exists()
    csv_text = csv_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    assert "scenario,route,status,evidence_scope,requirements,evidence_tests,evidence_artifacts,notes" in csv_text
    assert "object_exchange,java-standard-2025-jpype,missing,gap-record" in csv_text
    assert "save_restore,python-2025-fedpro-grpc,parity-covered,scenario-parity" in csv_text
    assert "# IEEE 1516-2025 Route Parity Matrix" in md_text
    assert "This matrix is not a conformance claim" in md_text
    assert "| Scenario | Route | Status | Evidence scope |" in md_text
