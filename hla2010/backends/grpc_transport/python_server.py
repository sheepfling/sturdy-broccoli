"""Transport-hosted Python RTI server for proving the gRPC wire path."""
from __future__ import annotations

from collections import deque
from concurrent import futures
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ...ambassadors import RecordingFederateAmbassador
from ...enums import CallbackModel, ResignAction
from ...exceptions import RTIexception
from ...handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
)
from ...time import HLAfloat64Interval, HLAfloat64Time
from ..python_rti import InMemoryRTIEngine, PythonRTIConfig, rti_ambassador
from ..transport import TransportRequest, TransportResponse
from ..certi_backend import _decode_bytes, _decode_handle_value_map, _decode_handle_set, _encode_bytes, _handle_set_spec, _handle_value_map_spec
from ...rti import create_rti_ambassador
from . import rti_transport_pb2_grpc as pb2_grpc
from .client import GrpcTransportClientAdapter

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


def _federate_handle_set_spec(values: Iterable[FederateHandle]) -> str:
    return ",".join(str(int(value.value)) for value in values)


class _CallbackQueueAmbassador(RecordingFederateAmbassador):
    def __init__(self) -> None:
        super().__init__()
        self.pending: deque[tuple[str, ...]] = deque()

    def record_callback(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        result = super().record_callback(method_name, *args, **kwargs)
        encoded = _encode_callback_payload(method_name, args)
        if encoded is not None:
            self.pending.append(encoded)
        return result


def _encode_callback_payload(method_name: str, args: tuple[Any, ...]) -> tuple[str, ...] | None:
    if method_name == "discoverObjectInstance":
        return ("DISCOVER", str(int(args[0].value)), str(int(args[1].value)), str(args[2]))
    if method_name == "reflectAttributeValues":
        payload = (
            str(int(args[0].value)),
            _handle_value_map_spec(args[1]),
            _encode_bytes(args[2]),
            str(int(args[3].value)),
            str(int(args[4].value)),
        )
        if len(args) >= 7:
            return ("REFLECT_TSO", *payload, str(float(args[5].value)), str(int(args[6].value)))
        return ("REFLECT", *payload)
    if method_name == "receiveInteraction":
        payload = (
            str(int(args[0].value)),
            _handle_value_map_spec(args[1]),
            _encode_bytes(args[2]),
            str(int(args[3].value)),
            str(int(args[4].value)),
        )
        if len(args) >= 7:
            return ("INTERACTION_TSO", *payload, str(float(args[5].value)), str(int(args[6].value)))
        return ("INTERACTION", *payload)
    if method_name == "timeRegulationEnabled":
        return ("TIME_REGULATION_ENABLED", str(float(args[0].value)))
    if method_name == "timeConstrainedEnabled":
        return ("TIME_CONSTRAINED_ENABLED", str(float(args[0].value)))
    if method_name == "timeAdvanceGrant":
        return ("TIME_ADVANCE_GRANT", str(float(args[0].value)))
    if method_name == "announceSynchronizationPoint":
        return ("ANNOUNCE_SYNC_POINT", str(args[0]), _encode_bytes(args[1]))
    if method_name == "federationSynchronized":
        return ("FEDERATION_SYNCHRONIZED", str(args[0]), _federate_handle_set_spec(args[1]))
    if method_name == "attributeOwnershipAcquisitionNotification":
        return ("OWNERSHIP_ACQUIRED", str(int(args[0].value)), _handle_set_spec(args[1]), _encode_bytes(args[2]))
    if method_name == "requestAttributeOwnershipAssumption":
        return (
            "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
            str(int(args[0].value)),
            _handle_set_spec(args[1]),
            _encode_bytes(args[2]),
        )
    if method_name == "informAttributeOwnership":
        return ("INFORM_ATTRIBUTE_OWNERSHIP", str(int(args[0].value)), str(int(args[1].value)), str(int(args[2].value)))
    if method_name == "attributeIsNotOwned":
        return ("ATTRIBUTE_IS_NOT_OWNED", str(int(args[0].value)), str(int(args[1].value)))
    if method_name == "attributeOwnershipUnavailable":
        return ("ATTRIBUTE_OWNERSHIP_UNAVAILABLE", str(int(args[0].value)), _handle_set_spec(args[1]))
    if method_name == "requestAttributeOwnershipRelease":
        return ("REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE", str(int(args[0].value)), _handle_set_spec(args[1]), _encode_bytes(args[2]))
    if method_name == "requestDivestitureConfirmation":
        return ("REQUEST_DIVESTITURE_CONFIRMATION", str(int(args[0].value)), _handle_set_spec(args[1]))
    if method_name == "confirmAttributeOwnershipAcquisitionCancellation":
        return (
            "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION",
            str(int(args[0].value)),
            _handle_set_spec(args[1]),
        )
    return None


@dataclass(frozen=True)
class PythonRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    engine: InMemoryRTIEngine | None = None
    python_config: PythonRTIConfig | None = None


@dataclass(frozen=True)
class CERTIRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    backend_options: Mapping[str, Any] = field(default_factory=dict)


class _RTITransportServicer(pb2_grpc.RTITransportServiceServicer):
    def __init__(self, rti: Any) -> None:
        self.adapter = GrpcTransportClientAdapter()
        self.federate = _CallbackQueueAmbassador()
        self.rti = rti

    def Request(self, request, context):  # noqa: N802 - grpc generated naming
        try:
            transport_request = self.adapter.decode_request(request)
            transport_response = self._handle_request(transport_request)
            return self.adapter.encode_response(transport_response)
        except RTIexception as exc:
            return self.adapter.encode_error(exc.__class__.__name__, str(exc))
        except Exception as exc:  # pragma: no cover - defensive server guard
            return self.adapter.encode_error("RTIinternalError", str(exc))

    def close(self) -> None:
        try:
            self.rti.close()
        except Exception:
            pass

    def _handle_request(self, request: TransportRequest) -> TransportResponse:
        command = request.command
        fields = request.fields

        if command == "GET_HLA_VERSION":
            return TransportResponse(fields=(self.rti.get_hla_version(),))
        if command == "CONNECT":
            callback_model = CallbackModel[str(fields[0])]
            local_settings = str(fields[1]) if len(fields) >= 2 and fields[1] not in {"", None} else None
            self.rti.connect(self.federate, callback_model, local_settings)
            return TransportResponse()
        if command == "DISCONNECT":
            self.rti.disconnect()
            return TransportResponse()
        if command == "CREATE":
            federation_name = str(fields[0])
            logical_time_name = str(fields[1]) if len(fields) >= 2 else ""
            fom_modules = [str(value) for value in fields[2:]]
            self.rti.create_federation_execution(federation_name, fom_modules, logical_time_name or None)
            return TransportResponse()
        if command == "DESTROY":
            self.rti.destroy_federation_execution(str(fields[0]))
            return TransportResponse()
        if command == "JOIN":
            federate_name = str(fields[0]) if fields and fields[0] is not None else ""
            federate_type = str(fields[1])
            federation_name = str(fields[2])
            additional_foms = [str(value) for value in fields[3:]]
            if additional_foms:
                handle = self.rti.join_federation_execution(federate_name, federate_type, federation_name, additional_foms)
            elif federate_name:
                handle = self.rti.join_federation_execution(federate_name, federate_type, federation_name)
            else:
                handle = self.rti.join_federation_execution(federate_type, federation_name)
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "RESIGN":
            self.rti.resign_federation_execution(ResignAction[str(fields[0])])
            return TransportResponse()
        if command == "GET_OBJECT_CLASS_HANDLE":
            return TransportResponse(fields=(str(int(self.rti.get_object_class_handle(str(fields[0])).value)),))
        if command == "GET_ATTRIBUTE_HANDLE":
            handle = self.rti.get_attribute_handle(ObjectClassHandle(int(fields[0])), str(fields[1]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "PUBLISH_OBJECT_CLASS_ATTRIBUTES":
            self.rti.publish_object_class_attributes(
                ObjectClassHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES":
            self.rti.subscribe_object_class_attributes(
                ObjectClassHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "REGISTER_OBJECT_INSTANCE":
            if len(fields) >= 2 and fields[1]:
                handle = self.rti.register_object_instance(ObjectClassHandle(int(fields[0])), str(fields[1]))
            else:
                handle = self.rti.register_object_instance(ObjectClassHandle(int(fields[0])))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_OBJECT_INSTANCE_HANDLE":
            handle = self.rti.get_object_instance_handle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_OBJECT_INSTANCE_NAME":
            return TransportResponse(fields=(self.rti.get_object_instance_name(ObjectInstanceHandle(int(fields[0]))),))
        if command == "GET_KNOWN_OBJECT_CLASS_HANDLE":
            handle = self.rti.get_known_object_class_handle(ObjectInstanceHandle(int(fields[0])))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "UPDATE_ATTRIBUTE_VALUES":
            self.rti.update_attribute_values(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_value_map(str(fields[1]), AttributeHandle, AttributeHandleValueMap),
                _decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP":
            handle = self.rti.update_attribute_values(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_value_map(str(fields[1]), AttributeHandle, AttributeHandleValueMap),
                _decode_bytes(str(fields[2])),
                HLAfloat64Time(float(fields[3])),
            )
            return TransportResponse(fields=(str(int(handle.handle.value)),))
        if command == "GET_INTERACTION_CLASS_HANDLE":
            handle = self.rti.get_interaction_class_handle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_PARAMETER_HANDLE":
            handle = self.rti.get_parameter_handle(InteractionClassHandle(int(fields[0])), str(fields[1]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "PUBLISH_INTERACTION_CLASS":
            self.rti.publish_interaction_class(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "SUBSCRIBE_INTERACTION_CLASS":
            self.rti.subscribe_interaction_class(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "SEND_INTERACTION":
            self.rti.send_interaction(
                InteractionClassHandle(int(fields[0])),
                _decode_handle_value_map(str(fields[1]), ParameterHandle, ParameterHandleValueMap),
                _decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "SEND_INTERACTION_TIMESTAMP":
            handle = self.rti.send_interaction(
                InteractionClassHandle(int(fields[0])),
                _decode_handle_value_map(str(fields[1]), ParameterHandle, ParameterHandleValueMap),
                _decode_bytes(str(fields[2])),
                HLAfloat64Time(float(fields[3])),
            )
            return TransportResponse(fields=(str(int(handle.handle.value)),))
        if command == "ENABLE_TIME_REGULATION":
            self.rti.enable_time_regulation(HLAfloat64Interval(float(fields[0])))
            return TransportResponse()
        if command == "ENABLE_TIME_CONSTRAINED":
            self.rti.enable_time_constrained()
            return TransportResponse()
        if command == "REGISTER_FEDERATION_SYNCHRONIZATION_POINT":
            label = str(fields[0])
            tag = _decode_bytes(str(fields[1]))
            synchronization_set = (
                _decode_handle_set(str(fields[2]), FederateHandle, FederateHandleSet)
                if len(fields) >= 3 and fields[2]
                else None
            )
            if synchronization_set is None:
                self.rti.register_federation_synchronization_point(label, tag)
            else:
                self.rti.register_federation_synchronization_point(label, tag, synchronization_set)
            return TransportResponse()
        if command == "SYNCHRONIZATION_POINT_ACHIEVED":
            label = str(fields[0])
            successful = str(fields[1]) == "1" if len(fields) >= 2 else True
            self.rti.synchronization_point_achieved(label, successful)
            return TransportResponse()
        if command == "UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.unconditional_attribute_ownership_divestiture(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.negotiated_attribute_ownership_divestiture(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                _decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "CONFIRM_DIVESTITURE":
            self.rti.confirm_divestiture(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                _decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_ACQUISITION":
            self.rti.attribute_ownership_acquisition(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                _decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE":
            self.rti.attribute_ownership_acquisition_if_available(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_RELEASE_DENIED":
            self.rti.attribute_ownership_release_denied(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED":
            result = self.rti.attribute_ownership_divestiture_if_wanted(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse(fields=(_handle_set_spec(result),))
        if command == "CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.cancel_negotiated_attribute_ownership_divestiture(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION":
            self.rti.cancel_attribute_ownership_acquisition(
                ObjectInstanceHandle(int(fields[0])),
                _decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "QUERY_ATTRIBUTE_OWNERSHIP":
            self.rti.query_attribute_ownership(ObjectInstanceHandle(int(fields[0])), AttributeHandle(int(fields[1])))
            return TransportResponse()
        if command == "IS_ATTRIBUTE_OWNED_BY_FEDERATE":
            owned = self.rti.is_attribute_owned_by_federate(
                ObjectInstanceHandle(int(fields[0])),
                AttributeHandle(int(fields[1])),
            )
            return TransportResponse(fields=("1" if owned else "0",))
        if command == "TIME_ADVANCE_REQUEST":
            self.rti.time_advance_request(HLAfloat64Time(float(fields[0])))
            return TransportResponse()
        if command == "EVOKE":
            return TransportResponse(fields=self._evoke(single=True, minimum=float(fields[0])))
        if command == "EVOKE_MANY":
            return TransportResponse(fields=self._evoke(single=False, minimum=float(fields[0]), maximum=float(fields[1])))
        if command == "CLOSE":
            self.close()
            return TransportResponse()
        raise ValueError(f"Unknown transport command: {command}")

    def _evoke(self, *, single: bool, minimum: float, maximum: float | None = None) -> tuple[str, ...]:
        if self.federate.pending:
            return ("1", *self.federate.pending.popleft())
        pending_before = len(self.federate.pending)
        if single:
            evoked = self.rti.evoke_callback(minimum)
        else:
            evoked = self.rti.evoke_multiple_callbacks(minimum, maximum if maximum is not None else minimum)
        delivered = len(self.federate.pending) > pending_before
        if delivered and self.federate.pending:
            return ("1", *self.federate.pending.popleft())
        return ("1",) if (delivered or evoked) else ("0",)


class PythonRTIGrpcServer:
    def __init__(self, config: PythonRTIGrpcServerConfig = PythonRTIGrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _RTITransportServicer(rti_ambassador(engine=config.engine, config=config.python_config))
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
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
        self.servicer = _RTITransportServicer(create_rti_ambassador("certi", **dict(config.backend_options)))
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
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


def start_python_rti_grpc_server(
    *,
    engine: InMemoryRTIEngine | None = None,
    python_config: PythonRTIConfig | None = None,
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
    "start_python_rti_grpc_server",
]
