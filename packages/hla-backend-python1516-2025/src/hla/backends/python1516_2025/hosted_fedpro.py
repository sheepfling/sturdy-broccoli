"""Hosted FedPro 2025 ambassador over the main python1516_2025 runtime lane."""
from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, NoReturn

from hla.rti1516_2025.datatypes import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformation,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformation,
    FederationExecutionMemberInformationSet,
    TimeQueryReturn,
)
from hla.rti1516_2025.enums import (
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    RestoreStatus,
    SaveFailureReason,
    SaveStatus,
    SynchronizationPointFailureReason,
)
from hla.rti1516_2025.exceptions import (
    AlreadyConnected,
    AttributeAlreadyOwned,
    AttributeNotDefined,
    AttributeNotOwned,
    AttributeNotPublished,
    CouldNotOpenFOM,
    ErrorReadingFOM,
    FederateAlreadyExecutionMember,
    FederateIsExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InconsistentFOM,
    InteractionClassNotPublished,
    InvalidInteractionClassHandle,
    InvalidLogicalTime,
    InvalidResignAction,
    InvalidTransportationTypeHandle,
    NotConnected,
    ObjectClassNotPublished,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
    RestoreInProgress,
    RestoreNotRequested,
    RTIinternalError,
    SaveInProgress,
    SaveNotInitiated,
    TimeRegulationIsNotEnabled,
)
from hla.rti1516_2025.handles import (
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
    TransportationTypeHandle,
)
from hla.rti1516_2025.time import (
    HLAfloat64Interval,
    HLAfloat64Time,
    HLAinteger64Interval,
    HLAinteger64Time,
    get_logical_time_factory,
)
from hla.transports.common import (
    TransportError,
    TransportRequest,
    coerce_transport_spec,
    decode_bytes,
    decode_handle_set,
    decode_handle_value_map,
    decode_order,
)


def resolve_fedpro_fom_path(designator: str) -> str:
    if designator.startswith("resource:"):
        return designator
    if Path(designator).is_absolute():
        return designator
    return designator


def _decode_logical_time(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Time":
        if str(raw).lower() in {"inf", "+inf", "-inf"}:
            return HLAfloat64Time(float(raw))
        return HLAinteger64Time(int(float(raw)))
    if type_name == "HLAfloat64Time":
        return HLAfloat64Time(float(raw))
    raise RTIinternalError(f"Unsupported logical time type from hosted FedPro transport: {type_name}")


def _invoke_federate_callback(ambassador: Any, method_name: str, *args: Any) -> None:
    getattr(ambassador, method_name)(*args)


def dispatch_fedpro_helper_callback(ambassador: Any, parts: list[str], *, logical_time_hint: str | None = None) -> None:
    if ambassador is None or not parts:
        return

    kind = parts[0]
    if kind == "DISCOVER":
        getattr(ambassador, "discoverObjectInstance")(ObjectInstanceHandle(int(parts[1])), ObjectClassHandle(int(parts[2])), parts[3])
        return
    if kind == "REFLECT":
        getattr(ambassador, "reflectAttributeValues")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "REFLECT_TSO":
        time_type = logical_time_hint or parts[6]
        getattr(ambassador, "reflectAttributeValues")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
            _decode_logical_time(time_type, parts[7]),
            decode_order(parts[8]),
        )
        return
    if kind == "INTERACTION":
        getattr(ambassador, "receiveInteraction")(
            InteractionClassHandle(int(parts[1])),
            decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "INTERACTION_TSO":
        time_type = logical_time_hint or parts[6]
        getattr(ambassador, "receiveInteraction")(
            InteractionClassHandle(int(parts[1])),
            decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
            _decode_logical_time(time_type, parts[7]),
            decode_order(parts[8]),
        )
        return
    if kind == "TIME_REGULATION_ENABLED":
        time_type = logical_time_hint or parts[1]
        getattr(ambassador, "timeRegulationEnabled")(_decode_logical_time(time_type, parts[2]))
        return
    if kind == "TIME_CONSTRAINED_ENABLED":
        time_type = logical_time_hint or parts[1]
        getattr(ambassador, "timeConstrainedEnabled")(_decode_logical_time(time_type, parts[2]))
        return
    if kind == "TIME_ADVANCE_GRANT":
        time_type = logical_time_hint or parts[1]
        getattr(ambassador, "timeAdvanceGrant")(_decode_logical_time(time_type, parts[2]))
        return
    if kind == "REQUEST_RETRACTION":
        _invoke_federate_callback(ambassador, "requestRetraction", MessageRetractionHandle(int(parts[1])))
        return
    if kind == "START_REGISTRATION_FOR_OBJECT_CLASS":
        _invoke_federate_callback(ambassador, "startRegistrationForObjectClass", ObjectClassHandle(int(parts[1])))
        return
    if kind == "STOP_REGISTRATION_FOR_OBJECT_CLASS":
        _invoke_federate_callback(ambassador, "stopRegistrationForObjectClass", ObjectClassHandle(int(parts[1])))
        return
    if kind == "TURN_INTERACTIONS_ON":
        _invoke_federate_callback(ambassador, "turnInteractionsOn", InteractionClassHandle(int(parts[1])))
        return
    if kind == "TURN_INTERACTIONS_OFF":
        _invoke_federate_callback(ambassador, "turnInteractionsOff", InteractionClassHandle(int(parts[1])))
        return
    if kind == "REMOVE_OBJECT_INSTANCE":
        if len(parts) >= 5:
            _invoke_federate_callback(
                ambassador,
                "removeObjectInstance",
                ObjectInstanceHandle(int(parts[1])),
                decode_bytes(parts[2]),
                decode_order(parts[3]),
                TransportationTypeHandle(int(parts[4])),
            )
            return
        _invoke_federate_callback(ambassador, "removeObjectInstance", ObjectInstanceHandle(int(parts[1])), decode_bytes(parts[2]))
        return
    if kind == "REMOVE_OBJECT_INSTANCE_TSO":
        time_type = logical_time_hint or parts[3]
        _invoke_federate_callback(
            ambassador,
            "removeObjectInstance",
            ObjectInstanceHandle(int(parts[1])),
            decode_bytes(parts[2]),
            FederateHandle(int(parts[7])),
            _decode_logical_time(time_type, parts[4]),
            decode_order(parts[5]),
            decode_order(parts[6]),
            MessageRetractionHandle(int(parts[8])) if len(parts) >= 9 else None,
        )
        return
    if kind == "PROVIDE_ATTRIBUTE_VALUE_UPDATE":
        _invoke_federate_callback(
            ambassador,
            "provideAttributeValueUpdate",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "SYNC_POINT_REGISTRATION_SUCCEEDED":
        getattr(ambassador, "synchronizationPointRegistrationSucceeded")(parts[1])
        return
    if kind == "SYNC_POINT_REGISTRATION_FAILED":
        getattr(ambassador, "synchronizationPointRegistrationFailed")(parts[1], SynchronizationPointFailureReason[parts[2]])
        return
    if kind == "ANNOUNCE_SYNC_POINT":
        getattr(ambassador, "announceSynchronizationPoint")(parts[1], decode_bytes(parts[2]))
        return
    if kind == "FEDERATION_SYNCHRONIZED":
        getattr(ambassador, "federationSynchronized")(parts[1], decode_handle_set(parts[2], FederateHandle, FederateHandleSet))
        return
    if kind == "INITIATE_FEDERATE_SAVE":
        getattr(ambassador, "initiateFederateSave")(parts[1])
        return
    if kind == "INITIATE_FEDERATE_SAVE_AT":
        time_type = logical_time_hint or parts[2]
        getattr(ambassador, "initiateFederateSave")(parts[1], _decode_logical_time(time_type, parts[3]))
        return
    if kind == "FEDERATION_SAVED":
        getattr(ambassador, "federationSaved")()
        return
    if kind == "FEDERATION_NOT_SAVED":
        getattr(ambassador, "federationNotSaved")(SaveFailureReason[parts[1]])
        return
    if kind == "FEDERATION_SAVE_STATUS_RESPONSE":
        payload = []
        if len(parts) >= 2 and parts[1]:
            for item in parts[1].split(";"):
                handle_raw, status_raw = item.split(":", 1)
                payload.append(FederateHandleSaveStatusPair(FederateHandle(int(handle_raw)), SaveStatus[status_raw]))
        getattr(ambassador, "federationSaveStatusResponse")(payload)
        return
    if kind == "REQUEST_FEDERATION_RESTORE_SUCCEEDED":
        getattr(ambassador, "requestFederationRestoreSucceeded")(parts[1])
        return
    if kind == "REQUEST_FEDERATION_RESTORE_FAILED":
        getattr(ambassador, "requestFederationRestoreFailed")(parts[1])
        return
    if kind == "FEDERATION_RESTORE_BEGUN":
        getattr(ambassador, "federationRestoreBegun")()
        return
    if kind == "INITIATE_FEDERATE_RESTORE":
        getattr(ambassador, "initiateFederateRestore")(parts[1], parts[2], FederateHandle(int(parts[3])))
        return
    if kind == "FEDERATION_RESTORED":
        getattr(ambassador, "federationRestored")()
        return
    if kind == "FEDERATION_NOT_RESTORED":
        getattr(ambassador, "federationNotRestored")(RestoreFailureReason[parts[1]])
        return
    if kind == "FEDERATION_RESTORE_STATUS_RESPONSE":
        payload = []
        if len(parts) >= 2 and parts[1]:
            for item in parts[1].split(";"):
                pre_raw, post_raw, status_raw = item.split(":", 2)
                payload.append(
                    FederateRestoreStatus(
                        FederateHandle(int(pre_raw)),
                        FederateHandle(int(post_raw)),
                        RestoreStatus[status_raw],
                    )
                )
        getattr(ambassador, "federationRestoreStatusResponse")(payload)
        return
    if kind == "OWNERSHIP_ACQUIRED":
        getattr(ambassador, "attributeOwnershipAcquisitionNotification")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION":
        getattr(ambassador, "requestAttributeOwnershipAssumption")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "INFORM_ATTRIBUTE_OWNERSHIP":
        getattr(ambassador, "informAttributeOwnership")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            FederateHandle(int(parts[3])),
        )
        return
    if kind == "ATTRIBUTE_IS_NOT_OWNED":
        getattr(ambassador, "attributeIsNotOwned")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE":
        getattr(ambassador, "attributeOwnershipUnavailable")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE":
        getattr(ambassador, "requestAttributeOwnershipRelease")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_DIVESTITURE_CONFIRMATION":
        getattr(ambassador, "requestDivestitureConfirmation")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION":
        getattr(ambassador, "confirmAttributeOwnershipAcquisitionCancellation")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    raise RTIinternalError(f"Unknown hosted FedPro callback payload: {parts!r}")


class FedPro2025RTIAmbassador:
    """Hosted RTI ambassador over the main python1516_2025 transport route."""

    backend_info: Any = None
    _CAMELCASE_ALIAS_OVERRIDES = {
        "reserveMultipleObjectInstanceNames": "reserve_multiple_object_instance_name",
        "releaseMultipleObjectInstanceNames": "release_multiple_object_instance_name",
    }

    def __init__(self, transport: Any, *, fom_resolver: Callable[[str], str] | None = None) -> None:
        self._transport = transport
        self._federate = None
        self._logical_time_hint = "HLAinteger64Time"
        self._joined_handle = None
        self._fom_resolver = fom_resolver or resolve_fedpro_fom_path

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        alias = self._CAMELCASE_ALIAS_OVERRIDES.get(name, self._camel_to_snake(name))
        try:
            candidate = object.__getattribute__(self, alias)
        except AttributeError as exc:
            raise AttributeError(name) from exc
        if callable(candidate):
            return candidate
        raise AttributeError(name)

    def _verification_spawn_like(self):
        config = getattr(self._transport, "config", None)
        target = getattr(config, "target", None)
        schema = getattr(config, "schema", "rti1516_2025")
        if target is None:
            raise TypeError("FedPro 2025 ambassador requires a transport target to spawn a sibling RTI")
        transport = coerce_transport_spec({"kind": "grpc", "target": target, "schema": schema})
        if transport is None:
            raise TypeError("Unable to create a sibling transport for hosted FedPro verification")
        clone = type(self)(transport.start(), fom_resolver=self._fom_resolver)
        clone._logical_time_hint = self._logical_time_hint
        return clone

    @staticmethod
    def _decode_time(kind: str, value: str):
        if kind == "HLAfloat64Time":
            return HLAfloat64Time(float(value))
        if kind == "HLAinteger64Time":
            return HLAinteger64Time(int(value))
        raise RTIinternalError(f"Hosted FedPro only supports HLAinteger64Time and HLAfloat64Time logical time values; got {kind}")

    @staticmethod
    def _decode_interval(kind: str, value: str):
        if kind == "HLAfloat64Interval":
            return HLAfloat64Interval(float(value))
        if kind == "HLAinteger64Interval":
            return HLAinteger64Interval(int(value))
        raise RTIinternalError(f"Hosted FedPro only supports HLAinteger64Interval and HLAfloat64Interval logical intervals; got {kind}")

    @staticmethod
    def _callback_model_name(model: Any) -> str:
        return str(getattr(model, "name", model))

    @staticmethod
    def _time_kind_and_value(value: Any) -> tuple[str, str]:
        kind = type(value).__name__
        scalar = getattr(value, "value", value)
        if kind not in {"HLAinteger64Time", "HLAfloat64Time", "HLAinteger64Interval", "HLAfloat64Interval"}:
            raise RTIinternalError(
                "Hosted FedPro only supports HLAinteger64Time and HLAfloat64Time logical time values; "
                f"got {kind}"
            )
        return kind, str(scalar)

    @staticmethod
    def _encode_parameter_values(parameter_values: dict[object, bytes]) -> str:
        return ",".join(
            f"{FedPro2025RTIAmbassador._field_text(parameter)}:{value.hex()}" for parameter, value in parameter_values.items()
        )

    @staticmethod
    def _encode_handle_set(handles: Any) -> str:
        return ",".join(FedPro2025RTIAmbassador._field_text(handle) for handle in handles)

    @classmethod
    def _encode_attribute_region_associations(cls, attribute_region_associations: Any) -> str:
        pair_specs: list[str] = []
        for association in attribute_region_associations:
            attributes = getattr(association, "attributes", association[0])
            regions = getattr(association, "regions", association[1])
            attribute_spec = ",".join(sorted(cls._field_text(attribute) for attribute in attributes))
            region_spec = ",".join(sorted(cls._field_text(region) for region in regions))
            pair_specs.append(f"{attribute_spec}|{region_spec}")
        return ";".join(pair_specs)

    @classmethod
    def _encode_region_set(cls, regions: Any) -> str:
        return ",".join(sorted(cls._field_text(region) for region in regions))

    @staticmethod
    def _as_handle(handle_type: Any, raw_value: str):
        return handle_type(int(raw_value))

    @staticmethod
    def _field_text(value: Any) -> str:
        scalar = getattr(value, "value", value)
        return str(scalar)

    @staticmethod
    def _remap_transport_error(exc: TransportError) -> NoReturn:
        if exc.code == "AlreadyConnected":
            raise AlreadyConnected(exc.message or exc.code) from exc
        if exc.code == "FederateIsExecutionMember":
            raise FederateIsExecutionMember(exc.message or exc.code) from exc
        if exc.code == "FederateAlreadyExecutionMember":
            raise FederateAlreadyExecutionMember(exc.message or exc.code) from exc
        if exc.code == "FederateNameAlreadyInUse":
            raise FederateNameAlreadyInUse(exc.message or exc.code) from exc
        if exc.code == "FederatesCurrentlyJoined":
            raise FederatesCurrentlyJoined(exc.message or exc.code) from exc
        if exc.code == "FederationExecutionAlreadyExists":
            raise FederationExecutionAlreadyExists(exc.message or exc.code) from exc
        if exc.code == "FederationExecutionDoesNotExist":
            raise FederationExecutionDoesNotExist(exc.message or exc.code) from exc
        if exc.code == "InvalidLogicalTime":
            raise InvalidLogicalTime(exc.message or exc.code) from exc
        if exc.code == "NotConnected":
            raise NotConnected(exc.message or exc.code) from exc
        if exc.code == "ObjectInstanceNotKnown":
            raise ObjectInstanceNotKnown(exc.message or exc.code) from exc
        if exc.code == "AttributeNotDefined":
            raise AttributeNotDefined(exc.message or exc.code) from exc
        if exc.code == "AttributeNotPublished":
            raise AttributeNotPublished(exc.message or exc.code) from exc
        if exc.code == "AttributeNotOwned":
            raise AttributeNotOwned(exc.message or exc.code) from exc
        if exc.code == "AttributeAlreadyOwned":
            raise AttributeAlreadyOwned(exc.message or exc.code) from exc
        if exc.code == "CouldNotOpenFOM":
            raise CouldNotOpenFOM(exc.message or exc.code) from exc
        if exc.code == "ErrorReadingFOM":
            raise ErrorReadingFOM(exc.message or exc.code) from exc
        if exc.code == "InvalidInteractionClassHandle":
            raise InvalidInteractionClassHandle(exc.message or exc.code) from exc
        if exc.code == "InconsistentFOM":
            raise InconsistentFOM(exc.message or exc.code) from exc
        if exc.code == "ObjectClassNotPublished":
            raise ObjectClassNotPublished(exc.message or exc.code) from exc
        if exc.code == "InteractionClassNotPublished":
            raise InteractionClassNotPublished(exc.message or exc.code) from exc
        if exc.code in {"InvalidTransportationType", "InvalidTransportationTypeHandle"}:
            raise InvalidTransportationTypeHandle(exc.message or exc.code) from exc
        if exc.code == "FederateNotExecutionMember":
            raise FederateNotExecutionMember(exc.message or exc.code) from exc
        if exc.code == "SaveInProgress":
            raise SaveInProgress(exc.message or exc.code) from exc
        if exc.code == "SaveNotInitiated":
            raise SaveNotInitiated(exc.message or exc.code) from exc
        if exc.code == "RestoreInProgress":
            raise RestoreInProgress(exc.message or exc.code) from exc
        if exc.code == "RestoreNotInProgress":
            from hla.rti1516_2025.exceptions import RestoreNotInProgress

            raise RestoreNotInProgress(exc.message or exc.code) from exc
        if exc.code == "RestoreNotRequested":
            raise RestoreNotRequested(exc.message or exc.code) from exc
        if exc.code == "TimeRegulationIsNotEnabled":
            raise TimeRegulationIsNotEnabled(exc.message or exc.code) from exc
        if exc.code == "InvalidMessageRetractionHandle":
            from hla.rti1516_2025.exceptions import InvalidMessageRetractionHandle

            raise InvalidMessageRetractionHandle(exc.message or exc.code) from exc
        if exc.code == "InvalidResignAction":
            raise InvalidResignAction(exc.message or exc.code) from exc
        if exc.code == "FederateOwnsAttributes":
            raise FederateOwnsAttributes(exc.message or exc.code) from exc
        if exc.code == "OwnershipAcquisitionPending":
            raise OwnershipAcquisitionPending(exc.message or exc.code) from exc
        raise exc

    def connect(self, federate: Any, callback_model: CallbackModel, local_settings_designator: str = "") -> None:
        self._federate = federate
        try:
            self._transport.request(
                TransportRequest(command="CONNECT", fields=(self._callback_model_name(callback_model), local_settings_designator))
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def disconnect(self) -> None:
        try:
            self._transport.request(TransportRequest(command="DISCONNECT"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def get_time_factory(self):
        return get_logical_time_factory(self._logical_time_hint)

    def create_federation_execution(
        self,
        federation_name: str,
        fom_modules: list[object],
        logical_time_implementation_name: str | None = None,
    ) -> None:
        effective_time = logical_time_implementation_name or "HLAinteger64Time"
        self._logical_time_hint = effective_time
        module_fields = tuple(self._fom_resolver(str(module)) for module in fom_modules)
        try:
            self._transport.request(TransportRequest(command="CREATE", fields=(federation_name, effective_time, *module_fields)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def createFederationExecution(  # noqa: N802
        self,
        federation_name: str,
        fom_modules: list[object],
        logicalTimeImplementationName: str | None = None,
    ) -> None:
        self.create_federation_execution(
            federation_name,
            fom_modules,
            logical_time_implementation_name=logicalTimeImplementationName,
        )

    def create_federation_execution_with_mim(
        self,
        federation_name: str,
        fom_modules: list[object],
        logical_time_implementation_name: str,
    ) -> None:
        self._logical_time_hint = logical_time_implementation_name
        mim_path = "HLAstandardMIM.xml"
        fields = (
            federation_name,
            logical_time_implementation_name,
            mim_path,
            *(self._fom_resolver(str(module)) for module in fom_modules),
        )
        try:
            self._transport.request(TransportRequest(command="CREATE_WITH_MIM_AND_TIME", fields=fields))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def createFederationExecutionWithMIM(  # noqa: N802
        self,
        federation_name: str,
        fom_modules: list[object],
        logicalTimeImplementationName: str,
    ) -> None:
        self.create_federation_execution_with_mim(
            federation_name,
            fom_modules,
            logical_time_implementation_name=logicalTimeImplementationName,
        )

    def destroy_federation_execution(self, federation_name: str) -> None:
        try:
            self._transport.request(TransportRequest(command="DESTROY", fields=(federation_name,)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def list_federation_executions(self) -> None:
        try:
            self._transport.request(TransportRequest(command="LIST_FEDERATION_EXECUTIONS"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def list_federation_execution_members(self, federation_name: str) -> None:
        try:
            self._transport.request(TransportRequest(command="LIST_FEDERATION_EXECUTION_MEMBERS", fields=(federation_name,)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def register_federation_synchronization_point(self, label: str, user_supplied_tag: bytes, sync_set: Any = None) -> None:
        fields = [label, user_supplied_tag.hex()]
        if sync_set is not None:
            fields.append(",".join(sorted(self._field_text(handle) for handle in sync_set)))
        try:
            self._transport.request(TransportRequest(command="REGISTER_FEDERATION_SYNCHRONIZATION_POINT", fields=tuple(fields)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def synchronization_point_achieved(self, label: str, success_indicator: bool = True) -> None:
        try:
            self._transport.request(
                TransportRequest(command="SYNCHRONIZATION_POINT_ACHIEVED", fields=(label, "1" if success_indicator else "0"))
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def join_federation_execution(
        self,
        federate_name: str,
        federate_type: str,
        federation_name: str,
        additional_fom_modules: Any = None,
    ):
        fields: tuple[str, ...] = (federate_name, federate_type, federation_name)
        if additional_fom_modules is not None:
            fields = (
                federate_name,
                federate_type,
                federation_name,
                *(self._fom_resolver(str(module)) for module in additional_fom_modules),
            )
        try:
            handle = self._as_handle(FederateHandle, self._transport.request(TransportRequest(command="JOIN", fields=fields)).fields[0])
            self._joined_handle = handle
            return handle
        except TransportError as exc:
            self._remap_transport_error(exc)

    def resign_federation_execution(self, resign_action: Any) -> None:
        action = getattr(resign_action, "name", str(resign_action))
        try:
            self._transport.request(TransportRequest(command="RESIGN", fields=(action,)))
        except KeyError as exc:
            raise InvalidResignAction(action) from exc
        except TransportError as exc:
            self._remap_transport_error(exc)

    def set_automatic_resign_directive(self, resign_action: Any) -> None:
        action = getattr(resign_action, "name", str(resign_action))
        try:
            self._transport.request(TransportRequest(command="SET_AUTOMATIC_RESIGN_DIRECTIVE", fields=(action,)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def get_automatic_resign_directive(self):
        raw = self._transport.request(TransportRequest(command="GET_AUTOMATIC_RESIGN_DIRECTIVE")).fields[0]
        if isinstance(raw, str):
            return ResignAction[raw]
        return ResignAction(int(raw))

    def set_service_reporting_switch(self, value: bool) -> None:
        self._transport.request(
            TransportRequest(command="SET_SERVICE_REPORTING_SWITCH", fields=("1" if value else "0",))
        )

    def get_service_reporting_switch(self) -> bool:
        return self._transport.request(TransportRequest(command="GET_SERVICE_REPORTING_SWITCH")).fields == ("1",)

    def set_exception_reporting_switch(self, value: bool) -> None:
        self._transport.request(
            TransportRequest(command="SET_EXCEPTION_REPORTING_SWITCH", fields=("1" if value else "0",))
        )

    def get_exception_reporting_switch(self) -> bool:
        return self._transport.request(TransportRequest(command="GET_EXCEPTION_REPORTING_SWITCH")).fields == ("1",)

    def request_federation_save(self, label: str, logical_time: Any = None) -> None:
        try:
            if logical_time is None:
                self._transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(label,)))
                return
            kind, scalar = self._time_kind_and_value(logical_time)
            self._logical_time_hint = kind
            self._transport.request(TransportRequest(command="REQUEST_FEDERATION_SAVE", fields=(label, kind, scalar)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def federate_save_begun(self) -> None:
        try:
            self._transport.request(TransportRequest(command="FEDERATE_SAVE_BEGUN"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def federate_save_complete(self) -> None:
        try:
            self._transport.request(TransportRequest(command="FEDERATE_SAVE_COMPLETE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def federate_save_not_complete(self) -> None:
        try:
            self._transport.request(TransportRequest(command="FEDERATE_SAVE_NOT_COMPLETE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def query_federation_save_status(self) -> None:
        try:
            self._transport.request(TransportRequest(command="QUERY_FEDERATION_SAVE_STATUS"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def request_federation_restore(self, label: str) -> None:
        try:
            self._transport.request(TransportRequest(command="REQUEST_FEDERATION_RESTORE", fields=(label,)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def federate_restore_complete(self) -> None:
        try:
            self._transport.request(TransportRequest(command="FEDERATE_RESTORE_COMPLETE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def federate_restore_not_complete(self) -> None:
        try:
            self._transport.request(TransportRequest(command="FEDERATE_RESTORE_NOT_COMPLETE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def query_federation_restore_status(self) -> None:
        try:
            self._transport.request(TransportRequest(command="QUERY_FEDERATION_RESTORE_STATUS"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def abort_federation_save(self) -> None:
        try:
            self._transport.request(TransportRequest(command="ABORT_FEDERATION_SAVE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def abort_federation_restore(self) -> None:
        try:
            self._transport.request(TransportRequest(command="ABORT_FEDERATION_RESTORE"))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def get_interaction_class_handle(self, name: str):
        return self._as_handle(
            InteractionClassHandle,
            self._transport.request(TransportRequest(command="GET_INTERACTION_CLASS_HANDLE", fields=(name,))).fields[0],
        )

    def get_object_class_handle(self, name: str):
        return self._as_handle(
            ObjectClassHandle,
            self._transport.request(TransportRequest(command="GET_OBJECT_CLASS_HANDLE", fields=(name,))).fields[0],
        )

    def get_attribute_handle(self, object_class: Any, attribute_name: str):
        return self._as_handle(
            AttributeHandle,
            self._transport.request(
                TransportRequest(command="GET_ATTRIBUTE_HANDLE", fields=(self._field_text(object_class), attribute_name))
            ).fields[0],
        )

    def get_parameter_handle(self, interaction_class: Any, parameter_name: str):
        return self._as_handle(
            ParameterHandle,
            self._transport.request(
                TransportRequest(command="GET_PARAMETER_HANDLE", fields=(self._field_text(interaction_class), parameter_name))
            ).fields[0],
        )

    def get_parameter_name(self, interaction_class: Any, parameter: Any) -> str:
        return self._transport.request(
            TransportRequest(command="GET_PARAMETER_NAME", fields=(self._field_text(interaction_class), self._field_text(parameter)))
        ).fields[0]

    def get_federate_handle(self, name: str):
        return self._as_handle(FederateHandle, self._transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=(name,))).fields[0])

    def normalize_federate_handle(self, federate_handle: Any) -> int:
        return int(
            self._transport.request(TransportRequest(command="NORMALIZE_FEDERATE_HANDLE", fields=(self._field_text(federate_handle),))).fields[0]
        )

    def get_object_class_name(self, object_class: Any) -> str:
        return self._transport.request(TransportRequest(command="GET_OBJECT_CLASS_NAME", fields=(self._field_text(object_class),))).fields[0]

    def get_attribute_name(self, object_class: Any, attribute: Any) -> str:
        return self._transport.request(
            TransportRequest(command="GET_ATTRIBUTE_NAME", fields=(self._field_text(object_class), self._field_text(attribute)))
        ).fields[0]

    def get_interaction_class_name(self, interaction_class: Any) -> str:
        return self._transport.request(
            TransportRequest(command="GET_INTERACTION_CLASS_NAME", fields=(self._field_text(interaction_class),))
        ).fields[0]

    def get_order_name(self, order_type: Any) -> str:
        return self._transport.request(TransportRequest(command="GET_ORDER_NAME", fields=(getattr(order_type, "name", order_type),))).fields[0]

    def get_order_type(self, name: str):
        raw = self._transport.request(TransportRequest(command="GET_ORDER_TYPE", fields=(name,))).fields[0]
        if isinstance(raw, str):
            return OrderType[raw]
        return OrderType(int(raw))

    def get_transportation_type_name(self, transportation_type: Any) -> str:
        return self._transport.request(
            TransportRequest(command="GET_TRANSPORTATION_TYPE_NAME", fields=(self._field_text(transportation_type),))
        ).fields[0]

    @staticmethod
    def get_transportation_type(name: str):
        normalized = name.strip().lower()
        if normalized == "hlareliable":
            return SimpleNamespace(name="RELIABLE")
        if normalized == "hlabesteffort":
            return SimpleNamespace(name="BEST_EFFORT")
        raise ValueError(name)

    @staticmethod
    def get_transportation_name(transportation_type: Any) -> str:
        member_name = getattr(transportation_type, "name", "")
        mapping = {"RELIABLE": "HLAreliable", "BEST_EFFORT": "HLAbestEffort"}
        return mapping[member_name]

    @staticmethod
    def get_attribute_handle_factory():
        from hla.rti1516_2025.handles import AttributeHandleFactory

        return AttributeHandleFactory()

    @staticmethod
    def get_attribute_handle_set_factory():
        from hla.rti1516_2025.handles import AttributeHandleSetFactory

        return AttributeHandleSetFactory()

    @staticmethod
    def get_attribute_handle_value_map_factory():
        from hla.rti1516_2025.handles import AttributeHandleValueMapFactory

        return AttributeHandleValueMapFactory()

    @staticmethod
    def get_attribute_set_region_set_pair_list_factory():
        from hla.rti1516_2025.handles import AttributeSetRegionSetPairListFactory

        return AttributeSetRegionSetPairListFactory()

    @staticmethod
    def get_dimension_handle_factory():
        from hla.rti1516_2025.handles import DimensionHandleFactory

        return DimensionHandleFactory()

    @staticmethod
    def get_dimension_handle_set_factory():
        from hla.rti1516_2025.handles import DimensionHandleSetFactory

        return DimensionHandleSetFactory()

    @staticmethod
    def get_federate_handle_factory():
        from hla.rti1516_2025.handles import FederateHandleFactory

        return FederateHandleFactory()

    @staticmethod
    def get_federate_handle_set_factory():
        from hla.rti1516_2025.handles import FederateHandleSetFactory

        return FederateHandleSetFactory()

    @staticmethod
    def get_interaction_class_handle_factory():
        from hla.rti1516_2025.handles import InteractionClassHandleFactory

        return InteractionClassHandleFactory()

    @staticmethod
    def get_object_class_handle_factory():
        from hla.rti1516_2025.handles import ObjectClassHandleFactory

        return ObjectClassHandleFactory()

    @staticmethod
    def get_object_instance_handle_factory():
        from hla.rti1516_2025.handles import ObjectInstanceHandleFactory

        return ObjectInstanceHandleFactory()

    @staticmethod
    def get_parameter_handle_factory():
        from hla.rti1516_2025.handles import ParameterHandleFactory

        return ParameterHandleFactory()

    @staticmethod
    def get_parameter_handle_value_map_factory():
        from hla.rti1516_2025.handles import ParameterHandleValueMapFactory

        return ParameterHandleValueMapFactory()

    @staticmethod
    def get_region_handle_factory():
        from hla.rti1516_2025.handles import RegionHandleFactory

        return RegionHandleFactory()

    @staticmethod
    def get_region_handle_set_factory():
        from hla.rti1516_2025.handles import RegionHandleSetFactory

        return RegionHandleSetFactory()

    @staticmethod
    def get_message_retraction_handle_factory():
        from hla.rti1516_2025.handles import MessageRetractionHandleFactory

        return MessageRetractionHandleFactory()

    @staticmethod
    def get_transportation_type_handle_factory():
        from hla.rti1516_2025.handles import TransportationTypeHandleFactory

        return TransportationTypeHandleFactory()

    @staticmethod
    def decode_attribute_handle(data: bytes, offset: int = 0):
        return AttributeHandle.decode(data, offset)

    @staticmethod
    def decode_dimension_handle(data: bytes, offset: int = 0):
        return DimensionHandle.decode(data, offset)

    @staticmethod
    def decode_federate_handle(data: bytes, offset: int = 0):
        return FederateHandle.decode(data, offset)

    @staticmethod
    def decode_interaction_class_handle(data: bytes, offset: int = 0):
        return InteractionClassHandle.decode(data, offset)

    @staticmethod
    def decode_message_retraction_handle(data: bytes, offset: int = 0):
        return MessageRetractionHandle.decode(data, offset)

    @staticmethod
    def decode_object_class_handle(data: bytes, offset: int = 0):
        return ObjectClassHandle.decode(data, offset)

    @staticmethod
    def decode_object_instance_handle(data: bytes, offset: int = 0):
        return ObjectInstanceHandle.decode(data, offset)

    @staticmethod
    def decode_parameter_handle(data: bytes, offset: int = 0):
        return ParameterHandle.decode(data, offset)

    @staticmethod
    def decode_region_handle(data: bytes, offset: int = 0):
        return RegionHandle.decode(data, offset)

    def get_dimension_handle(self, name: str):
        return self._as_handle(DimensionHandle, self._transport.request(TransportRequest(command="GET_DIMENSION_HANDLE", fields=(name,))).fields[0])

    def get_transportation_type_handle(self, transportation_name: str):
        return self._as_handle(
            TransportationTypeHandle,
            self._transport.request(TransportRequest(command="GET_TRANSPORTATION_TYPE_HANDLE", fields=(transportation_name,))).fields[0],
        )

    def get_federate_name(self, federate_handle: Any) -> str:
        return self._transport.request(TransportRequest(command="GET_FEDERATE_NAME", fields=(self._field_text(federate_handle),))).fields[0]

    def get_object_instance_name(self, object_instance: Any) -> str:
        try:
            return self._transport.request(
                TransportRequest(command="GET_OBJECT_INSTANCE_NAME", fields=(self._field_text(object_instance),))
            ).fields[0]
        except TransportError as exc:
            self._remap_transport_error(exc)

    def publish_interaction_class(self, interaction_class: Any) -> None:
        try:
            self._transport.request(TransportRequest(command="PUBLISH_INTERACTION_CLASS", fields=(self._field_text(interaction_class),)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def subscribe_interaction_class(self, interaction_class: Any) -> None:
        self._transport.request(TransportRequest(command="SUBSCRIBE_INTERACTION_CLASS", fields=(self._field_text(interaction_class),)))

    def publish_object_class_directed_interactions(self, object_class: Any, interaction_classes: Any) -> None:
        for interaction_class in interaction_classes:
            self._transport.request(
                TransportRequest(
                    command="PUBLISH_OBJECT_CLASS_DIRECTED_INTERACTIONS",
                    fields=(self._field_text(object_class), self._field_text(interaction_class)),
                )
            )

    def subscribe_object_class_directed_interactions(self, object_class: Any, interaction_classes: Any) -> None:
        for interaction_class in interaction_classes:
            self._transport.request(
                TransportRequest(
                    command="SUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS",
                    fields=(self._field_text(object_class), self._field_text(interaction_class)),
                )
            )

    def unsubscribe_object_class_directed_interactions(self, object_class: Any, interaction_classes: Any) -> None:
        del interaction_classes
        self._transport.request(
            TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_DIRECTED_INTERACTIONS", fields=(self._field_text(object_class),))
        )

    def unpublish_interaction_class(self, interaction_class: Any) -> None:
        try:
            self._transport.request(TransportRequest(command="UNPUBLISH_INTERACTION_CLASS", fields=(self._field_text(interaction_class),)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def unsubscribe_interaction_class(self, interaction_class: Any) -> None:
        self._transport.request(TransportRequest(command="UNSUBSCRIBE_INTERACTION_CLASS", fields=(self._field_text(interaction_class),)))

    def publish_object_class_attributes(self, object_class: Any, attributes: set[object]) -> None:
        try:
            self._transport.request(
                TransportRequest(command="PUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(self._field_text(object_class), self._encode_handle_set(attributes)))
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def subscribe_object_class_attributes(self, object_class: Any, attributes: set[object], update_rate_designator: str | None = None) -> None:
        command = "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_RATE" if update_rate_designator else "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES"
        if update_rate_designator:
            fields = (self._field_text(object_class), self._encode_handle_set(attributes), update_rate_designator)
        else:
            fields = (self._field_text(object_class), self._encode_handle_set(attributes))
        self._transport.request(TransportRequest(command=command, fields=fields))

    def enable_attribute_scope_advisory_switch(self) -> None:
        self._transport.request(TransportRequest(command="SET_ATTRIBUTE_SCOPE_ADVISORY_SWITCH", fields=("1",)))

    def subscribe_object_class_attributes_with_regions(self, object_class: Any, attribute_region_associations: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(self._field_text(object_class), self._encode_attribute_region_associations(attribute_region_associations), "1"),
            )
        )

    def subscribe_object_class_attributes_passively_with_regions(self, object_class: Any, attribute_region_associations: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(self._field_text(object_class), self._encode_attribute_region_associations(attribute_region_associations), "0"),
            )
        )

    def unpublish_object_class_attributes(self, object_class: Any, attributes: set[object]) -> None:
        self._transport.request(
            TransportRequest(command="UNPUBLISH_OBJECT_CLASS_ATTRIBUTES", fields=(self._field_text(object_class), self._encode_handle_set(attributes)))
        )

    def unsubscribe_object_class_attributes(self, object_class: Any, attributes: set[object]) -> None:
        self._transport.request(
            TransportRequest(command="UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES", fields=(self._field_text(object_class), self._encode_handle_set(attributes)))
        )

    def unsubscribe_object_class_attributes_with_regions(self, object_class: Any, attribute_region_associations: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="UNSUBSCRIBE_OBJECT_CLASS_ATTRIBUTES_WITH_REGIONS",
                fields=(self._field_text(object_class), self._encode_attribute_region_associations(attribute_region_associations)),
            )
        )

    def register_object_instance(self, object_class: Any, object_instance_name: str):
        return self._as_handle(
            ObjectInstanceHandle,
            self._transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE", fields=(self._field_text(object_class), object_instance_name))).fields[0],
        )

    def register_object_instance_with_regions(self, object_class: Any, attribute_region_associations: Any, object_instance_name: str | None = None):
        fields = [self._field_text(object_class), self._encode_attribute_region_associations(attribute_region_associations)]
        if object_instance_name is not None:
            fields.append(object_instance_name)
        return self._as_handle(
            ObjectInstanceHandle,
            self._transport.request(TransportRequest(command="REGISTER_OBJECT_INSTANCE_WITH_REGIONS", fields=tuple(fields))).fields[0],
        )

    def reserve_object_instance_name(self, object_instance_name: str) -> None:
        self._transport.request(TransportRequest(command="RESERVE_OBJECT_INSTANCE_NAME", fields=(object_instance_name,)))

    def release_object_instance_name(self, object_instance_name: str) -> None:
        self._transport.request(TransportRequest(command="RELEASE_OBJECT_INSTANCE_NAME", fields=(object_instance_name,)))

    def reserve_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self._transport.request(
            TransportRequest(command="RESERVE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(",".join(sorted(object_instance_names)),))
        )

    def release_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self._transport.request(
            TransportRequest(command="RELEASE_MULTIPLE_OBJECT_INSTANCE_NAMES", fields=(",".join(sorted(object_instance_names)),))
        )

    def create_region(self, dimensions: Any):
        return self._as_handle(
            RegionHandle,
            self._transport.request(
                TransportRequest(command="CREATE_REGION", fields=(",".join(sorted(self._field_text(dimension) for dimension in dimensions)),))
            ).fields[0],
        )

    def set_range_bounds(self, region_handle: Any, dimension_handle: Any, range_bounds: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="SET_RANGE_BOUNDS",
                fields=(self._field_text(region_handle), self._field_text(dimension_handle), f"{int(range_bounds.lower)}:{int(range_bounds.upper)}"),
            )
        )

    def commit_region_modifications(self, region_handles: Any) -> None:
        self._transport.request(
            TransportRequest(command="COMMIT_REGION_MODIFICATIONS", fields=(",".join(sorted(self._field_text(region) for region in region_handles)),))
        )

    def delete_region(self, region_handle: Any) -> None:
        self._transport.request(TransportRequest(command="DELETE_REGION", fields=(self._field_text(region_handle),)))

    def associate_regions_for_updates(self, object_instance: Any, attribute_region_associations: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="ASSOCIATE_REGIONS_FOR_UPDATES",
                fields=(self._field_text(object_instance), self._encode_attribute_region_associations(attribute_region_associations)),
            )
        )

    def unassociate_regions_for_updates(self, object_instance: Any, attribute_region_associations: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="UNASSOCIATE_REGIONS_FOR_UPDATES",
                fields=(self._field_text(object_instance), self._encode_attribute_region_associations(attribute_region_associations)),
            )
        )

    def request_attribute_value_update_with_regions(self, object_instance: Any, attribute_region_associations: Any, user_supplied_tag: bytes) -> None:
        attributes = {
            attribute
            for association in attribute_region_associations
            for attribute in getattr(association, "attributes", association[0])
        }
        self.request_attribute_value_update(object_instance, attributes, user_supplied_tag)

    def subscribe_interaction_class_with_regions(self, interaction_class: Any, regions: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                fields=(self._field_text(interaction_class), "1", self._encode_region_set(regions)),
            )
        )

    def subscribe_interaction_class_passively_with_regions(self, interaction_class: Any, regions: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="SUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                fields=(self._field_text(interaction_class), "0", self._encode_region_set(regions)),
            )
        )

    def unsubscribe_interaction_class_with_regions(self, interaction_class: Any, regions: Any) -> None:
        self._transport.request(
            TransportRequest(
                command="UNSUBSCRIBE_INTERACTION_CLASS_WITH_REGIONS",
                fields=(self._field_text(interaction_class), self._encode_region_set(regions)),
            )
        )

    def _dispatch_transport_callback(self, parts: list[str]) -> bool:
        if self._federate is None or not parts:
            return False
        kind = parts[0]
        if kind == "DIRECTED_INTERACTION":
            parameter_values: dict[ParameterHandle, bytes] = {}
            if len(parts) > 3 and parts[3]:
                for item in parts[3].split(","):
                    if not item:
                        continue
                    handle_raw, value_raw = item.split(":", 1)
                    parameter_values[self._as_handle(ParameterHandle, handle_raw)] = bytes.fromhex(value_raw)
            getattr(self._federate, "receiveDirectedInteraction")(
                self._as_handle(InteractionClassHandle, parts[1]),
                self._as_handle(ObjectInstanceHandle, parts[2]),
                parameter_values,
                bytes.fromhex(parts[4]),
                self._as_handle(TransportationTypeHandle, parts[5]),
                self._as_handle(FederateHandle, parts[6]),
            )
            return True
        if kind == "DIRECTED_INTERACTION_TSO":
            parameter_values: dict[ParameterHandle, bytes] = {}
            if len(parts) > 3 and parts[3]:
                for item in parts[3].split(","):
                    if not item:
                        continue
                    handle_raw, value_raw = item.split(":", 1)
                    parameter_values[self._as_handle(ParameterHandle, handle_raw)] = bytes.fromhex(value_raw)
            getattr(self._federate, "receiveDirectedInteraction")(
                self._as_handle(InteractionClassHandle, parts[1]),
                self._as_handle(ObjectInstanceHandle, parts[2]),
                parameter_values,
                bytes.fromhex(parts[4]),
                self._as_handle(TransportationTypeHandle, parts[5]),
                self._as_handle(FederateHandle, parts[6]),
                self._decode_time(parts[7], parts[8]),
                OrderType.TIMESTAMP,
                OrderType.TIMESTAMP,
                self._as_handle(MessageRetractionHandle, parts[9]),
            )
            return True
        if kind == "OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED":
            getattr(self._federate, "objectInstanceNameReservationSucceeded")(parts[1])
            return True
        if kind == "OBJECT_INSTANCE_NAME_RESERVATION_FAILED":
            getattr(self._federate, "objectInstanceNameReservationFailed")(parts[1])
            return True
        if kind == "CONNECTION_LOST":
            getattr(self._federate, "connectionLost")(parts[1])
            return True
        if kind == "FEDERATE_RESIGNED":
            getattr(self._federate, "federateResigned")(parts[1])
            return True
        if kind == "REPORT_FEDERATION_EXECUTIONS":
            report = FederationExecutionInformationSet()
            if len(parts) > 1 and parts[1]:
                for item in parts[1].split(";"):
                    federation_name, logical_time_name = item.split(":", 1)
                    report.add(
                        FederationExecutionInformation(
                            federationExecutionName=federation_name,
                            logicalTimeImplementationName=logical_time_name,
                        )
                    )
            getattr(self._federate, "reportFederationExecutions")(report)
            return True
        if kind == "REPORT_FEDERATION_EXECUTION_MEMBERS":
            report = FederationExecutionMemberInformationSet()
            if len(parts) > 2 and parts[2]:
                for item in parts[2].split(";"):
                    federate_name, federate_type = item.split(":", 1)
                    report.add(
                        FederationExecutionMemberInformation(
                            federateName=federate_name,
                            federateType=federate_type,
                        )
                    )
            getattr(self._federate, "reportFederationExecutionMembers")(parts[1], report)
            return True
        if kind == "REPORT_FEDERATION_EXECUTION_DOES_NOT_EXIST":
            getattr(self._federate, "reportFederationExecutionDoesNotExist")(parts[1])
            return True
        if kind == "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_SUCCEEDED":
            getattr(self._federate, "multipleObjectInstanceNameReservationSucceeded")({name for name in parts[1].split(",") if name})
            return True
        if kind == "MULTIPLE_OBJECT_INSTANCE_NAME_RESERVATION_FAILED":
            getattr(self._federate, "multipleObjectInstanceNameReservationFailed")({name for name in parts[1].split(",") if name})
            return True
        if kind == "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE":
            getattr(self._federate, "turnUpdatesOnForObjectInstance")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "TURN_UPDATES_ON_FOR_OBJECT_INSTANCE_WITH_RATE":
            getattr(self._federate, "turnUpdatesOnForObjectInstance")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                parts[3],
            )
            return True
        if kind == "TURN_UPDATES_OFF_FOR_OBJECT_INSTANCE":
            getattr(self._federate, "turnUpdatesOffForObjectInstance")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "ATTRIBUTES_IN_SCOPE":
            getattr(self._federate, "attributesInScope")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "ATTRIBUTES_OUT_OF_SCOPE":
            getattr(self._federate, "attributesOutOfScope")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "CONFIRM_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE":
            getattr(self._federate, "confirmAttributeTransportationTypeChange")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                self._as_handle(TransportationTypeHandle, parts[3]),
            )
            return True
        if kind == "REPORT_ATTRIBUTE_TRANSPORTATION_TYPE":
            getattr(self._federate, "reportAttributeTransportationType")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                self._as_handle(AttributeHandle, parts[2]),
                self._as_handle(TransportationTypeHandle, parts[3]),
            )
            return True
        if kind == "CONFIRM_INTERACTION_TRANSPORTATION_TYPE_CHANGE":
            getattr(self._federate, "confirmInteractionTransportationTypeChange")(
                self._as_handle(InteractionClassHandle, parts[1]),
                self._as_handle(TransportationTypeHandle, parts[2]),
            )
            return True
        if kind == "REPORT_INTERACTION_TRANSPORTATION_TYPE":
            getattr(self._federate, "reportInteractionTransportationType")(
                self._as_handle(FederateHandle, parts[1]),
                self._as_handle(InteractionClassHandle, parts[2]),
                self._as_handle(TransportationTypeHandle, parts[3]),
            )
            return True
        if kind == "OWNERSHIP_ACQUIRED":
            getattr(self._federate, "attributeOwnershipAcquisitionNotification")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                bytes.fromhex(parts[3]),
            )
            return True
        if kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE":
            getattr(self._federate, "attributeOwnershipUnavailable")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                bytes.fromhex(parts[3]),
            )
            return True
        if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION":
            getattr(self._federate, "requestAttributeOwnershipAssumption")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                bytes.fromhex(parts[3]),
            )
            return True
        if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE":
            getattr(self._federate, "requestAttributeOwnershipRelease")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                bytes.fromhex(parts[3]),
            )
            return True
        if kind == "REQUEST_DIVESTITURE_CONFIRMATION":
            getattr(self._federate, "requestDivestitureConfirmation")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                bytes.fromhex(parts[3]),
            )
            return True
        if kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION":
            getattr(self._federate, "confirmAttributeOwnershipAcquisitionCancellation")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "INFORM_ATTRIBUTE_OWNERSHIP":
            getattr(self._federate, "informAttributeOwnership")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
                self._as_handle(FederateHandle, parts[3]),
            )
            return True
        if kind == "ATTRIBUTE_IS_NOT_OWNED":
            getattr(self._federate, "attributeIsNotOwned")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "ATTRIBUTE_IS_OWNED_BY_RTI":
            getattr(self._federate, "attributeIsOwnedByRTI")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                {self._as_handle(AttributeHandle, value) for value in parts[2].split(",") if value},
            )
            return True
        if kind == "REMOVE_OBJECT_INSTANCE" and len(parts) >= 4:
            getattr(self._federate, "removeObjectInstance")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                bytes.fromhex(parts[2]),
                OrderType.RECEIVE,
                SimpleNamespace(producing_federate=self._as_handle(FederateHandle, parts[3])),
            )
            return True
        if kind == "REMOVE_OBJECT_INSTANCE_TSO" and len(parts) >= 8:
            getattr(self._federate, "removeObjectInstance")(
                self._as_handle(ObjectInstanceHandle, parts[1]),
                bytes.fromhex(parts[2]),
                self._as_handle(FederateHandle, parts[7]),
                self._decode_time(parts[3], parts[4]),
                decode_order(parts[5]),
                decode_order(parts[6]),
                MessageRetractionHandle(int(parts[8])) if len(parts) >= 9 else None,
            )
            return True
        return False

    def change_attribute_order_type(self, object_instance: Any, attributes: set[object], order_type: Any) -> None:
        order_name = order_type.name if isinstance(order_type, OrderType) else getattr(order_type, "name", str(order_type))
        for attribute in attributes:
            self._transport.request(
                TransportRequest(
                    command="CHANGE_ATTRIBUTE_ORDER_TYPE",
                    fields=(self._field_text(object_instance), self._field_text(attribute), order_name),
                )
            )

    def update_attribute_values(self, object_instance: Any, attribute_values: dict[object, bytes], user_supplied_tag: bytes, logical_time: Any = None) -> Any | None:
        encoded_attributes = self._encode_parameter_values(attribute_values)
        try:
            if logical_time is None:
                self._transport.request(
                    TransportRequest(command="UPDATE_ATTRIBUTE_VALUES", fields=(self._field_text(object_instance), encoded_attributes, user_supplied_tag.hex()))
                )
                return None
            kind, scalar = self._time_kind_and_value(logical_time)
            self._logical_time_hint = kind
            response = self._transport.request(
                TransportRequest(
                    command="UPDATE_ATTRIBUTE_VALUES_TIMESTAMP",
                    fields=(self._field_text(object_instance), encoded_attributes, user_supplied_tag.hex(), kind, scalar),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)
        if not response.fields:
            return None
        return SimpleNamespace(handle=MessageRetractionHandle(int(response.fields[0])))

    def enable_callbacks(self) -> None:
        self._transport.request(TransportRequest(command="ENABLE_CALLBACKS"))

    def disable_callbacks(self) -> None:
        self._transport.request(TransportRequest(command="DISABLE_CALLBACKS"))

    def enable_time_regulation(self, lookahead: Any) -> None:
        kind, scalar = self._time_kind_and_value(lookahead)
        self._transport.request(TransportRequest(command="ENABLE_TIME_REGULATION", fields=(kind.replace("Time", "Interval"), scalar)))

    def enable_time_constrained(self) -> None:
        self._transport.request(TransportRequest(command="ENABLE_TIME_CONSTRAINED"))

    def disable_time_regulation(self) -> None:
        self._transport.request(TransportRequest(command="DISABLE_TIME_REGULATION"))

    def disable_time_constrained(self) -> None:
        self._transport.request(TransportRequest(command="DISABLE_TIME_CONSTRAINED"))

    def enable_asynchronous_delivery(self) -> None:
        self._transport.request(TransportRequest(command="ENABLE_ASYNCHRONOUS_DELIVERY"))

    def disable_asynchronous_delivery(self) -> None:
        self._transport.request(TransportRequest(command="DISABLE_ASYNCHRONOUS_DELIVERY"))

    def modify_lookahead(self, lookahead: Any) -> None:
        kind, scalar = self._time_kind_and_value(lookahead)
        self._transport.request(TransportRequest(command="MODIFY_LOOKAHEAD", fields=(kind.replace("Time", "Interval"), scalar)))

    def query_lookahead(self):
        try:
            kind, scalar = self._transport.request(TransportRequest(command="QUERY_LOOKAHEAD")).fields
        except TransportError as exc:
            self._remap_transport_error(exc)
        return self._decode_interval(kind, scalar)

    def get_update_rate_value(self, update_rate_designator: str) -> float:
        return float(self._transport.request(TransportRequest(command="GET_UPDATE_RATE_VALUE", fields=(update_rate_designator,))).fields[0])

    def change_interaction_order_type(self, interaction_class: Any, order_type: Any) -> None:
        order_name = order_type.name if isinstance(order_type, OrderType) else getattr(order_type, "name", str(order_type))
        self._transport.request(TransportRequest(command="CHANGE_INTERACTION_ORDER_TYPE", fields=(self._field_text(interaction_class), order_name)))

    def time_advance_request_available(self, logical_time: Any) -> None:
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        self._transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST_AVAILABLE", fields=(kind, scalar)))

    def time_advance_request(self, logical_time: Any) -> None:
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        self._transport.request(TransportRequest(command="TIME_ADVANCE_REQUEST", fields=(kind, scalar)))

    def next_message_request(self, logical_time: Any) -> None:
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        self._transport.request(TransportRequest(command="NEXT_MESSAGE_REQUEST", fields=(kind, scalar)))

    def next_message_request_available(self, logical_time: Any) -> None:
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        self._transport.request(TransportRequest(command="NEXT_MESSAGE_REQUEST_AVAILABLE", fields=(kind, scalar)))

    def retract(self, retraction_handle: Any) -> None:
        try:
            self._transport.request(TransportRequest(command="RETRACT", fields=(self._field_text(retraction_handle),)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def query_logical_time(self):
        kind, scalar = self._transport.request(TransportRequest(command="QUERY_LOGICAL_TIME")).fields
        return self._decode_time(kind, scalar)

    def query_galt(self) -> TimeQueryReturn:
        valid, kind, scalar = self._transport.request(TransportRequest(command="QUERY_GALT")).fields
        return TimeQueryReturn(bool(int(valid)), self._decode_time(kind, scalar))

    def query_lits(self) -> TimeQueryReturn:
        valid, kind, scalar = self._transport.request(TransportRequest(command="QUERY_LITS")).fields
        return TimeQueryReturn(bool(int(valid)), self._decode_time(kind, scalar))

    def get_object_instance_handle(self, object_instance_name: str):
        try:
            return self._as_handle(
                ObjectInstanceHandle,
                self._transport.request(TransportRequest(command="GET_OBJECT_INSTANCE_HANDLE", fields=(object_instance_name,))).fields[0],
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def get_known_object_class_handle(self, object_instance: Any):
        try:
            return self._as_handle(
                ObjectClassHandle,
                self._transport.request(TransportRequest(command="GET_KNOWN_OBJECT_CLASS_HANDLE", fields=(self._field_text(object_instance),))).fields[0],
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def delete_object_instance(self, object_instance: Any, user_supplied_tag: bytes, time: Any | None = None) -> Any | None:
        fields = [self._field_text(object_instance), user_supplied_tag.hex()]
        command = "DELETE_OBJECT_INSTANCE"
        if time is not None:
            kind, scalar = self._time_kind_and_value(time)
            self._logical_time_hint = kind
            command = "DELETE_OBJECT_INSTANCE_TIMESTAMP"
            fields.extend((kind, scalar))
        try:
            response = self._transport.request(TransportRequest(command=command, fields=tuple(fields)))
        except TransportError as exc:
            self._remap_transport_error(exc)
        if time is None or not response.fields:
            return None
        return SimpleNamespace(handle=MessageRetractionHandle(int(response.fields[0])))

    def local_delete_object_instance(self, object_instance: Any) -> None:
        try:
            self._transport.request(TransportRequest(command="LOCAL_DELETE_OBJECT_INSTANCE", fields=(self._field_text(object_instance),)))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def request_attribute_value_update(self, object_or_class: Any, attributes: set[object], user_supplied_tag: bytes) -> None:
        command = "REQUEST_ATTRIBUTE_VALUE_UPDATE_CLASS"
        if isinstance(object_or_class, ObjectInstanceHandle):
            command = "REQUEST_ATTRIBUTE_VALUE_UPDATE_OBJECT"
        fields = (self._field_text(object_or_class), self._encode_handle_set(attributes), user_supplied_tag.hex())
        try:
            self._transport.request(TransportRequest(command=command, fields=fields))
        except TransportError as exc:
            self._remap_transport_error(exc)

    def request_attribute_transportation_type_change(self, object_instance: Any, attributes: set[object], transportation_type: Any) -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="REQUEST_ATTRIBUTE_TRANSPORTATION_TYPE_CHANGE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), self._field_text(transportation_type)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def query_attribute_transportation_type(self, object_instance: Any, attribute: Any) -> None:
        try:
            self._transport.request(
                TransportRequest(command="QUERY_ATTRIBUTE_TRANSPORTATION_TYPE", fields=(self._field_text(object_instance), self._field_text(attribute)))
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def request_interaction_transportation_type_change(self, interaction_class: Any, transportation_type: Any) -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="REQUEST_INTERACTION_TRANSPORTATION_TYPE_CHANGE",
                    fields=(self._field_text(interaction_class), self._field_text(transportation_type)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def query_interaction_transportation_type(self, interaction_class: Any) -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="QUERY_INTERACTION_TRANSPORTATION_TYPE",
                    fields=(self._field_text(self._joined_handle), self._field_text(interaction_class)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def unconditional_attribute_ownership_divestiture(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def attribute_ownership_acquisition_if_available(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def attribute_ownership_acquisition(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def negotiated_attribute_ownership_divestiture(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def confirm_divestiture(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="CONFIRM_DIVESTITURE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def cancel_negotiated_attribute_ownership_divestiture(self, object_instance: Any, attributes: set[object]) -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def cancel_attribute_ownership_acquisition(self, object_instance: Any, attributes: set[object]) -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def attribute_ownership_release_denied(self, object_instance: Any, attributes: set[object], user_supplied_tag: bytes = b"") -> None:
        try:
            self._transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_RELEASE_DENIED",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes), user_supplied_tag.hex()),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def attribute_ownership_divestiture_if_wanted(self, object_instance: Any, attributes: set[object]):
        try:
            fields = self._transport.request(
                TransportRequest(
                    command="ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED",
                    fields=(self._field_text(object_instance), self._encode_handle_set(attributes)),
                )
            ).fields
        except TransportError as exc:
            self._remap_transport_error(exc)
        return {self._as_handle(AttributeHandle, value) for value in fields if value}

    def query_attribute_ownership(self, object_instance: Any, attribute: Any) -> None:
        normalized_attributes = attribute
        if isinstance(attribute, (set, frozenset, list, tuple)):
            normalized_attributes = next(iter(attribute), "")
        if normalized_attributes in ("", None):
            return
        try:
            self._transport.request(
                TransportRequest(
                    command="QUERY_ATTRIBUTE_OWNERSHIP",
                    fields=(self._field_text(object_instance), self._field_text(normalized_attributes)),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def is_attribute_owned_by_federate(self, object_instance: Any, attribute: Any) -> bool:
        try:
            return bool(
                int(
                    self._transport.request(
                        TransportRequest(
                            command="IS_ATTRIBUTE_OWNED_BY_FEDERATE",
                            fields=(self._field_text(object_instance), self._field_text(attribute)),
                        )
                    ).fields[0]
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def send_interaction(self, interaction_class: Any, parameter_values: dict[object, bytes], user_supplied_tag: bytes, logical_time: Any = None) -> Any | None:
        encoded_parameters = self._encode_parameter_values(parameter_values)
        if logical_time is None:
            try:
                self._transport.request(
                    TransportRequest(command="SEND_INTERACTION", fields=(self._field_text(interaction_class), encoded_parameters, user_supplied_tag.hex()))
                )
            except TransportError as exc:
                self._remap_transport_error(exc)
            return None
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        try:
            response = self._transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_TIMESTAMP",
                    fields=(self._field_text(interaction_class), encoded_parameters, user_supplied_tag.hex(), kind, scalar),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)
        if not response.fields:
            return None
        return SimpleNamespace(handle=MessageRetractionHandle(int(response.fields[0])))

    def send_interaction_with_regions(
        self,
        interaction_class: Any,
        parameter_values: dict[object, bytes],
        regions: Any,
        user_supplied_tag: bytes,
        logical_time: Any = None,
    ) -> None:
        encoded_parameters = self._encode_parameter_values(parameter_values)
        encoded_regions = self._encode_region_set(regions)
        if logical_time is None:
            self._transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS",
                    fields=(self._field_text(interaction_class), encoded_parameters, encoded_regions, user_supplied_tag.hex()),
                )
            )
            return
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        try:
            self._transport.request(
                TransportRequest(
                    command="SEND_INTERACTION_WITH_REGIONS_TIMESTAMP",
                    fields=(self._field_text(interaction_class), encoded_parameters, encoded_regions, user_supplied_tag.hex(), kind, scalar),
                )
            )
        except TransportError as exc:
            self._remap_transport_error(exc)

    def send_directed_interaction(
        self,
        interaction_class: Any,
        object_instance: Any,
        parameter_values: dict[object, bytes],
        user_supplied_tag: bytes,
        logical_time: Any = None,
    ):
        encoded_parameters = self._encode_parameter_values(parameter_values)
        if logical_time is None:
            self._transport.request(
                TransportRequest(
                    command="SEND_DIRECTED_INTERACTION",
                    fields=(self._field_text(interaction_class), self._field_text(object_instance), encoded_parameters, user_supplied_tag.hex()),
                )
            )
            return SimpleNamespace(retractionHandleIsValid=False, handle=None)
        kind, scalar = self._time_kind_and_value(logical_time)
        self._logical_time_hint = kind
        handle = self._transport.request(
            TransportRequest(
                command="SEND_DIRECTED_INTERACTION_TIMESTAMP",
                fields=(self._field_text(interaction_class), self._field_text(object_instance), encoded_parameters, user_supplied_tag.hex(), kind, scalar),
            )
        ).fields[0]
        return SimpleNamespace(retractionHandleIsValid=True, handle=self._as_handle(MessageRetractionHandle, handle))

    def evoke_callback(self, seconds: float = 0.0) -> bool:
        del seconds
        fields = self._transport.request(TransportRequest(command="EVOKE")).fields
        if not fields:
            return False
        if fields[0] != "1":
            return False
        if self._dispatch_transport_callback(list(fields[1:])):
            return True
        dispatch_fedpro_helper_callback(self._federate, list(fields[1:]), logical_time_hint=self._logical_time_hint)
        return True

    def evoke_multiple_callbacks(self, min_seconds: float = 0.0, max_seconds: float = 0.1) -> bool:
        del min_seconds, max_seconds
        delivered = False
        for _ in range(8):
            if not self.evoke_callback():
                break
            delivered = True
        return delivered

    def close(self) -> None:
        close = getattr(self._transport, "close", None)
        if callable(close):
            close()


__all__ = ["FedPro2025RTIAmbassador", "dispatch_fedpro_helper_callback", "resolve_fedpro_fom_path"]
