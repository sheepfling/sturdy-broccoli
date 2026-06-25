"""Compare real Pitch 2010 FOM smoke with pitch-202x adapter FOM smoke."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PitchFomSmokeComparePaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


def _classify_packet(real_rows: list[dict[str, Any]], adapter_rows: list[dict[str, Any]]) -> str:
    real_green = all(row["status"] == "lookup-green" for row in real_rows)
    adapter_green = all(row["status"] == "lookup-green" for row in adapter_rows)
    if real_green and adapter_green:
        return "green-both"
    if not real_green and adapter_green:
        return "real-only-failure"
    if not real_green and not adapter_green:
        return "shared-failure"
    return "adapter-only-failure"


def _runtime_status(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for row in rows:
        payload[str(row["runtime_kind"])] = {
            "status": str(row["status"]),
            "error_type": row.get("error_type"),
            "error_message": row.get("error_message"),
            "evidence_mode": row.get("evidence_mode"),
            "spec_name": row.get("spec_name"),
        }
    return payload


def build_pitch_fom_smoke_comparison(
    real_summary: dict[str, Any],
    adapter_summary: dict[str, Any],
) -> dict[str, Any]:
    real_by_packet: dict[str, list[dict[str, Any]]] = {}
    adapter_by_packet: dict[str, list[dict[str, Any]]] = {}
    for row in real_summary["rows"]:
        real_by_packet.setdefault(str(row["packet_id"]), []).append(row)
    for row in adapter_summary["rows"]:
        adapter_by_packet.setdefault(str(row["packet_id"]), []).append(row)

    packet_ids = tuple(sorted(set(real_by_packet) | set(adapter_by_packet)))
    packet_rows: list[dict[str, Any]] = []
    bucket_counts = {
        "green-both": 0,
        "real-only-failure": 0,
        "shared-failure": 0,
        "adapter-only-failure": 0,
    }
    for packet_id in packet_ids:
        real_rows = real_by_packet.get(packet_id, [])
        adapter_rows = adapter_by_packet.get(packet_id, [])
        example = real_rows[0] if real_rows else adapter_rows[0]
        bucket = _classify_packet(real_rows, adapter_rows)
        bucket_counts[bucket] += 1
        packet_rows.append(
            {
                "packet_id": packet_id,
                "scenario_family": str(example["scenario_family"]),
                "load_mode": str(example["load_mode"]),
                "notes": str(example["notes"]),
                "comparison_bucket": bucket,
                "real_runtime_rows": _runtime_status(real_rows),
                "adapter_runtime_rows": _runtime_status(adapter_rows),
            }
        )

    return {
        "suite_name": "pitch-fom-smoke-compare",
        "real_suite_name": str(real_summary["suite_name"]),
        "adapter_suite_name": str(adapter_summary["suite_name"]),
        "packet_count": len(packet_rows),
        "bucket_counts": bucket_counts,
        "packet_rows": packet_rows,
    }


def render_pitch_fom_smoke_compare_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Pitch FOM Smoke Comparison",
        "",
        f"- packet count: `{summary['packet_count']}`",
        f"- green both: `{summary['bucket_counts']['green-both']}`",
        f"- real-only failure: `{summary['bucket_counts']['real-only-failure']}`",
        f"- shared failure: `{summary['bucket_counts']['shared-failure']}`",
        f"- adapter-only failure: `{summary['bucket_counts']['adapter-only-failure']}`",
        "",
        "| Packet | Family | Load mode | Bucket | Real Pitch 2010 | Pitch 202X adapters |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in summary["packet_rows"]:
        real_status = ", ".join(
            f"{runtime}={payload['status']}" for runtime, payload in sorted(row["real_runtime_rows"].items())
        ) or "n/a"
        adapter_status = ", ".join(
            f"{runtime}={payload['status']}" for runtime, payload in sorted(row["adapter_runtime_rows"].items())
        ) or "n/a"
        lines.append(
            f"| {row['packet_id']} | {row['scenario_family']} | {row['load_mode']} | {row['comparison_bucket']} | "
            f"{real_status} | {adapter_status} |"
        )
    lines.extend(
        [
            "",
            "## Learning Notes",
            "",
            "- `green-both` means the family survives both the real Pitch 2010 bridge lane and the explicit `pitch-202x-*` adapter lane.",
            "- `real-only-failure` means the problem is specific to the real Pitch vendor-runtime lane, not the repo Python 2025 adapter path.",
            "- `shared-failure` means the issue survives even through the `pitch-202x-*` wrappers and is worth treating as a broader family or lookup quirk.",
            "",
            "## Detailed Failures",
            "",
        ]
    )
    failures = [row for row in summary["packet_rows"] if row["comparison_bucket"] != "green-both"]
    if not failures:
        lines.append("- none")
    else:
        for row in failures:
            lines.append(f"### {row['packet_id']}")
            lines.append("")
            lines.append(f"- family: `{row['scenario_family']}`")
            lines.append(f"- load mode: `{row['load_mode']}`")
            lines.append(f"- bucket: `{row['comparison_bucket']}`")
            for label, runtime_rows in (
                ("real", row["real_runtime_rows"]),
                ("adapter", row["adapter_runtime_rows"]),
            ):
                if not runtime_rows:
                    continue
                for runtime, payload in sorted(runtime_rows.items()):
                    if payload["status"] == "lookup-green":
                        continue
                    message = payload.get("error_message") or ""
                    lines.append(
                        f"- {label} `{runtime}`: `{payload.get('error_type', 'unknown')}` {message}".rstrip()
                    )
            lines.append("")
    return "\n".join(lines) + "\n"


def write_pitch_fom_smoke_comparison(
    output_dir: str | Path,
    real_summary: dict[str, Any],
    adapter_summary: dict[str, Any],
) -> PitchFomSmokeComparePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = PitchFomSmokeComparePaths(
        output_dir=output_path,
        summary_json=output_path / "pitch_fom_smoke_compare_summary.json",
        report_markdown=output_path / "pitch_fom_smoke_compare_report.md",
    )
    summary = build_pitch_fom_smoke_comparison(real_summary, adapter_summary)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths.report_markdown.write_text(render_pitch_fom_smoke_compare_markdown(summary), encoding="utf-8")
    return paths


__all__ = [
    "PitchFomSmokeComparePaths",
    "build_pitch_fom_smoke_comparison",
    "render_pitch_fom_smoke_compare_markdown",
    "write_pitch_fom_smoke_comparison",
]
