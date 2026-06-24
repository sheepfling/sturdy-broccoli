"""Entry point descriptor for the extracted Python 2025 backend package."""
from __future__ import annotations

from hla.rti.plugin_api import RTIBackendDiscovery, RTIBackendPlugin

from .backend import Python2025BackendInfo, create_python2025_backend


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python1516_2025",
        aliases=("python-1516-2025",),
        family="python-rti-1516-2025",
        supports=("rti1516_2025",),
        description="Primary Python 1516.1-2025 RTI implementation package.",
        create_backend=create_python2025_backend,
        discover=lambda: RTIBackendDiscovery(
            name="python1516_2025",
            aliases=("python-1516-2025",),
            family="python-rti-1516-2025",
            supports=("rti1516_2025",),
            description="Primary Python 1516.1-2025 RTI implementation package.",
            available=True,
            info=Python2025BackendInfo(),
        ),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
