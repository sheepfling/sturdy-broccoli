"""Runtime profile selection for the two-federate verification suite."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from hla.backends.common import BackendUnavailableError

RuntimeProfileLauncher = Callable[[], Any]

@dataclass
class ProfileArtifacts:
    profile: str
    kind: str
    status: str
    reason: str | None
    scenario_rows: list[dict[str, Any]]
    callback_rows: list[dict[str, Any]]
    timeline_rows: list[dict[str, Any]]
    summary: dict[str, Any]


def _run_real_profile(
    kind: str,
    summary_factory: Any,
    *,
    target_radar_steps: int = 4,
    runtime_launchers: Mapping[str, RuntimeProfileLauncher] | None = None,
) -> ProfileArtifacts:
    runtime: Any = None
    try:
        launcher = (runtime_launchers or {}).get(kind)
        if kind not in {"certi", "pitch-jpype", "pitch-py4j"}:
            raise ValueError(f"Unsupported real profile: {kind}")
        if launcher is None:
            reason = f"No runtime launcher configured for profile {kind}"
            return ProfileArtifacts(
                profile=kind,
                kind=kind,
                status="skipped",
                reason=reason,
                scenario_rows=[],
                callback_rows=[],
                timeline_rows=[],
                summary={"profile": kind, "status": "skipped", "reason": reason},
            )
        runtime = launcher()

        summary = summary_factory(kind, target_radar_steps=target_radar_steps)
        summary["profile"] = kind
        return ProfileArtifacts(
            profile=kind,
            kind=kind,
            status="passed",
            reason=None,
            scenario_rows=list(summary["scenario_rows"]),
            callback_rows=list(summary["callback_rows"]),
            timeline_rows=list(summary["timeline_rows"]),
            summary=summary,
        )
    except BackendUnavailableError as exc:
        reason = str(exc)
        return ProfileArtifacts(
            profile=kind,
            kind=kind,
            status="skipped",
            reason=reason,
            scenario_rows=[],
            callback_rows=[],
            timeline_rows=[],
            summary={"profile": kind, "status": "skipped", "reason": reason},
        )
    except OSError as exc:
        reason = str(exc)
        return ProfileArtifacts(
            profile=kind,
            kind=kind,
            status="skipped",
            reason=reason,
            scenario_rows=[],
            callback_rows=[],
            timeline_rows=[],
            summary={"profile": kind, "status": "skipped", "reason": reason},
        )
    except Exception as exc:
        return ProfileArtifacts(
            profile=kind,
            kind=kind,
            status="failed",
            reason=str(exc),
            scenario_rows=[],
            callback_rows=[],
            timeline_rows=[],
            summary={"profile": kind, "status": "failed", "reason": str(exc)},
        )
    finally:
        if runtime is not None:
            terminate = getattr(runtime, "terminate", None)
            if callable(terminate):
                terminate()


def build_profile_artifacts(
    primary_summary: Mapping[str, Any],
    summary_factory: Any,
    *,
    target_radar_steps: int = 4,
    runtime_launchers: Mapping[str, RuntimeProfileLauncher] | None = None,
) -> list[ProfileArtifacts]:
    profiles = [
        ProfileArtifacts(
            profile="python",
            kind="python",
            status="passed",
            reason=None,
            scenario_rows=list(primary_summary["scenario_rows"]),
            callback_rows=list(primary_summary["callback_rows"]),
            timeline_rows=list(primary_summary["timeline_rows"]),
            summary=dict(primary_summary),
        )
    ]
    for kind in ("certi", "pitch-jpype", "pitch-py4j"):
        profiles.append(
            _run_real_profile(
                kind,
                summary_factory,
                target_radar_steps=target_radar_steps,
                runtime_launchers=runtime_launchers,
            )
        )
    return profiles


__all__ = ["ProfileArtifacts", "RuntimeProfileLauncher", "build_profile_artifacts"]
