"""Shared multi-federate Java-shaped shim kernel facade."""
from __future__ import annotations

from .java_shim_records import (
    SharedJavaFederationRecord,
    SharedJavaObjectRecord,
    SharedJavaSynchronizationPoint,
)
from typing import Callable, TypeVar

from .java_shim_runtime import SharedInProcessJavaRTIShim
from .java_shim_types import (
    JavaAttributeHandle,
    JavaDimensionHandle,
    JavaInteractionClassHandle,
    JavaObjectClassHandle,
    JavaParameterHandle,
    JavaRegionHandle,
    JavaTransportationTypeHandle,
)


TJavaShimHandle = TypeVar("TJavaShimHandle")


class SharedJavaShimKernel:
    def __init__(self) -> None:
        self._next_handle = 1
        self.transportation_reliable = JavaTransportationTypeHandle(self._alloc_value())
        self.federations: dict[str, SharedJavaFederationRecord] = {}
        self.object_classes: dict[str, JavaObjectClassHandle] = {}
        self.object_class_names: dict[JavaObjectClassHandle, str] = {}
        self.attributes: dict[tuple[JavaObjectClassHandle, str], JavaAttributeHandle] = {}
        self.attribute_names: dict[tuple[JavaObjectClassHandle, JavaAttributeHandle], str] = {}
        self.interaction_classes: dict[str, JavaInteractionClassHandle] = {}
        self.interaction_class_names: dict[JavaInteractionClassHandle, str] = {}
        self.parameters: dict[tuple[JavaInteractionClassHandle, str], JavaParameterHandle] = {}
        self.parameter_names: dict[tuple[JavaInteractionClassHandle, JavaParameterHandle], str] = {}
        self.dimensions: dict[str, JavaDimensionHandle] = {}
        self.dimension_names: dict[JavaDimensionHandle, str] = {}
        self.regions: dict[JavaRegionHandle, set[JavaDimensionHandle]] = {}

    def _alloc_value(self) -> int:
        value = self._next_handle
        self._next_handle += 1
        return value

    def alloc(self, handle_type: Callable[[int], TJavaShimHandle]) -> TJavaShimHandle:
        return handle_type(self._alloc_value())


__all__ = [
    "SharedInProcessJavaRTIShim",
    "SharedJavaFederationRecord",
    "SharedJavaObjectRecord",
    "SharedJavaShimKernel",
    "SharedJavaSynchronizationPoint",
]
