from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Generic, TypeVar

from hla.bridges.java.py4j.runtime import Py4JBridge, Py4JConfig


_ValueT = TypeVar("_ValueT")
_KeyT = TypeVar("_KeyT")
_MappedT = TypeVar("_MappedT")


class _FakeHashSet(Generic[_ValueT]):
    def __init__(self) -> None:
        self.values: list[_ValueT] = []

    def add(self, value: _ValueT) -> None:
        self.values.append(value)


class _FakeArrayList(Generic[_ValueT]):
    def __init__(self) -> None:
        self.values: list[_ValueT] = []

    def add(self, value: _ValueT) -> None:
        self.values.append(value)


class _FakeHashMap(Generic[_KeyT, _MappedT]):
    def __init__(self) -> None:
        self.items: list[tuple[_KeyT, _MappedT]] = []

    def put(self, key: _KeyT, value: _MappedT) -> None:
        self.items.append((key, value))


class _FakeGateway:
    def __init__(self) -> None:
        self.jvm = SimpleNamespace(
            Byte=SimpleNamespace(TYPE="BYTE_TYPE"),
            java=SimpleNamespace(
                util=SimpleNamespace(
                    HashSet=_FakeHashSet,
                    ArrayList=_FakeArrayList,
                    HashMap=_FakeHashMap,
                )
            ),
        )

    def new_array(self, component: Any, size: int) -> list[Any]:
        return [None] * size


def test_py4j_bridge_materializes_byte_arrays_with_signed_octets() -> None:
    bridge = Py4JBridge(Py4JConfig(gateway=_FakeGateway()))

    assert bridge.byte_array(bytes([0, 127, 128, 255])) == [0, 127, -128, -1]


def test_py4j_bridge_materializes_generic_java_collections() -> None:
    bridge = Py4JBridge(Py4JConfig(gateway=_FakeGateway()))

    java_set = bridge.new_set(["alpha", "beta"])
    java_list = bridge.new_list(["alpha", "beta"])
    java_map = bridge.new_map([("alpha", "beta")])

    assert isinstance(java_set, _FakeHashSet)
    assert java_set.values == ["alpha", "beta"]
    assert isinstance(java_list, _FakeArrayList)
    assert java_list.values == ["alpha", "beta"]
    assert isinstance(java_map, _FakeHashMap)
    assert java_map.items == [("alpha", "beta")]
