"""Transport-hosted RTI backend used for remote Python routes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence, cast

from hla2010 import handles as hla_handles
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import InvalidResignAction, RTIexception, RTIinternalError, resolve_rti_exception_type
from hla2010.fom import normalize_module_uri
from hla2010.handles import (
    AttributeHandle,
    AttributeHandleSet,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    RegionHandleSet,
    TransportationTypeHandle,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time, get_logical_time_factory
from hla2010.types import AttributeRegionAssociation, MessageRetractionReturn, TimeQueryReturn
from hla2010_rti_backend_common import BackendInfo, BackendUnavailableError, Invocation, RTIBackend, UnsupportedBackendService

from .hosted_callbacks import dispatch_hosted_callback
from .transport import RTITransport, TransportError, TransportRequest
from .transport_codecs import decode_handle_set, encode_bytes, federate_handle_set_spec, handle_set_spec, handle_value_map_spec


def _region_handle_set_spec(values: Any) -> str:
    return ",".join(str(int(value.value)) for value in values)


def _decode_region_handle_set(spec: str) -> RegionHandleSet:
    return decode_handle_set(spec, RegionHandle, RegionHandleSet)


def _attribute_region_association_spec(values: Sequence[AttributeRegionAssociation]) -> str:
    parts: list[str] = []
    for value in values:
        parts.append(f"{handle_set_spec(value.attributes)}@{_region_handle_set_spec(value.regions)}")
    return ";".join(parts)


def _normalize_module_values(modules: Any) -> list[str]:
    if isinstance(modules, (str, bytes)):
        values: Sequence[Any] = [modules]
    else:
        values = tuple(modules)
    normalized: list[str] = []
    for value in values:
        uri, path = normalize_module_uri(value)
        normalized.append(str(path) if path is not None else uri)
    return normalized


def _logical_time_name(value: Any) -> str:
    if isinstance(value, HLAinteger64Time):
        return "HLAinteger64Time"
    if isinstance(value, HLAfloat64Time):
        return "HLAfloat64Time"
    return type(value).__name__


def _logical_interval_name(value: Any) -> str:
    if isinstance(value, HLAinteger64Interval):
        return "HLAinteger64Interval"
    if isinstance(value, HLAfloat64Interval):
        return "HLAfloat64Interval"
    return type(value).__name__


def _coerce_time_scalar(value: Any) -> int | float:
    raw = getattr(value, "value", value)
    if isinstance(value, (HLAinteger64Time, HLAinteger64Interval)):
        return int(raw)
    if isinstance(value, (HLAfloat64Time, HLAfloat64Interval)):
        return float(raw)
    if isinstance(raw, int):
        return int(raw)
    return float(raw)


def _decode_logical_time(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Time":
        if str(raw).lower() in {"inf", "+inf", "-inf"}:
            return HLAfloat64Time(float(raw))
        return HLAinteger64Time(int(float(raw)))
    if type_name == "HLAfloat64Time":
        return HLAfloat64Time(float(raw))
    raise RTIinternalError(f"Unsupported logical time type from transport: {type_name}")


def _decode_logical_interval(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Interval":
        return HLAinteger64Interval(int(raw))
    if type_name == "HLAfloat64Interval":
        return HLAfloat64Interval(float(raw))
    raise RTIinternalError(f"Unsupported logical interval type from transport: {type_name}")


def _get_keyword(kwargs: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in kwargs:
            return kwargs[name]
    return default


@dataclass(frozen=True)
class HostedRTIBackendConfig:
    transport: RTITransport
    backend_name: str = "hosted"
    backend_kind: str = "hosted/transport"


class HostedRTIBackend(RTIBackend):
    """Backend-neutral client adapter for transport-hosted RTI servers."""

    def __init__(self, config: HostedRTIBackendConfig) -> None:
        self.config = config
        self.transport = config.transport
        self._python_federate_ambassador: Any | None = None
        self._logical_time_hint: str | None = None
        self.info = BackendInfo(
            name=config.backend_name,
            kind=config.backend_kind,
            details={"transport": type(config.transport).__name__},
        )

    def start(self) -> "HostedRTIBackend":
        self.transport = self.config.transport.start()
        self.info = BackendInfo(
            name=self.config.backend_name,
            kind=self.config.backend_kind,
            details={"transport": type(self.transport).__name__},
        )
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
            self._invoke_support_service,
            self._invoke_callback_service,
        ):
            result = dispatcher(invocation)
            if result is not NotImplemented:
                return result
        raise UnsupportedBackendService(f"Hosted backend does not implement {invocation.method_name}")

    def _invoke_connection_federation_service(self, invocation: Invocation) -> Any:
        args = cast(tuple[Any, ...], invocation.args)
        match invocation.method_name:
            case "connect":
                callback_model = args[1] if len(args) >= 2 else CallbackModel.HLA_EVOKED
                local_settings = args[2] if len(args) >= 3 else ""
                return self._request_value("CONNECT", callback_model.name, local_settings or "")
            case "disconnect":
                return self._request_value("DISCONNECT")
            case "listFederationExecutions":
                return self._request_value("LIST_FEDERATION_EXECUTIONS")
            case "createFederationExecution":
                if len(args) >= 3 and args[2] is not None:
                    self._logical_time_hint = str(args[2])
                return self._request_value("CREATE", args[0], str(args[2]) if len(args) >= 3 and args[2] is not None else "", *_normalize_module_values(args[1]))
            case "createFederationExecutionWithMIM":
                if len(args) >= 3 and args[2] is not None:
                    self._logical_time_hint = str(args[2])
                return self._request_value("CREATE_WITH_MIM", args[0], str(args[2]) if len(args) >= 3 and args[2] is not None else "", *_normalize_module_values(args[1]))
            case "destroyFederationExecution":
                return self._request_value("DESTROY", args[0])
            case "joinFederationExecution":
                return self._invoke_join(args)
            case "resignFederationExecution":
                action = args[0] if args else ResignAction.NO_ACTION
                if isinstance(action, ResignAction):
                    action_name = action.name
                else:
                    action_name = str(action)
                    if action_name not in ResignAction.__members__:
                        raise InvalidResignAction(repr(action))
                return self._request_value("RESIGN", action_name)
            case "requestFederationSave":
                if len(args) >= 2 and args[1] is not None:
                    return self._request_value("REQUEST_FEDERATION_SAVE", args[0], _logical_time_name(args[1]), _coerce_time_scalar(args[1]))
                return self._request_value("REQUEST_FEDERATION_SAVE", args[0])
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
                return self._request_value("REQUEST_FEDERATION_RESTORE", args[0])
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
            case "getDimensionHandle":
                return DimensionHandle(int(self._request_value("GET_DIMENSION_HANDLE", invocation.args[0])))
            case "getAttributeName":
                return self._request_value("GET_ATTRIBUTE_NAME", invocation.args[0].value, invocation.args[1].value)
            case "publishObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(invocation.kwargs, "attributeList", "attribute_list", "attributes")
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("publishObjectClassAttributes requires object class and attribute set")
                return self._request_value("PUBLISH_OBJECT_CLASS_ATTRIBUTES", object_class.value, handle_set_spec(attributes))
            case "unpublishObjectClassAttributes":
                return self._request_value("UNPUBLISH_OBJECT_CLASS_ATTRIBUTES", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "subscribeObjectClassAttributes":
                object_class = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "whichClass", "theClass", "which_class", "the_class")
                attributes = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(invocation.kwargs, "attributeList", "attribute_list", "attributes")
                if object_class is None or attributes is None:
                    raise UnsupportedBackendService("subscribeObjectClassAttributes requires object class and attribute set")
                return self._request_value("SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", object_class.value, handle_set_spec(attributes))
            case "unsubscribeObjectClassAttributes":
                return self._request_value("UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "subscribeObjectClassAttributesWithRegions" | "subscribeObjectClassAttributesPassivelyWithRegions":
                return self._request_value("SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS", invocation.args[0].value, _attribute_region_association_spec(invocation.args[1]))
            case "unsubscribeObjectClassAttributesWithRegions":
                return self._request_value("UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS", invocation.args[0].value, _attribute_region_association_spec(invocation.args[1]))
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
            case "unpublishInteractionClass":
                return self._request_value("UNPUBLISH_INTERACTION_CLASS", invocation.args[0].value)
            case "subscribeInteractionClass":
                return self._request_value("SUBSCRIBE_INTERACTION_CLASS", invocation.args[0].value)
            case "unsubscribeInteractionClass":
                return self._request_value("UNSUBSCRIBE_INTERACTION_CLASS", invocation.args[0].value)
            case "subscribeInteractionClassWithRegions" | "subscribeInteractionClassPassivelyWithRegions":
                return self._request_value("SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", invocation.args[0].value, _region_handle_set_spec(invocation.args[1]))
            case "unsubscribeInteractionClassWithRegions":
                return self._request_value("UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS", invocation.args[0].value, _region_handle_set_spec(invocation.args[1]))
            case _:
                return NotImplemented

    def _invoke_object_and_interaction_service(self, invocation: Invocation) -> Any:
        args = cast(tuple[Any, ...], invocation.args)
        match invocation.method_name:
            case "registerObjectInstance":
                return self._invoke_register_object_instance(args)
            case "createRegion":
                return RegionHandle(int(self._request_value("CREATE_REGION", handle_set_spec(args[0]))))
            case "setRangeBounds":
                return self._request_value("SET_RANGE_BOUNDS", args[0].value, args[1].value, args[2].lower_bound, args[2].upper_bound)
            case "commitRegionModifications":
                return self._request_value("COMMIT_REGION_MODIFICATIONS", _region_handle_set_spec(args[0]))
            case "deleteRegion":
                return self._request_value("DELETE_REGION", args[0].value)
            case "registerObjectInstanceWithRegions":
                object_name = args[2] if len(args) >= 3 else ""
                value = self._request_value("REGISTER_OBJECT_INSTANCE_WITH_REGIONS", args[0].value, _attribute_region_association_spec(args[1]), object_name)
                return ObjectInstanceHandle(int(value))
            case "associateRegionsForUpdates":
                return self._request_value("ASSOCIATE_REGIONS_FOR_UPDATES", args[0].value, _attribute_region_association_spec(args[1]))
            case "unassociateRegionsForUpdates":
                return self._request_value("UNASSOCIATE_REGIONS_FOR_UPDATES", args[0].value, _attribute_region_association_spec(args[1]))
            case "getObjectInstanceHandle":
                return ObjectInstanceHandle(int(self._request_value("GET_OBJECT_INSTANCE_HANDLE", args[0])))
            case "getObjectInstanceName":
                return self._request_value("GET_OBJECT_INSTANCE_NAME", args[0].value)
            case "getKnownObjectClassHandle":
                return ObjectClassHandle(int(self._request_value("GET_KNOWN_OBJECT_CLASS_HANDLE", args[0].value)))
            case "updateAttributeValues":
                if len(args) >= 4:
                    parts = self._request_parts("UPDATE_ATTRIBUTE_VALUES_TIMESTAMP", args[0].value, handle_value_map_spec(args[1]), encode_bytes(args[2]), _logical_time_name(args[3]), _coerce_time_scalar(args[3]))
                    if not parts:
                        return None
                    handle_id = int(parts[0])
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), args[3])
                return self._request_value("UPDATE_ATTRIBUTE_VALUES", args[0].value, handle_value_map_spec(args[1]), encode_bytes(args[2]))
            case "deleteObjectInstance":
                return self._request_value("DELETE_OBJECT_INSTANCE", args[0].value, encode_bytes(args[1]))
            case "requestAttributeValueUpdate":
                command = "REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS" if isinstance(args[0], ObjectClassHandle) else "REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT"
                return self._request_value(command, args[0].value, handle_set_spec(args[1]), encode_bytes(args[2]))
            case "requestAttributeValueUpdateWithRegions":
                return self._request_value("REQUEST_ATTRIBUTE_VALUE_UPDATE_WITH_REGIONS", args[0].value, _attribute_region_association_spec(args[1]), encode_bytes(args[2]))
            case "requestAttributeTransportationTypeChange":
                return self._request_value("REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE", args[0].value, handle_set_spec(args[1]), args[2].value)
            case "queryAttributeTransportationType":
                return self._request_value("QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", args[0].value, args[1].value)
            case "changeAttributeOrderType":
                return self._request_value("CHANGE_ATTRIBUTE_ORDER_TYPE", args[0].value, handle_set_spec(args[1]), args[2].name if isinstance(args[2], OrderType) else args[2])
            case "sendInteraction":
                if len(args) >= 4:
                    parts = self._request_parts("SEND_INTERACTION_TIMESTAMP", args[0].value, handle_value_map_spec(args[1]), encode_bytes(args[2]), _logical_time_name(args[3]), _coerce_time_scalar(args[3]))
                    if not parts:
                        return None
                    handle_id = int(parts[0])
                    return MessageRetractionReturn(MessageRetractionHandle(handle_id), args[3])
                return self._request_value("SEND_INTERACTION", args[0].value, handle_value_map_spec(args[1]), encode_bytes(args[2]))
            case "sendInteractionWithRegions":
                return self._request_value("SEND_INTERACTION_WITH_REGIONS", args[0].value, handle_value_map_spec(args[1]), _region_handle_set_spec(args[2]), encode_bytes(args[3]))
            case "changeInteractionOrderType":
                return self._request_value("CHANGE_INTERACTION_ORDER_TYPE", args[0].value, args[1].name if isinstance(args[1], OrderType) else args[1])
            case "requestInteractionTransportationTypeChange":
                return self._request_value("REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE", args[0].value, args[1].value)
            case "queryInteractionTransportationType":
                if len(args) >= 2:
                    return self._request_value("QUERY_INTERACTION_TRANSPORTATION_TYPE", args[0].value, args[1].value)
                return self._request_value("QUERY_INTERACTION_TRANSPORTATION_TYPE", args[0].value)
            case _:
                return NotImplemented

    def _invoke_time_management_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "enableTimeRegulation":
                self._logical_time_hint = "HLAinteger64Time" if _logical_interval_name(invocation.args[0]) == "HLAinteger64Interval" else "HLAfloat64Time"
                return self._request_value("ENABLE_TIME_REGULATION", _logical_interval_name(invocation.args[0]), _coerce_time_scalar(invocation.args[0]))
            case "enableTimeConstrained":
                return self._request_value("ENABLE_TIME_CONSTRAINED")
            case "disableTimeRegulation":
                return self._request_value("DISABLE_TIME_REGULATION")
            case "disableTimeConstrained":
                return self._request_value("DISABLE_TIME_CONSTRAINED")
            case "queryLogicalTime":
                parts = self._request_parts("QUERY_LOGICAL_TIME")
                return _decode_logical_time(parts[0], parts[1])
            case "queryLookahead":
                parts = self._request_parts("QUERY_LOOKAHEAD")
                return _decode_logical_interval(parts[0], parts[1])
            case "getTimeFactory":
                return get_logical_time_factory(self._logical_time_hint)
            case "modifyLookahead":
                return self._request_value("MODIFY_LOOKAHEAD", _logical_interval_name(invocation.args[0]), _coerce_time_scalar(invocation.args[0]))
            case "enableAsynchronousDelivery":
                return self._request_value("ENABLE_ASYNCHRONOUS_DELIVERY")
            case "disableAsynchronousDelivery":
                return self._request_value("DISABLE_ASYNCHRONOUS_DELIVERY")
            case "timeAdvanceRequest" | "timeAdvanceRequestAvailable" | "nextMessageRequest" | "nextMessageRequestAvailable" | "flushQueueRequest":
                command = {
                    "timeAdvanceRequest": "TIME_ADVANCE_REQUEST",
                    "timeAdvanceRequestAvailable": "TIME_ADVANCE_REQUEST_AVAILABLE",
                    "nextMessageRequest": "NEXT_MESSAGE_REQUEST",
                    "nextMessageRequestAvailable": "NEXT_MESSAGE_REQUEST_AVAILABLE",
                    "flushQueueRequest": "FLUSH_QUEUE_REQUEST",
                }[invocation.method_name]
                self._logical_time_hint = _logical_time_name(invocation.args[0])
                return self._request_value(command, _logical_time_name(invocation.args[0]), _coerce_time_scalar(invocation.args[0]))
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
                label = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                tag = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(invocation.kwargs, "userSuppliedTag", "theUserSuppliedTag", "tag", default=b"")
                synchronization_set = invocation.args[2] if len(invocation.args) >= 3 else _get_keyword(invocation.kwargs, "synchronizationSet", "synchronization_set", default=None)
                return self._request_value("REGISTER_FEDERATION_SYNCHRONIZATION_POINT", label, encode_bytes(tag), "" if synchronization_set is None else federate_handle_set_spec(synchronization_set))
            case "synchronizationPointAchieved":
                label = invocation.args[0] if invocation.args else _get_keyword(invocation.kwargs, "synchronizationPointLabel", "label")
                successful = invocation.args[1] if len(invocation.args) >= 2 else _get_keyword(invocation.kwargs, "successIndicator", "successful", "success", default=True)
                return self._request_value("SYNCHRONIZATION_POINT_ACHIEVED", label, "1" if successful else "0")
            case "unconditionalAttributeOwnershipDivestiture":
                return self._request_value("UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "negotiatedAttributeOwnershipDivestiture":
                return self._request_value("NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]), encode_bytes(invocation.args[2]))
            case "confirmDivestiture":
                return self._request_value("CONFIRM_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]), encode_bytes(invocation.args[2]))
            case "attributeOwnershipAcquisition":
                return self._request_value("ATTRIBUTE_OWNERSHIP_ACQUISITION", invocation.args[0].value, handle_set_spec(invocation.args[1]), encode_bytes(invocation.args[2]))
            case "attributeOwnershipAcquisitionIfAvailable":
                return self._request_value("ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "attributeOwnershipReleaseDenied":
                return self._request_value("ATTRIBUTE_OWNERSHIP_RELEASE_DENIED", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "attributeOwnershipDivestitureIfWanted":
                return decode_handle_set(self._request_value("ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED", invocation.args[0].value, handle_set_spec(invocation.args[1])), AttributeHandle, AttributeHandleSet)
            case "cancelNegotiatedAttributeOwnershipDivestiture":
                return self._request_value("CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "cancelAttributeOwnershipAcquisition":
                return self._request_value("CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION", invocation.args[0].value, handle_set_spec(invocation.args[1]))
            case "queryAttributeOwnership":
                return self._request_value("QUERY_ATTRIBUTE_OWNERSHIP", invocation.args[0].value, invocation.args[1].value)
            case "isAttributeOwnedByFederate":
                return self._request_value("IS_ATTRIBUTE_OWNED_BY_FEDERATE", invocation.args[0].value, invocation.args[1].value) == "1"
            case "normalizeFederateHandle":
                return invocation.args[0]
            case _:
                return NotImplemented

    def _invoke_support_service(self, invocation: Invocation) -> Any:
        match invocation.method_name:
            case "getTransportationTypeHandle" | "getTransportationType":
                value = invocation.args[0] if invocation.args else None
                return TransportationTypeHandle(int(self._request_value("GET_TRANSPORTATION_TYPE_HANDLE", value)))
            case "getTransportationTypeName" | "getTransportationName":
                return self._request_value("GET_TRANSPORTATION_TYPE_NAME", invocation.args[0].value)
            case "getOrderName":
                return cast(OrderType, invocation.args[0]).name
            case "getOrderType":
                normalized = str(invocation.args[0]).replace("HLA", "").replace("_", "").replace(" ", "").upper()
                if normalized in {"RECEIVE", "RECEIVEORDER"}:
                    return OrderType.RECEIVE
                if normalized in {"TIMESTAMP", "TIMESTAMPORDER", "TSO"}:
                    return OrderType.TIMESTAMP
                raise RTIinternalError(f"Unsupported order type name: {invocation.args[0]}")
            case "getAttributeHandleFactory":
                return hla_handles.AttributeHandleFactory()
            case "getAttributeHandleSetFactory":
                return hla_handles.AttributeHandleSetFactory()
            case "getAttributeHandleValueMapFactory":
                return hla_handles.AttributeHandleValueMapFactory()
            case "getAttributeSetRegionSetPairListFactory":
                return hla_handles.AttributeSetRegionSetPairListFactory()
            case "getDimensionHandleFactory":
                return hla_handles.DimensionHandleFactory()
            case "getDimensionHandleSetFactory":
                return hla_handles.DimensionHandleSetFactory()
            case "getFederateHandleFactory":
                return hla_handles.FederateHandleFactory()
            case "getFederateHandleSetFactory":
                return hla_handles.FederateHandleSetFactory()
            case "getInteractionClassHandleFactory":
                return hla_handles.InteractionClassHandleFactory()
            case "getObjectClassHandleFactory":
                return hla_handles.ObjectClassHandleFactory()
            case "getObjectInstanceHandleFactory":
                return hla_handles.ObjectInstanceHandleFactory()
            case "getParameterHandleFactory":
                return hla_handles.ParameterHandleFactory()
            case "getParameterHandleValueMapFactory":
                return hla_handles.ParameterHandleValueMapFactory()
            case "getRegionHandleSetFactory":
                return hla_handles.RegionHandleSetFactory()
            case "getTransportationTypeHandleFactory":
                return hla_handles.TransportationTypeHandleFactory()
            case "decodeFederateHandle":
                return FederateHandle.decode(invocation.args[0])
            case "decodeObjectClassHandle":
                return ObjectClassHandle.decode(invocation.args[0])
            case "decodeInteractionClassHandle":
                return InteractionClassHandle.decode(invocation.args[0])
            case "decodeObjectInstanceHandle":
                return ObjectInstanceHandle.decode(invocation.args[0])
            case "decodeAttributeHandle":
                return AttributeHandle.decode(invocation.args[0])
            case "decodeParameterHandle":
                return ParameterHandle.decode(invocation.args[0])
            case "decodeDimensionHandle":
                return DimensionHandle.decode(invocation.args[0])
            case "decodeMessageRetractionHandle":
                return MessageRetractionHandle.decode(invocation.args[0])
            case "decodeRegionHandle":
                return RegionHandle.decode(invocation.args[0])
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
            additional_foms = _normalize_module_values(additional_foms_raw)
        value = self._request_value("JOIN", federate_name, federate_type, federation_name, *additional_foms)
        return FederateHandle(int(value))

    def _invoke_register_object_instance(self, args: tuple[Any, ...]) -> ObjectInstanceHandle:
        if len(args) == 1:
            return ObjectInstanceHandle(int(self._request_value("REGISTER_OBJECT_INSTANCE", args[0].value)))
        if len(args) == 2:
            return ObjectInstanceHandle(int(self._request_value("REGISTER_OBJECT_INSTANCE", args[0].value, args[1])))
        raise UnsupportedBackendService(f"Unsupported registerObjectInstance argument shape: {args!r}")

    def _decode_time_query_return(self, parts: list[str]) -> TimeQueryReturn:
        valid = bool(parts) and parts[0] == "1"
        if not valid:
            return TimeQueryReturn(False, None)
        type_name = self._logical_time_hint or parts[1]
        return TimeQueryReturn(True, _decode_logical_time(type_name, parts[2]))

    def _invoke_evoke(self, minimum: float, *, maximum: float | None = None, multiple: bool = False) -> bool:
        parts = self._request_parts("EVOKE_MANY", minimum, maximum if maximum is not None else minimum) if multiple else self._request_parts("EVOKE", minimum)
        if not parts:
            return False
        evoked = parts[0] == "1"
        if evoked and len(parts) > 1:
            dispatch_hosted_callback(self._python_federate_ambassador, parts[1:], logical_time_hint=self._logical_time_hint)
        return evoked

    def _request_value(self, command: str, *fields: Any) -> str | None:
        parts = self._request_parts(command, *fields)
        if not parts:
            return None
        return parts[0]

    def _request_parts(self, command: str, *fields: Any, timeout: float | None = None) -> list[str]:
        transport = self.transport
        if transport is None:
            raise BackendUnavailableError("Hosted transport is not running")
        try:
            metadata = {"timeout": timeout} if timeout is not None else {}
            response = transport.request(TransportRequest(command=command, fields=tuple(fields), metadata=metadata))
            return [str(field) for field in response.fields]
        except TransportError as exc:
            exc_name = exc.code if exc.code else "RTIinternalError"
            message = exc.message or exc_name
            raise resolve_rti_exception_type(exc_name)(message)

    def close(self) -> None:
        if self.transport is not None:
            self.transport.close()

    def translate_exception(self, exc: BaseException, invocation: Invocation) -> RTIexception:
        if isinstance(exc, RTIexception):
            return exc
        return RTIinternalError(f"{self.__class__.__name__} failed during {invocation.method_name}: {exc}", cause=exc)


__all__ = ["HostedRTIBackend", "HostedRTIBackendConfig"]
