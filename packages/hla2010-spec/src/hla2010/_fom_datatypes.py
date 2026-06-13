from __future__ import annotations

import struct
from typing import Any, Callable, Mapping

from .exceptions import CouldNotDecode
from ._fom_models import (
    ArrayDatatypeSpec,
    BasicDatatypeSpec,
    EnumeratedDatatypeSpec,
    FOMCatalog,
    FixedRecordDatatypeSpec,
    SimpleDatatypeSpec,
    VariantRecordDatatypeSpec,
)

_NA_DATATYPE_MARKERS = {"", "NA", "N/A"}


def _datatype_spec_lookup(
    name: str,
    catalog: FOMCatalog | Mapping[str, Any] | None,
    *,
    standard_catalog_factory: Callable[[], dict[str, Any]],
) -> Any | None:
    if not name:
        return None
    if isinstance(catalog, FOMCatalog):
        for mapping in (
            catalog.basic_datatypes,
            catalog.simple_datatypes,
            catalog.enumerated_datatypes,
            catalog.array_datatypes,
            catalog.fixed_record_datatypes,
            catalog.variant_record_datatypes,
        ):
            if name in mapping:
                return mapping[name]
    elif catalog is not None and name in dict(catalog):
        return dict(catalog)[name]
    return standard_catalog_factory().get(name)


def _decode_primitive_datatype(name: str, payload: bytes) -> tuple[int, Any]:
    from . import encoding as hla_encoding

    cls = getattr(hla_encoding, name, None)
    if cls is None:
        raise CouldNotDecode(f"Unsupported primitive datatype {name!r}")
    element = cls()
    try:
        element.decode(payload)
        return element.encoded_length(), getattr(element, "value", None)
    except Exception as exc:  # pragma: no cover - specific message is asserted at call sites
        raise CouldNotDecode(f"Could not decode payload as {name}") from exc


def _consume_runtime_builtin(payload: bytes, datatype_name: str) -> int | None:
    if datatype_name == "HLAopaqueData":
        return len(payload)
    if datatype_name == "HLAASCIIstring":
        try:
            _decode_primitive_datatype(datatype_name, payload)
            return len(payload)
        except CouldNotDecode:
            try:
                payload.decode("ascii")
                return len(payload)
            except Exception:
                return None
    if datatype_name == "HLAunicodeString":
        try:
            _decode_primitive_datatype(datatype_name, payload)
            return len(payload)
        except CouldNotDecode:
            try:
                payload.decode("utf-8")
                return len(payload)
            except Exception:
                return None
    try:
        consumed, _value = _decode_primitive_datatype(datatype_name, payload)
        return consumed
    except CouldNotDecode:
        return None


def _enum_name_for_decoded_value(spec: EnumeratedDatatypeSpec, decoded_value: Any) -> str | None:
    token = str(decoded_value)
    for enumerator in spec.enumerators:
        if token in enumerator.values:
            return enumerator.name
    return None


def _cardinality_extent(token: str) -> int | None:
    text = token.strip()
    if not text or text == "Dynamic":
        return None
    if text.isdigit():
        return int(text)
    if text.startswith("[") and text.endswith("]") and ".." in text:
        lower, upper = text[1:-1].split("..", 1)
        if lower.isdigit() and upper.isdigit():
            return max(0, int(upper) - int(lower) + 1)
    raise CouldNotDecode(f"Unsupported array cardinality component {token!r}")


def _cardinality_count(cardinality: str | None) -> int | None:
    if not cardinality:
        return None
    extents = [_cardinality_extent(token) for token in cardinality.split(",")]
    if any(extent is None for extent in extents):
        return None
    count = 1
    for extent in extents:
        assert extent is not None
        count *= extent
    return count


def _alternative_matches(enumerator_token: str, decoded_name: str | None, enum_order: Mapping[str, int]) -> bool:
    token = enumerator_token.strip()
    if not token or token == "HLAother":
        return False
    decoded = decoded_name or ""
    for part in [item.strip() for item in token.split(",") if item.strip()]:
        if part == decoded:
            return True
        if part.startswith("[") and part.endswith("]") and ".." in part:
            lower, upper = [item.strip() for item in part[1:-1].split("..", 1)]
            if decoded in enum_order and lower in enum_order and upper in enum_order:
                if enum_order[lower] <= enum_order[decoded] <= enum_order[upper]:
                    return True
    return False


def _consume_datatype_value(
    payload: bytes,
    datatype_name: str,
    catalog: FOMCatalog | Mapping[str, Any] | None,
    *,
    standard_catalog_factory: Callable[[], dict[str, Any]],
) -> int:
    if datatype_name in _NA_DATATYPE_MARKERS:
        return len(payload)
    builtin_consumed = _consume_runtime_builtin(payload, datatype_name)
    if builtin_consumed is not None:
        return builtin_consumed
    spec = _datatype_spec_lookup(
        datatype_name,
        catalog,
        standard_catalog_factory=standard_catalog_factory,
    )
    if spec is None:
        consumed, _value = _decode_primitive_datatype(datatype_name, payload)
        return consumed
    if isinstance(spec, BasicDatatypeSpec):
        consumed, _value = _decode_primitive_datatype(spec.name, payload)
        return consumed
    if isinstance(spec, SimpleDatatypeSpec):
        if not spec.representation:
            raise CouldNotDecode(f"Simple datatype {spec.name!r} has no representation")
        return _consume_datatype_value(
            payload,
            spec.representation,
            catalog,
            standard_catalog_factory=standard_catalog_factory,
        )
    if isinstance(spec, EnumeratedDatatypeSpec):
        if not spec.representation:
            raise CouldNotDecode(f"Enumerated datatype {spec.name!r} has no representation")
        consumed, value = _decode_primitive_datatype(spec.representation, payload)
        allowed = {member_value for enumerator in spec.enumerators for member_value in enumerator.values}
        if allowed and str(value) not in allowed:
            raise CouldNotDecode(f"Decoded value {value!r} is not valid for enumeration {spec.name!r}")
        return consumed
    if isinstance(spec, ArrayDatatypeSpec):
        if not spec.data_type:
            raise CouldNotDecode(f"Array datatype {spec.name!r} has no element datatype")
        encoding = spec.encoding or ""
        offset = 0
        if encoding == "HLAfixedArray":
            count = _cardinality_count(spec.cardinality)
            if count is None:
                raise CouldNotDecode(f"Fixed array datatype {spec.name!r} requires fixed cardinality")
            for _ in range(count):
                offset += _consume_datatype_value(
                    payload[offset:],
                    spec.data_type,
                    catalog,
                    standard_catalog_factory=standard_catalog_factory,
                )
            return offset
        if encoding == "HLAvariableArray":
            if len(payload) < 4:
                raise CouldNotDecode(f"Variable array datatype {spec.name!r} is missing its element count")
            count = struct.unpack(">I", payload[:4])[0]
            offset = 4
            for _ in range(count):
                offset += _consume_datatype_value(
                    payload[offset:],
                    spec.data_type,
                    catalog,
                    standard_catalog_factory=standard_catalog_factory,
                )
            return offset
        raise CouldNotDecode(f"Unsupported array encoding {encoding!r} for datatype {spec.name!r}")
    if isinstance(spec, FixedRecordDatatypeSpec):
        offset = 0
        for field in spec.fields:
            if not field.data_type:
                raise CouldNotDecode(f"Fixed record field {spec.name}.{field.name} has no datatype")
            offset += _consume_datatype_value(
                payload[offset:],
                field.data_type,
                catalog,
                standard_catalog_factory=standard_catalog_factory,
            )
        return offset
    if isinstance(spec, VariantRecordDatatypeSpec):
        if not spec.data_type:
            raise CouldNotDecode(f"Variant record datatype {spec.name!r} has no discriminant datatype")
        discriminant_consumed = _consume_datatype_value(
            payload,
            spec.data_type,
            catalog,
            standard_catalog_factory=standard_catalog_factory,
        )
        discriminant_spec = _datatype_spec_lookup(
            spec.data_type,
            catalog,
            standard_catalog_factory=standard_catalog_factory,
        )
        decoded_name: str | None = None
        if isinstance(discriminant_spec, EnumeratedDatatypeSpec) and discriminant_spec.representation:
            _, discriminant_value = _decode_primitive_datatype(discriminant_spec.representation, payload)
            decoded_name = _enum_name_for_decoded_value(discriminant_spec, discriminant_value)
            enum_order = {enumerator.name: index for index, enumerator in enumerate(discriminant_spec.enumerators)}
        else:
            enum_order = {}
        remainder = payload[discriminant_consumed:]
        for alternative in spec.alternatives:
            if _alternative_matches(alternative.enumerator, decoded_name, enum_order):
                if not alternative.data_type:
                    return discriminant_consumed
                return discriminant_consumed + _consume_datatype_value(
                    remainder,
                    alternative.data_type,
                    catalog,
                    standard_catalog_factory=standard_catalog_factory,
                )
        for alternative in spec.alternatives:
            if alternative.enumerator.strip() == "HLAother":
                if not alternative.data_type:
                    return discriminant_consumed
                return discriminant_consumed + _consume_datatype_value(
                    remainder,
                    alternative.data_type,
                    catalog,
                    standard_catalog_factory=standard_catalog_factory,
                )
        return discriminant_consumed
    raise CouldNotDecode(f"Unsupported datatype declaration for {datatype_name!r}")


def validate_encoded_datatype_value(
    payload: bytes,
    datatype_name: str,
    catalog: FOMCatalog | Mapping[str, Any] | None = None,
    *,
    standard_catalog_factory: Callable[[], dict[str, Any]],
) -> None:
    consumed = _consume_datatype_value(
        bytes(payload),
        datatype_name,
        catalog,
        standard_catalog_factory=standard_catalog_factory,
    )
    if consumed != len(payload):
        raise CouldNotDecode(f"Decoded {consumed} bytes for datatype {datatype_name!r}, trailing payload remains")
