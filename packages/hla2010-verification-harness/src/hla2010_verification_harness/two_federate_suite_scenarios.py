"""Generic scenario bodies used by the two-federate suite coordinator."""
from __future__ import annotations

from collections.abc import Mapping as CollectionsMapping
from typing import Any, Mapping

from hla2010.enums import CallbackModel
from hla2010.time import HLAfloat64Interval

from .two_federate_suite_pairs import SuiteRecordingFederateAmbassador
from .scenario_support import wait_for_callback, wait_for_callback_count_pair
from .two_federate_suite_summary import _jsonable


def _evoke_pair(left_rti: Any, right_rti: Any, *, rounds: int = 1) -> None:
    for _ in range(rounds):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)


def _wait_for_callback(
    left_rti: Any,
    right_rti: Any,
    left_federate: SuiteRecordingFederateAmbassador,
    right_federate: SuiteRecordingFederateAmbassador,
    callback_name: str,
    *,
    rounds: int = 32,
) -> None:
    for _ in range(rounds):
        _evoke_pair(left_rti, right_rti)
        if left_federate.last_callback(callback_name) is not None and right_federate.last_callback(callback_name) is not None:
            return
    raise AssertionError(f"Timed out waiting for callback {callback_name!r}")


def _decode_handle_value_map(rti: Any, interaction: Any, payload: Any) -> Any:
    if not isinstance(payload, CollectionsMapping):
        return _jsonable(payload)

    decoded: dict[str, Any] = {}
    for handle, value in payload.items():
        try:
            key = str(rti.get_parameter_name(interaction, handle))
        except Exception:
            key = str(_jsonable(handle))
        if isinstance(value, bytes):
            try:
                decoded[key] = value.decode("utf-8")
            except UnicodeDecodeError:
                decoded[key] = value.hex()
        else:
            decoded[key] = _jsonable(value)
    return decoded


def decode_handle_value_map(rti: Any, interaction: Any, payload: Any) -> Any:
    return _decode_handle_value_map(rti, interaction, payload)


def run_suite_save_restore_scenario(
    left_rti: Any,
    right_rti: Any,
    *,
    config: Mapping[str, Any],
    left_federate: SuiteRecordingFederateAmbassador,
    right_federate: SuiteRecordingFederateAmbassador,
) -> dict[str, Any]:
    save_name = config["save_name"]
    resume_time = config["resume_time"]
    federation_name = config["federation_name"]

    left_rti.connect(left_federate, CallbackModel.HLA_EVOKED)
    right_rti.connect(right_federate, CallbackModel.HLA_EVOKED)
    left_rti.create_federation_execution(
        federation_name,
        list(config["fom_modules"]),
        config["logical_time_implementation_name"],
    )
    left_rti.join_federation_execution("left", "save-restore", federation_name)
    right_rti.join_federation_execution("right", "save-restore", federation_name)
    left_rti.enable_time_constrained()
    right_rti.enable_time_constrained()
    left_rti.enable_time_regulation(HLAfloat64Interval(1.0))
    right_rti.enable_time_regulation(HLAfloat64Interval(1.0))
    _evoke_pair(left_rti, right_rti, rounds=16)

    left_rti.request_federation_save(save_name)
    _wait_for_callback(left_rti, right_rti, left_federate, right_federate, "initiateFederateSave")

    left_rti.federate_save_begun()
    right_rti.federate_save_begun()
    left_rti.federate_save_complete()
    right_rti.federate_save_complete()
    _wait_for_callback(left_rti, right_rti, left_federate, right_federate, "federationSaved")

    left_rti.time_advance_request_available(resume_time)
    right_rti.time_advance_request_available(resume_time)
    _evoke_pair(left_rti, right_rti, rounds=16)

    left_rti.request_federation_restore(save_name)
    _wait_for_callback(left_rti, right_rti, left_federate, right_federate, "initiateFederateRestore")
    left_rti.federate_restore_complete()
    right_rti.federate_restore_complete()
    _wait_for_callback(left_rti, right_rti, left_federate, right_federate, "federationRestored")

    return {
        "left_callbacks": _jsonable(left_federate.records),
        "right_callbacks": _jsonable(right_federate.records),
        "federation_saved": bool(left_federate.last_callback("federationSaved")),
        "restore_completed": bool(left_federate.last_callback("federationRestored")),
        "left_time": _jsonable(left_rti.query_logical_time()),
        "right_time": _jsonable(right_rti.query_logical_time()),
    }


def run_suite_ddm_scenario(
    sender_rti: Any,
    receiver_rti: Any,
    *,
    config: Mapping[str, Any],
    sender_federate: SuiteRecordingFederateAmbassador,
    receiver_federate: SuiteRecordingFederateAmbassador,
) -> dict[str, Any]:
    federation_name = config["federation_name"]
    sender_rti.connect(sender_federate, CallbackModel.HLA_EVOKED)
    receiver_rti.connect(receiver_federate, CallbackModel.HLA_EVOKED)
    sender_rti.create_federation_execution(
        federation_name,
        list(config["fom_modules"]),
        config["logical_time_implementation_name"],
    )
    sender_rti.join_federation_execution("sender", "ddm", federation_name)
    receiver_rti.join_federation_execution("receiver", "ddm", federation_name)

    sender_rti.enable_time_regulation(config.get("lookahead", HLAfloat64Interval(1.0)))
    receiver_rti.enable_time_constrained()
    time_regulation = wait_for_callback(
        sender_rti,
        sender_federate,
        "timeRegulationEnabled",
        loops=120,
    )
    time_constrained = wait_for_callback(
        receiver_rti,
        receiver_federate,
        "timeConstrainedEnabled",
        loops=120,
    )
    assert time_regulation is not None
    assert time_constrained is not None

    sender_dimension = sender_rti.get_dimension_handle("HLAdefaultRoutingSpace")
    receiver_dimension = receiver_rti.get_dimension_handle("HLAdefaultRoutingSpace")
    source_near = sender_rti.create_region({sender_dimension})
    source_far = sender_rti.create_region({sender_dimension})
    target_region = receiver_rti.create_region({receiver_dimension})
    sender_rti.set_range_bounds(source_near, sender_dimension, config["source_near"])
    sender_rti.set_range_bounds(source_far, sender_dimension, config["source_far"])
    receiver_rti.set_range_bounds(target_region, receiver_dimension, config["target_bounds"])
    sender_rti.commit_region_modifications({source_near, source_far})
    receiver_rti.commit_region_modifications({target_region})

    sender_interaction = sender_rti.get_interaction_class_handle(config["interaction_class_name"])
    receiver_interaction = receiver_rti.get_interaction_class_handle(config["interaction_class_name"])
    parameter = sender_rti.get_parameter_handle(sender_interaction, config["parameter_name"])
    sender_rti.publish_interaction_class(sender_interaction)
    receiver_rti.subscribe_interaction_class_with_regions(receiver_interaction, {target_region})
    _evoke_pair(sender_rti, receiver_rti, rounds=16)

    received_baseline = len(receiver_federate.callbacks_named("receiveInteraction"))
    sender_rti.send_interaction_with_regions(
        sender_interaction,
        {parameter: config["far_payload"]},
        {source_far},
        config["far_tag"],
        config["far_time"],
    )
    sender_rti.send_interaction_with_regions(
        sender_interaction,
        {parameter: config["near_payload"]},
        {source_near},
        config["near_tag"],
        config["near_time"],
    )
    _evoke_pair(sender_rti, receiver_rti, rounds=16)
    sender_rti.time_advance_request(config["grant_time"])
    receiver_rti.next_message_request_available(config["next_request_time"])
    received_records = wait_for_callback_count_pair(
        sender_rti,
        receiver_rti,
        receiver_federate,
        "receiveInteraction",
        received_baseline + 1,
        loops=120,
    )

    received = received_records[received_baseline:]
    return {
        "time_regulation": _jsonable(time_regulation),
        "time_constrained": _jsonable(time_constrained),
        "sender_dimension": _jsonable(sender_dimension),
        "receiver_dimension": _jsonable(receiver_dimension),
        "source_near": _jsonable(source_near),
        "source_far": _jsonable(source_far),
        "target_region": _jsonable(target_region),
        "sender_interaction": _jsonable(sender_interaction),
        "receiver_interaction": _jsonable(receiver_interaction),
        "parameter": _jsonable(parameter),
        "receiver_callbacks": _jsonable(receiver_federate.records),
        "received_callbacks": _jsonable(received),
        "received_count": len(received),
        "received_payload": _decode_handle_value_map(receiver_rti, receiver_interaction, received[-1].args[1]) if received else None,
        "received_time": _jsonable(received[-1].args[5]) if received else None,
    }


__all__ = [
    "decode_handle_value_map",
    "run_suite_ddm_scenario",
    "run_suite_save_restore_scenario",
]
