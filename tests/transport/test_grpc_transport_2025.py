from __future__ import annotations

from concurrent import futures
import json
from pathlib import Path
import struct
import uuid

import grpc
import pytest
from hla.transports.common.transport import TransportError, TransportRequest
from hla.transports.grpc import GrpcTransport, GrpcTransportConfig
from hla.transports.grpc.client_2025 import decode_callback_request_details
from hla.transports.grpc.fedpro2025 import FederateAmbassador_2025_pb2 as callback_pb2
from hla.transports.grpc.fedpro2025 import HLA2025RTITransport_pb2_grpc as transport_pb2_grpc
from hla.transports.grpc.fedpro2025 import RTIambassador_2025_pb2 as rti_pb2
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2 as datatypes_pb2
from hla.transports.grpc.python_server_2025 import start_2025_grpc_server

pytestmark = pytest.mark.requires_loopback_server


class _FedPro2025Servicer(transport_pb2_grpc.HLA2025FedProGatewayServicer):
    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        request_kind = request.WhichOneof("callRequest")
        if request_kind in {
            "connectRequest",
            "connectWithCredentialsRequest",
            "connectWithConfigurationRequest",
            "connectWithConfigurationAndCredentialsRequest",
        }:
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "getFederateHandleRequest":
            return rti_pb2.CallResponse(getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(result=datatypes_pb2.FederateHandle(data=b"42")))
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName="RTIinternalError",
                details=f"Unsupported test call: {request_kind}",
            )
        )

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        return callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"7")))


def _start_server() -> tuple[grpc.Server, str]:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    transport_pb2_grpc.add_HLA2025FedProGatewayServicer_to_server(_FedPro2025Servicer(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    return server, f"127.0.0.1:{port}"


def test_fedpro2025_schema_imports_are_canonical():
    assert rti_pb2.CallRequest.DESCRIPTOR.full_name == "rti1516_2025.fedpro.CallRequest"
    assert callback_pb2.CallbackRequest.DESCRIPTOR.full_name == "rti1516_2025.fedpro.CallbackRequest"
    assert hasattr(transport_pb2_grpc, "HLA2025FedProGatewayStub")


def test_2025_grpc_transport_round_trips_typed_call_oneofs():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target, schema="rti1516_2025")).start()
        response = transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", "")))
        assert response.fields == ("",)

        handle = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))
        assert handle.fields == ("42",)
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_2025_grpc_transport_round_trips_typed_callback_oneofs():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target, schema="2025")).start()
        response = transport.request(TransportRequest(command="EVOKE"))

        assert response.fields[:2] == ("1", "TIME_ADVANCE_GRANT")
        assert response.fields[-1] == "7"
        assert response.fields[2] in {"HLAfloat64Time", "HLAinteger64Time"}
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_2025_transport_server_smoke_uses_the_new_schema_package():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        handle = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))
        assert handle.fields == ("42",)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-036",
    "HLA2025-FI-SVC-035",
    "HLA2025-FI-SVC-041",
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-058",
    "HLA2025-FI-SVC-059",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-061",
    "HLA2025-FI-SVC-062",
    "HLA2025-FI-SVC-123",
    "HLA2025-FI-SVC-125",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-exchange"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Exchange2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Publisher", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTarget-1"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTarget-1",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:313233", "7570646174652d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:313233",
            "7570646174652d746167",
            "1",
            "1",
        )
        assert (
            transport.request(
                TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, attribute, "TIMESTAMP"))
            ).fields
            == ()
        )
        assert server.servicer.default_attribute_order[(object_instance, attribute)] == datatypes_pb2.TIMESTAMP

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, f"{parameter}:545241434b2d31", "696e746572616374696f6e2d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:545241434b2d31",
            "696e746572616374696f6e2d746167",
            "1",
            "1",
        )
        assert transport.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(interaction_class, "TIMESTAMP"))).fields == ()
        assert server.servicer.interaction_order == (interaction_class, datatypes_pb2.TIMESTAMP)
        assert transport.request(TransportRequest(command="UNPUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        with pytest.raises(TransportError) as error:
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:6e6f2d7075626c697368", "61667465722d756e707562"),
                )
            )
        assert error.value.code == "ObjectClassNotPublished"

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "changeAttributeOrderTypeRequest",
            "changeInteractionOrderTypeRequest",
            "publishObjectClassAttributesRequest",
            "subscribeObjectClassAttributesRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassRequest",
            "unpublishObjectClassAttributesRequest",
            "updateAttributeValuesRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-035",
    "HLA2025-FI-SVC-065",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    federation_name = "fedpro-2025-discovery-remove-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Exchange2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025DiscoveryOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert subscriber.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DiscoverySubscriber", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTarget-Isolated-1"))
        ).fields[0]
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DISCOVER")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTarget-Isolated-1",
        )

        assert owner.request(
            TransportRequest(command="DELETE_OBJECT_INSTANCE", fields=(object_instance, "64656c6574652d69736f"))
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REMOVE_OBJECT_INSTANCE")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE",
            object_instance,
            "64656c6574652d69736f",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber is not None:
            subscriber.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-060",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_reflect_and_interaction_only_to_subscriber_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    federation_name = "fedpro-2025-reflect-interaction-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Exchange2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025ReflectOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert subscriber.request(
            TransportRequest(command="JOIN", fields=("FedPro2025ReflectSubscriber", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProReflectTarget-1"))
        ).fields[0]
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProReflectTarget-1",
        )

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES",
                fields=(object_instance, f"{attribute}:313233", "7265666c6563742d69736f"),
            )
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:313233",
            "7265666c6563742d69736f",
            "1",
            "1",
        )

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:545241434b2d49534f", "696e746572616374696f6e2d69736f"),
            )
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:545241434b2d49534f",
            "696e746572616374696f6e2d69736f",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber is not None:
            subscriber.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_delivers_timestamped_updates_and_interactions_to_all_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-tso-multi-subscriber"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025TSOOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert subscriber_a.request(TransportRequest(command="JOIN", fields=("FedPro2025TSO-A", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert subscriber_b.request(TransportRequest(command="JOIN", fields=("FedPro2025TSO-B", "TestFederate", federation_name))).fields == (
            "3",
            "HLAinteger64Time",
        )

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTSOTarget-1"))
        ).fields[0]
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:313233", "74736f2d7265666c656374", "HLAinteger64Time", "5"),
            )
        ).fields == ("1",)
        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:54534f", "74736f2d696e746572616374696f6e", "HLAinteger64Time", "5"),
            )
        ).fields == ("2",)
        assert server.servicer.queued_tso_callbacks.keys() == {"1", "2"}

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_a = subscriber_a.request(TransportRequest(command="EVOKE")).fields
        second_a = subscriber_a.request(TransportRequest(command="EVOKE")).fields
        grant_a = subscriber_a.request(TransportRequest(command="EVOKE")).fields
        assert first_a == (
            "1",
            "REFLECT_TSO",
            object_instance,
            f"{attribute}:313233",
            "74736f2d7265666c656374",
            "2",
            "1",
            "HLAinteger64Time",
            "5",
            "2",
        )
        assert second_a == (
            "1",
            "INTERACTION_TSO",
            interaction_class,
            f"{parameter}:54534f",
            "74736f2d696e746572616374696f6e",
            "2",
            "1",
            "HLAinteger64Time",
            "5",
            "2",
        )
        assert grant_a == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        second_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        grant_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        assert first_b == first_a
        assert second_b == second_a
        assert grant_b == grant_a

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_holds_tso_for_lagging_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-tso-split-subscriber-time"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025SplitOwner", "TestFederate", federation_name))).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(TransportRequest(command="JOIN", fields=("FedPro2025Split-A", "TestFederate", federation_name))).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(TransportRequest(command="JOIN", fields=("FedPro2025Split-B", "TestFederate", federation_name))).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = owner.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSplitTSO-1"))).fields[0]
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:313233", "73706c69742d7265666c656374", "HLAinteger64Time", "5"),
            )
        ).fields == ("1",)
        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:53504c4954", "73706c69742d696e746572616374696f6e", "HLAinteger64Time", "5"),
            )
        ).fields == ("2",)

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT_TSO")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION_TSO")

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-125",
    "HLA2025-BND-003",
)
def test_2025_transport_server_retracts_partially_delivered_tso_without_releasing_lagging_targets_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-partial-tso-retract"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025PartialOwner", "TestFederate", federation_name))).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(TransportRequest(command="JOIN", fields=("FedPro2025Partial-A", "TestFederate", federation_name))).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(TransportRequest(command="JOIN", fields=("FedPro2025Partial-B", "TestFederate", federation_name))).fields == ("3", "HLAinteger64Time")

        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        handle = owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:5041525449414c", "7061727469616c2d74736f", "HLAinteger64Time", "5"),
            )
        ).fields[0]

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RETRACT", fields=(handle,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", handle)

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        second_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        assert first_b[:2] != ("1", "INTERACTION_TSO")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5") in {first_b, second_b}

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-125",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_retraction_callbacks_for_disconnected_delivered_targets_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-disconnect-delivered-retract"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DisconnectRetractOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        subscriber_a_handle = subscriber_a.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DisconnectRetract-A", "TestFederate", federation_name))
        ).fields[0]
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DisconnectRetract-B", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        handle = owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:444953434f4e4e454354", "646973636f6e6e6563742d72657472616374", "HLAinteger64Time", "5"),
            )
        ).fields[0]

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert server.servicer.delivered_retraction_targets[handle] == frozenset({"2"})

        assert subscriber_a.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert subscriber_a_handle not in server.servicer.peer_federate_handles.values()

        assert owner.request(TransportRequest(command="RETRACT", fields=(handle,))).fields == ()
        assert handle not in server.servicer.delivered_retraction_targets or not server.servicer.delivered_retraction_targets[handle]
        assert all(
            callback.WhichOneof("callbackRequest") != "requestRetraction"
            for callback in server.servicer.callback_queue
        )

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        second_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        assert first_b[:2] != ("1", "INTERACTION_TSO")
        assert second_b[:2] != ("1", "INTERACTION_TSO")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5") in {first_b, second_b}

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "sendInteractionWithTimeRequest",
            "nextMessageRequestRequest",
            "retractRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_queued_plain_tso_for_disconnected_target_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    federation_name = "fedpro-2025-plain-tso-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025PlainTSODisconnectOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        subscriber_handle = subscriber.request(
            TransportRequest(command="JOIN", fields=("FedPro2025PlainTSODisconnectSubscriber", "TestFederate", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProPlainTSODisconnectTarget-1"))
        ).fields[0]
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProPlainTSODisconnectTarget-1",
        )

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:504c41494e2d54534f", "706c61696e2d74736f2d7265666c656374", "HLAinteger64Time", "5"),
            )
        ).fields == ("1",)
        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:504c41494e2d54534f", "706c61696e2d74736f2d696e746572616374696f6e", "HLAinteger64Time", "5"),
            )
        ).fields == ("2",)
        assert server.servicer.queued_tso_callbacks.keys() == {"1", "2"}

        assert subscriber.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert subscriber_handle not in server.servicer.peer_federate_handles.values()
        assert server.servicer.queued_tso_callbacks == {}

        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert server.servicer.queued_tso_callbacks == {}
        assert all(
            callback.WhichOneof("callbackRequest") not in {"reflectAttributeValuesWithTime", "receiveInteractionWithTime"}
            for callback in server.servicer.callback_queue
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "publishObjectClassAttributesRequest",
            "publishInteractionClassRequest",
            "subscribeObjectClassAttributesRequest",
            "subscribeInteractionClassRequest",
            "updateAttributeValuesWithTimeRequest",
            "sendInteractionWithTimeRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber is not None:
            subscriber.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    federation_name = "fedpro-2025-ddm-tso-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "RegionDDM2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DDMTSODisconnectOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        subscriber_handle = subscriber.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DDMTSODisconnectSubscriber", "TestFederate", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_region = subscriber.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert subscriber.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "5:15"))).fields == ()
        assert owner.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{subscriber_region}",))
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDDMTSODisconnectTarget-1"))
        ).fields[0]
        assert owner.request(
            TransportRequest(command="ASSOCIATE_REGIONS_FOR_UPDATES", fields=(object_instance, f"{attribute}|{publisher_region}"))
        ).fields == ()
        assert subscriber.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(object_class, f"{attribute}|{subscriber_region}", "1"),
            )
        ).fields == ()
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProDDMTSODisconnectTarget-1",
        )
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:44444d2d54534f", "64646d2d74736f2d7265666c656374", "HLAinteger64Time", "5"),
            )
        ).fields == ("1",)
        assert server.servicer.queued_tso_callbacks.keys() == {"1"}

        assert subscriber.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert subscriber_handle not in server.servicer.peer_federate_handles.values()
        assert server.servicer.queued_tso_callbacks == {}

        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert server.servicer.queued_tso_callbacks == {}
        assert all(
            callback.WhichOneof("callbackRequest") != "reflectAttributeValuesWithTime"
            for callback in server.servicer.callback_queue
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "publishObjectClassAttributesRequest",
            "subscribeObjectClassAttributesWithRegionsRequest",
            "associateRegionsForUpdatesRequest",
            "updateAttributeValuesWithTimeRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber is not None:
            subscriber.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_fans_out_post_delivery_retraction_to_all_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-tso-retraction-fanout"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025RetractOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert subscriber_a.request(TransportRequest(command="JOIN", fields=("FedPro2025Retract-A", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert subscriber_b.request(TransportRequest(command="JOIN", fields=("FedPro2025Retract-B", "TestFederate", federation_name))).fields == (
            "3",
            "HLAinteger64Time",
        )

        interaction_class = owner.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        handle = owner.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:52455452414354", "726574726163742d66616e6f7574", "HLAinteger64Time", "5"),
            )
        ).fields[0]
        assert handle == "1"

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "INTERACTION_TSO")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RETRACT", fields=(handle,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", handle)
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", handle)

        with pytest.raises(TransportError) as error:
            owner.request(TransportRequest(command="RETRACT", fields=(handle,)))
        assert error.value.code == "MessageCanNoLongerBeRetracted"

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-037",
    "HLA2025-FI-SVC-038",
    "HLA2025-FI-SVC-043",
    "HLA2025-FI-SVC-044",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_passive_and_universal_subscription_aliases_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-aliases"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Alias2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Aliases", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProAliasTarget-1"))).fields[0]

        passive_object_response = server.servicer.Call(
            rti_pb2.CallRequest(
                subscribeObjectClassAttributesPassivelyRequest=rti_pb2.SubscribeObjectClassAttributesPassivelyRequest(
                    objectClass=datatypes_pb2.ObjectClassHandle(data=object_class.encode("ascii")),
                    attributes=datatypes_pb2.AttributeHandleSet(
                        attributeHandle=[datatypes_pb2.AttributeHandle(data=attribute.encode("ascii"))]
                    ),
                )
            ),
            None,
        )
        assert passive_object_response.WhichOneof("callResponse") == "subscribeObjectClassAttributesPassivelyResponse"
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProAliasTarget-1",
        )

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:616c6961732d706f736974696f6e", "706173736976652d757064617465"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:616c6961732d706f736974696f6e",
            "706173736976652d757064617465",
            "1",
            "1",
        )

        passive_interaction_response = server.servicer.Call(
            rti_pb2.CallRequest(
                subscribeInteractionClassPassivelyRequest=rti_pb2.SubscribeInteractionClassPassivelyRequest(
                    interactionClass=datatypes_pb2.InteractionClassHandle(data=interaction_class.encode("ascii"))
                )
            ),
            None,
        )
        assert passive_interaction_response.WhichOneof("callResponse") == "subscribeInteractionClassPassivelyResponse"

        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, f"{parameter}:706173736976652d747261636b", "706173736976652d696e746572616374696f6e"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:706173736976652d747261636b",
            "706173736976652d696e746572616374696f6e",
            "1",
            "1",
        )

        universal_directed_response = server.servicer.Call(
            rti_pb2.CallRequest(
                subscribeObjectClassDirectedInteractionsUniversallyRequest=(
                    rti_pb2.SubscribeObjectClassDirectedInteractionsUniversallyRequest(
                        objectClass=datatypes_pb2.ObjectClassHandle(data=object_class.encode("ascii")),
                        interactionClasses=datatypes_pb2.InteractionClassHandleSet(
                            interactionClassHandle=[datatypes_pb2.InteractionClassHandle(data=interaction_class.encode("ascii"))]
                        ),
                    )
                )
            ),
            None,
        )
        assert universal_directed_response.WhichOneof("callResponse") == "subscribeObjectClassDirectedInteractionsUniversallyResponse"

        assert transport.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(
                        interaction_class,
                        object_instance,
                        f"{parameter}:756e6976657273616c2d747261636b",
                        "756e6976657273616c2d6469726563746564",
                    ),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:756e6976657273616c2d747261636b",
            "756e6976657273616c2d6469726563746564",
            "1",
            "1",
        )

        assert {
            "subscribeObjectClassAttributesPassivelyRequest",
            "subscribeInteractionClassPassivelyRequest",
            "subscribeObjectClassDirectedInteractionsUniversallyRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-FI-SVC-193", "HLA2025-FI-SVC-194", "HLA2025-BND-003")
def test_2025_transport_server_drains_multiple_callbacks_in_order_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-callback-queue"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "CallbackQueue2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025Callbacks", "TestFederate", federation_name))
        ).fields == (
            "1",
            "HLAinteger64Time",
        )

        interaction_class = transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, f"{parameter}:6669727374", "7175657565642d6f6e65"),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, f"{parameter}:7365636f6e64", "7175657565642d74776f"),
                )
            ).fields
            == ()
        )

        first = transport.request(TransportRequest(command="EVOKE_MANY", fields=("0.0", "0.0"))).fields
        assert first == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:6669727374",
            "7175657565642d6f6e65",
            "1",
            "1",
        )

        second = transport.request(TransportRequest(command="EVOKE")).fields
        assert second == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:7365636f6e64",
            "7175657565642d74776f",
            "1",
            "1",
        )
        trailing = transport.request(TransportRequest(command="EVOKE")).fields
        assert trailing == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-195",
    "HLA2025-FI-SVC-196",
    "HLA2025-BND-003",
)
def test_2025_transport_server_enable_disable_callbacks_controls_evoked_delivery_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-callback-control"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "CallbackControl2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CallbackControl", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        interaction_class = transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        server.servicer.callback_queue.clear()

        assert transport.request(TransportRequest(command="DISABLE_CALLBACKS")).fields == ()
        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:6f6e65", "7175657565642d6f6e65"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="ENABLE_CALLBACKS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:6f6e65",
            "7175657565642d6f6e65",
            "1",
            "1",
        )

        assert transport.request(TransportRequest(command="DISABLE_CALLBACKS")).fields == ()
        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:74776f", "7175657565642d74776f"))
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:7468726565", "7175657565642d7468726565"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="ENABLE_CALLBACKS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:74776f",
            "7175657565642d74776f",
            "1",
            "1",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:7468726565",
            "7175657565642d7468726565",
            "1",
            "1",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disableCallbacksRequest",
            "enableCallbacksRequest",
            "publishInteractionClassRequest",
            "sendInteractionRequest",
            "subscribeInteractionClassRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_routes_object_subscription_with_rate_aliases_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-rate-aliases"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "RateAlias2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025RateAliases", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        active_with_rate = server.servicer.Call(
            rti_pb2.CallRequest(
                subscribeObjectClassAttributesWithRateRequest=rti_pb2.SubscribeObjectClassAttributesWithRateRequest(
                    objectClass=datatypes_pb2.ObjectClassHandle(data=object_class.encode("ascii")),
                    attributes=datatypes_pb2.AttributeHandleSet(
                        attributeHandle=[datatypes_pb2.AttributeHandle(data=attribute.encode("ascii"))]
                    ),
                    updateRateDesignator="HLAdefaultUpdateRate",
                )
            ),
            None,
        )
        assert active_with_rate.WhichOneof("callResponse") == "subscribeObjectClassAttributesWithRateResponse"

        object_one = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProRateAliasTarget-1"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_one,
            object_class,
            "FedProRateAliasTarget-1",
        )

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_one, f"{attribute}:726174652d6f6e65", "726174652d6f6e652d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_one,
            f"{attribute}:726174652d6f6e65",
            "726174652d6f6e652d746167",
            "1",
            "1",
        )

        passive_with_rate = server.servicer.Call(
            rti_pb2.CallRequest(
                subscribeObjectClassAttributesPassivelyWithRateRequest=(
                    rti_pb2.SubscribeObjectClassAttributesPassivelyWithRateRequest(
                        objectClass=datatypes_pb2.ObjectClassHandle(data=object_class.encode("ascii")),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=attribute.encode("ascii"))]
                        ),
                        updateRateDesignator="rate-alias-passive",
                    )
                )
            ),
            None,
        )
        assert passive_with_rate.WhichOneof("callResponse") == "subscribeObjectClassAttributesPassivelyWithRateResponse"
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_one,
            object_class,
            "FedProRateAliasTarget-1",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_one,
            attribute,
            "rate-alias-passive",
        )

        object_two = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProRateAliasTarget-2"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_two,
            object_class,
            "FedProRateAliasTarget-2",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_two, f"{attribute}:726174652d74776f", "726174652d74776f2d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_two,
            f"{attribute}:726174652d74776f",
            "726174652d74776f2d746167",
            "1",
            "1",
        )

        assert {
            "subscribeObjectClassAttributesWithRateRequest",
            "subscribeObjectClassAttributesPassivelyWithRateRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_directed_interaction_exchange_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-directed"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Directed2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Directed", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedTarget-1"))).fields[0]
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:545241434b2d44", "64697265637465642d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:545241434b2d44",
            "64697265637465642d746167",
            "1",
            "1",
        )

        assert transport.request(TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:4e4f2d44454c4956455259", "756e737562"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []

        assert transport.request(TransportRequest(command="UNPUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class,))).fields == ()
        with pytest.raises(TransportError) as error:
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:455252", "756e707562"),
                )
            )
        assert error.value.code == "InteractionClassNotPublished"

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionRequest",
            "unsubscribeObjectClassDirectedInteractionsRequest",
            "unpublishObjectClassDirectedInteractionsRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_queues_timestamped_messages_and_retracts_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-tso-retraction"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Tso2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025TSO", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTsoTarget-1"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTsoTarget-1",
        )

        early_update = transport.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:6561726c79", "6561726c792d746167", "HLAinteger64Time", "10"),
            )
        ).fields[0]
        retracted_update = transport.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:64726f70", "64726f702d746167", "HLAinteger64Time", "15"),
            )
        ).fields[0]
        late_interaction = transport.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:6c617465", "6c6174652d746167", "HLAinteger64Time", "20"),
            )
        ).fields[0]
        assert (early_update, retracted_update, late_interaction) == ("1", "2", "3")

        assert transport.request(TransportRequest(command="RETRACT", fields=(retracted_update,))).fields == ()
        assert server.servicer.queued_tso_callbacks.keys() == {"1", "3"}

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "12"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT_TSO",
            object_instance,
            f"{attribute}:6561726c79",
            "6561726c792d746167",
            "2",
            "1",
            "HLAinteger64Time",
            "10",
            "2",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "12")

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "25"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION_TSO",
            interaction_class,
            f"{parameter}:6c617465",
            "6c6174652d746167",
            "2",
            "1",
            "HLAinteger64Time",
            "20",
            "2",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "25")
        assert transport.request(TransportRequest(command="RETRACT", fields=(early_update,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_RETRACTION",
            early_update,
        )
        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="RETRACT", fields=(early_update,)))
        assert error.value.code == "MessageCanNoLongerBeRetracted"

        assert {
            "updateAttributeValuesWithTimeRequest",
            "sendInteractionWithTimeRequest",
            "retractRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_object_management_support_callbacks_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-object-support"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "ObjectSupport2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025ObjectSupport", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSupportTarget-1"))
        ).fields[0]

        assert (
            transport.request(
                TransportRequest(
                    command="REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT",
                    fields=(object_instance, attribute, "696e7374616e63652d726571"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            object_instance,
            attribute,
            "696e7374616e63652d726571",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS",
                    fields=(object_class, attribute, "636c6173732d726571"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            object_instance,
            attribute,
            "636c6173732d726571",
        )

        assert transport.request(TransportRequest(command="LOCAL_DELETE_OBJECT_INSTANCE", fields=(object_instance,))).fields == ()
        assert transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(object_instance,))).fields == (
            "FedProSupportTarget-1",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "localDeleteObjectInstanceRequest",
            "requestClassAttributeValueUpdateRequest",
            "requestInstanceAttributeValueUpdateRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_attribute_value_update_requests_only_to_owner_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    requester = None
    federation_name = "fedpro-2025-object-support-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        requester = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert requester.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "ObjectSupport2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025ObjectOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert requester.request(
            TransportRequest(command="JOIN", fields=("FedPro2025ObjectRequester", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSupportIsolationTarget-1"))
        ).fields[0]

        assert requester.request(
            TransportRequest(
                command="REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT",
                fields=(object_instance, attribute, "696e7374616e63652d69736f"),
            )
        ).fields == ()
        assert requester.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "PROVIDE_ATTRIBUTE_VALUE_UPDATE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            object_instance,
            attribute,
            "696e7374616e63652d69736f",
        )

        assert requester.request(
            TransportRequest(
                command="REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS",
                fields=(object_class, attribute, "636c6173732d69736f"),
            )
        ).fields == ()
        assert requester.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "PROVIDE_ATTRIBUTE_VALUE_UPDATE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            object_instance,
            attribute,
            "636c6173732d69736f",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert requester.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert requester.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert requester.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if requester is not None:
            requester.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_attribute_value_update_requests_for_disconnected_owner_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    requester = None
    federation_name = "fedpro-2025-object-support-owner-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        requester = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert requester.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "ObjectSupport2025.xml"))
        ).fields == ()
        owner_handle = owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DeadOwner", "TestFederate", federation_name))
        ).fields[0]
        assert requester.request(
            TransportRequest(command="JOIN", fields=("FedPro2025LiveRequester", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSupportDeadOwner-1"))
        ).fields[0]
        assert server.servicer.attribute_owners[(object_instance, attribute)] == owner_handle

        assert owner.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert owner_handle not in server.servicer.peer_federate_handles.values()

        assert requester.request(
            TransportRequest(
                command="REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT",
                fields=(object_instance, attribute, "646561642d6f776e6572"),
            )
        ).fields == ()
        assert all(
            callback.WhichOneof("callbackRequest") != "provideAttributeValueUpdate"
            for callback in server.servicer.callback_queue
        )
        assert requester.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "PROVIDE_ATTRIBUTE_VALUE_UPDATE")

        assert requester.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert requester.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert requester.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "requestInstanceAttributeValueUpdateRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if requester is not None:
            requester.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-065",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-122",
    "HLA2025-BND-003",
)
def test_2025_transport_server_deletes_objects_and_queues_timed_removes_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-delete-tso"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DeleteTso2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DeleteTSO", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        object_class = transport.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))
        ).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        untimed_object = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDeleteNow-1"))
        ).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            untimed_object,
            object_class,
            "FedProDeleteNow-1",
        )
        assert transport.request(
            TransportRequest(command="DELETE_OBJECT_INSTANCE", fields=(untimed_object, "64656c6574652d6e6f77"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE",
            untimed_object,
            "64656c6574652d6e6f77",
            "1",
        )
        with pytest.raises(TransportError) as untimed_error:
            transport.request(
                TransportRequest(command="DELETE_OBJECT_INSTANCE", fields=(untimed_object, "64656c6574652d616761696e"))
            )
        assert untimed_error.value.code == "ObjectInstanceNotKnown"

        timed_object = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDeleteLater-1"))
        ).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            timed_object,
            object_class,
            "FedProDeleteLater-1",
        )
        timed_retraction = transport.request(
            TransportRequest(
                command="DELETE_OBJECT_INSTANCE_TIMESTAMP",
                fields=(timed_object, "64656c6574652d74736f", "HLAinteger64Time", "8"),
            )
        ).fields[0]
        with pytest.raises(TransportError) as timed_error:
            transport.request(
                TransportRequest(command="DELETE_OBJECT_INSTANCE", fields=(timed_object, "64656c6574652d6265666f72652d6772616e74"))
            )
        assert timed_error.value.code == "ObjectInstanceNotKnown"

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "10"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE_TSO",
            timed_object,
            "64656c6574652d74736f",
            "HLAinteger64Time",
            "8",
            "2",
            "2",
            "1",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "10",
        )
        assert transport.request(TransportRequest(command="RETRACT", fields=(timed_retraction,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_RETRACTION",
            timed_retraction,
        )
        with pytest.raises(TransportError) as retract_error:
            transport.request(TransportRequest(command="RETRACT", fields=(timed_retraction,)))
        assert retract_error.value.code == "MessageCanNoLongerBeRetracted"

        assert {
            "deleteObjectInstanceRequest",
            "deleteObjectInstanceWithTimeRequest",
            "timeAdvanceRequestRequest",
            "retractRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_directed_with_set_unsubscribe_and_unpublish_are_selective():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-directed-set"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedSelective2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025DirectedSet", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        track_report = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        alert_report = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation",),
            )
        ).fields[0]
        track_parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_report, "TrackId"))).fields[0]
        alert_federate = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(alert_report, "HLAfederate"))).fields[0]
        alert_service = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(alert_report, "HLAservice"))).fields[0]
        alert_serial = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(alert_report, "HLAserialNumber"))).fields[0]

        assert transport.request(
            TransportRequest(
                command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS",
                fields=(object_class, f"{track_report},{alert_report}"),
            )
        ).fields == ()
        assert transport.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS",
                fields=(object_class, f"{track_report},{alert_report}"),
            )
        ).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedSetTarget-1"))).fields[0]
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(track_report, object_instance, f"{track_parameter}:545241434b2d31", "747261636b2d6265666f7265"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            track_report,
            object_instance,
            f"{track_parameter}:545241434b2d31",
            "747261636b2d6265666f7265",
            "1",
            "1",
        )

        assert transport.request(
            TransportRequest(
                command="UNSUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS_WITH_SET",
                fields=(object_class, track_report),
            )
        ).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(track_report, object_instance, f"{track_parameter}:545241434b2d32", "747261636b2d6166746572"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(
                        alert_report,
                        object_instance,
                        f"{alert_federate}:31,{alert_service}:73657276696365,{alert_serial}:31",
                        "616c6572742d7374696c6c",
                    ),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            alert_report,
            object_instance,
            f"{alert_federate}:31,{alert_service}:73657276696365,{alert_serial}:31",
            "616c6572742d7374696c6c",
            "1",
            "1",
        )

        assert transport.request(
            TransportRequest(
                command="UNPUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS_WITH_SET",
                fields=(object_class, track_report),
            )
        ).fields == ()
        with pytest.raises(TransportError) as error:
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(track_report, object_instance, f"{track_parameter}:545241434b2d33", "747261636b2d756e707562"),
                )
            )
        assert error.value.code == "InteractionClassNotPublished"

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(
                        alert_report,
                        object_instance,
                        f"{alert_federate}:31,{alert_service}:7374696c6c,{alert_serial}:32",
                        "616c6572742d7075626c6973686564",
                    ),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            alert_report,
            object_instance,
            f"{alert_federate}:31,{alert_service}:7374696c6c,{alert_serial}:32",
            "616c6572742d7075626c6973686564",
            "1",
            "1",
        )

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "unsubscribeObjectClassDirectedInteractionsWithSetRequest",
            "unpublishObjectClassDirectedInteractionsWithSetRequest",
            "sendDirectedInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_queues_timestamped_directed_interactions_and_retracts_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-directed-tso"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedTso2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSO", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedTsoTarget-1"))).fields[0]
        assert server.servicer.callback_queue == []

        late = transport.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(interaction_class, object_instance, f"{parameter}:6c617465", "6c6174652d746167", "HLAinteger64Time", "20"),
            )
        ).fields[0]
        retracted = transport.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(interaction_class, object_instance, f"{parameter}:64726f70", "64726f702d746167", "HLAinteger64Time", "15"),
            )
        ).fields[0]
        assert (late, retracted) == ("1", "2")

        assert transport.request(TransportRequest(command="RETRACT", fields=(retracted,))).fields == ()
        assert server.servicer.queued_tso_callbacks.keys() == {"1"}

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "12"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "12")

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "25"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION_TSO",
            interaction_class,
            object_instance,
            f"{parameter}:6c617465",
            "6c6174652d746167",
            "2",
            "1",
            "HLAinteger64Time",
            "20",
            "2",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "25")
        assert transport.request(TransportRequest(command="RETRACT", fields=(late,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_RETRACTION",
            late,
        )
        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="RETRACT", fields=(late,)))
        assert error.value.code == "MessageCanNoLongerBeRetracted"

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionWithTimeRequest",
            "retractRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_delivers_and_retracts_timestamped_directed_interactions_for_all_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    observer = None
    federation_name = "fedpro-2025-directed-tso-routing"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, subscriber_a, subscriber_b, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedTsoRouting2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSOOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSO-A", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSO-B", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSOObserver", "TestFederate", federation_name))
        ).fields == ("4", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedTSORoutingTarget-1"))
        ).fields[0]

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        handle = owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    object_instance,
                    f"{parameter}:54494d4544",
                    "64697265637465642d74736f",
                    "HLAinteger64Time",
                    "5",
                ),
            )
        ).fields[0]
        assert handle == "1"

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_a = subscriber_a.request(TransportRequest(command="EVOKE")).fields
        grant_a = subscriber_a.request(TransportRequest(command="EVOKE")).fields
        assert first_a == (
            "1",
            "DIRECTED_INTERACTION_TSO",
            interaction_class,
            object_instance,
            f"{parameter}:54494d4544",
            "64697265637465642d74736f",
            "2",
            "1",
            "HLAinteger64Time",
            "5",
            "2",
        )
        assert grant_a == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        grant_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        assert first_b == first_a
        assert grant_b == grant_a

        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION_TSO")

        assert owner.request(TransportRequest(command="RETRACT", fields=(handle,))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", handle)
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", handle)
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_RETRACTION")

        with pytest.raises(TransportError) as error:
            owner.request(TransportRequest(command="RETRACT", fields=(handle,)))
        assert error.value.code == "MessageCanNoLongerBeRetracted"

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionWithTimeRequest",
            "retractRequest",
            "nextMessageRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_queued_directed_tso_for_disconnected_target_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    federation_name = "fedpro-2025-directed-tso-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedTsoRouting2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSODisconnectOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        subscriber_handle = subscriber.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedTSODisconnectSubscriber", "TestFederate", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedTSODisconnectTarget-1"))
        ).fields[0]
        handle = owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    object_instance,
                    f"{parameter}:44495245435445442d54534f",
                    "64697265637465642d74736f2d646973636f6e6e656374",
                    "HLAinteger64Time",
                    "5",
                ),
            )
        ).fields[0]
        assert handle == "1"
        assert server.servicer.queued_tso_callbacks.keys() == {"1"}

        assert subscriber.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert subscriber_handle not in server.servicer.peer_federate_handles.values()
        assert server.servicer.queued_tso_callbacks == {}

        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert server.servicer.queued_tso_callbacks == {}
        assert all(
            callback.WhichOneof("callbackRequest") != "receiveDirectedInteractionWithTime"
            for callback in server.servicer.callback_queue
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionWithTimeRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber is not None:
            subscriber.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_directed_interactions_only_to_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    observer = None
    federation_name = "fedpro-2025-directed-routing"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, subscriber_a, subscriber_b, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedRouting2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedSubscriberA", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedSubscriberB", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedObserver", "TestFederate", federation_name))
        ).fields == ("4", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedRoutingTarget-1"))
        ).fields[0]

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:524f55544544", "726f757465642d746167"),
            )
        ).fields == ()

        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 2
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:524f55544544",
            "726f757465642d746167",
            "1",
            "1",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:524f55544544",
            "726f757465642d746167",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-102",
    "HLA2025-FI-SVC-103",
    "HLA2025-FI-SVC-104",
    "HLA2025-FI-SVC-105",
    "HLA2025-FI-SVC-106",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-109",
    "HLA2025-FI-SVC-110",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-113",
    "HLA2025-FI-SVC-114",
    "HLA2025-FI-SVC-115",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-FI-SVC-118",
    "HLA2025-FI-SVC-120",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_time_management_services_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-time-services"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TimeServices2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Time", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        assert transport.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert server.servicer.time_regulating is True
        assert transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "2")
        assert transport.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert server.servicer.time_constrained is True
        assert transport.request(TransportRequest(command="ENABLE_ASYNCHRONOUS_DELIVERY")).fields == ()
        assert server.servicer.asynchronous_delivery_enabled is True

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTimeTarget-1"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")

        assert transport.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{attribute}:6e6d72", "6e6d722d746167", "HLAinteger64Time", "30"),
            )
        ).fields == ("1",)
        assert transport.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "30"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "REFLECT_TSO", object_instance)
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "30")
        assert transport.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "30")

        assert transport.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:6e6d7261", "6e6d72612d746167", "HLAinteger64Time", "35"),
            )
        ).fields == ("2",)
        assert transport.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "35"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "INTERACTION_TSO", interaction_class)
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "35")

        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "40"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "40")
        assert transport.request(TransportRequest(command="FLUSH_QUEUE_REQUEST", fields=("HLAinteger64Time", "45"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FLUSH_QUEUE_GRANT",
            "HLAinteger64Time",
            "45",
            "HLAinteger64Time",
            "45",
        )
        assert transport.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "45")
        assert transport.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "45")

        assert transport.request(TransportRequest(command="DISABLE_ASYNCHRONOUS_DELIVERY")).fields == ()
        assert server.servicer.asynchronous_delivery_enabled is False
        assert transport.request(TransportRequest(command="DISABLE_TIME_CONSTRAINED")).fields == ()
        assert server.servicer.time_constrained is False
        assert transport.request(TransportRequest(command="DISABLE_TIME_REGULATION")).fields == ()
        assert server.servicer.time_regulating is False

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "enableTimeRegulationRequest",
            "disableTimeRegulationRequest",
            "enableTimeConstrainedRequest",
            "disableTimeConstrainedRequest",
            "enableAsynchronousDeliveryRequest",
            "disableAsynchronousDeliveryRequest",
            "nextMessageRequestRequest",
            "nextMessageRequestAvailableRequest",
            "timeAdvanceRequestAvailableRequest",
            "flushQueueRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-122",
    "HLA2025-BND-003",
)
def test_2025_transport_server_tracks_lookahead_and_galt_per_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    left = None
    right = None
    federation_name = "fedpro-2025-time-query-isolation"
    try:
        left = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        right = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert left.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert right.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert left.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TimeServices2025.xml"))).fields == ()
        assert left.request(TransportRequest(command="JOIN", fields=("FedPro2025TimeLeft", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert right.request(TransportRequest(command="JOIN", fields=("FedPro2025TimeRight", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )

        assert left.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert right.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "5"))).fields == ()
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")

        assert left.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "2")
        assert right.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "5")

        assert left.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "4"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "9"))).fields == ()
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "9")

        assert left.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "9")
        assert right.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "6")

        assert server.servicer.handle_current_times["1"].data == b"HLAinteger64Time:4"
        assert server.servicer.handle_current_times["2"].data == b"HLAinteger64Time:9"
        assert server.servicer.handle_lookahead["1"].data == b"HLAinteger64Interval:2"
        assert server.servicer.handle_lookahead["2"].data == b"HLAinteger64Interval:5"

        assert left.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert right.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert right.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert left.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert right.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if left is not None:
            left.close()
        if right is not None:
            right.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-122",
    "HLA2025-FI-SVC-123",
    "HLA2025-BND-003",
)
def test_2025_transport_server_reports_lits_from_queued_tso_for_target_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    sender = None
    receiver = None
    federation_name = "fedpro-2025-lits-queued-tso"
    try:
        sender = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        receiver = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert sender.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert receiver.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert sender.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Exchange2025.xml"))).fields == ()
        assert sender.request(TransportRequest(command="JOIN", fields=("FedPro2025LitsSender", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert receiver.request(TransportRequest(command="JOIN", fields=("FedPro2025LitsReceiver", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )

        interaction_class = sender.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = sender.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert sender.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert receiver.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert sender.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert receiver.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert receiver.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")

        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "6"))).fields == ()
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "6")
        assert receiver.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "9"))).fields == ()
        assert receiver.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "9")

        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:4c495453", "7175657565642d6c697473", "HLAinteger64Time", "7"),
            )
        ).fields == ("1",)

        assert receiver.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "8")
        assert receiver.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "7")

        assert sender.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert receiver.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert receiver.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert sender.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert receiver.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if sender is not None:
            sender.close()
        if receiver is not None:
            receiver.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_transport_server_blocks_window_closure_until_future_inputs_are_excluded_over_fedpro_schema():
    server = start_2025_grpc_server()
    slow = None
    radar = None
    federation_name = "fedpro-2025-future-exclusion"
    try:
        slow = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert slow.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert radar.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert slow.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TimeServices2025.xml"))
        ).fields == ()
        assert slow.request(
            TransportRequest(command="JOIN", fields=("FedPro2025FutureSlow", "TimeWindowFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert radar.request(
            TransportRequest(command="JOIN", fields=("FedPro2025FutureRadar", "TimeWindowFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        interaction_class = slow.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = slow.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert slow.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert slow.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert slow.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        assert slow.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "100"))).fields == ()
        assert slow.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "100")

        assert radar.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "101")
        assert radar.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "101")

        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "110"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("0",)

        assert slow.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "109"))).fields == ()
        assert slow.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "109")

        assert radar.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        with pytest.raises(TransportError):
            slow.request(
                TransportRequest(
                    command="SEND_INTERACTION_TIMESTAMP",
                    fields=(interaction_class, f"{parameter}:6c6174652d313039", "6c6174652d313039", "HLAinteger64Time", "109"),
                )
            )

        assert slow.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{parameter}:626f756e646172792d313130",
                    "626f756e646172792d313130",
                    "HLAinteger64Time",
                    "110",
                ),
            )
        ).fields == ("1",)
        assert slow.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "120"))).fields == ()
        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "120"))).fields == ()

        receive = radar.request(TransportRequest(command="EVOKE")).fields
        assert receive[:5] == (
            "1",
            "INTERACTION_TSO",
            interaction_class,
            f"{parameter}:626f756e646172792d313130",
            "626f756e646172792d313130",
        )
        assert receive[7:9] == ("HLAinteger64Time", "110")
    finally:
        if slow is not None:
            try:
                slow.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if radar is not None:
            try:
                radar.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if radar is not None:
            try:
                radar.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        if slow is not None:
            slow.close()
        if radar is not None:
            radar.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006", "HLA2025-BND-003")
def test_2025_transport_server_proves_time_window_core_progression_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    fast = None
    slow = None
    federation_name = "fedpro-2025-time-window-core"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        fast = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        slow = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, consumer, fast, slow):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CoreTruth", "TimeWindowFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert radar.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CoreRadar", "TimeWindowFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert consumer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CoreConsumer", "TimeWindowFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        assert fast.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CoreFast", "TimeWindowFederate", federation_name))
        ).fields == ("4", "HLAinteger64Time")
        assert slow.request(
            TransportRequest(command="JOIN", fields=("FedPro2025CoreSlow", "TimeWindowFederate", federation_name))
        ).fields == ("5", "HLAinteger64Time")

        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        assert truth.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(track_interaction, f"{track_parameter}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(track_interaction, f"{track_parameter}:73656e736f722d313036", "73656e736f722d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "109"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "109")

        assert radar.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "105")

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        radar_callbacks: list[tuple[str, ...]] = []
        for _ in range(6):
            fields = radar.request(TransportRequest(command="EVOKE")).fields
            radar_callbacks.append(fields)
            if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110"):
                break
        delivered = [fields for fields in radar_callbacks if fields[:2] == ("1", "INTERACTION_TSO")]
        grants = [fields for fields in radar_callbacks if fields[:2] == ("1", "TIME_ADVANCE_GRANT")]
        assert len(delivered) == 2
        assert delivered[0][:5] == ("1", "INTERACTION_TSO", track_interaction, f"{track_parameter}:74727574682d313035", "74727574682d313035")
        assert delivered[0][7:9] == ("HLAinteger64Time", "105")
        assert delivered[1][:5] == ("1", "INTERACTION_TSO", track_interaction, f"{track_parameter}:73656e736f722d313036", "73656e736f722d313036")
        assert delivered[1][7:9] == ("HLAinteger64Time", "106")
        assert grants[-1] == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "110")
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "10"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert fast.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert fast.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert slow.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert slow.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")

        for illegal_time in ("100", "105", "109"):
            with pytest.raises(TransportError):
                truth.request(
                    TransportRequest(
                        command="SEND_INTERACTION_TIMESTAMP",
                        fields=(
                            track_interaction,
                            f"{track_parameter}:{('late-' + illegal_time).encode('ascii').hex()}",
                            ('late-' + illegal_time).encode('ascii').hex(),
                            "HLAinteger64Time",
                            illegal_time,
                        ),
                    )
                )

        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "119"))).fields == ()
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert fast.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "160"))).fields == ()
        assert slow.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "118"))).fields == ()
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "119") in collect_until_grant(truth, "119")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "160") in collect_until_grant(fast, "160")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "118") in collect_until_grant(slow, "118")
        assert truth.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "119")
        assert fast.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "160")
        assert slow.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "118")
    finally:
        for transport in (truth, radar, consumer, fast, slow):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer, fast, slow):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006", "HLA2025-BND-003")
def test_2025_transport_server_ignores_receive_order_poison_after_window_close_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    federation_name = "fedpro-2025-receive-order-poison"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, consumer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(
            TransportRequest(command="JOIN", fields=("FedPro2025PoisonTruth", "TimeWindowFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert radar.request(
            TransportRequest(command="JOIN", fields=("FedPro2025PoisonRadar", "TimeWindowFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert consumer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025PoisonConsumer", "TimeWindowFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        object_instance = truth.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "ReceiveOrderPoisonTarget-1"))
        ).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, position, "TIMESTAMP"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313036", "74727574682d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        first_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        second_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        window_close_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert first_reflect[:5] == ("1", "REFLECT_TSO", object_instance, f"{position}:74727574682d313035", "74727574682d313035")
        assert first_reflect[7:9] == ("HLAinteger64Time", "105")
        assert second_reflect[:5] == ("1", "REFLECT_TSO", object_instance, f"{position}:74727574682d313036", "74727574682d313036")
        assert second_reflect[7:9] == ("HLAinteger64Time", "106")
        assert window_close_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")
        closed_window_tags_before = [first_reflect[4], second_reflect[4]]

        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, position, "RECEIVE"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES",
                fields=(object_instance, f"{position}:726563656976652d6f726465722d706f69736f6e", "726563656976652d6f726465722d706f69736f6e"),
            )
        ).fields == ()
        poison_reflection = radar.request(TransportRequest(command="EVOKE")).fields
        assert poison_reflection == (
            "1",
            "REFLECT",
            object_instance,
            f"{position}:726563656976652d6f726465722d706f69736f6e",
            "726563656976652d6f726465722d706f69736f6e",
            "1",
            "1",
        )

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()

        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        send_handle = radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:747261636b2d706f69736f6e2d73616665",
                    "72616461722d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "111",
                ),
            )
        ).fields
        assert len(send_handle) == 1
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()

        delivered = consumer.request(TransportRequest(command="EVOKE")).fields
        assert delivered[:5] == (
            "1",
            "INTERACTION_TSO",
            track_interaction,
            f"{track_parameter}:747261636b2d706f69736f6e2d73616665",
            "72616461722d747261636b2d6f7574707574",
        )
        assert delivered[7:9] == ("HLAinteger64Time", "111")
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")

        closed_window_tags_after = [first_reflect[4], second_reflect[4]]
        assert closed_window_tags_after == closed_window_tags_before
    finally:
        for transport in (truth, radar, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_transport_server_delivers_post_closure_timestamped_output_to_consumer_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    federation_name = "fedpro-2025-output-delivery"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert truth.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert radar.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert consumer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("FedPro2025OutputTruth", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert radar.request(TransportRequest(command="JOIN", fields=("FedPro2025OutputRadar", "TimeWindowFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert consumer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025OutputConsumer", "TimeWindowFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        object_instance = truth.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "OutputTarget-1"))).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, position, "TIMESTAMP"))).fields == ()

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313036", "74727574682d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        first = radar.request(TransportRequest(command="EVOKE")).fields
        assert first[:3] == ("1", "REFLECT_TSO", object_instance)
        assert first[7:9] == ("HLAinteger64Time", "105")
        second = radar.request(TransportRequest(command="EVOKE")).fields
        assert second[:3] == ("1", "REFLECT_TSO", object_instance)
        assert second[7:9] == ("HLAinteger64Time", "106")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("0",)

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:747261636b2d3130302d3131305b66726f6d2074727574682d3130352c74727574682d3130365d",
                    "72616461722d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "111",
                ),
            )
        ).fields == ("3",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()

        delivered = consumer.request(TransportRequest(command="EVOKE")).fields
        assert delivered[:5] == (
            "1",
            "INTERACTION_TSO",
            track_interaction,
            f"{track_parameter}:747261636b2d3130302d3131305b66726f6d2074727574682d3130352c74727574682d3130365d",
            "72616461722d747261636b2d6f7574707574",
        )
        assert delivered[7:9] == ("HLAinteger64Time", "111")
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")
        radar_callback = radar.request(TransportRequest(command="EVOKE")).fields
        assert radar_callback in {
            ("0",),
            ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120"),
        }

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")
    finally:
        for transport in (truth, radar, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_transport_server_preserves_consumer_timestamp_order_between_competing_output_and_radar_output_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    other = None
    consumer = None
    federation_name = "fedpro-2025-consumer-order"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        other = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, other, consumer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("FedPro2025OrderTruth", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert radar.request(TransportRequest(command="JOIN", fields=("FedPro2025OrderRadar", "TimeWindowFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert other.request(TransportRequest(command="JOIN", fields=("FedPro2025OrderOther", "TimeWindowFederate", federation_name))).fields == (
            "3",
            "HLAinteger64Time",
        )
        assert consumer.request(TransportRequest(command="JOIN", fields=("FedPro2025OrderConsumer", "TimeWindowFederate", federation_name))).fields == (
            "4",
            "HLAinteger64Time",
        )

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert other.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        object_instance = truth.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "ConsumerOrderTarget-1"))).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, position, "TIMESTAMP"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:74727574682d313036", "74727574682d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert other.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert other.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()
        assert other.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()

        assert other.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:6f746865722d747261636b2d3131305b676174655d",
                    "6f746865722d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "110",
                ),
            )
        ).fields == ("3",)
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:72616461722d747261636b2d3131315b66726f6d2074727574682d3130352c74727574682d3130365d",
                    "72616461722d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "111",
                ),
            )
        ).fields == ("4",)
        assert other.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert other.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()

        first = consumer.request(TransportRequest(command="EVOKE")).fields
        second = consumer.request(TransportRequest(command="EVOKE")).fields
        assert [first[2], second[2]] == [track_interaction, track_interaction]
        assert [first[4], second[4]] == ["6f746865722d747261636b2d6f7574707574", "72616461722d747261636b2d6f7574707574"]
        assert [first[7:9], second[7:9]] == [("HLAinteger64Time", "110"), ("HLAinteger64Time", "111")]
        assert [first[3], second[3]] == [
            f"{track_parameter}:6f746865722d747261636b2d3131305b676174655d",
            f"{track_parameter}:72616461722d747261636b2d3131315b66726f6d2074727574682d3130352c74727574682d3130365d",
        ]

        next_callback = consumer.request(TransportRequest(command="EVOKE")).fields
        assert next_callback in {
            ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120"),
            ("0",),
        }

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")
        assert other.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert other.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        consumer_tail = []
        while True:
            fields = consumer.request(TransportRequest(command="EVOKE")).fields
            consumer_tail.append(fields)
            if fields in {("0",), ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")}:
                break
        assert not any(callback[:2] == ("1", "INTERACTION_TSO") for callback in consumer_tail)
    finally:
        for transport in (truth, radar, other, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, other, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_transport_server_keeps_two_scan_pipeline_outputs_separated_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    federation_name = "fedpro-2025-pipeline"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, consumer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("FedPro2025PipeTruth", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert radar.request(TransportRequest(command="JOIN", fields=("FedPro2025PipeRadar", "TimeWindowFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert consumer.request(TransportRequest(command="JOIN", fields=("FedPro2025PipeConsumer", "TimeWindowFederate", federation_name))).fields == (
            "3",
            "HLAinteger64Time",
        )

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        object_instance = truth.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "PipelineTarget-1"))).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, position, "TIMESTAMP"))).fields == ()

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:7363616e312d696e7075742d61", "7363616e312d696e7075742d61", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:7363616e312d696e7075742d62", "7363616e312d696e7075742d62", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{position}:7363616e322d696e707574", "7363616e322d696e707574", "HLAinteger64Time", "112"),
            )
        ).fields == ("3",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        scan2_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert scan2_reflect[:3] == ("1", "REFLECT_TSO", object_instance)
        assert scan2_reflect[7:9] == ("HLAinteger64Time", "112")

        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:747261636b2d7363616e2d315b66726f6d207363616e312d696e7075742d612c7363616e312d696e7075742d625d",
                    "7363616e312d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "115",
                ),
            )
        ).fields == ("4",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()

        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:747261636b2d7363616e2d325b66726f6d207363616e322d696e7075745d",
                    "7363616e322d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "122",
                ),
            )
        ).fields == ("5",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()

        deliveries = []
        for _ in range(32):
            fields = consumer.request(TransportRequest(command="EVOKE")).fields
            if fields[:2] == ("1", "INTERACTION_TSO"):
                deliveries.append(fields)
            if len(deliveries) >= 2:
                break
        assert len(deliveries) == 2
        assert [row[4] for row in deliveries] == ["7363616e312d747261636b2d6f7574707574", "7363616e322d747261636b2d6f7574707574"]
        assert [row[7:9] for row in deliveries] == [("HLAinteger64Time", "115"), ("HLAinteger64Time", "122")]
        assert [row[3] for row in deliveries] == [
            f"{track_parameter}:747261636b2d7363616e2d315b66726f6d207363616e312d696e7075742d612c7363616e312d696e7075742d625d",
            f"{track_parameter}:747261636b2d7363616e2d325b66726f6d207363616e322d696e7075745d",
        ]

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "140")
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        tail = []
        for _ in range(32):
            fields = consumer.request(TransportRequest(command="EVOKE")).fields
            tail.append(fields)
            if fields in {("0",), ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "140")}:
                break
        assert not any(callback[:2] == ("1", "INTERACTION_TSO") for callback in tail)
    finally:
        for transport in (truth, radar, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006", "HLA2025-BND-003")
def test_2025_transport_server_restores_open_and_closed_time_window_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    federation_name = "fedpro-2025-window-restore"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert truth.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert radar.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("TruthFederate", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        radar_handle = radar.request(
            TransportRequest(command="JOIN", fields=("RadarFederate", "TimeWindowFederate", federation_name))
        ).fields[0]

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        target_object = truth.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "WindowRestoreTarget-1"))
        ).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(target_object, position, "TIMESTAMP"))).fields == ()

        def complete_save(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        def complete_restore(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", save_label)
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
            radar_restore_callbacks = [radar.request(TransportRequest(command="EVOKE")).fields for _ in range(3)]
            assert (
                "1",
                "INITIATE_FEDERATE_RESTORE",
                save_label,
                "RadarFederate",
                radar_handle,
            ) in radar_restore_callbacks
            assert truth.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        def snapshot_window_state(
            *,
            phase: str,
            window_closed: bool,
            closed_at: int | None,
            last_grant: int,
            received_tags: list[str],
        ) -> dict[str, object]:
            return {
                "phase": phase,
                "window_closed": window_closed,
                "closed_at": closed_at,
                "last_grant": last_grant,
                "received_tags": list(received_tags),
            }

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "105"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "105")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "105"))).fields == ()
        first_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert first_reflect[:5] == ("1", "REFLECT_TSO", target_object, f"{position}:74727574682d313035", "74727574682d313035")
        assert first_reflect[7:9] == ("HLAinteger64Time", "105")
        first_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert first_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "105")
        saved_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=105,
            received_tags=["74727574682d313035"],
        )

        complete_save("SAVE-WINDOW-OPEN")

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:74727574682d313036", "74727574682d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        dirty_second_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert dirty_second_reflect[:5] == ("1", "REFLECT_TSO", target_object, f"{position}:74727574682d313036", "74727574682d313036")
        assert dirty_second_reflect[7:9] == ("HLAinteger64Time", "106")
        dirty_second_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert dirty_second_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")
        dirty_close_grant = dirty_second_grant
        assert dirty_close_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        complete_restore("SAVE-WINDOW-OPEN")
        assert truth.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "105")
        assert radar.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "105")
        restored_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=105,
            received_tags=["74727574682d313035"],
        )
        assert restored_open_state == saved_open_state

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(
                    target_object,
                    f"{position}:74727574682d3130362d6272616e6368",
                    "74727574682d3130362d6272616e6368",
                    "HLAinteger64Time",
                    "106",
                ),
            )
        ).fields == ("3",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        reclosed_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert reclosed_reflect[:5] == (
            "1",
            "REFLECT_TSO",
            target_object,
            f"{position}:74727574682d3130362d6272616e6368",
            "74727574682d3130362d6272616e6368",
        )
        assert reclosed_reflect[7:9] == ("HLAinteger64Time", "106")
        reclosed_second_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert reclosed_second_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")
        reclosed_grant = reclosed_second_grant
        assert reclosed_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")
        saved_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=110,
            last_grant=110,
            received_tags=["74727574682d313035", "74727574682d3130362d6272616e6368"],
        )

        complete_save("SAVE-WINDOW-CLOSED")

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:64697274792d706f73742d636c6f7365", "64697274792d706f73742d636c6f7365", "HLAinteger64Time", "120"),
            )
        ).fields == ("4",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        dirty_post_close_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert dirty_post_close_reflect[:5] == (
            "1",
            "REFLECT_TSO",
            target_object,
            f"{position}:64697274792d706f73742d636c6f7365",
            "64697274792d706f73742d636c6f7365",
        )
        assert dirty_post_close_reflect[7:9] == ("HLAinteger64Time", "120")
        dirty_post_close_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert dirty_post_close_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")

        complete_restore("SAVE-WINDOW-CLOSED")
        assert truth.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")
        restored_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=110,
            last_grant=110,
            received_tags=["74727574682d313035", "74727574682d3130362d6272616e6368"],
        )
        assert restored_closed_state == saved_closed_state

        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields in {
            ("0",),
            ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120"),
        }
    finally:
        for transport in (truth, radar):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006", "HLA2025-BND-003")
def test_2025_transport_server_restores_closed_window_output_resume_without_dirty_replay_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    federation_name = "fedpro-2025-window-restore-output"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, consumer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("TruthFederate", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        radar_handle = radar.request(
            TransportRequest(command="JOIN", fields=("RadarFederate", "TimeWindowFederate", federation_name))
        ).fields[0]
        consumer_handle = consumer.request(
            TransportRequest(command="JOIN", fields=("TrackConsumerFederate", "TimeWindowFederate", federation_name))
        ).fields[0]

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        target_object = truth.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "WindowRestoreOutputTarget-1"))
        ).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(target_object, position, "TIMESTAMP"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:74727574682d313035", "74727574682d313035", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:74727574682d313036", "74727574682d313036", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        def complete_save(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        def complete_restore(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", save_label)
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
            radar_restore_callbacks = []
            for _ in range(8):
                fields = radar.request(TransportRequest(command="EVOKE")).fields
                radar_restore_callbacks.append(fields)
                if fields[:2] == ("1", "INITIATE_FEDERATE_RESTORE"):
                    break
            consumer_restore_callbacks = []
            for _ in range(8):
                fields = consumer.request(TransportRequest(command="EVOKE")).fields
                consumer_restore_callbacks.append(fields)
                if fields[:2] == ("1", "INITIATE_FEDERATE_RESTORE"):
                    break
            assert ("1", "INITIATE_FEDERATE_RESTORE", save_label, "RadarFederate", radar_handle) in radar_restore_callbacks
            assert ("1", "INITIATE_FEDERATE_RESTORE", save_label, "TrackConsumerFederate", consumer_handle) in consumer_restore_callbacks
            assert truth.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        def collect_interactions(transport: GrpcTransport, *, expected: int, limit: int = 12) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                if fields[:2] == ("1", "INTERACTION_TSO"):
                    callbacks.append(fields)
                    if len(callbacks) == expected:
                        break
            return callbacks

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        complete_save("SAVE-WINDOW-CLOSED-BEFORE-OUTPUT")

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:64697274792d747261636b2d3130302d313130",
                    "64697274792d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "111",
                ),
            )
        ).fields == ("3",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        dirty_consumer_receive = consumer.request(TransportRequest(command="EVOKE")).fields
        assert dirty_consumer_receive[:5] == (
            "1",
            "INTERACTION_TSO",
            track_interaction,
            f"{track_parameter}:64697274792d747261636b2d3130302d313130",
            "64697274792d747261636b2d6f7574707574",
        )
        assert dirty_consumer_receive[7:9] == ("HLAinteger64Time", "111")

        complete_restore("SAVE-WINDOW-CLOSED-BEFORE-OUTPUT")
        assert truth.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")
        assert radar.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:726573746f7265642d747261636b2d3130302d313130",
                    "726573746f7265642d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "111",
                ),
            )
        ).fields == ("4",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        restored_consumer_receive = consumer.request(TransportRequest(command="EVOKE")).fields
        assert restored_consumer_receive[:5] == (
            "1",
            "INTERACTION_TSO",
            track_interaction,
            f"{track_parameter}:726573746f7265642d747261636b2d3130302d313130",
            "726573746f7265642d747261636b2d6f7574707574",
        )
        assert restored_consumer_receive[7:9] == ("HLAinteger64Time", "111")

        tail = []
        for _ in range(8):
            fields = consumer.request(TransportRequest(command="EVOKE")).fields
            tail.append(fields)
            if fields in {("0",), ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120")}:
                break
        assert not any(callback[:5] == (
            "1",
            "INTERACTION_TSO",
            track_interaction,
            f"{track_parameter}:64697274792d747261636b2d3130302d313130",
            "64697274792d747261636b2d6f7574707574",
        ) for callback in tail if len(callback) >= 5)
    finally:
        for transport in (truth, radar, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006", "HLA2025-BND-003")
def test_2025_transport_server_restores_pipeline_resume_without_cross_window_replay_over_fedpro_schema():
    server = start_2025_grpc_server()
    truth = None
    radar = None
    consumer = None
    federation_name = "fedpro-2025-pipeline-restore"
    try:
        truth = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        radar = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        consumer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (truth, radar, consumer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert truth.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        assert truth.request(TransportRequest(command="JOIN", fields=("TruthFederate", "TimeWindowFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        radar_handle = radar.request(
            TransportRequest(command="JOIN", fields=("RadarFederate", "TimeWindowFederate", federation_name))
        ).fields[0]
        consumer_handle = consumer.request(
            TransportRequest(command="JOIN", fields=("TrackConsumerFederate", "TimeWindowFederate", federation_name))
        ).fields[0]

        target_class = truth.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        position = truth.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        track_interaction = truth.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        track_parameter = truth.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(track_interaction, "TrackId"))).fields[0]
        assert truth.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, position))).fields == ()
        assert radar.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()
        assert consumer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(track_interaction,))).fields == ()

        assert truth.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        target_object = truth.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "PipelineRestoreTarget-1"))
        ).fields[0]
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert truth.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(target_object, position, "TIMESTAMP"))).fields == ()
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:7363616e312d696e7075742d61", "7363616e312d696e7075742d61", "HLAinteger64Time", "105"),
            )
        ).fields == ("1",)
        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:7363616e312d696e7075742d62", "7363616e312d696e7075742d62", "HLAinteger64Time", "106"),
            )
        ).fields == ("2",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "REFLECT_TSO")
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert radar.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "110")
        assert consumer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert radar.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(track_interaction, "TIMESTAMP"))).fields == ()
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "110"))).fields == ()
        assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "110")

        assert truth.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(target_object, f"{position}:7363616e322d696e707574", "7363616e322d696e707574", "HLAinteger64Time", "112"),
            )
        ).fields == ("3",)
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "130")

        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "112"))).fields == ()
        scan2_reflect = radar.request(TransportRequest(command="EVOKE")).fields
        assert scan2_reflect[:5] == ("1", "REFLECT_TSO", target_object, f"{position}:7363616e322d696e707574", "7363616e322d696e707574")
        assert scan2_reflect[7:9] == ("HLAinteger64Time", "112")
        scan2_grant = radar.request(TransportRequest(command="EVOKE")).fields
        assert scan2_grant == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "112")
        assert radar.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "112")

        def complete_save(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_label)
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
            assert truth.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        def complete_restore(save_label: str) -> None:
            assert truth.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(save_label,))).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", save_label)
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
            radar_restore_callbacks = []
            for _ in range(8):
                fields = radar.request(TransportRequest(command="EVOKE")).fields
                radar_restore_callbacks.append(fields)
                if fields[:2] == ("1", "INITIATE_FEDERATE_RESTORE"):
                    break
            consumer_restore_callbacks = []
            for _ in range(8):
                fields = consumer.request(TransportRequest(command="EVOKE")).fields
                consumer_restore_callbacks.append(fields)
                if fields[:2] == ("1", "INITIATE_FEDERATE_RESTORE"):
                    break
            assert ("1", "INITIATE_FEDERATE_RESTORE", save_label, "RadarFederate", radar_handle) in radar_restore_callbacks
            assert ("1", "INITIATE_FEDERATE_RESTORE", save_label, "TrackConsumerFederate", consumer_handle) in consumer_restore_callbacks
            assert truth.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert radar.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert consumer.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
            assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
            assert radar.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
            assert consumer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        def collect_interactions(transport: GrpcTransport, *, expected: int, limit: int = 12) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                if fields[:2] == ("1", "INTERACTION_TSO"):
                    callbacks.append(fields)
                    if len(callbacks) == expected:
                        break
            return callbacks

        complete_save("SAVE-PIPELINE-AFTER-SCAN2-COLLECT")

        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:64697274792d747261636b2d7363616e2d315b66726f6d2064697274795d",
                    "64697274792d7363616e312d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "131",
                ),
            )
        ).fields == ("4",)
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:64697274792d747261636b2d7363616e2d325b66726f6d2064697274795d",
                    "64697274792d7363616e322d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "132",
                ),
            )
        ).fields == ("5",)
        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        dirty_receives = collect_interactions(consumer, expected=2)
        assert [dirty_receives[0][4], dirty_receives[1][4]] == [
            "64697274792d7363616e312d747261636b2d6f7574707574",
            "64697274792d7363616e322d747261636b2d6f7574707574",
        ]

        complete_restore("SAVE-PIPELINE-AFTER-SCAN2-COLLECT")
        assert radar.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "112")
        assert consumer.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "110")

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "130"))).fields == ()
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:726573746f7265642d747261636b2d7363616e2d315b66726f6d207363616e312d696e7075742d612c7363616e312d696e7075742d625d",
                    "726573746f7265642d7363616e312d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "115",
                ),
            )
        ).fields == ("6",)
        restored_first_receive = collect_interactions(consumer, expected=1)
        assert [restored_first_receive[0][4]] == ["726573746f7265642d7363616e312d747261636b2d6f7574707574"]
        assert [restored_first_receive[0][3]] == [
            f"{track_parameter}:726573746f7265642d747261636b2d7363616e2d315b66726f6d207363616e312d696e7075742d612c7363616e312d696e7075742d625d"
        ]
        assert radar.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "120"))).fields == ()
        restored_scan2_callbacks = collect_until_grant(radar, "120")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "120") in restored_scan2_callbacks
        assert not any(callback[:2] == ("1", "REFLECT_TSO") for callback in restored_scan2_callbacks)

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert radar.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    track_interaction,
                    f"{track_parameter}:726573746f7265642d747261636b2d7363616e2d325b66726f6d207363616e322d696e7075745d",
                    "726573746f7265642d7363616e322d747261636b2d6f7574707574",
                    "HLAinteger64Time",
                    "131",
                ),
            )
        ).fields == ("7",)
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        restored_second_receive = collect_interactions(consumer, expected=1)
        assert [restored_second_receive[0][4]] == ["726573746f7265642d7363616e322d747261636b2d6f7574707574"]
        assert [restored_second_receive[0][3]] == [
            f"{track_parameter}:726573746f7265642d747261636b2d7363616e2d325b66726f6d207363616e322d696e7075745d"
        ]

        assert consumer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert truth.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        assert truth.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "140")
        assert radar.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "140"))).fields == ()
        tail = []
        for _ in range(16):
            fields = consumer.request(TransportRequest(command="EVOKE")).fields
            tail.append(fields)
            if fields in {("0",), ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "140")}:
                break
        assert not any(
            callback[:5] == (
                "1",
                "INTERACTION_TSO",
                track_interaction,
                f"{track_parameter}:64697274792d747261636b2d7363616e2d315b66726f6d2064697274795d",
                "64697274792d7363616e312d747261636b2d6f7574707574",
            )
            for callback in tail
            if len(callback) >= 5
        )
    finally:
        for transport in (truth, radar, consumer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if truth is not None:
            try:
                truth.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (truth, radar, consumer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_orders_timestamped_interactions_across_two_federates_over_fedpro_schema():
    server = start_2025_grpc_server()
    sender = None
    receiver = None
    federation_name = "fedpro-2025-time-ordering"
    try:
        sender = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        receiver = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert sender.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert receiver.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert sender.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TimeServices2025.xml"))
        ).fields == ()
        assert sender.request(
            TransportRequest(command="JOIN", fields=("FedPro2025TimeSender", "TimeSender", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert receiver.request(
            TransportRequest(command="JOIN", fields=("FedPro2025TimeReceiver", "TimeReceiver", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert sender.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert receiver.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert receiver.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        interaction_class = sender.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = sender.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert sender.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert receiver.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        # Queue messages out of time order so the receiving federate must advance through the earliest timestamp first.
        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:7433", "7461672d33", "HLAinteger64Time", "3"),
            )
        ).fields == ("1",)
        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(interaction_class, f"{parameter}:7432", "7461672d32", "HLAinteger64Time", "2"),
            )
        ).fields == ("2",)

        assert receiver.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first = receiver.request(TransportRequest(command="EVOKE")).fields
        assert first == (
            "1",
            "INTERACTION_TSO",
            interaction_class,
            f"{parameter}:7432",
            "7461672d32",
            "2",
            "1",
            "HLAinteger64Time",
            "2",
            "2",
        )
        second = receiver.request(TransportRequest(command="EVOKE")).fields
        assert second == (
            "1",
            "INTERACTION_TSO",
            interaction_class,
            f"{parameter}:7433",
            "7461672d33",
            "2",
            "1",
            "HLAinteger64Time",
            "3",
            "2",
        )
        assert receiver.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert receiver.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "5")

        assert sender.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert receiver.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert sender.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert sender.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert receiver.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "enableTimeRegulationRequest",
            "enableTimeConstrainedRequest",
            "nextMessageRequestRequest",
            "queryLogicalTimeRequest",
            "sendInteractionWithTimeRequest",
        } <= set(server.servicer.calls)
    finally:
        if receiver is not None:
            receiver.close()
        if sender is not None:
            sender.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-019",
    "HLA2025-FI-SVC-020",
    "HLA2025-FI-SVC-021",
    "HLA2025-FI-SVC-022",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-024",
    "HLA2025-FI-SVC-025",
    "HLA2025-FI-SVC-026",
    "HLA2025-FI-SVC-027",
    "HLA2025-FI-SVC-028",
    "HLA2025-FI-SVC-029",
    "HLA2025-FI-SVC-030",
    "HLA2025-FI-SVC-031",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-033",
    "HLA2025-FI-SVC-034",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-save-restore"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "SaveRestore2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025SaveRestore", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        saved_object = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSavedTarget-1"))
        ).fields[0]
        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert transport.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "5")

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-1",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-1")
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="QUERY_FEDERATION_SAVE_STATUS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SAVE_STATUS_RESPONSE",
            "1:FEDERATE_SAVING",
        )
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert transport.request(TransportRequest(command="QUERY_FEDERATION_SAVE_STATUS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SAVE_STATUS_RESPONSE",
            "1:NO_SAVE_IN_PROGRESS",
        )
        after_save_object = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProAfterSaveTarget-1"))
        ).fields[0]
        assert after_save_object != saved_object
        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "11"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "11")
        assert transport.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "11")

        assert transport.request(
            TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-TIME-13", "HLAinteger64Time", "13"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_SAVE",
            "SAVE-TIME-13",
            "HLAinteger64Time",
            "13",
        )
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("MISSING-SAVE",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_FAILED", "MISSING-SAVE")
        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-1",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-1")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-1",
            "FedPro2025SaveRestore",
            "1",
        )
        assert transport.request(TransportRequest(command="QUERY_FEDERATION_RESTORE_STATUS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_RESTORE_STATUS_RESPONSE",
            "1:1:FEDERATE_RESTORE_REQUEST_PENDING",
        )
        assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert transport.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "5")
        assert transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(saved_object,))).fields == (
            "FedProSavedTarget-1",
        )
        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=("FedProAfterSaveTarget-1",)))
        assert error.value.code == "ObjectInstanceNotKnown"
        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE"))
        assert error.value.code == "RestoreNotRequested"

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-FAIL",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-FAIL")
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_NOT_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_NOT_SAVED",
            "FEDERATE_REPORTED_FAILURE_DURING_SAVE",
        )

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-ABORT",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-ABORT")
        assert transport.request(TransportRequest(command="ABORT_FEDERATION_SAVE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_NOT_SAVED", "SAVE_ABORTED")

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-1",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-1")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "INITIATE_FEDERATE_RESTORE", "SAVE-1")
        assert transport.request(TransportRequest(command="ABORT_FEDERATION_RESTORE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_NOT_RESTORED", "RESTORE_ABORTED")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "getObjectInstanceHandleRequest",
            "getObjectInstanceNameRequest",
            "federateSaveBegunRequest",
            "queryFederationSaveStatusRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "queryFederationRestoreStatusRequest",
            "federateRestoreCompleteRequest",
            "federateSaveNotCompleteRequest",
            "abortFederationSaveRequest",
            "abortFederationRestoreRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-022",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-027",
    "HLA2025-FI-SVC-028",
    "HLA2025-FI-SVC-031",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-033",
    "HLA2025-FI-SVC-034",
    "HLA2025-BND-003",
)
def test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-save-restore-multi"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "SaveRestore2025.xml"))
        ).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("Leader", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("Wing", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-MULTI",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-MULTI")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-MULTI")

        assert leader.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert leader.request(TransportRequest(command="QUERY_FEDERATION_SAVE_STATUS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SAVE_STATUS_RESPONSE",
            "1:FEDERATE_SAVING;2:FEDERATE_INSTRUCTED_TO_SAVE",
        )

        assert wing.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert wing.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="QUERY_FEDERATION_SAVE_STATUS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SAVE_STATUS_RESPONSE",
            "1:FEDERATE_SAVING;2:FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE",
        )

        assert leader.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-MULTI",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-MULTI")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-MULTI")
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-MULTI",
            "Leader",
            "1",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-MULTI",
            "Wing",
            "2",
        )

        assert leader.request(TransportRequest(command="QUERY_FEDERATION_RESTORE_STATUS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_RESTORE_STATUS_RESPONSE",
            "1:1:FEDERATE_RESTORE_REQUEST_PENDING;2:2:FEDERATE_RESTORE_REQUEST_PENDING",
        )
        assert wing.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="QUERY_FEDERATION_RESTORE_STATUS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_RESTORE_STATUS_RESPONSE",
            "1:1:FEDERATE_RESTORE_REQUEST_PENDING;2:2:FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE",
        )
        assert leader.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "queryFederationSaveStatusRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "queryFederationRestoreStatusRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-BND-003",
)
def test_2025_transport_server_completes_restore_after_peer_disconnect_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-restore-peer-disconnect"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "SaveRestore2025.xml"))
        ).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("RestoreLeader", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("RestoreWing", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-DROP-PEER",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DROP-PEER")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DROP-PEER")
        assert leader.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert wing.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert leader.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert wing.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-DROP-PEER",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DROP-PEER")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DROP-PEER")
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DROP-PEER",
            "RestoreLeader",
            "1",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DROP-PEER",
            "RestoreWing",
            "2",
        )

        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert "2" not in server.servicer.restore_status

        assert leader.request(TransportRequest(command="QUERY_FEDERATION_RESTORE_STATUS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_RESTORE_STATUS_RESPONSE",
            "1:1:FEDERATE_RESTORE_REQUEST_PENDING",
        )

        assert leader.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert leader.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "queryFederationRestoreStatusRequest",
            "federateRestoreCompleteRequest",
            "disconnectRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_example_fom_save_restore_gauntlet_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    mirror = None
    sender = None
    observer = None
    federation_name = f"fedpro-2025-save-restore-gauntlet-{uuid.uuid4().hex[:8]}"
    save_name = f"SAVE-GAUNTLET-{uuid.uuid4().hex[:8]}"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        mirror = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        sender = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"))
        ).fields == ()
        owner_handle = owner.request(TransportRequest(command="JOIN", fields=("Owner", "SaveRestoreGauntlet", federation_name))).fields[0]
        mirror_handle = mirror.request(TransportRequest(command="JOIN", fields=("Mirror", "SaveRestoreGauntlet", federation_name))).fields[0]
        sender_handle = sender.request(
            TransportRequest(command="JOIN", fields=("Owner-Sender", "SaveRestoreGauntlet", federation_name))
        ).fields[0]
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("Mirror-Observer", "SaveRestoreGauntlet", federation_name))
        ).fields[0]

        role_ledgers = {
            "owner": {"role": "owner", "random_state": 101, "sequence_counter": 0, "phase": "bootstrap"},
            "mirror": {"role": "mirror", "random_state": 202, "sequence_counter": 0, "phase": "bootstrap"},
            "sender": {"role": "sender", "random_state": 303, "sequence_counter": 0, "phase": "bootstrap"},
            "observer": {"role": "observer", "random_state": 404, "sequence_counter": 0, "phase": "bootstrap"},
        }

        def advance_ledger(ledger: dict[str, object], *, phase: str) -> None:
            next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
            ledger["random_state"] = next_state
            ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
            ledger["phase"] = phase

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        target_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        mirror_target_class = mirror.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        owner_position = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        mirror_position = mirror.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(mirror_target_class, "Position"))).fields[0]
        interaction_class = sender.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        observer_interaction_class = observer.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        interaction_parameter = sender.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        observer_parameter = observer.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(observer_interaction_class, "TrackId"))
        ).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, owner_position))
        ).fields == ()
        assert mirror.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(mirror_target_class, mirror_position))
        ).fields == ()
        assert sender.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(observer_interaction_class,))).fields == ()

        assert owner.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert sender.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert mirror.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert mirror.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert observer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert sender.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(interaction_class, "TIMESTAMP"))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(target_class, "Target-Checkpoint-1"))
        ).fields[0]
        assert mirror.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert owner.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, owner_position, "TIMESTAMP"))).fields == ()
        mirror_object_instance = mirror.request(
            TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=("Target-Checkpoint-1",))
        ).fields[0]

        saved_position = struct.pack(">ddd", 10_000.0, 1_000.0, 2_000.0).hex()
        dirty_position = struct.pack(">ddd", 99_999.0, 88_888.0, 77_777.0).hex()
        branch_position = struct.pack(">ddd", 10_250.0, 1_030.0, 2_000.0).hex()

        update_result = owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(
                    object_instance,
                    f"{owner_position}:{saved_position}",
                    "626173656c696e652d61747472696275746573",
                    "HLAinteger64Time",
                    "4",
                ),
            )
        ).fields
        assert len(update_result) == 1
        send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:626173656c696e652d747261636b",
                    "626173656c696e652d747261636b",
                    "HLAinteger64Time",
                    "5",
                ),
            )
        ).fields
        assert len(send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()

        mirror_callbacks = collect_until_grant(mirror, "5")
        observer_callbacks = collect_until_grant(observer, "5")
        baseline_reflect = [fields for fields in mirror_callbacks if fields[:2] == ("1", "REFLECT_TSO")]
        baseline_interaction = [fields for fields in observer_callbacks if fields[:2] == ("1", "INTERACTION_TSO")]
        assert len(baseline_reflect) == 1
        assert len(baseline_interaction) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert baseline_reflect[0][:5] == (
            "1",
            "REFLECT_TSO",
            mirror_object_instance,
            f"{mirror_position}:{saved_position}",
            "626173656c696e652d61747472696275746573",
        )
        assert baseline_interaction[0][:5] == (
            "1",
            "INTERACTION_TSO",
            observer_interaction_class,
            f"{observer_parameter}:626173656c696e652d747261636b",
            "626173656c696e652d747261636b",
        )

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="saved")
        saved_ledgers = {role: dict(ledger) for role, ledger in role_ledgers.items()}
        saved_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(save_name,))).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_name)
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="dirty")
        dirty_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}
        assert dirty_fingerprints != saved_fingerprints

        dirty_update_result = owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(
                    object_instance,
                    f"{owner_position}:{dirty_position}",
                    "64697274792d61747472696275746573",
                    "HLAinteger64Time",
                    "7",
                ),
            )
        ).fields
        assert len(dirty_update_result) == 1
        dirty_send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:64697274792d747261636b",
                    "64697274792d747261636b",
                    "HLAinteger64Time",
                    "8",
                ),
            )
        ).fields
        assert len(dirty_send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        mirror_dirty_callbacks = collect_until_grant(mirror, "8")
        observer_dirty_callbacks = collect_until_grant(observer, "8")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        dirty_reflect = [fields for fields in mirror_dirty_callbacks if fields[:2] == ("1", "REFLECT_TSO")][-1]
        dirty_interaction = [fields for fields in observer_dirty_callbacks if fields[:2] == ("1", "INTERACTION_TSO")][-1]
        assert dirty_reflect[3] == f"{mirror_position}:{dirty_position}"
        assert dirty_interaction[:5] == (
            "1",
            "INTERACTION_TSO",
            observer_interaction_class,
            f"{observer_parameter}:64697274792d747261636b",
            "64697274792d747261636b",
        )
        assert owner.request(TransportRequest(command="DELETE_OBJECT_INSTANCE", fields=(object_instance, "64697274792d64656c657465"))).fields == ()
        dirty_remove = mirror.request(TransportRequest(command="EVOKE")).fields
        assert dirty_remove[:4] == ("1", "REMOVE_OBJECT_INSTANCE", mirror_object_instance, "64697274792d64656c657465")

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(save_name,))).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", save_name)
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            save_name,
            "Owner",
            owner_handle,
        )
        assert mirror.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            save_name,
            "Mirror",
            mirror_handle,
        )
        assert sender.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            save_name,
            "Owner-Sender",
            sender_handle,
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            save_name,
            "Mirror-Observer",
            observer_handle,
        )
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        restored_times = {
            "owner": owner.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "mirror": mirror.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "sender": sender.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "observer": observer.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
        }
        assert all(fields == ("HLAinteger64Time", "5") for fields in restored_times.values())
        restored_ledgers = {role: dict(ledger) for role, ledger in saved_ledgers.items()}
        assert {role: json.dumps(ledger, sort_keys=True) for role, ledger in restored_ledgers.items()} == saved_fingerprints
        assert owner.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(object_instance,))).fields == (
            "Target-Checkpoint-1",
        )

        branch_update_result = owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(
                    object_instance,
                    f"{owner_position}:{branch_position}",
                    "6272616e63682d61747472696275746573",
                    "HLAinteger64Time",
                    "7",
                ),
            )
        ).fields
        assert len(branch_update_result) == 1
        branch_send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:6272616e63682d747261636b",
                    "6272616e63682d747261636b",
                    "HLAinteger64Time",
                    "7",
                ),
            )
        ).fields
        assert len(branch_send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        branch_mirror_callbacks = collect_until_grant(mirror, "8")
        branch_observer_callbacks = collect_until_grant(observer, "8")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        branch_reflect = [fields for fields in branch_mirror_callbacks if fields[:2] == ("1", "REFLECT_TSO")]
        branch_interaction = [fields for fields in branch_observer_callbacks if fields[:2] == ("1", "INTERACTION_TSO")]
        assert any(branch_position in fields[3] and fields[4] == "6272616e63682d61747472696275746573" for fields in branch_reflect)
        assert any(
            fields[:5]
            == (
                "1",
                "INTERACTION_TSO",
                observer_interaction_class,
                f"{observer_parameter}:6272616e63682d747261636b",
                "6272616e63682d747261636b",
            )
            for fields in branch_interaction
        )
        branch_tags = {fields[4] for fields in branch_reflect}
        branch_tags.update(fields[4] for fields in branch_interaction)
        assert "64697274792d61747472696275746573" not in branch_tags
        assert "64697274792d747261636b" not in branch_tags
        remove_callbacks = [fields for fields in branch_mirror_callbacks if fields[:2] == ("1", "REMOVE_OBJECT_INSTANCE")]
        assert all(fields[3] != "64697274792d64656c657465" for fields in remove_callbacks)
    finally:
        for transport in (owner, mirror, sender, observer):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",)))
            except Exception:
                pass
        if owner is not None:
            try:
                owner.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (owner, mirror, sender, observer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema(tmp_path: Path):
    server = start_2025_grpc_server()
    owner = None
    mirror = None
    sender = None
    observer = None
    smoke_fom = tmp_path / "SmokeSaveRestore2025.xml"
    smoke_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Smoke Save Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused smoke FOM for save/restore ownership rollback.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter>
          <name>TrackId</name>
          <dataType>HLAunicodeString</dataType>
        </parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )
    federation_name = f"fedpro-2025-smoke-ownership-restore-{uuid.uuid4().hex[:8]}"
    save_name = f"SAVE-OWNERSHIP-GAUNTLET-{uuid.uuid4().hex[:8]}"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        mirror = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        sender = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", str(smoke_fom)))).fields == ()
        owner_handle = owner.request(TransportRequest(command="JOIN", fields=("Owner", "SaveRestoreGauntlet", federation_name))).fields[0]
        mirror_handle = mirror.request(TransportRequest(command="JOIN", fields=("Mirror", "SaveRestoreGauntlet", federation_name))).fields[0]
        sender.request(TransportRequest(command="JOIN", fields=("Owner-Sender", "SaveRestoreGauntlet", federation_name))).fields
        observer.request(TransportRequest(command="JOIN", fields=("Mirror-Observer", "SaveRestoreGauntlet", federation_name))).fields

        role_ledgers = {
            "owner": {"role": "owner", "random_state": 111, "sequence_counter": 0, "phase": "bootstrap"},
            "mirror": {"role": "mirror", "random_state": 222, "sequence_counter": 0, "phase": "bootstrap"},
            "sender": {"role": "sender", "random_state": 333, "sequence_counter": 0, "phase": "bootstrap"},
            "observer": {"role": "observer", "random_state": 444, "sequence_counter": 0, "phase": "bootstrap"},
        }

        def advance_ledger(ledger: dict[str, object], *, phase: str) -> None:
            next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
            ledger["random_state"] = next_state
            ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
            ledger["phase"] = phase

        def collect_until_grant(transport: GrpcTransport, logical_time: str, *, limit: int = 8) -> list[tuple[str, ...]]:
            callbacks: list[tuple[str, ...]] = []
            for _ in range(limit):
                fields = transport.request(TransportRequest(command="EVOKE")).fields
                callbacks.append(fields)
                if fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", logical_time):
                    break
            return callbacks

        owner_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        mirror_class = mirror.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        observer_class = observer.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        owner_attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(owner_class, "Position"))).fields[0]
        mirror_attribute = mirror.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(mirror_class, "Position"))).fields[0]
        observer_attribute = observer.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(observer_class, "Position"))).fields[0]
        interaction_class = sender.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        observer_interaction = observer.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        interaction_parameter = sender.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        observer_parameter = observer.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(observer_interaction, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(owner_class, owner_attribute))).fields == ()
        assert mirror.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(mirror_class, mirror_attribute))).fields == ()
        assert mirror.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(mirror_class, mirror_attribute))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(observer_class, observer_attribute))).fields == ()
        assert sender.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(observer_interaction,))).fields == ()

        assert owner.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert sender.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "1"))).fields == ()
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert mirror.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert mirror.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert observer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert sender.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(interaction_class, "TIMESTAMP"))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(owner_class, "Owned-Target-Checkpoint-1"))
        ).fields[0]
        assert mirror.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert owner.request(TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, owner_attribute, "TIMESTAMP"))).fields == ()
        mirror_object_instance = mirror.request(
            TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=("Owned-Target-Checkpoint-1",))
        ).fields[0]
        observer_object_instance = observer.request(
            TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=("Owned-Target-Checkpoint-1",))
        ).fields[0]

        saved_payload = b"saved-payload"
        dirty_payload = b"dirty-payload"
        branch_payload = b"branch-payload"

        update_result = owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{owner_attribute}:{saved_payload.hex()}", b"baseline-attributes".hex(), "HLAinteger64Time", "4"),
            )
        ).fields
        assert len(update_result) == 1
        send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:{b'baseline-message'.hex()}",
                    b"baseline-message".hex(),
                    "HLAinteger64Time",
                    "5",
                ),
            )
        ).fields
        assert len(send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "5"))).fields == ()

        collect_until_grant(mirror, "5")
        observer_callbacks = collect_until_grant(observer, "5")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        baseline_reflect = [fields for fields in observer_callbacks if fields[:2] == ("1", "REFLECT_TSO")]
        baseline_interaction = [fields for fields in observer_callbacks if fields[:2] == ("1", "INTERACTION_TSO")]
        assert len(baseline_reflect) == 1
        assert len(baseline_interaction) == 1
        assert baseline_reflect[0][:5] == (
            "1",
            "REFLECT_TSO",
            observer_object_instance,
            f"{observer_attribute}:{saved_payload.hex()}",
            b"baseline-attributes".hex(),
        )
        assert baseline_interaction[0][:5] == (
            "1",
            "INTERACTION_TSO",
            observer_interaction,
            f"{observer_parameter}:{b'baseline-message'.hex()}",
            b"baseline-message".hex(),
        )
        assert owner.request(TransportRequest(command="IS_ATTRIBUTE_OWNED_BY_FEDERATE", fields=(object_instance, owner_attribute))).fields == ("1",)

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="saved")
        saved_ledgers = {role: dict(ledger) for role, ledger in role_ledgers.items()}
        saved_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in saved_ledgers.items()}

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(save_name,))).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", save_name)
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="dirty")
        dirty_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}
        assert dirty_fingerprints != saved_fingerprints

        assert owner.request(
            TransportRequest(command="UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE", fields=(object_instance, owner_attribute))
        ).fields == ()
        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, owner_attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "ATTRIBUTE_IS_NOT_OWNED", object_instance, owner_attribute)

        assert mirror.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                fields=(mirror_object_instance, mirror_attribute, b"claim".hex()),
            )
        ).fields == ()
        assert mirror.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            mirror_object_instance,
            mirror_attribute,
            b"claim".hex(),
        )
        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, owner_attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            owner_attribute,
            mirror_handle,
        )

        assert mirror.request(
            TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(mirror_object_instance, f"{mirror_attribute}:{dirty_payload.hex()}", b"dirty-attributes".hex()))
        ).fields == ()
        dirty_send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:{b'dirty-message'.hex()}",
                    b"dirty-message".hex(),
                    "HLAinteger64Time",
                    "8",
                ),
            )
        ).fields
        assert len(dirty_send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        collect_until_grant(mirror, "8")
        dirty_observer_callbacks = collect_until_grant(observer, "8")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        dirty_reflect = [fields for fields in dirty_observer_callbacks if fields[:2] == ("1", "REFLECT")][-1]
        dirty_interaction = [fields for fields in dirty_observer_callbacks if fields[:2] == ("1", "INTERACTION_TSO")][-1]
        assert dirty_reflect[3] == f"{observer_attribute}:{dirty_payload.hex()}"
        assert dirty_interaction[:5] == (
            "1",
            "INTERACTION_TSO",
            observer_interaction,
            f"{observer_parameter}:{b'dirty-message'.hex()}",
            b"dirty-message".hex(),
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(save_name,))).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", save_name)
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_RESTORE", save_name, "Owner", owner_handle)
        assert mirror.request(TransportRequest(command="EVOKE")).fields[:4] == ("1", "INITIATE_FEDERATE_RESTORE", save_name, "Mirror")
        assert sender.request(TransportRequest(command="EVOKE")).fields[:4] == ("1", "INITIATE_FEDERATE_RESTORE", save_name, "Owner-Sender")
        assert observer.request(TransportRequest(command="EVOKE")).fields[:4] == ("1", "INITIATE_FEDERATE_RESTORE", save_name, "Mirror-Observer")
        restored_ledgers = {role: dict(ledger) for role, ledger in saved_ledgers.items()}
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        for transport in (owner, mirror, sender, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        restored_times = {
            "owner": owner.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "mirror": mirror.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "sender": sender.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
            "observer": observer.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields,
        }
        assert all(fields == ("HLAinteger64Time", "5") for fields in restored_times.values())
        restored_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in restored_ledgers.items()}
        assert restored_fingerprints == saved_fingerprints

        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, owner_attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            owner_attribute,
            owner_handle,
        )
        assert owner.request(TransportRequest(command="IS_ATTRIBUTE_OWNED_BY_FEDERATE", fields=(object_instance, owner_attribute))).fields == ("1",)

        branch_update_result = owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                fields=(object_instance, f"{owner_attribute}:{branch_payload.hex()}", b"branch-attributes".hex(), "HLAinteger64Time", "7"),
            )
        ).fields
        assert len(branch_update_result) == 1
        branch_send_result = sender.request(
            TransportRequest(
                command="SEND_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    f"{interaction_parameter}:{b'branch-message'.hex()}",
                    b"branch-message".hex(),
                    "HLAinteger64Time",
                    "7",
                ),
            )
        ).fields
        assert len(branch_send_result) == 1
        assert owner.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert sender.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert mirror.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=("HLAinteger64Time", "8"))).fields == ()
        collect_until_grant(mirror, "8")
        branch_observer_callbacks = collect_until_grant(observer, "8")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        assert sender.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "8")
        branch_reflect = [fields for fields in branch_observer_callbacks if fields[:2] == ("1", "REFLECT_TSO")]
        branch_interaction = [fields for fields in branch_observer_callbacks if fields[:2] == ("1", "INTERACTION_TSO")]
        assert any(fields[3] == f"{observer_attribute}:{branch_payload.hex()}" and fields[4] == b"branch-attributes".hex() for fields in branch_reflect)
        assert any(
            fields[:5] == (
                "1",
                "INTERACTION_TSO",
                observer_interaction,
                f"{observer_parameter}:{b'branch-message'.hex()}",
                b"branch-message".hex(),
            )
            for fields in branch_interaction
        )
        branch_tags = {fields[4] for fields in branch_reflect}
        branch_tags.update(fields[4] for fields in branch_interaction)
        assert b"dirty-attributes".hex() not in branch_tags
        assert b"dirty-message".hex() not in branch_tags
    finally:
        for transport, action in (
            (observer, "NO_ACTION"),
            (sender, "NO_ACTION"),
            (mirror, "UNCONDITIONALLY_DIVEST_ATTRIBUTES"),
            (owner, "DELETE_OBJECTS"),
        ):
            if transport is None:
                continue
            try:
                transport.request(TransportRequest(command="RESIGN", fields=(action,)))
            except Exception:
                pass
        if owner is not None:
            try:
                owner.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
            except Exception:
                pass
        for transport in (owner, mirror, sender, observer):
            if transport is not None:
                transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-ownership-restore"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025OwnerRestore", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipRestoreTarget-1"))
        ).fields[0]

        assert (
            transport.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute, "73617665642d6f66666572"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []
        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "73617665642d70656e64696e67"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_DIVESTITURE_CONFIRMATION",
            object_instance,
            attribute,
            "73617665642d70656e64696e67",
        )

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-OWNERSHIP",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OWNERSHIP")
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert (
            transport.request(
                TransportRequest(
                    command="CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION",
            object_instance,
            attribute,
        )
        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "61667465722d63616e63656c"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            object_instance,
            attribute,
            "61667465722d63616e63656c",
        )

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-OWNERSHIP",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OWNERSHIP")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OWNERSHIP",
            "FedPro2025OwnerRestore",
            "1",
        )
        assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "726573746f7265642d6f66666572"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_DIVESTITURE_CONFIRMATION",
            object_instance,
            attribute,
            "726573746f7265642d6f66666572",
        )
        assert transport.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED",
                fields=(object_instance, attribute, "726573746f7265642d70656e64696e67"),
            )
        ).fields == (attribute,)
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "726573746f7265642d70656e64696e67",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "requestFederationRestoreRequest",
            "negotiatedAttributeOwnershipDivestitureRequest",
            "cancelNegotiatedAttributeOwnershipDivestitureRequest",
            "cancelAttributeOwnershipAcquisitionRequest",
            "attributeOwnershipAcquisitionRequest",
            "attributeOwnershipDivestitureIfWantedRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    acquirer = None
    federation_name = "fedpro-2025-owner-visibility-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        acquirer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert acquirer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("Owner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert acquirer.request(
            TransportRequest(command="JOIN", fields=("Acquirer", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnerVisibilityTarget-1"))
        ).fields[0]

        assert owner.request(
            TransportRequest(
                command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                fields=(object_instance, attribute, "6f66666572"),
            )
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            object_instance,
            attribute,
            "6f66666572",
        )
        assert acquirer.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                fields=(object_instance, attribute, "61637175697265"),
            )
        ).fields == ()
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_DIVESTITURE_CONFIRMATION")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_DIVESTITURE_CONFIRMATION",
            object_instance,
            attribute,
            "61637175697265",
        )
        assert owner.request(
            TransportRequest(command="CONFIRM_DIVESTITURE", fields=(object_instance, attribute, "636f6e6669726d"))
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "OWNERSHIP_ACQUIRED")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "636f6e6669726d",
        )
        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            attribute,
            "2",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-OWNER-VIS",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OWNER-VIS")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OWNER-VIS")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert acquirer.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert acquirer.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert owner.request(
            TransportRequest(command="UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE", fields=(object_instance, attribute))
        ).fields == ()
        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_NOT_OWNED",
            object_instance,
            attribute,
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-OWNER-VIS",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OWNER-VIS")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OWNER-VIS")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OWNER-VIS",
            "Owner",
            "1",
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OWNER-VIS",
            "Acquirer",
            "2",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert acquirer.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert owner.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            attribute,
            "2",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert acquirer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "negotiatedAttributeOwnershipDivestitureRequest",
            "attributeOwnershipAcquisitionRequest",
            "confirmDivestitureRequest",
            "queryAttributeOwnershipRequest",
            "requestFederationSaveWithTimeRequest",
            "requestFederationRestoreRequest",
            "unconditionalAttributeOwnershipDivestitureRequest",
        } <= set(server.servicer.calls)
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FI-SVC-129",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-directed-ddm-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedDDMRestore2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("DirectedOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("DirectedA", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("DirectedB", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_a_region = subscriber_a.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_b_region = subscriber_b.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "5:15"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "50:60"))).fields == ()
        assert owner.request(
            TransportRequest(
                command="COMMIT_REGION_MODIFICATIONS",
                fields=(f"{publisher_region},{subscriber_a_region},{subscriber_b_region}",),
            )
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedRestoreTarget-1"))
        ).fields[0]
        assert owner.request(
            TransportRequest(command="ASSOCIATE_REGIONS_FOR_UPDATES", fields=(object_instance, f"{attribute}|{publisher_region}"))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_a_region))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_b_region))
        ).fields == ()

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:5341564544", "736176652d7374617465"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:5341564544",
            "736176652d7374617465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-DIRECTED-DDM",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-DDM")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-DDM")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-DDM")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert subscriber_a.request(
            TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class,))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, subscriber_a_region))
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "8:12"))).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_b_region,))
        ).fields == ()

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:4d555441544544", "6d7574617465642d7374617465"),
            )
        ).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:4d555441544544",
            "6d7574617465642d7374617465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-DIRECTED-DDM",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-DDM")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-DDM")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-DDM")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-DDM",
            "DirectedOwner",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-DDM",
            "DirectedA",
            "2",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-DDM",
            "DirectedB",
            "3",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:524553544f524544", "726573746f7265642d7374617465"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:524553544f524544",
            "726573746f7265642d7374617465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "unsubscribeObjectClassDirectedInteractionsRequest",
            "unsubscribeInteractionClassWithRegionsRequest",
            "sendDirectedInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if subscriber_b is not None:
            subscriber_b.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    observer = None
    federation_name = "fedpro-2025-directed-tso-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert observer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedTSORestore2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("DirectedTSOOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber.request(
            TransportRequest(command="JOIN", fields=("DirectedTSOSubscriber", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("DirectedTSOObserver", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedTSORestoreTarget-1"))
        ).fields[0]

        assert subscriber.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert observer.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        stale_handle = owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    object_instance,
                    f"{parameter}:5354414c45",
                    "7374616c652d74736f",
                    "HLAinteger64Time",
                    "5",
                ),
            )
        ).fields[0]
        assert stale_handle == "1"

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-DIRECTED-TSO",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-TSO")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-TSO")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-DIRECTED-TSO")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-DIRECTED-TSO",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-TSO")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-TSO")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-DIRECTED-TSO")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-TSO",
            "DirectedTSOOwner",
            "1",
        )
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-TSO",
            "DirectedTSOSubscriber",
            "2",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-DIRECTED-TSO",
            "DirectedTSOObserver",
            "3",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert stale_handle not in server.servicer.queued_tso_callbacks
        assert stale_handle not in server.servicer.delivered_retractions

        assert subscriber.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")
        with pytest.raises(TransportError) as stale_error:
            owner.request(TransportRequest(command="RETRACT", fields=(stale_handle,)))
        assert stale_error.value.code == "InvalidMessageRetractionHandle"

        fresh_handle = owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(
                    interaction_class,
                    object_instance,
                    f"{parameter}:4652455348",
                    "66726573682d74736f",
                    "HLAinteger64Time",
                    "7",
                ),
            )
        ).fields[0]
        assert fresh_handle == "2"

        assert subscriber.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "7"))).fields == ()
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION_TSO",
            interaction_class,
            object_instance,
            f"{parameter}:4652455348",
            "66726573682d74736f",
            "2",
            "1",
            "HLAinteger64Time",
            "7",
            "2",
        )
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert observer.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "7"))).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert owner.request(TransportRequest(command="RETRACT", fields=(fresh_handle,))).fields == ()
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_RETRACTION", fresh_handle)
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_RETRACTION")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "sendDirectedInteractionWithTimeRequest",
            "nextMessageRequestRequest",
            "retractRequest",
        } <= set(server.servicer.calls)
    finally:
        if observer is not None:
            observer.close()
        if subscriber is not None:
            subscriber.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-061",
    "HLA2025-FI-SVC-062",
    "HLA2025-FI-SVC-121",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-remove-tso-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DeleteTso2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("TimedRemoveOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("TimedRemoveA", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("TimedRemoveB", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTimedRemoveRestoreTarget-1"))
        ).fields[0]
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTimedRemoveRestoreTarget-1",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTimedRemoveRestoreTarget-1",
        )

        assert subscriber_a.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_b.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-TIMED-REMOVE",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIMED-REMOVE")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIMED-REMOVE")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIMED-REMOVE")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        stale_handle = owner.request(
            TransportRequest(
                command="DELETE_OBJECT_INSTANCE_TIMESTAMP",
                fields=(object_instance, "7374616c652d72656d6f7665", "HLAinteger64Time", "5"),
            )
        ).fields[0]
        assert stale_handle == "1"

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE_TSO",
            object_instance,
            "7374616c652d72656d6f7665",
            "HLAinteger64Time",
            "5",
            "2",
            "2",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5")

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-TIMED-REMOVE",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-TIMED-REMOVE")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-TIMED-REMOVE")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-TIMED-REMOVE")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-TIMED-REMOVE",
            "TimedRemoveOwner",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-TIMED-REMOVE",
            "TimedRemoveA",
            "2",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-TIMED-REMOVE",
            "TimedRemoveB",
            "3",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert stale_handle not in server.servicer.queued_tso_callbacks
        assert stale_handle not in server.servicer.delivered_retractions
        assert stale_handle not in server.servicer.delivered_retraction_targets
        assert stale_handle not in server.servicer.requested_retractions

        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "5"))).fields == ()
        first_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        second_b = subscriber_b.request(TransportRequest(command="EVOKE")).fields
        assert first_b[:2] != ("1", "REMOVE_OBJECT_INSTANCE_TSO")
        assert second_b[:2] != ("1", "REMOVE_OBJECT_INSTANCE_TSO")
        assert ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "5") in {first_b, second_b}

        with pytest.raises(TransportError) as stale_error:
            owner.request(TransportRequest(command="RETRACT", fields=(stale_handle,)))
        assert stale_error.value.code == "InvalidMessageRetractionHandle"

        fresh_handle = owner.request(
            TransportRequest(
                command="DELETE_OBJECT_INSTANCE_TIMESTAMP",
                fields=(object_instance, "66726573682d72656d6f7665", "HLAinteger64Time", "7"),
            )
        ).fields[0]
        assert fresh_handle == "2"

        assert subscriber_a.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "7"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE_TSO",
            object_instance,
            "66726573682d72656d6f7665",
            "HLAinteger64Time",
            "7",
            "2",
            "2",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REMOVE_OBJECT_INSTANCE_TSO")
        assert subscriber_b.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=("HLAinteger64Time", "7"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE_TSO",
            object_instance,
            "66726573682d72656d6f7665",
            "HLAinteger64Time",
            "7",
            "2",
            "2",
            "1",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "deleteObjectInstanceWithTimeRequest",
            "requestFederationSaveWithTimeRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "nextMessageRequestRequest",
        } <= set(server.servicer.calls)
    finally:
        if subscriber_b is not None:
            subscriber_b.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-018",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_clears_stale_plain_callbacks_and_preserves_post_restore_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber = None
    observer = None
    federation_name = "fedpro-2025-plain-callback-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, subscriber, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Interaction2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("PlainRestoreOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber.request(
            TransportRequest(command="JOIN", fields=("PlainRestoreSubscriber", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("PlainRestoreObserver", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert subscriber.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-PLAIN-CALLBACKS",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-PLAIN-CALLBACKS")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-PLAIN-CALLBACKS")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-PLAIN-CALLBACKS")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-PLAIN-CALLBACKS",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-PLAIN-CALLBACKS")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-PLAIN-CALLBACKS")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-PLAIN-CALLBACKS")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-PLAIN-CALLBACKS",
            "PlainRestoreOwner",
            "1",
        )
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-PLAIN-CALLBACKS",
            "PlainRestoreSubscriber",
            "2",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-PLAIN-CALLBACKS",
            "PlainRestoreObserver",
            "3",
        )

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:5354414c45", "7374616c652d706c61696e"),
            )
        ).fields == ()
        assert len(server.servicer.callback_queue) == 1

        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert observer.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert server.servicer.callback_queue == []
        assert subscriber.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:4652455348", "66726573682d706f73742d726573746f7265"),
            )
        ).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert subscriber.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:4652455348",
            "66726573682d706f73742d726573746f7265",
            "1",
            "1",
        )

        for transport in (owner, subscriber, observer):
            assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        for transport in (owner, subscriber, observer):
            assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "sendInteractionRequest",
            "requestFederationSaveWithTimeRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
        } <= set(server.servicer.calls)
    finally:
        if observer is not None:
            observer.close()
        if subscriber is not None:
            subscriber.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-object-routing-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "ObjectRestore2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("ObjectOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("ObjectA", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("ObjectB", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProObjectRestoreTarget-1"))
        ).fields[0]
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES",
                fields=(object_instance, f"{attribute}:5341564544", "73617665642d726f757465"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:5341564544",
            "73617665642d726f757465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-OBJECT-ROUTING",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OBJECT-ROUTING")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OBJECT-ROUTING")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-OBJECT-ROUTING")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert subscriber_a.request(TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES",
                fields=(object_instance, f"{attribute}:4d555441544544", "6d7574617465642d726f757465"),
            )
        ).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:4d555441544544",
            "6d7574617465642d726f757465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-OBJECT-ROUTING",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OBJECT-ROUTING")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OBJECT-ROUTING")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-OBJECT-ROUTING")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OBJECT-ROUTING",
            "ObjectOwner",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OBJECT-ROUTING",
            "ObjectA",
            "2",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-OBJECT-ROUTING",
            "ObjectB",
            "3",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert owner.request(
            TransportRequest(
                command="UPDATE_ATTRIBUTE_VALUES",
                fields=(object_instance, f"{attribute}:524553544f524544", "726573746f7265642d726f757465"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:524553544f524544",
            "726573746f7265642d726f757465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "publishObjectClassAttributesRequest",
            "subscribeObjectClassAttributesRequest",
            "unsubscribeObjectClassAttributesRequest",
            "updateAttributeValuesRequest",
        } <= set(server.servicer.calls)
    finally:
        if subscriber_b is not None:
            subscriber_b.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-134",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-interaction-routing-restore"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_a.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert subscriber_b.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "InteractionRestore2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("InteractionOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("InteractionA", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("InteractionB", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_a_region = subscriber_a.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_b_region = subscriber_b.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "5:15"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "50:60"))).fields == ()
        assert owner.request(
            TransportRequest(
                command="COMMIT_REGION_MODIFICATIONS",
                fields=(f"{publisher_region},{subscriber_a_region},{subscriber_b_region}",),
            )
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_a_region))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_b_region))
        ).fields == ()

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_WITH_REGIONS",
                fields=(interaction_class, f"{parameter}:5341564544", publisher_region, "73617665642d696e746572616374696f6e"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:5341564544",
            "73617665642d696e746572616374696f6e",
            "1",
            "1",
            f"{dimension}:0:10",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-INTERACTION-ROUTING",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-INTERACTION-ROUTING")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-INTERACTION-ROUTING")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-INTERACTION-ROUTING")
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert owner.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert subscriber_a.request(
            TransportRequest(command="UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, subscriber_a_region))
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "8:12"))).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_b_region,))
        ).fields == ()
        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_WITH_REGIONS",
                fields=(interaction_class, f"{parameter}:4d555441544544", publisher_region, "6d7574617465642d696e746572616374696f6e"),
            )
        ).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:4d555441544544",
            "6d7574617465642d696e746572616374696f6e",
            "1",
            "1",
            f"{dimension}:0:10",
        )

        assert owner.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-INTERACTION-ROUTING",))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-INTERACTION-ROUTING")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-INTERACTION-ROUTING")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-INTERACTION-ROUTING")
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-INTERACTION-ROUTING",
            "InteractionOwner",
            "1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-INTERACTION-ROUTING",
            "InteractionA",
            "2",
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-INTERACTION-ROUTING",
            "InteractionB",
            "3",
        )
        assert owner.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_a.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert subscriber_b.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_WITH_REGIONS",
                fields=(interaction_class, f"{parameter}:524553544f524544", publisher_region, "726573746f7265642d696e746572616374696f6e"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:524553544f524544",
            "726573746f7265642d696e746572616374696f6e",
            "1",
            "1",
            f"{dimension}:0:10",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "unsubscribeInteractionClassWithRegionsRequest",
            "sendInteractionWithRegionsRequest",
        } <= set(server.servicer.calls)
    finally:
        if subscriber_b is not None:
            subscriber_b.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if owner is not None:
            owner.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_time_and_switch_control_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-control-restore"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "ControlRestore2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("ControlRestore", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        assert transport.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert transport.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert transport.request(TransportRequest(command="ENABLE_ASYNCHRONOUS_DELIVERY")).fields == ()
        assert transport.request(TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("1",))).fields == ()
        assert transport.request(TransportRequest(command="SET_EXCEPTION_REPORTING_SWITCH", fields=("1",))).fields == ()
        assert transport.request(TransportRequest(command="SET_AUTOMATIC_RESIGN_DIRECTIVE", fields=("DELETE_OBJECTS",))).fields == ()
        assert transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "2")
        assert transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)
        assert transport.request(TransportRequest(command="GET_EXCEPTION_REPORTING_SWITCH")).fields == ("1",)
        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("DELETE_OBJECTS",)
        assert server.servicer.time_regulating is True
        assert server.servicer.time_constrained is True
        assert server.servicer.asynchronous_delivery_enabled is True

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-CONTROL",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-CONTROL")
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert transport.request(TransportRequest(command="MODIFY_LOOKAHEAD", fields=("HLAinteger64Interval", "7"))).fields == ()
        assert transport.request(TransportRequest(command="DISABLE_ASYNCHRONOUS_DELIVERY")).fields == ()
        assert transport.request(TransportRequest(command="DISABLE_TIME_CONSTRAINED")).fields == ()
        assert transport.request(TransportRequest(command="DISABLE_TIME_REGULATION")).fields == ()
        assert transport.request(TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("0",))).fields == ()
        assert transport.request(TransportRequest(command="SET_EXCEPTION_REPORTING_SWITCH", fields=("0",))).fields == ()
        assert transport.request(TransportRequest(command="SET_AUTOMATIC_RESIGN_DIRECTIVE", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "7")
        assert transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("0",)
        assert transport.request(TransportRequest(command="GET_EXCEPTION_REPORTING_SWITCH")).fields == ("0",)
        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("NO_ACTION",)
        assert server.servicer.time_regulating is False
        assert server.servicer.time_constrained is False
        assert server.servicer.asynchronous_delivery_enabled is False

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-CONTROL",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-CONTROL")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-CONTROL",
            "ControlRestore",
            "1",
        )
        assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "2")
        assert transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)
        assert transport.request(TransportRequest(command="GET_EXCEPTION_REPORTING_SWITCH")).fields == ("1",)
        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("DELETE_OBJECTS",)
        assert server.servicer.time_regulating is True
        assert server.servicer.time_constrained is True
        assert server.servicer.asynchronous_delivery_enabled is True

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "enableTimeRegulationRequest",
            "enableTimeConstrainedRequest",
            "enableAsynchronousDeliveryRequest",
            "setServiceReportingSwitchRequest",
            "setExceptionReportingSwitchRequest",
            "setAutomaticResignDirectiveRequest",
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "modifyLookaheadRequest",
            "disableAsynchronousDeliveryRequest",
            "disableTimeConstrainedRequest",
            "disableTimeRegulationRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "queryLookaheadRequest",
            "getServiceReportingSwitchRequest",
            "getExceptionReportingSwitchRequest",
            "getAutomaticResignDirectiveRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-FI-SVC-122",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_per_federate_time_state_and_flush_grant_targeting_over_fedpro_schema():
    server = start_2025_grpc_server()
    left = None
    right = None
    federation_name = "fedpro-2025-time-restore-isolation"
    try:
        left = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        right = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert left.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert right.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert left.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "TimeServices2025.xml"))
        ).fields == ()
        assert left.request(
            TransportRequest(command="JOIN", fields=("RestoreTimeLeft", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert right.request(
            TransportRequest(command="JOIN", fields=("RestoreTimeRight", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert left.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "2"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert right.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Interval", "5"))).fields == ()
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")

        assert left.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "4"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "9"))).fields == ()
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "9")

        assert left.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-TIME-ISOLATION",))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIME-ISOLATION")
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIME-ISOLATION")
        assert left.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert right.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert left.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert right.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert left.request(TransportRequest(command="MODIFY_LOOKAHEAD", fields=("HLAinteger64Interval", "7"))).fields == ()
        assert right.request(TransportRequest(command="MODIFY_LOOKAHEAD", fields=("HLAinteger64Interval", "11"))).fields == ()
        assert left.request(TransportRequest(command="FLUSH_QUEUE_REQUEST", fields=("HLAinteger64Time", "20"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FLUSH_QUEUE_GRANT",
            "HLAinteger64Time",
            "20",
            "HLAinteger64Time",
            "20",
        )
        assert right.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "18"))).fields == ()
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "18")
        assert left.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "7")
        assert right.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "11")

        assert left.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-TIME-ISOLATION",))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-TIME-ISOLATION")
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-TIME-ISOLATION")
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert left.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-TIME-ISOLATION",
            "RestoreTimeLeft",
            "1",
        )
        assert right.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-TIME-ISOLATION",
            "RestoreTimeRight",
            "2",
        )
        assert left.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert right.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")
        assert right.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert left.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "9")
        assert left.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "2")
        assert right.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "5")
        assert left.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "6")

        assert server.servicer.handle_current_times["1"].data == b"HLAinteger64Time:4"
        assert server.servicer.handle_current_times["2"].data == b"HLAinteger64Time:9"
        assert server.servicer.handle_lookahead["1"].data == b"HLAinteger64Interval:2"
        assert server.servicer.handle_lookahead["2"].data == b"HLAinteger64Interval:5"

        assert right.request(TransportRequest(command="FLUSH_QUEUE_REQUEST", fields=("HLAinteger64Time", "12"))).fields == ()
        assert left.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FLUSH_QUEUE_GRANT")
        assert right.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FLUSH_QUEUE_GRANT",
            "HLAinteger64Time",
            "12",
            "HLAinteger64Time",
            "12",
        )
        assert left.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields == ("HLAinteger64Time", "12")
        assert left.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "4")
        assert right.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "6")

        assert left.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert right.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert right.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert left.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert right.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "enableTimeRegulationRequest",
            "timeAdvanceRequestRequest",
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "modifyLookaheadRequest",
            "flushQueueRequestRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "queryLogicalTimeRequest",
            "queryLookaheadRequest",
            "queryGALTRequest",
        } <= set(server.servicer.calls)
    finally:
        if right is not None:
            right.close()
        if left is not None:
            left.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-068",
    "HLA2025-FI-SVC-069",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-FI-SVC-072",
    "HLA2025-FI-SVC-073",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-policy-restore"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "PolicyRestore2025.xml"))
        ).fields == ()
        federate_handle = transport.request(
            TransportRequest(command="JOIN", fields=("PolicyRestore", "TestFederate", federation_name))
        ).fields[0]

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProPolicyRestoreTarget-1"))
        ).fields[0]
        interaction_class = transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        best_effort = transport.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_HANDLE", fields=("HLAbestEffort",))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(
            TransportRequest(
                command="REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
                fields=(object_instance, attribute, best_effort),
            )
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
            object_instance,
            attribute,
            best_effort,
        )
        assert transport.request(
            TransportRequest(command="REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE", fields=(interaction_class, best_effort))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
            interaction_class,
            best_effort,
        )
        assert transport.request(
            TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, attribute, "TIMESTAMP"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(interaction_class, "TIMESTAMP"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", fields=(object_instance, attribute))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE",
            object_instance,
            attribute,
            best_effort,
        )
        assert transport.request(
            TransportRequest(command="QUERY_INTERACTION_TRANSPORTATION_TYPE", fields=(federate_handle, interaction_class))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_INTERACTION_TRANSPORTATION_TYPE",
            federate_handle,
            interaction_class,
            best_effort,
        )
        assert server.servicer.default_attribute_order[(object_instance, attribute)] == datatypes_pb2.TIMESTAMP
        assert server.servicer.interaction_order == (interaction_class, datatypes_pb2.TIMESTAMP)

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-POLICY",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "SAVE-POLICY")
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert transport.request(
            TransportRequest(command="REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE", fields=(object_instance, attribute, "1"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
            object_instance,
            attribute,
            "1",
        )
        assert transport.request(
            TransportRequest(command="REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE", fields=(interaction_class, "1"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
            interaction_class,
            "1",
        )
        assert transport.request(
            TransportRequest(command="CHANGE_ATTRIBUTE_ORDER_TYPE", fields=(object_instance, attribute, "RECEIVE"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(interaction_class, "RECEIVE"))
        ).fields == ()

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-POLICY",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-POLICY")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-POLICY",
            "PolicyRestore",
            federate_handle,
        )
        assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert transport.request(
            TransportRequest(command="QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", fields=(object_instance, attribute))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE",
            object_instance,
            attribute,
            best_effort,
        )
        assert transport.request(
            TransportRequest(command="QUERY_INTERACTION_TRANSPORTATION_TYPE", fields=(federate_handle, interaction_class))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_INTERACTION_TRANSPORTATION_TYPE",
            federate_handle,
            interaction_class,
            best_effort,
        )
        assert server.servicer.default_attribute_order[(object_instance, attribute)] == datatypes_pb2.TIMESTAMP
        assert server.servicer.interaction_order == (interaction_class, datatypes_pb2.TIMESTAMP)

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "requestAttributeTransportationTypeChangeRequest",
            "queryAttributeTransportationTypeRequest",
            "requestInteractionTransportationTypeChangeRequest",
            "queryInteractionTransportationTypeRequest",
            "changeAttributeOrderTypeRequest",
            "changeInteractionOrderTypeRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-193",
    "HLA2025-FI-SVC-194",
    "HLA2025-BND-003",
)
def test_2025_transport_server_restore_recovers_callback_delivery_policy_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-callback-restore"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "CallbackRestore2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("CallbackRestore", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        interaction_class = transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        server.servicer.callback_queue.clear()

        assert transport.request(TransportRequest(command="DISABLE_CALLBACKS")).fields == ()
        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:5341564544", "73617665642d6362"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("SAVE-CALLBACKS",))).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN")).fields == ()
        assert transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE")).fields == ()
        server.servicer.callback_queue.clear()

        assert transport.request(TransportRequest(command="ENABLE_CALLBACKS")).fields == ()
        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:4d555441544544", "6d7574617465642d6362"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:4d555441544544",
            "6d7574617465642d6362",
            "1",
            "1",
        )

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("SAVE-CALLBACKS",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "REQUEST_FEDERATION_RESTORE_SUCCEEDED", "SAVE-CALLBACKS")
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "SAVE-CALLBACKS",
            "CallbackRestore",
            "1",
        )
        assert transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )
        server.servicer.callback_queue.clear()

        assert (
            transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:524553544f524544", "726573746f7265642d6362"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )
        assert transport.request(TransportRequest(command="ENABLE_CALLBACKS")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:524553544f524544",
            "726573746f7265642d6362",
            "1",
            "1",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disableCallbacksRequest",
            "enableCallbacksRequest",
            "requestFederationSaveWithTimeRequest",
            "federateSaveBegunRequest",
            "federateSaveCompleteRequest",
            "requestFederationRestoreRequest",
            "federateRestoreCompleteRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-006",
    "HLA2025-FI-SVC-007",
    "HLA2025-FI-SVC-004",
    "HLA2025-FI-SVC-008",
    "HLA2025-FI-SVC-009",
    "HLA2025-FI-SVC-010",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_federation_reporting_callbacks_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-federation-reporting"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Lifecycle2025.xml"))
        ).fields == ()

        assert leader.request(
            TransportRequest(command="JOIN", fields=("Leader", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("Wing", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert leader.request(TransportRequest(command="LIST_FEDERATION_EXECUTIONS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_FEDERATION_EXECUTIONS",
            f"{federation_name}:HLAinteger64Time",
        )

        assert leader.request(
            TransportRequest(command="LIST_FEDERATION_EXECUTION_MEMBERS", fields=(federation_name,))
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_FEDERATION_EXECUTION_MEMBERS",
            federation_name,
            "Leader:TestFederate;Wing:Observer",
        )

        assert leader.request(
            TransportRequest(command="LIST_FEDERATION_EXECUTION_MEMBERS", fields=(f"{federation_name}-missing",))
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_FEDERATION_EXECUTION_DOES_NOT_EXIST",
            f"{federation_name}-missing",
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        with pytest.raises(TransportError) as error:
            leader.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
        assert error.value.code == "FederatesCurrentlyJoined"
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "listFederationExecutionsRequest",
            "listFederationExecutionMembersRequest",
            "resignFederationExecutionRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-193",
    "HLA2025-FI-SVC-194",
    "HLA2025-FI-SVC-195",
    "HLA2025-FI-SVC-196",
    "HLA2025-NEW-002",
    "HLA2025-BND-003",
)
def test_2025_transport_server_isolates_requester_and_disabled_callbacks_per_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-callback-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Lifecycle2025.xml"))
        ).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("Leader", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("Wing", "Publisher", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        server.servicer.callback_queue.clear()
        assert leader.request(TransportRequest(command="DISABLE_CALLBACKS")).fields == ()
        assert wing.request(TransportRequest(command="LIST_FEDERATION_EXECUTIONS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_FEDERATION_EXECUTIONS",
            f"{federation_name}:HLAinteger64Time",
        )

        interaction_class = leader.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert wing.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        assert wing.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:69736f6c61746564", "63616c6c6261636b2d746167"),
            )
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert leader.request(TransportRequest(command="ENABLE_CALLBACKS")).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:69736f6c61746564",
            "63616c6c6261636b2d746167",
            "1",
            "1",
        )

        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disableCallbacksRequest",
            "enableCallbacksRequest",
            "listFederationExecutionsRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-011",
    "HLA2025-NEW-002",
    "HLA2025-NEW-003",
    "HLA2025-BND-003",
)
def test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-lifecycle-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Lifecycle2025.xml"))
        ).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("Leader", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("Wing", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(
            TransportRequest(command="LIST_FEDERATION_EXECUTION_MEMBERS", fields=(federation_name,))
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_FEDERATION_EXECUTION_MEMBERS",
            federation_name,
            "Wing:Observer",
        )
        with pytest.raises(TransportError) as error:
            wing.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
        assert error.value.code == "FederatesCurrentlyJoined"

        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "listFederationExecutionMembersRequest",
            "resignFederationExecutionRequest",
            "destroyFederationExecutionRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-138",
    "HLA2025-FI-SVC-156",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-transport-query-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Support2025.xml"))
        ).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("Leader", "TestFederate", federation_name))
        ).fields[0]
        assert wing.request(
            TransportRequest(command="JOIN", fields=("Wing", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        object_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = leader.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTransportQueryTarget-1"))
        ).fields[0]
        interaction_class = leader.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        transportation = leader.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_HANDLE", fields=("HLAbestEffort",))).fields[0]

        assert leader.request(
            TransportRequest(
                command="REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
                fields=(object_instance, attribute, transportation),
            )
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
        )
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
            object_instance,
            attribute,
            transportation,
        )

        assert leader.request(
            TransportRequest(command="QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", fields=(object_instance, attribute))
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE")
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE",
            object_instance,
            attribute,
            transportation,
        )

        assert leader.request(
            TransportRequest(
                command="REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
                fields=(interaction_class, transportation),
            )
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
        )
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
            interaction_class,
            transportation,
        )

        assert leader.request(
            TransportRequest(
                command="QUERY_INTERACTION_TRANSPORTATION_TYPE",
                fields=(leader_handle, interaction_class),
            )
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REPORT_INTERACTION_TRANSPORTATION_TYPE")
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_INTERACTION_TRANSPORTATION_TYPE",
            leader_handle,
            interaction_class,
            transportation,
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "requestAttributeTransportationTypeChangeRequest",
            "queryAttributeTransportationTypeRequest",
            "requestInteractionTransportationTypeChangeRequest",
            "queryInteractionTransportationTypeRequest",
        } <= set(server.servicer.calls)
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-051",
    "HLA2025-FI-SVC-052",
    "HLA2025-FI-SVC-053",
    "HLA2025-FI-SVC-054",
    "HLA2025-FI-SVC-055",
    "HLA2025-FI-SVC-056",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_object_instance_name_reservation_flow_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-name-reservations"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025Names", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        object_class = transport.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))
        ).fields[0]

        reserved_name = "FedProReservedTarget-1"
        assert transport.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            reserved_name,
        )

        assert transport.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
            reserved_name,
        )

        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="RELEASE_OBJECT_INSTANCE_NAME", fields=("NotReserved-1",)))
        assert error.value.code == "ObjectInstanceNameNotReserved"

        assert transport.request(TransportRequest(command="RELEASE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert transport.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            reserved_name,
        )

        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, reserved_name))
        ).fields[0]
        assert object_instance
        assert transport.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
            reserved_name,
        )

        names = "FedProReserve-A,FedProReserve-B"
        assert transport.request(TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            names,
        )
        assert transport.request(TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
            names,
        )

        with pytest.raises(TransportError) as error:
            transport.request(TransportRequest(command="RELEASE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=("Missing-A,Missing-B",)))
        assert error.value.code == "ObjectInstanceNameNotReserved"

        assert transport.request(TransportRequest(command="RELEASE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert transport.request(TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            names,
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "reserveObjectInstanceNameRequest",
            "releaseObjectInstanceNameRequest",
            "reserveMultipleObjectInstanceNamesRequest",
            "releaseMultipleObjectInstanceNamesRequest",
            "registerObjectInstanceWithNameRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-042",
    "HLA2025-FI-SVC-048",
    "HLA2025-FI-SVC-050",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_turn_updates_advisory_callbacks_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-turn-updates"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025TurnUpdates", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        object_class = transport.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))
        ).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]

        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProTurnUpdatesTarget-1"))
        ).fields[0]

        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_RATE",
                    fields=(object_class, attribute, "fast"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProTurnUpdatesTarget-1",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
            "fast",
        )

        assert transport.request(
            TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATE_RESIGNED", "NO_ACTION")
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "subscribeObjectClassAttributesWithRateRequest",
            "unsubscribeObjectClassAttributesRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-051",
    "HLA2025-FI-SVC-052",
    "HLA2025-FI-SVC-054",
    "HLA2025-FI-SVC-055",
    "HLA2025-BND-003",
)
def test_2025_transport_server_isolates_name_reservation_callbacks_per_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    rival = None
    federation_name = "fedpro-2025-name-reservation-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        rival = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert rival.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025NamesOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert rival.request(
            TransportRequest(command="JOIN", fields=("FedPro2025NamesRival", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        reserved_name = "FedProIsolatedName-1"
        assert owner.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert rival.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
        )
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            reserved_name,
        )

        assert rival.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(reserved_name,))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
        )
        assert len(server.servicer.callback_queue) == 1
        assert rival.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
            reserved_name,
        )

        names = "FedProIsoMulti-A,FedProIsoMulti-B"
        assert rival.request(TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
        )
        assert len(server.servicer.callback_queue) == 1
        assert rival.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED",
            names,
        )

        assert owner.request(TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(names,))).fields == ()
        assert rival.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
        )
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_FAILED",
            names,
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert rival.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert rival.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert rival.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if rival is not None:
            rival.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-084",
    "HLA2025-FI-SVC-085",
    "HLA2025-FI-SVC-086",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-088",
    "HLA2025-FI-SVC-089",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-091",
    "HLA2025-FI-SVC-092",
    "HLA2025-FI-SVC-094",
    "HLA2025-FI-SVC-095",
    "HLA2025-FI-SVC-096",
    "HLA2025-FI-SVC-097",
    "HLA2025-FI-SVC-098",
    "HLA2025-FI-SVC-099",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    acquirer = None
    federation_name = "fedpro-2025-negotiated-ownership"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        acquirer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert acquirer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025Owner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert acquirer.request(TransportRequest(command="JOIN", fields=("FedPro2025Acquirer", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipTarget-1"))
        ).fields[0]

        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                    fields=(object_instance, attribute, "6f776e6564"),
                )
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ATTRIBUTE_OWNERSHIP_UNAVAILABLE")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_OWNERSHIP_UNAVAILABLE",
            object_instance,
            attribute,
            "6f776e6564",
        )

        assert acquirer.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            attribute,
            "1",
        )

        assert (
            owner.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute, "6f66666572"),
                )
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            object_instance,
            attribute,
            "6f66666572",
        )
        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "61637175697265"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_DIVESTITURE_CONFIRMATION")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_DIVESTITURE_CONFIRMATION",
            object_instance,
            attribute,
            "61637175697265",
        )
        assert (
            owner.request(
                TransportRequest(command="CONFIRM_DIVESTITURE", fields=(object_instance, attribute, "636f6e6669726d"))
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "OWNERSHIP_ACQUIRED")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "636f6e6669726d",
        )

        pending_object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipPending-1"))
        ).fields[0]

        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(pending_object_instance, attribute, "72656c65617365"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            pending_object_instance,
            attribute,
            "72656c65617365",
        )
        assert (
            owner.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_RELEASE_DENIED",
                    fields=(pending_object_instance, attribute, "64656e696564"),
                )
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ATTRIBUTE_OWNERSHIP_UNAVAILABLE")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_OWNERSHIP_UNAVAILABLE",
            pending_object_instance,
            attribute,
            "64656e696564",
        )

        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(pending_object_instance, attribute, "63616e63656c"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            pending_object_instance,
            attribute,
        )
        assert (
            acquirer.request(
                TransportRequest(command="CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION", fields=(pending_object_instance, attribute))
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != (
            "1",
            "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION",
        )
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION",
            pending_object_instance,
            attribute,
        )

        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(pending_object_instance, attribute, "7265747279"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            pending_object_instance,
            attribute,
        )
        assert owner.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED",
                fields=(pending_object_instance, attribute, "646976657374"),
            )
        ).fields == (attribute,)
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "OWNERSHIP_ACQUIRED")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            pending_object_instance,
            attribute,
            "646976657374",
        )

        cancelled_offer_object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipCancelledOffer-1"))
        ).fields[0]

        assert (
            owner.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(cancelled_offer_object_instance, attribute, "63616e63656c2d6f66666572"),
                )
            ).fields
            == ()
        )
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION")
        assert len(server.servicer.callback_queue) == 1
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            cancelled_offer_object_instance,
            attribute,
        )
        assert (
            owner.request(
                TransportRequest(
                    command="CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(cancelled_offer_object_instance, attribute),
                )
            ).fields
            == ()
        )
        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(cancelled_offer_object_instance, attribute, "61667465722d63616e63656c"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            cancelled_offer_object_instance,
            attribute,
            "61667465722d63616e63656c",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert acquirer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "attributeOwnershipAcquisitionIfAvailableRequest",
            "queryAttributeOwnershipRequest",
            "negotiatedAttributeOwnershipDivestitureRequest",
            "attributeOwnershipAcquisitionRequest",
            "confirmDivestitureRequest",
            "attributeOwnershipReleaseDeniedRequest",
            "cancelAttributeOwnershipAcquisitionRequest",
            "attributeOwnershipDivestitureIfWantedRequest",
            "cancelNegotiatedAttributeOwnershipDivestitureRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if acquirer is not None:
            acquirer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-094",
    "HLA2025-BND-003",
)
def test_2025_transport_server_drops_pending_ownership_requester_after_disconnect_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    acquirer = None
    federation_name = "fedpro-2025-ownership-disconnect-cleanup"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        acquirer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert acquirer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DisconnectOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        acquirer_handle = acquirer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DisconnectAcquirer", "TestFederate", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipDisconnect-1"))
        ).fields[0]

        assert (
            acquirer.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "646973636f6e6e6563742d61637175697265"),
                )
            ).fields
            == ()
        )
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE")
        assert len(server.servicer.callback_queue) == 1
        assert owner.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            object_instance,
            attribute,
        )
        assert server.servicer.pending_attribute_requesters[(object_instance, attribute)] == acquirer_handle

        assert acquirer.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert acquirer_handle not in server.servicer.peer_federate_handles.values()
        assert server.servicer.pending_attribute_acquisitions == {}
        assert server.servicer.pending_attribute_requesters == {}

        assert (
            owner.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_RELEASE_DENIED",
                    fields=(object_instance, attribute, "646973636f6e6e6563742d64656e696564"),
                )
            ).fields
            == ()
        )
        assert server.servicer.attribute_owners[(object_instance, attribute)] == "1"
        assert all(
            callback.WhichOneof("callbackRequest") != "attributeOwnershipUnavailable"
            for callback in server.servicer.callback_queue
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "attributeOwnershipAcquisitionRequest",
            "attributeOwnershipReleaseDeniedRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if acquirer is not None:
            acquirer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-084",
    "HLA2025-FI-SVC-087",
    "HLA2025-BND-003",
)
def test_2025_transport_server_releases_owned_attributes_when_owner_disconnects_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    acquirer = None
    federation_name = "fedpro-2025-ownership-owner-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        acquirer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert acquirer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        owner_handle = owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025GoneOwner", "TestFederate", federation_name))
        ).fields[0]
        assert acquirer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025SurvivingAcquirer", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipGoneOwner-1"))
        ).fields[0]
        assert server.servicer.attribute_owners[(object_instance, attribute)] == owner_handle

        assert owner.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert owner_handle not in server.servicer.peer_federate_handles.values()

        assert acquirer.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_NOT_OWNED",
            object_instance,
            attribute,
        )

        assert acquirer.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                fields=(object_instance, attribute, "646973636f6e6e6563742d61637661696c"),
            )
        ).fields == ()
        assert server.servicer.attribute_owners[(object_instance, attribute)] == "2"
        assert (object_instance, attribute) not in server.servicer.unowned_attributes
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "646973636f6e6e6563742d61637661696c",
        )

        assert acquirer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert acquirer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "queryAttributeOwnershipRequest",
            "attributeOwnershipAcquisitionIfAvailableRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if acquirer is not None:
            acquirer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-085",
    "HLA2025-FI-SVC-088",
    "HLA2025-BND-003",
)
def test_2025_transport_server_clears_offered_ownership_state_when_owner_disconnects_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    acquirer = None
    federation_name = "fedpro-2025-ownership-offer-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        acquirer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert acquirer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        owner_handle = owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025OfferOwner", "TestFederate", federation_name))
        ).fields[0]
        assert acquirer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025OfferAcquirer", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipOfferDisconnect-1"))
        ).fields[0]

        assert owner.request(
            TransportRequest(
                command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                fields=(object_instance, attribute, "6f666665722d646973636f6e6e656374"),
            )
        ).fields == ()
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION")
        assert acquirer.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            object_instance,
            attribute,
        )
        assert (object_instance, attribute) in server.servicer.offered_attributes

        assert owner.request(TransportRequest(command="DISCONNECT", fields=())).fields == ()
        assert owner_handle not in server.servicer.peer_federate_handles.values()
        assert (object_instance, attribute) not in server.servicer.offered_attributes

        assert acquirer.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_NOT_OWNED",
            object_instance,
            attribute,
        )

        assert acquirer.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                fields=(object_instance, attribute, "6f666665722d61637661696c"),
            )
        ).fields == ()
        assert acquirer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "6f666665722d61637661696c",
        )
        assert all(
            callback.WhichOneof("callbackRequest") != "requestDivestitureConfirmation"
            for callback in server.servicer.callback_queue
        )

        assert acquirer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert acquirer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert acquirer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "negotiatedAttributeOwnershipDivestitureRequest",
            "queryAttributeOwnershipRequest",
            "attributeOwnershipAcquisitionIfAvailableRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if acquirer is not None:
            acquirer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-087",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_attribute_ownership_query_callbacks_only_to_requester_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    requester = None
    bystander = None
    federation_name = "fedpro-2025-ownership-query-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        requester = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        bystander = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, requester, bystander):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedProOwnershipOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert requester.request(
            TransportRequest(command="JOIN", fields=("FedProOwnershipRequester", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert bystander.request(
            TransportRequest(command="JOIN", fields=("FedProOwnershipBystander", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipQueryTarget-1"))
        ).fields[0]

        assert requester.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert bystander.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INFORM_ATTRIBUTE_OWNERSHIP")
        assert requester.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            attribute,
            "1",
        )

        assert owner.request(
            TransportRequest(command="UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE", fields=(object_instance, attribute))
        ).fields == ()
        assert requester.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert bystander.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ATTRIBUTE_IS_NOT_OWNED")
        assert requester.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_NOT_OWNED",
            object_instance,
            attribute,
        )

        mom_object = owner.request(
            TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=(federation_name,))
        ).fields[0]
        federation_class = owner.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.HLAmanager.HLAfederation",))
        ).fields[0]
        federation_name_attribute = owner.request(
            TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(federation_class, "HLAfederationName"))
        ).fields[0]
        assert requester.request(
            TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(mom_object, federation_name_attribute))
        ).fields == ()
        assert bystander.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ATTRIBUTE_IS_OWNED_BY_RTI")
        assert requester.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_OWNED_BY_RTI",
            mom_object,
            federation_name_attribute,
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert requester.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert bystander.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert bystander.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert requester.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert bystander.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {"queryAttributeOwnershipRequest"} <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if requester is not None:
            requester.close()
        if bystander is not None:
            bystander.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-100",
    "HLA2025-BND-003",
)
def test_2025_transport_server_applies_resign_ownership_policy_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)

        for federation_name, federate_name, object_name, resign_action in (
            (
                "fedpro-2025-resign-divest",
                "FedPro2025Divest",
                "FedProDivestTarget-1",
                "UNCONDITIONALLY_DIVEST_ATTRIBUTES",
            ),
            (
                "fedpro-2025-resign-delete",
                "FedPro2025Delete",
                "FedProDeleteTarget-1",
                "DELETE_OBJECTS",
            ),
            (
                "fedpro-2025-resign-cancel",
                "FedPro2025Cancel",
                "FedProCancelTarget-1",
                "CANCEL_PENDING_OWNERSHIP_ACQUISITIONS",
            ),
        ):
            assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))).fields == ()
            join_fields = transport.request(TransportRequest(command="JOIN", fields=(federate_name, "TestFederate", federation_name))).fields
            assert join_fields[1] == "HLAinteger64Time"
            object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
            attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
            object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, object_name))).fields[0]
            if resign_action == "CANCEL_PENDING_OWNERSHIP_ACQUISITIONS":
                assert (
                    transport.request(
                        TransportRequest(
                            command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                            fields=(object_instance, attribute, "70656e64696e67"),
                        )
                    ).fields
                    == ()
                )
                assert transport.request(TransportRequest(command="EVOKE")).fields[:4] == (
                    "1",
                    "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
                    object_instance,
                    attribute,
                )

            assert transport.request(TransportRequest(command="RESIGN", fields=(resign_action,))).fields == ()
            assert transport.request(TransportRequest(command="EVOKE")).fields == (
                "1",
                "FEDERATE_RESIGNED",
                resign_action,
            )

            if resign_action == "UNCONDITIONALLY_DIVEST_ATTRIBUTES":
                assert transport.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
                assert transport.request(TransportRequest(command="EVOKE")).fields == (
                    "1",
                    "ATTRIBUTE_IS_NOT_OWNED",
                    object_instance,
                    attribute,
                )
            elif resign_action == "DELETE_OBJECTS":
                with pytest.raises(TransportError) as error:
                    transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(object_instance,)))
                assert error.value.code == "ObjectInstanceNotKnown"
            else:
                assert transport.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
                assert transport.request(TransportRequest(command="EVOKE")).fields == (
                    "1",
                    "INFORM_ATTRIBUTE_OWNERSHIP",
                    object_instance,
                    attribute,
                    join_fields[0],
                )

            assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()

        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert {
            "resignFederationExecutionRequest",
            "queryAttributeOwnershipRequest",
            "getObjectInstanceNameRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_reports_rti_owned_mom_attribute_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-rti-owned-mom"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomOwnership2025.xml"))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")

        federation_class = transport.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.HLAmanager.HLAfederation",))
        ).fields[0]
        federation_name_attribute = transport.request(
            TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(federation_class, "HLAfederationName"))
        ).fields[0]
        mom_object = server.servicer.mom_federation_object_handle

        assert mom_object is not None
        assert transport.request(
            TransportRequest(command="IS_ATTRIBUTE_OWNED_BY_FEDERATE", fields=(mom_object, federation_name_attribute))
        ).fields == ("0",)
        assert transport.request(
            TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(mom_object, federation_name_attribute))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_IS_OWNED_BY_RTI",
            mom_object,
            federation_name_attribute,
        )

        assert {
            "getObjectClassHandleRequest",
            "getAttributeHandleRequest",
            "isAttributeOwnedByFederateRequest",
            "queryAttributeOwnershipRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-049",
    "HLA2025-FI-SVC-050",
    "HLA2025-FI-SVC-137",
    "HLA2025-FI-SVC-128",
    "HLA2025-FI-SVC-131",
    "HLA2025-FI-SVC-133",
    "HLA2025-BND-003",
)
def test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-ddm"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "RegionDDM2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025DDM", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert transport.request(TransportRequest(command="SET_ATTRIBUTE_SCOPE_ADVISORY_SWITCH", fields=("1",))).fields == ()

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        publisher_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "50:60"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{subscriber_region}",))).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDDMTarget-1"))).fields[0]
        assert (
            transport.request(
                TransportRequest(
                    command="ASSOCIATE_REGIONS_FOR_UPDATES",
                    fields=(object_instance, f"{attribute}|{publisher_region}"),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                    fields=(object_class, f"{attribute}|{subscriber_region}", "1"),
                )
            ).fields
            == ()
        )

        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:6f757473696465", "6f7574736964652d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "5:15"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_region,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                    fields=(object_class, f"{attribute}|{subscriber_region}", "1"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_IN_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProDDMTarget-1",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:696e73696465", "696e736964652d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:696e73696465",
            "696e736964652d746167",
            "1",
            "1",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="REQUEST_ATTRIBUTE_VALUE_UPDATE_WITH_REGIONS",
                    fields=(object_class, f"{attribute}|{subscriber_region}", "726567696f6e2d726571"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            object_instance,
            attribute,
            "726567696f6e2d726571",
        )
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "50:60"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_region,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_OUT_OF_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                    fields=(object_class, f"{attribute}|{subscriber_region}"),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:756e737562", "756e7375622d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                    fields=(object_class, f"{attribute}|{subscriber_region}", "1"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "5:15"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_region,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_IN_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UNASSOCIATE_REGIONS_FOR_UPDATES",
                    fields=(object_instance, f"{attribute}|{publisher_region}"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_OUT_OF_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:756e6173736f63", "756e6173736f632d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="ASSOCIATE_REGIONS_FOR_UPDATES",
                    fields=(object_instance, f"{attribute}|{publisher_region}"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_IN_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="DELETE_REGION", fields=(subscriber_region,))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_OUT_OF_SCOPE",
            object_instance,
            attribute,
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES",
                    fields=(object_instance, f"{attribute}:64656c65746564", "64656c657465642d746167"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "createRegionRequest",
            "setRangeBoundsRequest",
            "commitRegionModificationsRequest",
            "associateRegionsForUpdatesRequest",
            "requestAttributeValueUpdateWithRegionsRequest",
            "unassociateRegionsForUpdatesRequest",
            "setAttributeScopeAdvisorySwitchRequest",
            "subscribeObjectClassAttributesWithRegionsRequest",
            "unsubscribeObjectClassAttributesWithRegionsRequest",
            "deleteRegionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-074",
    "HLA2025-FI-SVC-075",
    "HLA2025-FI-SVC-050",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_attribute_scope_advisories_only_to_overlapping_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    federation_name = "fedpro-2025-ddm-scope-routing"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, subscriber_a, subscriber_b):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "RegionDDMScope2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025DDMOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DDMSubscriberA", "TestFederate", federation_name))
        ).fields == (
            "2",
            "HLAinteger64Time",
        )
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DDMSubscriberB", "TestFederate", federation_name))
        ).fields == (
            "3",
            "HLAinteger64Time",
        )

        for transport in (subscriber_a, subscriber_b):
            assert transport.request(TransportRequest(command="SET_ATTRIBUTE_SCOPE_ADVISORY_SWITCH", fields=("1",))).fields == ()

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_a_region = subscriber_a.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_b_region = subscriber_b.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "5:15"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "50:60"))).fields == ()
        assert owner.request(
            TransportRequest(
                command="COMMIT_REGION_MODIFICATIONS",
                fields=(f"{publisher_region},{subscriber_a_region},{subscriber_b_region}",),
            )
        ).fields == ()

        object_instance = owner.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDDMScopeTarget-1"))).fields[0]
        assert owner.request(
            TransportRequest(
                command="ASSOCIATE_REGIONS_FOR_UPDATES",
                fields=(object_instance, f"{attribute}|{publisher_region}"),
            )
        ).fields == ()

        assert subscriber_a.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(object_class, f"{attribute}|{subscriber_a_region}", "1"),
            )
        ).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_IN_SCOPE",
            object_instance,
            attribute,
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProDDMScopeTarget-1",
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )

        assert subscriber_b.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(object_class, f"{attribute}|{subscriber_b_region}", "1"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_ADVANCE_GRANT",
            "HLAinteger64Time",
            "7",
        )

        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "50:60"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "5:15"))).fields == ()
        assert owner.request(
            TransportRequest(
                command="COMMIT_REGION_MODIFICATIONS",
                fields=(f"{subscriber_a_region},{subscriber_b_region}",),
            )
        ).fields == ()

        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_OUT_OF_SCOPE",
            object_instance,
            attribute,
        )
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTES_IN_SCOPE",
            object_instance,
            attribute,
        )
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE",
            object_instance,
            attribute,
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "createRegionRequest",
            "setRangeBoundsRequest",
            "commitRegionModificationsRequest",
            "associateRegionsForUpdatesRequest",
            "setAttributeScopeAdvisorySwitchRequest",
            "subscribeObjectClassAttributesWithRegionsRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        server.close()


def test_2025_transport_server_filters_interactions_by_ddm_region_overlap():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-interaction-ddm"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "InteractionDDM2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025InteractionDDM", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert transport.request(TransportRequest(command="GET_AVAILABLE_DIMENSIONS_FOR_INTERACTION_CLASS", fields=(interaction_class,))).fields == (dimension,)
        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        publisher_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "50:60"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{subscriber_region}",))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, "1", subscriber_region),
                )
            ).fields
            == ()
        )

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS",
                    fields=(interaction_class, f"{parameter}:4e4f2d44454c49564552", publisher_region, "6e6f2d64656c69766572"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "5:15"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_region,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS",
                    fields=(interaction_class, f"{parameter}:44454c49564552", publisher_region, "64656c69766572"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:44454c49564552",
            "64656c69766572",
            "1",
            "1",
            f"{dimension}:0:10",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, subscriber_region),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS",
                    fields=(interaction_class, f"{parameter}:554e535542", publisher_region, "756e737562"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, "1", subscriber_region),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="DELETE_REGION", fields=(subscriber_region,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS",
                    fields=(interaction_class, f"{parameter}:44454c455445", publisher_region, "64656c657465"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert {
            "getAvailableDimensionsForInteractionClassRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "unsubscribeInteractionClassWithRegionsRequest",
            "sendInteractionWithRegionsRequest",
            "deleteRegionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-134",
    "HLA2025-BND-003",
)
def test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    observer = None
    federation_name = "fedpro-2025-interaction-ddm-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert observer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "InteractionDDM2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025InteractionDDMOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025InteractionDDMObserver", "Observer", federation_name))
        ).fields[0]

        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        observer_region = observer.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert observer.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(observer_region, dimension, "5:15"))).fields == ()
        assert owner.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{observer_region}",))
        ).fields == ()
        assert observer.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", observer_region))
        ).fields == ()

        assert observer_handle in server.servicer.handle_subscribed_interactions
        assert server.servicer.handle_subscribed_interaction_regions[observer_handle][interaction_class] == {observer_region}

        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer_handle not in server.servicer.handle_subscribed_interactions
        assert observer_handle not in server.servicer.handle_subscribed_interaction_regions
        assert observer_handle not in server.servicer.peer_federate_handles.values()

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION_WITH_REGIONS",
                fields=(interaction_class, f"{parameter}:444953434f4e4e4543544544", publisher_region, "646973636f6e6e6563746564"),
            )
        ).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "sendInteractionWithRegionsRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-129",
    "HLA2025-BND-003",
)
def test_2025_transport_server_filters_directed_interactions_by_ddm_region_overlap():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-directed-ddm"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedDDM2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDM", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]

        assert transport.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert transport.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        publisher_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "50:60"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{subscriber_region}",))).fields == ()

        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedDDMTarget-1"))).fields[0]
        assert (
            transport.request(
                TransportRequest(
                    command="ASSOCIATE_REGIONS_FOR_UPDATES",
                    fields=(object_instance, f"{attribute}|{publisher_region}"),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, "1", subscriber_region),
                )
            ).fields
            == ()
        )

        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:4e4f2d444952454354", "6f757473696465"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []

        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_region, dimension, "5:15"))).fields == ()
        assert transport.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(subscriber_region,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:444952454354", "696e73696465"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:444952454354",
            "696e73696465",
            "1",
            "1",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, subscriber_region),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:554e535542", "756e737562"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []

        assert (
            transport.request(
                TransportRequest(
                    command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                    fields=(interaction_class, "1", subscriber_region),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="DELETE_REGION", fields=(subscriber_region,))).fields == ()
        assert (
            transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(interaction_class, object_instance, f"{parameter}:44454c455445", "64656c657465"),
                )
            ).fields
            == ()
        )
        assert server.servicer.callback_queue == []

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "associateRegionsForUpdatesRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "unsubscribeInteractionClassWithRegionsRequest",
            "sendDirectedInteractionRequest",
            "deleteRegionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-129",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    subscriber_a = None
    subscriber_b = None
    observer = None
    federation_name = "fedpro-2025-directed-ddm-routing"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_a = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        subscriber_b = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, subscriber_a, subscriber_b, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedDDMRouting2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDMOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert subscriber_a.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDM-A", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert subscriber_b.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDM-B", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDMObserver", "TestFederate", federation_name))
        ).fields == ("4", "HLAinteger64Time")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_a_region = subscriber_a.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        subscriber_b_region = subscriber_b.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        observer_region = observer.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]

        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "5:15"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "50:60"))).fields == ()
        assert observer.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(observer_region, dimension, "5:15"))).fields == ()
        assert owner.request(
            TransportRequest(
                command="COMMIT_REGION_MODIFICATIONS",
                fields=(f"{publisher_region},{subscriber_a_region},{subscriber_b_region},{observer_region}",),
            )
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedDDMRoutingTarget-1"))
        ).fields[0]
        assert owner.request(
            TransportRequest(command="ASSOCIATE_REGIONS_FOR_UPDATES", fields=(object_instance, f"{attribute}|{publisher_region}"))
        ).fields == ()

        assert subscriber_a.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_a_region))
        ).fields == ()
        assert subscriber_b.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", subscriber_b_region))
        ).fields == ()
        assert observer.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", observer_region))
        ).fields == ()

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:4f5645524c4150", "66697273742d726f757465"),
            )
        ).fields == ()
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:4f5645524c4150",
            "66697273742d726f757465",
            "1",
            "1",
        )

        assert subscriber_a.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_a_region, dimension, "70:80"))).fields == ()
        assert subscriber_b.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(subscriber_b_region, dimension, "8:12"))).fields == ()
        assert subscriber_a.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{subscriber_a_region},{subscriber_b_region}",))
        ).fields == ()

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:5348494654", "7365636f6e642d726f757465"),
            )
        ).fields == ()
        assert subscriber_a.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")
        assert len(server.servicer.callback_queue) == 1
        assert subscriber_b.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:5348494654",
            "7365636f6e642d726f757465",
            "1",
            "1",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_a.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert subscriber_b.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_a.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert subscriber_b.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "associateRegionsForUpdatesRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "sendDirectedInteractionRequest",
            "commitRegionModificationsRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if subscriber_a is not None:
            subscriber_a.close()
        if subscriber_b is not None:
            subscriber_b.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-129",
    "HLA2025-BND-003",
)
def test_2025_transport_server_removes_disconnected_directed_ddm_subscriber_from_delivery_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    observer = None
    federation_name = "fedpro-2025-directed-ddm-disconnect"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert observer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedDDM2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDMDisconnectOwner", "Controller", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedDDMDisconnectObserver", "Observer", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        dimension = owner.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]

        assert owner.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert observer.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        publisher_region = owner.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        observer_region = observer.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert owner.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(publisher_region, dimension, "0:10"))).fields == ()
        assert observer.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(observer_region, dimension, "5:15"))).fields == ()
        assert owner.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(f"{publisher_region},{observer_region}",))
        ).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProDirectedDDMDisconnectTarget-1"))
        ).fields[0]
        assert owner.request(
            TransportRequest(command="ASSOCIATE_REGIONS_FOR_UPDATES", fields=(object_instance, f"{attribute}|{publisher_region}"))
        ).fields == ()
        assert observer.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(interaction_class, "1", observer_region))
        ).fields == ()

        assert observer_handle in server.servicer.handle_subscribed_directed_interactions
        assert server.servicer.handle_subscribed_directed_interactions[observer_handle][object_class] == {interaction_class}
        assert server.servicer.handle_subscribed_interaction_regions[observer_handle][interaction_class] == {observer_region}

        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer_handle not in server.servicer.handle_subscribed_directed_interactions
        assert observer_handle not in server.servicer.handle_subscribed_interactions
        assert observer_handle not in server.servicer.handle_subscribed_interaction_regions
        assert observer_handle not in server.servicer.peer_federate_handles.values()

        assert owner.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:44495245435445442d444953434f4e4e454354", "64697265637465642d646973636f6e6e656374"),
            )
        ).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DIRECTED_INTERACTION")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "disconnectRequest",
            "publishObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "sendDirectedInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if owner is not None:
            owner.close()
        if observer is not None:
            observer.close()
        server.close()


def test_2025_transport_server_reports_mom_service_invocation_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Mom2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MOM", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation",),
            )
        ).fields[0]
        federate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        service_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAservice"))).fields[0]
        serial_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAserialNumber"))).fields[0]

        assert transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("0",)
        assert transport.request(TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("1",))).fields == ()
        assert transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)

        assert transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields == ("101",)
        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report == (
            "1",
            "INTERACTION",
            report_class,
            f"{federate_param}:31,{service_param}:6765744f626a656374436c61737348616e646c65,{serial_param}:31",
            "4d4f4d",
            "1",
            "1",
        )

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "getServiceReportingSwitchRequest",
            "setServiceReportingSwitchRequest",
            "getObjectClassHandleRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-FI-SVC-165", "HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_routes_mom_service_reports_only_to_enabled_federates_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-service-routing"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomRouting2025.xml"))).fields == ()
        assert leader.request(TransportRequest(command="JOIN", fields=("FedPro2025Leader", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        assert wing.request(TransportRequest(command="JOIN", fields=("FedPro2025Wing", "TestFederate", federation_name))).fields == (
            "2",
            "HLAinteger64Time",
        )

        report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation",),
            )
        ).fields[0]
        federate_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        service_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAservice"))).fields[0]
        serial_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAserialNumber"))).fields[0]

        assert leader.request(TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("1",))).fields == ()
        assert leader.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)
        assert wing.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("0",)

        assert wing.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields == ("101",)
        leader_report = leader.request(TransportRequest(command="EVOKE")).fields
        assert leader_report[:4] == (
            "1",
            "INTERACTION",
            report_class,
            f"{federate_param}:32,{service_param}:6765744f626a656374436c61737348616e646c65,{serial_param}:31",
        )
        assert leader_report[4:] == ("4d4f4d", "1", "1")
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert wing.request(TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("1",))).fields == ()
        assert wing.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)

        assert leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields == ("101",)
        leader_report = leader.request(TransportRequest(command="EVOKE")).fields
        wing_report = wing.request(TransportRequest(command="EVOKE")).fields
        for report in (leader_report, wing_report):
            assert report[:4] == (
                "1",
                "INTERACTION",
                report_class,
                f"{federate_param}:31,{service_param}:6765744f626a656374436c61737348616e646c65,{serial_param}:32",
            )
            assert report[4:] == ("4d4f4d", "1", "1")

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "getInteractionClassHandleRequest",
            "getParameterHandleRequest",
            "getServiceReportingSwitchRequest",
            "setServiceReportingSwitchRequest",
            "getObjectClassHandleRequest",
        } <= set(server.servicer.calls)
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


def test_2025_transport_server_reports_mim_data_for_mom_request_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-mim"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomMim2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MIM", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata",),
            )
        ).fields[0]
        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata",),
            )
        ).fields[0]
        mim_data_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAMIMdata"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        assert transport.request(TransportRequest(command="SEND_INTERACTION", fields=(request_class, "", "6d696d2d72657175657374"))).fields == ()

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        assert report[3].startswith(f"{mim_data_param}:")
        assert bytes.fromhex(report[3].split(":", 1)[1]).decode("ascii") == (
            "HLAstandardMIM-2025 HLAmanager HLArequestMIMdata HLAreportMIMdata"
        )
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "getInteractionClassHandleRequest",
            "getParameterHandleRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_reports_synchronization_points_for_mom_requests_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-sync-points"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomSync2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Sync", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        assert transport.request(
            TransportRequest(command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT", fields=("ReadyToRun", "73796e63", "1"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "SYNC_POINT_REGISTRATION_SUCCEEDED",
            "ReadyToRun",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )
        assert transport.request(
            TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )

        points_request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints",),
            )
        ).fields[0]
        points_report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints",),
            )
        ).fields[0]
        points_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(points_report_class, "HLAsynchronizationPoints"))
        ).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(points_report_class,))).fields == ()

        assert transport.request(
            TransportRequest(command="SEND_INTERACTION", fields=(points_request_class, "", "73796e632d706f696e74732d726571"))
        ).fields == ()
        points_report = transport.request(TransportRequest(command="EVOKE")).fields
        assert points_report[:3] == ("1", "INTERACTION", points_report_class)
        points_payloads = dict(item.split(":", 1) for item in points_report[3].split(","))
        assert bytes.fromhex(points_payloads[points_param]).decode("ascii") == "ReadyToRun"
        assert points_report[4:] == ("4d4f4d", "1", "1")

        status_request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus",),
            )
        ).fields[0]
        status_request_label = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_request_class, "HLAlabel"))
        ).fields[0]
        status_report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus",),
            )
        ).fields[0]
        status_label = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAlabel"))).fields[0]
        status_federates = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAfederateList"))
        ).fields[0]
        status_list = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAfederateSynchronizationStatusList"))
        ).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(status_report_class,))).fields == ()

        assert transport.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(status_request_class, f"{status_request_label}:5265616479546f52756e", "73796e632d7374617475732d726571"),
            )
        ).fields == ()
        status_report = transport.request(TransportRequest(command="EVOKE")).fields
        assert status_report[:3] == ("1", "INTERACTION", status_report_class)
        status_payloads = dict(item.split(":", 1) for item in status_report[3].split(","))
        assert bytes.fromhex(status_payloads[status_label]).decode("ascii") == "ReadyToRun"
        assert bytes.fromhex(status_payloads[status_federates]).decode("ascii") == "1"
        assert bytes.fromhex(status_payloads[status_list]).decode("ascii") == "ReadyToRun:1:achieved"
        assert status_report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "registerFederationSynchronizationPointWithSetRequest",
            "synchronizationPointAchievedRequest",
            "getInteractionClassHandleRequest",
            "getParameterHandleRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-013",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
    "HLA2025-FI-SVC-017",
    "HLA2025-BND-003",
)
def test_2025_transport_server_fans_out_mom_sync_status_reports_only_to_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    member = None
    observer = None
    federation_name = "fedpro-2025-mom-sync-status-fanout"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        member = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomSync2025.xml"))
        ).fields == ()

        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMSyncLeader", "TestFederate", federation_name))
        ).fields[0]
        member_handle = member.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMSyncMember", "TestFederate", federation_name))
        ).fields[0]
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMSyncObserver", "TestFederate", federation_name))
        ).fields[0]
        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == (
                "1",
                "TIME_ADVANCE_GRANT",
                "HLAinteger64Time",
                "7",
            )

        assert leader.request(
            TransportRequest(
                command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT",
                fields=("ReadyToRun", "73796e63", f"{leader_handle},{member_handle}"),
            )
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "SYNC_POINT_REGISTRATION_SUCCEEDED",
            "ReadyToRun",
        )
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )
        assert member.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ANNOUNCE_SYNC_POINT")

        assert leader.request(TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))).fields == ()
        assert member.request(TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )
        assert member.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SYNCHRONIZED")

        status_request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus",),
            )
        ).fields[0]
        status_request_label = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_request_class, "HLAlabel"))
        ).fields[0]
        status_report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus",),
            )
        ).fields[0]
        status_label = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAlabel"))).fields[0]
        status_federates = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAfederateList"))
        ).fields[0]
        status_list = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(status_report_class, "HLAfederateSynchronizationStatusList"))
        ).fields[0]

        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(status_report_class,))).fields == ()
        assert member.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(status_report_class,))).fields == ()

        assert observer_handle == "3"
        assert leader.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(status_request_class, f"{status_request_label}:5265616479546f52756e", "6d6f6d2d7374617475732d726571"),
            )
        ).fields == ()

        leader_report = leader.request(TransportRequest(command="EVOKE")).fields
        member_report = member.request(TransportRequest(command="EVOKE")).fields
        observer_report = observer.request(TransportRequest(command="EVOKE")).fields

        for report in (leader_report, member_report):
            assert report[:3] == ("1", "INTERACTION", status_report_class)
            payloads = dict(item.split(":", 1) for item in report[3].split(","))
            assert bytes.fromhex(payloads[status_label]).decode("ascii") == "ReadyToRun"
            assert bytes.fromhex(payloads[status_federates]).decode("ascii") == f"{leader_handle},{member_handle}"
            assert bytes.fromhex(payloads[status_list]).decode("ascii") == (
                f"ReadyToRun:{leader_handle}:achieved,{member_handle}:achieved"
            )
            assert report[4:] == ("4d4f4d", "1", "1")
        assert observer_report[:2] != ("1", "INTERACTION")

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert member.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert member.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "registerFederationSynchronizationPointWithSetRequest",
            "synchronizationPointAchievedRequest",
            "getInteractionClassHandleRequest",
            "getParameterHandleRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if leader is not None:
            leader.close()
        if member is not None:
            member.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_preserves_plain_mom_report_delivery_with_mixed_region_subscribers_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    plain = None
    regional = None
    federation_name = "fedpro-2025-mom-mixed-report-subscribers"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        plain = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        regional = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (leader, plain, regional):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomMixedSubscribers2025.xml"))
        ).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMMixedLeader", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert plain.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMMixedPlain", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert regional.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMMixedRegional", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        for transport in (leader, plain, regional):
            assert transport.request(TransportRequest(command="EVOKE")).fields == (
                "1",
                "TIME_ADVANCE_GRANT",
                "HLAinteger64Time",
                "7",
            )

        assert leader.request(
            TransportRequest(command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT", fields=("ReadyToRun", "73796e63", "1,2,3"))
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "SYNC_POINT_REGISTRATION_SUCCEEDED",
            "ReadyToRun",
        )
        for transport in (leader, plain, regional):
            assert transport.request(TransportRequest(command="EVOKE")).fields == (
                "1",
                "ANNOUNCE_SYNC_POINT",
                "ReadyToRun",
                "73796e63",
            )

        report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints",),
            )
        ).fields[0]
        request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints",),
            )
        ).fields[0]
        points_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAsynchronizationPoints"))
        ).fields[0]
        dimension = regional.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        region = regional.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]

        assert plain.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()
        assert regional.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(region, dimension, "0:10"))).fields == ()
        assert regional.request(TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(region,))).fields == ()
        assert regional.request(
            TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", fields=(report_class, "1", region))
        ).fields == ()

        assert leader.request(
            TransportRequest(command="SEND_INTERACTION", fields=(request_class, "", "6d6f6d2d6d697865642d726571"))
        ).fields == ()

        plain_report = plain.request(TransportRequest(command="EVOKE")).fields
        assert plain_report[:3] == ("1", "INTERACTION", report_class)
        plain_payloads = dict(item.split(":", 1) for item in plain_report[3].split(","))
        assert bytes.fromhex(plain_payloads[points_param]).decode("ascii") == "ReadyToRun"
        assert plain_report[4:] == ("4d4f4d", "1", "1")

        assert regional.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        for transport in (leader, plain, regional):
            assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert regional.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        for transport in (leader, plain, regional):
            assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "registerFederationSynchronizationPointWithSetRequest",
            "getInteractionClassHandleRequest",
            "getParameterHandleRequest",
            "subscribeInteractionClassRequest",
            "subscribeInteractionClassWithRegionsRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if leader is not None:
            leader.close()
        if plain is not None:
            plain.close()
        if regional is not None:
            regional.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_removes_mom_resigned_federate_from_delivery_state_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    observer = None
    federation_name = "fedpro-2025-mom-resign-state-cleanup"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(transport: GrpcTransport, scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(transport: GrpcTransport, interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                )
            ).fields == ()

        assert owner.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert observer.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        assert owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomResignOwner", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomResignObserver", "Observer", federation_name))
        ).fields[0]
        assert owner.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert observer.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        interaction_class = owner.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = owner.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert owner.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        resign_service = mom_class(observer, "HLAfederate", "HLAservice", "HLAresignFederationExecution")
        send_mom(
            observer,
            resign_service,
            {"HLAfederate": observer_handle, "HLAresignAction": "NO_ACTION"},
        )

        assert observer_handle not in server.servicer.handle_subscribed_interactions
        assert observer_handle not in server.servicer.peer_federate_handles.values()

        assert owner.request(
            TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:52455349474e4544", "6d6f6d2d72657369676e"))
        ).fields == ()
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert owner.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()

        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert {"HLAresignFederationExecution"} <= routed
    finally:
        if owner is not None:
            owner.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-100",
    "HLA2025-BND-003",
)
def test_2025_transport_server_applies_mom_resign_policy_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-resign-policy"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                )
            ).fields == ()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        federate_handle = transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomResignPolicy", "TestFederate", federation_name))
        ).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProMomResignDeleteTarget-1"))
        ).fields[0]
        assert transport.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                fields=(object_instance, attribute, "70656e64696e67"),
            )
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            object_instance,
            attribute,
        )

        resign_service = mom_class("HLAfederate", "HLAservice", "HLAresignFederationExecution")
        send_mom(
            resign_service,
            {
                "HLAfederate": federate_handle,
                "HLAresignAction": "CANCEL_THEN_DELETE_THEN_DIVEST",
            },
        )

        with pytest.raises(TransportError) as object_error:
            transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(object_instance,)))
        assert object_error.value.code == "ObjectInstanceNotKnown"
        assert server.servicer.pending_attribute_acquisitions == {}
        assert server.servicer.pending_attribute_requesters == {}
        assert (object_instance, attribute) not in server.servicer.attribute_owners
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert {"HLAresignFederationExecution"} <= routed
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-013",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
    "HLA2025-FI-SVC-017",
    "HLA2025-BND-003",
)
def test_2025_transport_server_emits_synchronization_callbacks_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-sync-callbacks"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "SyncCallbacks2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025SyncCallbacks", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        assert transport.request(
            TransportRequest(command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT", fields=("ReadyToRun", "73796e63"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "SYNC_POINT_REGISTRATION_SUCCEEDED",
            "ReadyToRun",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )

        assert transport.request(TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )
        assert server.servicer.callback_queue == []

        assert {
            "registerFederationSynchronizationPointWithSetRequest",
            "synchronizationPointAchievedRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-013",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
    "HLA2025-FI-SVC-017",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    member = None
    observer = None
    federation_name = "fedpro-2025-sync-target-set"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        member = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "SyncCallbacks2025.xml"))
        ).fields == ()

        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025SyncLeader", "TestFederate", federation_name))
        ).fields[0]
        member_handle = member.request(
            TransportRequest(command="JOIN", fields=("FedPro2025SyncMember", "TestFederate", federation_name))
        ).fields[0]
        observer_handle = observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025SyncObserver", "TestFederate", federation_name))
        ).fields[0]
        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="EVOKE")).fields == (
                "1",
                "TIME_ADVANCE_GRANT",
                "HLAinteger64Time",
                "7",
            )

        assert leader.request(
            TransportRequest(
                command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT",
                fields=("ReadyToRun", "73796e63", f"{leader_handle},{member_handle}"),
            )
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "SYNC_POINT_REGISTRATION_SUCCEEDED",
            "ReadyToRun",
        )
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )
        assert member.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ANNOUNCE_SYNC_POINT",
            "ReadyToRun",
            "73796e63",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "ANNOUNCE_SYNC_POINT")

        assert server.servicer.synchronization_points["ReadyToRun"]["federates"] == {leader_handle, member_handle}

        assert leader.request(TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SYNCHRONIZED")
        assert member.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SYNCHRONIZED")
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SYNCHRONIZED")

        assert member.request(TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=("ReadyToRun", "1"))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )
        assert member.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "FEDERATION_SYNCHRONIZED",
            "ReadyToRun",
            "",
        )
        assert observer.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SYNCHRONIZED")

        assert observer_handle not in server.servicer.synchronization_points["ReadyToRun"]["federates"]
        assert server.servicer.callback_queue == []

        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        for transport in (leader, member, observer):
            assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "registerFederationSynchronizationPointWithSetRequest",
            "synchronizationPointAchievedRequest",
        } <= set(server.servicer.calls)
    finally:
        if leader is not None:
            leader.close()
        if member is not None:
            member.close()
        if observer is not None:
            observer.close()
        server.close()


def test_2025_transport_server_decodes_request_retraction_callback_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        server.servicer.callback_queue.append(
            callback_pb2.CallbackRequest(
                requestRetraction=callback_pb2.RequestRetraction(
                    retraction=datatypes_pb2.MessageRetractionHandle(data=b"42")
                )
            )
        )

        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_RETRACTION",
            "42",
        )
        assert server.servicer.callback_queue == []
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_decoder_preserves_direct_callback_context_details():
    conveyed = datatypes_pb2.ConveyedRegionSet(
        conveyedRegions=[
            datatypes_pb2.ConveyedRegion(
                dimensionAndRange=[
                    datatypes_pb2.DimensionAndRange(
                        dimensionHandle=datatypes_pb2.DimensionHandle(data=b"700"),
                        rangeBounds=datatypes_pb2.RangeBounds(lower=5, upper=15),
                    )
                ]
            )
        ]
    )
    reflect = callback_pb2.CallbackRequest(
        reflectAttributeValuesWithTime=callback_pb2.ReflectAttributeValuesWithTime(
            objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
            attributeValues=datatypes_pb2.AttributeHandleValueMap(
                attributeHandleValue=[
                    datatypes_pb2.AttributeHandleValue(
                        attributeHandle=datatypes_pb2.AttributeHandle(data=b"5"),
                        value=b"inside",
                    )
                ]
            ),
            userSuppliedTag=b"reflect-tag",
            transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
            producingFederate=datatypes_pb2.FederateHandle(data=b"3"),
            optionalSentRegions=conveyed,
            time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:10"),
            sentOrderType=datatypes_pb2.TIMESTAMP,
            receivedOrderType=datatypes_pb2.TIMESTAMP,
            optionalRetraction=datatypes_pb2.MessageRetractionHandle(data=b"41"),
        )
    )
    interaction = callback_pb2.CallbackRequest(
        receiveInteractionWithTime=callback_pb2.ReceiveInteractionWithTime(
            interactionClass=datatypes_pb2.InteractionClassHandle(data=b"11"),
            parameterValues=datatypes_pb2.ParameterHandleValueMap(
                parameterHandleValue=[
                    datatypes_pb2.ParameterHandleValue(
                        parameterHandle=datatypes_pb2.ParameterHandle(data=b"9"),
                        value=b"track",
                    )
                ]
            ),
            userSuppliedTag=b"interaction-tag",
            transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
            producingFederate=datatypes_pb2.FederateHandle(data=b"3"),
            optionalSentRegions=conveyed,
            time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:12"),
            sentOrderType=datatypes_pb2.TIMESTAMP,
            receivedOrderType=datatypes_pb2.TIMESTAMP,
            optionalRetraction=datatypes_pb2.MessageRetractionHandle(data=b"42"),
        )
    )
    directed = callback_pb2.CallbackRequest(
        receiveDirectedInteractionWithTime=callback_pb2.ReceiveDirectedInteractionWithTime(
            interactionClass=datatypes_pb2.InteractionClassHandle(data=b"11"),
            objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
            parameterValues=datatypes_pb2.ParameterHandleValueMap(
                parameterHandleValue=[
                    datatypes_pb2.ParameterHandleValue(
                        parameterHandle=datatypes_pb2.ParameterHandle(data=b"9"),
                        value=b"track-directed",
                    )
                ]
            ),
            userSuppliedTag=b"directed-tag",
            transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
            producingFederate=datatypes_pb2.FederateHandle(data=b"3"),
            time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:13"),
            sentOrderType=datatypes_pb2.TIMESTAMP,
            receivedOrderType=datatypes_pb2.TIMESTAMP,
            optionalRetraction=datatypes_pb2.MessageRetractionHandle(data=b"43"),
        )
    )
    remove = callback_pb2.CallbackRequest(
        removeObjectInstanceWithTime=callback_pb2.RemoveObjectInstanceWithTime(
            objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
            userSuppliedTag=b"gone",
            producingFederate=datatypes_pb2.FederateHandle(data=b"3"),
            time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:14"),
            sentOrderType=datatypes_pb2.TIMESTAMP,
            receivedOrderType=datatypes_pb2.TIMESTAMP,
            optionalRetraction=datatypes_pb2.MessageRetractionHandle(data=b"44"),
        )
    )

    assert decode_callback_request_details(reflect) == {
        "kind": "reflectAttributeValuesWithTime",
        "object_instance": "17",
        "attribute_values": "5:696e73696465",
        "user_supplied_tag": "7265666c6563742d746167",
        "transportation_type": "2",
        "producing_federate": "3",
        "sent_regions": "700:5:15",
        "time": ("HLAinteger64Time", "10"),
        "sent_order_type": "2",
        "received_order_type": "2",
        "optional_retraction": "41",
    }
    assert decode_callback_request_details(interaction) == {
        "kind": "receiveInteractionWithTime",
        "interaction_class": "11",
        "parameter_values": "9:747261636b",
        "user_supplied_tag": "696e746572616374696f6e2d746167",
        "transportation_type": "2",
        "producing_federate": "3",
        "sent_regions": "700:5:15",
        "time": ("HLAinteger64Time", "12"),
        "sent_order_type": "2",
        "received_order_type": "2",
        "optional_retraction": "42",
    }
    assert decode_callback_request_details(directed) == {
        "kind": "receiveDirectedInteractionWithTime",
        "interaction_class": "11",
        "object_instance": "17",
        "parameter_values": "9:747261636b2d6469726563746564",
        "user_supplied_tag": "64697265637465642d746167",
        "transportation_type": "2",
        "producing_federate": "3",
        "time": ("HLAinteger64Time", "13"),
        "sent_order_type": "2",
        "received_order_type": "2",
        "optional_retraction": "43",
    }
    assert decode_callback_request_details(remove) == {
        "kind": "removeObjectInstanceWithTime",
        "object_instance": "17",
        "user_supplied_tag": "676f6e65",
        "producing_federate": "3",
        "time": ("HLAinteger64Time", "14"),
        "sent_order_type": "2",
        "received_order_type": "2",
        "optional_retraction": "44",
    }


@pytest.mark.requirements(
    "HLA2025-NEW-002",
    "HLA2025-NEW-003",
    "HLA2025-FI-SVC-003",
    "HLA2025-FI-SVC-012",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-017",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-068",
    "HLA2025-FI-SVC-069",
    "HLA2025-FI-SVC-072",
    "HLA2025-FI-SVC-073",
    "HLA2025-FI-SVC-075",
    "HLA2025-FI-SVC-078",
    "HLA2025-FI-SVC-080",
    "HLA2025-FI-SVC-082",
    "HLA2025-BND-003",
)
def test_2025_transport_server_decodes_extended_callback_routes_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        server.servicer.callback_queue.extend(
            [
                callback_pb2.CallbackRequest(connectionLost=callback_pb2.ConnectionLost(faultDescription="socket reset")),
                callback_pb2.CallbackRequest(
                    reportFederationExecutions=callback_pb2.ReportFederationExecutions(
                        report=datatypes_pb2.FederationExecutionInformationSet(
                            federationExecutionInformation=[
                                datatypes_pb2.FederationExecutionInformation(
                                    federationExecutionName="alpha",
                                    logicalTimeImplementationName="HLAinteger64Time",
                                ),
                                datatypes_pb2.FederationExecutionInformation(
                                    federationExecutionName="bravo",
                                    logicalTimeImplementationName="HLAfloat64Time",
                                ),
                            ]
                        )
                    )
                ),
                callback_pb2.CallbackRequest(
                    reportFederationExecutionMembers=callback_pb2.ReportFederationExecutionMembers(
                        federationName="alpha",
                        report=datatypes_pb2.FederationExecutionMemberInformationSet(
                            federationExecutionMemberInformation=[
                                datatypes_pb2.FederationExecutionMemberInformation(federateName="Red", federateType="TypeA"),
                                datatypes_pb2.FederationExecutionMemberInformation(federateName="Blue", federateType="TypeB"),
                            ]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    reportFederationExecutionDoesNotExist=callback_pb2.ReportFederationExecutionDoesNotExist(
                        federationName="missing-fed"
                    )
                ),
                callback_pb2.CallbackRequest(
                    federateResigned=callback_pb2.FederateResigned(reasonForResignDescription="publisher resigned")
                ),
                callback_pb2.CallbackRequest(
                    synchronizationPointRegistrationFailed=callback_pb2.SynchronizationPointRegistrationFailed(
                        synchronizationPointLabel="ReadyToRun",
                        reason=datatypes_pb2.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
                    )
                ),
                callback_pb2.CallbackRequest(
                    initiateFederateSaveWithTime=callback_pb2.InitiateFederateSaveWithTime(
                        label="SAVE-TIME-42",
                        time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:42"),
                    )
                ),
                callback_pb2.CallbackRequest(
                    objectInstanceNameReservationSucceeded=callback_pb2.ObjectInstanceNameReservationSucceeded(
                        objectInstanceName="Target-1"
                    )
                ),
                callback_pb2.CallbackRequest(
                    objectInstanceNameReservationFailed=callback_pb2.ObjectInstanceNameReservationFailed(
                        objectInstanceName="Target-2"
                    )
                ),
                callback_pb2.CallbackRequest(
                    multipleObjectInstanceNameReservationSucceeded=callback_pb2.MultipleObjectInstanceNameReservationSucceeded(
                        objectInstanceNames=["Target-3", "Target-4"]
                    )
                ),
                callback_pb2.CallbackRequest(
                    multipleObjectInstanceNameReservationFailed=callback_pb2.MultipleObjectInstanceNameReservationFailed(
                        objectInstanceNames=["Target-5", "Target-6"]
                    )
                ),
                callback_pb2.CallbackRequest(
                    removeObjectInstanceWithTime=callback_pb2.RemoveObjectInstanceWithTime(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        userSuppliedTag=b"gone",
                        producingFederate=datatypes_pb2.FederateHandle(data=b"3"),
                        time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:9"),
                        sentOrderType=datatypes_pb2.TIMESTAMP,
                        receivedOrderType=datatypes_pb2.RECEIVE,
                    )
                ),
                callback_pb2.CallbackRequest(
                    attributesInScope=callback_pb2.AttributesInScope(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[
                                datatypes_pb2.AttributeHandle(data=b"5"),
                                datatypes_pb2.AttributeHandle(data=b"8"),
                            ]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    attributesOutOfScope=callback_pb2.AttributesOutOfScope(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"8")]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    turnUpdatesOnForObjectInstance=callback_pb2.TurnUpdatesOnForObjectInstance(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"5")]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    turnUpdatesOnForObjectInstanceWithRate=callback_pb2.TurnUpdatesOnForObjectInstanceWithRate(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"5")]
                        ),
                        updateRateDesignator="fast",
                    )
                ),
                callback_pb2.CallbackRequest(
                    turnUpdatesOffForObjectInstance=callback_pb2.TurnUpdatesOffForObjectInstance(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"5")]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    confirmAttributeTransportationTypeChange=callback_pb2.ConfirmAttributeTransportationTypeChange(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"5")]
                        ),
                        transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
                    )
                ),
                callback_pb2.CallbackRequest(
                    reportAttributeTransportationType=callback_pb2.ReportAttributeTransportationType(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attribute=datatypes_pb2.AttributeHandle(data=b"5"),
                        transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
                    )
                ),
                callback_pb2.CallbackRequest(
                    confirmInteractionTransportationTypeChange=callback_pb2.ConfirmInteractionTransportationTypeChange(
                        interactionClass=datatypes_pb2.InteractionClassHandle(data=b"11"),
                        transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
                    )
                ),
                callback_pb2.CallbackRequest(
                    reportInteractionTransportationType=callback_pb2.ReportInteractionTransportationType(
                        federate=datatypes_pb2.FederateHandle(data=b"3"),
                        interactionClass=datatypes_pb2.InteractionClassHandle(data=b"11"),
                        transportationType=datatypes_pb2.TransportationTypeHandle(data=b"2"),
                    )
                ),
                callback_pb2.CallbackRequest(
                    attributeIsOwnedByRTI=callback_pb2.AttributeIsOwnedByRTI(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"17"),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=b"5")]
                        ),
                    )
                ),
                callback_pb2.CallbackRequest(
                    flushQueueGrant=callback_pb2.FlushQueueGrant(
                        time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:12"),
                        optimisticTime=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:14"),
                    )
                ),
            ]
        )

        expected_callbacks = [
            ("1", "CONNECTION_LOST", "socket reset"),
            ("1", "REPORT_FEDERATION_EXECUTIONS", "alpha:HLAinteger64Time;bravo:HLAfloat64Time"),
            ("1", "REPORT_FEDERATION_EXECUTION_MEMBERS", "alpha", "Red:TypeA;Blue:TypeB"),
            ("1", "REPORT_FEDERATION_EXECUTION_DOES_NOT_EXIST", "missing-fed"),
            ("1", "FEDERATE_RESIGNED", "publisher resigned"),
            ("1", "SYNC_POINT_REGISTRATION_FAILED", "ReadyToRun", "SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE"),
            ("1", "INITIATE_FEDERATE_SAVE", "SAVE-TIME-42", "HLAinteger64Time", "42"),
            ("1", "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED", "Target-1"),
            ("1", "OBJECT_INSTANCE_NAME_RESERVATION_FAILED", "Target-2"),
            ("1", "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED", "Target-3,Target-4"),
            ("1", "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_FAILED", "Target-5,Target-6"),
            ("1", "REMOVE_OBJECT_INSTANCE_TSO", "17", "676f6e65", "HLAinteger64Time", "9", "2", "1", "3"),
            ("1", "ATTRIBUTES_IN_SCOPE", "17", "5,8"),
            ("1", "ATTRIBUTES_OUT_OF_SCOPE", "17", "8"),
            ("1", "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE", "17", "5"),
            ("1", "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE", "17", "5", "fast"),
            ("1", "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE", "17", "5"),
            ("1", "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE", "17", "5", "2"),
            ("1", "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE", "17", "5", "2"),
            ("1", "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE", "11", "2"),
            ("1", "REPORT_INTERACTION_TRANSPORTATION_TYPE", "3", "11", "2"),
            ("1", "ATTRIBUTE_IS_OWNED_BY_RTI", "17", "5"),
            ("1", "FLUSH_QUEUE_GRANT", "HLAinteger64Time", "12", "HLAinteger64Time", "14"),
        ]
        for expected in expected_callbacks:
            assert transport.request(TransportRequest(command="EVOKE")).fields == expected
        assert server.servicer.callback_queue == []
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_reports_fom_module_data_for_mom_request_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-fom-module"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(
                command="CREATE",
                fields=(federation_name, "HLAinteger64Time", "MomFomCore2025.xml", "MomFomExtension2025.xml"),
            )
        ).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025FOMModule", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData",),
            )
        ).fields[0]
        request_federate_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        request_indicator_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAFOMmoduleIndicator"))
        ).fields[0]
        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData",),
            )
        ).fields[0]
        report_federate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        report_indicator_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAFOMmoduleIndicator"))
        ).fields[0]
        report_data_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAFOMmoduleData"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        assert transport.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    request_class,
                    f"{request_federate_param}:31,{request_indicator_param}:31",
                    "666f6d2d726571",
                ),
            )
        ).fields == ()

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        payloads = dict(item.split(":", 1) for item in report[3].split(","))
        assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[report_indicator_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[report_data_param]).decode("ascii") == "MomFomExtension2025.xml"
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "createFederationExecutionWithModulesAndTimeRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_reports_object_publications_for_mom_request_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-publications"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomPublications2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MomPub", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications",),
            )
        ).fields[0]
        request_federate_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication",),
            )
        ).fields[0]
        report_federate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        count_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAnumberOfClasses"))).fields[0]
        class_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectClass"))).fields[0]
        attributes_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAattributeList"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        assert transport.request(
            TransportRequest(command="SEND_INTERACTION", fields=(request_class, f"{request_federate_param}:31", "7075622d72657175657374"))
        ).fields == ()

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        payloads = dict(item.split(":", 1) for item in report[3].split(","))
        assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[count_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[class_param]).decode("ascii") == object_class
        assert bytes.fromhex(payloads[attributes_param]).decode("ascii") == f"{object_class}:{attribute}"
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassAttributesRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_reports_object_publications_for_requested_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-publications-per-federate"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomPublications2025.xml"))).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomPubLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomPubWing", "TestFederate", federation_name))
        ).fields[0]

        target_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        target_attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        route_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.RouteTarget",))).fields[0]
        route_attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(route_class, "Position"))).fields[0]
        assert leader.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, target_attribute))).fields == ()
        assert wing.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(route_class, route_attribute))).fields == ()

        request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications",),
            )
        ).fields[0]
        request_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication",),
            )
        ).fields[0]
        report_federate_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        count_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAnumberOfClasses"))).fields[0]
        class_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectClass"))).fields[0]
        attributes_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAattributeList"))).fields[0]
        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        def request_and_assert(requested_handle: str, expected_class: str, expected_attribute: str) -> None:
            assert leader.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(request_class, f"{request_federate_param}:{requested_handle.encode('ascii').hex()}", "7075622d72657175657374"),
                )
            ).fields == ()
            report = leader.request(TransportRequest(command="EVOKE")).fields
            assert report[:3] == ("1", "INTERACTION", report_class)
            payloads = dict(item.split(":", 1) for item in report[3].split(","))
            assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == requested_handle
            assert bytes.fromhex(payloads[count_param]).decode("ascii") == "1"
            assert bytes.fromhex(payloads[class_param]).decode("ascii") == expected_class
            assert bytes.fromhex(payloads[attributes_param]).decode("ascii") == f"{expected_class}:{expected_attribute}"

        request_and_assert(leader_handle, target_class, target_attribute)
        request_and_assert(wing_handle, route_class, route_attribute)

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


def test_2025_transport_server_reports_object_subscriptions_for_mom_request_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-subscriptions"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomSubscriptions2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MomSub", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions",),
            )
        ).fields[0]
        request_federate_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription",),
            )
        ).fields[0]
        report_federate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        count_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAnumberOfClasses"))).fields[0]
        class_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectClass"))).fields[0]
        active_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAactive"))).fields[0]
        max_rate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAmaxUpdateRate"))).fields[0]
        attributes_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAattributeList"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        assert transport.request(
            TransportRequest(command="SEND_INTERACTION", fields=(request_class, f"{request_federate_param}:31", "7375622d72657175657374"))
        ).fields == ()

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        payloads = dict(item.split(":", 1) for item in report[3].split(","))
        assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[count_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[class_param]).decode("ascii") == object_class
        assert bytes.fromhex(payloads[active_param]).decode("ascii") == "HLAtrue"
        assert bytes.fromhex(payloads[max_rate_param]).decode("ascii") == ""
        assert bytes.fromhex(payloads[attributes_param]).decode("ascii") == f"{object_class}:{attribute}"
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "subscribeObjectClassAttributesRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_reports_object_subscriptions_for_requested_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-subscriptions-per-federate"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomSubscriptions2025.xml"))).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSubLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSubWing", "TestFederate", federation_name))
        ).fields[0]

        target_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        target_attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(target_class, "Position"))).fields[0]
        route_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.RouteTarget",))).fields[0]
        route_attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(route_class, "Position"))).fields[0]
        assert leader.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(target_class, target_attribute))).fields == ()
        assert wing.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(route_class, route_attribute))).fields == ()

        request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions",),
            )
        ).fields[0]
        request_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription",),
            )
        ).fields[0]
        report_federate_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        count_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAnumberOfClasses"))).fields[0]
        class_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectClass"))).fields[0]
        active_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAactive"))).fields[0]
        attributes_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAattributeList"))).fields[0]
        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        def request_and_assert(requested_handle: str, expected_class: str, expected_attribute: str) -> None:
            assert leader.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(request_class, f"{request_federate_param}:{requested_handle.encode('ascii').hex()}", "7375622d72657175657374"),
                )
            ).fields == ()
            report = leader.request(TransportRequest(command="EVOKE")).fields
            assert report[:3] == ("1", "INTERACTION", report_class)
            payloads = dict(item.split(":", 1) for item in report[3].split(","))
            assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == requested_handle
            assert bytes.fromhex(payloads[count_param]).decode("ascii") == "1"
            assert bytes.fromhex(payloads[class_param]).decode("ascii") == expected_class
            assert bytes.fromhex(payloads[active_param]).decode("ascii") == "HLAtrue"
            assert bytes.fromhex(payloads[attributes_param]).decode("ascii") == f"{expected_class}:{expected_attribute}"

        request_and_assert(leader_handle, target_class, target_attribute)
        request_and_assert(wing_handle, route_class, route_attribute)

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


def test_2025_transport_server_reports_object_instance_information_for_mom_request_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-object-info"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomObjectInfo2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MomObjectInfo", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "MomInfoTarget"))).fields[0]

        request_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation",),
            )
        ).fields[0]
        request_federate_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
        ).fields[0]
        request_object_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAobjectInstance"))
        ).fields[0]
        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",),
            )
        ).fields[0]
        report_federate_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))).fields[0]
        report_object_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectInstance"))).fields[0]
        report_class_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectClass"))).fields[0]
        report_name_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAobjectInstanceName"))).fields[0]
        report_attributes_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAattributeList"))).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        assert transport.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    request_class,
                    f"{request_federate_param}:31,{request_object_param}:{object_instance.encode('ascii').hex()}",
                    "6f626a2d696e666f",
                ),
            )
        ).fields == ()

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        payloads = dict(item.split(":", 1) for item in report[3].split(","))
        assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == "1"
        assert bytes.fromhex(payloads[report_object_param]).decode("ascii") == object_instance
        assert bytes.fromhex(payloads[report_class_param]).decode("ascii") == object_class
        assert bytes.fromhex(payloads[report_name_param]).decode("ascii") == "MomInfoTarget"
        assert bytes.fromhex(payloads[report_attributes_param]).decode("ascii") == attribute
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "registerObjectInstanceWithNameRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_reports_requested_federate_identity_for_mom_object_info_and_fom_requests_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-federate-identity"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(
                command="CREATE",
                fields=(federation_name, "HLAinteger64Time", "MomBase2025.xml,MomFomExtension2025.xml"),
            )
        ).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomIdentityLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomIdentityWing", "TestFederate", federation_name))
        ).fields[0]

        object_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        object_instance = leader.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "MomIdentityTarget"))
        ).fields[0]

        object_request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation",),
            )
        ).fields[0]
        object_request_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(object_request_class, "HLAfederate"))
        ).fields[0]
        object_request_object_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(object_request_class, "HLAobjectInstance"))
        ).fields[0]
        object_report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",),
            )
        ).fields[0]
        object_report_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(object_report_class, "HLAfederate"))
        ).fields[0]
        object_report_object_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(object_report_class, "HLAobjectInstance"))
        ).fields[0]
        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(object_report_class,))).fields == ()

        assert leader.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    object_request_class,
                    f"{object_request_federate_param}:{wing_handle.encode('ascii').hex()},{object_request_object_param}:{object_instance.encode('ascii').hex()}",
                    "6f626a2d696e666f",
                ),
            )
        ).fields == ()
        object_report = leader.request(TransportRequest(command="EVOKE")).fields
        assert object_report[:3] == ("1", "INTERACTION", object_report_class)
        object_payloads = dict(item.split(":", 1) for item in object_report[3].split(","))
        assert bytes.fromhex(object_payloads[object_report_federate_param]).decode("ascii") == wing_handle
        assert bytes.fromhex(object_payloads[object_report_object_param]).decode("ascii") == object_instance

        fom_request_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData",),
            )
        ).fields[0]
        fom_request_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(fom_request_class, "HLAfederate"))
        ).fields[0]
        fom_request_indicator_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(fom_request_class, "HLAFOMmoduleIndicator"))
        ).fields[0]
        fom_report_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData",),
            )
        ).fields[0]
        fom_report_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(fom_report_class, "HLAfederate"))
        ).fields[0]
        fom_report_indicator_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(fom_report_class, "HLAFOMmoduleIndicator"))
        ).fields[0]
        assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(fom_report_class,))).fields == ()

        assert leader.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    fom_request_class,
                    f"{fom_request_federate_param}:{wing_handle.encode('ascii').hex()},{fom_request_indicator_param}:31",
                    "666f6d2d726571",
                ),
            )
        ).fields == ()
        fom_report = leader.request(TransportRequest(command="EVOKE")).fields
        assert fom_report[:3] == ("1", "INTERACTION", fom_report_class)
        fom_payloads = dict(item.split(":", 1) for item in fom_report[3].split(","))
        assert bytes.fromhex(fom_payloads[fom_report_federate_param]).decode("ascii") == wing_handle
        assert bytes.fromhex(fom_payloads[fom_report_indicator_param]).decode("ascii") == "1"

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-NEW-007")
def test_2025_transport_server_preserves_other_federate_interaction_publication_after_mom_unpublish_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    observer = None
    federation_name = "fedpro-2025-mom-interaction-publication"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (leader, wing, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomPubLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomPubWing", "TestFederate", federation_name))
        ).fields[0]
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomPubObserver", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        interaction_class = leader.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert leader.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert wing.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        unpublish_class = leader.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunpublishInteractionClass",),
            )
        ).fields[0]
        unpublish_federate_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unpublish_class, "HLAfederate"))
        ).fields[0]
        unpublish_interaction_param = leader.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unpublish_class, "HLAinteractionClass"))
        ).fields[0]
        assert leader.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    unpublish_class,
                    f"{unpublish_federate_param}:{leader_handle.encode('ascii').hex()},{unpublish_interaction_param}:{interaction_class.encode('ascii').hex()}",
                    "6d6f6d2d756e707562",
                ),
            )
        ).fields == ()

        assert wing.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:77696e672d7374696c6c2d707562", "77696e672d746167"),
            )
        ).fields == ()
        report = observer.request(TransportRequest(command="EVOKE")).fields
        assert report[:5] == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:77696e672d7374696c6c2d707562",
            "77696e672d746167",
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements("HLA2025-BND-003")
def test_2025_transport_server_preserves_other_federate_directed_publication_after_unpublish_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    observer = None
    federation_name = "fedpro-2025-directed-publication-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (leader, wing, observer):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "DirectedPub2025.xml"))).fields == ()
        assert leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedLeader", "TestFederate", federation_name))
        ).fields == ("1", "HLAinteger64Time")
        assert wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedWing", "TestFederate", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025DirectedObserver", "TestFederate", federation_name))
        ).fields == ("3", "HLAinteger64Time")

        object_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = leader.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]

        assert leader.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert wing.request(
            TransportRequest(command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()
        assert observer.request(
            TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class, interaction_class))
        ).fields == ()

        object_instance = leader.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "DirectedIsolationTarget"))
        ).fields[0]

        assert leader.request(
            TransportRequest(command="UNPUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(object_class,))
        ).fields == ()

        assert wing.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION",
                fields=(interaction_class, object_instance, f"{parameter}:77696e672d6469726563746564", "77696e672d746167"),
            )
        ).fields == ()
        report = observer.request(TransportRequest(command="EVOKE")).fields
        assert report[:6] == (
            "1",
            "DIRECTED_INTERACTION",
            interaction_class,
            object_instance,
            f"{parameter}:77696e672d6469726563746564",
            "77696e672d746167",
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        if observer is not None:
            observer.close()
        server.close()


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-NEW-007")
def test_2025_transport_server_preserves_other_federate_interaction_subscription_after_mom_unsubscribe_over_fedpro_schema():
    server = start_2025_grpc_server()
    sender = None
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-interaction-subscription"
    try:
        sender = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (sender, leader, wing):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert sender.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))).fields == ()
        assert sender.request(TransportRequest(command="JOIN", fields=("FedPro2025MomSubSender", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSubLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSubWing", "TestFederate", federation_name))
        ).fields[0]

        interaction_class = sender.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        parameter = sender.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert sender.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()

        subscribe_class = sender.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeInteractionClass",),
            )
        ).fields[0]
        subscribe_federate_param = sender.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(subscribe_class, "HLAfederate"))
        ).fields[0]
        subscribe_interaction_param = sender.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(subscribe_class, "HLAinteractionClass"))
        ).fields[0]
        unsubscribe_class = sender.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunsubscribeInteractionClass",),
            )
        ).fields[0]
        unsubscribe_federate_param = sender.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unsubscribe_class, "HLAfederate"))
        ).fields[0]
        unsubscribe_interaction_param = sender.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unsubscribe_class, "HLAinteractionClass"))
        ).fields[0]

        for handle in (leader_handle, wing_handle):
            assert sender.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(
                        subscribe_class,
                        f"{subscribe_federate_param}:{handle.encode('ascii').hex()},{subscribe_interaction_param}:{interaction_class.encode('ascii').hex()}",
                        "6d6f6d2d737562",
                    ),
                )
            ).fields == ()

        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:66697273742d626f7468", "66697273742d746167"),
            )
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields[:5] == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:66697273742d626f7468",
            "66697273742d746167",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields[:5] == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:66697273742d626f7468",
            "66697273742d746167",
        )

        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    unsubscribe_class,
                    f"{unsubscribe_federate_param}:{leader_handle.encode('ascii').hex()},{unsubscribe_interaction_param}:{interaction_class.encode('ascii').hex()}",
                    "6d6f6d2d756e737562",
                ),
            )
        ).fields == ()

        assert sender.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(interaction_class, f"{parameter}:7365636f6e642d77696e67", "7365636f6e642d746167"),
            )
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "INTERACTION")
        assert wing.request(TransportRequest(command="EVOKE")).fields[:5] == (
            "1",
            "INTERACTION",
            interaction_class,
            f"{parameter}:7365636f6e642d77696e67",
            "7365636f6e642d746167",
        )

        assert sender.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert sender.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if sender is not None:
            sender.close()
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-NEW-007")
def test_2025_transport_server_preserves_other_federate_object_subscription_after_mom_unsubscribe_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-object-subscription"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for transport in (owner, leader, wing):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))).fields == ()
        assert owner.request(TransportRequest(command="JOIN", fields=("FedPro2025MomObjOwner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomObjLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomObjWing", "TestFederate", federation_name))
        ).fields[0]

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "MomObjSubTarget"))
        ).fields[0]

        subscribe_class = owner.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeObjectClassAttributes",),
            )
        ).fields[0]
        subscribe_federate_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(subscribe_class, "HLAfederate"))
        ).fields[0]
        subscribe_object_class_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(subscribe_class, "HLAobjectClass"))
        ).fields[0]
        subscribe_attribute_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(subscribe_class, "HLAattributeList"))
        ).fields[0]
        unsubscribe_class = owner.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunsubscribeObjectClassAttributes",),
            )
        ).fields[0]
        unsubscribe_federate_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unsubscribe_class, "HLAfederate"))
        ).fields[0]
        unsubscribe_object_class_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unsubscribe_class, "HLAobjectClass"))
        ).fields[0]
        unsubscribe_attribute_param = owner.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(unsubscribe_class, "HLAattributeList"))
        ).fields[0]

        for handle in (leader_handle, wing_handle):
            assert owner.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(
                        subscribe_class,
                        ",".join(
                            (
                                f"{subscribe_federate_param}:{handle.encode('ascii').hex()}",
                                f"{subscribe_object_class_param}:{object_class.encode('ascii').hex()}",
                                f"{subscribe_attribute_param}:{attribute.encode('ascii').hex()}",
                            )
                        ),
                        "6d6f6d2d737562",
                    ),
                )
            ).fields == ()

        assert owner.request(
            TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(object_instance, f"{attribute}:66697273742d626f7468", "66697273742d746167"))
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:66697273742d626f7468",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:66697273742d626f7468",
        )

        assert owner.request(
            TransportRequest(
                command="SEND_INTERACTION",
                fields=(
                    unsubscribe_class,
                    ",".join(
                        (
                            f"{unsubscribe_federate_param}:{leader_handle.encode('ascii').hex()}",
                            f"{unsubscribe_object_class_param}:{object_class.encode('ascii').hex()}",
                            f"{unsubscribe_attribute_param}:{attribute.encode('ascii').hex()}",
                        )
                    ),
                    "6d6f6d2d756e737562",
                ),
            )
        ).fields == ()

        assert owner.request(
            TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(object_instance, f"{attribute}:7365636f6e642d77696e67", "7365636f6e642d746167"))
        ).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REFLECT")
        assert wing.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REFLECT",
            object_instance,
            f"{attribute}:7365636f6e642d77696e67",
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if owner is not None:
            owner.close()
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


def test_2025_transport_server_reports_activity_counts_for_mom_requests_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-activity"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomActivity2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025MomActivity", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert transport.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "MomActivityTarget"))).fields[0]
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert transport.request(
            TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(object_instance, f"{attribute}:313233", "7570646174652d746167"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "REFLECT", object_instance)

        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert transport.request(
            TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:747261636b2d31", "696e746572616374696f6e2d746167"))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "INTERACTION", interaction_class)

        for request_name, report_name, count_name, expected in (
            ("HLArequestObjectInstancesThatCanBeDeleted", "HLAreportObjectInstancesThatCanBeDeleted", "HLAobjectInstanceCounts", "1"),
            ("HLArequestObjectInstancesUpdated", "HLAreportObjectInstancesUpdated", "HLAobjectInstanceCounts", "1"),
            ("HLArequestObjectInstancesReflected", "HLAreportObjectInstancesReflected", "HLAobjectInstanceCounts", "1"),
            ("HLArequestUpdatesSent", "HLAreportUpdatesSent", "HLAupdatesSent", "1"),
            ("HLArequestReflectionsReceived", "HLAreportReflectionsReceived", "HLAreflectionsReceived", "1"),
            ("HLArequestInteractionsSent", "HLAreportInteractionsSent", "HLAinteractionsSent", "1"),
            ("HLArequestInteractionsReceived", "HLAreportInteractionsReceived", "HLAinteractionsReceived", "1"),
        ):
            request_class = transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{request_name}",),
                )
            ).fields[0]
            request_federate_param = transport.request(
                TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
            ).fields[0]
            report_class = transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.{report_name}",),
                )
            ).fields[0]
            report_federate_param = transport.request(
                TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))
            ).fields[0]
            count_param = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, count_name))).fields[0]
            assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()
            assert transport.request(
                TransportRequest(command="SEND_INTERACTION", fields=(request_class, f"{request_federate_param}:31", "6d6f6d2d636f756e74"))
            ).fields == ()
            report = transport.request(TransportRequest(command="EVOKE")).fields
            assert report[:3] == ("1", "INTERACTION", report_class)
            payloads = dict(item.split(":", 1) for item in report[3].split(","))
            assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == "1"
            assert bytes.fromhex(payloads[count_param]).decode("ascii") == expected
            assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishInteractionClassRequest",
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-BND-003")
def test_2025_transport_server_reports_per_federate_activity_counts_for_mom_requests_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-activity-per-federate"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomActivity2025.xml"))).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomWing", "TestFederate", federation_name))
        ).fields[0]

        object_class = leader.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = leader.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert leader.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert wing.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        object_instance = leader.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "MomActivityPerFederate"))).fields[0]
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert leader.request(
            TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(object_instance, f"{attribute}:313233", "7570646174652d746167"))
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "REFLECT", object_instance)

        interaction_class = leader.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        parameter = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert leader.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert wing.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(interaction_class,))).fields == ()
        assert leader.request(
            TransportRequest(command="SEND_INTERACTION", fields=(interaction_class, f"{parameter}:747261636b2d31", "696e746572616374696f6e2d746167"))
        ).fields == ()
        assert wing.request(TransportRequest(command="EVOKE")).fields[:3] == ("1", "INTERACTION", interaction_class)

        def assert_report(request_name: str, report_name: str, count_name: str, requested_handle: str, expected_count: str) -> None:
            request_class = leader.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{request_name}",),
                )
            ).fields[0]
            request_federate_param = leader.request(
                TransportRequest(command="GET_PARAMETER_HANDLE", fields=(request_class, "HLAfederate"))
            ).fields[0]
            report_class = leader.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.{report_name}",),
                )
            ).fields[0]
            report_federate_param = leader.request(
                TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAfederate"))
            ).fields[0]
            count_param = leader.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, count_name))).fields[0]
            assert leader.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()
            assert leader.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(request_class, f"{request_federate_param}:{requested_handle.encode('ascii').hex()}", "6d6f6d2d636f756e74"),
                )
            ).fields == ()
            report = leader.request(TransportRequest(command="EVOKE")).fields
            assert report[:3] == ("1", "INTERACTION", report_class)
            payloads = dict(item.split(":", 1) for item in report[3].split(","))
            assert bytes.fromhex(payloads[report_federate_param]).decode("ascii") == requested_handle
            assert bytes.fromhex(payloads[count_param]).decode("ascii") == expected_count

        assert_report("HLArequestUpdatesSent", "HLAreportUpdatesSent", "HLAupdatesSent", leader_handle, "1")
        assert_report("HLArequestUpdatesSent", "HLAreportUpdatesSent", "HLAupdatesSent", wing_handle, "0")
        assert_report(
            "HLArequestReflectionsReceived",
            "HLAreportReflectionsReceived",
            "HLAreflectionsReceived",
            wing_handle,
            "1",
        )
        assert_report("HLArequestInteractionsSent", "HLAreportInteractionsSent", "HLAinteractionsSent", leader_handle, "1")
        assert_report(
            "HLArequestInteractionsReceived",
            "HLAreportInteractionsReceived",
            "HLAinteractionsReceived",
            wing_handle,
            "1",
        )
        assert_report(
            "HLArequestObjectInstancesUpdated",
            "HLAreportObjectInstancesUpdated",
            "HLAobjectInstanceCounts",
            leader_handle,
            "1",
        )
        assert_report(
            "HLArequestObjectInstancesReflected",
            "HLAreportObjectInstancesReflected",
            "HLAobjectInstanceCounts",
            wing_handle,
            "1",
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


def test_2025_transport_server_routes_mom_manager_service_actions_over_fedpro_schema():
    from hla.transports.grpc.python_server_2025 import (
        _MOM_FEDERATE_ADJUST_LEAVES,
        _MOM_FEDERATE_SERVICE_LEAVES,
        _MOM_FEDERATION_ADJUST_LEAVES,
    )

    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-services"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert (
                transport.request(
                    TransportRequest(
                        command="SEND_INTERACTION",
                        fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                    )
                ).fields
                == ()
            )

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        federate_handle = transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMServices", "TestFederate", federation_name))
        ).fields[0]

        object_class = transport.request(
            TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))
        ).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        interaction_class = transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))
        ).fields[0]
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProMomServiceTarget"))
        ).fields[0]

        default_params = {
            "HLAfederate": federate_handle,
            "HLAobjectClass": object_class,
            "HLAattributeList": attribute,
            "HLAinteractionClass": interaction_class,
            "HLAobjectInstance": object_instance,
            "HLAtransportation": "HLAbestEffort",
            "HLAsendOrder": "1",
            "HLAtimeStamp": "8",
            "HLAlookahead": "3",
            "HLAlabel": "MOM-SYNC",
            "HLAsuccessIndicator": "HLAtrue",
            "HLAtag": "mom-delete",
            "HLAresignAction": "NO_ACTION",
        }

        for leaf in _MOM_FEDERATE_ADJUST_LEAVES:
            interaction = mom_class("HLAfederate", "HLAadjust", leaf)
            params = {"HLAfederate": federate_handle}
            if leaf in {"HLAsetServiceReporting", "HLAsetExceptionReporting"}:
                params["HLAreportingState"] = "HLAtrue"
            elif leaf == "HLAsetSwitches":
                params["HLAconveyRegionDesignatorSets"] = "HLAtrue"
            elif leaf == "HLAsetTiming":
                params["HLAreportPeriod"] = "2.5"
            elif leaf == "HLAmodifyAttributeState":
                params.update(
                    {
                        "HLAobjectInstance": object_instance,
                        "HLAattribute": attribute,
                        "HLAattributeState": "HLAunowned",
                    }
                )
            send_mom(interaction, params)

        for leaf in _MOM_FEDERATION_ADJUST_LEAVES:
            send_mom(mom_class("HLAfederation", "HLAadjust", leaf), {"HLAautoProvide": "HLAtrue"})

        assert server.servicer.service_reporting is True
        assert server.servicer.switch_states["exceptionReporting"] is True
        assert server.servicer.switch_states["conveyRegionDesignatorSets"] is True
        assert server.servicer.switch_states["autoProvide"] is True
        assert server.servicer.mom_report_period == "2.5"
        assert (object_instance, attribute) in server.servicer.unowned_attributes

        for leaf in _MOM_FEDERATE_SERVICE_LEAVES:
            if leaf == "HLAresignFederationExecution":
                continue
            send_mom(mom_class("HLAfederate", "HLAservice", leaf), default_params)

        assert attribute not in server.servicer.published_object_attributes.get(object_class, set())
        assert interaction_class not in server.servicer.published_interactions
        assert server.servicer.time_regulating is False
        assert server.servicer.time_constrained is False
        assert server.servicer.asynchronous_delivery_enabled is False
        assert server.servicer.current_time.data == b"HLAinteger64Time:8"
        assert server.servicer.lookahead.data == b"HLAinteger64Interval:3"
        assert server.servicer.interaction_transportation == (interaction_class, "HLAbestEffort")
        assert server.servicer.interaction_order == (interaction_class, datatypes_pb2.TIMESTAMP)
        assert server.servicer.default_attribute_transportation[(object_instance, attribute)] == "HLAbestEffort"
        assert server.servicer.default_attribute_order[(object_instance, attribute)] == datatypes_pb2.TIMESTAMP

        callback_kinds = [transport.request(TransportRequest(command="EVOKE")).fields[1] for _ in range(8)]
        assert "TIME_REGULATION_ENABLED" in callback_kinds
        assert "TIME_CONSTRAINED_ENABLED" in callback_kinds
        assert "TIME_ADVANCE_GRANT" in callback_kinds
        assert "FLUSH_QUEUE_GRANT" in callback_kinds
        assert "REMOVE_OBJECT_INSTANCE" not in callback_kinds

        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("MOM-SAVE",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "MOM-SAVE")
        send_mom(mom_class("HLAfederate", "HLAservice", "HLAfederateSaveBegun"), {"HLAfederate": federate_handle})
        send_mom(
            mom_class("HLAfederate", "HLAservice", "HLAfederateSaveComplete"),
            {"HLAfederate": federate_handle, "HLAsuccessIndicator": "HLAtrue"},
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")
        assert transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("MOM-SAVE",))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_FEDERATION_RESTORE_SUCCEEDED",
            "MOM-SAVE",
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert transport.request(TransportRequest(command="EVOKE")).fields[:3] == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "MOM-SAVE",
        )
        send_mom(
            mom_class("HLAfederate", "HLAservice", "HLAfederateRestoreComplete"),
            {"HLAfederate": federate_handle, "HLAsuccessIndicator": "HLAtrue"},
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        send_mom(mom_class("HLAfederate", "HLAservice", "HLAresignFederationExecution"), default_params)
        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert (set(_MOM_FEDERATE_ADJUST_LEAVES) | set(_MOM_FEDERATION_ADJUST_LEAVES) | set(_MOM_FEDERATE_SERVICE_LEAVES)) <= routed

        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-110",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-time-callback-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(transport: GrpcTransport, scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(transport: GrpcTransport, interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                )
            ).fields == ()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomWing", "Observer", federation_name))
        ).fields[0]
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        enable_reg = mom_class(leader, "HLAfederate", "HLAservice", "HLAenableTimeRegulation")
        send_mom(leader, enable_reg, {"HLAfederate": leader_handle, "HLAlookahead": "2"})
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "TIME_REGULATION_ENABLED")
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_REGULATION_ENABLED",
            "HLAinteger64Time",
            "0",
        )

        enable_con = mom_class(wing, "HLAfederate", "HLAservice", "HLAenableTimeConstrained")
        send_mom(wing, enable_con, {"HLAfederate": wing_handle})
        assert leader.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "TIME_CONSTRAINED_ENABLED")
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "TIME_CONSTRAINED_ENABLED",
            "HLAinteger64Time",
            "0",
        )

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert {"HLAenableTimeRegulation", "HLAenableTimeConstrained"} <= routed
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_mom_save_restore_completion_callbacks_only_to_reporting_federate_over_fedpro_schema():
    server = start_2025_grpc_server()
    leader = None
    wing = None
    federation_name = "fedpro-2025-mom-save-restore-callback-isolation"
    try:
        leader = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        wing = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(transport: GrpcTransport, scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(transport: GrpcTransport, interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                )
            ).fields == ()

        assert leader.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert wing.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert leader.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        leader_handle = leader.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSaveLeader", "TestFederate", federation_name))
        ).fields[0]
        wing_handle = wing.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomSaveWing", "Observer", federation_name))
        ).fields[0]
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=("MOM-SAVE",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "MOM-SAVE")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "INITIATE_FEDERATE_SAVE", "MOM-SAVE")

        save_begun = mom_class(leader, "HLAfederate", "HLAservice", "HLAfederateSaveBegun")
        save_complete = mom_class(leader, "HLAfederate", "HLAservice", "HLAfederateSaveComplete")
        send_mom(leader, save_begun, {"HLAfederate": leader_handle})
        send_mom(leader, save_complete, {"HLAfederate": leader_handle, "HLAsuccessIndicator": "HLAtrue"})
        assert wing.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_SAVED")
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_SAVED")

        assert leader.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=("MOM-SAVE",))).fields == ()
        assert leader.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_FEDERATION_RESTORE_SUCCEEDED",
            "MOM-SAVE",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_FEDERATION_RESTORE_SUCCEEDED",
            "MOM-SAVE",
        )
        assert leader.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORE_BEGUN")
        assert leader.request(TransportRequest(command="EVOKE")).fields[:3] == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "MOM-SAVE",
        )
        assert wing.request(TransportRequest(command="EVOKE")).fields[:3] == (
            "1",
            "INITIATE_FEDERATE_RESTORE",
            "MOM-SAVE",
        )

        restore_complete = mom_class(wing, "HLAfederate", "HLAservice", "HLAfederateRestoreComplete")
        send_mom(wing, restore_complete, {"HLAfederate": wing_handle, "HLAsuccessIndicator": "HLAtrue"})
        assert leader.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "FEDERATION_RESTORED")
        assert wing.request(TransportRequest(command="EVOKE")).fields == ("1", "FEDERATION_RESTORED")

        assert leader.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert wing.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert leader.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert wing.request(TransportRequest(command="DISCONNECT")).fields == ()

        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert {"HLAfederateSaveBegun", "HLAfederateSaveComplete", "HLAfederateRestoreComplete"} <= routed
    finally:
        if leader is not None:
            leader.close()
        if wing is not None:
            wing.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-061",
    "HLA2025-FI-SVC-062",
    "HLA2025-BND-003",
)
def test_2025_transport_server_routes_mom_delete_remove_only_to_discovered_observers_over_fedpro_schema():
    server = start_2025_grpc_server()
    owner = None
    observer = None
    bystander = None
    federation_name = "fedpro-2025-mom-delete-isolation"
    try:
        owner = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        observer = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        bystander = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        def encode(value: str) -> str:
            return value.encode("ascii").hex()

        def mom_class(transport: GrpcTransport, scope: str, group: str, leaf: str) -> str:
            return transport.request(
                TransportRequest(
                    command="GET_INTERACTION_CLASS_HANDLE",
                    fields=(f"HLAinteractionRoot.HLAmanager.{scope}.{group}.{leaf}",),
                )
            ).fields[0]

        def send_mom(transport: GrpcTransport, interaction_class: str, params: dict[str, str]) -> None:
            encoded_params = []
            for name, value in params.items():
                parameter = transport.request(
                    TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, name))
                ).fields[0]
                encoded_params.append(f"{parameter}:{encode(value)}")
            assert transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(interaction_class, ",".join(encoded_params), "4d4f4d"),
                )
            ).fields == ()

        for transport in (owner, observer, bystander):
            assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert owner.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomServices2025.xml"))
        ).fields == ()
        owner_handle = owner.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomDeleteOwner", "TestFederate", federation_name))
        ).fields[0]
        assert observer.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomDeleteObserver", "Observer", federation_name))
        ).fields == ("2", "HLAinteger64Time")
        assert bystander.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MomDeleteBystander", "Observer", federation_name))
        ).fields == ("3", "HLAinteger64Time")
        for transport in (owner, observer, bystander):
            assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        object_class = owner.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = owner.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert owner.request(TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()
        assert observer.request(TransportRequest(command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(object_class, attribute))).fields == ()

        object_instance = owner.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProMomDeleteTarget-1"))
        ).fields[0]
        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DISCOVER")
        assert observer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "DISCOVER",
            object_instance,
            object_class,
            "FedProMomDeleteTarget-1",
        )
        assert bystander.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "DISCOVER")

        delete_service = mom_class(owner, "HLAfederate", "HLAservice", "HLAdeleteObjectInstance")
        send_mom(
            owner,
            delete_service,
            {"HLAfederate": owner_handle, "HLAobjectInstance": object_instance, "HLAtag": "mom-delete-object"},
        )

        assert owner.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REMOVE_OBJECT_INSTANCE")
        assert bystander.request(TransportRequest(command="EVOKE")).fields[:2] != ("1", "REMOVE_OBJECT_INSTANCE")
        assert observer.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REMOVE_OBJECT_INSTANCE",
            object_instance,
            "6d6f6d2d64656c6574652d6f626a656374",
            owner_handle,
        )

        assert owner.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert observer.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert bystander.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert bystander.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert owner.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert observer.request(TransportRequest(command="DISCONNECT")).fields == ()
        assert bystander.request(TransportRequest(command="DISCONNECT")).fields == ()

        routed = {call.removeprefix("mom:") for call in server.servicer.calls if call.startswith("mom:")}
        assert {"HLAdeleteObjectInstance"} <= routed
    finally:
        if owner is not None:
            owner.close()
        if observer is not None:
            observer.close()
        if bystander is not None:
            bystander.close()
        server.close()


def test_2025_transport_server_reports_failed_mom_service_actions_as_mom_exception_interactions():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-mom-exception"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(
            TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "MomException2025.xml"))
        ).fields == ()
        federate_handle = transport.request(
            TransportRequest(command="JOIN", fields=("FedPro2025MOMException", "TestFederate", federation_name))
        ).fields[0]

        service_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance",),
            )
        ).fields[0]
        service_federate_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(service_class, "HLAfederate"))
        ).fields[0]

        report_class = transport.request(
            TransportRequest(
                command="GET_INTERACTION_CLASS_HANDLE",
                fields=("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception",),
            )
        ).fields[0]
        report_service_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAservice"))
        ).fields[0]
        report_exception_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAexception"))
        ).fields[0]
        report_parameter_error_param = transport.request(
            TransportRequest(command="GET_PARAMETER_HANDLE", fields=(report_class, "HLAparameterError"))
        ).fields[0]
        assert transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(report_class,))).fields == ()

        with pytest.raises(TransportError) as error:
            transport.request(
                TransportRequest(
                    command="SEND_INTERACTION",
                    fields=(service_class, f"{service_federate_param}:{federate_handle.encode('ascii').hex()}", "6d6f6d2d6661696c"),
                )
            )
        assert error.value.code == "RTIinternalError"
        assert "Missing MOM parameter HLAobjectInstance" in error.value.message

        report = transport.request(TransportRequest(command="EVOKE")).fields
        assert report[:3] == ("1", "INTERACTION", report_class)
        payloads = dict(item.split(":", 1) for item in report[3].split(","))
        assert bytes.fromhex(payloads[report_service_param]).decode("ascii") == (
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance"
        )
        assert "Missing MOM parameter HLAobjectInstance" in bytes.fromhex(payloads[report_exception_param]).decode("utf-8")
        assert bytes.fromhex(payloads[report_parameter_error_param]).decode("ascii") == "HLAfalse"
        assert report[4:] == ("4d4f4d", "1", "1")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "subscribeInteractionClassRequest",
            "sendInteractionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-170",
    "HLA2025-FI-SVC-171",
    "HLA2025-FI-SVC-172",
    "HLA2025-FI-SVC-173",
    "HLA2025-FI-SVC-174",
    "HLA2025-FI-SVC-175",
    "HLA2025-FI-SVC-176",
    "HLA2025-FI-SVC-177",
    "HLA2025-FI-SVC-178",
    "HLA2025-FI-SVC-179",
    "HLA2025-FI-SVC-180",
    "HLA2025-FI-SVC-181",
    "HLA2025-FI-SVC-182",
    "HLA2025-FI-SVC-183",
    "HLA2025-FI-SVC-184",
    "HLA2025-FI-SVC-185",
    "HLA2025-FI-SVC-186",
    "HLA2025-FI-SVC-187",
    "HLA2025-FI-SVC-188",
    "HLA2025-FI-SVC-189",
    "HLA2025-FI-SVC-190",
    "HLA2025-FI-SVC-191",
    "HLA2025-FI-SVC-192",
    "HLA2025-BND-003",
)
def test_2025_transport_server_round_trips_2025_switch_services_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        for get_command, set_command in (
            ("GET_EXCEPTION_REPORTING_SWITCH", "SET_EXCEPTION_REPORTING_SWITCH"),
            ("GET_OBJECT_CLASS_RELEVANCE_ADVISORY_SWITCH", "SET_OBJECT_CLASS_RELEVANCE_ADVISORY_SWITCH"),
            ("GET_ATTRIBUTE_RELEVANCE_ADVISORY_SWITCH", "SET_ATTRIBUTE_RELEVANCE_ADVISORY_SWITCH"),
            ("GET_ATTRIBUTE_SCOPE_ADVISORY_SWITCH", "SET_ATTRIBUTE_SCOPE_ADVISORY_SWITCH"),
            ("GET_INTERACTION_RELEVANCE_ADVISORY_SWITCH", "SET_INTERACTION_RELEVANCE_ADVISORY_SWITCH"),
            ("GET_CONVEY_REGION_DESIGNATOR_SETS_SWITCH", "SET_CONVEY_REGION_DESIGNATOR_SETS_SWITCH"),
            ("GET_SEND_SERVICE_REPORTS_TO_FILE_SWITCH", "SET_SEND_SERVICE_REPORTS_TO_FILE_SWITCH"),
        ):
            assert transport.request(TransportRequest(command=get_command)).fields == ("0",)
            assert transport.request(TransportRequest(command=set_command, fields=("1",))).fields == ()
            assert transport.request(TransportRequest(command=get_command)).fields == ("1",)
            assert transport.request(TransportRequest(command=set_command, fields=("0",))).fields == ()
            assert transport.request(TransportRequest(command=get_command)).fields == ("0",)

        for get_command, expected in (
            ("GET_AUTO_PROVIDE_SWITCH", "0"),
            ("GET_DELAY_SUBSCRIPTION_EVALUATION_SWITCH", "0"),
            ("GET_ADVISORIES_USE_KNOWN_CLASS_SWITCH", "0"),
            ("GET_ALLOW_RELAXED_DDM_SWITCH", "0"),
            ("GET_NON_REGULATED_GRANT_SWITCH", "0"),
        ):
            assert transport.request(TransportRequest(command=get_command)).fields == (expected,)

        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("NO_ACTION",)
        assert transport.request(TransportRequest(command="SET_AUTOMATIC_RESIGN_DIRECTIVE", fields=("DELETE_OBJECTS",))).fields == ()
        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("DELETE_OBJECTS",)
        assert transport.request(TransportRequest(command="SET_AUTOMATIC_RESIGN_DIRECTIVE", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields == ("NO_ACTION",)

        assert {
            "getExceptionReportingSwitchRequest",
            "setExceptionReportingSwitchRequest",
            "getObjectClassRelevanceAdvisorySwitchRequest",
            "setObjectClassRelevanceAdvisorySwitchRequest",
            "getAttributeRelevanceAdvisorySwitchRequest",
            "setAttributeRelevanceAdvisorySwitchRequest",
            "getAttributeScopeAdvisorySwitchRequest",
            "setAttributeScopeAdvisorySwitchRequest",
            "getInteractionRelevanceAdvisorySwitchRequest",
            "setInteractionRelevanceAdvisorySwitchRequest",
            "getConveyRegionDesignatorSetsSwitchRequest",
            "setConveyRegionDesignatorSetsSwitchRequest",
            "getSendServiceReportsToFileSwitchRequest",
            "setSendServiceReportsToFileSwitchRequest",
            "getAutoProvideSwitchRequest",
            "getDelaySubscriptionEvaluationSwitchRequest",
            "getAdvisoriesUseKnownClassSwitchRequest",
            "getAllowRelaxedDDMSwitchRequest",
            "getNonRegulatedGrantSwitchRequest",
            "getAutomaticResignDirectiveRequest",
            "setAutomaticResignDirectiveRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-NEW-005",
    "HLA2025-FI-SVC-074",
    "HLA2025-FI-SVC-075",
    "HLA2025-FI-SVC-077",
    "HLA2025-FI-SVC-078",
    "HLA2025-FI-SVC-079",
    "HLA2025-FI-SVC-080",
    "HLA2025-FI-SVC-081",
    "HLA2025-FI-SVC-082",
    "HLA2025-FI-SVC-138",
    "HLA2025-FI-SVC-139",
    "HLA2025-FI-SVC-140",
    "HLA2025-FI-SVC-141",
    "HLA2025-FI-SVC-142",
    "HLA2025-FI-SVC-143",
    "HLA2025-FI-SVC-144",
    "HLA2025-FI-SVC-145",
    "HLA2025-FI-SVC-146",
    "HLA2025-FI-SVC-147",
    "HLA2025-FI-SVC-148",
    "HLA2025-FI-SVC-149",
    "HLA2025-FI-SVC-150",
    "HLA2025-FI-SVC-151",
    "HLA2025-FI-SVC-152",
    "HLA2025-FI-SVC-153",
    "HLA2025-FI-SVC-154",
    "HLA2025-FI-SVC-155",
    "HLA2025-FI-SVC-156",
    "HLA2025-FI-SVC-158",
    "HLA2025-FI-SVC-159",
    "HLA2025-FI-SVC-160",
    "HLA2025-FI-SVC-161",
    "HLA2025-FI-SVC-165",
    "HLA2025-FI-SVC-166",
    "HLA2025-FI-SVC-167",
    "HLA2025-FI-SVC-168",
    "HLA2025-FI-SVC-169",
    "HLA2025-BND-003",
)
def test_2025_transport_server_round_trips_support_services_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-support"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Support2025.xml"))).fields == ()
        join_fields = transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Support", "TestFederate", federation_name))).fields
        federate_handle = join_fields[0]

        assert transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("FedPro2025Support",))).fields == (federate_handle,)
        assert transport.request(TransportRequest(command="GET_FEDERATE_NAME", fields=(federate_handle,))).fields == ("FedPro2025Support",)
        assert transport.request(TransportRequest(command="NORMALIZE_FEDERATE_HANDLE", fields=(federate_handle,))).fields == (federate_handle,)
        assert transport.request(TransportRequest(command="NORMALIZE_SERVICE_GROUP", fields=("FEDERATION_MANAGEMENT",))).fields == ("0",)

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        assert transport.request(TransportRequest(command="GET_OBJECT_CLASS_NAME", fields=(object_class,))).fields == ("HLAobjectRoot.Target",)
        assert transport.request(TransportRequest(command="NORMALIZE_OBJECT_CLASS_HANDLE", fields=(object_class,))).fields == (object_class,)
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        assert transport.request(TransportRequest(command="GET_ATTRIBUTE_NAME", fields=(object_class, attribute))).fields == ("Position",)
        object_instance = transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProSupportTarget-1"))).fields[0]
        assert transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=("FedProSupportTarget-1",))).fields == (
            object_instance,
        )
        assert transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(object_instance,))).fields == (
            "FedProSupportTarget-1",
        )
        assert transport.request(TransportRequest(command="GET_KNOWN_OBJECT_CLASS_HANDLE", fields=(object_instance,))).fields == (object_class,)
        assert transport.request(TransportRequest(command="NORMALIZE_OBJECT_INSTANCE_HANDLE", fields=(object_instance,))).fields == (object_instance,)

        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        assert transport.request(TransportRequest(command="GET_INTERACTION_CLASS_NAME", fields=(interaction_class,))).fields == (
            "HLAinteractionRoot.TrackReport",
        )
        assert transport.request(TransportRequest(command="NORMALIZE_INTERACTION_CLASS_HANDLE", fields=(interaction_class,))).fields == (interaction_class,)
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert transport.request(TransportRequest(command="GET_PARAMETER_NAME", fields=(interaction_class, parameter))).fields == ("TrackId",)
        assert transport.request(TransportRequest(command="GET_AVAILABLE_DIMENSIONS_FOR_INTERACTION_CLASS", fields=(interaction_class,))).fields

        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert transport.request(TransportRequest(command="GET_DIMENSION_NAME", fields=(dimension,))).fields == ("RoutingSpace",)
        assert transport.request(TransportRequest(command="GET_DIMENSION_UPPER_BOUND", fields=(dimension,))).fields == ("1024",)
        region = transport.request(TransportRequest(command="CREATE_REGION", fields=(dimension,))).fields[0]
        assert transport.request(TransportRequest(command="GET_DIMENSION_HANDLE_SET", fields=(region,))).fields == (dimension,)
        assert transport.request(TransportRequest(command="SET_RANGE_BOUNDS", fields=(region, dimension, "12:34"))).fields == ()
        assert transport.request(TransportRequest(command="GET_RANGE_BOUNDS", fields=(region, dimension))).fields == ("12", "34")

        transportation = transport.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_HANDLE", fields=("HLAbestEffort",))).fields[0]
        assert transport.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_NAME", fields=(transportation,))).fields == ("HLAbestEffort",)
        assert transport.request(TransportRequest(command="GET_ORDER_TYPE", fields=("HLAtimestamp",))).fields == ("TIMESTAMP",)
        assert transport.request(TransportRequest(command="GET_ORDER_NAME", fields=("TIMESTAMP",))).fields == ("HLAtimestamp",)
        assert transport.request(TransportRequest(command="GET_UPDATE_RATE_VALUE", fields=("HLAdefaultUpdateRate",))).fields == ("1.0",)
        assert transport.request(TransportRequest(command="GET_UPDATE_RATE_VALUE_FOR_ATTRIBUTE", fields=(object_instance, attribute))).fields == ("1.0",)
        assert (
            transport.request(
                TransportRequest(
                    command="REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
                    fields=(object_instance, attribute, transportation),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
            object_instance,
            attribute,
            transportation,
        )
        assert transport.request(
            TransportRequest(command="QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", fields=(object_instance, attribute))
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE",
            object_instance,
            attribute,
            transportation,
        )
        assert (
            transport.request(
                TransportRequest(
                    command="REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
                    fields=(interaction_class, transportation),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
            interaction_class,
            transportation,
        )
        assert transport.request(
            TransportRequest(
                command="QUERY_INTERACTION_TRANSPORTATION_TYPE",
                fields=(federate_handle, interaction_class),
            )
        ).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REPORT_INTERACTION_TRANSPORTATION_TYPE",
            federate_handle,
            interaction_class,
            transportation,
        )

        assert transport.request(TransportRequest(command="MODIFY_LOOKAHEAD", fields=("HLAinteger64Interval", "3"))).fields == ()
        assert transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields == ("HLAinteger64Interval", "3")
        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "18"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "18")
        assert transport.request(TransportRequest(command="QUERY_GALT")).fields == ("1", "HLAinteger64Time", "18")
        assert transport.request(TransportRequest(command="QUERY_LITS")).fields == ("1", "HLAinteger64Time", "18")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "getFederateHandleRequest",
            "getFederateNameRequest",
            "getAttributeNameRequest",
            "getParameterNameRequest",
            "getDimensionNameRequest",
            "getTransportationTypeNameRequest",
            "requestAttributeTransportationTypeChangeRequest",
            "queryAttributeTransportationTypeRequest",
            "requestInteractionTransportationTypeChangeRequest",
            "queryInteractionTransportationTypeRequest",
            "getOrderTypeRequest",
            "getOrderNameRequest",
            "normalizeServiceGroupRequest",
            "normalizeObjectInstanceHandleRequest",
            "queryGALTRequest",
            "queryLITSRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-001",
    "HLA2025-FI-SVC-002",
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-011",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_lifecycle_session_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-lifecycle"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert (
            transport.request(
                TransportRequest(
                    command="CREATE",
                    fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"),
                )
            ).fields
            == ()
        )
        assert transport.request(
            TransportRequest(
                command="JOIN",
                fields=("FedPro2025Federate", "TestFederate", federation_name),
            )
        ).fields == ("1", "HLAinteger64Time")

        callback = transport.request(TransportRequest(command="EVOKE"))
        assert callback.fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert server.servicer.calls == [
            "connectRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
            "joinFederationExecutionWithNameRequest",
            "resignFederationExecutionRequest",
            "destroyFederationExecutionRequest",
            "disconnectRequest",
        ]
        assert federation_name not in server.servicer.federations
        assert server.servicer.joined_federates == {}
    finally:
        if transport is not None:
            transport.close()
        server.close()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-076",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-157",
    "HLA2025-FI-SVC-162",
    "HLA2025-FI-SVC-163",
    "HLA2025-FI-SVC-164",
    "HLA2025-BND-003",
)
def test_2025_transport_server_runs_runtime_capability_session_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-runtime"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "RouteCapability2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Federate", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.RouteTarget",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert transport.request(TransportRequest(command="GET_AVAILABLE_DIMENSIONS_FOR_OBJECT_CLASS", fields=(object_class,))).fields == (dimension,)
        assert transport.request(TransportRequest(command="GET_DIMENSION_UPPER_BOUND", fields=(dimension,))).fields == ("1024",)

        best_effort = transport.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_HANDLE", fields=("HLAbestEffort",))).fields[0]
        assert (
            transport.request(
                TransportRequest(
                    command="CHANGE_DEFAULT_ATTRIBUTE_TRANSPORTATION_TYPE",
                    fields=(object_class, attribute, best_effort),
                )
            ).fields
            == ()
        )
        assert (
            transport.request(
                TransportRequest(
                    command="CHANGE_DEFAULT_ATTRIBUTE_ORDER_TYPE",
                    fields=(object_class, attribute, "TIMESTAMP"),
                )
            ).fields
            == ()
        )

        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProRouteTarget-1"))
        ).fields[0]
        assert transport.request(TransportRequest(command="IS_ATTRIBUTE_OWNED_BY_FEDERATE", fields=(object_instance, attribute))).fields == ("1",)
        assert (
            transport.request(
                TransportRequest(
                    command="UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute, "72756e74696d652d646976657374"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="IS_ATTRIBUTE_OWNED_BY_FEDERATE", fields=(object_instance, attribute))).fields == ("0",)
        assert transport.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "ATTRIBUTE_IS_NOT_OWNED", object_instance, attribute)
        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                    fields=(object_instance, attribute, "72756e74696d652d636c61696d"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "72756e74696d652d636c61696d",
        )

        assert transport.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=("HLAinteger64Time", "1"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_REGULATION_ENABLED", "HLAinteger64Time", "0")
        assert transport.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED")).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_CONSTRAINED_ENABLED", "HLAinteger64Time", "0")
        assert transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=("HLAinteger64Time", "9"))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "9")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "getObjectClassHandleRequest",
            "getAttributeHandleRequest",
            "getAvailableDimensionsForObjectClassRequest",
            "changeDefaultAttributeTransportationTypeRequest",
            "changeDefaultAttributeOrderTypeRequest",
            "registerObjectInstanceWithNameRequest",
            "unconditionalAttributeOwnershipDivestitureRequest",
            "attributeOwnershipAcquisitionIfAvailableRequest",
            "timeAdvanceRequestRequest",
        } <= set(server.servicer.calls)
        assert server.servicer.default_attribute_transportation == {(object_class, attribute): best_effort}
        assert server.servicer.default_attribute_order == {(object_class, attribute): datatypes_pb2.TIMESTAMP}
    finally:
        if transport is not None:
            transport.close()
        server.close()
