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

    assert len(partial_rows) == 0
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {}


def test_support_services_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Support-Services Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-SUP`" in text
    assert "`603 mapped`" in text
    assert "`0 partial`" in text
    assert "`REQ-RTI-SS-10_44-getMessageRetractionHandleFactory`" in text
    assert "`REQ-RTI-SS-10_44-getRegionHandleFactory`" in text
    assert "`python_runtime_disposition=verified`" in text
    assert "There are no remaining partial support rows for:" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text
    assert "requirements/2010/canonical_requirements.json" in text
    assert "requirements/2010/backend_resolution.json" in text
    assert "requirements/2010/hla1516_1_sup_detailed_reconciliation.csv" in text
    assert "requirements/2010/traceability_matrix.csv" in text
    assert "generated projection bridge" in text
    assert "docs/verification/requirement_compliance_exports.md" in text
    assert "analysis/compliance/requirements_matrix_2010.csv" not in text
    assert "analysis/compliance/requirements_ledger.csv" not in text
    assert "analysis/compliance/service_conformance.json" not in text
    assert "../../plans/requirements_gap_register.md" not in text


def test_support_services_clause10_tail_uses_explicit_pre_and_exception_notes() -> None:
    rows = list(csv.DictReader(CLAUSE10_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
