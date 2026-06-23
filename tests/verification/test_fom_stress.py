from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.fom_stress import build_fom_stress_report, write_fom_stress_report


def test_fom_stress_report_covers_both_editions() -> None:
    report = build_fom_stress_report()

    assert any(row.year == 2010 for row in report.families)
    assert any(row.year == 2025 for row in report.families)
    assert any(row.scenario_family == "rpr-normative" for row in report.families)
    assert any(row.scenario_family == "proto2025-v0.1" for row in report.families)
    assert any(row.scenario_family.startswith("siso-") for row in report.families)
    assert all(row.passed for row in report.families if row.baseline_kind == "repo-owned")
    assert all(row.module_names for row in report.families if row.passed)


def test_fom_stress_report_writes_artifacts(tmp_path: Path) -> None:
    json_path, md_path, report = write_fom_stress_report(tmp_path)

    assert json_path.exists()
    assert md_path.exists()
    assert report.title == "FOM parser stress report"
