"""Runtime-owned RTI factory and plugin integration helpers."""
# pyright: reportUnsupportedDunderAll=false

from __future__ import annotations

from .factory import RtiFactory, create_rti_ambassador


def __getattr__(name: str):
    if name in {
        "available_backend_plugins",
        "create_backend",
        "discover_rti_backends",
        "iter_rti_backend_plugins",
        "register_backend_plugin",
    }:
        from . import rti1516e

        return getattr(rti1516e, name)
    raise AttributeError(name)

__all__ = [
    "RtiFactory",
    "available_backend_plugins",
    "create_backend",
    "create_rti_ambassador",
    "discover_rti_backends",
    "iter_rti_backend_plugins",
    "register_backend_plugin",
]
