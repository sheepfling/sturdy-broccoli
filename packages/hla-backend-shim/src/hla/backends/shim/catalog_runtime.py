"""Legacy-package re-export for the live Python 2025 RTI catalog/runtime helpers."""

from __future__ import annotations

from hla.backends.python2025.catalog_runtime import (
    attribute_handles,
    interaction_class_name,
    object_class_name,
    object_instance_record,
    object_instance_record_known,
    parameter_handles,
    synchronization_required_federates,
    transportation_handle_by_name,
)

__all__ = [
    "attribute_handles",
    "interaction_class_name",
    "object_class_name",
    "object_instance_record",
    "object_instance_record_known",
    "parameter_handles",
    "synchronization_required_federates",
    "transportation_handle_by_name",
]
