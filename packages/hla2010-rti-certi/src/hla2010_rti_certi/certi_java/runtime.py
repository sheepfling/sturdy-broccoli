"""Runtime conversion helpers for Java-profile CERTI backends."""
from __future__ import annotations

from enum import Enum
from typing import Any

from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla2010_rti_java_common.java_common import JavaValueConverter
from hla2010_rti_java_common.java_shim_types import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaEnumConstant,
    JavaFederateHandle,
    JavaHLAinteger64Interval,
    JavaHLAinteger64Time,
    JavaInteractionClassHandle,
    JavaLikeObject,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
    JavaParameterHandle,
    JavaTransportationTypeHandle,
)


def python_bytes(value: Any) -> bytes:
    if isinstance(value, JavaByteArray):
        return bytes((int(item) + 256) % 256 for item in value)
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return bytes((int(item) + 256) % 256 for item in value)


def from_java_like(value: Any) -> Any:
    if isinstance(value, JavaByteArray):
        return python_bytes(value)
    if isinstance(value, dict):
        return {from_java_like(key): from_java_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [from_java_like(item) for item in value]
    if isinstance(value, tuple):
        return tuple(from_java_like(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return {from_java_like(item) for item in value}
    if isinstance(value, JavaFederateHandle):
        return FederateHandle(int(value.value))
    if isinstance(value, JavaObjectClassHandle):
        return ObjectClassHandle(int(value.value))
    if isinstance(value, JavaAttributeHandle):
        return AttributeHandle(int(value.value))
    if isinstance(value, JavaObjectInstanceHandle):
        return ObjectInstanceHandle(int(value.value))
    if isinstance(value, JavaInteractionClassHandle):
        return InteractionClassHandle(int(value.value))
    if isinstance(value, JavaParameterHandle):
        return ParameterHandle(int(value.value))
    if isinstance(value, JavaTransportationTypeHandle):
        return TransportationTypeHandle(int(value.value))
    if isinstance(value, JavaHLAinteger64Time):
        return HLAinteger64Time(int(value.value))
    if isinstance(value, JavaHLAinteger64Interval):
        return HLAinteger64Interval(int(value.value))
    if isinstance(value, JavaLikeObject):
        if value.simple_name == "HLAfloat64Time":
            return HLAfloat64Time(float(value.value))
        if value.simple_name == "HLAfloat64Interval":
            return HLAfloat64Interval(float(value.value))
        if value.simple_name == "CallbackModel":
            return CallbackModel[str(value.value)]
        if value.simple_name == "OrderType":
            return OrderType[str(value.value)]
        if value.simple_name == "ResignAction":
            return ResignAction[str(value.value)]
    return value


def to_java_like(value: Any) -> Any:
    if isinstance(value, bytes):
        return JavaByteArray(value)
    if isinstance(value, bytearray):
        return JavaByteArray(bytes(value))
    if isinstance(value, memoryview):
        return JavaByteArray(value.tobytes())
    if isinstance(value, dict):
        return {to_java_like(key): to_java_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_java_like(item) for item in value]
    if isinstance(value, tuple):
        return tuple(to_java_like(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return {to_java_like(item) for item in value}
    if isinstance(value, FederateHandle):
        return JavaFederateHandle(int(value.value))
    if isinstance(value, ObjectClassHandle):
        return JavaObjectClassHandle(int(value.value))
    if isinstance(value, AttributeHandle):
        return JavaAttributeHandle(int(value.value))
    if isinstance(value, ObjectInstanceHandle):
        return JavaObjectInstanceHandle(int(value.value))
    if isinstance(value, InteractionClassHandle):
        return JavaInteractionClassHandle(int(value.value))
    if isinstance(value, ParameterHandle):
        return JavaParameterHandle(int(value.value))
    if isinstance(value, TransportationTypeHandle):
        return JavaTransportationTypeHandle(int(value.value))
    if isinstance(value, HLAinteger64Time):
        return JavaHLAinteger64Time(int(value.value))
    if isinstance(value, HLAinteger64Interval):
        return JavaHLAinteger64Interval(int(value.value))
    if isinstance(value, HLAfloat64Time):
        return JavaLikeObject("HLAfloat64Time", float(value.value))
    if isinstance(value, HLAfloat64Interval):
        return JavaLikeObject("HLAfloat64Interval", float(value.value))
    if isinstance(value, Enum):
        return JavaEnumConstant(type(value).__name__, value.name)
    return value


class CERTIJavaValueConverter(JavaValueConverter):
    """Converter for the CERTI Java-profile shim that preserves numeric handles."""

    def to_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if isinstance(value, FederateHandle):
            return JavaFederateHandle(int(value.value))
        if isinstance(value, ObjectClassHandle):
            return JavaObjectClassHandle(int(value.value))
        if isinstance(value, AttributeHandle):
            return JavaAttributeHandle(int(value.value))
        if isinstance(value, ObjectInstanceHandle):
            return JavaObjectInstanceHandle(int(value.value))
        if isinstance(value, InteractionClassHandle):
            return JavaInteractionClassHandle(int(value.value))
        if isinstance(value, ParameterHandle):
            return JavaParameterHandle(int(value.value))
        if isinstance(value, TransportationTypeHandle):
            return JavaTransportationTypeHandle(int(value.value))
        return super().to_backend(value, expected_type_name=expected_type_name)

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if isinstance(value, JavaFederateHandle):
            return FederateHandle(int(value.value))
        if isinstance(value, JavaObjectClassHandle):
            return ObjectClassHandle(int(value.value))
        if isinstance(value, JavaAttributeHandle):
            return AttributeHandle(int(value.value))
        if isinstance(value, JavaObjectInstanceHandle):
            return ObjectInstanceHandle(int(value.value))
        if isinstance(value, JavaInteractionClassHandle):
            return InteractionClassHandle(int(value.value))
        if isinstance(value, JavaParameterHandle):
            return ParameterHandle(int(value.value))
        if isinstance(value, JavaTransportationTypeHandle):
            return TransportationTypeHandle(int(value.value))
        return super().from_backend(value, expected_type_name=expected_type_name)


__all__ = [
    "CERTIJavaValueConverter",
    "from_java_like",
    "python_bytes",
    "to_java_like",
]
