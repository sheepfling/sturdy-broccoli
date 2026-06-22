"""Interaction declaration, routing, and delivery helpers owned by the dedicated Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.datatypes import MessageRetractionReturn
from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.exceptions import InteractionClassNotPublished, InvalidFederateHandle
from hla.rti1516_2025.handles import (
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ParameterHandle,
    RegionHandle,
)

from .directed_interaction_boundary import matching_directed_interaction_targets


def publish_interaction_class(rti: Any, interaction_class: Any) -> None:
    federation = rti._federation_record()
    interaction_class_name = rti._interaction_class_name(interaction_class)
    had_match = rti._has_interaction_interest(federation, rti._current_federate_key(), interaction_class_name)
    federation.published_interactions.setdefault(rti._current_federate_key(), set()).add(interaction_class_name)
    has_match = rti._has_interaction_interest(federation, rti._current_federate_key(), interaction_class_name)
    if has_match and not had_match:
        rti._deliver_callback(
            "turnInteractionsOn",
            InteractionClassHandle(rti._interaction_class_handles()[interaction_class_name]),
        )


def unpublish_interaction_class(rti: Any, interaction_class: Any) -> None:
    federation = rti._federation_record()
    interaction_class_name = rti._interaction_class_name(interaction_class)
    had_match = rti._has_interaction_interest(federation, rti._current_federate_key(), interaction_class_name)
    federation.published_interactions.setdefault(rti._current_federate_key(), set()).discard(interaction_class_name)
    if had_match:
        rti._deliver_callback(
            "turnInteractionsOff",
            InteractionClassHandle(rti._interaction_class_handles()[interaction_class_name]),
        )


def subscribe_interaction_class(rti: Any, interaction_class: Any) -> None:
    federation = rti._federation_record()
    interaction_class_name = rti._interaction_class_name(interaction_class)
    affected_publishers = rti._matching_interaction_publishers(federation, interaction_class_name)
    before_matches = {
        publisher_key: rti._has_interaction_interest(federation, publisher_key, interaction_class_name)
        for publisher_key in affected_publishers
    }
    federation.subscribed_interactions.setdefault(rti._current_federate_key(), set()).add(interaction_class_name)
    for publisher_key in affected_publishers:
        if not before_matches[publisher_key] and rti._has_interaction_interest(
            federation,
            publisher_key,
            interaction_class_name,
        ):
            rti._deliver_to_federate_handle(
                FederateHandle(publisher_key),
                "turnInteractionsOn",
                InteractionClassHandle(rti._interaction_class_handles()[interaction_class_name]),
            )


def unsubscribe_interaction_class(rti: Any, interaction_class: Any) -> None:
    federation = rti._federation_record()
    interaction_class_name = rti._interaction_class_name(interaction_class)
    affected_publishers = rti._matching_interaction_publishers(federation, interaction_class_name)
    before_matches = {
        publisher_key: rti._has_interaction_interest(federation, publisher_key, interaction_class_name)
        for publisher_key in affected_publishers
    }
    subscribed = federation.subscribed_interactions.setdefault(rti._current_federate_key(), set())
    subscribed.discard(interaction_class_name)
    federation.subscribed_interaction_regions.setdefault(rti._current_federate_key(), {}).pop(
        interaction_class_name,
        None,
    )
    federation.directed_interaction_region_gates.setdefault(rti._current_federate_key(), set()).discard(
        interaction_class_name
    )
    for publisher_key in affected_publishers:
        if before_matches[publisher_key] and not rti._has_interaction_interest(
            federation,
            publisher_key,
            interaction_class_name,
        ):
            rti._deliver_to_federate_handle(
                FederateHandle(publisher_key),
                "turnInteractionsOff",
                InteractionClassHandle(rti._interaction_class_handles()[interaction_class_name]),
            )


def subscribe_interaction_class_with_regions(rti: Any, interaction_class: Any, regions: Any) -> None:
    interaction_class_name = rti._interaction_class_name(interaction_class)
    region_values = rti._region_values_from_handles(regions)
    federation = rti._federation_record()
    federation.subscribed_interactions.setdefault(rti._current_federate_key(), set()).add(interaction_class_name)
    federation.directed_interaction_region_gates.setdefault(rti._current_federate_key(), set()).add(
        interaction_class_name
    )
    federation.subscribed_interaction_regions.setdefault(rti._current_federate_key(), {}).setdefault(
        interaction_class_name,
        set(),
    ).update(region_values)


def unsubscribe_interaction_class_with_regions(rti: Any, interaction_class: Any, regions: Any) -> None:
    interaction_class_name = rti._interaction_class_name(interaction_class)
    region_values = rti._region_values_from_handles(regions)
    region_subscriptions = rti._federation_record().subscribed_interaction_regions.setdefault(
        rti._current_federate_key(),
        {},
    ).setdefault(
        interaction_class_name,
        set(),
    )
    region_subscriptions.difference_update(region_values)
    if not region_subscriptions:
        rti._federation_record().subscribed_interaction_regions[rti._current_federate_key()].pop(
            interaction_class_name,
            None,
        )
        rti._federation_record().subscribed_interactions.setdefault(rti._current_federate_key(), set()).discard(
            interaction_class_name
        )


def publish_object_class_directed_interactions(rti: Any, object_class: Any, interaction_classes: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    interaction_class_names = set(rti._interaction_class_names_from_handles(interaction_classes))
    rti._federation_record().published_directed_interactions.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    ).update(interaction_class_names)


def unpublish_object_class_directed_interactions(
    rti: Any,
    object_class: Any,
    interaction_classes: Any | None = None,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    published_by_class = rti._federation_record().published_directed_interactions.setdefault(
        rti._current_federate_key(),
        {},
    )
    if interaction_classes is None:
        published_by_class.pop(object_class_name, None)
        return
    published = published_by_class.setdefault(object_class_name, set())
    published.difference_update(rti._interaction_class_names_from_handles(interaction_classes))
    if not published:
        published_by_class.pop(object_class_name, None)


def subscribe_object_class_directed_interactions(rti: Any, object_class: Any, interaction_classes: Any) -> None:
    object_class_name = rti._object_class_name(object_class)
    interaction_class_names = set(rti._interaction_class_names_from_handles(interaction_classes))
    rti._federation_record().subscribed_directed_interactions.setdefault(rti._current_federate_key(), {}).setdefault(
        object_class_name,
        set(),
    ).update(interaction_class_names)


def unsubscribe_object_class_directed_interactions(
    rti: Any,
    object_class: Any,
    interaction_classes: Any | None = None,
) -> None:
    object_class_name = rti._object_class_name(object_class)
    subscribed_by_class = rti._federation_record().subscribed_directed_interactions.setdefault(
        rti._current_federate_key(),
        {},
    )
    if interaction_classes is None:
        subscribed_by_class.pop(object_class_name, None)
        return
    subscribed = subscribed_by_class.setdefault(object_class_name, set())
    subscribed.difference_update(rti._interaction_class_names_from_handles(interaction_classes))
    if not subscribed:
        subscribed_by_class.pop(object_class_name, None)


def change_interaction_order_type(rti: Any, interaction_class: Any, order_type: Any) -> None:
    interaction_class_name = rti._interaction_class_name(interaction_class)
    if interaction_class_name not in rti._federation_record().published_interactions.setdefault(
        rti._current_federate_key(),
        set(),
    ):
        raise InteractionClassNotPublished(interaction_class_name)
    rti._federation_record().interaction_order[
        (rti._current_federate_key(), interaction_class_name)
    ] = rti._coerce_order_type(order_type)


def send_interaction(
    rti: Any,
    interaction_class: Any,
    parameter_values: Mapping[Any, bytes],
    user_supplied_tag: bytes,
    time: Any | None = None,
) -> Any | None:
    interaction_class_name = rti._interaction_class_name(interaction_class)
    values_by_handle = _parameter_value_map(rti, interaction_class_name, parameter_values)
    if rti._handle_mom_interaction(interaction_class_name, values_by_handle):
        return None
    if interaction_class_name not in rti._federation_record().published_interactions.setdefault(
        rti._current_federate_key(),
        set(),
    ):
        raise InteractionClassNotPublished(interaction_class_name)
    transportation = rti._interaction_transportation_for(interaction_class_name)
    callback_time = rti._coerce_time(time) if time is not None else None
    if callback_time is not None:
        rti._validate_tso_send_time(callback_time)
    retraction_handles: list[MessageRetractionHandle] = []
    federation = rti._federation_record()
    rti._increment_mom_count(
        federation.mom_interactions_sent,
        (rti._current_federate_key(), interaction_class_name, rti.getTransportationTypeName(transportation)),
    )
    for federate_key, subscriptions in federation.subscribed_interactions.items():
        if interaction_class_name not in subscriptions:
            continue
        rti._increment_mom_count(
            federation.mom_interactions_received,
            (federate_key, interaction_class_name, rti.getTransportationTypeName(transportation)),
        )
        interaction_order = rti._interaction_order_for(interaction_class_name)
        explicit_receive_override = (
            federation.interaction_order.get((rti._current_federate_key(), interaction_class_name))
            is OrderType.RECEIVE
        )
        if callback_time is not None:
            if interaction_order is OrderType.RECEIVE and explicit_receive_override:
                rti._deliver_to_federate_handle(
                    FederateHandle(federate_key),
                    "receiveInteraction",
                    interaction_class,
                    values_by_handle,
                    bytes(user_supplied_tag),
                    transportation,
                    rti._current_federate_handle(),
                    set(),
                    None,
                    OrderType.RECEIVE,
                    OrderType.RECEIVE,
                    None,
                )
                continue
            retraction_handles.append(
                rti._queue_tso_callback(
                    FederateHandle(federate_key),
                    callback_time,
                    "receiveInteraction",
                    interaction_class,
                    values_by_handle,
                    bytes(user_supplied_tag),
                    transportation,
                    rti._current_federate_handle(),
                    set(),
                    callback_time,
                    OrderType.TIMESTAMP,
                    OrderType.TIMESTAMP,
                )
            )
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "receiveInteraction",
            interaction_class,
            values_by_handle,
            bytes(user_supplied_tag),
            transportation,
            rti._current_federate_handle(),
            set(),
            callback_time,
            interaction_order,
            interaction_order,
            None,
        )
    if callback_time is not None:
        handle = rti._canonicalize_retraction_handles(federation, retraction_handles)
        return MessageRetractionReturn(bool(retraction_handles), handle)
    return None


def send_interaction_with_regions(
    rti: Any,
    interaction_class: Any,
    parameter_values: Mapping[Any, bytes],
    regions: Any,
    user_supplied_tag: bytes,
    time: Any | None = None,
) -> Any | None:
    source_regions = rti._region_values_from_handles(regions)
    interaction_class_name = rti._interaction_class_name(interaction_class)
    if interaction_class_name not in rti._federation_record().published_interactions.setdefault(
        rti._current_federate_key(),
        set(),
    ):
        raise InteractionClassNotPublished(interaction_class_name)
    values_by_handle = _parameter_value_map(rti, interaction_class_name, parameter_values)
    transportation = rti._interaction_transportation_for(interaction_class_name)
    callback_time = rti._coerce_time(time) if time is not None else None
    if callback_time is not None:
        rti._validate_tso_send_time(callback_time)
    federation = rti._federation_record()
    rti._increment_mom_count(
        federation.mom_interactions_sent,
        (rti._current_federate_key(), interaction_class_name, rti.getTransportationTypeName(transportation)),
    )
    for federate_key, subscriptions in federation.subscribed_interactions.items():
        if federate_key == rti._current_federate_key() or interaction_class_name not in subscriptions:
            continue
        target_regions = rti._federation_record().subscribed_interaction_regions.get(federate_key, {}).get(
            interaction_class_name,
            set(),
        )
        if target_regions and not rti._region_sets_overlap(
            rti._current_federate_key(),
            source_regions,
            federate_key,
            target_regions,
        ):
            continue
        rti._increment_mom_count(
            federation.mom_interactions_received,
            (federate_key, interaction_class_name, rti.getTransportationTypeName(transportation)),
        )
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "receiveInteraction",
            interaction_class,
            values_by_handle,
            bytes(user_supplied_tag),
            transportation,
            rti._current_federate_handle(),
            {RegionHandle(region_value) for region_value in source_regions},
            callback_time,
            rti._interaction_order_for(interaction_class_name),
            rti._interaction_order_for(interaction_class_name),
            None,
        )
    return None


def send_directed_interaction(
    rti: Any,
    interaction_class: Any,
    object_instance: Any,
    parameter_values: Mapping[Any, bytes],
    user_supplied_tag: bytes,
    time: Any | None = None,
) -> Any | None:
    record = rti._object_instance_record(object_instance)
    object_class_name = record.object_class_name
    interaction_class_name = rti._interaction_class_name(interaction_class)
    published_for_object_class = (
        rti._federation_record()
        .published_directed_interactions.setdefault(rti._current_federate_key(), {})
        .get(object_class_name, set())
    )
    if interaction_class_name not in published_for_object_class:
        raise InteractionClassNotPublished(interaction_class_name)

    values_by_handle = _parameter_value_map(rti, interaction_class_name, parameter_values)
    transportation = rti._transportation_handle_by_name("HLAreliable")
    callback_time = rti._coerce_time(time) if time is not None else None
    federation = rti._federation_record()
    source_regions = rti._object_instance_region_values(record)
    retraction_handles: list[MessageRetractionHandle] = []
    rti._increment_mom_count(
        federation.mom_interactions_sent,
        (rti._current_federate_key(), interaction_class_name, rti.getTransportationTypeName(transportation)),
    )
    target_federate_keys = matching_directed_interaction_targets(
        federation,
        source_federate_key=rti._current_federate_key(),
        object_class_name=object_class_name,
        interaction_class_name=interaction_class_name,
        source_regions=source_regions,
        region_sets_overlap=rti._region_sets_overlap,
    )
    for federate_key in target_federate_keys:
        rti._increment_mom_count(
            federation.mom_interactions_received,
            (federate_key, interaction_class_name, rti.getTransportationTypeName(transportation)),
        )
        if callback_time is not None:
            retraction_handles.append(
                rti._queue_tso_callback(
                    FederateHandle(federate_key),
                    callback_time,
                    "receiveDirectedInteraction",
                    interaction_class,
                    object_instance,
                    values_by_handle,
                    bytes(user_supplied_tag),
                    transportation,
                    rti._current_federate_handle(),
                    callback_time,
                    OrderType.TIMESTAMP,
                    OrderType.TIMESTAMP,
                )
            )
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "receiveDirectedInteraction",
            interaction_class,
            object_instance,
            values_by_handle,
            bytes(user_supplied_tag),
            transportation,
            rti._current_federate_handle(),
            callback_time,
            rti._interaction_order_for(interaction_class_name),
            rti._interaction_order_for(interaction_class_name),
            None,
        )
    if callback_time is not None:
        handle = rti._canonicalize_retraction_handles(federation, retraction_handles)
        return MessageRetractionReturn(bool(retraction_handles), handle)
    return None


def request_interaction_transportation_type_change(
    rti: Any,
    interaction_class: Any,
    transportation_type: Any,
) -> None:
    interaction_class_name = rti._interaction_class_name(interaction_class)
    if interaction_class_name not in rti._federation_record().published_interactions.setdefault(
        rti._current_federate_key(),
        set(),
    ):
        raise InteractionClassNotPublished(interaction_class_name)
    transportation_name = rti.getTransportationTypeName(transportation_type)
    transportation = rti._transportation_handle_by_name(transportation_name)
    rti._federation_record().interaction_transportation[
        (rti._current_federate_key(), interaction_class_name)
    ] = transportation_name
    rti._deliver_callback("confirmInteractionTransportationTypeChange", interaction_class, transportation)


def query_interaction_transportation_type(rti: Any, federate: Any, interaction_class: Any) -> None:
    federate_value = rti._normalize_handle(federate, FederateHandle, InvalidFederateHandle)
    if federate_value not in {handle.value for handle in rti._federation_record().member_handles.values()}:
        raise InvalidFederateHandle(str(federate))
    interaction_class_name = rti._interaction_class_name(interaction_class)
    transportation_name = rti._federation_record().interaction_transportation.get(
        (federate_value, interaction_class_name),
        "HLAreliable",
    )
    rti._deliver_callback(
        "reportInteractionTransportationType",
        FederateHandle(federate_value),
        interaction_class,
        rti._transportation_handle_by_name(transportation_name),
    )


def _parameter_value_map(
    rti: Any,
    interaction_class_name: str,
    parameter_values: Mapping[Any, bytes],
) -> dict[ParameterHandle, bytes]:
    parameters_by_name = rti._parameter_handles(interaction_class_name)
    values_by_handle: dict[ParameterHandle, bytes] = {}
    for parameter, value in dict(parameter_values).items():
        parameter_name = rti._parameter_names_from_handles(interaction_class_name, {parameter})[0]
        values_by_handle[ParameterHandle(parameters_by_name[parameter_name])] = bytes(value)
    return values_by_handle


__all__ = [
    "change_interaction_order_type",
    "publish_interaction_class",
    "publish_object_class_directed_interactions",
    "query_interaction_transportation_type",
    "request_interaction_transportation_type_change",
    "send_directed_interaction",
    "send_interaction",
    "send_interaction_with_regions",
    "subscribe_interaction_class",
    "subscribe_interaction_class_with_regions",
    "subscribe_object_class_directed_interactions",
    "unpublish_interaction_class",
    "unpublish_object_class_directed_interactions",
    "unsubscribe_interaction_class",
    "unsubscribe_interaction_class_with_regions",
    "unsubscribe_object_class_directed_interactions",
]
