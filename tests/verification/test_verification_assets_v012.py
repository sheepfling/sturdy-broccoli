from __future__ import annotations

import json

from hla.verification.repo_internal.verification.asset_plan import build_verification_plan, write_verification_assets


def test_verification_plan_is_honest_about_progress_and_gaps(tmp_path):
    plan = build_verification_plan("0.12.0")
    summary = plan.coverage_summary()

    assert summary["asset_count"] >= 10
    assert summary["status_counts"]["implemented-slice"] >= 5
    assert summary["status_counts"]["planned"] >= 1
    assert summary["status_counts"]["gap"] >= 1
    assert "IEEE 1516.1-2010 (2010 edition) §11.4.1" in summary["sections"]
    assert any(asset.gaps for asset in plan.assets)

    output = write_verification_assets(tmp_path / "verification.json", version="0.12.0")
    payload = json.loads(output.read_text())
    assert payload["summary"]["version"] == "0.12.0"
    assert payload["summary"]["gap_asset_ids"]
