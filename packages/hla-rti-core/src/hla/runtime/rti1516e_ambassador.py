"""Runtime-facing 1516e ambassador classes."""

from __future__ import annotations

from hla.rti1516e.raw_api import RTIambassador as UnimplementedRTIambassador
from hla.rti1516e.rti_ambassador import RTIambassador

__all__ = [
    "RTIambassador",
    "UnimplementedRTIambassador",
]
