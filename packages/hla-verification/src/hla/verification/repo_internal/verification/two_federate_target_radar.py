"""Target/Radar-owned helpers for the two-federate verification suite."""

from __future__ import annotations

from typing import Any

from hla.rti1516e.time import HLAfloat64Time
from hla.rti1516e.datatypes import RangeBounds
from hla.foms.target_radar.scenarios import target_radar_fom_path
from hla.foms.target_radar.scenarios.target_radar import run_target_radar_scenario


def build_two_federate_target_radar_summary(*, target_radar_steps: int = 4) -> dict[str, Any]:
    result = run_target_radar_scenario(
        federation_name="TwoFederateSuiteTargetRadar",
        steps=target_radar_steps,
        fom_modules=[target_radar_fom_path()],
    )
    return {
        "scenario_row": {
            "scenario": "target_radar",
            "backend": ",".join(result.backend_kinds),
            "callbacks": len(result.target_events) + len(result.radar_events),
            "artifacts": ["track report csv", "svg summary", "scenario event log"],
            "key_outcome": f"{len(result.track_reports)} track reports",
        },
        "result": result,
        "fom_path": target_radar_fom_path(),
    }


def build_two_federate_target_radar_ddm_config() -> dict[str, Any]:
    return {
        "federation_name": "TwoFederateSuiteDDM",
        "fom_modules": (target_radar_fom_path(),),
        "logical_time_implementation_name": "HLAfloat64Time",
        "interaction_class_name": "HLAinteractionRoot.TrackReport",
        "parameter_name": "TrackId",
        "source_near": RangeBounds(0, 10),
        "source_far": RangeBounds(90, 100),
        "target_bounds": RangeBounds(5, 15),
        "far_payload": b"far",
        "near_payload": b"near",
        "far_tag": b"far",
        "near_tag": b"near",
        "far_time": HLAfloat64Time(2.0),
        "near_time": HLAfloat64Time(3.0),
        "grant_time": HLAfloat64Time(5.0),
        "next_request_time": HLAfloat64Time(6.0),
    }


__all__ = [
    "build_two_federate_target_radar_ddm_config",
    "build_two_federate_target_radar_summary",
]
