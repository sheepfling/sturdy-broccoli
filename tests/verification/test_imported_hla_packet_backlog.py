from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.requirements_backlog import write_imported_hla_backlog


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_imported_hla_backlog_is_generated_with_expected_families(tmp_path: Path):
    markdown_path = tmp_path / "imported_requirements_backlog_v1_0.md"
    json_path = tmp_path / "imported_requirements_backlog_v1_0.json"

    written = write_imported_hla_backlog(markdown_path, json_path)

    assert written["markdown"] == markdown_path
    assert written["json"] == json_path

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Imported HLA Requirements Backlog v1.0" in markdown
    assert "## Federation Management" in markdown
    assert "## MOM/MIM" in markdown
    assert "## Transports" in markdown

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    families = [family["family"] for family in payload["families"]]
    assert families == [
        "Federation Management",
        "Declaration Management",
        "Object Management",
        "Ownership Management",
        "Time Management",
        "Data Distribution Management",
        "Support Services",
        "MOM/MIM",
        "OMT",
        "XML",
        "Transports",
    ]
    assert payload["total_open_rows"] >= 1
    assert any(family["family"] == "Transports" and family["open_row_count"] >= 1 for family in payload["families"])
    federation_management = next(family for family in payload["families"] if family["family"] == "Federation Management")
    connect_item = next(item for item in federation_management["queue_items"] if item["queue_item"] == "Connect")
    assert connect_item["suggested_next_action"].startswith("Optional: tighten this bounded FM state-vector tail")


def test_imported_hla_backlog_script_bootstraps_source_checkout(tmp_path: Path):
    markdown_path = tmp_path / "imported_requirements_backlog_v1_0.md"
    json_path = tmp_path / "imported_requirements_backlog_v1_0.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_imported_packet_backlog.py",
            "--markdown",
            str(markdown_path),
            "--json",
            str(json_path),
        ],
        cwd=REPO_ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert markdown_path.exists()
    assert json_path.exists()
