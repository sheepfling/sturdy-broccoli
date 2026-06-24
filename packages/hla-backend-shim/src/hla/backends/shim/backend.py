"""Deprecated compatibility wrapper for the live Python 2025 RTI backend."""

from __future__ import annotations

from hla.backends.python1516_2025.backend import (
    MOM_2025_FEDERATE_ADJUST_LEAVES,
    MOM_2025_FEDERATE_REQUEST_LEAVES,
    MOM_2025_FEDERATE_SERVICE_LEAVES,
    MOM_2025_FEDERATION_ADJUST_LEAVES,
    MOM_2025_FEDERATION_REQUEST_LEAVES,
    MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES,
)
from hla.backends.python1516_2025.compatibility_wrapper import (
    Shim2025Backend,
    Shim2025RTIAmbassador,
    create_shim_backend,
)

__all__ = [
    "MOM_2025_FEDERATE_ADJUST_LEAVES",
    "MOM_2025_FEDERATE_REQUEST_LEAVES",
    "MOM_2025_FEDERATE_SERVICE_LEAVES",
    "MOM_2025_FEDERATION_ADJUST_LEAVES",
    "MOM_2025_FEDERATION_REQUEST_LEAVES",
    "MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES",
    "Shim2025Backend",
    "Shim2025RTIAmbassador",
    "create_shim_backend",
]
