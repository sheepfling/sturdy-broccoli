from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass

import pytest

from hla2010.backends.grpc_transport.python_server import start_python_grpc_server
from hla2010.exceptions import InvalidLogicalTime
from hla2010.rti import create_rti_ambassador
from hla2010_verification_harness.section8_matrix import (
    cleanup_section8_pair,
    connect_section8_pair,
    drain_callbacks,
    run_section8_state_services_case,
    section8_matrix_config,
)
from hla2010.time import HLAfloat64Time, HLAinteger64Time
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
    _publisher_fed, _subscriber_fed = connect_section8_pair(left, right, config=config)
    try:
        object_class = left.get_object_class_handle(config.object_class_name)
        attribute = left.get_attribute_handle(object_class, config.attribute_name)
        interaction = left.get_interaction_class_handle(config.order_interaction_class_name)
        parameter = left.get_parameter_handle(interaction, config.order_parameter_name)

        left.publish_object_class_attributes(object_class, {attribute})
        right.subscribe_object_class_attributes(object_class, {attribute})
        left.publish_interaction_class(interaction)
        right.subscribe_interaction_class(interaction)

        left.enable_time_regulation(config.lookahead)
        right.enable_time_constrained()
        drain_callbacks(left, right)

        assert left.query_lookahead() == config.lookahead
        left.modify_lookahead(config.modified_lookahead)
        assert left.query_lookahead() == config.modified_lookahead

        instance = left.register_object_instance(object_class, config.object_instance_name)
        zero_time = HLAinteger64Time(0) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(0.0)

        with pytest.raises(InvalidLogicalTime):
            left.update_attribute_values(
                instance,
                {attribute: config.first_payload},
                config.first_tag,
                zero_time,
            )
        with pytest.raises(InvalidLogicalTime):
            left.send_interaction(
                interaction,
                {parameter: config.second_payload},
                config.second_tag,
                zero_time,
            )
    finally:
        cleanup_section8_pair(left, right, config.federation_name)
