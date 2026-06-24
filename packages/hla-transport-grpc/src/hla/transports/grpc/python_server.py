"""Transport-hosted Python RTI server for proving the gRPC wire path."""
from __future__ import annotations

from concurrent import futures
from dataclasses import dataclass, field
from typing import Any, Mapping

from hla.transports.common.hosted_server import HostedRTICommandProcessor

from hla.rti1516e.exceptions import RTIexception
from hla.runtime.factory import create_rti_ambassador

from hla.transports.grpc.fedpro2010 import FederateAmbassador_pb2 as callback_pb2
from hla.transports.grpc.fedpro2010 import HLA2010RTITransport_pb2_grpc as pb2_grpc
from hla.transports.grpc.fedpro2010 import datatypes_pb2
from .client import GrpcTransportClientAdapter

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


@dataclass(frozen=True)
class PythonRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    engine: Any | None = None
    python_config: Any | None = None


@dataclass(frozen=True)
class CERTIRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    backend_options: Mapping[str, Any] = field(default_factory=dict)


def _handle(message: Any, field: str, value: str) -> None:
    getattr(message, field).data = str(value).encode("ascii")


def _handle_set(message: Any, field: str, values: str) -> None:
    repeated = getattr(getattr(message, field), "attributeHandle")
    for item in values.split(","):
        if item:
            repeated.add(data=item.encode("ascii"))


def _federate_handle_set(message: Any, field: str, values: str) -> None:
    repeated = getattr(getattr(message, field), "federateHandle")
    for item in values.split(","):
        if item:
            repeated.add(data=item.encode("ascii"))


def _handle_value_map(message: Any, field: str, repeated_name: str, handle_field: str, values: str) -> None:
    repeated = getattr(getattr(message, field), repeated_name)
    for item in values.split(","):
        if not item:
            continue
        handle, payload = item.split(":", 1)
        row = repeated.add()
        getattr(row, handle_field).data = handle.encode("ascii")
        row.value = bytes.fromhex(payload)


def _time_payload(type_name: str, value: str) -> bytes:
    return f"{type_name}:{value}".encode("ascii")


def _order(value: str) -> int:
    return {"1": datatypes_pb2.RECEIVE, "2": datatypes_pb2.TIMESTAMP}.get(str(value), int(value))


def _callback_request(parts: tuple[str, ...]) -> Any:
    if not parts:
        return callback_pb2.CallbackRequest()
    kind, *fields = parts
    builder = _CALLBACK_BUILDERS.get(kind)
    if builder is None:
        return callback_pb2.CallbackRequest()
    return builder(fields)


def _discover(fields: list[str]) -> Any:
    payload = callback_pb2.DiscoverObjectInstance(objectInstanceName=fields[2])
    _handle(payload, "objectInstance", fields[0])
    _handle(payload, "objectClass", fields[1])
    return callback_pb2.CallbackRequest(discoverObjectInstance=payload)


def _reflect(fields: list[str]) -> Any:
    payload = callback_pb2.ReflectAttributeValues(userSuppliedTag=bytes.fromhex(fields[2]), sentOrderType=_order(fields[3]))
    _handle(payload, "objectInstance", fields[0])
    _handle_value_map(payload, "attributeValues", "attributeHandleValue", "attributeHandle", fields[1])
    _handle(payload, "transportationType", fields[4])
    return callback_pb2.CallbackRequest(reflectAttributeValues=payload)


def _reflect_tso(fields: list[str]) -> Any:
    payload = callback_pb2.ReflectAttributeValuesWithTime(
        userSuppliedTag=bytes.fromhex(fields[2]),
        sentOrderType=_order(fields[3]),
        receivedOrderType=_order(fields[7]),
    )
    _handle(payload, "objectInstance", fields[0])
    _handle_value_map(payload, "attributeValues", "attributeHandleValue", "attributeHandle", fields[1])
    _handle(payload, "transportationType", fields[4])
    payload.time.data = _time_payload(fields[5], fields[6])
    return callback_pb2.CallbackRequest(reflectAttributeValuesWithTime=payload)


def _interaction(fields: list[str]) -> Any:
    payload = callback_pb2.ReceiveInteraction(userSuppliedTag=bytes.fromhex(fields[2]), sentOrderType=_order(fields[3]))
    _handle(payload, "interactionClass", fields[0])
    _handle_value_map(payload, "parameterValues", "parameterHandleValue", "parameterHandle", fields[1])
    _handle(payload, "transportationType", fields[4])
    return callback_pb2.CallbackRequest(receiveInteraction=payload)


def _interaction_tso(fields: list[str]) -> Any:
    payload = callback_pb2.ReceiveInteractionWithTime(
        userSuppliedTag=bytes.fromhex(fields[2]),
        sentOrderType=_order(fields[3]),
        receivedOrderType=_order(fields[7]),
    )
    _handle(payload, "interactionClass", fields[0])
    _handle_value_map(payload, "parameterValues", "parameterHandleValue", "parameterHandle", fields[1])
    _handle(payload, "transportationType", fields[4])
    payload.time.data = _time_payload(fields[5], fields[6])
    return callback_pb2.CallbackRequest(receiveInteractionWithTime=payload)


def _remove(fields: list[str]) -> Any:
    payload = callback_pb2.RemoveObjectInstance(userSuppliedTag=bytes.fromhex(fields[1]))
    _handle(payload, "objectInstance", fields[0])
    if len(fields) >= 4:
        payload.sentOrderType = _order(fields[2])
    return callback_pb2.CallbackRequest(removeObjectInstance=payload)


def _time(field_name: str, message_type: Any):
    def build(fields: list[str]) -> Any:
        payload = message_type()
        payload.time.data = _time_payload(fields[0], fields[1])
        return callback_pb2.CallbackRequest(**{field_name: payload})

    return build


def _one_handle(field_name: str, message_type: Any, handle_field: str):
    def build(fields: list[str]) -> Any:
        payload = message_type()
        _handle(payload, handle_field, fields[0])
        return callback_pb2.CallbackRequest(**{field_name: payload})

    return build


def _announce(fields: list[str]) -> Any:
    return callback_pb2.CallbackRequest(
        announceSynchronizationPoint=callback_pb2.AnnounceSynchronizationPoint(
            synchronizationPointLabel=fields[0],
            userSuppliedTag=bytes.fromhex(fields[1]),
        )
    )


def _federation_synchronized(fields: list[str]) -> Any:
    payload = callback_pb2.FederationSynchronized(synchronizationPointLabel=fields[0])
    _federate_handle_set(payload, "failedToSyncSet", fields[1])
    return callback_pb2.CallbackRequest(federationSynchronized=payload)


def _save_status_response(fields: list[str]) -> Any:
    payload = callback_pb2.FederationSaveStatusResponse()
    if fields and fields[0]:
        for item in fields[0].split(";"):
            federate, status = item.split(":", 1)
            payload.response.federateHandleSaveStatusPair.add(
                federateHandle=datatypes_pb2.FederateHandle(data=federate.encode("ascii")),
                saveStatus=getattr(datatypes_pb2, status),
            )
    return callback_pb2.CallbackRequest(federationSaveStatusResponse=payload)


def _restore_status_response(fields: list[str]) -> Any:
    payload = callback_pb2.FederationRestoreStatusResponse()
    if fields and fields[0]:
        for item in fields[0].split(";"):
            pre, post, status = item.split(":", 2)
            payload.response.federateRestoreStatus.add(
                preRestoreHandle=datatypes_pb2.FederateHandle(data=pre.encode("ascii")),
                postRestoreHandle=datatypes_pb2.FederateHandle(data=post.encode("ascii")),
                restoreStatus=getattr(datatypes_pb2, status),
            )
    return callback_pb2.CallbackRequest(federationRestoreStatusResponse=payload)


def _ownership_with_attributes(field_name: str, message_type: Any, attr_field: str, tag: bool):
    def build(fields: list[str]) -> Any:
        kwargs = {"userSuppliedTag": bytes.fromhex(fields[2])} if tag else {}
        payload = message_type(**kwargs)
        _handle(payload, "objectInstance", fields[0])
        _handle_set(payload, attr_field, fields[1])
        return callback_pb2.CallbackRequest(**{field_name: payload})

    return build


def _provide_attribute_value_update(fields: list[str]) -> Any:
    payload = callback_pb2.ProvideAttributeValueUpdate(userSuppliedTag=bytes.fromhex(fields[2]))
    _handle(payload, "objectInstance", fields[0])
    _handle_set(payload, "attributes", fields[1])
    return callback_pb2.CallbackRequest(provideAttributeValueUpdate=payload)


_CALLBACK_BUILDERS = {
    "DISCOVER": _discover,
    "REFLECT": _reflect,
    "REFLECT_TSO": _reflect_tso,
    "INTERACTION": _interaction,
    "INTERACTION_TSO": _interaction_tso,
    "REMOVE_OBJECT_INSTANCE": _remove,
    "TIME_REGULATION_ENABLED": _time("timeRegulationEnabled", callback_pb2.TimeRegulationEnabled),
    "TIME_CONSTRAINED_ENABLED": _time("timeConstrainedEnabled", callback_pb2.TimeConstrainedEnabled),
    "TIME_ADVANCE_GRANT": _time("timeAdvanceGrant", callback_pb2.TimeAdvanceGrant),
    "REQUEST_RETRACTION": _one_handle("requestRetraction", callback_pb2.RequestRetraction, "retraction"),
    "START_REGISTRATION_FOR_OBJECT_CLASS": _one_handle(
        "startRegistrationForObjectClass", callback_pb2.StartRegistrationForObjectClass, "objectClass"
    ),
    "STOP_REGISTRATION_FOR_OBJECT_CLASS": _one_handle(
        "stopRegistrationForObjectClass", callback_pb2.StopRegistrationForObjectClass, "objectClass"
    ),
    "TURN_INTERACTIONS_ON": _one_handle("turnInteractionsOn", callback_pb2.TurnInteractionsOn, "interactionClass"),
    "TURN_INTERACTIONS_OFF": _one_handle("turnInteractionsOff", callback_pb2.TurnInteractionsOff, "interactionClass"),
    "PROVIDE_ATTRIBUTE_VALUE_UPDATE": _provide_attribute_value_update,
    "SYNC_POINT_REGISTRATION_SUCCEEDED": lambda fields: callback_pb2.CallbackRequest(
        synchronizationPointRegistrationSucceeded=callback_pb2.SynchronizationPointRegistrationSucceeded(
            synchronizationPointLabel=fields[0]
        )
    ),
    "ANNOUNCE_SYNC_POINT": _announce,
    "FEDERATION_SYNCHRONIZED": _federation_synchronized,
    "INITIATE_FEDERATE_SAVE": lambda fields: callback_pb2.CallbackRequest(
        initiateFederateSave=callback_pb2.InitiateFederateSave(label=fields[0])
    ),
    "FEDERATION_SAVED": lambda fields: callback_pb2.CallbackRequest(federationSaved=callback_pb2.FederationSaved()),
    "FEDERATION_NOT_SAVED": lambda fields: callback_pb2.CallbackRequest(
        federationNotSaved=callback_pb2.FederationNotSaved(reason=getattr(datatypes_pb2, fields[0]))
    ),
    "FEDERATION_SAVE_STATUS_RESPONSE": _save_status_response,
    "REQUEST_FEDERATION_RESTORE_SUCCEEDED": lambda fields: callback_pb2.CallbackRequest(
        requestFederationRestoreSucceeded=callback_pb2.RequestFederationRestoreSucceeded(label=fields[0])
    ),
    "REQUEST_FEDERATION_RESTORE_FAILED": lambda fields: callback_pb2.CallbackRequest(
        requestFederationRestoreFailed=callback_pb2.RequestFederationRestoreFailed(label=fields[0])
    ),
    "FEDERATION_RESTORE_BEGUN": lambda fields: callback_pb2.CallbackRequest(
        federationRestoreBegun=callback_pb2.FederationRestoreBegun()
    ),
    "INITIATE_FEDERATE_RESTORE": lambda fields: callback_pb2.CallbackRequest(
        initiateFederateRestore=callback_pb2.InitiateFederateRestore(
            label=fields[0],
            federateName=fields[1],
            postRestoreFederateHandle=datatypes_pb2.FederateHandle(data=fields[2].encode("ascii")),
        )
    ),
    "FEDERATION_RESTORED": lambda fields: callback_pb2.CallbackRequest(federationRestored=callback_pb2.FederationRestored()),
    "FEDERATION_RESTORE_STATUS_RESPONSE": _restore_status_response,
    "OWNERSHIP_ACQUIRED": _ownership_with_attributes(
        "attributeOwnershipAcquisitionNotification",
        callback_pb2.AttributeOwnershipAcquisitionNotification,
        "securedAttributes",
        True,
    ),
    "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION": _ownership_with_attributes(
        "requestAttributeOwnershipAssumption",
        callback_pb2.RequestAttributeOwnershipAssumption,
        "offeredAttributes",
        True,
    ),
    "ATTRIBUTE_OWNERSHIP_UNAVAILABLE": _ownership_with_attributes(
        "attributeOwnershipUnavailable", callback_pb2.AttributeOwnershipUnavailable, "attributes", False
    ),
    "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE": _ownership_with_attributes(
        "requestAttributeOwnershipRelease", callback_pb2.RequestAttributeOwnershipRelease, "candidateAttributes", True
    ),
    "REQUEST_DIVESTITURE_CONFIRMATION": _ownership_with_attributes(
        "requestDivestitureConfirmation", callback_pb2.RequestDivestitureConfirmation, "offeredAttributes", False
    ),
    "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION": _ownership_with_attributes(
        "confirmAttributeOwnershipAcquisitionCancellation",
        callback_pb2.ConfirmAttributeOwnershipAcquisitionCancellation,
        "attributes",
        False,
    ),
    "INFORM_ATTRIBUTE_OWNERSHIP": lambda fields: callback_pb2.CallbackRequest(
        informAttributeOwnership=callback_pb2.InformAttributeOwnership(
            objectInstance=datatypes_pb2.ObjectInstanceHandle(data=fields[0].encode("ascii")),
            attribute=datatypes_pb2.AttributeHandle(data=fields[1].encode("ascii")),
            federate=datatypes_pb2.FederateHandle(data=fields[2].encode("ascii")),
        )
    ),
    "ATTRIBUTE_IS_NOT_OWNED": lambda fields: callback_pb2.CallbackRequest(
        attributeIsNotOwned=callback_pb2.AttributeIsNotOwned(
            objectInstance=datatypes_pb2.ObjectInstanceHandle(data=fields[0].encode("ascii")),
            attribute=datatypes_pb2.AttributeHandle(data=fields[1].encode("ascii")),
        )
    ),
}


class _FedPro2010GatewayServicer(pb2_grpc.HLA2010FedProGatewayServicer):
    def __init__(self, rti: Any) -> None:
        self.adapter = GrpcTransportClientAdapter()
        self.processor = HostedRTICommandProcessor(rti)

    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        try:
            transport_request = self.adapter.decode_call_request(request)
            transport_response = self.processor.handle_request(transport_request)
            return self.adapter.encode_response(request, transport_response)
        except RTIexception as exc:
            return self.adapter.encode_error(exc.__class__.__name__, str(exc))
        except Exception as exc:  # pragma: no cover - defensive server guard
            return self.adapter.encode_error("RTIinternalError", str(exc))

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        try:
            self.processor.rti.evoke_multiple_callbacks(0.0, 0.0)
        except Exception:
            try:
                self.processor.rti.evoke_callback(0.0)
            except Exception:
                pass
        if self.processor.federate.pending:
            return _callback_request(self.processor.federate.pending.popleft())
        return callback_pb2.CallbackRequest()

    def close(self) -> None:
        self.processor.close()


class PythonRTIGrpcServer:
    def __init__(self, config: PythonRTIGrpcServerConfig = PythonRTIGrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _FedPro2010GatewayServicer(
            create_rti_ambassador("python", engine=config.engine, config=config.python_config)
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_HLA2010FedProGatewayServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "PythonRTIGrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        self.servicer.close()
        if self._started:
            self.server.stop(0).wait()
            self._started = False


class CERTIRTIGrpcServer:
    def __init__(self, config: CERTIRTIGrpcServerConfig = CERTIRTIGrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _FedPro2010GatewayServicer(create_rti_ambassador("certi", **dict(config.backend_options)))
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_HLA2010FedProGatewayServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "CERTIRTIGrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        self.servicer.close()
        if self._started:
            self.server.stop(0).wait()
            self._started = False


def start_python_grpc_server(
    *,
    engine: Any | None = None,
    python_config: Any | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
) -> PythonRTIGrpcServer:
    return PythonRTIGrpcServer(
        PythonRTIGrpcServerConfig(host=host, port=port, engine=engine, python_config=python_config)
    ).start()


def start_certi_grpc_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    **backend_options: Any,
) -> CERTIRTIGrpcServer:
    return CERTIRTIGrpcServer(
        CERTIRTIGrpcServerConfig(host=host, port=port, backend_options=dict(backend_options))
    ).start()


__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "start_certi_grpc_server",
    "start_python_grpc_server",
]
