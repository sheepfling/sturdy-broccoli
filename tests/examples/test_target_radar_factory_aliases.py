from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_target_radar_example_accepts_in_memory_factory_alias() -> None:
    python_bin = ROOT / ".venv" / "bin" / "python"
    subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
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
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("backend=python/in-memory,python/in-memory")
