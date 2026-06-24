from __future__ import annotations

from pathlib import Path

from scripts.check_upstream_contract import load_json, validate_allowed_differences, validate_snapshot


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = ROOT / "compat" / "upstream_contract"


def test_upstream_contract_snapshot_packet_is_valid() -> None:
    errors: list[str] = []
    errors.extend(validate_allowed_differences(load_json(CONTRACT_ROOT / "allowed_differences.json")))
    for snapshot_path in (
        CONTRACT_ROOT / "v0.1.1" / "ieee1516e.json",
        CONTRACT_ROOT / "v0.1.1" / "ieee1516_2025.json",
    ):
        errors.extend(validate_snapshot(load_json(snapshot_path), path=snapshot_path))
    assert errors == []
