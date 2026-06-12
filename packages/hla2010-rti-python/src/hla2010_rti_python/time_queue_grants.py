"""Grant, GALT, and eligibility helpers for time-queue processing."""
from __future__ import annotations

from typing import Any

from hla2010.enums import OrderType
from hla2010.handles import FederateHandle, MessageRetractionHandle
from hla2010.types import MessageRetractionReturn, TimeQueryReturn
from hla2010_rti_backend_common import time_management as tm

from .state import CallbackEvent, FederateState, FederationState, TimeAdvanceRequestState, TimedMessage


def _time_value(value: Any) -> float | int:
    return tm.time_value(value)


def _time_key(value: Any) -> float:
    return tm.time_key(value)


def _time_lt(left: Any, right: Any) -> bool:
    return tm.time_lt(left, right)


class PythonRTITimeQueueGrantMixin:
    """Grant and eligibility helpers for queued time messages."""

    def _queued_tso_for(
        self,
        federation: FederationState,
        recipient: FederateState,
    ) -> list[TimedMessage]:
        if recipient.handle is None:
            return []
        return sorted(
            (
                msg
                for msg in federation.tso_messages
                if msg.recipient == recipient.handle and not msg.retracted
            ),
            key=lambda msg: (_time_key(msg.timestamp), msg.sequence),
        )

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn:
        handle = self.engine._alloc(MessageRetractionHandle)
        self.state.retractable_messages[handle] = True
        return MessageRetractionReturn(handle, timestamp)

    def _queue_or_deliver_tso(
        self,
        federation: FederationState,
        target: FederateState,
        timestamp: Any | None,
        event: CallbackEvent,
        *,
        retraction_handle: MessageRetractionHandle | None,
        producing_federate: FederateHandle | None,
        post_deliver_cleanup: Any | None = None,
    ) -> None:
        sent_order = OrderType.TIMESTAMP if timestamp is not None else OrderType.RECEIVE
        self._queue_or_deliver_message(
            target,
            event,
            sent_order=sent_order,
            timestamp=timestamp,
            sender=producing_federate,
            service_name=event.method_name,
            retraction_handle=retraction_handle,
            post_deliver_cleanup=post_deliver_cleanup,
        )

    def _eligible_tso_messages(
        self,
        federation: FederationState,
        federate: FederateState,
        request: TimeAdvanceRequestState,
    ) -> list[TimedMessage]:
        return tm.eligible_tso_messages(
            federation,
            federate,
            tm.TimeAdvanceRequestState(request.mode, request.requested_time),
        )

    def _can_grant_time_request(
        self,
        federation: FederationState,
        federate: FederateState,
        request: TimeAdvanceRequestState,
    ) -> bool:
        return tm.can_grant_time_request(
            federation,
            federate,
            tm.TimeAdvanceRequestState(request.mode, request.requested_time),
            enforce_galt=self.config.enforce_galt,
            factory=federation.time_factory,
        )

    def _grant_time_request(
        self,
        federation: FederationState,
        federate: FederateState,
        request: TimeAdvanceRequestState,
    ) -> None:
        normalized_request = tm.TimeAdvanceRequestState(request.mode, request.requested_time)
        decision = tm.compute_grant_decision(
            federation,
            federate,
            normalized_request,
            enforce_galt=self.config.enforce_galt,
            factory=federation.time_factory,
        )
        messages = list(decision.deliverable_messages)
        grant_time = decision.grant_time if decision.grant_time is not None else request.requested_time
        optimistic_time = decision.optimistic_time
        tm.remove_delivered_messages(federation, messages)
        for message in messages:
            if not message.retracted:
                event = getattr(message, "event", getattr(message, "callback", None))
                if event is not None:
                    if hasattr(message, "callback"):
                        self._deliver_time_message(federate, message)
                    else:
                        self._deliver(federate, event.method_name, *event.args)

        old_time = federate.current_time
        federate.current_time = grant_time
        federate.last_optimistic_logical_time = optimistic_time
        federate.time_advancing = False
        federate.pending_time_advance = None
        federate.requested_time = None
        federate.last_time_advance_kind = request.mode
        federate.time_advance_kind = None
        federate.last_grant_mode = request.mode
        if request.mode in {"TAR", "NMR"} and getattr(
            federate.lookahead, "is_zero", lambda: False
        )():
            federate.zero_lookahead_tarnmr_restriction = True
        elif _time_lt(old_time, grant_time):
            federate.zero_lookahead_tarnmr_restriction = False
        self._deliver(federate, "timeAdvanceGrant", grant_time)
        self._refresh_mom_federate_object(federation, federate, notify=True)
        self._process_scheduled_saves(federation)

    def _process_time_advances(self, federation: FederationState) -> None:
        progressed = True
        while progressed:
            progressed = False
            for federate in list(federation.federates.values()):
                request = federate.pending_time_advance
                if request is None:
                    continue
                if self._can_grant_time_request(federation, federate, request):
                    self._grant_time_request(federation, federate, request)
                    progressed = True
        self._process_scheduled_saves(federation)
        self._refresh_mom_federation_object(federation, notify=True)

    def _next_message_sequence(self, federation: FederationState) -> int:
        seq = federation.next_message_sequence
        federation.next_message_sequence += 1
        return seq

    def _compute_galt(
        self,
        federation: FederationState,
        federate: FederateState,
    ) -> TimeQueryReturn:
        return tm.compute_galt(federation, federate, factory=federation.time_factory)

    def _compute_lits(
        self,
        federation: FederationState,
        federate: FederateState,
    ) -> TimeQueryReturn:
        return tm.compute_lits(federation, federate, factory=federation.time_factory)

    def _galt_allows_grant(
        self,
        federation: FederationState,
        federate: FederateState,
        requested_time: Any,
        kind: str,
    ) -> bool:
        if not self.config.enforce_galt or not federate.time_constrained_enabled:
            return True
        request = tm.TimeAdvanceRequestState(kind, requested_time)
        return tm.can_grant_time_request(
            federation,
            federate,
            request,
            enforce_galt=self.config.enforce_galt,
            factory=federation.time_factory,
        )
