# ruff: noqa: F401,F403

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

@pytest.mark.parametrize("kind,udp_base", [("certi", 60901), ("certi-jpype", 60911), ("certi-py4j", 60921)])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_backend_time_query_and_fqr_matrix(kind: str, udp_base: int, time_factory_name: str):
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
        regulator = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
        constrained = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)

        regulator.connect(regulator_fed, CallbackModel.HLA_EVOKED)
        constrained.connect(constrained_fed, CallbackModel.HLA_EVOKED)
        regulator.create_federation_execution(federation_name, [smoke_fom], time_factory_name)
        regulator.join_federation_execution("Regulator", "TimeFederate", federation_name)
        constrained.join_federation_execution("Constrained", "TimeFederate", federation_name)

        initial_galt = constrained.query_galt()
        initial_lits = constrained.query_lits()
        assert isinstance(initial_galt, TimeQueryReturn)
        assert isinstance(initial_lits, TimeQueryReturn)
        assert initial_galt.time_is_valid is True
        assert initial_lits.time_is_valid is True
        assert isinf(initial_galt.time.value)
        assert isinf(initial_lits.time.value)

        time_profile = _exchange_time_profile(time_factory_name)
        regulator.enable_time_regulation(time_profile["lookahead"])
        constrained.enable_time_constrained()
        for _ in range(16):
            regulator.evoke_multiple_callbacks(0.0, 0.05)
            constrained.evoke_multiple_callbacks(0.0, 0.05)

        assert regulator_fed.last_callback("timeRegulationEnabled") is not None
        assert constrained_fed.last_callback("timeConstrainedEnabled") is not None

        enabled_galt = constrained.query_galt()
        enabled_lits = constrained.query_lits()
        assert enabled_galt.time_is_valid is True
        assert enabled_lits.time_is_valid is True
        _assert_certi_query_time_value(enabled_galt.time, time_factory_name)
        _assert_certi_query_time_value(enabled_lits.time, time_factory_name)
        assert _logical_time_value(enabled_galt.time) == pytest.approx(_logical_time_value(time_profile["lookahead"]))
        assert _logical_time_value(enabled_lits.time) == pytest.approx(_logical_time_value(time_profile["lookahead"]))

        constrained.flush_queue_request(time_profile["timestamped_interaction_time"])
        _evoke_pair(regulator, constrained)
        grant = constrained_fed.last_callback("timeAdvanceGrant")
        assert grant is not None
        _assert_time_value_type(grant.args[0], time_factory_name)
        assert _logical_time_value(grant.args[0]) == pytest.approx(
            _logical_time_value(time_profile["lookahead"])
        )

        constrained.resign_federation_execution(ResignAction.NO_ACTION)
        regulator.resign_federation_execution(ResignAction.NO_ACTION)
        regulator.destroy_federation_execution(federation_name)
        constrained.disconnect()
        regulator.disconnect()
    finally:
        if constrained is not None:
            constrained.close()
        if regulator is not None:
            regulator.close()
        rtig.terminate()
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_upstream_time_query_and_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_time_query_and_fqr_baseline("certi-upstream", 61001, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_time_query_and_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_time_query_and_fqr_baseline("certi-patched", 61011, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_upstream_queued_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_queued_fqr_baseline("certi-upstream", 61021, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_queued_fqr_baseline(time_factory_name: str):
    _assert_certi_profile_queued_fqr_baseline("certi-patched", 61031, time_factory_name)


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_certi_patched_time_advance_request_available_fail_fast_matrix(time_factory_name: str):
    _assert_certi_patched_fail_fast_time_request_matrix(61041, time_factory_name, "TIME_ADVANCE_REQUEST_AVAILABLE")
