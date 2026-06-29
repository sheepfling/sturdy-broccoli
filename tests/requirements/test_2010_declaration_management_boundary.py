from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_dm_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md"


def test_declaration_management_owner_ledger_is_fully_mapped() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
    assert Counter(row["current_status"] for row in rows) == {"mapped": 212}


def test_declaration_management_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Declaration-Management Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-DM`" in text
    assert "`212 mapped`" in text
    assert "`0 partial`" in text
    assert "the owner ledger no longer carries any remaining DM `partial` rows" in text
    assert "`requirements/2010/canonical_requirements.json`" in text
    assert "`requirements/2010/backend_resolution.json`" in text
    assert "`requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`" in text
    assert "`requirements/2010/traceability_matrix.csv`" in text
    assert "generated projection bridge" in text
    assert "`docs/verification/requirement_compliance_exports.md`" in text
    assert "`./tools/test-focus run backends`" in text
    assert "`./tools/test-surface run unit-scenarios-light`" in text
    assert "../../plans/requirements_gap_register.md" not in text
