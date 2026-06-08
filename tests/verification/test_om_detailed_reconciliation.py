from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla1516_1_om_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_om_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 391
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 266, "partial": 125}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("CB_SIG", "mapped"): 42,
            ("SIG", "mapped"): 38,
            ("EFF", "partial"): 25,
            ("CB_ORD", "partial"): 25,
            ("seed", "mapped"): 30,
            ("RTI_API", "mapped"): 19,
            ("EXC_API", "partial"): 19,
            ("MOM_TRACE", "mapped"): 19,
            ("FED_CB", "mapped"): 19,
            ("CB_ORDER", "partial"): 17,
            ("CB", "mapped"): 15,
            ("CB_PAYLOAD", "mapped"): 15,
            ("ARG", "mapped"): 15,
            ("EXC", "partial"): 14,
            ("MOM", "mapped"): 14,
            ("PRE", "partial"): 10,
            ("SVC", "mapped"): 14,
            ("seed", "partial"): 1,
            ("TEST", "mapped"): 14,
            ("FED_CB", "partial"): 6,
            ("RET", "mapped"): 5,
            ("ARG", "partial"): 4,
            ("PRE", "mapped"): 4,
            ("EFF", "mapped"): 3,
            ("CB", "partial"): 2,
            ("CB_PAYLOAD", "partial"): 2,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_om_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-OM-OVERVIEW-006"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-OVERVIEW-007"]["current_status"] == "partial"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001-ORD"]["current_status"] == "partial"
    assert rows["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB_PAYLOAD-001"]["current_status"] == "partial"
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
