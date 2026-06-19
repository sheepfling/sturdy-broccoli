from __future__ import annotations

import inspect
import json
import struct
import uuid
import xml.etree.ElementTree as ET
from importlib.resources import files
from pathlib import Path

import pytest


class Recording2025FederateAmbassador:
    def __init__(self) -> None:
        self.callbacks: list[tuple[str, tuple[object, ...]]] = []

    def connectionLost(self, faultDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("connectionLost", (faultDescription,)))

    def reportFederationExecutions(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutions", (report,)))

    def reportFederationExecutionMembers(self, federationName, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionMembers", (federationName, report)))

    def reportFederationExecutionDoesNotExist(self, federationName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionDoesNotExist", (federationName,)))

    def federateResigned(self, reasonForResignDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federateResigned", (reasonForResignDescription,)))

    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("synchronizationPointRegistrationSucceeded", (synchronizationPointLabel,)))

    def synchronizationPointRegistrationFailed(self, synchronizationPointLabel, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("synchronizationPointRegistrationFailed", (synchronizationPointLabel, reason)))

    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("announceSynchronizationPoint", (synchronizationPointLabel, userSuppliedTag)))

    def federationSynchronized(self, synchronizationPointLabel, failedToSyncSet) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationSynchronized", (synchronizationPointLabel, failedToSyncSet)))

    def initiateFederateSave(self, label, time=None) -> None:  # noqa: N802, ANN001
        args = (label,) if time is None else (label, time)
        self.callbacks.append(("initiateFederateSave", args))

    def federationSaved(self) -> None:  # noqa: N802
        self.callbacks.append(("federationSaved", ()))

    def federationNotSaved(self, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationNotSaved", (reason,)))

    def federationSaveStatusResponse(self, response) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationSaveStatusResponse", (response,)))

    def requestFederationRestoreSucceeded(self, label) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestFederationRestoreSucceeded", (label,)))

    def requestFederationRestoreFailed(self, label) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestFederationRestoreFailed", (label,)))

    def federationRestoreBegun(self) -> None:  # noqa: N802
        self.callbacks.append(("federationRestoreBegun", ()))

    def initiateFederateRestore(self, label, federateName, postRestoreFederateHandle) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("initiateFederateRestore", (label, federateName, postRestoreFederateHandle)))

    def federationRestored(self) -> None:  # noqa: N802
        self.callbacks.append(("federationRestored", ()))

    def federationNotRestored(self, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationNotRestored", (reason,)))

    def federationRestoreStatusResponse(self, response) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationRestoreStatusResponse", (response,)))

    def timeRegulationEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeRegulationEnabled", (time,)))

    def timeConstrainedEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeConstrainedEnabled", (time,)))

    def timeAdvanceGrant(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeAdvanceGrant", (time,)))

    def flushQueueGrant(self, time, optimisticTime) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("flushQueueGrant", (time, optimisticTime)))

    def requestRetraction(self, retraction) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestRetraction", (retraction,)))

    def momServiceReport(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("momServiceReport", (report,)))

    def objectInstanceNameReservationSucceeded(self, objectInstanceName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("objectInstanceNameReservationSucceeded", (objectInstanceName,)))

    def objectInstanceNameReservationFailed(self, objectInstanceName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("objectInstanceNameReservationFailed", (objectInstanceName,)))

    def multipleObjectInstanceNameReservationSucceeded(self, objectInstanceNames) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("multipleObjectInstanceNameReservationSucceeded", (objectInstanceNames,)))

    def multipleObjectInstanceNameReservationFailed(self, objectInstanceNames) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("multipleObjectInstanceNameReservationFailed", (objectInstanceNames,)))

    def discoverObjectInstance(self, objectInstance, objectClass, objectInstanceName, producingFederate) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("discoverObjectInstance", (objectInstance, objectClass, objectInstanceName, producingFederate)))

    def reflectAttributeValues(  # noqa: N802, ANN001
        self,
        objectInstance,
        attributeValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        optionalSentRegions,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "reflectAttributeValues",
                (
                    objectInstance,
                    attributeValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    optionalSentRegions,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def receiveInteraction(  # noqa: N802, ANN001
        self,
        interactionClass,
        parameterValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        optionalSentRegions,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "receiveInteraction",
                (
                    interactionClass,
                    parameterValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    optionalSentRegions,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def receiveDirectedInteraction(  # noqa: N802, ANN001
        self,
        interactionClass,
        objectInstance,
        parameterValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "receiveDirectedInteraction",
                (
                    interactionClass,
                    objectInstance,
                    parameterValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def removeObjectInstance(  # noqa: N802, ANN001
        self,
        objectInstance,
        userSuppliedTag,
        producingFederate,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "removeObjectInstance",
                (
                    objectInstance,
                    userSuppliedTag,
                    producingFederate,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def attributesInScope(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributesInScope", (objectInstance, attributes)))

    def attributesOutOfScope(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributesOutOfScope", (objectInstance, attributes)))

    def provideAttributeValueUpdate(self, objectInstance, attributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("provideAttributeValueUpdate", (objectInstance, attributes, userSuppliedTag)))

    def confirmAttributeTransportationTypeChange(self, objectInstance, attributes, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmAttributeTransportationTypeChange", (objectInstance, attributes, transportationType)))

    def reportAttributeTransportationType(self, objectInstance, attribute, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportAttributeTransportationType", (objectInstance, attribute, transportationType)))

    def confirmInteractionTransportationTypeChange(self, interactionClass, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmInteractionTransportationTypeChange", (interactionClass, transportationType)))

    def reportInteractionTransportationType(self, federate, interactionClass, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportInteractionTransportationType", (federate, interactionClass, transportationType)))

    def attributeOwnershipAcquisitionNotification(  # noqa: N802, ANN001
        self,
        objectInstance,
        securedAttributes,
        userSuppliedTag,
    ) -> None:
        self.callbacks.append(("attributeOwnershipAcquisitionNotification", (objectInstance, securedAttributes, userSuppliedTag)))

    def attributeOwnershipUnavailable(self, objectInstance, attributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributeOwnershipUnavailable", (objectInstance, attributes, userSuppliedTag)))

    def requestAttributeOwnershipAssumption(self, objectInstance, offeredAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestAttributeOwnershipAssumption", (objectInstance, offeredAttributes, userSuppliedTag)))

    def requestDivestitureConfirmation(self, objectInstance, releasedAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestDivestitureConfirmation", (objectInstance, releasedAttributes, userSuppliedTag)))

    def requestAttributeOwnershipRelease(self, objectInstance, candidateAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestAttributeOwnershipRelease", (objectInstance, candidateAttributes, userSuppliedTag)))

    def confirmAttributeOwnershipAcquisitionCancellation(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmAttributeOwnershipAcquisitionCancellation", (objectInstance, attributes)))

    def informAttributeOwnership(self, objectInstance, attributes, owner) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("informAttributeOwnership", (objectInstance, attributes, owner)))

    def attributeIsNotOwned(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributeIsNotOwned", (objectInstance, attributes)))

    def last_callback(self, method_name: str) -> tuple[object, ...] | None:
        for recorded_name, args in reversed(self.callbacks):
            if recorded_name == method_name:
                return args
        return None


def _callbacks_named_2025(
    federate: Recording2025FederateAmbassador,
    method_name: str,
) -> list[tuple[object, ...]]:
    return [args for recorded_name, args in federate.callbacks if recorded_name == method_name]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004")
def test_2025_spec_package_exposes_authoritative_surface_without_replacing_2010() -> None:
    import hla.rti1516_2025 as rti2025
    import hla.rti1516e as rti1516e
    from hla.rti1516_2025.plugin import plugin as rti2025_plugin

    assert rti2025.RTIambassador is not rti1516e.RTIambassador
    assert rti2025.FederateAmbassador is not rti1516e.FederateAmbassador
    assert hasattr(rti2025, "RtiConfiguration")
    assert hasattr(rti2025, "Credentials")
    assert hasattr(rti2025, "AuthorizationResultCode")
    assert hasattr(rti2025, "InconsistentFOM")
    assert not hasattr(rti1516e, "RtiConfiguration")
    assert "grpc" in rti2025_plugin().spec.capabilities


@pytest.mark.requirements("HLA2025-REQ-001")
def test_2025_spec_aliases_and_backend_discovery_are_spec_aware() -> None:
    from hla.rti import discover_rti_backends, resolve_spec

    spec = resolve_spec("hla4")
    assert spec.name == "rti1516_2025"
    assert spec.year == 2025
    assert spec.python_package == "hla.rti1516_2025"

    backends = {row.name: row for row in discover_rti_backends(spec="1516-2025")}
    assert set(backends) == {
        "cpp-shim-grpc",
        "cpp-shim-pybind",
        "cpp-2025-sdk-grpc",
        "cpp-2025-sdk-pybind",
        "cpp-standard-2025-grpc",
        "cpp-standard-2025-pybind",
        "java-2025-jpype",
        "java-2025-py4j",
        "java-shim-jpype",
        "java-shim-py4j",
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "shim",
    }
    assert backends["shim"].supports == ("rti1516_2025",)
    assert backends["java-shim-jpype"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-shim-py4j"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-pybind"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-grpc"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-standard-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-standard-2025-py4j"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-grpc"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-grpc"].supports == ("rti1516_2025",)
    assert backends["java-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-2025-py4j"].supports == ("rti1516_2025",)


@pytest.mark.requirements("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001")
def test_2025_callback_surface_uses_direct_context_parameters_not_supplemental_helpers() -> None:
    import hla.rti1516_2025 as rti2025
    from hla.rti1516_2025.federate_ambassador import FederateAmbassador

    callback_parameters = {
        "discoverObjectInstance": ("objectInstance", "objectClass", "objectInstanceName", "producingFederate"),
        "reflectAttributeValues": (
            "objectInstance",
            "attributeValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "optionalSentRegions",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "receiveInteraction": (
            "interactionClass",
            "parameterValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "optionalSentRegions",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "receiveDirectedInteraction": (
            "interactionClass",
            "objectInstance",
            "parameterValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "removeObjectInstance": (
            "objectInstance",
            "userSuppliedTag",
            "producingFederate",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
    }

    for method_name, expected in callback_parameters.items():
        signature = inspect.signature(getattr(FederateAmbassador, method_name))
        assert tuple(name for name in signature.parameters if name != "self") == expected
        assert not any("Supplemental" in name for name in signature.parameters)

    assert not hasattr(rti2025, "SupplementalReflectInfo")
    assert not hasattr(rti2025, "SupplementalReceiveInfo")
    assert not hasattr(rti2025, "SupplementalRemoveInfo")


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-MOD-004",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-035",
    "HLA2025-FI-SVC-036",
    "HLA2025-FI-SVC-041",
    "HLA2025-FI-SVC-042",
    "HLA2025-FI-SVC-047",
    "HLA2025-FI-SVC-049",
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-058",
    "HLA2025-FI-SVC-059",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-061",
    "HLA2025-FI-SVC-062",
    "HLA2025-FI-SVC-123",
    "HLA2025-FI-SVC-124",
    "HLA2025-FI-SVC-125",
)
def test_2025_shim_runs_two_federate_object_and_interaction_exchange(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished, ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "Exchange2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Exchange 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused exchange fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
""",
        encoding="utf-8",
    )

    federation_name = f"shim-exchange-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    subscriber.subscribeObjectClassAttributes(object_class, {attribute})
    subscriber.subscribeInteractionClass(interaction_class)
    object_instance = publisher.registerObjectInstance(object_class, "Target-Exchange-1")
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "Target-Exchange-1",
        publisher_handle,
    )

    with pytest.raises(ObjectClassNotPublished):
        publisher.updateAttributeValues(object_instance, {attribute: b"blocked"}, b"not-published")
    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
    publisher.updateAttributeValues(object_instance, {attribute: b"123,456"}, b"update-tag")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"123,456"},
        b"update-tag",
        reliable,
        publisher_handle,
        set(),
    )
    assert reflection[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)

    publisher.changeAttributeOrderType(object_instance, {attribute}, OrderType.RECEIVE)
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"receive-ordered"}, b"receive-order-tag")
    receive_order_reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert receive_order_reflection is not None
    assert receive_order_reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    with pytest.raises(InteractionClassNotPublished):
        publisher.sendInteraction(interaction_class, {parameter: b"T-1"}, b"not-published")
    publisher.publishInteractionClass(interaction_class)
    publisher.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)
    publisher.sendInteraction(interaction_class, {parameter: b"T-1"}, b"interaction-tag")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        {parameter: b"T-1"},
        b"interaction-tag",
        reliable,
        publisher_handle,
        set(),
    )
    assert received[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)

    subscriber.unsubscribeObjectClassAttributes(object_class, {attribute})
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"after-unsubscribe"}, b"update-after")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    subscriber.unsubscribeInteractionClass(interaction_class)
    publisher.sendInteraction(interaction_class, {parameter: b"T-2"}, b"interaction-after")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-MOD-006",
    "HLA2025-MOD-007",
    "HLA2025-FI-SVC-037",
    "HLA2025-FI-SVC-038",
    "HLA2025-FI-SVC-043",
    "HLA2025-FI-SVC-044",
)
def test_2025_shim_passive_and_universal_subscription_aliases_match_active_exchange(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "AliasExchange2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Alias Exchange 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Passive and universal alias exchange fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
""",
        encoding="utf-8",
    )

    federation_name = f"shim-alias-exchange-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("AliasPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("AliasSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    object_instance = publisher.registerObjectInstance(object_class, "AliasTarget-1")

    subscriber.subscribeObjectClassAttributesPassively(object_class, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "AliasTarget-1",
        publisher_handle,
    )

    publisher.publishObjectClassAttributes(object_class, {attribute})
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"alias-position"}, b"alias-update")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"alias-position"},
        b"alias-update",
        reliable,
        publisher_handle,
        set(),
    )
    assert reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.subscribeInteractionClassPassively(interaction_class)
    publisher.publishInteractionClass(interaction_class)
    subscriber_callbacks.callbacks.clear()
    publisher.sendInteraction(interaction_class, {parameter: b"passive-track"}, b"passive-interaction")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        {parameter: b"passive-track"},
        b"passive-interaction",
        reliable,
        publisher_handle,
        set(),
    )
    assert received[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.subscribeObjectClassDirectedInteractionsUniversally(object_class, {interaction_class})
    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber_callbacks.callbacks.clear()
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"universal-track"}, b"universal-directed")
    directed = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert directed is not None
    assert directed[:6] == (
        interaction_class,
        object_instance,
        {parameter: b"universal-track"},
        b"universal-directed",
        reliable,
        publisher_handle,
    )
    assert directed[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-FI-005", "HLA2025-FI-006", "HLA2025-FI-SVC-001", "HLA2025-FI-SVC-002")
def test_2025_shim_is_first_green_runtime_path() -> None:
    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel
    from hla.rti1516_2025.exceptions import FederateNotExecutionMember, NotConnected

    rti = create_rti_ambassador(spec="2025", backend="shim")
    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert rti.getHLAversion() == "IEEE 1516.1-2025"

    with pytest.raises(NotConnected):
        rti.evokeCallback(0.0)

    result = rti.connect(object(), CallbackModel.HLA_EVOKED)
    assert result.additionalSettingsResultCode is AdditionalSettingsResultCode.SETTINGS_IGNORED
    assert rti.connected is True
    assert rti.evokeMultipleCallbacks(0.0, 0.1) is False

    with pytest.raises(FederateNotExecutionMember, match="publishObjectClassAttributes"):
        rti.publishObjectClassAttributes(object(), object())

    rti.disconnect()
    assert rti.connected is False


@pytest.mark.requirements("HLA2025-FI-SVC-003")
def test_2025_shim_connection_lost_callback_tears_down_connection() -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import NotConnected
    from hla.rti1516_2025.factory import create_rti_ambassador

    callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    rti.connect(callbacks, CallbackModel.HLA_EVOKED)

    rti.forceConnectionLost("transport fault")

    assert callbacks.last_callback("connectionLost") == ("transport fault",)
    assert rti.connected is False
    with pytest.raises(NotConnected):
        rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-193",
    "HLA2025-FI-SVC-194",
    "HLA2025-FI-SVC-195",
    "HLA2025-FI-SVC-196",
)
def test_2025_shim_enable_disable_callbacks_controls_evoked_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "CallbackControl2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Callback Control 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused callback control fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>CallbackPing</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>Value</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-callback-control-{uuid.uuid4().hex[:8]}"
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.CallbackPing")
    parameter = publisher.getParameterHandle(interaction_class, "Value")
    publisher.publishInteractionClass(interaction_class)
    subscriber.subscribeInteractionClass(interaction_class)

    subscriber.disableCallbacks()
    publisher.sendInteraction(interaction_class, {parameter: b"one"}, b"queued-one")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None
    assert subscriber.evokeCallback(0.0) is False

    subscriber.enableCallbacks()
    assert subscriber.evokeCallback(0.0) is True
    first = subscriber_callbacks.last_callback("receiveInteraction")
    assert first is not None
    assert first[:3] == (interaction_class, {parameter: b"one"}, b"queued-one")
    assert first[4] == publisher_handle

    subscriber_callbacks.callbacks.clear()
    subscriber.disableCallbacks()
    publisher.sendInteraction(interaction_class, {parameter: b"two"}, b"queued-two")
    publisher.sendInteraction(interaction_class, {parameter: b"three"}, b"queued-three")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.enableCallbacks()
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is True
    received_tags = [
        args[2]
        for callback_name, args in subscriber_callbacks.callbacks
        if callback_name == "receiveInteraction"
    ]
    assert received_tags == [b"queued-two", b"queued-three"]
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is False

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-019",
    "HLA2025-FI-SVC-020",
    "HLA2025-FI-SVC-021",
    "HLA2025-FI-SVC-022",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-024",
    "HLA2025-FI-SVC-025",
    "HLA2025-FI-SVC-026",
    "HLA2025-FI-SVC-027",
    "HLA2025-FI-SVC-028",
    "HLA2025-FI-SVC-029",
    "HLA2025-FI-SVC-030",
    "HLA2025-FI-SVC-031",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-033",
    "HLA2025-FI-SVC-034",
)
def test_2025_shim_runs_federation_save_restore_lifecycle(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction, RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
    from hla.rti1516_2025.exceptions import ObjectInstanceNotKnown, RestoreNotRequested, SaveInProgress, SaveNotInitiated
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "SaveRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Save Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused save/restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>SavedTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-save-restore-{uuid.uuid4().hex[:8]}"
    leader_callbacks = Recording2025FederateAmbassador()
    wing_callbacks = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")

    leader.connect(leader_callbacks, CallbackModel.HLA_EVOKED)
    wing.connect(wing_callbacks, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    leader_handle = leader.joinFederationExecution("Leader", "TestFederate", federation_name)
    wing_handle = wing.joinFederationExecution("Wing", "TestFederate", federation_name)
    object_class = leader.getObjectClassHandle("HLAobjectRoot.SavedTarget")
    wing_object_class = wing.getObjectClassHandle("HLAobjectRoot.SavedTarget")
    attribute = leader.getAttributeHandle(object_class, "Position")
    wing_attribute = wing.getAttributeHandle(wing_object_class, "Position")
    leader.publishObjectClassAttributes(object_class, {attribute})
    wing.subscribeObjectClassAttributes(wing_object_class, {wing_attribute})
    object_instance = leader.registerObjectInstance(object_class, "Saved-Target-1")
    leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(5))
    assert leader.queryLogicalTime() == leader.getTimeFactory().makeTime(5)

    with pytest.raises(SaveNotInitiated):
        leader.federateSaveComplete()
    leader.requestFederationSave("SAVE-1")
    assert leader_callbacks.last_callback("initiateFederateSave") == ("SAVE-1",)
    assert wing_callbacks.last_callback("initiateFederateSave") == ("SAVE-1",)
    with pytest.raises(SaveInProgress):
        wing.requestFederationSave("SAVE-2")
    leader.federateSaveBegun()
    leader.queryFederationSaveStatus()
    save_status = {pair.handle: pair.status for pair in leader_callbacks.last_callback("federationSaveStatusResponse")[0]}
    assert save_status[leader_handle] is SaveStatus.FEDERATE_SAVING
    assert save_status[wing_handle] is SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE
    wing.federateSaveBegun()
    leader.federateSaveComplete()
    assert leader_callbacks.last_callback("federationSaved") is None
    wing.federateSaveComplete()
    assert leader_callbacks.last_callback("federationSaved") == ()
    assert wing_callbacks.last_callback("federationSaved") == ()
    leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(9))
    leader.deleteObjectInstance(object_instance, b"deleted-after-save")
    with pytest.raises(ObjectInstanceNotKnown):
        wing.requestAttributeValueUpdate(object_instance, {wing_attribute}, b"deleted")
    leader.queryFederationSaveStatus()
    save_status = {pair.handle: pair.status for pair in leader_callbacks.last_callback("federationSaveStatusResponse")[0]}
    assert save_status == {
        leader_handle: SaveStatus.NO_SAVE_IN_PROGRESS,
        wing_handle: SaveStatus.NO_SAVE_IN_PROGRESS,
    }

    leader.requestFederationRestore("MISSING-SAVE")
    assert leader_callbacks.last_callback("requestFederationRestoreFailed") == ("MISSING-SAVE",)
    leader.requestFederationRestore("SAVE-1")
    assert leader_callbacks.last_callback("requestFederationRestoreSucceeded") == ("SAVE-1",)
    assert leader_callbacks.last_callback("federationRestoreBegun") == ()
    assert wing_callbacks.last_callback("initiateFederateRestore") == ("SAVE-1", "Wing", wing_handle)
    leader.queryFederationRestoreStatus()
    restore_status = {pair.preRestoreHandle: pair.status for pair in leader_callbacks.last_callback("federationRestoreStatusResponse")[0]}
    assert restore_status[leader_handle] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    assert restore_status[wing_handle] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    leader.federateRestoreComplete()
    assert leader_callbacks.last_callback("federationRestored") is None
    wing.federateRestoreComplete()
    assert leader_callbacks.last_callback("federationRestored") == ()
    assert wing_callbacks.last_callback("federationRestored") == ()
    assert leader.queryLogicalTime() == leader.getTimeFactory().makeTime(5)
    wing.requestAttributeValueUpdate(object_instance, {wing_attribute}, b"after-restore")
    assert leader_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"after-restore")
    with pytest.raises(RestoreNotRequested):
        leader.federateRestoreComplete()

    leader.requestFederationSave("SAVE-FAIL")
    leader.federateSaveBegun()
    wing.federateSaveBegun()
    leader.federateSaveComplete()
    wing.federateSaveNotComplete()
    assert leader_callbacks.last_callback("federationNotSaved") == (SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,)

    leader.requestFederationSave("SAVE-ABORT")
    leader.abortFederationSave()
    assert wing_callbacks.last_callback("federationNotSaved") == (SaveFailureReason.SAVE_ABORTED,)

    leader.requestFederationRestore("SAVE-1")
    leader.abortFederationRestore()
    assert wing_callbacks.last_callback("federationNotRestored") == (RestoreFailureReason.RESTORE_ABORTED,)

    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    leader.disconnect()
    wing.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
)
def test_2025_shim_runs_example_fom_save_restore_gauntlet() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-save-restore-gauntlet-{uuid.uuid4().hex[:8]}"
    save_name = f"SAVE-GAUNTLET-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    mirror_federate = Recording2025FederateAmbassador()
    sender_federate = Recording2025FederateAmbassador()
    observer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    mirror = create_rti_ambassador(backend="shim")
    sender = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")

    def advance_ledger(ledger: dict[str, object], *, phase: str) -> None:
        next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
        ledger["random_state"] = next_state
        ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
        ledger["phase"] = phase

    try:
        for rti, federate in (
            (owner, owner_federate),
            (mirror, mirror_federate),
            (sender, sender_federate),
            (observer, observer_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        owner_handle = owner.joinFederationExecution("Owner", "SaveRestoreGauntlet", federation_name)
        mirror_handle = mirror.joinFederationExecution("Mirror", "SaveRestoreGauntlet", federation_name)
        sender_handle = sender.joinFederationExecution("Owner-Sender", "SaveRestoreGauntlet", federation_name)
        observer_handle = observer.joinFederationExecution("Mirror-Observer", "SaveRestoreGauntlet", federation_name)

        role_ledgers = {
            "owner": {"role": "owner", "random_state": 101, "sequence_counter": 0, "phase": "bootstrap"},
            "mirror": {"role": "mirror", "random_state": 202, "sequence_counter": 0, "phase": "bootstrap"},
            "sender": {"role": "sender", "random_state": 303, "sequence_counter": 0, "phase": "bootstrap"},
            "observer": {"role": "observer", "random_state": 404, "sequence_counter": 0, "phase": "bootstrap"},
        }

        target_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        mirror_target_class = mirror.getObjectClassHandle("HLAobjectRoot.Target")
        owner_position = owner.getAttributeHandle(target_class, "Position")
        owner_velocity = owner.getAttributeHandle(target_class, "Velocity")
        owner_rcs = owner.getAttributeHandle(target_class, "RCS")
        mirror_position = mirror.getAttributeHandle(mirror_target_class, "Position")
        mirror_velocity = mirror.getAttributeHandle(mirror_target_class, "Velocity")
        mirror_rcs = mirror.getAttributeHandle(mirror_target_class, "RCS")
        interaction_class = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        observer_interaction_class = observer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        interaction_parameter = sender.getParameterHandle(interaction_class, "TrackId")
        observer_parameter = observer.getParameterHandle(observer_interaction_class, "TrackId")

        owner.publishObjectClassAttributes(target_class, {owner_position, owner_velocity, owner_rcs})
        mirror.subscribeObjectClassAttributes(mirror_target_class, {mirror_position, mirror_velocity, mirror_rcs})
        sender.publishInteractionClass(interaction_class)
        observer.subscribeInteractionClass(observer_interaction_class)

        owner.enableTimeRegulation(HLAinteger64Interval(1))
        sender.enableTimeRegulation(HLAinteger64Interval(1))
        mirror.enableTimeConstrained()
        observer.enableTimeConstrained()
        sender.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)

        object_instance = owner.registerObjectInstance(target_class, "Target-Checkpoint-1")
        owner.changeAttributeOrderType(object_instance, {owner_position, owner_velocity, owner_rcs}, OrderType.TIMESTAMP)
        mirror_object_instance = mirror.getObjectInstanceHandle("Target-Checkpoint-1")

        saved_position = struct.pack(">ddd", 10_000.0, 1_000.0, 2_000.0)
        saved_velocity = struct.pack(">ddd", 250.0, 30.0, 0.0)
        saved_rcs = struct.pack(">d", 12.5)
        dirty_position = struct.pack(">ddd", 99_999.0, 88_888.0, 77_777.0)
        dirty_velocity = struct.pack(">ddd", 0.0, 0.0, 0.0)
        dirty_rcs = struct.pack(">d", 0.5)
        branch_position = struct.pack(">ddd", 10_250.0, 1_030.0, 2_000.0)

        owner.updateAttributeValues(
            object_instance,
            {owner_position: saved_position, owner_velocity: saved_velocity, owner_rcs: saved_rcs},
            b"baseline-attributes",
            HLAinteger64Time(4),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"baseline-track"},
            b"baseline-track",
            HLAinteger64Time(5),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(5))

        baseline_reflect = mirror_federate.last_callback("reflectAttributeValues")
        baseline_interaction = observer_federate.last_callback("receiveInteraction")
        assert baseline_reflect is not None
        assert baseline_interaction is not None
        assert baseline_reflect[0] == mirror_object_instance
        assert baseline_reflect[1][mirror_position] == saved_position
        assert baseline_reflect[1][mirror_velocity] == saved_velocity
        assert baseline_reflect[1][mirror_rcs] == saved_rcs
        assert baseline_interaction[0] == observer_interaction_class
        assert baseline_interaction[1] == {observer_parameter: b"baseline-track"}

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="saved")
        saved_ledgers = {role: dict(ledger) for role, ledger in role_ledgers.items()}
        saved_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in saved_ledgers.items()}

        owner.requestFederationSave(save_name)
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("initiateFederateSave") == (save_name,)
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveBegun()
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationSaved") == ()

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="dirty")
        dirty_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}
        assert dirty_fingerprints != saved_fingerprints

        owner.updateAttributeValues(
            object_instance,
            {owner_position: dirty_position, owner_velocity: dirty_velocity, owner_rcs: dirty_rcs},
            b"dirty-attributes",
            HLAinteger64Time(7),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"dirty-track"},
            b"dirty-track",
            HLAinteger64Time(8),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))
        dirty_reflect = _callbacks_named_2025(mirror_federate, "reflectAttributeValues")[-1]
        dirty_interaction = _callbacks_named_2025(observer_federate, "receiveInteraction")[-1]
        assert dirty_reflect[1][mirror_position] == dirty_position
        assert dirty_interaction[1] == {observer_parameter: b"dirty-track"}

        owner.deleteObjectInstance(object_instance, b"dirty-delete")
        dirty_remove = mirror_federate.last_callback("removeObjectInstance")
        assert dirty_remove is not None
        assert dirty_remove[0] == mirror_object_instance
        assert dirty_remove[1] == b"dirty-delete"

        owner.requestFederationRestore(save_name)
        assert owner_federate.last_callback("requestFederationRestoreSucceeded") == (save_name,)
        assert owner_federate.last_callback("initiateFederateRestore") == (save_name, "Owner", owner_handle)
        assert mirror_federate.last_callback("initiateFederateRestore") == (save_name, "Mirror", mirror_handle)
        assert sender_federate.last_callback("initiateFederateRestore") == (save_name, "Owner-Sender", sender_handle)
        assert observer_federate.last_callback("initiateFederateRestore") == (save_name, "Mirror-Observer", observer_handle)

        restored_ledgers = {role: dict(ledger) for role, ledger in saved_ledgers.items()}
        for rti in (owner, mirror, sender, observer):
            rti.federateRestoreComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationRestored") == ()

        restored_times = {
            "owner": owner.queryLogicalTime(),
            "mirror": mirror.queryLogicalTime(),
            "sender": sender.queryLogicalTime(),
            "observer": observer.queryLogicalTime(),
        }
        assert all(time == HLAinteger64Time(5) for time in restored_times.values())
        restored_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in restored_ledgers.items()}
        assert restored_fingerprints == saved_fingerprints
        assert owner.getObjectInstanceName(object_instance) == "Target-Checkpoint-1"

        mirror_federate.callbacks.clear()
        observer_federate.callbacks.clear()
        owner.updateAttributeValues(
            object_instance,
            {owner_position: branch_position, owner_velocity: saved_velocity, owner_rcs: saved_rcs},
            b"branch-attributes",
            HLAinteger64Time(7),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"branch-track"},
            b"branch-track",
            HLAinteger64Time(7),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))

        branch_reflect = mirror_federate.last_callback("reflectAttributeValues")
        branch_interaction = observer_federate.last_callback("receiveInteraction")
        assert branch_reflect is not None
        assert branch_interaction is not None
        assert branch_reflect[0] == mirror_object_instance
        assert branch_reflect[1][mirror_position] == branch_position
        assert branch_interaction[1] == {observer_parameter: b"branch-track"}
        branch_tags = {args[2] for name, args in mirror_federate.callbacks if name == "reflectAttributeValues"}
        branch_tags.update(args[2] for name, args in observer_federate.callbacks if name == "receiveInteraction")
        assert b"dirty-attributes" not in branch_tags
        assert b"dirty-track" not in branch_tags
        remove_tags = {args[1] for name, args in mirror_federate.callbacks if name == "removeObjectInstance"}
        assert b"dirty-delete" not in remove_tags
    finally:
        for rti in (observer, sender, mirror, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (observer, sender, mirror, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
)
def test_2025_shim_routes_directed_interactions_to_object_class_subscribers(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "DirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused directed interaction fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(
        federationName=federation_name,
        fomModule=str(fom),
    )
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Target-1")

    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-1"}, b"not-published")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-1"}, b"directed-tag")

    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received == (
        interaction_class,
        object_instance,
        {parameter: b"T-1"},
        b"directed-tag",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-2"}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    publisher.unpublishObjectClassDirectedInteractions(object_class, {interaction_class})
    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-3"}, b"after-unpublish")

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FR-010",
    "HLA2025-FI-SVC-112",
)
def test_2025_shim_queues_timestamped_directed_interactions_until_time_advance(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import MessageCanNoLongerBeRetracted
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Time

    fom = tmp_path / "TimedDirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Timed Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-20</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Timestamped directed interaction fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Timestamp</order>
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
        <order>Timestamp</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-tso-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)
    subscriber.enableTimeConstrained()

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Target-TSO")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})

    late = publisher.sendDirectedInteraction(
        interaction_class,
        object_instance,
        {parameter: b"late"},
        b"late",
        HLAinteger64Time(20),
    )
    retracted = publisher.sendDirectedInteraction(
        interaction_class,
        object_instance,
        {parameter: b"retracted"},
        b"retracted",
        HLAinteger64Time(15),
    )
    assert late.retractionHandleIsValid is True
    assert retracted.retractionHandleIsValid is True
    publisher.retract(retracted.handle)

    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None
    subscriber.timeAdvanceRequest(HLAinteger64Time(12))
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.timeAdvanceRequest(HLAinteger64Time(25))
    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        object_instance,
        {parameter: b"late"},
        b"late",
        reliable,
        publisher_handle,
    )
    assert received[6:] == (HLAinteger64Time(20), OrderType.TIMESTAMP, OrderType.TIMESTAMP, late.handle)
    publisher.retract(late.handle)
    request_retraction = subscriber_callbacks.last_callback("requestRetraction")
    assert request_retraction == (late.handle,)
    with pytest.raises(MessageCanNoLongerBeRetracted):
        publisher.retract(late.handle)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-129",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
)
def test_2025_shim_filters_directed_interactions_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "DirectedInteractionRegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed Interaction Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Directed interaction DDM overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-ddm-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstanceWithRegions(
        object_class,
        [({attribute}, {publisher_region})],
        "Directed-Region-Target-1",
    )
    subscriber.subscribeInteractionClassWithRegions(interaction_class, {subscriber_region})

    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"outside"}, b"outside-region")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"inside"}, b"inside-region")
    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received == (
        interaction_class,
        object_instance,
        {parameter: b"inside"},
        b"inside-region",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeInteractionClassWithRegions(interaction_class, {subscriber_region})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"after"}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
)
def test_2025_shim_directed_interaction_set_unsubscribe_and_unpublish_are_selective(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "SelectiveDirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Selective Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Directed interaction selective set fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
      <interactionClass>
        <name>AlertReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>AlertId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-set-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    track_report = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    alert_report = publisher.getInteractionClassHandle("HLAinteractionRoot.AlertReport")
    track_parameter = publisher.getParameterHandle(track_report, "TrackId")
    alert_parameter = publisher.getParameterHandle(alert_report, "AlertId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Selective-Target-1")

    publisher.publishObjectClassDirectedInteractions(object_class, {track_report, alert_report})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {track_report, alert_report})

    publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-1"}, b"track-before")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        track_report,
        object_instance,
        {track_parameter: b"T-1"},
        b"track-before",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassDirectedInteractions(object_class, {track_report})
    publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-2"}, b"track-after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    publisher.sendDirectedInteraction(alert_report, object_instance, {alert_parameter: b"A-1"}, b"alert-still-subscribed")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        alert_report,
        object_instance,
        {alert_parameter: b"A-1"},
        b"alert-still-subscribed",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    publisher.unpublishObjectClassDirectedInteractions(object_class, {track_report})
    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-3"}, b"track-after-unpublish")

    publisher.sendDirectedInteraction(alert_report, object_instance, {alert_parameter: b"A-2"}, b"alert-still-published")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        alert_report,
        object_instance,
        {alert_parameter: b"A-2"},
        b"alert-still-published",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-FI-SVC-051", "HLA2025-FI-SVC-052", "HLA2025-FI-SVC-053", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_supports_single_object_instance_name_reservation_callback_and_release() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateNotExecutionMember,
        NotConnected,
        ObjectInstanceNameNotReserved,
        RestoreInProgress,
        SaveInProgress,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    unjoined = create_rti_ambassador(backend="shim")
    with pytest.raises(NotConnected):
        unjoined.releaseObjectInstanceName("PreJoin-A")

    unjoined.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        unjoined.releaseObjectInstanceName("PreJoin-A")
    unjoined.disconnect()

    federation_name = f"shim-single-name-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    rival_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    rival = create_rti_ambassador(backend="shim")
    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    rival.connect(rival_federate, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule="TargetRadarFOMmodule.xml")
    owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    rival.joinFederationExecution(
        federateName="Rival",
        federateType="TestFederate",
        federationName=federation_name,
    )

    reserved_name = "Reserved-Solo"
    owner.reserveObjectInstanceName(reserved_name)
    assert owner_federate.last_callback("objectInstanceNameReservationSucceeded") == (reserved_name,)

    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationFailed") == (reserved_name,)

    owner.requestFederationSave("SINGLE-NAME-SAVE")
    with pytest.raises(SaveInProgress):
        owner.releaseObjectInstanceName(reserved_name)
    owner.abortFederationSave()

    owner.requestFederationSave("SINGLE-NAME-RESTORE")
    owner.federateSaveBegun()
    rival.federateSaveBegun()
    owner.federateSaveComplete()
    rival.federateSaveComplete()
    owner.requestFederationRestore("SINGLE-NAME-RESTORE")
    with pytest.raises(RestoreInProgress):
        owner.releaseObjectInstanceName(reserved_name)
    owner.federateRestoreComplete()
    rival.federateRestoreComplete()

    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationFailed") == (reserved_name,)

    owner.releaseObjectInstanceName(reserved_name)
    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationSucceeded") == (reserved_name,)

    with pytest.raises(ObjectInstanceNameNotReserved):
        owner.releaseObjectInstanceName(reserved_name)

    rival.releaseObjectInstanceName(reserved_name)

    rival.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    rival.disconnect()
    owner.disconnect()


@pytest.mark.requirements("HLA2025-FI-SVC-054", "HLA2025-FI-SVC-055", "HLA2025-FI-SVC-056", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_supports_multiple_object_instance_name_reservation_and_release() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateNotExecutionMember,
        NotConnected,
        ObjectInstanceNameNotReserved,
        RTIinternalError,
        RestoreInProgress,
        SaveInProgress,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    unjoined = create_rti_ambassador(backend="shim")
    with pytest.raises(NotConnected):
        unjoined.reserveMultipleObjectInstanceNames({"PreJoin-A"})
    with pytest.raises(NotConnected):
        unjoined.releaseMultipleObjectInstanceNames({"PreJoin-A"})

    unjoined.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        unjoined.reserveMultipleObjectInstanceNames({"PreJoin-A"})
    with pytest.raises(FederateNotExecutionMember):
        unjoined.releaseMultipleObjectInstanceNames({"PreJoin-A"})
    unjoined.disconnect()

    federation_name = f"shim-multi-name-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    rival_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    rival = create_rti_ambassador(backend="shim")
    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    rival.connect(rival_federate, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule="TargetRadarFOMmodule.xml")
    owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    rival.joinFederationExecution(
        federateName="Rival",
        federateType="TestFederate",
        federationName=federation_name,
    )

    names = {"Reserve-A", "Reserve-B"}
    owner.reserveMultipleObjectInstanceNames(names)
    assert owner_federate.last_callback("multipleObjectInstanceNameReservationSucceeded") == (names,)

    rival.reserveMultipleObjectInstanceNames(names)
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationFailed") == (names,)

    with pytest.raises(RTIinternalError):
        owner.reserveMultipleObjectInstanceNames(set())
    with pytest.raises(RTIinternalError):
        owner.releaseMultipleObjectInstanceNames(set())

    owner.requestFederationSave("MULTI-NAME-SAVE")
    with pytest.raises(SaveInProgress):
        owner.reserveMultipleObjectInstanceNames({"Save-Blocked"})
    with pytest.raises(SaveInProgress):
        owner.releaseMultipleObjectInstanceNames(names)
    owner.abortFederationSave()

    owner.reserveMultipleObjectInstanceNames({"Restore-Blocked"})
    owner.requestFederationSave("MULTI-NAME-RESTORE")
    owner.federateSaveBegun()
    rival.federateSaveBegun()
    owner.federateSaveComplete()
    rival.federateSaveComplete()
    owner.requestFederationRestore("MULTI-NAME-RESTORE")
    with pytest.raises(RestoreInProgress):
        owner.reserveMultipleObjectInstanceNames({"Restore-Locked"})
    with pytest.raises(RestoreInProgress):
        owner.releaseMultipleObjectInstanceNames({"Restore-Blocked"})
    owner.federateRestoreComplete()
    rival.federateRestoreComplete()
    rival.reserveMultipleObjectInstanceNames({"Restore-Blocked"})
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationFailed") == ({"Restore-Blocked"},)
    owner.releaseMultipleObjectInstanceNames({"Restore-Blocked"})

    owner.releaseMultipleObjectInstanceNames(names)
    rival.reserveMultipleObjectInstanceNames(names)
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationSucceeded") == (names,)

    with pytest.raises(ObjectInstanceNameNotReserved):
        owner.releaseMultipleObjectInstanceNames(names)

    rival.releaseMultipleObjectInstanceNames(names)

    rival.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    rival.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-NEW-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-162",
    "HLA2025-FI-SVC-163",
    "HLA2025-FI-SVC-164",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-076",
    "HLA2025-FI-SVC-124",
    "HLA2025-FI-SVC-157",
)
def test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeNotDefined,
        InvalidAttributeHandle,
        InvalidDimensionHandle,
        InvalidObjectClassHandle,
        InvalidOrderType,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import AttributeHandle, DimensionHandle, ObjectClassHandle

    fom = tmp_path / "PolicyDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Policy DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused DDM/default attribute policy fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>PolicyTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>1024</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ddm-policy-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    rti.joinFederationExecution(
        federateName="PolicyFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    object_class = rti.getObjectClassHandle("HLAobjectRoot.PolicyTarget")
    assert rti.getObjectClassName(object_class) == "HLAobjectRoot.PolicyTarget"
    attribute = rti.getAttributeHandle(object_class, "Position")
    assert rti.getAttributeName(object_class, attribute) == "Position"
    dimension = rti.getDimensionHandle("RoutingSpace")
    assert rti.getDimensionName(dimension) == "RoutingSpace"
    assert rti.getDimensionUpperBound(dimension) == 1024
    available_dimensions = rti.getAvailableDimensionsForObjectClass(object_class)
    assert dimension in available_dimensions
    assert {rti.getDimensionName(handle) for handle in available_dimensions} >= {"RoutingSpace"}
    assert rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAbestEffort")) == "HLAbestEffort"
    region = rti.createRegion({dimension})
    rti.setRangeBounds(region, dimension, RangeBounds(0, 10))
    assert dimension in rti.getDimensionHandleSet(region)
    assert rti.getRangeBounds(region, dimension) == RangeBounds(0, 10)

    rti.changeDefaultAttributeTransportationType(
        object_class,
        {attribute},
        rti.getTransportationTypeHandle("HLAbestEffort"),
    )
    rti.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
    assert rti.defaultAttributePolicySnapshot() == {
        "transportation": {"HLAobjectRoot.PolicyTarget.Position": "HLAbestEffort"},
        "order": {"HLAobjectRoot.PolicyTarget.Position": "TIMESTAMP"},
    }

    with pytest.raises(InvalidObjectClassHandle):
        rti.getAvailableDimensionsForObjectClass(ObjectClassHandle(9999))
    with pytest.raises(InvalidDimensionHandle):
        rti.getDimensionUpperBound(DimensionHandle(9999))
    with pytest.raises(AttributeNotDefined):
        rti.getAttributeHandle(object_class, "Missing")
    with pytest.raises(InvalidAttributeHandle):
        rti.changeDefaultAttributeOrderType(object_class, {AttributeHandle(9999)}, OrderType.RECEIVE)
    with pytest.raises(InvalidOrderType):
        rti.changeDefaultAttributeOrderType(object_class, {attribute}, "bad-order")

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-130",
    "HLA2025-FI-SVC-132",
)
def test_2025_shim_filters_object_reflections_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "RegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused region overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ddm-region-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)
    subscriber.setAttributeScopeAdvisorySwitch(True)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    publisher.publishObjectClassAttributes(object_class, {attribute})

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "Region-Target-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])

    assert subscriber_callbacks.last_callback("discoverObjectInstance") is None
    assert subscriber_callbacks.last_callback("attributesInScope") is None
    assert subscriber_callbacks.last_callback("attributesOutOfScope") is None
    publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-region")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "Region-Target-1",
        publisher_handle,
    )

    publisher.updateAttributeValues(object_instance, {attribute: b"inside"}, b"inside-region")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"inside"},
        b"inside-region",
        publisher.getTransportationTypeHandle("HLAreliable"),
        publisher_handle,
        {publisher_region},
    )

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    subscriber.commitRegionModifications({subscriber_region})
    assert subscriber_callbacks.last_callback("attributesOutOfScope") == (object_instance, {attribute})
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(0, 10))
    subscriber.commitRegionModifications({subscriber_region})
    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})

    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-136",
)
def test_2025_shim_filters_interactions_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "InteractionRegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Interaction Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused interaction DDM overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-interaction-ddm-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishInteractionClass(interaction_class)
    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})

    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"outside"}, {publisher_region}, b"outside-region")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"inside"}, {publisher_region}, b"inside-region")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received == (
        interaction_class,
        {parameter: b"inside"},
        b"inside-region",
        reliable,
        publisher_handle,
        {publisher_region},
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"after"}, {publisher_region}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


def test_2025_shim_preserves_direct_callback_context_for_timed_region_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "TimedRegionContext2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Timed Region Context 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Timed regional callback-context fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
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
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-timed-region-context-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(0, 10))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "TimedRegionTarget-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.subscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})

    publisher.enableTimeRegulation(HLAinteger64Interval(1))
    subscriber.enableTimeConstrained()
    publisher.changeAttributeOrderType(object_instance, {attribute}, OrderType.TIMESTAMP)
    publisher.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)

    attribute_result = publisher.updateAttributeValues(
        object_instance,
        {attribute: b"inside"},
        b"inside-tag",
        HLAinteger64Time(10),
    )
    interaction_result = publisher.sendInteractionWithRegions(
        interaction_class,
        {parameter: b"track"},
        {publisher_region},
        b"track-tag",
        HLAinteger64Time(12),
    )
    remove_result = publisher.deleteObjectInstance(
        object_instance,
        b"gone",
        HLAinteger64Time(14),
    )
    assert attribute_result is not None and attribute_result.retractionHandleIsValid is True
    assert interaction_result is None
    assert remove_result is None

    publisher.timeAdvanceRequest(HLAinteger64Time(20))
    subscriber.timeAdvanceRequest(HLAinteger64Time(20))

    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "TimedRegionTarget-1",
        publisher_handle,
    )
    assert subscriber_callbacks.last_callback("reflectAttributeValues") == (
        object_instance,
        {attribute: b"inside"},
        b"inside-tag",
        reliable,
        publisher_handle,
        {publisher_region},
        HLAinteger64Time(10),
        OrderType.TIMESTAMP,
        OrderType.TIMESTAMP,
        attribute_result.handle,
    )
    assert subscriber_callbacks.last_callback("receiveInteraction") == (
        interaction_class,
        {parameter: b"track"},
        b"track-tag",
        reliable,
        publisher_handle,
        {publisher_region},
        HLAinteger64Time(12),
        OrderType.TIMESTAMP,
        OrderType.TIMESTAMP,
        None,
    )
    assert subscriber_callbacks.last_callback("removeObjectInstance") == (
        object_instance,
        b"gone",
        publisher_handle,
        HLAinteger64Time(14),
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-130",
    "HLA2025-FI-SVC-132",
    "HLA2025-FI-SVC-133",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-136",
)
def test_2025_shim_passive_ddm_region_subscription_aliases_match_active_region_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "PassiveRegionAlias2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Passive Region Alias 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Passive region subscription alias fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <dimension>RoutingSpace</dimension>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <dimension>RoutingSpace</dimension>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-passive-region-alias-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("PassiveRegionPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("PassiveRegionSubscriber", "TestFederate", federation_name)
    subscriber.setAttributeScopeAdvisorySwitch(True)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "PassiveRegionTarget-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesPassivelyWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.subscribeInteractionClassPassivelyWithRegions(subscriber_interaction_class, {subscriber_region})

    assert subscriber_callbacks.last_callback("discoverObjectInstance") is None
    publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-attr")
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"outside"}, {publisher_region}, b"outside-interaction")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeObjectClassAttributesPassivelyWithRegions(object_class, [({attribute}, {subscriber_region})])

    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "PassiveRegionTarget-1",
        publisher_handle,
    )

    publisher.updateAttributeValues(object_instance, {attribute: b"inside-attr"}, b"inside-attr")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"inside-attr"},
        b"inside-attr",
        reliable,
        publisher_handle,
        {publisher_region},
    )

    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"inside-interaction"}, {publisher_region}, b"inside-interaction")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received == (
        interaction_class,
        {parameter: b"inside-interaction"},
        b"inside-interaction",
        reliable,
        publisher_handle,
        {publisher_region},
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.unsubscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})
    publisher.updateAttributeValues(object_instance, {attribute: b"after"}, b"after-attr")
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"after"}, {publisher_region}, b"after-interaction")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-065",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-068",
    "HLA2025-FI-SVC-069",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-FI-SVC-072",
    "HLA2025-FI-SVC-073",
    "HLA2025-FI-SVC-074",
    "HLA2025-FI-SVC-075",
    "HLA2025-FI-SVC-077",
    "HLA2025-FI-SVC-078",
    "HLA2025-FI-SVC-079",
    "HLA2025-FI-SVC-080",
    "HLA2025-FI-SVC-081",
    "HLA2025-FI-SVC-082",
)
def test_2025_shim_object_management_and_support_callbacks(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import DeletePrivilegeNotHeld, ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "ObjectSupport2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Object Support 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused object/support service fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>SupportTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
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
        <name>SupportReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-object-support-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner_handle = owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.SupportTarget")
    subscriber_object_class = subscriber.getObjectClassHandle("HLAobjectRoot.SupportTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    subscriber_attribute = subscriber.getAttributeHandle(subscriber_object_class, "Position")
    interaction_class = owner.getInteractionClassHandle("HLAinteractionRoot.SupportReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.SupportReport")
    best_effort = owner.getTransportationTypeHandle("HLAbestEffort")

    owner.publishObjectClassAttributes(object_class, {attribute})
    owner.publishInteractionClass(interaction_class)
    subscriber.subscribeObjectClassAttributes(subscriber_object_class, {subscriber_attribute})
    object_instance = owner.registerObjectInstance(object_class, "Support-Target-1")
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        subscriber_object_class,
        "Support-Target-1",
        owner_handle,
    )

    subscriber.requestAttributeValueUpdate(object_instance, {subscriber_attribute}, b"instance-request")
    assert owner_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"instance-request")

    subscriber.requestAttributeValueUpdate(subscriber_object_class, {subscriber_attribute}, b"class-request")
    assert owner_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"class-request")

    owner.requestAttributeTransportationTypeChange(object_instance, {attribute}, best_effort)
    assert owner_callbacks.last_callback("confirmAttributeTransportationTypeChange") == (object_instance, {attribute}, best_effort)
    subscriber.queryAttributeTransportationType(object_instance, subscriber_attribute)
    assert subscriber_callbacks.last_callback("reportAttributeTransportationType") == (object_instance, subscriber_attribute, best_effort)

    owner.requestInteractionTransportationTypeChange(interaction_class, best_effort)
    assert owner_callbacks.last_callback("confirmInteractionTransportationTypeChange") == (interaction_class, best_effort)
    subscriber.queryInteractionTransportationType(owner_handle, subscriber_interaction_class)
    assert subscriber_callbacks.last_callback("reportInteractionTransportationType") == (
        owner_handle,
        subscriber_interaction_class,
        best_effort,
    )

    subscriber.localDeleteObjectInstance(object_instance)
    with pytest.raises(DeletePrivilegeNotHeld):
        subscriber.deleteObjectInstance(object_instance, b"not-owner")
    owner.deleteObjectInstance(object_instance, b"delete-tag")
    assert subscriber_callbacks.last_callback("removeObjectInstance") == (
        object_instance,
        b"delete-tag",
        owner_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )
    with pytest.raises(ObjectInstanceNotKnown):
        subscriber.requestAttributeValueUpdate(object_instance, {subscriber_attribute}, b"after-delete")

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    owner.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-100",
)
def test_2025_shim_applies_resign_time_ownership_policies(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import NoAcquisitionPending, ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "ResignOwnership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Resign Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused resign-time ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-resign-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    acquirer.joinFederationExecution("Acquirer", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    subscriber_attribute = subscriber.getAttributeHandle(object_class, "Position")
    subscriber.subscribeObjectClassAttributes(object_class, {subscriber_attribute})

    cancelled = owner.registerObjectInstance(object_class, "Cancel-Pending")
    acquirer.attributeOwnershipAcquisition(cancelled, {attribute}, b"cancel-on-resign")
    assert owner_callbacks.last_callback("requestAttributeOwnershipRelease") == (
        cancelled,
        {attribute},
        b"cancel-on-resign",
    )
    acquirer.resignFederationExecution(ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS)
    with pytest.raises(NoAcquisitionPending):
        owner.attributeOwnershipDivestitureIfWanted(cancelled, {attribute})

    acquirer = create_rti_ambassador(backend="shim")
    acquirer_callbacks = Recording2025FederateAmbassador()
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    acquirer_handle = acquirer.joinFederationExecution("Acquirer-2", "TestFederate", federation_name)

    transferred = owner.registerObjectInstance(object_class, "Transfer-On-Resign")
    acquirer.attributeOwnershipAcquisition(transferred, {attribute}, b"transfer-on-resign")
    owner.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        transferred,
        {attribute},
        b"transfer-on-resign",
    )
    acquirer.queryAttributeOwnership(transferred, {attribute})
    assert acquirer_callbacks.last_callback("informAttributeOwnership") == (
        transferred,
        {attribute},
        acquirer_handle,
    )

    deleter = create_rti_ambassador(backend="shim")
    deleter_callbacks = Recording2025FederateAmbassador()
    deleter.connect(deleter_callbacks, CallbackModel.HLA_EVOKED)
    deleter.joinFederationExecution("Deleter", "TestFederate", federation_name)
    delete_object_class = deleter.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    delete_attribute = deleter.getAttributeHandle(delete_object_class, "Position")
    deleter.publishObjectClassAttributes(delete_object_class, {delete_attribute})
    deleted = deleter.registerObjectInstance(delete_object_class, "Delete-On-Resign")
    assert subscriber_callbacks.last_callback("discoverObjectInstance")[0] == deleted
    assert deleter.isAttributeOwnedByFederate(deleted, delete_attribute) is True
    deleter.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    assert subscriber_callbacks.last_callback("removeObjectInstance")[0] == deleted
    with pytest.raises(ObjectInstanceNotKnown):
        subscriber.requestAttributeValueUpdate(deleted, {subscriber_attribute}, b"deleted")

    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.destroyFederationExecution(federationName=federation_name)
    deleter.disconnect()
    acquirer.disconnect()
    subscriber.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-084",
    "HLA2025-FI-SVC-085",
    "HLA2025-FI-SVC-086",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-088",
    "HLA2025-FI-SVC-089",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-091",
    "HLA2025-FI-SVC-092",
)
def test_2025_shim_implements_basic_ownership_divest_acquire_and_query_callbacks(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeAlreadyOwned,
        AttributeNotOwned,
        InvalidObjectInstanceHandle,
        ObjectInstanceNameInUse,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import ObjectInstanceHandle

    fom = tmp_path / "Ownership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquiring_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquiring = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquiring.connect(acquiring_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner_handle = owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    acquiring_handle = acquiring.joinFederationExecution(
        federateName="Acquirer",
        federateType="TestFederate",
        federationName=federation_name,
    )

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    object_instance = owner.registerObjectInstance(object_class, "Target-1")

    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert acquiring.isAttributeOwnedByFederate(object_instance, attribute) is False
    with pytest.raises(ObjectInstanceNameInUse):
        owner.registerObjectInstance(object_class, "Target-1")
    with pytest.raises(InvalidObjectInstanceHandle):
        owner.isAttributeOwnedByFederate(ObjectInstanceHandle(9999), attribute)
    with pytest.raises(AttributeAlreadyOwned):
        owner.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"already-owned")

    acquiring.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"blocked")
    unavailable = acquiring_callbacks.last_callback("attributeOwnershipUnavailable")
    assert unavailable == (object_instance, {attribute}, b"blocked")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True

    with pytest.raises(AttributeNotOwned):
        acquiring.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"not-owned")

    owner.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"divest")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is False

    owner.queryAttributeOwnership(object_instance, {attribute})
    assert owner_callbacks.last_callback("attributeIsNotOwned") == (object_instance, {attribute})

    acquiring.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"claim")
    acquired = acquiring_callbacks.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired == (object_instance, {attribute}, b"claim")
    assert acquiring.isAttributeOwnedByFederate(object_instance, attribute) is True

    owner.queryAttributeOwnership(object_instance, {attribute})
    assert owner_callbacks.last_callback("informAttributeOwnership") == (
        object_instance,
        {attribute},
        acquiring_handle,
    )
    acquiring.queryAttributeOwnership(object_instance, {attribute})
    assert acquiring_callbacks.last_callback("informAttributeOwnership") == (
        object_instance,
        {attribute},
        acquiring_handle,
    )
    assert owner_handle != acquiring_handle

    acquiring.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    acquiring.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-089",
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-094",
    "HLA2025-FI-SVC-095",
    "HLA2025-FI-SVC-096",
    "HLA2025-FI-SVC-097",
    "HLA2025-FI-SVC-098",
    "HLA2025-FI-SVC-099",
)
def test_2025_shim_negotiated_ownership_matches_python_parity_flow(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeAcquisitionWasNotRequested,
        AttributeAlreadyBeingDivested,
        NoAcquisitionPending,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "NegotiatedOwnership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Negotiated Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused negotiated ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-negotiated-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    acquirer.joinFederationExecution("Acquirer", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")

    offered = owner.registerObjectInstance(object_class, "Negotiated-1")
    owner.negotiatedAttributeOwnershipDivestiture(offered, {attribute}, b"offer-tag")
    assert acquirer_callbacks.last_callback("requestAttributeOwnershipAssumption") == (
        offered,
        {attribute},
        b"offer-tag",
    )
    with pytest.raises(AttributeAlreadyBeingDivested):
        owner.negotiatedAttributeOwnershipDivestiture(offered, {attribute}, b"second-offer")
    assert owner.isAttributeOwnedByFederate(offered, attribute) is True

    acquirer.attributeOwnershipAcquisition(offered, {attribute}, b"acquire-tag")
    assert owner_callbacks.last_callback("requestDivestitureConfirmation") == (
        offered,
        {attribute},
        b"acquire-tag",
    )
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        offered,
        {attribute},
        b"acquire-tag",
    )
    assert acquirer.isAttributeOwnedByFederate(offered, attribute) is True

    pending = owner.registerObjectInstance(object_class, "Pending-1")
    acquirer.attributeOwnershipAcquisition(pending, {attribute}, b"request-tag")
    assert owner_callbacks.last_callback("requestAttributeOwnershipRelease") == (
        pending,
        {attribute},
        b"request-tag",
    )
    acquirer.cancelAttributeOwnershipAcquisition(pending, {attribute})
    assert acquirer_callbacks.last_callback("confirmAttributeOwnershipAcquisitionCancellation") == (
        pending,
        {attribute},
    )
    with pytest.raises(AttributeAcquisitionWasNotRequested):
        acquirer.cancelAttributeOwnershipAcquisition(pending, {attribute})

    acquirer.attributeOwnershipAcquisition(pending, {attribute}, b"retry-tag")
    divested = owner.attributeOwnershipDivestitureIfWanted(pending, {attribute})
    assert divested == {attribute}
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        pending,
        {attribute},
        b"",
    )
    assert acquirer.isAttributeOwnedByFederate(pending, attribute) is True

    no_candidate = owner.registerObjectInstance(object_class, "NoCandidate-1")
    with pytest.raises(NoAcquisitionPending):
        owner.attributeOwnershipDivestitureIfWanted(no_candidate, {attribute})

    cancellable = owner.registerObjectInstance(object_class, "Cancelable-1")
    owner.negotiatedAttributeOwnershipDivestiture(cancellable, {attribute}, b"cancel-offer")
    owner.cancelNegotiatedAttributeOwnershipDivestiture(cancellable, {attribute})
    assert owner.isAttributeOwnedByFederate(cancellable, attribute) is True
    owner.unconditionalAttributeOwnershipDivestiture(cancellable, {attribute}, b"final-divest")
    assert owner.isAttributeOwnedByFederate(cancellable, attribute) is False

    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    acquirer.disconnect()
    owner.disconnect()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-FI-001", "HLA2025-FI-005", "HLA2025-REQ-002")
def test_2025_shim_serializes_mom_service_reports_without_overclaiming_conformance() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import AttributeHandle

    federation_name = f"shim-mom-report-{uuid.uuid4().hex[:8]}"
    source_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    rti.connect(source_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="BoundaryFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )
    observer.joinFederationExecution(
        federateName="MomObserver",
        federateType="ObserverFederate",
        federationName=federation_name,
    )

    assert rti.getServiceReportingSwitch() is False
    assert observer.getServiceReportingSwitch() is False
    rti.setServiceReportingSwitch(True)
    observer.setServiceReportingSwitch(True)
    assert rti.getServiceReportingSwitch() is True
    assert observer.getServiceReportingSwitch() is True

    report = rti.serializeMOMServiceReport(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches",
        arguments={"HLAserviceReporting": True, "tag": b"mom-tag", "attrs": {AttributeHandle(7)}},
        result={"status": "serialized"},
    )
    assert report["recordType"] == "MOMServiceReport"
    assert report["spec"] == "IEEE 1516.1-2025"
    assert report["serialNumber"] == 1
    assert report["federationName"] == federation_name
    assert report["federateName"] == "BoundaryFederate"
    assert report["federateHandle"] == 1
    assert report["service"] == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    assert report["success"] is True
    assert report["exception"] == ""
    assert report["serviceReportingEnabled"] is True
    assert report["sendServiceReportsToFile"] is False
    assert report["arguments"]["HLAserviceReporting"] is True
    assert report["arguments"]["tag"] == "6d6f6d2d746167"
    assert report["arguments"]["attrs"] == [{"type": "AttributeHandle", "value": 7}]
    assert report["returned"] == {"value": {"status": "serialized"}}
    json.dumps(report, sort_keys=True)
    assert source_callbacks.last_callback("momServiceReport") == (report,)
    assert observer_callbacks.last_callback("momServiceReport") == (report,)

    failed = rti.serializeMOMServiceReport(
        "queryLogicalTime",
        success=False,
        exception="FederateNotExecutionMember",
        returned={"value": None},
    )
    assert failed["serialNumber"] == 2
    assert failed["success"] is False
    assert failed["exception"] == "FederateNotExecutionMember"
    assert rti.serviceReportRecordsSnapshot() == (report, failed)
    assert observer_callbacks.last_callback("momServiceReport") == (failed,)

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-NEW-004", "HLA2025-FI-001", "HLA2025-REQ-002")
def test_2025_shim_declares_all_bundled_mim_manager_command_leaves_as_routed() -> None:
    from hla.backends.shim.backend import (
        MOM_2025_FEDERATE_ADJUST_LEAVES,
        MOM_2025_FEDERATE_REQUEST_LEAVES,
        MOM_2025_FEDERATE_SERVICE_LEAVES,
        MOM_2025_FEDERATION_ADJUST_LEAVES,
        MOM_2025_FEDERATION_REQUEST_LEAVES,
        MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES,
    )

    mim_path = files("hla.rti1516e.resources.foms").joinpath("HLAstandardMIM.xml")
    with mim_path.open("rb") as handle:
        root = ET.parse(handle).getroot()
    namespace = root.tag.removesuffix("objectModel")

    categories = {
        "federate_adjust": set(),
        "federate_request": set(),
        "federate_service": set(),
        "federation_adjust": set(),
        "federation_request": set(),
    }

    def child_text(element: ET.Element, name: str) -> str:
        child = element.find(f"{namespace}{name}")
        return "" if child is None or child.text is None else child.text.strip()

    def walk_interaction_class(element: ET.Element, path: tuple[str, ...]) -> None:
        name = child_text(element, "name")
        if not name:
            return
        current_path = (*path, name)
        children = element.findall(f"{namespace}interactionClass")
        if children:
            for child in children:
                walk_interaction_class(child, current_path)
            return
        qualified_name = ".".join(current_path)
        leaf = current_path[-1]
        if ".HLAreport." in qualified_name:
            return
        if ".HLAfederate.HLAadjust." in qualified_name:
            categories["federate_adjust"].add(leaf)
        elif ".HLAfederate.HLArequest." in qualified_name:
            categories["federate_request"].add(leaf)
        elif ".HLAfederate.HLAservice." in qualified_name:
            categories["federate_service"].add(leaf)
        elif ".HLAfederation.HLAadjust." in qualified_name:
            categories["federation_adjust"].add(leaf)
        elif ".HLAfederation.HLArequest." in qualified_name:
            categories["federation_request"].add(leaf)

    for interaction_class in root.findall(f".//{namespace}interactions/{namespace}interactionClass"):
        walk_interaction_class(interaction_class, ())

    assert categories["federate_adjust"] == set(MOM_2025_FEDERATE_ADJUST_LEAVES)
    assert categories["federate_request"] == set(MOM_2025_FEDERATE_REQUEST_LEAVES)
    assert categories["federate_service"] == set(MOM_2025_FEDERATE_SERVICE_LEAVES)
    assert categories["federation_adjust"] == set(MOM_2025_FEDERATION_ADJUST_LEAVES)
    assert categories["federation_request"] == set(MOM_2025_FEDERATION_REQUEST_LEAVES)
    assert set().union(*categories.values()) == set(MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES)


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-NEW-007",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-013",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
    "HLA2025-FI-SVC-017",
)
def test_2025_shim_routes_mom_synchronization_point_reports_through_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-sync-{uuid.uuid4().hex[:8]}"
    leader_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    leader.connect(leader_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    leader_handle = leader.joinFederationExecution("SyncLeader", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("SyncObserver", "ObserverFederate", federation_name)

    leader.registerFederationSynchronizationPoint(
        "ReadyToRun",
        b"sync-tag",
        {leader_handle, observer_handle},
    )
    assert leader_callbacks.last_callback("synchronizationPointRegistrationSucceeded") == ("ReadyToRun",)
    assert leader_callbacks.last_callback("announceSynchronizationPoint") == ("ReadyToRun", b"sync-tag")
    assert observer_callbacks.last_callback("announceSynchronizationPoint") == ("ReadyToRun", b"sync-tag")

    leader.synchronizationPointAchieved("ReadyToRun")
    assert leader_callbacks.last_callback("federationSynchronized") is None
    observer.synchronizationPointAchieved("ReadyToRun")
    assert leader_callbacks.last_callback("federationSynchronized") == ("ReadyToRun", set())
    assert observer_callbacks.last_callback("federationSynchronized") == ("ReadyToRun", set())

    points_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints"
    )
    points_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints"
    )
    points_param = observer.getParameterHandle(points_report, "HLAsyncPoints")
    observer.subscribeInteractionClass(points_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(points_request, {}, b"mom-sync-points-request")
    points_callback = observer_callbacks.last_callback("receiveInteraction")
    assert points_callback is not None
    assert points_callback[0] == points_report
    assert points_callback[1][points_param] == b"ReadyToRun"
    assert points_callback[2] == b"MOM"

    status_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus"
    )
    status_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus"
    )
    status_label = observer.getParameterHandle(status_report, "HLAsyncPointName")
    status_list = observer.getParameterHandle(status_report, "HLAsyncPointFederates")
    observer.subscribeInteractionClass(status_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(status_request, {}, b"mom-sync-status-request")
    status_callback = observer_callbacks.last_callback("receiveInteraction")
    assert status_callback is not None
    assert status_callback[0] == status_report
    assert status_callback[1][status_label] == b"ReadyToRun"
    assert status_callback[1][status_list] == b"ReadyToRun:1:achieved,2:achieved"
    assert status_callback[2] == b"MOM"

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    leader.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    leader.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_mim_and_fom_module_reports_through_interactions(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    def write_module(path: Path, module_name: str, class_name: str) -> Path:
        path.write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>{module_name}</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-01-01</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>{module_name} for 2025 MOM routing tests.</description>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>Neither</sharing>
      <semantics>Root</semantics>
      <objectClass>
        <name>{class_name}</name>
        <sharing>PublishSubscribe</sharing>
        <semantics>{class_name}</semantics>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <updateCondition>On change</updateCondition>
          <ownership>NoTransfer</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <semantics>Position</semantics>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>Neither</sharing>
      <transportation>HLAreliable</transportation>
      <order>Receive</order>
      <semantics>Root</semantics>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
            encoding="utf-8",
        )
        return path

    core_fom = write_module(tmp_path / "mom-core.xml", "MOM Core FOM", "Target")
    extension_fom = write_module(tmp_path / "mom-extension.xml", "MOM Extension FOM", "Sensor")
    federation_name = f"shim-mom-fom-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModules=(str(core_fom), str(extension_fom)),
    )
    leader_handle = rti.joinFederationExecution("MomDataLeader", "TestFederate", federation_name)
    observer.joinFederationExecution("MomDataObserver", "ObserverFederate", federation_name)

    fom_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData"
    )
    fom_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData"
    )
    request_indicator = observer.getParameterHandle(fom_request, "HLAFOMmoduleIndicator")
    report_indicator = observer.getParameterHandle(fom_report, "HLAFOMmoduleIndicator")
    report_data = observer.getParameterHandle(fom_report, "HLAFOMmoduleData")
    observer.subscribeInteractionClass(fom_report)
    observer.sendInteraction(fom_request, {request_indicator: b"1"}, b"mom-fom-module-request")
    fom_callback = observer_callbacks.last_callback("receiveInteraction")
    assert fom_callback is not None
    assert fom_callback[0] == fom_report
    assert fom_callback[1][report_indicator] == b"1"
    assert b"MOM Extension FOM" in fom_callback[1][report_data]
    assert b"<name>Sensor</name>" in fom_callback[1][report_data]
    assert fom_callback[2] == b"MOM"

    mim_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    )
    mim_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )
    mim_data = observer.getParameterHandle(mim_report, "HLAMIMdata")
    observer.subscribeInteractionClass(mim_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(mim_request, {}, b"mom-mim-request")
    mim_callback = observer_callbacks.last_callback("receiveInteraction")
    assert mim_callback is not None
    assert mim_callback[0] == mim_report
    assert b"Standard MOM and Initialization Module" in mim_callback[1][mim_data]
    assert b"HLArequestMIMdata" in mim_callback[1][mim_data]
    assert mim_callback[2] == b"MOM"

    federate_fom_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData"
    )
    federate_fom_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData"
    )
    federate_param = observer.getParameterHandle(federate_fom_request, "HLAfederate")
    federate_request_indicator = observer.getParameterHandle(federate_fom_request, "HLAFOMmoduleIndicator")
    federate_report_target = observer.getParameterHandle(federate_fom_report, "HLAfederate")
    federate_report_indicator = observer.getParameterHandle(federate_fom_report, "HLAFOMmoduleIndicator")
    federate_report_data = observer.getParameterHandle(federate_fom_report, "HLAFOMmoduleData")
    observer.subscribeInteractionClass(federate_fom_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(
        federate_fom_request,
        {
            federate_param: str(leader_handle.value).encode("ascii"),
            federate_request_indicator: b"0",
        },
        b"mom-federate-fom-module-request",
    )
    federate_fom_callback = observer_callbacks.last_callback("receiveInteraction")
    assert federate_fom_callback is not None
    assert federate_fom_callback[0] == federate_fom_report
    assert federate_fom_callback[1][federate_report_target] == str(leader_handle.value).encode("ascii")
    assert federate_fom_callback[1][federate_report_indicator] == b"0"
    assert b"MOM Core FOM" in federate_fom_callback[1][federate_report_data]
    assert b"<name>Target</name>" in federate_fom_callback[1][federate_report_data]
    assert federate_fom_callback[2] == b"MOM"

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-MOD-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_adjust_interactions_for_reporting_switches() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-adjust-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomTarget", "TestFederate", federation_name)

    service_adjust = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_target = controller.getParameterHandle(service_adjust, "HLAfederate")
    service_state = controller.getParameterHandle(service_adjust, "HLAreportingState")
    assert target.getServiceReportingSwitch() is False
    controller.sendInteraction(
        service_adjust,
        {
            service_target: str(target_handle.value).encode("ascii"),
            service_state: b"HLAtrue",
        },
        b"mom-enable-service-reporting",
    )
    assert target.getServiceReportingSwitch() is True
    controller.sendInteraction(
        service_adjust,
        {
            service_target: str(target_handle.value).encode("ascii"),
            service_state: b"HLAfalse",
        },
        b"mom-disable-service-reporting",
    )
    assert target.getServiceReportingSwitch() is False

    exception_adjust = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting"
    )
    exception_target = controller.getParameterHandle(exception_adjust, "HLAfederate")
    exception_state = controller.getParameterHandle(exception_adjust, "HLAreportingState")
    assert target.getExceptionReportingSwitch() is True
    controller.sendInteraction(
        exception_adjust,
        {
            exception_target: str(target_handle.value).encode("ascii"),
            exception_state: b"HLAfalse",
        },
        b"mom-disable-exception-reporting",
    )
    assert target.getExceptionReportingSwitch() is False
    controller.sendInteraction(
        exception_adjust,
        {
            exception_target: str(target_handle.value).encode("ascii"),
            exception_state: b"HLAtrue",
        },
        b"mom-enable-exception-reporting",
    )
    assert target.getExceptionReportingSwitch() is True

    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-MOD-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_set_switches_adjust_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-switches-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("SwitchController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("SwitchTarget", "TestFederate", federation_name)

    federate_switches = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    )
    federate_target = controller.getParameterHandle(federate_switches, "HLAfederate")
    convey_regions = controller.getParameterHandle(federate_switches, "HLAconveyRegionDesignatorSets")
    assert target.getConveyRegionDesignatorSetsSwitch() is True
    controller.sendInteraction(
        federate_switches,
        {
            federate_target: str(target_handle.value).encode("ascii"),
            convey_regions: b"HLAfalse",
        },
        b"mom-disable-convey-region-designator-sets",
    )
    assert target.getConveyRegionDesignatorSetsSwitch() is False
    controller.sendInteraction(
        federate_switches,
        {
            federate_target: str(target_handle.value).encode("ascii"),
            convey_regions: b"HLAtrue",
        },
        b"mom-enable-convey-region-designator-sets",
    )
    assert target.getConveyRegionDesignatorSetsSwitch() is True

    federation_switches = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAadjust.HLAsetSwitches"
    )
    auto_provide = controller.getParameterHandle(federation_switches, "HLAautoProvide")
    assert controller.getAutoProvideSwitch() is True
    assert target.getAutoProvideSwitch() is True
    controller.sendInteraction(
        federation_switches,
        {auto_provide: b"HLAfalse"},
        b"mom-disable-auto-provide",
    )
    assert controller.getAutoProvideSwitch() is False
    assert target.getAutoProvideSwitch() is False
    controller.sendInteraction(
        federation_switches,
        {auto_provide: b"HLAtrue"},
        b"mom-enable-auto-provide",
    )
    assert controller.getAutoProvideSwitch() is True
    assert target.getAutoProvideSwitch() is True

    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-FR-005", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_timing_and_attribute_state_adjust_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-state-adjust-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    nonpublisher = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    nonpublisher.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("StateAdjustController", "TestFederate", federation_name)
    owner.joinFederationExecution("StateAdjustOwner", "TestFederate", federation_name)
    acquirer_handle = acquirer.joinFederationExecution("StateAdjustAcquirer", "TestFederate", federation_name)
    nonpublisher_handle = nonpublisher.joinFederationExecution("StateAdjustNonpublisher", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = owner.getAttributeHandle(object_class, "Position")
    owner.publishObjectClassAttributes(object_class, {attribute})
    acquirer.publishObjectClassAttributes(object_class, {attribute})
    object_instance = owner.registerObjectInstance(object_class, "MOM-State-Adjust-Target")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is False

    timing = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming"
    )
    controller.sendInteraction(
        timing,
        {
            controller.getParameterHandle(timing, "HLAfederate"): str(acquirer_handle.value).encode("ascii"),
            controller.getParameterHandle(timing, "HLAreportPeriod"): b"2.5",
        },
        b"mom-set-timing",
    )
    assert acquirer.momReportPeriodSecondsSnapshot() == 2.5

    modify_state = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAmodifyAttributeState"
    )

    def send_modify_state(target_handle, state: bytes) -> None:  # noqa: ANN001
        controller.sendInteraction(
            modify_state,
            {
                controller.getParameterHandle(modify_state, "HLAfederate"): str(target_handle.value).encode("ascii"),
                controller.getParameterHandle(modify_state, "HLAobjectInstance"): str(object_instance.value).encode(
                    "ascii"
                ),
                controller.getParameterHandle(modify_state, "HLAattribute"): str(attribute.value).encode("ascii"),
                controller.getParameterHandle(modify_state, "HLAattributeState"): state,
            },
            b"mom-modify-attribute-state",
        )

    owner_callbacks.callbacks.clear()
    acquirer_callbacks.callbacks.clear()
    send_modify_state(acquirer_handle, b"Owned")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is False
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert owner_callbacks.last_callback("requestDivestitureConfirmation") is None
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") is None

    send_modify_state(acquirer_handle, b"0")
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is False

    with pytest.raises(ObjectClassNotPublished):
        send_modify_state(nonpublisher_handle, b"1")
    report = controller_callbacks.last_callback("receiveInteraction")
    assert report is not None
    report_name = controller.getInteractionClassName(report[0])
    assert report_name == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    assert b"ObjectClassNotPublished" in report[1][controller.getParameterHandle(report[0], "HLAexception")]
    assert nonpublisher.isAttributeOwnedByFederate(object_instance, attribute) is False

    nonpublisher.resignFederationExecution(ResignAction.NO_ACTION)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    nonpublisher.disconnect()
    acquirer.disconnect()
    owner.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-004", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_federate_publication_subscription_and_object_information() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-fed-reports-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomFederateReportController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomFederateReportTarget", "TestFederate", federation_name)
    observer.joinFederationExecution("MomFederateReportObserver", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    target.subscribeObjectClassAttributes(object_class, {attribute})
    target.subscribeInteractionClass(interaction_class)
    object_instance = target.registerObjectInstance(object_class, "MOM-Federate-Report-Target")

    report_names = (
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",
    )
    for report_name in report_names:
        observer.subscribeInteractionClass(observer.getInteractionClassHandle(report_name))

    def send_request(name: str, extra: dict[str, bytes] | None = None) -> None:
        request = controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{name}")
        values = {controller.getParameterHandle(request, "HLAfederate"): str(target_handle.value).encode("ascii")}
        if extra:
            values.update({controller.getParameterHandle(request, key): value for key, value in extra.items()})
        controller.sendInteraction(request, values, f"mom-{name}".encode("ascii"))

    def last_report(report_name: str):  # noqa: ANN202
        for callback_name, args in reversed(observer_callbacks.callbacks):
            if callback_name == "receiveInteraction" and observer.getInteractionClassName(args[0]) == report_name:
                return args
        return None

    send_request("HLArequestPublications")
    object_publication = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
    )
    assert object_publication is not None
    object_pub_params = object_publication[1]
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAfederate")] == str(
        target_handle.value
    ).encode("ascii")
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAnumberOfClasses")] == b"1"
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAobjectClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAattributeList")] == str(
        attribute.value
    ).encode("ascii")

    interaction_publication = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication"
    )
    assert interaction_publication is not None
    assert interaction_publication[1][observer.getParameterHandle(interaction_publication[0], "HLAinteractionClassList")] == str(
        interaction_class.value
    ).encode("ascii")

    send_request("HLArequestSubscriptions")
    object_subscription = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
    )
    assert object_subscription is not None
    object_sub_params = object_subscription[1]
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAnumberOfClasses")] == b"1"
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAobjectClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAactive")] == b"HLAtrue"
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAattributeList")] == str(
        attribute.value
    ).encode("ascii")

    interaction_subscription = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription"
    )
    assert interaction_subscription is not None
    assert interaction_subscription[1][observer.getParameterHandle(interaction_subscription[0], "HLAinteractionClassList")] == str(
        interaction_class.value
    ).encode("ascii")

    send_request("HLArequestObjectInstanceInformation", {"HLAobjectInstance": str(object_instance.value).encode("ascii")})
    object_information = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation"
    )
    assert object_information is not None
    object_info_params = object_information[1]
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAobjectInstance")] == str(
        object_instance.value
    ).encode("ascii")
    owned_attributes = {
        int(value)
        for value in object_info_params[
            observer.getParameterHandle(object_information[0], "HLAownedInstanceAttributeList")
        ].split(b",")
        if value
    }
    assert attribute.value in owned_attributes
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAregisteredClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAknownClass")] == str(
        object_class.value
    ).encode("ascii")

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-004", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_federate_activity_counts() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-activity-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomActivityController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomActivityTarget", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("MomActivityObserver", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    observer.subscribeObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    observer.subscribeInteractionClass(interaction_class)

    object_instance = target.registerObjectInstance(object_class, "MOM-Activity-Target")
    target.updateAttributeValues(object_instance, {attribute: b"1,2,3"}, b"mom-activity-update")
    target.sendInteraction(interaction_class, {}, b"mom-activity-interaction")
    assert observer_callbacks.last_callback("reflectAttributeValues") is not None
    assert observer_callbacks.last_callback("receiveInteraction") is not None

    report_names = (
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
    )
    for report_name in report_names:
        observer.subscribeInteractionClass(observer.getInteractionClassHandle(report_name))

    def send_request(target_federate, name: str) -> None:  # noqa: ANN001
        request = controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{name}")
        controller.sendInteraction(
            request,
            {controller.getParameterHandle(request, "HLAfederate"): str(target_federate.value).encode("ascii")},
            f"mom-{name}".encode("ascii"),
        )

    def last_report(report_name: str):  # noqa: ANN202
        for callback_name, args in reversed(observer_callbacks.callbacks):
            if callback_name == "receiveInteraction" and observer.getInteractionClassName(args[0]) == report_name:
                return args
        return None

    def count_payload(report, parameter_name: str) -> dict[int, int]:  # noqa: ANN001
        payload = report[1][observer.getParameterHandle(report[0], parameter_name)]
        result: dict[int, int] = {}
        for item in payload.decode("ascii").split(","):
            if not item:
                continue
            handle, count = item.split(":", 1)
            result[int(handle)] = int(count)
        return result

    send_request(target_handle, "HLArequestObjectInstancesThatCanBeDeleted")
    deletable = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted"
    )
    assert deletable is not None
    assert count_payload(deletable, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestObjectInstancesUpdated")
    updated = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated")
    assert updated is not None
    assert count_payload(updated, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(observer_handle, "HLArequestObjectInstancesReflected")
    reflected = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected")
    assert reflected is not None
    assert count_payload(reflected, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestUpdatesSent")
    updates_sent = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent")
    assert updates_sent is not None
    assert updates_sent[1][observer.getParameterHandle(updates_sent[0], "HLAtransportation")] == b"HLAreliable"
    assert count_payload(updates_sent, "HLAupdateCounts") == {object_class.value: 1}

    send_request(observer_handle, "HLArequestReflectionsReceived")
    reflections_received = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived"
    )
    assert reflections_received is not None
    assert count_payload(reflections_received, "HLAreflectCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestInteractionsSent")
    interactions_sent = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent")
    assert interactions_sent is not None
    assert count_payload(interactions_sent, "HLAinteractionCounts") == {interaction_class.value: 1}

    send_request(observer_handle, "HLArequestInteractionsReceived")
    interactions_received = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived"
    )
    assert interactions_received is not None
    assert count_payload(interactions_received, "HLAinteractionCounts") == {interaction_class.value: 1}

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_declaration_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished, ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-service-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer_callbacks = Recording2025FederateAmbassador()
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("ServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("ServiceTarget", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("ServiceObserver", "TestFederate", federation_name)

    object_class = controller.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = controller.getAttributeHandle(object_class, "Position")
    interaction_class = controller.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    publish_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLApublishObjectClassAttributes"
    )
    subscribe_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeObjectClassAttributes"
    )
    unpublish_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunpublishObjectClassAttributes"
    )
    publish_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLApublishInteractionClass"
    )
    subscribe_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeInteractionClass"
    )
    unpublish_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunpublishInteractionClass"
    )

    def parameter(interaction, name: str):  # noqa: ANN001
        return controller.getParameterHandle(interaction, name)

    target_payload = str(target_handle.value).encode("ascii")
    observer_payload = str(observer_handle.value).encode("ascii")
    object_payload = str(object_class.value).encode("ascii")
    attribute_payload = str(attribute.value).encode("ascii")
    interaction_payload = str(interaction_class.value).encode("ascii")

    controller.sendInteraction(
        publish_object,
        {
            parameter(publish_object, "HLAfederate"): target_payload,
            parameter(publish_object, "HLAobjectClass"): object_payload,
            parameter(publish_object, "HLAattributeList"): attribute_payload,
        },
        b"mom-publish-object",
    )
    controller.sendInteraction(
        subscribe_object,
        {
            parameter(subscribe_object, "HLAfederate"): observer_payload,
            parameter(subscribe_object, "HLAobjectClass"): object_payload,
            parameter(subscribe_object, "HLAattributeList"): attribute_payload,
            parameter(subscribe_object, "HLAactive"): b"HLAtrue",
        },
        b"mom-subscribe-object",
    )
    object_instance = target.registerObjectInstance(object_class, "MOM-Service-Target-1")
    target.updateAttributeValues(object_instance, {attribute: b"1,2,3"}, b"mom-service-update")
    assert observer_callbacks.last_callback("discoverObjectInstance") is not None
    reflect = observer_callbacks.last_callback("reflectAttributeValues")
    assert reflect is not None
    assert reflect[0] == object_instance
    assert reflect[1][attribute] == b"1,2,3"

    controller.sendInteraction(
        unpublish_object,
        {
            parameter(unpublish_object, "HLAfederate"): target_payload,
            parameter(unpublish_object, "HLAobjectClass"): object_payload,
            parameter(unpublish_object, "HLAattributeList"): attribute_payload,
        },
        b"mom-unpublish-object",
    )
    with pytest.raises(ObjectClassNotPublished):
        target.updateAttributeValues(object_instance, {attribute: b"4,5,6"}, b"mom-service-update-after-unpublish")

    controller.sendInteraction(
        publish_interaction,
        {
            parameter(publish_interaction, "HLAfederate"): target_payload,
            parameter(publish_interaction, "HLAinteractionClass"): interaction_payload,
        },
        b"mom-publish-interaction",
    )
    controller.sendInteraction(
        subscribe_interaction,
        {
            parameter(subscribe_interaction, "HLAfederate"): observer_payload,
            parameter(subscribe_interaction, "HLAinteractionClass"): interaction_payload,
            parameter(subscribe_interaction, "HLAactive"): b"HLAtrue",
        },
        b"mom-subscribe-interaction",
    )
    target.sendInteraction(interaction_class, {}, b"mom-service-interaction")
    received = observer_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[0] == interaction_class
    assert received[2] == b"mom-service-interaction"

    controller.sendInteraction(
        unpublish_interaction,
        {
            parameter(unpublish_interaction, "HLAfederate"): target_payload,
            parameter(unpublish_interaction, "HLAinteractionClass"): interaction_payload,
        },
        b"mom-unpublish-interaction",
    )
    with pytest.raises(InteractionClassNotPublished):
        target.sendInteraction(interaction_class, {}, b"mom-service-interaction-after-unpublish")

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_federation_management_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-fm-service-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("FmServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("FmServiceTarget", "TestFederate", federation_name)

    sync_label = "MOM-SYNC"
    controller.registerFederationSynchronizationPoint(sync_label, b"mom-sync")
    sync_achieved = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsynchronizationPointAchieved"
    )
    controller.sendInteraction(
        sync_achieved,
        {
            controller.getParameterHandle(sync_achieved, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(sync_achieved, "HLAlabel"): sync_label.encode("utf-8"),
        },
        b"mom-sync-achieved",
    )
    controller.synchronizationPointAchieved(sync_label)
    assert controller_callbacks.last_callback("federationSynchronized") == (sync_label, set())
    assert target_callbacks.last_callback("federationSynchronized") == (sync_label, set())

    controller.requestFederationSave("MOM-SAVE")
    save_begun = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateSaveBegun"
    )
    save_complete = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateSaveComplete"
    )
    controller.sendInteraction(
        save_begun,
        {controller.getParameterHandle(save_begun, "HLAfederate"): str(target_handle.value).encode("ascii")},
        b"mom-save-begun",
    )
    controller.sendInteraction(
        save_complete,
        {
            controller.getParameterHandle(save_complete, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(save_complete, "HLAsuccessIndicator"): b"HLAtrue",
        },
        b"mom-save-complete",
    )
    controller.federateSaveComplete()
    assert controller_callbacks.last_callback("federationSaved") == ()
    assert target_callbacks.last_callback("federationSaved") == ()

    controller.requestFederationRestore("MOM-SAVE")
    restore_complete = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateRestoreComplete"
    )
    controller.sendInteraction(
        restore_complete,
        {
            controller.getParameterHandle(restore_complete, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(restore_complete, "HLAsuccessIndicator"): b"HLAtrue",
        },
        b"mom-restore-complete",
    )
    controller.federateRestoreComplete()
    assert controller_callbacks.last_callback("federationRestored") == ()
    assert target_callbacks.last_callback("federationRestored") == ()

    resign = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAresignFederationExecution"
    )
    controller.sendInteraction(
        resign,
        {
            controller.getParameterHandle(resign, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(resign, "HLAresignAction"): str(int(ResignAction.NO_ACTION)).encode("ascii"),
        },
        b"mom-resign",
    )
    assert target_callbacks.last_callback("federateResigned") is not None

    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-009",
    "HLA2025-NEW-007",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-102",
    "HLA2025-FI-SVC-103",
    "HLA2025-FI-SVC-104",
    "HLA2025-FI-SVC-105",
    "HLA2025-FI-SVC-106",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-109",
    "HLA2025-FI-SVC-110",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-113",
    "HLA2025-FI-SVC-114",
    "HLA2025-FI-SVC-115",
    "HLA2025-FI-SVC-119",
)
def test_2025_shim_routes_mom_time_management_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-time-service-{uuid.uuid4().hex[:8]}"
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("TimeServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("TimeServiceTarget", "TestFederate", federation_name)

    def mom_service(name: str):  # noqa: ANN202
        return controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.{name}")

    def send_service(name: str, parameters: dict[str, bytes]) -> None:
        interaction = mom_service(name)
        payload = {controller.getParameterHandle(interaction, "HLAfederate"): str(target_handle.value).encode("ascii")}
        payload.update({controller.getParameterHandle(interaction, key): value for key, value in parameters.items()})
        controller.sendInteraction(interaction, payload, f"mom-{name}".encode("ascii"))

    send_service("HLAenableTimeRegulation", {"HLAlookahead": b"2"})
    assert target.queryLookahead() == target.getTimeFactory().makeInterval(2)
    assert target_callbacks.last_callback("timeRegulationEnabled") == (target.getTimeFactory().makeInitial(),)

    send_service("HLAenableTimeConstrained", {})
    assert target_callbacks.last_callback("timeConstrainedEnabled") == (target.getTimeFactory().makeInitial(),)

    send_service("HLAtimeAdvanceRequest", {"HLAtimeStamp": b"10"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(10)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(10),)

    send_service("HLAmodifyLookahead", {"HLAlookahead": b"3"})
    assert target.queryLookahead() == target.getTimeFactory().makeInterval(3)

    send_service("HLAflushQueueRequest", {"HLAtimeStamp": b"12"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(12)
    assert target_callbacks.last_callback("flushQueueGrant") == (
        target.getTimeFactory().makeTime(12),
        target.getTimeFactory().makeTime(12),
    )

    send_service("HLAtimeAdvanceRequestAvailable", {"HLAtimeStamp": b"14"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(14)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(14),)

    send_service("HLAnextMessageRequest", {"HLAtimeStamp": b"16"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(16)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(16),)

    send_service("HLAnextMessageRequestAvailable", {"HLAtimeStamp": b"18"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(18)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(18),)

    send_service("HLAenableAsynchronousDelivery", {})
    send_service("HLAdisableAsynchronousDelivery", {})
    assert any(call[0] == "enableAsynchronousDelivery" for call in target.calls)
    assert any(call[0] == "disableAsynchronousDelivery" for call in target.calls)

    send_service("HLAdisableTimeConstrained", {})
    assert any(call[0] == "disableTimeConstrained" for call in target.calls)

    send_service("HLAdisableTimeRegulation", {})
    with pytest.raises(TimeRegulationIsNotEnabled):
        target.queryLookahead()

    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-FR-005", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_object_and_ownership_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-object-service-{uuid.uuid4().hex[:8]}"
    target_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("ObjectServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("ObjectServiceTarget", "TestFederate", federation_name)
    observer.joinFederationExecution("ObjectServiceObserver", "TestFederate", federation_name)
    acquirer.joinFederationExecution("ObjectServiceAcquirer", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    observer.subscribeObjectClassAttributes(object_class, {attribute})
    object_instance = target.registerObjectInstance(object_class, "MOM-Object-Service-Target")

    def mom_service(name: str):  # noqa: ANN202
        return controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.{name}")

    def send_service(name: str, parameters: dict[str, bytes]) -> None:
        interaction = mom_service(name)
        payload = {controller.getParameterHandle(interaction, "HLAfederate"): str(target_handle.value).encode("ascii")}
        payload.update({controller.getParameterHandle(interaction, key): value for key, value in parameters.items()})
        controller.sendInteraction(interaction, payload, f"mom-{name}".encode("ascii"))

    send_service(
        "HLArequestAttributeTransportationTypeChange",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
            "HLAtransportation": b"HLAbestEffort",
        },
    )
    assert target_callbacks.last_callback("confirmAttributeTransportationTypeChange") == (
        object_instance,
        {attribute},
        target.getTransportationTypeHandle("HLAbestEffort"),
    )

    send_service(
        "HLArequestInteractionTransportationTypeChange",
        {
            "HLAinteractionClass": str(interaction_class.value).encode("ascii"),
            "HLAtransportation": b"HLAbestEffort",
        },
    )
    assert target_callbacks.last_callback("confirmInteractionTransportationTypeChange") == (
        interaction_class,
        target.getTransportationTypeHandle("HLAbestEffort"),
    )

    send_service(
        "HLAchangeAttributeOrderType",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
            "HLAsendOrder": b"TimeStamp",
        },
    )
    observer_callbacks.callbacks.clear()
    target.updateAttributeValues(object_instance, {attribute: b"ordered"}, b"mom-order-update")
    ordered_reflection = observer_callbacks.last_callback("reflectAttributeValues")
    assert ordered_reflection is not None
    assert ordered_reflection[7:9] == (OrderType.TIMESTAMP, OrderType.TIMESTAMP)

    observer.subscribeInteractionClass(interaction_class)
    send_service(
        "HLAchangeInteractionOrderType",
        {
            "HLAinteractionClass": str(interaction_class.value).encode("ascii"),
            "HLAsendOrder": b"1",
        },
    )
    observer_callbacks.callbacks.clear()
    target.sendInteraction(interaction_class, {}, b"mom-order-interaction")
    ordered_interaction = observer_callbacks.last_callback("receiveInteraction")
    assert ordered_interaction is not None
    assert ordered_interaction[7:9] == (OrderType.TIMESTAMP, OrderType.TIMESTAMP)

    assert target.isAttributeOwnedByFederate(object_instance, attribute) is True
    send_service(
        "HLAunconditionalAttributeOwnershipDivestiture",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
        },
    )
    assert target.isAttributeOwnedByFederate(object_instance, attribute) is False
    acquirer.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"after-mom-divest")
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        object_instance,
        {attribute},
        b"after-mom-divest",
    )

    object_instance_to_delete = target.registerObjectInstance(object_class, "MOM-Object-Service-Delete")
    send_service(
        "HLAdeleteObjectInstance",
        {
            "HLAobjectInstance": str(object_instance_to_delete.value).encode("ascii"),
            "HLAtag": b"mom-delete-object",
        },
    )
    assert observer_callbacks.last_callback("removeObjectInstance") is not None
    assert observer_callbacks.last_callback("removeObjectInstance")[0] == object_instance_to_delete
    with pytest.raises(ObjectInstanceNotKnown):
        target.deleteObjectInstance(object_instance_to_delete, b"already-deleted")

    object_instance_to_forget = target.registerObjectInstance(object_class, "MOM-Object-Service-Local")
    send_service(
        "HLAlocalDeleteObjectInstance",
        {"HLAobjectInstance": str(object_instance_to_forget.value).encode("ascii")},
    )
    assert target.isAttributeOwnedByFederate(object_instance_to_forget, attribute) is True

    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    acquirer.disconnect()
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_service_failures_as_mom_exception_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import RTIinternalError
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-exception-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomExceptionController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomExceptionTarget", "TestFederate", federation_name)

    service = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance"
    )
    with pytest.raises(RTIinternalError, match="HLAobjectInstance"):
        controller.sendInteraction(
            service,
            {controller.getParameterHandle(service, "HLAfederate"): str(target_handle.value).encode("ascii")},
            b"mom-missing-object",
        )

    report = controller_callbacks.last_callback("receiveInteraction")
    assert report is not None
    report_class, parameter_values = report[0], report[1]
    report_name = controller.getInteractionClassName(report_class)
    assert report_name == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    service_param = controller.getParameterHandle(report_class, "HLAservice")
    exception_param = controller.getParameterHandle(report_class, "HLAexception")
    parameter_error_param = controller.getParameterHandle(report_class, "HLAparameterError")
    assert parameter_values[service_param] == b"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance"
    assert b"Missing MOM parameter HLAobjectInstance" in parameter_values[exception_param]
    assert parameter_values[parameter_error_param] == b"HLAfalse"
    assert target_callbacks.last_callback("receiveInteraction")[0] == report_class

    target.resignFederationExecution(ResignAction.NO_ACTION)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-SVC-005", "HLA2025-FI-SVC-006", "HLA2025-FI-SVC-007")
def test_2025_shim_rejects_duplicate_federation_and_federate_names() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateAlreadyExecutionMember,
        FederateNameAlreadyInUse,
        FederationExecutionAlreadyExists,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-join-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    late = create_rti_ambassador(backend="shim")

    for rti in (leader, wing, late):
        rti.connect(object(), CallbackModel.HLA_EVOKED)

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    with pytest.raises(FederationExecutionAlreadyExists):
        leader.createFederationExecution(federationName=federation_name)

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(FederateNameAlreadyInUse):
        late.joinFederationExecution(
            federateName="Leader",
            federateType="TestFederate",
            federationName=federation_name,
        )
    with pytest.raises(FederateAlreadyExecutionMember):
        leader.joinFederationExecution(
            federateName="Leader-Again",
            federateType="TestFederate",
            federationName=federation_name,
        )

    leader.resignFederationExecution(ResignAction.NO_ACTION)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    late.disconnect()
    wing.disconnect()
    leader.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-003",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-011",
    "HLA2025-FI-SVC-012",
)
def test_2025_shim_reports_federate_resigned_callback_with_reason_context() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-resign-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="ResigningFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    rti.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)

    resigned = federate.last_callback("federateResigned")
    assert resigned is not None
    reason = resigned[0]
    assert "federateName=ResigningFederate" in reason
    assert f"federationName={federation_name}" in reason
    assert "resignAction=UNCONDITIONALLY_DIVEST_ATTRIBUTES" in reason

    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-165",
    "HLA2025-FI-SVC-166",
    "HLA2025-FI-SVC-167",
    "HLA2025-FI-SVC-168",
    "HLA2025-FI-SVC-169",
)
def test_2025_shim_normalizes_typed_handles_and_rejects_wrong_handle_family() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction, ServiceGroup
    from hla.rti1516_2025.exceptions import (
        InvalidFederateHandle,
        InvalidInteractionClassHandle,
        InvalidObjectClassHandle,
        InvalidObjectInstanceHandle,
        InvalidServiceGroup,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import (
        FederateHandle,
        InteractionClassHandle,
        ObjectClassHandle,
        ObjectInstanceHandle,
    )

    federation_name = f"shim-normalize-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")

    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    federate_handle = rti.joinFederationExecution(
        federateName="Normalizer",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert isinstance(federate_handle, FederateHandle)
    assert rti.normalizeFederateHandle(federate_handle) == federate_handle.value
    assert rti.normalizeServiceGroup(ServiceGroup.SUPPORT_SERVICES) == int(ServiceGroup.SUPPORT_SERVICES)
    assert rti.normalizeObjectClassHandle(ObjectClassHandle(11)) == 11
    assert rti.normalizeInteractionClassHandle(InteractionClassHandle(12)) == 12
    assert rti.normalizeObjectInstanceHandle(ObjectInstanceHandle(13)) == 13

    with pytest.raises(InvalidFederateHandle):
        rti.normalizeFederateHandle(ObjectClassHandle(1))
    with pytest.raises(InvalidObjectClassHandle):
        rti.normalizeObjectClassHandle(FederateHandle(1))
    with pytest.raises(InvalidInteractionClassHandle):
        rti.normalizeInteractionClassHandle(ObjectInstanceHandle(1))
    with pytest.raises(InvalidObjectInstanceHandle):
        rti.normalizeObjectInstanceHandle(InteractionClassHandle(1))
    with pytest.raises(InvalidServiceGroup):
        rti.normalizeServiceGroup("not-a-service-group")

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-008",
    "HLA2025-RET-001",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-170",
    "HLA2025-FI-SVC-171",
    "HLA2025-FI-SVC-172",
    "HLA2025-FI-SVC-173",
    "HLA2025-FI-SVC-174",
    "HLA2025-FI-SVC-175",
    "HLA2025-FI-SVC-176",
    "HLA2025-FI-SVC-177",
    "HLA2025-FI-SVC-178",
    "HLA2025-FI-SVC-179",
    "HLA2025-FI-SVC-180",
    "HLA2025-FI-SVC-181",
    "HLA2025-FI-SVC-182",
    "HLA2025-FI-SVC-183",
    "HLA2025-FI-SVC-184",
    "HLA2025-FI-SVC-185",
    "HLA2025-FI-SVC-186",
    "HLA2025-FI-SVC-187",
    "HLA2025-FI-SVC-188",
    "HLA2025-FI-SVC-189",
    "HLA2025-FI-SVC-190",
    "HLA2025-FI-SVC-191",
    "HLA2025-FI-SVC-192",
)
def test_2025_shim_supports_explicit_switch_inquiry_and_control_model() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import RTIinternalError
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-switch-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="SwitchFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert rti.getObjectClassRelevanceAdvisorySwitch() is False
    assert rti.getAttributeRelevanceAdvisorySwitch() is False
    assert rti.getAttributeScopeAdvisorySwitch() is False
    assert rti.getInteractionRelevanceAdvisorySwitch() is False
    assert rti.getConveyRegionDesignatorSetsSwitch() is True
    assert rti.getServiceReportingSwitch() is False
    assert rti.getExceptionReportingSwitch() is True
    assert rti.getSendServiceReportsToFileSwitch() is False
    assert rti.getAutoProvideSwitch() is True
    assert rti.getDelaySubscriptionEvaluationSwitch() is False
    assert rti.getAdvisoriesUseKnownClassSwitch() is True
    assert rti.getAllowRelaxedDDMSwitch() is False
    assert rti.getNonRegulatedGrantSwitch() is False
    assert rti.getAutomaticResignDirective() is ResignAction.NO_ACTION

    rti.setObjectClassRelevanceAdvisorySwitch(True)
    rti.setAttributeRelevanceAdvisorySwitch(True)
    rti.setAttributeScopeAdvisorySwitch(True)
    rti.setInteractionRelevanceAdvisorySwitch(True)
    rti.setConveyRegionDesignatorSetsSwitch(False)
    rti.setAutomaticResignDirective(ResignAction.DELETE_OBJECTS)
    rti.setServiceReportingSwitch(True)
    rti.setExceptionReportingSwitch(False)
    rti.setSendServiceReportsToFileSwitch(True)

    assert rti.getObjectClassRelevanceAdvisorySwitch() is True
    assert rti.getAttributeRelevanceAdvisorySwitch() is True
    assert rti.getAttributeScopeAdvisorySwitch() is True
    assert rti.getInteractionRelevanceAdvisorySwitch() is True
    assert rti.getConveyRegionDesignatorSetsSwitch() is False
    assert rti.getAutomaticResignDirective() is ResignAction.DELETE_OBJECTS
    assert rti.getServiceReportingSwitch() is True
    assert rti.getExceptionReportingSwitch() is False
    assert rti.getSendServiceReportsToFileSwitch() is True

    with pytest.raises(RTIinternalError, match="requires a bool"):
        rti.setServiceReportingSwitch("yes")
    with pytest.raises(RTIinternalError, match="requires a ResignAction"):
        rti.setAutomaticResignDirective("delete")
    with pytest.raises(RTIinternalError, match="does not implement"):
        rti.enableObjectClassRelevanceAdvisorySwitch()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-002",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-004",
    "HLA2025-FI-SVC-008",
    "HLA2025-FI-SVC-009",
    "HLA2025-FI-SVC-010",
)
def test_2025_shim_reports_federation_executions_and_members() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-report-{uuid.uuid4().hex[:8]}"
    leader_fed = Recording2025FederateAmbassador()
    wing_fed = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")

    leader.connect(leader_fed, CallbackModel.HLA_EVOKED)
    wing.connect(wing_fed, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
        logicalTimeImplementationName="HLAinteger64Time",
    )

    leader.listFederationExecutions()
    execution_report = leader_fed.last_callback("reportFederationExecutions")
    assert execution_report is not None
    executions = execution_report[0]
    assert any(row.federationExecutionName == federation_name and row.logicalTimeImplementationName == "HLAinteger64Time" for row in executions)

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="Observer",
        federationName=federation_name,
    )

    leader.listFederationExecutionMembers(federation_name)
    members_report = leader_fed.last_callback("reportFederationExecutionMembers")
    assert members_report is not None
    assert members_report[0] == federation_name
    assert {(row.federateName, row.federateType) for row in members_report[1]} == {
        ("Leader", "TestFederate"),
        ("Wing", "Observer"),
    }

    leader.listFederationExecutionMembers(f"{federation_name}-missing")
    missing_report = leader_fed.last_callback("reportFederationExecutionDoesNotExist")
    assert missing_report == (f"{federation_name}-missing",)

    leader.resignFederationExecution(ResignAction.NO_ACTION)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    wing.disconnect()
    leader.disconnect()


@pytest.mark.requirements("HLA2025-MOD-001", "HLA2025-MOD-009", "HLA2025-FI-005", "HLA2025-FI-006")
def test_2025_shim_validates_callback_model_and_credentials_at_connect() -> None:
    from hla.rti1516_2025.auth import HLAplainTextPassword
    from hla.rti1516_2025.datatypes import Credentials
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import InvalidCredentials, UnsupportedCallbackModel
    from hla.rti1516_2025.factory import create_rti_ambassador

    rti = create_rti_ambassador(backend="shim")
    with pytest.raises(UnsupportedCallbackModel):
        rti.connect(object(), 99)

    with pytest.raises(InvalidCredentials, match="cannot be empty"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword(""))

    with pytest.raises(InvalidCredentials, match="rejected"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword("bad"))

    rti.connect(object(), CallbackModel.HLA_IMMEDIATE, credentials=Credentials("Proto2025Bearer", b"token"))
    assert rti.connected is True
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-FI-009")
def test_2025_shim_requires_valid_fom_modules_and_default_logical_time() -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import CouldNotCreateLogicalTimeFactory, InvalidFOM
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-fom-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(InvalidFOM, match="At least one FOM module"):
        rti.createFederationExecution(federationName=f"{federation_name}-missing-fom")

    with pytest.raises(CouldNotCreateLogicalTimeFactory, match="NoSuchTimeFactory"):
        rti.createFederationExecution(
            federationName=f"{federation_name}-bad-time",
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="NoSuchTimeFactory",
        )

    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    reporter = Recording2025FederateAmbassador()
    observer = create_rti_ambassador(backend="shim")
    observer.connect(reporter, CallbackModel.HLA_EVOKED)
    observer.listFederationExecutions()

    execution_report = reporter.last_callback("reportFederationExecutions")
    assert execution_report is not None
    assert any(row.federationExecutionName == federation_name and row.logicalTimeImplementationName == "HLAinteger64Time" for row in execution_report[0])

    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-MOD-003", "HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_rejects_invalid_join_fom_modules_and_destroy_while_joined(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import DesignatorIsHLAstandardMIM, ErrorReadingFOM, FederatesCurrentlyJoined
    from hla.rti1516_2025.factory import create_rti_ambassador

    broken_fom = tmp_path / "BrokenProto2025.xml"
    broken_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Broken Proto2025</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>BrokenEntity</name>
        <attribute><name>BadField</name><dataType>DoesNotExist</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-join-fom-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    leader.connect(object(), CallbackModel.HLA_EVOKED)
    wing.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(DesignatorIsHLAstandardMIM):
        leader.createFederationExecutionWithMIM(
            federationName=f"{federation_name}-bad-mim",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule="HLAstandardMIM",
        )

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(ErrorReadingFOM):
        wing.joinFederationExecution(
            federateName="Wing",
            federateType="TestFederate",
            federationName=federation_name,
            additionalFomModules=[broken_fom],
        )

    with pytest.raises(FederatesCurrentlyJoined):
        leader.destroyFederationExecution(federationName=federation_name)

    leader.disconnect()
    wing.disconnect()


@pytest.mark.requirements("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_distinguishes_fom_mim_open_read_invalid_and_merge_errors(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import (
        CouldNotOpenFOM,
        CouldNotOpenMIM,
        ErrorReadingFOM,
        ErrorReadingMIM,
        InconsistentFOM,
        InvalidFOM,
        InvalidMIM,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    def write_module(path: Path, name: str, representation: str) -> Path:
        path.write_text(
            f"""<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
            encoding="utf-8",
        )
        return path

    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(CouldNotOpenFOM):
        rti.createFederationExecution(
            federationName=f"missing-fom-{uuid.uuid4().hex[:8]}",
            fomModule=tmp_path / "missing-fom.xml",
        )
    with pytest.raises(CouldNotOpenMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"missing-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=tmp_path / "missing-mim.xml",
        )

    bad_fom = tmp_path / "bad-fom.xml"
    bad_fom.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFOM):
        rti.createFederationExecution(
            federationName=f"bad-fom-{uuid.uuid4().hex[:8]}",
            fomModule=bad_fom,
        )

    bad_mim = tmp_path / "bad-mim.xml"
    bad_mim.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"bad-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=bad_mim,
        )

    invalid_name_fom = tmp_path / "invalid-name-fom.xml"
    invalid_name_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Invalid Name FOM</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass><name>hlaReservedUserClass</name></objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InvalidFOM, match="reserved"):
        rti.createFederationExecution(
            federationName=f"invalid-fom-{uuid.uuid4().hex[:8]}",
            fomModule=invalid_name_fom,
        )

    with pytest.raises(InvalidMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"invalid-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=None,
        )

    conflict_a = write_module(tmp_path / "conflict-a.xml", "Conflict A", "HLAinteger32BE")
    conflict_b = write_module(tmp_path / "conflict-b.xml", "Conflict B", "HLAinteger64BE")
    with pytest.raises(InconsistentFOM, match="Conflicting simple datatype definition"):
        rti.createFederationExecution(
            federationName=f"conflicting-fom-{uuid.uuid4().hex[:8]}",
            fomModules=[conflict_a, conflict_b],
        )

    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-010",
    "HLA2025-FI-005",
    "HLA2025-FI-009",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-122",
)
def test_2025_shim_queues_timestamped_messages_and_supports_retraction(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import MessageCanNoLongerBeRetracted
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Time

    fom = tmp_path / "QueuedTso2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Queued TSO 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused queued TSO fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>TimedTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>TimeStamp</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TimedReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>TimeStamp</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-tso-queue-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)
    subscriber.enableTimeConstrained()

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.TimedTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TimedReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)
    subscriber.subscribeObjectClassAttributes(object_class, {attribute})
    subscriber.subscribeInteractionClass(interaction_class)
    object_instance = publisher.registerObjectInstance(object_class, "Timed-Target-1")

    late = publisher.sendInteraction(interaction_class, {parameter: b"late"}, b"late", HLAinteger64Time(20))
    early = publisher.updateAttributeValues(object_instance, {attribute: b"early"}, b"early", HLAinteger64Time(10))
    retracted = publisher.sendInteraction(interaction_class, {parameter: b"retracted"}, b"retracted", HLAinteger64Time(15))
    assert late.retractionHandleIsValid is True
    assert early.retractionHandleIsValid is True
    assert retracted.retractionHandleIsValid is True
    publisher.retract(retracted.handle)

    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None
    subscriber.timeAdvanceRequest(HLAinteger64Time(12))
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:3] == (object_instance, {attribute: b"early"}, b"early")
    assert reflection[6:] == (HLAinteger64Time(10), OrderType.TIMESTAMP, OrderType.TIMESTAMP, early.handle)
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.timeAdvanceRequest(HLAinteger64Time(25))
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:3] == (interaction_class, {parameter: b"late"}, b"late")
    assert received[6:] == (HLAinteger64Time(20), OrderType.TIMESTAMP, OrderType.TIMESTAMP, late.handle)
    publisher.retract(late.handle)
    request_retraction = subscriber_callbacks.last_callback("requestRetraction")
    assert request_retraction == (late.handle,)
    with pytest.raises(MessageCanNoLongerBeRetracted):
        publisher.retract(late.handle)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-010",
    "HLA2025-FI-005",
    "HLA2025-FI-009",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-102",
    "HLA2025-FI-SVC-104",
    "HLA2025-FI-SVC-105",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-113",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-FI-SVC-118",
    "HLA2025-FI-SVC-119",
    "HLA2025-FI-SVC-120",
)
def test_2025_shim_uses_selected_logical_time_factory_for_queries_and_grants() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import LogicalTimeAlreadyPassed, TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAfloat64Interval, HLAfloat64Time

    federation_name = f"shim-time-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
        logicalTimeImplementationName="HLAfloat64Time",
    )
    rti.joinFederationExecution(
        federateName="Clock",
        federateType="TestFederate",
        federationName=federation_name,
    )

    time_factory = rti.getTimeFactory()
    assert time_factory.getName() == "HLAfloat64Time"
    assert rti.queryLogicalTime() == HLAfloat64Time(0.0)
    assert rti.queryGALT().timeIsValid is True
    assert rti.queryGALT().time == HLAfloat64Time(0.0)
    assert rti.queryLITS().time == HLAfloat64Time(0.0)

    with pytest.raises(TimeRegulationIsNotEnabled):
        rti.queryLookahead()

    rti.enableTimeRegulation(HLAfloat64Interval(0.5))
    rti.enableTimeConstrained()
    assert rti.queryLookahead() == HLAfloat64Interval(0.5)
    rti.modifyLookahead(HLAfloat64Interval(0.25))
    assert rti.queryLookahead() == HLAfloat64Interval(0.25)

    rti.timeAdvanceRequest(HLAfloat64Time(12.5))
    assert rti.queryLogicalTime() == HLAfloat64Time(12.5)
    assert federate.last_callback("timeRegulationEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeConstrainedEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeAdvanceGrant") == (HLAfloat64Time(12.5),)

    with pytest.raises(LogicalTimeAlreadyPassed):
        rti.flushQueueRequest(HLAfloat64Time(12.0))

    rti.flushQueueRequest(HLAfloat64Time(20.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(20.0)
    assert federate.last_callback("flushQueueGrant") == (HLAfloat64Time(20.0), HLAfloat64Time(20.0))
    assert rti.queryGALT().time == HLAfloat64Time(20.0)
    assert rti.queryLITS().time == HLAfloat64Time(20.0)

    rti.timeAdvanceRequestAvailable(HLAfloat64Time(21.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(21.0)
    assert federate.last_callback("timeAdvanceGrant") == (HLAfloat64Time(21.0),)
    rti.nextMessageRequest(HLAfloat64Time(22.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(22.0)
    rti.nextMessageRequestAvailable(HLAfloat64Time(23.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(23.0)

    rti.enableAsynchronousDelivery()
    rti.disableAsynchronousDelivery()
    assert any(call[0] == "enableAsynchronousDelivery" for call in rti.calls)
    assert any(call[0] == "disableAsynchronousDelivery" for call in rti.calls)

    rti.disableTimeConstrained()
    assert any(call[0] == "disableTimeConstrained" for call in rti.calls)
    rti.disableTimeRegulation()
    with pytest.raises(TimeRegulationIsNotEnabled):
        rti.queryLookahead()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_blocks_window_closure_until_future_inputs_are_excluded() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import InvalidLogicalTime
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-future-exclusion-{uuid.uuid4().hex[:8]}"
    slow_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    slow = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")

    try:
        slow.connect(slow_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        slow.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        slow.joinFederationExecution(
            federateName="SlowRegulator",
            federateType="TimeWindowFederate",
            federationName=federation_name,
        )
        radar.joinFederationExecution(
            federateName="Radar",
            federateType="TimeWindowFederate",
            federationName=federation_name,
        )

        interaction_class = slow.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = slow.getParameterHandle(interaction_class, "TrackId")
        slow.publishInteractionClass(interaction_class)
        radar.subscribeInteractionClass(interaction_class)

        slow.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert slow_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        slow.timeAdvanceRequestAvailable(HLAinteger64Time(100))
        assert slow_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(100),)

        blocked_galt = radar.queryGALT()
        blocked_lits = radar.queryLITS()
        assert blocked_galt.timeIsValid is True
        assert blocked_lits.timeIsValid is True
        assert blocked_galt.time == HLAinteger64Time(101)
        assert blocked_lits.time == HLAinteger64Time(101)

        grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.timeAdvanceRequestAvailable(HLAinteger64Time(110))
        blocked_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[grant_baseline:]
        assert blocked_grants == []

        slow.timeAdvanceRequestAvailable(HLAinteger64Time(109))
        assert slow_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(109),)

        cleared_galt = radar.queryGALT()
        cleared_lits = radar.queryLITS()
        assert cleared_galt.timeIsValid is True
        assert cleared_lits.timeIsValid is True
        assert cleared_galt.time == HLAinteger64Time(110)
        assert cleared_lits.time == HLAinteger64Time(110)

        final_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[grant_baseline:]
        assert final_grants == [(HLAinteger64Time(110),)]

        with pytest.raises(InvalidLogicalTime):
            slow.sendInteraction(
                interaction_class,
                {parameter: b"late-track-109"},
                b"late-track-109",
                HLAinteger64Time(109),
            )

        receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        slow.sendInteraction(
            interaction_class,
            {parameter: b"boundary-track-110"},
            b"boundary-track-110",
            HLAinteger64Time(110),
        )
        slow.timeAdvanceRequestAvailable(HLAinteger64Time(120))
        radar.nextMessageRequestAvailable(HLAinteger64Time(120))

        receives = _callbacks_named_2025(radar_federate, "receiveInteraction")[receive_baseline:]
        assert len(receives) == 1
        assert receives[0][2] == b"boundary-track-110"
        assert receives[0][6] == HLAinteger64Time(110)
    finally:
        try:
            radar.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            slow.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            slow.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        try:
            radar.disconnect()
        except Exception:
            pass
        try:
            slow.disconnect()
        except Exception:
            pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_proves_time_window_core_progression() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InvalidLogicalTime
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-time-window-core-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    fast_federate = Recording2025FederateAmbassador()
    slow_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")
    fast = create_rti_ambassador(backend="shim")
    slow = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
            (fast, fast_federate),
            (slow, slow_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
            (fast, "FastMover"),
            (slow, "SlowMover"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishInteractionClass(track_interaction)
        radar.subscribeInteractionClass(track_interaction)
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        truth.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        truth.sendInteraction(
            track_interaction,
            {track_parameter: b"truth-105"},
            b"truth-105",
            HLAinteger64Time(105),
        )
        truth.sendInteraction(
            track_interaction,
            {track_parameter: b"sensor-106"},
            b"sensor-106",
            HLAinteger64Time(106),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(109))
        assert truth_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(109),)

        initial_galt = radar.queryGALT()
        initial_lits = radar.queryLITS()
        assert initial_galt.timeIsValid is True
        assert initial_lits.timeIsValid is True
        assert initial_galt.time == HLAinteger64Time(110)
        assert initial_lits.time == HLAinteger64Time(105)

        radar_receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        first_receive = _callbacks_named_2025(radar_federate, "receiveInteraction")[radar_receive_baseline:]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert len(first_receive) == 1
        assert len(first_grant) == 1
        assert first_receive[0][2] == b"truth-105"
        assert first_receive[0][6] == HLAinteger64Time(105)
        assert first_grant[0] == (HLAinteger64Time(105),)

        radar_receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        second_receive = _callbacks_named_2025(radar_federate, "receiveInteraction")[radar_receive_baseline:]
        second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert len(second_receive) == 1
        assert len(second_grant) == 1
        assert second_receive[0][2] == b"sensor-106"
        assert second_receive[0][6] == HLAinteger64Time(106)
        assert second_grant[0] == (HLAinteger64Time(106),)

        blocked_galt = radar.queryGALT()
        blocked_lits = radar.queryLITS()
        assert blocked_galt.timeIsValid is True
        assert blocked_lits.timeIsValid is True
        assert blocked_galt.time == HLAinteger64Time(110)
        assert blocked_lits.time == HLAinteger64Time(110)

        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        truth.timeAdvanceRequest(HLAinteger64Time(110))
        close_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert close_grants == [(HLAinteger64Time(110),)]
        assert truth_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(10))
        consumer.enableTimeConstrained()
        fast.enableTimeRegulation(HLAinteger64Interval(1))
        slow.enableTimeRegulation(HLAinteger64Interval(2))
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)
        assert fast_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert slow_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)

        for illegal_time in (100, 105, 109):
            with pytest.raises(InvalidLogicalTime):
                truth.sendInteraction(
                    track_interaction,
                    {track_parameter: f"late-{illegal_time}".encode("ascii")},
                    f"late-{illegal_time}".encode("ascii"),
                    HLAinteger64Time(illegal_time),
                )

        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.timeAdvanceRequest(HLAinteger64Time(119))
        consumer.nextMessageRequest(HLAinteger64Time(140))
        fast.timeAdvanceRequest(HLAinteger64Time(160))
        slow.timeAdvanceRequest(HLAinteger64Time(118))
        assert truth.queryLogicalTime() == HLAinteger64Time(119)
        assert fast.queryLogicalTime() == HLAinteger64Time(160)
        assert slow.queryLogicalTime() == HLAinteger64Time(118)

        post_close_inputs = [
            int(callback[6].value)
            for callback in _callbacks_named_2025(radar_federate, "receiveInteraction")
            if callback[6] is not None
        ]
        assert all(timestamp >= 110 for timestamp in post_close_inputs)
    finally:
        for rti in (slow, fast, consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (slow, fast, consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_ignores_receive_order_poison_after_window_close() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-receive-order-poison-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        target_object = truth.registerObjectInstance(target_class, "ReceiveOrderPoisonTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(110))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        timestamped_reflections = [
            callback
            for callback in _callbacks_named_2025(radar_federate, "reflectAttributeValues")
            if callback[6] is not None and callback[6] < HLAinteger64Time(110)
        ]
        closed_window_tags_before = [callback[2] for callback in timestamped_reflections]
        assert closed_window_tags_before == [b"truth-105", b"truth-106"]

        truth.changeAttributeOrderType(target_object, {position}, OrderType.RECEIVE)
        radar_federate.callbacks.clear()
        truth.updateAttributeValues(target_object, {position: b"receive-order-poison"}, b"receive-order-poison")

        poison_reflection = radar_federate.last_callback("reflectAttributeValues")
        assert poison_reflection is not None
        assert poison_reflection[2] == b"receive-order-poison"
        assert poison_reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

        closed_window_tags_after = [
            callback[2]
            for callback in _callbacks_named_2025(radar_federate, "reflectAttributeValues")
            if callback[6] is not None and callback[6] < HLAinteger64Time(110)
        ]
        assert closed_window_tags_after == []

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        truth.timeAdvanceRequest(HLAinteger64Time(120))
        consumer.nextMessageRequest(HLAinteger64Time(120))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-poison-safe"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(120))

        consumer_receive = _callbacks_named_2025(consumer_federate, "receiveInteraction")[-1]
        assert consumer_receive[2] == b"radar-track-output"
        assert consumer_receive[1] == {track_parameter: b"track-poison-safe"}
        assert consumer_receive[6] == HLAinteger64Time(111)
        assert closed_window_tags_before == [b"truth-105", b"truth-106"]
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_delivers_post_closure_timestamped_output_to_consumer() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-output-delivery-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        truth.connect(truth_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        consumer.connect(consumer_federate, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        target_object = truth.registerObjectInstance(target_class, "OutputTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(120))

        radar.nextMessageRequest(HLAinteger64Time(110))
        first_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert first_reflect[2] == b"truth-105"
        assert first_reflect[6] == HLAinteger64Time(105)
        assert first_grant == (HLAinteger64Time(105),)

        radar.nextMessageRequest(HLAinteger64Time(110))
        second_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert second_reflect[2] == b"truth-106"
        assert second_reflect[6] == HLAinteger64Time(106)
        assert second_grant == (HLAinteger64Time(106),)

        radar.nextMessageRequest(HLAinteger64Time(110))
        window_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert window_close_grant == (HLAinteger64Time(110),)
        assert _callbacks_named_2025(consumer_federate, "receiveInteraction") == []

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(120))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-100-110[from truth-105,truth-106]"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(120))

        consumer_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(consumer_receives) == 1
        consumer_receive = consumer_receives[-1]
        assert consumer_receive[2] == b"radar-track-output"
        assert consumer_receive[6] == HLAinteger64Time(111)
        assert consumer_receive[1] == {track_parameter: b"track-100-110[from truth-105,truth-106]"}

        consumer.nextMessageRequest(HLAinteger64Time(130))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        radar.timeAdvanceRequest(HLAinteger64Time(130))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 1
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_preserves_consumer_timestamp_order_between_competing_output_and_radar_output() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-consumer-order-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    other_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    other = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (other, other_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (other, "Other"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        other.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, "ConsumerOrderTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(120))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        other.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        other.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)

        consumer.nextMessageRequest(HLAinteger64Time(120))
        other.sendInteraction(
            track_interaction,
            {track_parameter: b"other-track-110[gate]"},
            b"other-track-output",
            HLAinteger64Time(110),
        )
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"radar-track-111[from truth-105,truth-106]"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        other.timeAdvanceRequest(HLAinteger64Time(120))
        radar.timeAdvanceRequest(HLAinteger64Time(120))
        consumer.nextMessageRequest(HLAinteger64Time(120))

        receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(receives) == 2
        assert [receive[2] for receive in receives] == [b"other-track-output", b"radar-track-output"]
        assert [receive[6] for receive in receives] == [HLAinteger64Time(110), HLAinteger64Time(111)]
        assert receives[0][1] == {track_parameter: b"other-track-110[gate]"}
        assert receives[1][1] == {track_parameter: b"radar-track-111[from truth-105,truth-106]"}

        consumer.nextMessageRequest(HLAinteger64Time(130))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        other.timeAdvanceRequest(HLAinteger64Time(130))
        radar.timeAdvanceRequest(HLAinteger64Time(130))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, other, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, other, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_keeps_two_scan_pipeline_outputs_separated() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-pipeline-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, "PipelineTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)

        truth.updateAttributeValues(target_object, {position: b"scan1-input-a"}, b"scan1-input-a", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"scan1-input-b"}, b"scan1-input-b", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(110))
        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)

        truth.updateAttributeValues(target_object, {position: b"scan2-input"}, b"scan2-input", HLAinteger64Time(112))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        radar.nextMessageRequest(HLAinteger64Time(120))
        scan2_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        assert scan2_reflect[2] == b"scan2-input"
        assert scan2_reflect[6] == HLAinteger64Time(112)

        consumer.nextMessageRequest(HLAinteger64Time(130))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-scan-1[from scan1-input-a,scan1-input-b]"},
            b"scan1-track-output",
            HLAinteger64Time(115),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(115))

        radar.nextMessageRequest(HLAinteger64Time(120))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(120),)

        consumer.nextMessageRequest(HLAinteger64Time(130))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-scan-2[from scan2-input]"},
            b"scan2-track-output",
            HLAinteger64Time(122),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(130))

        receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(receives) == 2
        assert [receive[2] for receive in receives] == [b"scan1-track-output", b"scan2-track-output"]
        assert [receive[6] for receive in receives] == [HLAinteger64Time(115), HLAinteger64Time(122)]
        assert receives[0][1] == {track_parameter: b"track-scan-1[from scan1-input-a,scan1-input-b]"}
        assert receives[1][1] == {track_parameter: b"track-scan-2[from scan2-input]"}

        consumer.nextMessageRequest(HLAinteger64Time(140))
        truth.timeAdvanceRequest(HLAinteger64Time(140))
        radar.timeAdvanceRequest(HLAinteger64Time(140))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass
@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_open_and_closed_time_window_state() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarWindowRestoreConfig

    federation_name = f"shim-2025-window-restore-{uuid.uuid4().hex[:8]}"
    config = TargetRadarWindowRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")

    def snapshot_window_state(
        *,
        phase: str,
        window_closed: bool,
        closed_at: int | None,
        last_grant: int,
        received_tags: list[bytes],
    ) -> dict[str, object]:
        return {
            "phase": phase,
            "window_closed": window_closed,
            "closed_at": closed_at,
            "last_grant": last_grant,
            "received_tags": list(received_tags),
        }

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert truth_federate.last_callback("federationRestoreBegun") == ()
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()

    try:
        truth.connect(truth_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-105"},
            b"truth-105",
            HLAinteger64Time(config.first_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.first_input_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        first_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert first_reflect[2] == b"truth-105"
        assert first_grant == (HLAinteger64Time(config.first_input_time),)
        saved_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=config.first_input_time,
            received_tags=[b"truth-105"],
        )

        complete_save(config.save_open_name)

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-106"},
            b"truth-106",
            HLAinteger64Time(config.second_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        dirty_second_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        dirty_second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_second_reflect[2] == b"truth-106"
        assert dirty_second_grant == (HLAinteger64Time(config.second_input_time),)
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        dirty_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_close_grant == (HLAinteger64Time(config.scan_window_end),)

        complete_restore(config.save_open_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.first_input_time)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.first_input_time)
        restored_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=config.first_input_time,
            received_tags=[b"truth-105"],
        )
        assert restored_open_state == saved_open_state

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-106-branch"},
            b"truth-106-branch",
            HLAinteger64Time(config.second_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        reclosed_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        reclosed_second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert reclosed_reflect[2] == b"truth-106-branch"
        assert reclosed_second_grant == (HLAinteger64Time(config.second_input_time),)
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        reclosed_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert reclosed_grant == (HLAinteger64Time(config.scan_window_end),)
        saved_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=config.scan_window_end,
            last_grant=config.scan_window_end,
            received_tags=[b"truth-105", b"truth-106-branch"],
        )

        complete_save(config.save_closed_name)

        truth.updateAttributeValues(
            target_object,
            {position: b"dirty-post-close"},
            b"dirty-post-close",
            HLAinteger64Time(config.post_close_resume_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.post_close_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.post_close_resume_time))
        dirty_post_close_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        dirty_post_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_post_close_reflect[2] == b"dirty-post-close"
        assert dirty_post_close_grant == (HLAinteger64Time(config.post_close_resume_time),)

        complete_restore(config.save_closed_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        restored_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=config.scan_window_end,
            last_grant=config.scan_window_end,
            received_tags=[b"truth-105", b"truth-106-branch"],
        )
        assert restored_closed_state == saved_closed_state

        radar_federate.callbacks.clear()
        truth.timeAdvanceRequest(HLAinteger64Time(config.post_close_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.post_close_resume_time))
        assert _callbacks_named_2025(radar_federate, "reflectAttributeValues") == []
    finally:
        for rti in (radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_closed_window_output_resume_without_dirty_replay() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarWindowRestoreOutputConfig

    federation_name = f"shim-2025-window-restore-output-{uuid.uuid4().hex[:8]}"
    config = TargetRadarWindowRestoreOutputConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        assert consumer_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        consumer.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        consumer.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()
        assert consumer_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        assert consumer_federate.last_callback("initiateFederateRestore") == (save_label, config.consumer_name, consumer_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        consumer.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()
        assert consumer_federate.last_callback("federationRestored") == ()

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        consumer_handle = consumer.joinFederationExecution(
            federateName=config.consumer_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        radar_track_interaction = radar.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        radar_track_parameter = radar.getParameterHandle(radar_track_interaction, "TrackId")
        consumer_track_interaction = consumer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        consumer_track_parameter = consumer.getParameterHandle(consumer_track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})
        radar.publishInteractionClass(radar_track_interaction)
        consumer.subscribeInteractionClass(consumer_track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(config.first_input_time))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(config.second_input_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        window_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert window_close_grant == (HLAinteger64Time(config.scan_window_end),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(radar_track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)

        complete_save(config.save_closed_name)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: b"dirty-track-100-110"},
            b"dirty-track-output",
            HLAinteger64Time(config.radar_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        dirty_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(dirty_receives) == 1
        assert dirty_receives[-1][2] == b"dirty-track-output"
        assert dirty_receives[-1][6] == HLAinteger64Time(config.radar_output_time)
        assert dirty_receives[-1][1] == {consumer_track_parameter: b"dirty-track-100-110"}

        complete_restore(config.save_closed_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: b"restored-track-100-110"},
            b"restored-track-output",
            HLAinteger64Time(config.radar_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        post_restore_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(post_restore_receives) == 1
        assert post_restore_receives[-1][2] == b"restored-track-output"
        assert post_restore_receives[-1][6] == HLAinteger64Time(config.radar_output_time)
        assert post_restore_receives[-1][1] == {consumer_track_parameter: b"restored-track-100-110"}
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_pipeline_resume_without_cross_window_replay() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarPipelineRestoreConfig

    federation_name = f"shim-2025-pipeline-restore-{uuid.uuid4().hex[:8]}"
    config = TargetRadarPipelineRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        assert consumer_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        consumer.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        consumer.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()
        assert consumer_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        assert consumer_federate.last_callback("initiateFederateRestore") == (save_label, config.consumer_name, consumer_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        consumer.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()
        assert consumer_federate.last_callback("federationRestored") == ()

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        consumer_handle = consumer.joinFederationExecution(
            federateName=config.consumer_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        radar_track_interaction = radar.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        radar_track_parameter = radar.getParameterHandle(radar_track_interaction, "TrackId")
        consumer_track_interaction = consumer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        consumer_track_parameter = consumer.getParameterHandle(consumer_track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})
        radar.publishInteractionClass(radar_track_interaction)
        consumer.subscribeInteractionClass(consumer_track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"scan1-input-a"}, b"scan1-input-a", HLAinteger64Time(config.scan1_input_a_time))
        truth.updateAttributeValues(target_object, {position: b"scan1-input-b"}, b"scan1-input-b", HLAinteger64Time(config.scan1_input_b_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan1_end))
        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(config.scan1_end))
        scan1_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert scan1_close_grant == (HLAinteger64Time(config.scan1_end),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(radar_track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(config.scan1_end))
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan1_end)

        truth.updateAttributeValues(target_object, {position: b"scan2-input"}, b"scan2-input", HLAinteger64Time(config.scan2_input_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        scan2_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        scan2_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert scan2_reflect[2] == b"scan2-input"
        assert scan2_grant == (HLAinteger64Time(config.scan2_input_time),)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan2_input_time)

        complete_save(config.save_name)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.dirty_scan1_track_id.encode("utf-8")},
            b"dirty-scan1-track-output",
            HLAinteger64Time(config.scan1_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.scan1_output_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        dirty_scan2_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_scan2_close_grant == (HLAinteger64Time(config.scan2_end),)
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.dirty_scan2_track_id.encode("utf-8")},
            b"dirty-scan2-track-output",
            HLAinteger64Time(config.scan2_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        dirty_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert [record[2] for record in dirty_receives] == [
            b"dirty-scan1-track-output",
            b"dirty-scan2-track-output",
        ]

        complete_restore(config.save_name)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan2_input_time)
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan1_end)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.restored_scan1_track_id.encode("utf-8")},
            b"restored-scan1-track-output",
            HLAinteger64Time(config.scan1_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.scan1_output_time))

        radar_federate.callbacks.clear()
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        post_restore_scan2_reflects = _callbacks_named_2025(radar_federate, "reflectAttributeValues")
        restored_scan2_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert post_restore_scan2_reflects == []
        assert restored_scan2_close_grant == (HLAinteger64Time(config.scan2_end),)

        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.restored_scan2_track_id.encode("utf-8")},
            b"restored-scan2-track-output",
            HLAinteger64Time(config.scan2_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        restored_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert [record[2] for record in restored_receives] == [
            b"restored-scan1-track-output",
            b"restored-scan2-track-output",
        ]
        assert restored_receives[0][1] == {consumer_track_parameter: config.restored_scan1_track_id.encode("utf-8")}
        assert restored_receives[1][1] == {consumer_track_parameter: config.restored_scan2_track_id.encode("utf-8")}

        consumer.nextMessageRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        radar.timeAdvanceRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
