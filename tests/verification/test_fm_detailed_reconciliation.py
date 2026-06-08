from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_fm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_fm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 632
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 510, "partial": 122}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_fm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-FM-4_2-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_2-ARG-001"]["current_status"] == "partial"
    assert rows["HLA1516.1-FM-4_8-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-OVERVIEW-001"]["current_status"] == "partial"


def test_fm_report_federation_executions_argument_row_has_direct_payload_evidence():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516.1-FM-4_8-ARG-001"]

    assert row["current_status"] == "mapped"
    assert (
        row["current_test_id"]
        == "tests/backends/test_python_backend_federation_extended.py::test_list_federation_executions_requires_connection_and_reports_known_federations"
    )
    assert "node-level" in row["notes"]
    assert "federation-execution information records" in row["notes"]


def test_fm_save_restore_effect_rows_use_direct_positive_state_witnesses():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    single_test_rows = {
        "HLA1516.1-FM-4_18-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_18-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-RTIAPI-001-EFF-DUP02": "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
        "HLA1516.1-FM-4_21-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_21-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
    }

    for packet_id, test_id in single_test_rows.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == test_id
        assert row["notes"].startswith("Direct ")

    for packet_id in (
        "HLA1516.1-FM-4_20-EFF-001",
        "HLA1516.1-FM-4_20-EFF-002",
        "HLA1516.1-FM-4_22-EFF-001",
        "HLA1516.1-FM-4_22-RTIAPI-001-EFF",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) == 2
        assert all(
            test_id.startswith("tests/backends/test_python_backend_federation_extended.py::")
            for test_id in test_ids
        )
        assert row["notes"].startswith("Direct ")
