"""Shared support-service verification scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla.rti1516e.enums import CallbackModel, OrderType
from hla.rti1516e.handles import (
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
    rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    federate_handle = rti.join_federation_execution(
        config.federate_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(federate_handle, FederateHandle)

    object_class = rti.get_object_class_handle(config.object_class_name)
    attribute = rti.get_attribute_handle(object_class, config.attribute_name)
    interaction_class = rti.get_interaction_class_handle(config.interaction_class_name)
    parameter = rti.get_parameter_handle(interaction_class, config.parameter_name)
    rti.publish_object_class_attributes(object_class, {attribute})
    object_instance = register_named_object_instance(
        rti,
        federate,
        object_class,
        config.object_instance_name,
    )

    lookup_summary = {
        "federate_name": rti.get_federate_name(rti.get_federate_handle(config.federate_name)),
        "normalized_federate_handle": rti.normalize_federate_handle(federate_handle),
        "object_class_name": rti.get_object_class_name(object_class),
        "attribute_name": rti.get_attribute_name(object_class, attribute),
        "interaction_class_name": rti.get_interaction_class_name(interaction_class),
        "parameter_name": rti.get_parameter_name(interaction_class, parameter),
        "object_instance_name": rti.get_object_instance_name(object_instance),
        "object_instance_handle": rti.get_object_instance_handle(config.object_instance_name),
        "known_object_class": rti.get_known_object_class_handle(object_instance),
    }
    if config.include_order_support:
        lookup_summary.update(
            {
                "receive_order_name": rti.get_order_name(OrderType.RECEIVE),
                "timestamp_order_type": rti.get_order_type("HLAtimestamp"),
            }
        )
    if config.include_transport_support:
        lookup_summary.update(
            {
                "reliable_transport_name": rti.get_transportation_type_name(rti.get_transportation_type_handle("HLAreliable")),
                "best_effort_transport_name": rti.get_transportation_type_name(rti.get_transportation_type_handle("HLAbestEffort")),
                "reliable_transport_enum_name": rti.get_transportation_name(rti.get_transportation_type("HLAreliable")),
                "best_effort_transport_enum_name": rti.get_transportation_name(rti.get_transportation_type("HLAbestEffort")),
            }
        )

    factory_summary: dict[str, Any] = {}
    if config.include_factory_support:
        factory_summary = {
            "attribute_factory": rti.get_attribute_handle_factory(),
            "attribute_set_factory": rti.get_attribute_handle_set_factory(),
            "attribute_value_map_factory": rti.get_attribute_handle_value_map_factory(),
            "attribute_region_pair_list_factory": rti.get_attribute_set_region_set_pair_list_factory(),
            "dimension_factory": rti.get_dimension_handle_factory(),
            "dimension_set_factory": rti.get_dimension_handle_set_factory(),
            "federate_factory": rti.get_federate_handle_factory(),
            "federate_set_factory": rti.get_federate_handle_set_factory(),
            "interaction_factory": rti.get_interaction_class_handle_factory(),
            "object_class_factory": rti.get_object_class_handle_factory(),
            "object_instance_factory": rti.get_object_instance_handle_factory(),
            "parameter_factory": rti.get_parameter_handle_factory(),
            "parameter_value_map_factory": rti.get_parameter_handle_value_map_factory(),
            "region_set_factory": rti.get_region_handle_set_factory(),
        }
        if config.include_transport_support:
            factory_summary["transportation_factory"] = rti.get_transportation_type_handle_factory()

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
            "federate_handle": rti.decode_federate_handle(federate_handle.encode()),
            "object_class_handle": rti.decode_object_class_handle(object_class.encode()),
            "interaction_class_handle": rti.decode_interaction_class_handle(interaction_class.encode()),
            "object_instance_handle": rti.decode_object_instance_handle(object_instance.encode()),
            "attribute_handle": rti.decode_attribute_handle(attribute.encode()),
            "parameter_handle": rti.decode_parameter_handle(parameter.encode()),
            "dimension_handle": rti.decode_dimension_handle(sample_dimension.encode()),
            "message_retraction_handle": rti.decode_message_retraction_handle(sample_retraction.encode()),
            "region_handle": rti.decode_region_handle(sample_region.encode()),
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
