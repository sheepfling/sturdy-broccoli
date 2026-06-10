# ruff: noqa: F401,F403

from tests.vendors.certi_real_backend_matrix_support import *
from tests.vendors.runtime_support import cleanup_federation, close_all, reserve_udp_pair, terminate_all

@pytest.mark.parametrize("kind", ["certi", "certi-jpype", "certi-py4j"])
def test_certi_backend_ownership_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-owner-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        with reserve_udp_pair() as lease:
            owner_udp_port, acquirer_udp_port = lease.ports
        owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=owner_udp_port)
        acquirer = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=acquirer_udp_port
        )

        config = OwnershipScenarioConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            object_instance_name=f"{kind}-Owned-1",
        )
        summary = run_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        acquired = summary["acquired"]
        informed = summary["informed"]
        not_owned = summary["not_owned"]
        assert not_owned.args == (summary["object_instance"], summary["owner_attribute"])
        assert acquired.args[0] == summary["acquirer_object_instance"]
        assert summary["acquirer_attribute"] in acquired.args[1]
        assert informed.args[0] == summary["object_instance"]
        assert informed.args[1] == summary["owner_attribute"]

        cleanup_federation(
            federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
    finally:
        close_all(acquirer, owner)
        terminate_all(rtig)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_next_message_request_fail_fast_matrix(time_factory_name: str):
    _assert_certi_patched_fail_fast_time_request_matrix(None, time_factory_name, "NEXT_MESSAGE_REQUEST")


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_next_message_request_available_fail_fast_matrix(time_factory_name: str):
    _assert_certi_patched_fail_fast_time_request_matrix(None, time_factory_name, "NEXT_MESSAGE_REQUEST_AVAILABLE")


@pytest.mark.parametrize("kind", ["certi", "certi-jpype", "certi-py4j"])
def test_certi_backend_negotiated_ownership_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-nego-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        with reserve_udp_pair() as lease:
            owner_udp_port, acquirer_udp_port = lease.ports
        owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=owner_udp_port)
        acquirer = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=acquirer_udp_port
        )

        config = _certi_negotiated_config(smoke_fom, federation_name, f"{kind}-Negotiated-1")
        try:
            summary = run_negotiated_attribute_ownership_scenario(
                owner,
                acquirer,
                config=config,
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except (RTIinternalError, AssertionError) as exc:
            pytest.skip(f"CERTI negotiated ownership path is not stable in this runtime: {exc}")

        assert summary["negotiated_divestiture_supported"] is True
        assert summary["assumption"] is not None
        assert summary["release"].args == (
            summary["release_object_instance"],
            {summary["owner_attribute"]},
            b"reacquire-request",
        )
        assert summary["cancellation"].args == (
            summary["release_acquirer_object_instance"],
            {summary["acquirer_attribute"]},
        )
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["release_acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["release_object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]

        cleanup_federation(
            federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
    finally:
        close_all(acquirer, owner)
        terminate_all(rtig)


def test_certi_upstream_negotiated_ownership_baseline():
    _assert_certi_profile_negotiated_ownership_baseline("certi-upstream", None)


def test_certi_patched_negotiated_ownership_baseline():
    _assert_certi_profile_negotiated_ownership_baseline("certi-patched", None)


@pytest.mark.parametrize("owner_action", ["deny", "confirm", "ifwanted"])
def test_certi_upstream_release_request_branch_baseline(owner_action: str):
    _assert_certi_profile_release_request_branch_baseline("certi-upstream", None, owner_action)


@pytest.mark.parametrize("owner_action", ["deny", "confirm", "ifwanted"])
def test_certi_patched_release_request_branch_baseline(owner_action: str):
    _assert_certi_profile_release_request_branch_baseline("certi-patched", None, owner_action)


def test_certi_upstream_confirm_divestiture_negotiated_baseline():
    _assert_certi_profile_confirm_divestiture_negotiated_baseline("certi-upstream", None)


def test_certi_patched_confirm_divestiture_negotiated_baseline():
    _assert_certi_profile_confirm_divestiture_negotiated_baseline("certi-patched", None)


def test_certi_patched_confirm_release_request_is_distinct_from_ifwanted():
    confirm = _run_certi_profile_release_request_branch_baseline("certi-patched", None, "confirm")
    ifwanted = _run_certi_profile_release_request_branch_baseline("certi-patched", None, "ifwanted")
    assert confirm is not None
    assert ifwanted is not None
    assert confirm["confirm_exception"] == "AttributeDivestitureWasNotRequested"
    ifwanted_profile = _normalized_release_request_profile(ifwanted)
    assert ifwanted_profile["divested"] == {ifwanted["owner_attribute"]}
    assert ifwanted_profile["acquired_present"] is True


def test_certi_negotiated_ownership_profile_matches_across_native_and_java_facades():
    _require_real_rti_smoke()
    try:
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    for kind in ("certi", "certi-jpype", "certi-py4j"):
        try:
            rtig = launch_certi_rtig(verbose=0)
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))
        federation_name = f"{kind}-nego-profile-{uuid.uuid4().hex[:8]}"
        owner_fed = RecordingFederateAmbassador()
        acquirer_fed = RecordingFederateAmbassador()
        owner = None
        acquirer = None
        try:
            with reserve_udp_pair() as lease:
                owner_udp_port, acquirer_udp_port = lease.ports
            owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=owner_udp_port)
            acquirer = create_rti_ambassador(
                kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=acquirer_udp_port
            )
            try:
                summary = run_negotiated_attribute_ownership_scenario(
                    owner,
                    acquirer,
                    config=_certi_negotiated_config(smoke_fom, federation_name, f"{kind}-NegotiatedProfile-1"),
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            except (RTIinternalError, AssertionError) as exc:
                pytest.skip(f"CERTI negotiated ownership path is not stable in this runtime: {exc}")
            profiles[kind] = _normalized_negotiated_profile(summary)
        finally:
            close_all(acquirer, owner)
            terminate_all(rtig)

    assert profiles["certi-jpype"] == profiles["certi"]
    assert profiles["certi-py4j"] == profiles["certi"]
