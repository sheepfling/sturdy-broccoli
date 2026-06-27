"""Attribute update and value-request services for object delivery."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol

from hla.rti1516e.enums import OrderType
from hla.rti1516e.exceptions import (
    AttributeNotOwned,
    AttributeNotPublished,
    InvalidObjectClassHandle,
    ObjectInstanceNotKnown,
    ObjectClassNotDefined,
)
from hla.rti1516e.handles import (
    AttributeHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)
from hla.rti1516e.datatypes import MessageRetractionReturn

from .object_delivery_transport import PythonRTIObjectTransportMixin
from .state import CallbackEvent, ObjectInstance, SupplementalReflectInfo

if TYPE_CHECKING:
    from .state import FederateState, FederationState, PythonRTIConfig


class _ObjectAttributeDeliveryContext(Protocol):
    state: "FederateState"
    config: "PythonRTIConfig"

    def _find_object(self, theObject: ObjectInstanceHandle) -> tuple["FederationState", ObjectInstance]: ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _validate_user_supplied_tag(self, federation: "FederationState", category: str, user_supplied_tag: bytes) -> None: ...

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None: ...

    def _validate_tso_send_time(self, timestamp: Any) -> None: ...

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn: ...

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

    def _require_joined(self) -> "FederationState": ...

    def _is_mom_object_instance(self, federation: "FederationState", instance: ObjectInstance) -> bool: ...

    def _deliver_mom_attribute_update(self, instance: ObjectInstance, attrs: set[AttributeHandle], tag: bytes) -> None: ...

    def _object_matches_subscription(self, actual_class: object, subscribed_class: object) -> bool: ...


if TYPE_CHECKING:
    class _ObjectAttributeDeliveryMixinBase(PythonRTIObjectTransportMixin, _ObjectAttributeDeliveryContext):
        pass
else:
    class _ObjectAttributeDeliveryMixinBase(PythonRTIObjectTransportMixin):
        pass


class PythonRTIObjectAttributeDeliveryMixin(_ObjectAttributeDeliveryMixinBase):
    """Attribute update, request, and provide services."""

    def _svc_updateAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Mapping[AttributeHandle, bytes],
        userSuppliedTag: bytes,
        *unused: Any,
    ) -> MessageRetractionReturn | None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        for handle in theAttributes:
            self.engine.attribute_name(instance.class_handle, handle)
        if self.config.strict_object_publication:
            published = self.state.published_objects.get(instance.class_handle, set())
            if not set(theAttributes).issubset(published):
                raise AttributeNotPublished("Attribute update includes unpublished attributes")
        if any(
            instance.attribute_owners.get(handle, instance.owner) != self.state.handle
            for handle in theAttributes
        ):
            raise AttributeNotOwned(repr(theObject))
        self._validate_user_supplied_tag(federation, "updateReflectTag", bytes(userSuppliedTag))

        timestamp = self._extract_timestamp(tuple(unused))
        attrs = {handle: bytes(value) for handle, value in dict(theAttributes).items()}
        preferred_orders = [
            self.state.attribute_order_overrides.get(
                (theObject, handle),
                OrderType.TIMESTAMP
                if timestamp is not None
                else self.config.default_preferred_order_type,
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
            reflected = self._apply_update_rate_reduction(federate, instance, reflected, timestamp)
            if not reflected:
                continue
            attrs_by_transport: dict[
                TransportationTypeHandle, dict[AttributeHandle, bytes]
            ] = defaultdict(dict)
            for handle, value in reflected.items():
                attrs_by_transport[
                    self._transportation_type_for_reflected_attribute(federate, instance, handle)
                ][handle] = value
            for transport, reflected_group in attrs_by_transport.items():
                group_regions = (
                    frozenset().union(
                        *(instance.update_regions.get(attr, set()) for attr in reflected_group)
                    )
                    if reflected_group
                    else frozenset()
                )
                info = SupplementalReflectInfo(
                    producing_federate=self.state.handle,
                    sent_regions=frozenset(group_regions),
                )
                if sent_tso and federate.time_constrained_enabled:
                    assert retraction is not None
                    event = CallbackEvent(
                        "reflectAttributeValues",
                        (
                            instance.handle,
                            reflected_group,
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
                        "reflectAttributeValues",
                        (
                            instance.handle,
                            reflected_group,
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
        self._validate_user_supplied_tag(federation, "requestUpdateTag", tag)

        def deliver(instance: ObjectInstance) -> None:
            if self._is_mom_object_instance(federation, instance):
                self._deliver_mom_attribute_update(instance, attrs, tag)
                return
            owner_handle = instance.owner
            owner = federation.federates.get(owner_handle) if owner_handle is not None else None
            if owner is not None:
                owner_backend = getattr(owner, "backend", None)
                if owner_backend is not None:
                    owner_backend._svc_provideAttributeValueUpdate(instance.handle, attrs, tag)

        if isinstance(target, ObjectInstanceHandle):
            try:
                instance = federation.objects[target]
            except KeyError as exc:
                raise ObjectInstanceNotKnown(repr(target)) from exc
            for attribute in attrs:
                self.engine.attribute_name(instance.class_handle, attribute)
            deliver(instance)
            return

        if isinstance(target, ObjectClassHandle):
            try:
                self.engine.object_class_for_handle(target)
            except InvalidObjectClassHandle as exc:
                raise ObjectClassNotDefined(repr(target)) from exc
            for attribute in attrs:
                self.engine.attribute_name(target, attribute)
            for instance in list(federation.objects.values()):
                if self._object_matches_subscription(instance.class_handle, target):
                    deliver(instance)
            return

        raise ObjectInstanceNotKnown(repr(target))

    def _svc_provideAttributeValueUpdate(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes = b"",
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(theAttributes)
        tag = bytes(userSuppliedTag)
        for attribute in attrs:
            self.engine.attribute_name(instance.class_handle, attribute)
        self._deliver(self.state, "provideAttributeValueUpdate", instance.handle, attrs, tag)
