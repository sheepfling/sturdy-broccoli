from __future__ import annotations

import io
import json
import subprocess
import zipfile
from pathlib import Path

from hla.verification.repo_internal.fom_roundtrip import build_fom_roundtrip, write_fom_roundtrip


def _extract_2025_mim_xml(tmp_path: Path) -> Path:
    outer_zip = Path(__file__).resolve().parents[2] / "specs" / "ieee-1516-2025" / "1516.2-2025_downloads.zip"
    extracted = tmp_path / "HLAstandardMIM-2025.xml"
    with zipfile.ZipFile(outer_zip) as outer:
        inner_name = next(name for name in outer.namelist() if name.endswith(".zip"))
        with zipfile.ZipFile(io.BytesIO(outer.read(inner_name))) as inner:
            xml_name = next(name for name in inner.namelist() if name.endswith("HLAstandardMIM-2025.xml"))
            extracted.write_bytes(inner.read(xml_name))
    return extracted


def test_generate_fom_roundtrip_writes_explicit_2010_and_2025_artifacts(tmp_path: Path) -> None:
    mim_2025 = _extract_2025_mim_xml(tmp_path)

    report_2010 = build_fom_roundtrip(2010)
    assert report_2010.protobuf_schema == "rti1516e"
    assert report_2010.mim_source == "HLAstandardMIM"
    assert {"HLAfederate", "HLAserviceGroup"}.issubset(set(report_2010.merged_summary["dimensions"]))
    assert len(report_2010.module_reports) == 4
    assert all(
        row.xml_roundtrip_ok
        and row.protobuf_file_roundtrip_ok
        and row.protobuf_url_roundtrip_ok
        and row.protobuf_compressed_roundtrip_ok
        for row in report_2010.module_reports
    )

    report_2025 = build_fom_roundtrip(2025, mim_source=mim_2025)
    assert report_2025.protobuf_schema == "rti1516_2025"
    assert report_2025.mim_source == str(mim_2025)
    assert len(report_2025.module_reports) == 2
    assert all(
        row.xml_roundtrip_ok
        and row.protobuf_file_roundtrip_ok
        and row.protobuf_url_roundtrip_ok
        and row.protobuf_compressed_roundtrip_ok
        for row in report_2025.module_reports
    )

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fom-roundtrip"
    result = subprocess.run(
        [
            str(repo_root / "tools" / "fom-roundtrip"),
            "2010",
            "--output-dir",
            str(output_dir),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    json_files = sorted(output_dir.glob("*.json"))
    md_files = sorted(output_dir.glob("*.md"))
    assert len(json_files) == 1
    assert len(md_files) == 1

    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert payload["year"] == 2010
    assert payload["protobuf_schema"] == "rti1516e"
    assert payload["mim_source"] == "HLAstandardMIM"
    assert len(payload["module_reports"]) == 4
    assert payload["module_reports"][0]["xml_roundtrip_ok"] is True
    assert payload["module_reports"][0]["protobuf_file_roundtrip_ok"] is True
    assert payload["module_reports"][0]["protobuf_url_roundtrip_ok"] is True
    assert payload["module_reports"][0]["protobuf_compressed_roundtrip_ok"] is True

    result_2025 = subprocess.run(
        [
            str(repo_root / "tools" / "fom-roundtrip"),
            "2025",
            "--mim-source",
            str(mim_2025),
            "--output-dir",
            str(tmp_path / "fom-roundtrip-2025"),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result_2025.returncode == 0, result_2025.stderr

    direct_json, direct_md = write_fom_roundtrip(2025, output_dir=tmp_path / "direct-2025", mim_source=mim_2025)
    assert direct_json.exists()
    assert direct_md.exists()
