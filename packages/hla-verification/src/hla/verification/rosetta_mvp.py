"""MVP Rosetta route evidence helpers."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    enum_name = getattr(value, "name", None)
    if isinstance(enum_name, str):
        return enum_name
    handle_value = getattr(value, "value", None)
    if isinstance(handle_value, (int, str)):
        return {"type": type(value).__name__, "value": handle_value}
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset, list, tuple)):
        return [_jsonable(item) for item in value]
    return repr(value)


def _event(name: str, **payload: Any) -> dict[str, Any]:
    return {"event": name, **{key: _jsonable(value) for key, value in payload.items()}}


def _callback_events(raw_events: Iterable[tuple[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for name, payload in raw_events:
        if name == "discover":
            object_instance, object_class, object_name, _extra = payload
            events.append(
                _event(
                    "discoverObjectInstance",
                    object=object_instance,
                    objectClass=object_class,
                    objectName=object_name,
                )
            )
        elif name == "reflect":
            object_instance, attributes, tag, order, _transport, _extra = payload
            events.append(
                _event(
                    "reflectAttributeValues",
                    object=object_instance,
                    attributes=attributes,
                    tag=tag,
                    order=order,
                )
            )
        elif name == "interaction":
            interaction_class, parameters, tag, order, _transport, _extra = payload
            events.append(
                _event(
                    "receiveInteraction",
                    interactionClass=interaction_class,
                    parameters=parameters,
                    tag=tag,
                    order=order,
                )
            )
        elif name == "time_regulation_enabled":
            events.append(_event("timeRegulationEnabled", time=payload))
        elif name == "time_constrained_enabled":
            events.append(_event("timeConstrainedEnabled", time=payload))
        elif name == "time_advance_grant":
            events.append(_event("timeAdvanceGrant", time=payload))
        else:
            events.append(_event(name, payload=payload))
    return events


def run_standard_2010_exchange_trace(backend_name: Any) -> dict[str, Any]:
    """Run the MVP 2010 object/interaction/time exchange and return a normalized trace."""

    from hla.backends.inmemory import InMemoryRTIEngine
    from hla.rti import create_rti_ambassador
    from hla.rti1516e.enums import CallbackModel, ResignAction
    from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification.scenario_support import DemoFederate, drain_callbacks

    engine = InMemoryRTIEngine()
    backend_label = getattr(backend_name, "kind", str(backend_name))
    federation_name = f"RosettaMvp{backend_label.replace('-', '').title()}"
    radar = create_rti_ambassador(spec="rti1516e", backend=backend_name, engine=engine)
    target = create_rti_ambassador(spec="rti1516e", backend=backend_name, engine=engine)
    radar_federate = DemoFederate()
    target_federate = DemoFederate()
    trace: list[dict[str, Any]] = []

    radar_connected = False
    target_connected = False
    radar_joined = False
    target_joined = False
    federation_created = False
    try:
        trace.append(_event("routeSelected", backend=backend_label, spec="rti1516e", standardBacked=radar.backend_info.details.get("standard_backed")))
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        radar_connected = True
        target.connect(target_federate, CallbackModel.HLA_EVOKED)
        target_connected = True
        trace.append(_event("connect", federates=["radar", "target"]))

        radar.create_federation_execution(federation_name, "DemoFOMmodule.xml")
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name))
        radar.join_federation_execution("radar", "demo", federation_name)
        radar_joined = True
        target.join_federation_execution("target", "demo", federation_name)
        target_joined = True
        trace.append(_event("joinFederationExecution", federates=["radar", "target"]))

        radar_object_class = radar.get_object_class_handle("HLAobjectRoot.DemoObject")
        radar_attribute = radar.get_attribute_handle(radar_object_class, "Payload")
        target_object_class = target.get_object_class_handle("HLAobjectRoot.DemoObject")
        target_attribute = target.get_attribute_handle(target_object_class, "Payload")
        radar.subscribe_object_class_attributes(the_class=radar_object_class, attribute_list={radar_attribute})
        target.publish_object_class_attributes(target_object_class, {target_attribute})
        trace.append(_event("publishSubscribeObject", objectClass=radar_object_class, attributes=[radar_attribute]))

        object_instance = target.register_object_instance(target_object_class, "DemoObject-1")
        drain_callbacks(radar)
        target.update_attribute_values(object_instance, {target_attribute: b"attribute-bytes"}, b"update-tag")
        drain_callbacks(radar)

        radar_interaction_class = radar.get_interaction_class_handle("HLAinteractionRoot.DemoInteraction")
        radar_parameter = radar.get_parameter_handle(radar_interaction_class, "Message")
        target_interaction_class = target.get_interaction_class_handle("HLAinteractionRoot.DemoInteraction")
        target_parameter = target.get_parameter_handle(target_interaction_class, "Message")
        radar.subscribe_interaction_class(radar_interaction_class)
        target.publish_interaction_class(target_interaction_class)
        trace.append(_event("publishSubscribeInteraction", interactionClass=radar_interaction_class, parameters=[radar_parameter]))
        target.send_interaction(target_interaction_class, {target_parameter: b"hello"}, b"interaction-tag")
        drain_callbacks(radar)

        radar.enable_time_regulation(HLAinteger64Interval(1))
        radar.enable_time_constrained()
        radar.time_advance_request(HLAinteger64Time(10))
        drain_callbacks(radar)
        trace.extend(_callback_events(radar_federate.events))
    finally:
        try:
            if target_joined:
                target.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
            if radar_joined:
                radar.resign_federation_execution(ResignAction.NO_ACTION)
            if federation_created:
                radar.destroy_federation_execution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if target_connected:
                target.disconnect()
            if radar_connected:
                radar.disconnect()
            if target_connected or radar_connected:
                trace.append(_event("disconnect", federates=["radar", "target"]))
        finally:
            close = getattr(target, "close", None)
            if callable(close):
                close()
            close = getattr(radar, "close", None)
            if callable(close):
                close()

    return {
        "route": backend_label,
        "edition": "2010",
        "scenario": "two-federate-core-exchange",
        "status": "core-green",
        "trace": trace,
    }


def run_standard_2025_lifecycle_trace(backend_name: str) -> dict[str, Any]:
    """Run the MVP 2025 lifecycle route proof and return a normalized trace."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025 import CallbackModel, ResignAction

    federation_name = f"RosettaMvp{backend_name.replace('-', '').title()}"
    rti = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=rti.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=rti.getHLAversion()),
    ]
    result = rti.connect(object(), CallbackModel.HLA_EVOKED)
    trace.append(_event("connect", result=result))
    rti.createFederationExecution(federation_name)
    trace.append(_event("createFederationExecution", federation=federation_name))
    rti.joinFederationExecution("python-federate", "demo", federation_name)
    trace.append(_event("joinFederationExecution", federate="python-federate", federation=federation_name))
    trace.append(_event("evokeCallback", delivered=rti.evokeCallback(0.0)))
    trace.append(_event("evokeMultipleCallbacks", delivered=rti.evokeMultipleCallbacks(0.0, 0.0)))
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    trace.append(_event("resignFederationExecution", action=ResignAction.NO_ACTION))
    rti.destroyFederationExecution(federation_name)
    trace.append(_event("destroyFederationExecution", federation=federation_name))
    rti.disconnect()
    trace.append(_event("disconnect"))

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "lifecycle-core",
        "status": "core-green",
        "trace": trace,
    }


__all__ = ["run_standard_2010_exchange_trace", "run_standard_2025_lifecycle_trace"]
