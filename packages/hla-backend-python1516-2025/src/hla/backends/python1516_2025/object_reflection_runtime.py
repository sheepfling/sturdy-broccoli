"""Object reflection delivery helpers owned by the dedicated Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.handles import (
    AttributeHandle,
    FederateHandle,
    ObjectClassHandle,
    RegionHandle,
    TransportationTypeHandle,
)


def group_source_values_by_transport(
    rti: Any,
    record: Any,
    values_by_handle: Mapping[AttributeHandle, bytes],
) -> dict[TransportationTypeHandle, dict[AttributeHandle, bytes]]:
    grouped: dict[TransportationTypeHandle, dict[AttributeHandle, bytes]] = {}
    for handle, value in values_by_handle.items():
        transportation = rti._attribute_transportation_for(record, {handle: value})
        grouped.setdefault(transportation, {})[handle] = value
    return grouped


def fanout_attribute_update(
    rti: Any,
    object_instance: Any,
    record: Any,
    values_by_handle: Mapping[AttributeHandle, bytes],
    user_supplied_tag: bytes,
    callback_time: Any | None,
) -> list[Any]:
    federation = rti._federation_record()
    object_class_name = record.object_class_name
    retraction_handles: list[Any] = []
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        discovery_class_name = rti._known_object_classes_for_federate(
            federate_key,
            object_instance,
            object_class_name,
        )
        if discovery_class_name is None:
            continue
        subscribed_names = rti._reflectable_attribute_names_for_subscriber(
            rti._current_federate_key(),
            federate_key,
            record,
            discovery_class_name,
            set(subscriptions.get(discovery_class_name, set())),
        )
        reflected_all = {
            AttributeHandle(rti._attribute_handles(discovery_class_name)[rti._attribute_name_by_handle(object_class_name, handle)]): value
            for handle, value in values_by_handle.items()
            if rti._attribute_name_by_handle(object_class_name, handle) in subscribed_names
        }
        if callback_time is not None:
            reflected_all = rti._apply_update_rate_reduction_for_subscriber(
                federate_key,
                object_instance,
                discovery_class_name,
                object_class_name,
                reflected_all,
                callback_time,
            )
        if not reflected_all:
            continue
        reflected_by_transport: dict[TransportationTypeHandle, dict[AttributeHandle, bytes]] = {}
        for handle, value in reflected_all.items():
            source_attribute = AttributeHandle(
                rti._attribute_handles(object_class_name)[rti._attribute_name_by_handle(discovery_class_name, handle)]
            )
            transportation = rti._attribute_transportation_for(record, {source_attribute: value})
            reflected_by_transport.setdefault(transportation, {})[handle] = value
        target_rti = federation.member_rtis.get(federate_key)
        if target_rti is not None and object_instance.value in target_rti._locally_deleted_objects:
            rti._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "discoverObjectInstance",
                object_instance,
                ObjectClassHandle(rti._object_class_handles()[discovery_class_name]),
                record.object_instance_name or "",
                rti._current_federate_handle(),
            )
        rti._increment_mom_count(federation.mom_object_instances_reflected, (federate_key, object_class_name))
        for transportation, reflected in reflected_by_transport.items():
            rti._increment_mom_count(
                federation.mom_reflections_received,
                (federate_key, object_class_name, rti.getTransportationTypeName(transportation)),
            )
            sent_regions = {
                RegionHandle(region_value)
                for handle in reflected
                for region_value in record.update_regions.get(rti._attribute_name_by_handle(discovery_class_name, handle), set())
            }
            reflected_order = rti._attribute_order_for(record, reflected)
            explicit_receive_override = all(
                record.attribute_order.get(rti._attribute_name_by_handle(record.object_class_name, handle)) is OrderType.RECEIVE
                for handle in reflected
            )
            if callback_time is not None:
                if reflected_order is OrderType.RECEIVE and explicit_receive_override:
                    rti._deliver_to_federate_handle(
                        FederateHandle(federate_key),
                        "reflectAttributeValues",
                        object_instance,
                        reflected,
                        bytes(user_supplied_tag),
                        transportation,
                        rti._current_federate_handle(),
                        sent_regions,
                        None,
                        OrderType.RECEIVE,
                        OrderType.RECEIVE,
                        None,
                    )
                    continue
                retraction_handles.append(
                    rti._queue_tso_callback(
                        FederateHandle(federate_key),
                        callback_time,
                        "reflectAttributeValues",
                        object_instance,
                        reflected,
                        bytes(user_supplied_tag),
                        transportation,
                        rti._current_federate_handle(),
                        sent_regions,
                        callback_time,
                        OrderType.TIMESTAMP,
                        OrderType.TIMESTAMP,
                    )
                )
                continue
            rti._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "reflectAttributeValues",
                object_instance,
                reflected,
                bytes(user_supplied_tag),
                transportation,
                rti._current_federate_handle(),
                sent_regions,
                None,
                reflected_order,
                reflected_order,
                None,
            )
    return retraction_handles


__all__ = ["fanout_attribute_update", "group_source_values_by_transport"]
