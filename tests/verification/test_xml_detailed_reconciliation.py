from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_xml_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_xml_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 367
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"partial": 364, "mapped": 3}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("XML_ELEM", "partial"): 274,
            ("XML_TYPE", "partial"): 89,
            ("CLAUSE12_13_DETAIL", "partial"): 1,
            ("XML_DIF", "mapped"): 1,
            ("OMT_CLAUSE_DETAIL", "mapped"): 1,
            ("XML_SCHEMA", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_xml_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.2-XML-DIF-032"]["current_status"] == "mapped"
    assert rows["HLA1516.2-XML-SCHEMA-033"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_XSD-030"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-ELEM-001"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-TYPE-001"]["current_status"] == "partial"
