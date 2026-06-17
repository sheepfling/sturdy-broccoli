"""Shared RTI spec, backend registry, and ambassador factory helpers."""
from __future__ import annotations

import importlib
from importlib import metadata
from typing import Any, Mapping

from .plugin_api import (
    BACKEND_ENTRY_POINT_GROUP,
    SPEC_ENTRY_POINT_GROUP,
    BackendRequest,
    HLASpec,
    RTIBackendDiscovery,
    RTIBackendPlugin,
    RTIBackendSpec,
    RTITransportSpec,
    SpecPlugin,
)

_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_PLUGINS: dict[str, RTIBackendPlugin] = {}
_BACKEND_PLUGINS_LOADED = False
_SPEC_PLUGINS: dict[str, SpecPlugin] = {}
_SPEC_PLUGINS_LOADED = False
_SOURCE_CHECKOUT_SPEC_PLUGIN_MODULES: tuple[str, ...] = (
    "hla.rti1516e.plugin",
    "hla.rti1516_2025.plugin",
)
_SOURCE_CHECKOUT_PLUGIN_MODULES: tuple[str, ...] = (
    "hla.backends.inmemory.plugin",
    "hla.backends.cpp_shim.plugin",
    "hla.backends.shim.plugin",
    "hla.bridges.java.common.java_shim_plugin",
    "hla.bridges.java.jpype.plugin",
    "hla.bridges.java.py4j.plugin",
    "hla.vendors.pitch.jpype.plugin",
    "hla.vendors.pitch.py4j.plugin",
    "hla.vendors.portico.plugin",
    "hla.backends.certi.certi.plugin",
)


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def _normalize_spec(spec: str) -> str:
    return spec.strip().lower().replace("-", "_")


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


def register_spec_plugin(plugin: SpecPlugin) -> None:
    """Register an HLA spec plugin and all of its aliases."""

    for name in (plugin.spec.name, *plugin.spec.aliases):
        _SPEC_PLUGINS[_normalize_spec(name)] = plugin


def _load_spec_plugins() -> None:
    global _SPEC_PLUGINS_LOADED
    if _SPEC_PLUGINS_LOADED:
        return
    loaded_plugins = [*_iter_entry_point_spec_plugins(), *_iter_source_checkout_spec_plugins()]
    for plugin in loaded_plugins:
        register_spec_plugin(plugin)
    _SPEC_PLUGINS_LOADED = True


def _load_backend_plugins() -> None:
    global _BACKEND_PLUGINS_LOADED
    if _BACKEND_PLUGINS_LOADED:
        return
    loaded_plugins = [*_iter_entry_point_backend_plugins(), *_iter_source_checkout_backend_plugins()]
    for plugin in loaded_plugins:
        register_backend_plugin(plugin)
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


def _iter_entry_point_spec_plugins() -> list[SpecPlugin]:
    plugins: list[SpecPlugin] = []
    try:
        entry_points = metadata.entry_points()
        selected = entry_points.select(group=SPEC_ENTRY_POINT_GROUP)
    except Exception:
        return plugins
    for entry_point in selected:
        try:
            loaded = entry_point.load()
        except ModuleNotFoundError:
            continue
        plugin = loaded() if callable(loaded) else loaded
        if not isinstance(plugin, SpecPlugin):
            raise TypeError(f"Spec entry point {entry_point.name!r} did not return SpecPlugin")
        plugins.append(plugin)
    return plugins


def _iter_source_checkout_spec_plugins() -> list[SpecPlugin]:
    plugins: list[SpecPlugin] = []
    for module_name in _SOURCE_CHECKOUT_SPEC_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        plugin = getattr(module, "plugin")()
        if not isinstance(plugin, SpecPlugin):
            raise TypeError(f"Source checkout spec module {module_name!r} returned a non-plugin object")
        plugins.append(plugin)
    return plugins


def _iter_source_checkout_backend_plugins() -> list[RTIBackendPlugin]:
    plugins: list[RTIBackendPlugin] = []
    for module_name in _SOURCE_CHECKOUT_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        for plugin in getattr(module, "backend_plugins", lambda: ())():
            if not isinstance(plugin, RTIBackendPlugin):
                raise TypeError(f"Source checkout backend module {module_name!r} returned a non-plugin object")
            plugins.append(plugin)
    return plugins


def available_spec_plugins() -> Mapping[str, SpecPlugin]:
    """Return registered spec plugins keyed by normalized names and aliases."""

    _load_spec_plugins()
    return dict(_SPEC_PLUGINS)


def iter_hla_spec_plugins() -> tuple[SpecPlugin, ...]:
    """Return unique installed HLA spec plugins sorted by spec name."""

    _load_spec_plugins()
    unique: dict[str, SpecPlugin] = {}
    for plugin in _SPEC_PLUGINS.values():
        unique[_normalize_spec(plugin.spec.name)] = plugin
    return tuple(unique[name] for name in sorted(unique))


def discover_specs() -> tuple[HLASpec, ...]:
    """Return installed HLA spec descriptors."""

    return tuple(plugin.spec for plugin in iter_hla_spec_plugins())


def resolve_spec(spec: str | HLASpec) -> HLASpec:
    """Resolve a spec name or alias to an installed HLA spec descriptor."""

    if isinstance(spec, HLASpec):
        return spec
    _load_spec_plugins()
    plugin = _SPEC_PLUGINS.get(_normalize_spec(spec))
    if plugin is None:
        raise ValueError(f"Unknown HLA spec: {spec!r}")
    return plugin.spec


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


def discover_rti_backends(*, spec: str | HLASpec | None = None, probe: bool = False) -> tuple[RTIBackendDiscovery, ...]:
    """Return installed RTI backend descriptors, optionally probing runtimes."""

    resolved_spec = resolve_spec(spec) if spec is not None else None
    rows: list[RTIBackendDiscovery] = []
    for plugin in iter_rti_backend_plugins():
        if resolved_spec is not None and resolved_spec.name not in plugin.supports:
            continue
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
                supports=plugin.supports,
                description=plugin.description,
                available=available,
                info=info,
                error=error,
            )
        )
    return tuple(rows)


def create_backend(
    backend: str | RTIBackendSpec = "inmemory",
    *,
    spec: str | HLASpec,
    **options: Any,
):
    """Create a backend by registered name."""

    if isinstance(backend, RTIBackendSpec):
        merged = dict(backend.options)
        merged.update(options)
        options = merged
        backend = backend.kind

    resolved_spec = resolve_spec(spec)
    _load_backend_plugins()
    normalized = _normalize_kind(backend)
    plugin = _BACKEND_PLUGINS.get(normalized)
    if plugin is None:
        raise ValueError(f"Unknown RTI backend kind: {backend!r}")
    if resolved_spec.name not in plugin.supports:
        raise ValueError(f"RTI backend {plugin.name!r} does not support HLA spec {resolved_spec.name!r}")
    return plugin.create_backend(BackendRequest(spec=resolved_spec, options=dict(options)))


def create_rti_ambassador(
    *,
    spec: str | HLASpec,
    backend: str | RTIBackendSpec = "inmemory",
    **options: Any,
) -> Any:
    """Create a backend-neutral RTI ambassador."""

    backend_instance = create_backend(backend, spec=spec, **options)
    create_native_ambassador = getattr(backend_instance, "create_rti_ambassador", None)
    if callable(create_native_ambassador):
        return create_native_ambassador()
    make_rti_ambassador = importlib.import_module("hla.backends.common").make_rti_ambassador
    return make_rti_ambassador(backend_instance)


def register_transport_factory(kind: str, factory: Any, *, aliases: tuple[str, ...] = ()) -> None:
    """Register a transport factory without importing transport support at module load."""

    _register_transport_factory = importlib.import_module("hla.transports.common").register_transport_factory
    for name in (kind, *aliases):
        _register_transport_factory(name, factory)


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "RTITransportSpec",
    "available_spec_plugins",
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "discover_specs",
    "discover_rti_backends",
    "iter_hla_spec_plugins",
    "iter_rti_backend_plugins",
    "register_backend_factory",
    "register_backend_plugin",
    "register_spec_plugin",
    "register_transport_factory",
    "resolve_spec",
]
