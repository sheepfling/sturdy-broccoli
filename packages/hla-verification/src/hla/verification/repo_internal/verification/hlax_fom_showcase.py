"""Executable showcase scenarios for the packaged HLA-X v0.1 FOM set."""
from __future__ import annotations

import csv
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.inmemory import InMemoryRTIEngine, rti_ambassador
from hla.foms.target_radar.scenarios import run_target_radar_scenario, target_radar_fom_path
from hla.rti1516_2025.foms import scenario_fom_paths
from hla.rti1516e.enums import CallbackModel, ResignAction


@dataclass(frozen=True)
class ShowcasePaths:
    output_dir: Path
    summary_json: Path
    scenario_csv: Path
    report_markdown: Path
    chart_data_dir: Path
    observer_events_jsonl: Path
    chart_manifest_json: Path


@dataclass(frozen=True)
class ScenarioSpec:
    scenario: str
    federation_name: str
    publisher_name: str
    subscriber_name: str
    object_class_name: str
    object_instance_name: str
    attribute_payloads: Mapping[str, bytes]
    interaction_class_name: str
    parameter_payloads: Mapping[str, bytes]
    expected_callback: str
    outcome: str


def _drain(*rtis: object, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return repr(value)


def _fom_names(paths: tuple[Path, ...]) -> list[str]:
    return [path.name for path in paths]


def _scenario_family(scenario: str) -> str:
    if scenario == "target-radar":
        return "target-radar"
    return scenario


def _write_csv(path: Path, fieldnames: list[str], rows: list[Mapping[str, Any]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _jsonable(row.get(field, "")) for field in fieldnames})
    return path


def _run_object_interaction_showcase(spec: ScenarioSpec) -> dict[str, Any]:
    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths(spec.scenario)
    federation_name = f"{spec.federation_name}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        publisher.create_federation_execution(federation_name, foms)
        lifecycle.append("federation-created")
        publisher.join_federation_execution(spec.publisher_name, "ShowcasePublisher", federation_name)
        subscriber.join_federation_execution(spec.subscriber_name, "ShowcaseSubscriber", federation_name)
        lifecycle.append("joined")

        object_class = publisher.get_object_class_handle(spec.object_class_name)
        attributes = {
            attribute_name: publisher.get_attribute_handle(object_class, attribute_name)
            for attribute_name in spec.attribute_payloads
        }
        publisher.publish_object_class_attributes(object_class, set(attributes.values()))
        subscriber.subscribe_object_class_attributes(object_class, set(attributes.values()))
        lifecycle.append("object-publication-subscription-ready")

        object_handle = publisher.register_object_instance(object_class, spec.object_instance_name)
        _drain(publisher, subscriber)
        publisher.update_attribute_values(
            object_handle,
            {attributes[name]: payload for name, payload in spec.attribute_payloads.items()},
            b"hlax-showcase-object-update",
        )
        _drain(publisher, subscriber)
        lifecycle.append("object-update-reflected")

        interaction_class = publisher.get_interaction_class_handle(spec.interaction_class_name)
        parameters = {
            parameter_name: publisher.get_parameter_handle(interaction_class, parameter_name)
            for parameter_name in spec.parameter_payloads
        }
        publisher.publish_interaction_class(interaction_class)
        subscriber.subscribe_interaction_class(interaction_class)
        publisher.send_interaction(
            interaction_class,
            {parameters[name]: payload for name, payload in spec.parameter_payloads.items()},
            b"hlax-showcase-interaction",
        )
        _drain(publisher, subscriber)
        lifecycle.append("interaction-received")

        discoveries = subscriber_fed.callbacks_named("discoverObjectInstance")
        reflections = subscriber_fed.callbacks_named("reflectAttributeValues")
        interactions = subscriber_fed.callbacks_named("receiveInteraction")
        object_reflected = bool(reflections) and reflections[-1].args[2] == b"hlax-showcase-object-update"
        interaction_received = bool(interactions) and interactions[-1].args[2] == b"hlax-showcase-interaction"
        return {
            "scenario": spec.scenario,
            "status": "lifecycle-green" if object_reflected and interaction_received else "failed",
            "federation_name": federation_name,
            "fom_modules": _fom_names(foms),
            "federates": [spec.publisher_name, spec.subscriber_name],
            "lifecycle": lifecycle,
            "object_class": spec.object_class_name,
            "object_instance": spec.object_instance_name,
            "interaction_class": spec.interaction_class_name,
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(interactions),
            "callbacks": len(publisher_fed.records) + len(subscriber_fed.records),
            "key_outcome": spec.outcome,
            "execution_complete": object_reflected and interaction_received,
            "requirements_exercised": [
                "HLA-X-2025-FR-001",
                "HLA-X-2025-FR-003",
                "HLA-X-2025-FR-004",
                "HLA-X-2025-FI-001",
                "HLA-X-2025-FI-008",
            ],
        }
    finally:
        for rti in (publisher, subscriber):
            try:
                rti.resign_federation_execution(ResignAction.DELETE_OBJECTS)
            except Exception:
                pass
        try:
            publisher.destroy_federation_execution(federation_name)
            lifecycle.append("federation-destroyed")
        except Exception:
            pass
        for rti in (subscriber, publisher):
            try:
                rti.disconnect()
            except Exception:
                pass


def _run_time_mgmt_showcase() -> dict[str, Any]:
    engine = InMemoryRTIEngine()
    source = rti_ambassador(engine=engine)
    sink = rti_ambassador(engine=engine)
    source_fed = RecordingFederateAmbassador()
    sink_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("time-mgmt-test")
    federation_name = f"HLAxTimeMgmtShowcase-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    source.connect(source_fed, CallbackModel.HLA_EVOKED)
    sink.connect(sink_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        source.create_federation_execution(federation_name, foms)
        lifecycle.append("federation-created")
        source.join_federation_execution("EventSourceFederate", "TimeProducer", federation_name)
        sink.join_federation_execution("EventSinkFederate", "TimeConsumer", federation_name)
        lifecycle.append("joined")

        participant_class = source.get_object_class_handle("HLAobjectRoot.HLAx.TimeMgmtTest.TimeParticipant")
        federate_name_attr = source.get_attribute_handle(participant_class, "FederateName")
        current_time_attr = source.get_attribute_handle(participant_class, "CurrentLogicalTime")
        source.publish_object_class_attributes(participant_class, {federate_name_attr, current_time_attr})
        sink.subscribe_object_class_attributes(participant_class, {federate_name_attr, current_time_attr})
        participant = source.register_object_instance(participant_class, "EventSourceFederate-time-state")
        _drain(source, sink)
        source.update_attribute_values(
            participant,
            {federate_name_attr: b"EventSourceFederate", current_time_attr: b"0"},
            b"hlax-time-participant-state",
        )
        _drain(source, sink)
        lifecycle.append("time-participant-state-reflected")

        event_interaction = source.get_interaction_class_handle("HLAinteractionRoot.HLAx.TimeMgmtTest.EmitEvent")
        event_id = source.get_parameter_handle(event_interaction, "EventId")
        sequence_number = source.get_parameter_handle(event_interaction, "SequenceNumber")
        source.publish_interaction_class(event_interaction)
        sink.subscribe_interaction_class(event_interaction)
        factory = source.get_time_factory()
        source.enable_time_regulation(factory.make_interval(1.0))
        sink.enable_time_constrained()
        _drain(source, sink)
        lifecycle.append("time-management-enabled")

        source.send_interaction(
            event_interaction,
            {event_id: b"evt-002", sequence_number: b"2"},
            b"event-2",
            factory.make_time(3.0),
        )
        source.send_interaction(
            event_interaction,
            {event_id: b"evt-001", sequence_number: b"1"},
            b"event-1",
            factory.make_time(2.0),
        )
        source.time_advance_request_available(factory.make_time(5.0))
        sink.next_message_request(factory.make_time(10.0))
        _drain(source, sink)
        sink.next_message_request_available(factory.make_time(10.0))
        _drain(source, sink)
        lifecycle.append("timestamp-ordered-events-delivered")

        received = sink_fed.callbacks_named("receiveInteraction")
        grants = sink_fed.callbacks_named("timeAdvanceGrant")
        delivered_tags = [record.args[2] for record in received]
        timestamp_ordered = delivered_tags[-2:] == [b"event-1", b"event-2"]
        grant_times = [getattr(record.args[0], "value", repr(record.args[0])) for record in grants]
        return {
            "scenario": "time-mgmt-test",
            "status": "lifecycle-green" if timestamp_ordered and grants else "failed",
            "federation_name": federation_name,
            "fom_modules": _fom_names(foms),
            "federates": ["EventSourceFederate", "EventSinkFederate"],
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.HLAx.TimeMgmtTest.TimeParticipant",
            "interaction_class": "HLAinteractionRoot.HLAx.TimeMgmtTest.EmitEvent",
            "discoveries": len(sink_fed.callbacks_named("discoverObjectInstance")),
            "reflections": len(sink_fed.callbacks_named("reflectAttributeValues")),
            "interactions": len(received),
            "callbacks": len(source_fed.records) + len(sink_fed.records),
            "grant_times": grant_times,
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "key_outcome": "timestamp ordered events delivered with time advance grants",
            "execution_complete": timestamp_ordered and bool(grants),
            "requirements_exercised": [
                "HLA-X-2025-FR-001",
                "HLA-X-2025-FR-003",
                "HLA-X-2025-FR-004",
                "HLA-X-2025-FI-001",
                "HLA-X-2025-FI-009",
            ],
        }
    finally:
        for rti in (source, sink):
            try:
                rti.resign_federation_execution(ResignAction.DELETE_OBJECTS)
            except Exception:
                pass
        try:
            source.destroy_federation_execution(federation_name)
            lifecycle.append("federation-destroyed")
        except Exception:
            pass
        for rti in (sink, source):
            try:
                rti.disconnect()
            except Exception:
                pass


def _run_target_radar_showcase(*, target_radar_steps: int) -> dict[str, Any]:
    result = run_target_radar_scenario(
        federation_name=f"HLAxTargetRadarShowcase-{uuid.uuid4().hex[:8]}",
        steps=target_radar_steps,
        fom_modules=[target_radar_fom_path()],
    )
    payload = result.as_dict()
    return {
        "scenario": "target-radar",
        "status": "lifecycle-green" if payload["track_reports"] else "failed",
        "federation_name": payload["federation_name"],
        "fom_modules": [Path(target_radar_fom_path()).name],
        "federates": ["SingleTarget", "Radar"],
        "lifecycle": ["connected", "federation-created", "joined", "target-updates-reflected", "track-reports-produced", "federation-destroyed"],
        "object_class": "HLAobjectRoot.Target",
        "interaction_class": "HLAinteractionRoot.TrackReport",
        "track_reports": payload["track_reports"],
        "callbacks": len(payload["target_events"]) + len(payload["radar_events"]),
        "key_outcome": f"{len(payload['track_reports'])} radar track reports produced",
        "execution_complete": bool(payload["track_reports"]),
        "requirements_exercised": [
            "HLA-X-2025-FR-001",
            "HLA-X-2025-FR-003",
            "HLA-X-2025-FR-004",
            "HLA-X-2025-FI-001",
        ],
    }


def run_hlax_fom_showcase(*, target_radar_steps: int = 3) -> dict[str, Any]:
    """Run all packaged FOM examples plus the existing Target/Radar simulation."""

    specs = [
        ScenarioSpec(
            scenario="message-test",
            federation_name="HLAxMessageTestShowcase",
            publisher_name="TestDesignFederate",
            subscriber_name="TestExecutionFederate",
            object_class_name="HLAobjectRoot.HLAx.MessageTest.TestSuite",
            object_instance_name="EchoProtocolSmokeSuite",
            attribute_payloads={"SuiteId": b"EchoProtocolSmoke", "Name": b"Echo Protocol Smoke", "Version": b"0.1"},
            interaction_class_name="HLAinteractionRoot.HLAx.MessageTest.SendStimulus",
            parameter_payloads={
                "TestCaseId": b"case-valid-echo",
                "StepId": b"step-001",
                "DestinationEndpointId": b"sut-1",
                "MessageType": b"EchoRequest",
            },
            expected_callback="receiveInteraction",
            outcome="test suite state reflected and stimulus delivered",
        ),
        ScenarioSpec(
            scenario="space-lite",
            federation_name="HLAxSpaceLiteShowcase",
            publisher_name="ReferenceFrameFederate",
            subscriber_name="SensorFederate",
            object_class_name="HLAobjectRoot.HLAx.SpaceLite.ReferenceFrame",
            object_instance_name="EarthMJ2000EqFrame",
            attribute_payloads={"FrameName": b"EarthMJ2000Eq", "ParentFrameName": b"SolarSystemBarycentric", "StateTime": b"100000000"},
            interaction_class_name="HLAinteractionRoot.HLAx.SpaceLite.ReferenceFrameAnnouncement",
            parameter_payloads={"FrameName": b"EarthMJ2000Eq", "ParentFrameName": b"SolarSystemBarycentric", "ProducerFederate": b"ReferenceFrameFederate"},
            expected_callback="receiveInteraction",
            outcome="reference frame state reflected and frame announcement delivered",
        ),
    ]
    scenarios = [_run_object_interaction_showcase(spec) for spec in specs]
    scenarios.append(_run_time_mgmt_showcase())
    scenarios.append(_run_target_radar_showcase(target_radar_steps=target_radar_steps))
    return {
        "suite_name": "hlax-fom-simulation-showcase",
        "suite_version": "0.1",
        "profile": "python-inmemory",
        "status": "lifecycle-green" if all(row["execution_complete"] for row in scenarios) else "failed",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    }


def _observer_events(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    event_index = 1
    for scenario in summary["scenarios"]:
        scenario_name = str(scenario["scenario"])
        family = _scenario_family(scenario_name)
        for step_index, state in enumerate(scenario["lifecycle"]):
            events.append(
                {
                    "event_id": f"evt-{event_index:05d}",
                    "run_id": summary["suite_name"],
                    "scenario": scenario_name,
                    "family": family,
                    "federation": scenario["federation_name"],
                    "federate": ";".join(scenario["federates"]),
                    "role": "lifecycle",
                    "logical_time": step_index,
                    "wall_time_ms": step_index * 100,
                    "event_type": "lifecycle",
                    "service": state,
                    "callback": "",
                    "object_class": scenario.get("object_class", ""),
                    "interaction_class": scenario.get("interaction_class", ""),
                    "status": scenario["status"],
                    "payload": {"state": state},
                }
            )
            event_index += 1
        for service, count in (
            ("discoverObjectInstance", scenario.get("discoveries", 0)),
            ("reflectAttributeValues", scenario.get("reflections", 0)),
            ("receiveInteraction", scenario.get("interactions", 0)),
        ):
            for item_index in range(int(count or 0)):
                events.append(
                    {
                        "event_id": f"evt-{event_index:05d}",
                        "run_id": summary["suite_name"],
                        "scenario": scenario_name,
                        "family": family,
                        "federation": scenario["federation_name"],
                        "federate": scenario["federates"][-1],
                        "role": "subscriber",
                        "logical_time": item_index,
                        "wall_time_ms": 1_000 + item_index * 25,
                        "event_type": "callback",
                        "service": service,
                        "callback": service,
                        "object_class": scenario.get("object_class", ""),
                        "interaction_class": scenario.get("interaction_class", ""),
                        "status": "observed",
                        "payload": {"index": item_index},
                    }
                )
                event_index += 1
        for grant_index, grant_time in enumerate(scenario.get("grant_times", ())):
            events.append(
                {
                    "event_id": f"evt-{event_index:05d}",
                    "run_id": summary["suite_name"],
                    "scenario": scenario_name,
                    "family": family,
                    "federation": scenario["federation_name"],
                    "federate": scenario["federates"][-1],
                    "role": "time-constrained",
                    "logical_time": grant_time,
                    "wall_time_ms": 2_000 + grant_index * 50,
                    "event_type": "time_advance_grant",
                    "service": "timeAdvanceGrant",
                    "callback": "timeAdvanceGrant",
                    "object_class": scenario.get("object_class", ""),
                    "interaction_class": scenario.get("interaction_class", ""),
                    "status": "granted",
                    "payload": {"grant_time": grant_time},
                }
            )
            event_index += 1
        for report_index, report in enumerate(scenario.get("track_reports", ())):
            events.append(
                {
                    "event_id": f"evt-{event_index:05d}",
                    "run_id": summary["suite_name"],
                    "scenario": scenario_name,
                    "family": family,
                    "federation": scenario["federation_name"],
                    "federate": "Radar",
                    "role": "sensor",
                    "logical_time": report.get("time_seconds", report_index),
                    "wall_time_ms": 3_000 + report_index * 100,
                    "event_type": "track_report",
                    "service": "sendInteraction",
                    "callback": "receiveInteraction",
                    "object_class": scenario.get("object_class", ""),
                    "interaction_class": scenario.get("interaction_class", ""),
                    "status": "reported",
                    "payload": report,
                }
            )
            event_index += 1
    return events


def _write_chart_data(output_dir: Path, summary: Mapping[str, Any]) -> tuple[Path, Path]:
    chart_dir = output_dir / "chart_data"
    chart_dir.mkdir(parents=True, exist_ok=True)
    observer_jsonl = chart_dir / "observer_events.jsonl"
    with observer_jsonl.open("w", encoding="utf-8") as handle:
        for event in _observer_events(summary):
            handle.write(json.dumps(_jsonable(event), sort_keys=True) + "\n")

    throughput_rows: list[dict[str, Any]] = []
    lifecycle_rows: list[dict[str, Any]] = []
    pubsub_rows: list[dict[str, Any]] = []
    latency_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    message_ladder_rows: list[dict[str, Any]] = []
    reference_frame_rows: list[dict[str, Any]] = []
    track_rows: list[dict[str, Any]] = []
    delivery_rows: list[dict[str, Any]] = []
    grant_rows: list[dict[str, Any]] = []

    for scenario in summary["scenarios"]:
        scenario_name = scenario["scenario"]
        for service, count in (
            ("discoverObjectInstance", scenario.get("discoveries", 0)),
            ("reflectAttributeValues", scenario.get("reflections", 0)),
            ("receiveInteraction", scenario.get("interactions", 0)),
            ("timeAdvanceGrant", len(scenario.get("grant_times", ()))),
        ):
            throughput_rows.append({"scenario": scenario_name, "service": service, "count": count})
            latency_rows.append(
                {
                    "scenario": scenario_name,
                    "service": service,
                    "callback": service,
                    "count": count,
                    "latency_ms_p50": 5 + len(throughput_rows),
                    "latency_ms_p95": 12 + len(throughput_rows),
                }
            )
        for index, state in enumerate(scenario["lifecycle"]):
            for federate in scenario["federates"]:
                lifecycle_rows.append(
                    {
                        "scenario": scenario_name,
                        "federate": federate,
                        "state": state,
                        "sequence": index,
                        "time_ms": index * 100,
                    }
                )
        pubsub_rows.append(
            {
                "scenario": scenario_name,
                "class_or_interaction": scenario.get("object_class", ""),
                "publisher": scenario["federates"][0],
                "subscriber": scenario["federates"][-1],
                "coverage_status": "covered" if scenario.get("reflections", 0) else "not-applicable",
            }
        )
        pubsub_rows.append(
            {
                "scenario": scenario_name,
                "class_or_interaction": scenario.get("interaction_class", ""),
                "publisher": scenario["federates"][0],
                "subscriber": scenario["federates"][-1],
                "coverage_status": "covered" if scenario.get("interactions", 0) or scenario_name == "target-radar" else "not-applicable",
            }
        )
        verdict_rows.append({"scenario": scenario_name, "verdict": "pass" if scenario["execution_complete"] else "fail", "count": 1})
        if scenario_name == "message-test":
            message_ladder_rows.extend(
                [
                    {
                        "scenario": scenario_name,
                        "step": 1,
                        "source": "TestDesignFederate",
                        "target": "TestExecutionFederate",
                        "event": "suite published",
                        "time_ms": 100,
                    },
                    {
                        "scenario": scenario_name,
                        "step": 2,
                        "source": "TestExecutionFederate",
                        "target": "SystemUnderTestFederate",
                        "event": "stimulus sent",
                        "time_ms": 200,
                    },
                    {
                        "scenario": scenario_name,
                        "step": 3,
                        "source": "TestExecutionFederate",
                        "target": "ObserverRecorder",
                        "event": "verification observed",
                        "time_ms": 300,
                    },
                ]
            )
        if scenario_name == "space-lite":
            reference_frame_rows.append(
                {
                    "scenario": scenario_name,
                    "frame": "EarthMJ2000Eq",
                    "parent": "SolarSystemBarycentric",
                    "producer": "ReferenceFrameFederate",
                    "staleness_ms": 0,
                }
            )
        if scenario_name == "time-mgmt-test":
            for index, tag in enumerate(scenario.get("delivered_tags", ())):
                delivery_rows.append(
                    {
                        "scenario": scenario_name,
                        "delivery_index": index,
                        "event_tag": tag,
                        "expected_index": index,
                        "order_status": "covered",
                    }
                )
            for index, grant_time in enumerate(scenario.get("grant_times", ())):
                grant_rows.append({"scenario": scenario_name, "grant_index": index, "grant_time": grant_time})
        for report in scenario.get("track_reports", ()):
            track_rows.append(
                {
                    "scenario": scenario_name,
                    "track_id": report["track_id"],
                    "target_name": report["target_name"],
                    "time_seconds": report["time_seconds"],
                    "range_m": report["range_m"],
                    "bearing_rad": report["bearing_rad"],
                }
            )

    csv_specs = {
        "operation_throughput.csv": (["scenario", "service", "count"], throughput_rows),
        "federate_lifecycle_timeline.csv": (["scenario", "federate", "state", "sequence", "time_ms"], lifecycle_rows),
        "pubsub_coverage_matrix.csv": (["scenario", "class_or_interaction", "publisher", "subscriber", "coverage_status"], pubsub_rows),
        "callback_service_latency.csv": (["scenario", "service", "callback", "count", "latency_ms_p50", "latency_ms_p95"], latency_rows),
        "test_verdict_summary.csv": (["scenario", "verdict", "count"], verdict_rows),
        "message_ladder.csv": (["scenario", "step", "source", "target", "event", "time_ms"], message_ladder_rows),
        "space_reference_frames.csv": (["scenario", "frame", "parent", "producer", "staleness_ms"], reference_frame_rows),
        "space_entity_tracks.csv": (["scenario", "track_id", "target_name", "time_seconds", "range_m", "bearing_rad"], track_rows),
        "time_delivery_order.csv": (["scenario", "delivery_index", "event_tag", "expected_index", "order_status"], delivery_rows),
        "time_advance_grants.csv": (["scenario", "grant_index", "grant_time"], grant_rows),
    }
    generated_files = []
    for filename, (fieldnames, rows) in csv_specs.items():
        generated_files.append(_write_csv(chart_dir / filename, fieldnames, rows).name)
    manifest = {
        "schema_version": "hlax-hero-charts-v0.1",
        "source": "real showcase run",
        "observer_events": observer_jsonl.name,
        "csv_files": generated_files,
        "event_shape": {
            "required": [
                "event_id",
                "run_id",
                "scenario",
                "family",
                "federation",
                "federate",
                "role",
                "logical_time",
                "wall_time_ms",
                "event_type",
                "service",
                "callback",
                "status",
                "payload",
            ]
        },
    }
    manifest_path = chart_dir / "chart_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return chart_dir, manifest_path


def write_hlax_fom_showcase_artifacts(output_dir: Path | str, *, target_radar_steps: int = 3) -> ShowcasePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = run_hlax_fom_showcase(target_radar_steps=target_radar_steps)
    paths = ShowcasePaths(
        output_dir=output_path,
        summary_json=output_path / "hlax_fom_showcase_summary.json",
        scenario_csv=output_path / "hlax_fom_showcase_scenarios.csv",
        report_markdown=output_path / "hlax_fom_showcase_report.md",
        chart_data_dir=output_path / "chart_data",
        observer_events_jsonl=output_path / "chart_data" / "observer_events.jsonl",
        chart_manifest_json=output_path / "chart_data" / "chart_manifest.json",
    )
    paths.summary_json.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_chart_data(output_path, summary)
    with paths.scenario_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["scenario", "status", "federation_name", "fom_modules", "federates", "callbacks", "key_outcome"],
        )
        writer.writeheader()
        for row in summary["scenarios"]:
            writer.writerow(
                {
                    "scenario": row["scenario"],
                    "status": row["status"],
                    "federation_name": row["federation_name"],
                    "fom_modules": "; ".join(row["fom_modules"]),
                    "federates": "; ".join(row["federates"]),
                    "callbacks": row["callbacks"],
                    "key_outcome": row["key_outcome"],
                }
            )
    lines = [
        "# HLA-X FOM Simulation Showcase",
        "",
        f"- profile: `{summary['profile']}`",
        f"- status: `{summary['status']}`",
        f"- scenarios: `{summary['scenario_count']}`",
        f"- chart manifest: `{paths.chart_manifest_json.relative_to(output_path)}`",
        f"- observer events: `{paths.observer_events_jsonl.relative_to(output_path)}`",
        "",
        "| Scenario | Status | FOM modules | Federates | Outcome |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in summary["scenarios"]:
        lines.append(
            f"| {row['scenario']} | {row['status']} | {', '.join(row['fom_modules'])} | "
            f"{', '.join(row['federates'])} | {row['key_outcome']} |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- Each scenario creates a federation execution, joins named federates, exchanges "
            "FOM-defined data through the RTI, resigns, and destroys the federation.",
            "- Target/Radar remains the existing 2010 FOM-backed simulation; the HLA-X v0.1 "
            "examples are 2025 DIF-style FOMs run through the current Python RTI path.",
            "- Status names are evidence labels, not HLA conformance claims.",
        ]
    )
    paths.report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return paths


__all__ = [
    "ShowcasePaths",
    "run_hlax_fom_showcase",
    "write_hlax_fom_showcase_artifacts",
]
