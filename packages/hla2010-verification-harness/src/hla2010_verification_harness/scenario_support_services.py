"""Shared support-service verification scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla2010.enums import CallbackModel, OrderType
from hla2010.handles import (
    AttributeHandle,
    AttributeHandleFactory,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)

from .scenario_support import register_named_object_instance


@dataclass(frozen=True)
class SupportServicesScenarioConfig:
    federation_name: str
    fom_modules: tuple[str, ...]
    logical_time_implementation_name: str
    federate_name: str = "Support"
    federate_type: str = "SupportFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    interaction_class_name: str = "HLAinteractionRoot.SmokeInteraction"
    parameter_name: str = "Message"
    object_instance_name: str = "support-object"
    include_decode_support: bool = True
    include_factory_support: bool = True
    include_order_support: bool = True
    include_transport_support: bool = True
    sample_dimension_value: int = 606
    sample_message_retraction_value: int = 707
    sample_region_value: int = 808


def run_support_factory_and_decode_scenario(
    rti: Any,
    *,
    config: SupportServicesScenarioConfig,
    federate: Any,
) -> dict[str, Any]:
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    federate_handle = rti.joinFederationExecution(
        config.federate_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(federate_handle, FederateHandle)

    object_class = rti.getObjectClassHandle(config.object_class_name)
    attribute = rti.getAttributeHandle(object_class, config.attribute_name)
    interaction_class = rti.getInteractionClassHandle(config.interaction_class_name)
    parameter = rti.getParameterHandle(interaction_class, config.parameter_name)
    rti.publishObjectClassAttributes(object_class, {attribute})
    object_instance = register_named_object_instance(
        rti,
        federate,
        object_class,
        config.object_instance_name,
    )

    lookup_summary = {
        "federate_name": rti.getFederateName(rti.getFederateHandle(config.federate_name)),
        "normalized_federate_handle": rti.normalizeFederateHandle(federate_handle),
        "object_class_name": rti.getObjectClassName(object_class),
        "attribute_name": rti.getAttributeName(object_class, attribute),
        "interaction_class_name": rti.getInteractionClassName(interaction_class),
        "parameter_name": rti.getParameterName(interaction_class, parameter),
        "object_instance_name": rti.getObjectInstanceName(object_instance),
        "object_instance_handle": rti.getObjectInstanceHandle(config.object_instance_name),
        "known_object_class": rti.getKnownObjectClassHandle(object_instance),
    }
    if config.include_order_support:
        lookup_summary.update(
            {
                "receive_order_name": rti.getOrderName(OrderType.RECEIVE),
                "timestamp_order_type": rti.getOrderType("HLAtimestamp"),
            }
        )
    if config.include_transport_support:
        lookup_summary.update(
            {
                "reliable_transport_name": rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAreliable")),
                "best_effort_transport_name": rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAbestEffort")),
                "reliable_transport_enum_name": rti.getTransportationName(rti.getTransportationType("HLAreliable")),
                "best_effort_transport_enum_name": rti.getTransportationName(rti.getTransportationType("HLAbestEffort")),
            }
        )

    factory_summary: dict[str, Any] = {}
    if config.include_factory_support:
        factory_summary = {
            "attribute_factory": rti.getAttributeHandleFactory(),
            "attribute_set_factory": rti.getAttributeHandleSetFactory(),
            "attribute_value_map_factory": rti.getAttributeHandleValueMapFactory(),
            "attribute_region_pair_list_factory": rti.getAttributeSetRegionSetPairListFactory(),
            "dimension_factory": rti.getDimensionHandleFactory(),
            "dimension_set_factory": rti.getDimensionHandleSetFactory(),
            "federate_factory": rti.getFederateHandleFactory(),
            "federate_set_factory": rti.getFederateHandleSetFactory(),
            "interaction_factory": rti.getInteractionClassHandleFactory(),
            "object_class_factory": rti.getObjectClassHandleFactory(),
            "object_instance_factory": rti.getObjectInstanceHandleFactory(),
            "parameter_factory": rti.getParameterHandleFactory(),
            "parameter_value_map_factory": rti.getParameterHandleValueMapFactory(),
            "region_set_factory": rti.getRegionHandleSetFactory(),
        }
        if config.include_transport_support:
            factory_summary["transportation_factory"] = rti.getTransportationTypeHandleFactory()

        assert isinstance(factory_summary["attribute_factory"], AttributeHandleFactory)
        assert isinstance(factory_summary["attribute_set_factory"], AttributeHandleSetFactory)
        assert isinstance(factory_summary["attribute_value_map_factory"], AttributeHandleValueMapFactory)
        assert isinstance(factory_summary["attribute_region_pair_list_factory"], AttributeSetRegionSetPairListFactory)
        assert isinstance(factory_summary["dimension_factory"], DimensionHandleFactory)
        assert isinstance(factory_summary["dimension_set_factory"], DimensionHandleSetFactory)
        assert isinstance(factory_summary["federate_factory"], FederateHandleFactory)
        assert isinstance(factory_summary["federate_set_factory"], FederateHandleSetFactory)
        assert isinstance(factory_summary["interaction_factory"], InteractionClassHandleFactory)
        assert isinstance(factory_summary["object_class_factory"], ObjectClassHandleFactory)
        assert isinstance(factory_summary["object_instance_factory"], ObjectInstanceHandleFactory)
        assert isinstance(factory_summary["parameter_factory"], ParameterHandleFactory)
        assert isinstance(factory_summary["parameter_value_map_factory"], ParameterHandleValueMapFactory)
        assert isinstance(factory_summary["region_set_factory"], RegionHandleSetFactory)
        if config.include_transport_support:
            assert isinstance(factory_summary["transportation_factory"], TransportationTypeHandleFactory)

    sample_dimension = DimensionHandle(config.sample_dimension_value)
    sample_region = RegionHandle(config.sample_region_value)
    sample_retraction = MessageRetractionHandle(config.sample_message_retraction_value)

    decoded_summary: dict[str, Any] = {}
    if config.include_decode_support:
        decoded_summary = {
            "federate_handle": rti.decodeFederateHandle(federate_handle.encode()),
            "object_class_handle": rti.decodeObjectClassHandle(object_class.encode()),
            "interaction_class_handle": rti.decodeInteractionClassHandle(interaction_class.encode()),
            "object_instance_handle": rti.decodeObjectInstanceHandle(object_instance.encode()),
            "attribute_handle": rti.decodeAttributeHandle(attribute.encode()),
            "parameter_handle": rti.decodeParameterHandle(parameter.encode()),
            "dimension_handle": rti.decodeDimensionHandle(sample_dimension.encode()),
            "message_retraction_handle": rti.decodeMessageRetractionHandle(sample_retraction.encode()),
            "region_handle": rti.decodeRegionHandle(sample_region.encode()),
        }

        assert decoded_summary["federate_handle"] == federate_handle
        assert decoded_summary["object_class_handle"] == object_class
        assert decoded_summary["interaction_class_handle"] == interaction_class
        assert decoded_summary["object_instance_handle"] == object_instance
        assert decoded_summary["attribute_handle"] == attribute
        assert decoded_summary["parameter_handle"] == parameter
        assert decoded_summary["dimension_handle"] == sample_dimension
        assert decoded_summary["message_retraction_handle"] == sample_retraction
        assert decoded_summary["region_handle"] == sample_region

    return {
        "federate_handle": federate_handle,
        "object_class": object_class,
        "attribute": attribute,
        "interaction_class": interaction_class,
        "parameter": parameter,
        "object_instance": object_instance,
        "lookup_summary": lookup_summary,
        "factory_summary": factory_summary,
        "decoded_summary": decoded_summary,
    }


__all__ = [
    "SupportServicesScenarioConfig",
    "run_support_factory_and_decode_scenario",
]
