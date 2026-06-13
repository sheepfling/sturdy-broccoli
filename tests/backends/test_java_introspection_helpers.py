from __future__ import annotations

from hla2010_rti_java_common.java_common import (
    java_runtime_full_class_name,
    java_runtime_public_field,
    java_runtime_simple_class_name,
    jpype_exception_class_name,
    py4j_exception_class_name,
    py4j_exception_message,
    python_runtime_simple_class_name,
)


class _FakeJavaClassInfo:
    def __init__(self, name: str, simple_name: str) -> None:
        self._name = name
        self._simple_name = simple_name

    def getName(self) -> str:  # noqa: N802
        return self._name

    def getSimpleName(self) -> str:  # noqa: N802
        return self._simple_name


class _FakeJavaObject:
    public_value = 9

    def getClass(self) -> _FakeJavaClassInfo:  # noqa: N802
        return _FakeJavaClassInfo("hla.rti1516e.FakeJavaObject", "FakeJavaObject")


class _FieldAwareObject:
    def _get_field(self, field_name: str) -> tuple[bool, object]:
        return (field_name == "present", 42)


class _PlainPythonObject:
    pass


class _FakeJPypeException(Exception):
    javaClass = "hla.rti1516e.FederationExecutionDoesNotExist"


class _FakePy4JJavaException:
    def getClass(self) -> _FakeJavaClassInfo:  # noqa: N802
        return _FakeJavaClassInfo("hla.rti1516e.FederateInternalError", "FederateInternalError")

    def getMessage(self) -> str:  # noqa: N802
        return "bridge failed"


class _FakePy4JException(Exception):
    def __init__(self) -> None:
        super().__init__("fallback")
        self.java_exception = _FakePy4JJavaException()


def test_java_runtime_class_name_helpers_resolve_java_get_class_metadata() -> None:
    value = _FakeJavaObject()

    assert java_runtime_full_class_name(value) == "hla.rti1516e.FakeJavaObject"
    assert java_runtime_simple_class_name(value) == "FakeJavaObject"


def test_java_runtime_public_field_prefers_explicit_field_hook_and_plain_attribute() -> None:
    assert java_runtime_public_field(_FieldAwareObject(), "present") == 42
    assert java_runtime_public_field(_FakeJavaObject(), "public_value") == 9


def test_python_runtime_simple_class_name_uses_python_type_name() -> None:
    assert python_runtime_simple_class_name(_PlainPythonObject()) == "_PlainPythonObject"


def test_jpype_exception_class_name_uses_java_class_or_java_class_fallback() -> None:
    class direct(Exception):
        def getClass(self):  # noqa: N802
            return _FakeJavaClassInfo("hla.rti1516e.AlreadyConnected", "AlreadyConnected")

    assert jpype_exception_class_name(direct()) == "AlreadyConnected"
    assert jpype_exception_class_name(_FakeJPypeException()) == "FederationExecutionDoesNotExist"


def test_py4j_exception_helpers_use_java_exception_proxy() -> None:
    exc = _FakePy4JException()

    assert py4j_exception_class_name(exc) == "FederateInternalError"
    assert py4j_exception_message(exc) == "bridge failed"
