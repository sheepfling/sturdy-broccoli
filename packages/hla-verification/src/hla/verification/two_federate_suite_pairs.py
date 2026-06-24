"""Pair construction helpers for the two-federate verification suite."""
from __future__ import annotations

from importlib import import_module
from typing import Any

from hla.rti1516e.enums import ResignAction
from hla.rti1516e.handles import ObjectClassHandle, ObjectInstanceHandle
from hla.backends.common import RecordingFederateAmbassador
from hla.rti import create_rti_ambassador
from hla.verification.two_federate_suite_timeline import TimelineRecorder


class SuiteRecordingFederateAmbassador(RecordingFederateAmbassador):
    """Recorder that normalizes callback shapes used by the suite helpers."""

    def __init__(
        self,
        *,
        profile: str = "python",
        scenario: str = "suite",
        role: str = "federate",
        timeline: TimelineRecorder | None = None,
    ) -> None:
        super().__init__()
        self.profile = profile
        self.scenario = scenario
        self.role = role
        self.timeline = timeline

    def discoverObjectInstance(
        self,
        the_object: ObjectInstanceHandle,
        the_object_class: ObjectClassHandle,
        object_name: str,
        *extra: Any,
    ) -> Any:
        return self.record_callback("discoverObjectInstance", the_object, the_object_class, object_name)

    def record_callback(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        result = super().record_callback(method_name, *args, **kwargs)
        if self.timeline is not None and self.records:
            self.timeline.record(
                profile=self.profile,
                scenario=self.scenario,
                role=self.role,
                callback=self.records[-1],
            )
        return result


def _python_pair():
    return import_module("hla.backends.python1516e").create_python_pair()


def _cleanup_pair(*rtis: Any, federation_name: str) -> None:
    for rti in rtis:
        try:
            rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            try:
                rti.resign_federation_execution(ResignAction.DELETE_OBJECTS)
            except Exception:
                pass
    try:
        rtis[0].destroy_federation_execution(federation_name)
    except Exception:
        pass
    for rti in rtis:
        try:
            rti.disconnect()
        except Exception:
            pass
        close = getattr(rti, "close", None)
        if callable(close):
            close()


def _make_python_pair(
    scenario: str,
    timeline: TimelineRecorder | None = None,
    *,
    profile: str = "python",
) -> tuple[Any, Any, SuiteRecordingFederateAmbassador, SuiteRecordingFederateAmbassador]:
    left_fed = SuiteRecordingFederateAmbassador(profile=profile, scenario=scenario, role="left", timeline=timeline)
    right_fed = SuiteRecordingFederateAmbassador(profile=profile, scenario=scenario, role="right", timeline=timeline)
    left_rti, right_rti = _python_pair()
    return (
        left_rti,
        right_rti,
        left_fed,
        right_fed,
    )


def _make_real_pair(
    kind: str,
    scenario: str,
    timeline: TimelineRecorder | None = None,
    *,
    profile: str,
    **options: Any,
) -> tuple[Any, Any, SuiteRecordingFederateAmbassador, SuiteRecordingFederateAmbassador]:
    left_fed = SuiteRecordingFederateAmbassador(profile=profile, scenario=scenario, role="left", timeline=timeline)
    right_fed = SuiteRecordingFederateAmbassador(profile=profile, scenario=scenario, role="right", timeline=timeline)
    return (
        create_rti_ambassador(kind, **options),
        create_rti_ambassador(kind, **options),
        left_fed,
        right_fed,
    )


__all__ = [
    "SuiteRecordingFederateAmbassador",
    "_cleanup_pair",
    "_make_python_pair",
    "_make_real_pair",
]
