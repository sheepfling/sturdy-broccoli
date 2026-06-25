from __future__ import annotations

import importlib.util
import subprocess
import sys
import os
from pathlib import Path
from typing import Any

import pytest

from hla.bridges.java.common import discover_java_tool
from hla.verification import run_basic_federate_scenario

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = PROJECT_ROOT / "java_shims" / "hla-rti1516e-shim" / "tools" / "build_java_shim.py"
BUILD_2025_SCRIPT = PROJECT_ROOT / "java_shims" / "hla-rti1516-2025-standard-shim" / "tools" / "build_standard_shim.py"


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    subprocess.run([sys.executable, str(BUILD_SCRIPT), "--output", str(out)], check=True, env=env)
    return out


def _build_standard_2025_shim_jar() -> tuple[Any, Path]:
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
    module = _load_module(BUILD_2025_SCRIPT, "optional_real_java_bridges_build_standard_2025")
    subprocess.run([sys.executable, str(BUILD_2025_SCRIPT)], cwd=PROJECT_ROOT, check=True)
    return module, module.JAR_PATH


def _py4j_probe(gateway: Any, class_name: str) -> Any:
    current = gateway.jvm
    for part in class_name.split("."):
        current = getattr(current, part)
    return current()


def test_java_shim_source_compiles(tmp_path):
    jar = _build_shim_jar(tmp_path)
    assert jar.exists()
    assert jar.stat().st_size > 0


def test_optional_jpype_backend_can_run_against_java_shim_jar(tmp_path):
    jpype = pytest.importorskip("jpype")  # noqa: F841
    jar = _build_shim_jar(tmp_path)
    from hla.bridges.java.jpype import JPypeConfig, rti_ambassador

    summary = run_basic_federate_scenario(
        lambda: rti_ambassador(JPypeConfig(classpath=[str(jar)], shutdown_jvm_on_close=False)),
        federation_name="optional-jpype-shim",
    )
    assert "time_advance_grant" in summary["event_names"]


def test_optional_jpype_java_encoder_oracle_matches_python_string_codecs(tmp_path):
    pytest.importorskip("jpype")
    jar = _build_shim_jar(tmp_path)

    from hla.bridges.java.jpype import JPypeConfig, rti_ambassador
    from hla.rti1516e.encoding import HLAASCIIstring, HLAfixedArray, HLAfixedRecord, HLAoctet, HLAunicodeString

    ambassador = rti_ambassador(JPypeConfig(classpath=[str(jar)], shutdown_jvm_on_close=False))
    try:
        oracle = ambassador.backend.java_encoder_oracle
        assert oracle is not None
        assert oracle.encode_ascii_string("radar") == HLAASCIIstring("radar").encode()
        assert oracle.encode_unicode_string("λ") == HLAunicodeString("λ").encode()
        assert oracle.encode_python_data_element(
            HLAfixedRecord([HLAASCIIstring("left"), HLAunicodeString("λ")])
        ) == HLAfixedRecord([HLAASCIIstring("left"), HLAunicodeString("λ")]).encode()
        assert oracle.encode_python_data_element(
            HLAfixedArray([HLAoctet(1), HLAoctet(2), HLAoctet(3)])
        ) == HLAfixedArray([HLAoctet(1), HLAoctet(2), HLAoctet(3)]).encode()
    finally:
        ambassador.close()


def test_optional_py4j_backend_can_run_against_java_shim_jar(tmp_path):
    pytest.importorskip("py4j")
    jar = _build_shim_jar(tmp_path)

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway

    from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
    from hla.bridges.java.py4j import Py4JConfig, rti_ambassador

    port = launch_gateway(classpath=str(jar), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    try:
        reset_py4j_callback_client(gateway)
        summary = run_basic_federate_scenario(
            lambda: rti_ambassador(Py4JConfig(gateway=gateway)),
            federation_name="optional-py4j-shim",
        )
        assert "time_advance_grant" in summary["event_names"]
    finally:
        gateway.shutdown()


def test_optional_py4j_java_encoder_oracle_matches_python_string_codecs(tmp_path):
    pytest.importorskip("py4j")
    jar = _build_shim_jar(tmp_path)

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway

    from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
    from hla.bridges.java.py4j import Py4JConfig, rti_ambassador
    from hla.rti1516e.encoding import HLAASCIIstring, HLAfixedArray, HLAfixedRecord, HLAoctet, HLAunicodeString

    port = launch_gateway(classpath=str(jar), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    try:
        reset_py4j_callback_client(gateway)
        ambassador = rti_ambassador(Py4JConfig(gateway=gateway))
        try:
            oracle = ambassador.backend.java_encoder_oracle
            assert oracle is not None
            assert oracle.encode_ascii_string("radar") == HLAASCIIstring("radar").encode()
            assert oracle.encode_unicode_string("λ") == HLAunicodeString("λ").encode()
            assert oracle.encode_python_data_element(
                HLAfixedRecord([HLAASCIIstring("left"), HLAunicodeString("λ")])
            ) == HLAfixedRecord([HLAASCIIstring("left"), HLAunicodeString("λ")]).encode()
            assert oracle.encode_python_data_element(
                HLAfixedArray([HLAoctet(1), HLAoctet(2), HLAoctet(3)])
            ) == HLAfixedArray([HLAoctet(1), HLAoctet(2), HLAoctet(3)]).encode()
        finally:
            ambassador.close()
    finally:
        gateway.shutdown()


def test_optional_jpype_2025_java_encoder_oracle_uses_live_java_classes_and_bytes() -> None:
    pytest.importorskip("jpype")
    module, jar = _build_standard_2025_shim_jar()

    from hla.bridges.java.jpype import JPypeConfig, create_jpype_backend
    from hla.rti1516_2025.auth import HLAnoCredentials, HLAplainTextPassword
    from hla.rti1516_2025.encoding import HLAASCIIstring, HLAfixedRecord, HLAoctet, HLAunicodeString

    backend = create_jpype_backend(
        JPypeConfig(
            classpath=[str(jar)],
            shutdown_jvm_on_close=False,
            java_api_profile="2025",
        )
    )
    try:
        oracle = backend.java_encoder_oracle
        assert oracle is not None
        probe = backend.bridge.JClass(f"{module.PACKAGE}.StandardShimProbe")()

        ascii_element = oracle.materialize(HLAASCIIstring("radar"))
        unicode_element = oracle.materialize(HLAunicodeString("λ"))
        record_element = oracle.materialize(HLAfixedRecord([HLAoctet(7), HLAASCIIstring("space")]))

        assert probe.className(ascii_element) == f"{module.PACKAGE}.StandardShimHLAASCIIstring"
        assert probe.className(unicode_element) == f"{module.PACKAGE}.StandardShimHLAunicodeString"
        assert probe.className(record_element) == f"{module.PACKAGE}.StandardShimHLAfixedRecord"
        assert backend.bridge.to_python_bytes(probe.encode(ascii_element)) == HLAASCIIstring("radar").encode()
        assert backend.bridge.to_python_bytes(probe.encode(unicode_element)) == HLAunicodeString("λ").encode()
        assert backend.bridge.to_python_bytes(probe.encode(record_element)) == HLAfixedRecord(
            [HLAoctet(7), HLAASCIIstring("space")]
        ).encode()

        exploding_ascii = type(
            "HLAASCIIstring",
            (),
            {
                "getValue": lambda self: "vendor-only",
                "toByteArray": lambda self: (_ for _ in ()).throw(AssertionError("python toByteArray should not run")),
            },
        )()
        java_bytes = backend.converter.to_backend(exploding_ascii, expected_type_name="byte[]")
        assert backend.bridge.to_python_bytes(java_bytes) == HLAASCIIstring("vendor-only").encode()

        no_credentials = backend.converter.to_backend(HLAnoCredentials(), expected_type_name="Credentials")
        password_credentials = backend.converter.to_backend(
            HLAplainTextPassword("secret"),
            expected_type_name="Credentials",
        )
        assert probe.credentialClassName(no_credentials) == "hla.rti1516_2025.auth.HLAnoCredentials"
        assert probe.credentialType(no_credentials) == "HLAnoCredentials"
        assert backend.bridge.to_python_bytes(probe.credentialData(no_credentials)) == b""
        assert probe.credentialClassName(password_credentials) == "hla.rti1516_2025.auth.HLAplainTextPassword"
        assert probe.credentialType(password_credentials) == "HLAplainTextPassword"
        assert backend.bridge.to_python_bytes(probe.credentialData(password_credentials)) == HLAplainTextPassword(
            "secret"
        ).data
    finally:
        backend.close()


def test_optional_py4j_2025_java_encoder_oracle_uses_live_java_classes_and_bytes() -> None:
    pytest.importorskip("py4j")
    module, jar = _build_standard_2025_shim_jar()

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway

    from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
    from hla.bridges.java.py4j import Py4JConfig, create_py4j_backend
    from hla.rti1516_2025.auth import HLAnoCredentials, HLAplainTextPassword
    from hla.rti1516_2025.encoding import HLAASCIIstring, HLAfixedRecord, HLAoctet, HLAunicodeString

    port = launch_gateway(classpath=str(jar), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    try:
        reset_py4j_callback_client(gateway)
        backend = create_py4j_backend(
            Py4JConfig(
                gateway=gateway,
                java_api_profile="2025",
            )
        )
        try:
            oracle = backend.java_encoder_oracle
            assert oracle is not None
            probe = _py4j_probe(gateway, f"{module.PACKAGE}.StandardShimProbe")

            ascii_element = oracle.materialize(HLAASCIIstring("radar"))
            unicode_element = oracle.materialize(HLAunicodeString("λ"))
            record_element = oracle.materialize(HLAfixedRecord([HLAoctet(7), HLAASCIIstring("space")]))

            assert probe.className(ascii_element) == f"{module.PACKAGE}.StandardShimHLAASCIIstring"
            assert probe.className(unicode_element) == f"{module.PACKAGE}.StandardShimHLAunicodeString"
            assert probe.className(record_element) == f"{module.PACKAGE}.StandardShimHLAfixedRecord"
            assert backend.bridge.to_python_bytes(probe.encode(ascii_element)) == HLAASCIIstring("radar").encode()
            assert backend.bridge.to_python_bytes(probe.encode(unicode_element)) == HLAunicodeString("λ").encode()
            assert backend.bridge.to_python_bytes(probe.encode(record_element)) == HLAfixedRecord(
                [HLAoctet(7), HLAASCIIstring("space")]
            ).encode()

            exploding_ascii = type(
                "HLAASCIIstring",
                (),
                {
                    "getValue": lambda self: "vendor-only",
                    "toByteArray": lambda self: (_ for _ in ()).throw(
                        AssertionError("python toByteArray should not run")
                    ),
                },
            )()
            java_bytes = backend.converter.to_backend(exploding_ascii, expected_type_name="byte[]")
            assert backend.bridge.to_python_bytes(java_bytes) == HLAASCIIstring("vendor-only").encode()

            no_credentials = backend.converter.to_backend(HLAnoCredentials(), expected_type_name="Credentials")
            password_credentials = backend.converter.to_backend(
                HLAplainTextPassword("secret"),
                expected_type_name="Credentials",
            )
            assert probe.credentialClassName(no_credentials) == "hla.rti1516_2025.auth.HLAnoCredentials"
            assert probe.credentialType(no_credentials) == "HLAnoCredentials"
            assert backend.bridge.to_python_bytes(probe.credentialData(no_credentials)) == b""
            assert probe.credentialClassName(password_credentials) == "hla.rti1516_2025.auth.HLAplainTextPassword"
            assert probe.credentialType(password_credentials) == "HLAplainTextPassword"
            assert backend.bridge.to_python_bytes(probe.credentialData(password_credentials)) == HLAplainTextPassword(
                "secret"
            ).data
        finally:
            backend.close()
    finally:
        gateway.shutdown()
