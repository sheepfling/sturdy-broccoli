"""Shared hosted RTI transport request processing."""
from __future__ import annotations

from collections import deque
from typing import Any, Sequence, cast

from .transport_codecs import (
    decode_bytes,
    decode_handle_set,
    decode_handle_value_map,
    encode_bytes,
    federate_handle_set_spec,
    handle_set_spec,
    handle_value_map_spec,
)

from .transport import TransportRequest, TransportResponse
from hla2010.enums import (
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    SaveFailureReason,
    SynchronizationPointFailureReason,
)
from hla2010.exceptions import InvalidResignAction
from hla2010.handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    DimensionHandle,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
    RegionHandle,
    RegionHandleSet,
    TransportationTypeHandle,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla2010.types import (
    AttributeRegionAssociation,
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformationSet,
    RangeBounds,
)
from hla2010_rti_backend_common import RecordingFederateAmbassador


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


def _logical_scalar(value: Any) -> str:
    raw = getattr(value, "value", value)
    if isinstance(value, (HLAinteger64Time, HLAinteger64Interval)):
        return str(int(raw))
    return str(float(raw))


def _decode_logical_time(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Time":
        return HLAinteger64Time(int(raw))
    if type_name == "HLAfloat64Time":
        return HLAfloat64Time(float(raw))
    raise ValueError(f"Unsupported logical time type: {type_name}")


def _decode_logical_interval(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Interval":
        return HLAinteger64Interval(int(raw))
    if type_name == "HLAfloat64Interval":
        return HLAfloat64Interval(float(raw))
    raise ValueError(f"Unsupported logical interval type: {type_name}")


def _region_set_spec(values: Sequence[Any]) -> str:
    return ",".join(str(int(value.value)) for value in values)


def _decode_region_set(spec: str) -> RegionHandleSet:
    return decode_handle_set(spec, RegionHandle, RegionHandleSet)


def _attribute_region_association_spec(values: Sequence[AttributeRegionAssociation]) -> str:
    parts: list[str] = []
    for value in values:
        parts.append(f"{handle_set_spec(value.attributes)}@{_region_set_spec(tuple(value.regions))}")
    return ";".join(parts)


def _decode_attribute_region_associations(spec: str) -> list[AttributeRegionAssociation]:
    if not spec:
        return []
    result: list[AttributeRegionAssociation] = []
    for entry in spec.split(";"):
        attributes_raw, regions_raw = entry.split("@", 1)
        result.append(
            AttributeRegionAssociation(
                decode_handle_set(attributes_raw, AttributeHandle, AttributeHandleSet),
                _decode_region_set(regions_raw),
            )
        )
    return result


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
    if method_name == "reportFederationExecutions":
        infos = cast(FederationExecutionInformationSet, args[0])
        payload = ";".join(
            f"{info.federation_execution_name}|{info.logical_time_implementation_name or ''}"
            for info in infos
        )
        return ("REPORT_FEDERATION_EXECUTIONS", payload)
    if method_name == "reflectAttributeValues":
        payload = (
            str(int(args[0].value)),
            handle_value_map_spec(args[1]),
            encode_bytes(args[2]),
            str(int(args[3].value)),
            str(int(args[4].value)),
        )
        if len(args) >= 7:
            return ("REFLECT_TSO", *payload, _logical_time_name(args[5]), _logical_scalar(args[5]), str(int(args[6].value)))
        return ("REFLECT", *payload)
    if method_name == "receiveInteraction":
        payload = (
            str(int(args[0].value)),
            handle_value_map_spec(args[1]),
            encode_bytes(args[2]),
            str(int(args[3].value)),
            str(int(args[4].value)),
        )
        if len(args) >= 7:
            return ("INTERACTION_TSO", *payload, _logical_time_name(args[5]), _logical_scalar(args[5]), str(int(args[6].value)))
        return ("INTERACTION", *payload)
    if method_name == "timeRegulationEnabled":
        return ("TIME_REGULATION_ENABLED", _logical_time_name(args[0]), _logical_scalar(args[0]))
    if method_name == "timeConstrainedEnabled":
        return ("TIME_CONSTRAINED_ENABLED", _logical_time_name(args[0]), _logical_scalar(args[0]))
    if method_name == "timeAdvanceGrant":
        return ("TIME_ADVANCE_GRANT", _logical_time_name(args[0]), _logical_scalar(args[0]))
    if method_name == "provideAttributeValueUpdate":
        return (
            "PROVIDE_ATTRIBUTE_VALUE_UPDATE",
            str(int(args[0].value)),
            handle_set_spec(args[1]),
            encode_bytes(args[2]),
        )
    if method_name == "requestRetraction":
        return ("REQUEST_RETRACTION", str(int(args[0].value)))
    if method_name == "startRegistrationForObjectClass":
        return ("START_REGISTRATION_FOR_OBJECT_CLASS", str(int(args[0].value)))
    if method_name == "stopRegistrationForObjectClass":
        return ("STOP_REGISTRATION_FOR_OBJECT_CLASS", str(int(args[0].value)))
    if method_name == "turnInteractionsOn":
        return ("TURN_INTERACTIONS_ON", str(int(args[0].value)))
    if method_name == "turnInteractionsOff":
        return ("TURN_INTERACTIONS_OFF", str(int(args[0].value)))
    if method_name == "removeObjectInstance":
        return ("REMOVE_OBJECT_INSTANCE", str(int(args[0].value)), encode_bytes(args[1]))
    if method_name == "confirmAttributeTransportationTypeChange":
        return (
            "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
            str(int(args[0].value)),
            handle_set_spec(args[1]),
            str(int(args[2].value)),
        )
    if method_name == "reportAttributeTransportationType":
        return (
            "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE",
            str(int(args[0].value)),
            str(int(args[1].value)),
            str(int(args[2].value)),
        )
    if method_name == "confirmInteractionTransportationTypeChange":
        return (
            "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
            str(int(args[0].value)),
            str(int(args[1].value)),
        )
    if method_name == "reportInteractionTransportationType":
        return (
            "REPORT_INTERACTION_TRANSPORTATION_TYPE",
            str(int(args[0].value)),
            str(int(args[1].value)),
            str(int(args[2].value)),
        )
    if method_name == "synchronizationPointRegistrationSucceeded":
        return ("SYNC_POINT_REGISTRATION_SUCCEEDED", str(args[0]))
    if method_name == "synchronizationPointRegistrationFailed":
        reason = args[1].name if isinstance(args[1], SynchronizationPointFailureReason) else str(args[1])
        return ("SYNC_POINT_REGISTRATION_FAILED", str(args[0]), reason)
    if method_name == "announceSynchronizationPoint":
        return ("ANNOUNCE_SYNC_POINT", str(args[0]), encode_bytes(args[1]))
    if method_name == "federationSynchronized":
        return ("FEDERATION_SYNCHRONIZED", str(args[0]), federate_handle_set_spec(args[1]))
    if method_name == "initiateFederateSave":
        if len(args) >= 2:
            return ("INITIATE_FEDERATE_SAVE_AT", str(args[0]), _logical_time_name(args[1]), _logical_scalar(args[1]))
        if not args:
            return ("INITIATE_FEDERATE_SAVE", "")
        return ("INITIATE_FEDERATE_SAVE", str(cast(Any, args[0])))
    if method_name == "federationSaved":
        return ("FEDERATION_SAVED",)
    if method_name == "federationNotSaved":
        reason = args[0].name if isinstance(args[0], SaveFailureReason) else str(args[0])
        return ("FEDERATION_NOT_SAVED", reason)
    if method_name == "federationSaveStatusResponse":
        encoded_pairs = ";".join(f"{int(pair.federate_handle.value)}:{pair.save_status.name}" for pair in cast(Sequence[FederateHandleSaveStatusPair], args[0]))
        return ("FEDERATION_SAVE_STATUS_RESPONSE", encoded_pairs)
    if method_name == "requestFederationRestoreSucceeded":
        return ("REQUEST_FEDERATION_RESTORE_SUCCEEDED", str(args[0]))
    if method_name == "requestFederationRestoreFailed":
        return ("REQUEST_FEDERATION_RESTORE_FAILED", str(args[0]))
    if method_name == "federationRestoreBegun":
        return ("FEDERATION_RESTORE_BEGUN",)
    if method_name == "initiateFederateRestore":
        return ("INITIATE_FEDERATE_RESTORE", str(args[0]), str(args[1]), str(int(args[2].value)))
    if method_name == "federationRestored":
        return ("FEDERATION_RESTORED",)
    if method_name == "federationNotRestored":
        reason = args[0].name if isinstance(args[0], RestoreFailureReason) else str(args[0])
        return ("FEDERATION_NOT_RESTORED", reason)
    if method_name == "federationRestoreStatusResponse":
        encoded_pairs = ";".join(
            f"{int(pair.pre_restore_handle.value)}:{int(pair.post_restore_handle.value)}:{pair.restore_status.name}"
            for pair in cast(Sequence[FederateRestoreStatus], args[0])
        )
        return ("FEDERATION_RESTORE_STATUS_RESPONSE", encoded_pairs)
    if method_name == "attributeOwnershipAcquisitionNotification":
        return ("OWNERSHIP_ACQUIRED", str(int(args[0].value)), handle_set_spec(args[1]), encode_bytes(args[2]))
    if method_name == "requestAttributeOwnershipAssumption":
        return ("REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION", str(int(args[0].value)), handle_set_spec(args[1]), encode_bytes(args[2]))
    if method_name == "informAttributeOwnership":
        return ("INFORM_ATTRIBUTE_OWNERSHIP", str(int(args[0].value)), str(int(args[1].value)), str(int(args[2].value)))
    if method_name == "attributeIsNotOwned":
        return ("ATTRIBUTE_IS_NOT_OWNED", str(int(args[0].value)), str(int(args[1].value)))
    if method_name == "attributeOwnershipUnavailable":
        return ("ATTRIBUTE_OWNERSHIP_UNAVAILABLE", str(int(args[0].value)), handle_set_spec(args[1]))
    if method_name == "requestAttributeOwnershipRelease":
        return ("REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE", str(int(args[0].value)), handle_set_spec(args[1]), encode_bytes(args[2]))
    if method_name == "requestDivestitureConfirmation":
        return ("REQUEST_DIVESTITURE_CONFIRMATION", str(int(args[0].value)), handle_set_spec(args[1]))
    if method_name == "confirmAttributeOwnershipAcquisitionCancellation":
        return ("CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION", str(int(args[0].value)), handle_set_spec(args[1]))
    return None


class HostedRTICommandProcessor:
    """Backend-neutral hosted transport command processor."""

    def __init__(self, rti: Any) -> None:
        self.federate = _CallbackQueueAmbassador()
        self.rti = rti

    def close(self) -> None:
        try:
            self.rti.close()
        except Exception:
            pass

    def handle_request(self, request: TransportRequest) -> TransportResponse:
        command = request.command
        fields = cast(Sequence[Any], request.fields)

        if command == "GET_HLA_VERSION":
            return TransportResponse(fields=(self.rti.getHLAversion(),))
        if command == "GET_FEDERATE_HANDLE":
            handle = self.rti.getFederateHandle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_FEDERATE_NAME":
            return TransportResponse(fields=(self.rti.getFederateName(FederateHandle(int(fields[0]))),))
        if command == "CONNECT":
            callback_model = CallbackModel[str(fields[0])]
            local_settings = str(fields[1]) if len(fields) >= 2 and fields[1] not in {"", None} else None
            self.rti.connect(self.federate, callback_model, local_settings)
            return TransportResponse()
        if command == "DISCONNECT":
            self.rti.disconnect()
            return TransportResponse()
        if command == "LIST_FEDERATION_EXECUTIONS":
            self.rti.listFederationExecutions()
            return TransportResponse()
        if command == "CREATE":
            federation_name = str(fields[0])
            logical_time_name = str(fields[1]) if len(fields) >= 2 else ""
            fom_modules = [str(value) for value in fields[2:]]
            self.rti.createFederationExecution(federation_name, fom_modules, logical_time_name or None)
            return TransportResponse()
        if command == "CREATE_WITH_MIM":
            federation_name = str(fields[0])
            logical_time_name = str(fields[1]) if len(fields) >= 2 else ""
            fom_modules = [str(value) for value in fields[2:]]
            self.rti.createFederationExecutionWithMIM(federation_name, fom_modules, logical_time_name or None)
            return TransportResponse()
        if command == "DESTROY":
            self.rti.destroyFederationExecution(str(fields[0]))
            return TransportResponse()
        if command == "JOIN":
            federate_name = str(fields[0]) if fields and fields[0] is not None else ""
            federate_type = str(fields[1])
            federation_name = str(fields[2])
            additional_foms = [str(value) for value in fields[3:]]
            if additional_foms:
                handle = self.rti.joinFederationExecution(federate_name, federate_type, federation_name, additional_foms)
            elif federate_name:
                handle = self.rti.joinFederationExecution(federate_name, federate_type, federation_name)
            else:
                handle = self.rti.joinFederationExecution(federate_type, federation_name)
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "RESIGN":
            try:
                action = ResignAction[str(fields[0])]
            except KeyError as exc:
                raise InvalidResignAction(repr(fields[0])) from exc
            self.rti.resignFederationExecution(action)
            return TransportResponse()
        if command == "REQUEST_FEDERATION_SAVE":
            label = str(fields[0])
            if len(fields) >= 3:
                self.rti.requestFederationSave(label, _decode_logical_time(str(fields[1]), fields[2]))
            else:
                self.rti.requestFederationSave(label)
            return TransportResponse()
        if command == "FEDERATE_SAVE_BEGUN":
            self.rti.federateSaveBegun()
            return TransportResponse()
        if command == "FEDERATE_SAVE_COMPLETE":
            self.rti.federateSaveComplete()
            return TransportResponse()
        if command == "FEDERATE_SAVE_NOT_COMPLETE":
            self.rti.federateSaveNotComplete()
            return TransportResponse()
        if command == "ABORT_FEDERATION_SAVE":
            self.rti.abortFederationSave()
            return TransportResponse()
        if command == "QUERY_FEDERATION_SAVE_STATUS":
            self.rti.queryFederationSaveStatus()
            return TransportResponse()
        if command == "REQUEST_FEDERATION_RESTORE":
            self.rti.requestFederationRestore(str(fields[0]))
            return TransportResponse()
        if command == "FEDERATE_RESTORE_COMPLETE":
            self.rti.federateRestoreComplete()
            return TransportResponse()
        if command == "FEDERATE_RESTORE_NOT_COMPLETE":
            self.rti.federateRestoreNotComplete()
            return TransportResponse()
        if command == "ABORT_FEDERATION_RESTORE":
            self.rti.abortFederationRestore()
            return TransportResponse()
        if command == "QUERY_FEDERATION_RESTORE_STATUS":
            self.rti.queryFederationRestoreStatus()
            return TransportResponse()
        if command == "GET_OBJECT_CLASS_HANDLE":
            return TransportResponse(fields=(str(int(self.rti.getObjectClassHandle(str(fields[0])).value)),))
        if command == "GET_OBJECT_CLASS_NAME":
            return TransportResponse(fields=(self.rti.getObjectClassName(ObjectClassHandle(int(fields[0]))),))
        if command == "GET_ATTRIBUTE_HANDLE":
            handle = self.rti.getAttributeHandle(ObjectClassHandle(int(fields[0])), str(fields[1]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_ATTRIBUTE_NAME":
            return TransportResponse(fields=(self.rti.getAttributeName(ObjectClassHandle(int(fields[0])), AttributeHandle(int(fields[1]))),))
        if command == "GET_DIMENSION_HANDLE":
            handle = self.rti.getDimensionHandle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_TRANSPORTATION_TYPE_HANDLE":
            requested = None if not fields or fields[0] in {"", None} else str(fields[0])
            handle = self.rti.getTransportationTypeHandle(requested)
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_TRANSPORTATION_TYPE_NAME":
            return TransportResponse(fields=(self.rti.getTransportationTypeName(TransportationTypeHandle(int(fields[0]))),))
        if command == "PUBLISH_OBJECT_CLASS_ATTRIBUTES":
            self.rti.publishObjectClassAttributes(
                ObjectClassHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "UNPUBLISH_OBJECT_CLASS_ATTRIBUTES":
            self.rti.unpublishObjectClassAttributes(
                ObjectClassHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES":
            self.rti.subscribeObjectClassAttributes(
                ObjectClassHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES":
            self.rti.unsubscribeObjectClassAttributes(
                ObjectClassHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS":
            self.rti.subscribeObjectClassAttributesWithRegions(
                ObjectClassHandle(int(fields[0])),
                _decode_attribute_region_associations(str(fields[1])),
            )
            return TransportResponse()
        if command == "UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS":
            self.rti.unsubscribeObjectClassAttributesWithRegions(
                ObjectClassHandle(int(fields[0])),
                _decode_attribute_region_associations(str(fields[1])),
            )
            return TransportResponse()
        if command == "CREATE_REGION":
            handle = self.rti.createRegion(
                decode_handle_set(str(fields[0]), DimensionHandle, set),
            )
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "SET_RANGE_BOUNDS":
            self.rti.setRangeBounds(
                RegionHandle(int(fields[0])),
                DimensionHandle(int(fields[1])),
                RangeBounds(int(fields[2]), int(fields[3])),
            )
            return TransportResponse()
        if command == "COMMIT_REGION_MODIFICATIONS":
            self.rti.commitRegionModifications(_decode_region_set(str(fields[0])))
            return TransportResponse()
        if command == "DELETE_REGION":
            self.rti.deleteRegion(RegionHandle(int(fields[0])))
            return TransportResponse()
        if command == "REGISTER_OBJECT_INSTANCE":
            if not fields:
                raise ValueError("REGISTER_OBJECT_INSTANCE requires an object class handle")
            if len(fields) >= 2 and fields[1]:
                handle = self.rti.registerObjectInstance(ObjectClassHandle(int(fields[0])), str(fields[1]))
            else:
                handle = self.rti.registerObjectInstance(ObjectClassHandle(int(fields[0])))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "REGISTER_OBJECT_INSTANCE_WITH_REGIONS":
            if len(fields) >= 3 and fields[2]:
                handle = self.rti.registerObjectInstanceWithRegions(
                    ObjectClassHandle(int(fields[0])),
                    _decode_attribute_region_associations(str(fields[1])),
                    str(fields[2]),
                )
            else:
                handle = self.rti.registerObjectInstanceWithRegions(
                    ObjectClassHandle(int(fields[0])),
                    _decode_attribute_region_associations(str(fields[1])),
                )
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "ASSOCIATE_REGIONS_FOR_UPDATES":
            self.rti.associateRegionsForUpdates(
                ObjectInstanceHandle(int(fields[0])),
                _decode_attribute_region_associations(str(fields[1])),
            )
            return TransportResponse()
        if command == "UNASSOCIATE_REGIONS_FOR_UPDATES":
            self.rti.unassociateRegionsForUpdates(
                ObjectInstanceHandle(int(fields[0])),
                _decode_attribute_region_associations(str(fields[1])),
            )
            return TransportResponse()
        if command == "GET_OBJECT_INSTANCE_HANDLE":
            handle = self.rti.getObjectInstanceHandle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_OBJECT_INSTANCE_NAME":
            return TransportResponse(fields=(self.rti.getObjectInstanceName(ObjectInstanceHandle(int(fields[0]))),))
        if command == "GET_KNOWN_OBJECT_CLASS_HANDLE":
            handle = self.rti.getKnownObjectClassHandle(ObjectInstanceHandle(int(fields[0])))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "UPDATE_ATTRIBUTE_VALUES":
            self.rti.updateAttributeValues(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_value_map(str(fields[1]), AttributeHandle, AttributeHandleValueMap),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP":
            handle = self.rti.updateAttributeValues(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_value_map(str(fields[1]), AttributeHandle, AttributeHandleValueMap),
                decode_bytes(str(fields[2])),
                _decode_logical_time(str(fields[3]), fields[4]),
            )
            if handle is None:
                return TransportResponse()
            return TransportResponse(fields=(str(int(handle.handle.value)),))
        if command == "DELETE_OBJECT_INSTANCE":
            self.rti.deleteObjectInstance(
                ObjectInstanceHandle(int(fields[0])),
                decode_bytes(str(fields[1])),
            )
            return TransportResponse()
        if command == "GET_INTERACTION_CLASS_HANDLE":
            handle = self.rti.getInteractionClassHandle(str(fields[0]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_INTERACTION_CLASS_NAME":
            return TransportResponse(fields=(self.rti.getInteractionClassName(InteractionClassHandle(int(fields[0]))),))
        if command == "GET_PARAMETER_HANDLE":
            handle = self.rti.getParameterHandle(InteractionClassHandle(int(fields[0])), str(fields[1]))
            return TransportResponse(fields=(str(int(handle.value)),))
        if command == "GET_PARAMETER_NAME":
            return TransportResponse(fields=(self.rti.getParameterName(InteractionClassHandle(int(fields[0])), ParameterHandle(int(fields[1]))),))
        if command == "PUBLISH_INTERACTION_CLASS":
            self.rti.publishInteractionClass(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "UNPUBLISH_INTERACTION_CLASS":
            self.rti.unpublishInteractionClass(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "SUBSCRIBE_INTERACTION_CLASS":
            self.rti.subscribeInteractionClass(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "UNSUBSCRIBE_INTERACTION_CLASS":
            self.rti.unsubscribeInteractionClass(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS":
            self.rti.subscribeInteractionClassWithRegions(
                InteractionClassHandle(int(fields[0])),
                _decode_region_set(str(fields[1])),
            )
            return TransportResponse()
        if command == "UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS":
            self.rti.unsubscribeInteractionClassWithRegions(
                InteractionClassHandle(int(fields[0])),
                _decode_region_set(str(fields[1])),
            )
            return TransportResponse()
        if command == "SEND_INTERACTION":
            self.rti.sendInteraction(
                InteractionClassHandle(int(fields[0])),
                decode_handle_value_map(str(fields[1]), ParameterHandle, ParameterHandleValueMap),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "SEND_INTERACTION_WITH_REGIONS":
            self.rti.sendInteractionWithRegions(
                InteractionClassHandle(int(fields[0])),
                decode_handle_value_map(str(fields[1]), ParameterHandle, ParameterHandleValueMap),
                _decode_region_set(str(fields[2])),
                decode_bytes(str(fields[3])),
            )
            return TransportResponse()
        if command == "SEND_INTERACTION_TIMESTAMP":
            handle = self.rti.sendInteraction(
                InteractionClassHandle(int(fields[0])),
                decode_handle_value_map(str(fields[1]), ParameterHandle, ParameterHandleValueMap),
                decode_bytes(str(fields[2])),
                _decode_logical_time(str(fields[3]), fields[4]),
            )
            if handle is None:
                return TransportResponse()
            return TransportResponse(fields=(str(int(handle.handle.value)),))
        if command == "REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT":
            self.rti.requestAttributeValueUpdate(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS":
            self.rti.requestAttributeValueUpdate(
                ObjectClassHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "REQUEST_ATTRIBUTE_VALUE_UPDATE_WITH_REGIONS":
            self.rti.requestAttributeValueUpdateWithRegions(
                ObjectInstanceHandle(int(fields[0])),
                _decode_attribute_region_associations(str(fields[1])),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE":
            self.rti.requestAttributeTransportationTypeChange(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                TransportationTypeHandle(int(fields[2])),
            )
            return TransportResponse()
        if command == "QUERY_ATTRIBUTE_TRANSPORTATION_TYPE":
            self.rti.queryAttributeTransportationType(
                ObjectInstanceHandle(int(fields[0])),
                AttributeHandle(int(fields[1])),
            )
            return TransportResponse()
        if command == "ENABLE_TIME_REGULATION":
            self.rti.enableTimeRegulation(_decode_logical_interval(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "ENABLE_TIME_CONSTRAINED":
            self.rti.enableTimeConstrained()
            return TransportResponse()
        if command == "DISABLE_TIME_REGULATION":
            self.rti.disableTimeRegulation()
            return TransportResponse()
        if command == "DISABLE_TIME_CONSTRAINED":
            self.rti.disableTimeConstrained()
            return TransportResponse()
        if command == "QUERY_LOGICAL_TIME":
            logical_time = self.rti.queryLogicalTime()
            return TransportResponse(fields=(_logical_time_name(logical_time), _logical_scalar(logical_time)))
        if command == "QUERY_LOOKAHEAD":
            lookahead = self.rti.queryLookahead()
            return TransportResponse(fields=(_logical_interval_name(lookahead), _logical_scalar(lookahead)))
        if command == "MODIFY_LOOKAHEAD":
            self.rti.modifyLookahead(_decode_logical_interval(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "ENABLE_ASYNCHRONOUS_DELIVERY":
            self.rti.enableAsynchronousDelivery()
            return TransportResponse()
        if command == "DISABLE_ASYNCHRONOUS_DELIVERY":
            self.rti.disableAsynchronousDelivery()
            return TransportResponse()
        if command == "REGISTER_FEDERATION_SYNCHRONIZATION_POINT":
            label = str(fields[0])
            tag = decode_bytes(str(fields[1]))
            synchronization_set = (
                decode_handle_set(str(fields[2]), FederateHandle, FederateHandleSet)
                if len(fields) >= 3 and fields[2]
                else None
            )
            if synchronization_set is None:
                self.rti.registerFederationSynchronizationPoint(label, tag)
            else:
                self.rti.registerFederationSynchronizationPoint(label, tag, synchronization_set)
            return TransportResponse()
        if command == "SYNCHRONIZATION_POINT_ACHIEVED":
            label = str(fields[0])
            successful = str(fields[1]) == "1" if len(fields) >= 2 else True
            self.rti.synchronizationPointAchieved(label, successful)
            return TransportResponse()
        if command == "UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.unconditionalAttributeOwnershipDivestiture(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.negotiatedAttributeOwnershipDivestiture(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "CONFIRM_DIVESTITURE":
            self.rti.confirmDivestiture(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_ACQUISITION":
            self.rti.attributeOwnershipAcquisition(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                decode_bytes(str(fields[2])),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE":
            self.rti.attributeOwnershipAcquisitionIfAvailable(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_RELEASE_DENIED":
            self.rti.attributeOwnershipReleaseDenied(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED":
            result = self.rti.attributeOwnershipDivestitureIfWanted(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse(fields=(handle_set_spec(result),))
        if command == "CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE":
            self.rti.cancelNegotiatedAttributeOwnershipDivestiture(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION":
            self.rti.cancelAttributeOwnershipAcquisition(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
            )
            return TransportResponse()
        if command == "QUERY_ATTRIBUTE_OWNERSHIP":
            self.rti.queryAttributeOwnership(ObjectInstanceHandle(int(fields[0])), AttributeHandle(int(fields[1])))
            return TransportResponse()
        if command == "IS_ATTRIBUTE_OWNED_BY_FEDERATE":
            owned = self.rti.isAttributeOwnedByFederate(ObjectInstanceHandle(int(fields[0])), AttributeHandle(int(fields[1])))
            return TransportResponse(fields=("1" if owned else "0",))
        if command == "CHANGE_ATTRIBUTE_ORDER_TYPE":
            self.rti.changeAttributeOrderType(
                ObjectInstanceHandle(int(fields[0])),
                decode_handle_set(str(fields[1]), AttributeHandle, AttributeHandleSet),
                OrderType[str(fields[2])],
            )
            return TransportResponse()
        if command == "CHANGE_INTERACTION_ORDER_TYPE":
            self.rti.changeInteractionOrderType(InteractionClassHandle(int(fields[0])), OrderType[str(fields[1])])
            return TransportResponse()
        if command == "REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE":
            self.rti.requestInteractionTransportationTypeChange(
                InteractionClassHandle(int(fields[0])),
                TransportationTypeHandle(int(fields[1])),
            )
            return TransportResponse()
        if command == "QUERY_INTERACTION_TRANSPORTATION_TYPE":
            if len(fields) >= 2:
                self.rti.queryInteractionTransportationType(
                    FederateHandle(int(fields[0])),
                    InteractionClassHandle(int(fields[1])),
                )
            else:
                self.rti.queryInteractionTransportationType(InteractionClassHandle(int(fields[0])))
            return TransportResponse()
        if command == "TIME_ADVANCE_REQUEST":
            self.rti.timeAdvanceRequest(_decode_logical_time(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "TIME_ADVANCE_REQUEST_AVAILABLE":
            self.rti.timeAdvanceRequestAvailable(_decode_logical_time(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "NEXT_MESSAGE_REQUEST":
            self.rti.nextMessageRequest(_decode_logical_time(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "NEXT_MESSAGE_REQUEST_AVAILABLE":
            self.rti.nextMessageRequestAvailable(_decode_logical_time(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "FLUSH_QUEUE_REQUEST":
            self.rti.flushQueueRequest(_decode_logical_time(str(fields[0]), fields[1]))
            return TransportResponse()
        if command == "QUERY_GALT":
            query = self.rti.queryGALT()
            if not query.time_is_valid:
                return TransportResponse(fields=("0",))
            return TransportResponse(fields=("1", _logical_time_name(query.time), _logical_scalar(query.time)))
        if command == "QUERY_LITS":
            query = self.rti.queryLITS()
            if not query.time_is_valid:
                return TransportResponse(fields=("0",))
            return TransportResponse(fields=("1", _logical_time_name(query.time), _logical_scalar(query.time)))
        if command == "RETRACT":
            self.rti.retract(MessageRetractionHandle(int(fields[0])))
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
            evoked = self.rti.evokeCallback(minimum)
        else:
            evoked = self.rti.evokeMultipleCallbacks(minimum, maximum if maximum is not None else minimum)
        delivered = len(self.federate.pending) > pending_before
        if delivered and self.federate.pending:
            return ("1", *self.federate.pending.popleft())
        return ("1",) if (delivered or evoked) else ("0",)
