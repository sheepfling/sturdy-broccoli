from __future__ import annotations

from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import (
    load_2010_reconciliation_rows,
    survey_requirement_artifacts,
)

try:
    from reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources
except ModuleNotFoundError:
    from tests.reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources

ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_REL = "requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv"
OWNER_DOC = "docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md"


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(ROOT, RECONCILIATION_REL, OWNER_DOC)
    }


def _typed_rows() -> list[object]:
    return list(_typed_rows_by_id().values())


def _typed_truth_source_rows() -> list[dict[str, str]]:
    return [
        {
            "packet_requirement_id": row.source_requirement_id,
            "current_test_id": ";".join(row.evidence_refs),
        }
        for row in _typed_rows()
    ]


def _assert_reference_is_live(reference: str) -> None:
    if "::" in reference:
        file_part, test_name = reference.split("::", 1)
        path = ROOT / file_part
        assert path.exists(), f"missing evidence file for {reference}"
        text = path.read_text(encoding="utf-8")
        base_name = test_name.split("[", 1)[0]
        assert (test_name in text or base_name in text), f"missing test anchor for {reference}"
        return

    path = ROOT / reference
    if path.exists():
        return

    matches: list[str] = []
    for candidate in (ROOT / "tests").rglob("*.py"):
        if f"def {reference}(" in candidate.read_text(encoding="utf-8"):
            matches.append(str(candidate.relative_to(ROOT)))
    assert matches, f"unresolved bare evidence ref {reference}"
    assert len(matches) == 1, f"ambiguous bare evidence ref {reference}: {matches}"


def test_ddm_detailed_reconciliation_has_expected_shape():
    rows = _typed_rows()

    assert len(rows) == 223
    assert Counter(row.current_status for row in rows) == Counter({"mapped": 223})
    assert {row.source_packet_file for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_ddm_detailed_reconciliation_spot_checks_key_rows():
    rows = _typed_rows_by_id()

    assert rows["HLA1516.1-DDM-OVERVIEW-012"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-OVERVIEW-012"].mapping_kind == "OVW"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"].mapping_kind == "RTI_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"].mapping_kind == "EXC_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"].mapping_kind == "MOM_TRACE"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"].mapping_kind == "RET"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"].mapping_kind == "SIG"
    assert rows["HLA1516.1-DDM-9_5-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_5-001"].mapping_kind == "SVC"
    assert rows["HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-EXC-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_5-RTIAPI-001-EXC"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_8-RTIAPI-001-EXC"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"].mapping_kind == "TEST"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"].current_status == "mapped"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"].mapping_kind == "RET"


def test_ddm_detailed_reconciliation_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[RECONCILIATION_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_ddm_region_lifecycle_exception_rows_are_now_directly_mapped() -> None:
    rows = _typed_rows_by_id()

    expected = {
        "HLA1516.1-DDM-9_2-CREATEREGION-EXC-001": "invalid-dimension",
        "HLA1516.1-DDM-9_2-RTIAPI-001-EXC": "invalid-dimension",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-EXC-001": "foreign-region ownership",
        "HLA1516.1-DDM-9_3-RTIAPI-001-EXC": "foreign-region ownership",
        "HLA1516.1-DDM-9_4-DELETEREGION-EXC-001": "region-in-use",
        "HLA1516.1-DDM-9_4-RTIAPI-001-EXC": "region-in-use",
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-EXC-001": "invalid-region-context",
        "HLA1516.1-DDM-9_6-RTIAPI-001-EXC": "invalid-region-context",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-EXC-001": "object-knownness",
        "HLA1516.1-DDM-9_7-RTIAPI-001-EXC": "object-knownness",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-EXC-001": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-RTIAPI-001-EXC": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-RTIAPI-001-EXC-DUP02": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001": "interaction-class-not-defined",
        "HLA1516.1-DDM-9_11-RTIAPI-001-EXC": "interaction-class-not-defined",
    }

    for requirement_id, phrase in expected.items():
        row = rows[requirement_id]
        assert row.current_status == "mapped"
        assert phrase in row.mapping_notes


def test_ddm_execution_membership_pre_promotions_are_recorded() -> None:
    rows = _typed_rows_by_id()

    send_row = rows["HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001"]
    update_row = rows["HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001"]

    assert send_row.current_status == "mapped"
    assert (
        "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in send_row.evidence_refs[0]
        or "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in ";".join(send_row.evidence_refs)
    )
    assert "publication-state" in send_row.mapping_notes
    assert "invalid-logical-time" in send_row.mapping_notes

    assert update_row.current_status == "mapped"
    assert (
        "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore"
        in ";".join(update_row.evidence_refs)
    )
    assert "class-handle and attribute-definition validation" in update_row.mapping_notes
    assert "invalid-region" in update_row.mapping_notes


def test_ddm_subscription_and_region_association_pre_promotions_are_recorded() -> None:
    rows = _typed_rows_by_id()

    promoted = {
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "attribute-definition validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }

    for requirement_id, phrase in promoted.items():
        row = rows[requirement_id]
        assert row.current_status == "mapped"
        assert "applicable precondition surface" in row.mapping_notes
        assert phrase in row.mapping_notes


def test_ddm_register_object_instance_with_regions_pre_promotion_is_recorded() -> None:
    rows = _typed_rows_by_id()
    row = rows["HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-PRE-001"]

    assert row.current_status == "mapped"
    assert (
        "test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region"
        in ";".join(row.evidence_refs)
    )
    assert (
        "test_strict_publication_gates_registration_update_and_interaction_sends"
        in ";".join(row.evidence_refs)
    )
    assert "publication-state" in row.mapping_notes
    assert "duplicate-name" in row.mapping_notes


def test_ddm_create_commit_and_unsubscribe_interaction_pre_promotions_are_recorded() -> None:
    rows = _typed_rows_by_id()

    promoted = {
        "HLA1516.1-DDM-9_2-CREATEREGION-PRE-001": "invalid-dimension",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-PRE-001": "invalid-region",
        "HLA1516.1-DDM-9_4-DELETEREGION-PRE-001": "region-in-use",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
    }
    for requirement_id, phrase in promoted.items():
        row = rows[requirement_id]
        assert row.current_status == "mapped"
        assert "applicable precondition surface" in row.mapping_notes
        assert phrase in row.mapping_notes


def test_ddm_rows_anchor_to_live_evidence_refs() -> None:
    for requirement_id, typed_row in _typed_rows_by_id().items():
        references = list(typed_row.evidence_refs)
        assert references, f"{requirement_id} should carry evidence references"
        for reference in references:
            _assert_reference_is_live(reference)


def test_ddm_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_typed_truth_source_rows())
