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
RECONCILIATION_REL = "requirements/2010/hla1516_1_conf_detailed_reconciliation.csv"
OWNER_DOC = "docs/requirements/ieee-1516-2010/clause13_conformance_closeout.md"


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


def test_conf_detailed_reconciliation_has_expected_shape():
    rows = _typed_rows()

    assert len(rows) == 2
    assert Counter(row.current_status for row in rows) == Counter({"mapped": 2})
    assert {row.source_packet_file for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_conf_detailed_reconciliation_spot_checks():
    rows = _typed_rows_by_id()

    assert rows["HLA1516.1-CONF_FEDERATE-014"].current_status == "mapped"
    assert (
        "tests/verification/test_clause13_conformance_packet.py::test_clause13_conformance_packet_backs_federate_and_rti_claims"
        in rows["HLA1516.1-CONF_FEDERATE-014"].evidence_refs
    )
    assert rows["HLA1516.1-CONF_RTI-015"].current_status == "mapped"
    assert (
        "tests/verification/test_service_conformance_matrix_v013.py::test_service_by_service_conformance_matrix_covers_generated_api_surface"
        in rows["HLA1516.1-CONF_RTI-015"].evidence_refs
    )


def test_conf_detailed_reconciliation_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[RECONCILIATION_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_conf_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_typed_truth_source_rows())
