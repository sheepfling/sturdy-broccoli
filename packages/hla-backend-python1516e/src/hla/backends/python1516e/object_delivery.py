"""Compatibility composition layer for object delivery helpers."""
from __future__ import annotations

from .object_delivery_services import PythonRTIObjectDeliveryServicesMixin


class PythonRTIObjectDeliveryMixin(PythonRTIObjectDeliveryServicesMixin):
    """Object delivery surface assembled from transport and service mixins."""
