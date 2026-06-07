"""Federation lifecycle and synchronization domain root."""
from __future__ import annotations

from .federation_lifecycle import PythonRTIFederationLifecycleMixin
from .federation_sync import PythonRTIFederationSyncMixin


class PythonRTIFederationMixin(
    PythonRTIFederationLifecycleMixin,
    PythonRTIFederationSyncMixin,
):
    """Composed federation domain root."""


__all__ = ["PythonRTIFederationMixin"]
