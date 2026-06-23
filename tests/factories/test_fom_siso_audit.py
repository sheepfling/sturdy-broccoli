from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import hla.verification.repo_internal.fom_siso_audit as fom_siso_audit


def test_build_fom_siso_audit_runs_family_pipeline(monkeypatch, tmp_path: Path) -> None:
    family = "siso-rpr-2.0"
    record = SimpleNamespace(
        id="siso-rpr-2.0-root",
        path="analysis/siso_downloads/rpr/root.xml",
        edition_class="2010",
        scenario_family=family,
    )

    monkeypatch.setattr(
        fom_siso_audit,
        "HIGH_VALUE_SISO_FAMILIES",
        (family,),
    )
    monkeypatch.setattr(
        fom_siso_audit,
        "inventory_records_by_family",
        lambda: {family: (record,)},
    )

    def fake_write_fom_validation(sources, *, output_dir, families=(), edition="auto", profile="auto", strict_identification=False, schema_path=None, title=None):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "fom_validation_report.json"
        md_path = output_dir / "fom_validation_report.md"
        json_path.write_text("{}", encoding="utf-8")
        md_path.write_text("# validation\n", encoding="utf-8")
        report = SimpleNamespace(
            source_reports=(SimpleNamespace(passed=True, verdict="conforming"),),
            load_set_reports=(SimpleNamespace(kind="family", name=family, passed=True, verdict="conforming"),),
        )
        return json_path, md_path, report

    def fake_write_fom_roundtrip(year, sources, *, output_dir, include_standard_mim=True, mim_source=None, title=None):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"fom-roundtrip-{year}.json"
        md_path = output_dir / f"fom-roundtrip-{year}.md"
        json_path.write_text("{}", encoding="utf-8")
        md_path.write_text("# roundtrip\n", encoding="utf-8")
        return json_path, md_path

    def fake_build_fom_roundtrip(year, sources, *, include_standard_mim=True, mim_source=None, title=None):
        return SimpleNamespace(
            year=year,
            module_reports=(
                SimpleNamespace(
                    xml_roundtrip_ok=True,
                    protobuf_file_roundtrip_ok=True,
                    protobuf_url_roundtrip_ok=True,
                    protobuf_compressed_roundtrip_ok=True,
                ),
            ),
        )

    def fake_write_fom_workbench_snapshot(*, output_dir, custom_load_sets=None, diff_specs=()):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "fom_workbench_snapshot.json"
        path.write_text(json.dumps({"custom_load_sets": [{"name": next(iter(custom_load_sets or {}))}]}), encoding="utf-8")
        return path

    def fake_write_fom_workbench_html(*, output_dir, custom_load_sets=None, diff_specs=()):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "fom_workbench.html"
        path.write_text("<html></html>", encoding="utf-8")
        return path

    monkeypatch.setattr(fom_siso_audit, "write_fom_validation", fake_write_fom_validation)
    monkeypatch.setattr(fom_siso_audit, "write_fom_roundtrip", fake_write_fom_roundtrip)
    monkeypatch.setattr(fom_siso_audit, "build_fom_roundtrip", fake_build_fom_roundtrip)
    monkeypatch.setattr(fom_siso_audit, "write_fom_workbench_snapshot", fake_write_fom_workbench_snapshot)
    monkeypatch.setattr(fom_siso_audit, "write_fom_workbench_html", fake_write_fom_workbench_html)

    report = fom_siso_audit.build_fom_siso_audit(output_root=tmp_path / "audit")

    assert report.passed is True
    assert [row.family for row in report.family_results] == [family]
    assert report.family_results[0].edition_scope == "2010 only"
    assert report.family_results[0].bucket == "validate-clean"
    assert report.family_results[0].validation_passed is True
    assert report.family_results[0].roundtrip_passed is True
    assert report.family_results[0].validation_verdict == "conforming"
    assert report.bucket_counts["validate-clean"] == 1
