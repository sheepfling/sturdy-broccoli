"""Java overload metadata parsing helpers."""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Mapping

from .base import Invocation, lower_camel_to_snake
from .conversion import clean_java_type_name


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


def ordered_args_for_overload(invocation: Invocation, overload: Mapping[str, Any]) -> tuple[Any, ...] | None:
    names = java_parameter_names(overload)
    positional_args = invocation.args
    if (
        not invocation.kwargs
        and len(positional_args) > len(names)
        and all(value is None for value in positional_args[len(names):])
    ):
        positional_args = positional_args[: len(names)]

    if len(positional_args) + len(invocation.kwargs) != len(names) or len(positional_args) > len(names):
        return None

    if not invocation.kwargs:
        return positional_args if len(positional_args) == len(names) else None

    values: list[Any] = [None] * len(names)
    filled = [False] * len(names)
    for idx, arg in enumerate(positional_args):
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


__all__ = [
    "java_parameter_names",
    "java_parameter_types",
    "ordered_args_for_overload",
]
