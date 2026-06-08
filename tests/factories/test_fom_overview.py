from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hla2010.fom_overview import build_fom_overview, write_fom_overview, write_fom_overview_html


def test_generate_fom_overview_writes_merged_target_radar_summary(tmp_path):
    report = build_fom_overview("TargetRadarFOMmodule.xml")
    assert report.title == "HLAstandardMIM + Target Radar FOM Module"
    assert len(report.object_rows) == 6
    assert len(report.interaction_rows) == 86

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fom-overview"
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_fom_overview.py",
            "TargetRadarFOMmodule.xml",
            "--output-dir",
            str(output_dir),
            "--html",
        ],
        cwd=repo_root,
        check=True,
    )

    json_files = sorted(output_dir.glob("*.json"))
    md_files = sorted(output_dir.glob("*.md"))
    html_files = sorted(output_dir.glob("*.html"))
    assert len(json_files) == 1
    assert len(md_files) == 1
    assert len(html_files) == 2
    index_path = output_dir / "index.html"
    assert index_path.exists()

    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert len(payload["merged_summary"]["object_classes"]) == 6
    assert len(payload["merged_summary"]["interaction_classes"]) == 86
    assert payload["merged_summary"]["dimensions"] == ["HLAfederate", "HLAserviceGroup"]
    assert payload["merged_summary"]["logical_time_implementation"] == "HLAfloat64Time"

    md_text = md_files[0].read_text(encoding="utf-8")
    assert "# HLAstandardMIM + Target Radar FOM Module" in md_text
    assert "## Object Classes Tree" in md_text
    assert "## Interaction Classes Tree" in md_text

    direct_json, direct_md = write_fom_overview("TargetRadarFOMmodule.xml", output_dir=tmp_path / "direct")
    assert direct_json.exists()
    assert direct_md.exists()

    html_path = write_fom_overview_html("TargetRadarFOMmodule.xml", output_dir=tmp_path / "html")
    html_text = html_path.read_text(encoding="utf-8")
    assert "<title>HLAstandardMIM + Target Radar FOM Module | FOM Overview</title>" in html_text
    assert "Object Classes Tree" in html_text
    assert "Interaction Classes Tree" in html_text
    assert 'id="object_detail_hlaobjectroot"' in html_text

    index_text = index_path.read_text(encoding="utf-8")
    assert "Target Radar FOM Module index" in index_text
    assert "Filter object classes" in index_text
    assert "Filter interaction classes" in index_text
    assert "Selected class" in index_text
    assert "Selected class provenance" in index_text
    assert "Show only leaf nodes" in index_text
    assert "ancestor-panel" in index_text
    assert "toggleLeaves(" in index_text
    assert "history.replaceState" in index_text
    assert "hlastandardmim-target-radar-fom-module.html" in index_text
