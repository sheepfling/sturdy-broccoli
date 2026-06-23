"""Object-region and attribute policy helpers owned by the dedicated Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.datatypes import RangeBounds
from hla.rti1516_2025.exceptions import (
    AttributeNotOwned,
    InvalidRegion,
    InvalidRegionContext,
    RegionDoesNotContainSpecifiedDimension,
)
from hla.rti1516_2025.handles import AttributeHandle, DimensionHandle, RegionHandle
from hla.backends.python2025.ddm_default_attribute_policy import (
    ranges_overlap,
    region_owner_key,
    region_sets_overlap,
    regions_overlap_pair,
)


def create_region(rti: Any, dimensions: Any) -> RegionHandle:
    dimension_names = {rti.getDimensionName(dimension) for dimension in set(dimensions)}
    if not dimension_names:
        raise InvalidRegionContext("createRegion requires at least one dimension")
    federation = rti._federation_record()
    region = RegionHandle(federation.next_region_handle)
    federation.next_region_handle += 1
    federation.member_regions.setdefault(rti._current_federate_key(), {})[region.value] = dimension_names
    federation.member_region_bounds.setdefault(rti._current_federate_key(), {})[region.value] = {
        dimension_name: RangeBounds(0, rti._dimension_default_upper_bound(dimension_name))
        for dimension_name in dimension_names
    }
    return region


def commit_region_modifications(rti: Any, regions: Any) -> None:
    for region in set(regions):
        rti._region_dimension_names(rti._current_federate_key(), region)
    rti._evaluate_attribute_scope_advisories()


def delete_region(rti: Any, region: Any) -> None:
    region_value = rti._normalize_handle(region, RegionHandle, InvalidRegion)
    federate_key = rti._current_federate_key()
    if region_value not in rti._federation_record().member_regions.setdefault(federate_key, {}):
        raise InvalidRegion(str(region))
    rti._federation_record().member_regions[federate_key].pop(region_value, None)
    rti._federation_record().member_region_bounds.setdefault(federate_key, {}).pop(region_value, None)


def get_dimension_handle_set(rti: Any, region: Any) -> set[DimensionHandle]:
    dimension_names = rti._region_dimension_names(rti._current_federate_key(), region)
    handles = rti._dimension_handles()
    return {DimensionHandle(handles[name]) for name in dimension_names}


def get_range_bounds(rti: Any, region: Any, dimension: Any) -> RangeBounds:
    federate_key = rti._current_federate_key()
    dimension_name = rti.getDimensionName(dimension)
    if dimension_name not in rti._region_dimension_names(federate_key, region):
        raise RegionDoesNotContainSpecifiedDimension(str(dimension))
    region_value = rti._normalize_handle(region, RegionHandle, InvalidRegion)
    return rti._federation_record().member_region_bounds[federate_key][region_value][dimension_name]


def set_range_bounds(rti: Any, region: Any, dimension: Any, range_bounds: Any) -> None:
    federate_key = rti._current_federate_key()
    dimension_name = rti.getDimensionName(dimension)
    if dimension_name not in rti._region_dimension_names(federate_key, region):
        raise RegionDoesNotContainSpecifiedDimension(str(dimension))
    bounds = rti._coerce_range_bounds(range_bounds)
    region_value = rti._normalize_handle(region, RegionHandle, InvalidRegion)
    rti._federation_record().member_region_bounds.setdefault(federate_key, {}).setdefault(region_value, {})[
        dimension_name
    ] = bounds


def region_values_from_handles(rti: Any, regions: Any) -> set[int]:
    try:
        region_handles = tuple(regions)
    except TypeError as exc:
        raise InvalidRegion("Region handle set must be iterable") from exc
    region_values = {rti._normalize_handle(region, RegionHandle, InvalidRegion) for region in region_handles}
    for region_value in region_values:
        rti._region_dimension_names(rti._current_federate_key(), RegionHandle(region_value))
    return region_values


def coerce_range_bounds(value: Any, *, invalid_range_bound_exc: type[Exception]) -> RangeBounds:
    if isinstance(value, RangeBounds):
        bounds = value
    elif hasattr(value, "lower") and hasattr(value, "upper"):
        bounds = RangeBounds(int(value.lower), int(value.upper))
    elif hasattr(value, "lower_bound") and hasattr(value, "upper_bound"):
        bounds = RangeBounds(int(value.lower_bound), int(value.upper_bound))
    else:
        lower, upper = value
        bounds = RangeBounds(int(lower), int(upper))
    if int(bounds.lower) > int(bounds.upper):
        raise invalid_range_bound_exc(repr(value))
    return bounds


def attribute_region_pairs(rti: Any, object_class_name: str, attributes_and_regions: Any) -> tuple[tuple[set[str], set[int]], ...]:
    pairs: list[tuple[set[str], set[int]]] = []
    for pair in attributes_and_regions or ():
        if hasattr(pair, "attributes") and hasattr(pair, "regions"):
            attributes = pair.attributes
            regions = pair.regions
        elif hasattr(pair, "ahset") and hasattr(pair, "rhset"):
            attributes = pair.ahset
            regions = pair.rhset
        elif isinstance(pair, dict):
            attributes = pair.get("attributes") or pair.get("ahset") or pair.get("attribute_handles") or ()
            regions = pair.get("regions") or pair.get("rhset") or pair.get("region_handles") or ()
        elif isinstance(pair, (tuple, list)) and len(pair) >= 2:
            attributes, regions = pair[0], pair[1]
        else:
            raise InvalidRegionContext(f"Bad attribute/region pair: {pair!r}")
        attribute_names = set(rti._attribute_names_from_handles(object_class_name, attributes))
        region_values = {rti._normalize_handle(region, RegionHandle, InvalidRegion) for region in set(regions)}
        for region_value in region_values:
            rti._region_dimension_names(rti._current_federate_key(), RegionHandle(region_value))
        pairs.append((attribute_names, region_values))
    return tuple(pairs)


def object_instance_region_values(record: Any) -> set[int]:
    source_regions: set[int] = set()
    for region_values in record.update_regions.values():
        source_regions.update(region_values)
    return source_regions


def subscribe_object_class_attributes_with_regions(
    rti: Any,
    object_class: Any,
    attributes_and_regions: Any,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    region_map = rti._federation_record().subscribed_object_regions.setdefault(
        rti._current_federate_key(),
        {},
    ).setdefault(object_class_name, {})
    all_attribute_names: set[str] = set()
    for attribute_names, region_values in rti._attribute_region_pairs(object_class_name, attributes_and_regions):
        all_attribute_names.update(attribute_names)
        for attribute_name in attribute_names:
            region_map.setdefault(attribute_name, set()).update(region_values)
    if all_attribute_names:
        rti._federation_record().subscribed_object_attributes.setdefault(rti._current_federate_key(), {}).setdefault(
            object_class_name,
            set(),
        ).update(all_attribute_names)
        rti._discover_existing_objects_for_current_subscription(object_class_name)
        rti._evaluate_attribute_scope_advisories()


def unsubscribe_object_class_attributes_with_regions(
    rti: Any,
    object_class: Any,
    attributes_and_regions: Any,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    federation = rti._federation_record()
    federate_key = rti._current_federate_key()
    subscription_regions = federation.subscribed_object_regions.setdefault(federate_key, {}).setdefault(
        object_class_name,
        {},
    )
    subscribed_attrs = federation.subscribed_object_attributes.setdefault(federate_key, {}).setdefault(
        object_class_name,
        set(),
    )
    for attribute_names, region_values in rti._attribute_region_pairs(object_class_name, attributes_and_regions):
        for attribute_name in attribute_names:
            if attribute_name in subscription_regions:
                subscription_regions[attribute_name].difference_update(region_values)
                if not subscription_regions[attribute_name]:
                    subscription_regions.pop(attribute_name, None)
            subscribed_attrs.discard(attribute_name)
    if not subscription_regions:
        federation.subscribed_object_regions[rti._current_federate_key()].pop(object_class_name, None)
    if not subscribed_attrs:
        federation.subscribed_object_attributes[rti._current_federate_key()].pop(object_class_name, None)
    rti._evaluate_attribute_scope_advisories()


def register_object_instance_with_regions(
    rti: Any,
    object_class: Any,
    attributes_and_regions: Any,
    object_instance_name: str | None = None,
) -> Any:
    handle = rti.registerObjectInstance(object_class, object_instance_name)
    record = rti._object_instance_record(handle)
    for attribute_names, region_values in rti._attribute_region_pairs(record.object_class_name, attributes_and_regions):
        for attribute_name in attribute_names:
            record.update_regions.setdefault(attribute_name, set()).update(region_values)
    rti._evaluate_attribute_scope_advisories()
    return handle


def associate_regions_for_updates(rti: Any, object_instance: Any, attributes_and_regions: Any) -> None:
    record = rti._object_instance_record(object_instance)
    for attribute_names, region_values in rti._attribute_region_pairs(record.object_class_name, attributes_and_regions):
        for attribute_name in attribute_names:
            record.update_regions.setdefault(attribute_name, set()).update(region_values)


def unassociate_regions_for_updates(rti: Any, object_instance: Any, attributes_and_regions: Any) -> None:
    record = rti._object_instance_record(object_instance)
    for attribute_names, region_values in rti._attribute_region_pairs(record.object_class_name, attributes_and_regions):
        for attribute_name in attribute_names:
            if attribute_name in record.update_regions:
                record.update_regions[attribute_name].difference_update(region_values)
                if not record.update_regions[attribute_name]:
                    record.update_regions.pop(attribute_name, None)
    rti._evaluate_attribute_scope_advisories()


def change_default_attribute_transportation_type(
    rti: Any,
    object_class: Any,
    attributes: Any,
    transportation_type: Any,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    transportation_name = rti.getTransportationTypeName(transportation_type)
    for attribute_name in rti._attribute_names_from_handles(object_class_name, attributes):
        rti._default_attribute_transportation[(object_class_name, attribute_name)] = transportation_name


def change_default_attribute_order_type(
    rti: Any,
    object_class: Any,
    attributes: Any,
    order_type: Any,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    coerced_order = rti._coerce_order_type(order_type)
    for attribute_name in rti._attribute_names_from_handles(object_class_name, attributes):
        rti._default_attribute_order[(object_class_name, attribute_name)] = coerced_order


def change_attribute_order_type(
    rti: Any,
    object_instance: Any,
    attributes: Any,
    order_type: Any,
) -> None:
    record = rti._object_instance_record_known(object_instance)
    coerced_order = rti._coerce_order_type(order_type)
    for attribute_name in rti._attribute_names_from_handles(record.object_class_name, attributes):
        if record.attribute_owners.get(attribute_name) != rti._federate_handle:
            raise AttributeNotOwned(attribute_name)
        record.attribute_order[attribute_name] = coerced_order


def request_attribute_transportation_type_change(
    rti: Any,
    object_instance: Any,
    attributes: Any,
    transportation_type: Any,
) -> None:
    record = rti._object_instance_record_known(object_instance)
    transportation_name = rti.getTransportationTypeName(transportation_type)
    transportation = rti._transportation_handle_by_name(transportation_name)
    attribute_names = rti._attribute_names_from_handles(record.object_class_name, attributes)
    attribute_handles: set[AttributeHandle] = set()
    for attribute_name in attribute_names:
        if record.attribute_owners.get(attribute_name) != rti._federate_handle:
            raise AttributeNotOwned(attribute_name)
        record.attribute_transportation[attribute_name] = transportation_name
        attribute_handles.add(AttributeHandle(rti._attribute_handles(record.object_class_name)[attribute_name]))
    rti._deliver_callback_now("confirmAttributeTransportationTypeChange", object_instance, attribute_handles, transportation)


def query_attribute_transportation_type(rti: Any, object_instance: Any, attribute: Any) -> None:
    record = rti._object_instance_record_known(object_instance)
    attribute_name = rti._attribute_names_from_handles(record.object_class_name, {attribute})[0]
    transportation_name = record.attribute_transportation.get(
        attribute_name,
        rti._default_attribute_transportation.get((record.object_class_name, attribute_name), "HLAreliable"),
    )
    rti._deliver_callback_now(
        "reportAttributeTransportationType",
        object_instance,
        attribute,
        rti._transportation_handle_by_name(transportation_name),
    )


__all__ = [
    "associate_regions_for_updates",
    "attribute_region_pairs",
    "change_attribute_order_type",
    "change_default_attribute_order_type",
    "change_default_attribute_transportation_type",
    "coerce_range_bounds",
    "commit_region_modifications",
    "create_region",
    "delete_region",
    "get_dimension_handle_set",
    "get_range_bounds",
    "object_instance_region_values",
    "query_attribute_transportation_type",
    "register_object_instance_with_regions",
    "region_values_from_handles",
    "request_attribute_transportation_type_change",
    "set_range_bounds",
    "subscribe_object_class_attributes_with_regions",
    "unassociate_regions_for_updates",
    "unsubscribe_object_class_attributes_with_regions",
]
