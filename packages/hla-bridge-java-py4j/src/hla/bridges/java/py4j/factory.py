"""Factory helpers for Py4J-backed Java RTI backends."""
from __future__ import annotations

from hla.bridges.java.common import BackendInfo, make_rti_ambassador
from .adapter import Py4JRTIBackend
from .runtime import Py4JBridge, Py4JConfig


def create_py4j_backend(config: Py4JConfig = Py4JConfig()) -> Py4JRTIBackend:
    """Create a Java RTI backend using a Py4J gateway and RtiFactoryFactory."""

    bridge = Py4JBridge(config)
    try:
        factory_factory = bridge.gateway.jvm
        for part in bridge.api_profile.factory_factory_class.split("."):
            factory_factory = getattr(factory_factory, part)
        if config.rti_factory_name:
            factory = factory_factory.getRtiFactory(config.rti_factory_name)
        else:
            factory = factory_factory.getRtiFactory()
        java_rti = factory.getRtiAmbassador()
        try:
            name = str(factory.rtiName())
        except Exception:
            name = "py4j"
        try:
            version = str(factory.rtiVersion())
        except Exception:
            version = None
    except BaseException:
        bridge.close()
        raise

    info = BackendInfo(
        name=name,
        kind="java/py4j",
        version=version,
        details={"rti_factory_name": config.rti_factory_name},
    )
    return Py4JRTIBackend(
        java_rti_ambassador=java_rti,
        bridge=bridge,
        info=info,
        connect_local_settings_designator=config.connect_local_settings_designator,
    )


def rti_ambassador(config: Py4JConfig = Py4JConfig()):
    """Convenience: return a DelegatingRTIAmbassador backed by Py4J."""

    return make_rti_ambassador(create_py4j_backend(config))


__all__ = ["create_py4j_backend", "rti_ambassador"]
