from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Literal

import pytest

from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_rti_transport_grpc.python_server import start_python_grpc_server
from hla2010_rti_python import InMemoryRTIEngine

PythonRoute = Literal["python-direct", "python-grpc"]


@dataclass(frozen=True)
class RtiPair:
    left: Any
    right: Any


@dataclass(frozen=True)
class RtiTriple:
    left: Any
    middle: Any
    right: Any


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


@contextmanager
def python_rti_pair(route: PythonRoute) -> Iterator[RtiPair]:
    with ExitStack() as stack:
        if route == "python-direct":
            engine = InMemoryRTIEngine()
            left = create_rti_ambassador("python", engine=engine)
            right = create_rti_ambassador("python", engine=engine)
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
            left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
            right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})
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
def python_rti_triple(route: PythonRoute) -> Iterator[RtiTriple]:
    with ExitStack() as stack:
        if route == "python-direct":
            engine = InMemoryRTIEngine()
            left = create_rti_ambassador("python", engine=engine)
            middle = create_rti_ambassador("python", engine=engine)
            right = create_rti_ambassador("python", engine=engine)
            stack.callback(_close_rti, right)
            stack.callback(_close_rti, middle)
            stack.callback(_close_rti, left)
            yield RtiTriple(left=left, middle=middle, right=right)
            return
        if route == "python-grpc":
            engine = InMemoryRTIEngine()
            left_server = start_python_grpc_server(engine=engine)
            middle_server = start_python_grpc_server(engine=engine)
            right_server = start_python_grpc_server(engine=engine)
            stack.callback(right_server.close)
            stack.callback(middle_server.close)
            stack.callback(left_server.close)
            left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
            middle = create_rti_ambassador("certi", transport={"kind": "grpc", "target": middle_server.target})
            right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})
            stack.callback(_close_rti, right)
            stack.callback(_close_rti, middle)
            stack.callback(_close_rti, left)
            yield RtiTriple(left=left, middle=middle, right=right)
            return
        raise ValueError(f"unsupported Python route: {route}")
