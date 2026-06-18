from __future__ import annotations

from concurrent import futures

import grpc
import pytest
from hla.transports.common.transport import TransportError, TransportRequest
from hla.transports.grpc import GrpcTransport, GrpcTransportConfig
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

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "publishObjectClassAttributesRequest",
            "subscribeObjectClassAttributesRequest",
            "publishInteractionClassRequest",
            "subscribeInteractionClassRequest",
            "updateAttributeValuesRequest",
            "sendInteractionRequest",
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
        assert transport.request(TransportRequest(command="EVOKE")).fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "45")
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


def test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-negotiated-ownership"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert transport.request(TransportRequest(command="CREATE", fields=(federation_name, "HLAinteger64Time", "Ownership2025.xml"))).fields == ()
        assert transport.request(TransportRequest(command="JOIN", fields=("FedPro2025Owner", "TestFederate", federation_name))).fields == (
            "1",
            "HLAinteger64Time",
        )

        object_class = transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=("HLAobjectRoot.Target",))).fields[0]
        attribute = transport.request(TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(object_class, "Position"))).fields[0]
        object_instance = transport.request(
            TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(object_class, "FedProOwnershipTarget-1"))
        ).fields[0]

        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                    fields=(object_instance, attribute, "6f776e6564"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_OWNERSHIP_UNAVAILABLE",
            object_instance,
            attribute,
            "6f776e6564",
        )

        assert transport.request(TransportRequest(command="QUERY_ATTRIBUTE_OWNERSHIP", fields=(object_instance, attribute))).fields == ()
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "INFORM_ATTRIBUTE_OWNERSHIP",
            object_instance,
            attribute,
            "1",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute, "6f66666572"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            object_instance,
            attribute,
            "6f66666572",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "61637175697265"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_DIVESTITURE_CONFIRMATION",
            object_instance,
            attribute,
            "61637175697265",
        )
        assert (
            transport.request(
                TransportRequest(command="CONFIRM_DIVESTITURE", fields=(object_instance, attribute, "636f6e6669726d"))
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "636f6e6669726d",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "72656c65617365"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
            object_instance,
            attribute,
            "72656c65617365",
        )
        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_RELEASE_DENIED",
                    fields=(object_instance, attribute, "64656e696564"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "ATTRIBUTE_OWNERSHIP_UNAVAILABLE",
            object_instance,
            attribute,
            "64656e696564",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(object_instance, attribute, "63616e63656c"),
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
        assert (
            transport.request(
                TransportRequest(command="CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION", fields=(object_instance, attribute))
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
                    fields=(object_instance, attribute, "7265747279"),
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
        assert transport.request(
            TransportRequest(
                command="ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED",
                fields=(object_instance, attribute, "646976657374"),
            )
        ).fields == (attribute,)
        assert transport.request(TransportRequest(command="EVOKE")).fields == (
            "1",
            "OWNERSHIP_ACQUIRED",
            object_instance,
            attribute,
            "646976657374",
        )

        assert (
            transport.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(object_instance, attribute, "63616e63656c2d6f66666572"),
                )
            ).fields
            == ()
        )
        assert transport.request(TransportRequest(command="EVOKE")).fields[:4] == (
            "1",
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            object_instance,
            attribute,
        )
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

        assert {
            "negotiatedAttributeOwnershipDivestitureRequest",
            "attributeOwnershipAcquisitionRequest",
            "confirmDivestitureRequest",
            "attributeOwnershipReleaseDeniedRequest",
            "cancelAttributeOwnershipAcquisitionRequest",
            "attributeOwnershipDivestitureIfWantedRequest",
            "cancelNegotiatedAttributeOwnershipDivestitureRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


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
                    "1",
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
        assert transport.request(TransportRequest(command="EVOKE")).fields[:2] == ("1", "DISCOVER")
        assert (
            transport.request(
                TransportRequest(
                    command="UNASSOCIATE_REGIONS_FOR_UPDATES",
                    fields=(object_instance, f"{attribute}|{publisher_region}"),
                )
            ).fields
            == ()
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
        assert transport.request(TransportRequest(command="DELETE_REGION", fields=(subscriber_region,))).fields == ()
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
            "unassociateRegionsForUpdatesRequest",
            "subscribeObjectClassAttributesWithRegionsRequest",
            "unsubscribeObjectClassAttributesWithRegionsRequest",
            "deleteRegionRequest",
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
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
        } <= set(server.servicer.calls)
    finally:
        if transport is not None:
            transport.close()
        server.close()


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
        assert transport.request(TransportRequest(command="GET_KNOWN_OBJECT_CLASS_HANDLE", fields=(object_instance,))).fields == (object_class,)
        assert transport.request(TransportRequest(command="NORMALIZE_OBJECT_INSTANCE_HANDLE", fields=(object_instance,))).fields == (object_instance,)

        interaction_class = transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=("HLAinteractionRoot.TrackReport",))).fields[0]
        assert transport.request(TransportRequest(command="GET_INTERACTION_CLASS_NAME", fields=(interaction_class,))).fields == (
            "HLAinteractionRoot.TrackReport",
        )
        assert transport.request(TransportRequest(command="NORMALIZE_INTERACTION_CLASS_HANDLE", fields=(interaction_class,))).fields == (interaction_class,)
        parameter = transport.request(TransportRequest(command="GET_PARAMETER_HANDLE", fields=(interaction_class, "TrackId"))).fields[0]
        assert transport.request(TransportRequest(command="GET_PARAMETER_NAME", fields=(interaction_class, parameter))).fields == ("TrackId",)

        dimension = transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=("RoutingSpace",))).fields[0]
        assert transport.request(TransportRequest(command="GET_DIMENSION_NAME", fields=(dimension,))).fields == ("RoutingSpace",)
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
