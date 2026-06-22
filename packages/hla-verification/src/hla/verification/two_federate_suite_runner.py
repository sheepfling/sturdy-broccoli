"""Generic coordinator for the artifact-producing two-federate suite."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .two_federate_suite_pairs import _cleanup_pair
from .two_federate_suite_summary import _callback_rows, _jsonable
from .two_federate_suite_timeline import TimelineRecorder


@dataclass(frozen=True)
class TwoFederateSuiteHooks:
    exchange_config_factory: Callable[[], Any]
    sync_config_factory: Callable[[], Any]
    ownership_config_factory: Callable[[], Any]
    negotiated_config_factory: Callable[[], Any]
    save_restore_config_factory: Callable[[], Mapping[str, Any]]
    ddm_config_factory: Callable[[], Mapping[str, Any]]
    future_exclusion_config_factory: Callable[[], Any]
    restore_state_config_factory: Callable[[], Any]
    run_exchange_scenario: Callable[..., Any]
    assert_exchange_history: Callable[..., Any]
    run_sync_scenario: Callable[..., Any]
    run_ownership_scenario: Callable[..., Any]
    run_negotiated_scenario: Callable[..., Any]
    run_save_restore_scenario: Callable[..., Any]
    run_ddm_scenario: Callable[..., Any]
    run_future_exclusion_scenario: Callable[..., Any]
    run_restore_state_scenario: Callable[..., Any]
    extension_name: str | None = None
    extension_summary_factory: Callable[..., Mapping[str, Any]] | None = None


def run_two_federate_suite_for_pair_factory(
    pair_factory: Any,
    *,
    hooks: TwoFederateSuiteHooks,
    extension_steps: int = 4,
) -> dict[str, Any]:
    timeline = TimelineRecorder(events=[])

    exchange_pub, exchange_sub, exchange_pub_fed, exchange_sub_fed = pair_factory("exchange_time", timeline)
    exchange_config = hooks.exchange_config_factory()
    exchange_summary = hooks.run_exchange_scenario(
        exchange_pub,
        exchange_sub,
        config=exchange_config,
        publisher_federate=exchange_pub_fed,
        subscriber_federate=exchange_sub_fed,
    )
    exchange_history = hooks.assert_exchange_history(
        exchange_summary,
        publisher_federate=exchange_pub_fed,
        subscriber_federate=exchange_sub_fed,
        config=exchange_config,
    )
    _cleanup_pair(exchange_pub, exchange_sub, federation_name=exchange_config.federation_name)

    sync_leader, sync_wing, sync_leader_fed, sync_wing_fed = pair_factory("synchronization", timeline)
    sync_config = hooks.sync_config_factory()
    sync_summary = hooks.run_sync_scenario(
        sync_leader,
        sync_wing,
        config=sync_config,
        leader_federate=sync_leader_fed,
        wing_federate=sync_wing_fed,
    )
    _cleanup_pair(sync_leader, sync_wing, federation_name=sync_config.federation_name)

    owner_rti, acquirer_rti, owner_fed, acquirer_fed = pair_factory("ownership", timeline)
    ownership_config = hooks.ownership_config_factory()
    ownership_summary = hooks.run_ownership_scenario(
        owner_rti,
        acquirer_rti,
        config=ownership_config,
        owner_federate=owner_fed,
        acquirer_federate=acquirer_fed,
    )
    _cleanup_pair(owner_rti, acquirer_rti, federation_name=ownership_config.federation_name)

    neg_owner_rti, neg_acquirer_rti, neg_owner_fed, neg_acquirer_fed = pair_factory("negotiated_ownership", timeline)
    negotiated_config = hooks.negotiated_config_factory()
    negotiated_summary = hooks.run_negotiated_scenario(
        neg_owner_rti,
        neg_acquirer_rti,
        config=negotiated_config,
        owner_federate=neg_owner_fed,
        acquirer_federate=neg_acquirer_fed,
    )
    _cleanup_pair(neg_owner_rti, neg_acquirer_rti, federation_name=negotiated_config.federation_name)

    save_restore_config = hooks.save_restore_config_factory()
    save_pub, save_sub, save_pub_fed, save_sub_fed = pair_factory("save_restore", timeline)
    save_restore_summary = hooks.run_save_restore_scenario(
        save_pub,
        save_sub,
        config=save_restore_config,
        left_federate=save_pub_fed,
        right_federate=save_sub_fed,
    )
    _cleanup_pair(save_pub, save_sub, federation_name=save_restore_config["federation_name"])

    ddm_config = hooks.ddm_config_factory()
    ddm_sender, ddm_receiver, ddm_sender_fed, ddm_receiver_fed = pair_factory("ddm", timeline)
    ddm_summary = hooks.run_ddm_scenario(
        ddm_sender,
        ddm_receiver,
        config=ddm_config,
        sender_federate=ddm_sender_fed,
        receiver_federate=ddm_receiver_fed,
    )
    _cleanup_pair(ddm_sender, ddm_receiver, federation_name=ddm_config["federation_name"])

    future_exclusion_config = hooks.future_exclusion_config_factory()
    future_slow, future_radar, future_slow_fed, future_radar_fed = pair_factory("time_window_future_exclusion", timeline)
    future_exclusion_summary = hooks.run_future_exclusion_scenario(
        future_slow,
        future_radar,
        config=future_exclusion_config,
        slow_federate=future_slow_fed,
        radar_federate=future_radar_fed,
    )
    _cleanup_pair(future_slow, future_radar, federation_name=future_exclusion_config.federation_name)

    restore_state_config = hooks.restore_state_config_factory()
    restore_truth, restore_radar, restore_truth_fed, restore_radar_fed = pair_factory("time_window_restore_state", timeline)
    restore_state_summary = hooks.run_restore_state_scenario(
        restore_truth,
        restore_radar,
        config=restore_state_config,
        truth_federate=restore_truth_fed,
        radar_federate=restore_radar_fed,
    )
    _cleanup_pair(restore_truth, restore_radar, federation_name=restore_state_config.federation_name)

    extension_summary: Mapping[str, Any] | None = None
    if hooks.extension_summary_factory is not None:
        extension_summary = hooks.extension_summary_factory(target_radar_steps=extension_steps)

    scenario_rows = [
        {
            "scenario": "exchange_time",
            "backend": "python/in-memory",
            "callbacks": len(exchange_sub_fed.records) + len(exchange_pub_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "receive + timestamp object and interaction delivery",
        },
        {
            "scenario": "synchronization",
            "backend": "python/in-memory",
            "callbacks": len(sync_leader_fed.records) + len(sync_wing_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "announce and federationSynchronized callbacks",
        },
        {
            "scenario": "ownership",
            "backend": "python/in-memory",
            "callbacks": len(owner_fed.records) + len(acquirer_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "divestiture and acquisition if available",
        },
        {
            "scenario": "negotiated_ownership",
            "backend": "python/in-memory",
            "callbacks": len(neg_owner_fed.records) + len(neg_acquirer_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "release, cancellation, and reacquisition flow",
        },
        {
            "scenario": "save_restore",
            "backend": "python/in-memory",
            "callbacks": len(save_pub_fed.records) + len(save_sub_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "federationSaved and restore callbacks with restored logical time",
        },
        {
            "scenario": "ddm",
            "backend": "python/in-memory",
            "callbacks": len(ddm_receiver_fed.records),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "region-filtered timestamped delivery",
        },
        {
            "scenario": "time_window_future_exclusion",
            "backend": "python/in-memory",
            "callbacks": len(future_slow_fed.records) + len(future_radar_fed.records),
            "artifacts": ["typed summary", "callback timeline", "oracle summary"],
            "key_outcome": "window closure blocked until future input is excluded",
        },
        {
            "scenario": "time_window_restore_state",
            "backend": "python/in-memory",
            "callbacks": len(restore_truth_fed.records) + len(restore_radar_fed.records),
            "artifacts": ["typed summary", "callback timeline", "oracle summary"],
            "key_outcome": "open and closed window state restores across save/restore checkpoints",
        },
    ]
    if extension_summary is not None:
        scenario_rows.append(dict(extension_summary["scenario_row"]))

    callback_rows = (
        _callback_rows("exchange_publisher", exchange_pub_fed.records, scenario="exchange_time")
        + _callback_rows("exchange_subscriber", exchange_sub_fed.records, scenario="exchange_time")
        + _callback_rows("sync_leader", sync_leader_fed.records, scenario="synchronization")
        + _callback_rows("sync_wing", sync_wing_fed.records, scenario="synchronization")
        + _callback_rows("owner", owner_fed.records, scenario="ownership")
        + _callback_rows("acquirer", acquirer_fed.records, scenario="ownership")
        + _callback_rows("neg_owner", neg_owner_fed.records, scenario="negotiated_ownership")
        + _callback_rows("neg_acquirer", neg_acquirer_fed.records, scenario="negotiated_ownership")
        + _callback_rows("left", save_pub_fed.records, scenario="save_restore")
        + _callback_rows("right", save_sub_fed.records, scenario="save_restore")
        + _callback_rows("sender", ddm_sender_fed.records, scenario="ddm")
        + _callback_rows("receiver", ddm_receiver_fed.records, scenario="ddm")
        + _callback_rows("slow", future_slow_fed.records, scenario="time_window_future_exclusion")
        + _callback_rows("radar", future_radar_fed.records, scenario="time_window_future_exclusion")
        + _callback_rows("truth", restore_truth_fed.records, scenario="time_window_restore_state")
        + _callback_rows("radar", restore_radar_fed.records, scenario="time_window_restore_state")
    )

    fom_modules = {"vendor_smoke": str(exchange_config.fom_modules[0])}
    if extension_summary is not None and hooks.extension_name is not None:
        fom_modules[hooks.extension_name] = extension_summary["fom_path"]

    summary = {
        "suite_name": "python-two-federate-suite",
        "suite_version": "0.1",
        "fom_modules": fom_modules,
        "scenario_rows": scenario_rows,
        "exchange": {
            "config": _jsonable(exchange_config),
            "summary": _jsonable(exchange_summary),
            "history": _jsonable(exchange_history),
            "publisher_callback_count": len(exchange_pub_fed.records),
            "subscriber_callback_count": len(exchange_sub_fed.records),
        },
        "synchronization": {
            "config": _jsonable(sync_config),
            "summary": _jsonable(sync_summary),
            "leader_callback_count": len(sync_leader_fed.records),
            "wing_callback_count": len(sync_wing_fed.records),
        },
        "ownership": {
            "config": _jsonable(ownership_config),
            "summary": _jsonable(ownership_summary),
            "owner_callback_count": len(owner_fed.records),
            "acquirer_callback_count": len(acquirer_fed.records),
        },
        "negotiated_ownership": {
            "config": _jsonable(negotiated_config),
            "summary": _jsonable(negotiated_summary),
            "owner_callback_count": len(neg_owner_fed.records),
            "acquirer_callback_count": len(neg_acquirer_fed.records),
        },
        "save_restore": {
            "config": _jsonable(save_restore_config),
            "summary": _jsonable(save_restore_summary),
            "left_callback_count": len(save_pub_fed.records),
            "right_callback_count": len(save_sub_fed.records),
            "left_callbacks": _jsonable(save_pub_fed.records),
            "right_callbacks": _jsonable(save_sub_fed.records),
        },
        "ddm": {
            "config": _jsonable(ddm_config),
            "summary": _jsonable(ddm_summary),
            "sender_callback_count": len(ddm_sender_fed.records),
            "receiver_callback_count": len(ddm_receiver_fed.records),
            "sender_callbacks": _jsonable(ddm_sender_fed.records),
            "receiver_callbacks": _jsonable(ddm_receiver_fed.records),
        },
        "time_window_future_exclusion": {
            "config": _jsonable(future_exclusion_config),
            "summary": _jsonable(future_exclusion_summary),
            "slow_callback_count": len(future_slow_fed.records),
            "radar_callback_count": len(future_radar_fed.records),
            "slow_callbacks": _jsonable(future_slow_fed.records),
            "radar_callbacks": _jsonable(future_radar_fed.records),
        },
        "time_window_restore_state": {
            "config": _jsonable(restore_state_config),
            "summary": _jsonable(restore_state_summary),
            "truth_callback_count": len(restore_truth_fed.records),
            "radar_callback_count": len(restore_radar_fed.records),
            "truth_callbacks": _jsonable(restore_truth_fed.records),
            "radar_callbacks": _jsonable(restore_radar_fed.records),
        },
        "callback_rows": callback_rows,
        "timeline_rows": [_jsonable(event) for event in timeline.events],
    }
    if extension_summary is not None and hooks.extension_name is not None:
        summary[hooks.extension_name] = _jsonable(extension_summary["result"])
    return summary


__all__ = ["TwoFederateSuiteHooks", "run_two_federate_suite_for_pair_factory"]
