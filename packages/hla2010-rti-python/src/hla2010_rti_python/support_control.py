"""Control, advisory, normalization, and rate support helpers."""

from __future__ import annotations

from typing import Any

from hla2010 import handles as hla_handles
from hla2010.enums import OrderType, ResignAction, ServiceGroup
from hla2010.exceptions import (
    AttributeRelevanceAdvisorySwitchIsOff,
    AttributeRelevanceAdvisorySwitchIsOn,
    AttributeScopeAdvisorySwitchIsOff,
    AttributeScopeAdvisorySwitchIsOn,
    InteractionRelevanceAdvisorySwitchIsOff,
    InteractionRelevanceAdvisorySwitchIsOn,
    InvalidFederateHandle,
    InvalidOrderName,
    InvalidOrderType,
    InvalidResignAction,
    InvalidServiceGroup,
    InvalidUpdateRateDesignator,
    ObjectClassRelevanceAdvisorySwitchIsOff,
    ObjectClassRelevanceAdvisorySwitchIsOn,
)
from hla2010.handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
)

from .support_lookup import PythonRTISupportLookupMixin


class PythonRTISupportControlMixin(PythonRTISupportLookupMixin):
    """Support services for order, advisory switches, and update rates."""

    def _svc_getOrderName(self, orderType: Any) -> str:
        self._require_joined()
        if not isinstance(orderType, OrderType):
            raise InvalidOrderType(repr(orderType))
        return orderType.name

    def _svc_getOrderType(self, orderName: str):
        self._require_joined()
        normalized = str(orderName).replace("HLA", "").replace("_", "").replace(" ", "").upper()
        if normalized in {"RECEIVE", "RECEIVEORDER"}:
            return OrderType.RECEIVE
        if normalized in {"TIMESTAMP", "TIMESTAMPORDER", "TSO"}:
            return OrderType.TIMESTAMP
        raise InvalidOrderName(str(orderName))

    def _svc_getTransportationType(self, transportationName: str | None = None):
        return self.get_transportation_type_handle(transportationName)

    def _svc_getTransportationName(self, transportationType):
        return self.get_transportation_type_name(transportationType)

    def _svc_getAutomaticResignDirective(self):
        self._require_joined()
        return self.state.automatic_resign_directive

    def _svc_setAutomaticResignDirective(self, resignAction: Any) -> None:
        self._require_joined()
        if not isinstance(resignAction, ResignAction):
            raise InvalidResignAction(repr(resignAction))
        self.state.automatic_resign_directive = resignAction

    def _svc_enableObjectClassRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.object_class_relevance_advisory:
            raise ObjectClassRelevanceAdvisorySwitchIsOn(
                "Object class relevance advisory switch is already enabled"
            )
        self.state.object_class_relevance_advisory = True

    def _svc_disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.object_class_relevance_advisory:
            raise ObjectClassRelevanceAdvisorySwitchIsOff(
                "Object class relevance advisory switch is already disabled"
            )
        self.state.object_class_relevance_advisory = False

    def _svc_enableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOn(
                "Attribute relevance advisory switch is already enabled"
            )
        self.state.attribute_relevance_advisory = True

    def _svc_disableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOff(
                "Attribute relevance advisory switch is already disabled"
            )
        self.state.attribute_relevance_advisory = False

    def _svc_enableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOn(
                "Attribute scope advisory switch is already enabled"
            )
        self.state.attribute_scope_advisory = True

    def _svc_disableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOff(
                "Attribute scope advisory switch is already disabled"
            )
        self.state.attribute_scope_advisory = False

    def _svc_enableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOn(
                "Interaction relevance advisory switch is already enabled"
            )
        self.state.interaction_relevance_advisory = True

    def _svc_disableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOff(
                "Interaction relevance advisory switch is already disabled"
            )
        self.state.interaction_relevance_advisory = False

    def _all_known_dimensions(self) -> hla_handles.DimensionHandleSet:
        if not self.engine.dimensions_by_name:
            return hla_handles.DimensionHandleSet(
                [self.engine.get_or_create_dimension("HLAdefaultRoutingSpace")]
            )
        return hla_handles.DimensionHandleSet(self.engine.dimensions_by_name.values())

    def _svc_getAvailableDimensionsForClassAttribute(
        self,
        theClass: ObjectClassHandle,
        theAttribute: AttributeHandle,
    ) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.attribute_name(theClass, theAttribute)
        return self._all_known_dimensions()

    def _svc_getAvailableDimensionsForInteractionClass(
        self,
        theClass: InteractionClassHandle,
    ) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        return self._all_known_dimensions()

    def _svc_getUpdateRateValue(self, updateRateDesignator: str) -> float:
        federation = self._require_joined()
        designator = str(updateRateDesignator)
        normalized = "HLAdefault" if designator == "default" else designator
        if normalized in federation.fom_catalog.update_rates:
            return float(federation.fom_catalog.update_rates[normalized])
        if normalized not in {"HLAdefault"}:
            raise InvalidUpdateRateDesignator(str(updateRateDesignator))
        return 0.0

    def _svc_getUpdateRateValueForAttribute(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> float:
        _, instance = self._find_object(theObject)
        try:
            self.engine.attribute_name(instance.class_handle, theAttribute)
            rate_map = self.state.subscribed_object_update_rates.get(instance.class_handle, {})
            return float(rate_map.get(theAttribute, 0.0))
        except Exception:
            pass
        if theObject in self.state.known_object_classes:
            known_class = self.state.known_object_classes[theObject]
            attribute_name = self.engine.attribute_name(known_class, theAttribute)
            for subscribed_class, rate_map in self.state.subscribed_object_update_rates.items():
                if not self.engine.object_class_is_a(instance.class_handle, subscribed_class):
                    continue
                subscribed_attr = self.engine.object_class_for_handle(
                    subscribed_class
                ).attributes_by_name.get(attribute_name)
                if subscribed_attr is None or subscribed_attr not in rate_map:
                    continue
                return float(rate_map[subscribed_attr])
        self.engine.attribute_name(instance.class_handle, theAttribute)
        return 0.0

    def _svc_normalizeFederateHandle(self, theFederateHandle: FederateHandle) -> FederateHandle:
        federation = self._require_joined()
        if (
            not isinstance(theFederateHandle, FederateHandle)
            or theFederateHandle not in federation.federates
        ):
            raise InvalidFederateHandle(repr(theFederateHandle))
        return theFederateHandle

    def _svc_normalizeServiceGroup(self, theServiceGroup: Any):
        self._require_joined()
        if isinstance(theServiceGroup, ServiceGroup):
            return theServiceGroup
        key = str(theServiceGroup).replace(" ", "_").replace("-", "_").upper()
        try:
            return ServiceGroup[key]
        except KeyError as exc:
            raise InvalidServiceGroup(str(theServiceGroup)) from exc
