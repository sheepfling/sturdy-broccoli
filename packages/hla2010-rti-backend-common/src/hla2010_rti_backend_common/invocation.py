"""Backend-neutral invocation resolution helpers."""
from __future__ import annotations

import os
import re
from collections.abc import Iterable as CollectionsIterable
from collections.abc import Mapping as CollectionsMapping
from dataclasses import dataclass
from typing import Any, Mapping

from .base import BackendConversionError, Invocation, lower_camel_to_snake
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time

from .conversion import clean_java_type_name

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


def _split_java_params(params: str) -> list[str]:
    params = params.strip()
    if not params:
        return []
    return [part.strip() for part in params.split(",") if part.strip()]


def _param_name(param_decl: str) -> str:
    return re.split(r"\s+", param_decl.strip())[-1].replace("...", "")


def _param_type(param_decl: str) -> str:
    pieces = re.split(r"\s+", param_decl.strip())
    if len(pieces) <= 1:
        return ""
    return _clean_java_type(" ".join(pieces[:-1])) or ""


def java_parameter_names(overload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(_param_name(part) for part in _split_java_params(str(overload.get("params", ""))))


def java_parameter_types(overload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(_param_type(part) for part in _split_java_params(str(overload.get("params", ""))))


def _keyword_matches(name: str, parameter_name: str) -> bool:
    return name == parameter_name or name == lower_camel_to_snake(parameter_name)


def _ordered_args_for_overload(invocation: Invocation, overload: Mapping[str, Any]) -> tuple[Any, ...] | None:
    names = java_parameter_names(overload)
    if len(invocation.args) + len(invocation.kwargs) != len(names) or len(invocation.args) > len(names):
        return None

    if not invocation.kwargs:
        return invocation.args if len(invocation.args) == len(names) else None

    values: list[Any] = [None] * len(names)
    filled = [False] * len(names)
    for idx, arg in enumerate(invocation.args):
        values[idx] = arg
        filled[idx] = True

    for kw_name, kw_value in invocation.kwargs.items():
        matches = [idx for idx, param_name in enumerate(names) if _keyword_matches(kw_name, param_name)]
        if not matches:
            return None
        idx = matches[0]
        if filled[idx]:
            return None
        values[idx] = kw_value
        filled[idx] = True

    return tuple(values) if all(filled) else None


def _looks_like_time_factory_name(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("HLA") and value.endswith("Time")


def _is_mapping(value: Any) -> bool:
    return isinstance(value, CollectionsMapping)


def _is_sequence_not_text(value: Any) -> bool:
    return not isinstance(value, (str, bytes, bytearray, memoryview, os.PathLike)) and isinstance(value, CollectionsIterable)


def _score_value_for_java_type(param_type: str, param_name: str, value: Any) -> int:
    t = _clean_java_type(param_type) or ""
    score = 0

    if t == "String":
        score += 4 if isinstance(value, str) else -6
        if param_name == "logicalTimeImplementationName":
            score += 8 if _looks_like_time_factory_name(value) else -3
        return score

    if t == "URL":
        if _looks_like_time_factory_name(value):
            return -8
        if _is_sequence_not_text(value):
            return -5
        return 5 if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri") else 1

    if t == "URL[]":
        if _is_sequence_not_text(value):
            return 6
        if _looks_like_time_factory_name(value):
            return -8
        return 1 if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri") else 0

    if t in _JAVA_HANDLE_SET_TYPES:
        return 6 if _is_sequence_not_text(value) else -4

    if t in _JAVA_HANDLE_VALUE_MAP_TYPES:
        return 6 if _is_mapping(value) else -4

    if t == "AttributeSetRegionSetPairList":
        return 6 if _is_sequence_not_text(value) else -4

    if t == "byte[]":
        return 6 if isinstance(value, (bytes, bytearray, memoryview)) else -2

    if t in {"LogicalTime", "LogicalTimeInterval"}:
        if isinstance(value, (HLAinteger64Time, HLAinteger64Interval, HLAfloat64Time, HLAfloat64Interval)):
            return 8
        if isinstance(value, (int, float)):
            return 2

    return score


@dataclass(frozen=True)
class ResolvedJavaInvocation:
    args: tuple[Any, ...]
    param_types: tuple[str | None, ...]
    overload: Mapping[str, Any] | None = None


def resolve_java_invocation(invocation: Invocation) -> ResolvedJavaInvocation:
    java_overloads = [o for o in invocation.overloads if o.get("language") == "java"]
    if not java_overloads:
        if invocation.kwargs:
            raise BackendConversionError(f"Keyword arguments need Java overload metadata for {invocation.method_name}")
        return ResolvedJavaInvocation(args=invocation.args, param_types=())

    candidates: list[tuple[int, int, tuple[Any, ...], tuple[str, ...], Mapping[str, Any]]] = []
    for source_index, overload in enumerate(java_overloads):
        ordered = _ordered_args_for_overload(invocation, overload)
        if ordered is None:
            continue
        names = java_parameter_names(overload)
        types = java_parameter_types(overload)
        score = sum(_score_value_for_java_type(types[idx], names[idx], value) for idx, value in enumerate(ordered))
        candidates.append((score, -source_index, ordered, types, overload))

    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        _, _, ordered, types, overload = candidates[0]
        return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

    names_by_overload = [java_parameter_names(o) for o in java_overloads]
    raise BackendConversionError(
        f"Could not map arguments for {invocation.method_name}. "
        f"Provided args={len(invocation.args)} kwargs={list(invocation.kwargs)}; Java overload parameters={names_by_overload}"
    )


def resolve_java_arguments(invocation: Invocation) -> tuple[Any, ...]:
    return resolve_java_invocation(invocation).args


__all__ = [
    "ResolvedJavaInvocation",
    "java_parameter_names",
    "java_parameter_types",
    "resolve_java_arguments",
    "resolve_java_invocation",
]
