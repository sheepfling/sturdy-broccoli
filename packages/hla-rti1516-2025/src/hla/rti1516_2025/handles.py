"""HLA handle, handle set, and handle map abstract models.

Sources: Java handle interfaces and C++ RTI/Handle.h plus RTI/Typedefs.h.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import Parameter, Signature
from typing import Any, cast
from typing import Any, Generic, Mapping, NamedTuple, TypeVar, cast
from typing_extensions import Self


class HandleKind(ABC):
    @abstractmethod
    def __eq__(self, value: object) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @abstractmethod
    def encodedLength(self) -> int: ...

    @abstractmethod
    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> Self: ...

    def toString(self) -> str:
        return str(self)

    def hash(self) -> int:
        return hash(self)

    def isValid(self) -> bool:
        """C++ handle affordance. Concrete RTIs may override invalid/null handles."""
        return True

    def __lt__(self, other: Self) -> bool:
        return str(self) < str(other)


THandle = TypeVar("THandle", bound=HandleKind)
TCollection = TypeVar("TCollection")


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


class HandleSet(Generic[THandle], set[THandle], ABC):
    @abstractmethod
    def clone(self) -> Self: ...

    def _validate(self, value: Any) -> THandle:
        return value


class AttributeHandleSet(HandleSet[AttributeHandle], ABC): ...


class InteractionClassHandleSet(HandleSet[InteractionClassHandle], ABC): ...


class ParameterHandleSet(HandleSet[ParameterHandle], ABC): ...


class FederateHandleSet(HandleSet[FederateHandle], ABC): ...


class DimensionHandleSet(HandleSet[DimensionHandle], ABC): ...


class RegionHandleSet(HandleSet[RegionHandle], ABC): ...


class HandleMap(Generic[THandle], Mapping[THandle, bytes], ABC):
    @abstractmethod
    def clone(self) -> Self: ...

    def getValueReference(self, handle: THandle) -> bytes:
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


class HandleFactory(Generic[THandle]):
    """Factory for decoding a specific 2025 handle type."""

    def __init__(self, handle_type: type[THandle]):
        self.handle_type = handle_type

    def decode(self, data: bytes | bytearray | memoryview, offset: int = 0) -> THandle:
        return self.handle_type.decode(data, offset)

    def make(self, value: int) -> THandle:
        return cast(THandle, cast(Any, self.handle_type)(value))


class CollectionFactory(Generic[TCollection]):
    """Small Java-style collection factory with a ``create`` helper."""

    def __init__(self, collection_type: type[Any]):
        self.collection_type = collection_type

    def create(self, capacity: int | None = None) -> Any:
        return self.collection_type()


class FederateHandleFactory(HandleFactory[FederateHandle]):
    def __init__(self) -> None:
        super().__init__(FederateHandle)


class ObjectClassHandleFactory(HandleFactory[ObjectClassHandle]):
    def __init__(self) -> None:
        super().__init__(ObjectClassHandle)


class InteractionClassHandleFactory(HandleFactory[InteractionClassHandle]):
    def __init__(self) -> None:
        super().__init__(InteractionClassHandle)


class ObjectInstanceHandleFactory(HandleFactory[ObjectInstanceHandle]):
    def __init__(self) -> None:
        super().__init__(ObjectInstanceHandle)


class AttributeHandleFactory(HandleFactory[AttributeHandle]):
    def __init__(self) -> None:
        super().__init__(AttributeHandle)


class ParameterHandleFactory(HandleFactory[ParameterHandle]):
    def __init__(self) -> None:
        super().__init__(ParameterHandle)


class DimensionHandleFactory(HandleFactory[DimensionHandle]):
    def __init__(self) -> None:
        super().__init__(DimensionHandle)


class MessageRetractionHandleFactory(HandleFactory[MessageRetractionHandle]):
    def __init__(self) -> None:
        super().__init__(MessageRetractionHandle)


class RegionHandleFactory(HandleFactory[RegionHandle]):
    def __init__(self) -> None:
        super().__init__(RegionHandle)


class TransportationTypeHandleFactory(HandleFactory[TransportationTypeHandle]):
    def __init__(self) -> None:
        super().__init__(TransportationTypeHandle)


class AttributeHandleSetFactory(CollectionFactory[AttributeHandleSet]):
    def __init__(self) -> None:
        super().__init__(AttributeHandleSet)


class DimensionHandleSetFactory(CollectionFactory[DimensionHandleSet]):
    def __init__(self) -> None:
        super().__init__(DimensionHandleSet)


class FederateHandleSetFactory(CollectionFactory[FederateHandleSet]):
    def __init__(self) -> None:
        super().__init__(FederateHandleSet)


class InteractionClassHandleSetFactory(CollectionFactory[InteractionClassHandleSet]):
    def __init__(self) -> None:
        super().__init__(InteractionClassHandleSet)


class RegionHandleSetFactory(CollectionFactory[RegionHandleSet]):
    def __init__(self) -> None:
        super().__init__(RegionHandleSet)


class AttributeHandleValueMapFactory(CollectionFactory[AttributeHandleValueMap]):
    def __init__(self) -> None:
        super().__init__(AttributeHandleValueMap)


class ParameterHandleValueMapFactory(CollectionFactory[ParameterHandleValueMap]):
    def __init__(self) -> None:
        super().__init__(ParameterHandleValueMap)


class AttributeSetRegionSetPairListFactory(CollectionFactory[AttributeSetRegionSetPairList]):
    def __init__(self) -> None:
        super().__init__(AttributeSetRegionSetPairList)


_HANDLE_ENCODE_SIGNATURE = Signature(
    parameters=(
        Parameter("self", kind=Parameter.POSITIONAL_OR_KEYWORD),
        Parameter("buffer", kind=Parameter.POSITIONAL_OR_KEYWORD),
        Parameter("offset", kind=Parameter.POSITIONAL_OR_KEYWORD),
    )
)
cast(Any, HandleKind.encode).__signature__ = _HANDLE_ENCODE_SIGNATURE
cast(Any, _IntegerHandle.encode).__signature__ = _HANDLE_ENCODE_SIGNATURE
