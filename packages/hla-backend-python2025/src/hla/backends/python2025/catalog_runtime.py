"""Catalog and runtime-state lookup helpers for the current Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.exceptions import (
    InteractionClassNotDefined,
    InvalidFederateHandle,
    InvalidInteractionClassHandle,
    InvalidObjectClassHandle,
    InvalidObjectInstanceHandle,
    InvalidTransportationName,
    ObjectClassNotDefined,
    ObjectInstanceNotKnown,
)
from hla.rti1516_2025.handles import (
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)


def attribute_handles(rti: Any, object_class_name: str) -> dict[str, int]:
    catalog = rti._catalog()
    try:
        spec = catalog.object_classes[object_class_name]
    except KeyError as exc:
        raise ObjectClassNotDefined(object_class_name) from exc
    return rti._stable_handles(spec.attributes)


def parameter_handles(rti: Any, interaction_class_name: str) -> dict[str, int]:
    catalog = rti._catalog()
    try:
        spec = catalog.interaction_classes[interaction_class_name]
    except KeyError as exc:
        raise InteractionClassNotDefined(interaction_class_name) from exc
    return rti._stable_handles(spec.parameters)


def object_class_name(rti: Any, object_class: Any) -> str:
    object_class_value = rti._normalize_handle(object_class, ObjectClassHandle, InvalidObjectClassHandle)
    names_by_handle = {value: name for name, value in rti._object_class_handles().items()}
    try:
        return names_by_handle[object_class_value]
    except KeyError as exc:
        raise InvalidObjectClassHandle(str(object_class)) from exc


def interaction_class_name(rti: Any, interaction_class: Any) -> str:
    interaction_class_value = rti._normalize_handle(
        interaction_class,
        InteractionClassHandle,
        InvalidInteractionClassHandle,
    )
    names_by_handle = {value: name for name, value in rti._interaction_class_handles().items()}
    try:
        return names_by_handle[interaction_class_value]
    except KeyError as exc:
        raise InvalidInteractionClassHandle(str(interaction_class)) from exc


def transportation_handle_by_name(rti: Any, name: str) -> TransportationTypeHandle:
    try:
        return TransportationTypeHandle(rti._transportation_handles()[name])
    except KeyError as exc:
        raise InvalidTransportationName(name) from exc


def object_instance_record(rti: Any, object_instance: Any) -> Any:
    object_instance_value = rti._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        InvalidObjectInstanceHandle,
    )
    try:
        return rti._federation_record().object_instances[object_instance_value]
    except KeyError as exc:
        raise InvalidObjectInstanceHandle(str(object_instance)) from exc


def object_instance_record_known(rti: Any, object_instance: Any) -> Any:
    object_instance_value = rti._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        InvalidObjectInstanceHandle,
    )
    try:
        return rti._federation_record().object_instances[object_instance_value]
    except KeyError as exc:
        raise ObjectInstanceNotKnown(str(object_instance)) from exc


def synchronization_required_federates(rti: Any, synchronization_set: Any | None) -> set[int]:
    federation = rti._federation_record()
    if synchronization_set is None:
        return set(federation.member_rtis)
    try:
        handles = tuple(synchronization_set)
    except TypeError as exc:
        raise InvalidFederateHandle("Synchronization set must be iterable") from exc
    required = {
        rti._normalize_handle(handle, FederateHandle, InvalidFederateHandle)
        for handle in handles
    }
    unknown = required - set(federation.member_rtis)
    if unknown:
        raise InvalidFederateHandle(f"Unknown synchronization federate handles: {sorted(unknown)}")
    return required
