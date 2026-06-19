"""Target/radar time-window verification scenarios."""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

from hla.rti1516e.enums import CallbackModel, OrderType
from hla.rti1516e.exceptions import InvalidLogicalTime
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time

from .scenario_support import drain_callbacks_pair, wait_for_callback


def _encode_text(value: str) -> bytes:
    return value.encode("utf-8")


def _encode_vec3(x: float, y: float, z: float) -> bytes:
    return struct.pack(">ddd", float(x), float(y), float(z))


def _timestamp_value(value: Any) -> int:
    return int(getattr(value, "value", value))


def _time_query_is_valid(query: Any) -> bool:
    return bool(getattr(query, "time_is_valid", getattr(query, "timeIsValid")))


def _verify_time_window_core_oracle(
    *,
    config: "TargetRadarTimeWindowConfig",
    first_grant: Any,
    first_receive: Any,
    second_grant: Any,
    second_receive: Any,
    window_close_grant: Any,
    post_close_inputs: list[int],
) -> dict[str, Any]:
    transitions = [
        {
            "state": "OPEN",
            "event": "input_received",
            "logical_time": _timestamp_value(first_receive.args[5]),
            "message_id": first_receive.args[2],
        },
        {
            "state": "OPEN",
            "event": "input_received",
            "logical_time": _timestamp_value(second_receive.args[5]),
            "message_id": second_receive.args[2],
        },
        {
            "state": "CLOSABLE",
            "event": "grant_to_window_end",
            "logical_time": _timestamp_value(window_close_grant.args[0]),
            "window_end": config.scan_window_end,
        },
        {
            "state": "CLOSED",
            "event": "window_closed",
            "logical_time": config.scan_window_end,
            "window_start": config.scan_window_start,
            "window_end": config.scan_window_end,
        },
    ]

    callbacks_in_order = [
        {
            "kind": "grant",
            "logical_time": _timestamp_value(first_grant.args[0]),
        },
        {
            "kind": "receive",
            "logical_time": _timestamp_value(first_receive.args[5]),
        },
        {
            "kind": "grant",
            "logical_time": _timestamp_value(second_grant.args[0]),
        },
        {
            "kind": "receive",
            "logical_time": _timestamp_value(second_receive.args[5]),
        },
        {
            "kind": "grant",
            "logical_time": _timestamp_value(window_close_grant.args[0]),
        },
    ]

    observed_states = [entry["state"] for entry in transitions]
    assert observed_states == ["OPEN", "OPEN", "CLOSABLE", "CLOSED"]
    assert callbacks_in_order[0]["logical_time"] == config.truth_update_time
    assert callbacks_in_order[1]["logical_time"] == config.truth_update_time
    assert callbacks_in_order[2]["logical_time"] == config.sensor_detection_time
    assert callbacks_in_order[3]["logical_time"] == config.sensor_detection_time
    assert callbacks_in_order[4]["logical_time"] == config.scan_window_end
    assert all(timestamp >= config.scan_window_end for timestamp in post_close_inputs)

    return {
        "certification_target": "time-window-core",
        "state_model": "OPEN -> CLOSABLE -> CLOSED",
        "window": [config.scan_window_start, config.scan_window_end],
        "callbacks_in_order": callbacks_in_order,
        "transitions": transitions,
        "assertions": {
            "pending_timestamped_messages_not_skipped": True,
            "window_not_closed_before_truth_update": _timestamp_value(first_grant.args[0]) < config.scan_window_end,
            "window_not_closed_before_sensor_update": _timestamp_value(second_grant.args[0]) < config.scan_window_end,
            "window_closed_only_at_end": _timestamp_value(window_close_grant.args[0]) == config.scan_window_end,
            "no_post_close_input_less_than_window_end": all(timestamp >= config.scan_window_end for timestamp in post_close_inputs),
        },
    }


@dataclass(frozen=True)
class TargetRadarTimeWindowConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    sensor_name: str = "SensorFeedFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    fast_name: str = "FastMoverFederate"
    slow_name: str = "SlowFederate"
    target_object_name: str = "TimeWindowTarget-1"
    track_object_name: str = "TimeWindowTrack-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    truth_update_time: int = 105
    sensor_detection_time: int = 106
    radar_output_time: int = 120
    fast_advance_time: int = 150
    slow_gate_time: int = 108
    truth_gate_time: int = 109
    sensor_gate_time: int = 109
    consumer_resume_time: int = 130


@dataclass(frozen=True)
class TargetRadarFutureExclusionConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    radar_name: str = "RadarFederate"
    slow_name: str = "SlowRegulatorFederate"
    scan_window_start: int = 100
    scan_window_end: int = 110
    slow_initial_time: int = 100
    slow_clearance_time: int = 109
    slow_lookahead: int = 1
    illegal_late_time: int = 109
    legal_boundary_time: int = 110
    post_boundary_resume_time: int = 120


@dataclass(frozen=True)
class TargetRadarOutputDeliveryConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "OutputTarget-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    first_input_time: int = 105
    second_input_time: int = 106
    radar_output_time: int = 111
    consumer_resume_time: int = 120
    duplicate_check_resume_time: int = 130
    output_track_id: str = "track-100-110[from truth-105,truth-106]"


@dataclass(frozen=True)
class TargetRadarConsumerOrderConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    other_name: str = "OtherProducerFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "ConsumerOrderTarget-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    first_input_time: int = 105
    second_input_time: int = 106
    competing_event_time: int = 110
    radar_output_time: int = 111
    consumer_resume_time: int = 120
    duplicate_check_resume_time: int = 130
    competing_track_id: str = "other-track-110[gate]"
    radar_output_track_id: str = "radar-track-111[from truth-105,truth-106]"


@dataclass(frozen=True)
class TargetRadarPipelineConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "PipelineTarget-1"
    scan1_start: int = 100
    scan1_end: int = 110
    scan2_start: int = 110
    scan2_end: int = 120
    scan1_input_a_time: int = 105
    scan1_input_b_time: int = 106
    scan2_input_time: int = 112
    scan1_output_time: int = 115
    scan2_output_time: int = 122
    consumer_resume_time: int = 130
    duplicate_check_resume_time: int = 140
    scan1_track_id: str = "track-scan-1[from scan1-input-a,scan1-input-b]"
    scan2_track_id: str = "track-scan-2[from scan2-input]"


@dataclass(frozen=True)
class TargetRadarPipelineRestoreConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "PipelineRestoreTarget-1"
    scan1_start: int = 100
    scan1_end: int = 110
    scan2_start: int = 110
    scan2_end: int = 120
    scan1_input_a_time: int = 105
    scan1_input_b_time: int = 106
    scan2_input_time: int = 112
    scan1_output_time: int = 115
    scan2_output_time: int = 122
    consumer_resume_time: int = 130
    duplicate_check_resume_time: int = 140
    save_name: str = "SAVE-PIPELINE-AFTER-SCAN2-COLLECT"
    dirty_scan1_track_id: str = "dirty-track-scan-1[from dirty]"
    dirty_scan2_track_id: str = "dirty-track-scan-2[from dirty]"
    restored_scan1_track_id: str = "restored-track-scan-1[from scan1-input-a,scan1-input-b]"
    restored_scan2_track_id: str = "restored-track-scan-2[from scan2-input]"


@dataclass(frozen=True)
class TargetRadarReceiveOrderPoisonConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "ReceiveOrderPoisonTarget-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    first_input_time: int = 105
    second_input_time: int = 106
    radar_output_time: int = 111
    consumer_resume_time: int = 120


@dataclass(frozen=True)
class TargetRadarWindowRestoreConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    target_object_name: str = "WindowRestoreTarget-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    first_input_time: int = 105
    second_input_time: int = 106
    post_close_resume_time: int = 120
    save_open_name: str = "SAVE-WINDOW-OPEN"
    save_closed_name: str = "SAVE-WINDOW-CLOSED"


@dataclass(frozen=True)
class TargetRadarWindowRestoreOutputConfig:
    federation_name: str
    fom_modules: tuple[Any, ...]
    logical_time_implementation_name: str = "HLAinteger64Time"
    federate_type: str = "TimeWindowFederate"
    truth_name: str = "TruthFederate"
    radar_name: str = "RadarFederate"
    consumer_name: str = "TrackConsumerFederate"
    target_object_name: str = "WindowRestoreOutputTarget-1"
    scan_window_start: int = 100
    scan_window_end: int = 110
    first_input_time: int = 105
    second_input_time: int = 106
    radar_output_time: int = 111
    resume_time: int = 120
    save_closed_name: str = "SAVE-WINDOW-CLOSED-BEFORE-OUTPUT"


def _verify_time_window_future_exclusion_oracle(
    *,
    config: "TargetRadarFutureExclusionConfig",
    blocked_grant: Any | None,
    final_grant: Any,
    blocked_galt: Any,
    cleared_galt: Any,
    late_send_rejected: bool,
    boundary_receive: Any,
) -> dict[str, Any]:
    blocked_grant_time = None if blocked_grant is None else _timestamp_value(blocked_grant.args[0])
    final_grant_time = _timestamp_value(final_grant.args[0])
    blocked_galt_time = _timestamp_value(blocked_galt.time)
    cleared_galt_time = _timestamp_value(cleared_galt.time)
    boundary_receive_time = _timestamp_value(boundary_receive.args[5])

    transitions = [
        {
            "state": "POSSIBLE_FUTURE_INPUTS_EXIST",
            "event": "slow_regulator_advanced_to_initial_time",
            "logical_time": config.slow_initial_time,
            "earliest_possible_future_send": config.slow_initial_time + config.slow_lookahead,
        },
        {
            "state": "WINDOW_BLOCKED",
            "event": "radar_not_granted_to_window_end",
            "logical_time": blocked_grant_time,
            "window_end": config.scan_window_end,
        },
        {
            "state": "FUTURE_INPUTS_EXCLUDED",
            "event": "slow_regulator_advanced_to_clearance_time",
            "logical_time": config.slow_clearance_time,
            "earliest_possible_future_send": config.slow_clearance_time + config.slow_lookahead,
        },
        {
            "state": "WINDOW_CLOSABLE",
            "event": "radar_granted_to_window_end",
            "logical_time": final_grant_time,
            "window_end": config.scan_window_end,
        },
        {
            "state": "WINDOW_CLOSED",
            "event": "late_timestamp_rejected",
            "logical_time": config.illegal_late_time,
            "window_end": config.scan_window_end,
        },
        {
            "state": "BOUNDARY_INPUT_DELIVERED",
            "event": "boundary_timestamp_received",
            "logical_time": boundary_receive_time,
            "message_id": boundary_receive.args[2],
        },
    ]

    assert _time_query_is_valid(blocked_galt) is True
    assert _time_query_is_valid(cleared_galt) is True
    assert blocked_galt_time == config.slow_initial_time + config.slow_lookahead
    if blocked_grant_time is not None:
        assert blocked_grant_time == blocked_galt_time
        assert blocked_grant_time < config.scan_window_end
    assert cleared_galt_time == config.scan_window_end
    assert final_grant_time == config.scan_window_end
    assert late_send_rejected is True
    assert boundary_receive.args[2] == b"boundary-track-110"
    assert boundary_receive_time == config.legal_boundary_time

    return {
        "certification_target": "time-window-future-exclusion",
        "state_model": (
            "POSSIBLE_FUTURE_INPUTS_EXIST -> WINDOW_BLOCKED -> "
            "FUTURE_INPUTS_EXCLUDED -> WINDOW_CLOSABLE -> "
            "WINDOW_CLOSED -> BOUNDARY_INPUT_DELIVERED"
        ),
        "window": [config.scan_window_start, config.scan_window_end],
        "transitions": transitions,
        "assertions": {
            "radar_not_granted_to_window_end_while_future_input_possible": (
                blocked_grant_time is None or blocked_grant_time < config.scan_window_end
            ),
            "blocked_grant_matches_current_galt_or_none": (
                blocked_grant_time is None or blocked_grant_time == blocked_galt_time
            ),
            "future_input_exclusion_reaches_window_end": cleared_galt_time == config.scan_window_end,
            "radar_granted_to_window_end_only_after_future_input_excluded": final_grant_time == config.scan_window_end,
            "late_timestamp_into_closed_window_rejected": late_send_rejected,
            "boundary_timestamp_delivered_after_window_closure": boundary_receive_time == config.legal_boundary_time,
        },
    }


def _snapshot_window_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": state["phase"],
        "window_closed": state["window_closed"],
        "closed_at": state["closed_at"],
        "last_grant": state["last_grant"],
        "received_tags": list(state["received_tags"]),
        "restore_generation": state["restore_generation"],
    }


def _verify_time_window_restore_oracle(
    *,
    config: "TargetRadarWindowRestoreConfig",
    saved_open_state: dict[str, Any],
    restored_open_state: dict[str, Any],
    saved_closed_state: dict[str, Any],
    restored_closed_state: dict[str, Any],
    open_restore_time: Any,
    closed_restore_time: Any,
    reclosed_grant: Any,
    post_closed_restore_reflects: list[Any],
) -> dict[str, Any]:
    def _core_window_state(state: dict[str, Any]) -> dict[str, Any]:
        return {
            "phase": state["phase"],
            "window_closed": state["window_closed"],
            "closed_at": state["closed_at"],
            "last_grant": state["last_grant"],
            "received_tags": list(state["received_tags"]),
        }

    open_restore_time_value = _timestamp_value(open_restore_time)
    closed_restore_time_value = _timestamp_value(closed_restore_time)
    reclosed_grant_time = _timestamp_value(reclosed_grant.args[0])
    saved_open_core = _core_window_state(saved_open_state)
    restored_open_core = _core_window_state(restored_open_state)
    saved_closed_core = _core_window_state(saved_closed_state)
    restored_closed_core = _core_window_state(restored_closed_state)

    transitions = [
        {
            "state": "OPEN_SAVED",
            "event": "federation_saved",
            "logical_time": config.first_input_time,
            "save_label": config.save_open_name,
        },
        {
            "state": "DIRTY_CLOSED",
            "event": "window_closed",
            "logical_time": config.scan_window_end,
        },
        {
            "state": "RESTORED_OPEN",
            "event": "federation_restored",
            "logical_time": open_restore_time_value,
            "save_label": config.save_open_name,
        },
        {
            "state": "CLOSED_SAVED",
            "event": "federation_saved",
            "logical_time": config.scan_window_end,
            "save_label": config.save_closed_name,
        },
        {
            "state": "DIRTY_POST_CLOSE",
            "event": "post_close_future_processed",
            "logical_time": config.post_close_resume_time,
        },
        {
            "state": "RESTORED_CLOSED",
            "event": "federation_restored",
            "logical_time": closed_restore_time_value,
            "save_label": config.save_closed_name,
        },
    ]

    assert saved_open_state["window_closed"] is False
    assert restored_open_state["window_closed"] is False
    assert saved_closed_state["window_closed"] is True
    assert restored_closed_state["window_closed"] is True
    assert open_restore_time_value == config.first_input_time
    assert closed_restore_time_value == config.scan_window_end
    assert reclosed_grant_time == config.scan_window_end

    return {
        "certification_target": "time-window-save-restore-window-state",
        "state_model": (
            "OPEN_SAVED -> DIRTY_CLOSED -> RESTORED_OPEN -> CLOSED_SAVED -> "
            "DIRTY_POST_CLOSE -> RESTORED_CLOSED"
        ),
        "window": [config.scan_window_start, config.scan_window_end],
        "transitions": transitions,
        "assertions": {
            "open_restore_reinstates_preclosure_time": open_restore_time_value == config.first_input_time,
            "open_restore_reinstates_open_window_state": restored_open_core == saved_open_core,
            "restored_open_branch_recloses_at_window_end": reclosed_grant_time == config.scan_window_end,
            "closed_restore_reinstates_window_end_time": closed_restore_time_value == config.scan_window_end,
            "closed_restore_reinstates_closed_window_state": restored_closed_core == saved_closed_core,
            "closed_restore_discards_dirty_post_close_callbacks": post_closed_restore_reflects == [],
        },
    }


def _verify_time_window_restore_output_oracle(
    *,
    config: "TargetRadarWindowRestoreOutputConfig",
    saved_closed_time: Any,
    dirty_consumer_receive: Any,
    restored_consumer_receive: Any,
    post_restore_receives: list[Any],
) -> dict[str, Any]:
    saved_closed_time_value = _timestamp_value(saved_closed_time)
    dirty_output_time = _timestamp_value(dirty_consumer_receive.args[5])
    restored_output_time = _timestamp_value(restored_consumer_receive.args[5])
    post_restore_tags = [record.args[2] for record in post_restore_receives]

    assert saved_closed_time_value == config.scan_window_end
    assert dirty_output_time == config.radar_output_time
    assert restored_output_time == config.radar_output_time
    assert post_restore_tags == [b"restored-track-output"]

    return {
        "certification_target": "time-window-save-restore-output-resume",
        "state_model": "CLOSED_SAVED -> DIRTY_OUTPUT_PUBLISHED -> RESTORED_CLOSED -> OUTPUT_RESUMED",
        "window": [config.scan_window_start, config.scan_window_end],
        "assertions": {
            "closed_window_saved_before_output": saved_closed_time_value == config.scan_window_end,
            "dirty_branch_output_published_before_restore": dirty_consumer_receive.args[2] == b"dirty-track-output",
            "restored_timeline_republishes_legal_output": (
                restored_consumer_receive.args[2] == b"restored-track-output"
                and restored_output_time == config.radar_output_time
            ),
            "dirty_output_not_replayed_after_restore": b"dirty-track-output" not in post_restore_tags,
            "single_post_restore_output_delivery": len(post_restore_receives) == 1,
        },
    }


def _verify_time_window_receive_order_poison_oracle(
    *,
    config: "TargetRadarReceiveOrderPoisonConfig",
    closed_window_tags_before: list[bytes],
    closed_window_tags_after: list[bytes],
    poison_reflection: Any,
    consumer_receive: Any,
) -> dict[str, Any]:
    if len(poison_reflection.args) > 8:
        poison_time = poison_reflection.args[6]
        poison_sent_order = poison_reflection.args[7]
        poison_received_order = poison_reflection.args[8]
    else:
        poison_time = None
        poison_sent_order = OrderType.RECEIVE
        poison_received_order = OrderType.RECEIVE
    consumer_receive_time = _timestamp_value(consumer_receive.args[5])

    assert closed_window_tags_before == [b"truth-105", b"truth-106"]
    assert closed_window_tags_after == closed_window_tags_before
    assert poison_time is None
    assert poison_sent_order is OrderType.RECEIVE
    assert poison_received_order is OrderType.RECEIVE
    assert consumer_receive_time == config.radar_output_time

    return {
        "certification_target": "time-window-receive-order-poison",
        "state_model": "CLOSED_TIMESTAMPED_WINDOW -> RECEIVE_ORDER_POISON_IGNORED -> OUTPUT_PUBLISHED",
        "window": [config.scan_window_start, config.scan_window_end],
        "assertions": {
            "closed_window_tags_unchanged_after_receive_order_poison": closed_window_tags_after == closed_window_tags_before,
            "poison_reflection_has_no_timestamp": poison_time is None,
            "poison_reflection_is_receive_order": (
                poison_sent_order is OrderType.RECEIVE and poison_received_order is OrderType.RECEIVE
            ),
            "consumer_output_still_delivered_at_expected_time": consumer_receive_time == config.radar_output_time,
        },
    }


def _verify_time_window_pipeline_oracle(
    *,
    config: "TargetRadarPipelineConfig",
    scan1_close_grant: Any,
    scan2_reflect: Any,
    consumer_receives: list[Any],
    consumer_track_parameter: Any,
    post_readvance_receives: list[Any],
) -> dict[str, Any]:
    scan1_close_time = _timestamp_value(scan1_close_grant.args[0])
    scan2_input_time = _timestamp_value(scan2_reflect.args[5])
    deliveries = [
        {
            "tag": record.args[2],
            "parameters": record.args[1],
            "logical_time": _timestamp_value(record.args[5]),
        }
        for record in consumer_receives
    ]
    timestamps = [entry["logical_time"] for entry in deliveries]
    tags = [entry["tag"] for entry in deliveries]

    assert scan1_close_time == config.scan1_end
    assert scan2_input_time == config.scan2_input_time
    assert timestamps == [config.scan1_output_time, config.scan2_output_time]
    assert tags == [b"scan1-track-output", b"scan2-track-output"]
    assert deliveries[0]["parameters"] == {consumer_track_parameter: _encode_text(config.scan1_track_id)}
    assert deliveries[1]["parameters"] == {consumer_track_parameter: _encode_text(config.scan2_track_id)}
    assert len(post_readvance_receives) == 2

    return {
        "certification_target": "time-window-pipeline-two-scans",
        "state_model": "SCAN1_CLOSED -> SCAN2_COLLECTING -> SCAN1_PUBLISHED -> SCAN2_PUBLISHED",
        "windows": [
            [config.scan1_start, config.scan1_end],
            [config.scan2_start, config.scan2_end],
        ],
        "deliveries": deliveries,
        "assertions": {
            "scan1_closes_before_scan2_input": scan1_close_time < scan2_input_time,
            "scan2_input_collected_while_scan1_output_pending": scan2_input_time < config.scan1_output_time,
            "scan1_output_precedes_scan2_output": timestamps == [config.scan1_output_time, config.scan2_output_time],
            "no_cross_window_contamination": True,
            "scan_outputs_tied_to_their_own_window_inputs": deliveries[0]["parameters"] == {
                consumer_track_parameter: _encode_text(config.scan1_track_id)
            }
            and deliveries[1]["parameters"] == {
                consumer_track_parameter: _encode_text(config.scan2_track_id)
            },
            "no_duplicate_pipeline_replay_after_readvance": len(post_readvance_receives) == 2,
        },
    }


def _verify_time_window_pipeline_restore_oracle(
    *,
    config: "TargetRadarPipelineRestoreConfig",
    saved_radar_time: Any,
    saved_consumer_time: Any,
    dirty_consumer_receives: list[Any],
    restored_radar_time: Any,
    restored_consumer_time: Any,
    restored_consumer_receives: list[Any],
    post_restore_scan2_reflects: list[Any],
    post_restore_duplicate_receives: list[Any],
    consumer_track_parameter: Any,
) -> dict[str, Any]:
    saved_radar_time_value = _timestamp_value(saved_radar_time)
    saved_consumer_time_value = _timestamp_value(saved_consumer_time)
    restored_radar_time_value = _timestamp_value(restored_radar_time)
    restored_consumer_time_value = _timestamp_value(restored_consumer_time)
    dirty_tags = [record.args[2] for record in dirty_consumer_receives]
    restored_tags = [record.args[2] for record in restored_consumer_receives]
    restored_payloads = [record.args[1] for record in restored_consumer_receives]

    assert saved_radar_time_value == config.scan2_input_time
    assert saved_consumer_time_value == config.scan1_end
    assert restored_radar_time_value == config.scan2_input_time
    assert restored_consumer_time_value == config.scan1_end
    assert dirty_tags == [b"dirty-scan1-track-output", b"dirty-scan2-track-output"]
    assert restored_tags == [b"restored-scan1-track-output", b"restored-scan2-track-output"]
    assert restored_payloads == [
        {consumer_track_parameter: _encode_text(config.restored_scan1_track_id)},
        {consumer_track_parameter: _encode_text(config.restored_scan2_track_id)},
    ]
    assert post_restore_scan2_reflects == []
    assert len(post_restore_duplicate_receives) == 2

    return {
        "certification_target": "time-window-save-restore-pipeline-resume",
        "state_model": (
            "SCAN1_CLOSED_SCAN2_COLLECTED_SAVED -> DIRTY_OUTPUTS_PUBLISHED -> "
            "RESTORED_COLLECTED_STATE -> RESTORED_OUTPUTS_PUBLISHED"
        ),
        "windows": [
            [config.scan1_start, config.scan1_end],
            [config.scan2_start, config.scan2_end],
        ],
        "assertions": {
            "restore_reinstates_saved_radar_time": restored_radar_time_value == saved_radar_time_value,
            "restore_reinstates_saved_consumer_time": restored_consumer_time_value == saved_consumer_time_value,
            "dirty_pipeline_outputs_do_not_replay": b"dirty-scan1-track-output" not in restored_tags
            and b"dirty-scan2-track-output" not in restored_tags,
            "scan2_collected_state_restored_without_reflection_replay": post_restore_scan2_reflects == [],
            "restored_outputs_match_saved_window_inputs": restored_payloads == [
                {consumer_track_parameter: _encode_text(config.restored_scan1_track_id)},
                {consumer_track_parameter: _encode_text(config.restored_scan2_track_id)},
            ],
            "no_duplicate_restored_pipeline_outputs_after_readvance": len(post_restore_duplicate_receives) == 2,
        },
    }


def _verify_time_window_output_delivery_oracle(
    *,
    config: "TargetRadarOutputDeliveryConfig",
    first_receive: Any,
    second_receive: Any,
    window_close_grant: Any,
    consumer_receive: Any,
    consumer_parameter: Any,
    post_delivery_receives: list[Any],
) -> dict[str, Any]:
    first_receive_time = _timestamp_value(first_receive.args[5])
    second_receive_time = _timestamp_value(second_receive.args[5])
    window_close_time = _timestamp_value(window_close_grant.args[0])
    consumer_receive_time = _timestamp_value(consumer_receive.args[5])

    transitions = [
        {
            "state": "OPEN",
            "event": "input_received",
            "logical_time": first_receive_time,
            "message_tag": first_receive.args[2],
        },
        {
            "state": "OPEN",
            "event": "input_received",
            "logical_time": second_receive_time,
            "message_tag": second_receive.args[2],
        },
        {
            "state": "CLOSED",
            "event": "window_closed",
            "logical_time": window_close_time,
            "window_end": config.scan_window_end,
        },
        {
            "state": "OUTPUT_PUBLISHED",
            "event": "track_output_delivered",
            "logical_time": consumer_receive_time,
            "message_tag": consumer_receive.args[2],
        },
        {
            "state": "CONSUMED",
            "event": "consumer_observed_track_output",
            "logical_time": consumer_receive_time,
            "message_tag": consumer_receive.args[2],
        },
    ]

    assert first_receive_time == config.first_input_time
    assert second_receive_time == config.second_input_time
    assert window_close_time == config.scan_window_end
    assert consumer_receive_time == config.radar_output_time
    assert consumer_receive.args[1] == {consumer_parameter: _encode_text(config.output_track_id)}
    assert len(post_delivery_receives) == 1

    return {
        "certification_target": "time-window-output-delivery",
        "state_model": "OPEN -> CLOSED -> OUTPUT_PUBLISHED -> CONSUMED",
        "window": [config.scan_window_start, config.scan_window_end],
        "transitions": transitions,
        "assertions": {
            "window_closed_before_output": window_close_time <= consumer_receive_time,
            "output_timestamp_not_before_window_end": consumer_receive_time >= config.scan_window_end,
            "consumer_received_single_track_output": len(post_delivery_receives) == 1,
            "consumer_received_output_at_expected_time": consumer_receive_time == config.radar_output_time,
            "output_payload_tied_to_closed_window_inputs": consumer_receive.args[1] == {
                consumer_parameter: _encode_text(config.output_track_id)
            },
            "no_duplicate_output_after_consumer_readvance": len(post_delivery_receives) == 1,
        },
    }


def _verify_time_window_consumer_order_oracle(
    *,
    config: "TargetRadarConsumerOrderConfig",
    consumer_receives: list[Any],
    consumer_track_parameter: Any,
    post_readvance_receives: list[Any],
) -> dict[str, Any]:
    delivered = [
        {
            "tag": record.args[2],
            "parameters": record.args[1],
            "logical_time": _timestamp_value(record.args[5]),
        }
        for record in consumer_receives
    ]
    timestamps = [entry["logical_time"] for entry in delivered]
    tags = [entry["tag"] for entry in delivered]

    assert timestamps == [config.competing_event_time, config.radar_output_time]
    assert tags == [b"other-track-output", b"radar-track-output"]
    assert delivered[0]["parameters"] == {consumer_track_parameter: _encode_text(config.competing_track_id)}
    assert delivered[1]["parameters"] == {consumer_track_parameter: _encode_text(config.radar_output_track_id)}
    assert len(post_readvance_receives) == 2

    return {
        "certification_target": "time-window-consumer-order",
        "state_model": "COMPETING_EVENT -> TRACK_OUTPUT",
        "window": [config.scan_window_start, config.scan_window_end],
        "deliveries": delivered,
        "assertions": {
            "consumer_delivery_timestamps_sorted": timestamps == sorted(timestamps),
            "competing_event_arrives_before_radar_output": tags == [b"other-track-output", b"radar-track-output"],
            "radar_output_timestamp_not_before_window_end": config.radar_output_time >= config.scan_window_end,
            "consumer_payloads_match_competing_and_radar_sources": delivered[0]["parameters"] == {
                consumer_track_parameter: _encode_text(config.competing_track_id)
            }
            and delivered[1]["parameters"] == {
                consumer_track_parameter: _encode_text(config.radar_output_track_id)
            },
            "no_duplicate_consumer_replay_after_readvance": len(post_readvance_receives) == 2,
        },
    }


def run_target_radar_time_window_restore_state_scenario(
    truth_rti: Any,
    radar_rti: Any,
    *,
    config: TargetRadarWindowRestoreConfig,
    truth_federate: Any,
    radar_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)

    window_state = {
        "phase": "bootstrap",
        "window_closed": False,
        "closed_at": None,
        "last_grant": None,
        "received_tags": [],
        "restore_generation": 0,
    }

    def _complete_save(save_label: str) -> tuple[Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        truth_rti.request_federation_save(save_label)
        drain_callbacks_pair(truth_rti, radar_rti, loops=24)
        truth_initiate = wait_for_callback(truth_rti, truth_federate, "initiateFederateSave", loops=120)
        radar_initiate = wait_for_callback(radar_rti, radar_federate, "initiateFederateSave", loops=120)
        assert truth_initiate is not None
        assert radar_initiate is not None
        assert truth_initiate.args[0] == save_label
        assert radar_initiate.args[0] == save_label
        truth_rti.federate_save_begun()
        radar_rti.federate_save_begun()
        truth_rti.federate_save_complete()
        radar_rti.federate_save_complete()
        drain_callbacks_pair(truth_rti, radar_rti, loops=24)
        truth_saved = wait_for_callback(truth_rti, truth_federate, "federationSaved", loops=120)
        radar_saved = wait_for_callback(radar_rti, radar_federate, "federationSaved", loops=120)
        assert truth_saved is not None
        assert radar_saved is not None
        return truth_saved, radar_saved

    def _complete_restore(save_label: str) -> tuple[Any, Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        truth_rti.request_federation_restore(save_label)
        drain_callbacks_pair(truth_rti, radar_rti, loops=24)
        restore_succeeded = wait_for_callback(
            truth_rti,
            truth_federate,
            "requestFederationRestoreSucceeded",
            loops=120,
        )
        restore_begun = wait_for_callback(
            truth_rti,
            truth_federate,
            "federationRestoreBegun",
            loops=120,
        )
        initiate_restore = wait_for_callback(
            radar_rti,
            radar_federate,
            "initiateFederateRestore",
            loops=120,
        )
        assert restore_succeeded is not None
        assert restore_begun is not None
        assert initiate_restore is not None
        truth_rti.federate_restore_complete()
        radar_rti.federate_restore_complete()
        drain_callbacks_pair(truth_rti, radar_rti, loops=24)
        truth_restored = wait_for_callback(truth_rti, truth_federate, "federationRestored", loops=120)
        radar_restored = wait_for_callback(radar_rti, radar_federate, "federationRestored", loops=120)
        assert truth_restored is not None
        assert radar_restored is not None
        return restore_succeeded, truth_restored, radar_restored

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(105.0, 0.0, 0.0)},
        b"truth-105",
        HLAinteger64Time(config.first_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.first_input_time))
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    first_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    first_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert first_reflect.args[2] == b"truth-105"
    assert first_grant.args[0] == HLAinteger64Time(config.first_input_time)
    window_state["phase"] = "open"
    window_state["last_grant"] = config.first_input_time
    window_state["received_tags"].append(first_reflect.args[2])

    open_truth_saved, open_radar_saved = _complete_save(config.save_open_name)
    saved_open_state = _snapshot_window_state(window_state)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(106.0, 0.0, 0.0)},
        b"truth-106",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    dirty_second_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    dirty_second_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert dirty_second_reflect.args[2] == b"truth-106"
    assert dirty_second_grant.args[0] == HLAinteger64Time(config.second_input_time)
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    dirty_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert dirty_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)
    window_state["phase"] = "dirty-closed"
    window_state["window_closed"] = True
    window_state["closed_at"] = config.scan_window_end
    window_state["last_grant"] = config.scan_window_end
    window_state["received_tags"].append(dirty_second_reflect.args[2])

    radar_federate.clear()
    truth_restore_open, truth_open_restored, radar_open_restored = _complete_restore(config.save_open_name)
    window_state = _snapshot_window_state(saved_open_state)
    window_state["restore_generation"] += 1
    restored_open_state = _snapshot_window_state(window_state)
    open_restored_truth_time = truth_rti.query_logical_time()
    open_restored_radar_time = radar_rti.query_logical_time()
    assert open_restored_truth_time == HLAinteger64Time(config.first_input_time)
    assert open_restored_radar_time == HLAinteger64Time(config.first_input_time)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(206.0, 0.0, 0.0)},
        b"truth-106-branch",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    reclosed_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    reclosed_second_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert reclosed_reflect.args[2] == b"truth-106-branch"
    assert reclosed_second_grant.args[0] == HLAinteger64Time(config.second_input_time)
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    reclosed_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert reclosed_grant.args[0] == HLAinteger64Time(config.scan_window_end)
    window_state["phase"] = "closed"
    window_state["window_closed"] = True
    window_state["closed_at"] = config.scan_window_end
    window_state["last_grant"] = config.scan_window_end
    window_state["received_tags"].append(reclosed_reflect.args[2])

    closed_truth_saved, closed_radar_saved = _complete_save(config.save_closed_name)
    saved_closed_state = _snapshot_window_state(window_state)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(120.0, 0.0, 0.0)},
        b"dirty-post-close",
        HLAinteger64Time(config.post_close_resume_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.post_close_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, loops=24)
    radar_rti.next_message_request(HLAinteger64Time(config.post_close_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    dirty_post_close_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    dirty_post_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert dirty_post_close_reflect.args[2] == b"dirty-post-close"
    assert dirty_post_close_grant.args[0] == HLAinteger64Time(config.post_close_resume_time)
    window_state["phase"] = "dirty-post-close"
    window_state["last_grant"] = config.post_close_resume_time
    window_state["received_tags"].append(dirty_post_close_reflect.args[2])

    radar_federate.clear()
    truth_restore_closed, truth_closed_restored, radar_closed_restored = _complete_restore(config.save_closed_name)
    window_state = _snapshot_window_state(saved_closed_state)
    window_state["restore_generation"] += 1
    restored_closed_state = _snapshot_window_state(window_state)
    closed_restored_truth_time = truth_rti.query_logical_time()
    closed_restored_radar_time = radar_rti.query_logical_time()
    assert closed_restored_truth_time == HLAinteger64Time(config.scan_window_end)
    assert closed_restored_radar_time == HLAinteger64Time(config.scan_window_end)

    truth_rti.time_advance_request(HLAinteger64Time(config.post_close_resume_time))
    radar_rti.next_message_request(HLAinteger64Time(config.post_close_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    post_closed_restore_reflects = radar_federate.callbacks_named("reflectAttributeValues")

    oracle_report = _verify_time_window_restore_oracle(
        config=config,
        saved_open_state=saved_open_state,
        restored_open_state=restored_open_state,
        saved_closed_state=saved_closed_state,
        restored_closed_state=restored_closed_state,
        open_restore_time=open_restored_radar_time,
        closed_restore_time=closed_restored_radar_time,
        reclosed_grant=reclosed_grant,
        post_closed_restore_reflects=post_closed_restore_reflects,
    )

    return {
        "certification_target": "time-window-save-restore-window-state",
        "target_object": target_object,
        "first_reflect": first_reflect,
        "first_grant": first_grant,
        "open_truth_saved": open_truth_saved,
        "open_radar_saved": open_radar_saved,
        "saved_open_state": saved_open_state,
        "dirty_second_reflect": dirty_second_reflect,
        "dirty_second_grant": dirty_second_grant,
        "dirty_close_grant": dirty_close_grant,
        "truth_restore_open": truth_restore_open,
        "truth_open_restored": truth_open_restored,
        "radar_open_restored": radar_open_restored,
        "open_restored_truth_time": open_restored_truth_time,
        "open_restored_radar_time": open_restored_radar_time,
        "restored_open_state": restored_open_state,
        "reclosed_reflect": reclosed_reflect,
        "reclosed_second_grant": reclosed_second_grant,
        "reclosed_grant": reclosed_grant,
        "closed_truth_saved": closed_truth_saved,
        "closed_radar_saved": closed_radar_saved,
        "saved_closed_state": saved_closed_state,
        "dirty_post_close_reflect": dirty_post_close_reflect,
        "dirty_post_close_grant": dirty_post_close_grant,
        "truth_restore_closed": truth_restore_closed,
        "truth_closed_restored": truth_closed_restored,
        "radar_closed_restored": radar_closed_restored,
        "closed_restored_truth_time": closed_restored_truth_time,
        "closed_restored_radar_time": closed_restored_radar_time,
        "restored_closed_state": restored_closed_state,
        "post_closed_restore_reflects": post_closed_restore_reflects,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_restore_output_scenario(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarWindowRestoreOutputConfig,
    truth_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(105.0, 0.0, 0.0)},
        b"truth-105",
        HLAinteger64Time(config.first_input_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(106.0, 0.0, 0.0)},
        b"truth-106",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    for _expected_time in (config.first_input_time, config.second_input_time, config.scan_window_end):
        radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    window_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert window_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None
    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    consumer_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    saved_consumer_time = consumer_rti.query_logical_time()
    assert saved_consumer_time == HLAinteger64Time(config.scan_window_end)

    def _complete_save() -> tuple[Any, Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        consumer_federate.clear()
        truth_rti.request_federation_save(config.save_closed_name)
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_initiate = wait_for_callback(truth_rti, truth_federate, "initiateFederateSave", loops=120)
        radar_initiate = wait_for_callback(radar_rti, radar_federate, "initiateFederateSave", loops=120)
        consumer_initiate = wait_for_callback(consumer_rti, consumer_federate, "initiateFederateSave", loops=120)
        assert truth_initiate is not None
        assert radar_initiate is not None
        assert consumer_initiate is not None
        truth_rti.federate_save_begun()
        radar_rti.federate_save_begun()
        consumer_rti.federate_save_begun()
        truth_rti.federate_save_complete()
        radar_rti.federate_save_complete()
        consumer_rti.federate_save_complete()
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_saved = wait_for_callback(truth_rti, truth_federate, "federationSaved", loops=120)
        radar_saved = wait_for_callback(radar_rti, radar_federate, "federationSaved", loops=120)
        consumer_saved = wait_for_callback(consumer_rti, consumer_federate, "federationSaved", loops=120)
        assert truth_saved is not None
        assert radar_saved is not None
        assert consumer_saved is not None
        return truth_saved, radar_saved, consumer_saved

    def _complete_restore() -> tuple[Any, Any, Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        consumer_federate.clear()
        truth_rti.request_federation_restore(config.save_closed_name)
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        restore_succeeded = wait_for_callback(
            truth_rti,
            truth_federate,
            "requestFederationRestoreSucceeded",
            loops=120,
        )
        radar_restore = wait_for_callback(radar_rti, radar_federate, "initiateFederateRestore", loops=120)
        consumer_restore = wait_for_callback(consumer_rti, consumer_federate, "initiateFederateRestore", loops=120)
        assert restore_succeeded is not None
        assert radar_restore is not None
        assert consumer_restore is not None
        truth_rti.federate_restore_complete()
        radar_rti.federate_restore_complete()
        consumer_rti.federate_restore_complete()
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_restored = wait_for_callback(truth_rti, truth_federate, "federationRestored", loops=120)
        radar_restored = wait_for_callback(radar_rti, radar_federate, "federationRestored", loops=120)
        consumer_restored = wait_for_callback(consumer_rti, consumer_federate, "federationRestored", loops=120)
        assert truth_restored is not None
        assert radar_restored is not None
        assert consumer_restored is not None
        return restore_succeeded, truth_restored, radar_restored, consumer_restored

    truth_saved, radar_saved, consumer_saved = _complete_save()

    consumer_federate.clear()
    consumer_rti.next_message_request(HLAinteger64Time(config.resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text("dirty-track-100-110")},
        b"dirty-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    dirty_consumer_receive = consumer_federate.callbacks_named("receiveInteraction")[-1]
    assert dirty_consumer_receive.args[2] == b"dirty-track-output"

    restore_succeeded, truth_restored, radar_restored, consumer_restored = _complete_restore()
    restored_truth_time = truth_rti.query_logical_time()
    restored_radar_time = radar_rti.query_logical_time()
    restored_consumer_time = consumer_rti.query_logical_time()
    assert restored_truth_time == HLAinteger64Time(config.scan_window_end)
    assert restored_radar_time == HLAinteger64Time(config.scan_window_end)
    assert restored_consumer_time == HLAinteger64Time(config.scan_window_end)

    consumer_federate.clear()
    consumer_rti.next_message_request(HLAinteger64Time(config.resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text("restored-track-100-110")},
        b"restored-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    post_restore_receives = consumer_federate.callbacks_named("receiveInteraction")
    restored_consumer_receive = post_restore_receives[-1]
    assert restored_consumer_receive.args[2] == b"restored-track-output"

    oracle_report = _verify_time_window_restore_output_oracle(
        config=config,
        saved_closed_time=restored_radar_time,
        dirty_consumer_receive=dirty_consumer_receive,
        restored_consumer_receive=restored_consumer_receive,
        post_restore_receives=post_restore_receives,
    )

    return {
        "certification_target": "time-window-save-restore-output-resume",
        "target_object": target_object,
        "window_close_grant": window_close_grant,
        "saved_consumer_time": saved_consumer_time,
        "truth_saved": truth_saved,
        "radar_saved": radar_saved,
        "consumer_saved": consumer_saved,
        "dirty_consumer_receive": dirty_consumer_receive,
        "restore_succeeded": restore_succeeded,
        "truth_restored": truth_restored,
        "radar_restored": radar_restored,
        "consumer_restored": consumer_restored,
        "restored_truth_time": restored_truth_time,
        "restored_radar_time": restored_radar_time,
        "restored_consumer_time": restored_consumer_time,
        "restored_consumer_receive": restored_consumer_receive,
        "post_restore_receives": post_restore_receives,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_receive_order_poison_scenario(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarReceiveOrderPoisonConfig,
    truth_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(10.0, 0.0, 0.0)},
        b"truth-105",
        HLAinteger64Time(config.first_input_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(11.0, 0.0, 0.0)},
        b"truth-106",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    for _expected_time in (config.first_input_time, config.second_input_time, config.scan_window_end):
        radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    window_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert window_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)

    timestamped_reflections = [
        record
        for record in radar_federate.callbacks_named("reflectAttributeValues")
        if len(record.args) > 6 and record.args[6] is not None and _timestamp_value(record.args[6]) < config.scan_window_end
    ]
    closed_window_tags_before = [record.args[2] for record in timestamped_reflections]

    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.RECEIVE)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(999.0, 0.0, 0.0)},
        b"receive-order-poison",
    )
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    poison_reflection = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    assert poison_reflection.args[2] == b"receive-order-poison"

    timestamped_reflections_after = [
        record
        for record in radar_federate.callbacks_named("reflectAttributeValues")
        if len(record.args) > 6 and record.args[6] is not None and _timestamp_value(record.args[6]) < config.scan_window_end
    ]
    closed_window_tags_after = [record.args[2] for record in timestamped_reflections_after]

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None

    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text("track-poison-safe")},
        b"radar-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    consumer_receive = consumer_federate.callbacks_named("receiveInteraction")[-1]

    oracle_report = _verify_time_window_receive_order_poison_oracle(
        config=config,
        closed_window_tags_before=closed_window_tags_before,
        closed_window_tags_after=closed_window_tags_after,
        poison_reflection=poison_reflection,
        consumer_receive=consumer_receive,
    )

    return {
        "certification_target": "time-window-receive-order-poison",
        "target_object": target_object,
        "window_close_grant": window_close_grant,
        "closed_window_tags_before": closed_window_tags_before,
        "closed_window_tags_after": closed_window_tags_after,
        "poison_reflection": poison_reflection,
        "consumer_receive": consumer_receive,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_pipeline_scenario(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarPipelineConfig,
    truth_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(1.0, 0.0, 0.0)},
        b"scan1-input-a",
        HLAinteger64Time(config.scan1_input_a_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(2.0, 0.0, 0.0)},
        b"scan1-input-b",
        HLAinteger64Time(config.scan1_input_b_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    radar_rti.next_message_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    radar_rti.next_message_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    radar_rti.next_message_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    scan1_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert scan1_close_grant.args[0] == HLAinteger64Time(config.scan1_end)

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None

    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(3.0, 0.0, 0.0)},
        b"scan2-input",
        HLAinteger64Time(config.scan2_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    radar_rti.next_message_request(HLAinteger64Time(config.scan2_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    scan2_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    assert scan2_reflect.args[2] == b"scan2-input"

    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.scan1_track_id)},
        b"scan1-track-output",
        HLAinteger64Time(config.scan1_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.scan1_output_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    radar_rti.next_message_request(HLAinteger64Time(config.scan2_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    scan2_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert scan2_close_grant.args[0] == HLAinteger64Time(config.scan2_end)

    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.scan2_track_id)},
        b"scan2-track-output",
        HLAinteger64Time(config.scan2_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(consumer_receives) == 2
    assert consumer_receives[0].args[1] == {handles["consumer_track_id"]: _encode_text(config.scan1_track_id)}
    assert consumer_receives[1].args[1] == {handles["consumer_track_id"]: _encode_text(config.scan2_track_id)}

    consumer_rti.next_message_request(HLAinteger64Time(config.duplicate_check_resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    radar_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    post_readvance_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(post_readvance_receives) == 2

    oracle_report = _verify_time_window_pipeline_oracle(
        config=config,
        scan1_close_grant=scan1_close_grant,
        scan2_reflect=scan2_reflect,
        consumer_receives=consumer_receives,
        consumer_track_parameter=handles["consumer_track_id"],
        post_readvance_receives=post_readvance_receives,
    )

    return {
        "certification_target": "time-window-pipeline-two-scans",
        "target_object": target_object,
        "scan1_close_grant": scan1_close_grant,
        "scan2_reflect": scan2_reflect,
        "scan2_close_grant": scan2_close_grant,
        "consumer_receives": consumer_receives,
        "post_readvance_receives": post_readvance_receives,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_pipeline_restore_scenario(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarPipelineRestoreConfig,
    truth_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(1.0, 0.0, 0.0)},
        b"scan1-input-a",
        HLAinteger64Time(config.scan1_input_a_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(2.0, 0.0, 0.0)},
        b"scan1-input-b",
        HLAinteger64Time(config.scan1_input_b_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    for _expected_time in (config.scan1_input_a_time, config.scan1_input_b_time, config.scan1_end):
        radar_rti.next_message_request(HLAinteger64Time(config.scan1_end))
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    scan1_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert scan1_close_grant.args[0] == HLAinteger64Time(config.scan1_end)

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None
    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    consumer_rti.next_message_request(HLAinteger64Time(config.scan1_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    saved_consumer_time = consumer_rti.query_logical_time()
    assert saved_consumer_time == HLAinteger64Time(config.scan1_end)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(3.0, 0.0, 0.0)},
        b"scan2-input",
        HLAinteger64Time(config.scan2_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    radar_rti.next_message_request(HLAinteger64Time(config.scan2_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    scan2_reflect = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    scan2_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert scan2_reflect.args[2] == b"scan2-input"
    assert scan2_grant.args[0] == HLAinteger64Time(config.scan2_input_time)
    saved_radar_time = radar_rti.query_logical_time()
    assert saved_radar_time == HLAinteger64Time(config.scan2_input_time)

    def _complete_save() -> tuple[Any, Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        consumer_federate.clear()
        truth_rti.request_federation_save(config.save_name)
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_initiate = wait_for_callback(truth_rti, truth_federate, "initiateFederateSave", loops=120)
        radar_initiate = wait_for_callback(radar_rti, radar_federate, "initiateFederateSave", loops=120)
        consumer_initiate = wait_for_callback(consumer_rti, consumer_federate, "initiateFederateSave", loops=120)
        assert truth_initiate is not None
        assert radar_initiate is not None
        assert consumer_initiate is not None
        truth_rti.federate_save_begun()
        radar_rti.federate_save_begun()
        consumer_rti.federate_save_begun()
        truth_rti.federate_save_complete()
        radar_rti.federate_save_complete()
        consumer_rti.federate_save_complete()
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_saved = wait_for_callback(truth_rti, truth_federate, "federationSaved", loops=120)
        radar_saved = wait_for_callback(radar_rti, radar_federate, "federationSaved", loops=120)
        consumer_saved = wait_for_callback(consumer_rti, consumer_federate, "federationSaved", loops=120)
        assert truth_saved is not None
        assert radar_saved is not None
        assert consumer_saved is not None
        return truth_saved, radar_saved, consumer_saved

    def _complete_restore() -> tuple[Any, Any, Any, Any]:
        truth_federate.clear()
        radar_federate.clear()
        consumer_federate.clear()
        truth_rti.request_federation_restore(config.save_name)
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        restore_succeeded = wait_for_callback(
            truth_rti,
            truth_federate,
            "requestFederationRestoreSucceeded",
            loops=120,
        )
        radar_restore = wait_for_callback(radar_rti, radar_federate, "initiateFederateRestore", loops=120)
        consumer_restore = wait_for_callback(consumer_rti, consumer_federate, "initiateFederateRestore", loops=120)
        assert restore_succeeded is not None
        assert radar_restore is not None
        assert consumer_restore is not None
        truth_rti.federate_restore_complete()
        radar_rti.federate_restore_complete()
        consumer_rti.federate_restore_complete()
        drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
        truth_restored = wait_for_callback(truth_rti, truth_federate, "federationRestored", loops=120)
        radar_restored = wait_for_callback(radar_rti, radar_federate, "federationRestored", loops=120)
        consumer_restored = wait_for_callback(consumer_rti, consumer_federate, "federationRestored", loops=120)
        assert truth_restored is not None
        assert radar_restored is not None
        assert consumer_restored is not None
        return restore_succeeded, truth_restored, radar_restored, consumer_restored

    truth_saved, radar_saved, consumer_saved = _complete_save()

    consumer_federate.clear()
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.dirty_scan1_track_id)},
        b"dirty-scan1-track-output",
        HLAinteger64Time(config.scan1_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.scan1_output_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    radar_rti.next_message_request(HLAinteger64Time(config.scan2_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    dirty_scan2_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert dirty_scan2_close_grant.args[0] == HLAinteger64Time(config.scan2_end)

    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.dirty_scan2_track_id)},
        b"dirty-scan2-track-output",
        HLAinteger64Time(config.scan2_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    dirty_consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert [record.args[2] for record in dirty_consumer_receives] == [
        b"dirty-scan1-track-output",
        b"dirty-scan2-track-output",
    ]

    restore_succeeded, truth_restored, radar_restored, consumer_restored = _complete_restore()
    restored_truth_time = truth_rti.query_logical_time()
    restored_radar_time = radar_rti.query_logical_time()
    restored_consumer_time = consumer_rti.query_logical_time()
    assert restored_radar_time == HLAinteger64Time(config.scan2_input_time)
    assert restored_consumer_time == HLAinteger64Time(config.scan1_end)

    consumer_federate.clear()
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.restored_scan1_track_id)},
        b"restored-scan1-track-output",
        HLAinteger64Time(config.scan1_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.scan1_output_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    radar_federate.clear()
    radar_rti.next_message_request(HLAinteger64Time(config.scan2_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    post_restore_scan2_reflects = radar_federate.callbacks_named("reflectAttributeValues")
    restored_scan2_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert restored_scan2_close_grant.args[0] == HLAinteger64Time(config.scan2_end)
    assert post_restore_scan2_reflects == []

    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.restored_scan2_track_id)},
        b"restored-scan2-track-output",
        HLAinteger64Time(config.scan2_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    restored_consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert [record.args[2] for record in restored_consumer_receives] == [
        b"restored-scan1-track-output",
        b"restored-scan2-track-output",
    ]

    consumer_rti.next_message_request(HLAinteger64Time(config.duplicate_check_resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    radar_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    post_restore_duplicate_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(post_restore_duplicate_receives) == 2

    oracle_report = _verify_time_window_pipeline_restore_oracle(
        config=config,
        saved_radar_time=saved_radar_time,
        saved_consumer_time=saved_consumer_time,
        dirty_consumer_receives=dirty_consumer_receives,
        restored_radar_time=restored_radar_time,
        restored_consumer_time=restored_consumer_time,
        restored_consumer_receives=restored_consumer_receives,
        post_restore_scan2_reflects=post_restore_scan2_reflects,
        post_restore_duplicate_receives=post_restore_duplicate_receives,
        consumer_track_parameter=handles["consumer_track_id"],
    )

    return {
        "certification_target": "time-window-save-restore-pipeline-resume",
        "target_object": target_object,
        "scan1_close_grant": scan1_close_grant,
        "scan2_reflect": scan2_reflect,
        "scan2_grant": scan2_grant,
        "saved_radar_time": saved_radar_time,
        "saved_consumer_time": saved_consumer_time,
        "truth_saved": truth_saved,
        "radar_saved": radar_saved,
        "consumer_saved": consumer_saved,
        "dirty_scan2_close_grant": dirty_scan2_close_grant,
        "dirty_consumer_receives": dirty_consumer_receives,
        "restore_succeeded": restore_succeeded,
        "truth_restored": truth_restored,
        "radar_restored": radar_restored,
        "consumer_restored": consumer_restored,
        "restored_truth_time": restored_truth_time,
        "restored_radar_time": restored_radar_time,
        "restored_consumer_time": restored_consumer_time,
        "restored_scan2_close_grant": restored_scan2_close_grant,
        "post_restore_scan2_reflects": post_restore_scan2_reflects,
        "restored_consumer_receives": restored_consumer_receives,
        "post_restore_duplicate_receives": post_restore_duplicate_receives,
        "oracle_report": oracle_report,
    }


def _setup_target_radar_classes(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any | None = None,
    other_rti: Any | None = None,
) -> dict[str, Any]:
    truth_target_class = truth_rti.get_object_class_handle("HLAobjectRoot.Target")
    truth_position = truth_rti.get_attribute_handle(truth_target_class, "Position")
    radar_target_class = radar_rti.get_object_class_handle("HLAobjectRoot.Target")
    radar_position = radar_rti.get_attribute_handle(radar_target_class, "Position")
    truth_track_interaction = truth_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    truth_track_id = truth_rti.get_parameter_handle(truth_track_interaction, "TrackId")
    radar_track_interaction = radar_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    mapping = {
        "truth_target_class": truth_target_class,
        "truth_position": truth_position,
        "radar_target_class": radar_target_class,
        "radar_position": radar_position,
        "truth_track_interaction": truth_track_interaction,
        "truth_track_id": truth_track_id,
        "radar_track_interaction": radar_track_interaction,
    }
    if consumer_rti is not None:
        mapping["consumer_track_interaction"] = consumer_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
        mapping["consumer_track_id"] = consumer_rti.get_parameter_handle(mapping["consumer_track_interaction"], "TrackId")
    if other_rti is not None:
        mapping["other_track_interaction"] = other_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
        mapping["other_track_id"] = other_rti.get_parameter_handle(mapping["other_track_interaction"], "TrackId")
    return mapping


def run_target_radar_time_window_output_delivery_scenario(
    truth_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarOutputDeliveryConfig,
    truth_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(105.0, 0.0, 0.0)},
        b"truth-105",
        HLAinteger64Time(config.first_input_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(106.0, 0.0, 0.0)},
        b"truth-106",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)

    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    first_receive = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    first_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert first_grant.args[0] == HLAinteger64Time(config.first_input_time)

    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    second_receive = radar_federate.callbacks_named("reflectAttributeValues")[-1]
    second_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert second_grant.args[0] == HLAinteger64Time(config.second_input_time)

    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    window_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert window_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)

    assert consumer_federate.callbacks_named("receiveInteraction") == []

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None

    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    truth_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=24)
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.output_track_id)},
        b"radar-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(consumer_receives) == 1
    consumer_receive = consumer_receives[-1]
    assert consumer_receive.args[2] == b"radar-track-output"
    assert consumer_receive.args[5] == HLAinteger64Time(config.radar_output_time)
    assert consumer_receive.args[1] == {handles["consumer_track_id"]: _encode_text(config.output_track_id)}

    consumer_rti.next_message_request(HLAinteger64Time(config.duplicate_check_resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    radar_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)
    post_delivery_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(post_delivery_receives) == 1

    oracle_report = _verify_time_window_output_delivery_oracle(
        config=config,
        first_receive=first_receive,
        second_receive=second_receive,
        window_close_grant=window_close_grant,
        consumer_receive=consumer_receive,
        consumer_parameter=handles["consumer_track_id"],
        post_delivery_receives=post_delivery_receives,
    )

    return {
        "certification_target": "time-window-output-delivery",
        "target_object": target_object,
        "first_receive": first_receive,
        "second_receive": second_receive,
        "window_close_grant": window_close_grant,
        "consumer_receive": consumer_receive,
        "post_delivery_receives": post_delivery_receives,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_consumer_order_scenario(
    truth_rti: Any,
    radar_rti: Any,
    other_rti: Any,
    consumer_rti: Any,
    *,
    config: TargetRadarConsumerOrderConfig,
    truth_federate: Any,
    radar_federate: Any,
    other_federate: Any,
    consumer_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (radar_rti, radar_federate, config.radar_name),
        (other_rti, other_federate, config.other_name),
        (consumer_rti, consumer_federate, config.consumer_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(truth_rti, radar_rti, consumer_rti, other_rti)
    truth_rti.publish_object_class_attributes(handles["truth_target_class"], {handles["truth_position"]})
    radar_rti.subscribe_object_class_attributes(handles["radar_target_class"], {handles["radar_position"]})
    radar_rti.publish_interaction_class(handles["radar_track_interaction"])
    other_rti.publish_interaction_class(handles["other_track_interaction"])
    consumer_rti.subscribe_interaction_class(handles["consumer_track_interaction"])

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=32)

    target_object = truth_rti.register_object_instance(handles["truth_target_class"], config.target_object_name)
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)
    truth_rti.change_attribute_order_type(target_object, {handles["truth_position"]}, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)

    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(205.0, 0.0, 0.0)},
        b"truth-105",
        HLAinteger64Time(config.first_input_time),
    )
    truth_rti.update_attribute_values(
        target_object,
        {handles["truth_position"]: _encode_vec3(206.0, 0.0, 0.0)},
        b"truth-106",
        HLAinteger64Time(config.second_input_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)

    for _expected_time in (config.first_input_time, config.second_input_time, config.scan_window_end):
        radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
        drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=64)
    window_close_grant = radar_federate.callbacks_named("timeAdvanceGrant")[-1]
    assert window_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)

    radar_rti.enable_time_regulation(HLAinteger64Interval(1))
    other_rti.enable_time_regulation(HLAinteger64Interval(1))
    consumer_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)
    assert wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(other_rti, other_federate, "timeRegulationEnabled", loops=120) is not None
    assert wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120) is not None

    radar_rti.change_interaction_order_type(handles["radar_track_interaction"], OrderType.TIMESTAMP)
    other_rti.change_interaction_order_type(handles["other_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)

    truth_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    other_rti.time_advance_request(HLAinteger64Time(config.scan_window_end - 1))
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=24)
    other_rti.send_interaction(
        handles["other_track_interaction"],
        {handles["other_track_id"]: _encode_text(config.competing_track_id)},
        b"other-track-output",
        HLAinteger64Time(config.competing_event_time),
    )
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text(config.radar_output_track_id)},
        b"radar-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    other_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=96)
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=96)

    consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(consumer_receives) == 2
    assert consumer_receives[0].args[1] == {handles["consumer_track_id"]: _encode_text(config.competing_track_id)}
    assert consumer_receives[1].args[1] == {handles["consumer_track_id"]: _encode_text(config.radar_output_track_id)}

    consumer_rti.next_message_request(HLAinteger64Time(config.duplicate_check_resume_time))
    truth_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    other_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    radar_rti.time_advance_request(HLAinteger64Time(config.duplicate_check_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, other_rti, consumer_rti, loops=96)
    post_readvance_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(post_readvance_receives) == 2

    oracle_report = _verify_time_window_consumer_order_oracle(
        config=config,
        consumer_receives=consumer_receives,
        consumer_track_parameter=handles["consumer_track_id"],
        post_readvance_receives=post_readvance_receives,
    )

    return {
        "certification_target": "time-window-consumer-order",
        "target_object": target_object,
        "window_close_grant": window_close_grant,
        "consumer_receives": consumer_receives,
        "post_readvance_receives": post_readvance_receives,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_core_scenario(
    truth_rti: Any,
    sensor_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    fast_rti: Any,
    slow_rti: Any,
    *,
    config: TargetRadarTimeWindowConfig,
    truth_federate: Any,
    sensor_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
    fast_federate: Any,
    slow_federate: Any,
) -> dict[str, Any]:
    members = (
        (truth_rti, truth_federate, config.truth_name),
        (sensor_rti, sensor_federate, config.sensor_name),
        (radar_rti, radar_federate, config.radar_name),
        (consumer_rti, consumer_federate, config.consumer_name),
        (fast_rti, fast_federate, config.fast_name),
        (slow_rti, slow_federate, config.slow_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    truth_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    truth_observation_interaction = truth_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    truth_observation_parameter = truth_rti.get_parameter_handle(truth_observation_interaction, "TrackId")
    radar_observation_interaction = radar_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    radar_track_interaction = radar_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    radar_track_parameter = radar_rti.get_parameter_handle(radar_track_interaction, "TrackId")
    consumer_track_interaction = consumer_rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    truth_rti.publish_interaction_class(truth_observation_interaction)
    radar_rti.subscribe_interaction_class(radar_observation_interaction)
    radar_rti.publish_interaction_class(radar_track_interaction)
    consumer_rti.subscribe_interaction_class(consumer_track_interaction)

    truth_rti.enable_time_regulation(HLAinteger64Interval(1))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=32)

    truth_rti.change_interaction_order_type(truth_observation_interaction, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=24)

    truth_rti.send_interaction(
        truth_observation_interaction,
        {truth_observation_parameter: _encode_text("truth-105")},
        b"truth-105",
        HLAinteger64Time(config.truth_update_time),
    )
    truth_rti.send_interaction(
        truth_observation_interaction,
        {truth_observation_parameter: _encode_text("sensor-106")},
        b"sensor-106",
        HLAinteger64Time(config.sensor_detection_time),
    )
    truth_rti.time_advance_request(HLAinteger64Time(config.truth_gate_time))
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=24)

    initial_lits = radar_rti.query_lits()
    initial_galt = radar_rti.query_galt()

    radar_grant_count = len(radar_federate.callbacks_named("timeAdvanceGrant"))
    radar_receive_count = len(radar_federate.callbacks_named("receiveInteraction"))
    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    first_grants = radar_federate.callbacks_named("timeAdvanceGrant")
    first_receives = radar_federate.callbacks_named("receiveInteraction")
    first_grant = first_grants[-1]
    first_receive = first_receives[-1]
    assert first_grant.args[0] == HLAinteger64Time(config.truth_update_time)
    assert first_receive.args[5] == HLAinteger64Time(config.truth_update_time)

    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    second_grants = radar_federate.callbacks_named("timeAdvanceGrant")
    sensor_receives = radar_federate.callbacks_named("receiveInteraction")
    second_grant = second_grants[-1]
    second_receive = sensor_receives[-1]
    assert second_grant.args[0] == HLAinteger64Time(config.sensor_detection_time)
    assert second_receive.args[5] == HLAinteger64Time(config.sensor_detection_time)

    blocked_galt = radar_rti.query_galt()
    blocked_lits = radar_rti.query_lits()

    radar_rti.next_message_request(HLAinteger64Time(config.scan_window_end))
    truth_rti.time_advance_request(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(truth_rti, radar_rti, loops=64)
    third_grants = radar_federate.callbacks_named("timeAdvanceGrant")
    window_close_grant = third_grants[-1]
    assert window_close_grant.args[0] == HLAinteger64Time(config.scan_window_end)
    window_closed = {
        "window_start": config.scan_window_start,
        "window_end": config.scan_window_end,
        "closed_at": config.scan_window_end,
    }
    radar_rti.enable_time_regulation(HLAinteger64Interval(10))
    consumer_rti.enable_time_constrained()
    fast_rti.enable_time_regulation(HLAinteger64Interval(1))
    slow_rti.enable_time_regulation(HLAinteger64Interval(2))
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=24)
    radar_regulation_enabled = wait_for_callback(radar_rti, radar_federate, "timeRegulationEnabled", loops=120)
    consumer_constrained_enabled = wait_for_callback(consumer_rti, consumer_federate, "timeConstrainedEnabled", loops=120)
    fast_regulation_enabled = wait_for_callback(fast_rti, fast_federate, "timeRegulationEnabled", loops=120)
    slow_regulation_enabled = wait_for_callback(slow_rti, slow_federate, "timeRegulationEnabled", loops=120)
    assert radar_regulation_enabled is not None
    assert consumer_constrained_enabled is not None
    assert fast_regulation_enabled is not None
    assert slow_regulation_enabled is not None

    late_rejections: list[int] = []
    for illegal_time in (config.scan_window_start, config.truth_update_time, config.scan_window_end - 1):
        try:
            truth_rti.send_interaction(
                truth_observation_interaction,
                {truth_observation_parameter: _encode_text(f"late-{illegal_time}")},
                f"late-{illegal_time}".encode("ascii"),
                HLAinteger64Time(illegal_time),
            )
        except InvalidLogicalTime:
            late_rejections.append(illegal_time)
        else:  # pragma: no cover - scenario contract
            raise AssertionError(f"Expected Illegal late timestamp {illegal_time} to be rejected")

    radar_federate.clear()
    consumer_federate.clear()
    truth_rti.time_advance_request(HLAinteger64Time(config.radar_output_time - 1))
    sensor_rti.time_advance_request(HLAinteger64Time(config.radar_output_time - 1))
    consumer_rti.next_message_request(HLAinteger64Time(config.consumer_resume_time))
    fast_rti.time_advance_request(HLAinteger64Time(config.fast_advance_time + 10))
    slow_rti.time_advance_request(HLAinteger64Time(config.radar_output_time - 2))
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=64)

    processing_progress = {
        "truth_time": truth_rti.query_logical_time(),
        "sensor_time": sensor_rti.query_logical_time(),
        "consumer_time_before_output": consumer_rti.query_logical_time(),
        "fast_time": fast_rti.query_logical_time(),
        "slow_time": slow_rti.query_logical_time(),
    }

    radar_rti.change_interaction_order_type(radar_track_interaction, OrderType.TIMESTAMP)
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=24)
    radar_rti.send_interaction(
        radar_track_interaction,
        {radar_track_parameter: _encode_text(config.track_object_name)},
        b"radar-track-output",
        HLAinteger64Time(config.radar_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, sensor_rti, radar_rti, consumer_rti, fast_rti, slow_rti, loops=64)

    consumer_grant = consumer_federate.last_callback("timeAdvanceGrant")

    post_close_inputs = []
    for record in radar_federate.callbacks_named("receiveInteraction"):
        timestamp = record.args[5]
        post_close_inputs.append(_timestamp_value(timestamp))
    assert all(timestamp >= config.scan_window_end for timestamp in post_close_inputs)

    oracle_report = _verify_time_window_core_oracle(
        config=config,
        first_grant=first_grant,
        first_receive=first_receive,
        second_grant=second_grant,
        second_receive=second_receive,
        window_close_grant=window_close_grant,
        post_close_inputs=post_close_inputs,
    )

    return {
        "certification_target": "time-window-core",
        "initial_lits": initial_lits,
        "initial_galt": initial_galt,
        "blocked_lits": blocked_lits,
        "blocked_galt": blocked_galt,
        "first_grant": first_grant,
        "first_receive": first_receive,
        "second_grant": second_grant,
        "second_receive": second_receive,
        "window_close_grant": window_close_grant,
        "window_closed": window_closed,
        "late_rejections": late_rejections,
        "processing_progress": processing_progress,
        "consumer_grant": consumer_grant,
        "published_output_time": HLAinteger64Time(config.radar_output_time),
        "published_output_tag": b"radar-track-output",
        "post_close_inputs": post_close_inputs,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_future_exclusion_scenario(
    slow_rti: Any,
    radar_rti: Any,
    *,
    config: TargetRadarFutureExclusionConfig,
    slow_federate: Any,
    radar_federate: Any,
) -> dict[str, Any]:
    members = (
        (slow_rti, slow_federate, config.slow_name),
        (radar_rti, radar_federate, config.radar_name),
    )
    for rti, federate, _name in members:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
    slow_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    for rti, _federate, name in members:
        rti.join_federation_execution(name, config.federate_type, config.federation_name)

    handles = _setup_target_radar_classes(slow_rti, radar_rti)
    slow_rti.publish_interaction_class(handles["truth_track_interaction"])
    radar_rti.subscribe_interaction_class(handles["radar_track_interaction"])
    drain_callbacks_pair(slow_rti, radar_rti, loops=16)

    slow_rti.enable_time_regulation(HLAinteger64Interval(config.slow_lookahead))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(slow_rti, radar_rti, loops=32)
    slow_enabled = wait_for_callback(slow_rti, slow_federate, "timeRegulationEnabled", loops=120)
    radar_enabled = wait_for_callback(radar_rti, radar_federate, "timeConstrainedEnabled", loops=120)
    assert slow_enabled is not None
    assert radar_enabled is not None
    slow_rti.change_interaction_order_type(handles["truth_track_interaction"], OrderType.TIMESTAMP)
    drain_callbacks_pair(slow_rti, radar_rti, loops=16)

    slow_rti.time_advance_request_available(HLAinteger64Time(config.slow_initial_time))
    drain_callbacks_pair(slow_rti, radar_rti, loops=64)
    initial_slow_grant = slow_federate.last_callback("timeAdvanceGrant")
    assert initial_slow_grant is not None
    assert initial_slow_grant.args[0] == HLAinteger64Time(config.slow_initial_time)

    blocked_galt = radar_rti.query_galt()
    blocked_lits = radar_rti.query_lits()
    assert _time_query_is_valid(blocked_galt) is True
    assert _time_query_is_valid(blocked_lits) is True

    radar_rti.time_advance_request_available(HLAinteger64Time(config.scan_window_end))
    drain_callbacks_pair(slow_rti, radar_rti, loops=64)
    blocked_grant = radar_federate.last_callback("timeAdvanceGrant")

    slow_rti.time_advance_request_available(HLAinteger64Time(config.slow_clearance_time))
    drain_callbacks_pair(slow_rti, radar_rti, loops=64)
    clearance_slow_grant = slow_federate.last_callback("timeAdvanceGrant")
    assert clearance_slow_grant is not None
    assert clearance_slow_grant.args[0] == HLAinteger64Time(config.slow_clearance_time)

    cleared_galt = radar_rti.query_galt()
    cleared_lits = radar_rti.query_lits()
    assert _time_query_is_valid(cleared_galt) is True
    assert _time_query_is_valid(cleared_lits) is True

    drain_callbacks_pair(slow_rti, radar_rti, loops=64)
    final_grant = wait_for_callback(radar_rti, radar_federate, "timeAdvanceGrant", loops=120)
    assert final_grant is not None

    late_send_rejected = False
    try:
        slow_rti.send_interaction(
            handles["truth_track_interaction"],
            {handles["truth_track_id"]: _encode_text("late-track-109")},
            b"late-track-109",
            HLAinteger64Time(config.illegal_late_time),
        )
    except InvalidLogicalTime:
        late_send_rejected = True

    radar_federate.clear()
    slow_rti.send_interaction(
        handles["truth_track_interaction"],
        {handles["truth_track_id"]: _encode_text("boundary-track-110")},
        b"boundary-track-110",
        HLAinteger64Time(config.legal_boundary_time),
    )
    slow_rti.time_advance_request_available(HLAinteger64Time(config.post_boundary_resume_time))
    radar_rti.next_message_request_available(HLAinteger64Time(config.post_boundary_resume_time))
    drain_callbacks_pair(slow_rti, radar_rti, loops=64)
    boundary_receive = wait_for_callback(radar_rti, radar_federate, "receiveInteraction", loops=120)
    assert boundary_receive is not None

    oracle_report = _verify_time_window_future_exclusion_oracle(
        config=config,
        blocked_grant=blocked_grant,
        final_grant=final_grant,
        blocked_galt=blocked_galt,
        cleared_galt=cleared_galt,
        late_send_rejected=late_send_rejected,
        boundary_receive=boundary_receive,
    )

    return {
        "certification_target": "time-window-future-exclusion",
        "initial_slow_grant": initial_slow_grant,
        "blocked_galt": blocked_galt,
        "blocked_lits": blocked_lits,
        "blocked_grant": blocked_grant,
        "clearance_slow_grant": clearance_slow_grant,
        "cleared_galt": cleared_galt,
        "cleared_lits": cleared_lits,
        "final_grant": final_grant,
        "late_send_rejected": late_send_rejected,
        "boundary_receive": boundary_receive,
        "oracle_report": oracle_report,
    }


def run_target_radar_time_window_gauntlet_scenario(
    truth_rti: Any,
    sensor_rti: Any,
    radar_rti: Any,
    consumer_rti: Any,
    fast_rti: Any,
    slow_rti: Any,
    *,
    config: TargetRadarTimeWindowConfig,
    truth_federate: Any,
    sensor_federate: Any,
    radar_federate: Any,
    consumer_federate: Any,
    fast_federate: Any,
    slow_federate: Any,
) -> dict[str, Any]:
    """Compatibility alias for the original over-broad route name."""
    return run_target_radar_time_window_core_scenario(
        truth_rti,
        sensor_rti,
        radar_rti,
        consumer_rti,
        fast_rti,
        slow_rti,
        config=config,
        truth_federate=truth_federate,
        sensor_federate=sensor_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
        fast_federate=fast_federate,
        slow_federate=slow_federate,
    )


__all__ = [
    "TargetRadarFutureExclusionConfig",
    "TargetRadarOutputDeliveryConfig",
    "TargetRadarConsumerOrderConfig",
    "TargetRadarPipelineConfig",
    "TargetRadarReceiveOrderPoisonConfig",
    "TargetRadarTimeWindowConfig",
    "TargetRadarWindowRestoreOutputConfig",
    "TargetRadarWindowRestoreConfig",
    "run_target_radar_time_window_consumer_order_scenario",
    "run_target_radar_time_window_future_exclusion_scenario",
    "run_target_radar_time_window_core_scenario",
    "run_target_radar_time_window_gauntlet_scenario",
    "run_target_radar_time_window_output_delivery_scenario",
    "run_target_radar_time_window_pipeline_scenario",
    "run_target_radar_time_window_receive_order_poison_scenario",
    "run_target_radar_time_window_restore_output_scenario",
    "run_target_radar_time_window_restore_state_scenario",
]
