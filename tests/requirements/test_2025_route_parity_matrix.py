from __future__ import annotations

from hla.verification.repo_internal.verification.spec2025_route_parity_matrix import (
    MISSING,
    PARITY_COVERED,
    PARTIAL,
    ROUTE_IDS_2025,
    SPEC2025_ROUTE_PARITY_ROWS,
    summarize_spec2025_route_parity,
    write_spec2025_route_parity_matrix,
)


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
    assert rows[("object_exchange", "python-2025-fedpro-grpc")].status == PARITY_COVERED
    assert rows[("time_management", "python-2025-fedpro-grpc")].status == PARTIAL
    assert "queued TSO delivery" in rows[("time_management", "python-2025-fedpro-grpc")].notes
    assert rows[("ownership", "python-2025-fedpro-grpc")].status == PARTIAL
    assert "negotiated divestiture" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert "resign-time ownership policy remains in-process only" in rows[("ownership", "python-2025-fedpro-grpc")].notes
    assert rows[("save_restore", "python-2025-fedpro-grpc")].status == PARTIAL
    assert "status callbacks" in rows[("save_restore", "python-2025-fedpro-grpc")].notes
    assert "rollback remains in-process only" in rows[("save_restore", "python-2025-fedpro-grpc")].notes

    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        assert rows[("object_exchange", route)].status == MISSING
        assert rows[("ownership", route)].status == MISSING
        assert rows[("ddm", route)].status == MISSING
        assert rows[("time_management", route)].status == MISSING


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

    assert "scenario,route,status,requirements,evidence_tests,notes" in csv_text
    assert "object_exchange,java-standard-2025-jpype,missing" in csv_text
    assert "save_restore,python-2025-fedpro-grpc,partial" in csv_text
    assert "# IEEE 1516-2025 Route Parity Matrix" in md_text
    assert "This matrix is not a conformance claim" in md_text
