from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "java_shims/hla-rti1516e-standard-shim/tools/build_standard_shim.py"
JAR_PATH = ROOT / "build/shim_routes/java-standard-2010/java-rti1516e-standard-shim.jar"


def _load_build_module() -> Any:
    spec = importlib.util.spec_from_file_location("shim_routes_build_standard_shim", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _usable_javac() -> bool:
    module = _load_build_module()
    try:
        module._java_tool("javac")
        module._java_tool("jar")
    except SystemExit:
        return False
    return True


def test_java_standard_2010_build_tool_reads_official_api_surface() -> None:
    module = _load_build_module()
    with module.zipfile.ZipFile(module.API_ZIP) as zf:
        text = zf.read("java/src/hla/rti1516e/RTIambassador.java").decode("utf-8")
    methods = module._parse_methods(text)
    names = {method.name for method in methods}

    assert len(methods) > 100
    assert {"connect", "joinFederationExecution", "sendInteraction", "timeAdvanceRequest"} <= names
    assert "saveFederation" not in module.IMPLEMENTED


@pytest.mark.skipif(not _usable_javac(), reason="Java 2010 standard shim build requires a usable JDK javac and jar")
def test_java_standard_2010_shim_jar_builds_against_official_api() -> None:
    subprocess.run(["python3", str(BUILD_SCRIPT)], cwd=ROOT, check=True)

    assert JAR_PATH.exists()


def _require_built_standard_jar() -> None:
    if not JAR_PATH.exists():
        pytest.skip("Java 2010 standard shim jar has not been built")


@pytest.mark.parametrize("backend_name", ["java-standard-2010-jpype", "java-standard-2010-py4j"])
def test_java_standard_2010_routes_pass_basic_lifecycle_when_built(backend_name: str) -> None:
    _require_built_standard_jar()
    pytest.importorskip("jpype" if backend_name.endswith("jpype") else "py4j")

    from hla.rti1516e.enums import CallbackModel, ResignAction
    from hla.rti import create_rti_ambassador

    rti = create_rti_ambassador(spec="rti1516e", backend=backend_name, jar_path=str(JAR_PATH))
    rti.connect(object(), CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("java-standard-2010-lifecycle", "DemoFOMmodule.xml")
    rti.join_federation_execution("federate", "type", "java-standard-2010-lifecycle")
    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution("java-standard-2010-lifecycle")
    rti.disconnect()
    rti.close()
    assert rti.backend_info.details["standard_backed"] is True


@pytest.mark.parametrize("backend_name", ["java-standard-2010-jpype", "java-standard-2010-py4j"])
def test_java_standard_2010_routes_pass_core_exchange_when_built(backend_name: str) -> None:
    _require_built_standard_jar()
    pytest.importorskip("jpype" if backend_name.endswith("jpype") else "py4j")

    from hla.rti import create_rti_ambassador
    from hla.verification import run_basic_federate_scenario

    summary = run_basic_federate_scenario(
        lambda: create_rti_ambassador(spec="rti1516e", backend=backend_name, jar_path=str(JAR_PATH)),
        federation_name=f"{backend_name}-core",
    )

    assert summary["event_names"].count("discover") == 1
    assert summary["event_names"].count("reflect") == 1
    assert summary["event_names"].count("interaction") == 1
