from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from hla.spec.refs import IEEE_1516_1_2010

from ..requirements import (
    build_2010_backend_resolution_catalog,
    build_2010_canonical_requirement_catalog,
    build_2010_projection_requirement_catalog,
)
from .extracted_clause_requirements import get_extracted_requirements_1516_1_clauses_5_6
from .repo_seed_artifacts import build_requirements_ledger
from .vendor_parity_metadata import (
    load_backend_conformance_vendor_rows,
    load_operational_vendor_profiles,
    with_vendor_parity,
)

_CANONICAL_2010_REQUIREMENTS = "requirements/2010/canonical_requirements.json"
_CANONICAL_2010_BACKEND_RESOLUTION = "requirements/2010/backend_resolution.json"
_CANONICAL_2010_PROJECTION_ROWS = "requirements/2010/canonical_projection_rows.json"
_LEGACY_2010_MATRIX_CSV = "analysis/compliance/requirements_matrix_2010.csv"


def require_project_root(project_root: str | Path | None) -> Path:
    if project_root is None:
        raise ValueError("project_root is required for repo-backed verification artifacts")
    return Path(project_root).resolve()


def _normalize_supported_subset_refs(value: Any) -> list[str] | str:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value in (None, ""):
        return ""
    return str(value)


def _partition_evidence_refs(refs: list[str] | tuple[str, ...]) -> tuple[list[str], list[str], list[str], list[str]]:
    implementation_refs: list[str] = []
    positive_test_refs: list[str] = []
    negative_test_refs: list[str] = []
    artifact_refs: list[str] = []

    negative_tokens = (
        "negative",
        "reject",
        "rejects",
        "invalid",
        "failure",
        "fail",
        "not_connected",
        "not_joined",
        "save_restore",
    )

    for ref in refs:
        if ref.startswith("tests/"):
            if any(token in ref.lower() for token in negative_tokens):
                negative_test_refs.append(ref)
            else:
                positive_test_refs.append(ref)
            continue
        if ref.startswith(("analysis/", "requirements/", "docs/", "verification/")):
            artifact_refs.append(ref)
            continue
        implementation_refs.append(ref)

    return implementation_refs, positive_test_refs, negative_test_refs, artifact_refs


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _split_semicolon_refs(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [item.strip() for item in text.split(";") if item.strip()]


def build_requirements_matrix_2010(project_root: str | Path | None = None, *, version: str = "0.13.0") -> dict[str, Any]:
    """Return a whole-spec requirements matrix spanning section areas, service rows, and verification slices."""
    repo_root = require_project_root(project_root)
    ledger = build_requirements_ledger(version=version)
    vendor_rows_by_clause = load_backend_conformance_vendor_rows(repo_root)
    operational_vendor_profiles = load_operational_vendor_profiles(repo_root)
    extracted_requirements = get_extracted_requirements_1516_1_clauses_5_6()
    extracted_specs_by_id = {spec["requirement_id"]: spec for spec in extracted_requirements}
    canonical_rows = build_2010_canonical_requirement_catalog(repo_root).rows
    projection_rows = build_2010_projection_requirement_catalog(repo_root).rows
    backend_resolution_rows = {
        row.requirement_id: row
        for row in build_2010_backend_resolution_catalog(repo_root).rows
    }
    legacy_matrix_rows_by_id = {
        (row.get("requirement_id", "").strip() or row.get("matrix_id", "").strip()): row
        for row in csv.DictReader((repo_root / _LEGACY_2010_MATRIX_CSV).open(newline="", encoding="utf-8"))
    }
    ledger_rows_by_id = {
        str(row["requirement_id"]): row
        for row in ledger["rows"]
    }

    rows: list[dict[str, Any]] = []

    def _normalize_requirement_status(status: str) -> str:
        mapping = {
            "implemented-slice": "pass",
            "implemented-smoke": "partial",
            "pass": "pass",
            "mapped": "pass",
            "partial": "partial",
            "planned": "planned",
            "seeded": "planned",
            "not-evidenced": "not-evidenced",
            "gap": "fail",
            "fail": "fail",
        }
        return mapping.get(status, "planned")

    def _aggregate_status(statuses: list[str]) -> str:
        normalized = [_normalize_requirement_status(item) for item in statuses if item]
        if not normalized:
            return "planned"
        if any(item == "fail" for item in normalized):
            return "fail"
        if any(item == "not-evidenced" for item in normalized):
            return "not-evidenced"
        if any(item == "partial" for item in normalized):
            return "partial"
        if any(item == "pass" for item in normalized):
            return "pass"
        return "planned"

    def _edition_qualified_document(document: str) -> str:
        if document == "IEEE 1516.1-2010":
            return IEEE_1516_1_2010
        if document == "IEEE 1516.2-2010":
            return "IEEE 1516.2-2010 (2010 edition)"
        return document

    def _edition_qualified_section_ref(section_ref: str) -> str:
        if section_ref.startswith("IEEE 1516.1-2010 §"):
            return section_ref.replace("IEEE 1516.1-2010 §", f"{IEEE_1516_1_2010} §", 1)
        if section_ref.startswith("IEEE 1516.2-2010 §"):
            return section_ref.replace("IEEE 1516.2-2010 §", "IEEE 1516.2-2010 (2010 edition) §", 1)
        return section_ref
    for canonical_row in canonical_rows:
        title = canonical_row.service_or_check or canonical_row.requirement_text or canonical_row.requirement_id
        backend_row = backend_resolution_rows.get(canonical_row.requirement_id)
        backend_fields = dict(backend_row.backend_fields) if backend_row is not None else {}
        claim_scope = backend_fields.get("claim_scope", canonical_row.boundary_note)
        policy_basis = backend_fields.get("policy_basis", "")

        if canonical_row.row_kind == "service-requirement":
            ledger_row = ledger_rows_by_id.get(canonical_row.requirement_id)
            implementation_refs = list(ledger_row["implementation_refs"]) if ledger_row is not None else []
            positive_test_refs = list(ledger_row["positive_test_refs"]) if ledger_row is not None else []
            negative_test_refs = list(ledger_row["negative_test_refs"]) if ledger_row is not None else []
            artifact_refs = list(ledger_row["artifact_refs"]) if ledger_row is not None else []
            source = str(ledger_row["method"]) if ledger_row is not None else f"canonical:{canonical_row.requirement_id}"
            status = canonical_row.canonical_status
            rows.append(
                with_vendor_parity(
                    {
                        "matrix_id": canonical_row.requirement_id,
                        "kind": canonical_row.row_kind,
                        "document": _edition_qualified_document(canonical_row.source_document),
                        "section_ref": _edition_qualified_section_ref(canonical_row.clause),
                        "title": title,
                        "requirement_id": canonical_row.requirement_id,
                        "service_group": canonical_row.service_group,
                        "status": status,
                        "implementation_refs": implementation_refs,
                        "positive_test_refs": positive_test_refs,
                        "negative_test_refs": negative_test_refs,
                        "artifact_refs": artifact_refs,
                        "linked_methods": [],
                        "linked_assets": [],
                        "claim_scope": claim_scope,
                        "supported_subset_for": _normalize_supported_subset_refs(canonical_row.parent_requirement_id),
                        "policy_basis": policy_basis,
                        "notes": canonical_row.canonical_status_reason,
                        "source": source,
                    },
                    vendor_rows_by_clause=vendor_rows_by_clause,
                    operational_vendor_profiles=operational_vendor_profiles,
                )
            )
            continue

        extracted_spec = extracted_specs_by_id.get(canonical_row.requirement_id, {})
        legacy_row = legacy_matrix_rows_by_id.get(canonical_row.requirement_id, {})
        implementation_refs, positive_test_refs, negative_test_refs, artifact_refs = _partition_evidence_refs(
            list(canonical_row.evidence_refs)
        )
        implementation_refs = list(extracted_spec.get("implementation_refs", implementation_refs))
        legacy_positive_test_refs = _split_semicolon_refs(legacy_row.get("positive_test_refs", ""))
        legacy_negative_test_refs = _split_semicolon_refs(legacy_row.get("negative_test_refs", ""))
        if "positive_test_refs" in extracted_spec:
            positive_test_refs = list(extracted_spec["positive_test_refs"])
        elif legacy_row:
            positive_test_refs = legacy_positive_test_refs
        if "negative_test_refs" in extracted_spec:
            negative_test_refs = list(extracted_spec["negative_test_refs"])
        elif legacy_row:
            negative_test_refs = legacy_negative_test_refs
        if "artifact_refs" in extracted_spec:
            artifact_refs = list(extracted_spec["artifact_refs"])
        elif legacy_row:
            artifact_refs = _split_semicolon_refs(legacy_row.get("artifact_refs", ""))
        linked_methods = list(extracted_spec.get("linked_methods", ())) or _split_semicolon_refs(legacy_row.get("linked_methods", ""))
        linked_assets = list(extracted_spec.get("linked_assets", ())) or _split_semicolon_refs(legacy_row.get("linked_assets", ""))
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": canonical_row.requirement_id,
                    "kind": canonical_row.row_kind,
                    "document": _edition_qualified_document(canonical_row.source_document),
                    "section_ref": _edition_qualified_section_ref(canonical_row.clause),
                    "title": title,
                    "requirement_id": canonical_row.requirement_id,
                    "service_group": canonical_row.service_group,
                    "status": canonical_row.canonical_status,
                    "implementation_refs": _dedupe_preserve_order(implementation_refs),
                    "positive_test_refs": _dedupe_preserve_order(positive_test_refs),
                    "negative_test_refs": _dedupe_preserve_order(negative_test_refs),
                    "artifact_refs": _dedupe_preserve_order(artifact_refs),
                    "linked_methods": linked_methods,
                    "linked_assets": linked_assets,
                    "claim_scope": claim_scope,
                    "supported_subset_for": _normalize_supported_subset_refs(canonical_row.parent_requirement_id),
                    "policy_basis": policy_basis,
                    "notes": canonical_row.canonical_status_reason,
                    "source": f"canonical:{canonical_row.requirement_id}",
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    for projection_row in projection_rows:
        implementation_refs, positive_test_refs, negative_test_refs, artifact_refs = _partition_evidence_refs(
            list(projection_row.evidence_refs)
        )
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": projection_row.requirement_id,
                    "kind": projection_row.row_kind,
                    "document": _edition_qualified_document(projection_row.source_document),
                    "section_ref": _edition_qualified_section_ref(projection_row.clause),
                    "title": projection_row.service_or_check or projection_row.requirement_text or projection_row.requirement_id,
                    "requirement_id": projection_row.requirement_id,
                    "service_group": projection_row.service_group,
                    "status": projection_row.canonical_status,
                    "implementation_refs": _dedupe_preserve_order(implementation_refs),
                    "positive_test_refs": _dedupe_preserve_order(positive_test_refs),
                    "negative_test_refs": _dedupe_preserve_order(negative_test_refs),
                    "artifact_refs": _dedupe_preserve_order(artifact_refs),
                    "linked_methods": [],
                    "linked_assets": [],
                    "claim_scope": projection_row.boundary_note,
                    "supported_subset_for": _normalize_supported_subset_refs(projection_row.parent_requirement_id),
                    "policy_basis": "",
                    "notes": projection_row.canonical_status_reason,
                    "source": f"projection:{projection_row.requirement_id}",
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    kind_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for row in rows:
        kind_counts[row["kind"]] = kind_counts.get(row["kind"], 0) + 1
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "summary": {
            "artifact": "requirements-matrix-2010",
            "artifact_class": "projection",
            "projection_basis": (
                "Legacy whole-spec 2010 review matrix spanning canonical leaf rows plus "
                "explicitly demoted rollup and grouping rows."
            ),
            "canonical_requirement_artifact": _CANONICAL_2010_REQUIREMENTS,
            "canonical_backend_resolution_artifact": _CANONICAL_2010_BACKEND_RESOLUTION,
            "projection_rollup_artifact": _CANONICAL_2010_PROJECTION_ROWS,
            "version": version,
            "row_count": len(rows),
            "kind_counts": dict(sorted(kind_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "documents": sorted({row["document"] for row in rows}),
        },
        "rows": rows,
    }


def write_requirements_matrix_2010_json(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    repo_root = require_project_root(project_root)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_requirements_matrix_2010(repo_root, version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_requirements_matrix_2010_csv(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    repo_root = require_project_root(project_root)
    matrix = build_requirements_matrix_2010(repo_root, version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "matrix_id",
        "kind",
        "document",
        "section_ref",
        "title",
        "requirement_id",
        "service_group",
        "status",
        "implementation_refs",
        "positive_test_refs",
        "negative_test_refs",
        "artifact_refs",
        "linked_methods",
        "linked_assets",
        "claim_scope",
        "supported_subset_for",
        "policy_basis",
        "python_runtime_status",
        "python_runtime_disposition",
        "certi_runtime_status",
        "certi_runtime_disposition",
        "portico_runtime_status",
        "portico_runtime_disposition",
        "pitch_runtime_status",
        "pitch_runtime_disposition",
        "pitch_jpype_runtime_disposition",
        "pitch_py4j_runtime_disposition",
        "vendor_evidence_refs",
        "vendor_notes",
        "vendor_source",
        "vendor_profile_bucket",
        "vendor_profile_refs",
        "vendor_profile_notes",
        "vendor_profile_source",
        "notes",
        "source",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in matrix["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, (list, tuple)):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target
