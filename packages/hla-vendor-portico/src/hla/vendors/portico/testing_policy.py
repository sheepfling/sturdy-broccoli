"""Portico-owned verification profile policy helpers."""
from __future__ import annotations

from .real_rti_portico import PorticoRuntime, discover_portico_runtime


def discover_portico_two_federate_profile() -> PorticoRuntime:
    """Resolve the Portico runtime used by verification scenarios."""
    return discover_portico_runtime()


__all__ = ["discover_portico_two_federate_profile"]
