"""IEEE 1516.1-2025 RTI shim backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Mapping

from hla.rti.plugin_api import BackendRequest
from hla.rti1516_2025.datatypes import (
    ConfigurationResult,
    FederationExecutionInformation,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformation,
    FederationExecutionMemberInformationSet,
    TimeQueryReturn,
)
from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel, OrderType, ResignAction, ServiceGroup
from hla.rti1516_2025.exceptions import (
    AlreadyConnected,
    AttributeAcquisitionWasNotRequested,
    AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested,
    AttributeAlreadyOwned,
    AttributeDivestitureWasNotRequested,
    AttributeNotDefined,
    AttributeNotOwned,
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFOM,
    CouldNotOpenMIM,
    DesignatorIsHLAstandardMIM,
    ErrorReadingFOM,
    ErrorReadingMIM,
    FederateAlreadyExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InconsistentFOM,
    InvalidAttributeHandle,
    InvalidCredentials,
    InvalidDimensionHandle,
    InvalidFederateHandle,
    InvalidFOM,
    InvalidInteractionClassHandle,
    InvalidLogicalTime,
    InvalidLookahead,
    InvalidMIM,
    InvalidObjectClassHandle,
    InvalidObjectInstanceHandle,
    InvalidOrderType,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationTypeHandle,
    LogicalTimeAlreadyPassed,
    NameNotFound,
    NoAcquisitionPending,
    NotConnected,
    ObjectClassNotDefined,
    ObjectInstanceNameInUse,
    RTIinternalError,
    TimeRegulationIsNotEnabled,
    Unauthorized,
    UnsupportedCallbackModel,
)
from hla.rti1516_2025.federate_ambassador import FederateAmbassador
from hla.rti1516_2025.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)

_DEFAULT_LOGICAL_TIME_IMPLEMENTATION = "HLAinteger64Time"
_SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS = frozenset(
    {
        "HLAinteger64Time",
        "HLAfloat64Time",
    }
)
_SWITCH_DEFAULTS = {
    "object_class_relevance_advisory": False,
    "attribute_relevance_advisory": False,
    "attribute_scope_advisory": False,
    "interaction_relevance_advisory": False,
    "convey_region_designator_sets": True,
    "service_reporting": False,
    "exception_reporting": True,
    "send_service_reports_to_file": False,
    "auto_provide": True,
    "delay_subscription_evaluation": False,
    "advisories_use_known_class": True,
    "allow_relaxed_ddm": False,
    "non_regulated_grant": False,
}


@dataclass(slots=True)
class _FederationRecord:
    logical_time_implementation_name: str = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    fom_modules: tuple[Any, ...] = ()
    mim_module: Any | None = None
    fom_catalog: Any | None = None
    members: dict[str, str] = field(default_factory=dict)
    member_handles: dict[str, FederateHandle] = field(default_factory=dict)
    member_ambassadors: dict[int, FederateAmbassador] = field(default_factory=dict)
    object_instances: dict[int, "_ObjectInstanceRecord"] = field(default_factory=dict)
    object_instance_names: dict[str, int] = field(default_factory=dict)
    next_object_instance_handle: int = 1


@dataclass(slots=True)
class _ObjectInstanceRecord:
    object_class_name: str
    object_instance_name: str | None
    attribute_owners: dict[str, FederateHandle | None] = field(default_factory=dict)
    attribute_divesting: set[str] = field(default_factory=set)
    attribute_candidates: dict[str, list[tuple[FederateHandle, bytes]]] = field(default_factory=dict)


_FEDERATION_REGISTRY: dict[str, _FederationRecord] = {}


@dataclass(frozen=True, slots=True)
class ShimBackendInfo:
    name: str = "shim-2025"
    kind: str = "shim/2025"
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=lambda: {"spec": "rti1516_2025"})


class Shim2025RTIAmbassador:
    """Minimal 2025 RTI ambassador for factory and adapter development."""

    backend_info = ShimBackendInfo()

    def __init__(self) -> None:
        self._connected = False
        self._joined = False
        self._federation_name: str | None = None
        self._federate_name: str | None = None
        self._federate_handle: FederateHandle | None = None
        self._federate_ambassador: FederateAmbassador | None = None
        self._callback_model: CallbackModel | None = None
        self._logical_time_implementation_name = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        self._logical_time_factory = self._get_time_factory(_DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False
        self._switches = dict(_SWITCH_DEFAULTS)
        self._default_attribute_transportation: dict[tuple[str, str], str] = {}
        self._default_attribute_order: dict[tuple[str, str], OrderType] = {}
        self._service_report_serial_number = 0
        self._service_report_records: list[dict[str, Any]] = []
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def joined(self) -> bool:
        return self._joined

    def connect(
        self,
        federateAmbassador: FederateAmbassador,
        callbackModel: CallbackModel,
        configuration: Any | None = None,
        credentials: Any | None = None,
    ) -> ConfigurationResult:
        self._record("connect", federateAmbassador, callbackModel, configuration, credentials)
        if self._connected:
            raise AlreadyConnected("2025 shim RTI ambassador is already connected")
        callbackModel = self._coerce_callback_model(callbackModel)
        self._validate_credentials(credentials)
        self._connected = True
        self._federate_ambassador = federateAmbassador
        self._callback_model = callbackModel
        return ConfigurationResult(
            configurationUsed=configuration is not None,
            addressUsed=False,
            additionalSettingsResultCode=AdditionalSettingsResultCode.SETTINGS_IGNORED,
            message="hla-backend-shim accepted the 2025 connection request",
        )

    def disconnect(self) -> None:
        self._record("disconnect")
        if not self._connected:
            raise NotConnected("2025 shim RTI ambassador is not connected")
        self._release_join()
        self._connected = False
        self._joined = False
        self._federation_name = None
        self._federate_name = None
        self._federate_handle = None
        self._federate_ambassador = None
        self._callback_model = None
        self._logical_time_implementation_name = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        self._logical_time_factory = self._get_time_factory(_DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False
        self._switches = dict(_SWITCH_DEFAULTS)
        self._default_attribute_transportation.clear()
        self._default_attribute_order.clear()
        self._service_report_serial_number = 0
        self._service_report_records.clear()

    def createFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecution", *args, **kwargs)
        self._require_connected("createFederationExecution")
        federation_name = self._extract_create_federation_name(args, kwargs)
        if federation_name in _FEDERATION_REGISTRY:
            raise FederationExecutionAlreadyExists(federation_name)
        fom_sources = self._extract_fom_sources(args, kwargs, with_mim=False)
        if not fom_sources:
            raise InvalidFOM("At least one FOM module designator is required")
        logical_time_name = self._extract_logical_time_implementation_name(args, kwargs)
        resolved_foms = self._resolve_fom_modules(fom_sources, mim=False)
        mim_module = self._standard_mim_module()
        fom_catalog = self._merge_fom_modules(resolved_foms, mim_module=mim_module)
        _FEDERATION_REGISTRY[federation_name] = _FederationRecord(
            logical_time_implementation_name=logical_time_name,
            fom_modules=resolved_foms,
            mim_module=mim_module,
            fom_catalog=fom_catalog,
        )
        self._select_logical_time_implementation(logical_time_name)

    def createFederationExecutionWithMIM(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecutionWithMIM", *args, **kwargs)
        self._require_connected("createFederationExecutionWithMIM")
        federation_name = self._extract_create_federation_name(args, kwargs)
        if federation_name in _FEDERATION_REGISTRY:
            raise FederationExecutionAlreadyExists(federation_name)
        fom_sources = self._extract_fom_sources(args, kwargs, with_mim=True)
        if not fom_sources:
            raise InvalidFOM("At least one FOM module designator is required")
        mim_source = self._extract_mim_source(args, kwargs)
        if mim_source in {"HLAstandardMIM", "HLAstandardMIM.xml"}:
            raise DesignatorIsHLAstandardMIM("Explicit MIM designator shall not be HLAstandardMIM")
        if mim_source is None:
            raise InvalidMIM("Explicit createFederationExecutionWithMIM requires a MIM module designator")
        logical_time_name = self._extract_logical_time_implementation_name(args, kwargs)
        resolved_foms = self._resolve_fom_modules(fom_sources, mim=False)
        resolved_mim = self._resolve_fom_modules((mim_source,), mim=True)[0]
        fom_catalog = self._merge_fom_modules(resolved_foms, mim_module=resolved_mim)
        _FEDERATION_REGISTRY[federation_name] = _FederationRecord(
            logical_time_implementation_name=logical_time_name,
            fom_modules=resolved_foms,
            mim_module=resolved_mim,
            fom_catalog=fom_catalog,
        )
        self._select_logical_time_implementation(logical_time_name)

    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("destroyFederationExecution", *args, **kwargs)
        self._require_connected("destroyFederationExecution")
        federation_name = self._extract_create_federation_name(args, kwargs)
        federation = _FEDERATION_REGISTRY.get(federation_name)
        if federation is None:
            raise FederationExecutionDoesNotExist(federation_name)
        if federation.members:
            raise FederatesCurrentlyJoined(federation_name)
        del _FEDERATION_REGISTRY[federation_name]

    def listFederationExecutions(self) -> None:  # noqa: N802
        self._record("listFederationExecutions")
        self._require_connected("listFederationExecutions")
        report = FederationExecutionInformationSet(
            FederationExecutionInformation(
                federationExecutionName=federation_name,
                logicalTimeImplementationName=record.logical_time_implementation_name,
            )
            for federation_name, record in sorted(_FEDERATION_REGISTRY.items())
        )
        self._deliver_callback("reportFederationExecutions", report)

    def listFederationExecutionMembers(self, federationName: str) -> None:  # noqa: N802
        self._record("listFederationExecutionMembers", federationName)
        self._require_connected("listFederationExecutionMembers")
        federation = _FEDERATION_REGISTRY.get(federationName)
        if federation is None:
            self._deliver_callback("reportFederationExecutionDoesNotExist", federationName)
            return
        report = FederationExecutionMemberInformationSet(
            FederationExecutionMemberInformation(federateName=name, federateType=federate_type) for name, federate_type in sorted(federation.members.items())
        )
        self._deliver_callback("reportFederationExecutionMembers", federationName, report)

    def joinFederationExecution(self, *args: Any, **kwargs: Any):  # noqa: N802
        self._record("joinFederationExecution", *args, **kwargs)
        self._require_connected("joinFederationExecution")
        federation_name, federate_name = self._extract_join_names(args, kwargs)
        federation = _FEDERATION_REGISTRY.get(federation_name)
        if federation is None:
            raise FederationExecutionDoesNotExist(federation_name)
        if self._joined:
            raise FederateAlreadyExecutionMember("2025 shim RTI ambassador is already joined")
        additional_fom_modules = self._extract_additional_fom_modules(args, kwargs)
        if additional_fom_modules:
            resolved_additional = self._resolve_fom_modules(additional_fom_modules, mim=False)
            federation.fom_catalog = self._merge_fom_modules(
                (*federation.fom_modules, *resolved_additional),
                mim_module=federation.mim_module,
            )
            federation.fom_modules = (*federation.fom_modules, *resolved_additional)
        if federate_name is not None and federate_name in federation.members:
            raise FederateNameAlreadyInUse(federate_name)
        federate_type = self._extract_federate_type(args, kwargs)
        if federate_name is None:
            federate_name = f"__anonymous_federate_{len(federation.member_handles) + 1}"
        federation.members[federate_name] = federate_type
        self._federate_handle = FederateHandle(len(federation.member_handles) + 1)
        federation.member_handles[federate_name] = self._federate_handle
        if self._federate_ambassador is not None:
            federation.member_ambassadors[self._federate_handle.value] = self._federate_ambassador
        self._select_logical_time_implementation(federation.logical_time_implementation_name)
        self._federation_name = federation_name
        self._federate_name = federate_name
        self._joined = True
        return self._federate_handle

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        self._record("resignFederationExecution", resignAction)
        self._require_joined("resignFederationExecution")
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "federateResigned"):
            self._deliver_callback("federateResigned", self._resign_reason_description(resignAction))
        self._release_join()
        self._joined = False
        self._federation_name = None
        self._federate_name = None
        self._federate_handle = None

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        self._record("evokeCallback", approximateMinimumTimeInSeconds)
        self._require_connected("evokeCallback")
        return False

    def evokeMultipleCallbacks(  # noqa: N802
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        self._record("evokeMultipleCallbacks", approximateMinimumTimeInSeconds, approximateMaximumTimeInSeconds)
        self._require_connected("evokeMultipleCallbacks")
        return False

    def enableCallbacks(self) -> None:  # noqa: N802
        self._record("enableCallbacks")
        self._require_connected("enableCallbacks")

    def disableCallbacks(self) -> None:  # noqa: N802
        self._record("disableCallbacks")
        self._require_connected("disableCallbacks")

    def enableTimeRegulation(self, lookahead: Any) -> None:  # noqa: N802
        self._record("enableTimeRegulation", lookahead)
        self._require_joined("enableTimeRegulation")
        self._lookahead = self._coerce_interval(lookahead)
        self._time_regulation_enabled = True
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "timeRegulationEnabled"):
            self._deliver_callback("timeRegulationEnabled", self._logical_time)

    def enableTimeConstrained(self) -> None:  # noqa: N802
        self._record("enableTimeConstrained")
        self._require_joined("enableTimeConstrained")
        self._time_constrained_enabled = True
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "timeConstrainedEnabled"):
            self._deliver_callback("timeConstrainedEnabled", self._logical_time)

    def timeAdvanceRequest(self, time: Any) -> None:  # noqa: N802
        self._record("timeAdvanceRequest", time)
        self._require_joined("timeAdvanceRequest")
        requested_time = self._coerce_time(time)
        if requested_time < self._logical_time:
            raise LogicalTimeAlreadyPassed(str(requested_time))
        self._logical_time = requested_time
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "timeAdvanceGrant"):
            self._deliver_callback("timeAdvanceGrant", self._logical_time)

    def flushQueueRequest(self, time: Any) -> None:  # noqa: N802
        self._record("flushQueueRequest", time)
        self._require_joined("flushQueueRequest")
        requested_time = self._coerce_time(time)
        if requested_time < self._logical_time:
            raise LogicalTimeAlreadyPassed(str(requested_time))
        self._logical_time = requested_time
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "flushQueueGrant"):
            self._deliver_callback("flushQueueGrant", self._logical_time, self._logical_time)

    def queryGALT(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryGALT")
        self._require_joined("queryGALT")
        return TimeQueryReturn(True, self._logical_time)

    def queryLogicalTime(self) -> Any:  # noqa: N802
        self._record("queryLogicalTime")
        self._require_joined("queryLogicalTime")
        return self._logical_time

    def queryLITS(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryLITS")
        self._require_joined("queryLITS")
        return TimeQueryReturn(True, self._logical_time)

    def modifyLookahead(self, lookahead: Any) -> None:  # noqa: N802
        self._record("modifyLookahead", lookahead)
        self._require_joined("modifyLookahead")
        if not self._time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Cannot modify lookahead before enableTimeRegulation")
        self._lookahead = self._coerce_interval(lookahead)

    def queryLookahead(self) -> Any:  # noqa: N802
        self._record("queryLookahead")
        self._require_joined("queryLookahead")
        if not self._time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Cannot query lookahead before enableTimeRegulation")
        return self._lookahead

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle:  # noqa: N802
        self._record("getObjectClassHandle", objectClassName)
        self._require_joined("getObjectClassHandle")
        if not isinstance(objectClassName, str):
            raise NameNotFound(repr(objectClassName))
        handles = self._object_class_handles()
        try:
            return ObjectClassHandle(handles[objectClassName])
        except KeyError as exc:
            raise NameNotFound(objectClassName) from exc

    def getObjectClassName(self, objectClass: Any) -> str:  # noqa: N802
        self._record("getObjectClassName", objectClass)
        return self._object_class_name(objectClass)

    def getAttributeHandle(self, objectClass: Any, attributeName: str) -> AttributeHandle:  # noqa: N802
        self._record("getAttributeHandle", objectClass, attributeName)
        object_class_name = self._object_class_name(objectClass)
        if not isinstance(attributeName, str):
            raise AttributeNotDefined(repr(attributeName))
        handles = self._attribute_handles(object_class_name)
        try:
            return AttributeHandle(handles[attributeName])
        except KeyError as exc:
            raise AttributeNotDefined(attributeName) from exc

    def getAttributeName(self, objectClass: Any, attribute: Any) -> str:  # noqa: N802
        self._record("getAttributeName", objectClass, attribute)
        object_class_name = self._object_class_name(objectClass)
        attribute_value = self._normalize_handle(attribute, AttributeHandle, InvalidAttributeHandle)
        names_by_handle = {value: name for name, value in self._attribute_handles(object_class_name).items()}
        try:
            return names_by_handle[attribute_value]
        except KeyError as exc:
            raise InvalidAttributeHandle(str(attribute)) from exc

    def getTransportationTypeHandle(self, transportationTypeName: str) -> TransportationTypeHandle:  # noqa: N802
        self._record("getTransportationTypeHandle", transportationTypeName)
        self._require_joined("getTransportationTypeHandle")
        if not isinstance(transportationTypeName, str):
            raise InvalidTransportationName(repr(transportationTypeName))
        handles = self._transportation_handles()
        try:
            return TransportationTypeHandle(handles[transportationTypeName])
        except KeyError as exc:
            raise InvalidTransportationName(transportationTypeName) from exc

    def getTransportationTypeName(self, transportationType: Any) -> str:  # noqa: N802
        self._record("getTransportationTypeName", transportationType)
        transportation_value = self._normalize_handle(
            transportationType,
            TransportationTypeHandle,
            InvalidTransportationTypeHandle,
        )
        names_by_handle = {value: name for name, value in self._transportation_handles().items()}
        try:
            return names_by_handle[transportation_value]
        except KeyError as exc:
            raise InvalidTransportationTypeHandle(str(transportationType)) from exc

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle:  # noqa: N802
        self._record("getDimensionHandle", dimensionName)
        self._require_joined("getDimensionHandle")
        if not isinstance(dimensionName, str):
            raise NameNotFound(repr(dimensionName))
        handles = self._dimension_handles()
        try:
            return DimensionHandle(handles[dimensionName])
        except KeyError as exc:
            raise NameNotFound(dimensionName) from exc

    def getDimensionName(self, dimension: Any) -> str:  # noqa: N802
        self._record("getDimensionName", dimension)
        dimension_value = self._normalize_handle(dimension, DimensionHandle, InvalidDimensionHandle)
        names_by_handle = {value: name for name, value in self._dimension_handles().items()}
        try:
            return names_by_handle[dimension_value]
        except KeyError as exc:
            raise InvalidDimensionHandle(str(dimension)) from exc

    def getDimensionUpperBound(self, dimension: Any) -> int:  # noqa: N802
        self._record("getDimensionUpperBound", dimension)
        dimension_name = self.getDimensionName(dimension)
        spec = self._dimension_spec(dimension_name)
        if spec is None or spec.upper_bound in {None, ""}:
            return 0
        try:
            return int(str(spec.upper_bound))
        except ValueError as exc:
            raise InvalidDimensionHandle(f"Dimension {dimension_name} has invalid upper bound {spec.upper_bound!r}") from exc

    def getAvailableDimensionsForObjectClass(self, objectClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForObjectClass", objectClass)
        self._object_class_name(objectClass)
        return {DimensionHandle(value) for value in self._dimension_handles().values()}

    def getAvailableDimensionsForInteractionClass(self, interactionClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForInteractionClass", interactionClass)
        self._interaction_class_name(interactionClass)
        return {DimensionHandle(value) for value in self._dimension_handles().values()}

    def changeDefaultAttributeTransportationType(  # noqa: N802
        self,
        objectClass: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("changeDefaultAttributeTransportationType", objectClass, attributes, transportationType)
        object_class_name = self._object_class_name(objectClass)
        transportation_name = self.getTransportationTypeName(transportationType)
        for attribute_name in self._attribute_names_from_handles(object_class_name, attributes):
            self._default_attribute_transportation[(object_class_name, attribute_name)] = transportation_name

    def changeDefaultAttributeOrderType(self, objectClass: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeDefaultAttributeOrderType", objectClass, attributes, orderType)
        object_class_name = self._object_class_name(objectClass)
        try:
            coerced_order = orderType if isinstance(orderType, OrderType) else OrderType(orderType)
        except Exception as exc:
            raise InvalidOrderType(repr(orderType)) from exc
        for attribute_name in self._attribute_names_from_handles(object_class_name, attributes):
            self._default_attribute_order[(object_class_name, attribute_name)] = coerced_order

    def defaultAttributePolicySnapshot(self) -> dict[str, dict[str, str]]:  # noqa: N802
        self._record("defaultAttributePolicySnapshot")
        self._require_joined("defaultAttributePolicySnapshot")
        return {
            "transportation": {
                f"{object_class}.{attribute}": transportation
                for (object_class, attribute), transportation in sorted(self._default_attribute_transportation.items())
            },
            "order": {f"{object_class}.{attribute}": order.name for (object_class, attribute), order in sorted(self._default_attribute_order.items())},
        }

    def serializeMOMServiceReport(  # noqa: N802
        self,
        serviceName: str,
        *,
        success: bool = True,
        exception: str | None = None,
        arguments: Mapping[str, Any] | None = None,
        returned: Mapping[str, Any] | None = None,
        result: Any = None,
    ) -> dict[str, Any]:
        self._record(
            "serializeMOMServiceReport",
            serviceName,
            success=success,
            exception=exception,
            arguments=arguments,
            returned=returned,
            result=result,
        )
        self._require_joined("serializeMOMServiceReport")
        if not isinstance(serviceName, str) or not serviceName:
            raise RTIinternalError("serializeMOMServiceReport requires a non-empty serviceName")
        self._service_report_serial_number += 1
        returned_payload: Mapping[str, Any] = returned or ({"value": result} if result is not None else {})
        record = {
            "recordType": "MOMServiceReport",
            "spec": "IEEE 1516.1-2025",
            "serialNumber": self._service_report_serial_number,
            "timestampUTC": datetime.now(timezone.utc).isoformat(),
            "federationName": self._federation_name,
            "federateName": self._federate_name,
            "federateHandle": self._federate_handle.value if self._federate_handle is not None else None,
            "service": serviceName,
            "success": bool(success),
            "exception": exception or "",
            "arguments": {str(key): self._safe_report_arg(value) for key, value in dict(arguments or {}).items()},
            "returned": {str(key): self._safe_report_arg(value) for key, value in dict(returned_payload).items()},
            "serviceReportingEnabled": self._switches["service_reporting"],
            "sendServiceReportsToFile": self._switches["send_service_reports_to_file"],
        }
        self._service_report_records.append(record)
        return dict(record)

    def serviceReportRecordsSnapshot(self) -> tuple[dict[str, Any], ...]:  # noqa: N802
        self._record("serviceReportRecordsSnapshot")
        self._require_joined("serviceReportRecordsSnapshot")
        return tuple(dict(record) for record in self._service_report_records)

    def registerObjectInstance(  # noqa: N802
        self,
        objectClass: Any,
        objectInstanceName: str | None = None,
    ) -> ObjectInstanceHandle:
        self._record("registerObjectInstance", objectClass, objectInstanceName)
        self._require_joined("registerObjectInstance")
        federation = self._federation_record()
        object_class_name = self._object_class_name(objectClass)
        if objectInstanceName is not None:
            if not isinstance(objectInstanceName, str) or not objectInstanceName:
                raise RTIinternalError("objectInstanceName must be a non-empty string when provided")
            if objectInstanceName in federation.object_instance_names:
                raise ObjectInstanceNameInUse(objectInstanceName)
        handle = ObjectInstanceHandle(federation.next_object_instance_handle)
        federation.next_object_instance_handle += 1
        attribute_owners = {attribute_name: self._federate_handle for attribute_name in self._attribute_handles(object_class_name)}
        federation.object_instances[handle.value] = _ObjectInstanceRecord(
            object_class_name=object_class_name,
            object_instance_name=objectInstanceName,
            attribute_owners=attribute_owners,
        )
        if objectInstanceName is not None:
            federation.object_instance_names[objectInstanceName] = handle.value
        return handle

    def unconditionalAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("unconditionalAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("unconditionalAttributeOwnershipDivestiture")
        record = self._object_instance_record(objectInstance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, attributes)
        for attribute_name in attribute_names:
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
        for attribute_name in attribute_names:
            candidate = self._pop_attribute_candidate(record, attribute_name)
            if candidate is None:
                record.attribute_owners[attribute_name] = None
                record.attribute_divesting.discard(attribute_name)
                continue
            new_owner, acquisition_tag = candidate
            record.attribute_owners[attribute_name] = new_owner
            record.attribute_divesting.discard(attribute_name)
            attribute_handle = AttributeHandle(self._attribute_handles(record.object_class_name)[attribute_name])
            self._deliver_to_federate_handle(new_owner, "attributeOwnershipAcquisitionNotification", objectInstance, {attribute_handle}, acquisition_tag)

    def negotiatedAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("negotiatedAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("negotiatedAttributeOwnershipDivestiture")
        record = self._object_instance_record(objectInstance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, attributes)
        for attribute_name in attribute_names:
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            if attribute_name in record.attribute_divesting:
                raise AttributeAlreadyBeingDivested(attribute_name)

        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        for attribute_name in attribute_names:
            candidate = self._pop_attribute_candidate(record, attribute_name)
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            if candidate is not None:
                new_owner, _candidate_tag = candidate
                record.attribute_owners[attribute_name] = new_owner
                record.attribute_divesting.discard(attribute_name)
                self._deliver_callback("requestDivestitureConfirmation", objectInstance, {attribute_handle}, bytes(userSuppliedTag))
                self._deliver_to_federate_handle(
                    new_owner,
                    "attributeOwnershipAcquisitionNotification",
                    objectInstance,
                    {attribute_handle},
                    bytes(userSuppliedTag),
                )
                continue

            record.attribute_divesting.add(attribute_name)
            for federate_handle in self._other_member_handles():
                self._deliver_to_federate_handle(
                    federate_handle,
                    "requestAttributeOwnershipAssumption",
                    objectInstance,
                    {attribute_handle},
                    bytes(userSuppliedTag),
                )

    def confirmDivestiture(self, objectInstance: Any, confirmedAttributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("confirmDivestiture", objectInstance, confirmedAttributes, userSuppliedTag)
        self._require_joined("confirmDivestiture")
        record = self._object_instance_record(objectInstance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, confirmedAttributes)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        for attribute_name in attribute_names:
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            if attribute_name not in record.attribute_divesting:
                raise AttributeDivestitureWasNotRequested(attribute_name)
            if not record.attribute_candidates.get(attribute_name):
                raise NoAcquisitionPending(attribute_name)

        for attribute_name in attribute_names:
            new_owner, _candidate_tag = self._pop_attribute_candidate(record, attribute_name) or (None, b"")
            if new_owner is None:
                raise NoAcquisitionPending(attribute_name)
            record.attribute_owners[attribute_name] = new_owner
            record.attribute_divesting.discard(attribute_name)
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            self._deliver_to_federate_handle(
                new_owner,
                "attributeOwnershipAcquisitionNotification",
                objectInstance,
                {attribute_handle},
                bytes(userSuppliedTag),
            )

    def attributeOwnershipAcquisition(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisition", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisition")
        record = self._object_instance_record(objectInstance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, desiredAttributes)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        for attribute_name in attribute_names:
            current_owner = record.attribute_owners.get(attribute_name)
            if current_owner == self._federate_handle:
                raise AttributeAlreadyOwned(attribute_name)
            if self._has_attribute_candidate(record, attribute_name, self._federate_handle):
                raise AttributeAlreadyBeingAcquired(attribute_name)

        for attribute_name in attribute_names:
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            current_owner = record.attribute_owners.get(attribute_name)
            if current_owner is None or attribute_name in record.attribute_divesting:
                old_owner = current_owner
                record.attribute_owners[attribute_name] = self._federate_handle
                record.attribute_divesting.discard(attribute_name)
                if old_owner is not None:
                    self._deliver_to_federate_handle(
                        old_owner,
                        "requestDivestitureConfirmation",
                        objectInstance,
                        {attribute_handle},
                        bytes(userSuppliedTag),
                    )
                self._deliver_callback("attributeOwnershipAcquisitionNotification", objectInstance, {attribute_handle}, bytes(userSuppliedTag))
            else:
                self._add_attribute_candidate(record, attribute_name, self._federate_handle, bytes(userSuppliedTag))
                self._deliver_to_federate_handle(
                    current_owner,
                    "requestAttributeOwnershipRelease",
                    objectInstance,
                    {attribute_handle},
                    bytes(userSuppliedTag),
                )

    def attributeOwnershipAcquisitionIfAvailable(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisitionIfAvailable", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisitionIfAvailable")
        record = self._object_instance_record(objectInstance)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        available: set[AttributeHandle] = set()
        unavailable: set[AttributeHandle] = set()
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, desiredAttributes):
            current_owner = record.attribute_owners.get(attribute_name)
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            if current_owner == self._federate_handle:
                raise AttributeAlreadyOwned(attribute_name)
            if self._has_attribute_candidate(record, attribute_name, self._federate_handle):
                raise AttributeAlreadyBeingAcquired(attribute_name)
            if current_owner is None:
                record.attribute_owners[attribute_name] = self._federate_handle
                available.add(attribute_handle)
            else:
                unavailable.add(attribute_handle)
        if available:
            self._deliver_callback("attributeOwnershipAcquisitionNotification", objectInstance, available, userSuppliedTag)
        if unavailable:
            self._deliver_callback("attributeOwnershipUnavailable", objectInstance, unavailable, userSuppliedTag)

    def attributeOwnershipReleaseDenied(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("attributeOwnershipReleaseDenied", objectInstance, attributes)
        self._require_joined("attributeOwnershipReleaseDenied")
        record = self._object_instance_record(objectInstance)
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, attributes):
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            record.attribute_candidates.pop(attribute_name, None)

    def attributeOwnershipDivestitureIfWanted(self, objectInstance: Any, attributes: Any) -> set[AttributeHandle]:  # noqa: N802
        self._record("attributeOwnershipDivestitureIfWanted", objectInstance, attributes)
        self._require_joined("attributeOwnershipDivestitureIfWanted")
        record = self._object_instance_record(objectInstance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, attributes)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        for attribute_name in attribute_names:
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            if not record.attribute_candidates.get(attribute_name):
                raise NoAcquisitionPending(attribute_name)

        divested: set[AttributeHandle] = set()
        for attribute_name in attribute_names:
            new_owner, _candidate_tag = self._pop_attribute_candidate(record, attribute_name) or (None, b"")
            if new_owner is None:
                raise NoAcquisitionPending(attribute_name)
            record.attribute_owners[attribute_name] = new_owner
            record.attribute_divesting.discard(attribute_name)
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            divested.add(attribute_handle)
            self._deliver_to_federate_handle(new_owner, "attributeOwnershipAcquisitionNotification", objectInstance, {attribute_handle}, b"")
        return divested

    def cancelNegotiatedAttributeOwnershipDivestiture(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelNegotiatedAttributeOwnershipDivestiture", objectInstance, attributes)
        self._require_joined("cancelNegotiatedAttributeOwnershipDivestiture")
        record = self._object_instance_record(objectInstance)
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, attributes):
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            if attribute_name not in record.attribute_divesting:
                raise AttributeDivestitureWasNotRequested(attribute_name)
            record.attribute_divesting.discard(attribute_name)

    def cancelAttributeOwnershipAcquisition(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelAttributeOwnershipAcquisition", objectInstance, attributes)
        self._require_joined("cancelAttributeOwnershipAcquisition")
        record = self._object_instance_record(objectInstance)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        cancelled: set[AttributeHandle] = set()
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, attributes):
            if record.attribute_owners.get(attribute_name) == self._federate_handle:
                raise AttributeAlreadyOwned(attribute_name)
            if not self._has_attribute_candidate(record, attribute_name, self._federate_handle):
                raise AttributeAcquisitionWasNotRequested(attribute_name)
            self._remove_attribute_candidate(record, attribute_name, self._federate_handle)
            cancelled.add(AttributeHandle(attribute_handles_by_name[attribute_name]))
        self._deliver_callback("confirmAttributeOwnershipAcquisitionCancellation", objectInstance, cancelled)

    def queryAttributeOwnership(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("queryAttributeOwnership", objectInstance, attributes)
        self._require_joined("queryAttributeOwnership")
        record = self._object_instance_record(objectInstance)
        attribute_handles_by_name = self._attribute_handles(record.object_class_name)
        owned_by_federate: dict[FederateHandle, set[AttributeHandle]] = {}
        not_owned: set[AttributeHandle] = set()
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, attributes):
            attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
            owner = record.attribute_owners.get(attribute_name)
            if owner is None:
                not_owned.add(attribute_handle)
            else:
                owned_by_federate.setdefault(owner, set()).add(attribute_handle)
        for owner, owned_attributes in sorted(owned_by_federate.items(), key=lambda item: item[0].value):
            self._deliver_callback("informAttributeOwnership", objectInstance, owned_attributes, owner)
        if not_owned:
            self._deliver_callback("attributeIsNotOwned", objectInstance, not_owned)

    def isAttributeOwnedByFederate(self, objectInstance: Any, attribute: Any) -> bool:  # noqa: N802
        self._record("isAttributeOwnedByFederate", objectInstance, attribute)
        self._require_joined("isAttributeOwnedByFederate")
        record = self._object_instance_record(objectInstance)
        attribute_name = self._attribute_names_from_handles(record.object_class_name, {attribute})[0]
        return record.attribute_owners.get(attribute_name) == self._federate_handle

    def getTimeFactory(self) -> Any:  # noqa: N802
        self._record("getTimeFactory")
        self._require_connected("getTimeFactory")
        return self._logical_time_factory

    def normalizeServiceGroup(self, serviceGroup: Any) -> int:  # noqa: N802
        self._record("normalizeServiceGroup", serviceGroup)
        self._require_joined("normalizeServiceGroup")
        try:
            return int(serviceGroup if isinstance(serviceGroup, ServiceGroup) else ServiceGroup(serviceGroup))
        except Exception as exc:
            raise InvalidServiceGroup(repr(serviceGroup)) from exc

    def normalizeFederateHandle(self, federate: Any) -> int:  # noqa: N802
        self._record("normalizeFederateHandle", federate)
        self._require_joined("normalizeFederateHandle")
        return self._normalize_handle(federate, FederateHandle, InvalidFederateHandle)

    def normalizeObjectClassHandle(self, objectClass: Any) -> int:  # noqa: N802
        self._record("normalizeObjectClassHandle", objectClass)
        self._require_joined("normalizeObjectClassHandle")
        return self._normalize_handle(objectClass, ObjectClassHandle, InvalidObjectClassHandle)

    def normalizeInteractionClassHandle(self, interactionClass: Any) -> int:  # noqa: N802
        self._record("normalizeInteractionClassHandle", interactionClass)
        self._require_joined("normalizeInteractionClassHandle")
        return self._normalize_handle(interactionClass, InteractionClassHandle, InvalidInteractionClassHandle)

    def normalizeObjectInstanceHandle(self, objectInstance: Any) -> int:  # noqa: N802
        self._record("normalizeObjectInstanceHandle", objectInstance)
        self._require_joined("normalizeObjectInstanceHandle")
        return self._normalize_handle(objectInstance, ObjectInstanceHandle, InvalidObjectInstanceHandle)

    def getObjectClassRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getObjectClassRelevanceAdvisorySwitch")
        return self._get_switch("getObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory")

    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setObjectClassRelevanceAdvisorySwitch", value)
        self._set_switch("setObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory", value)

    def getAttributeRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeRelevanceAdvisorySwitch")
        return self._get_switch("getAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory")

    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeRelevanceAdvisorySwitch", value)
        self._set_switch("setAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory", value)

    def getAttributeScopeAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeScopeAdvisorySwitch")
        return self._get_switch("getAttributeScopeAdvisorySwitch", "attribute_scope_advisory")

    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeScopeAdvisorySwitch", value)
        self._set_switch("setAttributeScopeAdvisorySwitch", "attribute_scope_advisory", value)

    def getInteractionRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getInteractionRelevanceAdvisorySwitch")
        return self._get_switch("getInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory")

    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setInteractionRelevanceAdvisorySwitch", value)
        self._set_switch("setInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory", value)

    def getConveyRegionDesignatorSetsSwitch(self) -> bool:  # noqa: N802
        self._record("getConveyRegionDesignatorSetsSwitch")
        return self._get_switch("getConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets")

    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setConveyRegionDesignatorSetsSwitch", value)
        self._set_switch("setConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets", value)

    def getServiceReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getServiceReportingSwitch")
        return self._get_switch("getServiceReportingSwitch", "service_reporting")

    def setServiceReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setServiceReportingSwitch", value)
        self._set_switch("setServiceReportingSwitch", "service_reporting", value)

    def getExceptionReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getExceptionReportingSwitch")
        return self._get_switch("getExceptionReportingSwitch", "exception_reporting")

    def setExceptionReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setExceptionReportingSwitch", value)
        self._set_switch("setExceptionReportingSwitch", "exception_reporting", value)

    def getSendServiceReportsToFileSwitch(self) -> bool:  # noqa: N802
        self._record("getSendServiceReportsToFileSwitch")
        return self._get_switch("getSendServiceReportsToFileSwitch", "send_service_reports_to_file")

    def setSendServiceReportsToFileSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setSendServiceReportsToFileSwitch", value)
        self._set_switch("setSendServiceReportsToFileSwitch", "send_service_reports_to_file", value)

    def getAutoProvideSwitch(self) -> bool:  # noqa: N802
        self._record("getAutoProvideSwitch")
        return self._get_switch("getAutoProvideSwitch", "auto_provide")

    def getDelaySubscriptionEvaluationSwitch(self) -> bool:  # noqa: N802
        self._record("getDelaySubscriptionEvaluationSwitch")
        return self._get_switch("getDelaySubscriptionEvaluationSwitch", "delay_subscription_evaluation")

    def getAdvisoriesUseKnownClassSwitch(self) -> bool:  # noqa: N802
        self._record("getAdvisoriesUseKnownClassSwitch")
        return self._get_switch("getAdvisoriesUseKnownClassSwitch", "advisories_use_known_class")

    def getAllowRelaxedDDMSwitch(self) -> bool:  # noqa: N802
        self._record("getAllowRelaxedDDMSwitch")
        return self._get_switch("getAllowRelaxedDDMSwitch", "allow_relaxed_ddm")

    def getNonRegulatedGrantSwitch(self) -> bool:  # noqa: N802
        self._record("getNonRegulatedGrantSwitch")
        return self._get_switch("getNonRegulatedGrantSwitch", "non_regulated_grant")

    def getHLAversion(self) -> str:  # noqa: N802
        self._record("getHLAversion")
        return "IEEE 1516.1-2025"

    def close(self) -> None:
        if self._connected:
            self.disconnect()

    def __enter__(self) -> "Shim2025RTIAmbassador":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.close()
        return False

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name.startswith("_"):
            raise AttributeError(name)

        def _unsupported(*args: Any, **kwargs: Any) -> Any:
            self._record(name, *args, **kwargs)
            raise RTIinternalError(f"hla-backend-shim does not implement IEEE 1516.1-2025 service {name}")

        return _unsupported

    def _record(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((method_name, args, dict(kwargs)))

    def _deliver_callback(self, method_name: str, *args: Any) -> None:
        if self._federate_ambassador is None:
            raise RTIinternalError(f"Cannot deliver {method_name} without a connected federate ambassador")
        callback = getattr(self._federate_ambassador, method_name, None)
        if callback is None:
            raise RTIinternalError(f"Connected federate ambassador does not implement {method_name}")
        callback(*args)

    def _deliver_to_federate_handle(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        federation = self._federation_record()
        ambassador = federation.member_ambassadors.get(federate_handle.value)
        if ambassador is None:
            raise InvalidFederateHandle(f"Unknown federate handle {federate_handle!r}")
        callback = getattr(ambassador, method_name, None)
        if callback is None:
            raise RTIinternalError(f"Federate ambassador {federate_handle!r} does not implement {method_name}")
        callback(*args)

    def _other_member_handles(self) -> tuple[FederateHandle, ...]:
        if self._federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        return tuple(
            handle
            for handle in self._federation_record().member_handles.values()
            if handle != self._federate_handle
        )

    @staticmethod
    def _has_attribute_candidate(
        record: _ObjectInstanceRecord,
        attribute_name: str,
        federate_handle: FederateHandle | None,
    ) -> bool:
        return any(candidate == federate_handle for candidate, _tag in record.attribute_candidates.get(attribute_name, ()))

    @staticmethod
    def _add_attribute_candidate(
        record: _ObjectInstanceRecord,
        attribute_name: str,
        federate_handle: FederateHandle | None,
        user_supplied_tag: bytes,
    ) -> None:
        if federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        candidates = record.attribute_candidates.setdefault(attribute_name, [])
        candidates[:] = [(candidate, tag) for candidate, tag in candidates if candidate != federate_handle]
        candidates.append((federate_handle, bytes(user_supplied_tag)))

    @staticmethod
    def _remove_attribute_candidate(
        record: _ObjectInstanceRecord,
        attribute_name: str,
        federate_handle: FederateHandle | None,
    ) -> None:
        candidates = record.attribute_candidates.get(attribute_name)
        if candidates is None:
            return
        candidates[:] = [(candidate, tag) for candidate, tag in candidates if candidate != federate_handle]
        if not candidates:
            record.attribute_candidates.pop(attribute_name, None)

    @staticmethod
    def _pop_attribute_candidate(
        record: _ObjectInstanceRecord,
        attribute_name: str,
    ) -> tuple[FederateHandle, bytes] | None:
        candidates = record.attribute_candidates.get(attribute_name)
        if not candidates:
            return None
        candidate = candidates.pop(0)
        if not candidates:
            record.attribute_candidates.pop(attribute_name, None)
        return candidate

    def _require_connected(self, method_name: str) -> None:
        if not self._connected:
            raise NotConnected(f"Cannot call {method_name} before connect")

    def _require_joined(self, method_name: str) -> None:
        self._require_connected(method_name)
        if not self._joined:
            raise FederateNotExecutionMember(f"Cannot call {method_name} before joinFederationExecution")

    def _extract_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federation_name = kwargs.get("federationName")
        if federation_name is None:
            federation_name = kwargs.get("federation_name")
        if federation_name is None:
            if len(args) >= 3:
                federation_name = args[2]
            elif len(args) >= 2:
                federation_name = args[1]
            elif args:
                federation_name = args[0]
        if not isinstance(federation_name, str) or not federation_name:
            raise RTIinternalError("2025 shim RTI ambassador requires a federation name")
        return federation_name

    def _extract_create_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federation_name = kwargs.get("federationName")
        if federation_name is None:
            federation_name = kwargs.get("federation_name")
        if federation_name is None and args:
            federation_name = args[0]
        if not isinstance(federation_name, str) or not federation_name:
            raise RTIinternalError("2025 shim RTI ambassador requires a federation name")
        return federation_name

    def _extract_join_names(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str, str | None]:
        federation_name = self._extract_federation_name(args, kwargs)
        federate_name = kwargs.get("federateName")
        if federate_name is None:
            federate_name = kwargs.get("federate_name")
        if federate_name is None and len(args) >= 3:
            federate_name = args[0]
        if federate_name is not None and not isinstance(federate_name, str):
            raise RTIinternalError("2025 shim RTI ambassador requires federateName to be a string when provided")
        return federation_name, federate_name

    def _extract_federate_type(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federate_type = kwargs.get("federateType")
        if federate_type is None:
            federate_type = kwargs.get("federate_type")
        if federate_type is None and len(args) >= 2:
            federate_type = args[1]
        if not isinstance(federate_type, str) or not federate_type:
            raise RTIinternalError("2025 shim RTI ambassador requires federateType to be a non-empty string")
        return federate_type

    def _extract_logical_time_implementation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        value = kwargs.get("logicalTimeImplementationName")
        if value is None:
            value = kwargs.get("logical_time_implementation_name")
        if value is None and len(args) >= 4:
            value = args[3]
        if value is None and len(args) == 3 and not isinstance(args[2], (list, tuple, set, frozenset)):
            value = args[2]
        if value is None:
            return _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        if not isinstance(value, str):
            raise RTIinternalError("2025 shim RTI ambassador requires logicalTimeImplementationName to be a string")
        if value not in _SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS:
            raise CouldNotCreateLogicalTimeFactory(value)
        return value

    def _extract_fom_sources(
        self,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        with_mim: bool,
    ) -> tuple[Any, ...]:
        fom_module = kwargs.get("fomModule")
        fom_modules = kwargs.get("fomModules")
        if fom_module is not None and fom_modules is not None:
            raise InvalidFOM("Use either fomModule or fomModules, not both")
        if fom_module is not None:
            return (fom_module,)
        if fom_modules is not None:
            return self._normalize_module_sources(fom_modules)
        if with_mim:
            if len(args) >= 2:
                return self._normalize_module_sources(args[1])
            return ()
        if len(args) >= 2:
            return self._normalize_module_sources(args[1])
        return ()

    def _extract_mim_source(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any | None:
        mim_source = kwargs.get("mimModule")
        if mim_source is None:
            mim_source = kwargs.get("mim_module")
        if mim_source is None and len(args) >= 3:
            mim_source = args[2]
        return mim_source

    def _extract_additional_fom_modules(
        self,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[Any, ...]:
        additional = kwargs.get("additionalFomModules")
        if additional is None:
            additional = kwargs.get("additional_fom_modules")
        if additional is None:
            return ()
        return self._normalize_module_sources(additional)

    @staticmethod
    def _normalize_module_sources(value: Any) -> tuple[Any, ...]:
        if value is None:
            return ()
        if isinstance(value, (str, bytes, bytearray, memoryview, Path)):
            return (value,)
        return tuple(value)

    @staticmethod
    def _coerce_callback_model(value: Any) -> CallbackModel:
        try:
            return value if isinstance(value, CallbackModel) else CallbackModel(value)
        except Exception as exc:
            raise UnsupportedCallbackModel(repr(value)) from exc

    def _coerce_time(self, value: Any) -> Any:
        factory = self._logical_time_factory
        time_type = getattr(factory, "time_type", None)
        if time_type is not None and isinstance(value, time_type):
            return value
        if hasattr(value, "getValue"):
            value = value.getValue()
        try:
            return factory.makeTime(value)
        except Exception as exc:
            raise InvalidLogicalTime(repr(value)) from exc

    def _coerce_interval(self, value: Any) -> Any:
        factory = self._logical_time_factory
        interval_type = getattr(factory, "interval_type", None)
        if interval_type is not None and isinstance(value, interval_type):
            return value
        if hasattr(value, "getValue"):
            value = value.getValue()
        try:
            return factory.makeInterval(value)
        except Exception as exc:
            raise InvalidLookahead(repr(value)) from exc

    @staticmethod
    def _validate_credentials(credentials: Any | None) -> None:
        if credentials is None:
            return
        credential_type = getattr(credentials, "type", None)
        credential_data = getattr(credentials, "data", None)
        if not isinstance(credential_type, str) or credential_data is None:
            raise InvalidCredentials("Credentials must expose type and data fields")
        if credential_type == "HLAnoCredentials":
            if bytes(credential_data) != b"":
                raise InvalidCredentials("HLAnoCredentials must not carry credential bytes")
            return
        if credential_type == "HLAplainTextPassword":
            auth_module = import_module("hla.rti1516_2025.auth")
            try:
                password = auth_module.HLAplainTextPassword(bytes(credential_data)).decode()
            except Exception as exc:
                raise InvalidCredentials("Encoded HLAplainTextPassword is malformed") from exc
            if not password:
                raise InvalidCredentials("HLAplainTextPassword cannot be empty")
            if password == "bad":
                raise InvalidCredentials("Credential provider rejected HLAplainTextPassword")
            return
        if not credential_type.strip():
            raise InvalidCredentials("Custom credentials must declare a non-empty type")
        if not isinstance(credential_data, (bytes, bytearray, memoryview)):
            raise Unauthorized("Custom credentials must provide byte payloads")

    @staticmethod
    def _resolve_fom_modules(sources: tuple[Any, ...], *, mim: bool) -> tuple[Any, ...]:
        fom = import_module("hla.rti1516e.fom")
        try:
            modules = fom.FOMResolver(require_local_parse=True).resolve_many(sources)
            if not mim:
                validation = import_module("hla.rti1516_2025.validation")
                issues = validation.validate_fom_modules(modules)
                if issues:
                    raise InvalidFOM(issues[0].message)
            return modules
        except fom.FOMResolutionError as exc:
            kind = getattr(exc, "kind", "open")
            if mim:
                if kind == "read":
                    raise ErrorReadingMIM(str(exc)) from exc
                raise CouldNotOpenMIM(str(exc)) from exc
            if kind == "read":
                raise ErrorReadingFOM(str(exc)) from exc
            raise CouldNotOpenFOM(str(exc)) from exc
        except InvalidFOM:
            raise
        except Exception as exc:
            if mim:
                raise InvalidMIM(str(exc)) from exc
            raise InvalidFOM(str(exc)) from exc

    @staticmethod
    def _merge_fom_modules(modules: tuple[Any, ...], *, mim_module: Any) -> Any:
        fom = import_module("hla.rti1516e.fom")
        try:
            return fom.merge_fom_modules(modules, mim_module=mim_module)
        except fom.FOMMergeError as exc:
            raise InconsistentFOM(str(exc)) from exc

    @staticmethod
    def _standard_mim_module() -> Any:
        fom = import_module("hla.rti1516e.fom")
        return fom.standard_mim_module()

    @staticmethod
    def _get_time_factory(name: str) -> Any:
        time = import_module("hla.rti1516_2025.time")
        return time.get_logical_time_factory(name)

    def _select_logical_time_implementation(self, name: str) -> None:
        self._logical_time_implementation_name = name
        self._logical_time_factory = self._get_time_factory(name)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False

    def _release_join(self) -> None:
        if self._federation_name is None:
            return
        federation = _FEDERATION_REGISTRY.get(self._federation_name)
        if federation is not None:
            if self._federate_name is not None:
                federation.members.pop(self._federate_name, None)
                federation.member_handles.pop(self._federate_name, None)
            if self._federate_handle is not None:
                federation.member_ambassadors.pop(self._federate_handle.value, None)

    def _resign_reason_description(self, resign_action: ResignAction) -> str:
        action = getattr(resign_action, "name", str(resign_action))
        return f"federateName={self._federate_name}; federationName={self._federation_name}; resignAction={action}"

    @staticmethod
    def _normalize_handle(handle: Any, expected_type: type[Any], exception_type: type[Exception]) -> int:
        if not isinstance(handle, expected_type):
            raise exception_type(f"Expected {expected_type.__name__}; got {type(handle).__name__}")
        value = getattr(handle, "value", None)
        if not isinstance(value, int) or value < 0:
            raise exception_type(f"Invalid {expected_type.__name__}: {handle!r}")
        return value

    def _federation_record(self) -> _FederationRecord:
        self._require_joined("FOM catalog access")
        if self._federation_name is None:
            raise FederateNotExecutionMember("Cannot access FOM catalog before joinFederationExecution")
        federation = _FEDERATION_REGISTRY.get(self._federation_name)
        if federation is None:
            raise FederationExecutionDoesNotExist(self._federation_name)
        return federation

    def _catalog(self) -> Any:
        catalog = self._federation_record().fom_catalog
        if catalog is None:
            raise InvalidFOM("Federation execution does not have a merged FOM catalog")
        return catalog

    @staticmethod
    def _stable_handles(names: Any) -> dict[str, int]:
        return {name: index for index, name in enumerate(sorted(str(name) for name in names), start=1)}

    def _object_class_handles(self) -> dict[str, int]:
        return self._stable_handles(self._catalog().object_classes)

    def _interaction_class_handles(self) -> dict[str, int]:
        return self._stable_handles(self._catalog().interaction_classes)

    def _dimension_handles(self) -> dict[str, int]:
        return self._stable_handles(self._catalog().dimensions)

    def _dimension_spec(self, dimension_name: str) -> Any | None:
        catalog = self._catalog()
        modules = tuple(getattr(catalog, "modules", ()))
        mim_module = getattr(catalog, "mim_module", None)
        if mim_module is not None:
            modules = (*modules, mim_module)
        for module in modules:
            spec = getattr(module, "dimension_specs", {}).get(dimension_name)
            if spec is not None:
                return spec
        return None

    def _transportation_handles(self) -> dict[str, int]:
        names = set(getattr(self._catalog(), "transportation_names", ()))
        names.update({"HLAreliable", "HLAbestEffort"})
        return self._stable_handles(names)

    def _attribute_handles(self, object_class_name: str) -> dict[str, int]:
        catalog = self._catalog()
        try:
            spec = catalog.object_classes[object_class_name]
        except KeyError as exc:
            raise ObjectClassNotDefined(object_class_name) from exc
        return self._stable_handles(spec.attributes)

    def _object_class_name(self, object_class: Any) -> str:
        object_class_value = self._normalize_handle(object_class, ObjectClassHandle, InvalidObjectClassHandle)
        names_by_handle = {value: name for name, value in self._object_class_handles().items()}
        try:
            return names_by_handle[object_class_value]
        except KeyError as exc:
            raise InvalidObjectClassHandle(str(object_class)) from exc

    def _interaction_class_name(self, interaction_class: Any) -> str:
        interaction_class_value = self._normalize_handle(
            interaction_class,
            InteractionClassHandle,
            InvalidInteractionClassHandle,
        )
        names_by_handle = {value: name for name, value in self._interaction_class_handles().items()}
        try:
            return names_by_handle[interaction_class_value]
        except KeyError as exc:
            raise InvalidInteractionClassHandle(str(interaction_class)) from exc

    def _object_instance_record(self, object_instance: Any) -> _ObjectInstanceRecord:
        object_instance_value = self._normalize_handle(
            object_instance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        try:
            return self._federation_record().object_instances[object_instance_value]
        except KeyError as exc:
            raise InvalidObjectInstanceHandle(str(object_instance)) from exc

    def _attribute_names_from_handles(self, object_class_name: str, attributes: Any) -> tuple[str, ...]:
        try:
            attribute_values = tuple(attributes)
        except TypeError as exc:
            raise AttributeNotDefined("Attribute handle set must be iterable") from exc
        if not attribute_values:
            raise AttributeNotDefined("Attribute handle set cannot be empty")
        names_by_handle = {value: name for name, value in self._attribute_handles(object_class_name).items()}
        names: list[str] = []
        for attribute in attribute_values:
            attribute_value = self._normalize_handle(attribute, AttributeHandle, InvalidAttributeHandle)
            try:
                names.append(names_by_handle[attribute_value])
            except KeyError as exc:
                raise InvalidAttributeHandle(str(attribute)) from exc
        return tuple(names)

    def _safe_report_arg(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, Mapping):
            return {str(key): self._safe_report_arg(item) for key, item in value.items()}
        if isinstance(value, (set, frozenset, list, tuple)):
            return [self._safe_report_arg(item) for item in value]
        if hasattr(value, "value") and isinstance(value.value, int):
            return {"type": type(value).__name__, "value": value.value}
        return repr(value)

    def _get_switch(self, method_name: str, name: str) -> bool:
        self._require_joined(method_name)
        return self._switches[name]

    def _set_switch(self, method_name: str, name: str, value: bool) -> None:
        self._require_joined(method_name)
        if not isinstance(value, bool):
            raise RTIinternalError(f"{method_name} requires a bool value")
        self._switches[name] = value


class Shim2025Backend:
    """Factory-facing backend wrapper that returns a 2025-native ambassador."""

    info = ShimBackendInfo()

    def __init__(self, request: BackendRequest):
        self.request = request

    def create_rti_ambassador(self) -> Shim2025RTIAmbassador:
        return Shim2025RTIAmbassador()


def create_shim_backend(request: BackendRequest) -> Shim2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"shim backend only supports rti1516_2025, not {request.spec.name!r}")
    return Shim2025Backend(request)


__all__ = ["Shim2025Backend", "Shim2025RTIAmbassador", "create_shim_backend"]
