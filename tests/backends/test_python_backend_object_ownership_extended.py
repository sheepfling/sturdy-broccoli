# ruff: noqa: F401,F403

import pytest

from hla2010 import mom as hla_mom
from tests.backends.python_backend_extended_support import *
from hla2010.api import RTIambassador, FederateAmbassador
from hla2010.exceptions import *
from hla2010.handles import *
from hla2010.raw_api import API_METADATA
from hla2010.enums import OrderType, ResignAction
from hla2010.types import RangeBounds
from hla2010.exceptions import AttributeAlreadyBeingDivested, AttributeAlreadyOwned, AttributeNotPublished, InteractionClassNotPublished

def test_support_surface_negative_paths_cover_handle_validation_region_bounds_and_advisory_switches():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.get_attribute_name(object(), object())
    with pytest.raises(NotConnected):
        rti.get_parameter_name(object(), object())
    with pytest.raises(NotConnected):
        rti.get_available_dimensions_for_class_attribute(object(), object())
    with pytest.raises(NotConnected):
        rti.get_dimension_handle_set(object())
    with pytest.raises(NotConnected):
        rti.enable_object_class_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.disable_object_class_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.enable_attribute_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.disable_attribute_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.enable_attribute_scope_advisory_switch()
    with pytest.raises(NotConnected):
        rti.disable_attribute_scope_advisory_switch()
    with pytest.raises(NotConnected):
        rti.get_range_bounds(object(), object())
    with pytest.raises(NotConnected):
        rti.set_range_bounds(object(), object(), RangeBounds(0, 1))

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.get_attribute_name(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.get_parameter_name(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.get_available_dimensions_for_class_attribute(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.get_dimension_handle_set(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_object_class_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_object_class_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_attribute_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_attribute_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_attribute_scope_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_attribute_scope_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.get_range_bounds(object(), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.set_range_bounds(object(), object(), RangeBounds(0, 1))
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("support-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    param = owner.get_parameter_handle(interaction, "TrackId")
    dim = owner.get_dimension_handle("HLAdefaultRoutingSpace")
    region = owner.create_region({dim})

    bad_class = type(cls)(cls.value + 1000)
    bad_attr = type(attr)(attr.value + 1000)
    bad_interaction = type(interaction)(interaction.value + 1000)
    bad_param = type(param)(param.value + 1000)
    bad_dim = type(dim)(dim.value + 1000)
    bad_region = type(region)(region.value + 1000)

    with pytest.raises(InvalidObjectClassHandle):
        owner.get_attribute_name(bad_class, attr)
    with pytest.raises(AttributeNotDefined):
        owner.get_attribute_name(cls, bad_attr)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.get_parameter_name(bad_interaction, param)
    with pytest.raises(InteractionParameterNotDefined):
        owner.get_parameter_name(interaction, bad_param)
    with pytest.raises(InvalidObjectClassHandle):
        owner.get_available_dimensions_for_class_attribute(bad_class, attr)
    with pytest.raises(AttributeNotDefined):
        owner.get_available_dimensions_for_class_attribute(cls, bad_attr)

    with pytest.raises(InvalidRegion):
        owner.get_dimension_handle_set(bad_region)
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOff):
        owner.disable_object_class_relevance_advisory_switch()
    owner.enable_object_class_relevance_advisory_switch()
    with pytest.raises(ObjectClassRelevanceAdvisorySwitchIsOn):
        owner.enable_object_class_relevance_advisory_switch()
    owner.disable_object_class_relevance_advisory_switch()

    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOff):
        owner.disable_attribute_relevance_advisory_switch()
    owner.enable_attribute_relevance_advisory_switch()
    with pytest.raises(AttributeRelevanceAdvisorySwitchIsOn):
        owner.enable_attribute_relevance_advisory_switch()
    owner.disable_attribute_relevance_advisory_switch()

    with pytest.raises(AttributeScopeAdvisorySwitchIsOff):
        owner.disable_attribute_scope_advisory_switch()
    owner.enable_attribute_scope_advisory_switch()
    with pytest.raises(AttributeScopeAdvisorySwitchIsOn):
        owner.enable_attribute_scope_advisory_switch()
    owner.disable_attribute_scope_advisory_switch()

    with pytest.raises(InvalidRegion):
        owner.get_range_bounds(bad_region, dim)
    with pytest.raises(RegionDoesNotContainSpecifiedDimension):
        owner.get_range_bounds(region, bad_dim)
    with pytest.raises(InvalidRegion):
        owner.set_range_bounds(bad_region, dim, RangeBounds(0, 1))
    with pytest.raises(RegionDoesNotContainSpecifiedDimension):
        owner.set_range_bounds(region, bad_dim, RangeBounds(0, 1))
    with pytest.raises(InvalidRangeBound):
        owner.set_range_bounds(region, dim, RangeBounds(10, 1))

    owner.request_federation_save("SUPPORT-NEGATIVE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.get_dimension_handle_set(region)
    with pytest.raises(SaveInProgress):
        owner.enable_object_class_relevance_advisory_switch()
    with pytest.raises(SaveInProgress):
        owner.disable_attribute_relevance_advisory_switch()
    with pytest.raises(SaveInProgress):
        owner.enable_attribute_scope_advisory_switch()
    with pytest.raises(SaveInProgress):
        owner.get_range_bounds(region, dim)
    with pytest.raises(SaveInProgress):
        owner.set_range_bounds(region, dim, RangeBounds(0, 1))

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("SUPPORT-NEGATIVE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.get_dimension_handle_set(region)
    with pytest.raises(RestoreInProgress):
        owner.enable_object_class_relevance_advisory_switch()
    with pytest.raises(RestoreInProgress):
        owner.disable_attribute_relevance_advisory_switch()
    with pytest.raises(RestoreInProgress):
        owner.enable_attribute_scope_advisory_switch()
    with pytest.raises(RestoreInProgress):
        owner.get_range_bounds(region, dim)
    with pytest.raises(RestoreInProgress):
        owner.set_range_bounds(region, dim, RangeBounds(0, 1))

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-negative-fed")


def test_request_attribute_transportation_type_change_rejects_not_connected_not_joined_and_unknown_object():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.request_attribute_transportation_type_change(ObjectInstanceHandle(999), set(), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_attribute_transportation_type_change(ObjectInstanceHandle(999), set(), object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("transport-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    rcs = owner.get_attribute_handle(cls, "RCS")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Transport-1")
    owner_fed.clear()
    with pytest.raises(ObjectInstanceNotKnown):
        owner.request_attribute_transportation_type_change(ObjectInstanceHandle(999), set(), owner.backend.engine.transportation_reliable)
    with pytest.raises(AttributeNotDefined):
        owner.request_attribute_transportation_type_change(obj, {type(attr)(attr.value + 1000)}, owner.backend.engine.transportation_reliable)
    with pytest.raises(InvalidTransportationType):
        owner.request_attribute_transportation_type_change(obj, {attr}, TransportationTypeHandle(999))
    with pytest.raises(AttributeNotOwned):
        observer.request_attribute_transportation_type_change(obj, {attr}, owner.backend.engine.transportation_reliable)

    owner.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        owner.request_attribute_transportation_type_change(obj, {rcs}, owner.backend.engine.transportation_reliable)
    owner.backend.config.strict_object_publication = False
    assert owner_fed.callbacks_named("confirmAttributeTransportationTypeChange") == []

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("transport-negative-fed")


def test_declaration_services_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unpublish_object_class_attributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribe_object_class_attributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribe_object_class_attributes_passively(object(), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublish_object_class_attributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribe_object_class_attributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribe_object_class_attributes_passively(object(), set())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("declaration-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.request_federation_save("DECL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.unpublish_object_class_attributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribe_object_class_attributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribe_object_class_attributes_passively(cls, {attr})

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("DECL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.unpublish_object_class_attributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribe_object_class_attributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribe_object_class_attributes_passively(cls, {attr})

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("declaration-negative-fed")


def test_publish_unpublish_unsubscribe_and_interaction_subscription_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.publish_object_class_attributes(object(), set())
    with pytest.raises(NotConnected):
        rti.unpublish_object_class(object())
    with pytest.raises(NotConnected):
        rti.unsubscribe_object_class_attributes(object(), set())
    with pytest.raises(NotConnected):
        rti.subscribe_interaction_class(object())
    with pytest.raises(NotConnected):
        rti.subscribe_interaction_class_passively(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.publish_object_class_attributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublish_object_class(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribe_object_class_attributes(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribe_interaction_class(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.subscribe_interaction_class_passively(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-tail-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    owner.request_federation_save("DECL-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.publish_object_class_attributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        owner.unpublish_object_class(cls)
    with pytest.raises(SaveInProgress):
        observer.unsubscribe_object_class_attributes(cls, {attr})
    with pytest.raises(SaveInProgress):
        observer.subscribe_interaction_class(interaction)
    with pytest.raises(SaveInProgress):
        observer.subscribe_interaction_class_passively(interaction)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("DECL-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.publish_object_class_attributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        owner.unpublish_object_class(cls)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribe_object_class_attributes(cls, {attr})
    with pytest.raises(RestoreInProgress):
        observer.subscribe_interaction_class(interaction)
    with pytest.raises(RestoreInProgress):
        observer.subscribe_interaction_class_passively(interaction)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-tail-negative-fed")


def test_publish_unpublish_and_unsubscribe_interaction_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.publish_interaction_class(object())
    with pytest.raises(NotConnected):
        rti.unpublish_interaction_class(object())
    with pytest.raises(NotConnected):
        rti.unsubscribe_object_class(object())
    with pytest.raises(NotConnected):
        rti.unsubscribe_interaction_class(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.publish_interaction_class(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unpublish_interaction_class(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribe_object_class(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribe_interaction_class(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-admin-tail-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    owner.request_federation_save("DECL-ADMIN-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.publish_interaction_class(interaction)
    with pytest.raises(SaveInProgress):
        owner.unpublish_interaction_class(interaction)
    with pytest.raises(SaveInProgress):
        observer.unsubscribe_object_class(cls)
    with pytest.raises(SaveInProgress):
        observer.unsubscribe_interaction_class(interaction)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("DECL-ADMIN-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.publish_interaction_class(interaction)
    with pytest.raises(RestoreInProgress):
        owner.unpublish_interaction_class(interaction)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribe_object_class(cls)
    with pytest.raises(RestoreInProgress):
        observer.unsubscribe_interaction_class(interaction)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-admin-tail-negative-fed")


def test_declaration_services_validate_declared_handles_attributes_and_update_rate_designators():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-arg-validation-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    bad_class = type(cls)(cls.value + 1000)
    bad_attr = type(attr)(attr.value + 1000)
    bad_interaction = type(interaction)(interaction.value + 1000)

    with pytest.raises(InvalidObjectClassHandle):
        owner.publish_object_class_attributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        owner.publish_object_class_attributes(cls, {bad_attr})

    with pytest.raises(InvalidObjectClassHandle):
        owner.unpublish_object_class(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        owner.unpublish_object_class_attributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        owner.unpublish_object_class_attributes(cls, {bad_attr})

    with pytest.raises(InvalidInteractionClassHandle):
        owner.publish_interaction_class(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.unpublish_interaction_class(bad_interaction)

    with pytest.raises(InvalidObjectClassHandle):
        observer.subscribe_object_class_attributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.subscribe_object_class_attributes(cls, {bad_attr})
    with pytest.raises(InvalidUpdateRateDesignator):
        observer.subscribe_object_class_attributes(cls, {attr}, "not-a-rate")

    with pytest.raises(InvalidObjectClassHandle):
        observer.subscribe_object_class_attributes_passively(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.subscribe_object_class_attributes_passively(cls, {bad_attr})
    with pytest.raises(InvalidUpdateRateDesignator):
        observer.subscribe_object_class_attributes_passively(cls, {attr}, "not-a-rate")

    with pytest.raises(InvalidObjectClassHandle):
        observer.unsubscribe_object_class(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        observer.unsubscribe_object_class_attributes(bad_class, {attr})
    with pytest.raises(AttributeNotDefined):
        observer.unsubscribe_object_class_attributes(cls, {bad_attr})

    with pytest.raises(InvalidInteractionClassHandle):
        observer.subscribe_interaction_class(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        observer.subscribe_interaction_class_passively(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        observer.unsubscribe_interaction_class(bad_interaction)

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-arg-validation-fed")


def test_declaration_services_are_observable_through_mom_service_invocation_reporting():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("decl-mom-service-report-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    set_reporting = owner.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_report = owner.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    sr_fed = owner.get_parameter_handle(set_reporting, "HLAfederate")
    sr_state = owner.get_parameter_handle(set_reporting, "HLAreportingState")
    report_service = observer.get_parameter_handle(service_report, "HLAservice")
    report_success = observer.get_parameter_handle(service_report, "HLAsuccessIndicator")

    observer.subscribe_interaction_class(service_report)
    owner.send_interaction(
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
    owner.publish_object_class_attributes(cls, {attr})
    owner.unpublish_object_class(cls)
    owner.publish_interaction_class(interaction)
    owner.unpublish_interaction_class(interaction)
    owner.subscribe_object_class_attributes(cls, {attr})
    owner.subscribe_object_class_attributes_passively(cls, {attr}, "HLAdefault")
    owner.unsubscribe_object_class(cls)
    owner.subscribe_interaction_class(interaction)
    owner.subscribe_interaction_class_passively(interaction)
    owner.unsubscribe_interaction_class(interaction)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-mom-service-report-fed")


def test_declaration_management_effects_apply_while_time_managed():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("decl-time-managed-fed")
    factory = owner.get_time_factory()
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = owner.get_parameter_handle(interaction, "TrackId")

    owner.enable_time_regulation(factory.make_interval(1.0))
    observer.enable_time_constrained()
    drain(owner, observer)

    observer.subscribe_object_class_attributes(cls, {attr})
    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_interaction_class(interaction)
    owner.publish_interaction_class(interaction)

    obj = owner.register_object_instance(cls, "Time-Managed-Declared")
    owner.send_interaction(interaction, {track_id: b"ro"}, b"\x00\x00\x00\x00")
    drain(owner, observer)

    discovery = observer_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    received = observer_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"ro"

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-time-managed-fed")


def test_unpublishing_object_class_attributes_prevents_strict_updates():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-unpublish-object-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Strict-Unpublish-Object")
    owner.unpublish_object_class_attributes(cls, {attr})
    owner.backend.config.strict_object_publication = True

    with pytest.raises(AttributeNotPublished):
        owner.update_attribute_values(obj, {attr: b"x"}, b"\x00\x00\x00\x00")

    owner.backend.config.strict_object_publication = False
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-unpublish-object-fed")


def test_unpublishing_interaction_class_prevents_strict_sends():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-unpublish-interaction-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = owner.get_parameter_handle(interaction, "TrackId")

    owner.publish_interaction_class(interaction)
    owner.unpublish_interaction_class(interaction)
    owner.backend.config.strict_interaction_publication = True

    with pytest.raises(InteractionClassNotPublished):
        owner.send_interaction(interaction, {track_id: b"x"}, b"\x00\x00\x00\x00")

    owner.backend.config.strict_interaction_publication = False
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-unpublish-interaction-fed")


def test_transportation_type_services_emit_confirm_and_report_callbacks():
    _, owner, observer, owner_fed, _observer_fed, owner_handle, _observer_handle = joined_pair("transport-positive-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    best_effort = owner.backend.engine.transportation_best_effort

    owner.publish_object_class_attributes(cls, {attr})
    owner.publish_interaction_class(interaction)
    obj = owner.register_object_instance(cls, "Transport-Positive-1")
    owner_fed.clear()

    owner.request_attribute_transportation_type_change(obj, {attr}, best_effort)
    owner.query_attribute_transportation_type(obj, attr)
    owner.request_interaction_transportation_type_change(interaction, best_effort)
    owner.backend._svc_queryInteractionTransportationType(interaction)
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

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("transport-positive-fed")


def test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("transport-runtime-behavior-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    pos = owner.get_attribute_handle(cls, "Position")
    rcs = owner.get_attribute_handle(cls, "RCS")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = owner.get_parameter_handle(interaction, "TrackId")
    reliable = owner.backend.engine.transportation_reliable
    best_effort = owner.backend.engine.transportation_best_effort

    owner.publish_object_class_attributes(cls, {pos, rcs})
    observer.subscribe_object_class_attributes(cls, {pos, rcs})
    owner.publish_interaction_class(interaction)
    observer.subscribe_interaction_class(interaction)
    obj = owner.register_object_instance(cls, "Transport-Runtime-Behavior")
    drain(owner, observer)
    observer_fed.clear()

    owner.request_attribute_transportation_type_change(obj, {pos}, reliable)
    owner.request_attribute_transportation_type_change(obj, {rcs}, best_effort)
    owner.request_interaction_transportation_type_change(interaction, best_effort)
    drain(owner, observer)
    observer_fed.clear()

    owner.update_attribute_values(obj, {pos: b"pos", rcs: b"rcs"}, b"mixed-transport")
    owner.send_interaction(interaction, {track_id: b"trk"}, b"be-interaction")
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

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("transport-runtime-behavior-fed")


def test_start_and_stop_registration_callbacks_are_delivered():
    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-registration-callback-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")

    owner_fed.clear()
    owner.backend._svc_startRegistrationForObjectClass(cls)
    owner.backend._svc_stopRegistrationForObjectClass(cls)
    drain(owner, observer)

    registration_callbacks = [
        record for record in owner_fed.records
        if record.method_name in {"startRegistrationForObjectClass", "stopRegistrationForObjectClass"}
    ]
    assert [record.method_name for record in registration_callbacks] == [
        "startRegistrationForObjectClass",
        "stopRegistrationForObjectClass",
    ]

    started = registration_callbacks[0]
    stopped = registration_callbacks[1]
    assert started is not None
    assert started.args == (cls,)
    assert stopped is not None
    assert stopped.args == (cls,)

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-registration-callback-fed")


def test_turn_interactions_on_and_off_callbacks_are_delivered():
    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("decl-interaction-callback-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    owner_fed.clear()
    owner.backend._svc_turnInteractionsOn(interaction)
    owner.backend._svc_turnInteractionsOff(interaction)
    drain(owner, observer)

    interaction_callbacks = [
        record for record in owner_fed.records
        if record.method_name in {"turnInteractionsOn", "turnInteractionsOff"}
    ]
    assert [record.method_name for record in interaction_callbacks] == [
        "turnInteractionsOn",
        "turnInteractionsOff",
    ]

    on = interaction_callbacks[0]
    off = interaction_callbacks[1]
    assert on is not None
    assert on.args == (interaction,)
    assert off is not None
    assert off.args == (interaction,)

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("decl-interaction-callback-fed")


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
        assert hasattr(RTIambassador, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassador, method_name)
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
        assert hasattr(RTIambassador, method_name)
        java_records = [
            record for record in API_METADATA["RTIambassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == expected_returns
        assert [record["params"] for record in java_records] == expected_params

    for method_name, (service, expected_params) in federate_checks.items():
        assert hasattr(FederateAmbassador, method_name)
        java_records = [
            record for record in API_METADATA["FederateAmbassador"][method_name]
            if record["language"] == "java"
        ]
        assert [record["service"] for record in java_records] == [service] * len(expected_params)
        assert [record["return_type"] for record in java_records] == ["void"] * len(expected_params)
        assert [record["params"] for record in java_records] == expected_params


def test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.update_attribute_values(ObjectInstanceHandle(999), {}, b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.update_attribute_values(ObjectInstanceHandle(999), {}, b"tag")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("update-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    observer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Update-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.update_attribute_values(ObjectInstanceHandle(999), {attr: b"x"}, b"tag")
    with pytest.raises(AttributeNotOwned):
        observer.update_attribute_values(obj, {attr: b"x"}, b"tag")

    owner.request_federation_save("UPDATE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.update_attribute_values(obj, {attr: b"x"}, b"tag")

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("UPDATE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.update_attribute_values(obj, {attr: b"x"}, b"tag")

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("update-negative-fed")


def test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.delete_object_instance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(NotConnected):
        rti.local_delete_object_instance(ObjectInstanceHandle(999))

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.delete_object_instance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(FederateNotExecutionMember):
        rti.local_delete_object_instance(ObjectInstanceHandle(999))
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("delete-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    observer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Delete-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.delete_object_instance(ObjectInstanceHandle(999), b"tag")
    with pytest.raises(DeletePrivilegeNotHeld):
        observer.delete_object_instance(obj, b"tag")
    with pytest.raises(FederateOwnsAttributes):
        owner.local_delete_object_instance(obj)

    owner.request_federation_save("DELETE-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.delete_object_instance(obj, b"tag")
    with pytest.raises(SaveInProgress):
        owner.local_delete_object_instance(obj)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("DELETE-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.delete_object_instance(obj, b"tag")
    with pytest.raises(RestoreInProgress):
        owner.local_delete_object_instance(obj)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("delete-negative-fed")


def test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.request_attribute_value_update(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_attribute_value_update(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("ravu-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.request_federation_save("RAVU-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.request_attribute_value_update(cls, {attr}, b"tag")

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("RAVU-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.request_attribute_value_update(cls, {attr}, b"tag")

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("ravu-negative-fed")


def test_request_interaction_transportation_type_change_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.request_interaction_transportation_type_change(object(), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_interaction_transportation_type_change(object(), object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("interaction-transport-negative-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    owner_fed.clear()
    owner.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        owner.request_interaction_transportation_type_change(interaction, owner.backend.engine.transportation_reliable)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.request_interaction_transportation_type_change(type(interaction)(interaction.value + 1000), owner.backend.engine.transportation_reliable)
    owner.backend.config.strict_interaction_publication = False
    owner.publish_interaction_class(interaction)
    with pytest.raises(InvalidTransportationType):
        owner.request_interaction_transportation_type_change(interaction, TransportationTypeHandle(999))
    assert owner_fed.callbacks_named("confirmInteractionTransportationTypeChange") == []

    owner.request_federation_save("INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.request_interaction_transportation_type_change(interaction, owner.backend.engine.transportation_reliable)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.request_interaction_transportation_type_change(interaction, owner.backend.engine.transportation_reliable)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("interaction-transport-negative-fed")


def test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.query_attribute_transportation_type(ObjectInstanceHandle(999), object())
    with pytest.raises(NotConnected):
        rti.reserve_multiple_object_instance_name(set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.query_attribute_transportation_type(ObjectInstanceHandle(999), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.reserve_multiple_object_instance_name(set())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("query-transport-reserve-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "QueryTransport")
    owner_fed.clear()

    with pytest.raises(ObjectInstanceNotKnown):
        owner.query_attribute_transportation_type(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.query_attribute_transportation_type(obj, type(attr)(attr.value + 1000))
    assert owner_fed.callbacks_named("reportAttributeTransportationType") == []

    owner.request_federation_save("QUERY-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.query_attribute_transportation_type(obj, attr)
    with pytest.raises(SaveInProgress):
        owner.reserve_multiple_object_instance_name({"A", "B"})

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("QUERY-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.query_attribute_transportation_type(obj, attr)
    with pytest.raises(RestoreInProgress):
        owner.reserve_multiple_object_instance_name({"A", "B"})

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("query-transport-reserve-negative-fed")


def test_query_interaction_transportation_type_rejects_not_connected_not_joined_invalid_handle_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.backend._svc_queryInteractionTransportationType(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.backend._svc_queryInteractionTransportationType(object())
    rti.disconnect()

    _, owner, observer, owner_fed, _observer_fed, _h1, _h2 = joined_pair("query-interaction-transport-negative-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    owner_fed.clear()

    with pytest.raises(InvalidInteractionClassHandle):
        owner.backend._svc_queryInteractionTransportationType(type(interaction)(interaction.value + 1000))
    assert owner_fed.callbacks_named("reportInteractionTransportationType") == []

    owner.request_federation_save("QUERY-INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.backend._svc_queryInteractionTransportationType(interaction)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("QUERY-INTERACTION-TRANSPORT-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.backend._svc_queryInteractionTransportationType(interaction)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("query-interaction-transport-negative-fed")


def test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.release_object_instance_name("name")
    with pytest.raises(NotConnected):
        rti.release_multiple_object_instance_name({"a", "b"})

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.release_object_instance_name("name")
    with pytest.raises(FederateNotExecutionMember):
        rti.release_multiple_object_instance_name({"a", "b"})
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("release-query-interaction-negative-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    owner.request_federation_save("REL-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.release_object_instance_name("name")
    with pytest.raises(SaveInProgress):
        owner.release_multiple_object_instance_name({"a", "b"})
    with pytest.raises(SaveInProgress):
        owner.backend._svc_queryInteractionTransportationType(interaction)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("REL-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.release_object_instance_name("name")
    with pytest.raises(RestoreInProgress):
        owner.release_multiple_object_instance_name({"a", "b"})
    with pytest.raises(RestoreInProgress):
        owner.backend._svc_queryInteractionTransportationType(interaction)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-query-interaction-negative-fed")


def test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.register_object_instance(object(), "bad")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.register_object_instance(object(), "bad")
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("register-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    owner.register_object_instance(cls, "Duplicate-Object")
    with pytest.raises(ObjectInstanceNameInUse):
        owner.register_object_instance(cls, "Duplicate-Object")

    owner.request_federation_save("REGISTER-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.register_object_instance(cls, "Blocked-Object")

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("REGISTER-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.register_object_instance(cls, "Blocked-Restore-Object")

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("register-negative-fed")


def test_python_rti_negotiated_ownership_tracks_divesting_and_candidate_flows():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("negotiated-ownership-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    acquirer.subscribe_object_class_attributes(cls, {attr})

    offered = owner.register_object_instance(cls, "Negotiated-1")
    drain(owner, acquirer)
    assert acquirer_fed.last_callback("discoverObjectInstance") is not None

    owner.negotiated_attribute_ownership_divestiture(offered, {attr}, b"offer-tag")
    drain(owner, acquirer)
    assumption = acquirer_fed.last_callback("requestAttributeOwnershipAssumption")
    assert assumption is not None
    assert assumption.args == (offered, AttributeHandleSet({attr}), b"offer-tag")
    assert owner.is_attribute_owned_by_federate(offered, attr) is True

    acquirer.attribute_ownership_acquisition(offered, {attr}, b"acquire-tag")
    drain(owner, acquirer)
    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (offered, AttributeHandleSet({attr}), b"acquire-tag")
    divest_notice = owner_fed.last_callback("requestDivestitureConfirmation")
    assert divest_notice is not None
    assert divest_notice.args == (offered, AttributeHandleSet({attr}))
    assert acquirer.is_attribute_owned_by_federate(offered, attr) is True

    pending = owner.register_object_instance(cls, "Pending-1")
    drain(owner, acquirer)
    acquirer.attribute_ownership_acquisition(pending, {attr}, b"request-tag")
    drain(owner, acquirer)
    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"request-tag")
    acquirer.cancel_attribute_ownership_acquisition(pending, {attr})
    drain(owner, acquirer)
    cancelled = acquirer_fed.last_callback("confirmAttributeOwnershipAcquisitionCancellation")
    assert cancelled is not None
    assert cancelled.args == (pending, AttributeHandleSet({attr}))

    acquirer.attribute_ownership_acquisition(pending, {attr}, b"retry-tag")
    drain(owner, acquirer)
    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"retry-tag")
    divested = owner.attribute_ownership_divestiture_if_wanted(pending, {attr})
    assert divested == AttributeHandleSet({attr})
    drain(owner, acquirer)
    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (pending, AttributeHandleSet({attr}), b"")
    assert acquirer.is_attribute_owned_by_federate(pending, attr) is True

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("negotiated-ownership-fed")


def test_negotiated_attribute_ownership_divestiture_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("negotiated-divest-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Negotiated-Divest-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.negotiated_attribute_ownership_divestiture(obj, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotOwned):
        acquirer.negotiated_attribute_ownership_divestiture(obj, {attr}, b"tag")
    owner.negotiated_attribute_ownership_divestiture(obj, {attr}, b"tag")
    with pytest.raises(AttributeAlreadyBeingDivested):
        owner.negotiated_attribute_ownership_divestiture(obj, {attr}, b"tag")

    owner.request_federation_save("NEGOTIATED-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.negotiated_attribute_ownership_divestiture(obj, {attr}, b"tag")

    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    drain(owner, acquirer)

    owner.request_federation_restore("NEGOTIATED-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.negotiated_attribute_ownership_divestiture(obj, {attr}, b"tag")

    owner.abort_federation_restore()
    drain(owner, acquirer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("negotiated-divest-negative-fed")


def test_confirm_divestiture_rejects_not_connected_not_joined_unknown_object_and_not_owned():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.confirm_divestiture(ObjectInstanceHandle(999), set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.confirm_divestiture(ObjectInstanceHandle(999), set(), b"tag")
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("confirm-divestiture-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    acquired = owner.register_object_instance(cls, "Confirm-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.confirm_divestiture(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(AttributeNotDefined):
        owner.confirm_divestiture(acquired, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotOwned):
        acquirer.confirm_divestiture(acquired, {attr}, b"tag")

    owner.negotiated_attribute_ownership_divestiture(acquired, {attr}, b"divest-tag")
    federation = owner.backend.engine.federations["confirm-divestiture-negative-fed"]
    federation.objects[acquired].attribute_candidates[attr] = {acquirer.backend.state.handle}

    owner.request_federation_save("CONFIRM-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.confirm_divestiture(acquired, {attr}, b"tag")
    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    drain(owner, acquirer)
    owner.request_federation_restore("CONFIRM-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.confirm_divestiture(acquired, {attr}, b"tag")
    owner.abort_federation_restore()
    drain(owner, acquirer)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("confirm-divestiture-negative-fed")


def test_python_rti_confirm_divestiture_requires_divesting_request_and_candidate():
    engine, owner, acquirer, _owner_fed, acquirer_fed, _h1, h2 = joined_pair("confirm-divestiture-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    acquirer.subscribe_object_class_attributes(cls, {attr})

    offered = owner.register_object_instance(cls, "Confirm-1")
    drain(owner, acquirer)

    try:
        owner.confirm_divestiture(offered, {attr}, b"confirm-tag")
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("confirm_divestiture should require prior negotiated divestiture")

    owner.negotiated_attribute_ownership_divestiture(offered, {attr}, b"offer-tag")
    drain(owner, acquirer)

    try:
        owner.confirm_divestiture(offered, {attr}, b"confirm-tag")
    except NoAcquisitionPending:
        pass
    else:
        raise AssertionError("confirm_divestiture should require a pending acquisition candidate")

    federation = engine.federations["confirm-divestiture-fed"]
    federation.objects[offered].attribute_candidates[attr] = {h2}
    owner.confirm_divestiture(offered, {attr}, b"confirm-tag")
    drain(owner, acquirer)

    acquired = acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (offered, AttributeHandleSet({attr}), b"confirm-tag")
    assert acquirer.is_attribute_owned_by_federate(offered, attr) is True

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("confirm-divestiture-fed")


def test_attribute_ownership_acquisition_services_reject_not_connected_not_joined_unknown_object_and_owned_attributes():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.attribute_ownership_acquisition(ObjectInstanceHandle(999), set(), b"tag")
    with pytest.raises(NotConnected):
        rti.attribute_ownership_acquisition_if_available(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.attribute_ownership_acquisition(ObjectInstanceHandle(999), set(), b"tag")
    with pytest.raises(FederateNotExecutionMember):
        rti.attribute_ownership_acquisition_if_available(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("acquisition-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    rcs = owner.get_attribute_handle(cls, "RCS")
    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    held = owner.register_object_instance(cls, "Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attribute_ownership_acquisition(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attribute_ownership_acquisition_if_available(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        acquirer.attribute_ownership_acquisition(held, {type(attr)(attr.value + 1000)}, b"tag")
    with pytest.raises(AttributeNotDefined):
        acquirer.attribute_ownership_acquisition_if_available(held, {type(attr)(attr.value + 1000)})
    with pytest.raises(FederateOwnsAttributes):
        owner.attribute_ownership_acquisition(held, {attr}, b"tag")
    with pytest.raises(FederateOwnsAttributes):
        owner.attribute_ownership_acquisition_if_available(held, {attr})

    acquirer.attribute_ownership_acquisition_if_available(held, {attr})
    with pytest.raises(AttributeAlreadyBeingAcquired):
        acquirer.attribute_ownership_acquisition_if_available(held, {attr})

    acquirer.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        acquirer.attribute_ownership_acquisition(held, {rcs}, b"tag")
    with pytest.raises(AttributeNotPublished):
        acquirer.attribute_ownership_acquisition_if_available(held, {rcs})
    acquirer.backend.config.strict_object_publication = False
    acquirer.unpublish_object_class(cls)
    with pytest.raises(ObjectClassNotPublished):
        acquirer.attribute_ownership_acquisition(held, {attr}, b"tag")
    with pytest.raises(ObjectClassNotPublished):
        acquirer.attribute_ownership_acquisition_if_available(held, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})

    acquirer.request_federation_save("ACQUIRE-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        acquirer.attribute_ownership_acquisition(held, {attr}, b"tag")
    with pytest.raises(SaveInProgress):
        acquirer.attribute_ownership_acquisition_if_available(held, {attr})
    acquirer.federate_save_begun()
    owner.federate_save_begun()
    acquirer.federate_save_complete()
    owner.federate_save_complete()
    drain(owner, acquirer)
    acquirer.request_federation_restore("ACQUIRE-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        acquirer.attribute_ownership_acquisition(held, {attr}, b"tag")
    with pytest.raises(RestoreInProgress):
        acquirer.attribute_ownership_acquisition_if_available(held, {attr})

    acquirer.abort_federation_restore()
    drain(owner, acquirer)
    owner.attribute_ownership_release_denied(held, {attr})
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("acquisition-negative-fed")


def test_python_rti_attribute_ownership_release_denied_clears_pending_acquisition():
    _, owner, acquirer, owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("release-denied-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})

    pending = owner.register_object_instance(cls, "Denied-1")
    acquirer.attribute_ownership_acquisition(pending, {attr}, b"deny-tag")
    drain(owner, acquirer)

    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"deny-tag")

    owner.attribute_ownership_release_denied(pending, {attr})

    try:
        acquirer.cancel_attribute_ownership_acquisition(pending, {attr})
    except AttributeAcquisitionWasNotRequested:
        pass
    else:
        raise AssertionError("release denial should clear the pending acquisition request")

    owner.unconditional_attribute_ownership_divestiture(pending, {attr})
    assert owner.is_attribute_owned_by_federate(pending, attr) is False
    assert acquirer.is_attribute_owned_by_federate(pending, attr) is False

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-denied-fed")


def test_attribute_ownership_release_denied_and_divestiture_if_wanted_reject_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.attribute_ownership_release_denied(ObjectInstanceHandle(999), set())
    with pytest.raises(NotConnected):
        rti.attribute_ownership_divestiture_if_wanted(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.attribute_ownership_release_denied(ObjectInstanceHandle(999), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.attribute_ownership_divestiture_if_wanted(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("release-divest-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Release-Divest-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.attribute_ownership_release_denied(ObjectInstanceHandle(999), {attr})
    with pytest.raises(ObjectInstanceNotKnown):
        owner.attribute_ownership_divestiture_if_wanted(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.attribute_ownership_release_denied(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotDefined):
        owner.attribute_ownership_divestiture_if_wanted(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        acquirer.attribute_ownership_release_denied(obj, {attr})
    with pytest.raises(AttributeNotOwned):
        acquirer.attribute_ownership_divestiture_if_wanted(obj, {attr})

    owner.request_federation_save("RELEASE-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.attribute_ownership_release_denied(obj, {attr})
    with pytest.raises(SaveInProgress):
        owner.attribute_ownership_divestiture_if_wanted(obj, {attr})

    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    drain(owner, acquirer)

    owner.request_federation_restore("RELEASE-DIVEST-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.attribute_ownership_release_denied(obj, {attr})
    with pytest.raises(RestoreInProgress):
        owner.attribute_ownership_divestiture_if_wanted(obj, {attr})

    owner.abort_federation_restore()
    drain(owner, acquirer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-divest-negative-fed")


def test_unconditional_divestiture_query_ownership_and_is_owned_reject_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unconditional_attribute_ownership_divestiture(ObjectInstanceHandle(999), set())
    with pytest.raises(NotConnected):
        rti.query_attribute_ownership(ObjectInstanceHandle(999), object())
    with pytest.raises(NotConnected):
        rti.is_attribute_owned_by_federate(ObjectInstanceHandle(999), object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unconditional_attribute_ownership_divestiture(ObjectInstanceHandle(999), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.query_attribute_ownership(ObjectInstanceHandle(999), object())
    with pytest.raises(FederateNotExecutionMember):
        rti.is_attribute_owned_by_federate(ObjectInstanceHandle(999), object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("ownership-query-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "OwnershipQuery")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.unconditional_attribute_ownership_divestiture(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.unconditional_attribute_ownership_divestiture(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        observer.unconditional_attribute_ownership_divestiture(obj, {attr})
    with pytest.raises(ObjectInstanceNotKnown):
        owner.query_attribute_ownership(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.query_attribute_ownership(obj, type(attr)(attr.value + 1000))
    with pytest.raises(ObjectInstanceNotKnown):
        owner.is_attribute_owned_by_federate(ObjectInstanceHandle(999), attr)
    with pytest.raises(AttributeNotDefined):
        owner.is_attribute_owned_by_federate(obj, type(attr)(attr.value + 1000))

    owner.request_federation_save("OWNERSHIP-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.unconditional_attribute_ownership_divestiture(obj, {attr})
    with pytest.raises(SaveInProgress):
        owner.query_attribute_ownership(obj, attr)
    with pytest.raises(SaveInProgress):
        owner.is_attribute_owned_by_federate(obj, attr)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("OWNERSHIP-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.unconditional_attribute_ownership_divestiture(obj, {attr})
    with pytest.raises(RestoreInProgress):
        owner.query_attribute_ownership(obj, attr)
    with pytest.raises(RestoreInProgress):
        owner.is_attribute_owned_by_federate(obj, attr)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("ownership-query-negative-fed")


def test_cancel_negotiated_divestiture_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.cancel_negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.cancel_negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-negotiated-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Cancel-Negotiated-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.cancel_negotiated_attribute_ownership_divestiture(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        owner.cancel_negotiated_attribute_ownership_divestiture(obj, {type(attr)(attr.value + 1000)})
    with pytest.raises(AttributeNotOwned):
        acquirer.cancel_negotiated_attribute_ownership_divestiture(obj, {attr})

    owner.request_federation_save("CANCEL-NEGOTIATED-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        owner.cancel_negotiated_attribute_ownership_divestiture(obj, {attr})

    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    drain(owner, acquirer)

    owner.request_federation_restore("CANCEL-NEGOTIATED-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        owner.cancel_negotiated_attribute_ownership_divestiture(obj, {attr})

    owner.abort_federation_restore()
    drain(owner, acquirer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("cancel-negotiated-negative-fed")


def test_python_rti_cancel_negotiated_divestiture_requires_active_request():
    _, owner, acquirer, owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-negotiated-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.subscribe_object_class_attributes(cls, {attr})
    offered = owner.register_object_instance(cls, "Cancel-1")
    drain(owner, acquirer)

    try:
        owner.cancel_negotiated_attribute_ownership_divestiture(offered, {attr})
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("cancel_negotiated_attribute_ownership_divestiture should require an active request")

    owner.negotiated_attribute_ownership_divestiture(offered, {attr}, b"cancel-tag")
    drain(owner, acquirer)
    assert owner_fed.last_callback("requestDivestitureConfirmation") is None

    owner.cancel_negotiated_attribute_ownership_divestiture(offered, {attr})
    try:
        owner.confirm_divestiture(offered, {attr}, b"confirm-tag")
    except AttributeDivestitureWasNotRequested:
        pass
    else:
        raise AssertionError("cancelled negotiated divestiture should clear the divesting state")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("cancel-negotiated-fed")


def test_python_rti_acquisition_if_available_reports_unavailable_without_transfer():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("acquire-if-available-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    offered = owner.register_object_instance(cls, "Unavailable-1")

    acquirer.attribute_ownership_acquisition_if_available(offered, {attr})
    drain(owner, acquirer)

    unavailable = acquirer_fed.last_callback("attributeOwnershipUnavailable")
    assert unavailable is not None
    assert unavailable.args == (offered, AttributeHandleSet({attr}))
    assert owner.is_attribute_owned_by_federate(offered, attr) is True
    assert acquirer.is_attribute_owned_by_federate(offered, attr) is False
    assert owner_fed.last_callback("requestAttributeOwnershipRelease") is None

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("acquire-if-available-fed")


def test_python_rti_divestiture_if_wanted_requires_pending_acquirer():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("divest-if-wanted-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    pending = owner.register_object_instance(cls, "Wanted-1")

    try:
        owner.attribute_ownership_divestiture_if_wanted(pending, {attr})
    except NoAcquisitionPending:
        pass
    else:
        raise AssertionError("attribute_ownership_divestiture_if_wanted should require a pending acquisition")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("divest-if-wanted-fed")


def test_python_rti_cancel_attribute_ownership_acquisition_requires_request():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-acquisition-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    pending = owner.register_object_instance(cls, "CancelAcquire-1")

    try:
        acquirer.cancel_attribute_ownership_acquisition(pending, {attr})
    except AttributeAcquisitionWasNotRequested:
        pass
    else:
        raise AssertionError("cancel_attribute_ownership_acquisition should require an outstanding request")

    with pytest.raises(AttributeAlreadyOwned):
        owner.cancel_attribute_ownership_acquisition(pending, {attr})

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("cancel-acquisition-fed")


def test_cancel_attribute_ownership_acquisition_rejects_not_connected_not_joined_unknown_object_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.cancel_attribute_ownership_acquisition(ObjectInstanceHandle(999), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.cancel_attribute_ownership_acquisition(ObjectInstanceHandle(999), set())
    rti.disconnect()

    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("cancel-acquisition-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Cancel-Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.cancel_attribute_ownership_acquisition(ObjectInstanceHandle(999), {attr})
    with pytest.raises(AttributeNotDefined):
        acquirer.cancel_attribute_ownership_acquisition(obj, {bad_attr})

    owner.request_federation_save("CANCEL-ACQ-SAVE")
    drain(owner, acquirer)
    with pytest.raises(SaveInProgress):
        acquirer.cancel_attribute_ownership_acquisition(obj, {attr})

    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    drain(owner, acquirer)

    owner.request_federation_restore("CANCEL-ACQ-SAVE")
    drain(owner, acquirer)
    with pytest.raises(RestoreInProgress):
        acquirer.cancel_attribute_ownership_acquisition(obj, {attr})

    owner.abort_federation_restore()
    drain(owner, acquirer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("cancel-acquisition-negative-fed")


def test_python_rti_query_attribute_ownership_reports_not_owned_after_divestiture():
    _, owner, observer, _owner_fed, observer_fed, _h1, _h2 = joined_pair("query-unowned-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Unowned-1")
    owner.unconditional_attribute_ownership_divestiture(obj, {attr})

    observer.query_attribute_ownership(obj, attr)
    drain(observer)

    not_owned = observer_fed.last_callback("attributeIsNotOwned")
    assert not_owned is not None
    assert not_owned.args == (obj, attr)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("query-unowned-fed")


def test_python_rti_release_denied_preserves_owner_and_no_acquisition_grant():
    _, owner, acquirer, owner_fed, acquirer_fed, _h1, _h2 = joined_pair("release-denied-retains-owner-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    pending = owner.register_object_instance(cls, "DeniedOwner-1")

    acquirer.attribute_ownership_acquisition(pending, {attr}, b"deny-tag")
    drain(owner, acquirer)

    release = owner_fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (pending, AttributeHandleSet({attr}), b"deny-tag")

    owner.attribute_ownership_release_denied(pending, {attr})
    drain(owner, acquirer)

    assert owner.is_attribute_owned_by_federate(pending, attr) is True
    assert acquirer.is_attribute_owned_by_federate(pending, attr) is False
    assert acquirer_fed.last_callback("attributeOwnershipAcquisitionNotification") is None

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-denied-retains-owner-fed")


def test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.modify_lookahead(object())
    with pytest.raises(NotConnected):
        rti.retract(MessageRetractionHandle(1))
    with pytest.raises(NotConnected):
        rti.change_attribute_order_type(ObjectInstanceHandle(999), set(), OrderType.RECEIVE)
    with pytest.raises(NotConnected):
        rti.enable_time_constrained()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.modify_lookahead(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.retract(MessageRetractionHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.change_attribute_order_type(ObjectInstanceHandle(999), set(), OrderType.RECEIVE)
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_time_constrained()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("time-tail-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    owner.publish_object_class_attributes(cls, {attr})
    observer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Time-Tail-Negative")

    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.modify_lookahead(1.0)
    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(AttributeNotOwned):
        observer.change_attribute_order_type(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.change_attribute_order_type(ObjectInstanceHandle(999), {attr}, OrderType.RECEIVE)
    with pytest.raises(AttributeNotDefined):
        owner.change_attribute_order_type(obj, {bad_attr}, OrderType.RECEIVE)

    owner.enable_time_regulation(owner.get_time_factory().make_interval(1.0))
    drain(owner, observer)
    owner.enable_time_constrained()
    drain(owner, observer)
    with pytest.raises(TimeConstrainedAlreadyEnabled):
        owner.enable_time_constrained()

    owner.disable_time_regulation()
    owner.request_federation_save("TIME-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.modify_lookahead(1.0)
    with pytest.raises(SaveInProgress):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(SaveInProgress):
        owner.change_attribute_order_type(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(SaveInProgress):
        observer.enable_time_constrained()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("TIME-TAIL-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.modify_lookahead(1.0)
    with pytest.raises(RestoreInProgress):
        owner.retract(MessageRetractionHandle(1))
    with pytest.raises(RestoreInProgress):
        owner.change_attribute_order_type(obj, {attr}, OrderType.RECEIVE)
    with pytest.raises(RestoreInProgress):
        observer.enable_time_constrained()

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.enable_time_regulation(owner.get_time_factory().make_interval(1.0))
    owner.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        owner.modify_lookahead(1.0)
    with pytest.raises(InvalidMessageRetractionHandle):
        owner.retract("bad")
    owner.backend.state.time_advancing = False
    owner.disable_time_regulation()

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("time-tail-negative-fed")


def test_change_interaction_order_type_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.change_interaction_order_type(object(), OrderType.RECEIVE)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.change_interaction_order_type(object(), OrderType.RECEIVE)
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("interaction-order-negative-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    owner.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        owner.change_interaction_order_type(interaction, OrderType.RECEIVE)
    with pytest.raises(InteractionClassNotDefined):
        owner.change_interaction_order_type(type(interaction)(interaction.value + 1000), OrderType.RECEIVE)

    owner.request_federation_save("INTERACTION-ORDER-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.change_interaction_order_type(interaction, OrderType.RECEIVE)

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("INTERACTION-ORDER-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.change_interaction_order_type(interaction, OrderType.RECEIVE)

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("interaction-order-negative-fed")


def test_async_delivery_and_time_query_disable_tail_reject_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.enable_asynchronous_delivery()
    with pytest.raises(NotConnected):
        rti.disable_asynchronous_delivery()
    with pytest.raises(NotConnected):
        rti.query_lookahead()
    with pytest.raises(NotConnected):
        rti.disable_time_regulation()
    with pytest.raises(NotConnected):
        rti.disable_time_constrained()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_asynchronous_delivery()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_asynchronous_delivery()
    with pytest.raises(FederateNotExecutionMember):
        rti.query_lookahead()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_time_regulation()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_time_constrained()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("async-time-tail-negative-fed")
    with pytest.raises(AsynchronousDeliveryAlreadyDisabled):
        owner.disable_asynchronous_delivery()
    owner.enable_asynchronous_delivery()
    with pytest.raises(AsynchronousDeliveryAlreadyEnabled):
        owner.enable_asynchronous_delivery()
    owner.disable_asynchronous_delivery()

    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.query_lookahead()
    with pytest.raises(TimeRegulationIsNotEnabled):
        owner.disable_time_regulation()
    with pytest.raises(TimeConstrainedIsNotEnabled):
        owner.disable_time_constrained()

    owner.request_federation_save("ASYNC-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enable_asynchronous_delivery()
    with pytest.raises(SaveInProgress):
        owner.disable_asynchronous_delivery()
    with pytest.raises(SaveInProgress):
        owner.query_lookahead()
    with pytest.raises(SaveInProgress):
        owner.disable_time_regulation()
    with pytest.raises(SaveInProgress):
        owner.disable_time_constrained()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("ASYNC-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enable_asynchronous_delivery()
    with pytest.raises(RestoreInProgress):
        owner.disable_asynchronous_delivery()
    with pytest.raises(RestoreInProgress):
        owner.query_lookahead()
    with pytest.raises(RestoreInProgress):
        owner.disable_time_regulation()
    with pytest.raises(RestoreInProgress):
        owner.disable_time_constrained()

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("async-time-tail-negative-fed")


def test_enable_time_regulation_rejects_not_connected_not_joined_invalid_lookahead_duplicate_save_restore_and_time_advancing():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.enable_time_regulation(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_time_regulation(object())
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("enable-time-reg-negative-fed")
    factory = owner.get_time_factory()

    with pytest.raises(InvalidLookahead):
        owner.enable_time_regulation(factory.make_interval(-1.0))

    owner.enable_time_regulation(factory.make_interval(1.0))
    drain(owner, observer)
    with pytest.raises(TimeRegulationAlreadyEnabled):
        owner.enable_time_regulation(factory.make_interval(1.0))

    owner.disable_time_regulation()
    owner.request_federation_save("ENABLE-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enable_time_regulation(factory.make_interval(1.0))

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("ENABLE-TIME-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enable_time_regulation(factory.make_interval(1.0))

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        owner.enable_time_regulation(factory.make_interval(1.0))
    owner.backend.state.time_advancing = False

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("enable-time-reg-negative-fed")


def test_time_enable_callbacks_are_not_emitted_on_failed_requests():
    _, owner, observer, owner_fed, observer_fed, _h1, _h2 = joined_pair("time-enable-callback-negative-fed")
    factory = owner.get_time_factory()

    owner_fed.clear()
    with pytest.raises(InvalidLookahead):
        owner.enable_time_regulation(factory.make_interval(-1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []

    owner.enable_time_regulation(factory.make_interval(1.0))
    drain(owner, observer)
    assert owner_fed.last_callback("timeRegulationEnabled") is not None

    owner_fed.clear()
    with pytest.raises(TimeRegulationAlreadyEnabled):
        owner.enable_time_regulation(factory.make_interval(1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []

    observer.enable_time_constrained()
    drain(owner, observer)
    assert observer_fed.last_callback("timeConstrainedEnabled") is not None

    observer_fed.clear()
    with pytest.raises(TimeConstrainedAlreadyEnabled):
        observer.enable_time_constrained()
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.disable_time_regulation()
    observer.disable_time_constrained()

    owner.request_federation_save("TIME-ENABLE-CB-SAVE")
    drain(owner, observer)
    owner_fed.clear()
    observer_fed.clear()
    with pytest.raises(SaveInProgress):
        owner.enable_time_regulation(factory.make_interval(1.0))
    with pytest.raises(SaveInProgress):
        observer.enable_time_constrained()
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("TIME-ENABLE-CB-SAVE")
    drain(owner, observer)
    owner_fed.clear()
    observer_fed.clear()
    with pytest.raises(RestoreInProgress):
        owner.enable_time_regulation(factory.make_interval(1.0))
    with pytest.raises(RestoreInProgress):
        observer.enable_time_constrained()
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    assert observer_fed.callbacks_named("timeConstrainedEnabled") == []

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.backend.state.time_advancing = True
    owner_fed.clear()
    with pytest.raises(InTimeAdvancingState):
        owner.enable_time_regulation(factory.make_interval(1.0))
    assert owner_fed.callbacks_named("timeRegulationEnabled") == []
    owner.backend.state.time_advancing = False

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("time-enable-callback-negative-fed")


def test_support_service_lookup_and_factory_tail_rejects_declared_exceptions():
    factory_getters = (
        lambda tx: tx.get_attribute_handle_factory(),
        lambda tx: tx.get_attribute_handle_set_factory(),
        lambda tx: tx.get_attribute_handle_value_map_factory(),
        lambda tx: tx.get_attribute_set_region_set_pair_list_factory(),
        lambda tx: tx.get_dimension_handle_factory(),
        lambda tx: tx.get_dimension_handle_set_factory(),
        lambda tx: tx.get_federate_handle_factory(),
        lambda tx: tx.get_federate_handle_set_factory(),
        lambda tx: tx.get_interaction_class_handle_factory(),
        lambda tx: tx.get_object_class_handle_factory(),
        lambda tx: tx.get_object_instance_handle_factory(),
        lambda tx: tx.get_parameter_handle_factory(),
        lambda tx: tx.get_parameter_handle_value_map_factory(),
        lambda tx: tx.get_region_handle_set_factory(),
        lambda tx: tx.get_transportation_type_handle_factory(),
    )

    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.get_federate_name(None)
    with pytest.raises(NotConnected):
        rti.get_attribute_handle(object(), "Position")
    with pytest.raises(NotConnected):
        rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    with pytest.raises(NotConnected):
        rti.get_parameter_handle(object(), "TrackId")
    with pytest.raises(NotConnected):
        rti.get_object_instance_name(ObjectInstanceHandle(1))
    with pytest.raises(NotConnected):
        rti.get_update_rate_value("default")
    with pytest.raises(NotConnected):
        rti.get_update_rate_value_for_attribute(ObjectInstanceHandle(1), AttributeHandle(1))
    with pytest.raises(NotConnected):
        rti.get_transportation_type("HLAreliable")
    with pytest.raises(NotConnected):
        rti.get_transportation_name(TransportationTypeHandle(1))
    with pytest.raises(NotConnected):
        rti.get_automatic_resign_directive()
    with pytest.raises(NotConnected):
        rti.set_automatic_resign_directive(ResignAction.NO_ACTION)
    with pytest.raises(NotConnected):
        rti.normalize_federate_handle(object())
    with pytest.raises(NotConnected):
        rti.normalize_service_group("OBJECT_MANAGEMENT")
    with pytest.raises(NotConnected):
        rti.enable_interaction_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.disable_interaction_relevance_advisory_switch()
    with pytest.raises(NotConnected):
        rti.get_time_factory()
    for getter in factory_getters:
        with pytest.raises(NotConnected):
            getter(rti)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.get_federate_name(None)
    with pytest.raises(FederateNotExecutionMember):
        rti.get_attribute_handle(object(), "Position")
    with pytest.raises(FederateNotExecutionMember):
        rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    with pytest.raises(FederateNotExecutionMember):
        rti.get_parameter_handle(object(), "TrackId")
    with pytest.raises(FederateNotExecutionMember):
        rti.get_object_instance_name(ObjectInstanceHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.get_update_rate_value("default")
    with pytest.raises(FederateNotExecutionMember):
        rti.get_update_rate_value_for_attribute(ObjectInstanceHandle(1), AttributeHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.get_transportation_type("HLAreliable")
    with pytest.raises(FederateNotExecutionMember):
        rti.get_transportation_name(TransportationTypeHandle(1))
    with pytest.raises(FederateNotExecutionMember):
        rti.get_automatic_resign_directive()
    with pytest.raises(FederateNotExecutionMember):
        rti.set_automatic_resign_directive(ResignAction.NO_ACTION)
    with pytest.raises(FederateNotExecutionMember):
        rti.normalize_federate_handle(object())
    with pytest.raises(FederateNotExecutionMember):
        rti.normalize_service_group("OBJECT_MANAGEMENT")
    with pytest.raises(FederateNotExecutionMember):
        rti.enable_interaction_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.disable_interaction_relevance_advisory_switch()
    with pytest.raises(FederateNotExecutionMember):
        rti.get_time_factory()
    for getter in factory_getters:
        with pytest.raises(FederateNotExecutionMember):
            getter(rti)
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, owner_handle, observer_handle = joined_pair("support-lookup-tail-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    object_handle = owner.register_object_instance(cls, "support-tail-object")

    bad_class = type(cls)(cls.value + 999)
    bad_interaction = type(interaction)(interaction.value + 999)
    bad_object = ObjectInstanceHandle(object_handle.value + 999)
    bad_dim = DimensionHandle(999999)
    bad_attr = AttributeHandle(999999)

    with pytest.raises(FederateHandleNotKnown):
        owner.get_federate_name(type(owner_handle)(owner_handle.value + observer_handle.value + 1000))
    with pytest.raises(InvalidFederateHandle):
        owner.get_federate_name(object())
    with pytest.raises(NameNotFound):
        owner.get_federate_handle("no-such-federate")
    with pytest.raises(NameNotFound):
        owner.get_object_class_handle("HLAobjectRoot.NoSuchClass")
    with pytest.raises(InvalidObjectClassHandle):
        owner.get_object_class_name(bad_class)
    with pytest.raises(InvalidObjectClassHandle):
        owner.get_attribute_handle(bad_class, "Position")
    with pytest.raises(NameNotFound):
        owner.get_attribute_handle(cls, "NoSuchAttribute")
    with pytest.raises(NameNotFound):
        owner.get_interaction_class_handle("HLAinteractionRoot.NoSuchInteraction")
    with pytest.raises(InvalidInteractionClassHandle):
        owner.get_interaction_class_name(bad_interaction)
    with pytest.raises(InvalidInteractionClassHandle):
        owner.get_parameter_handle(bad_interaction, "TrackId")
    with pytest.raises(NameNotFound):
        owner.get_parameter_handle(interaction, "NoSuchParameter")
    with pytest.raises(AttributeNotDefined):
        owner.get_update_rate_value_for_attribute(object_handle, bad_attr)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.get_update_rate_value_for_attribute(bad_object, attr)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.get_object_instance_name(bad_object)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.get_object_instance_handle("no-such-object")
    with pytest.raises(ObjectInstanceNotKnown):
        owner.get_known_object_class_handle(bad_object)
    with pytest.raises(InvalidUpdateRateDesignator):
        owner.get_update_rate_value("bogus-rate")
    with pytest.raises(InvalidInteractionClassHandle):
        owner.get_available_dimensions_for_interaction_class(bad_interaction)
    with pytest.raises(NameNotFound):
        owner.get_dimension_handle("NoSuchDimension")
    with pytest.raises(InvalidDimensionHandle):
        owner.get_dimension_name(bad_dim)
    with pytest.raises(InvalidDimensionHandle):
        owner.get_dimension_upper_bound(bad_dim)
    with pytest.raises(InvalidResignAction):
        owner.set_automatic_resign_directive(object())
    with pytest.raises(InvalidFederateHandle):
        owner.normalize_federate_handle(object())
    with pytest.raises(InvalidServiceGroup):
        owner.normalize_service_group("not-a-group")
    with pytest.raises(InvalidOrderType):
        owner.get_order_name(object())
    with pytest.raises(InvalidOrderName):
        owner.get_order_type("bogus-order")
    with pytest.raises(InvalidTransportationName):
        owner.get_transportation_type_handle("bogus-transport")
    with pytest.raises(InvalidTransportationName):
        owner.get_transportation_type("bogus-transport")
    with pytest.raises(InvalidTransportationType):
        owner.get_transportation_type_name(TransportationTypeHandle(999))
    with pytest.raises(InvalidTransportationType):
        owner.get_transportation_name(TransportationTypeHandle(999))
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOff):
        owner.disable_interaction_relevance_advisory_switch()
    owner.enable_interaction_relevance_advisory_switch()
    with pytest.raises(InteractionRelevanceAdvisorySwitchIsOn):
        owner.enable_interaction_relevance_advisory_switch()
    owner.disable_interaction_relevance_advisory_switch()
    assert owner.get_update_rate_value_for_attribute(object_handle, attr) == 0.0

    owner.request_federation_save("SUPPORT-LOOKUP-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enable_interaction_relevance_advisory_switch()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("SUPPORT-LOOKUP-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.disable_interaction_relevance_advisory_switch()

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-lookup-tail-fed")


class _ImmediateSupportCallbackAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti
        self.captured: list[type[BaseException]] = []

    def synchronizationPointRegistrationSucceeded(self, label):
        super().synchronizationPointRegistrationSucceeded(label)
        for fn, args in (
            (self.rti.evoke_callback, (0.0,)),
            (self.rti.evoke_multiple_callbacks, (0.0, 0.0)),
        ):
            try:
                fn(*args)
            except CallNotAllowedFromWithinCallback:
                self.captured.append(CallNotAllowedFromWithinCallback)


def test_callback_controls_reject_save_restore_and_within_callback_evoke():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("support-callback-tail-fed")
    owner.request_federation_save("SUPPORT-CALLBACK-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.enable_callbacks()
    with pytest.raises(SaveInProgress):
        owner.disable_callbacks()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("SUPPORT-CALLBACK-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.enable_callbacks()
    with pytest.raises(RestoreInProgress):
        owner.disable_callbacks()
    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-callback-tail-fed")

    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    fed = _ImmediateSupportCallbackAmbassador(rti)
    rti.connect(fed, CallbackModel.HLA_IMMEDIATE)
    rti.create_federation_execution("support-immediate-callback-fed", "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("alpha", "type-a", "support-immediate-callback-fed")
    rti.register_federation_synchronization_point("IMMEDIATE-CALLBACK", b"x")
    assert fed.captured == [CallNotAllowedFromWithinCallback, CallNotAllowedFromWithinCallback]
    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution("support-immediate-callback-fed")
