"""Placeholder 2025 ambassador contracts pending generated API import."""
from __future__ import annotations

from abc import ABC


class RTIambassador(ABC):
    """Abstract IEEE 1516.1-2025 RTI ambassador contract."""


class FederateAmbassador:
    """Default IEEE 1516.1-2025 federate ambassador callback base."""


NullFederateAmbassador = FederateAmbassador


__all__ = ["FederateAmbassador", "NullFederateAmbassador", "RTIambassador"]
