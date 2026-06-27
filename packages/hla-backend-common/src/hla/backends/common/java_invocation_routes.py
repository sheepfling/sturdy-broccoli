"""Java deterministic route and resolver policy."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .base import BackendConversionError, Invocation
from .conversion import handle_type_from_java_class_name, handle_type_from_java_type_name
from .java_invocation_metadata import java_parameter_names, java_parameter_types, ordered_args_for_overload
from .java_invocation_scoring import is_sequence_not_text, looks_like_time_factory_name, score_value_for_java_type
from .java_invocation_types import ResolvedJavaInvocation


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
            ordered = ordered_args_for_overload(invocation, overload)
            if ordered is None:
                continue
            types = java_parameter_types(overload)
            incompatible = False
            handle_only_incompatibility = len(java_overloads) == 1 and all(value is not None for value in ordered)
            for idx, value in enumerate(ordered):
                if score_value_for_java_type(types[idx], java_parameter_names(overload)[idx], value) is not None:
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
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload, strict_container_shapes=True)

        if len(candidates) == 1:
            ordered, types, overload = candidates[0]
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload, strict_container_shapes=True)

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
            return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload, strict_container_shapes=True)

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
        ordered = ordered_args_for_overload(invocation, overload)
        if ordered is None:
            continue
        names = java_parameter_names(overload)
        types = java_parameter_types(overload)
        param_scores: list[int] = []
        incompatible = False
        handle_only_incompatibility = len(java_overloads) == 1 and all(value is not None for value in ordered)
        for idx, value in enumerate(ordered):
            param_score = score_value_for_java_type(types[idx], names[idx], value)
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
    if looks_like_time_factory_name(value):
        return False
    if is_sequence_not_text(value):
        return False
    return isinstance(value, (str, os.PathLike)) or hasattr(value, "uri")


def _is_url_sequence(value: Any) -> bool:
    return is_sequence_not_text(value)


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
    DeterministicJavaRoute("connect", 2, ("federateAmbassador", "callbackModel"), "document the minimal connect route without local settings", _predicate_true),
    DeterministicJavaRoute("connect", 3, ("federateAmbassador", "callbackModel", "localSettingsDesignator"), "document the connect route that includes local settings designator injection", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("createFederationExecution", 2, ("federationExecutionName", "fomModules"), "route list/tuple-like second argument to URL[] FOM modules overload", lambda args: _is_url_sequence(args[1])),
    DeterministicJavaRoute("createFederationExecution", 2, ("federationExecutionName", "fomModule"), "route scalar URL-like second argument to single-URL FOM overload", lambda args: _is_url_like(args[1])),
    DeterministicJavaRoute("createFederationExecution", 3, ("federationExecutionName", "fomModules", "logicalTimeImplementationName"), "route URL[] plus exact Python str third argument to logical-time-factory overload", lambda args: _is_url_sequence(args[1]) and isinstance(args[2], str)),
    DeterministicJavaRoute("createFederationExecution", 3, ("federationExecutionName", "fomModules", "mimModule"), "route URL[] plus non-string URL-like third argument to MIM-module overload", lambda args: _is_url_sequence(args[1]) and not isinstance(args[2], str) and _is_url_like(args[2])),
    DeterministicJavaRoute("createFederationExecution", 4, ("federationExecutionName", "fomModules", "mimModule", "logicalTimeImplementationName"), "document the full createFederationExecution route with FOM modules, MIM module, and time factory", lambda args: _is_url_sequence(args[1]) and _is_url_like(args[2]) and isinstance(args[3], str)),
    DeterministicJavaRoute("joinFederationExecution", 2, ("federateType", "federationExecutionName"), "document the anonymous-name join route", lambda args: _all_are_strings(args[0], args[1])),
    DeterministicJavaRoute("joinFederationExecution", 3, ("federateType", "federationExecutionName", "additionalFomModules"), "route iterable third argument to additional-FOM-modules overload", lambda args: _is_url_sequence(args[2])),
    DeterministicJavaRoute("joinFederationExecution", 3, ("federateName", "federateType", "federationExecutionName"), "route exact Python str third argument to federate-name overload", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("joinFederationExecution", 4, ("federateName", "federateType", "federationExecutionName", "additionalFomModules"), "document the named join route with extra FOM modules", lambda args: _all_are_strings(args[0], args[1], args[2]) and _is_url_sequence(args[3])),
    DeterministicJavaRoute("subscribeObjectClassAttributes", 2, ("theClass", "attributeList"), "document the base subscribeObjectClassAttributes route", _predicate_true),
    DeterministicJavaRoute("subscribeObjectClassAttributes", 3, ("theClass", "attributeList", "updateRateDesignator"), "document the subscribeObjectClassAttributes route with update rate designator", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("subscribeObjectClassAttributesPassively", 2, ("theClass", "attributeList"), "document the passive subscribe route", _predicate_true),
    DeterministicJavaRoute("subscribeObjectClassAttributesPassively", 3, ("theClass", "attributeList", "updateRateDesignator"), "document the passive subscribe route with update rate designator", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("subscribeObjectClassAttributesWithRegions", 2, ("theClass", "attributesAndRegions"), "document the region-scoped subscribe route", _predicate_true),
    DeterministicJavaRoute("subscribeObjectClassAttributesWithRegions", 3, ("theClass", "attributesAndRegions", "updateRateDesignator"), "document the region-scoped subscribe route with update rate designator", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("subscribeObjectClassAttributesPassivelyWithRegions", 2, ("theClass", "attributesAndRegions"), "document the passive region-scoped subscribe route", _predicate_true),
    DeterministicJavaRoute("subscribeObjectClassAttributesPassivelyWithRegions", 3, ("theClass", "attributesAndRegions", "updateRateDesignator"), "document the passive region-scoped subscribe route with update rate designator", lambda args: isinstance(args[2], str)),
    DeterministicJavaRoute("requestAttributeValueUpdateWithRegions", 3, ("theObject", "attributesAndRegions", "userSuppliedTag"), "document the object-instance regional attribute refresh route", lambda args: _handle_matches_java_type(args[0], "ObjectInstanceHandle")),
    DeterministicJavaRoute("requestAttributeValueUpdateWithRegions", 3, ("theClass", "attributesAndRegions", "userSuppliedTag"), "document the object-class regional attribute refresh route", lambda args: _handle_matches_java_type(args[0], "ObjectClassHandle")),
    DeterministicJavaRoute("requestAttributeValueUpdate", 3, ("theObject", "theAttributes", "userSuppliedTag"), "route first argument in ObjectInstanceHandle family to object-instance overload", lambda args: _handle_matches_java_type(args[0], "ObjectInstanceHandle")),
    DeterministicJavaRoute("requestAttributeValueUpdate", 3, ("theClass", "theAttributes", "userSuppliedTag"), "route first argument in ObjectClassHandle family to object-class overload", lambda args: _handle_matches_java_type(args[0], "ObjectClassHandle")),
)

_DETERMINISTIC_JAVA_ROUTER = DeterministicJavaInvocationRouter(routes=_DETERMINISTIC_JAVA_ROUTES)


def resolve_java_invocation_deterministic(invocation: Invocation) -> ResolvedJavaInvocation:
    return _DETERMINISTIC_JAVA_ROUTER.resolve(invocation)


def resolve_java_invocation_weighted(invocation: Invocation) -> ResolvedJavaInvocation:
    return _resolve_java_invocation_weighted(invocation)


def get_deterministic_java_invocation_router() -> DeterministicJavaInvocationRouter:
    return _DETERMINISTIC_JAVA_ROUTER


def default_java_invocation_resolvers() -> dict[str, Callable[[Invocation], ResolvedJavaInvocation]]:
    return {
        "weighted": resolve_java_invocation_weighted,
        "deterministic": resolve_java_invocation_deterministic,
    }


__all__ = [
    "DeterministicJavaInvocationRouter",
    "DeterministicJavaRoute",
    "default_java_invocation_resolvers",
    "get_deterministic_java_invocation_router",
    "resolve_java_invocation_deterministic",
    "resolve_java_invocation_weighted",
]
