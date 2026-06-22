"""Federation, save/restore, callback, and time-management surface wrappers."""

from __future__ import annotations

from typing import Any

from hla.backends.common import time_management as tm
from hla.rti1516_2025.datatypes import ConfigurationResult, TimeQueryReturn
from hla.rti1516_2025.enums import CallbackModel, ResignAction
from hla.rti1516_2025.exceptions import InvalidLogicalTime, LogicalTimeAlreadyPassed
from hla.rti1516_2025.federate_ambassador import FederateAmbassador

from .callback_runtime import (
    disable_asynchronous_delivery,
    disable_callbacks,
    enable_asynchronous_delivery,
    enable_callbacks,
    evoke_callback,
    evoke_multiple_callbacks,
    force_connection_lost,
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
from .save_restore_lifecycle import (
    abort_federation_restore,
    abort_federation_save,
    complete_restore,
    complete_save,
    federate_save_begun,
    process_scheduled_save,
    query_federation_restore_status,
    query_federation_save_status,
    request_federation_restore,
    request_federation_save,
    start_federation_save,
)
from .time_management_runtime import (
    build_time_management_federation,
    build_time_management_state,
    deliver_due_tso_callbacks_for_request,
    disable_time_constrained,
    disable_time_regulation,
    enable_time_constrained,
    enable_time_regulation,
    modify_lookahead,
    process_time_advances,
    query_galt_for,
    query_lits_for,
    query_lookahead,
    request_time_advance,
    retract_message,
    try_grant_pending_time_advance,
    validate_tso_send_time,
)


class FederationTimeSurfaceMixin:
    """Keep the main ambassador body focused on stateful runtime helpers."""

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

    def joinFederationExecution(self, *args: Any, **kwargs: Any):  # noqa: N802, ANN201
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

    def _start_federation_save(self, federation: Any, label: str, save_time: Any | None) -> None:
        start_federation_save(self, federation, label, save_time)

    def _process_scheduled_save(self, federation: Any) -> None:
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

    def enable_time_regulation(self, lookahead: Any) -> None:
        self.enableTimeRegulation(lookahead)

    def disableTimeRegulation(self) -> None:  # noqa: N802
        self._record("disableTimeRegulation")
        self._require_joined("disableTimeRegulation")
        disable_time_regulation(self)

    def disable_time_regulation(self) -> None:
        self.disableTimeRegulation()

    def enableTimeConstrained(self) -> None:  # noqa: N802
        self._record("enableTimeConstrained")
        self._require_joined("enableTimeConstrained")
        enable_time_constrained(self)

    def enable_time_constrained(self) -> None:
        self.enableTimeConstrained()

    def disableTimeConstrained(self) -> None:  # noqa: N802
        self._record("disableTimeConstrained")
        self._require_joined("disableTimeConstrained")
        disable_time_constrained(self)

    def disable_time_constrained(self) -> None:
        self.disableTimeConstrained()

    def enableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("enableAsynchronousDelivery")
        self._require_joined("enableAsynchronousDelivery")
        enable_asynchronous_delivery(self)

    def enable_asynchronous_delivery(self) -> None:
        self.enableAsynchronousDelivery()

    def disableAsynchronousDelivery(self) -> None:  # noqa: N802
        self._record("disableAsynchronousDelivery")
        self._require_joined("disableAsynchronousDelivery")
        disable_asynchronous_delivery(self)

    def disable_asynchronous_delivery(self) -> None:
        self.disableAsynchronousDelivery()

    def timeAdvanceRequest(self, time: Any) -> None:  # noqa: N802
        self._record("timeAdvanceRequest", time)
        self._require_joined("timeAdvanceRequest")
        self._request_time_advance("timeAdvanceRequest", time)

    def time_advance_request(self, time: Any) -> None:
        self.timeAdvanceRequest(time)

    def timeAdvanceRequestAvailable(self, time: Any) -> None:  # noqa: N802
        self._record("timeAdvanceRequestAvailable", time)
        self._require_joined("timeAdvanceRequestAvailable")
        self._request_time_advance("timeAdvanceRequestAvailable", time)

    def time_advance_request_available(self, time: Any) -> None:
        self.timeAdvanceRequestAvailable(time)

    def nextMessageRequest(self, time: Any) -> None:  # noqa: N802
        self._record("nextMessageRequest", time)
        self._require_joined("nextMessageRequest")
        self._request_time_advance("nextMessageRequest", time)

    def next_message_request(self, time: Any) -> None:
        self.nextMessageRequest(time)

    def nextMessageRequestAvailable(self, time: Any) -> None:  # noqa: N802
        self._record("nextMessageRequestAvailable", time)
        self._require_joined("nextMessageRequestAvailable")
        self._request_time_advance("nextMessageRequestAvailable", time)

    def next_message_request_available(self, time: Any) -> None:
        self.nextMessageRequestAvailable(time)

    def flushQueueRequest(self, time: Any) -> None:  # noqa: N802
        self._record("flushQueueRequest", time)
        self._require_joined("flushQueueRequest")
        self._request_time_advance("flushQueueRequest", time)

    def flush_queue_request(self, time: Any) -> None:
        self.flushQueueRequest(time)

    def queryGALT(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryGALT")
        self._require_joined("queryGALT")
        return self._query_galt_for(self)

    def query_galt(self) -> TimeQueryReturn:
        return self.queryGALT()

    def queryLogicalTime(self) -> Any:  # noqa: N802
        self._record("queryLogicalTime")
        self._require_joined("queryLogicalTime")
        return self._logical_time

    def query_logical_time(self) -> Any:
        return self.queryLogicalTime()

    def queryLITS(self) -> TimeQueryReturn:  # noqa: N802
        self._record("queryLITS")
        self._require_joined("queryLITS")
        return self._query_lits_for(self)

    def query_lits(self) -> TimeQueryReturn:
        return self.queryLITS()

    def modifyLookahead(self, lookahead: Any) -> None:  # noqa: N802
        self._record("modifyLookahead", lookahead)
        self._require_joined("modifyLookahead")
        modify_lookahead(self, lookahead)

    def modify_lookahead(self, lookahead: Any) -> None:
        self.modifyLookahead(lookahead)

    def retract(self, retraction: Any) -> None:
        self._record("retract", retraction)
        self._require_joined("retract")
        retract_message(self, retraction)

    def queryLookahead(self) -> Any:  # noqa: N802
        self._record("queryLookahead")
        self._require_joined("queryLookahead")
        return query_lookahead(self)

    def query_lookahead(self) -> Any:
        return self.queryLookahead()

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

    def _time_management_state(self) -> tm.TimeAdvanceRequestState | Any:
        return build_time_management_state(self)

    def _time_management_federation(self, federation: Any) -> Any:
        return build_time_management_federation(federation)

    def _query_galt_for(self, target: Any) -> TimeQueryReturn:
        return query_galt_for(target)

    def _query_lits_for(self, target: Any) -> TimeQueryReturn:
        return query_lits_for(target)

    def _validate_tso_send_time(self, timestamp: Any) -> None:
        validate_tso_send_time(self, timestamp, invalid_logical_time_exc=InvalidLogicalTime)

    def _deliver_due_tso_callbacks_for_request(self, deliverable_messages: tuple[Any, ...]) -> None:
        deliver_due_tso_callbacks_for_request(self, deliverable_messages)
