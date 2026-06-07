"""Federation synchronization-point helpers and services."""
from __future__ import annotations

from typing import Iterable

from ... import handles as hla_handles
from ...enums import SynchronizationPointFailureReason
from ...handles import FederateHandle
from .state import FederationState, SynchronizationPointState


class PythonRTIFederationSyncMixin:
    """Synchronization-point helpers and public sync services."""

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

    def _complete_synchronization_point_if_ready(
        self,
        federation: FederationState,
        point: SynchronizationPointState,
    ) -> None:
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

    def _remove_federate_from_synchronization_points(
        self,
        federation: FederationState,
        handle: FederateHandle,
    ) -> None:
        for point in list(federation.synchronization_points.values()):
            point.targets.discard(handle)
            point.announced.discard(handle)
            point.achieved.discard(handle)
            point.failed.discard(handle)
            self._complete_synchronization_point_if_ready(federation, point)

    def _announce_open_synchronization_points_to_joiner(
        self,
        federation: FederationState,
        handle: FederateHandle,
    ) -> None:
        for point in list(federation.synchronization_points.values()):
            if point.open_to_late_joiners and handle not in point.reported():
                self._announce_synchronization_point(federation, point, handle)

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

    def _svc_synchronizationPointAchieved(
        self,
        synchronizationPointLabel: str,
        successIndicator: bool = True,
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        label = str(synchronizationPointLabel)
        point = federation.synchronization_points.get(label)
        if point is None:
            from ...exceptions import SynchronizationPointLabelNotAnnounced

            raise SynchronizationPointLabelNotAnnounced(label)
        assert self.state.handle is not None
        if self.state.handle not in point.announced:
            from ...exceptions import SynchronizationPointLabelNotAnnounced

            raise SynchronizationPointLabelNotAnnounced(label)
        if successIndicator:
            point.achieved.add(self.state.handle)
            point.failed.discard(self.state.handle)
        else:
            point.failed.add(self.state.handle)
            point.achieved.discard(self.state.handle)
        self._complete_synchronization_point_if_ready(federation, point)
