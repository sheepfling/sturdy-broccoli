"""Subscription matching, scope bookkeeping, and region-filter helpers for the Python RTI backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol, cast

from hla.rti1516e.exceptions import InvalidInteractionClassHandle, InvalidObjectClassHandle
from hla.rti1516e.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle, RegionHandle
from .state import RTI_FEDERATE_HANDLE, FederateState, ObjectInstance

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine


class _SubscriptionContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: FederateState

    def _deliver(self, target: FederateState, method_name: str, *args: Any) -> None: ...

    def _region_sets_overlap(
        self,
        source_federate: FederateState,
        source_regions: set[RegionHandle],
        target_federate: FederateState,
        target_regions: set[RegionHandle],
    ) -> bool: ...


if TYPE_CHECKING:
    class _SubscriptionMixinBase(_SubscriptionContext):
        pass
else:
    class _SubscriptionMixinBase:
        pass


class PythonRTISubscriptionMixin(_SubscriptionMixinBase):
    """Object/interaction subscription matching and region overlap helpers."""

    def _object_matches_subscription(self, actual_class: object, subscribed_class: object) -> bool:
        instance_class = cast(ObjectClassHandle, actual_class)
        subscribed_class = cast(ObjectClassHandle, subscribed_class)
        try:
            return self.engine.object_class_is_a(instance_class, subscribed_class)
        except InvalidObjectClassHandle:
            return instance_class == subscribed_class

    def _interaction_matches_subscription(self, actual_class: InteractionClassHandle, subscribed_class: InteractionClassHandle) -> bool:
        interaction_class = actual_class
        try:
            return self.engine.interaction_class_is_a(interaction_class, subscribed_class)
        except InvalidInteractionClassHandle:
            return interaction_class == subscribed_class

    def _discover_existing_objects(self, subscriber: FederateState, object_class: ObjectClassHandle) -> None:
        federation = subscriber.federation
        if federation is None:
            return
        for instance in federation.objects.values():
            if self._object_matches_subscription(instance.class_handle, object_class):
                if self._ensure_known_object(subscriber, instance) is not None:
                    self._reconcile_object_attribute_scope(subscriber, instance)

    def _best_subscribed_object_class(self, subscriber: FederateState, instance_class: ObjectClassHandle) -> ObjectClassHandle | None:
        matches = [
            subscribed
            for subscribed in subscriber.subscribed_objects
            if self._object_matches_subscription(instance_class, subscribed)
        ]
        if not matches:
            return None
        return max(matches, key=lambda handle: len(self.engine.object_class_for_handle(handle).name))

    def _remember_known_object(self, subscriber: FederateState, instance: ObjectInstance, known_class: ObjectClassHandle) -> None:
        subscriber.known_object_classes[instance.handle] = known_class
        subscriber.known_object_names[instance.name] = instance.handle
        subscriber.locally_deleted_objects.discard(instance.handle)

    def _ensure_known_object(self, subscriber: FederateState, instance: ObjectInstance) -> ObjectClassHandle | None:
        known_class = subscriber.known_object_classes.get(instance.handle)
        if known_class is not None:
            return known_class
        discovered_class = self._best_subscribed_object_class(subscriber, instance.class_handle)
        if discovered_class is None:
            return None
        self._remember_known_object(subscriber, instance, discovered_class)
        self._deliver(
            subscriber,
            "discoverObjectInstance",
            instance.handle,
            discovered_class,
            instance.name,
            instance.owner or RTI_FEDERATE_HANDLE,
        )
        return discovered_class

    def _current_in_scope_attributes(self, subscriber: FederateState, instance: ObjectInstance) -> set[AttributeHandle]:
        subscribed = self._subscribed_attributes_for(subscriber, instance.class_handle)
        if not subscribed:
            return set()
        source_region_map = instance.update_regions or subscriber.update_regions.get(instance.handle, {})
        return {
            attribute
            for attribute in subscribed
            if self._attribute_region_allows(subscriber, instance, attribute, set(source_region_map.get(attribute, set())))
        }

    def _subscriber_has_region_scoped_object_interest(self, subscriber: FederateState, instance: ObjectInstance) -> bool:
        return any(
            self._object_matches_subscription(instance.class_handle, subscribed_class) and bool(attr_regions)
            for subscribed_class, attr_regions in subscriber.object_region_subscriptions.items()
        )

    def _clear_object_scope_tracking(self, subscriber: FederateState, object_handle: Any) -> None:
        subscriber.in_scope_object_attributes.pop(object_handle, None)

    def _published_attributes_for(self, publisher: FederateState, object_class: ObjectClassHandle) -> set[AttributeHandle]:
        result: set[AttributeHandle] = set()
        object_def = self.engine.object_class_for_handle(object_class)
        for published_class, attrs in publisher.published_objects.items():
            if not self._object_matches_subscription(object_class, published_class):
                continue
            for attr in attrs:
                attr_name = self.engine.attribute_name(published_class, attr)
                mapped = object_def.attributes_by_name.get(attr_name)
                if mapped is not None:
                    result.add(mapped)
        return result

    def _preferred_update_rate_designator_for_subscriber(
        self,
        subscriber: FederateState,
        instance: ObjectInstance,
        attribute: AttributeHandle,
    ) -> str | None:
        attribute_name = self.engine.attribute_name(instance.class_handle, attribute)
        matches: list[tuple[int, str | None]] = []
        for subscribed_class, attrs in subscriber.subscribed_objects.items():
            if not self._object_matches_subscription(instance.class_handle, subscribed_class):
                continue
            subscribed_attr = self.engine.object_class_for_handle(subscribed_class).attributes_by_name.get(attribute_name)
            if subscribed_attr is None or subscribed_attr not in attrs:
                continue
            designator = subscriber.subscribed_object_update_rate_designators.get(subscribed_class, {}).get(subscribed_attr)
            specificity = len(self.engine.object_class_for_handle(subscribed_class).name)
            matches.append((specificity, designator))
        if not matches:
            return None
        return max(matches, key=lambda item: (item[0], item[1] is not None))[1]

    def _current_relevant_update_designators(
        self,
        publisher: FederateState,
        instance: ObjectInstance,
    ) -> dict[AttributeHandle, str | None]:
        federation = publisher.federation
        if federation is None or publisher.handle is None or instance.owner != publisher.handle:
            return {}
        published = self._published_attributes_for(publisher, instance.class_handle)
        if not published:
            return {}
        result: dict[AttributeHandle, str | None] = {}
        for subscriber in federation.federates.values():
            if subscriber is publisher:
                continue
            for attr in subscriber.in_scope_object_attributes.get(instance.handle, set()):
                if attr not in published:
                    continue
                designator = self._preferred_update_rate_designator_for_subscriber(subscriber, instance, attr)
                if attr not in result or (result[attr] is None and designator is not None):
                    result[attr] = designator
        return result

    def _deliver_turn_updates_on_callbacks(
        self,
        publisher: FederateState,
        object_handle: Any,
        attributes_by_designator: dict[AttributeHandle, str | None],
    ) -> None:
        grouped: dict[str | None, set[AttributeHandle]] = {}
        for attr, designator in attributes_by_designator.items():
            grouped.setdefault(designator, set()).add(attr)
        for designator, attrs in grouped.items():
            if designator is None:
                self._deliver(publisher, "turnUpdatesOnForObjectInstance", object_handle, set(attrs))
            else:
                self._deliver(publisher, "turnUpdatesOnForObjectInstance", object_handle, set(attrs), designator)

    def _reconcile_owner_update_interest(self, instance: ObjectInstance) -> None:
        federation = self.state.federation
        if federation is None or instance.owner is None:
            return
        owner = federation.federates.get(instance.owner)
        if owner is None:
            return
        previous = dict(owner.relevant_object_update_designators.get(instance.handle, {}))
        current = self._current_relevant_update_designators(owner, instance)
        lost = {
            attr
            for attr, prior_designator in previous.items()
            if attr not in current or current[attr] != prior_designator
        }
        gained = {
            attr: designator
            for attr, designator in current.items()
            if attr not in previous or previous[attr] != designator
        }
        if current:
            owner.relevant_object_update_designators[instance.handle] = current
        else:
            owner.relevant_object_update_designators.pop(instance.handle, None)
        if not owner.attribute_relevance_advisory:
            return
        if lost:
            self._deliver(owner, "turnUpdatesOffForObjectInstance", instance.handle, set(lost))
        if gained:
            self._deliver_turn_updates_on_callbacks(owner, instance.handle, gained)

    def _reconcile_update_interest_for_owned_objects(
        self,
        publisher: FederateState,
        object_class: ObjectClassHandle | None = None,
    ) -> None:
        federation = publisher.federation
        if federation is None or publisher.handle is None:
            return
        for instance in federation.objects.values():
            if instance.owner != publisher.handle:
                continue
            if object_class is not None and not self._object_matches_subscription(instance.class_handle, object_class):
                continue
            self._reconcile_owner_update_interest(instance)

    def _reconcile_object_attribute_scope(self, subscriber: FederateState, instance: ObjectInstance) -> None:
        if instance.handle not in subscriber.known_object_classes:
            self._clear_object_scope_tracking(subscriber, instance.handle)
            self._reconcile_owner_update_interest(instance)
            return
        current = self._current_in_scope_attributes(subscriber, instance)
        previous = set(subscriber.in_scope_object_attributes.get(instance.handle, set()))
        gained = current - previous
        lost = previous - current
        if current:
            subscriber.in_scope_object_attributes[instance.handle] = current
        else:
            self._clear_object_scope_tracking(subscriber, instance.handle)
        self._reconcile_owner_update_interest(instance)
        if not subscriber.attribute_scope_advisory:
            return
        if gained:
            self._deliver(subscriber, "attributesInScope", instance.handle, set(gained))
        if lost:
            self._deliver(subscriber, "attributesOutOfScope", instance.handle, set(lost))

    def _reconcile_all_scopes_for_known_object(self, instance: ObjectInstance) -> None:
        federation = self.state.federation
        if federation is None:
            return
        for federate in list(federation.federates.values()):
            if instance.handle in federate.known_object_classes:
                self._reconcile_object_attribute_scope(federate, instance)

    def _reconcile_scope_for_all_known_objects(self, subscriber: FederateState) -> None:
        federation = subscriber.federation
        if federation is None:
            return
        for handle in list(subscriber.known_object_classes):
            instance = federation.objects.get(handle)
            if instance is None:
                self._clear_object_scope_tracking(subscriber, handle)
                continue
            self._reconcile_object_attribute_scope(subscriber, instance)

    def _subscribed_attributes_for(self, subscriber: FederateState, object_class: ObjectClassHandle) -> set[AttributeHandle]:
        result: set[AttributeHandle] = set()
        for subscribed_class, attrs in subscriber.subscribed_objects.items():
            if self._object_matches_subscription(object_class, subscribed_class):
                result.update(attrs)
        return result

    def _attribute_region_allows(
        self, subscriber: FederateState, instance: ObjectInstance, attribute: AttributeHandle, sent_regions: set[RegionHandle] | None
    ) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, attr_regions in subscriber.object_region_subscriptions.items():
            if self._object_matches_subscription(instance.class_handle, subscribed_class):
                subscription_regions.update(attr_regions.get(attribute, set()))
        if not subscription_regions:
            return True
        source_federate = federation.federates.get(instance.owner) if instance.owner is not None else None
        return self._region_sets_overlap(source_federate or self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _interaction_region_allows(self, subscriber: FederateState, interaction_class: InteractionClassHandle, sent_regions: set[RegionHandle] | None) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, regions in subscriber.interaction_region_subscriptions.items():
            if self._interaction_matches_subscription(interaction_class, subscribed_class):
                subscription_regions.update(regions)
        if not subscription_regions:
            return True
        return self._region_sets_overlap(self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _attribute_subscription_intersection(
        self,
        federate: FederateState,
        object_class: object,
        attributes: Mapping[AttributeHandle, bytes],
        instance: ObjectInstance | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set[RegionHandle]] | None = None,
    ) -> dict[AttributeHandle, bytes]:
        subscriber = federate
        subscribed = self._subscribed_attributes_for(subscriber, cast(ObjectClassHandle, object_class))
        if not subscribed:
            return {}
        known_class = None
        if instance is not None:
            known_class = self._ensure_known_object(subscriber, instance)
            if known_class is None:
                return {}
        reflected: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            mapped_handle = handle
            if known_class is not None:
                assert instance is not None
                attr_name = self.engine.attribute_name(instance.class_handle, handle)
                mapped_handle = self.engine.object_class_for_handle(known_class).attributes_by_name.get(attr_name)
                if mapped_handle is None:
                    continue
            if mapped_handle not in subscribed:
                continue
            if instance is not None and not self._attribute_region_allows(
                subscriber, instance, handle, set((sent_regions_by_attribute or {}).get(handle, set()))
            ):
                continue
            reflected[mapped_handle] = value
        return reflected


__all__ = ["PythonRTISubscriptionMixin"]
