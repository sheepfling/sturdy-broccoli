from __future__ import annotations

from collections import UserString
from pathlib import Path

import pytest

from hla.backends.common import (
    BackendConversionError,
    Invocation,
    ResolvedJavaInvocation,
    install_deterministic_java_invocation_router,
    get_java_invocation_resolver,
    reset_java_invocation_resolver,
    resolve_java_invocation_deterministic,
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


def test_java_overload_resolution_keeps_single_overload_calls_strict_for_bad_shape_inputs():
    invocation = Invocation(
        method_name="getFederateName",
        args=(None,),
        overloads=(
            {"language": "java", "params": "FederateHandle theHandle"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Could not map arguments for getFederateName"):
        resolve_java_invocation(invocation)


def test_java_overload_resolution_allows_single_overload_concrete_bad_handle_to_reach_backend_validation():
    invocation = Invocation(
        method_name="getFederateName",
        args=(object(),),
        overloads=(
            {"language": "java", "params": "FederateHandle theHandle"},
        ),
    )

    resolved = resolve_java_invocation(invocation)

    assert resolved.args == invocation.args
    assert resolved.param_types == ("FederateHandle",)


def test_deterministic_java_router_can_be_installed_and_restored():
    original = get_java_invocation_resolver()

    previous = install_deterministic_java_invocation_router()
    assert previous is original
    try:
        assert get_java_invocation_resolver() is resolve_java_invocation_deterministic
    finally:
        set_java_invocation_resolver(previous)
        reset_java_invocation_resolver()


def test_deterministic_java_router_routes_request_attribute_value_update_by_handle_family():
    invocation = Invocation(
        method_name="requestAttributeValueUpdate",
        args=(ObjectInstanceHandle(99), {AttributeHandle(51)}, b"radar-rcs-query"),
        overloads=(
            {"language": "java", "params": "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
            {"language": "java", "params": "ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
        ),
    )

    resolved = resolve_java_invocation_deterministic(invocation)

    assert resolved.param_types == ("ObjectInstanceHandle", "AttributeHandleSet", "byte[]")


def test_deterministic_java_router_routes_join_federation_execution_by_third_argument_shape():
    invocation = Invocation(
        method_name="joinFederationExecution",
        args=("observer", "demo-fed", [Path("TargetRadarFOMmodule.xml")]),
        overloads=(
            {"language": "java", "params": "String federateType, String federationExecutionName, URL[] additionalFomModules"},
            {"language": "java", "params": "String federateName, String federateType, String federationExecutionName"},
        ),
    )

    resolved = resolve_java_invocation_deterministic(invocation)

    assert resolved.param_types == ("String", "String", "URL[]")


def test_deterministic_java_router_fails_closed_without_explicit_method_route():
    invocation = Invocation(
        method_name="ambiguousCall",
        args=("alpha",),
        overloads=(
            {"language": "java", "params": "String federationExecutionName"},
            {"language": "java", "params": "String federateType"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Deterministic Java router has no explicit route for ambiguousCall") as exc_info:
        resolve_java_invocation_deterministic(invocation)

    assert "matching overload parameters" in str(exc_info.value)


def test_java_overload_resolution_keeps_unique_arity_match_strict_for_bad_shape_inputs():
    invocation = Invocation(
        method_name="subscribeObjectClassAttributes",
        args=(object(), set()),
        overloads=(
            {"language": "java", "params": "ObjectClassHandle theClass, AttributeHandleSet attributeList"},
            {
                "language": "java",
                "params": "ObjectClassHandle theClass, AttributeHandleSet attributeList, String updateRateDesignator",
            },
        ),
    )

    with pytest.raises(BackendConversionError, match="Could not map arguments for subscribeObjectClassAttributes"):
        resolve_java_invocation(invocation)


def test_java_overload_resolution_treats_trailing_none_as_omitted_optional_suffix():
    invocation = Invocation(
        method_name="createFederationExecution",
        args=("fed", ["TargetRadarFOMmodule.xml"], None),
        overloads=(
            {"language": "java", "params": "String federationExecutionName, URL[] fomModules, String logicalTimeImplementationName"},
            {"language": "java", "params": "String federationExecutionName, URL[] fomModules"},
        ),
    )

    resolved = resolve_java_invocation(invocation)

    assert resolved.args == ("fed", ["TargetRadarFOMmodule.xml"])
    assert resolved.param_types == ("String", "URL[]")


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
