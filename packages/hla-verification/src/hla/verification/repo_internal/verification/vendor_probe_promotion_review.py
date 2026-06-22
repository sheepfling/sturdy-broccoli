"""Promotion-review artifacts for repeated-run vendor probe evidence."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .vendor_gap_profiles import get_vendor_gap_profile


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "analysis").exists() and (parent / "tools").exists():
            return parent
    raise RuntimeError("Could not locate repository root")


REPO_ROOT = _repo_root()


@dataclass(frozen=True)
class VendorProbePromotionReviewPaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


_PROFILE_SPECS: tuple[dict[str, str], ...] = (
    {
        "profile": "certi-save-restore-probe",
        "vendor": "certi",
        "area": "save_restore",
        "docs_ref": "docs/backend_conformance_matrix.md",
        "documented_state": "narrow runtime probe until repeated real-host evidence proves the save/restore path stable enough to promote",
    },
    {
        "profile": "certi-ddm-probe",
        "vendor": "certi",
        "area": "ddm",
        "docs_ref": "docs/backend_conformance_matrix.md",
        "documented_state": "narrow runtime probe until repeated real-host evidence proves it stable enough to promote",
    },
    {
        "profile": "pitch-save-restore-probe",
        "vendor": "pitch",
        "area": "save_restore",
        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        "documented_state": "deeper runtime probe for the Pitch save/restore path, not yet a promoted stable parity slice",
    },
    {
        "profile": "pitch-ddm-probe",
        "vendor": "pitch",
        "area": "ddm",
        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        "documented_state": "deeper runtime probe, not yet a promoted stable parity slice",
    },
    {
        "profile": "pitch-negotiated-probe",
        "vendor": "pitch",
        "area": "negotiated_ownership",
        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        "documented_state": "deeper runtime probe for a currently bridge-divergent path, not yet a promoted stable parity slice",
    },
    {
        "profile": "pitch-time-window-probe",
        "vendor": "pitch",
        "area": "time_window_future_exclusion",
        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        "documented_state": "two-federate-safe lookahead-window probe for vendor credence, not a replacement for the broader Python route proof ladder",
    },
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _gap_profile_name(profile: str) -> str | None:
    if not profile.endswith("-probe"):
        return None
    return profile[: -len("-probe")]


def _review_decision(stability: dict[str, Any] | None, *, gap_status: str | None) -> tuple[str, str]:
    if stability is None:
        return ("missing-evidence", "no repeated-run stability artifact is present")
    readiness = stability.get("promotion_readiness")
    if readiness == "candidate":
        if gap_status == "bridge-divergent":
            return (
                "blocked-by-documented-gap",
                "repeated-run stability evidence exists, but the documented vendor/runtime divergence still blocks promotion",
            )
        return ("candidate-review", "repeated-run stability evidence exists; perform clause-level parity review before promotion")
    if readiness == "needs-more-runs":
        return ("needs-more-runs", "the probe is green so far but below the current repetition floor")
    if readiness == "unstable":
        return ("unstable", "at least one repeated-run attempt failed")
    if readiness == "incomplete":
        return ("incomplete", "requested repeated-run attempts did not all produce artifacts")
    return ("unknown", "promotion readiness is not recognized")


def _next_action(
    *,
    profile: str,
    review_decision: str,
    docs_ref: str,
    gap_profile_name: str | None,
    gap_status: str | None,
) -> str:
    gap = None
    if gap_profile_name is not None:
        try:
            gap = get_vendor_gap_profile(gap_profile_name)
        except ValueError:
            gap = None
    review_command = None if gap is None or not gap.next_steps else gap.next_steps[-1]
    probe_command = None if gap is None or len(gap.next_steps) < 2 else gap.next_steps[1]

    if review_decision == "candidate-review":
        return f"compare {profile} against {docs_ref} and promote only if clause-level parity is now defensible"
    if review_decision == "blocked-by-documented-gap":
        if gap_status:
            return f"resolve the documented {gap_status} state before promotion; keep the lane at probe status"
        return "resolve the documented runtime gap before promotion; keep the lane at probe status"
    if review_decision == "needs-more-runs":
        return review_command or "collect more repeated-run probe evidence before promotion review"
    if review_decision == "missing-evidence":
        return review_command or probe_command or "run the supported probe-review route to produce stability evidence"
    if review_decision == "unstable":
        return probe_command or "debug the probe failure path before collecting more stability evidence"
    if review_decision == "incomplete":
        return review_command or "rerun the repeated probe review until every requested attempt produces an artifact"
    return "inspect the stability artifact and current docs before making a promotion claim"


def build_vendor_probe_promotion_review() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for spec in _PROFILE_SPECS:
        summary_path = REPO_ROOT / "analysis" / "vendor_probe_stability" / spec["profile"] / "vendor_probe_stability_summary.json"
        stability = _load_json(summary_path)
        gap_status = None
        gap_profile_name = _gap_profile_name(spec["profile"])
        if gap_profile_name is not None:
            try:
                gap_status = get_vendor_gap_profile(gap_profile_name).status
            except ValueError:
                gap_status = None
        decision, note = _review_decision(stability, gap_status=gap_status)
        rows.append(
            {
                **spec,
                "stability_path": str(summary_path.relative_to(REPO_ROOT)),
                "gap_profile": gap_profile_name,
                "gap_status": gap_status,
                "stability_present": stability is not None,
                "promotion_readiness": None if stability is None else stability.get("promotion_readiness"),
                "stable": None if stability is None else stability.get("stable"),
                "attempt_count": None if stability is None else stability.get("attempt_count"),
                "success_count": None if stability is None else stability.get("success_count"),
                "review_decision": decision,
                "review_note": note,
                "next_action": _next_action(
                    profile=spec["profile"],
                    review_decision=decision,
                    docs_ref=spec["docs_ref"],
                    gap_profile_name=gap_profile_name,
                    gap_status=gap_status,
                ),
            }
        )
    candidate_count = sum(1 for row in rows if row["review_decision"] == "candidate-review")
    return {
        "suite_name": "vendor-probe-promotion-review",
        "profiles": rows,
        "candidate_count": candidate_count,
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> Path:
    lines = [
        "# Vendor Probe Promotion Review",
        "",
        f"- candidate count: `{summary['candidate_count']}`",
        "",
        "| Profile | Vendor | Area | Readiness | Decision | Attempts | Docs |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in summary["profiles"]:
        lines.append(
            f"| {row['profile']} | {row['vendor']} | {row['area']} | "
            f"{row['promotion_readiness'] or 'missing'} | {row['review_decision']} | "
            f"{'' if row['attempt_count'] is None else row['attempt_count']} | {row['docs_ref']} |"
        )
    lines.append("")
    for row in summary["profiles"]:
        lines.append(f"- `{row['profile']}`: {row['review_note']}")
        lines.append(f"  - next: {row['next_action']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_vendor_probe_promotion_review(output_dir: Path | str) -> VendorProbePromotionReviewPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorProbePromotionReviewPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_probe_promotion_review_summary.json",
        report_markdown=output_path / "vendor_probe_promotion_review_report.md",
    )
    summary = build_vendor_probe_promotion_review()
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "VendorProbePromotionReviewPaths",
    "build_vendor_probe_promotion_review",
    "write_vendor_probe_promotion_review",
]
