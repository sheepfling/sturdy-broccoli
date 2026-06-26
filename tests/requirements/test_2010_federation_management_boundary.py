from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_fm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md"


def test_federation_management_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 109
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "ARG": 43,
        "EFF": 23,
        "CB_ORD": 17,
        "EXC": 15,
        "OVW": 3,
        "CB": 2,
        "FED_CB": 1,
        "MOM": 1,
        "PRE": 1,
        "SVC": 1,
        "EXC_API": 1,
        "MOM_TRACE": 1,
    }


def test_federation_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Federation-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-FM`" in text
    assert "`523 mapped`" in text
    assert "`109 partial`" in text
    assert "`43 ARG`" in text
    assert "`23 EFF`" in text
    assert "`17 CB_ORD`" in text
    assert "`15 EXC`" in text
