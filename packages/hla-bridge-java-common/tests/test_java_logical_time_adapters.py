from __future__ import annotations

import struct
from typing import Any

from hla.bridges.java.common.java_binding_profile import load_python_java_binding_profile
from hla.bridges.java.common.java_bridge_base import JavaBridge
from hla.bridges.java.common.java_logical_time import (
    JavaLogicalTimeAdapter,
    JavaLogicalTimeFactoryAdapter,
    wrap_java_logical_time_factory,
)
from hla.bridges.java.common.java_shim_backend import InProcessJavaRTIShim, ShimJavaBridge
from hla.bridges.java.common.java_value_adapter import HLAJavaValueAdapter
from hla.rti1516e.time import HLAfloat64Time, HLAinteger64Time


class _FakeClass:
    def __init__(self, name: str) -> None:
        self._name = name

    def getName(self) -> str:
        return self._name

    def getSimpleName(self) -> str:
        return self._name.rsplit(".", 1)[-1]


class _FakeJavaTime:
    def __init__(self, factory_name: str, value: int | float, *, interval: bool = False) -> None:
        self.factory_name = factory_name
        self.value = value
        self.interval = interval

    def getClass(self) -> _FakeClass:
        suffix = "Interval" if self.interval else "Time"
        return _FakeClass(f"vendor.{self.factory_name}{suffix}")

    def encodedLength(self) -> int:
        return 8

    def encode(self, buffer: bytearray, offset: int) -> None:
        if self.factory_name == "HLAfloat64Time":
            buffer[offset : offset + 8] = struct.pack(">d", float(self.value))
        else:
            buffer[offset : offset + 8] = struct.pack(">q", int(self.value))

    def compareTo(self, other: "_FakeJavaTime") -> int:
        return (self.value > other.value) - (self.value < other.value)

    def isInitial(self) -> bool:
        return self.value == 0

    def isFinal(self) -> bool:
        return self.value == 2**63 - 1

    def isZero(self) -> bool:
        return self.value == 0

    def isEpsilon(self) -> bool:
        return self.value == 1

    def add(self, interval: "_FakeJavaTime") -> "_FakeJavaTime":
        return _FakeJavaTime(self.factory_name, self.value + interval.value, interval=self.interval)

    def subtract(self, interval: "_FakeJavaTime") -> "_FakeJavaTime":
        return _FakeJavaTime(self.factory_name, self.value - interval.value, interval=self.interval)

    def distance(self, other: "_FakeJavaTime") -> "_FakeJavaTime":
        return _FakeJavaTime(self.factory_name, self.value - other.value, interval=True)


class _FakeJavaTimeFactory:
    def __init__(self, name: str) -> None:
        self.name = name
        self.decoded_time_bytes: bytes | None = None
        self.decoded_interval_bytes: bytes | None = None

    def getName(self) -> str:
        return self.name

    def decodeTime(self, buffer: bytes | bytearray, offset: int = 0) -> _FakeJavaTime:
        self.decoded_time_bytes = bytes(buffer[offset : offset + 8])
        if self.name == "HLAfloat64Time":
            return _FakeJavaTime(self.name, struct.unpack(">d", self.decoded_time_bytes)[0])
        return _FakeJavaTime(self.name, struct.unpack(">q", self.decoded_time_bytes)[0])

    def decodeInterval(self, buffer: bytes | bytearray, offset: int = 0) -> _FakeJavaTime:
        self.decoded_interval_bytes = bytes(buffer[offset : offset + 8])
        if self.name == "HLAfloat64Time":
            return _FakeJavaTime(self.name, struct.unpack(">d", self.decoded_interval_bytes)[0], interval=True)
        return _FakeJavaTime(self.name, struct.unpack(">q", self.decoded_interval_bytes)[0], interval=True)

    def makeInitial(self) -> _FakeJavaTime:
        return _FakeJavaTime(self.name, 0)

    def makeFinal(self) -> _FakeJavaTime:
        return _FakeJavaTime(self.name, 2**63 - 1)

    def makeZero(self) -> _FakeJavaTime:
        return _FakeJavaTime(self.name, 0, interval=True)

    def makeEpsilon(self) -> _FakeJavaTime:
        return _FakeJavaTime(self.name, 1, interval=True)


class _FakeRti:
    def __init__(self, factory: _FakeJavaTimeFactory) -> None:
        self.factory = factory

    def getTimeFactory(self) -> _FakeJavaTimeFactory:
        return self.factory


class _FakeBridge(JavaBridge):
    def __init__(self) -> None:
        super().__init__("2010")

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: Any) -> Any:
        return dispatcher

    def byte_array(self, data: bytes) -> bytearray:
        return bytearray(data)


def test_builtin_java_factory_decodes_to_native_python_time() -> None:
    bridge = _FakeBridge()
    factory = wrap_java_logical_time_factory(
        bridge,
        _FakeJavaTimeFactory("HLAinteger64Time"),
        load_python_java_binding_profile("2010"),
    )

    value = factory.decodeTime(struct.pack(">q", 42))

    assert isinstance(value, HLAinteger64Time)
    assert value.value == 42


def test_builtin_float_java_factory_decodes_to_native_python_time() -> None:
    bridge = _FakeBridge()
    factory = wrap_java_logical_time_factory(
        bridge,
        _FakeJavaTimeFactory("HLAfloat64Time"),
        load_python_java_binding_profile("2010"),
    )

    value = factory.decodeTime(struct.pack(">d", 42.5))

    assert isinstance(value, HLAfloat64Time)
    assert value.value == 42.5


def test_custom_java_factory_returns_opaque_python_wrapper() -> None:
    bridge = _FakeBridge()
    factory = wrap_java_logical_time_factory(
        bridge,
        _FakeJavaTimeFactory("Custom128Time"),
        load_python_java_binding_profile("2010"),
    )

    value = factory.decodeTime(struct.pack(">q", 42))
    interval = factory.decodeInterval(struct.pack(">q", 3))

    assert isinstance(value, JavaLogicalTimeAdapter)
    assert value.factory_name == "Custom128Time"
    assert bytes(value.encode()) == struct.pack(">q", 42)
    assert str(value.add(interval).factory_name) == "Custom128Time"


def test_value_adapter_wraps_get_time_factory_return() -> None:
    bridge = _FakeBridge()
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=_FakeRti(_FakeJavaTimeFactory("HLAinteger64Time")))

    wrapped = converter.from_backend(converter.rti_ambassador.getTimeFactory(), expected_type_name="LogicalTimeFactory")

    assert isinstance(wrapped, JavaLogicalTimeFactoryAdapter)
    assert wrapped.getName() == "HLAinteger64Time"


def test_to_backend_uses_current_java_factory_decode_path() -> None:
    bridge = _FakeBridge()
    java_factory = _FakeJavaTimeFactory("HLAinteger64Time")
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=_FakeRti(java_factory))

    java_value = converter.to_backend(HLAinteger64Time(77), expected_type_name="LogicalTime")

    assert isinstance(java_value, _FakeJavaTime)
    assert java_value.value == 77
    assert java_factory.decoded_time_bytes == struct.pack(">q", 77)


def test_to_backend_float_uses_current_java_factory_decode_path() -> None:
    bridge = _FakeBridge()
    java_factory = _FakeJavaTimeFactory("HLAfloat64Time")
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=_FakeRti(java_factory))

    java_value = converter.to_backend(HLAfloat64Time(77.5), expected_type_name="LogicalTime")

    assert isinstance(java_value, _FakeJavaTime)
    assert java_value.value == 77.5
    assert java_factory.decoded_time_bytes == struct.pack(">d", 77.5)


def test_inprocess_java_shim_exposes_wrappable_time_factory() -> None:
    shim = InProcessJavaRTIShim()
    shim.connect(object(), object())
    bridge = ShimJavaBridge("jpype")
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=shim)

    wrapped = converter.from_backend(shim.getTimeFactory(), expected_type_name="LogicalTimeFactory")
    java_value = converter.to_backend(HLAinteger64Time(99), expected_type_name="LogicalTime")

    assert wrapped.getName() == "HLAinteger64Time"
    assert java_value.getValue() == 99


def test_inprocess_java_shim_float_factory_round_trips_time() -> None:
    shim = InProcessJavaRTIShim()
    shim.connect(object(), object())
    shim.createFederationExecution("federation", "HLAfloat64Time")
    shim.joinFederationExecution("federate", "type", "federation")
    bridge = ShimJavaBridge("jpype")
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=shim)

    wrapped = converter.from_backend(shim.getTimeFactory(), expected_type_name="LogicalTimeFactory")
    java_value = converter.to_backend(HLAfloat64Time(12.25), expected_type_name="LogicalTime")

    assert wrapped.getName() == "HLAfloat64Time"
    assert java_value.getValue() == 12.25


def test_inprocess_java_shim_py4j_profile_uses_same_time_factory_path() -> None:
    shim = InProcessJavaRTIShim()
    shim.connect(object(), object())
    bridge = ShimJavaBridge("py4j")
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=shim)

    wrapped = converter.from_backend(shim.getTimeFactory(), expected_type_name="LogicalTimeFactory")
    java_value = converter.to_backend(HLAinteger64Time(33), expected_type_name="LogicalTime")

    assert wrapped.getName() == "HLAinteger64Time"
    assert java_value.getValue() == 33
