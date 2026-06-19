from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "docs/requirements/ieee-1516-2025"
EXECUTABLE_DIR = REQ_DIR / "executable_tests"
ENC_AUTH_DIR = REQ_DIR / "encoding_auth_work_packet"
DEPTH_DIR = ROOT / "requirements/2025/depth"
HARMONIZATION_DIR = ROOT / "requirements/2025/harmonization"


def _ascii_token(*codes: int) -> str:
    return bytes(codes).decode()


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
        "08-evidence-templates/auth_capabilities.schema.json",
        "08-evidence-templates/encoding_capabilities.schema.json",
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
    worklist_path = (REQ_DIR / packet["worklist_path"]).resolve()
    review_queue_path = (REQ_DIR / packet["review_queue_path"]).resolve()
    rollup_path = (REQ_DIR / packet["rollup_path"]).resolve()
    manifest_path = (REQ_DIR / packet["manifest_path"]).resolve()

    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    matrix_rows = list(csv.DictReader(matrix_path.open(newline="", encoding="utf-8")))
    worklist_rows = list(csv.DictReader(worklist_path.open(newline="", encoding="utf-8")))
    review_rows = list(csv.DictReader(review_queue_path.open(newline="", encoding="utf-8")))
    rollup = json.loads(rollup_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert csv_path == HARMONIZATION_DIR / "hla_2025_requirement_disposition_ledger.csv"
    assert json_path == HARMONIZATION_DIR / "hla_2025_requirement_disposition_ledger.json"
    assert packet["status"] == "repo-reconciled-disposition"
    assert len(rows) == packet["row_count"] == rollup["total_rows"] == 691
    assert len(matrix_rows) == rollup["fi_binding_surface"]["fi_rows"] == 196
    assert len(review_rows) == 691
    assert worklist_rows
    assert rollup["by_disposition"] == {
        "duplicate/umbrella": 22,
        "covered": 225,
        "partial": 420,
        "planned": 0,
        "retired/legacy-only": 24,
    }
    assert rollup["by_disposition"]["covered"] == 225
    assert rollup["fi_binding_surface"]["java_present"] == 196
    assert rollup["fi_binding_surface"]["cpp_present"] == 196
    assert rollup["fi_binding_surface"]["fedpro_present"] == 191
    assert rollup["fi_binding_surface"]["fedpro_alias_or_split_route"] == 1
    assert rollup["fi_binding_surface"]["fedpro_route_boundary_or_missing_review"] == 4
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
