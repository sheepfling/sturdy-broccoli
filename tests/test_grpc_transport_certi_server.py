from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.backends.grpc_transport import start_certi_grpc_server
from hla2010.enums import OrderType, ResignAction
from hla2010.real_rti import discover_certi_smoke_fom, launch_certi_rtig
from hla2010.rti import create_rti_ambassador
from hla2010.testing import (
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


def test_grpc_transport_can_host_certi_exchange_end_to_end():
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    left_server = right_server = None
    left = right = None
    try:
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=60901)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=60911)
        left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
        right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})

        left_fed = RecordingFederateAmbassador()
        right_fed = RecordingFederateAmbassador()
        federation_name = f"GrpcHostedCERTIFederation-{uuid.uuid4().hex[:8]}"
        config = TwoFederateExchangeConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            interaction_class_name="MsgR",
            parameter_name="MsgDataR",
            object_instance_name="GrpcHostedCERTIObject-1",
            attribute_payload=b"payload-r",
            attribute_tag=b"reflect-tag",
            interaction_payload=b"hello-r",
            interaction_tag=b"interaction-tag",
            enable_time_management=True,
            lookahead=HLAfloat64Interval(1.0),
            advance_time=HLAfloat64Time(8.0),
            timestamped_attribute_payload=b"payload-tso",
            timestamped_attribute_tag=b"reflect-tso",
            timestamped_attribute_time=HLAfloat64Time(5.0),
            timestamped_interaction_payload=b"hello-tso",
            timestamped_interaction_tag=b"interaction-tso",
            timestamped_interaction_time=HLAfloat64Time(6.0),
        )
        summary = run_two_federate_exchange_scenario(
            left,
            right,
            config=config,
            publisher_federate=left_fed,
            subscriber_federate=right_fed,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=left_fed,
            subscriber_federate=right_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        right.resign_federation_execution(ResignAction.NO_ACTION)
        left.resign_federation_execution(ResignAction.NO_ACTION)
        left.destroy_federation_execution(federation_name)
        right.disconnect()
        left.disconnect()
    finally:
        if right is not None:
            right.close()
        if left is not None:
            left.close()
        if right_server is not None:
            right_server.close()
        if left_server is not None:
            left_server.close()
        rtig.terminate()
