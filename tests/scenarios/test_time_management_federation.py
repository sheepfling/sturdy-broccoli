from __future__ import annotations

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.enums import CallbackModel, ResignAction
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador


def _drain(*rtis, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def _joined_group(name: str, count: int):
    engine = InMemoryRTIEngine()
    rtis = [rti_ambassador(engine=engine) for _ in range(count)]
    feds = [RecordingFederateAmbassador() for _ in range(count)]
    for rti, fed in zip(rtis, feds):
        rti.connect(fed, CallbackModel.HLA_EVOKED)
    rtis[0].create_federation_execution(name, "TargetRadarFOMmodule.xml")
    for index, rti in enumerate(rtis):
        rti.join_federation_execution(f"fed-{index}", f"type-{index}", name)
    return rtis, feds


def _track_interaction(rti):
    interaction = rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = rti.get_parameter_handle(interaction, "TrackId")
    return interaction, track_id


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.18-QUERYLITS-TEST-001",
)
def test_two_federate_regulated_constrained_exchange_and_simultaneous_timestamp_delivery():
    (sender, receiver), (_sender_fed, receiver_fed) = _joined_group("scenario-two-fed-time", 2)
    factory = sender.get_time_factory()
    interaction, track_id = _track_interaction(sender)
    sender.publish_interaction_class(interaction)
    receiver.subscribe_interaction_class(interaction)
    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    _drain(sender, receiver)

    sender.send_interaction(interaction, {track_id: b"b"}, b"seq-b", factory.make_time(2.0))
    sender.send_interaction(interaction, {track_id: b"a"}, b"seq-a", factory.make_time(2.0))
    sender.time_advance_request_available(factory.make_time(5.0))
    _drain(sender, receiver)

    assert receiver.query_lits().time == factory.make_time(2.0)
    receiver.next_message_request(factory.make_time(10.0))
    _drain(sender, receiver)

    delivered_tags = [record.args[2] for record in receiver_fed.callbacks_named("receiveInteraction")]
    assert delivered_tags[-2:] == [b"seq-b", b"seq-a"]
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(2.0)


@pytest.mark.requirements(
    "HLA1516.1-TM-8.16-QUERYGALT-TEST-001",
    "HLA1516.1-TM-8.18-QUERYLITS-TEST-001",
)
def test_three_federate_mixed_regulating_non_regulating_galt_and_resign():
    (left, right, observer), (_left_fed, _right_fed, _observer_fed) = _joined_group("scenario-three-fed-time", 3)
    factory = left.get_time_factory()
    left.enable_time_regulation(factory.make_interval(1.0))
    right.enable_time_regulation(factory.make_interval(3.0))
    observer.enable_time_constrained()
    _drain(left, right, observer)

    assert observer.query_galt().time == factory.make_time(1.0)
    left.time_advance_request_available(factory.make_time(5.0))
    _drain(left, right, observer)
    assert observer.query_galt().time == factory.make_time(3.0)

    right.resign_federation_execution(ResignAction.NO_ACTION)
    _drain(left, observer)
    assert observer.query_galt().time == factory.make_time(6.0)


@pytest.mark.requirements("HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001")
def test_scenario_fqr_grants_at_earliest_boundary_and_does_not_flush_later_messages():
    (sender, receiver), (_sender_fed, receiver_fed) = _joined_group("scenario-fqr-fed", 2)
    factory = sender.get_time_factory()
    interaction, track_id = _track_interaction(sender)
    sender.publish_interaction_class(interaction)
    receiver.subscribe_interaction_class(interaction)
    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    _drain(sender, receiver)

    sender.send_interaction(interaction, {track_id: b"first"}, b"first", factory.make_time(3.0))
    sender.send_interaction(interaction, {track_id: b"later"}, b"later", factory.make_time(4.0))
    sender.time_advance_request_available(factory.make_time(10.0))
    _drain(sender, receiver)

    receiver.flush_queue_request(factory.make_time(10.0))
    _drain(sender, receiver)

    delivered = [record.args[2] for record in receiver_fed.callbacks_named("receiveInteraction")]
    assert delivered == [b"first"]
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(3.0)

