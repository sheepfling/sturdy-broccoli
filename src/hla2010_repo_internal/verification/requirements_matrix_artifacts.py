from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from hla2010.spec_refs import FOM_REFERENCES, SERVICE_AREAS

from ..requirements_source import (
    format_requirement_section_ref,
    normalize_requirement_section_ref,
    requirement_document_title_for_binding,
)
from .asset_plan import build_verification_plan
from .curated_requirement_rows import load_curated_requirement_rows
from .extracted_clause_requirements import get_extracted_requirements_1516_1_clauses_5_6
from .repo_seed_artifacts import build_requirements_ledger
from .vendor_parity_metadata import (
    load_backend_conformance_vendor_rows,
    load_operational_vendor_profiles,
    with_vendor_parity,
)

def require_project_root(project_root: str | Path | None) -> Path:
    if project_root is None:
        raise ValueError("project_root is required for repo-backed verification artifacts")
    return Path(project_root).resolve()


def build_requirements_matrix_2010(project_root: str | Path | None = None, *, version: str = "0.13.0") -> dict[str, Any]:
    """Return a whole-spec requirements matrix spanning section areas, service rows, and verification slices."""
    repo_root = require_project_root(project_root)
    federate_interface_document = requirement_document_title_for_binding("federate_interface")
    omt_document = requirement_document_title_for_binding("omt")
    ledger = build_requirements_ledger(version=version)
    plan = build_verification_plan(version)
    vendor_rows_by_clause = load_backend_conformance_vendor_rows(repo_root)
    operational_vendor_profiles = load_operational_vendor_profiles(repo_root)
    extracted_requirements = get_extracted_requirements_1516_1_clauses_5_6()

    rows: list[dict[str, Any]] = []
    verification_slice_rows: list[dict[str, Any]] = []
    service_rows_by_method: dict[str, list[dict[str, Any]]] = {}
    for row in ledger["rows"]:
        service_rows_by_method.setdefault(str(row["method"]), []).append(row)
    assets_by_id = {asset.asset_id: asset for asset in plan.assets}
    extracted_specs_by_id = {spec["requirement_id"]: spec for spec in extracted_requirements}

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

    def _normalize_section_ref(section_ref: str, *, default_document: str) -> str:
        return normalize_requirement_section_ref(section_ref, default_document=default_document)

    def _normalize_known_section_ref(section_ref: str) -> str:
        return normalize_requirement_section_ref(section_ref)

    section_area_inputs: dict[str, list[str]] = {}
    omt_area_inputs: dict[str, list[str]] = {}
    for row in ledger["rows"]:
        raw_section = str(row["section"])
        section = raw_section.split("§", 1)[-1].split(".", 1)[0].strip()
        section_area_inputs.setdefault(section, []).append(row["outcome"])

    for key, ref in SERVICE_AREAS.items():
        section_status = _aggregate_status(section_area_inputs.get(ref.section, []))
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": f"AREA-1516.1-{ref.section}",
                    "kind": "section-area",
                    "document": federate_interface_document,
                    "section_ref": format_requirement_section_ref(federate_interface_document, ref.section),
                    "title": ref.title,
                    "requirement_id": "",
                    "service_group": ref.title,
                    "status": section_status,
                    "implementation_refs": [],
                    "positive_test_refs": [],
                    "negative_test_refs": [],
                    "artifact_refs": [],
                    "source": key,
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    def _omt_requirement_id(section: str, source_key: str) -> str:
        token = section.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
        return f"REQ-OMT-{token}-{source_key}"

    for key, ref in FOM_REFERENCES.items():
        requirement_id = _omt_requirement_id(ref.section, key)
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": requirement_id,
                    "kind": "omt-area",
                    "document": omt_document,
                    "section_ref": format_requirement_section_ref(omt_document, ref.section),
                    "title": ref.title,
                    "requirement_id": requirement_id,
                    "service_group": "OMT/FOM",
                    "status": "planned",
                    "implementation_refs": [],
                    "positive_test_refs": [],
                    "negative_test_refs": [],
                    "artifact_refs": [],
                    "source": key,
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    curated_requirement_ids: set[str] = set()
    for row in load_curated_requirement_rows(repo_root):
        normalized = dict(row)
        extracted_spec = extracted_specs_by_id.get(str(normalized.get("requirement_id", "")))
        if extracted_spec is not None:
            if not normalized.get("linked_methods"):
                normalized["linked_methods"] = list(extracted_spec.get("linked_methods", ()))
            if not normalized.get("linked_assets"):
                normalized["linked_assets"] = list(extracted_spec.get("linked_assets", ()))
        normalized["status"] = _normalize_requirement_status(str(row["status"]))
        rows.append(
            with_vendor_parity(
                normalized,
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )
        curated_requirement_ids.add(str(normalized["requirement_id"]))

    for row in ledger["rows"]:
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": row["requirement_id"],
                    "kind": "service-requirement",
                    "document": federate_interface_document,
                    "section_ref": _normalize_section_ref(str(row["section"]), default_document=federate_interface_document),
                    "title": row["title"],
                    "requirement_id": row["requirement_id"],
                    "service_group": row["service_group"],
                    "status": row["outcome"],
                    "implementation_refs": row["implementation_refs"],
                    "positive_test_refs": row["positive_test_refs"],
                    "negative_test_refs": row["negative_test_refs"],
                    "artifact_refs": row["artifact_refs"],
                    "source": row["method"],
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    for spec in extracted_requirements:
        if spec["requirement_id"] in curated_requirement_ids:
            continue
        linked_service_rows = [item for method_name in spec.get("linked_methods", ()) for item in service_rows_by_method.get(method_name, ())]
        linked_assets = [assets_by_id[asset_id] for asset_id in spec.get("linked_assets", ()) if asset_id in assets_by_id]
        statuses = [item["outcome"] for item in linked_service_rows] + [asset.status for asset in linked_assets]
        status = spec.get("status_override") or _aggregate_status(statuses)
        implementation_refs = (
            list(spec["implementation_refs"])
            if "implementation_refs" in spec
            else sorted(
                {
                    ref
                    for item in linked_service_rows
                    for ref in item["implementation_refs"]
                }
                | {
                    ref
                    for asset in linked_assets
                    for ref in asset.evidence
                    if ref.startswith("hla2010/")
                }
            )
        )
        positive_test_refs = (
            list(spec["positive_test_refs"])
            if "positive_test_refs" in spec
            else sorted(
                {
                    ref
                    for item in linked_service_rows
                    for ref in item["positive_test_refs"]
                }
                | {
                    ref
                    for asset in linked_assets
                    for ref in asset.evidence
                    if ref.startswith("tests/")
                }
            )
        )
        negative_test_refs = (
            list(spec["negative_test_refs"])
            if "negative_test_refs" in spec
            else sorted(
                {
                    ref
                    for item in linked_service_rows
                    for ref in item["negative_test_refs"]
                }
                | {
                    ref
                    for asset in linked_assets
                    for ref in asset.evidence
                    if ref.startswith("tests/") and "negative" in ref.lower()
                }
            )
        )
        artifact_refs = (
            list(spec["artifact_refs"])
            if "artifact_refs" in spec
            else sorted(
                {
                    ref
                    for item in linked_service_rows
                    for ref in item["artifact_refs"]
                }
                | {
                    ref
                    for asset in linked_assets
                    for ref in asset.evidence
                    if ref.startswith("analysis/") or ref.startswith("verification/")
                }
            )
        )
        rows.append(
            with_vendor_parity(
                {
                    "matrix_id": spec["requirement_id"],
                    "kind": "extracted-requirement",
                    "document": federate_interface_document,
                    "section_ref": _normalize_section_ref(str(spec["section_ref"]), default_document=federate_interface_document),
                    "title": spec["title"],
                    "requirement_id": spec["requirement_id"],
                    "service_group": spec["service_group"],
                    "status": status,
                    "implementation_refs": implementation_refs,
                    "positive_test_refs": positive_test_refs,
                    "negative_test_refs": negative_test_refs,
                    "artifact_refs": artifact_refs,
                    "linked_methods": list(spec.get("linked_methods", ())),
                    "linked_assets": list(spec.get("linked_assets", ())),
                    "claim_scope": spec.get("claim_scope", "broad-spec"),
                    "supported_subset_for": spec.get("supported_subset_for", ""),
                    "policy_basis": spec.get("policy_basis", ""),
                    "notes": spec.get("notes", ""),
                    "source": "curated-clause5-6",
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )
        normalized_spec_ref = _normalize_known_section_ref(str(spec["section_ref"]))
        if normalized_spec_ref.startswith(f"{federate_interface_document} §"):
            section = normalized_spec_ref.split("§", 1)[1].split(".", 1)[0].strip()
            section_area_inputs.setdefault(section, []).append(status)

    for asset in plan.assets:
        if asset.asset_type not in {"requirement", "scenario"}:
            continue
        asset_row = {
            "matrix_id": asset.asset_id,
            "kind": "verification-slice",
            "document": "multi-section",
            "section_ref": "; ".join(_normalize_known_section_ref(section_ref) for section_ref in asset.section_refs),
            "title": asset.title,
            "requirement_id": asset.asset_id,
            "service_group": asset.asset_type,
            "status": asset.status,
            "implementation_refs": [item for item in asset.evidence if item.startswith("hla2010/")],
            "positive_test_refs": [item for item in asset.evidence if item.startswith("tests/")],
            "negative_test_refs": [item for item in asset.evidence if "negative" in item.lower()],
            "artifact_refs": [item for item in asset.evidence if item.startswith("analysis/") or item.startswith("verification/")],
            "source": asset.asset_id,
        }
        asset_row = with_vendor_parity(
            asset_row,
            vendor_rows_by_clause=vendor_rows_by_clause,
            operational_vendor_profiles=operational_vendor_profiles,
        )
        verification_slice_rows.append(asset_row)
        rows.append(asset_row)
        for section_ref in asset.section_refs:
            normalized_section_ref = _normalize_known_section_ref(section_ref)
            if normalized_section_ref.startswith(f"{federate_interface_document} §"):
                section = normalized_section_ref.split("§", 1)[1].split(".", 1)[0].strip()
                section_area_inputs.setdefault(section, []).append(asset.status)
            elif normalized_section_ref.startswith(f"{omt_document} §"):
                section = normalized_section_ref.split("§", 1)[1].strip()
                omt_area_inputs.setdefault(section, []).append(asset.status)

    for row in rows:
        if row["kind"] == "section-area":
            section = row["section_ref"].split("§", 1)[1].strip()
            row["status"] = _aggregate_status(section_area_inputs.get(section, []))
        elif row["kind"] == "omt-area":
            section = row["section_ref"].split("§", 1)[1].strip()
            source_key = row["source"]
            matching_assets = [
                item for item in verification_slice_rows
                if format_requirement_section_ref(omt_document, section) in item["section_ref"].split("; ")
            ]
            row["status"] = _aggregate_status(omt_area_inputs.get(section, []))
            row["implementation_refs"] = [item for asset in matching_assets for item in asset["implementation_refs"]]
            row["positive_test_refs"] = [item for asset in matching_assets for item in asset["positive_test_refs"]]
            row["negative_test_refs"] = [item for asset in matching_assets for item in asset["negative_test_refs"]]
            row["artifact_refs"] = [item for asset in matching_assets for item in asset["artifact_refs"]]
            row["source"] = source_key

    kind_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for row in rows:
        kind_counts[row["kind"]] = kind_counts.get(row["kind"], 0) + 1
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "summary": {
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
        "certi_runtime_status",
        "pitch_runtime_status",
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
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target
