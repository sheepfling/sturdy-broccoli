from __future__ import annotations

from collections import Counter
from pathlib import Path

from tests.verification.reconciliation_helpers import (
    kind_status_counts,
    read_csv_rows,
    rows_by_id,
    status_counts,
)


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_1_om_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_om_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 391
    assert status_counts(rows) == Counter(
        {"mapped": 274, "partial": 117}
    )
    assert kind_status_counts(rows) == Counter(
        {
            ("CB_SIG", "mapped"): 42,
            ("SIG", "mapped"): 38,
            ("CB", "mapped"): 32,
            ("SVC", "mapped"): 28,
            ("EFF", "partial"): 25,
            ("CB_ORD", "partial"): 25,
            ("ARG", "mapped"): 19,
            ("RTI_API", "mapped"): 19,
            ("EXC_API", "partial"): 19,
            ("MOM_TRACE", "mapped"): 19,
            ("FED_CB", "mapped"): 19,
            ("CB_ORDER", "partial"): 17,
            ("CB_PAYLOAD", "mapped"): 17,
            ("EXC", "partial"): 14,
            ("MOM", "mapped"): 14,
            ("TEST", "mapped"): 14,
            ("PRE", "partial"): 10,
            ("FED_CB", "partial"): 6,
            ("RET", "mapped"): 5,
            ("PRE", "mapped"): 4,
            ("EFF", "mapped"): 3,
            ("OVW", "mapped"): 1,
            ("OVW", "partial"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_om_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.1-OM-OVERVIEW-006"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-OVERVIEW-007"]["current_status"] == "partial"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001-ORD"]["current_status"] == "partial"
    assert rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_20-PROVIDEATTRIBUTEVALUEUPDATE-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_12-SENDINTERACTION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-RTIAPI-001"]["current_status"] == "mapped"


def test_clause_6_object_name_argument_rows_use_direct_name_service_evidence():
    rows = rows_by_id(_read_rows())

    expected = {
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_time_ddm_extended.py::test_name_reservation_ddm_regions_ownership_and_time_support",
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
    }

    for packet_id, test_id in expected.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == test_id
        assert "node-level" in row["notes"]
