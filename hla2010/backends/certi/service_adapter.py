"""CERTI-backed adapter for backend-neutral real RTI smoke and exchange tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ...enums import CallbackModel, OrderType, ResignAction
from ...exceptions import RTIexception, RTIinternalError
from ...handles import (
    AttributeHandle,
    AttributeHandleSet,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
)
from ...real_rti import CERTIRuntime, RuntimeProcess, discover_certi_runtime, launch_certi_rtig
from ...types import MessageRetractionReturn, TimeQueryReturn
from ..base import BackendInfo, BackendUnavailableError, Invocation, RTIBackend, UnsupportedBackendService
from ..transport import RTITransport, SubprocessLineTransport, TransportError, TransportRequest
from .callbacks import dispatch_helper_callback
from .codecs import (
    decode_handle_set,
    encode_bytes,
    federate_handle_set_spec,
    handle_set_spec,
    handle_value_map_spec,
)
from .runtime import (
    HELPER_SOURCE,
    CERTIConfig,
    build_certi_smoke_helper,
    coerce_time_scalar,
    decode_logical_interval,
    decode_logical_time,
    get_keyword,
    logical_interval_name,
    logical_time_name,
    resolve_certi_module_paths,
)

_FEDERATION_LOGICAL_TIME_HINTS: dict[str, str] = {}


class CERTIBackend(RTIBackend):
    """Adapter for a real CERTI RTI while preserving the neutral Python RTI API."""

    def __init__(self, config: CERTIConfig = CERTIConfig()) -> None:
        self.config = config
        self.runtime: CERTIRuntime | None = None
        self.rtig_process: RuntimeProcess | None = None
        self.transport: RTITransport | None = config.transport
        self._python_federate_ambassador: Any | None = None
        self._logical_time_hint: str | None = None
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

        self.runtime = discover_certi_runtime(
            self.config.certi_prefix,
            certi_build_root=self.config.certi_build_root,
            allow_repo_build_overlay=self.config.allow_repo_build_overlay,
        )
        if self.config.launch_rtig:
            self.rtig_process = launch_certi_rtig(
                certi_prefix=self.config.certi_prefix,
                certi_build_root=self.config.certi_build_root,
                allow_repo_build_overlay=self.config.allow_repo_build_overlay,
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
        helper_binary = Path(self.config.helper_path).expanduser().resolve() if self.config.helper_path is not None else build_certi_smoke_helper(self.runtime)
        if self.config.helper_path is not None:
            if (not helper_binary.exists()) or (helper_binary.stat().st_mtime < HELPER_SOURCE.stat().st_mtime):
                helper_binary = build_certi_smoke_helper(self.runtime, output_path=helper_binary)
        env = self.runtime.runtime_env()
        env.update(
            {
                "CERTI_HOST": self.config.host,
                "CERTI_TCP_PORT": str(self.rtig_process.tcp_port if self.rtig_process else self.config.tcp_port or 60400),
                "CERTI_UDP_PORT": str(
                    self.config.udp_port or ((self.rtig_process.tcp_port + 100) if self.rtig_process and self.rtig_process.tcp_port else 60500)
                ),
            }
        )
        self.transport = SubprocessLineTransport(
            command=[str(helper_binary)],
            env=env,
            cwd=self.runtime.home,
            default_timeout=self.config.helper_request_timeout,
        ).start()
        return self

    def adapt_federate_ambassador(self, ambassador: Any) -> Any:
        self._python_federate_ambassador = ambassador
        return None

    def invoke(self, invocation: Invocation) -> Any:
        for dispatcher in (
            self._invoke_connection_federation_service,
            self._invoke_name_and_declaration_service,
            self._invoke_object_and_interaction_service,
            self._invoke_time_management_service,
            self._invoke_sync_and_ownership_service,
            self._invoke_callback_service,
        ):
            result = dispatcher(invocation)
            if result is not NotImplemented:
                return result
        raise UnsupportedBackendService(f"CERTI backend does not implement {invocation.method_name}")

    def _invoke_connection_federation_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "connect":
                callback_model = invocation.args[1] if len(invocation.args) >= 2 else CallbackModel.HLA_EVOKED
                local_settings = invocation.args[2] if len(invocation.args) >= 3 else ""
                return self._request_value("CONNECT", callback_model.name, local_settings or "")
            case "disconnect":
                return self._request_value("DISCONNECT")
            case "createFederationExecution":
                if len(invocation.args) >= 3 and invocation.args[2] is not None:
                    self._logical_time_hint = str(invocation.args[2])
                    _FEDERATION_LOGICAL_TIME_HINTS[str(invocation.args[0])] = self._logical_time_hint
                return self._invoke_create(invocation.args)
            case "destroyFederationExecution":
                _FEDERATION_LOGICAL_TIME_HINTS.pop(str(invocation.args[0]), None)
                return self._request_value("DESTROY", invocation.args[0])
            case "joinFederationExecution":
                return self._invoke_join(invocation.args)
            case "resignFederationExecution":
                action = invocation.args[0] if invocation.args else ResignAction.NO_ACTION
                return self._request_value("RESIGN", action.name if isinstance(action, ResignAction) else action)
            case "requestFederationSave":
                if len(invocation.args) >= 2 and invocation.args[1] is not None:
                    return self._request_value(
                        "REQUEST_FEDERATION_SAVE",
                        invocation.args[0],
                        logical_time_name(invocation.args[1]),
                        coerce_time_scalar(invocation.args[1]),
                    )
                return self._request_value("REQUEST_FEDERATION_SAVE", invocation.args[0])
            case "federateSaveBegun":
                return self._request_value("FEDERATE_SAVE_BEGUN")
            case "federateSaveComplete":
                return self._request_value("FEDERATE_SAVE_COMPLETE")
            case "federateSaveNotComplete":
                return self._request_value("FEDERATE_SAVE_NOT_COMPLETE")
            case "abortFederationSave":
                return self._request_value("ABORT_FEDERATION_SAVE")
            case "queryFederationSaveStatus":
                return self._request_value("QUERY_FEDERATION_SAVE_STATUS")
            case "requestFederationRestore":
                return self._request_value("REQUEST_FEDERATION_RESTORE", invocation.args[0])
            case "federateRestoreComplete":
                return self._request_value("FEDERATE_RESTORE_COMPLETE")
            case "federateRestoreNotComplete":
                return self._request_value("FEDERATE_RESTORE_NOT_COMPLETE")
            case "abortFederationRestore":
                return self._request_value("ABORT_FEDERATION_RESTORE")
            case "queryFederationRestoreStatus":
                return self._request_value("QUERY_FEDERATION_RESTORE_STATUS")
            case "getHLAversion":
                return self._request_value("GET_HLA_VERSION")
            case "getFederateHandle":
                return FederateHandle(int(self._request_value("GET_FEDERATE_HANDLE", invocation.args[0])))
            case "getFederateName":
                return self._request_value("GET_FEDERATE_NAME", invocation.args[0].value)
            case _:
                return NotImplemented

    def _invoke_name_and_declaration_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "getObjectClassHandle":
                return ObjectClassHandle(int(self._request_value("GET_OBJECT_CLASS_HANDLE", invocation.args[0])))
            case "getObjectClassName":
                return self._request_value("GET_OBJECT_CLASS_NAME", invocation.args[0].value)
            case "getAttributeHandle":
                return AttributeHandle(int(self._request_value("GET_ATTRIBUTE_HANDLE", invocation.args[0].value, invocation.args[1])))
            case "getAttributeName":
                return self._request_value("GET_ATTRIBUTE_NAME", invocation.args[0].value, invocation.args[1].value)
            case "publishObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = (
                    invocation.args[1] if len(invocation.args) >= 2 else get_keyword(invocation.kwargs, "attributeList", "attribute_list", "attributes")
                )
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("publishObjectClassAttributes requires object class and attribute set")
                return self._request_value("PUBLISH_OBJECT_CLASS_ATTRIBUTES", object_class.value, handle_set_spec(attributes))
            case "subscribeObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = (
                    invocation.args[1] if len(invocation.args) >= 2 else get_keyword(invocation.kwargs, "attributeList", "attribute_list", "attributes")
                )
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("subscribeObjectClassAttributes requires object class and attribute set")
                return self._request_value("SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", object_class.value, handle_set_spec(attributes))
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
            case _:
                return NotImplemented

    def _invoke_object_and_interaction_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
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
                    parts = self._request_parts(
                        "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                        invocation.args[0].value,
                        handle_value_map_spec(invocation.args[1]),
                        encode_bytes(invocation.args[2]),
                        logical_time_name(invocation.args[3]),
                        coerce_time_scalar(invocation.args[3]),
                    )
                    if not parts:
                        return None
                    handle_id = int(parts[0])
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), invocation.args[3])
                return self._request_value(
                    "UPDATE_ATTRIBUTE_VALUES",
                    invocation.args[0].value,
                    handle_value_map_spec(invocation.args[1]),
                    encode_bytes(invocation.args[2]),
                )
            case "changeAttributeOrderType":
                return self._request_value(
                    "CHANGE_ATTRIBUTE_ORDER_TYPE",
                    invocation.args[0].value,
                    handle_set_spec(invocation.args[1]),
                    invocation.args[2].name if isinstance(invocation.args[2], OrderType) else invocation.args[2],
                )
            case "sendInteraction":
                if len(invocation.args) >= 4:
                    parts = self._request_parts(
                        "SEND_INTERACTION_TIMESTAMP",
                        invocation.args[0].value,
                        handle_value_map_spec(invocation.args[1]),
                        encode_bytes(invocation.args[2]),
                        logical_time_name(invocation.args[3]),
                        coerce_time_scalar(invocation.args[3]),
                    )
                    if not parts:
                        return None
                    handle_id = int(parts[0])
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), invocation.args[3])
                return self._request_value(
                    "SEND_INTERACTION",
                    invocation.args[0].value,
                    handle_value_map_spec(invocation.args[1]),
                    encode_bytes(invocation.args[2]),
                )
            case "changeInteractionOrderType":
                return self._request_value(
                    "CHANGE_INTERACTION_ORDER_TYPE",
                    invocation.args[0].value,
                    invocation.args[1].name if isinstance(invocation.args[1], OrderType) else invocation.args[1],
                )
            case _:
                return NotImplemented

    def _invoke_time_management_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "enableTimeRegulation":
                self._logical_time_hint = "HLAinteger64Time" if logical_interval_name(invocation.args[0]) == "HLAinteger64Interval" else "HLAfloat64Time"
                return self._request_value(
                    "ENABLE_TIME_REGULATION",
                    logical_interval_name(invocation.args[0]),
                    coerce_time_scalar(invocation.args[0]),
                )
            case "enableTimeConstrained":
                return self._request_value("ENABLE_TIME_CONSTRAINED")
            case "disableTimeRegulation":
                return self._request_value("DISABLE_TIME_REGULATION")
            case "disableTimeConstrained":
                return self._request_value("DISABLE_TIME_CONSTRAINED")
            case "queryLogicalTime":
                parts = self._request_parts("QUERY_LOGICAL_TIME")
                return decode_logical_time(parts[0], parts[1])
            case "queryLookahead":
                parts = self._request_parts("QUERY_LOOKAHEAD")
                return decode_logical_interval(parts[0], parts[1])
            case "modifyLookahead":
                return self._request_value(
                    "MODIFY_LOOKAHEAD",
                    logical_interval_name(invocation.args[0]),
                    coerce_time_scalar(invocation.args[0]),
                )
            case "enableAsynchronousDelivery":
                return self._request_value("ENABLE_ASYNCHRONOUS_DELIVERY")
            case "disableAsynchronousDelivery":
                return self._request_value("DISABLE_ASYNCHRONOUS_DELIVERY")
            case "timeAdvanceRequest":
                self._logical_time_hint = logical_time_name(invocation.args[0])
                return self._request_value("TIME_ADVANCE_REQUEST", logical_time_name(invocation.args[0]), coerce_time_scalar(invocation.args[0]))
            case "timeAdvanceRequestAvailable":
                self._logical_time_hint = logical_time_name(invocation.args[0])
                return self._request_value("TIME_ADVANCE_REQUEST_AVAILABLE", logical_time_name(invocation.args[0]), coerce_time_scalar(invocation.args[0]))
            case "nextMessageRequest":
                self._logical_time_hint = logical_time_name(invocation.args[0])
                return self._request_value("NEXT_MESSAGE_REQUEST", logical_time_name(invocation.args[0]), coerce_time_scalar(invocation.args[0]))
            case "nextMessageRequestAvailable":
                self._logical_time_hint = logical_time_name(invocation.args[0])
                return self._request_value("NEXT_MESSAGE_REQUEST_AVAILABLE", logical_time_name(invocation.args[0]), coerce_time_scalar(invocation.args[0]))
            case "flushQueueRequest":
                self._logical_time_hint = logical_time_name(invocation.args[0])
                return self._request_value("FLUSH_QUEUE_REQUEST", logical_time_name(invocation.args[0]), coerce_time_scalar(invocation.args[0]))
            case "queryGALT":
                return self._decode_time_query_return(self._request_parts("QUERY_GALT"))
            case "queryLITS":
                return self._decode_time_query_return(self._request_parts("QUERY_LITS"))
            case "retract":
                return self._request_value("RETRACT", invocation.args[0].value)
            case _:
                return NotImplemented

    def _invoke_sync_and_ownership_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "registerFederationSynchronizationPoint":
                label = invocation.args[0] if invocation.args else get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                tag = (
                    invocation.args[1]
                    if len(invocation.args) >= 2
                    else get_keyword(invocation.kwargs, "userSuppliedTag", "theUserSuppliedTag", "tag", default=b"")
                )
                synchronization_set = (
                    invocation.args[2]
                    if len(invocation.args) >= 3
                    else get_keyword(invocation.kwargs, "synchronizationSet", "synchronization_set", default=None)
                )
                return self._request_value(
                    "REGISTER_FEDERATION_SYNCHRONIZATION_POINT",
                    label,
                    encode_bytes(tag),
                    "" if synchronization_set is None else federate_handle_set_spec(synchronization_set),
                )
            case "synchronizationPointAchieved":
                label = invocation.args[0] if invocation.args else get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                successful = (
                    invocation.args[1]
                    if len(invocation.args) >= 2
                    else get_keyword(invocation.kwargs, "successIndicator", "successful", "success", default=True)
                )
                return self._request_value("SYNCHRONIZATION_POINT_ACHIEVED", label, "1" if successful else "0")
            case "unconditionalAttributeOwnershipDivestiture":
                return self._request_value("UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "negotiatedAttributeOwnershipDivestiture":
                return self._request_value(
                    "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    invocation.args[0].value,
                    handle_set_spec(invocation.args[1]),
                    encode_bytes(invocation.args[2]),
                )
            case "confirmDivestiture":
                return self._request_value(
                    "CONFIRM_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]), encode_bytes(invocation.args[2])
                )
            case "attributeOwnershipAcquisition":
                return self._request_value(
                    "ATTRIBUTE_OWNERSHIP_ACQUISITION", invocation.args[0].value, handle_set_spec(invocation.args[1]), encode_bytes(invocation.args[2])
                )
            case "attributeOwnershipAcquisitionIfAvailable":
                return self._request_value("ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "attributeOwnershipReleaseDenied":
                return self._request_value("ATTRIBUTE_OWNERSHIP_RELEASE_DENIED", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "attributeOwnershipDivestitureIfWanted":
                return decode_handle_set(
                    self._request_value("ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED", invocation.args[0].value, handle_set_spec(invocation.args[1])),
                    AttributeHandle,
                    AttributeHandleSet,
                )
            case "cancelNegotiatedAttributeOwnershipDivestiture":
                return self._request_value("CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "cancelAttributeOwnershipAcquisition":
                return self._request_value("CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "queryAttributeOwnership":
                return self._request_value("QUERY_ATTRIBUTE_OWNERSHIP", invocation.args[0].value, invocation.args[1].value)
            case "isAttributeOwnedByFederate":
                return self._request_value("IS_ATTRIBUTE_OWNED_BY_FEDERATE", invocation.args[0].value, invocation.args[1].value) == "1"
            case _:
                return NotImplemented

    def _invoke_callback_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "evokeCallback":
                return self._invoke_evoke(float(invocation.args[0] if invocation.args else 0.0), multiple=False)
            case "evokeMultipleCallbacks":
                minimum = float(invocation.args[0] if invocation.args else 0.0)
                maximum = float(invocation.args[1] if len(invocation.args) >= 2 else minimum)
                return self._invoke_evoke(minimum, maximum=maximum, multiple=True)
            case _:
                return NotImplemented

    def _invoke_create(self, args: tuple[Any, ...]) -> None:
        if len(args) < 2:
            raise UnsupportedBackendService("createFederationExecution requires federation name and FOM modules")
        federation_name = args[0]
        fom_modules = resolve_certi_module_paths(args[1])
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
            additional_foms = resolve_certi_module_paths(additional_foms_raw)
        self._logical_time_hint = _FEDERATION_LOGICAL_TIME_HINTS.get(str(federation_name), self._logical_time_hint)
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

    def _decode_time_query_return(self, parts: list[str]) -> TimeQueryReturn:
        valid = bool(parts) and parts[0] == "1"
        if not valid:
            return TimeQueryReturn(False, None)
        type_name = self._logical_time_hint or parts[1]
        return TimeQueryReturn(True, decode_logical_time(type_name, parts[2]))

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
        dispatch_helper_callback(
            self._python_federate_ambassador,
            parts,
            logical_time_hint=self._logical_time_hint,
        )

    def _request_value(self, command: str, *fields: Any) -> Any:
        parts = self._request_parts(command, *fields)
        if not parts:
            return None
        return parts[0]

    def helper_request(self, command: str, *fields: Any, timeout: float | None = None) -> list[str]:
        if (
            command
            in {
                "TIME_ADVANCE_REQUEST",
                "TIME_ADVANCE_REQUEST_AVAILABLE",
                "NEXT_MESSAGE_REQUEST",
                "NEXT_MESSAGE_REQUEST_AVAILABLE",
                "FLUSH_QUEUE_REQUEST",
            }
            and fields
        ):
            self._logical_time_hint = str(fields[0])
        return self._request_parts(command, *fields, timeout=timeout)

    def _request_parts(self, command: str, *fields: Any, timeout: float | None = None) -> list[str]:
        transport = self.transport
        if transport is None:
            raise BackendUnavailableError("CERTI transport is not running")

        try:
            metadata = {"timeout": timeout} if timeout is not None else {}
            response = transport.request(TransportRequest(command=command, fields=tuple(fields), metadata=metadata))
            return [str(field) for field in response.fields]
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
