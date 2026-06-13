from __future__ import annotations

import pytest

from hla2010_rti_java_common.java_common import (
    append_java_collection_value,
    create_java_factory_collection,
    invoke_java_factory_method,
    java_handle_set_factory_method,
    java_handle_value_map_factory_method,
    put_java_map_entry,
)


class _FakeFactory:
    def __init__(self) -> None:
        self.capacities: list[int | None] = []

    def create(self, capacity: int | None = None) -> "_FakeCollection":
        self.capacities.append(capacity)
        return _FakeCollection()


class _FakeCollection:
    def __init__(self) -> None:
        self.values: list[object] = []
        self.entries: list[tuple[object, object]] = []

    def add(self, value: object) -> None:
        self.values.append(value)

    def put(self, key: object, value: object) -> None:
        self.entries.append((key, value))


class _FakeAmbassador:
    def __init__(self) -> None:
        self.attribute_set_factory = _FakeFactory()
        self.attribute_value_map_factory = _FakeFactory()
        self.pair_list_factory = _FakeFactory()

    def getAttributeHandleSetFactory(self) -> _FakeFactory:  # noqa: N802
        return self.attribute_set_factory

    def getAttributeHandleValueMapFactory(self) -> _FakeFactory:  # noqa: N802
        return self.attribute_value_map_factory

    def getAttributeSetRegionSetPairListFactory(self) -> _FakeFactory:  # noqa: N802
        return self.pair_list_factory


def test_java_handle_factory_method_maps_supported_types() -> None:
    assert java_handle_set_factory_method("AttributeHandleSet") == "getAttributeHandleSetFactory"
    assert java_handle_value_map_factory_method("AttributeHandleValueMap") == "getAttributeHandleValueMapFactory"


def test_java_handle_factory_method_rejects_unknown_types() -> None:
    with pytest.raises(AttributeError, match="UnknownSetType"):
        java_handle_set_factory_method("UnknownSetType")
    with pytest.raises(AttributeError, match="UnknownMapType"):
        java_handle_value_map_factory_method("UnknownMapType")


def test_invoke_and_create_java_factory_collection_use_explicit_factory_methods() -> None:
    ambassador = _FakeAmbassador()

    factory = invoke_java_factory_method(ambassador, "getAttributeHandleSetFactory")
    assert factory is ambassador.attribute_set_factory

    collection = create_java_factory_collection(ambassador, "getAttributeSetRegionSetPairListFactory", capacity=3)
    assert isinstance(collection, _FakeCollection)
    assert ambassador.pair_list_factory.capacities == [3]


def test_java_collection_helpers_use_explicit_add_and_put_apis() -> None:
    collection = _FakeCollection()

    append_java_collection_value(collection, "a")
    append_java_collection_value(collection, "b")
    put_java_map_entry(collection, "k", "v")

    assert collection.values == ["a", "b"]
    assert collection.entries == [("k", "v")]
