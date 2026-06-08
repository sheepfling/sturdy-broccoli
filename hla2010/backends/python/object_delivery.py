"""Object update, delete, interaction, and transport helpers."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

from ...enums import OrderType
from ...exceptions import (
    AttributeNotOwned,
    AttributeNotPublished,
    CouldNotDecode,
    DeletePrivilegeNotHeld,
    InteractionClassNotPublished,
    InvalidTransportationType,
    ObjectInstanceNotKnown,
)
from ...fom import validate_encoded_datatype_value
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

    def _transportation_handle_from_fom_name(self, name: str | None) -> TransportationTypeHandle:
        normalized = str(name or "").strip()
        handle = self._transportation_handle_by_name(normalized)
        if handle is None:
            return self.engine.transportation_reliable
        return handle

    def _default_transportation_type_for_attribute(
        self,
        object_handle: ObjectInstanceHandle,
        attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        federation = self.state.federation
        if federation is None:
            return self.engine.transportation_reliable
        try:
            instance = federation.objects[object_handle]
        except KeyError:
            return self.engine.transportation_reliable
        class_name = self.engine.object_class_for_handle(instance.class_handle).name
        spec = federation.fom_catalog.object_classes.get(class_name)
        if spec is None:
            return self.engine.transportation_reliable
        attribute_name = self.engine.attribute_name(instance.class_handle, attribute)
        return self._transportation_handle_from_fom_name(
            dict(spec.attribute_transportations).get(attribute_name)
        )

    def _default_transportation_type_for_interaction(
        self,
        interaction: InteractionClassHandle,
    ) -> TransportationTypeHandle:
        federation = self.state.federation
        if federation is None:
            return self.engine.transportation_reliable
        class_name = self.engine.interaction_for_handle(interaction).name
        spec = federation.fom_catalog.interaction_classes.get(class_name)
        if spec is None:
            return self.engine.transportation_reliable
        return self._transportation_handle_from_fom_name(spec.transportation)

    def _subscribed_update_rate_for_attribute(
        self,
        federate: Any,
        instance: ObjectInstance,
        attribute: AttributeHandle,
    ) -> float:
        try:
            attribute_name = self.engine.attribute_name(instance.class_handle, attribute)
        except Exception:
            known_class = federate.known_object_classes.get(instance.handle)
            if known_class is None:
                return 0.0
            attribute_name = self.engine.attribute_name(known_class, attribute)
        matches: list[tuple[int, float]] = []
        for subscribed_class, rate_map in federate.subscribed_object_update_rates.items():
            if not self._object_matches_subscription(instance.class_handle, subscribed_class):
                continue
            subscribed_attr = self.engine.object_class_for_handle(subscribed_class).attributes_by_name.get(attribute_name)
            if subscribed_attr is None:
                continue
            if subscribed_attr not in rate_map:
                continue
            specificity = len(self.engine.object_class_for_handle(subscribed_class).name)
            matches.append((specificity, float(rate_map[subscribed_attr])))
        if not matches:
            return 0.0
        return max(matches, key=lambda item: item[0])[1]

    def _transportation_type_for_attribute(
        self,
        object_handle: ObjectInstanceHandle,
        attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        return self.state.attribute_transportation_overrides.get(
            (object_handle, attribute),
            self._default_transportation_type_for_attribute(object_handle, attribute),
        )

    def _transportation_type_for_reflected_attribute(
        self,
        federate: Any,
        instance: ObjectInstance,
        reflected_attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        try:
            return self._transportation_type_for_attribute(instance.handle, reflected_attribute)
        except Exception:
            known_class = federate.known_object_classes.get(instance.handle)
            if known_class is None:
                raise
            attribute_name = self.engine.attribute_name(known_class, reflected_attribute)
            source_attribute = self.engine.object_class_for_handle(instance.class_handle).attributes_by_name.get(attribute_name)
            if source_attribute is None:
                raise
            return self._transportation_type_for_attribute(instance.handle, source_attribute)

    def _transportation_type_for_interaction(
        self,
        interaction: InteractionClassHandle,
    ) -> TransportationTypeHandle:
        return self.state.interaction_transportation_overrides.get(
            interaction,
            self._default_transportation_type_for_interaction(interaction),
        )

    def _validate_transportation_type(
        self,
        theType: TransportationTypeHandle,
    ) -> None:
        if theType not in {
            self.engine.transportation_reliable,
            self.engine.transportation_best_effort,
        }:
            raise InvalidTransportationType(repr(theType))

    @staticmethod
    def _time_scalar(value: Any) -> float | None:
        if value is None:
            return None
        scalar = getattr(value, "value", value)
        try:
            return float(scalar)
        except Exception:
            return None

    def _apply_update_rate_reduction(
        self,
        federate: Any,
        instance: ObjectInstance,
        attributes: Mapping[AttributeHandle, bytes],
        delivery_time: Any | None,
    ) -> dict[AttributeHandle, bytes]:
        scalar_time = self._time_scalar(delivery_time)
        if scalar_time is None and (self.state.time_regulation_enabled or self.state.time_constrained_enabled):
            scalar_time = self._time_scalar(self.state.current_time)
        if scalar_time is None:
            return dict(attributes)
        filtered: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            rate = self._subscribed_update_rate_for_attribute(federate, instance, handle)
            if rate <= 0.0:
                filtered[handle] = value
                federate.last_reflect_logical_times[(instance.handle, handle)] = scalar_time
                continue
            min_interval = 1.0 / rate
            last_time = federate.last_reflect_logical_times.get((instance.handle, handle))
            if last_time is None or (scalar_time - last_time) >= min_interval:
                filtered[handle] = value
                federate.last_reflect_logical_times[(instance.handle, handle)] = scalar_time
        return filtered

    def _validate_user_supplied_tag(self, federation: Any, category: str, user_supplied_tag: bytes) -> None:
        metadata = federation.fom_catalog.tag_representations.get(str(category), {})
        datatype = str(metadata.get("datatype", "")).strip()
        if not datatype or datatype in {"", "NA", "N/A"}:
            return
        try:
            validate_encoded_datatype_value(bytes(user_supplied_tag), datatype, federation.fom_catalog)
        except CouldNotDecode as exc:
            raise CouldNotDecode(f"Could not decode {category} as {datatype}") from exc

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
            # Update-rate reduction is only well-defined when delivery has a logical-time basis.
            reflected = self._apply_update_rate_reduction(federate, instance, reflected, timestamp)
            if not reflected:
                continue
            sent_regions = (
                frozenset().union(*(instance.update_regions.get(attr, set()) for attr in reflected))
                if reflected
                else frozenset()
            )
            attrs_by_transport: dict[TransportationTypeHandle, dict[AttributeHandle, bytes]] = defaultdict(dict)
            for handle, value in reflected.items():
                attrs_by_transport[self._transportation_type_for_reflected_attribute(federate, instance, handle)][handle] = value
            for transport, reflected_group in attrs_by_transport.items():
                group_regions = (
                    frozenset().union(*(instance.update_regions.get(attr, set()) for attr in reflected_group))
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
            owner = federation.federates.get(instance.owner)
            if owner is not None:
                self._deliver(owner, "provideAttributeValueUpdate", instance.handle, attrs, tag)

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
            self.engine.object_class_for_handle(target)
            for attribute in attrs:
                self.engine.attribute_name(target, attribute)
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
        for parameter in params:
            self.engine.parameter_name(theInteraction, parameter)
        self._validate_user_supplied_tag(federation, "sendReceiveTag", bytes(userSuppliedTag))

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
            if instance.handle not in federate.known_object_classes:
                continue
            if any(
                self._object_matches_subscription(instance.class_handle, subscribed)
                for subscribed in federate.subscribed_objects
            ):
                def cleanup_known_state(target=federate, object_handle=instance.handle, object_name=instance.name) -> None:
                    target.known_object_classes.pop(object_handle, None)
                    target.known_object_names.pop(object_name, None)
                    target.in_scope_object_attributes.pop(object_handle, None)
                    target.locally_deleted_objects.discard(object_handle)
                    stale_keys = [key for key in target.last_reflect_logical_times if key[0] == object_handle]
                    for key in stale_keys:
                        target.last_reflect_logical_times.pop(key, None)

                info = SupplementalRemoveInfo(producing_federate=self.state.handle)
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
                        producing_federate=self.state.handle,
                        post_deliver_cleanup=cleanup_known_state,
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
        self.state.known_object_classes.pop(theObject, None)
        self.state.known_object_names.pop(instance.name, None)
        self.state.in_scope_object_attributes.pop(theObject, None)
        self.state.locally_deleted_objects.add(theObject)
        stale_keys = [key for key in self.state.last_reflect_logical_times if key[0] == theObject]
        for key in stale_keys:
            self.state.last_reflect_logical_times.pop(key, None)

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
                raise AttributeNotPublished("Attribute transportation update includes unpublished attributes")
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
        federation, _instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.attribute_name(_instance.class_handle, theAttribute)
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
        self.engine.interaction_for_handle(theClass)
        if (
            self.config.strict_interaction_publication
            and theClass not in self.state.published_interactions
        ):
            raise InteractionClassNotPublished(repr(theClass))
        self._validate_transportation_type(theType)
        self.state.interaction_transportation_overrides[theClass] = theType
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
        transport = self._transportation_type_for_interaction(theClass)
        self._deliver(
            self.state,
            "reportInteractionTransportationType",
            self.state.handle,
            theClass,
            transport,
        )
