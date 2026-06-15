from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

import pytest
from conftest import REPO_ROOT, load_json_fixture, read_repo_text
from tests.doc_test_helpers import resolve_fixture_snippet


ROOT = REPO_ROOT
INVENTORY_PATH = ROOT / "analysis" / "human_editability" / "smell_inventory.json"
REQUIREMENTS_SURFACE_MANIFEST_PATH = ROOT / "requirements" / "surface_manifest.json"
REQUIREMENTS_SOURCE_PATH = ROOT / "requirements" / "source_of_truth.json"


@dataclass(frozen=True)
class InventoryCheck:
    check_id: str
    status: str
    remediation_workstream: str
    verification: tuple[str, ...]

    @classmethod
    def from_mapping(cls, row: dict[str, object]) -> InventoryCheck:
        verification = row.get("verification", [])
        return cls(
            check_id=str(row.get("id", "")).strip(),
            status=str(row.get("status", "")).strip(),
            remediation_workstream=str(row.get("remediation_workstream", "")).strip(),
            verification=tuple(str(item).strip() for item in verification) if isinstance(verification, list) else (),
        )


@dataclass(frozen=True)
class HumanEditabilityCommandCase:
    case_id: str
    argv: tuple[object, ...]
    must_contain: tuple[object, ...]
    must_not_contain: tuple[object, ...]

    @classmethod
    def from_mapping(cls, row: dict[str, object]) -> HumanEditabilityCommandCase:
        argv = row.get("argv", [])
        must_contain = row.get("must_contain", [])
        must_not_contain = row.get("must_not_contain", [])
        return cls(
            case_id=str(row.get("id", "")).strip(),
            argv=tuple(argv) if isinstance(argv, list) else (),
            must_contain=tuple(must_contain) if isinstance(must_contain, list) else (),
            must_not_contain=tuple(must_not_contain) if isinstance(must_not_contain, list) else (),
        )


@dataclass(frozen=True)
class RequirementsSurfaceManifest:
    active_authored: tuple[str, ...]
    generated: tuple[str, ...]
    reference_provenance: tuple[str, ...]
    packet_entrypoints: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> RequirementsSurfaceManifest:
        return cls(
            active_authored=tuple(str(path) for path in payload["active_authored"]),
            generated=tuple(str(path) for path in payload["generated"]),
            reference_provenance=tuple(str(path) for path in payload["reference_provenance"]),
            packet_entrypoints=tuple(str(path) for path in payload["packet_entrypoints"]),
        )


@dataclass(frozen=True)
class RequirementsRegistryBinding:
    federate_interface: str

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> RequirementsRegistryBinding:
        return cls(federate_interface=str(payload["federate_interface"]))


@dataclass(frozen=True)
class RequirementsRegistrySpec:
    spec_id: str

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> RequirementsRegistrySpec:
        return cls(spec_id=str(payload["spec_id"]))


@dataclass(frozen=True)
class RequirementsRegistry:
    specs: tuple[RequirementsRegistrySpec, ...]
    active_bindings: RequirementsRegistryBinding

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> RequirementsRegistry:
        return cls(
            specs=tuple(RequirementsRegistrySpec.from_mapping(spec) for spec in payload["specs"]),
            active_bindings=RequirementsRegistryBinding.from_mapping(payload["active_bindings"]),
        )


@dataclass(frozen=True)
class RequirementsSource:
    registry: RequirementsRegistry

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> RequirementsSource:
        return cls(
            registry=RequirementsRegistry.from_mapping(payload["requirement_id_registry"])
        )


def _inventory_checks() -> list[InventoryCheck]:
    data = json.loads(read_repo_text(INVENTORY_PATH))
    assert data["version"] == 1
    checks = data["checks"]
    assert isinstance(checks, list)
    return [InventoryCheck.from_mapping(check) for check in checks]


def _requirements_surface_manifest() -> RequirementsSurfaceManifest:
    data = json.loads(read_repo_text(REQUIREMENTS_SURFACE_MANIFEST_PATH))
    assert data["version"] == 1
    return RequirementsSurfaceManifest.from_mapping(data)


def _requirements_source() -> RequirementsSource:
    data = json.loads(read_repo_text(REQUIREMENTS_SOURCE_PATH))
    assert data["version"] == 1
    return RequirementsSource.from_mapping(data)


def _command_cases() -> list[HumanEditabilityCommandCase]:
    data = load_json_fixture("human_editability_commands.json")
    commands = data["commands"]
    assert isinstance(commands, list)
    return [HumanEditabilityCommandCase.from_mapping(case) for case in commands]


def _run_case(case: HumanEditabilityCommandCase) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [resolve_fixture_snippet(part) for part in case.argv],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_every_smell_row_has_an_id() -> None:
    for index, check in enumerate(_inventory_checks(), start=1):
        assert check.check_id, f"check[{index}] missing id"


def test_every_open_smell_has_a_planned_remediation_workstream() -> None:
    for check in _inventory_checks():
        if check.status != "open":
            continue
        assert check.remediation_workstream.startswith("Workstream "), check.check_id


def test_every_closed_smell_has_at_least_one_verification_command_or_test() -> None:
    for check in _inventory_checks():
        if check.status != "closed":
            continue
        assert any(item for item in check.verification), check.check_id


def test_requirements_surface_manifest_paths_exist_and_do_not_overlap() -> None:
    data = _requirements_surface_manifest()
    seen: dict[str, str] = {}
    for group_name in (
        "active_authored",
        "generated",
        "reference_provenance",
        "packet_entrypoints",
    ):
        paths = getattr(data, group_name)
        assert paths, group_name
        for rel_path in paths:
            assert (ROOT / rel_path).exists(), rel_path
            assert rel_path not in seen, f"{rel_path} listed in both {seen.get(rel_path)} and {group_name}"
            seen[rel_path] = group_name
    assert "requirements/active_service_rows.csv" in data.active_authored
    assert "requirements/family_seed_rows.csv" in data.active_authored
    assert "requirements/source_of_truth.json" in data.active_authored
    assert "requirements/requirement_id_registry.yaml" in data.generated
    assert "requirements/traceability_matrix.csv" in data.generated
    assert "requirements/surface_manifest.json" in data.generated
    source = _requirements_source()
    assert any(spec.spec_id == "HLA1516.1-2010" for spec in source.registry.specs)
    assert source.registry.active_bindings.federate_interface == "HLA1516.1-2010"
    generated_registry_text = read_repo_text("requirements/requirement_id_registry.yaml")
    assert "active_bindings:" in generated_registry_text
    assert "active_binding_editions:" in generated_registry_text
    assert "selected_editions:" in generated_registry_text
    assert "specs:" in generated_registry_text
    assert "federate_interface: HLA1516.1-2010" in generated_registry_text
    assert "  - 2010" in generated_registry_text


@pytest.mark.parametrize("case", _command_cases(), ids=lambda case: case.case_id)
def test_human_editability_command_surfaces(case: HumanEditabilityCommandCase) -> None:
    result = _run_case(case)
    assert result.returncode == 0, result.stderr
    for snippet in case.must_contain:
        assert resolve_fixture_snippet(snippet) in result.stdout
    for snippet in case.must_not_contain:
        assert resolve_fixture_snippet(snippet) not in result.stdout


def test_human_editability_script_bootstraps_source_checkout() -> None:
    result = subprocess.run(
        ["python3", "scripts/human_editability.py", "requirements-flow"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Human editability requirements flow" in result.stdout
