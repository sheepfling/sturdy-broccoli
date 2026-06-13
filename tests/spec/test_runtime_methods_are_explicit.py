from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

from hla2010.ambassadors import invoke_federate_callback
from hla2010_rti_backend_common import (
    CALLBACK_METHOD_NAMES,
    DelegatingRTIAmbassador,
    RecordingBackend,
    RecordingFederateAmbassador,
    RTI_METHOD_NAMES,
    lower_camel_to_snake,
    make_rti_ambassador,
)


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_METHOD_INDEX_PATH = ROOT / "analysis" / "traceability" / "runtime_method_index.md"


def test_delegating_rti_ambassador_is_concrete_without_abc_patch() -> None:
    assert not inspect.isabstract(DelegatingRTIAmbassador)


def test_representative_camelcase_methods_are_explicit() -> None:
    assert "def timeAdvanceRequest" in inspect.getsource(DelegatingRTIAmbassador.timeAdvanceRequest)
    assert "def createFederationExecution" in inspect.getsource(DelegatingRTIAmbassador.createFederationExecution)
    assert "def getHLAversion" in inspect.getsource(DelegatingRTIAmbassador.getHLAversion)


def test_representative_snake_case_methods_are_explicit() -> None:
    assert "def time_advance_request" in inspect.getsource(DelegatingRTIAmbassador.time_advance_request)
    assert "def create_federation_execution" in inspect.getsource(DelegatingRTIAmbassador.create_federation_execution)
    assert "def get_hla_version" in inspect.getsource(DelegatingRTIAmbassador.get_hla_version)


def test_representative_callback_methods_are_explicit() -> None:
    assert "def reflect_attribute_values" in inspect.getsource(RecordingFederateAmbassador.reflect_attribute_values)
    assert "def connection_lost" in inspect.getsource(RecordingFederateAmbassador.connection_lost)
    assert "def time_advance_grant" in inspect.getsource(RecordingFederateAmbassador.time_advance_grant)


def test_all_runtime_methods_are_defined_on_delegating_rti_ambassador() -> None:
    for method_name in RTI_METHOD_NAMES:
        snake_name = lower_camel_to_snake(method_name)
        assert method_name in DelegatingRTIAmbassador.__dict__
        if snake_name != method_name:
            assert snake_name in DelegatingRTIAmbassador.__dict__


def test_all_callback_methods_are_defined_on_recording_federate_ambassador() -> None:
    for method_name in CALLBACK_METHOD_NAMES:
        snake_name = lower_camel_to_snake(method_name)
        assert snake_name in RecordingFederateAmbassador.__dict__


def test_snake_case_alias_routes_to_same_backend_invocation() -> None:
    backend = RecordingBackend(results={"timeAdvanceRequest": "ok"})
    rti = make_rti_ambassador(backend)

    assert rti.time_advance_request("t1") == "ok"
    assert backend.calls[-1].method_name == "timeAdvanceRequest"


def test_camelcase_method_routes_to_same_backend_invocation() -> None:
    backend = RecordingBackend(results={"timeAdvanceRequest": "ok"})
    rti = make_rti_ambassador(backend)

    assert rti.timeAdvanceRequest("t1") == "ok"
    assert backend.calls[-1].method_name == "timeAdvanceRequest"


def test_callback_recording_routes_without_dunder_magic() -> None:
    ambassador = RecordingFederateAmbassador()

    ambassador.reflectAttributeValues("payload")
    assert ambassador.last_callback() is not None
    assert ambassador.last_callback().method_name == "reflectAttributeValues"
    assert ambassador.last_callback().args == ("payload",)


def test_shared_callback_invoker_routes_to_explicit_callback_method() -> None:
    ambassador = RecordingFederateAmbassador()

    invoke_federate_callback(ambassador, "timeAdvanceGrant", "grant")

    assert ambassador.last_callback() is not None
    assert ambassador.last_callback().method_name == "timeAdvanceGrant"
    assert ambassador.last_callback().args == ("grant",)


def test_runtime_method_index_is_current() -> None:
    result = subprocess.run(
        ["python3", "scripts/generate_runtime_method_index.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    text = RUNTIME_METHOD_INDEX_PATH.read_text(encoding="utf-8")
    assert "| timeAdvanceRequest | time_advance_request | RTIambassador | DelegatingRTIAmbassador | _invoke | specs/hla2010_api.json |" in text
    assert "| timeAdvanceGrant | time_advance_grant | FederateAmbassador | RecordingFederateAmbassador | record_callback | specs/hla2010_api.json |" in text
