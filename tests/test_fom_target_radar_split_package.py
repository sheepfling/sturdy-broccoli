from __future__ import annotations

from pathlib import Path

from hla2010.scenarios import target_radar_fom_path
from hla2010.scenarios.target_radar import run_target_radar_scenario
from hla2010_fom_target_radar.scenarios import (
    run_target_radar_scenario as split_run_target_radar_scenario,
)
from hla2010_fom_target_radar.scenarios import target_radar_fom_path as split_target_radar_fom_path
from hla2010_repo_internal.verification.target_radar_backend_matrix import run_target_radar_backend_matrix
from hla2010_repo_internal.verification.target_radar_proof import run_target_radar_proof


def test_target_radar_scenario_facade_points_to_split_package() -> None:
    assert run_target_radar_scenario is split_run_target_radar_scenario


def test_target_radar_fom_helper_points_to_split_package_resource() -> None:
    root_path = Path(target_radar_fom_path()).resolve()
    split_path = Path(split_target_radar_fom_path()).resolve()

    assert root_path == split_path
    assert split_path.name == "TargetRadarFOMmodule.xml"
    assert "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/resources/foms" in str(split_path)


def test_target_radar_verification_helpers_are_repo_internal() -> None:
    matrix_summary = run_target_radar_backend_matrix(["python"], target_radar_steps=2)
    proof_summary = run_target_radar_proof(["python"], target_radar_steps=2)

    assert matrix_summary["suite_name"] == "target-radar-backend-matrix"
    assert proof_summary["suite_name"] == "target-radar-proof"
    assert proof_summary["proof"]["track_reports"]
