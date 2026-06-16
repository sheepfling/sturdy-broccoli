"""GitHub-friendly summary rendering for normalized vendor runtime status."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VendorRuntimeJobSummaryPaths:
    status_dir: Path
    parity_dir: Path | None = None


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _summary_paths(status_dir: Path) -> list[Path]:
    if not status_dir.exists():
        return []
    return sorted(status_dir.glob("*/vendor_runtime_status_summary.json"))


def _profile_name(summary_path: Path) -> str:
    parent = summary_path.parent.name
    if parent == "repo_green":
        return "repo_green"
    prefix = "vendor_green_"
    if parent.startswith(prefix):
        return parent[len(prefix) :]
    return parent


def _evidence_tier(profile: str) -> tuple[str, str]:
    if profile == "repo_green":
        return ("aggregate", "repo-green aggregate lane")
    if profile.endswith("_probe"):
        return ("probe", "narrow executable probe evidence")
    if profile in {
        "certi_save_restore",
        "certi_ddm",
        "pitch_save_restore",
        "pitch_ddm",
        "pitch_negotiated",
    }:
        return ("known-gap", "explicit known-gap route")
    if profile in {
        "certi",
        "certi_patched",
        "certi_upstream",
        "certi_compare",
        "pitch",
        "pitch_smoke",
        "pitch_verify",
        "matrix",
        "all",
    }:
        return ("promoted", "promoted vendor lane")
    return ("other", "unclassified runtime lane")


def _render_vendor_rows(summary: dict[str, Any]) -> list[str]:
    rows = [
        "| Vendor | Classification | Environment | Blocked Reason | Next Steps |",
        "| --- | --- | --- | --- | --- |",
    ]
    for vendor in summary.get("vendors", []):
        next_steps = vendor.get("next_steps") or []
        rendered_next = "<br>".join(f"`{step}`" for step in next_steps) if next_steps else ""
        rows.append(
            f"| {vendor.get('vendor', '')} | {vendor.get('classification', '')} | "
            f"{vendor.get('environment', '') or ''} | {vendor.get('blocked_reason', '') or ''} | "
            f"{rendered_next} |"
        )
    return rows


def _render_blocked_details(summary: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for vendor in summary.get("vendors", []):
        blocked_checks = vendor.get("blocked_checks") or []
        if not blocked_checks:
            continue
        lines.append(f"Blocked checks for `{vendor.get('vendor', 'unknown')}`:")
        for check in blocked_checks:
            detail = check.get("detail") or check.get("message") or "blocked"
            lines.append(f"- `{check.get('name', 'unknown')}`: {detail}")
        lines.append("")
    return lines


def _render_required_expectations(summary: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for vendor in summary.get("vendors", []):
        required_markers = vendor.get("required_markers") or {}
        required_ports = vendor.get("required_ports") or {}
        if required_markers:
            lines.append(f"Required markers for `{vendor.get('vendor', 'unknown')}`:")
            for name, marker in required_markers.items():
                lines.append(f"- `{name}`: `{marker}`")
            lines.append("")
        if required_ports:
            lines.append(f"Required ports for `{vendor.get('vendor', 'unknown')}`:")
            for name, port in required_ports.items():
                host = port.get("host") or "unknown-host"
                number = port.get("port")
                status = port.get("status")
                rendered_status = f" [{status}]" if status else ""
                lines.append(f"- `{name}`: `{host}:{number}`{rendered_status}")
            lines.append("")
    return lines


def _render_probe_stability(payload: dict[str, Any]) -> list[str]:
    probe_stability = payload.get("probe_stability") or {}
    if not isinstance(probe_stability, dict):
        return []
    rows = [
        "## Probe Stability",
        "",
        "| Profile | Stable | Success / Attempts | Evidence Tier | Artifact |",
        "| --- | --- | --- | --- | --- |",
    ]
    has_any = False
    for profile_name, item in sorted(probe_stability.items()):
        has_any = True
        if item is None:
            rows.append(f"| {profile_name} | n/a | n/a | probe | missing |")
            continue
        rows.append(
            f"| {profile_name} | {item.get('stable')} | "
            f"{item.get('success_count')} / {item.get('attempt_count')} | "
            f"{item.get('evidence_tier')} / {item.get('promotion_readiness')} | {item.get('path')} |"
        )
    if not has_any:
        return []
    rows.append("")
    return rows


def _render_probe_promotion_review(payload: dict[str, Any]) -> list[str]:
    review = payload.get("probe_promotion_review")
    if not isinstance(review, dict):
        return []
    rows = [
        "## Promotion Review",
        "",
        f"- candidate count: `{review.get('candidate_count', 'unknown')}`",
        f"- artifact: `{review.get('path', 'unknown')}`",
        "",
    ]
    for item in review.get("profiles") or []:
        rows.append(
            f"- `{item.get('profile')}`: decision `{item.get('review_decision')}`, "
            f"readiness `{item.get('promotion_readiness') or 'missing'}`, docs `{item.get('docs_ref')}`"
        )
        if item.get("next_action"):
            rows.append(f"  - next: {item.get('next_action')}")
    rows.append("")
    return rows


def build_vendor_runtime_job_summary(paths: VendorRuntimeJobSummaryPaths) -> str:
    lines = [
        "# Vendor Runtime Status",
        "",
        "This summary is generated from the normalized vendor runtime status artifacts.",
        "",
    ]
    summary_paths = _summary_paths(paths.status_dir)
    if not summary_paths:
        lines.append(f"No runtime status summaries were found under `{paths.status_dir}`.")
        return "\n".join(lines) + "\n"

    for summary_path in summary_paths:
        payload = _load_json(summary_path)
        profile = _profile_name(summary_path)
        evidence_tier, evidence_note = _evidence_tier(profile)
        if payload is None:
            lines.append(f"## {summary_path.parent.name}")
            lines.append("")
            lines.append(f"Could not read `{summary_path}`.")
            lines.append("")
            continue
        lines.append(f"## {summary_path.parent.name}")
        lines.append("")
        lines.append(f"- lane: `{payload.get('lane', 'unknown')}`")
        lines.append(f"- evidence tier: `{evidence_tier}`")
        lines.append(f"- evidence note: {evidence_note}")
        lines.append(f"- overall classification: `{payload.get('overall_classification', 'unknown')}`")
        lines.append(f"- artifact: `{summary_path}`")
        lines.append("")
        lines.extend(_render_vendor_rows(payload))
        lines.append("")
        lines.extend(_render_blocked_details(payload))
        lines.extend(_render_required_expectations(payload))

    if paths.parity_dir is not None:
        parity_summary = paths.parity_dir / "vendor_parity_artifacts_summary.json"
        payload = _load_json(parity_summary)
        if payload is not None:
            lines.append("## Parity Packet")
            lines.append("")
            lines.append(f"- artifact count: `{payload.get('artifact_count', 'unknown')}`")
            lines.append(f"- missing required count: `{payload.get('missing_required_count', 'unknown')}`")
            lines.append(f"- summary: `{parity_summary}`")
            lines.append("")
            lines.extend(_render_probe_stability(payload))
            lines.extend(_render_probe_promotion_review(payload))

    return "\n".join(lines) + "\n"


__all__ = ["VendorRuntimeJobSummaryPaths", "build_vendor_runtime_job_summary"]
