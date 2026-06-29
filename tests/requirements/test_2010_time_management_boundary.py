from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_tm_detailed_reconciliation.csv"
CLAUSE8_LEDGER = ROOT / "requirements/2010/hla1516_1_clause_8_tm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/time_management_bounded_family.md"


def test_time_management_owner_ledger_is_fully_mapped() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
    assert Counter(row["current_status"] for row in rows) == {"mapped": 301}


def test_time_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Time-Management Closeout Surface" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "CAP-TM" in text
    assert "mixed_backend_priority_boundaries.md" in text
    assert "`./tools/test-focus run time`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "requirements/2010/canonical_requirements.json" in text
    assert "requirements/2010/backend_resolution.json" in text
    assert "requirements/2010/hla1516_1_tm_detailed_reconciliation.csv" in text
    assert "requirements/2010/traceability_matrix.csv" in text
    assert "generated projection bridge" in text
    assert "requirements/2010/hla_1516_master_harmonization_index_v1_0.csv" in text
    assert "requirement_compliance_exports.md" in text
    assert "HLA1516.1-TM-8.1.2-003" in text
    assert "../../plans/requirements_gap_register.md" not in text


def test_time_management_clause8_tail_uses_explicit_pre_and_exception_notes() -> None:
    rows = list(csv.DictReader(CLAUSE8_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
