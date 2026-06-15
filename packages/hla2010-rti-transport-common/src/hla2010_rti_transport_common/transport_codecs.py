"""Backend-neutral transport wire codecs."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from hla2010.enums import OrderType
from hla2010.handles import AttributeHandle, AttributeHandleSet, FederateHandle, RegionHandle, RegionHandleSet
from hla2010.types import AttributeRegionAssociation, RangeBounds


def encode_bytes(value: bytes | bytearray | memoryview) -> str:
    return bytes(value).hex()


def decode_bytes(value: str) -> bytes:
    return bytes.fromhex(value) if value else b""


def handle_set_spec(values: Iterable[AttributeHandle]) -> str:
    return ",".join(str(int(value.value)) for value in values)


def federate_handle_set_spec(values: Iterable[FederateHandle]) -> str:
    return ",".join(str(int(value.value)) for value in values)


def handle_value_map_spec(values: Mapping[Any, bytes | bytearray | memoryview]) -> str:
    parts: list[str] = []
    for handle, payload in values.items():
        parts.append(f"{int(handle.value)}:{encode_bytes(payload)}")
    return ",".join(parts)


def decode_handle_value_map(spec: str, handle_type: type[Any], map_type: type[Any]) -> Any:
    result = map_type()
    if not spec:
        return result
    for entry in spec.split(","):
        handle_id, value_hex = entry.split(":", 1)
        result[handle_type(int(handle_id))] = decode_bytes(value_hex)
    return result


def decode_order(value: str) -> OrderType:
    return OrderType(int(value))


def decode_handle_set(spec: str, handle_type: type[Any], set_type: type[Any]) -> Any:
    result = set_type()
    if not spec:
        return result
    for entry in spec.split(","):
        if entry:
            result.add(handle_type(int(entry)))
    return result


def range_bounds_spec(bounds: RangeBounds) -> str:
    return f"{int(bounds.lower_bound)}:{int(bounds.upper_bound)}"


def decode_range_bounds(spec: str) -> RangeBounds:
    lower_raw, upper_raw = spec.split(":", 1)
    return RangeBounds(int(lower_raw), int(upper_raw))


def attribute_region_associations_spec(values: Iterable[AttributeRegionAssociation]) -> str:
    parts: list[str] = []
    for association in values:
        parts.append(f"{handle_set_spec(association.attributes)}|{handle_set_spec(association.regions)}")
    return ";".join(parts)


def decode_attribute_region_associations(spec: str) -> list[AttributeRegionAssociation]:
    if not spec:
        return []
    result: list[AttributeRegionAssociation] = []
    for entry in spec.split(";"):
        attributes_raw, regions_raw = entry.split("|", 1)
        result.append(
            AttributeRegionAssociation(
                decode_handle_set(attributes_raw, AttributeHandle, AttributeHandleSet),
                decode_handle_set(regions_raw, RegionHandle, RegionHandleSet),
            )
        )
    return result


__all__ = [
    "attribute_region_associations_spec",
    "decode_bytes",
    "decode_attribute_region_associations",
    "decode_handle_set",
    "decode_handle_value_map",
    "decode_order",
    "decode_range_bounds",
    "encode_bytes",
    "federate_handle_set_spec",
    "handle_set_spec",
    "handle_value_map_spec",
    "range_bounds_spec",
]
