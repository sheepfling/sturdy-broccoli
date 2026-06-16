from __future__ import annotations

import os
import uuid

import pytest

from hla.rti1516e.enums import ResignAction
from hla.backends.common import BackendUnavailableError, RecordingFederateAmbassador
from hla.rti1516e.factory import create_rti_ambassador
from hla.verification import (
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from tests.vendors.runtime_support import cleanup_federation, close_all


def _require_portico_runtime_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


@pytest.mark.parametrize("kind", ["portico-jpype", "portico-py4j"])
@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_portico_backend_exchange_matrix(kind: str, time_factory_name: str) -> None:
    _require_portico_runtime_smoke()

    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    federation_name = f"{kind}-matrix-{uuid.uuid4().hex[:8]}"
    try:
        try:
            publisher = create_rti_ambassador(kind)
            subscriber = create_rti_ambassador(kind)
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        config = TwoFederateExchangeConfig(
            federation_name=federation_name,
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name=time_factory_name,
            object_instance_name=f"{kind}-{time_factory_name}-Object-1",
        )
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == config.object_instance_name
        assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
        assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
        assert summary["timed_reflect"].args[1] == {summary["subscriber_attribute"]: config.timestamped_attribute_payload}
        assert summary["timed_interaction"].args[1] == {summary["subscriber_parameter"]: config.timestamped_interaction_payload}

        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[2] == config.attribute_tag
        assert history["timestamp_interaction"].args[2] == config.timestamped_interaction_tag

        cleanup_federation(
            federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )
    finally:
        close_all(subscriber, publisher)


@pytest.mark.parametrize("kind", ["portico-jpype", "portico-py4j"])
def test_portico_backend_synchronization_matrix(kind: str) -> None:
    _require_portico_runtime_smoke()

    leader_fed = RecordingFederateAmbassador()
    wing_fed = RecordingFederateAmbassador()
    leader = None
    wing = None
    federation_name = f"{kind}-sync-{uuid.uuid4().hex[:8]}"
    try:
        try:
            leader = create_rti_ambassador(kind)
            wing = create_rti_ambassador(kind)
        except BackendUnavailableError as exc:
            pytest.skip(str(exc))

        config = SynchronizationScenarioConfig(
            federation_name=federation_name,
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
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

        assert summary["leader_registration"].args == (config.label,)
        assert summary["leader_announce"].args[:2] == (config.label, config.tag)
        assert summary["wing_announce"].args[:2] == (config.label, config.tag)
        assert summary["leader_sync"].args[0] == config.label
        assert summary["wing_sync"].args[0] == config.label

        cleanup_federation(
            federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )
    finally:
        close_all(wing, leader)
