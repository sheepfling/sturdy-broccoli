from __future__ import annotations

import csv
import json
from pathlib import Path
import re

from .models import BackendResolutionCatalog, BackendResolutionRow, CanonicalRequirementRow, NormalizedRequirementCatalog, RequirementMappingRow

CANONICAL_2010_REL = "requirements/2010/canonical_requirements.json"
CANONICAL_2025_REL = "requirements/2025/canonical_requirements.json"
BACKEND_2010_REL = "requirements/2010/backend_resolution.json"
BACKEND_2025_REL = "requirements/2025/backend_resolution.json"
HARMONIZATION_LEDGER_REL = "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"
COMPLIANCE_2010_REL = "analysis/compliance/requirements_matrix_2010.csv"
FM_RECONCILIATION_2010_REL = "requirements/2010/hla1516_1_fm_detailed_reconciliation.csv"
WORKLIST_2025_REL = "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"
PITCH_ROW_2025_REL = "requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv"
PITCH_GROUP_2025_REL = "requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv"
FI_BINDING_2025_REL = "requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv"

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")

_SPECIAL_2025_EVIDENCE_REFS = {
    "linked FI/OMT child rows": "literal:linked-fi-omt-child-rows",
    "migration/compatibility fixture if supported": "bounded:migration-compatibility-fixture-if-supported",
}

_SERVICE_GROUP_OWNER_DOCS = {
    "Federation management": "docs/requirements/ieee-1516-2025/federation_management_bounded_proof.md",
    "Declaration management": "docs/requirements/ieee-1516-2025/declaration_management_bounded_proof.md",
    "Object management": "docs/requirements/ieee-1516-2025/object_management_bounded_proof.md",
    "Ownership management": "docs/requirements/ieee-1516-2025/ownership_management_bounded_proof.md",
    "Data distribution management": "docs/requirements/ieee-1516-2025/ddm_bounded_proof.md",
    "Support services": "docs/requirements/ieee-1516-2025/support_services_bounded_proof.md",
    "Time management": "docs/requirements/ieee-1516-2025/time_management_bounded_proof.md",
}

_SHARD_COMMANDS = {
    "unit-foundation": "./tools/test-surface run unit-foundation",
    "unit-shim-tooling": "./tools/test-surface run unit-shim-tooling",
    "unit-fom-tooling": "./tools/test-surface run unit-fom-tooling",
    "unit-python-2025-core": "./tools/test-surface run unit-python-2025-core",
    "unit-transport-local": "./tools/test-surface run unit-transport-local",
}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _split_semicolon_items(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(";") if item.strip())


def _slug(value: str) -> str:
    candidate = _SLUG_NON_ALNUM.sub("-", value.strip().lower()).strip("-")
    return candidate or "unspecified"


def _derive_owner_doc(row: dict[str, str]) -> str:
    evidence_refs = _split_semicolon_items(row.get("suggested_repo_evidence_path", ""))
    for evidence_ref in evidence_refs:
        if evidence_ref.startswith("docs/requirements/ieee-1516-2025/") and evidence_ref.endswith(".md"):
            return evidence_ref

    area = row.get("area", "")
    service_group = row.get("service_group", "")
    service_or_check = row.get("service_or_check", "")

    if area == "Federate Interface service catalog":
        return _SERVICE_GROUP_OWNER_DOCS.get(service_group, "docs/requirements/ieee-1516-2025/federate_interface.md")
    if area == "SOM/FOM service-usage requirements":
        return "docs/requirements/ieee-1516-2025/omt.md"
    if area == "OMT component-level conformance":
        if "xs:any" in service_or_check.lower():
            return "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md"
        return "docs/requirements/ieee-1516-2025/omt.md"
    if area == "OMT validator-negative conformance":
        return "docs/requirements/ieee-1516-2025/omt.md"
    if area == "Callback/configuration/binding deltas":
        return "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
    if area == "Framework and Rules":
        return "docs/requirements/ieee-1516-2025/framework_rules.md"
    if area == "Retired / replacement mapping candidates":
        return "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
    return ""


def _derive_primary_shard(row: dict[str, str], owner_doc: str) -> str:
    area = row.get("area", "")
    if area == "Federate Interface service catalog":
        return "unit-python-2025-core"
    if area in {"SOM/FOM service-usage requirements", "OMT component-level conformance", "OMT validator-negative conformance"}:
        return "unit-fom-tooling"
    if area == "Callback/configuration/binding deltas":
        return "unit-shim-tooling"
    if area == "Framework and Rules":
        return "unit-python-2025-core"
    if area == "Retired / replacement mapping candidates":
        return "unit-foundation"
    if owner_doc == "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md":
        return "unit-transport-local"
    return "unit-foundation"


def _derive_boundary_note(row: dict[str, str]) -> str:
    parts = [
        row.get("negative_boundary", "").strip(),
        row.get("unsupported_boundary_candidate", "").strip(),
        row.get("notes", "").strip(),
    ]
    return " ".join(part for part in parts if part)


def _primary_shard_from_command(primary_command: str) -> str:
    command = primary_command.strip()
    if command == "./tools/test-surface run unit-transport-local":
        return "unit-transport-local"
    if command == "./tools/pitch 202x-micro-certify":
        return "unit-transport-local"
    return ""


def _pitch_202x_evidence_refs(row: dict[str, str]) -> tuple[str, ...]:
    refs: list[str] = []
    refs.extend(_split_semicolon_items(row.get("pitch_202x_evidence_packet", "")))
    refs.extend(
        ref
        for ref in (
            row.get("pitch_202x_owner_doc", "").strip(),
            row.get("pitch_202x_group_owner", "").strip(),
        )
        if ref
    )
    deduped: list[str] = []
    for ref in refs:
        if ref not in deduped:
            deduped.append(ref)
    return tuple(deduped)


def _derive_tags(row: dict[str, str], owner_doc: str) -> tuple[str, ...]:
    tags = [
        f"area:{_slug(row.get('area', ''))}",
        f"service-group:{_slug(row.get('service_group', ''))}",
        f"priority:{_slug(row.get('priority', ''))}",
        f"closure-wave:{_slug(row.get('closure_wave', ''))}",
    ]
    known_seed_slice = row.get("known_seed_slice", "").strip()
    if known_seed_slice:
        tags.append(f"seed-slice:{_slug(known_seed_slice)}")
    if owner_doc:
        tags.append(f"owner:{_slug(Path(owner_doc).stem)}")
    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return tuple(deduped)


def _normalize_2025_evidence_refs(row: dict[str, str]) -> tuple[str, ...]:
    refs = list(_split_semicolon_items(row.get("suggested_repo_evidence_path", "")))
    normalized: list[str] = []
    for ref in refs:
        if ref in _SPECIAL_2025_EVIDENCE_REFS:
            normalized.append(_SPECIAL_2025_EVIDENCE_REFS[ref])
        elif ref == "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py":
            normalized.append("packages/hla-rti-core/src/hla/fom/validation.py")
        else:
            normalized.append(ref)
    deduped: list[str] = []
    for ref in normalized:
        if ref not in deduped:
            deduped.append(ref)
    return tuple(deduped)


def build_2025_canonical_requirement_catalog(project_root: Path) -> NormalizedRequirementCatalog:
    ledger_rows = _read_csv_rows(project_root / HARMONIZATION_LEDGER_REL)
    rows: list[CanonicalRequirementRow] = []
    for row in ledger_rows:
        owner_doc = _derive_owner_doc(row)
        primary_test_shard = _derive_primary_shard(row, owner_doc)
        rows.append(
            CanonicalRequirementRow(
                edition="2025",
                requirement_id=row.get("id", "").strip(),
                source_document=row.get("source_document", "").strip(),
                clause=row.get("clause", "").strip(),
                page=row.get("page", "").strip(),
                area=row.get("area", "").strip(),
                service_group=row.get("service_group", "").strip(),
                service_or_check=row.get("service_or_check", "").strip(),
                priority=row.get("priority", "").strip(),
                closure_wave=row.get("closure_wave", "").strip(),
                requirement_text=row.get("requirement_text", "").strip(),
                normative_level=row.get("normative_level", "").strip(),
                row_kind=row.get("row_role", "").strip(),
                parent_requirement_id="",
                canonical_status=row.get("harmonization_disposition", "").strip(),
                canonical_status_reason=row.get("disposition_rationale", "").strip(),
                owner_doc=owner_doc,
                primary_test_shard=primary_test_shard,
                primary_command=_SHARD_COMMANDS.get(primary_test_shard, ""),
                evidence_refs=_normalize_2025_evidence_refs(row),
                boundary_note=_derive_boundary_note(row),
                source_trace_strength=row.get("source_trace_strength", "").strip(),
                repo_evidence_status=row.get("repo_evidence_status", "").strip(),
                tags=_derive_tags(row, owner_doc),
            )
        )
    return NormalizedRequirementCatalog(
        artifact="canonical-requirements-catalog",
        edition="2025",
        generated_from=(HARMONIZATION_LEDGER_REL,),
        row_count=len(rows),
        rows=tuple(rows),
    )


def build_2010_canonical_requirement_catalog(project_root: Path) -> NormalizedRequirementCatalog:
    matrix_rows = _read_csv_rows(project_root / COMPLIANCE_2010_REL)
    rows: list[CanonicalRequirementRow] = []
    for row in matrix_rows:
        evidence_parts = []
        for field in ("implementation_refs", "positive_test_refs", "negative_test_refs", "artifact_refs"):
            evidence_parts.extend(_split_semicolon_items(row.get(field, "")))
        deduped_evidence: list[str] = []
        for ref in evidence_parts:
            if ref not in deduped_evidence:
                deduped_evidence.append(ref)
        rows.append(
            CanonicalRequirementRow(
                edition="2010",
                requirement_id=row.get("requirement_id", "").strip() or row.get("matrix_id", "").strip(),
                source_document=row.get("document", "").strip(),
                clause=row.get("section_ref", "").strip(),
                page="",
                area=row.get("document", "").strip(),
                service_group=row.get("service_group", "").strip(),
                service_or_check=row.get("title", "").strip(),
                priority="",
                closure_wave="",
                requirement_text=row.get("title", "").strip(),
                normative_level="",
                row_kind=row.get("kind", "").strip(),
                parent_requirement_id=row.get("supported_subset_for", "").strip(),
                canonical_status=row.get("status", "").strip(),
                canonical_status_reason=row.get("notes", "").strip(),
                owner_doc="",
                primary_test_shard="",
                primary_command="",
                evidence_refs=tuple(deduped_evidence),
                boundary_note=row.get("claim_scope", "").strip(),
                source_trace_strength="",
                repo_evidence_status="",
                tags=tuple(
                    tag for tag in (
                        f"document:{_slug(row.get('document', ''))}",
                        f"service-group:{_slug(row.get('service_group', ''))}" if row.get("service_group", "").strip() else "",
                        f"policy:{_slug(row.get('policy_basis', ''))}" if row.get("policy_basis", "").strip() else "",
                    ) if tag
                ),
            )
        )
    return NormalizedRequirementCatalog(
        artifact="canonical-requirements-catalog",
        edition="2010",
        generated_from=(COMPLIANCE_2010_REL,),
        row_count=len(rows),
        rows=tuple(rows),
    )


def write_2010_canonical_requirement_catalog(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / CANONICAL_2010_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_2010_canonical_requirement_catalog(project_root).to_mapping()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_2025_canonical_requirement_catalog(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / CANONICAL_2025_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_2025_canonical_requirement_catalog(project_root).to_mapping()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load_canonical_requirement_catalog(path: Path) -> NormalizedRequirementCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return NormalizedRequirementCatalog.from_mapping(payload)


def build_2010_backend_resolution_catalog(project_root: Path) -> BackendResolutionCatalog:
    rows = _read_csv_rows(project_root / COMPLIANCE_2010_REL)
    backend_rows = [
        BackendResolutionRow(
            edition="2010",
            requirement_id=row.get("requirement_id", "").strip() or row.get("matrix_id", "").strip(),
            row_kind="requirement-row",
            resolution_type="backend-runtime-disposition",
            canonical_owner="",
            canonical_status=row.get("status", "").strip(),
            primary_shard="",
            primary_command="",
            evidence_artifact=row.get("artifact_refs", "").strip(),
            evidence_refs=_split_semicolon_items(row.get("artifact_refs", "")),
            boundary_note=row.get("notes", "").strip(),
            backend_fields={
                "python_runtime_disposition": row.get("python_runtime_disposition", "").strip(),
                "certi_runtime_disposition": row.get("certi_runtime_disposition", "").strip(),
                "pitch_runtime_disposition": row.get("pitch_runtime_disposition", "").strip(),
                "portico_runtime_disposition": row.get("portico_runtime_disposition", "").strip(),
                "pitch_jpype_runtime_disposition": row.get("pitch_jpype_runtime_disposition", "").strip(),
                "pitch_py4j_runtime_disposition": row.get("pitch_py4j_runtime_disposition", "").strip(),
                "policy_basis": row.get("policy_basis", "").strip(),
                "claim_scope": row.get("claim_scope", "").strip(),
            },
        )
        for row in rows
    ]
    return BackendResolutionCatalog(
        artifact="backend-resolution-catalog",
        edition="2010",
        generated_from=(COMPLIANCE_2010_REL,),
        row_count=len(backend_rows),
        rows=tuple(backend_rows),
    )


def write_2010_backend_resolution_catalog(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / BACKEND_2010_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_2010_backend_resolution_catalog(project_root).to_mapping()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def build_2025_backend_resolution_catalog(project_root: Path) -> BackendResolutionCatalog:
    backend_rows: list[BackendResolutionRow] = []
    worklist_rows = _read_csv_rows(project_root / WORKLIST_2025_REL)
    for row in worklist_rows:
        owner_doc = _derive_owner_doc(
            {
                "area": row.get("area", ""),
                "service_group": row.get("service_group", ""),
                "service_or_check": "",
                "suggested_repo_evidence_path": row.get("backend_resolution_reference", ""),
            }
        )
        primary_shard = _derive_primary_shard({"area": row.get("area", "")}, owner_doc)
        backend_rows.append(
            BackendResolutionRow(
                edition="2025",
                requirement_id=f"group::{row.get('closure_wave','').strip()}::{row.get('area','').strip()}::{row.get('service_group','').strip()}",
                row_kind="grouped-projection",
                resolution_type="grouped-backend-view",
                canonical_owner=owner_doc,
                canonical_status=row.get("canonical_disposition", "").strip(),
                primary_shard=primary_shard,
                primary_command=_SHARD_COMMANDS.get(primary_shard, ""),
                evidence_artifact=row.get("backend_resolution_reference", "").strip(),
                evidence_refs=_split_semicolon_items(row.get("backend_resolution_reference", "")),
                boundary_note=row.get("acceptance_gate", "").strip(),
                backend_fields={
                    "group_kind": "2025-group",
                    "closure_wave": row.get("closure_wave", "").strip(),
                    "priority": row.get("priority", "").strip(),
                    "area": row.get("area", "").strip(),
                    "service_group": row.get("service_group", "").strip(),
                    "python_runtime_resolution": row.get("python_runtime_resolution", "").strip(),
                    "java_cpp_binding_resolution": row.get("java_cpp_binding_resolution", "").strip(),
                    "hosted_fedpro_resolution": row.get("hosted_fedpro_resolution", "").strip(),
                    "pitch_202x_resolution": row.get("pitch_202x_resolution", "").strip(),
                    "backend_resolution_reference": row.get("backend_resolution_reference", "").strip(),
                    "row_count": row.get("row_count", "").strip(),
                    "delta_breakdown": row.get("delta_breakdown", "").strip(),
                    "closure_goal": row.get("closure_goal", "").strip(),
                },
            )
        )
    backend_rows.extend(load_2025_pitch_row_resolution_rows(project_root))
    backend_rows.extend(load_2025_pitch_group_resolution_rows(project_root))
    backend_rows.extend(load_2025_fi_binding_surface_rows(project_root))
    return BackendResolutionCatalog(
        artifact="backend-resolution-catalog",
        edition="2025",
        generated_from=(WORKLIST_2025_REL, PITCH_ROW_2025_REL, PITCH_GROUP_2025_REL, FI_BINDING_2025_REL),
        row_count=len(backend_rows),
        rows=tuple(backend_rows),
    )


def write_2025_backend_resolution_catalog(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / BACKEND_2025_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_2025_backend_resolution_catalog(project_root).to_mapping()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load_backend_resolution_catalog(path: Path) -> BackendResolutionCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return BackendResolutionCatalog.from_mapping(payload)


def load_2025_canonical_requirement_rows(project_root: Path) -> tuple[CanonicalRequirementRow, ...]:
    return build_2025_canonical_requirement_catalog(project_root).rows


def load_2010_fm_reconciliation_rows(project_root: Path) -> tuple[RequirementMappingRow, ...]:
    rows = _read_csv_rows(project_root / FM_RECONCILIATION_2010_REL)
    return tuple(
        RequirementMappingRow(
            edition="2010",
            source_requirement_id=row.get("packet_requirement_id", "").strip(),
            canonical_requirement_id=row.get("curated_requirement_id", "").strip(),
            mapping_kind=row.get("reconciliation_kind", "").strip(),
            mapping_notes=row.get("notes", "").strip(),
            source_packet_file=row.get("source_packet_file", "").strip(),
            owner_doc="docs/requirements/ieee-1516-2010/federation_management_bounded_family.md",
            evidence_refs=_split_semicolon_items(row.get("current_test_id", "")),
        )
        for row in rows
    )


def load_2010_reconciliation_rows(project_root: Path, relative_path: str, owner_doc: str) -> tuple[RequirementMappingRow, ...]:
    rows = _read_csv_rows(project_root / relative_path)
    return tuple(
        RequirementMappingRow(
            edition="2010",
            source_requirement_id=row.get("packet_requirement_id", "").strip(),
            canonical_requirement_id=row.get("curated_requirement_id", "").strip(),
            mapping_kind=row.get("reconciliation_kind", "").strip(),
            mapping_notes=row.get("notes", "").strip(),
            source_packet_file=row.get("source_packet_file", "").strip(),
            owner_doc=owner_doc,
            evidence_refs=_split_semicolon_items(row.get("current_test_id", "")),
        )
        for row in rows
    )


def load_2010_backend_resolution_rows(project_root: Path) -> tuple[BackendResolutionRow, ...]:
    return load_backend_resolution_catalog(project_root / BACKEND_2010_REL).rows


def load_2025_backend_group_rows(project_root: Path) -> tuple[BackendResolutionRow, ...]:
    return tuple(
        row for row in load_backend_resolution_catalog(project_root / BACKEND_2025_REL).rows
        if row.row_kind == "grouped-projection" or row.backend_fields.get("group_kind") == "2025-group"
    )


def load_2025_pitch_row_resolution_rows(project_root: Path) -> tuple[BackendResolutionRow, ...]:
    rows = _read_csv_rows(project_root / PITCH_ROW_2025_REL)
    return tuple(
        BackendResolutionRow(
            edition="2025",
            requirement_id=row.get("id", "").strip(),
            row_kind="requirement-row",
            resolution_type="vendor-route-resolution",
            canonical_owner=row.get("pitch_202x_owner_doc", "").strip(),
            canonical_status=row.get("harmonization_disposition", "").strip(),
            primary_shard="unit-transport-local",
            primary_command=_SHARD_COMMANDS["unit-transport-local"],
            evidence_artifact=row.get("pitch_202x_evidence_packet", "").strip(),
            evidence_refs=_pitch_202x_evidence_refs(row),
            boundary_note=row.get("pitch_202x_scope_note", "").strip(),
            backend_fields={
                "pitch_202x_row_resolution": row.get("pitch_202x_row_resolution", "").strip(),
                "pitch_202x_group_owner": row.get("pitch_202x_group_owner", "").strip(),
                "pitch_202x_vendor_command": row.get("pitch_202x_primary_command", "").strip(),
            },
        )
        for row in rows
    )


def load_2025_pitch_group_resolution_rows(project_root: Path) -> tuple[BackendResolutionRow, ...]:
    rows = _read_csv_rows(project_root / PITCH_GROUP_2025_REL)
    return tuple(
        BackendResolutionRow(
            edition="2025",
            requirement_id=f"{row.get('closure_wave','').strip()}::{row.get('area','').strip()}::{row.get('service_group','').strip()}",
            row_kind="grouped-projection",
            resolution_type="vendor-group-resolution",
            canonical_owner=row.get("pitch_202x_owner_doc", "").strip(),
            canonical_status=row.get("canonical_disposition", "").strip(),
            primary_shard="unit-transport-local",
            primary_command=_SHARD_COMMANDS["unit-transport-local"],
            evidence_artifact=row.get("pitch_202x_evidence_packet", "").strip(),
            evidence_refs=_pitch_202x_evidence_refs(row),
            boundary_note=row.get("pitch_202x_scope_note", "").strip(),
            backend_fields={
                "group_kind": "pitch-202x-group",
                "pitch_202x_resolution": row.get("pitch_202x_resolution", "").strip(),
                "pitch_202x_vendor_command": row.get("pitch_202x_primary_command", "").strip(),
                "closure_wave": row.get("closure_wave", "").strip(),
                "area": row.get("area", "").strip(),
                "service_group": row.get("service_group", "").strip(),
            },
        )
        for row in rows
    )


def load_2025_fi_binding_surface_rows(project_root: Path) -> tuple[BackendResolutionRow, ...]:
    rows = _read_csv_rows(project_root / FI_BINDING_2025_REL)
    return tuple(
        BackendResolutionRow(
            edition="2025",
            requirement_id=row.get("id", "").strip(),
            row_kind="requirement-row",
            resolution_type="binding-route-resolution",
            canonical_owner="docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md",
            canonical_status=row.get("disposition", "").strip(),
            primary_shard="unit-transport-local",
            primary_command="./tools/test-surface run unit-transport-local",
            evidence_artifact=FI_BINDING_2025_REL,
            evidence_refs=(FI_BINDING_2025_REL,),
            boundary_note=row.get("risk_note", "").strip(),
            backend_fields={
                "java_surface": row.get("java_surface", "").strip(),
                "java_methods": row.get("java_methods", "").strip(),
                "cpp_surface": row.get("cpp_surface", "").strip(),
                "cpp_methods": row.get("cpp_methods", "").strip(),
                "fedpro_surface": row.get("fedpro_surface", "").strip(),
                "fedpro_match_or_note": row.get("fedpro_match_or_note", "").strip(),
                "binding_surface_summary": row.get("binding_surface_summary", "").strip(),
            },
        )
        for row in rows
    )
