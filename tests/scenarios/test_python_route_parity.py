from __future__ import annotations

import math
import uuid

import pytest

from hla.backends.common import RecordingFederateAmbassador
from hla.foms.target_radar.scenarios import run_target_radar_scenario
from hla.rti1516e.enums import OrderType, ResignAction
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
from hla.verification import (
    FederationLifecycleScenarioConfig,
    OwnershipScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_federation_lifecycle_scenario,
    run_two_federate_exchange_scenario,
)
from tests.scenarios.python_route_parity_support import python_route_params, python_rti_pair, python_single_rti
from tests.vendors.runtime_support import cleanup_federation


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar(route) -> None:
    with python_rti_pair(route) as pair:
        result = run_target_radar_scenario(
            lambda role: pair.left if role == "target" else pair.right,
            federation_name=f"target-radar-{route}-{uuid.uuid4().hex[:8]}",
            steps=3,
        )

    assert len(result.track_reports) == 3
    assert any(name == "provide_attribute_value_update" for name, _ in result.target_events)
    assert [name for name, _ in result.radar_events].count("track") == 3
    first = result.track_reports[0]
    assert first.target_name == "Target-1"
    assert math.isclose(first.range_m, math.sqrt(10_250.0**2 + 1_030.0**2 + 2_000.0**2))
    assert first.rcs_square_meters == 12.5
    assert result.track_reports[-1].range_m > result.track_reports[0].range_m


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_federation_lifecycle(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-lifecycle-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_federation_lifecycle_scenario(
            rti,
            config=config,
            federate=RecordingFederateAmbassador(),
        )

        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_object_exchange(route) -> None:
    with python_rti_pair(route) as pair:
        publisher_fed = RecordingFederateAmbassador()
        subscriber_fed = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name=f"python-exchange-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            interaction_class_name="HLAinteractionRoot.SmokeInteraction",
            parameter_name="Message",
            object_instance_name=f"python-object-{uuid.uuid4().hex[:8]}",
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

        summary = run_two_federate_exchange_scenario(
            pair.left,
            pair.right,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == config.object_instance_name
        assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-r"}
        assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-r"}
        assert summary["remove"] is not None
        assert summary["remove"].args[1] == config.delete_tag

        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ownership(route) -> None:
    with python_rti_pair(route) as pair:
        config = OwnershipScenarioConfig(
            federation_name=f"python-ownership-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-owned-{uuid.uuid4().hex[:8]}",
        )

        summary = run_attribute_ownership_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
        )

        assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]
        assert summary["informed_federate_name"] == config.acquirer_name

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )

