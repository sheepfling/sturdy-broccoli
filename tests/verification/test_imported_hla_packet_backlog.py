from __future__ import annotations

import json
from pathlib import Path

from hla2010.requirements_backlog import write_imported_hla_backlog


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
