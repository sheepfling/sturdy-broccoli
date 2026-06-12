from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_sup_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_sup_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 603
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 474, "partial": 129}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("SIG", "mapped"): 86,
            ("SVC", "mapped"): 82,
            ("EFF", "mapped"): 55,
            ("ARG", "mapped"): 43,
            ("EXC", "partial"): 43,
            ("MOM", "mapped"): 43,
            ("PRE", "partial"): 43,
            ("TEST", "mapped"): 43,
            ("RTI_API", "mapped"): 43,
            ("EXC_API", "partial"): 43,
            ("MOM_TRACE", "mapped"): 43,
            ("RET", "mapped"): 31,
            ("CB", "mapped"): 4,
            ("OVW", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_sup_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-SUP-OVERVIEW-013"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-RET"]["current_status"] == "mapped"


def test_sup_handles_overview_row_has_direct_lookup_and_factory_evidence():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516.1-SUP-OVERVIEW-013"]

    assert row["current_status"] == "mapped"
    test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
    assert test_ids == [
        "tests/backends/test_python_backend_support_services.py::test_support_lookups_round_trip_class_handle_and_name",
        "tests/backends/test_python_backend_support_services.py::test_support_dimension_and_update_rate_helpers",
        "tests/backends/test_python_backend_support_services.py::test_support_normalizers_and_factories",
        "tests/backends/test_python_backend_support_services.py::test_support_invalid_inputs_raise_expected_errors",
    ]
    assert "stable" in row["notes"].lower()
    assert "round trips" in row["notes"].lower()
