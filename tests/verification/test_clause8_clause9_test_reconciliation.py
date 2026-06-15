from __future__ import annotations

from pathlib import Path

from tests.verification.reconciliation_helpers import (
    assert_mapped_test_rows_with_companions,
    read_csv_rows,
)


ROOT = Path(__file__).resolve().parents[2]
CLAUSE8_PATH = ROOT / "requirements" / "reference" / "hla1516_1_clause_8_tm_detailed_reconciliation.csv"
CLAUSE9_PATH = ROOT / "requirements" / "reference" / "hla1516_1_clause_9_ddm_detailed_reconciliation.csv"
TM_PATH = ROOT / "requirements" / "reference" / "hla1516_1_tm_detailed_reconciliation.csv"
DDM_PATH = ROOT / "requirements" / "reference" / "hla1516_1_ddm_detailed_reconciliation.csv"


def _load_rows(path: Path) -> list[dict[str, str]]:
    return read_csv_rows(path)


def test_clause8_time_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(CLAUSE8_PATH),
        group_key="service_name",
        expected_count=19,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )


def test_clause9_ddm_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(CLAUSE9_PATH),
        group_key="service_name",
        expected_count=14,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )


def test_tm_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(TM_PATH),
        group_key="feature",
        expected_count=19,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )


def test_ddm_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    assert_mapped_test_rows_with_companions(
        _load_rows(DDM_PATH),
        group_key="feature",
        expected_count=14,
        note_fragment="broader PRE and EXC envelope rows remain partial",
    )
