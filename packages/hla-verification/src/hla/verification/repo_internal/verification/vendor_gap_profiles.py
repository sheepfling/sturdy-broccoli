"""Known-gap vendor runtime profiles."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VendorGapProfile:
    profile: str
    vendor: str
    area: str
    classification: str
    status: str
    summary: str
    docs_ref: str
    recommended_operator_route: str
    next_steps: tuple[str, ...]
    operator_state: str | None = None
    blocker_summary: str | None = None
    operator_artifact_refs: tuple[str, ...] = ()


_PROFILES: dict[str, VendorGapProfile] = {
    "certi-save-restore": VendorGapProfile(
        profile="certi-save-restore",
        vendor="certi",
        area="save_restore",
        classification="known-gap",
        status="not-promoted",
        summary="CERTI real-runtime save/restore is not yet promoted as an executable matrix slice in this workspace.",
        docs_ref="packages/hla-backend-certi/docs/certi_runtime_limitations.md",
        recommended_operator_route="./tools/certi-easy save-restore",
        next_steps=(
            "./tools/certi-easy preflight",
            "./tools/certi-easy save-restore-probe",
            "./tools/certi-easy save-restore-review 5",
        ),
    ),
    "pitch-save-restore": VendorGapProfile(
        profile="pitch-save-restore",
        vendor="pitch",
        area="save_restore",
        classification="known-gap",
        status="not-promoted",
        summary="Pitch real-runtime save/restore is not yet promoted as an executable matrix slice in this workspace.",
        docs_ref="packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        recommended_operator_route="./tools/pitch save-restore",
        next_steps=(
            "./tools/pitch preflight",
            "./tools/pitch save-restore-probe",
            "./tools/pitch save-restore-review 5",
        ),
    ),
    "certi-ddm": VendorGapProfile(
        profile="certi-ddm",
        vendor="certi",
        area="ddm",
        classification="known-gap",
        status="not-promoted",
        summary="CERTI real-runtime DDM is not yet promoted as an executable matrix slice in this workspace.",
        docs_ref="packages/hla-backend-certi/docs/certi_runtime_limitations.md",
        recommended_operator_route="./tools/certi-easy ddm",
        next_steps=(
            "./tools/certi-easy preflight",
            "./tools/certi-easy ddm-probe",
            "./tools/certi-easy ddm-review 5",
        ),
    ),
    "pitch-ddm": VendorGapProfile(
        profile="pitch-ddm",
        vendor="pitch",
        area="ddm",
        classification="known-gap",
        status="not-promoted",
        summary="Pitch real-runtime DDM is not yet promoted as an executable matrix slice in this workspace.",
        docs_ref="packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        recommended_operator_route="./tools/pitch ddm",
        next_steps=(
            "./tools/pitch preflight",
            "./tools/pitch ddm-probe",
            "./tools/pitch ddm-review 5",
        ),
    ),
    "pitch-negotiated": VendorGapProfile(
        profile="pitch-negotiated",
        vendor="pitch",
        area="negotiated_ownership",
        classification="known-gap",
        status="bridge-divergent",
        summary="Pitch real-runtime negotiated ownership is not yet promoted as an executable parity slice in this workspace because the current JPype and Py4J bridge paths diverge.",
        docs_ref="packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        recommended_operator_route="./tools/pitch negotiated",
        next_steps=(
            "./tools/pitch preflight",
            "./tools/pitch negotiated-probe",
            "./tools/pitch negotiated-review 5",
        ),
    ),
    "pitch-lost-federate": VendorGapProfile(
        profile="pitch-lost-federate",
        vendor="pitch",
        area="lost_federate",
        classification="known-gap",
        status="backend-split",
        summary="Pitch real-runtime lost-federate parity remains blocked: both bridge routes now have executable probe paths, but the current fault injectors still fail to produce observer-visible lost-federate evidence, and JPype shows session auto-resume instead of stable loss.",
        docs_ref="packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
        recommended_operator_route="./tools/pitch lost-federate",
        next_steps=(
            "./tools/pitch preflight",
            "./tools/pitch lost-federate-probe",
            "./tools/pitch lost-federate-review 5",
        ),
        operator_state="environment-blocked",
        blocker_summary="The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable and the required CRC/FedPro loopback ports are not permitted.",
        operator_artifact_refs=(
            "artifacts/preflight_artifacts/pitch-preflight.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
        ),
    ),
}


def get_vendor_gap_profile(profile: str) -> VendorGapProfile:
    try:
        return _PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"unknown vendor gap profile: {profile}") from exc


def write_vendor_gap_profile(output_dir: Path | str, profile: str) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = get_vendor_gap_profile(profile)
    target = output_path / f"{profile}.json"
    target.write_text(
        json.dumps(
            {
                "profile": payload.profile,
                "vendor": payload.vendor,
                "area": payload.area,
                "classification": payload.classification,
                "status": payload.status,
                "summary": payload.summary,
                "docs_ref": payload.docs_ref,
                "recommended_operator_route": payload.recommended_operator_route,
                "next_steps": list(payload.next_steps),
                "operator_state": payload.operator_state,
                "blocker_summary": payload.blocker_summary,
                "operator_artifact_refs": list(payload.operator_artifact_refs),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


__all__ = ["VendorGapProfile", "get_vendor_gap_profile", "write_vendor_gap_profile"]
