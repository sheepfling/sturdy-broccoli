"""Repo-internal executable showcase scenario for Proto2025 TimeMgmtTest."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.inmemory import InMemoryRTIEngine, rti_ambassador
from hla.rti1516_2025.foms import scenario_fom_paths
from hla.rti1516e.enums import CallbackModel, ResignAction


def _drain(*rtis: object, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return repr(value)


def run_time_mgmt_test_showcase() -> dict[str, Any]:
    """Run the package-owned TimeMgmtTest showcase scenario."""

    engine = InMemoryRTIEngine()
    source = rti_ambassador(engine=engine)
    sink = rti_ambassador(engine=engine)
    source_fed = RecordingFederateAmbassador()
    sink_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("time-mgmt-test")
    federation_name = f"Proto2025TimeMgmtShowcase-{uuid.uuid4().hex[:8]}"
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

        participant_class = source.get_object_class_handle("HLAobjectRoot.Proto2025.TimeMgmtTest.TimeParticipant")
        federate_name_attr = source.get_attribute_handle(participant_class, "FederateName")
        current_time_attr = source.get_attribute_handle(participant_class, "CurrentLogicalTime")
        source.publish_object_class_attributes(participant_class, {federate_name_attr, current_time_attr})
        sink.subscribe_object_class_attributes(participant_class, {federate_name_attr, current_time_attr})
        participant = source.register_object_instance(participant_class, "EventSourceFederate-time-state")
        _drain(source, sink)
        source.update_attribute_values(
            participant,
            {federate_name_attr: b"EventSourceFederate", current_time_attr: b"0"},
            b"proto2025-time-participant-state",
        )
        _drain(source, sink)
        lifecycle.append("time-participant-state-reflected")

        event_interaction = source.get_interaction_class_handle("HLAinteractionRoot.Proto2025.TimeMgmtTest.EmitEvent")
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
            "fom_modules": [Path(path).name for path in foms],
            "federates": ["EventSourceFederate", "EventSinkFederate"],
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.Proto2025.TimeMgmtTest.TimeParticipant",
            "interaction_class": "HLAinteractionRoot.Proto2025.TimeMgmtTest.EmitEvent",
            "discoveries": len(sink_fed.callbacks_named("discoverObjectInstance")),
            "reflections": len(sink_fed.callbacks_named("reflectAttributeValues")),
            "interactions": len(received),
            "callbacks": len(source_fed.records) + len(sink_fed.records),
            "grant_times": grant_times,
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "key_outcome": "timestamp ordered events delivered with time advance grants",
            "execution_complete": timestamp_ordered and bool(grants),
            "requirements_exercised": [
                "HLA2025-FR-001",
                "HLA2025-FR-003",
                "HLA2025-FR-004",
                "HLA2025-FI-001",
                "HLA2025-FI-009",
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
