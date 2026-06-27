from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.siso_runtime_surface_matrix import (
    build_siso_runtime_surface_matrix_manifest,
    write_siso_runtime_surface_matrix_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


def test_siso_runtime_surface_matrix_manifest_explicit() -> None:
    manifest = build_siso_runtime_surface_matrix_manifest()

    assert manifest["schema_version"] == "siso-runtime-surface-matrix-v0.1"
    assert manifest["scenario_count"] == 18
    assert manifest["row_count"] == 54
    assert manifest["surface_profiles"] == [
        "runtime-only",
        "observer-visualizer",
        "observer-visualizer-bridge",
    ]
    by_row = {row["matrix_row_id"]: row for row in manifest["rows"]}
    assert by_row["link16-rpr2-integrated-2010-micro-2::runtime-only"]["includes_observer_api"] is False
    assert by_row["link16-rpr2-integrated-2010-micro-2::observer-visualizer"]["includes_visualizer_html"] is True
    assert by_row["link16-rpr2-integrated-2010-micro-2::observer-visualizer-bridge"]["includes_federate_service_api"] is True


def test_siso_runtime_surface_matrix_presets_select_expected_rows() -> None:
    manifest = build_siso_runtime_surface_matrix_manifest(presets=["showcase-hydrated"])

    assert manifest["presets"] == ["showcase-hydrated"]
    assert manifest["surface_profiles"] == ["observer-visualizer"]
    assert manifest["scenario_count"] == 12
    assert manifest["row_count"] == 12
    assert {row["topology"] for row in manifest["rows"]} == {"squad-5", "constellation-10"}
    assert {row["surface_profile"] for row in manifest["rows"]} == {"observer-visualizer"}


def test_siso_runtime_surface_matrix_heaviest_preset_selects_constellation_rows() -> None:
    manifest = build_siso_runtime_surface_matrix_manifest(presets=["heaviest-interesting"])

    assert manifest["presets"] == ["heaviest-interesting"]
    assert manifest["surface_profiles"] == ["observer-visualizer"]
    assert manifest["scenario_count"] == 6
    assert manifest["row_count"] == 6
    assert {row["topology"] for row in manifest["rows"]} == {"constellation-10"}
    assert {row["family"] for row in manifest["rows"]} == {"link16", "rpr", "space"}


def test_siso_runtime_surface_matrix_artifacts_are_generated(tmp_path: Path) -> None:
    paths = write_siso_runtime_surface_matrix_artifacts(
        tmp_path / "surface-matrix",
        families=["link16"],
        editions=["2010"],
        topologies=["micro-2"],
        surface_profiles=["runtime-only", "observer-visualizer-bridge"],
        include_screenshots=False,
    )

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["suite_name"] == "siso-runtime-surface-matrix"
    assert summary["status"] == "green"
    assert summary["selected_scenario_count"] == 1
    assert summary["selected_row_count"] == 2
    assert summary["screenshot_runtime_status"] == "not-requested"
    assert paths.index_html.exists()

    with paths.results_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    row_by_profile = {row["surface_profile"]: row for row in rows}
    assert row_by_profile["runtime-only"]["observer_api_status"] == "not-included"
    assert row_by_profile["runtime-only"]["bridge_api_status"] == "not-included"
    assert row_by_profile["observer-visualizer-bridge"]["observer_api_status"] == "captured"
    assert row_by_profile["observer-visualizer-bridge"]["bridge_api_status"] == "captured"

    runtime_listener_summary = (
        paths.rows_root
        / "link16-rpr2-integrated-2010-micro-2"
        / "runtime-only"
        / "listener"
        / "link16-rpr2-integrated-2010-micro-2"
        / "listener_summary.json"
    )
    observer_state_json = (
        paths.rows_root
        / "link16-rpr2-integrated-2010-micro-2"
        / "observer-visualizer-bridge"
        / "api"
        / "state.json"
    )
    bridge_contract_json = (
        paths.rows_root
        / "link16-rpr2-integrated-2010-micro-2"
        / "observer-visualizer-bridge"
        / "api"
        / "federate_service_contract.json"
    )
    assert runtime_listener_summary.exists()
    assert observer_state_json.exists()
    assert bridge_contract_json.exists()

    observer_state = json.loads(observer_state_json.read_text(encoding="utf-8"))
    assert observer_state["provider"] == "siso-runtime"
    assert observer_state["scenario"] == "link16-rpr2-integrated-2010-micro-2"
    assert observer_state["summary_ready"] is True
    assert "artifacts" in observer_state
    index_html = paths.index_html.read_text(encoding="utf-8")
    assert "SISO Runtime Surface Matrix" in index_html
    assert "link16-rpr2-integrated-2010-micro-2" in index_html
    assert "Observer state" in index_html


def test_siso_runtime_surface_matrix_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "surface-matrix"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-runtime-surface-matrix"),
            "--family",
            "space",
            "--edition",
            "2025",
            "--topology",
            "micro-2",
            "--surface-profile",
            "observer-visualizer",
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads((output_dir / "siso_runtime_surface_matrix_summary.json").read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 1
    assert summary["selected_row_count"] == 1


def test_siso_runtime_surface_matrix_wrapper_accepts_presets(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "surface-matrix-preset"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-runtime-surface-matrix"),
            "--preset",
            "micro-bridge-smoke",
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads((output_dir / "siso_runtime_surface_matrix_summary.json").read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] >= 1
    assert summary["selected_row_count"] >= 1
