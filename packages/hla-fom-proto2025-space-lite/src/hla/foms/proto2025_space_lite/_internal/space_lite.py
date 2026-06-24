"""Repo-internal executable showcase scenario for Proto2025 SpaceLite."""
from __future__ import annotations

from collections.abc import Callable
import uuid
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516_2025.enums import CallbackModel, ResignAction
from hla.runtime.rti1516_2025_factory import create_rti_ambassador
from hla.fom.proto2025 import scenario_fom_paths


def _drain(*rtis: object, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def run_space_lite_showcase(*, rti_factory: Callable[[], Any] | None = None) -> dict[str, Any]:
    """Run the package-owned SpaceLite showcase scenario."""

    spawn_rti = rti_factory or create_rti_ambassador
    publisher = spawn_rti()
    subscriber = spawn_rti()
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    foms = scenario_fom_paths("space-lite")
    federation_name = f"Proto2025SpaceLiteShowcase-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []

    publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
    lifecycle.append("connected")
    try:
        publisher.createFederationExecution(federation_name, foms)
        lifecycle.append("federation-created")
        publisher.joinFederationExecution("ReferenceFrameFederate", "ShowcasePublisher", federation_name)
        subscriber.joinFederationExecution("SensorFederate", "ShowcaseSubscriber", federation_name)
        lifecycle.append("joined")

        object_class = publisher.getObjectClassHandle("HLAobjectRoot.Proto2025.SpaceLite.ReferenceFrame")
        attributes = {
            attribute_name: publisher.getAttributeHandle(object_class, attribute_name)
            for attribute_name in ("FrameName", "ParentFrameName", "StateTime")
        }
        publisher.publishObjectClassAttributes(object_class, set(attributes.values()))
        subscriber.subscribeObjectClassAttributes(object_class, set(attributes.values()))
        lifecycle.append("object-publication-subscription-ready")

        object_handle = publisher.registerObjectInstance(object_class, "EarthMJ2000EqFrame")
        _drain(publisher, subscriber)
        publisher.updateAttributeValues(
            object_handle,
            {
                attributes["FrameName"]: b"EarthMJ2000Eq",
                attributes["ParentFrameName"]: b"SolarSystemBarycentric",
                attributes["StateTime"]: b"100000000",
            },
            b"proto2025-showcase-object-update",
        )
        _drain(publisher, subscriber)
        lifecycle.append("object-update-reflected")

        interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.Proto2025.SpaceLite.ReferenceFrameAnnouncement")
        parameters = {
            parameter_name: publisher.getParameterHandle(interaction_class, parameter_name)
            for parameter_name in ("FrameName", "ParentFrameName", "ProducerFederate")
        }
        publisher.publishInteractionClass(interaction_class)
        subscriber.subscribeInteractionClass(interaction_class)
        publisher.sendInteraction(
            interaction_class,
            {
                parameters["FrameName"]: b"EarthMJ2000Eq",
                parameters["ParentFrameName"]: b"SolarSystemBarycentric",
                parameters["ProducerFederate"]: b"ReferenceFrameFederate",
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
            "scenario": "space-lite",
            "status": "lifecycle-green" if object_reflected and interaction_received else "failed",
            "federation_name": federation_name,
            "fom_modules": [Path(path).name for path in foms],
            "federates": ["ReferenceFrameFederate", "SensorFederate"],
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.Proto2025.SpaceLite.ReferenceFrame",
            "object_instance": "EarthMJ2000EqFrame",
            "interaction_class": "HLAinteractionRoot.Proto2025.SpaceLite.ReferenceFrameAnnouncement",
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(interactions),
            "callbacks": len(publisher_fed.records) + len(subscriber_fed.records),
            "key_outcome": "reference frame state reflected and frame announcement delivered",
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
