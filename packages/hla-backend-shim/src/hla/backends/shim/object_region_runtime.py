"""Object-region helpers imported from the shared Python 2025 RTI runtime."""

from __future__ import annotations

from hla.backends.python1516_2025.object_region_runtime import (
    associate_regions_for_updates,
    attribute_region_pairs,
    change_attribute_order_type,
    change_default_attribute_order_type,
    change_default_attribute_transportation_type,
    coerce_range_bounds,
    commit_region_modifications,
    create_region,
    delete_region,
    get_dimension_handle_set,
    get_range_bounds,
    object_instance_region_values,
    query_attribute_transportation_type,
    ranges_overlap,
    region_owner_key,
    region_sets_overlap,
    region_values_from_handles,
    regions_overlap_pair,
    register_object_instance_with_regions,
    request_attribute_transportation_type_change,
    set_range_bounds,
    subscribe_object_class_attributes_with_regions,
    unassociate_regions_for_updates,
    unsubscribe_object_class_attributes_with_regions,
)
