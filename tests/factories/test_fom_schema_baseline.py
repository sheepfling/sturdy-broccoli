from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.fom_schema_baseline import build_fom_schema_baseline, write_fom_schema_baseline


def test_build_fom_schema_baseline_validates_positive_2025_xml_pairs() -> None:
    report = build_fom_schema_baseline()

    assert report.passed is True
    assert len(report.case_results) == 2
    assert {result.id for result in report.case_results} == {
        "encoding-smoke-2025",
        "omt-schema-valid-probe-2025",
    }
    assert all(result.passed for result in report.case_results)
    assert all(result.issue_count == 0 for result in report.case_results)


def test_write_fom_schema_baseline_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path, md_path, report = write_fom_schema_baseline(output_root=tmp_path / "schema-baseline")

    assert json_path.exists()
    assert md_path.exists()
    assert report.passed is True
    assert "# FOM Schema Validation Baseline" in md_path.read_text(encoding="utf-8")
