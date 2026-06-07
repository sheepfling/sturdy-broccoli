# ruff: noqa: F401,F403

from tests.backends.python_backend_extended_support import *

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


def test_list_federation_executions_requires_connection_and_reports_known_federations():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.list_federation_executions()

    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("listed-fed", "TargetRadarFOMmodule.xml")
    rti.list_federation_executions()
    drain(rti)

    callback = fed.last_callback("reportFederationExecutions")
    assert callback is not None
    infos = callback.args[0]
    assert any(info.federation_execution_name == "listed-fed" for info in infos)

    rti.destroy_federation_execution("listed-fed")
    rti.disconnect()


def test_register_federation_synchronization_point_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.register_federation_synchronization_point("READY", b"sync")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.register_federation_synchronization_point("READY", b"sync")
    rti.disconnect()


def test_register_federation_synchronization_point_reports_duplicate_and_invalid_target_failures():
    _, r1, r2, f1, _f2, _h1, h2 = joined_pair("sync-negative-fed")

    r1.register_federation_synchronization_point("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationSucceeded").args == ("READY",)

    r1.register_federation_synchronization_point("READY", b"sync")
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationFailed").args == (
        "READY",
        SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
    )

    invalid_handle = type(h2)(h2.value + 1000)
    r1.register_federation_synchronization_point("BAD-TARGET", b"sync", {invalid_handle})
    drain(r1, r2)
    assert f1.last_callback("synchronizationPointRegistrationFailed").args == (
        "BAD-TARGET",
        SynchronizationPointFailureReason.SYNCHRONIZATION_SET_MEMBER_NOT_JOINED,
    )

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("sync-negative-fed")


def test_register_federation_synchronization_point_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("sync-blocked-fed")

    r1.request_federation_save("SYNC-SAVE")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.register_federation_synchronization_point("BLOCKED", b"sync")

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore("SYNC-SAVE")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.register_federation_synchronization_point("BLOCKED-RESTORE", b"sync")

    r1.abort_federation_restore()
    drain(r1, r2)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("sync-blocked-fed")


def test_synchronization_point_achieved_rejects_not_connected_not_joined_and_unknown_label():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.synchronization_point_achieved("READY")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.synchronization_point_achieved("READY")
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, h2 = joined_pair("sync-achieve-negative-fed")
    with pytest.raises(SynchronizationPointLabelNotAnnounced):
        r1.synchronization_point_achieved("UNKNOWN")

    r1.register_federation_synchronization_point("KNOWN", b"sync", {h2})
    drain(r1, r2)
    with pytest.raises(SynchronizationPointLabelNotAnnounced):
        r1.synchronization_point_achieved("KNOWN")

    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("sync-achieve-negative-fed")


def test_synchronization_point_achieved_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("sync-achieve-blocked-fed")
    r1.register_federation_synchronization_point("READY", b"sync")
    drain(r1, r2)

    r1.request_federation_save("SYNC-ACHIEVE")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.synchronization_point_achieved("READY")

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore("SYNC-ACHIEVE")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.synchronization_point_achieved("READY")

    r1.abort_federation_restore()
    drain(r1, r2)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("sync-achieve-blocked-fed")


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


def test_save_failure_reports_federation_not_saved_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("save-failure-fed")

    r1.request_federation_save("SAVE-FAIL")
    drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args == ("SAVE-FAIL",)
    assert f2.last_callback("initiateFederateSave").args == ("SAVE-FAIL",)

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_not_complete()
    drain(r1, r2)

    assert f1.last_callback("federationNotSaved").args == (
        SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
    )
    assert f2.last_callback("federationNotSaved").args == (
        SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
    )

    r1.query_federation_save_status()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("save-failure-fed")


def test_abort_federation_save_reports_aborted_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("abort-save-fed")

    r1.request_federation_save("SAVE-ABORT")
    drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()

    r1.abort_federation_save()
    drain(r1, r2)

    assert f1.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)
    assert f2.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)

    r1.query_federation_save_status()
    drain(r1)
    status_response = f1.last_callback("federationSaveStatusResponse").args[0]
    assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("abort-save-fed")


def test_abort_federation_save_requires_save_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("abort-save-invalid-fed")

    with pytest.raises(SaveNotInProgress):
        r1.abort_federation_save()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("abort-save-invalid-fed")


def test_federate_save_begun_rejects_not_connected_not_joined_and_missing_save():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federate_save_begun()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federate_save_begun()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-begun-negative-fed")
    with pytest.raises(SaveNotInitiated):
        r1.federate_save_begun()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("save-begun-negative-fed")


def test_federate_save_complete_and_not_complete_reject_missing_save():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federate_save_complete()
    with pytest.raises(NotConnected):
        rti.federate_save_not_complete()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federate_save_complete()
    with pytest.raises(FederateNotExecutionMember):
        rti.federate_save_not_complete()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-complete-negative-fed")
    with pytest.raises(SaveNotInitiated):
        r1.federate_save_complete()
    with pytest.raises(SaveNotInitiated):
        r1.federate_save_not_complete()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("save-complete-negative-fed")


def test_request_federation_save_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.request_federation_save("SAVE")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_federation_save("SAVE")
    rti.disconnect()


def test_request_federation_save_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-negative-fed")

    r1.request_federation_save("SAVE-NEG")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.request_federation_save("SAVE-NEG-2")

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore("SAVE-NEG")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.request_federation_save("SAVE-DURING-RESTORE")

    r1.abort_federation_restore()
    drain(r1, r2)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("save-negative-fed")


def test_request_federation_save_rejects_past_and_invalid_time():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("save-time-negative-fed")
    factory = r1.get_time_factory()
    r1.enable_time_regulation(factory.make_interval(1.0))
    drain(r1, r2)
    r1.time_advance_request(factory.make_time(5.0))
    drain(r1, r2)

    with pytest.raises(LogicalTimeAlreadyPassed):
        r1.request_federation_save("PAST-SAVE", factory.make_time(4.0))

    with pytest.raises(InvalidLogicalTime):
        r1.request_federation_save("BAD-SAVE", object())

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("save-time-negative-fed")


def test_query_federation_save_status_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.query_federation_save_status()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.query_federation_save_status()
    rti.disconnect()


def test_restore_status_response_and_failure_callback_paths():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("restore-failure-fed")

    r1.request_federation_save("SAVE-RESTORE-FAIL")
    drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.request_federation_restore("SAVE-RESTORE-FAIL")
    drain(r1, r2)
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-RESTORE-FAIL",)
    assert f2.last_callback("initiateFederateRestore").args == ("SAVE-RESTORE-FAIL", "bravo", h2)

    r1.query_federation_restore_status()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    by_handle = {pair.pre_restore_handle: pair.restore_status for pair in status_response}
    assert by_handle[h1] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    assert by_handle[h2] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING

    r1.federate_restore_complete()
    r2.federate_restore_not_complete()
    drain(r1, r2)

    assert f1.last_callback("federationNotRestored").args == (
        RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
    )
    assert f2.last_callback("federationNotRestored").args == (
        RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
    )

    r1.query_federation_restore_status()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("restore-failure-fed")


def test_abort_federation_restore_reports_aborted_and_clears_status():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("abort-restore-fed")

    r1.request_federation_save("SAVE-ABORT-RESTORE")
    drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.request_federation_restore("SAVE-ABORT-RESTORE")
    drain(r1, r2)
    assert f1.last_callback("requestFederationRestoreSucceeded").args == ("SAVE-ABORT-RESTORE",)

    r1.abort_federation_restore()
    drain(r1, r2)

    assert f1.last_callback("federationNotRestored").args == (RestoreFailureReason.RESTORE_ABORTED,)
    assert f2.last_callback("federationNotRestored").args == (RestoreFailureReason.RESTORE_ABORTED,)

    r1.query_federation_restore_status()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("abort-restore-fed")


def test_abort_federation_restore_requires_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("abort-restore-invalid-fed")

    with pytest.raises(RestoreNotInProgress):
        r1.abort_federation_restore()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("abort-restore-invalid-fed")


def test_request_federation_restore_rejects_not_connected_not_joined_and_save_restore_in_progress():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.request_federation_restore("SAVE")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_federation_restore("SAVE")
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("restore-negative-fed")
    r1.request_federation_save("SAVE-RESTORE-BLOCK")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r2.request_federation_restore("SAVE-RESTORE-BLOCK")

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore("SAVE-RESTORE-BLOCK")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r2.request_federation_restore("SAVE-RESTORE-BLOCK")

    r1.abort_federation_restore()
    drain(r1, r2)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("restore-negative-fed")


def test_federate_restore_complete_and_not_complete_reject_missing_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.federate_restore_complete()
    with pytest.raises(NotConnected):
        rti.federate_restore_not_complete()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.federate_restore_complete()
    with pytest.raises(FederateNotExecutionMember):
        rti.federate_restore_not_complete()
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("restore-complete-negative-fed")
    with pytest.raises(RestoreNotRequested):
        r1.federate_restore_complete()
    with pytest.raises(RestoreNotRequested):
        r1.federate_restore_not_complete()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("restore-complete-negative-fed")


def test_request_federation_restore_failed_is_reported_for_unknown_save_label():
    _, r1, r2, f1, f2, _h1, _h2 = joined_pair("restore-request-failed-fed")

    r1.request_federation_restore("MISSING-SAVE")
    drain(r1, r2)

    assert f1.last_callback("requestFederationRestoreFailed").args == ("MISSING-SAVE",)
    assert f2.last_callback("requestFederationRestoreFailed") is None
    assert f1.last_callback("requestFederationRestoreSucceeded") is None
    assert f1.last_callback("federationRestoreStatusResponse") is None

    r1.query_federation_restore_status()
    drain(r1)
    status_response = f1.last_callback("federationRestoreStatusResponse").args[0]
    assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in status_response)

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("restore-request-failed-fed")


def test_query_federation_restore_status_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.query_federation_restore_status()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.query_federation_restore_status()
    rti.disconnect()


def test_disconnect_requires_resign_and_marks_backend_not_connected():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("disconnect-fed")

    with pytest.raises(FederateIsExecutionMember):
        r1.disconnect()

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r1.disconnect()

    with pytest.raises(NotConnected):
        r1.list_federation_executions()

    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r2.destroy_federation_execution("disconnect-fed")
    r2.disconnect()


def test_join_federation_execution_requires_connection():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.join_federation_execution("alpha", "type-a", "missing-fed")


def test_join_federation_execution_rejects_missing_federation():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.join_federation_execution("alpha", "type-a", "missing-fed")
    rti.disconnect()


def test_join_federation_execution_rejects_duplicate_federate_name():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-duplicate-name-fed")
    r3 = rti_ambassador(engine=r1.backend.engine)
    r3.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(FederateNameAlreadyInUse):
        r3.join_federation_execution("alpha", "type-c", "join-duplicate-name-fed")

    r3.disconnect()
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("join-duplicate-name-fed")


def test_join_federation_execution_rejects_already_joined_federate():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-already-member-fed")

    with pytest.raises(FederateAlreadyExecutionMember):
        r1.join_federation_execution("other", "type-a", "join-already-member-fed")

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("join-already-member-fed")


def test_join_federation_execution_rejects_save_and_restore_in_progress():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("join-save-restore-fed")
    r3 = rti_ambassador(engine=r1.backend.engine)
    r3.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    r1.request_federation_save("JOIN-BLOCK")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        r3.join_federation_execution("late-save", "type-c", "join-save-restore-fed")

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore("JOIN-BLOCK")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        r3.join_federation_execution("late-restore", "type-c", "join-save-restore-fed")

    r3.disconnect()
    r1.abort_federation_restore()
    drain(r1, r2)
    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("join-save-restore-fed")


def test_connect_rejects_second_connection_attempt():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(AlreadyConnected):
        rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.disconnect()


def test_create_federation_execution_rejects_duplicate_name():
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("duplicate-fed", "TargetRadarFOMmodule.xml")

    with pytest.raises(FederationExecutionAlreadyExists):
        rti.create_federation_execution("duplicate-fed", "TargetRadarFOMmodule.xml")

    rti.destroy_federation_execution("duplicate-fed")
    rti.disconnect()


def test_create_federation_execution_with_explicit_mim_uses_requested_module():
    engine = InMemoryRTIEngine()
    rti = rti_ambassador(engine=engine)
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    rti.create_federation_execution_with_mim(
        "explicit-mim-fed",
        "TargetRadarFOMmodule.xml",
        "hla2010/resources/foms/HLAstandardMIM.xml",
    )

    federation = engine.federations["explicit-mim-fed"]
    assert federation.mim_module is not None
    assert federation.mim_module.is_mim is True
    assert federation.mim_module.path is not None
    assert federation.mim_module.path.name == "HLAstandardMIM.xml"

    rti.destroy_federation_execution("explicit-mim-fed")
    rti.disconnect()


def test_create_federation_execution_with_standard_mim_designator_is_rejected():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(DesignatorIsHLAstandardMIM):
        rti.create_federation_execution_with_mim(
            "invalid-mim-fed",
            "TargetRadarFOMmodule.xml",
            "HLAstandardMIM",
        )
    rti.disconnect()


def test_destroy_federation_execution_requires_no_joined_federates():
    engine, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("destroy-fed")

    with pytest.raises(FederatesCurrentlyJoined):
        r1.destroy_federation_execution("destroy-fed")

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("destroy-fed")
    assert "destroy-fed" not in engine.federations


def test_destroy_federation_execution_rejects_missing_federation():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.destroy_federation_execution("missing-fed")
    rti.disconnect()


def test_resign_federation_execution_rejects_not_connected_and_not_joined():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.resign_federation_execution(ResignAction.NO_ACTION)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.disconnect()


def test_resign_federation_execution_rejects_invalid_action_and_owned_attributes():
    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("resign-negative-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    owner.register_object_instance(cls, "Owned-Target")

    with pytest.raises(InvalidResignAction):
        owner.resign_federation_execution("bogus")

    with pytest.raises(FederateOwnsAttributes):
        owner.resign_federation_execution(ResignAction.NO_ACTION)

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    observer.destroy_federation_execution("resign-negative-fed")


def test_resign_federation_execution_rejects_pending_acquisition():
    _, owner, acquirer, _owner_fed, _acquirer_fed, _h1, _h2 = joined_pair("resign-pending-acquisition-fed")
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})

    pending = owner.register_object_instance(cls, "Pending-Acquisition")
    acquirer.attribute_ownership_acquisition(pending, {attr}, b"req")
    drain(owner, acquirer)

    with pytest.raises(OwnershipAcquisitionPending):
        acquirer.resign_federation_execution(ResignAction.NO_ACTION)

    owner.attribute_ownership_release_denied(pending, {attr})
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("resign-pending-acquisition-fed")


