"""Scenario-specific helpers used by the two-federate suite runner."""
from __future__ import annotations

from typing import Any, Mapping

from ..enums import CallbackModel
from ..time import HLAfloat64Interval
from .two_federate_suite_summary import _jsonable
from .two_federate_suite_pairs import SuiteRecordingFederateAmbassador


def run_suite_save_restore_scenario(
    left_rti: Any,
    right_rti: Any,
    *,
    config: Mapping[str, Any],
    left_federate: SuiteRecordingFederateAmbassador,
    right_federate: SuiteRecordingFederateAmbassador,
) -> dict[str, Any]:
    save_name = config["save_name"]
    save_time = config["save_time"]
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
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)

    left_rti.request_federation_save(save_name, save_time)
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)
    left_rti.time_advance_request_available(save_time)
    right_rti.time_advance_request_available(save_time)
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)

    left_rti.federate_save_begun()
    right_rti.federate_save_begun()
    left_rti.federate_save_complete()
    right_rti.federate_save_complete()
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)

    left_rti.time_advance_request_available(resume_time)
    right_rti.time_advance_request_available(resume_time)
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)

    left_rti.request_federation_restore(save_name)
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)
    left_rti.federate_restore_complete()
    right_rti.federate_restore_complete()
    for _ in range(16):
        left_rti.evoke_multiple_callbacks(0.0, 0.1)
        right_rti.evoke_multiple_callbacks(0.0, 0.1)

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

    sender_rti.enable_time_regulation(HLAfloat64Interval(1.0))
    receiver_rti.enable_time_constrained()
    for _ in range(16):
        sender_rti.evoke_multiple_callbacks(0.0, 0.1)
        receiver_rti.evoke_multiple_callbacks(0.0, 0.1)

    dimension = sender_rti.get_dimension_handle("HLAdefaultRoutingSpace")
    source_near = sender_rti.create_region({dimension})
    source_far = sender_rti.create_region({dimension})
    target_region = receiver_rti.create_region({dimension})
    sender_rti.set_range_bounds(source_near, dimension, config["source_near"])
    sender_rti.set_range_bounds(source_far, dimension, config["source_far"])
    receiver_rti.set_range_bounds(target_region, dimension, config["target_bounds"])
    sender_rti.commit_region_modifications({source_near, source_far})
    receiver_rti.commit_region_modifications({target_region})

    interaction = sender_rti.get_interaction_class_handle(config["interaction_class_name"])
    parameter = sender_rti.get_parameter_handle(interaction, config["parameter_name"])
    sender_rti.publish_interaction_class(interaction)
    receiver_rti.subscribe_interaction_class_with_regions(interaction, {target_region})
    sender_rti.send_interaction_with_regions(
        interaction,
        {parameter: config["far_payload"]},
        {source_far},
        config["far_tag"],
        config["far_time"],
    )
    sender_rti.send_interaction_with_regions(
        interaction,
        {parameter: config["near_payload"]},
        {source_near},
        config["near_tag"],
        config["near_time"],
    )
    for _ in range(16):
        sender_rti.evoke_multiple_callbacks(0.0, 0.1)
        receiver_rti.evoke_multiple_callbacks(0.0, 0.1)
    sender_rti.time_advance_request(config["grant_time"])
    receiver_rti.next_message_request_available(config["next_request_time"])
    for _ in range(24):
        sender_rti.evoke_multiple_callbacks(0.0, 0.1)
        receiver_rti.evoke_multiple_callbacks(0.0, 0.1)

    received = receiver_federate.callbacks_named("receiveInteraction")
    return {
        "dimension": _jsonable(dimension),
        "source_near": _jsonable(source_near),
        "source_far": _jsonable(source_far),
        "target_region": _jsonable(target_region),
        "interaction": _jsonable(interaction),
        "parameter": _jsonable(parameter),
        "receiver_callbacks": _jsonable(receiver_federate.records),
        "received_callbacks": _jsonable(received),
        "received_count": len(received),
        "received_payload": _jsonable(received[-1].args[2]) if received else None,
        "received_time": _jsonable(received[-1].args[5]) if received else None,
    }
