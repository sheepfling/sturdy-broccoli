from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Literal

import pytest

from hla.runtime.factory import create_rti_ambassador
from hla.transports.grpc.python_server import start_python_grpc_server
from hla.backends.inmemory import InMemoryRTIEngine

PythonRoute = Literal["python-direct", "python-grpc"]


@dataclass(frozen=True)
class RtiPair:
    left: Any
    right: Any


@dataclass(frozen=True)
class RtiGroup:
    members: tuple[Any, ...]


PYTHON_ROUTES: tuple[PythonRoute, ...] = ("python-direct", "python-grpc")


def python_route_param(route: PythonRoute):
    marks = [pytest.mark.requires_loopback_server] if route == "python-grpc" else []
    return pytest.param(route, id=route, marks=marks)


def python_route_params() -> list[object]:
    return [python_route_param(route) for route in PYTHON_ROUTES]


def _close_rti(rti: Any) -> None:
    try:
        rti.disconnect()
    except Exception:
        pass
    close = getattr(rti, "close", None)
    if callable(close):
        close()
    spawned_server = getattr(rti, "_verification_spawned_server", None)
    if spawned_server is not None:
        try:
            spawned_server.close()
        except Exception:
            pass


def _attach_spawn_hook(rti: Any, spawn: Any) -> Any:
    setattr(rti, "_verification_spawn_like", spawn)
    return rti


@contextmanager
def python_rti_pair(route: PythonRoute) -> Iterator[RtiPair]:
    with ExitStack() as stack:
        if route == "python-direct":
            engine = InMemoryRTIEngine()
            left = _attach_spawn_hook(create_rti_ambassador("python", engine=engine), lambda: create_rti_ambassador("python", engine=engine))
            right = _attach_spawn_hook(create_rti_ambassador("python", engine=engine), lambda: create_rti_ambassador("python", engine=engine))
            stack.callback(_close_rti, right)
            stack.callback(_close_rti, left)
            yield RtiPair(left=left, right=right)
            return
        if route == "python-grpc":
            engine = InMemoryRTIEngine()
            left_server = start_python_grpc_server(engine=engine)
            right_server = start_python_grpc_server(engine=engine)
            stack.callback(right_server.close)
            stack.callback(left_server.close)
            def _spawn_grpc() -> Any:
                server = start_python_grpc_server(engine=engine)
                member = create_rti_ambassador("certi", transport={"kind": "grpc", "target": server.target})
                setattr(member, "_verification_spawned_server", server)
                return member

            left = _attach_spawn_hook(
                create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target}),
                _spawn_grpc,
            )
            right = _attach_spawn_hook(
                create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target}),
                _spawn_grpc,
            )
            stack.callback(_close_rti, right)
            stack.callback(_close_rti, left)
            yield RtiPair(left=left, right=right)
            return
        raise ValueError(f"unsupported Python route: {route}")


@contextmanager
def python_single_rti(route: PythonRoute) -> Iterator[Any]:
    with python_rti_pair(route) as pair:
        yield pair.left


@contextmanager
def python_rti_group(route: PythonRoute, count: int) -> Iterator[RtiGroup]:
    with ExitStack() as stack:
        if route == "python-direct":
            engine = InMemoryRTIEngine()
            members = tuple(
                _attach_spawn_hook(create_rti_ambassador("python", engine=engine), lambda: create_rti_ambassador("python", engine=engine))
                for _ in range(count)
            )
            for member in reversed(members):
                stack.callback(_close_rti, member)
            yield RtiGroup(members=members)
            return
        if route == "python-grpc":
            engine = InMemoryRTIEngine()
            servers = tuple(start_python_grpc_server(engine=engine) for _ in range(count))
            for server in reversed(servers):
                stack.callback(server.close)
            def _spawn_grpc() -> Any:
                server = start_python_grpc_server(engine=engine)
                member = create_rti_ambassador("certi", transport={"kind": "grpc", "target": server.target})
                setattr(member, "_verification_spawned_server", server)
                return member

            members = tuple(
                _attach_spawn_hook(
                    create_rti_ambassador("certi", transport={"kind": "grpc", "target": server.target}),
                    _spawn_grpc,
                )
                for server in servers
            )
            for member in reversed(members):
                stack.callback(_close_rti, member)
            yield RtiGroup(members=members)
            return
        raise ValueError(f"unsupported Python route: {route}")
