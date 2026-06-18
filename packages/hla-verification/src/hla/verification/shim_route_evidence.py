"""MVP language-shim route evidence helpers."""
from __future__ import annotations

import shutil
import tempfile
import textwrap
import uuid
from collections.abc import Iterable
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

OWNERSHIP_REQUIREMENTS_2025 = [
    "HLA2025-FR-005",
    "HLA2025-FR-008",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
]

DDM_REQUIREMENTS_2025 = [
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
]

SUPPORT_SERVICES_REQUIREMENTS_2025 = [
    "HLA2025-FI-001",
    "HLA2025-MOD-007",
]

SAVE_RESTORE_REQUIREMENTS_2025 = [
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-REQ-002",
]

MOM_REQUIREMENTS_2025 = [
    "HLA2025-NEW-004",
    "HLA2025-FI-001",
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

    def discoverObjectInstance(self, objectInstance: Any, objectClass: Any, objectInstanceName: str, producingFederate: Any) -> None:  # noqa: N802
        self.events.append(("discover", (objectInstance, objectClass, objectInstanceName, producingFederate)))

    def reflectAttributeValues(  # noqa: N802
        self,
        objectInstance: Any,
        attributeValues: Any,
        userSuppliedTag: bytes,
        transportationType: Any,
        producingFederate: Any,
        optionalSentRegions: Any,
        time: Any = None,
        sentOrderType: Any = None,
        receivedOrderType: Any = None,
        optionalRetraction: Any = None,
    ) -> None:
        self.events.append(
            (
                "reflect",
                (
                    objectInstance,
                    attributeValues,
                    userSuppliedTag,
                    sentOrderType,
                    transportationType,
                    (producingFederate, optionalSentRegions, time, receivedOrderType, optionalRetraction),
                ),
            )
        )

    def receiveInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Any,
        userSuppliedTag: bytes,
        transportationType: Any,
        producingFederate: Any,
        optionalSentRegions: Any,
        time: Any = None,
        sentOrderType: Any = None,
        receivedOrderType: Any = None,
        optionalRetraction: Any = None,
    ) -> None:
        self.events.append(
            (
                "interaction",
                (
                    interactionClass,
                    parameterValues,
                    userSuppliedTag,
                    sentOrderType,
                    transportationType,
                    (producingFederate, optionalSentRegions, time, receivedOrderType, optionalRetraction),
                ),
            )
        )

    def timeRegulationEnabled(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeRegulationEnabled", time))

    def timeConstrainedEnabled(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeConstrainedEnabled", time))

    def timeAdvanceGrant(self, time: Any) -> None:  # noqa: N802
        self.events.append(("timeAdvanceGrant", time))

    def initiateFederateSave(self, label: str) -> None:  # noqa: N802
        self.events.append(("initiateFederateSave", label))

    def federationSaved(self) -> None:  # noqa: N802
        self.events.append(("federationSaved", ()))

    def federationNotSaved(self, reason: Any) -> None:  # noqa: N802
        self.events.append(("federationNotSaved", reason))

    def federationSaveStatusResponse(self, response: Any) -> None:  # noqa: N802
        self.events.append(("federationSaveStatusResponse", response))

    def requestFederationRestoreSucceeded(self, label: str) -> None:  # noqa: N802
        self.events.append(("requestFederationRestoreSucceeded", label))

    def requestFederationRestoreFailed(self, label: str) -> None:  # noqa: N802
        self.events.append(("requestFederationRestoreFailed", label))

    def federationRestoreBegun(self) -> None:  # noqa: N802
        self.events.append(("federationRestoreBegun", ()))

    def initiateFederateRestore(self, label: str, federateName: str, federateHandle: Any) -> None:  # noqa: N802
        self.events.append(("initiateFederateRestore", (label, federateName, federateHandle)))

    def federationRestored(self) -> None:  # noqa: N802
        self.events.append(("federationRestored", ()))

    def federationNotRestored(self, reason: Any) -> None:  # noqa: N802
        self.events.append(("federationNotRestored", reason))

    def federationRestoreStatusResponse(self, response: Any) -> None:  # noqa: N802
        self.events.append(("federationRestoreStatusResponse", response))

    def provideAttributeValueUpdate(self, objectInstance: Any, attributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self.events.append(("provideAttributeValueUpdate", (objectInstance, attributes, userSuppliedTag)))

    def momServiceReport(self, report: Any) -> None:  # noqa: N802
        self.events.append(("momServiceReport", report))

    def removeObjectInstance(  # noqa: N802
        self,
        objectInstance: Any,
        userSuppliedTag: bytes,
        producingFederate: Any,
        time: Any = None,
        sentOrderType: Any = None,
        receivedOrderType: Any = None,
        optionalRetraction: Any = None,
    ) -> None:
        self.events.append(
            (
                "removeObjectInstance",
                (objectInstance, userSuppliedTag, producingFederate, time, sentOrderType, receivedOrderType, optionalRetraction),
            )
        )

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


def _write_2025_object_exchange_fom() -> tuple[Path, Path]:
    temp_dir = Path(tempfile.mkdtemp(prefix="hla-2025-route-exchange-fom-"))
    fom = temp_dir / "RouteObjectExchange2025.xml"
    fom.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
              <modelIdentification>
                <name>Route Object Exchange 2025 FOM</name>
                <type>FOM</type>
                <version>1.0</version>
                <modificationDate>2026-01-01</modificationDate>
                <securityClassification>UNCLASSIFIED</securityClassification>
                <description>Object exchange route test FOM.</description>
                <poc>HLA-X</poc>
                <reference>HLA-X 2025 route object exchange trace</reference>
              </modelIdentification>
              <objects>
                <objectClass>
                  <name>HLAobjectRoot</name>
                  <objectClass>
                    <name>Target</name>
                    <sharing>PublishSubscribe</sharing>
                    <attribute>
                      <name>Position</name>
                      <dataType>HLAunicodeString</dataType>
                      <sharing>PublishSubscribe</sharing>
                      <transportation>HLAreliable</transportation>
                      <order>Receive</order>
                    </attribute>
                  </objectClass>
                </objectClass>
              </objects>
              <interactions>
                <interactionClass>
                  <name>HLAinteractionRoot</name>
                  <interactionClass>
                    <name>TrackReport</name>
                    <sharing>PublishSubscribe</sharing>
                    <transportation>HLAreliable</transportation>
                    <order>Receive</order>
                    <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
                  </interactionClass>
                </interactionClass>
              </interactions>
              <transportations>
                <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
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
            object_instance, attributes, tag, order, transport, extra = payload
            producing_federate = extra[0] if len(extra) > 0 else None
            sent_regions = extra[1] if len(extra) > 1 else None
            time = extra[2] if len(extra) > 2 else None
            received_order = extra[3] if len(extra) > 3 else None
            optional_retraction = extra[4] if len(extra) > 4 else None
            events.append(
                _event(
                    "reflectAttributeValues",
                    object=object_instance,
                    attributes=attributes,
                    tag=tag,
                    order=order,
                    transportation=transport,
                    producingFederate=producing_federate,
                    sentRegions=sent_regions,
                    time=time,
                    receivedOrder=received_order,
                    retraction=optional_retraction,
                )
            )
        elif name == "interaction":
            interaction_class, parameters, tag, order, transport, extra = payload
            producing_federate = extra[0] if len(extra) > 0 else None
            sent_regions = extra[1] if len(extra) > 1 else None
            time = extra[2] if len(extra) > 2 else None
            received_order = extra[3] if len(extra) > 3 else None
            optional_retraction = extra[4] if len(extra) > 4 else None
            events.append(
                _event(
                    "receiveInteraction",
                    interactionClass=interaction_class,
                    parameters=parameters,
                    tag=tag,
                    order=order,
                    transportation=transport,
                    producingFederate=producing_federate,
                    sentRegions=sent_regions,
                    time=time,
                    receivedOrder=received_order,
                    retraction=optional_retraction,
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


def run_standard_2025_object_exchange_trace(backend_name: str) -> dict[str, Any]:
    """Run a two-federate 2025 object/interaction exchange trace for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, ResignAction

    temp_dir, fom_module = _write_2025_object_exchange_fom()
    federation_name = f"ShimRouteExchange{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    publisher_fed = _Recording2025FederateAmbassador()
    subscriber_fed = _Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(spec="2025", backend=backend_name)
    subscriber = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=publisher.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=publisher.getHLAversion()),
    ]
    publisher_connected = False
    subscriber_connected = False
    publisher_joined = False
    subscriber_joined = False
    federation_created = False
    try:
        publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
        publisher_connected = True
        subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
        subscriber_connected = True
        trace.append(_event("connect", federates=["publisher", "subscriber"], callbackModel=CallbackModel.HLA_EVOKED))

        publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        publisher_handle = publisher.joinFederationExecution("route-publisher", "route-exchange", federation_name)
        publisher_joined = True
        subscriber_handle = subscriber.joinFederationExecution("route-subscriber", "route-exchange", federation_name)
        subscriber_joined = True
        trace.append(
            _event(
                "joinFederationExecution",
                publisherHandle=publisher_handle,
                subscriberHandle=subscriber_handle,
            )
        )

        object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
        attribute = publisher.getAttributeHandle(object_class, "Position")
        interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = publisher.getParameterHandle(interaction_class, "TrackId")
        trace.append(
            _event(
                "resolveExchangeHandles",
                objectClass=object_class,
                attribute=attribute,
                interactionClass=interaction_class,
                parameter=parameter,
            )
        )

        subscriber.subscribeObjectClassAttributes(object_class, {attribute})
        subscriber.subscribeInteractionClass(interaction_class)
        trace.append(_event("subscribe", objectClass=object_class, attributes={attribute}, interactionClass=interaction_class))
        object_instance = publisher.registerObjectInstance(object_class, f"RouteTarget-{uuid.uuid4().hex[:8]}")
        trace.append(_event("registerObjectInstance", objectClass=object_class, objectInstance=object_instance))

        publisher.publishObjectClassAttributes(object_class, {attribute})
        publisher.updateAttributeValues(object_instance, {attribute: b"123,456"}, b"route-update")
        trace.append(_event("updateAttributeValues", objectInstance=object_instance, attributes={attribute}, tag=b"route-update"))

        publisher.publishInteractionClass(interaction_class)
        publisher.sendInteraction(interaction_class, {parameter: b"TRACK-1"}, b"route-interaction")
        trace.append(_event("sendInteraction", interactionClass=interaction_class, parameters={parameter: b"TRACK-1"}, tag=b"route-interaction"))
        trace.extend(_callback_events(subscriber_fed.events))

        subscriber.unsubscribeObjectClassAttributes(object_class, {attribute})
        subscriber.unsubscribeInteractionClass(interaction_class)
        subscriber_fed.events.clear()
        publisher.updateAttributeValues(object_instance, {attribute: b"after-unsubscribe"}, b"route-update-after")
        publisher.sendInteraction(interaction_class, {parameter: b"TRACK-2"}, b"route-interaction-after")
        trace.append(
            _event(
                "unsubscribeSuppression",
                reflectedAfterUnsubscribe=any(event[0] == "reflect" for event in subscriber_fed.events),
                interactionAfterUnsubscribe=any(event[0] == "interaction" for event in subscriber_fed.events),
            )
        )
    finally:
        try:
            if subscriber_joined:
                subscriber.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="subscriber", action=ResignAction.NO_ACTION))
            if publisher_joined:
                publisher.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="publisher", action=ResignAction.NO_ACTION))
            if federation_created:
                publisher.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if subscriber_connected:
                subscriber.disconnect()
            if publisher_connected:
                publisher.disconnect()
            if subscriber_connected or publisher_connected:
                trace.append(_event("disconnect", federates=["publisher", "subscriber"]))
        finally:
            close = getattr(subscriber, "close", None)
            if callable(close):
                close()
            close = getattr(publisher, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "object-exchange",
        "status": "core-exchange-green",
        "requirements_exercised": CORE_EXCHANGE_REQUIREMENTS_2025,
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


def run_standard_2025_ownership_trace(backend_name: str) -> dict[str, Any]:
    """Run a two-federate 2025 ownership transfer trace for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, ResignAction

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteOwnership{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    owner_fed = _Recording2025FederateAmbassador()
    acquirer_fed = _Recording2025FederateAmbassador()
    owner = create_rti_ambassador(spec="2025", backend=backend_name)
    acquirer = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=owner.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=owner.getHLAversion()),
    ]
    owner_connected = False
    acquirer_connected = False
    owner_joined = False
    acquirer_joined = False
    federation_created = False
    try:
        owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
        owner_connected = True
        acquirer.connect(acquirer_fed, CallbackModel.HLA_EVOKED)
        acquirer_connected = True
        trace.append(_event("connect", federates=["owner", "acquirer"], callbackModel=CallbackModel.HLA_EVOKED))

        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        owner_handle = owner.joinFederationExecution("route-owner", "route-ownership", federation_name)
        owner_joined = True
        acquirer_handle = acquirer.joinFederationExecution("route-acquirer", "route-ownership", federation_name)
        acquirer_joined = True
        trace.append(_event("joinFederationExecution", ownerHandle=owner_handle, acquirerHandle=acquirer_handle))

        object_class = owner.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        attribute = owner.getAttributeHandle(object_class, "Position")
        object_instance = owner.registerObjectInstance(object_class, f"RouteOwnedTarget-{uuid.uuid4().hex[:8]}")
        trace.append(
            _event(
                "registerObjectInstance",
                objectClass=object_class,
                attribute=attribute,
                objectInstance=object_instance,
                ownerInitiallyOwns=owner.isAttributeOwnedByFederate(object_instance, attribute),
                acquirerInitiallyOwns=acquirer.isAttributeOwnedByFederate(object_instance, attribute),
            )
        )

        acquirer.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"blocked")
        trace.append(_event("attributeOwnershipAcquisitionIfAvailable", objectInstance=object_instance, attributes={attribute}, tag=b"blocked"))
        trace.extend(_callback_events(acquirer_fed.events))

        owner.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"divest")
        trace.append(
            _event(
                "unconditionalAttributeOwnershipDivestiture",
                objectInstance=object_instance,
                attributes={attribute},
                tag=b"divest",
                ownerStillOwns=owner.isAttributeOwnedByFederate(object_instance, attribute),
            )
        )
        owner.queryAttributeOwnership(object_instance, {attribute})
        trace.append(_event("queryAttributeOwnership", objectInstance=object_instance, attributes={attribute}, requester="owner"))
        trace.extend(_callback_events(owner_fed.events))

        acquirer_fed.events.clear()
        owner_fed.events.clear()
        acquirer.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"claim")
        trace.append(
            _event(
                "attributeOwnershipAcquisitionIfAvailable",
                objectInstance=object_instance,
                attributes={attribute},
                tag=b"claim",
                acquirerOwns=acquirer.isAttributeOwnedByFederate(object_instance, attribute),
            )
        )
        trace.extend(_callback_events(acquirer_fed.events))

        owner.queryAttributeOwnership(object_instance, {attribute})
        trace.append(_event("queryAttributeOwnership", objectInstance=object_instance, attributes={attribute}, requester="owner-after-transfer"))
        trace.extend(_callback_events(owner_fed.events))
    finally:
        try:
            if acquirer_joined:
                acquirer.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="acquirer", action=ResignAction.NO_ACTION))
            if owner_joined:
                owner.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="owner", action=ResignAction.NO_ACTION))
            if federation_created:
                owner.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if acquirer_connected:
                acquirer.disconnect()
            if owner_connected:
                owner.disconnect()
            if acquirer_connected or owner_connected:
                trace.append(_event("disconnect", federates=["owner", "acquirer"]))
        finally:
            close = getattr(acquirer, "close", None)
            if callable(close):
                close()
            close = getattr(owner, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "ownership-runtime",
        "status": "trace-green",
        "requirements_exercised": OWNERSHIP_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_ddm_trace(backend_name: str) -> dict[str, Any]:
    """Run a two-federate 2025 object DDM region-overlap trace for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, ResignAction

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteDdm{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    publisher_fed = _Recording2025FederateAmbassador()
    subscriber_fed = _Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(spec="2025", backend=backend_name)
    subscriber = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=publisher.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=publisher.getHLAversion()),
    ]
    publisher_connected = False
    subscriber_connected = False
    publisher_joined = False
    subscriber_joined = False
    federation_created = False
    try:
        publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
        publisher_connected = True
        subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
        subscriber_connected = True
        trace.append(_event("connect", federates=["publisher", "subscriber"], callbackModel=CallbackModel.HLA_EVOKED))

        publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        publisher_handle = publisher.joinFederationExecution("route-publisher", "route-ddm", federation_name)
        publisher_joined = True
        subscriber_handle = subscriber.joinFederationExecution("route-subscriber", "route-ddm", federation_name)
        subscriber_joined = True
        trace.append(_event("joinFederationExecution", publisherHandle=publisher_handle, subscriberHandle=subscriber_handle))

        object_class = publisher.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        attribute = publisher.getAttributeHandle(object_class, "Position")
        dimension = publisher.getDimensionHandle("RoutingSpace")
        subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
        publisher.publishObjectClassAttributes(object_class, {attribute})
        trace.append(_event("publishObjectClassAttributes", objectClass=object_class, attributes={attribute}))

        publisher_region = publisher.createRegion({dimension})
        subscriber_region = subscriber.createRegion({subscriber_dimension})
        publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
        subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
        publisher.commitRegionModifications({publisher_region})
        subscriber.commitRegionModifications({subscriber_region})
        trace.append(
            _event(
                "createAndCommitRegions",
                publisherRegion=publisher_region,
                subscriberRegion=subscriber_region,
                publisherBounds=RangeBounds(0, 10),
                subscriberBounds=RangeBounds(50, 60),
            )
        )

        object_instance = publisher.registerObjectInstance(object_class, f"RouteDdmTarget-{uuid.uuid4().hex[:8]}")
        publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
        subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
        trace.append(
            _event(
                "subscribeObjectClassAttributesWithRegions",
                objectClass=object_class,
                attributes={attribute},
                subscriberRegion=subscriber_region,
                overlapsPublisherRegion=False,
                discovered=any(event[0] == "discover" for event in subscriber_fed.events),
            )
        )

        publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-region")
        trace.append(
            _event(
                "outsideRegionUpdateSuppressed",
                objectInstance=object_instance,
                reflected=any(event[0] == "reflect" for event in subscriber_fed.events),
            )
        )

        subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
        subscriber.commitRegionModifications({subscriber_region})
        subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
        trace.append(
            _event(
                "commitOverlappingRegion",
                subscriberRegion=subscriber_region,
                subscriberBounds=RangeBounds(5, 15),
                discovered=any(event[0] == "discover" for event in subscriber_fed.events),
            )
        )
        trace.extend(_callback_events(subscriber_fed.events))

        subscriber_fed.events.clear()
        publisher.updateAttributeValues(object_instance, {attribute: b"inside"}, b"inside-region")
        trace.append(_event("insideRegionUpdate", objectInstance=object_instance, attributes={attribute}, publisherRegion=publisher_region))
        trace.extend(_callback_events(subscriber_fed.events))
    finally:
        try:
            if subscriber_joined:
                subscriber.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="subscriber", action=ResignAction.NO_ACTION))
            if publisher_joined:
                publisher.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="publisher", action=ResignAction.NO_ACTION))
            if federation_created:
                publisher.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if subscriber_connected:
                subscriber.disconnect()
            if publisher_connected:
                publisher.disconnect()
            if subscriber_connected or publisher_connected:
                trace.append(_event("disconnect", federates=["publisher", "subscriber"]))
        finally:
            close = getattr(subscriber, "close", None)
            if callable(close):
                close()
            close = getattr(publisher, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "ddm-region-runtime",
        "status": "trace-green",
        "requirements_exercised": DDM_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_support_services_trace(backend_name: str) -> dict[str, Any]:
    """Run a focused 2025 support-services lookup/control trace for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteSupport{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
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
        rti.connect(federate, CallbackModel.HLA_EVOKED)
        connected = True
        trace.append(_event("connect", callbackModel=CallbackModel.HLA_EVOKED))
        rti.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        federate_handle = rti.joinFederationExecution("route-support", "route-support", federation_name)
        joined = True
        trace.append(_event("joinFederationExecution", federateHandle=federate_handle))

        object_class = rti.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        attribute = rti.getAttributeHandle(object_class, "Position")
        rti.publishObjectClassAttributes(object_class, {attribute})
        object_instance_name = f"RouteSupportTarget-{uuid.uuid4().hex[:8]}"
        object_instance = rti.registerObjectInstance(object_class, object_instance_name)
        dimension = rti.getDimensionHandle("RoutingSpace")
        transportation = rti.getTransportationTypeHandle("HLAreliable")

        trace.append(
            _event(
                "supportLookupRoundTrip",
                federateHandle=rti.getFederateHandle("route-support"),
                federateName=rti.getFederateName(federate_handle),
                normalizedFederateHandle=rti.normalizeFederateHandle(federate_handle),
                objectClassName=rti.getObjectClassName(object_class),
                attributeName=rti.getAttributeName(object_class, attribute),
                objectInstanceName=rti.getObjectInstanceName(object_instance),
                objectInstanceHandle=rti.getObjectInstanceHandle(object_instance_name),
                knownObjectClass=rti.getKnownObjectClassHandle(object_instance),
                dimensionName=rti.getDimensionName(dimension),
                dimensionUpperBound=rti.getDimensionUpperBound(dimension),
                availableDimensions=rti.getAvailableDimensionsForObjectClass(object_class),
                transportationName=rti.getTransportationTypeName(transportation),
                orderName=rti.getOrderName(OrderType.RECEIVE),
                orderType=rti.getOrderType("HLAtimestamp"),
                timeFactoryName=rti.getTimeFactory().getName(),
            )
        )

        rti.setServiceReportingSwitch(True)
        rti.setExceptionReportingSwitch(False)
        rti.setConveyRegionDesignatorSetsSwitch(False)
        trace.append(
            _event(
                "supportSwitchRoundTrip",
                serviceReporting=rti.getServiceReportingSwitch(),
                exceptionReporting=rti.getExceptionReportingSwitch(),
                conveyRegionDesignatorSets=rti.getConveyRegionDesignatorSetsSwitch(),
            )
        )
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
        "scenario": "support-services-runtime",
        "status": "trace-green",
        "requirements_exercised": SUPPORT_SERVICES_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_save_restore_trace(backend_name: str) -> dict[str, Any]:
    """Run a two-federate 2025 save/restore trace for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, ResignAction

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteSaveRestore{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    leader_fed = _Recording2025FederateAmbassador()
    wing_fed = _Recording2025FederateAmbassador()
    leader = create_rti_ambassador(spec="2025", backend=backend_name)
    wing = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=leader.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=leader.getHLAversion()),
    ]
    leader_connected = False
    wing_connected = False
    leader_joined = False
    wing_joined = False
    federation_created = False
    try:
        leader.connect(leader_fed, CallbackModel.HLA_EVOKED)
        leader_connected = True
        wing.connect(wing_fed, CallbackModel.HLA_EVOKED)
        wing_connected = True
        trace.append(_event("connect", federates=["leader", "wing"], callbackModel=CallbackModel.HLA_EVOKED))

        leader.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        leader_handle = leader.joinFederationExecution("route-leader", "route-save-restore", federation_name)
        leader_joined = True
        wing_handle = wing.joinFederationExecution("route-wing", "route-save-restore", federation_name)
        wing_joined = True
        trace.append(_event("joinFederationExecution", leaderHandle=leader_handle, wingHandle=wing_handle))

        object_class = leader.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        attribute = leader.getAttributeHandle(object_class, "Position")
        wing_object_class = wing.getObjectClassHandle("HLAobjectRoot.RouteTarget")
        wing_attribute = wing.getAttributeHandle(wing_object_class, "Position")
        leader.publishObjectClassAttributes(object_class, {attribute})
        wing.subscribeObjectClassAttributes(wing_object_class, {wing_attribute})
        object_instance = leader.registerObjectInstance(object_class, f"RouteSavedTarget-{uuid.uuid4().hex[:8]}")
        leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(5))
        trace.append(_event("preparedState", objectInstance=object_instance, logicalTime=leader.queryLogicalTime()))

        leader.requestFederationSave("SAVE-1")
        trace.append(
            _event(
                "requestFederationSave",
                label="SAVE-1",
                leaderInitiated=any(event == ("initiateFederateSave", "SAVE-1") for event in leader_fed.events),
                wingInitiated=any(event == ("initiateFederateSave", "SAVE-1") for event in wing_fed.events),
            )
        )
        leader.federateSaveBegun()
        wing.federateSaveBegun()
        leader.queryFederationSaveStatus()
        trace.append(_event("queryFederationSaveStatus", response=leader_fed.events[-1][1]))
        leader.federateSaveComplete()
        wing.federateSaveComplete()
        trace.append(
            _event(
                "federationSaved",
                leaderSaved=any(name == "federationSaved" for name, _payload in leader_fed.events),
                wingSaved=any(name == "federationSaved" for name, _payload in wing_fed.events),
            )
        )

        leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(9))
        leader.deleteObjectInstance(object_instance, b"deleted-after-save")
        trace.append(_event("mutatedAfterSave", logicalTime=leader.queryLogicalTime(), objectDeleted=True))

        leader.requestFederationRestore("MISSING-SAVE")
        trace.append(_event("requestFederationRestoreFailed", label=leader_fed.events[-1][1]))
        leader.requestFederationRestore("SAVE-1")
        trace.append(
            _event(
                "requestFederationRestore",
                label="SAVE-1",
                leaderSucceeded=any(event == ("requestFederationRestoreSucceeded", "SAVE-1") for event in leader_fed.events),
                leaderBegun=any(name == "federationRestoreBegun" for name, _payload in leader_fed.events),
                wingInitiated=any(name == "initiateFederateRestore" for name, _payload in wing_fed.events),
            )
        )
        leader.queryFederationRestoreStatus()
        trace.append(_event("queryFederationRestoreStatus", response=leader_fed.events[-1][1]))
        leader.federateRestoreComplete()
        wing.federateRestoreComplete()
        trace.append(
            _event(
                "federationRestored",
                leaderRestored=any(name == "federationRestored" for name, _payload in leader_fed.events),
                wingRestored=any(name == "federationRestored" for name, _payload in wing_fed.events),
                restoredLogicalTime=leader.queryLogicalTime(),
                restoredObjectName=leader.getObjectInstanceName(object_instance),
            )
        )

        wing.requestAttributeValueUpdate(object_instance, {wing_attribute}, b"after-restore")
        trace.append(_event("restoredObjectProvidesUpdate", callback=leader_fed.events[-1]))
    finally:
        try:
            if wing_joined:
                wing.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="wing", action=ResignAction.NO_ACTION))
            if leader_joined:
                leader.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="leader", action=ResignAction.NO_ACTION))
            if federation_created:
                leader.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if wing_connected:
                wing.disconnect()
            if leader_connected:
                leader.disconnect()
            if wing_connected or leader_connected:
                trace.append(_event("disconnect", federates=["leader", "wing"]))
        finally:
            close = getattr(wing, "close", None)
            if callable(close):
                close()
            close = getattr(leader, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "save-restore-runtime",
        "status": "trace-green",
        "requirements_exercised": SAVE_RESTORE_REQUIREMENTS_2025,
        "trace": trace,
    }


def run_standard_2025_mom_trace(backend_name: str) -> dict[str, Any]:
    """Run representative 2025 MOM report/request/adjust slices for a standard route."""

    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import CallbackModel, ResignAction

    temp_dir, fom_module = _write_2025_runtime_capability_fom()
    federation_name = f"ShimRouteMom{backend_name.replace('-', '').title()}{uuid.uuid4().hex[:8]}"
    source_fed = _Recording2025FederateAmbassador()
    observer_fed = _Recording2025FederateAmbassador()
    source = create_rti_ambassador(spec="2025", backend=backend_name)
    observer = create_rti_ambassador(spec="2025", backend=backend_name)
    trace = [
        _event("routeSelected", backend=backend_name, spec="rti1516_2025", standardBacked=source.backend_info.details.get("standard_backed")),
        _event("getHLAversion", value=source.getHLAversion()),
    ]
    source_connected = False
    observer_connected = False
    source_joined = False
    observer_joined = False
    federation_created = False
    try:
        source.connect(source_fed, CallbackModel.HLA_EVOKED)
        source_connected = True
        observer.connect(observer_fed, CallbackModel.HLA_EVOKED)
        observer_connected = True
        trace.append(_event("connect", federates=["source", "observer"], callbackModel=CallbackModel.HLA_EVOKED))

        source.createFederationExecution(federationName=federation_name, fomModule=str(fom_module))
        federation_created = True
        trace.append(_event("createFederationExecution", federation=federation_name, fomModule=fom_module.name))
        source_handle = source.joinFederationExecution("route-mom-source", "route-mom", federation_name)
        source_joined = True
        observer_handle = observer.joinFederationExecution("route-mom-observer", "route-mom", federation_name)
        observer_joined = True
        trace.append(_event("joinFederationExecution", sourceHandle=source_handle, observerHandle=observer_handle))

        source.setServiceReportingSwitch(True)
        observer.setServiceReportingSwitch(True)
        report = source.serializeMOMServiceReport(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches",
            arguments={"HLAserviceReporting": True, "HLAfederate": source_handle},
            result={"status": "serialized"},
        )
        trace.append(
            _event(
                "serializeMOMServiceReport",
                recordType=report["recordType"],
                serialNumber=report["serialNumber"],
                service=report["service"],
                observerReceived=any(name == "momServiceReport" and payload == report for name, payload in observer_fed.events),
            )
        )

        fom_request = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData"
        )
        fom_report = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData"
        )
        request_indicator = observer.getParameterHandle(fom_request, "HLAFOMmoduleIndicator")
        report_data = observer.getParameterHandle(fom_report, "HLAFOMmoduleData")
        observer.subscribeInteractionClass(fom_report)
        observer_fed.events.clear()
        observer.sendInteraction(fom_request, {request_indicator: b"0"}, b"mom-fom-module-request")
        fom_callback = next(payload for name, payload in reversed(observer_fed.events) if name == "interaction")
        trace.append(
            _event(
                "momFomModuleReport",
                reportClass=fom_callback[0],
                containsRouteFom=b"Route Capability 2025 FOM" in fom_callback[1][report_data],
                tag=fom_callback[2],
            )
        )

        mim_request = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
        )
        mim_report = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
        )
        mim_data = observer.getParameterHandle(mim_report, "HLAMIMdata")
        observer.subscribeInteractionClass(mim_report)
        observer_fed.events.clear()
        observer.sendInteraction(mim_request, {}, b"mom-mim-request")
        mim_callback = next(payload for name, payload in reversed(observer_fed.events) if name == "interaction")
        trace.append(
            _event(
                "momMimReport",
                reportClass=mim_callback[0],
                containsStandardMim=b"Standard MOM and Initialization Module" in mim_callback[1][mim_data],
                containsRequestMimData=b"HLArequestMIMdata" in mim_callback[1][mim_data],
                tag=mim_callback[2],
            )
        )

        service_adjust = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
        )
        service_target = observer.getParameterHandle(service_adjust, "HLAfederate")
        service_state = observer.getParameterHandle(service_adjust, "HLAreportingState")
        source.setServiceReportingSwitch(False)
        observer.sendInteraction(
            service_adjust,
            {
                service_target: str(source_handle.value).encode("ascii"),
                service_state: b"HLAtrue",
            },
            b"mom-enable-service-reporting",
        )
        trace.append(
            _event(
                "momAdjustServiceReporting",
                targetFederate=source_handle,
                sourceServiceReporting=source.getServiceReportingSwitch(),
            )
        )
    finally:
        try:
            if observer_joined:
                observer.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="observer", action=ResignAction.NO_ACTION))
            if source_joined:
                source.resignFederationExecution(ResignAction.NO_ACTION)
                trace.append(_event("resignFederationExecution", federate="source", action=ResignAction.NO_ACTION))
            if federation_created:
                source.destroyFederationExecution(federation_name)
                trace.append(_event("destroyFederationExecution", federation=federation_name))
            if observer_connected:
                observer.disconnect()
            if source_connected:
                source.disconnect()
            if observer_connected or source_connected:
                trace.append(_event("disconnect", federates=["source", "observer"]))
        finally:
            close = getattr(observer, "close", None)
            if callable(close):
                close()
            close = getattr(source, "close", None)
            if callable(close):
                close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "route": backend_name,
        "edition": "2025",
        "scenario": "mom-runtime",
        "status": "trace-green",
        "requirements_exercised": MOM_REQUIREMENTS_2025,
        "trace": trace,
    }


__all__ = [
    "run_2025_time_management_trace",
    "run_standard_2010_exchange_trace",
    "run_standard_2025_ddm_trace",
    "run_standard_2025_lifecycle_trace",
    "run_standard_2025_mom_trace",
    "run_standard_2025_object_exchange_trace",
    "run_standard_2025_ownership_trace",
    "run_standard_2025_runtime_capability_trace",
    "run_standard_2025_save_restore_trace",
    "run_standard_2025_support_services_trace",
]
