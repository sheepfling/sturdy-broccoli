"""Java-profile CERTI backends built on top of the real native CERTI adapter.

CERTI does not provide a usable Java IEEE 1516.1-2010 RTI in this workspace.
To exercise the same Java-adapter path used by JPype/Py4J without changing the
Python federate surface, this module wraps the working native CERTI backend in a
small Java-shaped facade.

The result is still real CERTI on the transport side:

* RTIG/RTIA/native IEEE 1516.1-2010 services are provided by the existing
  :mod:`hla2010.backends.certi_backend` helper path.
* The Python application still talks to :class:`DelegatingRTIAmbassador`.
* The call path goes through :class:`hla2010.backends.java_common.JavaRTIBackend`
  using a JPype-like or Py4J-like bridge profile.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .base import CALLBACK_METHOD_NAMES, BackendInfo, lower_camel_to_snake, make_rti_ambassador
from .certi_backend import CERTIConfig, create_certi_backend
from .java_common import JavaRTIBackend, JavaValueConverter
from ..api import FederateAmbassador
from ..enums import CallbackModel, OrderType, ResignAction
from ..handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from ..testing.java_shim import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaEnumConstant,
    JavaFederateHandle,
    JavaHLAinteger64Interval,
    JavaHLAinteger64Time,
    JavaInteractionClassHandle,
    JavaLikeException,
    JavaLikeObject,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
    JavaParameterHandle,
    JavaTransportationTypeHandle,
    ShimJavaBridge,
)
from ..time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time


def _python_bytes(value: Any) -> bytes:
    if isinstance(value, JavaByteArray):
        return bytes((int(item) + 256) % 256 for item in value)
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return bytes((int(item) + 256) % 256 for item in value)


def _from_java_like(value: Any) -> Any:
    if isinstance(value, JavaByteArray):
        return _python_bytes(value)
    if isinstance(value, dict):
        return {_from_java_like(key): _from_java_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_from_java_like(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_from_java_like(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return {_from_java_like(item) for item in value}
    if isinstance(value, JavaFederateHandle):
        return FederateHandle(int(value.value))
    if isinstance(value, JavaObjectClassHandle):
        return ObjectClassHandle(int(value.value))
    if isinstance(value, JavaAttributeHandle):
        return AttributeHandle(int(value.value))
    if isinstance(value, JavaObjectInstanceHandle):
        return ObjectInstanceHandle(int(value.value))
    if isinstance(value, JavaInteractionClassHandle):
        return InteractionClassHandle(int(value.value))
    if isinstance(value, JavaParameterHandle):
        return ParameterHandle(int(value.value))
    if isinstance(value, JavaTransportationTypeHandle):
        return TransportationTypeHandle(int(value.value))
    if isinstance(value, JavaHLAinteger64Time):
        return HLAinteger64Time(int(value.value))
    if isinstance(value, JavaHLAinteger64Interval):
        return HLAinteger64Interval(int(value.value))
    if isinstance(value, JavaLikeObject):
        if value.simple_name == "HLAfloat64Time":
            return HLAfloat64Time(float(value.value))
        if value.simple_name == "HLAfloat64Interval":
            return HLAfloat64Interval(float(value.value))
        if value.simple_name == "CallbackModel":
            return CallbackModel[str(value.value)]
        if value.simple_name == "OrderType":
            return OrderType[str(value.value)]
        if value.simple_name == "ResignAction":
            return ResignAction[str(value.value)]
    return value


def _to_java_like(value: Any) -> Any:
    if isinstance(value, bytes):
        return JavaByteArray(value)
    if isinstance(value, bytearray):
        return JavaByteArray(bytes(value))
    if isinstance(value, memoryview):
        return JavaByteArray(value.tobytes())
    if isinstance(value, dict):
        return {_to_java_like(key): _to_java_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_java_like(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_to_java_like(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return {_to_java_like(item) for item in value}
    if isinstance(value, FederateHandle):
        return JavaFederateHandle(int(value.value))
    if isinstance(value, ObjectClassHandle):
        return JavaObjectClassHandle(int(value.value))
    if isinstance(value, AttributeHandle):
        return JavaAttributeHandle(int(value.value))
    if isinstance(value, ObjectInstanceHandle):
        return JavaObjectInstanceHandle(int(value.value))
    if isinstance(value, InteractionClassHandle):
        return JavaInteractionClassHandle(int(value.value))
    if isinstance(value, ParameterHandle):
        return JavaParameterHandle(int(value.value))
    if isinstance(value, TransportationTypeHandle):
        return JavaTransportationTypeHandle(int(value.value))
    if isinstance(value, HLAinteger64Time):
        return JavaHLAinteger64Time(int(value.value))
    if isinstance(value, HLAinteger64Interval):
        return JavaHLAinteger64Interval(int(value.value))
    if isinstance(value, HLAfloat64Time):
        return JavaLikeObject("HLAfloat64Time", float(value.value))
    if isinstance(value, HLAfloat64Interval):
        return JavaLikeObject("HLAfloat64Interval", float(value.value))
    if isinstance(value, Enum):
        return JavaEnumConstant(type(value).__name__, value.name)
    return value


class _CERTIJavaFederateAdapter(FederateAmbassador):
    """Adapter that forwards native CERTI callbacks into a Java-style proxy."""

    def __init__(self, java_proxy: Any) -> None:
        self._java_proxy = java_proxy

    def _forward_callback(self, method_name: str, *args: Any) -> Any:
        callback = getattr(self._java_proxy, method_name)
        return callback(*(_to_java_like(arg) for arg in args))


def _make_adapter_callback(method_name: str):
    def _callback(self: _CERTIJavaFederateAdapter, *args: Any) -> Any:
        return self._forward_callback(method_name, *args)

    _callback.__name__ = method_name
    _callback.__qualname__ = f"_CERTIJavaFederateAdapter.{method_name}"
    return _callback


for _callback_name in CALLBACK_METHOD_NAMES:
    setattr(_CERTIJavaFederateAdapter, _callback_name, _make_adapter_callback(_callback_name))
    setattr(_CERTIJavaFederateAdapter, lower_camel_to_snake(_callback_name), _make_adapter_callback(_callback_name))


class CERTIJavaValueConverter(JavaValueConverter):
    """Converter for the CERTI Java-profile shim that preserves numeric handles."""

    def to_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if isinstance(value, FederateHandle):
            return JavaFederateHandle(int(value.value))
        if isinstance(value, ObjectClassHandle):
            return JavaObjectClassHandle(int(value.value))
        if isinstance(value, AttributeHandle):
            return JavaAttributeHandle(int(value.value))
        if isinstance(value, ObjectInstanceHandle):
            return JavaObjectInstanceHandle(int(value.value))
        if isinstance(value, InteractionClassHandle):
            return JavaInteractionClassHandle(int(value.value))
        if isinstance(value, ParameterHandle):
            return JavaParameterHandle(int(value.value))
        if isinstance(value, TransportationTypeHandle):
            return JavaTransportationTypeHandle(int(value.value))
        return super().to_backend(value, expected_type_name=expected_type_name)

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if isinstance(value, JavaFederateHandle):
            return FederateHandle(int(value.value))
        if isinstance(value, JavaObjectClassHandle):
            return ObjectClassHandle(int(value.value))
        if isinstance(value, JavaAttributeHandle):
            return AttributeHandle(int(value.value))
        if isinstance(value, JavaObjectInstanceHandle):
            return ObjectInstanceHandle(int(value.value))
        if isinstance(value, JavaInteractionClassHandle):
            return InteractionClassHandle(int(value.value))
        if isinstance(value, JavaParameterHandle):
            return ParameterHandle(int(value.value))
        if isinstance(value, JavaTransportationTypeHandle):
            return TransportationTypeHandle(int(value.value))
        return super().from_backend(value, expected_type_name=expected_type_name)


@dataclass
class CERTIJavaRTIShim:
    """Java-shaped facade for a real CERTI-backed RTI ambassador."""

    profile: str
    config: CERTIConfig = CERTIConfig()

    def __post_init__(self) -> None:
        self._rti = make_rti_ambassador(create_certi_backend(self.config))
        self._java_proxy = None

    def __getattr__(self, name: str):
        target = getattr(self._rti, name, None)
        if target is None:
            raise AttributeError(name)

        def _invoke(*args: Any) -> Any:
            py_args = tuple(_from_java_like(arg) for arg in args)
            result = target(*py_args)
            return _to_java_like(result)

        return _invoke

    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        self._java_proxy = federateReference
        python_ambassador = _CERTIJavaFederateAdapter(federateReference)
        callback_model = _from_java_like(callbackModel)
        if localSettingsDesignator is None:
            self._rti.connect(python_ambassador, callback_model)
        else:
            self._rti.connect(python_ambassador, callback_model, localSettingsDesignator)

    def close(self) -> None:
        self._rti.close()

    def getHLAversion(self) -> str:
        return self._rti.getHLAversion()


def create_certi_java_backend(profile: str, config: CERTIConfig = CERTIConfig()) -> JavaRTIBackend:
    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name="CERTI",
        kind=f"java/{profile}/certi-shim",
        version=None,
        details={"profile": profile, "transport": "native-certi"},
    )
    return JavaRTIBackend(
        java_rti_ambassador=CERTIJavaRTIShim(profile=profile, config=config),
        bridge=bridge,
        converter=CERTIJavaValueConverter(bridge),
        info=info,
    )


__all__ = ["CERTIJavaRTIShim", "create_certi_java_backend"]
