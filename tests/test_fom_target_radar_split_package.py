from __future__ import annotations

from pathlib import Path

from hla2010.scenarios import target_radar_fom_path
from hla2010.scenarios.target_radar import run_target_radar_scenario
from hla2010.testing.target_radar_backend_matrix import (
    run_target_radar_backend_matrix,
)
from hla2010.testing.target_radar_proof import run_target_radar_proof
from hla2010_fom_target_radar.scenarios import (
    run_target_radar_scenario as split_run_target_radar_scenario,
)
from hla2010_fom_target_radar.scenarios import target_radar_fom_path as split_target_radar_fom_path
from hla2010_fom_target_radar.testing import (
    run_target_radar_backend_matrix as split_run_target_radar_backend_matrix,
)
from hla2010_fom_target_radar.testing import (
    run_target_radar_proof as split_run_target_radar_proof,
)
from hla2010_fom_target_radar.testing import (
    build_two_federate_target_radar_artifact_summary,
    build_two_federate_target_radar_ddm_config,
    build_profile_artifacts,
    build_two_federate_target_radar_summary,
)


def _ddm_config() -> dict[str, object]:
    return build_two_federate_target_radar_ddm_config()


def test_target_radar_scenario_facade_points_to_split_package() -> None:
    assert run_target_radar_scenario is split_run_target_radar_scenario


def test_target_radar_fom_helper_points_to_split_package_resource() -> None:
    root_path = Path(target_radar_fom_path()).resolve()
    split_path = Path(split_target_radar_fom_path()).resolve()

    assert root_path == split_path
    assert split_path.name == "TargetRadarFOMmodule.xml"
    assert "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/resources/foms" in str(split_path)


def test_target_radar_testing_facades_point_to_split_package() -> None:
    assert run_target_radar_backend_matrix is split_run_target_radar_backend_matrix
    assert run_target_radar_proof is split_run_target_radar_proof


def test_two_federate_target_radar_helper_owns_ddm_config_and_summary() -> None:
    ddm_config = _ddm_config()
    split_ddm_config = build_two_federate_target_radar_ddm_config()
    target_radar_summary = build_two_federate_target_radar_summary(target_radar_steps=2)

    assert ddm_config == split_ddm_config
    assert ddm_config["fom_modules"] == (split_target_radar_fom_path(),)
    assert target_radar_summary["fom_path"] == split_target_radar_fom_path()
    assert target_radar_summary["scenario_row"]["scenario"] == "target_radar"
    assert target_radar_summary["scenario_row"]["key_outcome"] == "2 track reports"


def test_two_federate_target_radar_artifact_summary_owns_reporting_copy() -> None:
    target_radar_summary = build_two_federate_target_radar_summary(target_radar_steps=2)
    artifact_summary = build_two_federate_target_radar_artifact_summary(
        {"target_radar": {"track_reports": [report.as_dict() for report in target_radar_summary["result"].track_reports]}}
    )

    assert artifact_summary["track_report_count"] == 2
    assert artifact_summary["range_chart_title"] == "Target/radar range growth"
    assert "target/radar flow" in artifact_summary["suite_description"]
