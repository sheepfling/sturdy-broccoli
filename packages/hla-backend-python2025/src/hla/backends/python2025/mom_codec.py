"""MOM parameter decoding helpers for the current Python 2025 RTI runtime."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Iterable, Mapping

from hla.rti1516_2025.enums import OrderType, ResignAction
from hla.rti1516_2025.exceptions import (
    InteractionParameterNotDefined,
    InvalidFederateHandle,
    RTIinternalError,
)
from hla.rti1516_2025.handles import AttributeHandle, ParameterHandle


def mom_request_params_by_name(
    rti: Any,
    interaction_class_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> dict[str, bytes]:
    names_by_handle = {value: name for name, value in rti._parameter_handles(interaction_class_name).items()}
    result: dict[str, bytes] = {}
    for handle, value in values_by_handle.items():
        handle_value = rti._normalize_handle(handle, ParameterHandle, InteractionParameterNotDefined)
        parameter_name = names_by_handle.get(handle_value)
        if parameter_name is not None:
            result[parameter_name] = bytes(value)
    return result


def mom_target_rti(rti: Any, params: Mapping[str, bytes]) -> Any:
    federation = rti._federation_record()
    federate_payload = params.get("HLAfederate")
    if federate_payload:
        try:
            federate_key = int(federate_payload.decode("ascii"))
        except ValueError as exc:
            raise InvalidFederateHandle(federate_payload.decode("ascii", errors="replace")) from exc
    else:
        federate_key = rti._current_federate_key()
    target = federation.member_rtis.get(federate_key)
    if target is None:
        raise InvalidFederateHandle(str(federate_key))
    return target


def mom_bool(value: bytes | None, default: bool) -> bool:
    if value is None:
        return default
    text = value.decode("ascii", errors="ignore").strip().lower()
    if text in {"1", "true", "yes", "hlatrue", "on"}:
        return True
    if text in {"0", "false", "no", "hlafalse", "off"}:
        return False
    raise RTIinternalError("Invalid MOM boolean value")


def mom_int(value: bytes | None, field_name: str) -> int:
    if value is None:
        raise RTIinternalError(f"Missing MOM parameter {field_name}")
    try:
        return int(value.decode("ascii").strip())
    except ValueError as exc:
        raise RTIinternalError(f"Invalid MOM handle value for {field_name}") from exc


def mom_attribute_handles(value: bytes | None) -> set[AttributeHandle]:
    if value is None:
        raise RTIinternalError("Missing MOM parameter HLAattributeList")
    text = value.decode("ascii", errors="ignore").strip()
    if not text:
        return set()
    normalized = text.translate(str.maketrans({char: "," for char in "[](); \t\n\r"}))
    return {AttributeHandle(int(part)) for part in normalized.split(",") if part}


def mom_text(value: bytes | None, field_name: str) -> str:
    if value is None:
        raise RTIinternalError(f"Missing MOM parameter {field_name}")
    return value.decode("utf-8")


def mom_number(value: bytes | None, field_name: str) -> int | float:
    if value is None:
        raise RTIinternalError(f"Missing MOM parameter {field_name}")
    text = value.decode("ascii", errors="ignore").strip()
    try:
        return float(text) if any(char in text for char in ".eE") else int(text)
    except ValueError as exc:
        raise RTIinternalError(f"Invalid MOM numeric value for {field_name}") from exc


def mom_handle_list_payload(values: Iterable[int]) -> bytes:
    return ",".join(str(value) for value in values).encode("ascii")


def mom_ownership_state(value: bytes | None, field_name: str) -> str:
    if value is None:
        raise RTIinternalError(f"Missing MOM parameter {field_name}")
    text = value.decode("ascii", errors="ignore").strip()
    normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").lower()
    if normalized in {"1", "owned", "owner", "ownedbyfederate", "attributeowned"}:
        return "owned"
    if normalized in {"0", "unowned", "notowned", "attributeisnotowned", "none"}:
        return "unowned"
    raise RTIinternalError(f"Invalid MOM ownership state for {field_name}")


def mom_order_type(value: bytes | None, field_name: str) -> OrderType:
    if value is None:
        raise RTIinternalError(f"Missing MOM parameter {field_name}")
    text = value.decode("ascii", errors="ignore").strip()
    try:
        mom_value = int(text)
    except ValueError:
        normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").upper()
        aliases = {
            "RECEIVE": OrderType.RECEIVE,
            "RO": OrderType.RECEIVE,
            "TIMESTAMP": OrderType.TIMESTAMP,
            "TSO": OrderType.TIMESTAMP,
        }
        if normalized in aliases:
            return aliases[normalized]
        raise RTIinternalError(f"Invalid MOM order type for {field_name}")
    if mom_value == 0:
        return OrderType.RECEIVE
    if mom_value == 1:
        return OrderType.TIMESTAMP
    try:
        return OrderType(mom_value)
    except ValueError as exc:
        raise RTIinternalError(f"Invalid MOM order type for {field_name}") from exc


def mom_resign_action(value: bytes | None) -> ResignAction:
    if value is None:
        return ResignAction.NO_ACTION
    text = value.decode("ascii", errors="ignore").strip()
    try:
        return ResignAction(int(text))
    except ValueError:
        normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").upper()
        aliases = {
            "NOACTION": ResignAction.NO_ACTION,
            "UNCONDITIONALLYDIVESTATTRIBUTES": ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
            "DELETEOBJECTS": ResignAction.DELETE_OBJECTS,
            "CANCELPENDINGOWNERSHIPACQUISITIONS": ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
            "DELETEOBJECTSTHENDIVEST": ResignAction.DELETE_OBJECTS_THEN_DIVEST,
            "CANCELTHENDELETETHENDIVEST": ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST,
        }
        if normalized in aliases:
            return aliases[normalized]
        raise RTIinternalError(f"Invalid MOM resign action {text!r}")


def mom_index(value: bytes | None) -> int:
    if not value:
        return 0
    try:
        return int(value.decode("ascii") or "0")
    except ValueError:
        return 0


def mom_module_data(modules: tuple[Any, ...], indicator: int) -> str:
    if indicator == 0:
        if len(modules) <= 1:
            return mom_single_module_data(modules[0] if modules else None)
        return "\n".join(
            module_text
            for module_text in (mom_single_module_data(module) for module in modules)
            if module_text
        )
    if not 0 <= indicator < len(modules):
        return ""
    return mom_single_module_data(modules[indicator])


def mom_single_module_data(module: Any | None) -> str:
    if module is None:
        return ""
    path = getattr(module, "path", None)
    if path is not None and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    if getattr(module, "parsed", False):
        fom = import_module("hla.rti1516e.fom")
        return fom.serialize_fom_module(module, edition="2025")
    return str(getattr(module, "uri", None) or getattr(module, "source", ""))
