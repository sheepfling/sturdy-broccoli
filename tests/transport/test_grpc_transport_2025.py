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

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert {
            "createRegionRequest",
            "setRangeBoundsRequest",
            "commitRegionModificationsRequest",
            "associateRegionsForUpdatesRequest",
            "subscribeObjectClassAttributesWithRegionsRequest",
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
