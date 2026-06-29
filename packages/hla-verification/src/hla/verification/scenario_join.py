"""Shared join-precondition verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516_2025.exceptions import (
    FederateAlreadyExecutionMember as FederateAlreadyExecutionMember2025,
)
from hla.rti1516_2025.exceptions import (
    FederateNameAlreadyInUse as FederateNameAlreadyInUse2025,
)
from hla.rti1516_2025.exceptions import (
    FederationExecutionDoesNotExist as FederationExecutionDoesNotExist2025,
)
from hla.rti1516_2025.exceptions import (
    NotConnected as NotConnected2025,
)
from hla.rti1516_2025.exceptions import (
    RestoreInProgress as RestoreInProgress2025,
)
from hla.rti1516_2025.exceptions import (
    SaveInProgress as SaveInProgress2025,
)
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.exceptions import (
    FederateAlreadyExecutionMember,
    FederateNameAlreadyInUse,
    FederationExecutionDoesNotExist,
    NotConnected,
    RestoreInProgress,
    SaveInProgress,
)

from .scenario_support import drain_callbacks_pair, wait_for_callback


@dataclass(frozen=True)
class JoinScenarioConfig:
    federation_name: str = "JoinFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    late_name: str = "Late"
    federate_type: str = "JoinFederate"
    save_name: str = "JOIN-BLOCK"


def run_join_precondition_scenario(
    leader_rti: Any,
    wing_rti: Any,
    late_rti: Any,
    *,
    config: JoinScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    late_federate: Any,
) -> dict[str, Any]:
    try:
        late_rti.join_federation_execution(config.late_name, config.federate_type, config.federation_name)
    except (NotConnected, NotConnected2025) as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    late_rti.connect(late_federate, CallbackModel.HLA_EVOKED)

    try:
        late_rti.join_federation_execution(config.late_name, config.federate_type, f"{config.federation_name}-missing")
    except (FederationExecutionDoesNotExist, FederationExecutionDoesNotExist2025) as exc:
        missing_federation = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to reject a missing federation")

    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    try:
        late_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    except (FederateNameAlreadyInUse, FederateNameAlreadyInUse2025) as exc:
        duplicate_name = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to reject a duplicate federate name")

    try:
        leader_rti.join_federation_execution("Other", config.federate_type, config.federation_name)
    except (FederateAlreadyExecutionMember, FederateAlreadyExecutionMember2025) as exc:
        already_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to reject an already-joined ambassador")

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    try:
        late_rti.join_federation_execution(config.late_name, config.federate_type, config.federation_name)
    except (SaveInProgress, SaveInProgress2025) as exc:
        save_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to reject a federation save in progress")

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
    wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "requestFederationRestoreSucceeded", loops=120)
    wait_for_callback(leader_rti, leader_federate, "federationRestoreBegun", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateRestore", loops=120)
    try:
        late_rti.join_federation_execution(config.late_name, config.federate_type, config.federation_name)
    except (RestoreInProgress, RestoreInProgress2025) as exc:
        restore_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected join_federation_execution to reject a federation restore in progress")
    finally:
        try:
            leader_rti.abort_federation_restore()
            drain_callbacks_pair(leader_rti, wing_rti, loops=16)
        except Exception:
            pass
        try:
            late_rti.disconnect()
        except Exception:
            pass
        try:
            leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            leader_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            wing_rti.disconnect()
        except Exception:
            pass
        try:
            leader_rti.disconnect()
        except Exception:
            pass

    return {
        "not_connected": not_connected,
        "missing_federation": missing_federation,
        "duplicate_name": duplicate_name,
        "already_joined": already_joined,
        "save_in_progress": save_in_progress,
        "restore_in_progress": restore_in_progress,
    }


__all__ = [
    "JoinScenarioConfig",
    "run_join_precondition_scenario",
]
