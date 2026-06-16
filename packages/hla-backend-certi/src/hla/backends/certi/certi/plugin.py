"""Entry point descriptors for CERTI RTI backends."""
from __future__ import annotations

from typing import Any

from hla.rti.plugin_api import BackendRequest

from hla.backends.common import BackendInfo, BackendUnavailableError, RTIBackendPlugin


def _discover_certi_runtime() -> BackendInfo | None:
    try:
        from hla.backends.certi.real_rti_certi import discover_certi_runtime

        runtime = discover_certi_runtime()
        return BackendInfo(
            name="CERTI",
            kind="native/certi",
            details={"home": str(runtime.home), "profile": runtime.profile},
        )
    except BackendUnavailableError:
        return None


def _certi_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    from . import CERTIConfig, create_certi_backend
    from hla.transports.common import coerce_transport_spec

    transport = coerce_transport_spec(options.pop("transport", None))
    config = options.pop("config", None) or CERTIConfig(transport=transport, **options)
    return create_certi_backend(config)


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="certi",
        aliases=("certi-native", "native-certi"),
        family="certi",
        description="CERTI RTI adapter through the Python service transport.",
        create_backend=_certi_backend_factory,
        discover=_discover_certi_runtime,
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
