from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "analysis" / "human_editability" / "smell_inventory.json"
REQUIREMENTS_SURFACE_MANIFEST_PATH = ROOT / "requirements" / "surface_manifest.json"


def _inventory_checks() -> list[dict[str, object]]:
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert data["version"] == 1
    checks = data["checks"]
    assert isinstance(checks, list)
    return checks


def _requirements_surface_manifest() -> dict[str, object]:
    data = json.loads(REQUIREMENTS_SURFACE_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert data["version"] == 1
    return data


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


def test_requirements_surface_manifest_paths_exist_and_do_not_overlap() -> None:
    data = _requirements_surface_manifest()
    seen: dict[str, str] = {}
    for group_name in (
        "active_authored",
        "generated",
        "reference_provenance",
        "packet_entrypoints",
    ):
        paths = data[group_name]
        assert isinstance(paths, list)
        assert paths, group_name
        for rel_path in paths:
            assert isinstance(rel_path, str)
            assert (ROOT / rel_path).exists(), rel_path
            assert rel_path not in seen, f"{rel_path} listed in both {seen.get(rel_path)} and {group_name}"
            seen[rel_path] = group_name
    assert "requirements/traceability_matrix.csv" in data["active_authored"]


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


def test_human_editability_requirement_example_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "requirement", "REQ-RTI-TM-8_8-timeAdvanceRequest"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Human editability requirement for REQ-RTI-TM-8_8-timeAdvanceRequest" in result.stdout
    assert "Active requirement row:" in result.stdout
    assert "Generated trace row:" in result.stdout
    assert "traceability_matrix.csv" in result.stdout


def test_human_editability_front_doors_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "front-doors"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Human editability front doors" in result.stdout
    assert "Spec front door:" in result.stdout
    assert "Python RTI front door:" in result.stdout
    assert "Python RTI service-edit front door:" in result.stdout
    assert "RTI factory front door:" in result.stdout
    assert "Requirements front door:" in result.stdout
    assert "docs/spec_reading_map.md" in result.stdout
    assert "docs/python_rti_reading_map.md" in result.stdout
    assert "docs/python_rti_edit_one_service.md" in result.stdout
    assert "docs/rti_factory_reading_map.md" in result.stdout
    assert "docs/requirements_trace_one_method.md" in result.stdout
    assert "docs/requirements_edit_one_row.md" in result.stdout
    assert "requirements/surface_manifest.json" in result.stdout


def test_human_editability_front_doors_python_rti_topic_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "front-doors", "python-rti"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Python RTI front door:" in result.stdout
    assert "service_registry.py" in result.stdout
    assert "time_public_services.py" in result.stdout
    assert "Requirements front door:" not in result.stdout


def test_human_editability_front_doors_python_rti_service_topic_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "front-doors", "python-rti-service"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Python RTI service-edit front door:" in result.stdout
    assert "docs/python_rti_edit_one_service.md" in result.stdout
    assert "support_lookup.py" in result.stdout
    assert "test_python_rti_service_registry.py" in result.stdout
    assert "Requirements front door:" not in result.stdout


def test_human_editability_front_doors_requirements_trace_topic_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "front-doors", "requirements-trace"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Requirements front door:" in result.stdout
    assert "docs/requirements_trace_one_method.md" in result.stdout
    assert "docs/requirements_edit_one_row.md" in result.stdout
    assert "support_lookup.py" in result.stdout
    assert "test_support_services_backend_matrix.py" in result.stdout
    assert "Python RTI front door:" not in result.stdout


def test_human_editability_front_doors_rti_factories_topic_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "front-doors", "rti-factories"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "RTI factory front door:" in result.stdout
    assert "tools/rti-factories" in result.stdout
    assert "scripts/rti_factories.py" in result.stdout
    assert "Python RTI front door:" not in result.stdout


def test_human_editability_requirements_surfaces_runs() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "requirements-surfaces"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Human editability requirements surfaces" in result.stdout
    assert "requirements/surface_manifest.json" in result.stdout
    assert "Active authored:" in result.stdout
    assert "Generated:" in result.stdout
    assert "Reference / provenance:" in result.stdout
    assert "requirements/traceability_matrix.csv" in result.stdout
