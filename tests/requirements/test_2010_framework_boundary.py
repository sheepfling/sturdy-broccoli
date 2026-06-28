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
        "partial": 18,
        "mapped": 35,
    }
    assert kind_counts == {"DET": 9, "FW_RULE_DETAIL": 8, "partial": 1}


def test_framework_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 Framework Bounded Family" in text
    assert "## Default Final Stance" in text
    assert "## Exit Condition" in text
    assert "## Residual Row Groups" in text
    assert "### Broad conceptual framework rows" in text
    assert "### Federate-responsibility and semantics-breadth rows" in text
    assert "### SOM-documentation breadth rows" in text
    assert "### Residual Read Rule" in text
    assert "### Residual Exit Rule" in text
    assert "canonical final reading for the current `CAP-FW`" in text
    assert "`53` framework packet rows" in text
    assert "`35 mapped`" in text
    assert "`18 partial`" in text
    assert "`8 FW_RULE_DETAIL`" in text
    assert "`9 DET`" in text
    assert "`1 partial`" in text
    assert "`HLA1516-FW-FW_SCOPE-001`" in text
    assert "`HLA1516-FW-5_4-DET-002`" in text
    assert "`HLA1516-RULE-006`" in text
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

    assert rows["HLA1516-FW-5_2-DET-001"]["current_status"] == "mapped"
    assert "joined federate owner" in rows["HLA1516-FW-5_2-DET-001"]["notes"]
    assert "test_framework_rule_2_runtime_keeps_simulation_state_in_joined_federates_and_mom_state_in_rti" in rows["HLA1516-FW-5_2-DET-001"]["current_test_id"]

    assert rows["HLA1516-RULE-002"]["current_status"] == "mapped"
    assert "joined-federate simulation state" in rows["HLA1516-RULE-002"]["notes"]

    assert rows["HLA1516-FW-5_4-DET-001"]["current_status"] == "mapped"
    assert "standard generated HLA service and callback entry points" in rows["HLA1516-FW-5_4-DET-001"]["notes"]
    assert "test_framework_rule_4_joined_federates_use_standard_hla_interface_surface" in rows["HLA1516-FW-5_4-DET-001"]["current_test_id"]
    assert rows["HLA1516-RULE-004"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_3-DET-001"]["current_status"] == "mapped"
    assert "offer divestiture and acquire object-attribute ownership dynamically" in rows["HLA1516-FW-6_3-DET-001"]["notes"]
    assert rows["HLA1516-RULE-008"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_4-DET-001"]["current_status"] == "mapped"
    assert "vary attribute update conditions by selecting different update-rate designators" in rows["HLA1516-FW-6_4-DET-001"]["notes"]
    assert rows["HLA1516-RULE-009"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_2-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_2-DET-002"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-007"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_5-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-010"]["current_status"] == "mapped"

    assert rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["current_status"] == "mapped"
    assert "RTI services during federation execution" in rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["notes"]
    assert "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions" in rows["HLA1516-FW-RULE_3_RTI_EXCHANGE-007"]["current_test_id"]
    assert rows["HLA1516-FW-5_3-DET-004"]["current_status"] == "partial"
    assert "substantive correctness" in rows["HLA1516-FW-5_3-DET-004"]["requirement_text"]
    assert rows["HLA1516-FW-RULE_8_OWNERSHIP-012"]["current_status"] == "mapped"
    assert "dynamic object-attribute ownership transfer" in rows["HLA1516-FW-RULE_8_OWNERSHIP-012"]["notes"]
    assert rows["HLA1516-FW-RULE_6_SOM-010"]["current_status"] == "partial"
    assert "broader federate-specific SOM ownership claim remains intentionally partial" in rows["HLA1516-FW-RULE_6_SOM-010"]["notes"]
    assert "test_parse_fom_xml_recognizes_standard_omt_component_tables_across_fom_som_and_mim" in rows["HLA1516-FW-RULE_6_SOM-010"]["current_test_id"]
    assert rows["HLA1516-FW-6_2-DET-003"]["current_status"] == "partial"
    assert rows["HLA1516-FW-RULE_7_PUBLISH_SUBSCRIBE-011"]["current_status"] == "partial"
    assert rows["HLA1516-FW-6_5-DET-002"]["current_status"] == "partial"
    assert rows["HLA1516-FW-RULE_10_COMPLIANCE-014"]["current_status"] == "partial"
