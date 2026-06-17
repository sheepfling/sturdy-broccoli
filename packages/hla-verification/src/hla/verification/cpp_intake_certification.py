"""C++ RTI intake and standard-shim core certification evidence."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from hla.backends.cpp_shim.cpp_capsule_runtime import smoke_capsule
from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest, generate_cpp_sdk_capsule

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
    "evokeCallback",
    "evokeMultipleCallbacks",
    "resignFederationExecution",
    "destroyFederationExecution",
    "disconnect",
}

CORE_SCENARIO_GREEN_STATUSES = {"core-green", "core-exchange-green"}


@dataclass(frozen=True, slots=True)
class CppRtiCoreCertificationReport:
    edition: str
    transport: str
    route: str
    artifact: dict[str, Any]
    discovery: dict[str, Any] | None = None
    capsule_dir: str | None = None
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
    runtime: dict[str, Any] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slug(value: str, edition: str, transport: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "cpp-rti"
    return f"{slug}-{edition}-{transport}"


def _trace_event_names(trace: Sequence[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(str(item.get("event", "")) for item in trace)


def _trace_status(edition: str, trace: Sequence[dict[str, Any]]) -> tuple[str, tuple[str, ...]]:
    required = REQUIRED_2010_TRACE_EVENTS if edition == "2010" else REQUIRED_2025_TRACE_EVENTS
    missing = tuple(sorted(required - set(_trace_event_names(trace))))
    return ("trace-green" if not missing else "core-green", missing)


def certify_cpp_standard_core(edition: str, transport: str) -> CppRtiCoreCertificationReport:
    route = f"cpp-standard-{edition}-{transport}"
    artifact = {"kind": "cpp-standard-shim", "name": f"hla-x-cpp-standard-{edition}", "edition": edition, "route": route}
    try:
        if edition == "2010":
            from hla.verification.rosetta_mvp import run_standard_2010_exchange_trace

            evidence = run_standard_2010_exchange_trace(route)
        elif edition == "2025":
            from hla.verification.rosetta_mvp import run_standard_2025_lifecycle_trace

            evidence = run_standard_2025_lifecycle_trace(route)
        else:
            raise ValueError("C++ certification edition must be one of: 2010, 2025")
        trace = tuple(evidence.get("trace", ()))
        status, missing = _trace_status(edition, trace)
        events = set(_trace_event_names(trace))
        callback_status = "failed"
        if edition == "2010" and {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction"} <= events:
            callback_status = "callback-green"
        elif edition == "2025" and {"evokeCallback", "evokeMultipleCallbacks"} <= events:
            callback_status = "callback-poll-green"
        connect_green = "connect" in events and "disconnect" in events
        return CppRtiCoreCertificationReport(
            edition=edition,
            transport=transport,
            route=route,
            artifact=artifact,
            connect_status="connect-green" if connect_green else "failed",
            callback_status=callback_status,
            core_scenario_status="core-exchange-green" if evidence.get("status") in CORE_SCENARIO_GREEN_STATUSES else "failed",
            trace_comparison_status=status,
            status=status,
            trace=trace,
            missing_trace_events=missing,
            unsupported_services=("Full vendor C++ SDK service invocation awaits generated runtime capsule adapter.",),
        )
    except Exception as exc:
        return CppRtiCoreCertificationReport(
            edition=edition,
            transport=transport,
            route=route,
            artifact=artifact,
            status="failed",
            connect_status="failed",
            callback_status="failed",
            core_scenario_status="failed",
            trace_comparison_status="failed",
            errors=(f"C++ standard core certification failed: {exc}",),
        )


def certify_cpp_sdk_core(request: CppSdkIntakeRequest, output_root: str | Path) -> CppRtiCoreCertificationReport:
    discovery = generate_cpp_sdk_capsule(request, output_root)
    artifact = discovery.artifact
    if discovery.errors:
        return CppRtiCoreCertificationReport(
            edition=discovery.edition,
            transport=discovery.transport,
            route=discovery.route,
            artifact=artifact,
            discovery=discovery.to_json_dict(),
            capsule_dir=discovery.capsule_dir,
            status="failed",
            errors=discovery.errors,
            warnings=discovery.warnings,
        )
    runtime = smoke_capsule(discovery.capsule_dir, discovery.transport, timeout_seconds=request.timeout_seconds)
    if runtime.errors:
        return CppRtiCoreCertificationReport(
            edition=discovery.edition,
            transport=discovery.transport,
            route=discovery.route,
            artifact=artifact,
            discovery=discovery.to_json_dict(),
            capsule_dir=discovery.capsule_dir,
            status="failed",
            errors=runtime.errors,
            warnings=discovery.warnings,
            runtime=runtime.to_json_dict(),
        )
    return CppRtiCoreCertificationReport(
        edition=discovery.edition,
        transport=discovery.transport,
        route=discovery.route,
        artifact=artifact,
        discovery=discovery.to_json_dict(),
        capsule_dir=discovery.capsule_dir,
        connect_status="connect-green",
        callback_status="callback-poll-green",
        core_scenario_status="blocked",
        trace_comparison_status="blocked",
        status="adapter-smoke-green",
        trace=runtime.trace,
        unsupported_services=runtime.unsupported_services,
        warnings=discovery.warnings,
        blocked_reason="full core scenario through generated C++ SDK runtime capsule is not implemented yet",
        runtime=runtime.to_json_dict(),
    )


def smoke_cpp_sdk_capsule(request: CppSdkIntakeRequest, output_root: str | Path) -> CppRtiCoreCertificationReport:
    discovery = generate_cpp_sdk_capsule(request, output_root)
    artifact = discovery.artifact
    if discovery.errors:
        return CppRtiCoreCertificationReport(
            edition=discovery.edition,
            transport=discovery.transport,
            route=discovery.route,
            artifact=artifact,
            discovery=discovery.to_json_dict(),
            capsule_dir=discovery.capsule_dir,
            status="failed",
            errors=discovery.errors,
            warnings=discovery.warnings,
        )
    runtime = smoke_capsule(discovery.capsule_dir, discovery.transport, timeout_seconds=request.timeout_seconds)
    return CppRtiCoreCertificationReport(
        edition=discovery.edition,
        transport=discovery.transport,
        route=discovery.route,
        artifact=artifact,
        discovery=discovery.to_json_dict(),
        capsule_dir=discovery.capsule_dir,
        connect_status="connect-green" if runtime.checks.get("connect_disconnect") == "pass" else "failed",
        callback_status="callback-poll-green" if runtime.checks.get("callback_poll") == "pass" else "failed",
        core_scenario_status="not-run",
        trace_comparison_status="not-run",
        status=runtime.status,
        trace=runtime.trace,
        unsupported_services=runtime.unsupported_services,
        errors=runtime.errors,
        warnings=discovery.warnings + runtime.warnings,
        runtime=runtime.to_json_dict(),
    )


def render_certification_markdown(report: CppRtiCoreCertificationReport) -> str:
    def verdict(status: str) -> str:
        return "PASS" if status.endswith("-green") or status == "trace-green" else status.upper()

    lines = [
        f"# C++ RTI Core Certification: {report.edition} {report.transport}",
        "",
        f"- Status: `{report.status}`",
        f"- Artifact: `{report.artifact.get('name')}`",
        f"- Route: `{report.route}`",
        f"- Connect/disconnect: {verdict(report.connect_status)}",
        f"- Callbacks: {verdict(report.callback_status)}",
        f"- Core scenario: {verdict(report.core_scenario_status)}",
        f"- Trace comparison: {verdict(report.trace_comparison_status)}",
    ]
    if report.capsule_dir:
        lines.append(f"- Capsule directory: `{report.capsule_dir}`")
    if report.blocked_reason:
        lines.append(f"- Blocked reason: {report.blocked_reason}")
    lines.extend(["", "## Missing Trace Events", ""])
    lines.extend(f"- `{event}`" for event in report.missing_trace_events)
    if not report.missing_trace_events:
        lines.append("- none")
    lines.extend(["", "## Unsupported Services", ""])
    lines.extend(f"- {item}" for item in report.unsupported_services)
    if not report.unsupported_services:
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


def write_certification_reports(report: CppRtiCoreCertificationReport, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(report.artifact.get("name") or "cpp-rti"), report.edition, report.transport)
    json_path = output / f"{slug}.json"
    md_path = output / f"{slug}.md"
    json_path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_certification_markdown(report), encoding="utf-8")
    return json_path, md_path


__all__ = [
    "CppRtiCoreCertificationReport",
    "certify_cpp_sdk_core",
    "certify_cpp_standard_core",
    "render_certification_markdown",
    "smoke_cpp_sdk_capsule",
    "write_certification_reports",
]
