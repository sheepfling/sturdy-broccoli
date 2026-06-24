"""Compatibility exports for declaration-management runtime semantics."""

from __future__ import annotations

from .declaration_management_runtime import (
    publish_object_class_attributes,
    release_multiple_object_instance_names,
    release_object_instance_name,
    reserve_multiple_object_instance_names,
    reserve_object_instance_name,
    subscribe_object_class_attributes,
    unpublish_object_class,
    unpublish_object_class_attributes,
    unsubscribe_object_class,
    unsubscribe_object_class_attributes,
)

__all__ = [
    "publish_object_class_attributes",
    "release_multiple_object_instance_names",
    "release_object_instance_name",
    "reserve_multiple_object_instance_names",
    "reserve_object_instance_name",
    "subscribe_object_class_attributes",
    "unpublish_object_class",
    "unpublish_object_class_attributes",
    "unsubscribe_object_class",
    "unsubscribe_object_class_attributes",
]
