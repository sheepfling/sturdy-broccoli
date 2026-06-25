from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_tools_test_surface_help_describes_inventory_and_run_lanes() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/test-surface inventory" in result.stdout
    assert "./tools/test-surface validate" in result.stdout
    assert "./tools/test-surface recommend" in result.stdout
    assert "./tools/test-surface run smoke" in result.stdout
    assert "./tools/test-surface run fast" in result.stdout
    assert "./tools/test-surface run repo-green-units" in result.stdout
    assert "./tools/test-surface run unit-foundation" in result.stdout
    assert "./tools/test-surface run unit-python-core" in result.stdout
    assert "./tools/test-surface run unit-federate-examples" in result.stdout
    assert "./tools/test-surface run unit-fom-tooling" in result.stdout
    assert "./tools/test-surface run unit-python-2025-core" in result.stdout
    assert "./tools/test-surface run unit-transport-local" in result.stdout
    assert "./tools/test-surface run unit-scenarios-light" in result.stdout
    assert "./tools/test-surface run python1516_2025-main" in result.stdout
    assert "./tools/test-surface run python-routes" in result.stdout
    assert "./tools/test-surface run python1516_2025-routes" in result.stdout
    assert "./tools/test-surface run matrix" in result.stdout


def test_tools_test_surface_inventory_json_lists_canonical_lanes() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "inventory", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    lane_ids = [row["id"] for row in payload["lanes"]]
    assert lane_ids == [
        "smoke",
        "fast",
        "repo-green",
        "repo-green-units",
        "unit-foundation",
        "unit-python-core",
        "unit-federate-examples",
        "unit-fom-tooling",
        "unit-python-2025-core",
        "unit-transport-local",
        "unit-scenarios-light",
        "python1516_2025-main",
        "python-routes",
        "python1516_2025-routes",
        "vendor",
        "matrix",
    ]


def test_tools_test_surface_validate_json_reports_manifest_path() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "validate", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["manifest"].endswith("testing/test_surface_manifest.json")
    assert payload["errors"] == []


def test_tools_test_surface_inventory_fails_fast_on_invalid_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "invalid_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "lanes": [
                    {
                        "id": "broken",
                        "title": "broken",
                        "description": "broken",
                        "owner_command": ["./tools/test-surface", "run", "broken"],
                        "include_lanes": ["missing", "missing"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", "tools/test-surface", "inventory", "--json"],
        cwd=ROOT,
        env={
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "HLA2010_TEST_SURFACE_MANIFEST": str(manifest_path),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "test surface manifest invalid:" in result.stderr
    assert "includes 'missing' more than once" in result.stderr
    assert "includes unknown lane 'missing'" in result.stderr


def test_tools_test_surface_run_smoke_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "smoke", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "smoke"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-smoke"]
    assert payload["steps"][0]["status"] == "planned"
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_fast_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "fast", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "fast"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["status"] == "planned"
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_foundation_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-foundation", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-foundation"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["bash", "./tools/test-focus", "run", "foundation"]
    assert payload["steps"][1]["argv"] == [
        "./tools/test",
        "tests/test_operator_surface_policy.py",
        "tests/test_documentation_policy.py",
        "tests/test_tools_test_wrapper.py",
        "tests/test_tools_python_wrapper.py",
        "tests/scenarios/test_test_surface_wrapper.py",
        "tests/scenarios/test_ci_green_wrappers.py",
        "tests/test_backend_wrapper_policy.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_foundation_uses_bash_for_non_executable_wrapper() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-foundation", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["steps"][0]["argv"] == ["bash", "./tools/test-focus", "run", "foundation"]


def test_tools_test_surface_run_unit_federate_examples_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-federate-examples", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-federate-examples"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == [
        "./tools/test",
        "tests/test_tools_federate_cli_wrapper.py",
        "tests/test_operator_surface_policy.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_repo_green_units_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "repo-green-units", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "repo-green-units"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert [step["lane"] for step in payload["steps"]] == [
        "unit-foundation",
        "unit-python-core",
        "unit-federate-examples",
        "unit-fom-tooling",
        "unit-python-2025-core",
        "unit-transport-local",
        "unit-scenarios-light",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_routes_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python-routes", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python-routes"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-routes-preflight"]
    assert payload["steps"][1]["argv"] == ["./tools/python", "verify-routes"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_main_2025_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python1516_2025-main", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python1516_2025-main"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-main-2025"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_routes_2025_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python1516_2025-routes", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python1516_2025-routes"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-routes-preflight"]
    assert payload["steps"][1]["argv"] == ["./tools/python", "verify-routes-2025"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_matrix_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "matrix", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "matrix"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/compliance", "generate"]
    assert payload["steps"][1]["argv"] == ["python3", "scripts/run_spec2025_finish_line.py"]
    assert payload["steps"][2]["argv"] == ["./tools/compliance", "discover", "--show-backlog"]
    assert payload["steps"][3]["argv"] == ["./tools/section8-gate"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()
