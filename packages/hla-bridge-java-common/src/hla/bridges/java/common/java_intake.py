"""Generic Java RTI jar intake and discovery.

This module is intentionally about intake evidence, not HLA behavior
certification. It validates classpaths, selects the edition-specific Java API
profile, probes the standard factory path, and reports what was discovered.
"""
from __future__ import annotations

import json
import importlib
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence, cast


@dataclass(frozen=True, slots=True)
class JavaApiProfile:
    edition: str
    spec_name: str
    python_package: str
    java_package: str
    factory_factory_class: str
    factory_interface: str
    rti_ambassador_interface: str
    federate_ambassador_interface: str
    callback_model_class: str


JAVA_2010 = JavaApiProfile(
    edition="2010",
    spec_name="rti1516e",
    python_package="hla.rti1516e",
    java_package="hla.rti1516e",
    factory_factory_class="hla.rti1516e.RtiFactoryFactory",
    factory_interface="hla.rti1516e.RtiFactory",
    rti_ambassador_interface="hla.rti1516e.RTIambassador",
    federate_ambassador_interface="hla.rti1516e.FederateAmbassador",
    callback_model_class="hla.rti1516e.CallbackModel",
)
JAVA_2025 = JavaApiProfile(
    edition="2025",
    spec_name="rti1516_2025",
    python_package="hla.rti1516_2025",
    java_package="hla.rti1516_2025",
    factory_factory_class="hla.rti1516_2025.RtiFactoryFactory",
    factory_interface="hla.rti1516_2025.RtiFactory",
    rti_ambassador_interface="hla.rti1516_2025.RTIambassador",
    federate_ambassador_interface="hla.rti1516_2025.FederateAmbassador",
    callback_model_class="hla.rti1516_2025.CallbackModel",
)
JAVA_202X = JavaApiProfile(
    edition="202X",
    spec_name="rti1516_202x",
    python_package="hla.rti1516_2025",
    java_package="hla.rti1516_202X",
    factory_factory_class="hla.rti1516_202X.RtiFactoryFactory",
    factory_interface="hla.rti1516_202X.RtiFactory",
    rti_ambassador_interface="hla.rti1516_202X.RTIambassador",
    federate_ambassador_interface="hla.rti1516_202X.FederateAmbassador",
    callback_model_class="hla.rti1516_202X.CallbackModel",
)

JAVA_API_PROFILES = {
    "2010": JAVA_2010,
    "rti1516e": JAVA_2010,
    "1516e": JAVA_2010,
    "2025": JAVA_2025,
    "rti1516_2025": JAVA_2025,
    "rti1516-2025": JAVA_2025,
    "202x": JAVA_202X,
    "rti1516_202x": JAVA_202X,
    "rti1516-202x": JAVA_202X,
    "hla.rti1516_202x": JAVA_202X,
}


@dataclass(frozen=True, slots=True)
class JavaRtiIntakeRequest:
    edition: str
    bridge: str
    classpath: tuple[str, ...]
    rti_factory_name: str | None = None
    local_settings_designator: str | None = None
    jvm_args: tuple[str, ...] = ()
    gateway_port: int | None = None
    timeout_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class JavaRtiIntakeReport:
    edition: str
    bridge: str
    classpath: tuple[str, ...]
    factory_requested: str | None
    factory_found: bool = False
    factory_name: str | None = None
    factory_version: str | None = None
    rti_ambassador_created: bool = False
    rti_ambassador_class: str | None = None
    rti_ambassador_interfaces: tuple[str, ...] = ()
    hla_version: str | None = None
    edition_match: bool = False
    status: str = "planned"
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors and self.status in {"ambassador-green", "factory-green", "discoverable"}

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def java_api_profile(edition: str) -> JavaApiProfile:
    key = edition.strip().lower().replace("-", "_")
    try:
        return JAVA_API_PROFILES[key]
    except KeyError as exc:
        raise ValueError("Java RTI edition must be one of: 2010, 2025, 202X") from exc


def split_classpath(value: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        parts = [part for part in re.split(r"[:]", value) if part]
    else:
        parts = [str(part) for part in value if str(part)]
    return tuple(parts)


def validate_classpath(classpath: Sequence[str]) -> tuple[Path, ...]:
    if not classpath:
        raise ValueError("Classpath is empty; provide at least one Java RTI jar or class directory")
    paths = tuple(Path(item).expanduser() for item in classpath)
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"Classpath entry does not exist: {joined}")
    return paths


def _error_report(request: JavaRtiIntakeRequest, error: str, *, status: str = "planned") -> JavaRtiIntakeReport:
    return JavaRtiIntakeReport(
        edition=java_api_profile(request.edition).edition,
        bridge=request.bridge,
        classpath=request.classpath,
        factory_requested=request.rti_factory_name,
        status=status,
        errors=(error,),
    )


def _java_class_name(value: Any) -> str | None:
    get_class = getattr(value, "getClass", None)
    if callable(get_class):
        try:
            class_info = cast(Any, get_class())
            return str(class_info.getName())
        except Exception:
            return None
    return None


def _java_interface_names(value: Any) -> tuple[str, ...]:
    get_class = getattr(value, "getClass", None)
    if not callable(get_class):
        return ()
    try:
        class_info = cast(Any, get_class())
        interfaces = class_info.getInterfaces()
    except Exception:
        return ()
    names: list[str] = []
    for item in interfaces:
        get_name = getattr(item, "getName", None)
        try:
            names.append(str(get_name() if callable(get_name) else item))
        except Exception:
            names.append(str(item))
    return tuple(sorted(names))


def _string_call(obj: Any, method_name: str) -> str | None:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return None
    try:
        return str(method())
    except Exception:
        return None


def _edition_matches(profile: JavaApiProfile, hla_version: str | None, interfaces: Iterable[str]) -> bool:
    interface_set = set(interfaces)
    if profile.rti_ambassador_interface in interface_set:
        return True
    if hla_version is None:
        return False
    return profile.edition in hla_version or profile.spec_name in hla_version


def _status(factory_found: bool, ambassador_created: bool, errors: Sequence[str]) -> str:
    if errors:
        return "planned"
    if ambassador_created:
        return "ambassador-green"
    if factory_found:
        return "factory-green"
    return "discoverable"


def discover_java_rti_jar(request: JavaRtiIntakeRequest) -> JavaRtiIntakeReport:
    """Discover a standards-shaped Java RTI jar using JPype or Py4J."""

    try:
        validate_classpath(request.classpath)
    except Exception as exc:
        return _error_report(request, str(exc))

    bridge = request.bridge.strip().lower().replace("_", "-")
    if bridge in {"jpype", "java-jpype"}:
        return _discover_jpype(request)
    if bridge in {"py4j", "java-py4j"}:
        return _discover_py4j(request)
    return _error_report(request, "Java RTI bridge must be one of: jpype, py4j")


def _discover_jpype(request: JavaRtiIntakeRequest) -> JavaRtiIntakeReport:
    profile = java_api_profile(request.edition)
    errors: list[str] = []
    warnings: list[str] = []
    factory = None
    java_rti = None
    bridge = None

    try:
        jpype_runtime = importlib.import_module("hla.bridges.java.jpype.runtime")
        JPypeBridge = getattr(jpype_runtime, "JPypeBridge")
        JPypeConfig = getattr(jpype_runtime, "JPypeConfig")

        bridge = JPypeBridge(
            JPypeConfig(
                classpath=request.classpath,
                jvm_args=request.jvm_args,
                rti_factory_name=request.rti_factory_name,
                shutdown_jvm_on_close=False,
            )
        )
        factory_factory = bridge.JClass(profile.factory_factory_class)
        try:
            factory = (
                factory_factory.getRtiFactory(request.rti_factory_name)
                if request.rti_factory_name
                else factory_factory.getRtiFactory()
            )
        except Exception as exc:
            errors.append(f"RtiFactoryFactory could not select a factory: {bridge.exception_message(exc)}")
        if factory is not None:
            try:
                java_rti = factory.getRtiAmbassador()
            except Exception as exc:
                errors.append(f"RtiFactory.getRtiAmbassador failed: {bridge.exception_message(exc)}")
    except Exception as exc:
        errors.append(f"JPype discovery failed: {exc}")

    factory_found = factory is not None
    ambassador_created = java_rti is not None
    factory_name = _string_call(factory, "rtiName") if factory is not None else None
    factory_version = _string_call(factory, "rtiVersion") if factory is not None else None
    hla_version = _string_call(java_rti, "getHLAversion") if java_rti is not None else None
    class_name = _java_class_name(java_rti) if java_rti is not None else None
    interfaces = _java_interface_names(java_rti) if java_rti is not None else ()
    edition_match = _edition_matches(profile, hla_version, interfaces)
    if ambassador_created and not edition_match:
        warnings.append(f"RTIambassador did not explicitly confirm {profile.edition} via interface or HLA version")

    return JavaRtiIntakeReport(
        edition=profile.edition,
        bridge="jpype",
        classpath=request.classpath,
        factory_requested=request.rti_factory_name,
        factory_found=factory_found,
        factory_name=factory_name,
        factory_version=factory_version,
        rti_ambassador_created=ambassador_created,
        rti_ambassador_class=class_name,
        rti_ambassador_interfaces=interfaces,
        hla_version=hla_version,
        edition_match=edition_match,
        status=_status(factory_found, ambassador_created, errors),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _jvm_attr(root: Any, dotted_name: str) -> Any:
    current = root
    for part in dotted_name.split("."):
        current = getattr(current, part)
    return current


def _discover_py4j(request: JavaRtiIntakeRequest) -> JavaRtiIntakeReport:
    profile = java_api_profile(request.edition)
    errors: list[str] = []
    warnings: list[str] = []
    factory = None
    java_rti = None
    gateway = None
    factory_name = None
    factory_version = None
    hla_version = None
    class_name = None
    interfaces: tuple[str, ...] = ()

    try:
        from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway
        from hla.bridges.java.common.py4j_support import reset_py4j_callback_client
        from hla.bridges.java.common.java_runtime import discover_java_tool

        if request.gateway_port is None:
            java_path = discover_java_tool("java") or "java"
            port = cast(int, launch_gateway(classpath=os.pathsep.join(request.classpath), die_on_exit=True, java_path=java_path))
        else:
            port = request.gateway_port
        gateway = JavaGateway(
            gateway_parameters=GatewayParameters(port=port),
            callback_server_parameters=CallbackServerParameters(port=0),
        )
        reset_py4j_callback_client(gateway)
        factory_factory = _jvm_attr(gateway.jvm, profile.factory_factory_class)
        try:
            factory = (
                factory_factory.getRtiFactory(request.rti_factory_name)
                if request.rti_factory_name
                else factory_factory.getRtiFactory()
            )
        except Exception as exc:
            errors.append(f"RtiFactoryFactory could not select a factory: {exc}")
        if factory is not None:
            try:
                java_rti = factory.getRtiAmbassador()
            except Exception as exc:
                errors.append(f"RtiFactory.getRtiAmbassador failed: {exc}")
        factory_name = _string_call(factory, "rtiName") if factory is not None else None
        factory_version = _string_call(factory, "rtiVersion") if factory is not None else None
        hla_version = _string_call(java_rti, "getHLAversion") if java_rti is not None else None
        class_name = _java_class_name(java_rti) if java_rti is not None else None
        interfaces = _java_interface_names(java_rti) if java_rti is not None else ()
    except Exception as exc:
        errors.append(f"Py4J discovery failed: {exc}")
    finally:
        if gateway is not None:
            try:
                gateway.shutdown()
            except Exception:
                pass

    factory_found = factory is not None
    ambassador_created = java_rti is not None
    edition_match = _edition_matches(profile, hla_version, interfaces)
    if ambassador_created and not edition_match:
        warnings.append(f"RTIambassador did not explicitly confirm {profile.edition} via interface or HLA version")

    return JavaRtiIntakeReport(
        edition=profile.edition,
        bridge="py4j",
        classpath=request.classpath,
        factory_requested=request.rti_factory_name,
        factory_found=factory_found,
        factory_name=factory_name,
        factory_version=factory_version,
        rti_ambassador_created=ambassador_created,
        rti_ambassador_class=class_name,
        rti_ambassador_interfaces=interfaces,
        hla_version=hla_version,
        edition_match=edition_match,
        status=_status(factory_found, ambassador_created, errors),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def report_slug(report: JavaRtiIntakeReport) -> str:
    name = report.factory_name or report.factory_requested or "java-rti"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower() or "java-rti"
    return f"{slug}-{report.edition}-{report.bridge}"


def write_intake_reports(report: JavaRtiIntakeReport, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = report_slug(report)
    json_path = output / f"{slug}.json"
    md_path = output / f"{slug}.md"
    json_path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_intake_markdown(report), encoding="utf-8")
    return json_path, md_path


def render_intake_markdown(report: JavaRtiIntakeReport) -> str:
    def verdict(value: bool) -> str:
        return "PASS" if value else "FAIL"

    lines = [
        f"# Java RTI Intake: {report.edition} {report.bridge}",
        "",
        f"- Status: `{report.status}`",
        f"- Factory discovery: {verdict(report.factory_found)}",
        f"- RTI ambassador creation: {verdict(report.rti_ambassador_created)}",
        f"- Edition match: {verdict(report.edition_match)}",
        f"- Factory requested: `{report.factory_requested or ''}`",
        f"- Factory name: `{report.factory_name or ''}`",
        f"- Factory version: `{report.factory_version or ''}`",
        f"- RTI ambassador class: `{report.rti_ambassador_class or ''}`",
        f"- HLA version: `{report.hla_version or ''}`",
        "",
        "## Interfaces",
        "",
    ]
    lines.extend(f"- `{name}`" for name in report.rti_ambassador_interfaces)
    if not report.rti_ambassador_interfaces:
        lines.append("- none reported")
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


__all__ = [
    "JAVA_2010",
    "JAVA_2025",
    "JAVA_API_PROFILES",
    "JavaApiProfile",
    "JavaRtiIntakeReport",
    "JavaRtiIntakeRequest",
    "discover_java_rti_jar",
    "java_api_profile",
    "render_intake_markdown",
    "split_classpath",
    "validate_classpath",
    "write_intake_reports",
]
