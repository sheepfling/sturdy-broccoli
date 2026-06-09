from __future__ import annotations

import csv
import json

from hla2010.testing.vendor_parity_artifacts import write_vendor_parity_artifacts


def test_vendor_parity_artifacts_are_generated(tmp_path):
    paths = write_vendor_parity_artifacts(tmp_path)

    summary = json.loads(paths.summary_json.read_text())
    assert summary["suite_name"] == "vendor-parity-artifacts"
    assert summary["artifact_count"] >= 10
    assert summary["missing_required_count"] == 0
    assert any(profile["vendor_family"] == "certi" for profile in summary["profiles"])
    assert any(profile["vendor_family"] == "pitch" for profile in summary["profiles"])
    assert any(command["command"] == "./scripts/ci/vendor_runtime_smoke.sh certi-compare" for command in summary["profile_commands"])
    assert "certi" in summary["preflight"]
    assert "pitch" in summary["preflight"]

    with paths.artifact_manifest_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert any(row["path"] == "tests/vendors/test_pitch_real_backend_matrix.py" for row in rows)
    assert any(
        row["path"] == "packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md"
        for row in rows
    )
    assert any(row["artifact_kind"] == "preflight" for row in rows)

    report_text = paths.report_markdown.read_text()
    assert "Vendor Parity Artifacts" in report_text
    assert "## Profiles" in report_text
    assert "## Commands" in report_text
    assert "vendor_runtime_smoke.sh certi-compare" in report_text
