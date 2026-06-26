"""Backend-neutral invocation resolution helpers."""
from __future__ import annotations

import os
import re
from collections.abc import Iterable as CollectionsIterable
from collections.abc import Mapping as CollectionsMapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Literal, Mapping

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
JavaInvocationResolverName = Literal["weighted", "deterministic"]


@dataclass(frozen=True)
class DeterministicJavaRoute:
    """Explicit method+arity route for same-shape Java overload families."""

    method_name: str
    arity: int
    params: tuple[str, ...]
    rationale: str
    predicate: Callable[[tuple[Any, ...]], bool]


@dataclass(frozen=True)
class DeterministicJavaInvocationRouter:
    """Fail-closed Java overload router with method-specific explicit routes."""

    routes: tuple[DeterministicJavaRoute, ...]

    def resolve(self, invocation: Invocation) -> ResolvedJavaInvocation:
        java_overloads = [o for o in invocation.overloads if o.get("language") == "java"]
        if not java_overloads:
            if invocation.kwargs:
                raise BackendConversionError(f"Keyword arguments need Java overload metadata for {invocation.method_name}")
            return ResolvedJavaInvocation(args=invocation.args, param_types=())

        candidates: list[tuple[tuple[Any, ...], tuple[str, ...], Mapping[str, Any]]] = []
        single_overload_fallback: tuple[tuple[Any, ...], tuple[str, ...], Mapping[str, Any]] | None = None
        for overload in java_overloads:
            ordered = _ordered_args_for_overload(invocation, overload)
            if ordered is None:
                continue
            types = java_parameter_types(overload)
            incompatible = False
            handle_only_incompatibility = len(java_overloads) == 1 and all(value is not None for value in ordered)
            for idx, value in enumerate(ordered):
                if _score_value_for_java_type(types[idx], java_parameter_names(overload)[idx], value) is not None:
                    continue
                if handle_type_from_java_type_name(types[idx]) is None:
                    handle_only_incompatibility = False
                incompatible = True
                break
            if incompatible and handle_only_incompatibility:
                single_overload_fallback = (ordered, types, overload)
            if incompatible:
                continue
            candidates.append((ordered, types, overload))

        if not candidates and single_overload_fallback is not None:
            ordered, types, overload = single_overload_fallback
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

        if len(candidates) == 1:
            ordered, types, overload = candidates[0]
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

        if len(candidates) > 1:
            routed = self._resolve_explicit_route(invocation, candidates)
            if routed is not None:
                return routed

            overload_names = [java_parameter_names(candidate[2]) for candidate in candidates]
            raise BackendConversionError(
                f"Deterministic Java router has no explicit route for {invocation.method_name} "
                f"with args={invocation.args!r} kwargs={invocation.kwargs!r}; "
                f"matching overload parameters={overload_names}"
            )

        names_by_overload = [java_parameter_names(o) for o in java_overloads]
        raise BackendConversionError(
            f"Could not map arguments for {invocation.method_name}. "
            f"Provided args={len(invocation.args)} kwargs={list(invocation.kwargs)}; Java overload parameters={names_by_overload}"
        )

    def _resolve_explicit_route(
        self,
        invocation: Invocation,
        candidates: list[tuple[tuple[Any, ...], tuple[str, ...], Mapping[str, Any]]],
    ) -> ResolvedJavaInvocation | None:
        candidate_by_params = {
            tuple(java_parameter_names(overload)): (ordered, types, overload)
            for ordered, types, overload in candidates
        }
        matching_routes = []
        for route in self.routes:
            if route.method_name != invocation.method_name:
                continue
            candidate = candidate_by_params.get(route.params)
            if candidate is None:
                continue
            ordered, types, overload = candidate
            if route.arity != len(ordered):
                continue
            if route.predicate(ordered):
                matching_routes.append((route, ordered, types, overload))

        if len(matching_routes) == 1:
            _route, ordered, types, overload = matching_routes[0]
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

        if len(matching_routes) > 1:
            raise BackendConversionError(
                f"Deterministic Java router found multiple explicit routes for {invocation.method_name}. "
                f"Provided args={invocation.args!r} kwargs={invocation.kwargs!r}"
            )
        return None


def _resolve_java_invocation_weighted(invocation: Invocation) -> ResolvedJavaInvocation:
    java_overloads = [o for o in invocation.overloads if o.get("language") == "java"]
    if not java_overloads:
        if invocation.kwargs:
            raise BackendConversionError(f"Keyword arguments need Java overload metadata for {invocation.method_name}")
        return ResolvedJavaInvocation(args=invocation.args, param_types=())

    candidates: list[tuple[int, int, tuple[Any, ...], tuple[str, ...], Mapping[str, Any]]] = []
    single_overload_fallback: tuple[tuple[Any, ...], tuple[str, ...], Mapping[str, Any]] | None = None
    for source_index, overload in enumerate(java_overloads):
        ordered = _ordered_args_for_overload(invocation, overload)
        if ordered is None:
            continue
        names = java_parameter_names(overload)
        types = java_parameter_types(overload)
        param_scores: list[int] = []
        incompatible = False
        handle_only_incompatibility = len(java_overloads) == 1 and all(value is not None for value in ordered)
        for idx, value in enumerate(ordered):
            param_score = _score_value_for_java_type(types[idx], names[idx], value)
            if param_score is None:
                if handle_type_from_java_type_name(types[idx]) is None:
                    handle_only_incompatibility = False
                incompatible = True
                break
            param_scores.append(param_score)
        if incompatible and handle_only_incompatibility:
            single_overload_fallback = (ordered, types, overload)
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

    if single_overload_fallback is not None:
        ordered, types, overload = single_overload_fallback
        return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

    names_by_overload = [java_parameter_names(o) for o in java_overloads]
    raise BackendConversionError(
        f"Could not map arguments for {invocation.method_name}. "
        f"Provided args={len(invocation.args)} kwargs={list(invocation.kwargs)}; Java overload parameters={names_by_overload}"
    )


def _is_url_like(value: Any) -> bool:
    if _looks_like_time_factory_name(value):
        return False
    if _is_sequence_not_text(value):
        return False
    return isinstance(value, (str, os.PathLike)) or hasattr(value, "uri")


def _is_url_sequence(value: Any) -> bool:
    return _is_sequence_not_text(value)


def _handle_matches_java_type(value: Any, java_type: str) -> bool:
    handle_type = handle_type_from_java_type_name(java_type)
    if handle_type is None:
        return False
    value_type = type(value)
    module_name = getattr(value_type, "__module__", None)
    class_name = getattr(value_type, "__name__", None)
    if isinstance(module_name, str) and isinstance(class_name, str):
        inferred = handle_type_from_java_class_name(f"{module_name}.{class_name}")
        if inferred is handle_type:
            return True
        if inferred is not None:
            return False
    return isinstance(value, handle_type)


def _all_are_strings(*values: Any) -> bool:
    return all(isinstance(value, str) for value in values)


def _predicate_true(_args: tuple[Any, ...]) -> bool:
    return True


_DETERMINISTIC_JAVA_ROUTES: tuple[DeterministicJavaRoute, ...] = (
    DeterministicJavaRoute(
        method_name="connect",
        arity=2,
        params=("federateAmbassador", "callbackModel"),
        rationale="document the minimal connect route without local settings",
        predicate=_predicate_true,
    ),
    DeterministicJavaRoute(
        method_name="connect",
        arity=3,
        params=("federateAmbassador", "callbackModel", "localSettingsDesignator"),
        rationale="document the connect route that includes local settings designator injection",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="createFederationExecution",
        arity=2,
        params=("federationExecutionName", "fomModules"),
        rationale="route list/tuple-like second argument to URL[] FOM modules overload",
        predicate=lambda args: _is_url_sequence(args[1]),
    ),
    DeterministicJavaRoute(
        method_name="createFederationExecution",
        arity=2,
        params=("federationExecutionName", "fomModule"),
        rationale="route scalar URL-like second argument to single-URL FOM overload",
        predicate=lambda args: _is_url_like(args[1]),
    ),
    DeterministicJavaRoute(
        method_name="createFederationExecution",
        arity=3,
        params=("federationExecutionName", "fomModules", "logicalTimeImplementationName"),
        rationale="route URL[] plus exact Python str third argument to logical-time-factory overload",
        predicate=lambda args: _is_url_sequence(args[1]) and isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="createFederationExecution",
        arity=3,
        params=("federationExecutionName", "fomModules", "mimModule"),
        rationale="route URL[] plus non-string URL-like third argument to MIM-module overload",
        predicate=lambda args: _is_url_sequence(args[1]) and not isinstance(args[2], str) and _is_url_like(args[2]),
    ),
    DeterministicJavaRoute(
        method_name="createFederationExecution",
        arity=4,
        params=("federationExecutionName", "fomModules", "mimModule", "logicalTimeImplementationName"),
        rationale="document the full createFederationExecution route with FOM modules, MIM module, and time factory",
        predicate=lambda args: _is_url_sequence(args[1]) and _is_url_like(args[2]) and isinstance(args[3], str),
    ),
    DeterministicJavaRoute(
        method_name="joinFederationExecution",
        arity=2,
        params=("federateType", "federationExecutionName"),
        rationale="document the anonymous-name join route",
        predicate=lambda args: _all_are_strings(args[0], args[1]),
    ),
    DeterministicJavaRoute(
        method_name="joinFederationExecution",
        arity=3,
        params=("federateType", "federationExecutionName", "additionalFomModules"),
        rationale="route iterable third argument to additional-FOM-modules overload",
        predicate=lambda args: _is_url_sequence(args[2]),
    ),
    DeterministicJavaRoute(
        method_name="joinFederationExecution",
        arity=3,
        params=("federateName", "federateType", "federationExecutionName"),
        rationale="route exact Python str third argument to federate-name overload",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="joinFederationExecution",
        arity=4,
        params=("federateName", "federateType", "federationExecutionName", "additionalFomModules"),
        rationale="document the named join route with extra FOM modules",
        predicate=lambda args: _all_are_strings(args[0], args[1], args[2]) and _is_url_sequence(args[3]),
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributes",
        arity=2,
        params=("theClass", "attributeList"),
        rationale="document the base subscribeObjectClassAttributes route",
        predicate=_predicate_true,
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributes",
        arity=3,
        params=("theClass", "attributeList", "updateRateDesignator"),
        rationale="document the subscribeObjectClassAttributes route with update rate designator",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesPassively",
        arity=2,
        params=("theClass", "attributeList"),
        rationale="document the passive subscribe route",
        predicate=_predicate_true,
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesPassively",
        arity=3,
        params=("theClass", "attributeList", "updateRateDesignator"),
        rationale="document the passive subscribe route with update rate designator",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesWithRegions",
        arity=2,
        params=("theClass", "attributesAndRegions"),
        rationale="document the region-scoped subscribe route",
        predicate=_predicate_true,
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesWithRegions",
        arity=3,
        params=("theClass", "attributesAndRegions", "updateRateDesignator"),
        rationale="document the region-scoped subscribe route with update rate designator",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesPassivelyWithRegions",
        arity=2,
        params=("theClass", "attributesAndRegions"),
        rationale="document the passive region-scoped subscribe route",
        predicate=_predicate_true,
    ),
    DeterministicJavaRoute(
        method_name="subscribeObjectClassAttributesPassivelyWithRegions",
        arity=3,
        params=("theClass", "attributesAndRegions", "updateRateDesignator"),
        rationale="document the passive region-scoped subscribe route with update rate designator",
        predicate=lambda args: isinstance(args[2], str),
    ),
    DeterministicJavaRoute(
        method_name="requestAttributeValueUpdateWithRegions",
        arity=3,
        params=("theObject", "attributesAndRegions", "userSuppliedTag"),
        rationale="document the object-instance regional attribute refresh route",
        predicate=lambda args: _handle_matches_java_type(args[0], "ObjectInstanceHandle"),
    ),
    DeterministicJavaRoute(
        method_name="requestAttributeValueUpdateWithRegions",
        arity=3,
        params=("theClass", "attributesAndRegions", "userSuppliedTag"),
        rationale="document the object-class regional attribute refresh route",
        predicate=lambda args: _handle_matches_java_type(args[0], "ObjectClassHandle"),
    ),
    DeterministicJavaRoute(
        method_name="requestAttributeValueUpdate",
        arity=3,
        params=("theObject", "theAttributes", "userSuppliedTag"),
        rationale="route first argument in ObjectInstanceHandle family to object-instance overload",
        predicate=lambda args: _handle_matches_java_type(args[0], "ObjectInstanceHandle"),
    ),
    DeterministicJavaRoute(
        method_name="requestAttributeValueUpdate",
        arity=3,
        params=("theClass", "theAttributes", "userSuppliedTag"),
        rationale="route first argument in ObjectClassHandle family to object-class overload",
        predicate=lambda args: _handle_matches_java_type(args[0], "ObjectClassHandle"),
    ),
)

_DETERMINISTIC_JAVA_ROUTER = DeterministicJavaInvocationRouter(routes=_DETERMINISTIC_JAVA_ROUTES)
_JAVA_INVOCATION_RESOLVERS: dict[JavaInvocationResolverName, JavaInvocationResolver] = {
    "weighted": _resolve_java_invocation_weighted,
    "deterministic": lambda invocation: _DETERMINISTIC_JAVA_ROUTER.resolve(invocation),
}


def get_deterministic_java_invocation_router() -> DeterministicJavaInvocationRouter:
    return _DETERMINISTIC_JAVA_ROUTER


def resolve_java_invocation_deterministic(invocation: Invocation) -> ResolvedJavaInvocation:
    return _JAVA_INVOCATION_RESOLVERS["deterministic"](invocation)


def install_deterministic_java_invocation_router() -> JavaInvocationResolver:
    return set_java_invocation_resolver(resolve_java_invocation_deterministic)


def java_invocation_resolver(name: JavaInvocationResolverName) -> JavaInvocationResolver:
    try:
        return _JAVA_INVOCATION_RESOLVERS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(_JAVA_INVOCATION_RESOLVERS))
        raise ValueError(f"Unknown Java invocation resolver {name!r}; supported resolvers: {supported}") from exc


def java_invocation_resolver_name(resolver: JavaInvocationResolver) -> str:
    for name, candidate in _JAVA_INVOCATION_RESOLVERS.items():
        if resolver is candidate:
            return name
    if resolver is resolve_java_invocation_deterministic:
        return "deterministic"
    return getattr(resolver, "__name__", resolver.__class__.__name__)


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
    "DeterministicJavaInvocationRouter",
    "DeterministicJavaRoute",
    "ResolvedJavaInvocation",
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
