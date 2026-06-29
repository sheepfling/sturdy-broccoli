from __future__ import annotations

import json
from pathlib import Path

from hla.verification.repo_internal.requirements import (
    build_2010_canonical_requirement_catalog,
    build_2025_canonical_requirement_catalog,
    load_2010_backend_resolution_rows,
    load_2010_fm_reconciliation_rows,
    load_2010_reconciliation_rows,
    load_2025_fi_binding_surface_rows,
    load_2025_pitch_group_resolution_rows,
    load_2025_pitch_row_resolution_rows,
    load_canonical_requirement_catalog,
    survey_requirement_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]
SURVEY = ROOT / "requirements/normalized/row_shape_survey.json"
CANONICAL_2010 = ROOT / "requirements/2010/canonical_requirements.json"
CANONICAL_2025 = ROOT / "requirements/2025/canonical_requirements.json"


def test_requirement_row_shape_survey_checked_in_artifact_matches_live_generation() -> None:
    generated = survey_requirement_artifacts(ROOT).to_mapping()
    checked_in = json.loads(SURVEY.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "requirement-row-shape-survey"
    assert checked_in["entry_count"] == len(checked_in["entries"])

    entries_by_path = {entry["path"]: entry for entry in checked_in["entries"]}
    assert entries_by_path["requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"]["family"] == "canonical-requirement"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"]["family"] == "grouped-view"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv"]["family"] == "backend-resolution"
    assert entries_by_path["requirements/2010/hla1516_1_fm_detailed_reconciliation.csv"]["family"] == "requirement-mapping"
    assert entries_by_path["requirements/2010/canonical_requirements.json"]["family"] == "canonical-requirement"
    assert entries_by_path["requirements/imports/hla_1516_requirements_codebase_packet_v1_0/latest/hla_1516_requirements_master_v1_0.csv"]["family"] == "imported-requirement"


def test_2010_canonical_requirement_catalog_checked_in_artifact_matches_live_generation() -> None:
    generated = build_2010_canonical_requirement_catalog(ROOT).to_mapping()
    checked_in = json.loads(CANONICAL_2010.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "canonical-requirements-catalog"
    assert checked_in["edition"] == "2010"
    assert checked_in["row_count"] > 0

    rows_by_id = {row["requirement_id"]: row for row in checked_in["rows"]}
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["canonical_status"] == "pass"
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["source_document"] == "IEEE 1516.1-2010 (2010 edition)"
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["row_kind"] == "extracted-requirement"
    assert rows_by_id["REQ-OMT-SCHEMA-001"]["canonical_status"] == "implemented-slice"


def test_2025_canonical_requirement_catalog_checked_in_artifact_matches_live_generation() -> None:
    generated = build_2025_canonical_requirement_catalog(ROOT).to_mapping()
    checked_in = json.loads(CANONICAL_2025.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "canonical-requirements-catalog"
    assert checked_in["edition"] == "2025"
    assert checked_in["row_count"] == 691

    rows_by_id = {row["requirement_id"]: row for row in checked_in["rows"]}
    assert rows_by_id["HLA2025-FI-SVC-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/federation_management_bounded_proof.md"
    assert rows_by_id["HLA2025-FI-SVC-001"]["primary_test_shard"] == "unit-python-2025-core"
    assert rows_by_id["HLA2025-OMT-SU-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/omt.md"
    assert rows_by_id["HLA2025-OMT-SU-001"]["primary_test_shard"] == "unit-fom-tooling"
    assert rows_by_id["HLA2025-OMT-CV-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/omt.md"
    assert rows_by_id["HLA2025-FI-CB-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
    assert rows_by_id["HLA2025-FR-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/framework_rules.md"
    assert rows_by_id["HLA2025-FI-RET-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"


def test_2025_canonical_requirement_catalog_loader_reads_checked_in_projection() -> None:
    catalog = load_canonical_requirement_catalog(CANONICAL_2025)

    assert catalog.edition == "2025"
    assert catalog.row_count == len(catalog.rows) == 691
    rows_by_id = {row.requirement_id: row for row in catalog.rows}

    assert rows_by_id["HLA2025-FI-SVC-001"].primary_command == "./tools/test-surface run unit-python-2025-core"
    assert rows_by_id["HLA2025-OMT-SU-001"].primary_command == "./tools/test-surface run unit-fom-tooling"
    assert rows_by_id["HLA2025-FI-CB-001"].canonical_status == "duplicate/umbrella"


def test_2010_fm_reconciliation_loader_reads_typed_mapping_rows() -> None:
    rows = load_2010_fm_reconciliation_rows(ROOT)
    rows_by_id = {row.source_requirement_id: row for row in rows}

    assert len(rows) == 632
    assert rows_by_id["HLA1516.1-FM-4_2-SVC-001"].mapping_kind == "SVC"
    assert rows_by_id["HLA1516.1-FM-4_2-SVC-001"].canonical_requirement_id
    assert rows_by_id["HLA1516.1-FM-4_2-SVC-001"].owner_doc.endswith("federation_management_bounded_family.md")
    assert rows_by_id["HLA1516.1-FM-4_4-001"].evidence_refs


def test_generic_2010_reconciliation_loader_reads_dm_rows() -> None:
    rows = load_2010_reconciliation_rows(
        ROOT,
        "requirements/2010/hla1516_1_dm_detailed_reconciliation.csv",
        "docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md",
    )
    rows_by_id = {row.source_requirement_id: row for row in rows}

    assert len(rows) == 212
    assert rows_by_id["HLA1516.1-DM-5_2-RTIAPI-001"].mapping_kind == "RTI_API"
    assert rows_by_id["HLA1516.1-DM-5_2-RTIAPI-001"].owner_doc.endswith("declaration_management_bounded_family.md")


def test_typed_backend_resolution_loaders_cover_2010_and_2025_companion_surfaces() -> None:
    rows_2010 = load_2010_backend_resolution_rows(ROOT)
    rows_2025_pitch = load_2025_pitch_row_resolution_rows(ROOT)
    groups_2025_pitch = load_2025_pitch_group_resolution_rows(ROOT)
    rows_2025_binding = load_2025_fi_binding_surface_rows(ROOT)

    rows_2010_by_id = {row.requirement_id: row for row in rows_2010}
    assert rows_2010_by_id["HLA1516.1-FM-4.1.5-001"].row_kind == "requirement-row"
    assert rows_2010_by_id["HLA1516.1-FM-4.1.5-001"].resolution_type == "backend-runtime-disposition"
    assert rows_2010_by_id["HLA1516.1-FM-4.1.5-001"].backend_fields["python_runtime_disposition"] == "verified"
    assert rows_2010_by_id["REQ-OMT-SCHEMA-001"].backend_fields["pitch_runtime_disposition"] == "classification-required"
    assert any(row.row_kind == "requirement-row" and row.resolution_type == "vendor-route-resolution" for row in rows_2025_pitch)
    assert any(row.backend_fields["pitch_202x_row_resolution"] == "bounded-fi-overlap-only" for row in rows_2025_pitch)
    assert any(row.row_kind == "grouped-projection" and row.resolution_type == "vendor-group-resolution" for row in groups_2025_pitch)
    assert any(row.backend_fields["pitch_202x_resolution"].startswith("vendor-branded proto HLA 4 / 202X surface") for row in groups_2025_pitch)
    assert any(row.row_kind == "requirement-row" and row.resolution_type == "binding-route-resolution" for row in rows_2025_binding)
    assert any(row.backend_fields["fedpro_surface"] for row in rows_2025_binding)
