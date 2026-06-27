"""Shared Java invocation types used by registry and route modules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Mapping

from .base import Invocation


@dataclass(frozen=True)
class ResolvedJavaInvocation:
    args: tuple[Any, ...]
    param_types: tuple[str | None, ...]
    overload: Mapping[str, Any] | None = None
    strict_container_shapes: bool = False


JavaInvocationResolver = Callable[[Invocation], ResolvedJavaInvocation]
JavaInvocationResolverName = Literal["weighted", "deterministic"]


__all__ = [
    "JavaInvocationResolver",
    "JavaInvocationResolverName",
    "ResolvedJavaInvocation",
]
