"""Time-management domain root."""
from __future__ import annotations

from .time_queue import PythonRTITimeQueueMixin
from .time_services import PythonRTITimeServicesMixin


class PythonRTITimeMixin(PythonRTITimeServicesMixin, PythonRTITimeQueueMixin):
    """Composed time-management domain root."""
