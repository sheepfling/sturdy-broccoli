from __future__ import annotations

import inspect
from typing import Any

from hla2010.spec_inventory import RTIAMBASSADOR_METHODS
from hla2010_rti_certi.certi_java.adapter import CERTIJavaRTIShim
from hla2010_rti_java_common.java_shim_types import JavaByteArray


class _RecordingRTI:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def timeAdvanceRequest(self, *args: Any) -> bytes:  # noqa: N802
        self.calls.append(("timeAdvanceRequest", args))
        return b"grant"

    def createFederationExecution(self, *args: Any) -> str:  # noqa: N802
        self.calls.append(("createFederationExecution", args))
        return "created"

    def getHLAversion(self) -> str:  # noqa: N802
        self.calls.append(("getHLAversion", ()))
        return "HLA 1516.1-2010"


def _make_shim(rti: Any) -> CERTIJavaRTIShim:
    shim = object.__new__(CERTIJavaRTIShim)
    shim.profile = "jpype"
    shim.config = None
    shim._rti = rti
    shim._java_proxy = None
    return shim


def test_certi_java_shim_representative_methods_are_explicit() -> None:
    assert "def timeAdvanceRequest" in inspect.getsource(CERTIJavaRTIShim.timeAdvanceRequest)
    assert "def createFederationExecution" in inspect.getsource(CERTIJavaRTIShim.createFederationExecution)
    assert "def getHLAversion" in inspect.getsource(CERTIJavaRTIShim.getHLAversion)


def test_certi_java_shim_defines_all_rti_methods_explicitly() -> None:
    missing = sorted(name for name in RTIAMBASSADOR_METHODS if name not in CERTIJavaRTIShim.__dict__)
    assert not missing, "\n".join(missing)


def test_certi_java_shim_time_advance_request_forwards_with_java_conversion() -> None:
    rti = _RecordingRTI()
    shim = _make_shim(rti)

    result = shim.timeAdvanceRequest(JavaByteArray(b"tag"))

    assert isinstance(result, JavaByteArray)
    assert bytes(result) == b"grant"
    assert rti.calls == [("timeAdvanceRequest", (b"tag",))]


def test_certi_java_shim_create_federation_execution_forwards_explicitly() -> None:
    rti = _RecordingRTI()
    shim = _make_shim(rti)

    assert shim.createFederationExecution("demo-fed", ["fom.xml"]) == "created"
    assert rti.calls == [("createFederationExecution", ("demo-fed", ["fom.xml"]))]
