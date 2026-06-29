"""Region-state and overlap helpers for DDM services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol, cast

import hla.fom.mom as hla_mom
from hla.rti1516e.datatypes import RangeBounds
from hla.rti1516e.exceptions import (
    InvalidRegion,
    InvalidRegionContext,
    RegionNotCreatedByThisFederate,
)
from hla.rti1516e.handles import AttributeHandle, DimensionHandle, InteractionClassHandle, RegionHandle

from .state import FederateState, ObjectInstance

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederationState, PythonRTIConfig


class _DdmRegionContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: FederateState
    config: "PythonRTIConfig"

    def _require_joined(self) -> "FederationState": ...

    def _object_matches_subscription(self, actual_class: Any, subscribed_class: Any) -> bool: ...


if TYPE_CHECKING:
    class _DdmRegionMixinBase(_DdmRegionContext):
        pass
else:
    class _DdmRegionMixinBase:
        pass


class PythonRTIDdmRegionMixin(_DdmRegionMixinBase):
    """Helpers for region validation, overlap checks, and pair parsing."""

    def _reject_mom_object_class_for_ddm(self, theClass: Any) -> None:
        if hla_mom.is_mom_object_class_name(self.engine.object_class_for_handle(theClass).name):
            raise InvalidRegionContext("DDM services shall not be used with MOM object classes")

    def _reject_mom_interaction_class_for_ddm(self, theClass: InteractionClassHandle) -> None:
        if hla_mom.is_mom_interaction_class_name(self.engine.interaction_for_handle(theClass).name):
            raise InvalidRegionContext("DDM services shall not be used with MOM interaction classes")

    def _region_bounds_for(
        self,
        federate: FederateState,
        region: RegionHandle,
    ) -> dict[DimensionHandle, RangeBounds]:
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
        common_dims = set(source_federate.regions[source_region]) & set(
            target_federate.regions[target_region]
        )
        if not common_dims:
            return False
        for dimension in common_dims:
            source_bounds = self._region_bounds_for(source_federate, source_region).get(
                dimension, RangeBounds(0, (1 << 63) - 1)
            )
            target_bounds = self._region_bounds_for(target_federate, target_region).get(
                dimension, RangeBounds(0, (1 << 63) - 1)
            )
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
        if not target_regions or not source_regions:
            return True
        return any(
            self._regions_overlap_pair(
                source_federate, source_region, target_federate, target_region
            )
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
        source_region_map = instance.update_regions or self.state.update_regions.get(
            instance.handle, {}
        )
        for attr, value in reflected.items():
            target_regions = subscription.get(attr, set())
            if not target_regions:
                filtered[attr] = value
                continue
            source_regions = source_region_map.get(attr, set())
            if self._region_sets_overlap(
                self.state, set(source_regions), subscriber, set(target_regions)
            ):
                filtered[attr] = value
        return filtered

    def _attribute_region_pairs(
        self,
        attributesAndRegions: Iterable[Any],
    ) -> list[tuple[set[AttributeHandle], set[RegionHandle]]]:
        federation = self._require_joined()
        pairs: list[tuple[set[AttributeHandle], set[RegionHandle]]] = []
        for pair in attributesAndRegions or []:
            if hasattr(pair, "attributes") and hasattr(pair, "regions"):
                attrs = getattr(pair, "attributes")
                regions = getattr(pair, "regions")
            elif isinstance(pair, Mapping):
                attrs = (
                    pair.get("attributes")
                    or pair.get("attribute_handles")
                    or pair.get("attributeList")
                    or ()
                )
                regions = (
                    pair.get("regions")
                    or pair.get("region_handles")
                    or pair.get("regionSet")
                    or ()
                )
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
                    if region in federation.region_owners:
                        raise RegionNotCreatedByThisFederate(repr(region))
                    raise InvalidRegion(repr(region))
            pairs.append((attr_set, region_set))
        return pairs

    def _attributes_from_region_pairs(
        self,
        attributesAndRegions: Iterable[Any],
    ) -> set[AttributeHandle]:
        attrs: set[AttributeHandle] = set()
        for attr_set, _region_set in self._attribute_region_pairs(attributesAndRegions):
            attrs.update(attr_set)
        return attrs
