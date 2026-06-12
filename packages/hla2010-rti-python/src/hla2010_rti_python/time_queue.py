"""Compatibility composition layer for time-queue helpers."""
from __future__ import annotations

from .time_queue_delivery import PythonRTITimeQueueDeliveryMixin


class PythonRTITimeQueueMixin(PythonRTITimeQueueDeliveryMixin):
    """Time-queue surface assembled from grant and delivery/runtime mixins."""
