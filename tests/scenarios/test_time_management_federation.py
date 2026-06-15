from __future__ import annotations

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010.enums import CallbackModel, ResignAction
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from tests.requirement_marker_groups import (
    TM_FLUSH_QUEUE_REQUIREMENTS,
    TM_THREE_FEDERATE_SCENARIO_REQUIREMENTS,
    TM_TWO_FEDERATE_SCENARIO_REQUIREMENTS,
)


def _drain(*rtis, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def _joined_group(name: str, count: int):
    engine = InMemoryRTIEngine()
    rtis = [rti_ambassador(engine=engine) for _ in range(count)]
    feds = [RecordingFederateAmbassador() for _ in range(count)]
    for rti, fed in zip(rtis, feds):
        rti.connect(fed, CallbackModel.HLA_EVOKED)
    rtis[0].createFederationExecution(name, "TargetRadarFOMmodule.xml")
    for index, rti in enumerate(rtis):
        rti.joinFederationExecution(f"fed-{index}", f"type-{index}", name)
    return rtis, feds


def _track_interaction(rti):
    interaction = rti.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = rti.getParameterHandle(interaction, "TrackId")
    return interaction, track_id


@pytest.mark.requirements(*TM_TWO_FEDERATE_SCENARIO_REQUIREMENTS)
def test_two_federate_regulated_constrained_exchange_and_simultaneous_timestamp_delivery():
    (sender, receiver), (_sender_fed, receiver_fed) = _joined_group("scenario-two-fed-time", 2)
    factory = sender.getTimeFactory()
    interaction, track_id = _track_interaction(sender)
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    sender.sendInteraction(interaction, {track_id: b"b"}, b"seq-b", factory.make_time(2.0))
    sender.sendInteraction(interaction, {track_id: b"a"}, b"seq-a", factory.make_time(2.0))
    sender.timeAdvanceRequestAvailable(factory.make_time(5.0))
    _drain(sender, receiver)

    assert receiver.queryLITS().time == factory.make_time(2.0)
    receiver.nextMessageRequest(factory.make_time(10.0))
    _drain(sender, receiver)

    delivered_tags = [record.args[2] for record in receiver_fed.callbacks_named("receiveInteraction")]
    assert delivered_tags[-2:] == [b"seq-b", b"seq-a"]
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(2.0)


@pytest.mark.requirements(*TM_THREE_FEDERATE_SCENARIO_REQUIREMENTS)
def test_three_federate_mixed_regulating_non_regulating_galt_and_resign():
    (left, right, observer), (_left_fed, _right_fed, _observer_fed) = _joined_group("scenario-three-fed-time", 3)
    factory = left.getTimeFactory()
    left.enableTimeRegulation(factory.make_interval(1.0))
    right.enableTimeRegulation(factory.make_interval(3.0))
    observer.enableTimeConstrained()
    _drain(left, right, observer)

    assert observer.queryGALT().time == factory.make_time(1.0)
    left.timeAdvanceRequestAvailable(factory.make_time(5.0))
    _drain(left, right, observer)
    assert observer.queryGALT().time == factory.make_time(3.0)

    right.resignFederationExecution(ResignAction.NO_ACTION)
    _drain(left, observer)
    assert observer.queryGALT().time == factory.make_time(6.0)


@pytest.mark.requirements(*TM_FLUSH_QUEUE_REQUIREMENTS)
def test_scenario_fqr_grants_at_earliest_boundary_and_does_not_flush_later_messages():
    (sender, receiver), (_sender_fed, receiver_fed) = _joined_group("scenario-fqr-fed", 2)
    factory = sender.getTimeFactory()
    interaction, track_id = _track_interaction(sender)
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    sender.sendInteraction(interaction, {track_id: b"first"}, b"first", factory.make_time(3.0))
    sender.sendInteraction(interaction, {track_id: b"later"}, b"later", factory.make_time(4.0))
    sender.timeAdvanceRequestAvailable(factory.make_time(10.0))
    _drain(sender, receiver)

    receiver.flushQueueRequest(factory.make_time(10.0))
    _drain(sender, receiver)

    delivered = [record.args[2] for record in receiver_fed.callbacks_named("receiveInteraction")]
    assert delivered == [b"first"]
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(3.0)
