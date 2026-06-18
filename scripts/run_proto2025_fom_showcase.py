#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import tomllib

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

REQUIRED_CHART_CSVS = {
    "operation_throughput.csv",
    "federate_lifecycle_timeline.csv",
    "pubsub_coverage_matrix.csv",
    "callback_service_latency.csv",
    "test_verdict_summary.csv",
    "message_ladder.csv",
    "space_reference_frames.csv",
    "space_entity_tracks.csv",
    "time_delivery_order.csv",
    "time_advance_grants.csv",
}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _validate_artifacts(output_dir: Path) -> list[str]:
    errors: list[str] = []
    summary_path = output_dir / "proto2025_fom_showcase_summary.json"
    manifest_path = output_dir / "chart_data" / "chart_manifest.json"
    observer_path = output_dir / "chart_data" / "observer_events.jsonl"

    if not summary_path.exists():
        return [f"missing summary artifact: {summary_path}"]

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("status") != "lifecycle-green":
        errors.append(f"showcase status is {summary.get('status')!r}, expected 'lifecycle-green'")

    scenarios = {row.get("scenario"): row for row in summary.get("scenarios", [])}
    expected_scenarios = {"message-test", "space-lite", "time-mgmt-test", "target-radar"}
    missing_scenarios = expected_scenarios - set(scenarios)
    if missing_scenarios:
        errors.append(f"missing scenario summaries: {', '.join(sorted(missing_scenarios))}")
    for scenario_name in sorted(expected_scenarios & set(scenarios)):
        scenario = scenarios[scenario_name]
        if not scenario.get("execution_complete"):
            errors.append(f"{scenario_name} did not complete execution")
        if "federation-destroyed" not in scenario.get("lifecycle", []):
            errors.append(f"{scenario_name} did not destroy the federation")

    if scenarios.get("message-test", {}).get("interactions", 0) < 1:
        errors.append("message-test did not receive a FOM-defined interaction")
    if scenarios.get("space-lite", {}).get("reflections", 0) < 1:
        errors.append("space-lite did not reflect a FOM-defined object update")
    if scenarios.get("time-mgmt-test", {}).get("delivered_tags", [])[-2:] != ["event-1", "event-2"]:
        errors.append("time-mgmt-test did not preserve timestamp delivery order")
    if not scenarios.get("time-mgmt-test", {}).get("grant_times"):
        errors.append("time-mgmt-test did not produce time advance grants")
    if not scenarios.get("target-radar", {}).get("track_reports"):
        errors.append("target-radar did not produce track reports")

    if not manifest_path.exists():
        errors.append(f"missing chart manifest: {manifest_path}")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema_version") != "proto2025-hero-charts-v0.1":
            errors.append("chart manifest schema_version is not proto2025-hero-charts-v0.1")
        missing_csvs = REQUIRED_CHART_CSVS - set(manifest.get("csv_files", []))
        if missing_csvs:
            errors.append(f"chart manifest missing CSVs: {', '.join(sorted(missing_csvs))}")

    if not observer_path.exists() or observer_path.stat().st_size == 0:
        errors.append(f"missing or empty ObserverRecorder JSONL: {observer_path}")

    for csv_name in sorted(REQUIRED_CHART_CSVS):
        csv_path = output_dir / "chart_data" / csv_name
        if not csv_path.exists():
            errors.append(f"missing chart CSV: {csv_path}")
        elif not _read_csv_rows(csv_path):
            errors.append(f"empty chart CSV: {csv_path}")

    return errors


def main(argv: list[str] | None = None) -> int:
    from hla.verification.repo_internal.verification.proto2025_fom_showcase import write_proto2025_fom_showcase_artifacts

    parser = argparse.ArgumentParser(description="Run the Proto2025 v0.1 FOM simulation showcase and write chart-ready artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "proto2025_fom_showcase"),
        help="Directory for generated showcase artifacts",
    )
    parser.add_argument("--steps", type=int, default=3, help="Target/Radar steps to run inside the showcase")
    args = parser.parse_args(argv)

    paths = write_proto2025_fom_showcase_artifacts(args.output_dir, target_radar_steps=args.steps)
    errors = _validate_artifacts(paths.output_dir)
    print(paths.summary_json)
    print(paths.scenario_csv)
    print(paths.report_markdown)
    print(paths.chart_manifest_json)
    print(paths.observer_events_jsonl)
    for csv_name in sorted(REQUIRED_CHART_CSVS):
        print(paths.chart_data_dir / csv_name)
    if errors:
        for error in errors:
            print(f"proto2025 fom showcase failed postcondition: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
