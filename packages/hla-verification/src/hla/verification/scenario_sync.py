"""Federation synchronization smoke scenarios."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel, SynchronizationPointFailureReason

from .scenario_support import drain_callbacks_pair, wait_for_callback, wait_for_callback_count


@dataclass(frozen=True)
class SynchronizationScenarioConfig:
    federation_name: str = "JavaProfileSyncFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    late_name: str = "Late"
    federate_type: str = "Participant"
    label: str = "ReadyToRun"
    tag: bytes = b"startup"
    second_label: str = "PreRun"
    second_tag: bytes = b"prerun"


def run_synchronization_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(config.federation_name, list(config.fom_modules), config.logical_time_implementation_name)
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)
    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)
    leader_registration = wait_for_callback(
        leader_rti,
        leader_federate,
        "synchronizationPointRegistrationSucceeded",
        loops=120,
    )
    assert leader_registration is not None
    assert leader_registration.args == (config.label,)

    leader_announce = wait_for_callback(leader_rti, leader_federate, "announceSynchronizationPoint", loops=120)
    wing_announce = wait_for_callback(wing_rti, wing_federate, "announceSynchronizationPoint", loops=120)
    assert leader_announce is not None
    assert wing_announce is not None
    assert leader_announce.args[:2] == (config.label, config.tag)
    assert wing_announce.args[:2] == (config.label, config.tag)

    leader_rti.synchronization_point_achieved(config.label)
    wing_rti.synchronization_point_achieved(config.label)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)
    leader_sync = wait_for_callback(leader_rti, leader_federate, "federationSynchronized", loops=120)
    wing_sync = wait_for_callback(wing_rti, wing_federate, "federationSynchronized", loops=120)
    assert leader_sync is not None
    assert wing_sync is not None
    assert leader_sync.args[0] == config.label
    assert wing_sync.args[0] == config.label

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_registration": leader_registration,
        "leader_announce": leader_announce,
        "wing_announce": wing_announce,
        "leader_sync": leader_sync,
        "wing_sync": wing_sync,
    }


def run_synchronization_registration_failure_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)
    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    registration_success = wait_for_callback(
        leader_rti,
        leader_federate,
        "synchronizationPointRegistrationSucceeded",
        loops=120,
    )
    assert registration_success is not None
    assert registration_success.args == (config.label,)

    failure_count = len(leader_federate.callbacks_named("synchronizationPointRegistrationFailed")) + 1
    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)
    failure_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "synchronizationPointRegistrationFailed",
        failure_count,
        loops=120,
    )
    registration_failure = failure_records[-1]
    assert registration_failure.args == (
        config.label,
        SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
    )

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "registration_success": registration_success,
        "registration_failure": registration_failure,
    }


def run_failed_federate_synchronization_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    leader_success: bool = True,
    wing_success: bool = False,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    leader_registration = wait_for_callback(
        leader_rti,
        leader_federate,
        "synchronizationPointRegistrationSucceeded",
        loops=120,
    )
    leader_announce = wait_for_callback(leader_rti, leader_federate, "announceSynchronizationPoint", loops=120)
    wing_announce = wait_for_callback(wing_rti, wing_federate, "announceSynchronizationPoint", loops=120)
    assert leader_registration is not None
    assert leader_announce is not None
    assert wing_announce is not None

    leader_rti.synchronization_point_achieved(config.label, leader_success)
    wing_rti.synchronization_point_achieved(config.label, wing_success)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    leader_sync = wait_for_callback(leader_rti, leader_federate, "federationSynchronized", loops=120)
    wing_sync = wait_for_callback(wing_rti, wing_federate, "federationSynchronized", loops=120)
    assert leader_sync is not None
    assert wing_sync is not None
    assert leader_sync.args[0] == config.label
    assert wing_sync.args[0] == config.label

    leader_failed = leader_sync.args[1]
    wing_failed = wing_sync.args[1]
    assert leader_failed == wing_failed

    if leader_success:
        assert leader_handle not in leader_failed
    else:
        assert leader_handle in leader_failed
    if wing_success:
        assert wing_handle not in leader_failed
    else:
        assert wing_handle in leader_failed

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_registration": leader_registration,
        "leader_announce": leader_announce,
        "wing_announce": wing_announce,
        "leader_sync": leader_sync,
        "wing_sync": wing_sync,
    }


def run_late_join_synchronization_scenario(
    leader_rti: Any,
    wing_rti: Any,
    late_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    late_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    late_rti.connect(late_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)
    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    leader_announce = wait_for_callback(leader_rti, leader_federate, "announceSynchronizationPoint", loops=120)
    wing_announce = wait_for_callback(wing_rti, wing_federate, "announceSynchronizationPoint", loops=120)
    assert leader_announce is not None
    assert wing_announce is not None
    assert leader_announce.args[:2] == (config.label, config.tag)
    assert wing_announce.args[:2] == (config.label, config.tag)

    late_handle = late_rti.join_federation_execution(config.late_name, config.federate_type, config.federation_name)
    drain_callbacks_pair(leader_rti, wing_rti, late_rti, loops=12)
    late_announce = wait_for_callback(late_rti, late_federate, "announceSynchronizationPoint", loops=120)
    assert late_announce is not None
    assert late_announce.args[:2] == (config.label, config.tag)

    leader_rti.synchronization_point_achieved(config.label)
    wing_rti.synchronization_point_achieved(config.label)
    drain_callbacks_pair(leader_rti, wing_rti, late_rti, loops=12)
    assert leader_federate.last_callback("federationSynchronized") is None
    assert wing_federate.last_callback("federationSynchronized") is None
    assert late_federate.last_callback("federationSynchronized") is None

    late_rti.synchronization_point_achieved(config.label)
    drain_callbacks_pair(leader_rti, wing_rti, late_rti, loops=12)
    leader_sync = wait_for_callback(leader_rti, leader_federate, "federationSynchronized", loops=120)
    wing_sync = wait_for_callback(wing_rti, wing_federate, "federationSynchronized", loops=120)
    late_sync = wait_for_callback(late_rti, late_federate, "federationSynchronized", loops=120)
    assert leader_sync is not None
    assert wing_sync is not None
    assert late_sync is not None
    assert leader_sync.args[0] == config.label
    assert wing_sync.args[0] == config.label
    assert late_sync.args[0] == config.label

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "late_handle": late_handle,
        "leader_announce": leader_announce,
        "wing_announce": wing_announce,
        "late_announce": late_announce,
        "leader_sync": leader_sync,
        "wing_sync": wing_sync,
        "late_sync": late_sync,
    }


def run_multiple_synchronization_points_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    leader_rti.register_federation_synchronization_point(config.second_label, config.second_tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)

    first_leader_announce = wait_for_callback(leader_rti, leader_federate, "announceSynchronizationPoint", loops=120)
    first_wing_announce = wait_for_callback(wing_rti, wing_federate, "announceSynchronizationPoint", loops=120)
    first_leader_records = wait_for_callback_count(leader_rti, leader_federate, "announceSynchronizationPoint", 2, loops=120)
    first_wing_records = wait_for_callback_count(wing_rti, wing_federate, "announceSynchronizationPoint", 2, loops=120)
    assert first_leader_announce is not None
    assert first_wing_announce is not None

    announced_labels_leader = {record.args[0] for record in first_leader_records}
    announced_labels_wing = {record.args[0] for record in first_wing_records}
    assert announced_labels_leader == {config.label, config.second_label}
    assert announced_labels_wing == {config.label, config.second_label}

    leader_rti.synchronization_point_achieved(config.label)
    wing_rti.synchronization_point_achieved(config.label)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    first_sync_leader = wait_for_callback(leader_rti, leader_federate, "federationSynchronized", loops=120)
    first_sync_wing = wait_for_callback(wing_rti, wing_federate, "federationSynchronized", loops=120)
    assert first_sync_leader is not None
    assert first_sync_wing is not None
    assert first_sync_leader.args[0] == config.label
    assert first_sync_wing.args[0] == config.label

    leader_sync_records = leader_federate.callbacks_named("federationSynchronized")
    wing_sync_records = wing_federate.callbacks_named("federationSynchronized")
    assert len(leader_sync_records) == 1
    assert len(wing_sync_records) == 1

    leader_rti.synchronization_point_achieved(config.second_label)
    wing_rti.synchronization_point_achieved(config.second_label)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    second_sync_leader_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationSynchronized",
        2,
        loops=120,
    )
    second_sync_wing_records = wait_for_callback_count(
        wing_rti,
        wing_federate,
        "federationSynchronized",
        2,
        loops=120,
    )
    second_sync_leader = second_sync_leader_records[-1]
    second_sync_wing = second_sync_wing_records[-1]
    assert second_sync_leader.args[0] == config.second_label
    assert second_sync_wing.args[0] == config.second_label

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_announces": tuple(first_leader_records),
        "wing_announces": tuple(first_wing_records),
        "first_sync_leader": first_sync_leader,
        "first_sync_wing": first_sync_wing,
        "second_sync_leader": second_sync_leader,
        "second_sync_wing": second_sync_wing,
    }


__all__ = [
    "run_failed_federate_synchronization_scenario",
    "run_multiple_synchronization_points_scenario",
    "run_late_join_synchronization_scenario",
    "SynchronizationScenarioConfig",
    "run_synchronization_registration_failure_scenario",
    "run_synchronization_scenario",
]
