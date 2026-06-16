from hla.rti1516e.ambassadors import RecordingFederateAmbassador
from hla.rti1516e.backends.base import DelegatingRTIAmbassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine, PythonRTIBackend, rti_ambassador
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction, ServiceGroup
from hla.rti1516e.handles import AttributeHandleSet, MessageRetractionHandle, RegionHandleSet
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e.spec_refs import FOM_REFERENCES, method_reference
from hla.rti1516e.datatypes import AttributeRegionAssociation, RangeBounds


def drain(*rtis):
    for _ in range(20):
        any_pending = False
        for rti in rtis:
            any_pending = bool(rti.evoke_multiple_callbacks(0.0, 0.0)) or any_pending
        if not any_pending:
            break


def build_two_federates(federation_name="extended-python-fed"):
    engine = InMemoryRTIEngine()
    tx = rti_ambassador(engine=engine)
    rx = rti_ambassador(engine=engine)
    tx_fed = RecordingFederateAmbassador()
    rx_fed = RecordingFederateAmbassador()
    tx.connect(tx_fed, CallbackModel.HLA_EVOKED)
    rx.connect(rx_fed, CallbackModel.HLA_EVOKED)
    tx.create_federation_execution(federation_name, "TargetRadarFOMmodule.xml")
    tx_handle = tx.join_federation_execution("producer", "target", federation_name)
    rx_handle = rx.join_federation_execution("consumer", "radar", federation_name)
    return tx, rx, tx_fed, rx_fed, tx_handle, rx_handle


def cleanup(tx, rx, federation_name="extended-python-fed"):
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution(federation_name)
    tx.disconnect()
    rx.disconnect()


def test_all_raw_ambassador_methods_have_section_references_and_python_rti_services():
    for ambassador_name, methods in API_METADATA.items():
        missing_refs = [method for method in methods if method_reference(method) is None]
        assert missing_refs == [], f"{ambassador_name} missing spec refs: {missing_refs}"

    missing_services = [
        method
        for method in API_METADATA["RTIambassador"]
        if not hasattr(PythonRTIBackend, f"_svc_{method}")
    ]
    assert missing_services == []

    assert "§4.2" in (DelegatingRTIAmbassador.connect.__doc__ or "")
    assert method_reference("joinFederationExecution").section == "4.9"
    assert method_reference("timeAdvanceGrant").section == "8.13"
    assert method_reference("create_federation_execution_with_mim").section == "4.5"
    assert FOM_REFERENCES["object_class_structure"].section == "4.2"
    assert FOM_REFERENCES["time_representation_table"].section == "4.7"

    fed = RecordingFederateAmbassador()
    fed.timeAdvanceGrant("time")
    assert fed.records[-1].reference.section == "8.13"


def test_python_rti_ddm_region_and_support_services_work_in_basic_form():
    tx, rx, tx_fed, rx_fed, *_ = build_two_federates()
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "RCS")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    region = tx.create_region({dim})
    tx.set_range_bounds(region, dim, RangeBounds(10, 20))
    assert tx.get_range_bounds(region, dim) == RangeBounds(10, 20)
    rx_region = rx.create_region({dim})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]
    rx.subscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    tx.publish_object_class_attributes(cls, {attr})
    obj = tx.register_object_instance_with_regions(cls, update_pairs, "Target-DDM")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    tx.associate_regions_for_updates(obj, update_pairs)
    tx.unassociate_regions_for_updates(obj, update_pairs)
    tx.update_attribute_values(obj, {attr: b"12.5"}, b"tag")
    drain(tx, rx)
    assert rx_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"12.5"}

    rx.request_attribute_value_update_with_regions(cls, subscription_pairs, b"refresh")
    drain(tx, rx)
    provide = tx_fed.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args[0] == obj

    assert dim in tx.get_available_dimensions_for_class_attribute(cls, attr)
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    assert tx.get_available_dimensions_for_interaction_class(interaction)
    assert tx.get_dimension_upper_bound(dim) == (1 << 63) - 1
    assert tx.get_order_type("TimeStamp") is OrderType.TIMESTAMP
    assert tx.get_order_name(OrderType.RECEIVE) == "RECEIVE"
    reliable_handle = tx.get_transportation_type_handle("HLAreliable")
    assert tx.get_transportation_type_name(reliable_handle) == "HLAreliable"
    assert tx.get_transportation_type("HLAreliable") == reliable_handle
    assert tx.get_transportation_name(reliable_handle) == "HLAreliable"
    assert tx.normalize_service_group(ServiceGroup.FEDERATION_MANAGEMENT) is ServiceGroup.FEDERATION_MANAGEMENT
    assert tx.decode_message_retraction_handle(MessageRetractionHandle(99).encoded()) == MessageRetractionHandle(99)

    tx.set_automatic_resign_directive(ResignAction.NO_ACTION)
    assert tx.get_automatic_resign_directive() is ResignAction.NO_ACTION
    assert tx.get_update_rate_value("default") == 0.0
    assert tx.get_update_rate_value_for_attribute(obj, attr) == 0.0

    tx.enable_object_class_relevance_advisory_switch()
    tx.disable_object_class_relevance_advisory_switch()
    tx.enable_attribute_relevance_advisory_switch()
    tx.disable_attribute_relevance_advisory_switch()
    tx.enable_attribute_scope_advisory_switch()
    tx.disable_attribute_scope_advisory_switch()
    tx.enable_interaction_relevance_advisory_switch()
    tx.disable_interaction_relevance_advisory_switch()

    cleanup(tx, rx)


def test_python_rti_sync_save_restore_and_ownership_services_have_basic_behavior():
    federation_name = "sync-save-restore-fed"
    tx, rx, tx_fed, rx_fed, tx_handle, rx_handle = build_two_federates(federation_name)

    tx.list_federation_executions()
    drain(tx, rx)
    assert tx_fed.last_callback("reportFederationExecutions") is not None

    tx.register_federation_synchronization_point("ready", b"go")
    drain(tx, rx)
    assert tx_fed.last_callback("synchronizationPointRegistrationSucceeded") is not None
    assert rx_fed.last_callback("announceSynchronizationPoint") is not None
    tx.synchronization_point_achieved("ready")
    rx.synchronization_point_achieved("ready")
    drain(tx, rx)
    assert tx_fed.last_callback("federationSynchronized") is not None
    assert rx_fed.last_callback("federationSynchronized") is not None

    tx.request_federation_save("save-1")
    drain(tx, rx)
    assert tx_fed.last_callback("initiateFederateSave") is not None
    assert rx_fed.last_callback("initiateFederateSave") is not None
    tx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)
    assert tx_fed.last_callback("federationSaved") is not None

    tx.request_federation_restore("save-1")
    drain(tx, rx)
    assert tx_fed.last_callback("requestFederationRestoreSucceeded") is not None
    assert rx_fed.last_callback("initiateFederateRestore") is not None
    tx.federate_restore_complete()
    rx.federate_restore_complete()
    drain(tx, rx)
    assert rx_fed.last_callback("federationRestored") is not None

    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "RCS")
    obj = tx.register_object_instance(cls, "Ownable-Target")
    tx.update_attribute_values(obj, {attr: b"value"}, b"own")
    tx.unconditional_attribute_ownership_divestiture(obj, {attr})
    rx.attribute_ownership_acquisition_if_available(obj, {attr})
    drain(tx, rx)
    assert rx_fed.last_callback("attributeOwnershipAcquisitionNotification") is not None
    rx.query_attribute_ownership(obj, attr)
    drain(tx, rx)
    assert rx_fed.last_callback("informAttributeOwnership").args[-1] == rx_handle
    assert rx.is_attribute_owned_by_federate(obj, attr) is True

    cleanup(tx, rx, federation_name)
