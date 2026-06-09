"""Runtime profile selection for the two-federate verification suite."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from hla2010.backends.base import BackendUnavailableError

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


def _run_real_profile(kind: str, summary_factory: Any, *, target_radar_steps: int = 4) -> ProfileArtifacts:
    runtime: Any = None
    try:
        if kind in {"pitch-jpype", "pitch-py4j"}:
            from hla2010_rti_pitch_common.testing_policy import launch_pitch_two_federate_profile

            runtime = launch_pitch_two_federate_profile()
        elif kind == "certi":
            from hla2010_rti_certi.testing_policy import prepare_certi_two_federate_profile

            prepare_certi_two_federate_profile()
        elif kind not in {"certi", "pitch-jpype", "pitch-py4j"}:
            raise ValueError(f"Unsupported real profile: {kind}")

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
        profiles.append(_run_real_profile(kind, summary_factory, target_radar_steps=target_radar_steps))
    return profiles


__all__ = ["ProfileArtifacts", "build_profile_artifacts"]
