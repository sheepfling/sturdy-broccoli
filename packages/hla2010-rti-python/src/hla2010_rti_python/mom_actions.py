"""Compatibility composition layer for MOM action helpers."""

from __future__ import annotations

from .mom_action_routing import PythonRTIMomActionRoutingMixin


class PythonRTIMomActionsMixin(PythonRTIMomActionRoutingMixin):
    """MOM action surface assembled from decoding and routing mixins."""
