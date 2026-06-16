from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.verification.vendor_probe_promotion_review import write_vendor_probe_promotion_review

ROOT = Path(__file__).resolve().parents[2]


def _write_stability(
    path: Path,
    *,
    profile: str,
    promotion_readiness: str,
    stable: bool,
    attempt_count: int,
    success_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "profile": profile,
                "promotion_readiness": promotion_readiness,
                "stable": stable,
                "attempt_count": attempt_count,
                "success_count": success_count,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_vendor_probe_promotion_review_reports_candidates(tmp_path: Path) -> None:
    root = Path("analysis/vendor_probe_stability")
    certi_save_restore = root / "certi-save-restore-probe" / "vendor_probe_stability_summary.json"
    pitch_neg = root / "pitch-negotiated-probe" / "vendor_probe_stability_summary.json"
    pitch_save_restore = root / "pitch-save-restore-probe" / "vendor_probe_stability_summary.json"
    pitch_ddm = root / "pitch-ddm-probe" / "vendor_probe_stability_summary.json"
    certi_ddm = root / "certi-ddm-probe" / "vendor_probe_stability_summary.json"
    originals = {
        certi_save_restore: certi_save_restore.read_text(encoding="utf-8") if certi_save_restore.exists() else None,
        pitch_neg: pitch_neg.read_text(encoding="utf-8") if pitch_neg.exists() else None,
        pitch_save_restore: pitch_save_restore.read_text(encoding="utf-8") if pitch_save_restore.exists() else None,
        pitch_ddm: pitch_ddm.read_text(encoding="utf-8") if pitch_ddm.exists() else None,
        certi_ddm: certi_ddm.read_text(encoding="utf-8") if certi_ddm.exists() else None,
    }
    _write_stability(
        certi_save_restore,
        profile="certi-save-restore-probe",
        promotion_readiness="candidate",
        stable=True,
        attempt_count=5,
        success_count=5,
    )
    _write_stability(
        certi_ddm,
        profile="certi-ddm-probe",
        promotion_readiness="candidate",
        stable=True,
        attempt_count=5,
        success_count=5,
    )
    _write_stability(
        pitch_neg,
        profile="pitch-negotiated-probe",
        promotion_readiness="candidate",
        stable=True,
        attempt_count=5,
        success_count=5,
    )
    _write_stability(
        pitch_save_restore,
        profile="pitch-save-restore-probe",
        promotion_readiness="needs-more-runs",
        stable=True,
        attempt_count=3,
        success_count=3,
    )
    _write_stability(
        pitch_ddm,
        profile="pitch-ddm-probe",
        promotion_readiness="needs-more-runs",
        stable=True,
        attempt_count=3,
        success_count=3,
    )
    try:
        paths = write_vendor_probe_promotion_review(tmp_path)
        payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
        assert payload["suite_name"] == "vendor-probe-promotion-review"
        assert payload["candidate_count"] == 2
        rows = {row["profile"]: row for row in payload["profiles"]}
        assert rows["certi-save-restore-probe"]["review_decision"] == "candidate-review"
        assert "docs/backend_conformance_matrix.md" in rows["certi-save-restore-probe"]["next_action"]
        assert rows["certi-ddm-probe"]["review_decision"] == "candidate-review"
        assert "docs/backend_conformance_matrix.md" in rows["certi-ddm-probe"]["next_action"]
        assert rows["pitch-negotiated-probe"]["gap_status"] == "bridge-divergent"
        assert rows["pitch-negotiated-probe"]["review_decision"] == "blocked-by-documented-gap"
        assert "bridge-divergent" in rows["pitch-negotiated-probe"]["next_action"]
        assert rows["pitch-save-restore-probe"]["review_decision"] == "needs-more-runs"
        assert rows["pitch-save-restore-probe"]["next_action"] == "./tools/pitch save-restore-review 5"
        assert rows["pitch-ddm-probe"]["review_decision"] == "needs-more-runs"
        report = paths.report_markdown.read_text(encoding="utf-8")
        assert "Vendor Probe Promotion Review" in report
        assert "candidate-review" in report
        assert "blocked-by-documented-gap" in report
        assert "needs-more-runs" in report
        assert "next: compare certi-ddm-probe against docs/backend_conformance_matrix.md" in report
        assert "next: resolve the documented bridge-divergent state before promotion" in report
    finally:
        for path, original in originals.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(original, encoding="utf-8")


def test_vendor_probe_promotion_review_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ci/write_vendor_probe_promotion_review.py",
            "--output-dir",
            str(tmp_path / "review"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "review" / "vendor_probe_promotion_review_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "vendor-probe-promotion-review"
    assert "profiles" in payload
