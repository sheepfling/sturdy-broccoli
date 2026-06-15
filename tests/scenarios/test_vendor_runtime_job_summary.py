from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hla2010_repo_internal.verification.vendor_runtime_job_summary import (
    VendorRuntimeJobSummaryPaths,
    build_vendor_runtime_job_summary,
)


ROOT = Path(__file__).resolve().parents[2]


def _sample_pitch_marker(base: Path) -> str:
    return str(base / "pitch" / "lib" / "prtifull.jar")


def _sample_certi_marker(base: Path) -> str:
    return str(base / "certi" / "bin" / "rtig")


def _write_status(path: Path, *, lane: str, overall_classification: str, vendors: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "lane": lane,
                "overall_classification": overall_classification,
                "vendors": vendors,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_build_vendor_runtime_job_summary_renders_blocked_reason_and_next_steps(tmp_path: Path) -> None:
    status_dir = tmp_path / "runtime-status"
    parity_dir = tmp_path / "parity"
    pitch_marker = _sample_pitch_marker(tmp_path)
    _write_status(
        status_dir / "vendor_green_pitch" / "vendor_runtime_status_summary.json",
        lane="vendor-green",
        overall_classification="environment-blocked",
        vendors=[
            {
                "vendor": "pitch",
                "classification": "environment-blocked",
                "environment": "docker-blocked",
                "blocked_reason": "docker",
                "next_steps": ["./tools/pitch preflight", "./tools/pitch install"],
                "blocked_checks": [{"name": "docker", "detail": "blocked: Docker CLI exists but the daemon is not reachable"}],
                "required_markers": {
                    "runtime_home": pitch_marker,
                },
                "required_ports": {
                    "crc": {"host": "127.0.0.1", "port": 8989, "status": "blocked"},
                    "fedpro": {"host": "127.0.0.1", "port": 15164, "status": "blocked"},
                },
            }
        ],
    )
    parity_dir.mkdir(parents=True, exist_ok=True)
    (parity_dir / "vendor_parity_artifacts_summary.json").write_text(
        json.dumps(
            {
                "artifact_count": 12,
                "missing_required_count": 0,
                "probe_promotion_review": {
                    "candidate_count": 1,
                    "path": "analysis/vendor_probe_promotion_review/vendor_probe_promotion_review_summary.json",
                    "profiles": [
                        {
                            "profile": "pitch-negotiated-probe",
                            "next_action": "resolve the documented bridge-divergent state before promotion; keep the lane at probe status",
                            "promotion_readiness": "candidate",
                            "review_decision": "candidate-review",
                            "docs_ref": "packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md",
                        }
                    ],
                },
                "probe_stability": {
                    "pitch-negotiated-probe": {
                        "profile": "pitch-negotiated-probe",
                        "evidence_tier": "probe",
                        "success_count": 5,
                        "attempt_count": 5,
                        "stable": True,
                        "promotion_readiness": "candidate",
                        "path": "analysis/vendor_probe_stability/pitch-negotiated-probe/vendor_probe_stability_summary.json",
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    rendered = build_vendor_runtime_job_summary(
        VendorRuntimeJobSummaryPaths(status_dir=status_dir, parity_dir=parity_dir)
    )

    assert "vendor_green_pitch" in rendered
    assert "- evidence tier: `promoted`" in rendered
    assert "`environment-blocked`" in rendered
    assert "docker-blocked" in rendered
    assert "`./tools/pitch preflight`" in rendered
    assert "blocked: Docker CLI exists but the daemon is not reachable" in rendered
    assert "Required markers for `pitch`:" in rendered
    assert f"`runtime_home`: `{pitch_marker}`" in rendered
    assert "Required ports for `pitch`:" in rendered
    assert "`crc`: `127.0.0.1:8989` [blocked]" in rendered
    assert "## Parity Packet" in rendered
    assert "## Probe Stability" in rendered
    assert "## Promotion Review" in rendered
    assert "pitch-negotiated-probe" in rendered
    assert "5 / 5" in rendered
    assert "probe / candidate" in rendered
    assert "candidate-review" in rendered
    assert "next: resolve the documented bridge-divergent state before promotion; keep the lane at probe status" in rendered
    assert "analysis/vendor_probe_promotion_review/vendor_probe_promotion_review_summary.json" in rendered
    assert "analysis/vendor_probe_stability/pitch-negotiated-probe/vendor_probe_stability_summary.json" in rendered


def test_job_summary_script_bootstraps_source_checkout_and_writes_output_file(tmp_path: Path) -> None:
    status_dir = tmp_path / "runtime-status"
    certi_marker = _sample_certi_marker(tmp_path)
    _write_status(
        status_dir / "repo_green" / "vendor_runtime_status_summary.json",
        lane="repo-green",
        overall_classification="repo-green",
        vendors=[
            {
                "vendor": "certi",
                "classification": "ready",
                "environment": "loopback-ok",
                "blocked_reason": None,
                "next_steps": [],
                "blocked_checks": [],
                "required_markers": {
                    "active_prefix": certi_marker,
                },
                "required_ports": {},
            }
        ],
    )
    output_path = tmp_path / "summary.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/ci/write_vendor_runtime_job_summary.py",
            "--status-dir",
            str(status_dir),
            "--parity-dir",
            str(tmp_path / "missing-parity"),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )

    assert result.returncode == 0
    text = output_path.read_text(encoding="utf-8")
    assert "# Vendor Runtime Status" in text
    assert "repo_green" in text
    assert "- evidence tier: `aggregate`" in text
    assert "loopback-ok" in text
    assert "Required markers for `certi`:" in text


def test_build_vendor_runtime_job_summary_marks_probe_and_known_gap_profiles(tmp_path: Path) -> None:
    status_dir = tmp_path / "runtime-status"
    _write_status(
        status_dir / "vendor_green_pitch_negotiated_probe" / "vendor_runtime_status_summary.json",
        lane="vendor-green",
        overall_classification="vendor-green",
        vendors=[
            {
                "vendor": "pitch",
                "classification": "ready",
                "environment": "docker-ok",
                "blocked_reason": None,
                "next_steps": [],
                "blocked_checks": [],
                "required_markers": {},
                "required_ports": {},
            }
        ],
    )
    _write_status(
        status_dir / "vendor_green_pitch_negotiated" / "vendor_runtime_status_summary.json",
        lane="vendor-green",
        overall_classification="environment-blocked",
        vendors=[
            {
                "vendor": "pitch",
                "classification": "environment-blocked",
                "environment": "docker-blocked",
                "blocked_reason": "docker",
                "next_steps": ["./tools/pitch negotiated"],
                "blocked_checks": [],
                "required_markers": {},
                "required_ports": {},
            }
        ],
    )

    rendered = build_vendor_runtime_job_summary(
        VendorRuntimeJobSummaryPaths(status_dir=status_dir, parity_dir=None)
    )

    assert "vendor_green_pitch_negotiated_probe" in rendered
    assert "vendor_green_pitch_negotiated" in rendered
    assert "- evidence tier: `probe`" in rendered
    assert "narrow executable probe evidence" in rendered
    assert "- evidence tier: `known-gap`" in rendered
    assert "explicit known-gap route" in rendered
