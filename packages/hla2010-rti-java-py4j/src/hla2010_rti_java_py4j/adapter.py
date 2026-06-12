"""Adapter classes for Py4J-backed Java RTI backends."""
from __future__ import annotations

from hla2010_rti_java_common.java_common import JavaRTIBackend
from .runtime import Py4JFederateAmbassadorProxy


class Py4JRTIBackend(JavaRTIBackend):
    """JavaRTIBackend built from a Py4J Java RTIambassador."""


__all__ = ["Py4JFederateAmbassadorProxy", "Py4JRTIBackend"]
