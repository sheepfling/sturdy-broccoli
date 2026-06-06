from __future__ import annotations

from pathlib import Path

from hla2010.raw_api import API_METADATA
from hla2010.verification import (
    build_service_conformance_matrix,
    build_verification_plan,
    write_service_conformance_matrix_csv,
    write_service_conformance_matrix_json,
    write_service_conformance_summary_markdown,
)


def test_service_by_service_conformance_matrix_covers_generated_api_surface(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    matrix = build_service_conformance_matrix(project_root, version="0.13.0")
    expected_rows = sum(len(API_METADATA[interface]) for interface in ("RTIambassador", "FederateAmbassador"))

    assert matrix["summary"]["row_count"] == expected_rows
    assert matrix["summary"]["interface_counts"]["RTIambassador"] == len(API_METADATA["RTIambassador"])
    assert matrix["summary"]["interface_counts"]["FederateAmbassador"] == len(API_METADATA["FederateAmbassador"])
    assert matrix["summary"]["status_counts"]["reference-implemented-tested"] > 0
    assert matrix["summary"]["status_counts"]["reference-implemented-untested"] > 0

    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}
    assert by_method[("RTIambassador", "connect")]["section"] == "1516.1-2010 §4.2"
    assert by_method[("RTIambassador", "sendInteraction")]["python_backend_entrypoint"] is True
    assert by_method[("RTIambassador", "sendInteraction")]["negative_evidence"]
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["callback_helper"] is True


def test_service_conformance_matrix_writers_emit_review_assets(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    json_path = write_service_conformance_matrix_json(tmp_path / "matrix.json", project_root, version="0.13.0")
    csv_path = write_service_conformance_matrix_csv(tmp_path / "matrix.csv", project_root, version="0.13.0")
    md_path = write_service_conformance_summary_markdown(tmp_path / "matrix.md", project_root, version="0.13.0")

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    assert "row_id,interface,method" in csv_path.read_text(encoding="utf-8")
    assert "Service-by-service conformance matrix v0.13.0" in md_path.read_text(encoding="utf-8")


def test_verification_plan_now_tracks_executable_mom_matrix_and_conformance_matrix():
    plan = build_verification_plan("0.13.0")
    assets = {asset.asset_id: asset for asset in plan.assets}

    assert assets["REQ-MOM-NEG-001"].status == "implemented-slice"
    assert any("test_mom_negative_matrix_parametrized_v013.py" in item for item in assets["REQ-MOM-NEG-001"].evidence)
    assert assets["ASSET-CONFORMANCE-MATRIX-001"].status == "implemented-slice"
    assert any("service_conformance_matrix_v0_13.json" in item for item in assets["ASSET-CONFORMANCE-MATRIX-001"].evidence)
