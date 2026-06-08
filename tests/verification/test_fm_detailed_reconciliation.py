from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_fm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_fm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 632
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 498, "partial": 134}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_fm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-FM-4_2-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_2-ARG-001"]["current_status"] == "partial"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-OVERVIEW-001"]["current_status"] == "partial"
