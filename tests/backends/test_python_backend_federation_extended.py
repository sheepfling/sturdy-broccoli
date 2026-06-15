# ruff: noqa: F401,F403

import pytest

from hla2010 import mom as hla_mom
from tests.backends.python_backend_extended_support import *
from hla2010.fom import FOMModule
from hla2010_rti_python import PythonRTIConfig
from hla2010.enums import (
    CallbackModel,
    ResignAction,
    RestoreFailureReason,
    RestoreStatus,
    SaveFailureReason,
    SaveStatus,
    SynchronizationPointFailureReason,
)
from hla2010.exceptions import *
from hla2010.exceptions import (
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFDD,
    CouldNotOpenMIM,
    ErrorReadingFDD,
    ErrorReadingMIM,
    InconsistentFDD,
)
from hla2010.handles import FederateHandleSet
from tests.requirement_marker_groups import (
    FM_CONNECT_REQUIREMENTS,
    FM_CREATE_FEDERATION_REQUIREMENTS,
    FM_DESTROY_FEDERATION_REQUIREMENTS,
    FM_DISCONNECT_REQUIREMENTS,
    FM_RESIGN_FEDERATION_REQUIREMENTS,
)
from hla2010.spec_refs import method_label, method_reference

def test_spec_references_link_services_to_clause_numbers():
    assert method_reference("connect").section == "4.2"
    assert method_reference("createFederationExecution").section == "4.5"
    assert method_reference("publishObjectClassAttributes").section == "5.2"
    assert method_reference("time_advance_grant").section == "8.13"
    assert "IEEE 1516.1-2010 (2010 edition) §6.10" in method_label("updateAttributeValues")


def test_recording_federate_ambassador_records_callback_references():
    fed = RecordingFederateAmbassador()
    fed.announceSynchronizationPoint("ready", b"tag")
    record = fed.last_callback("announceSynchronizationPoint")
    assert record.method_name == "announceSynchronizationPoint"
    assert record.reference.section == "4.13"
    assert record.snake_name == "announce_synchronization_point"


def test_list_federation_executions_requires_connection_and_reports_known_federations():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.listFederationExecutions()

    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution("listed-fed", "TargetRadarFOMmodule.xml")
    rti.listFederationExecutions()
    drain(rti)

    callback = fed.last_callback("reportFederationExecutions")
    assert callback is not None
    infos = callback.args[0]
    assert any(info.federation_execution_name == "listed-fed" for info in infos)

    rti.destroyFederationExecution("listed-fed")
    rti.disconnect()


def test_destroy_federation_execution_removes_destroyed_federation_from_report_callback():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)

    rti.createFederationExecution("destroy-listed-fed", "TargetRadarFOMmodule.xml")
    rti.listFederationExecutions()
    drain(rti)
    infos = fed.last_callback("reportFederationExecutions").args[0]
    assert any(info.federation_execution_name == "destroy-listed-fed" for info in infos)

    rti.destroyFederationExecution("destroy-listed-fed")
    rti.listFederationExecutions()
    drain(rti)
    infos = fed.last_callback("reportFederationExecutions").args[0]
    assert all(info.federation_execution_name != "destroy-listed-fed" for info in infos)

    rti.disconnect()


def test_disconnect_clears_buffered_report_callbacks():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)

    rti.createFederationExecution("disconnect-buffered-fed", "TargetRadarFOMmodule.xml")
    rti.listFederationExecutions()
    assert fed.last_callback("reportFederationExecutions") is None
    assert rti.backend.state.queue

    rti.destroyFederationExecution("disconnect-buffered-fed")
    rti.disconnect()

    assert not rti.backend.state.queue
    assert fed.last_callback("reportFederationExecutions") is None


@pytest.mark.requirements(*FM_DISCONNECT_REQUIREMENTS)
def test_disconnect_is_observable_through_mom_service_invocation_reporting():
    engine, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("fm-disconnect-mom-report-fed")
    witness = rti_ambassador(engine=engine)
    witness_fed = RecordingFederateAmbassador()
    witness.connect(witness_fed, CallbackModel.HLA_EVOKED)
    witness.joinFederationExecution("charlie", "type-c", "fm-disconnect-mom-report-fed")

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
        b"enable-fm-disconnect-reporting",
    )
    drain(owner, observer, witness)
    assert owner.backend.state.service_reporting is True

    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.disconnect()
    drain(observer, witness)

    reports = [rec for rec in witness_fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]
    assert reports
    assert any(
        hla_mom.decode_text(rec.args[1][report_service]) == "disconnect"
        and hla_mom.decode_bool(rec.args[1][report_success])
        for rec in reports
    )
    assert owner.backend.state.connected is False

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    witness.resignFederationExecution(ResignAction.NO_ACTION)
    observer.destroyFederationExecution("fm-disconnect-mom-report-fed")


@pytest.mark.requirements(*FM_CONNECT_REQUIREMENTS)
def test_connect_establishes_callback_delivery_model_for_follow_on_reports():
    engine = InMemoryRTIEngine()

    evoked = rti_ambassador(engine=engine)
    evoked_fed = RecordingFederateAmbassador()
    evoked.connect(evoked_fed, CallbackModel.HLA_EVOKED)
    evoked.createFederationExecution("connect-callback-fed", "TargetRadarFOMmodule.xml")
    evoked.listFederationExecutions()
    assert evoked_fed.last_callback("reportFederationExecutions") is None
    drain(evoked)
    assert evoked_fed.last_callback("reportFederationExecutions") is not None
    evoked.destroyFederationExecution("connect-callback-fed")
    evoked.disconnect()

    immediate = rti_ambassador(engine=engine)
    immediate_fed = RecordingFederateAmbassador()
    immediate.connect(immediate_fed, CallbackModel.HLA_IMMEDIATE)
    immediate.createFederationExecution("connect-callback-fed-immediate", "TargetRadarFOMmodule.xml")
    immediate.listFederationExecutions()
    assert immediate_fed.last_callback("reportFederationExecutions") is not None
    immediate.destroyFederationExecution("connect-callback-fed-immediate")
    immediate.disconnect()


def test_connect_create_and_join_apply_positive_lifecycle_effects():
    engine = InMemoryRTIEngine()

    creator = rti_ambassador(engine=engine)
    creator_fed = RecordingFederateAmbassador()
    creator.connect(creator_fed, CallbackModel.HLA_EVOKED)

    assert creator.backend.state.connected is True
    assert creator.backend.state.callback_model is CallbackModel.HLA_EVOKED
    assert creator.backend.state.handle is None

    creator.createFederationExecution("fm-positive-lifecycle-fed", "TargetRadarFOMmodule.xml")
    federation = engine.federations["fm-positive-lifecycle-fed"]
    assert federation.name == "fm-positive-lifecycle-fed"

    joiner = rti_ambassador(engine=engine)
    joiner.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    handle = joiner.joinFederationExecution("alpha", "type-a", "fm-positive-lifecycle-fed")

    assert handle == joiner.backend.state.handle
    assert joiner.backend.state.federation is federation
    assert handle in federation.federates
    assert federation.federates[handle].name == "alpha"
    assert federation.federates[handle].federate_type == "type-a"

    joiner.resignFederationExecution(ResignAction.NO_ACTION)
    creator.destroyFederationExecution("fm-positive-lifecycle-fed")
    creator.disconnect()
    joiner.disconnect()


def test_connect_joined_federate_is_visible_in_mom_summary():
    _, r1, r2, _f1, _f2, h1, h2 = joined_pair("connect-mom-fed")

    summary = r1.backend.current_mom_summary()
    assert summary["federate_objects"][h1] == r1.backend.state.mom_federate_object
    assert summary["federate_objects"][h2] == r2.backend.state.mom_federate_object

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("connect-mom-fed")


def test_register_federation_synchronization_point_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.registerFederationSynchronizationPoint("READY", b"sync")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.registerFederationSynchronizationPoint("READY", b"sync")
    rti.disconnect()


def test_register_federation_synchronization_point_reports_duplicate_and_invalid_target_failures():
    _, r1, r2, f1, _f2, _h1, h2 = joined_pair("sync-negative-fed")

    r1.registerFederationSynchronizationPoint("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationSucceeded").args == ("READY",)

    r1.registerFederationSynchronizationPoint("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationFailed").args == (
        "READY",
        SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
    )

    invalid_handle = type(h2)(h2.value + 1000)
    r1.registerFederationSynchronizationPoint("BAD-TARGET", b"sync", {invalid_handle})
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationFailed").args == (
        "BAD-TARGET",
        SynchronizationPointFailureReason.SYNCHRONIZATION_SET_MEMBER_NOT_JOINED,
    )

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-negative-fed")


def test_register_federation_synchronization_point_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("sync-blocked-fed")

    r1.requestFederationSave("SYNC-SAVE")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.registerFederationSynchronizationPoint("BLOCKED", b"sync")

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore("SYNC-SAVE")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.registerFederationSynchronizationPoint("BLOCKED-RESTORE", b"sync")

    r1.abortFederationRestore()
    drain(r1, r2)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-blocked-fed")


def test_synchronization_point_achieved_rejects_not_connected_not_joined_and_unknown_label():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.synchronizationPointAchieved("READY")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.synchronizationPointAchieved("READY")
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, h2 = joined_pair("sync-achieve-negative-fed")
    with pytest.raises(SynchronizationPointLabelNotAnnounced):
        r1.synchronizationPointAchieved("UNKNOWN")

    r1.registerFederationSynchronizationPoint("KNOWN", b"sync", {h2})
    drain(r1, r2)
    with pytest.raises(SynchronizationPointLabelNotAnnounced):
        r1.synchronizationPointAchieved("KNOWN")

    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-achieve-negative-fed")


def test_synchronization_point_achieved_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("sync-achieve-blocked-fed")
    r1.registerFederationSynchronizationPoint("READY", b"sync")
    drain(r1, r2)

    r1.requestFederationSave("SYNC-ACHIEVE")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.synchronizationPointAchieved("READY")

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore("SYNC-ACHIEVE")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.synchronizationPointAchieved("READY")

    r1.abortFederationRestore()
    drain(r1, r2)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-achieve-blocked-fed")


def test_synchronization_points_and_save_status_callbacks():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("sync-save-fed")
    r1.registerFederationSynchronizationPoint("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationSucceeded").args == ("READY",)
    assert f2.last_callback("announceSynchronizationPoint").args[:2] == ("READY", b"sync")

    r1.synchronizationPointAchieved("READY")
    r2.synchronizationPointAchieved("READY")
    drain(r1, r2)
    assert f1.last_callback("federationSynchronized").args[0] == "READY"
    assert isinstance(f1.last_callback("federationSynchronized").args[1], FederateHandleSet)

    r1.requestFederationSave("SAVE-1")
    drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-1",)
    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.queryFederationSaveStatus()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-save-fed")


def test_synchronization_lifecycle_states_are_visible_in_mom_summary():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("sync-mom-fed")

    r1.registerFederationSynchronizationPoint("READY", b"sync")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["synchronization_labels"] == ["READY"]
    point = summary["synchronization_points"]["READY"]
    assert point["targets"] == [h1, h2]
    assert point["announced"] == [h1, h2]
    assert point["achieved"] == []
    assert point["failed"] == []
    assert point["reported"] == []
    assert point["open_to_late_joiners"] is True
    assert f1.last_callback("synchronizationPointRegistrationSucceeded").args == ("READY",)
    assert f2.last_callback("announceSynchronizationPoint").args[:2] == ("READY", b"sync")

    r1.synchronizationPointAchieved("READY")
    summary = r1.backend.current_mom_summary()
    point = summary["synchronization_points"]["READY"]
    assert point["achieved"] == [h1]
    assert point["reported"] == [h1]
    assert point["failed"] == []

    r2.synchronizationPointAchieved("READY", False)
    drain(r1, r2)
    assert f1.last_callback("federationSynchronized").args[0] == "READY"
    failed = f1.last_callback("federationSynchronized").args[1]
    assert h2 in failed
    summary = r1.backend.current_mom_summary()
    assert summary["synchronization_labels"] == []
    assert summary["synchronization_points"] == {}

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("sync-mom-fed")


def test_save_failure_reports_federation_not_saved_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("save-failure-fed")

    r1.requestFederationSave("SAVE-FAIL")
    drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-FAIL",)
    assert f2.last_callback("initiateFederateSave").args == ("SAVE-FAIL",)

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveNotComplete()
    drain(r1, r2)

    assert f1.last_callback("federationNotSaved").args == (
        SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
    )
    assert f2.last_callback("federationNotSaved").args == (
        SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
    )

    r1.queryFederationSaveStatus()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-failure-fed")


def test_abort_federation_save_reports_aborted_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("abort-save-fed")

    r1.requestFederationSave("SAVE-ABORT")
    drain(r1, r2)
    r1.federateSaveBegun()
    r2.federateSaveBegun()

    r1.abortFederationSave()
    drain(r1, r2)

    assert f1.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)
    assert f2.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)

    r1.queryFederationSaveStatus()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("abort-save-fed")


def test_abort_federation_save_requires_save_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("abort-save-invalid-fed")

    with pytest.raises(SaveNotInProgress):
        r1.abortFederationSave()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("abort-save-invalid-fed")


def test_federate_save_begun_rejects_not_connected_not_joined_and_missing_save():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federateSaveBegun()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federateSaveBegun()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-begun-negative-fed")
    with pytest.raises(SaveNotInitiated):
        r1.federateSaveBegun()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-begun-negative-fed")


def test_federate_save_complete_and_not_complete_reject_missing_save():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federateSaveComplete()
    with pytest.raises(NotConnected):
        rti.federateSaveNotComplete()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federateSaveComplete()
    with pytest.raises(FederateNotExecutionMember):
        rti.federateSaveNotComplete()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-complete-negative-fed")
    with pytest.raises(SaveNotInitiated):
        r1.federateSaveComplete()
    with pytest.raises(SaveNotInitiated):
        r1.federateSaveNotComplete()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-complete-negative-fed")


def test_request_federation_save_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestFederationSave("SAVE")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestFederationSave("SAVE")
    rti.disconnect()


def test_request_federation_save_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-negative-fed")

    r1.requestFederationSave("SAVE-NEG")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.requestFederationSave("SAVE-NEG-2")

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore("SAVE-NEG")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.requestFederationSave("SAVE-DURING-RESTORE")

    r1.abortFederationRestore()
    drain(r1, r2)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-negative-fed")


def test_request_federation_save_rejects_past_and_invalid_time():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-time-negative-fed")
    factory = r1.getTimeFactory()
    r1.enableTimeRegulation(factory.make_interval(1.0))
    drain(r1, r2)
    r1.timeAdvanceRequest(factory.make_time(5.0))
    drain(r1, r2)

    with pytest.raises(LogicalTimeAlreadyPassed):
        r1.requestFederationSave("PAST-SAVE", factory.make_time(4.0))

    with pytest.raises(InvalidLogicalTime):
        r1.requestFederationSave("BAD-SAVE", object())

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-time-negative-fed")


def test_query_federation_save_status_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.queryFederationSaveStatus()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.queryFederationSaveStatus()
    rti.disconnect()


def test_restore_status_response_and_failure_callback_paths():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("restore-failure-fed")

    r1.requestFederationSave("SAVE-RESTORE-FAIL")
    drain(r1, r2)
    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.requestFederationRestore("SAVE-RESTORE-FAIL")
    drain(r1, r2)
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-RESTORE-FAIL",)
    assert f2.last_callback("initiateFederateRestore").args == ("SAVE-RESTORE-FAIL", "bravo", h2)

    r1.queryFederationRestoreStatus()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    by_handle = {pair.pre_restore_handle: pair.restore_status for pair in status_response}
    assert by_handle[h1] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    assert by_handle[h2] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING

    r1.federateRestoreComplete()
    r2.federateRestoreNotComplete()
    drain(r1, r2)

    assert f1.last_callback("federationNotRestored").args == (
        RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
    )
    assert f2.last_callback("federationNotRestored").args == (
        RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
    )

    r1.queryFederationRestoreStatus()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("restore-failure-fed")


def test_abort_federation_restore_reports_aborted_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("abort-restore-fed")

    r1.requestFederationSave("SAVE-ABORT-RESTORE")
    drain(r1, r2)
    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.requestFederationRestore("SAVE-ABORT-RESTORE")
    drain(r1, r2)
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-ABORT-RESTORE",)

    r1.abortFederationRestore()
    drain(r1, r2)

    assert f1.last_callback("federationNotRestored").args == (RestoreFailureReason.RESTORE_ABORTED,)
    assert f2.last_callback("federationNotRestored").args == (RestoreFailureReason.RESTORE_ABORTED,)

    r1.queryFederationRestoreStatus()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("abort-restore-fed")


def test_abort_federation_restore_requires_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("abort-restore-invalid-fed")

    with pytest.raises(RestoreNotInProgress):
        r1.abortFederationRestore()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("abort-restore-invalid-fed")


def test_request_federation_restore_rejects_not_connected_not_joined_and_save_restore_in_progress():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestFederationRestore("SAVE")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestFederationRestore("SAVE")
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("restore-negative-fed")
    r1.requestFederationSave("SAVE-RESTORE-BLOCK")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.requestFederationRestore("SAVE-RESTORE-BLOCK")

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore("SAVE-RESTORE-BLOCK")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.requestFederationRestore("SAVE-RESTORE-BLOCK")

    r1.abortFederationRestore()
    drain(r1, r2)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("restore-negative-fed")


def test_federate_restore_complete_and_not_complete_reject_missing_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federateRestoreComplete()
    with pytest.raises(NotConnected):
        rti.federateRestoreNotComplete()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federateRestoreComplete()
    with pytest.raises(FederateNotExecutionMember):
        rti.federateRestoreNotComplete()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("restore-complete-negative-fed")
    with pytest.raises(RestoreNotRequested):
        r1.federateRestoreComplete()
    with pytest.raises(RestoreNotRequested):
        r1.federateRestoreNotComplete()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("restore-complete-negative-fed")


def test_request_federation_restore_failed_is_reported_for_unknown_save_label():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("restore-request-failed-fed")

    r1.requestFederationRestore("MISSING-SAVE")
    drain(r1, r2)

    assert f1.last_callback("requestFederationRestoreFailed").args == ("MISSING-SAVE",)
    assert f2.last_callback("requestFederationRestoreFailed") is None
    assert f1.last_callback("requestFederationRestoreSucceeded") is None
    assert f1.last_callback("federationRestoreStatusResponse") is None

    r1.queryFederationRestoreStatus()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("restore-request-failed-fed")


def test_query_federation_restore_status_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.queryFederationRestoreStatus()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.queryFederationRestoreStatus()
    rti.disconnect()


def test_disconnect_requires_resign_and_marks_backend_not_connected():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("disconnect-fed")

    with pytest.raises(FederateIsExecutionMember):
        r1.disconnect()

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r1.disconnect()

    with pytest.raises(NotConnected):
        r1.listFederationExecutions()

    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r2.destroyFederationExecution("disconnect-fed")
    r2.disconnect()


def test_join_federation_execution_requires_connection():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.joinFederationExecution("alpha", "type-a", "missing-fed")


def test_join_federation_execution_rejects_missing_federation():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.joinFederationExecution("alpha", "type-a", "missing-fed")
    rti.disconnect()


def test_join_federation_execution_rejects_duplicate_federate_name():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-duplicate-name-fed")
    r3 = rti_ambassador(engine=r1.backend.engine)
    r3.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(FederateNameAlreadyInUse):
        r3.joinFederationExecution("alpha", "type-c", "join-duplicate-name-fed")

    r3.disconnect()
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("join-duplicate-name-fed")


def test_join_federation_execution_rejects_already_joined_federate():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-already-member-fed")

    with pytest.raises(FederateAlreadyExecutionMember):
        r1.joinFederationExecution("other", "type-a", "join-already-member-fed")

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("join-already-member-fed")


def test_join_federation_execution_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-save-restore-fed")
    r3 = rti_ambassador(engine=r1.backend.engine)
    r3.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    r1.requestFederationSave("JOIN-BLOCK")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r3.joinFederationExecution("late-save", "type-c", "join-save-restore-fed")

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore("JOIN-BLOCK")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r3.joinFederationExecution("late-restore", "type-c", "join-save-restore-fed")

    r3.disconnect()
    r1.abortFederationRestore()
    drain(r1, r2)
    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("join-save-restore-fed")


def test_join_federation_execution_distinguishes_open_read_time_and_inconsistent_additional_fom_errors(tmp_path):
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(
        engine=engine,
        config=PythonRTIConfig(name="join-fom-negative-fed", strict_fom_loading=True),
    )
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution("join-fom-negative-fed", "TargetRadarFOMmodule.xml")

    missing_fdd = tmp_path / "missing-join-fed.xml"
    with pytest.raises(CouldNotOpenFDD):
        rti.joinFederationExecution("alpha", "type-a", "join-fom-negative-fed", [missing_fdd])

    bad_fdd = tmp_path / "bad-join-fed.xml"
    bad_fdd.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFDD):
        rti.joinFederationExecution("alpha", "type-a", "join-fom-negative-fed", [bad_fdd])

    rti_bad_time = rti_ambassador(
        engine=engine,
        config=PythonRTIConfig(
            name="join-fom-bad-time-fed",
            infer_time_factory_from_fom=False,
            default_logical_time_implementation_name="BogusLogicalTime",
        ),
    )
    rti_bad_time.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(CouldNotCreateLogicalTimeFactory):
        rti_bad_time.joinFederationExecution("time-alpha", "type-a", "join-fom-negative-fed")
    rti_bad_time.disconnect()

    good_time_int = tmp_path / "join-int-time.xml"
    good_time_float = tmp_path / "join-float-time.xml"
    good_time_int.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>JoinIntTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyJoinInt</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    good_time_float.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>JoinFloatTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyJoinFloat</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAfloat64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InconsistentFDD):
        rti.joinFederationExecution(
            "beta",
            "type-b",
            "join-fom-negative-fed",
            [good_time_int, good_time_float],
        )

    rti.destroyFederationExecution("join-fom-negative-fed")
    rti.disconnect()


def test_connect_rejects_second_connection_attempt():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(AlreadyConnected):
        rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.disconnect()


@pytest.mark.requirements(*FM_CREATE_FEDERATION_REQUIREMENTS)
def test_create_federation_execution_rejects_duplicate_name():
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution("duplicate-fed", "TargetRadarFOMmodule.xml")

    with pytest.raises(FederationExecutionAlreadyExists):
        rti.createFederationExecution("duplicate-fed", "TargetRadarFOMmodule.xml")

    rti.destroyFederationExecution("duplicate-fed")
    rti.disconnect()


def test_create_federation_execution_distinguishes_open_read_time_and_inconsistent_fom_errors(tmp_path):
    rti = rti_ambassador(
        engine=InMemoryRTIEngine(),
        config=PythonRTIConfig(name="create-fom-negative-fed", strict_fom_loading=True),
    )
    with pytest.raises(NotConnected):
        rti.createFederationExecution("missing-fed", tmp_path / "missing-fed.xml")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    missing_fdd = tmp_path / "missing-fed.xml"
    with pytest.raises(CouldNotOpenFDD):
        rti.createFederationExecution("missing-fed", missing_fdd)

    bad_fdd = tmp_path / "bad-fed.xml"
    bad_fdd.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFDD):
        rti.createFederationExecution("bad-fed", bad_fdd)

    missing_mim = tmp_path / "missing-mim.xml"
    with pytest.raises(CouldNotOpenMIM):
        rti.createFederationExecutionWithMIM(
            "missing-mim-fed",
            "TargetRadarFOMmodule.xml",
            missing_mim,
        )

    bad_mim = tmp_path / "bad-mim.xml"
    bad_mim.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingMIM):
        rti.createFederationExecutionWithMIM(
            "bad-mim-fed",
            "TargetRadarFOMmodule.xml",
            bad_mim,
        )

    rti_bad_time = rti_ambassador(
        engine=InMemoryRTIEngine(),
        config=PythonRTIConfig(
            name="create-fom-bad-time-fed",
            infer_time_factory_from_fom=False,
            default_logical_time_implementation_name="BogusLogicalTime",
        ),
    )
    rti_bad_time.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(CouldNotCreateLogicalTimeFactory):
        rti_bad_time.createFederationExecution("bogus-time-fed", "TargetRadarFOMmodule.xml")
    rti_bad_time.disconnect()

    int_time = tmp_path / "int-time.xml"
    float_time = tmp_path / "float-time.xml"
    int_time.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>IntTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyInt</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    float_time.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>FloatTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyFloat</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAfloat64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InconsistentFDD):
        rti.createFederationExecution("conflicting-time-fed", [int_time, float_time])

    rti.disconnect()


def test_create_federation_execution_with_explicit_mim_uses_requested_module():
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    rti.createFederationExecutionWithMIM(
        "explicit-mim-fed",
        "TargetRadarFOMmodule.xml",
        "hla2010/resources/foms/HLAstandardMIM.xml",
    )

    federation = engine.federations["explicit-mim-fed"]
    assert federation.mim_module is not None
    assert federation.mim_module.is_mim is True
    assert federation.mim_module.path is not None
    assert federation.mim_module.path.name == "HLAstandardMIM.xml"

    rti.destroyFederationExecution("explicit-mim-fed")
    rti.disconnect()


def test_create_federation_execution_with_mim_rejects_invalid_logical_time_factory():
    rti = rti_ambassador(
        engine=InMemoryRTIEngine(),
        config=PythonRTIConfig(
            name="create-mim-bad-time-fed",
            infer_time_factory_from_fom=False,
            default_logical_time_implementation_name="BogusLogicalTime",
        ),
    )
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(CouldNotCreateLogicalTimeFactory):
        rti.createFederationExecutionWithMIM(
            "bad-time-fed",
            "TargetRadarFOMmodule.xml",
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )

    rti.disconnect()


def test_create_federation_execution_with_mim_distinguishes_open_read_duplicate_and_inconsistent_fom_errors(tmp_path):
    rti = rti_ambassador(
        engine=InMemoryRTIEngine(),
        config=PythonRTIConfig(name="create-mim-fom-negative-fed", strict_fom_loading=True),
    )

    with pytest.raises(NotConnected):
        rti.createFederationExecutionWithMIM(
            "not-connected-fed",
            "TargetRadarFOMmodule.xml",
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    missing_fdd = tmp_path / "missing-mim-fdd.xml"
    with pytest.raises(CouldNotOpenFDD):
        rti.createFederationExecutionWithMIM(
            "missing-mim-fdd-fed",
            missing_fdd,
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )

    bad_fdd = tmp_path / "bad-mim-fdd.xml"
    bad_fdd.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFDD):
        rti.createFederationExecutionWithMIM(
            "bad-mim-fdd-fed",
            bad_fdd,
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )

    rti.createFederationExecutionWithMIM(
        "duplicate-mim-fed",
        "TargetRadarFOMmodule.xml",
        "hla2010/resources/foms/HLAstandardMIM.xml",
    )
    with pytest.raises(FederationExecutionAlreadyExists):
        rti.createFederationExecutionWithMIM(
            "duplicate-mim-fed",
            "TargetRadarFOMmodule.xml",
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )
    rti.destroyFederationExecution("duplicate-mim-fed")

    int_time = tmp_path / "mim-int-time.xml"
    float_time = tmp_path / "mim-float-time.xml"
    int_time.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>MimIntTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyMimInt</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    float_time.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<objectModel>
  <modelIdentification><name>MimFloatTimeFDD</name><type>FDD</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DummyMimFloat</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAfloat64BE</dataType></timeStamp>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InconsistentFDD):
        rti.createFederationExecutionWithMIM(
            "conflicting-mim-fed",
            [int_time, float_time],
            "hla2010/resources/foms/HLAstandardMIM.xml",
        )

    rti.disconnect()


def test_create_federation_execution_with_standard_mim_designator_is_rejected():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(DesignatorIsHLAstandardMIM):
        rti.createFederationExecutionWithMIM(
            "invalid-mim-fed",
            "TargetRadarFOMmodule.xml",
            "HLAstandardMIM",
        )
    rti.disconnect()


@pytest.mark.requirements(*FM_DESTROY_FEDERATION_REQUIREMENTS)
def test_destroy_federation_execution_requires_no_joined_federates():
    engine, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("destroy-fed")

    with pytest.raises(FederatesCurrentlyJoined):
        r1.destroyFederationExecution("destroy-fed")

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("destroy-fed")
    assert "destroy-fed" not in engine.federations


def test_destroy_federation_execution_rejects_missing_federation():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.destroyFederationExecution("missing-fed")
    rti.disconnect()


@pytest.mark.requirements(*FM_RESIGN_FEDERATION_REQUIREMENTS)
def test_resign_federation_execution_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.resignFederationExecution(ResignAction.NO_ACTION)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.disconnect()


def test_resign_federation_execution_rejects_invalid_action_and_owned_attributes():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("resign-negative-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    owner.registerObjectInstance(cls, "Owned-Target")

    with pytest.raises(InvalidResignAction):
        owner.resignFederationExecution("bogus")

    with pytest.raises(FederateOwnsAttributes):
        owner.resignFederationExecution(ResignAction.NO_ACTION)

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    observer.destroyFederationExecution("resign-negative-fed")


@pytest.mark.parametrize(
    "resign_action",
    [
        ResignAction.DELETE_OBJECTS,
        ResignAction.DELETE_OBJECTS_THEN_DIVEST,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    ],
    ids=[
        "delete_objects",
        "delete_objects_then_divest",
        "cancel_then_delete_then_divest",
    ],
)
def test_resign_delete_object_directives_clear_membership_and_owned_objects(resign_action):
    _, owner, observer, _owner_fed, observer_fed, owner_handle, _observer_handle = joined_pair(
        f"resign-positive-{resign_action.name.lower()}-fed"
    )
    federation = owner.backend.state.federation
    assert federation is not None

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})
    obj = owner.registerObjectInstance(cls, f"Owned-{resign_action.name}")
    owner.updateAttributeValues(obj, {attr: b"10,20"}, b"init")
    drain(owner, observer)

    assert obj in federation.objects
    assert federation.objects[obj].owner == owner_handle

    owner.resignFederationExecution(resign_action)
    drain(observer)

    assert owner.backend.state.handle is None
    assert owner.backend.state.federation is None
    assert owner_handle not in federation.federates
    assert obj not in federation.objects
    assert all(
        instance.owner != owner_handle
        and owner_handle not in instance.attribute_owners.values()
        for instance in federation.objects.values()
    )
    removed = observer_fed.last_callback("removeObjectInstance")
    assert removed is not None
    assert removed.args[0] == obj

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    observer.destroyFederationExecution(f"resign-positive-{resign_action.name.lower()}-fed")


def test_resign_federation_execution_rejects_pending_acquisition():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("resign-pending-acquisition-fed")
    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    acquirer.publishObjectClassAttributes(cls, {attr})

    pending = owner.registerObjectInstance(cls, "Pending-Acquisition")
    acquirer.attributeOwnershipAcquisition(pending, {attr}, b"req")
    drain(owner, acquirer)

    with pytest.raises(OwnershipAcquisitionPending):
        acquirer.resignFederationExecution(ResignAction.NO_ACTION)

    owner.attributeOwnershipReleaseDenied(pending, {attr})
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    acquirer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("resign-pending-acquisition-fed")


def test_resign_federation_execution_removes_mom_federate_object_and_refreshes_summary():
    _, r1, r2, _f1, _f2, h1, _h2 = joined_pair("resign-mom-cleanup-fed")
    federation = r1.backend.state.federation
    assert federation is not None

    mom_handle = federation.mom_federate_objects[h1]
    assert mom_handle in federation.objects

    r1.resignFederationExecution(ResignAction.NO_ACTION)

    assert h1 not in federation.mom_federate_objects
    assert mom_handle not in federation.objects
    summary = r2.backend.current_mom_summary()
    assert h1 not in summary["federate_objects"]

    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r2.destroyFederationExecution("resign-mom-cleanup-fed")


def test_save_restore_keeps_mom_summary_coherent_for_joined_federates():
    _, r1, r2, f1, _f2, h1, h2 = joined_pair("save-restore-mom-fed")
    summary = r1.backend.current_mom_summary()
    assert summary["federate_objects"][h1] == r1.backend.state.mom_federate_object
    assert summary["federate_objects"][h2] == r2.backend.state.mom_federate_object

    r1.requestFederationSave("SAVE-MOM")
    drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-MOM",)
    summary = r1.backend.current_mom_summary()
    assert set(summary["federate_objects"]) == {h1, h2}

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None
    summary = r1.backend.current_mom_summary()
    assert set(summary["federate_objects"]) == {h1, h2}

    r1.requestFederationRestore("SAVE-MOM")
    drain(r1, r2)
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-MOM",)
    summary = r1.backend.current_mom_summary()
    assert set(summary["federate_objects"]) == {h1, h2}

    r1.federateRestoreComplete()
    r2.federateRestoreComplete()
    drain(r1, r2)
    assert f1.last_callback("federationRestored") is not None
    summary = r1.backend.current_mom_summary()
    assert set(summary["federate_objects"]) == {h1, h2}

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-restore-mom-fed")


def test_save_restore_lifecycle_states_are_visible_in_mom_summary():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("save-restore-state-mom-fed")

    r1.requestFederationSave("SAVE-STATE")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["save_label"] == "SAVE-STATE"
    assert summary["save_status"] == {
        h1: SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE.name,
        h2: SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE.name,
    }
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-STATE",)
    assert f2.last_callback("initiateFederateSave").args == ("SAVE-STATE",)

    r1.federateSaveBegun()
    summary = r1.backend.current_mom_summary()
    assert summary["save_status"][h1] == SaveStatus.FEDERATE_SAVING.name
    assert summary["save_status"][h2] == SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE.name

    r2.federateSaveBegun()
    r1.federateSaveComplete()
    summary = r1.backend.current_mom_summary()
    assert summary["save_status"][h1] == SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE.name
    r2.federateSaveComplete()
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["save_label"] is None
    assert summary["save_status"] == {}
    assert summary["last_save_name"] == "SAVE-STATE"
    assert f1.last_callback("federationSaved") is not None

    r1.requestFederationSave("SAVE-ABORT-MOM")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["save_label"] == "SAVE-ABORT-MOM"
    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.abortFederationSave()
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["save_label"] is None
    assert summary["save_status"] == {}
    assert f1.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)

    r1.requestFederationRestore("MISSING-SAVE")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["restore_label"] is None
    assert summary["restore_status"] == {}
    assert f1.last_callback("requestFederationRestoreFailed").args == ("MISSING-SAVE",)

    r1.requestFederationRestore("SAVE-STATE")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["restore_label"] == "SAVE-STATE"
    assert summary["restore_status"] == {
        h1: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING.name,
        h2: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING.name,
    }
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-STATE",)
    assert f1.last_callback("federationRestoreBegun") is not None
    assert f2.last_callback("initiateFederateRestore").args == ("SAVE-STATE", "bravo", h2)

    r1.federateRestoreComplete()
    summary = r1.backend.current_mom_summary()
    assert summary["restore_status"][h1] == RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE.name
    assert summary["restore_status"][h2] == RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING.name
    r2.abortFederationRestore()
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["restore_label"] is None
    assert summary["restore_status"] == {}
    assert f1.last_callback("federationNotRestored").args == (RestoreFailureReason.RESTORE_ABORTED,)

    r1.requestFederationRestore("SAVE-STATE")
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["restore_status"] == {
        h1: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING.name,
        h2: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING.name,
    }
    r1.federateRestoreComplete()
    r2.federateRestoreNotComplete()
    drain(r1, r2)
    summary = r1.backend.current_mom_summary()
    assert summary["restore_label"] is None
    assert summary["restore_status"] == {}
    assert f1.last_callback("federationNotRestored").args == (
        RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
    )

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("save-restore-state-mom-fed")


def test_resign_federation_execution_stops_joined_member_callbacks():
    _, leader, wing, leader_fed, wing_fed, _h1, _h2 = joined_pair("resign-callback-fed")

    wing.resignFederationExecution(ResignAction.NO_ACTION)
    pre_records = len(wing_fed.records)

    leader.requestFederationSave("POST-RESIGN-SAVE")
    drain(leader, wing)
    leader.federateSaveBegun()
    leader.federateSaveComplete()
    drain(leader, wing)

    assert leader_fed.last_callback("federationSaved") is not None
    assert len(wing_fed.records) == pre_records
    assert wing_fed.last_callback("initiateFederateSave") is None
    assert wing_fed.last_callback("federationSaved") is None

    leader.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution("resign-callback-fed")


class _JoinFromCallbackAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti

    def reportFederationExecutions(self, infos):
        super().reportFederationExecutions(infos)
        with pytest.raises(CallNotAllowedFromWithinCallback):
            self.rti.joinFederationExecution("late", "type", "callback-join-fed")


class _ResignFromCallbackAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti

    def timeRegulationEnabled(self, time):
        super().timeRegulationEnabled(time)
        with pytest.raises(CallNotAllowedFromWithinCallback):
            self.rti.resignFederationExecution(ResignAction.NO_ACTION)


def test_join_and_resign_reject_calls_from_within_callback():
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    rti.connect(_JoinFromCallbackAmbassador(rti), CallbackModel.HLA_IMMEDIATE)
    rti.createFederationExecution("callback-join-fed", "TargetRadarFOMmodule.xml")
    rti.listFederationExecutions()
    rti.disconnect()

    rti2 = rti_ambassador(engine=engine)
    rti2.connect(_ResignFromCallbackAmbassador(rti2), CallbackModel.HLA_IMMEDIATE)
    rti2.joinFederationExecution("alpha", "type-a", "callback-join-fed")
    factory = rti2.getTimeFactory()
    rti2.enableTimeRegulation(factory.make_interval(1.0))
    rti2.resignFederationExecution(ResignAction.NO_ACTION)
    rti2.destroyFederationExecution("callback-join-fed")
