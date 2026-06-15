from __future__ import annotations

from collections import Counter
from pathlib import Path

from hla2010_repo_internal.requirements_packet import load_imported_hla_packet
from tests.verification.reconciliation_helpers import read_csv_rows, rows_by_id, status_counts


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_2_omt_xml_detailed_reconciliation.csv"
)

EXPECTED_COLUMNS = [
    "packet_requirement_id",
    "curated_requirement_id",
    "standard",
    "clause",
    "feature",
    "reconciliation_kind",
    "source_detail",
    "requirement_text",
    "packet_verification_method",
    "current_test_id",
    "current_status",
    "implementation_area",
    "source_packet_file",
    "notes",
]


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_omt_xml_detailed_reconciliation_matches_imported_packet_shape():
    rows = _read_rows()
    packet = load_imported_hla_packet()

    assert rows
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert len(rows) == len(packet.omt_xml_detailed_rows) == 1292
    assert {row["standard"] for row in rows} == {"IEEE 1516.2-2010 (2010 edition)"}
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_omt_xml_detailed_requirements_v1_0.csv"
    }
    assert {row["reconciliation_kind"] for row in rows} == {
        "omt_clause_detail",
        "xsd_element_detail",
        "xsd_type_detail",
    }


def test_omt_xml_detailed_reconciliation_status_distribution_is_intentional():
    rows = _read_rows()
    statuses = status_counts(rows)

    assert statuses == Counter({"partial": 1270, "mapped": 22})

    by_id = rows_by_id(rows)
    assert by_id["HLA1516.2-OMT-4_1-SEM-001"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_C-SEM-019"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_B-SEM-018"]["current_status"] == "partial"
    assert by_id["HLA1516.2-OMT-Annex_F-SEM-022"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_G-SEM-023"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-XML-SCHEMA-ELEM-0001"]["current_status"] == "partial"
    assert by_id["HLA1516.2-XML-SCHEMA-TYPE-0001"]["current_status"] == "partial"

    assert by_id["HLA1516.2-OMT-4_1-SEM-001"]["curated_requirement_id"].startswith(
        "HLA1516.2-OMID-4.1-001"
    )
    assert "HLA1516.2-OMT-E-001" in by_id["HLA1516.2-XML-SCHEMA-ELEM-0001"][
        "curated_requirement_id"
    ]
    assert by_id["HLA1516.2-OMT-Annex_F-SEM-022"]["curated_requirement_id"] == "HLA1516.2-OMT-F-001"
    assert by_id["HLA1516.2-OMT-Annex_G-SEM-023"]["curated_requirement_id"] == "HLA1516.2-OMT-G-001"
