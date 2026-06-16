"""Shared data types for two-federate exchange scenarios."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time


@dataclass(frozen=True)
class TwoFederateExchangeConfig:
    federation_name: str = "VendorExchangeFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "SmokeFederate"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    interaction_class_name: str = "HLAinteractionRoot.DemoInteraction"
    parameter_name: str = "Message"
    object_instance_name: str = "DemoObject-1"
    attribute_payload: bytes = b"attribute-bytes"
    attribute_tag: bytes = b"update-tag"
    interaction_payload: bytes = b"hello"
    interaction_tag: bytes = b"interaction-tag"
    enable_time_management: bool = False
    lookahead: Any = HLAinteger64Interval(1)
    advance_time: Any = HLAinteger64Time(10)
    timestamped_attribute_payload: bytes = b"attribute-tso"
    timestamped_attribute_tag: bytes = b"update-tso"
    timestamped_attribute_time: Any = HLAinteger64Time(5)
    timestamped_interaction_payload: bytes = b"hello-tso"
    timestamped_interaction_tag: bytes = b"interaction-tso"
    timestamped_interaction_time: Any = HLAinteger64Time(6)
    delete_tag: bytes = b"delete-tag"


@dataclass(frozen=True)
class ExchangeRoundConfig:
    attribute_payload: bytes
    attribute_tag: bytes
    interaction_payload: bytes
    interaction_tag: bytes
    attribute_time: Any | None = None
    interaction_time: Any | None = None


__all__ = ["ExchangeRoundConfig", "TwoFederateExchangeConfig"]
