"""Federation synchronization smoke scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from .scenario_support import drain_callbacks_pair, wait_for_callback


@dataclass(frozen=True)
class SynchronizationScenarioConfig:
    federation_name: str = "JavaProfileSyncFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    federate_type: str = "Participant"
    label: str = "ReadyToRun"
    tag: bytes = b"startup"


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
        "leader_announce": leader_announce,
        "wing_announce": wing_announce,
        "leader_sync": leader_sync,
        "wing_sync": wing_sync,
    }


__all__ = ["SynchronizationScenarioConfig", "run_synchronization_scenario"]
