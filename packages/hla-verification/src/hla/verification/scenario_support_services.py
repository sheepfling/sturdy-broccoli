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
    MessageRetractionHandleFactory,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandleFactory,
    RegionHandle,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)

from .scenario_support import register_named_object_instance
from .scenario_support import safe_evoke_callback
from .scenario_support import safe_evoke_multiple_callbacks
from .startup import drain_callbacks


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


@dataclass(frozen=True)
class CallbackControlScenarioConfig:
    federation_name: str
    fom_modules: tuple[str, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "SupportFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "callback-object"
    first_payload: bytes = b"one"
    first_tag: bytes = b"queued-one"
    second_payload: bytes = b"two"
    second_tag: bytes = b"queued-two"
    third_payload: bytes = b"three"
    third_tag: bytes = b"queued-three"


def _invoke_rti_method(rti: Any, snake_name: str, camel_name: str, *args: Any) -> Any:
    method = getattr(rti, snake_name, None)
    if callable(method):
        return method(*args)
    method = getattr(rti, camel_name)
    return method(*args)


def _enable_callbacks(rti: Any) -> None:
    _invoke_rti_method(rti, "enable_callbacks", "enableCallbacks")


def _disable_callbacks(rti: Any) -> None:
    _invoke_rti_method(rti, "disable_callbacks", "disableCallbacks")


def _evoke_callback(rti: Any, minimum_seconds: float) -> bool:
    method = getattr(rti, "evoke_callback", None)
    if callable(method):
        return safe_evoke_callback(rti, minimum_seconds)
    return bool(_invoke_rti_method(rti, "evoke_callback", "evokeCallback", minimum_seconds))


def _evoke_multiple_callbacks(rti: Any, minimum_seconds: float, maximum_seconds: float) -> bool:
    method = getattr(rti, "evoke_multiple_callbacks", None)
    if callable(method):
        return safe_evoke_multiple_callbacks(rti, minimum_seconds, maximum_seconds)
    return bool(
        _invoke_rti_method(
            rti,
            "evoke_multiple_callbacks",
            "evokeMultipleCallbacks",
            minimum_seconds,
            maximum_seconds,
        )
    )


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
            "attribute_factory": _invoke_rti_method(rti, "get_attribute_handle_factory", "getAttributeHandleFactory"),
            "attribute_set_factory": _invoke_rti_method(
                rti,
                "get_attribute_handle_set_factory",
                "getAttributeHandleSetFactory",
            ),
            "attribute_value_map_factory": _invoke_rti_method(
                rti,
                "get_attribute_handle_value_map_factory",
                "getAttributeHandleValueMapFactory",
            ),
            "attribute_region_pair_list_factory": _invoke_rti_method(
                rti,
                "get_attribute_set_region_set_pair_list_factory",
                "getAttributeSetRegionSetPairListFactory",
            ),
            "dimension_factory": _invoke_rti_method(rti, "get_dimension_handle_factory", "getDimensionHandleFactory"),
            "dimension_set_factory": _invoke_rti_method(
                rti,
                "get_dimension_handle_set_factory",
                "getDimensionHandleSetFactory",
            ),
            "federate_factory": _invoke_rti_method(rti, "get_federate_handle_factory", "getFederateHandleFactory"),
            "federate_set_factory": _invoke_rti_method(
                rti,
                "get_federate_handle_set_factory",
                "getFederateHandleSetFactory",
            ),
            "interaction_factory": _invoke_rti_method(
                rti,
                "get_interaction_class_handle_factory",
                "getInteractionClassHandleFactory",
            ),
            "object_class_factory": _invoke_rti_method(
                rti,
                "get_object_class_handle_factory",
                "getObjectClassHandleFactory",
            ),
            "object_instance_factory": _invoke_rti_method(
                rti,
                "get_object_instance_handle_factory",
                "getObjectInstanceHandleFactory",
            ),
            "parameter_factory": _invoke_rti_method(rti, "get_parameter_handle_factory", "getParameterHandleFactory"),
            "parameter_value_map_factory": _invoke_rti_method(
                rti,
                "get_parameter_handle_value_map_factory",
                "getParameterHandleValueMapFactory",
            ),
            "region_factory": _invoke_rti_method(rti, "get_region_handle_factory", "getRegionHandleFactory"),
            "region_set_factory": _invoke_rti_method(
                rti,
                "get_region_handle_set_factory",
                "getRegionHandleSetFactory",
            ),
            "message_retraction_factory": _invoke_rti_method(
                rti,
                "get_message_retraction_handle_factory",
                "getMessageRetractionHandleFactory",
            ),
        }
        if config.include_transport_support:
            factory_summary["transportation_factory"] = _invoke_rti_method(
                rti,
                "get_transportation_type_handle_factory",
                "getTransportationTypeHandleFactory",
            )

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
        assert isinstance(factory_summary["region_factory"], RegionHandleFactory)
        assert isinstance(factory_summary["region_set_factory"], RegionHandleSetFactory)
        assert isinstance(factory_summary["message_retraction_factory"], MessageRetractionHandleFactory)
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


def run_callback_control_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: CallbackControlScenarioConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_rti.join_federation_execution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )

    object_class = publisher_rti.get_object_class_handle(config.object_class_name)
    attribute = publisher_rti.get_attribute_handle(object_class, config.attribute_name)
    subscriber_object_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    subscriber_attribute = subscriber_rti.get_attribute_handle(subscriber_object_class, config.attribute_name)
    publisher_rti.publish_object_class_attributes(object_class, {attribute})
    subscriber_rti.subscribe_object_class_attributes(subscriber_object_class, {subscriber_attribute})

    object_instance = register_named_object_instance(
        publisher_rti,
        publisher_federate,
        object_class,
        config.object_instance_name,
    )
    initial_discovery = subscriber_federate.last_callback("discoverObjectInstance")
    if hasattr(subscriber_federate, "clear"):
        subscriber_federate.clear()
    _disable_callbacks(subscriber_rti)
    publisher_rti.update_attribute_values(object_instance, {attribute: config.first_payload}, config.first_tag)
    first_queued_while_disabled = (
        subscriber_federate.last_callback("discoverObjectInstance") is None
        and subscriber_federate.last_callback("reflectAttributeValues") is None
    )
    assert first_queued_while_disabled
    first_evoke = _evoke_callback(subscriber_rti, 0.0)
    assert first_evoke is False

    _enable_callbacks(subscriber_rti)
    second_evoke = _evoke_callback(subscriber_rti, 0.0)
    first_discoveries = subscriber_federate.callbacks_named("discoverObjectInstance")
    first_reflections = subscriber_federate.callbacks_named("reflectAttributeValues")
    first_release = bool(first_discoveries and first_reflections)
    if not first_release:
        first_release = _evoke_multiple_callbacks(subscriber_rti, 0.0, 0.0)
        first_discoveries = subscriber_federate.callbacks_named("discoverObjectInstance")
        first_reflections = subscriber_federate.callbacks_named("reflectAttributeValues")
    assert first_release is True or bool(first_reflections)
    first_delivery = first_discoveries[-1] if first_discoveries else initial_discovery
    assert first_delivery is not None
    assert first_reflections
    assert first_delivery.args[0] == object_instance
    assert first_delivery.args[1] == subscriber_object_class
    assert first_delivery.args[2] == config.object_instance_name
    first_reflection = first_reflections[-1]
    assert first_reflection.args[1] == {subscriber_attribute: config.first_payload}
    assert first_reflection.args[2] == config.first_tag

    subscriber_federate.clear()
    _disable_callbacks(subscriber_rti)
    publisher_rti.update_attribute_values(object_instance, {attribute: config.second_payload}, config.second_tag)
    publisher_rti.update_attribute_values(object_instance, {attribute: config.third_payload}, config.third_tag)
    second_batch_queued_while_disabled = subscriber_federate.last_callback("reflectAttributeValues") is None
    assert second_batch_queued_while_disabled
    blocked_batch_evoke = _evoke_multiple_callbacks(subscriber_rti, 0.0, 0.0)
    assert blocked_batch_evoke is False

    _enable_callbacks(subscriber_rti)
    drained_deliveries = subscriber_federate.callbacks_named("reflectAttributeValues")
    batch_evoke = bool(drained_deliveries)
    if not batch_evoke:
        batch_evoke = _evoke_multiple_callbacks(subscriber_rti, 0.0, 0.0)
        drained_deliveries = subscriber_federate.callbacks_named("reflectAttributeValues")
    assert batch_evoke is True
    batch_evoke_attempts = 1
    while len(drained_deliveries) < 2 and batch_evoke_attempts < 8:
        if not _evoke_multiple_callbacks(subscriber_rti, 0.0, 0.0):
            break
        batch_evoke_attempts += 1
        drained_deliveries = subscriber_federate.callbacks_named("reflectAttributeValues")
    drained_tags = [record.args[2] for record in drained_deliveries]
    assert drained_tags == [config.second_tag, config.third_tag]
    drained_payloads = [record.args[1] for record in drained_deliveries]
    assert drained_payloads == [
        {subscriber_attribute: config.second_payload},
        {subscriber_attribute: config.third_payload},
    ]
    post_drain = _evoke_multiple_callbacks(subscriber_rti, 0.0, 0.0)
    assert post_drain is False

    return {
        "publisher_handle": publisher_handle,
        "object_instance": object_instance,
        "object_class": object_class,
        "attribute": attribute,
        "subscriber_object_class": subscriber_object_class,
        "subscriber_attribute": subscriber_attribute,
        "first_queued_while_disabled": first_queued_while_disabled,
        "first_evoke": first_evoke,
        "second_evoke": second_evoke,
        "first_release": first_release,
        "first_delivery": first_delivery,
        "first_reflection": first_reflection,
        "second_batch_queued_while_disabled": second_batch_queued_while_disabled,
        "blocked_batch_evoke": blocked_batch_evoke,
        "batch_evoke": batch_evoke,
        "batch_evoke_attempts": batch_evoke_attempts,
        "drained_deliveries": drained_deliveries,
        "drained_tags": drained_tags,
        "drained_payloads": drained_payloads,
        "post_drain": post_drain,
    }


__all__ = [
    "CallbackControlScenarioConfig",
    "SupportServicesScenarioConfig",
    "run_callback_control_scenario",
    "run_support_factory_and_decode_scenario",
]
