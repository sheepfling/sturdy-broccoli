from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_shim_routes_help_mentions_cpp_doctor() -> None:
    result = subprocess.run(
        ["bash", "tools/shim-routes", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/shim-routes java doctor" in result.stdout
    assert "./tools/shim-routes cpp doctor" in result.stdout
    assert "./tools/shim-routes cpp certify-core --edition 2010 --artifact standard-shim --transports pybind,grpc" in result.stdout
