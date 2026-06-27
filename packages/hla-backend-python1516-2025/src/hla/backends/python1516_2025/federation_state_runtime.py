"""Federation-state and MOM-object helpers for the dedicated Python 2025 lane."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.enums import OrderType, ResignAction
from hla.rti1516_2025.handles import AttributeHandle, FederateHandle, ObjectClassHandle, ObjectInstanceHandle


def release_join(backend: Any) -> None:
    if backend._federation_name is None:
        return
    backend._pending_time_advance = None
    backend._known_object_classes.clear()
    backend._known_object_names.clear()
    backend._locally_deleted_objects.clear()
    backend._subscribed_object_update_rates.clear()
    backend._subscribed_object_update_rate_designators.clear()
    backend._last_reflect_logical_times.clear()
    federation = backend._FEDERATION_REGISTRY.get(backend._federation_name)
    if federation is not None:
        if backend._federate_name is not None:
            federation.members.pop(backend._federate_name, None)
            federation.member_handles.pop(backend._federate_name, None)
        if backend._federate_handle is not None:
            prune_tso_state_for_departing_federate(federation, backend._federate_handle)
            reserved_names = [
                name
                for name, owner in federation.reserved_object_instance_names.items()
                if owner == backend._federate_handle.value
            ]
            for name in reserved_names:
                federation.reserved_object_instance_names.pop(name, None)
            federation.member_ambassadors.pop(backend._federate_handle.value, None)
            federation.member_rtis.pop(backend._federate_handle.value, None)
            federation.published_object_attributes.pop(backend._federate_handle.value, None)
            federation.subscribed_object_attributes.pop(backend._federate_handle.value, None)
            federation.subscribed_object_regions.pop(backend._federate_handle.value, None)
            federation.published_interactions.pop(backend._federate_handle.value, None)
            federation.subscribed_interactions.pop(backend._federate_handle.value, None)
            federation.subscribed_interaction_regions.pop(backend._federate_handle.value, None)
            federation.directed_interaction_region_gates.pop(backend._federate_handle.value, None)
            federation.published_directed_interactions.pop(backend._federate_handle.value, None)
            federation.subscribed_directed_interactions.pop(backend._federate_handle.value, None)
            federation.member_regions.pop(backend._federate_handle.value, None)
            federation.member_region_bounds.pop(backend._federate_handle.value, None)
        backend._refresh_mom_federation_object()


def prune_tso_state_for_departing_federate(federation: Any, federate_handle: FederateHandle) -> None:
    queued_for_target = [
        handle_value
        for handle_value, queued in federation.queued_tso_callbacks.items()
        if queued.target_federate == federate_handle
    ]
    for handle_value in queued_for_target:
        federation.queued_tso_callbacks.pop(handle_value, None)
        backend_drop_retraction_group_member(federation, handle_value)

    stale_delivered = [
        handle_value
        for handle_value, target in federation.delivered_retraction_targets.items()
        if target == federate_handle
    ]
    for handle_value in stale_delivered:
        federation.delivered_retraction_targets.pop(handle_value, None)
        federation.delivered_retraction_handles.discard(handle_value)
        backend_drop_retraction_group_member(federation, handle_value)


def apply_resign_action(backend: Any, resign_action: ResignAction) -> None:
    if resign_action is ResignAction.NO_ACTION:
        return
    if resign_action in {
        ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        cancel_resigning_federate_pending_acquisitions(backend)
    if resign_action in {
        ResignAction.DELETE_OBJECTS,
        ResignAction.DELETE_OBJECTS_THEN_DIVEST,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        delete_objects_owned_by_resigning_federate(backend)
    if resign_action in {
        ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
        ResignAction.DELETE_OBJECTS_THEN_DIVEST,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        divest_resigning_federate_attributes(backend)


def cancel_resigning_federate_pending_acquisitions(backend: Any) -> None:
    federate_handle = backend._current_federate_handle()
    for record in backend._federation_record().object_instances.values():
        for attribute_name in tuple(record.attribute_candidates):
            backend._remove_attribute_candidate(record, attribute_name, federate_handle)


def resigning_federate_has_pending_acquisitions(backend: Any) -> bool:
    federate_handle = backend._current_federate_handle()
    for record in backend._federation_record().object_instances.values():
        for attribute_name in tuple(record.attribute_candidates):
            if backend._has_attribute_candidate(record, attribute_name, federate_handle):
                return True
    return False


def resigning_federate_owns_attributes(backend: Any) -> bool:
    federate_handle = backend._current_federate_handle()
    for record in backend._federation_record().object_instances.values():
        if is_mom_object_class_name(record.object_class_name):
            continue
        if federate_handle in set(record.attribute_owners.values()):
            return True
    return False


def delete_objects_owned_by_resigning_federate(backend: Any) -> None:
    delete_objects_owned_by_specific_federate(backend, backend._current_federate_handle(), user_supplied_tag=b"")


def delete_objects_owned_by_specific_federate(
    backend: Any,
    federate_handle: FederateHandle,
    *,
    user_supplied_tag: bytes,
) -> None:
    federation = backend._federation_record()
    for object_instance_value, record in tuple(federation.object_instances.items()):
        if is_mom_object_class_name(record.object_class_name):
            continue
        if federate_handle not in set(record.attribute_owners.values()):
            continue
        object_instance = ObjectInstanceHandle(object_instance_value)
        backend._deliver_forced_remove_callbacks(object_instance, record, federate_handle, user_supplied_tag)
        if record.object_instance_name is not None:
            federation.object_instance_names.pop(record.object_instance_name, None)
        federation.object_instances.pop(object_instance_value, None)


def divest_resigning_federate_attributes(backend: Any) -> None:
    divest_attributes_owned_by_specific_federate(backend, backend._current_federate_handle())


def divest_attributes_owned_by_specific_federate(backend: Any, federate_handle: FederateHandle) -> None:
    for object_instance_value, record in tuple(backend._federation_record().object_instances.items()):
        if is_mom_object_class_name(record.object_class_name):
            continue
        attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
        for attribute_name, owner in tuple(record.attribute_owners.items()):
            if owner != federate_handle:
                continue
            new_owner, acquisition_tag = backend._pop_attribute_candidate(record, attribute_name) or (None, b"")
            record.attribute_owners[attribute_name] = new_owner
            record.attribute_divesting.discard(attribute_name)
            if new_owner is not None:
                attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
                backend._deliver_to_federate_handle(
                    new_owner,
                    "attributeOwnershipAcquisitionNotification",
                    ObjectInstanceHandle(object_instance_value),
                    {attribute_handle},
                    acquisition_tag,
                )


def is_mom_object_class_name(object_class_name: str) -> bool:
    return ".HLAmanager." in object_class_name


def mom_runtime_federate_handle() -> FederateHandle:
    return FederateHandle(0)


def ensure_mom_objects(backend: Any) -> None:
    federation = backend._federation_record()
    ensure_mom_federation_object(backend, federation)
    for federate_name, federate_handle in sorted(
        federation.member_handles.items(),
        key=lambda item: item[1].value,
    ):
        ensure_mom_federate_object(
            backend,
            federation,
            federate_name,
            federation.members.get(federate_name, ""),
            federate_handle,
        )
    refresh_mom_federation_object(backend)
    for federate_name, federate_handle in sorted(
        federation.member_handles.items(),
        key=lambda item: item[1].value,
    ):
        refresh_mom_federate_object(
            backend,
            federate_name,
            federation.members.get(federate_name, ""),
            federate_handle,
        )


def ensure_mom_federation_object(backend: Any, federation: Any) -> None:
    class_name = "HLAobjectRoot.HLAmanager.HLAfederation"
    object_name = f"HLAmanager.HLAfederation.{backend._federation_name}"
    if object_name in federation.object_instance_names:
        return
    register_internal_object_instance(
        backend,
        object_class_name=class_name,
        object_instance_name=object_name,
        producing_federate=mom_runtime_federate_handle(),
        owner_by_attribute={},
    )


def ensure_mom_federate_object(
    backend: Any,
    federation: Any,
    federate_name: str,
    federate_type: str,
    federate_handle: FederateHandle,
) -> None:
    class_name = "HLAobjectRoot.HLAmanager.HLAfederate"
    object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{federate_name}"
    if object_name in federation.object_instance_names:
        return
    owner_by_attribute: dict[str, FederateHandle | None] = {
        attribute_name: federate_handle
        for attribute_name in backend._attribute_handles(class_name)
        if attribute_name in {"HLAfederateHandle", "HLAfederateName", "HLAfederateType"}
    }
    register_internal_object_instance(
        backend,
        object_class_name=class_name,
        object_instance_name=object_name,
        producing_federate=federate_handle,
        owner_by_attribute=owner_by_attribute,
    )


def register_internal_object_instance(
    backend: Any,
    object_class_name: str,
    object_instance_name: str,
    *,
    producing_federate: FederateHandle,
    owner_by_attribute: dict[str, FederateHandle | None],
) -> ObjectInstanceHandle:
    federation = backend._federation_record()
    handle = ObjectInstanceHandle(federation.next_object_instance_handle)
    federation.next_object_instance_handle += 1
    federation.object_instances[handle.value] = backend._object_instance_record_type()(
        object_class_name=object_class_name,
        object_instance_name=object_instance_name,
        producing_federate=producing_federate,
        attribute_owners=dict(owner_by_attribute),
    )
    federation.object_instance_names[object_instance_name] = handle.value
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        if federate_key == backend._current_federate_key():
            continue
        discovery_class_name = backend._subscribed_discovery_class_name(
            federate_key,
            object_class_name,
        )
        if discovery_class_name is None:
            continue
        subscribed_names = set(subscriptions.get(discovery_class_name, set()))
        reflected_names = backend._reflectable_attribute_names_for_subscriber(
            producing_federate.value,
            federate_key,
            federation.object_instances[handle.value],
            discovery_class_name,
            subscribed_names,
        )
        if reflected_names:
            backend._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "discoverObjectInstance",
                handle,
                ObjectClassHandle(backend._object_class_handles()[discovery_class_name]),
                object_instance_name,
                producing_federate,
            )
    return handle


def refresh_mom_federation_object(backend: Any) -> None:
    federation = backend._federation_record()
    object_name = f"HLAmanager.HLAfederation.{backend._federation_name}"
    object_value = federation.object_instance_names.get(object_name)
    if object_value is None:
        return
    backend._set_internal_object_attribute_values(
        ObjectInstanceHandle(object_value),
        {
            "HLAfederatesInFederation": ",".join(sorted(federation.members)),
        },
    )


def refresh_mom_federate_object(
    backend: Any,
    federate_name: str,
    federate_type: str,
    federate_handle: FederateHandle,
) -> None:
    federation = backend._federation_record()
    object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{federate_name}"
    object_value = federation.object_instance_names.get(object_name)
    if object_value is None:
        return
    backend._set_internal_object_attribute_values(
        ObjectInstanceHandle(object_value),
        {
            "HLAfederateHandle": str(federate_handle.value),
            "HLAfederateName": federate_name,
            "HLAfederateType": federate_type,
        },
    )


def remove_current_federate_mom_object(backend: Any) -> None:
    federation = backend._federation_record()
    federate_handle = backend._current_federate_handle()
    if backend._federate_name is None:
        return
    object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{backend._federate_name}"
    object_value = federation.object_instance_names.pop(object_name, None)
    if object_value is None:
        return
    record = federation.object_instances.pop(object_value, None)
    if record is None:
        return
    for federate_key, subscriptions in federation.subscribed_object_attributes.items():
        if federate_key == federate_handle.value or record.object_class_name not in subscriptions:
            continue
        backend._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "removeObjectInstance",
            ObjectInstanceHandle(object_value),
            b"",
            federate_handle,
            None,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )


def backend_drop_retraction_group_member(federation: Any, handle_value: int) -> None:
    group_id = federation.retraction_group_lookup.pop(handle_value, None)
    if group_id is None:
        return
    members = federation.retraction_groups.get(group_id)
    if not members:
        federation.retraction_groups.pop(group_id, None)
        return
    members.discard(handle_value)
    if not members:
        federation.retraction_groups.pop(group_id, None)


__all__ = [
    "apply_resign_action",
    "cancel_resigning_federate_pending_acquisitions",
    "delete_objects_owned_by_resigning_federate",
    "delete_objects_owned_by_specific_federate",
    "divest_attributes_owned_by_specific_federate",
    "divest_resigning_federate_attributes",
    "ensure_mom_federate_object",
    "ensure_mom_federation_object",
    "ensure_mom_objects",
    "is_mom_object_class_name",
    "mom_runtime_federate_handle",
    "prune_tso_state_for_departing_federate",
    "refresh_mom_federate_object",
    "refresh_mom_federation_object",
    "register_internal_object_instance",
    "release_join",
    "remove_current_federate_mom_object",
    "resigning_federate_has_pending_acquisitions",
    "resigning_federate_owns_attributes",
]
