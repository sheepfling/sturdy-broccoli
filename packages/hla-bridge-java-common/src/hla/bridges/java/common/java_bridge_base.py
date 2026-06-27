"""Base bridge abstraction for Java-backed RTI routes."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping as CollectionsMapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast

from hla.backends.common import BackendConversionError
from .java_binding_profile import load_python_java_binding_profile

if TYPE_CHECKING:
    from .java_intake import JavaApiProfile
    from .java_callbacks import PythonFederateAmbassadorDispatcher


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
    """Bridge operations needed by Java-backed RTI backends."""

    name: str = "java"

    def __init__(self, api_profile: str | JavaApiProfile = "2010"):
        self.python_binding = load_python_java_binding_profile(api_profile)
        self.api_profile = self.python_binding.api_profile

    @abstractmethod
    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_federate_proxy(self, dispatcher: PythonFederateAmbassadorDispatcher) -> Any:
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


__all__ = ["JavaBridge"]
