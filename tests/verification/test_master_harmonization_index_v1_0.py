from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from hla2010.requirements_packet import load_imported_hla_packet
from scripts.generate_master_harmonization_index import FIELDNAMES, build_index_rows


INDEX_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "hla_1516_master_harmonization_index_v1_0.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with INDEX_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_master_harmonization_index_matches_generated_rows():
    expected_rows = build_index_rows()
    actual_rows = _read_rows()

    assert actual_rows
    assert list(actual_rows[0].keys()) == FIELDNAMES
    assert actual_rows == expected_rows


def test_master_harmonization_index_covers_every_imported_master_requirement():
    packet = load_imported_hla_packet()
    rows = _read_rows()

    assert len(rows) == len(packet.master_rows) == 4003
    assert {row["master_requirement_id"] for row in rows} == {
        row.requirement_id for row in packet.master_rows
    }

    statuses = Counter(row["harmonization_status"] for row in rows)
    assert statuses == Counter(
        {"mapped": 2651, "partial": 1352}
    )

    by_id = {row["master_requirement_id"]: row for row in rows}
    assert by_id["HLA1516.1-SUP-10_2-GETAUTOMATICRESIGNDIRECTIVE-TEST-001"][
        "harmonization_status"
    ] == "mapped"
    assert (
        by_id["HLA1516.1-SUP-10_2-GETAUTOMATICRESIGNDIRECTIVE-TEST-001"][
            "harmonization_source_file"
        ]
        == "hla1516_1_sup_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-SUP-OVERVIEW-013"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-SUP-OVERVIEW-013"]["harmonization_source_file"]
        == "hla1516_1_sup_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516-FW-FW_SCOPE-001"]["harmonization_status"] == "partial"
    assert (
        by_id["HLA1516-FW-FW_SCOPE-001"]["harmonization_source_file"]
        == "hla1516_framework_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-API_MAPPING_OVERVIEW-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-API_MAPPING_OVERVIEW-001"]["harmonization_source_file"]
        == "hla1516_1_api_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-FM-4_2-SVC-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-FM-4_2-SVC-001"]["harmonization_source_file"]
        == "hla1516_1_fm_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-FM-4_8-ARG-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-FM-4_8-ARG-001"]["harmonization_source_file"]
        == "hla1516_1_fm_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-OM-6_2-RTIAPI-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-OM-6_2-RTIAPI-001"]["harmonization_source_file"]
        == "hla1516_1_om_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_23-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_24-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_25-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_26-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_27-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_28-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_29-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_30-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB-001"][
            "harmonization_source_file"
        ]
        == "hla1516_1_om_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB_PAYLOAD-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB_PAYLOAD-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_12-SENDINTERACTION-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-SVC-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-SVC-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-SVC-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-SVC-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-TEST-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OM-OVERVIEW-007"]["harmonization_status"] == "partial"
    assert by_id["HLA1516.1-TM-OVERVIEW-009"]["harmonization_status"] == "partial"
    assert (
        by_id["HLA1516.1-TM-OVERVIEW-009"]["harmonization_source_file"]
        == "hla1516_1_tm_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-TM-8_2-RTIAPI-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-TM-8_2-RTIAPI-001"]["harmonization_source_file"]
        == "hla1516_1_tm_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-TEST-001"]["harmonization_status"]
        == "mapped"
    )
    assert by_id["HLA1516.1-DDM-OVERVIEW-012"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-DDM-OVERVIEW-012"]["harmonization_source_file"]
        == "hla1516_1_ddm_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"]["harmonization_status"]
        == "mapped"
    )
    assert by_id["HLA1516.1-DDM-9_2-RTIAPI-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-DDM-9_2-RTIAPI-001"]["harmonization_source_file"]
        == "hla1516_1_ddm_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"]["harmonization_status"]
        == "partial"
    )
    assert by_id["HLA1516.1-DDM-9_12-RTIAPI-002-RET"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-OVERVIEW-008"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-OWN-OVERVIEW-008"]["harmonization_source_file"]
        == "hla1516_1_own_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-OWN-7_2-RTIAPI-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-OWN-7_2-RTIAPI-001"]["harmonization_source_file"]
        == "hla1516_1_own_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_3-NEGOTIATEDATTRIBUTEOWNERSHIPDIVESTITURE-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_6-CONFIRMDIVESTITURE-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_8-ATTRIBUTEOWNERSHIPACQUISITION-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_9-ATTRIBUTEOWNERSHIPACQUISITIONIFAVAILABLE-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_12-ATTRIBUTEOWNERSHIPRELEASEDENIED-ARG-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-OWN-7_13-ATTRIBUTEOWNERSHIPDIVESTITUREIFWANTED-ARG-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-TEST-001"][
            "harmonization_status"
        ]
        == "mapped"
    )
    assert (
        by_id["HLA1516.1-OWN-7_2-RTIAPI-001-EXC"]["harmonization_status"]
        == "partial"
    )
    assert by_id["HLA1516.1-OWN-7_13-RTIAPI-001-RET"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-DM-OVERVIEW-004"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-DM-OVERVIEW-004"]["harmonization_source_file"]
        == "hla1516_1_dm_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-DM-5_2-RTIAPI-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-DM-5_2-RTIAPI-001"]["harmonization_source_file"]
        == "hla1516_1_dm_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"][
            "harmonization_status"
        ]
        == "mapped"
    )
    assert by_id["HLA1516.1-API_REFLECT_METHODS-008"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-API_RECEIVE_METHODS-009"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-API_REMOVE_METHODS-010"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-DM-5_2-RTIAPI-001-EXC"]["harmonization_status"]
        == "partial"
    )
    assert by_id["HLA1516.1-DM-5_10-FEDCB-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.2-OMT-OMT_SCOPE-001"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.2-OMT-OMT_SCOPE-001"]["harmonization_source_file"]
        == "hla1516_2_omt_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.2-OMT-OMT_CONFORMANCE_VERIFICATION-024"][
            "harmonization_status"
        ]
        == "mapped"
    )
    assert (
        by_id["HLA1516.2-OMT-OMT_SERVICE_UTILIZATION-025"][
            "harmonization_status"
        ]
        == "mapped"
    )
    assert (
        by_id["HLA1516.2-OMT-OMT_CONFORMANCE_LABELS-023"][
            "harmonization_status"
        ]
        == "mapped"
    )
    assert by_id["HLA1516.2-NORMALIZATION-030"]["harmonization_status"] == "partial"
    assert (
        by_id["HLA1516.2-NORMALIZATION-030"]["harmonization_source_file"]
        == "hla1516_2_omt_detailed_reconciliation.csv"
    )
    assert (
        by_id["HLA1516.2-OMT-OMT_NORM_NORMALIZATION-027"]["harmonization_status"]
        == "partial"
    )
    assert by_id["HLA1516.2-MERGE-PRINCIPLES-031"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.2-OMT-OMT_NORM_MERGING_PRINCIPLES-028"]["harmonization_status"]
        == "mapped"
    )
    assert by_id["HLA1516.1-CONF_FEDERATE-014"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-CONF_FEDERATE-014"]["harmonization_source_file"]
        == "hla1516_1_conf_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-CONF_RTI-015"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.2-XML-DIF-032"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.2-XML-DIF-032"]["harmonization_source_file"]
        == "hla1516_xml_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.2-XML-ELEM-001"]["harmonization_status"] == "partial"
    assert by_id["HLA1516.1-MOM-OVERVIEW-014"]["harmonization_status"] == "mapped"
    assert (
        by_id["HLA1516.1-MOM-OVERVIEW-014"]["harmonization_source_file"]
        == "hla1516_1_mom_detailed_reconciliation.csv"
    )
    assert by_id["HLA1516.1-MIM-PARAM-001"]["harmonization_status"] == "mapped"
    assert by_id["HLA1516.1-FM-4_3-RTIAPI-001-MOM"]["harmonization_status"] == "mapped"
