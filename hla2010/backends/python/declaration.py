"""Declaration-management services for the in-memory Python RTI backend."""
from __future__ import annotations

from typing import Any, Iterable

from ...exceptions import FederateServiceInvocationsAreBeingReportedViaMOM
from ...handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle
from .state import FederateState


class PythonRTIDeclarationMixin:
    """HLA publication, subscription, and advisory declaration services."""

    def _svc_publishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        attrs = set(attributeList)
        self.state.published_objects.setdefault(theClass, set()).update(attrs)

    def _svc_unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        self.state.published_objects.pop(theClass, None)

    def _svc_unpublishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        attrs = self.state.published_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(set(attributeList))
            if not attrs:
                self.state.published_objects.pop(theClass, None)

    def _svc_subscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        attrs = set(attributeList)
        self.state.subscribed_objects.setdefault(theClass, set()).update(attrs)
        self._discover_existing_objects(self.state, theClass)

    def _svc_subscribeObjectClassAttributesPassively(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        self._svc_subscribeObjectClassAttributes(theClass, attributeList, *unused)

    def _svc_unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.state.subscribed_objects.pop(theClass, None)

    def _svc_unsubscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        attrs = self.state.subscribed_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(set(attributeList))
            if not attrs:
                self.state.subscribed_objects.pop(theClass, None)

    def _svc_publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theInteraction)
        self.state.published_interactions.add(theInteraction)

    def _svc_unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theInteraction)
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
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theClass)
        if self.state.service_reporting and self._is_service_invocation_report_handle(theClass):
            raise FederateServiceInvocationsAreBeingReportedViaMOM(
                "Disable MOM service reporting before subscribing to HLAreportServiceInvocation"
            )
        self.state.subscribed_interactions.add(theClass)

    def _svc_subscribeInteractionClassPassively(self, theClass: InteractionClassHandle, *unused: Any) -> None:
        self._svc_subscribeInteractionClass(theClass, *unused)

    def _svc_unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theClass)
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
