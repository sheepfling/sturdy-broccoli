from __future__ import annotations

import os
import uuid

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_backend_common import BackendUnavailableError, make_rti_ambassador
from hla2010.enums import ResignAction
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_rti_java_common.java_shim_factory import create_shared_java_shim_backend
from hla2010_rti_java_common.java_shim_kernel import SharedJavaShimKernel
from hla2010_verification_harness import (
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    SupportServicesScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_support_factory_and_decode_scenario,
    run_two_federate_exchange_scenario,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_synchronization_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla2010_rti_certi.real_rti_certi import discover_certi_smoke_fom, launch_certi_rtig
from tests.vendors.runtime_support import cleanup_federation, close_all, require_vendor_preflight, terminate_all, udp_port_pair


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    require_vendor_preflight("certi", operator_hint="./tools/certi-easy preflight")


def _exchange_time_profile(time_factory_name: str) -> dict[str, object]:
    if time_factory_name == "HLAinteger64Time":
        return {
            "logical_time_implementation_name": "HLAinteger64Time",
            "lookahead": HLAinteger64Interval(1),
            "advance_time": HLAinteger64Time(8),
            "timestamped_attribute_time": HLAinteger64Time(5),
            "timestamped_interaction_time": HLAinteger64Time(6),
        }
    if time_factory_name == "HLAfloat64Time":
        return {
            "logical_time_implementation_name": "HLAfloat64Time",
            "lookahead": HLAfloat64Interval(1.0),
            "advance_time": HLAfloat64Time(8.0),
            "timestamped_attribute_time": HLAfloat64Time(5.0),
            "timestamped_interaction_time": HLAfloat64Time(6.0),
        }
    raise AssertionError(f"unexpected time factory {time_factory_name}")


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_inprocess_java_shim_time_factory_matrix(profile: str, time_factory_name: str):
    kernel = SharedJavaShimKernel()
    publisher = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    subscriber = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    config = TwoFederateExchangeConfig(
        federation_name=f"java-shim-time-{profile}-{time_factory_name}-{uuid.uuid4().hex[:8]}",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name=f"java-shim-{profile}-{time_factory_name}-Object-1",
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=True,
        **_exchange_time_profile(time_factory_name),
    )
    try:
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[2] == b"reflect-tag"
        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )
    finally:
        close_all(subscriber, publisher)


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_inprocess_java_shim_backend_matrix(profile: str):
    kernel = SharedJavaShimKernel()
    publisher = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    subscriber = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    config = TwoFederateExchangeConfig(
        federation_name=f"java-shim-{profile}-{uuid.uuid4().hex[:8]}",
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name=f"java-shim-{profile}-Object-1",
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=False,
    )
    try:
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
            require_timed_delivery=False,
        )
        assert history["receive_interaction"].args[2] == b"interaction-tag"
        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )
    finally:
        close_all(subscriber, publisher)


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_inprocess_java_shim_synchronization_scenario(profile: str):
    kernel = SharedJavaShimKernel()
    leader = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    wing = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    config = SynchronizationScenarioConfig(
        federation_name=f"java-sync-{profile}-{uuid.uuid4().hex[:8]}",
        logical_time_implementation_name="HLAinteger64Time",
        label="ReadyToRun",
        tag=b"startup",
    )
    try:
        summary = run_synchronization_scenario(
            leader,
            wing,
            config=config,
            leader_federate=leader_fed,
            wing_federate=wing_fed,
        )
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"
        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )
    finally:
        close_all(wing, leader)


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_inprocess_java_shim_support_factory_and_decode_scenario(profile: str):
    kernel = SharedJavaShimKernel()
    rti = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    federate = RecordingFederateAmbassador()
    config = SupportServicesScenarioConfig(
        federation_name=f"java-support-{profile}-{uuid.uuid4().hex[:8]}",
        fom_modules=(),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name=f"java-support-{profile}-Object-1",
        include_decode_support=False,
        include_factory_support=False,
        include_order_support=False,
        include_transport_support=False,
    )
    try:
        summary = run_support_factory_and_decode_scenario(
            rti,
            config=config,
            federate=federate,
        )
        assert summary["lookup_summary"]["federate_name"] == config.federate_name
        assert summary["lookup_summary"]["object_class_name"] == config.object_class_name
        assert summary["lookup_summary"]["attribute_name"] == config.attribute_name
        assert summary["lookup_summary"]["interaction_class_name"] == config.interaction_class_name
        assert summary["lookup_summary"]["parameter_name"] == config.parameter_name
        assert summary["lookup_summary"]["object_instance_name"] == config.object_instance_name
        assert summary["lookup_summary"]["object_instance_handle"] == summary["object_instance"]
        assert summary["lookup_summary"]["known_object_class"] == summary["object_class"]
        cleanup_federation(
            config.federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            disconnect_rtis=(rti,),
        )
    finally:
        close_all(rti)


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_inprocess_java_shim_ownership_scenario(profile: str):
    kernel = SharedJavaShimKernel()
    owner = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    acquirer = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = OwnershipScenarioConfig(
        federation_name=f"java-owner-{profile}-{uuid.uuid4().hex[:8]}",
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        object_instance_name=f"owned-{profile}-1",
    )
    try:
        summary = run_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )
        assert summary["acquired"].args[0] == summary["object_instance"]
        assert summary["informed_federate_name"] == config.acquirer_name
        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
    finally:
        close_all(acquirer, owner)


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_inprocess_java_shim_negotiated_ownership_scenario(profile: str):
    kernel = SharedJavaShimKernel()
    owner = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    acquirer = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = NegotiatedOwnershipScenarioConfig(
        federation_name=f"java-nego-owner-{profile}-{uuid.uuid4().hex[:8]}",
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="NegotiatedOwnershipFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        object_instance_name=f"nego-owned-{profile}-1",
    )
    try:
        summary = run_negotiated_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )
        assert summary["release"].args[0] == summary["release_object_instance"]
        assert summary["cancellation"].args[0] == summary["release_acquirer_object_instance"]
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["release_acquirer_object_instance"]
        if summary["assumption"] is not None:
            assert summary["offered_acquired"] is not None
            assert summary["divestiture_confirmation"] is not None

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
    finally:
        close_all(acquirer, owner)


@pytest.mark.parametrize("kind", ["certi-jpype", "certi-py4j"])
def test_certi_java_profile_backend_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-matrix-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    config = TwoFederateExchangeConfig(
        federation_name=federation_name,
        fom_modules=(smoke_fom,),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="TestObjectClassR",
        attribute_name="DataR",
        interaction_class_name="MsgR",
        parameter_name="MsgDataR",
        object_instance_name=f"{kind}-Object-1",
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
    )
    try:
        with udp_port_pair() as (publisher_udp_port, subscriber_udp_port):
            publisher = create_rti_ambassador(
                kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=publisher_udp_port
            )
            subscriber = create_rti_ambassador(
                kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=subscriber_udp_port
            )
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[2] == b"reflect-tag"
        cleanup_federation(
            federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )
    finally:
        close_all(subscriber, publisher)
        terminate_all(rtig)
