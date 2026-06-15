"""Single-ambassador backend-neutral smoke scenario."""

from __future__ import annotations

from typing import Any, Callable

from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
)
from hla2010.time import HLAinteger64Interval, HLAinteger64Time
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
    rti.createFederationExecution(federation_name, "DemoFOMmodule.xml")
    federate_handle = rti.joinFederationExecution("python-federate", "demo", federation_name)
    assert isinstance(federate_handle, FederateHandle)
    assert rti.getFederateName(federate_handle) == "python-federate"
    assert rti.getFederateHandle("python-federate") == federate_handle
    object_class = rti.getObjectClassHandle("HLAobjectRoot.DemoObject")
    assert isinstance(object_class, ObjectClassHandle)
    assert rti.getObjectClassName(object_class) == "HLAobjectRoot.DemoObject"
    attribute = rti.getAttributeHandle(object_class, "Payload")
    assert isinstance(attribute, AttributeHandle)
    assert rti.getAttributeName(object_class, attribute) == "Payload"
    rti.publishObjectClassAttributes(object_class, {attribute})
    rti.subscribeObjectClassAttributes(the_class=object_class, attribute_list={attribute})
    object_instance = rti.registerObjectInstance(object_class, "DemoObject-1")
    assert isinstance(object_instance, ObjectInstanceHandle)
    assert rti.getObjectInstanceHandle("DemoObject-1") == object_instance
    assert rti.getObjectInstanceName(object_instance) == "DemoObject-1"
    assert rti.getKnownObjectClassHandle(object_instance) == object_class
    drain_callbacks(rti)
    rti.updateAttributeValues(object_instance, {attribute: b"attribute-bytes"}, b"update-tag")
    drain_callbacks(rti)
    interaction_class = rti.getInteractionClassHandle("HLAinteractionRoot.DemoInteraction")
    assert isinstance(interaction_class, InteractionClassHandle)
    assert rti.getInteractionClassName(interaction_class) == "HLAinteractionRoot.DemoInteraction"
    parameter = rti.getParameterHandle(interaction_class, "Message")
    assert isinstance(parameter, ParameterHandle)
    assert rti.getParameterName(interaction_class, parameter) == "Message"
    rti.publishInteractionClass(interaction_class)
    rti.subscribeInteractionClass(interaction_class)
    rti.sendInteraction(interaction_class, {parameter: b"hello"}, b"interaction-tag")
    drain_callbacks(rti)
    rti.enableTimeRegulation(HLAinteger64Interval(1))
    rti.enableTimeConstrained()
    rti.timeAdvanceRequest(HLAinteger64Time(10))
    drain_callbacks(rti)
    dimension = rti.getDimensionHandle("RoutingSpace")
    assert isinstance(dimension, DimensionHandle)
    assert rti.getDimensionName(dimension) == "RoutingSpace"
    region = rti.createRegion({dimension})
    assert isinstance(region, RegionHandle)
    rti.commitRegionModifications({region})
    rti.deleteRegion(region)
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
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federation_name)
    rti.disconnect()
    rti.close()
    return summary


__all__ = ["run_basic_federate_scenario"]
