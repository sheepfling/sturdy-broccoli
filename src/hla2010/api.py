"""Compatibility wrapper for the runtime-facing HLA API facade.

New code should import the clean spec layer from :mod:`hla2010.spec` or the
explicit runtime facade from :mod:`hla2010.runtime_api`.
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
