from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_sup_detailed_reconciliation.csv"
CLAUSE10_LEDGER = ROOT / "requirements/2010/hla1516_1_clause_10_sup_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/support_services_bounded_family.md"


def test_support_services_partial_tail_is_only_pre_exc_and_exc_api() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 129
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "PRE": 43,
        "EXC": 43,
        "EXC_API": 43,
    }


def test_support_services_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Support-Services Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-SUP`" in text
    assert "`474 mapped`" in text
    assert "`129 partial`" in text
    assert "`43 PRE`" in text
    assert "`43 EXC`" in text
    assert "`43 EXC_API`" in text
    assert "`REQ-RTI-SS-10_44-getMessageRetractionHandleFactory`" in text
    assert "`REQ-RTI-SS-10_44-getRegionHandleFactory`" in text
    assert "`python_runtime_disposition=verified`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text


def test_support_services_clause10_tail_uses_explicit_pre_and_exception_notes() -> None:
    rows = list(csv.DictReader(CLAUSE10_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 86
    for row in partial_rows:
        if row["reconciliation_kind"] == "PRE":
            assert "applicable precondition surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC":
            assert "standard exception surface" in row["notes"]

    by_id = {row["packet_requirement_id"]: row for row in partial_rows}
    assert "resign-action helper guards" in by_id[
        "HLA1516.1-SUP-10_3-SETAUTOMATICRESIGNDIRECTIVE-PRE-001"
    ]["notes"]
    assert "duplicate-switch-state" in by_id[
        "HLA1516.1-SUP-10_39-ENABLEINTERACTIONRELEVANCEADVISORYSWITCH-PRE-001"
    ]["notes"]
    assert "CallNotAllowedFromWithinCallback" in by_id[
        "HLA1516.1-SUP-10_41-EVOKECALLBACK-EXC-001"
    ]["notes"]
