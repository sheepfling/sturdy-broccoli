"""Distributed logical-time helpers for the pure Python RTI.

This module is deliberately independent from ``hla2010.backends.python``.
It operates on the backend's duck-typed federation/federate/message state
objects, so the HLA 1516.1 time-management rules can be tested without the
object-management and MOM plumbing.

Section anchors:
* IEEE 1516.1-2010 §8.1.4-§8.1.6 for valid TSO timestamps, GALT, and LITS.
* IEEE 1516.1-2010 §8.8-§8.13 for TAR/TARA/NMR/NMRA/FQR grant semantics.
* IEEE 1516.1-2010 §4.19 for scheduled federation-save eligibility with time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from .types import TimeQueryReturn

TAR = "TAR"
TARA = "TARA"
NMR = "NMR"
NMRA = "NMRA"
FQR = "FQR"

STRICT_GALT_MODES = {TAR, NMR, "timeAdvanceRequest", "nextMessageRequest"}
INCLUSIVE_GALT_MODES = {
    TARA,
    NMRA,
    FQR,
    "timeAdvanceRequestAvailable",
    "nextMessageRequestAvailable",
    "flushQueueRequest",
}
ALL_ADVANCE_MODES = STRICT_GALT_MODES | INCLUSIVE_GALT_MODES


@dataclass(frozen=True)
class TimeAdvanceRequestState:
    """Pending time-advance request used by pure-Python RTI coordination."""

    mode: str
    requested_time: Any


@dataclass(frozen=True)
class TimeGrantDecision:
    """Decision returned by :func:`compute_grant_decision`.

    ``grant_time`` is the time supplied to Time Advance Grant for normal
    time-advance services. ``optimistic_time`` is populated for Flush Queue
    Request; when GALT is not the limiting value it is the same as
    ``grant_time``. ``deliverable_messages`` is already ordered by timestamp
    and insertion sequence.
    """

    can_grant: bool
    grant_time: Any | None = None
    optimistic_time: Any | None = None
    deliverable_messages: tuple[Any, ...] = field(default_factory=tuple)
    reason: str = ""


def time_value(value: Any) -> float | int:
    """Return the primitive value carried by an HLA logical-time object."""

    return getattr(value, "value", value)


def time_key(value: Any) -> float:
    return float(time_value(value))


def time_lt(left: Any, right: Any) -> bool:
    return time_key(left) < time_key(right)


def time_le(left: Any, right: Any) -> bool:
    return time_key(left) <= time_key(right)


def time_ge(left: Any, right: Any) -> bool:
    return time_key(left) >= time_key(right)


def time_eq(left: Any, right: Any) -> bool:
    return time_key(left) == time_key(right)


def time_min(values: Iterable[Any]) -> Any:
    return min(values, key=time_key)


def add_time(time_value_obj: Any, interval: Any, *, factory: Any | None = None) -> Any:
    """Add a logical-time interval while preserving the time implementation."""

    if hasattr(time_value_obj, "add"):
        return time_value_obj.add(interval)
    total = time_value(time_value_obj) + time_value(interval)
    if factory is not None:
        return factory.make_time(total)
    return total


def time_add(time_value_obj: Any, interval: Any, factory: Any | None = None) -> Any:
    """Backward-compatible positional wrapper around :func:`add_time`."""

    return add_time(time_value_obj, interval, factory=factory)


def coerce_time_like(reference: Any, raw: Any, *, factory: Any | None = None) -> Any:
    """Coerce a primitive ``raw`` value to the same logical-time type."""

    if reference is not None and raw.__class__ is reference.__class__:
        return raw
    if factory is not None:
        return factory.make_time(time_value(raw))
    cls = reference.__class__ if reference is not None else None
    if cls is not None:
        try:
            return cls(time_value(raw))
        except Exception:
            pass
    return raw


def _federate_handle(state: Any) -> Any | None:
    return getattr(state, "handle", None)


def _request_mode(request: Any) -> str | None:
    return getattr(request, "mode", None) if request is not None else None


def _request_time(request: Any) -> Any | None:
    return getattr(request, "requested_time", None) if request is not None else None


def regulating_base_time(federate: Any) -> Any:
    """Base time used for a time-regulating federate's lower-bound.

    When the regulating federate has an outstanding time-advance request, the
    requested time is the relevant lower-bound base; otherwise current logical
    time is used. Lookahead is added by :func:`regulating_lower_bound`.
    """

    request = getattr(federate, "pending_time_advance", None)
    return _request_time(request) if request is not None else getattr(federate, "current_time")


def regulating_lower_bound(federate: Any, *, factory: Any | None = None) -> Any | None:
    if not getattr(federate, "time_regulation_enabled", False):
        return None
    lookahead = getattr(federate, "lookahead", None)
    if lookahead is None:
        return None
    return add_time(regulating_base_time(federate), lookahead, factory=factory)


def _message_sequence(msg: Any) -> int:
    if hasattr(msg, "sequence"):
        return int(getattr(msg, "sequence"))
    sort_key = getattr(msg, "sort_key", None)
    if sort_key is not None and len(sort_key) > 1:
        return int(sort_key[1])
    return 0


def queued_tso_messages(federation: Any, recipient: Any | None = None) -> list[Any]:
    """Return non-retracted TSO messages sorted by ``(timestamp, sequence)``."""

    messages: list[Any] = []
    recipient_handle = _federate_handle(recipient) if recipient is not None else None
    for msg in getattr(federation, "tso_messages", ()) or ():
        if getattr(msg, "retracted", False):
            continue
        if recipient_handle is not None and getattr(msg, "recipient", None) != recipient_handle:
            continue
        messages.append(msg)
    if recipient is not None:
        for msg in getattr(recipient, "tso_message_heap", ()) or ():
            if not getattr(msg, "retracted", False):
                messages.append(msg)
    # The same object can be visible through both the legacy federation queue
    # and the newer per-federate heap; deduplicate by object identity.
    unique = {id(msg): msg for msg in messages}
    return sorted(unique.values(), key=lambda msg: (time_key(getattr(msg, "timestamp")), _message_sequence(msg)))


def compute_galt(
    federation: Any,
    federate: Any,
    *,
    include_self: bool = False,
    nrg_enabled: bool = True,
    factory: Any | None = None,
) -> TimeQueryReturn:
    """Compute GALT for a joined federate.

    GALT is undefined when no relevant time-regulating federate contributes a
    lower-bound. The caller decides how the Non-Regulated-Grant switch treats
    that undefined value for grant decisions.
    """

    candidates: list[Any] = []
    for other in getattr(federation, "federates", {}).values():
        if other is federate and not include_self:
            continue
        lower = regulating_lower_bound(other, factory=factory)
        if lower is not None:
            candidates.append(lower)
    if not candidates:
        return TimeQueryReturn(False, None)
    return TimeQueryReturn(True, time_min(candidates))


def compute_lits(
    federation: Any,
    federate: Any,
    *,
    include_galt: bool = True,
    nrg_enabled: bool = True,
    factory: Any | None = None,
) -> TimeQueryReturn:
    """Compute LITS as the least of GALT and queued incoming TSO timestamps."""

    candidates: list[Any] = []
    if include_galt:
        galt = compute_galt(federation, federate, nrg_enabled=nrg_enabled, factory=factory)
        if galt.time_is_valid and galt.time is not None:
            candidates.append(galt.time)
    candidates.extend(getattr(msg, "timestamp") for msg in queued_tso_messages(federation, federate))
    if not candidates:
        return TimeQueryReturn(False, None)
    return TimeQueryReturn(True, time_min(candidates))


def deliverable_messages_for_request(federation: Any, federate: Any, request: Any) -> tuple[Any, ...]:
    """Select queued TSO messages deliverable for a pending time request."""

    queued = queued_tso_messages(federation, federate)
    requested = _request_time(request)
    mode = _request_mode(request)
    if requested is None or mode is None:
        return ()
    if mode in {FQR, "flushQueueRequest"}:
        return tuple(queued)
    if mode in {TAR, TARA, "timeAdvanceRequest", "timeAdvanceRequestAvailable"}:
        return tuple(msg for msg in queued if time_le(getattr(msg, "timestamp"), requested))
    if mode in {NMR, NMRA, "nextMessageRequest", "nextMessageRequestAvailable"}:
        candidates = [msg for msg in queued if time_le(getattr(msg, "timestamp"), requested)]
        if not candidates:
            return ()
        earliest = getattr(candidates[0], "timestamp")
        return tuple(msg for msg in candidates if time_eq(getattr(msg, "timestamp"), earliest))
    return ()


def eligible_tso_messages(federation: Any, federate: Any, request: Any) -> list[Any]:
    """Compatibility wrapper returning deliverable TSO messages as a list."""

    return list(deliverable_messages_for_request(federation, federate, request))


def galt_allows_requested_time(
    federation: Any,
    federate: Any,
    requested_time: Any,
    mode: str,
    *,
    enforce_galt: bool = True,
    nrg_enabled: bool = True,
    factory: Any | None = None,
) -> bool:
    """Return whether the request is on the permitted side of GALT."""

    if not enforce_galt or not getattr(federate, "time_constrained_enabled", False):
        return True
    galt = compute_galt(federation, federate, nrg_enabled=nrg_enabled, factory=factory)
    if not galt.time_is_valid or galt.time is None:
        if nrg_enabled:
            return True
        return time_le(requested_time, getattr(federate, "current_time"))
    if mode in STRICT_GALT_MODES:
        return time_lt(requested_time, galt.time)
    return time_le(requested_time, galt.time)


def compute_grant_decision(
    federation: Any,
    federate: Any,
    request: Any,
    *,
    enforce_galt: bool = True,
    nrg_enabled: bool = True,
    factory: Any | None = None,
) -> TimeGrantDecision:
    """Compute if a pending advance can be granted and at what time."""

    mode = _request_mode(request)
    requested = _request_time(request)
    if mode is None or requested is None:
        return TimeGrantDecision(False, reason="no pending request")

    messages = deliverable_messages_for_request(federation, federate, request)
    if mode in {FQR, "flushQueueRequest"}:
        optimistic_candidates = [requested]
        if messages:
            optimistic_candidates.append(getattr(messages[0], "timestamp"))
        optimistic = time_min(optimistic_candidates)
        candidates = list(optimistic_candidates)
        galt = compute_galt(federation, federate, nrg_enabled=nrg_enabled, factory=factory)
        if enforce_galt and getattr(federate, "time_constrained_enabled", False) and galt.time_is_valid and galt.time is not None:
            candidates.append(galt.time)
        elif enforce_galt and getattr(federate, "time_constrained_enabled", False) and not nrg_enabled:
            candidates.append(getattr(federate, "current_time"))
        return TimeGrantDecision(True, time_min(candidates), optimistic, messages)

    if not galt_allows_requested_time(
        federation,
        federate,
        requested,
        mode,
        enforce_galt=enforce_galt,
        nrg_enabled=nrg_enabled,
        factory=factory,
    ):
        # NMR/NMRA may grant at the earliest incoming TSO message before the
        # limiting requested time/GALT boundary. Available modes are inclusive.
        if mode in {NMR, "nextMessageRequest", NMRA, "nextMessageRequestAvailable"}:
            galt = compute_galt(federation, federate, nrg_enabled=nrg_enabled, factory=factory)
            if galt.time_is_valid and galt.time is not None:
                if mode in {NMR, "nextMessageRequest"}:
                    eligible = tuple(msg for msg in messages if time_lt(getattr(msg, "timestamp"), galt.time))
                else:
                    eligible = tuple(msg for msg in messages if time_le(getattr(msg, "timestamp"), galt.time))
                if eligible:
                    ts = getattr(eligible[0], "timestamp")
                    return TimeGrantDecision(True, ts, ts, eligible)
        if mode in {TARA, "timeAdvanceRequestAvailable"}:
            galt = compute_galt(federation, federate, nrg_enabled=nrg_enabled, factory=factory)
            if galt.time_is_valid and galt.time is not None:
                eligible = tuple(msg for msg in messages if time_le(getattr(msg, "timestamp"), galt.time))
                if eligible:
                    ts = getattr(eligible[0], "timestamp")
                    return TimeGrantDecision(True, ts, ts, eligible)
        return TimeGrantDecision(False, reason="requested time is beyond GALT")

    grant_time = requested
    if mode in {NMR, NMRA, "nextMessageRequest", "nextMessageRequestAvailable"} and messages:
        grant_time = getattr(messages[0], "timestamp")
    return TimeGrantDecision(True, grant_time, grant_time, messages)


def can_grant_time_request(
    federation: Any,
    federate: Any,
    request: Any,
    *,
    enforce_galt: bool = True,
    nrg_enabled: bool = True,
    factory: Any | None = None,
    time_factory: Any | None = None,
) -> bool:
    """Compatibility predicate used by the Python RTI backend."""

    return compute_grant_decision(
        federation,
        federate,
        request,
        enforce_galt=enforce_galt,
        nrg_enabled=nrg_enabled,
        factory=time_factory if time_factory is not None else factory,
    ).can_grant


def grant_time_for_request(
    federation: Any,
    federate: Any,
    request: Any,
    messages: Sequence[Any] | None = None,
    *,
    enforce_galt: bool = True,
    nrg_enabled: bool = True,
    factory: Any | None = None,
    time_factory: Any | None = None,
) -> tuple[Any, Any | None]:
    """Return ``(grant_time, optimistic_time)`` for a grantable request."""

    decision = compute_grant_decision(
        federation,
        federate,
        request,
        enforce_galt=enforce_galt,
        nrg_enabled=nrg_enabled,
        factory=time_factory if time_factory is not None else factory,
    )
    fallback = _request_time(request)
    return (decision.grant_time if decision.grant_time is not None else fallback, decision.optimistic_time)


def valid_tso_lower_bound(federate: Any, *, factory: Any | None = None) -> Any:
    """Return the minimum timestamp that the federate may use for TSO sends."""

    request = getattr(federate, "pending_time_advance", None)
    base = _request_time(request) if request is not None else getattr(federate, "current_time")
    return add_time(base, getattr(federate, "lookahead"), factory=factory)


def scheduled_save_time_reached(federate: Any, save_time: Any, next_grant_time: Any | None = None) -> bool:
    """Return whether a constrained federate is eligible for a timed save."""

    if not getattr(federate, "time_constrained_enabled", False):
        return True
    if time_ge(getattr(federate, "current_time"), save_time):
        return True
    request = getattr(federate, "pending_time_advance", None)
    if request is None:
        return False
    grant = next_grant_time if next_grant_time is not None else _request_time(request)
    if grant is None:
        return False
    mode = _request_mode(request)
    if mode in {TAR, NMR, "timeAdvanceRequest", "nextMessageRequest"}:
        return time_ge(grant, save_time)
    return time_lt(save_time, grant)


def remove_delivered_messages(federation: Any, messages: Iterable[Any]) -> None:
    """Remove delivered/retracted messages from all RTI timestamp queues."""

    ids = {id(message) for message in list(messages)}
    try:
        federation.tso_messages[:] = [message for message in federation.tso_messages if id(message) not in ids]
    except AttributeError:
        pass
    for federate in getattr(federation, "federates", {}).values():
        heap = getattr(federate, "tso_message_heap", None)
        if heap is not None:
            federate.tso_message_heap = [message for message in heap if id(message) not in ids]
            try:
                import heapq

                heapq.heapify(federate.tso_message_heap)
            except Exception:
                pass
        try:
            for handle, message in list(federate.retraction_messages.items()):
                if id(message) in ids:
                    stored = federate.retraction_messages.pop(handle, None)
                    if stored is not None and not getattr(stored, "retracted", False):
                        delivered = getattr(federate, "delivered_retraction_messages", None)
                        if isinstance(delivered, dict):
                            delivered[handle] = stored
        except AttributeError:
            pass


__all__ = [
    "TAR",
    "TARA",
    "NMR",
    "NMRA",
    "FQR",
    "STRICT_GALT_MODES",
    "INCLUSIVE_GALT_MODES",
    "ALL_ADVANCE_MODES",
    "TimeAdvanceRequestState",
    "TimeGrantDecision",
    "time_value",
    "time_key",
    "time_lt",
    "time_le",
    "time_ge",
    "time_eq",
    "time_min",
    "add_time",
    "time_add",
    "coerce_time_like",
    "regulating_base_time",
    "regulating_lower_bound",
    "queued_tso_messages",
    "compute_galt",
    "compute_lits",
    "deliverable_messages_for_request",
    "eligible_tso_messages",
    "galt_allows_requested_time",
    "compute_grant_decision",
    "can_grant_time_request",
    "grant_time_for_request",
    "valid_tso_lower_bound",
    "scheduled_save_time_reached",
    "remove_delivered_messages",
]
