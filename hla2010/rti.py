"""Uniform RTI ambassador factory.

Application code can create an RTI ambassador by backend name and then use the
same HLA methods regardless of whether the backend is pure Python, JPype, Py4J,
or an in-process Java-shaped test shim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Mapping

from .backends.base import DelegatingRTIAmbassador, make_rti_ambassador
from .backends.python_rti import InMemoryRTIEngine, PythonRTIConfig, create_python_backend


@dataclass(frozen=True)
class RTIBackendSpec:
    """Backend selection for :func:`create_rti_ambassador`."""

    kind: str = "python"
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RTITransportSpec:
    """Transport selection for backends that expose a transport layer."""

    kind: str = "subprocess-line"
    options: Mapping[str, Any] = field(default_factory=dict)


_TRANSPORT_FACTORIES: dict[str, Any] = {}
_TRANSPORT_MODULES: dict[str, str] = {
    "grpc": "hla2010.backends.grpc_transport",
    "http-json": "hla2010.backends.rest_transport",
    "rest": "hla2010.backends.rest_transport",
}


def register_transport_factory(kind: str, factory: Any) -> None:
    """Register a transport factory for a normalized transport kind."""

    normalized = kind.strip().lower().replace("_", "-")
    _TRANSPORT_FACTORIES[normalized] = factory


def _coerce_transport_spec(value: Any):
    if value is None:
        return None
    if hasattr(value, "request") and hasattr(value, "start"):
        return value
    if isinstance(value, RTITransportSpec):
        spec = value
    elif isinstance(value, Mapping):
        if "kind" in value or "options" in value:
            spec = RTITransportSpec(
                kind=value.get("kind", "subprocess-line"),
                options=value.get("options", {k: v for k, v in value.items() if k not in {"kind", "options"}}),
            )
        else:
            raise TypeError(f"Unsupported transport specification mapping: {value!r}")
    elif isinstance(value, str):
        spec = RTITransportSpec(kind=value)
    else:
        raise TypeError(f"Unsupported transport specification: {value!r}")

    normalized = spec.kind.strip().lower().replace("_", "-")
    factory = _TRANSPORT_FACTORIES.get(normalized)
    if factory is None:
        module_name = _TRANSPORT_MODULES.get(normalized)
        if module_name is not None:
            importlib.import_module(module_name)
            factory = _TRANSPORT_FACTORIES.get(normalized)
    if factory is not None:
        return factory(spec)
    if normalized in {"subprocess", "subprocess-line", "stdio", "pipe"}:
        from .backends.certi.transport import CERTITransportConfig, create_certi_transport

        return create_certi_transport(CERTITransportConfig(**dict(spec.options)))
    raise ValueError(f"Unknown transport kind: {spec.kind!r}")


def create_backend(kind: str | RTIBackendSpec = "python", **options: Any):
    """Create a backend by name.

    Supported names:

    * ``python`` / ``inmemory``: dependency-free in-process Python RTI subset.
    * ``jpype`` / ``java-jpype``: Java RTI through JPype.
    * ``py4j`` / ``java-py4j``: Java RTI through Py4J.
    * ``pitch-jpype`` / ``pitch-py4j``: repo-local Pitch pRTI runtime through the Java adapters.
    * ``certi`` / ``certi-native``: real CERTI RTI through a native smoke helper backend.
    * ``certi-jpype`` / ``certi-py4j``: real CERTI RTI exposed through the Java-adapter path.
    * ``java-shim-jpype`` / ``java-shim-py4j``: in-process Java-shaped test shim.
    """

    if isinstance(kind, RTIBackendSpec):
        merged = dict(kind.options)
        merged.update(options)
        options = merged
        kind = kind.kind

    normalized = kind.strip().lower().replace("_", "-")

    if normalized in {"python", "inmemory", "in-memory", "python-inmemory", "python-in-memory"}:
        engine = options.pop("engine", None)
        config = options.pop("config", None)
        if options:
            config = config or PythonRTIConfig(**options)
        return create_python_backend(engine=engine, config=config)

    if normalized in {"jpype", "java-jpype"}:
        from .backends.jpype_backend import JPypeConfig, create_jpype_backend

        config = options.pop("config", None) or JPypeConfig(**options)
        return create_jpype_backend(config)

    if normalized in {"py4j", "java-py4j"}:
        from .backends.py4j_backend import Py4JConfig, create_py4j_backend

        config = options.pop("config", None) or Py4JConfig(**options)
        return create_py4j_backend(config)

    if normalized in {"pitch-jpype", "java-pitch-jpype"}:
        from .real_rti import discover_pitch_runtime
        from .backends.jpype_backend import create_jpype_backend

        pitch_home = options.pop("pitch_home", None)
        runtime = discover_pitch_runtime(pitch_home)
        options.setdefault("rti_factory_name", "Federate Protocol")
        config = options.pop("config", None) or runtime.jpype_config(**options)
        return create_jpype_backend(config)

    if normalized in {"pitch-py4j", "java-pitch-py4j"}:
        from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway
        from .real_rti import launch_pitch_py4j_gateway
        from .backends.py4j_backend import Py4JConfig, create_py4j_backend

        gateway = options.pop("gateway", None)
        if gateway is None:
            launch_port = int(options.pop("launch_gateway_port", 0))
            port = launch_pitch_py4j_gateway(
                pitch_home=options.pop("pitch_home", None),
                port=launch_port,
                die_on_exit=bool(options.pop("die_on_exit", True)),
            )
            gateway = JavaGateway(
                gateway_parameters=GatewayParameters(port=port, auto_convert=True),
                callback_server_parameters=CallbackServerParameters(port=options.pop("callback_port", 0)),
            )
            gateway.start_callback_server()
        config = options.pop("config", None) or Py4JConfig(gateway=gateway, **options)
        return create_py4j_backend(config)

    if normalized in {"certi", "certi-native", "native-certi"}:
        from .backends.certi_backend import CERTIConfig, create_certi_backend

        transport = _coerce_transport_spec(options.pop("transport", None))
        config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
        return create_certi_backend(config)

    if normalized in {"certi-jpype", "java-certi-jpype"}:
        from .backends.certi_backend import CERTIConfig
        from .backends.certi_java_backend import create_certi_java_backend

        transport = _coerce_transport_spec(options.pop("transport", None))
        config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
        return create_certi_java_backend("jpype", config)

    if normalized in {"certi-py4j", "java-certi-py4j"}:
        from .backends.certi_backend import CERTIConfig
        from .backends.certi_java_backend import create_certi_java_backend

        transport = _coerce_transport_spec(options.pop("transport", None))
        config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
        return create_certi_java_backend("py4j", config)

    if normalized in {"java-shim", "java-shim-jpype", "shim-jpype"}:
        from .testing.java_shim import create_java_shim_backend, create_shared_java_shim_backend

        kernel = options.pop("kernel", None)
        shared = options.pop("shared", kernel is not None)
        return create_shared_java_shim_backend("jpype", kernel) if shared else create_java_shim_backend("jpype")

    if normalized in {"java-shim-py4j", "shim-py4j"}:
        from .testing.java_shim import create_java_shim_backend, create_shared_java_shim_backend

        kernel = options.pop("kernel", None)
        shared = options.pop("shared", kernel is not None)
        return create_shared_java_shim_backend("py4j", kernel) if shared else create_java_shim_backend("py4j")

    raise ValueError(f"Unknown RTI backend kind: {kind!r}")


def create_rti_ambassador(kind: str | RTIBackendSpec = "python", **options: Any) -> DelegatingRTIAmbassador:
    """Create a backend-neutral RTIambassador."""

    return make_rti_ambassador(create_backend(kind, **options))


def create_python_rti_pair(*, engine: InMemoryRTIEngine | None = None) -> tuple[DelegatingRTIAmbassador, DelegatingRTIAmbassador]:
    """Convenience for tests: two Python ambassadors sharing one engine."""

    engine = engine or InMemoryRTIEngine()
    return create_rti_ambassador("python", engine=engine), create_rti_ambassador("python", engine=engine)

__all__ = [
    "RTIBackendSpec",
    "RTITransportSpec",
    "create_backend",
    "create_rti_ambassador",
    "create_python_rti_pair",
    "register_transport_factory",
]
