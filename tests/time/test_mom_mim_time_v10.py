from __future__ import annotations

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_python import InMemoryRTIEngine, PythonRTIConfig
from hla2010.enums import CallbackModel, OrderType
from hla2010.exceptions import InTimeAdvancingState, MessageCanNoLongerBeRetracted
from hla2010.handles import ObjectInstanceHandle
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010.types import MessageRetractionReturn, TimeQueryReturn
from tests.requirement_label_helpers import framework_document_title


def _rti(engine: InMemoryRTIEngine, *, config: PythonRTIConfig | None = None):
    return create_rti_ambassador("python", engine=engine, config=config)


def _drain(*rtis) -> None:
    for _ in range(20):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def _joined_pair(name: str):
    engine = InMemoryRTIEngine()
    sender = _rti(engine)
    receiver = _rti(engine)
    sender_fed = RecordingFederateAmbassador()
    receiver_fed = RecordingFederateAmbassador()
    sender.connect(sender_fed, CallbackModel.HLA_EVOKED)
    receiver.connect(receiver_fed, CallbackModel.HLA_EVOKED)
    sender.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    sender.joinFederationExecution("sender", "sender-type", name)
    receiver.joinFederationExecution("receiver", "receiver-type", name)
    return engine, sender, receiver, sender_fed, receiver_fed


def test_standard_mim_is_loaded_first_and_mom_names_are_discoverable():
    engine = InMemoryRTIEngine()
    config = PythonRTIConfig(strict_fom_loading=True, strict_fom_lookup=True)
    manager = _rti(engine, config=config)
    manager_fed = RecordingFederateAmbassador()
    manager.connect(manager_fed, CallbackModel.HLA_EVOKED)
    manager.createFederationExecution("mim-discovery-fed", "TargetRadarFOMmodule.xml")
    manager.joinFederationExecution("manager", "manager-type", "mim-discovery-fed")

    summary = manager.backend.current_fom_summary()
    assert summary["mim"] == f"Standard MOM and Initialization Module (MIM) for HLA {framework_document_title()}"
    assert summary["mim_uri"].endswith("HLAstandardMIM.xml")
    assert summary["module_uris"][-1].endswith("TargetRadarFOMmodule.xml")

    federation_class = manager.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederation")
    federate_class = manager.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederate")
    assert manager.getAttributeHandle(federation_class, "HLAfederationName")
    assert manager.getAttributeHandle(federate_class, "HLAfederateName")

    request = manager.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    )
    report = manager.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )
    assert manager.getParameterHandle(report, "HLAMIMdata")
    assert request != report


def test_mom_federation_object_can_be_discovered_and_reflected_on_request():
    engine, manager, worker, manager_fed, _ = _joined_pair("mom-object-fed")
    federation_class = manager.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_name = manager.getAttributeHandle(federation_class, "HLAfederationName")

    manager.subscribeObjectClassAttributes(federation_class, {federation_name})
    _drain(manager, worker)

    discoveries = manager_fed.callbacks_named("discoverObjectInstance")
    assert discoveries
    assert any("HLAmanager.HLAfederation.mom-object-fed" == rec.args[2] for rec in discoveries)

    mom_object = manager.backend.current_mom_summary()["federation_object"]
    assert isinstance(mom_object, ObjectInstanceHandle)
    manager.requestAttributeValueUpdate(mom_object, {federation_name}, b"mom-refresh")
    _drain(manager, worker)

    reflection = manager_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == mom_object
    assert federation_name in reflection.args[1]
    assert reflection.args[2] == b"mom-refresh"
    assert reflection.args[3] is OrderType.RECEIVE


def test_mom_request_mim_data_reports_bundled_mim_payload():
    engine, manager, worker, manager_fed, _ = _joined_pair("mom-report-fed")
    request = manager.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    )
    report = manager.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )
    payload_param = manager.getParameterHandle(report, "HLAMIMdata")

    manager.subscribeInteractionClass(report)
    manager.sendInteraction(request, {}, b"mim-request")
    _drain(manager, worker)

    record = manager_fed.last_callback("receiveInteraction")
    assert record is not None
    assert record.args[0] == report
    assert payload_param in record.args[1]
    assert b"<objectModel" in record.args[1][payload_param]
    assert b"HLAstandardMIM" in record.args[1][payload_param]


def test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits():
    engine, sender, receiver, sender_fed, receiver_fed = _joined_pair("time-order-fed")
    factory = sender.getTimeFactory()
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    interaction = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = sender.getParameterHandle(interaction, "TrackId")
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)

    sender.sendInteraction(interaction, {track_id: b"t3"}, b"tag3", factory.make_time(3.0))
    sender.sendInteraction(interaction, {track_id: b"t2"}, b"tag2", factory.make_time(2.0))
    _drain(sender, receiver)
    assert not receiver_fed.callbacks_named("receiveInteraction")

    initial_galt = receiver.queryGALT()
    assert isinstance(initial_galt, TimeQueryReturn)
    assert initial_galt.time_is_valid and initial_galt.time == factory.make_time(1.0)

    sender.timeAdvanceRequest(factory.make_time(4.0))
    _drain(sender, receiver)
    assert sender_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(4.0)

    assert receiver.queryGALT().time == factory.make_time(5.0)
    assert receiver.queryLITS().time == factory.make_time(2.0)

    receiver.nextMessageRequest(factory.make_time(5.0))
    _drain(sender, receiver)
    first = receiver_fed.callbacks_named("receiveInteraction")[-1]
    assert first.args[2] == b"tag2"
    assert first.args[5] == factory.make_time(2.0)
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(2.0)

    receiver.nextMessageRequest(factory.make_time(5.0))
    _drain(sender, receiver)
    second = receiver_fed.callbacks_named("receiveInteraction")[-1]
    assert second.args[2] == b"tag3"
    assert second.args[5] == factory.make_time(3.0)
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(3.0)


def test_time_advance_request_waits_at_galt_boundary_but_available_request_can_grant_equal_galt():
    engine, sender, receiver, sender_fed, receiver_fed = _joined_pair("galt-boundary-fed")
    factory = sender.getTimeFactory()
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)
    sender.timeAdvanceRequest(factory.make_time(4.0))
    _drain(sender, receiver)
    assert receiver.queryGALT().time == factory.make_time(5.0)

    receiver.timeAdvanceRequest(factory.make_time(5.0))
    _drain(sender, receiver)
    assert receiver_fed.last_callback("timeAdvanceGrant") is None
    # A second request while waiting demonstrates the Time Advancing precondition.
    try:
        receiver.timeAdvanceRequestAvailable(factory.make_time(5.0))
    except InTimeAdvancingState:
        pass
    else:  # pragma: no cover - defensive, the strict state machine should raise.
        raise AssertionError("expected InTimeAdvancingState")

    # Separate federate/federation for the available-service equal-GALT case.
    engine2, sender2, receiver2, _, receiver2_fed = _joined_pair("galt-available-fed")
    factory2 = sender2.getTimeFactory()
    sender2.enableTimeRegulation(factory2.make_interval(1.0))
    receiver2.enableTimeConstrained()
    _drain(sender2, receiver2)
    sender2.timeAdvanceRequest(factory2.make_time(4.0))
    _drain(sender2, receiver2)
    receiver2.timeAdvanceRequestAvailable(factory2.make_time(5.0))
    _drain(sender2, receiver2)
    assert receiver2_fed.last_callback("timeAdvanceGrant").args[0] == factory2.make_time(5.0)


def test_retract_removes_queued_tso_message_before_grant():
    engine, sender, receiver, _, receiver_fed = _joined_pair("retract-time-fed")
    factory = sender.getTimeFactory()
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    interaction = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = sender.getParameterHandle(interaction, "TrackId")
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)

    retraction = sender.sendInteraction(interaction, {track_id: b"withdrawn"}, b"withdraw", factory.make_time(2.0))
    assert isinstance(retraction, MessageRetractionReturn)
    sender.retract(retraction.handle)
    try:
        sender.retract(retraction.handle)
    except MessageCanNoLongerBeRetracted:
        pass
    else:  # pragma: no cover - defensive, repeated retract should fail.
        raise AssertionError("expected MessageCanNoLongerBeRetracted")

    sender.timeAdvanceRequest(factory.make_time(4.0))
    _drain(sender, receiver)
    receiver.timeAdvanceRequestAvailable(factory.make_time(5.0))
    _drain(sender, receiver)
    assert not receiver_fed.callbacks_named("receiveInteraction")
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(5.0)
