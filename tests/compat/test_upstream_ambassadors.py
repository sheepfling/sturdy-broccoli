from __future__ import annotations

from pathlib import Path

from scripts.check_upstream_contract import load_json, validate_local_ambassador_contract


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = ROOT / "compat" / "upstream_contract"


def test_local_ambassador_protocols_match_frozen_contract() -> None:
    errors: list[str] = []
    for snapshot_path in (
        CONTRACT_ROOT / "v0.1.1" / "ieee1516e.json",
        CONTRACT_ROOT / "v0.1.1" / "ieee1516_2025.json",
    ):
        errors.extend(validate_local_ambassador_contract(load_json(snapshot_path)))
    assert errors == []
