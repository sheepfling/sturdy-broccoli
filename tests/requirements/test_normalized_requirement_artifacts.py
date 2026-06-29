from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil

from hla.verification.repo_internal.requirements import (
    build_2010_canonical_requirement_catalog,
    build_2010_canonical_row_triage,
    build_2010_projection_requirement_catalog,
    build_2025_canonical_requirement_catalog,
    load_2010_canonical_backend_requirement_rows,
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
CANONICAL_2010_CSV = ROOT / "requirements/2010/canonical_requirements.csv"
CANONICAL_2025_CSV = ROOT / "requirements/2025/canonical_requirements.csv"
BACKEND_2010_CSV = ROOT / "requirements/2010/backend_resolution.csv"
BACKEND_2025_CSV = ROOT / "requirements/2025/backend_resolution.csv"
TRIAGE_2010 = ROOT / "requirements/2010/canonical_row_triage.json"
PROJECTION_2010 = ROOT / "requirements/2010/canonical_projection_rows.json"


def test_requirement_row_shape_survey_checked_in_artifact_matches_live_generation() -> None:
    generated = survey_requirement_artifacts(ROOT).to_mapping()
    checked_in = json.loads(SURVEY.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "requirement-row-shape-survey"
    assert checked_in["entry_count"] == len(checked_in["entries"])

    entries_by_path = {entry["path"]: entry for entry in checked_in["entries"]}
    assert entries_by_path["requirements/2010/canonical_requirements.csv"]["family"] == "canonical-requirement"
    assert entries_by_path["requirements/2025/canonical_requirements.csv"]["family"] == "canonical-requirement"
    assert entries_by_path["requirements/2010/backend_resolution.csv"]["family"] == "backend-resolution"
    assert entries_by_path["requirements/2010/backend_resolution.json"]["family"] == "backend-resolution"
    assert entries_by_path["requirements/2010/backend_resolution.json"]["classification_basis"] == "canonical backend-resolution companion surface"
    assert entries_by_path["requirements/2025/backend_resolution.csv"]["family"] == "backend-resolution"
    assert entries_by_path["requirements/2010/canonical_row_triage.json"]["family"] == "projection"
    assert entries_by_path["requirements/2010/canonical_row_triage.json"]["classification_basis"] == "2010 canonical row normalization triage projection over canonical truth"
    assert entries_by_path["requirements/2010/canonical_projection_rows.json"]["family"] == "projection"
    assert entries_by_path["requirements/2010/canonical_projection_rows.json"]["classification_basis"] == "2010 demoted rollup projection over canonical truth"
    assert entries_by_path["requirements/2010/traceability_matrix.csv"]["family"] == "projection"
    assert entries_by_path["requirements/2010/hla1516_1_priority_backend_resolution.csv"]["family"] == "projection"
    assert entries_by_path["requirements/2010/hla1516_1_fm_detailed_reconciliation.csv"]["family"] == "mapping-bridge"
    assert entries_by_path["requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv"]["family"] == "import-history"
    assert entries_by_path["requirements/2010/hla_1516_master_harmonization_index_v1_0.csv"]["family"] == "import-history"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"]["family"] == "historical"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"]["classification_basis"] == "legacy row-shaped 2025 closeout projection"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"]["family"] == "grouped-view"
    assert entries_by_path["requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv"]["family"] == "backend-resolution"
    assert entries_by_path["requirements/2010/canonical_requirements.json"]["family"] == "canonical-requirement"
    assert entries_by_path["requirements/imports/hla_1516_requirements_codebase_packet_v1_0/latest/hla_1516_requirements_master_v1_0.csv"]["family"] == "imported-requirement"


def test_2010_canonical_requirement_catalog_checked_in_artifact_matches_live_generation() -> None:
    generated = build_2010_canonical_requirement_catalog(ROOT).to_mapping()
    checked_in = json.loads(CANONICAL_2010.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "canonical-requirements-catalog"
    assert checked_in["edition"] == "2010"
    assert checked_in["row_count"] == 880

    rows_by_id = {row["requirement_id"]: row for row in checked_in["rows"]}
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["canonical_status"] == "pass"
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["source_document"] == "IEEE 1516.1-2010 (2010 edition)"
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["row_kind"] == "extracted-requirement"
    assert rows_by_id["HLA1516.2-DT-001"]["canonical_status"] == "pass"
    assert rows_by_id["REQ-RTI-SS-10_11-getAttributeHandle"]["owner_doc"] == "docs/requirements/ieee-1516-2010/support_services_bounded_family.md"
    assert rows_by_id["REQ-RTI-SS-10_11-getAttributeHandle"]["primary_test_shard"] == "unit-python-core"
    assert rows_by_id["REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded"]["owner_doc"] == "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md"
    assert rows_by_id["REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded"]["primary_test_shard"] == "unit-scenarios-light"
    assert "AREA-1516.1-4" not in rows_by_id
    assert "REQ-OMT-4-omt_components" not in rows_by_id
    assert "REQ-MOM-TABLE-001" not in rows_by_id


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


def test_2010_canonical_row_triage_checked_in_artifact_matches_live_generation() -> None:
    generated = build_2010_canonical_row_triage(ROOT).to_mapping()
    checked_in = json.loads(TRIAGE_2010.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "canonical-row-triage"
    assert checked_in["edition"] == "2010"
    assert checked_in["row_count"] == 950
    assert checked_in["decision_counts"] == {
        "keep_in_canonical": 880,
        "move_to_projection": 70,
    }

    rows_by_id = {row["requirement_id"]: row for row in checked_in["rows"]}
    assert rows_by_id["AREA-1516.1-4"]["triage_decision"] == "move_to_projection"
    assert rows_by_id["REQ-OMT-4-omt_components"]["triage_decision"] == "move_to_projection"
    assert rows_by_id["REQ-MOM-TABLE-001"]["triage_decision"] == "move_to_projection"
    assert rows_by_id["REQ-FED-DM-5_10-startRegistrationForObjectClass"]["triage_decision"] == "keep_in_canonical"
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["triage_decision"] == "keep_in_canonical"


def test_2010_projection_requirement_catalog_checked_in_artifact_matches_live_generation() -> None:
    generated = build_2010_projection_requirement_catalog(ROOT).to_mapping()
    checked_in = json.loads(PROJECTION_2010.read_text(encoding="utf-8"))

    assert checked_in == generated
    assert checked_in["artifact"] == "projection-requirements-catalog"
    assert checked_in["edition"] == "2010"
    assert checked_in["row_count"] == 70

    rows_by_id = {row["requirement_id"]: row for row in checked_in["rows"]}
    assert rows_by_id["AREA-1516.1-4"]["row_kind"] == "section-area"
    assert rows_by_id["REQ-OMT-4-omt_components"]["row_kind"] == "omt-area"
    assert rows_by_id["REQ-MOM-TABLE-001"]["row_kind"] == "verification-slice"


def test_2010_typed_requirement_surfaces_load_from_checked_in_canonical_truth_without_matrix_bootstrap(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "requirements" / "2010").mkdir(parents=True, exist_ok=True)

    shutil.copy2(CANONICAL_2010, repo_root / "requirements" / "2010" / "canonical_requirements.json")
    shutil.copy2(BACKEND_2010_CSV.with_suffix(".json"), repo_root / "requirements" / "2010" / "backend_resolution.json")
    shutil.copy2(TRIAGE_2010, repo_root / "requirements" / "2010" / "canonical_row_triage.json")
    shutil.copy2(PROJECTION_2010, repo_root / "requirements" / "2010" / "canonical_projection_rows.json")

    canonical = build_2010_canonical_requirement_catalog(repo_root)
    backend = load_2010_backend_resolution_rows(repo_root)
    triage = build_2010_canonical_row_triage(repo_root)
    projection = build_2010_projection_requirement_catalog(repo_root)

    assert canonical.row_count == 880
    assert len(backend) == 880
    assert triage.row_count == 950
    assert projection.row_count == 70


def test_canonical_requirement_csv_truth_surfaces_share_one_schema_across_editions() -> None:
    with CANONICAL_2010_CSV.open(newline="", encoding="utf-8") as handle:
        rows_2010 = list(csv.DictReader(handle))
        header_2010 = list(rows_2010[0].keys())
    with CANONICAL_2025_CSV.open(newline="", encoding="utf-8") as handle:
        rows_2025 = list(csv.DictReader(handle))
        header_2025 = list(rows_2025[0].keys())

    assert header_2010 == header_2025
    assert header_2010 == [
        "edition",
        "requirement_id",
        "source_document",
        "clause",
        "page",
        "area",
        "service_group",
        "service_or_check",
        "priority",
        "closure_wave",
        "requirement_text",
        "normative_level",
        "row_kind",
        "parent_requirement_id",
        "canonical_status",
        "canonical_status_reason",
        "owner_doc",
        "primary_test_shard",
        "primary_command",
        "evidence_refs",
        "boundary_note",
        "source_trace_strength",
        "repo_evidence_status",
        "tags",
    ]
    assert len(rows_2010) == 880
    assert len(rows_2025) == 691


def test_backend_resolution_csv_truth_surfaces_share_one_schema_across_editions() -> None:
    with BACKEND_2010_CSV.open(newline="", encoding="utf-8") as handle:
        rows_2010 = list(csv.DictReader(handle))
        header_2010 = list(rows_2010[0].keys())
    with BACKEND_2025_CSV.open(newline="", encoding="utf-8") as handle:
        rows_2025 = list(csv.DictReader(handle))
        header_2025 = list(rows_2025[0].keys())

    assert header_2010 == header_2025
    assert header_2010 == [
        "edition",
        "requirement_id",
        "row_kind",
        "resolution_type",
        "canonical_owner",
        "canonical_status",
        "primary_shard",
        "primary_command",
        "evidence_artifact",
        "evidence_refs",
        "boundary_note",
        "backend_fields",
    ]
    assert len(rows_2010) == 880
    assert len(rows_2025) == 913


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
    assert rows_2010_by_id["HLA1516.2-DT-001"].backend_fields["pitch_runtime_disposition"] == "classification-required"
    assert any(row.row_kind == "requirement-row" and row.resolution_type == "vendor-route-resolution" for row in rows_2025_pitch)
    assert any(row.backend_fields["pitch_202x_row_resolution"] == "bounded-fi-overlap-only" for row in rows_2025_pitch)
    assert any(row.row_kind == "grouped-projection" and row.resolution_type == "vendor-group-resolution" for row in groups_2025_pitch)


def test_2010_canonical_backend_requirement_loader_joins_leaf_truth_and_backend_companion() -> None:
    rows = load_2010_canonical_backend_requirement_rows(ROOT)
    rows_by_id = {row.requirement_id: row for row in rows}

    assert len(rows) == 880
    assert "AREA-1516.1-4" not in rows_by_id
    assert "REQ-MOM-TABLE-001" not in rows_by_id
    assert "REQ-SAVE-RESTORE-001" not in rows_by_id

    fm_row = rows_by_id["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]
    assert fm_row.source_document == "IEEE 1516.1-2010 (2010 edition)"
    assert fm_row.row_kind == "service-requirement"
    assert fm_row.owner_doc == "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md"
    assert fm_row.primary_test_shard == "unit-scenarios-light"
    assert fm_row.backend_fields["python_runtime_disposition"] == "verified"
    assert fm_row.backend_fields["pitch_runtime_disposition"] == "verified"

    dt_row = rows_by_id["HLA1516.2-DT-001"]
    assert dt_row.row_kind == "extracted-requirement"
    assert dt_row.service_or_check == "OMT parser shall preserve logical-time and datatype metadata used by the active catalog"
    assert dt_row.backend_fields["python_runtime_disposition"] == "verified"
    assert dt_row.backend_fields["pitch_runtime_disposition"] == "classification-required"
