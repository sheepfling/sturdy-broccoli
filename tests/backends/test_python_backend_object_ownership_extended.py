# ruff: noqa: F401,F403

import pytest

from hla2010 import mom as hla_mom
from tests.backends.python_backend_extended_support import *
from hla2010.spec import RTIambassadorSpec, FederateAmbassadorSpec, lower_camel_to_snake
from hla2010.exceptions import *
from hla2010.handles import *
from hla2010.raw_api import API_METADATA
from hla2010.enums import OrderType, ResignAction, ServiceGroup
from hla2010_verification_harness.section8_matrix import run_section8_request_retraction_case, section8_matrix_config
from hla2010.types import AttributeRegionAssociation, RangeBounds
from hla2010.exceptions import AttributeAlreadyBeingDivested, AttributeAlreadyOwned, AttributeNotPublished, InteractionClassNotPublished
from tests.requirement_marker_groups import (
    CLAUSE5_DECLARATION_ADMIN_NEGATIVE_REQUIREMENTS,
    CLAUSE5_DECLARATION_NEGATIVE_REQUIREMENTS,
    CLAUSE6_MOM_CALLBACK_SUMMARY_REQUIREMENTS,
    CLAUSE6_MOM_SERVICE_REPORT_REQUIREMENTS,
    CLAUSE7_MOM_SERVICE_REPORT_REQUIREMENTS,
    CLAUSE7_NEGOTIATED_CALLBACK_SEQUENCE_REQUIREMENTS,
    CLAUSE7_OWNERSHIP_UNAVAILABLE_CALLBACK_REQUIREMENTS,
    CLAUSE8_ENABLE_AND_GRANT_CALLBACK_ORDER_REQUIREMENTS,
    CLAUSE8_MOM_SERVICE_REPORT_REQUIREMENTS,
    CLAUSE8_REQUEST_RETRACTION_CALLBACK_REQUIREMENTS,
    CLAUSE9_MOM_SERVICE_REPORT_REQUIREMENTS,
    CLAUSE10_MOM_SERVICE_REPORT_REQUIREMENTS,
)

def test_support_surface_negative_paths_cover_handle_validation_region_bounds_and_advisory_switches():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.getAttributeName(object(), object())
    with pytest.raises(NotConnected):
        rti.getParameterName(object(), object())
    with pytest.raises(NotConnected):
        rti.getAvailableDimensionsForClassAttribute(object(), object())
    with pytest.raises(NotConnected):
        rti.getDimensionHandleSet(object())
    with pytest.raises(NotConnected):
        rti.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.disableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.enableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.disableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.disableAttributeScopeAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.getRangeBounds(object(), object())
    with pytest.raises(NotConnected):
        rti.setRangeBounds(object(), object(), RangeBounds(0, 1))

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.getAttributeName(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.getParameterName(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.getAvailableDimensionsForClassAttribute(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.getDimensionHandleSet(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.enableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableAttributeScopeAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.getRangeBounds(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.setRangeBounds(object(), object(), RangeBounds(0, 1))
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("support-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    param = owner.getParameterHandle(interaction, "TrackId")
    dim = owner.getDimensionHandle("HLAdefaultRoutingSpace")
    region = owner.createRegion({dim})

    bad_class = type(cls)(cls.value + 1000)
    bad_attr = type(attr)(attr.value + 1000)
    bad_interaction = type(interaction)(interaction.value + 1000)
    bad_param = type(param)(param.value + 1000)
    bad_dim = type(dim)(dim.value + 1000)
    bad_region = type(region)(region.value + 1000)

    with pytest.raises(InvalidObjectClassHandle):
        owner.getAttributeName(bad_class, attr)
    with pytest.raises(AttributeNotDefined):
        owner.getAttributeName(cls, bad_attr)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.getParameterName(bad_interaction, param)
    with pytest.raises(InteractionParameterNotDefined):
        owner.getParameterName(interaction, bad_param)
    with pytest.raises(InvalidObjectClassHandle):
        owner.getAvailableDimensionsForClassAttribute(bad_class, attr)
    with pytest.raises(AttributeNotDefined):
        owner.getAvailableDimensionsForClassAttribute(cls, bad_attr)

    with pytest.raises(InvalidRegion):
        owner.getDimensionHandleSet(bad_region)
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOff):
        owner.disableObjectClassRelevanceAdvisorySwitch()
    owner.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOn):
        owner.enableObjectClassRelevanceAdvisorySwitch()
    owner.disableObjectClassRelevanceAdvisorySwitch()

    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOff):
        owner.disableAttributeRelevanceAdvisorySwitch()
    owner.enableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOn):
        owner.enableAttributeRelevanceAdvisorySwitch()
    owner.disableAttributeRelevanceAdvisorySwitch()

    with pytest.raises(AttributeScopeAdvisorySwitchIsOff):
        owner.disableAttributeScopeAdvisorySwitch()
    owner.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOn):
        owner.enableAttributeScopeAdvisorySwitch()
    owner.disableAttributeScopeAdvisorySwitch()

    with pytest.raises(InvalidRegion):
        owner.getRangeBounds(bad_region, dim)
    with pytest.raises(RegionDoesNotContainSpecifiedDimension):
        owner.getRangeBounds(region, bad_dim)
    with pytest.raises(InvalidRegion):
        owner.setRangeBounds(bad_region, dim, RangeBounds(0, 1))
    with pytest.raises(RegionDoesNotContainSpecifiedDimension):
        owner.setRangeBounds(region, bad_dim, RangeBounds(0, 1))
    with pytest.raises(InvalidRangeBound):
        owner.setRangeBounds(region, dim, RangeBounds(10, 1))

    owner.requestFederationSave("SUPPORT-NEGATIVE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.getDimensionHandleSet(region)
    with pytest.raises(SaveInProgress):
        owner.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(SaveInProgress):
        owner.disableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(SaveInProgress):
        owner.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(SaveInProgress):
        owner.getRangeBounds(region, dim)
    with pytest.raises(SaveInProgress):
        owner.setRangeBounds(region, dim, RangeBounds(0, 1))

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("SUPPORT-NEGATIVE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.getDimensionHandleSet(region)
    with pytest.raises(RestoreInProgress):
        owner.enableObjectClassRelevanceAdvisorySwitch()
    with pytest.raises(RestoreInProgress):
        owner.disableAttributeRelevanceAdvisorySwitch()
    with pytest.raises(RestoreInProgress):
        owner.enableAttributeScopeAdvisorySwitch()
    with pytest.raises(RestoreInProgress):
        owner.getRangeBounds(region, dim)
    with pytest.raises(RestoreInProgress):
        owner.setRangeBounds(region, dim, RangeBounds(0, 1))

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-negative-fed")


def test_request_attribute_transportation_type_change_rejects_not_connected_not_joined_and_unknown_object():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestAttributeTransportationTypeChange(ObjectInstanceHandle(999), set(), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestAttributeTransportationTypeChange(ObjectInstanceHandle(999), set(), object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("transport-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    rcs = owner.getAttributeHandle(cls, "RCS")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Transport-1")
    owner_fed.clear()
    with pytest.raises(ObjectInstanceNotKnown):
        owner.requestAttributeTransportationTypeChange(ObjectInstanceHandle(999), set(), owner.backend.engine.transportation_reliable)
    with pytest.raises(AttributeNotDefined):
        owner.requestAttributeTransportationTypeChange(obj, {type(attr)(attr.value + 1000)}, owner.backend.engine.transportation_reliable)
    with pytest.raises(InvalidTransportationType):
        owner.requestAttributeTransportationTypeChange(obj, {attr}, TransportationTypeHandle(999))
    with pytest.raises(AttributeNotOwned):
        observer.requestAttributeTransportationTypeChange(obj, {attr}, owner.backend.engine.transportation_reliable)

    owner.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        owner.requestAttributeTransportationTypeChange(obj, {rcs}, owner.backend.engine.transportation_reliable)
    owner.backend.config.strict_object_publication = False
    assert owner_fed.callbacks_named("confirmAttributeTransportationTypeChange") == []

    owner.requestFederationSave("ATTRIBUTE-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.requestAttributeTransportationTypeChange(obj, {attr}, owner.backend.engine.transportation_reliable)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("ATTRIBUTE-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.requestAttributeTransportationTypeChange(obj, {attr}, owner.backend.engine.transportation_reliable)

    owner.abortFederationRestore()
    drain(owner, observer)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("transport-negative-fed")


@pytest.mark.requirements(*CLAUSE5_DECLARATION_NEGATIVE_REQUIREMENTS)
def test_declaration_services_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unpublishObjectClassAttributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribeObjectClassAttributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribeObjectClassAttributesPassively(object(), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublishObjectClassAttributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribeObjectClassAttributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribeObjectClassAttributesPassively(object(), set())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("declaration-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.requestFederationSave("DECL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.unpublishObjectClassAttributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribeObjectClassAttributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribeObjectClassAttributesPassively(cls, {attr})

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("DECL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.unpublishObjectClassAttributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribeObjectClassAttributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribeObjectClassAttributesPassively(cls, {attr})

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("declaration-negative-fed")


def test_publish_unpublish_unsubscribe_and_interaction_subscription_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.publishObjectClassAttributes(object(), set())
    with pytest.raises(NotConnected):
        rti.unpublishObjectClass(object())
    with pytest.raises(NotConnected):
        rti.unsubscribeObjectClassAttributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribeInteractionClass(object())
    with pytest.raises(NotConnected):
        rti.subscribeInteractionClassPassively(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.publishObjectClassAttributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublishObjectClass(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribeObjectClassAttributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribeInteractionClass(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribeInteractionClassPassively(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-tail-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    owner.requestFederationSave("DECL-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.publishObjectClassAttributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        owner.unpublishObjectClass(cls)
    with pytest.raises(SaveInProgress):
        observer.unsubscribeObjectClassAttributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribeInteractionClass(interaction)
    with pytest.raises(SaveInProgress):
        observer.subscribeInteractionClassPassively(interaction)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("DECL-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.publishObjectClassAttributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        owner.unpublishObjectClass(cls)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribeObjectClassAttributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribeInteractionClass(interaction)
    with pytest.raises(RestoreInProgress):
        observer.subscribeInteractionClassPassively(interaction)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-tail-negative-fed")


@pytest.mark.requirements(*CLAUSE5_DECLARATION_ADMIN_NEGATIVE_REQUIREMENTS)
def test_publish_unpublish_and_unsubscribe_interaction_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.publishInteractionClass(object())
    with pytest.raises(NotConnected):
        rti.unpublishInteractionClass(object())
    with pytest.raises(NotConnected):
        rti.unsubscribeObjectClass(object())
    with pytest.raises(NotConnected):
        rti.unsubscribeInteractionClass(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.publishInteractionClass(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublishInteractionClass(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribeObjectClass(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribeInteractionClass(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-admin-tail-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    owner.requestFederationSave("DECL-ADMIN-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.publishInteractionClass(interaction)
    with pytest.raises(SaveInProgress):
        owner.unpublishInteractionClass(interaction)
    with pytest.raises(SaveInProgress):
        observer.unsubscribeObjectClass(cls)
    with pytest.raises(SaveInProgress):
        observer.unsubscribeInteractionClass(interaction)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("DECL-ADMIN-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.publishInteractionClass(interaction)
    with pytest.raises(RestoreInProgress):
        owner.unpublishInteractionClass(interaction)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribeObjectClass(cls)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribeInteractionClass(interaction)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-admin-tail-negative-fed")


def test_declaration_services_validate_declared_handles_attributes_and_update_rate_designators():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-arg-validation-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    bad_class = type(cls)(cls.value + 1000)
    bad_attr = type(attr)(attr.value + 1000)
    bad_interaction = type(interaction)(interaction.value + 1000)

    with pytest.raises(InvalidObjectClassHandle):
        owner.publishObjectClassAttributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        owner.publishObjectClassAttributes(cls, {bad_attr})

    with pytest.raises(InvalidObjectClassHandle):
        owner.unpublishObjectClass(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        owner.unpublishObjectClassAttributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        owner.unpublishObjectClassAttributes(cls, {bad_attr})

    with pytest.raises(InvalidInteractionClassHandle):
        owner.publishInteractionClass(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.unpublishInteractionClass(bad_interaction)

    with pytest.raises(InvalidObjectClassHandle):
        observer.subscribeObjectClassAttributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.subscribeObjectClassAttributes(cls, {bad_attr})
    with pytest.raises(InvalidUpdateRateDesignator):
        observer.subscribeObjectClassAttributes(cls, {attr}, "not-a-rate")

    with pytest.raises(InvalidObjectClassHandle):
        observer.subscribeObjectClassAttributesPassively(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.subscribeObjectClassAttributesPassively(cls, {bad_attr})
    with pytest.raises(InvalidUpdateRateDesignator):
        observer.subscribeObjectClassAttributesPassively(cls, {attr}, "not-a-rate")

    with pytest.raises(InvalidObjectClassHandle):
        observer.unsubscribeObjectClass(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        observer.unsubscribeObjectClassAttributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.unsubscribeObjectClassAttributes(cls, {bad_attr})

    with pytest.raises(InvalidInteractionClassHandle):
        observer.subscribeInteractionClass(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        observer.subscribeInteractionClassPassively(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        observer.unsubscribeInteractionClass(bad_interaction)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-arg-validation-fed")


def test_declaration_services_are_observable_through_mom_service_invocation_reporting():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("decl-mom-service-report-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = observer.getParameterHandle(service_report, "HLAservice")
    report_success = observer.getParameterHandle(service_report, "HLAsuccessIndicator")

    observer.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-decl-service-reporting",
    )
    drain(owner, observer)
    assert owner.backend.state.service_reporting is True

    observer_fed.clear()
    owner.publishObjectClassAttributes(cls, {attr})
    owner.unpublishObjectClass(cls)
    owner.publishInteractionClass(interaction)
    owner.unpublishInteractionClass(interaction)
    owner.subscribeObjectClassAttributes(cls, {attr})
    owner.subscribeObjectClassAttributesPassively(cls, {attr}, "HLAdefault")
    owner.unsubscribeObjectClass(cls)
    owner.subscribeInteractionClass(interaction)
    owner.subscribeInteractionClassPassively(interaction)
    owner.unsubscribeInteractionClass(interaction)
    drain(owner, observer)

    reports = [rec for rec in observer_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "publishObjectClassAttributes",
        "unpublishObjectClass",
        "publishInteractionClass",
        "unpublishInteractionClass",
        "subscribeObjectClassAttributes",
        "subscribeObjectClassAttributesPassively",
        "unsubscribeObjectClass",
        "subscribeInteractionClass",
        "subscribeInteractionClassPassively",
        "unsubscribeInteractionClass",
    }

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-mom-service-report-fed")


@pytest.mark.requirements(*CLAUSE6_MOM_SERVICE_REPORT_REQUIREMENTS)
def test_clause_6_federate_initiated_services_are_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-mom-service-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "om-mom-service-report-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")
    best_effort = owner.backend.engine.transportation_best_effort

    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = witness.getParameterHandle(service_report, "HLAservice")
    report_success = witness.getParameterHandle(service_report, "HLAsuccessIndicator")

    witness.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-om-service-reporting",
    )
    observer.sendInteraction(
        set_reporting,
        {
            sr_fed: observer.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-om-observer-service-reporting",
    )
    drain(owner, observer)
    assert owner.backend.state.service_reporting is True
    assert observer.backend.state.service_reporting is True

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)
    owner.reserveObjectInstanceName("OM-MOM-Reserved")
    owner.releaseObjectInstanceName("OM-MOM-Reserved")
    owner.reserveMultipleObjectInstanceName({"OM-MOM-A", "OM-MOM-B"})
    owner.releaseMultipleObjectInstanceName({"OM-MOM-A", "OM-MOM-B"})
    obj = owner.registerObjectInstance(cls, "OM-MOM-Object")
    drain(owner, observer)
    observer.localDeleteObjectInstance(obj)
    owner.updateAttributeValues(obj, {attr: b"mom-position"}, b"mom-update")
    owner.sendInteraction(interaction, {track_id: b"mom-track"}, b"mom-send")
    owner.requestAttributeValueUpdate(obj, {attr}, b"mom-refresh")
    owner.requestAttributeTransportationTypeChange(obj, {attr}, best_effort)
    owner.queryAttributeTransportationType(obj, attr)
    owner.requestInteractionTransportationTypeChange(interaction, best_effort)
    owner.queryInteractionTransportationType(interaction)
    owner.deleteObjectInstance(obj, b"mom-delete")
    drain(owner, observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "reserveObjectInstanceName",
        "releaseObjectInstanceName",
        "reserveMultipleObjectInstanceName",
        "releaseMultipleObjectInstanceName",
        "registerObjectInstance",
        "localDeleteObjectInstance",
        "updateAttributeValues",
        "sendInteraction",
        "requestAttributeValueUpdate",
        "requestAttributeTransportationTypeChange",
        "queryAttributeTransportationType",
        "requestInteractionTransportationTypeChange",
        "queryInteractionTransportationType",
        "deleteObjectInstance",
    }

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-mom-service-report-fed")


@pytest.mark.requirements(*CLAUSE6_MOM_CALLBACK_SUMMARY_REQUIREMENTS)
def test_clause_6_callback_activity_is_visible_in_mom_summary():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-mom-callback-summary-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")
    best_effort = owner.backend.engine.transportation_best_effort

    owner.reserveObjectInstanceName("OM-MOM-Callback-Reserved")
    owner.reserveMultipleObjectInstanceName({"OM-MOM-CB-A", "OM-MOM-CB-B"})
    drain(owner, observer)

    observer.subscribeObjectClassAttributes(cls, {attr})
    observer.subscribeInteractionClass(interaction)
    owner.publishObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)
    owner.enableAttributeRelevanceAdvisorySwitch()
    obj = owner.registerObjectInstance(cls, "OM-MOM-Callback-Object")
    drain(owner, observer)
    observer.unsubscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer)
    observer.subscribeObjectClassAttributes(cls, {attr}, "HLAdefault")
    drain(owner, observer)

    owner.updateAttributeValues(obj, {attr: b"mom-callback-position"}, b"mom-callback-update")
    owner.sendInteraction(interaction, {track_id: b"mom-callback-track"}, b"mom-callback-send")
    observer.requestAttributeValueUpdate(obj, {attr}, b"mom-callback-refresh")
    owner.requestAttributeTransportationTypeChange(obj, {attr}, best_effort)
    owner.queryAttributeTransportationType(obj, attr)
    owner.requestInteractionTransportationTypeChange(interaction, best_effort)
    owner.queryInteractionTransportationType(interaction)
    owner.deleteObjectInstance(obj, b"mom-callback-delete")
    drain(owner, observer)

    owner_summary = owner.backend.current_mom_summary()
    observer_summary = observer.backend.current_mom_summary()

    assert owner_summary["callback_counts"]["objectInstanceNameReservationSucceeded"] >= 1
    assert owner_summary["callback_counts"]["multipleObjectInstanceNameReservationSucceeded"] >= 1
    assert owner_summary["callback_counts"]["turnUpdatesOnForObjectInstance"] >= 2
    assert owner_summary["callback_counts"]["turnUpdatesOffForObjectInstance"] >= 1
    assert owner_summary["callback_counts"]["provideAttributeValueUpdate"] >= 1
    assert owner_summary["callback_counts"]["confirmAttributeTransportationTypeChange"] >= 1
    assert owner_summary["callback_counts"]["reportAttributeTransportationType"] >= 1
    assert owner_summary["callback_counts"]["confirmInteractionTransportationTypeChange"] >= 1
    assert owner_summary["callback_counts"]["reportInteractionTransportationType"] >= 1

    assert observer_summary["callback_counts"]["discoverObjectInstance"] >= 1
    assert observer_summary["callback_counts"]["reflectAttributeValues"] >= 1
    assert observer_summary["callback_counts"]["receiveInteraction"] >= 1
    assert observer_summary["callback_counts"]["removeObjectInstance"] >= 1

    assert "turnUpdatesOnForObjectInstance" in owner_summary["recent_callbacks"]
    assert "turnUpdatesOffForObjectInstance" in owner_summary["recent_callbacks"]
    assert "provideAttributeValueUpdate" in owner_summary["recent_callbacks"]
    assert "discoverObjectInstance" in observer_summary["recent_callbacks"]

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-mom-callback-summary-fed")


@pytest.mark.requirements(*CLAUSE7_MOM_SERVICE_REPORT_REQUIREMENTS)
def test_clause_7_services_are_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, _h1, h2 = joined_pair("own-mom-service-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "own-mom-service-report-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = witness.getParameterHandle(service_report, "HLAservice")
    report_success = witness.getParameterHandle(service_report, "HLAsuccessIndicator")

    witness.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-own-owner-service-reporting",
    )
    observer.sendInteraction(
        set_reporting,
        {
            sr_fed: observer.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-own-observer-service-reporting",
    )
    drain(owner, observer, witness)
    assert owner.backend.state.service_reporting is True
    assert observer.backend.state.service_reporting is True

    owner.publishObjectClassAttributes(cls, {attr})
    observer.publishObjectClassAttributes(cls, {attr})

    obj_uncond = owner.registerObjectInstance(cls, "OWN-MOM-Uncond")
    obj_neg = owner.registerObjectInstance(cls, "OWN-MOM-Neg")
    obj_confirm = owner.registerObjectInstance(cls, "OWN-MOM-Confirm")
    obj_acquire = owner.registerObjectInstance(cls, "OWN-MOM-Acquire")
    obj_available = owner.registerObjectInstance(cls, "OWN-MOM-Available")
    obj_deny = owner.registerObjectInstance(cls, "OWN-MOM-Deny")
    obj_wanted = owner.registerObjectInstance(cls, "OWN-MOM-Wanted")
    obj_cancel_neg = owner.registerObjectInstance(cls, "OWN-MOM-CancelNeg")
    obj_cancel_acq = owner.registerObjectInstance(cls, "OWN-MOM-CancelAcq")
    obj_query = owner.registerObjectInstance(cls, "OWN-MOM-Query")
    drain(owner, observer, witness)

    owner.unconditionalAttributeOwnershipDivestiture(obj_uncond, {attr})

    owner.negotiatedAttributeOwnershipDivestiture(obj_neg, {attr}, b"neg-offer")

    owner.negotiatedAttributeOwnershipDivestiture(obj_confirm, {attr}, b"confirm-offer")
    drain(owner, observer, witness)
    federation = engine.federations["own-mom-service-report-fed"]
    federation.objects[obj_confirm].attribute_candidates[attr] = {h2}
    owner.confirmDivestiture(obj_confirm, {attr}, b"confirm-tag")

    observer.attributeOwnershipAcquisition(obj_acquire, {attr}, b"acquire-tag")
    observer.attributeOwnershipAcquisitionIfAvailable(obj_available, {attr})

    observer.attributeOwnershipAcquisition(obj_deny, {attr}, b"deny-tag")
    drain(owner, observer, witness)
    owner.attributeOwnershipReleaseDenied(obj_deny, {attr})

    observer.attributeOwnershipAcquisition(obj_wanted, {attr}, b"wanted-tag")
    drain(owner, observer, witness)
    owner.attributeOwnershipDivestitureIfWanted(obj_wanted, {attr})

    owner.negotiatedAttributeOwnershipDivestiture(obj_cancel_neg, {attr}, b"cancel-neg-tag")
    drain(owner, observer, witness)
    owner.cancelNegotiatedAttributeOwnershipDivestiture(obj_cancel_neg, {attr})

    observer.attributeOwnershipAcquisition(obj_cancel_acq, {attr}, b"cancel-acq-tag")
    drain(owner, observer, witness)
    observer.cancelAttributeOwnershipAcquisition(obj_cancel_acq, {attr})

    observer.queryAttributeOwnership(obj_query, attr)
    assert owner.isAttributeOwnedByFederate(obj_query, attr) is True
    drain(owner, observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "unconditionalAttributeOwnershipDivestiture",
        "negotiatedAttributeOwnershipDivestiture",
        "confirmDivestiture",
        "attributeOwnershipAcquisition",
        "attributeOwnershipAcquisitionIfAvailable",
        "attributeOwnershipReleaseDenied",
        "attributeOwnershipDivestitureIfWanted",
        "cancelNegotiatedAttributeOwnershipDivestiture",
        "cancelAttributeOwnershipAcquisition",
        "queryAttributeOwnership",
        "isAttributeOwnedByFederate",
    }

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("own-mom-service-report-fed")


@pytest.mark.requirements(*CLAUSE8_MOM_SERVICE_REPORT_REQUIREMENTS)
def test_clause_8_services_are_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("tm-mom-service-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "tm-mom-service-report-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")
    factory = owner.getTimeFactory()

    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = witness.getParameterHandle(service_report, "HLAservice")
    report_success = witness.getParameterHandle(service_report, "HLAsuccessIndicator")

    witness.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-tm-owner-service-reporting",
    )
    observer.sendInteraction(
        set_reporting,
        {
            sr_fed: observer.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-tm-observer-service-reporting",
    )
    drain(owner, observer, witness)
    assert owner.backend.state.service_reporting is True
    assert observer.backend.state.service_reporting is True

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)
    observer.subscribeInteractionClass(interaction)

    owner.enableAsynchronousDelivery()
    owner.disableAsynchronousDelivery()
    owner.enableTimeRegulation(factory.make_interval(1.0))
    drain(owner, observer, witness)
    observer.enableTimeConstrained()
    drain(owner, observer, witness)

    owner.queryGALT()
    owner.queryLogicalTime()
    owner.queryLITS()
    owner.modifyLookahead(factory.make_interval(2.0))
    owner.queryLookahead()

    owner.timeAdvanceRequest(factory.make_time(4.0))
    observer.timeAdvanceRequestAvailable(factory.make_time(4.0))
    drain(owner, observer, witness)

    owner.nextMessageRequest(factory.make_time(5.0))
    observer.nextMessageRequestAvailable(factory.make_time(5.0))
    drain(owner, observer, witness)

    owner.flushQueueRequest(factory.make_time(6.0))
    drain(owner, observer, witness)

    obj = owner.registerObjectInstance(cls, "TM-MOM-Object")
    drain(owner, observer, witness)
    retraction = owner.sendInteraction(
        interaction,
        {track_id: b"tm-mom-track"},
        b"tm-mom-send",
        factory.make_time(8.0),
    )
    owner.retract(retraction.handle)
    owner.changeAttributeOrderType(obj, {attr}, OrderType.TIMESTAMP)
    owner.changeInteractionOrderType(interaction, OrderType.TIMESTAMP)
    owner.disableTimeRegulation()
    observer.disableTimeConstrained()
    drain(owner, observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "enableAsynchronousDelivery",
        "disableAsynchronousDelivery",
        "enableTimeRegulation",
        "enableTimeConstrained",
        "queryGALT",
        "queryLogicalTime",
        "queryLITS",
        "modifyLookahead",
        "queryLookahead",
        "timeAdvanceRequest",
        "timeAdvanceRequestAvailable",
        "nextMessageRequest",
        "nextMessageRequestAvailable",
        "flushQueueRequest",
        "retract",
        "changeAttributeOrderType",
        "changeInteractionOrderType",
        "disableTimeRegulation",
        "disableTimeConstrained",
    }

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("tm-mom-service-report-fed")


@pytest.mark.requirements(*CLAUSE10_MOM_SERVICE_REPORT_REQUIREMENTS)
def test_clause_10_services_are_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, h1, _h2 = joined_pair("sup-mom-service-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "sup-mom-service-report-fed")

    obj_cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(obj_cls, "Position")
    inter_cls = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    param = owner.getParameterHandle(inter_cls, "TrackId")
    dim = owner.getDimensionHandle("HLAdefaultRoutingSpace")
    region = owner.createRegion({dim})
    owner.setRangeBounds(region, dim, RangeBounds(10, 20))
    obj = owner.registerObjectInstance(obj_cls, "Support-MOM-1")
    drain(owner, observer, witness)

    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = witness.getParameterHandle(service_report, "HLAservice")
    report_success = witness.getParameterHandle(service_report, "HLAsuccessIndicator")

    witness.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-sup-owner-service-reporting",
    )
    observer.sendInteraction(
        set_reporting,
        {
            sr_fed: observer.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-sup-observer-service-reporting",
    )
    drain(owner, observer, witness)
    assert owner.backend.state.service_reporting is True
    assert observer.backend.state.service_reporting is True

    owner.getAutomaticResignDirective()
    owner.setAutomaticResignDirective(ResignAction.DELETE_OBJECTS)
    owner.getFederateHandle("alpha")
    owner.getFederateName(h1)
    owner.getObjectClassHandle("HLAobjectRoot.Target")
    owner.getObjectClassName(obj_cls)
    owner.getKnownObjectClassHandle(obj)
    owner.getObjectInstanceHandle("Support-MOM-1")
    owner.getObjectInstanceName(obj)
    owner.getAttributeHandle(obj_cls, "Position")
    owner.getAttributeName(obj_cls, attr)
    owner.getUpdateRateValue("default")
    owner.getUpdateRateValueForAttribute(obj, attr)
    owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    owner.getInteractionClassName(inter_cls)
    owner.getParameterHandle(inter_cls, "TrackId")
    owner.getParameterName(inter_cls, param)
    owner.getOrderType("HLAreceive")
    owner.getOrderName(OrderType.RECEIVE)
    owner.getTransportationTypeHandle("HLAreliable")
    owner.getTransportationTypeName(owner.getTransportationTypeHandle("HLAreliable"))
    owner.getAvailableDimensionsForClassAttribute(obj_cls, attr)
    owner.getAvailableDimensionsForInteractionClass(inter_cls)
    owner.getDimensionHandle("HLAdefaultRoutingSpace")
    owner.getDimensionName(dim)
    owner.getDimensionUpperBound(dim)
    owner.getDimensionHandleSet(region)
    owner.getRangeBounds(region, dim)
    owner.setRangeBounds(region, dim, RangeBounds(15, 25))
    owner.normalizeFederateHandle(h1)
    owner.normalizeServiceGroup(ServiceGroup.OBJECT_MANAGEMENT)
    owner.enableObjectClassRelevanceAdvisorySwitch()
    owner.disableObjectClassRelevanceAdvisorySwitch()
    owner.enableAttributeRelevanceAdvisorySwitch()
    owner.disableAttributeRelevanceAdvisorySwitch()
    owner.enableAttributeScopeAdvisorySwitch()
    owner.disableAttributeScopeAdvisorySwitch()
    owner.enableInteractionRelevanceAdvisorySwitch()
    owner.disableInteractionRelevanceAdvisorySwitch()
    owner.evokeCallback(0.0)
    owner.evokeMultipleCallbacks(0.0, 0.0)
    owner.disableCallbacks()
    owner.enableCallbacks()
    drain(owner, observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "getAutomaticResignDirective",
        "setAutomaticResignDirective",
        "getFederateHandle",
        "getFederateName",
        "getObjectClassHandle",
        "getObjectClassName",
        "getKnownObjectClassHandle",
        "getObjectInstanceHandle",
        "getObjectInstanceName",
        "getAttributeHandle",
        "getAttributeName",
        "getUpdateRateValue",
        "getUpdateRateValueForAttribute",
        "getInteractionClassHandle",
        "getInteractionClassName",
        "getParameterHandle",
        "getParameterName",
        "getOrderType",
        "getOrderName",
        "getTransportationTypeHandle",
        "getTransportationTypeName",
        "getAvailableDimensionsForClassAttribute",
        "getAvailableDimensionsForInteractionClass",
        "getDimensionHandle",
        "getDimensionName",
        "getDimensionUpperBound",
        "getDimensionHandleSet",
        "getRangeBounds",
        "setRangeBounds",
        "normalizeFederateHandle",
        "normalizeServiceGroup",
        "enableObjectClassRelevanceAdvisorySwitch",
        "disableObjectClassRelevanceAdvisorySwitch",
        "enableAttributeRelevanceAdvisorySwitch",
        "disableAttributeRelevanceAdvisorySwitch",
        "enableAttributeScopeAdvisorySwitch",
        "disableAttributeScopeAdvisorySwitch",
        "enableInteractionRelevanceAdvisorySwitch",
        "disableInteractionRelevanceAdvisorySwitch",
        "evokeCallback",
        "evokeMultipleCallbacks",
        "enableCallbacks",
        "disableCallbacks",
    }

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("sup-mom-service-report-fed")


@pytest.mark.requirements(*CLAUSE8_ENABLE_AND_GRANT_CALLBACK_ORDER_REQUIREMENTS)
def test_clause_8_enable_and_grant_callbacks_arrive_in_expected_order():
    _, owner, observer, owner_fed, observer_fed, _h1, _h2 = joined_pair("tm-callback-order-fed")
    factory = owner.getTimeFactory()

    owner.enableTimeRegulation(factory.make_interval(1.0))
    observer.enableTimeConstrained()
    drain(owner, observer)

    assert owner_fed.records
    assert observer_fed.records
    assert owner_fed.records[0].method_name == "timeRegulationEnabled"
    assert observer_fed.records[0].method_name == "timeConstrainedEnabled"
    assert owner_fed.callbacks_named("timeAdvanceGrant") == []
    assert observer_fed.callbacks_named("timeAdvanceGrant") == []

    owner_fed.clear()
    observer_fed.clear()
    owner.timeAdvanceRequest(factory.make_time(4.0))
    observer.timeAdvanceRequestAvailable(factory.make_time(4.0))
    drain(owner, observer)

    assert owner_fed.records
    assert observer_fed.records
    assert owner_fed.records[-1].method_name == "timeAdvanceGrant"
    assert observer_fed.records[-1].method_name == "timeAdvanceGrant"
    assert owner_fed.records[-1].args[0] == factory.make_time(4.0)
    assert observer_fed.records[-1].args[0] == factory.make_time(4.0)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("tm-callback-order-fed")


@pytest.mark.requirements(*CLAUSE8_REQUEST_RETRACTION_CALLBACK_REQUIREMENTS)
def test_clause_8_request_retraction_callback_arrives_after_delivered_interaction():
    publisher = rti_ambassador(engine=InMemoryRTIEngine())
    subscriber = rti_ambassador(engine=publisher.backend.engine)
    config = section8_matrix_config("tm-request-retraction-order-fed", "HLAfloat64Time")
    summary = run_section8_request_retraction_case(publisher, subscriber, config=config)

    subscriber_records = summary["subscriber_federate"].records
    receive_index = next(
        i for i, record in enumerate(subscriber_records)
        if record.method_name == "receiveInteraction" and record.args[1] == {summary["parameter"]: config.first_payload}
    )
    retract_index = next(
        i for i, record in enumerate(subscriber_records)
        if record.method_name == "requestRetraction" and record.args[0] == summary["sent"].handle
    )

    assert receive_index < retract_index
    assert subscriber_records[retract_index] == summary["request_retraction"]
    assert summary["received"] == subscriber_records[receive_index]
    assert not any(
        record.method_name == "receiveInteraction"
        and record.args[1] == {summary["parameter"]: config.first_payload}
        for record in subscriber_records[retract_index + 1 :]
    )


def test_python_rti_query_attribute_ownership_reports_owner_for_owned_attribute():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("query-owned-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Owned-1")

    observer.queryAttributeOwnership(obj, attr)
    drain(owner, observer)

    owned = observer_fed.last_callback("informAttributeOwnership")
    assert owned is not None
    assert owned.args == (obj, attr, owner.backend.state.handle)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("query-owned-fed")


def test_python_rti_query_attribute_ownership_reports_rti_for_mom_owned_attribute():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("query-rti-owned-fed")
    federation_class = observer.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_name = observer.getAttributeHandle(federation_class, "HLAfederationName")
    mom_object = observer.backend.current_mom_summary()["federation_object"]

    assert isinstance(mom_object, ObjectInstanceHandle)
    observer.queryAttributeOwnership(mom_object, federation_name)
    drain(owner, observer)

    owned = observer_fed.last_callback("attributeIsOwnedByRTI")
    assert owned is not None
    assert owned.args == (mom_object, federation_name)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("query-rti-owned-fed")


def test_declaration_management_effects_apply_while_time_managed():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("decl-time-managed-fed")
    factory = owner.getTimeFactory()
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")

    owner.enableTimeRegulation(factory.make_interval(1.0))
    observer.enableTimeConstrained()
    drain(owner, observer)

    observer.subscribeObjectClassAttributes(cls, {attr})
    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeInteractionClass(interaction)
    owner.publishInteractionClass(interaction)

    obj = owner.registerObjectInstance(cls, "Time-Managed-Declared")
    owner.sendInteraction(interaction, {track_id: b"ro"}, b"\x00\x00\x00\x00")
    drain(owner, observer)

    discovery = observer_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    received = observer_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"ro"

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-time-managed-fed")


def test_unpublishing_object_class_attributes_prevents_strict_updates():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-unpublish-object-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Strict-Unpublish-Object")
    owner.unpublishObjectClassAttributes(cls, {attr})
    owner.backend.config.strict_object_publication = True

    with pytest.raises(AttributeNotPublished):
        owner.updateAttributeValues(obj, {attr: b"x"}, b"\x00\x00\x00\x00")

    owner.backend.config.strict_object_publication = False
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-unpublish-object-fed")


def test_unpublishing_interaction_class_prevents_strict_sends():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-unpublish-interaction-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")

    owner.publishInteractionClass(interaction)
    owner.unpublishInteractionClass(interaction)
    owner.backend.config.strict_interaction_publication = True

    with pytest.raises(InteractionClassNotPublished):
        owner.sendInteraction(interaction, {track_id: b"x"}, b"\x00\x00\x00\x00")

    owner.backend.config.strict_interaction_publication = False
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-unpublish-interaction-fed")


def test_transportation_type_services_emit_confirm_and_report_callbacks():
    _, owner, observer, owner_fed, _observer_fed, owner_handle, _observer_handle = joined_pair("transport-positive-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    best_effort = owner.backend.engine.transportation_best_effort

    owner.publishObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)
    obj = owner.registerObjectInstance(cls, "Transport-Positive-1")
    owner_fed.clear()

    owner.requestAttributeTransportationTypeChange(obj, {attr}, best_effort)
    owner.queryAttributeTransportationType(obj, attr)
    owner.requestInteractionTransportationTypeChange(interaction, best_effort)
    owner.queryInteractionTransportationType(interaction)
    drain(owner, observer)

    assert owner.backend.state.attribute_transportation_overrides[(obj, attr)] == best_effort
    assert owner.backend.state.interaction_transportation_overrides[interaction] == best_effort

    confirm_attr = owner_fed.last_callback("confirmAttributeTransportationTypeChange")
    report_attr = owner_fed.last_callback("reportAttributeTransportationType")
    confirm_interaction = owner_fed.last_callback("confirmInteractionTransportationTypeChange")
    report_interaction = owner_fed.last_callback("reportInteractionTransportationType")

    assert confirm_attr is not None
    assert confirm_attr.args == (obj, {attr}, best_effort)
    assert report_attr is not None
    assert report_attr.args == (obj, attr, best_effort)
    assert confirm_interaction is not None
    assert confirm_interaction.args == (interaction, best_effort)
    assert report_interaction is not None
    assert report_interaction.args == (owner_handle, interaction, best_effort)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("transport-positive-fed")


def test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("transport-runtime-behavior-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    pos = owner.getAttributeHandle(cls, "Position")
    rcs = owner.getAttributeHandle(cls, "RCS")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")
    reliable = owner.backend.engine.transportation_reliable
    best_effort = owner.backend.engine.transportation_best_effort

    owner.publishObjectClassAttributes(cls, {pos, rcs})
    observer.subscribeObjectClassAttributes(cls, {pos, rcs})
    owner.publishInteractionClass(interaction)
    observer.subscribeInteractionClass(interaction)
    obj = owner.registerObjectInstance(cls, "Transport-Runtime-Behavior")
    drain(owner, observer)
    observer_fed.clear()

    owner.requestAttributeTransportationTypeChange(obj, {pos}, reliable)
    owner.requestAttributeTransportationTypeChange(obj, {rcs}, best_effort)
    owner.requestInteractionTransportationTypeChange(interaction, best_effort)
    drain(owner, observer)
    observer_fed.clear()

    owner.updateAttributeValues(obj, {pos: b"pos", rcs: b"rcs"}, b"mixed-transport")
    owner.sendInteraction(interaction, {track_id: b"trk"}, b"be-interaction")
    drain(owner, observer)

    reflections = observer_fed.callbacks_named("reflectAttributeValues")
    receives = observer_fed.callbacks_named("receiveInteraction")

    assert len(reflections) == 2
    reflected_by_transport = {record.args[4]: record.args[1] for record in reflections}
    assert reflected_by_transport[reliable] == {pos: b"pos"}
    assert reflected_by_transport[best_effort] == {rcs: b"rcs"}

    interaction_record = receives[-1]
    assert interaction_record.args[0] == interaction
    assert interaction_record.args[1][track_id] == b"trk"
    assert interaction_record.args[4] == best_effort

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("transport-runtime-behavior-fed")


@pytest.mark.requirements("HLA1516.1-DM-5.10-001", "HLA1516.1-DM-5.11-001")
def test_start_and_stop_registration_callbacks_are_delivered():
    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-registration-callback-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner_fed.clear()
    observer.subscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer)
    assert owner_fed.callbacks_named("startRegistrationForObjectClass") == []

    owner.publishObjectClassAttributes(cls, {attr})
    owner.unpublishObjectClassAttributes(cls, {attr})
    owner.publishObjectClassAttributes(cls, {attr})
    observer.unsubscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer)

    registration_callbacks = [
        record for record in owner_fed.records
        if record.method_name in {"startRegistrationForObjectClass", "stopRegistrationForObjectClass"}
    ]
    assert [record.method_name for record in registration_callbacks] == [
        "startRegistrationForObjectClass",
        "stopRegistrationForObjectClass",
        "startRegistrationForObjectClass",
        "stopRegistrationForObjectClass",
    ]

    started = registration_callbacks[0]
    first_stopped = registration_callbacks[1]
    second_started = registration_callbacks[2]
    second_stopped = registration_callbacks[3]
    assert started.args == (cls,)
    assert first_stopped.args == (cls,)
    assert second_started.args == (cls,)
    assert second_stopped.args == (cls,)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-registration-callback-fed")


@pytest.mark.requirements("HLA1516.1-DM-5.12-001", "HLA1516.1-DM-5.13-001")
def test_turn_interactions_on_and_off_callbacks_are_delivered():
    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-interaction-callback-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    owner_fed.clear()
    observer.subscribeInteractionClass(interaction)
    drain(owner, observer)
    assert owner_fed.callbacks_named("turnInteractionsOn") == []

    owner.publishInteractionClass(interaction)
    owner.unpublishInteractionClass(interaction)
    owner.publishInteractionClass(interaction)
    observer.unsubscribeInteractionClass(interaction)
    drain(owner, observer)

    interaction_callbacks = [
        record for record in owner_fed.records
        if record.method_name in {"turnInteractionsOn", "turnInteractionsOff"}
    ]
    assert [record.method_name for record in interaction_callbacks] == [
        "turnInteractionsOn",
        "turnInteractionsOff",
        "turnInteractionsOn",
        "turnInteractionsOff",
    ]

    on = interaction_callbacks[0]
    first_off = interaction_callbacks[1]
    second_on = interaction_callbacks[2]
    second_off = interaction_callbacks[3]
    assert on.args == (interaction,)
    assert first_off.args == (interaction,)
    assert second_on.args == (interaction,)
    assert second_off.args == (interaction,)

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("decl-interaction-callback-fed")


def test_turn_updates_on_and_off_callbacks_follow_object_instance_relevance():
    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-turn-updates-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    owner.enableAttributeRelevanceAdvisorySwitch()
    obj = owner.registerObjectInstance(cls, "Turn-Updates-Object")
    drain(owner, observer)
    owner_fed.clear()

    observer.subscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer)
    on = owner_fed.last_callback("turnUpdatesOnForObjectInstance")
    assert on is not None
    assert on.args == (obj, {attr})

    owner_fed.clear()
    observer.unsubscribeObjectClassAttributes(cls, {attr})
    drain(owner, observer)
    off = owner_fed.last_callback("turnUpdatesOffForObjectInstance")
    assert off is not None
    assert off.args == (obj, {attr})

    owner_fed.clear()
    observer.subscribeObjectClassAttributes(cls, {attr}, "HLAdefault")
    drain(owner, observer)
    on_with_designator = owner_fed.last_callback("turnUpdatesOnForObjectInstance")
    assert on_with_designator is not None
    assert on_with_designator.args == (obj, {attr}, "HLAdefault")

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-turn-updates-fed")


def test_turn_updates_object_instance_callbacks_validate_state_arguments_and_wrap_callback_failures():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.backend.turn_updates_on_for_object_instance(ObjectInstanceHandle(999), {AttributeHandle(1)})
    with pytest.raises(NotConnected):
        rti.backend.turn_updates_off_for_object_instance(ObjectInstanceHandle(999), {AttributeHandle(1)})

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.backend.turn_updates_on_for_object_instance(ObjectInstanceHandle(999), {AttributeHandle(1)})
    with pytest.raises(FederateNotExecutionMember):
        rti.backend.turn_updates_off_for_object_instance(ObjectInstanceHandle(999), {AttributeHandle(1)})
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-turn-updates-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)

    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Turn-Updates-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.backend.turn_updates_on_for_object_instance(ObjectInstanceHandle(999), {attr})
    with pytest.raises(ObjectInstanceNotKnown):
        owner.backend.turn_updates_off_for_object_instance(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.backend.turn_updates_on_for_object_instance(obj, {bad_attr})
    with pytest.raises(AttributeNotDefined):
        owner.backend.turn_updates_off_for_object_instance(obj, {bad_attr})
    with pytest.raises(InvalidUpdateRateDesignator):
        owner.backend.turn_updates_on_for_object_instance(obj, {attr}, "MissingRate")

    owner.requestFederationSave("TURN-UPDATES-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.backend.turn_updates_on_for_object_instance(obj, {attr})
    with pytest.raises(SaveInProgress):
        owner.backend.turn_updates_off_for_object_instance(obj, {attr})

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("TURN-UPDATES-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.backend.turn_updates_on_for_object_instance(obj, {attr})
    with pytest.raises(RestoreInProgress):
        owner.backend.turn_updates_off_for_object_instance(obj, {attr})
    owner.abortFederationRestore()
    drain(owner, observer)

    class _FailingTurnUpdatesAmbassador(RecordingFederateAmbassador):
        def on_turn_updates_on_for_object_instance(self, *args, **kwargs):
            raise RuntimeError("turn-updates-on-failed")

        def on_turn_updates_off_for_object_instance(self, *args, **kwargs):
            raise RuntimeError("turn-updates-off-failed")

    failing = rti_ambassador(engine=InMemoryRTIEngine())
    failing.connect(_FailingTurnUpdatesAmbassador(), CallbackModel.HLA_IMMEDIATE)
    failing.createFederationExecution("om-turn-updates-failing-fed", "TargetRadarFOMmodule.xml")
    failing.joinFederationExecution("alpha", "type-a", "om-turn-updates-failing-fed")
    fail_cls = failing.getObjectClassHandle("HLAobjectRoot.Target")
    fail_attr = failing.getAttributeHandle(fail_cls, "Position")
    failing.publishObjectClassAttributes(fail_cls, {fail_attr})
    fail_obj = failing.registerObjectInstance(fail_cls, "Turn-Updates-Failing")

    with pytest.raises(FederateInternalError):
        failing.backend.turn_updates_on_for_object_instance(fail_obj, {fail_attr})
    with pytest.raises(FederateInternalError):
        failing.backend.turn_updates_off_for_object_instance(fail_obj, {fail_attr})

    failing.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    failing.destroyFederationExecution("om-turn-updates-failing-fed")
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-turn-updates-negative-fed")


def test_provide_attribute_value_update_callback_validates_state_arguments_and_wraps_callback_failures():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.backend.provide_attribute_value_update(ObjectInstanceHandle(999), {AttributeHandle(1)}, b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.backend.provide_attribute_value_update(ObjectInstanceHandle(999), {AttributeHandle(1)}, b"tag")
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-provide-avu-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)

    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Provide-AVU-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.backend.provide_attribute_value_update(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.backend.provide_attribute_value_update(obj, {bad_attr}, b"tag")

    owner.requestFederationSave("PROVIDE-AVU-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.backend.provide_attribute_value_update(obj, {attr}, b"tag")

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("PROVIDE-AVU-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.backend.provide_attribute_value_update(obj, {attr}, b"tag")
    owner.abortFederationRestore()
    drain(owner, observer)

    owner_fed.clear()
    owner.backend.provide_attribute_value_update(obj, {attr}, b"tag")
    drain(owner, observer)
    provide = owner_fed.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args == (obj, {attr}, b"tag")

    class _FailingProvideAmbassador(RecordingFederateAmbassador):
        def on_provide_attribute_value_update(self, *args, **kwargs):
            raise RuntimeError("provide-avu-failed")

    failing = rti_ambassador(engine=InMemoryRTIEngine())
    failing.connect(_FailingProvideAmbassador(), CallbackModel.HLA_IMMEDIATE)
    failing.createFederationExecution("om-provide-avu-failing-fed", "TargetRadarFOMmodule.xml")
    failing.joinFederationExecution("alpha", "type-a", "om-provide-avu-failing-fed")
    fail_cls = failing.getObjectClassHandle("HLAobjectRoot.Target")
    fail_attr = failing.getAttributeHandle(fail_cls, "Position")
    failing.publishObjectClassAttributes(fail_cls, {fail_attr})
    fail_obj = failing.registerObjectInstance(fail_cls, "Provide-AVU-Failing")

    with pytest.raises(FederateInternalError):
        failing.backend.provide_attribute_value_update(fail_obj, {fail_attr}, b"tag")

    failing.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    failing.destroyFederationExecution("om-provide-avu-failing-fed")
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-provide-avu-negative-fed")


def test_clause_5_service_and_callback_signature_metadata_matches_source_bindings():
    rti_checks = {
        "publishObjectClassAttributes": ("5.2", ["ObjectClassHandle theClass, AttributeHandleSet attributeList"]),
        "unpublishObjectClass": ("5.3", ["ObjectClassHandle theClass"]),
        "unpublishObjectClassAttributes": ("5.3", ["ObjectClassHandle theClass, AttributeHandleSet attributeList"]),
        "publishInteractionClass": ("5.4", ["InteractionClassHandle theInteraction"]),
        "unpublishInteractionClass": ("5.5", ["InteractionClassHandle theInteraction"]),
        "subscribeObjectClassAttributes": (
            "5.6",
            [
                "ObjectClassHandle theClass, AttributeHandleSet attributeList",
                "ObjectClassHandle theClass, AttributeHandleSet attributeList, String updateRateDesignator",
            ],
        ),
        "subscribeObjectClassAttributesPassively": (
            "5.6",
            [
                "ObjectClassHandle theClass, AttributeHandleSet attributeList",
                "ObjectClassHandle theClass, AttributeHandleSet attributeList, String updateRateDesignator",
            ],
        ),
        "unsubscribeObjectClass": ("5.7", ["ObjectClassHandle theClass"]),
        "unsubscribeObjectClassAttributes": ("5.7", ["ObjectClassHandle theClass, AttributeHandleSet attributeList"]),
        "subscribeInteractionClass": ("5.8", ["InteractionClassHandle theClass"]),
        "subscribeInteractionClassPassively": ("5.8", ["InteractionClassHandle theClass"]),
        "unsubscribeInteractionClass": ("5.9", ["InteractionClassHandle theClass"]),
    }
    federate_checks = {
        "startRegistrationForObjectClass": ("5.10", ["ObjectClassHandle theClass"]),
        "stopRegistrationForObjectClass": ("5.11", ["ObjectClassHandle theClass"]),
        "turnInteractionsOn": ("5.12", ["InteractionClassHandle theHandle"]),
        "turnInteractionsOff": ("5.13", ["InteractionClassHandle theHandle"]),
    }

    for method_name, (service, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["FederateAmbassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params


def test_clause_6_service_and_callback_signature_metadata_matches_source_bindings():
    rti_checks = {
        "reserveObjectInstanceName": ("6.2", ["void"], ["String theObjectName"]),
        "releaseObjectInstanceName": ("6.4", ["void"], ["String theObjectInstanceName"]),
        "reserveMultipleObjectInstanceName": ("6.5", ["void"], ["Set<String> theObjectNames"]),
        "releaseMultipleObjectInstanceName": ("6.7", ["void"], ["Set<String> theObjectNames"]),
        "registerObjectInstance": (
            "6.8",
            ["ObjectInstanceHandle", "ObjectInstanceHandle"],
            [
                "ObjectClassHandle theClass",
                "ObjectClassHandle theClass, String theObjectName",
            ],
        ),
        "updateAttributeValues": (
            "6.10",
            ["void", "MessageRetractionReturn"],
            [
                "ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag",
                "ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, LogicalTime theTime",
            ],
        ),
        "sendInteraction": (
            "6.12",
            ["void", "MessageRetractionReturn"],
            [
                "InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, byte[] userSuppliedTag",
                "InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, LogicalTime theTime",
            ],
        ),
        "deleteObjectInstance": (
            "6.14",
            ["void", "MessageRetractionReturn"],
            [
                "ObjectInstanceHandle objectHandle, byte[] userSuppliedTag",
                "ObjectInstanceHandle objectHandle, byte[] userSuppliedTag, LogicalTime theTime",
            ],
        ),
        "localDeleteObjectInstance": ("6.16", ["void"], ["ObjectInstanceHandle objectHandle"]),
        "requestAttributeValueUpdate": (
            "6.19",
            ["void", "void"],
            [
                "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag",
                "ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag",
            ],
        ),
        "requestAttributeTransportationTypeChange": (
            "6.23",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, TransportationTypeHandle theType"],
        ),
        "queryAttributeTransportationType": (
            "6.25",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
        "requestInteractionTransportationTypeChange": (
            "6.27",
            ["void"],
            ["InteractionClassHandle theClass, TransportationTypeHandle theType"],
        ),
        "queryInteractionTransportationType": (
            "6.29",
            ["void"],
            ["FederateHandle theFederate, InteractionClassHandle theInteraction"],
        ),
    }
    federate_checks = {
        "objectInstanceNameReservationSucceeded": ("6.3", ["String objectName"]),
        "multipleObjectInstanceNameReservationSucceeded": ("6.6", ["Set<String> objectNames"]),
        "discoverObjectInstance": (
            "6.9",
            [
                "ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName",
                "ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName, FederateHandle producingFederate",
            ],
        ),
        "reflectAttributeValues": (
            "6.11",
            [
                "ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, SupplementalReflectInfo reflectInfo",
                "ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, SupplementalReflectInfo reflectInfo",
                "ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalReflectInfo reflectInfo",
            ],
        ),
        "receiveInteraction": (
            "6.13",
            [
                "InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, SupplementalReceiveInfo receiveInfo",
                "InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, SupplementalReceiveInfo receiveInfo",
                "InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalReceiveInfo receiveInfo",
            ],
        ),
        "removeObjectInstance": (
            "6.15",
            [
                "ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, SupplementalRemoveInfo removeInfo",
                "ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, LogicalTime theTime, OrderType receivedOrdering, SupplementalRemoveInfo removeInfo",
                "ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalRemoveInfo removeInfo",
            ],
        ),
        "attributesInScope": ("6.17", ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"]),
        "attributesOutOfScope": ("6.18", ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"]),
        "provideAttributeValueUpdate": (
            "6.20",
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"],
        ),
        "turnUpdatesOnForObjectInstance": (
            "6.21",
            [
                "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes",
                "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, String updateRateDesignator",
            ],
        ),
        "turnUpdatesOffForObjectInstance": (
            "6.22",
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "confirmAttributeTransportationTypeChange": (
            "6.24",
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, TransportationTypeHandle theTransportation"],
        ),
        "reportAttributeTransportationType": (
            "6.26",
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute, TransportationTypeHandle theTransportation"],
        ),
        "confirmInteractionTransportationTypeChange": (
            "6.28",
            ["InteractionClassHandle theInteraction, TransportationTypeHandle theTransportation"],
        ),
        "reportInteractionTransportationType": (
            "6.30",
            ["FederateHandle theFederate, InteractionClassHandle theInteraction, TransportationTypeHandle theTransportation"],
        ),
    }

    for method_name, (service, expected_returns, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["FederateAmbassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params


def test_clause_7_service_and_callback_signature_metadata_matches_source_bindings():
    rti_checks = {
        "unconditionalAttributeOwnershipDivestiture": (
            "7.2",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "negotiatedAttributeOwnershipDivestiture": (
            "7.3",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"],
        ),
        "confirmDivestiture": (
            "7.6",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"],
        ),
        "attributeOwnershipAcquisition": (
            "7.8",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet desiredAttributes, byte[] userSuppliedTag"],
        ),
        "attributeOwnershipAcquisitionIfAvailable": (
            "7.9",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet desiredAttributes"],
        ),
        "attributeOwnershipReleaseDenied": (
            "7.12",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "attributeOwnershipDivestitureIfWanted": (
            "7.13",
            ["AttributeHandleSet"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "cancelNegotiatedAttributeOwnershipDivestiture": (
            "7.14",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "cancelAttributeOwnershipAcquisition": (
            "7.15",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "queryAttributeOwnership": (
            "7.17",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
        "isAttributeOwnedByFederate": (
            "7.19",
            ["boolean"],
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
    }
    federate_checks = {
        "requestAttributeOwnershipAssumption": (
            "7.4",
            ["ObjectInstanceHandle theObject, AttributeHandleSet offeredAttributes, byte[] userSuppliedTag"],
        ),
        "requestDivestitureConfirmation": (
            "7.5",
            ["ObjectInstanceHandle theObject, AttributeHandleSet offeredAttributes"],
        ),
        "attributeOwnershipAcquisitionNotification": (
            "7.7",
            ["ObjectInstanceHandle theObject, AttributeHandleSet securedAttributes, byte[] userSuppliedTag"],
        ),
        "attributeOwnershipUnavailable": (
            "7.10",
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "requestAttributeOwnershipRelease": (
            "7.11",
            ["ObjectInstanceHandle theObject, AttributeHandleSet candidateAttributes, byte[] userSuppliedTag"],
        ),
        "confirmAttributeOwnershipAcquisitionCancellation": (
            "7.16",
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes"],
        ),
        "attributeIsNotOwned": (
            "7.18",
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
        "attributeIsOwnedByRTI": (
            "7.18",
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
        "informAttributeOwnership": (
            "7.18",
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute, FederateHandle theOwner"],
        ),
    }

    for method_name, (service, expected_returns, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["FederateAmbassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params


def test_clause_8_service_and_callback_signature_metadata_matches_source_bindings():
    rti_checks = {
        "enableTimeRegulation": ("8.2", ["void"], ["LogicalTimeInterval theLookahead"]),
        "disableTimeRegulation": ("8.4", ["void"], [""]),
        "enableTimeConstrained": ("8.5", ["void"], [""]),
        "disableTimeConstrained": ("8.7", ["void"], [""]),
        "timeAdvanceRequest": ("8.8", ["void"], ["LogicalTime theTime"]),
        "timeAdvanceRequestAvailable": ("8.9", ["void"], ["LogicalTime theTime"]),
        "nextMessageRequest": ("8.10", ["void"], ["LogicalTime theTime"]),
        "nextMessageRequestAvailable": ("8.11", ["void"], ["LogicalTime theTime"]),
        "flushQueueRequest": ("8.12", ["void"], ["LogicalTime theTime"]),
        "enableAsynchronousDelivery": ("8.14", ["void"], [""]),
        "disableAsynchronousDelivery": ("8.15", ["void"], [""]),
        "queryGALT": ("8.16", ["TimeQueryReturn"], [""]),
        "queryLogicalTime": ("8.17", ["LogicalTime"], [""]),
        "queryLITS": ("8.18", ["TimeQueryReturn"], [""]),
        "modifyLookahead": ("8.19", ["void"], ["LogicalTimeInterval theLookahead"]),
        "queryLookahead": ("8.20", ["LogicalTimeInterval"], [""]),
        "retract": ("8.21", ["void"], ["MessageRetractionHandle theHandle"]),
        "changeAttributeOrderType": (
            "8.23",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, OrderType theType"],
        ),
        "changeInteractionOrderType": (
            "8.24",
            ["void"],
            ["InteractionClassHandle theClass, OrderType theType"],
        ),
    }
    federate_checks = {
        "timeRegulationEnabled": ("8.3", ["LogicalTime time"]),
        "timeConstrainedEnabled": ("8.6", ["LogicalTime time"]),
        "timeAdvanceGrant": ("8.13", ["LogicalTime theTime"]),
        "requestRetraction": ("8.22", ["MessageRetractionHandle theHandle"]),
    }

    for method_name, (service, expected_returns, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["FederateAmbassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params


def test_clause_9_service_signature_metadata_matches_source_bindings():
    rti_checks = {
        "createRegion": ("9.2", ["RegionHandle"], ["DimensionHandleSet dimensions"]),
        "commitRegionModifications": ("9.3", ["void"], ["RegionHandleSet regions"]),
        "deleteRegion": ("9.4", ["void"], ["RegionHandle theRegion"]),
        "registerObjectInstanceWithRegions": (
            "9.5",
            ["ObjectInstanceHandle", "ObjectInstanceHandle"],
            [
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions",
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String theObject",
            ],
        ),
        "associateRegionsForUpdates": (
            "9.6",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeSetRegionSetPairList attributesAndRegions"],
        ),
        "unassociateRegionsForUpdates": (
            "9.7",
            ["void"],
            ["ObjectInstanceHandle theObject, AttributeSetRegionSetPairList attributesAndRegions"],
        ),
        "subscribeObjectClassAttributesPassivelyWithRegions": (
            "9.8",
            ["void", "void"],
            [
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions",
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String updateRateDesignator",
            ],
        ),
        "subscribeObjectClassAttributesWithRegions": (
            "9.8",
            ["void", "void"],
            [
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions",
                "ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String updateRateDesignator",
            ],
        ),
        "unsubscribeObjectClassAttributesWithRegions": (
            "9.9",
            ["void"],
            ["ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions"],
        ),
        "subscribeInteractionClassPassivelyWithRegions": (
            "9.10",
            ["void"],
            ["InteractionClassHandle theClass, RegionHandleSet regions"],
        ),
        "subscribeInteractionClassWithRegions": (
            "9.10",
            ["void"],
            ["InteractionClassHandle theClass, RegionHandleSet regions"],
        ),
        "unsubscribeInteractionClassWithRegions": (
            "9.11",
            ["void"],
            ["InteractionClassHandle theClass, RegionHandleSet regions"],
        ),
        "sendInteractionWithRegions": (
            "9.12",
            ["void", "MessageRetractionReturn"],
            [
                "InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, RegionHandleSet regions, byte[] userSuppliedTag",
                "InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, RegionHandleSet regions, byte[] userSuppliedTag, LogicalTime theTime",
            ],
        ),
        "requestAttributeValueUpdateWithRegions": (
            "9.13",
            ["void"],
            ["ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, byte[] userSuppliedTag"],
        ),
    }

    for method_name, (service, expected_returns, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params


@pytest.mark.requirements(*CLAUSE9_MOM_SERVICE_REPORT_REQUIREMENTS)
def test_clause_9_services_are_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("ddm-mom-service-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "ddm-mom-service-report-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    dim = owner.getDimensionHandle("HLAdefaultRoutingSpace")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")

    set_reporting = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.getParameterHandle(set_reporting, "HLAfederate")
    sr_state = owner.getParameterHandle(set_reporting, "HLAreportingState")
    report_service = witness.getParameterHandle(service_report, "HLAservice")
    report_success = witness.getParameterHandle(service_report, "HLAsuccessIndicator")

    witness.subscribeInteractionClass(service_report)
    owner.sendInteraction(
        set_reporting,
        {
            sr_fed: owner.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
        },
        b"enable-ddm-owner-service-reporting",
    )
    drain(owner, observer, witness)
    assert owner.backend.state.service_reporting is True

    owner.publishObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)

    region = owner.createRegion({dim})
    owner.setRangeBounds(region, dim, RangeBounds(10, 20))
    owner.commitRegionModifications({region})
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))]

    obj = owner.registerObjectInstanceWithRegions(cls, pairs, "DDM-MOM-Object")
    owner.unassociateRegionsForUpdates(obj, pairs)
    owner.associateRegionsForUpdates(obj, pairs)
    owner.subscribeObjectClassAttributesPassivelyWithRegions(cls, pairs)
    owner.subscribeObjectClassAttributesWithRegions(cls, pairs)
    owner.unsubscribeObjectClassAttributesWithRegions(cls, pairs)
    owner.subscribeInteractionClassPassivelyWithRegions(interaction, {region})
    owner.subscribeInteractionClassWithRegions(interaction, {region})
    owner.unsubscribeInteractionClassWithRegions(interaction, {region})
    owner.sendInteractionWithRegions(interaction, {track_id: b"ddm-mom-track"}, {region}, b"ddm-mom-send")
    owner.requestAttributeValueUpdateWithRegions(cls, pairs, b"ddm-mom-refresh")
    owner.deleteRegion(region)
    drain(owner, observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    service_names = [hla_mom.decode_text(rec.args[1][report_service]) for rec in reports]
    success_values = [hla_mom.decode_bool(rec.args[1][report_success]) for rec in reports]

    assert success_values and all(success_values)
    assert set(service_names) >= {
        "createRegion",
        "commitRegionModifications",
        "deleteRegion",
        "registerObjectInstanceWithRegions",
        "associateRegionsForUpdates",
        "unassociateRegionsForUpdates",
        "subscribeObjectClassAttributesPassivelyWithRegions",
        "subscribeObjectClassAttributesWithRegions",
        "unsubscribeObjectClassAttributesWithRegions",
        "subscribeInteractionClassPassivelyWithRegions",
        "subscribeInteractionClassWithRegions",
        "unsubscribeInteractionClassWithRegions",
        "sendInteractionWithRegions",
        "requestAttributeValueUpdateWithRegions",
    }

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("ddm-mom-service-report-fed")


def test_clause_10_service_signature_metadata_matches_source_bindings():
    rti_checks = {
        "getAutomaticResignDirective": ("10.2", ["ResignAction"], [""]),
        "setAutomaticResignDirective": ("10.3", ["void"], ["ResignAction resignAction"]),
        "getFederateHandle": ("10.4", ["FederateHandle"], ["String theName"]),
        "getFederateName": ("10.5", ["String"], ["FederateHandle theHandle"]),
        "getObjectClassHandle": ("10.6", ["ObjectClassHandle"], ["String theName"]),
        "getObjectClassName": ("10.7", ["String"], ["ObjectClassHandle theHandle"]),
        "getKnownObjectClassHandle": ("10.8", ["ObjectClassHandle"], ["ObjectInstanceHandle theObject"]),
        "getObjectInstanceHandle": ("10.9", ["ObjectInstanceHandle"], ["String theName"]),
        "getObjectInstanceName": ("10.10", ["String"], ["ObjectInstanceHandle theHandle"]),
        "getAttributeHandle": (
            "10.11",
            ["AttributeHandle"],
            ["ObjectClassHandle whichClass, String theName"],
        ),
        "getAttributeName": (
            "10.12",
            ["String"],
            ["ObjectClassHandle whichClass, AttributeHandle theHandle"],
        ),
        "getUpdateRateValue": ("10.13", ["double"], ["String updateRateDesignator"]),
        "getUpdateRateValueForAttribute": (
            "10.14",
            ["double"],
            ["ObjectInstanceHandle theObject, AttributeHandle theAttribute"],
        ),
        "getInteractionClassHandle": ("10.15", ["InteractionClassHandle"], ["String theName"]),
        "getInteractionClassName": ("10.16", ["String"], ["InteractionClassHandle theHandle"]),
        "getParameterHandle": (
            "10.17",
            ["ParameterHandle"],
            ["InteractionClassHandle whichClass, String theName"],
        ),
        "getParameterName": (
            "10.18",
            ["String"],
            ["InteractionClassHandle whichClass, ParameterHandle theHandle"],
        ),
        "getOrderType": ("10.19", ["OrderType"], ["String theName"]),
        "getOrderName": ("10.20", ["String"], ["OrderType theType"]),
        "getTransportationTypeHandle": (
            "10.21",
            ["TransportationTypeHandle"],
            ["String theName"],
        ),
        "getTransportationTypeName": (
            "10.22",
            ["String"],
            ["TransportationTypeHandle theHandle"],
        ),
        "getAvailableDimensionsForClassAttribute": (
            "10.23",
            ["DimensionHandleSet"],
            ["ObjectClassHandle whichClass, AttributeHandle theHandle"],
        ),
        "getAvailableDimensionsForInteractionClass": (
            "10.24",
            ["DimensionHandleSet"],
            ["InteractionClassHandle theHandle"],
        ),
        "getDimensionHandle": ("10.25", ["DimensionHandle"], ["String theName"]),
        "getDimensionName": ("10.26", ["String"], ["DimensionHandle theHandle"]),
        "getDimensionUpperBound": ("10.27", ["long"], ["DimensionHandle theHandle"]),
        "getDimensionHandleSet": ("10.28", ["DimensionHandleSet"], ["RegionHandle region"]),
        "getRangeBounds": (
            "10.29",
            ["RangeBounds"],
            ["RegionHandle region, DimensionHandle dimension"],
        ),
        "setRangeBounds": (
            "10.30",
            ["void"],
            ["RegionHandle region, DimensionHandle dimension, RangeBounds bounds"],
        ),
        "normalizeFederateHandle": ("10.31", ["long"], ["FederateHandle federateHandle"]),
        "normalizeServiceGroup": ("10.32", ["long"], ["ServiceGroup group"]),
        "enableObjectClassRelevanceAdvisorySwitch": ("10.33", ["void"], [""]),
        "disableObjectClassRelevanceAdvisorySwitch": ("10.34", ["void"], [""]),
        "enableAttributeRelevanceAdvisorySwitch": ("10.35", ["void"], [""]),
        "disableAttributeRelevanceAdvisorySwitch": ("10.36", ["void"], [""]),
        "enableAttributeScopeAdvisorySwitch": ("10.37", ["void"], [""]),
        "disableAttributeScopeAdvisorySwitch": ("10.38", ["void"], [""]),
        "enableInteractionRelevanceAdvisorySwitch": ("10.39", ["void"], [""]),
        "disableInteractionRelevanceAdvisorySwitch": ("10.40", ["void"], [""]),
        "evokeCallback": ("10.41", ["boolean"], ["double approximateMinimumTimeInSeconds"]),
        "evokeMultipleCallbacks": (
            "10.42",
            ["boolean"],
            ["double approximateMinimumTimeInSeconds, double approximateMaximumTimeInSeconds"],
        ),
        "enableCallbacks": ("10.43", ["void"], [""]),
        "disableCallbacks": ("10.44", ["void"], [""]),
    }

    for method_name, (service, expected_returns, expected_params) in rti_checks.items():
        assert hasattr(RTIambassadorSpec, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params


def test_clause_6_federate_initiated_services_validate_core_argument_shapes():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("om-arg-validation-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = owner.getParameterHandle(interaction, "TrackId")

    bad_class = type(cls)(cls.value + 1000)
    bad_attr = type(attr)(attr.value + 1000)
    bad_interaction = type(interaction)(interaction.value + 1000)
    bad_param = type(track_id)(track_id.value + 1000)

    owner.publishObjectClassAttributes(cls, {attr})
    owner.publishInteractionClass(interaction)
    obj = owner.registerObjectInstance(cls, "OM-Arg-Validation")

    with pytest.raises(InvalidObjectClassHandle):
        owner.registerObjectInstance(bad_class, "bad-class")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.updateAttributeValues(ObjectInstanceHandle(999), {attr: b"x"}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.updateAttributeValues(obj, {bad_attr: b"x"}, b"tag")

    with pytest.raises(InvalidInteractionClassHandle):
        owner.sendInteraction(bad_interaction, {track_id: b"x"}, b"tag")
    with pytest.raises(InteractionParameterNotDefined):
        owner.sendInteraction(interaction, {bad_param: b"x"}, b"tag")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.deleteObjectInstance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(ObjectInstanceNotKnown):
        owner.localDeleteObjectInstance(ObjectInstanceHandle(999))

    with pytest.raises(ObjectInstanceNotKnown):
        owner.requestAttributeValueUpdate(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.requestAttributeValueUpdate(obj, {bad_attr}, b"tag")
    with pytest.raises(InvalidObjectClassHandle):
        owner.requestAttributeValueUpdate(bad_class, {attr}, b"tag")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.requestAttributeTransportationTypeChange(
            ObjectInstanceHandle(999),
            {attr},
            owner.backend.engine.transportation_reliable,
        )
    with pytest.raises(AttributeNotDefined):
        owner.requestAttributeTransportationTypeChange(
            obj,
            {bad_attr},
            owner.backend.engine.transportation_reliable,
        )
    with pytest.raises(ObjectInstanceNotKnown):
        owner.queryAttributeTransportationType(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.queryAttributeTransportationType(obj, bad_attr)

    with pytest.raises(InvalidInteractionClassHandle):
        owner.requestInteractionTransportationTypeChange(
            bad_interaction,
            owner.backend.engine.transportation_reliable,
        )

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("om-arg-validation-fed")


def test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.updateAttributeValues(ObjectInstanceHandle(999), {}, b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.updateAttributeValues(ObjectInstanceHandle(999), {}, b"tag")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("update-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    observer.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Update-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.updateAttributeValues(ObjectInstanceHandle(999), {attr: b"x"}, b"tag")
    with pytest.raises(AttributeNotOwned):
        observer.updateAttributeValues(obj, {attr: b"x"}, b"tag")

    owner.requestFederationSave("UPDATE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.updateAttributeValues(obj, {attr: b"x"}, b"tag")

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("UPDATE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.updateAttributeValues(obj, {attr: b"x"}, b"tag")

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("update-negative-fed")


def test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.deleteObjectInstance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(NotConnected):
        rti.localDeleteObjectInstance(ObjectInstanceHandle(999))

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.deleteObjectInstance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(FederateNotExecutionMember):
        rti.localDeleteObjectInstance(ObjectInstanceHandle(999))
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("delete-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    observer.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Delete-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.deleteObjectInstance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(DeletePrivilegeNotHeld):
        observer.deleteObjectInstance(obj, b"tag")
    with pytest.raises(FederateOwnsAttributes):
        owner.localDeleteObjectInstance(obj)

    owner.requestFederationSave("DELETE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.deleteObjectInstance(obj, b"tag")
    with pytest.raises(SaveInProgress):
        owner.localDeleteObjectInstance(obj)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("DELETE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.deleteObjectInstance(obj, b"tag")
    with pytest.raises(RestoreInProgress):
        owner.localDeleteObjectInstance(obj)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("delete-negative-fed")


def test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestAttributeValueUpdate(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestAttributeValueUpdate(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("ravu-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.requestFederationSave("RAVU-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.requestAttributeValueUpdate(cls, {attr}, b"tag")

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("RAVU-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.requestAttributeValueUpdate(cls, {attr}, b"tag")

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("ravu-negative-fed")


def test_request_interaction_transportation_type_change_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestInteractionTransportationTypeChange(object(), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestInteractionTransportationTypeChange(object(), object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("interaction-transport-negative-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    owner_fed.clear()
    owner.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        owner.requestInteractionTransportationTypeChange(interaction, owner.backend.engine.transportation_reliable)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.requestInteractionTransportationTypeChange(type(interaction)(interaction.value + 1000), owner.backend.engine.transportation_reliable)
    owner.backend.config.strict_interaction_publication = False
    owner.publishInteractionClass(interaction)
    with pytest.raises(InvalidTransportationType):
        owner.requestInteractionTransportationTypeChange(interaction, TransportationTypeHandle(999))
    assert owner_fed.callbacks_named("confirmInteractionTransportationTypeChange") == []

    owner.requestFederationSave("INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.requestInteractionTransportationTypeChange(interaction, owner.backend.engine.transportation_reliable)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.requestInteractionTransportationTypeChange(interaction, owner.backend.engine.transportation_reliable)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("interaction-transport-negative-fed")


def test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.queryAttributeTransportationType(ObjectInstanceHandle(999), object())
    with pytest.raises(NotConnected):
        rti.reserveMultipleObjectInstanceName(set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.queryAttributeTransportationType(ObjectInstanceHandle(999), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.reserveMultipleObjectInstanceName(set())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("query-transport-reserve-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "QueryTransport")
    owner_fed.clear()

    with pytest.raises(ObjectInstanceNotKnown):
        owner.queryAttributeTransportationType(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.queryAttributeTransportationType(obj, type(attr)(attr.value + 1000))
    assert owner_fed.callbacks_named("reportAttributeTransportationType") == []

    owner.requestFederationSave("QUERY-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.queryAttributeTransportationType(obj, attr)
    with pytest.raises(SaveInProgress):
        owner.reserveMultipleObjectInstanceName({"A", "B"})

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("QUERY-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.queryAttributeTransportationType(obj, attr)
    with pytest.raises(RestoreInProgress):
        owner.reserveMultipleObjectInstanceName({"A", "B"})

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("query-transport-reserve-negative-fed")


def test_query_interaction_transportation_type_rejects_not_connected_not_joined_invalid_handle_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.queryInteractionTransportationType(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.queryInteractionTransportationType(object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("query-interaction-transport-negative-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    owner_fed.clear()

    with pytest.raises(InvalidInteractionClassHandle):
        owner.queryInteractionTransportationType(type(interaction)(interaction.value + 1000))
    assert owner_fed.callbacks_named("reportInteractionTransportationType") == []

    owner.queryInteractionTransportationType(interaction)
    drain(owner, observer)
    report = owner_fed.last_callback("reportInteractionTransportationType")
    assert report is not None
    assert report.args == (owner.backend.state.handle, interaction, owner.backend.engine.transportation_reliable)
    owner_fed.clear()

    owner.requestFederationSave("QUERY-INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.queryInteractionTransportationType(interaction)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("QUERY-INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.queryInteractionTransportationType(interaction)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("query-interaction-transport-negative-fed")


def test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.releaseObjectInstanceName("name")
    with pytest.raises(NotConnected):
        rti.releaseMultipleObjectInstanceName({"a", "b"})

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.releaseObjectInstanceName("name")
    with pytest.raises(FederateNotExecutionMember):
        rti.releaseMultipleObjectInstanceName({"a", "b"})
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("release-query-interaction-negative-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    owner.requestFederationSave("REL-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.releaseObjectInstanceName("name")
    with pytest.raises(SaveInProgress):
        owner.releaseMultipleObjectInstanceName({"a", "b"})
    with pytest.raises(SaveInProgress):
        owner.queryInteractionTransportationType(interaction)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("REL-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.releaseObjectInstanceName("name")
    with pytest.raises(RestoreInProgress):
        owner.releaseMultipleObjectInstanceName({"a", "b"})
    with pytest.raises(RestoreInProgress):
        owner.queryInteractionTransportationType(interaction)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("release-query-interaction-negative-fed")


def test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.registerObjectInstance(object(), "bad")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.registerObjectInstance(object(), "bad")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("register-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    owner.registerObjectInstance(cls, "Duplicate-Object")
    with pytest.raises(ObjectInstanceNameInUse):
        owner.registerObjectInstance(cls, "Duplicate-Object")

    owner.requestFederationSave("REGISTER-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.registerObjectInstance(cls, "Blocked-Object")

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("REGISTER-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.registerObjectInstance(cls, "Blocked-Restore-Object")

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("register-negative-fed")


def test_python_rti_negotiated_ownership_tracks_divesting_and_candidate_flows():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("negotiated-ownership-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    acquirer.subscribeObjectClassAttributes(cls, {attr})

    offered = owner.registerObjectInstance(cls, "Negotiated-1")
    drain(owner, acquirer)
    assert acquirer_fed.last_callback("discoverObjectInstance") is not None

    owner.negotiatedAttributeOwnershipDivestiture(offered, {attr}, b"offer-tag")
    drain(owner, acquirer)
    assumption = acquirer_fed.last_callback("requestAttributeOwnershipAssumption")
    assert assumption is not None
    assert assumption.args == (offered, AttributeHandleSet({attr}), b"offer-tag")
    assert owner.isAttributeOwnedByFederate(offered, attr) is True

    acquirer.attributeOwnershipAcquisition(offered, {attr}, b"acquire-tag")
    drain(owner, acquirer)
    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (offered, AttributeHandleSet({attr}), b"acquire-tag")
    divest_notice = owner_fed.last_callback("requestDivestitureConfirmation")
    assert divest_notice is not None
    assert divest_notice.args == (offered, AttributeHandleSet({attr}))
    assert acquirer.isAttributeOwnedByFederate(offered, attr) is True

    pending = owner.registerObjectInstance(cls, "Pending-1")
    drain(owner, acquirer)
    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"request-tag")
    drain(owner, acquirer)
    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"request-tag")
    acquirer.cancelAttributeOwnershipAcquisition(pending, {attr})
    drain(owner, acquirer)
    cancelled = acquirer_fed.last_callback("confirmAttributeOwnershipAcquisitionCancellation")
    assert cancelled is not None
    assert cancelled.args == (pending, AttributeHandleSet({attr}))

    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"retry-tag")
    drain(owner, acquirer)
    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"retry-tag")
    divested = owner.attributeOwnershipDivestitureIfWanted(pending, {attr})
    assert divested == AttributeHandleSet({attr})
    drain(owner, acquirer)
    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (pending, AttributeHandleSet({attr}), b"")
    assert acquirer.isAttributeOwnedByFederate(pending, attr) is True

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("negotiated-ownership-fed")


@pytest.mark.requirements(*CLAUSE7_NEGOTIATED_CALLBACK_SEQUENCE_REQUIREMENTS)
def test_ownership_callback_sequences_and_payloads_are_exact_for_negotiated_and_cancellation_flows():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("ownership-callback-sequence-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    acquirer.subscribeObjectClassAttributes(cls, {attr})

    offered = owner.registerObjectInstance(cls, "Callback-Offered-1")
    drain(owner, acquirer)
    owner_fed.clear()
    acquirer_fed.clear()

    owner.negotiatedAttributeOwnershipDivestiture(offered, {attr}, b"offer-tag")
    drain(owner, acquirer)
    assumption_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "requestAttributeOwnershipAssumption"
    ]
    assert [rec.method_name for rec in assumption_callbacks] == ["requestAttributeOwnershipAssumption"]
    assert assumption_callbacks[0].args == (offered, AttributeHandleSet({attr}), b"offer-tag")

    owner_fed.clear()
    acquirer_fed.clear()
    acquirer.attributeOwnershipAcquisition(offered, {attr}, b"acquire-tag")
    drain(owner, acquirer)

    divest_callbacks = [
        rec for rec in owner_fed.records if rec.method_name == "requestDivestitureConfirmation"
    ]
    acquisition_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "attributeOwnershipAcquisitionNotification"
    ]
    assert [rec.method_name for rec in divest_callbacks] == ["requestDivestitureConfirmation"]
    assert [rec.method_name for rec in acquisition_callbacks] == ["attributeOwnershipAcquisitionNotification"]
    assert divest_callbacks[0].args == (offered, AttributeHandleSet({attr}))
    assert acquisition_callbacks[0].args == (offered, AttributeHandleSet({attr}), b"acquire-tag")

    pending = owner.registerObjectInstance(cls, "Callback-Pending-1")
    drain(owner, acquirer)
    owner_fed.clear()
    acquirer_fed.clear()

    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"request-tag")
    drain(owner, acquirer)
    release_callbacks = [
        rec for rec in owner_fed.records if rec.method_name == "requestAttributeOwnershipRelease"
    ]
    assert [rec.method_name for rec in release_callbacks] == ["requestAttributeOwnershipRelease"]
    assert release_callbacks[0].args == (pending, AttributeHandleSet({attr}), b"request-tag")

    owner_fed.clear()
    acquirer_fed.clear()
    acquirer.cancelAttributeOwnershipAcquisition(pending, {attr})
    drain(owner, acquirer)
    cancellation_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "confirmAttributeOwnershipAcquisitionCancellation"
    ]
    assert [rec.method_name for rec in cancellation_callbacks] == [
        "confirmAttributeOwnershipAcquisitionCancellation"
    ]
    assert cancellation_callbacks[0].args == (pending, AttributeHandleSet({attr}))

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("ownership-callback-sequence-fed")


def test_negotiated_attribute_ownership_divestiture_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.negotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.negotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("negotiated-divest-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Negotiated-Divest-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.negotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.negotiatedAttributeOwnershipDivestiture(obj, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotOwned):
        acquirer.negotiatedAttributeOwnershipDivestiture(obj, {attr}, b"tag")
    owner.negotiatedAttributeOwnershipDivestiture(obj, {attr}, b"tag")
    with pytest.raises(AttributeAlreadyBeingDivested):
        owner.negotiatedAttributeOwnershipDivestiture(obj, {attr}, b"tag")

    owner.requestFederationSave("NEGOTIATED-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.negotiatedAttributeOwnershipDivestiture(obj, {attr}, b"tag")

    owner.federateSaveBegun()
    acquirer.federateSaveBegun()
    owner.federateSaveComplete()
    acquirer.federateSaveComplete()
    drain(owner, acquirer)

    owner.requestFederationRestore("NEGOTIATED-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.negotiatedAttributeOwnershipDivestiture(obj, {attr}, b"tag")

    owner.abortFederationRestore()
    drain(owner, acquirer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("negotiated-divest-negative-fed")


def test_confirm_divestiture_rejects_not_connected_not_joined_unknown_object_and_not_owned():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.confirmDivestiture(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.confirmDivestiture(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("confirm-divestiture-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    acquired = owner.registerObjectInstance(cls, "Confirm-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.confirmDivestiture(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.confirmDivestiture(acquired, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotOwned):
        acquirer.confirmDivestiture(acquired, {attr}, b"tag")

    owner.negotiatedAttributeOwnershipDivestiture(acquired, {attr}, b"divest-tag")
    federation = owner.backend.engine.federations["confirm-divestiture-negative-fed"]
    federation.objects[acquired].attribute_candidates[attr] = {acquirer.backend.state.handle}

    owner.requestFederationSave("CONFIRM-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.confirmDivestiture(acquired, {attr}, b"tag")
    owner.federateSaveBegun()
    acquirer.federateSaveBegun()
    owner.federateSaveComplete()
    acquirer.federateSaveComplete()
    drain(owner, acquirer)
    owner.requestFederationRestore("CONFIRM-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.confirmDivestiture(acquired, {attr}, b"tag")
    owner.abortFederationRestore()
    drain(owner, acquirer)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("confirm-divestiture-negative-fed")


def test_python_rti_confirm_divestiture_requires_divesting_request_and_candidate():
    engine, owner, acquirer, _owner_fed, acquirer_fed, _h1, h2 = joined_pair("confirm-divestiture-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    acquirer.subscribeObjectClassAttributes(cls, {attr})

    offered = owner.registerObjectInstance(cls, "Confirm-1")
    drain(owner, acquirer)

    try:
        owner.confirmDivestiture(offered, {attr}, b"confirm-tag")
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("confirm_divestiture should require prior negotiated divestiture")

    owner.negotiatedAttributeOwnershipDivestiture(offered, {attr}, b"offer-tag")
    drain(owner, acquirer)

    try:
        owner.confirmDivestiture(offered, {attr}, b"confirm-tag")
    except NoAcquisitionPending:
        pass
    else:
        raise AssertionError("confirm_divestiture should require a pending acquisition candidate")

    federation = engine.federations["confirm-divestiture-fed"]
    federation.objects[offered].attribute_candidates[attr] = {h2}
    owner.confirmDivestiture(offered, {attr}, b"confirm-tag")
    drain(owner, acquirer)

    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (offered, AttributeHandleSet({attr}), b"confirm-tag")
    assert acquirer.isAttributeOwnedByFederate(offered, attr) is True

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("confirm-divestiture-fed")


def test_attribute_ownership_acquisition_services_reject_not_connected_not_joined_unknown_object_and_owned_attributes():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.attributeOwnershipAcquisition(ObjectInstanceHandle(999), set(), b"tag")
    with pytest.raises(NotConnected):
        rti.attributeOwnershipAcquisitionIfAvailable(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.attributeOwnershipAcquisition(ObjectInstanceHandle(999), set(), b"tag")
    with pytest.raises(FederateNotExecutionMember):
        rti.attributeOwnershipAcquisitionIfAvailable(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("acquisition-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    rcs = owner.getAttributeHandle(cls, "RCS")
    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    held = owner.registerObjectInstance(cls, "Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attributeOwnershipAcquisition(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attributeOwnershipAcquisitionIfAvailable(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        acquirer.attributeOwnershipAcquisition(held, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotDefined):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {type(attr)(attr.value + 1000)})
    with pytest.raises(FederateOwnsAttributes):
        owner.attributeOwnershipAcquisition(held, {attr}, b"tag")
    with pytest.raises(FederateOwnsAttributes):
        owner.attributeOwnershipAcquisitionIfAvailable(held, {attr})

    acquirer.attributeOwnershipAcquisitionIfAvailable(held, {attr})
    with pytest.raises(AttributeAlreadyBeingAcquired):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {attr})

    acquirer.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        acquirer.attributeOwnershipAcquisition(held, {rcs}, b"tag")
    with pytest.raises(AttributeNotPublished):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {rcs})
    acquirer.backend.config.strict_object_publication = False
    acquirer.unpublishObjectClass(cls)
    with pytest.raises(ObjectClassNotPublished):
        acquirer.attributeOwnershipAcquisition(held, {attr}, b"tag")
    with pytest.raises(ObjectClassNotPublished):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})

    acquirer.requestFederationSave("ACQUIRE-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        acquirer.attributeOwnershipAcquisition(held, {attr}, b"tag")
    with pytest.raises(SaveInProgress):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {attr})
    acquirer.federateSaveBegun()
    owner.federateSaveBegun()
    acquirer.federateSaveComplete()
    owner.federateSaveComplete()
    drain(owner, acquirer)
    acquirer.requestFederationRestore("ACQUIRE-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        acquirer.attributeOwnershipAcquisition(held, {attr}, b"tag")
    with pytest.raises(RestoreInProgress):
        acquirer.attributeOwnershipAcquisitionIfAvailable(held, {attr})

    acquirer.abortFederationRestore()
    drain(owner, acquirer)
    owner.attributeOwnershipReleaseDenied(held, {attr})
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("acquisition-negative-fed")


def test_python_rti_attribute_ownership_release_denied_clears_pending_acquisition():
    _, owner, acquirer, owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("release-denied-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})

    pending = owner.registerObjectInstance(cls, "Denied-1")
    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"deny-tag")
    drain(owner, acquirer)

    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"deny-tag")

    owner.attributeOwnershipReleaseDenied(pending, {attr})

    try:
        acquirer.cancelAttributeOwnershipAcquisition(pending, {attr})
    except AttributeAcquisitionWasNotRequested:
        pass
    else:
        raise AssertionError("release denial should clear the pending acquisition request")

    owner.unconditionalAttributeOwnershipDivestiture(pending, {attr})
    assert owner.isAttributeOwnedByFederate(pending, attr) is False
    assert acquirer.isAttributeOwnedByFederate(pending, attr) is False

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("release-denied-fed")


def test_attribute_ownership_release_denied_and_divestiture_if_wanted_reject_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.attributeOwnershipReleaseDenied(ObjectInstanceHandle(999), set())
    with pytest.raises(NotConnected):
        rti.attributeOwnershipDivestitureIfWanted(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.attributeOwnershipReleaseDenied(ObjectInstanceHandle(999), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.attributeOwnershipDivestitureIfWanted(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("release-divest-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Release-Divest-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.attributeOwnershipReleaseDenied(ObjectInstanceHandle(999), {attr})
    with pytest.raises(ObjectInstanceNotKnown):
        owner.attributeOwnershipDivestitureIfWanted(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.attributeOwnershipReleaseDenied(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotDefined):
        owner.attributeOwnershipDivestitureIfWanted(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        acquirer.attributeOwnershipReleaseDenied(obj, {attr})
    with pytest.raises(AttributeNotOwned):
        acquirer.attributeOwnershipDivestitureIfWanted(obj, {attr})

    owner.requestFederationSave("RELEASE-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.attributeOwnershipReleaseDenied(obj, {attr})
    with pytest.raises(SaveInProgress):
        owner.attributeOwnershipDivestitureIfWanted(obj, {attr})

    owner.federateSaveBegun()
    acquirer.federateSaveBegun()
    owner.federateSaveComplete()
    acquirer.federateSaveComplete()
    drain(owner, acquirer)

    owner.requestFederationRestore("RELEASE-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.attributeOwnershipReleaseDenied(obj, {attr})
    with pytest.raises(RestoreInProgress):
        owner.attributeOwnershipDivestitureIfWanted(obj, {attr})

    owner.abortFederationRestore()
    drain(owner, acquirer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("release-divest-negative-fed")


def test_unconditional_divestiture_query_ownership_and_is_owned_reject_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unconditionalAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set())
    with pytest.raises(NotConnected):
        rti.queryAttributeOwnership(ObjectInstanceHandle(999), object())
    with pytest.raises(NotConnected):
        rti.isAttributeOwnedByFederate(ObjectInstanceHandle(999), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unconditionalAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.queryAttributeOwnership(ObjectInstanceHandle(999), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.isAttributeOwnedByFederate(ObjectInstanceHandle(999), object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("ownership-query-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "OwnershipQuery")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.unconditionalAttributeOwnershipDivestiture(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.unconditionalAttributeOwnershipDivestiture(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        observer.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    with pytest.raises(ObjectInstanceNotKnown):
        owner.queryAttributeOwnership(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.queryAttributeOwnership(obj, type(attr)(attr.value + 1000))
    with pytest.raises(ObjectInstanceNotKnown):
        owner.isAttributeOwnedByFederate(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.isAttributeOwnedByFederate(obj, type(attr)(attr.value + 1000))

    owner.requestFederationSave("OWNERSHIP-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    with pytest.raises(SaveInProgress):
        owner.queryAttributeOwnership(obj, attr)
    with pytest.raises(SaveInProgress):
        owner.isAttributeOwnedByFederate(obj, attr)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("OWNERSHIP-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    with pytest.raises(RestoreInProgress):
        owner.queryAttributeOwnership(obj, attr)
    with pytest.raises(RestoreInProgress):
        owner.isAttributeOwnedByFederate(obj, attr)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("ownership-query-negative-fed")


def test_cancel_negotiated_divestiture_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.cancelNegotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.cancelNegotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-negotiated-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Cancel-Negotiated-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.cancelNegotiatedAttributeOwnershipDivestiture(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.cancelNegotiatedAttributeOwnershipDivestiture(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        acquirer.cancelNegotiatedAttributeOwnershipDivestiture(obj, {attr})

    owner.requestFederationSave("CANCEL-NEGOTIATED-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.cancelNegotiatedAttributeOwnershipDivestiture(obj, {attr})

    owner.federateSaveBegun()
    acquirer.federateSaveBegun()
    owner.federateSaveComplete()
    acquirer.federateSaveComplete()
    drain(owner, acquirer)

    owner.requestFederationRestore("CANCEL-NEGOTIATED-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.cancelNegotiatedAttributeOwnershipDivestiture(obj, {attr})

    owner.abortFederationRestore()
    drain(owner, acquirer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("cancel-negotiated-negative-fed")


def test_python_rti_cancel_negotiated_divestiture_requires_active_request():
    _, owner, acquirer, owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-negotiated-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.subscribeObjectClassAttributes(cls, {attr})
    offered = owner.registerObjectInstance(cls, "Cancel-1")
    drain(owner, acquirer)

    try:
        owner.cancelNegotiatedAttributeOwnershipDivestiture(offered, {attr})
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("cancel_negotiated_attribute_ownership_divestiture should require an active request")

    owner.negotiatedAttributeOwnershipDivestiture(offered, {attr}, b"cancel-tag")
    drain(owner, acquirer)
    assert owner_fed.last_callback("requestDivestitureConfirmation") is None

    owner.cancelNegotiatedAttributeOwnershipDivestiture(offered, {attr})
    try:
        owner.confirmDivestiture(offered, {attr}, b"confirm-tag")
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("cancelled negotiated divestiture should clear the divesting state")

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("cancel-negotiated-fed")


def test_python_rti_acquisition_if_available_reports_unavailable_without_transfer():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("acquire-if-available-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    offered = owner.registerObjectInstance(cls, "Unavailable-1")

    acquirer.attributeOwnershipAcquisitionIfAvailable(offered, {attr})
    drain(owner, acquirer)

    unavailable = acquirer_fed.last_callback("attributeOwnershipUnavailable")
    assert unavailable is not None
    assert unavailable.args == (offered, AttributeHandleSet({attr}))
    assert owner.isAttributeOwnedByFederate(offered, attr) is True
    assert acquirer.isAttributeOwnedByFederate(offered, attr) is False
    assert owner_fed.last_callback("requestAttributeOwnershipRelease") is None

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("acquire-if-available-fed")


def test_python_rti_divestiture_if_wanted_requires_pending_acquirer():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("divest-if-wanted-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    pending = owner.registerObjectInstance(cls, "Wanted-1")

    try:
        owner.attributeOwnershipDivestitureIfWanted(pending, {attr})
    except NoAcquisitionPending:
        pass
    else:
        raise AssertionError("attribute_ownership_divestiture_if_wanted should require a pending acquisition")

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("divest-if-wanted-fed")


def test_python_rti_cancel_attribute_ownership_acquisition_requires_request():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-acquisition-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    pending = owner.registerObjectInstance(cls, "CancelAcquire-1")

    try:
        acquirer.cancelAttributeOwnershipAcquisition(pending, {attr})
    except AttributeAcquisitionWasNotRequested:
        pass
    else:
        raise AssertionError("cancel_attribute_ownership_acquisition should require an outstanding request")

    with pytest.raises(AttributeAlreadyOwned):
        owner.cancelAttributeOwnershipAcquisition(pending, {attr})

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("cancel-acquisition-fed")


def test_cancel_attribute_ownership_acquisition_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.cancelAttributeOwnershipAcquisition(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.cancelAttributeOwnershipAcquisition(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-acquisition-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Cancel-Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.cancelAttributeOwnershipAcquisition(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        acquirer.cancelAttributeOwnershipAcquisition(obj, {bad_attr})

    owner.requestFederationSave("CANCEL-ACQ-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        acquirer.cancelAttributeOwnershipAcquisition(obj, {attr})

    owner.federateSaveBegun()
    acquirer.federateSaveBegun()
    owner.federateSaveComplete()
    acquirer.federateSaveComplete()
    drain(owner, acquirer)

    owner.requestFederationRestore("CANCEL-ACQ-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        acquirer.cancelAttributeOwnershipAcquisition(obj, {attr})

    owner.abortFederationRestore()
    drain(owner, acquirer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("cancel-acquisition-negative-fed")


def test_python_rti_query_attribute_ownership_reports_not_owned_after_divestiture():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("query-unowned-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Unowned-1")
    owner.unconditionalAttributeOwnershipDivestiture(obj, {attr})

    observer.queryAttributeOwnership(obj, attr)
    drain(observer)

    not_owned = observer_fed.last_callback("attributeIsNotOwned")
    assert not_owned is not None
    assert not_owned.args == (obj, attr)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("query-unowned-fed")


@pytest.mark.requirements(*CLAUSE7_OWNERSHIP_UNAVAILABLE_CALLBACK_REQUIREMENTS)
def test_ownership_unavailable_and_query_callbacks_are_isolated_and_exact():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("ownership-callback-query-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    offered = owner.registerObjectInstance(cls, "Unavailable-Callback-1")
    drain(owner, acquirer)
    owner_fed.clear()
    acquirer_fed.clear()

    acquirer.attributeOwnershipAcquisitionIfAvailable(offered, {attr})
    drain(owner, acquirer)
    unavailable_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "attributeOwnershipUnavailable"
    ]
    assert [rec.method_name for rec in unavailable_callbacks] == ["attributeOwnershipUnavailable"]
    assert unavailable_callbacks[0].args == (offered, AttributeHandleSet({attr}))
    assert owner_fed.last_callback("requestAttributeOwnershipRelease") is None

    query_target = owner.registerObjectInstance(cls, "Query-Callback-1")
    owner_fed.clear()
    acquirer_fed.clear()
    acquirer.queryAttributeOwnership(query_target, attr)
    drain(owner, acquirer)
    owned_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "informAttributeOwnership"
    ]
    assert [rec.method_name for rec in owned_callbacks] == ["informAttributeOwnership"]
    assert owned_callbacks[0].args == (query_target, attr, owner.backend.state.handle)

    owner.unconditionalAttributeOwnershipDivestiture(query_target, {attr})
    owner_fed.clear()
    acquirer_fed.clear()
    acquirer.queryAttributeOwnership(query_target, attr)
    drain(owner, acquirer)
    not_owned_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "attributeIsNotOwned"
    ]
    assert [rec.method_name for rec in not_owned_callbacks] == ["attributeIsNotOwned"]
    assert not_owned_callbacks[0].args == (query_target, attr)

    mom_class = owner.getObjectClassHandle(hla_mom.MOM_FEDERATION_OBJECT_CLASS)
    mom_attr = owner.getAttributeHandle(mom_class, "HLAfederationName")
    mom_object = owner.backend.state.federation.mom_federation_object
    assert mom_object is not None
    owner_fed.clear()
    acquirer_fed.clear()
    acquirer.queryAttributeOwnership(mom_object, mom_attr)
    drain(owner, acquirer)
    rti_owned_callbacks = [
        rec for rec in acquirer_fed.records if rec.method_name == "attributeIsOwnedByRTI"
    ]
    assert [rec.method_name for rec in rti_owned_callbacks] == ["attributeIsOwnedByRTI"]
    assert rti_owned_callbacks[0].args == (mom_object, mom_attr)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("ownership-callback-query-fed")


def test_python_rti_release_denied_preserves_owner_and_no_acquisition_grant():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("release-denied-retains-owner-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")

    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})
    pending = owner.registerObjectInstance(cls, "DeniedOwner-1")

    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"deny-tag")
    drain(owner, acquirer)

    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"deny-tag")

    owner.attributeOwnershipReleaseDenied(pending, {attr})
    drain(owner, acquirer)

    assert owner.isAttributeOwnedByFederate(pending, attr) is True
    assert acquirer.isAttributeOwnedByFederate(pending, attr) is False
    assert acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification") is None

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("release-denied-retains-owner-fed")


def test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.modifyLookahead(object())
    with pytest.raises(NotConnected):
        rti.retract(MessageRetractionHandle(1))
    with pytest.raises(NotConnected):
        rti.changeAttributeOrderType(ObjectInstanceHandle(999), set(), OrderType.RECEIVE)
    with pytest.raises(NotConnected):
        rti.enableTimeConstrained()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.modifyLookahead(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.retract(MessageRetractionHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.changeAttributeOrderType(ObjectInstanceHandle(999), set(), OrderType.RECEIVE)
    with pytest.raises(FederateNotExecutionMember):
        rti.enableTimeConstrained()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("time-tail-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    owner.publishObjectClassAttributes(cls, {attr})
    observer.publishObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, "Time-Tail-Negative")

    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.modifyLookahead(1.0)
    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(AttributeNotOwned):
        observer.changeAttributeOrderType(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.changeAttributeOrderType(ObjectInstanceHandle(999), {attr}, OrderType.RECEIVE)
    with pytest.raises(AttributeNotDefined):
        owner.changeAttributeOrderType(obj, {bad_attr}, OrderType.RECEIVE)

    owner.enableTimeRegulation(owner.getTimeFactory().make_interval(1.0))
    drain(owner, observer)
    owner.enableTimeConstrained()
    drain(owner, observer)
    with pytest.raises(TimeConstrainedAlreadyEnabled):
        owner.enableTimeConstrained()

    owner.disableTimeRegulation()
    owner.requestFederationSave("TIME-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.modifyLookahead(1.0)
    with pytest.raises(SaveInProgress):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(SaveInProgress):
        owner.changeAttributeOrderType(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(SaveInProgress):
        observer.enableTimeConstrained()

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("TIME-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.modifyLookahead(1.0)
    with pytest.raises(RestoreInProgress):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(RestoreInProgress):
        owner.changeAttributeOrderType(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(RestoreInProgress):
        observer.enableTimeConstrained()

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.enableTimeRegulation(owner.getTimeFactory().make_interval(1.0))
    owner.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        owner.modifyLookahead(1.0)
    with pytest.raises(InvalidMessageRetractionHandle):
        owner.retract("bad")
    owner.backend.state.time_advancing = False
    owner.disableTimeRegulation()

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("time-tail-negative-fed")


def test_change_interaction_order_type_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.changeInteractionOrderType(object(), OrderType.RECEIVE)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.changeInteractionOrderType(object(), OrderType.RECEIVE)
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("interaction-order-negative-fed")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    owner.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        owner.changeInteractionOrderType(interaction, OrderType.RECEIVE)
    with pytest.raises(InteractionClassNotDefined):
        owner.changeInteractionOrderType(type(interaction)(interaction.value + 1000), OrderType.RECEIVE)

    owner.requestFederationSave("INTERACTION-ORDER-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.changeInteractionOrderType(interaction, OrderType.RECEIVE)

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("INTERACTION-ORDER-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.changeInteractionOrderType(interaction, OrderType.RECEIVE)

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("interaction-order-negative-fed")


def test_async_delivery_and_time_query_disable_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.enableAsynchronousDelivery()
    with pytest.raises(NotConnected):
        rti.disableAsynchronousDelivery()
    with pytest.raises(NotConnected):
        rti.queryLookahead()
    with pytest.raises(NotConnected):
        rti.disableTimeRegulation()
    with pytest.raises(NotConnected):
        rti.disableTimeConstrained()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.enableAsynchronousDelivery()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableAsynchronousDelivery()
    with pytest.raises(FederateNotExecutionMember):
        rti.queryLookahead()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableTimeRegulation()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableTimeConstrained()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("async-time-tail-negative-fed")
    with pytest.raises(AsynchronousDeliveryAlreadyDisabled):
        owner.disableAsynchronousDelivery()
    owner.enableAsynchronousDelivery()
    with pytest.raises(AsynchronousDeliveryAlreadyEnabled):
        owner.enableAsynchronousDelivery()
    owner.disableAsynchronousDelivery()

    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.queryLookahead()
    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.disableTimeRegulation()
    with pytest.raises(TimeConstrainedIsNotEnabled):
        owner.disableTimeConstrained()

    owner.requestFederationSave("ASYNC-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enableAsynchronousDelivery()
    with pytest.raises(SaveInProgress):
        owner.disableAsynchronousDelivery()
    with pytest.raises(SaveInProgress):
        owner.queryLookahead()
    with pytest.raises(SaveInProgress):
        owner.disableTimeRegulation()
    with pytest.raises(SaveInProgress):
        owner.disableTimeConstrained()

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("ASYNC-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enableAsynchronousDelivery()
    with pytest.raises(RestoreInProgress):
        owner.disableAsynchronousDelivery()
    with pytest.raises(RestoreInProgress):
        owner.queryLookahead()
    with pytest.raises(RestoreInProgress):
        owner.disableTimeRegulation()
    with pytest.raises(RestoreInProgress):
        owner.disableTimeConstrained()

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("async-time-tail-negative-fed")


def test_enable_time_regulation_rejects_not_connected_not_joined_invalid_lookahead_duplicate_save_restore_and_time_advancing():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.enableTimeRegulation(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.enableTimeRegulation(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("enable-time-reg-negative-fed")
    factory = owner.getTimeFactory()

    with pytest.raises(InvalidLookahead):
        owner.enableTimeRegulation(factory.make_interval(-1.0))

    owner.enableTimeRegulation(factory.make_interval(1.0))
    drain(owner, observer)
    with pytest.raises(TimeRegulationAlreadyEnabled):
        owner.enableTimeRegulation(factory.make_interval(1.0))

    owner.disableTimeRegulation()
    owner.requestFederationSave("ENABLE-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enableTimeRegulation(factory.make_interval(1.0))

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("ENABLE-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enableTimeRegulation(factory.make_interval(1.0))

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        owner.enableTimeRegulation(factory.make_interval(1.0))
    owner.backend.state.time_advancing = False

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("enable-time-reg-negative-fed")


def test_time_enable_callbacks_are_not_emitted_on_failed_requests():
    _, owner, observer, owner_fed, observer_fed, _h1, _h2 = joined_pair("time-enable-callback-negative-fed")
    factory = owner.getTimeFactory()

    owner_fed.clear()
    with pytest.raises(InvalidLookahead):
        owner.enableTimeRegulation(factory.make_interval(-1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []

    owner.enableTimeRegulation(factory.make_interval(1.0))
    drain(owner, observer)
    assert owner_fed.last_callback("timeRegulationEnabled") is not None

    owner_fed.clear()
    with pytest.raises(TimeRegulationAlreadyEnabled):
        owner.enableTimeRegulation(factory.make_interval(1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []

    observer.enableTimeConstrained()
    drain(owner, observer)
    assert observer_fed.last_callback("timeConstrainedEnabled") is not None

    observer_fed.clear()
    with pytest.raises(TimeConstrainedAlreadyEnabled):
        observer.enableTimeConstrained()
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.disableTimeRegulation()
    observer.disableTimeConstrained()

    owner.requestFederationSave("TIME-ENABLE-CB-SAVE")
    drain(owner, observer)
    owner_fed.clear()
    observer_fed.clear()
    with pytest.raises(SaveInProgress):
        owner.enableTimeRegulation(factory.make_interval(1.0))
    with pytest.raises(SaveInProgress):
        observer.enableTimeConstrained()
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("TIME-ENABLE-CB-SAVE")
    drain(owner, observer)
    owner_fed.clear()
    observer_fed.clear()
    with pytest.raises(RestoreInProgress):
        owner.enableTimeRegulation(factory.make_interval(1.0))
    with pytest.raises(RestoreInProgress):
        observer.enableTimeConstrained()
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.backend.state.time_advancing = True
    owner_fed.clear()
    with pytest.raises(InTimeAdvancingState):
        owner.enableTimeRegulation(factory.make_interval(1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    owner.backend.state.time_advancing = False

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("time-enable-callback-negative-fed")


def test_support_service_lookup_and_factory_tail_rejects_declared_exceptions():
    factory_getters = (
        lambda tx: tx.getAttributeHandleFactory(),
        lambda tx: tx.getAttributeHandleSetFactory(),
        lambda tx: tx.getAttributeHandleValueMapFactory(),
        lambda tx: tx.getAttributeSetRegionSetPairListFactory(),
        lambda tx: tx.getDimensionHandleFactory(),
        lambda tx: tx.getDimensionHandleSetFactory(),
        lambda tx: tx.getFederateHandleFactory(),
        lambda tx: tx.getFederateHandleSetFactory(),
        lambda tx: tx.getInteractionClassHandleFactory(),
        lambda tx: tx.getObjectClassHandleFactory(),
        lambda tx: tx.getObjectInstanceHandleFactory(),
        lambda tx: tx.getParameterHandleFactory(),
        lambda tx: tx.getParameterHandleValueMapFactory(),
        lambda tx: tx.getRegionHandleSetFactory(),
        lambda tx: tx.getTransportationTypeHandleFactory(),
    )

    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.getFederateName(None)
    with pytest.raises(NotConnected):
        rti.getAttributeHandle(object(), "Position")
    with pytest.raises(NotConnected):
        rti.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    with pytest.raises(NotConnected):
        rti.getParameterHandle(object(), "TrackId")
    with pytest.raises(NotConnected):
        rti.getObjectInstanceName(ObjectInstanceHandle(1))
    with pytest.raises(NotConnected):
        rti.getUpdateRateValue("default")
    with pytest.raises(NotConnected):
        rti.getUpdateRateValueForAttribute(ObjectInstanceHandle(1), AttributeHandle(1))
    with pytest.raises(NotConnected):
        rti.getTransportationType("HLAreliable")
    with pytest.raises(NotConnected):
        rti.getTransportationName(TransportationTypeHandle(1))
    with pytest.raises(NotConnected):
        rti.getAutomaticResignDirective()
    with pytest.raises(NotConnected):
        rti.setAutomaticResignDirective(ResignAction.NO_ACTION)
    with pytest.raises(NotConnected):
        rti.normalizeFederateHandle(object())
    with pytest.raises(NotConnected):
        rti.normalizeServiceGroup("OBJECT_MANAGEMENT")
    with pytest.raises(NotConnected):
        rti.enableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.disableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(NotConnected):
        rti.getTimeFactory()
    for getter in factory_getters:
        with pytest.raises(NotConnected):
            getter(rti)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.getFederateName(None)
    with pytest.raises(FederateNotExecutionMember):
        rti.getAttributeHandle(object(), "Position")
    with pytest.raises(FederateNotExecutionMember):
        rti.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    with pytest.raises(FederateNotExecutionMember):
        rti.getParameterHandle(object(), "TrackId")
    with pytest.raises(FederateNotExecutionMember):
        rti.getObjectInstanceName(ObjectInstanceHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.getUpdateRateValue("default")
    with pytest.raises(FederateNotExecutionMember):
        rti.getUpdateRateValueForAttribute(ObjectInstanceHandle(1), AttributeHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.getTransportationType("HLAreliable")
    with pytest.raises(FederateNotExecutionMember):
        rti.getTransportationName(TransportationTypeHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.getAutomaticResignDirective()
    with pytest.raises(FederateNotExecutionMember):
        rti.setAutomaticResignDirective(ResignAction.NO_ACTION)
    with pytest.raises(FederateNotExecutionMember):
        rti.normalizeFederateHandle(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.normalizeServiceGroup("OBJECT_MANAGEMENT")
    with pytest.raises(FederateNotExecutionMember):
        rti.enableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(FederateNotExecutionMember):
        rti.getTimeFactory()
    for getter in factory_getters:
        with pytest.raises(FederateNotExecutionMember):
            getter(rti)
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, owner_handle, observer_handle = joined_pair("support-lookup-tail-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    object_handle = owner.registerObjectInstance(cls, "support-tail-object")

    bad_class = type(cls)(cls.value + 999)
    bad_interaction = type(interaction)(interaction.value + 999)
    bad_object = ObjectInstanceHandle(object_handle.value + 999)
    bad_dim = DimensionHandle(999999)
    bad_attr = AttributeHandle(999999)

    with pytest.raises(FederateHandleNotKnown):
        owner.getFederateName(type(owner_handle)(owner_handle.value + observer_handle.value + 1000))
    with pytest.raises(InvalidFederateHandle):
        owner.getFederateName(object())
    with pytest.raises(NameNotFound):
        owner.getFederateHandle("no-such-federate")
    with pytest.raises(NameNotFound):
        owner.getObjectClassHandle("HLAobjectRoot.NoSuchClass")
    with pytest.raises(InvalidObjectClassHandle):
        owner.getObjectClassName(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        owner.getAttributeHandle(bad_class, "Position")
    with pytest.raises(NameNotFound):
        owner.getAttributeHandle(cls, "NoSuchAttribute")
    with pytest.raises(NameNotFound):
        owner.getInteractionClassHandle("HLAinteractionRoot.NoSuchInteraction")
    with pytest.raises(InvalidInteractionClassHandle):
        owner.getInteractionClassName(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.getParameterHandle(bad_interaction, "TrackId")
    with pytest.raises(NameNotFound):
        owner.getParameterHandle(interaction, "NoSuchParameter")
    with pytest.raises(AttributeNotDefined):
        owner.getUpdateRateValueForAttribute(object_handle, bad_attr)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.getUpdateRateValueForAttribute(bad_object, attr)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.getObjectInstanceName(bad_object)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.getObjectInstanceHandle("no-such-object")
    with pytest.raises(ObjectInstanceNotKnown):
        owner.getKnownObjectClassHandle(bad_object)
    with pytest.raises(InvalidUpdateRateDesignator):
        owner.getUpdateRateValue("bogus-rate")
    with pytest.raises(InvalidInteractionClassHandle):
        owner.getAvailableDimensionsForInteractionClass(bad_interaction)
    with pytest.raises(NameNotFound):
        owner.getDimensionHandle("NoSuchDimension")
    with pytest.raises(InvalidDimensionHandle):
        owner.getDimensionName(bad_dim)
    with pytest.raises(InvalidDimensionHandle):
        owner.getDimensionUpperBound(bad_dim)
    with pytest.raises(InvalidResignAction):
        owner.setAutomaticResignDirective(object())
    with pytest.raises(InvalidFederateHandle):
        owner.normalizeFederateHandle(object())
    with pytest.raises(InvalidServiceGroup):
        owner.normalizeServiceGroup("not-a-group")
    with pytest.raises(InvalidOrderType):
        owner.getOrderName(object())
    with pytest.raises(InvalidOrderName):
        owner.getOrderType("bogus-order")
    with pytest.raises(InvalidTransportationName):
        owner.getTransportationTypeHandle("bogus-transport")
    with pytest.raises(InvalidTransportationName):
        owner.getTransportationType("bogus-transport")
    with pytest.raises(InvalidTransportationType):
        owner.getTransportationTypeName(TransportationTypeHandle(999))
    with pytest.raises(InvalidTransportationType):
        owner.getTransportationName(TransportationTypeHandle(999))
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOff):
        owner.disableInteractionRelevanceAdvisorySwitch()
    owner.enableInteractionRelevanceAdvisorySwitch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOn):
        owner.enableInteractionRelevanceAdvisorySwitch()
    owner.disableInteractionRelevanceAdvisorySwitch()
    assert owner.getUpdateRateValueForAttribute(object_handle, attr) == 0.0

    owner.requestFederationSave("SUPPORT-LOOKUP-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enableInteractionRelevanceAdvisorySwitch()

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("SUPPORT-LOOKUP-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.disableInteractionRelevanceAdvisorySwitch()

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-lookup-tail-fed")


class _ImmediateSupportCallbackAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti
        self.captured: list[type[BaseException]] = []

    def synchronizationPointRegistrationSucceeded(self, label):
        super().synchronizationPointRegistrationSucceeded(label)
        for fn, args in (
            (self.rti.evokeCallback, (0.0,)),
            (self.rti.evokeMultipleCallbacks, (0.0, 0.0)),
        ):
            try:
                fn(*args)
            except CallNotAllowedFromWithinCallback:
                self.captured.append(CallNotAllowedFromWithinCallback)


def test_callback_controls_reject_save_restore_and_within_callback_evoke():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("support-callback-tail-fed")
    owner.requestFederationSave("SUPPORT-CALLBACK-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enableCallbacks()
    with pytest.raises(SaveInProgress):
        owner.disableCallbacks()

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("SUPPORT-CALLBACK-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enableCallbacks()
    with pytest.raises(RestoreInProgress):
        owner.disableCallbacks()
    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-callback-tail-fed")

    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    fed = _ImmediateSupportCallbackAmbassador(rti)
    rti.connect(fed, CallbackModel.HLA_IMMEDIATE)
    rti.createFederationExecution("support-immediate-callback-fed", "TargetRadarFOMmodule.xml")
    rti.joinFederationExecution("alpha", "type-a", "support-immediate-callback-fed")
    rti.registerFederationSynchronizationPoint("IMMEDIATE-CALLBACK", b"x")
    assert fed.captured == [CallNotAllowedFromWithinCallback, CallNotAllowedFromWithinCallback]
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution("support-immediate-callback-fed")
