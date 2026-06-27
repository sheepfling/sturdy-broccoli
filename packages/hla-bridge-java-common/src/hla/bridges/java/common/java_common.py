"""Shared Java RTI backend support.

Concrete bridge packages, such as the JPype and Py4J bridge packages, supply
the mechanics for their Java bridge.
This module supplies the bridge-facing composition surface: backend invocation,
callback dispatching, exception translation, and live encoder helpers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping as CollectionsMapping
from typing import TYPE_CHECKING, Any, Iterable, Protocol, Sequence, TypeVar, cast

from hla.backends.common import (
    CALLBACK_METHOD_NAMES,
    BackendConversionError,
    BackendInfo,
    Invocation,
    JavaInvocationResolver,
    RTIBackend,
    ResolvedJavaInvocation,
    java_parameter_names,
    java_parameter_types,
    resolve_java_arguments,
    resolve_java_invocation,
)
from .java_binding_profile import load_python_java_binding_profile
from .java_value_adapter import GenericJavaValueAdapter, HLAJavaValueAdapter, JavaValueConverter

if TYPE_CHECKING:
    from .java_intake import JavaApiProfile
    from hla.rti1516e import NullFederateAmbassador

_DEFAULT_BINDING = load_python_java_binding_profile("2010")
hla_exceptions = _DEFAULT_BINDING.exceptions_module
FederateInternalError = hla_exceptions.FederateInternalError
RTIexception = hla_exceptions.RTIexception
RTIinternalError = hla_exceptions.RTIinternalError


_JavaKeyT = TypeVar("_JavaKeyT", covariant=True)
_JavaValueT = TypeVar("_JavaValueT", covariant=True)
_JavaItemT = TypeVar("_JavaItemT", covariant=True)


class _JavaMapEntry(Protocol[_JavaKeyT, _JavaValueT]):
    def getKey(self) -> _JavaKeyT: ...

    def getValue(self) -> _JavaValueT: ...


class _JavaIterator(Protocol[_JavaItemT]):
    def hasNext(self) -> bool: ...

    def next(self) -> _JavaItemT: ...


class JavaBridge(ABC):
    """Bridge operations needed by ``JavaRTIBackend``."""

    name: str = "java"

    def __init__(self, api_profile: str | JavaApiProfile = "2010"):
        self.python_binding = load_python_java_binding_profile(api_profile)
        self.api_profile = self.python_binding.api_profile

    @abstractmethod
    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_federate_proxy(self, dispatcher: "PythonFederateAmbassadorDispatcher") -> Any:
        raise NotImplementedError

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        raise BackendConversionError(f"Bridge {self.name} cannot resolve Java enum {enum_class_name}.{member_name}")

    def enum_member_name(self, value: Any) -> str | None:
        name_attr = getattr(value, "name", None)
        if callable(name_attr):
            try:
                return str(name_attr())
            except Exception:
                pass
        if isinstance(name_attr, str):
            return name_attr
        text = str(value)
        if "." in text and text.rsplit(".", 1)[-1].isidentifier():
            return text.rsplit(".", 1)[-1]
        return None

    def byte_array(self, data: bytes) -> Any:
        return data

    def encoder_factory(self, java_factory: Any) -> Any:
        return self.call(java_factory, "getEncoderFactory")

    def is_byte_array(self, value: Any) -> bool:
        if isinstance(value, (bytes, bytearray, memoryview)):
            return True
        simple_name = self.simple_class_name(value)
        class_name = self.full_class_name(value) or simple_name or ""
        return simple_name in {"byte[]", "byte"} or class_name in {"[B", "byte[]"}

    def to_python_bytes(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, bytearray):
            return bytes(value)
        if isinstance(value, memoryview):
            return value.tobytes()
        try:
            return bytes((int(item) + 256) % 256 for item in value)
        except Exception as exc:
            raise BackendConversionError(f"Could not convert Java byte[] value {value!r} to bytes") from exc

    def new_set(self, values: Sequence[Any]) -> Any:
        return set(values)

    def new_list(self, values: Sequence[Any]) -> Any:
        return list(values)

    def new_map(self, items: Sequence[tuple[Any, Any]]) -> Any:
        return dict(items)

    def fom_url(self, value: Any) -> Any:
        return self.python_binding.fom_module.module_uri(value)

    def fom_url_array(self, values: Sequence[Any]) -> Any:
        return [self.fom_url(value) for value in values]

    def new_handle_set(self, type_name: str, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        return self.new_set(values)

    def new_handle_value_map(self, type_name: str, items: Sequence[tuple[Any, Any]], *, rti_ambassador: Any | None = None) -> Any:
        return self.new_map(items)

    def new_attribute_set_region_set_pair_list(self, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        return self.new_list(values)

    def logical_time(self, value: Any, *, rti_ambassador: Any | None = None) -> Any:
        return value

    def rti_configuration(self, value: Any) -> Any:
        return value

    def credentials(self, value: Any) -> Any:
        return value

    def range_bounds(self, value: Any) -> Any:
        return value

    def java_map_items(self, value: Any) -> Sequence[tuple[Any, Any]] | None:
        if isinstance(value, CollectionsMapping):
            return list(value.items())
        entry_set = getattr(value, "entrySet", None)
        if callable(entry_set):
            try:
                entries = cast(Iterable[_JavaMapEntry[Any, Any]], entry_set())
                return [(entry.getKey(), entry.getValue()) for entry in entries]
            except Exception:
                return None
        return None

    def java_collection_values(self, value: Any) -> Sequence[Any] | None:
        if isinstance(value, (str, bytes, bytearray, memoryview, CollectionsMapping)):
            return None
        if isinstance(value, (list, tuple, set, frozenset)):
            return list(value)
        iterator = getattr(value, "iterator", None)
        if callable(iterator):
            try:
                it = cast(_JavaIterator[Any], iterator())
                result: list[Any] = []
                while it.hasNext():
                    result.append(it.next())
                return result
            except Exception:
                return None
        return None

    def public_field(self, obj: Any, field_name: str) -> Any | None:
        get_field = getattr(obj, "_get_field", None)
        if callable(get_field):
            try:
                found, value = cast(tuple[bool, Any], get_field(field_name))
                if found:
                    return value
            except Exception:
                pass
        try:
            value = getattr(obj, field_name)
        except Exception:
            return None
        return None if callable(value) else value

    def full_class_name(self, obj: Any) -> str | None:
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                class_info = cast(Any, get_class())
                get_name = getattr(class_info, "getName", None)
                if callable(get_name):
                    return str(get_name())
            except Exception:
                pass
        return None

    def simple_class_name(self, obj: Any) -> str | None:
        cls = getattr(obj, "__class__", None)
        name = getattr(cls, "__name__", None)
        return name

    def exception_class_name(self, exc: BaseException) -> str | None:
        cls = getattr(exc, "__class__", None)
        name = getattr(cls, "__name__", None)
        return name

    def exception_message(self, exc: BaseException) -> str:
        return str(exc)


def _clean_java_type(type_name: str | None) -> str | None:
    from hla.backends.common import clean_java_type_name

    return clean_java_type_name(type_name)


def expected_java_return_type(invocation: Invocation) -> str | None:
    return_types = {
        _clean_java_type(str(o.get("return_type", "")).strip()) or ""
        for o in invocation.overloads
        if o.get("language") == "java" and str(o.get("return_type", "")).strip() not in {"", "void"}
    }
    return_types.discard("")
    if len(return_types) == 1:
        return next(iter(return_types))
    return None


_CALLBACK_TYPE_FALLBACKS: dict[str, tuple[str | None, ...]] = {
    "federationSynchronized": ("String", "FederateHandleSet"),
}


def expected_java_callback_parameter_types(
    method_name: str,
    arg_count: int | None = None,
    *,
    binding: Any | None = None,
) -> tuple[str | None, ...]:
    resolved = (binding or _DEFAULT_BINDING).callback_parameter_types(method_name, arg_count)
    if resolved:
        return resolved
    fallback = _CALLBACK_TYPE_FALLBACKS.get(method_name)
    if fallback is None:
        return ()
    if arg_count is None:
        return fallback
    return fallback[:arg_count]


class PythonFederateAmbassadorDispatcher:
    """Dispatch Java FederateAmbassador callbacks to a Python ambassador."""

    def __init__(self, ambassador: Any, converter: Any):
        self.ambassador = ambassador
        self.converter = converter

    def _invoke_callback(self, method_name: str, *backend_args: Any) -> Any:
        try:
            expected = expected_java_callback_parameter_types(method_name, len(backend_args), binding=self.converter.python_binding)
            py_args = tuple(
                self.converter.from_backend(arg, expected_type_name=expected[idx] if idx < len(expected) else None)
                for idx, arg in enumerate(backend_args)
            )
            result = getattr(self.ambassador, method_name)(*py_args)
            return self.converter.to_backend(result) if result is not None else None
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc) from exc


for _callback_name in CALLBACK_METHOD_NAMES:
    if not hasattr(PythonFederateAmbassadorDispatcher, _callback_name):
        setattr(
            PythonFederateAmbassadorDispatcher,
            _callback_name,
            lambda self, *args, _method_name=_callback_name: self._invoke_callback(_method_name, *args),
        )


class JavaEncoderOracle:
    """Live Java ``EncoderFactory`` helper bound to one backend runtime."""

    def __init__(self, bridge: JavaBridge, encoder_factory: Any) -> None:
        self.bridge = bridge
        self.encoder_factory = encoder_factory

    def _python_elements(self, value: Any) -> list[Any]:
        for attr_name in ("_elements", "elements", "fields"):
            elements = getattr(value, attr_name, None)
            if elements is not None:
                return list(elements)
        if isinstance(value, Iterable):
            return list(value)
        raise BackendConversionError(f"Cannot enumerate elements from Python data element {type(value).__name__}")

    def materialize(self, value: Any) -> Any:
        type_name = type(value).__name__
        if type_name == "HLAfixedRecord":
            java_record = self.bridge.call(self.encoder_factory, "createHLAfixedRecord")
            for element in self._python_elements(value):
                self.bridge.call(java_record, "add", self.materialize(element))
            return java_record

        if type_name == "HLAfixedArray":
            return self.bridge.call(
                self.encoder_factory,
                "createHLAfixedArray",
                *(self.materialize(element) for element in self._python_elements(value)),
            )

        if type_name == "HLAvariantRecord":
            python_discriminant = getattr(value, "_discriminant", None)
            if python_discriminant is None:
                raise BackendConversionError("Python HLAvariantRecord is missing an active discriminant")
            active_value = getattr(value, "_value", None)
            if active_value is None:
                getter = getattr(value, "getValue", None)
                if callable(getter):
                    active_value = getter()
            if active_value is None:
                raise BackendConversionError("Python HLAvariantRecord has no active value")
            java_discriminant = self.materialize(python_discriminant)
            java_variant = self.bridge.call(self.encoder_factory, "createHLAvariantRecord", java_discriminant)
            self.bridge.call(java_variant, "setVariant", java_discriminant, self.materialize(active_value))
            self.bridge.call(java_variant, "setDiscriminant", java_discriminant)
            return java_variant

        if hasattr(self.encoder_factory, f"create{type_name}"):
            getter = getattr(value, "getValue", None)
            if callable(getter):
                return self.bridge.call(self.encoder_factory, f"create{type_name}", getter())
            if hasattr(value, "value"):
                return self.bridge.call(self.encoder_factory, f"create{type_name}", getattr(value, "value"))

        raise BackendConversionError(f"Java encoder oracle cannot materialize {type_name}")

    def encode_element(self, factory_method: str, *args: Any) -> bytes:
        element = self.bridge.call(self.encoder_factory, factory_method, *args)
        return self.bridge.to_python_bytes(self.bridge.call(element, "toByteArray"))

    def encode_python_data_element(self, value: Any) -> bytes:
        return self.bridge.to_python_bytes(self.bridge.call(self.materialize(value), "toByteArray"))

    def encode_ascii_string(self, value: str) -> bytes:
        return self.encode_element("createHLAASCIIstring", value)

    def encode_unicode_string(self, value: str) -> bytes:
        return self.encode_element("createHLAunicodeString", value)


class JavaVendorEncoding:
    """Python-facing helper that routes final encoding through a live vendor runtime."""

    def __init__(self, backend: "JavaRTIBackend") -> None:
        self.backend = backend
        self.python_binding = backend.bridge.python_binding

    def _oracle(self) -> JavaEncoderOracle:
        oracle = self.backend.java_encoder_oracle
        if oracle is None:
            raise BackendConversionError("Vendor encoding requires a live Java factory with an EncoderFactory")
        return oracle

    def _python_type(self, name: str) -> Any:
        python_type = self.python_binding.python_type_or_none(name)
        if python_type is None:
            raise BackendConversionError(f"Python binding does not export data element {name!r}")
        return python_type

    def element(self, type_name: str, value: Any | None = None) -> Any:
        python_type = self._python_type(type_name)
        return python_type() if value is None else python_type(value)

    def ascii_string(self, value: str) -> Any:
        return self.element("HLAASCIIstring", value)

    def unicode_string(self, value: str) -> Any:
        return self.element("HLAunicodeString", value)

    def octet(self, value: int) -> Any:
        return self.element("HLAoctet", value)

    def opaque_data(self, value: bytes | bytearray | memoryview | Sequence[int]) -> Any:
        return self.element("HLAopaqueData", value)

    def fixed_record(self, *elements: Any) -> Any:
        return self._python_type("HLAfixedRecord")(elements)

    def fixed_array(self, *elements: Any) -> Any:
        return self._python_type("HLAfixedArray")(elements)

    def variable_array(self, *elements: Any) -> Any:
        return self._python_type("HLAvariableArray")(elements)

    def variant_record(self, discriminant: Any, value: Any, *, extendable: bool = False) -> Any:
        type_name = "HLAextendableVariantRecord" if extendable else "HLAvariantRecord"
        record = self._python_type(type_name)(discriminant)
        set_variant = getattr(record, "setVariant", None)
        if not callable(set_variant):
            raise BackendConversionError(f"Python binding data element {type_name!r} does not support setVariant")
        set_variant(discriminant, value)
        return record

    def encode(self, value: Any) -> bytes:
        return self._oracle().encode_python_data_element(value)

    def byte_array(self, value: Any) -> Any:
        return self.backend.bridge.byte_array(self.encode(value))


class JavaRTIBackend(RTIBackend):
    """RTIBackend implementation for an already-created Java RTIambassador."""

    def __init__(
        self,
        *,
        java_rti_ambassador: Any,
        bridge: JavaBridge,
        java_factory: Any | None = None,
        converter: HLAJavaValueAdapter | None = None,
        info: BackendInfo | None = None,
        connect_local_settings_designator: str | None = None,
        invocation_resolver: JavaInvocationResolver | None = None,
    ) -> None:
        self.java_rti_ambassador = java_rti_ambassador
        self.bridge = bridge
        self.java_factory = java_factory
        self._java_encoder_oracle: JavaEncoderOracle | None = None
        self._vendor_encoding: JavaVendorEncoding | None = None
        self.converter = converter or HLAJavaValueAdapter(
            bridge,
            rti_ambassador=java_rti_ambassador,
            java_encoder_oracle=self.java_encoder_oracle,
        )
        self.converter.rti_ambassador = java_rti_ambassador
        self.converter.java_encoder_oracle = self.java_encoder_oracle
        self.info = info or BackendInfo(name=bridge.name, kind="java")
        self.connect_local_settings_designator = connect_local_settings_designator
        self.invocation_resolver = invocation_resolver or resolve_java_invocation
        self._connected_ambassador_proxies: list[tuple[NullFederateAmbassador, PythonFederateAmbassadorDispatcher, Any]] = []

    def invoke(self, invocation: Invocation) -> Any:
        if (
            invocation.method_name == "connect"
            and self.connect_local_settings_designator
            and len(invocation.args) == 2
            and not invocation.kwargs
        ):
            invocation = Invocation(
                method_name=invocation.method_name,
                args=(*invocation.args, self.connect_local_settings_designator),
                kwargs=invocation.kwargs,
                overloads=invocation.overloads,
            )
        resolved = self.invocation_resolver(invocation)
        backend_args = self.converter.to_backend_args(
            resolved.args,
            expected_type_names=resolved.param_types,
            strict_container_shapes=resolved.strict_container_shapes,
        )
        result = self.bridge.call(self.java_rti_ambassador, invocation.method_name, *backend_args)
        return self.converter.from_backend(result, expected_type_name=expected_java_return_type(invocation))

    def adapt_federate_ambassador(self, ambassador: NullFederateAmbassador) -> Any:
        dispatcher = PythonFederateAmbassadorDispatcher(ambassador, self.converter)
        proxy = self.bridge.create_federate_proxy(dispatcher)
        self._connected_ambassador_proxies.append((ambassador, dispatcher, proxy))
        return proxy

    def close(self) -> None:
        close = getattr(self.bridge, "close", None)
        if callable(close):
            close()

    @property
    def java_encoder_oracle(self) -> JavaEncoderOracle | None:
        if self.java_factory is None:
            return None
        if self._java_encoder_oracle is None:
            self._java_encoder_oracle = JavaEncoderOracle(self.bridge, self.bridge.encoder_factory(self.java_factory))
        return self._java_encoder_oracle

    @property
    def vendor_encoding(self) -> JavaVendorEncoding:
        if self._vendor_encoding is None:
            self._vendor_encoding = JavaVendorEncoding(self)
        return self._vendor_encoding

    def translate_exception(self, exc: BaseException, invocation: Invocation) -> RTIexception:
        if isinstance(exc, RTIexception):
            return exc

        simple_name = self.bridge.exception_class_name(exc)
        if simple_name:
            simple_name = simple_name.split(".")[-1].split("$")[-1]
            py_exc_type = getattr(hla_exceptions, simple_name, None)
            if isinstance(py_exc_type, type) and issubclass(py_exc_type, RTIexception):
                return py_exc_type(self.bridge.exception_message(exc), cause=exc)

        return RTIinternalError(
            f"Java backend failed during {invocation.method_name}: {self.bridge.exception_message(exc)}",
            cause=exc,
        )


__all__ = [
    "GenericJavaValueAdapter",
    "HLAJavaValueAdapter",
    "JavaBridge",
    "JavaEncoderOracle",
    "JavaRTIBackend",
    "JavaVendorEncoding",
    "JavaValueConverter",
    "PythonFederateAmbassadorDispatcher",
    "expected_java_callback_parameter_types",
    "expected_java_return_type",
    "java_parameter_names",
    "java_parameter_types",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "ResolvedJavaInvocation",
]
