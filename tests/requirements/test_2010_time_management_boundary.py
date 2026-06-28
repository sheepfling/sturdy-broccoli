from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_tm_detailed_reconciliation.csv"
CLAUSE8_LEDGER = ROOT / "requirements/2010/hla1516_1_clause_8_tm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/time_management_bounded_family.md"


def test_time_management_partial_tail_is_only_pre_exc_exc_api_and_one_overview() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 1
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {"OVW": 1}


def test_time_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Time-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-TM`" in text
    assert "`300 mapped`" in text
    assert "`1 partial`" in text
    assert "`1 OVW`" in text
    assert "mixed_backend_priority_boundaries.md" in text
    assert "`./tools/test-focus run time`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "requirements/2010/hla1516_1_tm_detailed_reconciliation.csv" in text
    assert "requirements/2010/traceability_matrix.csv" in text
    assert "requirements/2010/hla_1516_master_harmonization_index_v1_0.csv" in text
    assert "requirement_compliance_exports.md" in text
    assert "../../plans/requirements_gap_register.md" not in text


def test_time_management_clause8_tail_uses_explicit_pre_and_exception_notes() -> None:
    rows = list(csv.DictReader(CLAUSE8_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
