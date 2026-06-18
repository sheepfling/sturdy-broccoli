from __future__ import annotations

import inspect
import json
import uuid
from pathlib import Path

import pytest


class Recording2025FederateAmbassador:
    def __init__(self) -> None:
        self.callbacks: list[tuple[str, tuple[object, ...]]] = []

    def reportFederationExecutions(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutions", (report,)))

    def reportFederationExecutionMembers(self, federationName, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionMembers", (federationName, report)))

    def reportFederationExecutionDoesNotExist(self, federationName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionDoesNotExist", (federationName,)))

    def federateResigned(self, reasonForResignDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federateResigned", (reasonForResignDescription,)))

    def timeRegulationEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeRegulationEnabled", (time,)))

    def timeConstrainedEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeConstrainedEnabled", (time,)))

    def timeAdvanceGrant(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeAdvanceGrant", (time,)))

    def flushQueueGrant(self, time, optimisticTime) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("flushQueueGrant", (time, optimisticTime)))

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


@pytest.mark.requirements("HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-FI-001", "HLA2025-MOD-006")
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

    with pytest.raises(InteractionClassNotPublished):
        publisher.sendInteraction(interaction_class, {parameter: b"T-1"}, b"not-published")
    publisher.publishInteractionClass(interaction_class)
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
    assert received[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

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


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-FI-005", "HLA2025-FI-006")
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


@pytest.mark.requirements("HLA2025-NEW-001", "HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-FI-001")
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


@pytest.mark.requirements("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy(tmp_path: Path) -> None:
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


@pytest.mark.requirements("HLA2025-MOD-007", "HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-FI-001")
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
    publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-region")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
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

    publisher.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements("HLA2025-MOD-005", "HLA2025-FI-001", "HLA2025-FI-005")
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


@pytest.mark.requirements("HLA2025-MOD-005", "HLA2025-FI-001", "HLA2025-FI-005")
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
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="BoundaryFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert rti.getServiceReportingSwitch() is False
    rti.setServiceReportingSwitch(True)
    assert rti.getServiceReportingSwitch() is True

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

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FI-005")
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


@pytest.mark.requirements("HLA2025-NEW-003", "HLA2025-FI-001", "HLA2025-FI-005")
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


@pytest.mark.requirements("HLA2025-NEW-005", "HLA2025-FI-001", "HLA2025-FI-005")
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


@pytest.mark.requirements("HLA2025-MOD-008", "HLA2025-RET-001", "HLA2025-FI-001", "HLA2025-FI-005")
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

    rti.setObjectClassRelevanceAdvisorySwitch(True)
    rti.setAttributeRelevanceAdvisorySwitch(True)
    rti.setAttributeScopeAdvisorySwitch(True)
    rti.setInteractionRelevanceAdvisorySwitch(True)
    rti.setConveyRegionDesignatorSetsSwitch(False)
    rti.setServiceReportingSwitch(True)
    rti.setExceptionReportingSwitch(False)
    rti.setSendServiceReportsToFileSwitch(True)

    assert rti.getObjectClassRelevanceAdvisorySwitch() is True
    assert rti.getAttributeRelevanceAdvisorySwitch() is True
    assert rti.getAttributeScopeAdvisorySwitch() is True
    assert rti.getInteractionRelevanceAdvisorySwitch() is True
    assert rti.getConveyRegionDesignatorSetsSwitch() is False
    assert rti.getServiceReportingSwitch() is True
    assert rti.getExceptionReportingSwitch() is False
    assert rti.getSendServiceReportsToFileSwitch() is True

    with pytest.raises(RTIinternalError, match="requires a bool"):
        rti.setServiceReportingSwitch("yes")
    with pytest.raises(RTIinternalError, match="does not implement"):
        rti.enableObjectClassRelevanceAdvisorySwitch()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-NEW-002", "HLA2025-FI-001", "HLA2025-FI-005")
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


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-006")
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


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-OMT-007")
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


@pytest.mark.requirements("HLA2025-FR-010", "HLA2025-FI-005", "HLA2025-FI-009", "HLA2025-MOD-006")
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

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
