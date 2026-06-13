from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_examples_tool_wrapper_runs_workspace_backed_factory_selection() -> None:
    subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    result = subprocess.run(
        ["bash", "./tools/examples", "rti-factory-selection", "--name", "in-memory", "--probe", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_name"] == "python"
    assert payload["backend_info"]["kind"] == "python/in-memory"
    assert payload["probe"]["available"] is True


def test_examples_tool_wrapper_runs_workspace_backed_target_radar_alias_path() -> None:
    result = subprocess.run(
        ["bash", "./tools/examples", "target-radar", "--backend", "in-memory", "--steps", "2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("backend=python/in-memory,python/in-memory")


def test_examples_tool_wrapper_runs_workspace_backed_minimal_demo_alias_path() -> None:
    result = subprocess.run(
        ["bash", "./tools/examples", "minimal-fom-demo", "--backend", "in-memory"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("backend=python/in-memory,python/in-memory")
