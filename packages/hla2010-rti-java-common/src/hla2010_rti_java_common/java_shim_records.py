"""Shared record types for the multi-federate Java shim."""
from __future__ import annotations

from dataclasses import dataclass, field
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
    attributes: dict[JavaAttributeHandle, JavaByteArray] = field(default_factory=dict)
    attribute_owners: dict[JavaAttributeHandle, JavaFederateHandle | None] = field(default_factory=dict)
    pending_acquisitions: dict[JavaAttributeHandle, SharedJavaPendingAcquisition] = field(default_factory=dict)
    negotiated_divestiture_attrs: set[JavaAttributeHandle] = field(default_factory=set)


@dataclass
class SharedJavaSynchronizationPoint:
    label: str
    tag: JavaByteArray
    announced: set[JavaFederateHandle] = field(default_factory=set)
    awaiting: set[JavaFederateHandle] = field(default_factory=set)
    failed: set[JavaFederateHandle] = field(default_factory=set)


@dataclass
class SharedJavaFederationRecord:
    name: str
    logical_time_name: str = "HLAinteger64Time"
    federates_by_handle: dict[JavaFederateHandle, "SharedInProcessJavaRTIShim"] = field(default_factory=dict)
    federate_names: dict[str, JavaFederateHandle] = field(default_factory=dict)
    objects: dict[JavaObjectInstanceHandle, SharedJavaObjectRecord] = field(default_factory=dict)
    object_names: dict[str, JavaObjectInstanceHandle] = field(default_factory=dict)
    synchronization_points: dict[str, SharedJavaSynchronizationPoint] = field(default_factory=dict)
