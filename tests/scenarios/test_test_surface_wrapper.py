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
    assert "./tools/test-surface recommend" in result.stdout
    assert "./tools/test-surface run fast" in result.stdout
    assert "./tools/test-surface run python-routes" in result.stdout
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
    assert lane_ids == ["fast", "repo-green", "python-routes", "vendor", "matrix"]


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
