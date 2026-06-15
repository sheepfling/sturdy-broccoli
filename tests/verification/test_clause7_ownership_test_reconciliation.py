from __future__ import annotations

from pathlib import Path

from .reconciliation_helpers import (
    assert_mapped_test_rows_with_companions,
    read_csv_rows,
)


ROOT = Path(__file__).resolve().parents[2]
OWN_PATH = ROOT / "requirements" / "reference" / "hla1516_1_own_detailed_reconciliation.csv"


def _load_rows(path: Path) -> list[dict[str, str]]:
    return read_csv_rows(path)


def test_ownership_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(OWN_PATH),
        group_key="feature",
        expected_count=11,
        note_fragment="broader ARG, PRE, and EXC envelope rows remain partial",
        companion_kinds=("SIG", "MOM", "EFF"),
        min_test_ids=1,
    )
