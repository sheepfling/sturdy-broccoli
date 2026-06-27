"""Java encoder-factory helpers and vendor-facing encoding composition."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Sequence

from hla.backends.common import BackendConversionError


class JavaEncoderOracle:
    """Live Java ``EncoderFactory`` helper bound to one backend runtime."""

    def __init__(self, bridge: Any, encoder_factory: Any) -> None:
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

    def __init__(self, backend: Any) -> None:
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


__all__ = ["JavaEncoderOracle", "JavaVendorEncoding"]
