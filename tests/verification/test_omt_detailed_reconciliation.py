from __future__ import annotations

from collections import Counter
from pathlib import Path

from .reconciliation_helpers import read_csv_rows, rows_by_id, status_counts


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_2_omt_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_omt_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 60
    assert status_counts(rows) == Counter(
        {"mapped": 58, "partial": 2}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_omt_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.2-OMT-OMT_SCOPE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.2-COMPONENTS-001"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_CONFORMANCE_LABELS-023"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_CONFORMANCE_VERIFICATION-024"]["current_status"] == "mapped"
    assert rows["HLA1516.2-NORMALIZATION-030"]["current_status"] == "partial"
    assert rows["HLA1516.2-OMT-OMT_NORM_NORMALIZATION-027"]["current_status"] == "partial"
    assert rows["HLA1516.2-MERGE-PRINCIPLES-031"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_NORM_MERGING_PRINCIPLES-028"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_DIF-029"]["current_status"] == "mapped"
    assert rows["HLA1516.2-MERGE-029"]["current_status"] == "mapped"
