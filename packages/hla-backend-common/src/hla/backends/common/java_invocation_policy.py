"""Java-specific overload policy facade.

This module keeps the public import surface stable while delegating to smaller
internal modules for metadata parsing, scoring, and route policy.
"""
from __future__ import annotations

from .java_invocation_metadata import java_parameter_names, java_parameter_types
from .java_invocation_routes import (
    DeterministicJavaInvocationRouter,
    DeterministicJavaRoute,
    default_java_invocation_resolvers,
    get_deterministic_java_invocation_router,
    resolve_java_invocation_deterministic,
    resolve_java_invocation_weighted,
)
from .java_invocation_scoring import (
    _JAVA_HANDLE_SET_TYPES,
    _JAVA_HANDLE_VALUE_MAP_TYPES,
)

__all__ = [
    "DeterministicJavaInvocationRouter",
    "DeterministicJavaRoute",
    "_JAVA_HANDLE_SET_TYPES",
    "_JAVA_HANDLE_VALUE_MAP_TYPES",
    "get_deterministic_java_invocation_router",
    "java_parameter_names",
    "java_parameter_types",
    "default_java_invocation_resolvers",
    "resolve_java_invocation_deterministic",
    "resolve_java_invocation_weighted",
]
