"""MVP language-shim route evidence helpers."""
from __future__ import annotations

from collections.abc import Iterable
import shutil
import tempfile
import textwrap
import uuid
from pathlib import Path
from typing import Any

LIFECYCLE_REQUIREMENTS_2025 = [
    "HLA2025-REQ-002",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-006",
]

CORE_EXCHANGE_REQUIREMENTS_2025 = [
    "HLA2025-FR-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FR-007",
    "HLA2025-FR-010",
    "HLA2025-FI-001",
    "HLA2025-FI-006",
    "HLA2025-FI-009",
]

TIME_MANAGEMENT_REQUIREMENTS_2025 = [
    "HLA2025-FR-010",
    "HLA2025-FI-005",
    "HLA2025-FI-009",
    "HLA2025-MOD-006",
]

RUNTIME_CAPABILITY_REQUIREMENTS_2025 = [
    "HLA2025-FR-001",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-003",
    "HLA2025-FI-004",
    "HLA2025-FI-005",
    "HLA2025-FI-006",
    "HLA2025-FI-009",
    "HLA2025-MOD-005",
    "HLA2025-MOD-006",
    "HLA2025-MOD-007",
    "HLA2025-NEW-004",
    "HLA2025-NEW-007",
]


def _route_runtime_requirements_2025(backend_name: str) -> list[str]:
    requirements = list(RUNTIME_CAPABILITY_REQUIREMENTS_2025)
    if backend_name.startswith("java-standard-2025"):
        requirements.append("HLA2025-BND-001")
    if backend_name.startswith("cpp-standard-2025"):
        requirements.append("HLA2025-BND-002")
    return requirements


class _Recording2025FederateAmbassador:
    def __init__(self) -> None:
        self.events: list[tuple[str, Any]] = []

    def timeRegulationEnabled(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeRegulationEnabled", time))

    def timeConstrainedEnabled(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeConstrainedEnabled", time))

    def timeAdvanceGrant(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeAdvanceGrant", time))

    def attributeOwnershipAcquisitionNotification(  # noqa: N802
        self,
        objectInstance: Any,
        securedAttributes: Any,
        userSuppliedTag: Any,
    ) -> None:
        self.events.append(("attributeOwnershipAcquisitionNotification", (objectInstance, securedAttributes, userSuppliedTag)))

    def attributeOwnershipUnavailable(self, objectInstance: Any, attributes: Any, userSuppliedTag: Any) -> None:  # noqa: N802
        self.events.append(("attributeOwnershipUnavailable", (objectInstance, attributes, userSuppliedTag)))

    def informAttributeOwnership(self, objectInstance: Any, attributes: Any, owner: Any) -> None:  # noqa: N802
        self.events.append(("informAttributeOwnership", (objectInstance, attributes, owner)))

    def attributeIsNotOwned(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self.events.append(("attributeIsNotOwned", (objectInstance, attributes)))


def _write_2025_runtime_capability_fom() -> tuple[Path, Path]:
    temp_dir = Path(tempfile.mkdtemp(prefix="hla-2025-route-fom-"))
    fom = temp_dir / "RouteCapability2025.xml"
    fom.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
              <modelIdentification>
                <name>Route Capability 2025 FOM</name>
                <type>FOM</type>
                <version>1.0</version>
                <modificationDate>2026-01-01</modificationDate>
                <securityClassification>UNCLASSIFIED</securityClassification>
                <description>Runtime route capability test FOM.</description>
                <poc>HLA-X</poc>
                <reference>HLA-X 2025 route capability trace</reference>
              </modelIdentification>
              <objects>
                <objectClass>
                  <name>HLAobjectRoot</name>
                  <objectClass>
                    <name>RouteTarget</name>
                    <sharing>PublishSubscribe</sharing>
                    <attribute>
                      <name>Position</name>
                      <dataType>HLAfloat64BE</dataType>
                      <updateType>Periodic</updateType>
                      <updateCondition>Route trace update</updateCondition>
                      <valueRequired>true</valueRequired>
                      <ownership>DivestAcquire</ownership>
                      <sharing>PublishSubscribe</sharing>
                      <transportation>HLAreliable</transportation>
                      <order>Receive</order>
                      <dimensions>RoutingSpace</dimensions>
                      <semantics>Route target position.</semantics>
                    </attribute>
                  </objectClass>
                </objectClass>
              </objects>
              <interactions>
                <interactionClass><name>HLAinteractionRoot</name><sharing>Neither</sharing></interactionClass>
              </interactions>
              <dimensions>
                <dimension>
                  <name>RoutingSpace</name>
                  <dataType>HLAinteger32BE</dataType>
                  <upperBound>1024</upperBound>
                  <normalization>Route trace normalization.</normalization>
                </dimension>
              </dimensions>
              <transportations>
                <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
                <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
              </transportations>
            </objectModel>
            """
        ),
        encoding="utf-8",
    )
    return temp_dir, fom


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
    federation_name = f"ShimRouteMvp{backend_label.replace('-', '').title()}"
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
        "status": "core-exchange-green",
        "requirements_exercised": CORE_EXCHANGE_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_lifecycle_trace(backend_name: str) -> dict[str, Any]:
    """Run the MVP 2025 lifecycle route proof and return a normalized trace."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025 import CallbackModel, ResignAction

    federation_name = f"ShimRouteMvp{backend_name.replace('-', '').title()}"
    fom_module = "TargetRadarFOMmodule.xml"
    rti = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=rti.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=rti.getHLAversion()),
    ]
    result = rti.connect(object(), CallbackModel.HLA_EVOKED)
    trace.append(_event("connect", result=result))
    rti.createFederationExecution(federation_name, fom_module)
    trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module))
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
        "status": "lifecycle-green",
        "requirements_exercised": LIFECYCLE_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_runtime_capability_trace(backend_name: str) -> dict[str, Any]:
    """Run a 2025 route capability trace beyond lifecycle without claiming conformance."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.time import HLAfloat64Interval, HLAfloat64Time

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteRuntime{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    federate = _Recording2025FederateAmbassador()
    rti = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=rti.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=rti.getHLAversion()),
    ]
    connected = False
    joined = False
    federation_created = False
    try:
        result = rti.connect(federate, CallbackModel.HLA_EVOKED)
        connected = True
        trace.append(_event("connect", result=result, callbackModel=CallbackModel.HLA_EVOKED))

        rti.createFederationExecution(
            federationName=federation_name,
            fomModule=str(fom_module),
            logicalTimeImplementationName="HLAfloat64Time",
        )
        federation_created = True
        trace.append(
            _event(
                "createFederationExecution",
                federation=federation_name,
                fomModule=fom_module.name,
                logicalTimeImplementationName="HLAfloat64Time",
            )
        )
        federate_handle = rti.joinFederationExecution(
            federateName="runtime-federate",
            federateType="route-capability",
            federationName=federation_name,
        )
        joined = True
        trace.append(_event("joinFederationExecution", federate="runtime-federate", federateHandle=federate_handle))

        object_class = rti.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        attribute = rti.getAttributeHandle(object_class, "Position")
        dimension = rti.getDimensionHandle("RoutingSpace")
        available_dimensions = rti.getAvailableDimensionsForObjectClass(object_class)
        trace.append(
            _event(
                "resolveFomHandles",
                objectClass=object_class,
                attribute=attribute,
                dimension=dimension,
                dimensionUpperBound=rti.getDimensionUpperBound(dimension),
                availableDimensions=available_dimensions,
            )
        )

        best_effort = rti.getTransportationTypeHandle("HLAbestEffort")
        rti.changeDefaultAttributeTransportationType(object_class, {attribute}, best_effort)
        trace.append(_event("changeDefaultAttributeTransportationType", objectClass=object_class, attributes={attribute}, transportation=best_effort))
        rti.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
        trace.append(_event("changeDefaultAttributeOrderType", objectClass=object_class, attributes={attribute}, order=OrderType.TIMESTAMP))
        trace.append(_event("defaultAttributePolicySnapshot", value=rti.defaultAttributePolicySnapshot()))

        object_instance = rti.registerObjectInstance(object_class, f"RouteTarget-{uuid.uuid4().hex[:8]}")
        trace.append(
            _event(
                "registerObjectInstance",
                objectClass=object_class,
                objectInstance=object_instance,
                initiallyOwned=rti.isAttributeOwnedByFederate(object_instance, attribute),
            )
        )
        rti.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"runtime-divest")
        trace.append(_event("unconditionalAttributeOwnershipDivestiture", objectInstance=object_instance, attributes={attribute}, tag=b"runtime-divest"))
        rti.queryAttributeOwnership(object_instance, {attribute})
        trace.append(_event("queryAttributeOwnership", objectInstance=object_instance, attributes={attribute}))
        rti.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"runtime-claim")
        trace.append(_event("attributeOwnershipAcquisitionIfAvailable", objectInstance=object_instance, attributes={attribute}, tag=b"runtime-claim"))

        time_factory = rti.getTimeFactory()
        trace.append(_event("getTimeFactory", factoryName=time_factory.getName()))
        rti.enableTimeRegulation(HLAfloat64Interval(0.5))
        trace.append(_event("enableTimeRegulation", lookahead=HLAfloat64Interval(0.5)))
        rti.enableTimeConstrained()
        trace.append(_event("enableTimeConstrained"))
        rti.timeAdvanceRequest(HLAfloat64Time(5.0))
        trace.append(_event("timeAdvanceRequest", value=HLAfloat64Time(5.0)))
        trace.append(_event("queryLogicalTime", value=rti.queryLogicalTime()))

        rti.setServiceReportingSwitch(True)
        trace.append(_event("setServiceReportingSwitch", value=True))
        service_report = rti.serializeMOMServiceReport(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation",
            arguments={"objectInstance": object_instance, "attribute": attribute},
            result={"scenario": "runtime-capability"},
        )
        trace.append(
            _event(
                "serializeMOMServiceReport",
                serialNumber=service_report["serialNumber"],
                service=service_report["service"],
                serviceReportingEnabled=service_report["serviceReportingEnabled"],
            )
        )
        trace.extend(_callback_events(federate.events))
    finally:
        try:
            if joined:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", action=ResignAction.NO_ACTION))
            if federation_created:
                rti.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if connected:
                rti.disconnect()
                trace.append(_event("disconnect"))
        finally:
            close = getattr(rti, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "runtime-capability",
        "status": "trace-green",
        "requirements_exercised": _route_runtime_requirements_2025(backend_name),
        "trace": trace,
    }


def run_2025_time_management_trace(backend_name: str = "shim") -> dict[str, Any]:
    """Run a focused 2025 logical-time trace and return normalized evidence."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025 import CallbackModel, ResignAction
    from hla.rti1516_2025.time import HLAfloat64Interval, HLAfloat64Time

    federation_name = f"ShimRouteTime{backend_name.replace('-', '').title()}"
    fom_module = "TargetRadarFOMmodule.xml"
    rti = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=rti.backend_info.details.get("standard_backed")),
    ]
    rti.connect(object(), CallbackModel.HLA_EVOKED)
    trace.append(_event("connect"))
    rti.createFederationExecution(
        federation_name,
        fom_module,
        logicalTimeImplementationName="HLAfloat64Time",
    )
    trace.append(
        _event(
            "createFederationExecution",
            federation=federation_name,
            fomModule=fom_module,
            logicalTimeImplementationName="HLAfloat64Time",
        )
    )
    rti.joinFederationExecution("python-federate", "demo", federation_name)
    trace.append(_event("joinFederationExecution", federate="python-federate", federation=federation_name))
    time_factory = rti.getTimeFactory()
    trace.append(_event("getTimeFactory", factoryName=time_factory.getName()))
    rti.enableTimeRegulation(HLAfloat64Interval(0.5))
    trace.append(_event("enableTimeRegulation", lookahead=HLAfloat64Interval(0.5)))
    rti.enableTimeConstrained()
    trace.append(_event("enableTimeConstrained"))
    trace.append(_event("queryLookahead", value=rti.queryLookahead()))
    rti.modifyLookahead(HLAfloat64Interval(0.25))
    trace.append(_event("modifyLookahead", value=HLAfloat64Interval(0.25)))
    trace.append(_event("queryLookahead", value=rti.queryLookahead()))
    rti.timeAdvanceRequest(HLAfloat64Time(12.5))
    trace.append(_event("timeAdvanceRequest", value=HLAfloat64Time(12.5)))
    rti.flushQueueRequest(HLAfloat64Time(20.0))
    trace.append(_event("flushQueueRequest", value=HLAfloat64Time(20.0)))
    trace.append(_event("queryLogicalTime", value=rti.queryLogicalTime()))
    trace.append(_event("queryGALT", value=rti.queryGALT()))
    trace.append(_event("queryLITS", value=rti.queryLITS()))
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    trace.append(_event("resignFederationExecution", action=ResignAction.NO_ACTION))
    rti.destroyFederationExecution(federation_name)
    trace.append(_event("destroyFederationExecution", federation=federation_name))
    rti.disconnect()
    trace.append(_event("disconnect"))

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "logical-time-runtime",
        "status": "trace-green",
        "requirements_exercised": TIME_MANAGEMENT_REQUIREMENTS_2025,
        "trace": trace,
    }


__all__ = [
    "run_2025_time_management_trace",
    "run_standard_2010_exchange_trace",
    "run_standard_2025_lifecycle_trace",
    "run_standard_2025_runtime_capability_trace",
]
