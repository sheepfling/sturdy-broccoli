from __future__ import annotations

from pathlib import Path

from .reconciliation_helpers import (
    assert_mapped_test_rows_with_companions,
    read_csv_rows,
)


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_1_clause_10_sup_detailed_reconciliation.csv"
)


def _load_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_clause10_support_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(),
        group_key="service_name",
        expected_count=43,
        note_fragment="transport-mediated delivery is not applicable",
    )
