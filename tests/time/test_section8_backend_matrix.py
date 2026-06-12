from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
import uuid

import pytest

from hla2010_rti_transport_grpc.python_server import start_python_grpc_server
from hla2010.enums import OrderType
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_verification_harness import (
    run_section8_available_and_flush_case,
    run_section8_available_and_retraction_case,
    run_section8_duplicate_enable_rejection_case,
    run_section8_early_timestamp_send_case,
    run_section8_order_override_case,
    run_section8_ordering_and_query_case,
    run_section8_time_bound_query_case,
    run_section8_request_retraction_case,
    run_section8_state_services_case,
    run_section8_tar_galt_boundary_case,
    section8_matrix_config,
)
from hla2010.types import TimeQueryReturn
from hla2010_rti_python import InMemoryRTIEngine
from hla2010_rti_transport_rest.rest_transport_host import start_python_rest_server


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
            left = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": left_server.base_url})
            right = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": right_server.base_url})
            yield case.id, left, right
            return
        if case.id == "grpc-hosted-python":
            engine = InMemoryRTIEngine()
            left_server = start_python_grpc_server(engine=engine)
            right_server = start_python_grpc_server(engine=engine)
            stack.callback(right_server.close)
            stack.callback(left_server.close)
            left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
            right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})
            yield case.id, left, right
            return
        raise AssertionError(f"unexpected backend case {case.id}")


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_state_services(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-state-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_state_services_case(left, right, config=config)

    assert summary["publisher_federate"].last_callback("timeRegulationEnabled") is not None
    assert summary["subscriber_federate"].last_callback("timeConstrainedEnabled") is not None
    assert summary["initial_time"].value == 0 or summary["initial_time"].value == 0.0
    assert summary["initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_logical_time_query(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-logical-time-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_state_services_case(left, right, config=config)

    assert summary["publisher_initial_time"].value == 0 or summary["publisher_initial_time"].value == 0.0
    assert summary["subscriber_initial_time"].value == 0 or summary["subscriber_initial_time"].value == 0.0


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_state_toggle_services(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-state-toggles-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_state_services_case(left, right, config=config)

    assert summary["initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_time_bound_queries(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-time-queries-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_time_bound_query_case(left, right, config=config)

    assert isinstance(summary["initial_galt"], TimeQueryReturn)
    assert isinstance(summary["initial_lits"], TimeQueryReturn)


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_ordering_and_queries(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-order-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_ordering_and_query_case(left, right, config=config)

    assert isinstance(summary["initial_galt"], TimeQueryReturn)
    assert isinstance(summary["initial_lits"], TimeQueryReturn)
    assert summary["sender_grant"].args[0] == config.sender_advance_time
    assert summary["first_receive"].args[1] == {summary["parameter"]: config.second_payload}
    assert summary["first_receive"].args[2] == config.second_tag
    assert summary["first_receive"].args[3] is OrderType.TIMESTAMP
    assert summary["first_receive"].args[5] == config.second_timestamp
    assert summary["first_grant"].args[0] == config.second_timestamp
    assert summary["second_receive"].args[1] == {summary["parameter"]: config.first_payload}
    assert summary["second_receive"].args[2] == config.first_tag
    assert summary["second_receive"].args[3] is OrderType.TIMESTAMP
    assert summary["second_receive"].args[5] == config.first_timestamp
    assert summary["second_grant"].args[0] == config.first_timestamp


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_available_and_flush_services(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-available-flush-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_available_and_flush_case(left, right, config=config)

    assert summary["available_grant"] is not None
    assert summary["flush_grant"] is not None
    assert summary["flushed_receive"] is not None


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_early_timestamp_send_rejection(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-early-send-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_early_timestamp_send_case(left, right, config=config)

    assert summary["publisher_initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead
    assert summary["update_error"] is not None
    assert summary["interaction_error"] is not None


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_available_and_retraction(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-available-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_available_and_retraction_case(left, right, config=config)

    assert summary["available_grant"] is not None
    assert summary["available_grant"].args[0] == config.receiver_window_time
    assert not summary["after_retract_callbacks"]
    assert summary["flush_grant"] is not None


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_order_override_services(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-order-override-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_order_override_case(left, right, config=config)

    assert summary["reflect"] is not None
    assert summary["reflect"].args[1] == {summary["attribute"]: config.first_payload}
    assert summary["reflect"].args[3] is OrderType.RECEIVE
    assert len(summary["reflect"].args) in {5, 6}
    assert summary["receive"] is not None
    assert summary["receive"].args[1] == {summary["parameter"]: config.second_payload}
    assert summary["receive"].args[3] is OrderType.RECEIVE
    assert len(summary["receive"].args) in {5, 6}


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_request_retraction_callback(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-request-retraction-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_request_retraction_case(left, right, config=config)

    assert summary["received"] is not None
    assert summary["received"].args[1] == {summary["parameter"]: config.first_payload}
    assert summary["received"].args[3] is OrderType.TIMESTAMP
    assert summary["request_retraction"] is not None
    assert summary["request_retraction"].args[0] == summary["sent"].handle


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_duplicate_enable_rejection(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-duplicate-enable-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_duplicate_enable_rejection_case(left, right, config=config)

    assert summary["regulation_error"] is not None
    assert summary["constrained_error"] is not None
    assert summary["final_regulation_callback_count"] == summary["initial_regulation_callback_count"]
    assert summary["final_constrained_callback_count"] == summary["initial_constrained_callback_count"]


@pytest.mark.parametrize("backend_pair", [_case_param(case) for case in BACKEND_CASES], indirect=True)
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_section8_backend_matrix_tar_galt_boundary(backend_pair, time_factory_name: str):
    backend_id, left, right = backend_pair
    config = section8_matrix_config(f"section8-tar-galt-{backend_id}-{uuid.uuid4().hex[:8]}", time_factory_name)
    summary = run_section8_tar_galt_boundary_case(left, right, config=config)

    assert summary["equal_galt"].time == config.receiver_window_time
    assert summary["grant"] is None
