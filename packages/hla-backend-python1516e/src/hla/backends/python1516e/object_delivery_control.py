"""Object removal, update-control, and transport-change services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol, cast

from hla.rti1516e.enums import OrderType
from hla.rti1516e.exceptions import (
    AttributeNotOwned,
    AttributeNotPublished,
    DeletePrivilegeNotHeld,
    InteractionClassNotPublished,
    InvalidUpdateRateDesignator,
)
from hla.rti1516e.handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)
from hla.rti1516e.datatypes import MessageRetractionReturn

from .object_delivery_interactions import PythonRTIObjectInteractionDeliveryMixin
from .state import CallbackEvent, ObjectInstance, SupplementalRemoveInfo

if TYPE_CHECKING:
    from .state import FederateState, FederationState


class _ObjectDeliveryControlContext(Protocol):
    state: "FederateState"

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...

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

    def _require_joined(self) -> "FederationState": ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None: ...

    def _validate_tso_send_time(self, timestamp: Any) -> None: ...

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn: ...

    def _refresh_mom_federate_object(self, federation: "FederationState", federate: "FederateState", *, notify: bool = True) -> None: ...

    def _process_time_advances(self, federation: "FederationState") -> None: ...

    def _reconcile_owner_update_interest(self, instance: ObjectInstance) -> None: ...


if TYPE_CHECKING:
    class _ObjectDeliveryControlMixinBase(PythonRTIObjectInteractionDeliveryMixin, _ObjectDeliveryControlContext):
        pass
else:
    class _ObjectDeliveryControlMixinBase(PythonRTIObjectInteractionDeliveryMixin):
        pass


class PythonRTIObjectDeliveryControlMixin(_ObjectDeliveryControlMixinBase):
    """Object deletion, update-control, and transport query/change services."""

    def _remove_object_with_producer(
        self,
        federation: "FederationState",
        instance: ObjectInstance,
        tag: bytes,
        *,
        producing_federate: FederateHandle,
        timestamp: Any | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
    ) -> None:
        federation.objects.pop(instance.handle, None)
        federation.object_names.pop(instance.name, None)
        for federate in list(federation.federates.values()):
            if federate.handle == producing_federate:
                continue
            if instance.handle not in federate.known_object_classes:
                continue
            if any(
                self._object_matches_subscription(instance.class_handle, subscribed)
                for subscribed in federate.subscribed_objects
            ):

                def cleanup_known_state(
                    target: Any = federate,
                    object_handle: ObjectInstanceHandle = instance.handle,
                    object_name: str = instance.name,
                ) -> None:
                    target.known_object_classes.pop(object_handle, None)
                    target.known_object_names.pop(object_name, None)
                    target.in_scope_object_attributes.pop(object_handle, None)
                    target.locally_deleted_objects.discard(object_handle)
                    stale_keys = [
                        key for key in target.last_reflect_logical_times if key[0] == object_handle
                    ]
                    for key in stale_keys:
                        target.last_reflect_logical_times.pop(key, None)

                info = SupplementalRemoveInfo(producing_federate=producing_federate)
                if timestamp is None:
                    event = CallbackEvent(
                        "removeObjectInstance",
                        (instance.handle, bytes(tag), OrderType.RECEIVE, info),
                    )
                    self._deliver(federate, event.method_name, *event.args)
                    cleanup_known_state()
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
                        producing_federate=producing_federate,
                        post_deliver_cleanup=cleanup_known_state,
                    )

    def _remove_object(
        self,
        instance: ObjectInstance,
        tag: bytes,
        *,
        timestamp: Any | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
    ) -> None:
        federation = self._require_joined()
        assert self.state.handle is not None
        self._remove_object_with_producer(
            federation,
            instance,
            tag,
            producing_federate=self.state.handle,
            timestamp=timestamp,
            retraction_handle=retraction_handle,
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
            from hla.rti1516e.exceptions import OwnershipAcquisitionPending

            raise OwnershipAcquisitionPending(repr(theObject))
        if (
            instance.owner == self.state.handle
            or any(owner == self.state.handle for owner in instance.attribute_owners.values())
        ):
            from hla.rti1516e.exceptions import FederateOwnsAttributes

            raise FederateOwnsAttributes(repr(theObject))
        self.state.known_object_classes.pop(theObject, None)
        self.state.known_object_names.pop(instance.name, None)
        self.state.in_scope_object_attributes.pop(theObject, None)
        self.state.locally_deleted_objects.add(theObject)
        stale_keys = [key for key in self.state.last_reflect_logical_times if key[0] == theObject]
        for key in stale_keys:
            self.state.last_reflect_logical_times.pop(key, None)
        self._reconcile_owner_update_interest(instance)

    def _validate_turn_updates_object_attributes(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> tuple["FederationState", ObjectInstance, set[AttributeHandle]]:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(theAttributes)
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
        return federation, instance, attrs

    def _validate_turn_updates_designator(
        self,
        federation: "FederationState",
        updateRateDesignator: str | None,
    ) -> str | None:
        if updateRateDesignator in (None, ""):
            return None
        designator = "HLAdefault" if updateRateDesignator == "default" else str(updateRateDesignator)
        if designator != "HLAdefault" and designator not in federation.fom_catalog.update_rates:
            raise InvalidUpdateRateDesignator(designator)
        return designator

    def _svc_turnUpdatesOnForObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        updateRateDesignator: str | None = None,
    ) -> None:
        federation, instance, attrs = self._validate_turn_updates_object_attributes(
            theObject, theAttributes
        )
        designator = self._validate_turn_updates_designator(federation, updateRateDesignator)
        if designator is None:
            self._deliver(self.state, "turnUpdatesOnForObjectInstance", instance.handle, attrs)
        else:
            self._deliver(
                self.state, "turnUpdatesOnForObjectInstance", instance.handle, attrs, designator
            )

    def _svc_turnUpdatesOffForObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> None:
        _federation, instance, attrs = self._validate_turn_updates_object_attributes(
            theObject, theAttributes
        )
        self._deliver(self.state, "turnUpdatesOffForObjectInstance", instance.handle, attrs)

    def _svc_requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        theType: TransportationTypeHandle,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self._validate_transportation_type(theType)
        attrs = set(theAttributes)
        if self.config.strict_object_publication:
            published = self.state.published_objects.get(instance.class_handle, set())
            if not attrs.issubset(published):
                raise AttributeNotPublished(
                    "Attribute transportation update includes unpublished attributes"
                )
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner != self.state.handle:
                raise AttributeNotOwned(repr(attr))
        for attr in attrs:
            self.state.attribute_transportation_overrides[(theObject, attr)] = theType
        self._deliver(
            self.state,
            "confirmAttributeTransportationTypeChange",
            theObject,
            attrs,
            theType,
        )

    def _svc_queryAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.attribute_name(instance.class_handle, theAttribute)
        transport = self._transportation_type_for_attribute(theObject, theAttribute)
        self._deliver(
            self.state,
            "reportAttributeTransportationType",
            theObject,
            theAttribute,
            transport,
        )

    def _svc_requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        interaction_class = theClass
        self.engine.interaction_for_handle(interaction_class)
        if (
            self.config.strict_interaction_publication
            and interaction_class not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(interaction_class))
        self._validate_transportation_type(theType)
        self.state.interaction_transportation_overrides[interaction_class] = theType
        self._deliver(
            self.state,
            "confirmInteractionTransportationTypeChange",
            interaction_class,
            theType,
        )

    def _svc_queryInteractionTransportationType(
        self,
        *args: FederateHandle | InteractionClassHandle,
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if len(args) == 1:
            theClass = args[0]
        elif len(args) == 2:
            _theFederate, theClass = args
        else:
            raise TypeError("queryInteractionTransportationType expects one or two arguments")
        interaction_class = cast(InteractionClassHandle, theClass)
        self.engine.interaction_for_handle(interaction_class)
        assert self.state.handle is not None
        transport = self._transportation_type_for_interaction(interaction_class)
        self._deliver(
            self.state,
            "reportInteractionTransportationType",
            self.state.handle,
            interaction_class,
            transport,
        )
