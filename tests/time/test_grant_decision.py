from __future__ import annotations

import pytest

from hla2010.time import HLAinteger64Time
from hla2010_rti_backend_common.time_management import FQR, NMR, NMRA, TAR, TARA, TimeAdvanceRequestState, compute_grant_decision

from tests.requirement_marker_groups import (
    TM_ADVANCE_AND_GRANT_REQUIREMENTS,
    TM_FLUSH_QUEUE_REQUIREMENTS,
    TM_NEXT_MESSAGE_REQUIREMENTS,
    TM_TIME_ADVANCE_REQUEST_REQUIREMENTS,
)
from tests.time._time_algorithm_support import DummyFederate, DummyMessage, federation, regulating_federate, target_federate


@pytest.mark.requirements(*TM_TIME_ADVANCE_REQUEST_REQUIREMENTS)
def test_grant_decision_rejects_unknown_mode_and_past_request():
    target = DummyFederate(current_time=HLAinteger64Time(5), time_constrained_enabled=True)
    fed = federation(("target", target))

    unknown = compute_grant_decision(fed, target, TimeAdvanceRequestState("badMode", HLAinteger64Time(6)))
    past = compute_grant_decision(fed, target, TimeAdvanceRequestState(TAR, HLAinteger64Time(4)))

    assert unknown.can_grant is False
    assert unknown.reason == "unknown time advance mode: badMode"
    assert past.can_grant is False
    assert past.reason == "requested time is before current time"


@pytest.mark.requirements(*TM_ADVANCE_AND_GRANT_REQUIREMENTS)
@pytest.mark.parametrize(
    ("mode", "requested", "can_grant", "grant"),
    [(TAR, 5, False, None), (TARA, 5, True, 5), (NMR, 5, False, None), (NMRA, 5, True, 5), (FQR, 5, True, 5)],
)
def test_grant_decision_strict_vs_inclusive_galt_boundary(mode, requested, can_grant, grant):
    regulator = regulating_federate(current_time=4, lookahead=1)
    target = target_federate(time_constrained_enabled=True)
    fed = federation(("regulator", regulator), ("target", target))

    decision = compute_grant_decision(fed, target, TimeAdvanceRequestState(mode, HLAinteger64Time(requested)))

    assert decision.can_grant is can_grant
    assert decision.grant_time == (None if grant is None else HLAinteger64Time(grant))


@pytest.mark.requirements(*TM_TIME_ADVANCE_REQUEST_REQUIREMENTS)
def test_grant_decision_no_galt_obeys_nrg_switch():
    target = DummyFederate(current_time=HLAinteger64Time(3), time_constrained_enabled=True)
    fed = federation(("target", target))

    enabled = compute_grant_decision(fed, target, TimeAdvanceRequestState(TAR, HLAinteger64Time(10)), nrg_enabled=True)
    disabled = compute_grant_decision(fed, target, TimeAdvanceRequestState(TAR, HLAinteger64Time(10)), nrg_enabled=False)

    assert enabled.can_grant is True
    assert disabled.can_grant is False


@pytest.mark.requirements(*TM_NEXT_MESSAGE_REQUIREMENTS)
def test_grant_decision_next_message_delivers_equal_earliest_group_only():
    regulator = regulating_federate(current_time=12, lookahead=1)
    target = target_federate(time_constrained_enabled=True)
    fed = federation(("regulator", regulator), ("target", target))
    fed.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(4), target.handle, 2),
            DummyMessage(HLAinteger64Time(4), target.handle, 1),
            DummyMessage(HLAinteger64Time(6), target.handle, 3),
        ]
    )

    decision = compute_grant_decision(fed, target, TimeAdvanceRequestState(NMR, HLAinteger64Time(8)))

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(4)
    assert [message.sequence for message in decision.deliverable_messages] == [1, 2]


@pytest.mark.requirements(*TM_FLUSH_QUEUE_REQUIREMENTS)
def test_grant_decision_fqr_delivers_only_through_computed_grant_boundary():
    regulator = regulating_federate(current_time=4, lookahead=1)
    target = target_federate(time_constrained_enabled=True)
    fed = federation(("regulator", regulator), ("target", target))
    fed.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(5), target.handle, 1),
            DummyMessage(HLAinteger64Time(6), target.handle, 2),
        ]
    )

    decision = compute_grant_decision(fed, target, TimeAdvanceRequestState(FQR, HLAinteger64Time(10)))

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(5)
    assert [message.sequence for message in decision.deliverable_messages] == [1]
