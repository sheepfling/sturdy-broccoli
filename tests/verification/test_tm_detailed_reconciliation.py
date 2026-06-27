from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_1_tm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_tm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 301
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 243, "partial": 58}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_tm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-TM-OVERVIEW-009"]["current_status"] == "partial"
    assert rows["HLA1516.1-TM-OVERVIEW-010"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001"]["reconciliation_kind"] == "FED_CB"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001-ORD"]["reconciliation_kind"] == "CB_ORD"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-TEST-001"]["reconciliation_kind"] == "TEST"
    assert (
        rows["HLA1516.1-TM-8_22-REQUESTRETRACTION-CB_PAYLOAD-001"]["current_status"]
        == "mapped"
    )
    assert (
        rows["HLA1516.1-TM-8_22-REQUESTRETRACTION-CB_PAYLOAD-001"][
            "reconciliation_kind"
        ]
        == "CB_PAYLOAD"
    )
    assert rows["HLA1516.1-TM-8_16-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_16-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"
    assert "mixed-backend priority-resolution note" in rows["HLA1516.1-TM-OVERVIEW-009"]["notes"]
    assert "applicable precondition surface" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["notes"]
    assert "invalid-lookahead" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["notes"]
    assert "standard exception surface" in rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-EXC-001"]["notes"]
    assert "invalid-or-past logical time" in rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-EXC-001"]["notes"]
    assert "imported API-exception row remains broader" in rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["notes"]
    assert "message-retraction-handle validation" in rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["notes"]


def test_tm_partial_rows_use_explicit_bounded_envelope_notes() -> None:
    rows = _read_rows()
    generic_note = (
        "Repo-native time-management tests exercise related positive or negative behavior, "
        "but this packet row is broader than the current direct evidence."
    )

    for row in rows:
        if row["current_status"] != "partial":
            continue
        assert row["notes"] != generic_note
        if row["reconciliation_kind"] == "PRE":
            assert "applicable precondition surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC":
            assert "standard exception surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC_API":
            assert "imported API-exception row remains broader" in row["notes"]
