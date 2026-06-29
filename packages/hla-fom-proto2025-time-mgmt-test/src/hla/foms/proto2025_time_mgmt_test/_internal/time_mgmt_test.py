"""Repo-internal executable showcase scenario for Proto2025 TimeMgmtTest."""
from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.fom.proto2025 import scenario_fom_paths
from hla.rti1516_2025.enums import CallbackModel, ResignAction
from hla.runtime.rti1516_2025_factory import create_rti_ambassador


def _drain(*rtis: Any, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return repr(value)


def run_time_mgmt_test_showcase(*, rti_factory: Callable[[], Any] | None = None) -> dict[str, Any]:
    """Run the package-owned TimeMgmtTest showcase scenario."""

    spawn_rti = rti_factory or create_rti_ambassador
    source = spawn_rti()
    sink = spawn_rti()
    source_fed = RecordingFederateAmbassador()
    sink_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("time-mgmt-test")
    federation_name = f"Proto2025TimeMgmtShowcase-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    source.connect(source_fed, CallbackModel.HLA_EVOKED)
    sink.connect(sink_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        source.createFederationExecution(federation_name, foms)
        lifecycle.append("federation-created")
        source.joinFederationExecution("EventSourceFederate", "TimeProducer", federation_name)
        sink.joinFederationExecution("EventSinkFederate", "TimeConsumer", federation_name)
        lifecycle.append("joined")

        participant_class = source.getObjectClassHandle("HLAobjectRoot.Proto2025.TimeMgmtTest.TimeParticipant")
        federate_name_attr = source.getAttributeHandle(participant_class, "FederateName")
        current_time_attr = source.getAttributeHandle(participant_class, "CurrentLogicalTime")
        source.publishObjectClassAttributes(participant_class, {federate_name_attr, current_time_attr})
        sink.subscribeObjectClassAttributes(participant_class, {federate_name_attr, current_time_attr})
        participant = source.registerObjectInstance(participant_class, "EventSourceFederate-time-state")
        _drain(source, sink)
        source.updateAttributeValues(
            participant,
            {federate_name_attr: b"EventSourceFederate", current_time_attr: b"0"},
            b"proto2025-time-participant-state",
        )
        _drain(source, sink)
        lifecycle.append("time-participant-state-reflected")

        event_interaction = source.getInteractionClassHandle("HLAinteractionRoot.Proto2025.TimeMgmtTest.EmitEvent")
        event_id = source.getParameterHandle(event_interaction, "EventId")
        sequence_number = source.getParameterHandle(event_interaction, "SequenceNumber")
        source.publishInteractionClass(event_interaction)
        sink.subscribeInteractionClass(event_interaction)
        factory = source.getTimeFactory()
        source.enableTimeRegulation(factory.makeInterval(1.0))
        sink.enableTimeConstrained()
        _drain(source, sink)
        lifecycle.append("time-management-enabled")

        source.sendInteraction(
            event_interaction,
            {event_id: b"evt-002", sequence_number: b"2"},
            b"event-2",
            factory.makeTime(3.0),
        )
        source.sendInteraction(
            event_interaction,
            {event_id: b"evt-001", sequence_number: b"1"},
            b"event-1",
            factory.makeTime(2.0),
        )
        source.timeAdvanceRequestAvailable(factory.makeTime(5.0))
        sink.nextMessageRequest(factory.makeTime(10.0))
        _drain(source, sink)
        sink.nextMessageRequestAvailable(factory.makeTime(10.0))
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
                rti.resignFederationExecution(ResignAction.DELETE_OBJECTS)
            except Exception:
                pass
        try:
            source.destroyFederationExecution(federation_name)
            lifecycle.append("federation-destroyed")
        except Exception:
            pass
        for rti in (sink, source):
            try:
                rti.disconnect()
            except Exception:
                pass
