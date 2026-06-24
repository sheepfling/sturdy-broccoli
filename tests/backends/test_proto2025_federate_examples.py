from __future__ import annotations

import uuid
from collections.abc import Mapping

import pytest
from hla.backends.inmemory import InMemoryRTIEngine, rti_ambassador
from hla.fom.proto2025 import scenario_fom_paths
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction


class ExampleReceiver(NullFederateAmbassador):
    def __init__(self) -> None:
        self.discoveries: list[tuple[object, object, str, tuple[object, ...]]] = []
        self.reflections: list[tuple[object, Mapping[object, bytes], bytes, object, object, tuple[object, ...]]] = []
        self.interactions: list[tuple[object, Mapping[object, bytes], bytes, object, object, tuple[object, ...]]] = []

    def discover_object_instance(self, the_object, the_object_class, object_name, *extra):  # noqa: ANN001
        self.discoveries.append((the_object, the_object_class, object_name, extra))

    def reflect_attribute_values(self, the_object, the_attributes, user_supplied_tag, sent_ordering, transport, *extra):  # noqa: ANN001
        self.reflections.append((the_object, the_attributes, user_supplied_tag, sent_ordering, transport, extra))

    def receive_interaction(self, interaction_class, parameters, user_supplied_tag, sent_ordering, transport, *extra):  # noqa: ANN001
        self.interactions.append((interaction_class, parameters, user_supplied_tag, sent_ordering, transport, extra))


def _drain(*rtis: object) -> None:
    for _ in range(10):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


@pytest.mark.requirements(
    "HLA2025-FR-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-007",
    "HLA2025-FI-008",
)
@pytest.mark.parametrize(
    (
        "scenario",
        "object_class_name",
        "attribute_payloads",
        "interaction_class_name",
        "parameter_payloads",
    ),
    [
        (
            "message-test",
            "HLAobjectRoot.Proto2025.MessageTest.TestSuite",
            {"SuiteId": b"EchoProtocolSmoke", "Name": b"Echo Protocol Smoke", "Version": b"0.1"},
            "HLAinteractionRoot.Proto2025.MessageTest.SendStimulus",
            {"TestCaseId": b"case-valid-echo", "StepId": b"step-001", "DestinationEndpointId": b"sut-1", "MessageType": b"EchoRequest"},
        ),
        (
            "space-lite",
            "HLAobjectRoot.Proto2025.SpaceLite.ReferenceFrame",
            {"FrameName": b"EarthMJ2000Eq", "ParentFrameName": b"SolarSystemBarycentric", "StateTime": b"100000000"},
            "HLAinteractionRoot.Proto2025.SpaceLite.ReferenceFrameAnnouncement",
            {"FrameName": b"EarthMJ2000Eq", "ParentFrameName": b"SolarSystemBarycentric", "ProducerFederate": b"ReferenceFrame"},
        ),
        (
            "time-mgmt-test",
            "HLAobjectRoot.Proto2025.TimeMgmtTest.TimeParticipant",
            {"FederateName": b"Producer", "IsTimeConstrained": b"true", "IsTimeRegulating": b"true"},
            "HLAinteractionRoot.Proto2025.TimeMgmtTest.EmitReceiveOrderEvent",
            {"EventId": b"evt-001", "SourceId": b"source-1", "SequenceNumber": b"1", "PayloadHash": b"abc123"},
        ),
    ],
)
def test_proto2025_2025_example_foms_drive_two_federate_exchange(
    scenario: str,
    object_class_name: str,
    attribute_payloads: Mapping[str, bytes],
    interaction_class_name: str,
    parameter_payloads: Mapping[str, bytes],
) -> None:
    engine = InMemoryRTIEngine()
    publisher = rti_ambassador(engine=engine)
    subscriber = rti_ambassador(engine=engine)
    publisher_fed = ExampleReceiver()
    subscriber_fed = ExampleReceiver()
    federation_name = f"proto2025-{scenario}-{uuid.uuid4().hex[:8]}"

    publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
    publisher.create_federation_execution(federation_name, scenario_fom_paths(scenario))
    publisher.join_federation_execution("publisher", "ExamplePublisher", federation_name)
    subscriber.join_federation_execution("subscriber", "ExampleSubscriber", federation_name)

    object_class = publisher.get_object_class_handle(object_class_name)
    attributes = {
        attribute_name: publisher.get_attribute_handle(object_class, attribute_name)
        for attribute_name in attribute_payloads
    }
    publisher.publish_object_class_attributes(object_class, set(attributes.values()))
    subscriber.subscribe_object_class_attributes(object_class, set(attributes.values()))

    object_handle = publisher.register_object_instance(object_class, f"{scenario}-object")
    _drain(publisher, subscriber)
    assert subscriber_fed.discoveries[-1][2] == f"{scenario}-object"

    publisher.update_attribute_values(
        object_handle,
        {attributes[name]: payload for name, payload in attribute_payloads.items()},
        b"proto2025-example-update",
    )
    _drain(publisher, subscriber)
    reflected = subscriber_fed.reflections[-1]
    assert reflected[0] == object_handle
    assert reflected[2] == b"proto2025-example-update"
    assert reflected[3] is OrderType.RECEIVE
    assert reflected[1] == {attributes[name]: payload for name, payload in attribute_payloads.items()}

    interaction_class = publisher.get_interaction_class_handle(interaction_class_name)
    parameters = {
        parameter_name: publisher.get_parameter_handle(interaction_class, parameter_name)
        for parameter_name in parameter_payloads
    }
    publisher.publish_interaction_class(interaction_class)
    subscriber.subscribe_interaction_class(interaction_class)
    publisher.send_interaction(
        interaction_class,
        {parameters[name]: payload for name, payload in parameter_payloads.items()},
        b"proto2025-example-interaction",
    )
    _drain(publisher, subscriber)
    received = subscriber_fed.interactions[-1]
    assert received[0] == interaction_class
    assert received[1] == {parameters[name]: payload for name, payload in parameter_payloads.items()}
    assert received[2] == b"proto2025-example-interaction"

    publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    publisher.destroy_federation_execution(federation_name)
