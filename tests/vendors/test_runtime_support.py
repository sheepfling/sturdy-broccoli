from __future__ import annotations

from dataclasses import dataclass, field

from hla2010.enums import ResignAction

from tests.vendors.runtime_support import cleanup_federation, close_all, reserve_udp_pair, terminate_all, udp_port_pair


@dataclass
class _FakeRTI:
    calls: list[tuple[str, object]] = field(default_factory=list)

    def resign_federation_execution(self, action: ResignAction) -> None:
        self.calls.append(("resign", action))

    def destroy_federation_execution(self, federation_name: str) -> None:
        self.calls.append(("destroy", federation_name))

    def disconnect(self) -> None:
        self.calls.append(("disconnect", None))

    def close(self) -> None:
        self.calls.append(("close", None))

    def terminate(self) -> None:
        self.calls.append(("terminate", None))


def test_reserve_udp_pair_returns_distinct_ports_and_releases_them() -> None:
    with reserve_udp_pair() as lease:
        assert len(lease.ports) == 2
        assert lease.ports[0] != lease.ports[1]

    assert lease._sockets == ()


def test_cleanup_federation_runs_best_effort_sequence() -> None:
    owner = _FakeRTI()
    peer = _FakeRTI()

    cleanup_federation(
        "fed",
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((peer, ResignAction.NO_ACTION),),
        disconnect_rtis=(peer, owner),
    )

    assert owner.calls == [
        ("resign", ResignAction.DELETE_OBJECTS),
        ("destroy", "fed"),
        ("disconnect", None),
    ]
    assert peer.calls == [
        ("resign", ResignAction.NO_ACTION),
        ("disconnect", None),
    ]


def test_close_all_and_terminate_all_ignore_none() -> None:
    closable = _FakeRTI()
    terminable = _FakeRTI()

    close_all(None, closable)
    terminate_all(None, terminable)

    assert closable.calls == [("close", None)]
    assert terminable.calls == [("terminate", None)]


def test_udp_port_pair_can_wrap_static_base() -> None:
    with udp_port_pair(61234) as ports:
        assert ports == (61234, 61235)
