"""Backend factories for generic user-supplied Java RTI jars."""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, cast

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest

from .java_intake import java_api_profile, validate_classpath
from .java_runtime import discover_java_tool
from .py4j_support import reset_py4j_callback_client


def _classpath(options: dict[str, Any]) -> tuple[str, ...]:
    value = options.get("classpath")
    if value is None:
        value = options.get("jar_path")
    if value is None:
        raise ValueError("Generic Java RTI intake routes require classpath=[...] or jar_path=...")
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def discover_java_intake_backend(edition: str, route: str) -> BackendInfo:
    profile = java_api_profile(edition)
    return BackendInfo(
        name=f"java-{profile.edition}-{route}",
        kind=f"java/{route}/intake-{profile.edition}",
        details={
            "route": route,
            "edition": profile.edition,
            "spec": profile.spec_name,
            "generic_intake": True,
            "requires_classpath": True,
            "factory_factory_class": profile.factory_factory_class,
        },
    )


def create_java_intake_backend(edition: str, route: str, request: BackendRequest):
    profile = java_api_profile(edition)
    if request.spec.name != profile.spec_name:
        raise ValueError(f"Java {profile.edition} intake route does not support HLA spec {request.spec.name!r}")
    if profile.edition == "2025":
        raise RuntimeError(
            "Generic Java 2025 RTI invocation is not implemented yet. "
            "Use './tools/shim-routes java discover --edition 2025 ...' for discovery evidence."
        )

    options = dict(request.options)
    classpath = tuple(str(path) for path in validate_classpath(_classpath(options)))
    factory_name = options.get("rti_factory_name") or options.get("factory")
    local_settings = options.get("local_settings_designator") or options.get("connect_local_settings_designator")

    if route == "jpype":
        jpype_factory = importlib.import_module("hla.bridges.java.jpype.factory")
        jpype_runtime = importlib.import_module("hla.bridges.java.jpype.runtime")
        create_jpype_backend = getattr(jpype_factory, "create_jpype_backend")
        JPypeConfig = getattr(jpype_runtime, "JPypeConfig")
        backend = create_jpype_backend(
            JPypeConfig(
                classpath=classpath,
                jvm_args=tuple(options.get("jvm_args", ())),
                rti_factory_name=str(factory_name) if factory_name else None,
                connect_local_settings_designator=str(local_settings) if local_settings else None,
                convert_strings=bool(options.get("convert_strings", False)),
            )
        )
    elif route == "py4j":
        try:
            from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Py4J is required for java-2010-py4j") from exc

        py4j_factory = importlib.import_module("hla.bridges.java.py4j.factory")
        py4j_runtime = importlib.import_module("hla.bridges.java.py4j.runtime")
        create_py4j_backend = getattr(py4j_factory, "create_py4j_backend")
        Py4JConfig = getattr(py4j_runtime, "Py4JConfig")

        gateway = options.get("gateway")
        port = options.get("gateway_port")
        if gateway is None and port is None:
            port = cast(int, launch_gateway(
                classpath=os.pathsep.join(classpath),
                die_on_exit=True,
                java_path=discover_java_tool("java") or "java",
            ))
        if gateway is None:
            if port is None:
                raise RuntimeError("Py4J gateway port was not provided and could not be discovered.")
            gateway = JavaGateway(
                gateway_parameters=GatewayParameters(port=int(port)),
                callback_server_parameters=CallbackServerParameters(port=0),
            )
            reset_py4j_callback_client(gateway)
        backend = create_py4j_backend(
            Py4JConfig(
                gateway=gateway,
                rti_factory_name=str(factory_name) if factory_name else None,
                connect_local_settings_designator=str(local_settings) if local_settings else None,
                shutdown_gateway_on_close=bool(options.get("shutdown_gateway_on_close", True)),
            )
        )
    else:
        raise ValueError(f"Unknown Java intake route {route!r}")

    backend.info = BackendInfo(
        name=f"java-{profile.edition}-{route}",
        kind=f"java/{route}/intake-{profile.edition}",
        version=backend.info.version,
        details={
            **backend.info.details,
            "generic_intake": True,
            "edition": profile.edition,
            "spec": profile.spec_name,
            "classpath": list(classpath),
            "factory_factory_class": profile.factory_factory_class,
        },
    )
    return backend


__all__ = ["create_java_intake_backend", "discover_java_intake_backend"]
