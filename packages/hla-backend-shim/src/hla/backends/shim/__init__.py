"""Package-root exports for the deprecated wrapper-only 2025 compatibility lane."""
from __future__ import annotations

from .backend import (
    Shim2025Backend,
    Shim2025RTIAmbassador,
    create_shim_backend,
)

__all__ = [
    "Shim2025Backend",
    "Shim2025RTIAmbassador",
    "create_shim_backend",
]
