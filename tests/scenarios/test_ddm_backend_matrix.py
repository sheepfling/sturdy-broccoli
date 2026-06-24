from __future__ import annotations

import uuid

from hla.rti1516e.enums import ResignAction
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
from hla.rti1516e.datatypes import RangeBounds
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    DdmDeclarationGatingScenarioConfig,
    DdmObjectRegionLifecycleScenarioConfig,
    DdmPassiveRegionScenarioConfig,
    SuiteRecordingFederateAmbassador,
    run_ddm_declaration_gating_scenario,
    run_ddm_object_region_lifecycle_scenario,
    run_ddm_passive_region_subscription_scenario,
    run_suite_ddm_scenario,
)
from tests.vendors.runtime_support import cleanup_federation


def test_python_backend_ddm_matrix():
    engine = InMemoryRTIEngine()
    sender = create_rti_ambassador("python", engine=engine)
    receiver = create_rti_ambassador("python", engine=engine)
    federation_name = f"python-ddm-{uuid.uuid4().hex[:8]}"
    sender_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-probe", role="sender")
    receiver_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-probe", role="receiver")

    summary = run_suite_ddm_scenario(
        sender,
        receiver,
        config={
            "federation_name": federation_name,
            "fom_modules": ("resource:VendorSmokeFOM.xml",),
            "logical_time_implementation_name": "HLAinteger64Time",
            "lookahead": HLAinteger64Interval(1),
            "source_near": RangeBounds(10, 20),
            "source_far": RangeBounds(30, 40),
            "target_bounds": RangeBounds(15, 25),
            "interaction_class_name": "HLAinteractionRoot.SmokeInteraction",
            "parameter_name": "Message",
            "far_payload": b"far",
            "far_tag": b"far-tag",
            "far_time": HLAinteger64Time(2),
            "near_payload": b"near",
            "near_tag": b"near-tag",
            "near_time": HLAinteger64Time(3),
            "grant_time": HLAinteger64Time(10),
            "next_request_time": HLAinteger64Time(10),
        },
        sender_federate=sender_fed,
        receiver_federate=receiver_fed,
    )

    assert summary["received_count"] == 1
    assert summary["received_payload"] == {"Message": "near"}

    cleanup_federation(
        federation_name,
        destroyer=sender,
        destroyer_resign_action=ResignAction.NO_ACTION,
        remaining_resignations=((receiver, ResignAction.NO_ACTION),),
        disconnect_rtis=(receiver, sender),
    )


def test_python_backend_ddm_object_region_lifecycle_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    federation_name = f"python-ddm-object-{uuid.uuid4().hex[:8]}"
    publisher_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-object-lifecycle", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-object-lifecycle", role="subscriber")

    summary = run_ddm_object_region_lifecycle_scenario(
        publisher,
        subscriber,
        config=DdmObjectRegionLifecycleScenarioConfig(
            federation_name=federation_name,
            fom_modules=("TargetRadarFOMmodule.xml",),
        ),
        publisher_federate=publisher_fed,
        subscriber_federate=subscriber_fed,
    )

    assert summary["discovery"] is not None
    assert summary["provide"] is not None
    assert summary["received"] is not None
    assert summary["suppressed_receive"] is None

    cleanup_federation(
        federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_backend_ddm_declaration_gating_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    federation_name = f"python-ddm-declaration-{uuid.uuid4().hex[:8]}"
    publisher_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-declaration-gating", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-declaration-gating", role="subscriber")

    summary = run_ddm_declaration_gating_scenario(
        publisher,
        subscriber,
        config=DdmDeclarationGatingScenarioConfig(
            federation_name=federation_name,
            fom_modules=("TargetRadarFOMmodule.xml",),
        ),
        publisher_federate=publisher_fed,
        subscriber_federate=subscriber_fed,
    )

    assert summary["discovery_before_subscription"] is None
    assert summary["reflection_before_subscription"] is None
    assert summary["interaction_before_subscription"] is None
    assert summary["discovery_after_subscription"] is not None
    assert summary["reflection_after_subscription"] is not None
    assert summary["interaction_after_subscription"] is not None

    cleanup_federation(
        federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_backend_ddm_passive_region_subscription_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    federation_name = f"python-ddm-passive-{uuid.uuid4().hex[:8]}"
    publisher_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-passive", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile="python", scenario="ddm-passive", role="subscriber")

    summary = run_ddm_passive_region_subscription_scenario(
        publisher,
        subscriber,
        config=DdmPassiveRegionScenarioConfig(
            federation_name=federation_name,
            fom_modules=("TargetRadarFOMmodule.xml",),
        ),
        publisher_federate=publisher_fed,
        subscriber_federate=subscriber_fed,
    )

    assert summary["discovery"] is not None
    assert summary["received"] is not None

    cleanup_federation(
        federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )
