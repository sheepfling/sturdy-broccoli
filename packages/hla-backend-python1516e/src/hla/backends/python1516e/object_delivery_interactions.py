"""Interaction delivery services for object delivery."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

from hla.rti1516e.enums import OrderType
from hla.rti1516e.exceptions import InteractionClassNotPublished
from hla.rti1516e.handles import InteractionClassHandle, ParameterHandle
from hla.rti1516e.datatypes import MessageRetractionReturn

from .object_delivery_attributes import PythonRTIObjectAttributeDeliveryMixin
from .state import CallbackEvent, SupplementalReceiveInfo

if TYPE_CHECKING:
    from .state import FederateState, FederationState, PythonRTIConfig


class _ObjectInteractionDeliveryContext(Protocol):
    state: "FederateState"
    config: "PythonRTIConfig"

    def _require_joined(self) -> "FederationState": ...

    def _handle_mom_interaction(self, interaction_name: str, parameters: Mapping[ParameterHandle, bytes], tag: bytes) -> bool: ...

    def _validate_user_supplied_tag(self, federation: "FederationState", category: str, user_supplied_tag: bytes) -> None: ...

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None: ...

    def _transportation_type_for_interaction(self, interaction: InteractionClassHandle) -> Any: ...

    def _validate_tso_send_time(self, timestamp: Any) -> None: ...

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn: ...

    def _interaction_matches_subscription(
        self,
        actual_class: InteractionClassHandle,
        subscribed_class: InteractionClassHandle,
    ) -> bool: ...

    def _queue_or_deliver_tso(
        self,
        federation: "FederationState",
        target: "FederateState",
        timestamp: Any | None,
        event: CallbackEvent,
        *,
        retraction_handle: Any,
        producing_federate: Any,
        post_deliver_cleanup: Any | None = None,
    ) -> None: ...

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...

    def _refresh_mom_federate_object(self, federation: "FederationState", federate: "FederateState", *, notify: bool = True) -> None: ...

    def _process_time_advances(self, federation: "FederationState") -> None: ...


if TYPE_CHECKING:
    class _ObjectInteractionDeliveryMixinBase(PythonRTIObjectAttributeDeliveryMixin, _ObjectInteractionDeliveryContext):
        pass
else:
    class _ObjectInteractionDeliveryMixinBase(PythonRTIObjectAttributeDeliveryMixin):
        pass


class PythonRTIObjectInteractionDeliveryMixin(_ObjectInteractionDeliveryMixinBase):
    """Interaction send services."""

    def _svc_sendInteraction(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: Mapping[ParameterHandle, bytes],
        userSuppliedTag: bytes,
        *unused: Any,
    ) -> MessageRetractionReturn | None:
        federation = self._require_joined()
        interaction_def = self.engine.interaction_for_handle(theInteraction)
        params = {handle: bytes(value) for handle, value in dict(theParameters).items()}
        if self._handle_mom_interaction(interaction_def.name, params, bytes(userSuppliedTag)):
            return None
        if (
            self.config.strict_interaction_publication
            and theInteraction not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(theInteraction))
        for parameter in params:
            self.engine.parameter_name(theInteraction, parameter)
        self._validate_user_supplied_tag(federation, "sendReceiveTag", bytes(userSuppliedTag))

        timestamp = self._extract_timestamp(tuple(unused))
        preferred = self.state.interaction_order_overrides.get(
            theInteraction,
            OrderType.TIMESTAMP
            if timestamp is not None
            else self.config.default_preferred_order_type,
        )
        sent_tso = bool(
            timestamp is not None
            and self.state.time_regulation_enabled
            and preferred is OrderType.TIMESTAMP
        )
        transport = self._transportation_type_for_interaction(theInteraction)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.interactions_sent += 1

        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if any(
                self._interaction_matches_subscription(theInteraction, subscribed)
                for subscribed in federate.subscribed_interactions
            ):
                info = SupplementalReceiveInfo(producing_federate=self.state.handle)
                if sent_tso and federate.time_constrained_enabled:
                    assert retraction is not None
                    event = CallbackEvent(
                        "receiveInteraction",
                        (
                            theInteraction,
                            params,
                            bytes(userSuppliedTag),
                            OrderType.TIMESTAMP,
                            transport,
                            timestamp,
                            OrderType.TIMESTAMP,
                            retraction.handle,
                            info,
                        ),
                    )
                    self._queue_or_deliver_tso(
                        federation,
                        federate,
                        timestamp,
                        event,
                        retraction_handle=retraction.handle,
                        producing_federate=self.state.handle,
                    )
                else:
                    event = CallbackEvent(
                        "receiveInteraction",
                        (
                            theInteraction,
                            params,
                            bytes(userSuppliedTag),
                            OrderType.RECEIVE,
                            transport,
                            info,
                        ),
                    )
                    self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction
