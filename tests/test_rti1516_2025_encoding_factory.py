from __future__ import annotations

import inspect
import struct
from typing import get_type_hints

import pytest
from hla.rti1516_2025 import BasicEncoderFactory, create_encoder_factory
from hla.rti1516_2025._byte_wrapper import BytesLike as BytesLike2025
from hla.rti1516_2025._byte_wrapper import ByteWrapper as ByteWrapper2025
from hla.rti1516_2025.encoding import (
    CallableDataElementFactory,
    SimpleByteWrapper,
    SimpleVariableLengthData,
)
from hla.rti1516e._byte_wrapper import BytesLike as BytesLike2010
from hla.rti1516e._byte_wrapper import ByteWrapper as ByteWrapper2010


@pytest.mark.requirements("HLA2025-FI-004")
def test_basic_encoder_factory_creates_and_round_trips_primitives() -> None:
    factory = create_encoder_factory()

    assert isinstance(factory, BasicEncoderFactory)
    assert factory.createHLAinteger32BE(42).toByteArray() == b"\x00\x00\x00*"
    assert factory.createHLAinteger32LE(42).toByteArray() == b"*\x00\x00\x00"
    assert factory.createHLAunsignedInteger64BE(9).toByteArray() == struct.pack(">Q", 9)
    assert factory.createHLAboolean(True).toByteArray() == b"\x01"
    assert factory.createHLAASCIIchar(65).toByteArray() == b"A"
    assert factory.createHLAunicodeChar(0x03BB).toByteArray() == b"\x03\xbb"

    decoded = factory.createHLAinteger32BE().decode(b"\x00\x00\x00*")
    assert decoded.getValue() == 42


@pytest.mark.requirements("HLA2025-FI-004", "HLA2025-OMT-002")
def test_strings_opaque_data_and_variable_length_data_helpers() -> None:
    factory = create_encoder_factory()

    ascii_value = factory.createHLAASCIIstring("radar")
    assert ascii_value.toByteArray() == b"\x00\x00\x00\x05radar"
    assert factory.createHLAASCIIstring().decode(ascii_value.toByteArray()).getValue() == "radar"

    unicode_value = factory.createHLAunicodeString("λ")
    assert unicode_value.toByteArray() == b"\x00\x00\x00\x02\x03\xbb"
    assert factory.createHLAunicodeString().decode(unicode_value.toByteArray()).getValue() == "λ"

    opaque = factory.createHLAopaqueData([1, 2, 3])
    holder = SimpleVariableLengthData()
    opaque.encode(holder)
    assert holder.data() == b"\x00\x00\x00\x03\x01\x02\x03"
    assert list(factory.createHLAopaqueData().decode(holder).getValue()) == [1, 2, 3]


@pytest.mark.requirements("HLA2025-FI-004")
def test_byte_wrapper_supports_java_style_put_get_and_slices() -> None:
    wrapper = SimpleByteWrapper()
    wrapper.putInt(7)
    wrapper.put(b"abcd")
    assert wrapper.toByteArray() == b"\x00\x00\x00\x07abcd"

    reader = SimpleByteWrapper(wrapper.array())
    assert reader.getInt() == 7
    assert reader.slice(2).toByteArray() == b"ab"
    assert reader.remaining() == 2


def test_2010_and_2025_byte_wrapper_put_signatures_and_mutables_stay_aligned() -> None:
    expected_put_value = int | bytes | bytearray | memoryview

    for byte_wrapper in (ByteWrapper2010, ByteWrapper2025):
        put_hints = get_type_hints(byte_wrapper.put)
        reassign_hints = get_type_hints(byte_wrapper.reassign)
        get_hints = get_type_hints(byte_wrapper.get)
        array_hints = get_type_hints(byte_wrapper.array)

        assert put_hints["value"] == expected_put_value
        assert put_hints["offset"] == (int | None)
        assert put_hints["count"] == (int | None)
        assert reassign_hints["buffer"] is bytearray
        assert get_hints["dest"] == (bytearray | None)
        assert get_hints["return"] == (int | None)
        assert array_hints["return"] is bytearray

    assert BytesLike2010.__args__ == BytesLike2025.__args__ == (bytes, bytearray, memoryview)

    assert inspect.signature(ByteWrapper2010.put) == inspect.signature(ByteWrapper2025.put)


def test_simple_byte_wrapper_supports_memoryview_inputs_and_offsets() -> None:
    wrapper = SimpleByteWrapper()
    wrapper.put(memoryview(b"\xAA\xCC"))
    wrapper.put(memoryview(b"\xDD\xEE"), 1, 1)

    assert wrapper.toByteArray() == b"\xAA\xCC\xEE"


def test_simple_byte_wrapper_mutable_paths_return_bytearray() -> None:
    wrapper = SimpleByteWrapper()
    wrapper.put(b"\x00\x01\x02\x03\x04")
    assert isinstance(wrapper.array(), bytearray)

    reader = SimpleByteWrapper(wrapper.array())
    target = bytearray(3)
    assert reader.get(target) is None
    assert target == b"\x00\x01\x02"

    scratch = bytearray(10)
    reader.reassign(scratch, 0, 4)
    assert reader.array() is scratch


@pytest.mark.requirements("HLA2025-FI-004", "HLA2025-OMT-002")
def test_factory_builds_arrays_records_and_variants() -> None:
    factory = create_encoder_factory()
    element_factory = CallableDataElementFactory(lambda index: factory.createHLAinteger16BE(index + 1))

    fixed_array = factory.createHLAfixedArray(element_factory, 3)
    assert fixed_array.size() == 3
    assert fixed_array.toByteArray() == b"\x00\x01\x00\x02\x00\x03"

    variable_array = factory.createHLAvariableArray(element_factory, factory.createHLAoctet(9), factory.createHLAoctet(10))
    assert variable_array.toByteArray() == b"\x00\x00\x00\x02\x09\x0a"

    record = factory.createHLAfixedRecord()
    record.appendElement(factory.createHLAinteger16BE(3)).appendElement(factory.createHLAASCIIchar(88))
    assert record.size() == 2
    assert record.toByteArray() == b"\x00\x03X"

    variant = factory.createHLAvariantRecord(factory.createHLAoctet(1))
    variant.setVariant(factory.createHLAoctet(1), factory.createHLAASCIIstring("one"))
    assert variant.getValue().getValue() == "one"
    assert variant.toByteArray() == b"\x01\x00\x00\x00\x03one"


@pytest.mark.requirements("HLA2025-FI-003", "HLA2025-FI-009")
def test_factory_wraps_handles_and_logical_time_values_without_vendor_dependency() -> None:
    factory = create_encoder_factory()
    sentinel = object()

    assert factory.createHLAfederateHandle(sentinel).toByteArray() == b""
    assert factory.createHLAlogicalTime(sentinel).toByteArray() == b""
    assert factory.createHLAlogicalTimeInterval(sentinel).toByteArray() == b""
