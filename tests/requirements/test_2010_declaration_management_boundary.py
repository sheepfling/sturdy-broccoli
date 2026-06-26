from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_dm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md"


def test_declaration_management_partial_tail_is_only_pre_exc_and_exc_api() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 38
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "EXC_API": 14,
        "EXC": 12,
        "PRE": 12,
    }


def test_declaration_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Declaration-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-DM`" in text
    assert "`174 mapped`" in text
    assert "`38 partial`" in text
    assert "`14 EXC_API`" in text
    assert "`12 EXC`" in text
    assert "`12 PRE`" in text
