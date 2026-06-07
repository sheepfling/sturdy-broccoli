"""Uniform RTI ambassador factory.

Application code can create an RTI ambassador by backend name and then use the
same HLA methods regardless of whether the backend is pure Python, JPype, Py4J,
or an in-process Java-shaped test shim. Backend and transport selection are
registry driven so concrete implementations can register without expanding a
central switchboard.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Mapping

from .backends.base import DelegatingRTIAmbassador, make_rti_ambassador
from .backends.python import InMemoryRTIEngine, PythonRTIConfig, create_python_backend


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


_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_BUILTINS_REGISTERED = False
_TRANSPORT_FACTORIES: dict[str, Any] = {}
_TRANSPORT_MODULES: dict[str, str] = {
    "grpc": "hla2010.backends.grpc_transport",
    "http-json": "hla2010.backends.rest_transport",
    "rest": "hla2010.backends.rest_transport",
}


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def register_backend_factory(kind: str, factory: Any, *, aliases: tuple[str, ...] = ()) -> None:
    """Register a backend factory for a normalized backend kind and aliases."""

    for name in (kind, *aliases):
        _BACKEND_FACTORIES[_normalize_kind(name)] = factory


def register_transport_factory(kind: str, factory: Any) -> None:
    """Register a transport factory for a normalized transport kind."""

    _TRANSPORT_FACTORIES[_normalize_kind(kind)] = factory


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

    normalized = _normalize_kind(spec.kind)
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


def _python_backend_factory(options: dict[str, Any]):
    engine = options.pop("engine", None)
    config = options.pop("config", None)
    if options:
        config = config or PythonRTIConfig(**options)
    return create_python_backend(engine=engine, config=config)


def _jpype_backend_factory(options: dict[str, Any]):
    from .backends.jpype import JPypeConfig, create_jpype_backend

    config = options.pop("config", None) or JPypeConfig(**options)
    return create_jpype_backend(config)


def _py4j_backend_factory(options: dict[str, Any]):
    from .backends.py4j import Py4JConfig, create_py4j_backend

    config = options.pop("config", None) or Py4JConfig(**options)
    return create_py4j_backend(config)


def _pitch_jpype_backend_factory(options: dict[str, Any]):
    from .backends.jpype import create_jpype_backend
    from .real_rti import discover_pitch_runtime, pitch_fedpro_local_settings_designator

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    options.setdefault("rti_factory_name", "Federate Protocol")
    options.setdefault("connect_local_settings_designator", pitch_fedpro_local_settings_designator())
    config = options.pop("config", None) or runtime.jpype_config(**options)
    return create_jpype_backend(config)


def _pitch_py4j_backend_factory(options: dict[str, Any]):
    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway

    from .backends.py4j import Py4JConfig, create_py4j_backend
    from .real_rti import launch_pitch_py4j_gateway, pitch_fedpro_local_settings_designator

    gateway = options.pop("gateway", None)
    options.setdefault("rti_factory_name", "Federate Protocol")
    options.setdefault("connect_local_settings_designator", pitch_fedpro_local_settings_designator())
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
        _reset_py4j_callback_client(gateway)
        options.setdefault("shutdown_gateway_on_close", True)
    config = options.pop("config", None) or Py4JConfig(gateway=gateway, **options)
    return create_py4j_backend(config)


def _reset_py4j_callback_client(gateway: Any) -> None:
    """Advertise Py4J's actual ephemeral Python callback port to Java."""

    callback_server = gateway.get_callback_server()
    if callback_server is None:
        return
    listening_port = getattr(callback_server, "get_listening_port", lambda: None)()
    if not listening_port or listening_port < 0:
        return
    java_gateway_server = getattr(gateway, "java_gateway_server", None)
    if java_gateway_server is None:
        return
    callback_client = java_gateway_server.getCallbackClient()
    java_gateway_server.resetCallbackClient(callback_client.getAddress(), int(listening_port))


def _portico_jpype_backend_factory(options: dict[str, Any]):
    from .backends.jpype import create_jpype_backend
    from .real_rti import discover_portico_runtime

    portico_home = options.pop("portico_home", None)
    runtime = discover_portico_runtime(portico_home)
    config = options.pop("config", None) or runtime.jpype_config(**options)
    return create_jpype_backend(config)


def _portico_py4j_backend_factory(options: dict[str, Any]):
    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway

    from .backends.py4j import Py4JConfig, create_py4j_backend
    from .real_rti import launch_portico_py4j_gateway

    gateway = options.pop("gateway", None)
    if gateway is None:
        launch_port = int(options.pop("launch_gateway_port", 0))
        port = launch_portico_py4j_gateway(
            portico_home=options.pop("portico_home", None),
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


def _certi_backend_factory(options: dict[str, Any]):
    from .backends.certi import CERTIConfig, create_certi_backend

    transport = _coerce_transport_spec(options.pop("transport", None))
    config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
    return create_certi_backend(config)


def _certi_java_backend_factory(adapter: str, options: dict[str, Any]):
    from .backends.certi import CERTIConfig
    from .backends.certi_java import create_certi_java_backend

    transport = _coerce_transport_spec(options.pop("transport", None))
    config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
    return create_certi_java_backend(adapter, config)


def _java_shim_backend_factory(adapter: str, options: dict[str, Any]):
    from .testing.java_shim import create_java_shim_backend, create_shared_java_shim_backend

    kernel = options.pop("kernel", None)
    shared = options.pop("shared", kernel is not None)
    return create_shared_java_shim_backend(adapter, kernel) if shared else create_java_shim_backend(adapter)


def _register_builtin_backend_factories() -> None:
    global _BACKEND_BUILTINS_REGISTERED
    if _BACKEND_BUILTINS_REGISTERED:
        return
    register_backend_factory("python", _python_backend_factory, aliases=("inmemory", "in-memory", "python-inmemory", "python-in-memory"))
    register_backend_factory("jpype", _jpype_backend_factory, aliases=("java-jpype",))
    register_backend_factory("py4j", _py4j_backend_factory, aliases=("java-py4j",))
    register_backend_factory("pitch-jpype", _pitch_jpype_backend_factory, aliases=("java-pitch-jpype",))
    register_backend_factory("pitch-py4j", _pitch_py4j_backend_factory, aliases=("java-pitch-py4j",))
    register_backend_factory("portico-jpype", _portico_jpype_backend_factory, aliases=("java-portico-jpype", "portico"))
    register_backend_factory("portico-py4j", _portico_py4j_backend_factory, aliases=("java-portico-py4j",))
    register_backend_factory("certi", _certi_backend_factory, aliases=("certi-native", "native-certi"))
    register_backend_factory("certi-jpype", lambda options: _certi_java_backend_factory("jpype", options), aliases=("java-certi-jpype",))
    register_backend_factory("certi-py4j", lambda options: _certi_java_backend_factory("py4j", options), aliases=("java-certi-py4j",))
    register_backend_factory("java-shim-jpype", lambda options: _java_shim_backend_factory("jpype", options), aliases=("java-shim", "shim-jpype"))
    register_backend_factory("java-shim-py4j", lambda options: _java_shim_backend_factory("py4j", options), aliases=("shim-py4j",))
    _BACKEND_BUILTINS_REGISTERED = True


def create_backend(kind: str | RTIBackendSpec = "python", **options: Any):
    """Create a backend by registered name."""

    if isinstance(kind, RTIBackendSpec):
        merged = dict(kind.options)
        merged.update(options)
        options = merged
        kind = kind.kind

    _register_builtin_backend_factories()
    normalized = _normalize_kind(kind)
    factory = _BACKEND_FACTORIES.get(normalized)
    if factory is None:
        raise ValueError(f"Unknown RTI backend kind: {kind!r}")
    return factory(dict(options))


def create_rti_ambassador(kind: str | RTIBackendSpec = "python", **options: Any) -> DelegatingRTIAmbassador:
    """Create a backend-neutral RTIambassador."""

    return make_rti_ambassador(create_backend(kind, **options))


def create_python_pair(*, engine: InMemoryRTIEngine | None = None) -> tuple[DelegatingRTIAmbassador, DelegatingRTIAmbassador]:
    """Canonical convenience helper for two Python ambassadors sharing one engine."""

    engine = engine or InMemoryRTIEngine()
    return create_rti_ambassador("python", engine=engine), create_rti_ambassador("python", engine=engine)


__all__ = [
    "RTIBackendSpec",
    "RTITransportSpec",
    "create_backend",
    "create_python_pair",
    "create_rti_ambassador",
    "register_backend_factory",
    "register_transport_factory",
]
