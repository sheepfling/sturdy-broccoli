from __future__ import annotations

from collections import Counter
from pathlib import Path

from .reconciliation_helpers import (
    assert_mapped_test_rows_with_companions,
    read_csv_rows,
    status_counts,
)


ROOT = Path(__file__).resolve().parents[2]
DM_PATH = ROOT / "requirements" / "reference" / "hla1516_1_dm_detailed_reconciliation.csv"
CLAUSE_5_PATH = ROOT / "requirements" / "reference" / "hla1516_1_clause_5_dm_detailed_reconciliation.csv"


def _load_rows() -> list[dict[str, str]]:
    return read_csv_rows(DM_PATH)


def _load_clause5_rows() -> list[dict[str, str]]:
    return read_csv_rows(CLAUSE_5_PATH)


def test_declaration_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(),
        group_key="feature",
        expected_count=12,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )


def test_clause5_declaration_test_rows_match_family_level_direct_evidence():
    rows = _load_clause5_rows()
    assert status_counts(rows) == Counter(
        {"mapped": 92, "partial": 24}
    )
    assert_mapped_test_rows_with_companions(
        rows,
        group_key="feature",
        expected_count=12,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )
