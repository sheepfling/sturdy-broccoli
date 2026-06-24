from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.common import BackendUnavailableError
from hla.rti1516e.enums import ResignAction
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e.datatypes import RangeBounds
from hla.verification import (
    FederationLifecycleScenarioConfig,
    SaveRestoreScenarioConfig,
    SuiteRecordingFederateAmbassador,
    TwoFederateExchangeConfig,
    run_federation_lifecycle_scenario,
    run_save_restore_scenario,
    run_suite_ddm_scenario,
    run_two_federate_exchange_scenario,
)
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla.backends.certi.real_rti_certi import discover_certi_smoke_fom, launch_certi_rtig
from hla.vendors.pitch.real_rti_pitch import launch_pitch_runtime
from tests.vendors.runtime_support import (
    cleanup_federation,
    isolated_vendor_runtime_test_state,
    require_vendor_preflight,
    reserve_udp_pair,
    shutdown_runtime_resources,
)


def _require_real_rti_smoke(vendor: str) -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    if vendor == "pitch":
        os.environ.setdefault("HLA2010_PITCH_CRC_MODE", "docker")
        os.environ.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")
    operator_hint = "./tools/certi-easy preflight" if vendor == "certi" else "./tools/pitch preflight"
    require_vendor_preflight(vendor, operator_hint=operator_hint)


def _runtime_state_root(vendor: str, *, kind: str | None = None) -> Path:
    suffix = vendor if kind is None else f"{vendor}-{kind}"
    return Path(__file__).resolve().parents[2] / ".pytest-runtime-state" / suffix


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_lifecycle_smoke(kind: str):
    _require_real_rti_smoke("pitch")
    with isolated_vendor_runtime_test_state(_runtime_state_root("pitch", kind=kind)):
        runtime = None
        try:
            runtime = launch_pitch_runtime()
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        federation_name = f"pitch-smoke-{uuid.uuid4().hex[:8]}"
        rti = None
        try:
            fed = RecordingFederateAmbassador()
            rti = create_rti_ambassador(kind)
            assert rti.getHLAversion() == "IEEE 1516-2010"
            summary = run_federation_lifecycle_scenario(
                rti,
                config=FederationLifecycleScenarioConfig(
                    federation_name=federation_name,
                    federate_name=f"{kind}-SmokeFederate",
                    federate_type="SmokeFederate",
                    fom_modules=("resource:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                ),
                federate=fed,
            )
            assert summary["federation_name"] == federation_name
            assert summary["federate_handle"] is not None
        finally:
            shutdown_runtime_resources(close_resources=(rti,), runtime_resources=(runtime,))


def test_certi_real_lifecycle_smoke():
    _require_real_rti_smoke("certi")
    with isolated_vendor_runtime_test_state(_runtime_state_root("certi")):
        federation_name = f"certi-smoke-{uuid.uuid4().hex[:8]}"
        fed = RecordingFederateAmbassador()
        rti = None
        try:
            smoke_fom = discover_certi_smoke_fom()
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))
        try:
            rti = create_rti_ambassador("certi")
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))
        try:
            assert rti.getHLAversion() == "IEEE 1516-2010"
            summary = run_federation_lifecycle_scenario(
                rti,
                config=FederationLifecycleScenarioConfig(
                    federation_name=federation_name,
                    federate_name="CERTISmokeFederate",
                    federate_type="SmokeFederate",
                    fom_modules=(smoke_fom,),
                    logical_time_implementation_name="HLAinteger64Time",
                ),
                federate=fed,
            )
            assert summary["federation_name"] == federation_name
            assert summary["federate_handle"] is not None
        finally:
            shutdown_runtime_resources(close_resources=(rti,))


def test_certi_real_exchange_smoke():
    _require_real_rti_smoke("certi")
    try:
        smoke_fom = discover_certi_smoke_fom()
        rtig = launch_certi_rtig(verbose=0)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"certi-exchange-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    try:
        with reserve_udp_pair() as lease:
            publisher_udp_port, subscriber_udp_port = lease.ports
        publisher = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=publisher_udp_port
        )
        subscriber = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=subscriber_udp_port
        )
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=TwoFederateExchangeConfig(
                federation_name=federation_name,
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
                object_class_name="TestObjectClassR",
                attribute_name="DataR",
                interaction_class_name="MsgR",
                parameter_name="MsgDataR",
                object_instance_name="SmokeObject-1",
                attribute_payload=b"payload-r",
                attribute_tag=b"reflect-tag",
                interaction_payload=b"hello-r",
                interaction_tag=b"interaction-tag",
                enable_time_management=True,
                lookahead=HLAfloat64Interval(1.0),
                advance_time=HLAfloat64Time(8.0),
                timestamped_attribute_payload=b"payload-tso",
                timestamped_attribute_tag=b"reflect-tso",
                timestamped_attribute_time=HLAfloat64Time(5.0),
                timestamped_interaction_payload=b"hello-tso",
                timestamped_interaction_tag=b"interaction-tso",
                timestamped_interaction_time=HLAfloat64Time(6.0),
            ),
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )
        assert summary["advance_grant"].args[0] == HLAfloat64Time(8.0)
        cleanup_federation(
            federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )
    finally:
        shutdown_runtime_resources(close_resources=(subscriber, publisher), runtime_resources=(rtig,))


def test_certi_real_save_restore_smoke():
    _require_real_rti_smoke("certi")
    try:
        smoke_fom = discover_certi_smoke_fom()
        rtig = launch_certi_rtig(verbose=0)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"certi-save-restore-{uuid.uuid4().hex[:8]}"
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    leader = None
    wing = None
    try:
        with reserve_udp_pair() as lease:
            leader_udp_port, wing_udp_port = lease.ports
        leader = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=leader_udp_port
        )
        wing = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=wing_udp_port
        )
        summary = run_save_restore_scenario(
            leader,
            wing,
            config=SaveRestoreScenarioConfig(
                federation_name=federation_name,
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
                save_name=f"CERTI-SAVE-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=leader_fed,
            wing_federate=wing_fed,
        )
        assert summary["leader_initiate_save"] is not None
        assert summary["wing_initiate_save"] is not None
        assert summary["leader_restore_succeeded"] is not None
        assert summary["wing_initiate_restore"] is not None
        assert summary["leader_restored"] is not None
        assert summary["wing_restored"] is not None

        cleanup_federation(
            federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )
    finally:
        shutdown_runtime_resources(close_resources=(wing, leader), runtime_resources=(rtig,))


def test_certi_real_ddm_smoke():
    _require_real_rti_smoke("certi")
    try:
        smoke_fom = discover_certi_smoke_fom()
        rtig = launch_certi_rtig(verbose=0)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"certi-ddm-{uuid.uuid4().hex[:8]}"
    sender_fed = SuiteRecordingFederateAmbassador(profile="certi", scenario="ddm-probe", role="sender")
    receiver_fed = SuiteRecordingFederateAmbassador(profile="certi", scenario="ddm-probe", role="receiver")
    sender = None
    receiver = None
    try:
        with reserve_udp_pair() as lease:
            sender_udp_port, receiver_udp_port = lease.ports
        sender = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=sender_udp_port
        )
        receiver = create_rti_ambassador(
            "certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=receiver_udp_port
        )
        summary = run_suite_ddm_scenario(
            sender,
            receiver,
            config={
                "federation_name": federation_name,
                "fom_modules": (smoke_fom,),
                "logical_time_implementation_name": "HLAfloat64Time",
                "lookahead": HLAfloat64Interval(1.0),
                "source_near": RangeBounds(10, 20),
                "source_far": RangeBounds(30, 40),
                "target_bounds": RangeBounds(15, 25),
                "interaction_class_name": "MsgR",
                "parameter_name": "MsgDataR",
                "far_payload": b"far",
                "far_tag": b"far-tag",
                "far_time": HLAfloat64Time(2.0),
                "near_payload": b"near",
                "near_tag": b"near-tag",
                "near_time": HLAfloat64Time(3.0),
                "grant_time": HLAfloat64Time(10.0),
                "next_request_time": HLAfloat64Time(10.0),
            },
            sender_federate=sender_fed,
            receiver_federate=receiver_fed,
        )
        assert summary["received_count"] == 1
        assert summary["received_payload"] == {"MsgDataR": "near"}

        cleanup_federation(
            federation_name,
            destroyer=sender,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((receiver, ResignAction.NO_ACTION),),
            disconnect_rtis=(receiver, sender),
        )
    finally:
        shutdown_runtime_resources(close_resources=(receiver, sender), runtime_resources=(rtig,))




@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_save_restore_smoke(kind: str):
    _require_real_rti_smoke("pitch")
    with isolated_vendor_runtime_test_state(_runtime_state_root("pitch", kind=f"{kind}-save-restore")):
        try:
            runtime = launch_pitch_runtime()
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        federation_name = f"{kind}-save-restore-{uuid.uuid4().hex[:8]}"
        leader_fed = RecordingFederateAmbassador()
        wing_fed = RecordingFederateAmbassador()
        leader = None
        wing = None
        try:
            leader = create_rti_ambassador(kind)
            wing = create_rti_ambassador(kind)
            summary = run_save_restore_scenario(
                leader,
                wing,
                config=SaveRestoreScenarioConfig(
                    federation_name=federation_name,
                    fom_modules=("resource:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                    save_name=f"PITCH-SAVE-{uuid.uuid4().hex[:8]}",
                ),
                leader_federate=leader_fed,
                wing_federate=wing_fed,
            )
            assert summary["leader_initiate_save"] is not None
            assert summary["wing_initiate_save"] is not None
            assert summary["leader_restore_succeeded"] is not None
            assert summary["wing_initiate_restore"] is not None
            assert summary["leader_restored"] is not None
            assert summary["wing_restored"] is not None

            cleanup_federation(
                federation_name,
                destroyer=leader,
                destroyer_resign_action=ResignAction.NO_ACTION,
                remaining_resignations=((wing, ResignAction.NO_ACTION),),
                disconnect_rtis=(wing, leader),
            )
        finally:
            shutdown_runtime_resources(close_resources=(wing, leader), runtime_resources=(runtime,))


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_ddm_smoke(kind: str):
    _require_real_rti_smoke("pitch")
    with isolated_vendor_runtime_test_state(_runtime_state_root("pitch", kind=f"{kind}-ddm")):
        try:
            runtime = launch_pitch_runtime()
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        federation_name = f"{kind}-ddm-{uuid.uuid4().hex[:8]}"
        sender_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-probe", role="sender")
        receiver_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-probe", role="receiver")
        sender = None
        receiver = None
        try:
            sender = create_rti_ambassador(kind)
            receiver = create_rti_ambassador(kind)
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
        finally:
            shutdown_runtime_resources(close_resources=(receiver, sender), runtime_resources=(runtime,))


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_exchange_smoke(kind: str):
    _require_real_rti_smoke("pitch")
    with isolated_vendor_runtime_test_state(_runtime_state_root("pitch", kind=f"{kind}-exchange")):
        try:
            runtime = launch_pitch_runtime()
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        federation_name = f"pitch-exchange-{uuid.uuid4().hex[:8]}"
        publisher_fed = RecordingFederateAmbassador()
        subscriber_fed = RecordingFederateAmbassador()
        publisher = None
        subscriber = None
        try:
            publisher = create_rti_ambassador(kind)
            subscriber = create_rti_ambassador(kind)
            summary = run_two_federate_exchange_scenario(
                publisher,
                subscriber,
                config=TwoFederateExchangeConfig(
                    federation_name=federation_name,
                    fom_modules=("resource:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                    object_class_name="HLAobjectRoot.SmokeObject",
                    attribute_name="Payload",
                    interaction_class_name="HLAinteractionRoot.SmokeInteraction",
                    parameter_name="Message",
                    object_instance_name=f"{kind}-PitchSmokeObject-1",
                    enable_time_management=True,
                    lookahead=HLAinteger64Interval(1),
                    advance_time=HLAinteger64Time(8),
                    timestamped_attribute_time=HLAinteger64Time(5),
                    timestamped_interaction_time=HLAinteger64Time(6),
                ),
                publisher_federate=publisher_fed,
                subscriber_federate=subscriber_fed,
            )
            assert summary["advance_grant"].args[0] == HLAinteger64Time(8)
            cleanup_federation(
                federation_name,
                destroyer=publisher,
                destroyer_resign_action=ResignAction.DELETE_OBJECTS,
                remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
                disconnect_rtis=(subscriber, publisher),
            )
        finally:
            shutdown_runtime_resources(close_resources=(subscriber, publisher), runtime_resources=(runtime,))
