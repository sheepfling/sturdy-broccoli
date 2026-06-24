"""Version-local RTI backend discovery and creation helpers for IEEE 1516.1-2010."""
from __future__ import annotations

from hla.rti import (
    available_backend_plugins,
    iter_rti_backend_plugins,
    register_backend_plugin,
)
from hla.rti import create_backend as _create_backend
from hla.rti import discover_rti_backends as _discover_rti_backends
from .factory import create_rti_ambassador


def create_backend(backend="python1516e", **options):
    return _create_backend(backend, spec="rti1516e", **options)


def discover_rti_backends(*, probe: bool = False):
    return _discover_rti_backends(spec="rti1516e", probe=probe)

__all__ = [
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "discover_rti_backends",
    "iter_rti_backend_plugins",
    "register_backend_plugin",
]
