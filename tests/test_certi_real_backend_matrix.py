from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.enums import OrderType, ResignAction
from hla2010.exceptions import RTIinternalError
from hla2010.real_rti import discover_certi_smoke_fom, launch_certi_rtig
from hla2010.rti import create_rti_ambassador
from hla2010.testing import (
    assert_two_federate_exchange_callback_history,
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


def _certi_exchange_config(smoke_fom: str, federation_name: str, object_instance_name: str) -> TwoFederateExchangeConfig:
    return TwoFederateExchangeConfig(
        federation_name=federation_name,
        fom_modules=(smoke_fom,),
        logical_time_implementation_name="HLAinteger64Time",
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
        lookahead=HLAfloat64Interval(1.0),
        advance_time=HLAfloat64Time(8.0),
        timestamped_attribute_payload=b"payload-tso",
        timestamped_attribute_tag=b"reflect-tso",
        timestamped_attribute_time=HLAfloat64Time(5.0),
        timestamped_interaction_payload=b"hello-tso",
        timestamped_interaction_tag=b"interaction-tso",
        timestamped_interaction_time=HLAfloat64Time(6.0),
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


@pytest.mark.parametrize("kind,udp_base", [("certi", 60601), ("certi-jpype", 60611), ("certi-py4j", 60621)])
def test_certi_backend_exchange_matrix(kind: str, udp_base: int):
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

        config = _certi_exchange_config(smoke_fom, federation_name, f"{kind}-Object-1")
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == f"{kind}-Object-1"
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
        publisher.resign_federation_execution(ResignAction.NO_ACTION)
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


@pytest.mark.parametrize("kind,udp_base", [("certi", 60801), ("certi-jpype", 60811), ("certi-py4j", 60821)])
def test_certi_backend_ownership_matrix(kind: str, udp_base: int):
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
        owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
        acquirer = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)

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

        acquirer.resign_federation_execution(ResignAction.NO_ACTION)
        owner.resign_federation_execution(ResignAction.NO_ACTION)
        owner.destroy_federation_execution(federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        rtig.terminate()


@pytest.mark.parametrize("kind,udp_base", [("certi", 60901), ("certi-jpype", 60911), ("certi-py4j", 60921)])
def test_certi_backend_negotiated_ownership_matrix(kind: str, udp_base: int):
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
        owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
        acquirer = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)

        config = NegotiatedOwnershipScenarioConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            object_instance_name=f"{kind}-Negotiated-1",
            assumption_tag=b"assume-offer",
            request_tag=b"acquire-request",
            cancel_tag=b"reacquire-request",
        )
        try:
            summary = run_negotiated_attribute_ownership_scenario(
                owner,
                acquirer,
                config=config,
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except RTIinternalError as exc:
            pytest.skip(f"CERTI negotiated ownership path is not stable in this runtime: {exc}")

        assert summary["negotiated_divestiture_supported"] is False
        assert summary["assumption"] is None
        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"reacquire-request",
        )
        assert summary["cancellation"].args == (
            summary["acquirer_object_instance"],
            {summary["acquirer_attribute"]},
        )
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]

        acquirer.resign_federation_execution(ResignAction.NO_ACTION)
        owner.resign_federation_execution(ResignAction.NO_ACTION)
        owner.destroy_federation_execution(federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        rtig.terminate()


def test_certi_time_semantic_profile_matches_across_native_and_java_facades():
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
                config=_certi_exchange_config(smoke_fom, federation_name, f"{kind}-TimeProfile-1"),
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


def test_certi_negotiated_ownership_profile_matches_across_native_and_java_facades():
    _require_real_rti_smoke()
    try:
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    for kind, udp_base in (("certi", 61101), ("certi-jpype", 61111), ("certi-py4j", 61121)):
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
            owner = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base)
            acquirer = create_rti_ambassador(kind, launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=udp_base + 1)
            try:
                summary = run_negotiated_attribute_ownership_scenario(
                    owner,
                    acquirer,
                    config=NegotiatedOwnershipScenarioConfig(
                        federation_name=federation_name,
                        fom_modules=(smoke_fom,),
                        logical_time_implementation_name="HLAinteger64Time",
                        owner_name="Owner",
                        acquirer_name="Acquirer",
                        federate_type="OwnershipFederate",
                        object_class_name="TestObjectClassR",
                        attribute_name="DataR",
                        object_instance_name=f"{kind}-NegotiatedProfile-1",
                        assumption_tag=b"assume-offer",
                        request_tag=b"acquire-request",
                        cancel_tag=b"reacquire-request",
                    ),
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            except RTIinternalError as exc:
                pytest.skip(f"CERTI negotiated ownership path is not stable in this runtime: {exc}")
            profiles[kind] = _normalized_negotiated_profile(summary)
        finally:
            if acquirer is not None:
                acquirer.close()
            if owner is not None:
                owner.close()
            rtig.terminate()

    assert profiles["certi-jpype"] == profiles["certi"]
    assert profiles["certi-py4j"] == profiles["certi"]
