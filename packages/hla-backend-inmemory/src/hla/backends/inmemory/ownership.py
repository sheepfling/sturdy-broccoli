"""Compatibility composition layer for ownership-management services."""
from __future__ import annotations

from .ownership_services import PythonRTIOwnershipServicesMixin


class PythonRTIOwnershipMixin(PythonRTIOwnershipServicesMixin):
    """Ownership surface assembled from core helpers and public services."""


__all__ = ["PythonRTIOwnershipMixin"]
