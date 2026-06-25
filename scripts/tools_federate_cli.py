#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import shlex
import sys
import time
import tomllib
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOL_LABEL = "./tools/federate-cli"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.backends.common import CALLBACK_METHOD_NAMES, lower_camel_to_snake
from hla.fom.proto2025 import scenario_fom_paths
from hla.runtime.factory import create_rti_ambassador as create_2010_rti_ambassador
from hla.runtime.rti1516_2025_factory import create_hla_factory as create_2025_hla_factory
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_2025_rti_ambassador


EXTRA_CALLBACK_METHOD_NAMES = (
    "receiveDirectedInteraction",
    "hasProducingFederate",
    "getProducingFederate",
    "hasSentRegions",
    "getSentRegions",
)
RECORDABLE_CALLBACK_METHOD_NAMES = CALLBACK_METHOD_NAMES + EXTRA_CALLBACK_METHOD_NAMES
RECORDABLE_CALLBACK_BY_SNAKE = {
    lower_camel_to_snake(method_name): method_name
    for method_name in RECORDABLE_CALLBACK_METHOD_NAMES
}


@dataclass(slots=True)
class CallbackRecord:
    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    @property
    def snake_name(self) -> str:
        return lower_camel_to_snake(self.method_name)


@dataclass(frozen=True, slots=True)
class WalkthroughStep:
    title: str
    summary: str
    command: str | None = None


@dataclass(slots=True)
class SessionConfig:
    edition: str
    backend: str
    federation_name: str
    federate_name: str
    federate_type: str
    fom_modules: tuple[str, ...]
    logical_time_implementation: str
    transport_kind: str | None = None
    transport_target: str | None = None
    json_output: bool = False


@dataclass(slots=True)
class SessionState:
    connected: bool = False
    federation_created: bool = False
    joined: bool = False
    active_federation_name: str | None = None
    joined_federate_name: str | None = None
    joined_federate_type: str | None = None
    federate_handle: Any = None
    validation_status: str | None = None
    validation_issues: tuple[Any, ...] = ()
    validation_diagnostics: tuple[str, ...] = ()
    object_instances: dict[str, Any] = field(default_factory=dict)
    object_instance_classes: dict[str, str] = field(default_factory=dict)
    published_object_classes: dict[str, tuple[str, ...]] = field(default_factory=dict)
    subscribed_object_classes: dict[str, tuple[str, ...]] = field(default_factory=dict)
    published_interaction_classes: tuple[str, ...] = ()
    subscribed_interaction_classes: tuple[str, ...] = ()
    command_history: list[str] = field(default_factory=list)
    walkthrough_name: str | None = None
    walkthrough_step_index: int = 0
    walkthrough_last_note: str | None = None
    tui_focus_title: str | None = None
    tui_focus_text: str | None = None
    tui_help_visible: bool = False
    tui_walkthrough_menu_visible: bool = False


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "name") and hasattr(value, "kind"):
        return {"name": value.name, "kind": value.kind, "version": getattr(value, "version", None)}
    if hasattr(value, "value"):
        return {"type": value.__class__.__name__, "value": value.value}
    if hasattr(value, "name"):
        return value.name
    return repr(value)


def _null_ambassador_class(edition: str) -> type[Any]:
    if edition == "2025":
        module = importlib.import_module("hla.rti1516_2025.federate_ambassador")
    else:
        module = importlib.import_module("hla.rti1516e.federate_ambassador")
    return getattr(module, "NullFederateAmbassador")


def _callback_model(edition: str) -> Any:
    if edition == "2025":
        module = importlib.import_module("hla.rti1516_2025.enums")
    else:
        module = importlib.import_module("hla.rti1516e.enums")
    return getattr(module, "CallbackModel").HLA_EVOKED


def _resign_action(edition: str, action_name: str = "NO_ACTION") -> Any:
    if edition == "2025":
        module = importlib.import_module("hla.rti1516_2025.enums")
    else:
        module = importlib.import_module("hla.rti1516e.enums")
    return getattr(module, "ResignAction")[action_name]


def _recording_ambassador_class(edition: str) -> type[Any]:
    base_cls = _null_ambassador_class(edition)

    class InteractiveRecordingFederateAmbassador(base_cls):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            self.records: list[CallbackRecord] = []

        def record_callback(self, method_name: str, *args: Any, **kwargs: Any) -> None:
            self.records.append(CallbackRecord(method_name=method_name, args=tuple(args), kwargs=dict(kwargs)))

        def clear(self) -> None:
            self.records.clear()

        def __getattribute__(self, name: str) -> Any:
            attr = super().__getattribute__(name)
            if name in {"records", "record_callback", "clear", "__class__"}:
                return attr
            method_name = name if name in RECORDABLE_CALLBACK_METHOD_NAMES else RECORDABLE_CALLBACK_BY_SNAKE.get(name)
            if method_name is None:
                return attr
            owner_attr = getattr(type(self), name, None)
            base_attr = getattr(base_cls, name, None)
            if owner_attr is not None and owner_attr is not base_attr:
                return attr
            return lambda *args, **kwargs: self.record_callback(method_name, *args, **kwargs)

    InteractiveRecordingFederateAmbassador.__name__ = f"InteractiveRecordingFederateAmbassador{edition}"
    return InteractiveRecordingFederateAmbassador


for _method_name in RECORDABLE_CALLBACK_METHOD_NAMES:
    def _recording_callback(method_name: str):
        def _callback(self: Any, *args: Any, **kwargs: Any) -> None:
            self.record_callback(method_name, *args, **kwargs)

        _callback.__name__ = method_name
        return _callback

    # The methods are injected per-instance subclass creation above.
    # Keeping the closure helper here avoids a second helper object at runtime.


def _call_surface(target: Any, *names: str, **kwargs: Any) -> Any:
    args = kwargs.pop("_args", ())
    for name in names:
        method = getattr(target, name, None)
        if callable(method):
            return method(*args, **kwargs)
    joined = " / ".join(name for name in names if name)
    raise AttributeError(f"{target!r} does not expose any of: {joined}")


def _walkthrough_definitions(config: SessionConfig) -> dict[str, tuple[WalkthroughStep, ...]]:
    message_test_object = "HLAobjectRoot.Proto2025.MessageTest.VerificationStatus"
    message_test_interaction = "HLAinteractionRoot.Proto2025.MessageTest.VerificationResult"
    walkthroughs: dict[str, tuple[WalkthroughStep, ...]] = {}
    if config.edition == "2010":
        walkthroughs["lifecycle-2010"] = (
            WalkthroughStep(
                title="Connect",
                summary="Connect a 2010 federate shell to the selected backend.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Federation",
                summary="Create the federation so later join and publish steps have a runtime target.",
                command="create $federation",
            ),
            WalkthroughStep(
                title="Join Federation",
                summary="Join as the configured federate so the session can inspect and drive runtime state.",
                command="join $federate_name $federate_type $federation",
            ),
            WalkthroughStep(
                title="Inspect Session",
                summary="Review the session state after the basic 2010 lifecycle is active.",
                command="status",
            ),
        )
    if config.edition == "2025":
        walkthroughs["message-test-tour"] = (
            WalkthroughStep(
                title="Connect",
                summary="Connect the 2025 shell to the configured backend and prepare the RTI surface.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Federation",
                summary="Create the 2025 federation and load the packaged MessageTest FOM scenario.",
                command="create $federation --fom-scenario message-test",
            ),
            WalkthroughStep(
                title="Inspect Object Class",
                summary="Inspect the verification-status object class before publishing it.",
                command=f"inspect-class {message_test_object}",
            ),
            WalkthroughStep(
                title="Inspect Interaction Class",
                summary="Inspect the verification-result interaction before sending it.",
                command=f"inspect-interaction {message_test_interaction}",
            ),
            WalkthroughStep(
                title="Inspect Datatype",
                summary="Inspect the verdict datatype before values move across the RTI surface.",
                command="inspect-datatype Proto2025Verdict",
            ),
            WalkthroughStep(
                title="Join Federation",
                summary="Join the federation so publications and updates can be issued.",
                command="join $federate_name analysis $federation",
            ),
            WalkthroughStep(
                title="Publish Object",
                summary="Publish the verification-status object attributes used in the demo lane.",
                command=(
                    f"publish-object {message_test_object} "
                    "TestCaseId,StepId,Verdict,Reason,ExpectedValueJson,ActualValueJson,CheckedLogicalTime"
                ),
            ),
            WalkthroughStep(
                title="Register Object",
                summary="Register one object instance that the walkthrough can update incrementally.",
                command=f"register-object {message_test_object} verdict-1",
            ),
            WalkthroughStep(
                title="Pause",
                summary="Pause here to let a learner inspect state before the update is sent.",
                command="pause Review status or callbacks before continuing.",
            ),
            WalkthroughStep(
                title="Update Object",
                summary="Send an object update so the object lane is visible in state and callbacks.",
                command=(
                    "update-object verdict-1 "
                    "TestCaseId=case-1 StepId=step-1 Verdict=PASS Reason=ready "
                    "ExpectedValueJson=expected ActualValueJson=actual CheckedLogicalTime=1"
                ),
            ),
            WalkthroughStep(
                title="Publish Interaction",
                summary="Publish the matching verification-result interaction class.",
                command=f"publish-interaction {message_test_interaction}",
            ),
            WalkthroughStep(
                title="Pause",
                summary="Pause again before emitting the interaction to discuss parameter mapping.",
                command="pause Inspect the interaction shape, then continue to send it.",
            ),
            WalkthroughStep(
                title="Send Interaction",
                summary="Send one verification-result interaction through the active session.",
                command=(
                    f"send-interaction {message_test_interaction} "
                    "TestCaseId=case-1 StepId=step-1 Verdict=PASS Reason=ready EvidenceArtifactId=evidence-1"
                ),
            ),
            WalkthroughStep(
                title="Evoke Callbacks",
                summary="Pump callbacks explicitly so the learner can see when callback delivery occurs.",
                command="evoke 0 0",
            ),
            WalkthroughStep(
                title="Inspect Session",
                summary="Review final state, publications, object instances, and callback count.",
                command="status",
            ),
        )
        walkthroughs["two-federate-callback-tour"] = (
            WalkthroughStep(
                title="Connect Sender Shell",
                summary="Connect the primary shell that will publish and send events.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Federation",
                summary="Create the federation and load the MessageTest scenario once from the sender side.",
                command="create $federation --fom-scenario message-test",
            ),
            WalkthroughStep(
                title="Prepare Receiver Peer",
                summary="Create a managed peer federate that will subscribe and later pump callbacks.",
                command="@peer-ensure sink SinkFederate observer",
            ),
            WalkthroughStep(
                title="Join Receiver Peer",
                summary="Join the receiver peer into the already-created federation without recreating it.",
                command="@peer-join sink SinkFederate observer $federation",
            ),
            WalkthroughStep(
                title="Receiver Subscribes Object",
                summary="Subscribe the receiver to the object attributes so discovery and reflection can occur.",
                command=(
                    f"@peer-subscribe-object sink {message_test_object} "
                    "TestCaseId,StepId,Verdict,Reason,ExpectedValueJson,ActualValueJson,CheckedLogicalTime"
                ),
            ),
            WalkthroughStep(
                title="Receiver Subscribes Interaction",
                summary="Subscribe the receiver to the interaction class before any send occurs.",
                command=f"@peer-subscribe-interaction sink {message_test_interaction}",
            ),
            WalkthroughStep(
                title="Join Sender",
                summary="Join the sender federate so publish and send services are available.",
                command="join $federate_name analysis $federation",
            ),
            WalkthroughStep(
                title="Publish Object",
                summary="Publish the object attributes from the sender side.",
                command=(
                    f"publish-object {message_test_object} "
                    "TestCaseId,StepId,Verdict,Reason,ExpectedValueJson,ActualValueJson,CheckedLogicalTime"
                ),
            ),
            WalkthroughStep(
                title="Publish Interaction",
                summary="Publish the interaction class from the sender side.",
                command=f"publish-interaction {message_test_interaction}",
            ),
            WalkthroughStep(
                title="Register Object",
                summary="Register an object instance that the receiver should discover.",
                command=f"register-object {message_test_object} verdict-2",
            ),
            WalkthroughStep(
                title="Update Object",
                summary="Send one attribute update so the receiver can later reflect it.",
                command=(
                    "update-object verdict-2 "
                    "TestCaseId=case-2 StepId=step-2 Verdict=PASS Reason=peer-demo "
                    "ExpectedValueJson=expected ActualValueJson=actual CheckedLogicalTime=2"
                ),
            ),
            WalkthroughStep(
                title="Send Interaction",
                summary="Send one interaction that should arrive at the receiver peer.",
                command=(
                    f"send-interaction {message_test_interaction} "
                    "TestCaseId=case-2 StepId=step-2 Verdict=PASS Reason=peer-demo EvidenceArtifactId=evidence-2"
                ),
            ),
            WalkthroughStep(
                title="Pump Receiver Callbacks",
                summary="Explicitly evoke callbacks on the receiver so discovery, reflection, and interaction delivery become visible.",
                command="@peer-evoke sink 0 0",
            ),
            WalkthroughStep(
                title="Inspect Receiver Callbacks",
                summary="Review the receiver callback log to confirm the delivered object and interaction effects.",
                command="@peer-callbacks sink 10",
            ),
            WalkthroughStep(
                title="Inspect Receiver Status",
                summary="Inspect the receiver peer state after the callback pump.",
                command="@peer-status sink",
            ),
        )
        walkthroughs["route-variation-tour"] = (
            WalkthroughStep(
                title="Connect Direct Route",
                summary="Connect the direct in-process Python 2025 route.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Direct Federation",
                summary="Create the direct-route federation with the packaged MessageTest FOM.",
                command="create $federation --fom-scenario message-test",
            ),
            WalkthroughStep(
                title="Join Direct Route",
                summary="Join the direct route so its runtime surface is active.",
                command="join $federate_name analysis $federation",
            ),
            WalkthroughStep(
                title="Inspect Direct Route",
                summary="Inspect direct-route status before introducing a hosted transport.",
                command="status",
            ),
            WalkthroughStep(
                title="Prepare Hosted gRPC Route",
                summary="Start a managed Python 2025 gRPC server and create a hosted route session.",
                command="@route-ensure hosted grpc",
            ),
            WalkthroughStep(
                title="Connect Hosted Route",
                summary="Connect the hosted route over gRPC using the same backend family.",
                command="@route-connect hosted",
            ),
            WalkthroughStep(
                title="Create Hosted Federation",
                summary="Create a separate hosted-route federation using the same FOM scenario.",
                command="@route-create hosted $federation_hosted --fom-scenario message-test",
            ),
            WalkthroughStep(
                title="Join Hosted Route",
                summary="Join the hosted route so the shell can compare direct and hosted status side by side.",
                command="@route-join hosted HostedRouteFederate analysis $federation_hosted",
            ),
            WalkthroughStep(
                title="Inspect Hosted Route",
                summary="Inspect hosted-route status and note the gRPC transport target in the session payload.",
                command="@route-status hosted",
            ),
            WalkthroughStep(
                title="Pause",
                summary="Pause here to compare direct in-process state against the hosted transport state.",
                command="pause Compare direct backend_info and hosted transport target before continuing.",
            ),
            WalkthroughStep(
                title="Inspect Shared Object Shape",
                summary="Inspect the same object class to reinforce that the route changes, not the FOM shape.",
                command=f"inspect-class {message_test_object}",
            ),
            WalkthroughStep(
                title="Inspect Direct Route Again",
                summary="Return to direct-route status so the learner can compare both route summaries in one dashboard.",
                command="status",
            ),
        )
        walkthroughs["adapter-boundary-tour"] = (
            WalkthroughStep(
                title="Connect Direct Route",
                summary="Connect the direct 2025 route so the baseline runtime lane is visible.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Federation",
                summary="Create the baseline federation for the direct route.",
                command="create $federation --fom-scenario message-test",
            ),
            WalkthroughStep(
                title="Join Direct Route",
                summary="Join the direct route so backend and route state are populated.",
                command="join $federate_name analysis $federation",
            ),
            WalkthroughStep(
                title="Inspect Hosted FedPro Adapter",
                summary="Inspect the maintained 2025 FedPro adapter boundary where hosted command fields and callback decoding are owned.",
                command="inspect-adapter grpc-fedpro-2025",
            ),
            WalkthroughStep(
                title="Inspect Quirky Vendor Adapter",
                summary="Inspect the thin vendor-variant gRPC scaffold that isolates a slightly different envelope shape without changing RTI semantics.",
                command="inspect-adapter grpc-quirky-vendor",
            ),
            WalkthroughStep(
                title="Prepare Hosted Route",
                summary="Stand up the managed hosted gRPC route that uses the normal FedPro adapter lane.",
                command="@route-ensure hosted grpc",
            ),
            WalkthroughStep(
                title="Connect Hosted Route",
                summary="Connect the hosted route so the learner can compare the operational path against the adapter profile surfaces.",
                command="@route-connect hosted",
            ),
            WalkthroughStep(
                title="Inspect Hosted Route Status",
                summary="Inspect hosted-route status and note that the transport target is the operational concern while the adapter file owns payload conventions.",
                command="@route-status hosted",
            ),
            WalkthroughStep(
                title="Pause",
                summary="Pause here to explain that a new vendor dialect should usually fork the wire adapter, not the RTI semantics above it.",
                command="pause Compare adapter profiles against hosted route status before continuing.",
            ),
            WalkthroughStep(
                title="Inspect Session",
                summary="Return to session status so the route and adapter boundary story stays together in one view.",
                command="status",
            ),
        )
    if config.edition == "2010":
        walkthroughs["transport-substitution-tour"] = (
            WalkthroughStep(
                title="Connect Direct 2010 Route",
                summary="Connect the direct in-process 2010 Python route as the baseline surface.",
                command="connect",
            ),
            WalkthroughStep(
                title="Create Direct Federation",
                summary="Create the direct-route federation with the standard demo FOM.",
                command="create $federation",
            ),
            WalkthroughStep(
                title="Join Direct Route",
                summary="Join the direct route so its baseline session state is visible.",
                command="join $federate_name analysis $federation",
            ),
            WalkthroughStep(
                title="Prepare Hosted gRPC Route",
                summary="Start a managed Python-backed gRPC transport server and wrap it through the 2010 transport client lane.",
                command="@route-ensure hosted-grpc grpc",
            ),
            WalkthroughStep(
                title="Connect Hosted gRPC Route",
                summary="Connect the hosted gRPC route through the transport-backed 2010 adapter surface.",
                command="@route-connect hosted-grpc",
            ),
            WalkthroughStep(
                title="Create Hosted gRPC Federation",
                summary="Create a dedicated hosted-gRPC federation for direct comparison.",
                command="@route-create hosted-grpc $federation-hosted-grpc",
            ),
            WalkthroughStep(
                title="Join Hosted gRPC Route",
                summary="Join the hosted gRPC route and inspect the target-based transport metadata.",
                command="@route-join hosted-grpc HostedGrpcFederate analysis $federation-hosted-grpc",
            ),
            WalkthroughStep(
                title="Inspect Hosted gRPC Route",
                summary="Capture the hosted gRPC route status before standing up the REST variant.",
                command="@route-status hosted-grpc",
            ),
            WalkthroughStep(
                title="Prepare Hosted REST Route",
                summary="Start a managed Python-backed REST transport server using the same 2010 backend family.",
                command="@route-ensure hosted-rest rest",
            ),
            WalkthroughStep(
                title="Connect Hosted REST Route",
                summary="Connect the hosted REST route through the same transport-backed client shape.",
                command="@route-connect hosted-rest",
            ),
            WalkthroughStep(
                title="Create Hosted REST Federation",
                summary="Create a dedicated hosted-REST federation for side-by-side comparison.",
                command="@route-create hosted-rest $federation-hosted-rest",
            ),
            WalkthroughStep(
                title="Join Hosted REST Route",
                summary="Join the hosted REST route and inspect the base-url transport metadata.",
                command="@route-join hosted-rest HostedRestFederate analysis $federation-hosted-rest",
            ),
            WalkthroughStep(
                title="Inspect Hosted REST Route",
                summary="Inspect the hosted REST route and compare it against the hosted gRPC route.",
                command="@route-status hosted-rest",
            ),
            WalkthroughStep(
                title="Pause",
                summary="Pause here to compare `target` versus `base_url` transport configuration and explain the substitution pattern.",
                command="pause Compare hosted-grpc target metadata against hosted-rest base_url metadata.",
            ),
            WalkthroughStep(
                title="Inspect Direct Route Again",
                summary="Return to the direct route so the learner can compare all three route summaries in one place.",
                command="status",
            ),
        )
    return walkthroughs


def _walkthrough_shortcuts(config: SessionConfig) -> dict[str, str]:
    shortcuts: dict[str, str] = {}
    if config.edition == "2010":
        shortcuts.update(
            {
                "l": "lifecycle-2010",
                "t": "transport-substitution-tour",
            }
        )
    if config.edition == "2025":
        shortcuts.update(
            {
                "m": "message-test-tour",
                "c": "two-federate-callback-tour",
                "r": "route-variation-tour",
                "a": "adapter-boundary-tour",
            }
        )
    return shortcuts


def _install_recording_methods(callback_cls: type[Any], base_cls: type[Any]) -> None:
    for method_name in RECORDABLE_CALLBACK_METHOD_NAMES:
        snake_name = lower_camel_to_snake(method_name)
        callback = _recording_callback(method_name)
        setattr(callback_cls, method_name, callback)
        setattr(callback_cls, snake_name, callback)
        if not hasattr(base_cls, method_name):
            continue


@dataclass(slots=True)
class InteractiveFederateSession:
    config: SessionConfig
    state: SessionState = field(default_factory=SessionState)
    rti: Any = None
    callbacks: Any = None
    callback_class: type[Any] | None = None
    fom_catalog: Any = None
    fom_resolved_modules: tuple[Any, ...] = ()
    walkthrough_steps: tuple[WalkthroughStep, ...] = ()
    peer_sessions: dict[str, "InteractiveFederateSession"] = field(default_factory=dict)
    route_sessions: dict[str, "InteractiveFederateSession"] = field(default_factory=dict)
    managed_servers: dict[str, Any] = field(default_factory=dict)

    def _transport_options(self) -> dict[str, Any]:
        if not self.config.transport_kind:
            return {}
        transport: dict[str, Any] = {"kind": self.config.transport_kind}
        if self.config.transport_target:
            if self.config.transport_kind == "rest":
                transport["base_url"] = self.config.transport_target
            else:
                transport["target"] = self.config.transport_target
        return {"transport": transport}

    def _create_rti(self) -> Any:
        options = self._transport_options()
        if self.config.edition == "2025":
            return create_2025_rti_ambassador(backend=self.config.backend, **options)
        return create_2010_rti_ambassador(backend=self.config.backend, **options)

    def _ensure_callbacks(self) -> Any:
        if self.callbacks is not None:
            return self.callbacks
        base_cls = _null_ambassador_class(self.config.edition)
        callback_cls = _recording_ambassador_class(self.config.edition)
        _install_recording_methods(callback_cls, base_cls)
        self.callback_class = callback_cls
        self.callbacks = callback_cls()
        return self.callbacks

    def _resolve_fom_modules(self, override_modules: tuple[str, ...] = (), override_scenario: str | None = None) -> tuple[str, ...]:
        if override_modules:
            return override_modules
        if self.config.edition == "2025":
            scenario_name = override_scenario or "message-test"
            return tuple(str(path) for path in scenario_fom_paths(scenario_name))
        if self.config.fom_modules:
            return self.config.fom_modules
        return ("DemoFOMmodule.xml",)

    def _validate_2025_fom(self, modules: tuple[str, ...]) -> None:
        if self.config.edition != "2025":
            return
        result = create_2025_hla_factory(provider=self.config.backend).load_fom(modules)
        self.state.validation_status = result.status
        self.state.validation_issues = tuple(result.validation_issues)
        self.state.validation_diagnostics = tuple(result.diagnostics)

    def _load_fom_catalog(self, modules: tuple[str, ...]) -> None:
        fom = importlib.import_module("hla.fom")
        resolved = fom.FOMResolver().resolve_many(tuple(modules))
        self.fom_resolved_modules = tuple(resolved)
        self.fom_catalog = fom.merge_fom_modules(resolved)

    def _ensure_fom_catalog(self) -> Any | None:
        if self.fom_catalog is not None:
            return self.fom_catalog
        modules = self._resolve_fom_modules()
        try:
            self._load_fom_catalog(modules)
        except Exception:
            return None
        return self.fom_catalog

    def _resolve_object_class_spec(self, class_name: str) -> Any | None:
        catalog = self._ensure_fom_catalog()
        if catalog is None:
            return None
        return catalog.object_classes.get(class_name)

    def _resolve_interaction_class_spec(self, class_name: str) -> Any | None:
        catalog = self._ensure_fom_catalog()
        if catalog is None:
            return None
        return catalog.interaction_classes.get(class_name)

    def _ensure_peer_session(
        self,
        alias: str,
        *,
        federate_name: str | None = None,
        federate_type: str | None = None,
    ) -> "InteractiveFederateSession":
        peer = self.peer_sessions.get(alias)
        if peer is not None:
            return peer
        peer_config = SessionConfig(
            edition=self.config.edition,
            backend=self.config.backend,
            federation_name=self.state.active_federation_name or self.config.federation_name,
            federate_name=federate_name or f"{alias.capitalize()}Federate",
            federate_type=federate_type or "observer",
            fom_modules=self.config.fom_modules,
            logical_time_implementation=self.config.logical_time_implementation,
            transport_kind=self.config.transport_kind,
            transport_target=self.config.transport_target,
            json_output=self.config.json_output,
        )
        peer = InteractiveFederateSession(config=peer_config)
        self.peer_sessions[alias] = peer
        return peer

    def ensure_peer(self, alias: str, *, federate_name: str | None = None, federate_type: str | None = None) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias, federate_name=federate_name, federate_type=federate_type)
        payload = {
            "status": "ok",
            "message": "peer session ready",
            "peer": {
                "alias": alias,
                "federate_name": peer.config.federate_name,
                "federate_type": peer.config.federate_type,
                "federation_name": peer.config.federation_name,
            },
        }
        self._set_focus(f"Peer {alias}", payload["peer"])
        return payload

    def peer_join(
        self,
        alias: str,
        *,
        federate_name: str | None = None,
        federate_type: str | None = None,
        federation_name: str | None = None,
    ) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias, federate_name=federate_name, federate_type=federate_type)
        result = peer.join(
            federate_name=federate_name,
            federate_type=federate_type,
            federation_name=federation_name or self.state.active_federation_name or self.config.federation_name,
            create_if_missing=False,
        )
        payload = {"status": "ok", "message": "peer joined", "peer_alias": alias, "peer_result": result}
        self._set_focus(f"Peer {alias}", payload)
        return payload

    def peer_subscribe_object(self, alias: str, class_name: str, attribute_names: tuple[str, ...]) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias)
        result = peer.subscribe_object(class_name, attribute_names)
        payload = {"status": "ok", "message": "peer object subscription updated", "peer_alias": alias, "peer_result": result}
        self._set_focus(f"Peer {alias}", payload)
        return payload

    def peer_subscribe_interaction(self, alias: str, class_name: str) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias)
        result = peer.subscribe_interaction(class_name)
        payload = {"status": "ok", "message": "peer interaction subscription updated", "peer_alias": alias, "peer_result": result}
        self._set_focus(f"Peer {alias}", payload)
        return payload

    def peer_evoke(self, alias: str, minimum_seconds: float = 0.0, maximum_seconds: float = 0.0) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias)
        result = peer.evoke(minimum_seconds, maximum_seconds)
        payload = {"status": "ok", "message": "peer callbacks evoked", "peer_alias": alias, "peer_result": result}
        self._set_focus(f"Peer {alias}", payload)
        return payload

    def peer_callbacks_snapshot(self, alias: str, limit: int = 10) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias)
        payload = {"status": "ok", "message": "peer callbacks snapshot", "peer_alias": alias, "peer": peer.callbacks_snapshot(limit=limit)}
        self._set_focus(f"Peer {alias} callbacks", payload["peer"])
        return payload

    def peer_status(self, alias: str) -> dict[str, Any]:
        peer = self._ensure_peer_session(alias)
        payload = {"status": "ok", "message": "peer status", "peer_alias": alias, "peer": peer.status()["session"]}
        self._set_focus(f"Peer {alias} status", payload["peer"])
        return payload

    def _ensure_managed_server(self, alias: str, kind: str) -> Any:
        server = self.managed_servers.get(alias)
        if server is not None:
            return server
        if kind == "grpc":
            if self.config.edition == "2025":
                from hla.transports.grpc.python_server_2025 import start_2025_grpc_server

                server = start_2025_grpc_server()
            else:
                from hla.transports.grpc.python_server import start_python_grpc_server

                server = start_python_grpc_server()
        elif kind == "rest":
            if self.config.edition == "2025":
                from hla.transports.rest.rest_transport_host import start_2025_rest_server

                server = start_2025_rest_server()
            else:
                from hla.transports.rest.rest_transport_host import start_python_rest_server

                server = start_python_rest_server()
        else:
            raise SystemExit(f"unsupported managed route server kind: {kind!r}")
        self.managed_servers[alias] = server
        return server

    def ensure_route_session(self, alias: str, route_kind: str) -> dict[str, Any]:
        route = self.route_sessions.get(alias)
        if route is not None:
            payload = {
                "status": "ok",
                "message": "route session ready",
                "route": {
                    "alias": alias,
                    "route_kind": route_kind,
                    "transport": route._transport_options().get("transport"),
                    "federation_name": route.config.federation_name,
                },
            }
            self._set_focus(f"Route {alias}", payload["route"])
            return payload
        transport_kind: str | None = None
        transport_target: str | None = None
        federation_name = f"{self.config.federation_name}-{alias}"
        backend_name = self.config.backend
        if route_kind == "grpc":
            server = self._ensure_managed_server(alias, route_kind)
            transport_kind = "grpc"
            transport_target = str(server.target)
            federation_name = f"{self.config.federation_name}-hosted"
            if self.config.edition == "2010":
                backend_name = "certi"
        elif route_kind != "direct":
            if route_kind == "rest":
                server = self._ensure_managed_server(alias, route_kind)
                transport_kind = "rest"
                transport_target = str(server.base_url)
                federation_name = f"{self.config.federation_name}-hosted-rest"
                if self.config.edition == "2010":
                    backend_name = "certi"
            else:
                raise SystemExit(f"unsupported route kind: {route_kind!r}")
        route_config = SessionConfig(
            edition=self.config.edition,
            backend=backend_name,
            federation_name=federation_name,
            federate_name=f"{alias.capitalize()}RouteFederate",
            federate_type="analysis",
            fom_modules=self.config.fom_modules,
            logical_time_implementation=self.config.logical_time_implementation,
            transport_kind=transport_kind,
            transport_target=transport_target,
            json_output=self.config.json_output,
        )
        route = InteractiveFederateSession(config=route_config)
        self.route_sessions[alias] = route
        payload = {
            "status": "ok",
            "message": "route session ready",
            "route": {
                "alias": alias,
                "route_kind": route_kind,
                "transport": route._transport_options().get("transport"),
                "federation_name": route.config.federation_name,
            },
        }
        self._set_focus(f"Route {alias}", payload["route"])
        return payload

    def route_connect(self, alias: str) -> dict[str, Any]:
        route = self.route_sessions.get(alias)
        if route is None:
            raise SystemExit(f"unknown route session: {alias!r}")
        payload = {"status": "ok", "message": "route connected", "route_alias": alias, "route_result": route.connect()}
        self._set_focus(f"Route {alias}", payload)
        return payload

    def route_create(
        self,
        alias: str,
        federation_name: str | None = None,
        *,
        fom_scenario: str | None = None,
    ) -> dict[str, Any]:
        route = self.route_sessions.get(alias)
        if route is None:
            raise SystemExit(f"unknown route session: {alias!r}")
        payload = {
            "status": "ok",
            "message": "route federation created",
            "route_alias": alias,
            "route_result": route.create(federation_name, fom_scenario=fom_scenario),
        }
        self._set_focus(f"Route {alias}", payload)
        return payload

    def route_join(
        self,
        alias: str,
        federate_name: str | None = None,
        federate_type: str | None = None,
        federation_name: str | None = None,
    ) -> dict[str, Any]:
        route = self.route_sessions.get(alias)
        if route is None:
            raise SystemExit(f"unknown route session: {alias!r}")
        payload = {
            "status": "ok",
            "message": "route federate joined",
            "route_alias": alias,
            "route_result": route.join(federate_name, federate_type, federation_name),
        }
        self._set_focus(f"Route {alias}", payload)
        return payload

    def route_status(self, alias: str) -> dict[str, Any]:
        route = self.route_sessions.get(alias)
        if route is None:
            raise SystemExit(f"unknown route session: {alias!r}")
        payload = {"status": "ok", "message": "route status", "route_alias": alias, "route": route.status()["session"]}
        self._set_focus(f"Route {alias} status", payload["route"])
        return payload

    def _object_class_handle(self, class_name: str) -> Any:
        if not self.state.joined:
            self.join()
        return _call_surface(
            self.rti,
            "getObjectClassHandle",
            "get_object_class_handle",
            _args=(class_name,),
        )

    def _interaction_class_handle(self, class_name: str) -> Any:
        if not self.state.joined:
            self.join()
        return _call_surface(
            self.rti,
            "getInteractionClassHandle",
            "get_interaction_class_handle",
            _args=(class_name,),
        )

    def _attribute_handles(self, class_handle: Any, attribute_names: tuple[str, ...]) -> dict[str, Any]:
        return {
            name: _call_surface(
                self.rti,
                "getAttributeHandle",
                "get_attribute_handle",
                _args=(class_handle, name),
            )
            for name in attribute_names
        }

    def _parameter_handles(self, class_handle: Any, parameter_names: tuple[str, ...]) -> dict[str, Any]:
        return {
            name: _call_surface(
                self.rti,
                "getParameterHandle",
                "get_parameter_handle",
                _args=(class_handle, name),
            )
            for name in parameter_names
        }

    def _encode_value_map(self, pairs: dict[str, str], *, handles: dict[str, Any]) -> dict[Any, bytes]:
        return {handles[name]: value.encode("utf-8") for name, value in pairs.items()}

    def _split_csv_names(self, raw: str) -> tuple[str, ...]:
        return tuple(item.strip() for item in raw.split(",") if item.strip())

    def _set_focus(self, title: str, payload: Any) -> None:
        self.state.tui_focus_title = title
        if isinstance(payload, str):
            self.state.tui_focus_text = payload
            return
        self.state.tui_focus_text = json.dumps(_jsonable(payload), indent=2, sort_keys=True)

    def _featured_object_class(self) -> str | None:
        for step in self.walkthrough_steps:
            if step.command is None:
                continue
            rendered = self._render_walkthrough_command(step.command)
            parts = shlex.split(rendered)
            if not parts:
                continue
            if parts[0] in {"inspect-class", "publish-object", "register-object"} and len(parts) > 1:
                return parts[1]
        if self.fom_catalog is None or not self.fom_catalog.object_classes:
            return None
        return sorted(self.fom_catalog.object_classes)[0]

    def _featured_interaction_class(self) -> str | None:
        for step in self.walkthrough_steps:
            if step.command is None:
                continue
            rendered = self._render_walkthrough_command(step.command)
            parts = shlex.split(rendered)
            if not parts:
                continue
            if parts[0] in {"inspect-interaction", "publish-interaction", "send-interaction"} and len(parts) > 1:
                return parts[1]
        if self.fom_catalog is None or not self.fom_catalog.interaction_classes:
            return None
        return sorted(self.fom_catalog.interaction_classes)[0]

    def _featured_datatype(self) -> str | None:
        for step in self.walkthrough_steps:
            if step.command is None:
                continue
            rendered = self._render_walkthrough_command(step.command)
            parts = shlex.split(rendered)
            if not parts:
                continue
            if parts[0] == "inspect-datatype" and len(parts) > 1:
                return parts[1]
        if self.fom_catalog is None or not self.fom_catalog.datatype_names:
            return None
        return sorted(self.fom_catalog.datatype_names)[0]

    def _help_overlay_lines(self) -> list[str]:
        return [
            "Help Overlay",
            "------------",
            "m -> toggle walkthrough menu",
            "1-9 or shortcut letters -> select a walkthrough when the menu is open",
            "n -> next walkthrough step",
            "o -> inspect featured object class",
            "i -> inspect featured interaction class",
            "d -> inspect featured datatype",
            "p -> inspect first peer callback pane",
            "s -> refresh status into focus pane",
            "e -> evoke local callbacks",
            "c -> clear local callbacks",
            "h or ? -> toggle this overlay",
            "q -> exit the TUI",
        ]

    def _walkthrough_names(self) -> tuple[str, ...]:
        return tuple(sorted(_walkthrough_definitions(self.config)))

    def _walkthrough_menu_lines(self) -> list[str]:
        shortcuts_by_name = {name: shortcut for shortcut, name in _walkthrough_shortcuts(self.config).items()}
        lines = [
            "Walkthrough Menu",
            "----------------",
        ]
        for index, name in enumerate(self._walkthrough_names(), start=1):
            current = " *" if name == self.state.walkthrough_name else "  "
            shortcut = shortcuts_by_name.get(name, "-")
            lines.append(f"{current} {index}. [{shortcut}] {name}")
        return lines

    def _adapter_profiles(self) -> dict[str, dict[str, Any]]:
        return {
            "grpc-fedpro-2025": {
                "name": "grpc-fedpro-2025",
                "route_kind": "hosted-grpc-2025",
                "purpose": "Default 2025 hosted adapter over the FedPro-shaped gRPC transport.",
                "swap_points": [
                    "transport envelope encode/decode",
                    "callback poll decode",
                    "helper callback dispatch",
                    "logical-time field coercion",
                ],
                "primary_files": [
                    "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
                    "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/hosted_fedpro.py",
                ],
            },
            "grpc-quirky-vendor": {
                "name": "grpc-quirky-vendor",
                "route_kind": "vendor-grpc-variant",
                "purpose": "Example of a mildly different gRPC dialect with a different envelope shape but the same RTI semantics.",
                "swap_points": [
                    "encode_request",
                    "decode_response",
                    "encode_callback_poll",
                    "decode_callback_request",
                    "rpc name mapping",
                ],
                "primary_files": [
                    "packages/hla-transport-grpc/src/hla/transports/grpc/vendor_variant.py",
                    "packages/hla-transport-common/src/hla/transports/common/transport.py",
                ],
            },
        }

    def _peer_summary_rows(self) -> list[str]:
        rows = []
        for alias, peer in sorted(self.peer_sessions.items()):
            callbacks = 0 if peer.callbacks is None else len(peer.callbacks.records)
            rows.append(
                f"- {alias}: connected={peer.state.connected} joined={peer.state.joined} "
                f"federate={peer.state.joined_federate_name or '-'} callbacks={callbacks}"
            )
        if not rows:
            rows.append("- <none>")
        return rows

    def _route_summary_rows(self) -> list[str]:
        rows = []
        for alias, route in sorted(self.route_sessions.items()):
            transport = route._transport_options().get("transport")
            rows.append(
                f"- {alias}: connected={route.state.connected} joined={route.state.joined} "
                f"transport={_jsonable(transport) if transport else 'direct'}"
            )
        if not rows:
            rows.append("- <none>")
        return rows

    def _render_walkthrough_command(self, command: str) -> str:
        replacements = {
            "$federation": self.state.active_federation_name or self.config.federation_name,
            "$federation_hosted": f"{self.config.federation_name}-hosted",
            "$federation-hosted-grpc": f"{self.config.federation_name}-hosted-grpc",
            "$federation-hosted-rest": f"{self.config.federation_name}-hosted-rest",
            "$federate_name": self.state.joined_federate_name or self.config.federate_name,
            "$federate_type": self.state.joined_federate_type or self.config.federate_type,
        }
        rendered = command
        for token, value in replacements.items():
            rendered = rendered.replace(token, value)
        return rendered

    def _walkthrough_overview(self) -> dict[str, Any]:
        next_step = None
        if self.walkthrough_steps and self.state.walkthrough_step_index < len(self.walkthrough_steps):
            step = self.walkthrough_steps[self.state.walkthrough_step_index]
            next_step = {
                "index": self.state.walkthrough_step_index + 1,
                "title": step.title,
                "summary": step.summary,
                "command": None if step.command is None else self._render_walkthrough_command(step.command),
            }
        return {
            "name": self.state.walkthrough_name,
            "loaded": bool(self.walkthrough_steps),
            "step_index": self.state.walkthrough_step_index,
            "step_count": len(self.walkthrough_steps),
            "completed": bool(self.walkthrough_steps) and self.state.walkthrough_step_index >= len(self.walkthrough_steps),
            "last_note": self.state.walkthrough_last_note,
            "next_step": next_step,
        }

    def _dashboard_text(self) -> str:
        object_classes = 0 if self.fom_catalog is None else len(self.fom_catalog.object_classes)
        interaction_classes = 0 if self.fom_catalog is None else len(self.fom_catalog.interaction_classes)
        datatype_names = 0 if self.fom_catalog is None else len(self.fom_catalog.datatype_names)
        callback_lines = []
        for record in ([] if self.callbacks is None else self.callbacks.records[-8:]):
            callback_lines.append(f"- {record.snake_name} args={_jsonable(record.args)}")
        if not callback_lines:
            callback_lines.append("- <none>")
        object_lines = []
        for name, class_name in sorted(self.state.object_instance_classes.items()):
            object_lines.append(f"- {name}: {class_name}")
        if not object_lines:
            object_lines.append("- <none>")
        focus_lines = (self.state.tui_focus_text or "<none>").splitlines()
        peer_lines = self._peer_summary_rows()
        route_lines = self._route_summary_rows()
        lines = [
            "Federate CLI Dashboard",
            "======================",
            f"edition: {self.config.edition} | backend: {self.config.backend} | connected: {self.state.connected} | joined: {self.state.joined} | menu={'on' if self.state.tui_walkthrough_menu_visible else 'off'} | help={'on' if self.state.tui_help_visible else 'off'}",
            f"federation: {self.state.active_federation_name or '-'} | federate: {self.state.joined_federate_name or '-'} ({self.state.joined_federate_type or '-'})",
            f"fom counts: objects={object_classes} | interactions={interaction_classes} | datatypes={datatype_names}",
            f"published objects: {len(self.state.published_object_classes)} | subscribed objects: {len(self.state.subscribed_object_classes)}",
            f"published interactions: {len(self.state.published_interaction_classes)} | subscribed interactions: {len(self.state.subscribed_interaction_classes)}",
            f"walkthrough: {self.state.walkthrough_name or '-'} | step {self.state.walkthrough_step_index}/{len(self.walkthrough_steps)}",
            "",
            "Object Instances",
            "----------------",
            *object_lines,
            "",
            "Peer Sessions",
            "-------------",
            *peer_lines,
            "",
            "Route Sessions",
            "--------------",
            *route_lines,
            "",
            "Recent Callbacks",
            "----------------",
            *callback_lines,
            "",
            "Walkthrough Note",
            "----------------",
            f"- {self.state.walkthrough_last_note or '<none>'}",
            "",
            f"Focus: {self.state.tui_focus_title or '<none>'}",
            "----------------",
            *focus_lines[:12],
            "",
        ]
        if self.state.tui_help_visible:
            lines.extend(["", *self._help_overlay_lines()])
        if self.state.tui_walkthrough_menu_visible:
            lines.extend(["", *self._walkthrough_menu_lines()])
        if not self.state.tui_help_visible and not self.state.tui_walkthrough_menu_visible:
            lines.append("Keys: h help | m menu | q exit | r refresh | e evoke | c clear | n next step | o object | i interaction | d datatype | p peer | s status")
        return "\n".join(lines)

    def connect(self) -> dict[str, Any]:
        if self.state.connected:
            return {"status": "ok", "message": "already connected", "backend": _jsonable(getattr(self.rti, "backend_info", None))}
        self.rti = self._create_rti()
        callbacks = self._ensure_callbacks()
        _call_surface(
            self.rti,
            "connect",
            _args=(callbacks, _callback_model(self.config.edition)),
        )
        self.state.connected = True
        return {"status": "ok", "message": "connected", "backend": _jsonable(getattr(self.rti, "backend_info", None))}

    def create(self, federation_name: str | None = None, *, fom_modules: tuple[str, ...] = (), fom_scenario: str | None = None, logical_time_implementation: str | None = None) -> dict[str, Any]:
        self.connect()
        active_federation = federation_name or self.state.active_federation_name or self.config.federation_name
        modules = self._resolve_fom_modules(override_modules=fom_modules, override_scenario=fom_scenario)
        logical_time_name = logical_time_implementation or self.config.logical_time_implementation
        self._load_fom_catalog(modules)
        self._validate_2025_fom(modules)
        if self.config.edition == "2025":
            _call_surface(
                self.rti,
                "createFederationExecution",
                "create_federation_execution",
                _args=(active_federation, list(modules), logical_time_name),
            )
        else:
            fom_payload: Any = modules[0] if len(modules) == 1 else list(modules)
            _call_surface(
                self.rti,
                "createFederationExecution",
                "create_federation_execution",
                _args=(active_federation, fom_payload),
            )
        self.state.federation_created = True
        self.state.active_federation_name = active_federation
        return {
            "status": "ok",
            "message": "federation created",
            "federation_name": active_federation,
            "fom_modules": modules,
            "logical_time_implementation": logical_time_name if self.config.edition == "2025" else None,
            "validation_status": self.state.validation_status,
        }

    def list_classes(self, *, kind: str = "all", contains: str | None = None) -> dict[str, Any]:
        catalog = self._ensure_fom_catalog()
        if catalog is None:
            return {"status": "blocked", "message": "no FOM catalog available"}
        contains_text = None if contains is None else contains.lower()
        object_rows: list[dict[str, Any]] = []
        interaction_rows: list[dict[str, Any]] = []
        if kind in {"all", "object", "objects"}:
            for spec in sorted(catalog.object_classes.values(), key=lambda item: item.full_name):
                if contains_text and contains_text not in spec.full_name.lower():
                    continue
                object_rows.append(
                    {
                        "full_name": spec.full_name,
                        "parent_name": spec.parent_name,
                        "attributes": list(spec.attributes),
                        "declared_attributes": list(spec.declared_attributes),
                        "attribute_datatypes": dict(spec.attribute_datatypes),
                    }
                )
        if kind in {"all", "interaction", "interactions"}:
            for spec in sorted(catalog.interaction_classes.values(), key=lambda item: item.full_name):
                if contains_text and contains_text not in spec.full_name.lower():
                    continue
                interaction_rows.append(
                    {
                        "full_name": spec.full_name,
                        "parent_name": spec.parent_name,
                        "parameters": list(spec.parameters),
                        "declared_parameters": list(spec.declared_parameters),
                        "parameter_datatypes": dict(spec.parameter_datatypes),
                    }
                )
        return {
            "status": "ok",
            "message": "class inventory",
            "kind": kind,
            "object_classes": object_rows,
            "interaction_classes": interaction_rows,
        }

    def list_interactions(self, *, contains: str | None = None) -> dict[str, Any]:
        payload = self.list_classes(kind="interaction", contains=contains)
        payload["message"] = "interaction inventory"
        return payload

    def list_datatypes(self, *, contains: str | None = None) -> dict[str, Any]:
        catalog = self._ensure_fom_catalog()
        if catalog is None:
            return {"status": "blocked", "message": "no FOM catalog available"}
        contains_text = None if contains is None else contains.lower()
        rows = []
        for name in sorted(catalog.datatype_names):
            if contains_text and contains_text not in name.lower():
                continue
            rows.append({"name": name})
        return {
            "status": "ok",
            "message": "datatype inventory",
            "datatypes": rows,
        }

    def inspect_class(self, class_name: str) -> dict[str, Any]:
        spec = self._resolve_object_class_spec(class_name)
        if spec is None:
            return {"status": "blocked", "message": "object class not found", "class_name": class_name}
        payload = {
            "status": "ok",
            "message": "object class detail",
            "class_name": class_name,
            "class": {
                "full_name": spec.full_name,
                "parent_name": spec.parent_name,
                "attributes": list(spec.attributes),
                "declared_attributes": list(spec.declared_attributes),
                "attribute_datatypes": dict(spec.attribute_datatypes),
            },
        }
        self._set_focus(f"Object {class_name}", payload["class"])
        return payload

    def inspect_interaction(self, class_name: str) -> dict[str, Any]:
        spec = self._resolve_interaction_class_spec(class_name)
        if spec is None:
            return {"status": "blocked", "message": "interaction class not found", "class_name": class_name}
        payload = {
            "status": "ok",
            "message": "interaction class detail",
            "class_name": class_name,
            "interaction": {
                "full_name": spec.full_name,
                "parent_name": spec.parent_name,
                "parameters": list(spec.parameters),
                "declared_parameters": list(spec.declared_parameters),
                "parameter_datatypes": dict(spec.parameter_datatypes),
            },
        }
        self._set_focus(f"Interaction {class_name}", payload["interaction"])
        return payload

    def inspect_datatype(self, name: str) -> dict[str, Any]:
        catalog = self._ensure_fom_catalog()
        if catalog is None:
            return {"status": "blocked", "message": "no FOM catalog available", "name": name}
        if name not in catalog.datatype_names:
            return {"status": "blocked", "message": "datatype not found", "name": name}
        payload = {
            "status": "ok",
            "message": "datatype detail",
            "datatype": {"name": name},
        }
        self._set_focus(f"Datatype {name}", payload["datatype"])
        return payload

    def inspect_adapter(self, name: str) -> dict[str, Any]:
        profiles = self._adapter_profiles()
        profile = profiles.get(name)
        if profile is None:
            return {
                "status": "blocked",
                "message": "adapter profile not found",
                "name": name,
                "available": sorted(profiles),
            }
        payload = {
            "status": "ok",
            "message": "adapter profile detail",
            "adapter": profile,
        }
        self._set_focus(f"Adapter {name}", payload["adapter"])
        return payload

    def join(
        self,
        federate_name: str | None = None,
        federate_type: str | None = None,
        federation_name: str | None = None,
        *,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        active_federation = federation_name or self.state.active_federation_name or self.config.federation_name
        if not self.state.federation_created or self.state.active_federation_name != active_federation:
            if create_if_missing:
                self.create(active_federation)
            else:
                self.connect()
                modules = self._resolve_fom_modules()
                self._load_fom_catalog(modules)
                self._validate_2025_fom(modules)
                self.state.federation_created = True
                self.state.active_federation_name = active_federation
        active_federate_name = federate_name or self.config.federate_name
        active_federate_type = federate_type or self.config.federate_type
        handle = _call_surface(
            self.rti,
            "joinFederationExecution",
            "join_federation_execution",
            _args=(active_federate_name, active_federate_type, active_federation),
        )
        self.state.joined = True
        self.state.active_federation_name = active_federation
        self.state.joined_federate_name = active_federate_name
        self.state.joined_federate_type = active_federate_type
        self.state.federate_handle = handle
        payload = {
            "status": "ok",
            "message": "federate joined",
            "federation_name": active_federation,
            "federate_name": active_federate_name,
            "federate_type": active_federate_type,
            "federate_handle": _jsonable(handle),
        }
        self._set_focus("Join", payload)
        return payload

    def publish_object(self, class_name: str, attribute_names: tuple[str, ...]) -> dict[str, Any]:
        object_class = self._object_class_handle(class_name)
        attributes = self._attribute_handles(object_class, attribute_names)
        _call_surface(
            self.rti,
            "publishObjectClassAttributes",
            "publish_object_class_attributes",
            _args=(object_class, set(attributes.values())),
        )
        self.state.published_object_classes[class_name] = attribute_names
        return {
            "status": "ok",
            "message": "object publication updated",
            "class_name": class_name,
            "attributes": list(attribute_names),
        }

    def subscribe_object(self, class_name: str, attribute_names: tuple[str, ...]) -> dict[str, Any]:
        object_class = self._object_class_handle(class_name)
        attributes = self._attribute_handles(object_class, attribute_names)
        _call_surface(
            self.rti,
            "subscribeObjectClassAttributes",
            "subscribe_object_class_attributes",
            _args=(object_class, set(attributes.values())),
        )
        self.state.subscribed_object_classes[class_name] = attribute_names
        return {
            "status": "ok",
            "message": "object subscription updated",
            "class_name": class_name,
            "attributes": list(attribute_names),
        }

    def publish_interaction(self, class_name: str) -> dict[str, Any]:
        interaction_class = self._interaction_class_handle(class_name)
        _call_surface(
            self.rti,
            "publishInteractionClass",
            "publish_interaction_class",
            _args=(interaction_class,),
        )
        values = list(self.state.published_interaction_classes)
        if class_name not in values:
            values.append(class_name)
        self.state.published_interaction_classes = tuple(values)
        return {"status": "ok", "message": "interaction publication updated", "class_name": class_name}

    def subscribe_interaction(self, class_name: str) -> dict[str, Any]:
        interaction_class = self._interaction_class_handle(class_name)
        _call_surface(
            self.rti,
            "subscribeInteractionClass",
            "subscribe_interaction_class",
            _args=(interaction_class,),
        )
        values = list(self.state.subscribed_interaction_classes)
        if class_name not in values:
            values.append(class_name)
        self.state.subscribed_interaction_classes = tuple(values)
        return {"status": "ok", "message": "interaction subscription updated", "class_name": class_name}

    def register_object(self, class_name: str, instance_name: str) -> dict[str, Any]:
        object_class = self._object_class_handle(class_name)
        object_handle = _call_surface(
            self.rti,
            "registerObjectInstance",
            "register_object_instance",
            _args=(object_class, instance_name),
        )
        self.state.object_instances[instance_name] = object_handle
        self.state.object_instance_classes[instance_name] = class_name
        return {
            "status": "ok",
            "message": "object registered",
            "class_name": class_name,
            "instance_name": instance_name,
            "object_handle": _jsonable(object_handle),
        }

    def update_object(self, instance_name: str, updates: dict[str, str]) -> dict[str, Any]:
        if instance_name not in self.state.object_instances:
            raise SystemExit(f"unknown object instance: {instance_name!r}")
        class_name = self.state.object_instance_classes[instance_name]
        object_class = self._object_class_handle(class_name)
        attribute_handles = self._attribute_handles(object_class, tuple(updates))
        encoded = self._encode_value_map(updates, handles=attribute_handles)
        _call_surface(
            self.rti,
            "updateAttributeValues",
            "update_attribute_values",
            _args=(self.state.object_instances[instance_name], encoded, b"interactive-federate-cli"),
        )
        return {
            "status": "ok",
            "message": "object updated",
            "instance_name": instance_name,
            "class_name": class_name,
            "attributes": updates,
        }

    def send_interaction(self, class_name: str, parameters: dict[str, str]) -> dict[str, Any]:
        interaction_class = self._interaction_class_handle(class_name)
        parameter_handles = self._parameter_handles(interaction_class, tuple(parameters))
        encoded = self._encode_value_map(parameters, handles=parameter_handles)
        _call_surface(
            self.rti,
            "sendInteraction",
            "send_interaction",
            _args=(interaction_class, encoded, b"interactive-federate-cli"),
        )
        return {
            "status": "ok",
            "message": "interaction sent",
            "class_name": class_name,
            "parameters": parameters,
        }

    def evoke(self, minimum_seconds: float = 0.0, maximum_seconds: float = 0.0) -> dict[str, Any]:
        if not self.state.connected:
            self.connect()
        evoked = _call_surface(
            self.rti,
            "evokeMultipleCallbacks",
            "evoke_multiple_callbacks",
            _args=(minimum_seconds, maximum_seconds),
        )
        return {
            "status": "ok",
            "message": "callbacks evoked",
            "evoked": bool(evoked),
            "minimum_seconds": minimum_seconds,
            "maximum_seconds": maximum_seconds,
            "callback_count": len(self.callbacks.records) if self.callbacks is not None else 0,
        }

    def callbacks_snapshot(self, limit: int = 10) -> dict[str, Any]:
        records = [] if self.callbacks is None else self.callbacks.records[-limit:]
        payload = {
            "status": "ok",
            "message": "callbacks snapshot",
            "callback_count": 0 if self.callbacks is None else len(self.callbacks.records),
            "records": [
                {
                    "method_name": record.method_name,
                    "snake_name": record.snake_name,
                    "args": _jsonable(record.args),
                    "kwargs": _jsonable(record.kwargs),
                }
                for record in records
            ],
        }
        self._set_focus("Callbacks", payload)
        return payload

    def clear_callbacks(self) -> dict[str, Any]:
        if self.callbacks is not None:
            self.callbacks.clear()
        payload = {"status": "ok", "message": "callbacks cleared", "callback_count": 0}
        self._set_focus("Callbacks", payload)
        return payload

    def pause(self, note: str | None = None, *, seconds: float = 0.0) -> dict[str, Any]:
        self.state.walkthrough_last_note = note
        if seconds > 0.0:
            time.sleep(seconds)
        elif sys.stdin.isatty() and sys.stdout.isatty() and not self.config.json_output:
            prompt = note or "Paused. Press Enter to continue."
            input(f"[{TOOL_LABEL}] {prompt} ")
        payload = {
            "status": "ok",
            "message": "pause reached",
            "note": note,
            "seconds": seconds,
        }
        self._set_focus("Pause", payload)
        return payload

    def load_walkthrough(self, name: str) -> dict[str, Any]:
        steps = _walkthrough_definitions(self.config).get(name)
        if steps is None:
            return {
                "status": "blocked",
                "message": "walkthrough not found",
                "name": name,
                "available": sorted(_walkthrough_definitions(self.config)),
            }
        self.walkthrough_steps = steps
        self.state.walkthrough_name = name
        self.state.walkthrough_step_index = 0
        self.state.walkthrough_last_note = None
        payload = {
            "status": "ok",
            "message": "walkthrough loaded",
            "walkthrough": self._walkthrough_overview(),
        }
        self._set_focus("Walkthrough", payload["walkthrough"])
        return payload

    def walkthrough_status(self) -> dict[str, Any]:
        payload = {
            "status": "ok",
            "message": "walkthrough status",
            "walkthrough": self._walkthrough_overview(),
        }
        self._set_focus("Walkthrough", payload["walkthrough"])
        return payload

    def run_next_walkthrough_step(self) -> dict[str, Any]:
        if not self.walkthrough_steps:
            return {"status": "blocked", "message": "no walkthrough loaded"}
        if self.state.walkthrough_step_index >= len(self.walkthrough_steps):
            return {
                "status": "ok",
                "message": "walkthrough already complete",
                "walkthrough": self._walkthrough_overview(),
            }
        step = self.walkthrough_steps[self.state.walkthrough_step_index]
        rendered_command = None if step.command is None else self._render_walkthrough_command(step.command)
        self.state.walkthrough_step_index += 1
        self.state.walkthrough_last_note = step.summary
        result: dict[str, Any] = {
            "status": "ok",
            "message": "walkthrough step completed",
            "walkthrough_step": {
                "index": self.state.walkthrough_step_index,
                "title": step.title,
                "summary": step.summary,
                "command": rendered_command,
            },
        }
        if rendered_command is not None:
            nested = _run_command(self, rendered_command, record_history=False)
            if nested is not None:
                result["step_result"] = nested
        result["walkthrough"] = self._walkthrough_overview()
        self._set_focus(f"Step {self.state.walkthrough_step_index}: {step.title}", result)
        return result

    def resign(self, action_name: str = "NO_ACTION") -> dict[str, Any]:
        if not self.state.joined:
            return {"status": "ok", "message": "not joined"}
        action = _resign_action(self.config.edition, action_name=action_name)
        _call_surface(
            self.rti,
            "resignFederationExecution",
            "resign_federation_execution",
            _args=(action,),
        )
        self.state.joined = False
        return {"status": "ok", "message": "federate resigned", "action": action_name}

    def destroy(self, federation_name: str | None = None) -> dict[str, Any]:
        active_federation = federation_name or self.state.active_federation_name or self.config.federation_name
        _call_surface(
            self.rti,
            "destroyFederationExecution",
            "destroy_federation_execution",
            _args=(active_federation,),
        )
        self.state.federation_created = False
        self.state.active_federation_name = active_federation
        return {"status": "ok", "message": "federation destroyed", "federation_name": active_federation}

    def disconnect(self) -> dict[str, Any]:
        if not self.state.connected:
            return {"status": "ok", "message": "already disconnected"}
        _call_surface(self.rti, "disconnect")
        self.state.connected = False
        self.state.joined = False
        self.state.federation_created = False
        if hasattr(self.rti, "close"):
            self.rti.close()
        self.rti = None
        return {"status": "ok", "message": "disconnected"}

    def status(self) -> dict[str, Any]:
        last_callback = None
        if self.callbacks is not None and self.callbacks.records:
            record = self.callbacks.records[-1]
            last_callback = {
                "method_name": record.method_name,
                "snake_name": record.snake_name,
                "args": _jsonable(record.args),
                "kwargs": _jsonable(record.kwargs),
            }
        payload = {
            "status": "ok",
            "message": "session status",
            "session": {
                "edition": self.config.edition,
                "backend": self.config.backend,
                "transport": _jsonable(self._transport_options().get("transport")),
                "connected": self.state.connected,
                "federation_created": self.state.federation_created,
                "joined": self.state.joined,
                "active_federation_name": self.state.active_federation_name,
                "joined_federate_name": self.state.joined_federate_name,
                "joined_federate_type": self.state.joined_federate_type,
                "federate_handle": _jsonable(self.state.federate_handle),
                "fom_modules": list(self.config.fom_modules),
                "validation_status": self.state.validation_status,
                "validation_issues": _jsonable(self.state.validation_issues),
                "validation_diagnostics": list(self.state.validation_diagnostics),
                "fom_catalog_counts": {
                    "object_classes": 0 if self.fom_catalog is None else len(self.fom_catalog.object_classes),
                    "interaction_classes": 0 if self.fom_catalog is None else len(self.fom_catalog.interaction_classes),
                    "datatype_names": 0 if self.fom_catalog is None else len(self.fom_catalog.datatype_names),
                },
                "callback_count": 0 if self.callbacks is None else len(self.callbacks.records),
                "last_callback": last_callback,
                "object_instances": {
                    name: {
                        "class_name": self.state.object_instance_classes[name],
                        "handle": _jsonable(handle),
                    }
                    for name, handle in self.state.object_instances.items()
                },
                "published_object_classes": dict(self.state.published_object_classes),
                "subscribed_object_classes": dict(self.state.subscribed_object_classes),
                "published_interaction_classes": list(self.state.published_interaction_classes),
                "subscribed_interaction_classes": list(self.state.subscribed_interaction_classes),
                "backend_info": _jsonable(getattr(self.rti, "backend_info", None)) if self.rti is not None else None,
                "command_history": list(self.state.command_history),
                "walkthrough": self._walkthrough_overview(),
                "peers": {
                    alias: {
                        "connected": peer.state.connected,
                        "joined": peer.state.joined,
                        "federate_name": peer.state.joined_federate_name or peer.config.federate_name,
                        "callback_count": 0 if peer.callbacks is None else len(peer.callbacks.records),
                    }
                    for alias, peer in sorted(self.peer_sessions.items())
                },
                "routes": {
                    alias: {
                        "connected": route.state.connected,
                        "joined": route.state.joined,
                        "federate_name": route.state.joined_federate_name or route.config.federate_name,
                        "transport": _jsonable(route._transport_options().get("transport")),
                        "callback_count": 0 if route.callbacks is None else len(route.callbacks.records),
                    }
                    for alias, route in sorted(self.route_sessions.items())
                },
            },
        }
        self._set_focus("Status", payload["session"])
        return payload

    def tui_snapshot(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "message": "tui snapshot",
            "dashboard": self._dashboard_text(),
        }

    def close(self) -> None:
        for peer in list(self.peer_sessions.values()):
            try:
                peer.close()
            except Exception:
                pass
        self.peer_sessions.clear()
        for route in list(self.route_sessions.values()):
            try:
                route.close()
            except Exception:
                pass
        self.route_sessions.clear()
        for server in list(self.managed_servers.values()):
            try:
                server.close()
            except Exception:
                pass
        self.managed_servers.clear()
        if self.rti is None:
            return
        try:
            if self.state.joined:
                self.resign()
        except Exception:
            pass
        try:
            if self.state.connected:
                _call_surface(self.rti, "disconnect")
        except Exception:
            pass
        try:
            if hasattr(self.rti, "close"):
                self.rti.close()
        except Exception:
            pass
        self.rti = None
        self.state.connected = False
        self.state.joined = False


def _top_level_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=TOOL_LABEL,
        description="Interactive/scriptable federate shell for 2010 and 2025 routes.",
        epilog=_command_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--edition", choices=["2010", "2025"], default="2010")
    parser.add_argument("--backend", default=None, help="Backend/route override.")
    parser.add_argument("--federation", default=None, help="Default federation name.")
    parser.add_argument("--federate-name", default="InteractiveFederate", help="Default federate name.")
    parser.add_argument("--federate-type", default="interactive", help="Default federate type.")
    parser.add_argument("--fom", action="append", default=[], help="Explicit FOM module path; may be repeated.")
    parser.add_argument(
        "--fom-scenario",
        default=None,
        help="Proto2025 packaged scenario name such as message-test. 2025 only.",
    )
    parser.add_argument(
        "--logical-time-implementation",
        default=None,
        help="Logical time implementation name. Defaults to HLAinteger64Time for 2025.",
    )
    parser.add_argument("--transport-kind", default=None, help="Optional transport override such as grpc.")
    parser.add_argument("--transport-target", default=None, help="Optional transport target such as 127.0.0.1:15164.")
    parser.add_argument("--command", action="append", default=[], help="Scripted command. May be repeated.")
    parser.add_argument("--json", action="store_true", help="Emit the final session/result payload as JSON.")
    return parser


def _resolve_config(args: argparse.Namespace) -> SessionConfig:
    edition = str(args.edition)
    backend = str(args.backend or ("python1516_2025" if edition == "2025" else "python1516e"))
    federation_name = str(args.federation or f"interactive-{edition}-{uuid.uuid4().hex[:8]}")
    if args.fom:
        fom_modules = tuple(str(Path(item)) for item in args.fom)
    elif edition == "2025":
        scenario_name = str(args.fom_scenario or "message-test")
        fom_modules = tuple(str(path) for path in scenario_fom_paths(scenario_name))
    else:
        fom_modules = ("DemoFOMmodule.xml",)
    logical_time_implementation = str(args.logical_time_implementation or "HLAinteger64Time")
    return SessionConfig(
        edition=edition,
        backend=backend,
        federation_name=federation_name,
        federate_name=str(args.federate_name),
        federate_type=str(args.federate_type),
        fom_modules=fom_modules,
        logical_time_implementation=logical_time_implementation,
        transport_kind=None if args.transport_kind is None else str(args.transport_kind),
        transport_target=None if args.transport_target is None else str(args.transport_target),
        json_output=bool(args.json),
    )


def _command_help() -> str:
    return "\n".join(
        [
            "commands:",
            "  help",
            "  connect",
            "  create [federation] [--fom PATH]... [--fom-scenario NAME] [--logical-time NAME]",
            "  join [federate-name] [federate-type] [federation]",
            "  list-classes [all|object|interaction] [contains-text]",
            "  list-interactions [contains-text]",
            "  list-datatypes [contains-text]",
            "  inspect-class FULL_NAME",
            "  inspect-interaction FULL_NAME",
            "  inspect-datatype NAME",
            "  inspect-adapter NAME",
            "  publish-object CLASS ATTR1,ATTR2",
            "  subscribe-object CLASS ATTR1,ATTR2",
            "  publish-interaction CLASS",
            "  subscribe-interaction CLASS",
            "  register-object CLASS INSTANCE",
            "  update-object INSTANCE attr=value [attr=value...]",
            "  send-interaction CLASS param=value [param=value...]",
            "  evoke [minimum-seconds] [maximum-seconds]",
            "  pause [seconds|note...]",
            "  walkthrough NAME",
            "  walkthrough-status",
            "  next-step",
            "  status",
            "  callbacks [limit]",
            "  clear-callbacks",
            "  tui",
            "  resign [NO_ACTION]",
            "  destroy [federation]",
            "  disconnect",
            "  quit | exit",
            "",
            "examples:",
            f"  {TOOL_LABEL} --edition 2010 --command 'connect' --command 'create demo2010' --command 'join alice operator demo2010' --command 'status' --command 'resign' --command 'destroy demo2010' --command 'disconnect' --json",
            f"  {TOOL_LABEL} --edition 2025 --backend python1516_2025 --command 'connect' --command 'create demo2025 --fom-scenario message-test' --command 'join observer analysis demo2025' --command 'evoke 0 0' --command 'status' --json",
            f"  {TOOL_LABEL} --edition 2025 --command 'create demo2025 --fom-scenario message-test' --command 'list-classes object Target' --command 'publish-object HLAobjectRoot.Proto2025Verdict VerdictCode,SummaryText' --command 'register-object HLAobjectRoot.Proto2025Verdict verdict-1' --command 'update-object verdict-1 VerdictCode=PASS SummaryText=ready' --json",
            f"  {TOOL_LABEL} --edition 2025 --command 'walkthrough message-test-tour' --command 'next-step' --command 'next-step' --command 'walkthrough-status' --json",
            f"  {TOOL_LABEL} --edition 2025 --backend python1516_2025 --command 'walkthrough route-variation-tour' --command 'next-step' --command 'next-step' --command 'next-step' --command 'next-step' --command 'next-step' --command 'walkthrough-status' --json",
            f"  {TOOL_LABEL} --edition 2025 --backend python1516_2025 --federation route-matrix-2025 --command 'create route-matrix-2025 --fom-scenario message-test' --command 'join alpha analysis route-matrix-2025' --command '@route-ensure hosted-grpc grpc' --command '@route-connect hosted-grpc' --command '@route-ensure hosted-rest rest' --command '@route-connect hosted-rest' --command '@route-status hosted-grpc' --command '@route-status hosted-rest' --command 'status' --json",
            f"  {TOOL_LABEL} --edition 2025 --command 'inspect-adapter grpc-quirky-vendor' --json",
            f"  printf 'connect\\ncreate demo\\njoin alice operator demo\\nstatus\\nquit\\n' | {TOOL_LABEL} --edition 2025 --json",
        ]
    )


def _parse_float(raw: str, *, name: str) -> float:
    try:
        return float(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be numeric: {raw!r}") from exc


def _parse_assignments(parts: list[str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    for token in parts:
        if "=" not in token:
            raise SystemExit(f"expected name=value token, got: {token!r}")
        name, value = token.split("=", 1)
        payload[name] = value
    return payload


def _apply_tui_key(session: InteractiveFederateSession, key: str) -> bool:
    lowered = key.lower()
    if session.state.tui_walkthrough_menu_visible and key.isdigit():
        index = int(key) - 1
        names = session._walkthrough_names()
        if 0 <= index < len(names):
            session.load_walkthrough(names[index])
            session.state.tui_walkthrough_menu_visible = False
        return True
    if session.state.tui_walkthrough_menu_visible:
        target = _walkthrough_shortcuts(session.config).get(lowered)
        if target is not None:
            session.load_walkthrough(target)
            session.state.tui_walkthrough_menu_visible = False
            return True
    if lowered == "q":
        return False
    if lowered in {"h", "?"}:
        session.state.tui_help_visible = not session.state.tui_help_visible
        session._set_focus("Help", "TUI help overlay toggled.")
        return True
    if lowered == "m":
        session.state.tui_walkthrough_menu_visible = not session.state.tui_walkthrough_menu_visible
        session._set_focus("Walkthrough Menu", "Select a walkthrough with keys 1-9.")
        return True
    if lowered == "r":
        return True
    if lowered == "e":
        session.evoke(0.0, 0.0)
        return True
    if lowered == "c":
        session.clear_callbacks()
        return True
    if lowered == "n":
        session.run_next_walkthrough_step()
        return True
    if lowered == "o":
        class_name = session._featured_object_class()
        if class_name is not None:
            session.inspect_class(class_name)
        return True
    if lowered == "i":
        class_name = session._featured_interaction_class()
        if class_name is not None:
            session.inspect_interaction(class_name)
        return True
    if lowered == "d":
        name = session._featured_datatype()
        if name is not None:
            session.inspect_datatype(name)
        return True
    if lowered == "p":
        alias = sorted(session.peer_sessions)[0] if session.peer_sessions else None
        if alias is not None:
            session.peer_callbacks_snapshot(alias, limit=10)
        else:
            session._set_focus("Peer", "No peer sessions are active.")
        return True
    if lowered == "s":
        session.status()
        return True
    return True


def _run_tui(session: InteractiveFederateSession, *, json_output: bool) -> dict[str, Any]:
    scripted_keys = "".join(ch for ch in os.environ.get("FEDERATE_CLI_TUI_KEYS", "") if not ch.isspace() and ch != ",")
    if scripted_keys:
        session.connect()
        for key in scripted_keys:
            if not _apply_tui_key(session, key):
                break
        snapshot = session.tui_snapshot()
        snapshot["tui_keys"] = list(scripted_keys)
        if not json_output:
            print(snapshot["dashboard"])
        return snapshot
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        snapshot = session.tui_snapshot()
        if not json_output:
            print(snapshot["dashboard"])
        return snapshot
    import curses

    session.connect()

    def _main(stdscr: Any) -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        while True:
            stdscr.erase()
            dashboard = session.tui_snapshot()["dashboard"].splitlines()
            height, width = stdscr.getmaxyx()
            for row, line in enumerate(dashboard[: max(0, height - 1)]):
                stdscr.addnstr(row, 0, line, max(0, width - 1))
            stdscr.refresh()
            key = stdscr.getch()
            if key == -1:
                continue
            if not _apply_tui_key(session, chr(key)):
                break

    curses.wrapper(_main)
    return session.tui_snapshot()


def _run_command(session: InteractiveFederateSession, command_text: str, *, record_history: bool = True) -> dict[str, Any] | None:
    parts = shlex.split(command_text)
    if not parts:
        return None
    if record_history:
        session.state.command_history.append(command_text)
    command = parts[0]
    if command == "@peer-ensure":
        if len(parts) < 2:
            raise SystemExit("@peer-ensure requires ALIAS [FEDERATE_NAME] [FEDERATE_TYPE]")
        return session.ensure_peer(
            parts[1],
            federate_name=parts[2] if len(parts) > 2 else None,
            federate_type=parts[3] if len(parts) > 3 else None,
        )
    if command == "@peer-join":
        if len(parts) < 2:
            raise SystemExit("@peer-join requires ALIAS [FEDERATE_NAME] [FEDERATE_TYPE] [FEDERATION]")
        return session.peer_join(
            parts[1],
            federate_name=parts[2] if len(parts) > 2 else None,
            federate_type=parts[3] if len(parts) > 3 else None,
            federation_name=parts[4] if len(parts) > 4 else None,
        )
    if command == "@peer-subscribe-object":
        if len(parts) < 4:
            raise SystemExit("@peer-subscribe-object requires ALIAS CLASS ATTR1,ATTR2")
        return session.peer_subscribe_object(parts[1], parts[2], session._split_csv_names(parts[3]))
    if command == "@peer-subscribe-interaction":
        if len(parts) < 3:
            raise SystemExit("@peer-subscribe-interaction requires ALIAS CLASS")
        return session.peer_subscribe_interaction(parts[1], parts[2])
    if command == "@peer-evoke":
        if len(parts) < 2:
            raise SystemExit("@peer-evoke requires ALIAS [minimum-seconds] [maximum-seconds]")
        minimum_seconds = _parse_float(parts[2], name="minimum_seconds") if len(parts) > 2 else 0.0
        maximum_seconds = _parse_float(parts[3], name="maximum_seconds") if len(parts) > 3 else minimum_seconds
        return session.peer_evoke(parts[1], minimum_seconds, maximum_seconds)
    if command == "@peer-callbacks":
        if len(parts) < 2:
            raise SystemExit("@peer-callbacks requires ALIAS [limit]")
        limit = int(parts[2]) if len(parts) > 2 else 10
        return session.peer_callbacks_snapshot(parts[1], limit=limit)
    if command == "@peer-status":
        if len(parts) < 2:
            raise SystemExit("@peer-status requires ALIAS")
        return session.peer_status(parts[1])
    if command == "@route-ensure":
        if len(parts) < 3:
            raise SystemExit("@route-ensure requires ALIAS ROUTE_KIND")
        return session.ensure_route_session(parts[1], parts[2])
    if command == "@route-connect":
        if len(parts) < 2:
            raise SystemExit("@route-connect requires ALIAS")
        return session.route_connect(parts[1])
    if command == "@route-create":
        if len(parts) < 2:
            raise SystemExit("@route-create requires ALIAS [FEDERATION] [--fom-scenario NAME]")
        alias = parts[1]
        federation_name: str | None = None
        fom_scenario: str | None = None
        index = 2
        while index < len(parts):
            token = parts[index]
            if token == "--fom-scenario":
                fom_scenario = parts[index + 1]
                index += 2
                continue
            if federation_name is None:
                federation_name = token
                index += 1
                continue
            raise SystemExit(f"unexpected @route-create argument: {token!r}")
        return session.route_create(alias, federation_name, fom_scenario=fom_scenario)
    if command == "@route-join":
        if len(parts) < 2:
            raise SystemExit("@route-join requires ALIAS [FEDERATE_NAME] [FEDERATE_TYPE] [FEDERATION]")
        return session.route_join(
            parts[1],
            parts[2] if len(parts) > 2 else None,
            parts[3] if len(parts) > 3 else None,
            parts[4] if len(parts) > 4 else None,
        )
    if command == "@route-status":
        if len(parts) < 2:
            raise SystemExit("@route-status requires ALIAS")
        return session.route_status(parts[1])
    if command == "help":
        return {"status": "ok", "message": _command_help()}
    if command == "connect":
        return session.connect()
    if command == "create":
        federation_name: str | None = None
        fom_modules: list[str] = []
        fom_scenario: str | None = None
        logical_time_name: str | None = None
        index = 1
        while index < len(parts):
            token = parts[index]
            if token == "--fom":
                fom_modules.append(parts[index + 1])
                index += 2
                continue
            if token == "--fom-scenario":
                fom_scenario = parts[index + 1]
                index += 2
                continue
            if token == "--logical-time":
                logical_time_name = parts[index + 1]
                index += 2
                continue
            if federation_name is None:
                federation_name = token
                index += 1
                continue
            raise SystemExit(f"unexpected create argument: {token!r}")
        return session.create(
            federation_name,
            fom_modules=tuple(fom_modules),
            fom_scenario=fom_scenario,
            logical_time_implementation=logical_time_name,
        )
    if command == "join":
        federate_name = parts[1] if len(parts) > 1 else None
        federate_type = parts[2] if len(parts) > 2 else None
        federation_name = parts[3] if len(parts) > 3 else None
        return session.join(federate_name, federate_type, federation_name)
    if command == "list-classes":
        kind = parts[1] if len(parts) > 1 else "all"
        contains = parts[2] if len(parts) > 2 else None
        return session.list_classes(kind=kind, contains=contains)
    if command == "list-interactions":
        contains = parts[1] if len(parts) > 1 else None
        return session.list_interactions(contains=contains)
    if command == "list-datatypes":
        contains = parts[1] if len(parts) > 1 else None
        return session.list_datatypes(contains=contains)
    if command == "inspect-class":
        if len(parts) < 2:
            raise SystemExit("inspect-class requires FULL_NAME")
        return session.inspect_class(parts[1])
    if command == "inspect-interaction":
        if len(parts) < 2:
            raise SystemExit("inspect-interaction requires FULL_NAME")
        return session.inspect_interaction(parts[1])
    if command == "inspect-datatype":
        if len(parts) < 2:
            raise SystemExit("inspect-datatype requires NAME")
        return session.inspect_datatype(parts[1])
    if command == "inspect-adapter":
        if len(parts) < 2:
            raise SystemExit("inspect-adapter requires NAME")
        return session.inspect_adapter(parts[1])
    if command == "publish-object":
        if len(parts) < 3:
            raise SystemExit("publish-object requires CLASS and ATTR1,ATTR2")
        return session.publish_object(parts[1], session._split_csv_names(parts[2]))
    if command == "subscribe-object":
        if len(parts) < 3:
            raise SystemExit("subscribe-object requires CLASS and ATTR1,ATTR2")
        return session.subscribe_object(parts[1], session._split_csv_names(parts[2]))
    if command == "publish-interaction":
        if len(parts) < 2:
            raise SystemExit("publish-interaction requires CLASS")
        return session.publish_interaction(parts[1])
    if command == "subscribe-interaction":
        if len(parts) < 2:
            raise SystemExit("subscribe-interaction requires CLASS")
        return session.subscribe_interaction(parts[1])
    if command == "register-object":
        if len(parts) < 3:
            raise SystemExit("register-object requires CLASS and INSTANCE")
        return session.register_object(parts[1], parts[2])
    if command == "update-object":
        if len(parts) < 3:
            raise SystemExit("update-object requires INSTANCE and attr=value pairs")
        return session.update_object(parts[1], _parse_assignments(parts[2:]))
    if command == "send-interaction":
        if len(parts) < 3:
            raise SystemExit("send-interaction requires CLASS and param=value pairs")
        return session.send_interaction(parts[1], _parse_assignments(parts[2:]))
    if command == "evoke":
        minimum_seconds = _parse_float(parts[1], name="minimum_seconds") if len(parts) > 1 else 0.0
        maximum_seconds = _parse_float(parts[2], name="maximum_seconds") if len(parts) > 2 else minimum_seconds
        return session.evoke(minimum_seconds, maximum_seconds)
    if command == "pause":
        if len(parts) == 1:
            return session.pause()
        try:
            seconds = _parse_float(parts[1], name="seconds")
        except SystemExit:
            return session.pause(" ".join(parts[1:]))
        note = " ".join(parts[2:]) if len(parts) > 2 else None
        return session.pause(note, seconds=seconds)
    if command == "walkthrough":
        if len(parts) < 2:
            raise SystemExit("walkthrough requires NAME")
        return session.load_walkthrough(parts[1])
    if command == "walkthrough-status":
        return session.walkthrough_status()
    if command == "next-step":
        return session.run_next_walkthrough_step()
    if command == "status":
        return session.status()
    if command == "callbacks":
        limit = int(parts[1]) if len(parts) > 1 else 10
        return session.callbacks_snapshot(limit=limit)
    if command == "clear-callbacks":
        return session.clear_callbacks()
    if command == "tui":
        return _run_tui(session, json_output=session.config.json_output)
    if command == "resign":
        action_name = parts[1] if len(parts) > 1 else "NO_ACTION"
        return session.resign(action_name)
    if command == "destroy":
        federation_name = parts[1] if len(parts) > 1 else None
        return session.destroy(federation_name)
    if command == "disconnect":
        return session.disconnect()
    if command in {"quit", "exit"}:
        return {"status": "ok", "message": "session exiting", "exit_requested": True}
    raise SystemExit(f"unknown command: {command!r}")


def _emit_result(result: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        return
    if result.get("message"):
        print(f"[{TOOL_LABEL}] {result['message']}")
    payload = {key: value for key, value in result.items() if key not in {"status", "message", "exit_requested"}}
    if payload:
        print(json.dumps(_jsonable(payload), indent=2, sort_keys=True))


def _interactive_commands(args: argparse.Namespace) -> list[str]:
    if args.command:
        return [str(item) for item in args.command]
    if sys.stdin.isatty():
        return []
    return [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]


def main(argv: list[str]) -> int:
    parser = _top_level_parser()
    args = parser.parse_args(argv[1:])
    config = _resolve_config(args)
    session = InteractiveFederateSession(config=config)
    scripted_commands = _interactive_commands(args)
    results: list[dict[str, Any]] = []

    try:
        if scripted_commands:
            for command_text in scripted_commands:
                result = _run_command(session, command_text)
                if result is None:
                    continue
                results.append({"command": command_text, **result})
                _emit_result(result, json_output=config.json_output)
                if result.get("exit_requested"):
                    break
        elif sys.stdin.isatty():
            if not config.json_output:
                print(_command_help())
            while True:
                try:
                    command_text = input("federate> ").strip()
                except EOFError:
                    break
                if not command_text:
                    continue
                result = _run_command(session, command_text)
                if result is None:
                    continue
                results.append({"command": command_text, **result})
                _emit_result(result, json_output=config.json_output)
                if result.get("exit_requested"):
                    break
        else:
            parser.error("no commands provided")
    finally:
        session.close()

    if config.json_output:
        summary = {
            "tool": "federate-cli",
            "edition": config.edition,
            "backend": config.backend,
            "transport": _jsonable(session._transport_options().get("transport")),
            "results": results,
            "final_status": session.status(),
        }
        json.dump(_jsonable(summary), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
