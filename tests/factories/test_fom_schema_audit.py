from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.fom_schema_audit import build_fom_schema_audit, write_fom_schema_audit


def test_build_fom_schema_audit_runs_validator_round_trip_and_workbench() -> None:
    report = build_fom_schema_audit()

    assert report.passed is True
    assert len(report.case_results) == 2
    assert {row.id for row in report.case_results} == {
        "encoding-smoke-2025",
        "omt-schema-valid-probe-2025",
    }
    assert all(row.validation_passed for row in report.case_results)
    assert all(row.roundtrip_passed for row in report.case_results)
    assert report.workbench_snapshot_path.endswith("fom_workbench_snapshot.json")
    assert report.workbench_html_path.endswith("fom_workbench.html")
    snapshot_text = Path(report.workbench_snapshot_path).read_text(encoding="utf-8")
    assert "schema-baseline" in snapshot_text


def test_write_fom_schema_audit_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path, md_path, report = write_fom_schema_audit(output_root=tmp_path / "schema-audit")

    assert json_path.exists()
    assert md_path.exists()
    assert report.passed is True
    assert "# FOM Schema Top-to-Bottom Audit" in md_path.read_text(encoding="utf-8")
