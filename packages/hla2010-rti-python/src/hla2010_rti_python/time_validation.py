"""Core time-management validation and coercion helpers."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from hla2010.enums import OrderType
from hla2010.exceptions import (
    InTimeAdvancingState,
    InvalidLogicalTime,
    LogicalTimeAlreadyPassed,
    RequestForTimeConstrainedPending,
    RequestForTimeRegulationPending,
    RestoreInProgress,
    SaveInProgress,
    TimeRegulationIsNotEnabled,
)
from hla2010.handles import (
    AttributeHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)
from hla2010.types import MessageRetractionReturn
from hla2010_rti_backend_common import time_management as tm

from .state import TimeAdvanceRequestState

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, FederationState, ObjectInstance, PythonRTIConfig


class _TimeValidationContext(Protocol):
    engine: InMemoryRTIEngine
    state: FederateState
    config: PythonRTIConfig

    def _require_joined(self) -> FederationState: ...

    def _coerce_time(self, value: Any) -> Any: ...

    def _coerce_interval(self, value: Any) -> Any: ...

    def _time_factory(self) -> Any: ...

    def _refresh_mom_federate_object(
        self,
        federation: FederationState,
        federate: FederateState,
        *,
        notify: bool = False,
    ) -> None: ...

    def _process_time_advances(self, federation: FederationState) -> None: ...

    def _deliver(
        self, federate: FederateState, method_name: str, *args: Any, **kwargs: Any
    ) -> Any: ...

    def _find_object(
        self, theObject: ObjectInstanceHandle
    ) -> tuple[FederationState, ObjectInstance]: ...

    def _compute_galt(self, federation: FederationState, federate: FederateState) -> Any: ...

    def _compute_lits(self, federation: FederationState, federate: FederateState) -> Any: ...


if TYPE_CHECKING:
    class _TimeValidationMixinBase(_TimeValidationContext):
        pass
else:
    class _TimeValidationMixinBase:
        pass


def _time_value(value: Any) -> float | int:
    return tm.time_value(value)


class PythonRTITimeValidationMixin(_TimeValidationMixinBase):
    """Core time-management validators and request helpers."""

    def _request_time_advance(self, mode: str, theTime: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.request_for_time_regulation_pending:
            raise RequestForTimeRegulationPending(
                "A request to enable time regulation is still pending"
            )
        if self.state.request_for_time_constrained_pending:
            raise RequestForTimeConstrainedPending(
                "A request to enable time constrained is still pending"
            )
        if self.state.time_advancing:
            raise InTimeAdvancingState(
                "Federate already has a pending time advance request"
            )
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

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn:
        handle = self.engine._alloc(MessageRetractionHandle)
        self.state.retractable_messages[handle] = True
        return MessageRetractionReturn(handle, timestamp)
