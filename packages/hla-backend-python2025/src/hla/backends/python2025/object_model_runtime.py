"""Shared object-model lookup semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.handles import ObjectInstanceHandle


def matching_object_publishers(
    federation: Any,
    object_class_name: str,
    attribute_names: set[str],
) -> set[int]:
    publishers: set[int] = set()
    for federate_key, classes in federation.published_object_attributes.items():
        published = classes.get(object_class_name, set())
        if published & attribute_names:
            publishers.add(federate_key)
    return publishers


def has_object_registration_interest(
    federation: Any,
    publisher_key: int,
    object_class_name: str,
) -> bool:
    published = federation.published_object_attributes.get(publisher_key, {}).get(object_class_name, set())
    if not published:
        return False
    for subscriber_key, classes in federation.subscribed_object_attributes.items():
        if subscriber_key == publisher_key:
            continue
        subscribed = classes.get(object_class_name, set())
        if published & subscribed:
            return True
    return False


def subscribed_discovery_class_name(rti: Any, federate_key: int, object_class_name: str) -> str | None:
    subscriptions = rti._federation_record().subscribed_object_attributes.get(federate_key, {})
    for candidate_name in object_class_lineage(rti, object_class_name):
        if candidate_name in subscriptions:
            return candidate_name
    return None


def object_class_lineage(rti: Any, object_class_name: str) -> tuple[str, ...]:
    catalog = rti._federation_record().fom_catalog
    lineage: list[str] = []
    current = catalog.object_classes.get(object_class_name)
    while current is not None:
        lineage.append(current.full_name)
        parent_name = current.parent_name
        if parent_name is None:
            break
        current = catalog.object_classes.get(parent_name)
    return tuple(lineage)


def attribute_name_by_handle(
    rti: Any,
    object_class_name: str,
    attribute: Any,
    *,
    expected_type: type[Any],
    invalid_handle_exc: type[Exception],
) -> str:
    attribute_value = rti._normalize_handle(attribute, expected_type, invalid_handle_exc)
    names_by_handle = {value: name for name, value in rti._attribute_handles(object_class_name).items()}
    try:
        return names_by_handle[attribute_value]
    except KeyError as exc:
        raise invalid_handle_exc(str(attribute)) from exc


def attribute_names_from_handles(
    rti: Any,
    object_class_name: str,
    attributes: Any,
    *,
    expected_type: type[Any],
    invalid_handle_exc: type[Exception],
    empty_set_exc: type[Exception],
) -> tuple[str, ...]:
    try:
        attribute_values = tuple(attributes)
    except TypeError as exc:
        raise empty_set_exc("Attribute handle set must be iterable") from exc
    if not attribute_values:
        raise empty_set_exc("Attribute handle set cannot be empty")
    names_by_handle = {value: name for name, value in rti._attribute_handles(object_class_name).items()}
    names: list[str] = []
    for attribute in attribute_values:
        attribute_value = rti._normalize_handle(attribute, expected_type, invalid_handle_exc)
        try:
            names.append(names_by_handle[attribute_value])
        except KeyError as exc:
            raise invalid_handle_exc(str(attribute)) from exc
    return tuple(names)


def published_attributes_for_current_federate(rti: Any, object_class_name: str) -> set[str]:
    return rti._federation_record().published_object_attributes.setdefault(rti._current_federate_key(), {}).get(
        object_class_name,
        set(),
    )


def discover_existing_objects_for_current_subscription(rti: Any, object_class_name: str) -> None:
    federation = rti._federation_record()
    for object_value, record in federation.object_instances.items():
        discovery_class_name = rti._subscribed_discovery_class_name(
            rti._current_federate_key(),
            record.object_class_name,
        )
        if discovery_class_name != object_class_name:
            continue
        owner_handles = {owner for owner in record.attribute_owners.values() if owner is not None}
        producing_federate = (
            sorted(owner_handles, key=lambda handle: handle.value)[0]
            if owner_handles
            else record.producing_federate
        )
        if producing_federate is None:
            continue
        subscribed_names = (
            federation.subscribed_object_attributes.get(rti._current_federate_key(), {})
            .get(object_class_name, set())
        )
        reflected_names = rti._reflectable_attribute_names_for_subscriber(
            producing_federate.value,
            rti._current_federate_key(),
            record,
            discovery_class_name,
            set(subscribed_names),
        )
        if not reflected_names:
            continue
        target_rti = federation.member_rtis.get(rti._current_federate_key())
        if target_rti is not None and object_value not in target_rti._known_object_classes:
            rti._deliver_callback_now(
                "discoverObjectInstance",
                ObjectInstanceHandle(object_value),
                rti.getObjectClassHandle(discovery_class_name),
                record.object_instance_name or "",
                producing_federate,
            )
