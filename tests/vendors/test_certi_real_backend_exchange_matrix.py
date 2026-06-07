# ruff: noqa: F401,F403

from tests.vendors.certi_real_backend_matrix_support import *
from tests.vendors.certi_real_backend_matrix_support import (
    _certi_exchange_config,
    _normalized_exchange_profile,
    _require_real_rti_smoke,
)

@pytest.mark.parametrize("kind,udp_base", [("certi", 60601), ("certi-jpype", 60611), ("certi-py4j", 60621)])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_exchange_matrix(kind: str, udp_base: int, time_factory_name: str):
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
        publisher = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
        subscriber = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)

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

        subscriber.resign_federation_execution(ResignAction.NO_ACTION)
        publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        publisher.destroy_federation_execution(federation_name)
        subscriber.disconnect()
        publisher.disconnect()
    finally:
        if subscriber is not None:
            subscriber.close()
        if publisher is not None:
            publisher.close()
        rtig.terminate()


@pytest.mark.parametrize("kind,udp_base", [("certi", 60701), ("certi-jpype", 60711), ("certi-py4j", 60721)])
def test_certi_backend_synchronization_matrix(kind: str, udp_base: int):
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
        leader = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
        wing = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)

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

        wing.resign_federation_execution(ResignAction.NO_ACTION)
        leader.resign_federation_execution(ResignAction.NO_ACTION)
        leader.destroy_federation_execution(federation_name)
        wing.disconnect()
        leader.disconnect()
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        rtig.terminate()


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_time_semantic_profile_matches_across_native_and_java_facades(time_factory_name: str):
    _require_real_rti_smoke()
    try:
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    for kind, udp_base in (("certi", 61001), ("certi-jpype", 61011), ("certi-py4j", 61021)):
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
            publisher = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
            subscriber = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)
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
            if subscriber is not None:
                subscriber.close()
            if publisher is not None:
                publisher.close()
            rtig.terminate()

    assert profiles["certi-jpype"] == profiles["certi"]
    assert profiles["certi-py4j"] == profiles["certi"]
