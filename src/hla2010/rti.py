"""Uniform RTI ambassador factory.

Application code can create an RTI ambassador by backend name and then use the
same HLA methods regardless of whether the backend is pure Python, JPype, Py4J,
or an in-process Java-shaped test shim. Backend and transport selection are
registry driven so concrete implementations can register without expanding a
central switchboard.
"""
from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import metadata
from typing import TYPE_CHECKING, Any, Mapping

from .backends.base import DelegatingRTIAmbassador, make_rti_ambassador

if TYPE_CHECKING:
    from .backends.python import InMemoryRTIEngine

BACKEND_ENTRY_POINT_GROUP = "hla2010.rti_backends"


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


@dataclass(frozen=True)
class RTIBackendPlugin:
    """Entry point descriptor for an installable RTI backend."""

    name: str
    create_backend: Callable[[dict[str, Any]], Any]
    aliases: tuple[str, ...] = ()
    family: str = "generic"
    description: str = ""
    discover: Callable[[], Any] | None = None


@dataclass(frozen=True)
class RTIBackendDiscovery:
    """Discovery status for one installed RTI backend plugin."""

    name: str
    aliases: tuple[str, ...]
    family: str
    description: str
    available: bool | None = None
    info: Any = None
    error: str | None = None


_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_PLUGINS: dict[str, RTIBackendPlugin] = {}
_BACKEND_PLUGINS_LOADED = False
_TRANSPORT_FACTORIES: dict[str, Any] = {}
_TRANSPORT_MODULES: dict[str, str] = {
    "grpc": "hla2010_rti_transport_grpc",
    "http-json": "hla2010_rti_transport_rest",
    "rest": "hla2010_rti_transport_rest",
}


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def register_backend_factory(kind: str, factory: Any, *, aliases: tuple[str, ...] = ()) -> None:
    """Register a backend factory for a normalized backend kind and aliases."""

    for name in (kind, *aliases):
        _BACKEND_FACTORIES[_normalize_kind(name)] = factory


def register_backend_plugin(plugin: RTIBackendPlugin) -> None:
    """Register an RTI backend plugin and all of its aliases."""

    for name in (plugin.name, *plugin.aliases):
        normalized = _normalize_kind(name)
        _BACKEND_PLUGINS[normalized] = plugin
        _BACKEND_FACTORIES[normalized] = plugin.create_backend


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


def _load_backend_plugins() -> None:
    global _BACKEND_PLUGINS_LOADED
    if _BACKEND_PLUGINS_LOADED:
        return
    for plugin in _iter_entry_point_backend_plugins():
        register_backend_plugin(plugin)
    _register_in_tree_backend_plugins()
    _BACKEND_PLUGINS_LOADED = True


def _iter_entry_point_backend_plugins() -> list[RTIBackendPlugin]:
    plugins: list[RTIBackendPlugin] = []
    try:
        entry_points = metadata.entry_points()
        selected = entry_points.select(group=BACKEND_ENTRY_POINT_GROUP)
    except Exception:
        return plugins
    for entry_point in selected:
        try:
            loaded = entry_point.load()
        except ModuleNotFoundError:
            continue
        plugin = loaded() if callable(loaded) else loaded
        if not isinstance(plugin, RTIBackendPlugin):
            raise TypeError(f"Backend entry point {entry_point.name!r} did not return RTIBackendPlugin")
        plugins.append(plugin)
    return plugins


def _register_in_tree_backend_plugins() -> None:
    modules = (
        "hla2010_rti_python.plugin",
        "hla2010.backends.python.plugin",
        "hla2010_rti_java_jpype.plugin",
        "hla2010_rti_java_py4j.plugin",
        "hla2010_rti_pitch_jpype.plugin",
        "hla2010_rti_pitch_py4j.plugin",
        "hla2010_rti_portico.plugin",
        "hla2010.backends.java_plugins",
        "hla2010_rti_certi.certi.plugin",
        "hla2010.backends.certi.plugin",
        "hla2010.testing.java_shim_plugin",
    )
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        for plugin_factory in getattr(module, "backend_plugins", lambda: ())():
            register_backend_plugin(plugin_factory)


def available_backend_plugins() -> Mapping[str, RTIBackendPlugin]:
    """Return registered backend plugins keyed by normalized names and aliases."""

    _load_backend_plugins()
    return dict(_BACKEND_PLUGINS)


def iter_rti_backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    """Return unique installed RTI backend plugins sorted by plugin name."""

    _load_backend_plugins()
    unique: dict[str, RTIBackendPlugin] = {}
    for plugin in _BACKEND_PLUGINS.values():
        unique[_normalize_kind(plugin.name)] = plugin
    return tuple(unique[name] for name in sorted(unique))


def discover_rti_backends(*, probe: bool = False) -> tuple[RTIBackendDiscovery, ...]:
    """Return installed RTI backend descriptors, optionally probing runtimes.

    With ``probe=False`` this is a pure registration query and does not require
    optional vendor runtimes. With ``probe=True`` each plugin's ``discover`` hook
    may inspect local installations and report availability.
    """

    rows: list[RTIBackendDiscovery] = []
    for plugin in iter_rti_backend_plugins():
        available: bool | None = None
        info: Any = None
        error: str | None = None
        if probe and plugin.discover is not None:
            try:
                info = plugin.discover()
                available = info is not None
            except Exception as exc:
                available = False
                error = str(exc)
        rows.append(
            RTIBackendDiscovery(
                name=plugin.name,
                aliases=plugin.aliases,
                family=plugin.family,
                description=plugin.description,
                available=available,
                info=info,
                error=error,
            )
        )
    return tuple(rows)


def create_backend(kind: str | RTIBackendSpec = "python", **options: Any):
    """Create a backend by registered name."""

    if isinstance(kind, RTIBackendSpec):
        merged = dict(kind.options)
        merged.update(options)
        options = merged
        kind = kind.kind

    _load_backend_plugins()
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

    from .backends.python import InMemoryRTIEngine

    engine = engine or InMemoryRTIEngine()
    return create_rti_ambassador("python", engine=engine), create_rti_ambassador("python", engine=engine)


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "RTITransportSpec",
    "available_backend_plugins",
    "create_backend",
    "create_python_pair",
    "create_rti_ambassador",
    "discover_rti_backends",
    "iter_rti_backend_plugins",
    "register_backend_factory",
    "register_backend_plugin",
    "register_transport_factory",
]
