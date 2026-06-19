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


def _verify_time_window_future_exclusion_oracle(
    *,
    config: "TargetRadarFutureExclusionConfig",
    blocked_grant: Any | None,
    final_grant: Any,
    blocked_galt: Any,
    cleared_galt: Any,
) -> dict[str, Any]:
    blocked_grant_time = None if blocked_grant is None else _timestamp_value(blocked_grant.args[0])
    final_grant_time = _timestamp_value(final_grant.args[0])
    blocked_galt_time = _timestamp_value(blocked_galt.time)
    cleared_galt_time = _timestamp_value(cleared_galt.time)

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
    ]

    assert _time_query_is_valid(blocked_galt) is True
    assert _time_query_is_valid(cleared_galt) is True
    assert blocked_galt_time == config.slow_initial_time + config.slow_lookahead
    if blocked_grant_time is not None:
        assert blocked_grant_time == blocked_galt_time
        assert blocked_grant_time < config.scan_window_end
    assert cleared_galt_time == config.scan_window_end
    assert final_grant_time == config.scan_window_end

    return {
        "certification_target": "time-window-future-exclusion",
        "state_model": (
            "POSSIBLE_FUTURE_INPUTS_EXIST -> WINDOW_BLOCKED -> "
            "FUTURE_INPUTS_EXCLUDED -> WINDOW_CLOSABLE"
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
        },
    }


def _verify_time_window_pipeline_oracle(
    *,
    config: "TargetRadarPipelineConfig",
    scan1_close_grant: Any,
    scan2_reflect: Any,
    consumer_receives: list[Any],
) -> dict[str, Any]:
    scan1_close_time = _timestamp_value(scan1_close_grant.args[0])
    scan2_input_time = _timestamp_value(scan2_reflect.args[5])
    deliveries = [
        {
            "tag": record.args[2],
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
        },
    }


def _verify_time_window_output_delivery_oracle(
    *,
    config: "TargetRadarOutputDeliveryConfig",
    first_receive: Any,
    second_receive: Any,
    window_close_grant: Any,
    consumer_receive: Any,
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

    return {
        "certification_target": "time-window-output-delivery",
        "state_model": "OPEN -> CLOSED -> OUTPUT_PUBLISHED -> CONSUMED",
        "window": [config.scan_window_start, config.scan_window_end],
        "transitions": transitions,
        "assertions": {
            "window_closed_before_output": window_close_time <= consumer_receive_time,
            "output_timestamp_not_before_window_end": consumer_receive_time >= config.scan_window_end,
            "consumer_received_single_track_output": True,
            "consumer_received_output_at_expected_time": consumer_receive_time == config.radar_output_time,
        },
    }


def _verify_time_window_consumer_order_oracle(
    *,
    config: "TargetRadarConsumerOrderConfig",
    consumer_receives: list[Any],
) -> dict[str, Any]:
    delivered = [
        {
            "tag": record.args[2],
            "logical_time": _timestamp_value(record.args[5]),
        }
        for record in consumer_receives
    ]
    timestamps = [entry["logical_time"] for entry in delivered]
    tags = [entry["tag"] for entry in delivered]

    assert timestamps == [config.competing_event_time, config.radar_output_time]
    assert tags == [b"other-track-output", b"radar-track-output"]

    return {
        "certification_target": "time-window-consumer-order",
        "state_model": "COMPETING_EVENT -> TRACK_OUTPUT",
        "window": [config.scan_window_start, config.scan_window_end],
        "deliveries": delivered,
        "assertions": {
            "consumer_delivery_timestamps_sorted": timestamps == sorted(timestamps),
            "competing_event_arrives_before_radar_output": tags == [b"other-track-output", b"radar-track-output"],
            "radar_output_timestamp_not_before_window_end": config.radar_output_time >= config.scan_window_end,
        },
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
        {handles["truth_track_id"]: _encode_text("track-scan-1")},
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
        {handles["truth_track_id"]: _encode_text("track-scan-2")},
        b"scan2-track-output",
        HLAinteger64Time(config.scan2_output_time),
    )
    radar_rti.time_advance_request(HLAinteger64Time(config.consumer_resume_time))
    drain_callbacks_pair(truth_rti, radar_rti, consumer_rti, loops=64)

    consumer_receives = consumer_federate.callbacks_named("receiveInteraction")
    assert len(consumer_receives) == 2

    oracle_report = _verify_time_window_pipeline_oracle(
        config=config,
        scan1_close_grant=scan1_close_grant,
        scan2_reflect=scan2_reflect,
        consumer_receives=consumer_receives,
    )

    return {
        "certification_target": "time-window-pipeline-two-scans",
        "target_object": target_object,
        "scan1_close_grant": scan1_close_grant,
        "scan2_reflect": scan2_reflect,
        "scan2_close_grant": scan2_close_grant,
        "consumer_receives": consumer_receives,
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
        {handles["truth_track_id"]: _encode_text("track-100-110")},
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

    oracle_report = _verify_time_window_output_delivery_oracle(
        config=config,
        first_receive=first_receive,
        second_receive=second_receive,
        window_close_grant=window_close_grant,
        consumer_receive=consumer_receive,
    )

    return {
        "certification_target": "time-window-output-delivery",
        "target_object": target_object,
        "first_receive": first_receive,
        "second_receive": second_receive,
        "window_close_grant": window_close_grant,
        "consumer_receive": consumer_receive,
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
        {handles["other_track_id"]: _encode_text("other-track-110")},
        b"other-track-output",
        HLAinteger64Time(config.competing_event_time),
    )
    radar_rti.send_interaction(
        handles["radar_track_interaction"],
        {handles["truth_track_id"]: _encode_text("radar-track-111")},
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

    oracle_report = _verify_time_window_consumer_order_oracle(
        config=config,
        consumer_receives=consumer_receives,
    )

    return {
        "certification_target": "time-window-consumer-order",
        "target_object": target_object,
        "window_close_grant": window_close_grant,
        "consumer_receives": consumer_receives,
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

    slow_rti.enable_time_regulation(HLAinteger64Interval(config.slow_lookahead))
    radar_rti.enable_time_constrained()
    drain_callbacks_pair(slow_rti, radar_rti, loops=32)
    slow_enabled = wait_for_callback(slow_rti, slow_federate, "timeRegulationEnabled", loops=120)
    radar_enabled = wait_for_callback(radar_rti, radar_federate, "timeConstrainedEnabled", loops=120)
    assert slow_enabled is not None
    assert radar_enabled is not None

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

    oracle_report = _verify_time_window_future_exclusion_oracle(
        config=config,
        blocked_grant=blocked_grant,
        final_grant=final_grant,
        blocked_galt=blocked_galt,
        cleared_galt=cleared_galt,
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
    "TargetRadarTimeWindowConfig",
    "run_target_radar_time_window_consumer_order_scenario",
    "run_target_radar_time_window_future_exclusion_scenario",
    "run_target_radar_time_window_core_scenario",
    "run_target_radar_time_window_gauntlet_scenario",
    "run_target_radar_time_window_output_delivery_scenario",
    "run_target_radar_time_window_pipeline_scenario",
]
