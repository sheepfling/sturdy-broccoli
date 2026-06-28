from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_framework_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/framework_bounded_family.md"
FRONT_DOOR_DOC = ROOT / "docs/requirements/ieee-1516-2010/README.md"
SOURCE_README = ROOT / "requirements/2010/README.md"
HIERARCHY_DOC = ROOT / "docs/verification/requirements_hierarchy.md"


def test_framework_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]
    kind_counts = Counter(row["reconciliation_kind"] for row in partial_rows)

    assert len(rows) == 53
    assert Counter(row["current_status"] for row in rows) == {
        "partial": 41,
        "mapped": 12,
    }
    assert kind_counts == {"DET": 21, "FW_RULE_DETAIL": 12, "partial": 8}


def test_framework_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Framework Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "canonical final reading for the current `CAP-FW`" in text
    assert "`53` framework packet rows" in text
    assert "`12 mapped`" in text
    assert "`41 partial`" in text
    assert "`12 FW_RULE_DETAIL`" in text
    assert "`21 DET`" in text
    assert "`8 partial`" in text
    assert "`requirements/2010/hla1516_framework_detailed_reconciliation.csv`" in text
    assert "`requirements/2010/traceability_matrix.csv`" in text
    assert "`requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`" in text
    assert "`docs/verification/requirement_compliance_exports.md`" in text
    assert "`tests/verification/test_framework_rule_docs_v1_0.py`" in text
    assert "`tests/backends/test_python_backend_object_ownership_extended.py`" in text
    assert "`tests/backends/test_python_backend_time_ddm_extended.py`" in text
    assert "`tests/factories/test_fom_omt_parsing.py`" in text
    assert "../../plans/requirements_gap_register.md" not in text


def test_framework_owner_surfaces_are_linked_from_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")
    hierarchy = HIERARCHY_DOC.read_text(encoding="utf-8")

    assert "framework bounded-family note" in front_door
    assert "framework bounded-family reading" in front_door
    assert "framework bounded-family note" in source_readme
    assert "framework bounded-family reading" in hierarchy
    assert "time-management closeout reading" in front_door
    assert "time-management closeout reading" in source_readme
    assert "time-management closeout reading" in hierarchy


def test_framework_partial_rows_anchor_to_expected_evidence_clusters() -> None:
    rows = {
        row["packet_requirement_id"]: row
        for row in csv.DictReader(LEDGER.open(newline="", encoding="utf-8"))
    }

    assert rows["HLA1516-FW-FW_SCOPE-001"]["current_status"] == "partial"
    assert "framework boundary and product-set scope" in rows["HLA1516-FW-FW_SCOPE-001"]["notes"]
    assert "test_framework_docs_capture_product_set_scope_and_source_policy" in rows["HLA1516-FW-FW_SCOPE-001"]["current_test_id"]

    assert rows["HLA1516-FW-5_2-DET-001"]["current_status"] == "partial"
    assert "RTI-owned management state" in rows["HLA1516-FW-5_2-DET-001"]["notes"]
    assert "test_python_rti_query_attribute_ownership_reports_rti_for_mom_owned_attribute" in rows["HLA1516-FW-5_2-DET-001"]["current_test_id"]

    assert rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["current_status"] == "partial"
    assert "RTI-mediated exchange is directly exercised" in rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["notes"]
    assert "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions" in rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["current_test_id"]

    assert rows["HLA1516-FW-RULE_6_SOM-010"]["current_status"] == "partial"
    assert "SOM parsing evidence" in rows["HLA1516-FW-RULE_6_SOM-010"]["notes"]
    assert "test_parse_fom_xml_recognizes_standard_omt_component_tables_across_fom_som_and_mim" in rows["HLA1516-FW-RULE_6_SOM-010"]["current_test_id"]
