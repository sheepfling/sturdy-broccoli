"""Compatibility composition layer for DDM helpers."""

from __future__ import annotations

from .ddm_services import PythonRTIDdmServicesMixin


class PythonRTIDdmMixin(PythonRTIDdmServicesMixin):
    """DDM surface assembled from region helpers and service mixins."""
