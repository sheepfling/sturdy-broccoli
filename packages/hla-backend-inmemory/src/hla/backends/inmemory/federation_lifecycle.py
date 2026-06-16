"""Compatibility composition layer for federation lifecycle services."""
from __future__ import annotations

from .federation_creation import PythonRTIFederationCreationMixin
from .federation_membership import PythonRTIFederationMembershipMixin


class PythonRTIFederationLifecycleMixin(
    PythonRTIFederationCreationMixin,
    PythonRTIFederationMembershipMixin,
):
    """Federation lifecycle surface assembled from creation and membership mixins."""
