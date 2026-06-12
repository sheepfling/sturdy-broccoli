"""Local Delete Object Instance verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.exceptions import ObjectInstanceNotKnown

from .scenario_support import drain_callbacks_pair, register_named_object_instance


@dataclass(frozen=True)
class LocalDeleteScenarioConfig:
    federation_name: str = "LocalDeleteFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    observer_name: str = "Observer"
    federate_type: str = "LocalDeleteFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "Local-Delete-Object-1"
    rediscover_payload: bytes = b"rediscover"
    rediscover_tag: bytes = b"local-delete-rediscover"


def run_local_delete_scenario(
    owner_rti: Any,
    observer_rti: Any,
    *,
    config: LocalDeleteScenarioConfig,
    owner_federate: Any,
    observer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    observer_handle = observer_rti.join_federation_execution(
        config.observer_name,
        config.federate_type,
        config.federation_name,
    )

    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    observer_class = observer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    observer_attr = observer_rti.get_attribute_handle(observer_class, config.attribute_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    observer_rti.subscribe_object_class_attributes(observer_class, {observer_attr})
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        owner_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)
    assert observer_rti.get_object_instance_handle(config.object_instance_name) == object_instance

    observer_federate.clear()
    observer_rti.local_delete_object_instance(object_instance)
    with_object_missing = False
    with_class_missing = False
    try:
        observer_rti.get_object_instance_handle(config.object_instance_name)
    except ObjectInstanceNotKnown:
        with_object_missing = True
    try:
        observer_rti.get_known_object_class_handle(object_instance)
    except ObjectInstanceNotKnown:
        with_class_missing = True
    assert with_object_missing
    assert with_class_missing

    owner_rti.update_attribute_values(
        object_instance,
        {owner_attr: config.rediscover_payload},
        config.rediscover_tag,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    discovery = observer_federate.last_callback("discoverObjectInstance")
    reflection = observer_federate.last_callback("reflectAttributeValues")
    assert discovery is not None
    assert reflection is not None
    assert observer_rti.get_object_instance_handle(config.object_instance_name) == object_instance
    assert observer_rti.get_known_object_class_handle(object_instance) == observer_class

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "owner_class": owner_class,
        "observer_class": observer_class,
        "owner_attribute": owner_attr,
        "observer_attribute": observer_attr,
        "object_instance": object_instance,
        "discovery": discovery,
        "reflection": reflection,
    }


__all__ = ["LocalDeleteScenarioConfig", "run_local_delete_scenario"]
