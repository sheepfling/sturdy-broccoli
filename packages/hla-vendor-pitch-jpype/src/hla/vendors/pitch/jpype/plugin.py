"""Entry point descriptor for the Pitch JPype RTI backend."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from hla.bridges.java.common import BackendInfo, BackendUnavailableError, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest

from .factory import create_jpype_backend


def _pitch_native_202x_details(*, bridge: str, home: str, surface: str) -> dict[str, Any]:
    return {
        "spec": "rti1516_2025",
        "vendor_surface": "hla.rti1516_202X",
        "bridge": bridge,
        "pitch_home": home,
        "native_hla4": True,
        "surface_mode": surface,
        "bridge_ready": False,
        "counts_as_vendor_runtime": surface == "fedpro",
    }


@dataclass(frozen=True, slots=True)
class _Pitch202XAdapterBackendInfo:
    name: str
    kind: str
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=dict)


class _Pitch202XJPypeAdapterBackend:
    def __init__(self, request: BackendRequest, *, home: str):
        self.request = request
        self.info = _Pitch202XAdapterBackendInfo(
            name="pitch-202x-jpype",
            kind="vendor/pitch/java-202x/jpype",
            details={
                "spec": "rti1516_2025",
                "vendor_surface": "hla.rti1516_202X",
                "bridge": "jpype",
                "pitch_home": home,
                "adapter_status": "python1516_2025-wrapped",
                "bridge_ready": False,
                "counts_as_vendor_runtime": False,
                "evidence_artifacts": [
                    "packages/hla-vendor-pitch/docs/evidence/pitch_202x_probe_2026-06-23.md",
                    "packages/hla-vendor-pitch/docs/evidence/pitch_202x_surface_audit_2026-06-23.md",
                    "packages/hla-vendor-pitch/docs/evidence/pitch_202x_surface_audit_2026-06-23.json",
                ],
            },
        )

    def create_rti_ambassador(self) -> Any:
        from hla.backends.python1516_2025.backend import create_python2025_backend

        native_backend = create_python2025_backend(self.request)
        ambassador = native_backend.create_rti_ambassador()
        native_info = ambassador.backend_info
        ambassador.backend_info = _Pitch202XAdapterBackendInfo(
            name=self.info.name,
            kind=self.info.kind,
            version=native_info.version,
            details={**dict(native_info.details), **dict(self.info.details)},
        )
        return ambassador


def _discover_pitch_runtime() -> BackendInfo | None:
    try:
        from hla.vendors.pitch import discover_pitch_runtime

        runtime = discover_pitch_runtime()
        return BackendInfo(name="Pitch", kind="vendor/pitch", details={"home": str(runtime.home)})
    except BackendUnavailableError:
        return None


def _discover_pitch_202x_runtime() -> BackendInfo | None:
    runtime = _discover_pitch_runtime()
    if runtime is None:
        return None
    return BackendInfo(
        name="pitch-202x-jpype",
        kind="vendor/pitch/java-202x/jpype",
        details={
            **dict(runtime.details),
            "spec": "rti1516_2025",
            "vendor_surface": "hla.rti1516_202X",
            "adapter_status": "python1516_2025-wrapped",
            "bridge_ready": False,
            "counts_as_vendor_runtime": False,
        },
    )


def _discover_pitch_native_202x_runtime() -> BackendInfo | None:
    runtime = _discover_pitch_runtime()
    if runtime is None:
        return None
    return BackendInfo(
        name="pitch-native-202x-jpype",
        kind="vendor/pitch/java-202x-native/jpype",
        details={
            **dict(runtime.details),
            **_pitch_native_202x_details(bridge="jpype", home=str(runtime.details["home"]), surface="direct"),
            "supported_surface_modes": ("direct", "fedpro"),
        },
    )


def _pitch_jpype_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from hla.vendors.pitch import discover_pitch_runtime, pitch_fedpro_local_settings_designator

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    options.setdefault("rti_factory_name", "Federate Protocol")
    options.setdefault("connect_local_settings_designator", pitch_fedpro_local_settings_designator())
    config = options.pop("config", None) or runtime.jpype_config(**options)
    return create_jpype_backend(config)


def _pitch_202x_jpype_backend_factory(request: BackendRequest):
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"pitch-202x-jpype only supports HLA spec {request.spec.name!r}")
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from hla.vendors.pitch import discover_pitch_runtime

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    return _Pitch202XJPypeAdapterBackend(request, home=str(runtime.home))


def _pitch_native_202x_jpype_backend_factory(request: BackendRequest):
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"pitch-native-202x-jpype only supports HLA spec {request.spec.name!r}")
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from hla.vendors.pitch import (
        discover_pitch_runtime,
        pitch_fedpro_local_settings_designator,
        pitch_hla4_direct_classpath,
        pitch_hla4_fedpro_classpath,
    )

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    surface = str(options.pop("surface", "direct")).strip().lower().replace("_", "-")
    if surface not in {"direct", "fedpro"}:
        raise ValueError(f"Unsupported native Pitch HLA4 surface {surface!r}; expected 'direct' or 'fedpro'")
    classpath = pitch_hla4_direct_classpath(runtime) if surface == "direct" else pitch_hla4_fedpro_classpath(runtime)
    base_config = runtime.jpype_config(**options)
    rti_factory_name = options.get("rti_factory_name")
    if rti_factory_name is None and surface == "fedpro":
        rti_factory_name = "Federate Protocol"
    config = replace(
        base_config,
        classpath=tuple(str(path) for path in classpath),
        rti_factory_name=rti_factory_name,
        connect_local_settings_designator=(
            pitch_fedpro_local_settings_designator() if surface == "fedpro" else options.get("connect_local_settings_designator")
        ),
        java_api_profile="202X",
    )
    try:
        backend = create_jpype_backend(config)
    except BaseException as exc:
        if surface != "fedpro" or rti_factory_name != "Federate Protocol":
            raise
        fallback_config = replace(config, rti_factory_name=None)
        backend = create_jpype_backend(fallback_config)
        backend.info = BackendInfo(
            name="pitch-native-202x-jpype",
            kind="vendor/pitch/java-202x-native/jpype",
            version=backend.info.version,
            details={
                **dict(backend.info.details),
                "factory_resolution_fallback": "default-rti-factory",
                "factory_resolution_error": str(exc),
            },
        )
    backend.info = BackendInfo(
        name="pitch-native-202x-jpype",
        kind="vendor/pitch/java-202x-native/jpype",
        version=backend.info.version,
        details={
            **dict(backend.info.details),
            **_pitch_native_202x_details(bridge="jpype", home=str(runtime.home), surface=surface),
            "classpath": [str(path) for path in classpath],
            "supported_surface_modes": ("direct", "fedpro"),
        },
    )
    return backend


def pitch_jpype_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="pitch-jpype",
        aliases=("java-pitch-jpype",),
        family="pitch/java",
        description="Pitch Federate Protocol adapter through JPype.",
        create_backend=_pitch_jpype_backend_factory,
        discover=_discover_pitch_runtime,
    )


def plugin() -> RTIBackendPlugin:
    return pitch_jpype_plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (
        plugin(),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="pitch-202x-jpype",
            aliases=("java-pitch-202x-jpype",),
            family="pitch/java-202x",
            description="Pitch vendor 202X Java surface exposed as an explicit 2025 adapter route through JPype.",
            create_backend=_pitch_202x_jpype_backend_factory,
            discover=_discover_pitch_202x_runtime,
        ),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="pitch-native-202x-jpype",
            aliases=("java-pitch-native-202x-jpype",),
            family="pitch/java-202x-native",
            description="Pitch native HLA4 Java surface exposed directly through JPype.",
            create_backend=_pitch_native_202x_jpype_backend_factory,
            discover=_discover_pitch_native_202x_runtime,
        ),
    )


def pitch_202x_plugin() -> RTIBackendPlugin:
    return backend_plugins()[1]


def pitch_native_202x_plugin() -> RTIBackendPlugin:
    return backend_plugins()[2]


__all__ = ["backend_plugins", "pitch_202x_plugin", "pitch_jpype_plugin", "pitch_native_202x_plugin", "plugin"]
