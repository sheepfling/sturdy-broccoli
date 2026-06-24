"""Compatibility exports for object-reflection runtime semantics."""

from __future__ import annotations

from .object_reflection_runtime import fanout_attribute_update, group_source_values_by_transport

__all__ = [
    "fanout_attribute_update",
    "group_source_values_by_transport",
]
