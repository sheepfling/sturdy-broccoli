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
RECONCILIATION_REL = "requirements/2010/hla1516_1_sup_detailed_reconciliation.csv"
OWNER_DOC = "docs/requirements/ieee-1516-2010/support_services_bounded_family.md"


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
        assert test_name in text, f"missing test anchor for {reference}"
        return

    path = ROOT / reference
    assert path.exists(), f"missing evidence artifact {reference}"


def test_sup_detailed_reconciliation_has_expected_shape():
    rows = _typed_rows()

    assert len(rows) == 603
    assert Counter(row.current_status for row in rows) == Counter({"mapped": 603})
    assert Counter((row.mapping_kind, row.current_status) for row in rows) == Counter(
        {
            ("SIG", "mapped"): 86,
            ("SVC", "mapped"): 82,
            ("EFF", "mapped"): 55,
            ("ARG", "mapped"): 43,
            ("EXC", "mapped"): 43,
            ("MOM", "mapped"): 43,
            ("PRE", "mapped"): 43,
            ("TEST", "mapped"): 43,
            ("RTI_API", "mapped"): 43,
            ("EXC_API", "mapped"): 43,
            ("MOM_TRACE", "mapped"): 43,
            ("RET", "mapped"): 31,
            ("CB", "mapped"): 4,
            ("OVW", "mapped"): 1,
        }
    )
    assert {row.source_packet_file for row in rows} == {"hla_1516_requirements_master_v1_0.csv"}


def test_sup_detailed_reconciliation_spot_checks_key_rows():
    rows = _typed_rows_by_id()

    assert rows["HLA1516.1-SUP-OVERVIEW-013"].current_status == "mapped"
    assert rows["HLA1516.1-SUP-10_2-001"].current_status == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001"].current_status == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-EXC"].current_status == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-MOM"].current_status == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-RET"].current_status == "mapped"
    assert "full applicable precondition surface the Python RTI exposes" in rows[
        "HLA1516.1-SUP-10_6-GETOBJECTCLASSHANDLE-PRE-001"
    ].mapping_notes
    assert "service-specific validation or state guards" in rows[
        "HLA1516.1-SUP-10_6-GETOBJECTCLASSHANDLE-PRE-001"
    ].mapping_notes
    assert "service-specific validation, membership, and connection guard surface" in rows[
        "HLA1516.1-SUP-10_13-GETUPDATERATEVALUE-EXC-001"
    ].mapping_notes
    assert "directly exercised `evokeCallback` guard surface" in rows[
        "HLA1516.1-SUP-10_41-RTIAPI-001-EXC"
    ].mapping_notes
    assert "within-callback rejection" in rows[
        "HLA1516.1-SUP-10_41-RTIAPI-001-EXC"
    ].mapping_notes


def test_sup_handles_overview_row_has_direct_lookup_and_factory_evidence():
    row = _typed_rows_by_id()["HLA1516.1-SUP-OVERVIEW-013"]

    assert row.current_status == "mapped"
    assert row.evidence_refs == (
        "tests/backends/test_python_backend_support_services.py::test_support_lookups_round_trip_class_handle_and_name",
        "tests/backends/test_python_backend_support_services.py::test_support_dimension_and_update_rate_helpers",
        "tests/backends/test_python_backend_support_services.py::test_support_normalizers_and_factories",
        "tests/backends/test_python_backend_support_services.py::test_support_invalid_inputs_raise_expected_errors",
    )
    assert "stable" in row.mapping_notes.lower()
    assert "round trips" in row.mapping_notes.lower()


def test_sup_detailed_reconciliation_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[RECONCILIATION_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_sup_partial_rows_use_explicit_bounded_envelope_notes() -> None:
    partial_rows = [row for row in _typed_rows() if row.current_status == "partial"]
    assert partial_rows == []


def test_sup_rows_anchor_to_live_evidence_refs() -> None:
    for requirement_id, typed_row in _typed_rows_by_id().items():
        references = list(typed_row.evidence_refs)
        assert references, f"{requirement_id} should carry evidence references"
        for reference in references:
            _assert_reference_is_live(reference)


def test_sup_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_typed_truth_source_rows())
