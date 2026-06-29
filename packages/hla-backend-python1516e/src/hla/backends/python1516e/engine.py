"""In-memory engine and handle registry for the Python RTI backend."""
from __future__ import annotations

from threading import RLock
from typing import Any, Iterable

from hla.fom import FOMModule, FOMResolver
from hla.rti1516e.exceptions import (
    AttributeNotDefined,
    InteractionParameterNotDefined,
    InvalidDimensionHandle,
    InvalidInteractionClassHandle,
    InvalidObjectClassHandle,
)
from hla.rti1516e.handles import (
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
from hla.rti1516e.time import DEFAULT_TIME_FACTORY_REGISTRY, TimeFactoryRegistry

from .state import FederateState, FederationState, InteractionClassDef, ObjectClassDef


class InMemoryRTIEngine:
    """Shared RTI state used by one or more PythonRTIBackend instances."""

    def __init__(
        self,
        *,
        name: str = "python1516e-rti",
        fom_resolver: FOMResolver | None = None,
        time_factories: TimeFactoryRegistry | None = None,
    ) -> None:
        self.name = name
        self._lock = RLock()
        self._next_backend_id = 1
        self._next_values: dict[type[Any], int] = {
            FederateHandle: 1,
            ObjectClassHandle: 1,
            AttributeHandle: 1,
            ObjectInstanceHandle: 1,
            InteractionClassHandle: 1,
            ParameterHandle: 1,
            DimensionHandle: 1,
            RegionHandle: 1,
            TransportationTypeHandle: 1,
            MessageRetractionHandle: 1,
        }
        self._next_tso_sequence = 1
        self.federations: dict[str, FederationState] = {}
        self.object_classes_by_name: dict[str, ObjectClassDef] = {}
        self.object_class_by_handle: dict[ObjectClassHandle, ObjectClassDef] = {}
        self.interactions_by_name: dict[str, InteractionClassDef] = {}
        self.interaction_by_handle: dict[InteractionClassHandle, InteractionClassDef] = {}
        self.dimensions_by_name: dict[str, DimensionHandle] = {}
        self.dimension_names: dict[DimensionHandle, str] = {}
        self.transportation_reliable = self._alloc(TransportationTypeHandle)
        self.transportation_best_effort = self._alloc(TransportationTypeHandle)
        self.fom_resolver = fom_resolver or FOMResolver()
        self.time_factories = time_factories or DEFAULT_TIME_FACTORY_REGISTRY
        self._bootstrap_standard_names()

    def _bootstrap_standard_names(self) -> None:
        self.get_or_create_object_class("HLAobjectRoot")
        self.get_or_create_interaction_class("HLAinteractionRoot")
        self.get_or_create_dimension("HLAdefaultRoutingSpace")

    def new_federate_state(self) -> FederateState:
        with self._lock:
            backend_id = self._next_backend_id
            self._next_backend_id += 1
            return FederateState(backend_id=backend_id)

    def _alloc(self, handle_type: type[Any]) -> Any:
        value = self._next_values[handle_type]
        self._next_values[handle_type] = value + 1
        return handle_type(value)

    def _next_sequence(self) -> int:
        value = self._next_tso_sequence
        self._next_tso_sequence += 1
        return value

    def get_or_create_object_class(self, name: str) -> ObjectClassDef:
        with self._lock:
            if name not in self.object_classes_by_name:
                handle = self._alloc(ObjectClassHandle)
                definition = ObjectClassDef(name=str(name), handle=handle)
                self.object_classes_by_name[str(name)] = definition
                self.object_class_by_handle[handle] = definition
            return self.object_classes_by_name[str(name)]

    def object_class_for_handle(self, handle: ObjectClassHandle) -> ObjectClassDef:
        try:
            return self.object_class_by_handle[handle]
        except KeyError as exc:
            raise InvalidObjectClassHandle(repr(handle)) from exc

    def object_class_is_a(self, candidate: ObjectClassHandle, subscribed: ObjectClassHandle) -> bool:
        candidate_name = self.object_class_for_handle(candidate).name
        subscribed_name = self.object_class_for_handle(subscribed).name
        return candidate_name == subscribed_name or candidate_name.startswith(subscribed_name + ".")

    def get_or_create_attribute(self, object_class: ObjectClassHandle, name: str) -> AttributeHandle:
        definition = self.object_class_for_handle(object_class)
        if name not in definition.attributes_by_name:
            handle = self._alloc(AttributeHandle)
            definition.attributes_by_name[str(name)] = handle
            definition.attribute_names[handle] = str(name)
        return definition.attributes_by_name[str(name)]

    def attribute_name(self, object_class: ObjectClassHandle, attribute: AttributeHandle) -> str:
        definition = self.object_class_for_handle(object_class)
        try:
            return definition.attribute_names[attribute]
        except KeyError as exc:
            raise AttributeNotDefined(repr(attribute)) from exc

    def get_or_create_interaction_class(self, name: str) -> InteractionClassDef:
        with self._lock:
            if name not in self.interactions_by_name:
                handle = self._alloc(InteractionClassHandle)
                definition = InteractionClassDef(name=str(name), handle=handle)
                self.interactions_by_name[str(name)] = definition
                self.interaction_by_handle[handle] = definition
            return self.interactions_by_name[str(name)]

    def interaction_for_handle(self, handle: InteractionClassHandle) -> InteractionClassDef:
        try:
            return self.interaction_by_handle[handle]
        except KeyError as exc:
            raise InvalidInteractionClassHandle(repr(handle)) from exc

    def interaction_class_is_a(self, candidate: InteractionClassHandle, subscribed: InteractionClassHandle) -> bool:
        candidate_name = self.interaction_for_handle(candidate).name
        subscribed_name = self.interaction_for_handle(subscribed).name
        return candidate_name == subscribed_name or candidate_name.startswith(subscribed_name + ".")

    def get_or_create_parameter(self, interaction: InteractionClassHandle, name: str) -> ParameterHandle:
        definition = self.interaction_for_handle(interaction)
        if name not in definition.parameters_by_name:
            handle = self._alloc(ParameterHandle)
            definition.parameters_by_name[str(name)] = handle
            definition.parameter_names[handle] = str(name)
        return definition.parameters_by_name[str(name)]

    def parameter_name(self, interaction: InteractionClassHandle, parameter: ParameterHandle) -> str:
        definition = self.interaction_for_handle(interaction)
        try:
            return definition.parameter_names[parameter]
        except KeyError as exc:
            raise InteractionParameterNotDefined(repr(parameter)) from exc

    def get_or_create_dimension(self, name: str) -> DimensionHandle:
        with self._lock:
            if name not in self.dimensions_by_name:
                handle = self._alloc(DimensionHandle)
                self.dimensions_by_name[str(name)] = handle
                self.dimension_names[handle] = str(name)
            return self.dimensions_by_name[str(name)]

    def dimension_name(self, handle: DimensionHandle) -> str:
        try:
            return self.dimension_names[handle]
        except KeyError as exc:
            raise InvalidDimensionHandle(repr(handle)) from exc

    def install_fom_module(self, module: FOMModule) -> None:
        with self._lock:
            for object_spec in module.object_classes:
                object_def = self.get_or_create_object_class(object_spec.full_name)
                for attribute_name in object_spec.attributes:
                    self.get_or_create_attribute(object_def.handle, attribute_name)

            for interaction_spec in module.interaction_classes:
                interaction_def = self.get_or_create_interaction_class(interaction_spec.full_name)
                for parameter_name in interaction_spec.parameters:
                    self.get_or_create_parameter(interaction_def.handle, parameter_name)

            for dimension_name in module.dimensions:
                self.get_or_create_dimension(dimension_name)

    def install_fom_modules(self, modules: Iterable[FOMModule]) -> None:
        for module in modules:
            self.install_fom_module(module)


__all__ = ["InMemoryRTIEngine"]
