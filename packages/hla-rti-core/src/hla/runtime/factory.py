"""Version-local RTI factory for IEEE 1516.1-2010."""
from __future__ import annotations

from typing import Any

from hla.rti import create_rti_ambassador as _create_rti_ambassador


class RtiFactory:
    """Factory that bakes in the 1516e spec selection."""

    def create_rti_ambassador(self, backend: str = "inmemory", **options: Any):
        return _create_rti_ambassador(spec="rti1516e", backend=backend, **options)


def create_rti_ambassador(backend: str = "inmemory", **options: Any):
    """Create an IEEE 1516.1-2010 RTI ambassador."""

    return RtiFactory().create_rti_ambassador(backend=backend, **options)


__all__ = ["RtiFactory", "create_rti_ambassador"]
