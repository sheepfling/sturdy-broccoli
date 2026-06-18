"""Concrete logical time helpers for IEEE 1516.1-2025.

The 2025 Python package exposes abstract logical-time interfaces in
``logical_time.py``.  This module provides the runtime value types and factory
implementations used by the Python shim and adapter layers.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .logical_time import (
    HLAfloat64Interval as HLAfloat64IntervalBase,
)
from .logical_time import (
    HLAfloat64Time as HLAfloat64TimeBase,
)
from .logical_time import (
    HLAfloat64TimeFactory as HLAfloat64TimeFactoryBase,
)
from .logical_time import (
    HLAinteger64Interval as HLAinteger64IntervalBase,
)
from .logical_time import (
    HLAinteger64Time as HLAinteger64TimeBase,
)
from .logical_time import (
    HLAinteger64TimeFactory as HLAinteger64TimeFactoryBase,
)
from .logical_time import (
    LogicalTimeFactory,
)


@dataclass(frozen=True, order=True)
class HLAinteger64Interval(HLAinteger64IntervalBase):
    value: int = 0

    def getValue(self) -> int:
        return self.value

    def isZero(self) -> bool:
        return self.value == 0

    def isEpsilon(self) -> bool:
        return self.value == 1

    def __iadd__(self, addend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return self.add(addend)

    def __isub__(self, subtrahend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return self.subtract(subtrahend)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, addend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return HLAinteger64Interval(self.value + addend.value)

    def subtract(self, subtrahend: "HLAinteger64Interval") -> "HLAinteger64Interval":
        return HLAinteger64Interval(self.value - subtrahend.value)

    def compareTo(self, other: "HLAinteger64Interval") -> int:
        return (self.value > other.value) - (self.value < other.value)

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        buffer[offset : offset + 8] = struct.pack(">q", int(self.value))

    def toByteArray(self) -> bytes:
        return struct.pack(">q", int(self.value))

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAinteger64Interval":
        return cls(struct.unpack(">q", bytes(data[offset : offset + 8]))[0])


@dataclass(frozen=True, order=True)
class HLAinteger64Time(HLAinteger64TimeBase):
    value: int = 0

    INITIAL: int = 0
    FINAL: int = 2**63 - 1

    def getValue(self) -> int:
        return self.value

    def isInitial(self) -> bool:
        return self.value == self.INITIAL

    def isFinal(self) -> bool:
        return self.value == self.FINAL

    def __iadd__(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return self.add(val)

    def __isub__(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return self.subtract(val)

    def __sub__(self, other: "HLAinteger64Time") -> HLAinteger64Interval:
        return self.distance(other)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value + val.value)

    def subtract(self, val: HLAinteger64Interval) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value - val.value)

    def distance(self, val: "HLAinteger64Time") -> HLAinteger64Interval:
        return HLAinteger64Interval(self.value - val.value)

    def compareTo(self, other: "HLAinteger64Time") -> int:
        return (self.value > other.value) - (self.value < other.value)

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        buffer[offset : offset + 8] = struct.pack(">q", int(self.value))

    def toByteArray(self) -> bytes:
        return struct.pack(">q", int(self.value))

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAinteger64Time":
        return cls(struct.unpack(">q", bytes(data[offset : offset + 8]))[0])


@dataclass(frozen=True, order=True)
class HLAfloat64Interval(HLAfloat64IntervalBase):
    value: float = 0.0

    def getValue(self) -> float:
        return self.value

    def isZero(self) -> bool:
        return self.value == 0.0

    def isEpsilon(self) -> bool:
        return self.value == math.ulp(1.0)

    def __iadd__(self, addend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return self.add(addend)

    def __isub__(self, subtrahend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return self.subtract(subtrahend)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, addend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return HLAfloat64Interval(self.value + addend.value)

    def subtract(self, subtrahend: "HLAfloat64Interval") -> "HLAfloat64Interval":
        return HLAfloat64Interval(self.value - subtrahend.value)

    def compareTo(self, other: "HLAfloat64Interval") -> int:
        return (self.value > other.value) - (self.value < other.value)

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        buffer[offset : offset + 8] = struct.pack(">d", float(self.value))

    def toByteArray(self) -> bytes:
        return struct.pack(">d", float(self.value))

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAfloat64Interval":
        return cls(struct.unpack(">d", bytes(data[offset : offset + 8]))[0])


@dataclass(frozen=True, order=True)
class HLAfloat64Time(HLAfloat64TimeBase):
    value: float = 0.0

    def getValue(self) -> float:
        return self.value

    def isInitial(self) -> bool:
        return self.value == 0.0

    def isFinal(self) -> bool:
        return math.isinf(self.value) and self.value > 0

    def __iadd__(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return self.add(val)

    def __isub__(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return self.subtract(val)

    def __sub__(self, other: "HLAfloat64Time") -> HLAfloat64Interval:
        return self.distance(other)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value + val.value)

    def subtract(self, val: HLAfloat64Interval) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value - val.value)

    def distance(self, val: "HLAfloat64Time") -> HLAfloat64Interval:
        return HLAfloat64Interval(self.value - val.value)

    def compareTo(self, other: "HLAfloat64Time") -> int:
        return (self.value > other.value) - (self.value < other.value)

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        buffer[offset : offset + 8] = struct.pack(">d", float(self.value))

    def toByteArray(self) -> bytes:
        return struct.pack(">d", float(self.value))

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAfloat64Time":
        return cls(struct.unpack(">d", bytes(data[offset : offset + 8]))[0])


TTime = TypeVar("TTime")
TInterval = TypeVar("TInterval")


class _LogicalTimeFactory(Generic[TTime, TInterval], LogicalTimeFactory[TTime, TInterval]):
    name: str
    time_type: type[Any]
    interval_type: type[Any]

    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TTime:
        return self.time_type.decode(buffer, offset)

    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> TInterval:
        return self.interval_type.decode(buffer, offset)

    def getName(self) -> str:
        return self.name


class HLAinteger64TimeFactory(_LogicalTimeFactory[HLAinteger64Time, HLAinteger64Interval], HLAinteger64TimeFactoryBase):
    NAME = "HLAinteger64Time"
    name = NAME
    time_type = HLAinteger64Time
    interval_type = HLAinteger64Interval

    def makeInitial(self) -> HLAinteger64Time:
        return HLAinteger64Time(HLAinteger64Time.INITIAL)

    def makeFinal(self) -> HLAinteger64Time:
        return HLAinteger64Time(HLAinteger64Time.FINAL)

    def makeZero(self) -> HLAinteger64Interval:
        return HLAinteger64Interval(0)

    def makeEpsilon(self) -> HLAinteger64Interval:
        return HLAinteger64Interval(1)

    def makeTime(self, value: int) -> HLAinteger64Time:
        return HLAinteger64Time(int(value))

    def makeInterval(self, value: int) -> HLAinteger64Interval:
        return HLAinteger64Interval(int(value))


class HLAfloat64TimeFactory(_LogicalTimeFactory[HLAfloat64Time, HLAfloat64Interval], HLAfloat64TimeFactoryBase):
    NAME = "HLAfloat64Time"
    name = NAME
    time_type = HLAfloat64Time
    interval_type = HLAfloat64Interval

    def makeInitial(self) -> HLAfloat64Time:
        return HLAfloat64Time(0.0)

    def makeFinal(self) -> HLAfloat64Time:
        return HLAfloat64Time(float("inf"))

    def makeZero(self) -> HLAfloat64Interval:
        return HLAfloat64Interval(0.0)

    def makeEpsilon(self) -> HLAfloat64Interval:
        return HLAfloat64Interval(math.ulp(1.0))

    def makeTime(self, value: float) -> HLAfloat64Time:
        return HLAfloat64Time(float(value))

    def makeInterval(self, value: float) -> HLAfloat64Interval:
        return HLAfloat64Interval(float(value))


class TimeFactoryRegistry:
    def __init__(self, factories: tuple[LogicalTimeFactory[Any, Any], ...] | None = None):
        self._factories: dict[str, LogicalTimeFactory[Any, Any]] = {}
        for factory in factories or ():
            self.register(factory)

    def register(self, factory: LogicalTimeFactory[Any, Any]) -> None:
        self._factories[factory.getName()] = factory

    def get(self, name: str | None = None) -> LogicalTimeFactory[Any, Any]:
        lookup = name or HLAinteger64TimeFactory.NAME
        try:
            return self._factories[lookup]
        except KeyError as exc:
            known = ", ".join(sorted(self._factories))
            raise KeyError(f"Unknown logical time implementation {lookup!r}; known: {known}") from exc


DEFAULT_TIME_FACTORY_REGISTRY = TimeFactoryRegistry(
    (HLAinteger64TimeFactory(), HLAfloat64TimeFactory())
)


def get_logical_time_factory(name: str | None = None) -> LogicalTimeFactory[Any, Any]:
    return DEFAULT_TIME_FACTORY_REGISTRY.get(name)


__all__ = [
    "DEFAULT_TIME_FACTORY_REGISTRY",
    "HLAfloat64Interval",
    "HLAfloat64Time",
    "HLAfloat64TimeFactory",
    "HLAinteger64Interval",
    "HLAinteger64Time",
    "HLAinteger64TimeFactory",
    "TimeFactoryRegistry",
    "get_logical_time_factory",
]
