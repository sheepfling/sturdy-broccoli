"""Java overload type-shape scoring helpers."""
from __future__ import annotations

import os
from collections.abc import Iterable as CollectionsIterable
from collections.abc import Mapping as CollectionsMapping
from typing import Any

from hla.rti1516e.handles import Handle
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time

from .conversion import clean_java_type_name, handle_type_from_java_class_name, handle_type_from_java_type_name

_JAVA_HANDLE_SET_TYPES = {
    "AttributeHandleSet",
    "DimensionHandleSet",
    "FederateHandleSet",
    "InteractionClassHandleSet",
    "RegionHandleSet",
}

_JAVA_HANDLE_VALUE_MAP_TYPES = {
    "AttributeHandleValueMap",
    "ParameterHandleValueMap",
}


def _clean_java_type(type_name: str | None) -> str | None:
    return clean_java_type_name(type_name)


def looks_like_time_factory_name(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("HLA") and value.endswith("Time")


def is_mapping(value: Any) -> bool:
    return isinstance(value, CollectionsMapping)


def is_sequence_not_text(value: Any) -> bool:
    return not isinstance(value, (str, bytes, bytearray, memoryview, os.PathLike)) and isinstance(value, CollectionsIterable)


def looks_like_python_data_element(value: Any) -> bool:
    type_name = type(value).__name__
    return type_name.startswith("HLA") and (
        callable(getattr(value, "getValue", None)) or hasattr(value, "value") or callable(getattr(value, "toByteArray", None))
    )


def score_value_for_java_type(param_type: str, param_name: str, value: Any) -> int | None:
    t = _clean_java_type(param_type) or ""
    score = 0

    handle_type = handle_type_from_java_type_name(t)
    if handle_type is not None:
        value_type_name = None
        value_type = type(value)
        module_name = getattr(value_type, "__module__", None)
        class_name = getattr(value_type, "__name__", None)
        if isinstance(module_name, str) and isinstance(class_name, str):
            value_type_name = f"{module_name}.{class_name}"
        inferred_handle_type = handle_type_from_java_class_name(value_type_name)
        if inferred_handle_type is handle_type:
            return 10
        if inferred_handle_type is not None:
            return None
        if isinstance(value, handle_type):
            return 10
        if isinstance(value, Handle):
            return None
        return None

    if t == "String":
        if not isinstance(value, str):
            return None
        score += 4
        if param_name == "logicalTimeImplementationName":
            score += 8 if looks_like_time_factory_name(value) else -3
        return score

    if t == "URL":
        if looks_like_time_factory_name(value):
            return None
        if is_sequence_not_text(value):
            return None
        if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri"):
            return 5
        return None

    if t == "URL[]":
        if is_sequence_not_text(value):
            return 6
        if looks_like_time_factory_name(value):
            return None
        if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri"):
            return 1
        return None

    if t in _JAVA_HANDLE_SET_TYPES:
        return 6 if is_sequence_not_text(value) else None

    if t in _JAVA_HANDLE_VALUE_MAP_TYPES:
        return 6 if is_mapping(value) else None

    if t == "AttributeSetRegionSetPairList":
        return 6 if is_sequence_not_text(value) else None

    if t == "byte[]":
        if isinstance(value, (bytes, bytearray, memoryview)):
            return 6
        if looks_like_python_data_element(value):
            return 3
        return None

    if t in {"LogicalTime", "LogicalTimeInterval"}:
        if isinstance(value, (HLAinteger64Time, HLAinteger64Interval, HLAfloat64Time, HLAfloat64Interval)):
            return 8
        if isinstance(value, (int, float)):
            return 2
        return None

    return score


__all__ = [
    "_JAVA_HANDLE_SET_TYPES",
    "_JAVA_HANDLE_VALUE_MAP_TYPES",
    "is_mapping",
    "is_sequence_not_text",
    "looks_like_python_data_element",
    "looks_like_time_factory_name",
    "score_value_for_java_type",
]
