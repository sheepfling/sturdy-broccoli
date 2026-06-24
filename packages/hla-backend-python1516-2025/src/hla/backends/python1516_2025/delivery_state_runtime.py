"""Timestamped-delivery and ownership-candidate helpers for the Python 2025 lane."""

from __future__ import annotations

from typing import Any, Iterable

from hla.rti1516_2025.exceptions import FederateNotExecutionMember
from hla.rti1516_2025.handles import FederateHandle, MessageRetractionHandle


def queue_tso_callback(
    backend: Any,
    target_federate: FederateHandle,
    callback_time: Any,
    method_name: str,
    *args: Any,
    exposed_retraction_handle: MessageRetractionHandle | None = None,
) -> MessageRetractionHandle:
    federation = backend._federation_record()
    handle = MessageRetractionHandle(federation.next_message_retraction_handle)
    federation.next_message_retraction_handle += 1
    federation.queued_tso_callbacks[handle.value] = backend._queued_tso_callback_type()(
        target_federate=target_federate,
        callback_time=callback_time,
        serial=handle.value,
        method_name=method_name,
        args=(*args, exposed_retraction_handle or handle),
    )
    backend._process_time_advances()
    return handle


def register_retraction_group(
    federation: Any,
    member_handles: Iterable[MessageRetractionHandle],
) -> MessageRetractionHandle:
    handles = tuple(member_handles)
    if not handles:
        return MessageRetractionHandle(0)
    canonical = handles[0]
    if len(handles) == 1:
        return canonical
    members = {handle.value for handle in handles}
    federation.retraction_groups[canonical.value] = members
    for handle in handles:
        federation.retraction_group_lookup[handle.value] = canonical.value
    return canonical


def resolve_retraction_group(federation: Any, handle_value: int) -> tuple[int, set[int]]:
    if handle_value in federation.retraction_groups:
        return handle_value, set(federation.retraction_groups[handle_value])
    canonical = federation.retraction_group_lookup.get(handle_value)
    if canonical is None:
        return handle_value, {handle_value}
    return canonical, set(federation.retraction_groups.get(canonical, {handle_value}))


def drop_retraction_group_member(federation: Any, handle_value: int) -> None:
    canonical = federation.retraction_group_lookup.get(handle_value)
    if canonical is None:
        return
    members = federation.retraction_groups.get(canonical)
    if members is None:
        federation.retraction_group_lookup.pop(handle_value, None)
        return
    members.discard(handle_value)
    federation.retraction_group_lookup.pop(handle_value, None)
    if members:
        federation.retraction_groups[canonical] = members
        return
    federation.retraction_groups.pop(canonical, None)


def finalize_retraction_group_if_inactive(federation: Any, canonical_handle: int) -> None:
    members = federation.retraction_groups.get(canonical_handle)
    if members is None:
        return
    if any(member in federation.queued_tso_callbacks or member in federation.delivered_retraction_handles for member in members):
        return
    federation.retraction_groups.pop(canonical_handle, None)
    for member in tuple(federation.retraction_group_lookup):
        if federation.retraction_group_lookup.get(member) == canonical_handle:
            federation.retraction_group_lookup.pop(member, None)


def canonicalize_retraction_handles(
    federation: Any,
    handles: list[MessageRetractionHandle],
) -> MessageRetractionHandle:
    canonical = register_retraction_group(federation, handles)
    if len(handles) <= 1:
        return canonical
    for handle in handles[1:]:
        queued = federation.queued_tso_callbacks.get(handle.value)
        if queued is not None:
            queued.args = (*queued.args[:-1], canonical)
    return canonical


def deliver_due_tso_callbacks(backend: Any) -> None:
    federation = backend._federation_record()
    due = sorted(
        (
            (handle_value, queued)
            for handle_value, queued in federation.queued_tso_callbacks.items()
            if queued.target_federate == backend._current_federate_handle() and queued.callback_time <= backend._logical_time
        ),
        key=lambda item: (item[1].callback_time, item[1].serial),
    )
    for handle_value, queued in due:
        federation.queued_tso_callbacks.pop(handle_value, None)
        federation.delivered_retraction_handles.add(handle_value)
        federation.delivered_retraction_targets[handle_value] = queued.target_federate
        backend._deliver_to_federate_handle(queued.target_federate, queued.method_name, *queued.args)


def has_attribute_candidate(
    record: Any,
    attribute_name: str,
    federate_handle: FederateHandle | None,
) -> bool:
    return any(candidate == federate_handle for candidate, _tag in record.attribute_candidates.get(attribute_name, ()))


def add_attribute_candidate(
    record: Any,
    attribute_name: str,
    federate_handle: FederateHandle | None,
    user_supplied_tag: bytes,
) -> None:
    if federate_handle is None:
        raise FederateNotExecutionMember("Current federate handle is not available")
    candidates = record.attribute_candidates.setdefault(attribute_name, [])
    candidates[:] = [(candidate, tag) for candidate, tag in candidates if candidate != federate_handle]
    candidates.append((federate_handle, bytes(user_supplied_tag)))


def remove_attribute_candidate(
    record: Any,
    attribute_name: str,
    federate_handle: FederateHandle | None,
) -> None:
    candidates = record.attribute_candidates.get(attribute_name)
    if candidates is None:
        return
    candidates[:] = [(candidate, tag) for candidate, tag in candidates if candidate != federate_handle]
    if not candidates:
        record.attribute_candidates.pop(attribute_name, None)


def pop_attribute_candidate(
    record: Any,
    attribute_name: str,
) -> tuple[FederateHandle, bytes] | None:
    candidates = record.attribute_candidates.get(attribute_name)
    if not candidates:
        return None
    candidate = candidates.pop(0)
    if not candidates:
        record.attribute_candidates.pop(attribute_name, None)
    return candidate


__all__ = [
    "add_attribute_candidate",
    "canonicalize_retraction_handles",
    "deliver_due_tso_callbacks",
    "drop_retraction_group_member",
    "finalize_retraction_group_if_inactive",
    "has_attribute_candidate",
    "pop_attribute_candidate",
    "queue_tso_callback",
    "register_retraction_group",
    "remove_attribute_candidate",
    "resolve_retraction_group",
]
