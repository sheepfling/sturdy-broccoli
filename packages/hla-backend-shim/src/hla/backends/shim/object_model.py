"""Object-model helpers imported from the shared Python 2025 RTI runtime."""

from __future__ import annotations

from hla.backends.python1516_2025.object_model_runtime import (
    attribute_name_by_handle,
    attribute_names_from_handles,
    discover_existing_objects_for_current_subscription,
    has_object_registration_interest,
    matching_object_publishers,
    object_class_lineage,
    published_attributes_for_current_federate,
    subscribed_discovery_class_name,
)
