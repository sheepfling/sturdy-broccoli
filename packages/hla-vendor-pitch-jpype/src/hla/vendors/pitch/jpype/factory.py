"""Compatibility facade for the generic JPype Java RTI bridge."""
from __future__ import annotations

from hla.bridges.java.jpype.factory import create_jpype_backend, rti_ambassador

__all__ = ["create_jpype_backend", "rti_ambassador"]
