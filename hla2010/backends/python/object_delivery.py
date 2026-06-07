"""Object update, delete, interaction, and transport helpers."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from ...enums import OrderType
from ...exceptions import (
    AttributeNotOwned,
    AttributeNotPublished,
    DeletePrivilegeNotHeld,
    InteractionClassNotPublished,
    ObjectInstanceNotKnown,
)
from ...handles import (
    AttributeHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from ...types import MessageRetractionReturn
from .state import (
    CallbackEvent,
    ObjectInstance,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
)


class PythonRTIObjectDeliveryMixin:
    """Object update/delete delivery and interaction/transport services."""

    def _svc_updateAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Mapping[AttributeHandle, bytes],
        userSuppliedTag: bytes,
        *unused: Any,
    ) -> MessageRetractionReturn | None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.config.strict_object_publication:
            published = self.state.published_objects.get(instance.class_handle, set())
            if not set(theAttributes).issubset(published):
                raise AttributeNotPublished("Attribute update includes unpublished attributes")
        if any(
            instance.attribute_owners.get(handle, instance.owner) != self.state.handle
            for handle in theAttributes
        ):
            raise AttributeNotOwned(repr(theObject))

        timestamp = self._extract_timestamp(tuple(unused))
        attrs = {handle: bytes(value) for handle, value in dict(theAttributes).items()}
        preferred_orders = [
            self.state.attribute_order_overrides.get(
                (theObject, handle),
                OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type,
            )
            for handle in attrs
        ]
        sent_tso = bool(
            timestamp is not None
            and self.state.time_regulation_enabled
            and any(order is OrderType.TIMESTAMP for order in preferred_orders)
        )
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None

        instance.attributes.update(attrs)
        for handle in attrs:
            instance.attribute_owners.setdefault(handle, self.state.handle)
        self.state.updates_sent += 1
        self.state.object_instances_updated += 1

        assert self.state.handle is not None
        update_region_map = {
            attr: set(regions)
            for attr, regions in self.state.update_regions.get(theObject, {}).items()
        }
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            reflected = self._attribute_subscription_intersection(
                federate,
                instance.class_handle,
                attrs,
                instance,
                update_region_map,
            )
            if not reflected:
                continue
            sent_regions = (
                frozenset().union(*(instance.update_regions.get(attr, set()) for attr in reflected))
                if reflected
                else frozenset()
            )
            info = SupplementalReflectInfo(
                producing_federate=self.state.handle,
                sent_regions=frozenset(sent_regions),
            )
            if sent_tso and federate.time_constrained_enabled:
                assert retraction is not None
                event = CallbackEvent(
                    "reflectAttributeValues",
                    (
                        instance.handle,
                        reflected,
                        bytes(userSuppliedTag),
                        OrderType.TIMESTAMP,
                        self.engine.transportation_reliable,
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
                    "reflectAttributeValues",
                    (
                        instance.handle,
                        reflected,
                        bytes(userSuppliedTag),
                        OrderType.RECEIVE,
                        self.engine.transportation_reliable,
                        info,
                    ),
                )
                self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_requestAttributeValueUpdate(
        self,
        target: Any,
        attributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes = b"",
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(attributes)
        tag = bytes(userSuppliedTag)

        def deliver(instance: ObjectInstance) -> None:
            if self._is_mom_object_instance(federation, instance):
                self._deliver_mom_attribute_update(instance, attrs, tag)
                return
            owner = federation.federates.get(instance.owner)
            if owner is not None:
                self._deliver(owner, "provideAttributeValueUpdate", instance.handle, attrs, tag)

        if isinstance(target, ObjectInstanceHandle):
            try:
                deliver(federation.objects[target])
                return
            except KeyError as exc:
                raise ObjectInstanceNotKnown(repr(target)) from exc

        if isinstance(target, ObjectClassHandle):
            self.engine.object_class_for_handle(target)
            for instance in list(federation.objects.values()):
                if self._object_matches_subscription(instance.class_handle, target):
                    deliver(instance)
            return

        raise ObjectInstanceNotKnown(repr(target))

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

        timestamp = self._extract_timestamp(tuple(unused))
        preferred = self.state.interaction_order_overrides.get(
            theInteraction,
            OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type,
        )
        sent_tso = bool(
            timestamp is not None
            and self.state.time_regulation_enabled
            and preferred is OrderType.TIMESTAMP
        )
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
                            self.engine.transportation_reliable,
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
                            self.engine.transportation_reliable,
                            info,
                        ),
                    )
                    self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _remove_object(
        self,
        instance: ObjectInstance,
        tag: bytes,
        *,
        timestamp: Any | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
    ) -> None:
        federation = self._require_joined()
        federation.objects.pop(instance.handle, None)
        federation.object_names.pop(instance.name, None)
        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if any(
                self._object_matches_subscription(instance.class_handle, subscribed)
                for subscribed in federate.subscribed_objects
            ):
                info = SupplementalRemoveInfo(producing_federate=self.state.handle)
                if timestamp is None:
                    event = CallbackEvent(
                        "removeObjectInstance",
                        (instance.handle, bytes(tag), OrderType.RECEIVE, info),
                    )
                    self._deliver(federate, event.method_name, *event.args)
                else:
                    event = CallbackEvent(
                        "removeObjectInstance",
                        (
                            instance.handle,
                            bytes(tag),
                            OrderType.TIMESTAMP,
                            timestamp,
                            OrderType.TIMESTAMP,
                            retraction_handle,
                            info,
                        ),
                    )
                    self._queue_or_deliver_tso(
                        federation,
                        federate,
                        timestamp,
                        event,
                        retraction_handle=retraction_handle,
                        producing_federate=self.state.handle,
                    )

    def _svc_deleteObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        *unused: Any,
    ) -> MessageRetractionReturn | None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        if instance.owner != self.state.handle:
            raise DeletePrivilegeNotHeld(repr(theObject))
        timestamp = self._extract_timestamp(tuple(unused))
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.object_instances_deleted += 1
        self._remove_object(
            instance,
            userSuppliedTag,
            timestamp=(timestamp if sent_tso else None),
            retraction_handle=(retraction.handle if retraction else None),
        )
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_localDeleteObjectInstance(self, theObject: ObjectInstanceHandle) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        assert self.state.handle is not None
        if any(self.state.handle in candidates for candidates in instance.attribute_candidates.values()):
            from ...exceptions import OwnershipAcquisitionPending

            raise OwnershipAcquisitionPending(repr(theObject))
        if (
            instance.owner == self.state.handle
            or any(owner == self.state.handle for owner in instance.attribute_owners.values())
        ):
            from ...exceptions import FederateOwnsAttributes

            raise FederateOwnsAttributes(repr(theObject))

    def _svc_requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        theType: TransportationTypeHandle,
    ) -> None:
        self._find_object(theObject)
        self._deliver(
            self.state,
            "confirmAttributeTransportationTypeChange",
            theObject,
            set(theAttributes),
            theType,
        )

    def _svc_queryAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:
        federation, _instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self._deliver(
            self.state,
            "reportAttributeTransportationType",
            theObject,
            theAttribute,
            self.engine.transportation_reliable,
        )

    def _svc_requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theClass)
        if (
            self.config.strict_interaction_publication
            and theClass not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(theClass))
        self._deliver(
            self.state,
            "confirmInteractionTransportationTypeChange",
            theClass,
            theType,
        )

    def _svc_queryInteractionTransportationType(self, theClass: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theClass)
        assert self.state.handle is not None
        self._deliver(
            self.state,
            "reportInteractionTransportationType",
            self.state.handle,
            theClass,
            self.engine.transportation_reliable,
        )
