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


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _assert_contains_all(text: str, snippets: list[str]) -> None:
    for snippet in snippets:
        assert snippet in text


def test_xml_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(XML_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]
    kind_counts = Counter(row["reconciliation_kind"] for row in partial_rows)

    assert len(partial_rows) <= 364
    assert set(kind_counts) <= {"XML_ELEM", "XML_TYPE", "CLAUSE12_13_DETAIL"}
    assert kind_counts["XML_ELEM"] > 0
    assert kind_counts["XML_TYPE"] > 0
    assert kind_counts["CLAUSE12_13_DETAIL"] <= 1


def test_omt_owner_ledger_is_fully_mapped_after_common_annex_b_support() -> None:
    rows = list(csv.DictReader(OMT_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 0
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 60})


def test_omt_xml_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    _assert_contains_all(
        text,
        [
            "2010 OMT/XML Bounded Family",
            "`364 partial`",
            "`274 XML_ELEM`",
            "`89 XML_TYPE`",
            "`1 CLAUSE12_13_DETAIL`",
            "`60 mapped`",
            "`0 partial`",
            "`requirements/2010/hla1516_xml_detailed_reconciliation.csv`",
            "`requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`",
            "`requirements/2010/hla1516_2_omt_xml_detailed_reconciliation.csv`",
            "`requirements/2010/traceability_matrix.csv`",
            "`docs/verification/requirement_compliance_exports.md`",
            "`assess_omt_conformance`",
            "linear (...)` and `linearEnumerated (...)",
            "Normalize Federate Handle service",
            "Normalize Service Group service",
        ],
    )
    assert "../../plans/requirements_gap_register.md" not in text


def test_omt_and_xml_owner_surfaces_are_split_in_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")
    hierarchy = HIERARCHY_DOC.read_text(encoding="utf-8")

    for text in (front_door, source_readme, hierarchy):
        assert "OMT family" in text
        assert "legacy OMT/XML bridge artifact" in text
        assert "XML family" in text

    assert "hla1516_2_omt_detailed_reconciliation.csv" in front_door
    assert "hla1516_xml_detailed_reconciliation.csv" in front_door
    assert "hla1516_2_omt_xml_detailed_reconciliation.csv" in front_door
    assert "former Annex B normalization tail is now also `mapped`" in (ROOT / "requirements/README.md").read_text(encoding="utf-8")


def test_2010_front_door_calls_out_basic_execution_rules_and_anchors() -> None:
    text = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        text,
        [
            "## Basic Execution Rules",
            'canonical 2010 "have we joined yet?" rule family',
            "hla1516_1_clause_4_fm_service_decomposition.csv",
            "hla1516_1_fm_detailed_reconciliation.csv",
            "federation_management_bounded_family.md",
            "../execution_membership_rules.md",
            "object_management_bounded_family.md",
            "data_distribution_management_bounded_family.md",
            "`HLA1516.1-FM-4_2-RTIAPI-001-EXC`",
            "`HLA1516.1-FM-4_6-RTIAPI-001-EXC`",
            "`HLA1516.1-FM-4_9-RTIAPI-001-EXC`",
            "`HLA1516.1-FM-4_10-RTIAPI-001-EXC`",
            "`HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`",
            "`HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001`",
            "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001`",
            "`HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`",
            "`HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`",
            "`HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`",
            "`HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`",
            "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001`",
            "`HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001`",
            "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001`",
            "`HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001`",
            "`NotConnected`",
            "`FederateNotExecutionMember`",
            "`FederatesCurrentlyJoined`",
            "`FederationExecutionDoesNotExist`",
            "The intended 2010 state-machine reading is:",
            "tests/backends/test_python_backend_federation_extended.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py",
            "tests/scenarios/test_federation_management_backend_matrix.py",
            "./tools/test-focus run execution-membership",
        ],
    )
    _assert_contains_all(
        normalized,
        [
            "connect before RTI interaction",
            "joined versus not-joined execution-member guards",
            "resign before disconnect",
            "destroy rejected while federates are still joined",
            "federation membership listing and reporting",
            "delete, local-delete, update, interaction, query, and region-gated DDM services rejected until the caller has joined",
            "after resign, those execution-affecting services continue to reject the caller as no longer joined",
            "later destroy or join attempts against that missing federation reject with `FederationExecutionDoesNotExist`",
        ],
    )


def test_2010_object_management_bounded_family_calls_out_execution_member_guards() -> None:
    text = (
        ROOT / "docs/requirements/ieee-1516-2010/object_management_bounded_family.md"
    ).read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        text,
        [
            "Execution-membership reading for this family:",
            "`HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`",
            "`HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001`",
            "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore",
            "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore",
            "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore",
            "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
            "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore",
        ],
    )
    _assert_contains_all(
        normalized,
        [
            "after a federate resigns, before it joins, or after it disconnects",
            "object and interaction services are expected to reject the caller as not connected or not joined",
            "not just federation-management services",
            "basic delete, local-delete, update, send, request, and transportation-query paths",
        ],
    )
