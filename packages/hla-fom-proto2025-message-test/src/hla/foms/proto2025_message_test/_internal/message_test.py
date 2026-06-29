"""Repo-internal executable showcase scenario for Proto2025 MessageTest."""
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


def run_message_test_showcase(*, rti_factory: Callable[[], Any] | None = None) -> dict[str, Any]:
    """Run the package-owned MessageTest showcase scenario."""

    spawn_rti = rti_factory or create_rti_ambassador
    publisher = spawn_rti()
    subscriber = spawn_rti()
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("message-test")
    federation_name = f"Proto2025MessageTestShowcase-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        publisher.createFederationExecution(federation_name, foms)
        lifecycle.append("federation-created")
        publisher.joinFederationExecution("TestDesignFederate", "ShowcasePublisher", federation_name)
        subscriber.joinFederationExecution("TestExecutionFederate", "ShowcaseSubscriber", federation_name)
        lifecycle.append("joined")

        object_class = publisher.getObjectClassHandle("HLAobjectRoot.Proto2025.MessageTest.TestSuite")
        attributes = {
            attribute_name: publisher.getAttributeHandle(object_class, attribute_name)
            for attribute_name in ("SuiteId", "Name", "Version")
        }
        publisher.publishObjectClassAttributes(object_class, set(attributes.values()))
        subscriber.subscribeObjectClassAttributes(object_class, set(attributes.values()))
        lifecycle.append("object-publication-subscription-ready")

        object_handle = publisher.registerObjectInstance(object_class, "EchoProtocolSmokeSuite")
        _drain(publisher, subscriber)
        publisher.updateAttributeValues(
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

        interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.Proto2025.MessageTest.SendStimulus")
        parameters = {
            parameter_name: publisher.getParameterHandle(interaction_class, parameter_name)
            for parameter_name in ("TestCaseId", "StepId", "DestinationEndpointId", "MessageType")
        }
        publisher.publishInteractionClass(interaction_class)
        subscriber.subscribeInteractionClass(interaction_class)
        publisher.sendInteraction(
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
                rti.resignFederationExecution(ResignAction.DELETE_OBJECTS)
            except Exception:
                pass
        try:
            publisher.destroyFederationExecution(federation_name)
            lifecycle.append("federation-destroyed")
        except Exception:
            pass
        for rti in (subscriber, publisher):
            try:
                rti.disconnect()
            except Exception:
                pass
