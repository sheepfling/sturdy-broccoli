"""Compatibility composition layer for time-management services."""
from __future__ import annotations

from .time_public_services import PythonRTITimePublicServicesMixin


class PythonRTITimeServicesMixin(PythonRTITimePublicServicesMixin):
    """Time-management surface assembled from validation and public-service mixins."""
