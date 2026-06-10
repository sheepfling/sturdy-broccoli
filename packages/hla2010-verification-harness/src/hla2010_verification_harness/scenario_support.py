"""Shared support types and callback helpers for backend-neutral RTI scenarios."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from hla2010.exceptions import CallNotAllowedFromWithinCallback, ObjectInstanceNameNotReserved, RTIexception
from hla2010.runtime_api import FederateAmbassador
from hla2010.time import HLAinteger64Time


@dataclass
class DemoFederate(FederateAmbassador):
    events: list[tuple[str, Any]] = field(default_factory=list)

    def discover_object_instance(self, the_object, the_object_class, object_name, *extra):
        self.events.append(("discover", (the_object, the_object_class, object_name, extra)))

    def reflect_attribute_values(self, the_object, the_attributes, user_supplied_tag, sent_ordering, the_transport, *extra):
        self.events.append(("reflect", (the_object, the_attributes, user_supplied_tag, sent_ordering, the_transport, extra)))

    def receive_interaction(self, interaction_class, the_parameters, user_supplied_tag, sent_ordering, the_transport, *extra):
        self.events.append(("interaction", (interaction_class, the_parameters, user_supplied_tag, sent_ordering, the_transport, extra)))

    def time_regulation_enabled(self, time):
        self.events.append(("time_regulation_enabled", time))

    def time_constrained_enabled(self, time):
        self.events.append(("time_constrained_enabled", time))

    def time_advance_grant(self, the_time):
        self.events.append(("time_advance_grant", the_time))


def drain_callbacks(rti: Any) -> None:
    while _safe_evoke_callback(rti):
        pass
    _safe_evoke_multiple_callbacks(rti)


def drain_callbacks_pair(*rtis: Any, loops: int = 8) -> None:
    for _ in range(loops):
        delivered = False
        for rti in rtis:
            if _safe_evoke_callback(rti):
                delivered = True
        for rti in rtis:
            if _safe_evoke_multiple_callbacks(rti, max_seconds=0.05):
                delivered = True
        if not delivered:
            return


def wait_for_callback(rti: Any, federate: Any, method_name: str, *, loops: int = 24) -> Any:
    for _ in range(loops):
        record = federate.last_callback(method_name)
        if record is not None:
            return record
        _safe_evoke_multiple_callbacks(rti)
        time.sleep(0.05)
    record = federate.last_callback(method_name)
    if record is not None:
        return record
    _safe_evoke_multiple_callbacks(rti)
    return federate.last_callback(method_name)


def wait_for_callback_count(rti: Any, federate: Any, method_name: str, expected_count: int, *, loops: int = 24) -> list[Any]:
    for _ in range(loops):
        records = federate.callbacks_named(method_name)
        if len(records) >= expected_count:
            return records
        _safe_evoke_multiple_callbacks(rti)
        time.sleep(0.05)
    records = federate.callbacks_named(method_name)
    if len(records) >= expected_count:
        return records
    _safe_evoke_multiple_callbacks(rti)
    return federate.callbacks_named(method_name)


def wait_for_callback_count_pair(
    publisher_rti: Any,
    subscriber_rti: Any,
    federate: Any,
    method_name: str,
    expected_count: int,
    *,
    loops: int = 24,
) -> list[Any]:
    for _ in range(loops):
        records = federate.callbacks_named(method_name)
        if len(records) >= expected_count:
            return records
        _safe_evoke_multiple_callbacks(publisher_rti)
        _safe_evoke_multiple_callbacks(subscriber_rti)
        time.sleep(0.05)
    records = federate.callbacks_named(method_name)
    if len(records) >= expected_count:
        return records
    _safe_evoke_multiple_callbacks(publisher_rti)
    _safe_evoke_multiple_callbacks(subscriber_rti)
    return federate.callbacks_named(method_name)


def advance_time_beyond(publisher_rti: Any, subscriber_rti: Any, target_time: Any) -> None:
    raw = float(getattr(target_time, "value", target_time))
    if isinstance(target_time, HLAinteger64Time):
        advance_to = type(target_time)(int(raw) + 1)
    else:
        advance_to = type(target_time)(raw + 1.0)
    publisher_rti.time_advance_request(advance_to)
    subscriber_rti.time_advance_request(advance_to)
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)


def order_value(value: Any) -> int:
    return int(getattr(value, "value", value))


def safe_evoke_callback(rti: Any, seconds: float = 0.0) -> bool:
    try:
        return bool(rti.evoke_callback(seconds))
    except CallNotAllowedFromWithinCallback:
        return False


def safe_evoke_multiple_callbacks(rti: Any, min_seconds: float = 0.0, max_seconds: float = 0.1) -> bool:
    try:
        return bool(rti.evoke_multiple_callbacks(min_seconds, max_seconds))
    except CallNotAllowedFromWithinCallback:
        return False


def register_named_object_instance(rti: Any, federate: Any, object_class: Any, object_instance_name: str) -> Any:
    reserved = False
    try:
        rti.reserve_object_instance_name(object_instance_name)
        reserved = True
    except RTIexception:
        reserved = False

    if reserved:
        for _ in range(24):
            reservation = federate.last_callback("objectInstanceNameReservationSucceeded")
            if reservation is not None and reservation.args == (object_instance_name,):
                break
            safe_evoke_multiple_callbacks(rti)

    try:
        return rti.register_object_instance(object_class, object_instance_name)
    except ObjectInstanceNameNotReserved:
        if not reserved:
            rti.reserve_object_instance_name(object_instance_name)
        for _ in range(24):
            reservation = federate.last_callback("objectInstanceNameReservationSucceeded")
            if reservation is not None and reservation.args == (object_instance_name,):
                return rti.register_object_instance(object_class, object_instance_name)
            safe_evoke_multiple_callbacks(rti, max_seconds=0.05)
            try:
                return rti.register_object_instance(object_class, object_instance_name)
            except ObjectInstanceNameNotReserved:
                continue
        reservation = federate.last_callback("objectInstanceNameReservationSucceeded")
        if reservation is not None:
            assert reservation.args == (object_instance_name,)
        return rti.register_object_instance(object_class, object_instance_name)


_safe_evoke_callback = safe_evoke_callback
_safe_evoke_multiple_callbacks = safe_evoke_multiple_callbacks


__all__ = [
    "DemoFederate",
    "advance_time_beyond",
    "drain_callbacks",
    "drain_callbacks_pair",
    "order_value",
    "register_named_object_instance",
    "safe_evoke_callback",
    "safe_evoke_multiple_callbacks",
    "wait_for_callback",
    "wait_for_callback_count",
    "wait_for_callback_count_pair",
]
