"""Target/radar proof packet generator."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..scenarios import make_target_radar_factory
from ..scenarios.target_radar import TrackReport, Vec3, run_target_radar_scenario
from .target_radar_backend_matrix import run_target_radar_backend_matrix


@dataclass(frozen=True)
class TargetRadarProofPaths:
    output_dir: Path
    summary_json: Path
    backend_results_csv: Path
    target_truth_csv: Path
    radar_events_csv: Path
    track_reports_csv: Path
    report_markdown: Path
    overview_svg: Path
    timeline_svg: Path
    trajectory_svg: Path


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Vec3):
        return {"x": value.x, "y": value.y, "z": value.z}
    if isinstance(value, TrackReport):
        return value.as_dict()
    if isinstance(value, Mapping):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return _jsonable(value.as_dict())
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


def _target_truth_rows(result: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    step_number = 0
    for index, (event_name, payload) in enumerate(result.target_events, start=1):
        if event_name != "step":
            continue
        step_number += 1
        rows.append(
            {
                "index": index,
                "step_number": step_number,
                "event_name": event_name,
                "time_seconds": payload["time_seconds"],
                "position_x": payload["position"].x,
                "position_y": payload["position"].y,
                "position_z": payload["position"].z,
            }
        )
    return rows


def _radar_event_rows(result: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (event_name, payload) in enumerate(result.radar_events, start=1):
        row: dict[str, Any] = {
            "index": index,
            "event_name": event_name,
        }
        if event_name == "discover":
            _, _, object_name = payload
            row["object_name"] = object_name
        elif event_name == "query_rcs":
            row["object_handle"] = repr(payload)
        elif event_name == "track":
            row["track_id"] = payload.track_id
            row["target_name"] = payload.target_name
            row["time_seconds"] = payload.time_seconds
            row["range_m"] = payload.range_m
            row["bearing_rad"] = payload.bearing_rad
            row["rcs_square_meters"] = payload.rcs_square_meters
        else:
            object_handle, attributes, user_supplied_tag = payload
            row["object_handle"] = repr(object_handle)
            row["attribute_count"] = len(attributes)
            row["tag_hex"] = user_supplied_tag.hex()
        rows.append(row)
    return rows


def _track_report_rows(result: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report in result.track_reports:
        rows.append(
            {
                "track_id": report.track_id,
                "target_name": report.target_name,
                "position_x": report.position.x,
                "position_y": report.position.y,
                "position_z": report.position.z,
                "range_m": report.range_m,
                "bearing_rad": report.bearing_rad,
                "rcs_square_meters": report.rcs_square_meters,
                "time_seconds": report.time_seconds,
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]], *, fieldnames: Sequence[str]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_markdown(path: Path, summary: Mapping[str, Any], paths: TargetRadarProofPaths) -> Path:
    proof = summary["proof"]
    matrix = summary["backend_matrix"]
    lines = [
        "# Target/Radar Simulation Proof",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- proof backend: `{proof['backend_kinds'][0]}`",
        f"- target truth samples: `{len(proof['target_truth_rows'])}`",
        f"- radar events: `{len(proof['radar_event_rows'])}`",
        f"- track reports: `{len(proof['track_reports'])}`",
        "",
        "## Backend Matrix",
        "",
        "| Backend | Status | Track reports | Reason |",
        "| --- | --- | ---: | --- |",
    ]
    for result in matrix["results"]:
        lines.append(
            f"| {result['backend']} | {result['status']} | {result['track_reports']} | {result.get('reason') or ''} |"
        )
    lines.extend(
        [
            "",
            "## Simulation Trace",
            "",
            "| Step | Time | Target Position (x, y, z) |",
            "| ---: | ---: | --- |",
        ]
    )
    for row in proof["target_truth_rows"]:
        lines.append(
            f"| {row['step_number']} | {row['time_seconds']} | ({row['position_x']}, {row['position_y']}, {row['position_z']}) |"
        )
    lines.extend(
        [
            "",
            "## Track Reports",
            "",
            "| Track | Target | Range (m) | Bearing (rad) | Time |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for report in proof["track_reports"]:
        lines.append(
            f"| {report['track_id']} | {report['target_name']} | {report['range_m']} | {report['bearing_rad']} | {report['time_seconds']} |"
        )
    lines.extend(
        [
            "",
            "## Visuals",
            "",
            f"- Backend overview: `{paths.overview_svg.name}`",
            f"- Event timeline: `{paths.timeline_svg.name}`",
            f"- Truth trajectory: `{paths.trajectory_svg.name}`",
            "",
            "## Re-run",
            "",
            "`./scripts/ci/target_radar_proof.sh`",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_overview_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    matrix = summary["backend_matrix"]
    proof = summary["proof"]
    results = list(matrix["results"])
    width = 1280
    row_height = 50
    top = 118
    height = top + row_height * len(results) + 150
    status_colors = {"passed": "#2b9348", "skipped": "#8d99ae", "failed": "#d00000"}
    rows: list[str] = []
    for index, item in enumerate(results):
        y = top + index * row_height
        rows.append(
            f'<text x="40" y="{y + 16}" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{item["backend"]}</text>'
            f'<rect x="260" y="{y}" width="110" height="24" rx="8" fill="{status_colors.get(item["status"], "#495057")}" opacity="0.92" />'
            f'<text x="315" y="{y + 16}" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#ffffff">{item["status"]}</text>'
            f'<text x="410" y="{y + 16}" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{item["track_reports"]} track reports</text>'
            f'<text x="620" y="{y + 16}" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{item.get("reason") or ""}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Target/Radar Simulation Proof</text>
  <text x="40" y="70" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Backend status plus a detailed Python proof trace.</text>
  <text x="40" y="100" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">Python proof backend</text>
  <text x="260" y="100" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{proof['backend_kinds'][0]}</text>
  <text x="40" y="120" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">Truth samples</text>
  <text x="260" y="120" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{len(proof['target_truth_rows'])}</text>
  <text x="40" y="140" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">Track reports</text>
  <text x="260" y="140" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{len(proof['track_reports'])}</text>
  {' '.join(rows)}
</svg>
"""
    path.write_text(svg)
    return path


def _write_timeline_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    proof = summary["proof"]
    target_rows = proof["target_truth_rows"]
    radar_rows = proof["radar_event_rows"]
    width = 1240
    lane_height = 64
    top = 120
    lanes = ["target_truth", "radar_query", "radar_track"]
    height = top + lane_height * len(lanes) + 130
    max_time = max((row["time_seconds"] for row in target_rows if row.get("time_seconds") is not None), default=1.0)
    event_nodes: list[str] = []
    for row in target_rows:
        x = 140 + 980 * float(row["time_seconds"]) / max(max_time, 1.0)
        y = top + 0 * lane_height + 14
        event_nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#2f6fed" />'
            f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-size="9" fill="#ffffff">{int(row["step_number"])}</text>'
        )
    for row in radar_rows:
        if row["event_name"] == "query_rcs":
            x = 140 + 980 * float(row["index"]) / max(len(radar_rows), 1)
            y = top + 1 * lane_height + 14
            event_nodes.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#e85d04" />'
                f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-size="9" fill="#ffffff">{int(row["index"])}</text>'
            )
        elif row["event_name"] == "track":
            x = 140 + 980 * float(row["time_seconds"]) / max(proof["track_reports"][-1]["time_seconds"], 1.0)
            y = top + 2 * lane_height + 14
            event_nodes.append(
                f'<rect x="{x - 8:.1f}" y="{y - 8:.1f}" width="16" height="16" rx="4" fill="#2b9348" />'
                f'<text x="{x:.1f}" y="{y + 15:.1f}" text-anchor="middle" font-size="9" fill="#132238">{row["track_id"]}</text>'
            )
    lane_nodes = []
    labels = {"target_truth": "Target truth steps", "radar_query": "RCS queries", "radar_track": "Track outputs"}
    for index, lane in enumerate(lanes):
        y = top + index * lane_height
        lane_nodes.append(
            f'<line x1="140" y1="{y}" x2="1140" y2="{y}" stroke="#d8e0ea" stroke-width="2" />'
            f'<text x="36" y="{y + 18}" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#132238">{labels[lane]}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Simulation Timeline</text>
  <text x="40" y="68" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Target truth updates, radar RCS queries, and track emissions.</text>
  {' '.join(lane_nodes)}
  <line x1="140" y1="{top - 18}" x2="140" y2="{top + lane_height * len(lanes) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <line x1="1140" y1="{top - 18}" x2="1140" y2="{top + lane_height * len(lanes) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <text x="140" y="{top - 26}" font-size="12" fill="#48607a">start</text>
  <text x="1128" y="{top - 26}" font-size="12" fill="#48607a">end</text>
  {' '.join(event_nodes)}
</svg>
"""
    path.write_text(svg)
    return path


def _write_trajectory_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    proof = summary["proof"]
    target_rows = proof["target_truth_rows"]
    track_reports = proof["track_reports"]
    width = 1240
    height = 580
    chart_left = 90
    chart_top = 100
    chart_width = 1020
    chart_height = 360
    xs = [row["position_x"] for row in target_rows] + [report["position_x"] for report in track_reports]
    ys = [row["position_y"] for row in target_rows] + [report["position_y"] for report in track_reports]
    x_min, x_max = min(xs, default=0.0), max(xs, default=1.0)
    y_min, y_max = min(ys, default=0.0), max(ys, default=1.0)
    x_span = max(x_max - x_min, 1.0)
    y_span = max(y_max - y_min, 1.0)

    def to_x(val: float) -> float:
        return chart_left + chart_width * (val - x_min) / x_span

    def to_y(val: float) -> float:
        return chart_top + chart_height - chart_height * (val - y_min) / y_span

    truth_points = " ".join(f"{to_x(row['position_x']):.1f},{to_y(row['position_y']):.1f}" for row in target_rows)
    track_points = " ".join(f"{to_x(report['position_x']):.1f},{to_y(report['position_y']):.1f}" for report in track_reports)
    truth_nodes = []
    for row in target_rows:
        x, y = to_x(row["position_x"]), to_y(row["position_y"])
        truth_nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2f6fed" />'
            f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="10" fill="#2f6fed">{int(row["time_seconds"])}s</text>'
        )
    track_nodes = []
    for report in track_reports:
        x, y = to_x(report["position_x"]), to_y(report["position_y"])
        track_nodes.append(
            f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" rx="2" fill="#e85d04" />'
            f'<text x="{x + 10:.1f}" y="{y + 4:.1f}" font-size="10" fill="#e85d04">{report["track_id"]}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Truth Trajectory vs Track Reports</text>
  <text x="40" y="68" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Blue line: target truth positions. Orange squares: radar track outputs.</text>
  <line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <line x1="{chart_left}" y1="{chart_top + chart_height}" x2="{chart_left + chart_width}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <polyline fill="none" stroke="#2f6fed" stroke-width="3" points="{truth_points}" />
  <polyline fill="none" stroke="#e85d04" stroke-width="2" stroke-dasharray="6 4" points="{track_points}" />
  {' '.join(truth_nodes)}
  {' '.join(track_nodes)}
  <text x="{chart_left}" y="{chart_top + chart_height + 28}" font-size="12" fill="#48607a">X axis: target position x; Y axis: target position y.</text>
</svg>
"""
    path.write_text(svg)
    return path


def run_target_radar_proof(
    backends: Sequence[str],
    *,
    proof_backend: str = "python",
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    backend_matrix = run_target_radar_backend_matrix(
        backends,
        target_radar_steps=target_radar_steps,
        dt=dt,
        backend_options_by_kind=backend_options_by_kind,
    )
    proof_result = run_target_radar_scenario(
        make_target_radar_factory(
            proof_backend,
            backend_options=(backend_options_by_kind or {}).get(proof_backend, {}),
        ),
        federation_name="TargetRadarProofFederation",
        steps=target_radar_steps,
        dt=dt,
    )
    proof = {
        "backend": proof_backend,
        "backend_kinds": proof_result.backend_kinds,
        "federation_name": proof_result.federation_name,
        "track_reports": _track_report_rows(proof_result),
        "target_truth_rows": _target_truth_rows(proof_result),
        "radar_event_rows": _radar_event_rows(proof_result),
    }
    return {
        "suite_name": "target-radar-proof",
        "target_radar_fom": backend_matrix["target_radar_fom"],
        "steps": target_radar_steps,
        "dt": dt,
        "backend_matrix": backend_matrix,
        "proof": proof,
    }


def write_target_radar_proof_artifacts(
    output_dir: Path | str,
    backends: Sequence[str],
    *,
    proof_backend: str = "python",
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
) -> TargetRadarProofPaths:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = run_target_radar_proof(
        backends,
        proof_backend=proof_backend,
        target_radar_steps=target_radar_steps,
        dt=dt,
        backend_options_by_kind=backend_options_by_kind,
    )
    paths = TargetRadarProofPaths(
        output_dir=output_dir,
        summary_json=output_dir / "target_radar_proof_summary.json",
        backend_results_csv=output_dir / "target_radar_backend_results.csv",
        target_truth_csv=output_dir / "target_radar_truth.csv",
        radar_events_csv=output_dir / "target_radar_radar_events.csv",
        track_reports_csv=output_dir / "target_radar_track_reports.csv",
        report_markdown=output_dir / "target_radar_proof_report.md",
        overview_svg=output_dir / "target_radar_proof_overview.svg",
        timeline_svg=output_dir / "target_radar_proof_timeline.svg",
        trajectory_svg=output_dir / "target_radar_proof_trajectory.svg",
    )
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(
        paths.backend_results_csv,
        summary["backend_matrix"]["results"],
        fieldnames=["backend", "status", "reason", "track_reports", "first_range_m", "last_range_m", "range_delta_m", "final_time_seconds", "backend_kinds", "track_ids"],
    )
    _write_csv(
        paths.target_truth_csv,
        summary["proof"]["target_truth_rows"],
        fieldnames=["index", "step_number", "event_name", "time_seconds", "position_x", "position_y", "position_z"],
    )
    radar_fieldnames = ["index", "event_name", "object_name", "object_handle", "attribute_count", "tag_hex", "track_id", "target_name", "time_seconds", "range_m", "bearing_rad", "rcs_square_meters"]
    _write_csv(paths.radar_events_csv, summary["proof"]["radar_event_rows"], fieldnames=radar_fieldnames)
    _write_csv(
        paths.track_reports_csv,
        summary["proof"]["track_reports"],
        fieldnames=["track_id", "target_name", "position_x", "position_y", "position_z", "range_m", "bearing_rad", "rcs_square_meters", "time_seconds"],
    )
    _write_markdown(paths.report_markdown, summary, paths)
    _write_overview_svg(paths.overview_svg, summary)
    _write_timeline_svg(paths.timeline_svg, summary)
    _write_trajectory_svg(paths.trajectory_svg, summary)
    return paths


__all__ = [
    "TargetRadarProofPaths",
    "run_target_radar_proof",
    "write_target_radar_proof_artifacts",
]
