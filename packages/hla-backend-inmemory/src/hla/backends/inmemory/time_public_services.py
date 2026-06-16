"""Public time-management service entrypoints."""
from __future__ import annotations

from typing import Any, Iterable

from hla.rti1516e.enums import OrderType
from hla.rti1516e.exceptions import (
    InTimeAdvancingState,
    InteractionClassNotPublished,
    InvalidInteractionClassHandle,
    InvalidLookahead,
    InvalidMessageRetractionHandle,
    InvalidOrderType,
    MessageCanNoLongerBeRetracted,
    RestoreInProgress,
    SaveInProgress,
    TimeConstrainedAlreadyEnabled,
    TimeConstrainedIsNotEnabled,
    TimeRegulationAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from hla.rti1516e.handles import (
    AttributeHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectInstanceHandle,
)
from hla.rti1516e.types import TimeQueryReturn

from .time_validation import PythonRTITimeValidationMixin, _time_value


class PythonRTITimePublicServicesMixin(PythonRTITimeValidationMixin):
    """Public time-management service methods."""

    def _svc_enableTimeRegulation(self, theLookahead: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState(
                "Cannot enable time regulation while time advancing"
            )
        if self.state.request_for_time_regulation_pending:
            from hla.rti1516e.exceptions import RequestForTimeRegulationPending

            raise RequestForTimeRegulationPending(
                "A request to enable time regulation is still pending"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState(
                "Cannot enable time constrained while time advancing"
            )
        if self.state.request_for_time_constrained_pending:
            from hla.rti1516e.exceptions import RequestForTimeConstrainedPending

            raise RequestForTimeConstrainedPending(
                "A request to enable time constrained is still pending"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self.state.current_time

    def _svc_queryGALT(self) -> TimeQueryReturn:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self._compute_galt(federation, self.state)

    def _svc_queryLITS(self) -> TimeQueryReturn:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        return self._compute_lits(federation, self.state)

    def _svc_queryLookahead(self) -> Any:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        return self.state.lookahead

    def _svc_modifyLookahead(self, theLookahead: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if not isinstance(theType, OrderType):
            raise InvalidOrderType(repr(theType))
        attrs = set(theAttributes)
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
        for attr in attrs:
            if instance.attribute_owners.get(attr, instance.owner) != self.state.handle:
                from hla.rti1516e.exceptions import AttributeNotOwned

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
            raise RestoreInProgress(
                f"Federation restore is in progress: {federation.restore_label}"
            )
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        try:
            self.engine.interaction_for_handle(theClass)
        except InvalidInteractionClassHandle as exc:
            from hla.rti1516e.exceptions import InteractionClassNotDefined

            raise InteractionClassNotDefined(repr(theClass)) from exc
        if (
            self.config.strict_interaction_publication
            and theClass not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(theClass))
        if not isinstance(theType, OrderType):
            raise InvalidOrderType(repr(theType))
        self.state.interaction_order_overrides[theClass] = theType
