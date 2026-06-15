from __future__ import annotations

from collections import Counter
from pathlib import Path

from tests.verification.reconciliation_helpers import read_csv_rows, rows_by_id, status_counts


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_framework_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_framework_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 53
    statuses = status_counts(rows)
    assert statuses == Counter({"partial": 41, "mapped": 12})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_framework_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

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
