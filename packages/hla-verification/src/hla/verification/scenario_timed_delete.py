"""Timed delete/remove verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import ObjectInstanceNotKnown
from hla.rti1516_2025.exceptions import ObjectInstanceNotKnown as ObjectInstanceNotKnown2025

from .scenario_support import drain_callbacks_pair, register_named_object_instance


def _handle_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _same_handle_value(left: Any, right: Any) -> bool:
    return _handle_value(left) == _handle_value(right)


def _factory_make_interval(factory: Any, value: float) -> Any:
    method = getattr(factory, "make_interval", None)
    if callable(method):
        return method(value)
    return factory.makeInterval(value)


def _factory_make_time(factory: Any, value: float) -> Any:
    method = getattr(factory, "make_time", None)
    if callable(method):
        return method(value)
    return factory.makeTime(value)


@dataclass(frozen=True)
class TimedDeleteScenarioConfig:
    federation_name: str = "TimedDeleteFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str = "HLAinteger64Time"
    owner_name: str = "Owner"
    observer_name: str = "Observer"
    federate_type: str = "TimedDeleteFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "TimedDelete-Object-1"
    delete_tag: bytes = b"delete-tag"


def run_timed_delete_scenario(
    owner_rti: Any,
    observer_rti: Any,
    *,
    config: TimedDeleteScenarioConfig,
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

    time_factory = owner_rti.get_time_factory()
    object_class = owner_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(object_class, config.attribute_name)
    observer_class = observer_rti.get_object_class_handle(config.object_class_name)
    observer_attr = observer_rti.get_attribute_handle(observer_class, config.attribute_name)

    owner_rti.publish_object_class_attributes(object_class, {owner_attr})
    observer_rti.subscribe_object_class_attributes(observer_class, {observer_attr})
    owner_rti.enable_time_regulation(_factory_make_interval(time_factory, 1.0))
    observer_rti.enable_time_constrained()
    drain_callbacks_pair(owner_rti, observer_rti, loops=24)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        object_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    assert _same_handle_value(observer_rti.get_object_instance_handle(config.object_instance_name), object_instance)
    observer_federate.clear()

    delete_time = _factory_make_time(time_factory, 1.0)
    advance_time = _factory_make_time(time_factory, 2.0)
    owner_rti.delete_object_instance(object_instance, config.delete_tag, delete_time)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    remove_before_grant = observer_federate.last_callback("removeObjectInstance")
    assert remove_before_grant is None
    assert _same_handle_value(observer_rti.get_object_instance_handle(config.object_instance_name), object_instance)

    owner_rti.time_advance_request(advance_time)
    observer_rti.next_message_request_available(advance_time)
    drain_callbacks_pair(owner_rti, observer_rti, loops=24)
    observer_rti.next_message_request_available(advance_time)
    drain_callbacks_pair(owner_rti, observer_rti, loops=24)

    remove_after_grant = observer_federate.last_callback("removeObjectInstance")
    assert remove_after_grant is not None
    assert _same_handle_value(remove_after_grant.args[0], object_instance)
    assert remove_after_grant.args[1] == config.delete_tag

    removed_from_catalog = False
    try:
        observer_rti.get_object_instance_handle(config.object_instance_name)
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025):
        removed_from_catalog = True
    assert removed_from_catalog

    removed_known_class = False
    try:
        observer_rti.get_known_object_class_handle(object_instance)
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025):
        removed_known_class = True
    assert removed_known_class

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "object_instance": object_instance,
        "delete_time": delete_time,
        "advance_time": advance_time,
        "remove_before_grant": remove_before_grant,
        "remove_after_grant": remove_after_grant,
    }


__all__ = ["TimedDeleteScenarioConfig", "run_timed_delete_scenario"]
