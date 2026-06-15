"""Runtime-facing Pythonic HLA API facade."""
from __future__ import annotations

from ._spec_impl import FederateAmbassadorSpec, RTIambassadorSpec


class RTIambassador(RTIambassadorSpec):
    """Abstract runtime-facing RTI ambassador base."""

    pass


class FederateAmbassador(FederateAmbassadorSpec):
    """Runtime-facing federate callback base."""

    pass


RTIAmbassador = RTIambassador
NullFederateAmbassador = FederateAmbassador

__all__ = ["RTIambassador", "RTIAmbassador", "FederateAmbassador", "NullFederateAmbassador"]
