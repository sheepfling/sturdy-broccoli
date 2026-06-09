"""Time-queue, delivery, and grant coordination helpers."""
from __future__ import annotations

import heapq
from typing import Any

from hla2010 import time_management as tm
from hla2010.enums import OrderType
from hla2010.handles import FederateHandle, MessageRetractionHandle
from hla2010.types import MessageRetractionReturn, TimeQueryReturn
from .state import (
    CallbackEvent,
    FederateState,
    FederationState,
    QueuedTimeMessage,
    TimeAdvanceRequestState,
    TimedMessage,
)


def _time_value(value: Any) -> float | int:
    return tm.time_value(value)


def _time_key(value: Any) -> float:
    return tm.time_key(value)


def _time_lt(left: Any, right: Any) -> bool:
    return tm.time_lt(left, right)


class PythonRTITimeQueueMixin:
    """Per-federate TSO/RO queue and grant coordination helpers."""

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
        if request.mode in {"TAR", "NMR"} and getattr(federate.lookahead, "is_zero", lambda: False)():
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

    def _queue_or_deliver_message(
        self,
        target: FederateState,
        callback: CallbackEvent,
        *,
        sent_order: OrderType,
        timestamp: Any | None,
        sender: FederateHandle | None,
        service_name: str,
        retraction_handle: MessageRetractionHandle | None = None,
        post_deliver_cleanup: Any | None = None,
    ) -> None:
        federation = target.federation
        if federation is None:
            return
        received_order = (
            OrderType.TIMESTAMP
            if target.time_constrained_enabled and sent_order is OrderType.TIMESTAMP
            else OrderType.RECEIVE
        )
        if received_order is OrderType.TIMESTAMP and timestamp is not None:
            msg = QueuedTimeMessage(
                sort_key=(_time_value(timestamp), self._next_message_sequence(federation)),
                timestamp=timestamp,
                sent_order=sent_order,
                received_order=received_order,
                callback=callback,
                retraction_handle=retraction_handle,
                sender=sender,
                service_name=service_name,
                post_deliver_cleanup=post_deliver_cleanup,
            )
            heapq.heappush(target.tso_message_heap, msg)
            if retraction_handle is not None:
                target.retraction_messages[retraction_handle] = msg
            self._attempt_time_advance(target)
            return
        msg = QueuedTimeMessage(
            sort_key=(0, self._next_message_sequence(federation)),
            timestamp=timestamp,
            sent_order=sent_order,
            received_order=OrderType.RECEIVE,
            callback=callback,
            retraction_handle=retraction_handle,
            sender=sender,
            service_name=service_name,
            post_deliver_cleanup=post_deliver_cleanup,
        )
        if (
            target.time_constrained_enabled
            and not target.asynchronous_delivery_enabled
            and not target.time_advancing
        ):
            target.ro_message_queue.append(msg)
        else:
            self._deliver_time_message(target, msg)

    def _deliver_time_message(self, target: FederateState, msg: QueuedTimeMessage) -> None:
        if msg.retracted:
            return
        name = msg.callback.method_name
        if name == "reflectAttributeValues":
            target.reflections_received += 1
            target.object_instances_reflected += 1
        elif name == "receiveInteraction":
            target.interactions_received += 1
        elif name == "removeObjectInstance":
            target.object_instances_removed += 1
        elif name == "discoverObjectInstance":
            target.object_instances_discovered += 1
        self._deliver(target, name, *msg.callback.args)
        if msg.post_deliver_cleanup is not None:
            msg.post_deliver_cleanup()

    def _drain_ro_messages(self, federate: FederateState) -> None:
        while federate.ro_message_queue:
            self._deliver_time_message(federate, federate.ro_message_queue.popleft())

    def _take_eligible_tso_messages(
        self,
        federate: FederateState,
        requested: Any,
        kind: str,
    ) -> list[QueuedTimeMessage]:
        if not federate.tso_message_heap:
            return []
        active = [msg for msg in federate.tso_message_heap if not msg.retracted]
        if not active:
            federate.tso_message_heap.clear()
            return []
        queue = tm.TSOMessageQueue(active)
        if kind == "flushQueueRequest":
            eligible = list(queue.list_deliverable_through(recipient=federate, boundary=requested))
        elif kind in {"nextMessageRequest", "nextMessageRequestAvailable"}:
            eligible = list(
                queue.list_deliverable_through(
                    recipient=federate,
                    boundary=requested,
                    earliest_only=True,
                )
            )
        else:
            eligible = list(queue.list_deliverable_through(recipient=federate, boundary=requested))
        eligible_ids = {id(msg) for msg in eligible}
        federate.tso_message_heap = [msg for msg in active if id(msg) not in eligible_ids]
        heapq.heapify(federate.tso_message_heap)
        return sorted(eligible, key=lambda m: m.sort_key)

    def _attempt_time_advance(self, federate: FederateState) -> None:
        federation = federate.federation
        if (
            federation is None
            or not federate.time_advancing
            or federate.requested_time is None
            or federate.time_advance_kind is None
        ):
            return
        requested = federate.requested_time
        kind = federate.time_advance_kind
        old_time = federate.current_time
        if not self._galt_allows_grant(federation, federate, requested, kind):
            return
        self._drain_ro_messages(federate)
        delivered = self._take_eligible_tso_messages(federate, requested, kind)
        grant_time = requested
        if delivered and kind in {"nextMessageRequest", "nextMessageRequestAvailable", "flushQueueRequest"}:
            earliest = min((msg.timestamp for msg in delivered), key=_time_value)
            if self._time_lt(earliest, requested):
                grant_time = earliest
        if kind == "flushQueueRequest":
            delivered = [msg for msg in delivered if self._time_le(msg.timestamp, grant_time)]
        for msg in delivered:
            self._deliver_time_message(federate, msg)
        federate.current_time = grant_time
        federate.time_advancing = False
        federate.last_time_advance_kind = kind
        federate.time_advance_kind = None
        federate.requested_time = None
        if kind in {"timeAdvanceRequest", "nextMessageRequest"} and getattr(
            federate.lookahead,
            "is_zero",
            lambda: False,
        )():
            federate.zero_lookahead_tarnmr_restriction = True
        elif self._time_lt(old_time, grant_time):
            federate.zero_lookahead_tarnmr_restriction = False
        self._deliver(federate, "timeAdvanceGrant", grant_time)
        self._refresh_mom_attribute_values(federation)

    def _attempt_all_time_advances(self, federation: FederationState) -> None:
        for federate in list(federation.federates.values()):
            self._attempt_time_advance(federate)
