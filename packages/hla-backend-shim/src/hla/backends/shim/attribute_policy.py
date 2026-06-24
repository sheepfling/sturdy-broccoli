"""Compatibility wrapper for DDM overlap and attribute-policy semantics."""

from __future__ import annotations

from hla.backends.python1516_2025.attribute_policy import known_object_classes_for_federate
from hla.backends.python1516_2025.ddm_default_attribute_policy import (
    attribute_order_for,
    attribute_transportation_for,
    default_order_for,
    default_transportation_for,
    reflectable_attribute_names_for_subscriber,
)


__all__ = [
    "attribute_order_for",
    "attribute_transportation_for",
    "default_order_for",
    "default_transportation_for",
    "known_object_classes_for_federate",
    "reflectable_attribute_names_for_subscriber",
]
