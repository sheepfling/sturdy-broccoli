"""Pure Python verification profile policy helpers."""
from __future__ import annotations

from .engine import InMemoryRTIEngine


def prepare_python_two_federate_profile() -> InMemoryRTIEngine:
    """Return the shared in-memory engine used by two-federate verification."""
    return InMemoryRTIEngine()


__all__ = ["prepare_python_two_federate_profile"]
