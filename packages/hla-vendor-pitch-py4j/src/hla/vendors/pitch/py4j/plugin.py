"""Entry point descriptor for the Pitch Py4J RTI backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti.plugin_api import BackendRequest

from hla.bridges.java.common import (
    BackendInfo,
    BackendUnavailableError,
    RTIBackendPlugin,
    reset_py4j_callback_client,
)

from .factory import create_py4j_backend
from .runtime import Py4JConfig


@dataclass(frozen=True, slots=True)
class _Pitch202XAdapterBackendInfo:
    name: str
    kind: str
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=dict)


class _Pitch202XPy4JAdapterBackend:
    def __init__(self, request: BackendRequest, *, home: str):
        self.request = request
        self.info = _Pitch202XAdapterBackendInfo(
            name="pitch-202x-py4j",
            kind="vendor/pitch/java-202x/py4j",
            details={
                "spec": "rti1516_2025",
                "vendor_surface": "hla.rti1516_202X",
                "bridge": "py4j",
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
        name="pitch-202x-py4j",
        kind="vendor/pitch/java-202x/py4j",
        details={
            **dict(runtime.details),
            "spec": "rti1516_2025",
            "vendor_surface": "hla.rti1516_202X",
            "adapter_status": "python1516_2025-wrapped",
            "bridge_ready": False,
            "counts_as_vendor_runtime": False,
        },
    )


def _pitch_py4j_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway

    from hla.vendors.pitch import launch_pitch_py4j_gateway, pitch_fedpro_local_settings_designator

    gateway = options.pop("gateway", None)
    options.setdefault("rti_factory_name", "Federate Protocol")
    options.setdefault("connect_local_settings_designator", pitch_fedpro_local_settings_designator())
    if gateway is None:
        launch_port = int(options.pop("launch_gateway_port", 0))
        port, gateway_process = launch_pitch_py4j_gateway(
            pitch_home=options.pop("pitch_home", None),
            port=launch_port,
            die_on_exit=bool(options.pop("die_on_exit", True)),
            return_proc=True,
        )
        gateway = JavaGateway(
            gateway_parameters=GatewayParameters(port=port, auto_convert=True),
            callback_server_parameters=CallbackServerParameters(port=options.pop("callback_port", 0)),
        )
        setattr(gateway, "_hla2010_gateway_process", gateway_process)
        gateway.start_callback_server()
        reset_py4j_callback_client(gateway)
        options.setdefault("shutdown_gateway_on_close", True)
    config = options.pop("config", None) or Py4JConfig(gateway=gateway, **options)
    return create_py4j_backend(config)


def _pitch_202x_py4j_backend_factory(request: BackendRequest):
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"pitch-202x-py4j only supports HLA spec {request.spec.name!r}")
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from hla.vendors.pitch import discover_pitch_runtime

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    return _Pitch202XPy4JAdapterBackend(request, home=str(runtime.home))


def pitch_py4j_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="pitch-py4j",
        aliases=("java-pitch-py4j",),
        family="pitch/java",
        description="Pitch Federate Protocol adapter through Py4J.",
        create_backend=_pitch_py4j_backend_factory,
        discover=_discover_pitch_runtime,
    )


def plugin() -> RTIBackendPlugin:
    return pitch_py4j_plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (
        plugin(),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="pitch-202x-py4j",
            aliases=("java-pitch-202x-py4j",),
            family="pitch/java-202x",
            description="Pitch vendor 202X Java surface exposed as an explicit 2025 adapter route through Py4J.",
            create_backend=_pitch_202x_py4j_backend_factory,
            discover=_discover_pitch_202x_runtime,
        ),
    )


def pitch_202x_plugin() -> RTIBackendPlugin:
    return backend_plugins()[1]


__all__ = ["backend_plugins", "pitch_202x_plugin", "pitch_py4j_plugin", "plugin"]
