from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md"


def test_ddm_partial_tail_is_only_pre_exc_and_exc_api() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 46
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "EXC_API": 18,
        "EXC": 14,
        "PRE": 14,
    }


def test_ddm_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Data-Distribution-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-DDM`" in text
    assert "`177 mapped`" in text
    assert "`46 partial`" in text
    assert "`18 EXC_API`" in text
    assert "`14 EXC`" in text
    assert "`14 PRE`" in text
