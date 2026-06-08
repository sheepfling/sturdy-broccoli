from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_own_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_ownership_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 225
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 195, "partial": 30}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_ownership_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-OWN-OVERVIEW-008"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-OVERVIEW-008"]["reconciliation_kind"] == "seed"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-OWN-7_4-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_4-FEDCB-001"]["reconciliation_kind"] == "FED_CB"
    assert rows["HLA1516.1-OWN-7_4-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_4-FEDCB-001-ORD"]["reconciliation_kind"] == "CB_ORD"
    assert rows["HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-TEST-001"]["reconciliation_kind"] == "TEST"
    assert rows["HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_3-NEGOTIATEDATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_6-CONFIRMDIVESTITURE-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_8-ATTRIBUTEOWNERSHIPACQUISITION-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_9-ATTRIBUTEOWNERSHIPACQUISITIONIFAVAILABLE-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_12-ATTRIBUTEOWNERSHIPRELEASEDENIED-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_13-ATTRIBUTEOWNERSHIPDIVESTITUREIFWANTED-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_13-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_13-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"
    assert rows["HLA1516.1-OWN-7_19-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OWN-7_19-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"


def test_ownership_argument_rows_use_direct_negative_path_nodes():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    expected = {
        "HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_unconditional_divestiture_query_ownership_and_is_owned_reject_not_connected_not_joined_unknown_object_and_save_restore",
        "HLA1516.1-OWN-7_3-NEGOTIATEDATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_negotiated_attribute_ownership_divestiture_rejects_not_connected_not_joined_unknown_object_and_save_restore",
        "HLA1516.1-OWN-7_6-CONFIRMDIVESTITURE-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_confirm_divestiture_rejects_not_connected_not_joined_unknown_object_and_not_owned",
        "HLA1516.1-OWN-7_8-ATTRIBUTEOWNERSHIPACQUISITION-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_attribute_ownership_acquisition_services_reject_not_connected_not_joined_unknown_object_and_owned_attributes",
        "HLA1516.1-OWN-7_9-ATTRIBUTEOWNERSHIPACQUISITIONIFAVAILABLE-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_attribute_ownership_acquisition_services_reject_not_connected_not_joined_unknown_object_and_owned_attributes",
        "HLA1516.1-OWN-7_12-ATTRIBUTEOWNERSHIPRELEASEDENIED-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_attribute_ownership_release_denied_and_divestiture_if_wanted_reject_not_connected_not_joined_unknown_object_and_save_restore",
        "HLA1516.1-OWN-7_13-ATTRIBUTEOWNERSHIPDIVESTITUREIFWANTED-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_attribute_ownership_release_denied_and_divestiture_if_wanted_reject_not_connected_not_joined_unknown_object_and_save_restore",
    }

    for packet_id, test_id in expected.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == test_id
        assert "node-level" in row["notes"]
