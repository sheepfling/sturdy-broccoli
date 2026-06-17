"""In-repo plugin descriptors for Java-shaped shim test backends."""
from __future__ import annotations

from typing import Any

from hla.rti.plugin_api import BackendRequest

from hla.backends.common.plugin_api import RTIBackendPlugin


def _java_shim_backend_factory(adapter: str, request: BackendRequest):
    if request.spec.name == "rti1516_2025":
        from .java_shim_2025 import JavaRouteShim2025Backend

        return JavaRouteShim2025Backend(adapter, request)
    if request.spec.name != "rti1516e":
        raise ValueError(f"Java shim route does not support HLA spec {request.spec.name!r}")

    from .java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend

    options: dict[str, Any] = dict(request.options)
    kernel = options.pop("kernel", None)
    shared = options.pop("shared", kernel is not None)
    return create_shared_java_shim_backend(adapter, kernel) if shared else create_java_shim_backend(adapter)


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    from .java_intake_backend import create_java_intake_backend, discover_java_intake_backend
    from .java_standard_2010 import create_java_standard_2010_backend, discover_java_standard_2010
    from .java_standard_2025 import create_java_standard_2025_backend, discover_java_standard_2025

    return (
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-2010-jpype",
            aliases=(),
            family="intake/java",
            description="Generic user-supplied Java 2010 RTI jar through the JPype bridge.",
            create_backend=lambda request: create_java_intake_backend("2010", "jpype", request),
            discover=lambda: discover_java_intake_backend("2010", "jpype"),
        ),
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-2010-py4j",
            aliases=(),
            family="intake/java",
            description="Generic user-supplied Java 2010 RTI jar through the Py4J bridge.",
            create_backend=lambda request: create_java_intake_backend("2010", "py4j", request),
            discover=lambda: discover_java_intake_backend("2010", "py4j"),
        ),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="java-2025-jpype",
            aliases=(),
            family="intake/java",
            description="Generic user-supplied Java 2025 RTI jar discovery route through JPype.",
            create_backend=lambda request: create_java_intake_backend("2025", "jpype", request),
            discover=lambda: discover_java_intake_backend("2025", "jpype"),
        ),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="java-2025-py4j",
            aliases=(),
            family="intake/java",
            description="Generic user-supplied Java 2025 RTI jar discovery route through Py4J.",
            create_backend=lambda request: create_java_intake_backend("2025", "py4j", request),
            discover=lambda: discover_java_intake_backend("2025", "py4j"),
        ),
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-standard-2010-jpype",
            aliases=(),
            family="standard/java",
            description="HLA-X Java 2010 standard shim jar through the JPype bridge.",
            create_backend=lambda request: create_java_standard_2010_backend("jpype", request),
            discover=lambda: discover_java_standard_2010("jpype"),
        ),
        RTIBackendPlugin(
            supports=("rti1516e",),
            name="java-standard-2010-py4j",
            aliases=(),
            family="standard/java",
            description="HLA-X Java 2010 standard shim jar through the Py4J bridge.",
            create_backend=lambda request: create_java_standard_2010_backend("py4j", request),
            discover=lambda: discover_java_standard_2010("py4j"),
        ),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="java-standard-2025-jpype",
            aliases=(),
            family="standard/java",
            description="HLA-X Java 2025 standard shim jar through the JPype bridge.",
            create_backend=lambda request: create_java_standard_2025_backend("jpype", request),
            discover=lambda: discover_java_standard_2025("jpype"),
        ),
        RTIBackendPlugin(
            supports=("rti1516_2025",),
            name="java-standard-2025-py4j",
            aliases=(),
            family="standard/java",
            description="HLA-X Java 2025 standard shim jar through the Py4J bridge.",
            create_backend=lambda request: create_java_standard_2025_backend("py4j", request),
            discover=lambda: discover_java_standard_2025("py4j"),
        ),
        RTIBackendPlugin(
            supports=("rti1516e", "rti1516_2025"),
            name="java-shim-jpype",
            aliases=("java-shim", "shim-jpype"),
            family="test/java-shim",
            description="In-process Java-shaped shim backend through the JPype adapter path.",
            create_backend=lambda request: _java_shim_backend_factory("jpype", request),
        ),
        RTIBackendPlugin(
            supports=("rti1516e", "rti1516_2025"),
            name="java-shim-py4j",
            aliases=("shim-py4j",),
            family="test/java-shim",
            description="In-process Java-shaped shim backend through the Py4J adapter path.",
            create_backend=lambda request: _java_shim_backend_factory("py4j", request),
        ),
    )


__all__ = ["backend_plugins"]
