from __future__ import annotations

import os
import uuid
from math import isinf
from pathlib import Path

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_backend_common import BackendUnavailableError
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import AttributeDivestitureWasNotRequested, InvalidLogicalTime, RTIinternalError
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_verification_harness import (
    NegotiatedOwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    TwoFederateExchangeConfig,
    run_confirm_divestiture_negotiated_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla2010.types import TimeQueryReturn
from hla2010_rti_certi.real_rti_certi import (
    discover_certi_runtime_profile,
    discover_certi_smoke_fom,
    launch_certi_rtig,
)
from tests.vendors.runtime_support import cleanup_federation, require_vendor_preflight, shutdown_runtime_resources, udp_port_pair


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    require_vendor_preflight("certi", operator_hint="./tools/certi-easy preflight")


def _exchange_time_profile(time_factory_name: str) -> dict[str, object]:
    if time_factory_name == "HLAinteger64Time":
        return {
            "logical_time_implementation_name": "HLAinteger64Time",
            "initial_time": HLAinteger64Time(0),
            "lookahead": HLAinteger64Interval(1),
            "advance_time": HLAinteger64Time(8),
            "timestamped_attribute_time": HLAinteger64Time(5),
            "timestamped_interaction_time": HLAinteger64Time(6),
        }
    if time_factory_name == "HLAfloat64Time":
        return {
            "logical_time_implementation_name": "HLAfloat64Time",
            "initial_time": HLAfloat64Time(0.0),
            "lookahead": HLAfloat64Interval(1.0),
            "advance_time": HLAfloat64Time(8.0),
            "timestamped_attribute_time": HLAfloat64Time(5.0),
            "timestamped_interaction_time": HLAfloat64Time(6.0),
        }
    raise AssertionError(f"unexpected time factory {time_factory_name}")


def _certi_exchange_config(
    smoke_fom: str,
    federation_name: str,
    object_instance_name: str,
    *,
    time_factory_name: str,
) -> TwoFederateExchangeConfig:
    time_profile = dict(_exchange_time_profile(time_factory_name))
    time_profile.pop("initial_time", None)
    return TwoFederateExchangeConfig(
        federation_name=federation_name,
        fom_modules=(smoke_fom,),
        object_class_name="TestObjectClassR",
        attribute_name="DataR",
        interaction_class_name="MsgR",
        parameter_name="MsgDataR",
        object_instance_name=object_instance_name,
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=True,
        timestamped_attribute_payload=b"payload-tso",
        timestamped_attribute_tag=b"reflect-tso",
        timestamped_interaction_payload=b"hello-tso",
        timestamped_interaction_tag=b"interaction-tso",
        **time_profile,
    )


def _normalized_exchange_profile(summary: dict[str, object]) -> dict[str, object]:
    return {
        "reflect_payload": summary["reflect"].args[1],
        "reflect_tag": summary["reflect"].args[2],
        "reflect_order": summary["reflect"].args[3].name,
        "interaction_payload": summary["interaction"].args[1],
        "interaction_tag": summary["interaction"].args[2],
        "interaction_order": summary["interaction"].args[3].name,
        "timed_reflect_payload": summary["timed_reflect"].args[1],
        "timed_reflect_tag": summary["timed_reflect"].args[2],
        "timed_reflect_order": summary["timed_reflect"].args[3].name,
        "timed_reflect_time": float(summary["timed_reflect"].args[5].value),
        "timed_interaction_payload": summary["timed_interaction"].args[1],
        "timed_interaction_tag": summary["timed_interaction"].args[2],
        "timed_interaction_order": summary["timed_interaction"].args[3].name,
        "timed_interaction_time": float(summary["timed_interaction"].args[5].value),
        "advance_grant_time": float(summary["advance_grant"].args[0].value),
    }


def _logical_time_value(value: object) -> float:
    return float(getattr(value, "value", value))


def _logical_time_wire_type(value: object) -> str:
    if isinstance(value, HLAinteger64Time):
        return "HLAinteger64Time"
    if isinstance(value, HLAfloat64Time):
        return "HLAfloat64Time"
    raise AssertionError(f"unexpected logical time value {value!r}")


def _evoke_pair(left, right, *, iterations: int = 16) -> None:
    for _ in range(iterations):
        left.evokeMultipleCallbacks(0.0, 0.05)
        right.evokeMultipleCallbacks(0.0, 0.05)


def _assert_time_value_type(value: object, time_factory_name: str) -> None:
    if time_factory_name == "HLAinteger64Time":
        assert isinstance(value, HLAinteger64Time)
        return
    if time_factory_name == "HLAfloat64Time":
        assert isinstance(value, HLAfloat64Time)
        return
    raise AssertionError(f"unexpected time factory {time_factory_name}")


def _assert_certi_query_time_value(value: object, time_factory_name: str) -> None:
    _assert_time_value_type(value, time_factory_name)


def _helper_time_request(rti: object, command: str, logical_time: object, *, timeout: float = 1.0) -> None:
    backend = rti.backend
    response = backend.helper_request(
        command,
        _logical_time_wire_type(logical_time),
        _logical_time_value(logical_time),
        timeout=timeout,
    )
    assert response == []


def _certi_profile_backend_options(profile_name: str) -> dict[str, object]:
    profile = discover_certi_runtime_profile(profile_name)
    repo_root = Path(__file__).resolve().parents[2]
    helper_path = repo_root / "build" / "certi" / f"certi_smoke_helper_{profile.name}"
    options: dict[str, object] = {
        "certi_prefix": str(profile.runtime.prefix),
        "helper_path": helper_path,
        "allow_repo_build_overlay": profile.name != "certi-upstream",
    }
    if profile.name == "certi-upstream":
        build_root = os.environ.get("HLA2010_CERTI_UPSTREAM_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_ORIGINAL_BUILD_ROOT")
    elif profile.name == "certi-patched":
        build_root = os.environ.get("HLA2010_CERTI_PATCHED_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_BUILD_ROOT")
    else:
        build_root = os.environ.get("HLA2010_CERTI_BUILD_ROOT")
    if build_root:
        options["certi_build_root"] = build_root
    return options


def _normalized_negotiated_profile(summary: dict[str, object]) -> dict[str, object]:
    assumption = summary["assumption"]
    return {
        "negotiated_divestiture_supported": summary["negotiated_divestiture_supported"],
        "assumption_tag": (assumption.args[2] if assumption is not None else None),
        "release_tag": summary["release"].args[2],
        "cancellation_attr_count": len(summary["cancellation"].args[1]),
        "divested_count": len(summary["divested"]),
        "acquired_attr_count": len(summary["acquired"].args[1]),
        "informed_attribute_match": summary["informed"].args[1] == summary["owner_attribute"],
    }


def _certi_negotiated_config(smoke_fom: str, federation_name: str, object_instance_name: str) -> NegotiatedOwnershipScenarioConfig:
    return NegotiatedOwnershipScenarioConfig(
        federation_name=federation_name,
        fom_modules=(smoke_fom,),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="TestObjectClassR",
        attribute_name="DataR",
        object_instance_name=object_instance_name,
        assumption_tag=b"assume-offer",
        request_tag=b"acquire-request",
        cancel_tag=b"reacquire-request",
    )


def _certi_release_request_config(
    smoke_fom: str,
    federation_name: str,
    object_instance_name: str,
    *,
    owner_action: str,
) -> ReleaseRequestOwnershipScenarioConfig:
    return ReleaseRequestOwnershipScenarioConfig(
        federation_name=federation_name,
        fom_modules=(smoke_fom,),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="TestObjectClassR",
        attribute_name="DataR",
        object_instance_name=object_instance_name,
        request_tag=b"acquire-request",
        confirm_tag=b"confirm-tag",
        owner_action=owner_action,
    )


def _assert_certi_profile_time_query_and_fqr_baseline(
    profile_name: str,
    udp_base: int | None,
    time_factory_name: str,
) -> None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options(profile_name)
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{profile_name}-time-baseline-{uuid.uuid4().hex[:8]}"
    regulator_fed = RecordingFederateAmbassador()
    constrained_fed = RecordingFederateAmbassador()
    regulator = None
    constrained = None
    try:
        with udp_port_pair(udp_base) as (regulator_udp_port, constrained_udp_port):
            regulator = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=regulator_udp_port,
                **options,
            )
            constrained = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=constrained_udp_port,
                **options,
            )

            regulator.connect(regulator_fed, CallbackModel.HLA_EVOKED)
            constrained.connect(constrained_fed, CallbackModel.HLA_EVOKED)
            regulator.createFederationExecution(federation_name, [smoke_fom], time_factory_name)
            regulator.joinFederationExecution("Regulator", "TimeFederate", federation_name)
            constrained.joinFederationExecution("Constrained", "TimeFederate", federation_name)

            if profile_name == "certi-upstream":
                with pytest.raises((BackendUnavailableError, RTIinternalError), match="Network Read Error|LAST message type"):
                    constrained.queryGALT()
                return

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
            _evoke_pair(regulator, constrained)

            assert regulator_fed.last_callback("timeRegulationEnabled") is not None
            assert constrained_fed.last_callback("timeConstrainedEnabled") is not None
            enabled_galt = constrained.queryGALT()
            enabled_lits = constrained.queryLITS()
            assert enabled_galt.time_is_valid is True
            assert enabled_lits.time_is_valid is True
            assert _logical_time_value(enabled_galt.time) == _logical_time_value(time_profile["lookahead"])
            assert _logical_time_value(enabled_lits.time) == _logical_time_value(time_profile["lookahead"])
            try:
                assert _logical_time_value(regulator.queryLookahead()) == _logical_time_value(time_profile["lookahead"])
                regulator.modifyLookahead(time_profile["modified_lookahead"])
                assert _logical_time_value(regulator.queryLookahead()) == _logical_time_value(time_profile["modified_lookahead"])
            except RTIinternalError as exc:
                if profile_name in {"certi-upstream", "certi-patched"} and "Not yet implemented" in str(exc):
                    pytest.xfail("CERTI queryLookahead/modifyLookahead are not implemented in this runtime")
                raise

            regulator_cls = regulator.getObjectClassHandle("TestObjectClassR")
            constrained_cls = constrained.getObjectClassHandle("TestObjectClassR")
            regulator_attr = regulator.getAttributeHandle(regulator_cls, "DataR")
            constrained_attr = constrained.getAttributeHandle(constrained_cls, "DataR")
            regulator_int = regulator.getInteractionClassHandle("MsgR")
            regulator_param = regulator.getParameterHandle(regulator_int, "MsgDataR")
            regulator.publishObjectClassAttributes(regulator_cls, {regulator_attr})
            constrained.subscribeObjectClassAttributes(constrained_cls, {constrained_attr})
            regulator.publishInteractionClass(regulator_int)
            constrained.subscribeInteractionClass(regulator_int)
            regulator_obj = regulator.registerObjectInstance(regulator_cls, f"{federation_name}-Lookahead")
            _evoke_pair(regulator, constrained)

            zero_time = time_profile["initial_time"]
            with pytest.raises(InvalidLogicalTime):
                regulator.updateAttributeValues(
                    regulator_obj,
                    {regulator_attr: b"lookahead-early"},
                    b"lookahead-early",
                    zero_time,
                )
            with pytest.raises(InvalidLogicalTime):
                regulator.sendInteraction(
                    regulator_int,
                    {regulator_param: b"lookahead-early"},
                    b"lookahead-early",
                    zero_time,
                )

            constrained.flushQueueRequest(time_profile["timestamped_interaction_time"])
            _evoke_pair(regulator, constrained)

            grant = constrained_fed.last_callback("timeAdvanceGrant")
            assert grant is not None
            _assert_time_value_type(grant.args[0], time_factory_name)
            assert getattr(grant.args[0], "value", grant.args[0]) == getattr(time_profile["lookahead"], "value", time_profile["lookahead"])

            cleanup_federation(
                federation_name,
                destroyer=regulator,
                destroyer_resign_action=ResignAction.NO_ACTION,
                remaining_resignations=((constrained, ResignAction.NO_ACTION),),
                disconnect_rtis=(constrained, regulator),
            )
    finally:
        shutdown_runtime_resources(close_resources=(constrained, regulator), runtime_resources=(rtig,))


def _assert_certi_profile_queued_fqr_baseline(
    profile_name: str,
    udp_base: int | None,
    time_factory_name: str,
) -> None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options(profile_name)
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{profile_name}-queued-fqr-{uuid.uuid4().hex[:8]}"
    regulator_fed = RecordingFederateAmbassador()
    constrained_fed = RecordingFederateAmbassador()
    regulator = None
    constrained = None
    try:
        with udp_port_pair(udp_base) as (regulator_udp_port, constrained_udp_port):
            regulator = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=regulator_udp_port,
                **options,
            )
            constrained = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=constrained_udp_port,
                **options,
            )

            regulator.connect(regulator_fed, CallbackModel.HLA_EVOKED)
            constrained.connect(constrained_fed, CallbackModel.HLA_EVOKED)
            regulator.createFederationExecution(federation_name, [smoke_fom], time_factory_name)
            regulator.joinFederationExecution("Regulator", "TimeFederate", federation_name)
            constrained.joinFederationExecution("Constrained", "TimeFederate", federation_name)

            if profile_name == "certi-upstream":
                with pytest.raises((BackendUnavailableError, RTIinternalError), match="LAST message type|Network Read Error|Unimplemented|RTIinternalError"):
                    regulator.getObjectClassHandle("TestObjectClassR")
                return

        regulator_cls = regulator.getObjectClassHandle("TestObjectClassR")
        constrained_cls = constrained.getObjectClassHandle("TestObjectClassR")
        regulator_attr = regulator.getAttributeHandle(regulator_cls, "DataR")
        constrained_attr = constrained.getAttributeHandle(constrained_cls, "DataR")
        time_profile = _exchange_time_profile(time_factory_name)
        object_name = f"{profile_name}-FlushTarget"

        regulator.publishObjectClassAttributes(regulator_cls, {regulator_attr})
        constrained.subscribeObjectClassAttributes(constrained_cls, {constrained_attr})
        regulator.enableTimeRegulation(time_profile["lookahead"])
        constrained.enableTimeConstrained()
        _evoke_pair(regulator, constrained)

        obj = regulator.registerObjectInstance(regulator_cls, object_name)
        _evoke_pair(regulator, constrained)
        constrained_fed.clear()

        regulator.changeAttributeOrderType(obj, {regulator_attr}, OrderType.TIMESTAMP)
        _evoke_pair(regulator, constrained)

        regulator.updateAttributeValues(
            obj,
            {regulator_attr: b"five"},
            b"t5",
            time_profile["timestamped_attribute_time"],
        )
        earlier_time_value = _logical_time_value(time_profile["timestamped_attribute_time"]) - 2.0
        earlier_time = type(time_profile["timestamped_attribute_time"])(earlier_time_value)
        regulator.updateAttributeValues(
            obj,
            {regulator_attr: b"three"},
            b"t3",
            earlier_time,
        )
        _evoke_pair(regulator, constrained)
        assert not constrained_fed.callbacks_named("reflectAttributeValues")

        regulator.timeAdvanceRequest(time_profile["advance_time"])
        _evoke_pair(regulator, constrained)

        constrained.flushQueueRequest(time_profile["timestamped_interaction_time"])
        _evoke_pair(regulator, constrained)

        reflections = constrained_fed.callbacks_named("reflectAttributeValues")
        assert [rec.args[1][constrained_attr] for rec in reflections] == [b"three", b"five"]
        grant = constrained_fed.last_callback("timeAdvanceGrant")
        assert grant is not None
        _assert_time_value_type(grant.args[0], time_factory_name)
        assert _logical_time_value(grant.args[0]) == _logical_time_value(earlier_time)

        cleanup_federation(
            federation_name,
            destroyer=regulator,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((constrained, ResignAction.NO_ACTION),),
            disconnect_rtis=(constrained, regulator),
        )
    finally:
        shutdown_runtime_resources(close_resources=(constrained, regulator), runtime_resources=(rtig,))


def _assert_certi_patched_fail_fast_time_request_matrix(
    udp_base: int | None,
    time_factory_name: str,
    helper_command: str,
) -> None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options("certi-patched")
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"certi-patched-{helper_command.lower()}-{uuid.uuid4().hex[:8]}"
    regulator_fed = RecordingFederateAmbassador()
    constrained_fed = RecordingFederateAmbassador()
    regulator = None
    constrained = None
    try:
        with udp_port_pair(udp_base) as (regulator_udp_port, constrained_udp_port):
            regulator = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=regulator_udp_port,
                **options,
            )
            constrained = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=constrained_udp_port,
                **options,
            )

            regulator.connect(regulator_fed, CallbackModel.HLA_EVOKED)
            constrained.connect(constrained_fed, CallbackModel.HLA_EVOKED)
            regulator.createFederationExecution(federation_name, [smoke_fom], time_factory_name)
            regulator.joinFederationExecution("Regulator", "TimeFederate", federation_name)
            constrained.joinFederationExecution("Constrained", "TimeFederate", federation_name)

        time_profile = _exchange_time_profile(time_factory_name)
        regulator.enableTimeRegulation(time_profile["lookahead"])
        constrained.enableTimeConstrained()
        _evoke_pair(regulator, constrained)

        if helper_command == "TIME_ADVANCE_REQUEST_AVAILABLE":
            regulator.timeAdvanceRequest(time_profile["advance_time"])
            _evoke_pair(regulator, constrained)

            _helper_time_request(constrained, helper_command, HLAinteger64Time(5) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(5.0))
            _evoke_pair(regulator, constrained)

            grant = constrained_fed.last_callback("timeAdvanceGrant")
            assert grant is not None
            _assert_time_value_type(grant.args[0], time_factory_name)
            assert _logical_time_value(grant.args[0]) == 5.0

        elif helper_command in {"NEXT_MESSAGE_REQUEST", "NEXT_MESSAGE_REQUEST_AVAILABLE"}:
            regulator_cls = regulator.getObjectClassHandle("TestObjectClassR")
            constrained_cls = constrained.getObjectClassHandle("TestObjectClassR")
            regulator_attr = regulator.getAttributeHandle(regulator_cls, "DataR")
            constrained_attr = constrained.getAttributeHandle(constrained_cls, "DataR")
            object_name = f"{federation_name}-Obj"

            regulator.publishObjectClassAttributes(regulator_cls, {regulator_attr})
            constrained.subscribeObjectClassAttributes(constrained_cls, {constrained_attr})
            obj = regulator.registerObjectInstance(regulator_cls, object_name)
            _evoke_pair(regulator, constrained)
            constrained_fed.clear()
            regulator.changeAttributeOrderType(obj, {regulator_attr}, OrderType.TIMESTAMP)
            _evoke_pair(regulator, constrained)

            regulator.updateAttributeValues(
                obj,
                {regulator_attr: b"late"},
                b"t3",
                HLAinteger64Time(3) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(3.0),
            )
            regulator.updateAttributeValues(
                obj,
                {regulator_attr: b"early"},
                b"t2",
                HLAinteger64Time(2) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(2.0),
            )
            regulator.timeAdvanceRequest(HLAinteger64Time(4) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(4.0))
            _evoke_pair(regulator, constrained)

            _helper_time_request(constrained, helper_command, HLAinteger64Time(10) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(10.0))
            _evoke_pair(regulator, constrained)

            first = constrained_fed.last_callback("reflectAttributeValues")
            assert first is not None
            assert first.args[1][constrained_attr] == b"early"
            grant = constrained_fed.last_callback("timeAdvanceGrant")
            assert grant is not None
            _assert_time_value_type(grant.args[0], time_factory_name)
            assert _logical_time_value(grant.args[0]) == 2.0

            _helper_time_request(constrained, helper_command, HLAinteger64Time(10) if time_factory_name == "HLAinteger64Time" else HLAfloat64Time(10.0))
            _evoke_pair(regulator, constrained)

            second = constrained_fed.last_callback("reflectAttributeValues")
            assert second is not None
            assert second.args[1][constrained_attr] == b"late"
            grant = constrained_fed.last_callback("timeAdvanceGrant")
            assert grant is not None
            _assert_time_value_type(grant.args[0], time_factory_name)
            assert _logical_time_value(grant.args[0]) == 3.0

        else:
            raise AssertionError(f"unexpected helper command {helper_command}")

        cleanup_federation(
            federation_name,
            destroyer=regulator,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((constrained, ResignAction.NO_ACTION),),
            disconnect_rtis=(constrained, regulator),
        )
    finally:
        shutdown_runtime_resources(close_resources=(constrained, regulator), runtime_resources=(rtig,))


def _assert_certi_profile_negotiated_ownership_baseline(profile_name: str, udp_base: int | None) -> None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options(profile_name)
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{profile_name}-nego-baseline-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        with udp_port_pair(udp_base) as (owner_udp_port, acquirer_udp_port):
            owner = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=owner_udp_port,
                **options,
            )
            acquirer = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=acquirer_udp_port,
                **options,
            )

            config = _certi_negotiated_config(smoke_fom, federation_name, f"{profile_name}-NegotiatedBaseline-1")
            if profile_name == "certi-upstream":
                with pytest.raises(
                    RTIinternalError,
                    match="Network Read Error|Connection closed by client|LAST message type",
                ):
                    run_negotiated_attribute_ownership_scenario(
                        owner,
                        acquirer,
                        config=config,
                        owner_federate=owner_fed,
                        acquirer_federate=acquirer_fed,
                    )
                return

            summary = run_negotiated_attribute_ownership_scenario(
                owner,
                acquirer,
                config=config,
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
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
        shutdown_runtime_resources(close_resources=(acquirer, owner), runtime_resources=(rtig,))


def _normalized_release_request_profile(summary: dict[str, object]) -> dict[str, object]:
    acquired = summary.get("acquired")
    informed = summary.get("informed")
    return {
        "release_tag": summary["release"].args[2],
        "acquired_present": acquired is not None,
        "acquired_tag": (acquired.args[2] if acquired is not None else None),
        "divested": summary.get("divested"),
        "informed_present": informed is not None,
        "informed_attribute_match": (informed.args[1] == summary["owner_attribute"] if informed is not None else False),
    }


def _normalized_confirm_divestiture_profile(summary: dict[str, object]) -> dict[str, object]:
    acquired = summary["acquired"]
    informed = summary["informed"]
    return {
        "confirm_notice_object_match": summary["divestiture_confirmation"].args[0] == summary["object_instance"],
        "confirm_notice_attribute_match": summary["divestiture_confirmation"].args[1] == {summary["owner_attribute"]},
        "acquired_tag": acquired.args[2] if acquired is not None else None,
        "acquired_attribute_match": acquired.args[1] == {summary["acquirer_attribute"]} if acquired is not None else False,
        "informed_present": informed is not None,
        "informed_attribute_match": informed.args[1] == summary["owner_attribute"] if informed is not None else False,
    }


def _run_certi_profile_release_request_branch_baseline(
    profile_name: str,
    udp_base: int | None,
    owner_action: str,
) -> dict[str, object] | None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options(profile_name)
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{profile_name}-release-{owner_action}-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        with udp_port_pair(udp_base) as (owner_udp_port, acquirer_udp_port):
            owner = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=owner_udp_port,
                **options,
            )
            acquirer = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=acquirer_udp_port,
                **options,
            )

        config = _certi_release_request_config(
            smoke_fom,
            federation_name,
            f"{profile_name}-ReleaseBranch-{owner_action}",
            owner_action=owner_action,
        )

        if profile_name == "certi-upstream":
            with pytest.raises(
                (RTIinternalError, BackendUnavailableError),
                match=(
                    "Not yet implemented|Not Implemented|Network Read Error|Connection closed by client|"
                    "LAST message type|Subprocess transport produced no response"
                ),
            ):
                run_release_request_ownership_scenario(
                    owner,
                    acquirer,
                    config=config,
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            return None

        if owner_action == "confirm":
            with pytest.raises(AttributeDivestitureWasNotRequested, match="confirmDivestiture requires prior negotiated divestiture"):
                run_release_request_ownership_scenario(
                    owner,
                    acquirer,
                    config=config,
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            return {"owner_action": owner_action, "confirm_exception": "AttributeDivestitureWasNotRequested"}

        summary = run_release_request_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )
        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"acquire-request",
        )

        if owner_action == "deny":
            assert summary["acquired"] is None
        elif owner_action == "ifwanted":
            assert summary["divested"] == {summary["owner_attribute"]}
            assert summary["acquired"].args[2] == b""
        else:
            raise AssertionError(f"unexpected owner_action {owner_action!r}")

        cleanup_federation(
            federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
        return summary
    finally:
        shutdown_runtime_resources(close_resources=(acquirer, owner), runtime_resources=(rtig,))


def _assert_certi_profile_release_request_branch_baseline(profile_name: str, udp_base: int, owner_action: str) -> None:
    summary = _run_certi_profile_release_request_branch_baseline(profile_name, udp_base, owner_action)
    if profile_name == "certi-upstream":
        return
    assert summary is not None
    if owner_action == "confirm":
        assert summary["confirm_exception"] == "AttributeDivestitureWasNotRequested"


def _run_certi_profile_confirm_divestiture_negotiated_baseline(profile_name: str, udp_base: int | None) -> dict[str, object] | None:
    _require_real_rti_smoke()
    try:
        options = _certi_profile_backend_options(profile_name)
        rtig = launch_certi_rtig(
            certi_prefix=options["certi_prefix"],
            certi_build_root=options.get("certi_build_root"),
            allow_repo_build_overlay=bool(options["allow_repo_build_overlay"]),
            verbose=0,
        )
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{profile_name}-confirm-nego-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        with udp_port_pair(udp_base) as (owner_udp_port, acquirer_udp_port):
            owner = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=owner_udp_port,
                **options,
            )
            acquirer = create_rti_ambassador(
                "certi",
                launch_rtig=False,
                tcp_port=rtig.tcp_port,
                udp_port=acquirer_udp_port,
                **options,
            )

        config = _certi_negotiated_config(smoke_fom, federation_name, f"{profile_name}-ConfirmNegotiated-1")
        if profile_name == "certi-upstream":
            with pytest.raises(
                (RTIinternalError, BackendUnavailableError),
                match=(
                    "Not yet implemented|Not Implemented|Network Read Error|Connection closed by client|"
                    "LAST message type|Subprocess transport produced no response"
                ),
            ):
                run_confirm_divestiture_negotiated_scenario(
                    owner,
                    acquirer,
                    config=config,
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            return None

        summary = run_confirm_divestiture_negotiated_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )
        assert summary["acquired"].args[2] == b"confirm-tag"

        cleanup_federation(
            federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )
        return summary
    finally:
        shutdown_runtime_resources(close_resources=(acquirer, owner), runtime_resources=(rtig,))


def _assert_certi_profile_confirm_divestiture_negotiated_baseline(profile_name: str, udp_base: int) -> None:
    summary = _run_certi_profile_confirm_divestiture_negotiated_baseline(profile_name, udp_base)
    if profile_name == "certi-upstream":
        return
    assert summary is not None


__all__ = [
    "BackendUnavailableError",
    "CallbackModel",
    "HLAfloat64Interval",
    "HLAfloat64Time",
    "HLAinteger64Interval",
    "HLAinteger64Time",
    "InvalidLogicalTime",
    "OrderType",
    "Path",
    "RTIinternalError",
    "RecordingFederateAmbassador",
    "ResignAction",
    "TimeQueryReturn",
    "create_rti_ambassador",
    "discover_certi_runtime_profile",
    "discover_certi_smoke_fom",
    "launch_certi_rtig",
    "pytest",
    "uuid",
    "_assert_certi_profile_negotiated_ownership_baseline",
    "_assert_certi_patched_fail_fast_time_request_matrix",
    "_assert_certi_profile_confirm_divestiture_negotiated_baseline",
    "_assert_certi_profile_queued_fqr_baseline",
    "_assert_certi_profile_release_request_branch_baseline",
    "_assert_certi_profile_time_query_and_fqr_baseline",
    "_assert_certi_query_time_value",
    "_assert_time_value_type",
    "_certi_exchange_config",
    "_certi_negotiated_config",
    "_certi_profile_backend_options",
    "_certi_release_request_config",
    "_evoke_pair",
    "_exchange_time_profile",
    "_helper_time_request",
    "_logical_time_value",
    "_logical_time_wire_type",
    "_normalized_confirm_divestiture_profile",
    "_normalized_exchange_profile",
    "_normalized_negotiated_profile",
    "_normalized_release_request_profile",
    "_require_real_rti_smoke",
    "_run_certi_profile_confirm_divestiture_negotiated_baseline",
    "_run_certi_profile_release_request_branch_baseline",
]
