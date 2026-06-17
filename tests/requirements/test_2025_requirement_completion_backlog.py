from __future__ import annotations

import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "requirements/2025/requirement_completion_backlog.csv"

REQUIRED_BUCKETS = {
    "carry-forward-cleanup",
    "modified-existing",
    "new-2025-requirements",
    "retired-mapped-2010",
    "binding-specific",
    "verification-matrix",
}

MODIFIED_EXISTING_AREAS = {
    "Connect authentication and configuration",
    "Create and join federation FOM handling",
    "FOM and MIM module loading",
    "Callback context parameters",
    "Ownership user tags and set callbacks",
    "Time management and flush queue grant",
    "DDM dimension lookup",
    "Switch inquiry and control model",
    "Exception delta pass",
    "XML logical time naming",
}

NEW_2025_AREAS = {
    "Directed interactions",
    "Federation execution member discovery",
    "Federate resigned callback",
    "Default attribute policy changes",
    "Handle normalization",
    "OMT reference data types and valueRequired",
    "MOM service reporting changes",
}

RETIRE_OR_MAP_AREAS = {
    "Advisory switch enable disable services",
    "Supplemental callback info helpers",
    "2010 WSDL",
}

BINDING_SCOPES = {"java", "cpp", "fedpro"}

HIGH_PRIORITIES = {"high", "very-high"}


def _rows() -> list[dict[str, str]]:
    with BACKLOG.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_2025_completion_backlog_is_canonical_and_human_editable() -> None:
    rows = _rows()
    assert rows
    assert {row["bucket"] for row in rows} == REQUIRED_BUCKETS
    assert len({row["id"] for row in rows}) == len(rows)


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_modified_existing_sections_are_explicitly_dispositioned() -> None:
    rows = [row for row in _rows() if row["bucket"] == "modified-existing"]
    assert {row["area"] for row in rows} == MODIFIED_EXISTING_AREAS
    assert {row["priority"] for row in rows} <= HIGH_PRIORITIES
    assert all(row["disposition"] in {"modify", "modify-add", "retire-replace"} for row in rows)


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_new_2025_surfaces_are_queued_as_full_requirement_work() -> None:
    rows = [row for row in _rows() if row["bucket"] == "new-2025-requirements"]
    assert {row["area"] for row in rows} == NEW_2025_AREAS
    assert all(row["disposition"] == "add" for row in rows)
    assert all(row["source_2010"] in {"none", "2010 MOM service reporting assumptions"} for row in rows)


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_retired_and_binding_specific_work_stays_separate() -> None:
    rows = _rows()
    retired = [row for row in rows if row["bucket"] == "retired-mapped-2010"]
    bindings = [row for row in rows if row["bucket"] == "binding-specific"]
    assert {row["area"] for row in retired} == RETIRE_OR_MAP_AREAS
    assert {row["binding_scope"] for row in bindings} == BINDING_SCOPES
    assert all(row["bucket"] != "binding-specific" for row in retired)


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_high_priority_rows_have_acceptance_and_verification_work() -> None:
    rows = [row for row in _rows() if row["priority"] in HIGH_PRIORITIES]
    assert rows
    missing = [
        row["id"]
        for row in rows
        if not row["acceptance_criteria"] or not row["verification_work"] or not row["differential_query"]
    ]
    assert not missing


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_native_2025_work_does_not_hide_legacy_terms_outside_source_fields() -> None:
    stale_terms = ("hla.rti1516e", "rti1516e::", "hla1516e.wsdl")
    checked_columns = (
        "target_2025",
        "requirement_work",
        "acceptance_criteria",
        "verification_work",
        "binding_scope",
    )
    violations: list[str] = []
    for row in _rows():
        if row["bucket"] == "retired-mapped-2010":
            continue
        text = " ".join(row[column] for column in checked_columns)
        for term in stale_terms:
            if term in text:
                violations.append(f"{row['id']}: {term}")
    assert not violations
