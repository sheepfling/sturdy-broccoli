"""Adapter class for JPype-backed Java RTI backends."""
from __future__ import annotations

from hla2010_rti_java_common.java_common import JavaRTIBackend


class JPypeRTIBackend(JavaRTIBackend):
    """JavaRTIBackend built from a JPype Java RTIambassador."""


__all__ = ["JPypeRTIBackend"]
