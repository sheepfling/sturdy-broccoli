from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from hla2010_repo_internal.verification.curated_requirement_refs import (
    get_curated_requirement_direct_refs,
)

_CURATED_REFERENCE_SOURCES = (
    "hla1516_1_clause_4_fm_service_decomposition.csv",
    "hla1516_1_federate_interface.csv",
    "hla1516_1_priority_clauses_4_8_11.csv",
)


def _split_semicolon_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [item.strip() for item in text.split(";") if item.strip()]


def _split_scalar_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    if ";" in text:
        return [item.strip() for item in text.split(";") if item.strip()]
    if "," in text:
        return [item.strip() for item in text.split(",") if item.strip()]
    return [text]


def _looks_like_artifact_ref(value: str) -> bool:
    text = str(value or "").strip()
    return any(token in text for token in ("/", ".py", ".md", ".csv", ".json", ".yaml", ".yml"))


def _path_like_refs(value: Any) -> list[str]:
    return [item for item in _split_semicolon_list(value) if _looks_like_artifact_ref(item)]


def _extract_markdown_link_targets(value: Any) -> list[str]:
    text = str(value or "")
    return [match.strip() for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text) if match.strip()]


def _section_ref(document: str, clause: str) -> str:
    normalized = str(clause).strip()
    if normalized.lower().startswith("clause "):
        normalized = normalized.split(" ", 1)[1].strip()
    if normalized in {"Framework concepts", "Federation and federate rules", "Object model concepts", "Time concept rules"}:
        return f"{document} {normalized}"
    return f"{document} §{normalized}"


def _curated_row_kind(row: dict[str, Any]) -> str:
    status = str(row.get("status", "")).strip().lower()
    seed_markers = {
        status,
        str(row.get("source_type", "")).strip().lower(),
        str(row.get("normative_keyword", "")).strip().lower(),
    }
    return "curated-seed" if {"seed", "seeded"} & seed_markers else "extracted-requirement"


def _curated_service_group(row: dict[str, Any]) -> str:
    family = str(row.get("family", "")).strip()
    service_group = str(row.get("service_group", "")).strip()
    topic = str(row.get("topic", "")).strip()
    decomposition_kind = str(row.get("decomposition_kind", "")).strip()
    if family and decomposition_kind:
        return f"{family}/{decomposition_kind}"
    if family:
        return family
    if service_group and decomposition_kind:
        return f"{service_group}/{decomposition_kind}"
    if service_group:
        return service_group
    if topic:
        return topic
    return "requirement"


def load_curated_requirement_rows(project_root: str | Path) -> list[dict[str, Any]]:
    repo_root = Path(project_root).resolve()
    traceability_path = repo_root / "requirements" / "traceability_matrix.csv"
    requirements_dir = repo_root / "requirements"
    reference_dir = requirements_dir / "reference"
    if not requirements_dir.exists() or not traceability_path.exists():
        return []
    excluded_sources = {
        "hla1516_1_clause_5_declaration_management.csv",
        "hla1516_1_clause_6_object_management.csv",
    }
    excluded_requirement_ids: set[str] = set()
    for source_name in excluded_sources:
        for source_path in (requirements_dir / source_name, reference_dir / source_name):
            if not source_path.exists():
                continue
            with source_path.open(newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    requirement_id = str(row.get("requirement_id", "")).strip()
                    if requirement_id:
                        excluded_requirement_ids.add(requirement_id)

    with traceability_path.open(newline="", encoding="utf-8") as fh:
        trace_rows = list(csv.DictReader(fh))
    trace_by_requirement = {row["requirement_id"]: row for row in trace_rows if row.get("requirement_id")}

    curated_rows_by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()

    source_paths = [
        source_path
        for source_path in sorted(requirements_dir.glob("*.csv"))
        if source_path.name != "traceability_matrix.csv" and source_path.name not in excluded_sources
    ]
    source_paths.extend(
        source_path
        for source_name in _CURATED_REFERENCE_SOURCES
        for source_path in [reference_dir / source_name]
        if source_path.exists() and source_path.name not in excluded_sources
    )

    for source_path in source_paths:
        with source_path.open(newline="", encoding="utf-8") as fh:
            source_rows = list(csv.DictReader(fh))
        for row in source_rows:
            requirement_id = str(row.get("requirement_id", "")).strip()
            if not requirement_id or requirement_id in seen or requirement_id in excluded_requirement_ids:
                continue
            trace = trace_by_requirement.get(requirement_id, {})
            document = str(row.get("standard") or row.get("source_document") or trace.get("source_document") or "").strip()
            clause = str(row.get("clause") or trace.get("clause") or "").strip()
            title = str(row.get("requirement_text") or row.get("topic") or row.get("canonical_topic") or requirement_id).strip()
            test_refs = _split_semicolon_list(trace.get("test_refs")) or _split_scalar_list(row.get("test_id"))
            implementation_refs = (
                _split_semicolon_list(trace.get("implementation_refs"))
                or _path_like_refs(row.get("implementation_target"))
                or _path_like_refs(row.get("derived_interpretation"))
            )
            linked_assets = [item for item in [str(trace.get("current_artifact_id", "")).strip(), str(row.get("parent_requirement_id", "")).strip()] if item]
            note_parts = [
                f"verification_method={row['verification_method']}" if row.get("verification_method") else "",
                str(row.get("notes", "")).strip(),
                str(trace.get("notes", "")).strip(),
            ]
            direct_refs = get_curated_requirement_direct_refs().get(requirement_id, {})
            source_ref = str(source_path.relative_to(repo_root)).replace("\\", "/")
            curated_rows_by_id[requirement_id] = {
                "matrix_id": requirement_id,
                "kind": _curated_row_kind(row),
                "document": document,
                "section_ref": _section_ref(document, clause) if document and clause else document or clause,
                "title": title,
                "requirement_id": requirement_id,
                "service_group": _curated_service_group(row),
                "status": trace.get("status") or row.get("status", "planned"),
                "implementation_refs": list(direct_refs.get("implementation_refs", implementation_refs)),
                "positive_test_refs": list(direct_refs.get("positive_test_refs", test_refs)),
                "negative_test_refs": list(direct_refs.get("negative_test_refs", ())),
                "artifact_refs": sorted(set(_split_semicolon_list(trace.get("artifact_refs"))) | {source_ref}),
                "linked_methods": _split_scalar_list(row.get("linked_methods")),
                "linked_assets": linked_assets,
                "notes": "; ".join(part for part in note_parts if part),
                "source": source_ref,
            }
            seen.add(requirement_id)

    for requirement_id, trace in sorted(trace_by_requirement.items()):
        if requirement_id in seen or requirement_id in excluded_requirement_ids:
            continue
        curated_rows_by_id[requirement_id] = {
            "matrix_id": requirement_id,
            "kind": "curated-seed",
            "document": trace["source_document"],
            "section_ref": _section_ref(trace["source_document"], trace["clause"]),
            "title": trace["canonical_topic"],
            "requirement_id": requirement_id,
            "service_group": "seed",
            "status": trace["status"],
            "implementation_refs": _split_semicolon_list(trace.get("implementation_refs")),
            "positive_test_refs": _split_semicolon_list(trace.get("test_refs")),
            "negative_test_refs": [],
            "artifact_refs": _split_semicolon_list(trace.get("artifact_refs")),
            "linked_assets": [item for item in [trace.get("current_artifact_id", "").strip()] if item],
            "notes": trace.get("notes", "").strip(),
            "source": "requirements/traceability_matrix.csv",
        }
    return [curated_rows_by_id[key] for key in sorted(curated_rows_by_id)]


__all__ = ["load_curated_requirement_rows"]
