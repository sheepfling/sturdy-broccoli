"""Logical time support for the HLA 1516.1-2010 Python binding.

The 1516.1 Java API exposes a ``LogicalTimeFactory`` via the RTI ambassador.
This module mirrors that pattern for the pure Python RTI and gives the Java
adapters a single Python value model to convert from.

"""
from __future__ import annotations
# pyright: reportInvalidTypeVarUse=false

import math
import struct
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

class LogicalTimeInterval(Protocol):
    def is_zero(self) -> bool: ...
    def is_epsilon(self) -> bool: ...
    def add(self, addend: Any): ...
    def subtract(self, subtrahend: Any): ...
    def encoded_length(self) -> int: ...
    def encode(self, buffer: bytearray | None = None, offset: int = 0): ...

TInterval = TypeVar("TInterval", bound=LogicalTimeInterval)

class LogicalTime(Protocol[TInterval]):
    def is_initial(self) -> bool: ...
    def is_final(self) -> bool: ...
    def add(self, val: TInterval): ...
    def subtract(self, val: TInterval): ...
    def distance(self, val: Any): ...
    def encoded_length(self) -> int: ...
    def encode(self, buffer: bytearray | None = None, offset: int = 0): ...

@dataclass(frozen=True, order=True)
class HLAinteger64Interval:
    value: int = 0

    def is_zero(self) -> bool:
        return self.value == 0

    def is_epsilon(self) -> bool:
        return self.value == 1

    def add(self, addend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return HLAinteger64Interval(self.value + addend.value)

    def subtract(self, subtrahend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return HLAinteger64Interval(self.value - subtrahend.value)

    def encoded_length(self) -> int:
        return 8

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = struct.pack(">q", int(self.value))
        if buffer is None:
            return data
        buffer[offset : offset + 8] = data
        return buffer

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAinteger64Interval":
        return cls(struct.unpack(">q", bytes(data[offset : offset + 8]))[0])

@dataclass(frozen=True, order=True)
class HLAinteger64Time:
    value: int = 0

    INITIAL: int = 0
    FINAL: int = 2**63 - 1

    def is_initial(self) -> bool:
        return self.value == self.INITIAL

    def is_final(self) -> bool:
        return self.value == self.FINAL

    def add(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value + val.value)

    def subtract(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value - val.value)

    def distance(self, val: "HLAinteger64Time") -> HLAinteger64Interval:
        return HLAinteger64Interval(self.value - val.value)

    def encoded_length(self) -> int:
        return 8

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = struct.pack(">q", int(self.value))
        if buffer is None:
            return data
        buffer[offset : offset + 8] = data
        return buffer

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAinteger64Time":
        return cls(struct.unpack(">q", bytes(data[offset : offset + 8]))[0])

@dataclass(frozen=True, order=True)
class HLAfloat64Interval:
    value: float = 0.0

    def is_zero(self) -> bool:
        return self.value == 0.0

    def is_epsilon(self) -> bool:
        return self.value == math.ulp(1.0)

    def add(self, addend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return HLAfloat64Interval(self.value + addend.value)

    def subtract(self, subtrahend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return HLAfloat64Interval(self.value - subtrahend.value)

    def encoded_length(self) -> int:
        return 8

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = struct.pack(">d", float(self.value))
        if buffer is None:
            return data
        buffer[offset : offset + 8] = data
        return buffer

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAfloat64Interval":
        return cls(struct.unpack(">d", bytes(data[offset : offset + 8]))[0])

@dataclass(frozen=True, order=True)
class HLAfloat64Time:
    value: float = 0.0

    def is_initial(self) -> bool:
        return self.value == 0.0

    def is_final(self) -> bool:
        return math.isinf(self.value) and self.value > 0

    def add(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value + val.value)

    def subtract(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value - val.value)

    def distance(self, val: "HLAfloat64Time") -> HLAfloat64Interval:
        return HLAfloat64Interval(self.value - val.value)

    def encoded_length(self) -> int:
        return 8

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = struct.pack(">d", float(self.value))
        if buffer is None:
            return data
        buffer[offset : offset + 8] = data
        return buffer

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAfloat64Time":
        return cls(struct.unpack(">d", bytes(data[offset : offset + 8]))[0])

TTime = TypeVar("TTime")
TIntervalConcrete = TypeVar("TIntervalConcrete")

class LogicalTimeFactory(Generic[TTime, TIntervalConcrete]):
    """Base class for Python logical-time factories."""

    name: str
    time_type: type[Any]
    interval_type: type[Any]

    def get_name(self) -> str:
        return self.name

    def getName(self) -> str:  # noqa: N802 - Java API spelling
        return self.get_name()

    def decode_time(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TTime:
        return self.time_type.decode(buffer, offset)

    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TTime:  # noqa: N802
        return self.decode_time(buffer, offset)

    def decode_interval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TIntervalConcrete:
        return self.interval_type.decode(buffer, offset)

    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TIntervalConcrete:  # noqa: N802
        return self.decode_interval(buffer, offset)

    def make_initial(self) -> TTime:
        raise NotImplementedError

    def makeInitial(self) -> TTime:  # noqa: N802
        return self.make_initial()

    def make_final(self) -> TTime:
        raise NotImplementedError

    def makeFinal(self) -> TTime:  # noqa: N802
        return self.make_final()

    def make_zero(self) -> TIntervalConcrete:
        raise NotImplementedError

    def makeZero(self) -> TIntervalConcrete:  # noqa: N802
        return self.make_zero()

    def make_epsilon(self) -> TIntervalConcrete:
        raise NotImplementedError

    def makeEpsilon(self) -> TIntervalConcrete:  # noqa: N802
        return self.make_epsilon()

    def make_time(self, value: Any) -> TTime:
        raise NotImplementedError

    def makeTime(self, value: Any) -> TTime:  # noqa: N802
        return self.make_time(value)

    def make_interval(self, value: Any) -> TIntervalConcrete:
        raise NotImplementedError

    def makeInterval(self, value: Any) -> TIntervalConcrete:  # noqa: N802
        return self.make_interval(value)

    def coerce_time(self, value: Any) -> TTime:
        if isinstance(value, self.time_type):
            return value
        if hasattr(value, "value"):
            value = value.value
        return self.make_time(value)

    def coerce_interval(self, value: Any) -> TIntervalConcrete:
        if isinstance(value, self.interval_type):
            return value
        if hasattr(value, "value"):
            value = value.value
        return self.make_interval(value)

class HLAinteger64TimeFactory(LogicalTimeFactory[HLAinteger64Time, HLAinteger64Interval]):
    NAME = "HLAinteger64Time"
    name = NAME
    time_type = HLAinteger64Time
    interval_type = HLAinteger64Interval

    def make_initial(self) -> HLAinteger64Time:
        return HLAinteger64Time(HLAinteger64Time.INITIAL)

    def make_final(self) -> HLAinteger64Time:
        return HLAinteger64Time(HLAinteger64Time.FINAL)

    def make_zero(self) -> HLAinteger64Interval:
        return HLAinteger64Interval(0)

    def make_epsilon(self) -> HLAinteger64Interval:
        return HLAinteger64Interval(1)

    def make_time(self, value: Any) -> HLAinteger64Time:
        return HLAinteger64Time(int(value))

    def make_interval(self, value: Any) -> HLAinteger64Interval:
        return HLAinteger64Interval(int(value))

class HLAfloat64TimeFactory(LogicalTimeFactory[HLAfloat64Time, HLAfloat64Interval]):
    NAME = "HLAfloat64Time"
    name = NAME
    time_type = HLAfloat64Time
    interval_type = HLAfloat64Interval

    def make_initial(self) -> HLAfloat64Time:
        return HLAfloat64Time(0.0)

    def make_final(self) -> HLAfloat64Time:
        return HLAfloat64Time(float("inf"))

    def make_zero(self) -> HLAfloat64Interval:
        return HLAfloat64Interval(0.0)

    def make_epsilon(self) -> HLAfloat64Interval:
        return HLAfloat64Interval(math.ulp(1.0))

    def make_time(self, value: Any) -> HLAfloat64Time:
        return HLAfloat64Time(float(value))

    def make_interval(self, value: Any) -> HLAfloat64Interval:
        return HLAfloat64Interval(float(value))

class TimeFactoryRegistry:
    """Lookup table for logical-time implementations."""

    def __init__(self, factories: list[LogicalTimeFactory[Any, Any]] | tuple[LogicalTimeFactory[Any, Any], ...] | None = None):
        self._factories: dict[str, LogicalTimeFactory[Any, Any]] = {}
        for factory in factories or ():
            self.register(factory)

    def register(self, factory: LogicalTimeFactory[Any, Any]) -> None:
        self._factories[factory.get_name()] = factory

    def get(self, name: str | None) -> LogicalTimeFactory[Any, Any]:
        if not name:
            name = HLAinteger64TimeFactory.NAME
        try:
            return self._factories[str(name)]
        except KeyError as exc:
            known = ", ".join(sorted(self._factories))
            raise KeyError(f"Unknown logical time implementation {name!r}; known: {known}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))

    def __contains__(self, name: object) -> bool:
        return str(name) in self._factories

DEFAULT_TIME_FACTORY_REGISTRY = TimeFactoryRegistry(
    (HLAinteger64TimeFactory(), HLAfloat64TimeFactory())
)

def get_logical_time_factory(name: str | None = None) -> LogicalTimeFactory[Any, Any]:
    return DEFAULT_TIME_FACTORY_REGISTRY.get(name)

__all__ = [
    "LogicalTime",
    "LogicalTimeInterval",
    "LogicalTimeFactory",
    "TimeFactoryRegistry",
    "DEFAULT_TIME_FACTORY_REGISTRY",
    "get_logical_time_factory",
    "HLAinteger64Interval",
    "HLAinteger64Time",
    "HLAinteger64TimeFactory",
    "HLAfloat64Interval",
    "HLAfloat64Time",
    "HLAfloat64TimeFactory",
]
