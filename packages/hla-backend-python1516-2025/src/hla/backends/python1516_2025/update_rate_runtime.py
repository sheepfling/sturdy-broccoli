"""Update-rate helpers for the current Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any, Mapping


def get_update_rate_value(
    rti: Any,
    update_rate_designator: str,
    *,
    invalid_update_rate_designator_exc: type[Exception],
) -> float:
    designator = str(update_rate_designator)
    normalized = "HLAdefault" if designator in {"default", "HLAdefaultUpdateRate"} else designator
    update_rates = getattr(rti._catalog(), "update_rates", {})
    if normalized in update_rates:
        return float(update_rates[normalized])
    if normalized == "HLAdefault":
        return 0.0
    raise invalid_update_rate_designator_exc(str(update_rate_designator))


def resolve_update_rate_designator(
    rti: Any,
    *unused: Any,
    invalid_update_rate_designator_exc: type[Exception],
) -> tuple[float | None, str | None]:
    designator = next((str(arg) for arg in reversed(unused) if isinstance(arg, str)), None)
    if designator in (None, "", "default", "HLAdefault", "HLAdefaultUpdateRate"):
        return (0.0, "HLAdefault") if designator is not None else (None, None)
    update_rates = getattr(rti._catalog(), "update_rates", {})
    if designator not in update_rates:
        raise invalid_update_rate_designator_exc(designator)
    return float(update_rates[designator]), designator


def default_update_rate_for_attribute(
    rti: Any,
    object_class_name: str,
    attribute_name: str,
    *,
    invalid_update_rate_designator_exc: type[Exception],
) -> float | None:
    spec = rti._catalog().object_classes.get(object_class_name)
    if spec is None:
        return None
    designator = dict(getattr(spec, "attribute_update_rates", {})).get(attribute_name)
    if not designator:
        return None
    normalized = "HLAdefault" if designator == "default" else str(designator)
    update_rates = getattr(rti._catalog(), "update_rates", {})
    if normalized in update_rates:
        return float(update_rates[normalized])
    if normalized == "HLAdefault":
        return 0.0
    raise invalid_update_rate_designator_exc(str(designator))


def default_update_rate_designator_for_attribute(
    rti: Any,
    object_class_name: str,
    attribute_name: str,
    *,
    invalid_update_rate_designator_exc: type[Exception],
) -> str | None:
    spec = rti._catalog().object_classes.get(object_class_name)
    if spec is None:
        return None
    designator = dict(getattr(spec, "attribute_update_rates", {})).get(attribute_name)
    if not designator:
        return None
    normalized = "HLAdefault" if designator == "default" else str(designator)
    update_rates = getattr(rti._catalog(), "update_rates", {})
    if normalized == "HLAdefault" or normalized in update_rates:
        return normalized
    raise invalid_update_rate_designator_exc(str(designator))


def subscribed_update_rate_for_attribute(
    rti: Any,
    federate_key: int,
    actual_class_name: str,
    attribute_name: str,
) -> float:
    federation = rti._federation_record()
    target_rti = federation.member_rtis.get(federate_key)
    if target_rti is None:
        return 0.0
    matches: list[tuple[int, float]] = []
    lineage = set(rti._object_class_lineage(actual_class_name))
    for subscribed_class_name, rate_map in target_rti._subscribed_object_update_rates.items():
        if subscribed_class_name not in lineage:
            continue
        if attribute_name not in rate_map:
            continue
        matches.append((len(subscribed_class_name), float(rate_map[attribute_name])))
    if not matches:
        return 0.0
    return max(matches, key=lambda item: item[0])[1]


def time_scalar(value: Any) -> float | None:
    if value is None:
        return None
    scalar = getattr(value, "value", value)
    try:
        return float(scalar)
    except Exception:
        return None


def apply_update_rate_reduction_for_subscriber(
    rti: Any,
    federate_key: int,
    object_instance: Any,
    reflected_class_name: str,
    actual_class_name: str,
    reflected: Mapping[Any, bytes],
    delivery_time: Any | None,
) -> dict[Any, bytes]:
    federation = rti._federation_record()
    target_rti = federation.member_rtis.get(federate_key)
    if target_rti is None:
        return dict(reflected)
    scalar_time = time_scalar(delivery_time)
    if scalar_time is None and (target_rti._time_regulation_enabled or target_rti._time_constrained_enabled):
        scalar_time = time_scalar(target_rti._logical_time)
    if scalar_time is None:
        return dict(reflected)
    filtered: dict[Any, bytes] = {}
    for handle, value in reflected.items():
        attribute_name = rti._attribute_name_by_handle(reflected_class_name, handle)
        rate = subscribed_update_rate_for_attribute(rti, federate_key, actual_class_name, attribute_name)
        key = (object_instance.value, attribute_name)
        if rate <= 0.0:
            filtered[handle] = value
            target_rti._last_reflect_logical_times[key] = scalar_time
            continue
        min_interval = 1.0 / rate
        last_time = target_rti._last_reflect_logical_times.get(key)
        if last_time is None or (scalar_time - last_time) >= min_interval:
            filtered[handle] = value
            target_rti._last_reflect_logical_times[key] = scalar_time
    return filtered
