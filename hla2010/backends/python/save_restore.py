"""Save and restore coordination for the Python RTI backend."""
from __future__ import annotations

import copy
from typing import Any

from ...enums import RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
from ...exceptions import LogicalTimeAlreadyPassed, RestoreInProgress, SaveInProgress
from ...time import LogicalTimeFactory
from ...types import FederateHandleSaveStatusPair, FederateRestoreStatus
from ..python.state import FederateState, FederationState


class PythonRTISaveRestoreMixin:
    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None:
        if federation.save_label is not None:
            raise SaveInProgress(f"Federation save is in progress: {federation.save_label}")
        if federation.restore_label is not None:
            raise RestoreInProgress(f"Federation restore is in progress: {federation.restore_label}")

    def _snapshot_time_state(self, federation: FederationState) -> dict[Any, dict[str, Any]]:
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
        if federation.next_save_name is None or federation.next_save_time is None or federation.save_label is not None:
            return
        save_time = federation.next_save_time

        def no_blocking_tso(fed: FederateState) -> bool:
            return not any(self._time_le(getattr(msg, "timestamp"), save_time) for msg in self._queued_tso_messages(federation, fed))

        for fed in list(federation.federates.values()):
            if fed.time_constrained_enabled:
                if not no_blocking_tso(fed):
                    return
                next_grant = None
                request = fed.pending_time_advance
                if request is not None:
                    decision = self._compute_grant_decision(
                        federation,
                        fed,
                        request,
                        enforce_galt=self.config.enforce_galt,
                        nrg_enabled=self.config.non_regulated_grant_enabled,
                        factory=federation.time_factory,
                    )
                    next_grant = decision.grant_time if decision.can_grant else getattr(request, "requested_time", None)
                if not self._scheduled_save_time_reached(fed, save_time, next_grant_time=next_grant):
                    return

        self._start_federation_save(federation, federation.next_save_name, save_time)

    def _svc_requestFederationSave(self, label: str, theTime: Any | None = None) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if theTime is not None:
            save_time = self._coerce_time(theTime)
            if self._time_lt(save_time, self.state.current_time):
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
            from ...exceptions import SaveNotInitiated

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
            from ...exceptions import SaveNotInitiated

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
        if federation.save_label is None and federation.next_save_name is None:
            from ...exceptions import SaveNotInProgress

            raise SaveNotInProgress("No federation save is in progress")
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
        restore_label = str(label)
        if restore_label not in federation.saved_time_states and restore_label not in federation.saved_object_snapshots:
            self._deliver(self.state, "requestFederationRestoreFailed", restore_label)
            return
        federation.restore_label = restore_label
        federation.restore_status = {
            handle: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING for handle in federation.federates
        }
        self._deliver(self.state, "requestFederationRestoreSucceeded", restore_label)
        for federate in list(federation.federates.values()):
            federate.time_advancing = False
            federate.pending_time_advance = None
            federate.requested_time = None
            federate.time_advance_kind = None
            self._deliver(federate, "federationRestoreBegun")
            self._deliver(federate, "initiateFederateRestore", restore_label, federate.name or "", federate.handle)
        self._refresh_all_mom_objects(federation, notify=True)

    def _svc_federateRestoreComplete(self) -> None:
        self._complete_restore(success=True)

    def _svc_federateRestoreNotComplete(self) -> None:
        self._complete_restore(success=False)

    def _complete_restore(self, *, success: bool) -> None:
        federation = self._require_joined()
        if federation.restore_label is None:
            from ...exceptions import RestoreNotRequested

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
        if federation.restore_label is None:
            from ...exceptions import RestoreNotInProgress

            raise RestoreNotInProgress("No federation restore is in progress")
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


__all__ = ["PythonRTISaveRestoreMixin"]
