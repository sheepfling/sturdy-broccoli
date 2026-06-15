from __future__ import annotations

from collections import Counter
from pathlib import Path

from .reconciliation_helpers import read_csv_rows, rows_by_id, status_counts


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_1_conf_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_conf_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 2
    assert status_counts(rows) == Counter(
        {"mapped": 2}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_conf_detailed_reconciliation_spot_checks():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.1-CONF_FEDERATE-014"]["current_status"] == "mapped"
    assert "test_clause13_conformance_packet_backs_federate_and_rti_claims" in rows[
        "HLA1516.1-CONF_FEDERATE-014"
    ]["current_test_id"]
    assert rows["HLA1516.1-CONF_RTI-015"]["current_status"] == "mapped"
    assert "test_service_by_service_conformance_matrix_covers_generated_api_surface" in rows[
        "HLA1516.1-CONF_RTI-015"
    ]["current_test_id"]
