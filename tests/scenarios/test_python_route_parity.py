from __future__ import annotations

import math
import uuid

import pytest

from hla.backends.common import RecordingFederateAmbassador
from hla.foms.target_radar._internal import run_target_radar_scenario
from hla.rti1516e.enums import OrderType, ResignAction
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
from hla.verification import (
    CallbackControlScenarioConfig,
    FederationLifecycleScenarioConfig,
    OwnershipScenarioConfig,
    SaveRestoreScenarioConfig,
    TargetRadarConsumerOrderConfig,
    TargetRadarFutureExclusionConfig,
    TargetRadarOutputDeliveryConfig,
    TargetRadarPipelineConfig,
    TargetRadarPipelineRestoreConfig,
    TargetRadarReceiveOrderPoisonConfig,
    TargetRadarTimeWindowConfig,
    TargetRadarWindowRestoreOutputConfig,
    TargetRadarWindowRestoreConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_callback_control_scenario,
    run_example_fom_save_restore_gauntlet_scenario,
    run_federation_lifecycle_scenario,
    run_smoke_fom_save_restore_ownership_gauntlet_scenario,
    run_target_radar_time_window_consumer_order_scenario,
    run_target_radar_time_window_future_exclusion_scenario,
    run_target_radar_time_window_core_scenario,
    run_target_radar_time_window_output_delivery_scenario,
    run_target_radar_time_window_pipeline_scenario,
    run_target_radar_time_window_pipeline_restore_scenario,
    run_target_radar_time_window_receive_order_poison_scenario,
    run_target_radar_time_window_restore_output_scenario,
    run_target_radar_time_window_restore_state_scenario,
    run_two_federate_exchange_scenario,
)
from tests.scenarios.python_route_parity_support import python_route_params, python_rti_group, python_rti_pair, python_single_rti
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


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_callback_control(route) -> None:
    with python_rti_pair(route) as pair:
        config = CallbackControlScenarioConfig(
            federation_name=f"python-callback-control-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_callback_control_scenario(
            pair.left,
            pair.right,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )

        assert summary["first_queued_while_disabled"] is True
        assert summary["first_evoke"] is False
        assert summary["first_release"] is True
        assert summary["first_delivery"].args[0] == summary["object_instance"]
        assert summary["first_delivery"].args[1] == summary["subscriber_object_class"]
        assert summary["first_delivery"].args[2] == config.object_instance_name
        assert summary["first_reflection"].args[1] == {summary["subscriber_attribute"]: config.first_payload}
        assert summary["first_reflection"].args[2] == config.first_tag
        assert summary["second_batch_queued_while_disabled"] is True
        assert summary["blocked_batch_evoke"] is False
        assert summary["batch_evoke"] is True
        assert summary["drained_tags"] == [config.second_tag, config.third_tag]
        assert summary["drained_payloads"] == [
            {summary["subscriber_attribute"]: config.second_payload},
            {summary["subscriber_attribute"]: config.third_payload},
        ]
        assert summary["post_drain"] is False

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_example_fom_save_restore_gauntlet(route) -> None:
    with python_rti_group(route, 4) as group:
        owner, mirror, sender, observer = group.members
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-restore-gauntlet-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Owner",
            wing_name="Mirror",
            federate_type="SaveRestoreGauntlet",
            save_name=f"SAVE-GAUNTLET-{uuid.uuid4().hex[:8]}",
        )
        owner_federate = RecordingFederateAmbassador()
        mirror_federate = RecordingFederateAmbassador()
        sender_federate = RecordingFederateAmbassador()
        observer_federate = RecordingFederateAmbassador()

        summary = run_example_fom_save_restore_gauntlet_scenario(
            owner,
            mirror,
            sender,
            observer,
            config=config,
            owner_federate=owner_federate,
            mirror_federate=mirror_federate,
            sender_federate=sender_federate,
            observer_federate=observer_federate,
        )

        assert summary["saved_fingerprints"] != summary["dirty_fingerprints"]
        assert summary["restored_fingerprints"] == summary["saved_fingerprints"]
        assert all(float(getattr(time, "value", time)) == 5.0 for time in summary["restored_times"].values())
        assert summary["dirty_remove"].args[1] == b"dirty-delete"
        assert summary["branch_interaction"].args[2] == b"branch-track"

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (mirror, ResignAction.NO_ACTION),
                (sender, ResignAction.NO_ACTION),
                (observer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(observer, sender, mirror, owner),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_smoke_fom_save_restore_ownership_gauntlet(route) -> None:
    with python_rti_group(route, 4) as group:
        owner, mirror, sender, observer = group.members
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-restore-ownership-gauntlet-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Owner",
            wing_name="Mirror",
            federate_type="SaveRestoreGauntlet",
            save_name=f"SAVE-OWNERSHIP-GAUNTLET-{uuid.uuid4().hex[:8]}",
        )
        owner_federate = RecordingFederateAmbassador()
        mirror_federate = RecordingFederateAmbassador()
        sender_federate = RecordingFederateAmbassador()
        observer_federate = RecordingFederateAmbassador()

        summary = run_smoke_fom_save_restore_ownership_gauntlet_scenario(
            owner,
            mirror,
            sender,
            observer,
            config=config,
            owner_federate=owner_federate,
            mirror_federate=mirror_federate,
            sender_federate=sender_federate,
            observer_federate=observer_federate,
        )

        assert summary["saved_fingerprints"] != summary["dirty_fingerprints"]
        assert summary["restored_fingerprints"] == summary["saved_fingerprints"]
        assert all(float(getattr(time, "value", time)) == 5.0 for time in summary["restored_times"].values())
        assert summary["dirty_acquired"].args[0] == summary["mirror_object_instance"]
        assert summary["restored_informed"].args[0] == summary["object_instance"]
        assert summary["branch_interaction"].args[2] == b"branch-message"

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (mirror, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),
                (sender, ResignAction.NO_ACTION),
                (observer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(observer, sender, mirror, owner),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_future_exclusion(route) -> None:
    with python_rti_pair(route) as pair:
        config = TargetRadarFutureExclusionConfig(
            federation_name=f"python-radar-time-window-future-exclusion-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_future_exclusion_scenario(
            pair.left,
            pair.right,
            config=config,
            slow_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
        )

        assert summary["initial_slow_grant"].args[0] == HLAinteger64Time(config.slow_initial_time)
        assert summary["blocked_galt"].time == HLAinteger64Time(config.slow_initial_time + config.slow_lookahead)
        assert summary["blocked_lits"].time == HLAinteger64Time(config.slow_initial_time + config.slow_lookahead)
        assert summary["blocked_grant"] is None
        assert summary["clearance_slow_grant"].args[0] == HLAinteger64Time(config.slow_clearance_time)
        assert summary["cleared_galt"].time == HLAinteger64Time(config.scan_window_end)
        assert summary["cleared_lits"].time == HLAinteger64Time(config.scan_window_end)
        assert summary["final_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["late_send_rejected"] is True
        assert summary["boundary_receive"].args[2] == b"boundary-track-110"
        assert summary["boundary_receive"].args[5] == HLAinteger64Time(config.legal_boundary_time)
        assert summary["certification_target"] == "time-window-future-exclusion"
        assert summary["oracle_report"]["certification_target"] == "time-window-future-exclusion"
        assert summary["oracle_report"]["assertions"] == {
            "radar_not_granted_to_window_end_while_future_input_possible": True,
            "blocked_grant_matches_current_galt_or_none": True,
            "future_input_exclusion_reaches_window_end": True,
            "radar_granted_to_window_end_only_after_future_input_excluded": True,
            "late_timestamp_into_closed_window_rejected": True,
            "boundary_timestamp_delivered_after_window_closure": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_core(route) -> None:
    with python_rti_group(route, 6) as group:
        truth, sensor, radar, consumer, fast, slow = group.members
        config = TargetRadarTimeWindowConfig(
            federation_name=f"python-radar-time-window-core-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_core_scenario(
            truth,
            sensor,
            radar,
            consumer,
            fast,
            slow,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            sensor_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
            fast_federate=RecordingFederateAmbassador(),
            slow_federate=RecordingFederateAmbassador(),
        )

        assert summary["first_grant"].args[0] == HLAinteger64Time(config.truth_update_time)
        assert summary["second_grant"].args[0] == HLAinteger64Time(config.sensor_detection_time)
        assert summary["window_close_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["late_rejections"] == [
            config.scan_window_start,
            config.truth_update_time,
            config.scan_window_end - 1,
        ]
        assert int(getattr(summary["processing_progress"]["fast_time"], "value", 0)) > config.scan_window_end
        assert summary["published_output_time"] == HLAinteger64Time(config.radar_output_time)
        assert summary["published_output_tag"] == b"radar-track-output"
        assert all(timestamp >= config.scan_window_end for timestamp in summary["post_close_inputs"])
        assert summary["certification_target"] == "time-window-core"
        assert summary["oracle_report"]["certification_target"] == "time-window-core"
        assert summary["oracle_report"]["state_model"] == "OPEN -> CLOSABLE -> CLOSED"
        assert summary["oracle_report"]["assertions"] == {
            "pending_timestamped_messages_not_skipped": True,
            "window_not_closed_before_truth_update": True,
            "window_not_closed_before_sensor_update": True,
            "window_closed_only_at_end": True,
            "no_post_close_input_less_than_window_end": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (sensor, ResignAction.NO_ACTION),
                (radar, ResignAction.DELETE_OBJECTS),
                (consumer, ResignAction.NO_ACTION),
                (fast, ResignAction.NO_ACTION),
                (slow, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(slow, fast, consumer, radar, sensor, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_output_delivery(route) -> None:
    with python_rti_group(route, 3) as group:
        truth, radar, consumer = group.members
        config = TargetRadarOutputDeliveryConfig(
            federation_name=f"python-radar-time-window-output-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_output_delivery_scenario(
            truth,
            radar,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        assert summary["window_close_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["consumer_receive"].args[2] == b"radar-track-output"
        assert summary["consumer_receive"].args[5] == HLAinteger64Time(config.radar_output_time)
        assert list(summary["consumer_receive"].args[1].values()) == [config.output_track_id.encode("utf-8")]
        assert len(summary["post_delivery_receives"]) == 1
        assert summary["certification_target"] == "time-window-output-delivery"
        assert summary["oracle_report"]["certification_target"] == "time-window-output-delivery"
        assert summary["oracle_report"]["state_model"] == "OPEN -> CLOSED -> OUTPUT_PUBLISHED -> CONSUMED"
        assert summary["oracle_report"]["assertions"] == {
            "window_closed_before_output": True,
            "output_timestamp_not_before_window_end": True,
            "consumer_received_single_track_output": True,
            "consumer_received_output_at_expected_time": True,
            "output_payload_tied_to_closed_window_inputs": True,
            "no_duplicate_output_after_consumer_readvance": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, radar, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_consumer_order(route) -> None:
    with python_rti_group(route, 4) as group:
        truth, radar, other, consumer = group.members
        config = TargetRadarConsumerOrderConfig(
            federation_name=f"python-radar-time-window-order-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_consumer_order_scenario(
            truth,
            radar,
            other,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            other_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        delivered = [(record.args[2], record.args[5]) for record in summary["consumer_receives"]]
        assert delivered == [
            (b"other-track-output", HLAinteger64Time(config.competing_event_time)),
            (b"radar-track-output", HLAinteger64Time(config.radar_output_time)),
        ]
        assert list(summary["consumer_receives"][0].args[1].values()) == [config.competing_track_id.encode("utf-8")]
        assert list(summary["consumer_receives"][1].args[1].values()) == [config.radar_output_track_id.encode("utf-8")]
        assert len(summary["post_readvance_receives"]) == 2
        assert summary["certification_target"] == "time-window-consumer-order"
        assert summary["oracle_report"]["certification_target"] == "time-window-consumer-order"
        assert summary["oracle_report"]["assertions"] == {
            "consumer_delivery_timestamps_sorted": True,
            "competing_event_arrives_before_radar_output": True,
            "radar_output_timestamp_not_before_window_end": True,
            "consumer_payloads_match_competing_and_radar_sources": True,
            "no_duplicate_consumer_replay_after_readvance": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (other, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, other, radar, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_pipeline(route) -> None:
    with python_rti_group(route, 3) as group:
        truth, radar, consumer = group.members
        config = TargetRadarPipelineConfig(
            federation_name=f"python-radar-time-window-pipeline-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_pipeline_scenario(
            truth,
            radar,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        delivered = [(record.args[2], record.args[5]) for record in summary["consumer_receives"]]
        assert delivered == [
            (b"scan1-track-output", HLAinteger64Time(config.scan1_output_time)),
            (b"scan2-track-output", HLAinteger64Time(config.scan2_output_time)),
        ]
        assert list(summary["consumer_receives"][0].args[1].values()) == [config.scan1_track_id.encode("utf-8")]
        assert list(summary["consumer_receives"][1].args[1].values()) == [config.scan2_track_id.encode("utf-8")]
        assert len(summary["post_readvance_receives"]) == 2
        assert summary["scan1_close_grant"].args[0] == HLAinteger64Time(config.scan1_end)
        assert summary["scan2_close_grant"].args[0] == HLAinteger64Time(config.scan2_end)
        assert summary["scan2_reflect"].args[2] == b"scan2-input"
        assert summary["certification_target"] == "time-window-pipeline-two-scans"
        assert summary["oracle_report"]["certification_target"] == "time-window-pipeline-two-scans"
        assert summary["oracle_report"]["assertions"] == {
            "scan1_closes_before_scan2_input": True,
            "scan2_input_collected_while_scan1_output_pending": True,
            "scan1_output_precedes_scan2_output": True,
            "no_cross_window_contamination": True,
            "scan_outputs_tied_to_their_own_window_inputs": True,
            "no_duplicate_pipeline_replay_after_readvance": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, radar, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_pipeline_restore(route) -> None:
    with python_rti_group(route, 3) as group:
        truth, radar, consumer = group.members
        config = TargetRadarPipelineRestoreConfig(
            federation_name=f"python-radar-time-window-pipeline-restore-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_pipeline_restore_scenario(
            truth,
            radar,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        assert summary["saved_radar_time"] == HLAinteger64Time(config.scan2_input_time)
        assert summary["saved_consumer_time"] == HLAinteger64Time(config.scan1_end)
        assert [record.args[2] for record in summary["dirty_consumer_receives"]] == [
            b"dirty-scan1-track-output",
            b"dirty-scan2-track-output",
        ]
        assert summary["restored_radar_time"] == HLAinteger64Time(config.scan2_input_time)
        assert summary["restored_consumer_time"] == HLAinteger64Time(config.scan1_end)
        assert summary["post_restore_scan2_reflects"] == []
        assert [record.args[2] for record in summary["restored_consumer_receives"]] == [
            b"restored-scan1-track-output",
            b"restored-scan2-track-output",
        ]
        assert list(summary["restored_consumer_receives"][0].args[1].values()) == [
            config.restored_scan1_track_id.encode("utf-8")
        ]
        assert list(summary["restored_consumer_receives"][1].args[1].values()) == [
            config.restored_scan2_track_id.encode("utf-8")
        ]
        assert len(summary["post_restore_duplicate_receives"]) == 2
        assert summary["certification_target"] == "time-window-save-restore-pipeline-resume"
        assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-pipeline-resume"
        assert summary["oracle_report"]["assertions"] == {
            "restore_reinstates_saved_radar_time": True,
            "restore_reinstates_saved_consumer_time": True,
            "dirty_pipeline_outputs_do_not_replay": True,
            "scan2_collected_state_restored_without_reflection_replay": True,
            "restored_outputs_match_saved_window_inputs": True,
            "no_duplicate_restored_pipeline_outputs_after_readvance": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, radar, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_receive_order_poison(route) -> None:
    with python_rti_group(route, 3) as group:
        truth, radar, consumer = group.members
        config = TargetRadarReceiveOrderPoisonConfig(
            federation_name=f"python-radar-time-window-receive-order-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_receive_order_poison_scenario(
            truth,
            radar,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        assert summary["window_close_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["closed_window_tags_before"] == [b"truth-105", b"truth-106"]
        assert summary["closed_window_tags_after"] == [b"truth-105", b"truth-106"]
        assert summary["poison_reflection"].args[2] == b"receive-order-poison"
        if len(summary["poison_reflection"].args) > 8:
            assert summary["poison_reflection"].args[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)
        assert summary["consumer_receive"].args[2] == b"radar-track-output"
        assert summary["consumer_receive"].args[5] == HLAinteger64Time(config.radar_output_time)
        assert summary["certification_target"] == "time-window-receive-order-poison"
        assert summary["oracle_report"]["certification_target"] == "time-window-receive-order-poison"
        assert summary["oracle_report"]["assertions"] == {
            "closed_window_tags_unchanged_after_receive_order_poison": True,
            "poison_reflection_has_no_timestamp": True,
            "poison_reflection_is_receive_order": True,
            "consumer_output_still_delivered_at_expected_time": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, radar, truth),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_restore_state(route) -> None:
    with python_rti_pair(route) as pair:
        config = TargetRadarWindowRestoreConfig(
            federation_name=f"python-radar-time-window-restore-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_restore_state_scenario(
            pair.left,
            pair.right,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
        )

        assert summary["first_grant"].args[0] == HLAinteger64Time(config.first_input_time)
        assert summary["dirty_close_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["open_restored_truth_time"] == HLAinteger64Time(config.first_input_time)
        assert summary["open_restored_radar_time"] == HLAinteger64Time(config.first_input_time)
        assert summary["reclosed_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["closed_restored_truth_time"] == HLAinteger64Time(config.scan_window_end)
        assert summary["closed_restored_radar_time"] == HLAinteger64Time(config.scan_window_end)
        assert summary["post_closed_restore_reflects"] == []
        assert summary["saved_open_state"]["window_closed"] is False
        assert summary["restored_open_state"]["window_closed"] is False
        assert summary["saved_closed_state"]["window_closed"] is True
        assert summary["restored_closed_state"]["window_closed"] is True
        assert summary["dirty_post_close_reflect"].args[2] == b"dirty-post-close"
        assert summary["certification_target"] == "time-window-save-restore-window-state"
        assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-window-state"
        assert summary["oracle_report"]["assertions"] == {
            "open_restore_reinstates_preclosure_time": True,
            "open_restore_reinstates_open_window_state": True,
            "restored_open_branch_recloses_at_window_end": True,
            "closed_restore_reinstates_window_end_time": True,
            "closed_restore_reinstates_closed_window_state": True,
            "closed_restore_discards_dirty_post_close_callbacks": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar_time_window_restore_output(route) -> None:
    with python_rti_group(route, 3) as group:
        truth, radar, consumer = group.members
        config = TargetRadarWindowRestoreOutputConfig(
            federation_name=f"python-radar-time-window-restore-output-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
        )
        summary = run_target_radar_time_window_restore_output_scenario(
            truth,
            radar,
            consumer,
            config=config,
            truth_federate=RecordingFederateAmbassador(),
            radar_federate=RecordingFederateAmbassador(),
            consumer_federate=RecordingFederateAmbassador(),
        )

        assert summary["window_close_grant"].args[0] == HLAinteger64Time(config.scan_window_end)
        assert summary["saved_consumer_time"] == HLAinteger64Time(config.scan_window_end)
        assert summary["dirty_consumer_receive"].args[2] == b"dirty-track-output"
        assert summary["dirty_consumer_receive"].args[5] == HLAinteger64Time(config.radar_output_time)
        assert summary["restored_truth_time"] == HLAinteger64Time(config.scan_window_end)
        assert summary["restored_radar_time"] == HLAinteger64Time(config.scan_window_end)
        assert summary["restored_consumer_time"] == HLAinteger64Time(config.scan_window_end)
        assert [record.args[2] for record in summary["post_restore_receives"]] == [b"restored-track-output"]
        assert summary["restored_consumer_receive"].args[5] == HLAinteger64Time(config.radar_output_time)
        assert summary["certification_target"] == "time-window-save-restore-output-resume"
        assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-output-resume"
        assert summary["oracle_report"]["assertions"] == {
            "closed_window_saved_before_output": True,
            "dirty_branch_output_published_before_restore": True,
            "restored_timeline_republishes_legal_output": True,
            "dirty_output_not_replayed_after_restore": True,
            "single_post_restore_output_delivery": True,
        }

        cleanup_federation(
            config.federation_name,
            destroyer=truth,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=(
                (radar, ResignAction.NO_ACTION),
                (consumer, ResignAction.NO_ACTION),
            ),
            disconnect_rtis=(consumer, radar, truth),
        )
