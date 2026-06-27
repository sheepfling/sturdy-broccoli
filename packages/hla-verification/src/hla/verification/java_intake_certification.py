"""Java RTI intake core certification evidence."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence, cast

from hla.bridges.java.common.java_intake import (
    JavaRtiIntakeRequest,
    discover_java_rti_jar,
    java_api_profile,
)
from hla.rti import RTIBackendSpec

REQUIRED_2010_TRACE_EVENTS = {
    "connect",
    "createFederationExecution",
    "joinFederationExecution",
    "publishSubscribeObject",
    "discoverObjectInstance",
    "reflectAttributeValues",
    "publishSubscribeInteraction",
    "receiveInteraction",
    "timeRegulationEnabled",
    "timeConstrainedEnabled",
    "timeAdvanceGrant",
    "destroyFederationExecution",
    "disconnect",
}

REQUIRED_2025_TRACE_EVENTS = {
    "getHLAversion",
    "connect",
    "createFederationExecution",
    "joinFederationExecution",
    "resolveFomHandles",
    "changeDefaultAttributeTransportationType",
    "changeDefaultAttributeOrderType",
    "registerObjectInstance",
    "unconditionalAttributeOwnershipDivestiture",
    "attributeOwnershipAcquisitionIfAvailable",
    "attributeIsNotOwned",
    "attributeOwnershipAcquisitionNotification",
    "getTimeFactory",
    "timeAdvanceRequest",
    "timeAdvanceGrant",
    "serializeMOMServiceReport",
    "resignFederationExecution",
    "destroyFederationExecution",
    "disconnect",
}
REQUIRED_202X_TRACE_EVENTS = REQUIRED_2025_TRACE_EVENTS

CORE_SCENARIO_GREEN_STATUSES = {"core-green", "core-exchange-green"}
JAVA_2025_STANDARD_FACTORY = "Java 2025 Standard Shim"


@dataclass(frozen=True, slots=True)
class JavaRtiCoreCertificationReport:
    edition: str
    bridge: str
    classpath: tuple[str, ...]
    factory_requested: str | None
    discovery: dict[str, Any]
    connect_status: str = "not-run"
    callback_status: str = "not-run"
    core_scenario_status: str = "not-run"
    trace_comparison_status: str = "not-run"
    status: str = "planned"
    trace: tuple[dict[str, Any], ...] = ()
    missing_trace_events: tuple[str, ...] = ()
    unsupported_services: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    blocked_reason: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slug(value: str | None, edition: str, bridge: str) -> str:
    text = value or "java-rti"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower() or "java-rti"
    return f"{slug}-{edition}-{bridge}"


def _trace_event_names(trace: Sequence[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(str(item.get("event", "")) for item in trace)


def _status_from_trace(edition: str, trace: Sequence[dict[str, Any]]) -> tuple[str, tuple[str, ...]]:
    events = set(_trace_event_names(trace))
    if edition == "2010":
        required = REQUIRED_2010_TRACE_EVENTS
    else:
        required = REQUIRED_202X_TRACE_EVENTS if edition == "202X" else REQUIRED_2025_TRACE_EVENTS
    missing = tuple(sorted(required - events))
    return ("trace-green" if not missing else "core-green", missing)


def certify_java_rti_core(request: JavaRtiIntakeRequest) -> JavaRtiCoreCertificationReport:
    """Run discovery and the supported Java RTI intake core certification lane."""

    profile = java_api_profile(request.edition)
    discovery = discover_java_rti_jar(request)
    discovery_payload = discovery.to_json_dict()

    if discovery.errors:
        return JavaRtiCoreCertificationReport(
            edition=profile.edition,
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            discovery=discovery_payload,
            status=discovery.status,
            errors=discovery.errors,
            warnings=discovery.warnings,
        )

    if profile.edition == "2025":
        if request.rti_factory_name != JAVA_2025_STANDARD_FACTORY:
            return JavaRtiCoreCertificationReport(
                edition=profile.edition,
                bridge=request.bridge,
                classpath=request.classpath,
                factory_requested=request.rti_factory_name,
                discovery=discovery_payload,
                connect_status="blocked",
                callback_status="blocked",
                core_scenario_status="blocked",
                trace_comparison_status="blocked",
                status="behavior-blocked",
                warnings=discovery.warnings,
                blocked_reason="generic/vendor Java 2025 RTI invocation is not implemented yet",
            )
        try:
            from hla.verification.shim_route_evidence import run_standard_2025_runtime_capability_trace

            evidence = run_standard_2025_runtime_capability_trace(f"java-standard-2025-{request.bridge}")
            trace = tuple(evidence.get("trace", ()))
            trace_status, missing = _status_from_trace(profile.edition, trace)
            events = set(_trace_event_names(trace))
            callback_green = {"attributeIsNotOwned", "attributeOwnershipAcquisitionNotification", "timeAdvanceGrant"} <= events
            connect_green = "connect" in events and "disconnect" in events
            return JavaRtiCoreCertificationReport(
                edition=profile.edition,
                bridge=request.bridge,
                classpath=request.classpath,
                factory_requested=request.rti_factory_name,
                discovery=discovery_payload,
                connect_status="connect-green" if connect_green else "failed",
                callback_status="callback-runtime-green" if callback_green else "failed",
                core_scenario_status="runtime-capability-green" if evidence.get("status") == "trace-green" else "failed",
                trace_comparison_status=trace_status,
                status=trace_status,
                trace=trace,
                missing_trace_events=missing,
                unsupported_services=(),
                warnings=discovery.warnings,
            )
        except Exception as exc:
            return JavaRtiCoreCertificationReport(
                edition=profile.edition,
                bridge=request.bridge,
                classpath=request.classpath,
                factory_requested=request.rti_factory_name,
                discovery=discovery_payload,
                connect_status="blocked",
                callback_status="blocked",
                core_scenario_status="blocked",
                trace_comparison_status="blocked",
                status="behavior-blocked",
                errors=(f"Java 2025 standard runtime capability trace could not run: {exc}",),
                warnings=discovery.warnings,
                blocked_reason="Java 2025 standard shim runtime evidence requires a built standard shim jar",
            )

    if profile.edition == "202X":
        return JavaRtiCoreCertificationReport(
            edition=profile.edition,
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            discovery=discovery_payload,
            connect_status="blocked",
            callback_status="blocked",
            core_scenario_status="blocked",
            trace_comparison_status="blocked",
            status="behavior-blocked",
            warnings=discovery.warnings,
            blocked_reason="vendor Java 202X RTI behavior certification is not implemented yet",
        )

    if profile.edition != "2010":
        return JavaRtiCoreCertificationReport(
            edition=profile.edition,
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            discovery=discovery_payload,
            connect_status="blocked",
            callback_status="blocked",
            core_scenario_status="blocked",
            trace_comparison_status="blocked",
            status="behavior-blocked",
            warnings=discovery.warnings,
            blocked_reason=f"Java edition {profile.edition} RTI invocation is not implemented by this certification lane",
        )

    try:
        from hla.verification.shim_route_evidence import run_standard_2010_exchange_trace

        gateway = None
        gateway_port = request.gateway_port
        if request.bridge == "py4j" and gateway_port is None:
            from hla.bridges.java.common.java_runtime import discover_java_tool
            from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
            from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway

            gateway_port = cast(int, launch_gateway(
                classpath=os.pathsep.join(request.classpath),
                die_on_exit=True,
                java_path=discover_java_tool("java") or "java",
            ))
            gateway = JavaGateway(
                gateway_parameters=GatewayParameters(port=int(gateway_port)),
                callback_server_parameters=CallbackServerParameters(port=0),
            )
            reset_py4j_callback_client(gateway)
        backend = RTIBackendSpec(
            kind=f"java-2010-{request.bridge}",
            options={
                "classpath": request.classpath,
                "rti_factory_name": request.rti_factory_name,
                "local_settings_designator": request.local_settings_designator,
                "jvm_args": request.jvm_args,
                "gateway_port": gateway_port,
                "gateway": gateway,
                "shutdown_gateway_on_close": False if gateway is not None else True,
            },
        )
        try:
            evidence = run_standard_2010_exchange_trace(backend)
        finally:
            if gateway is not None:
                try:
                    gateway.shutdown()
                except Exception:
                    pass
        trace = tuple(evidence.get("trace", ()))
        trace_status, missing = _status_from_trace(profile.edition, trace)
        events = set(_trace_event_names(trace))
        callback_green = {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction"} <= events
        connect_green = "connect" in events and "disconnect" in events
        return JavaRtiCoreCertificationReport(
            edition=profile.edition,
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            discovery=discovery_payload,
            connect_status="connect-green" if connect_green else "failed",
            callback_status="callback-green" if callback_green else "failed",
            core_scenario_status="core-exchange-green" if evidence.get("status") in CORE_SCENARIO_GREEN_STATUSES else "failed",
            trace_comparison_status=trace_status,
            status=trace_status,
            trace=trace,
            missing_trace_events=missing,
            unsupported_services=(),
            warnings=discovery.warnings,
        )
    except Exception as exc:
        return JavaRtiCoreCertificationReport(
            edition=profile.edition,
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            discovery=discovery_payload,
            connect_status="failed",
            callback_status="failed",
            core_scenario_status="failed",
            trace_comparison_status="failed",
            status="failed",
            errors=(f"Core certification failed: {exc}",),
            warnings=discovery.warnings,
        )


def render_certification_markdown(report: JavaRtiCoreCertificationReport) -> str:
    discovery = report.discovery

    def verdict(status: str) -> str:
        return "PASS" if status.endswith("-green") or status == "trace-green" else status.upper()

    lines = [
        f"# Java RTI Core Certification: {report.edition} {report.bridge}",
        "",
        f"- Status: `{report.status}`",
        f"- Factory discovery: {'PASS' if discovery.get('factory_found') else 'FAIL'}",
        f"- RTI ambassador creation: {'PASS' if discovery.get('rti_ambassador_created') else 'FAIL'}",
        f"- Connect/disconnect: {verdict(report.connect_status)}",
        f"- Callbacks: {verdict(report.callback_status)}",
        f"- Core scenario: {verdict(report.core_scenario_status)}",
        f"- Trace comparison: {verdict(report.trace_comparison_status)}",
        f"- Factory requested: `{report.factory_requested or ''}`",
        f"- Factory name: `{discovery.get('factory_name') or ''}`",
        f"- Factory version: `{discovery.get('factory_version') or ''}`",
        f"- RTI ambassador class: `{discovery.get('rti_ambassador_class') or ''}`",
        f"- HLA version: `{discovery.get('hla_version') or ''}`",
    ]
    if report.blocked_reason:
        lines.append(f"- Blocked reason: {report.blocked_reason}")
    lines.extend(["", "## Missing Trace Events", ""])
    lines.extend(f"- `{event}`" for event in report.missing_trace_events)
    if not report.missing_trace_events:
        lines.append("- none")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {item}" for item in report.errors)
    if not report.errors:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {item}" for item in report.warnings)
    if not report.warnings:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_certification_reports(report: JavaRtiCoreCertificationReport, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = _slug(report.discovery.get("factory_name") or report.factory_requested, report.edition, report.bridge)
    json_path = output / f"{slug}.json"
    md_path = output / f"{slug}.md"
    json_path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_certification_markdown(report), encoding="utf-8")
    return json_path, md_path


__all__ = [
    "JavaRtiCoreCertificationReport",
    "certify_java_rti_core",
    "render_certification_markdown",
    "write_certification_reports",
]
