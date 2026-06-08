from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_framework_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_framework_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 53
    statuses = Counter(row["current_status"] for row in rows)
    assert statuses == Counter({"partial": 41, "mapped": 12})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_framework_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516-FW-FW_HLA_COMPONENTS-003"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-FW_HLA_COMPONENTS-003"]["curated_requirement_id"].startswith(
        "HLA1516-FW-001;"
    )
    assert rows["HLA1516-FW-5_1-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-5_2-DET-001"]["current_status"] == "partial"
    assert rows["HLA1516-FW-RULE_5_OWNERSHIP-009"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_status"] == "mapped"
    assert (
        rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_test_id"]
        == "tests/verification/test_framework_rule_docs_v1_0.py::test_framework_docs_capture_product_set_scope_and_source_policy"
    )
