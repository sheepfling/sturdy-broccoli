"""Concrete logical time helpers for IEEE 1516.1-2025.

The 2025 Python package exposes abstract logical-time interfaces in
``logical_time.py``.  This module provides the runtime value types and factory
implementations used by the Python shim and adapter layers.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from typing import Any, cast

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
    LogicalTime as LogicalTimeBase,
)
from .logical_time import (
    LogicalTimeFactory,
)
from .logical_time import (
    LogicalTimeInterval as LogicalTimeIntervalBase,
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

    def __iadd__(self, addend: LogicalTimeIntervalBase) -> "HLAinteger64Interval":
        return self.add(addend)

    def __isub__(self, subtrahend: LogicalTimeIntervalBase) -> "HLAinteger64Interval":
        return self.subtract(subtrahend)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, addend: LogicalTimeIntervalBase) -> "HLAinteger64Interval":
        other = cast(HLAinteger64IntervalBase, addend)
        return HLAinteger64Interval(self.value + other.getValue())

    def subtract(self, subtrahend: LogicalTimeIntervalBase) -> "HLAinteger64Interval":
        other = cast(HLAinteger64IntervalBase, subtrahend)
        return HLAinteger64Interval(self.value - other.getValue())

    def compareTo(self, other: LogicalTimeIntervalBase) -> int:
        other_value = cast(HLAinteger64IntervalBase, other).getValue()
        return (self.value > other_value) - (self.value < other_value)

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

    def __iadd__(self, val: HLAinteger64IntervalBase) -> "HLAinteger64Time":
        return self.add(val)

    def __isub__(self, val: HLAinteger64IntervalBase) -> "HLAinteger64Time":
        return self.subtract(val)

    def __sub__(self, other: LogicalTimeBase[HLAinteger64IntervalBase]) -> HLAinteger64Interval:
        return self.distance(other)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, val: HLAinteger64IntervalBase) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value + val.getValue())

    def subtract(self, val: HLAinteger64IntervalBase) -> "HLAinteger64Time":
        return HLAinteger64Time(self.value - val.getValue())

    def distance(self, val: LogicalTimeBase[HLAinteger64IntervalBase]) -> HLAinteger64Interval:
        other = cast(HLAinteger64TimeBase, val)
        return HLAinteger64Interval(self.value - other.getValue())

    def compareTo(self, other: LogicalTimeBase[HLAinteger64IntervalBase]) -> int:
        other_value = cast(HLAinteger64TimeBase, other).getValue()
        return (self.value > other_value) - (self.value < other_value)

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

    def __iadd__(self, addend: LogicalTimeIntervalBase) -> "HLAfloat64Interval":
        return self.add(addend)

    def __isub__(self, subtrahend: LogicalTimeIntervalBase) -> "HLAfloat64Interval":
        return self.subtract(subtrahend)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, addend: LogicalTimeIntervalBase) -> "HLAfloat64Interval":
        other = cast(HLAfloat64IntervalBase, addend)
        return HLAfloat64Interval(self.value + other.getValue())

    def subtract(self, subtrahend: LogicalTimeIntervalBase) -> "HLAfloat64Interval":
        other = cast(HLAfloat64IntervalBase, subtrahend)
        return HLAfloat64Interval(self.value - other.getValue())

    def compareTo(self, other: LogicalTimeIntervalBase) -> int:
        other_value = cast(HLAfloat64IntervalBase, other).getValue()
        return (self.value > other_value) - (self.value < other_value)

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

    def __iadd__(self, val: HLAfloat64IntervalBase) -> "HLAfloat64Time":
        return self.add(val)

    def __isub__(self, val: HLAfloat64IntervalBase) -> "HLAfloat64Time":
        return self.subtract(val)

    def __sub__(self, other: LogicalTimeBase[HLAfloat64IntervalBase]) -> HLAfloat64Interval:
        return self.distance(other)

    def __str__(self) -> str:
        return str(self.value)

    def add(self, val: HLAfloat64IntervalBase) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value + val.getValue())

    def subtract(self, val: HLAfloat64IntervalBase) -> "HLAfloat64Time":
        return HLAfloat64Time(self.value - val.getValue())

    def distance(self, val: LogicalTimeBase[HLAfloat64IntervalBase]) -> HLAfloat64Interval:
        other = cast(HLAfloat64TimeBase, val)
        return HLAfloat64Interval(self.value - other.getValue())

    def compareTo(self, other: LogicalTimeBase[HLAfloat64IntervalBase]) -> int:
        other_value = cast(HLAfloat64TimeBase, other).getValue()
        return (self.value > other_value) - (self.value < other_value)

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        buffer[offset : offset + 8] = struct.pack(">d", float(self.value))

    def toByteArray(self) -> bytes:
        return struct.pack(">d", float(self.value))

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "HLAfloat64Time":
        return cls(struct.unpack(">d", bytes(data[offset : offset + 8]))[0])


class HLAinteger64TimeFactory(HLAinteger64TimeFactoryBase):
    NAME = "HLAinteger64Time"
    name = NAME
    time_type = HLAinteger64Time
    interval_type = HLAinteger64Interval

    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> HLAinteger64Time:
        return self.time_type.decode(buffer, offset)

    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> HLAinteger64Interval:
        return self.interval_type.decode(buffer, offset)

    def getName(self) -> str:
        return self.name

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


class HLAfloat64TimeFactory(HLAfloat64TimeFactoryBase):
    NAME = "HLAfloat64Time"
    name = NAME
    time_type = HLAfloat64Time
    interval_type = HLAfloat64Interval

    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> HLAfloat64Time:
        return self.time_type.decode(buffer, offset)

    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> HLAfloat64Interval:
        return self.interval_type.decode(buffer, offset)

    def getName(self) -> str:
        return self.name

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
