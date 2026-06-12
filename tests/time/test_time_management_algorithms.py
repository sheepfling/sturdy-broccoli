from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from hla2010.time import HLAinteger64Interval, HLAinteger64Time, HLAinteger64TimeFactory
from hla2010_rti_backend_common.time_management import (
    FQR,
    NMR,
    NMRA,
    TAR,
    TARA,
    TimeAdvanceRequestState,
    TSOMessage,
    TSOMessageQueue,
    compute_galt,
    compute_grant_decision,
    compute_lits,
    queued_tso_messages,
    valid_tso_lower_bound,
)


@dataclass
class DummyFederate:
    handle: object = field(default_factory=object)
    current_time: HLAinteger64Time = field(default_factory=lambda: HLAinteger64Time(0))
    lookahead: HLAinteger64Interval = field(default_factory=lambda: HLAinteger64Interval(0))
    time_regulation_enabled: bool = False
    time_constrained_enabled: bool = False
    pending_time_advance: TimeAdvanceRequestState | None = None
    tso_message_heap: list[object] = field(default_factory=list)
    resigned: bool = False
    deleted: bool = False


@dataclass
class DummyMessage:
    timestamp: HLAinteger64Time
    recipient: object
    sequence: int
    retracted: bool = False


@dataclass
class DummyFederation:
    federates: dict[str, DummyFederate] = field(default_factory=dict)
    tso_messages: list[DummyMessage] = field(default_factory=list)
    time_factory: HLAinteger64TimeFactory = field(default_factory=HLAinteger64TimeFactory)


def _regulating_federate(
    *,
    current_time: int,
    lookahead: int,
    pending: int | None = None,
    time_constrained_enabled: bool = False,
) -> DummyFederate:
    fed = DummyFederate(
        current_time=HLAinteger64Time(current_time),
        lookahead=HLAinteger64Interval(lookahead),
        time_regulation_enabled=True,
        time_constrained_enabled=time_constrained_enabled,
    )
    if pending is not None:
        fed.pending_time_advance = TimeAdvanceRequestState(TAR, HLAinteger64Time(pending))
    return fed


def _target_federate(*, time_constrained_enabled: bool = True) -> DummyFederate:
    return DummyFederate(time_constrained_enabled=time_constrained_enabled)


def _federation(*pairs: tuple[str, DummyFederate]) -> DummyFederation:
    return DummyFederation(federates={name: federate for name, federate in pairs})


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_message_queue_enqueues_filters_and_lists_deliverable_messages_through_boundary():
    target = object()
    other = object()
    queue = TSOMessageQueue()
    queue.enqueue(TSOMessage(HLAinteger64Time(5), sender="sender", recipient=target, sequence=3))
    queue.enqueue(TSOMessage(HLAinteger64Time(2), sender="sender", recipient=other, sequence=1))
    queue.enqueue(TSOMessage(HLAinteger64Time(5), sender="sender", recipient=target, sequence=1))
    queue.enqueue(TSOMessage(HLAinteger64Time(4), sender="sender", recipient=target, sequence=2))

    assert [
        (message.timestamp, message.sequence)
        for message in queue.list_deliverable_through(recipient=target, boundary=HLAinteger64Time(5))
    ] == [
        (HLAinteger64Time(4), 2),
        (HLAinteger64Time(5), 1),
        (HLAinteger64Time(5), 3),
    ]
    assert queue.peek_deliverable(recipient=target, boundary=HLAinteger64Time(5)).sequence == 2


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_message_queue_retracts_before_delivery_and_rejects_retraction_after_delivery():
    target = object()
    queue = TSOMessageQueue(
        [
            TSOMessage(HLAinteger64Time(3), sender="sender", recipient=target, sequence=1, retraction_handle="r1"),
            TSOMessage(HLAinteger64Time(4), sender="sender", recipient=target, sequence=2, retraction_handle="r2"),
        ]
    )

    assert queue.retract("r1") is True
    assert queue.retract("r1") is False
    assert [message.sequence for message in queue.active_messages(target)] == [2]

    delivered = queue.pop_deliverable_through(recipient=target, boundary=HLAinteger64Time(4))
    assert [message.sequence for message in delivered] == [2]
    assert delivered[0].delivered is True
    assert queue.retract("r2") is False
    assert queue.active_messages(target) == ()


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_message_queue_pop_supports_exclusive_boundary_and_earliest_only_modes():
    target = object()
    queue = TSOMessageQueue(
        [
            TSOMessage(HLAinteger64Time(3), sender="sender", recipient=target, sequence=1),
            TSOMessage(HLAinteger64Time(5), sender="sender", recipient=target, sequence=2),
            TSOMessage(HLAinteger64Time(5), sender="sender", recipient=target, sequence=3),
            TSOMessage(HLAinteger64Time(7), sender="sender", recipient=target, sequence=4),
        ]
    )

    first = queue.pop_deliverable_through(
        recipient=target,
        boundary=HLAinteger64Time(5),
        inclusive=False,
        earliest_only=True,
    )
    assert [message.sequence for message in first] == [1]

    equal_boundary = queue.pop_deliverable_through(
        recipient=target,
        boundary=HLAinteger64Time(5),
        earliest_only=True,
    )
    assert [message.sequence for message in equal_boundary] == [2, 3]
    assert [message.sequence for message in queue.active_messages(target)] == [4]


@pytest.mark.requirements("HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001")
def test_tso_message_queue_matches_recipient_handles_and_ignores_delivered_messages():
    recipient = DummyFederate()
    other = DummyFederate()
    delivered = TSOMessage(HLAinteger64Time(1), sender="sender", recipient=recipient.handle, sequence=1, delivered=True)
    queue = TSOMessageQueue(
        [
            delivered,
            TSOMessage(HLAinteger64Time(2), sender="sender", recipient=other.handle, sequence=2),
            TSOMessage(HLAinteger64Time(3), sender="sender", recipient=recipient.handle, sequence=3),
        ]
    )

    assert [message.sequence for message in queue.active_messages(recipient)] == [3]


@pytest.mark.requirements("HLA1516.1-TM-8.16-QUERYGALT-TEST-001")
def test_compute_galt_returns_invalid_without_regulating_contributors_and_minimum_of_other_regulators():
    target = _target_federate()
    federation = _federation(("target", target))

    empty = compute_galt(federation, target)
    assert empty.time_is_valid is False
    assert empty.time is None

    left = _regulating_federate(current_time=4, lookahead=2)
    right = _regulating_federate(current_time=8, lookahead=1, pending=3)
    target = _target_federate()
    federation = _federation(("left", left), ("right", right), ("target", target))

    galt = compute_galt(federation, target)
    assert galt.time_is_valid is True
    assert galt.time == HLAinteger64Time(4)


@pytest.mark.requirements("HLA1516.1-TM-8.1.4-LOWERBOUND-TEST-001")
def test_non_regulating_federates_do_not_contribute_valid_tso_lower_bounds():
    fed = DummyFederate(
        current_time=HLAinteger64Time(4),
        lookahead=HLAinteger64Interval(2),
        time_regulation_enabled=False,
    )

    assert valid_tso_lower_bound(fed) is None

    target = _target_federate()
    federation = _federation(("fed", fed), ("target", target))
    assert compute_galt(federation, target).time_is_valid is False


@pytest.mark.requirements("HLA1516.1-TM-8.16-QUERYGALT-TEST-001")
def test_compute_galt_excludes_querying_and_inactive_federates():
    target = _regulating_federate(current_time=1, lookahead=1)
    active = _regulating_federate(current_time=10, lookahead=2)
    resigned = _regulating_federate(current_time=0, lookahead=1)
    resigned.resigned = True
    deleted = _regulating_federate(current_time=0, lookahead=2)
    deleted.deleted = True
    federation = _federation(
        ("target", target),
        ("active", active),
        ("resigned", resigned),
        ("deleted", deleted),
    )

    galt = compute_galt(federation, target)

    assert galt.time_is_valid is True
    assert galt.time == HLAinteger64Time(12)

    self_included = compute_galt(federation, target, include_self=True)
    assert self_included.time == HLAinteger64Time(2)


@pytest.mark.requirements("HLA1516.1-TM-8.16-QUERYGALT-TEST-001")
def test_negative_lookahead_is_rejected_before_galt_contribution():
    target = _target_federate()
    bad = _regulating_federate(current_time=4, lookahead=-1)
    federation = _federation(("bad", bad), ("target", target))

    with pytest.raises(ValueError, match="lookahead must be non-negative"):
        compute_galt(federation, target)


@pytest.mark.requirements("HLA1516.1-TM-8.16-QUERYGALT-TEST-001", "HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_compute_lits_can_be_invalid_without_galt_or_messages_and_valid_from_messages_without_galt():
    target = _target_federate()
    federation = _federation(("target", target))

    empty = compute_lits(federation, target)
    assert empty.time_is_valid is False
    assert empty.time is None

    federation.tso_messages.append(DummyMessage(HLAinteger64Time(7), target.handle, 1))
    with_message = compute_lits(federation, target)
    assert with_message.time_is_valid is True
    assert with_message.time == HLAinteger64Time(7)


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_compute_lits_uses_galt_and_queued_timestamp_order_messages():
    left = _regulating_federate(current_time=4, lookahead=2)
    right = _regulating_federate(current_time=8, lookahead=1, pending=3)
    target = _target_federate()
    federation = _federation(("left", left), ("right", right), ("target", target))

    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(5), target_handle, 2),
            DummyMessage(HLAinteger64Time(2), target_handle, 1),
            DummyMessage(HLAinteger64Time(7), object(), 3),
        ]
    )
    target.tso_message_heap.append(DummyMessage(HLAinteger64Time(3), target_handle, 0))

    lits = compute_lits(federation, target)

    assert lits.time_is_valid is True
    assert lits.time == HLAinteger64Time(2)


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_compute_lits_can_be_galt_only_and_takes_minimum_of_galt_and_messages():
    left = _regulating_federate(current_time=4, lookahead=2)
    target = _target_federate()
    federation = _federation(("left", left), ("target", target))

    galt_only = compute_lits(federation, target)
    assert galt_only.time_is_valid is True
    assert galt_only.time == HLAinteger64Time(6)

    federation.tso_messages.append(DummyMessage(HLAinteger64Time(8), target.handle, 1))
    assert compute_lits(federation, target).time == HLAinteger64Time(6)

    federation.tso_messages.append(DummyMessage(HLAinteger64Time(3), target.handle, 2))
    assert compute_lits(federation, target).time == HLAinteger64Time(3)


@pytest.mark.requirements("HLA1516.1-TM-8.18-QUERYLITS-TEST-001")
def test_queued_tso_messages_ignore_retracted_and_wrong_recipient_messages_and_preserve_sequence_order():
    target = _target_federate()
    other = _target_federate()
    federation = _federation(("target", target), ("other", other))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(5), target_handle, 3),
            DummyMessage(HLAinteger64Time(2), other.handle, 1),
            DummyMessage(HLAinteger64Time(5), target_handle, 1),
            DummyMessage(HLAinteger64Time(1), target_handle, 0, retracted=True),
            DummyMessage(HLAinteger64Time(5), target_handle, 2),
        ]
    )
    target.tso_message_heap.extend(
        [
            DummyMessage(HLAinteger64Time(4), other.handle, 4),
            DummyMessage(HLAinteger64Time(4), target_handle, 4),
        ]
    )

    queued = queued_tso_messages(federation, target)

    assert [(msg.timestamp, msg.sequence) for msg in queued] == [
        (HLAinteger64Time(4), 4),
        (HLAinteger64Time(5), 1),
        (HLAinteger64Time(5), 2),
        (HLAinteger64Time(5), 3),
    ]
    assert compute_lits(federation, target).time == HLAinteger64Time(4)


@pytest.mark.requirements(
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
)
def test_next_message_request_strictly_rejects_equal_galt_while_available_request_can_grant_it():
    sender = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))
    target_handle = target.handle
    federation.tso_messages.append(DummyMessage(HLAinteger64Time(5), target_handle, 1))

    strict = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMR, HLAinteger64Time(5)),
    )
    inclusive = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMRA, HLAinteger64Time(5)),
    )

    assert strict.can_grant is False
    assert strict.reason == "requested time is beyond GALT"
    assert inclusive.can_grant is True
    assert inclusive.grant_time == HLAinteger64Time(5)
    assert inclusive.optimistic_time == HLAinteger64Time(5)
    assert [msg.sequence for msg in inclusive.deliverable_messages] == [1]


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
)
def test_zero_lookahead_keeps_the_bound_at_the_current_or_pending_time_and_strict_modes_reject_equal_galt():
    sender = _regulating_federate(current_time=4, lookahead=0)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))

    assert valid_tso_lower_bound(sender) == HLAinteger64Time(4)
    assert compute_galt(federation, target).time == HLAinteger64Time(4)

    target_handle = target.handle
    federation.tso_messages.append(DummyMessage(HLAinteger64Time(4), target_handle, 1))
    strict_tar = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(4)),
    )
    strict_nmr = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMR, HLAinteger64Time(4)),
    )

    assert strict_tar.can_grant is False
    assert strict_nmr.can_grant is False
    assert strict_tar.reason == "requested time is beyond GALT"
    assert strict_nmr.reason == "requested time is beyond GALT"

    available_tar = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TARA, HLAinteger64Time(4)),
    )
    available_nmr = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMRA, HLAinteger64Time(4)),
    )

    assert available_tar.can_grant is True
    assert available_tar.grant_time == HLAinteger64Time(4)
    assert available_nmr.can_grant is True
    assert available_nmr.grant_time == HLAinteger64Time(4)


@pytest.mark.requirements("HLA1516.1-TM-8.19-MODIFYLOOKAHEAD-TEST-001")
def test_zero_lookahead_pending_time_advance_shifts_the_lower_bound_to_the_pending_request_time():
    fed = DummyFederate(
        current_time=HLAinteger64Time(4),
        lookahead=HLAinteger64Interval(0),
        time_regulation_enabled=True,
        pending_time_advance=TimeAdvanceRequestState(TAR, HLAinteger64Time(10)),
    )

    assert valid_tso_lower_bound(fed) == HLAinteger64Time(4)


@pytest.mark.requirements("HLA1516.1-TM-8.19-MODIFYLOOKAHEAD-TEST-001")
def test_valid_tso_lower_bound_uses_pending_advance_base_for_lookahead():
    fed = DummyFederate(
        current_time=HLAinteger64Time(4),
        lookahead=HLAinteger64Interval(2),
        time_regulation_enabled=True,
    )

    assert valid_tso_lower_bound(fed) == HLAinteger64Time(6)

    fed.pending_time_advance = TimeAdvanceRequestState(TAR, HLAinteger64Time(10))
    assert valid_tso_lower_bound(fed) == HLAinteger64Time(6)

    fed.pending_time_advance = TimeAdvanceRequestState(TAR, HLAinteger64Time(2))
    assert valid_tso_lower_bound(fed) == HLAinteger64Time(4)


@pytest.mark.requirements("HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001")
def test_compute_grant_decision_rejects_unknown_modes_and_past_requested_times():
    target = DummyFederate(current_time=HLAinteger64Time(5), time_constrained_enabled=True)
    federation = _federation(("target", target))

    unknown = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState("badMode", HLAinteger64Time(6)),
    )
    past = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(4)),
    )

    assert unknown.can_grant is False
    assert unknown.reason == "unknown time advance mode: badMode"
    assert past.can_grant is False
    assert past.reason == "requested time is before current time"


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.9-TIMEADVANCEREQUESTAVAILABLE-TEST-001",
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
    "HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001",
)
@pytest.mark.parametrize(
    ("mode", "requested", "expected_can_grant", "expected_grant"),
    [
        (TAR, 4, True, 4),
        (TAR, 5, False, None),
        (TARA, 5, True, 5),
        (NMR, 4, True, 4),
        (NMR, 5, False, None),
        (NMRA, 5, True, 5),
        (FQR, 5, True, 5),
    ],
)
def test_compute_grant_decision_galt_boundary_matrix(mode, requested, expected_can_grant, expected_grant):
    regulator = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("regulator", regulator), ("target", target))

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(mode, HLAinteger64Time(requested)),
    )

    assert decision.can_grant is expected_can_grant
    if expected_grant is None:
        assert decision.grant_time is None
        assert decision.reason == "requested time is beyond GALT"
    else:
        assert decision.grant_time == HLAinteger64Time(expected_grant)


@pytest.mark.requirements("HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001")
def test_compute_grant_decision_no_galt_respects_non_regulated_grant_switch():
    target = DummyFederate(
        current_time=HLAinteger64Time(3),
        time_constrained_enabled=True,
    )
    federation = _federation(("target", target))

    enabled = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(10)),
        nrg_enabled=True,
    )
    disabled_future = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(10)),
        nrg_enabled=False,
    )
    disabled_current = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(3)),
        nrg_enabled=False,
    )

    assert enabled.can_grant is True
    assert enabled.grant_time == HLAinteger64Time(10)
    assert disabled_future.can_grant is False
    assert disabled_future.reason == "requested time is beyond GALT"
    assert disabled_current.can_grant is True
    assert disabled_current.grant_time == HLAinteger64Time(3)


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.9-TIMEADVANCEREQUESTAVAILABLE-TEST-001",
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
    "HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001",
)
@pytest.mark.parametrize(
    ("mode", "expected_grant", "expected_sequences"),
    [
        ("timeAdvanceRequest", 8, [1, 2]),
        ("timeAdvanceRequestAvailable", 8, [1, 2]),
        ("nextMessageRequest", 4, [1]),
        ("nextMessageRequestAvailable", 4, [1]),
        ("flushQueueRequest", 4, [1]),
    ],
)
def test_compute_grant_decision_accepts_python_and_hla_service_mode_names(mode, expected_grant, expected_sequences):
    regulator = _regulating_federate(current_time=12, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("regulator", regulator), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(4), target_handle, 1),
            DummyMessage(HLAinteger64Time(6), target_handle, 2),
            DummyMessage(HLAinteger64Time(9), target_handle, 3),
        ]
    )

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(mode, HLAinteger64Time(8)),
    )

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(expected_grant)
    assert [msg.sequence for msg in decision.deliverable_messages] == expected_sequences


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.9-TIMEADVANCEREQUESTAVAILABLE-TEST-001",
)
def test_compute_grant_decision_distinguishes_strict_and_inclusive_time_advance_requests():
    left = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("left", left), ("target", target))

    strict = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(5)),
    )
    inclusive = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TARA, HLAinteger64Time(5)),
    )

    assert strict.can_grant is False
    assert strict.reason == "requested time is beyond GALT"
    assert inclusive.can_grant is True
    assert inclusive.grant_time == HLAinteger64Time(5)
    assert inclusive.optimistic_time == HLAinteger64Time(5)


@pytest.mark.requirements(
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
)
def test_next_message_requests_deliver_equal_earliest_timestamp_group_only():
    sender = _regulating_federate(current_time=9, lookahead=2)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(6), target_handle, 3),
            DummyMessage(HLAinteger64Time(4), target_handle, 2),
            DummyMessage(HLAinteger64Time(4), target_handle, 1),
            DummyMessage(HLAinteger64Time(7), target_handle, 4),
        ]
    )

    strict = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMR, HLAinteger64Time(8)),
    )
    available = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMRA, HLAinteger64Time(8)),
    )

    assert strict.can_grant is True
    assert strict.grant_time == HLAinteger64Time(4)
    assert [msg.sequence for msg in strict.deliverable_messages] == [1, 2]
    assert available.can_grant is True
    assert available.grant_time == HLAinteger64Time(4)
    assert [msg.sequence for msg in available.deliverable_messages] == [1, 2]


@pytest.mark.requirements(
    "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
    "HLA1516.1-TM-8.9-TIMEADVANCEREQUESTAVAILABLE-TEST-001",
)
def test_time_advance_requests_deliver_all_messages_through_requested_time_when_galt_allows():
    sender = _regulating_federate(current_time=12, lookahead=2)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(6), target_handle, 2),
            DummyMessage(HLAinteger64Time(8), target_handle, 3),
            DummyMessage(HLAinteger64Time(5), target_handle, 1),
            DummyMessage(HLAinteger64Time(9), target_handle, 4),
        ]
    )

    strict = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(8)),
    )
    available = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TARA, HLAinteger64Time(8)),
    )

    assert strict.can_grant is True
    assert strict.grant_time == HLAinteger64Time(8)
    assert [msg.sequence for msg in strict.deliverable_messages] == [1, 2, 3]
    assert available.can_grant is True
    assert available.grant_time == HLAinteger64Time(8)
    assert [msg.sequence for msg in available.deliverable_messages] == [1, 2, 3]


@pytest.mark.requirements("HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001")
def test_time_advance_request_blocked_by_galt_does_not_deliver_pre_galt_messages():
    regulator = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("regulator", regulator), ("target", target))
    federation.tso_messages.append(DummyMessage(HLAinteger64Time(4), target.handle, 1))

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(TAR, HLAinteger64Time(6)),
    )

    assert decision.can_grant is False
    assert decision.deliverable_messages == ()
    assert decision.reason == "requested time is beyond GALT"


@pytest.mark.requirements("HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001")
def test_flush_queue_request_limited_by_galt_before_queued_messages_grants_without_delivery():
    regulator = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("regulator", regulator), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(6), target_handle, 1),
            DummyMessage(HLAinteger64Time(7), target_handle, 2),
        ]
    )

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(FQR, HLAinteger64Time(10)),
    )

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(5)
    assert decision.optimistic_time == HLAinteger64Time(6)
    assert decision.deliverable_messages == ()


@pytest.mark.requirements("HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001")
def test_flush_queue_request_delivers_messages_at_inclusive_galt_boundary():
    regulator = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("regulator", regulator), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(5), target_handle, 1),
            DummyMessage(HLAinteger64Time(6), target_handle, 2),
        ]
    )

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(FQR, HLAinteger64Time(10)),
    )

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(5)
    assert decision.optimistic_time == HLAinteger64Time(5)
    assert [msg.sequence for msg in decision.deliverable_messages] == [1]


@pytest.mark.requirements(
    "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
    "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
    "HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001",
)
def test_compute_grant_decision_next_message_request_uses_earliest_eligible_timestamp_order_message():
    sender = _regulating_federate(current_time=4, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(9), target_handle, 2),
            DummyMessage(HLAinteger64Time(3), target_handle, 1),
            DummyMessage(HLAinteger64Time(5), target_handle, 3),
        ]
    )

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMR, HLAinteger64Time(10)),
    )

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(3)
    assert decision.optimistic_time == HLAinteger64Time(3)
    assert [msg.timestamp for msg in decision.deliverable_messages] == [HLAinteger64Time(3)]

    available = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(NMRA, HLAinteger64Time(10)),
    )

    assert available.can_grant is True
    assert available.grant_time == HLAinteger64Time(3)
    assert available.optimistic_time == HLAinteger64Time(3)

    flush = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(FQR, HLAinteger64Time(10)),
    )
    assert flush.can_grant is True
    assert flush.grant_time == HLAinteger64Time(3)
    assert flush.optimistic_time == HLAinteger64Time(3)
    assert [msg.sequence for msg in flush.deliverable_messages] == [1]


@pytest.mark.requirements("HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001")
def test_flush_queue_request_does_not_deliver_messages_past_the_request_or_grant_boundary():
    sender = _regulating_federate(current_time=9, lookahead=1)
    target = _target_federate(time_constrained_enabled=True)
    federation = _federation(("sender", sender), ("target", target))
    target_handle = target.handle
    federation.tso_messages.extend(
        [
            DummyMessage(HLAinteger64Time(4), target_handle, 1),
            DummyMessage(HLAinteger64Time(7), target_handle, 2),
            DummyMessage(HLAinteger64Time(11), target_handle, 3),
        ]
    )

    decision = compute_grant_decision(
        federation,
        target,
        TimeAdvanceRequestState(FQR, HLAinteger64Time(8)),
    )

    assert decision.can_grant is True
    assert decision.grant_time == HLAinteger64Time(4)
    assert [msg.sequence for msg in decision.deliverable_messages] == [1]
