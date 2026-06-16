"""HLA handle, handle set, and handle map abstract models.

Sources: Java handle interfaces and C++ RTI/Handle.h plus RTI/Typedefs.h.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Mapping, NamedTuple, Self, TypeVar


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


class FederateHandle(HandleKind): ...


class ObjectClassHandle(HandleKind): ...


class InteractionClassHandle(HandleKind): ...


class ObjectInstanceHandle(HandleKind): ...


class AttributeHandle(HandleKind): ...


class ParameterHandle(HandleKind): ...


class DimensionHandle(HandleKind): ...


class MessageRetractionHandle(HandleKind): ...


class RegionHandle(HandleKind): ...


class TransportationTypeHandle(HandleKind): ...


class HandleSet(Generic[T], set[T], ABC):
    @abstractmethod
    def clone(self) -> Self: ...


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
