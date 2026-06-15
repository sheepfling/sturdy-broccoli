"""Temporary root facade for RTI backend discovery and creation helpers."""
from __future__ import annotations

from hla2010_rti_runtime_common import (
    available_backend_plugins,
    create_backend,
    create_rti_ambassador,
    debug_rti_backend_registry,
    discover_rti_backends,
    get_rti_factory,
    iter_rti_backend_plugins,
    iter_rti_factories,
    register_backend_plugin,
)

__all__ = [
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "debug_rti_backend_registry",
    "discover_rti_backends",
    "get_rti_factory",
    "iter_rti_backend_plugins",
    "iter_rti_factories",
    "register_backend_plugin",
]
