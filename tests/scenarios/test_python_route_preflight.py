from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.typed_json_models import PythonRoutePreflightOutput


ROOT = Path(__file__).resolve().parents[2]


def test_python_route_preflight_json_reports_expected_shape() -> None:
    result = subprocess.run(
        ["python3", "scripts/check_python_route_preflight.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = PythonRoutePreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.tool == "python-verify-routes-preflight"
    assert payload.python_direct == "runnable"
    assert payload.loopback.status in {"ok", "blocked"}
    assert payload.grpc_import.status in {"ok", "blocked"}
    assert payload.python_grpc.status in {"runnable", "blocked"}


def test_tools_python_verify_routes_preflight_runs_script() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "verify-routes-preflight", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = PythonRoutePreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.tool == "python-verify-routes-preflight"
