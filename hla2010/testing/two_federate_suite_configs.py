"""Scenario configuration builders for the two-federate verification suite."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..time import HLAfloat64Interval, HLAfloat64Time
from ..types import RangeBounds
from .scenarios import NegotiatedOwnershipScenarioConfig, OwnershipScenarioConfig, SynchronizationScenarioConfig, TwoFederateExchangeConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = PROJECT_ROOT / "hla2010" / "resources" / "foms"
VENDOR_SMOKE_FOM = RESOURCE_ROOT / "VendorSmokeFOM.xml"
TARGET_RADAR_FOM = RESOURCE_ROOT / "TargetRadarFOMmodule.xml"


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


def _ddm_config() -> dict[str, Any]:
    return {
        "federation_name": "TwoFederateSuiteDDM",
        "fom_modules": (str(TARGET_RADAR_FOM),),
        "logical_time_implementation_name": "HLAfloat64Time",
        "interaction_class_name": "HLAinteractionRoot.TrackReport",
        "parameter_name": "TrackId",
        "source_near": RangeBounds(0, 10),
        "source_far": RangeBounds(90, 100),
        "target_bounds": RangeBounds(5, 15),
        "far_payload": b"far",
        "near_payload": b"near",
        "far_tag": b"far",
        "near_tag": b"near",
        "far_time": HLAfloat64Time(2.0),
        "near_time": HLAfloat64Time(3.0),
        "grant_time": HLAfloat64Time(5.0),
        "next_request_time": HLAfloat64Time(6.0),
    }

