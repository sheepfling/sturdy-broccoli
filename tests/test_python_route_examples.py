from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = PROJECT_ROOT / "examples" / "python_route_federate.py"


@pytest.mark.parametrize(
    ("edition", "backend"),
    [
        ("2010", "python1516e"),
        ("2025", "python1516_2025"),
    ],
)
def test_python_route_federate_example_runs_for_supported_editions(edition: str, backend: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    completed = subprocess.run(
        [sys.executable, str(EXAMPLE), "--edition", edition],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["edition"] == edition
    assert payload["backend"] == backend
    assert payload["runtime_backend"] is not None
    assert payload["federate_handle"] is not None
    assert "join_federation_execution" in payload["event_names"]
