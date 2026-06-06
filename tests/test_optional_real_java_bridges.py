from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from hla2010.java_runtime import discover_java_tool
from hla2010.testing.scenarios import run_basic_federate_scenario

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = PROJECT_ROOT / "java_shims" / "hla-rti1516e-shim" / "tools" / "build_java_shim.py"


def _build_shim_jar(tmp_path: Path) -> Path:
    javac = discover_java_tool("javac")
    jar = discover_java_tool("jar")
    if javac is None or jar is None:
        pytest.skip("JDK javac/jar not available")
    try:
        probe = subprocess.run([javac, "-version"], capture_output=True, check=False, text=True)
    except OSError:
        pytest.skip("JDK javac is not executable")
    if probe.returncode != 0:
        pytest.skip("JDK javac is not usable on this host")
    out = tmp_path / "hla-rti1516e-shim.jar"
    subprocess.run([sys.executable, str(BUILD_SCRIPT), "--output", str(out)], check=True)
    return out


def test_java_shim_source_compiles(tmp_path):
    jar = _build_shim_jar(tmp_path)
    assert jar.exists()
    assert jar.stat().st_size > 0


def test_optional_jpype_backend_can_run_against_java_shim_jar(tmp_path):
    jpype = pytest.importorskip("jpype")  # noqa: F841
    jar = _build_shim_jar(tmp_path)
    from hla2010.backends.jpype_backend import JPypeConfig, rti_ambassador

    summary = run_basic_federate_scenario(
        lambda: rti_ambassador(JPypeConfig(classpath=[str(jar)], shutdown_jvm_on_close=False)),
        federation_name="optional-jpype-shim",
    )
    assert "time_advance_grant" in summary["event_names"]


def test_optional_py4j_backend_can_run_against_java_shim_jar(tmp_path):
    pytest.importorskip("py4j")
    jar = _build_shim_jar(tmp_path)

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway
    from hla2010.backends.py4j_backend import Py4JConfig, rti_ambassador

    port = launch_gateway(classpath=str(jar), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    try:
        gateway.start_callback_server()
        summary = run_basic_federate_scenario(
            lambda: rti_ambassador(Py4JConfig(gateway=gateway)),
            federation_name="optional-py4j-shim",
        )
        assert "time_advance_grant" in summary["event_names"]
    finally:
        gateway.shutdown()
