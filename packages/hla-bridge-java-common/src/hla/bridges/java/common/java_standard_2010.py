"""Standard-backed Java 2010 Rosetta route helpers."""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest
from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
from hla.bridges.java.common.java_runtime import discover_java_tool


FACTORY_NAME = "HLA-X Java 2010 Standard Shim"
DEFAULT_JAR = Path(
    os.environ.get(
        "HLA_X_JAVA_STANDARD_2010_JAR",
        "build/rosetta/java-standard-2010/hla-x-rti1516e-java-shim.jar",
    )
)


@dataclass(frozen=True, slots=True)
class JavaStandard2010Discovery:
    name: str
    kind: str
    details: dict[str, Any]


def _jar_path(options: dict[str, Any]) -> Path:
    value = options.get("jar_path") or options.get("classpath")
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    return Path(str(value)).expanduser() if value else DEFAULT_JAR


def discover_java_standard_2010(route: str) -> BackendInfo:
    jar_path = DEFAULT_JAR
    return BackendInfo(
        name=f"java-standard-2010-{route}",
        kind=f"java/{route}/standard-2010",
        details={
            "route": route,
            "standard_backed": jar_path.exists(),
            "jar_path": str(jar_path),
            "factory_name": FACTORY_NAME,
        },
    )


def create_java_standard_2010_backend(route: str, request: BackendRequest):
    if request.spec.name != "rti1516e":
        raise ValueError(f"Java 2010 standard route does not support HLA spec {request.spec.name!r}")

    options = dict(request.options)
    jar_path = _jar_path(options)
    if not jar_path.exists():
        raise RuntimeError(
            f"Java 2010 standard shim jar is missing at {jar_path}. "
            "Run ./tools/hla-x build java-standard-2010 first."
        )

    if route == "jpype":
        jpype_factory = importlib.import_module("hla.bridges.java.jpype.factory")
        jpype_runtime = importlib.import_module("hla.bridges.java.jpype.runtime")
        create_jpype_backend = getattr(jpype_factory, "create_jpype_backend")
        JPypeConfig = getattr(jpype_runtime, "JPypeConfig")

        backend = create_jpype_backend(
            JPypeConfig(
                classpath=(str(jar_path),),
                rti_factory_name=FACTORY_NAME,
                convert_strings=bool(options.get("convert_strings", False)),
            )
        )
        backend.info = BackendInfo(
            name="java-standard-2010-jpype",
            kind="java/jpype/standard-2010",
            version=backend.info.version,
            details={**backend.info.details, "standard_backed": True, "jar_path": str(jar_path)},
        )
        return backend

    if route == "py4j":
        try:
            from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Py4J is required for java-standard-2010-py4j") from exc

        py4j_factory = importlib.import_module("hla.bridges.java.py4j.factory")
        py4j_runtime = importlib.import_module("hla.bridges.java.py4j.runtime")
        create_py4j_backend = getattr(py4j_factory, "create_py4j_backend")
        Py4JConfig = getattr(py4j_runtime, "Py4JConfig")

        port = launch_gateway(classpath=str(jar_path), die_on_exit=True, java_path=discover_java_tool("java") or "java")
        gateway = JavaGateway(
            gateway_parameters=GatewayParameters(port=port),
            callback_server_parameters=CallbackServerParameters(port=0),
        )
        reset_py4j_callback_client(gateway)
        backend = create_py4j_backend(
            Py4JConfig(
                gateway=gateway,
                rti_factory_name=FACTORY_NAME,
                shutdown_gateway_on_close=True,
            )
        )
        backend.info = BackendInfo(
            name="java-standard-2010-py4j",
            kind="java/py4j/standard-2010",
            version=backend.info.version,
            details={**backend.info.details, "standard_backed": True, "jar_path": str(jar_path)},
        )
        return backend

    raise ValueError(f"Unknown Java 2010 standard route {route!r}")


__all__ = ["FACTORY_NAME", "DEFAULT_JAR", "create_java_standard_2010_backend", "discover_java_standard_2010"]
