from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OM_PATH = ROOT / "requirements" / "2010" / "hla1516_1_om_detailed_reconciliation.csv"


def _load_rows() -> list[dict[str, str]]:
    with OM_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _node_exists(node_id: str) -> bool:
    file_part, _, test_name = node_id.partition("::")
    if not file_part or not test_name:
        return False
    path = Path(file_part)
    if not path.exists():
        return False
    return f"def {test_name}(" in path.read_text(encoding="utf-8")


def test_clause_6_transport_service_and_test_rows_have_direct_supported_subset_evidence():
    rows = _load_rows()
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    targets = {
        "OM-REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHAN": {"SVC", "TEST"},
        "OM-QUERY_ATTRIBUTE_TRANSPORTATION_TYPE": {"SVC", "TEST"},
        "OM-REQUEST_INTERACTION_TRANSPORTATION_TYPE_CH": {"SVC", "TEST"},
        "OM-QUERY_INTERACTION_TRANSPORTATION_TYPE": {"SVC", "TEST"},
    }

    for feature, kinds in targets.items():
        feature_rows = by_feature[feature]
        for kind in kinds:
            row = feature_rows[kind]
            assert row["current_status"] == "mapped"
            assert "supported" in row["notes"].lower()
            assert "subset" in row["notes"].lower()
            test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
            assert len(test_ids) >= 2
            assert all(_node_exists(test_id) for test_id in test_ids)

        for companion_kind in ("SIG", "MOM", "ARG", "PRE"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"


def test_clause_6_transport_seed_rows_follow_mapped_service_or_callback_surface():
    rows = _load_rows()
    by_id = {row["packet_requirement_id"]: row for row in rows}

    targets = {
        "HLA1516.1-OM-6_23-001": ("HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-SVC-001",),
        "HLA1516.1-OM-6_24-001": ("HLA1516.1-OM-6_24-CONFIRMATTRIBUTETRANSPORTATIONTYPECHANGE-CB-001",),
        "HLA1516.1-OM-6_25-001": ("HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-SVC-001",),
        "HLA1516.1-OM-6_26-001": ("HLA1516.1-OM-6_26-REPORTATTRIBUTETRANSPORTATIONTYPE-CB-001",),
        "HLA1516.1-OM-6_27-001": ("HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-SVC-001",),
        "HLA1516.1-OM-6_28-001": ("HLA1516.1-OM-6_28-CONFIRMINTERACTIONTRANSPORTATIONTYPECHANGE-CB-001",),
        "HLA1516.1-OM-6_29-001": ("HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-SVC-001",),
        "HLA1516.1-OM-6_30-001": ("HLA1516.1-OM-6_30-REPORTINTERACTIONTRANSPORTATIONTYPE-CB-001",),
    }

    for seed_id, companion_ids in targets.items():
        seed = by_id[seed_id]
        assert seed["current_status"] == "mapped"
        test_ids = [item.strip() for item in seed["current_test_id"].split(";") if item.strip()]
        assert test_ids
        assert all(_node_exists(test_id) for test_id in test_ids)
        for companion_id in companion_ids:
            assert by_id[companion_id]["current_status"] == "mapped"


def test_clause_6_send_and_delete_test_rows_have_direct_node_level_evidence():
    rows = _load_rows()
    targets = {
        "HLA1516.1-OM-6_12-SENDINTERACTION-TEST-001",
        "HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-TEST-001",
    }
    selected = [row for row in rows if row["packet_requirement_id"] in targets]
    assert len(selected) == 2

    for row in selected:
        assert row["current_status"] == "mapped"
        assert "node-level" in row["notes"]
        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert test_ids
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_clause_6_reflect_and_receive_callback_rows_have_direct_payload_evidence():
    rows = _load_rows()
    targets = {
        "HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB-001": "reflectAttributeValues",
        "HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB_PAYLOAD-001": "reflectAttributeValues",
        "HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB-001": "receiveInteraction",
        "HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB_PAYLOAD-001": "receiveInteraction",
    }
    selected = [row for row in rows if row["packet_requirement_id"] in targets]
    assert len(selected) == len(targets)

    for row in selected:
        assert row["current_status"] == "mapped"
        assert "node-level" in row["notes"]
        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert test_ids
        assert all(_node_exists(test_id) for test_id in test_ids)
