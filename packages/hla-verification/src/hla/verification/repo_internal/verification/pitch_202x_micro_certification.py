"""Bounded Pitch 202X micro comparison packet over the SISO micro showcase."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class Pitch202xMicroCertificationPaths:
    output_dir: Path
    summary_json: Path
    comparison_csv: Path
    report_markdown: Path


PITCH_202X_MICRO_BACKENDS = (
    "pitch-jpype",
    "pitch-py4j",
    "pitch-202x-jpype",
    "pitch-202x-py4j",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


def _command_row(
    run: Mapping[str, Any],
    *,
    artifact_refs: Sequence[str] | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(run["id"]),
        "label": str(run["label"]),
        "command": str(run["command"]),
        "exit_code": int(run["exit_code"]),
        "duration_seconds": round(float(run["duration_seconds"]), 3),
        "ok": int(run["exit_code"]) == 0,
        "artifact_refs": list(artifact_refs or ()),
        "notes": notes,
    }


def _missing_run(run_id: str, label: str, command: str, note: str) -> dict[str, Any]:
    return {
        "id": run_id,
        "label": label,
        "command": command,
        "exit_code": 99,
        "duration_seconds": 0.0,
        "ok": False,
        "artifact_refs": [],
        "notes": note,
    }


def _bridge_name(backend: str) -> str:
    if backend.endswith("-jpype"):
        return "jpype"
    if backend.endswith("-py4j"):
        return "py4j"
    return backend


def _vendor_lane(backend: str) -> str:
    return "real-pitch-2010" if backend in {"pitch-jpype", "pitch-py4j"} else "pitch-202x-adapter"


def build_pitch_202x_micro_certification_summary(
    *,
    project_root: Path,
    micro_summary: Mapping[str, Any],
    command_runs: list[Mapping[str, Any]],
) -> dict[str, Any]:
    rows_by_id = {str(run["id"]): run for run in command_runs}
    preflight_run = rows_by_id.get("preflight")
    micro_run = rows_by_id.get("micro-parity")

    executed_runs = [
        _command_row(
            preflight_run or _missing_run("preflight", "preflight", "./tools/pitch preflight", "Preflight did not execute."),
            artifact_refs=["artifacts/preflight_artifacts/pitch-preflight.json"],
            notes="Pitch runtime and Docker gate for the real 2010 comparison anchor.",
        ),
        _command_row(
            micro_run
            or _missing_run(
                "micro-parity",
                "micro parity",
                "python3 scripts/run_siso_pitch_micro_parity.py --require-real-vendor-preflight",
                "The bounded SISO micro parity lane did not execute.",
            ),
            artifact_refs=[
                "micro_parity/siso_pitch_micro_parity_summary.json",
                "micro_parity/siso_pitch_micro_parity_results.csv",
                "micro_parity/siso_pitch_micro_parity_manifest.json",
                "micro_parity/siso_pitch_micro_parity_report.md",
            ],
            notes="Runs the three-family micro-2 comparison across real Pitch 2010 and bounded Pitch 202X adapter routes.",
        ),
    ]

    results = [dict(row) for row in micro_summary.get("results", [])]
    comparison_index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in results:
        key = (str(row["family"]), _bridge_name(str(row["backend"])))
        lane = _vendor_lane(str(row["backend"]))
        entry = comparison_index.setdefault(
            key,
            {
                "family": str(row["family"]),
                "bridge": _bridge_name(str(row["backend"])),
                "source_packet_2010": None,
                "status_2010": None,
                "reason_2010": None,
                "discoveries_2010": None,
                "reflections_2010": None,
                "interactions_2010": None,
                "source_packet_2025": None,
                "status_2025": None,
                "reason_2025": None,
                "discoveries_2025": None,
                "reflections_2025": None,
                "interactions_2025": None,
            },
        )
        suffix = "2010" if lane == "real-pitch-2010" else "2025"
        entry[f"source_packet_{suffix}"] = str(row["source_packet"])
        entry[f"status_{suffix}"] = str(row["status"])
        entry[f"reason_{suffix}"] = row.get("reason")
        entry[f"discoveries_{suffix}"] = int(row.get("discoveries", 0))
        entry[f"reflections_{suffix}"] = int(row.get("reflections", 0))
        entry[f"interactions_{suffix}"] = int(row.get("interactions", 0))

    comparison_rows = [comparison_index[key] for key in sorted(comparison_index)]
    comparison_complete = all(
        row["status_2010"] == "passed" and row["status_2025"] == "passed"
        for row in comparison_rows
    )
    bounded_202x_rows = [row for row in results if str(row["backend"]).startswith("pitch-202x-")]
    all_ok = all(run["ok"] for run in executed_runs) and comparison_complete and bool(bounded_202x_rows)

    return {
        "suite_name": "pitch-202x-micro-certification",
        "certification_state": "bounded-vendor-comparison" if all_ok else "blocked-or-failed",
        "scope": "Three-family SISO micro-2 comparison across real Pitch 2010 and bounded Pitch 202X adapter routes.",
        "selected_scenario_count": int(micro_summary.get("selected_scenario_count", 0)),
        "passed": int(micro_summary.get("passed", 0)),
        "skipped": int(micro_summary.get("skipped", 0)),
        "failed": int(micro_summary.get("failed", 0)),
        "executed_runs": executed_runs,
        "micro_summary": _jsonable(micro_summary),
        "comparison_rows": comparison_rows,
        "known_boundaries": [
            {
                "area": "adapter-claim-boundary",
                "status": "not-2025-conformance",
                "summary": (
                    "Pitch 202X rows execute through explicit pitch-202x-* adapter routes over the repo Python 2025 runtime. "
                    "They are behavior-discovery evidence only and do not count as IEEE 1516.1-2025 vendor conformance."
                ),
            },
            {
                "area": "micro-scope-boundary",
                "status": "bounded-micro-only",
                "summary": "This packet only covers the existing SISO micro-2 showcase families: Link 16, RPR, and Space.",
            },
            {
                "area": "bridge-anchor",
                "status": "real-vendor-anchor",
                "summary": (
                    "Real vendor evidence in this packet is limited to Pitch 2010 `pitch-jpype` and `pitch-py4j` rows used as a comparison anchor."
                ),
            },
        ],
    }


def _write_comparison_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    fieldnames = [
        "family",
        "bridge",
        "source_packet_2010",
        "status_2010",
        "reason_2010",
        "discoveries_2010",
        "reflections_2010",
        "interactions_2010",
        "source_packet_2025",
        "status_2025",
        "reason_2025",
        "discoveries_2025",
        "reflections_2025",
        "interactions_2025",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _jsonable(row.get(key, "")) for key in fieldnames})
    return path


def _render_markdown(summary: Mapping[str, Any], paths: Pitch202xMicroCertificationPaths) -> str:
    lines = [
        "# Pitch 202X Micro Certification",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- state: `{summary['certification_state']}`",
        f"- scope: `{summary['scope']}`",
        f"- selected scenarios: `{summary['selected_scenario_count']}`",
        f"- passed: `{summary['passed']}`",
        f"- skipped: `{summary['skipped']}`",
        f"- failed: `{summary['failed']}`",
        f"- summary json: `{paths.summary_json.name}`",
        f"- comparison csv: `{paths.comparison_csv.name}`",
        f"- underlying micro packet: `micro_parity/siso_pitch_micro_parity_report.md`",
        "",
        "## Executed Runs",
        "",
        "| Step | Command | Exit | Notes |",
        "| --- | --- | ---: | --- |",
    ]
    for row in summary["executed_runs"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["label"]),
                    f"`{row['command']}`",
                    str(row["exit_code"]),
                    str(row.get("notes") or ""),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Side-by-Side Comparison",
            "",
            "| Family | Bridge | 2010 Status | 2025 Status | 2010 Counts | 2025 Counts |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in summary["comparison_rows"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["family"]),
                    str(row["bridge"]),
                    str(row["status_2010"] or "n/a"),
                    str(row["status_2025"] or "n/a"),
                    f"d={row['discoveries_2010']} r={row['reflections_2010']} i={row['interactions_2010']}",
                    f"d={row['discoveries_2025']} r={row['reflections_2025']} i={row['interactions_2025']}",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- `pitch-jpype` and `pitch-py4j` are the real Pitch 2010 comparison anchor.",
            "- `pitch-202x-jpype` and `pitch-202x-py4j` are bounded adapter routes over the repo Python 2025 runtime.",
            "- This packet is behavior-discovery evidence and does not claim IEEE 1516.1-2025 vendor conformance.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_pitch_202x_micro_certification(
    output_dir: str | Path,
    *,
    project_root: Path,
    micro_summary: Mapping[str, Any],
    command_runs: list[Mapping[str, Any]],
) -> Pitch202xMicroCertificationPaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = Pitch202xMicroCertificationPaths(
        output_dir=out,
        summary_json=out / "pitch_202x_micro_certification_summary.json",
        comparison_csv=out / "pitch_202x_micro_certification_comparison.csv",
        report_markdown=out / "pitch_202x_micro_certification_report.md",
    )
    summary = build_pitch_202x_micro_certification_summary(
        project_root=project_root,
        micro_summary=micro_summary,
        command_runs=command_runs,
    )
    paths.summary_json.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_comparison_csv(paths.comparison_csv, summary["comparison_rows"])
    paths.report_markdown.write_text(_render_markdown(summary, paths), encoding="utf-8")
    return paths


__all__ = [
    "PITCH_202X_MICRO_BACKENDS",
    "Pitch202xMicroCertificationPaths",
    "build_pitch_202x_micro_certification_summary",
    "write_pitch_202x_micro_certification",
]
