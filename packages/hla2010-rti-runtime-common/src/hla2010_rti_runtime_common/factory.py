"""Shared RTI backend registry and ambassador factory helpers."""
from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from importlib import metadata
from typing import Any, Mapping

from hla2010_rti_backend_common import DelegatingRTIAmbassador, RTIBackendPlugin, RTIBackendSpec, make_rti_ambassador
from hla2010_rti_backend_common.plugin_api import (
    BACKEND_ENTRY_POINT_GROUP,
    BACKEND_ENTRY_POINT_GROUPS,
    RTIBackendDiscovery,
    RTITransportSpec,
)
from hla2010_rti_transport_common import coerce_transport_spec as _coerce_transport_spec
from hla2010_rti_transport_common import register_transport_factory

_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_PLUGINS: dict[str, RTIBackendPlugin] = {}
_BACKEND_PLUGINS_LOADED = False
_SELECTED_BACKEND_EDITION = "2010"
_BACKEND_PLUGIN_RECORDS: dict[str, "_LoadedBackendPluginRecord"] = {}
_BACKEND_PLUGIN_LOAD_ISSUES: tuple["RTIBackendRegistryIssue", ...] = ()
_BACKEND_PLUGIN_LOAD_STRATEGY = "uninitialized"
_SOURCE_CHECKOUT_PLUGIN_MODULES: tuple[str, ...] = (
    "hla2010_rti_python.plugin",
    "hla2010_rti_java_jpype.plugin",
    "hla2010_rti_java_py4j.plugin",
    "hla2010_rti_pitch_jpype.plugin",
    "hla2010_rti_pitch_py4j.plugin",
    "hla2010_rti_portico.plugin",
    "hla2010_rti_certi.certi.plugin",
)


@dataclass(frozen=True)
class RTIAmbassadorFactory:
    """Human-facing installed RTI factory descriptor."""

    name: str
    aliases: tuple[str, ...]
    supported_editions: tuple[str, ...]
    selectable_names: tuple[str, ...]
    family: str
    description: str
    probe_supported: bool
    source_kind: str
    _plugin: RTIBackendPlugin = field(repr=False, compare=False)
    source_module: str | None = None
    entry_point_group: str | None = None
    entry_point_name: str | None = None
    entry_point_value: str | None = None

    def create_backend(self, **options: Any) -> Any:
        """Instantiate the backend implementation behind this factory."""

        return create_backend(self.name, **options)

    def create_rti_ambassador(self, **options: Any) -> DelegatingRTIAmbassador:
        """Instantiate a backend-neutral RTI ambassador from this factory."""

        return create_rti_ambassador(self.name, **options)

    def discover(self) -> RTIBackendDiscovery:
        """Probe this installed factory when it exposes runtime discovery."""

        available: bool | None = None
        info: Any = None
        error: str | None = None
        if self._plugin.discover is not None:
            try:
                info = self._plugin.discover()
                available = info is not None
            except Exception as exc:
                available = False
                error = str(exc)
        return RTIBackendDiscovery(
            name=self.name,
            aliases=self.aliases,
            supported_editions=self.supported_editions,
            family=self.family,
            description=self.description,
            selectable_names=self.selectable_names,
            probe_supported=self.probe_supported,
            available=available,
            info=info,
            error=error,
        )


@dataclass(frozen=True)
class RTIBackendRegistryIssue:
    """One skipped or failed backend-plugin load step."""

    source_kind: str
    phase: str
    locator: str
    error_type: str
    error: str


@dataclass(frozen=True)
class RTIBackendRegistryEntry:
    """Debug-facing registry row for one installed backend plugin."""

    name: str
    aliases: tuple[str, ...]
    supported_editions: tuple[str, ...]
    selectable_names: tuple[str, ...]
    family: str
    description: str
    probe_supported: bool
    source_kind: str
    source_module: str | None = None
    entry_point_group: str | None = None
    entry_point_name: str | None = None
    entry_point_value: str | None = None
    matches_selected_edition: bool = True


@dataclass(frozen=True)
class RTIBackendRegistryDebugReport:
    """Debug-facing summary of backend-plugin registry state."""

    selected_backend_edition: str
    load_strategy: str
    entry_point_groups: tuple[str, ...]
    plugins: tuple[RTIBackendRegistryEntry, ...]
    issues: tuple[RTIBackendRegistryIssue, ...]


@dataclass(frozen=True)
class _LoadedBackendPluginRecord:
    plugin: RTIBackendPlugin = field(repr=False, compare=False)
    source_kind: str
    source_module: str | None = None
    entry_point_group: str | None = None
    entry_point_name: str | None = None
    entry_point_value: str | None = None


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def _normalize_edition_name(edition: str) -> str:
    normalized = edition.strip().lower().replace("_", "-")
    if normalized.isdigit():
        return normalized
    if normalized.startswith("ed") and normalized[2:].isdigit():
        return normalized[2:]
    match = re.search(r"(19|20)\d{2}", normalized)
    if match is not None:
        return match.group(0)
    raise ValueError(f"Unsupported RTI backend edition selection: {edition!r}")


def selected_backend_edition() -> str:
    """Return the active RTI backend edition selection."""

    return _SELECTED_BACKEND_EDITION


def set_selected_backend_edition(edition: str) -> str:
    """Set the active RTI backend edition selection and return the normalized key."""

    global _SELECTED_BACKEND_EDITION
    _SELECTED_BACKEND_EDITION = _normalize_edition_name(edition)
    return _SELECTED_BACKEND_EDITION


def _edition_matches(plugin: RTIBackendPlugin, edition: str | None) -> bool:
    if edition is None:
        return True
    normalized = _normalize_edition_name(edition)
    return normalized in {str(item).strip() for item in plugin.supported_editions}


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
    global _BACKEND_PLUGIN_LOAD_ISSUES
    global _BACKEND_PLUGIN_LOAD_STRATEGY
    if _BACKEND_PLUGINS_LOADED:
        return
    _BACKEND_PLUGIN_RECORDS.clear()
    loaded_records, issues, strategy = _collect_backend_plugin_records()
    for record in loaded_records:
        register_backend_plugin(record.plugin)
        _BACKEND_PLUGIN_RECORDS[_normalize_kind(record.plugin.name)] = record
    _BACKEND_PLUGIN_LOAD_ISSUES = tuple(issues)
    _BACKEND_PLUGIN_LOAD_STRATEGY = strategy
    _BACKEND_PLUGINS_LOADED = True


def _iter_entry_point_backend_plugins() -> list[RTIBackendPlugin]:
    return [record.plugin for record in _collect_entry_point_backend_plugin_records()[0]]


def _collect_entry_point_backend_plugin_records() -> tuple[list[_LoadedBackendPluginRecord], list[RTIBackendRegistryIssue]]:
    records: list[_LoadedBackendPluginRecord] = []
    issues: list[RTIBackendRegistryIssue] = []
    seen_entry_points: set[tuple[str, str]] = set()
    try:
        entry_points = metadata.entry_points()
    except Exception:
        return records, issues
    for group_name in BACKEND_ENTRY_POINT_GROUPS:
        for entry_point in entry_points.select(group=group_name):
            identity = (entry_point.name, entry_point.value)
            if identity in seen_entry_points:
                continue
            seen_entry_points.add(identity)
            try:
                loaded = entry_point.load()
            except ModuleNotFoundError as exc:
                issues.append(
                    RTIBackendRegistryIssue(
                        source_kind="entry-point",
                        phase="load",
                        locator=f"{group_name}:{entry_point.name} -> {entry_point.value}",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    )
                )
                continue
            except Exception as exc:
                issues.append(
                    RTIBackendRegistryIssue(
                        source_kind="entry-point",
                        phase="load",
                        locator=f"{group_name}:{entry_point.name} -> {entry_point.value}",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    )
                )
                continue
            plugin = loaded() if callable(loaded) else loaded
            if not isinstance(plugin, RTIBackendPlugin):
                issues.append(
                    RTIBackendRegistryIssue(
                        source_kind="entry-point",
                        phase="validate",
                        locator=f"{group_name}:{entry_point.name} -> {entry_point.value}",
                        error_type="TypeError",
                        error=f"Backend entry point {entry_point.name!r} did not return RTIBackendPlugin",
                    )
                )
                continue
            records.append(
                _LoadedBackendPluginRecord(
                    plugin=plugin,
                    source_kind="entry-point",
                    entry_point_group=group_name,
                    entry_point_name=entry_point.name,
                    entry_point_value=entry_point.value,
                )
            )
    return records, issues


def _iter_source_checkout_backend_plugins() -> list[RTIBackendPlugin]:
    return [record.plugin for record in _collect_source_checkout_backend_plugin_records()[0]]


def _collect_source_checkout_backend_plugin_records() -> tuple[list[_LoadedBackendPluginRecord], list[RTIBackendRegistryIssue]]:
    records: list[_LoadedBackendPluginRecord] = []
    issues: list[RTIBackendRegistryIssue] = []
    for module_name in _SOURCE_CHECKOUT_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                issues.append(
                    RTIBackendRegistryIssue(
                        source_kind="source-checkout",
                        phase="import",
                        locator=module_name,
                        error_type=type(exc).__name__,
                        error=str(exc),
                    )
                )
                continue
            raise
        for plugin in getattr(module, "backend_plugins", lambda: ())():
            if not isinstance(plugin, RTIBackendPlugin):
                raise TypeError(f"Source checkout backend module {module_name!r} returned a non-plugin object")
            records.append(
                _LoadedBackendPluginRecord(
                    plugin=plugin,
                    source_kind="source-checkout",
                    source_module=module_name,
                )
            )
    return records, issues


def _collect_backend_plugin_records() -> tuple[list[_LoadedBackendPluginRecord], list[RTIBackendRegistryIssue], str]:
    entry_point_records, entry_point_issues = _collect_entry_point_backend_plugin_records()
    if entry_point_records:
        return entry_point_records, entry_point_issues, "entry-point"
    source_records, source_issues = _collect_source_checkout_backend_plugin_records()
    if source_records:
        return source_records, [*entry_point_issues, *source_issues], "source-checkout"
    return [], [*entry_point_issues, *source_issues], "empty"


def available_backend_plugins() -> Mapping[str, RTIBackendPlugin]:
    """Return registered backend plugins keyed by normalized names and aliases."""

    _load_backend_plugins()
    return dict(_BACKEND_PLUGINS)


def iter_rti_backend_plugins(*, edition: str | None = None) -> tuple[RTIBackendPlugin, ...]:
    """Return unique installed RTI backend plugins sorted by plugin name."""

    _load_backend_plugins()
    unique: dict[str, RTIBackendPlugin] = {}
    for plugin in _BACKEND_PLUGINS.values():
        if not _edition_matches(plugin, edition):
            continue
        unique[_normalize_kind(plugin.name)] = plugin
    return tuple(unique[name] for name in sorted(unique))


def _selectable_names_for_plugin(plugin: RTIBackendPlugin) -> tuple[str, ...]:
    names = {_normalize_kind(plugin.name), *(_normalize_kind(alias) for alias in plugin.aliases)}
    return tuple(sorted(names))


def iter_rti_factories(*, edition: str | None = None) -> tuple[RTIAmbassadorFactory, ...]:
    """Return installed RTI ambassador factories with human-facing metadata."""

    rows: list[RTIAmbassadorFactory] = []
    for plugin in iter_rti_backend_plugins(edition=edition):
        record = _BACKEND_PLUGIN_RECORDS.get(_normalize_kind(plugin.name))
        rows.append(
            RTIAmbassadorFactory(
                name=plugin.name,
                aliases=plugin.aliases,
                supported_editions=plugin.supported_editions,
                selectable_names=_selectable_names_for_plugin(plugin),
                family=plugin.family,
                description=plugin.description,
                probe_supported=plugin.discover is not None,
                source_kind="unknown" if record is None else record.source_kind,
                source_module=None if record is None else record.source_module,
                entry_point_group=None if record is None else record.entry_point_group,
                entry_point_name=None if record is None else record.entry_point_name,
                entry_point_value=None if record is None else record.entry_point_value,
                _plugin=plugin,
            )
        )
    return tuple(rows)


def get_rti_factory(name: str, *, edition: str | None = None) -> RTIAmbassadorFactory:
    """Resolve one installed RTI ambassador factory by canonical name or alias."""

    normalized = _normalize_kind(name)
    resolved_edition = selected_backend_edition() if edition is None else _normalize_edition_name(edition)
    for factory in iter_rti_factories(edition=resolved_edition):
        if normalized in factory.selectable_names:
            return factory
    all_factories = iter_rti_factories()
    if any(normalized in factory.selectable_names for factory in all_factories):
        raise ValueError(f"RTI factory {name!r} is not available for edition {resolved_edition!r}")
    raise ValueError(f"Unknown RTI factory name: {name!r}")


def discover_rti_backends(*, probe: bool = False, edition: str | None = None) -> tuple[RTIBackendDiscovery, ...]:
    """Return installed RTI backend descriptors, optionally probing runtimes."""

    rows: list[RTIBackendDiscovery] = []
    resolved_edition = selected_backend_edition() if edition is None else _normalize_edition_name(edition)
    for factory in iter_rti_factories(edition=resolved_edition):
        if probe:
            rows.append(factory.discover())
            continue
        rows.append(
            RTIBackendDiscovery(
                name=factory.name,
                aliases=factory.aliases,
                supported_editions=factory.supported_editions,
                family=factory.family,
                description=factory.description,
                selectable_names=factory.selectable_names,
                probe_supported=factory.probe_supported,
            )
        )
    return tuple(rows)


def debug_rti_backend_registry(*, edition: str | None = None) -> RTIBackendRegistryDebugReport:
    """Return provenance and skip/failure details for backend-plugin discovery."""

    _load_backend_plugins()
    resolved_edition = selected_backend_edition() if edition is None else _normalize_edition_name(edition)
    rows: list[RTIBackendRegistryEntry] = []
    for name in sorted(_BACKEND_PLUGIN_RECORDS):
        record = _BACKEND_PLUGIN_RECORDS[name]
        plugin = record.plugin
        rows.append(
            RTIBackendRegistryEntry(
                name=plugin.name,
                aliases=plugin.aliases,
                supported_editions=plugin.supported_editions,
                selectable_names=_selectable_names_for_plugin(plugin),
                family=plugin.family,
                description=plugin.description,
                probe_supported=plugin.discover is not None,
                source_kind=record.source_kind,
                source_module=record.source_module,
                entry_point_group=record.entry_point_group,
                entry_point_name=record.entry_point_name,
                entry_point_value=record.entry_point_value,
                matches_selected_edition=_edition_matches(plugin, resolved_edition),
            )
        )
    return RTIBackendRegistryDebugReport(
        selected_backend_edition=resolved_edition,
        load_strategy=_BACKEND_PLUGIN_LOAD_STRATEGY,
        entry_point_groups=BACKEND_ENTRY_POINT_GROUPS,
        plugins=tuple(rows),
        issues=_BACKEND_PLUGIN_LOAD_ISSUES,
    )


def create_backend(
    kind: str | RTIBackendSpec = "python",
    *,
    edition: str | None = None,
    **options: Any,
):
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
    resolved_edition = selected_backend_edition() if edition is None else _normalize_edition_name(edition)
    plugin = _BACKEND_PLUGINS.get(normalized)
    if plugin is not None and not _edition_matches(plugin, resolved_edition):
        raise ValueError(f"RTI backend kind {kind!r} is not available for edition {resolved_edition!r}")
    factory = _BACKEND_FACTORIES.get(normalized)
    if factory is None:
        raise ValueError(f"Unknown RTI backend kind: {kind!r}")
    return factory(dict(options))


def create_rti_ambassador(
    kind: str | RTIBackendSpec = "python",
    *,
    edition: str | None = None,
    **options: Any,
) -> DelegatingRTIAmbassador:
    """Create a backend-neutral RTI ambassador."""

    return make_rti_ambassador(create_backend(kind, edition=edition, **options))


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "RTIAmbassadorFactory",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendRegistryDebugReport",
    "RTIBackendRegistryEntry",
    "RTIBackendRegistryIssue",
    "RTIBackendSpec",
    "RTITransportSpec",
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "debug_rti_backend_registry",
    "discover_rti_backends",
    "get_rti_factory",
    "iter_rti_backend_plugins",
    "iter_rti_factories",
    "register_backend_factory",
    "register_backend_plugin",
    "register_transport_factory",
    "selected_backend_edition",
    "set_selected_backend_edition",
]
