"""Target/Radar-owned composite two-federate verification suite."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from hla2010_verification_harness.scenario_exchange import (
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
)
from hla2010_verification_harness.scenario_ownership import (
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
)
from hla2010_verification_harness.scenario_sync import run_synchronization_scenario
from hla2010_verification_harness.two_federate_suite_configs import (
    _exchange_config,
    _negotiated_config,
    _ownership_config,
    _save_restore_config,
    _sync_config,
)
from hla2010_verification_harness.two_federate_suite_pairs import _make_python_pair, _make_real_pair
from hla2010_verification_harness.two_federate_suite_runner import (
    TwoFederateSuiteHooks,
    run_two_federate_suite_for_pair_factory,
)
from hla2010_verification_harness.two_federate_suite_scenarios import (
    run_suite_ddm_scenario,
    run_suite_save_restore_scenario,
)
from hla2010_verification_harness.two_federate_suite_summary import _jsonable
from hla2010_verification_harness.two_federate_suite_types import SuitePaths
from hla2010_verification_harness.two_federate_suite_writers import (
    _write_callbacks_csv,
    _write_json,
    _write_markdown,
    _write_svg,
    _write_timeline_svg,
)

from .two_federate_suite_profiles import RuntimeProfileLauncher, build_profile_artifacts
from .two_federate_target_radar import (
    build_two_federate_target_radar_ddm_config,
    build_two_federate_target_radar_summary,
)
from .two_federate_target_radar_artifacts import (
    build_two_federate_target_radar_artifact_summary,
    write_two_federate_target_radar_track_csv,
)


def _ddm_config() -> dict[str, object]:
    return build_two_federate_target_radar_ddm_config()


_SUITE_HOOKS = TwoFederateSuiteHooks(
    exchange_config_factory=_exchange_config,
    sync_config_factory=_sync_config,
    ownership_config_factory=_ownership_config,
    negotiated_config_factory=_negotiated_config,
    save_restore_config_factory=_save_restore_config,
    ddm_config_factory=_ddm_config,
    run_exchange_scenario=run_two_federate_exchange_scenario,
    assert_exchange_history=assert_two_federate_exchange_callback_history,
    run_sync_scenario=run_synchronization_scenario,
    run_ownership_scenario=run_attribute_ownership_scenario,
    run_negotiated_scenario=run_negotiated_attribute_ownership_scenario,
    run_save_restore_scenario=run_suite_save_restore_scenario,
    run_ddm_scenario=run_suite_ddm_scenario,
    extension_name="target_radar",
    extension_summary_factory=build_two_federate_target_radar_summary,
)


def run_python_two_federate_suite(*, target_radar_steps: int = 4) -> dict[str, Any]:
    return run_two_federate_suite_for_pair_factory(
        _make_python_pair,
        hooks=_SUITE_HOOKS,
        extension_steps=target_radar_steps,
    )


def _run_profile_summary(kind: str, *, target_radar_steps: int = 4) -> dict[str, Any]:
    return run_two_federate_suite_for_pair_factory(
        lambda scenario, timeline: _make_real_pair(kind, scenario, timeline, profile=kind),
        hooks=_SUITE_HOOKS,
        extension_steps=target_radar_steps,
    )


def run_two_federate_suite(
    *,
    target_radar_steps: int = 4,
    runtime_launchers: Mapping[str, RuntimeProfileLauncher] | None = None,
) -> dict[str, Any]:
    primary_summary = run_python_two_federate_suite(target_radar_steps=target_radar_steps)
    profiles = build_profile_artifacts(
        primary_summary,
        _run_profile_summary,
        target_radar_steps=target_radar_steps,
        runtime_launchers=runtime_launchers,
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


def write_two_federate_suite_artifacts(
    output_dir: Path | str,
    *,
    target_radar_steps: int = 4,
    runtime_launchers: Mapping[str, RuntimeProfileLauncher] | None = None,
) -> SuitePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = run_two_federate_suite(target_radar_steps=target_radar_steps, runtime_launchers=runtime_launchers)
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
    write_two_federate_target_radar_track_csv(paths.track_reports_csv, summary["target_radar"]["track_reports"])
    _write_callbacks_csv(paths.callbacks_csv, summary["callback_rows"])
    artifact_summary = build_two_federate_target_radar_artifact_summary(summary)
    _write_markdown(paths.report_markdown, summary, paths, artifact_summary=artifact_summary)
    _write_svg(paths.summary_svg, summary, artifact_summary=artifact_summary)
    _write_timeline_svg(paths.timeline_svg, summary)
    return paths


__all__ = [
    "SuitePaths",
    "run_two_federate_suite",
    "run_python_two_federate_suite",
    "write_two_federate_suite_artifacts",
]
