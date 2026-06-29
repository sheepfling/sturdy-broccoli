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
RECONCILIATION_REL = "requirements/2010/hla1516_xml_detailed_reconciliation.csv"
OWNER_DOC = "docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md"


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


def test_xml_detailed_reconciliation_has_expected_shape():
    rows = _typed_rows()

    assert len(rows) == 367
    assert Counter(row.current_status for row in rows) == Counter({"partial": 364, "mapped": 3})
    assert Counter((row.mapping_kind, row.current_status) for row in rows) == Counter(
        {
            ("XML_ELEM", "partial"): 274,
            ("XML_TYPE", "partial"): 89,
            ("CLAUSE12_13_DETAIL", "partial"): 1,
            ("XML_DIF", "mapped"): 1,
            ("OMT_CLAUSE_DETAIL", "mapped"): 1,
            ("XML_SCHEMA", "mapped"): 1,
        }
    )
    assert {row.source_packet_file for row in rows} == {"hla_1516_requirements_master_v1_0.csv"}


def test_xml_detailed_reconciliation_spot_checks_key_rows():
    rows = _typed_rows_by_id()

    assert rows["HLA1516.2-XML-DIF-032"].current_status == "mapped"
    assert rows["HLA1516.2-XML-SCHEMA-033"].current_status == "mapped"
    assert rows["HLA1516.2-OMT-OMT_XSD-030"].current_status == "mapped"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"].current_status == "partial"
    assert rows["HLA1516.2-XML-ELEM-001"].current_status == "partial"
    assert rows["HLA1516.2-XML-TYPE-001"].current_status == "partial"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"].mapping_notes.startswith(
        "Canonical residual disposition:"
    )
    assert "broader IEEE 1516.1 normative-source claim remains intentionally partial" in rows[
        "HLA1516.1-FDD_XSD_NORMATIVE-019"
    ].mapping_notes
    assert "atom-level XML element row remains intentionally partial" in rows[
        "HLA1516.2-XML-ELEM-001"
    ].mapping_notes
    assert "atom-level XML type row remains intentionally partial" in rows[
        "HLA1516.2-XML-TYPE-001"
    ].mapping_notes


def test_xml_detailed_reconciliation_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[RECONCILIATION_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_xml_partial_rows_carry_explicit_canonical_residual_dispositions() -> None:
    for row in _typed_rows():
        if row.current_status != "partial":
            continue
        assert row.mapping_notes.startswith("Canonical residual disposition:"), row.source_requirement_id


def test_xml_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_typed_truth_source_rows())
