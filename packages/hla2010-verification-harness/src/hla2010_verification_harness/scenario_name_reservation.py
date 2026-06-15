"""Object-instance name reservation verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel

from .scenario_support import drain_callbacks_pair, wait_for_callback, wait_for_callback_count


@dataclass(frozen=True)
class NameReservationScenarioConfig:
    federation_name: str = "NameReservationFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    rival_name: str = "Rival"
    federate_type: str = "NameReservationFederate"
    reserved_name: str = "ReservedTarget"
    multiple_names: tuple[str, ...] = ("Reserved-A", "Reserved-B")


def run_name_reservation_scenario(
    owner_rti: Any,
    rival_rti: Any,
    *,
    config: NameReservationScenarioConfig,
    owner_federate: Any,
    rival_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    rival_rti.connect(rival_federate, CallbackModel.HLA_EVOKED)
    owner_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.joinFederationExecution(config.owner_name, config.federate_type, config.federation_name)
    rival_handle = rival_rti.joinFederationExecution(config.rival_name, config.federate_type, config.federation_name)

    owner_rti.reserveObjectInstanceName(config.reserved_name)
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    owner_reserved = wait_for_callback(
        owner_rti,
        owner_federate,
        "objectInstanceNameReservationSucceeded",
        loops=120,
    )
    assert owner_reserved is not None
    assert owner_reserved.args == (config.reserved_name,)

    rival_failure_count = len(rival_federate.callbacks_named("objectInstanceNameReservationFailed")) + 1
    rival_rti.reserveObjectInstanceName(config.reserved_name)
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    rival_failed_records = wait_for_callback_count(
        rival_rti,
        rival_federate,
        "objectInstanceNameReservationFailed",
        rival_failure_count,
        loops=120,
    )
    rival_reserved_failed = rival_failed_records[-1]
    assert rival_reserved_failed.args == (config.reserved_name,)

    owner_rti.releaseObjectInstanceName(config.reserved_name)
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)

    rival_success_count = len(rival_federate.callbacks_named("objectInstanceNameReservationSucceeded")) + 1
    rival_rti.reserveObjectInstanceName(config.reserved_name)
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    rival_reserved_records = wait_for_callback_count(
        rival_rti,
        rival_federate,
        "objectInstanceNameReservationSucceeded",
        rival_success_count,
        loops=120,
    )
    rival_reserved = rival_reserved_records[-1]
    assert rival_reserved.args == (config.reserved_name,)

    owner_rti.reserveMultipleObjectInstanceName(set(config.multiple_names))
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    owner_multiple_reserved = wait_for_callback(
        owner_rti,
        owner_federate,
        "multipleObjectInstanceNameReservationSucceeded",
        loops=120,
    )
    assert owner_multiple_reserved is not None
    assert owner_multiple_reserved.args[0] == set(config.multiple_names)

    rival_multiple_failure_count = len(rival_federate.callbacks_named("multipleObjectInstanceNameReservationFailed")) + 1
    rival_rti.reserveMultipleObjectInstanceName(set(config.multiple_names))
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    rival_multiple_failed_records = wait_for_callback_count(
        rival_rti,
        rival_federate,
        "multipleObjectInstanceNameReservationFailed",
        rival_multiple_failure_count,
        loops=120,
    )
    rival_multiple_reserved_failed = rival_multiple_failed_records[-1]
    assert rival_multiple_reserved_failed.args[0] == set(config.multiple_names)

    owner_rti.releaseMultipleObjectInstanceName(set(config.multiple_names))
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)

    rival_multiple_success_count = len(rival_federate.callbacks_named("multipleObjectInstanceNameReservationSucceeded")) + 1
    rival_rti.reserveMultipleObjectInstanceName(set(config.multiple_names))
    drain_callbacks_pair(owner_rti, rival_rti, loops=12)
    rival_multiple_reserved_records = wait_for_callback_count(
        rival_rti,
        rival_federate,
        "multipleObjectInstanceNameReservationSucceeded",
        rival_multiple_success_count,
        loops=120,
    )
    rival_multiple_reserved = rival_multiple_reserved_records[-1]
    assert rival_multiple_reserved.args[0] == set(config.multiple_names)

    return {
        "owner_handle": owner_handle,
        "rival_handle": rival_handle,
        "owner_reserved": owner_reserved,
        "rival_reserved_failed": rival_reserved_failed,
        "rival_reserved": rival_reserved,
        "owner_multiple_reserved": owner_multiple_reserved,
        "rival_multiple_reserved_failed": rival_multiple_reserved_failed,
        "rival_multiple_reserved": rival_multiple_reserved,
    }


__all__ = ["NameReservationScenarioConfig", "run_name_reservation_scenario"]
