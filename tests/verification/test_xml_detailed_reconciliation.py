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
    / "hla1516_xml_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_xml_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 367
    assert status_counts(rows) == Counter(
        {"partial": 364, "mapped": 3}
    )
    assert kind_status_counts(rows) == Counter(
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
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.2-XML-DIF-032"]["current_status"] == "mapped"
    assert rows["HLA1516.2-XML-SCHEMA-033"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_XSD-030"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-ELEM-001"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-TYPE-001"]["current_status"] == "partial"
