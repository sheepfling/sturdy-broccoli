"""CERTI-backed adapter for backend-neutral real RTI smoke and exchange tests.

This backend keeps the Python-facing RTIambassador surface backend-neutral.
Vendor-specific process control and native handle translation stay behind this
adapter and the small helper binary in ``tools/certi_smoke_helper.cpp``.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from .base import BackendInfo, BackendUnavailableError, Invocation, RTIBackend, UnsupportedBackendService
from ..enums import CallbackModel, OrderType, ResignAction
from ..exceptions import RTIexception, RTIinternalError
from ..fom import normalize_module_uri
from ..handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
    TransportationTypeHandle,
)
from ..real_rti import CERTIRuntime, RuntimeProcess, discover_certi_runtime, launch_certi_rtig, project_root
from ..time import HLAfloat64Time
from ..types import MessageRetractionReturn
from .transport import RTITransport, SubprocessLineTransport, TransportError

HELPER_SOURCE = project_root() / "tools" / "certi_smoke_helper.cpp"
HELPER_OUTPUT = project_root() / "build" / "certi" / "certi_smoke_helper"


def _encode_bytes(value: bytes | bytearray | memoryview) -> str:
    return bytes(value).hex()


def _decode_bytes(value: str) -> bytes:
    return bytes.fromhex(value) if value else b""


def _resolve_certi_module_paths(modules: Any) -> list[str]:
    if isinstance(modules, (str, os.PathLike)):
        values: Sequence[Any] = [modules]
    else:
        values = tuple(modules)

    resolved: list[str] = []
    for value in values:
        _uri, path = normalize_module_uri(value)
        if path is None:
            raise UnsupportedBackendService(f"CERTI backend requires local FOM paths; got {value!r}")
        resolved.append(str(path))
    return resolved


def _handle_set_spec(values: Iterable[AttributeHandle]) -> str:
    return ",".join(str(int(value.value)) for value in values)


def _federate_handle_set_spec(values: Iterable[FederateHandle]) -> str:
    return ",".join(str(int(value.value)) for value in values)


def _handle_value_map_spec(values: Mapping[Any, bytes | bytearray | memoryview]) -> str:
    parts: list[str] = []
    for handle, payload in values.items():
        parts.append(f"{int(handle.value)}:{_encode_bytes(payload)}")
    return ",".join(parts)


def _decode_handle_value_map(spec: str, handle_type: type[Any], map_type: type[Any]) -> Any:
    result = map_type()
    if not spec:
        return result
    for entry in spec.split(","):
        handle_id, value_hex = entry.split(":", 1)
        result[handle_type(int(handle_id))] = _decode_bytes(value_hex)
    return result


def _decode_order(value: str) -> OrderType:
    return OrderType(int(value))


def _decode_handle_set(spec: str, handle_type: type[Any], set_type: type[Any]) -> Any:
    result = set_type()
    if not spec:
        return result
    for entry in spec.split(","):
        if entry:
            result.add(handle_type(int(entry)))
    return result


def _coerce_time_scalar(value: Any) -> float:
    raw = getattr(value, "value", value)
    return float(raw)


def _get_keyword(kwargs: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in kwargs:
            return kwargs[name]
    return default


@dataclass(frozen=True)
class CERTIConfig:
    certi_prefix: str | os.PathLike[str] | None = None
    launch_rtig: bool = True
    host: str = "127.0.0.1"
    tcp_port: int | None = None
    udp_port: int | None = None
    rtig_verbose: int = 0
    helper_path: str | os.PathLike[str] | None = None
    transport: RTITransport | None = None


def build_certi_smoke_helper(runtime: CERTIRuntime, *, output_path: str | os.PathLike[str] | None = None) -> Path:
    compiler = os.environ.get("CXX") or shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        raise BackendUnavailableError("No C++ compiler found for CERTI smoke helper build")

    output = Path(output_path).expanduser().resolve() if output_path is not None else HELPER_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    include_1516e = runtime.prefix / "include" / "ieee1516-2010"
    include_libhla = runtime.prefix / "include" / "libhla"
    lib_dirs = runtime.lib_dirs

    command = [
        compiler,
        "-std=c++11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Wno-deprecated-declarations",
        f"-I{include_1516e}",
        f"-I{include_libhla}",
        str(HELPER_SOURCE),
    ]
    for lib_dir in lib_dirs:
        command.extend((f"-L{lib_dir}", f"-Wl,-rpath,{lib_dir}"))
    command.extend(
        [
            "-lRTI1516ed",
            "-lCERTId",
            "-lFedTime1516ed",
            "-o",
            str(output),
        ]
    )
    subprocess.run(command, check=True, capture_output=True, text=True)
    return output


class CERTIBackend(RTIBackend):
    """Adapter for a real CERTI RTI while preserving the neutral Python RTI API."""

    def __init__(self, config: CERTIConfig = CERTIConfig()) -> None:
        self.config = config
        self.runtime: CERTIRuntime | None = None
        self.rtig_process: RuntimeProcess | None = None
        self.transport: RTITransport | None = config.transport
        self._python_federate_ambassador: Any | None = None
        self.info = BackendInfo(
            name="CERTI",
            kind="native/certi",
            version=None,
            details={"host": config.host, "tcp_port": config.tcp_port},
        )

    def start(self) -> "CERTIBackend":
        if self.config.transport is not None:
            self.transport = self.config.transport.start()
            self.info = BackendInfo(
                name="CERTI",
                kind="native/certi",
                version=None,
                details={"host": self.config.host, "transport": type(self.transport).__name__},
            )
            return self

        self.runtime = discover_certi_runtime(self.config.certi_prefix)
        if self.config.launch_rtig:
            self.rtig_process = launch_certi_rtig(
                certi_prefix=self.config.certi_prefix,
                host=self.config.host,
                tcp_port=self.config.tcp_port,
                udp_port=self.config.udp_port,
                verbose=self.config.rtig_verbose,
            )
            self.info = BackendInfo(
                name="CERTI",
                kind="native/certi",
                version=None,
                details={"host": self.config.host, "tcp_port": self.rtig_process.tcp_port},
            )
        helper_binary = (
            Path(self.config.helper_path).expanduser().resolve()
            if self.config.helper_path is not None
            else build_certi_smoke_helper(self.runtime)
        )
        env = self.runtime.runtime_env()
        env.update(
            {
                "CERTI_HOST": self.config.host,
                "CERTI_TCP_PORT": str(self.rtig_process.tcp_port if self.rtig_process else self.config.tcp_port or 60400),
                "CERTI_UDP_PORT": str(
                    self.config.udp_port
                    or ((self.rtig_process.tcp_port + 100) if self.rtig_process and self.rtig_process.tcp_port else 60500)
                ),
            }
        )
        self.transport = SubprocessLineTransport(command=[str(helper_binary)], env=env, cwd=self.runtime.home).start()
        return self

    def adapt_federate_ambassador(self, ambassador: Any) -> Any:
        self._python_federate_ambassador = ambassador
        return None

    def invoke(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "connect":
                callback_model = invocation.args[1] if len(invocation.args) >= 2 else CallbackModel.HLA_EVOKED
                local_settings = invocation.args[2] if len(invocation.args) >= 3 else ""
                return self._request_value("CONNECT", callback_model.name, local_settings or "")
            case "disconnect":
                return self._request_value("DISCONNECT")
            case "createFederationExecution":
                return self._invoke_create(invocation.args)
            case "destroyFederationExecution":
                return self._request_value("DESTROY", invocation.args[0])
            case "joinFederationExecution":
                return self._invoke_join(invocation.args)
            case "resignFederationExecution":
                action = invocation.args[0] if invocation.args else ResignAction.NO_ACTION
                return self._request_value("RESIGN", action.name if isinstance(action, ResignAction) else action)
            case "getHLAversion":
                return self._request_value("GET_HLA_VERSION")
            case "getFederateHandle":
                return FederateHandle(int(self._request_value("GET_FEDERATE_HANDLE", invocation.args[0])))
            case "getFederateName":
                return self._request_value("GET_FEDERATE_NAME", invocation.args[0].value)
            case "getObjectClassHandle":
                return ObjectClassHandle(int(self._request_value("GET_OBJECT_CLASS_HANDLE", invocation.args[0])))
            case "getObjectClassName":
                return self._request_value("GET_OBJECT_CLASS_NAME", invocation.args[0].value)
            case "getAttributeHandle":
                return AttributeHandle(int(self._request_value("GET_ATTRIBUTE_HANDLE", invocation.args[0].value, invocation.args[1])))
            case "getAttributeName":
                return self._request_value("GET_ATTRIBUTE_NAME", invocation.args[0].value, invocation.args[1].value)
            case "publishObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(
                    invocation.kwargs, "attributeList", "attribute_list", "attributes"
                )
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("publishObjectClassAttributes requires object class and attribute set")
                return self._request_value("PUBLISH_OBJECT_CLASS_ATTRIBUTES", object_class.value, _handle_set_spec(attributes))
            case "subscribeObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(
                    invocation.kwargs, "attributeList", "attribute_list", "attributes"
                )
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("subscribeObjectClassAttributes requires object class and attribute set")
                return self._request_value("SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", object_class.value, _handle_set_spec(attributes))
            case "registerObjectInstance":
                return self._invoke_register_object_instance(invocation.args)
            case "getObjectInstanceHandle":
                return ObjectInstanceHandle(int(self._request_value("GET_OBJECT_INSTANCE_HANDLE", invocation.args[0])))
            case "getObjectInstanceName":
                return self._request_value("GET_OBJECT_INSTANCE_NAME", invocation.args[0].value)
            case "getKnownObjectClassHandle":
                return ObjectClassHandle(int(self._request_value("GET_KNOWN_OBJECT_CLASS_HANDLE", invocation.args[0].value)))
            case "updateAttributeValues":
                if len(invocation.args) >= 4:
                    handle_id = int(self._request_value(
                        "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                        invocation.args[0].value,
                        _handle_value_map_spec(invocation.args[1]),
                        _encode_bytes(invocation.args[2]),
                        _coerce_time_scalar(invocation.args[3]),
                    ))
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), HLAfloat64Time(_coerce_time_scalar(invocation.args[3])))
                return self._request_value(
                    "UPDATE_ATTRIBUTE_VALUES",
                    invocation.args[0].value,
                    _handle_value_map_spec(invocation.args[1]),
                    _encode_bytes(invocation.args[2]),
                )
            case "getInteractionClassHandle":
                return InteractionClassHandle(int(self._request_value("GET_INTERACTION_CLASS_HANDLE", invocation.args[0])))
            case "getInteractionClassName":
                return self._request_value("GET_INTERACTION_CLASS_NAME", invocation.args[0].value)
            case "getParameterHandle":
                return ParameterHandle(int(self._request_value("GET_PARAMETER_HANDLE", invocation.args[0].value, invocation.args[1])))
            case "getParameterName":
                return self._request_value("GET_PARAMETER_NAME", invocation.args[0].value, invocation.args[1].value)
            case "publishInteractionClass":
                return self._request_value("PUBLISH_INTERACTION_CLASS", invocation.args[0].value)
            case "subscribeInteractionClass":
                return self._request_value("SUBSCRIBE_INTERACTION_CLASS", invocation.args[0].value)
            case "sendInteraction":
                if len(invocation.args) >= 4:
                    handle_id = int(self._request_value(
                        "SEND_INTERACTION_TIMESTAMP",
                        invocation.args[0].value,
                        _handle_value_map_spec(invocation.args[1]),
                        _encode_bytes(invocation.args[2]),
                        _coerce_time_scalar(invocation.args[3]),
                    ))
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), HLAfloat64Time(_coerce_time_scalar(invocation.args[3])))
                return self._request_value(
                    "SEND_INTERACTION",
                    invocation.args[0].value,
                    _handle_value_map_spec(invocation.args[1]),
                    _encode_bytes(invocation.args[2]),
                )
            case "enableTimeRegulation":
                return self._request_value("ENABLE_TIME_REGULATION", _coerce_time_scalar(invocation.args[0]))
            case "enableTimeConstrained":
                return self._request_value("ENABLE_TIME_CONSTRAINED")
            case "registerFederationSynchronizationPoint":
                label = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                tag = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(
                    invocation.kwargs,
                    "userSuppliedTag",
                    "theUserSuppliedTag",
                    "tag",
                    default=b"",
                )
                synchronization_set = invocation.args[2] if len(invocation.args) >= 3 else _get_keyword(
                    invocation.kwargs,
                    "synchronizationSet",
                    "synchronization_set",
                    default=None,
                )
                return self._request_value(
                    "REGISTER_FEDERATION_SYNCHRONIZATION_POINT",
                    label,
                    _encode_bytes(tag),
                    "" if synchronization_set is None else _federate_handle_set_spec(synchronization_set),
                )
            case "synchronizationPointAchieved":
                label = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                successful = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(
                    invocation.kwargs,
                    "successIndicator",
                    "successful",
                    "success",
                    default=True,
                )
                return self._request_value("SYNCHRONIZATION_POINT_ACHIEVED", label, "1" if successful else "0")
            case "unconditionalAttributeOwnershipDivestiture":
                return self._request_value(
                    "UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                )
            case "negotiatedAttributeOwnershipDivestiture":
                return self._request_value(
                    "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                    _encode_bytes(invocation.args[2]),
                )
            case "confirmDivestiture":
                return self._request_value(
                    "CONFIRM_DIVESTITURE",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                    _encode_bytes(invocation.args[2]),
                )
            case "attributeOwnershipAcquisition":
                return self._request_value(
                    "ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                    _encode_bytes(invocation.args[2]),
                )
            case "attributeOwnershipAcquisitionIfAvailable":
                return self._request_value(
                    "ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                )
            case "attributeOwnershipReleaseDenied":
                return self._request_value(
                    "ATTRIBUTE_OWNERSHIP_RELEASE_DENIED",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                )
            case "attributeOwnershipDivestitureIfWanted":
                return _decode_handle_set(
                    self._request_value(
                        "ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED",
                        invocation.args[0].value,
                        _handle_set_spec(invocation.args[1]),
                    ),
                    AttributeHandle,
                    AttributeHandleSet,
                )
            case "cancelNegotiatedAttributeOwnershipDivestiture":
                return self._request_value(
                    "CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                )
            case "cancelAttributeOwnershipAcquisition":
                return self._request_value(
                    "CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    invocation.args[0].value,
                    _handle_set_spec(invocation.args[1]),
                )
            case "queryAttributeOwnership":
                return self._request_value("QUERY_ATTRIBUTE_OWNERSHIP", invocation.args[0].value, invocation.args[1].value)
            case "isAttributeOwnedByFederate":
                return self._request_value("IS_ATTRIBUTE_OWNED_BY_FEDERATE", invocation.args[0].value, invocation.args[1].value) == "1"
            case "timeAdvanceRequest":
                return self._request_value("TIME_ADVANCE_REQUEST", _coerce_time_scalar(invocation.args[0]))
            case "evokeCallback":
                return self._invoke_evoke(float(invocation.args[0] if invocation.args else 0.0), multiple=False)
            case "evokeMultipleCallbacks":
                minimum = float(invocation.args[0] if invocation.args else 0.0)
                maximum = float(invocation.args[1] if len(invocation.args) >= 2 else minimum)
                return self._invoke_evoke(minimum, maximum=maximum, multiple=True)
            case _:
                raise UnsupportedBackendService(f"CERTI backend does not implement {invocation.method_name}")

    def _invoke_create(self, args: tuple[Any, ...]) -> None:
        if len(args) < 2:
            raise UnsupportedBackendService("createFederationExecution requires federation name and FOM modules")
        federation_name = args[0]
        fom_modules = _resolve_certi_module_paths(args[1])
        logical_time_name = ""
        if len(args) >= 3 and args[2] is not None:
            logical_time_name = str(args[2])
        if len(args) > 3:
            raise UnsupportedBackendService("CERTI backend does not implement MIM-specific create overloads")
        return self._request_value("CREATE", federation_name, logical_time_name, *fom_modules)

    def _invoke_join(self, args: tuple[Any, ...]) -> FederateHandle:
        if len(args) not in {2, 3, 4}:
            raise UnsupportedBackendService(f"Unsupported joinFederationExecution argument shape: {args!r}")
        federate_name = ""
        additional_foms: Sequence[str] = ()
        if len(args) == 2:
            federate_type, federation_name = args
        elif len(args) == 3:
            federate_name, federate_type, federation_name = args
        else:
            federate_name, federate_type, federation_name, additional_foms_raw = args
            additional_foms = _resolve_certi_module_paths(additional_foms_raw)
        value = self._request_value("JOIN", federate_name, federate_type, federation_name, *additional_foms)
        return FederateHandle(int(value))

    def _invoke_register_object_instance(self, args: tuple[Any, ...]) -> ObjectInstanceHandle:
        if len(args) == 1:
            value = self._request_value("REGISTER_OBJECT_INSTANCE", args[0].value)
            return ObjectInstanceHandle(int(value))
        if len(args) == 2:
            value = self._request_value("REGISTER_OBJECT_INSTANCE", args[0].value, args[1])
            return ObjectInstanceHandle(int(value))
        raise UnsupportedBackendService(f"Unsupported registerObjectInstance argument shape: {args!r}")

    def _invoke_evoke(self, minimum: float, *, maximum: float | None = None, multiple: bool = False) -> bool:
        if multiple:
            parts = self._request_parts("EVOKE_MANY", minimum, maximum if maximum is not None else minimum)
        else:
            parts = self._request_parts("EVOKE", minimum)
        if not parts:
            return False
        evoked = parts[0] == "1"
        if evoked and len(parts) > 1:
            self._dispatch_helper_callback(parts[1:])
        return evoked

    def _dispatch_helper_callback(self, parts: list[str]) -> None:
        ambassador = self._python_federate_ambassador
        if ambassador is None or not parts:
            return

        kind = parts[0]
        if kind == "DISCOVER":
            callback = getattr(ambassador, "discoverObjectInstance")
            callback(ObjectInstanceHandle(int(parts[1])), ObjectClassHandle(int(parts[2])), parts[3])
            return
        if kind == "REFLECT":
            callback = getattr(ambassador, "reflectAttributeValues")
            callback(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
                _decode_bytes(parts[3]),
                _decode_order(parts[4]),
                TransportationTypeHandle(int(parts[5])),
            )
            return
        if kind == "REFLECT_TSO":
            callback = getattr(ambassador, "reflectAttributeValues")
            callback(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
                _decode_bytes(parts[3]),
                _decode_order(parts[4]),
                TransportationTypeHandle(int(parts[5])),
                HLAfloat64Time(float(parts[6])),
                _decode_order(parts[7]),
            )
            return
        if kind == "INTERACTION":
            callback = getattr(ambassador, "receiveInteraction")
            callback(
                InteractionClassHandle(int(parts[1])),
                _decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
                _decode_bytes(parts[3]),
                _decode_order(parts[4]),
                TransportationTypeHandle(int(parts[5])),
            )
            return
        if kind == "INTERACTION_TSO":
            callback = getattr(ambassador, "receiveInteraction")
            callback(
                InteractionClassHandle(int(parts[1])),
                _decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
                _decode_bytes(parts[3]),
                _decode_order(parts[4]),
                TransportationTypeHandle(int(parts[5])),
                HLAfloat64Time(float(parts[6])),
                _decode_order(parts[7]),
            )
            return
        if kind == "TIME_REGULATION_ENABLED":
            getattr(ambassador, "timeRegulationEnabled")(HLAfloat64Time(float(parts[1])))
            return
        if kind == "TIME_CONSTRAINED_ENABLED":
            getattr(ambassador, "timeConstrainedEnabled")(HLAfloat64Time(float(parts[1])))
            return
        if kind == "TIME_ADVANCE_GRANT":
            getattr(ambassador, "timeAdvanceGrant")(HLAfloat64Time(float(parts[1])))
            return
        if kind == "ANNOUNCE_SYNC_POINT":
            getattr(ambassador, "announceSynchronizationPoint")(parts[1], _decode_bytes(parts[2]))
            return
        if kind == "FEDERATION_SYNCHRONIZED":
            getattr(ambassador, "federationSynchronized")(parts[1], _decode_handle_set(parts[2], FederateHandle, FederateHandleSet))
            return
        if kind == "OWNERSHIP_ACQUIRED":
            getattr(ambassador, "attributeOwnershipAcquisitionNotification")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
                _decode_bytes(parts[3]),
            )
            return
        if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION":
            getattr(ambassador, "requestAttributeOwnershipAssumption")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
                _decode_bytes(parts[3]),
            )
            return
        if kind == "INFORM_ATTRIBUTE_OWNERSHIP":
            getattr(ambassador, "informAttributeOwnership")(
                ObjectInstanceHandle(int(parts[1])),
                AttributeHandle(int(parts[2])),
                FederateHandle(int(parts[3])),
            )
            return
        if kind == "ATTRIBUTE_IS_NOT_OWNED":
            getattr(ambassador, "attributeIsNotOwned")(ObjectInstanceHandle(int(parts[1])), AttributeHandle(int(parts[2])))
            return
        if kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE":
            getattr(ambassador, "attributeOwnershipUnavailable")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            )
            return
        if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE":
            getattr(ambassador, "requestAttributeOwnershipRelease")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
                _decode_bytes(parts[3]),
            )
            return
        if kind == "REQUEST_DIVESTITURE_CONFIRMATION":
            getattr(ambassador, "requestDivestitureConfirmation")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            )
            return
        if kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION":
            getattr(ambassador, "confirmAttributeOwnershipAcquisitionCancellation")(
                ObjectInstanceHandle(int(parts[1])),
                _decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            )
            return
        raise RTIinternalError(f"Unknown CERTI helper callback payload: {parts!r}")

    def _request_value(self, command: str, *fields: Any) -> Any:
        parts = self._request_parts(command, *fields)
        if not parts:
            return None
        return parts[0]

    def _request_parts(self, command: str, *fields: Any) -> list[str]:
        transport = self.transport
        if transport is None:
            raise BackendUnavailableError("CERTI transport is not running")

        try:
            return transport.request(command, *fields)
        except TransportError as exc:
            exc_name = exc.code if exc.code else "RTIinternalError"
            message = exc.message or exc_name
            exc_type = getattr(__import__("hla2010.exceptions", fromlist=[exc_name]), exc_name, RTIexception)
            if isinstance(exc_type, type) and issubclass(exc_type, RTIexception):
                raise exc_type(message)
            raise RTIinternalError(message)

    def close(self) -> None:
        self._python_federate_ambassador = None
        if self.transport is not None:
            try:
                try:
                    self._request_value("CLOSE")
                except Exception:
                    pass
            finally:
                self.transport.close()
                self.transport = None
        if self.rtig_process is not None:
            self.rtig_process.terminate()
            self.rtig_process = None


def create_certi_backend(config: CERTIConfig = CERTIConfig()) -> CERTIBackend:
    return CERTIBackend(config)


__all__ = [
    "CERTIBackend",
    "CERTIConfig",
    "build_certi_smoke_helper",
    "create_certi_backend",
]
