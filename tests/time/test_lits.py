from __future__ import annotations

import pytest

from hla2010.time import HLAinteger64Time
from hla2010_rti_backend_common.time_management import compute_lits, queued_tso_messages

from tests.time._time_algorithm_support import DummyMessage, federation, regulating_federate, target_federate


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_compute_lits_returns_invalid_without_galt_or_queued_tso_and_message_only_when_no_galt():
    target = target_federate()
    fed = federation(("target", target))

    empty = compute_lits(fed, target)
    assert empty.time_is_valid is False
    assert empty.time is None

    fed.tso_messages.append(DummyMessage(HLAinteger64Time(7), target.handle, 1))
    message_only = compute_lits(fed, target)
    assert message_only.time_is_valid is True
    assert message_only.time == HLAinteger64Time(7)


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_compute_lits_is_minimum_of_valid_galt_and_recipient_tso_queue():
    regulator = regulating_federate(current_time=4, lookahead=2)
    target = target_federate()
    fed = federation(("regulator", regulator), ("target", target))

    assert compute_lits(fed, target).time == HLAinteger64Time(6)
    fed.tso_messages.append(DummyMessage(HLAinteger64Time(8), target.handle, 1))
    assert compute_lits(fed, target).time == HLAinteger64Time(6)
    fed.tso_messages.append(DummyMessage(HLAinteger64Time(3), target.handle, 2))
    assert compute_lits(fed, target).time == HLAinteger64Time(3)


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_lits_queue_filtering_ignores_retracted_delivered_and_wrong_recipient_messages():
    target = target_federate()
    other = target_federate()
    fed = federation(("target", target), ("other", other))
    fed.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(1), target.handle, 1, retracted=True),
            DummyMessage(HLAinteger64Time(2), target.handle, 2, delivered=True),
            DummyMessage(HLAinteger64Time(3), other.handle, 3),
            DummyMessage(HLAinteger64Time(4), target.handle, 4),
        ]
    )

    queued = queued_tso_messages(fed, target)

    assert [message.sequence for message in queued] == [4]
    assert compute_lits(fed, target).time == HLAinteger64Time(4)
