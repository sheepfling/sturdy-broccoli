from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.enums import OrderType, ResignAction
from hla2010.real_rti import launch_pitch_runtime
from hla2010.rti import create_rti_ambassador
from hla2010.testing import (
    assert_two_federate_exchange_callback_history,
    OwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    run_attribute_ownership_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAinteger64Interval, HLAinteger64Time


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


def _pitch_exchange_config(federation_name: str, object_instance_name: str) -> TwoFederateExchangeConfig:
    return TwoFederateExchangeConfig(
        federation_name=federation_name,
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=object_instance_name,
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=True,
        lookahead=HLAinteger64Interval(1),
        advance_time=HLAinteger64Time(8),
        timestamped_attribute_payload=b"payload-tso",
        timestamped_attribute_tag=b"reflect-tso",
        timestamped_attribute_time=HLAinteger64Time(5),
        timestamped_interaction_payload=b"hello-tso",
        timestamped_interaction_tag=b"interaction-tso",
        timestamped_interaction_time=HLAinteger64Time(6),
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
        "timed_reflect_time": int(summary["timed_reflect"].args[5].value),
        "timed_interaction_payload": summary["timed_interaction"].args[1],
        "timed_interaction_tag": summary["timed_interaction"].args[2],
        "timed_interaction_order": summary["timed_interaction"].args[3].name,
        "timed_interaction_time": int(summary["timed_interaction"].args[5].value),
        "advance_grant_time": int(summary["advance_grant"].args[0].value),
    }


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_exchange_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-matrix-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    try:
        publisher = create_rti_ambassador(kind)
        subscriber = create_rti_ambassador(kind)
        config = _pitch_exchange_config(federation_name, f"{kind}-Object-1")
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
        runtime.terminate()


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_synchronization_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-sync-{uuid.uuid4().hex[:8]}"
    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    leader = None
    wing = None
    try:
        leader = create_rti_ambassador(kind)
        wing = create_rti_ambassador(kind)
        config = SynchronizationScenarioConfig(
            federation_name=federation_name,
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
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
        runtime.terminate()


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ownership_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-owner-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        owner = create_rti_ambassador(kind)
        acquirer = create_rti_ambassador(kind)
        config = OwnershipScenarioConfig(
            federation_name=federation_name,
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
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
        runtime.terminate()


def test_pitch_time_semantic_profile_matches_across_java_bridges():
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    try:
        for kind in ("pitch-jpype", "pitch-py4j"):
            federation_name = f"{kind}-time-profile-{uuid.uuid4().hex[:8]}"
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
                    config=_pitch_exchange_config(federation_name, f"{kind}-TimeProfile-1"),
                    publisher_federate=publisher_fed,
                    subscriber_federate=subscriber_fed,
                )
                profiles[kind] = _normalized_exchange_profile(summary)
            finally:
                if subscriber is not None:
                    subscriber.close()
                if publisher is not None:
                    publisher.close()
    finally:
        runtime.terminate()

    assert profiles["pitch-py4j"] == profiles["pitch-jpype"]
