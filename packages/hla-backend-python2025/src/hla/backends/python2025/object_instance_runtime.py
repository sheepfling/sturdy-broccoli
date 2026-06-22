"""Object-instance lifecycle and update-routing helpers owned by the dedicated Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.datatypes import MessageRetractionReturn
from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.exceptions import (
    AttributeNotOwned,
    DeletePrivilegeNotHeld,
    InvalidObjectInstanceHandle,
    ObjectClassNotPublished,
    ObjectInstanceNameInUse,
    ObjectInstanceNotKnown,
    RTIinternalError,
)
from hla.rti1516_2025.handles import (
    AttributeHandle,
    FederateHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
)

from .object_reflection_runtime import fanout_attribute_update, group_source_values_by_transport


def register_object_instance(
    rti: Any,
    object_class: Any,
    object_instance_name: str | None = None,
) -> ObjectInstanceHandle:
    federation = rti._federation_record()
    object_class_name = rti._object_class_name(object_class)
    if object_instance_name is not None:
        if not isinstance(object_instance_name, str) or not object_instance_name:
            raise RTIinternalError("objectInstanceName must be a non-empty string when provided")
        if object_instance_name in federation.object_instance_names:
            raise ObjectInstanceNameInUse(object_instance_name)
        reserved_by = federation.reserved_object_instance_names.get(object_instance_name)
        if reserved_by is not None and reserved_by != rti._current_federate_key():
            raise ObjectInstanceNameInUse(object_instance_name)
    handle = ObjectInstanceHandle(federation.next_object_instance_handle)
    federation.next_object_instance_handle += 1
    attribute_owners = {
        attribute_name: rti._federate_handle for attribute_name in rti._attribute_handles(object_class_name)
    }
    object_instance_record_type = rti._object_instance_record_type()
    federation.object_instances[handle.value] = object_instance_record_type(
        object_class_name=object_class_name,
        object_instance_name=object_instance_name,
        producing_federate=rti._federate_handle,
        attribute_owners=attribute_owners,
    )
    if object_instance_name is not None:
        federation.object_instance_names[object_instance_name] = handle.value
        federation.reserved_object_instance_names.pop(object_instance_name, None)
    rti._known_object_classes[handle.value] = object_class_name
    if object_instance_name is not None:
        rti._known_object_names[object_instance_name] = handle.value
    source_key = rti._current_federate_key()
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        discovery_class_name = rti._subscribed_discovery_class_name(federate_key, object_class_name)
        if discovery_class_name is None:
            continue
        subscribed_names = set(subscriptions.get(discovery_class_name, set()))
        reflected_names = rti._reflectable_attribute_names_for_subscriber(
            source_key,
            federate_key,
            federation.object_instances[handle.value],
            discovery_class_name,
            subscribed_names,
        )
        if reflected_names:
            rti._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "discoverObjectInstance",
                handle,
                ObjectClassHandle(rti._object_class_handles()[discovery_class_name]),
                object_instance_name or "",
                rti._current_federate_handle(),
            )
    return handle


def update_attribute_values(
    rti: Any,
    object_instance: Any,
    attribute_values: Mapping[Any, bytes],
    user_supplied_tag: bytes,
    time: Any | None = None,
) -> Any | None:
    record = rti._object_instance_record(object_instance)
    object_class_name = record.object_class_name
    attributes_by_name = rti._attribute_handles(object_class_name)
    values_by_handle: dict[AttributeHandle, bytes] = {}
    for attribute, value in dict(attribute_values).items():
        attribute_name = rti._attribute_names_from_handles(object_class_name, {attribute})[0]
        if record.attribute_owners.get(attribute_name) != rti._federate_handle:
            raise AttributeNotOwned(attribute_name)
        if attribute_name not in rti._published_attributes_for_current_federate(object_class_name):
            raise ObjectClassNotPublished(object_class_name)
        values_by_handle[AttributeHandle(attributes_by_name[attribute_name])] = bytes(value)
        record.attribute_values[attribute_name] = bytes(value)

    callback_time = rti._coerce_time(time) if time is not None else None
    if callback_time is not None:
        rti._validate_tso_send_time(callback_time)
    federation = rti._federation_record()
    rti._increment_mom_count(federation.mom_object_instances_updated, (rti._current_federate_key(), object_class_name))
    source_values_by_transport = group_source_values_by_transport(rti, record, values_by_handle)
    for transportation in source_values_by_transport:
        rti._increment_mom_count(
            federation.mom_updates_sent,
            (rti._current_federate_key(), object_class_name, rti.getTransportationTypeName(transportation)),
        )
    retraction_handles = fanout_attribute_update(
        rti,
        object_instance,
        record,
        values_by_handle,
        user_supplied_tag,
        callback_time,
    )
    if callback_time is not None:
        handle = rti._canonicalize_retraction_handles(federation, retraction_handles)
        return MessageRetractionReturn(bool(retraction_handles), handle)
    return None


def delete_object_instance(
    rti: Any,
    object_instance: Any,
    user_supplied_tag: bytes,
    time: Any | None = None,
) -> Any | None:
    object_instance_value = rti._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        rti._invalid_object_instance_handle_type(),
    )
    federation = rti._federation_record()
    try:
        record = federation.object_instances[object_instance_value]
    except KeyError as exc:
        raise ObjectInstanceNotKnown(str(object_instance)) from exc
    delete_privilege_holder = record.producing_federate
    if delete_privilege_holder is None or rti._current_federate_handle() != delete_privilege_holder:
        raise DeletePrivilegeNotHeld(str(object_instance))

    callback_time = rti._coerce_time(time) if time is not None else None
    if callback_time is not None:
        rti._validate_tso_send_time(callback_time)
    object_class_name = record.object_class_name
    retraction_handles: list[MessageRetractionHandle] = []
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        if federate_key == rti._current_federate_key() or object_class_name not in subscriptions:
            continue
        target_rti = federation.member_rtis.get(federate_key)
        if target_rti is not None and object_instance_value in target_rti._locally_deleted_objects:
            continue
        if callback_time is not None:
            retraction_handles.append(
                rti._queue_tso_callback(
                    FederateHandle(federate_key),
                    callback_time,
                    "removeObjectInstance",
                    object_instance,
                    bytes(user_supplied_tag),
                    rti._current_federate_handle(),
                    callback_time,
                    OrderType.TIMESTAMP,
                    OrderType.TIMESTAMP,
                )
            )
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "removeObjectInstance",
            object_instance,
            bytes(user_supplied_tag),
            rti._current_federate_handle(),
            callback_time,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )

    if record.object_instance_name is not None:
        federation.object_instance_names.pop(record.object_instance_name, None)
    federation.object_instances.pop(object_instance_value, None)
    if callback_time is not None:
        handle = rti._canonicalize_retraction_handles(federation, retraction_handles)
        return MessageRetractionReturn(bool(retraction_handles), handle)
    return None


def local_delete_object_instance(rti: Any, object_instance: Any) -> None:
    record = rti._object_instance_record_known(object_instance)
    object_instance_value = rti._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        rti._invalid_object_instance_handle_type(),
    )
    rti._known_object_classes.pop(object_instance_value, None)
    if record.object_instance_name is not None:
        rti._known_object_names.pop(record.object_instance_name, None)
    rti._locally_deleted_objects.add(object_instance_value)


def request_attribute_value_update(
    rti: Any,
    object_class_or_instance: Any,
    attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    try:
        request_instance_attribute_value_update(rti, object_class_or_instance, attributes, user_supplied_tag)
        return
    except InvalidObjectInstanceHandle:
        pass
    object_class_name = rti._object_class_name(object_class_or_instance)
    attribute_names = rti._attribute_names_from_handles(object_class_name, attributes)
    attribute_handles = {
        AttributeHandle(rti._attribute_handles(object_class_name)[name]) for name in attribute_names
    }
    for object_value, record in rti._federation_record().object_instances.items():
        if record.object_class_name != object_class_name:
            continue
        deliver_value_update_requests(
            rti,
            ObjectInstanceHandle(object_value),
            record,
            attribute_handles,
            user_supplied_tag,
        )


def request_instance_attribute_value_update(
    rti: Any,
    object_instance: ObjectInstanceHandle,
    attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    if not isinstance(object_instance, ObjectInstanceHandle):
        object_instance_value = getattr(object_instance, "value", None)
        if type(object_instance).__name__ == "ObjectInstanceHandle" and isinstance(object_instance_value, int):
            object_instance = ObjectInstanceHandle(object_instance_value)
    record = rti._object_instance_record_known(object_instance)
    attribute_names = rti._attribute_names_from_handles(record.object_class_name, attributes)
    attribute_handles = {
        AttributeHandle(rti._attribute_handles(record.object_class_name)[name]) for name in attribute_names
    }
    deliver_value_update_requests(rti, object_instance, record, attribute_handles, user_supplied_tag)


def deliver_value_update_requests(
    rti: Any,
    object_instance: ObjectInstanceHandle,
    record: Any,
    attribute_handles: set[AttributeHandle],
    user_supplied_tag: bytes,
) -> None:
    if rti._is_mom_object_class_name(record.object_class_name):
        reflected = {
            attribute_handle: record.attribute_values.get(
                rti._attribute_name_by_handle(record.object_class_name, attribute_handle),
                b"",
            )
            for attribute_handle in attribute_handles
        }
        rti._deliver_callback(
            "reflectAttributeValues",
            object_instance,
            reflected,
            bytes(user_supplied_tag),
            rti._transportation_handle_by_name("HLAreliable"),
            record.producing_federate or rti._mom_runtime_federate_handle(),
            set(),
            None,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )
        return
    handles_by_name = rti._attribute_handles(record.object_class_name)
    attributes_by_owner: dict[FederateHandle, set[AttributeHandle]] = {}
    for attribute in attribute_handles:
        attribute_name = rti._attribute_name_by_handle(record.object_class_name, attribute)
        owner = record.attribute_owners.get(attribute_name)
        if owner is not None:
            attributes_by_owner.setdefault(owner, set()).add(AttributeHandle(handles_by_name[attribute_name]))
    for owner, owned_attributes in sorted(attributes_by_owner.items(), key=lambda item: item[0].value):
        rti._deliver_to_federate_handle(
            owner,
            "provideAttributeValueUpdate",
            object_instance,
            owned_attributes,
            bytes(user_supplied_tag),
        )


def set_internal_object_attribute_values(
    rti: Any,
    object_instance: ObjectInstanceHandle,
    attribute_values: Mapping[str, str | bytes],
) -> None:
    record = rti._object_instance_record(object_instance)
    changed: dict[AttributeHandle, bytes] = {}
    handles_by_name = rti._attribute_handles(record.object_class_name)
    for attribute_name, raw_value in attribute_values.items():
        if attribute_name not in handles_by_name:
            continue
        value = bytes(raw_value) if isinstance(raw_value, bytes) else str(raw_value).encode("utf-8")
        if record.attribute_values.get(attribute_name) == value:
            continue
        record.attribute_values[attribute_name] = value
        changed[AttributeHandle(handles_by_name[attribute_name])] = value
    if not changed:
        return
    federation = rti._federation_record()
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        discovery_class_name = rti._known_object_classes_for_federate(
            federate_key,
            object_instance,
            record.object_class_name,
        )
        if discovery_class_name is None:
            continue
        subscribed_names = rti._reflectable_attribute_names_for_subscriber(
            record.producing_federate.value if record.producing_federate is not None else 0,
            federate_key,
            record,
            discovery_class_name,
            set(subscriptions.get(discovery_class_name, set())),
        )
        reflected = {
            AttributeHandle(
                rti._attribute_handles(discovery_class_name)[
                    rti._attribute_name_by_handle(record.object_class_name, handle)
                ]
            ): value
            for handle, value in changed.items()
            if rti._attribute_name_by_handle(record.object_class_name, handle) in subscribed_names
        }
        if reflected:
            rti._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "reflectAttributeValues",
                object_instance,
                reflected,
                b"MOM",
                rti._transportation_handle_by_name("HLAreliable"),
                record.producing_federate or rti._mom_runtime_federate_handle(),
                set(),
                None,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )


__all__ = [
    "delete_object_instance",
    "deliver_value_update_requests",
    "local_delete_object_instance",
    "register_object_instance",
    "request_attribute_value_update",
    "request_instance_attribute_value_update",
    "set_internal_object_attribute_values",
    "update_attribute_values",
]
