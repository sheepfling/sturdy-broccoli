"""Entry point descriptor for the 2025 shim backend."""
from __future__ import annotations

from hla.rti.plugin_api import RTIBackendDiscovery, RTIBackendPlugin

from .backend import create_shim_backend


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="shim",
        aliases=("2025-shim", "rti1516_2025-shim", "reference-shim"),
        family="shim",
        supports=("rti1516_2025",),
        description="Spec-shaped IEEE 1516.1-2025 RTI shim backend.",
        create_backend=create_shim_backend,
        discover=lambda: RTIBackendDiscovery(
            name="shim",
            aliases=("2025-shim", "rti1516_2025-shim", "reference-shim"),
            family="shim",
            supports=("rti1516_2025",),
            description="Spec-shaped IEEE 1516.1-2025 RTI shim backend.",
            available=True,
        ),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
