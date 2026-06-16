"""Compatibility composition layer for object-delivery services."""
from __future__ import annotations

from .object_delivery_control import PythonRTIObjectDeliveryControlMixin


class PythonRTIObjectDeliveryServicesMixin(PythonRTIObjectDeliveryControlMixin):
    """Object-delivery surface assembled from attribute, interaction, and control mixins."""
