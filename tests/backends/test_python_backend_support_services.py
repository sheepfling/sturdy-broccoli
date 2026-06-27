import pytest
from pathlib import Path

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.python1516e import InMemoryRTIEngine, rti_ambassador
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.enums import OrderType, ResignAction, ServiceGroup
from hla.rti1516e.exceptions import (
    AttributeNotOwned,
    AttributeNotDefined,
    FederateInternalError,
    FederateNotExecutionMember,
    FederateHandleNotKnown,
    InvalidAttributeHandle,
    InvalidFederateHandle,
    InvalidOrderName,
    InvalidOrderType,
    InvalidParameterHandle,
    InvalidRegion,
    InvalidResignAction,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationType,
    InvalidUpdateRateDesignator,
    NameNotFound,
    NotConnected,
    ObjectInstanceNotKnown,
    InteractionParameterNotDefined,
    AttributeRelevanceAdvisorySwitchIsOn,
    AttributeRelevanceAdvisorySwitchIsOff,
    AttributeScopeAdvisorySwitchIsOn,
    AttributeScopeAdvisorySwitchIsOff,
    InteractionRelevanceAdvisorySwitchIsOn,
    InteractionRelevanceAdvisorySwitchIsOff,
    ObjectClassRelevanceAdvisorySwitchIsOn,
    ObjectClassRelevanceAdvisorySwitchIsOff,
    RegionNotCreatedByThisFederate,
    RestoreInProgress,
    SaveInProgress,
)
from hla.rti1516e.handles import (
    AttributeHandleFactory,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    AttributeHandleSet,
    DimensionHandleFactory,
    DimensionHandleSetFactory,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    MessageRetractionHandleFactory,
    ObjectClassHandleFactory,
    ObjectInstanceHandleFactory,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandleFactory,
    RegionHandle,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)
from hla.rti1516e.datatypes import RangeBounds

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


@pytest.mark.requirements(
    "HLA2025-FI-SVC-138",
    "HLA2025-FI-SVC-139",
    "HLA2025-FI-SVC-140",
    "HLA2025-FI-SVC-141",
    "HLA2025-FI-SVC-142",
    "HLA2025-FI-SVC-143",
    "HLA2025-FI-SVC-144",
    "HLA2025-FI-SVC-145",
    "HLA2025-FI-SVC-146",
    "HLA2025-FI-SVC-149",
    "HLA2025-FI-SVC-150",
    "HLA2025-FI-SVC-151",
    "HLA2025-FI-SVC-152",
    "HLA2025-FI-SVC-153",
    "HLA2025-FI-SVC-154",
    "HLA2025-FI-SVC-155",
    "HLA2025-FI-SVC-156",
)
def test_support_lookups_round_trip_class_handle_and_name():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("support-lookups-fed")
    obj_cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(obj_cls, "Position")
    inter_cls = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    param = owner.get_parameter_handle(inter_cls, "TrackId")

    owner.publish_object_class_attributes(obj_cls, {attr})
    owner.publish_interaction_class(inter_cls)
    obj = owner.register_object_instance(obj_cls, "Support-1")

    drain(owner, acquirer)

    assert owner.get_federate_name(owner.get_federate_handle("alpha")) == "alpha"
    assert acquirer.get_federate_name(acquirer.get_federate_handle("bravo")) == "bravo"
    assert owner.get_object_class_name(obj_cls) == "HLAobjectRoot.Target"
    assert owner.get_attribute_name(obj_cls, attr) == "Position"
    assert owner.get_interaction_class_name(inter_cls) == "HLAinteractionRoot.TrackReport"
    assert owner.get_parameter_name(inter_cls, param) == "TrackId"
    assert owner.get_object_instance_name(obj) == "Support-1"
    assert owner.get_known_object_class_handle(obj) == obj_cls
    assert owner.get_object_instance_handle("Support-1") == obj
    assert owner.get_transportation_type_name(owner.get_transportation_type_handle("HLAreliable")) == "HLAreliable"
    assert owner.get_transportation_name(owner.get_transportation_type("HLAreliable")) == "HLAreliable"
    assert owner.get_transportation_type_name(owner.get_transportation_type_handle("HLAbestEffort")) == "HLAbestEffort"
    assert owner.get_transportation_name(owner.get_transportation_type("HLAbestEffort")) == "HLAbestEffort"
    assert owner.get_order_name(OrderType.RECEIVE) == "RECEIVE"
    assert owner.get_order_type("HLAtimestamp") is OrderType.TIMESTAMP

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-lookups-fed")


@pytest.mark.requirements(
    "HLA2025-FI-SVC-147",
    "HLA2025-FI-SVC-148",
    "HLA2025-FI-SVC-158",
    "HLA2025-FI-SVC-159",
    "HLA2025-FI-SVC-160",
    "HLA2025-FI-SVC-161",
)
def test_support_dimension_and_update_rate_helpers():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-dim-fed")
    obj_cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(obj_cls, "Position")
    inter_cls = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    class_dims = owner.get_available_dimensions_for_class_attribute(obj_cls, attr)
    interaction_dims = owner.get_available_dimensions_for_interaction_class(inter_cls)
    assert class_dims
    assert interaction_dims

    dim = next(iter(class_dims))
    assert owner.get_dimension_handle(owner.get_dimension_name(dim)) == dim
    assert owner.get_update_rate_value("default") == 0.0
    assert owner.get_update_rate_value_for_attribute(owner.register_object_instance(obj_cls, "Support-2"), attr) == 0.0

    owner.set_automatic_resign_directive(ResignAction.DELETE_OBJECTS)
    assert owner.get_automatic_resign_directive() is ResignAction.DELETE_OBJECTS
    owner.set_automatic_resign_directive(ResignAction.NO_ACTION)
    assert owner.get_automatic_resign_directive() is ResignAction.NO_ACTION

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-dim-fed")


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
    owner.create_federation_execution("support-update-rate-fed", fom_path)
    owner.join_federation_execution("alpha", "type-a", "support-update-rate-fed")
    observer.join_federation_execution("bravo", "type-b", "support-update-rate-fed")

    obj_cls = owner.get_object_class_handle("HLAobjectRoot.RateObject")
    attr = owner.get_attribute_handle(obj_cls, "Payload")
    owner.publish_object_class_attributes(obj_cls, {attr})
    observer.subscribe_object_class_attributes(obj_cls, {attr}, "Fast")
    obj = owner.register_object_instance(obj_cls, "Rate-1")

    drain(owner, observer)

    assert observer.get_update_rate_value("Fast") == 2.0
    assert observer.get_update_rate_value_for_attribute(obj, attr) == 2.0
    assert owner.get_update_rate_value_for_attribute(obj, attr) == 0.0

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-update-rate-fed")


def test_support_normalizers_and_factories():
    _, owner, acquirer, _owner_fed, _acquirer_fed, h1, _h2 = joined_pair("support-normalize-fed")

    assert owner.normalize_federate_handle(h1) == h1
    assert owner.normalize_service_group(ServiceGroup.OBJECT_MANAGEMENT) is ServiceGroup.OBJECT_MANAGEMENT
    assert owner.normalize_service_group("object-management") is ServiceGroup.OBJECT_MANAGEMENT

    assert isinstance(owner.get_attribute_handle_factory(), AttributeHandleFactory)
    assert isinstance(owner.get_attribute_handle_set_factory(), AttributeHandleSetFactory)
    assert isinstance(owner.get_attribute_handle_value_map_factory(), AttributeHandleValueMapFactory)
    assert isinstance(owner.get_attribute_set_region_set_pair_list_factory(), AttributeSetRegionSetPairListFactory)
    assert isinstance(owner.get_dimension_handle_factory(), DimensionHandleFactory)
    assert isinstance(owner.get_dimension_handle_set_factory(), DimensionHandleSetFactory)
    assert isinstance(owner.get_federate_handle_factory(), FederateHandleFactory)
    assert isinstance(owner.get_federate_handle_set_factory(), FederateHandleSetFactory)
    assert isinstance(owner.get_interaction_class_handle_factory(), InteractionClassHandleFactory)
    assert isinstance(owner.get_object_class_handle_factory(), ObjectClassHandleFactory)
    assert isinstance(owner.get_object_instance_handle_factory(), ObjectInstanceHandleFactory)
    assert isinstance(owner.get_parameter_handle_factory(), ParameterHandleFactory)
    assert isinstance(owner.get_parameter_handle_value_map_factory(), ParameterHandleValueMapFactory)
    assert isinstance(owner.get_region_handle_set_factory(), RegionHandleSetFactory)
    assert isinstance(owner.get_transportation_type_handle_factory(), TransportationTypeHandleFactory)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-normalize-fed")


@pytest.mark.requirements(
    "REQ-RTI-SS-10_44-getRegionHandleFactory",
    "REQ-RTI-SS-10_44-getMessageRetractionHandleFactory",
)
def test_support_handle_factory_rows_have_direct_runtime_witnesses():
    rti = rti_ambassador(engine=InMemoryRTIEngine())

    with pytest.raises(NotConnected):
        rti.get_region_handle_factory()
    with pytest.raises(NotConnected):
        rti.get_message_retraction_handle_factory()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-handle-factory-fed")

    assert isinstance(owner.get_region_handle_factory(), RegionHandleFactory)
    assert isinstance(owner.get_message_retraction_handle_factory(), MessageRetractionHandleFactory)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-handle-factory-fed")


def test_support_invalid_inputs_raise_expected_errors():
    _, owner, acquirer, _owner_fed, _acquirer_fed, h1, _h2 = joined_pair("support-invalid-fed")
    obj_cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(obj_cls, "Position")
    inter_cls = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    param = owner.get_parameter_handle(inter_cls, "TrackId")

    with pytest.raises(FederateHandleNotKnown):
        owner.get_federate_name(type(h1)(h1.value + 1000))
    with pytest.raises(InvalidFederateHandle):
        owner.normalize_federate_handle(type(h1)(h1.value + 1000))
    with pytest.raises(AttributeNotDefined):
        owner.get_attribute_name(obj_cls, type(attr)(999999))
    with pytest.raises(AttributeNotDefined):
        owner.get_available_dimensions_for_class_attribute(obj_cls, type(attr)(999999))
    with pytest.raises(InteractionParameterNotDefined):
        owner.get_parameter_name(inter_cls, type(param)(999999))
    with pytest.raises(InvalidServiceGroup):
        owner.normalize_service_group("not-a-service-group")
    with pytest.raises(InvalidOrderName):
        owner.get_order_type("not-an-order")
    with pytest.raises(InvalidOrderType):
        owner.get_order_name("receive")  # type: ignore[arg-type]
    with pytest.raises(InvalidTransportationName):
        owner.get_transportation_type_handle("HLAimaginaryTransport")
    with pytest.raises(InvalidTransportationType):
        owner.get_transportation_type_name(type(owner.get_transportation_type_handle("HLAreliable"))(999999))
    with pytest.raises(InvalidUpdateRateDesignator):
        owner.get_update_rate_value("fast")
    with pytest.raises(NameNotFound):
        owner.get_federate_handle("missing")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-invalid-fed")


def test_support_advisory_switches_toggle_and_reject_duplicates():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-switch-fed")

    owner.enable_object_class_relevance_advisory_switch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOn):
        owner.enable_object_class_relevance_advisory_switch()
    owner.disable_object_class_relevance_advisory_switch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOff):
        owner.disable_object_class_relevance_advisory_switch()

    owner.enable_attribute_relevance_advisory_switch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOn):
        owner.enable_attribute_relevance_advisory_switch()
    owner.disable_attribute_relevance_advisory_switch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOff):
        owner.disable_attribute_relevance_advisory_switch()

    owner.enable_attribute_scope_advisory_switch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOn):
        owner.enable_attribute_scope_advisory_switch()
    owner.disable_attribute_scope_advisory_switch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOff):
        owner.disable_attribute_scope_advisory_switch()

    owner.enable_interaction_relevance_advisory_switch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOn):
        owner.enable_interaction_relevance_advisory_switch()
    owner.disable_interaction_relevance_advisory_switch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOff):
        owner.disable_interaction_relevance_advisory_switch()

    owner.enable_callbacks()
    owner.disable_callbacks()

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-switch-fed")


def test_support_dimension_handle_set_and_advisory_switches_cover_runtime_guards():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    unjoined_calls = (
        lambda: rti.get_dimension_handle_set(RegionHandle(999999)),
        lambda: rti.enable_object_class_relevance_advisory_switch(),
        lambda: rti.disable_object_class_relevance_advisory_switch(),
        lambda: rti.enable_attribute_relevance_advisory_switch(),
        lambda: rti.disable_attribute_relevance_advisory_switch(),
        lambda: rti.enable_attribute_scope_advisory_switch(),
        lambda: rti.disable_attribute_scope_advisory_switch(),
    )

    for call in unjoined_calls:
        with pytest.raises(NotConnected):
            call()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    for call in unjoined_calls:
        with pytest.raises(FederateNotExecutionMember):
            call()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("support-dimension-switch-guards-fed")
    dim = owner.get_dimension_handle("HLAdefaultRoutingSpace")
    region = owner.create_region({dim})
    invalid_region = type(region)(region.value + 1000)

    with pytest.raises(InvalidRegion):
        owner.get_dimension_handle_set(invalid_region)

    owner.enable_object_class_relevance_advisory_switch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOn):
        owner.enable_object_class_relevance_advisory_switch()
    owner.disable_object_class_relevance_advisory_switch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOff):
        owner.disable_object_class_relevance_advisory_switch()

    owner.enable_attribute_relevance_advisory_switch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOn):
        owner.enable_attribute_relevance_advisory_switch()
    owner.disable_attribute_relevance_advisory_switch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOff):
        owner.disable_attribute_relevance_advisory_switch()

    owner.enable_attribute_scope_advisory_switch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOn):
        owner.enable_attribute_scope_advisory_switch()
    owner.disable_attribute_scope_advisory_switch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOff):
        owner.disable_attribute_scope_advisory_switch()

    guarded_calls = (
        lambda: owner.get_dimension_handle_set(region),
        lambda: owner.enable_object_class_relevance_advisory_switch(),
        lambda: owner.disable_object_class_relevance_advisory_switch(),
        lambda: owner.enable_attribute_relevance_advisory_switch(),
        lambda: owner.disable_attribute_relevance_advisory_switch(),
        lambda: owner.enable_attribute_scope_advisory_switch(),
        lambda: owner.disable_attribute_scope_advisory_switch(),
    )

    owner.request_federation_save("SUPPORT-DIMENSION-SWITCH-GUARDS")
    drain(owner, observer)
    for call in guarded_calls:
        with pytest.raises(SaveInProgress):
            call()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("SUPPORT-DIMENSION-SWITCH-GUARDS")
    drain(owner, observer)
    for call in guarded_calls:
        with pytest.raises(RestoreInProgress):
            call()

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-dimension-switch-guards-fed")


def test_support_interaction_dimension_lookup_requires_active_membership():
    rti = rti_ambassador(engine=InMemoryRTIEngine())

    with pytest.raises(NotConnected):
        rti.get_available_dimensions_for_interaction_class(InteractionClassHandle(999999))

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.get_available_dimensions_for_interaction_class(InteractionClassHandle(999999))
    rti.disconnect()


def test_support_set_range_bounds_rejects_foreign_region_owner():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-foreign-region-fed")
    owner_dim = owner.get_dimension_handle("HLAdefaultRoutingSpace")
    acquirer_dim = acquirer.get_dimension_handle("HLAdefaultRoutingSpace")
    owner_region = owner.create_region({owner_dim})

    with pytest.raises(RegionNotCreatedByThisFederate):
        acquirer.set_range_bounds(owner_region, acquirer_dim, RangeBounds(0, 10))

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-foreign-region-fed")


def test_support_runtime_service_inquiries_and_factories_require_active_membership():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-runtime-membership-fed")

    calls = (
        lambda: owner.get_automatic_resign_directive(),
        lambda: owner.get_attribute_handle_factory(),
        lambda: owner.get_attribute_handle_set_factory(),
        lambda: owner.get_attribute_handle_value_map_factory(),
        lambda: owner.get_attribute_set_region_set_pair_list_factory(),
        lambda: owner.get_dimension_handle_factory(),
        lambda: owner.get_dimension_handle_set_factory(),
        lambda: owner.get_federate_handle_factory(),
        lambda: owner.get_federate_handle_set_factory(),
        lambda: owner.get_interaction_class_handle_factory(),
        lambda: owner.get_object_class_handle_factory(),
        lambda: owner.get_object_instance_handle_factory(),
        lambda: owner.get_parameter_handle_factory(),
        lambda: owner.get_parameter_handle_value_map_factory(),
        lambda: owner.get_region_handle_set_factory(),
        lambda: owner.get_time_factory(),
        lambda: owner.get_transportation_type_handle_factory(),
    )

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    for call in calls:
        with pytest.raises(FederateNotExecutionMember):
            call()

    owner.disconnect()
    for call in calls:
        with pytest.raises(NotConnected):
            call()

    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.destroy_federation_execution("support-runtime-membership-fed")


def test_support_lookup_runtime_negatives_cover_invalid_not_member_and_not_connected():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("support-runtime-negative-fed")
    obj_cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(obj_cls, "Position")
    obj = owner.register_object_instance(obj_cls, "Support-Negative-1")
    reliable = owner.get_transportation_type_handle("HLAreliable")

    with pytest.raises(InvalidUpdateRateDesignator):
        owner.get_update_rate_value("fast")
    with pytest.raises(AttributeNotDefined):
        owner.get_update_rate_value_for_attribute(obj, type(attr)(999999))
    with pytest.raises(ObjectInstanceNotKnown):
        owner.get_update_rate_value_for_attribute(type(obj)(999999), attr)
    with pytest.raises(InvalidTransportationName):
        owner.get_transportation_type("HLAimaginaryTransport")
    with pytest.raises(InvalidTransportationType):
        owner.get_transportation_type_name(type(reliable)(999999))
    with pytest.raises(InvalidResignAction):
        owner.set_automatic_resign_directive("bogus")  # type: ignore[arg-type]
    with pytest.raises(InvalidServiceGroup):
        owner.normalize_service_group("not-a-service-group")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    with pytest.raises(FederateNotExecutionMember):
        owner.get_update_rate_value("default")
    with pytest.raises(FederateNotExecutionMember):
        owner.get_update_rate_value_for_attribute(obj, attr)
    with pytest.raises(FederateNotExecutionMember):
        owner.get_transportation_type("HLAreliable")
    with pytest.raises(FederateNotExecutionMember):
        owner.get_transportation_type_handle("HLAreliable")
    with pytest.raises(FederateNotExecutionMember):
        owner.get_transportation_name(reliable)
    with pytest.raises(FederateNotExecutionMember):
        owner.get_transportation_type_name(reliable)
    with pytest.raises(FederateNotExecutionMember):
        owner.get_automatic_resign_directive()
    with pytest.raises(FederateNotExecutionMember):
        owner.set_automatic_resign_directive(ResignAction.NO_ACTION)
    with pytest.raises(FederateNotExecutionMember):
        owner.normalize_service_group(ServiceGroup.OBJECT_MANAGEMENT)

    owner.disconnect()
    with pytest.raises(NotConnected):
        owner.get_update_rate_value("default")
    with pytest.raises(NotConnected):
        owner.get_update_rate_value_for_attribute(obj, attr)
    with pytest.raises(NotConnected):
        owner.get_transportation_type("HLAreliable")
    with pytest.raises(NotConnected):
        owner.get_transportation_type_handle("HLAreliable")
    with pytest.raises(NotConnected):
        owner.get_transportation_name(reliable)
    with pytest.raises(NotConnected):
        owner.get_transportation_type_name(reliable)
    with pytest.raises(NotConnected):
        owner.get_automatic_resign_directive()
    with pytest.raises(NotConnected):
        owner.set_automatic_resign_directive(ResignAction.NO_ACTION)
    with pytest.raises(NotConnected):
        owner.normalize_service_group(ServiceGroup.OBJECT_MANAGEMENT)

    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.destroy_federation_execution("support-runtime-negative-fed")


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
    publisher.create_federation_execution("hierarchy-discovery-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "hierarchy-discovery-fed")
    subscriber.join_federation_execution("sub", "type-sub", "hierarchy-discovery-fed")

    base = subscriber.get_object_class_handle("HLAobjectRoot.Base")
    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    payload = subscriber.get_attribute_handle(base, "Payload")

    subscriber.subscribe_object_class_attributes(base, {payload})
    publisher.publish_object_class_attributes(child, {publisher.get_attribute_handle(child, "Payload")})
    obj = publisher.register_object_instance(child, "Hierarchy-1")
    drain(publisher, subscriber)

    discovery = sub_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    assert discovery.args[1] == base
    assert subscriber.get_known_object_class_handle(obj) == base

    publisher.update_attribute_values(obj, {publisher.get_attribute_handle(child, "Payload"): b"first"}, b"tag")
    drain(publisher, subscriber)
    assert subscriber.get_known_object_class_handle(obj) == base

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("hierarchy-discovery-fed")


def test_discovery_callback_validates_payload_context_and_wraps_callback_failures(tmp_path: Path):
    fom_path = tmp_path / "hierarchy-discovery-contract-fom.xml"
    _write_hierarchy_fom(fom_path)

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    pub_fed = RecordingFederateAmbassador()
    sub_fed = RecordingFederateAmbassador()

    publisher.connect(pub_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(sub_fed, CallbackModel.HLA_EVOKED)
    publisher.create_federation_execution("hierarchy-discovery-contract-fed", str(fom_path))
    pub_handle = publisher.join_federation_execution("pub", "type-pub", "hierarchy-discovery-contract-fed")
    subscriber.join_federation_execution("sub", "type-sub", "hierarchy-discovery-contract-fed")

    base = subscriber.get_object_class_handle("HLAobjectRoot.Base")
    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    payload = subscriber.get_attribute_handle(base, "Payload")

    subscriber.subscribe_object_class_attributes(base, {payload})
    publisher.publish_object_class_attributes(child, {publisher.get_attribute_handle(child, "Payload")})
    obj = publisher.register_object_instance(child, "Hierarchy-Contract-1")
    drain(publisher, subscriber)

    discovery = sub_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args == (obj, base, "Hierarchy-Contract-1", pub_handle)
    assert pub_fed.callbacks_named("discoverObjectInstance") == []
    assert subscriber.get_known_object_class_handle(obj) == base

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("hierarchy-discovery-contract-fed")

    class _FailingDiscoveryAmbassador(RecordingFederateAmbassador):
        def on_discover_object_instance(self, *args, **kwargs):
            raise RuntimeError("discover-object-instance-failed")

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    publisher.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    subscriber.connect(_FailingDiscoveryAmbassador(), CallbackModel.HLA_IMMEDIATE)
    publisher.create_federation_execution("hierarchy-discovery-failing-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "hierarchy-discovery-failing-fed")
    subscriber.join_federation_execution("sub", "type-sub", "hierarchy-discovery-failing-fed")

    base = subscriber.get_object_class_handle("HLAobjectRoot.Base")
    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    payload = subscriber.get_attribute_handle(base, "Payload")

    subscriber.subscribe_object_class_attributes(base, {payload})
    publisher.publish_object_class_attributes(child, {publisher.get_attribute_handle(child, "Payload")})

    with pytest.raises(FederateInternalError):
        publisher.register_object_instance(child, "Hierarchy-Failing-1")

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("hierarchy-discovery-failing-fed")


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
    publisher.create_federation_execution("hierarchy-reflect-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "hierarchy-reflect-fed")
    subscriber.join_federation_execution("sub", "type-sub", "hierarchy-reflect-fed")

    base = subscriber.get_object_class_handle("HLAobjectRoot.Base")
    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    base_payload = subscriber.get_attribute_handle(base, "Payload")
    child_payload = publisher.get_attribute_handle(child, "Payload")

    subscriber.subscribe_object_class_attributes(base, {base_payload})
    publisher.publish_object_class_attributes(child, {child_payload})
    obj = publisher.register_object_instance(child, "Hierarchy-Reflect-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.update_attribute_values(obj, {child_payload: b"payload"}, b"tag")
    drain(publisher, subscriber)

    reflection = sub_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {base_payload: b"payload"}
    assert subscriber.get_known_object_class_handle(obj) == base

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("hierarchy-reflect-fed")


def test_local_delete_clears_only_local_knowledge_and_object_can_be_rediscovered():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("local-delete-knowledge-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Local-Delete-1")
    drain(owner, observer)
    assert observer.get_object_instance_handle("Local-Delete-1") == obj

    observer.local_delete_object_instance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Local-Delete-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_known_object_class_handle(obj)

    owner.update_attribute_values(obj, {attr: b"rediscover"}, b"\x00\x00\x00\x00")
    drain(owner, observer)

    discovery = observer_fed.last_callback("discoverObjectInstance")
    reflection = observer_fed.last_callback("reflectAttributeValues")
    assert discovery is not None
    assert reflection is not None
    assert observer.get_object_instance_handle("Local-Delete-1") == obj
    assert observer.get_known_object_class_handle(obj) == cls

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("local-delete-knowledge-fed")


def test_orphan_object_remains_discovered_until_local_delete_clears_only_local_knowledge():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("orphan-object-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Orphan-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.unconditional_attribute_ownership_divestiture(obj, {attr})
    assert owner.is_attribute_owned_by_federate(obj, attr) is False
    assert observer.get_object_instance_handle("Orphan-1") == obj
    assert observer.get_known_object_class_handle(obj) == cls

    observer.local_delete_object_instance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Orphan-1")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("orphan-object-fed")


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
    owner.create_federation_execution("orphan-lifecycle-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("owner", "type-owner", "orphan-lifecycle-fed")
    observer.join_federation_execution("observer", "type-observer", "orphan-lifecycle-fed")

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Orphan-Lifecycle-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.unconditional_attribute_ownership_divestiture(obj, {attr})
    assert owner.is_attribute_owned_by_federate(obj, attr) is False
    assert observer.get_object_instance_handle("Orphan-Lifecycle-1") == obj

    late.join_federation_execution("late", "type-late", "orphan-lifecycle-fed")
    late.subscribe_object_class_attributes(cls, {attr})
    drain(owner, observer, late)

    late_discovery = late_fed.last_callback("discoverObjectInstance")
    assert late_discovery is not None
    assert late_discovery.args[0] == obj
    assert late.get_object_instance_handle("Orphan-Lifecycle-1") == obj
    assert late.get_known_object_class_handle(obj) == cls

    observer.local_delete_object_instance(obj)
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Orphan-Lifecycle-1")

    owner.delete_object_instance(obj, b"orphan-delete")
    drain(owner, observer, late)

    assert observer_fed.last_callback("removeObjectInstance") is None
    removed = late_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"orphan-delete"
    with pytest.raises(ObjectInstanceNotKnown):
        late.get_object_instance_handle("Orphan-Lifecycle-1")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    late.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("orphan-lifecycle-fed")


def test_delete_object_instance_notifies_known_federates_with_remove_object_instance():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("remove-object-callback-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Remove-1")
    drain(owner, observer)
    assert observer.get_object_instance_handle("Remove-1") == obj
    observer_fed.clear()

    owner.delete_object_instance(obj, b"delete-tag")
    drain(owner, observer)

    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"delete-tag"
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Remove-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_known_object_class_handle(obj)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("remove-object-callback-fed")


def test_remove_object_instance_callback_validates_payload_context_and_wraps_callback_failures():
    _, owner, observer, owner_fed, observer_fed, owner_handle, _observer_handle = joined_pair(
        "remove-object-contract-fed"
    )
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Remove-Contract-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.delete_object_instance(obj, b"remove-contract-tag")
    drain(owner, observer)

    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"remove-contract-tag"
    assert removed.args[2] == OrderType.RECEIVE
    info = removed.args[3]
    assert getattr(info, "producing_federate") == owner_handle
    assert owner_fed.callbacks_named("removeObjectInstance") == []
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Remove-Contract-1")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("remove-object-contract-fed")

    class _FailingRemoveAmbassador(RecordingFederateAmbassador):
        def on_remove_object_instance(self, *args, **kwargs):
            raise RuntimeError("remove-object-instance-failed")

    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(_FailingRemoveAmbassador(), CallbackModel.HLA_IMMEDIATE)
    owner.create_federation_execution("remove-object-failing-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("owner", "type-owner", "remove-object-failing-fed")
    observer.join_federation_execution("observer", "type-observer", "remove-object-failing-fed")

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Remove-Failing-1")
    drain(owner, observer)

    with pytest.raises(FederateInternalError):
        owner.delete_object_instance(obj, b"remove-failing-tag")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("remove-object-failing-fed")


def test_receive_interaction_callback_validates_payload_context_and_wraps_callback_failures():
    _, owner, observer, owner_fed, observer_fed, owner_handle, _observer_handle = joined_pair(
        "receive-interaction-contract-fed"
    )
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    parameter = owner.get_parameter_handle(interaction, "TrackId")
    reliable = owner.backend.engine.transportation_reliable

    owner.publish_interaction_class(interaction)
    observer.subscribe_interaction_class(interaction)
    observer_fed.clear()

    owner.send_interaction(interaction, {parameter: b"ri-contract"}, b"ri-tag")
    drain(owner, observer)

    received = observer_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1] == {parameter: b"ri-contract"}
    assert received.args[2] == b"ri-tag"
    assert received.args[3] == OrderType.RECEIVE
    assert received.args[4] == reliable
    info = received.args[5]
    assert getattr(info, "producing_federate") == owner_handle
    assert owner_fed.callbacks_named("receiveInteraction") == []

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("receive-interaction-contract-fed")

    class _FailingReceiveInteractionAmbassador(RecordingFederateAmbassador):
        def on_receive_interaction(self, *args, **kwargs):
            raise RuntimeError("receive-interaction-failed")

    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(_FailingReceiveInteractionAmbassador(), CallbackModel.HLA_IMMEDIATE)
    owner.create_federation_execution("receive-interaction-failing-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("owner", "type-owner", "receive-interaction-failing-fed")
    observer.join_federation_execution("observer", "type-observer", "receive-interaction-failing-fed")

    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    parameter = owner.get_parameter_handle(interaction, "TrackId")
    owner.publish_interaction_class(interaction)
    observer.subscribe_interaction_class(interaction)

    with pytest.raises(FederateInternalError):
        owner.send_interaction(interaction, {parameter: b"ri-failing"}, b"ri-tag")

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("receive-interaction-failing-fed")


def test_reflect_attribute_values_callback_validates_payload_context_and_wraps_callback_failures():
    _, owner, observer, owner_fed, observer_fed, owner_handle, _observer_handle = joined_pair(
        "reflect-attributes-contract-fed"
    )
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    reliable = owner.backend.engine.transportation_reliable

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Reflect-Contract-1")
    drain(owner, observer)
    observer_fed.clear()

    owner.update_attribute_values(obj, {attr: b"reflect-contract"}, b"reflect-tag")
    drain(owner, observer)

    reflected = observer_fed.last_callback("reflectAttributeValues")
    assert reflected is not None
    assert reflected.args[0] == obj
    assert reflected.args[1] == {attr: b"reflect-contract"}
    assert reflected.args[2] == b"reflect-tag"
    assert reflected.args[3] == OrderType.RECEIVE
    assert reflected.args[4] == reliable
    info = reflected.args[5]
    assert getattr(info, "producing_federate") == owner_handle
    assert getattr(info, "sent_regions") == frozenset()
    assert owner_fed.callbacks_named("reflectAttributeValues") == []

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("reflect-attributes-contract-fed")

    class _FailingReflectAmbassador(RecordingFederateAmbassador):
        def on_reflect_attribute_values(self, *args, **kwargs):
            raise RuntimeError("reflect-attributes-failed")

    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(_FailingReflectAmbassador(), CallbackModel.HLA_IMMEDIATE)
    owner.create_federation_execution("reflect-attributes-failing-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("owner", "type-owner", "reflect-attributes-failing-fed")
    observer.join_federation_execution("observer", "type-observer", "reflect-attributes-failing-fed")

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Reflect-Failing-1")
    drain(owner, observer)

    with pytest.raises(FederateInternalError):
        owner.update_attribute_values(obj, {attr: b"reflect-failing"}, b"reflect-tag")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("reflect-attributes-failing-fed")


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
    publisher.create_federation_execution("update-rate-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "update-rate-fed")
    subscriber.join_federation_execution("sub", "type-sub", "update-rate-fed")

    cls = publisher.get_object_class_handle("HLAobjectRoot.RateObject")
    attr = publisher.get_attribute_handle(cls, "Payload")
    factory = publisher.get_time_factory()

    publisher.publish_object_class_attributes(cls, {attr})
    subscriber.subscribe_object_class_attributes(cls, {attr}, "Fast")
    publisher.enable_time_regulation(factory.make_interval(0.1))
    subscriber.enable_time_constrained()
    drain(publisher, subscriber)

    obj = publisher.register_object_instance(cls, "Rate-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.update_attribute_values(obj, {attr: b"t1"}, b"tag1", factory.make_time(1.0))
    publisher.update_attribute_values(obj, {attr: b"t12"}, b"tag12", factory.make_time(1.2))
    publisher.update_attribute_values(obj, {attr: b"t16"}, b"tag16", factory.make_time(1.6))
    drain(publisher, subscriber)

    publisher.time_advance_request(factory.make_time(2.0))
    subscriber.next_message_request_available(factory.make_time(2.0))
    drain(publisher, subscriber)
    subscriber.next_message_request_available(factory.make_time(2.0))
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][attr] for record in reflections]
    assert values == [b"t1", b"t16"]
    assert subscriber.get_update_rate_value("Fast") == 2.0

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("update-rate-fed")


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
    publisher.create_federation_execution("update-rate-ro-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "update-rate-ro-fed")
    subscriber.join_federation_execution("sub", "type-sub", "update-rate-ro-fed")

    cls = publisher.get_object_class_handle("HLAobjectRoot.RateObject")
    attr = publisher.get_attribute_handle(cls, "Payload")

    publisher.publish_object_class_attributes(cls, {attr})
    subscriber.subscribe_object_class_attributes(cls, {attr}, "Fast")
    obj = publisher.register_object_instance(cls, "Rate-RO-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.update_attribute_values(obj, {attr: b"ro-1"}, b"tag1")
    publisher.update_attribute_values(obj, {attr: b"ro-2"}, b"tag2")
    publisher.update_attribute_values(obj, {attr: b"ro-3"}, b"tag3")
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][attr] for record in reflections]
    assert values == [b"ro-1", b"ro-2", b"ro-3"]

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("update-rate-ro-fed")


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
    publisher.create_federation_execution("transport-defaults-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "transport-defaults-fed")
    subscriber.join_federation_execution("sub", "type-sub", "transport-defaults-fed")

    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    payload = publisher.get_attribute_handle(child, "Payload")
    interaction = publisher.get_interaction_class_handle("HLAinteractionRoot.Ping")
    value = publisher.get_parameter_handle(interaction, "Value")
    best_effort = publisher.get_transportation_type_handle("HLAbestEffort")

    publisher.publish_object_class_attributes(child, {payload})
    subscriber.subscribe_object_class_attributes(child, {subscriber.get_attribute_handle(child, "Payload")})
    publisher.publish_interaction_class(interaction)
    subscriber.subscribe_interaction_class(interaction)
    obj = publisher.register_object_instance(child, "Transport-Default-1")
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.update_attribute_values(obj, {payload: b"payload"}, b"transport-default")
    publisher.send_interaction(interaction, {value: b"ping"}, b"transport-default")
    drain(publisher, subscriber)

    reflection = sub_fed.last_callback("reflectAttributeValues")
    receive = sub_fed.last_callback("receiveInteraction")
    assert reflection is not None
    assert reflection.args[4] == best_effort
    assert receive is not None
    assert receive.args[4] == best_effort

    subscriber.query_attribute_transportation_type(obj, subscriber.get_attribute_handle(child, "Payload"))
    subscriber.query_interaction_transportation_type(interaction)
    drain(publisher, subscriber)
    report_attr = sub_fed.last_callback("reportAttributeTransportationType")
    report_interaction = sub_fed.last_callback("reportInteractionTransportationType")
    assert report_attr is not None
    assert report_attr.args == (obj, subscriber.get_attribute_handle(child, "Payload"), best_effort)
    assert report_interaction is not None
    assert report_interaction.args[1:] == (interaction, best_effort)

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("transport-defaults-fed")


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
    publisher.create_federation_execution("update-rate-defaults-fed", str(fom_path))
    publisher.join_federation_execution("pub", "type-pub", "update-rate-defaults-fed")
    subscriber.join_federation_execution("sub", "type-sub", "update-rate-defaults-fed")

    base = subscriber.get_object_class_handle("HLAobjectRoot.Base")
    child = publisher.get_object_class_handle("HLAobjectRoot.Base.Child")
    base_payload = subscriber.get_attribute_handle(base, "Payload")
    child_payload = publisher.get_attribute_handle(child, "Payload")
    factory = publisher.get_time_factory()
    dim = publisher.get_dimension_handle("HLAdefaultRoutingSpace")
    pub_region = publisher.create_region({dim})
    sub_region = subscriber.create_region({dim})
    publisher.set_range_bounds(pub_region, dim, RangeBounds(0, 10))
    subscriber.set_range_bounds(sub_region, dim, RangeBounds(0, 10))
    publisher.commit_region_modifications({pub_region})
    subscriber.commit_region_modifications({sub_region})

    publisher.publish_object_class_attributes(child, {child_payload})
    subscriber.subscribe_object_class_attributes_with_regions(
        base,
        [(AttributeHandleSet({base_payload}), {sub_region})],
    )
    publisher.enable_time_regulation(factory.make_interval(0.1))
    subscriber.enable_time_constrained()
    drain(publisher, subscriber)

    obj = publisher.register_object_instance_with_regions(
        child,
        [(AttributeHandleSet({child_payload}), {pub_region})],
        "Update-Rate-Default-1",
    )
    drain(publisher, subscriber)
    sub_fed.clear()

    publisher.update_attribute_values(obj, {child_payload: b"t1"}, b"tag1", factory.make_time(1.0))
    publisher.update_attribute_values(obj, {child_payload: b"t12"}, b"tag12", factory.make_time(1.2))
    publisher.update_attribute_values(obj, {child_payload: b"t16"}, b"tag16", factory.make_time(1.6))
    drain(publisher, subscriber)

    publisher.time_advance_request(factory.make_time(2.0))
    subscriber.next_message_request_available(factory.make_time(2.0))
    drain(publisher, subscriber)
    subscriber.next_message_request_available(factory.make_time(2.0))
    drain(publisher, subscriber)

    reflections = sub_fed.callbacks_named("reflectAttributeValues")
    values = [record.args[1][base_payload] for record in reflections]
    assert values == [b"t1", b"t16"]
    assert subscriber.get_update_rate_value_for_attribute(obj, base_payload) == 2.0

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution("update-rate-defaults-fed")


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
    owner.create_federation_execution("attribute-relevance-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("owner", "type-owner", "attribute-relevance-fed")
    acquirer.join_federation_execution("acquirer", "type-acquirer", "attribute-relevance-fed")
    observer.join_federation_execution("observer", "type-observer", "attribute-relevance-fed")

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    dim = owner.get_dimension_handle("HLAdefaultRoutingSpace")

    owner_region = owner.create_region({dim})
    acquirer_region = acquirer.create_region({dim})
    observer_region = observer.create_region({dim})
    owner.set_range_bounds(owner_region, dim, RangeBounds(0, 10))
    acquirer.set_range_bounds(acquirer_region, dim, RangeBounds(0, 10))
    observer.set_range_bounds(observer_region, dim, RangeBounds(0, 10))

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    pairs = [(AttributeHandleSet({attr}), {acquirer_region})]
    acquirer.subscribe_object_class_attributes_with_regions(cls, pairs)
    observer.subscribe_object_class_attributes_with_regions(
        cls,
        [(AttributeHandleSet({attr}), {observer_region})],
    )

    obj = owner.register_object_instance_with_regions(
        cls,
        [(AttributeHandleSet({attr}), {owner_region})],
        "Relevance-1",
    )
    drain(owner, acquirer, observer)
    observer_fed.clear()
    acquirer_fed.clear()

    owner.update_attribute_values(obj, {attr: b"owner-in-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    reflected = observer_fed.last_callback("reflectAttributeValues")
    assert reflected is not None
    assert reflected.args[1][attr] == b"owner-in-scope"

    observer.set_range_bounds(observer_region, dim, RangeBounds(90, 100))
    observer_fed.clear()
    owner.update_attribute_values(obj, {attr: b"owner-out-of-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    assert observer_fed.last_callback("reflectAttributeValues") is None

    acquirer.attribute_ownership_acquisition(obj, {attr}, b"relevance-acquire")
    drain(owner, acquirer, observer)
    owner.attribute_ownership_divestiture_if_wanted(obj, {attr})
    drain(owner, acquirer, observer)
    owner.set_range_bounds(owner_region, dim, RangeBounds(0, 10))
    observer.set_range_bounds(observer_region, dim, RangeBounds(0, 10))

    with pytest.raises(AttributeNotOwned):
        owner.update_attribute_values(obj, {attr: b"stale-owner"}, b"\x00\x00\x00\x00")

    observer_fed.clear()
    acquirer.update_attribute_values(obj, {attr: b"new-owner-in-scope"}, b"\x00\x00\x00\x00")
    drain(owner, acquirer, observer)
    reflected = observer_fed.last_callback("reflectAttributeValues")
    assert reflected is not None
    assert reflected.args[1][attr] == b"new-owner-in-scope"

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("attribute-relevance-fed")


def test_time_managed_delete_defers_remove_until_grant_and_then_clears_known_object():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("timed-delete-fed")
    factory = owner.get_time_factory()
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})
    owner.enable_time_regulation(factory.make_interval(1.0))
    observer.enable_time_constrained()
    drain(owner, observer)

    obj = owner.register_object_instance(cls, "Timed-Delete-1")
    drain(owner, observer)
    assert observer.get_object_instance_handle("Timed-Delete-1") == obj
    observer_fed.clear()

    owner.delete_object_instance(obj, b"delete-tag", factory.make_time(1.0))
    drain(owner, observer)
    assert observer_fed.last_callback("removeObjectInstance") is None
    assert observer.get_object_instance_handle("Timed-Delete-1") == obj

    owner.time_advance_request(factory.make_time(2.0))
    observer.next_message_request_available(factory.make_time(2.0))
    drain(owner, observer)
    observer.next_message_request_available(factory.make_time(2.0))
    drain(owner, observer)

    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj
    assert removed.args[1] == b"delete-tag"
    assert removed.args[6].producing_federate == owner.get_federate_handle("alpha")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_object_instance_handle("Timed-Delete-1")
    with pytest.raises(ObjectInstanceNotKnown):
        observer.get_known_object_class_handle(obj)

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("timed-delete-fed")
