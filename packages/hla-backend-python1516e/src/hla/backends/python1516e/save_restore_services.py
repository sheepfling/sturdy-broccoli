"""Public save/restore service entrypoints."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from hla.rti1516e.enums import RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
from hla.rti1516e.exceptions import LogicalTimeAlreadyPassed
from hla.rti1516e.datatypes import FederateHandleSaveStatusPair, FederateRestoreStatus

from .save_restore_state import PythonRTISaveRestoreStateMixin

if TYPE_CHECKING:
    from .state import FederationState


class _SaveRestoreServicesContext(Protocol):
    state: Any

    def _require_joined(self) -> "FederationState": ...

    def _deliver(self, target: Any, method_name: str, *args: Any) -> None: ...

    def _coerce_time(self, value: Any) -> Any: ...

    def _time_lt(self, a: Any, b: Any) -> bool: ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _process_scheduled_saves(self, federation: "FederationState") -> None: ...

    def _refresh_all_mom_objects(self, federation: "FederationState", *, notify: bool = True) -> None: ...

    def _refresh_mom_federate_object(
        self,
        federation: "FederationState",
        federate: Any,
        *,
        notify: bool = True,
    ) -> None: ...

    def _start_federation_save(
        self,
        federation: "FederationState",
        label: str,
        theTime: Any | None = None,
    ) -> None: ...

    def _complete_save(self, *, success: bool) -> None: ...

    def _complete_restore(self, *, success: bool) -> None: ...


if TYPE_CHECKING:
    class _SaveRestoreServicesMixinBase(PythonRTISaveRestoreStateMixin, _SaveRestoreServicesContext):
        pass
else:
    class _SaveRestoreServicesMixinBase(PythonRTISaveRestoreStateMixin):
        pass


class PythonRTISaveRestoreServicesMixin(_SaveRestoreServicesMixinBase):
    """Public save/restore service methods."""

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
            from hla.rti1516e.exceptions import SaveNotInitiated

            raise SaveNotInitiated("No federation save is in progress")
        assert self.state.handle is not None
        federation.save_status[self.state.handle] = SaveStatus.FEDERATE_SAVING
        self._refresh_mom_federate_object(federation, self.state, notify=True)

    def _svc_federateSaveComplete(self) -> None:
        self._complete_save(success=True)

    def _svc_federateSaveNotComplete(self) -> None:
        self._complete_save(success=False)

    def _svc_abortFederationSave(self) -> None:
        federation = self._require_joined()
        if federation.save_label is None and federation.next_save_name is None:
            from hla.rti1516e.exceptions import SaveNotInProgress

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
            FederateHandleSaveStatusPair(
                handle,
                federation.save_status.get(handle, SaveStatus.NO_SAVE_IN_PROGRESS),
            )
            for handle in federation.federates
        ]
        self._deliver(self.state, "federationSaveStatusResponse", response)

    def _svc_requestFederationRestore(self, label: str) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        restore_label = str(label)
        if (
            restore_label not in federation.saved_time_states
            and restore_label not in federation.saved_object_snapshots
        ):
            self._deliver(self.state, "requestFederationRestoreFailed", restore_label)
            return
        federation.restore_label = restore_label
        federation.restore_status = {
            handle: RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
            for handle in federation.federates
        }
        self._deliver(self.state, "requestFederationRestoreSucceeded", restore_label)
        for federate in list(federation.federates.values()):
            federate.time_advancing = False
            federate.pending_time_advance = None
            federate.requested_time = None
            federate.time_advance_kind = None
            self._deliver(federate, "federationRestoreBegun")
            self._deliver(
                federate,
                "initiateFederateRestore",
                restore_label,
                federate.name or "",
                federate.handle,
            )
        self._refresh_all_mom_objects(federation, notify=True)

    def _svc_federateRestoreComplete(self) -> None:
        self._complete_restore(success=True)

    def _svc_federateRestoreNotComplete(self) -> None:
        self._complete_restore(success=False)

    def _svc_abortFederationRestore(self) -> None:
        federation = self._require_joined()
        if federation.restore_label is None:
            from hla.rti1516e.exceptions import RestoreNotInProgress

            raise RestoreNotInProgress("No federation restore is in progress")
        for federate in list(federation.federates.values()):
            self._deliver(
                federate, "federationNotRestored", RestoreFailureReason.RESTORE_ABORTED
            )
        federation.restore_label = None
        federation.restore_status.clear()

    def _svc_queryFederationRestoreStatus(self) -> None:
        federation = self._require_joined()
        response = [
            FederateRestoreStatus(
                handle,
                handle,
                federation.restore_status.get(handle, RestoreStatus.NO_RESTORE_IN_PROGRESS),
            )
            for handle in federation.federates
        ]
        self._deliver(self.state, "federationRestoreStatusResponse", response)
