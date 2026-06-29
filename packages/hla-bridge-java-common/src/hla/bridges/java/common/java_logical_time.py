"""Bridge-neutral Java logical-time factory and value adapters."""
from __future__ import annotations

from functools import total_ordering
from typing import Any, cast

from hla.backends.common import BackendConversionError


def _call_first(obj: Any, *names: str, args: tuple[Any, ...] = ()) -> Any:
    last_error: BaseException | None = None
    for name in names:
        method = getattr(obj, name, None)
        if callable(method):
            try:
                return method(*args)
            except BaseException as exc:
                last_error = exc
    if last_error is not None:
        raise last_error
    raise AttributeError(f"{type(obj).__name__} does not provide any of: {', '.join(names)}")


def _factory_name(factory: Any) -> str:
    return str(_call_first(factory, "getName", "get_name"))


def _local_time_factory(binding: Any, name: str) -> Any | None:
    getter = getattr(binding.time_module, "get_logical_time_factory", None)
    if callable(getter):
        try:
            return getter(name)
        except Exception:
            return None
    registry = getattr(binding.time_module, "DEFAULT_TIME_FACTORY_REGISTRY", None)
    get = getattr(registry, "get", None)
    if callable(get):
        try:
            return get(name)
        except Exception:
            return None
    return None


def _local_decode(factory: Any, data: bytes, *, is_interval: bool) -> Any:
    if is_interval:
        return _call_first(factory, "decodeInterval", "decode_interval", args=(data, 0))
    return _call_first(factory, "decodeTime", "decode_time", args=(data, 0))


def _coerce_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    raise BackendConversionError(f"Cannot coerce {type(value).__name__} to bytes")


def _encoded_length_value(value: Any) -> int:
    encoded_length = getattr(value, "encodedLength", None)
    if not callable(encoded_length):
        encoded_length = getattr(value, "encoded_length", None)
    if not callable(encoded_length):
        raise BackendConversionError(f"Cannot determine encoded length for {type(value).__name__}")
    return int(cast(Any, encoded_length)())


def python_logical_time_to_bytes(value: Any) -> bytes:
    to_byte_array = getattr(value, "toByteArray", None)
    if callable(to_byte_array):
        return _coerce_bytes(to_byte_array())

    encode = getattr(value, "encode", None)
    if not callable(encode):
        raise BackendConversionError(f"Cannot encode logical time value {type(value).__name__}")

    try:
        encoded = encode()
    except TypeError:
        buffer = bytearray(_encoded_length_value(value))
        result = encode(buffer, 0)
        encoded = buffer if result is None else result

    return _coerce_bytes(encoded)


def java_logical_time_to_bytes(bridge: Any, value: Any) -> bytes:
    to_byte_array = getattr(value, "toByteArray", None)
    if callable(to_byte_array):
        return _coerce_bytes(bridge.to_python_bytes(to_byte_array()))

    encode = getattr(value, "encode", None)
    if not callable(encode):
        raise BackendConversionError(f"Java logical time value {type(value).__name__} cannot be encoded")

    buffer = bridge.byte_array(bytes(_encoded_length_value(value)))
    encode(buffer, 0)
    return _coerce_bytes(bridge.to_python_bytes(buffer))


def _is_interval_type(value: Any) -> bool:
    return "Interval" in type(value).__name__


@total_ordering
class _JavaLogicalBase:
    def __init__(
        self,
        *,
        bridge: Any,
        factory: "JavaLogicalTimeFactoryAdapter",
        java_value: Any,
        encoded: bytes | None = None,
    ) -> None:
        self._bridge = bridge
        self._factory = factory
        self._java_value = java_value
        self._encoded = encoded

    @property
    def java_value(self) -> Any:
        return self._java_value

    @property
    def factory_name(self) -> str:
        return self._factory.getName()

    def encodedLength(self) -> int:  # noqa: N802
        if self._encoded is not None:
            return len(self._encoded)
        return int(_call_first(self._java_value, "encodedLength", "encoded_length"))

    def encoded_length(self) -> int:
        return self.encodedLength()

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray | None:
        data = self._encoded
        if data is None:
            data = java_logical_time_to_bytes(self._bridge, self._java_value)
            self._encoded = data
        if buffer is None:
            return data
        buffer[offset : offset + len(data)] = data
        return None

    def compareTo(self, other: Any) -> int:  # noqa: N802
        other_java = self._factory.to_java_value(other, is_interval=isinstance(self, JavaLogicalTimeIntervalAdapter))
        return int(_call_first(self._java_value, "compareTo", args=(other_java,)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _JavaLogicalBase):
            return False
        return self.compareTo(other) == 0

    def __lt__(self, other: Any) -> bool:
        return self.compareTo(other) < 0

    def __hash__(self) -> int:
        try:
            return int(_call_first(self._java_value, "hashCode"))
        except Exception:
            return hash((self.factory_name, self._encoded))

    def __str__(self) -> str:
        to_string = getattr(self._java_value, "toString", None)
        if callable(to_string):
            return str(to_string())
        return str(self._java_value)

    def toString(self) -> str:  # noqa: N802
        return str(self)


class JavaLogicalTimeAdapter(_JavaLogicalBase):
    def isInitial(self) -> bool:  # noqa: N802
        return bool(_call_first(self._java_value, "isInitial", "is_initial"))

    def isFinal(self) -> bool:  # noqa: N802
        return bool(_call_first(self._java_value, "isFinal", "is_final"))

    def is_initial(self) -> bool:
        return self.isInitial()

    def is_final(self) -> bool:
        return self.isFinal()

    def add(self, val: Any) -> Any:
        return self._factory.from_java_time(_call_first(self._java_value, "add", args=(self._factory.to_java_value(val, is_interval=True),)))

    def subtract(self, val: Any) -> Any:
        return self._factory.from_java_time(
            _call_first(self._java_value, "subtract", args=(self._factory.to_java_value(val, is_interval=True),))
        )

    def distance(self, val: Any) -> Any:
        return self._factory.from_java_interval(
            _call_first(self._java_value, "distance", args=(self._factory.to_java_value(val, is_interval=False),))
        )


class JavaLogicalTimeIntervalAdapter(_JavaLogicalBase):
    def isZero(self) -> bool:  # noqa: N802
        return bool(_call_first(self._java_value, "isZero", "is_zero"))

    def isEpsilon(self) -> bool:  # noqa: N802
        return bool(_call_first(self._java_value, "isEpsilon", "is_epsilon"))

    def is_zero(self) -> bool:
        return self.isZero()

    def is_epsilon(self) -> bool:
        return self.isEpsilon()

    def add(self, addend: Any) -> Any:
        return self._factory.from_java_interval(
            _call_first(self._java_value, "add", args=(self._factory.to_java_value(addend, is_interval=True),))
        )

    def subtract(self, subtrahend: Any) -> Any:
        return self._factory.from_java_interval(
            _call_first(self._java_value, "subtract", args=(self._factory.to_java_value(subtrahend, is_interval=True),))
        )


class JavaLogicalTimeFactoryAdapter:
    """Python LogicalTimeFactory facade around a Java LogicalTimeFactory."""

    def __init__(self, *, bridge: Any, java_factory: Any, binding: Any) -> None:
        self.bridge = bridge
        self.java_factory = java_factory
        self.binding = binding
        self._name: str | None = None
        self._local_factory: Any | None | bool = False

    @property
    def name(self) -> str:
        return self.getName()

    def getName(self) -> str:  # noqa: N802
        if self._name is None:
            self._name = _factory_name(self.java_factory)
        return self._name

    def get_name(self) -> str:
        return self.getName()

    @property
    def local_factory(self) -> Any | None:
        if self._local_factory is False:
            self._local_factory = _local_time_factory(self.binding, self.getName())
        return self._local_factory or None

    def _decode_java(self, data: bytes, *, is_interval: bool) -> Any:
        method_name = "decodeInterval" if is_interval else "decodeTime"
        return self.bridge.call(self.java_factory, method_name, self.bridge.byte_array(data), 0)

    def _wrap_java_value(self, java_value: Any, *, is_interval: bool, encoded: bytes | None = None) -> Any:
        local = self.local_factory
        if local is not None:
            if encoded is None:
                try:
                    encoded = java_logical_time_to_bytes(self.bridge, java_value)
                except Exception:
                    encoded = None
            if encoded is not None:
                try:
                    return _local_decode(local, encoded, is_interval=is_interval)
                except Exception:
                    pass
            try:
                raw = _call_first(java_value, "getValue", "value", "longValue", "doubleValue")
                method_names = ("makeInterval", "make_interval") if is_interval else ("makeTime", "make_time")
                return _call_first(local, *method_names, args=(raw,))
            except Exception:
                pass
        wrapper_cls = JavaLogicalTimeIntervalAdapter if is_interval else JavaLogicalTimeAdapter
        return wrapper_cls(bridge=self.bridge, factory=self, java_value=java_value, encoded=encoded)

    def from_java_time(self, java_value: Any) -> Any:
        return self._wrap_java_value(java_value, is_interval=False)

    def from_java_interval(self, java_value: Any) -> Any:
        return self._wrap_java_value(java_value, is_interval=True)

    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> Any:  # noqa: N802
        data = bytes(buffer[offset:])
        local = self.local_factory
        if local is not None:
            try:
                return _local_decode(local, data, is_interval=False)
            except Exception:
                pass
        return self._wrap_java_value(self._decode_java(data, is_interval=False), is_interval=False, encoded=data)

    def decode_time(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> Any:
        return self.decodeTime(buffer, offset)

    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> Any:  # noqa: N802
        data = bytes(buffer[offset:])
        local = self.local_factory
        if local is not None:
            try:
                return _local_decode(local, data, is_interval=True)
            except Exception:
                pass
        return self._wrap_java_value(self._decode_java(data, is_interval=True), is_interval=True, encoded=data)

    def decode_interval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> Any:
        return self.decodeInterval(buffer, offset)

    def makeInitial(self) -> Any:  # noqa: N802
        return self.from_java_time(self.bridge.call(self.java_factory, "makeInitial"))

    def make_initial(self) -> Any:
        return self.makeInitial()

    def makeFinal(self) -> Any:  # noqa: N802
        return self.from_java_time(self.bridge.call(self.java_factory, "makeFinal"))

    def make_final(self) -> Any:
        return self.makeFinal()

    def makeZero(self) -> Any:  # noqa: N802
        return self.from_java_interval(self.bridge.call(self.java_factory, "makeZero"))

    def make_zero(self) -> Any:
        return self.makeZero()

    def makeEpsilon(self) -> Any:  # noqa: N802
        return self.from_java_interval(self.bridge.call(self.java_factory, "makeEpsilon"))

    def make_epsilon(self) -> Any:
        return self.makeEpsilon()

    def makeTime(self, value: Any) -> Any:  # noqa: N802
        return self.from_java_time(self.bridge.call(self.java_factory, "makeTime", value))

    def make_time(self, value: Any) -> Any:
        return self.makeTime(value)

    def makeInterval(self, value: Any) -> Any:  # noqa: N802
        return self.from_java_interval(self.bridge.call(self.java_factory, "makeInterval", value))

    def make_interval(self, value: Any) -> Any:
        return self.makeInterval(value)

    def coerce_time(self, value: Any) -> Any:
        if isinstance(value, JavaLogicalTimeAdapter) and value.factory_name == self.getName():
            return value
        if isinstance(value, (bytes, bytearray, memoryview)):
            return self.decodeTime(value)
        return self.decodeTime(python_logical_time_to_bytes(value))

    def coerce_interval(self, value: Any) -> Any:
        if isinstance(value, JavaLogicalTimeIntervalAdapter) and value.factory_name == self.getName():
            return value
        if isinstance(value, (bytes, bytearray, memoryview)):
            return self.decodeInterval(value)
        return self.decodeInterval(python_logical_time_to_bytes(value))

    def to_java_value(self, value: Any, *, is_interval: bool | None = None) -> Any:
        if isinstance(value, _JavaLogicalBase):
            return value.java_value
        if is_interval is None:
            is_interval = _is_interval_type(value)
        return self._decode_java(python_logical_time_to_bytes(value), is_interval=is_interval)


def wrap_java_logical_time_factory(bridge: Any, java_factory: Any, binding: Any) -> JavaLogicalTimeFactoryAdapter:
    return JavaLogicalTimeFactoryAdapter(bridge=bridge, java_factory=java_factory, binding=binding)


__all__ = [
    "JavaLogicalTimeAdapter",
    "JavaLogicalTimeFactoryAdapter",
    "JavaLogicalTimeIntervalAdapter",
    "java_logical_time_to_bytes",
    "python_logical_time_to_bytes",
    "wrap_java_logical_time_factory",
]
