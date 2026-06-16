from __future__ import annotations

from pathlib import Path

from hla.foms.target_radar.scenarios import (
    run_target_radar_scenario as split_run_target_radar_scenario,
)
from hla.foms.target_radar.scenarios import target_radar_fom_path as split_target_radar_fom_path
from hla.verification.repo_internal.verification.target_radar_backend_matrix import run_target_radar_backend_matrix
from hla.verification.repo_internal.verification.target_radar_proof import run_target_radar_proof


def test_target_radar_scenario_uses_package_owned_entrypoint() -> None:
    assert split_run_target_radar_scenario.__module__.startswith("hla.foms.target_radar.scenarios")


def test_target_radar_fom_helper_points_to_package_owned_resource() -> None:
    split_path = Path(split_target_radar_fom_path()).resolve()
    assert split_path.name == "TargetRadarFOMmodule.xml"
    assert "packages/hla-fom-target-radar/src/hla/foms/target_radar/resources/foms" in str(split_path)


def test_target_radar_verification_helpers_are_repo_internal() -> None:
    matrix_summary = run_target_radar_backend_matrix(["python"], target_radar_steps=2)
    proof_summary = run_target_radar_proof(["python"], target_radar_steps=2)

    assert matrix_summary["suite_name"] == "target-radar-backend-matrix"
    assert proof_summary["suite_name"] == "target-radar-proof"
    assert proof_summary["proof"]["track_reports"]
