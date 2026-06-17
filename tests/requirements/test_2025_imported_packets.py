from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "docs/requirements/ieee-1516-2025"
EXECUTABLE_DIR = REQ_DIR / "executable_tests"
ENC_AUTH_DIR = REQ_DIR / "encoding_auth_work_packet"


@pytest.mark.requirements("HLA-X-2025-REQ-001", "HLA-X-2025-FI-002")
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


@pytest.mark.requirements("HLA-X-2025-FI-003", "HLA-X-2025-FI-004")
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
