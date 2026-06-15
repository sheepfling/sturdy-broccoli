# ruff: noqa: F401,F403

from tests.vendors.certi_real_backend_matrix_support import *
from tests.vendors.certi_real_backend_matrix_support import (
    _certi_exchange_config,
    _normalized_exchange_profile,
    _require_real_rti_smoke,
)
from hla2010_verification_harness import (
    SupportServicesScenarioConfig,
    SynchronizationScenarioConfig,
    assert_two_federate_exchange_callback_history,
    run_support_factory_and_decode_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from tests.vendors.runtime_support import assert_all_terminated, cleanup_federation, close_all, reserve_udp_pair, terminate_all

@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_exchange_matrix(kind: str, time_factory_name: str):
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
    try:
        with reserve_udp_pair() as lease:
            publisher_udp_port, subscriber_udp_port = lease.ports
        publisher = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=publisher_udp_port)
        subscriber = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=subscriber_udp_port
        )

        config = _certi_exchange_config(
            smoke_fom,
            federation_name,
            f"{kind}-{time_factory_name}-Object-1",
            time_factory_name=time_factory_name,
        )
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == config.object_instance_name
        assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-r"}
        assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-r"}
        assert summary["timed_reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-tso"}
        assert summary["timed_interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-tso"}

        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

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
        assert_all_terminated(rtig)


@pytest.mark.parametrize("kind", ["certi"])
def test_certi_backend_synchronization_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-sync-{uuid.uuid4().hex[:8]}"
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    leader = None
    wing = None
    try:
        with reserve_udp_pair() as lease:
            leader_udp_port, wing_udp_port = lease.ports
        leader = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=leader_udp_port)
        wing = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=wing_udp_port)

        config = SynchronizationScenarioConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
        )
        summary = run_synchronization_scenario(
            leader,
            wing,
            config=config,
            leader_federate=leader_fed,
            wing_federate=wing_fed,
        )

        assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"
        assert len(summary["leader_sync"].args[1]) == 0
        assert len(summary["wing_sync"].args[1]) == 0

        cleanup_federation(
            federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )
    finally:
        close_all(wing, leader)
        terminate_all(rtig)
        assert_all_terminated(rtig)


def test_certi_backend_support_factory_and_decode_matrix():
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"certi-support-{uuid.uuid4().hex[:8]}"
    federate = RecordingFederateAmbassador()
    rti = None
    try:
        with reserve_udp_pair() as lease:
            (udp_port,) = lease.ports[:1]
        rti = create_rti_ambassador("certi", launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_port)

        config = SupportServicesScenarioConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            federate_name="Support",
            federate_type="SupportFederate",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            interaction_class_name="MsgR",
            parameter_name="MsgDataR",
            object_instance_name=f"certi-support-{uuid.uuid4().hex[:8]}",
            include_decode_support=False,
            include_factory_support=False,
            include_order_support=False,
            include_transport_support=False,
        )
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
            federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            disconnect_rtis=(rti,),
        )
    finally:
        close_all(rti)
        terminate_all(rtig)
        assert_all_terminated(rtig)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_time_semantic_profile_native_smoke(time_factory_name: str):
    _require_real_rti_smoke()
    try:
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    for kind in ("certi",):
        try:
            rtig = launch_certi_rtig(verbose=0)
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))
        federation_name = f"{kind}-time-profile-{uuid.uuid4().hex[:8]}"
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
                config=_certi_exchange_config(
                    smoke_fom,
                    federation_name,
                    f"{kind}-{time_factory_name}-TimeProfile-1",
                    time_factory_name=time_factory_name,
                ),
                publisher_federate=publisher_fed,
                subscriber_federate=subscriber_fed,
            )
            profiles[kind] = _normalized_exchange_profile(summary)
        finally:
            close_all(subscriber, publisher)
            terminate_all(rtig)
            assert_all_terminated(rtig)

