"""Concrete in-memory Python RTI backend implementation."""
from __future__ import annotations

from typing import Any, Mapping

import hla.fom.mom as hla_mom
from hla.rti1516e.enums import ResignAction
from hla.rti1516e.exceptions import (
    FederateNotExecutionMember,
    NotConnected,
    RTIexception,
)
from hla.fom import FOMCatalog, FOMResolver
from hla.rti1516e.handles import (
    AttributeHandle,
    InteractionClassHandle,
    ObjectInstanceHandle,
    RegionHandle,
    TransportationTypeHandle,
)
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e.time import LogicalTimeFactory
from hla.backends.common import BackendInfo, Invocation, RTIBackend, UnsupportedBackendService
from hla.backends.common import resolve_java_arguments
from hla.backends.common import time_management as tm
from .callbacks import PythonRTICallbacksMixin
from .ddm import PythonRTIDdmMixin
from .ddm_regions import PythonRTIDdmRegionMixin
from .declaration import PythonRTIDeclarationMixin
from .engine import InMemoryRTIEngine
from .federation import PythonRTIFederationMixin
from .federation_sync import PythonRTIFederationSyncMixin
from .fom_helpers import PythonRTIFomMixin
from .mom import PythonRTIMomMixin
from .mom_parameter_decoding import PythonRTIMomParameterDecodingMixin
from .mom_reporting import PythonRTIMomReportingMixin
from .object import PythonRTIObjectMixin
from .object_delivery_transport import PythonRTIObjectTransportMixin
from .ownership import PythonRTIOwnershipMixin
from .reporting import PythonRTIServiceReportFiles
from .save_restore import PythonRTISaveRestoreMixin
from .save_restore_state import PythonRTISaveRestoreStateMixin
from .service_reporting import ServiceReportSink
from .state import (
    MOM_TEXT_ENCODING,
    FederateState,
    FederationState,
    PythonRTIConfig,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
)
from .subscriptions import PythonRTISubscriptionMixin
from .support import PythonRTISupportMixin
from .support_lookup import PythonRTISupportLookupMixin
from .time import PythonRTITimeMixin
from .time_queue_delivery import PythonRTITimeQueueDeliveryMixin
from .time_queue_grants import PythonRTITimeQueueGrantMixin
from .time_validation import PythonRTITimeValidationMixin


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


class PythonRTIBackend(
    PythonRTIFomMixin,
    PythonRTIFederationMixin,
    PythonRTISaveRestoreMixin,
    PythonRTICallbacksMixin,
    PythonRTISubscriptionMixin,
    PythonRTIDeclarationMixin,
    PythonRTIObjectMixin,
    PythonRTIOwnershipMixin,
    PythonRTITimeMixin,
    PythonRTIDdmMixin,
    PythonRTISupportMixin,
    PythonRTIMomMixin,
    RTIBackend,
    ):
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
        setattr(self.state, "backend", self)
        self.delivered_callback_count = 0
        self.service_report_sink = (
            ServiceReportSink(self.config.service_report_file, truncate=self.config.service_report_file_truncate)
            if self.config.service_report_file
            else None
        )
        self.service_report_files = PythonRTIServiceReportFiles(directory=self.config.service_report_directory)
        self.info = BackendInfo(
            name=self.config.name,
            kind="python/1516e",
            version=self.config.version,
            details={"engine": self.engine.name, "backend_id": self.state.backend_id},
        )
        self._service_dispatch = {
            method_name: service
            for method_name in API_METADATA["RTIambassador"]
            if (service := getattr(self, "_svc_" + method_name, None)) is not None
        }
        self._services_allowed_before_join = {
            "connect",
            "disconnect",
            "createFederationExecution",
            "destroyFederationExecution",
            "listFederationExecutions",
            "joinFederationExecution",
        }

    def invoke(self, invocation: Invocation) -> Any:
        service = self._service_dispatch.get(invocation.method_name)
        if service is None:
            raise UnsupportedBackendService(f"Python in-memory RTI does not yet implement {invocation.method_name}")
        if invocation.method_name == "queryInteractionTransportationType" and len(invocation.args) == 1 and not invocation.kwargs:
            args = invocation.args
        elif not self.state.connected:
            args = invocation.args
        elif self.state.handle is None and invocation.method_name not in self._services_allowed_before_join:
            args = invocation.args
        else:
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
        federation = self._require_joined()
        return federation.fom_catalog

    def current_fom_summary(self) -> dict[str, Any]:
        return self._current_fom_summary()

    def close(self) -> None:
        try:
            if self.state.connected and self.state.handle is not None:
                self._svc_resignFederationExecution(ResignAction.NO_ACTION)
            if self.state.connected:
                self._svc_disconnect()
        except Exception:
            pass

    def force_federate_loss(self, federate_handle: Any, fault_description: str = "simulated federate fault") -> None:
        """Test-only helper that injects a non-orderly federate loss into the active federation."""

        federation = self._require_joined()
        target = federation.federates.get(federate_handle)
        if target is None or target.handle is None:
            raise FederateNotExecutionMember(repr(federate_handle))

        lost_handle = target.handle
        lost_name = target.name or self._federate_name(target)
        automatic_resign = target.automatic_resign_directive
        action_name = self._enum_name(automatic_resign)

        if target.ambassador is not None:
            target.disconnect_pending_after_connection_lost = True
            self._deliver(target, "connectionLost", fault_description)

        self._send_mom_report(
            federation,
            f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportFederateLost",
            {
                "HLAfederate": lost_handle,
                "HLAfederateName": lost_name,
                "HLAtimeStamp": target.current_time,
                "HLAfaultDescription": fault_description,
            },
        )

        original_remove_object = self._remove_object

        def _remove_object_with_loss_producer(instance: Any, tag: bytes, *, timestamp: Any | None = None, retraction_handle: Any | None = None) -> None:
            self._remove_object_with_producer(
                federation,
                instance,
                tag,
                timestamp=timestamp,
                retraction_handle=retraction_handle,
                producing_federate=lost_handle,
            )

        self._remove_object = _remove_object_with_loss_producer
        try:
            self._apply_departure_resign_action(
                federation,
                target,
                action_name,
                removal_tag=b"lost",
            )
        finally:
            self._remove_object = original_remove_object
        self._finalize_departed_federate_membership(federation, target)

    def _finalize_connection_lost_disconnect(self, federate: FederateState) -> None:
        federate.disconnect_pending_after_connection_lost = False
        federate.connected = False
        federate.ambassador = None
        federate.queue.clear()
        federate.ro_message_queue.clear()
        federate.tso_message_heap.clear()
        federate.retraction_messages.clear()
        federate.delivered_retraction_messages.clear()
        federate.retractable_messages.clear()

    def _enum_name(self, value: Any) -> str:
        return _enum_name(value)

    def _deliver(self, target: FederateState, method_name: str, *args: Any) -> None:
        PythonRTICallbacksMixin._deliver(self, target, method_name, *args)

    def _require_connected(self) -> None:
        if not self.state.connected:
            raise NotConnected("RTI ambassador is not connected")

    def _require_joined(self) -> FederationState:
        self._require_connected()
        federation = self.state.federation
        if self.state.handle is None or federation is None:
            raise FederateNotExecutionMember("Federate has not joined a federation execution")
        return federation

    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None:
        PythonRTISaveRestoreStateMixin._ensure_no_save_or_restore_in_progress(self, federation)

    def _federate_name(self, state: FederateState | None = None) -> str:
        state = state or self.state
        return state.name or f"Federate-{state.backend_id}"

    def _enforce_fom_names(self, federation: FederationState) -> bool:
        return bool(self.config.strict_fom_lookup and federation.fom_catalog.modules)

    def _time_factory(self) -> LogicalTimeFactory[Any, Any]:
        federation = self.state.federation
        if federation is not None:
            return federation.time_factory
        return self.engine.time_factories.get(self.config.default_logical_time_implementation_name)

    def _time_lt(self, a: Any, b: Any) -> bool:
        return tm.time_lt(a, b)

    def _time_le(self, a: Any, b: Any) -> bool:
        return tm.time_le(a, b)

    def _queued_tso_messages(self, federation: FederationState, fed: FederateState):
        return tm.queued_tso_messages(federation, fed)

    def _compute_grant_decision(self, federation: FederationState, fed: FederateState, request: Any, **kwargs: Any):
        return tm.compute_grant_decision(federation, fed, request, **kwargs)

    def _scheduled_save_time_reached(self, fed: FederateState, save_time: Any, *, next_grant_time: Any | None = None) -> bool:
        return tm.scheduled_save_time_reached(fed, save_time, next_grant_time=next_grant_time)

    def _object_matches_subscription(self, actual_class: object, subscribed_class: object) -> bool:
        return PythonRTISubscriptionMixin._object_matches_subscription(self, actual_class, subscribed_class)

    def _interaction_matches_subscription(
        self,
        actual_class: InteractionClassHandle,
        subscribed_class: InteractionClassHandle,
    ) -> bool:
        return PythonRTISubscriptionMixin._interaction_matches_subscription(self, actual_class, subscribed_class)

    def _attribute_subscription_intersection(
        self,
        federate: FederateState,
        object_class: object,
        attributes: Mapping[AttributeHandle, bytes],
        instance: Any | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set[RegionHandle]] | None = None,
    ) -> dict[AttributeHandle, bytes]:
        return PythonRTISubscriptionMixin._attribute_subscription_intersection(
            self,
            federate,
            object_class,
            attributes,
            instance=instance,
            sent_regions_by_attribute=sent_regions_by_attribute,
        )

    def _region_sets_overlap(
        self,
        source_federate: FederateState,
        source_regions: set[RegionHandle],
        target_federate: FederateState,
        target_regions: set[RegionHandle],
    ) -> bool:
        return PythonRTIDdmRegionMixin._region_sets_overlap(
            self,
            source_federate,
            source_regions,
            target_federate,
            target_regions,
        )

    def _resolve_fom_modules(
        self,
        sources: Any,
        *,
        require_non_empty: bool = False,
        mim: bool = False,
    ) -> tuple[Any, ...]:
        return PythonRTIFomMixin._resolve_fom_modules(
            self,
            sources,
            require_non_empty=require_non_empty,
            mim=mim,
        )

    def _combine_fom_catalog(
        self,
        modules: Any,
        *,
        mim_module: Any | None = None,
        base_catalog: Any | None = None,
    ) -> Any:
        return PythonRTIFomMixin._combine_fom_catalog(
            self,
            modules,
            mim_module=mim_module,
            base_catalog=base_catalog,
        )

    def _choose_time_factory(self, requested_name: str | None, modules: Any) -> Any:
        return PythonRTIFomMixin._choose_time_factory(self, requested_name, modules)

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle | None:
        return PythonRTISupportLookupMixin._transportation_handle_by_name(self, name)

    def _find_object(self, theObject: ObjectInstanceHandle):
        return PythonRTISupportLookupMixin._find_object(self, theObject)

    def _process_time_advances(self, federation: FederationState) -> None:
        PythonRTITimeQueueGrantMixin._process_time_advances(self, federation)

    def _queue_or_deliver_message(
        self,
        target: FederateState,
        callback: Any,
        *,
        sent_order: Any,
        timestamp: Any | None,
        sender: Any,
        service_name: str,
        retraction_handle: Any | None = None,
        post_deliver_cleanup: Any | None = None,
    ) -> None:
        PythonRTITimeQueueDeliveryMixin._queue_or_deliver_message(
            self,
            target,
            callback,
            sent_order=sent_order,
            timestamp=timestamp,
            sender=sender,
            service_name=service_name,
            retraction_handle=retraction_handle,
            post_deliver_cleanup=post_deliver_cleanup,
        )

    def _queue_or_deliver_tso(
        self,
        federation: FederationState,
        target: FederateState,
        timestamp: Any | None,
        event: Any,
        *,
        retraction_handle: Any,
        producing_federate: Any,
        post_deliver_cleanup: Any | None = None,
    ) -> None:
        PythonRTITimeQueueGrantMixin._queue_or_deliver_tso(
            self,
            federation,
            target,
            timestamp,
            event,
            retraction_handle=retraction_handle,
            producing_federate=producing_federate,
            post_deliver_cleanup=post_deliver_cleanup,
        )

    def _extract_timestamp(self, args: tuple[Any, ...]) -> Any | None:
        return PythonRTITimeValidationMixin._extract_timestamp(self, args)

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        PythonRTITimeValidationMixin._validate_tso_send_time(self, timestamp)

    def _make_retraction_return(self, timestamp: Any) -> Any:
        return PythonRTITimeValidationMixin._make_retraction_return(self, timestamp)

    def _transportation_type_for_interaction(self, interaction: InteractionClassHandle) -> Any:
        return PythonRTIObjectTransportMixin._transportation_type_for_interaction(self, interaction)

    def _validate_user_supplied_tag(
        self,
        federation: FederationState,
        category: str,
        user_supplied_tag: bytes,
    ) -> None:
        PythonRTIObjectTransportMixin._validate_user_supplied_tag(
            self,
            federation,
            category,
            user_supplied_tag,
        )

    def _compute_galt(self, federation: FederationState, federate: FederateState) -> Any:
        return PythonRTITimeQueueGrantMixin._compute_galt(self, federation, federate)

    def _compute_lits(self, federation: FederationState, federate: FederateState) -> Any:
        return PythonRTITimeQueueGrantMixin._compute_lits(self, federation, federate)

    def _svc_getHLAversion(self) -> str:
        return PythonRTISupportLookupMixin._svc_getHLAversion(self)

    def _mom_exposure_model(self, federation: FederationState) -> Any:
        return PythonRTIMomMixin._mom_exposure_model(self, federation)

    def _mom_interaction_rule(self, federation: FederationState, interaction_name: str) -> Any:
        return PythonRTIMomMixin._mom_interaction_rule(self, federation, interaction_name)

    def _mom_parameter_handle(self, interaction_name: str, parameter_name: str) -> Any:
        return PythonRTIMomMixin._mom_parameter_handle(self, interaction_name, parameter_name)

    def _send_mom_report(self, federation: FederationState, report_name: str, values: Mapping[str, Any]) -> None:
        PythonRTIMomReportingMixin._send_mom_report(self, federation, report_name, values)

    def _mom_request_report_values(
        self,
        federation: FederationState,
        request_name: str,
        report_name: str,
        params: Mapping[str, bytes],
    ) -> dict[str, Any]:
        return PythonRTIMomReportingMixin._mom_request_report_values(
            self,
            federation,
            request_name,
            report_name,
            params,
        )

    def _apply_mom_set_service_reporting(
        self,
        federation: FederationState,
        target: FederateState,
        enabled: bool,
        interaction_name: str = "",
        parameter_name: str = "HLAreportingState",
    ) -> None:
        PythonRTIMomReportingMixin._apply_mom_set_service_reporting(
            self,
            federation,
            target,
            enabled,
            interaction_name=interaction_name,
            parameter_name=parameter_name,
        )

    def _ensure_service_report_file(self, federation: FederationState, federate: FederateState) -> str:
        return PythonRTIMomReportingMixin._ensure_service_report_file(self, federation, federate)

    def _refresh_mom_attribute_values(self, federation: FederationState) -> None:
        PythonRTIMomMixin._refresh_mom_attribute_values(self, federation)

    def _refresh_all_mom_objects(self, federation: FederationState, *, notify: bool = True) -> None:
        PythonRTIMomMixin._refresh_all_mom_objects(self, federation, notify=notify)

    def _is_mom_object_instance(self, federation: FederationState, instance: Any) -> bool:
        return PythonRTIMomMixin._is_mom_object_instance(self, federation, instance)

    def _deliver_mom_attribute_update(self, instance: Any, attrs: set[AttributeHandle], tag: bytes) -> None:
        PythonRTIMomMixin._deliver_mom_attribute_update(self, instance, attrs, tag)

    def _all_fom_module_data(self, federation: FederationState) -> bytes:
        return PythonRTIMomMixin._all_fom_module_data(self, federation)

    def _module_xml_or_uri(self, module: Any) -> bytes:
        return PythonRTIMomMixin._module_xml_or_uri(self, module)

    def _decode_mom_object_instance_handle(self, value: bytes | None) -> Any:
        return PythonRTIMomParameterDecodingMixin._decode_mom_object_instance_handle(self, value)

    def _send_mom_exception(
        self,
        federation: FederationState,
        interaction_name: str,
        exception_name: str,
        parameter_error: str = "",
        *,
        federate: Any | None = None,
    ) -> None:
        PythonRTIMomParameterDecodingMixin._send_mom_exception(
            self,
            federation,
            interaction_name,
            exception_name,
            parameter_error,
            federate=federate,
        )

    def _target_federate_from_mom_params(self, federation: FederationState, params: Mapping[str, bytes]) -> FederateState:
        return PythonRTIMomParameterDecodingMixin._target_federate_from_mom_params(self, federation, params)

    def _handle_mom_interaction(
        self,
        interaction_name: str,
        parameters: Mapping[Any, bytes],
        tag: bytes,
    ) -> bool:
        return PythonRTIMomMixin._handle_mom_interaction(self, interaction_name, parameters, tag)

    def _refresh_mom_federation_object(
        self,
        federation: FederationState,
        *,
        notify: bool = True,
    ) -> None:
        PythonRTIMomMixin._refresh_mom_federation_object(self, federation, notify=notify)

    def _refresh_mom_federate_object(
        self,
        federation: FederationState,
        federate: FederateState,
        *,
        notify: bool = True,
    ) -> None:
        PythonRTIMomMixin._refresh_mom_federate_object(self, federation, federate, notify=notify)

    def _ensure_mom_federation_object(self, federation: FederationState) -> None:
        PythonRTIMomMixin._ensure_mom_federation_object(self, federation)

    def _ensure_mom_federate_object(self, federation: FederationState, federate: FederateState) -> None:
        PythonRTIMomMixin._ensure_mom_federate_object(self, federation, federate)

    def _process_scheduled_saves(self, federation: FederationState) -> None:
        PythonRTISaveRestoreStateMixin._process_scheduled_saves(self, federation)

    def _reconcile_owner_update_interest(self, instance: Any) -> None:
        PythonRTISubscriptionMixin._reconcile_owner_update_interest(self, instance)

    def _current_in_scope_attributes(self, subscriber: FederateState, instance: Any) -> set[Any]:
        return PythonRTISubscriptionMixin._current_in_scope_attributes(self, subscriber, instance)

    def _announce_open_synchronization_points_to_joiner(
        self,
        federation: FederationState,
        handle: Any,
    ) -> None:
        PythonRTIFederationSyncMixin._announce_open_synchronization_points_to_joiner(self, federation, handle)

    def _remove_federate_from_synchronization_points(
        self,
        federation: FederationState,
        handle: Any,
    ) -> None:
        PythonRTIFederationSyncMixin._remove_federate_from_synchronization_points(self, federation, handle)

    def _remove_object(
        self,
        instance: Any,
        tag: bytes,
        *,
        timestamp: Any | None = None,
        retraction_handle: Any | None = None,
    ) -> None:
        PythonRTIObjectMixin._remove_object(
            self,
            instance,
            tag,
            timestamp=timestamp,
            retraction_handle=retraction_handle,
        )

__all__ = [
    "PythonRTIBackend",
    "InMemoryRTIEngine",
    "PythonRTIConfig",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
]
