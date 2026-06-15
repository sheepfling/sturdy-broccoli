# ruff: noqa: F401,F403

from dataclasses import replace

from tests.vendors.certi_real_backend_matrix_support import *
from tests.vendors.certi_real_backend_matrix_support import (
    _assert_certi_profile_queued_fqr_baseline,
    _assert_certi_profile_time_query_and_fqr_baseline,
    _assert_certi_patched_fail_fast_time_request_matrix,
    _assert_certi_query_time_value,
    _assert_time_value_type,
    _evoke_pair,
    _exchange_time_profile,
    _logical_time_value,
    _require_real_rti_smoke,
)
from hla2010_verification_harness import (
    run_section8_available_and_flush_case,
    run_section8_available_and_retraction_case,
    run_section8_duplicate_enable_rejection_case,
    run_section8_order_override_case,
    run_section8_ordering_and_query_case,
    run_section8_request_retraction_case,
    run_section8_state_services_case,
    run_section8_tar_galt_boundary_case,
    run_section8_time_bound_query_case,
    section8_matrix_config,
)
from tests.vendors.runtime_support import assert_all_terminated, cleanup_federation, close_all, reserve_udp_pair, terminate_all


def _run_certi_section8_pair(kind: str, time_factory_name: str, case_name: str, runner):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    left = None
    right = None
    try:
        with reserve_udp_pair() as lease:
            left_udp_port, right_udp_port = lease.ports
        left = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=left_udp_port)
        right = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=right_udp_port)
        config = replace(
            section8_matrix_config(f"{kind}-{case_name}-{uuid.uuid4().hex[:8]}", time_factory_name),
            fom_modules=(smoke_fom,),
        )
        return runner(left, right, config=config)
    finally:
        close_all(right, left)
        terminate_all(rtig)
        assert_all_terminated(rtig)

@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_time_query_and_fqr_matrix(kind: str, time_factory_name: str):
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-time-query-{uuid.uuid4().hex[:8]}"
    regulator_fed = RecordingFederateAmbassador()
    constrained_fed = RecordingFederateAmbassador()
    regulator = None
    constrained = None
    try:
        with reserve_udp_pair() as lease:
            regulator_udp_port, constrained_udp_port = lease.ports
        regulator = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=regulator_udp_port
        )
        constrained = create_rti_ambassador(
            kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=constrained_udp_port
        )

        regulator.connect(regulator_fed, CallbackModel.HLA_EVOKED)
        constrained.connect(constrained_fed, CallbackModel.HLA_EVOKED)
        regulator.createFederationExecution(federation_name, [smoke_fom], time_factory_name)
        regulator.joinFederationExecution("Regulator", "TimeFederate", federation_name)
        constrained.joinFederationExecution("Constrained", "TimeFederate", federation_name)

        initial_galt = constrained.queryGALT()
        initial_lits = constrained.queryLITS()
        assert isinstance(initial_galt, TimeQueryReturn)
        assert isinstance(initial_lits, TimeQueryReturn)
        assert initial_galt.time_is_valid is True
        assert initial_lits.time_is_valid is True
        assert isinf(initial_galt.time.value)
        assert isinf(initial_lits.time.value)

        time_profile = _exchange_time_profile(time_factory_name)
        regulator.enableTimeRegulation(time_profile["lookahead"])
        constrained.enableTimeConstrained()
        for _ in range(16):
            regulator.evokeMultipleCallbacks(0.0, 0.05)
            constrained.evokeMultipleCallbacks(0.0, 0.05)

        assert regulator_fed.last_callback("timeRegulationEnabled") is not None
        assert constrained_fed.last_callback("timeConstrainedEnabled") is not None

        enabled_galt = constrained.queryGALT()
        enabled_lits = constrained.queryLITS()
        assert enabled_galt.time_is_valid is True
        assert enabled_lits.time_is_valid is True
        _assert_certi_query_time_value(enabled_galt.time, time_factory_name)
        _assert_certi_query_time_value(enabled_lits.time, time_factory_name)
        assert _logical_time_value(enabled_galt.time) == pytest.approx(_logical_time_value(time_profile["lookahead"]))
        assert _logical_time_value(enabled_lits.time) == pytest.approx(_logical_time_value(time_profile["lookahead"]))

        constrained.flushQueueRequest(time_profile["timestamped_interaction_time"])
        _evoke_pair(regulator, constrained)
        grant = constrained_fed.last_callback("timeAdvanceGrant")
        assert grant is not None
        _assert_time_value_type(grant.args[0], time_factory_name)
        assert _logical_time_value(grant.args[0]) == pytest.approx(
            _logical_time_value(time_profile["lookahead"])
        )

        cleanup_federation(
            federation_name,
            destroyer=regulator,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((constrained, ResignAction.NO_ACTION),),
            disconnect_rtis=(constrained, regulator),
        )
    finally:
        close_all(constrained, regulator)
        terminate_all(rtig)
        assert_all_terminated(rtig)


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_state_services_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-state", run_section8_state_services_case)

    assert summary["publisher_federate"].last_callback("timeRegulationEnabled") is not None
    assert summary["subscriber_federate"].last_callback("timeConstrainedEnabled") is not None
    assert summary["initial_lookahead"] is not None
    assert summary["modified_lookahead"] is not None
    assert summary["modified_lookahead"] != summary["initial_lookahead"]


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_logical_time_query_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-logical-time", run_section8_state_services_case)

    assert summary["publisher_initial_time"].value == 0 or summary["publisher_initial_time"].value == 0.0
    assert summary["subscriber_initial_time"].value == 0 or summary["subscriber_initial_time"].value == 0.0


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_state_toggle_services_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-state-toggles", run_section8_state_services_case)

    assert summary["initial_lookahead"] is not None
    assert summary["modified_lookahead"] is not None
    assert summary["modified_lookahead"] != summary["initial_lookahead"]


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_time_bound_query_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-time-queries", run_section8_time_bound_query_case)

    assert isinstance(summary["initial_galt"], TimeQueryReturn)
    assert isinstance(summary["initial_lits"], TimeQueryReturn)


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_ordering_and_query_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-ordering", run_section8_ordering_and_query_case)

    assert summary["sender_grant"] is not None
    assert summary["first_grant"] is not None
    assert summary["second_grant"] is not None
    assert summary["first_receive"] is not None
    assert summary["second_receive"] is not None


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_available_and_flush_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-available-flush", run_section8_available_and_flush_case)

    assert summary["available_grant"] is not None
    assert summary["flush_grant"] is not None
    assert summary["flushed_receive"] is not None


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_available_and_retraction_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-available", run_section8_available_and_retraction_case)

    assert summary["available_grant"] is not None
    assert summary["flush_grant"] is not None


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_order_override_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-order-override", run_section8_order_override_case)

    assert summary["reflect"] is not None
    assert summary["receive"] is not None


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_request_retraction_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-request-retraction", run_section8_request_retraction_case)

    assert summary["received"] is not None
    assert summary["request_retraction"] is not None


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_duplicate_enable_rejection_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(
        kind,
        time_factory_name,
        "section8-duplicate-enable",
        run_section8_duplicate_enable_rejection_case,
    )

    assert summary["regulation_error"] is not None
    assert summary["constrained_error"] is not None
    assert summary["final_regulation_callback_count"] == summary["initial_regulation_callback_count"]
    assert summary["final_constrained_callback_count"] == summary["initial_constrained_callback_count"]


@pytest.mark.parametrize("kind", ["certi"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_section8_tar_galt_boundary_matrix(kind: str, time_factory_name: str):
    summary = _run_certi_section8_pair(kind, time_factory_name, "section8-tar-galt", run_section8_tar_galt_boundary_case)

    assert summary["equal_galt"].time is not None
    assert summary["grant"] is None
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_upstream_time_query_and_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_time_query_and_fqr_baseline("certi-upstream", None, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_time_query_and_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_time_query_and_fqr_baseline("certi-patched", None, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_upstream_queued_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_queued_fqr_baseline("certi-upstream", None, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_queued_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_queued_fqr_baseline("certi-patched", None, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_time_advance_request_available_fail_fast_matrix(time_factory_name: str):
    _assert_certi_patched_fail_fast_time_request_matrix(None, time_factory_name, "TIME_ADVANCE_REQUEST_AVAILABLE")
