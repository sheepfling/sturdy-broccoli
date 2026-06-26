"""Backend-neutral invocation resolution helpers."""
from __future__ import annotations

import os
import re
from collections.abc import Iterable as CollectionsIterable
from collections.abc import Mapping as CollectionsMapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Mapping

from .base import BackendConversionError, Invocation, lower_camel_to_snake
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


@lru_cache(maxsize=None)
def _parsed_java_params(params: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    parts = tuple(_split_java_params(params))
    names = tuple(_param_name(part) for part in parts)
    types = tuple(_param_type(part) for part in parts)
    return names, types


def java_parameter_names(overload: Mapping[str, Any]) -> tuple[str, ...]:
    names, _types = _parsed_java_params(str(overload.get("params", "")))
    return names


def java_parameter_types(overload: Mapping[str, Any]) -> tuple[str, ...]:
    _names, types = _parsed_java_params(str(overload.get("params", "")))
    return types


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


def _looks_like_python_data_element(value: Any) -> bool:
    type_name = type(value).__name__
    return type_name.startswith("HLA") and (
        callable(getattr(value, "getValue", None)) or hasattr(value, "value") or callable(getattr(value, "toByteArray", None))
    )


def _score_value_for_java_type(param_type: str, param_name: str, value: Any) -> int | None:
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
            score += 8 if _looks_like_time_factory_name(value) else -3
        return score

    if t == "URL":
        if _looks_like_time_factory_name(value):
            return None
        if _is_sequence_not_text(value):
            return None
        if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri"):
            return 5
        return None

    if t == "URL[]":
        if _is_sequence_not_text(value):
            return 6
        if _looks_like_time_factory_name(value):
            return None
        if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri"):
            return 1
        return None

    if t in _JAVA_HANDLE_SET_TYPES:
        return 6 if _is_sequence_not_text(value) else None

    if t in _JAVA_HANDLE_VALUE_MAP_TYPES:
        return 6 if _is_mapping(value) else None

    if t == "AttributeSetRegionSetPairList":
        return 6 if _is_sequence_not_text(value) else None

    if t == "byte[]":
        if isinstance(value, (bytes, bytearray, memoryview)):
            return 6
        if _looks_like_python_data_element(value):
            return 3
        return None

    if t in {"LogicalTime", "LogicalTimeInterval"}:
        if isinstance(value, (HLAinteger64Time, HLAinteger64Interval, HLAfloat64Time, HLAfloat64Interval)):
            return 8
        if isinstance(value, (int, float)):
            return 2
        return None

    return score


@dataclass(frozen=True)
class ResolvedJavaInvocation:
    args: tuple[Any, ...]
    param_types: tuple[str | None, ...]
    overload: Mapping[str, Any] | None = None


JavaInvocationResolver = Callable[[Invocation], ResolvedJavaInvocation]


def _resolve_java_invocation_weighted(invocation: Invocation) -> ResolvedJavaInvocation:
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
        param_scores: list[int] = []
        incompatible = False
        for idx, value in enumerate(ordered):
            param_score = _score_value_for_java_type(types[idx], names[idx], value)
            if param_score is None:
                incompatible = True
                break
            param_scores.append(param_score)
        if incompatible:
            continue
        score = sum(param_scores)
        candidates.append((score, -source_index, ordered, types, overload))

    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if len(candidates) > 1:
            top_score = candidates[0][0]
            ambiguous = [candidate for candidate in candidates if candidate[0] == top_score]
            if len(ambiguous) > 1:
                overload_names = [java_parameter_names(candidate[4]) for candidate in ambiguous]
                raise BackendConversionError(
                    f"Ambiguous Java overload resolution for {invocation.method_name}. "
                    f"Provided args={invocation.args!r} kwargs={invocation.kwargs!r}; "
                    f"matching overload parameters={overload_names}"
                )
        _, _, ordered, types, overload = candidates[0]
        return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

    names_by_overload = [java_parameter_names(o) for o in java_overloads]
    raise BackendConversionError(
        f"Could not map arguments for {invocation.method_name}. "
        f"Provided args={len(invocation.args)} kwargs={list(invocation.kwargs)}; Java overload parameters={names_by_overload}"
    )


_JAVA_INVOCATION_RESOLVER: JavaInvocationResolver = _resolve_java_invocation_weighted


def get_java_invocation_resolver() -> JavaInvocationResolver:
    return _JAVA_INVOCATION_RESOLVER


def set_java_invocation_resolver(resolver: JavaInvocationResolver) -> JavaInvocationResolver:
    global _JAVA_INVOCATION_RESOLVER
    previous = _JAVA_INVOCATION_RESOLVER
    _JAVA_INVOCATION_RESOLVER = resolver
    return previous


def reset_java_invocation_resolver() -> None:
    global _JAVA_INVOCATION_RESOLVER
    _JAVA_INVOCATION_RESOLVER = _resolve_java_invocation_weighted


def resolve_java_invocation(invocation: Invocation) -> ResolvedJavaInvocation:
    return _JAVA_INVOCATION_RESOLVER(invocation)


def resolve_java_arguments(invocation: Invocation) -> tuple[Any, ...]:
    return resolve_java_invocation(invocation).args


__all__ = [
    "JavaInvocationResolver",
    "ResolvedJavaInvocation",
    "get_java_invocation_resolver",
    "java_parameter_names",
    "java_parameter_types",
    "reset_java_invocation_resolver",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "set_java_invocation_resolver",
]
