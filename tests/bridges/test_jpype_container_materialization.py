from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Generic, TypeVar

from hla.bridges.java.common.java_binding_profile import load_python_java_binding_profile
from hla.bridges.java.jpype.runtime import JPypeBridge


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


class _FakeJPypeModule:
    JByte = "JByte"

    def JClass(self, class_name: str) -> Any:
        mapping = {
            "java.util.HashSet": _FakeHashSet,
            "java.util.ArrayList": _FakeArrayList,
            "java.util.HashMap": _FakeHashMap,
        }
        return mapping[class_name]

    def JArray(self, component: Any) -> Any:
        def _factory(values: list[Any]) -> tuple[Any, tuple[Any, ...]]:
            return (component, tuple(values))

        return _factory


def _bridge() -> JPypeBridge:
    bridge = object.__new__(JPypeBridge)
    bridge.jpype = _FakeJPypeModule()
    bridge.python_binding = load_python_java_binding_profile("2010")
    bridge.api_profile = bridge.python_binding.api_profile
    bridge.config = SimpleNamespace()
    bridge.started_here = False
    return bridge


def test_jpype_bridge_materializes_byte_arrays_with_signed_octets() -> None:
    bridge = _bridge()

    assert bridge.byte_array(bytes([0, 127, 128, 255])) == ("JByte", (0, 127, -128, -1))


def test_jpype_bridge_materializes_generic_java_collections() -> None:
    bridge = _bridge()

    java_set = bridge.new_set(["alpha", "beta"])
    java_list = bridge.new_list(["alpha", "beta"])
    java_map = bridge.new_map([("alpha", "beta")])

    assert isinstance(java_set, _FakeHashSet)
    assert java_set.values == ["alpha", "beta"]
    assert isinstance(java_list, _FakeArrayList)
    assert java_list.values == ["alpha", "beta"]
    assert isinstance(java_map, _FakeHashMap)
    assert java_map.items == [("alpha", "beta")]
