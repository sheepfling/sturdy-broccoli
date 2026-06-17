# ruff: noqa: E501,F811
"""Encoding protocols for IEEE 1516.1-2025.

Sources: Java hla/rti1516_2025/encoding/*.java, C++ RTI/encoding/*.h, and HLAstandardMIM-2025 XML for HLAtransportationTypeHandle.
"""

from __future__ import annotations

import copy
import struct
from collections.abc import Callable
from typing import Any, Generic, Iterable, Iterator, Protocol, Sequence, TypeVar, overload, runtime_checkable

from ._byte_wrapper import ByteWrapper
from .handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    TransportationTypeHandle,
)
from .logical_time import LogicalTime, LogicalTimeInterval

BytesLike = bytes | bytearray | memoryview
T = TypeVar("T")
D = TypeVar("D", bound="DataElement")
LT = TypeVar("LT", bound=LogicalTime)
LTI = TypeVar("LTI", bound=LogicalTimeInterval)


class EncoderException(Exception):
    pass


class DecoderException(Exception):
    pass


@runtime_checkable
class VariableLengthData(Protocol):
    """C++ VariableLengthData equivalent for encoded byte sequences."""

    def data(self) -> bytes: ...

    def size(self) -> int: ...

    def setData(self, data: BytesLike) -> None: ...


@runtime_checkable
class DataElement(Protocol):
    def getOctetBoundary(self) -> int: ...

    @overload
    def encode(self) -> ByteWrapper | VariableLengthData: ...

    @overload
    def encode(self, byteWrapper: ByteWrapper) -> None: ...

    @overload
    def encode(self, inData: VariableLengthData) -> None: ...

    def encode(
        self, target: ByteWrapper | VariableLengthData | None = None
    ) -> ByteWrapper | VariableLengthData | None: ...

    def encodeInto(self, buffer: bytearray) -> None: ...

    def getEncodedLength(self) -> int: ...

    def toByteArray(self) -> bytes: ...

    @overload
    def decode(self: D, byteWrapper: ByteWrapper) -> D: ...

    @overload
    def decode(self: D, data: BytesLike | VariableLengthData) -> D: ...

    def decode(self: D, source: ByteWrapper | BytesLike | VariableLengthData) -> D: ...

    def clone(self: D) -> D: ...

    def isSameTypeAs(self, inData: DataElement) -> bool: ...

    def hash(self) -> int: ...


@runtime_checkable
class DataElementFactory(Protocol[D]):
    def createElement(self, index: int = 0) -> D: ...


@runtime_checkable
class ValueDataElement(DataElement, Protocol[T]):
    def getValue(self) -> T: ...

    def setValue(self: D, value: T) -> D: ...


class HLAASCIIchar(ValueDataElement[int], Protocol): ...
class HLAASCIIstring(ValueDataElement[str], Protocol): ...
class HLAboolean(ValueDataElement[bool], Protocol): ...
class HLAbyte(ValueDataElement[int], Protocol): ...
class HLAfloat32BE(ValueDataElement[float], Protocol): ...
class HLAfloat32LE(ValueDataElement[float], Protocol): ...
class HLAfloat64BE(ValueDataElement[float], Protocol): ...
class HLAfloat64LE(ValueDataElement[float], Protocol): ...
class HLAinteger16BE(ValueDataElement[int], Protocol): ...
class HLAinteger16LE(ValueDataElement[int], Protocol): ...
class HLAinteger32BE(ValueDataElement[int], Protocol): ...
class HLAinteger32LE(ValueDataElement[int], Protocol): ...
class HLAinteger64BE(ValueDataElement[int], Protocol): ...
class HLAinteger64LE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger16BE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger16LE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger32BE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger32LE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger64BE(ValueDataElement[int], Protocol): ...
class HLAunsignedInteger64LE(ValueDataElement[int], Protocol): ...
class HLAoctet(ValueDataElement[int], Protocol): ...
class HLAoctetPairBE(ValueDataElement[int], Protocol): ...
class HLAoctetPairLE(ValueDataElement[int], Protocol): ...
class HLAunicodeChar(ValueDataElement[int], Protocol): ...
class HLAunicodeString(ValueDataElement[str], Protocol): ...


class HLAopaqueData(ValueDataElement[bytes], Iterable[int], Protocol):
    def size(self) -> int: ...
    def get(self, index: int) -> int: ...
    def __iter__(self) -> Iterator[int]: ...
    def setValue(self: D, value: BytesLike | Sequence[int]) -> D: ...


class HLAfixedArray(DataElement, Iterable[D], Protocol[D]):
    def size(self) -> int: ...
    def get(self, index: int) -> D: ...
    def __iter__(self) -> Iterator[D]: ...
    def set(self, index: int, dataElement: D) -> HLAfixedArray[D]: ...


class HLAvariableArray(DataElement, Iterable[D], Protocol[D]):
    def addElement(self, dataElement: D) -> HLAvariableArray[D]: ...
    def size(self) -> int: ...
    def get(self, index: int) -> D: ...
    def __iter__(self) -> Iterator[D]: ...
    def resize(self, newSize: int) -> HLAvariableArray[D]: ...
    def set(self, index: int, dataElement: D) -> HLAvariableArray[D]: ...


class HLAfixedRecord(DataElement, Iterable[DataElement], Protocol):
    def add(self, dataElement: DataElement) -> None: ...
    def appendElement(self, dataElement: DataElement) -> HLAfixedRecord: ...
    def size(self) -> int: ...
    def get(self, index: int) -> DataElement: ...
    def __iter__(self) -> Iterator[DataElement]: ...
    def set(self, index: int, dataElement: DataElement) -> HLAfixedRecord: ...


class HLAvariantRecord(DataElement, Protocol[D]):
    def setVariant(self, discriminant: D, dataElement: DataElement) -> HLAvariantRecord[D]: ...
    def setDiscriminant(self, discriminant: D) -> HLAvariantRecord[D]: ...
    def getDiscriminant(self) -> D: ...
    def getValue(self) -> DataElement: ...


class HLAextendableVariantRecord(HLAvariantRecord[D], Protocol[D]): ...


class HLAfederateHandle(ValueDataElement[FederateHandle], Protocol): ...
class HLAobjectClassHandle(ValueDataElement[ObjectClassHandle], Protocol): ...
class HLAinteractionClassHandle(ValueDataElement[InteractionClassHandle], Protocol): ...
class HLAobjectInstanceHandle(ValueDataElement[ObjectInstanceHandle], Protocol): ...
class HLAattributeHandle(ValueDataElement[AttributeHandle], Protocol): ...
class HLAparameterHandle(ValueDataElement[ParameterHandle], Protocol): ...
class HLAdimensionHandle(ValueDataElement[DimensionHandle], Protocol): ...
class HLAmessageRetractionHandle(ValueDataElement[MessageRetractionHandle], Protocol): ...
class HLAregionHandle(ValueDataElement[RegionHandle], Protocol): ...
class HLAtransportationTypeHandle(ValueDataElement[TransportationTypeHandle], Protocol): ...


class HLAlogicalTime(ValueDataElement[LT], Protocol[LT, LTI]): ...
class HLAlogicalTimeInterval(ValueDataElement[LTI], Protocol[LT, LTI]): ...


@runtime_checkable
class EncoderFactory(Protocol):
    # Primitive HLA data types. Optional value arguments collapse the Java
    # overloaded factory methods into typed Python signatures.
    # Source: Java encoding/EncoderFactory.java declares createHLAASCIIchar() and createHLAASCIIchar(value).
    @overload
    def createHLAASCIIchar(self) -> HLAASCIIchar: ...

    @overload
    def createHLAASCIIchar(self, value: int) -> HLAASCIIchar: ...

    def createHLAASCIIchar(self, value: int | None = None) -> HLAASCIIchar: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAASCIIstring() and createHLAASCIIstring(value).
    @overload
    def createHLAASCIIstring(self) -> HLAASCIIstring: ...

    @overload
    def createHLAASCIIstring(self, value: str) -> HLAASCIIstring: ...

    def createHLAASCIIstring(self, value: str | None = None) -> HLAASCIIstring: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAboolean() and createHLAboolean(value).
    @overload
    def createHLAboolean(self) -> HLAboolean: ...

    @overload
    def createHLAboolean(self, value: bool) -> HLAboolean: ...

    def createHLAboolean(self, value: bool | None = None) -> HLAboolean: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAbyte() and createHLAbyte(value).
    @overload
    def createHLAbyte(self) -> HLAbyte: ...

    @overload
    def createHLAbyte(self, value: int) -> HLAbyte: ...

    def createHLAbyte(self, value: int | None = None) -> HLAbyte: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAfloat32BE() and createHLAfloat32BE(value).
    @overload
    def createHLAfloat32BE(self) -> HLAfloat32BE: ...

    @overload
    def createHLAfloat32BE(self, value: float) -> HLAfloat32BE: ...

    def createHLAfloat32BE(self, value: float | None = None) -> HLAfloat32BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAfloat32LE() and createHLAfloat32LE(value).
    @overload
    def createHLAfloat32LE(self) -> HLAfloat32LE: ...

    @overload
    def createHLAfloat32LE(self, value: float) -> HLAfloat32LE: ...

    def createHLAfloat32LE(self, value: float | None = None) -> HLAfloat32LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAfloat64BE() and createHLAfloat64BE(value).
    @overload
    def createHLAfloat64BE(self) -> HLAfloat64BE: ...

    @overload
    def createHLAfloat64BE(self, value: float) -> HLAfloat64BE: ...

    def createHLAfloat64BE(self, value: float | None = None) -> HLAfloat64BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAfloat64LE() and createHLAfloat64LE(value).
    @overload
    def createHLAfloat64LE(self) -> HLAfloat64LE: ...

    @overload
    def createHLAfloat64LE(self, value: float) -> HLAfloat64LE: ...

    def createHLAfloat64LE(self, value: float | None = None) -> HLAfloat64LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger16BE() and createHLAinteger16BE(value).
    @overload
    def createHLAinteger16BE(self) -> HLAinteger16BE: ...

    @overload
    def createHLAinteger16BE(self, value: int) -> HLAinteger16BE: ...

    def createHLAinteger16BE(self, value: int | None = None) -> HLAinteger16BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger16LE() and createHLAinteger16LE(value).
    @overload
    def createHLAinteger16LE(self) -> HLAinteger16LE: ...

    @overload
    def createHLAinteger16LE(self, value: int) -> HLAinteger16LE: ...

    def createHLAinteger16LE(self, value: int | None = None) -> HLAinteger16LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger32BE() and createHLAinteger32BE(value).
    @overload
    def createHLAinteger32BE(self) -> HLAinteger32BE: ...

    @overload
    def createHLAinteger32BE(self, value: int) -> HLAinteger32BE: ...

    def createHLAinteger32BE(self, value: int | None = None) -> HLAinteger32BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger32LE() and createHLAinteger32LE(value).
    @overload
    def createHLAinteger32LE(self) -> HLAinteger32LE: ...

    @overload
    def createHLAinteger32LE(self, value: int) -> HLAinteger32LE: ...

    def createHLAinteger32LE(self, value: int | None = None) -> HLAinteger32LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger64BE() and createHLAinteger64BE(value).
    @overload
    def createHLAinteger64BE(self) -> HLAinteger64BE: ...

    @overload
    def createHLAinteger64BE(self, value: int) -> HLAinteger64BE: ...

    def createHLAinteger64BE(self, value: int | None = None) -> HLAinteger64BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteger64LE() and createHLAinteger64LE(value).
    @overload
    def createHLAinteger64LE(self) -> HLAinteger64LE: ...

    @overload
    def createHLAinteger64LE(self, value: int) -> HLAinteger64LE: ...

    def createHLAinteger64LE(self, value: int | None = None) -> HLAinteger64LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger16BE() and createHLAunsignedInteger16BE(value).
    @overload
    def createHLAunsignedInteger16BE(self) -> HLAunsignedInteger16BE: ...

    @overload
    def createHLAunsignedInteger16BE(self, value: int) -> HLAunsignedInteger16BE: ...

    def createHLAunsignedInteger16BE(self, value: int | None = None) -> HLAunsignedInteger16BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger16LE() and createHLAunsignedInteger16LE(value).
    @overload
    def createHLAunsignedInteger16LE(self) -> HLAunsignedInteger16LE: ...

    @overload
    def createHLAunsignedInteger16LE(self, value: int) -> HLAunsignedInteger16LE: ...

    def createHLAunsignedInteger16LE(self, value: int | None = None) -> HLAunsignedInteger16LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger32BE() and createHLAunsignedInteger32BE(value).
    @overload
    def createHLAunsignedInteger32BE(self) -> HLAunsignedInteger32BE: ...

    @overload
    def createHLAunsignedInteger32BE(self, value: int) -> HLAunsignedInteger32BE: ...

    def createHLAunsignedInteger32BE(self, value: int | None = None) -> HLAunsignedInteger32BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger32LE() and createHLAunsignedInteger32LE(value).
    @overload
    def createHLAunsignedInteger32LE(self) -> HLAunsignedInteger32LE: ...

    @overload
    def createHLAunsignedInteger32LE(self, value: int) -> HLAunsignedInteger32LE: ...

    def createHLAunsignedInteger32LE(self, value: int | None = None) -> HLAunsignedInteger32LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger64BE() and createHLAunsignedInteger64BE(value).
    @overload
    def createHLAunsignedInteger64BE(self) -> HLAunsignedInteger64BE: ...

    @overload
    def createHLAunsignedInteger64BE(self, value: int) -> HLAunsignedInteger64BE: ...

    def createHLAunsignedInteger64BE(self, value: int | None = None) -> HLAunsignedInteger64BE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunsignedInteger64LE() and createHLAunsignedInteger64LE(value).
    @overload
    def createHLAunsignedInteger64LE(self) -> HLAunsignedInteger64LE: ...

    @overload
    def createHLAunsignedInteger64LE(self, value: int) -> HLAunsignedInteger64LE: ...

    def createHLAunsignedInteger64LE(self, value: int | None = None) -> HLAunsignedInteger64LE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAoctet() and createHLAoctet(value).
    @overload
    def createHLAoctet(self) -> HLAoctet: ...

    @overload
    def createHLAoctet(self, value: int) -> HLAoctet: ...

    def createHLAoctet(self, value: int | None = None) -> HLAoctet: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAoctetPairBE() and createHLAoctetPairBE(value).
    @overload
    def createHLAoctetPairBE(self) -> HLAoctetPairBE: ...

    @overload
    def createHLAoctetPairBE(self, value: int) -> HLAoctetPairBE: ...

    def createHLAoctetPairBE(self, value: int | None = None) -> HLAoctetPairBE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAoctetPairLE() and createHLAoctetPairLE(value).
    @overload
    def createHLAoctetPairLE(self) -> HLAoctetPairLE: ...

    @overload
    def createHLAoctetPairLE(self, value: int) -> HLAoctetPairLE: ...

    def createHLAoctetPairLE(self, value: int | None = None) -> HLAoctetPairLE: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAopaqueData() and createHLAopaqueData(value).
    @overload
    def createHLAopaqueData(self) -> HLAopaqueData: ...

    @overload
    def createHLAopaqueData(self, value: BytesLike) -> HLAopaqueData: ...

    def createHLAopaqueData(self, value: BytesLike | None = None) -> HLAopaqueData: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunicodeChar() and createHLAunicodeChar(value).
    @overload
    def createHLAunicodeChar(self) -> HLAunicodeChar: ...

    @overload
    def createHLAunicodeChar(self, value: int) -> HLAunicodeChar: ...

    def createHLAunicodeChar(self, value: int | None = None) -> HLAunicodeChar: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAunicodeString() and createHLAunicodeString(value).
    @overload
    def createHLAunicodeString(self) -> HLAunicodeString: ...

    @overload
    def createHLAunicodeString(self, value: str) -> HLAunicodeString: ...

    def createHLAunicodeString(self, value: str | None = None) -> HLAunicodeString: ...

    # Complex HLA data types.
    @overload
    def createHLAfixedArray(self, factory: DataElementFactory[D], size: int) -> HLAfixedArray[D]: ...

    @overload
    def createHLAfixedArray(self, *elements: D) -> HLAfixedArray[D]: ...

    def createHLAfixedArray(
        self,
        factoryOrFirstElement: DataElementFactory[D] | D,
        sizeOrSecondElement: int | D | None = None,
        *elements: D,
    ) -> HLAfixedArray[D]: ...

    def createHLAvariableArray(self, factory: DataElementFactory[D], *elements: D) -> HLAvariableArray[D]: ...
    def createHLAfixedRecord(self) -> HLAfixedRecord: ...
    def createHLAvariantRecord(self, discriminant: D) -> HLAvariantRecord[D]: ...
    def createHLAextendableVariantRecord(self, discriminant: D) -> HLAextendableVariantRecord[D]: ...

    # Encoded RTI handles and time values.
    # Source: Java encoding/EncoderFactory.java declares createHLAfederateHandle(RTIambassador) and createHLAfederateHandle(RTIambassador, handle).
    @overload
    def createHLAfederateHandle(self, rtiAmbassador) -> HLAfederateHandle: ...

    @overload
    def createHLAfederateHandle(self, rtiAmbassador, federateHandle: FederateHandle) -> HLAfederateHandle: ...

    def createHLAfederateHandle(self, rtiAmbassador, federateHandle: FederateHandle | None = None) -> HLAfederateHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAobjectClassHandle(RTIambassador) and createHLAobjectClassHandle(RTIambassador, handle).
    @overload
    def createHLAobjectClassHandle(self, rtiAmbassador) -> HLAobjectClassHandle: ...

    @overload
    def createHLAobjectClassHandle(self, rtiAmbassador, objectClassHandle: ObjectClassHandle) -> HLAobjectClassHandle: ...

    def createHLAobjectClassHandle(self, rtiAmbassador, objectClassHandle: ObjectClassHandle | None = None) -> HLAobjectClassHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAinteractionClassHandle(RTIambassador) and createHLAinteractionClassHandle(RTIambassador, handle).
    @overload
    def createHLAinteractionClassHandle(self, rtiAmbassador) -> HLAinteractionClassHandle: ...

    @overload
    def createHLAinteractionClassHandle(self, rtiAmbassador, interactionClassHandle: InteractionClassHandle) -> HLAinteractionClassHandle: ...

    def createHLAinteractionClassHandle(self, rtiAmbassador, interactionClassHandle: InteractionClassHandle | None = None) -> HLAinteractionClassHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAobjectInstanceHandle(RTIambassador) and createHLAobjectInstanceHandle(RTIambassador, handle).
    @overload
    def createHLAobjectInstanceHandle(self, rtiAmbassador) -> HLAobjectInstanceHandle: ...

    @overload
    def createHLAobjectInstanceHandle(self, rtiAmbassador, objectInstanceHandle: ObjectInstanceHandle) -> HLAobjectInstanceHandle: ...

    def createHLAobjectInstanceHandle(self, rtiAmbassador, objectInstanceHandle: ObjectInstanceHandle | None = None) -> HLAobjectInstanceHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAattributeHandle(RTIambassador) and createHLAattributeHandle(RTIambassador, handle).
    @overload
    def createHLAattributeHandle(self, rtiAmbassador) -> HLAattributeHandle: ...

    @overload
    def createHLAattributeHandle(self, rtiAmbassador, attributeHandle: AttributeHandle) -> HLAattributeHandle: ...

    def createHLAattributeHandle(self, rtiAmbassador, attributeHandle: AttributeHandle | None = None) -> HLAattributeHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAparameterHandle(RTIambassador) and createHLAparameterHandle(RTIambassador, handle).
    @overload
    def createHLAparameterHandle(self, rtiAmbassador) -> HLAparameterHandle: ...

    @overload
    def createHLAparameterHandle(self, rtiAmbassador, parameterHandle: ParameterHandle) -> HLAparameterHandle: ...

    def createHLAparameterHandle(self, rtiAmbassador, parameterHandle: ParameterHandle | None = None) -> HLAparameterHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAdimensionHandle(RTIambassador) and createHLAdimensionHandle(RTIambassador, handle).
    @overload
    def createHLAdimensionHandle(self, rtiAmbassador) -> HLAdimensionHandle: ...

    @overload
    def createHLAdimensionHandle(self, rtiAmbassador, dimensionHandle: DimensionHandle) -> HLAdimensionHandle: ...

    def createHLAdimensionHandle(self, rtiAmbassador, dimensionHandle: DimensionHandle | None = None) -> HLAdimensionHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAmessageRetractionHandle(RTIambassador) and createHLAmessageRetractionHandle(RTIambassador, handle).
    @overload
    def createHLAmessageRetractionHandle(self, rtiAmbassador) -> HLAmessageRetractionHandle: ...

    @overload
    def createHLAmessageRetractionHandle(self, rtiAmbassador, messageRetractionHandle: MessageRetractionHandle) -> HLAmessageRetractionHandle: ...

    def createHLAmessageRetractionHandle(self, rtiAmbassador, messageRetractionHandle: MessageRetractionHandle | None = None) -> HLAmessageRetractionHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAregionHandle(RTIambassador) and createHLAregionHandle(RTIambassador, handle).
    @overload
    def createHLAregionHandle(self, rtiAmbassador) -> HLAregionHandle: ...

    @overload
    def createHLAregionHandle(self, rtiAmbassador, regionHandle: RegionHandle) -> HLAregionHandle: ...

    def createHLAregionHandle(self, rtiAmbassador, regionHandle: RegionHandle | None = None) -> HLAregionHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAtransportationTypeHandle(RTIambassador) and createHLAtransportationTypeHandle(RTIambassador, handle).
    @overload
    def createHLAtransportationTypeHandle(self, rtiAmbassador) -> HLAtransportationTypeHandle: ...

    @overload
    def createHLAtransportationTypeHandle(self, rtiAmbassador, transportationTypeHandle: TransportationTypeHandle) -> HLAtransportationTypeHandle: ...

    def createHLAtransportationTypeHandle(self, rtiAmbassador, transportationTypeHandle: TransportationTypeHandle | None = None) -> HLAtransportationTypeHandle: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAlogicalTime(RTIambassador) and createHLAlogicalTime(RTIambassador, LogicalTime).
    @overload
    def createHLAlogicalTime(self, rtiAmbassador) -> HLAlogicalTime[LT, LTI]: ...

    @overload
    def createHLAlogicalTime(self, rtiAmbassador, logicalTime: LT) -> HLAlogicalTime[LT, LTI]: ...

    def createHLAlogicalTime(self, rtiAmbassador, logicalTime: LT | None = None) -> HLAlogicalTime[LT, LTI]: ...
    # Source: Java encoding/EncoderFactory.java declares createHLAlogicalTimeInterval(RTIambassador) and createHLAlogicalTimeInterval(RTIambassador, LogicalTimeInterval).
    @overload
    def createHLAlogicalTimeInterval(self, rtiAmbassador) -> HLAlogicalTimeInterval[LT, LTI]: ...

    @overload
    def createHLAlogicalTimeInterval(self, rtiAmbassador, logicalTimeInterval: LTI) -> HLAlogicalTimeInterval[LT, LTI]: ...

    def createHLAlogicalTimeInterval(self, rtiAmbassador, logicalTimeInterval: LTI | None = None) -> HLAlogicalTimeInterval[LT, LTI]: ...


def _as_bytes(value: BytesLike | VariableLengthData) -> bytes:
    if hasattr(value, "data") and callable(value.data):  # type: ignore[attr-defined]
        return value.data()  # type: ignore[no-any-return]
    return bytes(value)


def _copy_value(value: T) -> T:
    return copy.deepcopy(value)


class SimpleVariableLengthData:
    """Concrete C++-style variable-length byte holder."""

    def __init__(self, data: BytesLike = b"") -> None:
        self._data = bytes(data)

    def data(self) -> bytes:
        return self._data

    def size(self) -> int:
        return len(self._data)

    def setData(self, data: BytesLike) -> None:  # noqa: N802
        self._data = bytes(data)


class SimpleByteWrapper(ByteWrapper):
    """Concrete ByteWrapper for Python-side encoder tests and utilities."""

    def __init__(self, buffer: BytesLike | None = None, offset: int = 0, length: int | None = None) -> None:
        raw = bytearray(buffer or b"")
        self.reassign(raw, offset, len(raw) - offset if length is None else length)

    def reassign(self, buffer: bytearray, offset: int, length: int) -> None:
        if offset < 0 or length < 0 or offset + length > len(buffer):
            raise DecoderException("ByteWrapper assignment is outside the supplied buffer")
        self._buffer = buffer
        self._start = offset
        self._length = length
        self._pos = offset

    def reset(self) -> None:
        self._pos = self._start

    def verify(self, length: int) -> None:
        if self.remaining() < length:
            raise DecoderException(f"ByteWrapper needs {length} bytes, only {self.remaining()} remain")

    def getInt(self) -> int:  # noqa: N802
        self.verify(4)
        value = struct.unpack(">i", self._buffer[self._pos : self._pos + 4])[0]
        self._pos += 4
        return value

    def get(self, dest: bytearray | None = None) -> int | None:
        if dest is None:
            self.verify(1)
            value = self._buffer[self._pos]
            self._pos += 1
            return value
        self.verify(len(dest))
        dest[:] = self._buffer[self._pos : self._pos + len(dest)]
        self._pos += len(dest)
        return None

    def putInt(self, value: int) -> None:  # noqa: N802
        self.put(struct.pack(">i", value))

    def put(self, value: int | BytesLike, offset: int | None = None, count: int | None = None) -> None:
        payload = bytes([value]) if isinstance(value, int) else bytes(value)
        if offset is not None or count is not None:
            start = offset or 0
            stop = len(payload) if count is None else start + count
            payload = payload[start:stop]
        self._ensure_write_capacity(len(payload))
        self._buffer[self._pos : self._pos + len(payload)] = payload
        self._pos += len(payload)
        self._length = max(self._length, self._pos - self._start)

    def array(self) -> bytearray:
        return self._buffer

    def getPos(self) -> int:  # noqa: N802
        return self._pos

    def remaining(self) -> int:
        return self._start + self._length - self._pos

    def advance(self, n: int) -> None:
        self.verify(n)
        self._pos += n

    def align(self, n: int) -> None:
        if n <= 1:
            return
        aligned = self._start + (((self._pos - self._start) + n - 1) // n) * n
        self.advance(aligned - self._pos)

    def slice(self, length: int | None = None) -> "SimpleByteWrapper":
        actual = self.remaining() if length is None else length
        self.verify(actual)
        sliced = SimpleByteWrapper(self._buffer, self._pos, actual)
        self._pos += actual
        return sliced

    def toString(self) -> str:  # noqa: N802
        return self.toByteArray().hex()

    def toByteArray(self) -> bytes:  # noqa: N802
        return bytes(self._buffer[self._start : self._start + self._length])

    def _ensure_write_capacity(self, length: int) -> None:
        required = self._pos + length
        if required > len(self._buffer):
            self._buffer.extend(b"\x00" * (required - len(self._buffer)))


class _DataElement:
    _octet_boundary = 1

    def getOctetBoundary(self) -> int:  # noqa: N802
        return self._octet_boundary

    def encode(self, target: ByteWrapper | VariableLengthData | None = None) -> ByteWrapper | VariableLengthData | None:
        payload = self.toByteArray()
        if target is None:
            return SimpleVariableLengthData(payload)
        if hasattr(target, "put"):
            target.put(payload)  # type: ignore[attr-defined]
            return None
        if hasattr(target, "setData"):
            target.setData(payload)  # type: ignore[attr-defined]
            return None
        raise EncoderException(f"Unsupported encode target {type(target)!r}")

    def encodeInto(self, buffer: bytearray) -> None:  # noqa: N802
        buffer.extend(self.toByteArray())

    def getEncodedLength(self) -> int:  # noqa: N802
        return len(self.toByteArray())

    def toByteArray(self) -> bytes:  # noqa: N802
        raise NotImplementedError

    def decode(self: D, source: ByteWrapper | BytesLike | VariableLengthData) -> D:
        data = source.toByteArray() if hasattr(source, "toByteArray") else _as_bytes(source)  # type: ignore[arg-type]
        self._decode_from(data)
        return self

    def clone(self: D) -> D:
        return copy.deepcopy(self)

    def isSameTypeAs(self, inData: DataElement) -> bool:  # noqa: N802
        return type(self) is type(inData)

    def hash(self) -> int:
        return hash((type(self), self.toByteArray()))

    def _decode_from(self, data: bytes) -> None:
        raise NotImplementedError


class _ScalarElement(_DataElement):
    _fmt = ""
    _default: Any = 0
    _octet_boundary = 1

    def __init__(self, value: Any | None = None) -> None:
        self._value = self._default if value is None else value

    def getValue(self) -> Any:  # noqa: N802
        return self._value

    def setValue(self, value: Any) -> "_ScalarElement":  # noqa: N802
        self._value = value
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        try:
            return struct.pack(self._fmt, self._value)
        except struct.error as exc:
            raise EncoderException(str(exc)) from exc

    def _decode_from(self, data: bytes) -> None:
        size = struct.calcsize(self._fmt)
        if len(data) < size:
            raise DecoderException(f"{type(self).__name__} needs {size} bytes, got {len(data)}")
        self._value = struct.unpack(self._fmt, data[:size])[0]


class HLAboolean(_ScalarElement):
    _fmt = ">B"
    _default = False

    def toByteArray(self) -> bytes:  # noqa: N802
        return struct.pack(">B", 1 if self._value else 0)

    def _decode_from(self, data: bytes) -> None:
        if not data:
            raise DecoderException("HLAboolean needs 1 byte")
        self._value = bool(data[0])


class HLAbyte(_ScalarElement):
    _fmt = ">b"


class HLAoctet(_ScalarElement):
    _fmt = ">B"


class HLAinteger16BE(_ScalarElement):
    _fmt = ">h"
    _octet_boundary = 2


class HLAinteger16LE(_ScalarElement):
    _fmt = "<h"
    _octet_boundary = 2


class HLAinteger32BE(_ScalarElement):
    _fmt = ">i"
    _octet_boundary = 4


class HLAinteger32LE(_ScalarElement):
    _fmt = "<i"
    _octet_boundary = 4


class HLAinteger64BE(_ScalarElement):
    _fmt = ">q"
    _octet_boundary = 8


class HLAinteger64LE(_ScalarElement):
    _fmt = "<q"
    _octet_boundary = 8


class HLAunsignedInteger16BE(_ScalarElement):
    _fmt = ">H"
    _octet_boundary = 2


class HLAunsignedInteger16LE(_ScalarElement):
    _fmt = "<H"
    _octet_boundary = 2


class HLAunsignedInteger32BE(_ScalarElement):
    _fmt = ">I"
    _octet_boundary = 4


class HLAunsignedInteger32LE(_ScalarElement):
    _fmt = "<I"
    _octet_boundary = 4


class HLAunsignedInteger64BE(_ScalarElement):
    _fmt = ">Q"
    _octet_boundary = 8


class HLAunsignedInteger64LE(_ScalarElement):
    _fmt = "<Q"
    _octet_boundary = 8


class HLAfloat32BE(_ScalarElement):
    _fmt = ">f"
    _default = 0.0
    _octet_boundary = 4


class HLAfloat32LE(_ScalarElement):
    _fmt = "<f"
    _default = 0.0
    _octet_boundary = 4


class HLAfloat64BE(_ScalarElement):
    _fmt = ">d"
    _default = 0.0
    _octet_boundary = 8


class HLAfloat64LE(_ScalarElement):
    _fmt = "<d"
    _default = 0.0
    _octet_boundary = 8


class HLAoctetPairBE(HLAunsignedInteger16BE): ...


class HLAoctetPairLE(HLAunsignedInteger16LE): ...


class HLAASCIIchar(_DataElement):
    def __init__(self, value: int | str = 0) -> None:
        self._value = value if isinstance(value, int) else ord(value[:1])

    def getValue(self) -> int:  # noqa: N802
        return self._value

    def setValue(self, value: int | str) -> "HLAASCIIchar":  # noqa: N802
        self._value = value if isinstance(value, int) else ord(value[:1])
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        if not 0 <= self._value <= 0x7F:
            raise EncoderException("HLAASCIIchar value must be in ASCII range")
        return bytes([self._value])

    def _decode_from(self, data: bytes) -> None:
        if not data:
            raise DecoderException("HLAASCIIchar needs 1 byte")
        self._value = data[0]


class HLAunicodeChar(_ScalarElement):
    _fmt = ">H"
    _octet_boundary = 2


class _LengthPrefixedString(_DataElement):
    _encoding = "ascii"
    _octet_boundary = 4

    def __init__(self, value: str = "") -> None:
        self._value = value

    def getValue(self) -> str:  # noqa: N802
        return self._value

    def setValue(self, value: str) -> "_LengthPrefixedString":  # noqa: N802
        self._value = value
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        payload = self._value.encode(self._encoding)
        return struct.pack(">I", len(payload)) + payload

    def _decode_from(self, data: bytes) -> None:
        if len(data) < 4:
            raise DecoderException(f"{type(self).__name__} needs a 4-byte length prefix")
        size = struct.unpack(">I", data[:4])[0]
        payload = data[4 : 4 + size]
        if len(payload) != size:
            raise DecoderException(f"{type(self).__name__} expected {size} payload bytes, got {len(payload)}")
        self._value = payload.decode(self._encoding)


class HLAASCIIstring(_LengthPrefixedString):
    _encoding = "ascii"


class HLAunicodeString(_LengthPrefixedString):
    _encoding = "utf-16-be"


class HLAopaqueData(_DataElement):
    _octet_boundary = 4

    def __init__(self, value: BytesLike | Sequence[int] = b"") -> None:
        self.setValue(value)

    def __iter__(self) -> Iterator[int]:
        return iter(self._value)

    def size(self) -> int:
        return len(self._value)

    def get(self, index: int) -> int:
        return self._value[index]

    def getValue(self) -> bytes:  # noqa: N802
        return self._value

    def setValue(self, value: BytesLike | Sequence[int]) -> "HLAopaqueData":  # noqa: N802
        self._value = bytes(value)
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        return struct.pack(">I", len(self._value)) + self._value

    def _decode_from(self, data: bytes) -> None:
        if len(data) < 4:
            raise DecoderException("HLAopaqueData needs a 4-byte length prefix")
        size = struct.unpack(">I", data[:4])[0]
        payload = data[4 : 4 + size]
        if len(payload) != size:
            raise DecoderException(f"HLAopaqueData expected {size} bytes, got {len(payload)}")
        self._value = payload


class HLAfixedArray(_DataElement, Iterable[D]):
    def __init__(self, elements: Iterable[D] = ()) -> None:
        self._elements = list(elements)

    def __iter__(self) -> Iterator[D]:
        return iter(self._elements)

    def size(self) -> int:
        return len(self._elements)

    def get(self, index: int) -> D:
        return self._elements[index]

    def set(self, index: int, dataElement: D) -> "HLAfixedArray[D]":  # noqa: N802
        self._elements[index] = dataElement
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"".join(element.toByteArray() for element in self._elements)  # type: ignore[attr-defined]

    def _decode_from(self, data: bytes) -> None:
        offset = 0
        for element in self._elements:
            element.decode(data[offset:])  # type: ignore[attr-defined]
            offset += element.getEncodedLength()  # type: ignore[attr-defined]


class HLAvariableArray(HLAfixedArray[D]):
    def addElement(self, dataElement: D) -> "HLAvariableArray[D]":  # noqa: N802
        self._elements.append(dataElement)
        return self

    def resize(self, newSize: int) -> "HLAvariableArray[D]":  # noqa: N802
        if newSize < 0:
            raise EncoderException("HLAvariableArray size cannot be negative")
        if not self._elements and newSize:
            raise EncoderException("Cannot resize an empty variable array without an element factory")
        while len(self._elements) < newSize:
            self._elements.append(self._elements[-1].clone())  # type: ignore[attr-defined]
        del self._elements[newSize:]
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        return struct.pack(">I", len(self._elements)) + super().toByteArray()

    def _decode_from(self, data: bytes) -> None:
        if len(data) < 4:
            raise DecoderException("HLAvariableArray needs a 4-byte element count")
        count = struct.unpack(">I", data[:4])[0]
        if count != len(self._elements):
            raise DecoderException(f"HLAvariableArray expected {len(self._elements)} elements, encoded {count}")
        super()._decode_from(data[4:])


class HLAfixedRecord(_DataElement, Iterable[DataElement]):
    def __init__(self, elements: Iterable[DataElement] = ()) -> None:
        self._elements = list(elements)

    def __iter__(self) -> Iterator[DataElement]:
        return iter(self._elements)

    def add(self, dataElement: DataElement) -> None:
        self._elements.append(dataElement)

    def appendElement(self, dataElement: DataElement) -> "HLAfixedRecord":  # noqa: N802
        self.add(dataElement)
        return self

    def size(self) -> int:
        return len(self._elements)

    def get(self, index: int) -> DataElement:
        return self._elements[index]

    def set(self, index: int, dataElement: DataElement) -> "HLAfixedRecord":
        self._elements[index] = dataElement
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"".join(element.toByteArray() for element in self._elements)  # type: ignore[attr-defined]

    def _decode_from(self, data: bytes) -> None:
        offset = 0
        for element in self._elements:
            element.decode(data[offset:])  # type: ignore[attr-defined]
            offset += element.getEncodedLength()  # type: ignore[attr-defined]


class HLAvariantRecord(_DataElement, Generic[D]):
    def __init__(self, discriminant: D) -> None:
        self._discriminant = discriminant
        self._variants: dict[bytes, DataElement] = {}
        self._value: DataElement | None = None

    def setVariant(self, discriminant: D, dataElement: DataElement) -> "HLAvariantRecord[D]":  # noqa: N802
        self._variants[discriminant.toByteArray()] = dataElement  # type: ignore[attr-defined]
        if self._discriminant.toByteArray() == discriminant.toByteArray() or self._value is None:  # type: ignore[attr-defined]
            self._discriminant = discriminant
            self._value = dataElement
        return self

    def setDiscriminant(self, discriminant: D) -> "HLAvariantRecord[D]":  # noqa: N802
        self._discriminant = discriminant
        self._value = self._variants.get(discriminant.toByteArray())  # type: ignore[attr-defined]
        return self

    def getDiscriminant(self) -> D:  # noqa: N802
        return self._discriminant

    def getValue(self) -> DataElement:  # noqa: N802
        if self._value is None:
            raise EncoderException("HLAvariantRecord has no value for the active discriminant")
        return self._value

    def toByteArray(self) -> bytes:  # noqa: N802
        return self._discriminant.toByteArray() + self.getValue().toByteArray()  # type: ignore[attr-defined]

    def _decode_from(self, data: bytes) -> None:
        self._discriminant.decode(data)  # type: ignore[attr-defined]
        discriminant_length = self._discriminant.getEncodedLength()  # type: ignore[attr-defined]
        self._value = self._variants.get(self._discriminant.toByteArray())  # type: ignore[attr-defined]
        if self._value is None:
            raise DecoderException("No HLAvariantRecord value registered for decoded discriminant")
        self._value.decode(data[discriminant_length:])  # type: ignore[attr-defined]


class HLAextendableVariantRecord(HLAvariantRecord[D]): ...


class _EncodedValueElement(_DataElement, Generic[T]):
    def __init__(self, value: T | None = None) -> None:
        self._value = value

    def getValue(self) -> T | None:  # noqa: N802
        return self._value

    def setValue(self, value: T) -> "_EncodedValueElement[T]":  # noqa: N802
        self._value = value
        return self

    def toByteArray(self) -> bytes:  # noqa: N802
        if self._value is None:
            return b""
        encode = getattr(self._value, "encode", None)
        if callable(encode):
            buffer = bytearray(getattr(self._value, "encodedLength", lambda: 0)())
            self._value.encode(buffer, 0)
            return bytes(buffer)
        raw = getattr(self._value, "value", self._value)
        if isinstance(raw, int):
            return struct.pack(">i", raw)
        return str(raw).encode("utf-8")

    def _decode_from(self, data: bytes) -> None:
        self._encoded = data


class HLAfederateHandle(_EncodedValueElement[FederateHandle]): ...
class HLAobjectClassHandle(_EncodedValueElement[ObjectClassHandle]): ...
class HLAinteractionClassHandle(_EncodedValueElement[InteractionClassHandle]): ...
class HLAobjectInstanceHandle(_EncodedValueElement[ObjectInstanceHandle]): ...
class HLAattributeHandle(_EncodedValueElement[AttributeHandle]): ...
class HLAparameterHandle(_EncodedValueElement[ParameterHandle]): ...
class HLAdimensionHandle(_EncodedValueElement[DimensionHandle]): ...
class HLAmessageRetractionHandle(_EncodedValueElement[MessageRetractionHandle]): ...
class HLAregionHandle(_EncodedValueElement[RegionHandle]): ...
class HLAtransportationTypeHandle(_EncodedValueElement[TransportationTypeHandle]): ...
class HLAlogicalTime(_EncodedValueElement[LT], Generic[LT, LTI]): ...
class HLAlogicalTimeInterval(_EncodedValueElement[LTI], Generic[LT, LTI]): ...


class CallableDataElementFactory(Generic[D]):
    def __init__(self, create: Callable[[int], D] | Callable[[], D]) -> None:
        self._create = create

    def createElement(self, index: int = 0) -> D:  # noqa: N802
        try:
            return self._create(index)  # type: ignore[misc]
        except TypeError:
            return self._create()  # type: ignore[call-arg,no-any-return]


class BasicEncoderFactory:
    """Default Python implementation of the IEEE 1516.1-2025 EncoderFactory surface."""

    def createHLAfixedArray(self, factoryOrFirstElement: DataElementFactory[D] | D, sizeOrSecondElement: int | D | None = None, *elements: D) -> HLAfixedArray[D]:  # noqa: N802
        if isinstance(sizeOrSecondElement, int):
            factory = factoryOrFirstElement
            created = [factory.createElement(index) for index in range(sizeOrSecondElement)]  # type: ignore[attr-defined]
            return HLAfixedArray(created)
        sequence = [factoryOrFirstElement]
        if sizeOrSecondElement is not None:
            sequence.append(sizeOrSecondElement)
        sequence.extend(elements)
        return HLAfixedArray(sequence)  # type: ignore[arg-type]

    def createHLAvariableArray(self, factory: DataElementFactory[D], *elements: D) -> HLAvariableArray[D]:  # noqa: N802
        return HLAvariableArray(elements)

    def createHLAfixedRecord(self) -> HLAfixedRecord:  # noqa: N802
        return HLAfixedRecord()

    def createHLAvariantRecord(self, discriminant: D) -> HLAvariantRecord[D]:  # noqa: N802
        return HLAvariantRecord(discriminant)

    def createHLAextendableVariantRecord(self, discriminant: D) -> HLAextendableVariantRecord[D]:  # noqa: N802
        return HLAextendableVariantRecord(discriminant)

    def createHLAfederateHandle(self, rtiAmbassador: Any, federateHandle: FederateHandle | None = None) -> HLAfederateHandle:  # noqa: N802
        return HLAfederateHandle(federateHandle)

    def createHLAobjectClassHandle(self, rtiAmbassador: Any, objectClassHandle: ObjectClassHandle | None = None) -> HLAobjectClassHandle:  # noqa: N802
        return HLAobjectClassHandle(objectClassHandle)

    def createHLAinteractionClassHandle(self, rtiAmbassador: Any, interactionClassHandle: InteractionClassHandle | None = None) -> HLAinteractionClassHandle:  # noqa: N802
        return HLAinteractionClassHandle(interactionClassHandle)

    def createHLAobjectInstanceHandle(self, rtiAmbassador: Any, objectInstanceHandle: ObjectInstanceHandle | None = None) -> HLAobjectInstanceHandle:  # noqa: N802
        return HLAobjectInstanceHandle(objectInstanceHandle)

    def createHLAattributeHandle(self, rtiAmbassador: Any, attributeHandle: AttributeHandle | None = None) -> HLAattributeHandle:  # noqa: N802
        return HLAattributeHandle(attributeHandle)

    def createHLAparameterHandle(self, rtiAmbassador: Any, parameterHandle: ParameterHandle | None = None) -> HLAparameterHandle:  # noqa: N802
        return HLAparameterHandle(parameterHandle)

    def createHLAdimensionHandle(self, rtiAmbassador: Any, dimensionHandle: DimensionHandle | None = None) -> HLAdimensionHandle:  # noqa: N802
        return HLAdimensionHandle(dimensionHandle)

    def createHLAmessageRetractionHandle(self, rtiAmbassador: Any, messageRetractionHandle: MessageRetractionHandle | None = None) -> HLAmessageRetractionHandle:  # noqa: N802
        return HLAmessageRetractionHandle(messageRetractionHandle)

    def createHLAregionHandle(self, rtiAmbassador: Any, regionHandle: RegionHandle | None = None) -> HLAregionHandle:  # noqa: N802
        return HLAregionHandle(regionHandle)

    def createHLAtransportationTypeHandle(self, rtiAmbassador: Any, transportationTypeHandle: TransportationTypeHandle | None = None) -> HLAtransportationTypeHandle:  # noqa: N802
        return HLAtransportationTypeHandle(transportationTypeHandle)

    def createHLAlogicalTime(self, rtiAmbassador: Any, logicalTime: LT | None = None) -> HLAlogicalTime[LT, Any]:  # noqa: N802
        return HLAlogicalTime(logicalTime)

    def createHLAlogicalTimeInterval(self, rtiAmbassador: Any, logicalTimeInterval: LTI | None = None) -> HLAlogicalTimeInterval[Any, LTI]:  # noqa: N802
        return HLAlogicalTimeInterval(logicalTimeInterval)


_PRIMITIVE_FACTORIES: dict[str, type[_DataElement]] = {
    name: cls
    for name, cls in {
        "HLAASCIIchar": HLAASCIIchar,
        "HLAASCIIstring": HLAASCIIstring,
        "HLAboolean": HLAboolean,
        "HLAbyte": HLAbyte,
        "HLAfloat32BE": HLAfloat32BE,
        "HLAfloat32LE": HLAfloat32LE,
        "HLAfloat64BE": HLAfloat64BE,
        "HLAfloat64LE": HLAfloat64LE,
        "HLAinteger16BE": HLAinteger16BE,
        "HLAinteger16LE": HLAinteger16LE,
        "HLAinteger32BE": HLAinteger32BE,
        "HLAinteger32LE": HLAinteger32LE,
        "HLAinteger64BE": HLAinteger64BE,
        "HLAinteger64LE": HLAinteger64LE,
        "HLAunsignedInteger16BE": HLAunsignedInteger16BE,
        "HLAunsignedInteger16LE": HLAunsignedInteger16LE,
        "HLAunsignedInteger32BE": HLAunsignedInteger32BE,
        "HLAunsignedInteger32LE": HLAunsignedInteger32LE,
        "HLAunsignedInteger64BE": HLAunsignedInteger64BE,
        "HLAunsignedInteger64LE": HLAunsignedInteger64LE,
        "HLAoctet": HLAoctet,
        "HLAoctetPairBE": HLAoctetPairBE,
        "HLAoctetPairLE": HLAoctetPairLE,
        "HLAopaqueData": HLAopaqueData,
        "HLAunicodeChar": HLAunicodeChar,
        "HLAunicodeString": HLAunicodeString,
    }.items()
}


def _install_primitive_factory(method_name: str, element_type: type[_DataElement]) -> None:
    def _factory(self: BasicEncoderFactory, value: Any | None = None) -> _DataElement:
        return element_type() if value is None else element_type(value)

    _factory.__name__ = method_name
    setattr(BasicEncoderFactory, method_name, _factory)


for _element_name, _element_type in _PRIMITIVE_FACTORIES.items():
    _install_primitive_factory(f"create{_element_name}", _element_type)


def create_encoder_factory() -> BasicEncoderFactory:
    return BasicEncoderFactory()


__all__ = [
    "BasicEncoderFactory",
    "CallableDataElementFactory",
    "DataElement",
    "DataElementFactory",
    "DecoderException",
    "EncoderException",
    "EncoderFactory",
    "HLAASCIIchar",
    "HLAASCIIstring",
    "HLAattributeHandle",
    "HLAboolean",
    "HLAbyte",
    "HLAdimensionHandle",
    "HLAextendableVariantRecord",
    "HLAfederateHandle",
    "HLAfixedArray",
    "HLAfixedRecord",
    "HLAfloat32BE",
    "HLAfloat32LE",
    "HLAfloat64BE",
    "HLAfloat64LE",
    "HLAinteger16BE",
    "HLAinteger16LE",
    "HLAinteger32BE",
    "HLAinteger32LE",
    "HLAinteger64BE",
    "HLAinteger64LE",
    "HLAinteractionClassHandle",
    "HLAlogicalTime",
    "HLAlogicalTimeInterval",
    "HLAmessageRetractionHandle",
    "HLAobjectClassHandle",
    "HLAobjectInstanceHandle",
    "HLAoctet",
    "HLAoctetPairBE",
    "HLAoctetPairLE",
    "HLAopaqueData",
    "HLAparameterHandle",
    "HLAregionHandle",
    "HLAtransportationTypeHandle",
    "HLAunicodeChar",
    "HLAunicodeString",
    "HLAunsignedInteger16BE",
    "HLAunsignedInteger16LE",
    "HLAunsignedInteger32BE",
    "HLAunsignedInteger32LE",
    "HLAunsignedInteger64BE",
    "HLAunsignedInteger64LE",
    "HLAvariableArray",
    "HLAvariantRecord",
    "SimpleByteWrapper",
    "SimpleVariableLengthData",
    "ValueDataElement",
    "VariableLengthData",
    "create_encoder_factory",
]
