"""Save/restore runtime semantics for the dedicated Python 2025 lane."""

from __future__ import annotations

import copy
from typing import Any

from hla.backends.common import time_management as tm
from hla.rti1516_2025.datatypes import FederateHandleSaveStatusPair, FederateRestoreStatus
from hla.rti1516_2025.enums import RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
from hla.rti1516_2025.exceptions import (
    LogicalTimeAlreadyPassed,
    RestoreInProgress,
    RestoreNotInProgress,
    RestoreNotRequested,
    SaveInProgress,
    SaveNotInitiated,
    SaveNotInProgress,
)


def capture_federation_save_snapshot(federation: Any, label: str) -> None:
    """Capture the federation-owned state that must roll back on restore."""
    federation.saved_labels.add(label)
    federation.saved_object_instances[label] = copy.deepcopy(federation.object_instances)
    federation.saved_object_instance_names[label] = dict(federation.object_instance_names)
    federation.saved_reserved_object_instance_names[label] = dict(federation.reserved_object_instance_names)
    federation.saved_next_object_instance_handles[label] = federation.next_object_instance_handle
    federation.saved_member_logical_times[label] = {
        federate_key: rti._logical_time
        for federate_key, rti in federation.member_rtis.items()
    }
    federation.saved_published_object_attributes[label] = copy.deepcopy(federation.published_object_attributes)
    federation.saved_subscribed_object_attributes[label] = copy.deepcopy(federation.subscribed_object_attributes)
    federation.saved_subscribed_object_regions[label] = copy.deepcopy(federation.subscribed_object_regions)
    federation.saved_published_interactions[label] = copy.deepcopy(federation.published_interactions)
    federation.saved_subscribed_interactions[label] = copy.deepcopy(federation.subscribed_interactions)
    federation.saved_subscribed_interaction_regions[label] = copy.deepcopy(federation.subscribed_interaction_regions)
    federation.saved_directed_interaction_region_gates[label] = copy.deepcopy(federation.directed_interaction_region_gates)
    federation.saved_published_directed_interactions[label] = copy.deepcopy(federation.published_directed_interactions)
    federation.saved_subscribed_directed_interactions[label] = copy.deepcopy(federation.subscribed_directed_interactions)
    federation.saved_member_regions[label] = copy.deepcopy(federation.member_regions)
    federation.saved_member_region_bounds[label] = copy.deepcopy(federation.member_region_bounds)
    federation.saved_queued_tso_callbacks[label] = copy.deepcopy(federation.queued_tso_callbacks)
    federation.saved_delivered_retraction_handles[label] = set(federation.delivered_retraction_handles)
    federation.saved_delivered_retraction_targets[label] = dict(federation.delivered_retraction_targets)
    federation.saved_retraction_groups[label] = copy.deepcopy(federation.retraction_groups)
    federation.saved_retraction_group_lookup[label] = dict(federation.retraction_group_lookup)
    federation.saved_member_time_states[label] = {
        federate_key: {
            "lookahead": rti._lookahead,
            "time_regulation_enabled": rti._time_regulation_enabled,
            "time_constrained_enabled": rti._time_constrained_enabled,
            "asynchronous_delivery_enabled": rti._asynchronous_delivery_enabled,
            "callbacks_enabled": rti._callbacks_enabled,
            "automatic_resign_directive": rti._automatic_resign_directive,
            "switches": copy.deepcopy(rti._switches),
            "default_attribute_transportation": copy.deepcopy(rti._default_attribute_transportation),
            "default_attribute_order": copy.deepcopy(rti._default_attribute_order),
        }
        for federate_key, rti in federation.member_rtis.items()
    }
    federation.saved_member_known_objects[label] = {
        federate_key: {
            "known_object_classes": dict(rti._known_object_classes),
            "known_object_names": dict(rti._known_object_names),
            "locally_deleted_objects": set(rti._locally_deleted_objects),
        }
        for federate_key, rti in federation.member_rtis.items()
    }
    federation.saved_interaction_order[label] = copy.deepcopy(federation.interaction_order)
    federation.saved_interaction_transportation[label] = copy.deepcopy(federation.interaction_transportation)
    for rti in federation.member_rtis.values():
        rti._evoked_callback_queue.clear()


def restore_federation_save_snapshot(federation: Any, label: str) -> None:
    """Restore federation-owned state from a previously captured label."""
    federation.object_instances = copy.deepcopy(federation.saved_object_instances.get(label, {}))
    federation.object_instance_names = dict(federation.saved_object_instance_names.get(label, {}))
    federation.reserved_object_instance_names = dict(
        federation.saved_reserved_object_instance_names.get(label, {})
    )
    federation.published_object_attributes = copy.deepcopy(
        federation.saved_published_object_attributes.get(label, federation.published_object_attributes)
    )
    federation.subscribed_object_attributes = copy.deepcopy(
        federation.saved_subscribed_object_attributes.get(label, federation.subscribed_object_attributes)
    )
    federation.subscribed_object_regions = copy.deepcopy(
        federation.saved_subscribed_object_regions.get(label, federation.subscribed_object_regions)
    )
    federation.published_interactions = copy.deepcopy(
        federation.saved_published_interactions.get(label, federation.published_interactions)
    )
    federation.subscribed_interactions = copy.deepcopy(
        federation.saved_subscribed_interactions.get(label, federation.subscribed_interactions)
    )
    federation.subscribed_interaction_regions = copy.deepcopy(
        federation.saved_subscribed_interaction_regions.get(label, federation.subscribed_interaction_regions)
    )
    federation.directed_interaction_region_gates = copy.deepcopy(
        federation.saved_directed_interaction_region_gates.get(label, federation.directed_interaction_region_gates)
    )
    federation.published_directed_interactions = copy.deepcopy(
        federation.saved_published_directed_interactions.get(label, federation.published_directed_interactions)
    )
    federation.subscribed_directed_interactions = copy.deepcopy(
        federation.saved_subscribed_directed_interactions.get(label, federation.subscribed_directed_interactions)
    )
    federation.member_regions = copy.deepcopy(
        federation.saved_member_regions.get(label, federation.member_regions)
    )
    federation.member_region_bounds = copy.deepcopy(
        federation.saved_member_region_bounds.get(label, federation.member_region_bounds)
    )
    federation.queued_tso_callbacks = copy.deepcopy(
        federation.saved_queued_tso_callbacks.get(label, federation.queued_tso_callbacks)
    )
    federation.delivered_retraction_handles = set(
        federation.saved_delivered_retraction_handles.get(label, federation.delivered_retraction_handles)
    )
    federation.delivered_retraction_targets = dict(
        federation.saved_delivered_retraction_targets.get(label, federation.delivered_retraction_targets)
    )
    federation.retraction_groups = copy.deepcopy(
        federation.saved_retraction_groups.get(label, federation.retraction_groups)
    )
    federation.retraction_group_lookup = dict(
        federation.saved_retraction_group_lookup.get(label, federation.retraction_group_lookup)
    )
    federation.interaction_order = copy.deepcopy(
        federation.saved_interaction_order.get(label, federation.interaction_order)
    )
    federation.interaction_transportation = copy.deepcopy(
        federation.saved_interaction_transportation.get(label, federation.interaction_transportation)
    )
    federation.next_object_instance_handle = federation.saved_next_object_instance_handles.get(
        label,
        federation.next_object_instance_handle,
    )
    for federate_key, logical_time in federation.saved_member_logical_times.get(label, {}).items():
        rti = federation.member_rtis.get(federate_key)
        if rti is not None:
            rti._logical_time = logical_time
    for federate_key, values in federation.saved_member_time_states.get(label, {}).items():
        rti = federation.member_rtis.get(federate_key)
        if rti is None:
            continue
        rti._lookahead = values.get("lookahead", rti._lookahead)
        rti._time_regulation_enabled = bool(
            values.get("time_regulation_enabled", rti._time_regulation_enabled)
        )
        rti._time_constrained_enabled = bool(
            values.get("time_constrained_enabled", rti._time_constrained_enabled)
        )
        rti._asynchronous_delivery_enabled = bool(
            values.get(
                "asynchronous_delivery_enabled",
                rti._asynchronous_delivery_enabled,
            )
        )
        rti._automatic_resign_directive = values.get(
            "automatic_resign_directive",
            rti._automatic_resign_directive,
        )
        rti._switches = dict(values.get("switches", rti._switches))
        rti._default_attribute_transportation = copy.deepcopy(
            values.get(
                "default_attribute_transportation",
                rti._default_attribute_transportation,
            )
        )
        rti._default_attribute_order = copy.deepcopy(
            values.get("default_attribute_order", rti._default_attribute_order)
        )
        rti._evoked_callback_queue.clear()
    for federate_key, values in federation.saved_member_known_objects.get(label, {}).items():
        rti = federation.member_rtis.get(federate_key)
        if rti is None:
            continue
        rti._known_object_classes = dict(values.get("known_object_classes", rti._known_object_classes))
        rti._known_object_names = dict(values.get("known_object_names", rti._known_object_names))
        rti._locally_deleted_objects = set(values.get("locally_deleted_objects", rti._locally_deleted_objects))


def request_federation_save(rti: Any, label: str, time: Any | None = None) -> None:
    """Begin or schedule a federation save for the current federation."""
    federation = rti._federation_record()
    if federation.save_label is not None or federation.next_save_name is not None:
        raise SaveInProgress("A federation save is already in progress")
    if federation.restore_label is not None:
        raise RestoreInProgress("A federation restore is already in progress")
    if time is not None:
        save_time = rti._coerce_time(time)
        if save_time < rti._logical_time:
            raise LogicalTimeAlreadyPassed(str(time))
        federation.next_save_name = str(label)
        federation.next_save_time = save_time
        process_scheduled_save(rti, federation)
        return
    start_federation_save(rti, federation, str(label), None)


def start_federation_save(
    rti: Any,
    federation: Any,
    label: str,
    save_time: Any | None,
) -> None:
    """Drive initiateFederateSave callbacks for a new active save."""
    federation.save_label = str(label)
    federation.next_save_name = None
    federation.next_save_time = None
    federation.save_status = {
        handle.value: SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE
        for handle in federation.member_handles.values()
    }
    for federate_handle in federation.member_handles.values():
        if save_time is None:
            rti._deliver_to_federate_handle(federate_handle, "initiateFederateSave", str(label))
        else:
            rti._deliver_to_federate_handle(federate_handle, "initiateFederateSave", str(label), save_time)


def process_scheduled_save(rti: Any, federation: Any) -> None:
    """Start a scheduled save once constrained members have safely reached the save time."""
    if (
        federation.next_save_name is None
        or federation.next_save_time is None
        or federation.save_label is not None
    ):
        return
    save_time = federation.next_save_time
    federation_state = rti._time_management_federation(federation)
    for member in list(federation.member_rtis.values()):
        state = member._time_management_state()
        if not state.time_constrained_enabled:
            continue
        if any(
            queued.target_federate == member._current_federate_handle() and queued.callback_time <= save_time
            for queued in federation.queued_tso_callbacks.values()
        ):
            return
        request = member._pending_time_advance
        next_grant = None
        if request is not None:
            decision = tm.compute_grant_decision(
                federation_state,
                state,
                request,
                enforce_galt=True,
                factory=member._logical_time_factory,
            )
            next_grant = decision.grant_time if decision.can_grant else getattr(request, "requested_time", None)
        if not tm.scheduled_save_time_reached(state, save_time, next_grant_time=next_grant):
            return
    start_federation_save(rti, federation, federation.next_save_name, save_time)


def federate_save_begun(rti: Any) -> None:
    """Mark the local federate as actively saving."""
    federation = rti._federation_record()
    if federation.save_label is None:
        raise SaveNotInitiated("No federation save is in progress")
    federation.save_status[rti._current_federate_key()] = SaveStatus.FEDERATE_SAVING


def complete_save(rti: Any, *, success: bool) -> None:
    """Finalize the local federate's save response and close the federation save if complete."""
    federation = rti._federation_record()
    if federation.save_label is None:
        raise SaveNotInitiated("No federation save is in progress")
    federation.save_status[rti._current_federate_key()] = SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
    if not success:
        for federate_handle in federation.member_handles.values():
            rti._deliver_to_federate_handle(
                federate_handle,
                "federationNotSaved",
                SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
            )
        federation.save_label = None
        federation.save_status.clear()
        return
    if federation.save_status and all(
        status is SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
        for status in federation.save_status.values()
    ):
        label = federation.save_label
        assert label is not None
        capture_federation_save_snapshot(federation, label)
        for federate_handle in federation.member_handles.values():
            rti._deliver_to_federate_handle(federate_handle, "federationSaved")
        federation.save_label = None
        federation.save_status.clear()


def abort_federation_save(rti: Any) -> None:
    """Abort an active or scheduled federation save."""
    federation = rti._federation_record()
    if federation.save_label is None and federation.next_save_name is None:
        raise SaveNotInProgress("No federation save is in progress")
    for federate_handle in federation.member_handles.values():
        rti._deliver_to_federate_handle(federate_handle, "federationNotSaved", SaveFailureReason.SAVE_ABORTED)
    federation.save_label = None
    federation.next_save_name = None
    federation.next_save_time = None
    federation.save_status.clear()


def query_federation_save_status(rti: Any) -> None:
    """Emit the current federation save status vector."""
    federation = rti._federation_record()
    response = [
        FederateHandleSaveStatusPair(
            handle,
            federation.save_status.get(handle.value, SaveStatus.NO_SAVE_IN_PROGRESS),
        )
        for handle in federation.member_handles.values()
    ]
    rti._deliver_callback("federationSaveStatusResponse", response)


def request_federation_restore(rti: Any, label: str) -> None:
    """Begin a federation restore if a saved label exists."""
    federation = rti._federation_record()
    if federation.save_label is not None:
        raise SaveInProgress("A federation save is already in progress")
    if federation.restore_label is not None:
        raise RestoreInProgress("A federation restore is already in progress")
    restore_label = str(label)
    if restore_label not in federation.saved_labels:
        rti._deliver_callback_now("requestFederationRestoreFailed", restore_label)
        return
    federation.restore_label = restore_label
    federation.restore_status = {
        handle.value: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
        for handle in federation.member_handles.values()
    }
    rti._deliver_callback_now("requestFederationRestoreSucceeded", restore_label)
    for federate_name, federate_handle in federation.member_handles.items():
        rti._deliver_to_federate_handle_now(federate_handle, "federationRestoreBegun")
        rti._deliver_to_federate_handle_now(
            federate_handle,
            "initiateFederateRestore",
            restore_label,
            federate_name,
            federate_handle,
        )


def complete_restore(rti: Any, *, success: bool) -> None:
    """Finalize the local federate's restore response and close the federation restore if complete."""
    federation = rti._federation_record()
    if federation.restore_label is None:
        raise RestoreNotRequested("No federation restore is in progress")
    federation.restore_status[rti._current_federate_key()] = RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
    if not success:
        for federate_handle in federation.member_handles.values():
            rti._deliver_to_federate_handle(
                federate_handle,
                "federationNotRestored",
                RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
            )
        federation.restore_label = None
        federation.restore_status.clear()
        return
    if federation.restore_status and all(
        status is RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
        for status in federation.restore_status.values()
    ):
        label = federation.restore_label
        assert label is not None
        restore_federation_save_snapshot(federation, label)
        for federate_handle in federation.member_handles.values():
            target_rti = federation.member_rtis.get(federate_handle.value)
            if target_rti is not None and not target_rti._callbacks_enabled:
                continue
            rti._deliver_to_federate_handle_now(federate_handle, "federationRestored")
        federation.restore_label = None
        federation.restore_status.clear()


def abort_federation_restore(rti: Any) -> None:
    """Abort an active federation restore."""
    federation = rti._federation_record()
    if federation.restore_label is None:
        raise RestoreNotInProgress("No federation restore is in progress")
    for federate_handle in federation.member_handles.values():
        rti._deliver_to_federate_handle_now(
            federate_handle,
            "federationNotRestored",
            RestoreFailureReason.RESTORE_ABORTED,
        )
    federation.restore_label = None
    federation.restore_status.clear()


def query_federation_restore_status(rti: Any) -> None:
    """Emit the current federation restore status vector."""
    federation = rti._federation_record()
    response = [
        FederateRestoreStatus(
            handle,
            handle,
            federation.restore_status.get(handle.value, RestoreStatus.NO_RESTORE_IN_PROGRESS),
        )
        for handle in federation.member_handles.values()
    ]
    rti._deliver_callback_now("federationRestoreStatusResponse", response)


__all__ = [
    "abort_federation_restore",
    "abort_federation_save",
    "capture_federation_save_snapshot",
    "complete_restore",
    "complete_save",
    "federate_save_begun",
    "process_scheduled_save",
    "query_federation_restore_status",
    "query_federation_save_status",
    "request_federation_restore",
    "request_federation_save",
    "restore_federation_save_snapshot",
    "start_federation_save",
]
