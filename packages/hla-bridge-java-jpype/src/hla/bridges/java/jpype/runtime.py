"""Runtime and bridge helpers for JPype-backed Java RTI backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from hla.bridges.java.common import BackendUnavailableError
from hla.bridges.java.common.java_common import JavaBridge, PythonFederateAmbassadorDispatcher
from hla.bridges.java.common.java_runtime import ensure_java_home
from hla.bridges.java.common.java_intake import JavaApiProfile


@dataclass(frozen=True)
class JPypeConfig:
    """Configuration for an in-process Java RTI accessed with JPype."""

    classpath: Sequence[str] = field(default_factory=tuple)
    jvm_args: Sequence[str] = field(default_factory=tuple)
    rti_factory_name: str | None = None
    connect_local_settings_designator: str | None = None
    start_jvm: bool = True
    shutdown_jvm_on_close: bool = False
    convert_strings: bool = False
    java_api_profile: str | JavaApiProfile = "2010"
    invocation_router: str = "weighted"


class JPypeBridge(JavaBridge):
    name = "jpype"

    def __init__(self, config: JPypeConfig = JPypeConfig()):
        super().__init__(config.java_api_profile)
        ensure_java_home()
        try:
            import jpype  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise BackendUnavailableError("JPype backend requested, but jpype is not installed") from exc

        self.jpype = jpype
        self.config = config
        self.started_here = False

        if config.start_jvm and not jpype.isJVMStarted():
            kwargs: dict[str, Any] = {"convertStrings": config.convert_strings}
            if config.classpath:
                kwargs["classpath"] = list(config.classpath)
            jpype.startJVM(*config.jvm_args, **kwargs)
            self.started_here = True

    def JClass(self, class_name: str) -> Any:
        return self.jpype.JClass(class_name)

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: PythonFederateAmbassadorDispatcher) -> Any:
        return self.jpype.JProxy(self.api_profile.federate_ambassador_interface, inst=dispatcher)

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        enum_class = self.JClass(enum_class_name)
        return getattr(enum_class, member_name)

    def byte_array(self, data: bytes) -> Any:
        JArray = self.jpype.JArray
        JByte = self.jpype.JByte
        return JArray(JByte)([(item if item < 128 else item - 256) for item in data])

    def new_set(self, values: Sequence[Any]) -> Any:
        java_set = self.JClass("java.util.HashSet")()
        for value in values:
            java_set.add(value)
        return java_set

    def new_list(self, values: Sequence[Any]) -> Any:
        java_list = self.JClass("java.util.ArrayList")()
        for value in values:
            java_list.add(value)
        return java_list

    def new_map(self, items: Sequence[tuple[Any, Any]]) -> Any:
        java_map = self.JClass("java.util.HashMap")()
        for key, value in items:
            java_map.put(key, value)
        return java_map

    def fom_url(self, value: Any) -> Any:
        uri = self.python_binding.fom_module.module_uri(value)
        return self.JClass("java.net.URI")(uri).toURL()

    def fom_url_array(self, values: Sequence[Any]) -> Any:
        URL = self.JClass("java.net.URL")
        return self.jpype.JArray(URL)([self.fom_url(value) for value in values])

    def _factory_collection(
        self,
        rti_ambassador: Any,
        factory_method: str,
        values: Sequence[Any],
        *,
        capacity: int | None = None,
    ) -> Any:
        factory = getattr(rti_ambassador, factory_method)()
        collection = factory.create(len(values) if capacity is not None else None) if capacity is not None else factory.create()
        for value in values:
            add = getattr(collection, "add", None)
            if callable(add):
                add(value)
            else:
                collection.append(value)
        return collection

    def new_handle_set(self, type_name: str, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
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

    def new_handle_value_map(self, type_name: str, items: Sequence[tuple[Any, Any]], *, rti_ambassador: Any | None = None) -> Any:
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

    def new_attribute_set_region_set_pair_list(self, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        if rti_ambassador is not None:
            try:
                return self._factory_collection(rti_ambassador, "getAttributeSetRegionSetPairListFactory", values, capacity=len(values))
            except Exception:
                pass
        return self.new_list(values)

    def logical_time(self, value: Any, *, rti_ambassador: Any | None = None) -> Any:
        try:
            HLAfloat64Interval = self.python_binding.python_type("HLAfloat64Interval")
            HLAfloat64Time = self.python_binding.python_type("HLAfloat64Time")
            HLAinteger64Interval = self.python_binding.python_type("HLAinteger64Interval")
            HLAinteger64Time = self.python_binding.python_type("HLAinteger64Time")

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
                return self.JClass(f"{self.api_profile.java_package}.HLAinteger64Time")(int(value.value))
            if isinstance(value, HLAinteger64Interval):
                return self.JClass(f"{self.api_profile.java_package}.HLAinteger64Interval")(int(value.value))
            if isinstance(value, HLAfloat64Time):
                return self.JClass(f"{self.api_profile.java_package}.HLAfloat64Time")(float(value.value))
            if isinstance(value, HLAfloat64Interval):
                return self.JClass(f"{self.api_profile.java_package}.HLAfloat64Interval")(float(value.value))
        except Exception:
            return value
        return value

    def range_bounds(self, value: Any) -> Any:
        try:
            return self.JClass(f"{self.api_profile.java_package}.RangeBounds")(int(value.lower_bound), int(value.upper_bound))
        except Exception:
            return value

    def rti_configuration(self, value: Any) -> Any:
        try:
            config = self.JClass(f"{self.api_profile.java_package}.RtiConfiguration").createConfiguration()
            configuration_name = getattr(value, "configuration_name", "")
            rti_address = getattr(value, "rti_address", "")
            additional_settings = getattr(value, "additional_settings", "")
            if configuration_name:
                config = config.withConfigurationName(str(configuration_name))
            if rti_address:
                config = config.withRtiAddress(str(rti_address))
            if additional_settings:
                config = config.withAdditionalSettings(str(additional_settings))
            return config
        except Exception:
            return value

    def credentials(self, value: Any) -> Any:
        try:
            credential_type = str(getattr(value, "type"))
            credential_data = bytes(getattr(value, "data"))
        except Exception:
            return value
        try:
            if credential_type == "HLAnoCredentials":
                return self.JClass(f"{self.api_profile.java_package}.auth.HLAnoCredentials")()
            if credential_type == "HLAplainTextPassword":
                return self.JClass(f"{self.api_profile.java_package}.auth.HLAplainTextPassword")(self.byte_array(credential_data))
        except Exception:
            pass
        try:
            return self.JClass(f"{self.api_profile.java_package}.Credentials")(credential_type, self.byte_array(credential_data))
        except Exception:
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
        get_class = getattr(exc, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getSimpleName())
            except Exception:
                pass
        java_class = getattr(exc, "javaClass", None)
        if java_class is not None:
            return str(java_class).split(".")[-1]
        return super().exception_class_name(exc)

    def exception_message(self, exc: BaseException) -> str:
        message = getattr(exc, "message", None)
        if message:
            return str(message)
        return str(exc)

    def close(self) -> None:
        if self.config.shutdown_jvm_on_close and self.started_here and self.jpype.isJVMStarted():
            self.jpype.shutdownJVM()


__all__ = ["JPypeBridge", "JPypeConfig"]
