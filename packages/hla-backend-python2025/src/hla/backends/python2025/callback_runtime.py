from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.exceptions import (
    InvalidFederateHandle,
    InvalidObjectInstanceHandle,
    RTIinternalError,
)
from hla.rti1516_2025.handles import FederateHandle, ObjectInstanceHandle


@dataclass(slots=True)
class QueuedCallback:
    target_federate: FederateHandle | None
    method_name: str
    args: tuple[Any, ...]


def _callback_requires_evocation(backend: Any) -> bool:
    return backend._callback_model is CallbackModel.HLA_EVOKED


def force_connection_lost(backend: Any, fault_description: str) -> None:
    backend._deliver_callback_now("connectionLost", str(fault_description))
    backend.disconnect()


def evoke_callback(backend: Any) -> bool:
    if not backend._callbacks_enabled or not backend._evoked_callback_queue:
        return False
    deliver_queued_callback(backend, backend._evoked_callback_queue.pop(0))
    return True


def evoke_multiple_callbacks(backend: Any) -> bool:
    if not backend._callbacks_enabled or not backend._evoked_callback_queue:
        return False
    while backend._evoked_callback_queue:
        deliver_queued_callback(backend, backend._evoked_callback_queue.pop(0))
    return True


def enable_callbacks(backend: Any) -> None:
    backend._callbacks_enabled = True


def disable_callbacks(backend: Any) -> None:
    backend._callbacks_enabled = False


def enable_asynchronous_delivery(backend: Any) -> None:
    backend._asynchronous_delivery_enabled = True


def disable_asynchronous_delivery(backend: Any) -> None:
    backend._asynchronous_delivery_enabled = False


def deliver_callback(backend: Any, method_name: str, *args: Any) -> None:
    if not backend._callbacks_enabled or _callback_requires_evocation(backend):
        backend._evoked_callback_queue.append(QueuedCallback(None, method_name, args))
        return
    deliver_callback_now(backend, method_name, *args)


def deliver_callback_now(backend: Any, method_name: str, *args: Any) -> None:
    if backend._federate_ambassador is None:
        raise RTIinternalError(f"Cannot deliver {method_name} without a connected federate ambassador")
    apply_object_callback_state(backend, method_name, args)
    callback = getattr(backend._federate_ambassador, method_name, None)
    if callback is None:
        return
    callback(*args)


def deliver_to_federate_handle(backend: Any, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
    federation = backend._federation_record()
    target_rti = federation.member_rtis.get(federate_handle.value)
    if target_rti is not None and not target_rti._callbacks_enabled:
        target_rti._evoked_callback_queue.append(QueuedCallback(None, method_name, args))
        return
    if target_rti is not None and _callback_requires_evocation(target_rti):
        deliver_to_federate_handle_now(backend, federate_handle, method_name, *args)
        target_rti._evoked_callback_queue.append(QueuedCallback(None, "__hla_noop__", ()))
        return
    deliver_to_federate_handle_now(backend, federate_handle, method_name, *args)


def deliver_to_federate_handle_now(
    backend: Any,
    federate_handle: FederateHandle,
    method_name: str,
    *args: Any,
) -> None:
    federation = backend._federation_record()
    ambassador = federation.member_ambassadors.get(federate_handle.value)
    if ambassador is None:
        raise InvalidFederateHandle(f"Unknown federate handle {federate_handle!r}")
    target_rti = federation.member_rtis.get(federate_handle.value)
    if target_rti is not None:
        apply_object_callback_state(target_rti, method_name, args)
    callback = getattr(ambassador, method_name, None)
    if callback is None:
        return
    callback(*args)


def apply_object_callback_state(backend: Any, method_name: str, args: tuple[Any, ...]) -> None:
    if method_name == "discoverObjectInstance" and len(args) >= 3:
        object_instance = args[0]
        object_class = args[1]
        object_name = args[2]
        try:
            object_instance_value = backend._normalize_handle(
                object_instance,
                ObjectInstanceHandle,
                InvalidObjectInstanceHandle,
            )
            object_class_name = backend._object_class_name(object_class)
        except Exception:
            return
        backend._known_object_classes[object_instance_value] = object_class_name
        if isinstance(object_name, str) and object_name:
            backend._known_object_names[object_name] = object_instance_value
        backend._locally_deleted_objects.discard(object_instance_value)
        return
    if method_name == "removeObjectInstance" and args:
        try:
            object_instance_value = backend._normalize_handle(
                args[0],
                ObjectInstanceHandle,
                InvalidObjectInstanceHandle,
            )
        except Exception:
            return
        object_names = [
            name
            for name, known_handle in backend._known_object_names.items()
            if known_handle == object_instance_value
        ]
        for object_name in object_names:
            backend._known_object_names.pop(object_name, None)
        backend._known_object_classes.pop(object_instance_value, None)
        backend._locally_deleted_objects.discard(object_instance_value)


def deliver_queued_callback(backend: Any, queued: QueuedCallback) -> None:
    if queued.target_federate is None:
        deliver_callback_now(backend, queued.method_name, *queued.args)
    else:
        deliver_to_federate_handle_now(backend, queued.target_federate, queued.method_name, *queued.args)


def deliver_mom_service_report(backend: Any, report: Mapping[str, Any]) -> None:
    federation = backend._federation_record()
    for federate_key, ambassador in federation.member_ambassadors.items():
        rti = federation.member_rtis.get(federate_key)
        if rti is None or getattr(ambassador, "momServiceReport", None) is None or not rti._switches["service_reporting"]:
            continue
        deliver_callback(rti, "momServiceReport", dict(report))


__all__ = [
    "QueuedCallback",
    "apply_object_callback_state",
    "deliver_callback",
    "deliver_callback_now",
    "deliver_mom_service_report",
    "deliver_queued_callback",
    "deliver_to_federate_handle",
    "deliver_to_federate_handle_now",
    "disable_asynchronous_delivery",
    "disable_callbacks",
    "enable_asynchronous_delivery",
    "enable_callbacks",
    "evoke_callback",
    "evoke_multiple_callbacks",
    "force_connection_lost",
]
