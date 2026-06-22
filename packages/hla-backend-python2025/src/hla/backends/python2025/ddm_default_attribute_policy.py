"""DDM overlap and default-attribute-policy runtime semantics."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.datatypes import RangeBounds
from hla.rti1516_2025.enums import OrderType


def ranges_overlap(left: RangeBounds, right: RangeBounds) -> bool:
    return int(left.lower) <= int(right.upper) and int(right.lower) <= int(left.upper)


def region_owner_key(rti: Any, preferred_key: int, region_value: int) -> int | None:
    federation = rti._federation_record()
    if region_value in federation.member_regions.get(preferred_key, {}):
        return preferred_key
    for member_key, regions in federation.member_regions.items():
        if region_value in regions:
            return member_key
    return None


def regions_overlap_pair(rti: Any, source_key: int, source_region: int, target_key: int, target_region: int) -> bool:
    federation = rti._federation_record()
    resolved_source_key = region_owner_key(rti, source_key, source_region)
    resolved_target_key = region_owner_key(rti, target_key, target_region)
    if resolved_source_key is None or resolved_target_key is None:
        return False
    source_dims = federation.member_regions.get(resolved_source_key, {}).get(source_region, set())
    target_dims = federation.member_regions.get(resolved_target_key, {}).get(target_region, set())
    common_dimensions = set(source_dims) & set(target_dims)
    if not common_dimensions:
        return False
    source_bounds = federation.member_region_bounds.get(resolved_source_key, {}).get(source_region, {})
    target_bounds = federation.member_region_bounds.get(resolved_target_key, {}).get(target_region, {})
    for dimension_name in common_dimensions:
        default_bounds = RangeBounds(0, rti._dimension_default_upper_bound(dimension_name))
        if not ranges_overlap(source_bounds.get(dimension_name, default_bounds), target_bounds.get(dimension_name, default_bounds)):
            return False
    return True


def region_sets_overlap(rti: Any, source_key: int, source_regions: set[int], target_key: int, target_regions: set[int]) -> bool:
    if not source_regions or not target_regions:
        return True
    return any(
        regions_overlap_pair(rti, source_key, source_region, target_key, target_region)
        for source_region in source_regions
        for target_region in target_regions
    )


def reflectable_attribute_names_for_subscriber(
    rti: Any,
    source_key: int,
    subscriber_key: int,
    record: Any,
    discovery_class_name: str,
    subscribed_names: set[str],
) -> set[str]:
    region_subscription = (
        rti._federation_record()
        .subscribed_object_regions.get(subscriber_key, {})
        .get(discovery_class_name, {})
    )
    if not region_subscription:
        return subscribed_names
    reflected: set[str] = set()
    for attribute_name in subscribed_names:
        target_regions = set(region_subscription.get(attribute_name, set()))
        source_regions = set(record.update_regions.get(attribute_name, set()))
        if region_sets_overlap(rti, source_key, source_regions, subscriber_key, target_regions):
            reflected.add(attribute_name)
    return reflected


def default_transportation_for(
    rti: Any,
    object_class_name: str,
    values_by_handle: Mapping[Any, bytes],
) -> Any:
    transportation_names = {
        rti._default_attribute_transportation.get(
            (object_class_name, rti._attribute_name_by_handle(object_class_name, attribute)),
            "HLAreliable",
        )
        for attribute in values_by_handle
    }
    return rti._transportation_handle_by_name(sorted(transportation_names)[0])


def attribute_transportation_for(
    rti: Any,
    record: Any,
    values_by_handle: Mapping[Any, bytes],
) -> Any:
    transportation_names = {
        record.attribute_transportation.get(
            rti._attribute_name_by_handle(record.object_class_name, attribute),
            rti._default_attribute_transportation.get(
                (record.object_class_name, rti._attribute_name_by_handle(record.object_class_name, attribute)),
                "HLAreliable",
            ),
        )
        for attribute in values_by_handle
    }
    return rti._transportation_handle_by_name(sorted(transportation_names)[0])


def default_order_for(
    rti: Any,
    object_class_name: str,
    values_by_handle: Mapping[Any, bytes],
) -> OrderType:
    orders = {
        rti._default_attribute_order.get(
            (object_class_name, rti._attribute_name_by_handle(object_class_name, attribute)),
            OrderType.RECEIVE,
        )
        for attribute in values_by_handle
    }
    return sorted(orders, key=lambda value: value.name)[0]


def attribute_order_for(
    rti: Any,
    record: Any,
    values_by_handle: Mapping[Any, bytes],
) -> OrderType:
    orders = {
        record.attribute_order.get(
            rti._attribute_name_by_handle(record.object_class_name, attribute),
            rti._default_attribute_order.get(
                (record.object_class_name, rti._attribute_name_by_handle(record.object_class_name, attribute)),
                OrderType.RECEIVE,
            ),
        )
        for attribute in values_by_handle
    }
    return sorted(orders, key=lambda value: value.name)[0]


__all__ = [
    "attribute_order_for",
    "attribute_transportation_for",
    "default_order_for",
    "default_transportation_for",
    "ranges_overlap",
    "reflectable_attribute_names_for_subscriber",
    "region_owner_key",
    "region_sets_overlap",
    "regions_overlap_pair",
]
