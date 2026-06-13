from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_new_fom_package_tool_scaffolds_repo_native_layout(tmp_path: Path) -> None:
    result = subprocess.run(
        ["bash", "./tools/new-fom-package", "target-tracker", "--output-root", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Scaffolded FOM package for target-tracker" in result.stdout
    assert "packages/hla2010-fom-target-tracker/README.md" in result.stdout
    assert "examples/target_tracker_demo.py" in result.stdout
    assert "tests/examples/test_target_tracker_demo.py" in result.stdout

    package_root = tmp_path / "packages" / "hla2010-fom-target-tracker"
    module_root = package_root / "src" / "hla2010_fom_target_tracker"
    assert (package_root / "pyproject.toml").exists()
    assert (package_root / "README.md").exists()
    assert (package_root / "docs" / "README.md").exists()
    assert (module_root / "__init__.py").exists()
    assert (module_root / "resources" / "foms" / "TargetTrackerFOMmodule.xml").exists()
    assert (module_root / "scenarios" / "target_tracker.py").exists()
    assert (module_root / "scenarios" / "target_tracker_factory.py").exists()
    assert (tmp_path / "examples" / "target_tracker_demo.py").exists()
    assert (tmp_path / "tests" / "examples" / "test_target_tracker_demo.py").exists()

    pyproject = (package_root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "hla2010-fom-target-tracker"' in pyproject
    assert 'include = ["hla2010_fom_target_tracker*"]' in pyproject

    scenario_text = (module_root / "scenarios" / "target_tracker.py").read_text(encoding="utf-8")
    assert 'TARGET_TRACKER_OBJECT_CLASS = "HLAobjectRoot.TargetTrackerObject"' in scenario_text
    assert "def run_target_tracker_scenario(" in scenario_text

    example_text = (tmp_path / "examples" / "target_tracker_demo.py").read_text(encoding="utf-8")
    assert "make_target_tracker_factory" in example_text
    assert "run_target_tracker_scenario" in example_text


def test_new_fom_package_refuses_to_overwrite_existing_paths(tmp_path: Path) -> None:
    occupied = tmp_path / "packages" / "hla2010-fom-target-tracker"
    occupied.mkdir(parents=True)

    result = subprocess.run(
        [sys.executable, "scripts/new_fom_package.py", "target-tracker", "--output-root", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "refusing to overwrite existing path" in result.stderr
