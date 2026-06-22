"""Orphan object lifecycle verification scenario."""
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


@dataclass(frozen=True)
class OrphanObjectScenarioConfig:
    federation_name: str = "OrphanObjectFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    observer_name: str = "Observer"
    late_name: str = "Late"
    federate_type: str = "OrphanObjectFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "Orphan-Object-1"
    delete_tag: bytes = b"orphan-delete"


def run_orphan_object_lifecycle_scenario(
    owner_rti: Any,
    observer_rti: Any,
    late_rti: Any,
    *,
    config: OrphanObjectScenarioConfig,
    owner_federate: Any,
    observer_federate: Any,
    late_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    late_rti.connect(late_federate, CallbackModel.HLA_EVOKED)
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
    assert _same_handle_value(observer_rti.get_object_instance_handle(config.object_instance_name), object_instance)
    observer_federate.clear()

    owner_rti.unconditional_attribute_ownership_divestiture(object_instance, {owner_attr})
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr) is False
    assert _same_handle_value(observer_rti.get_object_instance_handle(config.object_instance_name), object_instance)
    assert _same_handle_value(observer_rti.get_known_object_class_handle(object_instance), observer_class)

    late_handle = late_rti.join_federation_execution(config.late_name, config.federate_type, config.federation_name)
    late_class = late_rti.get_object_class_handle(config.object_class_name)
    late_attr = late_rti.get_attribute_handle(late_class, config.attribute_name)
    late_rti.subscribe_object_class_attributes(late_class, {late_attr})
    drain_callbacks_pair(owner_rti, observer_rti, late_rti, loops=16)

    late_discovery = late_federate.last_callback("discoverObjectInstance")
    assert late_discovery is not None
    assert _same_handle_value(late_discovery.args[0], object_instance)
    assert _same_handle_value(late_rti.get_object_instance_handle(config.object_instance_name), object_instance)
    assert _same_handle_value(late_rti.get_known_object_class_handle(object_instance), late_class)

    observer_rti.local_delete_object_instance(object_instance)
    observer_removed_local_knowledge = False
    try:
        observer_rti.get_object_instance_handle(config.object_instance_name)
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025):
        observer_removed_local_knowledge = True
    assert observer_removed_local_knowledge

    owner_rti.delete_object_instance(object_instance, config.delete_tag)
    drain_callbacks_pair(owner_rti, observer_rti, late_rti, loops=16)

    observer_remove = observer_federate.last_callback("removeObjectInstance")
    late_remove = late_federate.last_callback("removeObjectInstance")
    assert observer_remove is None
    assert late_remove is not None
    assert _same_handle_value(late_remove.args[0], object_instance)
    assert late_remove.args[1] == config.delete_tag

    late_removed_global_knowledge = False
    try:
        late_rti.get_object_instance_handle(config.object_instance_name)
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025):
        late_removed_global_knowledge = True
    assert late_removed_global_knowledge

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "late_handle": late_handle,
        "owner_class": owner_class,
        "observer_class": observer_class,
        "late_class": late_class,
        "owner_attribute": owner_attr,
        "observer_attribute": observer_attr,
        "late_attribute": late_attr,
        "object_instance": object_instance,
        "late_discovery": late_discovery,
        "observer_remove": observer_remove,
        "late_remove": late_remove,
    }


__all__ = [
    "OrphanObjectScenarioConfig",
    "run_orphan_object_lifecycle_scenario",
]
