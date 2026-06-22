from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.proto2025_fom_showcase import (
    run_proto2025_fom_showcase,
    write_proto2025_fom_showcase_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]


def test_proto2025_fom_showcase_completes_all_example_federations() -> None:
    summary = run_proto2025_fom_showcase(target_radar_steps=2)

    assert summary["suite_name"] == "proto2025-fom-simulation-showcase"
    assert summary["profile"] == "python2025-direct"
    assert summary["status"] == "lifecycle-green"
    assert {row["scenario"] for row in summary["scenarios"]} == {
        "message-test",
        "space-lite",
        "time-mgmt-test",
        "target-radar",
    }
    assert all(row["execution_complete"] for row in summary["scenarios"])
    assert all("federation-destroyed" in row["lifecycle"] for row in summary["scenarios"])

    by_scenario = {row["scenario"]: row for row in summary["scenarios"]}
    assert by_scenario["message-test"]["fom_modules"] == ["Proto2025_Base.xml", "Proto2025_MessageTest.xml"]
    assert by_scenario["space-lite"]["fom_modules"] == ["Proto2025_Base.xml", "Proto2025_SpaceLite.xml"]
    assert by_scenario["time-mgmt-test"]["fom_modules"] == ["Proto2025_Base.xml", "Proto2025_TimeMgmtTest.xml"]
    assert by_scenario["time-mgmt-test"]["delivered_tags"][-2:] == ["event-1", "event-2"]
    assert len(by_scenario["target-radar"]["track_reports"]) == 2


def test_proto2025_fom_showcase_artifacts_are_generated(tmp_path) -> None:
    paths = write_proto2025_fom_showcase_artifacts(tmp_path, target_radar_steps=1)

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["profile"] == "python2025-direct"
    assert summary["status"] == "lifecycle-green"
    assert len(summary["scenarios"]) == 4

    with paths.scenario_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["scenario"] for row in rows] == [
        "message-test",
        "space-lite",
        "time-mgmt-test",
        "target-radar",
    ]
    assert all(row["status"] == "lifecycle-green" for row in rows)

    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "Proto2025 FOM Simulation Showcase" in report
    assert "MessageTest" in report
    assert "TargetRadarFOMmodule.xml" in report
    assert "chart manifest" in report

    manifest = json.loads(paths.chart_manifest_json.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "proto2025-hero-charts-v0.1"
    assert manifest["observer_events"] == "observer_events.jsonl"
    assert {
        "operation_throughput.csv",
        "message_ladder.csv",
        "space_reference_frames.csv",
        "time_delivery_order.csv",
        "time_advance_grants.csv",
    }.issubset(set(manifest["csv_files"]))

    observer_lines = paths.observer_events_jsonl.read_text(encoding="utf-8").splitlines()
    assert observer_lines
    observer_event = json.loads(observer_lines[0])
    assert {
        "event_id",
        "run_id",
        "scenario",
        "family",
        "federation",
        "federate",
        "event_type",
        "status",
        "payload",
    }.issubset(observer_event)

    with (paths.chart_data_dir / "message_ladder.csv").open(encoding="utf-8") as handle:
        message_rows = list(csv.DictReader(handle))
    assert [row["event"] for row in message_rows] == [
        "suite published",
        "stimulus sent",
        "verification observed",
    ]

    with (paths.chart_data_dir / "time_delivery_order.csv").open(encoding="utf-8") as handle:
        time_rows = list(csv.DictReader(handle))
    assert [row["event_tag"] for row in time_rows][-2:] == ["event-1", "event-2"]


def test_proto2025_fom_showcase_ci_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "analysis" / "proto2025_fom_showcase"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts" / "ci" / "proto2025_fom_showcase.sh"),
            "--output-dir",
            str(output_dir),
            "--steps",
            "1",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = output_dir / "proto2025_fom_showcase_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["suite_name"] == "proto2025-fom-simulation-showcase"
    assert summary["profile"] == "python2025-direct"
    assert summary["status"] == "lifecycle-green"
    assert all(row["execution_complete"] for row in summary["scenarios"])
    assert (output_dir / "chart_data" / "chart_manifest.json").exists()
    assert (output_dir / "chart_data" / "observer_events.jsonl").exists()
