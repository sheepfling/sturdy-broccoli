"""Compatibility wrapper for the standard-facing HLA API facade."""
from __future__ import annotations

from .ambassadors import NullFederateAmbassador
from .federate_ambassador import FederateAmbassador
from .rti_ambassador import RTIambassador

RTIAmbassador = RTIambassador
RTIambassadorBase = RTIambassador

__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "RTIAmbassador",
    "RTIambassadorBase",
    "RTIambassador",
]
