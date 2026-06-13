from __future__ import annotations

import pytest

from hla2010_rti_java_common.java_common import invoke_java_rti_method


class _RecordingJavaRTI:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def _record(self, name: str, *args: object) -> str:
        self.calls.append((name, args))
        return name

    def connect(self, *args: object) -> str:
        return self._record("connect", *args)

    def createFederationExecution(self, *args: object) -> str:  # noqa: N802
        return self._record("createFederationExecution", *args)

    def timeAdvanceRequest(self, *args: object) -> str:  # noqa: N802
        return self._record("timeAdvanceRequest", *args)


def test_invoke_java_rti_method_routes_to_explicit_method() -> None:
    rti = _RecordingJavaRTI()

    assert invoke_java_rti_method(rti, "connect", "fed-amb", "HLA_EVOKED") == "connect"
    assert invoke_java_rti_method(rti, "createFederationExecution", "fed", "demo.xml") == "createFederationExecution"
    assert invoke_java_rti_method(rti, "timeAdvanceRequest", 3.0) == "timeAdvanceRequest"

    assert rti.calls == [
        ("connect", ("fed-amb", "HLA_EVOKED")),
        ("createFederationExecution", ("fed", "demo.xml")),
        ("timeAdvanceRequest", (3.0,)),
    ]


def test_invoke_java_rti_method_rejects_unknown_service_name() -> None:
    with pytest.raises(AttributeError, match="totallyUnknownMethod"):
        invoke_java_rti_method(_RecordingJavaRTI(), "totallyUnknownMethod")
