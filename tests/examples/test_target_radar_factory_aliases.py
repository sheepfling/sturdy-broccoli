from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import workspace_python_bin, workspace_python_env

ROOT = Path(__file__).resolve().parents[2]


def test_target_radar_example_accepts_in_memory_factory_alias() -> None:
    python_bin = workspace_python_bin()
    result = subprocess.run(
        [
            str(python_bin),
            "examples/target_radar_simulation.py",
            "--backend",
            "in-memory",
            "--steps",
            "2",
        ],
        cwd=ROOT,
        env=workspace_python_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("backend=python/in-memory,python/in-memory")
