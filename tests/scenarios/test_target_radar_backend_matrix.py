from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.target_radar_backend_matrix import write_target_radar_backend_matrix_artifacts


ROOT = Path(__file__).resolve().parents[2]


def test_target_radar_backend_matrix_artifacts_are_generated(tmp_path):
    paths = write_target_radar_backend_matrix_artifacts(
        tmp_path,
        ["python1516e", "java-shim-jpype", "java-shim-py4j"],
        target_radar_steps=2,
    )

    summary = json.loads(paths.summary_json.read_text())
    assert summary["suite_name"] == "target-radar-backend-matrix"
    assert summary["passed"] == 3
    assert summary["skipped"] == 0
    assert summary["failed"] == 0
    assert len(summary["results"]) == 3
    assert summary["results"][0]["backend"] == "python1516e"
    assert summary["results"][0]["status"] == "passed"
    assert summary["results"][0]["track_reports"] == 2
    assert summary["results"][0]["range_delta_m"] > 0

    with paths.results_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert rows[0]["backend"] == "python1516e"
    assert rows[0]["status"] == "passed"

    report_text = paths.report_markdown.read_text()
    assert "Target/Radar Backend Matrix" in report_text
    assert "How To Re-run" in report_text
    assert "java-shim-jpype" in report_text
    assert "./tools/target-radar matrix" in report_text

    svg_text = paths.summary_svg.read_text()
    assert "<svg" in svg_text
    assert "Target/Radar Backend Matrix" in svg_text


def test_target_radar_backend_matrix_ci_wrapper_bootstraps_source_checkout(tmp_path):
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "artifacts" / "target_radar_backend_matrix"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts" / "ci" / "target_radar_backend_matrix.sh"),
            "--backend",
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
    summary_path = output_dir / "target_radar_backend_matrix_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["suite_name"] == "target-radar-backend-matrix"
    assert summary["passed"] == 1
