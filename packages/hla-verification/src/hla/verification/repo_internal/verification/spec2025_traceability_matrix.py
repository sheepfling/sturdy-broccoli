"""Derived traceability artifact for 2025 packet rows and umbrella mappings."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from hla.verification.repo_internal.spec2025_finish_line import (
    IMPLEMENTED_EVIDENCE_SLICES,
    build_spec2025_finish_line_snapshot,
)


TRACEABILITY_ARTIFACT_REL = "docs/evidence/spec2025/traceability_matrix.json"
HARMONIZATION_LEDGER_REL = "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"
EXECUTABLE_PACKET_REL = (
    "docs/requirements/ieee-1516-2025/executable_tests/hla_2025_executable_test_requirements_v3.csv"
)
TRACEABILITY_PYTEST_PREFIX = "tests/requirements/test_2025_traceability.py::"


def _read_harmonization_rows(project_root: Path) -> list[dict[str, str]]:
    ledger_path = project_root / HARMONIZATION_LEDGER_REL
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _read_traceability_packet_rows(project_root: Path) -> list[dict[str, str]]:
    packet_path = project_root / EXECUTABLE_PACKET_REL
    with packet_path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: value or "" for key, value in row.items()}
            for row in csv.DictReader(handle)
            if (value := row.get("pytest_candidate", "") or "").startswith(TRACEABILITY_PYTEST_PREFIX)
        ]


def _requirement_evidence_index() -> dict[str, list[str]]:
    evidence_by_requirement: dict[str, list[str]] = {}
    for slice_row in IMPLEMENTED_EVIDENCE_SLICES:
        evidence = [
            str(path)
            for path in slice_row.get("evidence", ())
            if "tests/requirements/test_2025_finish_line_snapshot.py" not in str(path)
        ]
        for requirement_id in slice_row.get("requirements", ()):
            bucket = evidence_by_requirement.setdefault(str(requirement_id), [])
            for anchor in evidence:
                if anchor not in bucket:
                    bucket.append(anchor)
    return evidence_by_requirement


def build_spec2025_traceability_matrix(project_root: Path) -> dict[str, Any]:
    snapshot = build_spec2025_finish_line_snapshot(project_root)
    duplicate_audit = snapshot["duplicate_umbrella_mapping_audit"]
    harmonization_rows = _read_harmonization_rows(project_root)
    traceability_packet_rows = _read_traceability_packet_rows(project_root)
    evidence_by_requirement = _requirement_evidence_index()
    row_by_id = {str(row["id"]): row for row in harmonization_rows}
    umbrella_child_links = {
        **duplicate_audit["framework_child_links"],
        **duplicate_audit["delta_child_links"],
    }
    owner_doc_by_requirement = {
        **{
            requirement_id: str(duplicate_audit["framework_doc_path"])
            for requirement_id in duplicate_audit["framework_child_links"]
        },
        **{
            requirement_id: str(duplicate_audit["delta_doc_path"])
            for requirement_id in duplicate_audit["delta_child_links"]
        },
    }

    rows: list[dict[str, Any]] = []
    emitted_requirement_ids: set[str] = set()
    for packet_row in traceability_packet_rows:
        requirement_id = packet_row["parent_requirement_id"]
        child_ids = list(umbrella_child_links.get(requirement_id, ()))
        direct_evidence_anchors = list(evidence_by_requirement.get(requirement_id, ()))
        inherited_evidence_anchors: list[str] = []
        for child_id in child_ids:
            for anchor in evidence_by_requirement.get(child_id, ()):
                if anchor not in inherited_evidence_anchors:
                    inherited_evidence_anchors.append(anchor)
        evidence_anchors = list(direct_evidence_anchors)
        for anchor in inherited_evidence_anchors:
            if anchor not in evidence_anchors:
                evidence_anchors.append(anchor)
        harmonization_row = row_by_id.get(requirement_id)
        rows.append(
            {
                "requirement_id": requirement_id,
                "executable_test_id": packet_row["executable_test_id"],
                "pytest_candidate": packet_row["pytest_candidate"],
                "implementation_target": packet_row["implementation_target"],
                "requirement_summary": packet_row["requirement_summary"],
                "expected_result_from_extraction": packet_row["expected_result_from_extraction"],
                "expected_status": packet_row["expected_status"],
                "traceability_basis": (
                    "duplicate-umbrella-child-evidence"
                    if child_ids
                    else "direct-requirement-evidence"
                    if direct_evidence_anchors
                    else "packet-only-no-direct-anchor"
                ),
                "harmonization_disposition": (
                    harmonization_row["harmonization_disposition"] if harmonization_row else "packet-only"
                ),
                "row_role": harmonization_row["row_role"] if harmonization_row else "packet-traceability",
                "owner_doc": owner_doc_by_requirement.get(requirement_id, ""),
                "child_requirement_ids": child_ids,
                "child_dispositions": {
                    child_id: row_by_id[child_id]["harmonization_disposition"]
                    for child_id in child_ids
                    if child_id in row_by_id
                },
                "direct_evidence_anchors": direct_evidence_anchors,
                "inherited_evidence_anchors": inherited_evidence_anchors,
                "evidence_anchors": evidence_anchors,
            }
        )
        emitted_requirement_ids.add(requirement_id)

    for requirement_id, child_ids in sorted(umbrella_child_links.items()):
        if requirement_id in emitted_requirement_ids:
            continue
        inherited_evidence_anchors: list[str] = []
        for child_id in child_ids:
            for anchor in evidence_by_requirement.get(child_id, ()):
                if anchor not in inherited_evidence_anchors:
                    inherited_evidence_anchors.append(anchor)
        harmonization_row = row_by_id[requirement_id]
        rows.append(
            {
                "requirement_id": requirement_id,
                "executable_test_id": "",
                "pytest_candidate": "",
                "implementation_target": "",
                "requirement_summary": "",
                "expected_result_from_extraction": "",
                "expected_status": "",
                "traceability_basis": "duplicate-umbrella-child-evidence",
                "harmonization_disposition": harmonization_row["harmonization_disposition"],
                "row_role": harmonization_row["row_role"],
                "owner_doc": owner_doc_by_requirement.get(requirement_id, ""),
                "child_requirement_ids": child_ids,
                "child_dispositions": {
                    child_id: row_by_id[child_id]["harmonization_disposition"]
                    for child_id in child_ids
                    if child_id in row_by_id
                },
                "direct_evidence_anchors": [],
                "inherited_evidence_anchors": inherited_evidence_anchors,
                "evidence_anchors": inherited_evidence_anchors,
            }
        )

    return {
        "artifact": "spec2025-traceability-matrix",
        "scope": (
            "2025 executable packet traceability rows mapped to direct evidence anchors, "
            "or to explicit umbrella child evidence / packet-only no-direct-anchor states"
        ),
        "row_count": len(rows),
        "rows": rows,
    }


def write_spec2025_traceability_matrix(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / TRACEABILITY_ARTIFACT_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_spec2025_traceability_matrix(project_root)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


__all__ = [
    "TRACEABILITY_ARTIFACT_REL",
    "build_spec2025_traceability_matrix",
    "write_spec2025_traceability_matrix",
]
