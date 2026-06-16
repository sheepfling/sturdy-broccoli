"""Version-local RTI factory for IEEE 1516.1-2025."""
from __future__ import annotations

from typing import Any

from hla.rti import create_rti_ambassador as _create_rti_ambassador


def create_rti_ambassador(backend: str = "shim", **options: Any):
    """Create an IEEE 1516.1-2025 RTI ambassador."""

    return _create_rti_ambassador(spec="rti1516_2025", backend=backend, **options)


__all__ = ["create_rti_ambassador"]
