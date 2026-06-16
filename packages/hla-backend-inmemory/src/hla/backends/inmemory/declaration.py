"""Declaration-management services for the in-memory Python RTI backend."""
from __future__ import annotations

from typing import Any, Iterable

from hla.rti1516e.exceptions import FederateServiceInvocationsAreBeingReportedViaMOM, InvalidUpdateRateDesignator
from hla.rti1516e.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle
from .state import FederateState


class PythonRTIDeclarationMixin:
    """HLA publication, subscription, and advisory declaration services."""

    def _current_registration_interest_classes(self, publisher: FederateState) -> set[ObjectClassHandle]:
        federation = publisher.federation
        if federation is None:
            return set()
        result: set[ObjectClassHandle] = set()
        for published_class, published_attrs in publisher.published_objects.items():
            if not published_attrs:
                continue
            published_def = self.engine.object_class_for_handle(published_class)
            published_names = {self.engine.attribute_name(published_class, attr) for attr in published_attrs}
            if not published_names:
                continue
            for subscriber in federation.federates.values():
                if subscriber is publisher:
                    continue
                for subscribed_class, subscribed_attrs in subscriber.subscribed_objects.items():
                    if not self._object_matches_subscription(published_class, subscribed_class):
                        continue
                    subscribed_names = {
                        self.engine.attribute_name(subscribed_class, attr)
                        for attr in subscribed_attrs
                        if self.engine.attribute_name(subscribed_class, attr) in published_def.attributes_by_name
                    }
                    if published_names & subscribed_names:
                        result.add(published_class)
                        break
                if published_class in result:
                    break
        return result

    def _reconcile_registration_interest_for_publisher(self, publisher: FederateState) -> None:
        previous = set(publisher.registration_interest_classes)
        current = self._current_registration_interest_classes(publisher)
        publisher.registration_interest_classes = current
        for the_class in sorted(previous - current, key=lambda handle: handle.value):
            self._deliver(publisher, "stopRegistrationForObjectClass", the_class)
        for the_class in sorted(current - previous, key=lambda handle: handle.value):
            self._deliver(publisher, "startRegistrationForObjectClass", the_class)

    def _reconcile_registration_interest_for_all_publishers(self) -> None:
        federation = self.state.federation
        if federation is None:
            return
        for federate in list(federation.federates.values()):
            self._reconcile_registration_interest_for_publisher(federate)

    def _current_interaction_interest_classes(self, publisher: FederateState) -> set[InteractionClassHandle]:
        federation = publisher.federation
        if federation is None:
            return set()
        result: set[InteractionClassHandle] = set()
        for published_class in publisher.published_interactions:
            for subscriber in federation.federates.values():
                if subscriber is publisher:
                    continue
                if any(
                    self._interaction_matches_subscription(published_class, subscribed_class)
                    for subscribed_class in subscriber.subscribed_interactions
                ):
                    result.add(published_class)
                    break
        return result

    def _reconcile_interaction_interest_for_publisher(self, publisher: FederateState) -> None:
        previous = set(publisher.interaction_interest_classes)
        current = self._current_interaction_interest_classes(publisher)
        publisher.interaction_interest_classes = current
        for the_class in sorted(previous - current, key=lambda handle: handle.value):
            self._deliver(publisher, "turnInteractionsOff", the_class)
        for the_class in sorted(current - previous, key=lambda handle: handle.value):
            self._deliver(publisher, "turnInteractionsOn", the_class)

    def _reconcile_interaction_interest_for_all_publishers(self) -> None:
        federation = self.state.federation
        if federation is None:
            return
        for federate in list(federation.federates.values()):
            self._reconcile_interaction_interest_for_publisher(federate)

    def _validate_object_class_attributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: Iterable[AttributeHandle],
    ) -> set[AttributeHandle]:
        self.engine.object_class_for_handle(theClass)
        attrs = set(attributeList)
        for attr in attrs:
            self.engine.attribute_name(theClass, attr)
        return attrs

    def _resolve_update_rate_designator(self, federation, *unused: Any) -> tuple[float | None, str | None]:
        designator = next((str(arg) for arg in reversed(unused) if isinstance(arg, str)), None)
        if designator in (None, "", "default", "HLAdefault"):
            return (0.0, "HLAdefault") if designator is not None else (None, None)
        if designator not in federation.fom_catalog.update_rates:
            raise InvalidUpdateRateDesignator(designator)
        return float(federation.fom_catalog.update_rates[designator]), designator

    def _default_update_rate_for_attribute(
        self,
        federation: Any,
        object_class: ObjectClassHandle,
        attribute: AttributeHandle,
    ) -> float | None:
        class_name = self.engine.object_class_for_handle(object_class).name
        spec = federation.fom_catalog.object_classes.get(class_name)
        if spec is None:
            return None
        attribute_name = self.engine.attribute_name(object_class, attribute)
        designator = dict(spec.attribute_update_rates).get(attribute_name)
        if not designator:
            return None
        normalized = "HLAdefault" if designator == "default" else designator
        if normalized in federation.fom_catalog.update_rates:
            return float(federation.fom_catalog.update_rates[normalized])
        if normalized == "HLAdefault":
            return 0.0
        raise InvalidUpdateRateDesignator(str(designator))

    def _default_update_rate_designator_for_attribute(
        self,
        federation: Any,
        object_class: ObjectClassHandle,
        attribute: AttributeHandle,
    ) -> str | None:
        class_name = self.engine.object_class_for_handle(object_class).name
        spec = federation.fom_catalog.object_classes.get(class_name)
        if spec is None:
            return None
        attribute_name = self.engine.attribute_name(object_class, attribute)
        designator = dict(spec.attribute_update_rates).get(attribute_name)
        if not designator:
            return None
        normalized = "HLAdefault" if designator == "default" else str(designator)
        if normalized == "HLAdefault" or normalized in federation.fom_catalog.update_rates:
            return normalized
        raise InvalidUpdateRateDesignator(str(designator))

    def _svc_publishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = self._validate_object_class_attributes(theClass, attributeList)
        self.state.published_objects.setdefault(theClass, set()).update(attrs)
        self._reconcile_registration_interest_for_publisher(self.state)
        self._reconcile_update_interest_for_owned_objects(self.state, theClass)

    def _svc_unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        self.state.published_objects.pop(theClass, None)
        self._reconcile_registration_interest_for_publisher(self.state)
        self._reconcile_update_interest_for_owned_objects(self.state, theClass)

    def _svc_unpublishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs_to_remove = self._validate_object_class_attributes(theClass, attributeList)
        attrs = self.state.published_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(attrs_to_remove)
            if not attrs:
                self.state.published_objects.pop(theClass, None)
        self._reconcile_registration_interest_for_publisher(self.state)
        self._reconcile_update_interest_for_owned_objects(self.state, theClass)

    def _svc_subscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = self._validate_object_class_attributes(theClass, attributeList)
        explicit_update_rate, explicit_designator = self._resolve_update_rate_designator(federation, *unused)
        self.state.subscribed_objects.setdefault(theClass, set()).update(attrs)
        rate_map = self.state.subscribed_object_update_rates.setdefault(theClass, {})
        designator_map = self.state.subscribed_object_update_rate_designators.setdefault(theClass, {})
        for attr in attrs:
            resolved_rate = explicit_update_rate
            resolved_designator = explicit_designator
            if resolved_rate is None:
                resolved_rate = self._default_update_rate_for_attribute(federation, theClass, attr)
                resolved_designator = self._default_update_rate_designator_for_attribute(federation, theClass, attr)
            if resolved_rate is None:
                rate_map.pop(attr, None)
                designator_map.pop(attr, None)
            else:
                rate_map[attr] = resolved_rate
                if resolved_designator is None:
                    designator_map.pop(attr, None)
                else:
                    designator_map[attr] = resolved_designator
        if not rate_map:
            self.state.subscribed_object_update_rates.pop(theClass, None)
        if not designator_map:
            self.state.subscribed_object_update_rate_designators.pop(theClass, None)
        self._discover_existing_objects(self.state, theClass)
        self._reconcile_scope_for_all_known_objects(self.state)
        self._reconcile_registration_interest_for_all_publishers()

    def _svc_subscribeObjectClassAttributesPassively(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle], *unused: Any) -> None:
        self._svc_subscribeObjectClassAttributes(theClass, attributeList, *unused)

    def _svc_unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.object_class_for_handle(theClass)
        self.state.subscribed_objects.pop(theClass, None)
        self.state.subscribed_object_update_rates.pop(theClass, None)
        self.state.subscribed_object_update_rate_designators.pop(theClass, None)
        self._reconcile_scope_for_all_known_objects(self.state)

    def _svc_unsubscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: Iterable[AttributeHandle]) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs_to_remove = self._validate_object_class_attributes(theClass, attributeList)
        attrs = self.state.subscribed_objects.get(theClass)
        if attrs is not None:
            attrs.difference_update(attrs_to_remove)
            if not attrs:
                self.state.subscribed_objects.pop(theClass, None)
        rate_map = self.state.subscribed_object_update_rates.get(theClass)
        if rate_map is not None:
            for attr in attrs_to_remove:
                rate_map.pop(attr, None)
            if not rate_map:
                self.state.subscribed_object_update_rates.pop(theClass, None)
        designator_map = self.state.subscribed_object_update_rate_designators.get(theClass)
        if designator_map is not None:
            for attr in attrs_to_remove:
                designator_map.pop(attr, None)
            if not designator_map:
                self.state.subscribed_object_update_rate_designators.pop(theClass, None)
        self._reconcile_scope_for_all_known_objects(self.state)
        self._reconcile_registration_interest_for_all_publishers()

    def _svc_publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theInteraction)
        self.state.published_interactions.add(theInteraction)
        self._reconcile_interaction_interest_for_publisher(self.state)

    def _svc_unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theInteraction)
        self.state.published_interactions.discard(theInteraction)
        self._reconcile_interaction_interest_for_publisher(self.state)

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
        self._reconcile_interaction_interest_for_all_publishers()

    def _svc_subscribeInteractionClassPassively(self, theClass: InteractionClassHandle, *unused: Any) -> None:
        self._svc_subscribeInteractionClass(theClass, *unused)

    def _svc_unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.interaction_for_handle(theClass)
        self.state.subscribed_interactions.discard(theClass)
        self._reconcile_interaction_interest_for_all_publishers()

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
