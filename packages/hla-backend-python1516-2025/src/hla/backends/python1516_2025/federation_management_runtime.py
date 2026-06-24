"""Shared federation-management semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from hla.rti1516_2025.datatypes import (
    ConfigurationResult,
    FederationExecutionInformation,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformation,
    FederationExecutionMemberInformationSet,
)
from hla.rti1516_2025.enums import AdditionalSettingsResultCode, ResignAction, SynchronizationPointFailureReason
from hla.rti1516_2025.exceptions import (
    AlreadyConnected,
    DesignatorIsHLAstandardMIM,
    FederateAlreadyExecutionMember,
    FederateIsExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InvalidFOM,
    InvalidMIM,
    InvalidFederateHandle,
    InvalidResignAction,
    NotConnected,
    OwnershipAcquisitionPending,
    RestoreInProgress,
    RTIinternalError,
    SaveInProgress,
    SynchronizationPointLabelNotAnnounced,
)
from hla.rti1516_2025.handles import FederateHandle


def connect(
    backend: Any,
    federate_ambassador: Any,
    callback_model: Any,
    configuration: Any | None = None,
    credentials: Any | None = None,
) -> ConfigurationResult:
    if backend._connected:
        raise AlreadyConnected("2025 Python RTI ambassador is already connected")
    callback_model = backend._coerce_callback_model(callback_model)
    backend._validate_credentials(credentials)
    backend._connected = True
    backend._federate_ambassador = federate_ambassador
    backend._callback_model = callback_model
    backend._callbacks_enabled = True
    backend._evoked_callback_queue.clear()
    return ConfigurationResult(
        configurationUsed=configuration is not None,
        addressUsed=False,
        additionalSettingsResultCode=AdditionalSettingsResultCode.SETTINGS_IGNORED,
        message="hla-backend-python1516-2025 accepted the 2025 Python RTI connection request",
    )


def disconnect(backend: Any) -> None:
    if not backend._connected:
        raise NotConnected("2025 Python RTI ambassador is not connected")
    if backend._joined:
        raise FederateIsExecutionMember("Cannot disconnect while joined to a federation execution")
    backend._release_join()
    backend._connected = False
    backend._joined = False
    backend._federation_name = None
    backend._federate_name = None
    backend._federate_handle = None
    backend._federate_ambassador = None
    backend._callback_model = None
    backend._callbacks_enabled = True
    backend._evoked_callback_queue.clear()
    backend._logical_time_implementation_name = backend._DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    backend._logical_time_factory = backend._get_time_factory(backend._DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
    backend._logical_time = backend._logical_time_factory.makeInitial()
    backend._lookahead = backend._logical_time_factory.makeZero()
    backend._time_regulation_enabled = False
    backend._time_constrained_enabled = False
    backend._asynchronous_delivery_enabled = False
    backend._pending_time_advance = None
    backend._switches = dict(backend._SWITCH_DEFAULTS)
    backend._automatic_resign_directive = ResignAction.NO_ACTION
    backend._mom_report_period_seconds = None
    backend._default_attribute_transportation.clear()
    backend._default_attribute_order.clear()
    backend._service_report_serial_number = 0
    backend._service_report_records.clear()
    backend._known_object_classes.clear()
    backend._known_object_names.clear()
    backend._locally_deleted_objects.clear()
    backend._subscribed_object_update_rates.clear()
    backend._subscribed_object_update_rate_designators.clear()
    backend._last_reflect_logical_times.clear()


def force_federate_loss(
    backend: Any,
    federate: Any,
    fault_description: str = "simulated federate fault",
) -> None:
    federate_value = backend._normalize_handle(federate, FederateHandle, InvalidFederateHandle)
    federation = backend._federation_record()

    lost_name = next(
        (name for name, handle in federation.member_handles.items() if handle.value == federate_value),
        None,
    )
    target = federation.member_rtis.get(federate_value)
    if lost_name is None or target is None or target._federate_handle is None:
        raise FederateNotExecutionMember(repr(federate))

    lost_handle = target._federate_handle
    lost_time = target._logical_time
    mom = import_module("hla.fom.mom")
    lost_handle_bytes = import_module("hla.rti1516e.handles").FederateHandle(int(lost_handle.value)).encode()
    lost_time_bytes = import_module("hla.rti1516e.time").HLAinteger64Time(int(lost_time.value)).encode()
    if target._federate_ambassador is not None:
        target._deliver_callback_now("connectionLost", str(fault_description))

    backend._send_mom_report_interaction(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFederateLost",
        {
            "HLAfederate": lost_handle_bytes,
            "HLAfederateName": mom.encode_text(lost_name),
            "HLAtimeStamp": lost_time_bytes,
            "HLAfaultDescription": mom.encode_text(fault_description),
        },
    )

    automatic_resign = target._automatic_resign_directive
    if automatic_resign in {
        ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        target._cancel_resigning_federate_pending_acquisitions()
    if automatic_resign in {
        ResignAction.DELETE_OBJECTS,
        ResignAction.DELETE_OBJECTS_THEN_DIVEST,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        target._delete_objects_owned_by_specific_federate(lost_handle, user_supplied_tag=b"lost")
    if automatic_resign in {
        ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
        ResignAction.DELETE_OBJECTS_THEN_DIVEST,
        ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
    }:
        target._divest_attributes_owned_by_specific_federate(lost_handle)
    target._remove_current_federate_mom_object()
    target._release_join()
    target._joined = False
    target._federation_name = None
    target._federate_name = None
    target._federate_handle = None
    target._connected = False
    target._federate_ambassador = None


def create_federation_execution(backend: Any, *args: Any, **kwargs: Any) -> None:
    federation_name = backend._extract_create_federation_name(args, kwargs)
    if federation_name in backend._FEDERATION_REGISTRY:
        raise FederationExecutionAlreadyExists(federation_name)
    fom_sources = backend._extract_fom_sources(args, kwargs, with_mim=False)
    if not fom_sources:
        raise InvalidFOM("At least one FOM module designator is required")
    logical_time_name = backend._extract_logical_time_implementation_name(args, kwargs)
    resolved_foms = backend._resolve_fom_modules(fom_sources, mim=False)
    mim_module = backend._standard_mim_module()
    fom_catalog = backend._merge_fom_modules(resolved_foms, mim_module=mim_module)
    backend._FEDERATION_REGISTRY[federation_name] = backend._FederationRecord(
        logical_time_implementation_name=logical_time_name,
        fom_modules=resolved_foms,
        mim_module=mim_module,
        fom_catalog=fom_catalog,
    )
    backend._select_logical_time_implementation(logical_time_name)


def create_federation_execution_with_mim(backend: Any, *args: Any, **kwargs: Any) -> None:
    federation_name = backend._extract_create_federation_name(args, kwargs)
    if federation_name in backend._FEDERATION_REGISTRY:
        raise FederationExecutionAlreadyExists(federation_name)
    fom_sources = backend._extract_fom_sources(args, kwargs, with_mim=True)
    if not fom_sources:
        raise InvalidFOM("At least one FOM module designator is required")
    mim_source = backend._extract_mim_source(args, kwargs)
    if mim_source in {"HLAstandardMIM", "HLAstandardMIM.xml"}:
        raise DesignatorIsHLAstandardMIM("Explicit MIM designator shall not be HLAstandardMIM")
    if mim_source is None:
        raise InvalidMIM("Explicit createFederationExecutionWithMIM requires a MIM module designator")
    logical_time_name = backend._extract_logical_time_implementation_name(args, kwargs)
    resolved_foms = backend._resolve_fom_modules(fom_sources, mim=False)
    resolved_mim = backend._resolve_fom_modules((mim_source,), mim=True)[0]
    fom_catalog = backend._merge_fom_modules(resolved_foms, mim_module=resolved_mim)
    backend._FEDERATION_REGISTRY[federation_name] = backend._FederationRecord(
        logical_time_implementation_name=logical_time_name,
        fom_modules=resolved_foms,
        mim_module=resolved_mim,
        fom_catalog=fom_catalog,
    )
    backend._select_logical_time_implementation(logical_time_name)


def destroy_federation_execution(backend: Any, *args: Any, **kwargs: Any) -> None:
    federation_name = backend._extract_create_federation_name(args, kwargs)
    federation = backend._FEDERATION_REGISTRY.get(federation_name)
    if federation is None:
        raise FederationExecutionDoesNotExist(federation_name)
    if federation.members:
        raise FederatesCurrentlyJoined(federation_name)
    del backend._FEDERATION_REGISTRY[federation_name]


def list_federation_executions(backend: Any) -> None:
    report = FederationExecutionInformationSet(
        FederationExecutionInformation(
            federationExecutionName=federation_name,
            logicalTimeImplementationName=record.logical_time_implementation_name,
        )
        for federation_name, record in sorted(backend._FEDERATION_REGISTRY.items())
    )
    backend._deliver_callback_now("reportFederationExecutions", report)


def list_federation_execution_members(backend: Any, federation_name: str) -> None:
    federation = backend._FEDERATION_REGISTRY.get(federation_name)
    if federation is None:
        backend._deliver_callback_now("reportFederationExecutionDoesNotExist", federation_name)
        return
    report = FederationExecutionMemberInformationSet(
        FederationExecutionMemberInformation(federateName=name, federateType=federate_type)
        for name, federate_type in sorted(federation.members.items())
    )
    backend._deliver_callback_now("reportFederationExecutionMembers", federation_name, report)


def join_federation_execution(backend: Any, *args: Any, **kwargs: Any) -> FederateHandle:
    federation_name, federate_name = backend._extract_join_names(args, kwargs)
    federation = backend._FEDERATION_REGISTRY.get(federation_name)
    if federation is None:
        raise FederationExecutionDoesNotExist(federation_name)
    if federation.save_label is not None:
        raise SaveInProgress("A federation save is already in progress")
    if federation.restore_label is not None:
        raise RestoreInProgress("A federation restore is already in progress")
    if backend._joined:
        raise FederateAlreadyExecutionMember("2025 Python RTI ambassador is already joined")
    additional_fom_modules = backend._extract_additional_fom_modules(args, kwargs)
    if additional_fom_modules:
        resolved_additional = backend._resolve_fom_modules(additional_fom_modules, mim=False)
        federation.fom_catalog = backend._merge_fom_modules(
            (*federation.fom_modules, *resolved_additional),
            mim_module=federation.mim_module,
        )
        federation.fom_modules = (*federation.fom_modules, *resolved_additional)
    if federate_name is not None and federate_name in federation.members:
        raise FederateNameAlreadyInUse(federate_name)
    federate_type = backend._extract_federate_type(args, kwargs)
    if federate_name is None:
        federate_name = f"__anonymous_federate_{len(federation.member_handles) + 1}"
    federation.members[federate_name] = federate_type
    backend._federate_handle = FederateHandle(federation.next_federate_handle)
    federation.next_federate_handle += 1
    federation.member_handles[federate_name] = backend._federate_handle
    federation.member_rtis[backend._federate_handle.value] = backend
    if backend._federate_ambassador is not None:
        federation.member_ambassadors[backend._federate_handle.value] = backend._federate_ambassador
    federation.published_object_attributes.setdefault(backend._federate_handle.value, {})
    federation.subscribed_object_attributes.setdefault(backend._federate_handle.value, {})
    federation.subscribed_object_regions.setdefault(backend._federate_handle.value, {})
    federation.published_interactions.setdefault(backend._federate_handle.value, set())
    federation.subscribed_interactions.setdefault(backend._federate_handle.value, set())
    federation.subscribed_interaction_regions.setdefault(backend._federate_handle.value, {})
    federation.directed_interaction_region_gates.setdefault(backend._federate_handle.value, set())
    federation.published_directed_interactions.setdefault(backend._federate_handle.value, {})
    federation.subscribed_directed_interactions.setdefault(backend._federate_handle.value, {})
    federation.member_regions.setdefault(backend._federate_handle.value, {})
    federation.member_region_bounds.setdefault(backend._federate_handle.value, {})
    backend._select_logical_time_implementation(federation.logical_time_implementation_name)
    backend._federation_name = federation_name
    backend._federate_name = federate_name
    backend._joined = True
    for label, point in federation.synchronization_points.items():
        if point.synchronized:
            continue
        point.required_federates.add(backend._federate_handle.value)
        backend._deliver_to_federate_handle(
            backend._federate_handle,
            "announceSynchronizationPoint",
            label,
            point.user_supplied_tag,
        )
    backend._ensure_mom_objects()
    return backend._federate_handle


def resign_federation_execution(backend: Any, resign_action: ResignAction) -> None:
    if not isinstance(resign_action, ResignAction):
        try:
            if hasattr(resign_action, "name"):
                resign_action = ResignAction[getattr(resign_action, "name")]
            else:
                resign_action = ResignAction(resign_action)
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidResignAction(str(resign_action)) from exc
    if resign_action is ResignAction.NO_ACTION:
        if backend._resigning_federate_has_pending_acquisitions():
            raise OwnershipAcquisitionPending("Cannot resign with pending ownership acquisition using NO_ACTION")
        if backend._resigning_federate_owns_attributes():
            raise FederateOwnsAttributes("Cannot resign while owning attributes using NO_ACTION")
    backend._apply_resign_action(resign_action)
    if backend._federate_ambassador is not None and hasattr(backend._federate_ambassador, "federateResigned"):
        backend._deliver_callback("federateResigned", backend._resign_reason_description(resign_action))
    backend._remove_current_federate_mom_object()
    backend._release_join()
    backend._joined = False
    backend._federation_name = None
    backend._federate_name = None
    backend._federate_handle = None


def register_federation_synchronization_point(
    backend: Any,
    synchronization_point_label: str,
    user_supplied_tag: bytes,
    synchronization_set: Any | None = None,
) -> None:
    if not isinstance(synchronization_point_label, str) or not synchronization_point_label:
        raise RTIinternalError("Synchronization point label must be a non-empty string")
    federation = backend._federation_record()
    if synchronization_point_label in federation.synchronization_points:
        backend._deliver_callback(
            "synchronizationPointRegistrationFailed",
            synchronization_point_label,
            SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
        )
        return
    required = backend._synchronization_required_federates(synchronization_set)
    federation.synchronization_points[synchronization_point_label] = backend._SynchronizationPointRecord(
        user_supplied_tag=bytes(user_supplied_tag),
        required_federates=required,
    )
    backend._deliver_callback("synchronizationPointRegistrationSucceeded", synchronization_point_label)
    for federate_key in sorted(required):
        backend._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "announceSynchronizationPoint",
            synchronization_point_label,
            bytes(user_supplied_tag),
        )


def synchronization_point_achieved(
    backend: Any,
    synchronization_point_label: str,
    successfully: bool = True,
) -> None:
    federation = backend._federation_record()
    try:
        point = federation.synchronization_points[synchronization_point_label]
    except KeyError as exc:
        raise SynchronizationPointLabelNotAnnounced(synchronization_point_label) from exc
    federate_key = backend._current_federate_key()
    if federate_key not in point.required_federates:
        raise SynchronizationPointLabelNotAnnounced(synchronization_point_label)
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
            backend._deliver_to_federate_handle(
                FederateHandle(target_key),
                "federationSynchronized",
                synchronization_point_label,
                failed,
            )
