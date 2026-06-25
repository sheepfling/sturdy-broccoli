from __future__ import annotations

import sys
import importlib.util
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_test_surface_manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_test_surface_manifest", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_validate_test_surface_manifest_accepts_checked_in_manifest() -> None:
    errors = MODULE.validate_manifest(ROOT / "testing" / "test_surface_manifest.json")
    assert errors == []


def test_validate_test_surface_manifest_rejects_duplicate_unknown_and_cycle(tmp_path: Path) -> None:
    manifest = {
        "lanes": [
            {
                "id": "alpha",
                "title": "alpha",
                "description": "alpha",
                "owner_command": ["./tools/test-surface", "run", "alpha"],
                "include_lanes": ["beta", "beta", "missing"],
            },
            {
                "id": "beta",
                "title": "beta",
                "description": "beta",
                "owner_command": ["./tools/test-surface", "run", "beta"],
                "include_lanes": ["gamma"],
            },
            {
                "id": "gamma",
                "title": "gamma",
                "description": "gamma",
                "owner_command": ["./tools/test-surface", "run", "gamma"],
                "include_lanes": ["alpha"],
            },
            {
                "id": "dup",
                "title": "dup",
                "description": "dup",
                "owner_command": ["./tools/test-surface", "run", "dup"],
                "commands": [["./tools/python", "verify-fast"]],
            },
            {
                "id": "dup",
                "title": "dup 2",
                "description": "dup 2",
                "owner_command": ["./tools/test-surface", "run", "dup2"],
                "commands": [["./tools/python", "verify-smoke"]],
            },
        ]
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    errors = MODULE.validate_manifest(path)

    assert "duplicate lane id: dup" in errors
    assert "lane 'alpha' includes 'beta' more than once" in errors
    assert "lane 'alpha' includes unknown lane 'missing'" in errors
    assert any(error.startswith("include_lanes cycle detected:") for error in errors)


def test_validate_test_surface_manifest_rejects_mixed_or_empty_lane_definitions(tmp_path: Path) -> None:
    manifest = {
        "lanes": [
            {
                "id": "mixed",
                "title": "mixed",
                "description": "mixed",
                "owner_command": ["./tools/test-surface", "run", "mixed"],
                "commands": [["./tools/python", "verify-fast"]],
                "include_lanes": ["leaf"],
            },
            {
                "id": "empty",
                "title": "empty",
                "description": "empty",
                "owner_command": ["./tools/test-surface", "run", "empty"],
            },
            {
                "id": "leaf",
                "title": "leaf",
                "description": "leaf",
                "owner_command": ["./tools/test-surface", "run", "leaf"],
                "commands": [["./tools/python", "verify-smoke"]],
            },
        ]
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    errors = MODULE.validate_manifest(path)

    assert "lane 'mixed' cannot declare both commands and include_lanes" in errors
    assert "lane 'empty' must declare commands or include_lanes" in errors


def test_validate_test_surface_manifest_writes_artifacts(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    result = subprocess.run(
        ["python3", "scripts/validate_test_surface_manifest.py"],
        cwd=ROOT,
        env={
            **os.environ,
            "HLA2010_TEST_SURFACE_ARTIFACT_DIR": str(artifact_dir),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    json_path = artifact_dir / "validate_manifest.json"
    md_path = artifact_dir / "validate_manifest.md"
    assert json_path.is_file()
    assert md_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["manifest"].endswith("testing/test_surface_manifest.json")
    markdown = md_path.read_text(encoding="utf-8")
    assert "# Test Surface Manifest Validation" in markdown
    assert "No manifest errors detected." in markdown
