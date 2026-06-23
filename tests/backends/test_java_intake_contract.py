from __future__ import annotations

import json
import subprocess
import sys

import pytest

from hla.bridges.java.common.java_intake import (
    JavaRtiIntakeRequest,
    discover_java_rti_jar,
    java_api_profile,
)
from hla.rti import available_backend_plugins, create_rti_ambassador


def test_java_intake_profiles_keep_2010_and_2025_packages_separate() -> None:
    profile_2010 = java_api_profile("2010")
    profile_2025 = java_api_profile("2025")
    profile_202x = java_api_profile("202X")

    assert profile_2010.spec_name == "rti1516e"
    assert profile_2010.factory_factory_class == "hla.rti1516e.RtiFactoryFactory"
    assert profile_2025.spec_name == "rti1516_2025"
    assert profile_2025.factory_factory_class == "hla.rti1516_2025.RtiFactoryFactory"
    assert profile_202x.spec_name == "rti1516_202x"
    assert profile_202x.factory_factory_class == "hla.rti1516_202X.RtiFactoryFactory"


def test_java_intake_discovery_reports_missing_classpath_without_stack_trace() -> None:
    report = discover_java_rti_jar(
        JavaRtiIntakeRequest(
            edition="2010",
            bridge="jpype",
            classpath=("missing-vendor-rti.jar",),
            rti_factory_name="Vendor RTI",
        )
    )

    assert report.status == "planned"
    assert report.factory_found is False
    assert report.rti_ambassador_created is False
    assert report.errors == ("Classpath entry does not exist: missing-vendor-rti.jar",)


def test_generic_java_intake_routes_are_registered_separately_from_standard_shims() -> None:
    plugins = available_backend_plugins()

    assert plugins["java-2010-jpype"].family == "intake/java"
    assert plugins["java-2010-py4j"].family == "intake/java"
    assert plugins["java-2025-jpype"].family == "intake/java"
    assert plugins["java-2025-py4j"].family == "intake/java"
    assert plugins["java-standard-2010-jpype"].family == "standard/java"
    assert plugins["java-standard-2025-jpype"].family == "standard/java"


def test_generic_java_2010_route_requires_user_supplied_classpath() -> None:
    with pytest.raises(ValueError, match="require classpath"):
        create_rti_ambassador(spec="rti1516e", backend="java-2010-jpype")


def test_generic_java_2025_route_is_discovery_only_until_real_adapter_exists() -> None:
    with pytest.raises(RuntimeError, match="Generic Java 2025 RTI invocation is not implemented yet"):
        create_rti_ambassador(
            spec="rti1516_2025",
            backend="java-2025-jpype",
            classpath=["pyproject.toml"],
        )


def test_java_discover_writes_structured_missing_classpath_report(tmp_path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "java",
            "discover",
            "--edition",
            "2010",
            "--bridge",
            "jpype",
            "--classpath",
            "missing-vendor-rti.jar",
            "--factory",
            "Vendor RTI",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["status"] == "planned"
    assert payload["errors"] == ["Classpath entry does not exist: missing-vendor-rti.jar"]
    assert payload["evidence_json"].endswith(".json")
    assert payload["evidence_markdown"].endswith(".md")


def test_java_certify_core_reports_missing_classpath(tmp_path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "java",
            "certify-core",
            "--edition",
            "2010",
            "--bridges",
            "jpype",
            "--classpath",
            "missing-vendor-rti.jar",
            "--factory",
            "Vendor RTI",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    report = payload["reports"][0]
    assert report["status"] == "planned"
    assert report["errors"] == ["Classpath entry does not exist: missing-vendor-rti.jar"]


def test_java_certify_core_2025_generic_vendor_is_behavior_blocked_after_discovery(monkeypatch) -> None:
    from hla.bridges.java.common.java_intake import JavaRtiIntakeReport
    from hla.verification import java_intake_certification as cert

    def fake_discover(request):
        return JavaRtiIntakeReport(
            edition="2025",
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            factory_found=True,
            rti_ambassador_created=True,
            edition_match=True,
            status="ambassador-green",
        )

    monkeypatch.setattr(cert, "discover_java_rti_jar", fake_discover)
    report = cert.certify_java_rti_core(
        JavaRtiIntakeRequest(
            edition="2025",
            bridge="jpype",
            classpath=("pyproject.toml",),
            rti_factory_name="Vendor Java 2025 RTI",
        )
    )

    assert report.status == "behavior-blocked"
    assert report.core_scenario_status == "blocked"
    assert report.blocked_reason == "generic/vendor Java 2025 RTI invocation is not implemented yet"


def test_java_certify_core_202x_vendor_is_behavior_blocked_after_discovery(monkeypatch) -> None:
    from hla.bridges.java.common.java_intake import JavaRtiIntakeReport
    from hla.verification import java_intake_certification as cert

    def fake_discover(request):
        return JavaRtiIntakeReport(
            edition="202X",
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            factory_found=True,
            rti_ambassador_created=True,
            edition_match=True,
            status="ambassador-green",
        )

    monkeypatch.setattr(cert, "discover_java_rti_jar", fake_discover)
    report = cert.certify_java_rti_core(
        JavaRtiIntakeRequest(
            edition="202X",
            bridge="jpype",
            classpath=("pyproject.toml",),
            rti_factory_name="Federate Protocol",
        )
    )

    assert report.status == "behavior-blocked"
    assert report.core_scenario_status == "blocked"
    assert report.blocked_reason == "vendor Java 202X RTI behavior certification is not implemented yet"


def test_java_certify_core_2025_standard_shim_uses_runtime_capability_trace(monkeypatch) -> None:
    from hla.bridges.java.common.java_intake import JavaRtiIntakeReport
    from hla.verification import java_intake_certification as cert

    def fake_discover(request):
        return JavaRtiIntakeReport(
            edition="2025",
            bridge=request.bridge,
            classpath=request.classpath,
            factory_requested=request.rti_factory_name,
            factory_found=True,
            rti_ambassador_created=True,
            edition_match=True,
            status="ambassador-green",
        )

    def fake_runtime_trace(backend_name):
        assert backend_name == "java-standard-2025-jpype"
        return {
            "status": "trace-green",
            "trace": tuple({"event": event} for event in cert.REQUIRED_2025_TRACE_EVENTS),
        }

    monkeypatch.setattr(cert, "discover_java_rti_jar", fake_discover)
    monkeypatch.setattr("hla.verification.shim_route_evidence.run_standard_2025_runtime_capability_trace", fake_runtime_trace)

    report = cert.certify_java_rti_core(
        JavaRtiIntakeRequest(
            edition="2025",
            bridge="jpype",
            classpath=("pyproject.toml",),
            rti_factory_name="Java 2025 Standard Shim",
        )
    )

    assert report.status == "trace-green"
    assert report.connect_status == "connect-green"
    assert report.callback_status == "callback-runtime-green"
    assert report.core_scenario_status == "runtime-capability-green"
    assert report.missing_trace_events == ()
