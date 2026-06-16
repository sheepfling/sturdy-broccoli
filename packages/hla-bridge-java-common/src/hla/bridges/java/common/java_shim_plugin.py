"""In-repo plugin descriptors for Java-shaped shim test backends."""
from __future__ import annotations

from typing import Any

from hla.rti.plugin_api import BackendRequest

from hla.backends.common.plugin_api import RTIBackendPlugin


def _java_shim_backend_factory(adapter: str, options: dict[str, Any]):
    from .java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend

    kernel = options.pop("kernel", None)
    shared = options.pop("shared", kernel is not None)
    return create_shared_java_shim_backend(adapter, kernel) if shared else create_java_shim_backend(adapter)


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-shim-jpype",
            aliases=("java-shim", "shim-jpype"),
            family="test/java-shim",
            description="In-process Java-shaped shim backend through the JPype adapter path.",
            create_backend=lambda request: _java_shim_backend_factory("jpype", dict(request.options)),
        ),
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-shim-py4j",
            aliases=("shim-py4j",),
            family="test/java-shim",
            description="In-process Java-shaped shim backend through the Py4J adapter path.",
            create_backend=lambda request: _java_shim_backend_factory("py4j", dict(request.options)),
        ),
    )


__all__ = ["backend_plugins"]
