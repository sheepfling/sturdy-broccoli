"""Shared RTI backend registry and ambassador factory helpers."""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from importlib import metadata
from typing import Any, Mapping

from hla2010_rti_backend_common import DelegatingRTIAmbassador, RTIBackendPlugin, RTIBackendSpec, make_rti_ambassador
from hla2010_rti_backend_common.plugin_api import BACKEND_ENTRY_POINT_GROUP, RTIBackendDiscovery, RTITransportSpec
from hla2010_rti_transport_common import coerce_transport_spec as _coerce_transport_spec
from hla2010_rti_transport_common import register_transport_factory

_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_PLUGINS: dict[str, RTIBackendPlugin] = {}
_BACKEND_PLUGINS_LOADED = False
_SOURCE_CHECKOUT_PLUGIN_MODULES: tuple[str, ...] = (
    "hla2010_rti_python.plugin",
    "hla2010_rti_java_jpype.plugin",
    "hla2010_rti_java_py4j.plugin",
    "hla2010_rti_pitch_jpype.plugin",
    "hla2010_rti_pitch_py4j.plugin",
    "hla2010_rti_portico.plugin",
    "hla2010_rti_certi.certi.plugin",
)


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


def _load_backend_plugins() -> None:
    global _BACKEND_PLUGINS_LOADED
    if _BACKEND_PLUGINS_LOADED:
        return
    loaded_plugins = _iter_entry_point_backend_plugins()
    if not loaded_plugins:
        loaded_plugins = _iter_source_checkout_backend_plugins()
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
    """Return installed RTI backend descriptors, optionally probing runtimes."""

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

    transport = options.get("transport")
    if transport is not None:
        options = dict(options)
        options["transport"] = _coerce_transport_spec(transport)

    _load_backend_plugins()
    normalized = _normalize_kind(kind)
    factory = _BACKEND_FACTORIES.get(normalized)
    if factory is None:
        raise ValueError(f"Unknown RTI backend kind: {kind!r}")
    return factory(dict(options))


def create_rti_ambassador(kind: str | RTIBackendSpec = "python", **options: Any) -> DelegatingRTIAmbassador:
    """Create a backend-neutral RTI ambassador."""

    return make_rti_ambassador(create_backend(kind, **options))


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "RTITransportSpec",
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "discover_rti_backends",
    "iter_rti_backend_plugins",
    "register_backend_factory",
    "register_backend_plugin",
    "register_transport_factory",
]
