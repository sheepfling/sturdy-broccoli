"""Repeated-run stability artifacts for vendor probe profiles."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROMOTION_MIN_REPEAT_COUNT = 5

PROFILE_OPERATOR_COMMANDS: dict[str, str] = {
    "certi-compare": "./tools/certi-easy smoke compare",
    "certi-save-restore": "./tools/certi-easy save-restore",
    "certi-save-restore-probe": "./tools/certi-easy save-restore-probe",
    "certi-ddm": "./tools/certi-easy ddm",
    "certi-ddm-probe": "./tools/certi-easy ddm-probe",
    "pitch": "./tools/pitch smoke",
    "pitch-smoke": "./tools/pitch smoke",
    "pitch-save-restore": "./tools/pitch save-restore",
    "pitch-save-restore-probe": "./tools/pitch save-restore-probe",
    "pitch-ddm": "./tools/pitch ddm",
    "pitch-ddm-probe": "./tools/pitch ddm-probe",
    "pitch-negotiated": "./tools/pitch negotiated",
    "pitch-negotiated-probe": "./tools/pitch negotiated-probe",
    "pitch-time-window-probe": "./tools/pitch time-window-probe",
    "pitch-time-window-restore-state-probe": "./tools/pitch time-window-restore-state-probe",
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


def parse_pytest_summary_text(text: str) -> dict[str, int] | None:
    summary_line: str | None = None
    for raw_line in reversed(text.splitlines()):
        line = raw_line.strip()
        if not line:
            continue
        if any(token in line for token in (" passed", " failed", " error", " skipped", " xfailed", " xpassed")):
            summary_line = line
            break
    if summary_line is None:
        return None
    counts = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    for amount, label in re.findall(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed)\b", summary_line):
        normalized = "error" if label == "errors" else label
        counts[normalized] += int(amount)
    if not any(counts.values()):
        return None
    return counts


def _attempt_outcome_counts(attempt: dict[str, Any]) -> dict[str, int] | None:
    summary_texts: list[str] = []
    for key in ("stdout_path", "stderr_path"):
        path_text = attempt.get(key)
        if not path_text:
            continue
        path = Path(str(path_text))
        if path.exists():
            summary_texts.append(path.read_text(encoding="utf-8", errors="replace"))
    if not summary_texts:
        return None
    merged = "\n".join(summary_texts)
    return parse_pytest_summary_text(merged)


def _outcome_signature(counts: dict[str, int] | None) -> str | None:
    if counts is None:
        return None
    ordered = [f"{key}={counts[key]}" for key in ("passed", "failed", "error", "skipped", "xfailed", "xpassed")]
    return ",".join(ordered)


def promotion_readiness(
    *,
    repeat_count: int,
    attempt_count: int,
    failure_count: int,
    semantic_issue: str | None,
) -> tuple[str, str]:
    if failure_count > 0:
        return ("unstable", "at least one repeated-run attempt failed")
    if semantic_issue == "xpass-present":
        return ("semantic-instability", "repeated runs stayed exit-green but produced at least one xpass outcome")
    if semantic_issue == "mixed-outcomes":
        return ("semantic-instability", "repeated runs stayed exit-green but pytest outcome signatures drifted between attempts")
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
    enriched_attempts: list[dict[str, Any]] = []
    aggregate_outcomes = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    outcome_signatures: list[str] = []
    has_xpass = False
    for item in attempts:
        counts = _attempt_outcome_counts(item)
        enriched = dict(item)
        enriched["pytest_outcomes"] = counts
        enriched["pytest_outcome_signature"] = _outcome_signature(counts)
        if counts is not None:
            for key in aggregate_outcomes:
                aggregate_outcomes[key] += counts[key]
            if counts["xpassed"] > 0:
                has_xpass = True
        if enriched["pytest_outcome_signature"] is not None:
            outcome_signatures.append(str(enriched["pytest_outcome_signature"]))
        enriched_attempts.append(enriched)
    semantic_issue = None
    unique_signatures = set(outcome_signatures)
    if has_xpass:
        semantic_issue = "xpass-present"
    elif len(unique_signatures) > 1:
        semantic_issue = "mixed-outcomes"
    readiness, readiness_note = promotion_readiness(
        repeat_count=repeat_count,
        attempt_count=len(attempts),
        failure_count=failure_count,
        semantic_issue=semantic_issue,
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
        "semantic_stable": semantic_issue is None,
        "semantic_issue": semantic_issue,
        "pytest_outcome_totals": aggregate_outcomes,
        "promotion_readiness": readiness,
        "promotion_note": readiness_note,
        "min_duration_seconds": min(durations) if durations else None,
        "max_duration_seconds": max(durations) if durations else None,
        "attempts": [_jsonable(item) for item in enriched_attempts],
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
        f"- semantic stable: `{summary['semantic_stable']}`",
        f"- semantic issue: `{summary['semantic_issue']}`",
        f"- promotion readiness: `{summary['promotion_readiness']}`",
        f"- promotion note: {summary['promotion_note']}",
        "",
        "## Pytest Outcomes",
        "",
        f"- passed: `{summary['pytest_outcome_totals']['passed']}`",
        f"- failed: `{summary['pytest_outcome_totals']['failed']}`",
        f"- error: `{summary['pytest_outcome_totals']['error']}`",
        f"- skipped: `{summary['pytest_outcome_totals']['skipped']}`",
        f"- xfailed: `{summary['pytest_outcome_totals']['xfailed']}`",
        f"- xpassed: `{summary['pytest_outcome_totals']['xpassed']}`",
        "",
        "## Attempts",
        "",
        "| Iteration | Exit | Duration (s) | Pytest outcome |",
        "| ---: | ---: | ---: | --- |",
    ]
    for item in summary["attempts"]:
        lines.append(
            f"| {item['iteration']} | {item['exit_code']} | {item['duration_seconds']} | {item.get('pytest_outcome_signature') or 'n/a'} |"
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
    "parse_pytest_summary_text",
    "profile_evidence_tier",
    "promotion_readiness",
    "write_vendor_probe_stability",
]
