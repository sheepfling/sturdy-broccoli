"""Py4J bridge for Java HLA RTI implementations.

Use this backend when the RTI lives in a separate JVM process or when a vendor
already exposes a Py4J gateway.  The module imports Py4J only when used.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .base import BackendInfo, BackendUnavailableError, CALLBACK_METHOD_NAMES
from .java_common import JavaBridge, JavaRTIBackend, PythonFederateAmbassadorDispatcher
from ..fom import module_uri


@dataclass(frozen=True)
class Py4JConfig:
    """Configuration for a Java RTI accessed through Py4J."""

    gateway: Any | None = None
    gateway_parameters: Mapping[str, Any] = field(default_factory=dict)
    callback_server_parameters: Mapping[str, Any] = field(default_factory=dict)
    rti_factory_name: str | None = None
    shutdown_gateway_on_close: bool = False


class Py4JFederateAmbassadorProxy:
    """Py4J callback object implementing hla.rti1516e.FederateAmbassador."""

    class Java:
        implements = ["hla.rti1516e.FederateAmbassador"]

    def __init__(self, dispatcher: PythonFederateAmbassadorDispatcher):
        self._dispatcher = dispatcher

    def _invoke(self, method_name: str, *args: Any) -> Any:
        return self._dispatcher._invoke_callback(method_name, *args)


def _make_py4j_callback(method_name: str):
    def _callback(self: Py4JFederateAmbassadorProxy, *args: Any) -> Any:
        return self._invoke(method_name, *args)

    _callback.__name__ = method_name
    _callback.__qualname__ = f"Py4JFederateAmbassadorProxy.{method_name}"
    return _callback


for _callback_name in CALLBACK_METHOD_NAMES:
    setattr(Py4JFederateAmbassadorProxy, _callback_name, _make_py4j_callback(_callback_name))


class Py4JBridge(JavaBridge):
    name = "py4j"

    def __init__(self, config: Py4JConfig = Py4JConfig()):
        self.config = config
        self.owns_gateway = False

        if config.gateway is not None:
            self.gateway = config.gateway
            return

        try:
            from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise BackendUnavailableError("Py4J backend requested, but py4j is not installed") from exc

        gateway_parameters = GatewayParameters(**dict(config.gateway_parameters))
        callback_parameters = CallbackServerParameters(**dict(config.callback_server_parameters))
        self.gateway = JavaGateway(
            gateway_parameters=gateway_parameters,
            callback_server_parameters=callback_parameters,
        )
        self.owns_gateway = True

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: PythonFederateAmbassadorDispatcher) -> Any:
        return Py4JFederateAmbassadorProxy(dispatcher)

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        current = self.gateway.jvm
        for part in enum_class_name.split("."):
            current = getattr(current, part)
        return getattr(current, member_name)

    def byte_array(self, data: bytes) -> Any:
        try:
            byte_type = self.gateway.jvm.Byte.TYPE
            arr = self.gateway.new_array(byte_type, len(data))
            for idx, item in enumerate(data):
                arr[idx] = item if item < 128 else item - 256
            return arr
        except Exception:
            # Some gateways do not expose primitive array creation cleanly.  Let
            # the RTI/vendor adapter decide whether bytearray is acceptable.
            return bytearray(data)

    def new_set(self, values: list[Any] | tuple[Any, ...]) -> Any:
        java_set = self.gateway.jvm.java.util.HashSet()
        for value in values:
            java_set.add(value)
        return java_set

    def new_list(self, values: list[Any] | tuple[Any, ...]) -> Any:
        java_list = self.gateway.jvm.java.util.ArrayList()
        for value in values:
            java_list.add(value)
        return java_list

    def new_map(self, items: list[tuple[Any, Any]] | tuple[tuple[Any, Any], ...]) -> Any:
        java_map = self.gateway.jvm.java.util.HashMap()
        for key, value in items:
            java_map.put(key, value)
        return java_map

    def fom_url(self, value: Any) -> Any:
        uri = module_uri(value)
        return self.gateway.jvm.java.net.URI(uri).toURL()

    def fom_url_array(self, values: list[Any] | tuple[Any, ...]) -> Any:
        URL = self.gateway.jvm.java.net.URL
        arr = self.gateway.new_array(URL, len(values))
        for idx, value in enumerate(values):
            arr[idx] = self.fom_url(value)
        return arr

    def _factory_collection(self, rti_ambassador: Any, factory_method: str, values: list[Any] | tuple[Any, ...], *, capacity: int | None = None) -> Any:
        factory = getattr(rti_ambassador, factory_method)()
        collection = factory.create(len(values)) if capacity is not None else factory.create()
        for value in values:
            add = getattr(collection, "add", None)
            if callable(add):
                add(value)
            else:
                collection.append(value)
        return collection

    def new_handle_set(self, type_name: str, values: list[Any] | tuple[Any, ...], *, rti_ambassador: Any | None = None) -> Any:
        methods = {
            "AttributeHandleSet": "getAttributeHandleSetFactory",
            "DimensionHandleSet": "getDimensionHandleSetFactory",
            "FederateHandleSet": "getFederateHandleSetFactory",
            "RegionHandleSet": "getRegionHandleSetFactory",
        }
        if rti_ambassador is not None and type_name in methods:
            try:
                return self._factory_collection(rti_ambassador, methods[type_name], values)
            except Exception:
                pass
        return self.new_set(values)

    def new_handle_value_map(self, type_name: str, items: list[tuple[Any, Any]] | tuple[tuple[Any, Any], ...], *, rti_ambassador: Any | None = None) -> Any:
        methods = {
            "AttributeHandleValueMap": "getAttributeHandleValueMapFactory",
            "ParameterHandleValueMap": "getParameterHandleValueMapFactory",
        }
        if rti_ambassador is not None and type_name in methods:
            try:
                factory = getattr(rti_ambassador, methods[type_name])()
                java_map = factory.create(len(items))
                for key, value in items:
                    java_map.put(key, value)
                return java_map
            except Exception:
                pass
        return self.new_map(items)

    def new_attribute_set_region_set_pair_list(self, values: list[Any] | tuple[Any, ...], *, rti_ambassador: Any | None = None) -> Any:
        if rti_ambassador is not None:
            try:
                return self._factory_collection(rti_ambassador, "getAttributeSetRegionSetPairListFactory", values, capacity=len(values))
            except Exception:
                pass
        return self.new_list(values)

    def logical_time(self, value: Any, *, rti_ambassador: Any | None = None) -> Any:
        try:
            from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
            if rti_ambassador is not None:
                try:
                    factory = rti_ambassador.getTimeFactory()
                    if isinstance(value, (HLAinteger64Time, HLAfloat64Time)) and hasattr(factory, "makeTime"):
                        raw = int(value.value) if isinstance(value, HLAinteger64Time) else float(value.value)
                        return factory.makeTime(raw)
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and hasattr(factory, "makeInterval"):
                        raw = int(value.value) if isinstance(value, HLAinteger64Interval) else float(value.value)
                        return factory.makeInterval(raw)
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and getattr(value, "is_zero")():
                        return factory.makeZero()
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and getattr(value, "is_epsilon")():
                        return factory.makeEpsilon()
                except Exception:
                    pass
            if isinstance(value, HLAinteger64Time):
                return self.gateway.jvm.hla.rti1516e.HLAinteger64Time(int(value.value))
            if isinstance(value, HLAinteger64Interval):
                return self.gateway.jvm.hla.rti1516e.HLAinteger64Interval(int(value.value))
            if isinstance(value, HLAfloat64Time):
                return self.gateway.jvm.hla.rti1516e.HLAfloat64Time(float(value.value))
            if isinstance(value, HLAfloat64Interval):
                return self.gateway.jvm.hla.rti1516e.HLAfloat64Interval(float(value.value))
        except Exception:
            return value
        return value

    def full_class_name(self, obj: Any) -> str | None:
        if obj is None:
            return None
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getName())
            except Exception:
                pass
        return super().full_class_name(obj)

    def simple_class_name(self, obj: Any) -> str | None:
        if obj is None:
            return None
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getSimpleName())
            except Exception:
                pass
        return super().simple_class_name(obj)

    def exception_class_name(self, exc: BaseException) -> str | None:
        java_exception = getattr(exc, "java_exception", None)
        if java_exception is not None:
            try:
                return str(java_exception.getClass().getSimpleName())
            except Exception:
                pass
        return super().exception_class_name(exc)

    def exception_message(self, exc: BaseException) -> str:
        java_exception = getattr(exc, "java_exception", None)
        if java_exception is not None:
            try:
                return str(java_exception.getMessage())
            except Exception:
                pass
        return str(exc)

    def close(self) -> None:
        if self.config.shutdown_gateway_on_close and self.owns_gateway:
            shutdown = getattr(self.gateway, "shutdown", None)
            if callable(shutdown):
                shutdown()


class Py4JRTIBackend(JavaRTIBackend):
    """JavaRTIBackend built from a Py4J Java RTIambassador."""


def create_py4j_backend(config: Py4JConfig = Py4JConfig()) -> Py4JRTIBackend:
    """Create a Java RTI backend using a Py4J gateway and RtiFactoryFactory."""

    bridge = Py4JBridge(config)
    try:
        factory_factory = bridge.gateway.jvm.hla.rti1516e.RtiFactoryFactory
        if config.rti_factory_name:
            factory = factory_factory.getRtiFactory(config.rti_factory_name)
        else:
            factory = factory_factory.getRtiFactory()
        java_rti = factory.getRtiAmbassador()
        try:
            name = str(factory.rtiName())
        except Exception:
            name = "py4j"
        try:
            version = str(factory.rtiVersion())
        except Exception:
            version = None
    except BaseException:
        bridge.close()
        raise

    info = BackendInfo(
        name=name,
        kind="java/py4j",
        version=version,
        details={"rti_factory_name": config.rti_factory_name},
    )
    return Py4JRTIBackend(java_rti_ambassador=java_rti, bridge=bridge, info=info)


def rti_ambassador(config: Py4JConfig = Py4JConfig()):
    """Convenience: return a DelegatingRTIAmbassador backed by Py4J."""
    from .base import make_rti_ambassador

    return make_rti_ambassador(create_py4j_backend(config))


__all__ = [
    "Py4JBridge",
    "Py4JConfig",
    "Py4JFederateAmbassadorProxy",
    "Py4JRTIBackend",
    "create_py4j_backend",
    "rti_ambassador",
]
