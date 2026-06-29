"""Backend value-conversion helpers.

These helpers are intentionally conservative.  Real RTI implementations often
use implementation-specific handle objects, set factories, logical-time classes,
and exception classes.  The converter keeps those details out of application
code while still allowing a backend to override every conversion hook.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, MutableMapping, TypeVar, cast

from hla.rti1516e.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    Handle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    TransportationTypeHandle,
)

from .base import BackendConversionError

HANDLE_TYPES: tuple[type[Handle], ...] = (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    TransportationTypeHandle,
)

HANDLE_TYPE_BY_JAVA_SIMPLE_NAME: dict[str, type[Handle]] = {cls.__name__: cls for cls in HANDLE_TYPES}
_HANDLE_CLASS_NAME_BY_TYPE: dict[type[Handle], str] = {cls: cls.__name__ for cls in HANDLE_TYPES}
_HANDLE_TYPE_NAMES_BY_LENGTH: tuple[tuple[str, type[Handle]], ...] = tuple(
    sorted(HANDLE_TYPE_BY_JAVA_SIMPLE_NAME.items(), key=lambda item: len(item[0]), reverse=True)
)


def clean_java_type_name(type_name: str | None) -> str | None:
    """Normalize a Java type name enough for adapter dispatch.

    The generated metadata can contain package names, ``final`` modifiers, Java
    array suffixes, or generic arguments. Vendor implementations can also return
    concrete classes whose names merely contain the standard handle interface
    name. This helper deliberately keeps only the parts needed to choose Python
    wrapper types.
    """

    if not type_name:
        return None
    text = str(type_name).strip()
    text = text.replace("final ", "")
    text = text.replace("java.net.", "")
    text = text.replace("hla.rti1516e.", "")
    text = text.replace("hla.rti1516e.encoding.", "")
    if "<" in text:
        text = text.split("<", 1)[0]
    text = text.replace("...", "[]")
    return text.strip()


def handle_type_from_java_type_name(type_name: str | None) -> type[Handle] | None:
    """Return the Python handle type implied by a Java type/class name.

    Exact standard names are preferred.  Vendor-specific implementation names
    such as ``com.vendor.ObjectInstanceHandleImpl`` are also recognized, while
    collection/map/factory names are intentionally ignored because they need
    higher-level conversion.
    """

    clean = clean_java_type_name(type_name)
    if not clean:
        return None
    simple = clean.rsplit(".", 1)[-1].replace("[]", "")
    if simple.endswith(("Set", "Map", "Factory", "ValueMap")):
        return None
    if simple in HANDLE_TYPE_BY_JAVA_SIMPLE_NAME:
        return HANDLE_TYPE_BY_JAVA_SIMPLE_NAME[simple]
    for standard_name, handle_type in _HANDLE_TYPE_NAMES_BY_LENGTH:
        if standard_name in simple:
            return handle_type
    return None


THandle = TypeVar("THandle", bound=Handle)


def handle_type_from_java_class_name(class_name: str | None) -> type[Handle] | None:
    """Infer the Python handle type from a Java/vendor class name.

    Real Java RTIs often return implementation classes such as
    ``com.vendor.rti.ObjectInstanceHandleImpl`` rather than the exact
    ``hla.rti1516e.ObjectInstanceHandle`` interface name.  Match the longest
    known HLA handle token while ignoring factory/set/map helper classes.
    """

    if not class_name:
        return None
    text = str(class_name)
    simple = text.rsplit(".", 1)[-1].split("$", 1)[-1]
    candidates = (simple, text)
    excluded_tokens = ("Factory", "Set", "Map", "Encoder", "Decoder")
    for handle_name, handle_type in sorted(
        HANDLE_TYPE_BY_JAVA_SIMPLE_NAME.items(), key=lambda item: len(item[0]), reverse=True
    ):
        for candidate in candidates:
            if candidate == handle_name:
                return handle_type
            if handle_name in candidate and not any(token in candidate for token in excluded_tokens):
                return handle_type
    return None


@dataclass(frozen=True)
class NativeObjectRef:
    """Explicit wrapper for a backend-native object.

    This is useful for advanced callers who need to pass a native JPype/Py4J
    object through the Python layer without conversion.
    """

    value: Any


class NativeHandleRegistry:
    """Map backend-native HLA handle objects to stable Python surrogate handles.

    Java RTIs usually return opaque Java handle instances.  Python application
    code should not have to keep those bridge objects.  The registry creates a
    typed Python ``Handle`` with an adapter-local integer value and remembers how
    to convert it back when the handle is passed to the same backend later.
    """

    def __init__(self) -> None:
        self._next_value = 1
        self._native_by_key: MutableMapping[tuple[type[Handle], int], Any] = {}
        self._python_by_native_key: MutableMapping[tuple[type[Handle], Hashable], Handle] = {}

    @staticmethod
    def native_key(native: Any) -> Hashable:
        """Return a stable key for a backend-native handle object.

        Java RTIs may hand the adapter a fresh proxy object for the same semantic
        HLA handle in a later callback. Prefer encoded bytes or explicit numeric
        values, then Java ``hashCode`` plus class name, then Python hash, and
        finally object identity. This makes Java-created objects round-trip
        through JPype/Py4J as stable Python handles whenever the backend exposes
        value semantics.
        """

        class_name = None
        get_class = getattr(native, "getClass", None)
        if callable(get_class):
            try:
                class_info = cast(Any, get_class())
                get_name = getattr(class_info, "getName", None)
                if callable(get_name):
                    class_name = str(get_name())
            except Exception:
                class_name = None
        if class_name is None:
            cls = getattr(native, "__class__", None)
            class_name = getattr(cls, "__name__", None)

        for method_name in ("encoded", "encode"):
            method = getattr(native, method_name, None)
            if callable(method):
                try:
                    data = method()
                except TypeError:
                    data = None
                except Exception:
                    data = None
                if isinstance(data, (bytes, bytearray, memoryview)):
                    return ("encoded", class_name, bytes(data))

        for attr_name in ("getValue", "value", "longValue", "intValue"):
            attr = getattr(native, attr_name, None)
            try:
                raw = attr() if callable(attr) else attr
            except Exception:
                raw = None
            if raw is not None:
                try:
                    hash(raw)
                    return ("value", class_name, raw)
                except Exception:
                    pass

        hash_code = getattr(native, "hashCode", None)
        if callable(hash_code):
            try:
                java_hash = cast(Callable[[], Any], hash_code)()
                return ("java-hash", class_name, int(java_hash))
            except Exception:
                pass

        try:
            return ("py-hash", class_name, hash(native))
        except Exception:
            return ("id", id(native))

    def to_python(self, handle_type: type[THandle], native: Any) -> THandle:
        key = (handle_type, self.native_key(native))
        existing = self._python_by_native_key.get(key)
        if existing is not None:
            return cast(THandle, existing)
        value = self._next_value
        self._next_value += 1
        py_handle = handle_type(value)
        self._python_by_native_key[key] = py_handle
        self._native_by_key[(handle_type, value)] = native
        return py_handle

    def to_native(self, handle: Handle) -> Any:
        key = (type(handle), handle.value)
        try:
            return self._native_by_key[key]
        except KeyError as exc:
            raise BackendConversionError(
                f"Cannot convert {handle!r} to a backend-native handle. "
                "Only handles returned by this backend can be passed back to it."
            ) from exc


class ValueConverter:
    """Base value converter used by generic backends.

    Subclasses for Java bridges can override detection and collection creation
    without changing the RTIAmbassador façade.
    """

    def __init__(self, *, handle_registry: NativeHandleRegistry | None = None) -> None:
        self.handle_registry = handle_registry or NativeHandleRegistry()

    def to_backend(self, value: Any) -> Any:
        """Convert a Python value before sending it to a backend."""
        if isinstance(value, NativeObjectRef):
            return value.value
        if isinstance(value, Handle):
            return self.handle_registry.to_native(value)
        if isinstance(value, Enum):
            return self.to_backend_enum(value)
        if isinstance(value, bytes):
            return self.to_backend_bytes(value)
        if isinstance(value, tuple):
            return tuple(self.to_backend(item) for item in value)
        if isinstance(value, list):
            return [self.to_backend(item) for item in value]
        if isinstance(value, set):
            return {self.to_backend(item) for item in value}
        if isinstance(value, frozenset):
            return frozenset(self.to_backend(item) for item in value)
        if isinstance(value, Mapping):
            return {self.to_backend(k): self.to_backend(v) for k, v in value.items()}
        return value

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        """Convert a value returned by a backend to a Python value."""
        handle_type = handle_type_from_java_type_name(expected_type_name)
        if handle_type is not None:
            return self.handle_registry.to_python(handle_type, value)
        return value

    def to_backend_args(self, args: Iterable[Any]) -> tuple[Any, ...]:
        return tuple(self.to_backend(arg) for arg in args)

    def to_backend_kwargs(self, kwargs: Mapping[str, Any]) -> dict[str, Any]:
        return {name: self.to_backend(value) for name, value in kwargs.items()}

    def to_backend_enum(self, value: Enum) -> Any:
        # Java adapters override this to look up the Java enum constant.  Generic
        # backends receive the Python enum object directly.
        return value

    def to_backend_bytes(self, value: bytes) -> Any:
        # Java adapters override this if their bridge requires byte[] creation.
        return value


__all__ = [
    "HANDLE_TYPE_BY_JAVA_SIMPLE_NAME",
    "HANDLE_TYPES",
    "clean_java_type_name",
    "handle_type_from_java_type_name",
    "handle_type_from_java_class_name",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "ValueConverter",
]
