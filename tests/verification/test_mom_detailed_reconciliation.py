from __future__ import annotations

from collections import Counter
from pathlib import Path

from .reconciliation_helpers import (
    kind_status_counts,
    read_csv_rows,
    rows_by_id,
    status_counts,
)


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_1_mom_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_mom_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 320
    assert status_counts(rows) == Counter({"mapped": 320})
    assert kind_status_counts(rows) == Counter(
        {
            ("MIM_PARAM", "mapped"): 101,
            ("MIM_INT", "mapped"): 85,
            ("MIM_DT", "mapped"): 53,
            ("MIM_ATTR", "mapped"): 45,
            ("OVW", "mapped"): 7,
            ("OBJ", "mapped"): 7,
            ("RTI", "mapped"): 7,
            ("INT", "mapped"): 6,
            ("MIM_OBJ", "mapped"): 4,
            ("SRV", "mapped"): 3,
            ("TABLE", "mapped"): 1,
            ("CLAUSE12_13_DETAIL", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_mom_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.1-MOM-11_1-OVW-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MOM-OVERVIEW-014"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-OBJ-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-ATTR-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-INT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-PARAM-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-DT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM_NORMATIVE-020"]["current_status"] == "mapped"
