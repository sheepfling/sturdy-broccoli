"""Bridge-neutral Java RTI factory selection helpers."""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any

from hla.backends.common import DelegatingRTIAmbassador, make_rti_ambassador


@dataclass(frozen=True)
class JavaRTIFactorySelection:
    """Resolved Java RTI factory selection.

    ``bridge`` selects the Python-to-Java transport package. ``implementation``
    is passed to ``hla.rti1516e.RtiFactoryFactory.getRtiFactory(name)`` by that
    bridge package.
    """

    bridge: str
    implementation: str | None = None
    edition: str = "2010"


@dataclass(frozen=True)
class JavaRTIDiscoveryReport:
    """Debug-facing report for a selected Java RTI implementation."""

    bridge: str
    implementation: str | None
    requested_edition: str
    available: bool
    factory_name: str | None = None
    factory_version: str | None = None
    rti_class_name: str | None = None
    interface_names: tuple[str, ...] = ()
    hla_version: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    error_type: str | None = None
    error: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class _BridgeFactory:
    module_name: str
    config_name: str
    create_backend_name: str


_BRIDGE_FACTORIES: dict[str, _BridgeFactory] = {
    "jpype": _BridgeFactory(
        module_name="hla.bridges.java.jpype.factory",
        config_name="JPypeConfig",
        create_backend_name="create_jpype_backend",
    ),
    "java-jpype": _BridgeFactory(
        module_name="hla.bridges.java.jpype.factory",
        config_name="JPypeConfig",
        create_backend_name="create_jpype_backend",
    ),
    "py4j": _BridgeFactory(
        module_name="hla.bridges.java.py4j.factory",
        config_name="Py4JConfig",
        create_backend_name="create_py4j_backend",
    ),
    "java-py4j": _BridgeFactory(
        module_name="hla.bridges.java.py4j.factory",
        config_name="Py4JConfig",
        create_backend_name="create_py4j_backend",
    ),
}
_SHIM_IMPLEMENTATIONS = frozenset({"shim", "java-shim", "inprocess-java-shim"})
_SHIM_BRIDGE_PROFILES: dict[str, str] = {
    "shim": "jpype",
    "java-shim": "jpype",
    "shim-jpype": "jpype",
    "java-shim-jpype": "jpype",
    "shim-py4j": "py4j",
    "java-shim-py4j": "py4j",
}


def _normalize_bridge_name(bridge: str) -> str:
    return bridge.strip().lower().replace("_", "-")


def _resolve_bridge_factory(bridge: str) -> _BridgeFactory:
    normalized = _normalize_bridge_name(bridge)
    try:
        return _BRIDGE_FACTORIES[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(_BRIDGE_FACTORIES))
        raise ValueError(f"Unknown Java RTI bridge {bridge!r}; supported bridges: {supported}") from exc


def _normalize_edition(edition: str) -> str:
    normalized = edition.strip().lower().replace("_", "-")
    if normalized.startswith("ed"):
        normalized = normalized[2:]
    return normalized


def _edition_warnings(requested_edition: str, hla_version: str | None) -> tuple[str, ...]:
    requested = _normalize_edition(requested_edition)
    warnings: list[str] = []
    if requested != "2010":
        warnings.append(f"No standard Java adapter for edition {requested_edition!r} is implemented yet; available adapter edition is '2010'.")
    if hla_version is not None and requested == "2010" and "2010" not in hla_version:
        warnings.append(f"RTI reported HLA version {hla_version!r}, which does not explicitly confirm edition '2010'.")
    return tuple(warnings)


def _shim_profile(bridge: str, implementation: str | None) -> str | None:
    normalized_bridge = _normalize_bridge_name(bridge)
    if normalized_bridge in _SHIM_BRIDGE_PROFILES:
        return _SHIM_BRIDGE_PROFILES[normalized_bridge]
    if implementation is not None and _normalize_bridge_name(implementation) in _SHIM_IMPLEMENTATIONS:
        if normalized_bridge in {"jpype", "java-jpype"}:
            return "jpype"
        if normalized_bridge in {"py4j", "java-py4j"}:
            return "py4j"
    return None


def _create_java_shim_backend(profile: str, options: dict[str, Any]) -> Any:
    from .java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend

    kernel = options.pop("kernel", None)
    shared = options.pop("shared", kernel is not None)
    if options:
        names = ", ".join(sorted(options))
        raise ValueError(f"Unsupported Java shim options: {names}")
    return create_shared_java_shim_backend(profile, kernel) if shared else create_java_shim_backend(profile)


def _configured_bridge_factory(
    bridge: str,
    selected_implementation: str | None,
    config: Any | None,
    edition: str,
    options: dict[str, Any],
) -> tuple[_BridgeFactory, Any, Any]:
    factory = _resolve_bridge_factory(bridge)
    module = importlib.import_module(factory.module_name)

    if config is not None:
        if selected_implementation is not None and getattr(config, "rti_factory_name", None) != selected_implementation:
            raise ValueError("config.rti_factory_name does not match the selected implementation")
        if getattr(config, "java_api_profile", edition) != edition:
            raise ValueError("config.java_api_profile does not match the selected edition")
        if options:
            names = ", ".join(sorted(options))
            raise ValueError(f"config cannot be combined with explicit bridge options: {names}")
        return factory, module, config

    config_cls = getattr(module, factory.config_name)
    if selected_implementation is not None:
        options["rti_factory_name"] = selected_implementation
    options.setdefault("java_api_profile", edition)
    return factory, module, config_cls(**options)


def create_java_backend(
    bridge: str = "jpype",
    implementation: str | None = None,
    *,
    config: Any | None = None,
    rti_factory_name: str | None = None,
    edition: str = "2010",
    **options: Any,
) -> Any:
    """Create a Java RTI backend using a selected bridge and implementation.

    ``implementation`` is the HLA Java RTI factory implementation string. When
    supplied, it becomes the bridge config's ``rti_factory_name``. Passing both
    ``implementation`` and ``rti_factory_name`` with different values is
    rejected so callers do not accidentally select two vendor factories.
    """

    if implementation is not None and rti_factory_name is not None and implementation != rti_factory_name:
        raise ValueError("implementation and rti_factory_name select different Java RTI factories")

    selected_implementation = implementation if implementation is not None else rti_factory_name
    shim_profile = _shim_profile(bridge, selected_implementation)
    if shim_profile is not None:
        if config is not None:
            raise ValueError("config is only supported for real Java bridge factories, not the in-process Java shim")
        return _create_java_shim_backend(shim_profile, dict(options))

    factory, module, resolved_config = _configured_bridge_factory(bridge, selected_implementation, config, edition, dict(options))
    create_backend = getattr(module, factory.create_backend_name)
    return create_backend(resolved_config)


def _interface_names(bridge_instance: Any, java_rti: Any) -> tuple[str, ...]:
    try:
        if hasattr(java_rti, "getClass"):
            java_class = java_rti.getClass()
            if hasattr(java_class, "getInterfaces"):
                names = []
                for item in java_class.getInterfaces():
                    if hasattr(item, "getName"):
                        names.append(str(item.getName()))
                    else:
                        names.append(str(item))
                return tuple(sorted(names))
    except Exception:
        pass
    class_name = bridge_instance.full_class_name(java_rti)
    return (class_name,) if class_name else ()


def discover_java_rti(
    bridge: str = "jpype",
    implementation: str | None = None,
    *,
    config: Any | None = None,
    rti_factory_name: str | None = None,
    edition: str = "2010",
    **options: Any,
) -> JavaRTIDiscoveryReport:
    """Probe a Java RTI factory selection and report debug metadata."""

    if implementation is not None and rti_factory_name is not None and implementation != rti_factory_name:
        raise ValueError("implementation and rti_factory_name select different Java RTI factories")

    selected_implementation = implementation if implementation is not None else rti_factory_name
    shim_profile = _shim_profile(bridge, selected_implementation)
    if shim_profile is not None:
        hla_version = "HLA 1516-2010"
        return JavaRTIDiscoveryReport(
            bridge=bridge,
            implementation=selected_implementation,
            requested_edition=edition,
            available=True,
            factory_name=f"inprocess-{shim_profile}-java-shim",
            factory_version="0.5",
            rti_class_name="hla.bridges.java.common.java_shim_backend.InProcessJavaRTIShim",
            interface_names=("hla.rti1516e.RTIambassador",),
            hla_version=hla_version,
            details={"profile": shim_profile, "implementation": "Python Java-shaped RTI shim"},
            warnings=_edition_warnings(edition, hla_version),
        )

    bridge_instance = None
    try:
        factory, module, resolved_config = _configured_bridge_factory(bridge, selected_implementation, config, edition, dict(options))
        bridge_cls_name = factory.config_name.replace("Config", "Bridge")
        bridge_cls = getattr(importlib.import_module(factory.module_name.replace(".factory", ".runtime")), bridge_cls_name)
        bridge_instance = bridge_cls(resolved_config)
        if _normalize_bridge_name(bridge) in {"jpype", "java-jpype"}:
            factory_factory = bridge_instance.JClass(bridge_instance.api_profile.factory_factory_class)
            java_factory = (
                factory_factory.getRtiFactory(selected_implementation)
                if selected_implementation
                else factory_factory.getRtiFactory()
            )
        else:
            factory_factory = bridge_instance.gateway.jvm
            for part in bridge_instance.api_profile.factory_factory_class.split("."):
                factory_factory = getattr(factory_factory, part)
            java_factory = (
                factory_factory.getRtiFactory(selected_implementation)
                if selected_implementation
                else factory_factory.getRtiFactory()
            )
        java_rti = java_factory.getRtiAmbassador()
        try:
            factory_name = str(java_factory.rtiName())
        except Exception:
            factory_name = None
        try:
            factory_version = str(java_factory.rtiVersion())
        except Exception:
            factory_version = None
        try:
            hla_version = str(java_rti.getHLAversion())
        except Exception:
            hla_version = None
        return JavaRTIDiscoveryReport(
            bridge=bridge,
            implementation=selected_implementation,
            requested_edition=edition,
            available=True,
            factory_name=factory_name,
            factory_version=factory_version,
            rti_class_name=bridge_instance.full_class_name(java_rti),
            interface_names=_interface_names(bridge_instance, java_rti),
            hla_version=hla_version,
            details={"config_class": type(resolved_config).__name__},
            warnings=_edition_warnings(edition, hla_version),
        )
    except Exception as exc:
        return JavaRTIDiscoveryReport(
            bridge=bridge,
            implementation=selected_implementation,
            requested_edition=edition,
            available=False,
            error_type=type(exc).__name__,
            error=str(exc),
            warnings=_edition_warnings(edition, None),
        )
    finally:
        if bridge_instance is not None:
            try:
                bridge_instance.close()
            except Exception:
                pass


def create_java_rti_ambassador(
    bridge: str = "jpype",
    implementation: str | None = None,
    *,
    config: Any | None = None,
    rti_factory_name: str | None = None,
    edition: str = "2010",
    **options: Any,
) -> DelegatingRTIAmbassador:
    """Create a backend-neutral RTI ambassador backed by a Java RTI."""

    return make_rti_ambassador(
        create_java_backend(
            bridge=bridge,
            implementation=implementation,
            config=config,
            rti_factory_name=rti_factory_name,
            edition=edition,
            **options,
        )
    )


__all__ = [
    "JavaRTIDiscoveryReport",
    "JavaRTIFactorySelection",
    "create_java_backend",
    "create_java_rti_ambassador",
    "discover_java_rti",
]
