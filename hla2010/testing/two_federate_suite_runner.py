"""Artifact-producing two-federate verification suite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..scenarios.target_radar import run_target_radar_scenario
from .scenarios import (
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from .two_federate_suite_configs import (
    _ddm_config,
    _exchange_config,
    _negotiated_config,
    _ownership_config,
    _save_restore_config,
    _sync_config,
)
from .two_federate_suite_pairs import _cleanup_pair, _make_python_pair, _make_real_pair
from .two_federate_suite_profiles import build_profile_artifacts
from .two_federate_suite_scenarios import run_suite_ddm_scenario, run_suite_save_restore_scenario
from .two_federate_suite_summary import _callback_rows, _jsonable
from .two_federate_suite_timeline import TimelineRecorder
from .two_federate_suite_types import SuitePaths
from .two_federate_suite_writers import (
    _write_callbacks_csv,
    _write_json,
    _write_markdown,
    _write_svg,
    _write_timeline_svg,
    _write_track_csv,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = PROJECT_ROOT / "hla2010" / "resources" / "foms"
VENDOR_SMOKE_FOM = RESOURCE_ROOT / "VendorSmokeFOM.xml"
TARGET_RADAR_FOM = RESOURCE_ROOT / "TargetRadarFOMmodule.xml"


def _run_two_federate_suite_for_pair_factory(
    pair_factory: Any,
    *,
    target_radar_steps: int = 4,
) -> dict[str, Any]:
    timeline = TimelineRecorder(events=[])
    exchange_pub, exchange_sub, exchange_pub_fed, exchange_sub_fed = pair_factory("exchange_time", timeline)
    exchange_config = _exchange_config()
    exchange_summary = run_two_federate_exchange_scenario(
        exchange_pub,
        exchange_sub,
        config=exchange_config,
        publisher_federate=exchange_pub_fed,
        subscriber_federate=exchange_sub_fed,
    )
    exchange_history = assert_two_federate_exchange_callback_history(
        exchange_summary,
        publisher_federate=exchange_pub_fed,
        subscriber_federate=exchange_sub_fed,
        config=exchange_config,
    )
    _cleanup_pair(exchange_pub, exchange_sub, federation_name=exchange_config.federation_name)

    sync_leader, sync_wing, sync_leader_fed, sync_wing_fed = pair_factory("synchronization", timeline)
    sync_config = _sync_config()
    sync_summary = run_synchronization_scenario(
        sync_leader,
        sync_wing,
        config=sync_config,
        leader_federate=sync_leader_fed,
        wing_federate=sync_wing_fed,
    )
    _cleanup_pair(sync_leader, sync_wing, federation_name=sync_config.federation_name)

    owner_rti, acquirer_rti, owner_fed, acquirer_fed = pair_factory("ownership", timeline)
    ownership_config = _ownership_config()
    ownership_summary = run_attribute_ownership_scenario(
        owner_rti,
        acquirer_rti,
        config=ownership_config,
        owner_federate=owner_fed,
        acquirer_federate=acquirer_fed,
    )
    _cleanup_pair(owner_rti, acquirer_rti, federation_name=ownership_config.federation_name)

    neg_owner_rti, neg_acquirer_rti, neg_owner_fed, neg_acquirer_fed = pair_factory("negotiated_ownership", timeline)
    negotiated_config = _negotiated_config()
    negotiated_summary = run_negotiated_attribute_ownership_scenario(
        neg_owner_rti,
        neg_acquirer_rti,
        config=negotiated_config,
        owner_federate=neg_owner_fed,
        acquirer_federate=neg_acquirer_fed,
    )
    _cleanup_pair(neg_owner_rti, neg_acquirer_rti, federation_name=negotiated_config.federation_name)

    save_restore_config = _save_restore_config()
    save_pub, save_sub, save_pub_fed, save_sub_fed = pair_factory("save_restore", timeline)
    save_restore_summary = run_suite_save_restore_scenario(
        save_pub,
        save_sub,
        config=save_restore_config,
        left_federate=save_pub_fed,
        right_federate=save_sub_fed,
    )
    _cleanup_pair(save_pub, save_sub, federation_name=save_restore_config["federation_name"])

    ddm_config = _ddm_config()
    ddm_sender, ddm_receiver, ddm_sender_fed, ddm_receiver_fed = pair_factory("ddm", timeline)
    ddm_summary = run_suite_ddm_scenario(
        ddm_sender,
        ddm_receiver,
        config=ddm_config,
        sender_federate=ddm_sender_fed,
        receiver_federate=ddm_receiver_fed,
    )
    _cleanup_pair(ddm_sender, ddm_receiver, federation_name=ddm_config["federation_name"])

    target_radar_result = run_target_radar_scenario(
        federation_name="TwoFederateSuiteTargetRadar",
        steps=target_radar_steps,
        fom_modules=[str(TARGET_RADAR_FOM)],
    )

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
            "scenario": "target_radar",
            "backend": ",".join(target_radar_result.backend_kinds),
            "callbacks": len(target_radar_result.target_events) + len(target_radar_result.radar_events),
            "artifacts": ["track report csv", "svg summary", "scenario event log"],
            "key_outcome": f"{len(target_radar_result.track_reports)} track reports",
        },
    ]

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
    )

    return {
        "suite_name": "python-two-federate-suite",
        "suite_version": "0.1",
        "project_root": str(PROJECT_ROOT),
        "fom_modules": {
            "vendor_smoke": str(VENDOR_SMOKE_FOM),
            "target_radar": str(TARGET_RADAR_FOM),
        },
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
        "target_radar": _jsonable(target_radar_result),
        "callback_rows": callback_rows,
        "timeline_rows": [_jsonable(event) for event in timeline.events],
    }


def run_python_two_federate_suite(*, target_radar_steps: int = 4) -> dict[str, Any]:
    return _run_two_federate_suite_for_pair_factory(_make_python_pair, target_radar_steps=target_radar_steps)


def _run_profile_summary(kind: str, *, target_radar_steps: int = 4) -> dict[str, Any]:
    return _run_two_federate_suite_for_pair_factory(
        lambda scenario, timeline: _make_real_pair(kind, scenario, timeline, profile=kind),
        target_radar_steps=target_radar_steps,
    )


def run_two_federate_suite(*, target_radar_steps: int = 4) -> dict[str, Any]:
    primary_summary = run_python_two_federate_suite(target_radar_steps=target_radar_steps)
    profiles = build_profile_artifacts(
        primary_summary,
        _run_profile_summary,
        target_radar_steps=target_radar_steps,
    )

    return {
        "suite_name": "two-federate-suite",
        "suite_version": "0.2",
        "profiles": [_jsonable(profile) for profile in profiles],
        "primary_profile": "python",
        "scenario_rows": primary_summary["scenario_rows"],
        "exchange": primary_summary["exchange"],
        "synchronization": primary_summary["synchronization"],
        "ownership": primary_summary["ownership"],
        "negotiated_ownership": primary_summary["negotiated_ownership"],
        "save_restore": primary_summary["save_restore"],
        "ddm": primary_summary["ddm"],
        "target_radar": primary_summary["target_radar"],
        "callback_rows": primary_summary["callback_rows"],
        "timeline_rows": primary_summary["timeline_rows"],
    }


def write_two_federate_suite_artifacts(output_dir: Path | str, *, target_radar_steps: int = 4) -> SuitePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = run_two_federate_suite(target_radar_steps=target_radar_steps)
    paths = SuitePaths(
        output_dir=output_path,
        summary_json=output_path / "two_federate_suite_summary.json",
        track_reports_csv=output_path / "two_federate_track_reports.csv",
        callbacks_csv=output_path / "two_federate_callbacks.csv",
        report_markdown=output_path / "two_federate_suite_report.md",
        summary_svg=output_path / "two_federate_suite_summary.svg",
        timeline_svg=output_path / "two_federate_suite_timeline.svg",
    )
    _write_json(paths.summary_json, summary)
    _write_track_csv(paths.track_reports_csv, summary["target_radar"]["track_reports"])
    _write_callbacks_csv(paths.callbacks_csv, summary["callback_rows"])
    _write_markdown(paths.report_markdown, summary, paths)
    _write_svg(paths.summary_svg, summary)
    _write_timeline_svg(paths.timeline_svg, summary)
    return paths


__all__ = [
    "SuitePaths",
    "run_two_federate_suite",
    "run_python_two_federate_suite",
    "write_two_federate_suite_artifacts",
]
