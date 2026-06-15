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
    / "hla1516_1_api_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_api_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 614
    assert status_counts(rows) == Counter(
        {"partial": 394, "mapped": 220}
    )
    assert kind_status_counts(rows) == Counter(
        {
            ("WSDL_OP", "partial"): 308,
            ("CPP_METHOD", "mapped"): 211,
            ("CPP_CLASS", "partial"): 79,
            ("CLAUSE12_13_DETAIL", "partial"): 7,
            ("CLAUSE12_13_DETAIL", "mapped"): 9,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_api_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.1-CPP-4_2-CONNECT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-4_2-CONNECT-001"]["curated_requirement_id"] == "HLA1516.1-FM-001"
    assert (
        rows["HLA1516.1-CPP-4_2-CONNECT-001"]["current_test_id"]
        == "tests/verification/test_spec_traceability_all_methods.py::test_all_generated_ambassador_methods_are_section_mapped;tests/verification/test_requirements_ledger_v013.py::test_requirements_ledger_covers_generated_api_surface"
    )
    assert rows["HLA1516.1-API_MAPPING_OVERVIEW-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_REFLECT_METHODS-008"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_RECEIVE_METHODS-009"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_REMOVE_METHODS-010"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_CPP-012"]["current_status"] == "partial"
    assert rows["HLA1516.1-CPP-12_12-RTIAMBASSADOR-234"]["current_status"] == "partial"
    assert rows["HLA1516.1-API_WSDL-013"]["current_status"] == "partial"
    assert rows["HLA1516.1-WSDL-OP-001"]["current_status"] == "partial"
    assert (
        rows["HLA1516.1-WSDL-OP-001"]["current_test_id"]
        == "tests/verification/test_api_detailed_reconciliation.py::test_api_detailed_reconciliation_spot_checks_key_rows"
    )
