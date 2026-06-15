from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

from hla2010.ambassadors import invoke_federate_callback
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.handles import AttributeHandleValueMap, FederateHandle, ObjectInstanceHandle, TransportationTypeHandle
from hla2010.time import HLAinteger64Time
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


def test_representative_runtime_and_callback_methods_are_owned_explicitly() -> None:
    for owner, method_names in (
        (
            DelegatingRTIAmbassador,
            (
                "timeAdvanceRequest",
                "createFederationExecution",
                "getHLAversion",
            ),
        ),
        (
            RecordingFederateAmbassador,
            (
                "reflect_attribute_values",
                "connection_lost",
                "time_advance_grant",
            ),
        ),
    ):
        for method_name in method_names:
            assert method_name in owner.__dict__
            assert callable(owner.__dict__[method_name])


def test_all_runtime_methods_are_defined_on_delegating_rti_ambassador() -> None:
    for method_name in RTI_METHOD_NAMES:
        assert method_name in DelegatingRTIAmbassador.__dict__


def test_all_callback_methods_are_defined_on_recording_federate_ambassador() -> None:
    for method_name in CALLBACK_METHOD_NAMES:
        snake_name = lower_camel_to_snake(method_name)
        assert snake_name in RecordingFederateAmbassador.__dict__


def test_source_named_method_routes_to_same_backend_invocation() -> None:
    backend = RecordingBackend(results={"timeAdvanceRequest": "ok"})
    rti = make_rti_ambassador(backend)

    assert rti.timeAdvanceRequest("t1") == "ok"
    assert backend.calls[-1].method_name == "timeAdvanceRequest"


def test_typed_snake_case_runtime_alias_routes_to_same_backend_invocation() -> None:
    backend = RecordingBackend(results={"timeAdvanceRequest": None})
    rti = make_rti_ambassador(backend)

    assert rti.time_advance_request(HLAinteger64Time(10)) is None
    assert backend.calls[-1].method_name == "timeAdvanceRequest"
    assert backend.calls[-1].args == (HLAinteger64Time(10),)


def test_typed_snake_case_runtime_aliases_cover_basic_return_and_enum_inputs() -> None:
    backend = RecordingBackend(
        results={
            "connect": None,
            "createFederationExecution": None,
            "destroyFederationExecution": None,
            "disconnect": None,
            "getHLAversion": "HLA 1516.1-2010",
            "joinFederationExecution": FederateHandle(42),
            "resignFederationExecution": None,
        }
    )
    rti = make_rti_ambassador(backend)

    ambassador = RecordingFederateAmbassador()
    assert rti.connect(ambassador, CallbackModel.HLA_IMMEDIATE) is None
    assert backend.calls[-1].method_name == "connect"
    assert backend.calls[-1].args == (ambassador, CallbackModel.HLA_IMMEDIATE)

    assert rti.create_federation_execution(
        "fed",
        ["DemoFOMmodule.xml"],
        logical_time_implementation_name="HLAinteger64Time",
    ) is None
    assert backend.calls[-1].method_name == "createFederationExecution"
    assert backend.calls[-1].args == ("fed", ["DemoFOMmodule.xml"], "HLAinteger64Time")

    assert rti.destroy_federation_execution("fed") is None
    assert backend.calls[-1].method_name == "destroyFederationExecution"
    assert backend.calls[-1].args == ("fed",)

    assert rti.disconnect() is None
    assert backend.calls[-1].method_name == "disconnect"

    assert rti.get_hla_version() == "HLA 1516.1-2010"
    assert backend.calls[-1].method_name == "getHLAversion"

    assert rti.join_federation_execution(
        "observer",
        "fed",
        federate_name="ObserverOne",
        additional_fom_modules=["ExtraFOMmodule.xml"],
    ) == FederateHandle(42)
    assert backend.calls[-1].method_name == "joinFederationExecution"
    assert backend.calls[-1].args == ("ObserverOne", "observer", "fed", ["ExtraFOMmodule.xml"])

    assert rti.resign_federation_execution(ResignAction.NO_ACTION) is None
    assert backend.calls[-1].method_name == "resignFederationExecution"
    assert backend.calls[-1].args == (ResignAction.NO_ACTION,)


def test_callback_recording_routes_without_dunder_magic() -> None:
    ambassador = RecordingFederateAmbassador()

    ambassador.reflectAttributeValues(
        ObjectInstanceHandle(1),
        AttributeHandleValueMap(),
        b"payload",
        OrderType.RECEIVE,
        TransportationTypeHandle(1),
        HLAinteger64Time(0),
    )
    assert ambassador.last_callback() is not None
    assert ambassador.last_callback().method_name == "reflectAttributeValues"
    assert ambassador.last_callback().args[:3] == (ObjectInstanceHandle(1), AttributeHandleValueMap(), b"payload")


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
    assert "| createFederationExecution | create_federation_execution | RTIambassador | DelegatingRTIAmbassador | _invoke | specs/hla2010_api.json |" in text
    assert "| destroyFederationExecution | destroy_federation_execution | RTIambassador | DelegatingRTIAmbassador | _invoke | specs/hla2010_api.json |" in text
    assert "| joinFederationExecution | join_federation_execution | RTIambassador | DelegatingRTIAmbassador | _invoke | specs/hla2010_api.json |" in text
    assert "| timeAdvanceRequest | time_advance_request | RTIambassador | DelegatingRTIAmbassador | _invoke | specs/hla2010_api.json |" in text
    assert "| timeAdvanceGrant | time_advance_grant | FederateAmbassador | RecordingFederateAmbassador | record_callback | specs/hla2010_api.json |" in text
