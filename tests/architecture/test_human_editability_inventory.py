from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "analysis" / "human_editability" / "smell_inventory.json"


def _inventory_checks() -> list[dict[str, object]]:
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert data["version"] == 1
    checks = data["checks"]
    assert isinstance(checks, list)
    return checks


def test_every_smell_row_has_an_id() -> None:
    for index, check in enumerate(_inventory_checks(), start=1):
        check_id = str(check.get("id", "")).strip()
        assert check_id, f"check[{index}] missing id"


def test_every_open_smell_has_a_planned_remediation_workstream() -> None:
    for check in _inventory_checks():
        if check.get("status") != "open":
            continue
        remediation = str(check.get("remediation_workstream", "")).strip()
        assert remediation.startswith("Workstream "), check["id"]


def test_every_closed_smell_has_at_least_one_verification_command_or_test() -> None:
    for check in _inventory_checks():
        if check.get("status") != "closed":
            continue
        verification = check.get("verification", [])
        assert isinstance(verification, list)
        assert any(str(item).strip() for item in verification), check["id"]


def test_human_editability_wrapper_check_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Human editability check passed" in result.stdout
    assert "remaining_open_smells: 0" in result.stdout
    assert "SMELL-SPEC-SOURCE-ROOT-EXCEPTION" not in result.stdout


def test_human_editability_trace_example_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "trace", "timeAdvanceRequest"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "requirement_id: REQ-RTI-TM-8_8-timeAdvanceRequest" in result.stdout
    assert "hla_method: timeAdvanceRequest" in result.stdout
