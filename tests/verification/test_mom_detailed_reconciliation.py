from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_mom_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_mom_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 320
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 320})
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("MIM_PARAM", "mapped"): 101,
            ("MIM_INT", "mapped"): 85,
            ("MIM_DT", "mapped"): 53,
            ("MIM_ATTR", "mapped"): 45,
            ("OBJ", "mapped"): 7,
            ("RTI", "mapped"): 7,
            ("INT", "mapped"): 6,
            ("seed", "mapped"): 4,
            ("MIM_OBJ", "mapped"): 4,
            ("OVW", "mapped"): 3,
            ("SRV", "mapped"): 3,
            ("TABLE", "mapped"): 1,
            ("CLAUSE12_13_DETAIL", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_mom_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-MOM-11_1-OVW-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MOM-OVERVIEW-014"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-OBJ-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-ATTR-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-INT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-PARAM-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-DT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM_NORMATIVE-020"]["current_status"] == "mapped"
