from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import hla.verification.repo_internal.fom_siso_showcase as fom_siso_showcase


def test_build_fom_siso_showcase_tracks_expected_bucket_and_story(monkeypatch, tmp_path: Path) -> None:
    record = SimpleNamespace(
        id="siso-siso-link-16-link-16-v2-0",
        path="artifacts/siso_downloads/Link_16_v2.0.xml",
        edition_class="2010",
        load_mode="ordered-family",
        baseline_kind="third-party",
        scenario_family="siso-link-16",
    )

    monkeypatch.setattr(
        fom_siso_showcase,
        "inventory_records",
        lambda: (record,),
    )
    monkeypatch.setattr(
        fom_siso_showcase,
        "write_fom_validation",
        lambda sources, *, output_dir, edition="auto", strict_identification=False, title=None: (
            Path(output_dir) / "fom_validation_report.json",
            Path(output_dir) / "fom_validation_report.md",
            SimpleNamespace(source_reports=(SimpleNamespace(passed=False, verdict="parse-failed"),), load_set_reports=()),
        ),
    )
    monkeypatch.setattr(
        fom_siso_showcase,
        "write_fom_validation_html",
        lambda sources, *, output_dir, edition="auto", strict_identification=False, title=None: Path(output_dir)
        / "fom_validation_report.html",
    )

    def fail_roundtrip(year, sources, *, output_dir, include_standard_mim=False, title=None):
        raise RuntimeError("standalone link16 cannot round-trip")

    def fail_overview(sources, *, output_dir=None, include_standard_mim=False, title=None):
        raise RuntimeError("standalone link16 cannot merge")

    monkeypatch.setattr(fom_siso_showcase, "write_fom_roundtrip", fail_roundtrip)
    monkeypatch.setattr(fom_siso_showcase, "build_fom_roundtrip", fail_roundtrip)
    monkeypatch.setattr(fom_siso_showcase, "write_fom_overview", fail_overview)
    monkeypatch.setattr(fom_siso_showcase, "write_fom_overview_html", fail_overview)
    monkeypatch.setattr(fom_siso_showcase, "build_fom_overview", fail_overview)

    def fake_write_fom_workbench_snapshot(*, output_dir, custom_load_sets=None, diff_specs=()):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "fom_workbench_snapshot.json"
        path.write_text(json.dumps({"custom_load_sets": custom_load_sets or {}}), encoding="utf-8")
        return path

    def fake_write_fom_workbench_html(*, output_dir, custom_load_sets=None, diff_specs=()):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "fom_workbench.html"
        path.write_text("<html></html>", encoding="utf-8")
        return path

    monkeypatch.setattr(fom_siso_showcase, "write_fom_workbench_snapshot", fake_write_fom_workbench_snapshot)
    monkeypatch.setattr(fom_siso_showcase, "write_fom_workbench_html", fake_write_fom_workbench_html)

    report = fom_siso_showcase.build_fom_siso_showcase(
        output_root=tmp_path / "showcase",
        packet_ids=("link16-standalone-template",),
    )

    assert report.passed is True
    assert len(report.packet_results) == 1
    packet = report.packet_results[0]
    assert packet.id == "link16-standalone-template"
    assert packet.bucket == "parse-fail-fast"
    assert packet.matches_expectation is True
    assert packet.validation_verdict == "parse-failed"
    assert packet.roundtrip_passed is False
    assert packet.overview_passed is False


def test_write_fom_siso_showcase_writes_html(monkeypatch, tmp_path: Path) -> None:
    report = fom_siso_showcase.FOMSisoShowcaseReport(
        title="demo",
        packet_results=(),
        workbench_snapshot_path="snapshot.json",
        workbench_html_path="workbench.html",
        workbench_error=None,
        bucket_counts={},
    )
    monkeypatch.setattr(fom_siso_showcase, "build_fom_siso_showcase", lambda **kwargs: report)

    json_path, md_path, html_path, written_report = fom_siso_showcase.write_fom_siso_showcase(tmp_path / "out")

    assert written_report is report
    assert json_path.exists()
    assert md_path.exists()
    assert html_path.exists()
    html_text = html_path.read_text(encoding="utf-8").lower()
    assert "<!doctype html>" in html_text
    assert "lane legend" in html_text
    assert "template-fail-fast" in html_text
