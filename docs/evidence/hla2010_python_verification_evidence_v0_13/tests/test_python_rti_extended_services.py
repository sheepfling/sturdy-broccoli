from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.python_rti import InMemoryRTIEngine, rti_ambassador
from hla2010.enums import CallbackModel, OrderType, ResignAction, SaveStatus
from hla2010.handles import AttributeHandleSet, FederateHandleSet, MessageRetractionHandle
from hla2010.spec_refs import method_reference, method_label
from hla2010.types import RangeBounds, TimeQueryReturn


def drain(*rtis):
    for _ in range(20):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def joined_pair(name="extended-fed"):
    engine = InMemoryRTIEngine()
    r1 = rti_ambassador(engine=engine)
    r2 = rti_ambassador(engine=engine)
    f1 = RecordingFederateAmbassador()
    f2 = RecordingFederateAmbassador()
    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    h1 = r1.join_federation_execution("alpha", "type-a", name)
    h2 = r2.join_federation_execution("bravo", "type-b", name)
    return engine, r1, r2, f1, f2, h1, h2


def test_spec_references_link_services_to_clause_numbers():
    assert method_reference("connect").section == "4.2"
    assert method_reference("createFederationExecution").section == "4.5"
    assert method_reference("publishObjectClassAttributes").section == "5.2"
    assert method_reference("time_advance_grant").section == "8.13"
    assert "IEEE 1516.1-2010 §6.10" in method_label("update_attribute_values")


def test_recording_federate_ambassador_records_callback_references():
    fed = RecordingFederateAmbassador()
    fed.announceSynchronizationPoint("ready", b"tag")
    record = fed.last_callback("announceSynchronizationPoint")
    assert record.method_name == "announceSynchronizationPoint"
    assert record.reference.section == "4.13"
    assert record.snake_name == "announce_synchronization_point"


def test_synchronization_points_and_save_status_callbacks():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("sync-save-fed")
    r1.register_federation_synchronization_point("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationSucceeded").args == ("READY",)
    assert f2.last_callback("announceSynchronizationPoint").args[:2] == ("READY", b"sync")

    r1.synchronization_point_achieved("READY")
    r2.synchronization_point_achieved("READY")
    drain(r1, r2)
    assert f1.last_callback("federationSynchronized").args[0] == "READY"
    assert isinstance(f1.last_callback("federationSynchronized").args[1], FederateHandleSet)

    r1.request_federation_save("SAVE-1")
    drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-1",)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.query_federation_save_status()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("sync-save-fed")


def test_name_reservation_ddm_regions_ownership_and_time_support():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("ddm-ownership-fed")
    cls = r1.get_object_class_handle("HLAobjectRoot.Target")
    attr = r1.get_attribute_handle(cls, "Position")

    r1.reserve_object_instance_name("ReservedTarget")
    drain(r1)
    assert f1.last_callback("objectInstanceNameReservationSucceeded").args == ("ReservedTarget",)
    r2.reserve_object_instance_name("ReservedTarget")
    drain(r2)
    assert f2.last_callback("objectInstanceNameReservationFailed").args == ("ReservedTarget",)

    r1.publish_object_class_attributes(cls, {attr})
    obj = r1.register_object_instance(cls, "ReservedTarget")
    assert r1.is_attribute_owned_by_federate(obj, attr)
    r1.unconditional_attribute_ownership_divestiture(obj, {attr})
    assert not r1.is_attribute_owned_by_federate(obj, attr)
    r2.attribute_ownership_acquisition_if_available(obj, {attr})
    drain(r2)
    acquired = f2.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired.args[0] == obj
    assert isinstance(acquired.args[1], AttributeHandleSet)
    assert r2.is_attribute_owned_by_federate(obj, attr)
    r1.query_attribute_ownership(obj, attr)
    drain(r1)
    assert f1.last_callback("informAttributeOwnership").args == (obj, attr, h2)

    dim = r1.get_dimension_handle("HLAdefaultRoutingSpace")
    region = r1.create_region({dim})
    r1.set_range_bounds(region, dim, RangeBounds(10, 20))
    assert r1.get_range_bounds(region, dim) == RangeBounds(10, 20)
    assert r1.get_dimension_upper_bound(dim) > 20
    assert dim in r1.get_available_dimensions_for_class_attribute(cls, attr)

    assert r1.get_order_name(OrderType.RECEIVE) == "RECEIVE"
    assert r1.get_order_type("HLAreceive") is OrderType.RECEIVE
    assert r1.decode_message_retraction_handle(MessageRetractionHandle(7).encoded()) == MessageRetractionHandle(7)
    assert isinstance(r1.query_galt(), TimeQueryReturn)
    assert r1.normalize_federate_handle(h1) == h1

    r1.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("ddm-ownership-fed")
