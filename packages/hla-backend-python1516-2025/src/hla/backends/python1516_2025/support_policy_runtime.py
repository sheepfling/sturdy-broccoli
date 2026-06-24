"""Shared support-policy and MOM reporting semantics for the Python 2025 RTI lane."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from hla.rti1516_2025.enums import ResignAction, ServiceGroup
from hla.rti1516_2025.exceptions import InvalidServiceGroup, RTIinternalError


def serialize_mom_service_report(
    backend: Any,
    service_name: str,
    *,
    success: bool = True,
    exception: str | None = None,
    arguments: Mapping[str, Any] | None = None,
    returned: Mapping[str, Any] | None = None,
    result: Any = None,
) -> dict[str, Any]:
    if not isinstance(service_name, str) or not service_name:
        raise RTIinternalError("serializeMOMServiceReport requires a non-empty serviceName")
    backend._service_report_serial_number += 1
    returned_payload: Mapping[str, Any] = returned or ({"value": result} if result is not None else {})
    record = {
        "recordType": "MOMServiceReport",
        "spec": "IEEE 1516.1-2025",
        "serialNumber": backend._service_report_serial_number,
        "timestampUTC": datetime.now(timezone.utc).isoformat(),
        "federationName": backend._federation_name,
        "federateName": backend._federate_name,
        "federateHandle": backend._federate_handle.value if backend._federate_handle is not None else None,
        "service": service_name,
        "success": bool(success),
        "exception": exception or "",
        "arguments": {str(key): safe_report_arg(value) for key, value in dict(arguments or {}).items()},
        "returned": {str(key): safe_report_arg(value) for key, value in dict(returned_payload).items()},
        "serviceReportingEnabled": backend._switches["service_reporting"],
        "sendServiceReportsToFile": backend._switches["send_service_reports_to_file"],
    }
    backend._service_report_records.append(record)
    backend._deliver_mom_service_report(record)
    return dict(record)


def service_report_records_snapshot(backend: Any) -> tuple[dict[str, Any], ...]:
    return tuple(dict(record) for record in backend._service_report_records)


def normalize_service_group(service_group: Any) -> int:
    try:
        return int(service_group if isinstance(service_group, ServiceGroup) else ServiceGroup(service_group))
    except Exception as exc:
        raise InvalidServiceGroup(repr(service_group)) from exc


def get_switch(backend: Any, method_name: str, name: str) -> bool:
    backend._require_joined(method_name)
    return backend._switches[name]


def set_switch(backend: Any, method_name: str, name: str, value: bool) -> None:
    backend._require_joined(method_name)
    if not isinstance(value, bool):
        raise RTIinternalError(f"{method_name} requires a bool value")
    backend._switches[name] = value


def set_attribute_scope_advisory_switch(backend: Any, value: bool) -> None:
    set_switch(backend, "setAttributeScopeAdvisorySwitch", "attribute_scope_advisory", value)
    if value:
        federation = backend._federation_record()
        current_key = backend._current_federate_key()
        for key in tuple(federation.attribute_scope_state):
            if key[0] == current_key:
                federation.attribute_scope_state.pop(key, None)
        backend._evaluate_attribute_scope_advisories()


def get_automatic_resign_directive(backend: Any) -> ResignAction:
    return backend._automatic_resign_directive


def set_automatic_resign_directive(backend: Any, value: ResignAction) -> None:
    try:
        if isinstance(value, ResignAction):
            backend._automatic_resign_directive = value
        elif hasattr(value, "name"):
            backend._automatic_resign_directive = ResignAction[getattr(value, "name")]
        else:
            backend._automatic_resign_directive = ResignAction(value)
    except Exception as exc:
        raise RTIinternalError(f"setAutomaticResignDirective requires a ResignAction value; got {value!r}") from exc


def safe_report_arg(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Mapping):
        return {str(key): safe_report_arg(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset, list, tuple)):
        return [safe_report_arg(item) for item in value]
    if hasattr(value, "value") and isinstance(value.value, int):
        return {"type": type(value).__name__, "value": value.value}
    return repr(value)
