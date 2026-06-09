"""Public time-management services and validation helpers."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from hla2010 import time_management as tm
from hla2010.enums import OrderType
from hla2010.exceptions import (
    InTimeAdvancingState,
    InteractionClassNotPublished,
    InvalidInteractionClassHandle,
    InvalidLogicalTime,
    InvalidLookahead,
    InvalidMessageRetractionHandle,
    InvalidOrderType,
    LogicalTimeAlreadyPassed,
    MessageCanNoLongerBeRetracted,
    RequestForTimeConstrainedPending,
    RequestForTimeRegulationPending,
    RestoreInProgress,
    SaveInProgress,
    TimeConstrainedAlreadyEnabled,
    TimeConstrainedIsNotEnabled,
    TimeRegulationAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from hla2010.handles import (
    AttributeHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)
from hla2010.types import TimeQueryReturn
from .state import TimeAdvanceRequestState

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, FederationState, ObjectInstance, PythonRTIConfig


class _TimeServicesContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: "FederateState"
    config: "PythonRTIConfig"

    def _require_joined(self) -> "FederationState": ...

    def _coerce_time(self, value: Any) -> Any: ...

    def _coerce_interval(self, value: Any) -> Any: ...

    def _time_factory(self) -> Any: ...

    def _refresh_mom_federate_object(self, federation: "FederationState", federate: "FederateState", *, notify: bool = False) -> None: ...

    def _process_time_advances(self, federation: "FederationState") -> None: ...

    def _deliver(self, federate: "FederateState", method_name: str, *args: Any, **kwargs: Any) -> Any: ...

    def _find_object(self, theObject: "ObjectInstanceHandle") -> tuple["FederationState", "ObjectInstance"]: ...

    def _compute_galt(self, federation: "FederationState", federate: "FederateState") -> Any: ...

    def _compute_lits(self, federation: "FederationState", federate: "FederateState") -> Any: ...

if TYPE_CHECKING:
    class _TimeServicesMixinBase(_TimeServicesContext):
        pass
else:
    class _TimeServicesMixinBase:
        pass


def _time_value(value: Any) -> float | int:
    return tm.time_value(value)


class PythonRTITimeServicesMixin(_TimeServicesMixinBase):
    """Public time-management services and supporting validators."""

    def _request_time_advance(self, mode: str, theTime: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.request_for_time_regulation_pending:
            raise RequestForTimeRegulationPending("A request to enable time regulation is still pending")
        if self.state.request_for_time_constrained_pending:
            raise RequestForTimeConstrainedPending("A request to enable time constrained is still pending")
        if self.state.time_advancing:
            raise InTimeAdvancingState("Federate already has a pending time advance request")
        requested = self._coerce_time(theTime)
        if self._time_lt(requested, self.state.current_time):
            raise LogicalTimeAlreadyPassed(repr(theTime))
        self.state.time_advancing = True
        self.state.pending_time_advance = TimeAdvanceRequestState(mode, requested)
        self.state.requested_time = requested
        self.state.time_advance_kind = mode
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _time_add(self, time_value: Any, interval: Any) -> Any:
        return tm.time_add(time_value, interval, self._time_factory())

    def _time_lt(self, a: Any, b: Any) -> bool:
        return _time_value(a) < _time_value(b)

    def _time_le(self, a: Any, b: Any) -> bool:
        return _time_value(a) <= _time_value(b)

    def _validate_time_advance_request(self, requested_time: Any) -> Any:
        requested = self._coerce_time(requested_time)
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("A time advance request is already outstanding")
        if self._time_lt(requested, self.state.current_time):
            raise LogicalTimeAlreadyPassed(repr(requested))
        return requested

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None:
        if not args:
            return None
        skip_types = (
            OrderType,
            AttributeHandle,
            ObjectInstanceHandle,
            InteractionClassHandle,
            MessageRetractionHandle,
            TransportationTypeHandle,
        )
        for arg in args:
            if arg is None or isinstance(arg, skip_types):
                continue
            try:
                return self._coerce_time(arg)
            except Exception:
                continue
        return None

    def _sent_order_type(self, preferred: OrderType, timestamp: Any | None) -> OrderType:
        if (
            preferred is OrderType.TIMESTAMP
            and timestamp is not None
            and self.state.time_regulation_enabled
        ):
            return OrderType.TIMESTAMP
        return OrderType.RECEIVE

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled(
                "Timestamp-order messages require time regulation to be enabled"
            )
        federation = self._require_joined()
        lower_bound = tm.valid_tso_lower_bound(self.state, factory=federation.time_factory)
        if tm.time_lt(timestamp, lower_bound):
            raise InvalidLogicalTime(
                f"TSO timestamp {timestamp!r} is earlier than logical time/lookahead bound {lower_bound!r}"
            )
        if (
            self.state.zero_lookahead_tarnmr_restriction
            and getattr(self.state.lookahead, "is_zero", lambda: False)()
            and tm.time_le(timestamp, self.state.current_time)
        ):
            raise InvalidLogicalTime(
                "Zero-lookahead TAR/NMR restriction forbids TSO timestamps <= current logical time"
            )

    def _make_retraction_handle(self, sent_order: OrderType) -> MessageRetractionHandle | None:
        if sent_order is not OrderType.TIMESTAMP:
            return None
        return self.engine._alloc(MessageRetractionHandle)

    def _svc_enableTimeRegulation(self, theLookahead: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("Cannot enable time regulation while time advancing")
        if self.state.request_for_time_regulation_pending:
            raise RequestForTimeRegulationPending("A request to enable time regulation is still pending")
        if self.state.time_regulation_enabled:
            raise TimeRegulationAlreadyEnabled("Time regulation is already enabled")
        lookahead = self._coerce_interval(theLookahead)
        if _time_value(lookahead) < 0:
            raise InvalidLookahead("Lookahead must be non-negative")
        self.state.lookahead = lookahead
        self.state.request_for_time_regulation_pending = True
        try:
            self._deliver(self.state, "timeRegulationEnabled", self.state.current_time)
            self.state.time_regulation_enabled = True
        finally:
            self.state.request_for_time_regulation_pending = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_disableTimeRegulation(self) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        self.state.time_regulation_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_enableTimeConstrained(self) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("Cannot enable time constrained while time advancing")
        if self.state.request_for_time_constrained_pending:
            raise RequestForTimeConstrainedPending("A request to enable time constrained is still pending")
        if self.state.time_constrained_enabled:
            raise TimeConstrainedAlreadyEnabled("Time constrained is already enabled")
        self.state.request_for_time_constrained_pending = True
        try:
            self._deliver(self.state, "timeConstrainedEnabled", self.state.current_time)
            self.state.time_constrained_enabled = True
        finally:
            self.state.request_for_time_constrained_pending = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_disableTimeConstrained(self) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_constrained_enabled:
            raise TimeConstrainedIsNotEnabled("Time constrained is not enabled")
        self.state.time_constrained_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_timeAdvanceRequest(self, theTime: Any) -> None:
        self._request_time_advance("TAR", theTime)

    def _svc_timeAdvanceRequestAvailable(self, theTime: Any) -> None:
        self._request_time_advance("TARA", theTime)

    def _svc_nextMessageRequest(self, theTime: Any) -> None:
        self._request_time_advance("NMR", theTime)

    def _svc_nextMessageRequestAvailable(self, theTime: Any) -> None:
        self._request_time_advance("NMRA", theTime)

    def _svc_flushQueueRequest(self, theTime: Any) -> None:
        self._request_time_advance("FQR", theTime)

    def _svc_queryLogicalTime(self) -> Any:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self.state.current_time

    def _svc_queryGALT(self) -> TimeQueryReturn:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self._compute_galt(federation, self.state)

    def _svc_queryLITS(self) -> TimeQueryReturn:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self._compute_lits(federation, self.state)

    def _svc_queryLookahead(self) -> Any:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        return self.state.lookahead

    def _svc_modifyLookahead(self, theLookahead: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("Cannot modify lookahead while time advancing")
        lookahead = self._coerce_interval(theLookahead)
        if _time_value(lookahead) < 0:
            raise InvalidLookahead("Lookahead must be non-negative")
        self.state.lookahead = lookahead
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_retract(self, theHandle: MessageRetractionHandle) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        if not isinstance(theHandle, MessageRetractionHandle):
            raise InvalidMessageRetractionHandle(repr(theHandle))
        for federate in list(federation.federates.values()):
            message = federate.retraction_messages.get(theHandle)
            delivered = False
            if message is None:
                message = federate.delivered_retraction_messages.get(theHandle)
                delivered = message is not None
            if message is not None and not message.retracted:
                queued = (
                    not delivered
                    and (message in federate.tso_message_heap or message in federate.ro_message_queue)
                )
                message.retracted = True
                federate.retraction_messages.pop(theHandle, None)
                federate.delivered_retraction_messages.pop(theHandle, None)
                federate.retractable_messages[theHandle] = False
                self.state.retractable_messages[theHandle] = False
                if not queued:
                    self._deliver(federate, "requestRetraction", theHandle)
                return
        for message in list(federation.tso_messages):
            if message.retraction_handle == theHandle and not message.retracted:
                message.retracted = True
                try:
                    federation.tso_messages.remove(message)
                except ValueError:
                    pass
                self.state.retractable_messages[theHandle] = False
                return
        raise MessageCanNoLongerBeRetracted(repr(theHandle))

    def _svc_changeAttributeOrderType(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        theType: OrderType,
    ) -> None:
        federation, instance = self._find_object(theObject)
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not isinstance(theType, OrderType):
            raise InvalidOrderType(repr(theType))
        attrs = set(theAttributes)
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
        for attr in attrs:
            if instance.attribute_owners.get(attr, instance.owner) != self.state.handle:
                from hla2010.exceptions import AttributeNotOwned

                raise AttributeNotOwned(repr(theObject))
        for attr in attrs:
            self.state.attribute_order_overrides[(theObject, attr)] = theType

    def _svc_changeInteractionOrderType(
        self,
        theClass: InteractionClassHandle,
        theType: OrderType,
    ) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        try:
            self.engine.interaction_for_handle(theClass)
        except InvalidInteractionClassHandle as exc:
            from hla2010.exceptions import InteractionClassNotDefined

            raise InteractionClassNotDefined(repr(theClass)) from exc
        if (
            self.config.strict_interaction_publication
            and theClass not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(theClass))
        if not isinstance(theType, OrderType):
            raise InvalidOrderType(repr(theType))
        self.state.interaction_order_overrides[theClass] = theType
