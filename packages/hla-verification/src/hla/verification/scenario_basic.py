"""Single-ambassador backend-neutral smoke scenario."""

from __future__ import annotations

from typing import Any, Callable

from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516e.exceptions import FederateOwnsAttributes, NameNotFound
from hla.rti1516e.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
)
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time

from .scenario_support import DemoFederate, drain_callbacks


def _resolve_first_named(getter: Callable[[str], Any], *names: str) -> tuple[str, Any]:
    last_error: Exception | None = None
    for name in names:
        try:
            return name, getter(name)
        except NameNotFound as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise AssertionError("at least one candidate name is required")


def _payload_contains(value: Any, expected: Any) -> bool:
    if value == expected:
        return True
    expected_name = getattr(expected, "name", None)
    value_name = getattr(value, "name", None)
    if expected_name is not None and value_name == expected_name:
        return True
    if _handle_value(value) == _handle_value(expected):
        return True
    if isinstance(value, tuple):
        return any(_payload_contains(item, expected) for item in value)
    if isinstance(value, set):
        return any(_payload_contains(item, expected) for item in value)
    return False


def _handle_value(handle: Any) -> Any:
    return getattr(handle, "value", handle)


def _normalize_handle_map(values: dict[Any, bytes]) -> dict[Any, bytes]:
    return {_handle_value(handle): value for handle, value in values.items()}


def run_basic_federate_scenario(
    rti_factory: Callable[[], Any],
    *,
    federation_name: str = "PythonShimFederation",
) -> dict[str, Any]:
    rti = rti_factory()
    federate = DemoFederate()
    summary: dict[str, Any] = {"backend": getattr(rti, "backend_info", None)}
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(federation_name, "DemoFOMmodule.xml")
    federate_handle = rti.join_federation_execution("python-federate", "demo", federation_name)
    assert isinstance(federate_handle, FederateHandle)
    assert rti.get_federate_name(federate_handle) == "python-federate"
    assert rti.get_federate_handle("python-federate") == federate_handle
    object_class = rti.get_object_class_handle("HLAobjectRoot.DemoObject")
    assert isinstance(object_class, ObjectClassHandle)
    assert rti.get_object_class_name(object_class) == "HLAobjectRoot.DemoObject"
    attribute = rti.get_attribute_handle(object_class, "Payload")
    assert isinstance(attribute, AttributeHandle)
    assert rti.get_attribute_name(object_class, attribute) == "Payload"
    rti.publish_object_class_attributes(object_class, {attribute})
    rti.subscribe_object_class_attributes(the_class=object_class, attribute_list={attribute})
    object_instance = rti.register_object_instance(object_class, "DemoObject-1")
    assert isinstance(object_instance, ObjectInstanceHandle)
    assert rti.get_object_instance_handle("DemoObject-1") == object_instance
    assert rti.get_object_instance_name(object_instance) == "DemoObject-1"
    assert rti.get_known_object_class_handle(object_instance) == object_class
    drain_callbacks(rti)
    rti.update_attribute_values(object_instance, {attribute: b"attribute-bytes"}, b"update-tag")
    drain_callbacks(rti)
    interaction_class_name, interaction_class = _resolve_first_named(
        rti.get_interaction_class_handle,
        "HLAinteractionRoot.Ping",
        "HLAinteractionRoot.DemoInteraction",
    )
    assert isinstance(interaction_class, InteractionClassHandle)
    assert rti.get_interaction_class_name(interaction_class) == interaction_class_name
    parameter_name, parameter = _resolve_first_named(
        lambda candidate: rti.get_parameter_handle(interaction_class, candidate),
        "RequestId",
        "Message",
    )
    assert isinstance(parameter, ParameterHandle)
    assert rti.get_parameter_name(interaction_class, parameter) == parameter_name
    rti.publish_interaction_class(interaction_class)
    rti.subscribe_interaction_class(interaction_class)
    rti.send_interaction(interaction_class, {parameter: b"hello"}, b"interaction-tag")
    drain_callbacks(rti)
    rti.enable_time_regulation(HLAinteger64Interval(1))
    rti.enable_time_constrained()
    rti.time_advance_request(HLAinteger64Time(10))
    drain_callbacks(rti)
    dimension_name, dimension = _resolve_first_named(
        rti.get_dimension_handle,
        "HLAdefaultRoutingSpace",
        "RoutingSpace",
    )
    assert isinstance(dimension, DimensionHandle)
    assert rti.get_dimension_name(dimension) == dimension_name
    region = rti.create_region({dimension})
    assert isinstance(region, RegionHandle)
    rti.commit_region_modifications({region})
    rti.delete_region(region)
    event_names = [name for name, _ in federate.events]
    assert "discover" in event_names
    assert "reflect" in event_names
    assert "interaction" in event_names
    assert "time_regulation_enabled" in event_names
    assert "time_constrained_enabled" in event_names
    assert "time_advance_grant" in event_names
    reflect_events = [payload for name, payload in federate.events if name == "reflect"]
    reflected_object, reflected_attrs, reflected_tag, *reflect_tail = reflect_events[-1]
    assert _handle_value(reflected_object) == _handle_value(object_instance)
    assert _normalize_handle_map(reflected_attrs) == {_handle_value(attribute): b"attribute-bytes"}
    assert reflected_tag == b"update-tag"
    assert _payload_contains(tuple(reflect_tail), OrderType.RECEIVE)
    interaction_events = [payload for name, payload in federate.events if name == "interaction"]
    received_interaction, received_params, received_tag, *interaction_tail = interaction_events[-1]
    assert _handle_value(received_interaction) == _handle_value(interaction_class)
    assert _normalize_handle_map(received_params) == {_handle_value(parameter): b"hello"}
    assert received_tag == b"interaction-tag"
    assert _payload_contains(tuple(interaction_tail), OrderType.RECEIVE)
    time_grants = [payload for name, payload in federate.events if name == "time_advance_grant"]
    assert _handle_value(time_grants[-1]) == _handle_value(HLAinteger64Time(10))
    summary.update(
        {
            "federate_handle": federate_handle,
            "object_class": object_class,
            "attribute": attribute,
            "object_instance": object_instance,
            "interaction_class": interaction_class,
            "interaction_class_name": interaction_class_name,
            "parameter": parameter,
            "parameter_name": parameter_name,
            "dimension": dimension,
            "dimension_name": dimension_name,
            "region": region,
            "events": federate.events,
            "event_names": event_names,
        }
    )
    try:
        rti.resign_federation_execution(ResignAction.NO_ACTION)
    except FederateOwnsAttributes:
        rti.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rti.destroy_federation_execution(federation_name)
    rti.disconnect()
    rti.close()
    return summary


__all__ = ["run_basic_federate_scenario"]
