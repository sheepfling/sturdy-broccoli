"""Single-ambassador backend-neutral smoke scenario."""
from __future__ import annotations

from typing import Any, Callable

from ..enums import CallbackModel, OrderType, ResignAction
from ..handles import AttributeHandle, DimensionHandle, FederateHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle, RegionHandle
from ..time import HLAinteger64Interval, HLAinteger64Time
from .scenario_support import DemoFederate, drain_callbacks


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
    interaction_class = rti.get_interaction_class_handle("HLAinteractionRoot.DemoInteraction")
    assert isinstance(interaction_class, InteractionClassHandle)
    assert rti.get_interaction_class_name(interaction_class) == "HLAinteractionRoot.DemoInteraction"
    parameter = rti.get_parameter_handle(interaction_class, "Message")
    assert isinstance(parameter, ParameterHandle)
    assert rti.get_parameter_name(interaction_class, parameter) == "Message"
    rti.publish_interaction_class(interaction_class)
    rti.subscribe_interaction_class(interaction_class)
    rti.send_interaction(interaction_class, {parameter: b"hello"}, b"interaction-tag")
    drain_callbacks(rti)
    rti.enable_time_regulation(HLAinteger64Interval(1))
    rti.enable_time_constrained()
    rti.time_advance_request(HLAinteger64Time(10))
    drain_callbacks(rti)
    dimension = rti.get_dimension_handle("RoutingSpace")
    assert isinstance(dimension, DimensionHandle)
    assert rti.get_dimension_name(dimension) == "RoutingSpace"
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
    reflected_object, reflected_attrs, reflected_tag, reflected_order, *_ = reflect_events[-1]
    assert reflected_object == object_instance
    assert reflected_attrs == {attribute: b"attribute-bytes"}
    assert reflected_tag == b"update-tag"
    assert reflected_order is OrderType.RECEIVE
    interaction_events = [payload for name, payload in federate.events if name == "interaction"]
    received_interaction, received_params, received_tag, received_order, *_ = interaction_events[-1]
    assert received_interaction == interaction_class
    assert received_params == {parameter: b"hello"}
    assert received_tag == b"interaction-tag"
    assert received_order is OrderType.RECEIVE
    time_grants = [payload for name, payload in federate.events if name == "time_advance_grant"]
    assert time_grants[-1] == HLAinteger64Time(10)
    summary.update(
        {
            "federate_handle": federate_handle,
            "object_class": object_class,
            "attribute": attribute,
            "object_instance": object_instance,
            "interaction_class": interaction_class,
            "parameter": parameter,
            "dimension": dimension,
            "region": region,
            "events": federate.events,
            "event_names": event_names,
        }
    )
    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution(federation_name)
    rti.disconnect()
    rti.close()
    return summary


__all__ = ["run_basic_federate_scenario"]
