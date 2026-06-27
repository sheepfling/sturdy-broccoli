from __future__ import annotations

"""Verification tests for the IEEE/HLA 2010 editorial-edition requirements matrix."""

import csv
from pathlib import Path

from hla.verification.repo_internal.verification.requirements_matrix_artifacts import (
    build_requirements_matrix_2010,
    write_requirements_matrix_2010_csv,
    write_requirements_matrix_2010_json,
)


def test_requirements_matrix_2010_covers_section_areas_service_rows_and_verification_slices(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")

    assert matrix["summary"]["row_count"] > 0
    assert matrix["summary"]["kind_counts"]["section-area"] >= 9
    assert matrix["summary"]["kind_counts"]["service-requirement"] > 0
    assert matrix["summary"]["kind_counts"]["extracted-requirement"] > 0
    assert matrix["summary"]["kind_counts"]["verification-slice"] > 0
    assert "IEEE 1516.1-2010 (2010 edition)" in matrix["summary"]["documents"]
    assert "IEEE 1516.2-2010 (2010 edition)" in matrix["summary"]["documents"]

    by_id = {row["matrix_id"]: row for row in matrix["rows"]}
    assert by_id["AREA-1516.1-4"]["status"] in {"pass", "partial", "not-evidenced", "fail"}
    assert by_id["AREA-1516.1-11"]["status"] in {"pass", "partial"}
    assert by_id["REQ-RTI-FM-4_5-createFederationExecution"]["kind"] == "service-requirement"
    assert by_id["REQ-MOM-OBSERVER-001"]["kind"] == "verification-slice"
    assert by_id["REQ-MOM-OBSERVER-001"]["positive_test_refs"]
    assert by_id["REQ-OMT-4-omt_components"]["kind"] == "omt-area"
    assert by_id["REQ-OMT-4_2-object_class_structure"]["status"] in {"pass", "partial"}
    assert by_id["REQ-OMT-4_1-object_model_identification"]["status"] == "pass"
    assert by_id["REQ-OMT-4_8-user_supplied_tag_table"]["status"] == "pass"
    assert by_id["REQ-OMT-Annex_E-schema"]["status"] == "pass"
    assert by_id["REQ-OMT-Annex_E-schema"]["positive_test_refs"]
    assert by_id["REQ-OMT-SCHEMA-001"]["status"] == "implemented-slice"
    assert by_id["REQ-OMT-SCHEMA-001"]["positive_test_refs"]
    assert by_id["HLA1516.1-DM-5.2-001"]["kind"] == "extracted-requirement"
    assert "publishObjectClassAttributes" in by_id["HLA1516.1-DM-5.2-001"]["linked_methods"]
    assert by_id["HLA1516.1-TM-8.2-002"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.2-003"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.5-002"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.5-003"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.8-002"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.8-003"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.16-001"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.19-001"]["status"] == "pass"
    assert by_id["HLA1516.1-TM-8.2-002"]["negative_test_refs"] == []
    assert by_id["HLA1516.1-TM-8.2-003"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-TM-8.8-003"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-FM-4.25-001"]["positive_test_refs"]
    assert by_id["HLA1516-RULE-001"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.2-EFF-001"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.5-EFF-001"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.9-EFF-001"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.10-EFF-001"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.15-002"]["status"] == "pass"
    assert by_id["HLA1516.1-FM-4.15-002"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-FM-4.15-002"]["negative_test_refs"]
    assert by_id["HLA1516.1-FM-4.17-001"]["negative_test_refs"]
    assert by_id["HLA1516.1-FM-4.31-001"]["negative_test_refs"]
    assert by_id["HLA1516.1-OWN-7.7-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OWN-7.7-002"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-OWN-7.7-002"]["negative_test_refs"]
    assert by_id["HLA1516.1-OWN-7.9-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OWN-7.9-002"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-OWN-7.9-002"]["negative_test_refs"]
    assert by_id["HLA1516.1-MOM-11.3-006"]["status"] == "pass"
    assert by_id["HLA1516.1-MOM-11.3-006"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-MOM-11.3-006"]["negative_test_refs"]
    assert by_id["HLA1516.1-MOM-11.5-003"]["status"] == "pass"
    assert by_id["HLA1516.1-MOM-11.5-003"]["positive_test_refs"] == []
    assert by_id["HLA1516.1-MOM-11.5-003"]["negative_test_refs"]
    assert by_id["HLA1516.1-OM-6.10-003"]["kind"] == "extracted-requirement"
    assert by_id["HLA1516.1-OM-6.10-003"]["status"] in {"pass", "partial"}
    assert by_id["HLA1516.1-OM-6.10-005"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.12-005"]["status"] == "pass"
    assert by_id["HLA1516.1-DM-5.1.6-001"]["status"] == "pass"
    assert by_id["HLA1516.1-DM-5.1.6-001"]["supported_subset_for"] == ""
    assert by_id["HLA1516.1-OM-6.1.11-001"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.1.11-001"]["supported_subset_for"] == ""
    assert by_id["HLA1516.1-OM-6.1.12-001"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.1.12-001"]["supported_subset_for"] == ""
    assert by_id["HLA1516.1-OM-6.1.10-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.1.10-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.1.10-004"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.1.10-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.1.10-002",
        "HLA1516.1-OM-6.1.10-003",
        "HLA1516.1-OM-6.1.10-004",
    ]
    assert by_id["REQ-OM-TRANSPORT-BEST-EFFORT-001"]["status"] == "implemented-slice"
    assert by_id["HLA1516.1-OM-6.23-001"]["status"] == "partial"
    assert by_id["HLA1516.1-OM-6.23-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.23-002",
        "HLA1516.1-OM-6.23-003",
    ]
    assert by_id["HLA1516.1-OM-6.23-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.23-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.24-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.24-002",
        "HLA1516.1-OM-6.24-003",
        "HLA1516.1-OM-6.24-004",
    ]
    assert by_id["HLA1516.1-OM-6.24-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.24-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.24-004"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.25-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.25-002",
        "HLA1516.1-OM-6.25-003",
    ]
    assert by_id["HLA1516.1-OM-6.25-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.25-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.26-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.26-002",
        "HLA1516.1-OM-6.26-003",
        "HLA1516.1-OM-6.26-004",
    ]
    assert by_id["HLA1516.1-OM-6.26-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.26-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.26-004"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.27-001"]["status"] == "partial"
    assert by_id["HLA1516.1-OM-6.27-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.27-002",
        "HLA1516.1-OM-6.27-003",
    ]
    assert by_id["HLA1516.1-OM-6.27-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.27-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.28-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.28-002",
        "HLA1516.1-OM-6.28-003",
        "HLA1516.1-OM-6.28-004",
    ]
    assert by_id["HLA1516.1-OM-6.28-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.28-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.28-004"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.29-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.29-002",
        "HLA1516.1-OM-6.29-003",
    ]
    assert by_id["HLA1516.1-OM-6.29-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.29-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.30-001"]["supported_subset_for"] == [
        "HLA1516.1-OM-6.30-002",
        "HLA1516.1-OM-6.30-003",
        "HLA1516.1-OM-6.30-004",
    ]
    assert by_id["HLA1516.1-OM-6.30-002"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.30-003"]["status"] == "pass"
    assert by_id["HLA1516.1-OM-6.30-004"]["status"] == "pass"


def test_requirements_matrix_2010_uses_edition_qualified_2010_documents() -> None:
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")

    for row in matrix["rows"]:
        requirement_id = row.get("requirement_id") or row.get("matrix_id") or ""
        document = row.get("document") or ""
        if str(requirement_id).startswith("HLA1516.1-"):
            assert document == "IEEE 1516.1-2010 (2010 edition)", requirement_id
        if str(requirement_id).startswith("HLA1516.2-"):
            assert document == "IEEE 1516.2-2010 (2010 edition)", requirement_id


def test_requirements_matrix_2010_writers_emit_review_assets(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    json_path = write_requirements_matrix_2010_json(tmp_path / "requirements-matrix-2010.json", project_root, version="0.13.0")
    csv_path = write_requirements_matrix_2010_csv(tmp_path / "requirements-matrix-2010.csv", project_root, version="0.13.0")

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "matrix_id,kind,document,section_ref,title,requirement_id" in csv_text
    assert "REQ-MOM-OBSERVER-001" in csv_text
    assert "REQ-OMT-4-omt_components" in csv_text
    assert "HLA1516.1-DM-5.2-001" in csv_text


def test_checked_in_requirements_matrix_2010_csv_matches_current_generator_for_bounded_omt_rows() -> None:
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")
    generated_by_id = {row["matrix_id"]: row for row in matrix["rows"]}
    checked_in_rows = list(csv.DictReader((project_root / "analysis" / "compliance" / "requirements_matrix_2010.csv").open()))
    checked_in_by_id = {row["matrix_id"]: row for row in checked_in_rows}

    assert "planned" not in {row["status"] for row in checked_in_rows}

    for requirement_id in (
        "REQ-OMT-4_1-object_model_identification",
        "REQ-OMT-4_8-user_supplied_tag_table",
        "REQ-OMT-Annex_E-schema",
        "REQ-OMT-SCHEMA-001",
    ):
        assert checked_in_by_id[requirement_id]["status"] == generated_by_id[requirement_id]["status"]
        assert checked_in_by_id[requirement_id]["title"] == generated_by_id[requirement_id]["title"]


def test_repo_does_not_keep_stale_duplicate_2010_direct_matrix_artifact() -> None:
    project_root = Path(__file__).resolve().parents[2]

    assert not (project_root / "analysis" / "compliance" / "requirements_matrix_2010.direct.csv").exists()


def test_requirements_matrix_2010_keeps_bounded_family_summary_rows_partial() -> None:
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")
    by_id = {row["matrix_id"]: row for row in matrix["rows"]}

    for requirement_id in (
        "HLA1516.1-FM-001",
        "HLA1516.1-TM-001",
        "HLA1516.1-DDM-001",
        "HLA1516.1-OWN-001",
        "HLA1516.1-SUP-001",
        "HLA1516.1-MOM-001",
    ):
        assert by_id[requirement_id]["status"] == "partial"


def test_clause4_requirements_matrix_rows_use_shared_harness_backing_refs() -> None:
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")
    by_id = {row["matrix_id"]: row for row in matrix["rows"]}

    selected_rows = {
        "REQ-RTI-FM-4_7-listFederationExecutions",
        "REQ-FED-FM-4_8-reportFederationExecutions",
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_23-federationSaveStatusResponse",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }
    disallowed_prefixes = (
        "tests/backends/",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/scenarios/test_startup_sync_fom_java_translation_v09.py",
    )
    allowed_prefixes = (
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py",
        "tests/scenarios/test_federation_management_backend_matrix.py",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
        "tests/scenarios/test_federation_management_backend_matrix.py::",
        "tests/transport/test_grpc_transport_2025.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )

    for requirement_id in selected_rows:
        row = by_id[requirement_id]
        refs = row["positive_test_refs"]
        assert refs, requirement_id
        assert not any(ref.startswith(disallowed_prefixes) for ref in refs), (requirement_id, refs)
        assert all(ref.startswith(allowed_prefixes) for ref in refs), (requirement_id, refs)


def test_clause7_requirements_matrix_rows_use_shared_harness_backing_refs() -> None:
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")
    by_id = {row["matrix_id"]: row for row in matrix["rows"]}

    selected_rows = {
        "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied",
        "REQ-RTI-OWN-7_17-queryAttributeOwnership",
        "REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption",
        "REQ-FED-OWN-7_18-attributeIsOwnedByRTI",
    }
    disallowed_refs = {
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    }
    allowed_prefixes = (
        "tests/scenarios/test_ownership_management_backend_matrix.py",
        "tests/scenarios/test_ownership_management_backend_matrix.py::",
        "tests/transport/test_grpc_transport_2025.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )

    for requirement_id in selected_rows:
        row = by_id[requirement_id]
        refs = row["positive_test_refs"]
        assert refs, requirement_id
        assert not any(ref in disallowed_refs for ref in refs), (requirement_id, refs)
        assert all(ref.startswith(allowed_prefixes) for ref in refs), (requirement_id, refs)
