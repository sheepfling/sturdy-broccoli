from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.target_radar_proof import write_target_radar_proof_artifacts


ROOT = Path(__file__).resolve().parents[2]


def test_target_radar_proof_artifacts_are_generated(tmp_path):
    paths = write_target_radar_proof_artifacts(
        tmp_path,
        ["python1516e", "java-shim-jpype", "java-shim-py4j"],
        target_radar_steps=3,
    )

    summary = json.loads(paths.summary_json.read_text())
    assert summary["suite_name"] == "target-radar-proof"
    assert summary["backend_matrix"]["passed"] == 3
    assert summary["backend_matrix"]["failed"] == 0
    assert len(summary["proof"]["target_truth_rows"]) == 3
    assert len(summary["proof"]["radar_event_rows"]) > 0
    assert len(summary["proof"]["track_reports"]) == 3
    assert summary["proof"]["track_reports"][0]["track_id"] == "TRK-001"

    with paths.target_truth_csv.open() as handle:
        truth_rows = list(csv.DictReader(handle))
    assert len(truth_rows) == 3
    assert truth_rows[0]["event_name"] == "step"

    with paths.radar_events_csv.open() as handle:
        radar_rows = list(csv.DictReader(handle))
    assert any(row["event_name"] == "query_rcs" for row in radar_rows)
    assert any(row["event_name"] == "track" for row in radar_rows)

    with paths.track_reports_csv.open() as handle:
        track_rows = list(csv.DictReader(handle))
    assert len(track_rows) == 3
    assert track_rows[0]["track_id"] == "TRK-001"

    report_text = paths.report_markdown.read_text()
    assert "Target/Radar Simulation Proof" in report_text
    assert "Backend overview PNG" in report_text
    assert "Event timeline PNG" in report_text
    assert "Truth trajectory PNG" in report_text
    assert "RCS exchange PNG" in report_text
    assert "## Track Reports" in report_text
    assert "./tools/target-radar proof" in report_text

    assert paths.overview_png.exists() and paths.overview_png.stat().st_size > 0
    assert paths.timeline_png.exists() and paths.timeline_png.stat().st_size > 0
    assert paths.trajectory_png.exists() and paths.trajectory_png.stat().st_size > 0
    assert paths.rcs_exchange_png.exists() and paths.rcs_exchange_png.stat().st_size > 0

    overview_svg = paths.overview_svg.read_text()
    assert "<svg" in overview_svg
    assert "Target/Radar Simulation Proof" in overview_svg

    timeline_svg = paths.timeline_svg.read_text()
    assert "<svg" in timeline_svg
    assert "Simulation Timeline" in timeline_svg

    trajectory_svg = paths.trajectory_svg.read_text()
    assert "<svg" in trajectory_svg
    assert "Truth Trajectory vs Track Reports" in trajectory_svg


def test_target_radar_proof_ci_wrapper_bootstraps_source_checkout(tmp_path):
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "artifacts" / "target_radar_proof"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts" / "ci" / "target_radar_proof.sh"),
            "--backend",
            "python1516e",
            "--proof-backend",
            "python1516e",
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
    summary_path = output_dir / "target_radar_proof_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["suite_name"] == "target-radar-proof"
    assert summary["backend_matrix"]["passed"] == 1
