"""Logical time and logical time interval abstractions for IEEE 1516.1-2025.

Sources: Java hla/rti1516_2025/time/*.java and C++ RTI/time/*.h.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Generic, Literal, Protocol, TypeVar, runtime_checkable

from typing_extensions import Self

T = TypeVar("T", bound="LogicalTime")
U = TypeVar("U", bound="LogicalTimeInterval")


@total_ordering
class LogicalTimeInterval(ABC):
    @abstractmethod
    def isZero(self) -> bool: ...

    @abstractmethod
    def isEpsilon(self) -> bool: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __iadd__(self, addend: Self) -> Self: ...

    @abstractmethod
    def __isub__(self, subtrahend: Self) -> Self: ...

    @abstractmethod
    def __lt__(self, other: Self) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def add(self, addend: Self) -> Self: ...

    @abstractmethod
    def subtract(self, subtrahend: Self) -> Self: ...

    @abstractmethod
    def compareTo(self, other: Self) -> int: ...

    def equals(self, other: object) -> bool:
        return self == other

    def hashCode(self) -> int:
        return hash(self)

    def toString(self) -> str:
        return str(self)

    @abstractmethod
    def encodedLength(self) -> int: ...

    @abstractmethod
    def encode(self, buffer: bytearray, offset: int) -> None: ...


@total_ordering
class LogicalTime(Generic[U], ABC):
    @abstractmethod
    def isInitial(self) -> bool: ...

    @abstractmethod
    def isFinal(self) -> bool: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __iadd__(self, val: U) -> Self: ...

    @abstractmethod
    def __isub__(self, val: U) -> Self: ...

    @abstractmethod
    def __sub__(self, other: Self) -> U: ...

    @abstractmethod
    def __lt__(self, other: Self) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def add(self, val: U) -> Self: ...

    @abstractmethod
    def subtract(self, val: U) -> Self: ...

    @abstractmethod
    def distance(self, val: Self) -> U: ...

    @abstractmethod
    def compareTo(self, other: Self) -> int: ...

    def equals(self, other: object) -> bool:
        return self == other

    def hashCode(self) -> int:
        return hash(self)

    def toString(self) -> str:
        return str(self)

    @abstractmethod
    def encodedLength(self) -> int: ...

    @abstractmethod
    def encode(self, buffer: bytearray, offset: int) -> None: ...


class HLAinteger64Interval(LogicalTimeInterval, ABC):
    @abstractmethod
    def getValue(self) -> int: ...

    def __int__(self) -> int:
        return self.getValue()


class HLAfloat64Interval(LogicalTimeInterval, ABC):
    @abstractmethod
    def getValue(self) -> float: ...

    def __float__(self) -> float:
        return self.getValue()


class HLAinteger64Time(LogicalTime[HLAinteger64Interval], ABC):
    @abstractmethod
    def getValue(self) -> int: ...

    def __int__(self) -> int:
        return self.getValue()


class HLAfloat64Time(LogicalTime[HLAfloat64Interval], ABC):
    @abstractmethod
    def getValue(self) -> float: ...

    def __float__(self) -> float:
        return self.getValue()


class LogicalTimeFactory(Generic[T, U], ABC):
    @abstractmethod
    def decodeTime(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> T: ...

    @abstractmethod
    def decodeInterval(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> U: ...

    @abstractmethod
    def makeInitial(self) -> T: ...

    @abstractmethod
    def makeFinal(self) -> T: ...

    @abstractmethod
    def makeZero(self) -> U: ...

    @abstractmethod
    def makeEpsilon(self) -> U: ...

    @abstractmethod
    def getName(self) -> str: ...


class HLAinteger64TimeFactory(
    LogicalTimeFactory[HLAinteger64Time, HLAinteger64Interval], ABC
):
    NAME: Literal["HLAinteger64Time"]

    @abstractmethod
    def makeTime(self, value: int) -> HLAinteger64Time: ...

    @abstractmethod
    def makeInterval(self, value: int) -> HLAinteger64Interval: ...


class HLAfloat64TimeFactory(
    LogicalTimeFactory[HLAfloat64Time, HLAfloat64Interval], ABC
):
    NAME: Literal["HLAfloat64Time"]

    @abstractmethod
    def makeTime(self, value: float) -> HLAfloat64Time: ...

    @abstractmethod
    def makeInterval(self, value: float) -> HLAfloat64Interval: ...


@runtime_checkable
class LogicalTimeFactoryFactory(Protocol):
    @staticmethod
    def getLogicalTimeFactory(name: str) -> LogicalTimeFactory: ...


# C++ spelling alias.
HLAlogicalTimeFactoryFactory = LogicalTimeFactoryFactory


class TimeQueryReturn(ABC):
    @property
    @abstractmethod
    def timeIsValid(self) -> bool: ...

    @property
    @abstractmethod
    def time(self) -> LogicalTime: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...
