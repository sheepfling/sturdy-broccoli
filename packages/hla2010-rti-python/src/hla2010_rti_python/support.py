"""Support-service helpers for the in-memory Python RTI backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from hla2010 import handles as hla_handles
from hla2010.enums import OrderType, ResignAction, ServiceGroup
from hla2010.exceptions import (
    AttributeRelevanceAdvisorySwitchIsOff,
    AttributeRelevanceAdvisorySwitchIsOn,
    AttributeScopeAdvisorySwitchIsOff,
    AttributeScopeAdvisorySwitchIsOn,
    FederateHandleNotKnown,
    InteractionRelevanceAdvisorySwitchIsOff,
    InteractionRelevanceAdvisorySwitchIsOn,
    InvalidFederateHandle,
    InvalidOrderName,
    InvalidOrderType,
    InvalidRegion,
    InvalidResignAction,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationType,
    InvalidUpdateRateDesignator,
    NameNotFound,
    ObjectClassRelevanceAdvisorySwitchIsOff,
    ObjectClassRelevanceAdvisorySwitchIsOn,
    ObjectInstanceNotKnown,
)
from hla2010.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    TransportationTypeHandle,
)
from .state import FederationState, ObjectInstance

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, PythonRTIConfig


class _SupportContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: "FederateState"
    config: "PythonRTIConfig"

    def _require_joined(self) -> FederationState: ...

    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None: ...

    def _enforce_fom_names(self, federation: FederationState) -> bool: ...

    def _time_factory(self) -> Any: ...

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle | None: ...

    def _transportation_name_by_handle(self, handle: TransportationTypeHandle) -> str | None: ...

    def _find_object(self, theObject: ObjectInstanceHandle) -> tuple[FederationState, ObjectInstance]: ...


if TYPE_CHECKING:
    class _SupportMixinBase(_SupportContext):
        pass
else:
    class _SupportMixinBase:
        pass


class PythonRTISupportMixin(_SupportMixinBase):
    """HLA support services, factories, and normalization helpers."""

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle | None:
        normalized = str(name).strip()
        if normalized == "HLAreliable":
            return self.engine.transportation_reliable
        if normalized == "HLAbestEffort":
            return self.engine.transportation_best_effort
        return None

    def _transportation_name_by_handle(self, handle: TransportationTypeHandle) -> str | None:
        if handle == self.engine.transportation_reliable:
            return "HLAreliable"
        if handle == self.engine.transportation_best_effort:
            return "HLAbestEffort"
        return None

    def _find_object(self, theObject: ObjectInstanceHandle) -> tuple[FederationState, ObjectInstance]:
        federation = self._require_joined()
        try:
            return federation, federation.objects[theObject]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(theObject)) from exc

    def _svc_getFederateName(self, theHandle: FederateHandle | None = None) -> str:
        federation = self._require_joined()
        if theHandle is None:
            if self.state.name is None:
                raise FederateHandleNotKnown("Current federate has no name")
            return self.state.name
        if not isinstance(theHandle, FederateHandle):
            raise InvalidFederateHandle(repr(theHandle))
        target = federation.federates.get(theHandle)
        if target is None or target.name is None:
            raise FederateHandleNotKnown(repr(theHandle))
        return target.name

    def _svc_getFederateHandle(self, theName: str) -> FederateHandle:
        federation = self._require_joined()
        for handle, federate in federation.federates.items():
            if federate.name == theName:
                return handle
        raise NameNotFound(str(theName))

    def _svc_getObjectClassHandle(self, theName: str) -> ObjectClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if name not in self.engine.object_classes_by_name:
            raise NameNotFound(name)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.object_classes:
            raise NameNotFound(name)
        return self.engine.object_classes_by_name[name].handle

    def _svc_getObjectClassName(self, theHandle: ObjectClassHandle) -> str:
        self._require_joined()
        return self.engine.object_class_for_handle(theHandle).name

    def _svc_getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:
        federation = self._require_joined()
        class_def = self.engine.object_class_for_handle(whichClass)
        name = str(theName)
        spec = federation.fom_catalog.object_classes.get(class_def.name)
        if spec is not None and name not in spec.attributes:
            raise NameNotFound(name)
        if name not in class_def.attributes_by_name:
            raise NameNotFound(name)
        return class_def.attributes_by_name[name]

    def _svc_getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:
        self._require_joined()
        return self.engine.attribute_name(whichClass, theHandle)

    def _svc_getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if name not in self.engine.interactions_by_name:
            raise NameNotFound(name)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.interaction_classes:
            raise NameNotFound(name)
        return self.engine.interactions_by_name[name].handle

    def _svc_getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:
        self._require_joined()
        return self.engine.interaction_for_handle(theHandle).name

    def _svc_getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:
        federation = self._require_joined()
        class_def = self.engine.interaction_for_handle(whichClass)
        name = str(theName)
        spec = federation.fom_catalog.interaction_classes.get(class_def.name)
        if spec is not None and name not in spec.parameters:
            raise NameNotFound(name)
        if name not in class_def.parameters_by_name:
            raise NameNotFound(name)
        return class_def.parameters_by_name[name]

    def _svc_getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:
        self._require_joined()
        return self.engine.parameter_name(whichClass, theHandle)

    def _svc_getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:
        self._require_joined()
        try:
            return self.state.known_object_names[str(theName)]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(theName)) from exc

    def _svc_getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:
        federation = self._require_joined()
        if theHandle in self.state.known_object_classes:
            return federation.objects[theHandle].name
        try:
            instance = federation.objects[theHandle]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(theHandle)) from exc
        raise ObjectInstanceNotKnown(repr(theHandle))

    def _svc_getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:
        federation = self._require_joined()
        known_class = self.state.known_object_classes.get(theObject)
        if known_class is not None:
            return known_class
        try:
            instance = federation.objects[theObject]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(theObject)) from exc
        if instance.owner == self.state.handle:
            self.state.known_object_classes[theObject] = instance.class_handle
            self.state.known_object_names[instance.name] = theObject
            return instance.class_handle
        raise ObjectInstanceNotKnown(repr(theObject))

    def _svc_getDimensionHandle(self, theName: str) -> DimensionHandle:
        federation = self._require_joined()
        name = str(theName)
        if name not in self.engine.dimensions_by_name:
            raise NameNotFound(name)
        if self._enforce_fom_names(federation) and federation.fom_catalog.dimensions and name not in federation.fom_catalog.dimensions:
            raise NameNotFound(name)
        return self.engine.dimensions_by_name[name]

    def _svc_getDimensionName(self, theHandle: DimensionHandle) -> str:
        self._require_joined()
        return self.engine.dimension_name(theHandle)

    def _svc_getTransportationTypeHandle(self, transportationType: str | None = None) -> TransportationTypeHandle:
        federation = self._require_joined()
        if transportationType in (None, ""):
            return self.engine.transportation_reliable
        normalized = str(transportationType)
        handle = self._transportation_handle_by_name(normalized)
        if handle is None:
            raise InvalidTransportationName(normalized)
        if federation.fom_catalog.transportation_names and normalized not in federation.fom_catalog.transportation_names:
            raise InvalidTransportationName(normalized)
        return handle

    def _svc_getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        self._require_joined()
        name = self._transportation_name_by_handle(theHandle)
        if name is None:
            raise InvalidTransportationType(repr(theHandle))
        return name

    def _svc_getHLAversion(self) -> str:
        return "HLA 1516-2010 Python in-memory RTI subset"

    def _svc_getTimeFactory(self):
        self._require_joined()
        return self._time_factory()

    def _svc_getDimensionHandleSet(self, region: RegionHandle) -> hla_handles.DimensionHandleSet:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        try:
            return hla_handles.DimensionHandleSet(self.state.regions[region])
        except KeyError as exc:
            raise InvalidRegion(repr(region)) from exc

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

    def _svc_getTransportationType(self, transportationName: str | None = None) -> TransportationTypeHandle:
        return self._svc_getTransportationTypeHandle(transportationName)

    def _svc_getTransportationName(self, transportationType: TransportationTypeHandle) -> str:
        return self._svc_getTransportationTypeName(transportationType)

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
            raise ObjectClassRelevanceAdvisorySwitchIsOn("Object class relevance advisory switch is already enabled")
        self.state.object_class_relevance_advisory = True

    def _svc_disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.object_class_relevance_advisory:
            raise ObjectClassRelevanceAdvisorySwitchIsOff("Object class relevance advisory switch is already disabled")
        self.state.object_class_relevance_advisory = False

    def _svc_enableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOn("Attribute relevance advisory switch is already enabled")
        self.state.attribute_relevance_advisory = True

    def _svc_disableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOff("Attribute relevance advisory switch is already disabled")
        self.state.attribute_relevance_advisory = False

    def _svc_enableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOn("Attribute scope advisory switch is already enabled")
        self.state.attribute_scope_advisory = True

    def _svc_disableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOff("Attribute scope advisory switch is already disabled")
        self.state.attribute_scope_advisory = False

    def _svc_enableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOn("Interaction relevance advisory switch is already enabled")
        self.state.interaction_relevance_advisory = True

    def _svc_disableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOff("Interaction relevance advisory switch is already disabled")
        self.state.interaction_relevance_advisory = False

    def _all_known_dimensions(self) -> hla_handles.DimensionHandleSet:
        if not self.engine.dimensions_by_name:
            return hla_handles.DimensionHandleSet([self.engine.get_or_create_dimension("HLAdefaultRoutingSpace")])
        return hla_handles.DimensionHandleSet(self.engine.dimensions_by_name.values())

    def _svc_getAvailableDimensionsForClassAttribute(self, theClass: ObjectClassHandle, theAttribute: AttributeHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.attribute_name(theClass, theAttribute)
        return self._all_known_dimensions()

    def _svc_getAvailableDimensionsForInteractionClass(self, theClass: InteractionClassHandle) -> hla_handles.DimensionHandleSet:
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

    def _svc_getUpdateRateValueForAttribute(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> float:
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
                subscribed_attr = self.engine.object_class_for_handle(subscribed_class).attributes_by_name.get(attribute_name)
                if subscribed_attr is None or subscribed_attr not in rate_map:
                    continue
                return float(rate_map[subscribed_attr])
        self.engine.attribute_name(instance.class_handle, theAttribute)
        return 0.0

    def _svc_normalizeFederateHandle(self, theFederateHandle: FederateHandle) -> FederateHandle:
        federation = self._require_joined()
        if not isinstance(theFederateHandle, FederateHandle) or theFederateHandle not in federation.federates:
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

    def _svc_getAttributeHandleFactory(self) -> hla_handles.AttributeHandleFactory:
        self._require_joined()
        return hla_handles.AttributeHandleFactory()

    def _svc_getAttributeHandleSetFactory(self) -> hla_handles.AttributeHandleSetFactory:
        self._require_joined()
        return hla_handles.AttributeHandleSetFactory()

    def _svc_getAttributeHandleValueMapFactory(self) -> hla_handles.AttributeHandleValueMapFactory:
        self._require_joined()
        return hla_handles.AttributeHandleValueMapFactory()

    def _svc_getAttributeSetRegionSetPairListFactory(self) -> hla_handles.AttributeSetRegionSetPairListFactory:
        self._require_joined()
        return hla_handles.AttributeSetRegionSetPairListFactory()

    def _svc_getDimensionHandleFactory(self) -> hla_handles.DimensionHandleFactory:
        self._require_joined()
        return hla_handles.DimensionHandleFactory()

    def _svc_getDimensionHandleSetFactory(self) -> hla_handles.DimensionHandleSetFactory:
        self._require_joined()
        return hla_handles.DimensionHandleSetFactory()

    def _svc_getFederateHandleFactory(self) -> hla_handles.FederateHandleFactory:
        self._require_joined()
        return hla_handles.FederateHandleFactory()

    def _svc_getFederateHandleSetFactory(self) -> hla_handles.FederateHandleSetFactory:
        self._require_joined()
        return hla_handles.FederateHandleSetFactory()

    def _svc_getInteractionClassHandleFactory(self) -> hla_handles.InteractionClassHandleFactory:
        self._require_joined()
        return hla_handles.InteractionClassHandleFactory()

    def _svc_getObjectClassHandleFactory(self) -> hla_handles.ObjectClassHandleFactory:
        self._require_joined()
        return hla_handles.ObjectClassHandleFactory()

    def _svc_getObjectInstanceHandleFactory(self) -> hla_handles.ObjectInstanceHandleFactory:
        self._require_joined()
        return hla_handles.ObjectInstanceHandleFactory()

    def _svc_getParameterHandleFactory(self) -> hla_handles.ParameterHandleFactory:
        self._require_joined()
        return hla_handles.ParameterHandleFactory()

    def _svc_getParameterHandleValueMapFactory(self) -> hla_handles.ParameterHandleValueMapFactory:
        self._require_joined()
        return hla_handles.ParameterHandleValueMapFactory()

    def _svc_getRegionHandleSetFactory(self) -> hla_handles.RegionHandleSetFactory:
        self._require_joined()
        return hla_handles.RegionHandleSetFactory()

    def _svc_getTransportationTypeHandleFactory(self) -> hla_handles.TransportationTypeHandleFactory:
        self._require_joined()
        return hla_handles.TransportationTypeHandleFactory()

    def _svc_decodeMessageRetractionHandle(self, buffer: bytes) -> MessageRetractionHandle:
        return MessageRetractionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeFederateHandle(self, buffer: bytes) -> FederateHandle:
        return FederateHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectClassHandle(self, buffer: bytes) -> ObjectClassHandle:
        return ObjectClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeAttributeHandle(self, buffer: bytes) -> AttributeHandle:
        return AttributeHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectInstanceHandle(self, buffer: bytes) -> ObjectInstanceHandle:
        return ObjectInstanceHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeInteractionClassHandle(self, buffer: bytes) -> InteractionClassHandle:
        return InteractionClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeParameterHandle(self, buffer: bytes) -> ParameterHandle:
        return ParameterHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeDimensionHandle(self, buffer: bytes) -> DimensionHandle:
        return DimensionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeRegionHandle(self, buffer: bytes) -> RegionHandle:
        return RegionHandle.decode(buffer)  # type: ignore[return-value]


__all__ = ["PythonRTISupportMixin"]
