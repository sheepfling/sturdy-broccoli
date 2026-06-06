from __future__ import annotations

from pathlib import Path

from hla2010.raw_api import API_METADATA
from hla2010.verification import (
    build_requirements_ledger,
    build_verification_plan,
    write_requirements_ledger_csv,
    write_requirements_ledger_json,
)


def test_requirements_ledger_covers_generated_api_surface(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    ledger = build_requirements_ledger(project_root, version="0.13.0")
    expected_rows = sum(len(API_METADATA[interface]) for interface in ("RTIambassador", "FederateAmbassador"))

    assert ledger["summary"]["row_count"] == expected_rows
    assert ledger["summary"]["interface_counts"]["RTIambassador"] == len(API_METADATA["RTIambassador"])
    assert ledger["summary"]["interface_counts"]["FederateAmbassador"] == len(API_METADATA["FederateAmbassador"])
    assert ledger["summary"]["outcome_counts"]["pass"] > 0
    assert ledger["summary"]["outcome_counts"]["partial"] > 0
    assert set(ledger["summary"]["outcome_counts"]).issubset({"pass", "partial", "fail", "not-evidenced"})

    by_method = {(row["interface"], row["method"]): row for row in ledger["rows"]}
    assert by_method[("RTIambassador", "connect")]["outcome"] == "partial"
    assert by_method[("RTIambassador", "sendInteraction")]["outcome"] == "partial"
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["outcome"] == "pass"


def test_requirements_ledger_writers_emit_review_assets(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    json_path = write_requirements_ledger_json(tmp_path / "requirements.json", project_root, version="0.13.0")
    csv_path = write_requirements_ledger_csv(tmp_path / "requirements.csv", project_root, version="0.13.0")

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    assert "requirement_id,interface,method" in csv_path.read_text(encoding="utf-8")


def test_verification_plan_tracks_requirements_ledger_asset():
    plan = build_verification_plan("0.13.0")
    assets = {asset.asset_id: asset for asset in plan.assets}

    assert assets["ASSET-REQUIREMENTS-LEDGER-001"].status == "implemented-slice"
    assert any("requirements_ledger_v0_13.json" in item for item in assets["ASSET-REQUIREMENTS-LEDGER-001"].evidence)
