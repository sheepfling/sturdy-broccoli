"""Java-shaped value types and conversion helpers for shim backends."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from hla2010.time import HLAfloat64Time, HLAinteger64Time


class JavaClassInfo:
    def __init__(self, simple_name: str, package: str = "hla.rti1516e") -> None:
        self._simple_name = simple_name
        self._package = package

    def getSimpleName(self) -> str:
        return self._simple_name

    def getName(self) -> str:
        if self._simple_name == "byte[]":
            return "[B"
        return f"{self._package}.{self._simple_name}"


@dataclass(eq=False)
class JavaLikeObject:
    simple_name: str
    value: Any = None

    def getClass(self) -> JavaClassInfo:
        return JavaClassInfo(self.simple_name)

    def getValue(self) -> Any:
        return self.value

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{self.simple_name}({self.value!r})"


class JavaLikeException(RuntimeError):
    def __init__(self, simple_name: str, message: str):
        super().__init__(message)
        self.simple_name = simple_name
        self.message = message

    def getClass(self) -> JavaClassInfo:
        return JavaClassInfo(self.simple_name, package="hla.rti1516e.exceptions")

    def getMessage(self) -> str:
        return self.message


class JavaEnumConstant(JavaLikeObject):
    def __init__(self, enum_simple_name: str, member_name: str):
        super().__init__(enum_simple_name, member_name)
        self._member_name = member_name

    def name(self) -> str:
        return self._member_name

    def __repr__(self) -> str:
        return f"{self.simple_name}.{self._member_name}"


class JavaByteArray(JavaLikeObject):
    def __init__(self, data: bytes):
        super().__init__("byte[]", bytes(data))

    def __iter__(self):
        for item in self.value:
            yield item if item < 128 else item - 256

    def __len__(self) -> int:
        return len(self.value)


class JavaFederateHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("FederateHandle", value)


class JavaObjectClassHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("ObjectClassHandle", value)


class JavaAttributeHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("AttributeHandle", value)


class JavaObjectInstanceHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("ObjectInstanceHandle", value)


class JavaInteractionClassHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("InteractionClassHandle", value)


class JavaParameterHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("ParameterHandle", value)


class JavaDimensionHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("DimensionHandle", value)


class JavaRegionHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("RegionHandle", value)


class JavaTransportationTypeHandle(JavaLikeObject):
    def __init__(self, value: int): super().__init__("TransportationTypeHandle", value)


class JavaHLAinteger64Time(JavaLikeObject):
    def __init__(self, value: int): super().__init__("HLAinteger64Time", int(value))


class JavaHLAinteger64Interval(JavaLikeObject):
    def __init__(self, value: int): super().__init__("HLAinteger64Interval", int(value))


class JavaHLAfloat64Time(JavaLikeObject):
    def __init__(self, value: float): super().__init__("HLAfloat64Time", float(value))


class JavaHLAfloat64Interval(JavaLikeObject):
    def __init__(self, value: float): super().__init__("HLAfloat64Interval", float(value))


class JavaRangeBounds(JavaLikeObject):
    def __init__(self, lower_bound: int, upper_bound: int):
        super().__init__("RangeBounds", (int(lower_bound), int(upper_bound)))

    def getLowerBound(self) -> int:
        return int(self.value[0])

    def getUpperBound(self) -> int:
        return int(self.value[1])


def enum_name(value: Any) -> str:
    if isinstance(value, Enum):
        return value.name
    if hasattr(value, "name") and callable(value.name):
        return str(value.name())
    if isinstance(value, JavaLikeObject):
        return str(value.value)
    return str(value)


def python_bytes(value: Any) -> bytes:
    if isinstance(value, JavaByteArray):
        return bytes((int(item) + 256) % 256 for item in value)
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    try:
        return bytes((int(item) + 256) % 256 for item in value)
    except Exception:
        return bytes(str(value), "utf-8")


def logical_time_name(value: Any, default: str = "HLAinteger64Time") -> str:
    if isinstance(value, HLAinteger64Time | JavaHLAinteger64Time):
        return "HLAinteger64Time"
    if isinstance(value, HLAfloat64Time | JavaHLAfloat64Time):
        return "HLAfloat64Time"
    simple_name = getattr(value, "simple_name", None)
    if simple_name in {"HLAinteger64Time", "HLAfloat64Time"}:
        return str(simple_name)
    return default


def make_java_time(type_name: str, value: Any) -> JavaLikeObject:
    if type_name == "HLAfloat64Time":
        return JavaHLAfloat64Time(float(value))
    return JavaHLAinteger64Time(int(value))


def time_value(value: Any) -> int | float:
    if isinstance(value, HLAinteger64Time):
        return int(value.value)
    if isinstance(value, HLAfloat64Time):
        return float(value.value)
    if isinstance(value, JavaHLAinteger64Time):
        return int(value.value)
    if isinstance(value, JavaHLAfloat64Time):
        return float(value.value)
    if hasattr(value, "getValue"):
        raw = value.getValue()
        if logical_time_name(value, "") == "HLAfloat64Time":
            return float(raw)
        return int(raw)
    if isinstance(value, float):
        return float(value)
    return int(value)


__all__ = [
    "JavaAttributeHandle",
    "JavaByteArray",
    "JavaClassInfo",
    "JavaDimensionHandle",
    "JavaEnumConstant",
    "JavaFederateHandle",
    "JavaHLAfloat64Interval",
    "JavaHLAfloat64Time",
    "JavaHLAinteger64Interval",
    "JavaHLAinteger64Time",
    "JavaInteractionClassHandle",
    "JavaLikeException",
    "JavaLikeObject",
    "JavaObjectClassHandle",
    "JavaObjectInstanceHandle",
    "JavaParameterHandle",
    "JavaRangeBounds",
    "JavaRegionHandle",
    "JavaTransportationTypeHandle",
    "enum_name",
    "logical_time_name",
    "make_java_time",
    "python_bytes",
    "time_value",
]
