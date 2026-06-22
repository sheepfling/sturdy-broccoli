"""Entry point descriptor for the deprecated wrapper-only 2025 compatibility package."""
from __future__ import annotations

from hla.backends.python2025.compatibility_wrapper import ShimBackendInfo
from hla.rti.plugin_api import RTIBackendDiscovery, RTIBackendPlugin

from .backend import create_shim_backend


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="shim",
        aliases=(),
        family="compatibility-wrapper-2025",
        supports=("rti1516_2025",),
        description="Deprecated compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation; slated for removal.",
        create_backend=create_shim_backend,
        discover=lambda: RTIBackendDiscovery(
            name="shim",
            aliases=(),
            family="compatibility-wrapper-2025",
            supports=("rti1516_2025",),
            description="Deprecated compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation; slated for removal.",
            available=True,
            info=ShimBackendInfo(),
        ),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
