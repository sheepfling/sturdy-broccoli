"""Shared declaration-management semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.exceptions import (
    AttributeNotDefined,
    InvalidAttributeHandle,
    ObjectInstanceNameNotReserved,
)
from hla.rti1516_2025.handles import FederateHandle, ObjectClassHandle


def publish_object_class_attributes(rti: Any, object_class: Any, attributes: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    try:
        attribute_names = set(rti._attribute_names_from_handles(object_class_name, attributes))
    except InvalidAttributeHandle as exc:
        raise AttributeNotDefined(str(exc)) from exc
    federation = rti._federation_record()
    published = federation.published_object_attributes.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    )
    had_match = rti._has_object_registration_interest(federation, rti._current_federate_key(), object_class_name)
    published.update(attribute_names)
    has_match = rti._has_object_registration_interest(federation, rti._current_federate_key(), object_class_name)
    if has_match and not had_match:
        rti._deliver_callback(
            "startRegistrationForObjectClass",
            ObjectClassHandle(rti._object_class_handles()[object_class_name]),
        )


def unpublish_object_class(rti: Any, object_class: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    federation = rti._federation_record()
    had_match = rti._has_object_registration_interest(federation, rti._current_federate_key(), object_class_name)
    federation.published_object_attributes.setdefault(rti._current_federate_key(), {}).pop(object_class_name, None)
    if had_match:
        rti._deliver_callback(
            "stopRegistrationForObjectClass",
            ObjectClassHandle(rti._object_class_handles()[object_class_name]),
        )


def unpublish_object_class_attributes(rti: Any, object_class: Any, attributes: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    try:
        attribute_names = set(rti._attribute_names_from_handles(object_class_name, attributes))
    except InvalidAttributeHandle as exc:
        raise AttributeNotDefined(str(exc)) from exc
    federation = rti._federation_record()
    published = federation.published_object_attributes.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    )
    had_match = rti._has_object_registration_interest(federation, rti._current_federate_key(), object_class_name)
    published.difference_update(attribute_names)
    if not published:
        federation.published_object_attributes[rti._current_federate_key()].pop(object_class_name, None)
    has_match = rti._has_object_registration_interest(federation, rti._current_federate_key(), object_class_name)
    if had_match and not has_match:
        rti._deliver_callback(
            "stopRegistrationForObjectClass",
            ObjectClassHandle(rti._object_class_handles()[object_class_name]),
        )


def subscribe_object_class_attributes(rti: Any, object_class: Any, attributes: Any, *unused: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    try:
        attribute_names = set(rti._attribute_names_from_handles(object_class_name, attributes))
    except InvalidAttributeHandle as exc:
        raise AttributeNotDefined(str(exc)) from exc
    explicit_update_rate, explicit_designator = rti._resolve_update_rate_designator(*unused)
    federation = rti._federation_record()
    affected_publishers = rti._matching_object_publishers(federation, object_class_name, attribute_names)
    before_matches = {
        publisher_key: rti._has_object_registration_interest(federation, publisher_key, object_class_name)
        for publisher_key in affected_publishers
    }
    federation.subscribed_object_attributes.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    ).update(attribute_names)
    rate_map = rti._subscribed_object_update_rates.setdefault(object_class_name, {})
    designator_map = rti._subscribed_object_update_rate_designators.setdefault(object_class_name, {})
    for attribute_name in attribute_names:
        resolved_rate = explicit_update_rate
        resolved_designator = explicit_designator
        if resolved_rate is None:
            resolved_rate = rti._default_update_rate_for_attribute(object_class_name, attribute_name)
            resolved_designator = rti._default_update_rate_designator_for_attribute(object_class_name, attribute_name)
        if resolved_rate is None:
            rate_map.pop(attribute_name, None)
            designator_map.pop(attribute_name, None)
            continue
        rate_map[attribute_name] = resolved_rate
        if resolved_designator is None:
            designator_map.pop(attribute_name, None)
        else:
            designator_map[attribute_name] = resolved_designator
    if not rate_map:
        rti._subscribed_object_update_rates.pop(object_class_name, None)
    if not designator_map:
        rti._subscribed_object_update_rate_designators.pop(object_class_name, None)
    rti._discover_existing_objects_for_current_subscription(object_class_name)
    for publisher_key in affected_publishers:
        if not before_matches[publisher_key] and rti._has_object_registration_interest(
            federation,
            publisher_key,
            object_class_name,
        ):
            rti._deliver_to_federate_handle(
                FederateHandle(publisher_key),
                "startRegistrationForObjectClass",
                ObjectClassHandle(rti._object_class_handles()[object_class_name]),
            )


def unsubscribe_object_class(rti: Any, object_class: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    federation = rti._federation_record()
    affected_publishers = rti._matching_object_publishers(
        federation,
        object_class_name,
        federation.subscribed_object_attributes.setdefault(rti._current_federate_key(), {}).get(object_class_name, set()),
    )
    before_matches = {
        publisher_key: rti._has_object_registration_interest(federation, publisher_key, object_class_name)
        for publisher_key in affected_publishers
    }
    federation.subscribed_object_attributes.setdefault(rti._current_federate_key(), {}).pop(object_class_name, None)
    rti._subscribed_object_update_rates.pop(object_class_name, None)
    rti._subscribed_object_update_rate_designators.pop(object_class_name, None)
    for publisher_key in affected_publishers:
        if before_matches[publisher_key] and not rti._has_object_registration_interest(
            federation,
            publisher_key,
            object_class_name,
        ):
            rti._deliver_to_federate_handle(
                FederateHandle(publisher_key),
                "stopRegistrationForObjectClass",
                ObjectClassHandle(rti._object_class_handles()[object_class_name]),
            )


def unsubscribe_object_class_attributes(rti: Any, object_class: Any, attributes: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    try:
        attribute_names = set(rti._attribute_names_from_handles(object_class_name, attributes))
    except InvalidAttributeHandle as exc:
        raise AttributeNotDefined(str(exc)) from exc
    federation = rti._federation_record()
    affected_publishers = rti._matching_object_publishers(federation, object_class_name, attribute_names)
    before_matches = {
        publisher_key: rti._has_object_registration_interest(federation, publisher_key, object_class_name)
        for publisher_key in affected_publishers
    }
    subscribed = federation.subscribed_object_attributes.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    )
    subscribed.difference_update(attribute_names)
    if not subscribed:
        federation.subscribed_object_attributes[rti._current_federate_key()].pop(object_class_name, None)
    rate_map = rti._subscribed_object_update_rates.get(object_class_name)
    if rate_map is not None:
        for attribute_name in attribute_names:
            rate_map.pop(attribute_name, None)
        if not rate_map:
            rti._subscribed_object_update_rates.pop(object_class_name, None)
    designator_map = rti._subscribed_object_update_rate_designators.get(object_class_name)
    if designator_map is not None:
        for attribute_name in attribute_names:
            designator_map.pop(attribute_name, None)
        if not designator_map:
            rti._subscribed_object_update_rate_designators.pop(object_class_name, None)
    for publisher_key in affected_publishers:
        if before_matches[publisher_key] and not rti._has_object_registration_interest(
            federation,
            publisher_key,
            object_class_name,
        ):
            rti._deliver_to_federate_handle(
                FederateHandle(publisher_key),
                "stopRegistrationForObjectClass",
                ObjectClassHandle(rti._object_class_handles()[object_class_name]),
            )


def reserve_object_instance_name(rti: Any, object_instance_name: str) -> None:
    name = rti._normalize_reserved_object_instance_name(
        object_instance_name,
        method_name="reserveObjectInstanceName",
    )
    federation = rti._federation_record()
    if name in federation.object_instance_names or name in federation.reserved_object_instance_names:
        rti._deliver_callback("objectInstanceNameReservationFailed", name)
        return
    federation.reserved_object_instance_names[name] = rti._current_federate_key()
    rti._deliver_callback("objectInstanceNameReservationSucceeded", name)


def release_object_instance_name(rti: Any, object_instance_name: str) -> None:
    name = rti._normalize_reserved_object_instance_name(
        object_instance_name,
        method_name="releaseObjectInstanceName",
    )
    federation = rti._federation_record()
    if federation.reserved_object_instance_names.get(name) != rti._current_federate_key():
        raise ObjectInstanceNameNotReserved(name)
    federation.reserved_object_instance_names.pop(name, None)


def reserve_multiple_object_instance_names(rti: Any, object_instance_names: Any) -> None:
    names = rti._normalize_reserved_object_instance_name_set(
        object_instance_names,
        method_name="reserveMultipleObjectInstanceNames",
    )
    federation = rti._federation_record()
    if any(name in federation.object_instance_names or name in federation.reserved_object_instance_names for name in names):
        rti._deliver_callback("multipleObjectInstanceNameReservationFailed", names)
        return
    federate_key = rti._current_federate_key()
    for name in names:
        federation.reserved_object_instance_names[name] = federate_key
    rti._deliver_callback("multipleObjectInstanceNameReservationSucceeded", names)


def release_multiple_object_instance_names(rti: Any, object_instance_names: Any) -> None:
    names = rti._normalize_reserved_object_instance_name_set(
        object_instance_names,
        method_name="releaseMultipleObjectInstanceNames",
    )
    federation = rti._federation_record()
    federate_key = rti._current_federate_key()
    for name in sorted(names):
        if federation.reserved_object_instance_names.get(name) != federate_key:
            raise ObjectInstanceNameNotReserved(name)
    for name in names:
        federation.reserved_object_instance_names.pop(name, None)
