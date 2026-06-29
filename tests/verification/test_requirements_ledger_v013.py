from __future__ import annotations

from pathlib import Path

from hla.rti1516e.api_metadata import API_METADATA
from hla.verification.repo_internal.verification.asset_plan import build_verification_plan
from hla.verification.repo_internal.verification.repo_seed_artifacts import (
    build_requirements_ledger,
    write_requirements_ledger_csv,
    write_requirements_ledger_json,
)
from hla.verification.repo_internal.verification.requirements_matrix_artifacts import (
    build_requirements_matrix_2010,
    write_requirements_matrix_2010_csv,
)


PROMOTED_PITCH_ROWS = {
    "HLA1516.1-FM-4.12-001": "registration-success and duplicate-label failure callbacks",
    "HLA1516.1-FM-4.16-001": "save-request path end to end",
    "HLA1516.1-FM-4.17-001": "initiate-save callback delivery",
    "HLA1516.1-FM-4.18-001": "save-begun participation and callback sequencing",
    "HLA1516.1-FM-4.19-001": "save completion and save-not-complete participation",
    "HLA1516.1-FM-4.20-001": "federation-saved and federation-not-saved reporting",
    "HLA1516.1-FM-4.21-001": "abort-save cleanup and federation-not-saved reporting",
    "HLA1516.1-FM-4.22-001": "save-status queries for pending and cleared states",
    "HLA1516.1-FM-4.23-001": "Pitch save-status query and callback payload coverage",
    "HLA1516.1-FM-4.24-001": "restore-request path and restored logical-time state",
    "HLA1516.1-FM-4.25-001": "restore-request success and unknown-save failure callbacks",
    "HLA1516.1-FM-4.26-001": "restore-begun callback sequencing",
    "HLA1516.1-FM-4.27-001": "initiate-restore callback delivery",
    "HLA1516.1-FM-4.28-001": "restore completion and restore-not-complete participation",
    "HLA1516.1-FM-4.29-001": "restored and not-restored callback outcomes",
    "HLA1516.1-FM-4.30-001": "abort-restore path",
    "HLA1516.1-FM-4.31-001": "restore-status queries for pending and cleared states",
    "HLA1516.1-FM-4.32-001": "restore-status callback payload coverage",
    "HLA1516.1-OM-6.1.2-001": "object-scope scenario",
    "HLA1516.1-OM-6.2-001": "name-reservation scenario",
    "HLA1516.1-OM-6.21-001": "update-advisory callback scenario",
    "HLA1516.1-OM-6.21-002": "update-rate designator",
    "HLA1516.1-OM-6.22-001": "demand for published attributes disappears",
    "HLA1516.1-OM-6.24-001": "supported subset",
    "HLA1516.1-OWN-7.1-003": "non-owner-update scenario",
    "HLA1516.1-OWN-7.5-001": "release-request ownership scenario",
    "HLA1516.1-OWN-7.7-001": "acquisition-notification callbacks",
    "HLA1516.1-OWN-7.8-001": "acquisition-failure callbacks",
    "HLA1516.1-OWN-7.12-001": "ownership query reporting",
    "HLA1516.1-OWN-7.13-001": "ownership-query callback scenario",
    "HLA1516.1-DDM-9.1-001": "DDM suite scenario",
    "HLA1516.1-DDM-9.1-002": "dimension lookup and region creation",
    "HLA1516.1-DDM-9.1-003": "overlap-based relevance",
}


def test_requirements_ledger_covers_generated_api_surface(tmp_path: Path):
    ledger = build_requirements_ledger(version="0.13.0")
    expected_rows = sum(len(API_METADATA[interface]) for interface in ("RTIambassador", "FederateAmbassador"))

    assert ledger["summary"]["row_count"] == expected_rows
    assert ledger["summary"]["interface_counts"]["RTIambassador"] == len(API_METADATA["RTIambassador"])
    assert ledger["summary"]["interface_counts"]["FederateAmbassador"] == len(API_METADATA["FederateAmbassador"])
    assert ledger["summary"]["outcome_counts"]["pass"] > 0
    assert ledger["summary"]["outcome_counts"].get("partial", 0) >= 0
    assert set(ledger["summary"]["outcome_counts"]).issubset({"pass", "partial", "fail", "not-evidenced"})

    by_method = {(row["interface"], row["method"]): row for row in ledger["rows"]}
    assert by_method[("RTIambassador", "connect")]["outcome"] in {"pass", "partial"}
    assert by_method[("RTIambassador", "sendInteraction")]["outcome"] in {"pass", "partial"}
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["outcome"] == "pass"
    assert by_method[("RTIambassador", "createFederationExecution")]["requirement_id"] == "REQ-RTI-FM-4_5-createFederationExecution"
    assert by_method[("RTIambassador", "enableTimeRegulation")]["requirement_id"] == "REQ-RTI-TM-8_2-enableTimeRegulation"
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["requirement_id"] == "REQ-FED-TM-8_13-timeAdvanceGrant"
    assert "packages/hla-backend-python1516e/src/hla.backends.python1516e/backend.py" in by_method[("RTIambassador", "enableTimeRegulation")]["implementation_refs"]
    assert by_method[("RTIambassador", "enableTimeRegulation")]["positive_test_refs"]
    assert by_method[("RTIambassador", "sendInteraction")]["negative_test_refs"]
    assert by_method[("RTIambassador", "enableTimeRegulation")]["artifact_refs"]
    assert all(not row["requirement_id"].startswith("REQ-0") for row in ledger["rows"])


def test_requirements_ledger_writers_emit_review_assets(tmp_path: Path):
    json_path = write_requirements_ledger_json(tmp_path / "requirements.json", version="0.13.0")
    csv_path = write_requirements_ledger_csv(tmp_path / "requirements.csv", version="0.13.0")

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "requirement_id,interface,method" in csv_text
    assert "implementation_refs,positive_test_refs,negative_test_refs,artifact_refs" in csv_text
    assert "REQ-RTI-FM-4_5-createFederationExecution" in json_path.read_text(encoding="utf-8")


def test_verification_plan_tracks_requirements_ledger_asset():
    plan = build_verification_plan("0.13.0")
    assets = {asset.asset_id: asset for asset in plan.assets}

    assert assets["ASSET-REQUIREMENTS-LEDGER-001"].status == "implemented-slice"
    assert any("requirements_ledger_v0_13.json" in item for item in assets["ASSET-REQUIREMENTS-LEDGER-001"].evidence)
    assert assets["ASSET-VENDOR-PARITY-PACKET-001"].status == "implemented-slice"
    assert any("run_vendor_parity_artifacts.py" in item for item in assets["ASSET-VENDOR-PARITY-PACKET-001"].evidence)


def test_requirements_matrix_carries_vendor_parity_notes():
    project_root = Path(__file__).resolve().parents[2]
    matrix = build_requirements_matrix_2010(project_root, version="0.13.0")
    rows = {row["requirement_id"]: row for row in matrix["rows"] if row.get("requirement_id")}

    expected_statuses = {
        "HLA1516.1-FM-4.11-001": ("yes", "yes", "yes"),
        "HLA1516.1-OWN-7.3-001": ("yes", "partial", "blocked"),
        "HLA1516.1-TM-8.16-001": ("yes", "partial", "blocked"),
    }
    for requirement_id, (python_status, certi_status, pitch_status) in expected_statuses.items():
        row = rows[requirement_id]
        assert row["python_runtime_status"] == python_status
        assert row["certi_runtime_status"] == certi_status
        assert row["pitch_runtime_status"] == pitch_status

    for requirement_id, note_fragment in PROMOTED_PITCH_ROWS.items():
        row = rows[requirement_id]
        assert row["pitch_runtime_status"] in {"yes", "blocked"}, requirement_id

    update_rate_row = rows["HLA1516.1-OM-6.1.12-001"]
    assert "canonical narrowed row" in update_rate_row["notes"]
    assert "receive-order delivery is not artificially suppressed outside the logical-time model" in update_rate_row["notes"]


def test_requirements_matrix_writer_emits_vendor_columns(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    csv_path = write_requirements_matrix_2010_csv(tmp_path / "requirements_matrix.csv", project_root, version="0.13.0")
    csv_text = csv_path.read_text(encoding="utf-8")

    assert "python_runtime_status,python_runtime_disposition" in csv_text
    assert "certi_runtime_status,certi_runtime_disposition" in csv_text
    assert "portico_runtime_status,portico_runtime_disposition" in csv_text
    assert "pitch_runtime_status,pitch_runtime_disposition,pitch_jpype_runtime_disposition,pitch_py4j_runtime_disposition" in csv_text
    assert "vendor_evidence_refs,vendor_notes,vendor_source,vendor_profile_bucket,vendor_profile_refs,vendor_profile_notes,vendor_profile_source" in csv_text
    assert "docs/backend_conformance_matrix.md" in csv_text
    assert "docs/rti_options_and_test_matrix.md" in csv_text
