"""Attribute-scope advisory helpers for the current Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.handles import AttributeHandle, FederateHandle, ObjectInstanceHandle


def deliver_forced_remove_callbacks(
    rti: Any,
    object_instance: ObjectInstanceHandle,
    record: Any,
    producing_federate: FederateHandle,
    user_supplied_tag: bytes,
) -> None:
    for federate_key, subscriptions in rti._federation_record().subscribed_object_attributes.items():
        if federate_key == rti._current_federate_key() or record.object_class_name not in subscriptions:
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "removeObjectInstance",
            object_instance,
            bytes(user_supplied_tag),
            producing_federate,
            None,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )


def evaluate_attribute_scope_advisories(rti: Any) -> None:
    federation = rti._federation_record()
    in_scope_callbacks: dict[tuple[int, int], set[AttributeHandle]] = {}
    out_of_scope_callbacks: dict[tuple[int, int], set[AttributeHandle]] = {}
    active_keys = set()
    for subscriber_key, subscriptions in federation.subscribed_object_attributes.items():
        subscriber_rti = federation.member_rtis.get(subscriber_key)
        if subscriber_rti is None or not subscriber_rti._switches["attribute_scope_advisory"]:
            continue
        for object_instance_value, record in federation.object_instances.items():
            subscribed_names = set(subscriptions.get(record.object_class_name, set()))
            if not subscribed_names:
                continue
            handles_by_name = rti._attribute_handles(record.object_class_name)
            for attribute_name in subscribed_names:
                source_owner = record.attribute_owners.get(attribute_name)
                if source_owner is None:
                    continue
                active_key = (subscriber_key, object_instance_value, attribute_name)
                active_keys.add(active_key)
                source_regions = set(record.update_regions.get(attribute_name, set()))
                target_regions = (
                    federation.subscribed_object_regions
                    .get(subscriber_key, {})
                    .get(record.object_class_name, {})
                    .get(attribute_name, set())
                )
                in_scope = not target_regions or rti._region_sets_overlap(
                    source_owner.value,
                    source_regions,
                    subscriber_key,
                    set(target_regions),
                )
                previous = federation.attribute_scope_state.get(active_key)
                federation.attribute_scope_state[active_key] = in_scope
                if previous is None and in_scope:
                    in_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                        AttributeHandle(handles_by_name[attribute_name])
                    )
                elif previous is True and not in_scope:
                    out_of_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                        AttributeHandle(handles_by_name[attribute_name])
                    )
                elif previous is False and in_scope:
                    in_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                        AttributeHandle(handles_by_name[attribute_name])
                    )
    for state_key in tuple(federation.attribute_scope_state):
        subscriber_key, object_instance_value, attribute_name = state_key
        if state_key in active_keys:
            continue
        if federation.attribute_scope_state.pop(state_key, False):
            record = federation.object_instances.get(object_instance_value)
            if record is not None:
                out_of_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                    AttributeHandle(rti._attribute_handles(record.object_class_name)[attribute_name])
                )
    for (subscriber_key, object_instance_value), attributes in sorted(in_scope_callbacks.items()):
        rti._deliver_to_federate_handle(
            FederateHandle(subscriber_key),
            "attributesInScope",
            ObjectInstanceHandle(object_instance_value),
            attributes,
        )
    for (subscriber_key, object_instance_value), attributes in sorted(out_of_scope_callbacks.items()):
        rti._deliver_to_federate_handle(
            FederateHandle(subscriber_key),
            "attributesOutOfScope",
            ObjectInstanceHandle(object_instance_value),
            attributes,
        )
