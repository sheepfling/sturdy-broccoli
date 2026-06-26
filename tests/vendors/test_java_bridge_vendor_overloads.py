from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import pytest

from hla.backends.common import BackendUnavailableError, RecordingFederateAmbassador
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.runtime.factory import create_rti_ambassador
from hla.verification import (
    RequestAttributeValueUpdateScenarioConfig,
    run_request_attribute_value_update_routing_scenario,
)
from hla.vendors.pitch.real_rti_pitch import launch_pitch_runtime
from tests.vendors.runtime_support import cleanup_federation, require_vendor_preflight, shutdown_runtime_resources


@dataclass(frozen=True)
class CapturedJavaCall:
    method_name: str
    arg_kinds: tuple[str, ...]


def _require_real_vendor_runtime(kind: str) -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    if kind.startswith("pitch-"):
        require_vendor_preflight("pitch", operator_hint="./tools/pitch preflight")


@contextmanager
def _vendor_runtime_case(kind: str, ambassador_count: int) -> Iterator[tuple[Any, ...]]:
    _require_real_vendor_runtime(kind)
    runtime = None
    rtis: list[Any | None] = [None] * ambassador_count
    try:
        if kind.startswith("pitch-"):
            runtime = launch_pitch_runtime()
        for index in range(ambassador_count):
            rtis[index] = create_rti_ambassador(kind)
        yield tuple(rtis)
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))
    finally:
        shutdown_runtime_resources(close_resources=tuple(rtis), runtime_resources=((runtime,) if runtime is not None else ()))


def _classify_bridge_arg(bridge: Any, value: Any) -> str:
    full_name = bridge.full_class_name(value)
    if full_name:
        return full_name
    if isinstance(value, str):
        return "python:str"
    if isinstance(value, bytes):
        return "python:bytes"
    if isinstance(value, bytearray):
        return "python:bytearray"
    if isinstance(value, (list, tuple)):
        return f"python:{type(value).__name__}"
    return f"python:{type(value).__name__}"


@contextmanager
def _capture_java_bridge_calls(rti: Any) -> Iterator[list[CapturedJavaCall]]:
    backend = rti.backend
    bridge = backend.bridge
    original_call = bridge.call
    calls: list[CapturedJavaCall] = []

    def recording_call(obj: Any, method_name: str, *args: Any) -> Any:
        calls.append(
            CapturedJavaCall(
                method_name=method_name,
                arg_kinds=tuple(_classify_bridge_arg(bridge, arg) for arg in args),
            )
        )
        return original_call(obj, method_name, *args)

    bridge.call = recording_call
    try:
        yield calls
    finally:
        bridge.call = original_call


def _captured_call(calls: list[CapturedJavaCall], method_name: str, *, ordinal: int = 0) -> CapturedJavaCall:
    matches = [call for call in calls if call.method_name == method_name]
    assert len(matches) > ordinal, f"missing captured call {method_name}[{ordinal}] in {matches!r}"
    return matches[ordinal]


def _is_stringish(kind: str) -> bool:
    return kind in {"python:str", "java.lang.String"}


def _is_url_arrayish(kind: str) -> bool:
    return kind in {"[Ljava.net.URL;", "java.net.URL[]"}


def _is_handle_kind(kind: str, suffix: str) -> bool:
    return kind.endswith(suffix) or kind.endswith(f".{suffix}")


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j", "portico-jpype", "portico-py4j"])
def test_real_vendor_backend_create_and_join_overload_shapes(kind: str) -> None:
    federation_name = f"{kind}-overload-create-join-{uuid.uuid4().hex[:8]}"
    federate_name = f"Overload-{uuid.uuid4().hex[:6]}"
    federate = RecordingFederateAmbassador()
    rti = None
    try:
        with _vendor_runtime_case(kind, 1) as (rti,):
            with _capture_java_bridge_calls(rti) as calls:
                rti.connect(federate, CallbackModel.HLA_EVOKED)
                rti.create_federation_execution(
                    federation_name,
                    ["resource:VendorSmokeFOM.xml"],
                    "HLAinteger64Time",
                )
                rti.join_federation_execution(federate_name, "OverloadFederate", federation_name)

            create_call = _captured_call(calls, "createFederationExecution")
            join_call = _captured_call(calls, "joinFederationExecution")

            assert len(create_call.arg_kinds) == 3
            assert _is_stringish(create_call.arg_kinds[0])
            assert _is_url_arrayish(create_call.arg_kinds[1])
            assert _is_stringish(create_call.arg_kinds[2])

            assert join_call.arg_kinds == ("python:str", "python:str", "python:str") or all(
                _is_stringish(kind_name) for kind_name in join_call.arg_kinds
            )

            cleanup_federation(
                federation_name,
                destroyer=rti,
                destroyer_resign_action=ResignAction.NO_ACTION,
                disconnect_rtis=(rti,),
            )
    finally:
        if rti is not None:
            try:
                rti.close()
            except BaseException:
                pass


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j", "portico-jpype", "portico-py4j"])
def test_real_vendor_backend_request_attribute_value_update_overload_shapes(kind: str) -> None:
    config = RequestAttributeValueUpdateScenarioConfig(
        federation_name=f"{kind}-request-update-overloads-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"RequestUpdate-{uuid.uuid4().hex[:8]}",
    )
    owner_a_federate = RecordingFederateAmbassador()
    owner_b_federate = RecordingFederateAmbassador()
    requester_federate = RecordingFederateAmbassador()
    owner_a = None
    owner_b = None
    requester = None
    try:
        with _vendor_runtime_case(kind, 3) as (owner_a, owner_b, requester):
            with _capture_java_bridge_calls(requester) as calls:
                run_request_attribute_value_update_routing_scenario(
                    owner_a,
                    owner_b,
                    requester,
                    config=config,
                    owner_a_federate=owner_a_federate,
                    owner_b_federate=owner_b_federate,
                    requester_federate=requester_federate,
                )

            object_request = _captured_call(calls, "requestAttributeValueUpdate", ordinal=0)
            class_request = _captured_call(calls, "requestAttributeValueUpdate", ordinal=1)

            assert len(object_request.arg_kinds) == 3
            assert len(class_request.arg_kinds) == 3
            assert _is_handle_kind(object_request.arg_kinds[0], "ObjectInstanceHandle")
            assert _is_handle_kind(class_request.arg_kinds[0], "ObjectClassHandle")
            assert object_request.arg_kinds[1] == class_request.arg_kinds[1]
            assert object_request.arg_kinds[2] == class_request.arg_kinds[2]

            cleanup_federation(
                config.federation_name,
                destroyer=owner_a,
                destroyer_resign_action=ResignAction.DELETE_OBJECTS,
                remaining_resignations=(
                    (owner_b, ResignAction.NO_ACTION),
                    (requester, ResignAction.NO_ACTION),
                ),
                disconnect_rtis=(requester, owner_b, owner_a),
            )
    finally:
        for rti in (requester, owner_b, owner_a):
            if rti is None:
                continue
            try:
                rti.close()
            except BaseException:
                pass
