"""Request Attribute Value Update verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel

from .scenario_support import drain_callbacks_pair, register_named_object_instance


@dataclass(frozen=True)
class RequestAttributeValueUpdateScenarioConfig:
    federation_name: str = "RequestAttributeValueUpdateFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    requester_name: str = "Requester"
    federate_type: str = "RequestAttributeValueUpdateFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "Request-Update-Object-1"
    request_tag: bytes = b"request-update"


def run_request_attribute_value_update_scenario(
    owner_rti: Any,
    requester_rti: Any,
    *,
    config: RequestAttributeValueUpdateScenarioConfig,
    owner_federate: Any,
    requester_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    requester_rti.connect(requester_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    requester_handle = requester_rti.join_federation_execution(
        config.requester_name,
        config.federate_type,
        config.federation_name,
    )

    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    requester_class = requester_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    requester_attr = requester_rti.get_attribute_handle(requester_class, config.attribute_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    requester_rti.subscribe_object_class_attributes(requester_class, {requester_attr})
    drain_callbacks_pair(owner_rti, requester_rti, loops=8)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        owner_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, requester_rti, loops=8)
    owner_federate.clear()

    requester_rti.request_attribute_value_update(object_instance, {requester_attr}, config.request_tag)
    drain_callbacks_pair(owner_rti, requester_rti, loops=16)

    provide_record = owner_federate.last_callback("provideAttributeValueUpdate")
    assert provide_record is not None
    assert provide_record.args == (object_instance, {owner_attr}, config.request_tag)

    return {
        "owner_handle": owner_handle,
        "requester_handle": requester_handle,
        "owner_class": owner_class,
        "requester_class": requester_class,
        "owner_attribute": owner_attr,
        "requester_attribute": requester_attr,
        "object_instance": object_instance,
        "provide_record": provide_record,
    }


def run_request_attribute_value_update_routing_scenario(
    owner_a_rti: Any,
    owner_b_rti: Any,
    requester_rti: Any,
    *,
    config: RequestAttributeValueUpdateScenarioConfig,
    owner_a_federate: Any,
    owner_b_federate: Any,
    requester_federate: Any,
) -> dict[str, Any]:
    owner_a_rti.connect(owner_a_federate, CallbackModel.HLA_EVOKED)
    owner_b_rti.connect(owner_b_federate, CallbackModel.HLA_EVOKED)
    requester_rti.connect(requester_federate, CallbackModel.HLA_EVOKED)
    owner_a_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_a_handle = owner_a_rti.join_federation_execution("OwnerA", config.federate_type, config.federation_name)
    owner_b_handle = owner_b_rti.join_federation_execution("OwnerB", config.federate_type, config.federation_name)
    requester_handle = requester_rti.join_federation_execution(
        config.requester_name,
        config.federate_type,
        config.federation_name,
    )

    owner_a_class = owner_a_rti.get_object_class_handle(config.object_class_name)
    owner_b_class = owner_b_rti.get_object_class_handle(config.object_class_name)
    requester_class = requester_rti.get_object_class_handle(config.object_class_name)
    owner_a_attr = owner_a_rti.get_attribute_handle(owner_a_class, config.attribute_name)
    owner_b_attr = owner_b_rti.get_attribute_handle(owner_b_class, config.attribute_name)
    requester_attr = requester_rti.get_attribute_handle(requester_class, config.attribute_name)

    owner_a_rti.publish_object_class_attributes(owner_a_class, {owner_a_attr})
    owner_b_rti.publish_object_class_attributes(owner_b_class, {owner_b_attr})
    requester_rti.subscribe_object_class_attributes(requester_class, {requester_attr})
    drain_callbacks_pair(owner_a_rti, owner_b_rti, requester_rti, loops=8)

    object_a = register_named_object_instance(
        owner_a_rti,
        owner_a_federate,
        owner_a_class,
        f"{config.object_instance_name}-A",
    )
    object_b = register_named_object_instance(
        owner_b_rti,
        owner_b_federate,
        owner_b_class,
        f"{config.object_instance_name}-B",
    )
    drain_callbacks_pair(owner_a_rti, owner_b_rti, requester_rti, loops=8)
    owner_a_federate.clear()
    owner_b_federate.clear()
    requester_federate.clear()

    requester_rti.request_attribute_value_update(object_a, {requester_attr}, config.request_tag)
    drain_callbacks_pair(owner_a_rti, owner_b_rti, requester_rti, loops=16)
    object_target_provide_a = owner_a_federate.last_callback("provideAttributeValueUpdate")
    object_target_provide_b = owner_b_federate.last_callback("provideAttributeValueUpdate")
    assert object_target_provide_a is not None
    assert object_target_provide_a.args == (object_a, {owner_a_attr}, config.request_tag)
    assert object_target_provide_b is None

    owner_a_federate.clear()
    owner_b_federate.clear()
    requester_rti.request_attribute_value_update(requester_class, {requester_attr}, b"class-wide")
    drain_callbacks_pair(owner_a_rti, owner_b_rti, requester_rti, loops=16)
    class_target_provide_a = owner_a_federate.last_callback("provideAttributeValueUpdate")
    class_target_provide_b = owner_b_federate.last_callback("provideAttributeValueUpdate")
    assert class_target_provide_a is not None
    assert class_target_provide_b is not None
    assert class_target_provide_a.args == (object_a, {owner_a_attr}, b"class-wide")
    assert class_target_provide_b.args == (object_b, {owner_b_attr}, b"class-wide")

    return {
        "owner_a_handle": owner_a_handle,
        "owner_b_handle": owner_b_handle,
        "requester_handle": requester_handle,
        "requester_class": requester_class,
        "requester_attribute": requester_attr,
        "object_a": object_a,
        "object_b": object_b,
        "object_target_provide_a": object_target_provide_a,
        "object_target_provide_b": object_target_provide_b,
        "class_target_provide_a": class_target_provide_a,
        "class_target_provide_b": class_target_provide_b,
    }


__all__ = [
    "RequestAttributeValueUpdateScenarioConfig",
    "run_request_attribute_value_update_scenario",
    "run_request_attribute_value_update_routing_scenario",
]
