"""Shared Java value-adaptation layers.

This module intentionally separates:

- generic Java runtime shape adaptation
- HLA semantic adaptation layered on top
- a temporary compatibility facade for existing callers
"""
# pyright: reportMissingImports=false
from __future__ import annotations

import os
from collections.abc import Iterable as CollectionsIterable
from enum import Enum
from typing import Any, Iterable, Mapping, cast

from hla.backends.common import (
    BackendConversionError,
    NativeHandleRegistry,
    ValueConverter,
    clean_java_type_name,
    handle_type_from_java_class_name,
    handle_type_from_java_type_name,
)
from hla.backends.common.java_invocation_scoring import (
    _JAVA_HANDLE_SET_TYPES,
    _JAVA_HANDLE_VALUE_MAP_TYPES,
)

from .java_binding_profile import PythonJavaBindingProfile
from .java_logical_time import (
    JavaLogicalTimeAdapter,
    JavaLogicalTimeFactoryAdapter,
    JavaLogicalTimeIntervalAdapter,
    java_logical_time_to_bytes,
    wrap_java_logical_time_factory,
)


def _maybe_call_noarg(obj: Any, *names: str) -> Any:
    for name in names:
        attr = getattr(obj, name, None)
        if callable(attr):
            try:
                return attr()
            except Exception:
                pass
        elif attr is not None:
            return attr
    return None


def _sequence_for_java_array(value: Any) -> list[Any]:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return [value]
    if isinstance(value, CollectionsIterable):
        return list(value)
    return [value]


def _is_url_like(value: Any) -> bool:
    return isinstance(value, (str, os.PathLike)) or hasattr(value, "uri")


def _looks_like_java_list_family(type_name: str | None) -> bool:
    text = str(type_name or "")
    return any(token in text for token in ("List", "ArrayList", "URL[]"))


def _looks_like_java_set_family(type_name: str | None) -> bool:
    text = str(type_name or "")
    return "Set" in text and "List" not in text


_EXPLICIT_STANDARD_JAVA_CONTAINER_TYPES = frozenset(
    {
        "URL[]",
        "AttributeHandleSet",
        "DimensionHandleSet",
        "FederateHandleSet",
        "InteractionClassHandleSet",
        "RegionHandleSet",
        "AttributeHandleValueMap",
        "ParameterHandleValueMap",
        "AttributeSetRegionSetPairList",
    }
)


_JAVA_COMPOSITE_DATATYPE_NAMES = {
    "FederateHandleSaveStatusPair",
    "FederateRestoreStatus",
    "FederationExecutionInformation",
    "MessageRetractionReturn",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "TimeQueryReturn",
}


def _container_kind(value: Any) -> str | None:
    if isinstance(value, list):
        return "list"
    if isinstance(value, tuple):
        return "tuple"
    if isinstance(value, set):
        return "set"
    if isinstance(value, frozenset):
        return "frozenset"
    if isinstance(value, Mapping):
        return "mapping"
    return None


def _clean_java_type(type_name: str | None) -> str | None:
    return clean_java_type_name(type_name)


def _py_handle_set_by_java_type(binding: PythonJavaBindingProfile) -> dict[str, tuple[type[Any], str]]:
    return {
        "AttributeHandleSet": (binding.handles_module.AttributeHandleSet, "AttributeHandle"),
        "DimensionHandleSet": (binding.handles_module.DimensionHandleSet, "DimensionHandle"),
        "FederateHandleSet": (binding.handles_module.FederateHandleSet, "FederateHandle"),
        "InteractionClassHandleSet": (binding.handles_module.InteractionClassHandleSet, "InteractionClassHandle"),
        "RegionHandleSet": (binding.handles_module.RegionHandleSet, "RegionHandle"),
    }


def _py_handle_value_map_by_java_type(binding: PythonJavaBindingProfile) -> dict[str, tuple[type[Any], str]]:
    return {
        "AttributeHandleValueMap": (binding.handles_module.AttributeHandleValueMap, "AttributeHandle"),
        "ParameterHandleValueMap": (binding.handles_module.ParameterHandleValueMap, "ParameterHandle"),
    }


class GenericJavaValueAdapter(ValueConverter):
    """Generic Python <-> Java runtime shape adapter."""

    def __init__(
        self,
        bridge: Any,
        *,
        handle_registry: NativeHandleRegistry | None = None,
        rti_ambassador: Any | None = None,
        java_encoder_oracle: Any | None = None,
    ) -> None:
        super().__init__(handle_registry=handle_registry)
        self.bridge = bridge
        self.python_binding = bridge.python_binding
        self.rti_ambassador = rti_ambassador
        self.java_encoder_oracle = java_encoder_oracle
        self._logical_time_factory_adapter: JavaLogicalTimeFactoryAdapter | None = None

    def _conversion_error(self, expected_type_name: str, value: Any, detail: str) -> BackendConversionError:
        return BackendConversionError(
            f"Expected Java {expected_type_name} for bridge conversion; got {type(value).__name__}: {detail}"
        )

    def _strict_generic_container_error(self, value: Any, *, expected_type_name: str | None) -> BackendConversionError:
        container_kind = _container_kind(value) or type(value).__name__
        expected = _clean_java_type(expected_type_name)
        return BackendConversionError(
            "Deterministic Java route forbids generic container fallback for "
            f"{container_kind} when expected Java type is {expected or 'unspecified'}. "
            "Add an explicit standard container family mapping or route-specific conversion rule."
        )

    def to_backend(
        self,
        value: Any,
        *,
        expected_type_name: str | None = None,
        strict_container_shapes: bool = False,
    ) -> Any:
        expected = _clean_java_type(expected_type_name)

        if expected == "String":
            if not isinstance(value, str):
                raise self._conversion_error("String", value, "only exact Python str values are accepted")
            return value
        if expected == "byte[]":
            if not isinstance(value, (bytes, bytearray, memoryview)):
                raise self._conversion_error(
                    "byte[]",
                    value,
                    "expected bytes, bytearray, memoryview",
                )
        if isinstance(value, Enum):
            return self.to_backend_enum(value)
        if isinstance(value, bytes):
            return self.to_backend_bytes(value)
        if isinstance(value, bytearray):
            return self.to_backend_bytes(bytes(value))
        if isinstance(value, tuple):
            return tuple(self.to_backend(item, strict_container_shapes=strict_container_shapes) for item in value)
        if isinstance(value, list):
            if strict_container_shapes and expected not in _EXPLICIT_STANDARD_JAVA_CONTAINER_TYPES:
                raise self._strict_generic_container_error(value, expected_type_name=expected)
            return self.bridge.new_list(
                [self.to_backend(item, strict_container_shapes=strict_container_shapes) for item in value]
            )
        if isinstance(value, (set, frozenset)):
            if strict_container_shapes and expected not in _EXPLICIT_STANDARD_JAVA_CONTAINER_TYPES:
                raise self._strict_generic_container_error(value, expected_type_name=expected)
            return self.bridge.new_set(
                [self.to_backend(item, strict_container_shapes=strict_container_shapes) for item in value]
            )
        if isinstance(value, Mapping):
            if strict_container_shapes and expected not in _EXPLICIT_STANDARD_JAVA_CONTAINER_TYPES:
                raise self._strict_generic_container_error(value, expected_type_name=expected)
            return self.bridge.new_map(
                [
                    (
                        self.to_backend(k, strict_container_shapes=strict_container_shapes),
                        self.to_backend(v, strict_container_shapes=strict_container_shapes),
                    )
                    for k, v in value.items()
                ]
            )
        return super().to_backend(value)

    def to_backend_enum(self, value: Enum) -> Any:
        enum_class_name = f"{self.bridge.api_profile.java_package}.{value.__class__.__name__}"
        return self.bridge.enum_constant(enum_class_name, value.name)

    def to_backend_bytes(self, value: bytes) -> Any:
        return self.bridge.byte_array(value)

    def to_backend_args(
        self,
        args: Iterable[Any],
        expected_type_names: Iterable[str | None] | None = None,
        *,
        strict_container_shapes: bool = False,
    ) -> tuple[Any, ...]:
        expected = tuple(expected_type_names or ())
        return tuple(
            self.to_backend(
                arg,
                expected_type_name=expected[idx] if idx < len(expected) else None,
                strict_container_shapes=strict_container_shapes,
            )
            for idx, arg in enumerate(args)
        )

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if value is None:
            return None

        expected = _clean_java_type(expected_type_name)
        simple_name = self.bridge.simple_class_name(value)

        if self.bridge.is_byte_array(value):
            return self.bridge.to_python_bytes(value)

        map_items = self.bridge.java_map_items(value)
        if map_items is not None:
            return {
                self.from_backend(key): self.from_backend(item_value)
                for key, item_value in map_items
            }

        if isinstance(value, tuple):
            return tuple(self.from_backend(item) for item in value)
        if isinstance(value, list):
            return [self.from_backend(item) for item in value]
        if isinstance(value, (set, frozenset)):
            return {self.from_backend(item) for item in value}

        collection_values = self.bridge.java_collection_values(value)
        if collection_values is not None:
            class_text = " ".join(filter(None, [expected, simple_name, self.bridge.full_class_name(value)]))
            if _looks_like_java_list_family(class_text):
                return [self.from_backend(item) for item in collection_values]
            if _looks_like_java_set_family(class_text):
                return {self.from_backend(item) for item in collection_values}
            return {self.from_backend(item) for item in collection_values}

        return super().from_backend(value, expected_type_name=expected_type_name)


class HLAJavaValueAdapter(GenericJavaValueAdapter):
    """HLA semantic adapter layered on top of generic Java runtime conversion."""

    def _java_time_factory(self) -> JavaLogicalTimeFactoryAdapter | None:
        if self.rti_ambassador is None:
            return None
        if self._logical_time_factory_adapter is None:
            try:
                java_factory = self.bridge.call(self.rti_ambassador, "getTimeFactory")
            except Exception:
                return None
            self._logical_time_factory_adapter = wrap_java_logical_time_factory(
                self.bridge,
                java_factory,
                self.python_binding,
            )
        return self._logical_time_factory_adapter

    def _data_element_factory_method(self, value: Any) -> str | None:
        if type(value).__name__ in {"HLAfixedRecord", "HLAfixedArray", "HLAvariableArray", "HLAvariantRecord", "HLAextendableVariantRecord"}:
            return None
        method_name = f"create{type(value).__name__}"
        oracle = self.java_encoder_oracle
        if oracle is None or not hasattr(oracle.encoder_factory, method_name):
            return None
        if not callable(getattr(value, "getValue", None)) and not hasattr(value, "value"):
            return None
        return method_name

    def _data_element_value(self, value: Any) -> Any:
        getter = getattr(value, "getValue", None)
        if callable(getter):
            return getter()
        if hasattr(value, "value"):
            return getattr(value, "value")
        raise BackendConversionError(f"Cannot extract a value from Python data element {type(value).__name__}")

    def _encode_data_element_with_java_factory(self, value: Any) -> bytes | None:
        method_name = self._data_element_factory_method(value)
        if self.java_encoder_oracle is None:
            return None
        if method_name is not None:
            return self.java_encoder_oracle.encode_element(method_name, self._data_element_value(value))
        try:
            return self.java_encoder_oracle.encode_python_data_element(value)
        except BackendConversionError:
            return None

    def to_backend(
        self,
        value: Any,
        *,
        expected_type_name: str | None = None,
        strict_container_shapes: bool = False,
    ) -> Any:
        handle_type = self.python_binding.python_type_or_none("Handle")
        range_bounds_type = self.python_binding.python_type("RangeBounds")
        attribute_region_association_type = self.python_binding.python_type("AttributeRegionAssociation")
        rti_configuration_type = self.python_binding.python_type_or_none("RtiConfiguration")
        credentials_type = self.python_binding.python_type_or_none("Credentials")
        logical_time_types = tuple(
            self.python_binding.python_type(name)
            for name in ("HLAinteger64Time", "HLAinteger64Interval", "HLAfloat64Time", "HLAfloat64Interval")
        )

        expected = _clean_java_type(expected_type_name)

        if expected == "byte[]":
            encoded = self._encode_data_element_with_java_factory(value)
            if encoded is not None:
                return self.to_backend_bytes(encoded)

        if expected == "URL":
            if not _is_url_like(value):
                raise self._conversion_error(
                    "URL",
                    value,
                    "expected str, os.PathLike, or an object with a uri attribute",
                )
            return self.bridge.fom_url(value)
        if expected == "URL[]":
            values = _sequence_for_java_array(value)
            for index, item in enumerate(values):
                if not _is_url_like(item):
                    raise self._conversion_error(
                        "URL[]",
                        value,
                        f"item {index}={type(item).__name__} is not URL-like; expected str, os.PathLike, or an object with a uri attribute",
                    )
            return self.bridge.fom_url_array(values)
        if expected == "RtiConfiguration":
            return self.bridge.rti_configuration(value)
        if expected == "Credentials":
            return self.bridge.credentials(value)
        if rti_configuration_type is not None and isinstance(value, rti_configuration_type):
            return self.bridge.rti_configuration(value)
        if credentials_type is not None and isinstance(value, credentials_type):
            return self.bridge.credentials(value)

        if expected in _JAVA_HANDLE_SET_TYPES:
            if not isinstance(value, CollectionsIterable) or isinstance(value, (str, bytes, bytearray, memoryview, os.PathLike)):
                raise self._conversion_error(expected, value, "expected an iterable of handle values")
            values = [self.to_backend(item) for item in _sequence_for_java_array(value)]
            return self.bridge.new_handle_set(expected, values, rti_ambassador=self.rti_ambassador)

        if expected in _JAVA_HANDLE_VALUE_MAP_TYPES:
            if not isinstance(value, Mapping):
                raise self._conversion_error(expected, value, "expected a mapping of handle keys to byte[] values")
            items = [(self.to_backend(k), self.to_backend(v, expected_type_name="byte[]")) for k, v in value.items()]
            return self.bridge.new_handle_value_map(expected, items, rti_ambassador=self.rti_ambassador)

        if expected == "AttributeSetRegionSetPairList":
            if not isinstance(value, CollectionsIterable) or isinstance(value, (str, bytes, bytearray, memoryview, os.PathLike)):
                raise self._conversion_error(expected, value, "expected an iterable of AttributeRegionAssociation values")
            return self.bridge.new_attribute_set_region_set_pair_list(
                [self.to_backend(item) for item in _sequence_for_java_array(value)],
                rti_ambassador=self.rti_ambassador,
            )

        if handle_type is not None and isinstance(value, handle_type):
            return self.handle_registry.to_native(cast(Any, value))
        if isinstance(value, range_bounds_type):
            return self.bridge.range_bounds(value)
        if isinstance(value, attribute_region_association_type):
            association = cast(Any, value)
            return (
                self.to_backend(
                    association.ahset,
                    expected_type_name="AttributeHandleSet",
                    strict_container_shapes=strict_container_shapes,
                ),
                self.to_backend(
                    association.rhset,
                    expected_type_name="RegionHandleSet",
                    strict_container_shapes=strict_container_shapes,
                ),
            )
        if isinstance(value, (JavaLogicalTimeAdapter, JavaLogicalTimeIntervalAdapter)):
            return value.java_value
        if isinstance(value, logical_time_types):
            factory = self._java_time_factory()
            if factory is not None:
                return factory.to_java_value(value)
            return self.bridge.logical_time(value, rti_ambassador=self.rti_ambassador)
        return super().to_backend(
            value,
            expected_type_name=expected_type_name,
            strict_container_shapes=strict_container_shapes,
        )

    def from_backend(self, value: Any, *, expected_type_name: str | None = None) -> Any:
        if value is None:
            return None

        expected = _clean_java_type(expected_type_name)
        if expected == "LogicalTimeFactory":
            return wrap_java_logical_time_factory(self.bridge, value, self.python_binding)
        expected_handle_type = None if expected in _JAVA_COMPOSITE_DATATYPE_NAMES else handle_type_from_java_type_name(expected)
        if expected_handle_type is not None:
            return self.handle_registry.to_python(expected_handle_type, value)

        simple_name = self.bridge.simple_class_name(value)
        time_query_return = self._from_backend_time_query_return(value, expected_type_name=expected, simple_name=simple_name)
        if time_query_return is not None:
            return time_query_return

        message_retraction_return = self._from_backend_message_retraction_return(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if message_retraction_return is not None:
            return message_retraction_return

        save_status_pair = self._from_backend_federate_handle_save_status_pair(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if save_status_pair is not None:
            return save_status_pair

        restore_status = self._from_backend_federate_restore_status(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if restore_status is not None:
            return restore_status

        supplemental_reflect_type = self.python_binding.python_type_or_none("SupplementalReflectInfo")
        supplemental_reflect = self._from_backend_supplemental_reflect_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
            info_type=supplemental_reflect_type,
        )
        if supplemental_reflect is not None:
            return supplemental_reflect

        supplemental_receive_type = self.python_binding.python_type_or_none("SupplementalReceiveInfo")
        supplemental_receive = self._from_backend_supplemental_reflect_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
            info_type=supplemental_receive_type,
        )
        if supplemental_receive is not None:
            return supplemental_receive

        supplemental_remove = self._from_backend_supplemental_remove_info(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if supplemental_remove is not None:
            return supplemental_remove

        class_text = " ".join(filter(None, [simple_name, self.bridge.full_class_name(value)]))
        inferred_handle_type = handle_type_from_java_class_name(class_text)
        if inferred_handle_type is not None:
            return self.handle_registry.to_python(inferred_handle_type, value)

        handle_value_map_types = _py_handle_value_map_by_java_type(self.python_binding)
        handle_set_types = _py_handle_set_by_java_type(self.python_binding)
        python_enum_by_name = self.python_binding.enum_types_by_name()

        if expected in handle_value_map_types:
            map_items = self.bridge.java_map_items(value)
            if map_items is None and isinstance(value, Mapping):
                map_items = list(value.items())
            if map_items is not None:
                map_type, key_type_name = handle_value_map_types[expected]
                return map_type(
                    (
                        self.from_backend(key, expected_type_name=key_type_name),
                        self.from_backend(item_value),
                    )
                    for key, item_value in map_items
                )

        if expected in handle_set_types:
            collection_values = self.bridge.java_collection_values(value)
            if collection_values is None and isinstance(value, (list, tuple, set, frozenset)):
                collection_values = list(value)
            if collection_values is not None:
                set_type, item_type_name = handle_set_types[expected]
                return set_type(self.from_backend(item, expected_type_name=item_type_name) for item in collection_values)

        if expected == "FederationExecutionInformationSet":
            collection_values = self.bridge.java_collection_values(value)
            if collection_values is None and isinstance(value, (list, tuple, set, frozenset)):
                collection_values = list(value)
            if collection_values is not None:
                return {
                    self.from_backend(item, expected_type_name="FederationExecutionInformation")
                    for item in collection_values
                }

        if expected == "AttributeSetRegionSetPairList":
            collection_values = self.bridge.java_collection_values(value)
            if collection_values is None and isinstance(value, (list, tuple)):
                collection_values = list(value)
            if collection_values is not None:
                association_type = self.python_binding.python_type("AttributeRegionAssociation")
                rows: list[Any] = []
                for item in collection_values:
                    if isinstance(item, tuple) and len(item) == 2:
                        attr_values, region_values = item
                    else:
                        pair_values = self.bridge.java_collection_values(item)
                        if pair_values is None or len(pair_values) != 2:
                            continue
                        attr_values, region_values = pair_values
                    rows.append(
                        association_type(
                            self.from_backend(attr_values, expected_type_name="AttributeHandleSet"),
                            self.from_backend(region_values, expected_type_name="RegionHandleSet"),
                        )
                    )
                if rows:
                    return rows

        if simple_name in python_enum_by_name:
            member_name = self.bridge.enum_member_name(value)
            if member_name:
                enum_type = python_enum_by_name[simple_name]
                try:
                    return enum_type[member_name]
                except KeyError:
                    pass

        logical_time = self._from_backend_logical_time(value, expected_type_name=expected, simple_name=simple_name)
        if logical_time is not None:
            return logical_time

        range_bounds = self._from_backend_range_bounds(value, expected_type_name=expected, simple_name=simple_name)
        if range_bounds is not None:
            return range_bounds

        federation_execution_info = self._from_backend_federation_execution_information(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if federation_execution_info is not None:
            return federation_execution_info

        configuration_result = self._from_backend_configuration_result(
            value,
            expected_type_name=expected,
            simple_name=simple_name,
        )
        if configuration_result is not None:
            return configuration_result

        return super().from_backend(value, expected_type_name=expected_type_name)

    def _from_backend_logical_time(self, value: Any, *, expected_type_name: str | None, simple_name: str | None) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        is_expected_logical_time = expected_type_name in {"LogicalTime", "LogicalTimeInterval"}
        is_named_builtin = any(token in class_text for token in ("HLAinteger64Time", "HLAinteger64Interval", "HLAfloat64Time", "HLAfloat64Interval"))
        if not is_expected_logical_time and not is_named_builtin:
            return None

        factory = self._java_time_factory()
        is_interval = expected_type_name == "LogicalTimeInterval" or "Interval" in class_text
        if factory is not None:
            try:
                encoded = java_logical_time_to_bytes(self.bridge, value)
                return factory.decodeInterval(encoded) if is_interval else factory.decodeTime(encoded)
            except Exception:
                return factory.from_java_interval(value) if is_interval else factory.from_java_time(value)

        if is_named_builtin:
            raw = _maybe_call_noarg(value, "getValue", "value", "longValue", "doubleValue")
            if raw is None:
                return None
            if "HLAinteger64Time" in class_text:
                return self.python_binding.python_type("HLAinteger64Time")(int(raw))
            if "HLAinteger64Interval" in class_text:
                return self.python_binding.python_type("HLAinteger64Interval")(int(raw))
            if "HLAfloat64Time" in class_text:
                return self.python_binding.python_type("HLAfloat64Time")(float(raw))
            if "HLAfloat64Interval" in class_text:
                return self.python_binding.python_type("HLAfloat64Interval")(float(raw))
        return None

    def _from_backend_range_bounds(self, value: Any, *, expected_type_name: str | None, simple_name: str | None) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "RangeBounds" not in class_text:
            return None

        lower = _maybe_call_noarg(value, "getLowerBound", "lowerBound", "lower", "getLower")
        upper = _maybe_call_noarg(value, "getUpperBound", "upperBound", "upper", "getUpper")
        if lower is None or upper is None:
            return None
        return self.python_binding.python_type("RangeBounds")(int(lower), int(upper))

    def _from_backend_federation_execution_information(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederationExecutionInformation" not in class_text:
            return None

        federation_name = self.bridge.public_field(value, "federationExecutionName")
        logical_time_name = self.bridge.public_field(value, "logicalTimeImplementationName")
        if federation_name is None:
            return None
        return self.python_binding.python_type("FederationExecutionInformation")(
            federationExecutionName=str(federation_name),
            logicalTimeImplementationName=str(logical_time_name) if logical_time_name is not None else "",
        )

    def _from_backend_configuration_result(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "ConfigurationResult" not in class_text:
            return None

        configuration_used = self.bridge.public_field(value, "configurationUsed")
        if configuration_used is None:
            configuration_used = _maybe_call_noarg(value, "getConfigurationUsed", "isConfigurationUsed")
        address_used = self.bridge.public_field(value, "addressUsed")
        if address_used is None:
            address_used = _maybe_call_noarg(value, "getAddressUsed", "isAddressUsed")
        settings_result = self.bridge.public_field(value, "additionalSettingsResultCode")
        if settings_result is None:
            settings_result = self.bridge.public_field(value, "additionalSettingsResult")
        if settings_result is None:
            settings_result = _maybe_call_noarg(value, "getAdditionalSettingsResultCode", "getAdditionalSettingsResult")
        message = self.bridge.public_field(value, "message")
        if message is None:
            message = _maybe_call_noarg(value, "getMessage")
        if configuration_used is None or address_used is None or settings_result is None or message is None:
            return None
        return self.python_binding.python_type("ConfigurationResult")(
            bool(configuration_used),
            bool(address_used),
            self.from_backend(settings_result),
            str(message),
        )

    def _from_backend_time_query_return(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "TimeQueryReturn" not in class_text:
            return None

        valid = _maybe_call_noarg(value, "timeIsValid", "getTimeIsValid", "logicalTimeIsValid", "getLogicalTimeIsValid")
        if valid is None:
            return None
        raw_time = self.bridge.public_field(value, "time")
        if raw_time is None:
            raw_time = self.bridge.public_field(value, "logicalTime")
        if raw_time is None:
            raw_time = _maybe_call_noarg(value, "getTime", "getLogicalTime")
        return self.python_binding.python_type("TimeQueryReturn")(
            bool(valid),
            self.from_backend(raw_time, expected_type_name="LogicalTime") if raw_time is not None else None,
        )

    def _from_backend_message_retraction_return(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "MessageRetractionReturn" not in class_text:
            return None

        valid = _maybe_call_noarg(value, "retractionHandleIsValid", "getRetractionHandleIsValid", "messageRetractionHandleIsValid")
        handle = self.bridge.public_field(value, "handle")
        if handle is None:
            handle = self.bridge.public_field(value, "messageRetractionHandle")
        if handle is None:
            handle = _maybe_call_noarg(value, "getHandle", "getMessageRetractionHandle")
        if valid is None or handle is None:
            return None
        return self.python_binding.python_type("MessageRetractionReturn")(
            bool(valid),
            self.from_backend(handle, expected_type_name="MessageRetractionHandle"),
        )

    def _from_backend_federate_handle_save_status_pair(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederateHandleSaveStatusPair" not in class_text:
            return None

        handle = self.bridge.public_field(value, "handle")
        if handle is None:
            handle = self.bridge.public_field(value, "federateHandle")
        if handle is None:
            handle = _maybe_call_noarg(value, "getHandle", "getFederateHandle")
        status = self.bridge.public_field(value, "status")
        if status is None:
            status = self.bridge.public_field(value, "saveStatus")
        if status is None:
            status = _maybe_call_noarg(value, "getStatus", "getSaveStatus")
        if handle is None or status is None:
            return None
        return self.python_binding.python_type("FederateHandleSaveStatusPair")(
            self.from_backend(handle, expected_type_name="FederateHandle"),
            self.from_backend(status),
        )

    def _from_backend_federate_restore_status(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "FederateRestoreStatus" not in class_text:
            return None

        pre = self.bridge.public_field(value, "preRestoreHandle")
        if pre is None:
            pre = _maybe_call_noarg(value, "getPreRestoreHandle")
        post = self.bridge.public_field(value, "postRestoreHandle")
        if post is None:
            post = _maybe_call_noarg(value, "getPostRestoreHandle")
        status = self.bridge.public_field(value, "status")
        if status is None:
            status = self.bridge.public_field(value, "restoreStatus")
        if status is None:
            status = _maybe_call_noarg(value, "getStatus", "getRestoreStatus")
        if pre is None or post is None or status is None:
            return None
        return self.python_binding.python_type("FederateRestoreStatus")(
            self.from_backend(pre, expected_type_name="FederateHandle"),
            self.from_backend(post, expected_type_name="FederateHandle"),
            self.from_backend(status),
        )

    def _from_backend_supplemental_reflect_info(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
        info_type: type[Any] | None = None,
    ) -> Any | None:
        if info_type is None:
            info_type = self.python_binding.python_type("SupplementalReflectInfo")
        info_type = cast(type[Any], info_type)
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if info_type.__name__ not in class_text:
            return None

        has_producing = _maybe_call_noarg(
            value,
            "hasProducingFederate",
            "getHasProducingFederate",
            "producingFederateIsValid",
            "getProducingFederateIsValid",
        )
        has_sent = _maybe_call_noarg(
            value,
            "hasSentRegions",
            "getHasSentRegions",
            "sentRegionsIsValid",
            "getSentRegionsIsValid",
            "conveyedRegionsIsValid",
            "getConveyedRegionsIsValid",
        )
        producing = self.bridge.public_field(value, "producingFederate")
        if producing is None:
            producing = _maybe_call_noarg(value, "getProducingFederate")
        sent_regions = self.bridge.public_field(value, "sentRegions")
        if sent_regions is None:
            sent_regions = self.bridge.public_field(value, "conveyedRegions")
        if sent_regions is None:
            sent_regions = _maybe_call_noarg(value, "getSentRegions", "getConveyedRegions")
        if has_producing is None:
            return None
        return info_type(
            hasProducingFederateValue=bool(has_producing),
            hasSentRegionsValue=bool(has_sent) if has_sent is not None else False,
            producingFederate=self.from_backend(producing, expected_type_name="FederateHandle") if producing is not None else None,
            sentRegions=self.from_backend(sent_regions, expected_type_name="RegionHandleSet") if sent_regions is not None else None,
        )

    def _from_backend_supplemental_remove_info(
        self,
        value: Any,
        *,
        expected_type_name: str | None,
        simple_name: str | None,
    ) -> Any | None:
        class_text = " ".join(filter(None, [expected_type_name, simple_name, self.bridge.full_class_name(value)]))
        if "SupplementalRemoveInfo" not in class_text:
            return None

        has_producing = _maybe_call_noarg(
            value,
            "hasProducingFederate",
            "getHasProducingFederate",
            "producingFederateIsValid",
            "getProducingFederateIsValid",
        )
        producing = self.bridge.public_field(value, "producingFederate")
        if producing is None:
            producing = _maybe_call_noarg(value, "getProducingFederate")
        if has_producing is None:
            return None
        return self.python_binding.python_type("SupplementalRemoveInfo")(
            hasProducingFederateValue=bool(has_producing),
            producingFederate=self.from_backend(producing, expected_type_name="FederateHandle") if producing is not None else None,
        )
