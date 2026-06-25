"""Retired shim plugin module kept only so legacy imports resolve cleanly."""
from __future__ import annotations

from hla.rti.plugin_api import RTIBackendPlugin


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return ()


__all__ = ["backend_plugins"]
