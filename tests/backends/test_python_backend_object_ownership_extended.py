# ruff: noqa: F401,F403

from tests.backends.python_backend_extended_support import *

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

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("transport-negative-fed")
    with pytest.raises(ObjectInstanceNotKnown):
        owner.request_attribute_transportation_type_change(ObjectInstanceHandle(999), set(), owner.backend.engine.transportation_reliable)

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

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("interaction-transport-negative-fed")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

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

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("query-transport-reserve-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "QueryTransport")

    with pytest.raises(ObjectInstanceNotKnown):
        owner.query_attribute_transportation_type(ObjectInstanceHandle(999), attr)

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
    with pytest.raises(AttributeNotOwned):
        acquirer.confirm_divestiture(acquired, {attr}, b"tag")

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
    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    held = owner.register_object_instance(cls, "Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attribute_ownership_acquisition(ObjectInstanceHandle(999), {attr}, b"tag")
    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.attribute_ownership_acquisition_if_available(ObjectInstanceHandle(999), {attr})
    with pytest.raises(FederateOwnsAttributes):
        owner.attribute_ownership_acquisition(held, {attr}, b"tag")
    with pytest.raises(FederateOwnsAttributes):
        owner.attribute_ownership_acquisition_if_available(held, {attr})

    acquirer.attribute_ownership_acquisition_if_available(held, {attr})
    with pytest.raises(AttributeAlreadyBeingAcquired):
        acquirer.attribute_ownership_acquisition_if_available(held, {attr})

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
    with pytest.raises(ObjectInstanceNotKnown):
        owner.query_attribute_ownership(ObjectInstanceHandle(999), attr)
    with pytest.raises(ObjectInstanceNotKnown):
        owner.is_attribute_owned_by_federate(ObjectInstanceHandle(999), attr)

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
    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Cancel-Acquisition-Negative")

    with pytest.raises(ObjectInstanceNotKnown):
        acquirer.cancel_attribute_ownership_acquisition(ObjectInstanceHandle(999), {attr})

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
