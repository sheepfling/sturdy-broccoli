"""Compatibility wrapper for the runtime-facing HLA API facade.

New code should import the clean spec layer from :mod:`hla.rti1516e.spec` or the
explicit runtime facade from :mod:`hla.rti1516e.runtime_api`.
"""
from __future__ import annotations

from .runtime_api import (
    FederateAmbassador,
    NullFederateAmbassador,
    PythonicRTIAmbassadorMixin,
    RTIAmbassador,
    RTIambassador,
)

__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "PythonicRTIAmbassadorMixin",
    "RTIAmbassador",
    "RTIambassador",
]
