"""Generic configuration builders for the two-federate verification suite."""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from typing import Any

from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time


VENDOR_SMOKE_FOM = resources.files("hla.rti1516e").joinpath("resources", "foms", "VendorSmokeFOM.xml")


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
    lookahead: Any = HLAfloat64Interval(1.0)
    advance_time: Any = HLAfloat64Time(8.0)
    timestamped_attribute_payload: bytes = b"attribute-tso"
    timestamped_attribute_tag: bytes = b"update-tso"
    timestamped_attribute_time: Any = HLAfloat64Time(5.0)
    timestamped_interaction_payload: bytes = b"hello-tso"
    timestamped_interaction_tag: bytes = b"interaction-tso"
    timestamped_interaction_time: Any = HLAfloat64Time(6.0)
    delete_tag: bytes = b"delete-tag"


@dataclass(frozen=True)
class SynchronizationScenarioConfig:
    federation_name: str = "JavaProfileSyncFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    federate_type: str = "Participant"
    label: str = "ReadyToRun"
    tag: bytes = b"startup"


@dataclass(frozen=True)
class OwnershipScenarioConfig:
    federation_name: str = "JavaProfileOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "OwnedObject-1"


@dataclass(frozen=True)
class NegotiatedOwnershipScenarioConfig:
    federation_name: str = "JavaProfileNegotiatedOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "NegotiatedOwnedObject-1"
    assumption_tag: bytes = b"assume-offer"
    request_tag: bytes = b"acquire-request"
    cancel_tag: bytes = b"cancel-request"


def _exchange_config() -> TwoFederateExchangeConfig:
    return TwoFederateExchangeConfig(
        federation_name="TwoFederateSuiteExchange",
        fom_modules=(str(VENDOR_SMOKE_FOM),),
        logical_time_implementation_name="HLAfloat64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name="SuiteObject-1",
        attribute_payload=b"suite-attribute",
        attribute_tag=b"suite-receive-tag",
        interaction_payload=b"suite-interaction",
        interaction_tag=b"suite-interaction-tag",
        enable_time_management=True,
        lookahead=HLAfloat64Interval(1.0),
        advance_time=HLAfloat64Time(8.0),
        timestamped_attribute_payload=b"suite-attribute-tso",
        timestamped_attribute_tag=b"suite-tso-tag",
        timestamped_attribute_time=HLAfloat64Time(5.0),
        timestamped_interaction_payload=b"suite-interaction-tso",
        timestamped_interaction_tag=b"suite-interaction-tso-tag",
        timestamped_interaction_time=HLAfloat64Time(6.0),
    )


def _sync_config() -> SynchronizationScenarioConfig:
    return SynchronizationScenarioConfig(
        federation_name="TwoFederateSuiteSync",
        fom_modules=(str(VENDOR_SMOKE_FOM),),
        logical_time_implementation_name="HLAfloat64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"suite-sync",
    )


def _ownership_config() -> OwnershipScenarioConfig:
    return OwnershipScenarioConfig(
        federation_name="TwoFederateSuiteOwnership",
        fom_modules=(str(VENDOR_SMOKE_FOM),),
        logical_time_implementation_name="HLAfloat64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name="OwnedSuiteObject-1",
    )


def _negotiated_config() -> NegotiatedOwnershipScenarioConfig:
    return NegotiatedOwnershipScenarioConfig(
        federation_name="TwoFederateSuiteNegotiatedOwnership",
        fom_modules=(str(VENDOR_SMOKE_FOM),),
        logical_time_implementation_name="HLAfloat64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="NegotiatedOwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name="NegotiatedSuiteObject-1",
    )


def _save_restore_config() -> dict[str, Any]:
    return {
        "federation_name": "TwoFederateSuiteSaveRestore",
        "fom_modules": (str(VENDOR_SMOKE_FOM),),
        "logical_time_implementation_name": "HLAfloat64Time",
        "save_name": "SAVE-AT-5",
        "save_time": HLAfloat64Time(5.0),
        "resume_time": HLAfloat64Time(8.0),
    }


__all__ = [
    "_exchange_config",
    "_negotiated_config",
    "_ownership_config",
    "_save_restore_config",
    "_sync_config",
]
