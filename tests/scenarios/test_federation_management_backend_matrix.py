from __future__ import annotations

import uuid
from importlib import resources

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import RestoreStatus, SaveStatus, SynchronizationPointFailureReason
from hla.rti1516e.exceptions import (
    FederateAlreadyExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederationExecutionDoesNotExist,
    InvalidResignAction,
    NotConnected,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
    RestoreInProgress,
    RestoreNotInProgress,
    SaveInProgress,
)
from hla.runtime.factory import create_rti_ambassador
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    LostFederateScenarioConfig,
    SaveRestoreScenarioConfig,
    JoinScenarioConfig,
    ResignScenarioConfig,
    SynchronizationScenarioConfig,
    run_abort_save_exception_scenario,
    run_failed_federate_synchronization_scenario,
    run_late_join_synchronization_scenario,
    run_lost_federate_mom_scenario,
    run_multiple_synchronization_points_scenario,
    run_connection_lost_callback_scenario,
    run_disconnect_mom_cleanup_scenario,
    run_join_precondition_scenario,
    run_resign_mom_cleanup_scenario,
    run_resign_precondition_scenario,
    run_resigned_federate_callback_silence_scenario,
    run_restore_abort_scenario,
    run_restore_participant_exception_scenario,
    run_restore_request_precondition_scenario,
    run_restore_failure_scenario,
    run_restore_request_failure_scenario,
    run_save_abort_scenario,
    run_save_failure_scenario,
    run_save_participant_exception_scenario,
    run_save_restore_queued_callback_scenario,
    run_save_request_precondition_scenario,
    run_save_status_exception_scenario,
    run_restore_abort_exception_scenario,
    run_restore_status_exception_scenario,
    run_restore_federate_local_state_scenario,
    run_restore_object_state_scenario,
    run_scheduled_save_restore_time_state_scenario,
    run_save_restore_scenario,
    run_synchronization_registration_failure_scenario,
    run_synchronization_scenario,
)

_VENDOR_SMOKE_FOM = str(resources.files("hla.fom").joinpath("resources", "foms", "VendorSmokeFOM.xml"))


def test_python_backend_synchronization_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SynchronizationScenarioConfig(
        federation_name=f"python-sync-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"startup",
    )

    summary = run_synchronization_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_registration"].args == ("ReadyToRun",)
    assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
    assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
    assert summary["leader_sync"].args[0] == "ReadyToRun"
    assert summary["wing_sync"].args[0] == "ReadyToRun"


def test_python_connection_lost_callback_matrix():
    federate = RecordingFederateAmbassador()
    summary = run_connection_lost_callback_scenario(
        federate.connectionLost,
        federate=federate,
        fault_description="python callback bridge loss",
    )
    assert summary["record"].args == ("python callback bridge loss",)


def test_python_backend_lost_federate_mom_matrix():
    engine = InMemoryRTIEngine()
    observer = create_rti_ambassador("python", engine=engine)
    victim = create_rti_ambassador("python", engine=engine)
    config = LostFederateScenarioConfig(
        federation_name=f"python-lost-federate-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        observer_name="Observer",
        victim_name="Victim",
        federate_type="LostFederateProbe",
        object_instance_name=f"python-lost-{uuid.uuid4().hex[:8]}",
        fault_description="python in-memory induced loss",
    )

    summary = run_lost_federate_mom_scenario(
        observer,
        victim,
        config=config,
        observer_federate=RecordingFederateAmbassador(),
        victim_federate=RecordingFederateAmbassador(),
        induce_loss=observer.backend.force_federate_loss,
    )

    assert summary["loss_record"].args[1]
    assert summary["removal"].args[0] == summary["object_instance"]


def test_python_backend_synchronization_registration_failure_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SynchronizationScenarioConfig(
        federation_name=f"python-sync-failure-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"startup",
    )

    summary = run_synchronization_registration_failure_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["registration_success"].args == ("ReadyToRun",)
    assert summary["registration_failure"].args == (
        "ReadyToRun",
        SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
    )


def test_python_backend_failed_federate_synchronization_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SynchronizationScenarioConfig(
        federation_name=f"python-sync-failed-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="PreRun",
        tag=b"startup",
    )

    summary = run_failed_federate_synchronization_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        leader_success=True,
        wing_success=False,
    )

    assert summary["leader_sync"].args[0] == "PreRun"
    assert summary["wing_handle"] in summary["leader_sync"].args[1]
    assert summary["leader_handle"] not in summary["leader_sync"].args[1]


def test_python_backend_late_join_synchronization_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    late = create_rti_ambassador("python", engine=engine)
    config = SynchronizationScenarioConfig(
        federation_name=f"python-sync-late-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        late_name="Late",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"startup",
    )

    summary = run_late_join_synchronization_scenario(
        leader,
        wing,
        late,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        late_federate=RecordingFederateAmbassador(),
    )

    assert summary["late_announce"].args[:2] == ("ReadyToRun", b"startup")
    assert summary["leader_sync"].args[0] == "ReadyToRun"
    assert summary["wing_sync"].args[0] == "ReadyToRun"
    assert summary["late_sync"].args[0] == "ReadyToRun"


def test_python_backend_multiple_synchronization_points_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SynchronizationScenarioConfig(
        federation_name=f"python-sync-multi-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"startup",
        second_label="PreRun",
        second_tag=b"prerun",
    )

    summary = run_multiple_synchronization_points_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert {record.args[0] for record in summary["leader_announces"]} == {"ReadyToRun", "PreRun"}
    assert {record.args[0] for record in summary["wing_announces"]} == {"ReadyToRun", "PreRun"}
    assert summary["first_sync_leader"].args[0] == "ReadyToRun"
    assert summary["first_sync_wing"].args[0] == "ReadyToRun"
    assert summary["second_sync_leader"].args[0] == "PreRun"
    assert summary["second_sync_wing"].args[0] == "PreRun"


def test_python_backend_save_restore_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-save-restore-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-{uuid.uuid4().hex[:8]}",
    )

    summary = run_save_restore_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_initiate_save"].args[0] == config.save_name
    assert summary["wing_initiate_save"].args == (config.save_name,)
    assert all(
        pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS
        for pair in summary["save_status_cleared"].args[0]
    )
    assert summary["leader_restore_succeeded"].args == (config.save_name,)
    assert summary["wing_initiate_restore"].args[0] == config.save_name
    assert all(
        pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS
        for pair in summary["restore_status_cleared"].args[0]
    )


def test_python_backend_save_restore_queued_callback_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-save-restore-queued-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-QUEUED-{uuid.uuid4().hex[:8]}",
    )

    summary = run_save_restore_queued_callback_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_initiate_save"].args[0] == config.save_name
    assert summary["wing_initiate_save"].args == (config.save_name,)
    assert summary["leader_saved"] is not None
    assert summary["wing_saved"] is not None
    assert summary["leader_restore_succeeded"].args == (config.save_name,)
    assert summary["wing_initiate_restore"].args[0] == config.save_name
    assert summary["leader_restored"] is not None
    assert summary["wing_restored"] is not None


def test_python_backend_scheduled_save_restore_time_state_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-scheduled-save-restore-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-AT-{uuid.uuid4().hex[:8]}",
    )

    summary = run_scheduled_save_restore_time_state_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        save_time=5.0,
        post_save_time=8.0,
    )

    assert summary["leader_initiate_save"].args[0] == config.save_name
    assert summary["leader_logical_time"].value == 8.0
    assert summary["restored_leader_time"].value == 5.0
    assert summary["restored_wing_time"].value == 5.0


def test_python_backend_restore_object_state_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-restore-object-state-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-OBJECT-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_object_state_scenario(
        leader,
        wing,
        config=config,
        leader_federate=leader_fed,
        wing_federate=wing_fed,
    )

    assert summary["leader_restore_succeeded"].args == (config.save_name,)
    assert summary["wing_initiate_restore"].args[0] == config.save_name
    assert summary["informed_federate_name"] == config.wing_name


def test_python_backend_restore_federate_local_state_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-restore-local-state-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-LOCAL-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_federate_local_state_scenario(
        leader,
        wing,
        config=config,
        leader_federate=leader_fed,
        wing_federate=wing_fed,
    )

    assert summary["leader_restored"] is not None
    assert summary["wing_restored"] is not None


def test_python_backend_save_failure_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-save-failure-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-FAIL-{uuid.uuid4().hex[:8]}",
    )

    summary = run_save_failure_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"
    assert summary["wing_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"
    assert all(
        pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS
        for pair in summary["save_status_cleared"].args[0]
    )


def test_python_backend_restore_request_failure_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-restore-request-failure-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_request_failure_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        missing_save_name=f"MISSING-{uuid.uuid4().hex[:8]}",
    )

    assert summary["restore_failed"].args[0].startswith("MISSING-")
    assert all(
        pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS
        for pair in summary["restore_status_cleared"].args[0]
    )


def test_python_backend_restore_failure_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-restore-failure-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-RESTORE-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_failure_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"
    assert summary["wing_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"
    assert all(
        pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS
        for pair in summary["restore_status_cleared"].args[0]
    )


def test_python_backend_save_abort_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-save-abort-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-ABORT-{uuid.uuid4().hex[:8]}",
    )

    summary = run_save_abort_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_not_saved"].args[0].name == "SAVE_ABORTED"
    assert summary["wing_not_saved"].args[0].name == "SAVE_ABORTED"
    assert all(
        pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS
        for pair in summary["save_status_cleared"].args[0]
    )


def test_python_backend_restore_abort_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-restore-abort-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"RESTORE-ABORT-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_abort_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_not_restored"].args[0].name == "RESTORE_ABORTED"
    assert summary["wing_not_restored"].args[0].name == "RESTORE_ABORTED"
    assert all(
        pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS
        for pair in summary["restore_status_cleared"].args[0]
    )


def test_python_backend_restore_abort_exception_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-save-status-negative-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"SAVE-STATUS-{uuid.uuid4().hex[:8]}",
    )

    summary = run_restore_abort_exception_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["restore_not_in_progress"], RestoreNotInProgress)


def test_python_backend_save_status_exception_matrix():
    rti = create_rti_ambassador("python")

    summary = run_save_status_exception_scenario(
        rti,
        federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)


def test_python_backend_restore_status_exception_matrix():
    rti = create_rti_ambassador("python")

    summary = run_restore_status_exception_scenario(
        rti,
        federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)


def test_python_backend_save_request_precondition_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)

    summary = run_save_request_precondition_scenario(
        leader,
        wing,
        config=SaveRestoreScenarioConfig(
            federation_name=f"python-save-request-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-REQ-{uuid.uuid4().hex[:8]}",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["save_in_progress"], SaveInProgress)
    assert isinstance(summary["restore_in_progress"], RestoreInProgress)


def test_python_backend_restore_request_precondition_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)

    summary = run_restore_request_precondition_scenario(
        leader,
        wing,
        config=SaveRestoreScenarioConfig(
            federation_name=f"python-restore-request-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"RESTORE-REQ-{uuid.uuid4().hex[:8]}",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["save_in_progress"], SaveInProgress)
    assert isinstance(summary["restore_in_progress"], RestoreInProgress)


def test_python_backend_save_participant_exception_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)

    summary = run_save_participant_exception_scenario(
        leader,
        wing,
        config=SaveRestoreScenarioConfig(
            federation_name=f"python-save-participant-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-PART-{uuid.uuid4().hex[:8]}",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["begun_not_connected"], NotConnected)
    assert isinstance(summary["complete_not_connected"], NotConnected)
    assert isinstance(summary["not_complete_not_connected"], NotConnected)
    assert isinstance(summary["begun_not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["complete_not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["not_complete_not_joined"], FederateNotExecutionMember)


def test_python_backend_abort_save_exception_matrix():
    rti = create_rti_ambassador("python")

    summary = run_abort_save_exception_scenario(
        rti,
        federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)


def test_python_backend_restore_participant_exception_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)

    summary = run_restore_participant_exception_scenario(
        leader,
        wing,
        config=SaveRestoreScenarioConfig(
            federation_name=f"python-restore-participant-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"RESTORE-PART-{uuid.uuid4().hex[:8]}",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["complete_not_connected"], NotConnected)
    assert isinstance(summary["not_complete_not_connected"], NotConnected)
    assert isinstance(summary["complete_not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["not_complete_not_joined"], FederateNotExecutionMember)


def test_python_backend_resigned_federate_callback_silence_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = SaveRestoreScenarioConfig(
        federation_name=f"python-resign-callback-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"POST-RESIGN-SAVE-{uuid.uuid4().hex[:8]}",
    )

    summary = run_resigned_federate_callback_silence_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_initiate_save"].args == (config.save_name,)
    assert summary["leader_saved"] is not None
    assert summary["wing_record_count_after"] == summary["wing_record_count_before"]
    assert summary["wing_post_resign_records"] == []


def test_python_backend_resign_precondition_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = ResignScenarioConfig(
        federation_name=f"python-resign-negative-{uuid.uuid4().hex[:8]}",
        fom_modules=(_VENDOR_SMOKE_FOM,),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="ResignFederate",
        object_instance_name=f"Pending-Acquisition-{uuid.uuid4().hex[:8]}",
    )

    summary = run_resign_precondition_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["not_joined"], FederateNotExecutionMember)
    assert isinstance(summary["invalid_action"], InvalidResignAction)
    assert isinstance(summary["owns_attributes"], FederateOwnsAttributes)
    assert isinstance(summary["acquisition_pending"], OwnershipAcquisitionPending)


def test_python_backend_resign_mom_cleanup_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = ResignScenarioConfig(
        federation_name=f"python-resign-mom-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="ResignFederate",
    )

    summary = run_resign_mom_cleanup_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["wing_before"].args[1]
    assert summary["federation_after"].args[1]
    assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


def test_python_backend_disconnect_mom_cleanup_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    config = ResignScenarioConfig(
        federation_name=f"python-disconnect-mom-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="ResignFederate",
    )

    summary = run_disconnect_mom_cleanup_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert summary["leader_before"].args[1]
    assert summary["federation_after"].args[1]
    assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


def test_python_backend_join_precondition_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python", engine=engine)
    wing = create_rti_ambassador("python", engine=engine)
    late = create_rti_ambassador("python", engine=engine)
    config = JoinScenarioConfig(
        federation_name=f"python-join-negative-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        late_name="Late",
        federate_type="JoinFederate",
        save_name=f"JOIN-BLOCK-{uuid.uuid4().hex[:8]}",
    )

    summary = run_join_precondition_scenario(
        leader,
        wing,
        late,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        late_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["not_connected"], NotConnected)
    assert isinstance(summary["missing_federation"], FederationExecutionDoesNotExist)
    assert isinstance(summary["duplicate_name"], FederateNameAlreadyInUse)
    assert isinstance(summary["already_joined"], FederateAlreadyExecutionMember)
    assert isinstance(summary["save_in_progress"], SaveInProgress)
    assert isinstance(summary["restore_in_progress"], RestoreInProgress)
