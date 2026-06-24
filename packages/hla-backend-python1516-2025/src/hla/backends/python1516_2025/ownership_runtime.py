from __future__ import annotations

from typing import Any

from hla.rti1516_2025.exceptions import (
    AttributeAcquisitionWasNotRequested,
    AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested,
    AttributeAlreadyOwned,
    AttributeDivestitureWasNotRequested,
    AttributeNotOwned,
    NoAcquisitionPending,
)
from hla.rti1516_2025.handles import AttributeHandle, FederateHandle


def unconditional_attribute_ownership_divestiture(
    backend: Any,
    object_instance: Any,
    attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_names = backend._attribute_names_from_handles(record.object_class_name, attributes)
    for attribute_name in attribute_names:
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
    for attribute_name in attribute_names:
        candidate = backend._pop_attribute_candidate(record, attribute_name)
        if candidate is None:
            record.attribute_owners[attribute_name] = None
            record.attribute_divesting.discard(attribute_name)
            continue
        new_owner, acquisition_tag = candidate
        record.attribute_owners[attribute_name] = new_owner
        record.attribute_divesting.discard(attribute_name)
        attribute_handle = AttributeHandle(backend._attribute_handles(record.object_class_name)[attribute_name])
        backend._deliver_to_federate_handle(
            new_owner,
            "attributeOwnershipAcquisitionNotification",
            object_instance,
            {attribute_handle},
            acquisition_tag,
        )


def negotiated_attribute_ownership_divestiture(
    backend: Any,
    object_instance: Any,
    attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_names = backend._attribute_names_from_handles(record.object_class_name, attributes)
    for attribute_name in attribute_names:
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
        if attribute_name in record.attribute_divesting:
            raise AttributeAlreadyBeingDivested(attribute_name)

    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    for attribute_name in attribute_names:
        candidate = backend._pop_attribute_candidate(record, attribute_name)
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        if candidate is not None:
            new_owner, _candidate_tag = candidate
            record.attribute_owners[attribute_name] = new_owner
            record.attribute_divesting.discard(attribute_name)
            backend._deliver_callback(
                "requestDivestitureConfirmation",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )
            backend._deliver_to_federate_handle(
                new_owner,
                "attributeOwnershipAcquisitionNotification",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )
            continue

        record.attribute_divesting.add(attribute_name)
        for federate_handle in backend._other_member_handles():
            backend._deliver_to_federate_handle(
                federate_handle,
                "requestAttributeOwnershipAssumption",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )


def confirm_divestiture(
    backend: Any,
    object_instance: Any,
    confirmed_attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_names = backend._attribute_names_from_handles(record.object_class_name, confirmed_attributes)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    for attribute_name in attribute_names:
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
        if attribute_name not in record.attribute_divesting:
            raise AttributeDivestitureWasNotRequested(attribute_name)
        if not record.attribute_candidates.get(attribute_name):
            raise NoAcquisitionPending(attribute_name)

    for attribute_name in attribute_names:
        new_owner, _candidate_tag = backend._pop_attribute_candidate(record, attribute_name) or (None, b"")
        if new_owner is None:
            raise NoAcquisitionPending(attribute_name)
        record.attribute_owners[attribute_name] = new_owner
        record.attribute_divesting.discard(attribute_name)
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        backend._deliver_to_federate_handle(
            new_owner,
            "attributeOwnershipAcquisitionNotification",
            object_instance,
            {attribute_handle},
            bytes(user_supplied_tag),
        )


def attribute_ownership_acquisition(
    backend: Any,
    object_instance: Any,
    desired_attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_names = backend._attribute_names_from_handles(record.object_class_name, desired_attributes)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    for attribute_name in attribute_names:
        current_owner = record.attribute_owners.get(attribute_name)
        if current_owner == backend._federate_handle:
            raise AttributeAlreadyOwned(attribute_name)
        if backend._has_attribute_candidate(record, attribute_name, backend._federate_handle):
            raise AttributeAlreadyBeingAcquired(attribute_name)

    for attribute_name in attribute_names:
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        current_owner = record.attribute_owners.get(attribute_name)
        if current_owner is None:
            record.attribute_owners[attribute_name] = backend._federate_handle
            backend._deliver_callback(
                "attributeOwnershipAcquisitionNotification",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )
        elif attribute_name in record.attribute_divesting:
            backend._add_attribute_candidate(record, attribute_name, backend._federate_handle, bytes(user_supplied_tag))
            backend._deliver_to_federate_handle(
                current_owner,
                "requestDivestitureConfirmation",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )
        else:
            backend._add_attribute_candidate(record, attribute_name, backend._federate_handle, bytes(user_supplied_tag))
            backend._deliver_to_federate_handle(
                current_owner,
                "requestAttributeOwnershipRelease",
                object_instance,
                {attribute_handle},
                bytes(user_supplied_tag),
            )


def attribute_ownership_acquisition_if_available(
    backend: Any,
    object_instance: Any,
    desired_attributes: Any,
    user_supplied_tag: bytes,
) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    available: set[AttributeHandle] = set()
    unavailable: set[AttributeHandle] = set()
    for attribute_name in backend._attribute_names_from_handles(record.object_class_name, desired_attributes):
        current_owner = record.attribute_owners.get(attribute_name)
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        if current_owner == backend._federate_handle:
            raise AttributeAlreadyOwned(attribute_name)
        if backend._has_attribute_candidate(record, attribute_name, backend._federate_handle):
            raise AttributeAlreadyBeingAcquired(attribute_name)
        if current_owner is None:
            record.attribute_owners[attribute_name] = backend._federate_handle
            available.add(attribute_handle)
        else:
            unavailable.add(attribute_handle)
    if available:
        backend._deliver_callback("attributeOwnershipAcquisitionNotification", object_instance, available, user_supplied_tag)
    if unavailable:
        backend._deliver_callback("attributeOwnershipUnavailable", object_instance, unavailable, user_supplied_tag)


def attribute_ownership_release_denied(backend: Any, object_instance: Any, attributes: Any) -> None:
    record = backend._object_instance_record(object_instance)
    for attribute_name in backend._attribute_names_from_handles(record.object_class_name, attributes):
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
        record.attribute_candidates.pop(attribute_name, None)


def attribute_ownership_divestiture_if_wanted(
    backend: Any,
    object_instance: Any,
    attributes: Any,
) -> set[AttributeHandle]:
    record = backend._object_instance_record(object_instance)
    attribute_names = backend._attribute_names_from_handles(record.object_class_name, attributes)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    for attribute_name in attribute_names:
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
        if not record.attribute_candidates.get(attribute_name):
            raise NoAcquisitionPending(attribute_name)

    divested: set[AttributeHandle] = set()
    for attribute_name in attribute_names:
        new_owner, _candidate_tag = backend._pop_attribute_candidate(record, attribute_name) or (None, b"")
        if new_owner is None:
            raise NoAcquisitionPending(attribute_name)
        record.attribute_owners[attribute_name] = new_owner
        record.attribute_divesting.discard(attribute_name)
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        divested.add(attribute_handle)
        backend._deliver_to_federate_handle(
            new_owner,
            "attributeOwnershipAcquisitionNotification",
            object_instance,
            {attribute_handle},
            b"",
        )
    return divested


def cancel_negotiated_attribute_ownership_divestiture(
    backend: Any,
    object_instance: Any,
    attributes: Any,
) -> None:
    record = backend._object_instance_record(object_instance)
    for attribute_name in backend._attribute_names_from_handles(record.object_class_name, attributes):
        if record.attribute_owners.get(attribute_name) != backend._federate_handle:
            raise AttributeNotOwned(attribute_name)
        if attribute_name not in record.attribute_divesting:
            raise AttributeDivestitureWasNotRequested(attribute_name)
        record.attribute_divesting.discard(attribute_name)


def cancel_attribute_ownership_acquisition(backend: Any, object_instance: Any, attributes: Any) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    cancelled: set[AttributeHandle] = set()
    for attribute_name in backend._attribute_names_from_handles(record.object_class_name, attributes):
        if record.attribute_owners.get(attribute_name) == backend._federate_handle:
            raise AttributeAlreadyOwned(attribute_name)
        if not backend._has_attribute_candidate(record, attribute_name, backend._federate_handle):
            raise AttributeAcquisitionWasNotRequested(attribute_name)
        backend._remove_attribute_candidate(record, attribute_name, backend._federate_handle)
        cancelled.add(AttributeHandle(attribute_handles_by_name[attribute_name]))
    backend._deliver_callback("confirmAttributeOwnershipAcquisitionCancellation", object_instance, cancelled)


def query_attribute_ownership(backend: Any, object_instance: Any, attributes: Any) -> None:
    record = backend._object_instance_record(object_instance)
    attribute_handles_by_name = backend._attribute_handles(record.object_class_name)
    owned_by_federate: dict[FederateHandle, set[AttributeHandle]] = {}
    not_owned: set[AttributeHandle] = set()
    for attribute_name in backend._attribute_names_from_handles(record.object_class_name, attributes):
        attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
        owner = record.attribute_owners.get(attribute_name)
        if owner is None:
            not_owned.add(attribute_handle)
        else:
            owned_by_federate.setdefault(owner, set()).add(attribute_handle)
    for owner, owned_attributes in sorted(owned_by_federate.items(), key=lambda item: item[0].value):
        backend._deliver_callback_now("informAttributeOwnership", object_instance, owned_attributes, owner)
    if not_owned:
        backend._deliver_callback_now("attributeIsNotOwned", object_instance, not_owned)


def is_attribute_owned_by_federate(backend: Any, object_instance: Any, attribute: Any) -> bool:
    record = backend._object_instance_record(object_instance)
    attribute_name = backend._attribute_names_from_handles(record.object_class_name, {attribute})[0]
    return record.attribute_owners.get(attribute_name) == backend._federate_handle
