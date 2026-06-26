from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import load_workbook

from scripts.generate_requirement_compliance_spreadsheets import generate_exports


def test_requirement_compliance_spreadsheet_export_writes_both_editions(tmp_path: Path) -> None:
    created = generate_exports(tmp_path)
    names = {path.name for path in created}

    assert names == {
        "requirements_2010_backend_compliance.xlsx",
        "requirements_2010_backend_compliance_detail.csv",
        "requirements_2010_backend_compliance_summary.csv",
        "requirements_2025_backend_compliance.xlsx",
        "requirements_2025_backend_compliance_detail.csv",
        "requirements_2025_backend_compliance_summary.csv",
    }

    workbook_2010 = load_workbook(tmp_path / "requirements_2010_backend_compliance.xlsx", read_only=True)
    workbook_2025 = load_workbook(tmp_path / "requirements_2025_backend_compliance.xlsx", read_only=True)
    assert workbook_2010.sheetnames == ["summary", "detail", "metadata"]
    assert workbook_2025.sheetnames == ["summary", "detail", "metadata"]

    with (tmp_path / "requirements_2010_backend_compliance_detail.csv").open(newline="", encoding="utf-8") as handle:
        rows_2010 = list(csv.DictReader(handle))
    with (tmp_path / "requirements_2025_backend_compliance_detail.csv").open(newline="", encoding="utf-8") as handle:
        rows_2025 = list(csv.DictReader(handle))

    assert any(row["requirement_id"] == "HLA1516.1-FM-4.1.5-001" for row in rows_2010)
    assert any(row["service_group"] == "Data distribution management" for row in rows_2025)
    assert any(row["canonical_status"] == "partial" for row in rows_2010)
    assert any(row["canonical_disposition"] == "covered" for row in rows_2025)
    assert any(row["canonical_disposition"] == "duplicate/umbrella" for row in rows_2025)
