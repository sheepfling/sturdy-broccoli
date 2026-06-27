"""FastAPI RTI Bridge API contract and bounded RTIambassador proxy surface."""
from __future__ import annotations

import importlib
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from hla.backends.common import lower_camel_to_snake
from hla.rti1516e.raw_api import API_METADATA


FEDERATE_SERVICE_CONTRACT_VERSION = "1.0.0"
FEDERATE_SERVICE_NAME = "federate-service"


def _render_rti_bridge_landing_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RTI Bridge API</title>
  <style>
    :root {
      --bg: linear-gradient(180deg, #f7f0e6, #eaf0ec);
      --panel: rgba(255,255,255,0.9);
      --ink: #16232c;
      --muted: #5d6c75;
      --line: rgba(22,35,44,0.10);
      --accent: #0e6671;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font: 15px/1.55 "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    main { max-width: 1120px; margin: 0 auto; padding: 28px; }
    .hero, .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 16px 38px rgba(18,32,43,0.06);
    }
    .hero { padding: 24px; margin-bottom: 18px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
    .card { padding: 18px; }
    .kicker {
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 8px;
    }
    h1, h2 { margin-top: 0; }
    code {
      background: rgba(14,102,113,0.08);
      border-radius: 6px;
      padding: 2px 6px;
    }
    a { color: var(--accent); text-decoration: none; font-weight: 600; }
    a:hover { text-decoration: underline; }
    .muted { color: var(--muted); }
    @media (max-width: 720px) {
      main { padding: 18px 14px 28px; }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="kicker">HLA Studio Surface</div>
      <h1>RTI Bridge API</h1>
      <p class="muted"><strong>Alias:</strong> <code>federate-service</code> remains the tool and service identifier.</p>
      <p>Bounded HTTP bridge for canonical RTIambassador-style operations, session lifecycle control, and contract inspection.</p>
    </section>
    <section class="grid">
      <article class="card">
        <div class="kicker">Docs</div>
        <h2>Interactive Contract Docs</h2>
        <p>Swagger UI for the typed bridge routes and request models.</p>
        <p><a href="/docs">Open Swagger docs</a></p>
      </article>
      <article class="card">
        <div class="kicker">Contract</div>
        <h2>Generated Interface Contract</h2>
        <p>Metadata-derived RTIambassador and FederateAmbassador contract JSON.</p>
        <p><a href="/api/contract">Open contract JSON</a></p>
      </article>
      <article class="card">
        <div class="kicker">Sessions</div>
        <h2>Session Control Surface</h2>
        <p>Create, inspect, invoke, and remove bounded bridge sessions.</p>
        <p><a href="/api/sessions">Open sessions endpoint</a></p>
      </article>
      <article class="card">
        <div class="kicker">Health</div>
        <h2>Bridge Status</h2>
        <p>Quick health and active session count for operator checks.</p>
        <p><a href="/api/health">Open health endpoint</a></p>
      </article>
    </section>
  </main>
</body>
</html>
"""

_SUPPORTED_METHOD_ARGUMENTS: dict[str, tuple[str, ...]] = {
    "connect": (),
    "disconnect": (),
    "createFederationExecution": (
        "federationExecutionName",
        "fomModules",
        "logicalTimeImplementationName",
    ),
    "joinFederationExecution": (
        "federateName",
        "federateType",
        "federationExecutionName",
    ),
    "publishObjectClassAttributes": ("className", "attributeNames"),
    "subscribeObjectClassAttributes": ("className", "attributeNames"),
    "publishInteractionClass": ("className",),
    "subscribeInteractionClass": ("className",),
    "registerObjectInstance": ("className", "instanceName"),
    "updateAttributeValues": ("instanceName", "attributeValues"),
    "sendInteraction": ("className", "parameterValues"),
    "evokeMultipleCallbacks": ("minimumSeconds", "maximumSeconds"),
    "resignFederationExecution": ("resignAction",),
    "destroyFederationExecution": ("federationExecutionName",),
}

_SUPPORTED_METHOD_NOTES: dict[str, list[str]] = {
    "connect": [
        "The service owns the internal FederateAmbassador callback object.",
        "HTTP callers do not pass federateReference or callbackModel directly.",
    ],
    "createFederationExecution": [
        "The HTTP binding accepts resolved FOM module paths or URLs as fomModules.",
        "For 2010 sessions the logical time implementation is ignored by the bounded session helper.",
    ],
    "joinFederationExecution": [
        "Use kwargs for overload-stable invocation because the Java overload set is ambiguous positionally.",
    ],
    "publishObjectClassAttributes": [
        "The HTTP binding resolves class and attribute handles from FOM names inside the session.",
    ],
    "subscribeObjectClassAttributes": [
        "The HTTP binding resolves class and attribute handles from FOM names inside the session.",
    ],
    "publishInteractionClass": [
        "The HTTP binding resolves the interaction class handle from the provided className.",
    ],
    "subscribeInteractionClass": [
        "The HTTP binding resolves the interaction class handle from the provided className.",
    ],
    "registerObjectInstance": [
        "The HTTP binding resolves the object class handle from the provided className.",
    ],
    "updateAttributeValues": [
        "The HTTP binding accepts string attribute values and encodes them as UTF-8 for the bounded session helper.",
    ],
    "sendInteraction": [
        "The HTTP binding accepts string parameter values and encodes them as UTF-8 for the bounded session helper.",
    ],
    "evokeMultipleCallbacks": [
        "Callbacks remain internal to the service session and are exposed through session status snapshots.",
    ],
    "resignFederationExecution": [
        "The bounded helper accepts the Java enum member name, for example NO_ACTION.",
    ],
}

_PARAM_SPLIT_RE = re.compile(r"\s*,\s*")


class ContractParameter(BaseModel):
    name: str
    python_alias: str
    type_name: str
    required: bool


class ContractOverload(BaseModel):
    language: str | None = None
    return_type: str | None = None
    params: str = ""
    throws: list[str] = Field(default_factory=list)
    service: str | None = None
    group: str | None = None
    source_file: str | None = None
    source_line: int | None = None


class MethodSupport(BaseModel):
    execution_status: Literal["supported", "metadata-only"]
    http_argument_names: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class MethodContract(BaseModel):
    method_name: str
    python_alias: str
    canonical_return_type: str | None = None
    minimum_required_parameters: int
    canonical_parameters: list[ContractParameter] = Field(default_factory=list)
    overload_count: int
    java_overload_count: int
    service: str | None = None
    group: str | None = None
    overloads: list[ContractOverload] = Field(default_factory=list)
    support: MethodSupport


class InterfaceContract(BaseModel):
    interface_name: str
    method_count: int
    methods: dict[str, MethodContract]


class FederateServiceContract(BaseModel):
    service: str
    contract_version: str
    generated_from: str
    interfaces: dict[str, InterfaceContract]


class HealthResponse(BaseModel):
    service: str
    status: str
    contract_version: str
    active_sessions: int


class SessionCreateRequest(BaseModel):
    edition: Literal["2010", "2025"] = "2010"
    backend: str | None = None
    federation_name: str | None = None
    federate_name: str = "FederateService"
    federate_type: str = "service"
    fom_modules: list[str] = Field(default_factory=list)
    logical_time_implementation: str | None = None
    transport_kind: str | None = None
    transport_target: str | None = None


class InvokeRequest(BaseModel):
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class SessionEnvelope(BaseModel):
    session_id: str
    created_at: str
    support_contract_version: str
    session: dict[str, Any]


class SessionListResponse(BaseModel):
    sessions: list[SessionEnvelope]


class InvokeResponse(BaseModel):
    session_id: str
    method_name: str
    execution_status: str
    result: dict[str, Any]
    session: dict[str, Any]


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
    if hasattr(value, "value"):
        return getattr(value, "value")
    if hasattr(value, "name"):
        return getattr(value, "name")
    return repr(value)


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / "scripts" / "tools_federate_cli.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root for federate service bootstrap.")


def _bootstrap_repo_root() -> Path:
    repo_root = _find_repo_root()
    root_text = str(repo_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return repo_root


def _load_federate_cli_module() -> Any:
    _bootstrap_repo_root()
    return importlib.import_module("scripts.tools_federate_cli")


def _split_java_params(params: str) -> list[str]:
    cleaned = params.strip()
    cleaned = cleaned.split(") const", 1)[0]
    cleaned = cleaned.split(") throw", 1)[0]
    if not cleaned:
        return []
    return [part.strip() for part in _PARAM_SPLIT_RE.split(cleaned) if part.strip()]


def _param_required(param_decl: str) -> bool:
    return "=" not in param_decl


def _param_name(param_decl: str) -> str:
    cleaned = param_decl.split("=", 1)[0].strip()
    return cleaned.split()[-1].replace("...", "")


def _param_type(param_decl: str) -> str:
    cleaned = param_decl.split("=", 1)[0].strip()
    parts = cleaned.split()
    if len(parts) <= 1:
        return "object"
    return " ".join(parts[:-1]).replace("&", "").replace("const ", "").replace(" const", "").strip()


def _canonical_java_overloads(method_overloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    java_overloads = [row for row in method_overloads if row.get("language") == "java"]
    return java_overloads or method_overloads


def _canonical_parameters(method_name: str, method_overloads: list[dict[str, Any]]) -> tuple[list[ContractParameter], int, str | None]:
    overloads = _canonical_java_overloads(method_overloads)
    parsed = [_split_java_params(str(row.get("params") or "")) for row in overloads]
    longest = max(parsed, key=len, default=[])
    required_counts = [sum(1 for part in params if _param_required(part)) for params in parsed]
    minimum_required = min(required_counts, default=0)
    return_type = str(overloads[0].get("return_type")) if overloads else None
    params: list[ContractParameter] = []
    for index, decl in enumerate(longest):
        source_name = _param_name(decl)
        params.append(
            ContractParameter(
                name=source_name,
                python_alias=lower_camel_to_snake(source_name),
                type_name=_param_type(decl),
                required=index < minimum_required,
            )
        )
    return params, minimum_required, return_type


def _method_support(method_name: str) -> MethodSupport:
    if method_name in _SUPPORTED_METHOD_ARGUMENTS:
        return MethodSupport(
            execution_status="supported",
            http_argument_names=list(_SUPPORTED_METHOD_ARGUMENTS[method_name]),
            notes=_SUPPORTED_METHOD_NOTES.get(method_name, []),
        )
    return MethodSupport(execution_status="metadata-only")


def _build_interface_contract(interface_name: str) -> InterfaceContract:
    method_rows = API_METADATA[interface_name]
    methods: dict[str, MethodContract] = {}
    for method_name, overload_rows in method_rows.items():
        canonical_parameters, minimum_required, return_type = _canonical_parameters(method_name, overload_rows)
        java_overload_count = sum(1 for row in overload_rows if row.get("language") == "java")
        methods[method_name] = MethodContract(
            method_name=method_name,
            python_alias=lower_camel_to_snake(method_name),
            canonical_return_type=return_type,
            minimum_required_parameters=minimum_required,
            canonical_parameters=canonical_parameters,
            overload_count=len(overload_rows),
            java_overload_count=java_overload_count,
            service=next((str(row.get("service")) for row in overload_rows if row.get("service")), None),
            group=next((str(row.get("group")) for row in overload_rows if row.get("group")), None),
            overloads=[ContractOverload.model_validate(row) for row in overload_rows],
            support=_method_support(method_name) if interface_name == "RTIambassador" else MethodSupport(execution_status="metadata-only"),
        )
    return InterfaceContract(
        interface_name=interface_name,
        method_count=len(methods),
        methods=methods,
    )


@lru_cache(maxsize=1)
def build_federate_service_contract() -> FederateServiceContract:
    return FederateServiceContract(
        service=FEDERATE_SERVICE_NAME,
        contract_version=FEDERATE_SERVICE_CONTRACT_VERSION,
        generated_from="hla.rti1516e.raw_api.API_METADATA",
        interfaces={
            "RTIambassador": _build_interface_contract("RTIambassador"),
            "FederateAmbassador": _build_interface_contract("FederateAmbassador"),
        },
    )


@dataclass(slots=True)
class _ManagedSession:
    session_id: str
    created_at: str
    session: Any


@dataclass(slots=True)
class FederateServiceControl:
    sessions: dict[str, _ManagedSession] = field(default_factory=dict)

    def create_session(self, request: SessionCreateRequest) -> SessionEnvelope:
        federate_cli = _load_federate_cli_module()
        session_id = uuid.uuid4().hex[:12]
        edition = request.edition
        backend = request.backend or ("python1516_2025" if edition == "2025" else "python1516e")
        federation_name = request.federation_name or f"federate-service-{edition}-{session_id}"
        logical_time_implementation = request.logical_time_implementation or "HLAinteger64Time"
        config = federate_cli.SessionConfig(
            edition=edition,
            backend=backend,
            federation_name=federation_name,
            federate_name=request.federate_name,
            federate_type=request.federate_type,
            fom_modules=tuple(request.fom_modules),
            logical_time_implementation=logical_time_implementation,
            transport_kind=request.transport_kind,
            transport_target=request.transport_target,
            json_output=False,
        )
        session = federate_cli.InteractiveFederateSession(config=config)
        created_at = datetime.now(timezone.utc).isoformat()
        managed = _ManagedSession(session_id=session_id, created_at=created_at, session=session)
        self.sessions[session_id] = managed
        return self._envelope(managed)

    def _require(self, session_id: str) -> _ManagedSession:
        managed = self.sessions.get(session_id)
        if managed is None:
            raise KeyError(session_id)
        return managed

    def _envelope(self, managed: _ManagedSession) -> SessionEnvelope:
        snapshot = managed.session.status()
        return SessionEnvelope(
            session_id=managed.session_id,
            created_at=managed.created_at,
            support_contract_version=FEDERATE_SERVICE_CONTRACT_VERSION,
            session=_jsonable(snapshot["session"]),
        )

    def list_sessions(self) -> SessionListResponse:
        return SessionListResponse(sessions=[self._envelope(managed) for managed in self.sessions.values()])

    def session(self, session_id: str) -> SessionEnvelope:
        return self._envelope(self._require(session_id))

    def delete_session(self, session_id: str) -> SessionEnvelope:
        managed = self._require(session_id)
        managed.session.close()
        envelope = self._envelope(managed)
        self.sessions.pop(session_id, None)
        return envelope

    def invoke(self, session_id: str, method_name: str, request: InvokeRequest) -> InvokeResponse:
        if method_name not in API_METADATA["RTIambassador"]:
            raise KeyError(method_name)
        support = _method_support(method_name)
        if support.execution_status != "supported":
            raise ValueError(f"{method_name} is metadata-only in the bounded federate service.")
        managed = self._require(session_id)
        result = _invoke_supported_method(managed.session, method_name, request)
        return InvokeResponse(
            session_id=session_id,
            method_name=method_name,
            execution_status=support.execution_status,
            result=_jsonable(result),
            session=_jsonable(managed.session.status()["session"]),
        )


def _coerce_mapping(name: str, value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return {str(key): str(item) for key, item in value.items()}


def _coerce_name_list(name: str, value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be a JSON array.")
    return tuple(str(item) for item in value)


def _resolve_join_kwargs(args: list[Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    if kwargs:
        return dict(kwargs)
    if len(args) == 2:
        return {
            "federateType": str(args[0]),
            "federationExecutionName": str(args[1]),
        }
    if len(args) == 3:
        return {
            "federateName": str(args[0]),
            "federateType": str(args[1]),
            "federationExecutionName": str(args[2]),
        }
    raise ValueError("joinFederationExecution expects kwargs or 2/3 positional arguments.")


def _resolve_named_kwargs(method_name: str, expected_names: tuple[str, ...], args: list[Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    if kwargs:
        return dict(kwargs)
    if len(args) > len(expected_names):
        raise ValueError(f"{method_name} received too many positional arguments.")
    return {name: args[index] for index, name in enumerate(expected_names)}


def _invoke_supported_method(session: Any, method_name: str, request: InvokeRequest) -> dict[str, Any]:
    kwargs = dict(request.kwargs)
    args = list(request.args)
    if method_name == "connect":
        return session.connect()
    if method_name == "disconnect":
        return session.disconnect()
    if method_name == "createFederationExecution":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        federation_name = named.get("federationExecutionName")
        fom_modules = tuple(str(item) for item in named.get("fomModules", []) or ())
        logical_time = named.get("logicalTimeImplementationName")
        return session.create(
            federation_name=None if federation_name is None else str(federation_name),
            fom_modules=fom_modules,
            logical_time_implementation=None if logical_time is None else str(logical_time),
        )
    if method_name == "joinFederationExecution":
        named = _resolve_join_kwargs(args, kwargs)
        return session.join(
            federate_name=None if named.get("federateName") is None else str(named["federateName"]),
            federate_type=None if named.get("federateType") is None else str(named["federateType"]),
            federation_name=None if named.get("federationExecutionName") is None else str(named["federationExecutionName"]),
        )
    if method_name == "publishObjectClassAttributes":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.publish_object(
            str(named["className"]),
            _coerce_name_list("attributeNames", named["attributeNames"]),
        )
    if method_name == "subscribeObjectClassAttributes":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.subscribe_object(
            str(named["className"]),
            _coerce_name_list("attributeNames", named["attributeNames"]),
        )
    if method_name == "publishInteractionClass":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.publish_interaction(str(named["className"]))
    if method_name == "subscribeInteractionClass":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.subscribe_interaction(str(named["className"]))
    if method_name == "registerObjectInstance":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.register_object(str(named["className"]), str(named["instanceName"]))
    if method_name == "updateAttributeValues":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.update_object(
            str(named["instanceName"]),
            _coerce_mapping("attributeValues", named["attributeValues"]),
        )
    if method_name == "sendInteraction":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.send_interaction(
            str(named["className"]),
            _coerce_mapping("parameterValues", named["parameterValues"]),
        )
    if method_name == "evokeMultipleCallbacks":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.evoke(
            float(named.get("minimumSeconds", 0.0) or 0.0),
            float(named.get("maximumSeconds", 0.0) or 0.0),
        )
    if method_name == "resignFederationExecution":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.resign(str(named.get("resignAction", "NO_ACTION")))
    if method_name == "destroyFederationExecution":
        named = _resolve_named_kwargs(method_name, _SUPPORTED_METHOD_ARGUMENTS[method_name], args, kwargs)
        return session.destroy(None if named.get("federationExecutionName") is None else str(named["federationExecutionName"]))
    raise ValueError(f"Unsupported bounded method: {method_name}")


def create_federate_service_fastapi_app(control: FederateServiceControl | None = None) -> FastAPI:
    app = FastAPI(
        title="RTI Bridge API",
        version=FEDERATE_SERVICE_CONTRACT_VERSION,
        description="Canonical RTIambassador-named FastAPI contract with bounded execution adapters.",
    )
    active_control = control or FederateServiceControl()

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            service=FEDERATE_SERVICE_NAME,
            status="ok",
            contract_version=FEDERATE_SERVICE_CONTRACT_VERSION,
            active_sessions=len(active_control.sessions),
        )

    @app.get("/api/contract", response_model=FederateServiceContract)
    async def contract() -> FederateServiceContract:
        return build_federate_service_contract()

    @app.get("/api/contract/{interface_name}", response_model=InterfaceContract)
    async def contract_interface(interface_name: str) -> InterfaceContract:
        contract_model = build_federate_service_contract()
        interface = contract_model.interfaces.get(interface_name)
        if interface is None:
            raise HTTPException(status_code=404, detail=f"Unknown interface: {interface_name}")
        return interface

    @app.get("/api/contract/{interface_name}/{method_name}", response_model=MethodContract)
    async def contract_method(interface_name: str, method_name: str) -> MethodContract:
        contract_model = build_federate_service_contract()
        interface = contract_model.interfaces.get(interface_name)
        if interface is None:
            raise HTTPException(status_code=404, detail=f"Unknown interface: {interface_name}")
        method = interface.methods.get(method_name)
        if method is None:
            raise HTTPException(status_code=404, detail=f"Unknown method on {interface_name}: {method_name}")
        return method

    @app.post("/api/sessions", response_model=SessionEnvelope)
    async def create_session(request: SessionCreateRequest) -> SessionEnvelope:
        try:
            return active_control.create_session(request)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=repr(exc)) from exc

    @app.get("/api/sessions", response_model=SessionListResponse)
    async def list_sessions() -> SessionListResponse:
        return active_control.list_sessions()

    @app.get("/api/sessions/{session_id}", response_model=SessionEnvelope)
    async def get_session(session_id: str) -> SessionEnvelope:
        try:
            return active_control.session(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}") from exc

    @app.delete("/api/sessions/{session_id}", response_model=SessionEnvelope)
    async def delete_session(session_id: str) -> SessionEnvelope:
        try:
            return active_control.delete_session(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}") from exc

    @app.post("/api/sessions/{session_id}/invoke/{method_name}", response_model=InvokeResponse)
    async def invoke(session_id: str, method_name: str, request: InvokeRequest) -> InvokeResponse:
        try:
            return active_control.invoke(session_id, method_name, request)
        except KeyError as exc:
            detail = f"Unknown session: {session_id}" if exc.args == (session_id,) else f"Unknown method: {method_name}"
            raise HTTPException(status_code=404, detail=detail) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=repr(exc)) from exc

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return _render_rti_bridge_landing_html()

    return app


def build_federate_service_fastapi_app() -> FastAPI:
    return create_federate_service_fastapi_app(FederateServiceControl())


def federate_service_contract_json(indent: int = 2) -> str:
    return json.dumps(build_federate_service_contract().model_dump(mode="json"), indent=indent, sort_keys=True) + "\n"


__all__ = [
    "FEDERATE_SERVICE_CONTRACT_VERSION",
    "FEDERATE_SERVICE_NAME",
    "FederateServiceControl",
    "FederateServiceContract",
    "HealthResponse",
    "InvokeRequest",
    "InvokeResponse",
    "InterfaceContract",
    "MethodContract",
    "SessionCreateRequest",
    "SessionEnvelope",
    "SessionListResponse",
    "build_federate_service_contract",
    "build_federate_service_fastapi_app",
    "create_federate_service_fastapi_app",
    "federate_service_contract_json",
]
