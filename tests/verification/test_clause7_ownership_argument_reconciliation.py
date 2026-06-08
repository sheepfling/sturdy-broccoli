from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLAUSE_7_PATH = (
    ROOT / "requirements" / "hla1516_1_clause_7_own_detailed_reconciliation.csv"
)


def _load_rows() -> list[dict[str, str]]:
    with CLAUSE_7_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _node_exists(node_id: str) -> bool:
    file_part, _, test_name = node_id.partition("::")
    if not file_part or not test_name:
        return False
    path = ROOT / file_part if not Path(file_part).is_absolute() else Path(file_part)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return f"def {test_name}(" in text


def test_clause7_ownership_argument_rows_use_direct_negative_path_nodes():
    rows = {row["packet_requirement_id"]: row for row in _load_rows()}

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
        assert _node_exists(test_id)
        assert "Direct ownership negative-path tests now prove object-handle and attribute-handle validation" in row["notes"]


def test_clause7_ownership_argument_status_counts_reflect_promoted_rows():
    rows = _load_rows()
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 94, "partial": 30}
    )

    arg_rows = [row for row in rows if row["reconciliation_kind"] == "ARG"]
    assert Counter(row["current_status"] for row in arg_rows) == Counter(
        {"mapped": 11}
    )
