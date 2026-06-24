"""Live IEEE 1516.1-2025 Python RTI backend implementation."""

from __future__ import annotations

import copy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from hla.backends.common import time_management as tm
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
    AlreadyConnected, AttributeAcquisitionWasNotRequested, AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested, AttributeAlreadyOwned, AttributeDivestitureWasNotRequested,
    AttributeNotDefined, AttributeNotOwned, CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM,
    CouldNotOpenMIM, DeletePrivilegeNotHeld, DesignatorIsHLAstandardMIM, ErrorReadingFOM,
    ErrorReadingMIM, FederateAlreadyExecutionMember, FederateIsExecutionMember,
    FederateNameAlreadyInUse, FederatesCurrentlyJoined, FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist, InconsistentFOM, InteractionClassNotDefined,
    InteractionClassNotPublished, InteractionParameterNotDefined, InvalidAttributeHandle,
    InvalidCredentials, InvalidDimensionHandle, InvalidFederateHandle, InvalidFOM,
    InvalidInteractionClassHandle, InvalidLogicalTime, InvalidLookahead, InvalidMessageRetractionHandle,
    InvalidMIM, InvalidObjectClassHandle, InvalidObjectInstanceHandle, InvalidOrderType,
    InvalidParameterHandle, InvalidRangeBound, InvalidResignAction, InvalidRegion,
    InvalidRegionContext, InvalidServiceGroup, InvalidUpdateRateDesignator, InvalidTransportationName,
    InvalidTransportationTypeHandle, LogicalTimeAlreadyPassed, MessageCanNoLongerBeRetracted,
    NameNotFound, TimeConstrainedAlreadyEnabled, TimeRegulationAlreadyEnabled, NoAcquisitionPending,
    NotConnected, ObjectClassNotDefined, ObjectClassNotPublished, ObjectInstanceNameInUse,
    ObjectInstanceNameNotReserved, ObjectInstanceNotKnown, RegionDoesNotContainSpecifiedDimension,
    RestoreInProgress, RestoreNotInProgress, RestoreNotRequested, SaveInProgress, SaveNotInitiated,
    SaveNotInProgress, SynchronizationPointLabelNotAnnounced, TimeRegulationIsNotEnabled,
    Unauthorized, UnsupportedCallbackModel,
)
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
from .ambassador_core_surface_mixin import AmbassadorCoreSurfaceMixin
from .backend_factory_runtime import (
    Python2025Backend,
    Python2025BackendInfo,
    HostedPython2025Backend,
    create_python2025_backend as _create_python2025_backend,
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
from .catalog_access_runtime import (
    catalog,
    dimension_default_upper_bound,
    dimension_handles,
    dimension_spec,
    federation_record,
    interaction_class_handles,
    normalize_handle,
    object_class_handles,
    stable_handles,
    transportation_handles,
)
from .federation_management_runtime import (
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
from .federation_state_runtime import (
    apply_resign_action,
    cancel_resigning_federate_pending_acquisitions,
    delete_objects_owned_by_resigning_federate,
    delete_objects_owned_by_specific_federate,
    divest_attributes_owned_by_specific_federate,
    divest_resigning_federate_attributes,
    ensure_mom_federate_object,
    ensure_mom_federation_object,
    ensure_mom_objects,
    is_mom_object_class_name,
    mom_runtime_federate_handle,
    prune_tso_state_for_departing_federate,
    refresh_mom_federate_object,
    refresh_mom_federation_object,
    register_internal_object_instance,
    release_join,
    remove_current_federate_mom_object,
    resigning_federate_has_pending_acquisitions,
    resigning_federate_owns_attributes,
)
from .federation_bootstrap_runtime import (
    coerce_callback_model,
    extract_additional_fom_modules,
    extract_create_federation_name,
    extract_federate_type,
    extract_federation_name,
    extract_fom_sources,
    extract_join_names,
    extract_logical_time_implementation_name,
    extract_mim_source,
    get_time_factory,
    merge_fom_modules,
    normalize_module_sources,
    resolve_fom_modules,
    select_logical_time_implementation,
    standard_mim_module,
    validate_credentials,
)
from .interaction_runtime import (
    query_interaction_transportation_type,
    request_interaction_transportation_type_change,
    send_directed_interaction,
    send_interaction,
    send_interaction_with_regions,
)
from .interaction_policy_runtime import (
    coerce_order_type,
    interaction_class_names_from_handles,
    interaction_order_for,
    interaction_transportation_for,
    parameter_names_from_handles,
)
from .input_guard_runtime import (
    coerce_interval,
    coerce_time,
    normalize_reserved_object_instance_name,
    normalize_reserved_object_instance_name_set,
    require_connected,
    require_joined,
    require_no_save_or_restore,
)
from .save_restore_lifecycle import capture_federation_save_snapshot, restore_federation_save_snapshot
from .attribute_policy_runtime import (
    attribute_order_for,
    attribute_transportation_for,
    default_order_for,
    default_transportation_for,
    known_object_classes_for_federate,
    reflectable_attribute_names_for_subscriber,
)
from .attribute_scope_runtime import (
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
from .delivery_state_runtime import (
    add_attribute_candidate,
    canonicalize_retraction_handles,
    deliver_due_tso_callbacks,
    drop_retraction_group_member,
    finalize_retraction_group_if_inactive,
    has_attribute_candidate,
    pop_attribute_candidate,
    queue_tso_callback,
    register_retraction_group,
    remove_attribute_candidate,
    resolve_retraction_group,
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
from .object_model_runtime import (
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
    attribute_region_pairs,
    coerce_range_bounds,
    object_instance_region_values,
    region_owner_key,
    region_sets_overlap,
    region_values_from_handles,
    regions_overlap_pair,
    ranges_overlap,
    query_attribute_transportation_type,
    request_attribute_transportation_type_change,
)
from .object_reflection_runtime import (
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
from .time_management_runtime import (
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
from .update_rate_runtime import (
    apply_update_rate_reduction_for_subscriber,
    default_update_rate_designator_for_attribute,
    default_update_rate_for_attribute,
    resolve_update_rate_designator,
    subscribed_update_rate_for_attribute,
    time_scalar,
)
from .declaration_ddm_surface_mixin import DeclarationDdmSurfaceMixin
from .object_ownership_surface_mixin import ObjectOwnershipSurfaceMixin
from .runtime_helper_surface_mixin import RuntimeHelperSurfaceMixin
from .support_surface_mixin import SupportSurfaceMixin
from .federation_time_surface_mixin import FederationTimeSurfaceMixin
from .mom_surface_mixin import MomSurfaceMixin
from .runtime_state import FEDERATION_REGISTRY as _FEDERATION_REGISTRY
from .runtime_state import FederationRecord as _FederationRecord
from .runtime_state import SynchronizationPointRecord as _SynchronizationPointRecord

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

class Python2025RTIAmbassador(
    AmbassadorCoreSurfaceMixin,
    RuntimeHelperSurfaceMixin,
    MomSurfaceMixin,
    DeclarationDdmSurfaceMixin,
    ObjectOwnershipSurfaceMixin,
    FederationTimeSurfaceMixin,
    SupportSurfaceMixin,
):
    """Minimal 2025 RTI ambassador for factory and adapter development."""

    backend_info = Python2025BackendInfo()
    _DEFAULT_LOGICAL_TIME_IMPLEMENTATION = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    _SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS = _SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS
    _SWITCH_DEFAULTS = _SWITCH_DEFAULTS
    _FEDERATION_REGISTRY = _FEDERATION_REGISTRY
    _FederationRecord = _FederationRecord
    _SynchronizationPointRecord = _SynchronizationPointRecord

Python2025BackendScaffold = Python2025Backend
Python2025BackendInfo.__module__ = __name__
Python2025Backend.__module__ = __name__
HostedPython2025Backend.__module__ = __name__


def create_python2025_backend(request):  # noqa: ANN001, ANN201
    return _create_python2025_backend(request)

__all__ = [
    "Python2025Backend",
    "Python2025BackendInfo",
    "Python2025BackendScaffold",
    "Python2025RTIAmbassador",
    "create_python2025_backend",
]
