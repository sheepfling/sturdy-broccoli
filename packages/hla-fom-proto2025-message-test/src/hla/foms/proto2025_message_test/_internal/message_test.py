"""Repo-internal executable showcase scenario for Proto2025 MessageTest."""
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


def run_message_test_showcase() -> dict[str, Any]:
    """Run the package-owned MessageTest showcase scenario."""

    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("message-test")
    federation_name = f"Proto2025MessageTestShowcase-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        publisher.create_federation_execution(federation_name, foms)
        lifecycle.append("federation-created")
        publisher.join_federation_execution("TestDesignFederate", "ShowcasePublisher", federation_name)
        subscriber.join_federation_execution("TestExecutionFederate", "ShowcaseSubscriber", federation_name)
        lifecycle.append("joined")

        object_class = publisher.get_object_class_handle("HLAobjectRoot.Proto2025.MessageTest.TestSuite")
        attributes = {
            attribute_name: publisher.get_attribute_handle(object_class, attribute_name)
            for attribute_name in ("SuiteId", "Name", "Version")
        }
        publisher.publish_object_class_attributes(object_class, set(attributes.values()))
        subscriber.subscribe_object_class_attributes(object_class, set(attributes.values()))
        lifecycle.append("object-publication-subscription-ready")

        object_handle = publisher.register_object_instance(object_class, "EchoProtocolSmokeSuite")
        _drain(publisher, subscriber)
        publisher.update_attribute_values(
            object_handle,
            {
                attributes["SuiteId"]: b"EchoProtocolSmoke",
                attributes["Name"]: b"Echo Protocol Smoke",
                attributes["Version"]: b"0.1",
            },
            b"proto2025-showcase-object-update",
        )
        _drain(publisher, subscriber)
        lifecycle.append("object-update-reflected")

        interaction_class = publisher.get_interaction_class_handle("HLAinteractionRoot.Proto2025.MessageTest.SendStimulus")
        parameters = {
            parameter_name: publisher.get_parameter_handle(interaction_class, parameter_name)
            for parameter_name in ("TestCaseId", "StepId", "DestinationEndpointId", "MessageType")
        }
        publisher.publish_interaction_class(interaction_class)
        subscriber.subscribe_interaction_class(interaction_class)
        publisher.send_interaction(
            interaction_class,
            {
                parameters["TestCaseId"]: b"case-valid-echo",
                parameters["StepId"]: b"step-001",
                parameters["DestinationEndpointId"]: b"sut-1",
                parameters["MessageType"]: b"EchoRequest",
            },
            b"proto2025-showcase-interaction",
        )
        _drain(publisher, subscriber)
        lifecycle.append("interaction-received")

        discoveries = subscriber_fed.callbacks_named("discoverObjectInstance")
        reflections = subscriber_fed.callbacks_named("reflectAttributeValues")
        interactions = subscriber_fed.callbacks_named("receiveInteraction")
        object_reflected = bool(reflections) and reflections[-1].args[2] == b"proto2025-showcase-object-update"
        interaction_received = bool(interactions) and interactions[-1].args[2] == b"proto2025-showcase-interaction"
        return {
            "scenario": "message-test",
            "status": "lifecycle-green" if object_reflected and interaction_received else "failed",
            "federation_name": federation_name,
            "fom_modules": [Path(path).name for path in foms],
            "federates": ["TestDesignFederate", "TestExecutionFederate"],
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.Proto2025.MessageTest.TestSuite",
            "object_instance": "EchoProtocolSmokeSuite",
            "interaction_class": "HLAinteractionRoot.Proto2025.MessageTest.SendStimulus",
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(interactions),
            "callbacks": len(publisher_fed.records) + len(subscriber_fed.records),
            "key_outcome": "test suite state reflected and stimulus delivered",
            "execution_complete": object_reflected and interaction_received,
            "requirements_exercised": [
                "HLA2025-FR-001",
                "HLA2025-FR-003",
                "HLA2025-FR-004",
                "HLA2025-FI-001",
                "HLA2025-FI-008",
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
