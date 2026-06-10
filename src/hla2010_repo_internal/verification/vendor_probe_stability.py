"""Repeated-run stability artifacts for vendor probe profiles."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROMOTION_MIN_REPEAT_COUNT = 5

PROFILE_OPERATOR_COMMANDS: dict[str, str] = {
    "certi-compare": "./certi-easy smoke compare",
    "certi-save-restore": "./certi-easy save-restore",
    "certi-save-restore-probe": "./certi-easy save-restore-probe",
    "certi-ddm": "./certi-easy ddm",
    "certi-ddm-probe": "./certi-easy ddm-probe",
    "pitch": "./pitch smoke",
    "pitch-smoke": "./pitch smoke",
    "pitch-save-restore": "./pitch save-restore",
    "pitch-save-restore-probe": "./pitch save-restore-probe",
    "pitch-ddm": "./pitch ddm",
    "pitch-ddm-probe": "./pitch ddm-probe",
    "pitch-negotiated": "./pitch negotiated",
    "pitch-negotiated-probe": "./pitch negotiated-probe",
}


@dataclass(frozen=True)
class VendorProbeStabilityPaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


def profile_evidence_tier(profile: str) -> str:
    if profile.endswith("-probe"):
        return "probe"
    if profile in {
        "certi-save-restore",
        "certi-ddm",
        "pitch-save-restore",
        "pitch-ddm",
        "pitch-negotiated",
    }:
        return "known-gap"
    if profile in {
        "certi",
        "certi-patched",
        "certi-upstream",
        "certi-compare",
        "pitch",
        "pitch-smoke",
        "pitch-verify",
        "matrix",
        "all",
    }:
        return "promoted"
    return "other"


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


def canonical_operator_command(profile: str) -> str:
    return PROFILE_OPERATOR_COMMANDS.get(profile, f"./scripts/ci/vendor_green.sh {profile}")


def promotion_readiness(*, repeat_count: int, attempt_count: int, failure_count: int) -> tuple[str, str]:
    if failure_count > 0:
        return ("unstable", "at least one repeated-run attempt failed")
    if attempt_count < repeat_count:
        return ("incomplete", "not every requested repeated-run attempt produced an artifact")
    if repeat_count < PROMOTION_MIN_REPEAT_COUNT:
        return ("needs-more-runs", f"repeat count is below the promotion floor of {PROMOTION_MIN_REPEAT_COUNT}")
    return ("candidate", "repeated-run stability evidence is present; promotion still requires clause-level parity review")


def build_vendor_probe_stability_summary(
    *,
    profile: str,
    repeat_count: int,
    command: str,
    executor_command: str | None = None,
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    success_count = sum(1 for item in attempts if int(item["exit_code"]) == 0)
    failure_count = len(attempts) - success_count
    durations = [int(item["duration_seconds"]) for item in attempts]
    readiness, readiness_note = promotion_readiness(
        repeat_count=repeat_count,
        attempt_count=len(attempts),
        failure_count=failure_count,
    )
    return {
        "suite_name": "vendor-probe-stability",
        "profile": profile,
        "evidence_tier": profile_evidence_tier(profile),
        "command": command,
        "executor_command": executor_command or command,
        "repeat_count": repeat_count,
        "attempt_count": len(attempts),
        "success_count": success_count,
        "failure_count": failure_count,
        "stable": failure_count == 0 and len(attempts) == repeat_count,
        "promotion_readiness": readiness,
        "promotion_note": readiness_note,
        "min_duration_seconds": min(durations) if durations else None,
        "max_duration_seconds": max(durations) if durations else None,
        "attempts": [_jsonable(item) for item in attempts],
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> Path:
    lines = [
        "# Vendor Probe Stability",
        "",
        f"- profile: `{summary['profile']}`",
        f"- evidence tier: `{summary['evidence_tier']}`",
        f"- command: `{summary['command']}`",
        f"- executor command: `{summary['executor_command']}`",
        f"- repeat count: `{summary['repeat_count']}`",
        f"- attempt count: `{summary['attempt_count']}`",
        f"- success count: `{summary['success_count']}`",
        f"- failure count: `{summary['failure_count']}`",
        f"- stable: `{summary['stable']}`",
        f"- promotion readiness: `{summary['promotion_readiness']}`",
        f"- promotion note: {summary['promotion_note']}",
        "",
        "## Attempts",
        "",
        "| Iteration | Exit | Duration (s) |",
        "| ---: | ---: | ---: |",
    ]
    for item in summary["attempts"]:
        lines.append(
            f"| {item['iteration']} | {item['exit_code']} | {item['duration_seconds']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_vendor_probe_stability(
    output_dir: Path | str,
    *,
    profile: str,
    repeat_count: int,
    command: str,
    executor_command: str | None = None,
    attempts: list[dict[str, Any]],
) -> VendorProbeStabilityPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorProbeStabilityPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_probe_stability_summary.json",
        report_markdown=output_path / "vendor_probe_stability_report.md",
    )
    summary = build_vendor_probe_stability_summary(
        profile=profile,
        repeat_count=repeat_count,
        command=command,
        executor_command=executor_command,
        attempts=attempts,
    )
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "PROMOTION_MIN_REPEAT_COUNT",
    "PROFILE_OPERATOR_COMMANDS",
    "VendorProbeStabilityPaths",
    "build_vendor_probe_stability_summary",
    "canonical_operator_command",
    "profile_evidence_tier",
    "promotion_readiness",
    "write_vendor_probe_stability",
]
