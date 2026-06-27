"""Backend-neutral invocation framework and swappable resolver hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Literal, Mapping

from .base import BackendConversionError, Invocation

if TYPE_CHECKING:
    from .java_invocation_policy import DeterministicJavaInvocationRouter, DeterministicJavaRoute


@dataclass(frozen=True)
class ResolvedJavaInvocation:
    args: tuple[Any, ...]
    param_types: tuple[str | None, ...]
    overload: Mapping[str, Any] | None = None
    strict_container_shapes: bool = False


JavaInvocationResolver = Callable[[Invocation], ResolvedJavaInvocation]
JavaInvocationResolverName = Literal["weighted", "deterministic"]

_JAVA_INVOCATION_RESOLVERS: dict[JavaInvocationResolverName, JavaInvocationResolver] = {}
_JAVA_DEFAULT_RESOLVER_NAME: JavaInvocationResolverName | None = None
_JAVA_INVOCATION_RESOLVER: JavaInvocationResolver | None = None
_JAVA_POLICY_LOADED = False


def _load_java_policy_defaults() -> None:
    global _JAVA_POLICY_LOADED
    if _JAVA_POLICY_LOADED:
        return
    from .java_invocation_policy import register_default_java_invocation_resolvers

    register_default_java_invocation_resolvers()
    _JAVA_POLICY_LOADED = True


def register_java_invocation_resolver(
    name: JavaInvocationResolverName,
    resolver: JavaInvocationResolver,
    *,
    default: bool = False,
) -> JavaInvocationResolver:
    global _JAVA_DEFAULT_RESOLVER_NAME, _JAVA_INVOCATION_RESOLVER
    previous = _JAVA_INVOCATION_RESOLVERS.get(name, resolver)
    _JAVA_INVOCATION_RESOLVERS[name] = resolver
    if default or _JAVA_DEFAULT_RESOLVER_NAME is None:
        _JAVA_DEFAULT_RESOLVER_NAME = name
        if _JAVA_INVOCATION_RESOLVER is None:
            _JAVA_INVOCATION_RESOLVER = resolver
    return previous


def _require_java_resolver(name: JavaInvocationResolverName) -> JavaInvocationResolver:
    _load_java_policy_defaults()
    try:
        return _JAVA_INVOCATION_RESOLVERS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(_JAVA_INVOCATION_RESOLVERS))
        raise ValueError(f"Unknown Java invocation resolver {name!r}; supported resolvers: {supported}") from exc


def java_invocation_resolver(name: JavaInvocationResolverName) -> JavaInvocationResolver:
    return _require_java_resolver(name)


def java_invocation_resolver_name(resolver: JavaInvocationResolver) -> str:
    _load_java_policy_defaults()
    for name, candidate in _JAVA_INVOCATION_RESOLVERS.items():
        if resolver is candidate:
            return name
    return getattr(resolver, "__name__", resolver.__class__.__name__)


def get_java_invocation_resolver() -> JavaInvocationResolver:
    _load_java_policy_defaults()
    if _JAVA_INVOCATION_RESOLVER is None:
        raise BackendConversionError("Java invocation resolver registry is not initialized")
    return _JAVA_INVOCATION_RESOLVER


def set_java_invocation_resolver(resolver: JavaInvocationResolver) -> JavaInvocationResolver:
    global _JAVA_INVOCATION_RESOLVER
    _load_java_policy_defaults()
    previous = _JAVA_INVOCATION_RESOLVER
    _JAVA_INVOCATION_RESOLVER = resolver
    if previous is None:
        raise BackendConversionError("Java invocation resolver registry is not initialized")
    return previous


def reset_java_invocation_resolver() -> None:
    global _JAVA_INVOCATION_RESOLVER
    _load_java_policy_defaults()
    if _JAVA_DEFAULT_RESOLVER_NAME is None:
        raise BackendConversionError("Java invocation resolver registry has no default")
    _JAVA_INVOCATION_RESOLVER = _require_java_resolver(_JAVA_DEFAULT_RESOLVER_NAME)


def get_deterministic_java_invocation_router() -> DeterministicJavaInvocationRouter:
    from .java_invocation_policy import get_deterministic_java_invocation_router as _get_router

    return _get_router()


def resolve_java_invocation_deterministic(invocation: Invocation) -> ResolvedJavaInvocation:
    return _require_java_resolver("deterministic")(invocation)


def install_deterministic_java_invocation_router() -> JavaInvocationResolver:
    return set_java_invocation_resolver(resolve_java_invocation_deterministic)


def resolve_java_invocation(invocation: Invocation) -> ResolvedJavaInvocation:
    return get_java_invocation_resolver()(invocation)


def resolve_java_arguments(invocation: Invocation) -> tuple[Any, ...]:
    return resolve_java_invocation(invocation).args


def java_parameter_names(overload: Mapping[str, Any]) -> tuple[str, ...]:
    from .java_invocation_policy import java_parameter_names as _java_parameter_names

    return _java_parameter_names(overload)


def java_parameter_types(overload: Mapping[str, Any]) -> tuple[str, ...]:
    from .java_invocation_policy import java_parameter_types as _java_parameter_types

    return _java_parameter_types(overload)


__all__ = [
    "JavaInvocationResolver",
    "ResolvedJavaInvocation",
    "register_java_invocation_resolver",
    "get_java_invocation_resolver",
    "get_deterministic_java_invocation_router",
    "install_deterministic_java_invocation_router",
    "java_invocation_resolver",
    "java_invocation_resolver_name",
    "java_parameter_names",
    "java_parameter_types",
    "reset_java_invocation_resolver",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "resolve_java_invocation_deterministic",
    "set_java_invocation_resolver",
]
