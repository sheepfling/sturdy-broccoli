"""Live IEEE 1516.1-2025 Python RTI backend implementation."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Mapping

from hla.backends.common import BackendInfo
from hla.backends.common import time_management as tm
from hla.backends.common.base import snake_to_lower_camel
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
    InvalidParameterHandle,
    InvalidRangeBound,
    InvalidResignAction,
    InvalidRegion,
    InvalidRegionContext,
    InvalidServiceGroup,
    InvalidUpdateRateDesignator,
    InvalidTransportationName,
    InvalidTransportationTypeHandle,
    LogicalTimeAlreadyPassed,
    MessageCanNoLongerBeRetracted,
    NameNotFound,
    TimeConstrainedAlreadyEnabled,
    TimeRegulationAlreadyEnabled,
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
    AttributeHandleFactory,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    InteractionClassHandleSetFactory,
    MessageRetractionHandle,
    MessageRetractionHandleFactory,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleFactory,
    RegionHandleSetFactory,
    TransportationTypeHandle,
    TransportationTypeHandleFactory,
)

from .declaration_management import (
    publish_object_class_attributes,
    release_multiple_object_instance_names,
    release_object_instance_name,
    reserve_multiple_object_instance_names,
    reserve_object_instance_name,
    subscribe_object_class_attributes,
    unpublish_object_class,
    unpublish_object_class_attributes,
    unsubscribe_object_class,
    unsubscribe_object_class_attributes,
)
from .catalog_runtime import (
    attribute_handles,
    interaction_class_name,
    object_class_name,
    object_instance_record,
    object_instance_record_known,
    parameter_handles,
    synchronization_required_federates,
    transportation_handle_by_name,
)
from .federation_management import (
    connect as federation_connect,
    create_federation_execution,
    create_federation_execution_with_mim,
    destroy_federation_execution,
    disconnect as federation_disconnect,
    force_federate_loss,
    join_federation_execution,
    list_federation_execution_members,
    list_federation_executions,
    register_federation_synchronization_point,
    resign_federation_execution,
    synchronization_point_achieved,
)
from .interaction_runtime import (
    change_interaction_order_type,
    publish_interaction_class,
    publish_object_class_directed_interactions,
    query_interaction_transportation_type,
    request_interaction_transportation_type_change,
    send_directed_interaction,
    send_interaction,
    send_interaction_with_regions,
    subscribe_interaction_class,
    subscribe_interaction_class_with_regions,
    subscribe_object_class_directed_interactions,
    unpublish_interaction_class,
    unpublish_object_class_directed_interactions,
    unsubscribe_interaction_class,
    unsubscribe_interaction_class_with_regions,
    unsubscribe_object_class_directed_interactions,
)
from .interaction_policy import (
    coerce_order_type,
    interaction_class_names_from_handles,
    interaction_order_for,
    interaction_transportation_for,
    parameter_names_from_handles,
)
from .save_restore import (
    abort_federation_restore,
    abort_federation_save,
    capture_federation_save_snapshot,
    complete_restore,
    complete_save,
    federate_save_begun,
    process_scheduled_save,
    query_federation_restore_status,
    query_federation_save_status,
    request_federation_restore,
    request_federation_save,
    restore_federation_save_snapshot,
    start_federation_save,
)
from .support_lookup import (
    get_attribute_handle,
    get_attribute_name,
    get_available_dimensions_for_interaction_class,
    get_available_dimensions_for_object_class,
    get_dimension_handle,
    get_dimension_name,
    get_dimension_upper_bound,
    get_federate_handle,
    get_federate_name,
    get_interaction_class_handle,
    get_interaction_class_name,
    get_known_object_class_handle,
    get_object_class_handle,
    get_object_class_name,
    get_object_instance_handle,
    get_object_instance_name,
    get_order_name,
    get_order_type,
    get_parameter_handle,
    get_parameter_name,
    get_transportation_type_handle,
    get_transportation_type_name,
)
from .support_services_runtime import (
    decode_attribute_handle as runtime_decode_attribute_handle,
    decode_dimension_handle as runtime_decode_dimension_handle,
    decode_federate_handle as runtime_decode_federate_handle,
    decode_interaction_class_handle as runtime_decode_interaction_class_handle,
    decode_message_retraction_handle as runtime_decode_message_retraction_handle,
    decode_object_class_handle as runtime_decode_object_class_handle,
    decode_object_instance_handle as runtime_decode_object_instance_handle,
    decode_parameter_handle as runtime_decode_parameter_handle,
    decode_region_handle as runtime_decode_region_handle,
    make_attribute_handle_factory,
    make_attribute_handle_set_factory,
    make_attribute_handle_value_map_factory,
    make_attribute_set_region_set_pair_list_factory,
    make_dimension_handle_factory,
    make_dimension_handle_set_factory,
    make_federate_handle_factory,
    make_federate_handle_set_factory,
    make_interaction_class_handle_factory,
    make_interaction_class_handle_set_factory,
    make_message_retraction_handle_factory,
    make_object_class_handle_factory,
    make_object_instance_handle_factory,
    make_parameter_handle_factory,
    make_parameter_handle_value_map_factory,
    make_region_handle_factory,
    make_region_handle_set_factory,
    make_transportation_type_handle_factory,
)
from .support_policy import (
    get_automatic_resign_directive,
    get_switch,
    normalize_service_group,
    serialize_mom_service_report,
    service_report_records_snapshot,
    set_attribute_scope_advisory_switch,
    set_automatic_resign_directive,
    set_switch,
)
from .attribute_policy import (
    attribute_order_for,
    attribute_transportation_for,
    default_order_for,
    default_transportation_for,
    known_object_classes_for_federate,
    reflectable_attribute_names_for_subscriber,
)
from .attribute_scope import (
    deliver_forced_remove_callbacks,
    evaluate_attribute_scope_advisories,
)
from .callback_runtime import (
    QueuedCallback,
    deliver_callback,
    deliver_callback_now,
    deliver_mom_service_report,
    deliver_queued_callback,
    deliver_to_federate_handle,
    deliver_to_federate_handle_now,
    disable_asynchronous_delivery,
    disable_callbacks,
    enable_asynchronous_delivery,
    enable_callbacks,
    evoke_callback,
    evoke_multiple_callbacks,
    force_connection_lost,
)
from .mom_codec import (
    mom_attribute_handles,
    mom_bool,
    mom_handle_list_payload,
    mom_index,
    mom_int,
    mom_module_data,
    mom_number,
    mom_order_type,
    mom_ownership_state,
    mom_request_params_by_name,
    mom_resign_action,
    mom_single_module_data,
    mom_target_rti,
    mom_text,
)
from .mom_runtime import (
    handle_mom_adjust_interaction,
    handle_mom_federate_request_interaction,
    handle_mom_interaction,
    handle_mom_service_interaction,
    modify_mom_attribute_state,
    mom_counts_for_federate,
    mom_deletable_object_counts,
    mom_request_report_values,
    mom_transport_counts_for_federate,
    send_mom_exception_interaction,
    send_mom_object_class_count_report,
    send_mom_object_instance_information_report,
    send_mom_publication_reports,
    send_mom_report_interaction,
    send_mom_subscription_reports,
    send_mom_transport_count_report,
)
from .object_model import (
    attribute_name_by_handle,
    attribute_names_from_handles,
    discover_existing_objects_for_current_subscription,
    has_object_registration_interest,
    matching_object_publishers,
    object_class_lineage,
    published_attributes_for_current_federate,
    subscribed_discovery_class_name,
)
from .object_instance_runtime import (
    delete_object_instance,
    deliver_value_update_requests,
    local_delete_object_instance,
    register_object_instance,
    request_attribute_value_update,
    request_instance_attribute_value_update,
    set_internal_object_attribute_values,
    update_attribute_values,
)
from .object_region_runtime import (
    associate_regions_for_updates,
    attribute_region_pairs,
    change_attribute_order_type,
    change_default_attribute_order_type,
    change_default_attribute_transportation_type,
    coerce_range_bounds,
    commit_region_modifications,
    create_region,
    delete_region,
    get_dimension_handle_set,
    get_range_bounds,
    object_instance_region_values,
    region_owner_key,
    region_sets_overlap,
    region_values_from_handles,
    regions_overlap_pair,
    ranges_overlap,
    query_attribute_transportation_type,
    register_object_instance_with_regions,
    request_attribute_transportation_type_change,
    set_range_bounds,
    subscribe_object_class_attributes_with_regions,
    unassociate_regions_for_updates,
    unsubscribe_object_class_attributes_with_regions,
)
from .object_reflection import (
    fanout_attribute_update,
    group_source_values_by_transport,
)
from .ownership_runtime import (
    attribute_ownership_acquisition,
    attribute_ownership_acquisition_if_available,
    attribute_ownership_divestiture_if_wanted,
    attribute_ownership_release_denied,
    cancel_attribute_ownership_acquisition,
    cancel_negotiated_attribute_ownership_divestiture,
    confirm_divestiture,
    is_attribute_owned_by_federate,
    negotiated_attribute_ownership_divestiture,
    query_attribute_ownership,
    unconditional_attribute_ownership_divestiture,
)
from .time_management import (
    build_time_management_federation,
    build_time_management_state,
    disable_time_constrained,
    disable_time_regulation,
    deliver_due_tso_callbacks_for_request,
    enable_time_constrained,
    enable_time_regulation,
    modify_lookahead,
    process_time_advances,
    query_lookahead,
    query_galt_for,
    query_lits_for,
    retract_message,
    request_time_advance,
    try_grant_pending_time_advance,
    validate_tso_send_time,
)
from .update_rate import (
    apply_update_rate_reduction_for_subscriber,
    default_update_rate_designator_for_attribute,
    default_update_rate_for_attribute,
    get_update_rate_value,
    resolve_update_rate_designator,
    subscribed_update_rate_for_attribute,
    time_scalar,
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
    member_rtis: dict[int, "Python2025RTIAmbassador"] = field(default_factory=dict)
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
    retraction_groups: dict[int, set[int]] = field(default_factory=dict)
    retraction_group_lookup: dict[int, int] = field(default_factory=dict)
    saved_labels: set[str] = field(default_factory=set)
    saved_object_instances: dict[str, dict[int, "_ObjectInstanceRecord"]] = field(default_factory=dict)
    saved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_reserved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_next_object_instance_handles: dict[str, int] = field(default_factory=dict)
    saved_member_logical_times: dict[str, dict[int, Any]] = field(default_factory=dict)
    saved_member_time_states: dict[str, dict[int, dict[str, Any]]] = field(default_factory=dict)
    saved_member_known_objects: dict[str, dict[int, dict[str, Any]]] = field(default_factory=dict)
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
    saved_retraction_groups: dict[str, dict[int, set[int]]] = field(default_factory=dict)
    saved_retraction_group_lookup: dict[str, dict[int, int]] = field(default_factory=dict)
    save_label: str | None = None
    next_save_name: str | None = None
    next_save_time: Any | None = None
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
    producing_federate: FederateHandle | None = None
    attribute_values: dict[str, bytes] = field(default_factory=dict)
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


_FEDERATION_REGISTRY: dict[str, _FederationRecord] = {}


@dataclass(frozen=True, slots=True)
class Python2025BackendInfo(BackendInfo):
    name: str = "python2025-rti"
    kind: str = "python/2025"
    version: str = "0.13.0"
    details: dict[str, Any] = field(
        default_factory=lambda: {
            "spec": "rti1516_2025",
            "provider": "python2025",
            "implementation_lane": "hla-backend-python2025",
            "counts_as_python_2025_rti": True,
        }
    )

class Python2025RTIAmbassador:
    """Minimal 2025 RTI ambassador for factory and adapter development."""

    backend_info = Python2025BackendInfo()
    _DEFAULT_LOGICAL_TIME_IMPLEMENTATION = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    _SWITCH_DEFAULTS = _SWITCH_DEFAULTS
    _FEDERATION_REGISTRY = _FEDERATION_REGISTRY
    _FederationRecord = _FederationRecord
    _SynchronizationPointRecord = _SynchronizationPointRecord

    def __init__(self) -> None:
        self._connected = False
        self._joined = False
        self._federation_name: str | None = None
        self._federate_name: str | None = None
        self._federate_handle: FederateHandle | None = None
        self._federate_ambassador: FederateAmbassador | None = None
        self._callback_model: CallbackModel | None = None
        self._callbacks_enabled = True
        self._evoked_callback_queue: list[QueuedCallback] = []
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
        self._subscribed_object_update_rates: dict[str, dict[str, float]] = {}
        self._subscribed_object_update_rate_designators: dict[str, dict[str, str]] = {}
        self._last_reflect_logical_times: dict[tuple[int, str], float] = {}
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
        return federation_connect(self, federateAmbassador, callbackModel, configuration, credentials)

    def disconnect(self) -> None:
        self._record("disconnect")
        federation_disconnect(self)

    def forceConnectionLost(self, faultDescription: str = "simulated connection lost") -> None:  # noqa: N802
        """Test harness hook for injecting a non-orderly connection loss."""

        self._record("forceConnectionLost", faultDescription)
        self._require_connected("forceConnectionLost")
        force_connection_lost(self, faultDescription)

    def force_connection_lost(self, fault_description: str = "simulated connection lost") -> None:
        self.forceConnectionLost(fault_description)

    def forceFederateLoss(  # noqa: N802
        self,
        federate: Any,
        faultDescription: str = "simulated federate fault",
    ) -> None:
        """Test harness hook for injecting a non-orderly loss into another joined federate."""

        self._record("forceFederateLoss", federate, faultDescription)
        self._require_joined("forceFederateLoss")
        force_federate_loss(self, federate, faultDescription)

    def force_federate_loss(
        self,
        federate: Any,
        fault_description: str = "simulated federate fault",
    ) -> None:
        self.forceFederateLoss(federate, fault_description)

    def createFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecution", *args, **kwargs)
        self._require_connected("createFederationExecution")
        create_federation_execution(self, *args, **kwargs)

    def createFederationExecutionWithMIM(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecutionWithMIM", *args, **kwargs)
        self._require_connected("createFederationExecutionWithMIM")
        create_federation_execution_with_mim(self, *args, **kwargs)

    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("destroyFederationExecution", *args, **kwargs)
        self._require_connected("destroyFederationExecution")
        destroy_federation_execution(self, *args, **kwargs)

    def listFederationExecutions(self) -> None:  # noqa: N802
        self._record("listFederationExecutions")
        self._require_connected("listFederationExecutions")
        list_federation_executions(self)

    def listFederationExecutionMembers(self, federationName: str) -> None:  # noqa: N802
        self._record("listFederationExecutionMembers", federationName)
        self._require_connected("listFederationExecutionMembers")
        list_federation_execution_members(self, federationName)

    def joinFederationExecution(self, *args: Any, **kwargs: Any):  # noqa: N802
        self._record("joinFederationExecution", *args, **kwargs)
        self._require_connected("joinFederationExecution")
        return join_federation_execution(self, *args, **kwargs)

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        self._record("resignFederationExecution", resignAction)
        self._require_joined("resignFederationExecution")
        resign_federation_execution(self, resignAction)

    def registerFederationSynchronizationPoint(  # noqa: N802
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: Any | None = None,
    ) -> None:
        self._record("registerFederationSynchronizationPoint", synchronizationPointLabel, userSuppliedTag, synchronizationSet)
        self._require_joined("registerFederationSynchronizationPoint")
        register_federation_synchronization_point(self, synchronizationPointLabel, userSuppliedTag, synchronizationSet)

    def synchronizationPointAchieved(self, synchronizationPointLabel: str, successfully: bool = True) -> None:  # noqa: N802
        self._record("synchronizationPointAchieved", synchronizationPointLabel, successfully)
        self._require_joined("synchronizationPointAchieved")
        synchronization_point_achieved(self, synchronizationPointLabel, successfully)

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        self._record("evokeCallback", approximateMinimumTimeInSeconds)
        self._require_connected("evokeCallback")
        return evoke_callback(self)

    def evokeMultipleCallbacks(  # noqa: N802
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        self._record("evokeMultipleCallbacks", approximateMinimumTimeInSeconds, approximateMaximumTimeInSeconds)
        self._require_connected("evokeMultipleCallbacks")
        return evoke_multiple_callbacks(self)

    def enableCallbacks(self) -> None:  # noqa: N802
        self._record("enableCallbacks")
        self._require_connected("enableCallbacks")
        enable_callbacks(self)

    def disableCallbacks(self) -> None:  # noqa: N802
        self._record("disableCallbacks")
        self._require_connected("disableCallbacks")
        disable_callbacks(self)

    def requestFederationSave(self, label: str, time: Any | None = None) -> None:  # noqa: N802
        self._record("requestFederationSave", label, time)
        self._require_joined("requestFederationSave")
        request_federation_save(self, label, time)

    def _start_federation_save(
        self,
        federation: _FederationRecord,
        label: str,
        save_time: Any | None,
    ) -> None:
        start_federation_save(self, federation, label, save_time)

    def _process_scheduled_save(self, federation: _FederationRecord) -> None:
        process_scheduled_save(self, federation)

    def federateSaveBegun(self) -> None:  # noqa: N802
        self._record("federateSaveBegun")
        self._require_joined("federateSaveBegun")
        federate_save_begun(self)

    def federateSaveComplete(self) -> None:  # noqa: N802
        self._record("federateSaveComplete")
        complete_save(self, success=True)

    def federateSaveNotComplete(self) -> None:  # noqa: N802
        self._record("federateSaveNotComplete")
        complete_save(self, success=False)

    def abortFederationSave(self) -> None:  # noqa: N802
        self._record("abortFederationSave")
        self._require_joined("abortFederationSave")
        abort_federation_save(self)

    def queryFederationSaveStatus(self) -> None:  # noqa: N802
        self._record("queryFederationSaveStatus")
        self._require_joined("queryFederationSaveStatus")
        query_federation_save_status(self)

    def requestFederationRestore(self, label: str) -> None:  # noqa: N802
        self._record("requestFederationRestore", label)
        self._require_joined("requestFederationRestore")
        request_federation_restore(self, label)

    def federateRestoreComplete(self) -> None:  # noqa: N802
        self._record("federateRestoreComplete")
        complete_restore(self, success=True)

    def federateRestoreNotComplete(self) -> None:  # noqa: N802
        self._record("federateRestoreNotComplete")
        complete_restore(self, success=False)

    def abortFederationRestore(self) -> None:  # noqa: N802
        self._record("abortFederationRestore")
        self._require_joined("abortFederationRestore")
        abort_federation_restore(self)

    def queryFederationRestoreStatus(self) -> None:  # noqa: N802
        self._record("queryFederationRestoreStatus")
        self._require_joined("queryFederationRestoreStatus")
        query_federation_restore_status(self)

    def enableTimeRegulation(self, lookahead: Any) -> None:  # noqa: N802
        self._record("enableTimeRegulation", lookahead)
        self._require_joined("enableTimeRegulation")
        enable_time_regulation(self, lookahead)

    def disableTimeRegulation(self) -> None:  # noqa: N802
        self._record("disableTimeRegulation")
        self._require_joined("disableTimeRegulation")
        disable_time_regulation(self)

    def enableTimeConstrained(self) -> None:  # noqa: N802
        self._record("enableTimeConstrained")
        self._require_joined("enableTimeConstrained")
        enable_time_constrained(self)

    def disableTimeConstrained(self) -> None:  # noqa: N802
        self._record("disableTimeConstrained")
        self._require_joined("disableTimeConstrained")
        disable_time_constrained(self)

    def enableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("enableAsynchronousDelivery")
        self._require_joined("enableAsynchronousDelivery")
        enable_asynchronous_delivery(self)

    def disableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("disableAsynchronousDelivery")
        self._require_joined("disableAsynchronousDelivery")
        disable_asynchronous_delivery(self)

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
        modify_lookahead(self, lookahead)

    def retract(self, retraction: Any) -> None:
        self._record("retract", retraction)
        self._require_joined("retract")
        retract_message(self, retraction)

    def queryLookahead(self) -> Any:  # noqa: N802
        self._record("queryLookahead")
        self._require_joined("queryLookahead")
        return query_lookahead(self)

    def _request_time_advance(self, mode: str, time: Any) -> None:
        request_time_advance(
            self,
            mode,
            time,
            logical_time_already_passed_exc=LogicalTimeAlreadyPassed,
        )

    def _process_time_advances(self) -> None:
        process_time_advances(self)

    def _try_grant_pending_time_advance(self) -> bool:
        return try_grant_pending_time_advance(self)

    def _time_management_state(self) -> Any:
        return build_time_management_state(self)

    def _time_management_federation(self, federation: _FederationRecord) -> Any:
        return build_time_management_federation(federation)

    def _query_galt_for(self, target: "Python2025RTIAmbassador") -> TimeQueryReturn:
        return query_galt_for(target)

    def _query_lits_for(self, target: "Python2025RTIAmbassador") -> TimeQueryReturn:
        return query_lits_for(target)

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        validate_tso_send_time(self, timestamp, invalid_logical_time_exc=InvalidLogicalTime)

    def _deliver_due_tso_callbacks_for_request(self, deliverable_messages: tuple[Any, ...]) -> None:
        deliver_due_tso_callbacks_for_request(self, deliverable_messages)

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle:  # noqa: N802
        self._record("getObjectClassHandle", objectClassName)
        self._require_joined("getObjectClassHandle")
        return get_object_class_handle(self, objectClassName)

    def getObjectClassName(self, objectClass: Any) -> str:  # noqa: N802
        self._record("getObjectClassName", objectClass)
        return get_object_class_name(self, objectClass)

    def getAttributeHandle(self, objectClass: Any, attributeName: str) -> AttributeHandle:  # noqa: N802
        self._record("getAttributeHandle", objectClass, attributeName)
        return get_attribute_handle(self, objectClass, attributeName)

    def getAttributeName(self, objectClass: Any, attribute: Any) -> str:  # noqa: N802
        self._record("getAttributeName", objectClass, attribute)
        return get_attribute_name(self, objectClass, attribute)

    def getInteractionClassHandle(self, interactionClassName: str) -> InteractionClassHandle:  # noqa: N802
        self._record("getInteractionClassHandle", interactionClassName)
        self._require_joined("getInteractionClassHandle")
        return get_interaction_class_handle(self, interactionClassName)

    def getInteractionClassName(self, interactionClass: Any) -> str:  # noqa: N802
        self._record("getInteractionClassName", interactionClass)
        return get_interaction_class_name(self, interactionClass)

    def getParameterHandle(self, interactionClass: Any, parameterName: str) -> ParameterHandle:  # noqa: N802
        self._record("getParameterHandle", interactionClass, parameterName)
        return get_parameter_handle(self, interactionClass, parameterName)

    def getParameterName(self, interactionClass: Any, parameter: Any) -> str:  # noqa: N802
        self._record("getParameterName", interactionClass, parameter)
        return get_parameter_name(self, interactionClass, parameter)

    def publishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("publishObjectClassAttributes", objectClass, attributes)
        self._require_joined("publishObjectClassAttributes")
        publish_object_class_attributes(self, objectClass, attributes)

    def unpublishObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClass", objectClass)
        self._require_joined("unpublishObjectClass")
        unpublish_object_class(self, objectClass)

    def unpublishObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unpublishObjectClassAttributes", objectClass, attributes)
        self._require_joined("unpublishObjectClassAttributes")
        unpublish_object_class_attributes(self, objectClass, attributes)

    def subscribeObjectClassAttributes(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributes", objectClass, attributes, *unused)
        self._require_joined("subscribeObjectClassAttributes")
        subscribe_object_class_attributes(self, objectClass, attributes, *unused)

    def subscribeObjectClassAttributesPassively(self, objectClass: Any, attributes: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassively", objectClass, attributes, *unused)
        self.subscribeObjectClassAttributes(objectClass, attributes, *unused)

    def unsubscribeObjectClass(self, objectClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClass", objectClass)
        self._require_joined("unsubscribeObjectClass")
        unsubscribe_object_class(self, objectClass)

    def unsubscribeObjectClassAttributes(self, objectClass: Any, attributes: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributes", objectClass, attributes)
        self._require_joined("unsubscribeObjectClassAttributes")
        unsubscribe_object_class_attributes(self, objectClass, attributes)

    def publishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("publishInteractionClass", interactionClass)
        self._require_joined("publishInteractionClass")
        publish_interaction_class(self, interactionClass)

    def unpublishInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unpublishInteractionClass", interactionClass)
        self._require_joined("unpublishInteractionClass")
        unpublish_interaction_class(self, interactionClass)

    def subscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClass", interactionClass)
        self._require_joined("subscribeInteractionClass")
        subscribe_interaction_class(self, interactionClass)

    def subscribeInteractionClassPassively(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassively", interactionClass)
        self.subscribeInteractionClass(interactionClass)

    def unsubscribeInteractionClass(self, interactionClass: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClass", interactionClass)
        self._require_joined("unsubscribeInteractionClass")
        unsubscribe_interaction_class(self, interactionClass)

    def subscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("subscribeInteractionClassWithRegions")
        subscribe_interaction_class_with_regions(self, interactionClass, regions)

    def subscribeInteractionClassPassivelyWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("subscribeInteractionClassPassivelyWithRegions", interactionClass, regions)
        self.subscribeInteractionClassWithRegions(interactionClass, regions)

    def unsubscribeInteractionClassWithRegions(self, interactionClass: Any, regions: Any) -> None:  # noqa: N802
        self._record("unsubscribeInteractionClassWithRegions", interactionClass, regions)
        self._require_joined("unsubscribeInteractionClassWithRegions")
        unsubscribe_interaction_class_with_regions(self, interactionClass, regions)

    def publishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("publishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("publishObjectClassDirectedInteractions")
        publish_object_class_directed_interactions(self, objectClass, interactionClasses)

    def unpublishObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unpublishObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unpublishObjectClassDirectedInteractions")
        unpublish_object_class_directed_interactions(self, objectClass, interactionClasses)

    def subscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("subscribeObjectClassDirectedInteractions")
        subscribe_object_class_directed_interactions(self, objectClass, interactionClasses)

    def subscribeObjectClassDirectedInteractionsUniversally(self, objectClass: Any, interactionClasses: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassDirectedInteractionsUniversally", objectClass, interactionClasses)
        self.subscribeObjectClassDirectedInteractions(objectClass, interactionClasses)

    def unsubscribeObjectClassDirectedInteractions(self, objectClass: Any, interactionClasses: Any | None = None) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassDirectedInteractions", objectClass, interactionClasses)
        self._require_joined("unsubscribeObjectClassDirectedInteractions")
        unsubscribe_object_class_directed_interactions(self, objectClass, interactionClasses)

    def getTransportationTypeHandle(self, transportationTypeName: str) -> TransportationTypeHandle:  # noqa: N802
        self._record("getTransportationTypeHandle", transportationTypeName)
        self._require_joined("getTransportationTypeHandle")
        return get_transportation_type_handle(self, transportationTypeName)

    def getTransportationTypeName(self, transportationType: Any) -> str:  # noqa: N802
        self._record("getTransportationTypeName", transportationType)
        return get_transportation_type_name(self, transportationType)

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle:  # noqa: N802
        self._record("getDimensionHandle", dimensionName)
        self._require_joined("getDimensionHandle")
        return get_dimension_handle(self, dimensionName)

    def getDimensionName(self, dimension: Any) -> str:  # noqa: N802
        self._record("getDimensionName", dimension)
        return get_dimension_name(self, dimension)

    def getDimensionUpperBound(self, dimension: Any) -> int:  # noqa: N802
        self._record("getDimensionUpperBound", dimension)
        return get_dimension_upper_bound(self, dimension)

    def getAvailableDimensionsForObjectClass(self, objectClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForObjectClass", objectClass)
        return get_available_dimensions_for_object_class(self, objectClass)

    def getAvailableDimensionsForInteractionClass(self, interactionClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForInteractionClass", interactionClass)
        return get_available_dimensions_for_interaction_class(self, interactionClass)

    def createRegion(self, dimensions: Any) -> RegionHandle:  # noqa: N802
        self._record("createRegion", dimensions)
        self._require_joined("createRegion")
        return create_region(self, dimensions)

    def commitRegionModifications(self, regions: Any) -> None:  # noqa: N802
        self._record("commitRegionModifications", regions)
        self._require_joined("commitRegionModifications")
        commit_region_modifications(self, regions)

    def deleteRegion(self, region: Any) -> None:  # noqa: N802
        self._record("deleteRegion", region)
        self._require_joined("deleteRegion")
        delete_region(self, region)

    def getDimensionHandleSet(self, region: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getDimensionHandleSet", region)
        return get_dimension_handle_set(self, region)

    def getRangeBounds(self, region: Any, dimension: Any) -> RangeBounds:  # noqa: N802
        self._record("getRangeBounds", region, dimension)
        return get_range_bounds(self, region, dimension)

    def setRangeBounds(self, region: Any, dimension: Any, rangeBounds: Any) -> None:  # noqa: N802
        self._record("setRangeBounds", region, dimension, rangeBounds)
        set_range_bounds(self, region, dimension, rangeBounds)

    def subscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions, *unused)
        self._require_joined("subscribeObjectClassAttributesWithRegions")
        subscribe_object_class_attributes_with_regions(self, objectClass, attributesAndRegions)

    def subscribeObjectClassAttributesPassivelyWithRegions(self, objectClass: Any, attributesAndRegions: Any, *unused: Any) -> None:  # noqa: N802
        self._record("subscribeObjectClassAttributesPassivelyWithRegions", objectClass, attributesAndRegions, *unused)
        self.subscribeObjectClassAttributesWithRegions(objectClass, attributesAndRegions, *unused)

    def unsubscribeObjectClassAttributesWithRegions(self, objectClass: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unsubscribeObjectClassAttributesWithRegions", objectClass, attributesAndRegions)
        self._require_joined("unsubscribeObjectClassAttributesWithRegions")
        unsubscribe_object_class_attributes_with_regions(self, objectClass, attributesAndRegions)

    def registerObjectInstanceWithRegions(self, objectClass: Any, attributesAndRegions: Any, objectInstanceName: str | None = None) -> ObjectInstanceHandle:  # noqa: N802
        self._record("registerObjectInstanceWithRegions", objectClass, attributesAndRegions, objectInstanceName)
        return register_object_instance_with_regions(self, objectClass, attributesAndRegions, objectInstanceName)

    def associateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("associateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("associateRegionsForUpdates")
        associate_regions_for_updates(self, objectInstance, attributesAndRegions)

    def unassociateRegionsForUpdates(self, objectInstance: Any, attributesAndRegions: Any) -> None:  # noqa: N802
        self._record("unassociateRegionsForUpdates", objectInstance, attributesAndRegions)
        self._require_joined("unassociateRegionsForUpdates")
        unassociate_regions_for_updates(self, objectInstance, attributesAndRegions)

    def changeDefaultAttributeTransportationType(  # noqa: N802
        self,
        objectClass: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("changeDefaultAttributeTransportationType", objectClass, attributes, transportationType)
        change_default_attribute_transportation_type(self, objectClass, attributes, transportationType)

    def changeDefaultAttributeOrderType(self, objectClass: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeDefaultAttributeOrderType", objectClass, attributes, orderType)
        change_default_attribute_order_type(self, objectClass, attributes, orderType)

    def changeAttributeOrderType(self, objectInstance: Any, attributes: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeAttributeOrderType", objectInstance, attributes, orderType)
        self._require_joined("changeAttributeOrderType")
        change_attribute_order_type(self, objectInstance, attributes, orderType)

    def changeInteractionOrderType(self, interactionClass: Any, orderType: Any) -> None:  # noqa: N802
        self._record("changeInteractionOrderType", interactionClass, orderType)
        self._require_joined("changeInteractionOrderType")
        change_interaction_order_type(self, interactionClass, orderType)

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
        return serialize_mom_service_report(
            self,
            serviceName,
            success=success,
            exception=exception,
            arguments=arguments,
            returned=returned,
            result=result,
        )

    def serviceReportRecordsSnapshot(self) -> tuple[dict[str, Any], ...]:  # noqa: N802
        self._record("serviceReportRecordsSnapshot")
        self._require_joined("serviceReportRecordsSnapshot")
        return service_report_records_snapshot(self)

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("reserveObjectInstanceName", objectInstanceName)
        self._require_joined("reserveObjectInstanceName")
        self._require_no_save_or_restore("reserveObjectInstanceName")
        reserve_object_instance_name(self, objectInstanceName)

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None:  # noqa: N802
        self._record("releaseObjectInstanceName", objectInstanceName)
        self._require_joined("releaseObjectInstanceName")
        self._require_no_save_or_restore("releaseObjectInstanceName")
        release_object_instance_name(self, objectInstanceName)

    def reserveMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("reserveMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("reserveMultipleObjectInstanceNames")
        self._require_no_save_or_restore("reserveMultipleObjectInstanceNames")
        reserve_multiple_object_instance_names(self, objectInstanceNames)

    def releaseMultipleObjectInstanceNames(self, objectInstanceNames: Any) -> None:  # noqa: N802
        self._record("releaseMultipleObjectInstanceNames", objectInstanceNames)
        self._require_joined("releaseMultipleObjectInstanceNames")
        self._require_no_save_or_restore("releaseMultipleObjectInstanceNames")
        release_multiple_object_instance_names(self, objectInstanceNames)

    def reserve_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self.reserveMultipleObjectInstanceNames(object_instance_names)

    def release_multiple_object_instance_name(self, object_instance_names: Any) -> None:
        self.releaseMultipleObjectInstanceNames(object_instance_names)

    def reserve_multiple_object_instance_names(self, object_instance_names: Any) -> None:
        self.reserveMultipleObjectInstanceNames(object_instance_names)

    def release_multiple_object_instance_names(self, object_instance_names: Any) -> None:
        self.releaseMultipleObjectInstanceNames(object_instance_names)

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
        return register_object_instance(self, objectClass, objectInstanceName)

    def updateAttributeValues(  # noqa: N802
        self,
        objectInstance: Any,
        attributeValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("updateAttributeValues", objectInstance, attributeValues, userSuppliedTag, time)
        self._require_joined("updateAttributeValues")
        return update_attribute_values(self, objectInstance, attributeValues, userSuppliedTag, time)

    def sendInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendInteraction", interactionClass, parameterValues, userSuppliedTag, time)
        self._require_joined("sendInteraction")
        return send_interaction(self, interactionClass, parameterValues, userSuppliedTag, time)

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
        return send_interaction_with_regions(self, interactionClass, parameterValues, regions, userSuppliedTag, time)

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
        return send_directed_interaction(self, interactionClass, objectInstance, parameterValues, userSuppliedTag, time)

    def deleteObjectInstance(  # noqa: N802
        self,
        objectInstance: Any,
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("deleteObjectInstance", objectInstance, userSuppliedTag, time)
        self._require_joined("deleteObjectInstance")
        return delete_object_instance(self, objectInstance, userSuppliedTag, time)

    def localDeleteObjectInstance(self, objectInstance: Any) -> None:  # noqa: N802
        self._record("localDeleteObjectInstance", objectInstance)
        self._require_joined("localDeleteObjectInstance")
        local_delete_object_instance(self, objectInstance)

    def requestAttributeValueUpdate(self, objectClassOrInstance: Any, attributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("requestAttributeValueUpdate", objectClassOrInstance, attributes, userSuppliedTag)
        self._require_joined("requestAttributeValueUpdate")
        request_attribute_value_update(self, objectClassOrInstance, attributes, userSuppliedTag)

    def requestAttributeTransportationTypeChange(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("requestAttributeTransportationTypeChange", objectInstance, attributes, transportationType)
        self._require_joined("requestAttributeTransportationTypeChange")
        self._require_no_save_or_restore("requestAttributeTransportationTypeChange")
        request_attribute_transportation_type_change(self, objectInstance, attributes, transportationType)

    def queryAttributeTransportationType(self, objectInstance: Any, attribute: Any) -> None:  # noqa: N802
        self._record("queryAttributeTransportationType", objectInstance, attribute)
        self._require_joined("queryAttributeTransportationType")
        self._require_no_save_or_restore("queryAttributeTransportationType")
        query_attribute_transportation_type(self, objectInstance, attribute)

    def requestInteractionTransportationTypeChange(self, interactionClass: Any, transportationType: Any) -> None:  # noqa: N802
        self._record("requestInteractionTransportationTypeChange", interactionClass, transportationType)
        self._require_joined("requestInteractionTransportationTypeChange")
        self._require_no_save_or_restore("requestInteractionTransportationTypeChange")
        request_interaction_transportation_type_change(self, interactionClass, transportationType)

    def queryInteractionTransportationType(self, federate: Any, interactionClass: Any) -> None:  # noqa: N802
        self._record("queryInteractionTransportationType", federate, interactionClass)
        self._require_joined("queryInteractionTransportationType")
        self._require_no_save_or_restore("queryInteractionTransportationType")
        query_interaction_transportation_type(self, federate, interactionClass)

    def unconditionalAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("unconditionalAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("unconditionalAttributeOwnershipDivestiture")
        unconditional_attribute_ownership_divestiture(self, objectInstance, attributes, userSuppliedTag)

    def negotiatedAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("negotiatedAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("negotiatedAttributeOwnershipDivestiture")
        negotiated_attribute_ownership_divestiture(self, objectInstance, attributes, userSuppliedTag)

    def confirmDivestiture(self, objectInstance: Any, confirmedAttributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("confirmDivestiture", objectInstance, confirmedAttributes, userSuppliedTag)
        self._require_joined("confirmDivestiture")
        confirm_divestiture(self, objectInstance, confirmedAttributes, userSuppliedTag)

    def attributeOwnershipAcquisition(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisition", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisition")
        attribute_ownership_acquisition(self, objectInstance, desiredAttributes, userSuppliedTag)

    def attributeOwnershipAcquisitionIfAvailable(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisitionIfAvailable", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisitionIfAvailable")
        attribute_ownership_acquisition_if_available(self, objectInstance, desiredAttributes, userSuppliedTag)

    def attributeOwnershipReleaseDenied(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("attributeOwnershipReleaseDenied", objectInstance, attributes)
        self._require_joined("attributeOwnershipReleaseDenied")
        attribute_ownership_release_denied(self, objectInstance, attributes)

    def attributeOwnershipDivestitureIfWanted(self, objectInstance: Any, attributes: Any) -> set[AttributeHandle]:  # noqa: N802
        self._record("attributeOwnershipDivestitureIfWanted", objectInstance, attributes)
        self._require_joined("attributeOwnershipDivestitureIfWanted")
        return attribute_ownership_divestiture_if_wanted(self, objectInstance, attributes)

    def cancelNegotiatedAttributeOwnershipDivestiture(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelNegotiatedAttributeOwnershipDivestiture", objectInstance, attributes)
        self._require_joined("cancelNegotiatedAttributeOwnershipDivestiture")
        cancel_negotiated_attribute_ownership_divestiture(self, objectInstance, attributes)

    def cancelAttributeOwnershipAcquisition(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelAttributeOwnershipAcquisition", objectInstance, attributes)
        self._require_joined("cancelAttributeOwnershipAcquisition")
        cancel_attribute_ownership_acquisition(self, objectInstance, attributes)

    def queryAttributeOwnership(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("queryAttributeOwnership", objectInstance, attributes)
        self._require_joined("queryAttributeOwnership")
        query_attribute_ownership(self, objectInstance, attributes)

    def query_attribute_ownership(self, object_instance: Any, attributes: Any) -> None:
        normalized_attributes = attributes
        try:
            iter(attributes)
        except TypeError:
            normalized_attributes = {attributes}
        self.queryAttributeOwnership(object_instance, normalized_attributes)

    def isAttributeOwnedByFederate(self, objectInstance: Any, attribute: Any) -> bool:  # noqa: N802
        self._record("isAttributeOwnedByFederate", objectInstance, attribute)
        self._require_joined("isAttributeOwnedByFederate")
        return is_attribute_owned_by_federate(self, objectInstance, attribute)

    def getFederateHandle(self, federateName: str) -> FederateHandle:  # noqa: N802
        self._record("getFederateHandle", federateName)
        self._require_joined("getFederateHandle")
        return get_federate_handle(self, federateName)

    def getFederateName(self, federate: Any) -> str:  # noqa: N802
        self._record("getFederateName", federate)
        self._require_joined("getFederateName")
        return get_federate_name(self, federate)

    def getKnownObjectClassHandle(self, objectInstance: Any) -> ObjectClassHandle:  # noqa: N802
        self._record("getKnownObjectClassHandle", objectInstance)
        self._require_joined("getKnownObjectClassHandle")
        return get_known_object_class_handle(self, objectInstance)

    def getObjectInstanceHandle(self, objectInstanceName: str) -> ObjectInstanceHandle:  # noqa: N802
        self._record("getObjectInstanceHandle", objectInstanceName)
        self._require_joined("getObjectInstanceHandle")
        return get_object_instance_handle(self, objectInstanceName)

    def getObjectInstanceName(self, objectInstance: Any) -> str:  # noqa: N802
        self._record("getObjectInstanceName", objectInstance)
        self._require_joined("getObjectInstanceName")
        return get_object_instance_name(self, objectInstance)

    def getOrderType(self, orderTypeName: str) -> OrderType:  # noqa: N802
        self._record("getOrderType", orderTypeName)
        self._require_joined("getOrderType")
        return get_order_type(self, orderTypeName)

    def getOrderName(self, orderType: Any) -> str:  # noqa: N802
        self._record("getOrderName", orderType)
        self._require_joined("getOrderName")
        return get_order_name(self, orderType)

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:  # noqa: N802
        self._record("getUpdateRateValue", updateRateDesignator)
        self._require_joined("getUpdateRateValue")
        return get_update_rate_value(
            self,
            updateRateDesignator,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def getUpdateRateValueForAttribute(self, theObject: Any, theAttribute: Any) -> float:  # noqa: N802
        self._record("getUpdateRateValueForAttribute", theObject, theAttribute)
        self._require_joined("getUpdateRateValueForAttribute")
        record = self._object_instance_record(theObject)
        attribute_name = self._attribute_name_by_handle(record.object_class_name, theAttribute)
        return self._subscribed_update_rate_for_attribute(
            self._current_federate_key(),
            record.object_class_name,
            attribute_name,
        )

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:  # noqa: N802
        self._record("getAttributeHandleFactory")
        self._require_connected("getAttributeHandleFactory")
        return make_attribute_handle_factory()

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:  # noqa: N802
        self._record("getAttributeHandleSetFactory")
        self._require_connected("getAttributeHandleSetFactory")
        return make_attribute_handle_set_factory()

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:  # noqa: N802
        self._record("getAttributeHandleValueMapFactory")
        self._require_connected("getAttributeHandleValueMapFactory")
        return make_attribute_handle_value_map_factory()

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:  # noqa: N802
        self._record("getAttributeSetRegionSetPairListFactory")
        self._require_connected("getAttributeSetRegionSetPairListFactory")
        return make_attribute_set_region_set_pair_list_factory()

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:  # noqa: N802
        self._record("getDimensionHandleFactory")
        self._require_connected("getDimensionHandleFactory")
        return make_dimension_handle_factory()

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:  # noqa: N802
        self._record("getDimensionHandleSetFactory")
        self._require_connected("getDimensionHandleSetFactory")
        return make_dimension_handle_set_factory()

    def getFederateHandleFactory(self) -> FederateHandleFactory:  # noqa: N802
        self._record("getFederateHandleFactory")
        self._require_connected("getFederateHandleFactory")
        return make_federate_handle_factory()

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:  # noqa: N802
        self._record("getFederateHandleSetFactory")
        self._require_connected("getFederateHandleSetFactory")
        return make_federate_handle_set_factory()

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:  # noqa: N802
        self._record("getInteractionClassHandleFactory")
        self._require_connected("getInteractionClassHandleFactory")
        return make_interaction_class_handle_factory()

    def getInteractionClassHandleSetFactory(self) -> InteractionClassHandleSetFactory:  # noqa: N802
        self._record("getInteractionClassHandleSetFactory")
        self._require_connected("getInteractionClassHandleSetFactory")
        return make_interaction_class_handle_set_factory()

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:  # noqa: N802
        self._record("getObjectClassHandleFactory")
        self._require_connected("getObjectClassHandleFactory")
        return make_object_class_handle_factory()

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:  # noqa: N802
        self._record("getObjectInstanceHandleFactory")
        self._require_connected("getObjectInstanceHandleFactory")
        return make_object_instance_handle_factory()

    def getParameterHandleFactory(self) -> ParameterHandleFactory:  # noqa: N802
        self._record("getParameterHandleFactory")
        self._require_connected("getParameterHandleFactory")
        return make_parameter_handle_factory()

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:  # noqa: N802
        self._record("getParameterHandleValueMapFactory")
        self._require_connected("getParameterHandleValueMapFactory")
        return make_parameter_handle_value_map_factory()

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:  # noqa: N802
        self._record("getRegionHandleSetFactory")
        self._require_connected("getRegionHandleSetFactory")
        return make_region_handle_set_factory()

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:  # noqa: N802
        self._record("getTransportationTypeHandleFactory")
        self._require_connected("getTransportationTypeHandleFactory")
        return make_transportation_type_handle_factory()

    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:  # noqa: N802
        self._record("decodeFederateHandle", encodedValue)
        self._require_connected("decodeFederateHandle")
        return runtime_decode_federate_handle(encodedValue, InvalidFederateHandle)

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:  # noqa: N802
        self._record("decodeObjectClassHandle", encodedValue)
        self._require_connected("decodeObjectClassHandle")
        return runtime_decode_object_class_handle(encodedValue, InvalidObjectClassHandle)

    def decodeInteractionClassHandle(self, encodedValue: bytes) -> InteractionClassHandle:  # noqa: N802
        self._record("decodeInteractionClassHandle", encodedValue)
        self._require_connected("decodeInteractionClassHandle")
        return runtime_decode_interaction_class_handle(encodedValue, InvalidInteractionClassHandle)

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:  # noqa: N802
        self._record("decodeObjectInstanceHandle", encodedValue)
        self._require_connected("decodeObjectInstanceHandle")
        return runtime_decode_object_instance_handle(encodedValue, InvalidObjectInstanceHandle)

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:  # noqa: N802
        self._record("decodeAttributeHandle", encodedValue)
        self._require_connected("decodeAttributeHandle")
        return runtime_decode_attribute_handle(encodedValue, InvalidAttributeHandle)

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:  # noqa: N802
        self._record("decodeParameterHandle", encodedValue)
        self._require_connected("decodeParameterHandle")
        return runtime_decode_parameter_handle(encodedValue, InvalidParameterHandle)

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:  # noqa: N802
        self._record("decodeDimensionHandle", encodedValue)
        self._require_connected("decodeDimensionHandle")
        return runtime_decode_dimension_handle(encodedValue, InvalidDimensionHandle)

    def decodeMessageRetractionHandle(self, encodedValue: bytes) -> MessageRetractionHandle:  # noqa: N802
        self._record("decodeMessageRetractionHandle", encodedValue)
        self._require_connected("decodeMessageRetractionHandle")
        return runtime_decode_message_retraction_handle(encodedValue, InvalidMessageRetractionHandle)

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:  # noqa: N802
        self._record("decodeRegionHandle", encodedValue)
        self._require_connected("decodeRegionHandle")
        return runtime_decode_region_handle(encodedValue, InvalidRegion)

    def getRegionHandleFactory(self) -> RegionHandleFactory:  # noqa: N802
        self._record("getRegionHandleFactory")
        self._require_connected("getRegionHandleFactory")
        return make_region_handle_factory()

    def getMessageRetractionHandleFactory(self) -> MessageRetractionHandleFactory:  # noqa: N802
        self._record("getMessageRetractionHandleFactory")
        self._require_connected("getMessageRetractionHandleFactory")
        return make_message_retraction_handle_factory()

    def getTimeFactory(self) -> Any:  # noqa: N802
        self._record("getTimeFactory")
        self._require_connected("getTimeFactory")
        return self._logical_time_factory

    def normalizeServiceGroup(self, serviceGroup: Any) -> int:  # noqa: N802
        self._record("normalizeServiceGroup", serviceGroup)
        self._require_joined("normalizeServiceGroup")
        return normalize_service_group(serviceGroup)

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
        return get_switch(self, "getObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory")

    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setObjectClassRelevanceAdvisorySwitch", value)
        set_switch(self, "setObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory", value)

    def getAttributeRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeRelevanceAdvisorySwitch")
        return get_switch(self, "getAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory")

    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeRelevanceAdvisorySwitch", value)
        set_switch(self, "setAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory", value)

    def getAttributeScopeAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeScopeAdvisorySwitch")
        return get_switch(self, "getAttributeScopeAdvisorySwitch", "attribute_scope_advisory")

    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeScopeAdvisorySwitch", value)
        set_attribute_scope_advisory_switch(self, value)

    def getInteractionRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getInteractionRelevanceAdvisorySwitch")
        return get_switch(self, "getInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory")

    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setInteractionRelevanceAdvisorySwitch", value)
        set_switch(self, "setInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory", value)

    def getConveyRegionDesignatorSetsSwitch(self) -> bool:  # noqa: N802
        self._record("getConveyRegionDesignatorSetsSwitch")
        return get_switch(self, "getConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets")

    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setConveyRegionDesignatorSetsSwitch", value)
        set_switch(self, "setConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets", value)

    def getAutomaticResignDirective(self) -> ResignAction:  # noqa: N802
        self._record("getAutomaticResignDirective")
        self._require_joined("getAutomaticResignDirective")
        return get_automatic_resign_directive(self)

    def setAutomaticResignDirective(self, value: ResignAction) -> None:  # noqa: N802
        self._record("setAutomaticResignDirective", value)
        self._require_joined("setAutomaticResignDirective")
        set_automatic_resign_directive(self, value)

    def getServiceReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getServiceReportingSwitch")
        return get_switch(self, "getServiceReportingSwitch", "service_reporting")

    def setServiceReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setServiceReportingSwitch", value)
        set_switch(self, "setServiceReportingSwitch", "service_reporting", value)

    def getExceptionReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getExceptionReportingSwitch")
        return get_switch(self, "getExceptionReportingSwitch", "exception_reporting")

    def setExceptionReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setExceptionReportingSwitch", value)
        set_switch(self, "setExceptionReportingSwitch", "exception_reporting", value)

    def getSendServiceReportsToFileSwitch(self) -> bool:  # noqa: N802
        self._record("getSendServiceReportsToFileSwitch")
        return get_switch(self, "getSendServiceReportsToFileSwitch", "send_service_reports_to_file")

    def setSendServiceReportsToFileSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setSendServiceReportsToFileSwitch", value)
        set_switch(self, "setSendServiceReportsToFileSwitch", "send_service_reports_to_file", value)

    def getAutoProvideSwitch(self) -> bool:  # noqa: N802
        self._record("getAutoProvideSwitch")
        return get_switch(self, "getAutoProvideSwitch", "auto_provide")

    def getDelaySubscriptionEvaluationSwitch(self) -> bool:  # noqa: N802
        self._record("getDelaySubscriptionEvaluationSwitch")
        return get_switch(self, "getDelaySubscriptionEvaluationSwitch", "delay_subscription_evaluation")

    def getAdvisoriesUseKnownClassSwitch(self) -> bool:  # noqa: N802
        self._record("getAdvisoriesUseKnownClassSwitch")
        return get_switch(self, "getAdvisoriesUseKnownClassSwitch", "advisories_use_known_class")

    def getAllowRelaxedDDMSwitch(self) -> bool:  # noqa: N802
        self._record("getAllowRelaxedDDMSwitch")
        return get_switch(self, "getAllowRelaxedDDMSwitch", "allow_relaxed_ddm")

    def getNonRegulatedGrantSwitch(self) -> bool:  # noqa: N802
        self._record("getNonRegulatedGrantSwitch")
        return get_switch(self, "getNonRegulatedGrantSwitch", "non_regulated_grant")

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

    def __enter__(self) -> "Python2025RTIAmbassador":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.close()
        return False

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name.startswith("_"):
            raise AttributeError(name)
        camel_name = snake_to_lower_camel(name)
        if camel_name != name:
            try:
                target = object.__getattribute__(self, camel_name)
            except AttributeError:
                target = None
            if callable(target):
                return lambda *args, **kwargs: target(*args, **kwargs)

        def _unsupported(*args: Any, **kwargs: Any) -> Any:
            self._record(name, *args, **kwargs)
            raise RTIinternalError(f"hla-backend-python2025 does not implement IEEE 1516.1-2025 service {name}")

        return _unsupported

    def _record(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((method_name, args, dict(kwargs)))

    def _deliver_callback(self, method_name: str, *args: Any) -> None:
        deliver_callback(self, method_name, *args)

    def _deliver_callback_now(self, method_name: str, *args: Any) -> None:
        deliver_callback_now(self, method_name, *args)

    def _deliver_to_federate_handle(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        deliver_to_federate_handle(self, federate_handle, method_name, *args)

    def _deliver_to_federate_handle_now(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        deliver_to_federate_handle_now(self, federate_handle, method_name, *args)

    def _deliver_queued_callback(self, queued: QueuedCallback) -> None:
        deliver_queued_callback(self, queued)

    def _deliver_mom_service_report(self, report: Mapping[str, Any]) -> None:
        deliver_mom_service_report(self, report)

    def _queue_tso_callback(
        self,
        target_federate: FederateHandle,
        callback_time: Any,
        method_name: str,
        *args: Any,
        exposed_retraction_handle: MessageRetractionHandle | None = None,
    ) -> MessageRetractionHandle:
        federation = self._federation_record()
        handle = MessageRetractionHandle(federation.next_message_retraction_handle)
        federation.next_message_retraction_handle += 1
        federation.queued_tso_callbacks[handle.value] = _QueuedTsoCallback(
            target_federate=target_federate,
            callback_time=callback_time,
            serial=handle.value,
            method_name=method_name,
            args=(*args, exposed_retraction_handle or handle),
        )
        self._process_time_advances()
        return handle

    @staticmethod
    def _register_retraction_group(
        federation: _FederationRecord,
        member_handles: Iterable[MessageRetractionHandle],
    ) -> MessageRetractionHandle:
        handles = tuple(member_handles)
        if not handles:
            return MessageRetractionHandle(0)
        canonical = handles[0]
        if len(handles) == 1:
            return canonical
        members = {handle.value for handle in handles}
        federation.retraction_groups[canonical.value] = members
        for handle in handles:
            federation.retraction_group_lookup[handle.value] = canonical.value
        return canonical

    @staticmethod
    def _resolve_retraction_group(
        federation: _FederationRecord,
        handle_value: int,
    ) -> tuple[int, set[int]]:
        if handle_value in federation.retraction_groups:
            return handle_value, set(federation.retraction_groups[handle_value])
        canonical = federation.retraction_group_lookup.get(handle_value)
        if canonical is None:
            return handle_value, {handle_value}
        return canonical, set(federation.retraction_groups.get(canonical, {handle_value}))

    @staticmethod
    def _drop_retraction_group_member(federation: _FederationRecord, handle_value: int) -> None:
        canonical = federation.retraction_group_lookup.get(handle_value)
        if canonical is None:
            return
        members = federation.retraction_groups.get(canonical)
        if members is None:
            federation.retraction_group_lookup.pop(handle_value, None)
            return
        members.discard(handle_value)
        federation.retraction_group_lookup.pop(handle_value, None)
        if members:
            federation.retraction_groups[canonical] = members
            return
        federation.retraction_groups.pop(canonical, None)

    @staticmethod
    def _finalize_retraction_group_if_inactive(federation: _FederationRecord, canonical_handle: int) -> None:
        members = federation.retraction_groups.get(canonical_handle)
        if members is None:
            return
        if any(member in federation.queued_tso_callbacks or member in federation.delivered_retraction_handles for member in members):
            return
        federation.retraction_groups.pop(canonical_handle, None)
        for member in tuple(federation.retraction_group_lookup):
            if federation.retraction_group_lookup.get(member) == canonical_handle:
                federation.retraction_group_lookup.pop(member, None)

    @classmethod
    def _canonicalize_retraction_handles(
        cls,
        federation: _FederationRecord,
        handles: list[MessageRetractionHandle],
    ) -> MessageRetractionHandle:
        canonical = cls._register_retraction_group(federation, handles)
        if len(handles) <= 1:
            return canonical
        for handle in handles[1:]:
            queued = federation.queued_tso_callbacks.get(handle.value)
            if queued is not None:
                queued.args = (*queued.args[:-1], canonical)
        return canonical

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
            raise RTIinternalError("2025 Python RTI ambassador requires a federation name")
        return federation_name

    def _extract_create_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federation_name = kwargs.get("federationName")
        if federation_name is None:
            federation_name = kwargs.get("federation_name")
        if federation_name is None and args:
            federation_name = args[0]
        if not isinstance(federation_name, str) or not federation_name:
            raise RTIinternalError("2025 Python RTI ambassador requires a federation name")
        return federation_name

    def _extract_join_names(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str, str | None]:
        federation_name = self._extract_federation_name(args, kwargs)
        federate_name = kwargs.get("federateName")
        if federate_name is None:
            federate_name = kwargs.get("federate_name")
        if federate_name is None and len(args) >= 3:
            federate_name = args[0]
        if federate_name is not None and not isinstance(federate_name, str):
            raise RTIinternalError("2025 Python RTI ambassador requires federateName to be a string when provided")
        return federation_name, federate_name

    def _extract_federate_type(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federate_type = kwargs.get("federateType")
        if federate_type is None:
            federate_type = kwargs.get("federate_type")
        if federate_type is None and len(args) >= 2:
            federate_type = args[1]
        if not isinstance(federate_type, str) or not federate_type:
            raise RTIinternalError("2025 Python RTI ambassador requires federateType to be a non-empty string")
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
            raise RTIinternalError("2025 Python RTI ambassador requires logicalTimeImplementationName to be a string")
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
            if isinstance(value, CallbackModel):
                return value
            member_name = getattr(value, "name", "")
            if member_name in CallbackModel.__members__:
                return CallbackModel[member_name]
            return CallbackModel(value)
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
        self._last_reflect_logical_times.clear()

    def _release_join(self) -> None:
        if self._federation_name is None:
            return
        self._pending_time_advance = None
        self._known_object_classes.clear()
        self._known_object_names.clear()
        self._locally_deleted_objects.clear()
        self._subscribed_object_update_rates.clear()
        self._subscribed_object_update_rate_designators.clear()
        self._last_reflect_logical_times.clear()
        federation = _FEDERATION_REGISTRY.get(self._federation_name)
        if federation is not None:
            if self._federate_name is not None:
                federation.members.pop(self._federate_name, None)
                federation.member_handles.pop(self._federate_name, None)
            if self._federate_handle is not None:
                self._prune_tso_state_for_departing_federate(federation, self._federate_handle)
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
            self._refresh_mom_federation_object()

    @staticmethod
    def _prune_tso_state_for_departing_federate(
        federation: _FederationRecord,
        federate_handle: FederateHandle,
    ) -> None:
        queued_for_target = [
            handle_value
            for handle_value, queued in federation.queued_tso_callbacks.items()
            if queued.target_federate == federate_handle
        ]
        for handle_value in queued_for_target:
            federation.queued_tso_callbacks.pop(handle_value, None)
            Python2025RTIAmbassador._drop_retraction_group_member(federation, handle_value)

        stale_delivered = [
            handle_value
            for handle_value, target in federation.delivered_retraction_targets.items()
            if target == federate_handle
        ]
        for handle_value in stale_delivered:
            federation.delivered_retraction_targets.pop(handle_value, None)
            federation.delivered_retraction_handles.discard(handle_value)
            Python2025RTIAmbassador._drop_retraction_group_member(federation, handle_value)

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
            if self._is_mom_object_class_name(record.object_class_name):
                continue
            if federate_handle in set(record.attribute_owners.values()):
                return True
        return False

    def _delete_objects_owned_by_resigning_federate(self) -> None:
        self._delete_objects_owned_by_specific_federate(self._current_federate_handle(), user_supplied_tag=b"")

    def _delete_objects_owned_by_specific_federate(
        self,
        federate_handle: FederateHandle,
        *,
        user_supplied_tag: bytes,
    ) -> None:
        federation = self._federation_record()
        for object_instance_value, record in tuple(federation.object_instances.items()):
            if self._is_mom_object_class_name(record.object_class_name):
                continue
            if federate_handle not in set(record.attribute_owners.values()):
                continue
            object_instance = ObjectInstanceHandle(object_instance_value)
            self._deliver_forced_remove_callbacks(object_instance, record, federate_handle, user_supplied_tag)
            if record.object_instance_name is not None:
                federation.object_instance_names.pop(record.object_instance_name, None)
            federation.object_instances.pop(object_instance_value, None)

    def _divest_resigning_federate_attributes(self) -> None:
        self._divest_attributes_owned_by_specific_federate(self._current_federate_handle())

    def _divest_attributes_owned_by_specific_federate(self, federate_handle: FederateHandle) -> None:
        for object_instance_value, record in tuple(self._federation_record().object_instances.items()):
            if self._is_mom_object_class_name(record.object_class_name):
                continue
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

    @staticmethod
    def _is_mom_object_class_name(object_class_name: str) -> bool:
        return ".HLAmanager." in object_class_name

    @staticmethod
    def _mom_runtime_federate_handle() -> FederateHandle:
        return FederateHandle(0)

    def _ensure_mom_objects(self) -> None:
        federation = self._federation_record()
        self._ensure_mom_federation_object(federation)
        for federate_name, federate_handle in sorted(
            federation.member_handles.items(),
            key=lambda item: item[1].value,
        ):
            self._ensure_mom_federate_object(
                federation,
                federate_name,
                federation.members.get(federate_name, ""),
                federate_handle,
            )
        self._refresh_mom_federation_object()
        for federate_name, federate_handle in sorted(
            federation.member_handles.items(),
            key=lambda item: item[1].value,
        ):
            self._refresh_mom_federate_object(
                federate_name,
                federation.members.get(federate_name, ""),
                federate_handle,
            )

    def _ensure_mom_federation_object(self, federation: _FederationRecord) -> None:
        class_name = "HLAobjectRoot.HLAmanager.HLAfederation"
        object_name = f"HLAmanager.HLAfederation.{self._federation_name}"
        if object_name in federation.object_instance_names:
            return
        self._register_internal_object_instance(
            class_name,
            object_name,
            producing_federate=self._mom_runtime_federate_handle(),
            owner_by_attribute={},
        )

    def _ensure_mom_federate_object(
        self,
        federation: _FederationRecord,
        federate_name: str,
        federate_type: str,
        federate_handle: FederateHandle,
    ) -> None:
        class_name = "HLAobjectRoot.HLAmanager.HLAfederate"
        object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{federate_name}"
        if object_name in federation.object_instance_names:
            return
        owner_by_attribute = {
            attribute_name: federate_handle
            for attribute_name in self._attribute_handles(class_name)
            if attribute_name in {"HLAfederateHandle", "HLAfederateName", "HLAfederateType"}
        }
        self._register_internal_object_instance(
            class_name,
            object_name,
            producing_federate=federate_handle,
            owner_by_attribute=owner_by_attribute,
        )

    def _register_internal_object_instance(
        self,
        object_class_name: str,
        object_instance_name: str,
        *,
        producing_federate: FederateHandle,
        owner_by_attribute: dict[str, FederateHandle | None],
    ) -> ObjectInstanceHandle:
        federation = self._federation_record()
        handle = ObjectInstanceHandle(federation.next_object_instance_handle)
        federation.next_object_instance_handle += 1
        federation.object_instances[handle.value] = _ObjectInstanceRecord(
            object_class_name=object_class_name,
            object_instance_name=object_instance_name,
            producing_federate=producing_federate,
            attribute_owners=dict(owner_by_attribute),
        )
        federation.object_instance_names[object_instance_name] = handle.value
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
                producing_federate.value,
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
                    object_instance_name,
                    producing_federate,
                )
        return handle

    def _refresh_mom_federation_object(self) -> None:
        federation = self._federation_record()
        object_name = f"HLAmanager.HLAfederation.{self._federation_name}"
        object_value = federation.object_instance_names.get(object_name)
        if object_value is None:
            return
        self._set_internal_object_attribute_values(
            ObjectInstanceHandle(object_value),
            {
                "HLAfederatesInFederation": ",".join(sorted(federation.members)),
            },
        )

    def _refresh_mom_federate_object(
        self,
        federate_name: str,
        federate_type: str,
        federate_handle: FederateHandle,
    ) -> None:
        federation = self._federation_record()
        object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{federate_name}"
        object_value = federation.object_instance_names.get(object_name)
        if object_value is None:
            return
        self._set_internal_object_attribute_values(
            ObjectInstanceHandle(object_value),
            {
                "HLAfederateHandle": str(federate_handle.value),
                "HLAfederateName": federate_name,
                "HLAfederateType": federate_type,
            },
        )

    def _set_internal_object_attribute_values(
        self,
        object_instance: ObjectInstanceHandle,
        attribute_values: Mapping[str, str | bytes],
    ) -> None:
        set_internal_object_attribute_values(self, object_instance, attribute_values)

    def _remove_current_federate_mom_object(self) -> None:
        federation = self._federation_record()
        federate_handle = self._current_federate_handle()
        if self._federate_name is None:
            return
        object_name = f"HLAmanager.HLAfederate.{federate_handle.value}.{self._federate_name}"
        object_value = federation.object_instance_names.pop(object_name, None)
        if object_value is None:
            return
        record = federation.object_instances.pop(object_value, None)
        if record is None:
            return
        for federate_key, subscriptions in federation.subscribed_object_attributes.items():
            if federate_key == federate_handle.value or record.object_class_name not in subscriptions:
                continue
            self._deliver_to_federate_handle(
                FederateHandle(federate_key),
                "removeObjectInstance",
                ObjectInstanceHandle(object_value),
                b"",
                federate_handle,
                None,
                OrderType.RECEIVE,
                OrderType.RECEIVE,
                None,
            )

    def _matching_object_publishers(
        self,
        federation: _FederationRecord,
        object_class_name: str,
        attribute_names: set[str],
    ) -> set[int]:
        return matching_object_publishers(federation, object_class_name, attribute_names)

    def _has_object_registration_interest(
        self,
        federation: _FederationRecord,
        publisher_key: int,
        object_class_name: str,
    ) -> bool:
        return has_object_registration_interest(federation, publisher_key, object_class_name)

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
        self._deliver_forced_remove_callbacks(object_instance, record, self._current_federate_handle(), b"")

    def _deliver_forced_remove_callbacks(
        self,
        object_instance: ObjectInstanceHandle,
        record: _ObjectInstanceRecord,
        producing_federate: FederateHandle,
        user_supplied_tag: bytes,
    ) -> None:
        deliver_forced_remove_callbacks(
            self,
            object_instance,
            record,
            producing_federate,
            user_supplied_tag,
        )

    def _evaluate_attribute_scope_advisories(self) -> None:
        evaluate_attribute_scope_advisories(self)

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

    @staticmethod
    def _object_instance_record_type() -> type[_ObjectInstanceRecord]:
        return _ObjectInstanceRecord

    @staticmethod
    def _invalid_object_instance_handle_type() -> type[Exception]:
        return InvalidObjectInstanceHandle

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
        return attribute_handles(self, object_class_name)

    def _parameter_handles(self, interaction_class_name: str) -> dict[str, int]:
        return parameter_handles(self, interaction_class_name)

    def _object_class_name(self, object_class: Any) -> str:
        return object_class_name(self, object_class)

    def _interaction_class_name(self, interaction_class: Any) -> str:
        return interaction_class_name(self, interaction_class)

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle:
        return transportation_handle_by_name(self, name)

    def _object_instance_record(self, object_instance: Any) -> _ObjectInstanceRecord:
        return object_instance_record(self, object_instance)

    def _object_instance_record_known(self, object_instance: Any) -> _ObjectInstanceRecord:
        return object_instance_record_known(self, object_instance)

    def _synchronization_required_federates(self, synchronization_set: Any | None) -> set[int]:
        return synchronization_required_federates(self, synchronization_set)

    def _handle_mom_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_interaction(self, interaction_class_name, values_by_handle)

    def _handle_mom_federate_request_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_federate_request_interaction(self, interaction_class_name, values_by_handle)

    def _send_mom_publication_reports(self, target_federate: FederateHandle) -> None:
        send_mom_publication_reports(self, target_federate)

    def _send_mom_subscription_reports(self, target_federate: FederateHandle) -> None:
        send_mom_subscription_reports(self, target_federate)

    def _send_mom_object_instance_information_report(
        self,
        target_federate: FederateHandle,
        object_instance: ObjectInstanceHandle,
    ) -> None:
        send_mom_object_instance_information_report(self, target_federate, object_instance)

    def _send_mom_object_class_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_class: Mapping[str, int],
        count_parameter_name: str,
    ) -> None:
        send_mom_object_class_count_report(self, report_name, target_federate, counts_by_class, count_parameter_name)

    def _send_mom_transport_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_transport: Mapping[str, Mapping[str, int]],
        count_parameter_name: str,
    ) -> None:
        send_mom_transport_count_report(self, report_name, target_federate, counts_by_transport, count_parameter_name)

    def _mom_deletable_object_counts(self, target_federate: FederateHandle) -> dict[str, int]:
        return mom_deletable_object_counts(self, target_federate)

    @staticmethod
    def _mom_counts_for_federate(counts: Mapping[tuple[int, str], int], target_federate: FederateHandle) -> dict[str, int]:
        return mom_counts_for_federate(counts, target_federate)

    @staticmethod
    def _mom_transport_counts_for_federate(
        counts: Mapping[tuple[int, str, str], int],
        target_federate: FederateHandle,
    ) -> dict[str, dict[str, int]]:
        return mom_transport_counts_for_federate(counts, target_federate)

    def _handle_mom_service_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_service_interaction(self, interaction_class_name, values_by_handle)

    def _handle_mom_adjust_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_adjust_interaction(self, interaction_class_name, values_by_handle)

    def _modify_mom_attribute_state(
        self,
        object_instance: ObjectInstanceHandle,
        attribute: AttributeHandle,
        ownership_state: str,
    ) -> None:
        modify_mom_attribute_state(self, object_instance, attribute, ownership_state)

    def _mom_request_params_by_name(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        return mom_request_params_by_name(self, interaction_class_name, values_by_handle)

    def _mom_target_rti(self, params: Mapping[str, bytes]) -> "Python2025RTIAmbassador":
        return mom_target_rti(self, params)

    @staticmethod
    def _mom_bool(value: bytes | None, default: bool) -> bool:
        return mom_bool(value, default)

    @staticmethod
    def _mom_int(value: bytes | None, field_name: str) -> int:
        return mom_int(value, field_name)

    @staticmethod
    def _mom_attribute_handles(value: bytes | None) -> set[AttributeHandle]:
        return mom_attribute_handles(value)

    @staticmethod
    def _mom_text(value: bytes | None, field_name: str) -> str:
        return mom_text(value, field_name)

    def _mom_transportation_handle(self, value: bytes | None, field_name: str) -> TransportationTypeHandle:
        return self.getTransportationTypeHandle(self._mom_text(value, field_name))

    def _mom_time(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_time(self._mom_number(value, field_name))

    def _mom_interval(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_interval(self._mom_number(value, field_name))

    @staticmethod
    def _mom_number(value: bytes | None, field_name: str) -> int | float:
        return mom_number(value, field_name)

    @staticmethod
    def _mom_handle_list_payload(values: Iterable[int]) -> bytes:
        return mom_handle_list_payload(values)

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
        return mom_ownership_state(value, field_name)

    @staticmethod
    def _mom_order_type(value: bytes | None, field_name: str) -> OrderType:
        return mom_order_type(value, field_name)

    @classmethod
    def _mom_resign_action(cls, value: bytes | None) -> ResignAction:
        return mom_resign_action(value)

    def _mom_request_report_values(
        self,
        request_name: str,
        report_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        return mom_request_report_values(self, request_name, report_name, values_by_handle)

    @staticmethod
    def _mom_index(value: bytes | None) -> int:
        return mom_index(value)

    def _mom_module_data(self, modules: tuple[Any, ...], indicator: int) -> str:
        return mom_module_data(modules, indicator)

    @staticmethod
    def _mom_single_module_data(module: Any | None) -> str:
        return mom_single_module_data(module)

    def _send_mom_report_interaction(self, report_name: str, values: Mapping[str, bytes]) -> None:
        send_mom_report_interaction(self, report_name, values)

    def _send_mom_exception_interaction(
        self,
        interaction_class_name: str,
        exception: Exception,
        *,
        parameter_error: bool,
    ) -> None:
        send_mom_exception_interaction(
            self,
            interaction_class_name,
            exception,
            parameter_error=parameter_error,
        )

    def _request_instance_attribute_value_update(self, object_instance: ObjectInstanceHandle, attributes: Any, user_supplied_tag: bytes) -> None:
        request_instance_attribute_value_update(self, object_instance, attributes, user_supplied_tag)

    def _deliver_value_update_requests(
        self,
        object_instance: ObjectInstanceHandle,
        record: _ObjectInstanceRecord,
        attribute_handles: set[AttributeHandle],
        user_supplied_tag: bytes,
    ) -> None:
        deliver_value_update_requests(self, object_instance, record, attribute_handles, user_supplied_tag)

    def _current_federate_handle(self) -> FederateHandle:
        if self._federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        return self._federate_handle

    def _current_federate_key(self) -> int:
        return self._current_federate_handle().value

    def _published_attributes_for_current_federate(self, object_class_name: str) -> set[str]:
        return published_attributes_for_current_federate(self, object_class_name)

    def _region_dimension_names(self, federate_key: int, region: Any) -> set[str]:
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        try:
            return set(self._federation_record().member_regions[federate_key][region_value])
        except KeyError as exc:
            raise InvalidRegion(str(region)) from exc

    def _region_values_from_handles(self, regions: Any) -> set[int]:
        return region_values_from_handles(self, regions)

    def _coerce_range_bounds(self, value: Any) -> RangeBounds:
        return coerce_range_bounds(value, invalid_range_bound_exc=InvalidRangeBound)

    def _attribute_region_pairs(self, object_class_name: str, attributes_and_regions: Any) -> tuple[tuple[set[str], set[int]], ...]:
        return attribute_region_pairs(self, object_class_name, attributes_and_regions)

    @staticmethod
    def _ranges_overlap(left: RangeBounds, right: RangeBounds) -> bool:
        return ranges_overlap(left, right)

    def _region_owner_key(self, preferred_key: int, region_value: int) -> int | None:
        return region_owner_key(self, preferred_key, region_value)

    def _regions_overlap_pair(self, source_key: int, source_region: int, target_key: int, target_region: int) -> bool:
        return regions_overlap_pair(self, source_key, source_region, target_key, target_region)

    def _region_sets_overlap(self, source_key: int, source_regions: set[int], target_key: int, target_regions: set[int]) -> bool:
        return region_sets_overlap(self, source_key, source_regions, target_key, target_regions)

    def _object_instance_region_values(self, record: _ObjectInstanceRecord) -> set[int]:
        return object_instance_region_values(record)

    def _reflectable_attribute_names_for_subscriber(
        self,
        source_key: int,
        subscriber_key: int,
        record: _ObjectInstanceRecord,
        discovery_class_name: str,
        subscribed_names: set[str],
    ) -> set[str]:
        return reflectable_attribute_names_for_subscriber(
            self,
            source_key,
            subscriber_key,
            record,
            discovery_class_name,
            subscribed_names,
        )

    def _known_object_classes_for_federate(
        self,
        federate_key: int,
        object_instance: ObjectInstanceHandle,
        object_class_name: str,
    ) -> str | None:
        return known_object_classes_for_federate(
            self,
            federate_key,
            object_instance,
            object_class_name,
        )

    def _subscribed_discovery_class_name(self, federate_key: int, object_class_name: str) -> str | None:
        return subscribed_discovery_class_name(self, federate_key, object_class_name)

    def _object_class_lineage(self, object_class_name: str) -> tuple[str, ...]:
        return object_class_lineage(self, object_class_name)

    def _attribute_name_by_handle(self, object_class_name: str, attribute: AttributeHandle) -> str:
        return attribute_name_by_handle(
            self,
            object_class_name,
            attribute,
            expected_type=AttributeHandle,
            invalid_handle_exc=InvalidAttributeHandle,
        )

    def _attribute_names_from_handles(self, object_class_name: str, attributes: Any) -> tuple[str, ...]:
        return attribute_names_from_handles(
            self,
            object_class_name,
            attributes,
            expected_type=AttributeHandle,
            invalid_handle_exc=InvalidAttributeHandle,
            empty_set_exc=AttributeNotDefined,
        )

    def _resolve_update_rate_designator(self, *unused: Any) -> tuple[float | None, str | None]:
        return resolve_update_rate_designator(
            self,
            *unused,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _default_update_rate_for_attribute(self, object_class_name: str, attribute_name: str) -> float | None:
        return default_update_rate_for_attribute(
            self,
            object_class_name,
            attribute_name,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _default_update_rate_designator_for_attribute(self, object_class_name: str, attribute_name: str) -> str | None:
        return default_update_rate_designator_for_attribute(
            self,
            object_class_name,
            attribute_name,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _subscribed_update_rate_for_attribute(
        self,
        federate_key: int,
        actual_class_name: str,
        attribute_name: str,
    ) -> float:
        return subscribed_update_rate_for_attribute(
            self,
            federate_key,
            actual_class_name,
            attribute_name,
        )

    @staticmethod
    def _time_scalar(value: Any) -> float | None:
        return time_scalar(value)

    def _apply_update_rate_reduction_for_subscriber(
        self,
        federate_key: int,
        object_instance: ObjectInstanceHandle,
        reflected_class_name: str,
        actual_class_name: str,
        reflected: Mapping[AttributeHandle, bytes],
        delivery_time: Any | None,
    ) -> dict[AttributeHandle, bytes]:
        return apply_update_rate_reduction_for_subscriber(
            self,
            federate_key,
            object_instance,
            reflected_class_name,
            actual_class_name,
            reflected,
            delivery_time,
        )

    def _parameter_names_from_handles(self, interaction_class_name: str, parameters: Any) -> tuple[str, ...]:
        return parameter_names_from_handles(self, interaction_class_name, parameters)

    def _interaction_class_names_from_handles(self, interaction_classes: Any) -> tuple[str, ...]:
        return interaction_class_names_from_handles(self, interaction_classes)

    def _default_transportation_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> TransportationTypeHandle:
        return default_transportation_for(self, object_class_name, values_by_handle)

    def _attribute_transportation_for(self, record: _ObjectInstanceRecord, values_by_handle: Mapping[AttributeHandle, bytes]) -> TransportationTypeHandle:
        return attribute_transportation_for(self, record, values_by_handle)

    def _default_order_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        return default_order_for(self, object_class_name, values_by_handle)

    def _attribute_order_for(self, record: _ObjectInstanceRecord, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        return attribute_order_for(self, record, values_by_handle)

    def _interaction_order_for(self, interaction_class_name: str) -> OrderType:
        return interaction_order_for(self, interaction_class_name)

    def _interaction_transportation_for(self, interaction_class_name: str) -> TransportationTypeHandle:
        return interaction_transportation_for(self, interaction_class_name)

    @staticmethod
    def _coerce_order_type(order_type: Any) -> OrderType:
        return coerce_order_type(order_type)

    def _discover_existing_objects_for_current_subscription(self, object_class_name: str) -> None:
        discover_existing_objects_for_current_subscription(self, object_class_name)

class Python2025Backend:
    """Factory-facing backend wrapper that returns a 2025-native ambassador."""

    info = Python2025BackendInfo()

    def __init__(self, request: BackendRequest):
        self.request = request

    def create_rti_ambassador(self) -> Python2025RTIAmbassador:
        ambassador = Python2025RTIAmbassador()
        ambassador.backend_info = self.info
        return ambassador


class HostedPython2025Backend(Python2025Backend):
    """Factory-facing backend wrapper for the hosted FedPro transport route."""

    def __init__(self, request: BackendRequest, transport: Any):
        super().__init__(request)
        self.transport = transport

    def create_rti_ambassador(self):  # noqa: ANN201
        from .hosted_fedpro import FedPro2025RTIAmbassador

        ambassador = FedPro2025RTIAmbassador(self.transport)
        ambassador.backend_info = replace(
            self.info,
            details={**dict(self.info.details), "wrapper_only": False},
        )
        return ambassador


def create_python2025_backend(request: BackendRequest) -> Python2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(
            f"the current Python 2025 RTI backend only supports rti1516_2025, not {request.spec.name!r}"
        )
    options = dict(request.options)
    transport_spec = options.pop("transport", None)
    if transport_spec is not None:
        from hla.transports.common import coerce_transport_spec

        if isinstance(transport_spec, Mapping):
            transport_spec = dict(transport_spec)
            if "kind" in transport_spec or "options" in transport_spec:
                option_map = {
                    key: value for key, value in transport_spec.items() if key not in {"kind", "options"}
                }
                option_map.update(dict(transport_spec.get("options", {})))
                option_map.setdefault("schema", "rti1516_2025")
                transport_spec["options"] = option_map
                transport_spec.setdefault("kind", "grpc")
            else:
                transport_spec.setdefault("kind", "grpc")
                transport_spec.setdefault("schema", "rti1516_2025")
        transport = coerce_transport_spec(transport_spec)
        if transport is None:
            raise ValueError("backend='python2025' received an empty transport specification")
        return HostedPython2025Backend(request, transport)
    if options:
        unsupported = ", ".join(sorted(options))
        raise ValueError(
            f"unsupported backend option(s) for backend='python2025': {unsupported}; "
            "the in-process 2025 backend does not currently accept backend-specific factory options"
        )
    return Python2025Backend(request)


Python2025BackendScaffold = Python2025Backend

__all__ = [
    "Python2025Backend",
    "Python2025BackendInfo",
    "Python2025BackendScaffold",
    "Python2025RTIAmbassador",
    "create_python2025_backend",
]
