from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction, ServiceGroup
from hla.rti1516e.handles import AttributeHandleSet, MessageRetractionHandle, RegionHandleSet
from hla.rti1516e.raw_api import API_METADATA
from hla.spec.refs import FOM_REFERENCES, method_reference
from hla.rti1516e.datatypes import AttributeRegionAssociation, RangeBounds
from hla.backends.common import DelegatingRTIAmbassador
from hla.backends.python1516e import InMemoryRTIEngine, PythonRTIBackend, rti_ambassador


def drain(*rtis):
    for _ in range(20):
        any_pending = False
        for rti in rtis:
            any_pending = bool(rti.evokeMultipleCallbacks(0.0, 0.0)) or any_pending
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
    tx.createFederationExecution(federation_name, "TargetRadarFOMmodule.xml")
    tx_handle = tx.joinFederationExecution("producer", "target", federation_name)
    rx_handle = rx.joinFederationExecution("consumer", "radar", federation_name)
    return tx, rx, tx_fed, rx_fed, tx_handle, rx_handle


def cleanup(tx, rx, federation_name="extended-python-fed"):
    try:
        tx.resignFederationExecution(ResignAction.NO_ACTION)
    except Exception:
        tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    try:
        rx.resignFederationExecution(ResignAction.NO_ACTION)
    except Exception:
        rx.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
    tx.destroyFederationExecution(federation_name)
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
    assert method_reference("createFederationExecutionWithMIM").section == "4.5"
    assert FOM_REFERENCES["object_class_structure"].section == "4.2"
    assert FOM_REFERENCES["time_representation_table"].section == "4.7"

    fed = RecordingFederateAmbassador()
    fed.timeAdvanceGrant("time")
    assert fed.records[-1].reference.section == "8.13"


def test_python_rti_ddm_region_and_support_services_work_in_basic_form():
    tx, rx, tx_fed, rx_fed, *_ = build_two_federates()
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "RCS")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    region = tx.createRegion({dim})
    tx.setRangeBounds(region, dim, RangeBounds(10, 20))
    assert tx.getRangeBounds(region, dim) == RangeBounds(10, 20)
    rx_region = rx.createRegion({dim})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]
    rx.subscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    tx.publishObjectClassAttributes(cls, {attr})
    obj = tx.registerObjectInstanceWithRegions(cls, update_pairs, "Target-DDM")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    tx.associateRegionsForUpdates(obj, update_pairs)
    tx.unassociateRegionsForUpdates(obj, update_pairs)
    tx.updateAttributeValues(obj, {attr: b"12.5"}, b"tag")
    drain(tx, rx)
    assert rx_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"12.5"}

    rx.requestAttributeValueUpdateWithRegions(cls, subscription_pairs, b"refresh")
    drain(tx, rx)
    provide = tx_fed.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args[0] == obj

    assert dim in tx.getAvailableDimensionsForClassAttribute(cls, attr)
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    assert tx.getAvailableDimensionsForInteractionClass(interaction)
    assert tx.getDimensionUpperBound(dim) == (1 << 63) - 1
    assert tx.getOrderType("TimeStamp") is OrderType.TIMESTAMP
    assert tx.getOrderName(OrderType.RECEIVE) == "RECEIVE"
    reliable_handle = tx.getTransportationTypeHandle("HLAreliable")
    assert tx.getTransportationTypeName(reliable_handle) == "HLAreliable"
    assert tx.getTransportationType("HLAreliable") == reliable_handle
    assert tx.getTransportationName(reliable_handle) == "HLAreliable"
    assert tx.normalizeServiceGroup(ServiceGroup.FEDERATION_MANAGEMENT) is ServiceGroup.FEDERATION_MANAGEMENT
    assert tx.decodeMessageRetractionHandle(MessageRetractionHandle(99).encoded()) == MessageRetractionHandle(99)

    tx.setAutomaticResignDirective(ResignAction.NO_ACTION)
    assert tx.getAutomaticResignDirective() is ResignAction.NO_ACTION
    assert tx.getUpdateRateValue("default") == 0.0
    assert tx.getUpdateRateValueForAttribute(obj, attr) == 0.0

    tx.enableObjectClassRelevanceAdvisorySwitch()
    tx.disableObjectClassRelevanceAdvisorySwitch()
    tx.enableAttributeRelevanceAdvisorySwitch()
    tx.disableAttributeRelevanceAdvisorySwitch()
    tx.enableAttributeScopeAdvisorySwitch()
    tx.disableAttributeScopeAdvisorySwitch()
    tx.enableInteractionRelevanceAdvisorySwitch()
    tx.disableInteractionRelevanceAdvisorySwitch()

    cleanup(tx, rx)


def test_python_rti_sync_save_restore_and_ownership_services_have_basic_behavior():
    federation_name = "sync-save-restore-fed"
    tx, rx, tx_fed, rx_fed, tx_handle, rx_handle = build_two_federates(federation_name)

    tx.listFederationExecutions()
    drain(tx, rx)
    assert tx_fed.last_callback("reportFederationExecutions") is not None

    tx.registerFederationSynchronizationPoint("ready", b"go")
    drain(tx, rx)
    assert tx_fed.last_callback("synchronizationPointRegistrationSucceeded") is not None
    assert rx_fed.last_callback("announceSynchronizationPoint") is not None
    tx.synchronizationPointAchieved("ready")
    rx.synchronizationPointAchieved("ready")
    drain(tx, rx)
    assert tx_fed.last_callback("federationSynchronized") is not None
    assert rx_fed.last_callback("federationSynchronized") is not None

    tx.requestFederationSave("save-1")
    drain(tx, rx)
    assert tx_fed.last_callback("initiateFederateSave") is not None
    assert rx_fed.last_callback("initiateFederateSave") is not None
    tx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)
    assert tx_fed.last_callback("federationSaved") is not None

    tx.requestFederationRestore("save-1")
    drain(tx, rx)
    assert tx_fed.last_callback("requestFederationRestoreSucceeded") is not None
    assert rx_fed.last_callback("initiateFederateRestore") is not None
    tx.federateRestoreComplete()
    rx.federateRestoreComplete()
    drain(tx, rx)
    assert rx_fed.last_callback("federationRestored") is not None

    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "RCS")
    obj = tx.registerObjectInstance(cls, "Ownable-Target")
    rx.publishObjectClassAttributes(cls, {attr})
    tx.updateAttributeValues(obj, {attr: b"value"}, b"own")
    tx.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    rx.attributeOwnershipAcquisitionIfAvailable(obj, {attr})
    drain(tx, rx)
    assert rx_fed.last_callback("attributeOwnershipAcquisitionNotification") is not None
    rx.queryAttributeOwnership(obj, attr)
    drain(tx, rx)
    assert rx_fed.last_callback("informAttributeOwnership").args[-1] == rx_handle
    assert rx.isAttributeOwnedByFederate(obj, attr) is True

    cleanup(tx, rx, federation_name)
