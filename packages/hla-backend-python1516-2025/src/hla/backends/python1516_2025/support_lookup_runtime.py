"""Shared support and catalog lookup semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.exceptions import (
    AttributeNotDefined,
    InteractionParameterNotDefined,
    InvalidAttributeHandle,
    InvalidDimensionHandle,
    InvalidFederateHandle,
    InvalidObjectInstanceHandle,
    InvalidOrderType,
    InvalidTransportationName,
    InvalidTransportationTypeHandle,
    NameNotFound,
    ObjectInstanceNotKnown,
)
from hla.rti1516_2025.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)


def get_object_class_handle(backend: Any, object_class_name: str) -> ObjectClassHandle:
    if not isinstance(object_class_name, str):
        raise NameNotFound(repr(object_class_name))
    handles = backend._object_class_handles()
    try:
        return ObjectClassHandle(handles[object_class_name])
    except KeyError as exc:
        raise NameNotFound(object_class_name) from exc


def get_object_class_name(backend: Any, object_class: Any) -> str:
    return backend._object_class_name(object_class)


def get_attribute_handle(backend: Any, object_class: Any, attribute_name: str) -> AttributeHandle:
    object_class_name = backend._object_class_name(object_class)
    if not isinstance(attribute_name, str):
        raise AttributeNotDefined(repr(attribute_name))
    handles = backend._attribute_handles(object_class_name)
    try:
        return AttributeHandle(handles[attribute_name])
    except KeyError as exc:
        raise AttributeNotDefined(attribute_name) from exc


def get_attribute_name(backend: Any, object_class: Any, attribute: Any) -> str:
    object_class_name = backend._object_class_name(object_class)
    attribute_value = backend._normalize_handle(attribute, AttributeHandle, InvalidAttributeHandle)
    names_by_handle = {value: name for name, value in backend._attribute_handles(object_class_name).items()}
    try:
        return names_by_handle[attribute_value]
    except KeyError as exc:
        raise InvalidAttributeHandle(str(attribute)) from exc


def get_interaction_class_handle(backend: Any, interaction_class_name: str) -> InteractionClassHandle:
    if not isinstance(interaction_class_name, str):
        raise NameNotFound(repr(interaction_class_name))
    handles = backend._interaction_class_handles()
    try:
        return InteractionClassHandle(handles[interaction_class_name])
    except KeyError as exc:
        raise NameNotFound(interaction_class_name) from exc


def get_interaction_class_name(backend: Any, interaction_class: Any) -> str:
    return backend._interaction_class_name(interaction_class)


def get_parameter_handle(backend: Any, interaction_class: Any, parameter_name: str) -> ParameterHandle:
    interaction_class_name = backend._interaction_class_name(interaction_class)
    if not isinstance(parameter_name, str):
        raise InteractionParameterNotDefined(repr(parameter_name))
    handles = backend._parameter_handles(interaction_class_name)
    try:
        return ParameterHandle(handles[parameter_name])
    except KeyError as exc:
        raise InteractionParameterNotDefined(parameter_name) from exc


def get_parameter_name(backend: Any, interaction_class: Any, parameter: Any) -> str:
    interaction_class_name = backend._interaction_class_name(interaction_class)
    parameter_value = backend._normalize_handle(parameter, ParameterHandle, InteractionParameterNotDefined)
    names_by_handle = {value: name for name, value in backend._parameter_handles(interaction_class_name).items()}
    try:
        return names_by_handle[parameter_value]
    except KeyError as exc:
        raise InteractionParameterNotDefined(str(parameter)) from exc


def get_transportation_type_handle(backend: Any, transportation_type_name: str) -> TransportationTypeHandle:
    if not isinstance(transportation_type_name, str):
        raise InvalidTransportationName(repr(transportation_type_name))
    handles = backend._transportation_handles()
    try:
        return TransportationTypeHandle(handles[transportation_type_name])
    except KeyError as exc:
        raise InvalidTransportationName(transportation_type_name) from exc


def get_transportation_type_name(backend: Any, transportation_type: Any) -> str:
    transportation_value = backend._normalize_handle(
        transportation_type,
        TransportationTypeHandle,
        InvalidTransportationTypeHandle,
    )
    names_by_handle = {value: name for name, value in backend._transportation_handles().items()}
    try:
        return names_by_handle[transportation_value]
    except KeyError as exc:
        raise InvalidTransportationTypeHandle(str(transportation_type)) from exc


def get_dimension_handle(backend: Any, dimension_name: str) -> DimensionHandle:
    if not isinstance(dimension_name, str):
        raise NameNotFound(repr(dimension_name))
    handles = backend._dimension_handles()
    try:
        return DimensionHandle(handles[dimension_name])
    except KeyError as exc:
        raise NameNotFound(dimension_name) from exc


def get_dimension_name(backend: Any, dimension: Any) -> str:
    dimension_value = backend._normalize_handle(dimension, DimensionHandle, InvalidDimensionHandle)
    names_by_handle = {value: name for name, value in backend._dimension_handles().items()}
    try:
        return names_by_handle[dimension_value]
    except KeyError as exc:
        raise InvalidDimensionHandle(str(dimension)) from exc


def get_dimension_upper_bound(backend: Any, dimension: Any) -> int:
    dimension_name = get_dimension_name(backend, dimension)
    spec = backend._dimension_spec(dimension_name)
    if spec is None or spec.upper_bound in {None, ""}:
        return 0
    try:
        return int(str(spec.upper_bound))
    except ValueError as exc:
        raise InvalidDimensionHandle(f"Dimension {dimension_name} has invalid upper bound {spec.upper_bound!r}") from exc


def get_available_dimensions_for_object_class(backend: Any, object_class: Any) -> set[DimensionHandle]:
    backend._object_class_name(object_class)
    return {DimensionHandle(value) for value in backend._dimension_handles().values()}


def get_available_dimensions_for_interaction_class(backend: Any, interaction_class: Any) -> set[DimensionHandle]:
    backend._interaction_class_name(interaction_class)
    return {DimensionHandle(value) for value in backend._dimension_handles().values()}


def get_federate_handle(backend: Any, federate_name: str) -> FederateHandle:
    federation = backend._federation_record()
    try:
        return federation.member_handles[str(federate_name)]
    except KeyError as exc:
        raise NameNotFound(str(federate_name)) from exc


def get_federate_name(backend: Any, federate: Any) -> str:
    federate_value = backend._normalize_handle(federate, FederateHandle, InvalidFederateHandle)
    federation = backend._federation_record()
    names_by_handle = {handle.value: name for name, handle in federation.member_handles.items()}
    try:
        return names_by_handle[federate_value]
    except KeyError as exc:
        raise InvalidFederateHandle(str(federate)) from exc


def get_known_object_class_handle(backend: Any, object_instance: Any) -> ObjectClassHandle:
    object_instance_value = backend._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        InvalidObjectInstanceHandle,
    )
    try:
        record = backend._federation_record().object_instances[object_instance_value]
    except KeyError as exc:
        raise ObjectInstanceNotKnown(str(object_instance)) from exc
    known_class_name = backend._known_object_classes.get(object_instance_value)
    if known_class_name is not None:
        return ObjectClassHandle(backend._object_class_handles()[known_class_name])
    if backend._current_federate_handle() in set(record.attribute_owners.values()):
        backend._known_object_classes[object_instance_value] = record.object_class_name
        if record.object_instance_name is not None:
            backend._known_object_names[record.object_instance_name] = object_instance_value
        return ObjectClassHandle(backend._object_class_handles()[record.object_class_name])
    raise ObjectInstanceNotKnown(str(object_instance))


def get_object_instance_handle(backend: Any, object_instance_name: str) -> ObjectInstanceHandle:
    try:
        return ObjectInstanceHandle(backend._known_object_names[str(object_instance_name)])
    except KeyError as exc:
        raise ObjectInstanceNotKnown(str(object_instance_name)) from exc


def get_object_instance_name(backend: Any, object_instance: Any) -> str:
    object_instance_value = backend._normalize_handle(
        object_instance,
        ObjectInstanceHandle,
        InvalidObjectInstanceHandle,
    )
    record = backend._object_instance_record_known(object_instance)
    if object_instance_value in backend._known_object_classes:
        if record.object_instance_name is None:
            raise ObjectInstanceNotKnown(str(object_instance))
        return record.object_instance_name
    if backend._current_federate_handle() in set(record.attribute_owners.values()):
        backend._known_object_classes[object_instance_value] = record.object_class_name
        if record.object_instance_name is not None:
            backend._known_object_names[record.object_instance_name] = object_instance_value
            return record.object_instance_name
    raise ObjectInstanceNotKnown(str(object_instance))


def get_order_type(_backend: Any, order_type_name: str) -> OrderType:
    normalized = str(order_type_name).strip().lower()
    if normalized in {"hlareceive", "receive", "ro"}:
        return OrderType.RECEIVE
    if normalized in {"hlatimestamp", "timestamp", "tso"}:
        return OrderType.TIMESTAMP
    raise InvalidOrderType(str(order_type_name))


def get_order_name(_backend: Any, order_type: Any) -> str:
    try:
        coerced = order_type if isinstance(order_type, OrderType) else OrderType(order_type)
    except Exception as exc:
        raise InvalidOrderType(str(order_type)) from exc
    if coerced is OrderType.RECEIVE:
        return "HLAreceive"
    if coerced is OrderType.TIMESTAMP:
        return "HLAtimestamp"
    raise InvalidOrderType(str(order_type))
