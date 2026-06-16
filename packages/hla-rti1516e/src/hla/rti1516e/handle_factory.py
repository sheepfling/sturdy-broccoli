"""HLA 1516.1-2010 handle factory abstract models.

Sources: Java *HandleFactory.java, *SetFactory.java, and C++ handle decode conventions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    AttributeSetRegionSetPairList,
    DimensionHandle,
    DimensionHandleSet,
    FederateHandle,
    FederateHandleSet,
    HandleKind,
    HandleMap,
    HandleSet,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
    RegionHandle,
    RegionHandleSet,
    TransportationTypeHandle,
)

T_Handle = TypeVar("T_Handle", bound=HandleKind, covariant=True)


class HandleFactory(Generic[T_Handle], ABC):
    @abstractmethod
    def decode(self, buffer: bytes | bytearray | memoryview, offset: int = 0) -> T_Handle: ...


class FederateHandleFactory(HandleFactory[FederateHandle], ABC): ...
class ObjectClassHandleFactory(HandleFactory[ObjectClassHandle], ABC): ...
class InteractionClassHandleFactory(HandleFactory[InteractionClassHandle], ABC): ...
class ObjectInstanceHandleFactory(HandleFactory[ObjectInstanceHandle], ABC): ...
class AttributeHandleFactory(HandleFactory[AttributeHandle], ABC): ...
class ParameterHandleFactory(HandleFactory[ParameterHandle], ABC): ...
class DimensionHandleFactory(HandleFactory[DimensionHandle], ABC): ...
class MessageRetractionHandleFactory(HandleFactory[MessageRetractionHandle], ABC): ...
class RegionHandleFactory(HandleFactory[RegionHandle], ABC): ...


class TransportationTypeHandleFactory(HandleFactory[TransportationTypeHandle], ABC):
    @abstractmethod
    def getHLAdefaultReliable(self) -> TransportationTypeHandle: ...

    @abstractmethod
    def getHLAdefaultBestEffort(self) -> TransportationTypeHandle: ...


T_Set = TypeVar("T_Set", bound=HandleSet, covariant=True)


class HandleSetFactory(Generic[T_Set], ABC):
    @abstractmethod
    def create(self) -> T_Set: ...


class AttributeHandleSetFactory(HandleSetFactory[AttributeHandleSet], ABC): ...
class DimensionHandleSetFactory(HandleSetFactory[DimensionHandleSet], ABC): ...
class FederateHandleSetFactory(HandleSetFactory[FederateHandleSet], ABC): ...
class RegionHandleSetFactory(HandleSetFactory[RegionHandleSet], ABC): ...


T_Map = TypeVar("T_Map", bound=HandleMap, covariant=True)


class HandleMapFactory(Generic[T_Map], ABC):
    @abstractmethod
    def create(self, capacity: int) -> T_Map: ...


class AttributeHandleValueMapFactory(HandleMapFactory[AttributeHandleValueMap], ABC): ...
class ParameterHandleValueMapFactory(HandleMapFactory[ParameterHandleValueMap], ABC): ...


class AttributeSetRegionSetPairListFactory(ABC):
    @abstractmethod
    def create(self, capacity: int) -> AttributeSetRegionSetPairList: ...
