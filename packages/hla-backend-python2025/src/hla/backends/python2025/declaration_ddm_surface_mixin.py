"""Declaration, interaction subscription, DDM, and naming surface wrappers."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.datatypes import RangeBounds
from hla.rti1516_2025.handles import DimensionHandle, ObjectInstanceHandle, RegionHandle

from .declaration_management_runtime import (
    publish_object_class_attributes,
    release_multiple_object_instance_names,
    release_object_instance_name,
    reserve_multiple_object_instance_names,
    reserve_object_instance_name,
    subscribe_object_class_attributes,
    unpublish_object_class,
    unpublish_object_class_attributes,
    unsubscribe_object_class,
    unsubscribe_object_class_attributes,
)
from .input_guard_runtime import normalize_object_class_subscription_args
from .interaction_runtime import (
    change_interaction_order_type,
    publish_interaction_class,
    publish_object_class_directed_interactions,
    subscribe_interaction_class,
    subscribe_interaction_class_with_regions,
    subscribe_object_class_directed_interactions,
    unpublish_interaction_class,
    unpublish_object_class_directed_interactions,
    unsubscribe_interaction_class,
    unsubscribe_interaction_class_with_regions,
    unsubscribe_object_class_directed_interactions,
)
from .object_region_runtime import (
    associate_regions_for_updates,
    change_attribute_order_type,
    change_default_attribute_order_type,
    change_default_attribute_transportation_type,
    commit_region_modifications,
    create_region,
    delete_region,
    get_dimension_handle_set,
    get_range_bounds,
    register_object_instance_with_regions,
    set_range_bounds,
    subscribe_object_class_attributes_with_regions,
    unassociate_regions_for_updates,
    unsubscribe_object_class_attributes_with_regions,
)


class DeclarationDdmSurfaceMixin:
    """Move mechanical declaration and DDM wrappers out of the ambassador body."""

    def publishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("publishObjectClassAttributes", objectClass, attributes)
        self._require_joined("publishObjectClassAttributes")
        publish_object_class_attributes(self, objectClass, attributes)

    def unpublishObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClass", objectClass)
        self._require_joined("unpublishObjectClass")
        unpublish_object_class(self, objectClass)

    def unpublishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClassAttributes", objectClass, attributes)
        self._require_joined("unpublishObjectClassAttributes")
        unpublish_object_class_attributes(self, objectClass, attributes)

    @staticmethod
    def _normalize_object_class_subscription_args(object_class=None, attributes=None, **kwargs):  # noqa: ANN001, ANN205
        return normalize_object_class_subscription_args(object_class=object_class, attributes=attributes, **kwargs)

    def subscribeObjectClassAttributes(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributes", objectClass, attributes, *unused)
        self._require_joined("subscribeObjectClassAttributes")
        subscribe_object_class_attributes(self, objectClass, attributes, *unused)

    def subscribeObjectClassAttributesPassively(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassively", objectClass, attributes, *unused)
        self.subscribeObjectClassAttributes(objectClass, attributes, *unused)

    def unsubscribeObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClass", objectClass)
        self._require_joined("unsubscribeObjectClass")
        unsubscribe_object_class(self, objectClass)

    def unsubscribeObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributes", objectClass, attributes)
        self._require_joined("unsubscribeObjectClassAttributes")
        unsubscribe_object_class_attributes(self, objectClass, attributes)

    def subscribe_object_class_attributes(self, object_class=None, attributes=None, *args, **kwargs) -> None:  # noqa: ANN001
        update_rate_designator = kwargs.pop("update_rate_designator", None)
        object_class, attributes = self._normalize_object_class_subscription_args(
            object_class=object_class,
            attributes=attributes,
            **kwargs,
        )
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        self.subscribeObjectClassAttributes(object_class, attributes, *args)

    def subscribe_object_class_attributes_passively(self, object_class=None, attributes=None, *args, **kwargs) -> None:  # noqa: ANN001
        update_rate_designator = kwargs.pop("update_rate_designator", None)
        object_class, attributes = self._normalize_object_class_subscription_args(
            object_class=object_class,
            attributes=attributes,
            **kwargs,
        )
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        self.subscribeObjectClassAttributesPassively(object_class, attributes, *args)

    def unsubscribe_object_class_attributes(self, object_class=None, attributes=None, **kwargs) -> None:  # noqa: ANN001
        object_class, attributes = self._normalize_object_class_subscription_args(
            object_class=object_class,
            attributes=attributes,
            **kwargs,
        )
        self.unsubscribeObjectClassAttributes(object_class, attributes)

    def publishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("publishInteractionClass", interactionClass)
        self._require_joined("publishInteractionClass")
        publish_interaction_class(self, interactionClass)

    def unpublishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unpublishInteractionClass", interactionClass)
        self._require_joined("unpublishInteractionClass")
        unpublish_interaction_class(self, interactionClass)

    def subscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClass", interactionClass)
        self._require_joined("subscribeInteractionClass")
        subscribe_interaction_class(self, interactionClass)

    def subscribeInteractionClassPassively(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassively", interactionClass)
        self.subscribeInteractionClass(interactionClass)

    def unsubscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClass", interactionClass)
        self._require_joined("unsubscribeInteractionClass")
        unsubscribe_interaction_class(self, interactionClass)

    def subscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("subscribeInteractionClassWithRegions")
        subscribe_interaction_class_with_regions(self, interactionClass, regions)

    def subscribeInteractionClassPassivelyWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassivelyWithRegions", interactionClass, regions)
        self.subscribeInteractionClassWithRegions(interactionClass, regions)

    def unsubscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("unsubscribeInteractionClassWithRegions")
        unsubscribe_interaction_class_with_regions(self, interactionClass, regions)

    def publishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("publishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("publishObjectClassDirectedInteractions")
        publish_object_class_directed_interactions(self, objectClass, interactionClasses)

    def unpublishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unpublishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unpublishObjectClassDirectedInteractions")
        unpublish_object_class_directed_interactions(self, objectClass, interactionClasses)

    def subscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("subscribeObjectClassDirectedInteractions")
        subscribe_object_class_directed_interactions(self, objectClass, interactionClasses)

    def subscribeObjectClassDirectedInteractionsUniversally(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractionsUniversally", objectClass, interactionClasses)
        self.subscribeObjectClassDirectedInteractions(objectClass, interactionClasses)

    def unsubscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unsubscribeObjectClassDirectedInteractions")
        unsubscribe_object_class_directed_interactions(self, objectClass, interactionClasses)

    def createRegion(self, dimensions: Any) -> RegionHandle:  # noqa: N802
        self._record("createRegion", dimensions)
        self._require_joined("createRegion")
        return create_region(self, dimensions)

    def commitRegionModifications(self, regions: Any) -> None:  # noqa: N802
        self._record("commitRegionModifications", regions)
        self._require_joined("commitRegionModifications")
        commit_region_modifications(self, regions)

    def deleteRegion(self, region: Any) -> None:  # noqa: N802
        self._record("deleteRegion", region)
        self._require_joined("deleteRegion")
        delete_region(self, region)

    def getDimensionHandleSet(self, region: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getDimensionHandleSet", region)
        return get_dimension_handle_set(self, region)

    def getRangeBounds(self, region: Any, dimension: Any) -> RangeBounds:  # noqa: N802
        self._record("getRangeBounds", region, dimension)
        return get_range_bounds(self, region, dimension)

    def setRangeBounds(self, region: Any, dimension: Any, rangeBounds: Any) -> None:  # noqa: N802
        self._record("setRangeBounds", region, dimension, rangeBounds)
        set_range_bounds(self, region, dimension, rangeBounds)

    def subscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions, *unused)
        self._require_joined("subscribeObjectClassAttributesWithRegions")
        subscribe_object_class_attributes_with_regions(self, objectClass, attributesAndRegions)

    def subscribeObjectClassAttributesPassivelyWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassivelyWithRegions", objectClass, attributesAndRegions, *unused)
        self.subscribeObjectClassAttributesWithRegions(objectClass, attributesAndRegions, *unused)

    def unsubscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions)
        self._require_joined("unsubscribeObjectClassAttributesWithRegions")
        unsubscribe_object_class_attributes_with_regions(self, objectClass, attributesAndRegions)

    def registerObjectInstanceWithRegions(self, objectClass: Any, attributesAndRegions: Any, objectInstanceName: str | None = None) -> ObjectInstanceHandle:  # noqa: N802
        self._record("registerObjectInstanceWithRegions", objectClass, attributesAndRegions, objectInstanceName)
        return register_object_instance_with_regions(self, objectClass, attributesAndRegions, objectInstanceName)

    def associateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("associateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("associateRegionsForUpdates")
        associate_regions_for_updates(self, objectInstance, attributesAndRegions)

    def unassociateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unassociateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("unassociateRegionsForUpdates")
        unassociate_regions_for_updates(self, objectInstance, attributesAndRegions)

    def changeDefaultAttributeTransportationType(  # noqa: N802
        self,
        objectClass: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("changeDefaultAttributeTransportationType", objectClass, attributes, transportationType)
        change_default_attribute_transportation_type(self, objectClass, attributes, transportationType)

    def changeDefaultAttributeOrderType(self, objectClass: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeDefaultAttributeOrderType", objectClass, attributes, orderType)
        change_default_attribute_order_type(self, objectClass, attributes, orderType)

    def changeAttributeOrderType(self, objectInstance: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeAttributeOrderType", objectInstance, attributes, orderType)
        self._require_joined("changeAttributeOrderType")
        change_attribute_order_type(self, objectInstance, attributes, orderType)

    def changeInteractionOrderType(self, interactionClass: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeInteractionOrderType", interactionClass, orderType)
        self._require_joined("changeInteractionOrderType")
        change_interaction_order_type(self, interactionClass, orderType)

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("reserveObjectInstanceName", objectInstanceName)
        self._require_joined("reserveObjectInstanceName")
        self._require_no_save_or_restore("reserveObjectInstanceName")
        reserve_object_instance_name(self, objectInstanceName)

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("releaseObjectInstanceName", objectInstanceName)
        self._require_joined("releaseObjectInstanceName")
        self._require_no_save_or_restore("releaseObjectInstanceName")
        release_object_instance_name(self, objectInstanceName)

    def reserveMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("reserveMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("reserveMultipleObjectInstanceNames")
        self._require_no_save_or_restore("reserveMultipleObjectInstanceNames")
        reserve_multiple_object_instance_names(self, objectInstanceNames)

    def releaseMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("releaseMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("releaseMultipleObjectInstanceNames")
        self._require_no_save_or_restore("releaseMultipleObjectInstanceNames")
        release_multiple_object_instance_names(self, objectInstanceNames)

    def reserve_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self.reserveMultipleObjectInstanceNames(object_instance_names)

    def release_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self.releaseMultipleObjectInstanceNames(object_instance_names)

    def reserve_multiple_object_instance_names(self, object_instance_names: Any) -> None:
        self.reserveMultipleObjectInstanceNames(object_instance_names)

    def release_multiple_object_instance_names(self, object_instance_names: Any) -> None:
        self.releaseMultipleObjectInstanceNames(object_instance_names)
