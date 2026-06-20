"""Federation save/restore verification scenario."""
from __future__ import annotations

import copy
import json
import struct
from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction, RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
from hla.rti1516e.exceptions import (
    FederateNotExecutionMember,
    NotConnected,
    RestoreInProgress,
    RestoreNotRequested,
    RestoreNotInProgress,
    SaveInProgress,
    SaveNotInitiated,
    SaveNotInProgress,
)
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time

from .scenario_support import (
    drain_callbacks_pair,
    order_value,
    register_named_object_instance,
    wait_for_callback,
    wait_for_callback_count,
)


@dataclass(frozen=True)
class SaveRestoreScenarioConfig:
    federation_name: str = "SaveRestoreFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    federate_type: str = "SaveRestoreFederate"
    save_name: str = "SAVE-STATE"


def _save_statuses(record: Any) -> dict[Any, SaveStatus]:
    return {pair.federate_handle: pair.save_status for pair in record.args[0]}


def _restore_statuses(record: Any) -> dict[Any, RestoreStatus]:
    return {pair.pre_restore_handle: pair.restore_status for pair in record.args[0]}


def _time_value(value: Any) -> float:
    return float(getattr(value, "value", value))


def _encode_vec3(x: float, y: float, z: float) -> bytes:
    return struct.pack(">ddd", float(x), float(y), float(z))


def _decode_vec3(data: bytes) -> tuple[float, float, float]:
    return struct.unpack(">ddd", bytes(data)[:24])


def _encode_float64(value: float) -> bytes:
    return struct.pack(">d", float(value))


def _encode_text(value: str) -> bytes:
    return value.encode("utf-8")


def _ledger_fingerprint(ledger: dict[str, Any]) -> str:
    return json.dumps(ledger, sort_keys=True)


def _advance_ledger(ledger: dict[str, Any], *, phase: str) -> None:
    next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
    ledger["random_state"] = next_state
    ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
    ledger["phase"] = phase


def run_example_fom_save_restore_gauntlet_scenario(
    owner_rti: Any,
    mirror_rti: Any,
    sender_rti: Any,
    observer_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    owner_federate: Any,
    mirror_federate: Any,
    sender_federate: Any,
    observer_federate: Any,
    object_class_name: str = "HLAobjectRoot.Target",
    object_instance_name: str = "Target-Checkpoint-1",
    position_attribute_name: str = "Position",
    velocity_attribute_name: str = "Velocity",
    rcs_attribute_name: str = "RCS",
    interaction_class_name: str = "HLAinteractionRoot.TrackReport",
    interaction_parameter_name: str = "TrackId",
    save_time: int = 5,
    dirty_time: int = 8,
    branch_time: int = 7,
) -> dict[str, Any]:
    members = (
        (owner_rti, owner_federate, config.leader_name),
        (mirror_rti, mirror_federate, config.wing_name),
        (sender_rti, sender_federate, f"{config.leader_name}-Sender"),
        (observer_rti, observer_federate, f"{config.wing_name}-Observer"),
    )
    role_ledgers = {
        "owner": {"role": "owner", "random_state": 101, "sequence_counter": 0, "phase": "bootstrap"},
        "mirror": {"role": "mirror", "random_state": 202, "sequence_counter": 0, "phase": "bootstrap"},
        "sender": {"role": "sender", "random_state": 303, "sequence_counter": 0, "phase": "bootstrap"},
        "observer": {"role": "observer", "random_state": 404, "sequence_counter": 0, "phase": "bootstrap"},
    }
    saved_ledgers: dict[str, dict[str, Any]] = {}

    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    lookahead = HLAinteger64Interval(1)
    saved_time = HLAinteger64Time(save_time)
    dirty_advance_time = HLAinteger64Time(dirty_time)
    branch_event_time = HLAinteger64Time(branch_time)

    owner_class = owner_rti.get_object_class_handle(object_class_name)
    mirror_class = mirror_rti.get_object_class_handle(object_class_name)
    owner_position = owner_rti.get_attribute_handle(owner_class, position_attribute_name)
    owner_velocity = owner_rti.get_attribute_handle(owner_class, velocity_attribute_name)
    owner_rcs = owner_rti.get_attribute_handle(owner_class, rcs_attribute_name)
    mirror_position = mirror_rti.get_attribute_handle(mirror_class, position_attribute_name)
    mirror_velocity = mirror_rti.get_attribute_handle(mirror_class, velocity_attribute_name)
    mirror_rcs = mirror_rti.get_attribute_handle(mirror_class, rcs_attribute_name)
    interaction_class = sender_rti.get_interaction_class_handle(interaction_class_name)
    observer_interaction = observer_rti.get_interaction_class_handle(interaction_class_name)
    interaction_parameter = sender_rti.get_parameter_handle(interaction_class, interaction_parameter_name)
    observer_parameter = observer_rti.get_parameter_handle(observer_interaction, interaction_parameter_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_position, owner_velocity, owner_rcs})
    mirror_rti.subscribe_object_class_attributes(mirror_class, {mirror_position, mirror_velocity, mirror_rcs})
    sender_rti.publish_interaction_class(interaction_class)
    observer_rti.subscribe_interaction_class(observer_interaction)

    owner_rti.enable_time_regulation(lookahead)
    sender_rti.enable_time_regulation(lookahead)
    mirror_rti.enable_time_constrained()
    observer_rti.enable_time_constrained()
    sender_rti.change_interaction_order_type(interaction_class, OrderType.TIMESTAMP)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)

    object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, object_instance_name)
    owner_rti.change_attribute_order_type(object_instance, {owner_position, owner_velocity, owner_rcs}, OrderType.TIMESTAMP)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    mirror_object_instance = mirror_rti.get_object_instance_handle(object_instance_name)

    saved_position = (10_000.0, 1_000.0, 2_000.0)
    saved_velocity = (250.0, 30.0, 0.0)
    saved_rcs = 12.5
    dirty_position = (99_999.0, 88_888.0, 77_777.0)
    dirty_velocity = (0.0, 0.0, 0.0)
    dirty_rcs = 0.5
    branch_position = tuple(saved_position[index] + saved_velocity[index] for index in range(3))
    dirty_delete_tag = b"dirty-delete"

    owner_rti.update_attribute_values(
        object_instance,
        {
            owner_position: _encode_vec3(*saved_position),
            owner_velocity: _encode_vec3(*saved_velocity),
            owner_rcs: _encode_float64(saved_rcs),
        },
        b"baseline-attributes",
        HLAinteger64Time(save_time - 1),
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: _encode_text("baseline-track")},
        b"baseline-track",
        saved_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(saved_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    baseline_reflect = wait_for_callback(mirror_rti, mirror_federate, "reflectAttributeValues", loops=120)
    baseline_interaction = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=120)
    assert baseline_reflect is not None
    assert baseline_interaction is not None
    assert baseline_reflect.args[0] == mirror_object_instance
    assert _decode_vec3(baseline_reflect.args[1][mirror_position]) == saved_position
    assert _decode_vec3(baseline_reflect.args[1][mirror_velocity]) == saved_velocity
    assert baseline_interaction.args[0] == observer_interaction
    assert baseline_interaction.args[1] == {observer_parameter: _encode_text("baseline-track")}

    for ledger in role_ledgers.values():
        _advance_ledger(ledger, phase="saved")
    saved_ledgers = {role: copy.deepcopy(ledger) for role, ledger in role_ledgers.items()}
    saved_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in saved_ledgers.items()}

    owner_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        initiate = wait_for_callback(rti, federate, "initiateFederateSave", loops=120)
        assert initiate is not None
        assert initiate.args[0] == config.save_name

    for rti, _federate, _name in members:
        rti.federate_save_begun()
    for rti, _federate, _name in members:
        rti.federate_save_complete()
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        assert wait_for_callback(rti, federate, "federationSaved", loops=120) is not None

    for ledger in role_ledgers.values():
        _advance_ledger(ledger, phase="dirty")
    dirty_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in role_ledgers.items()}
    assert dirty_fingerprints != saved_fingerprints

    owner_rti.update_attribute_values(
        object_instance,
        {
            owner_position: _encode_vec3(*dirty_position),
            owner_velocity: _encode_vec3(*dirty_velocity),
            owner_rcs: _encode_float64(dirty_rcs),
        },
        b"dirty-attributes",
        HLAinteger64Time(dirty_time - 1),
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: _encode_text("dirty-track")},
        b"dirty-track",
        dirty_advance_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(dirty_advance_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    dirty_reflect = mirror_federate.callbacks_named("reflectAttributeValues")[-1]
    dirty_interaction = observer_federate.callbacks_named("receiveInteraction")[-1]
    assert _decode_vec3(dirty_reflect.args[1][mirror_position]) == dirty_position
    assert dirty_interaction.args[1] == {observer_parameter: _encode_text("dirty-track")}
    owner_rti.delete_object_instance(object_instance, dirty_delete_tag)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    dirty_remove = wait_for_callback(mirror_rti, mirror_federate, "removeObjectInstance", loops=120)
    assert dirty_remove is not None
    assert dirty_remove.args[0] == mirror_object_instance
    assert dirty_remove.args[1] == dirty_delete_tag

    owner_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        initiate = wait_for_callback(rti, federate, "initiateFederateRestore", loops=120)
        assert initiate is not None
        assert initiate.args[0] == config.save_name
    role_ledgers = {role: copy.deepcopy(snapshot) for role, snapshot in saved_ledgers.items()}

    for rti, _federate, _name in members:
        rti.federate_restore_complete()
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        assert wait_for_callback(rti, federate, "federationRestored", loops=120) is not None

    restored_times = {
        "owner": owner_rti.query_logical_time(),
        "mirror": mirror_rti.query_logical_time(),
        "sender": sender_rti.query_logical_time(),
        "observer": observer_rti.query_logical_time(),
    }
    for restored_time in restored_times.values():
        assert restored_time == saved_time

    restored_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in role_ledgers.items()}
    assert restored_fingerprints == saved_fingerprints
    assert owner_rti.get_object_instance_name(object_instance) == object_instance_name

    mirror_federate.clear()
    observer_federate.clear()
    owner_rti.update_attribute_values(
        object_instance,
        {
            owner_position: _encode_vec3(*branch_position),
            owner_velocity: _encode_vec3(*saved_velocity),
            owner_rcs: _encode_float64(saved_rcs),
        },
        b"branch-attributes",
        branch_event_time,
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: _encode_text("branch-track")},
        b"branch-track",
        branch_event_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(dirty_advance_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    branch_reflect = wait_for_callback(mirror_rti, mirror_federate, "reflectAttributeValues", loops=120)
    branch_interaction = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=120)
    assert branch_reflect is not None
    assert branch_interaction is not None
    assert branch_reflect.args[0] == mirror_object_instance
    assert _decode_vec3(branch_reflect.args[1][mirror_position]) == branch_position
    assert branch_interaction.args[1] == {observer_parameter: _encode_text("branch-track")}
    branch_tags = {record.args[2] for record in mirror_federate.callbacks_named("reflectAttributeValues")}
    branch_tags.update(record.args[2] for record in observer_federate.callbacks_named("receiveInteraction"))
    assert b"dirty-attributes" not in branch_tags
    assert b"dirty-track" not in branch_tags
    remove_tags = {record.args[1] for record in mirror_federate.callbacks_named("removeObjectInstance")}
    assert dirty_delete_tag not in remove_tags

    return {
        "object_instance": object_instance,
        "mirror_object_instance": mirror_object_instance,
        "baseline_reflect": baseline_reflect,
        "baseline_interaction": baseline_interaction,
        "dirty_reflect": dirty_reflect,
        "dirty_interaction": dirty_interaction,
        "dirty_remove": dirty_remove,
        "branch_reflect": branch_reflect,
        "branch_interaction": branch_interaction,
        "saved_fingerprints": saved_fingerprints,
        "dirty_fingerprints": dirty_fingerprints,
        "restored_fingerprints": restored_fingerprints,
        "restored_times": restored_times,
    }


def run_smoke_fom_save_restore_ownership_gauntlet_scenario(
    owner_rti: Any,
    mirror_rti: Any,
    sender_rti: Any,
    observer_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    owner_federate: Any,
    mirror_federate: Any,
    sender_federate: Any,
    observer_federate: Any,
    object_class_name: str = "HLAobjectRoot.SmokeObject",
    object_instance_name: str = "Owned-Smoke-Checkpoint-1",
    attribute_name: str = "Payload",
    interaction_class_name: str = "HLAinteractionRoot.SmokeInteraction",
    parameter_name: str = "Message",
    save_time: int = 5,
    dirty_time: int = 8,
    branch_time: int = 7,
) -> dict[str, Any]:
    members = (
        (owner_rti, owner_federate, config.leader_name),
        (mirror_rti, mirror_federate, config.wing_name),
        (sender_rti, sender_federate, f"{config.leader_name}-Sender"),
        (observer_rti, observer_federate, f"{config.wing_name}-Observer"),
    )
    role_ledgers = {
        "owner": {"role": "owner", "random_state": 111, "sequence_counter": 0, "phase": "bootstrap"},
        "mirror": {"role": "mirror", "random_state": 222, "sequence_counter": 0, "phase": "bootstrap"},
        "sender": {"role": "sender", "random_state": 333, "sequence_counter": 0, "phase": "bootstrap"},
        "observer": {"role": "observer", "random_state": 444, "sequence_counter": 0, "phase": "bootstrap"},
    }

    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    lookahead = HLAinteger64Interval(1)
    saved_time = HLAinteger64Time(save_time)
    dirty_advance_time = HLAinteger64Time(dirty_time)
    branch_event_time = HLAinteger64Time(branch_time)

    owner_class = owner_rti.get_object_class_handle(object_class_name)
    mirror_class = mirror_rti.get_object_class_handle(object_class_name)
    observer_class = observer_rti.get_object_class_handle(object_class_name)
    owner_attribute = owner_rti.get_attribute_handle(owner_class, attribute_name)
    mirror_attribute = mirror_rti.get_attribute_handle(mirror_class, attribute_name)
    observer_attribute = observer_rti.get_attribute_handle(observer_class, attribute_name)
    interaction_class = sender_rti.get_interaction_class_handle(interaction_class_name)
    observer_interaction = observer_rti.get_interaction_class_handle(interaction_class_name)
    interaction_parameter = sender_rti.get_parameter_handle(interaction_class, parameter_name)
    observer_parameter = observer_rti.get_parameter_handle(observer_interaction, parameter_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_attribute})
    mirror_rti.publish_object_class_attributes(mirror_class, {mirror_attribute})
    mirror_rti.subscribe_object_class_attributes(mirror_class, {mirror_attribute})
    observer_rti.subscribe_object_class_attributes(observer_class, {observer_attribute})
    sender_rti.publish_interaction_class(interaction_class)
    observer_rti.subscribe_interaction_class(observer_interaction)

    owner_rti.enable_time_regulation(lookahead)
    sender_rti.enable_time_regulation(lookahead)
    mirror_rti.enable_time_constrained()
    observer_rti.enable_time_constrained()
    sender_rti.change_interaction_order_type(interaction_class, OrderType.TIMESTAMP)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)

    object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, object_instance_name)
    owner_rti.change_attribute_order_type(object_instance, {owner_attribute}, OrderType.TIMESTAMP)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    mirror_object_instance = mirror_rti.get_object_instance_handle(object_instance_name)
    observer_object_instance = observer_rti.get_object_instance_handle(object_instance_name)

    saved_payload = b"saved-payload"
    dirty_payload = b"dirty-payload"
    branch_payload = b"branch-payload"

    owner_rti.update_attribute_values(
        object_instance,
        {owner_attribute: saved_payload},
        b"baseline-attributes",
        HLAinteger64Time(save_time - 1),
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: b"baseline-message"},
        b"baseline-message",
        saved_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(saved_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    baseline_reflect = wait_for_callback(observer_rti, observer_federate, "reflectAttributeValues", loops=120)
    baseline_interaction = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=120)
    assert baseline_reflect is not None
    assert baseline_interaction is not None
    assert baseline_reflect.args[0] == observer_object_instance
    assert baseline_reflect.args[1] == {observer_attribute: saved_payload}
    assert baseline_interaction.args[1] == {observer_parameter: b"baseline-message"}
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attribute) is True
    assert mirror_rti.is_attribute_owned_by_federate(mirror_object_instance, mirror_attribute) is False

    for ledger in role_ledgers.values():
        _advance_ledger(ledger, phase="saved")
    saved_ledgers = {role: copy.deepcopy(ledger) for role, ledger in role_ledgers.items()}
    saved_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in saved_ledgers.items()}

    owner_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        initiate = wait_for_callback(rti, federate, "initiateFederateSave", loops=120)
        assert initiate is not None
        assert initiate.args[0] == config.save_name
    for rti, _federate, _name in members:
        rti.federate_save_begun()
    for rti, _federate, _name in members:
        rti.federate_save_complete()
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        assert wait_for_callback(rti, federate, "federationSaved", loops=120) is not None

    for ledger in role_ledgers.values():
        _advance_ledger(ledger, phase="dirty")
    dirty_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in role_ledgers.items()}
    assert dirty_fingerprints != saved_fingerprints

    owner_rti.unconditional_attribute_ownership_divestiture(object_instance, {owner_attribute})
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=12)
    owner_rti.query_attribute_ownership(object_instance, owner_attribute)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=12)
    dirty_not_owned = wait_for_callback(owner_rti, owner_federate, "attributeIsNotOwned", loops=120)
    assert dirty_not_owned is not None

    mirror_rti.attribute_ownership_acquisition_if_available(mirror_object_instance, {mirror_attribute})
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=12)
    dirty_acquired = wait_for_callback(
        mirror_rti,
        mirror_federate,
        "attributeOwnershipAcquisitionNotification",
        loops=120,
    )
    assert dirty_acquired is not None
    assert mirror_rti.is_attribute_owned_by_federate(mirror_object_instance, mirror_attribute) is True
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attribute) is False

    mirror_rti.update_attribute_values(
        mirror_object_instance,
        {mirror_attribute: dirty_payload},
        b"dirty-attributes",
        HLAinteger64Time(dirty_time - 1),
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: b"dirty-message"},
        b"dirty-message",
        dirty_advance_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(dirty_advance_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    dirty_reflect = observer_federate.callbacks_named("reflectAttributeValues")[-1]
    dirty_interaction = observer_federate.callbacks_named("receiveInteraction")[-1]
    assert dirty_reflect.args[0] == observer_object_instance
    assert dirty_reflect.args[1] == {observer_attribute: dirty_payload}
    assert dirty_interaction.args[1] == {observer_parameter: b"dirty-message"}

    owner_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        initiate = wait_for_callback(rti, federate, "initiateFederateRestore", loops=120)
        assert initiate is not None
        assert initiate.args[0] == config.save_name
    role_ledgers = {role: copy.deepcopy(snapshot) for role, snapshot in saved_ledgers.items()}

    for rti, _federate, _name in members:
        rti.federate_restore_complete()
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=24)
    for rti, federate, _name in members:
        assert wait_for_callback(rti, federate, "federationRestored", loops=120) is not None

    restored_times = {
        "owner": owner_rti.query_logical_time(),
        "mirror": mirror_rti.query_logical_time(),
        "sender": sender_rti.query_logical_time(),
        "observer": observer_rti.query_logical_time(),
    }
    for restored_time in restored_times.values():
        assert restored_time == saved_time
    restored_fingerprints = {role: _ledger_fingerprint(ledger) for role, ledger in role_ledgers.items()}
    assert restored_fingerprints == saved_fingerprints

    owner_federate.clear()
    observer_federate.clear()

    owner_rti.query_attribute_ownership(object_instance, owner_attribute)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=12)
    restored_informed = wait_for_callback(owner_rti, owner_federate, "informAttributeOwnership", loops=120)
    assert restored_informed is not None
    assert restored_informed.args[0] == object_instance
    assert restored_informed.args[1] == owner_attribute
    assert owner_rti.get_federate_name(restored_informed.args[2]) == config.leader_name
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attribute) is True
    assert mirror_rti.is_attribute_owned_by_federate(mirror_object_instance, mirror_attribute) is False

    owner_rti.update_attribute_values(
        object_instance,
        {owner_attribute: branch_payload},
        b"branch-attributes",
        branch_event_time,
    )
    sender_rti.send_interaction(
        interaction_class,
        {interaction_parameter: b"branch-message"},
        b"branch-message",
        branch_event_time,
    )
    for rti, _federate, _name in members:
        rti.time_advance_request_available(dirty_advance_time)
    drain_callbacks_pair(owner_rti, mirror_rti, sender_rti, observer_rti, loops=32)

    branch_reflect = wait_for_callback(observer_rti, observer_federate, "reflectAttributeValues", loops=120)
    branch_interaction = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=120)
    assert branch_reflect is not None
    assert branch_interaction is not None
    assert branch_reflect.args[0] == observer_object_instance
    assert branch_reflect.args[1] == {observer_attribute: branch_payload}
    assert branch_interaction.args[1] == {observer_parameter: b"branch-message"}
    branch_tags = {record.args[2] for record in observer_federate.callbacks_named("reflectAttributeValues")}
    branch_tags.update(record.args[2] for record in observer_federate.callbacks_named("receiveInteraction"))
    assert b"dirty-attributes" not in branch_tags
    assert b"dirty-message" not in branch_tags

    return {
        "object_instance": object_instance,
        "mirror_object_instance": mirror_object_instance,
        "observer_object_instance": observer_object_instance,
        "baseline_reflect": baseline_reflect,
        "baseline_interaction": baseline_interaction,
        "dirty_not_owned": dirty_not_owned,
        "dirty_acquired": dirty_acquired,
        "dirty_reflect": dirty_reflect,
        "dirty_interaction": dirty_interaction,
        "restored_informed": restored_informed,
        "branch_reflect": branch_reflect,
        "branch_interaction": branch_interaction,
        "saved_fingerprints": saved_fingerprints,
        "dirty_fingerprints": dirty_fingerprints,
        "restored_fingerprints": restored_fingerprints,
        "restored_times": restored_times,
    }


def run_save_restore_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
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

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None
    assert leader_initiate_save.args[0] == config.save_name
    assert wing_initiate_save.args[0] == config.save_name

    save_status_count = len(leader_federate.callbacks_named("federationSaveStatusResponse")) + 1
    leader_rti.query_federation_save_status()
    save_status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationSaveStatusResponse",
        save_status_count,
        loops=120,
    )
    save_status_pending = save_status_records[-1]
    pending_save = _save_statuses(save_status_pending)
    assert pending_save[leader_handle] is not SaveStatus.NO_SAVE_IN_PROGRESS
    assert pending_save[wing_handle] is not SaveStatus.NO_SAVE_IN_PROGRESS

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
    wing_saved = wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)
    assert leader_saved is not None
    assert wing_saved is not None

    leader_rti.query_federation_save_status()
    save_status_cleared_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationSaveStatusResponse",
        save_status_count + 1,
        loops=120,
    )
    save_status_cleared = save_status_cleared_records[-1]
    cleared_save = _save_statuses(save_status_cleared)
    assert all(status is SaveStatus.NO_SAVE_IN_PROGRESS for status in cleared_save.values())

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restore_succeeded = wait_for_callback(
        leader_rti,
        leader_federate,
        "requestFederationRestoreSucceeded",
        loops=120,
    )
    leader_restore_begun = wait_for_callback(
        leader_rti,
        leader_federate,
        "federationRestoreBegun",
        loops=120,
    )
    wing_initiate_restore = wait_for_callback(
        wing_rti,
        wing_federate,
        "initiateFederateRestore",
        loops=120,
    )
    assert leader_restore_succeeded is not None
    assert leader_restore_begun is not None
    assert wing_initiate_restore is not None
    assert leader_restore_succeeded.args == (config.save_name,)
    assert wing_initiate_restore.args[0] == config.save_name

    restore_status_count = len(leader_federate.callbacks_named("federationRestoreStatusResponse")) + 1
    leader_rti.query_federation_restore_status()
    restore_status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationRestoreStatusResponse",
        restore_status_count,
        loops=120,
    )
    restore_status_pending = restore_status_records[-1]
    pending_restore = _restore_statuses(restore_status_pending)
    assert pending_restore[leader_handle] is not RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert pending_restore[wing_handle] is not RestoreStatus.NO_RESTORE_IN_PROGRESS

    leader_rti.federate_restore_complete()
    wing_rti.federate_restore_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restored = wait_for_callback(leader_rti, leader_federate, "federationRestored", loops=120)
    wing_restored = wait_for_callback(wing_rti, wing_federate, "federationRestored", loops=120)
    assert leader_restored is not None
    assert wing_restored is not None

    leader_rti.query_federation_restore_status()
    restore_status_cleared_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationRestoreStatusResponse",
        restore_status_count + 1,
        loops=120,
    )
    restore_status_cleared = restore_status_cleared_records[-1]
    cleared_restore = _restore_statuses(restore_status_cleared)
    assert all(status is RestoreStatus.NO_RESTORE_IN_PROGRESS for status in cleared_restore.values())

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "save_status_pending": save_status_pending,
        "leader_saved": leader_saved,
        "wing_saved": wing_saved,
        "save_status_cleared": save_status_cleared,
        "leader_restore_succeeded": leader_restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
        "wing_initiate_restore": wing_initiate_restore,
        "restore_status_pending": restore_status_pending,
        "leader_restored": leader_restored,
        "wing_restored": wing_restored,
        "restore_status_cleared": restore_status_cleared,
    }


def run_scheduled_save_restore_time_state_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    save_time: Any,
    post_save_time: Any,
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
    leader_factory = leader_rti.get_time_factory()
    wing_factory = wing_rti.get_time_factory()
    expected_save_time_leader = leader_factory.make_time(_time_value(save_time))
    expected_save_time_wing = wing_factory.make_time(_time_value(save_time))
    expected_post_save_time_leader = leader_factory.make_time(_time_value(post_save_time))
    expected_post_save_time_wing = wing_factory.make_time(_time_value(post_save_time))

    leader_rti.enable_time_constrained()
    wing_rti.enable_time_constrained()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)

    leader_rti.request_federation_save(config.save_name, save_time)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    assert leader_federate.last_callback("initiateFederateSave") is None
    assert wing_federate.last_callback("initiateFederateSave") is None

    leader_rti.time_advance_request_available(save_time)
    wing_rti.time_advance_request_available(save_time)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None
    assert leader_initiate_save.args[0] == config.save_name
    assert wing_initiate_save.args[0] == config.save_name

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
    wing_saved = wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)
    assert leader_saved is not None
    assert wing_saved is not None

    leader_rti.time_advance_request_available(post_save_time)
    wing_rti.time_advance_request_available(post_save_time)
    leader_logical_time = None
    wing_logical_time = None
    for _ in range(24):
        drain_callbacks_pair(leader_rti, wing_rti, loops=2)
        leader_logical_time = leader_rti.query_logical_time()
        wing_logical_time = wing_rti.query_logical_time()
        if (
            leader_logical_time == expected_post_save_time_leader
            and wing_logical_time == expected_post_save_time_wing
        ):
            break
    assert leader_logical_time == expected_post_save_time_leader
    assert wing_logical_time == expected_post_save_time_wing

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restore_succeeded = wait_for_callback(
        leader_rti,
        leader_federate,
        "requestFederationRestoreSucceeded",
        loops=120,
    )
    leader_restore_begun = wait_for_callback(
        leader_rti,
        leader_federate,
        "federationRestoreBegun",
        loops=120,
    )
    wing_initiate_restore = wait_for_callback(
        wing_rti,
        wing_federate,
        "initiateFederateRestore",
        loops=120,
    )
    assert leader_restore_succeeded is not None
    assert leader_restore_begun is not None
    assert wing_initiate_restore is not None
    assert leader_restore_succeeded.args == (config.save_name,)
    assert wing_initiate_restore.args[0] == config.save_name

    leader_rti.federate_restore_complete()
    wing_rti.federate_restore_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restored = wait_for_callback(leader_rti, leader_federate, "federationRestored", loops=120)
    wing_restored = wait_for_callback(wing_rti, wing_federate, "federationRestored", loops=120)
    assert leader_restored is not None
    assert wing_restored is not None

    restored_leader_time = leader_rti.query_logical_time()
    restored_wing_time = wing_rti.query_logical_time()
    assert restored_leader_time == expected_save_time_leader
    assert restored_wing_time == expected_save_time_wing

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "leader_saved": leader_saved,
        "wing_saved": wing_saved,
        "leader_logical_time": leader_logical_time,
        "wing_logical_time": wing_logical_time,
        "leader_restore_succeeded": leader_restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
        "wing_initiate_restore": wing_initiate_restore,
        "leader_restored": leader_restored,
        "wing_restored": wing_restored,
        "restored_leader_time": restored_leader_time,
        "restored_wing_time": restored_wing_time,
    }


def run_save_restore_queued_callback_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    try:
        leader_rti.request_federation_save(config.save_name)
        leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
        assert leader_initiate_save is not None
        assert leader_initiate_save.args == (config.save_name,)

        wing_initiate_save = wing_federate.last_callback("initiateFederateSave")
        if wing_initiate_save is None:
            wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
        assert wing_initiate_save is not None
        assert wing_initiate_save.args == (config.save_name,)

        leader_rti.federate_save_begun()
        wing_rti.federate_save_begun()
        leader_rti.federate_save_complete()
        wing_rti.federate_save_complete()

        leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
        assert leader_saved is not None

        wing_saved = wing_federate.last_callback("federationSaved")
        if wing_saved is None:
            wing_saved = wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)
        assert wing_saved is not None

        leader_rti.request_federation_restore(config.save_name)
        leader_restore_succeeded = wait_for_callback(
            leader_rti,
            leader_federate,
            "requestFederationRestoreSucceeded",
            loops=120,
        )
        leader_restore_begun = wait_for_callback(
            leader_rti,
            leader_federate,
            "federationRestoreBegun",
            loops=120,
        )
        assert leader_restore_succeeded is not None
        assert leader_restore_begun is not None
        assert leader_restore_succeeded.args == (config.save_name,)

        wing_initiate_restore = wing_federate.last_callback("initiateFederateRestore")
        if wing_initiate_restore is None:
            wing_initiate_restore = wait_for_callback(
                wing_rti,
                wing_federate,
                "initiateFederateRestore",
                loops=120,
            )
        assert wing_initiate_restore is not None
        assert wing_initiate_restore.args[0] == config.save_name

        leader_rti.federate_restore_complete()
        wing_rti.federate_restore_complete()

        leader_restored = wait_for_callback(leader_rti, leader_federate, "federationRestored", loops=120)
        assert leader_restored is not None

        wing_restored = wing_federate.last_callback("federationRestored")
        if wing_restored is None:
            wing_restored = wait_for_callback(wing_rti, wing_federate, "federationRestored", loops=120)
        assert wing_restored is not None

        return {
            "leader_initiate_save": leader_initiate_save,
            "wing_initiate_save": wing_initiate_save,
            "leader_saved": leader_saved,
            "wing_saved": wing_saved,
            "leader_restore_succeeded": leader_restore_succeeded,
            "leader_restore_begun": leader_restore_begun,
            "wing_initiate_restore": wing_initiate_restore,
            "leader_restored": leader_restored,
            "wing_restored": wing_restored,
        }
    finally:
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


def _connect_pair(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> tuple[Any, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)
    return leader_handle, wing_handle


def run_restore_round_trip_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    setup_saved_state: Any,
    mutate_post_save_state: Any,
    assert_restored_state: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )
    context = {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
    }
    setup_saved_state(leader_rti, wing_rti, context)

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
    wing_saved = wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)
    assert leader_saved is not None
    assert wing_saved is not None

    mutate_post_save_state(leader_rti, wing_rti, context)

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restore_succeeded = wait_for_callback(
        leader_rti,
        leader_federate,
        "requestFederationRestoreSucceeded",
        loops=120,
    )
    leader_restore_begun = wait_for_callback(
        leader_rti,
        leader_federate,
        "federationRestoreBegun",
        loops=120,
    )
    wing_initiate_restore = wait_for_callback(
        wing_rti,
        wing_federate,
        "initiateFederateRestore",
        loops=120,
    )
    assert leader_restore_succeeded is not None
    assert leader_restore_begun is not None
    assert wing_initiate_restore is not None

    leader_rti.federate_restore_complete()
    wing_rti.federate_restore_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restored = wait_for_callback(leader_rti, leader_federate, "federationRestored", loops=120)
    wing_restored = wait_for_callback(wing_rti, wing_federate, "federationRestored", loops=120)
    assert leader_restored is not None
    assert wing_restored is not None

    assert_restored_state(leader_rti, wing_rti, context)

    return {
        **context,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "leader_saved": leader_saved,
        "wing_saved": wing_saved,
        "leader_restore_succeeded": leader_restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
        "wing_initiate_restore": wing_initiate_restore,
        "leader_restored": leader_restored,
        "wing_restored": wing_restored,
    }


def run_restore_object_state_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    setup_saved_state: Any | None = None,
    mutate_post_save_state: Any | None = None,
    assert_restored_state: Any | None = None,
    object_class_name: str = "HLAobjectRoot.Target",
    attribute_name: str = "Position",
    object_instance_name: str = "Restore-State-Object",
    saved_value: bytes = b"saved-value",
    saved_tag: bytes = b"saved",
    mutated_value: bytes = b"mutated-value",
    mutated_tag: bytes = b"mutated",
) -> dict[str, Any]:
    def _default_setup_saved_state(owner: Any, acquirer: Any, context: dict[str, Any]) -> None:
        owner_class = owner.get_object_class_handle(object_class_name)
        acquirer_class = acquirer.get_object_class_handle(object_class_name)
        owner_attribute = owner.get_attribute_handle(owner_class, attribute_name)
        acquirer_attribute = acquirer.get_attribute_handle(acquirer_class, attribute_name)
        owner.publish_object_class_attributes(owner_class, {owner_attribute})
        acquirer.publish_object_class_attributes(acquirer_class, {acquirer_attribute})
        acquirer.subscribe_object_class_attributes(acquirer_class, {acquirer_attribute})
        object_instance = owner.register_object_instance(owner_class, object_instance_name)
        owner.update_attribute_values(object_instance, {owner_attribute: saved_value}, saved_tag)
        drain_callbacks_pair(owner, acquirer, loops=16)
        owner.unconditional_attribute_ownership_divestiture(object_instance, {owner_attribute})
        acquirer_object_instance = acquirer.get_object_instance_handle(object_instance_name)
        acquirer.attribute_ownership_acquisition_if_available(acquirer_object_instance, {acquirer_attribute})
        drain_callbacks_pair(owner, acquirer, loops=16)
        context.update(
            {
                "object_instance": object_instance,
                "acquirer_object_instance": acquirer_object_instance,
                "owner_class": owner_class,
                "acquirer_class": acquirer_class,
                "owner_attribute": owner_attribute,
                "acquirer_attribute": acquirer_attribute,
            }
        )

    def _default_mutate_post_save_state(owner: Any, acquirer: Any, context: dict[str, Any]) -> None:
        object_instance = context["object_instance"]
        owner_attribute = context["owner_attribute"]
        acquirer_object_instance = context["acquirer_object_instance"]
        acquirer_attribute = context["acquirer_attribute"]
        acquirer.unconditional_attribute_ownership_divestiture(acquirer_object_instance, {acquirer_attribute})
        owner.attribute_ownership_acquisition_if_available(object_instance, {owner_attribute})
        drain_callbacks_pair(owner, acquirer, loops=16)
        owner.update_attribute_values(object_instance, {owner_attribute: mutated_value}, mutated_tag)
        drain_callbacks_pair(owner, acquirer, loops=16)

    def _default_assert_restored_state(owner: Any, acquirer: Any, context: dict[str, Any]) -> None:
        object_instance = context["object_instance"]
        acquirer_object_instance = context["acquirer_object_instance"]
        owner_attribute = context["owner_attribute"]
        acquirer_attribute = context["acquirer_attribute"]
        assert owner.get_object_instance_name(object_instance) == object_instance_name
        assert acquirer.get_object_instance_name(acquirer_object_instance) == object_instance_name
        owner.query_attribute_ownership(object_instance, owner_attribute)
        drain_callbacks_pair(owner, acquirer, loops=16)
        informed = wait_for_callback(owner, leader_federate, "informAttributeOwnership", loops=120)
        assert informed is not None
        assert informed.args[0] == object_instance
        assert informed.args[1] == owner_attribute
        assert acquirer.is_attribute_owned_by_federate(acquirer_object_instance, acquirer_attribute)
        context["informed"] = informed
        context["informed_federate_name"] = owner.get_federate_name(informed.args[2])

    if setup_saved_state is None:
        setup_saved_state = _default_setup_saved_state
    if mutate_post_save_state is None:
        mutate_post_save_state = _default_mutate_post_save_state
    if assert_restored_state is None:
        assert_restored_state = _default_assert_restored_state

    return run_restore_round_trip_scenario(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
        setup_saved_state=setup_saved_state,
        mutate_post_save_state=mutate_post_save_state,
        assert_restored_state=assert_restored_state,
    )


def run_restore_federate_local_state_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    setup_saved_state: Any | None = None,
    mutate_post_save_state: Any | None = None,
    assert_restored_state: Any | None = None,
    object_class_name: str = "HLAobjectRoot.Target",
    attribute_name: str = "Position",
    interaction_class_name: str = "HLAinteractionRoot.TrackReport",
    parameter_name: str = "TrackId",
    object_instance_name: str = "Restore-Local-State",
    best_effort_transportation_name: str = "HLAbestEffort",
    reliable_transportation_name: str = "HLAreliable",
    initial_lookahead: float = 2.0,
    modified_lookahead: float = 5.0,
    attribute_payload: bytes = b"restored-attribute",
    attribute_tag: bytes = b"restored-attribute-tag",
    interaction_payload: bytes = b"restored-interaction",
    interaction_tag: bytes = b"restored-interaction-tag",
    attribute_time: float = 6.0,
    interaction_time: float = 7.0,
    advance_time: float = 8.0,
) -> dict[str, Any]:
    def _default_setup_saved_state(r1: Any, r2: Any, context: dict[str, Any]) -> None:
        factory = r1.get_time_factory()
        leader_object_class = r1.get_object_class_handle(object_class_name)
        wing_object_class = r2.get_object_class_handle(object_class_name)
        leader_attribute = r1.get_attribute_handle(leader_object_class, attribute_name)
        wing_attribute = r2.get_attribute_handle(wing_object_class, attribute_name)
        leader_interaction = r1.get_interaction_class_handle(interaction_class_name)
        wing_interaction = r2.get_interaction_class_handle(interaction_class_name)
        leader_parameter = r1.get_parameter_handle(leader_interaction, parameter_name)
        wing_parameter = r2.get_parameter_handle(wing_interaction, parameter_name)
        best_effort_transport = r1.get_transportation_type_handle(best_effort_transportation_name)
        r1.publish_object_class_attributes(leader_object_class, {leader_attribute})
        r2.subscribe_object_class_attributes(wing_object_class, {wing_attribute})
        r1.publish_interaction_class(leader_interaction)
        r2.subscribe_interaction_class(wing_interaction)
        drain_callbacks_pair(r1, r2, loops=8)
        object_instance = r1.register_object_instance(leader_object_class, object_instance_name)
        drain_callbacks_pair(r1, r2, loops=8)
        wing_object_instance = r2.get_object_instance_handle(object_instance_name)
        r1.enable_time_regulation(factory.make_interval(initial_lookahead))
        r1.enable_asynchronous_delivery()
        r2.enable_time_constrained()
        r1.change_attribute_order_type(object_instance, {leader_attribute}, OrderType.TIMESTAMP)
        r1.change_interaction_order_type(leader_interaction, OrderType.TIMESTAMP)
        r1.request_attribute_transportation_type_change(object_instance, {leader_attribute}, best_effort_transport)
        r1.request_interaction_transportation_type_change(leader_interaction, best_effort_transport)
        drain_callbacks_pair(r1, r2, loops=16)
        context.update(
            {
                "factory": factory,
                "object_instance": object_instance,
                "wing_object_instance": wing_object_instance,
                "leader_object_class": leader_object_class,
                "wing_object_class": wing_object_class,
                "leader_attribute": leader_attribute,
                "wing_attribute": wing_attribute,
                "leader_interaction": leader_interaction,
                "wing_interaction": wing_interaction,
                "leader_parameter": leader_parameter,
                "wing_parameter": wing_parameter,
                "best_effort_transport": best_effort_transport,
            }
        )

    def _default_mutate_post_save_state(r1: Any, r2: Any, context: dict[str, Any]) -> None:
        object_instance = context["object_instance"]
        leader_attribute = context["leader_attribute"]
        leader_interaction = context["leader_interaction"]
        factory = context["factory"]
        reliable_transport = r1.get_transportation_type_handle(reliable_transportation_name)
        r1.modify_lookahead(factory.make_interval(modified_lookahead))
        r1.disable_asynchronous_delivery()
        r1.disable_time_regulation()
        r2.disable_time_constrained()
        r1.change_attribute_order_type(object_instance, {leader_attribute}, OrderType.RECEIVE)
        r1.change_interaction_order_type(leader_interaction, OrderType.RECEIVE)
        r1.request_attribute_transportation_type_change(object_instance, {leader_attribute}, reliable_transport)
        r1.request_interaction_transportation_type_change(leader_interaction, reliable_transport)
        drain_callbacks_pair(r1, r2, loops=16)
        context["reliable_transport"] = reliable_transport

    def _default_assert_restored_state(r1: Any, r2: Any, context: dict[str, Any]) -> None:
        object_instance = context["object_instance"]
        wing_object_instance = context["wing_object_instance"]
        leader_attribute = context["leader_attribute"]
        wing_attribute = context["wing_attribute"]
        leader_interaction = context["leader_interaction"]
        wing_parameter = context["wing_parameter"]
        leader_parameter = context["leader_parameter"]
        factory = context["factory"]
        best_effort_transport = context["best_effort_transport"]

        assert r1.query_lookahead() == factory.make_interval(initial_lookahead)

        leader_federate.clear()
        r1.query_attribute_transportation_type(object_instance, leader_attribute)
        r1.query_interaction_transportation_type(leader_interaction)
        drain_callbacks_pair(r1, r2, loops=16)
        attribute_report = wait_for_callback(r1, leader_federate, "reportAttributeTransportationType", loops=120)
        interaction_report = wait_for_callback(r1, leader_federate, "reportInteractionTransportationType", loops=120)
        assert attribute_report is not None
        assert interaction_report is not None
        assert attribute_report.args[0] == object_instance
        assert attribute_report.args[1] == leader_attribute
        assert attribute_report.args[2] == best_effort_transport
        assert interaction_report.args[1] == leader_interaction
        assert interaction_report.args[2] == best_effort_transport

        leader_federate.clear()
        wing_federate.clear()
        r1.update_attribute_values(
            object_instance,
            {leader_attribute: attribute_payload},
            attribute_tag,
            factory.make_time(attribute_time),
        )
        r1.send_interaction(
            leader_interaction,
            {leader_parameter: interaction_payload},
            interaction_tag,
            factory.make_time(interaction_time),
        )
        r1.time_advance_request(factory.make_time(advance_time))
        r2.time_advance_request(factory.make_time(advance_time))
        drain_callbacks_pair(r1, r2, loops=24)

        reflect = wait_for_callback(r2, wing_federate, "reflectAttributeValues", loops=120)
        interaction = wait_for_callback(r2, wing_federate, "receiveInteraction", loops=120)
        assert reflect is not None
        assert interaction is not None
        assert reflect.args[0] == wing_object_instance
        assert reflect.args[1] == {wing_attribute: attribute_payload}
        assert reflect.args[2] == attribute_tag
        assert order_value(reflect.args[3]) == OrderType.TIMESTAMP.value
        assert reflect.args[4] == best_effort_transport
        assert reflect.args[5] == factory.make_time(attribute_time)
        assert interaction.args[0] == context["wing_interaction"]
        assert interaction.args[1] == {wing_parameter: interaction_payload}
        assert interaction.args[2] == interaction_tag
        assert order_value(interaction.args[3]) == OrderType.TIMESTAMP.value
        assert interaction.args[4] == best_effort_transport
        assert interaction.args[5] == factory.make_time(interaction_time)

        r1.disable_asynchronous_delivery()
        r1.disable_time_regulation()
        r2.disable_time_constrained()
        context["post_restore_attribute_report"] = attribute_report
        context["post_restore_interaction_report"] = interaction_report
        context["post_restore_reflect"] = reflect
        context["post_restore_receive_interaction"] = interaction

    if setup_saved_state is None:
        setup_saved_state = _default_setup_saved_state
    if mutate_post_save_state is None:
        mutate_post_save_state = _default_mutate_post_save_state
    if assert_restored_state is None:
        assert_restored_state = _default_assert_restored_state

    return run_restore_round_trip_scenario(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
        setup_saved_state=setup_saved_state,
        mutate_post_save_state=mutate_post_save_state,
        assert_restored_state=assert_restored_state,
    )


def run_restore_callback_policy_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    setup_saved_state: Any,
    mutate_post_save_state: Any,
    assert_restored_state: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )
    context = {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
    }
    setup_saved_state(leader_rti, wing_rti, context)

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
    wing_saved = wait_for_callback(wing_rti, wing_federate, "federationSaved", loops=120)
    assert leader_saved is not None
    assert wing_saved is not None

    mutate_post_save_state(leader_rti, wing_rti, context)

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_restore_succeeded = wait_for_callback(
        leader_rti,
        leader_federate,
        "requestFederationRestoreSucceeded",
        loops=120,
    )
    leader_restore_begun = wait_for_callback(
        leader_rti,
        leader_federate,
        "federationRestoreBegun",
        loops=120,
    )
    assert leader_restore_succeeded is not None
    assert leader_restore_begun is not None

    leader_rti.federate_restore_complete()
    wing_rti.federate_restore_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    assert_restored_state(leader_rti, wing_rti, context)

    return {
        **context,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "leader_saved": leader_saved,
        "wing_saved": wing_saved,
        "leader_restore_succeeded": leader_restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
    }


def run_restore_transient_state_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    setup_saved_state: Any,
    mutate_post_save_state: Any,
    assert_restored_state: Any,
) -> dict[str, Any]:
    return run_restore_round_trip_scenario(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
        setup_saved_state=setup_saved_state,
        mutate_post_save_state=mutate_post_save_state,
        assert_restored_state=assert_restored_state,
    )


def run_save_request_precondition_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.request_federation_save(config.save_name)
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_save to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.request_federation_save(config.save_name)
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_save to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)

    try:
        wing_rti.request_federation_save(f"{config.save_name}-DUP")
    except SaveInProgress as exc:
        save_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_save to raise SaveInProgress during save")

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
        wing_rti.request_federation_save(f"{config.save_name}-RESTORE-BLOCK")
    except RestoreInProgress as exc:
        restore_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_save to raise RestoreInProgress during restore")
    finally:
        try:
            leader_rti.abort_federation_restore()
            drain_callbacks_pair(leader_rti, wing_rti, loops=16)
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
        "not_joined": not_joined,
        "save_in_progress": save_in_progress,
        "restore_in_progress": restore_in_progress,
    }


def run_save_failure_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_not_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_not_saved = wait_for_callback(leader_rti, leader_federate, "federationNotSaved", loops=120)
    wing_not_saved = wait_for_callback(wing_rti, wing_federate, "federationNotSaved", loops=120)
    assert leader_not_saved is not None
    assert wing_not_saved is not None
    assert leader_not_saved.args == (SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,)
    assert wing_not_saved.args == (SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,)

    status_count = len(leader_federate.callbacks_named("federationSaveStatusResponse")) + 1
    leader_rti.query_federation_save_status()
    status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationSaveStatusResponse",
        status_count,
        loops=120,
    )
    save_status_cleared = status_records[-1]
    cleared = _save_statuses(save_status_cleared)
    assert cleared[leader_handle] is SaveStatus.NO_SAVE_IN_PROGRESS
    assert cleared[wing_handle] is SaveStatus.NO_SAVE_IN_PROGRESS

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "leader_not_saved": leader_not_saved,
        "wing_not_saved": wing_not_saved,
        "save_status_cleared": save_status_cleared,
    }


def run_restore_request_failure_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    missing_save_name: str,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    leader_rti.request_federation_restore(missing_save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    restore_failed = wait_for_callback(leader_rti, leader_federate, "requestFederationRestoreFailed", loops=120)
    assert restore_failed is not None
    assert restore_failed.args == (missing_save_name,)
    assert wing_federate.last_callback("requestFederationRestoreFailed") is None

    status_count = len(leader_federate.callbacks_named("federationRestoreStatusResponse")) + 1
    leader_rti.query_federation_restore_status()
    status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationRestoreStatusResponse",
        status_count,
        loops=120,
    )
    restore_status_cleared = status_records[-1]
    cleared = _restore_statuses(restore_status_cleared)
    assert cleared[leader_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert cleared[wing_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "restore_failed": restore_failed,
        "restore_status_cleared": restore_status_cleared,
    }


def run_restore_failure_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    restore_succeeded = wait_for_callback(leader_rti, leader_federate, "requestFederationRestoreSucceeded", loops=120)
    leader_restore_begun = wait_for_callback(leader_rti, leader_federate, "federationRestoreBegun", loops=120)
    wing_initiate_restore = wait_for_callback(wing_rti, wing_federate, "initiateFederateRestore", loops=120)
    assert restore_succeeded is not None
    assert leader_restore_begun is not None
    assert wing_initiate_restore is not None

    leader_rti.federate_restore_complete()
    wing_rti.federate_restore_not_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_not_restored = wait_for_callback(leader_rti, leader_federate, "federationNotRestored", loops=120)
    wing_not_restored = wait_for_callback(wing_rti, wing_federate, "federationNotRestored", loops=120)
    assert leader_not_restored is not None
    assert wing_not_restored is not None
    assert leader_not_restored.args == (RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,)
    assert wing_not_restored.args == (RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,)

    status_count = len(leader_federate.callbacks_named("federationRestoreStatusResponse")) + 1
    leader_rti.query_federation_restore_status()
    status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationRestoreStatusResponse",
        status_count,
        loops=120,
    )
    restore_status_cleared = status_records[-1]
    cleared = _restore_statuses(restore_status_cleared)
    assert cleared[leader_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert cleared[wing_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "restore_succeeded": restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
        "wing_initiate_restore": wing_initiate_restore,
        "leader_not_restored": leader_not_restored,
        "wing_not_restored": wing_not_restored,
        "restore_status_cleared": restore_status_cleared,
    }


def run_save_abort_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wing_initiate_save = wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    assert leader_initiate_save is not None
    assert wing_initiate_save is not None

    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.abort_federation_save()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_not_saved = wait_for_callback(leader_rti, leader_federate, "federationNotSaved", loops=120)
    wing_not_saved = wait_for_callback(wing_rti, wing_federate, "federationNotSaved", loops=120)
    assert leader_not_saved is not None
    assert wing_not_saved is not None
    assert leader_not_saved.args == (SaveFailureReason.SAVE_ABORTED,)
    assert wing_not_saved.args == (SaveFailureReason.SAVE_ABORTED,)

    status_count = len(leader_federate.callbacks_named("federationSaveStatusResponse")) + 1
    leader_rti.query_federation_save_status()
    status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationSaveStatusResponse",
        status_count,
        loops=120,
    )
    save_status_cleared = status_records[-1]
    cleared = _save_statuses(save_status_cleared)
    assert cleared[leader_handle] is SaveStatus.NO_SAVE_IN_PROGRESS
    assert cleared[wing_handle] is SaveStatus.NO_SAVE_IN_PROGRESS

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_initiate_save": leader_initiate_save,
        "wing_initiate_save": wing_initiate_save,
        "leader_not_saved": leader_not_saved,
        "wing_not_saved": wing_not_saved,
        "save_status_cleared": save_status_cleared,
    }


def run_restore_abort_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_handle, wing_handle = _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)

    leader_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    restore_succeeded = wait_for_callback(leader_rti, leader_federate, "requestFederationRestoreSucceeded", loops=120)
    leader_restore_begun = wait_for_callback(leader_rti, leader_federate, "federationRestoreBegun", loops=120)
    wing_initiate_restore = wait_for_callback(wing_rti, wing_federate, "initiateFederateRestore", loops=120)
    assert restore_succeeded is not None
    assert leader_restore_begun is not None
    assert wing_initiate_restore is not None

    leader_rti.abort_federation_restore()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    leader_not_restored = wait_for_callback(leader_rti, leader_federate, "federationNotRestored", loops=120)
    wing_not_restored = wait_for_callback(wing_rti, wing_federate, "federationNotRestored", loops=120)
    assert leader_not_restored is not None
    assert wing_not_restored is not None
    assert leader_not_restored.args == (RestoreFailureReason.RESTORE_ABORTED,)
    assert wing_not_restored.args == (RestoreFailureReason.RESTORE_ABORTED,)

    status_count = len(leader_federate.callbacks_named("federationRestoreStatusResponse")) + 1
    leader_rti.query_federation_restore_status()
    status_records = wait_for_callback_count(
        leader_rti,
        leader_federate,
        "federationRestoreStatusResponse",
        status_count,
        loops=120,
    )
    restore_status_cleared = status_records[-1]
    cleared = _restore_statuses(restore_status_cleared)
    assert cleared[leader_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert cleared[wing_handle] is RestoreStatus.NO_RESTORE_IN_PROGRESS

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "restore_succeeded": restore_succeeded,
        "leader_restore_begun": leader_restore_begun,
        "wing_initiate_restore": wing_initiate_restore,
        "leader_not_restored": leader_not_restored,
        "wing_not_restored": wing_not_restored,
        "restore_status_cleared": restore_status_cleared,
    }


def run_restore_abort_exception_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.abort_federation_restore()
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected abort_federation_restore to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.abort_federation_restore()
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected abort_federation_restore to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)
    leader_rti.federate_save_begun()
    wing_rti.federate_save_begun()
    leader_rti.federate_save_complete()
    wing_rti.federate_save_complete()
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)

    try:
        leader_rti.abort_federation_restore()
    except RestoreNotInProgress as exc:
        restore_not_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected abort_federation_restore to raise RestoreNotInProgress before restore starts")
    finally:
        leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
        wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
        leader_rti.destroy_federation_execution(config.federation_name)
        wing_rti.disconnect()
        leader_rti.disconnect()

    return {
        "not_connected": not_connected,
        "not_joined": not_joined,
        "restore_not_in_progress": restore_not_in_progress,
    }


def run_save_status_exception_scenario(
    rti: Any,
    *,
    federate: Any,
) -> dict[str, Any]:
    try:
        rti.query_federation_save_status()
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected query_federation_save_status to raise NotConnected before connect")

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    try:
        rti.query_federation_save_status()
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected query_federation_save_status to raise FederateNotExecutionMember before join")
    finally:
        rti.disconnect()

    return {
        "not_connected": not_connected,
        "not_joined": not_joined,
    }


def run_restore_status_exception_scenario(
    rti: Any,
    *,
    federate: Any,
) -> dict[str, Any]:
    try:
        rti.query_federation_restore_status()
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected query_federation_restore_status to raise NotConnected before connect")

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    try:
        rti.query_federation_restore_status()
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected query_federation_restore_status to raise FederateNotExecutionMember before join")
    finally:
        rti.disconnect()

    return {
        "not_connected": not_connected,
        "not_joined": not_joined,
    }


def run_restore_request_precondition_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.request_federation_restore(config.save_name)
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_restore to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.request_federation_restore(config.save_name)
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_restore to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
    wait_for_callback(wing_rti, wing_federate, "initiateFederateSave", loops=120)

    try:
        wing_rti.request_federation_restore(config.save_name)
    except SaveInProgress as exc:
        save_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_restore to raise SaveInProgress during save")

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
        wing_rti.request_federation_restore(config.save_name)
    except RestoreInProgress as exc:
        restore_in_progress = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected request_federation_restore to raise RestoreInProgress during restore")
    finally:
        try:
            leader_rti.abort_federation_restore()
            drain_callbacks_pair(leader_rti, wing_rti, loops=16)
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
        "not_joined": not_joined,
        "save_in_progress": save_in_progress,
        "restore_in_progress": restore_in_progress,
    }


def run_save_participant_exception_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.federate_save_begun()
    except NotConnected as exc:
        begun_not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_begun to raise NotConnected before connect")

    try:
        leader_rti.federate_save_complete()
    except NotConnected as exc:
        complete_not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_complete to raise NotConnected before connect")

    try:
        leader_rti.federate_save_not_complete()
    except NotConnected as exc:
        not_complete_not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_not_complete to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.federate_save_begun()
    except FederateNotExecutionMember as exc:
        begun_not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_begun to raise FederateNotExecutionMember before join")

    try:
        leader_rti.federate_save_complete()
    except FederateNotExecutionMember as exc:
        complete_not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_complete to raise FederateNotExecutionMember before join")

    try:
        leader_rti.federate_save_not_complete()
    except FederateNotExecutionMember as exc:
        not_complete_not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_not_complete to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    try:
        leader_rti.federate_save_begun()
    except SaveNotInitiated as exc:
        begun_not_initiated = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_begun to raise SaveNotInitiated without an active save")

    try:
        leader_rti.federate_save_complete()
    except SaveNotInitiated as exc:
        complete_not_initiated = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_complete to raise SaveNotInitiated without an active save")

    try:
        leader_rti.federate_save_not_complete()
    except SaveNotInitiated as exc:
        not_complete_not_initiated = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_save_not_complete to raise SaveNotInitiated without an active save")
    finally:
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
        "begun_not_connected": begun_not_connected,
        "complete_not_connected": complete_not_connected,
        "not_complete_not_connected": not_complete_not_connected,
        "begun_not_joined": begun_not_joined,
        "complete_not_joined": complete_not_joined,
        "not_complete_not_joined": not_complete_not_joined,
        "begun_not_initiated": begun_not_initiated,
        "complete_not_initiated": complete_not_initiated,
        "not_complete_not_initiated": not_complete_not_initiated,
    }


def run_abort_save_exception_scenario(
    leader_rti: Any,
    *,
    federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.abort_federation_save()
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected abort_federation_save to raise NotConnected before connect")

    leader_rti.connect(federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.abort_federation_save()
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected abort_federation_save to raise FederateNotExecutionMember before join")
    finally:
        leader_rti.disconnect()

    return {
        "not_connected": not_connected,
        "not_joined": not_joined,
    }


def run_restore_participant_exception_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.federate_restore_complete()
    except NotConnected as exc:
        complete_not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_complete to raise NotConnected before connect")

    try:
        leader_rti.federate_restore_not_complete()
    except NotConnected as exc:
        not_complete_not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_not_complete to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.federate_restore_complete()
    except FederateNotExecutionMember as exc:
        complete_not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_complete to raise FederateNotExecutionMember before join")

    try:
        leader_rti.federate_restore_not_complete()
    except FederateNotExecutionMember as exc:
        not_complete_not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_not_complete to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    try:
        leader_rti.federate_restore_complete()
    except RestoreNotRequested as exc:
        complete_not_requested = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_complete to raise RestoreNotRequested without an active restore")

    try:
        leader_rti.federate_restore_not_complete()
    except RestoreNotRequested as exc:
        not_complete_not_requested = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected federate_restore_not_complete to raise RestoreNotRequested without an active restore")
    finally:
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
        "complete_not_connected": complete_not_connected,
        "not_complete_not_connected": not_complete_not_connected,
        "complete_not_joined": complete_not_joined,
        "not_complete_not_joined": not_complete_not_joined,
        "complete_not_requested": complete_not_requested,
        "not_complete_not_requested": not_complete_not_requested,
    }


def run_resigned_federate_callback_silence_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SaveRestoreScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    _connect_pair(
        leader_rti,
        wing_rti,
        config=config,
        leader_federate=leader_federate,
        wing_federate=wing_federate,
    )

    try:
        wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
        resigned_record_count = len(wing_federate.records)

        leader_rti.request_federation_save(config.save_name)
        drain_callbacks_pair(leader_rti, wing_rti, loops=16)
        leader_initiate_save = wait_for_callback(leader_rti, leader_federate, "initiateFederateSave", loops=120)
        assert leader_initiate_save is not None
        assert leader_initiate_save.args == (config.save_name,)

        leader_rti.federate_save_begun()
        leader_rti.federate_save_complete()
        drain_callbacks_pair(leader_rti, wing_rti, loops=16)
        leader_saved = wait_for_callback(leader_rti, leader_federate, "federationSaved", loops=120)
        assert leader_saved is not None

        post_resign_records = wing_federate.records[resigned_record_count:]
        assert not post_resign_records
        assert wing_federate.last_callback("initiateFederateSave") is None
        assert wing_federate.last_callback("federationSaved") is None
        return {
            "leader_initiate_save": leader_initiate_save,
            "leader_saved": leader_saved,
            "wing_record_count_before": resigned_record_count,
            "wing_record_count_after": len(wing_federate.records),
            "wing_post_resign_records": post_resign_records,
        }
    finally:
        try:
            leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
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


__all__ = [
    "SaveRestoreScenarioConfig",
    "run_abort_save_exception_scenario",
    "run_restore_callback_policy_scenario",
    "run_restore_request_precondition_scenario",
    "run_restore_participant_exception_scenario",
    "run_restore_federate_local_state_scenario",
    "run_restore_object_state_scenario",
    "run_restore_round_trip_scenario",
    "run_save_restore_queued_callback_scenario",
    "run_save_participant_exception_scenario",
    "run_save_request_precondition_scenario",
    "run_resigned_federate_callback_silence_scenario",
    "run_restore_abort_exception_scenario",
    "run_restore_status_exception_scenario",
    "run_restore_abort_scenario",
    "run_restore_failure_scenario",
    "run_restore_request_failure_scenario",
    "run_scheduled_save_restore_time_state_scenario",
    "run_save_abort_scenario",
    "run_save_failure_scenario",
    "run_save_status_exception_scenario",
    "run_save_restore_scenario",
    "run_restore_transient_state_scenario",
]
