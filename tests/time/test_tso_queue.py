from __future__ import annotations

import pytest

from hla2010.time import HLAinteger64Time
from hla2010.time_management import TSOMessage, TSOMessageQueue

from tests.time._time_algorithm_support import DummyFederate


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_queue_orders_by_timestamp_then_sequence_and_filters_recipient():
    target = DummyFederate()
    other = DummyFederate()
    queue = TSOMessageQueue(
        [
            TSOMessage(HLAinteger64Time(5), "sender", target.handle, 3),
            TSOMessage(HLAinteger64Time(2), "sender", other.handle, 1),
            TSOMessage(HLAinteger64Time(5), "sender", target.handle, 1),
            TSOMessage(HLAinteger64Time(4), "sender", target.handle, 2),
        ]
    )

    assert [
        (message.timestamp, message.sequence)
        for message in queue.list_deliverable_through(recipient=target, boundary=HLAinteger64Time(5))
    ] == [
        (HLAinteger64Time(4), 2),
        (HLAinteger64Time(5), 1),
        (HLAinteger64Time(5), 3),
    ]


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_queue_retracts_before_delivery_and_rejects_after_delivery():
    target = DummyFederate()
    queue = TSOMessageQueue(
        [
            TSOMessage(HLAinteger64Time(3), "sender", target.handle, 1, retraction_handle="r1"),
            TSOMessage(HLAinteger64Time(4), "sender", target.handle, 2, retraction_handle="r2"),
        ]
    )

    assert queue.retract("r1") is True
    assert queue.retract("r1") is False
    assert [message.sequence for message in queue.active_messages(target)] == [2]

    delivered = queue.pop_deliverable_through(recipient=target, boundary=HLAinteger64Time(4))
    assert [message.sequence for message in delivered] == [2]
    assert delivered[0].delivered is True
    assert queue.retract("r2") is False


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_queue_supports_exclusive_boundaries_and_earliest_only_groups():
    target = DummyFederate()
    queue = TSOMessageQueue(
        [
            TSOMessage(HLAinteger64Time(3), "sender", target.handle, 1),
            TSOMessage(HLAinteger64Time(5), "sender", target.handle, 2),
            TSOMessage(HLAinteger64Time(5), "sender", target.handle, 3),
            TSOMessage(HLAinteger64Time(7), "sender", target.handle, 4),
        ]
    )

    first = queue.pop_deliverable_through(
        recipient=target,
        boundary=HLAinteger64Time(5),
        inclusive=False,
        earliest_only=True,
    )
    equal = queue.pop_deliverable_through(
        recipient=target,
        boundary=HLAinteger64Time(5),
        earliest_only=True,
    )

    assert [message.sequence for message in first] == [1]
    assert [message.sequence for message in equal] == [2, 3]

