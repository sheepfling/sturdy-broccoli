"""Transport-hosted IEEE 1516.1-2025 RTI server for the gRPC wire path."""

from __future__ import annotations

from concurrent import futures
from dataclasses import dataclass

from hla.transports.grpc.fedpro2025 import FederateAmbassador_2025_pb2 as callback_pb2
from hla.transports.grpc.fedpro2025 import HLA2025RTITransport_pb2_grpc as pb2_grpc
from hla.transports.grpc.fedpro2025 import RTIambassador_2025_pb2 as rti_pb2
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2 as datatypes_pb2

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


@dataclass(frozen=True)
class RTI2025GrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4


def _callback_request() -> callback_pb2.CallbackRequest:
    return callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:7")))


def _handle(handle_type: type, value: str | int):
    return handle_type(data=str(value).encode("ascii"))


def _attribute_set(values: list[str] | tuple[str, ...] | str) -> datatypes_pb2.AttributeHandleSet:
    result = datatypes_pb2.AttributeHandleSet()
    items = values.split(",") if isinstance(values, str) else values
    for item in items:
        if item:
            result.attributeHandle.add(data=str(item).encode("ascii"))
    return result


def _dimension_set(values: list[str] | tuple[str, ...] | str) -> datatypes_pb2.DimensionHandleSet:
    result = datatypes_pb2.DimensionHandleSet()
    items = values.split(",") if isinstance(values, str) else values
    for item in items:
        if item:
            result.dimensionHandle.add(data=str(item).encode("ascii"))
    return result


class _FedPro2025GatewayServicer(pb2_grpc.HLA2025FedProGatewayServicer):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.federations: set[str] = set()
        self.joined_federates: dict[str, str] = {}
        self.next_federate_handle = 1
        self.next_object_instance_handle = 1000
        self.object_classes = {"HLAobjectRoot.RouteTarget": "100", "HLAobjectRoot.Target": "101"}
        self.object_class_names = {value: key for key, value in self.object_classes.items()}
        self.attributes = {("100", "Position"): "200", ("101", "Position"): "201"}
        self.dimensions = {"RoutingSpace": "300"}
        self.transportations = {"HLAreliable": "1", "HLAbestEffort": "2"}
        self.object_instances: dict[str, dict[str, str]] = {}
        self.unowned_attributes: set[tuple[str, str]] = set()
        self.default_attribute_transportation: dict[tuple[str, str], str] = {}
        self.default_attribute_order: dict[tuple[str, str], int] = {}
        self.callback_queue: list[callback_pb2.CallbackRequest] = []

    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        request_kind = request.WhichOneof("callRequest")
        if request_kind is not None:
            self.calls.append(request_kind)
        if request_kind in {
            "connectRequest",
            "connectWithCredentialsRequest",
            "connectWithConfigurationRequest",
            "connectWithConfigurationAndCredentialsRequest",
        }:
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "disconnectRequest":
            self.joined_federates.clear()
            return rti_pb2.CallResponse(disconnectResponse=rti_pb2.DisconnectResponse())
        if request_kind in {
            "createFederationExecutionWithModulesRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
        }:
            payload = getattr(request, request_kind)
            self.federations.add(payload.federationName)
            if request_kind == "createFederationExecutionWithModulesAndTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithModulesAndTimeResponse=rti_pb2.CreateFederationExecutionWithModulesAndTimeResponse())
            return rti_pb2.CallResponse(createFederationExecutionWithModulesResponse=rti_pb2.CreateFederationExecutionWithModulesResponse())
        if request_kind in {
            "joinFederationExecutionRequest",
            "joinFederationExecutionWithNameRequest",
            "joinFederationExecutionWithModulesRequest",
            "joinFederationExecutionWithNameAndModulesRequest",
        }:
            payload = getattr(request, request_kind)
            federation_name = payload.federationName
            if federation_name not in self.federations:
                return self._error("FederationExecutionDoesNotExist", federation_name)
            federate_name = getattr(payload, "federateName", "") or f"fedpro-federate-{self.next_federate_handle}"
            handle = self.next_federate_handle
            self.next_federate_handle += 1
            self.joined_federates[federate_name] = federation_name
            result = datatypes_pb2.JoinResult(
                federateHandle=datatypes_pb2.FederateHandle(data=str(handle).encode("ascii")),
                logicalTimeImplementationName="HLAinteger64Time",
            )
            if request_kind in {"joinFederationExecutionWithNameRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                return rti_pb2.CallResponse(joinFederationExecutionWithNameResponse=rti_pb2.JoinFederationExecutionWithNameResponse(result=result))
            return rti_pb2.CallResponse(joinFederationExecutionResponse=rti_pb2.JoinFederationExecutionResponse(result=result))
        if request_kind == "resignFederationExecutionRequest":
            self.joined_federates.clear()
            return rti_pb2.CallResponse(resignFederationExecutionResponse=rti_pb2.ResignFederationExecutionResponse())
        if request_kind == "destroyFederationExecutionRequest":
            payload = request.destroyFederationExecutionRequest
            if self.joined_federates:
                return self._error("FederatesCurrentlyJoined", payload.federationName)
            self.federations.discard(payload.federationName)
            return rti_pb2.CallResponse(destroyFederationExecutionResponse=rti_pb2.DestroyFederationExecutionResponse())
        if request_kind == "getFederateHandleRequest":
            return rti_pb2.CallResponse(getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(result=datatypes_pb2.FederateHandle(data=b"42")))
        if request_kind == "getObjectClassHandleRequest":
            name = request.getObjectClassHandleRequest.objectClassName
            try:
                handle = self.object_classes[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(getObjectClassHandleResponse=rti_pb2.GetObjectClassHandleResponse(result=_handle(datatypes_pb2.ObjectClassHandle, handle)))
        if request_kind == "getObjectClassNameRequest":
            handle = request.getObjectClassNameRequest.objectClass.data.decode("ascii")
            return rti_pb2.CallResponse(getObjectClassNameResponse=rti_pb2.GetObjectClassNameResponse(result=self.object_class_names.get(handle, "")))
        if request_kind == "getAttributeHandleRequest":
            payload = request.getAttributeHandleRequest
            object_class = payload.objectClass.data.decode("ascii")
            try:
                handle = self.attributes[(object_class, payload.attributeName)]
            except KeyError:
                return self._error("NameNotFound", payload.attributeName)
            return rti_pb2.CallResponse(getAttributeHandleResponse=rti_pb2.GetAttributeHandleResponse(result=_handle(datatypes_pb2.AttributeHandle, handle)))
        if request_kind == "getDimensionHandleRequest":
            name = request.getDimensionHandleRequest.dimensionName
            try:
                handle = self.dimensions[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(getDimensionHandleResponse=rti_pb2.GetDimensionHandleResponse(result=_handle(datatypes_pb2.DimensionHandle, handle)))
        if request_kind == "getAvailableDimensionsForObjectClassRequest":
            return rti_pb2.CallResponse(
                getAvailableDimensionsForObjectClassResponse=rti_pb2.GetAvailableDimensionsForObjectClassResponse(
                    result=_dimension_set(("300",))
                )
            )
        if request_kind == "getDimensionUpperBoundRequest":
            return rti_pb2.CallResponse(getDimensionUpperBoundResponse=rti_pb2.GetDimensionUpperBoundResponse(result=1024))
        if request_kind == "getTransportationTypeHandleRequest":
            name = request.getTransportationTypeHandleRequest.transportationTypeName
            try:
                handle = self.transportations[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(
                getTransportationTypeHandleResponse=rti_pb2.GetTransportationTypeHandleResponse(
                    result=_handle(datatypes_pb2.TransportationTypeHandle, handle)
                )
            )
        if request_kind == "changeDefaultAttributeTransportationTypeRequest":
            payload = request.changeDefaultAttributeTransportationTypeRequest
            object_class = payload.objectClass.data.decode("ascii")
            transportation = payload.transportationType.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_transportation[(object_class, attribute.data.decode("ascii"))] = transportation
            return rti_pb2.CallResponse(changeDefaultAttributeTransportationTypeResponse=rti_pb2.ChangeDefaultAttributeTransportationTypeResponse())
        if request_kind == "changeDefaultAttributeOrderTypeRequest":
            payload = request.changeDefaultAttributeOrderTypeRequest
            object_class = payload.theObjectClass.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_order[(object_class, attribute.data.decode("ascii"))] = payload.orderType
            return rti_pb2.CallResponse(changeDefaultAttributeOrderTypeResponse=rti_pb2.ChangeDefaultAttributeOrderTypeResponse())
        if request_kind in {"registerObjectInstanceRequest", "registerObjectInstanceWithNameRequest"}:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            handle = str(self.next_object_instance_handle)
            self.next_object_instance_handle += 1
            object_name = getattr(payload, "objectInstanceName", "") or f"fedpro-object-{handle}"
            self.object_instances[handle] = {"name": object_name, "objectClass": object_class}
            response_kind = "registerObjectInstanceWithNameResponse" if request_kind == "registerObjectInstanceWithNameRequest" else "registerObjectInstanceResponse"
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type(result=_handle(datatypes_pb2.ObjectInstanceHandle, handle))})
        if request_kind == "isAttributeOwnedByFederateRequest":
            payload = request.isAttributeOwnedByFederateRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            attribute = payload.attribute.data.decode("ascii")
            return rti_pb2.CallResponse(
                isAttributeOwnedByFederateResponse=rti_pb2.IsAttributeOwnedByFederateResponse(
                    result=(object_instance, attribute) not in self.unowned_attributes
                )
            )
        if request_kind == "unconditionalAttributeOwnershipDivestitureRequest":
            payload = request.unconditionalAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.unowned_attributes.add((object_instance, attribute.data.decode("ascii")))
            return rti_pb2.CallResponse(unconditionalAttributeOwnershipDivestitureResponse=rti_pb2.UnconditionalAttributeOwnershipDivestitureResponse())
        if request_kind == "queryAttributeOwnershipRequest":
            payload = request.queryAttributeOwnershipRequest
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeIsNotOwned=callback_pb2.AttributeIsNotOwned(
                        objectInstance=payload.objectInstance,
                        attributes=payload.attributes,
                    )
                )
            )
            return rti_pb2.CallResponse(queryAttributeOwnershipResponse=rti_pb2.QueryAttributeOwnershipResponse())
        if request_kind == "attributeOwnershipAcquisitionIfAvailableRequest":
            payload = request.attributeOwnershipAcquisitionIfAvailableRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.desiredAttributes.attributeHandle:
                self.unowned_attributes.discard((object_instance, attribute.data.decode("ascii")))
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                        objectInstance=payload.objectInstance,
                        securedAttributes=payload.desiredAttributes,
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                )
            )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionIfAvailableResponse=rti_pb2.AttributeOwnershipAcquisitionIfAvailableResponse())
        if request_kind == "enableTimeRegulationRequest":
            self.callback_queue.append(callback_pb2.CallbackRequest(timeRegulationEnabled=callback_pb2.TimeRegulationEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeRegulationResponse=rti_pb2.EnableTimeRegulationResponse())
        if request_kind == "enableTimeConstrainedRequest":
            self.callback_queue.append(callback_pb2.CallbackRequest(timeConstrainedEnabled=callback_pb2.TimeConstrainedEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeConstrainedResponse=rti_pb2.EnableTimeConstrainedResponse())
        if request_kind == "timeAdvanceRequestRequest":
            self.callback_queue.append(callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=request.timeAdvanceRequestRequest.time)))
            return rti_pb2.CallResponse(timeAdvanceRequestResponse=rti_pb2.TimeAdvanceRequestResponse())
        return self._error("RTIinternalError", f"Unsupported 2025 test call: {request_kind}")

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        if self.callback_queue:
            return self.callback_queue.pop(0)
        return _callback_request()

    @staticmethod
    def _error(name: str, details: str) -> rti_pb2.CallResponse:
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName=name,
                details=details,
            )
        )


class RTI2025GrpcServer:
    def __init__(self, config: RTI2025GrpcServerConfig = RTI2025GrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _FedPro2025GatewayServicer()
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_HLA2025FedProGatewayServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "RTI2025GrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        if self._started:
            self.server.stop(0).wait()
            self._started = False


def start_2025_grpc_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> RTI2025GrpcServer:
    return RTI2025GrpcServer(RTI2025GrpcServerConfig(host=host, port=port)).start()


__all__ = [
    "RTI2025GrpcServer",
    "RTI2025GrpcServerConfig",
    "start_2025_grpc_server",
]
