"""Entry point descriptor for the extracted Python 2025 backend package."""
from __future__ import annotations

from hla.rti.plugin_api import RTIBackendDiscovery, RTIBackendPlugin

from .backend import Python2025BackendInfo, create_python2025_backend


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python2025",
        aliases=("python-2025", "python-2025-backend"),
        family="python-rti-2025",
        supports=("rti1516_2025",),
        description="Primary Python 2025 RTI implementation package.",
        create_backend=create_python2025_backend,
        discover=lambda: RTIBackendDiscovery(
            name="python2025",
            aliases=("python-2025", "python-2025-backend"),
            family="python-rti-2025",
            supports=("rti1516_2025",),
            description="Primary Python 2025 RTI implementation package.",
            available=True,
            info=Python2025BackendInfo(),
        ),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
