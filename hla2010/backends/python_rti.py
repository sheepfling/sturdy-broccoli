"""In-memory Python RTI backend for early HLA 1516.1-2010 development.

This backend is intentionally small, deterministic, and dependency-free.  It is
not a complete conforming RTI; it implements the federation, declaration,
object/interaction, callback, and simple time services needed for local tests and
for small stand-up simulations.  The public application surface is the same
``DelegatingRTIAmbassador`` used by the Java JPype/Py4J backends.
"""
from __future__ import annotations

from collections import deque
import copy
import heapq
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable, Deque, Iterable, Mapping, MutableMapping, Sequence

from ..api import FederateAmbassador
from ..enums import (
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    RestoreStatus,
    SaveFailureReason,
    SaveStatus,
    ServiceGroup,
    SynchronizationPointFailureReason,
    TransportationType,
)
from ..fom import FOMCatalog, FOMMergeError, FOMModule, FOMResolutionError, FOMResolver, merge_fom_modules, standard_mim_module
from .. import handles as hla_handles
from .. import mom as hla_mom
from .. import mom_catalog as mom_table
from .. import time_management as tm
from ..service_reporting import ServiceReportRecord, ServiceReportSink
from ..spec_refs import method_reference
from ..exceptions import (
    AlreadyConnected,
    AttributeAcquisitionWasNotRequested,
    AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested,
    AttributeDivestitureWasNotRequested,
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFDD,
    CouldNotOpenMIM,
    AttributeNotDefined,
    AttributeNotOwned,
    DesignatorIsHLAstandardMIM,
    FederateAlreadyExecutionMember,
    FederateHandleNotKnown,
    FederateInternalError,
    FederateServiceInvocationsAreBeingReportedViaMOM,
    FederateIsExecutionMember,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InteractionClassNotDefined,
    InteractionClassNotPublished,
    InteractionParameterNotDefined,
    InconsistentFDD,
    InTimeAdvancingState,
    InvalidLogicalTime,
    InvalidLookahead,
    LogicalTimeAlreadyPassed,
    MessageCanNoLongerBeRetracted,
    InvalidDimensionHandle,
    InvalidInteractionClassHandle,
    InvalidObjectClassHandle,
    InvalidParameterHandle,
    InvalidRegion,
    NameNotFound,
    NotConnected,
    ObjectClassNotDefined,
    RestoreInProgress,
    SaveInProgress,
    ObjectInstanceNameInUse,
    ObjectInstanceNotKnown,
    NoAcquisitionPending,
    RTIexception,
    RTIinternalError,
    TimeConstrainedAlreadyEnabled,
    TimeRegulationAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from ..handles import (
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
from ..types import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformation,
    RangeBounds,
    MessageRetractionReturn,
    TimeQueryReturn,
)
from ..time import (
    DEFAULT_TIME_FACTORY_REGISTRY,
    HLAfloat64Time,
    HLAinteger64Time,
    HLAinteger64TimeFactory,
    HLAfloat64TimeFactory,
    LogicalTimeFactory,
    TimeFactoryRegistry,
)
from .base import BackendInfo, Invocation, RTIBackend, UnsupportedBackendService, make_rti_ambassador
from .java_common import resolve_java_arguments


@dataclass(frozen=True)
class SupplementalReflectInfo:
    """Small placeholder for the HLA SupplementalReflectInfo callback argument."""

    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SupplementalReceiveInfo:
    """Small placeholder for the HLA SupplementalReceiveInfo callback argument."""

    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SupplementalRemoveInfo:
    """Small placeholder for the HLA SupplementalRemoveInfo callback argument."""

    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass
class PythonRTIConfig:
    """Configuration for a Python in-memory RTI ambassador."""

    name: str = "python-inmemory-rti"
    version: str = "0.12"
    strict_object_publication: bool = False
    strict_interaction_publication: bool = False
    immediate_callbacks_inline: bool = True
    default_logical_time_implementation_name: str = HLAfloat64TimeFactory.NAME
    infer_time_factory_from_fom: bool = True
    fom_search_paths: tuple[str, ...] = ()
    require_fom_parse: bool = False
    strict_fom_lookup: bool = False
    strict_fom_loading: bool = False
    require_fom_modules: bool = False
    enable_mom: bool = True
    enforce_time_advancing_state: bool = True
    enforce_galt: bool = True
    default_preferred_order_type: OrderType = OrderType.RECEIVE
    non_regulated_grant_enabled: bool = True
    service_report_file: str | None = None
    service_report_file_truncate: bool = False
    service_report_directory: str | None = None
    service_report_file_on_by_default: bool = False
    strict_mom_parameter_decoding: bool = False


@dataclass
class ObjectClassDef:
    name: str
    handle: ObjectClassHandle
    attributes_by_name: dict[str, AttributeHandle] = field(default_factory=dict)
    attribute_names: dict[AttributeHandle, str] = field(default_factory=dict)


@dataclass
class InteractionClassDef:
    name: str
    handle: InteractionClassHandle
    parameters_by_name: dict[str, ParameterHandle] = field(default_factory=dict)
    parameter_names: dict[ParameterHandle, str] = field(default_factory=dict)


@dataclass
class ObjectInstance:
    handle: ObjectInstanceHandle
    class_handle: ObjectClassHandle
    name: str
    owner: FederateHandle | None
    attributes: dict[AttributeHandle, bytes] = field(default_factory=dict)
    attribute_owners: dict[AttributeHandle, FederateHandle | None] = field(default_factory=dict)
    attribute_divesting: set[AttributeHandle] = field(default_factory=set)
    attribute_candidates: dict[AttributeHandle, set[FederateHandle]] = field(default_factory=dict)
    update_regions: dict[AttributeHandle, set[RegionHandle]] = field(default_factory=dict)


@dataclass
class SynchronizationPointState:
    """Runtime state for one federation synchronization point.

    Section anchor: IEEE 1516.1-2010 services 4.11-4.15. The RTI remembers
    which federates were announced, records every achieved/failed report, emits
    the failure set in Federation Synchronized, and removes the point once the
    synchronization set completes.
    """

    label: str
    tag: bytes
    registering_federate: FederateHandle
    targets: set[FederateHandle] = field(default_factory=set)
    announced: set[FederateHandle] = field(default_factory=set)
    achieved: set[FederateHandle] = field(default_factory=set)
    failed: set[FederateHandle] = field(default_factory=set)
    open_to_late_joiners: bool = True

    def reported(self) -> set[FederateHandle]:
        return set(self.achieved) | set(self.failed)

    def is_complete(self) -> bool:
        return bool(self.targets) and self.targets.issubset(self.reported())


@dataclass
class FederationState:
    name: str
    fom_modules: tuple[FOMModule, ...] = ()
    mim_module: FOMModule | None = None
    fom_catalog: FOMCatalog = field(default_factory=FOMCatalog)
    mom_model: mom_table.MOMExposureModel | None = None
    time_factory: LogicalTimeFactory[Any, Any] = field(default_factory=lambda: DEFAULT_TIME_FACTORY_REGISTRY.get(HLAfloat64TimeFactory.NAME))
    federates: dict[FederateHandle, "FederateState"] = field(default_factory=dict)
    objects: dict[ObjectInstanceHandle, ObjectInstance] = field(default_factory=dict)
    object_names: dict[str, ObjectInstanceHandle] = field(default_factory=dict)
    reserved_object_names: dict[str, FederateHandle] = field(default_factory=dict)
    synchronization_points: dict[str, SynchronizationPointState] = field(default_factory=dict)

    # Federation save/restore state (§4.16-§4.26).
    save_label: str | None = None
    save_status: dict[FederateHandle, SaveStatus] = field(default_factory=dict)
    restore_label: str | None = None
    restore_status: dict[FederateHandle, RestoreStatus] = field(default_factory=dict)
    last_save_name: str | None = None
    last_save_time: Any | None = None
    next_save_name: str | None = None
    next_save_time: Any | None = None
    saved_time_states: dict[str, dict[FederateHandle, dict[str, Any]]] = field(default_factory=dict)
    saved_object_snapshots: dict[str, dict[ObjectInstanceHandle, ObjectInstance]] = field(default_factory=dict)
    scheduled_save_requested_by: FederateHandle | None = None

    # Time-management queues (§8.1.6 and §8.8-§8.13).
    tso_messages: list[TimedMessage] = field(default_factory=list)
    next_message_sequence: int = 1

    # MOM/MIM runtime objects (§11 and Annex G).
    mom_federation_object: ObjectInstanceHandle | None = None
    mom_federate_objects: dict[FederateHandle, ObjectInstanceHandle] = field(default_factory=dict)
    mom_auto_provide: bool = True
    auto_provide: bool = True


@dataclass
class CallbackEvent:
    method_name: str
    args: tuple[Any, ...]


@dataclass
class TimeAdvanceRequestState:
    """One pending time-advance request.

    Section anchors: IEEE 1516.1-2010 §8.8 through §8.13.  The mode controls
    whether messages at the requested time are considered blocking/deliverable
    and whether the grant is a normal grant or a flush-queue grant.
    """

    mode: str
    requested_time: Any


@dataclass
class TimedMessage:
    """A TSO callback held by the local RTI until the recipient advances time."""

    sequence: int
    recipient: FederateHandle
    timestamp: Any
    event: CallbackEvent
    retraction_handle: MessageRetractionHandle
    producing_federate: FederateHandle | None = None
    retracted: bool = False


RTI_FEDERATE_HANDLE = FederateHandle(0)
MOM_TEXT_ENCODING = "utf-8"
MOM_FEDERATION_CLASS = "HLAobjectRoot.HLAmanager.HLAfederation"
MOM_FEDERATE_CLASS = "HLAobjectRoot.HLAmanager.HLAfederate"


@dataclass(order=True)
class QueuedTimeMessage:
    """Queued HLA message used by local time-management delivery.

    Section anchor: IEEE 1516.1-2010 §8.1.1-§8.1.6 and Table 1-Table 3.
    The RTI sorts timestamp-order (TSO) messages by timestamp and stable send
    sequence; receive-order (RO) messages keep local FIFO order.
    """

    sort_key: tuple[float | int, int]
    timestamp: Any = field(compare=False)
    sent_order: OrderType = field(compare=False)
    received_order: OrderType = field(compare=False)
    callback: CallbackEvent = field(compare=False)
    retraction_handle: MessageRetractionHandle | None = field(default=None, compare=False)
    sender: FederateHandle | None = field(default=None, compare=False)
    service_name: str = field(default="", compare=False)
    retracted: bool = field(default=False, compare=False)


@dataclass
class FederateState:
    backend_id: int
    ambassador: FederateAmbassador | None = None
    callback_model: CallbackModel = CallbackModel.HLA_EVOKED
    connected: bool = False
    local_settings_designator: str | None = None
    handle: FederateHandle | None = None
    name: str | None = None
    federate_type: str | None = None
    federation: FederationState | None = None
    callbacks_enabled: bool = True
    queue: Deque[CallbackEvent] = field(default_factory=deque)

    published_objects: dict[ObjectClassHandle, set[AttributeHandle]] = field(default_factory=dict)
    subscribed_objects: dict[ObjectClassHandle, set[AttributeHandle]] = field(default_factory=dict)
    published_interactions: set[InteractionClassHandle] = field(default_factory=set)
    subscribed_interactions: set[InteractionClassHandle] = field(default_factory=set)
    regions: dict[RegionHandle, set[DimensionHandle]] = field(default_factory=dict)
    region_bounds: dict[RegionHandle, dict[DimensionHandle, RangeBounds]] = field(default_factory=dict)
    update_regions: dict[ObjectInstanceHandle, dict[AttributeHandle, set[RegionHandle]]] = field(default_factory=dict)
    object_region_subscriptions: dict[ObjectClassHandle, dict[AttributeHandle, set[RegionHandle]]] = field(default_factory=dict)
    interaction_region_subscriptions: dict[InteractionClassHandle, set[RegionHandle]] = field(default_factory=dict)

    # Time-management state (§8).  The implementation uses federation-level
    # ``TimedMessage`` queues for TSO message delivery; the per-federate queues
    # remain available for MOM length reporting and future queue-refinement work.
    time_regulation_enabled: bool = False
    time_constrained_enabled: bool = False
    time_advancing: bool = False
    pending_time_advance: TimeAdvanceRequestState | None = None
    current_time: Any = field(default_factory=lambda: HLAinteger64Time(0))
    lookahead: Any = None
    requested_time: Any | None = None
    time_advance_kind: str | None = None
    last_time_advance_kind: str | None = None
    last_grant_mode: str | None = None
    zero_lookahead_tarnmr_restriction: bool = False
    asynchronous_delivery_enabled: bool = False
    ro_message_queue: Deque[QueuedTimeMessage] = field(default_factory=deque)
    tso_message_heap: list[QueuedTimeMessage] = field(default_factory=list)
    retraction_messages: dict[MessageRetractionHandle, QueuedTimeMessage] = field(default_factory=dict)
    retractable_messages: dict[MessageRetractionHandle, bool] = field(default_factory=dict)

    # MOM-visible switches/state (§11).
    mom_federate_object: ObjectInstanceHandle | None = None
    automatic_resign_directive: ResignAction = ResignAction.NO_ACTION
    object_class_relevance_advisory: bool = False
    attribute_relevance_advisory: bool = False
    attribute_scope_advisory: bool = False
    interaction_relevance_advisory: bool = False
    convey_region_designator_sets: bool = False
    convey_producing_federate: bool = True
    service_reporting: bool = False
    exception_reporting: bool = True
    service_reports_to_file: bool = False
    service_report_file: str | None = None
    service_report_initial_record_written: bool = False
    service_report_serial_number: int = 0
    service_report_records: list[dict[str, Any]] = field(default_factory=list)

    attribute_order_overrides: dict[tuple[ObjectInstanceHandle, AttributeHandle], OrderType] = field(default_factory=dict)
    interaction_order_overrides: dict[InteractionClassHandle, OrderType] = field(default_factory=dict)

    updates_sent: int = 0
    reflections_received: int = 0
    interactions_sent: int = 0
    interactions_received: int = 0
    object_instances_registered: int = 0
    object_instances_discovered: int = 0
    object_instances_updated: int = 0
    object_instances_reflected: int = 0
    object_instances_deleted: int = 0
    object_instances_removed: int = 0
    last_optimistic_logical_time: Any | None = None
    mom_report_period: float = 0.0
    mom_attribute_reporting: dict[tuple[ObjectInstanceHandle, AttributeHandle], bool] = field(default_factory=dict)
    mom_attribute_reporting_states: dict[tuple[str, str], str] = field(default_factory=dict)


class InMemoryRTIEngine:
    """Shared RTI state used by one or more PythonRTIBackend instances.

    Create one engine per local federation process, then create one ambassador
    per federate using that same engine.
    """

    def __init__(self, *, name: str = "python-inmemory-rti", fom_resolver: FOMResolver | None = None, time_factories: TimeFactoryRegistry | None = None) -> None:
        self.name = name
        self._lock = RLock()
        self._next_backend_id = 1
        self._next_values: dict[type[Any], int] = {
            FederateHandle: 1,
            ObjectClassHandle: 1,
            AttributeHandle: 1,
            ObjectInstanceHandle: 1,
            InteractionClassHandle: 1,
            ParameterHandle: 1,
            DimensionHandle: 1,
            RegionHandle: 1,
            TransportationTypeHandle: 1,
            MessageRetractionHandle: 1,
        }
        self._next_tso_sequence = 1
        self.federations: dict[str, FederationState] = {}
        self.object_classes_by_name: dict[str, ObjectClassDef] = {}
        self.object_class_by_handle: dict[ObjectClassHandle, ObjectClassDef] = {}
        self.interactions_by_name: dict[str, InteractionClassDef] = {}
        self.interaction_by_handle: dict[InteractionClassHandle, InteractionClassDef] = {}
        self.dimensions_by_name: dict[str, DimensionHandle] = {}
        self.dimension_names: dict[DimensionHandle, str] = {}
        self.transportation_reliable = self._alloc(TransportationTypeHandle)
        self.fom_resolver = fom_resolver or FOMResolver()
        self.time_factories = time_factories or DEFAULT_TIME_FACTORY_REGISTRY
        self._bootstrap_standard_names()

    def _bootstrap_standard_names(self) -> None:
        self.get_or_create_object_class("HLAobjectRoot")
        self.get_or_create_interaction_class("HLAinteractionRoot")
        self.get_or_create_dimension("HLAdefaultRoutingSpace")

    def new_federate_state(self) -> FederateState:
        with self._lock:
            backend_id = self._next_backend_id
            self._next_backend_id += 1
            return FederateState(backend_id=backend_id)

    def _alloc(self, handle_type: type[Any]) -> Any:
        value = self._next_values[handle_type]
        self._next_values[handle_type] = value + 1
        return handle_type(value)


    def _next_sequence(self) -> int:
        value = self._next_tso_sequence
        self._next_tso_sequence += 1
        return value

    def get_or_create_object_class(self, name: str) -> ObjectClassDef:
        with self._lock:
            if name not in self.object_classes_by_name:
                handle = self._alloc(ObjectClassHandle)
                definition = ObjectClassDef(name=str(name), handle=handle)
                self.object_classes_by_name[str(name)] = definition
                self.object_class_by_handle[handle] = definition
            return self.object_classes_by_name[str(name)]

    def object_class_for_handle(self, handle: ObjectClassHandle) -> ObjectClassDef:
        try:
            return self.object_class_by_handle[handle]
        except KeyError as exc:
            raise InvalidObjectClassHandle(repr(handle)) from exc

    def object_class_is_a(self, candidate: ObjectClassHandle, subscribed: ObjectClassHandle) -> bool:
        candidate_name = self.object_class_for_handle(candidate).name
        subscribed_name = self.object_class_for_handle(subscribed).name
        return candidate_name == subscribed_name or candidate_name.startswith(subscribed_name + ".")

    def get_or_create_attribute(self, object_class: ObjectClassHandle, name: str) -> AttributeHandle:
        definition = self.object_class_for_handle(object_class)
        if name not in definition.attributes_by_name:
            handle = self._alloc(AttributeHandle)
            definition.attributes_by_name[str(name)] = handle
            definition.attribute_names[handle] = str(name)
        return definition.attributes_by_name[str(name)]

    def attribute_name(self, object_class: ObjectClassHandle, attribute: AttributeHandle) -> str:
        definition = self.object_class_for_handle(object_class)
        try:
            return definition.attribute_names[attribute]
        except KeyError as exc:
            raise AttributeNotDefined(repr(attribute)) from exc

    def get_or_create_interaction_class(self, name: str) -> InteractionClassDef:
        with self._lock:
            if name not in self.interactions_by_name:
                handle = self._alloc(InteractionClassHandle)
                definition = InteractionClassDef(name=str(name), handle=handle)
                self.interactions_by_name[str(name)] = definition
                self.interaction_by_handle[handle] = definition
            return self.interactions_by_name[str(name)]

    def interaction_for_handle(self, handle: InteractionClassHandle) -> InteractionClassDef:
        try:
            return self.interaction_by_handle[handle]
        except KeyError as exc:
            raise InvalidInteractionClassHandle(repr(handle)) from exc

    def interaction_class_is_a(self, candidate: InteractionClassHandle, subscribed: InteractionClassHandle) -> bool:
        candidate_name = self.interaction_for_handle(candidate).name
        subscribed_name = self.interaction_for_handle(subscribed).name
        return candidate_name == subscribed_name or candidate_name.startswith(subscribed_name + ".")

    def get_or_create_parameter(self, interaction: InteractionClassHandle, name: str) -> ParameterHandle:
        definition = self.interaction_for_handle(interaction)
        if name not in definition.parameters_by_name:
            handle = self._alloc(ParameterHandle)
            definition.parameters_by_name[str(name)] = handle
            definition.parameter_names[handle] = str(name)
        return definition.parameters_by_name[str(name)]

    def parameter_name(self, interaction: InteractionClassHandle, parameter: ParameterHandle) -> str:
        definition = self.interaction_for_handle(interaction)
        try:
            return definition.parameter_names[parameter]
        except KeyError as exc:
            raise InteractionParameterNotDefined(repr(parameter)) from exc

    def get_or_create_dimension(self, name: str) -> DimensionHandle:
        with self._lock:
            if name not in self.dimensions_by_name:
                handle = self._alloc(DimensionHandle)
                self.dimensions_by_name[str(name)] = handle
                self.dimension_names[handle] = str(name)
            return self.dimensions_by_name[str(name)]

    def dimension_name(self, handle: DimensionHandle) -> str:
        try:
            return self.dimension_names[handle]
        except KeyError as exc:
            raise InvalidDimensionHandle(repr(handle)) from exc

    def install_fom_module(self, module: FOMModule) -> None:
        """Install parsed FOM names into the engine handle tables."""

        with self._lock:
            for object_spec in module.object_classes:
                object_def = self.get_or_create_object_class(object_spec.full_name)
                for attribute_name in object_spec.attributes:
                    self.get_or_create_attribute(object_def.handle, attribute_name)

            for interaction_spec in module.interaction_classes:
                interaction_def = self.get_or_create_interaction_class(interaction_spec.full_name)
                for parameter_name in interaction_spec.parameters:
                    self.get_or_create_parameter(interaction_def.handle, parameter_name)

            for dimension_name in module.dimensions:
                self.get_or_create_dimension(dimension_name)

    def install_fom_modules(self, modules: Iterable[FOMModule]) -> None:
        for module in modules:
            self.install_fom_module(module)


def _enum_name(value: Any) -> str:
    name_attr = getattr(value, "name", None)
    if isinstance(name_attr, str):
        return name_attr
    if callable(name_attr):
        try:
            return str(name_attr())
        except Exception:
            pass
    return str(value)


def _time_value(value: Any) -> float | int:
    return tm.time_value(value)


def _time_key(value: Any) -> float:
    return tm.time_key(value)


def _time_lt(left: Any, right: Any) -> bool:
    return tm.time_lt(left, right)


def _time_le(left: Any, right: Any) -> bool:
    return tm.time_le(left, right)


def _time_ge(left: Any, right: Any) -> bool:
    return tm.time_ge(left, right)


def _time_min(values: Iterable[Any]) -> Any:
    return tm.time_min(values)


def _as_mom_bytes(value: Any) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return str(value).encode(MOM_TEXT_ENCODING)


def _handle_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _is_non_string_sequence(value: Any) -> bool:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return False
    return isinstance(value, Iterable)


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if _is_non_string_sequence(value):
        return tuple(value)
    return (value,)


def _looks_like_time_factory_name(value: Any, registry: TimeFactoryRegistry) -> bool:
    return isinstance(value, str) and value in registry


def _parse_create_federation_args(
    raw_args: tuple[Any, ...],
    *,
    registry: TimeFactoryRegistry,
    default_time_name: str,
) -> tuple[tuple[Any, ...], Any | None, str | None]:
    """Return ``(fom_sources, mim_source, explicit_logical_time_name)`` for HLA overloads."""

    foms: tuple[Any, ...] = ()
    mim: Any | None = None
    time_name: str | None = None
    args = tuple(raw_args)

    if not args:
        return foms, mim, time_name

    if len(args) == 1:
        if _looks_like_time_factory_name(args[0], registry):
            return (), None, str(args[0])
        return _as_tuple(args[0]), None, time_name

    if len(args) == 2:
        first, second = args
        if _looks_like_time_factory_name(second, registry):
            return _as_tuple(first), None, str(second)
        return _as_tuple(first), second, time_name

    if len(args) == 3:
        first, second, third = args
        if _looks_like_time_factory_name(third, registry):
            return _as_tuple(first), second, str(third)
        # Last-resort Python convenience: treat all three as FOM modules.
        return args, None, time_name

    if _looks_like_time_factory_name(args[-1], registry):
        return tuple(args[:-1]), None, str(args[-1])
    return args, None, time_name


def _parse_join_args(args: tuple[Any, ...]) -> tuple[str, str, str, tuple[Any, ...]]:
    """Return ``(federate_name, federate_type, federation_name, additional_foms)``."""

    if len(args) == 2:
        federate_type, federation_name = args
        return "", str(federate_type), str(federation_name), ()

    if len(args) == 3:
        a, b, c = args
        if _is_non_string_sequence(c):
            return "", str(a), str(b), _as_tuple(c)
        return str(a), str(b), str(c), ()

    if len(args) >= 4:
        federate_name, federate_type, federation_name, additional = args[:4]
        return str(federate_name), str(federate_type), str(federation_name), _as_tuple(additional)

    raise RTIinternalError(f"Bad joinFederationExecution arguments: {args!r}")


class PythonRTIBackend(RTIBackend):
    """A dependency-free RTIBackend implemented entirely in Python."""

    def __init__(
        self,
        *,
        engine: InMemoryRTIEngine | None = None,
        config: PythonRTIConfig | None = None,
        federate_state: FederateState | None = None,
    ) -> None:
        self.engine = engine or InMemoryRTIEngine()
        self.config = config or PythonRTIConfig(name=self.engine.name)
        self.fom_resolver = (
            FOMResolver(
                base_paths=tuple(self.config.fom_search_paths),
                require_local_parse=(self.config.require_fom_parse or self.config.strict_fom_loading),
            )
            if (self.config.fom_search_paths or self.config.require_fom_parse or self.config.strict_fom_loading)
            else self.engine.fom_resolver
        )
        self.state = federate_state or self.engine.new_federate_state()
        self.delivered_callback_count = 0
        self.service_report_sink = (
            ServiceReportSink(self.config.service_report_file, truncate=self.config.service_report_file_truncate)
            if self.config.service_report_file
            else None
        )
        self.info = BackendInfo(
            name=self.config.name,
            kind="python/in-memory",
            version=self.config.version,
            details={"engine": self.engine.name, "backend_id": self.state.backend_id},
        )

    # RTIBackend interface -------------------------------------------------
    def invoke(self, invocation: Invocation) -> Any:
        service = getattr(self, f"_svc_{invocation.method_name}", None)
        if service is None:
            raise UnsupportedBackendService(
                f"Python in-memory RTI does not yet implement {invocation.method_name}"
            )
        args = resolve_java_arguments(invocation)
        try:
            result = service(*args)
        except RTIexception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        except Exception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        self._report_service_invocation(invocation.method_name, success=True, exception_name="", args=args, result=result)
        return result

    def pending_callback_count(self) -> int:
        return len(self.state.queue)

    def current_fom_catalog(self) -> FOMCatalog:
        """Return the current FOM/FDD catalog for the joined federation.

        Section anchor: IEEE 1516.1-2010 4.1.4.2 access to current FOM
        information.  This is a Python convenience mirror of the MOM-visible
        information rather than a standard RTIambassador service.
        """

        federation = self._require_joined()
        return federation.fom_catalog

    def current_fom_summary(self) -> dict[str, Any]:
        return self.current_fom_catalog().as_summary()

    def close(self) -> None:
        """Best-effort cleanup for examples/tests."""
        try:
            if self.state.connected and self.state.handle is not None:
                self._svc_resignFederationExecution(ResignAction.NO_ACTION)
            if self.state.connected:
                self._svc_disconnect()
        except Exception:
            # Close is deliberately non-throwing; explicit HLA calls still raise.
            pass

    # Helpers --------------------------------------------------------------
    def _require_connected(self) -> None:
        if not self.state.connected:
            raise NotConnected("RTI ambassador is not connected")

    def _require_joined(self) -> FederationState:
        self._require_connected()
        federation = self.state.federation
        if self.state.handle is None or federation is None:
            raise FederateNotExecutionMember("Federate has not joined a federation execution")
        return federation

    def _federate_name(self, state: FederateState | None = None) -> str:
        state = state or self.state
        return state.name or f"Federate-{state.backend_id}"

    def _enforce_fom_names(self, federation: FederationState) -> bool:
        """Return whether handle lookup should reject names absent from the FDD catalog."""

        return bool(self.config.strict_fom_lookup and federation.fom_catalog.modules)

    def _time_factory(self) -> LogicalTimeFactory[Any, Any]:
        federation = self.state.federation
        if federation is not None:
            return federation.time_factory
        return self.engine.time_factories.get(self.config.default_logical_time_implementation_name)

    def _coerce_time(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_time(value)
        except Exception as exc:
            raise InvalidLogicalTime(repr(value)) from exc

    def _coerce_interval(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_interval(value)
        except Exception as exc:
            raise InvalidLookahead(repr(value)) from exc

    def _resolve_fom_modules(
        self,
        sources: Iterable[Any] | Any | None,
        *,
        require_non_empty: bool = False,
        mim: bool = False,
    ) -> tuple[FOMModule, ...]:
        try:
            modules = self.fom_resolver.resolve_many(sources)
            if require_non_empty and not modules:
                raise FOMResolutionError("At least one FOM module designator is required")
            if self.config.require_fom_parse or self.config.strict_fom_loading:
                for module in modules:
                    if module.uri.startswith("builtin:"):
                        continue
                    if not module.parsed:
                        raise FOMResolutionError(f"FOM module could not be parsed locally by the Python RTI: {module.uri}")
            return modules
        except FOMResolutionError as exc:
            if mim:
                from ..exceptions import CouldNotOpenMIM

                raise CouldNotOpenMIM(str(exc)) from exc
            raise CouldNotOpenFDD(str(exc)) from exc

    def _combine_fom_catalog(
        self,
        modules: Iterable[FOMModule],
        *,
        mim_module: FOMModule | None = None,
        base_catalog: FOMCatalog | None = None,
    ) -> FOMCatalog:
        try:
            base_modules = tuple(base_catalog.modules) if base_catalog is not None else ()
            effective_mim = mim_module if mim_module is not None else (base_catalog.mim_module if base_catalog is not None else standard_mim_module())
            return merge_fom_modules((*base_modules, *tuple(modules)), mim_module=effective_mim)
        except FOMMergeError as exc:
            raise InconsistentFDD(str(exc)) from exc

    def _current_fom_summary(self, federation: FederationState | None = None) -> dict[str, Any]:
        federation = federation or self._require_joined()
        return federation.fom_catalog.as_summary()

    def _choose_time_factory(self, requested_name: str | None, modules: Iterable[FOMModule]) -> LogicalTimeFactory[Any, Any]:
        name = requested_name or self.config.default_logical_time_implementation_name
        if self.config.infer_time_factory_from_fom and not requested_name:
            for module in modules:
                if module.inferred_time_implementation:
                    name = module.inferred_time_implementation
                    break
        try:
            return self.engine.time_factories.get(name)
        except KeyError as exc:
            raise CouldNotCreateLogicalTimeFactory(str(exc)) from exc

    def _deliver(self, target: FederateState, method_name: str, *args: Any) -> None:
        if target.ambassador is None:
            return
        if target.callback_model is CallbackModel.HLA_IMMEDIATE and self.config.immediate_callbacks_inline:
            self._invoke_callback(target, method_name, args)
        else:
            target.queue.append(CallbackEvent(method_name, tuple(args)))

    def _invoke_callback(self, target: FederateState, method_name: str, args: tuple[Any, ...]) -> None:
        if target.ambassador is None:
            return
        try:
            getattr(target.ambassador, method_name)(*args)
            self.delivered_callback_count += 1
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(
                f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc
            ) from exc

    def _find_object(self, handle: ObjectInstanceHandle) -> tuple[FederationState, ObjectInstance]:
        federation = self._require_joined()
        try:
            return federation, federation.objects[handle]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(handle)) from exc

    def _object_matches_subscription(self, instance_class: ObjectClassHandle, subscribed_class: ObjectClassHandle) -> bool:
        try:
            return self.engine.object_class_is_a(instance_class, subscribed_class)
        except InvalidObjectClassHandle:
            return instance_class == subscribed_class

    def _interaction_matches_subscription(self, interaction_class: InteractionClassHandle, subscribed_class: InteractionClassHandle) -> bool:
        try:
            return self.engine.interaction_class_is_a(interaction_class, subscribed_class)
        except InvalidInteractionClassHandle:
            return interaction_class == subscribed_class

    def _discover_existing_objects(self, subscriber: FederateState, object_class: ObjectClassHandle) -> None:
        federation = subscriber.federation
        if federation is None:
            return
        for instance in federation.objects.values():
            if self._object_matches_subscription(instance.class_handle, object_class):
                self._deliver(
                    subscriber,
                    "discoverObjectInstance",
                    instance.handle,
                    instance.class_handle,
                    instance.name,
                    instance.owner or RTI_FEDERATE_HANDLE,
                )

    def _subscribed_attributes_for(self, subscriber: FederateState, object_class: ObjectClassHandle) -> set[AttributeHandle]:
        result: set[AttributeHandle] = set()
        for subscribed_class, attrs in subscriber.subscribed_objects.items():
            if self._object_matches_subscription(object_class, subscribed_class):
                result.update(attrs)
        return result

    def _attribute_region_allows(self, subscriber: FederateState, instance: ObjectInstance, attribute: AttributeHandle, sent_regions: set[RegionHandle] | None) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, attr_regions in subscriber.object_region_subscriptions.items():
            if self._object_matches_subscription(instance.class_handle, subscribed_class):
                subscription_regions.update(attr_regions.get(attribute, set()))
        if not subscription_regions:
            return True
        return self._region_sets_overlap(self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _interaction_region_allows(self, subscriber: FederateState, interaction_class: InteractionClassHandle, sent_regions: set[RegionHandle] | None) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, regions in subscriber.interaction_region_subscriptions.items():
            if self._interaction_matches_subscription(interaction_class, subscribed_class):
                subscription_regions.update(regions)
        if not subscription_regions:
            return True
        return self._region_sets_overlap(self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _attribute_subscription_intersection(
        self,
        subscriber: FederateState,
        object_class: ObjectClassHandle,
        attributes: Mapping[AttributeHandle, bytes],
        instance: ObjectInstance | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set[RegionHandle]] | None = None,
    ) -> dict[AttributeHandle, bytes]:
        subscribed = self._subscribed_attributes_for(subscriber, object_class)
        if not subscribed:
            return {}
        reflected: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            if handle not in subscribed:
                continue
            if instance is not None and not self._attribute_region_allows(
                subscriber,
                instance,
                handle,
                set((sent_regions_by_attribute or {}).get(handle, set())),
            ):
                continue
            reflected[handle] = value
        return reflected

    def _announce_synchronization_point(
        self,
        federation: FederationState,
        point: SynchronizationPointState,
        handle: FederateHandle,
    ) -> None:
        target = federation.federates.get(handle)
        if target is None:
            return
        point.targets.add(handle)
        point.announced.add(handle)
        self._deliver(target, "announceSynchronizationPoint", point.label, point.tag)

    def _complete_synchronization_point_if_ready(self, federation: FederationState, point: SynchronizationPointState) -> None:
        active_targets = {handle for handle in point.targets if handle in federation.federates}
        point.targets.intersection_update(active_targets)
        point.announced.intersection_update(active_targets)
        point.achieved.intersection_update(active_targets)
        point.failed.intersection_update(active_targets)
        if not active_targets or not active_targets.issubset(point.reported()):
            return
        failed = hla_handles.FederateHandleSet(point.failed)
        for handle in sorted(active_targets, key=lambda h: h.value):
            target = federation.federates.get(handle)
            if target is not None:
                self._deliver(target, "federationSynchronized", point.label, failed)
        federation.synchronization_points.pop(point.label, None)

    def _remove_federate_from_synchronization_points(self, federation: FederationState, handle: FederateHandle) -> None:
        for point in list(federation.synchronization_points.values()):
            point.targets.discard(handle)
            point.announced.discard(handle)
            point.achieved.discard(handle)
            point.failed.discard(handle)
            self._complete_synchronization_point_if_ready(federation, point)

    def _announce_open_synchronization_points_to_joiner(self, federation: FederationState, handle: FederateHandle) -> None:
        for point in list(federation.synchronization_points.values()):
            if point.open_to_late_joiners and handle not in point.reported():
                self._announce_synchronization_point(federation, point, handle)

    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None:
        if federation.save_label is not None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")

    # MOM/MIM helpers -------------------------------------------------------
    def _class_handle_by_name(self, name: str) -> ObjectClassHandle:
        return self.engine.get_or_create_object_class(name).handle

    def _interaction_handle_by_name(self, name: str) -> InteractionClassHandle:
        return self.engine.get_or_create_interaction_class(name).handle

    def _attr_handle_by_name(self, class_name: str, attr_name: str) -> AttributeHandle:
        return self.engine.get_or_create_attribute(self._class_handle_by_name(class_name), attr_name)

    def _param_handle_by_name(self, interaction_name: str, param_name: str) -> ParameterHandle:
        return self.engine.get_or_create_parameter(self._interaction_handle_by_name(interaction_name), param_name)

    def _mom_parameter_map(self, interaction_name: str, values: Mapping[str, Any]) -> dict[ParameterHandle, bytes]:
        return {
            self._param_handle_by_name(interaction_name, name): _as_mom_bytes(value)
            for name, value in values.items()
        }

    def _mom_attribute_map(self, class_name: str, values: Mapping[str, Any]) -> dict[AttributeHandle, bytes]:
        return {
            self._attr_handle_by_name(class_name, name): _as_mom_bytes(value)
            for name, value in values.items()
        }

    def _make_internal_object(self, federation: FederationState, class_name: str, object_name: str) -> ObjectInstance:
        class_handle = self._class_handle_by_name(class_name)
        existing = federation.object_names.get(object_name)
        if existing is not None:
            return federation.objects[existing]
        handle = self.engine._alloc(ObjectInstanceHandle)
        instance = ObjectInstance(handle=handle, class_handle=class_handle, name=object_name, owner=RTI_FEDERATE_HANDLE)
        federation.objects[handle] = instance
        federation.object_names[object_name] = handle
        for federate in list(federation.federates.values()):
            if any(self._object_matches_subscription(class_handle, subscribed) for subscribed in federate.subscribed_objects):
                self._deliver(federate, "discoverObjectInstance", handle, class_handle, object_name, RTI_FEDERATE_HANDLE)
        return instance

    def _reflect_internal_attribute_update(self, federation: FederationState, instance: ObjectInstance, attributes: Mapping[AttributeHandle, bytes]) -> None:
        for federate in list(federation.federates.values()):
            reflected = self._attribute_subscription_intersection(federate, instance.class_handle, attributes, instance)
            if reflected:
                self._deliver(
                    federate,
                    "reflectAttributeValues",
                    instance.handle,
                    reflected,
                    b"MOM",
                    OrderType.RECEIVE,
                    self.engine.transportation_reliable,
                    SupplementalReflectInfo(producing_federate=RTI_FEDERATE_HANDLE),
                )

    def _set_internal_attributes(self, federation: FederationState, instance: ObjectInstance, attributes: Mapping[AttributeHandle, bytes], *, notify: bool = True) -> None:
        changed: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            value_bytes = bytes(value)
            if instance.attributes.get(handle) != value_bytes:
                changed[handle] = value_bytes
                instance.attributes[handle] = value_bytes
            instance.attribute_owners[handle] = RTI_FEDERATE_HANDLE
        if changed and notify:
            self._reflect_internal_attribute_update(federation, instance, changed)

    def _fom_module_designator_list(self, federation: FederationState) -> str:
        return "\n".join(module.uri for module in federation.fom_modules)

    def _fdd_summary_text(self, federation: FederationState) -> str:
        summary = federation.fom_catalog.as_summary()
        lines = [
            f"MIM={summary.get('mim_uri') or ''}",
            "FOMs=" + ";".join(summary.get("module_uris", [])),
            "Objects=" + ";".join(summary.get("object_classes", [])),
            "Interactions=" + ";".join(summary.get("interaction_classes", [])),
            "Dimensions=" + ";".join(summary.get("dimensions", [])),
            f"Time={summary.get('logical_time_implementation') or federation.time_factory.get_name()}",
        ]
        return "\n".join(lines)

    def _module_xml_or_uri(self, module: FOMModule | None) -> bytes:
        if module is None:
            return b""
        if module.path is not None and module.path.exists():
            try:
                return module.path.read_bytes()
            except OSError:
                pass
        return _as_mom_bytes(module.uri)

    def _all_fom_module_data(self, federation: FederationState) -> bytes:
        payloads: list[bytes] = []
        for index, module in enumerate(federation.fom_modules):
            payloads.append(f"--- FOM module {index}: {module.uri}\n".encode(MOM_TEXT_ENCODING))
            payloads.append(self._module_xml_or_uri(module))
            payloads.append(b"\n")
        return b"".join(payloads) if payloads else b""

    def _ensure_mom_federation_object(self, federation: FederationState) -> None:
        instance = self._make_internal_object(federation, MOM_FEDERATION_CLASS, f"HLAmanager.HLAfederation.{federation.name}")
        federation.mom_federation_object = instance.handle
        self._refresh_mom_federation_object(federation, notify=False)

    def _ensure_mom_federate_object(self, federation: FederationState, federate: FederateState) -> None:
        if federate.handle is None:
            return
        name = f"HLAmanager.HLAfederate.{federate.handle.value}.{federate.name or 'unnamed'}"
        instance = self._make_internal_object(federation, MOM_FEDERATE_CLASS, name)
        federation.mom_federate_objects[federate.handle] = instance.handle
        federate.mom_federate_object = instance.handle
        self._refresh_mom_federate_object(federation, federate, notify=False)

    def _refresh_mom_federation_object(self, federation: FederationState, *, notify: bool = True) -> None:
        if federation.mom_federation_object is None:
            return
        instance = federation.objects.get(federation.mom_federation_object)
        if instance is None:
            return
        attrs = self._mom_attribute_map(
            MOM_FEDERATION_CLASS,
            {
                "HLAfederationName": federation.name,
                "HLAfederatesInFederation": ",".join(sorted(f.name or _handle_value(h) for h, f in federation.federates.items())),
                "HLARTIversion": self._svc_getHLAversion(),
                "HLAMIMdesignator": (federation.mim_module.uri if federation.mim_module else "builtin:HLAstandardMIM"),
                "HLAFOMmoduleDesignatorList": self._fom_module_designator_list(federation),
                "HLAcurrentFDD": self._fdd_summary_text(federation),
                "HLAtimeImplementationName": federation.time_factory.get_name(),
                "HLAlastSaveName": federation.save_label or "",
                "HLAnextSaveName": federation.save_label or "",
                "HLAautoProvide": str(federation.mom_auto_provide).lower(),
            },
        )
        self._set_internal_attributes(federation, instance, attrs, notify=notify)

    def _refresh_mom_federate_object(self, federation: FederationState, federate: FederateState, *, notify: bool = True) -> None:
        if federate.handle is None or federate.mom_federate_object is None:
            return
        instance = federation.objects.get(federate.mom_federate_object)
        if instance is None:
            return
        galt = self._compute_galt(federation, federate)
        lits = self._compute_lits(federation, federate)
        attrs = self._mom_attribute_map(
            MOM_FEDERATE_CLASS,
            {
                "HLAfederateHandle": _handle_value(federate.handle),
                "HLAfederateName": federate.name or "",
                "HLAfederateType": federate.federate_type or "",
                "HLAfederateHost": "local-python",
                "HLARTIversion": self._svc_getHLAversion(),
                "HLAFOMmoduleDesignatorList": self._fom_module_designator_list(federation),
                "HLAtimeConstrained": str(federate.time_constrained_enabled).lower(),
                "HLAtimeRegulating": str(federate.time_regulation_enabled).lower(),
                "HLAasynchronousDelivery": str(federate.asynchronous_delivery_enabled).lower(),
                "HLAfederateState": "TimeAdvancing" if federate.time_advancing else "Granted",
                "HLAtimeManagerState": (federate.pending_time_advance.mode if federate.pending_time_advance else "Granted"),
                "HLAlogicalTime": _time_value(federate.current_time),
                "HLAlookahead": _time_value(federate.lookahead) if federate.lookahead is not None else "",
                "HLAGALT": _time_value(galt.time) if galt.time_is_valid else "",
                "HLALITS": _time_value(lits.time) if lits.time_is_valid else "",
                "HLAobjectClassRelevanceAdvisorySwitch": str(federate.object_class_relevance_advisory).lower(),
                "HLAattributeRelevanceAdvisorySwitch": str(federate.attribute_relevance_advisory).lower(),
                "HLAattributeScopeAdvisorySwitch": str(federate.attribute_scope_advisory).lower(),
                "HLAinteractionRelevanceAdvisorySwitch": str(federate.interaction_relevance_advisory).lower(),
            },
        )
        self._set_internal_attributes(federation, instance, attrs, notify=notify)

    def _refresh_all_mom_objects(self, federation: FederationState, *, notify: bool = True) -> None:
        self._refresh_mom_federation_object(federation, notify=notify)
        for federate in list(federation.federates.values()):
            self._refresh_mom_federate_object(federation, federate, notify=notify)

    def _deliver_mom_report_to_invoker(self, interaction_name: str, values: Mapping[str, Any]) -> None:
        federation = self._require_joined()
        interaction = self._interaction_handle_by_name(interaction_name)
        params = self._mom_parameter_map(interaction_name, values)
        self._deliver(
            self.state,
            "receiveInteraction",
            interaction,
            params,
            b"MOM",
            OrderType.RECEIVE,
            self.engine.transportation_reliable,
            SupplementalReceiveInfo(producing_federate=RTI_FEDERATE_HANDLE),
        )

    def current_mom_summary(self) -> dict[str, Any]:
        federation = self._require_joined()
        return {
            "federation_object": federation.mom_federation_object,
            "federate_objects": dict(federation.mom_federate_objects),
            "mim_uri": federation.mim_module.uri if federation.mim_module else None,
            "mom_object_classes": sorted(name for name in federation.fom_catalog.object_classes if ".HLAmanager" in name),
            "mom_interaction_classes": sorted(name for name in federation.fom_catalog.interaction_classes if ".HLAmanager" in name),
            "mom_model": self._mom_exposure_model(federation).as_summary(),
            "mom_interaction_matrix": self._mom_exposure_model(federation).interaction_matrix(),
            "mom_object_matrix": self._mom_exposure_model(federation).object_matrix(),
        }

    # Time-management helpers ----------------------------------------------
    def _queued_tso_for(self, federation: FederationState, recipient: FederateState) -> list[TimedMessage]:
        if recipient.handle is None:
            return []
        return sorted(
            (msg for msg in federation.tso_messages if msg.recipient == recipient.handle and not msg.retracted),
            key=lambda msg: (_time_key(msg.timestamp), msg.sequence),
        )

    def _make_retraction_return(self, timestamp: Any) -> MessageRetractionReturn:
        handle = self.engine._alloc(MessageRetractionHandle)
        self.state.retractable_messages[handle] = True
        return MessageRetractionReturn(handle, timestamp)

    def _queue_or_deliver_tso(self, federation: FederationState, target: FederateState, timestamp: Any | None, event: CallbackEvent, *, retraction_handle: MessageRetractionHandle | None, producing_federate: FederateHandle | None) -> None:
        """Compatibility wrapper over the consolidated per-federate time queue."""
        sent_order = OrderType.TIMESTAMP if timestamp is not None else OrderType.RECEIVE
        self._queue_or_deliver_message(
            target,
            event,
            sent_order=sent_order,
            timestamp=timestamp,
            sender=producing_federate,
            service_name=event.method_name,
            retraction_handle=retraction_handle,
        )

    def _eligible_tso_messages(self, federation: FederationState, federate: FederateState, request: TimeAdvanceRequestState) -> list[TimedMessage]:
        return tm.eligible_tso_messages(federation, federate, tm.TimeAdvanceRequestState(request.mode, request.requested_time))

    def _can_grant_time_request(self, federation: FederationState, federate: FederateState, request: TimeAdvanceRequestState) -> bool:
        """Return whether a pending time advance can be granted now.

        Section anchors: IEEE 1516.1-2010 §8.1.5 and §8.8-§8.13.
        """

        return tm.can_grant_time_request(
            federation,
            federate,
            tm.TimeAdvanceRequestState(request.mode, request.requested_time),
            enforce_galt=self.config.enforce_galt,
            factory=federation.time_factory,
        )

    def _grant_time_request(self, federation: FederationState, federate: FederateState, request: TimeAdvanceRequestState) -> None:
        normalized_request = tm.TimeAdvanceRequestState(request.mode, request.requested_time)
        messages = self._eligible_tso_messages(federation, federate, request)
        grant_time, optimistic_time = tm.grant_time_for_request(
            federation, federate, normalized_request, messages, factory=federation.time_factory
        )
        tm.remove_delivered_messages(federation, messages)
        for message in messages:
            if not message.retracted:
                event = getattr(message, "event", getattr(message, "callback", None))
                if event is not None:
                    self._deliver_time_message(federate, message) if hasattr(message, "callback") else self._deliver(federate, event.method_name, *event.args)

        old_time = federate.current_time
        federate.current_time = grant_time
        federate.last_optimistic_logical_time = optimistic_time
        federate.time_advancing = False
        federate.pending_time_advance = None
        federate.requested_time = None
        federate.last_time_advance_kind = request.mode
        federate.time_advance_kind = None
        federate.last_grant_mode = request.mode
        if request.mode in {"TAR", "NMR"} and getattr(federate.lookahead, "is_zero", lambda: False)():
            federate.zero_lookahead_tarnmr_restriction = True
        elif _time_lt(old_time, grant_time):
            federate.zero_lookahead_tarnmr_restriction = False
        self._deliver(federate, "timeAdvanceGrant", grant_time)
        self._refresh_mom_federate_object(federation, federate, notify=True)
        self._process_scheduled_saves(federation)

    def _process_time_advances(self, federation: FederationState) -> None:
        progressed = True
        while progressed:
            progressed = False
            for federate in list(federation.federates.values()):
                request = federate.pending_time_advance
                if request is None:
                    continue
                if self._can_grant_time_request(federation, federate, request):
                    self._grant_time_request(federation, federate, request)
                    progressed = True
        self._process_scheduled_saves(federation)
        self._refresh_mom_federation_object(federation, notify=True)

    def _request_time_advance(self, mode: str, theTime: Any) -> None:
        federation = self._require_joined()
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")
        if federation.save_label is not None and federation.next_save_time is None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if self.state.time_advancing:
            raise InTimeAdvancingState("Federate already has a pending time advance request")
        requested = self._coerce_time(theTime)
        if _time_lt(requested, self.state.current_time):
            raise LogicalTimeAlreadyPassed(repr(theTime))
        self.state.time_advancing = True
        self.state.pending_time_advance = TimeAdvanceRequestState(mode, requested)
        self.state.requested_time = requested
        self.state.time_advance_kind = mode
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    # MOM/MIM helpers -------------------------------------------------------
    def _is_mom_object_instance(self, federation: FederationState, instance: ObjectInstance) -> bool:
        try:
            class_name = self.engine.object_class_for_handle(instance.class_handle).name
        except Exception:
            return False
        return self.config.enable_mom and hla_mom.is_mom_object_class_name(class_name)

    def _ensure_mom_objects(self, federation: FederationState) -> None:
        """Create/update RTI-owned MOM object instances.

        Section anchor: IEEE 1516.1-2010 §11.2 and §11.4.1.  The RTI publishes
        the MOM federate/federation object classes and registers one federation
        object plus one federate object for each joined federate.
        """

        if not self.config.enable_mom:
            return
        fed_class = self.engine.get_or_create_object_class(hla_mom.MOM_FEDERATION_OBJECT_CLASS).handle
        federate_class = self.engine.get_or_create_object_class(hla_mom.MOM_FEDERATE_OBJECT_CLASS).handle
        if federation.mom_federation_object is None:
            handle = self.engine._alloc(ObjectInstanceHandle)
            name = f"{hla_mom.RTI_FEDERATION_OBJECT_NAME_PREFIX}.{federation.name}"
            federation.mom_federation_object = handle
            federation.objects[handle] = ObjectInstance(handle=handle, class_handle=fed_class, name=name, owner=None)
            federation.object_names[name] = handle
        for fed_handle, fed_state in list(federation.federates.items()):
            if fed_handle not in federation.mom_federate_objects:
                handle = self.engine._alloc(ObjectInstanceHandle)
                name = f"{hla_mom.RTI_FEDERATE_OBJECT_NAME_PREFIX}.{fed_handle.value}"
                federation.mom_federate_objects[fed_handle] = handle
                federation.objects[handle] = ObjectInstance(handle=handle, class_handle=federate_class, name=name, owner=None)
                federation.object_names[name] = handle
        self._refresh_mom_attribute_values(federation)

    def _mom_attribute_handle(self, class_name: str, attribute_name: str) -> AttributeHandle:
        class_handle = self.engine.get_or_create_object_class(class_name).handle
        return self.engine.get_or_create_attribute(class_handle, attribute_name)

    def _mom_parameter_handle(self, interaction_name: str, parameter_name: str) -> ParameterHandle:
        interaction_handle = self.engine.get_or_create_interaction_class(interaction_name).handle
        return self.engine.get_or_create_parameter(interaction_handle, parameter_name)

    def _filter_mom_attribute_values(self, federation: FederationState, class_name: str, values: Mapping[str, bytes]) -> dict[str, bytes]:
        rule = self._mom_object_rule(federation, class_name) if federation.fom_catalog.object_classes else None
        if rule is None:
            return dict(values)
        filtered: dict[str, bytes] = {}
        for name, data in values.items():
            canonical = mom_table.canonical_attribute_name(rule, name)
            if canonical in rule.attributes:
                filtered[canonical] = data
        return filtered

    def _refresh_mom_attribute_values(self, federation: FederationState) -> None:
        if not self.config.enable_mom:
            return
        if federation.mom_federation_object is not None and federation.mom_federation_object in federation.objects:
            obj = federation.objects[federation.mom_federation_object]
            values = {
                "HLAfederationName": hla_mom.encode_text(federation.name),
                "HLAfederatesInFederation": hla_mom.encode_handle_list(federation.federates.keys()),
                "HLARTIversion": hla_mom.encode_text(self._svc_getHLAversion()),
                "HLAMIMDesignator": hla_mom.encode_text(federation.mim_module.name if federation.mim_module else hla_mom.STANDARD_MIM_NAME),
                "HLAFOMmoduleDesignatorList": hla_mom.encode_text(",".join(module.uri for module in federation.fom_modules)),
                "HLAcurrentFDD": hla_mom.encode_text(str(federation.fom_catalog.as_summary())),
                "HLAtimeImplementationName": hla_mom.encode_text(federation.time_factory.get_name()),
                "HLAlastSaveName": hla_mom.encode_text(federation.last_save_name or ""),
                "HLAlastSaveTime": (federation.last_save_time.encode() if federation.last_save_time is not None and hasattr(federation.last_save_time, "encode") else b""),
                "HLAnextSaveName": hla_mom.encode_text(federation.next_save_name or ""),
                "HLAnextSaveTime": (federation.next_save_time.encode() if federation.next_save_time is not None and hasattr(federation.next_save_time, "encode") else b""),
                "HLAautoProvide": hla_mom.encode_bool(federation.auto_provide),
            }
            values = self._filter_mom_attribute_values(federation, hla_mom.MOM_FEDERATION_OBJECT_CLASS, values)
            obj.attributes.update({self._mom_attribute_handle(hla_mom.MOM_FEDERATION_OBJECT_CLASS, name): data for name, data in values.items()})
        for fed_handle, obj_handle in list(federation.mom_federate_objects.items()):
            fed_state = federation.federates.get(fed_handle)
            obj = federation.objects.get(obj_handle)
            if fed_state is None or obj is None:
                continue
            galt = self._compute_galt(federation, fed_state)
            lits = self._compute_lits(federation, fed_state)
            values = {
                "HLAfederateHandle": fed_handle.encode(),
                "HLAfederateName": hla_mom.encode_text(fed_state.name or ""),
                "HLAfederateType": hla_mom.encode_text(fed_state.federate_type or ""),
                "HLAfederateHost": hla_mom.encode_text(socket.gethostname()),
                "HLARTIversion": hla_mom.encode_text(self._svc_getHLAversion()),
                "HLAFOMmoduleDesignatorList": hla_mom.encode_text(",".join(module.uri for module in federation.fom_modules)),
                "HLAtimeConstrained": hla_mom.encode_bool(fed_state.time_constrained_enabled),
                "HLAtimeRegulating": hla_mom.encode_bool(fed_state.time_regulation_enabled),
                "HLAasynchronousDelivery": hla_mom.encode_bool(fed_state.asynchronous_delivery_enabled),
                "HLAfederateState": hla_mom.encode_text("TimeAdvancing" if fed_state.time_advancing else "TimeGranted"),
                "HLAtimeManagerState": hla_mom.encode_text(fed_state.time_advance_kind or fed_state.last_time_advance_kind or "TimeGranted"),
                "HLAlogicalTime": fed_state.current_time.encode() if hasattr(fed_state.current_time, "encode") else hla_mom.encode_text(fed_state.current_time),
                "HLAlookahead": fed_state.lookahead.encode() if hasattr(fed_state.lookahead, "encode") else hla_mom.encode_text(fed_state.lookahead),
                "HLAGALT": galt.time.encode() if galt.time_is_valid and hasattr(galt.time, "encode") else b"",
                "HLALITS": lits.time.encode() if lits.time_is_valid and hasattr(lits.time, "encode") else b"",
                "HLAROlength": hla_mom.encode_count(len(fed_state.ro_message_queue)),
                "HLATSOlength": hla_mom.encode_count(len([msg for msg in fed_state.tso_message_heap if not msg.retracted])),
                "HLAreflectionsReceived": hla_mom.encode_count(fed_state.reflections_received),
                "HLAupdatesSent": hla_mom.encode_count(fed_state.updates_sent),
                "HLAinteractionsReceived": hla_mom.encode_count(fed_state.interactions_received),
                "HLAinteractionsSent": hla_mom.encode_count(fed_state.interactions_sent),
                "HLAobjectInstancesThatCanBeDeleted": hla_mom.encode_count(0),
                "HLAobjectInstancesUpdated": hla_mom.encode_count(fed_state.object_instances_updated),
                "HLAobjectInstancesReflected": hla_mom.encode_count(fed_state.object_instances_reflected),
                "HLAobjectInstancesDeleted": hla_mom.encode_count(fed_state.object_instances_deleted),
                "HLAobjectInstancesRemoved": hla_mom.encode_count(fed_state.object_instances_removed),
                "HLAobjectInstancesRegistered": hla_mom.encode_count(fed_state.object_instances_registered),
                "HLAobjectInstancesDiscovered": hla_mom.encode_count(fed_state.object_instances_discovered),
                "HLAtimeGrantedTime": hla_mom.encode_count(0),
                "HLAtimeAdvancingTime": hla_mom.encode_count(0),
                "HLAconveyRegionDesignatorSets": hla_mom.encode_bool(fed_state.convey_region_designator_sets),
                "HLAconveyProducingFederate": hla_mom.encode_bool(fed_state.convey_producing_federate),
                "HLAserviceReporting": hla_mom.encode_bool(fed_state.service_reporting),
                "HLAexceptionReporting": hla_mom.encode_bool(fed_state.exception_reporting),
                "HLAreportServiceFile": hla_mom.encode_text(fed_state.service_report_file or ""),
                "HLAsendServiceReportsToFile": hla_mom.encode_bool(fed_state.service_reports_to_file),
            }
            values = self._filter_mom_attribute_values(federation, hla_mom.MOM_FEDERATE_OBJECT_CLASS, values)
            obj.attributes.update({self._mom_attribute_handle(hla_mom.MOM_FEDERATE_OBJECT_CLASS, name): data for name, data in values.items()})

    def _deliver_mom_attribute_update(self, instance: ObjectInstance, attrs: set[AttributeHandle], tag: bytes) -> None:
        federation = self._require_joined()
        self._refresh_mom_attribute_values(federation)
        reflected = {handle: data for handle, data in instance.attributes.items() if not attrs or handle in attrs}
        if reflected:
            self._deliver(
                self.state,
                "reflectAttributeValues",
                instance.handle,
                reflected,
                tag,
                OrderType.RECEIVE,
                self.engine.transportation_reliable,
                SupplementalReflectInfo(producing_federate=None),
            )

    # MOM service-report file helpers --------------------------------------
    def _service_report_directory(self) -> Path:
        raw = self.config.service_report_directory or os.environ.get("HLA2010_SERVICE_REPORT_DIR")
        if raw:
            directory = Path(raw)
        else:
            root = Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", "/private/tmp/hla-2010"))
            directory = root / "service_reports"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _ensure_service_report_file(self, federation: FederationState, federate: FederateState) -> str:
        if federate.service_report_file is None:
            safe_federation = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in federation.name)
            safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in (federate.name or f"federate-{federate.backend_id}"))
            handle_value = getattr(federate.handle, "value", federate.backend_id)
            path = self._service_report_directory() / f"{safe_federation}_{safe_name}_{handle_value}.service-report.jsonl"
            federate.service_report_file = str(path)
        if not federate.service_report_initial_record_written:
            self._write_service_report_initial_record(federation, federate)
        return federate.service_report_file

    def _json_safe(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return value.hex()
        if isinstance(value, Mapping):
            return {str(self._json_safe(k)): self._json_safe(v) for k, v in value.items()}
        if _is_non_string_sequence(value):
            return [self._json_safe(v) for v in value]
        if hasattr(value, "value"):
            return {"type": value.__class__.__name__, "value": getattr(value, "value")}
        return str(value)

    def _write_service_report_record(self, federation: FederationState, federate: FederateState, record: Mapping[str, Any]) -> None:
        path = federate.service_report_file or self._ensure_service_report_file(federation, federate)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(self._json_safe(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")

    def _write_service_report_initial_record(self, federation: FederationState, federate: FederateState) -> None:
        if federate.service_report_file is None:
            # Avoid recursion: allocate the path but do not call _ensure here.
            safe_federation = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in federation.name)
            safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in (federate.name or f"federate-{federate.backend_id}"))
            handle_value = getattr(federate.handle, "value", federate.backend_id)
            federate.service_report_file = str(self._service_report_directory() / f"{safe_federation}_{safe_name}_{handle_value}.service-report.jsonl")
        initial = {
            "recordType": "ServiceReportInitialRecord",
            "specSection": "1516.1-2010 §11.5.2",
            "timestampUTC": datetime.now(timezone.utc).isoformat(),
            "connect": {
                "callbackModel": _enum_name(federate.callback_model),
                "localSettingsDesignator": federate.local_settings_designator or "",
            },
            "federation": {
                "name": federation.name,
                "logicalTimeImplementation": federation.time_factory.get_name(),
                "mimDesignator": federation.mim_module.name if federation.mim_module else hla_mom.STANDARD_MIM_NAME,
                "fomModules": [module.uri for module in federation.fom_modules],
            },
            "federate": {
                "handle": getattr(federate.handle, "value", None),
                "name": federate.name,
                "type": federate.federate_type,
            },
        }
        self._write_service_report_record(federation, federate, initial)
        federate.service_report_initial_record_written = True

    def _append_service_report_record(
        self,
        service_name: str,
        *,
        success: bool,
        exception_name: str | None = None,
        args: Sequence[Any] | None = None,
        result: Any = None,
        section: str | None = None,
    ) -> None:
        federation = self.state.federation
        if federation is None or self.state.handle is None:
            return
        if not (self.state.service_reporting and self.state.service_reports_to_file):
            return
        self._ensure_service_report_file(federation, self.state)
        self.state.service_report_serial_number += 1
        record = {
            "recordType": "ServiceReportRecord",
            "specSection": f"1516.1-2010 §{section}" if section else "1516.1-2010 §11.5.2",
            "timestampUTC": datetime.now(timezone.utc).isoformat(),
            "serialNumber": self.state.service_report_serial_number,
            "federate": getattr(self.state.handle, "value", self.state.handle),
            "federateName": self.state.name or "",
            "service": service_name,
            "success": bool(success),
            "exception": exception_name or "",
            "arguments": {str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())},
            "returned": {"value": self._safe_report_arg(result)} if result is not None else {},
        }
        self.state.service_report_records.append(record)
        self._write_service_report_record(federation, self.state, record)
        self._refresh_mom_attribute_values(federation)

    def _mom_exposure_model(self, federation: FederationState) -> mom_table.MOMExposureModel:
        if federation.mom_model is None:
            federation.mom_model = mom_table.build_mom_exposure_model(federation.fom_catalog)
        return federation.mom_model

    def _mom_interaction_rule(self, federation: FederationState, interaction_name: str) -> mom_table.MOMInteractionRule | None:
        return self._mom_exposure_model(federation).interaction_rule(interaction_name)

    def _mom_object_rule(self, federation: FederationState, class_name: str) -> mom_table.MOMObjectClassRule | None:
        return self._mom_exposure_model(federation).object_rule(class_name)

    def _send_mom_exception(
        self,
        federation: FederationState,
        interaction_name: str,
        exception_name: str,
        parameter_error: str = "",
        *,
        federate: FederateHandle | None = None,
    ) -> None:
        """Send a MOM exception report using the active MIM report class.

        Section anchor: IEEE 1516.1-2010 §11.3/§11.4.1. The report class and
        parameters come from the table-driven MOM catalog, with the hard-coded
        name retained only as a fallback if the active FDD omits the report.
        """

        model = self._mom_exposure_model(federation)
        report_name = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportMOMexception"
        report_name = model.canonical_interaction_name(report_name) or report_name
        self._send_mom_report(
            federation,
            report_name,
            {
                "HLAfederate": federate or self.state.handle or "",
                "HLAservice": interaction_name,
                "HLAexception": exception_name,
                "HLAparameterError": parameter_error,
            },
        )

    def _mom_parameter_failure(
        self,
        federation: FederationState,
        interaction_name: str,
        exception: RTIexception,
        parameter_error: str,
        *,
        mom_exception_name: str | None = None,
    ) -> dict[str, bytes]:
        self._send_mom_exception(
            federation,
            interaction_name,
            mom_exception_name or exception.__class__.__name__,
            parameter_error,
        )
        if self.config.strict_mom_parameter_decoding:
            raise exception
        return {}

    def _mom_bool_payload_is_valid(self, value: bytes) -> bool:
        data = bytes(value)
        if len(data) == 1:
            return data in {b"\x00", b"\x01"}
        text = ""
        try:
            text = hla_mom.decode_text(data).strip().lower()
        except Exception:
            try:
                text = data.decode("utf-8").strip().lower()
            except Exception:
                return False
        return text in {"0", "1", "true", "false", "t", "f", "yes", "no", "y", "n", "enabled", "disabled", "enable", "disable"}

    def _mom_parameter_payload_issue(
        self,
        federation: FederationState,
        rule: mom_table.MOMInteractionRule,
        name: str,
        value: bytes,
    ) -> str | None:
        """Return a validation issue string for a strict MOM parameter value.

        The active MIM/FOM catalog supplies the datatype where available.  Small
        name-based fallbacks cover generated development MIMs and vendor FOMs
        that omit a datatype for MOM extension parameters.
        """

        data_type = (rule.parameter_datatypes.get(name, "") or "").lower()
        lower_name = name.lower()
        if data_type in {"hlaswitch", "hlaboolean"} or lower_name in {"hlareportingstate", "hlasuccessindicator", "hlaactive", "hlaautoprovide"} or lower_name.startswith("hlaconvey"):
            return None if self._mom_bool_payload_is_valid(value) else "InvalidMOMParameterEncoding"
        if name in mom_table.MOM_FLOAT_PARAMETERS or data_type in {"hlafloat64be", "hlafloat64le", "hlafloat32be", "hlafloat32le"}:
            try:
                float(self._decode_mom_text(value, ""))
                return None
            except Exception:
                return "InvalidMOMParameterEncoding"
        if name in mom_table.MOM_HANDLE_PARAMETERS or data_type == "hlahandle":
            handle_types = {
                "HLAfederate": FederateHandle,
                "HLAobjectClass": ObjectClassHandle,
                "HLAobjectClassName": ObjectClassHandle,
                "HLAinteractionClass": InteractionClassHandle,
                "HLAinteractionClassName": InteractionClassHandle,
                "HLAobjectInstance": ObjectInstanceHandle,
                "HLAtransportation": TransportationTypeHandle,
                "HLAtransportationType": TransportationTypeHandle,
            }
            handle_type = handle_types.get(name, FederateHandle)
            try:
                handle = self._decode_mom_handle(value, handle_type, name)
            except Exception:
                return "InvalidMOMParameterEncoding"
            if name == "HLAfederate" and handle not in federation.federates:
                return "FederateHandleNotKnown"
            return None
        if name in mom_table.MOM_HANDLE_SET_PARAMETERS or data_type == "hlahandlelist":
            handle_set_types = {
                "HLAattributeList": AttributeHandle,
                "HLAattribute": AttributeHandle,
                "HLAfederateList": FederateHandle,
                "HLAdimensionHandleSet": DimensionHandle,
            }
            handle_type = handle_set_types.get(name, FederateHandle)
            try:
                values = self._decode_mom_handle_set(value, handle_type, name)
            except Exception:
                return "InvalidMOMParameterEncoding"
            if handle_type is FederateHandle and any(item not in federation.federates for item in values):
                return "FederateHandleNotKnown"
            return None
        if lower_name in {"hlatimestamp", "hlatimeadvancingtime", "hlatimegrantedtime"}:
            return None if self._decode_mom_time(value) is not None else "InvalidMOMParameterEncoding"
        if lower_name == "hlalookahead":
            return None if self._decode_mom_interval(value) is not None else "InvalidMOMParameterEncoding"
        if data_type in {"hlacount", "hlainteger32be", "hlainteger32le"} or lower_name.endswith("count") or lower_name in {"hlanumberofclasses", "hlaserialnumber"}:
            try:
                hla_mom.decode_count(value)
                return None
            except Exception:
                try:
                    int(self._decode_mom_text(value, ""))
                    return None
                except Exception:
                    return "InvalidMOMParameterEncoding"
        # Text, opaque, handle-list and extension payloads are accepted here.
        return None

    def _validate_mom_parameter_payloads(
        self,
        federation: FederationState,
        rule: mom_table.MOMInteractionRule | None,
        params: Mapping[str, bytes],
    ) -> tuple[mom_table.MOMValidationIssue, ...]:
        if rule is None:
            return ()
        issues: list[mom_table.MOMValidationIssue] = []
        for name, value in params.items():
            if name not in rule.allowed_parameters:
                continue
            kind = self._mom_parameter_payload_issue(federation, rule, name, bytes(value))
            if kind:
                issues.append(mom_table.MOMValidationIssue(kind, rule.name, name))
        return tuple(issues)

    def _mom_params_by_name(self, interaction_name: str, parameters: Mapping[ParameterHandle, bytes]) -> dict[str, bytes]:
        federation = self._require_joined()
        model = self._mom_exposure_model(federation)
        canonical_interaction = model.canonical_interaction_name(interaction_name) or interaction_name
        definition = self.engine.get_or_create_interaction_class(canonical_interaction)
        rule = self._mom_interaction_rule(federation, canonical_interaction)
        params: dict[str, bytes] = {}
        for handle, value in dict(parameters).items():
            try:
                raw_name = definition.parameter_names[handle]
            except KeyError:
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InvalidParameterHandle(f"Parameter handle {handle!r} is not defined for {canonical_interaction}"),
                    repr(handle),
                    mom_exception_name="InvalidMOMParameterHandle",
                )
            name = mom_table.canonical_parameter_name(rule, raw_name)
            if rule is not None and name not in rule.allowed_parameters:
                if self.config.strict_mom_parameter_decoding:
                    return self._mom_parameter_failure(
                        federation,
                        canonical_interaction,
                        InteractionParameterNotDefined(f"Parameter {raw_name!r} is not allowed for {canonical_interaction}"),
                        raw_name,
                        mom_exception_name="UnexpectedMOMParameter",
                    )
                name = raw_name
            if name in params:
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InteractionParameterNotDefined(f"Duplicate MOM parameter {name!r} for {canonical_interaction}"),
                    name,
                    mom_exception_name="DuplicateMOMParameter",
                )
            params[name] = bytes(value)

        if rule is not None and self.config.strict_mom_parameter_decoding:
            for issue in model.validate_incoming_parameters(canonical_interaction, params, strict=True):
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InteractionParameterNotDefined(issue.detail or issue.kind),
                    issue.parameter_name,
                    mom_exception_name=issue.kind,
                )
            for issue in self._validate_mom_parameter_payloads(federation, rule, params):
                exc = FederateHandleNotKnown(issue.parameter_name) if issue.kind == "FederateHandleNotKnown" else InteractionParameterNotDefined(issue.kind)
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    exc,
                    issue.parameter_name,
                    mom_exception_name=issue.kind,
                )
        return params

    def _decode_mom_text(self, value: bytes | None, default: str = "") -> str:
        if value is None:
            return default
        try:
            return hla_mom.decode_text(value)
        except Exception:
            try:
                return bytes(value).decode("utf-8")
            except Exception:
                return default

    def _decode_mom_bool(self, value: bytes | None, default: bool = True) -> bool:
        if value is None:
            return default
        try:
            return hla_mom.decode_bool(value)
        except Exception:
            text = self._decode_mom_text(value, "").strip().lower()
            if text in {"1", "true", "t", "yes", "y", "enabled", "enable"}:
                return True
            if text in {"0", "false", "f", "no", "n", "disabled", "disable"}:
                return False
            return default

    def _decode_mom_float(self, value: bytes | None, default: float | None = None) -> float | None:
        if value is None:
            return default
        try:
            return float(self._decode_mom_text(value, ""))
        except Exception:
            try:
                return float(int.from_bytes(value[-4:], "big", signed=True))
            except Exception:
                return default

    def _decode_mom_time(self, value: bytes | None) -> Any:
        if value is None:
            return None
        federation = self._require_joined()
        data = bytes(value)
        try:
            return federation.time_factory.decode_time(data)
        except Exception:
            text = self._decode_mom_text(data, "")
            try:
                return federation.time_factory.make_time(float(text))
            except Exception:
                return None

    def _decode_mom_interval(self, value: bytes | None) -> Any:
        if value is None:
            return None
        federation = self._require_joined()
        data = bytes(value)
        try:
            return federation.time_factory.decode_interval(data)
        except Exception:
            text = self._decode_mom_text(data, "")
            try:
                return federation.time_factory.make_interval(float(text))
            except Exception:
                return None

    def _decode_mom_federate_handle(self, value: bytes | None) -> FederateHandle | None:
        if value is None:
            return None
        data = bytes(value)
        try:
            return FederateHandle.decode(data)
        except Exception:
            text = self._decode_mom_text(data, "").strip()
            if text:
                try:
                    return FederateHandle(int(text))
                except Exception:
                    return None
        return None

    def _decode_mom_handle(self, value: bytes | None, handle_type: type[Any], parameter_name: str) -> Any:
        if value is None:
            raise InteractionParameterNotDefined(f"Missing required MOM parameter {parameter_name}")
        data = bytes(value)
        try:
            return handle_type.decode(data)
        except Exception:
            text = self._decode_mom_text(data, "").strip()
            if text:
                try:
                    return handle_type(int(text))
                except Exception as exc:
                    raise InteractionParameterNotDefined(f"Could not decode {parameter_name} as {handle_type.__name__}: {text!r}") from exc
        raise InteractionParameterNotDefined(f"Could not decode {parameter_name} as {handle_type.__name__}")

    def _decode_mom_object_class_handle(self, value: bytes | None) -> ObjectClassHandle:
        return self._decode_mom_handle(value, ObjectClassHandle, "HLAobjectClass")

    def _decode_mom_interaction_class_handle(self, value: bytes | None) -> InteractionClassHandle:
        return self._decode_mom_handle(value, InteractionClassHandle, "HLAinteractionClass")

    def _decode_mom_object_instance_handle(self, value: bytes | None) -> ObjectInstanceHandle:
        return self._decode_mom_handle(value, ObjectInstanceHandle, "HLAobjectInstance")

    def _decode_mom_transportation_handle(self, value: bytes | None) -> TransportationTypeHandle:
        if value is None:
            return self.engine.transportation_reliable
        try:
            return self._decode_mom_handle(value, TransportationTypeHandle, "HLAtransportation")
        except InteractionParameterNotDefined:
            text = self._decode_mom_text(value, "").strip().lower()
            if text in {"", "hlareliable", "reliable"}:
                return self.engine.transportation_reliable
            raise

    def _decode_mom_handle_set(self, value: bytes | None, handle_type: type[Any], parameter_name: str) -> set[Any]:
        if value is None:
            raise InteractionParameterNotDefined(f"Missing required MOM parameter {parameter_name}")
        data = bytes(value)
        if data and len(data) % 8 == 0 and any(b < 32 or b > 126 for b in data):
            try:
                return {handle_type.decode(data[offset : offset + 8]) for offset in range(0, len(data), 8)}
            except Exception:
                pass
        text = self._decode_mom_text(data, "")
        if not text:
            try:
                text = data.decode("utf-8")
            except Exception:
                text = ""
        tokens = [token.strip() for token in text.replace("[", "").replace("]", "").replace(";", ",").split(",") if token.strip()]
        result: set[Any] = set()
        for token in tokens:
            if token.startswith(f"{handle_type.__name__}(") and token.endswith(")"):
                token = token[token.find("(") + 1 : -1]
            if "value=" in token:
                token = token.split("value=", 1)[1].strip(" )")
            try:
                result.add(handle_type(int(token)))
            except Exception as exc:
                raise InteractionParameterNotDefined(f"Could not decode {parameter_name} element {token!r} as {handle_type.__name__}") from exc
        return result

    def _decode_mom_attribute_set(self, value: bytes | None) -> set[AttributeHandle]:
        return self._decode_mom_handle_set(value, AttributeHandle, "HLAattributeList")

    def _decode_mom_order_type(self, value: bytes | None, default: OrderType = OrderType.RECEIVE) -> OrderType:
        if value is None:
            return default
        text = self._decode_mom_text(value, "").strip().upper()
        if "TIMESTAMP" in text or text.endswith("TSO"):
            return OrderType.TIMESTAMP
        if "RECEIVE" in text or text.endswith("RO"):
            return OrderType.RECEIVE
        return default

    def _decode_mom_resign_action(self, value: bytes | None, default: ResignAction = ResignAction.NO_ACTION) -> ResignAction:
        if value is None:
            return default
        text = self._decode_mom_text(value, "").strip().upper()
        for action in ResignAction:
            if text in {action.name.upper(), str(action.value).upper(), str(action).upper()}:
                return action
        return default

    def _target_federate_from_mom_params(self, federation: FederationState, params: Mapping[str, bytes]) -> FederateState:
        target_handle = self._decode_mom_federate_handle(params.get("HLAfederate"))
        if target_handle is None:
            return self.state
        try:
            return federation.federates[target_handle]
        except KeyError as exc:
            raise FederateHandleNotKnown(repr(target_handle)) from exc

    def _run_mom_service_action(self, interaction_name: str, params: Mapping[str, bytes]) -> None:
        federation = self._require_joined()
        target = self._target_federate_from_mom_params(federation, params)
        old_state = self.state
        self.state = target
        try:
            leaf = interaction_name.rsplit(".", 1)[-1]
            if leaf == "HLAresignFederationExecution":
                self._svc_resignFederationExecution(self._decode_mom_resign_action(params.get("HLAresignAction")))
            elif leaf == "HLAsynchronizationPointAchieved":
                label = self._decode_mom_text(params.get("HLAlabel"), "")
                self._svc_synchronizationPointAchieved(label, self._decode_mom_bool(params.get("HLAsuccessIndicator"), True))
            elif leaf == "HLAfederateSaveBegun":
                self._svc_federateSaveBegun()
            elif leaf == "HLAfederateSaveComplete":
                self._svc_federateSaveComplete() if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True) else self._svc_federateSaveNotComplete()
            elif leaf == "HLAfederateRestoreComplete":
                self._svc_federateRestoreComplete() if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True) else self._svc_federateRestoreNotComplete()
            elif leaf == "HLApublishObjectClassAttributes":
                self._svc_publishObjectClassAttributes(self._decode_mom_object_class_handle(params.get("HLAobjectClass")), self._decode_mom_attribute_set(params.get("HLAattributeList")))
            elif leaf == "HLAunpublishObjectClassAttributes":
                self._svc_unpublishObjectClassAttributes(self._decode_mom_object_class_handle(params.get("HLAobjectClass")), self._decode_mom_attribute_set(params.get("HLAattributeList")))
            elif leaf == "HLApublishInteractionClass":
                self._svc_publishInteractionClass(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")))
            elif leaf == "HLAunpublishInteractionClass":
                self._svc_unpublishInteractionClass(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")))
            elif leaf == "HLAsubscribeObjectClassAttributes":
                service = self._svc_subscribeObjectClassAttributes if self._decode_mom_bool(params.get("HLAactive"), True) else self._svc_subscribeObjectClassAttributesPassively
                service(self._decode_mom_object_class_handle(params.get("HLAobjectClass")), self._decode_mom_attribute_set(params.get("HLAattributeList")))
            elif leaf == "HLAunsubscribeObjectClassAttributes":
                self._svc_unsubscribeObjectClassAttributes(self._decode_mom_object_class_handle(params.get("HLAobjectClass")), self._decode_mom_attribute_set(params.get("HLAattributeList")))
            elif leaf == "HLAsubscribeInteractionClass":
                service = self._svc_subscribeInteractionClass if self._decode_mom_bool(params.get("HLAactive"), True) else self._svc_subscribeInteractionClassPassively
                service(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")))
            elif leaf == "HLAunsubscribeInteractionClass":
                self._svc_unsubscribeInteractionClass(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")))
            elif leaf == "HLAdeleteObjectInstance":
                obj = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
                tag = bytes(params.get("HLAtag", b"MOM"))
                timestamp = self._decode_mom_time(params.get("HLAtimeStamp"))
                self._svc_deleteObjectInstance(obj, tag, timestamp) if timestamp is not None else self._svc_deleteObjectInstance(obj, tag)
            elif leaf == "HLAlocalDeleteObjectInstance":
                self._svc_localDeleteObjectInstance(self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")))
            elif leaf == "HLArequestAttributeTransportationTypeChange":
                self._svc_requestAttributeTransportationTypeChange(self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")), self._decode_mom_attribute_set(params.get("HLAattributeList")), self._decode_mom_transportation_handle(params.get("HLAtransportation")))
            elif leaf == "HLArequestInteractionTransportationTypeChange":
                self._svc_requestInteractionTransportationTypeChange(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")), self._decode_mom_transportation_handle(params.get("HLAtransportation")))
            elif leaf == "HLAunconditionalAttributeOwnershipDivestiture":
                self._svc_unconditionalAttributeOwnershipDivestiture(self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")), self._decode_mom_attribute_set(params.get("HLAattributeList")))
            elif leaf == "HLAenableTimeRegulation":
                lookahead = self._decode_mom_interval(params.get("HLAlookahead")) or federation.time_factory.make_zero()
                self._svc_enableTimeRegulation(lookahead)
            elif leaf == "HLAdisableTimeRegulation":
                self._svc_disableTimeRegulation()
            elif leaf == "HLAenableTimeConstrained":
                self._svc_enableTimeConstrained()
            elif leaf == "HLAdisableTimeConstrained":
                self._svc_disableTimeConstrained()
            elif leaf == "HLAtimeAdvanceRequest":
                self._svc_timeAdvanceRequest(self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time)
            elif leaf == "HLAtimeAdvanceRequestAvailable":
                self._svc_timeAdvanceRequestAvailable(self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time)
            elif leaf == "HLAnextMessageRequest":
                self._svc_nextMessageRequest(self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time)
            elif leaf == "HLAnextMessageRequestAvailable":
                self._svc_nextMessageRequestAvailable(self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time)
            elif leaf == "HLAflushQueueRequest":
                self._svc_flushQueueRequest(self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time)
            elif leaf == "HLAenableAsynchronousDelivery":
                self._svc_enableAsynchronousDelivery()
            elif leaf == "HLAdisableAsynchronousDelivery":
                self._svc_disableAsynchronousDelivery()
            elif leaf == "HLAmodifyLookahead":
                lookahead = self._decode_mom_interval(params.get("HLAlookahead")) or target.lookahead
                self._svc_modifyLookahead(lookahead)
            elif leaf == "HLAchangeAttributeOrderType":
                self._svc_changeAttributeOrderType(self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")), self._decode_mom_attribute_set(params.get("HLAattributeList")), self._decode_mom_order_type(params.get("HLAsendOrder")))
            elif leaf == "HLAchangeInteractionOrderType":
                self._svc_changeInteractionOrderType(self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")), self._decode_mom_order_type(params.get("HLAsendOrder")))
            else:
                raise UnsupportedBackendService(f"Unsupported MOM service action {leaf}")
        finally:
            self.state = old_state

    def _send_mom_report(self, federation: FederationState, report_name: str, values: Mapping[str, Any]) -> None:
        model = self._mom_exposure_model(federation)
        report_name = model.canonical_interaction_name(report_name) or report_name
        report_handle = self.engine.get_or_create_interaction_class(report_name).handle
        rule = self._mom_interaction_rule(federation, report_name)
        normalized_values: dict[str, Any] = {}
        for name, value in values.items():
            normalized_values[mom_table.canonical_parameter_name(rule, str(name))] = value
        expected_names = tuple(rule.parameters) if rule is not None else tuple(normalized_values)
        params: dict[ParameterHandle, bytes] = {}
        for name in expected_names:
            value = normalized_values.get(name, "")
            param = self._mom_parameter_handle(report_name, name)
            if report_name.endswith("HLAreportMOMexception"):
                params[param] = hla_mom.encode_text(value)
            elif isinstance(value, bytes):
                params[param] = value
            elif hasattr(value, "encode") and not isinstance(value, str):
                params[param] = value.encode()
            elif isinstance(value, bool):
                params[param] = hla_mom.encode_bool(value)
            elif isinstance(value, int):
                params[param] = hla_mom.encode_count(value)
            else:
                params[param] = hla_mom.encode_text(value)
        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if report_handle in federate.subscribed_interactions or report_name.endswith("HLAreportMOMexception"):
                self._queue_or_deliver_message(
                    federate,
                    CallbackEvent("receiveInteraction", (
                        report_handle,
                        params,
                        b"MOM",
                        OrderType.RECEIVE,
                        self.engine.transportation_reliable,
                        SupplementalReceiveInfo(producing_federate=None),
                    )),
                    sent_order=OrderType.RECEIVE,
                    timestamp=None,
                    sender=None,
                    service_name=report_name,
                )

    def _service_report_serial(self) -> int:
        return self.engine._next_sequence()

    def _safe_report_arg(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, Mapping):
            return {str(k): self._safe_report_arg(v) for k, v in value.items()}
        if isinstance(value, (set, frozenset, list, tuple)):
            return [self._safe_report_arg(v) for v in value]
        return repr(value)

    def _report_service_invocation(
        self,
        service_name: str,
        *,
        success: bool,
        exception_name: str | None = None,
        args: Sequence[Any] | None = None,
        result: Any = None,
    ) -> None:
        """Emit service-report file records and optional MOM service reports.

        Section anchor: IEEE 1516.1-2010 §11.5.  File reporting is a local
        audit sink. MOM reporting follows the federate switch state and remains
        best-effort/non-throwing so observability never changes service result.
        """

        try:
            serial = self._service_report_serial()
            ref = method_reference(service_name)
            if self.service_report_sink is not None:
                self.service_report_sink.write(
                    ServiceReportRecord(
                        serial_number=serial,
                        service_name=service_name,
                        federate_handle=repr(self.state.handle) if self.state.handle is not None else None,
                        federate_name=self.state.name,
                        success=success,
                        exception_name=exception_name or None,
                        section=ref.section if ref is not None else None,
                        arguments={str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())},
                        returned={"value": self._safe_report_arg(result)} if result is not None else {},
                    )
                )

            self._append_service_report_record(
                service_name,
                success=success,
                exception_name=exception_name or None,
                args=args or (),
                result=result,
                section=ref.section if ref is not None else None,
            )

            federation = self.state.federation
            if (
                not self.config.enable_mom
                or federation is None
                or self.state.handle is None
                or not self.state.service_reporting
            ):
                return
            report_name = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportServiceInvocation"
            self._send_mom_report(
                federation,
                report_name,
                {
                    "HLAfederate": self.state.handle,
                    "HLAservice": service_name,
                    "HLAinitiator": self.state.handle,
                    "HLAsuccessIndicator": success,
                    "HLAsuppliedArguments": json.dumps({str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())}, sort_keys=True),
                    "HLAreturnedArguments": json.dumps({"value": self._safe_report_arg(result)} if result is not None else {}, sort_keys=True),
                    "HLAexception": exception_name or "",
                    "HLAserialNumber": serial,
                },
            )
            if exception_name and self.state.exception_reporting:
                exception_report = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportException"
                self._send_mom_report(
                    federation,
                    exception_report,
                    {
                        "HLAfederate": self.state.handle,
                        "HLAservice": service_name,
                        "HLAexception": exception_name,
                        "HLAserialNumber": serial,
                    },
                )
        except Exception:
            return

    def _mom_request_report_values(self, federation: FederationState, request_name: str, report_name: str, params: Mapping[str, bytes]) -> dict[str, Any]:
        """Build a table-filtered MOM report payload for an HLArequest interaction.

        The active MIM/FOM catalog defines the report parameter names. This
        method computes broad local-process values and leaves final filtering to
        :meth:`_send_mom_report`, so spelling differences such as MIMdata/MIMData
        remain controlled by the merged FDD.
        """

        summary = federation.fom_catalog.as_summary()
        lower_report = report_name.lower()
        target = self._target_federate_from_mom_params(federation, params)
        base: dict[str, Any] = {
            "HLAfederate": target.handle or self.state.handle or "",
            "HLAservice": request_name,
            "HLAsuccessIndicator": True,
        }
        if report_name.endswith("HLAreportFOMmoduleData"):
            base.update(
                {
                    "HLAFOMmoduleIndicator": 0,
                    "HLAFOMmoduleData": hla_mom.encode_opaque(self._all_fom_module_data(federation) or str(summary)),
                }
            )
            return base
        if lower_report.endswith("hlareportmimdata"):
            mim_payload = self._module_xml_or_uri(federation.mim_module)
            base.update({"HLAMIMdata": hla_mom.encode_opaque(mim_payload), "HLAMIMData": hla_mom.encode_opaque(mim_payload)})
            return base
        if report_name.endswith("HLAreportSynchronizationPoints"):
            labels = ",".join(sorted(federation.synchronization_points))
            base.update({"HLAsyncPoints": labels, "HLAsynchronizationPoints": labels})
            return base
        if report_name.endswith("HLAreportSynchronizationPointStatus"):
            status = ";".join(
                f"{label}:{','.join(str(h.value) for h in sorted(point.reported(), key=lambda x: x.value))}"
                for label, point in sorted(federation.synchronization_points.items())
            )
            base.update(
                {
                    "HLAsyncPointName": ",".join(sorted(federation.synchronization_points)),
                    "HLAsyncPointFederates": status,
                    "HLAlabel": ",".join(sorted(federation.synchronization_points)),
                    "HLAfederateSynchronizationStatusList": status,
                }
            )
            return base
        if report_name.endswith("HLAreportObjectClassPublication"):
            base.update(
                {
                    "HLAnumberOfClasses": len(target.published_objects),
                    "HLAobjectClass": str(list(target.published_objects)),
                    "HLAattributeList": str({str(k): list(v) for k, v in target.published_objects.items()}),
                }
            )
            return base
        if report_name.endswith("HLAreportObjectClassSubscription"):
            base.update(
                {
                    "HLAnumberOfClasses": len(target.subscribed_objects),
                    "HLAobjectClass": str(list(target.subscribed_objects)),
                    "HLAactive": True,
                    "HLAmaxUpdateRate": "",
                    "HLAattributeList": str({str(k): list(v) for k, v in target.subscribed_objects.items()}),
                }
            )
            return base
        if report_name.endswith("HLAreportInteractionPublication"):
            base.update({"HLAinteractionClassList": str(list(target.published_interactions)), "HLAnumberOfClasses": len(target.published_interactions)})
            return base
        if report_name.endswith("HLAreportInteractionSubscription"):
            base.update({"HLAinteractionClassList": str(list(target.subscribed_interactions)), "HLAnumberOfClasses": len(target.subscribed_interactions)})
            return base
        if report_name.endswith("HLAreportUpdatesSent"):
            base.update({"HLAtransportation": "", "HLAtransportationType": "", "HLAupdateCounts": target.updates_sent, "HLAupdatesSent": target.updates_sent})
            return base
        if report_name.endswith("HLAreportReflectionsReceived"):
            base.update({"HLAtransportation": "", "HLAtransportationType": "", "HLAreflectCounts": target.reflections_received, "HLAreflectionsReceived": target.reflections_received})
            return base
        if report_name.endswith("HLAreportInteractionsSent"):
            base.update({"HLAtransportation": "", "HLAtransportationType": "", "HLAinteractionCounts": target.interactions_sent, "HLAinteractionsSent": target.interactions_sent})
            return base
        if report_name.endswith("HLAreportInteractionsReceived"):
            base.update({"HLAtransportation": "", "HLAtransportationType": "", "HLAinteractionCounts": target.interactions_received, "HLAinteractionsReceived": target.interactions_received})
            return base
        if report_name.endswith("HLAreportObjectInstancesUpdated"):
            base.update({"HLAobjectInstanceCounts": target.object_instances_updated})
            return base
        if report_name.endswith("HLAreportObjectInstancesReflected"):
            base.update({"HLAobjectInstanceCounts": target.object_instances_reflected})
            return base
        if report_name.endswith("HLAreportObjectInstancesThatCanBeDeleted"):
            deletable = sum(1 for obj in federation.objects.values() if obj.owner == target.handle)
            base.update({"HLAobjectInstanceCounts": deletable})
            return base
        if report_name.endswith("HLAreportObjectInstanceInformation"):
            requested = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")) if params.get("HLAobjectInstance") is not None else None
            objects = [f"{obj.handle.value}:{obj.name}" for obj in federation.objects.values() if requested is None or obj.handle == requested]
            object_text = ";".join(objects)
            base.update({"HLAobjectInstance": object_text, "HLAobjectClass": "", "HLAobjectInstanceName": object_text, "HLAattributeList": ""})
            return base

        rule = self._mom_interaction_rule(federation, report_name)
        if rule is not None:
            for name in rule.parameters:
                base.setdefault(name, "")
        return base

    def _apply_mom_set_service_reporting(
        self,
        federation: FederationState,
        target: FederateState,
        enabled: bool,
        interaction_name: str,
        parameter_name: str = "HLAreportingState",
    ) -> None:
        if enabled and not target.service_reporting and self._is_subscribed_to_service_invocation_report(target):
            self._send_mom_exception(
                federation,
                interaction_name,
                "FederateServiceInvocationsAreBeingReportedViaMOM",
                parameter_name,
                federate=target.handle,
            )
            return
        target.service_reporting = bool(enabled)

    def _handle_mom_interaction(self, interaction_name: str, parameters: Mapping[ParameterHandle, bytes], tag: bytes) -> bool:
        """Process MOM request/adjust/service interactions sent to the RTI.

        The interaction table is derived from the active merged MIM/FOM catalog.
        Strict mode raises the ordinary RTI exception after sending a
        HLAreportMOMexception diagnostic; non-strict mode reports diagnostics but
        retains development-friendly extension behavior.
        Section anchor: IEEE 1516.1-2010 §11.3-§11.5.
        """

        if not (self.config.enable_mom and hla_mom.is_mom_interaction_class_name(interaction_name)):
            return False
        federation = self._require_joined()
        model = self._mom_exposure_model(federation)
        rule = model.interaction_rule(interaction_name)
        if rule is None:
            self._send_mom_exception(federation, interaction_name, "MOMInteractionClassNotDefined", interaction_name)
            if self.config.strict_mom_parameter_decoding:
                raise InteractionClassNotDefined(interaction_name)
            return True
        if rule.rti_direction == "rti-sends":
            self._send_mom_exception(federation, rule.name, "MOMInteractionNotReceivableByRTI", rule.name)
            if self.config.strict_mom_parameter_decoding:
                raise InteractionClassNotPublished(f"MOM report interaction {rule.name!r} is RTI-sent only")
            return True
        if rule.rti_direction == "neither":
            # Clause 11.3.1 says MOM interactions that are neither sent nor
            # received by the RTI are ignored.  Strict mode makes that visible
            # as a diagnostic/exception for conformance testing.
            if self.config.strict_mom_parameter_decoding:
                self._send_mom_exception(federation, rule.name, "MOMInteractionNotReceivableByRTI", rule.name)
                raise InteractionClassNotDefined(f"MOM non-leaf interaction {rule.name!r} is not RTI-receivable")
            return True

        params = self._mom_params_by_name(rule.name, parameters)
        self._refresh_mom_attribute_values(federation)

        if rule.role == "HLArequest":
            report_name = rule.report_name or model.report_for_request(interaction_name) or hla_mom.mom_report_name_for_request(interaction_name)
            if report_name is None:
                self._send_mom_exception(federation, interaction_name, "UnsupportedMOMRequest", interaction_name)
                return True
            self._send_mom_report(federation, report_name, self._mom_request_report_values(federation, interaction_name, report_name, params))
            return True

        if rule.name.endswith(".HLAadjust.HLAsetServiceReporting"):
            target = self._target_federate_from_mom_params(federation, params)
            enabled = self._decode_mom_bool(params.get("HLAreportingState"), target.service_reporting)
            self._apply_mom_set_service_reporting(federation, target, enabled, interaction_name, "HLAreportingState")
            self._refresh_mom_attribute_values(federation)
            return True

        if rule.name.endswith(".HLAadjust.HLAsetExceptionReporting"):
            target = self._target_federate_from_mom_params(federation, params)
            target.exception_reporting = self._decode_mom_bool(params.get("HLAreportingState"), target.exception_reporting)
            self._refresh_mom_attribute_values(federation)
            return True

        if rule.name.endswith(".HLAadjust.HLAsetSwitches"):
            if ".HLAfederate." in rule.name:
                target = self._target_federate_from_mom_params(federation, params)
                if not params and not self.config.strict_mom_parameter_decoding:
                    # Development-friendly shorthand retained outside strict mode.
                    target.convey_region_designator_sets = True
                    target.convey_producing_federate = True
                    # Empty no-argument shorthand is a development convenience
                    # retained for legacy examples; explicit parameterized
                    # service-reporting changes still use the conflict rules.
                    target.service_reporting = True
                    target.exception_reporting = True
                    target.service_reports_to_file = bool(
                        self.config.service_report_directory
                        or self.config.service_report_file
                        or self.config.service_report_file_on_by_default
                    )
                    if target.service_reports_to_file:
                        self._ensure_service_report_file(federation, target)
                else:
                    if "HLAconveyRegionDesignatorSets" in params:
                        target.convey_region_designator_sets = self._decode_mom_bool(params.get("HLAconveyRegionDesignatorSets"), target.convey_region_designator_sets)
                    if "HLAconveyProducingFederate" in params:
                        target.convey_producing_federate = self._decode_mom_bool(params.get("HLAconveyProducingFederate"), target.convey_producing_federate)
                    # Backward-compatible extension names are accepted only when
                    # present in non-strict parameter maps or vendor MIMs.
                    if "HLAserviceReporting" in params:
                        self._apply_mom_set_service_reporting(
                            federation,
                            target,
                            self._decode_mom_bool(params.get("HLAserviceReporting"), target.service_reporting),
                            interaction_name,
                            "HLAserviceReporting",
                        )
                    if "HLAexceptionReporting" in params:
                        target.exception_reporting = self._decode_mom_bool(params.get("HLAexceptionReporting"), target.exception_reporting)
                    if "HLAsendServiceReportsToFile" in params:
                        target.service_reports_to_file = self._decode_mom_bool(params.get("HLAsendServiceReportsToFile"), target.service_reports_to_file)
                    if target.service_reports_to_file:
                        self._ensure_service_report_file(federation, target)
            else:
                if "HLAautoProvide" in params or not params:
                    federation.mom_auto_provide = self._decode_mom_bool(params.get("HLAautoProvide"), federation.mom_auto_provide)
                    federation.auto_provide = federation.mom_auto_provide
            self._refresh_mom_attribute_values(federation)
            return True

        if rule.name.endswith(".HLAadjust.HLAsetTiming"):
            target = self._target_federate_from_mom_params(federation, params)
            target.mom_report_period = self._decode_mom_float(params.get("HLAreportPeriod"), target.mom_report_period)
            self._refresh_mom_attribute_values(federation)
            return True

        if rule.name.endswith(".HLAadjust.HLAmodifyAttributeState"):
            target = self._target_federate_from_mom_params(federation, params)
            obj_name = self._decode_mom_text(params.get("HLAobjectInstance"), "")
            attr_name = self._decode_mom_text(params.get("HLAattribute"), "")
            state = self._decode_mom_text(params.get("HLAattributeState"), "")
            target.mom_attribute_reporting_states[(obj_name, attr_name)] = state
            self._refresh_mom_attribute_values(federation)
            return True

        if rule.role == "HLAservice":
            try:
                self._run_mom_service_action(interaction_name, params)
            except Exception as exc:
                self._send_mom_exception(federation, interaction_name, exc.__class__.__name__, str(exc))
                if self.config.strict_mom_parameter_decoding:
                    raise
            self._refresh_mom_attribute_values(federation)
            return True

        return False

    # Time-management helpers ----------------------------------------------
    def _next_message_sequence(self, federation: FederationState) -> int:
        seq = federation.next_message_sequence
        federation.next_message_sequence += 1
        return seq

    def _time_add(self, time_value: Any, interval: Any) -> Any:
        return tm.time_add(time_value, interval, self._time_factory())

    def _time_lt(self, a: Any, b: Any) -> bool:
        return _time_value(a) < _time_value(b)

    def _time_le(self, a: Any, b: Any) -> bool:
        return _time_value(a) <= _time_value(b)

    def _compute_galt(self, federation: FederationState, federate: FederateState) -> TimeQueryReturn:
        """Compute GALT using the dedicated time-management coordinator.

        Section anchor: IEEE 1516.1-2010 §8.16.  The v0.12 algorithm uses
        per-regulator lower-bound-on-timestamp (LBTS) contributions from current
        or pending logical time plus lookahead.
        """

        return tm.compute_galt(federation, federate, factory=federation.time_factory)

    def _compute_lits(self, federation: FederationState, federate: FederateState) -> TimeQueryReturn:
        """Compute LITS from queued incoming TSO messages and GALT.

        Section anchor: IEEE 1516.1-2010 §8.18.
        """

        return tm.compute_lits(federation, federate, factory=federation.time_factory)

    def _galt_allows_grant(self, federation: FederationState, federate: FederateState, requested_time: Any, kind: str) -> bool:
        if not self.config.enforce_galt or not federate.time_constrained_enabled:
            return True
        request = tm.TimeAdvanceRequestState(kind, requested_time)
        return tm.can_grant_time_request(
            federation, federate, request, enforce_galt=self.config.enforce_galt, factory=federation.time_factory
        )

    def _validate_time_advance_request(self, requested_time: Any) -> Any:
        requested = self._coerce_time(requested_time)
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("A time advance request is already outstanding")
        if self._time_lt(requested, self.state.current_time):
            raise LogicalTimeAlreadyPassed(repr(requested))
        return requested

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None:
        if not args:
            return None
        # HLA timestamp overloads place logical time after the tag.  Ignore
        # supplemental region/order arguments that are not coercible as time.
        for arg in args:
            if arg is None or isinstance(arg, (OrderType, TransportationTypeHandle, SupplementalReceiveInfo, SupplementalReflectInfo, SupplementalRemoveInfo)):
                continue
            try:
                return self._coerce_time(arg)
            except Exception:
                continue
        return None

    def _sent_order_type(self, preferred: OrderType, timestamp: Any | None) -> OrderType:
        if preferred is OrderType.TIMESTAMP and timestamp is not None and self.state.time_regulation_enabled:
            return OrderType.TIMESTAMP
        return OrderType.RECEIVE

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        """Validate timestamped send/delete/update requests.

        Section anchor: IEEE 1516.1-2010 §8.1.4. A time-regulating federate
        may send TSO messages only at or after logical-time-plus-lookahead.
        """

        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Timestamp-order messages require time regulation to be enabled")
        federation = self._require_joined()
        lower_bound = tm.valid_tso_lower_bound(self.state, factory=federation.time_factory)
        if tm.time_lt(timestamp, lower_bound):
            raise InvalidLogicalTime(f"TSO timestamp {timestamp!r} is earlier than logical time/lookahead bound {lower_bound!r}")
        if self.state.zero_lookahead_tarnmr_restriction and getattr(self.state.lookahead, "is_zero", lambda: False)() and tm.time_le(timestamp, self.state.current_time):
            raise InvalidLogicalTime("Zero-lookahead TAR/NMR restriction forbids TSO timestamps <= current logical time")

    def _make_retraction_handle(self, sent_order: OrderType) -> MessageRetractionHandle | None:
        if sent_order is not OrderType.TIMESTAMP:
            return None
        return self.engine._alloc(MessageRetractionHandle)

    def _queue_or_deliver_message(
        self,
        target: FederateState,
        callback: CallbackEvent,
        *,
        sent_order: OrderType,
        timestamp: Any | None,
        sender: FederateHandle | None,
        service_name: str,
        retraction_handle: MessageRetractionHandle | None = None,
    ) -> None:
        federation = target.federation
        if federation is None:
            return
        received_order = OrderType.TIMESTAMP if target.time_constrained_enabled and sent_order is OrderType.TIMESTAMP else OrderType.RECEIVE
        if received_order is OrderType.TIMESTAMP and timestamp is not None:
            msg = QueuedTimeMessage(
                sort_key=(_time_value(timestamp), self._next_message_sequence(federation)),
                timestamp=timestamp,
                sent_order=sent_order,
                received_order=received_order,
                callback=callback,
                retraction_handle=retraction_handle,
                sender=sender,
                service_name=service_name,
            )
            heapq.heappush(target.tso_message_heap, msg)
            if retraction_handle is not None:
                target.retraction_messages[retraction_handle] = msg
            self._attempt_time_advance(target)
            return
        msg = QueuedTimeMessage(
            sort_key=(0, self._next_message_sequence(federation)),
            timestamp=timestamp,
            sent_order=sent_order,
            received_order=OrderType.RECEIVE,
            callback=callback,
            retraction_handle=retraction_handle,
            sender=sender,
            service_name=service_name,
        )
        if target.time_constrained_enabled and not target.asynchronous_delivery_enabled and not target.time_advancing:
            target.ro_message_queue.append(msg)
        else:
            self._deliver_time_message(target, msg)

    def _deliver_time_message(self, target: FederateState, msg: QueuedTimeMessage) -> None:
        if msg.retracted:
            return
        name = msg.callback.method_name
        if name == "reflectAttributeValues":
            target.reflections_received += 1
            target.object_instances_reflected += 1
        elif name == "receiveInteraction":
            target.interactions_received += 1
        elif name == "removeObjectInstance":
            target.object_instances_removed += 1
        elif name == "discoverObjectInstance":
            target.object_instances_discovered += 1
        self._deliver(target, name, *msg.callback.args)

    def _drain_ro_messages(self, federate: FederateState) -> None:
        while federate.ro_message_queue:
            self._deliver_time_message(federate, federate.ro_message_queue.popleft())

    def _take_eligible_tso_messages(self, federate: FederateState, requested: Any, kind: str) -> list[QueuedTimeMessage]:
        if not federate.tso_message_heap:
            return []
        active = [msg for msg in federate.tso_message_heap if not msg.retracted]
        if not active:
            federate.tso_message_heap.clear()
            return []
        if kind == "flushQueueRequest":
            eligible = active
        elif kind in {"nextMessageRequest", "nextMessageRequestAvailable"}:
            below = [msg for msg in active if self._time_le(msg.timestamp, requested)]
            if not below:
                eligible = []
            else:
                first_time = min((msg.timestamp for msg in below), key=_time_value)
                eligible = [msg for msg in below if _time_value(msg.timestamp) == _time_value(first_time)]
        else:
            eligible = [msg for msg in active if self._time_le(msg.timestamp, requested)]
        eligible_ids = {id(msg) for msg in eligible}
        federate.tso_message_heap = [msg for msg in active if id(msg) not in eligible_ids]
        heapq.heapify(federate.tso_message_heap)
        return sorted(eligible, key=lambda m: m.sort_key)

    def _attempt_time_advance(self, federate: FederateState) -> None:
        federation = federate.federation
        if federation is None or not federate.time_advancing or federate.requested_time is None or federate.time_advance_kind is None:
            return
        requested = federate.requested_time
        kind = federate.time_advance_kind
        old_time = federate.current_time
        if not self._galt_allows_grant(federation, federate, requested, kind):
            return
        self._drain_ro_messages(federate)
        delivered = self._take_eligible_tso_messages(federate, requested, kind)
        grant_time = requested
        if delivered and kind in {"nextMessageRequest", "nextMessageRequestAvailable"}:
            earliest = min((msg.timestamp for msg in delivered), key=_time_value)
            if self._time_lt(earliest, requested):
                grant_time = earliest
        for msg in delivered:
            self._deliver_time_message(federate, msg)
        federate.current_time = grant_time
        federate.time_advancing = False
        federate.last_time_advance_kind = kind
        federate.time_advance_kind = None
        federate.requested_time = None
        if kind in {"timeAdvanceRequest", "nextMessageRequest"} and getattr(federate.lookahead, "is_zero", lambda: False)():
            federate.zero_lookahead_tarnmr_restriction = True
        elif self._time_lt(old_time, grant_time):
            federate.zero_lookahead_tarnmr_restriction = False
        self._deliver(federate, "timeAdvanceGrant", grant_time)
        self._refresh_mom_attribute_values(federation)

    def _attempt_all_time_advances(self, federation: FederationState) -> None:
        for federate in list(federation.federates.values()):
            self._attempt_time_advance(federate)

    # Federation management ------------------------------------------------
    def _svc_connect(
        self,
        federateReference: FederateAmbassador,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:
        if self.state.connected:
            raise AlreadyConnected("RTI ambassador is already connected")
        self.state.ambassador = federateReference
        self.state.callback_model = callbackModel
        self.state.local_settings_designator = localSettingsDesignator
        self.state.connected = True

    def _svc_disconnect(self) -> None:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateIsExecutionMember("Resign before disconnecting")
        self.state.connected = False
        self.state.ambassador = None
        self.state.queue.clear()

    def _svc_createFederationExecution(self, federationExecutionName: str, *fomModules: Any) -> None:
        self._require_connected()
        fom_sources, mim_source, time_name = _parse_create_federation_args(
            tuple(fomModules),
            registry=self.engine.time_factories,
            default_time_name=self.config.default_logical_time_implementation_name,
        )
        if str(mim_source) == "HLAstandardMIM":
            raise DesignatorIsHLAstandardMIM("Explicit MIM designator shall not be HLAstandardMIM")
        require_foms = self.config.require_fom_modules or bool(fom_sources)
        resolved_foms = self._resolve_fom_modules(fom_sources, require_non_empty=require_foms)
        resolved_mim = self._resolve_fom_modules((mim_source,), mim=True)[0] if mim_source is not None else standard_mim_module()
        catalog = self._combine_fom_catalog(resolved_foms, mim_module=resolved_mim)
        time_modules = tuple(module for module in ((resolved_mim,) if resolved_mim is not None else ()) + tuple(resolved_foms) if module is not None)
        time_factory = self._choose_time_factory(time_name, time_modules)
        with self.engine._lock:
            if federationExecutionName in self.engine.federations:
                raise FederationExecutionAlreadyExists(str(federationExecutionName))
            self.engine.install_fom_modules([module for module in ((resolved_mim,) if resolved_mim is not None else ()) + tuple(resolved_foms) if module is not None])
            federation = FederationState(
                name=str(federationExecutionName),
                fom_modules=tuple(resolved_foms),
                mim_module=resolved_mim,
                fom_catalog=catalog,
                mom_model=mom_table.build_mom_exposure_model(catalog),
                time_factory=time_factory,
            )
            self.engine.federations[str(federationExecutionName)] = federation
            self._ensure_mom_federation_object(federation)

    def _svc_createFederationExecutionWithMIM(self, federationExecutionName: str, *fomModules: Any) -> None:
        self._svc_createFederationExecution(federationExecutionName, *fomModules)

    def _svc_destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        with self.engine._lock:
            federation = self.engine.federations.get(str(federationExecutionName))
            if federation is None:
                raise FederationExecutionDoesNotExist(str(federationExecutionName))
            if federation.federates:
                raise FederatesCurrentlyJoined(str(federationExecutionName))
            del self.engine.federations[str(federationExecutionName)]

    def _svc_listFederationExecutions(self) -> None:
        self._require_connected()
        infos = {
            FederationExecutionInformation(
                federation.name,
                federation.time_factory.get_name(),
            )
            for federation in self.engine.federations.values()
        }
        self._deliver(self.state, "reportFederationExecutions", infos)

    def _svc_joinFederationExecution(self, *args: Any) -> FederateHandle:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateAlreadyExecutionMember("Already joined")
        federate_name, federate_type, federation_name, additional_fom_sources = _parse_join_args(tuple(args))
        if not federate_name:
            federate_name = f"federate-{self.state.backend_id}"
        with self.engine._lock:
            federation = self.engine.federations.get(str(federation_name))
            if federation is None:
                raise FederationExecutionDoesNotExist(str(federation_name))
            additional_modules = self._resolve_fom_modules(additional_fom_sources)
            new_catalog = federation.fom_catalog
            if additional_modules:
                new_catalog = self._combine_fom_catalog(additional_modules, base_catalog=federation.fom_catalog)
            if any(federate.name == str(federate_name) for federate in federation.federates.values()):
                from ..exceptions import FederateNameAlreadyInUse

                raise FederateNameAlreadyInUse(str(federate_name))
            if additional_modules:
                self.engine.install_fom_modules(additional_modules)
                federation.fom_modules = tuple((*federation.fom_modules, *additional_modules))
                federation.fom_catalog = new_catalog
                federation.mom_model = mom_table.build_mom_exposure_model(new_catalog)
            handle = self.engine._alloc(FederateHandle)
            self.state.handle = handle
            self.state.name = str(federate_name)
            self.state.federate_type = str(federate_type)
            self.state.federation = federation
            self.state.current_time = federation.time_factory.make_initial()
            self.state.lookahead = federation.time_factory.make_zero()
            self.state.service_reports_to_file = bool(self.config.service_report_file_on_by_default)
            if self.state.service_reports_to_file:
                self._ensure_service_report_file(federation, self.state)
            federation.federates[handle] = self.state
            self._ensure_mom_federation_object(federation)
            self._ensure_mom_federate_object(federation, self.state)
            self._refresh_all_mom_objects(federation, notify=True)
            self._announce_open_synchronization_points_to_joiner(federation, handle)
            self._process_time_advances(federation)
            return handle

    def _svc_resignFederationExecution(self, resignAction: ResignAction) -> None:
        federation = self._require_joined()
        action_name = _enum_name(resignAction)
        handle = self.state.handle
        assert handle is not None
        if action_name in {"DELETE_OBJECTS", "DELETE_OBJECTS_THEN_DIVEST", "CANCEL_THEN_DELETE_THEN_DIVEST"}:
            to_remove = [obj for obj in federation.objects.values() if obj.owner == handle]
            for obj in to_remove:
                self._remove_object(obj, b"resign")
        self._remove_federate_from_synchronization_points(federation, handle)
        mom_handle = federation.mom_federate_objects.pop(handle, None)
        if mom_handle is not None:
            mom_instance = federation.objects.pop(mom_handle, None)
            if mom_instance is not None:
                federation.object_names.pop(mom_instance.name, None)
        federation.federates.pop(handle, None)
        self._process_time_advances(federation)
        self._refresh_all_mom_objects(federation, notify=True)
        self.state.handle = None
        self.state.name = None
        self.state.federate_type = None
        self.state.federation = None
        self.state.published_objects.clear()
        self.state.subscribed_objects.clear()
        self.state.published_interactions.clear()
        self.state.subscribed_interactions.clear()

    def _svc_registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: Iterable[FederateHandle] | None = None,
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        label = str(synchronizationPointLabel)
        if label in federation.synchronization_points:
            self._deliver(
                self.state,
                "synchronizationPointRegistrationFailed",
                label,
                SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
            )
            return
        assert self.state.handle is not None
        open_to_late_joiners = synchronizationSet is None
        if synchronizationSet is None:
            targets = set(federation.federates)
        else:
            targets = set(synchronizationSet)
            if not targets:
                targets = set(federation.federates)
                open_to_late_joiners = True
            elif not targets.issubset(set(federation.federates)):
                self._deliver(
                    self.state,
                    "synchronizationPointRegistrationFailed",
                    label,
                    SynchronizationPointFailureReason.SYNCHRONIZATION_SET_MEMBER_NOT_JOINED,
                )
                return
        point = SynchronizationPointState(
            label=label,
            tag=bytes(userSuppliedTag),
            registering_federate=self.state.handle,
            targets=set(targets),
            open_to_late_joiners=open_to_late_joiners,
        )
        federation.synchronization_points[label] = point
        self._deliver(self.state, "synchronizationPointRegistrationSucceeded", label)
        for handle in sorted(targets, key=lambda h: h.value):
            self._announce_synchronization_point(federation, point, handle)

    def _svc_synchronizationPointAchieved(self, synchronizationPointLabel: str, successIndicator: bool = True) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        label = str(synchronizationPointLabel)
        point = federation.synchronization_points.get(label)
        if point is None:
            from ..exceptions import SynchronizationPointLabelNotAnnounced

            raise SynchronizationPointLabelNotAnnounced(label)
        assert self.state.handle is not None
        if self.state.handle not in point.announced:
            from ..exceptions import SynchronizationPointLabelNotAnnounced

            raise SynchronizationPointLabelNotAnnounced(label)
        if successIndicator:
            point.achieved.add(self.state.handle)
            point.failed.discard(self.state.handle)
        else:
            point.failed.add(self.state.handle)
            point.achieved.discard(self.state.handle)
        self._complete_synchronization_point_if_ready(federation, point)

    def _snapshot_time_state(self, federation: FederationState) -> dict[FederateHandle, dict[str, Any]]:
        """Capture the time-state portion of a federation save snapshot.

        Section anchors: IEEE 1516.1-2010 §4.16-§4.26 and §8.8-§8.13.
        """

        return {
            handle: {
                "current_time": federate.current_time,
                "lookahead": federate.lookahead,
                "time_regulation_enabled": federate.time_regulation_enabled,
                "time_constrained_enabled": federate.time_constrained_enabled,
                "asynchronous_delivery_enabled": federate.asynchronous_delivery_enabled,
                "zero_lookahead_tarnmr_restriction": federate.zero_lookahead_tarnmr_restriction,
            }
            for handle, federate in federation.federates.items()
        }

    def _restore_time_state(self, federation: FederationState, label: str) -> None:
        snapshot = federation.saved_time_states.get(label, {})
        for handle, values in snapshot.items():
            federate = federation.federates.get(handle)
            if federate is None:
                continue
            federate.current_time = values.get("current_time", federate.current_time)
            federate.lookahead = values.get("lookahead", federate.lookahead)
            federate.time_regulation_enabled = bool(values.get("time_regulation_enabled", federate.time_regulation_enabled))
            federate.time_constrained_enabled = bool(values.get("time_constrained_enabled", federate.time_constrained_enabled))
            federate.asynchronous_delivery_enabled = bool(values.get("asynchronous_delivery_enabled", federate.asynchronous_delivery_enabled))
            federate.zero_lookahead_tarnmr_restriction = bool(values.get("zero_lookahead_tarnmr_restriction", False))
            federate.time_advancing = False
            federate.pending_time_advance = None
            federate.requested_time = None
            federate.time_advance_kind = None
            federate.ro_message_queue.clear()
            federate.tso_message_heap.clear()
        federation.tso_messages.clear()

    def _start_federation_save(self, federation: FederationState, label: str, theTime: Any | None = None) -> None:
        federation.save_label = str(label)
        federation.save_status = {
            handle: SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE for handle in federation.federates
        }
        federation.next_save_name = None
        federation.next_save_time = None
        federation.scheduled_save_requested_by = None
        for federate in list(federation.federates.values()):
            if theTime is None:
                self._deliver(federate, "initiateFederateSave", str(label))
            else:
                self._deliver(federate, "initiateFederateSave", str(label), self._coerce_time(theTime))
        self._refresh_all_mom_objects(federation, notify=True)

    def _process_scheduled_saves(self, federation: FederationState) -> None:
        """Start a scheduled save when §4.19 time eligibility is satisfied.

        A time-constrained federate is eligible after all queued TSO messages at
        or below the save timestamp have been delivered and its current/pending
        grant boundary reaches the scheduled save point.  Non-time-constrained
        federates are instructed after the time-constrained set is eligible.
        """

        if federation.next_save_name is None or federation.next_save_time is None or federation.save_label is not None:
            return
        save_time = federation.next_save_time

        def no_blocking_tso(fed: FederateState) -> bool:
            return not any(tm.time_le(getattr(msg, "timestamp"), save_time) for msg in tm.queued_tso_messages(federation, fed))

        for fed in list(federation.federates.values()):
            if fed.time_constrained_enabled:
                if not no_blocking_tso(fed):
                    return
                next_grant = None
                request = fed.pending_time_advance
                if request is not None:
                    decision = tm.compute_grant_decision(
                        federation,
                        fed,
                        request,
                        enforce_galt=self.config.enforce_galt,
                        nrg_enabled=self.config.non_regulated_grant_enabled,
                        factory=federation.time_factory,
                    )
                    next_grant = decision.grant_time if decision.can_grant else getattr(request, "requested_time", None)
                if not tm.scheduled_save_time_reached(fed, save_time, next_grant_time=next_grant):
                    return

        self._start_federation_save(federation, federation.next_save_name, save_time)

    def _svc_requestFederationSave(self, label: str, theTime: Any | None = None) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if theTime is not None:
            save_time = self._coerce_time(theTime)
            if _time_lt(save_time, self.state.current_time):
                raise LogicalTimeAlreadyPassed(repr(theTime))
            federation.next_save_name = str(label)
            federation.next_save_time = save_time
            federation.scheduled_save_requested_by = self.state.handle
            self._process_scheduled_saves(federation)
            self._refresh_all_mom_objects(federation, notify=True)
            return
        self._start_federation_save(federation, str(label), None)

    def _svc_federateSaveBegun(self) -> None:
        federation = self._require_joined()
        if federation.save_label is None:
            from ..exceptions import SaveNotInitiated
            raise SaveNotInitiated("No federation save is in progress")
        assert self.state.handle is not None
        federation.save_status[self.state.handle] = SaveStatus.FEDERATE_SAVING
        self._refresh_mom_federate_object(federation, self.state, notify=True)

    def _svc_federateSaveComplete(self) -> None:
        self._complete_save(success=True)

    def _svc_federateSaveNotComplete(self) -> None:
        self._complete_save(success=False)

    def _complete_save(self, *, success: bool) -> None:
        federation = self._require_joined()
        if federation.save_label is None:
            from ..exceptions import SaveNotInitiated
            raise SaveNotInitiated("No federation save is in progress")
        assert self.state.handle is not None
        federation.save_status[self.state.handle] = SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
        if not success:
            for federate in list(federation.federates.values()):
                self._deliver(federate, "federationNotSaved", SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE)
            federation.save_label = None
            federation.save_status.clear()
            self._refresh_all_mom_objects(federation, notify=True)
            return
        if federation.save_status and all(status is SaveStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE for status in federation.save_status.values()):
            label = federation.save_label
            assert label is not None
            federation.last_save_name = label
            federation.last_save_time = federation.next_save_time
            federation.saved_time_states[label] = self._snapshot_time_state(federation)
            federation.saved_object_snapshots[label] = copy.deepcopy(federation.objects)
            for federate in list(federation.federates.values()):
                self._deliver(federate, "federationSaved")
            federation.save_label = None
            federation.save_status.clear()
            self._refresh_all_mom_objects(federation, notify=True)

    def _svc_abortFederationSave(self) -> None:
        federation = self._require_joined()
        for federate in list(federation.federates.values()):
            self._deliver(federate, "federationNotSaved", SaveFailureReason.SAVE_ABORTED)
        federation.save_label = None
        federation.save_status.clear()
        federation.next_save_name = None
        federation.next_save_time = None
        federation.scheduled_save_requested_by = None
        self._refresh_all_mom_objects(federation, notify=True)

    def _svc_queryFederationSaveStatus(self) -> None:
        federation = self._require_joined()
        response = [
            FederateHandleSaveStatusPair(handle, federation.save_status.get(handle, SaveStatus.NO_SAVE_IN_PROGRESS))
            for handle in federation.federates
        ]
        self._deliver(self.state, "federationSaveStatusResponse", response)

    def _svc_requestFederationRestore(self, label: str) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        federation.restore_label = str(label)
        federation.restore_status = {
            handle: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING for handle in federation.federates
        }
        self._deliver(self.state, "requestFederationRestoreSucceeded", str(label))
        for federate in list(federation.federates.values()):
            federate.time_advancing = False
            federate.pending_time_advance = None
            federate.requested_time = None
            federate.time_advance_kind = None
            self._deliver(federate, "federationRestoreBegun")
            self._deliver(federate, "initiateFederateRestore", str(label), federate.name or "", federate.handle)
        self._refresh_all_mom_objects(federation, notify=True)

    def _svc_federateRestoreComplete(self) -> None:
        self._complete_restore(success=True)

    def _svc_federateRestoreNotComplete(self) -> None:
        self._complete_restore(success=False)

    def _complete_restore(self, *, success: bool) -> None:
        federation = self._require_joined()
        if federation.restore_label is None:
            from ..exceptions import RestoreNotRequested
            raise RestoreNotRequested("No federation restore is in progress")
        assert self.state.handle is not None
        federation.restore_status[self.state.handle] = RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
        if not success:
            for federate in list(federation.federates.values()):
                self._deliver(federate, "federationNotRestored", RestoreFailureReason.FEDERATE_REPORTED_FAILURE_DURING_RESTORE)
            federation.restore_label = None
            federation.restore_status.clear()
            self._refresh_all_mom_objects(federation, notify=True)
            return
        if federation.restore_status and all(status is RestoreStatus.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE for status in federation.restore_status.values()):
            label = federation.restore_label
            assert label is not None
            if label in federation.saved_time_states:
                self._restore_time_state(federation, label)
                snapshot = federation.saved_object_snapshots.get(label)
                if snapshot is not None:
                    federation.objects = copy.deepcopy(snapshot)
                    federation.object_names = {obj.name: handle for handle, obj in federation.objects.items()}
            for federate in list(federation.federates.values()):
                self._deliver(federate, "federationRestored")
            federation.restore_label = None
            federation.restore_status.clear()
            self._refresh_all_mom_objects(federation, notify=True)

    def _svc_abortFederationRestore(self) -> None:
        federation = self._require_joined()
        for federate in list(federation.federates.values()):
            self._deliver(federate, "federationNotRestored", RestoreFailureReason.RESTORE_ABORTED)
        federation.restore_label = None
        federation.restore_status.clear()

    def _svc_queryFederationRestoreStatus(self) -> None:
        federation = self._require_joined()
        response = [
            FederateRestoreStatus(handle, handle, federation.restore_status.get(handle, RestoreStatus.NO_RESTORE_IN_PROGRESS))
            for handle in federation.federates
        ]
        self._deliver(self.state, "federationRestoreStatusResponse", response)

    # Declaration management -----------------------------------------------
    def _svc_publishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        self._require_joined()
        self.engine.object_class_for_handle(theClass)
        attrs = set(attributeList)
        self.state.published_objects.setdefault(theClass, set()).update(attrs)

    def _svc_unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:
        self._require_joined()
        self.state.published_objects.pop(theClass, None)

    def _svc_unpublishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        self._require_joined()
        attrs = self.state.published_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(set(attributeList))
            if not attrs:
                self.state.published_objects.pop(theClass, None)

    def _svc_subscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        self._require_joined()
        self.engine.object_class_for_handle(theClass)
        attrs = set(attributeList)
        self.state.subscribed_objects.setdefault(theClass, set()).update(attrs)
        self._discover_existing_objects(self.state, theClass)

    def _svc_subscribeObjectClassAttributesPassively(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        # Passive subscription differs in advisory behavior.  For this local RTI
        # it installs the same receive filter without requesting production.
        self._svc_subscribeObjectClassAttributes(theClass, attributeList, *unused)

    def _svc_unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:
        self._require_joined()
        self.state.subscribed_objects.pop(theClass, None)

    def _svc_unsubscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        self._require_joined()
        attrs = self.state.subscribed_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(set(attributeList))
            if not attrs:
                self.state.subscribed_objects.pop(theClass, None)

    def _svc_publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theInteraction)
        self.state.published_interactions.add(theInteraction)

    def _svc_unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        self._require_joined()
        self.state.published_interactions.discard(theInteraction)

    def _is_service_invocation_report_handle(self, handle: InteractionClassHandle) -> bool:
        try:
            name = self.engine.interaction_for_handle(handle).name
        except Exception:
            return False
        return name.endswith(".HLAreport.HLAreportServiceInvocation")

    def _is_subscribed_to_service_invocation_report(self, federate: FederateState) -> bool:
        return any(self._is_service_invocation_report_handle(handle) for handle in federate.subscribed_interactions)

    def _svc_subscribeInteractionClass(self, theClass: InteractionClassHandle, *unused: Any) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        if self.state.service_reporting and self._is_service_invocation_report_handle(theClass):
            raise FederateServiceInvocationsAreBeingReportedViaMOM(
                "Disable MOM service reporting before subscribing to HLAreportServiceInvocation"
            )
        self.state.subscribed_interactions.add(theClass)

    def _svc_subscribeInteractionClassPassively(self, theClass: InteractionClassHandle, *unused: Any) -> None:
        self._svc_subscribeInteractionClass(theClass, *unused)

    def _svc_unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        self._require_joined()
        self.state.subscribed_interactions.discard(theClass)

    def _svc_startRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        self._require_joined()
        self.engine.object_class_for_handle(theClass)
        self._deliver(self.state, "startRegistrationForObjectClass", theClass)

    def _svc_stopRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        self._require_joined()
        self.engine.object_class_for_handle(theClass)
        self._deliver(self.state, "stopRegistrationForObjectClass", theClass)

    def _svc_turnInteractionsOn(self, theHandle: InteractionClassHandle) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theHandle)
        self._deliver(self.state, "turnInteractionsOn", theHandle)

    def _svc_turnInteractionsOff(self, theHandle: InteractionClassHandle) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theHandle)
        self._deliver(self.state, "turnInteractionsOff", theHandle)

    # Object management -----------------------------------------------------
    def _svc_reserveObjectInstanceName(self, theObjectInstanceName: str) -> None:
        federation = self._require_joined()
        name = str(theObjectInstanceName)
        assert self.state.handle is not None
        if name in federation.object_names or name in federation.reserved_object_names:
            self._deliver(self.state, "objectInstanceNameReservationFailed", name)
            return
        federation.reserved_object_names[name] = self.state.handle
        self._deliver(self.state, "objectInstanceNameReservationSucceeded", name)

    def _svc_releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:
        federation = self._require_joined()
        name = str(theObjectInstanceName)
        if federation.reserved_object_names.get(name) == self.state.handle:
            federation.reserved_object_names.pop(name, None)

    def _svc_reserveMultipleObjectInstanceName(self, theObjectInstanceNames: Iterable[str]) -> None:
        federation = self._require_joined()
        names = {str(name) for name in theObjectInstanceNames}
        assert self.state.handle is not None
        if not names or any(name in federation.object_names or name in federation.reserved_object_names for name in names):
            self._deliver(self.state, "multipleObjectInstanceNameReservationFailed", names)
            return
        for name in names:
            federation.reserved_object_names[name] = self.state.handle
        self._deliver(self.state, "multipleObjectInstanceNameReservationSucceeded", names)

    def _svc_releaseMultipleObjectInstanceName(self, theObjectInstanceNames: Iterable[str]) -> None:
        federation = self._require_joined()
        for name in {str(name) for name in theObjectInstanceNames}:
            if federation.reserved_object_names.get(name) == self.state.handle:
                federation.reserved_object_names.pop(name, None)

    def _svc_registerObjectInstance(self, theClass: ObjectClassHandle, theObjectName: str | None = None, *unused: Any) -> ObjectInstanceHandle:
        federation = self._require_joined()
        self.engine.object_class_for_handle(theClass)
        if theObjectName is None:
            theObjectName = f"Object-{self.engine._next_values[ObjectInstanceHandle]}"
        with self.engine._lock:
            if str(theObjectName) in federation.object_names:
                raise ObjectInstanceNameInUse(str(theObjectName))
            reserved_by = federation.reserved_object_names.get(str(theObjectName))
            if reserved_by is not None and reserved_by != self.state.handle:
                raise ObjectInstanceNameInUse(str(theObjectName))
            handle = self.engine._alloc(ObjectInstanceHandle)
            assert self.state.handle is not None
            instance = ObjectInstance(handle=handle, class_handle=theClass, name=str(theObjectName), owner=self.state.handle)
            federation.objects[handle] = instance
            federation.object_names[str(theObjectName)] = handle
            federation.reserved_object_names.pop(str(theObjectName), None)
            for federate in list(federation.federates.values()):
                if any(self._object_matches_subscription(theClass, subscribed) for subscribed in federate.subscribed_objects):
                    self._deliver(
                        federate,
                        "discoverObjectInstance",
                        handle,
                        theClass,
                        str(theObjectName),
                        self.state.handle,
                    )
            return handle

    def _svc_updateAttributeValues(self, theObject: ObjectInstanceHandle, theAttributes: Mapping[AttributeHandle, bytes], userSuppliedTag: bytes, *unused: Any) -> MessageRetractionReturn | None:
        federation, instance = self._find_object(theObject)
        if self.config.strict_object_publication:
            published = self.state.published_objects.get(instance.class_handle, set())
            if not set(theAttributes).issubset(published):
                from ..exceptions import AttributeNotPublished

                raise AttributeNotPublished("Attribute update includes unpublished attributes")

        timestamp = self._extract_timestamp(tuple(unused))
        attrs = {handle: bytes(value) for handle, value in dict(theAttributes).items()}
        preferred_orders = [
            self.state.attribute_order_overrides.get(
                (theObject, handle),
                OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type,
            )
            for handle in attrs
        ]
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled and any(order is OrderType.TIMESTAMP for order in preferred_orders))
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None

        instance.attributes.update(attrs)
        for handle in attrs:
            instance.attribute_owners.setdefault(handle, self.state.handle)
        self.state.updates_sent += 1
        self.state.object_instances_updated += 1

        assert self.state.handle is not None
        update_region_map = {attr: set(regions) for attr, regions in self.state.update_regions.get(theObject, {}).items()}
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            reflected = self._attribute_subscription_intersection(federate, instance.class_handle, attrs, instance, update_region_map)
            if not reflected:
                continue
            sent_regions = frozenset().union(*(instance.update_regions.get(attr, set()) for attr in reflected)) if reflected else frozenset()
            info = SupplementalReflectInfo(producing_federate=self.state.handle, sent_regions=frozenset(sent_regions))
            if sent_tso and federate.time_constrained_enabled:
                assert retraction is not None
                event = CallbackEvent(
                    "reflectAttributeValues",
                    (instance.handle, reflected, bytes(userSuppliedTag), OrderType.TIMESTAMP, self.engine.transportation_reliable, timestamp, OrderType.TIMESTAMP, retraction.handle, info),
                )
                self._queue_or_deliver_tso(federation, federate, timestamp, event, retraction_handle=retraction.handle, producing_federate=self.state.handle)
            else:
                event = CallbackEvent(
                    "reflectAttributeValues",
                    (instance.handle, reflected, bytes(userSuppliedTag), OrderType.RECEIVE, self.engine.transportation_reliable, info),
                )
                self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_requestAttributeValueUpdate(self, target: Any, attributes: Iterable[AttributeHandle], userSuppliedTag: bytes = b"") -> None:
        """Ask object owners to provide fresh values for a set of attributes.

        The HLA API has object-instance and object-class overloads.  This local
        backend implements both enough for smoke simulations: an
        ``ObjectInstanceHandle`` routes the request to that object's owner; an
        ``ObjectClassHandle`` routes the request to owners of all known objects
        of that class.
        """

        federation = self._require_joined()
        attrs = set(attributes)
        tag = bytes(userSuppliedTag)

        def deliver(instance: ObjectInstance) -> None:
            if self._is_mom_object_instance(federation, instance):
                self._deliver_mom_attribute_update(instance, attrs, tag)
                return
            owner = federation.federates.get(instance.owner)
            if owner is not None:
                self._deliver(owner, "provideAttributeValueUpdate", instance.handle, attrs, tag)

        if isinstance(target, ObjectInstanceHandle):
            try:
                deliver(federation.objects[target])
                return
            except KeyError as exc:
                raise ObjectInstanceNotKnown(repr(target)) from exc

        if isinstance(target, ObjectClassHandle):
            self.engine.object_class_for_handle(target)
            for instance in list(federation.objects.values()):
                if self._object_matches_subscription(instance.class_handle, target):
                    deliver(instance)
            return

        raise ObjectInstanceNotKnown(repr(target))

    def _svc_sendInteraction(self, theInteraction: InteractionClassHandle, theParameters: Mapping[ParameterHandle, bytes], userSuppliedTag: bytes, *unused: Any) -> MessageRetractionReturn | None:
        federation = self._require_joined()
        interaction_def = self.engine.interaction_for_handle(theInteraction)
        params = {handle: bytes(value) for handle, value in dict(theParameters).items()}
        if self._handle_mom_interaction(interaction_def.name, params, bytes(userSuppliedTag)):
            return None
        if self.config.strict_interaction_publication and theInteraction not in self.state.published_interactions:
            raise InteractionClassNotPublished(repr(theInteraction))

        timestamp = self._extract_timestamp(tuple(unused))
        preferred = self.state.interaction_order_overrides.get(theInteraction, OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type)
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled and preferred is OrderType.TIMESTAMP)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.interactions_sent += 1

        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if any(self._interaction_matches_subscription(theInteraction, subscribed) for subscribed in federate.subscribed_interactions):
                info = SupplementalReceiveInfo(producing_federate=self.state.handle)
                if sent_tso and federate.time_constrained_enabled:
                    assert retraction is not None
                    event = CallbackEvent(
                        "receiveInteraction",
                        (theInteraction, params, bytes(userSuppliedTag), OrderType.TIMESTAMP, self.engine.transportation_reliable, timestamp, OrderType.TIMESTAMP, retraction.handle, info),
                    )
                    self._queue_or_deliver_tso(federation, federate, timestamp, event, retraction_handle=retraction.handle, producing_federate=self.state.handle)
                else:
                    event = CallbackEvent(
                        "receiveInteraction",
                        (theInteraction, params, bytes(userSuppliedTag), OrderType.RECEIVE, self.engine.transportation_reliable, info),
                    )
                    self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _remove_object(self, instance: ObjectInstance, tag: bytes, *, timestamp: Any | None = None, retraction_handle: MessageRetractionHandle | None = None) -> None:
        federation = self._require_joined()
        federation.objects.pop(instance.handle, None)
        federation.object_names.pop(instance.name, None)
        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if any(self._object_matches_subscription(instance.class_handle, subscribed) for subscribed in federate.subscribed_objects):
                info = SupplementalRemoveInfo(producing_federate=self.state.handle)
                if timestamp is None:
                    event = CallbackEvent("removeObjectInstance", (instance.handle, bytes(tag), OrderType.RECEIVE, info))
                    self._deliver(federate, event.method_name, *event.args)
                else:
                    event = CallbackEvent("removeObjectInstance", (instance.handle, bytes(tag), OrderType.TIMESTAMP, timestamp, OrderType.TIMESTAMP, retraction_handle, info))
                    self._queue_or_deliver_tso(federation, federate, timestamp, event, retraction_handle=retraction_handle, producing_federate=self.state.handle)

    def _svc_deleteObjectInstance(self, theObject: ObjectInstanceHandle, userSuppliedTag: bytes, *unused: Any) -> MessageRetractionReturn | None:
        _, instance = self._find_object(theObject)
        if instance.owner != self.state.handle:
            from ..exceptions import DeletePrivilegeNotHeld

            raise DeletePrivilegeNotHeld(repr(theObject))
        timestamp = self._extract_timestamp(tuple(unused))
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.object_instances_deleted += 1
        self._remove_object(instance, userSuppliedTag, timestamp=(timestamp if sent_tso else None), retraction_handle=(retraction.handle if retraction else None))
        federation = self._require_joined()
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_localDeleteObjectInstance(self, theObject: ObjectInstanceHandle) -> None:
        # This RTI does not maintain per-federate discovery caches yet.  Verify
        # the object is known and accept the local deletion request.
        self._find_object(theObject)

    def _svc_requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        theType: TransportationTypeHandle,
    ) -> None:
        self._find_object(theObject)
        self._deliver(self.state, "confirmAttributeTransportationTypeChange", theObject, set(theAttributes), theType)

    def _svc_queryAttributeTransportationType(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        self._find_object(theObject)
        self._deliver(self.state, "reportAttributeTransportationType", theObject, theAttribute, self.engine.transportation_reliable)

    def _svc_requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        self._deliver(self.state, "confirmInteractionTransportationTypeChange", theClass, theType)

    def _svc_queryInteractionTransportationType(self, theClass: InteractionClassHandle) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        assert self.state.handle is not None
        self._deliver(self.state, "reportInteractionTransportationType", self.state.handle, theClass, self.engine.transportation_reliable)

    # Ownership management ---------------------------------------------------
    def _owned_attributes_or_raise(self, instance: ObjectInstance, attributes: Iterable[AttributeHandle]) -> set[AttributeHandle]:
        attrs = set(attributes)
        for attr in attrs:
            # Validate the attribute against the object's class if it is known in the FOM.
            try:
                self.engine.attribute_name(instance.class_handle, attr)
            except AttributeNotDefined:
                # The in-memory RTI allows dynamic attribute handles for early
                # simulations, but an unknown handle is still not owned.
                if attr not in instance.attribute_owners and attr not in instance.attributes:
                    raise
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner != self.state.handle:
                raise AttributeNotOwned(repr(attr))
        return attrs

    @staticmethod
    def _attribute_candidates(instance: ObjectInstance, attr: AttributeHandle) -> set[FederateHandle]:
        return instance.attribute_candidates.setdefault(attr, set())

    @staticmethod
    def _attribute_has_candidates(instance: ObjectInstance, attr: AttributeHandle) -> bool:
        return bool(instance.attribute_candidates.get(attr))

    @staticmethod
    def _attribute_is_divesting(instance: ObjectInstance, attr: AttributeHandle) -> bool:
        return attr in instance.attribute_divesting

    @staticmethod
    def _attribute_is_available_for_immediate_acquisition(instance: ObjectInstance, attr: AttributeHandle) -> bool:
        owner = instance.attribute_owners.get(attr, instance.owner)
        return owner is None or attr in instance.attribute_divesting

    @staticmethod
    def _pop_first_candidate(instance: ObjectInstance, attr: AttributeHandle) -> FederateHandle:
        candidates = instance.attribute_candidates.get(attr, set())
        if not candidates:
            raise NoAcquisitionPending(repr(attr))
        candidate = min(candidates, key=lambda handle: int(handle.value))
        candidates.remove(candidate)
        if not candidates:
            instance.attribute_candidates.pop(attr, None)
        return candidate

    def _deliver_to_federate_handle(
        self,
        federation: FederationState,
        federate_handle: FederateHandle,
        method_name: str,
        *args: Any,
    ) -> None:
        self._deliver(federation.federates[federate_handle], method_name, *args)

    def _complete_immediate_attribute_transfer(
        self,
        federation: FederationState,
        instance: ObjectInstance,
        attr: AttributeHandle,
        new_owner: FederateHandle,
        *,
        old_owner: FederateHandle | None,
        acquisition_tag: bytes,
        notify_previous_owner: bool,
    ) -> None:
        instance.attribute_owners[attr] = new_owner
        instance.attribute_divesting.discard(attr)
        candidates = instance.attribute_candidates.get(attr)
        if candidates is not None:
            candidates.discard(new_owner)
            if not candidates:
                instance.attribute_candidates.pop(attr, None)
        self._deliver_to_federate_handle(
            federation,
            new_owner,
            "attributeOwnershipAcquisitionNotification",
            instance.handle,
            hla_handles.AttributeHandleSet({attr}),
            bytes(acquisition_tag),
        )
        if notify_previous_owner and old_owner is not None:
            self._deliver_to_federate_handle(
                federation,
                old_owner,
                "requestDivestitureConfirmation",
                instance.handle,
                hla_handles.AttributeHandleSet({attr}),
            )

    def _svc_unconditionalAttributeOwnershipDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle]) -> None:
        federation, instance = self._find_object(theObject)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_has_candidates(instance, attr):
                new_owner = self._pop_first_candidate(instance, attr)
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    new_owner,
                    old_owner=old_owner,
                    acquisition_tag=b"",
                    notify_previous_owner=False,
                )
            else:
                instance.attribute_owners[attr] = None
                instance.attribute_divesting.discard(attr)

    def _svc_negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes,
    ) -> None:
        federation, instance = self._find_object(theObject)
        attrs = self._owned_attributes_or_raise(instance, theAttributes)
        for attr in attrs:
            if self._attribute_is_divesting(instance, attr):
                raise AttributeAlreadyBeingDivested(repr(attr))

        for attr in attrs:
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_has_candidates(instance, attr):
                new_owner = self._pop_first_candidate(instance, attr)
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    new_owner,
                    old_owner=old_owner,
                    acquisition_tag=bytes(userSuppliedTag),
                    notify_previous_owner=True,
                )
                continue

            instance.attribute_divesting.add(attr)
            for federate in list(federation.federates.values()):
                if federate is not self.state:
                    self._deliver(
                        federate,
                        "requestAttributeOwnershipAssumption",
                        theObject,
                        hla_handles.AttributeHandleSet({attr}),
                        bytes(userSuppliedTag),
                    )

    def _svc_confirmDivestiture(self, theObject: ObjectInstanceHandle, confirmedAttributes: Iterable[AttributeHandle], userSuppliedTag: bytes) -> None:
        federation, instance = self._find_object(theObject)
        for attr in self._owned_attributes_or_raise(instance, confirmedAttributes):
            if not self._attribute_is_divesting(instance, attr):
                raise AttributeDivestitureWasNotRequested(repr(attr))
            if not self._attribute_has_candidates(instance, attr):
                raise NoAcquisitionPending(repr(attr))
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            new_owner = self._pop_first_candidate(instance, attr)
            self._complete_immediate_attribute_transfer(
                federation,
                instance,
                attr,
                new_owner,
                old_owner=old_owner,
                acquisition_tag=bytes(userSuppliedTag),
                notify_previous_owner=False,
            )

    def _svc_attributeOwnershipAcquisition(self, theObject: ObjectInstanceHandle, desiredAttributes: Iterable[AttributeHandle], userSuppliedTag: bytes) -> None:
        federation, instance = self._find_object(theObject)
        attrs = set(desiredAttributes)
        assert self.state.handle is not None
        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise FederateOwnsAttributes(repr(attr))

        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_is_available_for_immediate_acquisition(instance, attr):
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    self.state.handle,
                    old_owner=owner,
                    acquisition_tag=bytes(userSuppliedTag),
                    notify_previous_owner=self._attribute_is_divesting(instance, attr),
                )
            else:
                candidates = self._attribute_candidates(instance, attr)
                candidates.discard(self.state.handle)
                candidates.add(self.state.handle)
                if owner is not None:
                    self._deliver_to_federate_handle(
                        federation,
                        owner,
                        "requestAttributeOwnershipRelease",
                        theObject,
                        hla_handles.AttributeHandleSet({attr}),
                        bytes(userSuppliedTag),
                    )

    def _svc_attributeOwnershipAcquisitionIfAvailable(self, theObject: ObjectInstanceHandle, desiredAttributes: Iterable[AttributeHandle]) -> None:
        federation, instance = self._find_object(theObject)
        attrs = set(desiredAttributes)
        unavailable: set[AttributeHandle] = set()
        assert self.state.handle is not None
        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise FederateOwnsAttributes(repr(attr))
            if self.state.handle in instance.attribute_candidates.get(attr, set()):
                raise AttributeAlreadyBeingAcquired(repr(attr))

        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_is_available_for_immediate_acquisition(instance, attr):
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    self.state.handle,
                    old_owner=owner,
                    acquisition_tag=b"",
                    notify_previous_owner=self._attribute_is_divesting(instance, attr),
                )
            else:
                self._attribute_candidates(instance, attr).add(self.state.handle)
                unavailable.add(attr)
        if unavailable:
            self._deliver(self.state, "attributeOwnershipUnavailable", theObject, hla_handles.AttributeHandleSet(unavailable))

    def _svc_attributeOwnershipReleaseDenied(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle]) -> None:
        _, instance = self._find_object(theObject)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            instance.attribute_candidates.pop(attr, None)

    def _svc_attributeOwnershipDivestitureIfWanted(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle]) -> hla_handles.AttributeHandleSet:
        federation, instance = self._find_object(theObject)
        divested = self._owned_attributes_or_raise(instance, theAttributes)
        for attr in divested:
            if not self._attribute_has_candidates(instance, attr):
                raise NoAcquisitionPending(repr(attr))
        for attr in divested:
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            new_owner = self._pop_first_candidate(instance, attr)
            self._complete_immediate_attribute_transfer(
                federation,
                instance,
                attr,
                new_owner,
                old_owner=old_owner,
                acquisition_tag=b"",
                notify_previous_owner=False,
            )
        return hla_handles.AttributeHandleSet(divested)

    def _svc_cancelNegotiatedAttributeOwnershipDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle]) -> None:
        _, instance = self._find_object(theObject)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            if not self._attribute_is_divesting(instance, attr):
                raise AttributeDivestitureWasNotRequested(repr(attr))
            instance.attribute_divesting.discard(attr)

    def _svc_cancelAttributeOwnershipAcquisition(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle]) -> None:
        _, instance = self._find_object(theObject)
        attrs = set(theAttributes)
        assert self.state.handle is not None
        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise AttributeAlreadyOwned(repr(attr))
            if self.state.handle not in instance.attribute_candidates.get(attr, set()):
                raise AttributeAcquisitionWasNotRequested(repr(attr))
        for attr in attrs:
            candidates = instance.attribute_candidates.get(attr)
            if candidates is not None:
                candidates.discard(self.state.handle)
                if not candidates:
                    instance.attribute_candidates.pop(attr, None)
        self._deliver(self.state, "confirmAttributeOwnershipAcquisitionCancellation", theObject, hla_handles.AttributeHandleSet(attrs))

    def _svc_queryAttributeOwnership(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        _, instance = self._find_object(theObject)
        owner = instance.attribute_owners.get(theAttribute, instance.owner)
        if owner is None:
            self._deliver(self.state, "attributeIsNotOwned", theObject, theAttribute)
        else:
            self._deliver(self.state, "informAttributeOwnership", theObject, theAttribute, owner)

    def _svc_isAttributeOwnedByFederate(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> bool:
        _, instance = self._find_object(theObject)
        return instance.attribute_owners.get(theAttribute, instance.owner) == self.state.handle

    # Time management -------------------------------------------------------
    def _svc_enableTimeRegulation(self, theLookahead: Any) -> None:
        federation = self._require_joined()
        if self.state.time_regulation_enabled:
            raise TimeRegulationAlreadyEnabled("Time regulation is already enabled")
        lookahead = self._coerce_interval(theLookahead)
        if _time_value(lookahead) < 0:
            raise InvalidLookahead("Lookahead must be non-negative")
        self.state.lookahead = lookahead
        self.state.time_regulation_enabled = True
        self._deliver(self.state, "timeRegulationEnabled", self.state.current_time)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_disableTimeRegulation(self) -> None:
        federation = self._require_joined()
        self.state.time_regulation_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_enableTimeConstrained(self) -> None:
        federation = self._require_joined()
        if self.state.time_constrained_enabled:
            raise TimeConstrainedAlreadyEnabled("Time constrained is already enabled")
        self.state.time_constrained_enabled = True
        self._deliver(self.state, "timeConstrainedEnabled", self.state.current_time)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_disableTimeConstrained(self) -> None:
        federation = self._require_joined()
        self.state.time_constrained_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_timeAdvanceRequest(self, theTime: Any) -> None:
        self._request_time_advance("TAR", theTime)

    def _svc_timeAdvanceRequestAvailable(self, theTime: Any) -> None:
        self._request_time_advance("TARA", theTime)

    def _svc_nextMessageRequest(self, theTime: Any) -> None:
        self._request_time_advance("NMR", theTime)

    def _svc_nextMessageRequestAvailable(self, theTime: Any) -> None:
        self._request_time_advance("NMRA", theTime)

    def _svc_flushQueueRequest(self, theTime: Any) -> None:
        self._request_time_advance("FQR", theTime)

    def _svc_queryLogicalTime(self) -> Any:
        self._require_joined()
        return self.state.current_time

    def _svc_queryGALT(self) -> TimeQueryReturn:
        federation = self._require_joined()
        return self._compute_galt(federation, self.state)

    def _svc_queryLITS(self) -> TimeQueryReturn:
        federation = self._require_joined()
        return self._compute_lits(federation, self.state)

    def _svc_queryLookahead(self) -> Any:
        self._require_joined()
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        return self.state.lookahead

    def _svc_modifyLookahead(self, theLookahead: Any) -> None:
        self._require_joined()
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        if self.state.time_advancing and self.config.enforce_time_advancing_state:
            raise InTimeAdvancingState("Cannot modify lookahead while time advancing")
        lookahead = self._coerce_interval(theLookahead)
        if _time_value(lookahead) < 0:
            raise InvalidLookahead("Lookahead must be non-negative")
        self.state.lookahead = lookahead
        federation = self._require_joined()
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)

    def _svc_retract(self, theHandle: MessageRetractionHandle) -> None:
        federation = self._require_joined()
        if not self.state.time_regulation_enabled:
            raise TimeRegulationIsNotEnabled("Time regulation is not enabled")
        if not isinstance(theHandle, MessageRetractionHandle):
            from ..exceptions import InvalidMessageRetractionHandle

            raise InvalidMessageRetractionHandle(repr(theHandle))
        for federate in list(federation.federates.values()):
            message = federate.retraction_messages.get(theHandle)
            if message is not None and not message.retracted:
                message.retracted = True
                federate.retraction_messages.pop(theHandle, None)
                federate.retractable_messages[theHandle] = False
                self.state.retractable_messages[theHandle] = False
                return
        for message in list(federation.tso_messages):
            if message.retraction_handle == theHandle and not message.retracted:
                message.retracted = True
                try:
                    federation.tso_messages.remove(message)
                except ValueError:
                    pass
                self.state.retractable_messages[theHandle] = False
                return
        raise MessageCanNoLongerBeRetracted(repr(theHandle))

    def _svc_changeAttributeOrderType(self, theObject: ObjectInstanceHandle, theAttributes: Iterable[AttributeHandle], theType: OrderType) -> None:
        self._find_object(theObject)
        if not isinstance(theType, OrderType):
            from ..exceptions import InvalidOrderType

            raise InvalidOrderType(repr(theType))
        for attr in set(theAttributes):
            self.state.attribute_order_overrides[(theObject, attr)] = theType

    def _svc_changeInteractionOrderType(self, theClass: InteractionClassHandle, theType: OrderType) -> None:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        if not isinstance(theType, OrderType):
            from ..exceptions import InvalidOrderType

            raise InvalidOrderType(repr(theType))
        self.state.interaction_order_overrides[theClass] = theType

    # Callback control/support ---------------------------------------------
    def _svc_enableCallbacks(self) -> None:
        self._require_connected()
        self.state.callbacks_enabled = True

    def _svc_disableCallbacks(self) -> None:
        self._require_connected()
        self.state.callbacks_enabled = False

    def _svc_evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        self._require_connected()
        if not self.state.callbacks_enabled or not self.state.queue:
            return False
        event = self.state.queue.popleft()
        self._invoke_callback(self.state, event.method_name, event.args)
        return bool(self.state.queue)

    def _svc_evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        self._require_connected()
        delivered = False
        while self.state.callbacks_enabled and self.state.queue:
            event = self.state.queue.popleft()
            self._invoke_callback(self.state, event.method_name, event.args)
            delivered = True
        return delivered

    def _svc_enableAsynchronousDelivery(self) -> None:
        federation = self._require_joined()
        self.state.asynchronous_delivery_enabled = True
        self._refresh_mom_federate_object(federation, self.state, notify=True)

    def _svc_disableAsynchronousDelivery(self) -> None:
        federation = self._require_joined()
        self.state.asynchronous_delivery_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)

    # DDM ------------------------------------------------------------------
    def _svc_createRegion(self, dimensions: Iterable[DimensionHandle]) -> RegionHandle:
        self._require_joined()
        handle = self.engine._alloc(RegionHandle)
        dims = set(dimensions)
        for dimension in dims:
            self.engine.dimension_name(dimension)
        self.state.regions[handle] = dims
        self.state.region_bounds[handle] = {dimension: RangeBounds(0, (1 << 63) - 1) for dimension in dims}
        return handle

    def _svc_commitRegionModifications(self, regions: Iterable[RegionHandle]) -> None:
        self._require_joined()
        for region in regions:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))

    def _svc_deleteRegion(self, theRegion: RegionHandle) -> None:
        self._require_joined()
        self.state.regions.pop(theRegion, None)
        self.state.region_bounds.pop(theRegion, None)

    # DDM helpers -----------------------------------------------------------
    def _region_bounds_for(self, federate: FederateState, region: RegionHandle) -> dict[DimensionHandle, RangeBounds]:
        return federate.region_bounds.setdefault(region, {})

    def _range_overlap(self, left: RangeBounds, right: RangeBounds) -> bool:
        left_lower = getattr(left, "lower", getattr(left, "lower_bound"))
        left_upper = getattr(left, "upper", getattr(left, "upper_bound"))
        right_lower = getattr(right, "lower", getattr(right, "lower_bound"))
        right_upper = getattr(right, "upper", getattr(right, "upper_bound"))
        return int(left_lower) <= int(right_upper) and int(right_lower) <= int(left_upper)

    def _regions_overlap(self, source_federate: FederateState, source_region: RegionHandle, target_federate: FederateState, target_region: RegionHandle) -> bool:
        if source_region not in source_federate.regions or target_region not in target_federate.regions:
            return False
        common_dims = set(source_federate.regions[source_region]) & set(target_federate.regions[target_region])
        if not common_dims:
            return False
        for dimension in common_dims:
            source_bounds = self._region_bounds_for(source_federate, source_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            target_bounds = self._region_bounds_for(target_federate, target_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            if not self._range_overlap(source_bounds, target_bounds):
                return False
        return True

    def _region_sets_overlap(self, source_federate: FederateState, source_regions: set[RegionHandle], target_federate: FederateState, target_regions: set[RegionHandle]) -> bool:
        if not target_regions:
            return True
        if not source_regions:
            return False
        return any(
            self._regions_overlap(source_federate, source, target_federate, target)
            for source in source_regions
            for target in target_regions
        )

    def _filter_reflected_attributes_by_regions(self, subscriber: FederateState, instance: ObjectInstance, reflected: dict[AttributeHandle, bytes]) -> dict[AttributeHandle, bytes]:
        subscription: dict[AttributeHandle, set[RegionHandle]] = {}
        for subscribed_class, class_regions in subscriber.object_region_subscriptions.items():
            if self._object_matches_subscription(instance.class_handle, subscribed_class):
                for attr, regions in class_regions.items():
                    subscription.setdefault(attr, set()).update(regions)
        if not subscription:
            return reflected
        filtered: dict[AttributeHandle, bytes] = {}
        source_region_map = instance.update_regions or self.state.update_regions.get(instance.handle, {})
        for attr, value in reflected.items():
            target_regions = subscription.get(attr, set())
            if not target_regions:
                filtered[attr] = value
                continue
            source_regions = source_region_map.get(attr, set())
            if self._region_sets_overlap(self.state, set(source_regions), subscriber, set(target_regions)):
                filtered[attr] = value
        return filtered

    # DDM region-overlap helpers -------------------------------------------
    def _region_bounds_for(self, federate: FederateState, region: RegionHandle) -> dict[DimensionHandle, RangeBounds]:
        if region not in federate.regions:
            raise InvalidRegion(repr(region))
        return federate.region_bounds.setdefault(region, {})

    def _range_overlap(self, left: RangeBounds, right: RangeBounds) -> bool:
        left_lower = getattr(left, "lower", getattr(left, "lower_bound", 0))
        left_upper = getattr(left, "upper", getattr(left, "upper_bound", 0))
        right_lower = getattr(right, "lower", getattr(right, "lower_bound", 0))
        right_upper = getattr(right, "upper", getattr(right, "upper_bound", 0))
        return int(left_lower) <= int(right_upper) and int(right_lower) <= int(left_upper)

    def _regions_overlap_pair(self, source_federate: FederateState, source_region: RegionHandle, target_federate: FederateState, target_region: RegionHandle) -> bool:
        if source_region not in source_federate.regions or target_region not in target_federate.regions:
            return False
        common_dims = set(source_federate.regions[source_region]) & set(target_federate.regions[target_region])
        if not common_dims:
            return False
        for dimension in common_dims:
            source_bounds = self._region_bounds_for(source_federate, source_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            target_bounds = self._region_bounds_for(target_federate, target_region).get(dimension, RangeBounds(0, (1 << 63) - 1))
            if not self._range_overlap(source_bounds, target_bounds):
                return False
        return True

    def _region_sets_overlap(self, source_federate: FederateState, source_regions: set[RegionHandle], target_federate: FederateState, target_regions: set[RegionHandle]) -> bool:
        if not target_regions:
            return True
        if not source_regions:
            return True
        return any(
            self._regions_overlap_pair(source_federate, source_region, target_federate, target_region)
            for source_region in source_regions
            for target_region in target_regions
        )

    def _attribute_region_pairs(self, attributesAndRegions: Iterable[Any]) -> list[tuple[set[AttributeHandle], set[RegionHandle]]]:
        self._require_joined()
        pairs: list[tuple[set[AttributeHandle], set[RegionHandle]]] = []
        for pair in attributesAndRegions or []:
            if hasattr(pair, "attributes") and hasattr(pair, "regions"):
                attrs = getattr(pair, "attributes")
                regions = getattr(pair, "regions")
            elif isinstance(pair, Mapping):
                attrs = pair.get("attributes") or pair.get("attribute_handles") or pair.get("attributeList") or ()
                regions = pair.get("regions") or pair.get("region_handles") or pair.get("regionSet") or ()
            elif isinstance(pair, (tuple, list)) and len(pair) >= 2:
                attrs, regions = pair[0], pair[1]
            else:
                from ..exceptions import InvalidRegionContext
                raise InvalidRegionContext(f"Bad attribute/region pair: {pair!r}")
            attr_set = {attrs} if isinstance(attrs, AttributeHandle) else set(attrs)
            region_set = {regions} if isinstance(regions, RegionHandle) else set(regions)
            for region in region_set:
                if region not in self.state.regions:
                    raise InvalidRegion(repr(region))
            pairs.append((attr_set, region_set))
        return pairs

    def _attributes_from_region_pairs(self, attributesAndRegions: Iterable[Any]) -> set[AttributeHandle]:
        attrs: set[AttributeHandle] = set()
        for attr_set, _region_set in self._attribute_region_pairs(attributesAndRegions):
            attrs.update(attr_set)
        return attrs

    def _regions_from_region_pairs(self, attributesAndRegions: Iterable[Any]) -> set[RegionHandle]:
        regions: set[RegionHandle] = set()
        for _attr_set, region_set in self._attribute_region_pairs(attributesAndRegions):
            regions.update(region_set)
        return regions

    def _svc_subscribeObjectClassAttributesWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: Iterable[Any], *unused: Any) -> None:
        pairs = self._attribute_region_pairs(attributesAndRegions)
        attrs = set()
        region_map = self.state.object_region_subscriptions.setdefault(theClass, {})
        for attr_set, region_set in pairs:
            attrs.update(attr_set)
            for attr in attr_set:
                region_map.setdefault(attr, set()).update(region_set)
        self._svc_subscribeObjectClassAttributes(theClass, attrs, *unused)

    def _svc_subscribeObjectClassAttributesPassivelyWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: Iterable[Any], *unused: Any) -> None:
        self._svc_subscribeObjectClassAttributesWithRegions(theClass, attributesAndRegions, *unused)

    def _svc_unsubscribeObjectClassAttributesWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: Iterable[Any]) -> None:
        pairs = self._attribute_region_pairs(attributesAndRegions)
        class_regions = self.state.object_region_subscriptions.get(theClass, {})
        attrs: set[AttributeHandle] = set()
        for attr_set, region_set in pairs:
            attrs.update(attr_set)
            for attr in attr_set:
                if attr in class_regions:
                    class_regions[attr].difference_update(region_set)
                    if not class_regions[attr]:
                        class_regions.pop(attr, None)
        if not class_regions:
            self.state.object_region_subscriptions.pop(theClass, None)
        if attrs:
            self._svc_unsubscribeObjectClassAttributes(theClass, attrs)
        else:
            self._svc_unsubscribeObjectClass(theClass)

    def _svc_subscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle], *unused: Any) -> None:
        self._require_joined()
        region_set = set(regions)
        for region in region_set:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        self.state.interaction_region_subscriptions.setdefault(theClass, set()).update(region_set)
        self._svc_subscribeInteractionClass(theClass, *unused)

    def _svc_subscribeInteractionClassPassivelyWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle], *unused: Any) -> None:
        self._svc_subscribeInteractionClassWithRegions(theClass, regions, *unused)

    def _svc_unsubscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: Iterable[RegionHandle]) -> None:
        self._require_joined()
        region_set = set(regions)
        for region in region_set:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        if theClass in self.state.interaction_region_subscriptions:
            self.state.interaction_region_subscriptions[theClass].difference_update(region_set)
            if not self.state.interaction_region_subscriptions[theClass]:
                self.state.interaction_region_subscriptions.pop(theClass, None)
        self._svc_unsubscribeInteractionClass(theClass)

    def _svc_registerObjectInstanceWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: Iterable[Any], theObjectName: str | None = None) -> ObjectInstanceHandle:
        handle = self._svc_registerObjectInstance(theClass, theObjectName)
        _fed, instance = self._find_object(handle)
        region_map = self.state.update_regions.setdefault(handle, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                region_map.setdefault(attr, set()).update(regions)
                instance.update_regions.setdefault(attr, set()).update(regions)
        return handle

    def _svc_associateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: Iterable[Any]) -> None:
        _fed, instance = self._find_object(theObject)
        region_map = self.state.update_regions.setdefault(theObject, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                region_map.setdefault(attr, set()).update(regions)
                instance.update_regions.setdefault(attr, set()).update(regions)

    def _svc_unassociateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: Iterable[Any]) -> None:
        _fed, instance = self._find_object(theObject)
        region_map = self.state.update_regions.setdefault(theObject, {})
        for attrs, regions in self._attribute_region_pairs(attributesAndRegions):
            for attr in attrs:
                if attr in region_map:
                    region_map[attr].difference_update(regions)
                    if not region_map[attr]:
                        del region_map[attr]
                if attr in instance.update_regions:
                    instance.update_regions[attr].difference_update(regions)
                    if not instance.update_regions[attr]:
                        del instance.update_regions[attr]

    def _svc_sendInteractionWithRegions(self, theInteraction: InteractionClassHandle, theParameters: Mapping[ParameterHandle, bytes], regions: Iterable[RegionHandle], userSuppliedTag: bytes, *unused: Any) -> MessageRetractionReturn | None:
        federation = self._require_joined()
        interaction_def = self.engine.interaction_for_handle(theInteraction)
        source_regions = set(regions)
        for region in source_regions:
            if region not in self.state.regions:
                raise InvalidRegion(repr(region))
        params = {handle: bytes(value) for handle, value in dict(theParameters).items()}
        if self._handle_mom_interaction(interaction_def.name, params, bytes(userSuppliedTag)):
            return None
        if self.config.strict_interaction_publication and theInteraction not in self.state.published_interactions:
            raise InteractionClassNotPublished(repr(theInteraction))
        timestamp = self._extract_timestamp(tuple(unused))
        preferred = self.state.interaction_order_overrides.get(theInteraction, OrderType.TIMESTAMP if timestamp is not None else self.config.default_preferred_order_type)
        sent_tso = bool(timestamp is not None and self.state.time_regulation_enabled and preferred is OrderType.TIMESTAMP)
        if sent_tso:
            self._validate_tso_send_time(timestamp)
        retraction = self._make_retraction_return(timestamp) if sent_tso else None
        self.state.interactions_sent += 1
        assert self.state.handle is not None
        for federate in list(federation.federates.values()):
            if federate is self.state:
                continue
            if not any(self._interaction_matches_subscription(theInteraction, subscribed) for subscribed in federate.subscribed_interactions):
                continue
            target_regions = federate.interaction_region_subscriptions.get(theInteraction, set())
            if target_regions and not self._region_sets_overlap(self.state, source_regions, federate, set(target_regions)):
                continue
            info = SupplementalReceiveInfo(producing_federate=self.state.handle, sent_regions=frozenset(source_regions))
            if sent_tso and federate.time_constrained_enabled:
                assert retraction is not None
                event = CallbackEvent(
                    "receiveInteraction",
                    (theInteraction, params, bytes(userSuppliedTag), OrderType.TIMESTAMP, self.engine.transportation_reliable, timestamp, OrderType.TIMESTAMP, retraction.handle, info),
                )
                self._queue_or_deliver_tso(federation, federate, timestamp, event, retraction_handle=retraction.handle, producing_federate=self.state.handle)
            else:
                event = CallbackEvent(
                    "receiveInteraction",
                    (theInteraction, params, bytes(userSuppliedTag), OrderType.RECEIVE, self.engine.transportation_reliable, info),
                )
                self._deliver(federate, event.method_name, *event.args)
        self._refresh_mom_federate_object(federation, self.state, notify=True)
        self._process_time_advances(federation)
        return retraction

    def _svc_requestAttributeValueUpdateWithRegions(self, target: Any, attributesAndRegions: Iterable[Any], userSuppliedTag: bytes = b"") -> None:
        self._svc_requestAttributeValueUpdate(target, self._attributes_from_region_pairs(attributesAndRegions), userSuppliedTag)

    def _svc_getRangeBounds(self, theRegion: RegionHandle, theDimension: DimensionHandle) -> RangeBounds:
        self._require_joined()
        if theRegion not in self.state.regions:
            raise InvalidRegion(repr(theRegion))
        if theDimension not in self.state.regions[theRegion]:
            from ..exceptions import RegionDoesNotContainSpecifiedDimension
            raise RegionDoesNotContainSpecifiedDimension(repr(theDimension))
        return self.state.region_bounds.setdefault(theRegion, {}).get(theDimension, RangeBounds(0, (1 << 63) - 1))

    def _svc_setRangeBounds(self, theRegion: RegionHandle, theDimension: DimensionHandle, theRangeBounds: RangeBounds | tuple[int, int]) -> None:
        self._require_joined()
        if theRegion not in self.state.regions:
            raise InvalidRegion(repr(theRegion))
        if theDimension not in self.state.regions[theRegion]:
            from ..exceptions import RegionDoesNotContainSpecifiedDimension
            raise RegionDoesNotContainSpecifiedDimension(repr(theDimension))
        if not isinstance(theRangeBounds, RangeBounds):
            theRangeBounds = RangeBounds(*theRangeBounds)
        self.state.region_bounds.setdefault(theRegion, {})[theDimension] = theRangeBounds

    def _svc_getDimensionUpperBound(self, theDimension: DimensionHandle) -> int:
        self.engine.dimension_name(theDimension)
        return (1 << 63) - 1

    # Support services ------------------------------------------------------
    def _svc_getAutomaticResignDirective(self) -> ResignAction:
        self._require_connected()
        return self.state.automatic_resign_directive

    def _svc_setAutomaticResignDirective(self, resignAction: ResignAction) -> None:
        self._require_connected()
        self.state.automatic_resign_directive = resignAction

    def _svc_enableObjectClassRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.object_class_relevance_advisory = True

    def _svc_disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.object_class_relevance_advisory = False

    def _svc_enableAttributeRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.attribute_relevance_advisory = True

    def _svc_disableAttributeRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.attribute_relevance_advisory = False

    def _svc_enableAttributeScopeAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.attribute_scope_advisory = True

    def _svc_disableAttributeScopeAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.attribute_scope_advisory = False

    def _svc_enableInteractionRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.interaction_relevance_advisory = True

    def _svc_disableInteractionRelevanceAdvisorySwitch(self) -> None:
        self._require_joined()
        self.state.interaction_relevance_advisory = False

    def _svc_getFederateName(self, theHandle: FederateHandle | None = None) -> str:
        federation = self._require_joined()
        if theHandle is None:
            if self.state.name is None:
                raise FederateHandleNotKnown("Current federate has no name")
            return self.state.name
        target = federation.federates.get(theHandle)
        if target is None or target.name is None:
            raise FederateHandleNotKnown(repr(theHandle))
        return target.name

    def _svc_getFederateHandle(self, theName: str) -> FederateHandle:
        federation = self._require_joined()
        for handle, federate in federation.federates.items():
            if federate.name == theName:
                return handle
        raise NameNotFound(str(theName))

    def _svc_getObjectClassHandle(self, theName: str) -> ObjectClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.object_classes:
            raise NameNotFound(name)
        return self.engine.get_or_create_object_class(name).handle

    def _svc_getObjectClassName(self, theHandle: ObjectClassHandle) -> str:
        self._require_joined()
        return self.engine.object_class_for_handle(theHandle).name

    def _svc_getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:
        federation = self._require_joined()
        class_def = self.engine.object_class_for_handle(whichClass)
        name = str(theName)
        if self._enforce_fom_names(federation):
            spec = federation.fom_catalog.object_classes.get(class_def.name)
            if spec is None or name not in spec.attributes:
                raise NameNotFound(name)
        return self.engine.get_or_create_attribute(whichClass, name)

    def _svc_getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:
        self._require_joined()
        return self.engine.attribute_name(whichClass, theHandle)

    def _svc_getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.interaction_classes:
            raise NameNotFound(name)
        return self.engine.get_or_create_interaction_class(name).handle

    def _svc_getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:
        self._require_joined()
        return self.engine.interaction_for_handle(theHandle).name

    def _svc_getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:
        federation = self._require_joined()
        class_def = self.engine.interaction_for_handle(whichClass)
        name = str(theName)
        if self._enforce_fom_names(federation):
            spec = federation.fom_catalog.interaction_classes.get(class_def.name)
            if spec is None or name not in spec.parameters:
                raise NameNotFound(name)
        return self.engine.get_or_create_parameter(whichClass, name)

    def _svc_getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:
        self._require_joined()
        return self.engine.parameter_name(whichClass, theHandle)

    def _svc_getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:
        federation = self._require_joined()
        try:
            return federation.object_names[str(theName)]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(theName)) from exc

    def _svc_getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:
        federation = self._require_joined()
        try:
            return federation.objects[theHandle].name
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(theHandle)) from exc

    def _svc_getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:
        _, instance = self._find_object(theObject)
        return instance.class_handle

    def _svc_getDimensionHandle(self, theName: str) -> DimensionHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and federation.fom_catalog.dimensions and name not in federation.fom_catalog.dimensions:
            raise NameNotFound(name)
        return self.engine.get_or_create_dimension(name)

    def _svc_getDimensionName(self, theHandle: DimensionHandle) -> str:
        self._require_joined()
        return self.engine.dimension_name(theHandle)

    def _svc_getTransportationTypeHandle(self, transportationType: str | None = None) -> TransportationTypeHandle:
        self._require_joined()
        return self.engine.transportation_reliable

    def _svc_getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        self._require_joined()
        if theHandle == self.engine.transportation_reliable:
            return "HLAreliable"
        return f"TransportationType-{theHandle.value}"

    def _svc_getHLAversion(self) -> str:
        return "HLA 1516-2010 Python in-memory RTI subset"

    def _svc_getTimeFactory(self) -> LogicalTimeFactory[Any, Any]:
        self._require_joined()
        return self._time_factory()

    def _svc_getDimensionHandleSet(self, region: RegionHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        try:
            return hla_handles.DimensionHandleSet(self.state.regions[region])
        except KeyError as exc:
            raise InvalidRegion(repr(region)) from exc

    def _svc_getOrderName(self, orderType: OrderType) -> str:
        if not isinstance(orderType, OrderType):
            from ..exceptions import InvalidOrderType
            raise InvalidOrderType(repr(orderType))
        return orderType.name

    def _svc_getOrderType(self, orderName: str) -> OrderType:
        normalized = str(orderName).replace("HLA", "").replace("_", "").replace(" ", "").upper()
        if normalized in {"RECEIVE", "RECEIVEORDER"}:
            return OrderType.RECEIVE
        if normalized in {"TIMESTAMP", "TIMESTAMPORDER", "TSO"}:
            return OrderType.TIMESTAMP
        from ..exceptions import InvalidOrderName
        raise InvalidOrderName(str(orderName))

    def _svc_getTransportationType(self, transportationName: str | None = None) -> TransportationTypeHandle:
        return self._svc_getTransportationTypeHandle(transportationName)

    def _svc_getTransportationName(self, transportationType: TransportationTypeHandle) -> str:
        return self._svc_getTransportationTypeName(transportationType)

    def _all_known_dimensions(self) -> hla_handles.DimensionHandleSet:
        if not self.engine.dimensions_by_name:
            return hla_handles.DimensionHandleSet([self.engine.get_or_create_dimension("HLAdefaultRoutingSpace")])
        return hla_handles.DimensionHandleSet(self.engine.dimensions_by_name.values())

    def _svc_getAvailableDimensionsForClassAttribute(self, theClass: ObjectClassHandle, theAttribute: AttributeHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.attribute_name(theClass, theAttribute)
        return self._all_known_dimensions()

    def _svc_getAvailableDimensionsForInteractionClass(self, theClass: InteractionClassHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        return self._all_known_dimensions()

    def _svc_getUpdateRateValue(self, updateRateDesignator: str) -> float:
        self._require_connected()
        return 0.0

    def _svc_getUpdateRateValueForAttribute(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> float:
        self._find_object(theObject)
        return 0.0

    def _svc_normalizeFederateHandle(self, theFederateHandle: FederateHandle) -> FederateHandle:
        federation = self._require_joined()
        if theFederateHandle not in federation.federates:
            from ..exceptions import InvalidFederateHandle
            raise InvalidFederateHandle(repr(theFederateHandle))
        return theFederateHandle

    def _svc_normalizeServiceGroup(self, theServiceGroup: ServiceGroup | str) -> ServiceGroup:
        self._require_connected()
        if isinstance(theServiceGroup, ServiceGroup):
            return theServiceGroup
        key = str(theServiceGroup).replace(" ", "_").replace("-", "_").upper()
        try:
            return ServiceGroup[key]
        except KeyError as exc:
            from ..exceptions import InvalidServiceGroup
            raise InvalidServiceGroup(str(theServiceGroup)) from exc

    # Java-style handle/set/map factory helpers -----------------------------
    def _svc_getAttributeHandleFactory(self) -> hla_handles.AttributeHandleFactory:
        self._require_connected()
        return hla_handles.AttributeHandleFactory()

    def _svc_getAttributeHandleSetFactory(self) -> hla_handles.AttributeHandleSetFactory:
        self._require_connected()
        return hla_handles.AttributeHandleSetFactory()

    def _svc_getAttributeHandleValueMapFactory(self) -> hla_handles.AttributeHandleValueMapFactory:
        self._require_connected()
        return hla_handles.AttributeHandleValueMapFactory()

    def _svc_getAttributeSetRegionSetPairListFactory(self) -> hla_handles.AttributeSetRegionSetPairListFactory:
        self._require_connected()
        return hla_handles.AttributeSetRegionSetPairListFactory()

    def _svc_getDimensionHandleFactory(self) -> hla_handles.DimensionHandleFactory:
        self._require_connected()
        return hla_handles.DimensionHandleFactory()

    def _svc_getDimensionHandleSetFactory(self) -> hla_handles.DimensionHandleSetFactory:
        self._require_connected()
        return hla_handles.DimensionHandleSetFactory()

    def _svc_getFederateHandleFactory(self) -> hla_handles.FederateHandleFactory:
        self._require_connected()
        return hla_handles.FederateHandleFactory()

    def _svc_getFederateHandleSetFactory(self) -> hla_handles.FederateHandleSetFactory:
        self._require_connected()
        return hla_handles.FederateHandleSetFactory()

    def _svc_getInteractionClassHandleFactory(self) -> hla_handles.InteractionClassHandleFactory:
        self._require_connected()
        return hla_handles.InteractionClassHandleFactory()

    def _svc_getObjectClassHandleFactory(self) -> hla_handles.ObjectClassHandleFactory:
        self._require_connected()
        return hla_handles.ObjectClassHandleFactory()

    def _svc_getObjectInstanceHandleFactory(self) -> hla_handles.ObjectInstanceHandleFactory:
        self._require_connected()
        return hla_handles.ObjectInstanceHandleFactory()

    def _svc_getParameterHandleFactory(self) -> hla_handles.ParameterHandleFactory:
        self._require_connected()
        return hla_handles.ParameterHandleFactory()

    def _svc_getParameterHandleValueMapFactory(self) -> hla_handles.ParameterHandleValueMapFactory:
        self._require_connected()
        return hla_handles.ParameterHandleValueMapFactory()

    def _svc_getRegionHandleSetFactory(self) -> hla_handles.RegionHandleSetFactory:
        self._require_connected()
        return hla_handles.RegionHandleSetFactory()

    def _svc_getTransportationTypeHandleFactory(self) -> hla_handles.TransportationTypeHandleFactory:
        self._require_connected()
        return hla_handles.TransportationTypeHandleFactory()

    # Handle factory helpers -----------------------------------------------
    def _svc_decodeMessageRetractionHandle(self, buffer: bytes) -> MessageRetractionHandle:
        return MessageRetractionHandle.decode(buffer)

    def _svc_decodeFederateHandle(self, buffer: bytes) -> FederateHandle:
        return FederateHandle.decode(buffer)

    def _svc_decodeObjectClassHandle(self, buffer: bytes) -> ObjectClassHandle:
        return ObjectClassHandle.decode(buffer)

    def _svc_decodeAttributeHandle(self, buffer: bytes) -> AttributeHandle:
        return AttributeHandle.decode(buffer)

    def _svc_decodeObjectInstanceHandle(self, buffer: bytes) -> ObjectInstanceHandle:
        return ObjectInstanceHandle.decode(buffer)

    def _svc_decodeInteractionClassHandle(self, buffer: bytes) -> InteractionClassHandle:
        return InteractionClassHandle.decode(buffer)

    def _svc_decodeParameterHandle(self, buffer: bytes) -> ParameterHandle:
        return ParameterHandle.decode(buffer)

    def _svc_decodeDimensionHandle(self, buffer: bytes) -> DimensionHandle:
        return DimensionHandle.decode(buffer)

    def _svc_decodeRegionHandle(self, buffer: bytes) -> RegionHandle:
        return RegionHandle.decode(buffer)


def create_python_backend(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
) -> PythonRTIBackend:
    """Create one PythonRTIBackend/federate connection against an engine."""

    return PythonRTIBackend(engine=engine, config=config)


def rti_ambassador(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
):
    """Convenience: return a DelegatingRTIAmbassador backed by the Python RTI."""

    return make_rti_ambassador(create_python_backend(engine=engine, config=config))


__all__ = [
    "InMemoryRTIEngine",
    "PythonRTIBackend",
    "PythonRTIConfig",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "create_python_backend",
    "rti_ambassador",
]
