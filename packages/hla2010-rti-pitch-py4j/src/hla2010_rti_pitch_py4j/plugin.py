"""Entry point descriptor for the Pitch Py4J RTI backend."""
from __future__ import annotations

from typing import Any

from hla2010.backends.base import BackendInfo, BackendUnavailableError
from hla2010.rti import RTIBackendPlugin, _reset_py4j_callback_client

from .factory import create_py4j_backend
from .runtime import Py4JConfig


def _discover_pitch_runtime() -> BackendInfo | None:
    try:
        from hla2010_rti_pitch_common import discover_pitch_runtime

        runtime = discover_pitch_runtime()
        return BackendInfo(name="Pitch", kind="vendor/pitch", details={"home": str(runtime.home)})
    except BackendUnavailableError:
        return None


def _pitch_py4j_backend_factory(options: dict[str, Any]):
    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway

    from hla2010_rti_pitch_common import launch_pitch_py4j_gateway, pitch_fedpro_local_settings_designator

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


def pitch_py4j_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
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
    return (plugin(),)


__all__ = ["backend_plugins", "pitch_py4j_plugin", "plugin"]
