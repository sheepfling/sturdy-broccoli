"""Data distribution management services for the in-memory Python RTI backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol, cast

from hla2010 import mom as hla_mom
from hla2010.enums import OrderType
from hla2010.exceptions import (
    AttributeNotPublished,
    InteractionClassNotPublished,
    InvalidRangeBound,
    InvalidRegion,
    InvalidRegionContext,
    InvalidUpdateRateDesignator,
    RegionDoesNotContainSpecifiedDimension,
)
from hla2010.handles import AttributeHandle, DimensionHandle, InteractionClassHandle, ObjectInstanceHandle, ParameterHandle, RegionHandle
from hla2010.types import MessageRetractionReturn, RangeBounds
from .state import CallbackEvent, FederateState, ObjectInstance, SupplementalReceiveInfo

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederationState, PythonRTIConfig


class _DdmContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: FederateState
    config: "PythonRTIConfig"

    def _require_joined(self) -> "FederationState": ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _object_matches_subscription(self, actual_class: Any, subscribed_class: Any) -> bool: ...

    def _reconcile_scope_for_all_known_objects(self, subscriber: FederateState) -> None: ...

    def _reconcile_all_scopes_for_known_object(self, instance: ObjectInstance) -> None: ...

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None: ...

    def _transportation_type_for_interaction(self, theInteraction: InteractionClassHandle) -> Any: ...

    def _validate_tso_send_time(self, timestamp: Any) -> None: ...

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn: ...

    def _interaction_matches_subscription(self, actual_class: InteractionClassHandle, subscribed_class: InteractionClassHandle) -> bool: ...

    def _queue_or_deliver_tso(
        self,
        federation: "FederationState",
        recipient: FederateState,
        timestamp: Any | None,
        event: CallbackEvent,
        *,
        retraction_handle: Any | None,
        producing_federate: Any | None,
        post_deliver_cleanup: Any | None = None,
    ) -> Any: ...

    def _deliver(self, federate: FederateState, method_name: str, *args: Any, **kwargs: Any) -> Any: ...

    def _refresh_mom_federate_object(self, federation: "FederationState", federate: FederateState, *, notify: bool = False) -> None: ...

    def _process_time_advances(self, federation: "FederationState") -> None: ...

    def _svc_subscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any: ...

    def _svc_unsubscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any: ...

    def _svc_unsubscribeObjectClass(self, *args: Any, **kwargs: Any) -> Any: ...

    def _svc_subscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any: ...

    def _svc_unsubscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any: ...

    def _svc_registerObjectInstance(self, *args: Any, **kwargs: Any) -> Any: ...

    def _find_object(self, theObject: Any) -> tuple["FederationState", ObjectInstance]: ...

    def _validate_user_supplied_tag(self, federation: "FederationState", category: str, user_supplied_tag: bytes) -> None: ...

    def _handle_mom_interaction(self, interaction_name: str, params: Mapping[ParameterHandle, bytes], tag: bytes) -> bool: ...

    def _svc_requestAttributeValueUpdate(self, target: Any, attributes: Iterable[AttributeHandle], userSuppliedTag: bytes = b"") -> None: ...

if TYPE_CHECKING:
    class _DdmMixinBase(_DdmContext):
        pass
else:
    class _DdmMixinBase:
        pass


class PythonRTIDdmMixin(_DdmMixinBase):
    """HLA DDM region lifecycle, overlap filtering, and region-aware services."""

    def _reject_mom_object_class_for_ddm(self, theClass: Any) -> None:
        if hla_mom.is_mom_object_class_name(self.engine.object_class_for_handle(theClass).name):
            raise InvalidRegionContext("DDM services shall not be used with MOM object classes")

    def _reject_mom_interaction_class_for_ddm(self, theClass: InteractionClassHandle) -> None:
        if hla_mom.is_mom_interaction_class_name(self.engine.interaction_for_handle(theClass).name):
            raise InvalidRegionContext("DDM services shall not be used with MOM interaction classes")

    def _svc_createRegion(self, dimensions: Iterable[DimensionHandle]) -> RegionHandle:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        handle = self.engine._alloc(RegionHandle)
        dims = set(dimensions)
        for dimension in dims:
            self.engine.dimension_name(dimension)
        self.state.regions[handle] = dims
        self.state.region_bounds[handle] = {dimension: RangeBounds(0, (1 << 63) - 1) for dimension in dims}
        return handle

    def _svc_commitRegionModifications(self, regions: Iterable[RegionHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        changed_regions = set(regions)
        for region in changed_regions:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        if any(region in regions_for_attr for attr_regions in self.state.object_region_subscriptions.values() for regions_for_attr in attr_regions.values() for region in changed_regions):
            self._reconcile_scope_for_all_known_objects(self.state)
        for instance in list(federation.objects.values()):
            source_region_map = instance.update_regions or {}
            if any(region in regions_for_attr for regions_for_attr in source_region_map.values() for region in changed_regions):
                self._reconcile_all_scopes_for_known_object(instance)

    def _svc_deleteRegion(self, theRegion: RegionHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if theRegion not in self.state.regions:
            raise InvalidRegion(repr(theRegion))
        self.state.regions.pop(theRegion, None)
        self.state.region_bounds.pop(theRegion, None)

    def _region_bounds_for(self, federate: FederateState, region: RegionHandle) -> dict[DimensionHandle, RangeBounds]:
        if region not in federate.regions:
            raise InvalidRegion(repr(region))
        return federate.region_bounds.setdefault(region, {})

    @staticmethod
    def _range_overlap(left: RangeBounds, right: RangeBounds) -> bool:
        left_lower = getattr(left, "lower", getattr(left, "lower_bound", 0))
        left_upper = getattr(left, "upper", getattr(left, "upper_bound", 0))
        right_lower = getattr(right, "lower", getattr(right, "lower_bound", 0))
        right_upper = getattr(right, "upper", getattr(right, "upper_bound", 0))
        return int(left_lower) <= int(right_upper) and int(right_lower) <= int(left_upper)

    def _regions_overlap_pair(
        self,
        source_federate: FederateState,
        source_region: RegionHandle,
        target_federate: FederateState,
        target_region: RegionHandle,
    ) -> bool:
        if source_region not in source_federate.regions or target_region not in target_federate.regions:
            return False
        common_dims = set(source_federate.regions[source_region]) & set(target_federate.regions[target_region])
        if not common_dims:
            return False
        for dimension in common_dims:
            source_bounds = self._region_bounds_for(source_federate, source_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            target_bounds = self._region_bounds_for(target_federate, target_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            if not self._range_overlap(source_bounds, target_bounds):
                return False
        return True

    def _region_sets_overlap(
        self,
        source_federate: FederateState,
        source_regions: set[RegionHandle],
        target_federate: FederateState,
        target_regions: set[RegionHandle],
    ) -> bool:
        if not target_regions:
            return True
        if not source_regions:
            return True
        return any(
            self._regions_overlap_pair(source_federate, source_region, target_federate, target_region)
            for source_region in source_regions
            for target_region in target_regions
        )

    def _filter_reflected_attributes_by_regions(
        self,
        subscriber: FederateState,
        instance: ObjectInstance,
        reflected: dict[AttributeHandle, bytes],
    ) -> dict[AttributeHandle, bytes]:
        subscription: dict[AttributeHandle, set[RegionHandle]] = {}
        for subscribed_class, class_regions in subscriber.object_region_subscriptions.items():
            if self._object_matches_subscription(instance.class_handle, subscribed_class):
                for attr, regions in class_regions.items():
                    subscription.setdefault(attr, set()).update(regions)
        if not subscription:
            return reflected
        filtered: dict[AttributeHandle, bytes] = {}
        source_region_map = instance.update_regions or self.state.update_regions.get(instance.handle, {})
        for attr, value in reflected.items():
            target_regions = subscription.get(attr, set())
            if not target_regions:
                filtered[attr] = value
                continue
            source_regions = source_region_map.get(attr, set())
            if self._region_sets_overlap(self.state, set(source_regions), subscriber, set(target_regions)):
                filtered[attr] = value
        return filtered

    def _attribute_region_pairs(self, attributesAndRegions: Iterable[Any]) -> list[tuple[set[AttributeHandle], set[RegionHandle]]]:
        self._require_joined()
        pairs: list[tuple[set[AttributeHandle], set[RegionHandle]]] = []
        for pair in attributesAndRegions or []:
            if hasattr(pair, "attributes") and hasattr(pair, "regions"):
                attrs = getattr(pair, "attributes")
                regions = getattr(pair, "regions")
            elif isinstance(pair, Mapping):
                attrs = pair.get("attributes") or pair.get("attribute_handles") or pair.get("attributeList") or ()
                regions = pair.get("regions") or pair.get("region_handles") or pair.get("regionSet") or ()
            elif isinstance(pair, (tuple, list)) and len(pair) >= 2:
                attrs, regions = pair[0], pair[1]
            else:
                raise InvalidRegionContext(f"Bad attribute/region pair: {pair!r}")
            attr_set: set[AttributeHandle] = (
                {attrs} if isinstance(attrs, AttributeHandle) else set(cast(Iterable[AttributeHandle], attrs))
            )
            region_set: set[RegionHandle] = (
                {regions} if isinstance(regions, RegionHandle) else set(cast(Iterable[RegionHandle], regions))
            )
            for region in region_set:
                if region not in self.state.regions:
                    raise InvalidRegion(repr(region))
            pairs.append((attr_set, region_set))
        return pairs

    def _attributes_from_region_pairs(self, attributesAndRegions: Iterable[Any]) -> set[AttributeHandle]:
        attrs: set[AttributeHandle] = set()
        for attr_set, _region_set in self._attribute_region_pairs(attributesAndRegions):
            attrs.update(attr_set)
        return attrs

    def _svc_subscribeObjectClassAttributesWithRegions(self, theClass: Any, attributesAndRegions: Iterable[Any], *unused: Any) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self._reject_mom_object_class_for_ddm(theClass)
        update_rate_designator = next((str(arg) for arg in reversed(unused) if isinstance(arg, str)), None)
        if update_rate_designator not in (None, "", "default", "HLAdefault"):
            raise InvalidUpdateRateDesignator(update_rate_designator)
        pairs = self._attribute_region_pairs(attributesAndRegions)
        attrs = set()
        region_map = self.state.object_region_subscriptions.setdefault(theClass, {})
        for attr_set, region_set in pairs:
            attrs.update(attr_set)
            for attr in attr_set:
                self.engine.attribute_name(theClass, attr)
                region_map.setdefault(attr, set()).update(region_set)
        self._svc_subscribeObjectClassAttributes(theClass, attrs, *unused)
        self._reconcile_scope_for_all_known_objects(self.state)

    def _svc_subscribeObjectClassAttributesPassivelyWithRegions(self, theClass: Any, attributesAndRegions: Iterable[Any], *unused: Any) -> None:
        self._svc_subscribeObjectClassAttributesWithRegions(theClass, attributesAndRegions, *unused)

    def _svc_unsubscribeObjectClassAttributesWithRegions(self, theClass: Any, attributesAndRegions: Iterable[Any]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self._reject_mom_object_class_for_ddm(theClass)
        pairs = self._attribute_region_pairs(attributesAndRegions)
        class_regions = self.state.object_region_subscriptions.get(theClass, {})
        attrs: set[AttributeHandle] = set()
        for attr_set, region_set in pairs:
            attrs.update(attr_set)
            for attr in attr_set:
                if attr in class_regions:
                    class_regions[attr].difference_update(region_set)
                    if not class_regions[attr]:
                        class_regions.pop(attr, None)
        if not class_regions:
            self.state.object_region_subscriptions.pop(theClass, None)
        if attrs:
            self._svc_unsubscribeObjectClassAttributes(theClass, attrs)
        else:
            self._svc_unsubscribeObjectClass(theClass)
        self._reconcile_scope_for_all_known_objects(self.state)

    def _svc_subscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle], *unused: Any) -> None:
        self._require_joined()
        self._reject_mom_interaction_class_for_ddm(theClass)
        region_set = set(regions)
        for region in region_set:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        self.state.interaction_region_subscriptions.setdefault(theClass, set()).update(region_set)
        self._svc_subscribeInteractionClass(theClass, *unused)

    def _svc_subscribeInteractionClassPassivelyWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle], *unused: Any) -> None:
        self._svc_subscribeInteractionClassWithRegions(theClass, regions, *unused)

    def _svc_unsubscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self._reject_mom_interaction_class_for_ddm(theClass)
        region_set = set(regions)
        for region in region_set:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        if theClass in self.state.interaction_region_subscriptions:
            self.state.interaction_region_subscriptions[theClass].difference_update(region_set)
            if not self.state.interaction_region_subscriptions[theClass]:
                self.state.interaction_region_subscriptions.pop(theClass, None)
        self._svc_unsubscribeInteractionClass(theClass)

    def _svc_registerObjectInstanceWithRegions(
        self, theClass: Any, attributesAndRegions: Iterable[Any], theObjectName: str | None = None
    ) -> ObjectInstanceHandle:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self._reject_mom_object_class_for_ddm(theClass)
        handle = self._svc_registerObjectInstance(theClass, theObjectName)
        _fed, instance = self._find_object(handle)
        region_map = self.state.update_regions.setdefault(handle, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                self.engine.attribute_name(instance.class_handle, attr)
                if self.config.strict_object_publication:
                    published = self.state.published_objects.get(instance.class_handle, set())
                    if attr not in published:
                        raise AttributeNotPublished(repr(attr))
                region_map.setdefault(attr, set()).update(regions)
                instance.update_regions.setdefault(attr, set()).update(regions)
        return handle

    def _svc_associateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: Iterable[Any]) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        region_map = self.state.update_regions.setdefault(theObject, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                self.engine.attribute_name(instance.class_handle, attr)
                region_map.setdefault(attr, set()).update(regions)
                instance.update_regions.setdefault(attr, set()).update(regions)
        self._reconcile_all_scopes_for_known_object(instance)

    def _svc_unassociateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: Iterable[Any]) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        region_map = self.state.update_regions.setdefault(theObject, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                self.engine.attribute_name(instance.class_handle, attr)
                if attr in region_map:
                    region_map[attr].difference_update(regions)
                    if not region_map[attr]:
                        del region_map[attr]
                if attr in instance.update_regions:
                    instance.update_regions[attr].difference_update(regions)
                    if not instance.update_regions[attr]:
                        del instance.update_regions[attr]
        self._reconcile_all_scopes_for_known_object(instance)

    def _svc_sendInteractionWithRegions(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: Mapping[ParameterHandle, bytes],
        regions: Iterable[RegionHandle],
        userSuppliedTag: bytes,
        *unused: Any,
    ) -> MessageRetractionReturn | None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self._validate_user_supplied_tag(federation, "sendReceiveTag", bytes(userSuppliedTag))
        self._reject_mom_interaction_class_for_ddm(theInteraction)
        interaction_def = self.engine.interaction_for_handle(theInteraction)
        source_regions = set(regions)
        for region in source_regions:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        params = {handle: bytes(value) for handle, value in dict(theParameters).items()}
        if self._handle_mom_interaction(interaction_def.name, params, bytes(userSuppliedTag)):
            return None
        if self.config.strict_interaction_publication and theInteraction not in self.state.published_interactions:
            raise InteractionClassNotPublished(repr(theInteraction))
        for parameter in params:
            self.engine.parameter_name(theInteraction, parameter)
        timestamp = self._extract_timestamp(tuple(unused))
        preferred = self.state.interaction_order_overrides.get(
            theInteraction,
            OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type,
        )
        transport = self._transportation_type_for_interaction(theInteraction)
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled and preferred is OrderType.TIMESTAMP)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.interactions_sent += 1
        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if not any(self._interaction_matches_subscription(theInteraction, subscribed) for subscribed in federate.subscribed_interactions):
                continue
            target_regions = federate.interaction_region_subscriptions.get(theInteraction, set())
            if target_regions and not self._region_sets_overlap(self.state, source_regions, federate, set(target_regions)):
                continue
            info = SupplementalReceiveInfo(producing_federate=self.state.handle, sent_regions=frozenset(source_regions))
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
                    (theInteraction, params, bytes(userSuppliedTag), OrderType.RECEIVE, transport, info),
                )
                self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_requestAttributeValueUpdateWithRegions(self, target: Any, attributesAndRegions: Iterable[Any], userSuppliedTag: bytes = b"") -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if isinstance(target, ObjectInstanceHandle):
            _owner, instance = self._find_object(target)
            if hla_mom.is_mom_object_class_name(self.engine.object_class_for_handle(instance.class_handle).name):
                raise InvalidRegionContext("DDM services shall not be used with MOM object classes")
        else:
            self._reject_mom_object_class_for_ddm(target)
        self._svc_requestAttributeValueUpdate(target, self._attributes_from_region_pairs(attributesAndRegions), userSuppliedTag)

    def _svc_getRangeBounds(self, theRegion: RegionHandle, theDimension: DimensionHandle) -> RangeBounds:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if theRegion not in self.state.regions:
            raise InvalidRegion(repr(theRegion))
        if theDimension not in self.state.regions[theRegion]:
            raise RegionDoesNotContainSpecifiedDimension(repr(theDimension))
        return self.state.region_bounds.setdefault(theRegion, {}).get(theDimension, RangeBounds(0, (1 << 63) - 1))

    def _svc_setRangeBounds(self, theRegion: RegionHandle, theDimension: DimensionHandle, theRangeBounds: RangeBounds | tuple[int, int]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if theRegion not in self.state.regions:
            raise InvalidRegion(repr(theRegion))
        if theDimension not in self.state.regions[theRegion]:
            raise RegionDoesNotContainSpecifiedDimension(repr(theDimension))
        if not isinstance(theRangeBounds, RangeBounds):
            theRangeBounds = RangeBounds(*theRangeBounds)
        lower = int(getattr(theRangeBounds, "lower", getattr(theRangeBounds, "lower_bound", 0)))
        upper = int(getattr(theRangeBounds, "upper", getattr(theRangeBounds, "upper_bound", 0)))
        if lower > upper:
            raise InvalidRangeBound(repr(theRangeBounds))
        self.state.region_bounds.setdefault(theRegion, {})[theDimension] = theRangeBounds

    def _svc_getDimensionUpperBound(self, theDimension: DimensionHandle) -> int:
        self.engine.dimension_name(theDimension)
        return (1 << 63) - 1
