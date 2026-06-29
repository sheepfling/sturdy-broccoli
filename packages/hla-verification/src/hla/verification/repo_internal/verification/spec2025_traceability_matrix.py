"""Derived traceability artifact for 2025 packet rows and umbrella mappings."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any

from hla.verification.repo_internal.requirements import load_2025_canonical_requirement_rows

TRACEABILITY_ARTIFACT_REL = "docs/evidence/spec2025/traceability_matrix.json"
EXECUTABLE_PACKET_REL = (
    "docs/requirements/ieee-1516-2025/executable_tests/hla_2025_executable_test_requirements_v3.csv"
)
TRACEABILITY_PYTEST_PREFIX = "tests/requirements/test_2025_traceability.py::"
FRAMEWORK_DOC_REL = "docs/requirements/ieee-1516-2025/framework_rules.md"
DELTA_DOC_REL = "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"

_BACKTICKED_TOKEN = re.compile(r"`([^`]+)`")


def _read_traceability_packet_rows(project_root: Path) -> list[dict[str, str]]:
    packet_path = project_root / EXECUTABLE_PACKET_REL
    with packet_path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: value or "" for key, value in row.items()}
            for row in csv.DictReader(handle)
            if (value := row.get("pytest_candidate", "") or "").startswith(TRACEABILITY_PYTEST_PREFIX)
        ]


def _parse_markdown_tables(doc_text: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    lines = doc_text.splitlines()
    i = 0
    while i < len(lines):
        if "|" not in lines[i]:
            i += 1
            continue
        if i + 1 >= len(lines) or not lines[i + 1].strip().startswith("| ---"):
            i += 1
            continue
        headers = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
        table_rows: list[dict[str, str]] = []
        i += 2
        while i < len(lines) and lines[i].strip().startswith("|"):
            cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
            if len(cells) == len(headers):
                table_rows.append(dict(zip(headers, cells)))
            i += 1
        tables.append(table_rows)
    return tables


def _split_cell_items(cell: str) -> list[str]:
    backticked = [token.strip() for token in _BACKTICKED_TOKEN.findall(cell) if token.strip()]
    if backticked:
        return backticked
    return [item.strip() for item in cell.split(",") if item.strip()]


def _canonical_evidence_items(cell: str) -> list[str]:
    items: list[str] = []
    for item in _split_cell_items(cell):
        normalized = item.strip()
        if not normalized or "linked child rows" in normalized.lower():
            continue
        if "/" not in normalized and not normalized.endswith((".md", ".json", ".csv", ".py")):
            continue
        if normalized not in items:
            items.append(normalized)
    return items


def _read_owner_doc_mappings(project_root: Path) -> tuple[dict[str, list[str]], dict[str, str], dict[str, list[str]]]:
    child_links: dict[str, list[str]] = {}
    owner_doc_by_requirement: dict[str, str] = {}
    owner_evidence_by_requirement: dict[str, list[str]] = {}

    for owner_doc in (FRAMEWORK_DOC_REL, DELTA_DOC_REL):
        doc_text = (project_root / owner_doc).read_text(encoding="utf-8")
        for table in _parse_markdown_tables(doc_text):
            if not table or "ID" not in table[0]:
                continue
            for row in table:
                requirement_id = row.get("ID", "").strip()
                if not requirement_id.startswith("HLA2025-"):
                    continue
                if "Linked child rows" in row:
                    child_links[requirement_id] = sorted(_split_cell_items(row["Linked child rows"]))
                    owner_doc_by_requirement[requirement_id] = owner_doc
                if "Evidence anchors" in row:
                    owner_evidence_by_requirement[requirement_id] = _canonical_evidence_items(row["Evidence anchors"])

    return child_links, owner_doc_by_requirement, owner_evidence_by_requirement


def _requirement_evidence_index(
    canonical_rows_by_requirement: dict[str, dict[str, Any]],
    owner_evidence_by_requirement: dict[str, list[str]],
) -> dict[str, list[str]]:
    evidence_by_requirement: dict[str, list[str]] = {}
    for requirement_id, row in canonical_rows_by_requirement.items():
        bucket = evidence_by_requirement.setdefault(requirement_id, [])
        for anchor in row.get("evidence_refs", []):
            if anchor not in bucket:
                bucket.append(anchor)
    for requirement_id, anchors in owner_evidence_by_requirement.items():
        bucket = evidence_by_requirement.setdefault(requirement_id, [])
        for anchor in anchors:
            if anchor not in bucket:
                bucket.append(anchor)
    return evidence_by_requirement


def build_spec2025_traceability_matrix(project_root: Path) -> dict[str, Any]:
    canonical_rows = load_2025_canonical_requirement_rows(project_root)
    traceability_packet_rows = _read_traceability_packet_rows(project_root)
    umbrella_child_links, owner_doc_by_requirement, owner_evidence_by_requirement = _read_owner_doc_mappings(project_root)
    canonical_rows_by_requirement = {
        row.requirement_id: {
            "canonical_status": row.canonical_status,
            "row_kind": row.row_kind,
            "owner_doc": row.owner_doc,
            "evidence_refs": list(row.evidence_refs),
        }
        for row in canonical_rows
    }
    evidence_by_requirement = _requirement_evidence_index(canonical_rows_by_requirement, owner_evidence_by_requirement)

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
        if not direct_evidence_anchors and requirement_id in owner_evidence_by_requirement:
            direct_evidence_anchors = list(owner_evidence_by_requirement[requirement_id])
        evidence_anchors = list(direct_evidence_anchors)
        for anchor in inherited_evidence_anchors:
            if anchor not in evidence_anchors:
                evidence_anchors.append(anchor)
        canonical_row = canonical_rows_by_requirement.get(requirement_id)
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
                    canonical_row["canonical_status"] if canonical_row else "packet-only"
                ),
                "row_role": canonical_row["row_kind"] if canonical_row else "packet-traceability",
                "owner_doc": owner_doc_by_requirement.get(requirement_id, canonical_row["owner_doc"] if canonical_row else ""),
                "child_requirement_ids": child_ids,
                "child_dispositions": {
                    child_id: canonical_rows_by_requirement[child_id]["canonical_status"]
                    for child_id in child_ids
                    if child_id in canonical_rows_by_requirement
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
        direct_evidence_anchors = list(owner_evidence_by_requirement.get(requirement_id, ()))
        inherited_evidence_anchors: list[str] = []
        for child_id in child_ids:
            for anchor in evidence_by_requirement.get(child_id, ()):
                if anchor not in inherited_evidence_anchors:
                    inherited_evidence_anchors.append(anchor)
        evidence_anchors = list(direct_evidence_anchors)
        for anchor in inherited_evidence_anchors:
            if anchor not in evidence_anchors:
                evidence_anchors.append(anchor)
        canonical_row = canonical_rows_by_requirement[requirement_id]
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
                "harmonization_disposition": canonical_row["canonical_status"],
                "row_role": canonical_row["row_kind"],
                "owner_doc": owner_doc_by_requirement.get(requirement_id, canonical_row["owner_doc"]),
                "child_requirement_ids": child_ids,
                "child_dispositions": {
                    child_id: canonical_rows_by_requirement[child_id]["canonical_status"]
                    for child_id in child_ids
                    if child_id in canonical_rows_by_requirement
                },
                "direct_evidence_anchors": direct_evidence_anchors,
                "inherited_evidence_anchors": inherited_evidence_anchors,
                "evidence_anchors": evidence_anchors,
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
