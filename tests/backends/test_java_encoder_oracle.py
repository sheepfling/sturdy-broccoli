from __future__ import annotations

import pytest

from hla.backends.common import BackendConversionError, BackendInfo, Invocation
from hla.bridges.java.common import HLAJavaValueAdapter, JavaBridge, JavaRTIBackend


class _FakeEncodedElement:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def toByteArray(self) -> bytes:  # noqa: N802
        return self._payload


class _FakeEncoderFactory:
    def createHLAASCIIstring(self, value: str) -> _FakeEncodedElement:  # noqa: N802
        return _FakeEncodedElement(b"ascii:" + value.encode("ascii"))

    def createHLAunicodeString(self, value: str) -> _FakeEncodedElement:  # noqa: N802
        return _FakeEncodedElement(b"unicode:" + value.encode("utf-8"))

    def createHLAoctet(self, value: int) -> _FakeEncodedElement:  # noqa: N802
        return _FakeEncodedElement(b"octet:" + bytes([value]))

    def createHLAfixedRecord(self):  # noqa: N802
        return _FakeJavaFixedRecord()

    def createHLAfixedArray(self, *elements):  # noqa: N802
        return _FakeJavaFixedArray(elements)

    def createHLAvariantRecord(self, discriminant):  # noqa: N802
        return _FakeJavaVariantRecord(discriminant)


class _FakeJavaFixedRecord:
    def __init__(self) -> None:
        self._elements: list[_FakeEncodedElement] = []

    def add(self, element) -> None:
        self._elements.append(element)

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"record(" + b"|".join(element.toByteArray() for element in self._elements) + b")"


class _FakeJavaFixedArray:
    def __init__(self, elements) -> None:
        self._elements = list(elements)

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"array(" + b"|".join(element.toByteArray() for element in self._elements) + b")"


class _FakeJavaVariantRecord:
    def __init__(self, discriminant) -> None:
        self._discriminant = discriminant
        self._value = None

    def setVariant(self, discriminant, value) -> None:  # noqa: N802
        self._discriminant = discriminant
        self._value = value

    def setDiscriminant(self, discriminant) -> None:  # noqa: N802
        self._discriminant = discriminant

    def toByteArray(self) -> bytes:  # noqa: N802
        value = b"" if self._value is None else self._value.toByteArray()
        return b"variant(" + self._discriminant.toByteArray() + b"|" + value + b")"


class _FakeJavaFactory:
    def getEncoderFactory(self) -> _FakeEncoderFactory:  # noqa: N802
        return _FakeEncoderFactory()


class _FakeJavaRTIAmbassador:
    def connect(self, *args):
        return args


class _PythonOwnedEncodingShouldNotRun:
    def getValue(self):  # noqa: N802
        return "vendor-only"

    def toByteArray(self) -> bytes:  # noqa: N802
        raise AssertionError("python-owned toByteArray should not run for vendor-backed byte[] conversion")


class _FakeBridge(JavaBridge):
    def call(self, obj, method_name: str, *args):
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher):
        return dispatcher

    def enum_constant(self, enum_class_name: str, member_name: str):
        return member_name

    def byte_array(self, data: bytes):
        return b"java-byte-array:" + data

    def credentials(self, value):
        return {
            "java_type": getattr(value, "type"),
            "java_data": bytes(getattr(value, "data")),
        }


def test_java_encoder_oracle_uses_live_factory_bound_to_backend() -> None:
    backend = JavaRTIBackend(
        java_rti_ambassador=object(),
        java_factory=_FakeJavaFactory(),
        bridge=_FakeBridge(),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    oracle = backend.java_encoder_oracle

    assert oracle is not None
    assert oracle.encode_ascii_string("radar") == b"ascii:radar"
    assert oracle.encode_unicode_string("lambda-\u03bb") == b"unicode:lambda-\xce\xbb"
    assert backend.java_encoder_oracle is oracle


def test_java_encoder_oracle_is_absent_without_java_factory() -> None:
    backend = JavaRTIBackend(
        java_rti_ambassador=object(),
        bridge=_FakeBridge(),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    assert backend.java_encoder_oracle is None


def test_vendor_encoding_helper_builds_python_elements_and_encodes_with_vendor_factory() -> None:
    backend = JavaRTIBackend(
        java_rti_ambassador=object(),
        java_factory=_FakeJavaFactory(),
        bridge=_FakeBridge(),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    helper = backend.vendor_encoding
    record = helper.fixed_record(
        helper.ascii_string("radar"),
        helper.unicode_string("lambda-\u03bb"),
    )

    assert type(helper.ascii_string("radar")).__name__ == "HLAASCIIstring"
    assert helper.encode(record) == b"record(ascii:radar|unicode:lambda-\xce\xbb)"
    assert helper.byte_array(helper.ascii_string("rti")) == b"java-byte-array:ascii:rti"


def test_vendor_encoding_helper_supports_2025_variant_records() -> None:
    backend = JavaRTIBackend(
        java_rti_ambassador=object(),
        java_factory=_FakeJavaFactory(),
        bridge=_FakeBridge(api_profile="2025"),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    helper = backend.vendor_encoding
    variant = helper.variant_record(
        helper.octet(7),
        helper.ascii_string("space"),
    )

    assert helper.encode(variant) == b"variant(octet:\x07|ascii:space)"


def test_vendor_encoding_helper_requires_live_java_factory_for_encoding() -> None:
    backend = JavaRTIBackend(
        java_rti_ambassador=object(),
        bridge=_FakeBridge(),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    with pytest.raises(BackendConversionError, match="live Java factory"):
        backend.vendor_encoding.encode(backend.vendor_encoding.ascii_string("offline"))


def test_java_converter_materializes_2025_credentials_for_vendor_routes() -> None:
    from hla.rti1516_2025.auth import HLAnoCredentials, HLAplainTextPassword
    from hla.rti1516_2025.datatypes import Credentials

    converter = HLAJavaValueAdapter(_FakeBridge(api_profile="2025"))

    assert converter.to_backend(HLAnoCredentials(), expected_type_name="Credentials") == {
        "java_type": "HLAnoCredentials",
        "java_data": b"",
    }
    assert converter.to_backend(HLAplainTextPassword("secret"), expected_type_name="Credentials") == {
        "java_type": "HLAplainTextPassword",
        "java_data": HLAplainTextPassword("secret").data,
    }
    assert converter.to_backend(Credentials("Proto2025Bearer", b"token"), expected_type_name="Credentials") == {
        "java_type": "Proto2025Bearer",
        "java_data": b"token",
    }


def test_java_converter_prefers_vendor_factory_over_python_owned_encoding_for_byte_arrays() -> None:
    converter = HLAJavaValueAdapter(
        _FakeBridge(),
        java_encoder_oracle=JavaRTIBackend(
            java_rti_ambassador=object(),
            java_factory=_FakeJavaFactory(),
            bridge=_FakeBridge(),
            info=BackendInfo(name="fake", kind="java/fake"),
        ).java_encoder_oracle,
    )

    payload = type("HLAASCIIstring", (_PythonOwnedEncodingShouldNotRun,), {})()

    assert converter.to_backend(payload, expected_type_name="byte[]") == b"java-byte-array:ascii:vendor-only"


def test_java_backend_connect_invocation_materializes_vendor_credentials_and_vendor_bytes() -> None:
    from hla.rti1516_2025.auth import HLAplainTextPassword
    from hla.rti1516_2025.enums import CallbackModel

    backend = JavaRTIBackend(
        java_rti_ambassador=_FakeJavaRTIAmbassador(),
        java_factory=_FakeJavaFactory(),
        bridge=_FakeBridge(api_profile="2025"),
        info=BackendInfo(name="fake", kind="java/fake"),
    )

    result = backend.invoke(
        Invocation(
            method_name="connect",
            args=(object(), CallbackModel.HLA_IMMEDIATE),
            kwargs={"credentials": HLAplainTextPassword("secret")},
            overloads=(
                {
                    "language": "java",
                    "params": (
                        "FederateAmbassador federateAmbassador, "
                        "CallbackModel callbackModel, "
                        "Credentials credentials"
                    ),
                    "return_type": "ConfigurationResult",
                },
            ),
        )
    )

    assert result[1] == "HLA_IMMEDIATE"
    assert result[2] == {
        "java_type": "HLAplainTextPassword",
        "java_data": HLAplainTextPassword("secret").data,
    }
