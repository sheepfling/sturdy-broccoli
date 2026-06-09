from __future__ import annotations

from dataclasses import dataclass, field

from hla2010.time import HLAinteger64Interval, HLAinteger64Time, HLAinteger64TimeFactory
from hla2010.time_management import TimeAdvanceRequestState, TAR


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
    delivered: bool = False
    retraction_handle: object | None = None


@dataclass
class DummyFederation:
    federates: dict[str, DummyFederate] = field(default_factory=dict)
    tso_messages: list[DummyMessage] = field(default_factory=list)
    time_factory: HLAinteger64TimeFactory = field(default_factory=HLAinteger64TimeFactory)


def regulating_federate(
    *,
    current_time: int,
    lookahead: int,
    pending: int | None = None,
    time_constrained_enabled: bool = False,
) -> DummyFederate:
    federate = DummyFederate(
        current_time=HLAinteger64Time(current_time),
        lookahead=HLAinteger64Interval(lookahead),
        time_regulation_enabled=True,
        time_constrained_enabled=time_constrained_enabled,
    )
    if pending is not None:
        federate.pending_time_advance = TimeAdvanceRequestState(TAR, HLAinteger64Time(pending))
    return federate


def target_federate(*, time_constrained_enabled: bool = True) -> DummyFederate:
    return DummyFederate(time_constrained_enabled=time_constrained_enabled)


def federation(*pairs: tuple[str, DummyFederate]) -> DummyFederation:
    return DummyFederation(federates={name: federate for name, federate in pairs})

