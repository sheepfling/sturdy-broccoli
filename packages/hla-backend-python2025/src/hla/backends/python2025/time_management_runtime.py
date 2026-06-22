"""Shared time-management runtime semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from hla.backends.common import time_management as tm
from hla.rti1516_2025.datatypes import TimeQueryReturn
from hla.rti1516_2025.exceptions import (
    InvalidMessageRetractionHandle,
    MessageCanNoLongerBeRetracted,
    TimeConstrainedAlreadyEnabled,
    TimeRegulationAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from hla.rti1516_2025.handles import MessageRetractionHandle


def build_time_management_state(rti: Any) -> Any:
    return SimpleNamespace(
        handle=rti._current_federate_handle(),
        current_time=rti._logical_time,
        lookahead=rti._lookahead,
        time_regulation_enabled=rti._time_regulation_enabled,
        time_constrained_enabled=rti._time_constrained_enabled,
        pending_time_advance=rti._pending_time_advance,
        zero_lookahead_tarnmr_restriction=False,
    )


def build_time_management_federation(federation: Any) -> Any:
    federates = {handle: build_time_management_state(member) for handle, member in federation.member_rtis.items()}
    messages = [
        SimpleNamespace(
            timestamp=queued.callback_time,
            recipient=queued.target_federate,
            sequence=queued.serial,
            retraction_handle=MessageRetractionHandle(handle_value),
            retracted=False,
            delivered=False,
            queued_handle=handle_value,
        )
        for handle_value, queued in federation.queued_tso_callbacks.items()
    ]
    return SimpleNamespace(federates=federates, tso_messages=messages)


def query_galt_for(target: Any) -> TimeQueryReturn:
    federation = target._federation_record()
    others = [
        build_time_management_state(member)
        for handle, member in federation.member_rtis.items()
        if handle != target._current_federate_key() and member._time_regulation_enabled
    ]
    if others:
        query = tm.compute_galt(
            SimpleNamespace(federates={index: state for index, state in enumerate(others, start=1)}, tso_messages=[]),
            build_time_management_state(target),
            include_self=False,
            factory=target._logical_time_factory,
        )
        return TimeQueryReturn(query.time_is_valid, query.time)
    return TimeQueryReturn(True, target._logical_time)


def query_lits_for(target: Any) -> TimeQueryReturn:
    federation = target._federation_record()
    query = tm.compute_lits(
        build_time_management_federation(federation),
        build_time_management_state(target),
        include_galt=False,
        factory=target._logical_time_factory,
    )
    galt = query_galt_for(target)
    candidates = [query.time] if query.time_is_valid and query.time is not None else []
    if galt.timeIsValid and galt.time is not None:
        candidates.append(galt.time)
    if not candidates:
        return TimeQueryReturn(False, None)
    return TimeQueryReturn(True, min(candidates))


def validate_tso_send_time(rti: Any, timestamp: Any, *, invalid_logical_time_exc: type[Exception]) -> None:
    if not rti._time_regulation_enabled:
        raise invalid_logical_time_exc("Timestamp-order messages require time regulation to be enabled")
    lower_bound = tm.valid_tso_lower_bound(build_time_management_state(rti), factory=rti._logical_time_factory)
    if lower_bound is not None and timestamp < lower_bound:
        raise invalid_logical_time_exc(
            f"TSO timestamp {timestamp!r} is earlier than logical time/lookahead bound {lower_bound!r}"
        )


def enable_time_regulation(rti: Any, lookahead: Any) -> None:
    if rti._time_regulation_enabled:
        raise TimeRegulationAlreadyEnabled("Time regulation is already enabled")
    rti._lookahead = rti._coerce_interval(lookahead)
    rti._time_regulation_enabled = True
    if rti._federate_ambassador is not None and hasattr(rti._federate_ambassador, "timeRegulationEnabled"):
        rti._deliver_callback("timeRegulationEnabled", rti._logical_time)


def disable_time_regulation(rti: Any) -> None:
    rti._time_regulation_enabled = False
    rti._lookahead = rti._logical_time_factory.makeZero()
    process_time_advances(rti)


def enable_time_constrained(rti: Any) -> None:
    if rti._time_constrained_enabled:
        raise TimeConstrainedAlreadyEnabled("Time constrained mode is already enabled")
    rti._time_constrained_enabled = True
    if rti._federate_ambassador is not None and hasattr(rti._federate_ambassador, "timeConstrainedEnabled"):
        rti._deliver_callback("timeConstrainedEnabled", rti._logical_time)
    process_time_advances(rti)


def disable_time_constrained(rti: Any) -> None:
    rti._time_constrained_enabled = False
    process_time_advances(rti)


def modify_lookahead(rti: Any, lookahead: Any) -> None:
    if not rti._time_regulation_enabled:
        raise TimeRegulationIsNotEnabled("Cannot modify lookahead before enableTimeRegulation")
    rti._lookahead = rti._coerce_interval(lookahead)
    process_time_advances(rti)


def query_lookahead(rti: Any) -> Any:
    if not rti._time_regulation_enabled:
        raise TimeRegulationIsNotEnabled("Cannot query lookahead before enableTimeRegulation")
    return rti._lookahead


def retract_message(rti: Any, retraction: Any) -> None:
    retraction_value = rti._normalize_handle(
        retraction,
        MessageRetractionHandle,
        InvalidMessageRetractionHandle,
    )
    federation = rti._federation_record()
    canonical_handle, member_handles = rti._resolve_retraction_group(federation, retraction_value)
    queued_removed = False
    delivered_targets: list[Any] = []
    delivered_state_seen = False
    for handle_value in member_handles:
        if federation.queued_tso_callbacks.pop(handle_value, None) is not None:
            queued_removed = True
            rti._drop_retraction_group_member(federation, handle_value)
        if handle_value in federation.delivered_retraction_handles:
            delivered_state_seen = True
            target = federation.delivered_retraction_targets.pop(handle_value, None)
            if target is not None:
                delivered_targets.append(target)
    if queued_removed or delivered_targets:
        seen_targets: set[int] = set()
        for target in delivered_targets:
            if target.value in seen_targets:
                continue
            seen_targets.add(target.value)
            rti._deliver_to_federate_handle(
                target,
                "requestRetraction",
                MessageRetractionHandle(canonical_handle),
            )
        if not delivered_targets:
            rti._finalize_retraction_group_if_inactive(federation, canonical_handle)
        return
    if delivered_state_seen:
        raise MessageCanNoLongerBeRetracted(str(retraction))
    raise InvalidMessageRetractionHandle(str(retraction))


def request_time_advance(
    rti: Any,
    mode: str,
    time: Any,
    *,
    logical_time_already_passed_exc: type[Exception],
) -> None:
    requested_time = rti._coerce_time(time)
    if requested_time < rti._logical_time:
        raise logical_time_already_passed_exc(str(requested_time))
    rti._pending_time_advance = tm.TimeAdvanceRequestState(mode, requested_time)
    process_time_advances(rti)


def process_time_advances(rti: Any) -> None:
    if not rti._joined or rti._federation_name is None:
        return
    federation = rti._federation_record()
    progressed = True
    while progressed:
        progressed = False
        for member in list(federation.member_rtis.values()):
            if member._pending_time_advance is None:
                continue
            if try_grant_pending_time_advance(member):
                progressed = True
    rti._process_scheduled_save(federation)


def try_grant_pending_time_advance(rti: Any) -> bool:
    request = rti._pending_time_advance
    if request is None:
        return False
    federation = rti._federation_record()
    state = build_time_management_state(rti)
    decision = tm.compute_grant_decision(
        build_time_management_federation(federation),
        state,
        request,
        enforce_galt=True,
        factory=rti._logical_time_factory,
    )
    if not decision.can_grant or decision.grant_time is None:
        return False
    deliver_due_tso_callbacks_for_request(rti, decision.deliverable_messages)
    rti._logical_time = decision.grant_time
    rti._pending_time_advance = None
    if request.mode == "flushQueueRequest":
        rti._deliver_callback(
            "flushQueueGrant",
            decision.grant_time,
            decision.optimistic_time or decision.grant_time,
        )
    else:
        rti._deliver_callback("timeAdvanceGrant", decision.grant_time)
    return True


def deliver_due_tso_callbacks_for_request(rti: Any, deliverable_messages: tuple[Any, ...]) -> None:
    federation = rti._federation_record()
    for message in deliverable_messages:
        handle_value = getattr(message, "queued_handle", None)
        if handle_value is None:
            continue
        queued = federation.queued_tso_callbacks.pop(handle_value, None)
        if queued is None:
            continue
        federation.delivered_retraction_handles.add(handle_value)
        federation.delivered_retraction_targets[handle_value] = queued.target_federate
        rti._deliver_to_federate_handle(queued.target_federate, queued.method_name, *queued.args)
