from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

from hla.verification.repo_internal.verification.vendor_parity_artifacts import write_vendor_parity_artifacts

TMP_ROOT = Path(tempfile.gettempdir())
CERTI_PREFIX = TMP_ROOT / "certi" / "bin" / "rtig"
CERTI_BUILD_ROOT = TMP_ROOT / "certi-build" / "libRTI" / "ieee1516-2010"
PITCH_RUNTIME_HOME = TMP_ROOT / "pitch" / "lib" / "prtifull.jar"


def _write_preflight(path: Path, *, tool: str, environment: str, result: str, exit_code: int) -> None:
    payload = {
        "tool": tool,
        "environment": environment,
        "result": result,
        "exit_code": exit_code,
    }
    if tool == "certi-preflight":
        payload["required_markers"] = {
            "active_prefix": str(CERTI_PREFIX),
            "active_build_root": str(CERTI_BUILD_ROOT),
        }
    else:
        payload["required_markers"] = {
            "runtime_home": str(PITCH_RUNTIME_HOME),
        }
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
    analysis_root = Path("artifacts/preflight_artifacts")
    gap_root = Path("artifacts/vendor_gap_profiles")
    certi_path = analysis_root / "certi-preflight.json"
    pitch_path = analysis_root / "pitch-preflight.json"
    certi_gap_path = gap_root / "certi-save-restore.json"
    pitch_save_restore_gap_path = gap_root / "pitch-save-restore.json"
    pitch_gap_path = gap_root / "pitch-ddm.json"
    pitch_negotiated_gap_path = gap_root / "pitch-negotiated.json"
    pitch_lost_federate_gap_path = gap_root / "pitch-lost-federate.json"
    stability_root = Path("artifacts/vendor_probe_stability")
    certi_ddm_stability_path = stability_root / "certi-ddm-probe" / "vendor_probe_stability_summary.json"
    pitch_stability_path = stability_root / "pitch-negotiated-probe" / "vendor_probe_stability_summary.json"
    pitch_time_window_stability_path = stability_root / "pitch-time-window-probe" / "vendor_probe_stability_summary.json"
    pitch_time_window_restore_stability_path = (
        stability_root / "pitch-time-window-restore-state-probe" / "vendor_probe_stability_summary.json"
    )
    pitch_lost_federate_stability_path = (
        stability_root / "pitch-lost-federate-probe" / "vendor_probe_stability_summary.json"
    )
    promotion_review_path = (
        Path("artifacts/vendor_probe_promotion_review") / "vendor_probe_promotion_review_summary.json"
    )
    certi_original = certi_path.read_text(encoding="utf-8") if certi_path.exists() else None
    pitch_original = pitch_path.read_text(encoding="utf-8") if pitch_path.exists() else None
    certi_gap_original = certi_gap_path.read_text(encoding="utf-8") if certi_gap_path.exists() else None
    pitch_save_restore_gap_original = (
        pitch_save_restore_gap_path.read_text(encoding="utf-8") if pitch_save_restore_gap_path.exists() else None
    )
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
    pitch_time_window_stability_original = (
        pitch_time_window_stability_path.read_text(encoding="utf-8")
        if pitch_time_window_stability_path.exists()
        else None
    )
    pitch_time_window_restore_stability_original = (
        pitch_time_window_restore_stability_path.read_text(encoding="utf-8")
        if pitch_time_window_restore_stability_path.exists()
        else None
    )
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
    _write_gap_profile(
        pitch_save_restore_gap_path,
        profile="pitch-save-restore",
        vendor="pitch",
        area="save_restore",
    )
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
        pitch_time_window_stability_path,
        profile="pitch-time-window-probe",
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
        pitch_time_window_restore_stability_path,
        profile="pitch-time-window-restore-state-probe",
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
                "candidate_count": 4,
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
                        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
                    },
                    {
                        "profile": "pitch-time-window-probe",
                        "next_action": "compare pitch-time-window-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible",
                        "promotion_readiness": "candidate",
                        "review_decision": "candidate-review",
                        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
                    },
                    {
                        "profile": "pitch-time-window-restore-state-probe",
                        "next_action": "compare pitch-time-window-restore-state-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible",
                        "promotion_readiness": "candidate",
                        "review_decision": "candidate-review",
                        "docs_ref": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
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

        summary = json.loads(paths.summary_json.read_text())
        assert summary["suite_name"] == "vendor-parity-artifacts"
        assert summary["artifact_count"] >= 10
        assert summary["missing_required_count"] == 0
        assert any(profile["vendor_family"] == "certi" for profile in summary["profiles"])
        assert any(profile["vendor_family"] == "pitch" for profile in summary["profiles"])
        assert any(profile["evidence_tier"] == "promoted" for profile in summary["profiles"])
        assert any(profile["evidence_tier"] == "known-gap" for profile in summary["profiles"])
        assert any(command["command"] == "./tools/certi-easy smoke compare" for command in summary["profile_commands"])
        assert any(command["command"] == "./tools/pitch negotiated-probe" and command["evidence_tier"] == "probe" for command in summary["profile_commands"])
        assert any(command["command"] == "./tools/pitch negotiated" and command["evidence_tier"] == "known-gap" for command in summary["profile_commands"])
        assert any(command["command"] == "./tools/pitch lost-federate-probe" and command["evidence_tier"] == "probe" for command in summary["profile_commands"])
        assert any(command["command"] == "./tools/pitch lost-federate" and command["evidence_tier"] == "known-gap" for command in summary["profile_commands"])
        assert any(command["command"] == "./tools/vendor-state classify --lane repo-green --json" for command in summary["profile_commands"])
        assert "certi" in summary["preflight"]
        assert "pitch" in summary["preflight"]
        assert summary["runtime_status"]["repo_green"]["overall_classification"] == "repo-green"
        assert summary["runtime_status"]["vendor_green"]["certi"]["overall_classification"] == "environment-blocked"
        assert summary["runtime_status"]["vendor_green"]["pitch"]["overall_classification"] == "environment-blocked"
        assert summary["gap_profiles"]["certi-save-restore"]["classification"] == "known-gap"
        assert summary["gap_profiles"]["certi-save-restore"]["next_steps"] == [
            "./tools/certi-easy preflight",
            "./tools/certi-easy save-restore-probe",
            "./tools/certi-easy save-restore-review 5",
        ]
        assert summary["gap_profiles"]["pitch-ddm"]["area"] == "ddm"
        assert summary["gap_profiles"]["pitch-ddm"]["next_steps"] == [
            "./tools/pitch preflight",
            "./tools/pitch ddm-probe",
            "./tools/pitch ddm-review 5",
        ]
        assert summary["gap_profiles"]["pitch-negotiated"]["area"] == "negotiated_ownership"
        assert summary["gap_profiles"]["pitch-negotiated"]["next_steps"] == [
            "./tools/pitch preflight",
            "./tools/pitch negotiated-probe",
            "./tools/pitch negotiated-review 5",
        ]
        assert summary["gap_profiles"]["pitch-lost-federate"]["area"] == "lost_federate"
        assert summary["gap_profiles"]["pitch-lost-federate"]["operator_state"] == "environment-blocked"
        assert "Docker is unreachable" in summary["gap_profiles"]["pitch-lost-federate"]["blocker_summary"]
        assert summary["gap_profiles"]["pitch-lost-federate"]["operator_artifact_refs"] == [
            "artifacts/preflight_artifacts/pitch-preflight.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
        ]
        assert summary["gap_profiles"]["pitch-lost-federate"]["next_steps"] == [
            "./tools/pitch preflight",
            "./tools/pitch lost-federate-probe",
            "./tools/pitch lost-federate-review 5",
        ]
        assert summary["gap_profiles"]["pitch-save-restore"]["classification"] == "known-gap"
        assert summary["probe_stability"]["pitch-negotiated-probe"]["stable"] is True
        assert summary["probe_stability"]["pitch-negotiated-probe"]["promotion_readiness"] == "candidate"
        assert summary["probe_stability"]["pitch-negotiated-probe"]["attempt_count"] == 5
        assert summary["probe_stability"]["pitch-lost-federate-probe"]["stable"] is False
        assert summary["probe_stability"]["pitch-lost-federate-probe"]["promotion_readiness"] == "needs-investigation"
        assert summary["probe_stability"]["pitch-lost-federate-probe"]["failure_count"] == 1
        assert summary["probe_stability"]["certi-ddm-probe"]["promotion_readiness"] == "candidate"
        assert summary["probe_stability"]["certi-ddm-probe"]["attempt_count"] == 5
        assert summary["probe_promotion_review"]["candidate_count"] == 4

        with paths.artifact_manifest_csv.open() as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        assert any(row["path"] == "tests/vendors/test_pitch_real_backend_matrix.py" for row in rows)
        assert any(
            row["path"] == "packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md"
            for row in rows
        )
        assert any(row["artifact_kind"] == "preflight" for row in rows)
        assert any(row["path"] == "tools/vendor-state" for row in rows)
        assert any(row["artifact_kind"] == "gap-profile" for row in rows)
        assert any(row["artifact_kind"] == "stability-summary" for row in rows)
        assert any(row["artifact_kind"] == "promotion-review" for row in rows)
        assert any(row["evidence_tier"] == "promoted" for row in rows)
        assert any(row["evidence_tier"] == "known-gap" for row in rows)
        assert any(row["path"] == "artifacts/vendor_probe_stability/certi-ddm-probe/vendor_probe_stability_summary.json" for row in rows)
        assert any(row["path"] == "artifacts/vendor_probe_stability/pitch-negotiated-probe/vendor_probe_stability_summary.json" for row in rows)
        assert any(row["path"] == "artifacts/vendor_probe_stability/pitch-time-window-probe/vendor_probe_stability_summary.json" for row in rows)
        assert any(
            row["path"]
            == "artifacts/vendor_probe_stability/pitch-time-window-restore-state-probe/vendor_probe_stability_summary.json"
            for row in rows
        )
        assert any(row["path"] == "artifacts/vendor_probe_stability/pitch-lost-federate-probe/vendor_probe_stability_summary.json" for row in rows)
        assert any(row["path"] == "artifacts/vendor_gap_profiles/certi-save-restore.json" for row in rows)
        assert any(row["path"] == "artifacts/vendor_gap_profiles/pitch-lost-federate.json" for row in rows)

        report_text = paths.report_markdown.read_text()
        assert "Vendor Parity Artifacts" in report_text
        assert "## Profiles" in report_text
        assert "## Commands" in report_text
        assert "## Runtime Status" in report_text
        assert "## Known Gaps" in report_text
        assert "## Probe Stability" in report_text
        assert "## Promotion Review" in report_text
        assert "| Vendor | Profile | Tier | Indexed | Existing | Missing required | Kinds |" in report_text
        assert "./tools/certi-easy smoke compare" in report_text
        assert "./tools/pitch negotiated-probe` [probe]" in report_text
        assert "./tools/pitch negotiated` [known-gap]" in report_text
        assert "./tools/pitch negotiated-review 5" in report_text
        assert "./tools/pitch time-window-probe` [probe]" in report_text
        assert "./tools/pitch time-window-restore-state-probe` [probe]" in report_text
        assert "./tools/pitch lost-federate-probe` [probe]" in report_text
        assert "./tools/pitch lost-federate` [known-gap]" in report_text
        assert "./tools/pitch lost-federate-review 5" in report_text
        assert "operator-state: `environment-blocked`" in report_text
        assert "blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable" in report_text
        assert "artifact: `artifacts/preflight_artifacts/pitch-preflight.json`" in report_text
        assert "next: `./tools/pitch ddm-review 5`" in report_text
        assert "next: `./tools/pitch lost-federate-review 5`" in report_text
        assert "./tools/vendor-probe-review promotion-review" in report_text
        assert "pitch-negotiated-probe`: stable `True`" in report_text
        assert "pitch-lost-federate-probe`: stable `False`" in report_text
        assert "promotion `needs-investigation`" in report_text
        assert "promotion `candidate`" in report_text
        assert "decision `candidate-review`" in report_text
        assert "next: compare certi-ddm-probe against docs/backend_conformance_matrix.md and promote only if clause-level parity is now defensible" in report_text
        assert "next: compare pitch-time-window-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible" in report_text
        assert "next: compare pitch-time-window-restore-state-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible" in report_text
        assert "next: resolve the documented bridge-divergent state before promotion; keep the lane at probe status" in report_text
        assert "candidate count: `4`" in report_text
        assert "repo-green" in report_text
        assert "./tools/pitch ddm" in report_text
        assert "Required markers for `certi` in `repo-green`:" in report_text
        assert f"`active_build_root`: `{CERTI_BUILD_ROOT}`" in report_text
        assert "Required markers for `pitch` in `pitch vendor-green`:" in report_text
        assert f"`runtime_home`: `{PITCH_RUNTIME_HOME}`" in report_text
        assert "Required ports for `pitch` in `pitch vendor-green`:" in report_text
        assert "`crc`: `127.0.0.1:8989` [blocked]" in report_text
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
        if pitch_save_restore_gap_original is None:
            pitch_save_restore_gap_path.unlink(missing_ok=True)
        else:
            pitch_save_restore_gap_path.write_text(pitch_save_restore_gap_original, encoding="utf-8")
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
    payload = json.loads(
        (
            Path("artifacts/vendor_parity_artifacts") / "vendor_parity_artifacts_summary.json"
        ).read_text(encoding="utf-8")
    )

    gap_profile = payload["gap_profiles"]["pitch-lost-federate"]
    assert gap_profile is not None
    assert gap_profile["profile"] == "pitch-lost-federate"
    assert gap_profile["status"] == "backend-split"
    assert gap_profile["operator_state"] == "environment-blocked"
    assert "Docker is unreachable" in gap_profile["blocker_summary"]
    assert gap_profile["operator_artifact_refs"] == [
        "artifacts/preflight_artifacts/pitch-preflight.json",
        "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
        "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    ]


def test_live_vendor_parity_report_surfaces_pitch_lost_federate_operator_blockers() -> None:
    report_text = (
        Path("artifacts/vendor_parity_artifacts") / "vendor_parity_artifacts_report.md"
    ).read_text(encoding="utf-8")

    assert "pitch-lost-federate`: classification `known-gap`, status `backend-split`" in report_text
    assert "operator-state: `environment-blocked`" in report_text
    assert "blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable" in report_text
    assert "artifact: `artifacts/preflight_artifacts/pitch-preflight.json`" in report_text
    assert (
        "artifact: `artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json`"
        in report_text
    )
    assert (
        "artifact: `artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md`"
        in report_text
    )
    assert "pitch-lost-federate-probe`: no stability artifact is currently present" in report_text
