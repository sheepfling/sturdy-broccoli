from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass

import pytest

from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_verification_harness.section8_matrix import (
    run_section8_early_timestamp_send_case,
    run_section8_state_services_case,
    section8_matrix_config,
)
from hla2010_rti_python import InMemoryRTIEngine
from hla2010_rti_transport_rest.rest_transport_host import start_python_rest_server

try:
    from hla2010_rti_transport_grpc.python_server import start_python_grpc_server
except ModuleNotFoundError:
    start_python_grpc_server = None


@dataclass(frozen=True)
class BackendCase:
    id: str
    loopback_required: bool = False


BACKEND_CASES = (
    BackendCase("python"),
    BackendCase("rest-hosted-python", loopback_required=True),
    BackendCase("grpc-hosted-python", loopback_required=True),
)


def _case_param(case: BackendCase):
    marks = [pytest.mark.requires_loopback_server] if case.loopback_required else []
    if case.id == "grpc-hosted-python" and start_python_grpc_server is None:
        marks.append(pytest.mark.skip(reason="grpc-hosted-python backend requires grpcio"))
    return pytest.param(case, id=case.id, marks=marks)


@pytest.fixture
def backend_pair(request):
    case: BackendCase = request.param
    with ExitStack() as stack:
        if case.id == "python":
            engine = InMemoryRTIEngine()
            left = create_rti_ambassador("python", engine=engine)
            right = create_rti_ambassador("python", engine=engine)
            yield case.id, left, right
            return
        if case.id == "rest-hosted-python":
            engine = InMemoryRTIEngine()
            left_server = start_python_rest_server(engine=engine)
            right_server = start_python_rest_server(engine=engine)
            stack.callback(right_server.close)
            stack.callback(left_server.close)
            left = create_rti_ambassador("python", transport={"kind": "rest", "base_url": left_server.base_url})
            right = create_rti_ambassador("python", transport={"kind": "rest", "base_url": right_server.base_url})
            yield case.id, left, right
            return
        if case.id == "grpc-hosted-python":
            if start_python_grpc_server is None:
                pytest.skip("grpc-hosted-python backend requires grpcio")
            engine = InMemoryRTIEngine()
            left_server = start_python_grpc_server(engine=engine)
            right_server = start_python_grpc_server(engine=engine)
            stack.callback(right_server.close)
            stack.callback(left_server.close)
            left = create_rti_ambassador("python", transport={"kind": "grpc", "target": left_server.target})
            right = create_rti_ambassador("python", transport={"kind": "grpc", "target": right_server.target})
            yield case.id, left, right
            return
        raise AssertionError(f"unexpected backend case {case.id}")


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_lookahead_backend_matrix_state_services(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"lookahead-state-{backend_id}-{time_factory_name}", time_factory_name)
    summary = run_section8_state_services_case(left, right, config=config)

    assert summary["initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_lookahead_backend_matrix_blocks_early_timestamped_send(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"lookahead-window-{backend_id}-{time_factory_name}", time_factory_name)
    summary = run_section8_early_timestamp_send_case(left, right, config=config)

    assert summary["publisher_initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead
    assert summary["update_error"] is not None
    assert summary["interaction_error"] is not None
