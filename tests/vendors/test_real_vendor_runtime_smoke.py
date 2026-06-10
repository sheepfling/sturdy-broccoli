from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.enums import ResignAction
from hla2010.handles import FederateHandle
from hla2010.real_rti import discover_certi_smoke_fom, launch_certi_rtig, launch_pitch_runtime
from hla2010.rti import create_rti_ambassador
from hla2010.startup import FederationStartupConfig, connect_create_join
from hla2010_verification_harness.scenario_exchange import TwoFederateExchangeConfig, run_two_federate_exchange_scenario
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from tests.vendors.runtime_support import cleanup_federation, close_all, reserve_udp_pair, terminate_all


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_lifecycle_smoke(kind: str):
    _require_real_rti_smoke()
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
        result = connect_create_join(
            rti,
            fed,
            FederationStartupConfig(
                federation_name=federation_name,
                federate_name=f"{kind}-SmokeFederate",
                federate_type="SmokeFederate",
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
            ),
        )
        assert isinstance(result.federate_handle, FederateHandle)
        cleanup_federation(
            federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(rti,),
        )
    finally:
        close_all(rti)
        terminate_all(runtime)


def test_certi_real_lifecycle_smoke():
    _require_real_rti_smoke()
    federation_name = f"certi-smoke-{uuid.uuid4().hex[:8]}"
    fed = RecordingFederateAmbassador()
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
        result = connect_create_join(
            rti,
            fed,
            FederationStartupConfig(
                federation_name=federation_name,
                federate_name="CERTISmokeFederate",
                federate_type="SmokeFederate",
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
            ),
        )
        assert isinstance(result.federate_handle, FederateHandle)
        cleanup_federation(
            federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(rti,),
        )
    finally:
        close_all(rti)


def test_certi_real_exchange_smoke():
    _require_real_rti_smoke()
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
        close_all(subscriber, publisher)
        terminate_all(rtig)


@pytest.mark.parametrize("kind", ["certi-jpype", "certi-py4j"])
def test_certi_java_profile_real_lifecycle_smoke(kind: str):
    _require_real_rti_smoke()
    federation_name = f"{kind}-smoke-{uuid.uuid4().hex[:8]}"
    fed = RecordingFederateAmbassador()
    try:
        smoke_fom = discover_certi_smoke_fom()
        rtig = launch_certi_rtig(verbose=0)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))
    rti = None
    try:
        with reserve_udp_pair() as lease:
            (rti_udp_port, _) = lease.ports
        rti = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=rti_udp_port)
        assert rti.getHLAversion() == "IEEE 1516-2010"
        result = connect_create_join(
            rti,
            fed,
            FederationStartupConfig(
                federation_name=federation_name,
                federate_name=f"{kind}-Federate",
                federate_type="SmokeFederate",
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
            ),
        )
        assert isinstance(result.federate_handle, FederateHandle)
        cleanup_federation(
            federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(rti,),
        )
    finally:
        close_all(rti)
        terminate_all(rtig)


@pytest.mark.parametrize("kind", ["certi-jpype", "certi-py4j"])
def test_certi_java_profile_real_exchange_smoke(kind: str):
    _require_real_rti_smoke()
    try:
        smoke_fom = discover_certi_smoke_fom()
        rtig = launch_certi_rtig(verbose=0)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-exchange-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    try:
        with reserve_udp_pair() as lease:
            publisher_udp_port, subscriber_udp_port = lease.ports
        publisher = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=publisher_udp_port
        )
        subscriber = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=subscriber_udp_port
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
        close_all(subscriber, publisher)
        terminate_all(rtig)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_java_real_exchange_smoke(kind: str):
    _require_real_rti_smoke()
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
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
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
        close_all(subscriber, publisher)
        terminate_all(runtime)
