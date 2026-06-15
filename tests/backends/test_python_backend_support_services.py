import pytest
from pathlib import Path

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from hla2010.enums import CallbackModel
from hla2010.enums import OrderType, ResignAction, ServiceGroup
from hla2010.exceptions import (
    AttributeNotOwned,
    FederateHandleNotKnown,
    InvalidFederateHandle,
    InvalidOrderName,
    InvalidOrderType,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationType,
    InvalidUpdateRateDesignator,
    NameNotFound,
    ObjectInstanceNotKnown,
    AttributeRelevanceAdvisorySwitchIsOn,
    AttributeRelevanceAdvisorySwitchIsOff,
    AttributeScopeAdvisorySwitchIsOn,
    AttributeScopeAdvisorySwitchIsOff,
    InteractionRelevanceAdvisorySwitchIsOn,
    InteractionRelevanceAdvisorySwitchIsOff,
    ObjectClassRelevanceAdvisorySwitchIsOn,
    ObjectClassRelevanceAdvisorySwitchIsOff,
)
from hla2010.handles import (
    AttributeHandleFactory,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    AttributeHandleSet,
    DimensionHandleFactory,
    DimensionHandleSetFactory,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandleFactory,
    ObjectClassHandleFactory,
    ObjectInstanceHandleFactory,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)
from hla2010.types import RangeBounds

from tests.backends.python_backend_extended_support import drain, joined_pair


def _write_hierarchy_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Hierarchy Test FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Base</name>
        <attribute><name>Payload</name><dataType>HLAunicodeString</dataType></attribute>
        <objectClass>
          <name>Child</name>
          <attribute><name>Extra</name><dataType>HLAunicodeString</dataType></attribute>
        </objectClass>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData representation="HLAunicodeString"/>
    </basicDataRepresentations>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )


def _write_update_rate_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Update Rate Test FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <updateRates>
    <updateRate><name>HLAdefault</name><rate>0.0</rate></updateRate>
    <updateRate><name>Fast</name><rate>2.0</rate></updateRate>
  </updateRates>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RateObject</name>
        <attribute><name>Payload</name><dataType>HLAunicodeString</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData representation="HLAunicodeString"/>
    </basicDataRepresentations>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )


def _write_transport_and_update_rate_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Transport Update Rate Test FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>HLAdefault</name><rate>0.0</rate></updateRate>
    <updateRate><name>Fast</name><rate>2.0</rate></updateRate>
  </updateRates>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Base</name>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <transportation>HLAbestEffort</transportation>
          <updateRate>Fast</updateRate>
        </attribute>
        <objectClass>
          <name>Child</name>
          <attribute>
            <name>Extra</name>
            <dataType>HLAunicodeString</dataType>
            <transportation>HLAreliable</transportation>
          </attribute>
        </objectClass>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>Ping</name>
        <transportation>HLAbestEffort</transportation>
        <parameter><name>Value</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dataTypes>
    <basicDataRepresentations>
      <basicData representation="HLAunicodeString"/>
    </basicDataRepresentations>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )


def test_support_lookups_round_trip_class_handle_and_name():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("support-lookups-fed")
    obj_cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(obj_cls, "Position")
    inter_cls = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    param = owner.getParameterHandle(inter_cls, "TrackId")

    owner.publishObjectClassAttributes(obj_cls, {attr})
    owner.publishInteractionClass(inter_cls)
    obj = owner.registerObjectInstance(obj_cls, "Support-1")

    drain(owner, acquirer)

    assert owner.getFederateName(owner.getFederateHandle("alpha")) == "alpha"
    assert acquirer.getFederateName(acquirer.getFederateHandle("bravo")) == "bravo"
    assert owner.getObjectClassName(obj_cls) == "HLAobjectRoot.Target"
    assert owner.getAttributeName(obj_cls, attr) == "Position"
    assert owner.getInteractionClassName(inter_cls) == "HLAinteractionRoot.TrackReport"
    assert owner.getParameterName(inter_cls, param) == "TrackId"
    assert owner.getObjectInstanceName(obj) == "Support-1"
    assert owner.getKnownObjectClassHandle(obj) == obj_cls
    assert owner.getObjectInstanceHandle("Support-1") == obj
    assert owner.getTransportationTypeName(owner.getTransportationTypeHandle("HLAreliable")) == "HLAreliable"
    assert owner.getTransportationName(owner.getTransportationType("HLAreliable")) == "HLAreliable"
    assert owner.getTransportationTypeName(owner.getTransportationTypeHandle("HLAbestEffort")) == "HLAbestEffort"
    assert owner.getTransportationName(owner.getTransportationType("HLAbestEffort")) == "HLAbestEffort"
    assert owner.getOrderName(OrderType.RECEIVE) == "RECEIVE"
    assert owner.getOrderType("HLAtimestamp") is OrderType.TIMESTAMP

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-lookups-fed")


def test_support_dimension_and_update_rate_helpers():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-dim-fed")
    obj_cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(obj_cls, "Position")
    inter_cls = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    class_dims = owner.getAvailableDimensionsForClassAttribute(obj_cls, attr)
    interaction_dims = owner.getAvailableDimensionsForInteractionClass(inter_cls)
    assert class_dims
    assert interaction_dims

    dim = next(iter(class_dims))
    assert owner.getDimensionHandle(owner.getDimensionName(dim)) == dim
    assert owner.getUpdateRateValue("default") == 0.0
    assert owner.getUpdateRateValueForAttribute(owner.registerObjectInstance(obj_cls, "Support-2"), attr) == 0.0

    owner.setAutomaticResignDirective(ResignAction.DELETE_OBJECTS)
    assert owner.getAutomaticResignDirective() is ResignAction.DELETE_OBJECTS
    owner.setAutomaticResignDirective(ResignAction.NO_ACTION)
    assert owner.getAutomaticResignDirective() is ResignAction.NO_ACTION

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-dim-fed")


def test_support_update_rate_lookup_for_attribute_reflects_subscribed_rate(tmp_path: Path):
    fom_path = tmp_path / "update-rate-support.xml"
    _write_update_rate_fom(fom_path)

    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()
    owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution("support-update-rate-fed", fom_path)
    owner.joinFederationExecution("alpha", "type-a", "support-update-rate-fed")
    observer.joinFederationExecution("bravo", "type-b", "support-update-rate-fed")

    obj_cls = owner.getObjectClassHandle("HLAobjectRoot.RateObject")
    attr = owner.getAttributeHandle(obj_cls, "Payload")
    owner.publishObjectClassAttributes(obj_cls, {attr})
    observer.subscribeObjectClassAttributes(obj_cls, {attr}, "Fast")
    obj = owner.registerObjectInstance(obj_cls, "Rate-1")

    drain(owner, observer)

    assert observer.getUpdateRateValue("Fast") == 2.0
    assert observer.getUpdateRateValueForAttribute(obj, attr) == 2.0
    assert owner.getUpdateRateValueForAttribute(obj, attr) == 0.0

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-update-rate-fed")


def test_support_normalizers_and_factories():
    _, owner, acquirer, _owner_fed, _acquirer_fed, h1, _h2 = joined_pair("support-normalize-fed")

    assert owner.normalizeFederateHandle(h1) == h1
    assert owner.normalizeServiceGroup(ServiceGroup.OBJECT_MANAGEMENT) is ServiceGroup.OBJECT_MANAGEMENT
    assert owner.normalizeServiceGroup("object-management") is ServiceGroup.OBJECT_MANAGEMENT

    assert isinstance(owner.getAttributeHandleFactory(), AttributeHandleFactory)
    assert isinstance(owner.getAttributeHandleSetFactory(), AttributeHandleSetFactory)
    assert isinstance(owner.getAttributeHandleValueMapFactory(), AttributeHandleValueMapFactory)
    assert isinstance(owner.getAttributeSetRegionSetPairListFactory(), AttributeSetRegionSetPairListFactory)
    assert isinstance(owner.getDimensionHandleFactory(), DimensionHandleFactory)
    assert isinstance(owner.getDimensionHandleSetFactory(), DimensionHandleSetFactory)
    assert isinstance(owner.getFederateHandleFactory(), FederateHandleFactory)
    assert isinstance(owner.getFederateHandleSetFactory(), FederateHandleSetFactory)
    assert isinstance(owner.getInteractionClassHandleFactory(), InteractionClassHandleFactory)
    assert isinstance(owner.getObjectClassHandleFactory(), ObjectClassHandleFactory)
    assert isinstance(owner.getObjectInstanceHandleFactory(), ObjectInstanceHandleFactory)
    assert isinstance(owner.getParameterHandleFactory(), ParameterHandleFactory)
    assert isinstance(owner.getParameterHandleValueMapFactory(), ParameterHandleValueMapFactory)
    assert isinstance(owner.getRegionHandleSetFactory(), RegionHandleSetFactory)
    assert isinstance(owner.getTransportationTypeHandleFactory(), TransportationTypeHandleFactory)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-normalize-fed")


def test_support_invalid_inputs_raise_expected_errors():
    _, owner, acquirer, _owner_fed, _acquirer_fed, h1, _h2 = joined_pair("support-invalid-fed")

    with pytest.raises(FederateHandleNotKnown):
        owner.getFederateName(type(h1)(h1.value + 1000))
    with pytest.raises(InvalidFederateHandle):
        owner.normalizeFederateHandle(type(h1)(h1.value + 1000))
    with pytest.raises(InvalidServiceGroup):
        owner.normalizeServiceGroup("not-a-service-group")
    with pytest.raises(InvalidOrderName):
        owner.getOrderType("not-an-order")
    with pytest.raises(InvalidOrderType):
        owner.getOrderName("receive")  # type: ignore[arg-type]
    with pytest.raises(InvalidTransportationName):
        owner.getTransportationTypeHandle("HLAimaginaryTransport")
    with pytest.raises(InvalidTransportationType):
        owner.getTransportationTypeName(type(owner.getTransportationTypeHandle("HLAreliable"))(999999))
    with pytest.raises(InvalidUpdateRateDesignator):
        owner.getUpdateRateValue("fast")
    with pytest.raises(NameNotFound):
        owner.getFederateHandle("missing")

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-invalid-fed")


def test_support_advisory_switches_toggle_and_reject_duplicates():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-switch-fed")

    owner.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOn):
        owner.enableObjectClassRelevanceAdvisorySwitch()
    owner.disableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOff):
        owner.disableObjectClassRelevanceAdvisorySwitch()

    owner.enableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOn):
        owner.enableAttributeRelevanceAdvisorySwitch()
    owner.disableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOff):
        owner.disableAttributeRelevanceAdvisorySwitch()

    owner.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOn):
        owner.enableAttributeScopeAdvisorySwitch()
    owner.disableAttributeScopeAdvisorySwitch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOff):
        owner.disableAttributeScopeAdvisorySwitch()

    owner.enableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOn):
        owner.enableInteractionRelevanceAdvisorySwitch()
    owner.disableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOff):
        owner.disableInteractionRelevanceAdvisorySwitch()

    owner.enableCallbacks()
    owner.disableCallbacks()

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-switch-fed")


def test_discovery_uses_closest_subscribed_superclass_and_known_class_stays_stable(tmp_path: Path):
    fom_path = tmp_path / "hierarchy-fom.xml"
    _write_hierarchy_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()

    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("hierarchy-discovery-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "hierarchy-discovery-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "hierarchy-discovery-fed")

    base = subscriber.getObjectClassHandle("HLAobjectRoot.Base")
    child = publisher.getObjectClassHandle("HLAobjectRoot.Base.Child")
    payload = subscriber.getAttributeHandle(base, "Payload")

    subscriber.subscribeObjectClassAttributes(base, {payload})
    publisher.publishObjectClassAttributes(child, {publisher.getAttributeHandle(child, "Payload")})
    obj = publisher.registerObjectInstance(child, "Hierarchy-1")
    drain(publisher, subscriber)

    discovery = sub_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    assert discovery.args[1] == base
    assert subscriber.getKnownObjectClassHandle(obj) == base

    publisher.updateAttributeValues(obj, {publisher.getAttributeHandle(child, "Payload"): b"first"}, b"tag")
    drain(publisher, subscriber)
    assert subscriber.getKnownObjectClassHandle(obj) == base

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("hierarchy-discovery-fed")


def test_reflect_attributes_are_mapped_to_known_discovered_class_handles(tmp_path: Path):
    fom_path = tmp_path / "hierarchy-fom.xml"
    _write_hierarchy_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()

    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("hierarchy-reflect-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "hierarchy-reflect-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "hierarchy-reflect-fed")

    base = subscriber.getObjectClassHandle("HLAobjectRoot.Base")
    child = publisher.getObjectClassHandle("HLAobjectRoot.Base.Child")
    base_payload = subscriber.getAttributeHandle(base, "Payload")
    child_payload = publisher.getAttributeHandle(child, "Payload")

    subscriber.subscribeObjectClassAttributes(base, {base_payload})
    publisher.publishObjectClassAttributes(child, {child_payload})
    obj = publisher.registerObjectInstance(child, "Hierarchy-Reflect-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.updateAttributeValues(obj, {child_payload: b"payload"}, b"tag")
    drain(publisher, subscriber)

    reflection = sub_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {base_payload: b"payload"}
    assert subscriber.getKnownObjectClassHandle(obj) == base

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("hierarchy-reflect-fed")


def test_local_delete_clears_only_local_knowledge_and_object_can_be_rediscovered():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("local-delete-knowledge-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Local-Delete-1")
    drain(owner, observer)
    assert observer.getObjectInstanceHandle("Local-Delete-1") == obj

    observer.localDeleteObjectInstance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getObjectInstanceHandle("Local-Delete-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getKnownObjectClassHandle(obj)

    owner.updateAttributeValues(obj, {attr: b"rediscover"}, b"\x00\x00\x00\x00")
    drain(owner, observer)

    discovery = observer_fed.last_callback("discoverObjectInstance")
    reflection = observer_fed.last_callback("reflectAttributeValues")
    assert discovery is not None
    assert reflection is not None
    assert observer.getObjectInstanceHandle("Local-Delete-1") == obj
    assert observer.getKnownObjectClassHandle(obj) == cls

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("local-delete-knowledge-fed")


def test_orphan_object_remains_discovered_until_local_delete_clears_only_local_knowledge():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("orphan-object-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Orphan-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    assert owner.isAttributeOwnedByFederate(obj, attr) is False
    assert observer.getObjectInstanceHandle("Orphan-1") == obj
    assert observer.getKnownObjectClassHandle(obj) == cls

    observer.localDeleteObjectInstance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getObjectInstanceHandle("Orphan-1")

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("orphan-object-fed")


def test_orphan_object_lifecycle_supports_late_discovery_local_delete_and_global_remove():
    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    late = rti_ambassador(engine=engine)
    owner_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()
    late_fed = RecordingFederateAmbassador()

    owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_EVOKED)
    late.connect(late_fed, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution("orphan-lifecycle-fed", "TargetRadarFOMmodule.xml")
    owner.joinFederationExecution("owner", "type-owner", "orphan-lifecycle-fed")
    observer.joinFederationExecution("observer", "type-observer", "orphan-lifecycle-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Orphan-Lifecycle-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    assert owner.isAttributeOwnedByFederate(obj, attr) is False
    assert observer.getObjectInstanceHandle("Orphan-Lifecycle-1") == obj

    late.joinFederationExecution("late", "type-late", "orphan-lifecycle-fed")
    late.subscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer, late)

    late_discovery = late_fed.last_callback("discoverObjectInstance")
    assert late_discovery is not None
    assert late_discovery.args[0] == obj
    assert late.getObjectInstanceHandle("Orphan-Lifecycle-1") == obj
    assert late.getKnownObjectClassHandle(obj) == cls

    observer.localDeleteObjectInstance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getObjectInstanceHandle("Orphan-Lifecycle-1")

    owner.deleteObjectInstance(obj, b"orphan-delete")
    drain(owner, observer, late)

    assert observer_fed.last_callback("removeObjectInstance") is None
    removed = late_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"orphan-delete"
    with pytest.raises(ObjectInstanceNotKnown):
        late.getObjectInstanceHandle("Orphan-Lifecycle-1")

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    late.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("orphan-lifecycle-fed")


def test_delete_object_instance_notifies_known_federates_with_remove_object_instance():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("remove-object-callback-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Remove-1")
    drain(owner, observer)
    assert observer.getObjectInstanceHandle("Remove-1") == obj
    observer_fed.clear()

    owner.deleteObjectInstance(obj, b"delete-tag")
    drain(owner, observer)

    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"delete-tag"
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getObjectInstanceHandle("Remove-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getKnownObjectClassHandle(obj)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("remove-object-callback-fed")


def test_update_rate_designator_throttles_timed_reflects(tmp_path: Path):
    fom_path = tmp_path / "update-rate-fom.xml"
    _write_update_rate_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()

    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("update-rate-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "update-rate-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "update-rate-fed")

    cls = publisher.getObjectClassHandle("HLAobjectRoot.RateObject")
    attr = publisher.getAttributeHandle(cls, "Payload")
    factory = publisher.getTimeFactory()

    publisher.publishObjectClassAttributes(cls, {attr})
    subscriber.subscribeObjectClassAttributes(cls, {attr}, "Fast")
    publisher.enableTimeRegulation(factory.make_interval(0.1))
    subscriber.enableTimeConstrained()
    drain(publisher, subscriber)

    obj = publisher.registerObjectInstance(cls, "Rate-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.updateAttributeValues(obj, {attr: b"t1"}, b"tag1", factory.make_time(1.0))
    publisher.updateAttributeValues(obj, {attr: b"t12"}, b"tag12", factory.make_time(1.2))
    publisher.updateAttributeValues(obj, {attr: b"t16"}, b"tag16", factory.make_time(1.6))
    drain(publisher, subscriber)

    publisher.timeAdvanceRequest(factory.make_time(2.0))
    subscriber.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(publisher, subscriber)
    subscriber.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][attr] for record in reflections]
    assert values == [b"t1", b"t16"]
    assert subscriber.getUpdateRateValue("Fast") == 2.0

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("update-rate-fed")


def test_update_rate_designator_does_not_suppress_receive_order_updates(tmp_path: Path):
    fom_path = tmp_path / "update-rate-ro-fom.xml"
    _write_update_rate_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()

    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("update-rate-ro-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "update-rate-ro-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "update-rate-ro-fed")

    cls = publisher.getObjectClassHandle("HLAobjectRoot.RateObject")
    attr = publisher.getAttributeHandle(cls, "Payload")

    publisher.publishObjectClassAttributes(cls, {attr})
    subscriber.subscribeObjectClassAttributes(cls, {attr}, "Fast")
    obj = publisher.registerObjectInstance(cls, "Rate-RO-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.updateAttributeValues(obj, {attr: b"ro-1"}, b"tag1")
    publisher.updateAttributeValues(obj, {attr: b"ro-2"}, b"tag2")
    publisher.updateAttributeValues(obj, {attr: b"ro-3"}, b"tag3")
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][attr] for record in reflections]
    assert values == [b"ro-1", b"ro-2", b"ro-3"]

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("update-rate-ro-fed")


def test_fom_declared_transport_defaults_apply_to_attributes_and_interactions(tmp_path: Path):
    fom_path = tmp_path / "transport-update-rate-fom.xml"
    _write_transport_and_update_rate_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()
    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("transport-defaults-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "transport-defaults-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "transport-defaults-fed")

    child = publisher.getObjectClassHandle("HLAobjectRoot.Base.Child")
    payload = publisher.getAttributeHandle(child, "Payload")
    interaction = publisher.getInteractionClassHandle("HLAinteractionRoot.Ping")
    value = publisher.getParameterHandle(interaction, "Value")
    best_effort = publisher.getTransportationTypeHandle("HLAbestEffort")

    publisher.publishObjectClassAttributes(child, {payload})
    subscriber.subscribeObjectClassAttributes(child, {subscriber.getAttributeHandle(child, "Payload")})
    publisher.publishInteractionClass(interaction)
    subscriber.subscribeInteractionClass(interaction)
    obj = publisher.registerObjectInstance(child, "Transport-Default-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.updateAttributeValues(obj, {payload: b"payload"}, b"transport-default")
    publisher.sendInteraction(interaction, {value: b"ping"}, b"transport-default")
    drain(publisher, subscriber)

    reflection = sub_fed.last_callback("reflectAttributeValues")
    receive = sub_fed.last_callback("receiveInteraction")
    assert reflection is not None
    assert reflection.args[4] == best_effort
    assert receive is not None
    assert receive.args[4] == best_effort

    subscriber.queryAttributeTransportationType(obj, subscriber.getAttributeHandle(child, "Payload"))
    subscriber.queryInteractionTransportationType(interaction)
    drain(publisher, subscriber)
    report_attr = sub_fed.last_callback("reportAttributeTransportationType")
    report_interaction = sub_fed.last_callback("reportInteractionTransportationType")
    assert report_attr is not None
    assert report_attr.args == (obj, subscriber.getAttributeHandle(child, "Payload"), best_effort)
    assert report_interaction is not None
    assert report_interaction.args[1:] == (interaction, best_effort)

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("transport-defaults-fed")


def test_fom_declared_update_rate_defaults_apply_to_inherited_and_regioned_subscriptions(tmp_path: Path):
    fom_path = tmp_path / "transport-update-rate-fom.xml"
    _write_transport_and_update_rate_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()
    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution("update-rate-defaults-fed", str(fom_path))
    publisher.joinFederationExecution("pub", "type-pub", "update-rate-defaults-fed")
    subscriber.joinFederationExecution("sub", "type-sub", "update-rate-defaults-fed")

    base = subscriber.getObjectClassHandle("HLAobjectRoot.Base")
    child = publisher.getObjectClassHandle("HLAobjectRoot.Base.Child")
    base_payload = subscriber.getAttributeHandle(base, "Payload")
    child_payload = publisher.getAttributeHandle(child, "Payload")
    factory = publisher.getTimeFactory()
    dim = publisher.getDimensionHandle("HLAdefaultRoutingSpace")
    pub_region = publisher.createRegion({dim})
    sub_region = subscriber.createRegion({dim})
    publisher.setRangeBounds(pub_region, dim, RangeBounds(0, 10))
    subscriber.setRangeBounds(sub_region, dim, RangeBounds(0, 10))
    publisher.commitRegionModifications({pub_region})
    subscriber.commitRegionModifications({sub_region})

    publisher.publishObjectClassAttributes(child, {child_payload})
    subscriber.subscribeObjectClassAttributesWithRegions(
        base,
        [(AttributeHandleSet({base_payload}), {sub_region})],
    )
    publisher.enableTimeRegulation(factory.make_interval(0.1))
    subscriber.enableTimeConstrained()
    drain(publisher, subscriber)

    obj = publisher.registerObjectInstanceWithRegions(
        child,
        [(AttributeHandleSet({child_payload}), {pub_region})],
        "Update-Rate-Default-1",
    )
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.updateAttributeValues(obj, {child_payload: b"t1"}, b"tag1", factory.make_time(1.0))
    publisher.updateAttributeValues(obj, {child_payload: b"t12"}, b"tag12", factory.make_time(1.2))
    publisher.updateAttributeValues(obj, {child_payload: b"t16"}, b"tag16", factory.make_time(1.6))
    drain(publisher, subscriber)

    publisher.timeAdvanceRequest(factory.make_time(2.0))
    subscriber.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(publisher, subscriber)
    subscriber.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][base_payload] for record in reflections]
    assert values == [b"t1", b"t16"]
    assert subscriber.getUpdateRateValueForAttribute(obj, base_payload) == 2.0

    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution("update-rate-defaults-fed")


def test_attribute_relevance_combines_publication_subscription_ownership_and_scope():
    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    acquirer = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()

    owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution("attribute-relevance-fed", "TargetRadarFOMmodule.xml")
    owner.joinFederationExecution("owner", "type-owner", "attribute-relevance-fed")
    acquirer.joinFederationExecution("acquirer", "type-acquirer", "attribute-relevance-fed")
    observer.joinFederationExecution("observer", "type-observer", "attribute-relevance-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    dim = owner.getDimensionHandle("HLAdefaultRoutingSpace")

    owner_region = owner.createRegion({dim})
    acquirer_region = acquirer.createRegion({dim})
    observer_region = observer.createRegion({dim})
    owner.setRangeBounds(owner_region, dim, RangeBounds(0, 10))
    acquirer.setRangeBounds(acquirer_region, dim, RangeBounds(0, 10))
    observer.setRangeBounds(observer_region, dim, RangeBounds(0, 10))

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    pairs = [(AttributeHandleSet({attr}), {acquirer_region})]
    acquirer.subscribeObjectClassAttributesWithRegions(cls, pairs)
    observer.subscribeObjectClassAttributesWithRegions(
        cls,
        [(AttributeHandleSet({attr}), {observer_region})],
    )

    obj = owner.registerObjectInstanceWithRegions(
        cls,
        [(AttributeHandleSet({attr}), {owner_region})],
        "Relevance-1",
    )
    drain(owner, acquirer, observer)
    observer_fed.clear()
    acquirer_fed.clear()

    owner.updateAttributeValues(obj, {attr: b"owner-in-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    reflected = observer_fed.last_callback("reflectAttributeValues")
    assert reflected is not None
    assert reflected.args[1][attr] == b"owner-in-scope"

    observer.setRangeBounds(observer_region, dim, RangeBounds(90, 100))
    observer_fed.clear()
    owner.updateAttributeValues(obj, {attr: b"owner-out-of-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    assert observer_fed.last_callback("reflectAttributeValues") is None

    acquirer.attributeOwnershipAcquisition(obj, {attr}, b"relevance-acquire")
    drain(owner, acquirer, observer)
    owner.attributeOwnershipDivestitureIfWanted(obj, {attr})
    drain(owner, acquirer, observer)
    owner.setRangeBounds(owner_region, dim, RangeBounds(0, 10))
    observer.setRangeBounds(observer_region, dim, RangeBounds(0, 10))

    with pytest.raises(AttributeNotOwned):
        owner.updateAttributeValues(obj, {attr: b"stale-owner"}, b"\x00\x00\x00\x00")

    observer_fed.clear()
    acquirer.updateAttributeValues(obj, {attr: b"new-owner-in-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    reflected = observer_fed.last_callback("reflectAttributeValues")
    assert reflected is not None
    assert reflected.args[1][attr] == b"new-owner-in-scope"

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("attribute-relevance-fed")


def test_time_managed_delete_defers_remove_until_grant_and_then_clears_known_object():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("timed-delete-fed")
    factory = owner.getTimeFactory()
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    owner.enableTimeRegulation(factory.make_interval(1.0))
    observer.enableTimeConstrained()
    drain(owner, observer)

    obj = owner.registerObjectInstance(cls, "Timed-Delete-1")
    drain(owner, observer)
    assert observer.getObjectInstanceHandle("Timed-Delete-1") == obj
    observer_fed.clear()

    owner.deleteObjectInstance(obj, b"delete-tag", factory.make_time(1.0))
    drain(owner, observer)
    assert observer_fed.last_callback("removeObjectInstance") is None
    assert observer.getObjectInstanceHandle("Timed-Delete-1") == obj

    owner.timeAdvanceRequest(factory.make_time(2.0))
    observer.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(owner, observer)
    observer.nextMessageRequestAvailable(factory.make_time(2.0))
    drain(owner, observer)

    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"delete-tag"
    assert removed.args[6].producing_federate == owner.getFederateHandle("alpha")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getObjectInstanceHandle("Timed-Delete-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.getKnownObjectClassHandle(obj)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("timed-delete-fed")
