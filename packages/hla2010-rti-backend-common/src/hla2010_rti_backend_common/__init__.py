"""Shared backend conversion support package."""
from __future__ import annotations

from .conversion import (
    HANDLE_TYPE_BY_JAVA_SIMPLE_NAME,
    HANDLE_TYPES,
    NativeHandleRegistry,
    NativeObjectRef,
    ValueConverter,
    clean_java_type_name,
    handle_type_from_java_class_name,
    handle_type_from_java_type_name,
)
from .invocation import (
    ResolvedJavaInvocation,
    java_parameter_names,
    java_parameter_types,
    resolve_java_arguments,
    resolve_java_invocation,
)

__all__ = [
    "HANDLE_TYPE_BY_JAVA_SIMPLE_NAME",
    "HANDLE_TYPES",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "ValueConverter",
    "clean_java_type_name",
    "handle_type_from_java_class_name",
    "handle_type_from_java_type_name",
    "ResolvedJavaInvocation",
    "java_parameter_names",
    "java_parameter_types",
    "resolve_java_arguments",
    "resolve_java_invocation",
]
