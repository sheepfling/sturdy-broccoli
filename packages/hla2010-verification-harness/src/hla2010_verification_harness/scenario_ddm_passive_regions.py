"""Passive DDM region subscription verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.handles import AttributeHandleSet, RegionHandleSet
from hla2010.types import AttributeRegionAssociation, RangeBounds

from .scenario_support import drain_callbacks_pair


@dataclass(frozen=True)
class DdmPassiveRegionScenarioConfig:
    federation_name: str = "DdmPassiveRegionFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "DdmPassiveRegionFederate"
    object_class_name: str = "HLAobjectRoot.Target"
    attribute_name: str = "Position"
    interaction_class_name: str = "HLAinteractionRoot.TrackReport"
    parameter_name: str = "TrackId"
    object_instance_name: str = "DDM-Passive-Object"
    publish_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(10, 20))
    subscribe_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(15, 25))
    interaction_payload: bytes = b"passive-match"
    interaction_tag: bytes = b"passive-ddm"


def run_ddm_passive_region_subscription_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DdmPassiveRegionScenarioConfig,
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

    subscriber_rti.subscribeObjectClassAttributesPassivelyWithRegions(subscriber_class, subscription_pairs)
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

    publisher_rti.publishInteractionClass(publisher_interaction)
    subscriber_rti.subscribeInteractionClassPassivelyWithRegions(subscriber_interaction, {subscriber_region})
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
    assert publisher_federate.last_callback("provideAttributeValueUpdate") is None

    subscriber_rti.unsubscribeObjectClassAttributesWithRegions(subscriber_class, subscription_pairs)
    subscriber_rti.unsubscribeInteractionClassWithRegions(subscriber_interaction, {subscriber_region})

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
        "received": received,
    }


__all__ = [
    "DdmPassiveRegionScenarioConfig",
    "run_ddm_passive_region_subscription_scenario",
]
