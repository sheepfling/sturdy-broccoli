"""Opaque handle value objects and typed handle collections for HLA 1516.1-2010.

The Java API exposes small factories for handle values, handle sets, and
handle-value maps.  This module mirrors that shape while staying Pythonic:
handles are frozen dataclasses, sets behave like ``set``, and value maps behave
like ``dict``.

"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Iterable, Mapping, TypeVar, cast


@dataclass(frozen=True, order=True)
class Handle:
    """Opaque, hashable handle.

    The integer value is adapter-local.  It is not meaningful outside the RTI or
    adapter instance that created it, but keeping it stable makes tests and local
    in-memory simulations deterministic.
    """

    value: int

    def encoded(self) -> bytes:
        return int(self.value).to_bytes(8, byteorder="big", signed=False)

    def encoded_length(self) -> int:
        return 8

    def encodedLength(self) -> int:  # noqa: N802 - standard API spelling
        return self.encoded_length()

    def encode(self, buffer: bytearray | None = None, offset: int = 0) -> bytes | bytearray:
        data = self.encoded()
        if buffer is None:
            return data
        buffer[offset : offset + len(data)] = data
        return buffer

    def equals(self, other: object) -> bool:
        return self == other

    def hashCode(self) -> int:  # noqa: N802 - standard API spelling
        return hash(self)

    def toString(self) -> str:  # noqa: N802 - standard API spelling
        return str(self)

    def isValid(self) -> bool:  # noqa: N802 - C++ handle affordance
        return True

    @classmethod
    def decode(cls, data: bytes | bytearray | memoryview, offset: int = 0) -> "Handle":
        raw = bytes(data[offset : offset + 8])
        if len(raw) != 8:
            raise ValueError(f"Need 8 bytes to decode {cls.__name__}; got {len(raw)}")
        return cls(int.from_bytes(raw, byteorder="big", signed=False))

THandle = TypeVar("THandle", bound=Handle)
TCollection = TypeVar("TCollection")

HandleKind = Handle

class HandleFactory(Generic[THandle]):
    """Factory for decoding a specific handle type."""

    def __init__(self, handle_type: type[THandle]):
        self.handle_type = handle_type

    def decode(self, data: bytes | bytearray | memoryview, offset: int = 0) -> THandle:
        return self.handle_type.decode(data, offset)  # type: ignore[return-value]

    def make(self, value: int) -> THandle:
        return self.handle_type(value)

@dataclass(frozen=True, order=True)
class AttributeHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class DimensionHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class FederateHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class InteractionClassHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class MessageRetractionHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class ObjectClassHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class ObjectInstanceHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class ParameterHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class RegionHandle(Handle):
    pass

@dataclass(frozen=True, order=True)
class TransportationTypeHandle(Handle):
    pass


def _coerce_compatible_handle(value: Any, expected_type: type[Handle]) -> Handle:
    if isinstance(value, expected_type):
        return value
    if type(value).__name__ == expected_type.__name__ and hasattr(value, "value"):
        raw_value = getattr(value, "value")
        if isinstance(raw_value, int):
            return expected_type(raw_value)
    raise TypeError(f"{expected_type.__name__} compatibility check failed for {type(value).__name__}")


class TypedHandleSet(set):
    """A ``set`` that enforces the handle type used by an HLA set interface."""

    handle_type: type[Handle] = Handle

    def __init__(self, values: Iterable[Handle] = ()) -> None:
        super().__init__()
        self.update(values)

    def _validate(self, value: Any) -> Handle:
        try:
            return _coerce_compatible_handle(value, self.handle_type)
        except TypeError as exc:
            raise TypeError(f"{type(self).__name__} only accepts {self.handle_type.__name__}; got {type(value).__name__}") from exc

    def add(self, value: Handle) -> None:  # type: ignore[override]
        super().add(self._validate(value))

    def update(self, *others: Iterable[Handle]) -> None:  # type: ignore[override]
        for other in others:
            for value in other:
                self.add(value)

    def clone(self):
        return type(self)(self)

HandleSet = TypedHandleSet

class AttributeHandleSet(TypedHandleSet):
    handle_type = AttributeHandle

class DimensionHandleSet(TypedHandleSet):
    handle_type = DimensionHandle

class FederateHandleSet(TypedHandleSet):
    handle_type = FederateHandle

class InteractionClassHandleSet(TypedHandleSet):
    handle_type = InteractionClassHandle

class RegionHandleSet(TypedHandleSet):
    handle_type = RegionHandle

class HandleValueMap(dict):
    """A dict-like handle-to-bytes map with Java-style helper names."""

    key_type: type[Handle] = Handle

    def __init__(self, initial: Mapping[Handle, bytes] | Iterable[tuple[Handle, bytes]] | None = None) -> None:
        super().__init__()
        if initial is not None:
            self.update(initial)

    def _validate_key(self, key: Any) -> Handle:
        try:
            return _coerce_compatible_handle(key, self.key_type)
        except TypeError as exc:
            raise TypeError(f"{type(self).__name__} keys must be {self.key_type.__name__}; got {type(key).__name__}") from exc

    @staticmethod
    def _validate_value(value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, (bytearray, memoryview)):
            return bytes(value)
        raise TypeError(f"Handle value maps store bytes; got {type(value).__name__}")

    def __setitem__(self, key: Handle, value: bytes) -> None:  # type: ignore[override]
        super().__setitem__(self._validate_key(key), self._validate_value(value))

    def update(  # type: ignore[override]
        self,
        other: Mapping[Handle, bytes] | Iterable[tuple[Handle, bytes]] = (),
        **kwargs: bytes,
    ) -> None:
        items = cast(Iterable[tuple[Handle, bytes]], other.items()) if isinstance(other, Mapping) else other
        for key, value in items:
            self[key] = value
        for key, value in kwargs.items():
            self[cast(Any, key)] = value

    def clone(self):
        return type(self)(self)

    def get_value_reference(self, key: Handle, byte_wrapper: Any | None = None) -> bytes | None:
        # Python bytes are immutable, so returning the bytes object is the safest
        # equivalent to Java's ByteWrapper reference helper for now.
        return self.get(key)

    def getValueReference(self, key: Handle, byteWrapper: Any | None = None) -> bytes | None:  # noqa: N802 - Java API name
        return self.get_value_reference(key, byteWrapper)

HandleMap = HandleValueMap

class AttributeHandleValueMap(HandleValueMap):
    key_type = AttributeHandle

class ParameterHandleValueMap(HandleValueMap):
    key_type = ParameterHandle

class AttributeSetRegionSetPairList(list):
    """List used by DDM services for attribute/region associations."""

    def clone(self):
        return type(self)(self)

class CollectionFactory(Generic[TCollection]):
    """Small Java-style factory with a ``create`` method."""

    collection_type: type[Any]

    def __init__(self, collection_type: type[Any]):
        self.collection_type = collection_type

    def create(self, capacity: int | None = None):
        return self.collection_type()

class AttributeHandleFactory(HandleFactory[AttributeHandle]):
    def __init__(self):
        super().__init__(AttributeHandle)

class DimensionHandleFactory(HandleFactory[DimensionHandle]):
    def __init__(self):
        super().__init__(DimensionHandle)

class FederateHandleFactory(HandleFactory[FederateHandle]):
    def __init__(self):
        super().__init__(FederateHandle)

class InteractionClassHandleFactory(HandleFactory[InteractionClassHandle]):
    def __init__(self):
        super().__init__(InteractionClassHandle)

class MessageRetractionHandleFactory(HandleFactory[MessageRetractionHandle]):
    def __init__(self):
        super().__init__(MessageRetractionHandle)

class ObjectClassHandleFactory(HandleFactory[ObjectClassHandle]):
    def __init__(self):
        super().__init__(ObjectClassHandle)

class ObjectInstanceHandleFactory(HandleFactory[ObjectInstanceHandle]):
    def __init__(self):
        super().__init__(ObjectInstanceHandle)

class ParameterHandleFactory(HandleFactory[ParameterHandle]):
    def __init__(self):
        super().__init__(ParameterHandle)

class RegionHandleFactory(HandleFactory[RegionHandle]):
    def __init__(self):
        super().__init__(RegionHandle)

class TransportationTypeHandleFactory(HandleFactory[TransportationTypeHandle]):
    def __init__(self):
        super().__init__(TransportationTypeHandle)

class AttributeHandleSetFactory(CollectionFactory[AttributeHandleSet]):
    def __init__(self):
        super().__init__(AttributeHandleSet)

class DimensionHandleSetFactory(CollectionFactory[DimensionHandleSet]):
    def __init__(self):
        super().__init__(DimensionHandleSet)

class FederateHandleSetFactory(CollectionFactory[FederateHandleSet]):
    def __init__(self):
        super().__init__(FederateHandleSet)

class RegionHandleSetFactory(CollectionFactory[RegionHandleSet]):
    def __init__(self):
        super().__init__(RegionHandleSet)

class AttributeHandleValueMapFactory(CollectionFactory[AttributeHandleValueMap]):
    def __init__(self):
        super().__init__(AttributeHandleValueMap)

class ParameterHandleValueMapFactory(CollectionFactory[ParameterHandleValueMap]):
    def __init__(self):
        super().__init__(ParameterHandleValueMap)

class AttributeSetRegionSetPairListFactory(CollectionFactory[AttributeSetRegionSetPairList]):
    def __init__(self):
        super().__init__(AttributeSetRegionSetPairList)

__all__ = [
    "Handle",
    "HandleFactory",
    "AttributeHandle",
    "DimensionHandle",
    "FederateHandle",
    "InteractionClassHandle",
    "MessageRetractionHandle",
    "ObjectClassHandle",
    "ObjectInstanceHandle",
    "ParameterHandle",
    "RegionHandle",
    "TransportationTypeHandle",
    "TypedHandleSet",
    "AttributeHandleSet",
    "DimensionHandleSet",
    "FederateHandleSet",
    "InteractionClassHandleSet",
    "RegionHandleSet",
    "HandleValueMap",
    "AttributeHandleValueMap",
    "ParameterHandleValueMap",
    "AttributeSetRegionSetPairList",
    "CollectionFactory",
    "AttributeHandleFactory",
    "DimensionHandleFactory",
    "FederateHandleFactory",
    "InteractionClassHandleFactory",
    "MessageRetractionHandleFactory",
    "ObjectClassHandleFactory",
    "ObjectInstanceHandleFactory",
    "ParameterHandleFactory",
    "RegionHandleFactory",
    "TransportationTypeHandleFactory",
    "AttributeHandleSetFactory",
    "DimensionHandleSetFactory",
    "FederateHandleSetFactory",
    "RegionHandleSetFactory",
    "AttributeHandleValueMapFactory",
    "ParameterHandleValueMapFactory",
    "AttributeSetRegionSetPairListFactory",
]
