"""Shared Java RTI backend support.

Concrete bridge packages, such as the JPype and Py4J bridge packages, supply
the mechanics for their Java bridge.
This module supplies backend composition for Java-backed RTI routes.
Bridge abstraction, callback dispatch, encoding helpers, and value adapters
live in dedicated sibling modules.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hla.backends.common import (
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
from .java_bridge_base import JavaBridge
from .java_callbacks import (
    FederateInternalError,
    PythonFederateAmbassadorDispatcher,
    _DEFAULT_BINDING as _CALLBACK_BINDING,
    expected_java_callback_parameter_types,
    expected_java_return_type,
)
from .java_encoding import JavaEncoderOracle, JavaVendorEncoding
from .java_value_adapter import GenericJavaValueAdapter, HLAJavaValueAdapter

if TYPE_CHECKING:
    from hla.rti1516e import NullFederateAmbassador

hla_exceptions = _CALLBACK_BINDING.exceptions_module
RTIexception = hla_exceptions.RTIexception
RTIinternalError = hla_exceptions.RTIinternalError


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
    "PythonFederateAmbassadorDispatcher",
    "expected_java_callback_parameter_types",
    "expected_java_return_type",
    "java_parameter_names",
    "java_parameter_types",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "ResolvedJavaInvocation",
]
