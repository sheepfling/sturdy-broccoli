"""IEEE 1516.1-2025 RTI shim backend."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Mapping

from hla.backends.common import time_management as tm
from hla.rti.plugin_api import BackendRequest
from hla.rti1516_2025.datatypes import (
    ConfigurationResult,
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformation,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformation,
    FederationExecutionMemberInformationSet,
    MessageRetractionReturn,
    RangeBounds,
    TimeQueryReturn,
)
from hla.rti1516_2025.enums import (
    AdditionalSettingsResultCode,
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    RestoreStatus,
    SaveFailureReason,
    SaveStatus,
    ServiceGroup,
    SynchronizationPointFailureReason,
)
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
    FederateIsExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
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
    InvalidMessageRetractionHandle,
    InvalidMIM,
    InvalidObjectClassHandle,
    InvalidObjectInstanceHandle,
    InvalidOrderType,
    InvalidRangeBound,
    InvalidResignAction,
    InvalidRegion,
    InvalidRegionContext,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationTypeHandle,
    LogicalTimeAlreadyPassed,
    MessageCanNoLongerBeRetracted,
    NameNotFound,
    NoAcquisitionPending,
    NotConnected,
    ObjectClassNotDefined,
    ObjectClassNotPublished,
    ObjectInstanceNameInUse,
    ObjectInstanceNameNotReserved,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
    RegionDoesNotContainSpecifiedDimension,
    RestoreInProgress,
    RestoreNotInProgress,
    RestoreNotRequested,
    RTIinternalError,
    SaveInProgress,
    SaveNotInitiated,
    SaveNotInProgress,
    SynchronizationPointLabelNotAnnounced,
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
    MessageRetractionHandle,
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
MOM_2025_FEDERATE_ADJUST_LEAVES = frozenset(
    {
        "HLAsetTiming",
        "HLAmodifyAttributeState",
        "HLAsetServiceReporting",
        "HLAsetExceptionReporting",
        "HLAsetSwitches",
    }
)
MOM_2025_FEDERATION_ADJUST_LEAVES = frozenset({"HLAsetSwitches"})
MOM_2025_FEDERATE_REQUEST_LEAVES = frozenset(
    {
        "HLArequestPublications",
        "HLArequestSubscriptions",
        "HLArequestObjectInstancesThatCanBeDeleted",
        "HLArequestObjectInstancesUpdated",
        "HLArequestObjectInstancesReflected",
        "HLArequestUpdatesSent",
        "HLArequestInteractionsSent",
        "HLArequestReflectionsReceived",
        "HLArequestInteractionsReceived",
        "HLArequestObjectInstanceInformation",
        "HLArequestFOMmoduleData",
    }
)
MOM_2025_FEDERATION_REQUEST_LEAVES = frozenset(
    {
        "HLArequestSynchronizationPoints",
        "HLArequestSynchronizationPointStatus",
        "HLArequestFOMmoduleData",
        "HLArequestMIMdata",
    }
)
MOM_2025_FEDERATE_SERVICE_LEAVES = frozenset(
    {
        "HLAresignFederationExecution",
        "HLAsynchronizationPointAchieved",
        "HLAfederateSaveBegun",
        "HLAfederateSaveComplete",
        "HLAfederateRestoreComplete",
        "HLApublishObjectClassAttributes",
        "HLAunpublishObjectClassAttributes",
        "HLApublishInteractionClass",
        "HLAunpublishInteractionClass",
        "HLAsubscribeObjectClassAttributes",
        "HLAunsubscribeObjectClassAttributes",
        "HLAsubscribeInteractionClass",
        "HLAunsubscribeInteractionClass",
        "HLAdeleteObjectInstance",
        "HLAlocalDeleteObjectInstance",
        "HLArequestAttributeTransportationTypeChange",
        "HLArequestInteractionTransportationTypeChange",
        "HLAunconditionalAttributeOwnershipDivestiture",
        "HLAenableTimeRegulation",
        "HLAdisableTimeRegulation",
        "HLAenableTimeConstrained",
        "HLAdisableTimeConstrained",
        "HLAtimeAdvanceRequest",
        "HLAtimeAdvanceRequestAvailable",
        "HLAnextMessageRequest",
        "HLAnextMessageRequestAvailable",
        "HLAflushQueueRequest",
        "HLAenableAsynchronousDelivery",
        "HLAdisableAsynchronousDelivery",
        "HLAmodifyLookahead",
        "HLAchangeAttributeOrderType",
        "HLAchangeInteractionOrderType",
    }
)
MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES = frozenset(
    MOM_2025_FEDERATE_ADJUST_LEAVES
    | MOM_2025_FEDERATION_ADJUST_LEAVES
    | MOM_2025_FEDERATE_REQUEST_LEAVES
    | MOM_2025_FEDERATION_REQUEST_LEAVES
    | MOM_2025_FEDERATE_SERVICE_LEAVES
)


@dataclass(slots=True)
class _FederationRecord:
    logical_time_implementation_name: str = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    fom_modules: tuple[Any, ...] = ()
    mim_module: Any | None = None
    fom_catalog: Any | None = None
    members: dict[str, str] = field(default_factory=dict)
    member_handles: dict[str, FederateHandle] = field(default_factory=dict)
    member_ambassadors: dict[int, FederateAmbassador] = field(default_factory=dict)
    member_rtis: dict[int, "Shim2025RTIAmbassador"] = field(default_factory=dict)
    published_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_regions: dict[int, dict[str, dict[str, set[int]]]] = field(default_factory=dict)
    published_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interaction_regions: dict[int, dict[str, set[int]]] = field(default_factory=dict)
    directed_interaction_region_gates: dict[int, set[str]] = field(default_factory=dict)
    published_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    interaction_order: dict[tuple[int, str], OrderType] = field(default_factory=dict)
    member_regions: dict[int, dict[int, set[str]]] = field(default_factory=dict)
    member_region_bounds: dict[int, dict[int, dict[str, RangeBounds]]] = field(default_factory=dict)
    object_instances: dict[int, "_ObjectInstanceRecord"] = field(default_factory=dict)
    object_instance_names: dict[str, int] = field(default_factory=dict)
    reserved_object_instance_names: dict[str, int] = field(default_factory=dict)
    mom_object_instances_updated: dict[tuple[int, str], int] = field(default_factory=dict)
    mom_object_instances_reflected: dict[tuple[int, str], int] = field(default_factory=dict)
    mom_updates_sent: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_reflections_received: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_interactions_sent: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_interactions_received: dict[tuple[int, str, str], int] = field(default_factory=dict)
    attribute_scope_state: dict[tuple[int, int, str], bool] = field(default_factory=dict)
    interaction_transportation: dict[tuple[int, str], str] = field(default_factory=dict)
    queued_tso_callbacks: dict[int, "_QueuedTsoCallback"] = field(default_factory=dict)
    delivered_retraction_handles: set[int] = field(default_factory=set)
    delivered_retraction_targets: dict[int, FederateHandle] = field(default_factory=dict)
    saved_labels: set[str] = field(default_factory=set)
    saved_object_instances: dict[str, dict[int, "_ObjectInstanceRecord"]] = field(default_factory=dict)
    saved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_reserved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_next_object_instance_handles: dict[str, int] = field(default_factory=dict)
    saved_member_logical_times: dict[str, dict[int, Any]] = field(default_factory=dict)
    saved_member_time_states: dict[str, dict[int, dict[str, Any]]] = field(default_factory=dict)
    saved_published_object_attributes: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_object_attributes: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_object_regions: dict[str, dict[int, dict[str, dict[str, set[int]]]]] = field(default_factory=dict)
    saved_published_interactions: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_subscribed_interactions: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_subscribed_interaction_regions: dict[str, dict[int, dict[str, set[int]]]] = field(default_factory=dict)
    saved_directed_interaction_region_gates: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_published_directed_interactions: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_directed_interactions: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_member_regions: dict[str, dict[int, dict[int, set[str]]]] = field(default_factory=dict)
    saved_member_region_bounds: dict[str, dict[int, dict[int, dict[str, RangeBounds]]]] = field(default_factory=dict)
    saved_interaction_order: dict[str, dict[tuple[int, str], OrderType]] = field(default_factory=dict)
    saved_interaction_transportation: dict[str, dict[tuple[int, str], str]] = field(default_factory=dict)
    saved_queued_tso_callbacks: dict[str, dict[int, "_QueuedTsoCallback"]] = field(default_factory=dict)
    saved_delivered_retraction_handles: dict[str, set[int]] = field(default_factory=dict)
    saved_delivered_retraction_targets: dict[str, dict[int, FederateHandle]] = field(default_factory=dict)
    save_label: str | None = None
    save_status: dict[int, SaveStatus] = field(default_factory=dict)
    restore_label: str | None = None
    restore_status: dict[int, RestoreStatus] = field(default_factory=dict)
    synchronization_points: dict[str, "_SynchronizationPointRecord"] = field(default_factory=dict)
    next_federate_handle: int = 1
    next_object_instance_handle: int = 1
    next_region_handle: int = 1
    next_message_retraction_handle: int = 1


@dataclass(slots=True)
class _ObjectInstanceRecord:
    object_class_name: str
    object_instance_name: str | None
    attribute_owners: dict[str, FederateHandle | None] = field(default_factory=dict)
    attribute_divesting: set[str] = field(default_factory=set)
    attribute_candidates: dict[str, list[tuple[FederateHandle, bytes]]] = field(default_factory=dict)
    update_regions: dict[str, set[int]] = field(default_factory=dict)
    attribute_transportation: dict[str, str] = field(default_factory=dict)
    attribute_order: dict[str, OrderType] = field(default_factory=dict)


@dataclass(slots=True)
class _SynchronizationPointRecord:
    user_supplied_tag: bytes
    required_federates: set[int]
    achieved_federates: set[int] = field(default_factory=set)
    failed_federates: set[int] = field(default_factory=set)
    synchronized: bool = False


@dataclass(slots=True)
class _QueuedTsoCallback:
    target_federate: FederateHandle
    callback_time: Any
    serial: int
    method_name: str
    args: tuple[Any, ...]


@dataclass(slots=True)
class _QueuedCallback:
    target_federate: FederateHandle | None
    method_name: str
    args: tuple[Any, ...]


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
        self._callbacks_enabled = True
        self._evoked_callback_queue: list[_QueuedCallback] = []
        self._logical_time_implementation_name = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        self._logical_time_factory = self._get_time_factory(_DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False
        self._asynchronous_delivery_enabled = False
        self._pending_time_advance: tm.TimeAdvanceRequestState | None = None
        self._switches = dict(_SWITCH_DEFAULTS)
        self._automatic_resign_directive = ResignAction.NO_ACTION
        self._mom_report_period_seconds: float | None = None
        self._default_attribute_transportation: dict[tuple[str, str], str] = {}
        self._default_attribute_order: dict[tuple[str, str], OrderType] = {}
        self._service_report_serial_number = 0
        self._service_report_records: list[dict[str, Any]] = []
        self._known_object_classes: dict[int, str] = {}
        self._known_object_names: dict[str, int] = {}
        self._locally_deleted_objects: set[int] = set()
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
        self._callbacks_enabled = True
        self._evoked_callback_queue.clear()
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
        if self._joined:
            raise FederateIsExecutionMember("Cannot disconnect while joined to a federation execution")
        self._release_join()
        self._connected = False
        self._joined = False
        self._federation_name = None
        self._federate_name = None
        self._federate_handle = None
        self._federate_ambassador = None
        self._callback_model = None
        self._callbacks_enabled = True
        self._evoked_callback_queue.clear()
        self._logical_time_implementation_name = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        self._logical_time_factory = self._get_time_factory(_DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False
        self._asynchronous_delivery_enabled = False
        self._pending_time_advance = None
        self._switches = dict(_SWITCH_DEFAULTS)
        self._automatic_resign_directive = ResignAction.NO_ACTION
        self._mom_report_period_seconds = None
        self._default_attribute_transportation.clear()
        self._default_attribute_order.clear()
        self._service_report_serial_number = 0
        self._service_report_records.clear()
        self._known_object_classes.clear()
        self._known_object_names.clear()
        self._locally_deleted_objects.clear()

    def forceConnectionLost(self, faultDescription: str = "simulated connection lost") -> None:  # noqa: N802
        """Test harness hook for injecting a non-orderly connection loss."""

        self._record("forceConnectionLost", faultDescription)
        self._require_connected("forceConnectionLost")
        self._deliver_callback_now("connectionLost", str(faultDescription))
        self.disconnect()

    def force_connection_lost(self, fault_description: str = "simulated connection lost") -> None:
        self.forceConnectionLost(fault_description)

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
        if federation.save_label is not None:
            raise SaveInProgress("A federation save is already in progress")
        if federation.restore_label is not None:
            raise RestoreInProgress("A federation restore is already in progress")
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
        self._federate_handle = FederateHandle(federation.next_federate_handle)
        federation.next_federate_handle += 1
        federation.member_handles[federate_name] = self._federate_handle
        federation.member_rtis[self._federate_handle.value] = self
        if self._federate_ambassador is not None:
            federation.member_ambassadors[self._federate_handle.value] = self._federate_ambassador
        federation.published_object_attributes.setdefault(self._federate_handle.value, {})
        federation.subscribed_object_attributes.setdefault(self._federate_handle.value, {})
        federation.subscribed_object_regions.setdefault(self._federate_handle.value, {})
        federation.published_interactions.setdefault(self._federate_handle.value, set())
        federation.subscribed_interactions.setdefault(self._federate_handle.value, set())
        federation.subscribed_interaction_regions.setdefault(self._federate_handle.value, {})
        federation.directed_interaction_region_gates.setdefault(self._federate_handle.value, set())
        federation.published_directed_interactions.setdefault(self._federate_handle.value, {})
        federation.subscribed_directed_interactions.setdefault(self._federate_handle.value, {})
        federation.member_regions.setdefault(self._federate_handle.value, {})
        federation.member_region_bounds.setdefault(self._federate_handle.value, {})
        self._select_logical_time_implementation(federation.logical_time_implementation_name)
        self._federation_name = federation_name
        self._federate_name = federate_name
        self._joined = True
        for label, point in federation.synchronization_points.items():
            if point.synchronized:
                continue
            point.required_federates.add(self._federate_handle.value)
            self._deliver_to_federate_handle(
                self._federate_handle,
                "announceSynchronizationPoint",
                label,
                point.user_supplied_tag,
            )
        return self._federate_handle

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        self._record("resignFederationExecution", resignAction)
        self._require_joined("resignFederationExecution")
        if not isinstance(resignAction, ResignAction):
            raise InvalidResignAction(str(resignAction))
        if resignAction is ResignAction.NO_ACTION:
            if self._resigning_federate_has_pending_acquisitions():
                raise OwnershipAcquisitionPending("Cannot resign with pending ownership acquisition using NO_ACTION")
            if self._resigning_federate_owns_attributes():
                raise FederateOwnsAttributes("Cannot resign while owning attributes using NO_ACTION")
        self._apply_resign_action(resignAction)
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "federateResigned"):
            self._deliver_callback("federateResigned", self._resign_reason_description(resignAction))
        self._release_join()
        self._joined = False
        self._federation_name = None
        self._federate_name = None
        self._federate_handle = None

    def registerFederationSynchronizationPoint(  # noqa: N802
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: Any | None = None,
    ) -> None:
        self._record("registerFederationSynchronizationPoint", synchronizationPointLabel, userSuppliedTag, synchronizationSet)
        self._require_joined("registerFederationSynchronizationPoint")
        if not isinstance(synchronizationPointLabel, str) or not synchronizationPointLabel:
            raise RTIinternalError("Synchronization point label must be a non-empty string")
        federation = self._federation_record()
        if synchronizationPointLabel in federation.synchronization_points:
            self._deliver_callback(
                "synchronizationPointRegistrationFailed",
                synchronizationPointLabel,
                SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
            )
            return
        required = self._synchronization_required_federates(synchronizationSet)
        federation.synchronization_points[synchronizationPointLabel] = _SynchronizationPointRecord(
            user_supplied_tag=bytes(userSuppliedTag),
            required_federates=required,
        )
        self._deliver_callback("synchronizationPointRegistrationSucceeded", synchronizationPointLabel)
        for federate_key in sorted(required):
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "announceSynchronizationPoint",
                synchronizationPointLabel,
                bytes(userSuppliedTag),
            )

    def synchronizationPointAchieved(self, synchronizationPointLabel: str, successfully: bool = True) -> None:  # noqa: N802
        self._record("synchronizationPointAchieved", synchronizationPointLabel, successfully)
        self._require_joined("synchronizationPointAchieved")
        federation = self._federation_record()
        try:
            point = federation.synchronization_points[synchronizationPointLabel]
        except KeyError as exc:
            raise SynchronizationPointLabelNotAnnounced(synchronizationPointLabel) from exc
        federate_key = self._current_federate_key()
        if federate_key not in point.required_federates:
            raise SynchronizationPointLabelNotAnnounced(synchronizationPointLabel)
        if successfully:
            point.achieved_federates.add(federate_key)
            point.failed_federates.discard(federate_key)
        else:
            point.failed_federates.add(federate_key)
            point.achieved_federates.discard(federate_key)
        reported = point.achieved_federates | point.failed_federates
        if not point.synchronized and point.required_federates <= reported:
            point.synchronized = True
            failed = {FederateHandle(value) for value in sorted(point.failed_federates)}
            for target_key in sorted(point.required_federates):
                self._deliver_to_federate_handle(
                    FederateHandle(target_key),
                    "federationSynchronized",
                    synchronizationPointLabel,
                    failed,
                )

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        self._record("evokeCallback", approximateMinimumTimeInSeconds)
        self._require_connected("evokeCallback")
        if not self._callbacks_enabled or not self._evoked_callback_queue:
            return False
        self._deliver_queued_callback(self._evoked_callback_queue.pop(0))
        return True

    def evokeMultipleCallbacks(  # noqa: N802
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        self._record("evokeMultipleCallbacks", approximateMinimumTimeInSeconds, approximateMaximumTimeInSeconds)
        self._require_connected("evokeMultipleCallbacks")
        if not self._callbacks_enabled or not self._evoked_callback_queue:
            return False
        while self._evoked_callback_queue:
            self._deliver_queued_callback(self._evoked_callback_queue.pop(0))
        return True

    def enableCallbacks(self) -> None:  # noqa: N802
        self._record("enableCallbacks")
        self._require_connected("enableCallbacks")
        self._callbacks_enabled = True

    def disableCallbacks(self) -> None:  # noqa: N802
        self._record("disableCallbacks")
        self._require_connected("disableCallbacks")
        self._callbacks_enabled = False

    def requestFederationSave(self, label: str, time: Any | None = None) -> None:  # noqa: N802
        self._record("requestFederationSave", label, time)
        self._require_joined("requestFederationSave")
        federation = self._federation_record()
        if federation.save_label is not None:
            raise SaveInProgress("A federation save is already in progress")
        if federation.restore_label is not None:
            raise RestoreInProgress("A federation restore is already in progress")
        if time is not None:
            save_time = self._coerce_time(time)
            if save_time < self._logical_time:
                raise LogicalTimeAlreadyPassed(str(time))
        else:
            save_time = None
        federation.save_label = str(label)
        federation.save_status = {
            handle.value: SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE
            for handle in federation.member_handles.values()
        }
        for federate_handle in federation.member_handles.values():
            if save_time is None:
                self._deliver_to_federate_handle(federate_handle, "initiateFederateSave", str(label))
            else:
                self._deliver_to_federate_handle(federate_handle, "initiateFederateSave", str(label), save_time)

    def federateSaveBegun(self) -> None:  # noqa: N802
        self._record("federateSaveBegun")
        self._require_joined("federateSaveBegun")
        federation = self._federation_record()
        if federation.save_label is None:
            raise SaveNotInitiated("No federation save is in progress")
        federation.save_status[self._current_federate_key()] = SaveStatus.FEDERATE_SAVING

    def federateSaveComplete(self) -> None:  # noqa: N802
        self._record("federateSaveComplete")
        self._complete_save(success=True)

    def federateSaveNotComplete(self) -> None:  # noqa: N802
        self._record("federateSaveNotComplete")
        self._complete_save(success=False)

    def abortFederationSave(self) -> None:  # noqa: N802
        self._record("abortFederationSave")
        self._require_joined("abortFederationSave")
        federation = self._federation_record()
        if federation.save_label is None:
            raise SaveNotInProgress("No federation save is in progress")
        for federate_handle in federation.member_handles.values():
            self._deliver_to_federate_handle(federate_handle, "federationNotSaved", SaveFailureReason.SAVE_ABORTED)
        federation.save_label = None
        federation.save_status.clear()

    def queryFederationSaveStatus(self) -> None:  # noqa: N802
        self._record("queryFederationSaveStatus")
        self._require_joined("queryFederationSaveStatus")
        federation = self._federation_record()
        response = [
            FederateHandleSaveStatusPair(
                handle,
                federation.save_status.get(handle.value, SaveStatus.NO_SAVE_IN_PROGRESS),
            )
            for handle in federation.member_handles.values()
        ]
        self._deliver_callback("federationSaveStatusResponse", response)

    def requestFederationRestore(self, label: str) -> None:  # noqa: N802
        self._record("requestFederationRestore", label)
        self._require_joined("requestFederationRestore")
        federation = self._federation_record()
        if federation.save_label is not None:
            raise SaveInProgress("A federation save is already in progress")
        if federation.restore_label is not None:
            raise RestoreInProgress("A federation restore is already in progress")
        restore_label = str(label)
        if restore_label not in federation.saved_labels:
            self._deliver_callback("requestFederationRestoreFailed", restore_label)
            return
        federation.restore_label = restore_label
        federation.restore_status = {
            handle.value: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
            for handle in federation.member_handles.values()
        }
        self._deliver_callback("requestFederationRestoreSucceeded", restore_label)
        for federate_name, federate_handle in federation.member_handles.items():
            self._deliver_to_federate_handle(federate_handle, "federationRestoreBegun")
            self._deliver_to_federate_handle(federate_handle, "initiateFederateRestore", restore_label, federate_name, federate_handle)

    def federateRestoreComplete(self) -> None:  # noqa: N802
        self._record("federateRestoreComplete")
        self._complete_restore(success=True)

    def federateRestoreNotComplete(self) -> None:  # noqa: N802
        self._record("federateRestoreNotComplete")
        self._complete_restore(success=False)

    def abortFederationRestore(self) -> None:  # noqa: N802
        self._record("abortFederationRestore")
        self._require_joined("abortFederationRestore")
        federation = self._federation_record()
        if federation.restore_label is None:
            raise RestoreNotInProgress("No federation restore is in progress")
        for federate_handle in federation.member_handles.values():
            self._deliver_to_federate_handle(federate_handle, "federationNotRestored", RestoreFailureReason.RESTORE_ABORTED)
        federation.restore_label = None
        federation.restore_status.clear()

    def queryFederationRestoreStatus(self) -> None:  # noqa: N802
        self._record("queryFederationRestoreStatus")
        self._require_joined("queryFederationRestoreStatus")
        federation = self._federation_record()
        response = [
            FederateRestoreStatus(
                handle,
                handle,
                federation.restore_status.get(handle.value, RestoreStatus.NO_RESTORE_IN_PROGRESS),
            )
            for handle in federation.member_handles.values()
        ]
        self._deliver_callback("federationRestoreStatusResponse", response)

    def enableTimeRegulation(self, lookahead: Any) -> None:  # noqa: N802
        self._record("enableTimeRegulation", lookahead)
        self._require_joined("enableTimeRegulation")
        self._lookahead = self._coerce_interval(lookahead)
        self._time_regulation_enabled = True
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "timeRegulationEnabled"):
            self._deliver_callback("timeRegulationEnabled", self._logical_time)

    def disableTimeRegulation(self) -> None:  # noqa: N802
        self._record("disableTimeRegulation")
        self._require_joined("disableTimeRegulation")
        self._time_regulation_enabled = False
        self._lookahead = self._logical_time_factory.makeZero()
        self._process_time_advances()

    def enableTimeConstrained(self) -> None:  # noqa: N802
        self._record("enableTimeConstrained")
        self._require_joined("enableTimeConstrained")
        self._time_constrained_enabled = True
        if self._federate_ambassador is not None and hasattr(self._federate_ambassador, "timeConstrainedEnabled"):
            self._deliver_callback("timeConstrainedEnabled", self._logical_time)
        self._process_time_advances()

    def disableTimeConstrained(self) -> None:  # noqa: N802
        self._record("disableTimeConstrained")
        self._require_joined("disableTimeConstrained")
        self._time_constrained_enabled = False
        self._process_time_advances()

    def enableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("enableAsynchronousDelivery")
        self._require_joined("enableAsynchronousDelivery")
        self._asynchronous_delivery_enabled = True

    def disableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("disableAsynchronousDelivery")
        self._require_joined("disableAsynchronousDelivery")
        self._asynchronous_delivery_enabled = False

    def timeAdvanceRequest(self, time: Any) -> None:  # noqa: N802
        self._record("timeAdvanceRequest", time)
        self._require_joined("timeAdvanceRequest")
        self._request_time_advance("timeAdvanceRequest", time)

    def timeAdvanceRequestAvailable(self, time: Any) -> None:  # noqa: N802
        self._record("timeAdvanceRequestAvailable", time)
        self._require_joined("timeAdvanceRequestAvailable")
        self._request_time_advance("timeAdvanceRequestAvailable", time)

    def nextMessageRequest(self, time: Any) -> None:  # noqa: N802
        self._record("nextMessageRequest", time)
        self._require_joined("nextMessageRequest")
        self._request_time_advance("nextMessageRequest", time)

    def nextMessageRequestAvailable(self, time: Any) -> None:  # noqa: N802
        self._record("nextMessageRequestAvailable", time)
        self._require_joined("nextMessageRequestAvailable")
        self._request_time_advance("nextMessageRequestAvailable", time)

    def flushQueueRequest(self, time: Any) -> None:  # noqa: N802
        self._record("flushQueueRequest", time)
        self._require_joined("flushQueueRequest")
        self._request_time_advance("flushQueueRequest", time)

    def queryGALT(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryGALT")
        self._require_joined("queryGALT")
        return self._query_galt_for(self)

    def queryLogicalTime(self) -> Any:  # noqa: N802
        self._record("queryLogicalTime")
        self._require_joined("queryLogicalTime")
        return self._logical_time

    def queryLITS(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryLITS")
        self._require_joined("queryLITS")
        return self._query_lits_for(self)

    def modifyLookahead(self, lookahead: Any) -> None:  # noqa: N802
        self._record("modifyLookahead", lookahead)
        self._require_joined("modifyLookahead")
        if not self._time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Cannot modify lookahead before enableTimeRegulation")
        self._lookahead = self._coerce_interval(lookahead)
        self._process_time_advances()

    def retract(self, retraction: Any) -> None:
        self._record("retract", retraction)
        self._require_joined("retract")
        retraction_value = self._normalize_handle(
            retraction,
            MessageRetractionHandle,
            InvalidMessageRetractionHandle,
        )
        federation = self._federation_record()
        if federation.queued_tso_callbacks.pop(retraction_value, None) is not None:
            return
        if retraction_value in federation.delivered_retraction_handles:
            target = federation.delivered_retraction_targets.pop(retraction_value, None)
            if target is not None:
                self._deliver_to_federate_handle(target, "requestRetraction", MessageRetractionHandle(retraction_value))
                return
            raise MessageCanNoLongerBeRetracted(str(retraction))
        raise InvalidMessageRetractionHandle(str(retraction))

    def queryLookahead(self) -> Any:  # noqa: N802
        self._record("queryLookahead")
        self._require_joined("queryLookahead")
        if not self._time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Cannot query lookahead before enableTimeRegulation")
        return self._lookahead

    def _request_time_advance(self, mode: str, time: Any) -> None:
        requested_time = self._coerce_time(time)
        if requested_time < self._logical_time:
            raise LogicalTimeAlreadyPassed(str(requested_time))
        self._pending_time_advance = tm.TimeAdvanceRequestState(mode, requested_time)
        self._process_time_advances()

    def _process_time_advances(self) -> None:
        if not self._joined or self._federation_name is None:
            return
        federation = self._federation_record()
        progressed = True
        while progressed:
            progressed = False
            for member in list(federation.member_rtis.values()):
                if member._pending_time_advance is None:
                    continue
                if member._try_grant_pending_time_advance():
                    progressed = True

    def _try_grant_pending_time_advance(self) -> bool:
        request = self._pending_time_advance
        if request is None:
            return False
        federation = self._federation_record()
        state = self._time_management_state()
        decision = tm.compute_grant_decision(
            self._time_management_federation(federation),
            state,
            request,
            enforce_galt=True,
            factory=self._logical_time_factory,
        )
        if not decision.can_grant or decision.grant_time is None:
            return False
        self._deliver_due_tso_callbacks_for_request(decision.deliverable_messages)
        self._logical_time = decision.grant_time
        self._pending_time_advance = None
        if request.mode == "flushQueueRequest":
            self._deliver_callback("flushQueueGrant", decision.grant_time, decision.optimistic_time or decision.grant_time)
        else:
            self._deliver_callback("timeAdvanceGrant", decision.grant_time)
        return True

    def _time_management_state(self) -> Any:
        return SimpleNamespace(
            handle=self._current_federate_handle(),
            current_time=self._logical_time,
            lookahead=self._lookahead,
            time_regulation_enabled=self._time_regulation_enabled,
            time_constrained_enabled=self._time_constrained_enabled,
            pending_time_advance=self._pending_time_advance,
            zero_lookahead_tarnmr_restriction=False,
        )

    def _time_management_federation(self, federation: _FederationRecord) -> Any:
        federates = {handle: member._time_management_state() for handle, member in federation.member_rtis.items()}
        messages = [
            SimpleNamespace(
                timestamp=queued.callback_time,
                recipient=queued.target_federate,
                sequence=queued.serial,
                retraction_handle=MessageRetractionHandle(handle_value),
                retracted=False,
                delivered=False,
                queued_handle=handle_value,
            )
            for handle_value, queued in federation.queued_tso_callbacks.items()
        ]
        return SimpleNamespace(federates=federates, tso_messages=messages)

    def _query_galt_for(self, target: "Shim2025RTIAmbassador") -> TimeQueryReturn:
        federation = target._federation_record()
        others = [
            member._time_management_state()
            for handle, member in federation.member_rtis.items()
            if handle != target._current_federate_key() and member._time_regulation_enabled
        ]
        if others:
            query = tm.compute_galt(
                SimpleNamespace(federates={index: state for index, state in enumerate(others, start=1)}, tso_messages=[]),
                target._time_management_state(),
                include_self=False,
                factory=target._logical_time_factory,
            )
            return TimeQueryReturn(query.time_is_valid, query.time)
        return TimeQueryReturn(True, target._logical_time)

    def _query_lits_for(self, target: "Shim2025RTIAmbassador") -> TimeQueryReturn:
        federation = target._federation_record()
        query = tm.compute_lits(
            target._time_management_federation(federation),
            target._time_management_state(),
            include_galt=False,
            factory=target._logical_time_factory,
        )
        galt = target._query_galt_for(target)
        candidates = [query.time] if query.time_is_valid and query.time is not None else []
        if galt.timeIsValid and galt.time is not None:
            candidates.append(galt.time)
        if not candidates:
            return TimeQueryReturn(False, None)
        return TimeQueryReturn(True, min(candidates))

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        if not self._time_regulation_enabled:
            raise InvalidLogicalTime("Timestamp-order messages require time regulation to be enabled")
        lower_bound = tm.valid_tso_lower_bound(self._time_management_state(), factory=self._logical_time_factory)
        if lower_bound is not None and timestamp < lower_bound:
            raise InvalidLogicalTime(
                f"TSO timestamp {timestamp!r} is earlier than logical time/lookahead bound {lower_bound!r}"
            )

    def _deliver_due_tso_callbacks_for_request(self, deliverable_messages: tuple[Any, ...]) -> None:
        federation = self._federation_record()
        for message in deliverable_messages:
            handle_value = getattr(message, "queued_handle", None)
            if handle_value is None:
                continue
            queued = federation.queued_tso_callbacks.pop(handle_value, None)
            if queued is None:
                continue
            federation.delivered_retraction_handles.add(handle_value)
            federation.delivered_retraction_targets[handle_value] = queued.target_federate
            self._deliver_to_federate_handle(queued.target_federate, queued.method_name, *queued.args)

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
        try:
            attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        except InvalidAttributeHandle as exc:
            raise AttributeNotDefined(str(exc)) from exc
        federation = self._federation_record()
        published = federation.published_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set())
        had_match = self._has_object_registration_interest(federation, self._current_federate_key(), object_class_name)
        published.update(attribute_names)
        has_match = self._has_object_registration_interest(federation, self._current_federate_key(), object_class_name)
        if has_match and not had_match:
            self._deliver_callback("startRegistrationForObjectClass", ObjectClassHandle(self._object_class_handles()[object_class_name]))

    def unpublishObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClass", objectClass)
        self._require_joined("unpublishObjectClass")
        object_class_name = self._object_class_name(objectClass)
        federation = self._federation_record()
        had_match = self._has_object_registration_interest(federation, self._current_federate_key(), object_class_name)
        self._federation_record().published_object_attributes.setdefault(self._current_federate_key(), {}).pop(object_class_name, None)
        if had_match:
            self._deliver_callback("stopRegistrationForObjectClass", ObjectClassHandle(self._object_class_handles()[object_class_name]))

    def unpublishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClassAttributes", objectClass, attributes)
        self._require_joined("unpublishObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        try:
            attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        except InvalidAttributeHandle as exc:
            raise AttributeNotDefined(str(exc)) from exc
        federation = self._federation_record()
        published = federation.published_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set())
        had_match = self._has_object_registration_interest(federation, self._current_federate_key(), object_class_name)
        published.difference_update(attribute_names)
        if not published:
            federation.published_object_attributes[self._current_federate_key()].pop(object_class_name, None)
        has_match = self._has_object_registration_interest(federation, self._current_federate_key(), object_class_name)
        if had_match and not has_match:
            self._deliver_callback("stopRegistrationForObjectClass", ObjectClassHandle(self._object_class_handles()[object_class_name]))

    def subscribeObjectClassAttributes(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributes", objectClass, attributes, *unused)
        self._require_joined("subscribeObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        try:
            attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        except InvalidAttributeHandle as exc:
            raise AttributeNotDefined(str(exc)) from exc
        federation = self._federation_record()
        affected_publishers = self._matching_object_publishers(federation, object_class_name, attribute_names)
        before_matches = {
            publisher_key: self._has_object_registration_interest(federation, publisher_key, object_class_name)
            for publisher_key in affected_publishers
        }
        federation.subscribed_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set()).update(attribute_names)
        self._discover_existing_objects_for_current_subscription(object_class_name)
        for publisher_key in affected_publishers:
            if not before_matches[publisher_key] and self._has_object_registration_interest(federation, publisher_key, object_class_name):
                self._deliver_to_federate_handle(
                    FederateHandle(publisher_key),
                    "startRegistrationForObjectClass",
                    ObjectClassHandle(self._object_class_handles()[object_class_name]),
                )

    def subscribeObjectClassAttributesPassively(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassively", objectClass, attributes, *unused)
        self.subscribeObjectClassAttributes(objectClass, attributes, *unused)

    def unsubscribeObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClass", objectClass)
        self._require_joined("unsubscribeObjectClass")
        object_class_name = self._object_class_name(objectClass)
        federation = self._federation_record()
        affected_publishers = self._matching_object_publishers(
            federation,
            object_class_name,
            federation.subscribed_object_attributes.setdefault(self._current_federate_key(), {}).get(object_class_name, set()),
        )
        before_matches = {
            publisher_key: self._has_object_registration_interest(federation, publisher_key, object_class_name)
            for publisher_key in affected_publishers
        }
        federation.subscribed_object_attributes.setdefault(self._current_federate_key(), {}).pop(object_class_name, None)
        for publisher_key in affected_publishers:
            if before_matches[publisher_key] and not self._has_object_registration_interest(federation, publisher_key, object_class_name):
                self._deliver_to_federate_handle(
                    FederateHandle(publisher_key),
                    "stopRegistrationForObjectClass",
                    ObjectClassHandle(self._object_class_handles()[object_class_name]),
                )

    def unsubscribeObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributes", objectClass, attributes)
        self._require_joined("unsubscribeObjectClassAttributes")
        object_class_name = self._object_class_name(objectClass)
        try:
            attribute_names = set(self._attribute_names_from_handles(object_class_name, attributes))
        except InvalidAttributeHandle as exc:
            raise AttributeNotDefined(str(exc)) from exc
        federation = self._federation_record()
        affected_publishers = self._matching_object_publishers(federation, object_class_name, attribute_names)
        before_matches = {
            publisher_key: self._has_object_registration_interest(federation, publisher_key, object_class_name)
            for publisher_key in affected_publishers
        }
        subscribed = federation.subscribed_object_attributes.setdefault(self._current_federate_key(), {}).setdefault(object_class_name, set())
        subscribed.difference_update(attribute_names)
        if not subscribed:
            federation.subscribed_object_attributes[self._current_federate_key()].pop(object_class_name, None)
        for publisher_key in affected_publishers:
            if before_matches[publisher_key] and not self._has_object_registration_interest(federation, publisher_key, object_class_name):
                self._deliver_to_federate_handle(
                    FederateHandle(publisher_key),
                    "stopRegistrationForObjectClass",
                    ObjectClassHandle(self._object_class_handles()[object_class_name]),
                )

    def publishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("publishInteractionClass", interactionClass)
        self._require_joined("publishInteractionClass")
        federation = self._federation_record()
        interaction_class_name = self._interaction_class_name(interactionClass)
        had_match = self._has_interaction_interest(federation, self._current_federate_key(), interaction_class_name)
        federation.published_interactions.setdefault(self._current_federate_key(), set()).add(interaction_class_name)
        has_match = self._has_interaction_interest(federation, self._current_federate_key(), interaction_class_name)
        if has_match and not had_match:
            self._deliver_callback("turnInteractionsOn", InteractionClassHandle(self._interaction_class_handles()[interaction_class_name]))

    def unpublishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unpublishInteractionClass", interactionClass)
        self._require_joined("unpublishInteractionClass")
        federation = self._federation_record()
        interaction_class_name = self._interaction_class_name(interactionClass)
        had_match = self._has_interaction_interest(federation, self._current_federate_key(), interaction_class_name)
        federation.published_interactions.setdefault(self._current_federate_key(), set()).discard(interaction_class_name)
        if had_match:
            self._deliver_callback("turnInteractionsOff", InteractionClassHandle(self._interaction_class_handles()[interaction_class_name]))

    def subscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClass", interactionClass)
        self._require_joined("subscribeInteractionClass")
        federation = self._federation_record()
        interaction_class_name = self._interaction_class_name(interactionClass)
        affected_publishers = self._matching_interaction_publishers(federation, interaction_class_name)
        before_matches = {
            publisher_key: self._has_interaction_interest(federation, publisher_key, interaction_class_name)
            for publisher_key in affected_publishers
        }
        federation.subscribed_interactions.setdefault(self._current_federate_key(), set()).add(interaction_class_name)
        for publisher_key in affected_publishers:
            if not before_matches[publisher_key] and self._has_interaction_interest(federation, publisher_key, interaction_class_name):
                self._deliver_to_federate_handle(
                    FederateHandle(publisher_key),
                    "turnInteractionsOn",
                    InteractionClassHandle(self._interaction_class_handles()[interaction_class_name]),
                )

    def subscribeInteractionClassPassively(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassively", interactionClass)
        self.subscribeInteractionClass(interactionClass)

    def unsubscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClass", interactionClass)
        self._require_joined("unsubscribeInteractionClass")
        federation = self._federation_record()
        interaction_class_name = self._interaction_class_name(interactionClass)
        affected_publishers = self._matching_interaction_publishers(federation, interaction_class_name)
        before_matches = {
            publisher_key: self._has_interaction_interest(federation, publisher_key, interaction_class_name)
            for publisher_key in affected_publishers
        }
        subscribed = federation.subscribed_interactions.setdefault(self._current_federate_key(), set())
        subscribed.discard(interaction_class_name)
        federation.subscribed_interaction_regions.setdefault(self._current_federate_key(), {}).pop(
            interaction_class_name,
            None,
        )
        federation.directed_interaction_region_gates.setdefault(self._current_federate_key(), set()).discard(
            interaction_class_name
        )
        for publisher_key in affected_publishers:
            if before_matches[publisher_key] and not self._has_interaction_interest(federation, publisher_key, interaction_class_name):
                self._deliver_to_federate_handle(
                    FederateHandle(publisher_key),
                    "turnInteractionsOff",
                    InteractionClassHandle(self._interaction_class_handles()[interaction_class_name]),
                )

    def subscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("subscribeInteractionClassWithRegions")
        interaction_class_name = self._interaction_class_name(interactionClass)
        region_values = self._region_values_from_handles(regions)
        federation = self._federation_record()
        federation.subscribed_interactions.setdefault(self._current_federate_key(), set()).add(interaction_class_name)
        federation.directed_interaction_region_gates.setdefault(self._current_federate_key(), set()).add(interaction_class_name)
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
        self._evaluate_attribute_scope_advisories()

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
            self._evaluate_attribute_scope_advisories()

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
        self._evaluate_attribute_scope_advisories()

    def registerObjectInstanceWithRegions(self, objectClass: Any, attributesAndRegions: Any, objectInstanceName: str | None = None) -> ObjectInstanceHandle:  # noqa: N802
        self._record("registerObjectInstanceWithRegions", objectClass, attributesAndRegions, objectInstanceName)
        handle = self.registerObjectInstance(objectClass, objectInstanceName)
        record = self._object_instance_record(handle)
        for attribute_names, region_values in self._attribute_region_pairs(record.object_class_name, attributesAndRegions):
            for attribute_name in attribute_names:
                record.update_regions.setdefault(attribute_name, set()).update(region_values)
        self._evaluate_attribute_scope_advisories()
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
        self._evaluate_attribute_scope_advisories()

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
        coerced_order = self._coerce_order_type(orderType)
        for attribute_name in self._attribute_names_from_handles(object_class_name, attributes):
            self._default_attribute_order[(object_class_name, attribute_name)] = coerced_order

    def changeAttributeOrderType(self, objectInstance: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeAttributeOrderType", objectInstance, attributes, orderType)
        self._require_joined("changeAttributeOrderType")
        record = self._object_instance_record_known(objectInstance)
        coerced_order = self._coerce_order_type(orderType)
        for attribute_name in self._attribute_names_from_handles(record.object_class_name, attributes):
            if record.attribute_owners.get(attribute_name) != self._federate_handle:
                raise AttributeNotOwned(attribute_name)
            record.attribute_order[attribute_name] = coerced_order

    def changeInteractionOrderType(self, interactionClass: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeInteractionOrderType", interactionClass, orderType)
        self._require_joined("changeInteractionOrderType")
        interaction_class_name = self._interaction_class_name(interactionClass)
        if interaction_class_name not in self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()):
            raise InteractionClassNotPublished(interaction_class_name)
        self._federation_record().interaction_order[(self._current_federate_key(), interaction_class_name)] = self._coerce_order_type(orderType)

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
        self._deliver_mom_service_report(record)
        return dict(record)

    def serviceReportRecordsSnapshot(self) -> tuple[dict[str, Any], ...]:  # noqa: N802
        self._record("serviceReportRecordsSnapshot")
        self._require_joined("serviceReportRecordsSnapshot")
        return tuple(dict(record) for record in self._service_report_records)

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("reserveObjectInstanceName", objectInstanceName)
        self._require_joined("reserveObjectInstanceName")
        self._require_no_save_or_restore("reserveObjectInstanceName")
        name = self._normalize_reserved_object_instance_name(objectInstanceName, method_name="reserveObjectInstanceName")
        federation = self._federation_record()
        if name in federation.object_instance_names or name in federation.reserved_object_instance_names:
            self._deliver_callback("objectInstanceNameReservationFailed", name)
            return
        federation.reserved_object_instance_names[name] = self._current_federate_key()
        self._deliver_callback("objectInstanceNameReservationSucceeded", name)

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("releaseObjectInstanceName", objectInstanceName)
        self._require_joined("releaseObjectInstanceName")
        self._require_no_save_or_restore("releaseObjectInstanceName")
        name = self._normalize_reserved_object_instance_name(objectInstanceName, method_name="releaseObjectInstanceName")
        federation = self._federation_record()
        if federation.reserved_object_instance_names.get(name) != self._current_federate_key():
            raise ObjectInstanceNameNotReserved(name)
        federation.reserved_object_instance_names.pop(name, None)

    def reserveMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("reserveMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("reserveMultipleObjectInstanceNames")
        self._require_no_save_or_restore("reserveMultipleObjectInstanceNames")
        names = self._normalize_reserved_object_instance_name_set(
            objectInstanceNames,
            method_name="reserveMultipleObjectInstanceNames",
        )
        federation = self._federation_record()
        if any(name in federation.object_instance_names or name in federation.reserved_object_instance_names for name in names):
            self._deliver_callback("multipleObjectInstanceNameReservationFailed", names)
            return
        federate_key = self._current_federate_key()
        for name in names:
            federation.reserved_object_instance_names[name] = federate_key
        self._deliver_callback("multipleObjectInstanceNameReservationSucceeded", names)

    def releaseMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("releaseMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("releaseMultipleObjectInstanceNames")
        self._require_no_save_or_restore("releaseMultipleObjectInstanceNames")
        names = self._normalize_reserved_object_instance_name_set(
            objectInstanceNames,
            method_name="releaseMultipleObjectInstanceNames",
        )
        federation = self._federation_record()
        federate_key = self._current_federate_key()
        for name in sorted(names):
            if federation.reserved_object_instance_names.get(name) != federate_key:
                raise ObjectInstanceNameNotReserved(name)
        for name in names:
            federation.reserved_object_instance_names.pop(name, None)

    def momReportPeriodSecondsSnapshot(self) -> float | None:  # noqa: N802
        self._record("momReportPeriodSecondsSnapshot")
        self._require_joined("momReportPeriodSecondsSnapshot")
        return self._mom_report_period_seconds

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
            reserved_by = federation.reserved_object_instance_names.get(objectInstanceName)
            if reserved_by is not None and reserved_by != self._current_federate_key():
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
            federation.reserved_object_instance_names.pop(objectInstanceName, None)
        object_class_handle = ObjectClassHandle(self._object_class_handles()[object_class_name])
        source_key = self._current_federate_key()
        self._known_object_classes[handle.value] = object_class_name
        if objectInstanceName is not None:
            self._known_object_names[objectInstanceName] = handle.value
        for federate_key, subscriptions in federation.subscribed_object_attributes.items():
            if federate_key == self._current_federate_key():
                continue
            discovery_class_name = self._subscribed_discovery_class_name(
                federate_key,
                object_class_name,
            )
            if discovery_class_name is None:
                continue
            subscribed_names = set(subscriptions.get(discovery_class_name, set()))
            reflected_names = self._reflectable_attribute_names_for_subscriber(
                source_key,
                federate_key,
                federation.object_instances[handle.value],
                discovery_class_name,
                subscribed_names,
            )
            if reflected_names:
                self._deliver_to_federate_handle(
                    FederateHandle(federate_key),
                    "discoverObjectInstance",
                    handle,
                    ObjectClassHandle(self._object_class_handles()[discovery_class_name]),
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
        if callback_time is not None:
            self._validate_tso_send_time(callback_time)
        retraction_handles: list[MessageRetractionHandle] = []
        federation = self._federation_record()
        self._increment_mom_count(federation.mom_object_instances_updated, (self._current_federate_key(), object_class_name))
        self._increment_mom_count(
            federation.mom_updates_sent,
            (self._current_federate_key(), object_class_name, self.getTransportationTypeName(transportation)),
        )
        for federate_key, subscriptions in federation.subscribed_object_attributes.items():
            if federate_key == self._current_federate_key():
                continue
            discovery_class_name = self._known_object_classes_for_federate(
                federate_key,
                objectInstance,
                record.object_class_name,
            )
            if discovery_class_name is None:
                continue
            subscribed_names = self._reflectable_attribute_names_for_subscriber(
                self._current_federate_key(),
                federate_key,
                record,
                discovery_class_name,
                set(subscriptions.get(discovery_class_name, set())),
            )
            reflected = {
                AttributeHandle(self._attribute_handles(discovery_class_name)[self._attribute_name_by_handle(object_class_name, handle)]): value
                for handle, value in values_by_handle.items()
                if self._attribute_name_by_handle(object_class_name, handle) in subscribed_names
            }
            if not reflected:
                continue
            target_rti = federation.member_rtis.get(federate_key)
            if target_rti is not None and objectInstance.value in target_rti._locally_deleted_objects:
                self._deliver_to_federate_handle(
                    FederateHandle(federate_key),
                    "discoverObjectInstance",
                    objectInstance,
                    ObjectClassHandle(self._object_class_handles()[discovery_class_name]),
                    record.object_instance_name or "",
                    self._current_federate_handle(),
                )
            self._increment_mom_count(federation.mom_object_instances_reflected, (federate_key, object_class_name))
            self._increment_mom_count(
                federation.mom_reflections_received,
                (federate_key, object_class_name, self.getTransportationTypeName(transportation)),
            )
            sent_regions = {
                RegionHandle(region_value)
                for handle in reflected
                for region_value in record.update_regions.get(self._attribute_name_by_handle(object_class_name, handle), set())
            }
            if callback_time is not None:
                retraction_handles.append(
                    self._queue_tso_callback(
                        FederateHandle(federate_key),
                        callback_time,
                        "reflectAttributeValues",
                        objectInstance,
                        reflected,
                        bytes(userSuppliedTag),
                        transportation,
                        self._current_federate_handle(),
                        sent_regions,
                        callback_time,
                        OrderType.TIMESTAMP,
                        OrderType.TIMESTAMP,
                    )
                )
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "reflectAttributeValues",
                objectInstance,
                reflected,
                bytes(userSuppliedTag),
                transportation,
                self._current_federate_handle(),
                sent_regions,
                None,
                self._attribute_order_for(record, reflected),
                self._attribute_order_for(record, reflected),
                None,
            )
        if callback_time is not None:
            handle = retraction_handles[0] if retraction_handles else MessageRetractionHandle(0)
            return MessageRetractionReturn(bool(retraction_handles), handle)
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
        parameters_by_name = self._parameter_handles(interaction_class_name)
        values_by_handle: dict[ParameterHandle, bytes] = {}
        for parameter, value in dict(parameterValues).items():
            parameter_name = self._parameter_names_from_handles(interaction_class_name, {parameter})[0]
            values_by_handle[ParameterHandle(parameters_by_name[parameter_name])] = bytes(value)
        if self._handle_mom_interaction(interaction_class_name, values_by_handle):
            return None
        if interaction_class_name not in self._federation_record().published_interactions.setdefault(self._current_federate_key(), set()):
            raise InteractionClassNotPublished(interaction_class_name)
        transportation = self._interaction_transportation_for(interaction_class_name)
        callback_time = self._coerce_time(time) if time is not None else None
        if callback_time is not None:
            self._validate_tso_send_time(callback_time)
        retraction_handles: list[MessageRetractionHandle] = []
        federation = self._federation_record()
        self._increment_mom_count(
            federation.mom_interactions_sent,
            (self._current_federate_key(), interaction_class_name, self.getTransportationTypeName(transportation)),
        )
        for federate_key, subscriptions in federation.subscribed_interactions.items():
            if federate_key == self._current_federate_key() or interaction_class_name not in subscriptions:
                continue
            self._increment_mom_count(
                federation.mom_interactions_received,
                (federate_key, interaction_class_name, self.getTransportationTypeName(transportation)),
            )
            if callback_time is not None:
                retraction_handles.append(
                    self._queue_tso_callback(
                        FederateHandle(federate_key),
                        callback_time,
                        "receiveInteraction",
                        interactionClass,
                        values_by_handle,
                        bytes(userSuppliedTag),
                        transportation,
                        self._current_federate_handle(),
                        set(),
                        callback_time,
                        OrderType.TIMESTAMP,
                        OrderType.TIMESTAMP,
                    )
                )
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
                self._interaction_order_for(interaction_class_name),
                self._interaction_order_for(interaction_class_name),
                None,
            )
        if callback_time is not None:
            handle = retraction_handles[0] if retraction_handles else MessageRetractionHandle(0)
            return MessageRetractionReturn(bool(retraction_handles), handle)
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
        transportation = self._interaction_transportation_for(interaction_class_name)
        callback_time = self._coerce_time(time) if time is not None else None
        if callback_time is not None:
            self._validate_tso_send_time(callback_time)
        federation = self._federation_record()
        self._increment_mom_count(
            federation.mom_interactions_sent,
            (self._current_federate_key(), interaction_class_name, self.getTransportationTypeName(transportation)),
        )
        for federate_key, subscriptions in federation.subscribed_interactions.items():
            if federate_key == self._current_federate_key() or interaction_class_name not in subscriptions:
                continue
            target_regions = self._federation_record().subscribed_interaction_regions.get(federate_key, {}).get(
                interaction_class_name,
                set(),
            )
            if target_regions and not self._region_sets_overlap(self._current_federate_key(), source_regions, federate_key, target_regions):
                continue
            self._increment_mom_count(
                federation.mom_interactions_received,
                (federate_key, interaction_class_name, self.getTransportationTypeName(transportation)),
            )
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
                self._interaction_order_for(interaction_class_name),
                self._interaction_order_for(interaction_class_name),
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
        federation = self._federation_record()
        source_regions = self._object_instance_region_values(record)
        retraction_handles: list[MessageRetractionHandle] = []
        self._increment_mom_count(
            federation.mom_interactions_sent,
            (self._current_federate_key(), interaction_class_name, self.getTransportationTypeName(transportation)),
        )
        for federate_key, subscriptions in federation.subscribed_directed_interactions.items():
            if federate_key == self._current_federate_key():
                continue
            if interaction_class_name not in subscriptions.get(object_class_name, set()):
                continue
            gated_interactions = federation.directed_interaction_region_gates.get(federate_key, set())
            if interaction_class_name in gated_interactions:
                target_regions = federation.subscribed_interaction_regions.get(federate_key, {}).get(interaction_class_name, set())
                if not target_regions or not self._region_sets_overlap(
                    self._current_federate_key(),
                    source_regions,
                    federate_key,
                    target_regions,
                ):
                    continue
            self._increment_mom_count(
                federation.mom_interactions_received,
                (federate_key, interaction_class_name, self.getTransportationTypeName(transportation)),
            )
            if callback_time is not None:
                retraction_handles.append(
                    self._queue_tso_callback(
                        FederateHandle(federate_key),
                        callback_time,
                        "receiveDirectedInteraction",
                        interactionClass,
                        objectInstance,
                        values_by_handle,
                        bytes(userSuppliedTag),
                        transportation,
                        self._current_federate_handle(),
                        callback_time,
                        OrderType.TIMESTAMP,
                        OrderType.TIMESTAMP,
                    )
                )
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
                self._interaction_order_for(interaction_class_name),
                self._interaction_order_for(interaction_class_name),
                None,
            )
        if callback_time is not None:
            handle = retraction_handles[0] if retraction_handles else MessageRetractionHandle(0)
            return MessageRetractionReturn(bool(retraction_handles), handle)
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
        record = self._object_instance_record_known(objectInstance)
        object_instance_value = self._normalize_handle(
            objectInstance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        self._known_object_classes.pop(object_instance_value, None)
        if record.object_instance_name is not None:
            self._known_object_names.pop(record.object_instance_name, None)
        self._locally_deleted_objects.add(object_instance_value)

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
            if current_owner is None:
                record.attribute_owners[attribute_name] = self._federate_handle
                self._deliver_callback("attributeOwnershipAcquisitionNotification", objectInstance, {attribute_handle}, bytes(userSuppliedTag))
            elif attribute_name in record.attribute_divesting:
                self._add_attribute_candidate(record, attribute_name, self._federate_handle, bytes(userSuppliedTag))
                self._deliver_to_federate_handle(
                    current_owner,
                    "requestDivestitureConfirmation",
                    objectInstance,
                    {attribute_handle},
                    bytes(userSuppliedTag),
                )
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

    def getFederateHandle(self, federateName: str) -> FederateHandle:  # noqa: N802
        self._record("getFederateHandle", federateName)
        self._require_joined("getFederateHandle")
        federation = self._federation_record()
        try:
            return federation.member_handles[str(federateName)]
        except KeyError as exc:
            raise NameNotFound(str(federateName)) from exc

    def getFederateName(self, federate: Any) -> str:  # noqa: N802
        self._record("getFederateName", federate)
        self._require_joined("getFederateName")
        federate_value = self._normalize_handle(federate, FederateHandle, InvalidFederateHandle)
        federation = self._federation_record()
        names_by_handle = {handle.value: name for name, handle in federation.member_handles.items()}
        try:
            return names_by_handle[federate_value]
        except KeyError as exc:
            raise InvalidFederateHandle(str(federate)) from exc

    def getKnownObjectClassHandle(self, objectInstance: Any) -> ObjectClassHandle:  # noqa: N802
        self._record("getKnownObjectClassHandle", objectInstance)
        self._require_joined("getKnownObjectClassHandle")
        object_instance_value = self._normalize_handle(
            objectInstance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        try:
            record = self._federation_record().object_instances[object_instance_value]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(objectInstance)) from exc
        known_class_name = self._known_object_classes.get(object_instance_value)
        if known_class_name is not None:
            return ObjectClassHandle(self._object_class_handles()[known_class_name])
        if self._current_federate_handle() in set(record.attribute_owners.values()):
            self._known_object_classes[object_instance_value] = record.object_class_name
            if record.object_instance_name is not None:
                self._known_object_names[record.object_instance_name] = object_instance_value
            return ObjectClassHandle(self._object_class_handles()[record.object_class_name])
        raise ObjectInstanceNotKnown(str(objectInstance))

    def getObjectInstanceHandle(self, objectInstanceName: str) -> ObjectInstanceHandle:  # noqa: N802
        self._record("getObjectInstanceHandle", objectInstanceName)
        self._require_joined("getObjectInstanceHandle")
        try:
            return ObjectInstanceHandle(self._known_object_names[str(objectInstanceName)])
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(objectInstanceName)) from exc

    def getObjectInstanceName(self, objectInstance: Any) -> str:  # noqa: N802
        self._record("getObjectInstanceName", objectInstance)
        self._require_joined("getObjectInstanceName")
        object_instance_value = self._normalize_handle(
            objectInstance,
            ObjectInstanceHandle,
            InvalidObjectInstanceHandle,
        )
        record = self._object_instance_record_known(objectInstance)
        if object_instance_value in self._known_object_classes:
            if record.object_instance_name is None:
                raise ObjectInstanceNotKnown(str(objectInstance))
            return record.object_instance_name
        if self._current_federate_handle() in set(record.attribute_owners.values()):
            self._known_object_classes[object_instance_value] = record.object_class_name
            if record.object_instance_name is not None:
                self._known_object_names[record.object_instance_name] = object_instance_value
                return record.object_instance_name
        raise ObjectInstanceNotKnown(str(objectInstance))

    def getOrderType(self, orderTypeName: str) -> OrderType:  # noqa: N802
        self._record("getOrderType", orderTypeName)
        self._require_joined("getOrderType")
        normalized = str(orderTypeName).strip().lower()
        if normalized in {"hlareceive", "receive", "ro"}:
            return OrderType.RECEIVE
        if normalized in {"hlatimestamp", "timestamp", "tso"}:
            return OrderType.TIMESTAMP
        raise InvalidOrderType(str(orderTypeName))

    def getOrderName(self, orderType: Any) -> str:  # noqa: N802
        self._record("getOrderName", orderType)
        self._require_joined("getOrderName")
        try:
            coerced = orderType if isinstance(orderType, OrderType) else OrderType(orderType)
        except Exception as exc:
            raise InvalidOrderType(str(orderType)) from exc
        if coerced is OrderType.RECEIVE:
            return "HLAreceive"
        if coerced is OrderType.TIMESTAMP:
            return "HLAtimestamp"
        raise InvalidOrderType(str(orderType))

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
        if value:
            federation = self._federation_record()
            current_key = self._current_federate_key()
            for key in tuple(federation.attribute_scope_state):
                if key[0] == current_key:
                    federation.attribute_scope_state.pop(key, None)
            self._evaluate_attribute_scope_advisories()

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

    def getAutomaticResignDirective(self) -> ResignAction:  # noqa: N802
        self._record("getAutomaticResignDirective")
        self._require_joined("getAutomaticResignDirective")
        return self._automatic_resign_directive

    def setAutomaticResignDirective(self, value: ResignAction) -> None:  # noqa: N802
        self._record("setAutomaticResignDirective", value)
        self._require_joined("setAutomaticResignDirective")
        try:
            self._automatic_resign_directive = value if isinstance(value, ResignAction) else ResignAction(value)
        except Exception as exc:
            raise RTIinternalError(f"setAutomaticResignDirective requires a ResignAction value; got {value!r}") from exc

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
            if self._joined:
                try:
                    self.resignFederationExecution(self._automatic_resign_directive)
                except (FederateOwnsAttributes, OwnershipAcquisitionPending):
                    self.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
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
        if not self._callbacks_enabled:
            self._evoked_callback_queue.append(_QueuedCallback(None, method_name, args))
            return
        self._deliver_callback_now(method_name, *args)

    def _deliver_callback_now(self, method_name: str, *args: Any) -> None:
        if self._federate_ambassador is None:
            raise RTIinternalError(f"Cannot deliver {method_name} without a connected federate ambassador")
        callback = getattr(self._federate_ambassador, method_name, None)
        if callback is None:
            return
        callback(*args)

    def _deliver_to_federate_handle(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        federation = self._federation_record()
        target_rti = federation.member_rtis.get(federate_handle.value)
        if target_rti is not None and not target_rti._callbacks_enabled:
            target_rti._evoked_callback_queue.append(_QueuedCallback(None, method_name, args))
            return
        self._deliver_to_federate_handle_now(federate_handle, method_name, *args)

    def _deliver_to_federate_handle_now(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        federation = self._federation_record()
        ambassador = federation.member_ambassadors.get(federate_handle.value)
        if ambassador is None:
            raise InvalidFederateHandle(f"Unknown federate handle {federate_handle!r}")
        target_rti = federation.member_rtis.get(federate_handle.value)
        if target_rti is not None:
            target_rti._apply_object_callback_state(method_name, args)
        callback = getattr(ambassador, method_name, None)
        if callback is None:
            return
        callback(*args)

    def _apply_object_callback_state(self, method_name: str, args: tuple[Any, ...]) -> None:
        if method_name == "discoverObjectInstance" and len(args) >= 3:
            object_instance = args[0]
            object_class = args[1]
            object_name = args[2]
            try:
                object_instance_value = self._normalize_handle(
                    object_instance,
                    ObjectInstanceHandle,
                    InvalidObjectInstanceHandle,
                )
                object_class_name = self._object_class_name(object_class)
            except Exception:
                return
            self._known_object_classes[object_instance_value] = object_class_name
            if isinstance(object_name, str) and object_name:
                self._known_object_names[object_name] = object_instance_value
            self._locally_deleted_objects.discard(object_instance_value)
            return
        if method_name == "removeObjectInstance" and args:
            try:
                object_instance_value = self._normalize_handle(
                    args[0],
                    ObjectInstanceHandle,
                    InvalidObjectInstanceHandle,
                )
            except Exception:
                return
            object_names = [
                name for name, known_handle in self._known_object_names.items() if known_handle == object_instance_value
            ]
            for object_name in object_names:
                self._known_object_names.pop(object_name, None)
            self._known_object_classes.pop(object_instance_value, None)
            self._locally_deleted_objects.discard(object_instance_value)

    def _deliver_queued_callback(self, queued: _QueuedCallback) -> None:
        if queued.target_federate is None:
            self._deliver_callback_now(queued.method_name, *queued.args)
        else:
            self._deliver_to_federate_handle_now(queued.target_federate, queued.method_name, *queued.args)

    def _deliver_mom_service_report(self, report: Mapping[str, Any]) -> None:
        federation = self._federation_record()
        for federate_key, ambassador in federation.member_ambassadors.items():
            rti = federation.member_rtis.get(federate_key)
            if rti is None or getattr(ambassador, "momServiceReport", None) is None or not rti._switches["service_reporting"]:
                continue
            rti._deliver_callback("momServiceReport", dict(report))

    def _queue_tso_callback(self, target_federate: FederateHandle, callback_time: Any, method_name: str, *args: Any) -> MessageRetractionHandle:
        federation = self._federation_record()
        handle = MessageRetractionHandle(federation.next_message_retraction_handle)
        federation.next_message_retraction_handle += 1
        federation.queued_tso_callbacks[handle.value] = _QueuedTsoCallback(
            target_federate=target_federate,
            callback_time=callback_time,
            serial=handle.value,
            method_name=method_name,
            args=(*args, handle),
        )
        self._process_time_advances()
        return handle

    def _deliver_due_tso_callbacks(self) -> None:
        federation = self._federation_record()
        due = sorted(
            (
                (handle_value, queued)
                for handle_value, queued in federation.queued_tso_callbacks.items()
                if queued.target_federate == self._current_federate_handle() and queued.callback_time <= self._logical_time
            ),
            key=lambda item: (item[1].callback_time, item[1].serial),
        )
        for handle_value, queued in due:
            federation.queued_tso_callbacks.pop(handle_value, None)
            federation.delivered_retraction_handles.add(handle_value)
            federation.delivered_retraction_targets[handle_value] = queued.target_federate
            self._deliver_to_federate_handle(queued.target_federate, queued.method_name, *queued.args)

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

    def _complete_save(self, *, success: bool) -> None:
        self._require_joined("federateSaveComplete")
        federation = self._federation_record()
        if federation.save_label is None:
            raise SaveNotInitiated("No federation save is in progress")
        federation.save_status[self._current_federate_key()] = SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
        if not success:
            for federate_handle in federation.member_handles.values():
                self._deliver_to_federate_handle(
                    federate_handle,
                    "federationNotSaved",
                    SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,
                )
            federation.save_label = None
            federation.save_status.clear()
            return
        if federation.save_status and all(status is SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE for status in federation.save_status.values()):
            label = federation.save_label
            assert label is not None
            federation.saved_labels.add(label)
            federation.saved_object_instances[label] = copy.deepcopy(federation.object_instances)
            federation.saved_object_instance_names[label] = dict(federation.object_instance_names)
            federation.saved_reserved_object_instance_names[label] = dict(federation.reserved_object_instance_names)
            federation.saved_next_object_instance_handles[label] = federation.next_object_instance_handle
            federation.saved_member_logical_times[label] = {
                federate_key: rti._logical_time
                for federate_key, rti in federation.member_rtis.items()
            }
            federation.saved_published_object_attributes[label] = copy.deepcopy(federation.published_object_attributes)
            federation.saved_subscribed_object_attributes[label] = copy.deepcopy(federation.subscribed_object_attributes)
            federation.saved_subscribed_object_regions[label] = copy.deepcopy(federation.subscribed_object_regions)
            federation.saved_published_interactions[label] = copy.deepcopy(federation.published_interactions)
            federation.saved_subscribed_interactions[label] = copy.deepcopy(federation.subscribed_interactions)
            federation.saved_subscribed_interaction_regions[label] = copy.deepcopy(federation.subscribed_interaction_regions)
            federation.saved_directed_interaction_region_gates[label] = copy.deepcopy(federation.directed_interaction_region_gates)
            federation.saved_published_directed_interactions[label] = copy.deepcopy(federation.published_directed_interactions)
            federation.saved_subscribed_directed_interactions[label] = copy.deepcopy(federation.subscribed_directed_interactions)
            federation.saved_member_regions[label] = copy.deepcopy(federation.member_regions)
            federation.saved_member_region_bounds[label] = copy.deepcopy(federation.member_region_bounds)
            federation.saved_queued_tso_callbacks[label] = copy.deepcopy(federation.queued_tso_callbacks)
            federation.saved_delivered_retraction_handles[label] = set(federation.delivered_retraction_handles)
            federation.saved_delivered_retraction_targets[label] = dict(federation.delivered_retraction_targets)
            federation.saved_member_time_states[label] = {
                federate_key: {
                    "lookahead": rti._lookahead,
                    "time_regulation_enabled": rti._time_regulation_enabled,
                    "time_constrained_enabled": rti._time_constrained_enabled,
                    "asynchronous_delivery_enabled": rti._asynchronous_delivery_enabled,
                    "callbacks_enabled": rti._callbacks_enabled,
                    "automatic_resign_directive": rti._automatic_resign_directive,
                    "switches": copy.deepcopy(rti._switches),
                    "default_attribute_transportation": copy.deepcopy(rti._default_attribute_transportation),
                    "default_attribute_order": copy.deepcopy(rti._default_attribute_order),
                }
                for federate_key, rti in federation.member_rtis.items()
            }
            federation.saved_interaction_order[label] = copy.deepcopy(federation.interaction_order)
            federation.saved_interaction_transportation[label] = copy.deepcopy(federation.interaction_transportation)
            for federate_handle in federation.member_handles.values():
                self._deliver_to_federate_handle(federate_handle, "federationSaved")
            federation.save_label = None
            federation.save_status.clear()

    def _complete_restore(self, *, success: bool) -> None:
        self._require_joined("federateRestoreComplete")
        federation = self._federation_record()
        if federation.restore_label is None:
            raise RestoreNotRequested("No federation restore is in progress")
        federation.restore_status[self._current_federate_key()] = RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
        if not success:
            for federate_handle in federation.member_handles.values():
                self._deliver_to_federate_handle(
                    federate_handle,
                    "federationNotRestored",
                    RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE,
                )
            federation.restore_label = None
            federation.restore_status.clear()
            return
        if federation.restore_status and all(
            status is RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
            for status in federation.restore_status.values()
        ):
            label = federation.restore_label
            assert label is not None
            federation.object_instances = copy.deepcopy(federation.saved_object_instances.get(label, {}))
            federation.object_instance_names = dict(federation.saved_object_instance_names.get(label, {}))
            federation.reserved_object_instance_names = dict(
                federation.saved_reserved_object_instance_names.get(label, {})
            )
            federation.published_object_attributes = copy.deepcopy(
                federation.saved_published_object_attributes.get(label, federation.published_object_attributes)
            )
            federation.subscribed_object_attributes = copy.deepcopy(
                federation.saved_subscribed_object_attributes.get(label, federation.subscribed_object_attributes)
            )
            federation.subscribed_object_regions = copy.deepcopy(
                federation.saved_subscribed_object_regions.get(label, federation.subscribed_object_regions)
            )
            federation.published_interactions = copy.deepcopy(
                federation.saved_published_interactions.get(label, federation.published_interactions)
            )
            federation.subscribed_interactions = copy.deepcopy(
                federation.saved_subscribed_interactions.get(label, federation.subscribed_interactions)
            )
            federation.subscribed_interaction_regions = copy.deepcopy(
                federation.saved_subscribed_interaction_regions.get(label, federation.subscribed_interaction_regions)
            )
            federation.directed_interaction_region_gates = copy.deepcopy(
                federation.saved_directed_interaction_region_gates.get(label, federation.directed_interaction_region_gates)
            )
            federation.published_directed_interactions = copy.deepcopy(
                federation.saved_published_directed_interactions.get(label, federation.published_directed_interactions)
            )
            federation.subscribed_directed_interactions = copy.deepcopy(
                federation.saved_subscribed_directed_interactions.get(label, federation.subscribed_directed_interactions)
            )
            federation.member_regions = copy.deepcopy(
                federation.saved_member_regions.get(label, federation.member_regions)
            )
            federation.member_region_bounds = copy.deepcopy(
                federation.saved_member_region_bounds.get(label, federation.member_region_bounds)
            )
            federation.queued_tso_callbacks = copy.deepcopy(
                federation.saved_queued_tso_callbacks.get(label, federation.queued_tso_callbacks)
            )
            federation.delivered_retraction_handles = set(
                federation.saved_delivered_retraction_handles.get(label, federation.delivered_retraction_handles)
            )
            federation.delivered_retraction_targets = dict(
                federation.saved_delivered_retraction_targets.get(label, federation.delivered_retraction_targets)
            )
            federation.interaction_order = copy.deepcopy(
                federation.saved_interaction_order.get(label, federation.interaction_order)
            )
            federation.interaction_transportation = copy.deepcopy(
                federation.saved_interaction_transportation.get(label, federation.interaction_transportation)
            )
            federation.next_object_instance_handle = federation.saved_next_object_instance_handles.get(
                label,
                federation.next_object_instance_handle,
            )
            for federate_key, logical_time in federation.saved_member_logical_times.get(label, {}).items():
                rti = federation.member_rtis.get(federate_key)
                if rti is not None:
                    rti._logical_time = logical_time
            for federate_key, values in federation.saved_member_time_states.get(label, {}).items():
                rti = federation.member_rtis.get(federate_key)
                if rti is None:
                    continue
                rti._lookahead = values.get("lookahead", rti._lookahead)
                rti._time_regulation_enabled = bool(
                    values.get("time_regulation_enabled", rti._time_regulation_enabled)
                )
                rti._time_constrained_enabled = bool(
                    values.get("time_constrained_enabled", rti._time_constrained_enabled)
                )
                rti._asynchronous_delivery_enabled = bool(
                    values.get(
                        "asynchronous_delivery_enabled",
                        rti._asynchronous_delivery_enabled,
                    )
                )
                rti._callbacks_enabled = bool(values.get("callbacks_enabled", rti._callbacks_enabled))
                rti._automatic_resign_directive = values.get(
                    "automatic_resign_directive",
                    rti._automatic_resign_directive,
                )
                rti._switches = dict(values.get("switches", rti._switches))
                rti._default_attribute_transportation = copy.deepcopy(
                    values.get(
                        "default_attribute_transportation",
                        rti._default_attribute_transportation,
                    )
                )
                rti._default_attribute_order = copy.deepcopy(
                    values.get("default_attribute_order", rti._default_attribute_order)
                )
                rti._evoked_callback_queue.clear()
            for federate_handle in federation.member_handles.values():
                target_rti = federation.member_rtis.get(federate_handle.value)
                if target_rti is not None and not target_rti._callbacks_enabled:
                    continue
                self._deliver_to_federate_handle(federate_handle, "federationRestored")
            federation.restore_label = None
            federation.restore_status.clear()

    def _require_connected(self, method_name: str) -> None:
        if not self._connected:
            raise NotConnected(f"Cannot call {method_name} before connect")

    def _require_joined(self, method_name: str) -> None:
        self._require_connected(method_name)
        if not self._joined:
            raise FederateNotExecutionMember(f"Cannot call {method_name} before joinFederationExecution")

    def _require_no_save_or_restore(self, method_name: str) -> None:
        federation = self._federation_record()
        if federation.save_label is not None:
            raise SaveInProgress(f"A federation save is already in progress during {method_name}")
        if federation.restore_label is not None:
            raise RestoreInProgress(f"A federation restore is already in progress during {method_name}")

    @staticmethod
    def _normalize_reserved_object_instance_name(object_instance_name: Any, *, method_name: str) -> str:
        if not isinstance(object_instance_name, str) or not object_instance_name:
            raise RTIinternalError(f"{method_name} requires non-empty object instance names")
        return object_instance_name

    def _normalize_reserved_object_instance_name_set(self, object_instance_names: Any, *, method_name: str) -> set[str]:
        if isinstance(object_instance_names, str):
            raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names")
        try:
            names = set(object_instance_names)
        except TypeError as exc:
            raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names") from exc
        if not names:
            raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names")
        return {
            self._normalize_reserved_object_instance_name(name, method_name=method_name)
            for name in names
        }

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
        self._pending_time_advance = None
        self._known_object_classes.clear()
        self._known_object_names.clear()
        self._locally_deleted_objects.clear()
        federation = _FEDERATION_REGISTRY.get(self._federation_name)
        if federation is not None:
            if self._federate_name is not None:
                federation.members.pop(self._federate_name, None)
                federation.member_handles.pop(self._federate_name, None)
            if self._federate_handle is not None:
                reserved_names = [
                    name
                    for name, owner in federation.reserved_object_instance_names.items()
                    if owner == self._federate_handle.value
                ]
                for name in reserved_names:
                    federation.reserved_object_instance_names.pop(name, None)
                federation.member_ambassadors.pop(self._federate_handle.value, None)
                federation.member_rtis.pop(self._federate_handle.value, None)
                federation.published_object_attributes.pop(self._federate_handle.value, None)
                federation.subscribed_object_attributes.pop(self._federate_handle.value, None)
                federation.subscribed_object_regions.pop(self._federate_handle.value, None)
                federation.published_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_interaction_regions.pop(self._federate_handle.value, None)
                federation.directed_interaction_region_gates.pop(self._federate_handle.value, None)
                federation.published_directed_interactions.pop(self._federate_handle.value, None)
                federation.subscribed_directed_interactions.pop(self._federate_handle.value, None)
                federation.member_regions.pop(self._federate_handle.value, None)
                federation.member_region_bounds.pop(self._federate_handle.value, None)

    def _apply_resign_action(self, resign_action: ResignAction) -> None:
        if resign_action is ResignAction.NO_ACTION:
            return
        if resign_action in {
            ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
            ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._cancel_resigning_federate_pending_acquisitions()
        if resign_action in {
            ResignAction.DELETE_OBJECTS,
            ResignAction.DELETE_OBJECTS_THEN_DIVEST,
            ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._delete_objects_owned_by_resigning_federate()
        if resign_action in {
            ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
            ResignAction.DELETE_OBJECTS_THEN_DIVEST,
            ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._divest_resigning_federate_attributes()

    def _cancel_resigning_federate_pending_acquisitions(self) -> None:
        federate_handle = self._current_federate_handle()
        for record in self._federation_record().object_instances.values():
            for attribute_name in tuple(record.attribute_candidates):
                self._remove_attribute_candidate(record, attribute_name, federate_handle)

    def _resigning_federate_has_pending_acquisitions(self) -> bool:
        federate_handle = self._current_federate_handle()
        for record in self._federation_record().object_instances.values():
            for attribute_name in tuple(record.attribute_candidates):
                if self._has_attribute_candidate(record, attribute_name, federate_handle):
                    return True
        return False

    def _resigning_federate_owns_attributes(self) -> bool:
        federate_handle = self._current_federate_handle()
        for record in self._federation_record().object_instances.values():
            if federate_handle in set(record.attribute_owners.values()):
                return True
        return False

    def _delete_objects_owned_by_resigning_federate(self) -> None:
        federation = self._federation_record()
        federate_handle = self._current_federate_handle()
        for object_instance_value, record in tuple(federation.object_instances.items()):
            if federate_handle not in set(record.attribute_owners.values()):
                continue
            object_instance = ObjectInstanceHandle(object_instance_value)
            self._deliver_resign_remove_callbacks(object_instance, record)
            if record.object_instance_name is not None:
                federation.object_instance_names.pop(record.object_instance_name, None)
            federation.object_instances.pop(object_instance_value, None)

    def _divest_resigning_federate_attributes(self) -> None:
        federate_handle = self._current_federate_handle()
        for object_instance_value, record in tuple(self._federation_record().object_instances.items()):
            attribute_handles_by_name = self._attribute_handles(record.object_class_name)
            for attribute_name, owner in tuple(record.attribute_owners.items()):
                if owner != federate_handle:
                    continue
                new_owner, acquisition_tag = self._pop_attribute_candidate(record, attribute_name) or (None, b"")
                record.attribute_owners[attribute_name] = new_owner
                record.attribute_divesting.discard(attribute_name)
                if new_owner is not None:
                    attribute_handle = AttributeHandle(attribute_handles_by_name[attribute_name])
                    self._deliver_to_federate_handle(
                        new_owner,
                        "attributeOwnershipAcquisitionNotification",
                        ObjectInstanceHandle(object_instance_value),
                        {attribute_handle},
                        acquisition_tag,
                    )

    def _matching_object_publishers(
        self,
        federation: _FederationRecord,
        object_class_name: str,
        attribute_names: set[str],
    ) -> set[int]:
        publishers: set[int] = set()
        for federate_key, classes in federation.published_object_attributes.items():
            published = classes.get(object_class_name, set())
            if published & attribute_names:
                publishers.add(federate_key)
        return publishers

    def _has_object_registration_interest(
        self,
        federation: _FederationRecord,
        publisher_key: int,
        object_class_name: str,
    ) -> bool:
        published = federation.published_object_attributes.get(publisher_key, {}).get(object_class_name, set())
        if not published:
            return False
        for subscriber_key, classes in federation.subscribed_object_attributes.items():
            if subscriber_key == publisher_key:
                continue
            subscribed = classes.get(object_class_name, set())
            if published & subscribed:
                return True
        return False

    def _matching_interaction_publishers(
        self,
        federation: _FederationRecord,
        interaction_class_name: str,
    ) -> set[int]:
        publishers: set[int] = set()
        for federate_key, published in federation.published_interactions.items():
            if interaction_class_name in published:
                publishers.add(federate_key)
        return publishers

    def _has_interaction_interest(
        self,
        federation: _FederationRecord,
        publisher_key: int,
        interaction_class_name: str,
    ) -> bool:
        if interaction_class_name not in federation.published_interactions.get(publisher_key, set()):
            return False
        for subscriber_key, subscribed in federation.subscribed_interactions.items():
            if subscriber_key == publisher_key:
                continue
            if interaction_class_name in subscribed:
                return True
        return False

    def _deliver_resign_remove_callbacks(self, object_instance: ObjectInstanceHandle, record: _ObjectInstanceRecord) -> None:
        for federate_key, subscriptions in self._federation_record().subscribed_object_attributes.items():
            if federate_key == self._current_federate_key() or record.object_class_name not in subscriptions:
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "removeObjectInstance",
                object_instance,
                b"",
                self._current_federate_handle(),
                None,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )

    def _evaluate_attribute_scope_advisories(self) -> None:
        federation = self._federation_record()
        in_scope_callbacks: dict[tuple[int, int], set[AttributeHandle]] = {}
        out_of_scope_callbacks: dict[tuple[int, int], set[AttributeHandle]] = {}
        active_keys = set()
        for subscriber_key, subscriptions in federation.subscribed_object_attributes.items():
            subscriber_rti = federation.member_rtis.get(subscriber_key)
            if subscriber_rti is None or not subscriber_rti._switches["attribute_scope_advisory"]:
                continue
            for object_instance_value, record in federation.object_instances.items():
                subscribed_names = set(subscriptions.get(record.object_class_name, set()))
                if not subscribed_names:
                    continue
                handles_by_name = self._attribute_handles(record.object_class_name)
                for attribute_name in subscribed_names:
                    source_owner = record.attribute_owners.get(attribute_name)
                    if source_owner is None:
                        continue
                    active_key = (subscriber_key, object_instance_value, attribute_name)
                    active_keys.add(active_key)
                    source_regions = set(record.update_regions.get(attribute_name, set()))
                    target_regions = (
                        federation.subscribed_object_regions
                        .get(subscriber_key, {})
                        .get(record.object_class_name, {})
                        .get(attribute_name, set())
                    )
                    in_scope = not target_regions or self._region_sets_overlap(
                        source_owner.value,
                        source_regions,
                        subscriber_key,
                        set(target_regions),
                    )
                    previous = federation.attribute_scope_state.get(active_key)
                    federation.attribute_scope_state[active_key] = in_scope
                    if previous is None and in_scope:
                        in_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                            AttributeHandle(handles_by_name[attribute_name])
                        )
                    elif previous is True and not in_scope:
                        out_of_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                            AttributeHandle(handles_by_name[attribute_name])
                        )
                    elif previous is False and in_scope:
                        in_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                            AttributeHandle(handles_by_name[attribute_name])
                        )
        for state_key in tuple(federation.attribute_scope_state):
            subscriber_key, object_instance_value, attribute_name = state_key
            if state_key in active_keys:
                continue
            if federation.attribute_scope_state.pop(state_key, False):
                record = federation.object_instances.get(object_instance_value)
                if record is not None:
                    out_of_scope_callbacks.setdefault((subscriber_key, object_instance_value), set()).add(
                        AttributeHandle(self._attribute_handles(record.object_class_name)[attribute_name])
                    )
        for (subscriber_key, object_instance_value), attributes in sorted(in_scope_callbacks.items()):
            self._deliver_to_federate_handle(
                FederateHandle(subscriber_key),
                "attributesInScope",
                ObjectInstanceHandle(object_instance_value),
                attributes,
            )
        for (subscriber_key, object_instance_value), attributes in sorted(out_of_scope_callbacks.items()):
            self._deliver_to_federate_handle(
                FederateHandle(subscriber_key),
                "attributesOutOfScope",
                ObjectInstanceHandle(object_instance_value),
                attributes,
            )

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

    def _synchronization_required_federates(self, synchronization_set: Any | None) -> set[int]:
        federation = self._federation_record()
        if synchronization_set is None:
            return set(federation.member_rtis)
        try:
            handles = tuple(synchronization_set)
        except TypeError as exc:
            raise InvalidFederateHandle("Synchronization set must be iterable") from exc
        required = {
            self._normalize_handle(handle, FederateHandle, InvalidFederateHandle)
            for handle in handles
        }
        unknown = required - set(federation.member_rtis)
        if unknown:
            raise InvalidFederateHandle(f"Unknown synchronization federate handles: {sorted(unknown)}")
        return required

    def _handle_mom_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        if ".HLAmanager." not in interaction_class_name:
            return False
        try:
            if ".HLAadjust." in interaction_class_name:
                return self._handle_mom_adjust_interaction(interaction_class_name, values_by_handle)
            if ".HLAservice." in interaction_class_name:
                return self._handle_mom_service_interaction(interaction_class_name, values_by_handle)
        except Exception as exc:
            self._send_mom_exception_interaction(interaction_class_name, exc, parameter_error=False)
            raise
        if ".HLArequest." not in interaction_class_name:
            return False
        if ".HLAfederate.HLArequest." in interaction_class_name:
            try:
                return self._handle_mom_federate_request_interaction(interaction_class_name, values_by_handle)
            except Exception as exc:
                self._send_mom_exception_interaction(interaction_class_name, exc, parameter_error=True)
                raise
        request_to_report = {
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints":
                "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus":
                "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData":
                "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata":
                "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata",
        }
        report_name = request_to_report.get(interaction_class_name)
        if report_name is None:
            return False
        try:
            self._send_mom_report_interaction(
                report_name,
                self._mom_request_report_values(interaction_class_name, report_name, values_by_handle),
            )
        except Exception as exc:
            self._send_mom_exception_interaction(interaction_class_name, exc, parameter_error=True)
            raise
        return True

    def _handle_mom_federate_request_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        params = self._mom_request_params_by_name(interaction_class_name, values_by_handle)
        target = self._mom_target_rti(params)
        target_federate = target._current_federate_handle()
        if interaction_class_name.endswith("HLArequestPublications"):
            target._send_mom_publication_reports(target_federate)
            return True
        if interaction_class_name.endswith("HLArequestSubscriptions"):
            target._send_mom_subscription_reports(target_federate)
            return True
        if interaction_class_name.endswith("HLArequestObjectInstanceInformation"):
            object_instance = ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
            target._send_mom_object_instance_information_report(target_federate, object_instance)
            return True
        if interaction_class_name.endswith("HLArequestFOMmoduleData"):
            report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData"
            values = target._mom_request_report_values(interaction_class_name, report_name, values_by_handle)
            values["HLAfederate"] = str(target_federate.value).encode("ascii")
            target._send_mom_report_interaction(report_name, values)
            return True
        if interaction_class_name.endswith("HLArequestObjectInstancesThatCanBeDeleted"):
            target._send_mom_object_class_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
                target_federate,
                target._mom_deletable_object_counts(target_federate),
                "HLAobjectInstanceCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestObjectInstancesUpdated"):
            target._send_mom_object_class_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
                target_federate,
                target._mom_counts_for_federate(target._federation_record().mom_object_instances_updated, target_federate),
                "HLAobjectInstanceCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestObjectInstancesReflected"):
            target._send_mom_object_class_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
                target_federate,
                target._mom_counts_for_federate(target._federation_record().mom_object_instances_reflected, target_federate),
                "HLAobjectInstanceCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestUpdatesSent"):
            target._send_mom_transport_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
                target_federate,
                target._mom_transport_counts_for_federate(target._federation_record().mom_updates_sent, target_federate),
                "HLAupdateCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestReflectionsReceived"):
            target._send_mom_transport_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
                target_federate,
                target._mom_transport_counts_for_federate(target._federation_record().mom_reflections_received, target_federate),
                "HLAreflectCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestInteractionsSent"):
            target._send_mom_transport_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
                target_federate,
                target._mom_transport_counts_for_federate(target._federation_record().mom_interactions_sent, target_federate),
                "HLAinteractionCounts",
            )
            return True
        if interaction_class_name.endswith("HLArequestInteractionsReceived"):
            target._send_mom_transport_count_report(
                "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
                target_federate,
                target._mom_transport_counts_for_federate(target._federation_record().mom_interactions_received, target_federate),
                "HLAinteractionCounts",
            )
            return True
        return False

    def _send_mom_publication_reports(self, target_federate: FederateHandle) -> None:
        federation = self._federation_record()
        object_publications = federation.published_object_attributes.get(target_federate.value, {})
        object_report = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
        if not object_publications:
            self._send_mom_report_interaction(
                object_report,
                {
                    "HLAfederate": str(target_federate.value).encode("ascii"),
                    "HLAnumberOfClasses": b"0",
                },
            )
        else:
            for object_class_name, attribute_names in sorted(object_publications.items()):
                self._send_mom_report_interaction(
                    object_report,
                    {
                        "HLAfederate": str(target_federate.value).encode("ascii"),
                        "HLAnumberOfClasses": str(len(object_publications)).encode("ascii"),
                        "HLAobjectClass": str(self._object_class_handles()[object_class_name]).encode("ascii"),
                        "HLAattributeList": self._mom_handle_list_payload(
                            self._attribute_handles(object_class_name)[attribute_name]
                            for attribute_name in sorted(attribute_names)
                        ),
                    },
                )
        self._send_mom_report_interaction(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication",
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAinteractionClassList": self._mom_handle_list_payload(
                    self._interaction_class_handles()[interaction_class_name]
                    for interaction_class_name in sorted(federation.published_interactions.get(target_federate.value, set()))
                ),
            },
        )

    def _send_mom_subscription_reports(self, target_federate: FederateHandle) -> None:
        federation = self._federation_record()
        object_subscriptions = federation.subscribed_object_attributes.get(target_federate.value, {})
        object_report = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
        if not object_subscriptions:
            self._send_mom_report_interaction(
                object_report,
                {
                    "HLAfederate": str(target_federate.value).encode("ascii"),
                    "HLAnumberOfClasses": b"0",
                },
            )
        else:
            for object_class_name, attribute_names in sorted(object_subscriptions.items()):
                self._send_mom_report_interaction(
                    object_report,
                    {
                        "HLAfederate": str(target_federate.value).encode("ascii"),
                        "HLAnumberOfClasses": str(len(object_subscriptions)).encode("ascii"),
                        "HLAobjectClass": str(self._object_class_handles()[object_class_name]).encode("ascii"),
                        "HLAactive": b"HLAtrue",
                        "HLAmaxUpdateRate": b"",
                        "HLAattributeList": self._mom_handle_list_payload(
                            self._attribute_handles(object_class_name)[attribute_name]
                            for attribute_name in sorted(attribute_names)
                        ),
                    },
                )
        self._send_mom_report_interaction(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription",
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAinteractionClassList": self._mom_handle_list_payload(
                    self._interaction_class_handles()[interaction_class_name]
                    for interaction_class_name in sorted(federation.subscribed_interactions.get(target_federate.value, set()))
                ),
            },
        )

    def _send_mom_object_instance_information_report(
        self,
        target_federate: FederateHandle,
        object_instance: ObjectInstanceHandle,
    ) -> None:
        record = self._object_instance_record_known(object_instance)
        owned_attribute_handles = [
            self._attribute_handles(record.object_class_name)[attribute_name]
            for attribute_name, owner in sorted(record.attribute_owners.items())
            if owner == target_federate
        ]
        object_class_handle = self._object_class_handles()[record.object_class_name]
        self._send_mom_report_interaction(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAobjectInstance": str(object_instance.value).encode("ascii"),
                "HLAownedInstanceAttributeList": self._mom_handle_list_payload(owned_attribute_handles),
                "HLAregisteredClass": str(object_class_handle).encode("ascii"),
                "HLAknownClass": str(object_class_handle).encode("ascii"),
            },
        )

    def _send_mom_object_class_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_class: Mapping[str, int],
        count_parameter_name: str,
    ) -> None:
        self._send_mom_report_interaction(
            report_name,
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                count_parameter_name: self._mom_object_class_counts_payload(counts_by_class),
            },
        )

    def _send_mom_transport_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_transport: Mapping[str, Mapping[str, int]],
        count_parameter_name: str,
    ) -> None:
        if not counts_by_transport:
            counts_by_transport = {"HLAreliable": {}}
        for transportation_name, counts_by_name in sorted(counts_by_transport.items()):
            self._send_mom_report_interaction(
                report_name,
                {
                    "HLAfederate": str(target_federate.value).encode("ascii"),
                    "HLAtransportation": transportation_name.encode("ascii"),
                    count_parameter_name: self._mom_object_class_counts_payload(counts_by_name),
                },
            )

    def _mom_deletable_object_counts(self, target_federate: FederateHandle) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._federation_record().object_instances.values():
            if target_federate not in set(record.attribute_owners.values()):
                continue
            counts[record.object_class_name] = counts.get(record.object_class_name, 0) + 1
        return counts

    @staticmethod
    def _mom_counts_for_federate(counts: Mapping[tuple[int, str], int], target_federate: FederateHandle) -> dict[str, int]:
        result: dict[str, int] = {}
        for (federate_key, class_name), count in counts.items():
            if federate_key == target_federate.value:
                result[class_name] = count
        return result

    @staticmethod
    def _mom_transport_counts_for_federate(
        counts: Mapping[tuple[int, str, str], int],
        target_federate: FederateHandle,
    ) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        for (federate_key, class_name, transportation_name), count in counts.items():
            if federate_key == target_federate.value:
                result.setdefault(transportation_name, {})[class_name] = count
        return result

    def _handle_mom_service_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        params = self._mom_request_params_by_name(interaction_class_name, values_by_handle)
        target = self._mom_target_rti(params)
        leaf = interaction_class_name.rsplit(".", 1)[-1]
        if leaf == "HLAresignFederationExecution":
            target.resignFederationExecution(self._mom_resign_action(params.get("HLAresignAction")))
            return True
        if leaf == "HLAsynchronizationPointAchieved":
            target.synchronizationPointAchieved(
                self._mom_text(params.get("HLAlabel"), "HLAlabel"),
                self._mom_bool(params.get("HLAsuccessIndicator"), True),
            )
            return True
        if leaf == "HLAfederateSaveBegun":
            target.federateSaveBegun()
            return True
        if leaf == "HLAfederateSaveComplete":
            if self._mom_bool(params.get("HLAsuccessIndicator"), True):
                target.federateSaveComplete()
            else:
                target.federateSaveNotComplete()
            return True
        if leaf == "HLAfederateRestoreComplete":
            if self._mom_bool(params.get("HLAsuccessIndicator"), True):
                target.federateRestoreComplete()
            else:
                target.federateRestoreNotComplete()
            return True
        if leaf == "HLAenableTimeRegulation":
            target.enableTimeRegulation(target._mom_interval(params.get("HLAlookahead"), "HLAlookahead"))
            return True
        if leaf == "HLAdisableTimeRegulation":
            target.disableTimeRegulation()
            return True
        if leaf == "HLAenableTimeConstrained":
            target.enableTimeConstrained()
            return True
        if leaf == "HLAdisableTimeConstrained":
            target.disableTimeConstrained()
            return True
        if leaf == "HLAenableAsynchronousDelivery":
            target.enableAsynchronousDelivery()
            return True
        if leaf == "HLAdisableAsynchronousDelivery":
            target.disableAsynchronousDelivery()
            return True
        if leaf == "HLAtimeAdvanceRequest":
            target.timeAdvanceRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
            return True
        if leaf == "HLAtimeAdvanceRequestAvailable":
            target.timeAdvanceRequestAvailable(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
            return True
        if leaf == "HLAnextMessageRequest":
            target.nextMessageRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
            return True
        if leaf == "HLAnextMessageRequestAvailable":
            target.nextMessageRequestAvailable(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
            return True
        if leaf == "HLAflushQueueRequest":
            target.flushQueueRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
            return True
        if leaf == "HLAmodifyLookahead":
            target.modifyLookahead(target._mom_interval(params.get("HLAlookahead"), "HLAlookahead"))
            return True
        if leaf == "HLAdeleteObjectInstance":
            time = target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp") if params.get("HLAtimeStamp") else None
            target.deleteObjectInstance(
                ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
                bytes(params.get("HLAtag", b"MOM")),
                time,
            )
            return True
        if leaf == "HLAlocalDeleteObjectInstance":
            target.localDeleteObjectInstance(
                ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
            )
            return True
        if leaf == "HLArequestAttributeTransportationTypeChange":
            target.requestAttributeTransportationTypeChange(
                ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
                target._mom_transportation_handle(params.get("HLAtransportation"), "HLAtransportation"),
            )
            return True
        if leaf == "HLArequestInteractionTransportationTypeChange":
            target.requestInteractionTransportationTypeChange(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass")),
                target._mom_transportation_handle(params.get("HLAtransportation"), "HLAtransportation"),
            )
            return True
        if leaf == "HLAchangeAttributeOrderType":
            target.changeAttributeOrderType(
                ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
                self._mom_order_type(params.get("HLAsendOrder"), "HLAsendOrder"),
            )
            return True
        if leaf == "HLAchangeInteractionOrderType":
            target.changeInteractionOrderType(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass")),
                self._mom_order_type(params.get("HLAsendOrder"), "HLAsendOrder"),
            )
            return True
        if leaf == "HLAunconditionalAttributeOwnershipDivestiture":
            target.unconditionalAttributeOwnershipDivestiture(
                ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
                b"MOM",
            )
            return True
        if leaf == "HLApublishObjectClassAttributes":
            target.publishObjectClassAttributes(
                ObjectClassHandle(self._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
            )
            return True
        if leaf == "HLAunpublishObjectClassAttributes":
            target.unpublishObjectClassAttributes(
                ObjectClassHandle(self._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
            )
            return True
        if leaf == "HLApublishInteractionClass":
            target.publishInteractionClass(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
            )
            return True
        if leaf == "HLAunpublishInteractionClass":
            target.unpublishInteractionClass(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
            )
            return True
        if leaf == "HLAsubscribeObjectClassAttributes":
            service = (
                target.subscribeObjectClassAttributes
                if self._mom_bool(params.get("HLAactive"), True)
                else target.subscribeObjectClassAttributesPassively
            )
            service(
                ObjectClassHandle(self._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
            )
            return True
        if leaf == "HLAunsubscribeObjectClassAttributes":
            target.unsubscribeObjectClassAttributes(
                ObjectClassHandle(self._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
                self._mom_attribute_handles(params.get("HLAattributeList")),
            )
            return True
        if leaf == "HLAsubscribeInteractionClass":
            service = (
                target.subscribeInteractionClass
                if self._mom_bool(params.get("HLAactive"), True)
                else target.subscribeInteractionClassPassively
            )
            service(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
            )
            return True
        if leaf == "HLAunsubscribeInteractionClass":
            target.unsubscribeInteractionClass(
                InteractionClassHandle(self._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
            )
            return True
        return False

    def _handle_mom_adjust_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        params = self._mom_request_params_by_name(interaction_class_name, values_by_handle)
        target = self._mom_target_rti(params)
        if interaction_class_name.endswith("HLAsetServiceReporting"):
            target._switches["service_reporting"] = self._mom_bool(params.get("HLAreportingState"), False)
            return True
        if interaction_class_name.endswith("HLAsetExceptionReporting"):
            target._switches["exception_reporting"] = self._mom_bool(params.get("HLAreportingState"), False)
            return True
        if interaction_class_name.endswith("HLAsetTiming"):
            target._mom_report_period_seconds = float(self._mom_number(params.get("HLAreportPeriod"), "HLAreportPeriod"))
            return True
        if interaction_class_name.endswith("HLAmodifyAttributeState"):
            object_instance = ObjectInstanceHandle(self._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
            attribute = AttributeHandle(self._mom_int(params.get("HLAattribute"), "HLAattribute"))
            ownership_state = self._mom_ownership_state(params.get("HLAattributeState"), "HLAattributeState")
            target._modify_mom_attribute_state(object_instance, attribute, ownership_state)
            return True
        if interaction_class_name.endswith("HLAsetSwitches") and ".HLAfederate." in interaction_class_name:
            if "HLAconveyRegionDesignatorSets" in params:
                target._switches["convey_region_designator_sets"] = self._mom_bool(
                    params.get("HLAconveyRegionDesignatorSets"),
                    target._switches["convey_region_designator_sets"],
                )
            return True
        if interaction_class_name.endswith("HLAsetSwitches") and ".HLAfederation." in interaction_class_name:
            if "HLAautoProvide" in params:
                auto_provide = self._mom_bool(params.get("HLAautoProvide"), target._switches["auto_provide"])
                for member_rti in self._federation_record().member_rtis.values():
                    member_rti._switches["auto_provide"] = auto_provide
            return True
        return False

    def _modify_mom_attribute_state(
        self,
        object_instance: ObjectInstanceHandle,
        attribute: AttributeHandle,
        ownership_state: str,
    ) -> None:
        record = self._object_instance_record(object_instance)
        attribute_name = self._attribute_names_from_handles(record.object_class_name, {attribute})[0]
        if ownership_state == "owned":
            if attribute_name not in self._published_attributes_for_current_federate(record.object_class_name):
                raise ObjectClassNotPublished(record.object_class_name)
            record.attribute_owners[attribute_name] = self._current_federate_handle()
            record.attribute_divesting.discard(attribute_name)
            record.attribute_candidates.pop(attribute_name, None)
            return
        if record.attribute_owners.get(attribute_name) != self._current_federate_handle():
            raise AttributeNotOwned(attribute_name)
        record.attribute_owners[attribute_name] = None
        record.attribute_divesting.discard(attribute_name)
        record.attribute_candidates.pop(attribute_name, None)

    def _mom_request_params_by_name(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        names_by_handle = {value: name for name, value in self._parameter_handles(interaction_class_name).items()}
        result: dict[str, bytes] = {}
        for handle, value in values_by_handle.items():
            handle_value = self._normalize_handle(handle, ParameterHandle, InteractionParameterNotDefined)
            parameter_name = names_by_handle.get(handle_value)
            if parameter_name is not None:
                result[parameter_name] = bytes(value)
        return result

    def _mom_target_rti(self, params: Mapping[str, bytes]) -> "Shim2025RTIAmbassador":
        federation = self._federation_record()
        federate_payload = params.get("HLAfederate")
        if federate_payload:
            try:
                federate_key = int(federate_payload.decode("ascii"))
            except ValueError as exc:
                raise InvalidFederateHandle(federate_payload.decode("ascii", errors="replace")) from exc
        else:
            federate_key = self._current_federate_key()
        target = federation.member_rtis.get(federate_key)
        if target is None:
            raise InvalidFederateHandle(str(federate_key))
        return target

    @staticmethod
    def _mom_bool(value: bytes | None, default: bool) -> bool:
        if value is None:
            return default
        text = value.decode("ascii", errors="ignore").strip().lower()
        if text in {"1", "true", "yes", "hlatrue", "on"}:
            return True
        if text in {"0", "false", "no", "hlafalse", "off"}:
            return False
        return default

    @staticmethod
    def _mom_int(value: bytes | None, field_name: str) -> int:
        if value is None:
            raise RTIinternalError(f"Missing MOM parameter {field_name}")
        try:
            return int(value.decode("ascii").strip())
        except ValueError as exc:
            raise RTIinternalError(f"Invalid MOM handle value for {field_name}") from exc

    @staticmethod
    def _mom_attribute_handles(value: bytes | None) -> set[AttributeHandle]:
        if value is None:
            raise RTIinternalError("Missing MOM parameter HLAattributeList")
        text = value.decode("ascii", errors="ignore").strip()
        if not text:
            return set()
        normalized = text.translate(str.maketrans({char: "," for char in "[](); \t\n\r"}))
        return {AttributeHandle(int(part)) for part in normalized.split(",") if part}

    @staticmethod
    def _mom_text(value: bytes | None, field_name: str) -> str:
        if value is None:
            raise RTIinternalError(f"Missing MOM parameter {field_name}")
        return value.decode("utf-8")

    def _mom_transportation_handle(self, value: bytes | None, field_name: str) -> TransportationTypeHandle:
        return self.getTransportationTypeHandle(self._mom_text(value, field_name))

    def _mom_time(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_time(self._mom_number(value, field_name))

    def _mom_interval(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_interval(self._mom_number(value, field_name))

    @staticmethod
    def _mom_number(value: bytes | None, field_name: str) -> int | float:
        if value is None:
            raise RTIinternalError(f"Missing MOM parameter {field_name}")
        text = value.decode("ascii", errors="ignore").strip()
        try:
            return float(text) if any(char in text for char in ".eE") else int(text)
        except ValueError as exc:
            raise RTIinternalError(f"Invalid MOM numeric value for {field_name}") from exc

    @staticmethod
    def _mom_handle_list_payload(values: Iterable[int]) -> bytes:
        return ",".join(str(value) for value in values).encode("ascii")

    @staticmethod
    def _increment_mom_count(counts: dict[Any, int], key: Any) -> None:
        counts[key] = counts.get(key, 0) + 1

    def _mom_object_class_counts_payload(self, counts_by_class: Mapping[str, int]) -> bytes:
        handle_pairs: list[tuple[int, int]] = []
        object_class_handles = self._object_class_handles()
        interaction_class_handles = self._interaction_class_handles()
        for class_name, count in counts_by_class.items():
            handle = object_class_handles.get(class_name, interaction_class_handles.get(class_name))
            if handle is not None:
                handle_pairs.append((handle, count))
        return ",".join(f"{handle}:{count}" for handle, count in sorted(handle_pairs)).encode("ascii")

    @staticmethod
    def _mom_ownership_state(value: bytes | None, field_name: str) -> str:
        if value is None:
            raise RTIinternalError(f"Missing MOM parameter {field_name}")
        text = value.decode("ascii", errors="ignore").strip()
        normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").lower()
        if normalized in {"1", "owned", "owner", "ownedbyfederate", "attributeowned"}:
            return "owned"
        if normalized in {"0", "unowned", "notowned", "attributeisnotowned", "none"}:
            return "unowned"
        raise RTIinternalError(f"Invalid MOM ownership state for {field_name}")

    @staticmethod
    def _mom_order_type(value: bytes | None, field_name: str) -> OrderType:
        if value is None:
            raise RTIinternalError(f"Missing MOM parameter {field_name}")
        text = value.decode("ascii", errors="ignore").strip()
        try:
            mom_value = int(text)
        except ValueError:
            normalized = text.removeprefix("HLA").upper()
            try:
                return OrderType[normalized]
            except KeyError as exc:
                raise RTIinternalError(f"Invalid MOM order type for {field_name}") from exc
        if mom_value == 0:
            return OrderType.RECEIVE
        if mom_value == 1:
            return OrderType.TIMESTAMP
        try:
            return OrderType(mom_value)
        except ValueError as exc:
            raise RTIinternalError(f"Invalid MOM order type for {field_name}") from exc

    @classmethod
    def _mom_resign_action(cls, value: bytes | None) -> ResignAction:
        if value is None:
            return ResignAction.NO_ACTION
        text = value.decode("ascii", errors="ignore").strip()
        try:
            return ResignAction(int(text))
        except ValueError:
            normalized = text.removeprefix("HLA").upper()
            try:
                return ResignAction[normalized]
            except KeyError as exc:
                raise RTIinternalError(f"Invalid MOM resign action {text!r}") from exc

    def _mom_request_report_values(
        self,
        request_name: str,
        report_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        federation = self._federation_record()
        params = self._mom_request_params_by_name(request_name, values_by_handle)
        if report_name.endswith("HLAreportFOMmoduleData"):
            indicator = self._mom_index(params.get("HLAFOMmoduleIndicator"))
            module_data = self._mom_module_data(federation.fom_modules, indicator)
            return {
                "HLAFOMmoduleIndicator": str(indicator).encode("ascii"),
                "HLAFOMmoduleData": module_data.encode("utf-8"),
            }
        if report_name.endswith("HLAreportMIMdata"):
            return {
                "HLAMIMdata": self._mom_single_module_data(federation.mim_module).encode("utf-8"),
            }
        if report_name.endswith("HLAreportSynchronizationPoints"):
            labels = ",".join(sorted(federation.synchronization_points)).encode("ascii")
            return {
                "HLAsyncPoints": labels,
                "HLAsynchronizationPoints": labels,
            }
        if report_name.endswith("HLAreportSynchronizationPointStatus"):
            requested_label = (params.get("HLAlabel") or params.get("HLAsyncPointName") or b"").decode("ascii")
            labels = [requested_label] if requested_label else sorted(federation.synchronization_points)
            federates: set[int] = set()
            statuses = []
            for label in labels:
                point = federation.synchronization_points.get(label)
                if point is None:
                    statuses.append(f"{label}:")
                    continue
                reported = sorted(point.achieved_federates | point.failed_federates)
                federates.update(reported)
                status_bits = ",".join(f"{handle}:failed" if handle in point.failed_federates else f"{handle}:achieved" for handle in reported)
                statuses.append(f"{label}:{status_bits}")
            label_payload = ",".join(labels).encode("ascii")
            federates_payload = ",".join(str(handle) for handle in sorted(federates)).encode("ascii")
            statuses_payload = ";".join(statuses).encode("ascii")
            return {
                "HLAsyncPointName": label_payload,
                "HLAsyncPointFederates": statuses_payload,
                "HLAlabel": label_payload,
                "HLAfederateList": federates_payload,
                "HLAfederateSynchronizationStatusList": statuses_payload,
            }
        return {}

    @staticmethod
    def _mom_index(value: bytes | None) -> int:
        if not value:
            return 0
        try:
            return int(value.decode("ascii") or "0")
        except ValueError:
            return 0

    def _mom_module_data(self, modules: tuple[Any, ...], indicator: int) -> str:
        if not 0 <= indicator < len(modules):
            return ""
        return self._mom_single_module_data(modules[indicator])

    @staticmethod
    def _mom_single_module_data(module: Any | None) -> str:
        if module is None:
            return ""
        path = getattr(module, "path", None)
        if path is not None and Path(path).exists():
            return Path(path).read_text(encoding="utf-8")
        if getattr(module, "parsed", False):
            fom = import_module("hla.rti1516e.fom")
            return fom.serialize_fom_module(module, edition="2025")
        return str(getattr(module, "uri", None) or getattr(module, "source", ""))

    def _send_mom_report_interaction(self, report_name: str, values: Mapping[str, bytes]) -> None:
        report_class = InteractionClassHandle(self._interaction_class_handles()[report_name])
        report_parameters = self._parameter_handles(report_name)
        parameter_values: dict[ParameterHandle, bytes] = {
            ParameterHandle(report_parameters[name]): bytes(value)
            for name, value in values.items()
            if name in report_parameters
        }
        transportation = self._transportation_handle_by_name("HLAreliable")
        federation = self._federation_record()
        for federate_key, subscriptions in federation.subscribed_interactions.items():
            if report_name not in subscriptions:
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "receiveInteraction",
                report_class,
                parameter_values,
                b"MOM",
                transportation,
                self._current_federate_handle(),
                set(),
                None,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )

    def _send_mom_exception_interaction(
        self,
        interaction_class_name: str,
        exception: Exception,
        *,
        parameter_error: bool,
    ) -> None:
        report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
        try:
            report_class = InteractionClassHandle(self._interaction_class_handles()[report_name])
            report_parameters = self._parameter_handles(report_name)
        except Exception:
            return
        values = {
            "HLAservice": interaction_class_name.encode("utf-8"),
            "HLAexception": f"{type(exception).__name__}: {exception}".encode("utf-8"),
            "HLAparameterError": b"HLAtrue" if parameter_error else b"HLAfalse",
        }
        parameter_values = {
            ParameterHandle(report_parameters[name]): value
            for name, value in values.items()
            if name in report_parameters
        }
        transportation = self._transportation_handle_by_name("HLAreliable")
        federation = self._federation_record()
        for federate_key in sorted(federation.member_ambassadors):
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "receiveInteraction",
                report_class,
                parameter_values,
                b"MOM",
                transportation,
                self._current_federate_handle(),
                set(),
                None,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )

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

    def _region_owner_key(self, preferred_key: int, region_value: int) -> int | None:
        federation = self._federation_record()
        if region_value in federation.member_regions.get(preferred_key, {}):
            return preferred_key
        for member_key, regions in federation.member_regions.items():
            if region_value in regions:
                return member_key
        return None

    def _regions_overlap_pair(self, source_key: int, source_region: int, target_key: int, target_region: int) -> bool:
        federation = self._federation_record()
        resolved_source_key = self._region_owner_key(source_key, source_region)
        resolved_target_key = self._region_owner_key(target_key, target_region)
        if resolved_source_key is None or resolved_target_key is None:
            return False
        source_dims = federation.member_regions.get(resolved_source_key, {}).get(source_region, set())
        target_dims = federation.member_regions.get(resolved_target_key, {}).get(target_region, set())
        common_dimensions = set(source_dims) & set(target_dims)
        if not common_dimensions:
            return False
        source_bounds = federation.member_region_bounds.get(resolved_source_key, {}).get(source_region, {})
        target_bounds = federation.member_region_bounds.get(resolved_target_key, {}).get(target_region, {})
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

    def _object_instance_region_values(self, record: _ObjectInstanceRecord) -> set[int]:
        source_regions: set[int] = set()
        for region_values in record.update_regions.values():
            source_regions.update(region_values)
        return source_regions

    def _reflectable_attribute_names_for_subscriber(
        self,
        source_key: int,
        subscriber_key: int,
        record: _ObjectInstanceRecord,
        discovery_class_name: str,
        subscribed_names: set[str],
    ) -> set[str]:
        region_subscription = (
            self._federation_record()
            .subscribed_object_regions.get(subscriber_key, {})
            .get(discovery_class_name, {})
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

    def _known_object_classes_for_federate(
        self,
        federate_key: int,
        object_instance: ObjectInstanceHandle,
        object_class_name: str,
    ) -> str | None:
        federation = self._federation_record()
        target_rti = federation.member_rtis.get(federate_key)
        if target_rti is None:
            return None
        known_class_name = target_rti._known_object_classes.get(object_instance.value)
        if known_class_name is not None:
            return known_class_name
        return self._subscribed_discovery_class_name(federate_key, object_class_name)

    def _subscribed_discovery_class_name(self, federate_key: int, object_class_name: str) -> str | None:
        subscriptions = self._federation_record().subscribed_object_attributes.get(federate_key, {})
        for candidate_name in self._object_class_lineage(object_class_name):
            if candidate_name in subscriptions:
                return candidate_name
        return None

    def _object_class_lineage(self, object_class_name: str) -> tuple[str, ...]:
        catalog = self._federation_record().fom_catalog
        lineage: list[str] = []
        current = catalog.object_classes.get(object_class_name)
        while current is not None:
            lineage.append(current.full_name)
            parent_name = current.parent_name
            if parent_name is None:
                break
            current = catalog.object_classes.get(parent_name)
        return tuple(lineage)

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

    def _attribute_order_for(self, record: _ObjectInstanceRecord, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        orders = {
            record.attribute_order.get(
                self._attribute_name_by_handle(record.object_class_name, attribute),
                self._default_attribute_order.get(
                    (record.object_class_name, self._attribute_name_by_handle(record.object_class_name, attribute)),
                    OrderType.RECEIVE,
                ),
            )
            for attribute in values_by_handle
        }
        return sorted(orders, key=lambda value: value.name)[0]

    def _interaction_order_for(self, interaction_class_name: str) -> OrderType:
        return self._federation_record().interaction_order.get(
            (self._current_federate_key(), interaction_class_name),
            OrderType.RECEIVE,
        )

    def _interaction_transportation_for(self, interaction_class_name: str) -> TransportationTypeHandle:
        transportation_name = self._federation_record().interaction_transportation.get(
            (self._current_federate_key(), interaction_class_name),
            "HLAreliable",
        )
        return self._transportation_handle_by_name(transportation_name)

    @staticmethod
    def _coerce_order_type(order_type: Any) -> OrderType:
        if isinstance(order_type, OrderType):
            return order_type
        try:
            return OrderType(order_type)
        except Exception as exc:
            raise InvalidOrderType(repr(order_type)) from exc

    def _discover_existing_objects_for_current_subscription(self, object_class_name: str) -> None:
        federation = self._federation_record()
        for object_value, record in federation.object_instances.items():
            discovery_class_name = self._subscribed_discovery_class_name(
                self._current_federate_key(),
                record.object_class_name,
            )
            if discovery_class_name != object_class_name:
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
                discovery_class_name,
                set(subscribed_names),
            )
            if not reflected_names:
                continue
            self._deliver_callback(
                "discoverObjectInstance",
                ObjectInstanceHandle(object_value),
                ObjectClassHandle(self._object_class_handles()[discovery_class_name]),
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
