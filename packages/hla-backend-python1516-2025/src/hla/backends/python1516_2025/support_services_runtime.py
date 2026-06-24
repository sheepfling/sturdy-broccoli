"""Factory/decode support helpers for the Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.handles import (
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
    InteractionClassHandleSetFactory,
    MessageRetractionHandle,
    MessageRetractionHandleFactory,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleFactory,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)


def make_attribute_handle_factory() -> AttributeHandleFactory:
    return AttributeHandleFactory()


def make_attribute_handle_set_factory() -> AttributeHandleSetFactory:
    return AttributeHandleSetFactory()


def make_attribute_handle_value_map_factory() -> AttributeHandleValueMapFactory:
    return AttributeHandleValueMapFactory()


def make_attribute_set_region_set_pair_list_factory() -> AttributeSetRegionSetPairListFactory:
    return AttributeSetRegionSetPairListFactory()


def make_dimension_handle_factory() -> DimensionHandleFactory:
    return DimensionHandleFactory()


def make_dimension_handle_set_factory() -> DimensionHandleSetFactory:
    return DimensionHandleSetFactory()


def make_federate_handle_factory() -> FederateHandleFactory:
    return FederateHandleFactory()


def make_federate_handle_set_factory() -> FederateHandleSetFactory:
    return FederateHandleSetFactory()


def make_interaction_class_handle_factory() -> InteractionClassHandleFactory:
    return InteractionClassHandleFactory()


def make_interaction_class_handle_set_factory() -> InteractionClassHandleSetFactory:
    return InteractionClassHandleSetFactory()


def make_object_class_handle_factory() -> ObjectClassHandleFactory:
    return ObjectClassHandleFactory()


def make_object_instance_handle_factory() -> ObjectInstanceHandleFactory:
    return ObjectInstanceHandleFactory()


def make_parameter_handle_factory() -> ParameterHandleFactory:
    return ParameterHandleFactory()


def make_parameter_handle_value_map_factory() -> ParameterHandleValueMapFactory:
    return ParameterHandleValueMapFactory()


def make_region_handle_factory() -> RegionHandleFactory:
    return RegionHandleFactory()


def make_region_handle_set_factory() -> RegionHandleSetFactory:
    return RegionHandleSetFactory()


def make_message_retraction_handle_factory() -> MessageRetractionHandleFactory:
    return MessageRetractionHandleFactory()


def make_transportation_type_handle_factory() -> TransportationTypeHandleFactory:
    return TransportationTypeHandleFactory()


def decode_handle(encoded_value: bytes, handle_type: type[Any], exception_type: type[Exception]) -> Any:
    try:
        return handle_type.decode(encoded_value)
    except (TypeError, ValueError) as exc:
        raise exception_type(str(exc)) from exc


def decode_federate_handle(encoded_value: bytes, exception_type: type[Exception]) -> FederateHandle:
    return decode_handle(encoded_value, FederateHandle, exception_type)


def decode_object_class_handle(encoded_value: bytes, exception_type: type[Exception]) -> ObjectClassHandle:
    return decode_handle(encoded_value, ObjectClassHandle, exception_type)


def decode_interaction_class_handle(encoded_value: bytes, exception_type: type[Exception]) -> InteractionClassHandle:
    return decode_handle(encoded_value, InteractionClassHandle, exception_type)


def decode_object_instance_handle(encoded_value: bytes, exception_type: type[Exception]) -> ObjectInstanceHandle:
    return decode_handle(encoded_value, ObjectInstanceHandle, exception_type)


def decode_attribute_handle(encoded_value: bytes, exception_type: type[Exception]) -> AttributeHandle:
    return decode_handle(encoded_value, AttributeHandle, exception_type)


def decode_parameter_handle(encoded_value: bytes, exception_type: type[Exception]) -> ParameterHandle:
    return decode_handle(encoded_value, ParameterHandle, exception_type)


def decode_dimension_handle(encoded_value: bytes, exception_type: type[Exception]) -> DimensionHandle:
    return decode_handle(encoded_value, DimensionHandle, exception_type)


def decode_message_retraction_handle(encoded_value: bytes, exception_type: type[Exception]) -> MessageRetractionHandle:
    return decode_handle(encoded_value, MessageRetractionHandle, exception_type)


def decode_region_handle(encoded_value: bytes, exception_type: type[Exception]) -> RegionHandle:
    return decode_handle(encoded_value, RegionHandle, exception_type)
