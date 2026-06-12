"""Interaction delivery services for object delivery."""

from __future__ import annotations

from typing import Any, Mapping

from hla2010.enums import OrderType
from hla2010.exceptions import InteractionClassNotPublished
from hla2010.handles import InteractionClassHandle, ParameterHandle
from hla2010.types import MessageRetractionReturn

from .object_delivery_attributes import PythonRTIObjectAttributeDeliveryMixin
from .state import CallbackEvent, SupplementalReceiveInfo


class PythonRTIObjectInteractionDeliveryMixin(PythonRTIObjectAttributeDeliveryMixin):
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
