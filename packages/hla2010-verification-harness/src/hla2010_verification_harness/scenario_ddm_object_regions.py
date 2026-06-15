"""DDM object-region lifecycle verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.handles import AttributeHandleSet, RegionHandleSet
from hla2010.types import AttributeRegionAssociation, RangeBounds

from .scenario_support import drain_callbacks_pair


@dataclass(frozen=True)
class DdmObjectRegionLifecycleScenarioConfig:
    federation_name: str = "DdmObjectRegionLifecycleFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "DdmObjectRegionFederate"
    object_class_name: str = "HLAobjectRoot.Target"
    attribute_name: str = "Position"
    interaction_class_name: str = "HLAinteractionRoot.TrackReport"
    parameter_name: str = "TrackId"
    object_instance_name: str = "DDM-Region-Object"
    publish_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(10, 20))
    subscribe_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(15, 25))
    interaction_payload: bytes = b"match"
    interaction_tag: bytes = b"ddm-match"
    interaction_after_unsubscribe_payload: bytes = b"after-unsub"
    interaction_after_unsubscribe_tag: bytes = b"ddm-after-unsub"
    request_tag: bytes = b"refresh-ddm"


@dataclass(frozen=True)
class DdmDeclarationGatingScenarioConfig:
    federation_name: str = "DdmDeclarationGatingFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "DdmDeclarationGatingFederate"
    object_class_name: str = "HLAobjectRoot.Target"
    attribute_name: str = "Position"
    interaction_class_name: str = "HLAinteractionRoot.TrackReport"
    parameter_name: str = "TrackId"
    object_instance_name: str = "DDM-Declaration-Gating-Object"
    region_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(10, 20))
    pre_subscription_attribute_payload: bytes = b"before-subscription"
    pre_subscription_update_tag: bytes = b"ddm-before-update"
    pre_subscription_interaction_payload: bytes = b"before-subscription"
    pre_subscription_interaction_tag: bytes = b"ddm-before-interaction"
    post_subscription_attribute_payload: bytes = b"after-subscription"
    post_subscription_update_tag: bytes = b"ddm-after-update"
    post_subscription_interaction_payload: bytes = b"after-subscription"
    post_subscription_interaction_tag: bytes = b"ddm-after-interaction"


def run_ddm_object_region_lifecycle_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DdmObjectRegionLifecycleScenarioConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.joinFederationExecution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_handle = subscriber_rti.joinFederationExecution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )

    publisher_class = publisher_rti.getObjectClassHandle(config.object_class_name)
    subscriber_class = subscriber_rti.getObjectClassHandle(config.object_class_name)
    publisher_attribute = publisher_rti.getAttributeHandle(publisher_class, config.attribute_name)
    subscriber_attribute = subscriber_rti.getAttributeHandle(subscriber_class, config.attribute_name)
    publisher_dimension = publisher_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    subscriber_dimension = subscriber_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    publisher_interaction = publisher_rti.getInteractionClassHandle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.getInteractionClassHandle(config.interaction_class_name)
    publisher_parameter = publisher_rti.getParameterHandle(publisher_interaction, config.parameter_name)
    subscriber_parameter = subscriber_rti.getParameterHandle(subscriber_interaction, config.parameter_name)

    publisher_region = publisher_rti.createRegion({publisher_dimension})
    subscriber_region = subscriber_rti.createRegion({subscriber_dimension})
    publisher_rti.setRangeBounds(publisher_region, publisher_dimension, config.publish_bounds)
    subscriber_rti.setRangeBounds(subscriber_region, subscriber_dimension, config.subscribe_bounds)
    publisher_rti.commitRegionModifications({publisher_region})
    subscriber_rti.commitRegionModifications({subscriber_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({publisher_attribute}), RegionHandleSet({publisher_region}))]
    subscription_pairs = [
        AttributeRegionAssociation(AttributeHandleSet({subscriber_attribute}), RegionHandleSet({subscriber_region}))
    ]

    subscriber_rti.subscribeObjectClassAttributesWithRegions(subscriber_class, subscription_pairs)
    publisher_rti.publishObjectClassAttributes(publisher_class, {publisher_attribute})
    object_instance = publisher_rti.registerObjectInstanceWithRegions(
        publisher_class,
        update_pairs,
        config.object_instance_name,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    discovery = subscriber_federate.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == object_instance
    assert discovery.args[1] == subscriber_class

    publisher_rti.unassociateRegionsForUpdates(object_instance, update_pairs)
    publisher_rti.associateRegionsForUpdates(object_instance, update_pairs)

    publisher_federate.clear()
    subscriber_rti.requestAttributeValueUpdateWithRegions(object_instance, subscription_pairs, config.request_tag)
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)
    provide = publisher_federate.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args[0] == object_instance
    assert provide.args[2] == config.request_tag

    publisher_rti.publishInteractionClass(publisher_interaction)
    subscriber_rti.subscribeInteractionClassWithRegions(subscriber_interaction, {subscriber_region})
    publisher_federate.clear()
    subscriber_federate.clear()
    publisher_rti.sendInteractionWithRegions(
        publisher_interaction,
        {publisher_parameter: config.interaction_payload},
        {publisher_region},
        config.interaction_tag,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)
    received = subscriber_federate.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == subscriber_interaction
    assert received.args[1] == {subscriber_parameter: config.interaction_payload}

    subscriber_federate.clear()
    subscriber_rti.unsubscribeInteractionClassWithRegions(subscriber_interaction, {subscriber_region})
    publisher_rti.sendInteractionWithRegions(
        publisher_interaction,
        {publisher_parameter: config.interaction_after_unsubscribe_payload},
        {publisher_region},
        config.interaction_after_unsubscribe_tag,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)
    suppressed_receive = subscriber_federate.last_callback("receiveInteraction")
    assert suppressed_receive is None

    subscriber_rti.unsubscribeObjectClassAttributesWithRegions(subscriber_class, subscription_pairs)
    publisher_rti.deleteRegion(publisher_region)
    subscriber_rti.deleteRegion(subscriber_region)

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attribute,
        "subscriber_attribute": subscriber_attribute,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_parameter,
        "subscriber_parameter": subscriber_parameter,
        "publisher_region": publisher_region,
        "subscriber_region": subscriber_region,
        "update_pairs": update_pairs,
        "subscription_pairs": subscription_pairs,
        "object_instance": object_instance,
        "discovery": discovery,
        "provide": provide,
        "received": received,
        "suppressed_receive": suppressed_receive,
    }


def run_ddm_declaration_gating_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DdmDeclarationGatingScenarioConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.joinFederationExecution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_handle = subscriber_rti.joinFederationExecution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )

    publisher_class = publisher_rti.getObjectClassHandle(config.object_class_name)
    subscriber_class = subscriber_rti.getObjectClassHandle(config.object_class_name)
    publisher_attribute = publisher_rti.getAttributeHandle(publisher_class, config.attribute_name)
    subscriber_attribute = subscriber_rti.getAttributeHandle(subscriber_class, config.attribute_name)
    publisher_dimension = publisher_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    subscriber_dimension = subscriber_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    publisher_interaction = publisher_rti.getInteractionClassHandle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.getInteractionClassHandle(config.interaction_class_name)
    publisher_parameter = publisher_rti.getParameterHandle(publisher_interaction, config.parameter_name)
    subscriber_parameter = subscriber_rti.getParameterHandle(subscriber_interaction, config.parameter_name)

    publisher_region = publisher_rti.createRegion({publisher_dimension})
    subscriber_region = subscriber_rti.createRegion({subscriber_dimension})
    publisher_rti.setRangeBounds(publisher_region, publisher_dimension, config.region_bounds)
    subscriber_rti.setRangeBounds(subscriber_region, subscriber_dimension, config.region_bounds)
    publisher_rti.commitRegionModifications({publisher_region})
    subscriber_rti.commitRegionModifications({subscriber_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({publisher_attribute}), RegionHandleSet({publisher_region}))]
    subscription_pairs = [
        AttributeRegionAssociation(AttributeHandleSet({subscriber_attribute}), RegionHandleSet({subscriber_region}))
    ]

    publisher_rti.publishObjectClassAttributes(publisher_class, {publisher_attribute})
    publisher_rti.publishInteractionClass(publisher_interaction)
    object_instance = publisher_rti.registerObjectInstanceWithRegions(
        publisher_class,
        update_pairs,
        config.object_instance_name,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    discovery_before_subscription = subscriber_federate.last_callback("discoverObjectInstance")
    assert discovery_before_subscription is None

    publisher_rti.updateAttributeValues(
        object_instance,
        {publisher_attribute: config.pre_subscription_attribute_payload},
        config.pre_subscription_update_tag,
    )
    publisher_rti.sendInteractionWithRegions(
        publisher_interaction,
        {publisher_parameter: config.pre_subscription_interaction_payload},
        {publisher_region},
        config.pre_subscription_interaction_tag,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    reflection_before_subscription = subscriber_federate.last_callback("reflectAttributeValues")
    interaction_before_subscription = subscriber_federate.last_callback("receiveInteraction")
    assert reflection_before_subscription is None
    assert interaction_before_subscription is None

    subscriber_rti.subscribeObjectClassAttributesWithRegions(subscriber_class, subscription_pairs)
    subscriber_rti.subscribeInteractionClassWithRegions(subscriber_interaction, {subscriber_region})
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    discovery_after_subscription = subscriber_federate.last_callback("discoverObjectInstance")
    assert discovery_after_subscription is not None
    assert discovery_after_subscription.args[0] == object_instance
    assert discovery_after_subscription.args[1] == subscriber_class
    subscriber_federate.clear()

    publisher_rti.updateAttributeValues(
        object_instance,
        {publisher_attribute: config.post_subscription_attribute_payload},
        config.post_subscription_update_tag,
    )
    publisher_rti.sendInteractionWithRegions(
        publisher_interaction,
        {publisher_parameter: config.post_subscription_interaction_payload},
        {publisher_region},
        config.post_subscription_interaction_tag,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    reflection_after_subscription = subscriber_federate.last_callback("reflectAttributeValues")
    interaction_after_subscription = subscriber_federate.last_callback("receiveInteraction")
    assert reflection_after_subscription is not None
    assert reflection_after_subscription.args[0] == object_instance
    assert reflection_after_subscription.args[1] == {subscriber_attribute: config.post_subscription_attribute_payload}
    assert interaction_after_subscription is not None
    assert interaction_after_subscription.args[0] == subscriber_interaction
    assert interaction_after_subscription.args[1] == {subscriber_parameter: config.post_subscription_interaction_payload}

    subscriber_rti.unsubscribeObjectClassAttributesWithRegions(subscriber_class, subscription_pairs)
    subscriber_rti.unsubscribeInteractionClassWithRegions(subscriber_interaction, {subscriber_region})
    publisher_rti.deleteRegion(publisher_region)
    subscriber_rti.deleteRegion(subscriber_region)

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attribute,
        "subscriber_attribute": subscriber_attribute,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_parameter,
        "subscriber_parameter": subscriber_parameter,
        "publisher_region": publisher_region,
        "subscriber_region": subscriber_region,
        "update_pairs": update_pairs,
        "subscription_pairs": subscription_pairs,
        "object_instance": object_instance,
        "discovery_before_subscription": discovery_before_subscription,
        "reflection_before_subscription": reflection_before_subscription,
        "interaction_before_subscription": interaction_before_subscription,
        "discovery_after_subscription": discovery_after_subscription,
        "reflection_after_subscription": reflection_after_subscription,
        "interaction_after_subscription": interaction_after_subscription,
    }


__all__ = [
    "DdmDeclarationGatingScenarioConfig",
    "DdmObjectRegionLifecycleScenarioConfig",
    "run_ddm_declaration_gating_scenario",
    "run_ddm_object_region_lifecycle_scenario",
]
