"""Target/radar proof packet generator."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from hla.foms.target_radar._internal.target_radar import TrackReport, Vec3, run_target_radar_scenario
from .target_radar_backend_matrix import _make_backend_factory, run_target_radar_backend_matrix


@dataclass(frozen=True)
class TargetRadarProofPaths:
    output_dir: Path
    summary_json: Path
    backend_results_csv: Path
    target_truth_csv: Path
    radar_events_csv: Path
    track_reports_csv: Path
    report_markdown: Path
    overview_png: Path
    timeline_png: Path
    trajectory_png: Path
    rcs_exchange_png: Path
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
            try:
                row["tag_text"] = user_supplied_tag.decode("utf-8")
            except Exception:
                row["tag_text"] = ""
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
        lines.append(f"| {result['backend']} | {result['status']} | {result['track_reports']} | {result.get('reason') or ''} |")
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
        lines.append(f"| {row['step_number']} | {row['time_seconds']} | ({row['position_x']}, {row['position_y']}, {row['position_z']}) |")
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
        lines.append(f"| {report['track_id']} | {report['target_name']} | {report['range_m']} | {report['bearing_rad']} | {report['time_seconds']} |")
    lines.extend(
        [
            "",
            "## Visuals",
            "",
            f"- Backend overview PNG: `{paths.overview_png.name}`",
            f"- Event timeline PNG: `{paths.timeline_png.name}`",
            f"- Truth trajectory PNG: `{paths.trajectory_png.name}`",
            f"- RCS exchange PNG: `{paths.rcs_exchange_png.name}`",
            f"- Backend overview: `{paths.overview_svg.name}`",
            f"- Event timeline: `{paths.timeline_svg.name}`",
            f"- Truth trajectory: `{paths.trajectory_svg.name}`",
            "",
            "## Re-run",
            "",
            "`./tools/target-radar proof`",
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
  <text x="260" y="100" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{proof["backend_kinds"][0]}</text>
  <text x="40" y="120" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">Truth samples</text>
  <text x="260" y="120" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{len(proof["target_truth_rows"])}</text>
  <text x="40" y="140" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">Track reports</text>
  <text x="260" y="140" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{len(proof["track_reports"])}</text>
  {" ".join(rows)}
</svg>
"""
    path.write_text(svg)
    return path


def _render_png_plots(paths: TargetRadarProofPaths, summary: Mapping[str, Any]) -> None:
    output_dir = paths.output_dir
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".mplconfig"))
    os.environ.setdefault("XDG_CACHE_HOME", str(output_dir / ".cache"))
    (output_dir / ".mplconfig").mkdir(parents=True, exist_ok=True)
    (output_dir / ".cache").mkdir(parents=True, exist_ok=True)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    matrix = summary["backend_matrix"]
    proof = summary["proof"]
    results = list(matrix["results"])
    statuses = [result["status"] for result in results]
    colors = []
    color_map = {"passed": "#2b9348", "skipped": "#8d99ae", "failed": "#d00000"}
    for result in results:
        colors.append(color_map.get(result["status"], "#495057"))

    fig, (ax_counts, ax_ranges) = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    backends = [result["backend"] for result in results]
    track_counts = [result["track_reports"] for result in results]
    final_ranges = [result.get("last_range_m") or 0.0 for result in results]
    x_positions = list(range(len(backends)))
    bars = ax_counts.bar(x_positions, track_counts, color=colors, edgecolor="#243447", linewidth=0.8)
    ax_counts.set_title("Target/Radar Backend Matrix")
    ax_counts.set_ylabel("Track reports")
    ax_counts.grid(axis="y", alpha=0.2)
    ax_counts.set_ylim(0, max(track_counts) + 1)
    for bar, status in zip(bars, statuses):
        ax_counts.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.08,
            status,
            ha="center",
            va="bottom",
            fontsize=9,
            rotation=0,
        )
    ax_counts.set_xticks(x_positions, labels=backends)
    ax_counts.tick_params(axis="x", rotation=20)

    ax_ranges.plot(x_positions, final_ranges, marker="o", color="#2f6fed", linewidth=2.5)
    ax_ranges.set_ylabel("Final range (m)")
    ax_ranges.set_title("Final Track Range by Backend")
    ax_ranges.grid(axis="y", alpha=0.2)
    ax_ranges.set_xticks(x_positions, labels=backends)
    ax_ranges.tick_params(axis="x", rotation=20)
    for x, y in zip(x_positions, final_ranges):
        ax_ranges.text(x, y, f" {y:.1f}", ha="center", va="bottom", fontsize=9)
    fig.suptitle("Target/Radar Simulation Proof - Backend Matrix", fontsize=15, y=1.02)
    fig.savefig(paths.overview_png, dpi=160, bbox_inches="tight")
    plt.close(fig)

    target_rows = proof["target_truth_rows"]
    radar_rows = proof["radar_event_rows"]
    track_reports = proof["track_reports"]

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    target_times = [row["time_seconds"] for row in target_rows]
    target_steps = [row["step_number"] for row in target_rows]
    query_indices = [row["index"] for row in radar_rows if row["event_name"] == "query_rcs"]
    query_times = [idx for idx in query_indices]
    track_times = [row["time_seconds"] for row in radar_rows if row["event_name"] == "track"]

    ax.scatter(target_times, [1] * len(target_times), s=110, color="#2f6fed", label="Target truth step", zorder=3)
    for time, step in zip(target_times, target_steps):
        ax.text(time, 1.08, f"S{step}", ha="center", va="bottom", fontsize=9, color="#2f6fed")
    if query_times:
        ax.scatter(query_times, [2] * len(query_times), s=110, color="#e85d04", label="Radar RCS query", zorder=3)
        for idx in query_times:
            ax.text(idx, 2.08, f"Q{idx}", ha="center", va="bottom", fontsize=9, color="#e85d04")
    if track_times:
        ax.scatter(track_times, [3] * len(track_times), s=110, marker="s", color="#2b9348", label="Track emission", zorder=3)
        for report in track_reports:
            ax.text(report["time_seconds"], 3.08, report["track_id"], ha="center", va="bottom", fontsize=9, color="#2b9348")
    ax.set_yticks([1, 2, 3], labels=["Target truth", "RCS query", "Track output"])
    ax.set_xlabel("Simulation time / event order")
    ax.set_title("Target/Radar Simulation Timeline")
    ax.grid(axis="x", alpha=0.2)
    ax.grid(axis="y", alpha=0.12)
    ax.set_xlim(0.5, max(max(target_times, default=1.0), max(track_times, default=1.0), max(query_times, default=1.0)) + 0.5)
    ax.legend(loc="upper left")
    fig.savefig(paths.timeline_png, dpi=160, bbox_inches="tight")
    plt.close(fig)

    exchange_steps: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in radar_rows:
        if row["event_name"] == "query_rcs":
            current = {"query": row}
            continue
        if current is None:
            continue
        if row["event_name"] == "reflect" and "response" not in current:
            tag_text = row.get("tag_text", "")
            if "rcs-response:" in tag_text:
                current["response"] = row
            continue
        if row["event_name"] == "track" and "track" not in current:
            current["track"] = row
            exchange_steps.append(current)
            current = None

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    y_levels = {"query": 3, "response": 2, "track": 1}
    y_labels = {3: "Radar query", 2: "Target RCS response", 1: "Track emission"}
    colors = {"query": "#e85d04", "response": "#2f6fed", "track": "#2b9348"}
    for step_index, step in enumerate(exchange_steps, start=1):
        query_row = step.get("query")
        response_row = step.get("response")
        track_row = step.get("track")
        if query_row is not None:
            ax.scatter(step_index, y_levels["query"], s=140, color=colors["query"], zorder=3)
            ax.text(step_index, y_levels["query"] + 0.12, f"Q{step_index}", ha="center", va="bottom", fontsize=9, color=colors["query"])
        if response_row is not None:
            ax.scatter(step_index, y_levels["response"], s=140, color=colors["response"], zorder=3)
            ax.text(
                step_index,
                y_levels["response"] + 0.12,
                "RCS",
                ha="center",
                va="bottom",
                fontsize=9,
                color=colors["response"],
            )
        if track_row is not None:
            ax.scatter(step_index, y_levels["track"], s=140, marker="s", color=colors["track"], zorder=3)
            ax.text(step_index, y_levels["track"] - 0.14, track_row["track_id"], ha="center", va="top", fontsize=9, color=colors["track"])
        if query_row is not None and response_row is not None:
            ax.annotate(
                "",
                xy=(step_index, y_levels["response"] + 0.05),
                xytext=(step_index, y_levels["query"] - 0.05),
                arrowprops={"arrowstyle": "->", "color": colors["query"], "lw": 2},
            )
        if response_row is not None and track_row is not None:
            ax.annotate(
                "",
                xy=(step_index, y_levels["track"] + 0.05),
                xytext=(step_index, y_levels["response"] - 0.05),
                arrowprops={"arrowstyle": "->", "color": colors["track"], "lw": 2},
            )
    ax.set_xlim(0.5, max(len(exchange_steps), 1) + 0.5)
    ax.set_ylim(0.5, 3.5)
    ax.set_xticks(list(range(1, len(exchange_steps) + 1)))
    ax.set_yticks([1, 2, 3], labels=[y_labels[1], y_labels[2], y_labels[3]])
    ax.set_xlabel("Step")
    ax.set_title("RCS Query, Response, and Track Exchange")
    ax.grid(axis="y", alpha=0.15)
    ax.grid(axis="x", alpha=0.08)
    fig.savefig(paths.rcs_exchange_png, dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)
    truth_x = [row["position_x"] for row in target_rows]
    truth_y = [row["position_y"] for row in target_rows]
    track_x = [report["position_x"] for report in track_reports]
    track_y = [report["position_y"] for report in track_reports]
    ax.plot(truth_x, truth_y, color="#2f6fed", linewidth=2.5, marker="o", label="Target truth")
    ax.scatter(track_x, track_y, color="#e85d04", s=90, marker="s", label="Radar track")
    for row in target_rows:
        ax.annotate(
            f"S{int(row['step_number'])}", (row["position_x"], row["position_y"]), textcoords="offset points", xytext=(6, 6), fontsize=9, color="#2f6fed"
        )
    for report in track_reports:
        ax.annotate(report["track_id"], (report["position_x"], report["position_y"]), textcoords="offset points", xytext=(6, -10), fontsize=9, color="#e85d04")
    ax.set_title("Truth Trajectory vs Track Reports")
    ax.set_xlabel("Position X (m)")
    ax.set_ylabel("Position Y (m)")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.savefig(paths.trajectory_png, dpi=160, bbox_inches="tight")
    plt.close(fig)


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
    timeline_caption = "Target truth updates, radar RCS queries, and track emissions."
    for index, lane in enumerate(lanes):
        y = top + index * lane_height
        lane_nodes.append(
            f'<line x1="140" y1="{y}" x2="1140" y2="{y}" stroke="#d8e0ea" stroke-width="2" />'
            f'<text x="36" y="{y + 18}" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#132238">{labels[lane]}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Simulation Timeline</text>
  <text x="40" y="68" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{timeline_caption}</text>
  {" ".join(lane_nodes)}
  <line x1="140" y1="{top - 18}" x2="140" y2="{top + lane_height * len(lanes) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <line x1="1140" y1="{top - 18}" x2="1140" y2="{top + lane_height * len(lanes) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <text x="140" y="{top - 26}" font-size="12" fill="#48607a">start</text>
  <text x="1128" y="{top - 26}" font-size="12" fill="#48607a">end</text>
  {" ".join(event_nodes)}
</svg>
"""
    path.write_text(svg)
    return path


def _write_trajectory_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    proof = summary["proof"]
    target_rows = proof["target_truth_rows"]
    track_reports = proof["track_reports"]
    trajectory_caption = "Blue line: target truth positions. Orange squares: radar track outputs."
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
  <text x="40" y="68" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{trajectory_caption}</text>
  <line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <line x1="{chart_left}" y1="{chart_top + chart_height}" x2="{chart_left + chart_width}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <polyline fill="none" stroke="#2f6fed" stroke-width="3" points="{truth_points}" />
  <polyline fill="none" stroke="#e85d04" stroke-width="2" stroke-dasharray="6 4" points="{track_points}" />
  {" ".join(truth_nodes)}
  {" ".join(track_nodes)}
  <text x="{chart_left}" y="{chart_top + chart_height + 28}" font-size="12" fill="#48607a">X axis: target position x; Y axis: target position y.</text>
</svg>
"""
    path.write_text(svg)
    return path


def run_target_radar_proof(
    backends: Sequence[str],
    *,
    proof_backend: str = "python1516e",
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
    event_sink: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    backend_matrix = run_target_radar_backend_matrix(
        backends,
        target_radar_steps=target_radar_steps,
        dt=dt,
        backend_options_by_kind=backend_options_by_kind,
    )
    proof_result = run_target_radar_scenario(
        _make_backend_factory(proof_backend, dict((backend_options_by_kind or {}).get(proof_backend, {}))),
        federation_name="TargetRadarProofFederation",
        steps=target_radar_steps,
        dt=dt,
        event_sink=event_sink,
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
    proof_backend: str = "python1516e",
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
    event_sink: Callable[[dict[str, Any]], None] | None = None,
) -> TargetRadarProofPaths:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = run_target_radar_proof(
        backends,
        proof_backend=proof_backend,
        target_radar_steps=target_radar_steps,
        dt=dt,
        backend_options_by_kind=backend_options_by_kind,
        event_sink=event_sink,
    )
    paths = TargetRadarProofPaths(
        output_dir=output_dir,
        summary_json=output_dir / "target_radar_proof_summary.json",
        backend_results_csv=output_dir / "target_radar_backend_results.csv",
        target_truth_csv=output_dir / "target_radar_truth.csv",
        radar_events_csv=output_dir / "target_radar_radar_events.csv",
        track_reports_csv=output_dir / "target_radar_track_reports.csv",
        report_markdown=output_dir / "target_radar_proof_report.md",
        overview_png=output_dir / "target_radar_proof_overview.png",
        timeline_png=output_dir / "target_radar_proof_timeline.png",
        trajectory_png=output_dir / "target_radar_proof_trajectory.png",
        rcs_exchange_png=output_dir / "target_radar_proof_rcs_exchange.png",
        overview_svg=output_dir / "target_radar_proof_overview.svg",
        timeline_svg=output_dir / "target_radar_proof_timeline.svg",
        trajectory_svg=output_dir / "target_radar_proof_trajectory.svg",
    )
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(
        paths.backend_results_csv,
        summary["backend_matrix"]["results"],
        fieldnames=[
            "backend",
            "status",
            "reason",
            "track_reports",
            "first_range_m",
            "last_range_m",
            "range_delta_m",
            "final_time_seconds",
            "backend_kinds",
            "track_ids",
        ],
    )
    _write_csv(
        paths.target_truth_csv,
        summary["proof"]["target_truth_rows"],
        fieldnames=["index", "step_number", "event_name", "time_seconds", "position_x", "position_y", "position_z"],
    )
    radar_fieldnames = [
        "index",
        "event_name",
        "object_name",
        "object_handle",
        "attribute_count",
        "tag_hex",
        "tag_text",
        "track_id",
        "target_name",
        "time_seconds",
        "range_m",
        "bearing_rad",
        "rcs_square_meters",
    ]
    _write_csv(paths.radar_events_csv, summary["proof"]["radar_event_rows"], fieldnames=radar_fieldnames)
    _write_csv(
        paths.track_reports_csv,
        summary["proof"]["track_reports"],
        fieldnames=["track_id", "target_name", "position_x", "position_y", "position_z", "range_m", "bearing_rad", "rcs_square_meters", "time_seconds"],
    )
    _write_markdown(paths.report_markdown, summary, paths)
    _render_png_plots(paths, summary)
    _write_overview_svg(paths.overview_svg, summary)
    _write_timeline_svg(paths.timeline_svg, summary)
    _write_trajectory_svg(paths.trajectory_svg, summary)
    return paths


__all__ = [
    "TargetRadarProofPaths",
    "run_target_radar_proof",
    "write_target_radar_proof_artifacts",
]
