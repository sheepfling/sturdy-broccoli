from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.python_rti import InMemoryRTIEngine, rti_ambassador
from hla2010.enums import CallbackModel, OrderType, ResignAction, SaveStatus
from hla2010.exceptions import (
    AttributeAcquisitionWasNotRequested,
    AttributeDivestitureWasNotRequested,
    NoAcquisitionPending,
)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("negotiated-ownership-fed")


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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("confirm-divestiture-fed")


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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-denied-fed")


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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("cancel-acquisition-fed")


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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
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

    owner.resign_federation_execution(ResignAction.NO_ACTION)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("release-denied-retains-owner-fed")
