from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from hla2010_repo_internal.verification.vendor_parity_artifacts import write_vendor_parity_artifacts
from tests.typed_json_models import (
    VendorGapProfile,
    VendorParityArtifactsFullSummary,
    VendorProbePromotionReviewSummary,
    VendorRuntimeStatusSummary,
)

HOST_ABSOLUTE_PATH_RE = re.compile(r"(/Users/|/private/tmp|/private/var/folders/|/var/folders/)")


def _assert_no_host_paths(text: str) -> None:
    assert not HOST_ABSOLUTE_PATH_RE.search(text), text


def _assert_manifest_contains(rows: list[dict[str, str]], field: str, values: tuple[str, ...]) -> None:
    actual = {row[field] for row in rows}
    for value in values:
        assert value in actual


def _sample_certi_marker(base: Path) -> dict[str, str]:
    return {
        "active_prefix": str(base / "certi" / "bin" / "rtig"),
        "active_build_root": str(base / "certi-build" / "libRTI" / "ieee1516-2010"),
    }


def _sample_pitch_marker(base: Path) -> dict[str, str]:
    return {
        "runtime_home": str(base / "pitch" / "lib" / "prtifull.jar"),
    }


def _write_preflight(path: Path, *, tool: str, environment: str, result: str, exit_code: int) -> None:
    payload = {
        "tool": tool,
        "environment": environment,
        "result": result,
        "exit_code": exit_code,
    }
    if tool == "certi-preflight":
        payload["required_markers"] = _sample_certi_marker(path.parent)
    else:
        payload["required_markers"] = _sample_pitch_marker(path.parent)
        payload["ports"] = {
            "crc": {
                "host": "127.0.0.1",
                "port": 8989,
                "status": "blocked" if exit_code else "ok",
                "detail": result,
            },
            "fedpro": {
                "host": "127.0.0.1",
                "port": 15164,
                "status": "blocked" if exit_code else "ok",
                "detail": result,
            },
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def _write_gap_profile(path: Path, *, profile: str, vendor: str, area: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "profile": profile,
                "vendor": vendor,
                "area": area,
                "classification": "known-gap",
                "status": "not-promoted",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_probe_stability(
    path: Path,
    *,
    profile: str,
    evidence_tier: str,
    repeat_count: int,
    attempt_count: int,
    success_count: int,
    failure_count: int,
    stable: bool,
    promotion_readiness: str,
    promotion_note: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "profile": profile,
                "evidence_tier": evidence_tier,
                "repeat_count": repeat_count,
                "attempt_count": attempt_count,
                "success_count": success_count,
                "failure_count": failure_count,
                "stable": stable,
                "promotion_readiness": promotion_readiness,
                "promotion_note": promotion_note,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_vendor_parity_artifacts_are_generated(tmp_path):
    analysis_root = Path("analysis/preflight_artifacts")
    gap_root = Path("analysis/vendor_gap_profiles")
    certi_path = analysis_root / "certi-preflight.json"
    pitch_path = analysis_root / "pitch-preflight.json"
    certi_gap_path = gap_root / "certi-save-restore.json"
    pitch_gap_path = gap_root / "pitch-ddm.json"
    pitch_negotiated_gap_path = gap_root / "pitch-negotiated.json"
    pitch_lost_federate_gap_path = gap_root / "pitch-lost-federate.json"
    stability_root = Path("analysis/vendor_probe_stability")
    certi_ddm_stability_path = stability_root / "certi-ddm-probe" / "vendor_probe_stability_summary.json"
    pitch_stability_path = stability_root / "pitch-negotiated-probe" / "vendor_probe_stability_summary.json"
    pitch_lost_federate_stability_path = (
        stability_root / "pitch-lost-federate-probe" / "vendor_probe_stability_summary.json"
    )
    promotion_review_path = (
        Path("analysis/vendor_probe_promotion_review") / "vendor_probe_promotion_review_summary.json"
    )
    certi_original = certi_path.read_text(encoding="utf-8") if certi_path.exists() else None
    pitch_original = pitch_path.read_text(encoding="utf-8") if pitch_path.exists() else None
    certi_gap_original = certi_gap_path.read_text(encoding="utf-8") if certi_gap_path.exists() else None
    pitch_gap_original = pitch_gap_path.read_text(encoding="utf-8") if pitch_gap_path.exists() else None
    pitch_negotiated_gap_original = (
        pitch_negotiated_gap_path.read_text(encoding="utf-8") if pitch_negotiated_gap_path.exists() else None
    )
    pitch_lost_federate_gap_original = (
        pitch_lost_federate_gap_path.read_text(encoding="utf-8")
        if pitch_lost_federate_gap_path.exists()
        else None
    )
    certi_ddm_stability_original = (
        certi_ddm_stability_path.read_text(encoding="utf-8") if certi_ddm_stability_path.exists() else None
    )
    pitch_stability_original = pitch_stability_path.read_text(encoding="utf-8") if pitch_stability_path.exists() else None
    pitch_lost_federate_stability_original = (
        pitch_lost_federate_stability_path.read_text(encoding="utf-8")
        if pitch_lost_federate_stability_path.exists()
        else None
    )
    promotion_review_original = promotion_review_path.read_text(encoding="utf-8") if promotion_review_path.exists() else None
    _write_preflight(
        certi_path,
        tool="certi-preflight",
        environment="loopback-blocked",
        result="real CERTI will skip",
        exit_code=1,
    )
    _write_preflight(
        pitch_path,
        tool="pitch-preflight",
        environment="docker-blocked",
        result="Pitch runtime is not ready",
        exit_code=1,
    )
    _write_gap_profile(certi_gap_path, profile="certi-save-restore", vendor="certi", area="save_restore")
    _write_gap_profile(pitch_gap_path, profile="pitch-ddm", vendor="pitch", area="ddm")
    _write_gap_profile(
        pitch_negotiated_gap_path,
        profile="pitch-negotiated",
        vendor="pitch",
        area="negotiated_ownership",
    )
    _write_gap_profile(
        pitch_lost_federate_gap_path,
        profile="pitch-lost-federate",
        vendor="pitch",
        area="lost_federate",
    )
    _write_probe_stability(
        certi_ddm_stability_path,
        profile="certi-ddm-probe",
        evidence_tier="probe",
        repeat_count=5,
        attempt_count=5,
        success_count=5,
        failure_count=0,
        stable=True,
        promotion_readiness="candidate",
        promotion_note="repeated-run stability evidence is present; promotion still requires clause-level parity review",
    )
    _write_probe_stability(
        pitch_stability_path,
        profile="pitch-negotiated-probe",
        evidence_tier="probe",
        repeat_count=5,
        attempt_count=5,
        success_count=5,
        failure_count=0,
        stable=True,
        promotion_readiness="candidate",
        promotion_note="repeated-run stability evidence is present; promotion still requires clause-level parity review",
    )
    _write_probe_stability(
        pitch_lost_federate_stability_path,
        profile="pitch-lost-federate-probe",
        evidence_tier="probe",
        repeat_count=5,
        attempt_count=5,
        success_count=4,
        failure_count=1,
        stable=False,
        promotion_readiness="needs-investigation",
        promotion_note="fault-injection coverage exists, but repeated-run instability still blocks promotion",
    )
    promotion_review_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_review_path.write_text(
        json.dumps(
            {
                "candidate_count": 2,
                "profiles": [
                    {
                        "profile": "certi-ddm-probe",
                        "next_action": "compare certi-ddm-probe against docs/backend_conformance_matrix.md and promote only if clause-level parity is now defensible",
                        "promotion_readiness": "candidate",
                        "review_decision": "candidate-review",
                        "docs_ref": "docs/backend_conformance_matrix.md",
                    },
                    {
                        "profile": "pitch-negotiated-probe",
                        "next_action": "resolve the documented bridge-divergent state before promotion; keep the lane at probe status",
                        "promotion_readiness": "candidate",
                        "review_decision": "candidate-review",
                        "docs_ref": "packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        paths = write_vendor_parity_artifacts(tmp_path)

        summary = VendorParityArtifactsFullSummary.from_mapping(json.loads(paths.summary_json.read_text()))
        assert summary.suite_name == "vendor-parity-artifacts"
        assert summary.artifact_count is not None and summary.artifact_count >= 10
        assert summary.missing_required_count == 0
        assert any(profile.vendor_family == "certi" for profile in summary.profiles)
        assert any(profile.vendor_family == "pitch" for profile in summary.profiles)
        assert any(profile.evidence_tier == "promoted" for profile in summary.profiles)
        assert any(profile.evidence_tier == "known-gap" for profile in summary.profiles)
        assert any(command.command == "./tools/certi-easy smoke compare" for command in summary.profile_commands)
        assert any(command.command == "./tools/pitch negotiated-probe" and command.evidence_tier == "probe" for command in summary.profile_commands)
        assert any(command.command == "./tools/pitch negotiated" and command.evidence_tier == "known-gap" for command in summary.profile_commands)
        assert any(command.command == "./tools/pitch lost-federate-probe" and command.evidence_tier == "probe" for command in summary.profile_commands)
        assert any(command.command == "./tools/pitch lost-federate" and command.evidence_tier == "known-gap" for command in summary.profile_commands)
        assert any(command.command == "./tools/vendor-state classify --lane repo-green --json" for command in summary.profile_commands)
        assert "certi" in summary.preflight
        assert "pitch" in summary.preflight
        repo_green = VendorRuntimeStatusSummary.from_mapping(summary.runtime_status["repo_green"])
        vendor_green_certi = VendorRuntimeStatusSummary.from_mapping(summary.runtime_status["vendor_green"]["certi"])
        vendor_green_pitch = VendorRuntimeStatusSummary.from_mapping(summary.runtime_status["vendor_green"]["pitch"])
        assert repo_green.overall_classification == "repo-green"
        assert vendor_green_certi.overall_classification == "environment-blocked"
        assert vendor_green_pitch.overall_classification == "environment-blocked"
        certi_gap = summary.gap_profiles["certi-save-restore"]
        assert certi_gap is not None
        assert certi_gap.classification == "known-gap"
        assert certi_gap.next_steps == (
            "./tools/certi-easy preflight",
            "./tools/certi-easy save-restore-probe",
            "./tools/certi-easy save-restore-review 5",
        )
        pitch_ddm_gap = summary.gap_profiles["pitch-ddm"]
        assert pitch_ddm_gap is not None
        assert pitch_ddm_gap.area == "ddm"
        assert pitch_ddm_gap.next_steps == (
            "./tools/pitch preflight",
            "./tools/pitch ddm-probe",
            "./tools/pitch ddm-review 5",
        )
        pitch_negotiated_gap = summary.gap_profiles["pitch-negotiated"]
        assert pitch_negotiated_gap is not None
        assert pitch_negotiated_gap.area == "negotiated_ownership"
        assert pitch_negotiated_gap.next_steps == (
            "./tools/pitch preflight",
            "./tools/pitch negotiated-probe",
            "./tools/pitch negotiated-review 5",
        )
        lost_federate_gap = summary.gap_profiles["pitch-lost-federate"]
        assert lost_federate_gap is not None
        assert lost_federate_gap.area == "lost_federate"
        assert lost_federate_gap.operator_state == "environment-blocked"
        assert "Docker is unreachable" in lost_federate_gap.blocker_summary
        assert lost_federate_gap.operator_artifact_refs == (
            "analysis/preflight_artifacts/pitch-preflight.json",
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
        )
        assert lost_federate_gap.next_steps == (
            "./tools/pitch preflight",
            "./tools/pitch lost-federate-probe",
            "./tools/pitch lost-federate-review 5",
        )
        assert summary.gap_profiles["pitch-save-restore"] is None
        pitch_neg_stability = summary.probe_stability["pitch-negotiated-probe"]
        assert pitch_neg_stability is not None
        assert pitch_neg_stability.stable is True
        assert pitch_neg_stability.promotion_readiness == "candidate"
        assert pitch_neg_stability.attempt_count == 5
        pitch_lost_stability = summary.probe_stability["pitch-lost-federate-probe"]
        assert pitch_lost_stability is not None
        assert pitch_lost_stability.stable is False
        assert pitch_lost_stability.promotion_readiness == "needs-investigation"
        assert pitch_lost_stability.failure_count == 1
        certi_ddm_stability = summary.probe_stability["certi-ddm-probe"]
        assert certi_ddm_stability is not None
        assert certi_ddm_stability.promotion_readiness == "candidate"
        assert certi_ddm_stability.attempt_count == 5
        assert summary.probe_promotion_review is not None
        assert summary.probe_promotion_review.candidate_count == 2

        with paths.artifact_manifest_csv.open() as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        _assert_manifest_contains(
            rows,
            "path",
            (
                "tests/vendors/test_pitch_real_backend_matrix.py",
                "packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md",
                "tools/vendor-state",
                "analysis/vendor_probe_stability/certi-ddm-probe/vendor_probe_stability_summary.json",
                "analysis/vendor_probe_stability/pitch-negotiated-probe/vendor_probe_stability_summary.json",
                "analysis/vendor_probe_stability/pitch-lost-federate-probe/vendor_probe_stability_summary.json",
                "analysis/vendor_gap_profiles/certi-save-restore.json",
                "analysis/vendor_gap_profiles/pitch-lost-federate.json",
            ),
        )
        _assert_manifest_contains(
            rows,
            "artifact_kind",
            ("preflight", "gap-profile", "stability-summary", "promotion-review"),
        )
        _assert_manifest_contains(rows, "evidence_tier", ("promoted", "known-gap"))

        report_text = paths.report_markdown.read_text()
        for fragment in (
            "Vendor Parity Artifacts",
            "## Profiles",
            "## Commands",
            "## Runtime Status",
            "## Known Gaps",
            "## Probe Stability",
            "## Promotion Review",
            "| Vendor | Profile | Tier | Indexed | Existing | Missing required | Kinds |",
            "./tools/certi-easy smoke compare",
            "./tools/pitch negotiated-probe` [probe]",
            "./tools/pitch negotiated` [known-gap]",
            "./tools/pitch negotiated-review 5",
            "./tools/pitch lost-federate-probe` [probe]",
            "./tools/pitch lost-federate` [known-gap]",
            "./tools/pitch lost-federate-review 5",
            "operator-state: `environment-blocked`",
            "blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable",
            "artifact: `analysis/preflight_artifacts/pitch-preflight.json`",
            "next: `./tools/pitch ddm-review 5`",
            "next: `./tools/pitch lost-federate-review 5`",
            "./tools/vendor-probe-review promotion-review",
            "pitch-negotiated-probe`: stable `True`",
            "pitch-lost-federate-probe`: stable `False`",
            "promotion `needs-investigation`",
            "promotion `candidate`",
            "decision `candidate-review`",
            "next: compare certi-ddm-probe against docs/backend_conformance_matrix.md and promote only if clause-level parity is now defensible",
            "next: resolve the documented bridge-divergent state before promotion; keep the lane at probe status",
            "repo-green",
            "./tools/pitch ddm",
            "Required markers for `certi` in `repo-green`:",
            "`active_build_root`: `analysis/preflight_artifacts/certi-build/libRTI/ieee1516-2010`",
            "Required markers for `pitch` in `pitch vendor-green`:",
            "`runtime_home`: `analysis/preflight_artifacts/pitch/lib/prtifull.jar`",
            "Required ports for `pitch` in `pitch vendor-green`:",
            "`crc`: `127.0.0.1:8989` [blocked]",
        ):
            assert fragment in report_text
        _assert_no_host_paths(paths.summary_json.read_text(encoding="utf-8"))
        _assert_no_host_paths(report_text)
    finally:
        if certi_original is None:
            certi_path.unlink(missing_ok=True)
        else:
            certi_path.write_text(certi_original, encoding="utf-8")
        if pitch_original is None:
            pitch_path.unlink(missing_ok=True)
        else:
            pitch_path.write_text(pitch_original, encoding="utf-8")
        if certi_gap_original is None:
            certi_gap_path.unlink(missing_ok=True)
        else:
            certi_gap_path.write_text(certi_gap_original, encoding="utf-8")
        if pitch_gap_original is None:
            pitch_gap_path.unlink(missing_ok=True)
        else:
            pitch_gap_path.write_text(pitch_gap_original, encoding="utf-8")
        if pitch_negotiated_gap_original is None:
            pitch_negotiated_gap_path.unlink(missing_ok=True)
        else:
            pitch_negotiated_gap_path.write_text(pitch_negotiated_gap_original, encoding="utf-8")
        if pitch_lost_federate_gap_original is None:
            pitch_lost_federate_gap_path.unlink(missing_ok=True)
        else:
            pitch_lost_federate_gap_path.write_text(pitch_lost_federate_gap_original, encoding="utf-8")
        if certi_ddm_stability_original is None:
            certi_ddm_stability_path.unlink(missing_ok=True)
        else:
            certi_ddm_stability_path.write_text(certi_ddm_stability_original, encoding="utf-8")
        if pitch_stability_original is None:
            pitch_stability_path.unlink(missing_ok=True)
        else:
            pitch_stability_path.write_text(pitch_stability_original, encoding="utf-8")
        if pitch_lost_federate_stability_original is None:
            pitch_lost_federate_stability_path.unlink(missing_ok=True)
        else:
            pitch_lost_federate_stability_path.write_text(
                pitch_lost_federate_stability_original,
                encoding="utf-8",
            )
        if promotion_review_original is None:
            promotion_review_path.unlink(missing_ok=True)
        else:
            promotion_review_path.write_text(promotion_review_original, encoding="utf-8")


def test_live_vendor_parity_summary_surfaces_pitch_lost_federate_gap_profile() -> None:
    payload = VendorParityArtifactsFullSummary.from_mapping(json.loads(
        (
            Path("analysis/vendor_parity_artifacts") / "vendor_parity_artifacts_summary.json"
        ).read_text(encoding="utf-8")
    ))

    gap_profile = payload.gap_profiles["pitch-lost-federate"]
    assert gap_profile is not None
    assert gap_profile.profile == "pitch-lost-federate"
    assert gap_profile.status == "backend-split"
    assert gap_profile.operator_state == "environment-blocked"
    assert "Docker is unreachable" in gap_profile.blocker_summary
    assert gap_profile.operator_artifact_refs == (
        "analysis/preflight_artifacts/pitch-preflight.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    )


def test_live_vendor_parity_report_surfaces_pitch_lost_federate_operator_blockers() -> None:
    report_text = (
        Path("analysis/vendor_parity_artifacts") / "vendor_parity_artifacts_report.md"
    ).read_text(encoding="utf-8")

    assert "pitch-lost-federate`: classification `known-gap`, status `backend-split`" in report_text
    assert "operator-state: `environment-blocked`" in report_text
    assert "blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable" in report_text
    assert "artifact: `analysis/preflight_artifacts/pitch-preflight.json`" in report_text
    assert (
        "artifact: `analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json`"
        in report_text
    )
    assert (
        "artifact: `analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md`"
        in report_text
    )
    assert "pitch-lost-federate-probe`: no stability artifact is currently present" in report_text
