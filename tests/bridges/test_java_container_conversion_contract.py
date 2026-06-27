from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import pytest

from hla.bridges.java.common import GenericJavaValueAdapter, HLAJavaValueAdapter, JavaBridge
from hla.foms.target_radar._internal import target_radar_fom_path
from hla.rti1516e.datatypes import AttributeRegionAssociation
from hla.rti1516e.handles import (
    AttributeHandle,
    AttributeHandleSet,
    ParameterHandle,
    RegionHandle,
    RegionHandleSet,
)


TARGET_RADAR_FOM = target_radar_fom_path()


_ValueT = TypeVar("_ValueT")
_KeyT = TypeVar("_KeyT")
_MappedT = TypeVar("_MappedT")


@dataclass(frozen=True)
class _FakeJavaCollection(Generic[_ValueT]):
    kind: str
    values: tuple[_ValueT, ...]


@dataclass(frozen=True)
class _FakeJavaMap(Generic[_KeyT, _MappedT]):
    items: tuple[tuple[_KeyT, _MappedT], ...]


class _ContractBridge(JavaBridge):
    def __init__(self, route_name: str) -> None:
        super().__init__("2010")
        self.route_name = route_name

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: Any) -> Any:
        return dispatcher

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        return (enum_class_name, member_name)

    def byte_array(self, data: bytes) -> Any:
        return ("byte_array", self.route_name, tuple(data))

    def is_byte_array(self, value: Any) -> bool:
        return isinstance(value, tuple) and len(value) == 3 and value[0] == "byte_array"

    def to_python_bytes(self, value: Any) -> bytes:
        if self.is_byte_array(value):
            return bytes(value[2])
        return super().to_python_bytes(value)

    def fom_url(self, value: Any) -> Any:
        return f"{self.route_name}:url:{value}"

    def fom_url_array(self, values: Sequence[Any]) -> Any:
        return _FakeJavaCollection("URL[]", tuple(self.fom_url(value) for value in values))

    def new_set(self, values: Sequence[Any]) -> Any:
        return _FakeJavaCollection("HashSet", tuple(values))

    def new_list(self, values: Sequence[Any]) -> Any:
        return _FakeJavaCollection("ArrayList", tuple(values))

    def new_map(self, items: Sequence[tuple[Any, Any]]) -> Any:
        return _FakeJavaMap(tuple(items))

    def new_handle_set(self, type_name: str, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        return _FakeJavaCollection(type_name, tuple(values))

    def new_handle_value_map(
        self,
        type_name: str,
        items: Sequence[tuple[Any, Any]],
        *,
        rti_ambassador: Any | None = None,
    ) -> Any:
        return _FakeJavaMap((("type_name", type_name), *tuple(items)))

    def new_attribute_set_region_set_pair_list(self, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        return _FakeJavaCollection("AttributeSetRegionSetPairList", tuple(values))

    def java_map_items(self, value: Any) -> Sequence[tuple[Any, Any]] | None:
        if isinstance(value, _FakeJavaMap):
            if value.items and value.items[0][0] == "type_name":
                return list(value.items[1:])
            return list(value.items)
        return super().java_map_items(value)

    def java_collection_values(self, value: Any) -> Sequence[Any] | None:
        if isinstance(value, _FakeJavaCollection):
            return list(value.values)
        return super().java_collection_values(value)

    def simple_class_name(self, obj: Any) -> str | None:
        if isinstance(obj, _FakeJavaCollection):
            return obj.kind
        if isinstance(obj, _FakeJavaMap):
            return "HashMap"
        return super().simple_class_name(obj)


@pytest.fixture(params=["jpype-like", "py4j-like"])
def contract_converter(request: pytest.FixtureRequest) -> HLAJavaValueAdapter:
    return HLAJavaValueAdapter(_ContractBridge(str(request.param)), rti_ambassador=object())


@pytest.fixture(params=["jpype-like", "py4j-like"])
def generic_converter(request: pytest.FixtureRequest) -> GenericJavaValueAdapter:
    return GenericJavaValueAdapter(_ContractBridge(str(request.param)))


def test_explicit_standard_java_container_families_are_wrapped_centrally(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter
    native_attr = ("native-attribute", 1)
    native_param = ("native-parameter", 2)
    native_region = ("native-region", 3)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)
    py_param = converter.handle_registry.to_python(ParameterHandle, native_param)
    py_region = converter.handle_registry.to_python(RegionHandle, native_region)

    assert converter.to_backend([TARGET_RADAR_FOM], expected_type_name="URL[]") == _FakeJavaCollection(
        "URL[]",
        (f"{converter.bridge.route_name}:url:{TARGET_RADAR_FOM}",),
    )
    assert converter.to_backend({py_attr}, expected_type_name="AttributeHandleSet") == _FakeJavaCollection(
        "AttributeHandleSet",
        (native_attr,),
    )
    assert converter.to_backend({py_attr: b"abc"}, expected_type_name="AttributeHandleValueMap") == _FakeJavaMap(
        (("type_name", "AttributeHandleValueMap"), (native_attr, ("byte_array", converter.bridge.route_name, (97, 98, 99)))),
    )
    assert converter.to_backend({py_param: b"xyz"}, expected_type_name="ParameterHandleValueMap") == _FakeJavaMap(
        (("type_name", "ParameterHandleValueMap"), (native_param, ("byte_array", converter.bridge.route_name, (120, 121, 122)))),
    )

    pair_list = converter.to_backend(
        [AttributeRegionAssociation(AttributeHandleSet({py_attr}), RegionHandleSet({py_region}))],
        expected_type_name="AttributeSetRegionSetPairList",
    )
    assert pair_list == _FakeJavaCollection(
        "AttributeSetRegionSetPairList",
        (
            (
                _FakeJavaCollection("AttributeHandleSet", (native_attr,)),
                _FakeJavaCollection("RegionHandleSet", (native_region,)),
            ),
        ),
    )


def test_generic_fallback_container_families_are_shared_across_bridge_routes(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter

    assert converter.to_backend(["alpha", "beta"]) == _FakeJavaCollection("ArrayList", ("alpha", "beta"))
    assert set(converter.to_backend({"alpha", "beta"}).values) == {"alpha", "beta"}
    assert set(converter.to_backend(frozenset({"alpha", "beta"})).values) == {"alpha", "beta"}
    assert converter.to_backend({"alpha": "beta"}) == _FakeJavaMap((("alpha", "beta"),))


def test_generic_adapter_owns_generic_container_round_trip(generic_converter: GenericJavaValueAdapter) -> None:
    wrapped_list = generic_converter.to_backend(["alpha", "beta"])
    wrapped_set = generic_converter.to_backend({"alpha", "beta"})
    wrapped_map = generic_converter.to_backend({"alpha": "beta"})

    assert generic_converter.from_backend(wrapped_list) == ["alpha", "beta"]
    assert generic_converter.from_backend(wrapped_set) == {"alpha", "beta"}
    assert generic_converter.from_backend(wrapped_map) == {"alpha": "beta"}


def test_deterministic_strict_container_policy_rejects_generic_fallbacks(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter

    with pytest.raises(Exception, match="forbids generic container fallback"):
        converter.to_backend(["alpha"], expected_type_name="java.util.List", strict_container_shapes=True)
    with pytest.raises(Exception, match="forbids generic container fallback"):
        converter.to_backend({"alpha"}, expected_type_name="java.util.Set", strict_container_shapes=True)
    with pytest.raises(Exception, match="forbids generic container fallback"):
        converter.to_backend({"alpha": "beta"}, expected_type_name="java.util.Map", strict_container_shapes=True)


def test_reverse_normalization_uses_typed_and_generic_paths_centrally(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter
    native_attr = ("native-attribute", 9)

    typed_set = converter.from_backend(_FakeJavaCollection("AttributeHandleSet", (native_attr,)), expected_type_name="AttributeHandleSet")
    assert isinstance(typed_set, AttributeHandleSet)
    assert list(typed_set)[0].value == 1

    typed_map = converter.from_backend(
        _FakeJavaMap(((native_attr, b"abc"),)),
        expected_type_name="AttributeHandleValueMap",
    )
    assert typed_map[list(typed_map.keys())[0]] == b"abc"

    generic_map = converter.from_backend(_FakeJavaMap((("alpha", "beta"),)))
    assert generic_map == {"alpha": "beta"}

    generic_collection = converter.from_backend(_FakeJavaCollection("HashSet", ("alpha", "beta")))
    assert generic_collection == {"alpha", "beta"}


def test_round_trip_typed_handle_set_preserves_semantic_values(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter
    native_attr = ("native-attribute", 21)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)

    wrapped = converter.to_backend({py_attr}, expected_type_name="AttributeHandleSet")
    unwrapped = converter.from_backend(wrapped, expected_type_name="AttributeHandleSet")

    assert isinstance(unwrapped, AttributeHandleSet)
    assert unwrapped == AttributeHandleSet({py_attr})


def test_round_trip_typed_handle_value_map_preserves_keys_and_payloads(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter
    native_attr = ("native-attribute", 22)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)
    payload = b"abc"

    wrapped = converter.to_backend({py_attr: payload}, expected_type_name="AttributeHandleValueMap")
    unwrapped = converter.from_backend(wrapped, expected_type_name="AttributeHandleValueMap")

    assert dict(unwrapped.items()) == {py_attr: payload}


def test_round_trip_attribute_set_region_set_pair_list_preserves_associations(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter
    native_attr = ("native-attribute", 23)
    native_region = ("native-region", 24)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)
    py_region = converter.handle_registry.to_python(RegionHandle, native_region)
    associations = [AttributeRegionAssociation(AttributeHandleSet({py_attr}), RegionHandleSet({py_region}))]

    wrapped = converter.to_backend(associations, expected_type_name="AttributeSetRegionSetPairList")
    unwrapped = converter.from_backend(wrapped, expected_type_name="AttributeSetRegionSetPairList")

    assert len(unwrapped) == 1
    assert unwrapped[0].ahset == AttributeHandleSet({py_attr})
    assert unwrapped[0].rhset == RegionHandleSet({py_region})


def test_round_trip_generic_list_preserves_list_shape(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter

    wrapped = converter.to_backend(["alpha", "beta"])
    unwrapped = converter.from_backend(wrapped)

    assert unwrapped == ["alpha", "beta"]


def test_round_trip_generic_set_preserves_set_shape(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter

    wrapped = converter.to_backend({"alpha", "beta"})
    unwrapped = converter.from_backend(wrapped)

    assert unwrapped == {"alpha", "beta"}


def test_round_trip_generic_map_preserves_mapping_shape(contract_converter: HLAJavaValueAdapter) -> None:
    converter = contract_converter

    wrapped = converter.to_backend({"alpha": "beta"})
    unwrapped = converter.from_backend(wrapped)

    assert unwrapped == {"alpha": "beta"}
