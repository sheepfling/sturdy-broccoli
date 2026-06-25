from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.verification import pitch_fom_smoke_compare as module


ROOT = Path(__file__).resolve().parents[2]


def test_build_pitch_fom_smoke_comparison_marks_real_only_and_shared_failures() -> None:
    real = {
        "suite_name": "pitch-fom-smoke",
        "rows": [
            {
                "packet_id": "repo-2010-demo",
                "scenario_family": "demo",
                "load_mode": "standalone",
                "notes": "demo",
                "runtime_kind": "pitch-jpype",
                "status": "failed",
                "error_type": "ErrorReadingFDD",
                "error_message": "Invalid FDD",
            },
            {
                "packet_id": "space-fom-core",
                "scenario_family": "siso-space-fom",
                "load_mode": "ordered-family",
                "notes": "space",
                "runtime_kind": "pitch-jpype",
                "status": "failed",
                "error_type": "NameNotFound",
                "error_message": "ReferenceFrameAnnouncement",
            },
        ],
    }
    adapter = {
        "suite_name": "pitch-fom-smoke",
        "rows": [
            {
                "packet_id": "repo-2010-demo",
                "scenario_family": "demo",
                "load_mode": "standalone",
                "notes": "demo",
                "runtime_kind": "pitch-202x-jpype",
                "status": "lookup-green",
            },
            {
                "packet_id": "space-fom-core",
                "scenario_family": "siso-space-fom",
                "load_mode": "ordered-family",
                "notes": "space",
                "runtime_kind": "pitch-202x-jpype",
                "status": "failed",
                "error_type": "NameNotFound",
                "error_message": "ReferenceFrameAnnouncement",
            },
        ],
    }

    summary = module.build_pitch_fom_smoke_comparison(real, adapter)

    assert summary["suite_name"] == "pitch-fom-smoke-compare"
    packet_rows = {row["packet_id"]: row for row in summary["packet_rows"]}
    assert packet_rows["repo-2010-demo"]["comparison_bucket"] == "real-only-failure"
    assert packet_rows["space-fom-core"]["comparison_bucket"] == "shared-failure"


def test_write_pitch_fom_smoke_comparison_emits_summary_and_markdown(tmp_path: Path) -> None:
    paths = module.write_pitch_fom_smoke_comparison(
        tmp_path,
        {
            "suite_name": "pitch-fom-smoke",
            "rows": [
                {
                    "packet_id": "repo-cross-target-radar",
                    "scenario_family": "target-radar",
                    "load_mode": "standalone",
                    "notes": "target-radar",
                    "runtime_kind": "pitch-jpype",
                    "status": "lookup-green",
                }
            ],
        },
        {
            "suite_name": "pitch-fom-smoke",
            "rows": [
                {
                    "packet_id": "repo-cross-target-radar",
                    "scenario_family": "target-radar",
                    "load_mode": "standalone",
                    "notes": "target-radar",
                    "runtime_kind": "pitch-202x-jpype",
                    "status": "lookup-green",
                }
            ],
        },
    )

    assert paths.summary_json.exists()
    assert paths.report_markdown.exists()
    text = paths.report_markdown.read_text(encoding="utf-8")
    assert "Pitch FOM Smoke Comparison" in text
    assert "green-both" in text


def test_generate_pitch_fom_smoke_comparison_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    real = tmp_path / "real.json"
    adapter = tmp_path / "adapter.json"
    real.write_text(
        json.dumps(
            {
                "suite_name": "pitch-fom-smoke",
                "rows": [
                    {
                        "packet_id": "repo-cross-target-radar",
                        "scenario_family": "target-radar",
                        "load_mode": "standalone",
                        "notes": "target-radar",
                        "runtime_kind": "pitch-jpype",
                        "status": "lookup-green",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    adapter.write_text(
        json.dumps(
            {
                "suite_name": "pitch-fom-smoke",
                "rows": [
                    {
                        "packet_id": "repo-cross-target-radar",
                        "scenario_family": "target-radar",
                        "load_mode": "standalone",
                        "notes": "target-radar",
                        "runtime_kind": "pitch-202x-jpype",
                        "status": "lookup-green",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "compare"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_pitch_fom_smoke_comparison.py"),
            "--real-summary",
            str(real),
            "--adapter-summary",
            str(adapter),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "pitch_fom_smoke_compare_summary.json").exists()
    assert (output_dir / "pitch_fom_smoke_compare_report.md").exists()
