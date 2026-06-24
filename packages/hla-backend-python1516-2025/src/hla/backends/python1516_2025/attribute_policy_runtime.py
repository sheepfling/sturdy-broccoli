"""Attribute-policy runtime semantics owned by the dedicated Python 2025 lane."""

from __future__ import annotations

from typing import Any

from .ddm_default_attribute_policy import (
    attribute_order_for,
    attribute_transportation_for,
    default_order_for,
    default_transportation_for,
    reflectable_attribute_names_for_subscriber,
)


def known_object_classes_for_federate(
    rti: Any,
    federate_key: int,
    object_instance: Any,
    object_class_name: str,
) -> str | None:
    federation = rti._federation_record()
    target_rti = federation.member_rtis.get(federate_key)
    if target_rti is None:
        return None
    known_class_name = target_rti._known_object_classes.get(object_instance.value)
    if known_class_name is not None:
        return known_class_name
    return rti._subscribed_discovery_class_name(federate_key, object_class_name)


__all__ = [
    "attribute_order_for",
    "attribute_transportation_for",
    "default_order_for",
    "default_transportation_for",
    "known_object_classes_for_federate",
    "reflectable_attribute_names_for_subscriber",
]
