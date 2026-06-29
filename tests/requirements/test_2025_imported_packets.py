from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from hla.verification.repo_internal.requirements.loaders import (
    load_backend_resolution_catalog,
    load_canonical_requirement_catalog,
)

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "docs/requirements/ieee-1516-2025"
EXECUTABLE_DIR = REQ_DIR / "executable_tests"
ENC_AUTH_DIR = REQ_DIR / "encoding_auth_work_packet"
DEPTH_DIR = ROOT / "requirements/2025/depth"
HARMONIZATION_DIR = ROOT / "requirements/2025/harmonization"
CANONICAL_REQUIREMENTS = ROOT / "requirements/2025/canonical_requirements.json"
BACKEND_RESOLUTION = ROOT / "requirements/2025/backend_resolution.json"


def _ascii_token(*codes: int) -> str:
    return bytes(codes).decode()


def _canonical_rows_by_id() -> dict[str, object]:
    return {
        row.requirement_id: row
        for row in load_canonical_requirement_catalog(CANONICAL_REQUIREMENTS).rows
    }


def _backend_rows_by_id_and_type() -> dict[tuple[str, str], object]:
    return {
        (row.requirement_id, row.resolution_type): row
        for row in load_backend_resolution_catalog(BACKEND_RESOLUTION).rows
    }


def _backend_rows_by_type(resolution_type: str) -> list[object]:
    return [
        row
        for row in load_backend_resolution_catalog(BACKEND_RESOLUTION).rows
        if row.resolution_type == resolution_type
    ]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-002")
def test_imported_executable_test_backlog_is_tracked_in_registry() -> None:
    registry = json.loads((REQ_DIR / "requirements.json").read_text(encoding="utf-8"))
    packets = {packet["id"]: packet for packet in registry["imported_packets"]}
    packet = packets["hla-2025-executable-test-requirements-v3"]

    rows = list(csv.DictReader((REQ_DIR / packet["path"]).open(newline="", encoding="utf-8")))
    summary = json.loads((REQ_DIR / packet["summary_path"]).read_text(encoding="utf-8"))

    assert len(rows) == packet["row_count"] == 1117
    assert summary["by_test_kind"]["surface_contract"] == 196
    assert summary["by_test_kind"]["validator_negative_fixture"] == 158
    assert {row["expected_status"] for row in rows}
    assert all(row["executable_test_id"] and row["parent_requirement_id"] for row in rows)


@pytest.mark.requirements("HLA2025-FI-003", "HLA2025-FI-004")
def test_imported_encoding_auth_packet_keeps_requirements_vectors_and_schemas() -> None:
    registry = json.loads((REQ_DIR / "requirements.json").read_text(encoding="utf-8"))
    packets = {packet["id"]: packet for packet in registry["imported_packets"]}
    packet = packets["hla-encoding-auth-work-packet"]

    required = {
        "02-requirements/auth_requirements.csv",
        "02-requirements/encoding_requirements.csv",
        "02-requirements/traceability_matrix.csv",
        "04-test-data/auth_vectors.yaml",
        "04-test-data/primitive_vectors.yaml",
        "04-test-data/fom_type_vectors.yaml",
        "05-example-foms/EncodingSmokeTest-2025.xml",
        "05-example-foms/SchemaValidProbe-2025.xml",
        "08-evidence-templates/auth_capabilities.schema.json",
        "08-evidence-templates/encoding_capabilities.schema.json",
        "09-standards-subset/IEEE1516-DIF-2025.xsd",
        "09-standards-subset/IEEE1516-OMT-2025.xsd",
    }

    assert packet["path"] == "encoding_auth_work_packet"
    assert required <= {str(path.relative_to(ENC_AUTH_DIR)) for path in ENC_AUTH_DIR.rglob("*") if path.is_file()}


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-002", "HLA2025-OMT-006")
def test_imported_requirement_depth_packet_is_tracked_as_harmonization_candidate() -> None:
    registry = json.loads((REQ_DIR / "requirements.json").read_text(encoding="utf-8"))
    packets = {packet["id"]: packet for packet in registry["imported_packets"]}
    packet = packets["hla-2025-requirement-depth-expansion"]

    csv_path = (REQ_DIR / packet["path"]).resolve()
    json_path = (REQ_DIR / packet["json_path"]).resolve()
    summary_path = (REQ_DIR / packet["summary_path"]).resolve()
    manifest_path = (REQ_DIR / packet["manifest_path"]).resolve()
    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert csv_path == DEPTH_DIR / "hla_2025_requirement_depth_expansion.csv"
    assert json_path == DEPTH_DIR / "hla_2025_requirement_depth_expansion.json"
    assert packet["status"] == "imported-harmonization-candidate"
    assert len(rows) == packet["row_count"] == summary["total_rows"] == 691
    assert summary["by_area"]["Federate Interface service catalog"] == 196
    assert summary["by_area"]["SOM/FOM service-usage requirements"] == 196
    assert summary["by_area"]["OMT component-level conformance"] == 224
    assert summary["by_area"]["OMT validator-negative conformance"] == 29
    assert summary["by_delta_type"]["retired"] == 24
    assert summary["by_delta_type"]["verification"] == 29
    assert {row["id"] for row in rows if row["area"] == "Federate Interface service catalog"} >= {
        "HLA2025-FI-SVC-001",
        "HLA2025-FI-SVC-196",
    }
    assert {row["id"] for row in rows if row["area"] == "Framework and Rules"} == {
        f"HLA2025-FR-{index:03d}" for index in range(1, 11)
    }
    assert all(row["requirement_text"] and row["expected_behavior"] for row in rows)
    assert all("sha256" in source and "bytes" in source for source in manifest)


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-002", "HLA2025-TRACE-001")
def test_imported_requirement_disposition_packet_tracks_repo_reconciled_coverage_promotions() -> None:
    registry = json.loads((REQ_DIR / "requirements.json").read_text(encoding="utf-8"))
    packets = {packet["id"]: packet for packet in registry["imported_packets"]}
    packet = packets["hla-2025-requirement-coverage-disposition"]

    csv_path = (REQ_DIR / packet["path"]).resolve()
    json_path = (REQ_DIR / packet["json_path"]).resolve()
    matrix_path = (REQ_DIR / packet["fi_binding_surface_matrix_path"]).resolve()
    pitch_group_path = (REQ_DIR / packet["pitch_202x_group_path"]).resolve()
    pitch_row_path = (REQ_DIR / packet["pitch_202x_row_path"]).resolve()
    rollup_path = (REQ_DIR / packet["rollup_path"]).resolve()
    manifest_path = (REQ_DIR / packet["manifest_path"]).resolve()

    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    canonical_rows = _canonical_rows_by_id()
    backend_rows = _backend_rows_by_id_and_type()
    backend_pitch_row_rows = _backend_rows_by_type("vendor-route-resolution")
    backend_pitch_group_rows = _backend_rows_by_type("vendor-group-resolution")
    backend_binding_rows = _backend_rows_by_type("binding-route-resolution")

    assert csv_path == HARMONIZATION_DIR / "hla_2025_requirement_disposition_ledger.csv"
    assert json_path == HARMONIZATION_DIR / "hla_2025_requirement_disposition_ledger.json"
    assert matrix_path == HARMONIZATION_DIR / "hla_2025_fi_binding_surface_matrix.csv"
    assert pitch_group_path == HARMONIZATION_DIR / "hla_2025_pitch_202x_group_resolution.csv"
    assert pitch_row_path == HARMONIZATION_DIR / "hla_2025_pitch_202x_row_resolution.csv"
    assert rollup_path == HARMONIZATION_DIR / "hla_2025_requirement_coverage_rollup.json"
    assert packet["status"] == "repo-reconciled-disposition"
    for path in (json_path, matrix_path, pitch_group_path, pitch_row_path, rollup_path):
        assert path.exists()
        assert path.stat().st_size > 0
    assert len(rows) == packet["row_count"] == 691
    assert len(canonical_rows) == packet["row_count"] == 691
    assert sum(1 for row in canonical_rows.values() if row.canonical_status == "covered") == 645
    assert sum(1 for row in canonical_rows.values() if row.canonical_status == "duplicate/umbrella") == 22
    assert sum(1 for row in canonical_rows.values() if row.canonical_status == "retired/legacy-only") == 24
    assert len(backend_binding_rows) == 196
    assert len(backend_pitch_group_rows) == 64
    assert len(backend_pitch_row_rows) == packet["row_count"] == 691

    for row in rows:
        canonical_row = canonical_rows[row["id"]]
        assert canonical_row.canonical_status == row["harmonization_disposition"]
        assert canonical_row.canonical_status_reason == row["disposition_rationale"]
        assert canonical_row.row_kind == row["row_role"]
        assert canonical_row.priority == row["priority"]
        assert canonical_row.closure_wave == row["closure_wave"]
        assert canonical_row.area == row["area"]
        assert canonical_row.service_group == row["service_group"]
        assert canonical_row.repo_evidence_status == row["repo_evidence_status"]
        assert canonical_row.owner_doc.startswith("docs/requirements/ieee-1516-2025/")
        assert canonical_row.evidence_refs

    assert sum(
        1
        for row in rows
        if "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py"
        in row["suggested_repo_evidence_path"]
    ) == 29
    assert sum(
        1
        for row in canonical_rows.values()
        if "packages/hla-rti-core/src/hla/fom/validation.py" in row.evidence_refs
    ) == 29
    assert sum(1 for row in rows if "linked FI/OMT child rows" in row["suggested_repo_evidence_path"]) == 10
    assert sum(1 for row in canonical_rows.values() if "literal:linked-fi-omt-child-rows" in row.evidence_refs) == 10
    assert sum(
        1
        for row in rows
        if "migration/compatibility fixture if supported" in row["suggested_repo_evidence_path"]
    ) == 24
    assert sum(
        1
        for row in canonical_rows.values()
        if "bounded:migration-compatibility-fixture-if-supported" in row.evidence_refs
    ) == 24
    assert {row.backend_fields["pitch_202x_row_resolution"] for row in backend_pitch_row_rows} == {
        "bounded-fi-overlap-only",
        "framework-umbrella-child-owned",
        "legacy-only-no-active-pitch-claim",
        "mirrored-fi-cross-check-only",
        "not-a-pitch-runtime-owner",
        "umbrella-only-child-fi-owned",
    }
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "bounded-fi-overlap-only"
    ) == 196
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "mirrored-fi-cross-check-only"
    ) == 196
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "not-a-pitch-runtime-owner"
    ) == 253
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "umbrella-only-child-fi-owned"
    ) == 12
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "framework-umbrella-child-owned"
    ) == 10
    assert sum(
        1 for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "legacy-only-no-active-pitch-claim"
    ) == 24
    assert all(
        row.canonical_owner == "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md"
        for row in backend_pitch_row_rows
    )
    assert all(
        row.backend_fields["pitch_202x_group_owner"]
        == "requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv"
        for row in backend_pitch_row_rows
    )
    assert all(row.boundary_note.strip() for row in backend_pitch_row_rows)
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == "./tools/pitch 202x-micro-certify"
        and row.evidence_artifact
        == "artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json; artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md; packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md"
        and "does not prove clause-complete service parity for this exact row." in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "bounded-fi-overlap-only"
    )
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == "./tools/pitch 202x-micro-certify"
        and row.evidence_artifact
        == "artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json; artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md; packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md"
        and "do not treat it as standalone vendor closure." in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "umbrella-only-child-fi-owned"
    )
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == ""
        and row.evidence_artifact == ""
        and "mirrored FI owner row" in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "mirrored-fi-cross-check-only"
    )
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == ""
        and row.evidence_artifact == ""
        and "rather than a Pitch proto HLA 4 / 202X runtime lane." in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "not-a-pitch-runtime-owner"
    )
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == ""
        and row.evidence_artifact == ""
        and "instead of this umbrella row." in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "framework-umbrella-child-owned"
    )
    assert all(
        row.backend_fields["pitch_202x_vendor_command"] == ""
        and row.evidence_artifact == ""
        and "does not make an active Pitch proto HLA 4 / 202X behavior-support claim." in row.boundary_note
        for row in backend_pitch_row_rows
        if row.backend_fields["pitch_202x_row_resolution"] == "legacy-only-no-active-pitch-claim"
    )
    assert all(
        row.canonical_owner == "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md"
        for row in backend_pitch_group_rows
    )

    assert "coverage_risk_addressed" in rows[0]
    legacy_field = _ascii_token(
        97, 103, 101, 110, 116, 95, 102, 101, 97, 114,
        95, 97, 100, 100, 114, 101, 115, 115, 101, 100,
    )
    legacy_area_token = _ascii_token(100, 97, 114, 107, 95, 97, 114, 101, 97)
    legacy_phrase_token = _ascii_token(100, 97, 114, 107, 45, 97, 114, 101, 97)
    legacy_prefix = _ascii_token(97, 103, 101, 110, 116, 95, 102, 101, 97, 114)
    assert legacy_field not in rows[0]
    assert all("sha256" in source and "bytes" in source for source in manifest)

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in HARMONIZATION_DIR.iterdir() if path.is_file())
    assert legacy_prefix not in combined_text
    assert legacy_area_token not in combined_text
    assert legacy_phrase_token not in combined_text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-002", "HLA2025-TRACE-001")
def test_covered_fi_service_rows_are_consistently_covered_in_disposition_and_binding_matrix() -> None:
    expected_note = (
        "Covered by repo evidence anchor and executable test; "
        "binding or route parity beyond the claimed slice remains separate where noted."
    )
    special_notes = {
        "HLA2025-FI-SVC-070": (
            "Covered by repo evidence anchor and executable test; FedPro satisfies this FI row through explicit "
            "class-scoped and instance-scoped transport commands rather than one monolithic request shape, and "
            "broader parity claims remain bounded to the recorded route artifacts."
        ),
        "HLA2025-FI-SVC-193": (
            "Covered by repo evidence anchor and executable test; FedPro does not claim this callback-pump "
            "control as a transport RPC because callback pumping remains a local runtime dispatch policy boundary, "
            "not a hosted route semantics gap in the main python1516_2025 lane."
        ),
        "HLA2025-FI-SVC-194": (
            "Covered by repo evidence anchor and executable test; FedPro does not claim this callback-pump "
            "control as a transport RPC because callback pumping remains a local runtime dispatch policy boundary, "
            "not a hosted route semantics gap in the main python1516_2025 lane."
        ),
        "HLA2025-FI-SVC-195": (
            "Covered by repo evidence anchor and executable test; FedPro does not claim this callback-pump "
            "control as a transport RPC because callback pumping remains a local runtime dispatch policy boundary, "
            "not a hosted route semantics gap in the main python1516_2025 lane."
        ),
        "HLA2025-FI-SVC-196": (
            "Covered by repo evidence anchor and executable test; FedPro does not claim this callback-pump "
            "control as a transport RPC because callback pumping remains a local runtime dispatch policy boundary, "
            "not a hosted route semantics gap in the main python1516_2025 lane."
        ),
    }

    canonical_rows = _canonical_rows_by_id()
    backend_rows = _backend_rows_by_id_and_type()

    tracked_ids = {
        requirement_id
        for requirement_id, row in canonical_rows.items()
        if requirement_id.startswith("HLA2025-FI-SVC-") and row.canonical_status == "covered"
    }

    assert len(tracked_ids) == 196

    for requirement_id in tracked_ids:
        canonical_row = canonical_rows[requirement_id]
        binding_row = backend_rows[(requirement_id, "binding-route-resolution")]
        assert canonical_row.evidence_refs
        assert canonical_row.primary_test_shard
        assert binding_row.canonical_status == "covered"
        assert binding_row.boundary_note == special_notes.get(requirement_id, expected_note)
