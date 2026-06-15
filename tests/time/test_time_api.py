from __future__ import annotations

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010.enums import CallbackModel
from hla2010.handles import MessageRetractionHandle
from hla2010.types import TimeQueryReturn
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from tests.requirement_marker_groups import (
    TM_ADVANCE_AND_GRANT_REQUIREMENTS,
    TM_REQUEST_RETRACTION_REQUIREMENTS,
    TM_TIME_QUERY_API_REQUIREMENTS,
)


def _drain(*rtis, rounds: int = 20) -> None:
    for _ in range(rounds):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def _joined_pair(name: str):
    engine = InMemoryRTIEngine()
    left = rti_ambassador(engine=engine)
    right = rti_ambassador(engine=engine)
    left_fed = RecordingFederateAmbassador()
    right_fed = RecordingFederateAmbassador()
    left.connect(left_fed, CallbackModel.HLA_EVOKED)
    right.connect(right_fed, CallbackModel.HLA_EVOKED)
    left.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    left.joinFederationExecution("left", "producer", name)
    right.joinFederationExecution("right", "consumer", name)
    return left, right, left_fed, right_fed


@pytest.mark.requirements(*TM_TIME_QUERY_API_REQUIREMENTS)
def test_time_query_api_reports_galt_lits_logical_time_and_lookahead():
    regulator, constrained, regulator_fed, constrained_fed = _joined_pair("time-api-query-fed")
    factory = regulator.getTimeFactory()

    assert regulator.queryLogicalTime() == factory.make_time(0.0)
    assert isinstance(constrained.queryGALT(), TimeQueryReturn)
    assert constrained.queryGALT().time_is_valid is False
    assert constrained.queryLITS().time_is_valid is False

    regulator.enableTimeRegulation(factory.make_interval(1.0))
    constrained.enableTimeConstrained()
    _drain(regulator, constrained)

    assert regulator_fed.last_callback("timeRegulationEnabled").args[0] == factory.make_time(0.0)
    assert constrained_fed.last_callback("timeConstrainedEnabled").args[0] == factory.make_time(0.0)
    assert regulator.queryLookahead() == factory.make_interval(1.0)
    assert constrained.queryGALT().time == factory.make_time(1.0)
    assert constrained.queryLITS().time == factory.make_time(1.0)


@pytest.mark.requirements(*TM_ADVANCE_AND_GRANT_REQUIREMENTS)
def test_time_advance_api_delivers_tso_callbacks_before_or_with_grants():
    sender, receiver, sender_fed, receiver_fed = _joined_pair("time-api-advance-fed")
    factory = sender.getTimeFactory()
    interaction = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = sender.getParameterHandle(interaction, "TrackId")
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    sender.sendInteraction(interaction, {track_id: b"early"}, b"early", factory.make_time(2.0))
    sender.sendInteraction(interaction, {track_id: b"late"}, b"late", factory.make_time(3.0))
    _drain(sender, receiver)
    assert not receiver_fed.callbacks_named("receiveInteraction")

    sender.timeAdvanceRequest(factory.make_time(4.0))
    _drain(sender, receiver)
    assert sender_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(4.0)

    receiver.nextMessageRequest(factory.make_time(10.0))
    _drain(sender, receiver)
    assert receiver_fed.callbacks_named("receiveInteraction")[-1].args[2] == b"early"
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(2.0)

    receiver.nextMessageRequestAvailable(factory.make_time(10.0))
    _drain(sender, receiver)
    assert receiver_fed.callbacks_named("receiveInteraction")[-1].args[2] == b"late"
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(3.0)


@pytest.mark.requirements(*TM_REQUEST_RETRACTION_REQUIREMENTS)
def test_time_api_retraction_before_delivery_removes_queued_tso_callback():
    sender, receiver, _sender_fed, receiver_fed = _joined_pair("time-api-retract-fed")
    factory = sender.getTimeFactory()
    interaction = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = sender.getParameterHandle(interaction, "TrackId")
    sender.publishInteractionClass(interaction)
    receiver.subscribeInteractionClass(interaction)
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    _drain(sender, receiver)

    retraction = sender.sendInteraction(interaction, {track_id: b"gone"}, b"gone", factory.make_time(2.0))
    assert retraction is not None
    assert isinstance(retraction.handle, MessageRetractionHandle)
    sender.retract(retraction.handle)
    sender.timeAdvanceRequest(factory.make_time(4.0))
    receiver.timeAdvanceRequestAvailable(factory.make_time(5.0))
    _drain(sender, receiver)

    assert not receiver_fed.callbacks_named("receiveInteraction")
    assert receiver_fed.last_callback("timeAdvanceGrant").args[0] == factory.make_time(5.0)
