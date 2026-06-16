"""Queued message delivery and local time-advance runtime helpers."""
from __future__ import annotations

import heapq
from typing import Any

from hla.rti1516e.enums import OrderType
from hla.rti1516e.handles import FederateHandle, MessageRetractionHandle
from hla.backends.common import time_management as tm

from .state import CallbackEvent, FederateState, FederationState, QueuedTimeMessage
from .time_queue_grants import PythonRTITimeQueueGrantMixin, _time_lt, _time_value


class PythonRTITimeQueueDeliveryMixin(PythonRTITimeQueueGrantMixin):
    """Queued message delivery, draining, and local grant-attempt helpers."""

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
                sort_key=(tm.time_key(timestamp), self._next_message_sequence(federation)),
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
            eligible = list(
                queue.list_deliverable_through(recipient=federate, boundary=requested)
            )
        elif kind in {"nextMessageRequest", "nextMessageRequestAvailable"}:
            eligible = list(
                queue.list_deliverable_through(
                    recipient=federate,
                    boundary=requested,
                    earliest_only=True,
                )
            )
        else:
            eligible = list(
                queue.list_deliverable_through(recipient=federate, boundary=requested)
            )
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
        if delivered and kind in {
            "nextMessageRequest",
            "nextMessageRequestAvailable",
            "flushQueueRequest",
        }:
            earliest = min((msg.timestamp for msg in delivered), key=_time_value)
            if _time_lt(earliest, requested):
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
            federate.lookahead, "is_zero", lambda: False
        )():
            federate.zero_lookahead_tarnmr_restriction = True
        elif _time_lt(old_time, grant_time):
            federate.zero_lookahead_tarnmr_restriction = False
        self._deliver(federate, "timeAdvanceGrant", grant_time)
        self._refresh_mom_attribute_values(federation)

    def _attempt_all_time_advances(self, federation: FederationState) -> None:
        for federate in list(federation.federates.values()):
            self._attempt_time_advance(federate)
