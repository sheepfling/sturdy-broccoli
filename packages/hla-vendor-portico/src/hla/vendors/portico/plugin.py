"""Entry point descriptors for Portico RTI backend plugins."""
from __future__ import annotations

from typing import Any

from hla.bridges.java.common import BackendInfo, BackendUnavailableError, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest


def _discover_portico_runtime() -> BackendInfo | None:
    try:
        from hla.vendors.portico import discover_portico_runtime

        runtime = discover_portico_runtime()
        return BackendInfo(name="Portico", kind="vendor/portico", details={"home": str(runtime.home)})
    except BackendUnavailableError:
        return None


def _portico_jpype_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options)
    from hla.bridges.java.jpype import create_jpype_backend
    from hla.vendors.portico import discover_portico_runtime

    portico_home = options.pop("portico_home", None)
    runtime = discover_portico_runtime(portico_home)
    config = options.pop("config", None) or runtime.jpype_config(**options)
    return create_jpype_backend(config)


def _portico_py4j_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options)
    from hla.bridges.java.py4j import Py4JConfig, create_py4j_backend
    from hla.vendors.portico import launch_portico_py4j_gateway
    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway

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


def portico_jpype_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="portico-jpype",
        aliases=("java-portico-jpype", "portico"),
        family="portico/java",
        description="Portico RTI adapter through JPype.",
        create_backend=_portico_jpype_backend_factory,
        discover=_discover_portico_runtime,
    )


def portico_py4j_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="portico-py4j",
        aliases=("java-portico-py4j",),
        family="portico/java",
        description="Portico RTI adapter through Py4J.",
        create_backend=_portico_py4j_backend_factory,
        discover=_discover_portico_runtime,
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (portico_jpype_plugin(), portico_py4j_plugin())


__all__ = ["backend_plugins", "portico_jpype_plugin", "portico_py4j_plugin"]
