"""Data model for the in-memory Python RTI backend."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque

from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction, RestoreStatus, SaveStatus
from hla.fom import FOMCatalog, FOMModule
from hla.rti1516e.handles import (
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
from hla.rti1516e.time import DEFAULT_TIME_FACTORY_REGISTRY, HLAfloat64TimeFactory, HLAinteger64Time, LogicalTimeFactory
from hla.rti1516e.datatypes import FederateHandleSaveStatusPair, FederateRestoreStatus, MessageRetractionReturn, RangeBounds, TimeQueryReturn


@dataclass(frozen=True)
class SupplementalReflectInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SupplementalReceiveInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SupplementalRemoveInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: frozenset[RegionHandle] = field(default_factory=frozenset)


@dataclass
class PythonRTIConfig:
    name: str = "python1516e-rti"
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
    mom_model: Any | None = None
    time_factory: LogicalTimeFactory[Any, Any] = field(default_factory=lambda: DEFAULT_TIME_FACTORY_REGISTRY.get(HLAfloat64TimeFactory.NAME))
    federates: dict[FederateHandle, "FederateState"] = field(default_factory=dict)
    objects: dict[ObjectInstanceHandle, ObjectInstance] = field(default_factory=dict)
    object_names: dict[str, ObjectInstanceHandle] = field(default_factory=dict)
    reserved_object_names: dict[str, FederateHandle] = field(default_factory=dict)
    synchronization_points: dict[str, SynchronizationPointState] = field(default_factory=dict)
    region_owners: dict[RegionHandle, FederateHandle] = field(default_factory=dict)
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
    tso_messages: list["TimedMessage"] = field(default_factory=list)
    next_message_sequence: int = 1
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
    mode: str
    requested_time: Any


@dataclass
class TimedMessage:
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
    sort_key: tuple[float | int, int]
    timestamp: Any = field(compare=False)
    sent_order: OrderType = field(compare=False)
    received_order: OrderType = field(compare=False)
    callback: CallbackEvent = field(compare=False)
    retraction_handle: MessageRetractionHandle | None = field(default=None, compare=False)
    sender: FederateHandle | None = field(default=None, compare=False)
    service_name: str = field(default="", compare=False)
    retracted: bool = field(default=False, compare=False)
    post_deliver_cleanup: Any | None = field(default=None, compare=False)


@dataclass
class FederateState:
    backend_id: int
    ambassador: Any | None = None
    callback_model: CallbackModel = CallbackModel.HLA_EVOKED
    connected: bool = False
    disconnect_pending_after_connection_lost: bool = False
    local_settings_designator: str | None = None
    handle: FederateHandle | None = None
    name: str | None = None
    federate_type: str | None = None
    federation: FederationState | None = None
    callbacks_enabled: bool = True
    in_callback: bool = False
    queue: Deque[CallbackEvent] = field(default_factory=deque)
    published_objects: dict[ObjectClassHandle, set[AttributeHandle]] = field(default_factory=dict)
    subscribed_objects: dict[ObjectClassHandle, set[AttributeHandle]] = field(default_factory=dict)
    subscribed_object_update_rates: dict[ObjectClassHandle, dict[AttributeHandle, float]] = field(default_factory=dict)
    subscribed_object_update_rate_designators: dict[ObjectClassHandle, dict[AttributeHandle, str]] = field(default_factory=dict)
    registration_interest_classes: set[ObjectClassHandle] = field(default_factory=set)
    published_interactions: set[InteractionClassHandle] = field(default_factory=set)
    subscribed_interactions: set[InteractionClassHandle] = field(default_factory=set)
    interaction_interest_classes: set[InteractionClassHandle] = field(default_factory=set)
    regions: dict[RegionHandle, set[DimensionHandle]] = field(default_factory=dict)
    region_bounds: dict[RegionHandle, dict[DimensionHandle, RangeBounds]] = field(default_factory=dict)
    update_regions: dict[ObjectInstanceHandle, dict[AttributeHandle, set[RegionHandle]]] = field(default_factory=dict)
    object_region_subscriptions: dict[ObjectClassHandle, dict[AttributeHandle, set[RegionHandle]]] = field(default_factory=dict)
    interaction_region_subscriptions: dict[InteractionClassHandle, set[RegionHandle]] = field(default_factory=dict)
    time_regulation_enabled: bool = False
    time_constrained_enabled: bool = False
    request_for_time_regulation_pending: bool = False
    request_for_time_constrained_pending: bool = False
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
    delivered_retraction_messages: dict[MessageRetractionHandle, QueuedTimeMessage] = field(default_factory=dict)
    retractable_messages: dict[MessageRetractionHandle, bool] = field(default_factory=dict)
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
    last_reporting_handle: FederateHandle | None = None
    last_reporting_name: str | None = None
    last_reporting_federation: FederationState | None = None
    service_reports_to_file: bool = False
    service_report_file: str | None = None
    service_report_initial_record_written: bool = False
    service_report_serial_number: int = 0
    service_report_records: list[dict[str, Any]] = field(default_factory=list)
    callback_counts: dict[str, int] = field(default_factory=dict)
    recent_callbacks: list[str] = field(default_factory=list)
    attribute_order_overrides: dict[tuple[ObjectInstanceHandle, AttributeHandle], OrderType] = field(default_factory=dict)
    interaction_order_overrides: dict[InteractionClassHandle, OrderType] = field(default_factory=dict)
    attribute_transportation_overrides: dict[tuple[ObjectInstanceHandle, AttributeHandle], TransportationTypeHandle] = field(default_factory=dict)
    interaction_transportation_overrides: dict[InteractionClassHandle, TransportationTypeHandle] = field(default_factory=dict)
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
    known_object_classes: dict[ObjectInstanceHandle, ObjectClassHandle] = field(default_factory=dict)
    known_object_names: dict[str, ObjectInstanceHandle] = field(default_factory=dict)
    in_scope_object_attributes: dict[ObjectInstanceHandle, set[AttributeHandle]] = field(default_factory=dict)
    relevant_object_update_designators: dict[ObjectInstanceHandle, dict[AttributeHandle, str | None]] = field(default_factory=dict)
    locally_deleted_objects: set[ObjectInstanceHandle] = field(default_factory=set)
    last_reflect_logical_times: dict[tuple[ObjectInstanceHandle, AttributeHandle], float] = field(default_factory=dict)
    mom_attribute_reporting: dict[tuple[ObjectInstanceHandle, AttributeHandle], bool] = field(default_factory=dict)
    mom_attribute_reporting_states: dict[tuple[str, str], str] = field(default_factory=dict)


__all__ = [
    "CallbackEvent",
    "FederateHandleSaveStatusPair",
    "FederateRestoreStatus",
    "FederateState",
    "FederationState",
    "InteractionClassDef",
    "MOM_FEDERATE_CLASS",
    "MOM_FEDERATION_CLASS",
    "MOM_TEXT_ENCODING",
    "MessageRetractionReturn",
    "ObjectClassDef",
    "ObjectInstance",
    "PythonRTIConfig",
    "QueuedTimeMessage",
    "RTI_FEDERATE_HANDLE",
    "RangeBounds",
    "SupplementalReceiveInfo",
    "SupplementalReflectInfo",
    "SupplementalRemoveInfo",
    "SynchronizationPointState",
    "TimeAdvanceRequestState",
    "TimeQueryReturn",
    "TimedMessage",
]
