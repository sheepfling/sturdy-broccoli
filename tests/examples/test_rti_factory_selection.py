from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rti_factory_selection_example_script_runs() -> None:
    python_bin = ROOT / ".venv" / "bin" / "python"
    subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    result = subprocess.run(
        [str(python_bin), "examples/rti_factory_selection.py", "--name", "in-memory"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "installed factories:" in result.stdout
    assert "- python [python-reference]" in result.stdout
    assert "selected factory: python -> backend=python/in-memory" in result.stdout


def test_rti_factory_selection_example_script_json_probe_output() -> None:
    python_bin = ROOT / ".venv" / "bin" / "python"
    result = subprocess.run(
        [str(python_bin), "examples/rti_factory_selection.py", "--name", "python", "--probe", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_name"] == "python"
    assert "in-memory" in payload["selectable_names"]
    assert payload["backend_info"]["kind"] == "python/in-memory"
    assert payload["probe"]["available"] is True
