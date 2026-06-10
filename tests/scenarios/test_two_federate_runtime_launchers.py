from __future__ import annotations

from hla2010_repo_internal.verification.two_federate_runtime_launchers import (
    build_two_federate_runtime_launchers,
)
from hla2010_repo_internal.verification import workspace_two_federate_suite as facade_runner


def test_two_federate_runtime_launcher_registry_exposes_vendor_profiles() -> None:
    launchers = build_two_federate_runtime_launchers()

    assert launchers["certi"].__name__ == "prepare_certi_two_federate_profile"
    assert launchers["pitch-jpype"].__name__ == "launch_pitch_two_federate_profile"
    assert launchers["pitch-py4j"].__name__ == "launch_pitch_two_federate_profile"


def test_workspace_two_federate_suite_injects_repo_launchers(monkeypatch) -> None:
    sentinel_launchers = {
        "certi": lambda: object(),
        "pitch-jpype": lambda: object(),
        "pitch-py4j": lambda: object(),
    }
    seen: dict[str, object] = {}

    def fake_build_two_federate_runtime_launchers():
        return sentinel_launchers

    def fake_run_two_federate_suite(*, target_radar_steps: int, runtime_launchers):
        seen["target_radar_steps"] = target_radar_steps
        seen["runtime_launchers"] = runtime_launchers
        return {"suite_name": "two-federate-suite"}

    monkeypatch.setattr(
        facade_runner,
        "build_two_federate_runtime_launchers",
        fake_build_two_federate_runtime_launchers,
    )
    monkeypatch.setattr(
        facade_runner,
        "run_two_federate_suite",
        fake_run_two_federate_suite,
    )

    summary = facade_runner.run_workspace_two_federate_suite(target_radar_steps=6)

    assert summary["suite_name"] == "two-federate-suite"
    assert seen["target_radar_steps"] == 6
    assert seen["runtime_launchers"] is sentinel_launchers
