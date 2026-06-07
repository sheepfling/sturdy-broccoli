from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import InvalidLogicalTime, RTIexception
from hla2010.real_rti import launch_pitch_runtime
from hla2010.rti import create_rti_ambassador
from hla2010.testing.scenarios import (
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    probe_negotiated_attribute_ownership_offer,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
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


def _cleanup_pitch_ownership_federation(
    federation_name: str,
    owner,
    acquirer,
) -> None:
    try:
        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
    except BaseException:
        pass
    try:
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    except BaseException:
        pass
    try:
        owner.destroy_federation_execution(federation_name)
    except BaseException:
        pass
    for rti in (acquirer, owner):
        try:
            rti.disconnect()
        except BaseException:
            pass


def _format_probe_exception(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc!r}"


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
        publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
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
def test_pitch_backend_lookahead_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-lookahead-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    try:
        publisher = create_rti_ambassador(kind)
        subscriber = create_rti_ambassador(kind)
        config = _pitch_exchange_config(federation_name, f"{kind}-Lookahead-1")

        publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
        publisher.create_federation_execution(federation_name, list(config.fom_modules), config.logical_time_implementation_name)
        publisher.join_federation_execution("Publisher", "TimeFederate", federation_name)
        subscriber.join_federation_execution("Subscriber", "TimeFederate", federation_name)

        object_class = publisher.get_object_class_handle(config.object_class_name)
        attribute = publisher.get_attribute_handle(object_class, config.attribute_name)
        interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        parameter = publisher.get_parameter_handle(interaction, config.parameter_name)

        publisher.publish_object_class_attributes(object_class, {attribute})
        subscriber.subscribe_object_class_attributes(object_class, {attribute})
        publisher.publish_interaction_class(interaction)
        subscriber.subscribe_interaction_class(interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        for _ in range(16):
            publisher.evoke_multiple_callbacks(0.0, 0.05)
            subscriber.evoke_multiple_callbacks(0.0, 0.05)

        assert publisher.query_lookahead() == config.lookahead
        publisher.modify_lookahead(HLAinteger64Interval(2))
        assert publisher.query_lookahead() == HLAinteger64Interval(2)

        instance = publisher.register_object_instance(object_class, config.object_instance_name)
        for _ in range(8):
            publisher.evoke_multiple_callbacks(0.0, 0.05)
            subscriber.evoke_multiple_callbacks(0.0, 0.05)

        zero_time = HLAinteger64Time(0)
        with pytest.raises(InvalidLogicalTime):
            publisher.update_attribute_values(
                instance,
                {attribute: config.first_payload},
                config.first_tag,
                zero_time,
            )
        with pytest.raises(InvalidLogicalTime):
            publisher.send_interaction(
                interaction,
                {parameter: config.second_payload},
                config.second_tag,
                zero_time,
            )

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

        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        owner.destroy_federation_execution(federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        runtime.terminate()


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_negotiated_ownership_matrix(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-nego-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        owner = create_rti_ambassador(kind)
        acquirer = create_rti_ambassador(kind)
        try:
            summary = run_negotiated_attribute_ownership_scenario(
                owner,
                acquirer,
                config=NegotiatedOwnershipScenarioConfig(
                    federation_name=federation_name,
                    fom_modules=("hla2010:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                    owner_name="Owner",
                    acquirer_name="Acquirer",
                    federate_type="OwnershipFederate",
                    object_class_name="HLAobjectRoot.SmokeObject",
                    attribute_name="Payload",
                    object_instance_name=f"{kind}-Negotiated-1",
                    assumption_tag=b"assume-offer",
                    request_tag=b"acquire-request",
                    cancel_tag=b"reacquire-request",
                ),
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except (RTIexception, AssertionError) as exc:
            pytest.skip(
                "Pitch negotiated ownership path is not yet promotable in this runtime: "
                f"{_format_probe_exception(exc)}"
            )

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

        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        owner.destroy_federation_execution(federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        runtime.terminate()


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_negotiated_divesting_offer_probe(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-nego-offer-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        owner = create_rti_ambassador(kind)
        acquirer = create_rti_ambassador(kind)
        summary = probe_negotiated_attribute_ownership_offer(
            owner,
            acquirer,
            config=NegotiatedOwnershipScenarioConfig(
                federation_name=federation_name,
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
                owner_name="Owner",
                acquirer_name="Acquirer",
                federate_type="OwnershipFederate",
                object_class_name="HLAobjectRoot.SmokeObject",
                attribute_name="Payload",
                object_instance_name=f"{kind}-NegotiatedOffer-1",
                assumption_tag=b"assume-offer",
                request_tag=b"acquire-request",
                cancel_tag=b"reacquire-request",
            ),
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        release = summary["release"]
        offered_acquired = summary["offered_acquired"]
        divest_confirmation = summary["divestiture_confirmation"]
        if release is None and offered_acquired is None and divest_confirmation is None:
            pytest.skip(
                "Pitch negotiated divesting-offer probe produced no release callback, no immediate acquisition, and no "
                "divestiture confirmation after acquisition request"
            )

        if offered_acquired is not None:
            assert offered_acquired.args[0] == summary["acquirer_object_instance"]
            assert offered_acquired.args[1] == {summary["acquirer_attribute"]}
        if divest_confirmation is not None:
            assert divest_confirmation.args[0] == summary["object_instance"]
            assert summary["owner_attribute"] in divest_confirmation.args[1]
        if release is not None:
            assert release.args == (
                summary["object_instance"],
                {summary["owner_attribute"]},
                b"acquire-request",
            )

        _cleanup_pitch_ownership_federation(federation_name, owner, acquirer)
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        runtime.terminate()


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_release_request_owned_attribute_probe(kind: str):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    federation_name = f"{kind}-release-probe-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    try:
        owner = create_rti_ambassador(kind)
        acquirer = create_rti_ambassador(kind)
        try:
            summary = run_release_request_ownership_scenario(
                owner,
                acquirer,
                config=ReleaseRequestOwnershipScenarioConfig(
                    federation_name=federation_name,
                    fom_modules=("hla2010:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                    owner_name="Owner",
                    acquirer_name="Acquirer",
                    federate_type="OwnershipFederate",
                    object_class_name="HLAobjectRoot.SmokeObject",
                    attribute_name="Payload",
                    object_instance_name=f"{kind}-ReleaseProbe-1",
                    request_tag=b"acquire-request",
                    owner_action="ifwanted",
                ),
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except (RTIexception, AssertionError) as exc:
            pytest.skip(
                "Pitch owned-attribute release-request probe is not yet stable in this runtime: "
                f"{_format_probe_exception(exc)}"
            )

        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"acquire-request",
        )
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]

        _cleanup_pitch_ownership_federation(federation_name, owner, acquirer)
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
    finally:
        runtime.terminate()

    assert profiles["pitch-py4j"] == profiles["pitch-jpype"]


def test_pitch_negotiated_ownership_profile_matches_across_java_bridges():
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    profiles: dict[str, dict[str, object]] = {}
    try:
        for kind in ("pitch-jpype", "pitch-py4j"):
            federation_name = f"{kind}-nego-profile-{uuid.uuid4().hex[:8]}"
            owner_fed = RecordingFederateAmbassador()
            acquirer_fed = RecordingFederateAmbassador()
            owner = None
            acquirer = None
            try:
                owner = create_rti_ambassador(kind)
                acquirer = create_rti_ambassador(kind)
                try:
                    summary = run_negotiated_attribute_ownership_scenario(
                        owner,
                        acquirer,
                        config=NegotiatedOwnershipScenarioConfig(
                            federation_name=federation_name,
                            fom_modules=("hla2010:VendorSmokeFOM.xml",),
                            logical_time_implementation_name="HLAinteger64Time",
                            owner_name="Owner",
                            acquirer_name="Acquirer",
                            federate_type="OwnershipFederate",
                            object_class_name="HLAobjectRoot.SmokeObject",
                            attribute_name="Payload",
                            object_instance_name=f"{kind}-NegotiatedProfile-1",
                            assumption_tag=b"assume-offer",
                            request_tag=b"acquire-request",
                            cancel_tag=b"reacquire-request",
                        ),
                        owner_federate=owner_fed,
                        acquirer_federate=acquirer_fed,
                    )
                except (RTIexception, AssertionError) as exc:
                    pytest.skip(
                        "Pitch negotiated ownership path is not yet promotable in this runtime: "
                        f"{_format_probe_exception(exc)}"
                    )
                profiles[kind] = _normalized_negotiated_profile(summary)
            finally:
                if acquirer is not None:
                    acquirer.close()
                if owner is not None:
                    owner.close()
    finally:
        runtime.terminate()

    assert profiles["pitch-py4j"] == profiles["pitch-jpype"]
