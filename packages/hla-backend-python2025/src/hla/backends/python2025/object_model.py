"""Compatibility exports for object-model runtime semantics."""

from __future__ import annotations

from .object_model_runtime import (
    attribute_name_by_handle,
    attribute_names_from_handles,
    discover_existing_objects_for_current_subscription,
    has_object_registration_interest,
    matching_object_publishers,
    object_class_lineage,
    published_attributes_for_current_federate,
    subscribed_discovery_class_name,
)

__all__ = [
    "attribute_name_by_handle",
    "attribute_names_from_handles",
    "discover_existing_objects_for_current_subscription",
    "has_object_registration_interest",
    "matching_object_publishers",
    "object_class_lineage",
    "published_attributes_for_current_federate",
    "subscribed_discovery_class_name",
]
