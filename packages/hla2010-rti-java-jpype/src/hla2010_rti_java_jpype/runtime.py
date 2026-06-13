"""Runtime and bridge helpers for JPype-backed Java RTI backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from hla2010.fom import module_uri
from hla2010.types import RangeBounds
from hla2010_rti_java_common import BackendUnavailableError
from hla2010_rti_java_common.java_common import (
    JavaBridge,
    PythonFederateAmbassadorDispatcher,
    append_java_collection_value,
    convert_python_logical_time_with_factory,
    create_java_factory_collection,
    invoke_java_enum_constant,
    invoke_java_rti_method,
    invoke_java_time_factory,
    jpype_exception_class_name,
    java_handle_set_factory_method,
    java_handle_value_map_factory_method,
    java_runtime_full_class_name,
    java_runtime_simple_class_name,
    python_logical_time_shim_spec,
    put_java_map_entry,
)
from hla2010_rti_java_common.java_runtime import ensure_java_home


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


class JPypeBridge(JavaBridge):
    name = "jpype"

    def __init__(self, config: JPypeConfig = JPypeConfig()):
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
        return invoke_java_rti_method(obj, method_name, *args)

    def create_federate_proxy(self, dispatcher: PythonFederateAmbassadorDispatcher) -> Any:
        return self.jpype.JProxy("hla.rti1516e.FederateAmbassador", inst=dispatcher)

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        enum_class = self.JClass(enum_class_name)
        return invoke_java_enum_constant(enum_class, member_name)

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
        uri = module_uri(value)
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
        collection = create_java_factory_collection(
            rti_ambassador,
            factory_method,
            capacity=len(values) if capacity is not None else None,
        )
        for value in values:
            append_java_collection_value(collection, value)
        return collection

    def new_handle_set(self, type_name: str, values: Sequence[Any], *, rti_ambassador: Any | None = None) -> Any:
        if rti_ambassador is not None:
            try:
                return self._factory_collection(rti_ambassador, java_handle_set_factory_method(type_name), values)
            except Exception:
                pass
        return self.new_set(values)

    def new_handle_value_map(self, type_name: str, items: Sequence[tuple[Any, Any]], *, rti_ambassador: Any | None = None) -> Any:
        if rti_ambassador is not None:
            try:
                java_map = create_java_factory_collection(
                    rti_ambassador,
                    java_handle_value_map_factory_method(type_name),
                    capacity=len(items),
                )
                for key, value in items:
                    put_java_map_entry(java_map, key, value)
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
            if rti_ambassador is not None:
                try:
                    return convert_python_logical_time_with_factory(invoke_java_time_factory(rti_ambassador), value)
                except Exception:
                    pass
            class_name, raw = python_logical_time_shim_spec(value)
            return self.JClass(f"hla.rti1516e.{class_name}")(raw)
        except Exception:
            return value
        return value

    def range_bounds(self, value: RangeBounds) -> Any:
        try:
            return self.JClass("hla.rti1516e.RangeBounds")(int(value.lower_bound), int(value.upper_bound))
        except Exception:
            return value

    def full_class_name(self, obj: Any) -> str | None:
        return java_runtime_full_class_name(obj) if obj is not None else None

    def simple_class_name(self, obj: Any) -> str | None:
        return java_runtime_simple_class_name(obj) if obj is not None else None

    def exception_class_name(self, exc: BaseException) -> str | None:
        return jpype_exception_class_name(exc) or super().exception_class_name(exc)

    def exception_message(self, exc: BaseException) -> str:
        message = getattr(exc, "message", None)
        if message:
            return str(message)
        return str(exc)

    def close(self) -> None:
        if self.config.shutdown_jvm_on_close and self.started_here and self.jpype.isJVMStarted():
            self.jpype.shutdownJVM()


__all__ = ["JPypeBridge", "JPypeConfig"]
