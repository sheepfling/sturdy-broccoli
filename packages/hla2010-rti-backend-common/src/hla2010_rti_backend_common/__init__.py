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

__all__ = [
    "HANDLE_TYPE_BY_JAVA_SIMPLE_NAME",
    "HANDLE_TYPES",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "ValueConverter",
    "clean_java_type_name",
    "handle_type_from_java_class_name",
    "handle_type_from_java_type_name",
]
