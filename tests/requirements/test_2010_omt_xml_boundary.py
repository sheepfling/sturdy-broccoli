from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
XML_LEDGER = ROOT / "requirements/2010/hla1516_xml_detailed_reconciliation.csv"
OMT_LEDGER = ROOT / "requirements/2010/hla1516_2_omt_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md"
FRONT_DOOR_DOC = ROOT / "docs/requirements/ieee-1516-2010/README.md"
SOURCE_README = ROOT / "requirements/2010/README.md"
HIERARCHY_DOC = ROOT / "docs/verification/requirements_hierarchy.md"


def test_xml_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(XML_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 364
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "XML_ELEM": 274,
        "XML_TYPE": 89,
        "CLAUSE12_13_DETAIL": 1,
    }


def test_omt_partial_tail_is_only_annex_b_normalization() -> None:
    rows = list(csv.DictReader(OMT_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 2
    assert Counter(row["implementation_area"] for row in partial_rows) == {
        "omt.normalization": 1,
        "ddm/normalization": 1,
    }


def test_omt_xml_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 OMT/XML Bounded Family" in text
    assert "`364 partial`" in text
    assert "`274 XML_ELEM`" in text
    assert "`89 XML_TYPE`" in text
    assert "`1 CLAUSE12_13_DETAIL`" in text
    assert "`58 mapped`" in text
    assert "`2 partial`" in text
    assert "`assess_omt_conformance`" in text
    assert "non-identity normalization as only partially conforming" in text


def test_omt_and_xml_owner_surfaces_are_split_in_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")
    hierarchy = HIERARCHY_DOC.read_text(encoding="utf-8")

    for text in (front_door, source_readme, hierarchy):
        assert "OMT family" in text
        assert "OMT clause-detail and OMT/XML bridge" in text
        assert "XML family" in text

    assert "hla1516_2_omt_detailed_reconciliation.csv" in front_door
    assert "hla1516_2_omt_xml_detailed_reconciliation.csv" in front_door
    assert "hla1516_xml_detailed_reconciliation.csv" in front_door
    assert "bounded `partial` rows" in (ROOT / "requirements/README.md").read_text(encoding="utf-8")


def test_2010_front_door_calls_out_basic_execution_rules_and_anchors() -> None:
    text = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Basic Execution Rules" in text
    assert 'canonical 2010 "have we joined yet?" rule family' in text
    assert "connect before RTI interaction" in normalized
    assert "joined versus not-joined execution-member guards" in normalized
    assert "delete, local-delete, update, interaction, query, and region-gated DDM services rejected until the caller has joined" in normalized
    assert "after resign, those execution-affecting services continue to reject the caller as no longer joined, including delete/local-delete plus the region-gated DDM send and request-update variants" in normalized
    assert "resign before disconnect" in normalized
    assert "destroy rejected while federates are still joined" in normalized
    assert "after destroy succeeds, later destroy or join attempts against that missing federation reject with `FederationExecutionDoesNotExist`" in normalized
    assert "federation membership listing and reporting" in normalized
    assert "hla1516_1_clause_4_fm_service_decomposition.csv" in text
    assert "hla1516_1_fm_detailed_reconciliation.csv" in text
    assert "federation_management_bounded_family.md" in text
    assert "../execution_membership_rules.md" in text
    assert "object_management_bounded_family.md" in text
    assert "data_distribution_management_bounded_family.md" in text
    assert "`HLA1516.1-FM-4_2-RTIAPI-001-EXC`" in text
    assert "`HLA1516.1-FM-4_6-RTIAPI-001-EXC`" in text
    assert "`HLA1516.1-FM-4_9-RTIAPI-001-EXC`" in text
    assert "`HLA1516.1-FM-4_10-RTIAPI-001-EXC`" in text
    assert "`HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001`" in text
    assert "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`" in text
    assert "`HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`" in text
    assert "`HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`" in text
    assert "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001`" in text
    assert "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001`" in text
    assert "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001`" in text
    assert "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001`" in text
    assert "`NotConnected`" in text
    assert "`FederateNotExecutionMember`" in text
    assert "`FederatesCurrentlyJoined`" in text
    assert "`FederationExecutionDoesNotExist`" in text
    assert "The intended 2010 state-machine reading is:" in text
    assert "tests/backends/test_python_backend_federation_extended.py" in text
    assert "tests/backends/test_python_backend_object_ownership_extended.py" in text
    assert "tests/backends/test_python_backend_time_ddm_extended.py" in text
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py" in text
    assert "tests/scenarios/test_federation_management_backend_matrix.py" in text
    assert "./tools/test-focus run execution-membership" in text


def test_2010_object_management_bounded_family_calls_out_execution_member_guards() -> None:
    text = (
        ROOT / "docs/requirements/ieee-1516-2010/object_management_bounded_family.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Execution-membership reading for this family:" in text
    assert "after a federate resigns, before it joins, or after it disconnects" in normalized
    assert "object and interaction services are expected to reject the caller as not connected or not joined" in normalized
    assert "not just federation-management services" in normalized
    assert "basic delete, local-delete, update, send, request, and transportation-query paths" in normalized
    assert "`HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`" in text
    assert "`HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001`" in text
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in text
    assert "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore" in text
    assert "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text


def test_2010_front_door_links_honest_closeout_program_surfaces() -> None:
    text = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Honest 100 Percent Reading" in text
    assert "no longer contains any hidden `planned` inventory" in normalized
    assert "maintained bounded-family, mixed-backend, or explicitly aggregated OMT/XML boundary surfaces" in normalized
    assert "PLN-004_python_rti_100_percent_compliance_plan.md" in text
    assert "2010_python_rti_bounded_family_execution_worklist.md" in text
    assert "requirements_completion_audit.md" in text
