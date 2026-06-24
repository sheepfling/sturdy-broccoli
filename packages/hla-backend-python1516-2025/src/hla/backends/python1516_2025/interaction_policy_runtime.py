"""Interaction-policy helpers owned by the dedicated Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.exceptions import (
    InteractionClassNotDefined,
    InteractionParameterNotDefined,
    InvalidInteractionClassHandle,
    InvalidOrderType,
)
from hla.rti1516_2025.handles import InteractionClassHandle, ParameterHandle


def parameter_names_from_handles(rti: Any, interaction_class_name: str, parameters: Any) -> tuple[str, ...]:
    try:
        parameter_values = tuple(parameters)
    except TypeError as exc:
        raise InteractionParameterNotDefined("Parameter handle set must be iterable") from exc
    names_by_handle = {value: name for name, value in rti._parameter_handles(interaction_class_name).items()}
    names: list[str] = []
    for parameter in parameter_values:
        parameter_value = rti._normalize_handle(parameter, ParameterHandle, InteractionParameterNotDefined)
        try:
            names.append(names_by_handle[parameter_value])
        except KeyError as exc:
            raise InteractionParameterNotDefined(str(parameter)) from exc
    return tuple(names)


def interaction_class_names_from_handles(rti: Any, interaction_classes: Any) -> tuple[str, ...]:
    try:
        interaction_class_values = tuple(interaction_classes)
    except TypeError as exc:
        raise InteractionClassNotDefined("Interaction class handle set must be iterable") from exc
    if not interaction_class_values:
        raise InteractionClassNotDefined("Interaction class handle set cannot be empty")
    names_by_handle = {value: name for name, value in rti._interaction_class_handles().items()}
    names: list[str] = []
    for interaction_class in interaction_class_values:
        interaction_class_value = rti._normalize_handle(
            interaction_class,
            InteractionClassHandle,
            InvalidInteractionClassHandle,
        )
        try:
            names.append(names_by_handle[interaction_class_value])
        except KeyError as exc:
            raise InvalidInteractionClassHandle(str(interaction_class)) from exc
    return tuple(names)


def interaction_order_for(rti: Any, interaction_class_name: str) -> OrderType:
    return rti._federation_record().interaction_order.get(
        (rti._current_federate_key(), interaction_class_name),
        OrderType.RECEIVE,
    )


def interaction_transportation_for(rti: Any, interaction_class_name: str) -> Any:
    transportation_name = rti._federation_record().interaction_transportation.get(
        (rti._current_federate_key(), interaction_class_name),
        "HLAreliable",
    )
    return rti._transportation_handle_by_name(transportation_name)


def coerce_order_type(order_type: Any) -> OrderType:
    if isinstance(order_type, OrderType):
        return order_type
    member_name = getattr(order_type, "name", None)
    if isinstance(member_name, str) and member_name in OrderType.__members__:
        return OrderType[member_name]
    try:
        return OrderType(order_type)
    except Exception as exc:
        raise InvalidOrderType(repr(order_type)) from exc


__all__ = [
    "coerce_order_type",
    "interaction_class_names_from_handles",
    "interaction_order_for",
    "interaction_transportation_for",
    "parameter_names_from_handles",
]
