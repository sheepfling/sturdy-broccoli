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

    assert len(partial_rows) == 58
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "PRE": 19,
        "EXC": 19,
        "EXC_API": 19,
        "OVW": 1,
    }


def test_time_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Time-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-TM`" in text
    assert "`243 mapped`" in text
    assert "`58 partial`" in text
    assert "`19 PRE`" in text
    assert "`19 EXC`" in text
    assert "`19 EXC_API`" in text
    assert "`1 OVW`" in text
    assert "mixed_backend_priority_boundaries.md" in text
    assert "`./tools/test-focus run time`" in text
    assert "`./tools/test-focus run backends`" in text


def test_time_management_clause8_tail_uses_explicit_pre_and_exception_notes() -> None:
    rows = list(csv.DictReader(CLAUSE8_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 38
    for row in partial_rows:
        if row["reconciliation_kind"] == "PRE":
            assert "applicable precondition surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC":
            assert "standard exception surface" in row["notes"]

    by_id = {row["packet_requirement_id"]: row for row in partial_rows}
    assert "failed-request callback-suppression guards" in by_id[
        "HLA1516.1-TM-8_5-ENABLETIMECONSTRAINED-PRE-001"
    ]["notes"]
    assert "outstanding-advance" in by_id[
        "HLA1516.1-TM-8_10-NEXTMESSAGEREQUEST-EXC-001"
    ]["notes"]
    assert "message-retraction-handle validation" in by_id[
        "HLA1516.1-TM-8_21-RETRACT-EXC-001"
    ]["notes"]
