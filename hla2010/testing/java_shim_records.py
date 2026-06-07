"""Shared record types for the multi-federate Java shim."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .java_shim_types import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaFederateHandle,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
)

if TYPE_CHECKING:
    from .java_shim_runtime import SharedInProcessJavaRTIShim


@dataclass
class SharedJavaPendingAcquisition:
    requester: "SharedInProcessJavaRTIShim"
    tag: JavaByteArray


@dataclass
class SharedJavaObjectRecord:
    handle: JavaObjectInstanceHandle
    class_handle: JavaObjectClassHandle
    name: str
    owner: "SharedInProcessJavaRTIShim"
    attributes: dict[JavaAttributeHandle, JavaByteArray] | None = None
    attribute_owners: dict[JavaAttributeHandle, JavaFederateHandle | None] | None = None
    pending_acquisitions: dict[JavaAttributeHandle, SharedJavaPendingAcquisition] | None = None
    negotiated_divestiture_attrs: set[JavaAttributeHandle] | None = None

    def __post_init__(self) -> None:
        self.attributes = {} if self.attributes is None else self.attributes
        self.attribute_owners = {} if self.attribute_owners is None else self.attribute_owners
        self.pending_acquisitions = {} if self.pending_acquisitions is None else self.pending_acquisitions
        self.negotiated_divestiture_attrs = set() if self.negotiated_divestiture_attrs is None else self.negotiated_divestiture_attrs


@dataclass
class SharedJavaSynchronizationPoint:
    label: str
    tag: JavaByteArray
    announced: set[JavaFederateHandle] | None = None
    awaiting: set[JavaFederateHandle] | None = None
    failed: set[JavaFederateHandle] | None = None

    def __post_init__(self) -> None:
        self.announced = set() if self.announced is None else self.announced
        self.awaiting = set() if self.awaiting is None else self.awaiting
        self.failed = set() if self.failed is None else self.failed


@dataclass
class SharedJavaFederationRecord:
    name: str
    logical_time_name: str = "HLAinteger64Time"
    federates_by_handle: dict[JavaFederateHandle, "SharedInProcessJavaRTIShim"] | None = None
    federate_names: dict[str, JavaFederateHandle] | None = None
    objects: dict[JavaObjectInstanceHandle, SharedJavaObjectRecord] | None = None
    object_names: dict[str, JavaObjectInstanceHandle] | None = None
    synchronization_points: dict[str, SharedJavaSynchronizationPoint] | None = None

    def __post_init__(self) -> None:
        self.federates_by_handle = {} if self.federates_by_handle is None else self.federates_by_handle
        self.federate_names = {} if self.federate_names is None else self.federate_names
        self.objects = {} if self.objects is None else self.objects
        self.object_names = {} if self.object_names is None else self.object_names
        self.synchronization_points = {} if self.synchronization_points is None else self.synchronization_points
