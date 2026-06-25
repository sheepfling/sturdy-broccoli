from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.siso_pitch_micro_parity import (
    run_siso_pitch_micro_parity,
    write_siso_pitch_micro_parity_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


def test_siso_pitch_micro_parity_defaults_to_pitch_eligible_micro_rows() -> None:
    summary = run_siso_pitch_micro_parity()

    assert summary["suite_name"] == "siso-pitch-micro-parity"
    assert summary["selected_scenario_count"] == 12
    assert summary["passed"] + summary["skipped"] + summary["failed"] == 12
    assert summary["selected_manifest"]["scenario_count"] == 12
    backends = {row["backend"] for row in summary["results"]}
    assert backends == {
        "pitch-jpype",
        "pitch-py4j",
        "pitch-202x-jpype",
        "pitch-202x-py4j",
    }


def test_siso_pitch_micro_parity_artifacts_are_generated(tmp_path: Path) -> None:
    paths = write_siso_pitch_micro_parity_artifacts(tmp_path)

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 12

    with paths.results_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 12
    assert any(row["counts_as_vendor_runtime"] == "True" for row in rows)
    assert any(row["counts_as_vendor_runtime"] == "False" for row in rows)

    manifest = json.loads(paths.selected_manifest_json.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "siso-pitch-micro-parity-v0.1"
    assert manifest["scenario_count"] == 12

    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "SISO Pitch Micro Parity" in report
    assert "bounded adapter rows" in report


def test_siso_pitch_micro_parity_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "siso-pitch-micro-parity"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-pitch-micro-parity"),
            "--output-dir",
            str(output_dir),
            "--backend",
            "pitch-jpype",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = output_dir / "siso_pitch_micro_parity_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "siso-pitch-micro-parity"
    assert payload["selected_scenario_count"] == 3
