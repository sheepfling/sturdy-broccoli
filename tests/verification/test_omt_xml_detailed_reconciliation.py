from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements_packet import load_imported_hla_packet


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
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
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_omt_xml_detailed_reconciliation_matches_imported_packet_shape():
    rows = _read_rows()
    packet = load_imported_hla_packet()

    assert rows
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert len(rows) == len(packet.omt_xml_detailed_rows) == 1292
    assert {row["standard"] for row in rows} == {"IEEE 1516.2-2010"}
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
    statuses = Counter(row["current_status"] for row in rows)

    assert set(statuses) <= {"mapped", "partial"}
    assert statuses["mapped"] >= 23
    assert statuses["partial"] <= 1269
    assert statuses["mapped"] + statuses["partial"] == len(rows)

    by_id = {row["packet_requirement_id"]: row for row in rows}
    assert by_id["HLA1516.2-OMT-4_1-SEM-001"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_C-SEM-019"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_B-SEM-018"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_F-SEM-022"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-Annex_G-SEM-023"]["current_status"] == "mapped"
    assert by_id["HLA1516.2-XML-SCHEMA-ELEM-0001"]["current_status"] == "partial"
    assert by_id["HLA1516.2-XML-SCHEMA-TYPE-0001"]["current_status"] == "partial"
    assert "common Annex B subset" in by_id["HLA1516.2-OMT-Annex_B-SEM-018"]["notes"]

    assert by_id["HLA1516.2-OMT-4_1-SEM-001"]["curated_requirement_id"].startswith(
        "HLA1516.2-OMID-4.1-001"
    )
    assert "HLA1516.2-OMT-E-001" in by_id["HLA1516.2-XML-SCHEMA-ELEM-0001"][
        "curated_requirement_id"
    ]
    assert by_id["HLA1516.2-OMT-Annex_F-SEM-022"]["curated_requirement_id"] == "HLA1516.2-OMT-F-001"
    assert by_id["HLA1516.2-OMT-Annex_G-SEM-023"]["curated_requirement_id"] == "HLA1516.2-OMT-G-001"
