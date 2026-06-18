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
    RangeBounds,
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
    DeletePrivilegeNotHeld,
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
    InteractionClassNotDefined,
    InteractionClassNotPublished,
    InteractionParameterNotDefined,
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
    InvalidRangeBound,
    InvalidRegion,
    InvalidRegionContext,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationTypeHandle,
    LogicalTimeAlreadyPassed,
    NameNotFound,
    NoAcquisitionPending,
    NotConnected,
    ObjectClassNotDefined,
    ObjectClassNotPublished,
    ObjectInstanceNameInUse,
    ObjectInstanceNotKnown,
    RegionDoesNotContainSpecifiedDimension,
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
    ParameterHandle,
    RegionHandle,
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
    published_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_regions: dict[int, dict[str, dict[str, set[int]]]] = field(default_factory=dict)
    published_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interaction_regions: dict[int, dict[str, set[int]]] = field(default_factory=dict)
    published_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    member_regions: dict[int, dict[int, set[str]]] = field(default_factory=dict)
    member_region_bounds: dict[int, dict[int, dict[str, RangeBounds]]] = field(default_factory=dict)
    object_instances: dict[int, "_ObjectInstanceRecord"] = field(default_factory=dict)
    object_instance_names: dict[str, int] = field(default_factory=dict)
    interaction_transportation: dict[tuple[int, str], str] = field(default_factory=dict)
    next_object_instance_handle: int = 1
    next_region_handle: int = 1


@dataclass(slots=True)
class _ObjectInstanceRecord:
    object_class_name: str
    object_instance_name: str | None
    attribute_owners: dict[str, FederateHandle | None] = field(default_factory=dict)
    attribute_divesting: set[str] = field(default_factory=set)
    attribute_candidates: dict[str, list[tuple[FederateHandle, bytes]]] = field(default_factory=dict)
    update_regions: dict[str, set[int]] = field(default_factory=dict)
    attribute_transportation: dict[str, str] = field(default_factory=dict)


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
        federation.published_object_attributes.setdefault(self._federate_handle.value, {})
        federation.subscribed_object_attributes.setdefault(self._federate_handle.value, {})
        federation.subscribed_object_regions.setdefault(self._federate_handle.value, {})
        federation.published_interactions.setdefault(self._federate_handle.value, set())
        federation.subscribed_interactions.setdefault(self._federate_handle.value, set())
        federation.subscribed_interaction_regions.setdefault(self._federate_handle.value, {})
        federation.published_directed_interactions.setdefault(self._federate_handle.value, {})
        federation.subscribed_directed_interactions.setdefault(self._federate_handle.value, {})
        federation.member_regions.setdefault(self._federate_handle.value, {})
        federation.member_region_bounds.setdefault(self._federate_handle.value, {})
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

    def getInteractionClassHandle(self, interactionClassName: str) -> InteractionClassHandle:  # noqa: N802
        self._record("getInteractionClassHandle", interactionClassName)
        self._require_joined("getInteractionClassHandle")
        if not isinstance(interactionClassName, str):
            raise NameNotFound(repr(interactionClassName))
        handles = self._interaction_class_handles()
        try:
            return InteractionClassHandle(handles[interactionClassName])
        except KeyError as exc:
            raise NameNotFound(interactionClassName) from exc

    def getInteractionClassName(self, interactionClass: Any) -> str:  # noqa: N802
        self._record("getInteractionClassName", interactionClass)
        return self._interaction_class_name(interactionClass)

    def getParameterHandle(self, interactionClass: Any, parameterName: str) -> ParameterHandle:  # noqa: N802
        self._record("getParameterHandle", interactionClass, parameterName)
        interaction_class_name = self._interaction_class_name(interactionClass)
        if not isinstance(parameterName, str):
            raise InteractionParameterNotDefined(repr(parameterName))
        handles = self._parameter_handles(interaction_class_name)
        try:
            return ParameterHandle(handles[parameterName])
        except KeyError as exc:
            raise InteractionParameterNotDefined(parameterName) from exc

    def getParameterName(self, interactionClass: Any, parameter: Any) -> str:  # noqa: N802
        self._record("getParameterName", interactionClass, parameter)
        interaction_class_name = self._interaction_class_name(interactionClass)
        parameter_value = self._normalize_handle(parameter, ParameterHandle, InteractionParameterNotDefined)
        names_by_handle = {value: name for name, value in self._parameter_handles(interaction_class_name).items()}
        try:
            return names_by_handle[parameter_value]
        except KeyError as exc:
            raise InteractionParameterNotDefined(str(parameter)) from exc

    def publishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("publishObjectClassAttributes", objectClass, attributes)
        self._require_joined("publishObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        federation = self._federation_record()
        federation.published_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set()).update(attribute_names)

    def unpublishObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClass", objectClass)
        self._require_joined("unpublishObjectClass")
        object_class_name = self._object_class_name(objectClass)
        self._federation_record().published_object_attributes.setdefault(self._current_federate_key(), {}).pop(object_class_name, None)

    def unpublishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClassAttributes", objectClass, attributes)
        self._require_joined("unpublishObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        published = self._federation_record().published_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set())
        published.difference_update(attribute_names)
        if not published:
            self._federation_record().published_object_attributes[self._current_federate_key()].pop(object_class_name, None)

    def subscribeObjectClassAttributes(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributes", objectClass, attributes, *unused)
        self._require_joined("subscribeObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        federation = self._federation_record()
        federation.subscribed_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set()).update(attribute_names)
        self._discover_existing_objects_for_current_subscription(object_class_name)

    def subscribeObjectClassAttributesPassively(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassively", objectClass, attributes, *unused)
        self.subscribeObjectClassAttributes(objectClass, attributes, *unused)

    def unsubscribeObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClass", objectClass)
        self._require_joined("unsubscribeObjectClass")
        object_class_name = self._object_class_name(objectClass)
        self._federation_record().subscribed_object_attributes.setdefault(self._current_federate_key(), {}).pop(object_class_name, None)

    def unsubscribeObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributes", objectClass, attributes)
        self._require_joined("unsubscribeObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        subscribed = self._federation_record().subscribed_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set())
        subscribed.difference_update(attribute_names)
        if not subscribed:
            self._federation_record().subscribed_object_attributes[self._current_federate_key()].pop(object_class_name, None)

    def publishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("publishInteractionClass", interactionClass)
        self._require_joined("publishInteractionClass")
        self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()).add(self._interaction_class_name(interactionClass))

    def unpublishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unpublishInteractionClass", interactionClass)
        self._require_joined("unpublishInteractionClass")
        self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()).discard(self._interaction_class_name(interactionClass))

    def subscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClass", interactionClass)
        self._require_joined("subscribeInteractionClass")
        self._federation_record().subscribed_interactions.setdefault(self._current_federate_key(), set()).add(self._interaction_class_name(interactionClass))

    def subscribeInteractionClassPassively(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassively", interactionClass)
        self.subscribeInteractionClass(interactionClass)

    def unsubscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClass", interactionClass)
        self._require_joined("unsubscribeInteractionClass")
        subscribed = self._federation_record().subscribed_interactions.setdefault(self._current_federate_key(), set())
        subscribed.discard(self._interaction_class_name(interactionClass))
        self._federation_record().subscribed_interaction_regions.setdefault(self._current_federate_key(), {}).pop(
            self._interaction_class_name(interactionClass),
            None,
        )

    def subscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("subscribeInteractionClassWithRegions")
        interaction_class_name = self._interaction_class_name(interactionClass)
        region_values = self._region_values_from_handles(regions)
        federation = self._federation_record()
        federation.subscribed_interactions.setdefault(self._current_federate_key(), set()).add(interaction_class_name)
        federation.subscribed_interaction_regions.setdefault(self._current_federate_key(), {}).setdefault(
            interaction_class_name,
            set(),
        ).update(region_values)

    def subscribeInteractionClassPassivelyWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassivelyWithRegions", interactionClass, regions)
        self.subscribeInteractionClassWithRegions(interactionClass, regions)

    def unsubscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("unsubscribeInteractionClassWithRegions")
        interaction_class_name = self._interaction_class_name(interactionClass)
        region_values = self._region_values_from_handles(regions)
        region_subscriptions = self._federation_record().subscribed_interaction_regions.setdefault(self._current_federate_key(), {}).setdefault(
            interaction_class_name,
            set(),
        )
        region_subscriptions.difference_update(region_values)
        if not region_subscriptions:
            self._federation_record().subscribed_interaction_regions[self._current_federate_key()].pop(interaction_class_name, None)
            self._federation_record().subscribed_interactions.setdefault(self._current_federate_key(), set()).discard(interaction_class_name)

    def publishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("publishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("publishObjectClassDirectedInteractions")
        object_class_name = self._object_class_name(objectClass)
        interaction_class_names = set(self._interaction_class_names_from_handles(interactionClasses))
        self._federation_record().published_directed_interactions.setdefault(self._current_federate_key(), {}).setdefault(
            object_class_name,
            set(),
        ).update(interaction_class_names)

    def unpublishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unpublishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unpublishObjectClassDirectedInteractions")
        object_class_name = self._object_class_name(objectClass)
        published_by_class = self._federation_record().published_directed_interactions.setdefault(self._current_federate_key(), {})
        if interactionClasses is None:
            published_by_class.pop(object_class_name, None)
            return
        published = published_by_class.setdefault(object_class_name, set())
        published.difference_update(self._interaction_class_names_from_handles(interactionClasses))
        if not published:
            published_by_class.pop(object_class_name, None)

    def subscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("subscribeObjectClassDirectedInteractions")
        object_class_name = self._object_class_name(objectClass)
        interaction_class_names = set(self._interaction_class_names_from_handles(interactionClasses))
        self._federation_record().subscribed_directed_interactions.setdefault(self._current_federate_key(), {}).setdefault(
            object_class_name,
            set(),
        ).update(interaction_class_names)

    def subscribeObjectClassDirectedInteractionsUniversally(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractionsUniversally", objectClass, interactionClasses)
        self.subscribeObjectClassDirectedInteractions(objectClass, interactionClasses)

    def unsubscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unsubscribeObjectClassDirectedInteractions")
        object_class_name = self._object_class_name(objectClass)
        subscribed_by_class = self._federation_record().subscribed_directed_interactions.setdefault(self._current_federate_key(), {})
        if interactionClasses is None:
            subscribed_by_class.pop(object_class_name, None)
            return
        subscribed = subscribed_by_class.setdefault(object_class_name, set())
        subscribed.difference_update(self._interaction_class_names_from_handles(interactionClasses))
        if not subscribed:
            subscribed_by_class.pop(object_class_name, None)

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

    def createRegion(self, dimensions: Any) -> RegionHandle:  # noqa: N802
        self._record("createRegion", dimensions)
        self._require_joined("createRegion")
        dimension_names = {self.getDimensionName(dimension) for dimension in set(dimensions)}
        if not dimension_names:
            raise InvalidRegionContext("createRegion requires at least one dimension")
        federation = self._federation_record()
        region = RegionHandle(federation.next_region_handle)
        federation.next_region_handle += 1
        federation.member_regions.setdefault(self._current_federate_key(), {})[region.value] = dimension_names
        federation.member_region_bounds.setdefault(self._current_federate_key(), {})[region.value] = {
            dimension_name: RangeBounds(0, self._dimension_default_upper_bound(dimension_name)) for dimension_name in dimension_names
        }
        return region

    def commitRegionModifications(self, regions: Any) -> None:  # noqa: N802
        self._record("commitRegionModifications", regions)
        self._require_joined("commitRegionModifications")
        for region in set(regions):
            self._region_dimension_names(self._current_federate_key(), region)

    def deleteRegion(self, region: Any) -> None:  # noqa: N802
        self._record("deleteRegion", region)
        self._require_joined("deleteRegion")
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        federate_key = self._current_federate_key()
        if region_value not in self._federation_record().member_regions.setdefault(federate_key, {}):
            raise InvalidRegion(str(region))
        self._federation_record().member_regions[federate_key].pop(region_value, None)
        self._federation_record().member_region_bounds.setdefault(federate_key, {}).pop(region_value, None)

    def getDimensionHandleSet(self, region: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getDimensionHandleSet", region)
        dimension_names = self._region_dimension_names(self._current_federate_key(), region)
        handles = self._dimension_handles()
        return {DimensionHandle(handles[name]) for name in dimension_names}

    def getRangeBounds(self, region: Any, dimension: Any) -> RangeBounds:  # noqa: N802
        self._record("getRangeBounds", region, dimension)
        federate_key = self._current_federate_key()
        dimension_name = self.getDimensionName(dimension)
        if dimension_name not in self._region_dimension_names(federate_key, region):
            raise RegionDoesNotContainSpecifiedDimension(str(dimension))
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        return self._federation_record().member_region_bounds[federate_key][region_value][dimension_name]

    def setRangeBounds(self, region: Any, dimension: Any, rangeBounds: Any) -> None:  # noqa: N802
        self._record("setRangeBounds", region, dimension, rangeBounds)
        federate_key = self._current_federate_key()
        dimension_name = self.getDimensionName(dimension)
        if dimension_name not in self._region_dimension_names(federate_key, region):
            raise RegionDoesNotContainSpecifiedDimension(str(dimension))
        bounds = self._coerce_range_bounds(rangeBounds)
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        self._federation_record().member_region_bounds.setdefault(federate_key, {}).setdefault(region_value, {})[dimension_name] = bounds

    def subscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions, *unused)
        self._require_joined("subscribeObjectClassAttributesWithRegions")
        object_class_name = self._object_class_name(objectClass)
        region_map = self._federation_record().subscribed_object_regions.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, {})
        all_attribute_names: set[str] = set()
        for attribute_names, region_values in self._attribute_region_pairs(object_class_name, attributesAndRegions):
            all_attribute_names.update(attribute_names)
            for attribute_name in attribute_names:
                region_map.setdefault(attribute_name, set()).update(region_values)
        if all_attribute_names:
            self._federation_record().subscribed_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set()).update(
                all_attribute_names
            )
            self._discover_existing_objects_for_current_subscription(object_class_name)

    def subscribeObjectClassAttributesPassivelyWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassivelyWithRegions", objectClass, attributesAndRegions, *unused)
        self.subscribeObjectClassAttributesWithRegions(objectClass, attributesAndRegions, *unused)

    def unsubscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions)
        self._require_joined("unsubscribeObjectClassAttributesWithRegions")
        object_class_name = self._object_class_name(objectClass)
        federation = self._federation_record()
        federate_key = self._current_federate_key()
        subscription_regions = federation.subscribed_object_regions.setdefault(federate_key, {}).setdefault(
            object_class_name,
            {},
        )
        subscribed_attrs = federation.subscribed_object_attributes.setdefault(federate_key, {}).setdefault(
            object_class_name,
            set(),
        )
        for attribute_names, region_values in self._attribute_region_pairs(object_class_name, attributesAndRegions):
            for attribute_name in attribute_names:
                if attribute_name in subscription_regions:
                    subscription_regions[attribute_name].difference_update(region_values)
                    if not subscription_regions[attribute_name]:
                        subscription_regions.pop(attribute_name, None)
                subscribed_attrs.discard(attribute_name)
        if not subscription_regions:
            self._federation_record().subscribed_object_regions[self._current_federate_key()].pop(object_class_name, None)
        if not subscribed_attrs:
            self._federation_record().subscribed_object_attributes[self._current_federate_key()].pop(object_class_name, None)

    def registerObjectInstanceWithRegions(self, objectClass: Any, attributesAndRegions: Any, objectInstanceName: str | None = None) -> ObjectInstanceHandle:  # noqa: N802
        self._record("registerObjectInstanceWithRegions", objectClass, attributesAndRegions, objectInstanceName)
        handle = self.registerObjectInstance(objectClass, objectInstanceName)
        record = self._object_instance_record(handle)
        for attribute_names, region_values in self._attribute_region_pairs(record.object_class_name, attributesAndRegions):
            for attribute_name in attribute_names:
                record.update_regions.setdefault(attribute_name, set()).update(region_values)
        return handle

    def associateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("associateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("associateRegionsForUpdates")
        record = self._object_instance_record(objectInstance)
        for attribute_names, region_values in self._attribute_region_pairs(record.object_class_name, attributesAndRegions):
            for attribute_name in attribute_names:
                record.update_regions.setdefault(attribute_name, set()).update(region_values)

    def unassociateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unassociateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("unassociateRegionsForUpdates")
        record = self._object_instance_record(objectInstance)
        for attribute_names, region_values in self._attribute_region_pairs(record.object_class_name, attributesAndRegions):
            for attribute_name in attribute_names:
                if attribute_name in record.update_regions:
                    record.update_regions[attribute_name].difference_update(region_values)
                    if not record.update_regions[attribute_name]:
                        record.update_regions.pop(attribute_name, None)

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
        object_class_handle = ObjectClassHandle(self._object_class_handles()[object_class_name])
        source_key = self._current_federate_key()
        for federate_key, subscriptions in federation.subscribed_object_attributes.items():
            if federate_key == self._current_federate_key():
                continue
            subscribed_names = set(subscriptions.get(object_class_name, set()))
            reflected_names = self._reflectable_attribute_names_for_subscriber(
                source_key,
                federate_key,
                federation.object_instances[handle.value],
                subscribed_names,
            )
            if reflected_names:
                self._deliver_to_federate_handle(
                    FederateHandle(federate_key),
                    "discoverObjectInstance",
                    handle,
                    object_class_handle,
                    objectInstanceName or "",
                    self._current_federate_handle(),
                )
        return handle

    def updateAttributeValues(  # noqa: N802
        self,
        objectInstance: Any,
        attributeValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("updateAttributeValues", objectInstance, attributeValues, userSuppliedTag, time)
        self._require_joined("updateAttributeValues")
        record = self._object_instance_record(objectInstance)
        object_class_name = record.object_class_name
        attributes_by_name = self._attribute_handles(object_class_name)
        values_by_handle: dict[AttributeHandle, bytes] = {}
        for attribute, value in dict(attributeValues).items():
            attribute_name = self._attribute_names_from_handles(object_class_name, {attribute})[0]
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            if attribute_name not in self._published_attributes_for_current_federate(object_class_name):
                raise ObjectClassNotPublished(object_class_name)
            values_by_handle[AttributeHandle(attributes_by_name[attribute_name])] = bytes(value)

        transportation = self._default_transportation_for(object_class_name, values_by_handle)
        callback_time = self._coerce_time(time) if time is not None else None
        for federate_key, subscriptions in self._federation_record().subscribed_object_attributes.items():
            if federate_key == self._current_federate_key():
                continue
            subscribed_names = self._reflectable_attribute_names_for_subscriber(
                self._current_federate_key(),
                federate_key,
                record,
                set(subscriptions.get(object_class_name, set())),
            )
            reflected = {
                handle: value
                for handle, value in values_by_handle.items()
                if self._attribute_name_by_handle(object_class_name, handle) in subscribed_names
            }
            if not reflected:
                continue
            sent_regions = {
                RegionHandle(region_value)
                for handle in reflected
                for region_value in record.update_regions.get(self._attribute_name_by_handle(object_class_name, handle), set())
            }
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "reflectAttributeValues",
                objectInstance,
                reflected,
                bytes(userSuppliedTag),
                transportation,
                self._current_federate_handle(),
                sent_regions,
                callback_time,
                self._default_order_for(object_class_name, reflected),
                self._default_order_for(object_class_name, reflected),
                None,
            )
        return None

    def sendInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendInteraction", interactionClass, parameterValues, userSuppliedTag, time)
        self._require_joined("sendInteraction")
        interaction_class_name = self._interaction_class_name(interactionClass)
        if interaction_class_name not in self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()):
            raise InteractionClassNotPublished(interaction_class_name)
        parameters_by_name = self._parameter_handles(interaction_class_name)
        values_by_handle: dict[ParameterHandle, bytes] = {}
        for parameter, value in dict(parameterValues).items():
            parameter_name = self._parameter_names_from_handles(interaction_class_name, {parameter})[0]
            values_by_handle[ParameterHandle(parameters_by_name[parameter_name])] = bytes(value)
        transportation = self._transportation_handle_by_name("HLAreliable")
        callback_time = self._coerce_time(time) if time is not None else None
        for federate_key, subscriptions in self._federation_record().subscribed_interactions.items():
            if federate_key == self._current_federate_key() or interaction_class_name not in subscriptions:
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "receiveInteraction",
                interactionClass,
                values_by_handle,
                bytes(userSuppliedTag),
                transportation,
                self._current_federate_handle(),
                set(),
                callback_time,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )
        return None

    def sendInteractionWithRegions(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Mapping[Any, bytes],
        regions: Any,
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendInteractionWithRegions", interactionClass, parameterValues, regions, userSuppliedTag, time)
        self._require_joined("sendInteractionWithRegions")
        source_regions = self._region_values_from_handles(regions)
        interaction_class_name = self._interaction_class_name(interactionClass)
        if interaction_class_name not in self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()):
            raise InteractionClassNotPublished(interaction_class_name)
        parameters_by_name = self._parameter_handles(interaction_class_name)
        values_by_handle: dict[ParameterHandle, bytes] = {}
        for parameter, value in dict(parameterValues).items():
            parameter_name = self._parameter_names_from_handles(interaction_class_name, {parameter})[0]
            values_by_handle[ParameterHandle(parameters_by_name[parameter_name])] = bytes(value)
        transportation = self._transportation_handle_by_name("HLAreliable")
        callback_time = self._coerce_time(time) if time is not None else None
        for federate_key, subscriptions in self._federation_record().subscribed_interactions.items():
            if federate_key == self._current_federate_key() or interaction_class_name not in subscriptions:
                continue
            target_regions = self._federation_record().subscribed_interaction_regions.get(federate_key, {}).get(
                interaction_class_name,
                set(),
            )
            if target_regions and not self._region_sets_overlap(self._current_federate_key(), source_regions, federate_key, target_regions):
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "receiveInteraction",
                interactionClass,
                values_by_handle,
                bytes(userSuppliedTag),
                transportation,
                self._current_federate_handle(),
                {RegionHandle(region_value) for region_value in source_regions},
                callback_time,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )
        return None

    def sendDirectedInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        objectInstance: Any,
        parameterValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendDirectedInteraction", interactionClass, objectInstance, parameterValues, userSuppliedTag, time)
        self._require_joined("sendDirectedInteraction")
        record = self._object_instance_record(objectInstance)
        object_class_name = record.object_class_name
        interaction_class_name = self._interaction_class_name(interactionClass)
        published_for_object_class = (
            self._federation_record()
            .published_directed_interactions.setdefault(self._current_federate_key(), {})
            .get(object_class_name, set())
        )
        if interaction_class_name not in published_for_object_class:
            raise InteractionClassNotPublished(interaction_class_name)

        parameters_by_name = self._parameter_handles(interaction_class_name)
        values_by_handle: dict[ParameterHandle, bytes] = {}
        for parameter, value in dict(parameterValues).items():
            parameter_name = self._parameter_names_from_handles(interaction_class_name, {parameter})[0]
            values_by_handle[ParameterHandle(parameters_by_name[parameter_name])] = bytes(value)

        transportation = self._transportation_handle_by_name("HLAreliable")
        callback_time = self._coerce_time(time) if time is not None else None
        for federate_key, subscriptions in self._federation_record().subscribed_directed_interactions.items():
            if federate_key == self._current_federate_key():
                continue
            if interaction_class_name not in subscriptions.get(object_class_name, set()):
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "receiveDirectedInteraction",
                interactionClass,
                objectInstance,
                values_by_handle,
                bytes(userSuppliedTag),
                transportation,
                self._current_federate_handle(),
                callback_time,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )
        return None

    def deleteObjectInstance(  # noqa: N802
        self,
        objectInstance: Any,
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("deleteObjectInstance", objectInstance, userSuppliedTag, time)
        self._require_joined("deleteObjectInstance")
        object_instance_value = self._normalize_handle(
            objectInstance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        federation = self._federation_record()
        try:
            record = federation.object_instances[object_instance_value]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(objectInstance)) from exc
        if self._current_federate_handle() not in set(record.attribute_owners.values()):
            raise DeletePrivilegeNotHeld(str(objectInstance))

        callback_time = self._coerce_time(time) if time is not None else None
        object_class_name = record.object_class_name
        for federate_key, subscriptions in federation.subscribed_object_attributes.items():
            if federate_key == self._current_federate_key() or object_class_name not in subscriptions:
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "removeObjectInstance",
                objectInstance,
                bytes(userSuppliedTag),
                self._current_federate_handle(),
                callback_time,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )

        if record.object_instance_name is not None:
            federation.object_instance_names.pop(record.object_instance_name, None)
        federation.object_instances.pop(object_instance_value, None)
        return None

    def localDeleteObjectInstance(self, objectInstance: Any) -> None:  # noqa: N802
        self._record("localDeleteObjectInstance", objectInstance)
        self._require_joined("localDeleteObjectInstance")
        self._object_instance_record_known(objectInstance)

    def requestAttributeValueUpdate(self, objectClassOrInstance: Any, attributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("requestAttributeValueUpdate", objectClassOrInstance, attributes, userSuppliedTag)
        self._require_joined("requestAttributeValueUpdate")
        if isinstance(objectClassOrInstance, ObjectInstanceHandle):
            self._request_instance_attribute_value_update(objectClassOrInstance, attributes, userSuppliedTag)
            return
        object_class_name = self._object_class_name(objectClassOrInstance)
        attribute_names = self._attribute_names_from_handles(object_class_name, attributes)
        attribute_handles = {AttributeHandle(self._attribute_handles(object_class_name)[name]) for name in attribute_names}
        for object_value, record in self._federation_record().object_instances.items():
            if record.object_class_name != object_class_name:
                continue
            self._deliver_value_update_requests(ObjectInstanceHandle(object_value), record, attribute_handles, userSuppliedTag)

    def requestAttributeTransportationTypeChange(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("requestAttributeTransportationTypeChange", objectInstance, attributes, transportationType)
        self._require_joined("requestAttributeTransportationTypeChange")
        record = self._object_instance_record_known(objectInstance)
        transportation_name = self.getTransportationTypeName(transportationType)
        transportation = self._transportation_handle_by_name(transportation_name)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, attributes)
        attribute_handles: set[AttributeHandle] = set()
        for attribute_name in attribute_names:
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            record.attribute_transportation[attribute_name] = transportation_name
            attribute_handles.add(AttributeHandle(self._attribute_handles(record.object_class_name)[attribute_name]))
        self._deliver_callback("confirmAttributeTransportationTypeChange", objectInstance, attribute_handles, transportation)

    def queryAttributeTransportationType(self, objectInstance: Any, attribute: Any) -> None:  # noqa: N802
        self._record("queryAttributeTransportationType", objectInstance, attribute)
        self._require_joined("queryAttributeTransportationType")
        record = self._object_instance_record_known(objectInstance)
        attribute_name = self._attribute_names_from_handles(record.object_class_name, {attribute})[0]
        transportation_name = record.attribute_transportation.get(
            attribute_name,
            self._default_attribute_transportation.get((record.object_class_name, attribute_name), "HLAreliable"),
        )
        self._deliver_callback(
            "reportAttributeTransportationType",
            objectInstance,
            attribute,
            self._transportation_handle_by_name(transportation_name),
        )

    def requestInteractionTransportationTypeChange(self, interactionClass: Any, transportationType: Any) -> None:  # noqa: N802
        self._record("requestInteractionTransportationTypeChange", interactionClass, transportationType)
        self._require_joined("requestInteractionTransportationTypeChange")
        interaction_class_name = self._interaction_class_name(interactionClass)
        if interaction_class_name not in self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()):
            raise InteractionClassNotPublished(interaction_class_name)
        transportation_name = self.getTransportationTypeName(transportationType)
        transportation = self._transportation_handle_by_name(transportation_name)
        self._federation_record().interaction_transportation[(self._current_federate_key(), interaction_class_name)] = transportation_name
        self._deliver_callback("confirmInteractionTransportationTypeChange", interactionClass, transportation)

    def queryInteractionTransportationType(self, federate: Any, interactionClass: Any) -> None:  # noqa: N802
        self._record("queryInteractionTransportationType", federate, interactionClass)
        self._require_joined("queryInteractionTransportationType")
        federate_value = self._normalize_handle(federate, FederateHandle, InvalidFederateHandle)
        if federate_value not in {handle.value for handle in self._federation_record().member_handles.values()}:
            raise InvalidFederateHandle(str(federate))
        interaction_class_name = self._interaction_class_name(interactionClass)
        transportation_name = self._federation_record().interaction_transportation.get(
            (federate_value, interaction_class_name),
            "HLAreliable",
        )
        self._deliver_callback(
            "reportInteractionTransportationType",
            FederateHandle(federate_value),
            interactionClass,
            self._transportation_handle_by_name(transportation_name),
        )

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
                federation.published_object_attributes.pop(self._federate_handle.value, None)
                federation.subscribed_object_attributes.pop(self._federate_handle.value, None)
                federation.subscribed_object_regions.pop(self._federate_handle.value, None)
                federation.published_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_interaction_regions.pop(self._federate_handle.value, None)
                federation.published_directed_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_directed_interactions.pop(self._federate_handle.value, None)
                federation.member_regions.pop(self._federate_handle.value, None)
                federation.member_region_bounds.pop(self._federate_handle.value, None)

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

    def _dimension_default_upper_bound(self, dimension_name: str) -> int:
        spec = self._dimension_spec(dimension_name)
        if spec is None or spec.upper_bound in {None, ""}:
            return (1 << 63) - 1
        try:
            return int(str(spec.upper_bound))
        except ValueError:
            return (1 << 63) - 1

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

    def _parameter_handles(self, interaction_class_name: str) -> dict[str, int]:
        catalog = self._catalog()
        try:
            spec = catalog.interaction_classes[interaction_class_name]
        except KeyError as exc:
            raise InteractionClassNotDefined(interaction_class_name) from exc
        return self._stable_handles(spec.parameters)

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

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle:
        try:
            return TransportationTypeHandle(self._transportation_handles()[name])
        except KeyError as exc:
            raise InvalidTransportationName(name) from exc

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

    def _object_instance_record_known(self, object_instance: Any) -> _ObjectInstanceRecord:
        object_instance_value = self._normalize_handle(
            object_instance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        try:
            return self._federation_record().object_instances[object_instance_value]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(object_instance)) from exc

    def _request_instance_attribute_value_update(self, object_instance: ObjectInstanceHandle, attributes: Any, user_supplied_tag: bytes) -> None:
        record = self._object_instance_record_known(object_instance)
        attribute_names = self._attribute_names_from_handles(record.object_class_name, attributes)
        attribute_handles = {AttributeHandle(self._attribute_handles(record.object_class_name)[name]) for name in attribute_names}
        self._deliver_value_update_requests(object_instance, record, attribute_handles, user_supplied_tag)

    def _deliver_value_update_requests(
        self,
        object_instance: ObjectInstanceHandle,
        record: _ObjectInstanceRecord,
        attribute_handles: set[AttributeHandle],
        user_supplied_tag: bytes,
    ) -> None:
        handles_by_name = self._attribute_handles(record.object_class_name)
        attributes_by_owner: dict[FederateHandle, set[AttributeHandle]] = {}
        for attribute in attribute_handles:
            attribute_name = self._attribute_name_by_handle(record.object_class_name, attribute)
            owner = record.attribute_owners.get(attribute_name)
            if owner is not None:
                attributes_by_owner.setdefault(owner, set()).add(AttributeHandle(handles_by_name[attribute_name]))
        for owner, owned_attributes in sorted(attributes_by_owner.items(), key=lambda item: item[0].value):
            self._deliver_to_federate_handle(owner, "provideAttributeValueUpdate", object_instance, owned_attributes, bytes(user_supplied_tag))

    def _current_federate_handle(self) -> FederateHandle:
        if self._federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        return self._federate_handle

    def _current_federate_key(self) -> int:
        return self._current_federate_handle().value

    def _published_attributes_for_current_federate(self, object_class_name: str) -> set[str]:
        return self._federation_record().published_object_attributes.setdefault(self._current_federate_key(), {}).get(object_class_name, set())

    def _region_dimension_names(self, federate_key: int, region: Any) -> set[str]:
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        try:
            return set(self._federation_record().member_regions[federate_key][region_value])
        except KeyError as exc:
            raise InvalidRegion(str(region)) from exc

    def _region_values_from_handles(self, regions: Any) -> set[int]:
        try:
            region_handles = tuple(regions)
        except TypeError as exc:
            raise InvalidRegion("Region handle set must be iterable") from exc
        region_values = {self._normalize_handle(region, RegionHandle, InvalidRegion) for region in region_handles}
        for region_value in region_values:
            self._region_dimension_names(self._current_federate_key(), RegionHandle(region_value))
        return region_values

    def _coerce_range_bounds(self, value: Any) -> RangeBounds:
        if isinstance(value, RangeBounds):
            bounds = value
        elif hasattr(value, "lower") and hasattr(value, "upper"):
            bounds = RangeBounds(int(value.lower), int(value.upper))
        elif hasattr(value, "lower_bound") and hasattr(value, "upper_bound"):
            bounds = RangeBounds(int(value.lower_bound), int(value.upper_bound))
        else:
            lower, upper = value
            bounds = RangeBounds(int(lower), int(upper))
        if int(bounds.lower) > int(bounds.upper):
            raise InvalidRangeBound(repr(value))
        return bounds

    def _attribute_region_pairs(self, object_class_name: str, attributes_and_regions: Any) -> tuple[tuple[set[str], set[int]], ...]:
        pairs: list[tuple[set[str], set[int]]] = []
        for pair in attributes_and_regions or ():
            if hasattr(pair, "attributes") and hasattr(pair, "regions"):
                attributes = pair.attributes
                regions = pair.regions
            elif hasattr(pair, "ahset") and hasattr(pair, "rhset"):
                attributes = pair.ahset
                regions = pair.rhset
            elif isinstance(pair, Mapping):
                attributes = pair.get("attributes") or pair.get("ahset") or pair.get("attribute_handles") or ()
                regions = pair.get("regions") or pair.get("rhset") or pair.get("region_handles") or ()
            elif isinstance(pair, (tuple, list)) and len(pair) >= 2:
                attributes, regions = pair[0], pair[1]
            else:
                raise InvalidRegionContext(f"Bad attribute/region pair: {pair!r}")
            attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
            region_values = {self._normalize_handle(region, RegionHandle, InvalidRegion) for region in set(regions)}
            for region_value in region_values:
                self._region_dimension_names(self._current_federate_key(), RegionHandle(region_value))
            pairs.append((attribute_names, region_values))
        return tuple(pairs)

    @staticmethod
    def _ranges_overlap(left: RangeBounds, right: RangeBounds) -> bool:
        return int(left.lower) <= int(right.upper) and int(right.lower) <= int(left.upper)

    def _regions_overlap_pair(self, source_key: int, source_region: int, target_key: int, target_region: int) -> bool:
        source_dims = self._federation_record().member_regions.get(source_key, {}).get(source_region, set())
        target_dims = self._federation_record().member_regions.get(target_key, {}).get(target_region, set())
        common_dimensions = set(source_dims) & set(target_dims)
        if not common_dimensions:
            return False
        source_bounds = self._federation_record().member_region_bounds.get(source_key, {}).get(source_region, {})
        target_bounds = self._federation_record().member_region_bounds.get(target_key, {}).get(target_region, {})
        for dimension_name in common_dimensions:
            default_bounds = RangeBounds(0, self._dimension_default_upper_bound(dimension_name))
            if not self._ranges_overlap(source_bounds.get(dimension_name, default_bounds), target_bounds.get(dimension_name, default_bounds)):
                return False
        return True

    def _region_sets_overlap(self, source_key: int, source_regions: set[int], target_key: int, target_regions: set[int]) -> bool:
        if not source_regions or not target_regions:
            return True
        return any(
            self._regions_overlap_pair(source_key, source_region, target_key, target_region)
            for source_region in source_regions
            for target_region in target_regions
        )

    def _reflectable_attribute_names_for_subscriber(
        self,
        source_key: int,
        subscriber_key: int,
        record: _ObjectInstanceRecord,
        subscribed_names: set[str],
    ) -> set[str]:
        region_subscription = (
            self._federation_record()
            .subscribed_object_regions.get(subscriber_key, {})
            .get(record.object_class_name, {})
        )
        if not region_subscription:
            return subscribed_names
        reflected: set[str] = set()
        for attribute_name in subscribed_names:
            target_regions = set(region_subscription.get(attribute_name, set()))
            source_regions = set(record.update_regions.get(attribute_name, set()))
            if self._region_sets_overlap(source_key, source_regions, subscriber_key, target_regions):
                reflected.add(attribute_name)
        return reflected

    def _attribute_name_by_handle(self, object_class_name: str, attribute: AttributeHandle) -> str:
        attribute_value = self._normalize_handle(attribute, AttributeHandle, InvalidAttributeHandle)
        names_by_handle = {value: name for name, value in self._attribute_handles(object_class_name).items()}
        try:
            return names_by_handle[attribute_value]
        except KeyError as exc:
            raise InvalidAttributeHandle(str(attribute)) from exc

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

    def _parameter_names_from_handles(self, interaction_class_name: str, parameters: Any) -> tuple[str, ...]:
        try:
            parameter_values = tuple(parameters)
        except TypeError as exc:
            raise InteractionParameterNotDefined("Parameter handle set must be iterable") from exc
        names_by_handle = {value: name for name, value in self._parameter_handles(interaction_class_name).items()}
        names: list[str] = []
        for parameter in parameter_values:
            parameter_value = self._normalize_handle(parameter, ParameterHandle, InteractionParameterNotDefined)
            try:
                names.append(names_by_handle[parameter_value])
            except KeyError as exc:
                raise InteractionParameterNotDefined(str(parameter)) from exc
        return tuple(names)

    def _interaction_class_names_from_handles(self, interaction_classes: Any) -> tuple[str, ...]:
        try:
            interaction_class_values = tuple(interaction_classes)
        except TypeError as exc:
            raise InteractionClassNotDefined("Interaction class handle set must be iterable") from exc
        if not interaction_class_values:
            raise InteractionClassNotDefined("Interaction class handle set cannot be empty")
        names_by_handle = {value: name for name, value in self._interaction_class_handles().items()}
        names: list[str] = []
        for interaction_class in interaction_class_values:
            interaction_class_value = self._normalize_handle(
                interaction_class,
                InteractionClassHandle,
                InvalidInteractionClassHandle,
            )
            try:
                names.append(names_by_handle[interaction_class_value])
            except KeyError as exc:
                raise InvalidInteractionClassHandle(str(interaction_class)) from exc
        return tuple(names)

    def _default_transportation_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> TransportationTypeHandle:
        transportation_names = {
            self._default_attribute_transportation.get((object_class_name, self._attribute_name_by_handle(object_class_name, attribute)), "HLAreliable")
            for attribute in values_by_handle
        }
        return self._transportation_handle_by_name(sorted(transportation_names)[0])

    def _default_order_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        orders = {
            self._default_attribute_order.get((object_class_name, self._attribute_name_by_handle(object_class_name, attribute)), OrderType.RECEIVE)
            for attribute in values_by_handle
        }
        return sorted(orders, key=lambda value: value.name)[0]

    def _discover_existing_objects_for_current_subscription(self, object_class_name: str) -> None:
        federation = self._federation_record()
        object_class_handle = ObjectClassHandle(self._object_class_handles()[object_class_name])
        for object_value, record in federation.object_instances.items():
            if record.object_class_name != object_class_name:
                continue
            owner_handles = {owner for owner in record.attribute_owners.values() if owner is not None}
            producing_federate = sorted(owner_handles, key=lambda handle: handle.value)[0] if owner_handles else self._current_federate_handle()
            if producing_federate == self._current_federate_handle():
                continue
            subscribed_names = (
                federation.subscribed_object_attributes.get(self._current_federate_key(), {})
                .get(object_class_name, set())
            )
            reflected_names = self._reflectable_attribute_names_for_subscriber(
                producing_federate.value,
                self._current_federate_key(),
                record,
                set(subscribed_names),
            )
            if not reflected_names:
                continue
            self._deliver_callback(
                "discoverObjectInstance",
                ObjectInstanceHandle(object_value),
                object_class_handle,
                record.object_instance_name or "",
                producing_federate,
            )

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
