"""Compatibility facade for the generic Py4J Java RTI bridge."""
from __future__ import annotations

from hla2010_rti_java_py4j.factory import create_py4j_backend, rti_ambassador

__all__ = ["create_py4j_backend", "rti_ambassador"]
