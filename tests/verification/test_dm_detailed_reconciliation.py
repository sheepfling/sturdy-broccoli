from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_dm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_declaration_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 212
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 174, "partial": 38}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_declaration_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-DM-OVERVIEW-004"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-OVERVIEW-004"]["reconciliation_kind"] == "OVW"
    assert rows["HLA1516.1-DM-OVERVIEW-005"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001"]["reconciliation_kind"] == "FED_CB"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001-ORD"]["reconciliation_kind"] == "CB_ORD"
    assert rows["HLA1516.1-DM-5_12-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_12-FEDCB-001-SIG"]["reconciliation_kind"] == "CB_SIG"
    assert rows["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"]["reconciliation_kind"] == "TEST"
