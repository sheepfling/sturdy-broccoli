"""HLA handle, handle set, and handle map abstract models.

Sources: Java handle interfaces and C++ RTI/Handle.h plus RTI/Typedefs.h.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, NamedTuple, Self, TypeVar


class HandleKind(ABC):
    @abstractmethod
    def __eq__(self, value: object) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @abstractmethod
    def encodedLength(self) -> int: ...

    @abstractmethod
    def encode(self, buffer: bytearray, offset: int) -> None: ...

    @abstractmethod
    def __str__(self) -> str: ...

    def toString(self) -> str:
        return str(self)

    def hash(self) -> int:
        return hash(self)

    def isValid(self) -> bool:
        """C++ handle affordance. Concrete RTIs may override invalid/null handles."""
        return True

    def __lt__(self, other: Self) -> bool:
        return str(self) < str(other)


T = TypeVar("T", bound=HandleKind)


@dataclass(frozen=True, order=True)
class _IntegerHandle(HandleKind):
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"{type(self).__name__} value must be an integer")
        if self.value < 0:
            raise ValueError(f"{type(self).__name__} value must be non-negative")

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = int(self.value).to_bytes(self.encodedLength(), byteorder="big", signed=False)
        if buffer is None:
            return data
        buffer[offset : offset + len(data)] = data
        return buffer

    def encoded(self) -> bytes:
        return self.encode()  # type: ignore[return-value]

    def toInt(self) -> int:
        return self.value

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.value})"

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> Self:
        raw = bytes(data[offset : offset + 8])
        if len(raw) != 8:
            raise ValueError(f"Need 8 bytes to decode {cls.__name__}; got {len(raw)}")
        return cls(int.from_bytes(raw, byteorder="big", signed=False))


class FederateHandle(_IntegerHandle): ...


class ObjectClassHandle(_IntegerHandle): ...


class InteractionClassHandle(_IntegerHandle): ...


class ObjectInstanceHandle(_IntegerHandle): ...


class AttributeHandle(_IntegerHandle): ...


class ParameterHandle(_IntegerHandle): ...


class DimensionHandle(_IntegerHandle): ...


class MessageRetractionHandle(_IntegerHandle): ...


class RegionHandle(_IntegerHandle): ...


class TransportationTypeHandle(_IntegerHandle): ...


class HandleSet(Generic[T], set[T], ABC):
    @abstractmethod
    def clone(self) -> Self: ...

    def _validate(self, value: Any) -> T:
        return value


class AttributeHandleSet(HandleSet[AttributeHandle], ABC): ...


class InteractionClassHandleSet(HandleSet[InteractionClassHandle], ABC): ...


class ParameterHandleSet(HandleSet[ParameterHandle], ABC): ...


class FederateHandleSet(HandleSet[FederateHandle], ABC): ...


class DimensionHandleSet(HandleSet[DimensionHandle], ABC): ...


class RegionHandleSet(HandleSet[RegionHandle], ABC): ...


class HandleMap(Generic[T], Mapping[T, bytes], ABC):
    @abstractmethod
    def clone(self) -> Self: ...

    def getValueReference(self, handle: T) -> bytes:
        """C++ map affordance; for Python this aliases normal mapping access."""
        return self[handle]


class AttributeHandleValueMap(HandleMap[AttributeHandle], ABC): ...


class ParameterHandleValueMap(HandleMap[ParameterHandle], ABC): ...


class AttributeRegionAssociation(NamedTuple):
    ahset: AttributeHandleSet
    rhset: RegionHandleSet


class AttributeSetRegionSetPairList(list[AttributeRegionAssociation], ABC):
    @abstractmethod
    def clone(self) -> Self: ...
