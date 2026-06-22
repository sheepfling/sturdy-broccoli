"""Artifact writers for the two-federate verification suite."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

from hla.verification.two_federate_suite_types import SuitePaths


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path

def _write_callbacks_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["profile", "scenario", "role", "index", "method_name", "snake_name", "reference", "args_json"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_markdown(path: Path, summary: Mapping[str, Any], paths: SuitePaths, *, artifact_summary: Mapping[str, Any]) -> Path:
    scenario_rows = summary["scenario_rows"]
    profiles = summary["profiles"]
    profile_note = (
        "The default profile runs the Python reference RTI; CERTI and Pitch profiles will "
        "record skipped or failed status when their runtimes are unavailable or incomplete."
    )
    lines = [
        "# Two-Federate Suite",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- version: `{summary['suite_version']}`",
        f"- scenarios: `{len(scenario_rows)}`",
        f"- track reports: `{artifact_summary['track_report_count']}`",
        "",
        "## Profiles",
        "",
        "| Profile | Status | Reason | Scenario rows |",
        "| --- | --- | --- | ---: |",
    ]
    for profile in profiles:
        lines.append(f"| {profile['profile']} | {profile['status']} | {profile.get('reason') or ''} | {len(profile.get('scenario_rows', []))} |")
    lines.extend(
        [
            "",
            "## Coverage",
            "",
            "| Scenario | Backend | Callbacks | Key outcome |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for row in scenario_rows:
        lines.append(f"| {row['scenario']} | {row['backend']} | {row['callbacks']} | {row['key_outcome']} |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- JSON summary: `{paths.summary_json.name}`",
            f"- Track CSV: `{paths.track_reports_csv.name}`",
            f"- Callback CSV: `{paths.callbacks_csv.name}`",
            f"- SVG summary: `{paths.summary_svg.name}`",
            f"- SVG timeline: `{paths.timeline_svg.name}`",
            "",
            "## Assessment",
            "",
            f"- {artifact_summary['suite_description']}",
            f"- {profile_note}",
            "- The same scenario structure is reused across the python, CERTI, and Pitch runtime profiles.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_svg(path: Path, summary: Mapping[str, Any], *, artifact_summary: Mapping[str, Any]) -> Path:
    scenario_rows = summary["scenario_rows"]
    reports = artifact_summary["reports"]
    width = max(960, 170 * len(scenario_rows) + 80)
    height = 560
    chart_left = 80
    chart_top = 280
    chart_width = 820
    chart_height = 220
    max_range = max((report["range_m"] for report in reports), default=1.0)
    max_callbacks = max((row["callbacks"] for row in scenario_rows), default=1)
    bar_width = 120
    bar_gap = 20
    bars = []
    for index, row in enumerate(scenario_rows):
        bar_height = 140 * row["callbacks"] / max_callbacks if max_callbacks else 0
        x = 60 + index * (bar_width + bar_gap)
        y = 210 - bar_height
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" fill="#2f6fed" rx="8" />'
            f'<text x="{x + bar_width / 2}" y="230" text-anchor="middle" font-size="12">{row["scenario"]}</text>'
            f'<text x="{x + bar_width / 2}" y="{y - 8:.1f}" text-anchor="middle" font-size="12">{row["callbacks"]}</text>'
        )
    points = []
    for index, report in enumerate(reports):
        x = chart_left + (chart_width * index / max(len(reports) - 1, 1))
        y = chart_top + chart_height - (chart_height * report["range_m"] / max_range)
        points.append((x, y, report))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
    dots = []
    for x, y, report in points:
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#e85d04" />'
            f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="11">{report["track_id"]}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="44" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Two-Federate Verification Suite</text>
  <text x="40" y="72" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{artifact_summary["overview_caption"]}</text>
  <text x="40" y="112" font-size="18" font-family="Helvetica, Arial, sans-serif" fill="#132238">Scenario callback volume</text>
  {"".join(bars)}
  <text x="40" y="268" font-size="18" font-family="Helvetica, Arial, sans-serif" fill="#132238">{artifact_summary["range_chart_title"]}</text>
  <line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <line x1="{chart_left}" y1="{chart_top + chart_height}" x2="{chart_left + chart_width}" y2="{chart_top + chart_height}" stroke="#5b6b7a" stroke-width="2" />
  <text x="{chart_left - 20}" y="{chart_top + 8}" text-anchor="end" font-size="12" fill="#48607a">{max_range:.0f} m</text>
  <text x="{chart_left - 20}" y="{chart_top + chart_height}" text-anchor="end" font-size="12" fill="#48607a">0</text>
  <polyline fill="none" stroke="#e85d04" stroke-width="3" points="{polyline}" />
  {"".join(dots)}
</svg>
"""
    path.write_text(svg)
    return path


def _write_timeline_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    timeline_rows = [row for row in summary["timeline_rows"] if row.get("profile") == "python"]
    scenarios = [
        "exchange_time",
        "synchronization",
        "ownership",
        "negotiated_ownership",
        "save_restore",
        "ddm",
        "time_window_future_exclusion",
        "time_window_restore_state",
    ]
    lane_map = {scenario: index for index, scenario in enumerate(scenarios)}
    lane_height = 64
    top = 110
    width = 1240
    height = top + lane_height * len(scenarios) + 120
    max_sequence = max((int(row["sequence"]) for row in timeline_rows), default=1)
    timeline_caption = "Python profile callback order across both federates and the suite scenarios."
    role_colors = {
        "publisher": "#2f6fed",
        "subscriber": "#e85d04",
        "leader": "#2f6fed",
        "wing": "#e85d04",
        "owner": "#2f6fed",
        "acquirer": "#e85d04",
        "left": "#2f6fed",
        "right": "#e85d04",
        "sender": "#2f6fed",
        "receiver": "#e85d04",
    }
    lane_labels = {
        "exchange_time": "Exchange / time",
        "synchronization": "Synchronization",
        "ownership": "Ownership",
        "negotiated_ownership": "Negotiated ownership",
        "save_restore": "Save / restore",
        "ddm": "DDM region filter",
        "time_window_future_exclusion": "Time window future exclusion",
        "time_window_restore_state": "Time window restore state",
    }
    event_nodes: list[str] = []
    for row in timeline_rows:
        lane_index = lane_map.get(row["scenario"], 0)
        x = 140 + 980 * int(row["sequence"]) / max_sequence
        y = top + lane_index * lane_height + 12
        color = role_colors.get(row["role"], "#132238")
        event_nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color}" opacity="0.92" />'
            f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-size="9" fill="#ffffff">{row["sequence"]}</text>'
        )
    lane_nodes: list[str] = []
    for scenario, lane_index in lane_map.items():
        y = top + lane_index * lane_height
        lane_nodes.append(
            f'<line x1="140" y1="{y}" x2="1140" y2="{y}" stroke="#d8e0ea" stroke-width="2" />'
            f'<text x="36" y="{y + 18}" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#132238">{lane_labels[scenario]}</text>'
        )
    legend = [
        ("publisher", "#2f6fed"),
        ("subscriber", "#e85d04"),
        ("leader", "#2f6fed"),
        ("wing", "#e85d04"),
        ("owner", "#2f6fed"),
        ("acquirer", "#e85d04"),
        ("left", "#2f6fed"),
        ("right", "#e85d04"),
        ("sender", "#2f6fed"),
        ("receiver", "#e85d04"),
    ]
    legend_nodes = []
    for index, (label, color) in enumerate(legend):
        x = 140 + (index % 5) * 180
        y = height - 48 + (index // 5) * 20
        legend_nodes.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" /><text x="{x + 12}" y="{y + 4}" font-size="11" fill="#48607a">{label}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Callback Timeline</text>
  <text x="40" y="68" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{timeline_caption}</text>
  {" ".join(lane_nodes)}
  <line x1="140" y1="{top - 18}" x2="140" y2="{top + lane_height * len(scenarios) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <line x1="1140" y1="{top - 18}" x2="1140" y2="{top + lane_height * len(scenarios) - 8}" stroke="#9fb2c6" stroke-width="2" />
  <text x="140" y="{top - 26}" font-size="12" fill="#48607a">1</text>
  <text x="1128" y="{top - 26}" font-size="12" fill="#48607a">{max_sequence}</text>
  {" ".join(event_nodes)}
  {" ".join(legend_nodes)}
</svg>
"""
    path.write_text(svg)
    return path


__all__ = [
    "_write_callbacks_csv",
    "_write_json",
    "_write_markdown",
    "_write_svg",
    "_write_timeline_svg",
]
