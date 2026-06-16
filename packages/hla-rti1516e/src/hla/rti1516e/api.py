"""Compatibility wrapper for the standard-facing HLA API facade."""
from __future__ import annotations

from .federate_ambassador import FederateAmbassador, NullFederateAmbassador
from .rti_ambassador import RTIambassador

RTIAmbassador = RTIambassador
PythonicRTIAmbassadorMixin = RTIambassador

__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "PythonicRTIAmbassadorMixin",
    "RTIAmbassador",
    "RTIambassador",
]
