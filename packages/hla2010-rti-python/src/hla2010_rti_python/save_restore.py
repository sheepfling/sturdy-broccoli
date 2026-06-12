"""Compatibility composition layer for save/restore services."""

from __future__ import annotations

from .save_restore_services import PythonRTISaveRestoreServicesMixin


class PythonRTISaveRestoreMixin(PythonRTISaveRestoreServicesMixin):
    """Save/restore surface assembled from state helpers and public services."""


__all__ = ["PythonRTISaveRestoreMixin"]
