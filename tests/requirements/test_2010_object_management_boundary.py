from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_om_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/object_management_bounded_family.md"


def test_object_management_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 117
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "EFF": 25,
        "CB_ORD": 25,
        "EXC_API": 19,
        "CB_ORDER": 17,
        "EXC": 14,
        "PRE": 10,
        "FED_CB": 6,
        "OVW": 1,
    }


def test_object_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Object-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-OM`" in text
    assert "`274 mapped`" in text
    assert "`117 partial`" in text
    assert "`25 EFF`" in text
    assert "`25 CB_ORD`" in text
    assert "`19 EXC_API`" in text
    assert "`17 CB_ORDER`" in text
    assert "`14 EXC`" in text
    assert "`10 PRE`" in text
