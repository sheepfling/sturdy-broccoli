"""Lookup and naming support helpers for the in-memory Python RTI backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from hla2010 import handles as hla_handles
from hla2010.exceptions import (
    FederateHandleNotKnown,
    InvalidFederateHandle,
    InvalidRegion,
    InvalidTransportationName,
    InvalidTransportationType,
    NameNotFound,
    ObjectInstanceNotKnown,
)
from hla2010.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
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


class _SupportLookupContext(Protocol):
    engine: InMemoryRTIEngine
    state: FederateState
    config: PythonRTIConfig

    def _require_joined(self) -> FederationState: ...

    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None: ...

    def _enforce_fom_names(self, federation: FederationState) -> bool: ...

    def _time_factory(self) -> Any: ...


if TYPE_CHECKING:
    class _SupportLookupMixinBase(_SupportLookupContext):
        pass
else:
    class _SupportLookupMixinBase:
        pass


class PythonRTISupportLookupMixin(_SupportLookupMixinBase):
    """Name, handle, and instance lookup services."""

    def get_hla_version(self) -> str:
        return "HLA 1516-2010 Python in-memory RTI subset"

    def get_transportation_type_handle(
        self,
        transportationType: str | None = None,
    ) -> TransportationTypeHandle:
        federation = self._require_joined()
        if transportationType in (None, ""):
            return self.engine.transportation_reliable
        normalized = str(transportationType)
        handle = self._transportation_handle_by_name(normalized)
        if handle is None:
            raise InvalidTransportationName(normalized)
        if (
            federation.fom_catalog.transportation_names
            and normalized not in federation.fom_catalog.transportation_names
        ):
            raise InvalidTransportationName(normalized)
        return handle

    def get_transportation_type_name(self, theHandle: TransportationTypeHandle) -> str:
        self._require_joined()
        name = self._transportation_name_by_handle(theHandle)
        if name is None:
            raise InvalidTransportationType(repr(theHandle))
        return name

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
            federation.objects[theHandle]
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

    def _svc_getTransportationTypeHandle(
        self,
        transportationType: str | None = None,
    ) -> TransportationTypeHandle:
        return self.get_transportation_type_handle(transportationType)

    def _svc_getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        return self.get_transportation_type_name(theHandle)

    def _svc_getHLAversion(self) -> str:
        return self.get_hla_version()

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
