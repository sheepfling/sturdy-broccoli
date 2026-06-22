"""Version-local RTI factory for IEEE 1516.1-2025."""
from __future__ import annotations

from typing import Any

from hla.rti import HlaFactoryRegistry as _HlaFactoryRegistry
from hla.rti import create_rti_ambassador as _create_rti_ambassador


def create_rti_ambassador(backend: str = "python2025", **options: Any):
    """Create an IEEE 1516.1-2025 RTI ambassador."""

    return _create_rti_ambassador(spec="rti1516_2025", backend=backend, **options)


def create_hla_factory(provider: str = "python2025", **options: Any):
    """Create a composed IEEE 1516.1-2025 factory for one provider route."""

    return _HlaFactoryRegistry.get("rti1516_2025", provider=provider, **options)


__all__ = ["create_hla_factory", "create_rti_ambassador"]
