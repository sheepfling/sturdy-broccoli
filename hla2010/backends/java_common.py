"""Shared Java RTI backend support.

Concrete bridge packages, such as :mod:`hla2010.backends.jpype` and
:mod:`hla2010.backends.py4j`, supply the mechanics for their Java bridge.
This module supplies the bridge-independent policy: overload argument ordering,
value conversion hooks, callback dispatching, Java collection conversion, and
Java exception translation.
"""
from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable as CollectionsIterable
from collections.abc import Mapping as CollectionsMapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from .. import enums as hla_enums
from .. import exceptions as hla_exceptions
from .. import handles as hla_handles
from ..runtime_api import FederateAmbassador
from ..exceptions import FederateInternalError, RTIexception, RTIinternalError
from ..fom import module_uri
from ..raw_api import API_METADATA
from ..time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from .base import (
    CALLBACK_METHOD_NAMES,
    BackendConversionError,
    BackendInfo,
    Invocation,
    RTIBackend,
    lower_camel_to_snake,
)
from .conversion import (
    NativeHandleRegistry,
    ValueConverter,
    clean_java_type_name,
    handle_type_from_java_class_name,
    handle_type_from_java_type_name,
)

_PYTHON_ENUM_BY_JAVA_SIMPLE_NAME: dict[str, type[Enum]] = {
    name: value
    for name, value in vars(hla_enums).items()
    if isinstance(value, type) and issubclass(value, Enum)
}


class JavaBridge(ABC):
    """Bridge operations needed by ``JavaRTIBackend``.

    Implementations are deliberately small: JPype and Py4J have very different
    object models, but both can provide these operations.  Methods with default
    implementations are conservative fallbacks so test shims can be lightweight
    and vendor-specific adapters can override only the pieces they need.
    """

    name: str = "java"

    @abstractmethod
    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        """Call ``obj.method_name(*args)`` in the Java runtime."""
        raise NotImplementedError

    @abstractmethod
    def create_federate_proxy(self, dispatcher: "PythonFederateAmbassadorDispatcher") -> Any:
        """Create a Java-side FederateAmbassador proxy for ``dispatcher``."""
        raise NotImplementedError

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        """Return a Java enum constant.

        Bridges override this when they can look up Java classes.  The default is
        intentionally strict so conversion errors are caught at the boundary.
        """
        raise BackendConversionError(f"Bridge {self.name} cannot resolve Java enum {enum_class_name}.{member_name}")

    def enum_member_name(self, value: Any) -> str | None:
        """Return a Java enum constant's member name, if detectable."""
        name_attr = getattr(value, "name", None)
        if callable(name_attr):
            try:
                return str(name_attr())
            except Exception:
                pass
        if isinstance(name_attr, str):
            return name_attr
        # Some bridge objects stringify as "EnumClass.MEMBER".
        text = str(value)
        if "." in text and text.rsplit(".", 1)[-1].isidentifier():
            return text.rsplit(".", 1)[-1]
        return None

    def byte_array(self, data: bytes) -> Any:
        """Create a Java byte[] from Python bytes.  Default passes bytes through."""
        return data

    def is_byte_array(self, value: Any) -> bool:
        """Best-effort detection for Java byte[] values returned by a backend."""
        if isinstance(value, (bytes, bytearray, memoryview)):
            return True
        simple_name = self.simple_class_name(value)
        class_name = self.full_class_name(value) or simple_name or ""
        return simple_name in {"byte[]", "byte"} or class_name in {"[B", "byte[]"}

    def to_python_bytes(self, value: Any) -> bytes:
        """Convert a Java byte[]-like object to immutable Python bytes."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, bytearray):
            return bytes(value)
        if isinstance(value, memoryview):
            return value.tobytes()
        try:
            return bytes((int(item) + 256) % 256 for item in value)
        except Exception as exc:
            raise BackendConversionError(f"Could not convert Java byte[] value {value!r} to bytes") from exc

    def new_set(self, values: Sequence[Any]) -> Any:
        """Create a Java Set-like object.  Default returns a Python set for shims."""
        return set(values)

    def new_list(self, values: Sequence[Any]) -> Any:
        """Create a Java List-like object.  Default returns a Python list for shims."""
        return list(values)

    def new_map(self, items: Sequence[tuple[Any, Any]]) -> Any:
        """Create a Java Map-like object.  Default returns a Python dict for shims."""
        return dict(items)

    def fom_url(self, value: Any) -> Any:
        """Create a Java URL-like value for a FOM/MIM module designator."""
        return module_uri(value)

    def fom_url_array(self, values: Sequence[Any]) -> Any:
        """Create a Java URL[]-like value for FOM/MIM module designators."""
        return [self.fom_url(value) for value in values]

    def new_handle_set(self, type_name: str, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        """Create an RTI-owned Java handle set where possible."""
        return self.new_set(values)

    def new_handle_value_map(self, type_name: str, items: Sequence[tuple[Any, Any]], *, rti_ambassador: Any | None = None) -> Any:
        """Create an RTI-owned Java handle-value map where possible."""
        return self.new_map(items)

    def new_attribute_set_region_set_pair_list(self, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        """Create a Java AttributeSetRegionSetPairList where possible."""
        return self.new_list(values)

    def logical_time(self, value: Any, *, rti_ambassador: Any | None = None) -> Any:
        """Convert a Python logical-time object to a Java logical-time object.

        Vendor RTIs usually require logical-time values created by the RTI's own
        ``getTimeFactory()``.  Concrete bridges should use that factory when it
        is available and fall back to shim classes only for tests.
        """
        return value

    def java_map_items(self, value: Any) -> Sequence[tuple[Any, Any]] | None:
        """Return Java Map items, or ``None`` when ``value`` is not map-like."""
        if isinstance(value, CollectionsMapping):
            return list(value.items())
        entry_set = getattr(value, "entrySet", None)
        if callable(entry_set):
            try:
                entries = entry_set()
                return [(entry.getKey(), entry.getValue()) for entry in entries]
            except Exception:
                return None
        return None

    def java_collection_values(self, value: Any) -> Sequence[Any] | None:
        """Return Java Collection values, or ``None`` when not collection-like."""
        if isinstance(value, (str, bytes, bytearray, memoryview, CollectionsMapping)):
            return None
        if isinstance(value, (list, tuple, set, frozenset)):
            return list(value)
        iterator = getattr(value, "iterator", None)
        if callable(iterator):
            try:
                it = iterator()
                result: list[Any] = []
                while it.hasNext():
                    result.append(it.next())
                return result
            except Exception:
                return None
        return None

    def full_class_name(self, obj: Any) -> str | None:
        """Best-effort Java fully qualified class name."""
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getName())
            except Exception:
                pass
        return None

    def simple_class_name(self, obj: Any) -> str | None:
        """Best-effort Java simple class name for return-value conversion."""
        cls = getattr(obj, "__class__", None)
        name = getattr(cls, "__name__", None)
        return name

    def exception_class_name(self, exc: BaseException) -> str | None:
        cls = getattr(exc, "__class__", None)
        name = getattr(cls, "__name__", None)
        return name

    def exception_message(self, exc: BaseException) -> str:
        return str(exc)


def _maybe_call_noarg(obj: Any, *names: str) -> Any:
    for name in names:
        attr = getattr(obj, name, None)
        if callable(attr):
            try:
                return attr()
            except Exception:
                pass
        elif attr is not None:
            return attr
    return None


class JavaValueConverter(ValueConverter):
    """Value converter for Java bridge backends.

    The converter is intentionally generic enough for JPype, Py4J, and the
    in-process test shims.  Vendor adapters can still subclass it when an RTI
    requires factory-owned handle sets/maps or custom logical-time factories.
    """

    def __init__(
        self,
        bridge: JavaBridge,
        *,
        handle_registry: NativeHandleRegistry | None = None,
        rti_ambassador: Any | None = None,
    ):
        super().__init__(handle_registry=handle_registry)
        self.bridge = bridge
        self.rti_ambassador = rti_ambassador

    def to_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:  # noqa: D401 - inherited contract
        from ..handles import Handle

        expected = _clean_java_type(expected_type_name)

        if expected == "URL":
            return self.bridge.fom_url(value)
        if expected == "URL[]":
            values = _sequence_for_java_array(value)
            return self.bridge.fom_url_array(values)

        if isinstance(value, Handle):
            return self.handle_registry.to_native(value)
        if isinstance(value, Enum):
            return self.to_backend_enum(value)
        if isinstance(value, bytes):
            return self.to_backend_bytes(value)
        if isinstance(value, bytearray):
            return self.to_backend_bytes(bytes(value))

        if expected in _JAVA_HANDLE_SET_TYPES:
            values = [self.to_backend(item) for item in _sequence_for_java_array(value)]
            return self.bridge.new_handle_set(expected, values, rti_ambassador=self.rti_ambassador)

        if expected in _JAVA_HANDLE_VALUE_MAP_TYPES and isinstance(value, Mapping):
            items = [(self.to_backend(k), self.to_backend(v)) for k, v in value.items()]
            return self.bridge.new_handle_value_map(expected, items, rti_ambassador=self.rti_ambassador)

        if expected == "AttributeSetRegionSetPairList":
            return self.bridge.new_attribute_set_region_set_pair_list(
                [self.to_backend(item) for item in _sequence_for_java_array(value)],
                rti_ambassador=self.rti_ambassador,
            )

        if isinstance(value, tuple):
            return tuple(self.to_backend(item) for item in value)
        if isinstance(value, list):
            return self.bridge.new_list([self.to_backend(item) for item in value])
        if isinstance(value, (set, frozenset)):
            return self.bridge.new_set([self.to_backend(item) for item in value])
        if isinstance(value, Mapping):
            return self.bridge.new_map([(self.to_backend(k), self.to_backend(v)) for k, v in value.items()])
        if isinstance(value, (HLAinteger64Time, HLAinteger64Interval, HLAfloat64Time, HLAfloat64Interval)):
            return self.bridge.logical_time(value, rti_ambassador=self.rti_ambassador)
        return super().to_backend(value)

    def to_backend_enum(self, value: Enum) -> Any:
        enum_class_name = f"hla.rti1516e.{value.__class__.__name__}"
        return self.bridge.enum_constant(enum_class_name, value.name)

    def to_backend_bytes(self, value: bytes) -> Any:
        return self.bridge.byte_array(value)

    def to_backend_args(self, args: Sequence[Any], expected_type_names: Sequence[str | None] | None = None) -> tuple[Any, ...]:
        expected = tuple(expected_type_names or ())
        return tuple(
            self.to_backend(arg, expected_type_name=expected[idx] if idx < len(expected) else None)
            for idx, arg in enumerate(args)
        )

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if value is None:
            return None

        expected = _clean_java_type(expected_type_name)

        if self.bridge.is_byte_array(value):
            return self.bridge.to_python_bytes(value)

        expected_handle_type = handle_type_from_java_type_name(expected)
        if expected_handle_type is not None:
            return self.handle_registry.to_python(expected_handle_type, value)

        simple_name = self.bridge.simple_class_name(value)
        class_text = " ".join(filter(None, [simple_name, self.bridge.full_class_name(value)]))
        inferred_handle_type = handle_type_from_java_class_name(class_text)
        if inferred_handle_type is not None:
            return self.handle_registry.to_python(inferred_handle_type, value)

        if expected in _PY_HANDLE_VALUE_MAP_BY_JAVA_TYPE:
            map_items = self.bridge.java_map_items(value)
            if map_items is None and isinstance(value, Mapping):
                map_items = list(value.items())
            if map_items is not None:
                map_type, key_type_name = _PY_HANDLE_VALUE_MAP_BY_JAVA_TYPE[expected]
                return map_type(
                    (
                        self.from_backend(key, expected_type_name=key_type_name),
                        self.from_backend(item_value),
                    )
                    for key, item_value in map_items
                )

        if expected in _PY_HANDLE_SET_BY_JAVA_TYPE:
            collection_values = self.bridge.java_collection_values(value)
            if collection_values is None and isinstance(value, (list, tuple, set, frozenset)):
                collection_values = list(value)
            if collection_values is not None:
                set_type, item_type_name = _PY_HANDLE_SET_BY_JAVA_TYPE[expected]
                return set_type(self.from_backend(item, expected_type_name=item_type_name) for item in collection_values)

        if simple_name in _PYTHON_ENUM_BY_JAVA_SIMPLE_NAME:
            member_name = self.bridge.enum_member_name(value)
            if member_name:
                enum_type = _PYTHON_ENUM_BY_JAVA_SIMPLE_NAME[simple_name]
                try:
                    return enum_type[member_name]
                except KeyError:
                    pass

        logical_time = self._from_backend_logical_time(value, simple_name=simple_name)
        if logical_time is not None:
            return logical_time

        map_items = self.bridge.java_map_items(value)
        if map_items is not None:
            return {
                self.from_backend(key): self.from_backend(item_value)
                for key, item_value in map_items
            }

        # Preserve native Python sequence shapes for in-process shims.  Real Java
        # collections normally reach the generic bridge.java_collection_values
        # branch below.
        if isinstance(value, tuple):
            return tuple(self.from_backend(item) for item in value)
        if isinstance(value, list):
            return [self.from_backend(item) for item in value]
        if isinstance(value, (set, frozenset)):
            return {self.from_backend(item) for item in value}

        collection_values = self.bridge.java_collection_values(value)
        if collection_values is not None:
            return {self.from_backend(item) for item in collection_values}

        return value

    def _from_backend_logical_time(self, value: Any, *, simple_name: str | None) -> Any | None:
        class_text = " ".join(filter(None, [simple_name, self.bridge.full_class_name(value)]))
        if not any(token in class_text for token in ("HLAinteger64Time", "HLAinteger64Interval", "HLAfloat64Time", "HLAfloat64Interval")):
            return None

        raw = _maybe_call_noarg(value, "getValue", "value", "longValue", "doubleValue")
        if raw is None:
            return None
        if "HLAinteger64Time" in class_text:
            return HLAinteger64Time(int(raw))
        if "HLAinteger64Interval" in class_text:
            return HLAinteger64Interval(int(raw))
        if "HLAfloat64Time" in class_text:
            return HLAfloat64Time(float(raw))
        if "HLAfloat64Interval" in class_text:
            return HLAfloat64Interval(float(raw))
        return None


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

_PY_HANDLE_SET_BY_JAVA_TYPE = {
    "AttributeHandleSet": (hla_handles.AttributeHandleSet, "AttributeHandle"),
    "DimensionHandleSet": (hla_handles.DimensionHandleSet, "DimensionHandle"),
    "FederateHandleSet": (hla_handles.FederateHandleSet, "FederateHandle"),
    "InteractionClassHandleSet": (hla_handles.InteractionClassHandleSet, "InteractionClassHandle"),
    "RegionHandleSet": (hla_handles.RegionHandleSet, "RegionHandle"),
}

_PY_HANDLE_VALUE_MAP_BY_JAVA_TYPE = {
    "AttributeHandleValueMap": (hla_handles.AttributeHandleValueMap, "AttributeHandle"),
    "ParameterHandleValueMap": (hla_handles.ParameterHandleValueMap, "ParameterHandle"),
}


def _clean_java_type(type_name: str | None) -> str | None:
    return clean_java_type_name(type_name)


def _sequence_for_java_array(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray, memoryview, os.PathLike)):
        return [value]
    if isinstance(value, CollectionsIterable):
        return list(value)
    return [value]


def _split_java_params(params: str) -> list[str]:
    params = params.strip()
    if not params:
        return []
    # The 1516.1 Java declarations used to build API_METADATA do not contain
    # nested generic commas in RTIambassador parameter lists.  Keep this parser
    # intentionally simple and predictable.
    return [part.strip() for part in params.split(",") if part.strip()]


def _param_name(param_decl: str) -> str:
    # Examples: "String federationExecutionName", "URL[] fomModules",
    # "byte[] userSuppliedTag".
    return re.split(r"\s+", param_decl.strip())[-1].replace("...", "")


def _param_type(param_decl: str) -> str:
    pieces = re.split(r"\s+", param_decl.strip())
    if len(pieces) <= 1:
        return ""
    return _clean_java_type(" ".join(pieces[:-1])) or ""


def java_parameter_names(overload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(_param_name(part) for part in _split_java_params(str(overload.get("params", ""))))


def java_parameter_types(overload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(_param_type(part) for part in _split_java_params(str(overload.get("params", ""))))


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


def _score_value_for_java_type(param_type: str, param_name: str, value: Any) -> int:
    t = _clean_java_type(param_type) or ""
    score = 0

    if t == "String":
        score += 4 if isinstance(value, str) else -6
        if param_name == "logicalTimeImplementationName":
            score += 8 if _looks_like_time_factory_name(value) else -3
        return score

    if t == "URL":
        if _looks_like_time_factory_name(value):
            return -8
        if _is_sequence_not_text(value):
            return -5
        return 5 if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri") else 1

    if t == "URL[]":
        if _is_sequence_not_text(value):
            return 6
        if _looks_like_time_factory_name(value):
            return -8
        # A single path can be promoted to URL[], but prefer the URL overload
        # when Java offers both at the same arity.
        return 1 if isinstance(value, (str, os.PathLike)) or hasattr(value, "uri") else 0

    if t in _JAVA_HANDLE_SET_TYPES:
        return 6 if _is_sequence_not_text(value) else -4

    if t in _JAVA_HANDLE_VALUE_MAP_TYPES:
        return 6 if _is_mapping(value) else -4

    if t == "AttributeSetRegionSetPairList":
        return 6 if _is_sequence_not_text(value) else -4

    if t == "byte[]":
        return 6 if isinstance(value, (bytes, bytearray, memoryview)) else -2

    if t in {"LogicalTime", "LogicalTimeInterval"}:
        if isinstance(value, (HLAinteger64Time, HLAinteger64Interval, HLAfloat64Time, HLAfloat64Interval)):
            return 8
        if isinstance(value, (int, float)):
            return 2

    return score


@dataclass(frozen=True)
class ResolvedJavaInvocation:
    args: tuple[Any, ...]
    param_types: tuple[str | None, ...]
    overload: Mapping[str, Any] | None = None


def resolve_java_invocation(invocation: Invocation) -> ResolvedJavaInvocation:
    """Resolve args/kwargs and select the most likely Java overload.

    JPype/Py4J can perform Java overload resolution, but the adapter needs the
    selected parameter *shapes* before the call so it can build URL arrays,
    RTI-owned handle sets, and RTI-owned handle-value maps.
    """

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
        score = sum(_score_value_for_java_type(types[idx], names[idx], value) for idx, value in enumerate(ordered))
        candidates.append((score, -source_index, ordered, types, overload))

    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        _, _, ordered, types, overload = candidates[0]
        return ResolvedJavaInvocation(args=ordered, param_types=tuple(types), overload=overload)

    names_by_overload = [java_parameter_names(o) for o in java_overloads]
    raise BackendConversionError(
        f"Could not map arguments for {invocation.method_name}. "
        f"Provided args={len(invocation.args)} kwargs={list(invocation.kwargs)}; Java overload parameters={names_by_overload}"
    )


def resolve_java_arguments(invocation: Invocation) -> tuple[Any, ...]:
    """Resolve args/kwargs against Java overload metadata.

    Java itself has no keyword arguments; this helper lets Python callers use
    either Java-style names or snake_case names.  It returns only ordered values
    for backwards compatibility; Java backends should prefer
    :func:`resolve_java_invocation` so type-aware conversion can happen.
    """

    return resolve_java_invocation(invocation).args


def expected_java_return_type(invocation: Invocation) -> str | None:
    return_types = {
        _clean_java_type(str(o.get("return_type", "")).strip()) or ""
        for o in invocation.overloads
        if o.get("language") == "java" and str(o.get("return_type", "")).strip() not in {"", "void"}
    }
    return_types.discard("")
    if len(return_types) == 1:
        return next(iter(return_types))
    return None




def expected_java_callback_parameter_types(method_name: str, arg_count: int | None = None) -> tuple[str | None, ...]:
    """Return Java parameter types for a FederateAmbassador callback overload.

    Callback conversion needs the expected Java shapes because vendors often
    deliver maps/sets through implementation classes rather than API interface
    names.  The metadata is source-derived from the uploaded Java binding.
    """

    overloads = [
        overload
        for overload in API_METADATA.get("FederateAmbassador", {}).get(method_name, ())
        if overload.get("language") == "java"
    ]
    if arg_count is not None:
        overloads = [overload for overload in overloads if len(java_parameter_types(overload)) == arg_count]
    if overloads:
        return tuple(java_parameter_types(overloads[0]))
    return ()

class PythonFederateAmbassadorDispatcher:
    """Dispatch Java FederateAmbassador callbacks to a Python ambassador."""

    def __init__(self, ambassador: FederateAmbassador, converter: JavaValueConverter):
        self.ambassador = ambassador
        self.converter = converter

    def _invoke_callback(self, method_name: str, *backend_args: Any) -> Any:
        try:
            expected = expected_java_callback_parameter_types(method_name, len(backend_args))
            py_args = tuple(
                self.converter.from_backend(
                    arg,
                    expected_type_name=expected[idx] if idx < len(expected) else None,
                )
                for idx, arg in enumerate(backend_args)
            )
            result = getattr(self.ambassador, method_name)(*py_args)
            return self.converter.to_backend(result) if result is not None else None
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc) from exc


# Add concrete methods for every HLA callback.  Py4J's callback server is happier
# with real attributes than with __getattr__ generated callables, and JPype can
# consume the same dispatcher instance.
def _make_callback_dispatcher(method_name: str):
    def _callback(self: PythonFederateAmbassadorDispatcher, *args: Any) -> Any:
        return self._invoke_callback(method_name, *args)

    _callback.__name__ = method_name
    _callback.__qualname__ = f"PythonFederateAmbassadorDispatcher.{method_name}"
    return _callback


for _callback_name in CALLBACK_METHOD_NAMES:
    setattr(PythonFederateAmbassadorDispatcher, _callback_name, _make_callback_dispatcher(_callback_name))


class JavaRTIBackend(RTIBackend):
    """RTIBackend implementation for an already-created Java RTIambassador."""

    def __init__(
        self,
        *,
        java_rti_ambassador: Any,
        bridge: JavaBridge,
        converter: JavaValueConverter | None = None,
        info: BackendInfo | None = None,
        connect_local_settings_designator: str | None = None,
    ) -> None:
        self.java_rti_ambassador = java_rti_ambassador
        self.bridge = bridge
        self.converter = converter or JavaValueConverter(bridge, rti_ambassador=java_rti_ambassador)
        self.converter.rti_ambassador = java_rti_ambassador
        self.info = info or BackendInfo(name=bridge.name, kind="java")
        self.connect_local_settings_designator = connect_local_settings_designator
        self._connected_ambassador_proxies: list[tuple[FederateAmbassador, PythonFederateAmbassadorDispatcher, Any]] = []

    def invoke(self, invocation: Invocation) -> Any:
        if (
            invocation.method_name == "connect"
            and self.connect_local_settings_designator
            and len(invocation.args) == 2
            and not invocation.kwargs
        ):
            invocation = Invocation(
                method_name=invocation.method_name,
                args=(*invocation.args, self.connect_local_settings_designator),
                kwargs=invocation.kwargs,
                overloads=invocation.overloads,
            )
        resolved = resolve_java_invocation(invocation)
        backend_args = self.converter.to_backend_args(resolved.args, expected_type_names=resolved.param_types)
        result = self.bridge.call(self.java_rti_ambassador, invocation.method_name, *backend_args)
        return self.converter.from_backend(result, expected_type_name=expected_java_return_type(invocation))

    def adapt_federate_ambassador(self, ambassador: FederateAmbassador) -> Any:
        dispatcher = PythonFederateAmbassadorDispatcher(ambassador, self.converter)
        proxy = self.bridge.create_federate_proxy(dispatcher)
        # JPype and Py4J callback objects need a live Python-side reference or
        # vendor callbacks can disappear after connect.
        self._connected_ambassador_proxies.append((ambassador, dispatcher, proxy))
        return proxy

    def close(self) -> None:
        close = getattr(self.bridge, "close", None)
        if callable(close):
            close()

    def translate_exception(self, exc: BaseException, invocation: Invocation) -> RTIexception:
        if isinstance(exc, RTIexception):
            return exc

        simple_name = self.bridge.exception_class_name(exc)
        if simple_name:
            simple_name = simple_name.split(".")[-1].split("$")[-1]
            py_exc_type = getattr(hla_exceptions, simple_name, None)
            if isinstance(py_exc_type, type) and issubclass(py_exc_type, RTIexception):
                return py_exc_type(self.bridge.exception_message(exc), cause=exc)

        return RTIinternalError(
            f"Java backend failed during {invocation.method_name}: {self.bridge.exception_message(exc)}",
            cause=exc,
        )


__all__ = [
    "JavaBridge",
    "JavaRTIBackend",
    "JavaValueConverter",
    "PythonFederateAmbassadorDispatcher",
    "expected_java_callback_parameter_types",
    "expected_java_return_type",
    "java_parameter_names",
    "java_parameter_types",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "ResolvedJavaInvocation",
]
