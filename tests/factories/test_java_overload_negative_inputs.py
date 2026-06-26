from __future__ import annotations

from collections import UserString
from pathlib import Path

import pytest

from hla.backends.common import (
    BackendConversionError,
    Invocation,
    ResolvedJavaInvocation,
    get_java_invocation_resolver,
    reset_java_invocation_resolver,
    set_java_invocation_resolver,
)
from hla.bridges.java.common import JavaBridge, JavaValueConverter, resolve_java_invocation
from hla.rti1516e.handles import AttributeHandle, ObjectInstanceHandle, ParameterHandle


class _FakeBridge(JavaBridge):
    def call(self, obj, method_name: str, *args):
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher):
        return dispatcher

    def byte_array(self, data: bytes):
        return b"java-byte-array:" + data

    def fom_url(self, value):
        return f"url:{value}"

    def fom_url_array(self, values):
        return tuple(f"url:{value}" for value in values)


class _CustomStringLike:
    def __str__(self) -> str:
        return "string-ish"


class _FakeUriLike:
    def __init__(self, uri: str) -> None:
        self.uri = uri


def test_java_invocation_resolver_is_swappable_and_restorable():
    original = get_java_invocation_resolver()

    def _alternate(invocation: Invocation) -> ResolvedJavaInvocation:
        assert invocation.method_name == "swapCheck"
        return ResolvedJavaInvocation(args=("alternate-route",), param_types=("String",), overload=None)

    previous = set_java_invocation_resolver(_alternate)
    assert previous is original
    try:
        resolved = resolve_java_invocation(Invocation(method_name="swapCheck", args=("ignored",)))
        assert resolved.args == ("alternate-route",)
        assert resolved.param_types == ("String",)
    finally:
        reset_java_invocation_resolver()

    assert get_java_invocation_resolver() is original


def test_java_overload_resolution_rejects_userstring_for_string_and_url_routes_with_clear_error():
    invocation = Invocation(
        method_name="createFederationExecution",
        args=("fed", UserString("resource:VendorSmokeFOM.xml"), UserString("HLAfloat64Time")),
        overloads=(
            {"language": "java", "params": "String federationExecutionName, URL[] fomModules, String logicalTimeImplementationName"},
            {"language": "java", "params": "String federationExecutionName, String fomModule, String logicalTimeImplementationName"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Could not map arguments for createFederationExecution") as exc_info:
        resolve_java_invocation(invocation)

    text = str(exc_info.value)
    assert "Provided args=3" in text
    assert "Java overload parameters" in text


def test_java_overload_resolution_rejects_off_shape_join_argument_with_clear_error():
    invocation = Invocation(
        method_name="joinFederationExecution",
        args=("Observer", "JoinFederate", object()),
        overloads=(
            {"language": "java", "params": "String federateType, String federationExecutionName, URL[] additionalFomModules"},
            {"language": "java", "params": "String federateName, String federateType, String federationExecutionName"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Could not map arguments for joinFederationExecution") as exc_info:
        resolve_java_invocation(invocation)

    text = str(exc_info.value)
    assert "Provided args=3" in text
    assert "federateType" in text


def test_java_overload_resolution_rejects_wrong_handle_family_with_clear_error():
    invocation = Invocation(
        method_name="requestAttributeValueUpdate",
        args=(ParameterHandle(99), {AttributeHandle(51)}, b"radar-rcs-query"),
        overloads=(
            {"language": "java", "params": "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
            {"language": "java", "params": "ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Could not map arguments for requestAttributeValueUpdate") as exc_info:
        resolve_java_invocation(invocation)

    text = str(exc_info.value)
    assert "Java overload parameters" in text
    assert "theObject" in text or "theClass" in text


def test_java_converter_rejects_string_like_impostor_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java String") as exc_info:
        converter.to_backend(UserString("fed"), expected_type_name="String")

    text = str(exc_info.value)
    assert "UserString" in text
    assert "exact Python str" in text


def test_java_converter_rejects_custom_str_impostor_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java String") as exc_info:
        converter.to_backend(_CustomStringLike(), expected_type_name="String")

    text = str(exc_info.value)
    assert "_CustomStringLike" in text
    assert "exact Python str" in text


def test_java_converter_rejects_non_url_like_url_target_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java URL") as exc_info:
        converter.to_backend(object(), expected_type_name="URL")

    text = str(exc_info.value)
    assert "object" in text
    assert "os.PathLike" in text


def test_java_converter_rejects_bad_url_array_member_with_indexed_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java URL\\[\\]") as exc_info:
        converter.to_backend([Path("demo.xml"), object(), _FakeUriLike("resource:VendorSmokeFOM.xml")], expected_type_name="URL[]")

    text = str(exc_info.value)
    assert "item 1=object" in text
    assert "URL-like" in text


def test_java_converter_rejects_non_iterable_handle_set_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java AttributeHandleSet") as exc_info:
        converter.to_backend(ObjectInstanceHandle(7), expected_type_name="AttributeHandleSet")

    text = str(exc_info.value)
    assert "ObjectInstanceHandle" in text
    assert "iterable of handle values" in text


def test_java_converter_rejects_non_mapping_handle_value_map_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java AttributeHandleValueMap") as exc_info:
        converter.to_backend(object(), expected_type_name="AttributeHandleValueMap")

    text = str(exc_info.value)
    assert "object" in text
    assert "mapping of handle keys" in text


def test_java_converter_rejects_non_bytes_like_byte_array_target_with_clear_error():
    converter = JavaValueConverter(_FakeBridge())

    with pytest.raises(BackendConversionError, match="Expected Java byte\\[\\]") as exc_info:
        converter.to_backend(object(), expected_type_name="byte[]")

    text = str(exc_info.value)
    assert "object" in text
    assert "bytes, bytearray, memoryview" in text
