from __future__ import annotations

from hla2010_repo_internal.verification.python_route_parity_matrix import (
    PYTHON_ROUTE_IDS,
    PYTHON_ROUTE_PARITY_SCENARIOS,
    write_python_route_parity_matrix,
)


def test_python_route_parity_matrix_artifacts_are_generated(tmp_path) -> None:
    csv_path, md_path = write_python_route_parity_matrix(tmp_path)

    assert csv_path.exists()
    assert md_path.exists()
    csv_text = csv_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    assert "scenario,routes,parity_status,evidence_tests,notes" in csv_text
    assert "python-direct; python-grpc" in csv_text
    assert "# Python Route Parity Matrix" in md_text
    assert "target_radar" in md_text

    scenario_names = {scenario.name for scenario in PYTHON_ROUTE_PARITY_SCENARIOS}
    assert {"federation_lifecycle", "object_exchange", "ownership", "target_radar", "time_management"} <= scenario_names
    assert all(scenario.routes == PYTHON_ROUTE_IDS for scenario in PYTHON_ROUTE_PARITY_SCENARIOS)
