"""Compatibility facade for the generic Py4J Java RTI bridge."""
from __future__ import annotations

from hla2010_rti_java_py4j.adapter import Py4JFederateAmbassadorProxy, Py4JRTIBackend

__all__ = ["Py4JFederateAmbassadorProxy", "Py4JRTIBackend"]
