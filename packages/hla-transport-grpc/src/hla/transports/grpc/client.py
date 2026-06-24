"""FedPro 2010 protobuf adapter for the gRPC transport."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message

from hla.transports.common import TransportError, TransportRequest, TransportResponse
from hla.transports.common.transport_codecs import decode_bytes

from .fedpro2010 import RTIambassador_pb2 as rti_pb2
from .fedpro2010 import FederateAmbassador_pb2 as callback_pb2
from .fedpro2010 import datatypes_pb2


_COMMAND_REQUESTS: Mapping[str, str] = {
    "ABORT_FEDERATION_RESTORE": "abortFederationRestoreRequest",
    "ABORT_FEDERATION_SAVE": "abortFederationSaveRequest",
    "ASSOCIATE_REGIONS_FOR_UPDATES": "associateRegionsForUpdatesRequest",
    "ATTRIBUTE_OWNERSHIP_ACQUISITION": "attributeOwnershipAcquisitionRequest",
    "ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE": "attributeOwnershipAcquisitionIfAvailableRequest",
    "ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED": "attributeOwnershipDivestitureIfWantedRequest",
    "ATTRIBUTE_OWNERSHIP_RELEASE_DENIED": "attributeOwnershipReleaseDeniedRequest",
    "CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION": "cancelAttributeOwnershipAcquisitionRequest",
    "CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE": "cancelNegotiatedAttributeOwnershipDivestitureRequest",
    "CHANGE_ATTRIBUTE_ORDER_TYPE": "changeAttributeOrderTypeRequest",
    "CHANGE_INTERACTION_ORDER_TYPE": "changeInteractionOrderTypeRequest",
    "COMMIT_REGION_MODIFICATIONS": "commitRegionModificationsRequest",
    "CONFIRM_DIVESTITURE": "confirmDivestitureRequest",
    "CREATE_REGION": "createRegionRequest",
    "DELETE_OBJECT_INSTANCE": "deleteObjectInstanceRequest",
    "DELETE_REGION": "deleteRegionRequest",
    "DESTROY": "destroyFederationExecutionRequest",
    "DISABLE_ASYNCHRONOUS_DELIVERY": "disableAsynchronousDeliveryRequest",
    "DISABLE_CALLBACKS": "disableCallbacksRequest",
    "DISABLE_TIME_CONSTRAINED": "disableTimeConstrainedRequest",
    "DISABLE_TIME_REGULATION": "disableTimeRegulationRequest",
    "DISCONNECT": "disconnectRequest",
    "ENABLE_ASYNCHRONOUS_DELIVERY": "enableAsynchronousDeliveryRequest",
    "ENABLE_CALLBACKS": "enableCallbacksRequest",
    "ENABLE_TIME_CONSTRAINED": "enableTimeConstrainedRequest",
    "ENABLE_TIME_REGULATION": "enableTimeRegulationRequest",
    "FEDERATE_RESTORE_COMPLETE": "federateRestoreCompleteRequest",
    "FEDERATE_RESTORE_NOT_COMPLETE": "federateRestoreNotCompleteRequest",
    "FEDERATE_SAVE_BEGUN": "federateSaveBegunRequest",
    "FEDERATE_SAVE_COMPLETE": "federateSaveCompleteRequest",
    "FEDERATE_SAVE_NOT_COMPLETE": "federateSaveNotCompleteRequest",
    "FLUSH_QUEUE_REQUEST": "flushQueueRequestRequest",
    "GET_ATTRIBUTE_HANDLE": "getAttributeHandleRequest",
    "GET_ATTRIBUTE_NAME": "getAttributeNameRequest",
    "GET_DIMENSION_HANDLE": "getDimensionHandleRequest",
    "GET_FEDERATE_HANDLE": "getFederateHandleRequest",
    "GET_FEDERATE_NAME": "getFederateNameRequest",
    "GET_KNOWN_OBJECT_CLASS_HANDLE": "getKnownObjectClassHandleRequest",
    "GET_OBJECT_CLASS_HANDLE": "getObjectClassHandleRequest",
    "GET_OBJECT_CLASS_NAME": "getObjectClassNameRequest",
    "GET_OBJECT_INSTANCE_HANDLE": "getObjectInstanceHandleRequest",
    "GET_OBJECT_INSTANCE_NAME": "getObjectInstanceNameRequest",
    "IS_ATTRIBUTE_OWNED_BY_FEDERATE": "isAttributeOwnedByFederateRequest",
    "MODIFY_LOOKAHEAD": "modifyLookaheadRequest",
    "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE": "negotiatedAttributeOwnershipDivestitureRequest",
    "NEXT_MESSAGE_REQUEST": "nextMessageRequestRequest",
    "NEXT_MESSAGE_REQUEST_AVAILABLE": "nextMessageRequestAvailableRequest",
    "PUBLISH_OBJECT_CLASS_ATTRIBUTES": "publishObjectClassAttributesRequest",
    "QUERY_ATTRIBUTE_OWNERSHIP": "queryAttributeOwnershipRequest",
    "QUERY_FEDERATION_RESTORE_STATUS": "queryFederationRestoreStatusRequest",
    "QUERY_FEDERATION_SAVE_STATUS": "queryFederationSaveStatusRequest",
    "QUERY_GALT": "queryGALTRequest",
    "QUERY_LITS": "queryLITSRequest",
    "QUERY_LOGICAL_TIME": "queryLogicalTimeRequest",
    "QUERY_LOOKAHEAD": "queryLookaheadRequest",
    "REGISTER_FEDERATION_SYNCHRONIZATION_POINT": "registerFederationSynchronizationPointWithSetRequest",
    "REGISTER_OBJECT_INSTANCE": "registerObjectInstanceWithNameRequest",
    "REGISTER_OBJECT_INSTANCE_WITH_REGIONS": "registerObjectInstanceWithNameAndRegionsRequest",
    "REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS": "requestClassAttributeValueUpdateRequest",
    "REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT": "requestInstanceAttributeValueUpdateRequest",
    "REQUEST_ATTRIBUTE_VALUE_UPDATE_WITH_REGIONS": "requestAttributeValueUpdateWithRegionsRequest",
    "REQUEST_FEDERATION_RESTORE": "requestFederationRestoreRequest",
    "REQUEST_FEDERATION_SAVE": "requestFederationSaveWithTimeRequest",
    "RESIGN": "resignFederationExecutionRequest",
    "RETRACT": "retractRequest",
    "SEND_INTERACTION": "sendInteractionRequest",
    "SEND_INTERACTION_TIMESTAMP": "sendInteractionWithTimeRequest",
    "SEND_INTERACTION_WITH_REGIONS": "sendInteractionWithRegionsRequest",
    "SET_RANGE_BOUNDS": "setRangeBoundsRequest",
    "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES": "subscribeObjectClassAttributesRequest",
    "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS": "subscribeObjectClassAttributesWithRegionsRequest",
    "SYNCHRONIZATION_POINT_ACHIEVED": "synchronizationPointAchievedWithSuccessRequest",
    "TIME_ADVANCE_REQUEST": "timeAdvanceRequestRequest",
    "TIME_ADVANCE_REQUEST_AVAILABLE": "timeAdvanceRequestAvailableRequest",
    "UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE": "unconditionalAttributeOwnershipDivestitureRequest",
    "UNPUBLISH_OBJECT_CLASS_ATTRIBUTES": "unpublishObjectClassAttributesRequest",
    "UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES": "unsubscribeObjectClassAttributesRequest",
    "UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS": "unsubscribeObjectClassAttributesWithRegionsRequest",
    "UPDATE_ATTRIBUTE_VALUES": "updateAttributeValuesRequest",
    "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP": "updateAttributeValuesWithTimeRequest",
}

_REQUEST_COMMANDS = {value: key for key, value in _COMMAND_REQUESTS.items()}
_REQUEST_COMMANDS.update(
    {
        "connectRequest": "CONNECT",
        "connectWithLocalSettingsDesignatorRequest": "CONNECT",
        "createFederationExecutionWithModulesRequest": "CREATE",
        "createFederationExecutionWithModulesAndTimeRequest": "CREATE",
        "joinFederationExecutionRequest": "JOIN",
        "joinFederationExecutionWithModulesRequest": "JOIN",
        "joinFederationExecutionWithNameRequest": "JOIN",
        "joinFederationExecutionWithNameAndModulesRequest": "JOIN",
    }
)


def _connect_request_field(request: TransportRequest) -> str:
    return "connectWithLocalSettingsDesignatorRequest" if len(request.fields) > 1 and request.fields[1] else "connectRequest"


def _create_request_field(request: TransportRequest) -> str:
    return "createFederationExecutionWithModulesAndTimeRequest" if len(request.fields) > 1 else "createFederationExecutionWithModulesRequest"


def _join_request_field(request: TransportRequest) -> str:
    if len(request.fields) >= 4:
        return "joinFederationExecutionWithNameAndModulesRequest"
    if len(request.fields) >= 3 and request.fields[0]:
        return "joinFederationExecutionWithNameRequest"
    if len(request.fields) >= 3:
        return "joinFederationExecutionWithModulesRequest"
    return "joinFederationExecutionRequest"


_SPECIAL_REQUEST_FIELDS = {
    "CONNECT": _connect_request_field,
    "CREATE": _create_request_field,
    "JOIN": _join_request_field,
}

_CALLBACK_POLL_COMMANDS = frozenset({"EVOKE", "EVOKE_MANY"})
_UNSUPPORTED_INTERNAL_COMMANDS = frozenset({"CLOSE", "GET_HLA_VERSION"})
_TYPED_TIME_REQUESTS = frozenset(
    {
        "enableTimeRegulationRequest",
        "modifyLookaheadRequest",
        "timeAdvanceRequestRequest",
        "timeAdvanceRequestAvailableRequest",
        "nextMessageRequestRequest",
        "nextMessageRequestAvailableRequest",
        "flushQueueRequestRequest",
    }
)
_TRAILING_TIME_REQUESTS = frozenset(
    {
        "updateAttributeValuesWithTimeRequest",
        "sendInteractionWithTimeRequest",
        "deleteObjectInstanceWithTimeRequest",
        "sendInteractionWithRegionsAndTimeRequest",
        "requestFederationSaveWithTimeRequest",
    }
)


def _command_to_request_field(command: str) -> str | None:
    parts = command.lower().split("_")
    candidate = parts[0] + "".join(item.title() for item in parts[1:]) + "Request"
    oneof = rti_pb2.CallRequest.DESCRIPTOR.oneofs_by_name["callRequest"]
    return candidate if any(field.name == candidate for field in oneof.fields) else None


def _request_field_to_command(request_field: str) -> str:
    stem = request_field.removesuffix("Request")
    chars: list[str] = []
    for char in stem:
        if char.isupper() and chars:
            chars.append("_")
        chars.append(char.upper())
    return "".join(chars)


def _opaque(value: Any) -> bytes:
    raw = getattr(value, "value", value)
    if isinstance(raw, bytes):
        return raw
    return str(raw).encode("ascii")


def _opaque_text(value: bytes) -> str:
    return value.decode("ascii") if value else "0"


def _enum_number(enum_type: Any, value: Any) -> int:
    name = getattr(value, "name", value)
    if isinstance(name, str):
        return enum_type.values_by_name[name].number
    return int(name)


def _field_values(message: Message, fields: Sequence[Any]) -> list[Any]:
    descriptors = [field for field in message.DESCRIPTOR.fields if not field.is_repeated]
    return list(fields[: len(descriptors)])


def _copy_message_field(target: Message, field: FieldDescriptor, value: Any) -> None:
    message_name = field.message_type.name
    if message_name.endswith("Handle") or message_name == "LogicalTime" or message_name == "LogicalTimeInterval":
        getattr(target, field.name).data = _opaque(value)
        return
    if message_name.endswith("HandleSet"):
        repeated = getattr(getattr(target, field.name), field.message_type.fields[0].name)
        for item in str(value).split(","):
            if item:
                repeated.add(data=_opaque(item))
        return
    if message_name in {"AttributeHandleValueMap", "ParameterHandleValueMap"}:
        repeated_name = field.message_type.fields[0].name
        entry = field.message_type.fields[0].message_type
        handle_field = entry.fields[0].name
        value_field = entry.fields[1].name
        repeated = getattr(getattr(target, field.name), repeated_name)
        for item in str(value).split(","):
            if not item:
                continue
            handle_id, payload = item.split(":", 1)
            row = repeated.add()
            getattr(row, handle_field).data = _opaque(handle_id)
            setattr(row, value_field, decode_bytes(payload))
        return
    if message_name == "FomModule":
        getattr(target, field.name).url = str(value)
        return
    if message_name == "FomModuleSet":
        modules = getattr(target, field.name).fomModule
        for item in value if isinstance(value, (list, tuple)) else str(value).split(","):
            if item:
                modules.add(url=str(item))
        return
    if message_name == "AttributeSetRegionSetPairList":
        return
    if message_name == "RangeBounds":
        bounds = getattr(target, field.name)
        if isinstance(value, str) and ":" in value:
            lower, upper = value.split(":", 1)
            bounds.lower = int(lower)
            bounds.upper = int(upper)
        return
    if message_name == "MessageRetractionReturn":
        result = getattr(target, field.name)
        result.retractionHandleIsValid = bool(str(value))
        result.messageRetractionHandle.data = _opaque(value)
        return
    if message_name == "TimeQueryReturn":
        result = getattr(target, field.name)
        values = tuple(value) if isinstance(value, (list, tuple)) else (value,)
        result.logicalTimeIsValid = bool(values and str(values[0]) == "1")
        if result.logicalTimeIsValid and len(values) >= 3:
            result.logicalTime.data = f"{values[1]}:{values[2]}".encode("ascii")
        return
    getattr(target, field.name).CopyFrom(value)


def _assign_field(message: Message, field: FieldDescriptor, value: Any) -> None:
    if field.type == FieldDescriptor.TYPE_STRING:
        setattr(message, field.name, str(value))
    elif field.type == FieldDescriptor.TYPE_BOOL:
        setattr(message, field.name, str(value).lower() in {"1", "true", "yes"})
    elif field.type in {FieldDescriptor.TYPE_INT32, FieldDescriptor.TYPE_INT64, FieldDescriptor.TYPE_UINT32, FieldDescriptor.TYPE_UINT64}:
        setattr(message, field.name, int(value))
    elif field.type == FieldDescriptor.TYPE_DOUBLE:
        setattr(message, field.name, float(value))
    elif field.type == FieldDescriptor.TYPE_BYTES:
        setattr(message, field.name, decode_bytes(str(value)))
    elif field.type == FieldDescriptor.TYPE_ENUM:
        setattr(message, field.name, _enum_number(field.enum_type, value))
    elif field.type == FieldDescriptor.TYPE_MESSAGE:
        _copy_message_field(message, field, value)


def _build_payload(payload_name: str, fields: Sequence[Any]) -> Message:
    payload_type = getattr(rti_pb2, payload_name[0].upper() + payload_name[1:])
    payload = payload_type()
    values = _field_values(payload, fields)
    for field, value in zip(payload.DESCRIPTOR.fields, values, strict=False):
        _assign_field(payload, field, value)
    return payload


def _request_fields_for_call(request_field: str, fields: Sequence[Any]) -> Sequence[Any]:
    if request_field == "connectRequest":
        return fields[:1]
    if request_field == "connectWithLocalSettingsDesignatorRequest":
        return fields[:2]
    if request_field == "createFederationExecutionWithModulesAndTimeRequest":
        return (fields[0], fields[2:] if len(fields) > 2 else (), fields[1] if len(fields) > 1 else "")
    if request_field == "createFederationExecutionWithModulesRequest":
        return (fields[0], fields[1:] if len(fields) > 1 else ())
    if request_field == "joinFederationExecutionWithModulesRequest":
        return (fields[0], fields[1], fields[2:] if len(fields) > 2 else ())
    if request_field == "requestFederationSaveWithTimeRequest" and len(fields) == 1:
        return fields
    if request_field in _TYPED_TIME_REQUESTS and len(fields) >= 2:
        return (f"{fields[0]}:{fields[1]}",)
    if request_field in _TRAILING_TIME_REQUESTS and len(fields) >= 2:
        return (*fields[:-2], f"{fields[-2]}:{fields[-1]}")
    return fields


def _response_field_name(request_field: str) -> str:
    if not request_field.endswith("Request"):
        raise KeyError(request_field)
    return request_field.removesuffix("Request") + "Response"


def _decode_message_value(value: Any) -> str:
    if hasattr(value, "data"):
        return _opaque_text(value.data)
    return str(value)


def _decode_response_payload(payload: Message) -> tuple[str, ...]:
    result_fields = []
    for field in payload.DESCRIPTOR.fields:
        if field.is_repeated:
            repeated = getattr(payload, field.name)
            result_fields.append(",".join(_decode_message_value(item) for item in repeated))
            continue
        value = getattr(payload, field.name)
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            if field.message_type.name.endswith("HandleSet"):
                repeated = getattr(value, field.message_type.fields[0].name)
                result_fields.append(",".join(_opaque_text(item.data) for item in repeated))
            elif field.message_type.name == "MessageRetractionReturn":
                if value.retractionHandleIsValid:
                    result_fields.append(_opaque_text(value.messageRetractionHandle.data))
            elif field.message_type.name in {"LogicalTime", "LogicalTimeInterval"}:
                result_fields.extend(_decode_logical_time(value))
            elif field.message_type.name == "TimeQueryReturn":
                if value.logicalTimeIsValid:
                    time_type, time_value = _decode_logical_time(value.logicalTime)
                    result_fields.extend(("1", time_type, time_value))
                else:
                    result_fields.append("0")
            else:
                result_fields.append(_decode_message_value(value))
        elif field.type == FieldDescriptor.TYPE_BOOL:
            result_fields.append("1" if value else "0")
        elif field.type == FieldDescriptor.TYPE_ENUM:
            result_fields.append(field.enum_type.values_by_number[int(value)].name)
        else:
            result_fields.append(str(value))
    return tuple(result_fields)


def _decode_request_value(field: FieldDescriptor, value: Any) -> Any:
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        if hasattr(value, "data"):
            return _opaque_text(value.data)
        if field.message_type.name.endswith("HandleSet"):
            repeated = getattr(value, field.message_type.fields[0].name)
            return ",".join(_opaque_text(item.data) for item in repeated)
        if field.message_type.name in {"AttributeHandleValueMap", "ParameterHandleValueMap"}:
            repeated = getattr(value, field.message_type.fields[0].name)
            parts = []
            for item in repeated:
                handle = getattr(item, item.DESCRIPTOR.fields[0].name)
                payload = getattr(item, item.DESCRIPTOR.fields[1].name)
                parts.append(f"{_opaque_text(handle.data)}:{bytes(payload).hex()}")
            return ",".join(parts)
        if field.message_type.name == "FomModuleSet":
            return tuple(item.url or item.file.name for item in value.fomModule)
        if field.message_type.name == "FomModule":
            return value.url or value.file.name
        if field.message_type.name == "RangeBounds":
            return f"{value.lower}:{value.upper}"
        return value
    if field.type == FieldDescriptor.TYPE_BYTES:
        return bytes(value).hex()
    if field.type == FieldDescriptor.TYPE_BOOL:
        return "1" if value else "0"
    if field.type == FieldDescriptor.TYPE_ENUM:
        return field.enum_type.values_by_number[int(value)].name
    return value


def _decode_request_payload(payload: Message) -> tuple[Any, ...]:
    values: list[Any] = []
    for field in payload.DESCRIPTOR.fields:
        if field.is_repeated:
            values.append(tuple(getattr(payload, field.name)))
        else:
            values.append(_decode_request_value(field, getattr(payload, field.name)))
    return tuple(values)


def _decode_handle_value_map(value: Any, repeated_name: str) -> str:
    parts = []
    for item in getattr(value, repeated_name):
        handle = getattr(item, item.DESCRIPTOR.fields[0].name)
        payload = getattr(item, item.DESCRIPTOR.fields[1].name)
        parts.append(f"{_opaque_text(handle.data)}:{bytes(payload).hex()}")
    return ",".join(parts)


def _decode_logical_time(value: Any) -> tuple[str, str]:
    raw = value.data.decode("ascii") if value.data else "HLAfloat64Time:0.0"
    if ":" in raw:
        return tuple(raw.split(":", 1))  # type: ignore[return-value]
    return "HLAfloat64Time", raw


def _enum_wire_number(value: int) -> str:
    return {"RECEIVE": "1", "TIMESTAMP": "2"}.get(datatypes_pb2.OrderType.Name(int(value)), str(int(value)))


def _callback_discover(value: Any) -> tuple[str, ...]:
    return ("DISCOVER", _opaque_text(value.objectInstance.data), _opaque_text(value.objectClass.data), value.objectInstanceName)


def _callback_reflect(value: Any) -> tuple[str, ...]:
    return (
        "REFLECT",
        _opaque_text(value.objectInstance.data),
        _decode_handle_value_map(value.attributeValues, "attributeHandleValue"),
        bytes(value.userSuppliedTag).hex(),
        _enum_wire_number(value.sentOrderType),
        _opaque_text(value.transportationType.data),
    )


def _callback_reflect_tso(value: Any) -> tuple[str, ...]:
    time_type, time_value = _decode_logical_time(value.time)
    return (
        "REFLECT_TSO",
        _opaque_text(value.objectInstance.data),
        _decode_handle_value_map(value.attributeValues, "attributeHandleValue"),
        bytes(value.userSuppliedTag).hex(),
        _enum_wire_number(value.sentOrderType),
        _opaque_text(value.transportationType.data),
        time_type,
        time_value,
        _enum_wire_number(value.receivedOrderType),
    )


def _callback_interaction(value: Any) -> tuple[str, ...]:
    return (
        "INTERACTION",
        _opaque_text(value.interactionClass.data),
        _decode_handle_value_map(value.parameterValues, "parameterHandleValue"),
        bytes(value.userSuppliedTag).hex(),
        _enum_wire_number(value.sentOrderType),
        _opaque_text(value.transportationType.data),
    )


def _callback_interaction_tso(value: Any) -> tuple[str, ...]:
    time_type, time_value = _decode_logical_time(value.time)
    return (
        "INTERACTION_TSO",
        _opaque_text(value.interactionClass.data),
        _decode_handle_value_map(value.parameterValues, "parameterHandleValue"),
        bytes(value.userSuppliedTag).hex(),
        _enum_wire_number(value.sentOrderType),
        _opaque_text(value.transportationType.data),
        time_type,
        time_value,
        _enum_wire_number(value.receivedOrderType),
    )


def _callback_remove(value: Any) -> tuple[str, ...]:
    return (
        "REMOVE_OBJECT_INSTANCE",
        _opaque_text(value.objectInstance.data),
        bytes(value.userSuppliedTag).hex(),
        _enum_wire_number(value.sentOrderType),
        _opaque_text(value.supplementalRemoveInfo.producingFederate.data),
    )


def _callback_time(kind: str):
    def decode(value: Any) -> tuple[str, ...]:
        time_type, time_value = _decode_logical_time(value.time)
        return (kind, time_type, time_value)

    return decode


def _callback_handle(kind: str, field_name: str):
    return lambda value: (kind, _opaque_text(getattr(value, field_name).data))


_CALLBACK_RESPONSE_FIELDS = {
    "discoverObjectInstance": _callback_discover,
    "reflectAttributeValues": _callback_reflect,
    "reflectAttributeValuesWithTime": _callback_reflect_tso,
    "receiveInteraction": _callback_interaction,
    "receiveInteractionWithTime": _callback_interaction_tso,
    "removeObjectInstance": _callback_remove,
    "timeRegulationEnabled": _callback_time("TIME_REGULATION_ENABLED"),
    "timeConstrainedEnabled": _callback_time("TIME_CONSTRAINED_ENABLED"),
    "timeAdvanceGrant": _callback_time("TIME_ADVANCE_GRANT"),
    "requestRetraction": _callback_handle("REQUEST_RETRACTION", "retraction"),
    "startRegistrationForObjectClass": _callback_handle("START_REGISTRATION_FOR_OBJECT_CLASS", "objectClass"),
    "stopRegistrationForObjectClass": _callback_handle("STOP_REGISTRATION_FOR_OBJECT_CLASS", "objectClass"),
    "turnInteractionsOn": _callback_handle("TURN_INTERACTIONS_ON", "interactionClass"),
    "turnInteractionsOff": _callback_handle("TURN_INTERACTIONS_OFF", "interactionClass"),
    "provideAttributeValueUpdate": lambda value: (
        "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.attributes.attributeHandle),
        bytes(value.userSuppliedTag).hex(),
    ),
    "synchronizationPointRegistrationSucceeded": lambda value: ("SYNC_POINT_REGISTRATION_SUCCEEDED", value.synchronizationPointLabel),
    "announceSynchronizationPoint": lambda value: ("ANNOUNCE_SYNC_POINT", value.synchronizationPointLabel, bytes(value.userSuppliedTag).hex()),
    "federationSynchronized": lambda value: (
        "FEDERATION_SYNCHRONIZED",
        value.synchronizationPointLabel,
        ",".join(_opaque_text(item.data) for item in value.failedToSyncSet.federateHandle),
    ),
    "initiateFederateSave": lambda value: ("INITIATE_FEDERATE_SAVE", value.label),
    "federationSaved": lambda value: ("FEDERATION_SAVED",),
    "federationNotSaved": lambda value: ("FEDERATION_NOT_SAVED", datatypes_pb2.SaveFailureReason.Name(value.reason)),
    "federationSaveStatusResponse": lambda value: (
        "FEDERATION_SAVE_STATUS_RESPONSE",
        ";".join(
            f"{_opaque_text(item.federateHandle.data)}:{datatypes_pb2.SaveStatus.Name(item.saveStatus)}"
            for item in value.response.federateHandleSaveStatusPair
        ),
    ),
    "requestFederationRestoreSucceeded": lambda value: ("REQUEST_FEDERATION_RESTORE_SUCCEEDED", value.label),
    "requestFederationRestoreFailed": lambda value: ("REQUEST_FEDERATION_RESTORE_FAILED", value.label),
    "federationRestoreBegun": lambda value: ("FEDERATION_RESTORE_BEGUN",),
    "initiateFederateRestore": lambda value: (
        "INITIATE_FEDERATE_RESTORE",
        value.label,
        value.federateName,
        _opaque_text(value.postRestoreFederateHandle.data),
    ),
    "federationRestored": lambda value: ("FEDERATION_RESTORED",),
    "federationNotRestored": lambda value: ("FEDERATION_NOT_RESTORED", datatypes_pb2.RestoreFailureReason.Name(value.reason)),
    "federationRestoreStatusResponse": lambda value: (
        "FEDERATION_RESTORE_STATUS_RESPONSE",
        ";".join(
            f"{_opaque_text(item.preRestoreHandle.data)}:{_opaque_text(item.postRestoreHandle.data)}:{datatypes_pb2.RestoreStatus.Name(item.restoreStatus)}"
            for item in value.response.federateRestoreStatus
        ),
    ),
    "attributeOwnershipAcquisitionNotification": lambda value: (
        "OWNERSHIP_ACQUIRED",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.securedAttributes.attributeHandle),
        bytes(value.userSuppliedTag).hex(),
    ),
    "requestAttributeOwnershipAssumption": lambda value: (
        "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.offeredAttributes.attributeHandle),
        bytes(value.userSuppliedTag).hex(),
    ),
    "informAttributeOwnership": lambda value: (
        "INFORM_ATTRIBUTE_OWNERSHIP",
        _opaque_text(value.objectInstance.data),
        _opaque_text(value.attribute.data),
        _opaque_text(value.federate.data),
    ),
    "attributeIsNotOwned": lambda value: (
        "ATTRIBUTE_IS_NOT_OWNED",
        _opaque_text(value.objectInstance.data),
        _opaque_text(value.attribute.data),
    ),
    "attributeOwnershipUnavailable": lambda value: (
        "ATTRIBUTE_OWNERSHIP_UNAVAILABLE",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.attributes.attributeHandle),
    ),
    "requestAttributeOwnershipRelease": lambda value: (
        "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.candidateAttributes.attributeHandle),
        bytes(value.userSuppliedTag).hex(),
    ),
    "requestDivestitureConfirmation": lambda value: (
        "REQUEST_DIVESTITURE_CONFIRMATION",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.offeredAttributes.attributeHandle),
    ),
    "confirmAttributeOwnershipAcquisitionCancellation": lambda value: (
        "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION",
        _opaque_text(value.objectInstance.data),
        ",".join(_opaque_text(item.data) for item in value.attributes.attributeHandle),
    ),
}


class FedPro2010ClientAdapter:
    """Map internal backend transport envelopes onto FedPro 2010 protobuf calls."""

    runtime_provider = "python1516e"
    implementation_lane = "hla-backend-python1516e"
    wrapper_only = False
    spec = "rti1516e"
    transport_kind = "grpc"
    route_family = "fedpro"

    def encode_request(self, request: TransportRequest) -> Any:
        request_field = self.request_field_for(request)
        payload = _build_payload(request_field, _request_fields_for_call(request_field, request.fields))
        call = rti_pb2.CallRequest()
        getattr(call, request_field).CopyFrom(payload)
        return call

    def request_field_for(self, request: TransportRequest) -> str:
        special = _SPECIAL_REQUEST_FIELDS.get(request.command)
        if special is not None:
            return special(request)
        if request.command in _UNSUPPORTED_INTERNAL_COMMANDS:
            raise TransportError("UnsupportedTransportCall", f"{request.command} is not in the FedPro 2010 RTIambassador protobuf")
        try:
            return _COMMAND_REQUESTS[request.command]
        except KeyError as exc:
            generated = _command_to_request_field(request.command)
            if generated is not None:
                return generated
            raise TransportError("UnsupportedTransportCall", f"No FedPro 2010 mapping for {request.command}") from exc

    def decode_response(self, request: TransportRequest, response: Any) -> TransportResponse:
        response_kind = response.WhichOneof("callResponse")
        if response_kind == "exceptionData":
            error = response.exceptionData
            raise TransportError(error.exceptionName or "RTIinternalError", error.details or error.exceptionName)
        if response_kind is None:
            return TransportResponse()
        expected = _response_field_name(self.request_field_for(request))
        if response_kind != expected:
            raise TransportError("RTIinternalError", f"Expected {expected}, got {response_kind}")
        return TransportResponse(fields=_decode_response_payload(getattr(response, response_kind)))

    def decode_call_request(self, request: Any) -> TransportRequest:
        request_kind = request.WhichOneof("callRequest")
        if request_kind is None:
            raise TransportError("RTIinternalError", "Empty FedPro 2010 CallRequest")
        try:
            command = _REQUEST_COMMANDS[request_kind]
        except KeyError as exc:
            if request_kind.endswith("Request"):
                command = _request_field_to_command(request_kind)
            else:
                raise TransportError("UnsupportedTransportCall", f"No hosted processor mapping for {request_kind}") from exc
        fields = _decode_request_payload(getattr(request, request_kind))
        if request_kind in _TYPED_TIME_REQUESTS and fields and ":" in str(fields[0]):
            fields = tuple(str(fields[0]).split(":", 1))
        if request_kind in _TRAILING_TIME_REQUESTS and fields and ":" in str(fields[-1]):
            fields = (*fields[:-1], *str(fields[-1]).split(":", 1))
        if request_kind == "createFederationExecutionWithModulesAndTimeRequest":
            modules = fields[1] if len(fields) > 1 else ()
            fields = (fields[0], fields[2], *modules)
        elif request_kind == "createFederationExecutionWithModulesRequest":
            modules = fields[1] if len(fields) > 1 else ()
            fields = (fields[0], "", *modules)
        elif request_kind == "joinFederationExecutionWithModulesRequest":
            modules = fields[2] if len(fields) > 2 else ()
            fields = (None, fields[0], fields[1], *modules)
        return TransportRequest(command=command, fields=tuple(fields))

    def encode_response(self, request: Any, response: TransportResponse) -> Any:
        request_kind = request.WhichOneof("callRequest")
        if request_kind is None:
            return self.encode_error("RTIinternalError", "Empty FedPro 2010 CallRequest")
        response_kind = _response_field_name(request_kind)
        response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
        payload = response_type()
        payload_fields = tuple(payload.DESCRIPTOR.fields)
        if (
            len(payload_fields) == 1
            and payload_fields[0].type == FieldDescriptor.TYPE_MESSAGE
            and payload_fields[0].message_type.name in {"LogicalTime", "LogicalTimeInterval"}
            and len(response.fields) >= 2
        ):
            _assign_field(payload, payload_fields[0], f"{response.fields[0]}:{response.fields[1]}")
        elif (
            len(payload_fields) == 1
            and payload_fields[0].type == FieldDescriptor.TYPE_MESSAGE
            and payload_fields[0].message_type.name == "TimeQueryReturn"
        ):
            _assign_field(payload, payload_fields[0], response.fields)
        else:
            for field, value in zip(payload.DESCRIPTOR.fields, response.fields, strict=False):
                _assign_field(payload, field, value)
        call_response = rti_pb2.CallResponse()
        getattr(call_response, response_kind).CopyFrom(payload)
        return call_response

    def encode_error(self, code: str, message: str) -> Any:
        return rti_pb2.CallResponse(exceptionData=datatypes_pb2.ExceptionData(exceptionName=code, details=message))

    def encode_callback_poll(self) -> Any:
        return callback_pb2.CallbackResponse(callbackSucceeded=callback_pb2.CallbackSucceeded())

    def decode_callback_request(self, request: Any) -> TransportResponse:
        callback_kind = request.WhichOneof("callbackRequest")
        if callback_kind is None:
            return TransportResponse(fields=("0",))
        encoded = _CALLBACK_RESPONSE_FIELDS.get(callback_kind, lambda payload: (callback_kind,))(getattr(request, callback_kind))
        return TransportResponse(fields=("1", *encoded))

    def capability_report(self) -> dict[str, object]:
        return {
            "runtime_provider": self.runtime_provider,
            "implementation_lane": self.implementation_lane,
            "wrapper_only": self.wrapper_only,
            "spec": self.spec,
            "transport_kind": self.transport_kind,
            "route_family": self.route_family,
        }


GrpcTransportClientAdapter = FedPro2010ClientAdapter

__all__ = ["FedPro2010ClientAdapter", "GrpcTransportClientAdapter"]
