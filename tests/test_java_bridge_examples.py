from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = PROJECT_ROOT / "examples" / "java_shim_federate.py"


@pytest.mark.parametrize(
    ("edition", "bridge"),
    [
        ("2010", "jpype"),
        ("2010", "py4j"),
        ("2025", "jpype"),
        ("2025", "py4j"),
    ],
)
def test_java_shim_federate_example_runs_for_supported_editions_and_routes(edition: str, bridge: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    completed = subprocess.run(
        [sys.executable, str(EXAMPLE), "--edition", edition, "--bridge", bridge],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["edition"] == edition
    assert payload["bridge"] == bridge
    if edition == "2025":
        assert payload["federate_handle"] is not None
        assert "join_federation_execution" in payload["event_names"]
    else:
        assert "time_advance_grant" in payload["event_names"]
