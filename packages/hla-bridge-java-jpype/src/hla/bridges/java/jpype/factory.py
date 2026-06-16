"""Factory helpers for JPype-backed Java RTI backends."""
from __future__ import annotations

from hla.bridges.java.common import BackendInfo, make_rti_ambassador
from .adapter import JPypeRTIBackend
from .runtime import JPypeBridge, JPypeConfig


def create_jpype_backend(config: JPypeConfig = JPypeConfig()) -> JPypeRTIBackend:
    """Create a Java RTI backend using ``hla.rti1516e.RtiFactoryFactory``."""

    bridge = JPypeBridge(config)
    try:
        factory_factory = bridge.JClass("hla.rti1516e.RtiFactoryFactory")
        if config.rti_factory_name:
            factory = factory_factory.getRtiFactory(config.rti_factory_name)
        else:
            factory = factory_factory.getRtiFactory()
        java_rti = factory.getRtiAmbassador()
        try:
            name = str(factory.rtiName())
        except Exception:
            name = "jpype"
        try:
            version = str(factory.rtiVersion())
        except Exception:
            version = None
    except BaseException:
        bridge.close()
        raise

    info = BackendInfo(
        name=name,
        kind="java/jpype",
        version=version,
        details={"rti_factory_name": config.rti_factory_name, "classpath": list(config.classpath)},
    )
    return JPypeRTIBackend(
        java_rti_ambassador=java_rti,
        bridge=bridge,
        info=info,
        connect_local_settings_designator=config.connect_local_settings_designator,
    )


def rti_ambassador(config: JPypeConfig = JPypeConfig()):
    """Convenience: return a DelegatingRTIAmbassador backed by JPype."""

    return make_rti_ambassador(create_jpype_backend(config))


__all__ = ["create_jpype_backend", "rti_ambassador"]
