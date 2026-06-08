from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from hla2010.requirements_packet import load_imported_hla_packet
from scripts.generate_master_harmonization_index import FIELDNAMES, build_index_rows


INDEX_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla_1516_master_harmonization_index_v1_0.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with INDEX_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_master_harmonization_index_matches_generated_rows():
    expected_rows = build_index_rows()
    actual_rows = _read_rows()

    assert actual_rows
    assert list(actual_rows[0].keys()) == FIELDNAMES
    assert actual_rows == expected_rows


def test_master_harmonization_index_covers_every_imported_master_requirement():
    packet = load_imported_hla_packet()
    rows = _read_rows()

    assert len(rows) == len(packet.master_rows) == 4003
    assert {row["master_requirement_id"] for row in rows} == {
        row.requirement_id for row in packet.master_rows
    }

    statuses = Counter(row["harmonization_status"] for row in rows)
    assert statuses == Counter({"unreconciled": 3104, "mapped": 641, "partial": 258})

    by_id = {row["master_requirement_id"]: row for row in rows}
    assert by_id["HLA1516.1-SUP-10_2-GETAUTOMATICRESIGNDIRECTIVE-TEST-001"][
        "harmonization_status"
    ] == "mapped"
    assert by_id["HLA1516-FW-FW_SCOPE-001"]["harmonization_status"] == "unreconciled"
    assert by_id["HLA1516-FW-FW_SCOPE-001"]["harmonization_source_file"] == "hla1516_framework_rules.csv"
    assert by_id["HLA1516.1-API_MAPPING_OVERVIEW-001"]["harmonization_status"] == "unreconciled"
    assert by_id["HLA1516.1-API_MAPPING_OVERVIEW-001"]["harmonization_source_file"] == "hla1516_1_federate_interface.csv"
    assert by_id["HLA1516.1-SUP-10_2-GETAUTOMATICRESIGNDIRECTIVE-TEST-001"][
        "harmonization_source_file"
    ] == "hla1516_1_clause_10_sup_detailed_reconciliation.csv"
