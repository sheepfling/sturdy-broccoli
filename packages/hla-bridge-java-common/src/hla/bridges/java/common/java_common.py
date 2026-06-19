"""Shared Java RTI backend support.

Concrete bridge packages, such as :mod:`hla.rti1516e.backends.jpype` and
:mod:`hla.rti1516e.backends.py4j`, supply the mechanics for their Java bridge.
This module supplies the bridge-independent policy: overload argument ordering,
value conversion hooks, callback dispatching, Java collection conversion, and
Java exception translation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping as CollectionsMapping
from enum import Enum
from typing import Any, Iterable, Mapping, Protocol, Sequence, cast

from hla.rti1516e import enums as hla_enums
from hla.rti1516e import exceptions as hla_exceptions
from hla.rti1516e import handles as hla_handles
from hla.backends.common import (
    CALLBACK_METHOD_NAMES,
    BackendConversionError,
    BackendInfo,
    Invocation,
    RTIBackend,
    lower_camel_to_snake,
)
from hla.backends.common import (
    NativeHandleRegistry,
    ResolvedJavaInvocation,
    ValueConverter,
    clean_java_type_name,
    handle_type_from_java_class_name,
    handle_type_from_java_type_name,
    java_parameter_names,
    java_parameter_types,
    resolve_java_arguments,
    resolve_java_invocation,
)
from hla.backends.common.invocation import (
    _JAVA_HANDLE_SET_TYPES,
    _JAVA_HANDLE_VALUE_MAP_TYPES,
)
from hla.rti1516e.exceptions import FederateInternalError, RTIexception, RTIinternalError
from hla.rti1516e.fom import module_uri
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla.rti1516e.datatypes import (
    AttributeRegionAssociation,
    FederationExecutionInformation,
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    MessageRetractionReturn,
    RangeBounds,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
    TimeQueryReturn,
)

_PYTHON_ENUM_BY_JAVA_SIMPLE_NAME: dict[str, type[Enum]] = {
    name: value
    for name, value in vars(hla_enums).items()
    if isinstance(value, type) and issubclass(value, Enum)
}


class _JavaMapEntry(Protocol):
    def getKey(self) -> Any: ...

    def getValue(self) -> Any: ...


class _JavaIterator(Protocol):
    def hasNext(self) -> bool: ...

    def next(self) -> Any: ...


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

    def range_bounds(self, value: RangeBounds) -> Any:
        """Convert Python RangeBounds to a Java RangeBounds-like object."""
        return value

    def java_map_items(self, value: Any) -> Sequence[tuple[Any, Any]] | None:
        """Return Java Map items, or ``None`` when ``value`` is not map-like."""
        if isinstance(value, CollectionsMapping):
            return list(value.items())
        entry_set = getattr(value, "entrySet", None)
        if callable(entry_set):
            try:
                entries = cast(Iterable[_JavaMapEntry], entry_set())
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
                it = cast(_JavaIterator, iterator())
                result: list[Any] = []
                while it.hasNext():
                    result.append(it.next())
                return result
            except Exception:
                return None
        return None

    def public_field(self, obj: Any, field_name: str) -> Any | None:
        """Return a public Java field value when the bridge exposes one."""
        get_field = getattr(obj, "_get_field", None)
        if callable(get_field):
            try:
                found, value = cast(tuple[bool, Any], get_field(field_name))
                if found:
                    return value
            except Exception:
                pass
        try:
            value = getattr(obj, field_name)
        except Exception:
            return None
        return None if callable(value) else value

    def full_class_name(self, obj: Any) -> str | None:
        """Best-effort Java fully qualified class name."""
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                class_info = cast(Any, get_class())
                get_name = getattr(class_info, "getName", None)
                if callable(get_name):
                    return str(get_name())
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


def _sequence_for_java_array(value: Any) -> list[Any]:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return [value]
    if isinstance(value, Iterable):
        return list(value)
    return [value]


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
        from hla.rti1516e.handles import Handle

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

        if isinstance(value, RangeBounds):
            return self.bridge.range_bounds(value)
        if isinstance(value, AttributeRegionAssociation):
            return (
                self.to_backend(value.ahset, expected_type_name="AttributeHandleSet"),
                self.to_backend(value.rhset, expected_type_name="RegionHandleSet"),
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

    def to_backend_args(self, args: Iterable[Any], expected_type_names: Iterable[str | None] | None = None) -> tuple[Any, ...]:
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

        expected_handle_type = None if expected in _JAVA_COMPOSITE_DATATYPE_NAMES else handle_type_from_java_type_name(expected)
        if expected_handle_type is not None:
            return self.handle_registry.to_python(expected_handle_type, value)

        simple_name = self.bridge.simple_class_name(value)
        time_query_return = self._from_backend_time_query_return(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if time_query_return is not None:
            return time_query_return

        message_retraction_return = self._from_backend_message_retraction_return(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if message_retraction_return is not None:
            return message_retraction_return

        save_status_pair = self._from_backend_federate_handle_save_status_pair(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if save_status_pair is not None:
            return save_status_pair

        restore_status = self._from_backend_federate_restore_status(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if restore_status is not None:
            return restore_status

        supplemental_reflect = self._from_backend_supplemental_reflect_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
            info_type=SupplementalReflectInfo,
        )
        if supplemental_reflect is not None:
            return supplemental_reflect

        supplemental_receive = self._from_backend_supplemental_reflect_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
            info_type=SupplementalReceiveInfo,
        )
        if supplemental_receive is not None:
            return supplemental_receive

        supplemental_remove = self._from_backend_supplemental_remove_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if supplemental_remove is not None:
            return supplemental_remove

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

        if expected == "FederationExecutionInformationSet":
            collection_values = self.bridge.java_collection_values(value)
            if collection_values is None and isinstance(value, (list, tuple, set, frozenset)):
                collection_values = list(value)
            if collection_values is not None:
                return {
                    self.from_backend(item, expected_type_name="FederationExecutionInformation")
                    for item in collection_values
                }

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

        range_bounds = self._from_backend_range_bounds(value, expected_type_name=expected, simple_name=simple_name)
        if range_bounds is not None:
            return range_bounds

        federation_execution_info = self._from_backend_federation_execution_information(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if federation_execution_info is not None:
            return federation_execution_info

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

    def _from_backend_range_bounds(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> RangeBounds | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "RangeBounds" not in class_text:
            return None

        lower = _maybe_call_noarg(value, "getLowerBound", "lowerBound", "lower", "getLower")
        upper = _maybe_call_noarg(value, "getUpperBound", "upperBound", "upper", "getUpper")
        if lower is None or upper is None:
            return None
        return RangeBounds(int(lower), int(upper))

    def _from_backend_federation_execution_information(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> FederationExecutionInformation | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederationExecutionInformation" not in class_text:
            return None

        federation_name = self.bridge.public_field(value, "federationExecutionName")
        logical_time_name = self.bridge.public_field(value, "logicalTimeImplementationName")
        if federation_name is None:
            return None
        return FederationExecutionInformation(
            federationExecutionName=str(federation_name),
            logicalTimeImplementationName=str(logical_time_name) if logical_time_name is not None else "",
        )

    def _from_backend_time_query_return(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> TimeQueryReturn | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "TimeQueryReturn" not in class_text:
            return None

        valid = _maybe_call_noarg(
            value,
            "timeIsValid",
            "getTimeIsValid",
            "logicalTimeIsValid",
            "getLogicalTimeIsValid",
        )
        if valid is None:
            return None
        raw_time = self.bridge.public_field(value, "time")
        if raw_time is None:
            raw_time = self.bridge.public_field(value, "logicalTime")
        if raw_time is None:
            raw_time = _maybe_call_noarg(value, "getTime", "getLogicalTime")
        return TimeQueryReturn(bool(valid), self.from_backend(raw_time) if raw_time is not None else None)

    def _from_backend_message_retraction_return(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> MessageRetractionReturn | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "MessageRetractionReturn" not in class_text:
            return None

        valid = _maybe_call_noarg(
            value,
            "retractionHandleIsValid",
            "getRetractionHandleIsValid",
            "messageRetractionHandleIsValid",
        )
        handle = self.bridge.public_field(value, "handle")
        if handle is None:
            handle = self.bridge.public_field(value, "messageRetractionHandle")
        if handle is None:
            handle = _maybe_call_noarg(value, "getHandle", "getMessageRetractionHandle")
        if valid is None or handle is None:
            return None
        return MessageRetractionReturn(
            bool(valid),
            self.from_backend(handle, expected_type_name="MessageRetractionHandle"),
        )

    def _from_backend_federate_handle_save_status_pair(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> FederateHandleSaveStatusPair | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederateHandleSaveStatusPair" not in class_text:
            return None

        handle = self.bridge.public_field(value, "handle")
        if handle is None:
            handle = self.bridge.public_field(value, "federateHandle")
        if handle is None:
            handle = _maybe_call_noarg(value, "getHandle", "getFederateHandle")
        status = self.bridge.public_field(value, "status")
        if status is None:
            status = self.bridge.public_field(value, "saveStatus")
        if status is None:
            status = _maybe_call_noarg(value, "getStatus", "getSaveStatus")
        if handle is None or status is None:
            return None
        return FederateHandleSaveStatusPair(
            self.from_backend(handle, expected_type_name="FederateHandle"),
            self.from_backend(status),
        )

    def _from_backend_federate_restore_status(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> FederateRestoreStatus | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederateRestoreStatus" not in class_text:
            return None

        pre = self.bridge.public_field(value, "preRestoreHandle")
        if pre is None:
            pre = _maybe_call_noarg(value, "getPreRestoreHandle")
        post = self.bridge.public_field(value, "postRestoreHandle")
        if post is None:
            post = _maybe_call_noarg(value, "getPostRestoreHandle")
        status = self.bridge.public_field(value, "status")
        if status is None:
            status = self.bridge.public_field(value, "restoreStatus")
        if status is None:
            status = _maybe_call_noarg(value, "getStatus", "getRestoreStatus")
        if pre is None or post is None or status is None:
            return None
        return FederateRestoreStatus(
            self.from_backend(pre, expected_type_name="FederateHandle"),
            self.from_backend(post, expected_type_name="FederateHandle"),
            self.from_backend(status),
        )

    def _from_backend_supplemental_reflect_info(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
        info_type: type[SupplementalReflectInfo] = SupplementalReflectInfo,
    ) -> SupplementalReflectInfo | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if info_type.__name__ not in class_text:
            return None

        has_producing = _maybe_call_noarg(
            value,
            "hasProducingFederate",
            "getHasProducingFederate",
            "producingFederateIsValid",
            "getProducingFederateIsValid",
        )
        has_sent = _maybe_call_noarg(
            value,
            "hasSentRegions",
            "getHasSentRegions",
            "sentRegionsIsValid",
            "getSentRegionsIsValid",
            "conveyedRegionsIsValid",
            "getConveyedRegionsIsValid",
        )
        producing = self.bridge.public_field(value, "producingFederate")
        if producing is None:
            producing = _maybe_call_noarg(value, "getProducingFederate")
        sent_regions = self.bridge.public_field(value, "sentRegions")
        if sent_regions is None:
            sent_regions = self.bridge.public_field(value, "conveyedRegions")
        if sent_regions is None:
            sent_regions = _maybe_call_noarg(value, "getSentRegions", "getConveyedRegions")
        if has_producing is None:
            return None
        return info_type(
            hasProducingFederateValue=bool(has_producing),
            hasSentRegionsValue=bool(has_sent) if has_sent is not None else False,
            producingFederate=(
                self.from_backend(producing, expected_type_name="FederateHandle")
                if producing is not None else None
            ),
            sentRegions=(
                self.from_backend(sent_regions, expected_type_name="RegionHandleSet")
                if sent_regions is not None else None
            ),
        )

    def _from_backend_supplemental_remove_info(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> SupplementalRemoveInfo | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "SupplementalRemoveInfo" not in class_text:
            return None

        has_producing = _maybe_call_noarg(
            value,
            "hasProducingFederate",
            "getHasProducingFederate",
            "producingFederateIsValid",
            "getProducingFederateIsValid",
        )
        producing = self.bridge.public_field(value, "producingFederate")
        if producing is None:
            producing = _maybe_call_noarg(value, "getProducingFederate")
        if has_producing is None:
            return None
        return SupplementalRemoveInfo(
            hasProducingFederateValue=bool(has_producing),
            producingFederate=(
                self.from_backend(producing, expected_type_name="FederateHandle")
                if producing is not None else None
            ),
        )


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

_JAVA_COMPOSITE_DATATYPE_NAMES = {
    "FederateHandleSaveStatusPair",
    "FederateRestoreStatus",
    "FederationExecutionInformation",
    "MessageRetractionReturn",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "TimeQueryReturn",
}


def _clean_java_type(type_name: str | None) -> str | None:
    return clean_java_type_name(type_name)


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

    def __init__(self, ambassador: NullFederateAmbassador, converter: JavaValueConverter):
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


    def connectionLost(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("connectionLost", *args)

    def reportFederationExecutions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("reportFederationExecutions", *args)

    def synchronizationPointRegistrationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("synchronizationPointRegistrationSucceeded", *args)

    def synchronizationPointRegistrationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("synchronizationPointRegistrationFailed", *args)

    def announceSynchronizationPoint(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("announceSynchronizationPoint", *args)

    def federationSynchronized(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationSynchronized", *args)

    def initiateFederateSave(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("initiateFederateSave", *args)

    def federationSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationSaved", *args)

    def federationNotSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationNotSaved", *args)

    def federationSaveStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationSaveStatusResponse", *args)

    def requestFederationRestoreSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestFederationRestoreSucceeded", *args)

    def requestFederationRestoreFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestFederationRestoreFailed", *args)

    def federationRestoreBegun(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationRestoreBegun", *args)

    def initiateFederateRestore(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("initiateFederateRestore", *args)

    def federationRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationRestored", *args)

    def federationNotRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationNotRestored", *args)

    def federationRestoreStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("federationRestoreStatusResponse", *args)

    def startRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("startRegistrationForObjectClass", *args)

    def stopRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("stopRegistrationForObjectClass", *args)

    def turnInteractionsOn(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("turnInteractionsOn", *args)

    def turnInteractionsOff(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("turnInteractionsOff", *args)

    def objectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("objectInstanceNameReservationSucceeded", *args)

    def objectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("objectInstanceNameReservationFailed", *args)

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("multipleObjectInstanceNameReservationSucceeded", *args)

    def multipleObjectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("multipleObjectInstanceNameReservationFailed", *args)

    def discoverObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("discoverObjectInstance", *args)

    def hasProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("hasProducingFederate", *args)

    def hasSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("hasSentRegions", *args)

    def getProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("getProducingFederate", *args)

    def getSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("getSentRegions", *args)

    def reflectAttributeValues(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("reflectAttributeValues", *args)

    def receiveInteraction(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("receiveInteraction", *args)

    def removeObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("removeObjectInstance", *args)

    def attributesInScope(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributesInScope", *args)

    def attributesOutOfScope(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributesOutOfScope", *args)

    def provideAttributeValueUpdate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("provideAttributeValueUpdate", *args)

    def turnUpdatesOnForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("turnUpdatesOnForObjectInstance", *args)

    def turnUpdatesOffForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("turnUpdatesOffForObjectInstance", *args)

    def confirmAttributeTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("confirmAttributeTransportationTypeChange", *args)

    def reportAttributeTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("reportAttributeTransportationType", *args)

    def confirmInteractionTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("confirmInteractionTransportationTypeChange", *args)

    def reportInteractionTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("reportInteractionTransportationType", *args)

    def requestAttributeOwnershipAssumption(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestAttributeOwnershipAssumption", *args)

    def requestDivestitureConfirmation(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestDivestitureConfirmation", *args)

    def attributeOwnershipAcquisitionNotification(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributeOwnershipAcquisitionNotification", *args)

    def attributeOwnershipUnavailable(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributeOwnershipUnavailable", *args)

    def requestAttributeOwnershipRelease(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestAttributeOwnershipRelease", *args)

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("confirmAttributeOwnershipAcquisitionCancellation", *args)

    def informAttributeOwnership(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("informAttributeOwnership", *args)

    def attributeIsNotOwned(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributeIsNotOwned", *args)

    def attributeIsOwnedByRTI(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("attributeIsOwnedByRTI", *args)

    def timeRegulationEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("timeRegulationEnabled", *args)

    def timeConstrainedEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("timeConstrainedEnabled", *args)

    def timeAdvanceGrant(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("timeAdvanceGrant", *args)

    def requestRetraction(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke_callback("requestRetraction", *args)


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
        self._connected_ambassador_proxies: list[tuple[NullFederateAmbassador, PythonFederateAmbassadorDispatcher, Any]] = []

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

    def adapt_federate_ambassador(self, ambassador: NullFederateAmbassador) -> Any:
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
