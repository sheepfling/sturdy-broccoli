#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import tomllib

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
JAVA_2010_REPORT = SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/java-standard-2010.json"
SHIM_ROUTE_REPORTS = {
    "java-2010": SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/java-standard-2010.json",
    "java-2025": SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/java-standard-2025.json",
    "cpp-2010": SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/cpp-standard-2010.json",
    "cpp-2025": SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/cpp-standard-2025.json",
}
JAVA_INTAKE_REPORT_DIR = SCRIPT_REPO_ROOT / "docs/evidence/java-intake"
CPP_INTAKE_REPORT_DIR = SCRIPT_REPO_ROOT / "docs/evidence/cpp-intake"
JAVA_TOOLCHAIN_REPORT_DIR = SCRIPT_REPO_ROOT / "docs/evidence/shim_routes"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


def _matrix(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.rti.standard_shims import iter_standard_shim_artifacts

    editions = {item.strip() for item in args.editions.split(",") if item.strip()}
    print("Language-shim route matrix")
    print("")
    print("artifact | edition | status | routes")
    print("--- | --- | --- | ---")
    for artifact in iter_standard_shim_artifacts():
        if artifact.edition not in editions:
            continue
        routes = ", ".join(route.name for route in artifact.routes)
        status = artifact.status
        report_path = SHIM_ROUTE_REPORTS.get(artifact.key)
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path is not None and report_path.exists() else {}
        if report.get("compile_status") == "passed":
            status = "surface-backed"
            route_statuses = {
                name: details.get("status")
                for name, details in dict(report.get("routes", {})).items()
                if isinstance(details, dict)
            }
            scenario_status = None
            scenario_evidence = report.get("scenario_evidence")
            if isinstance(scenario_evidence, dict):
                scenario_status = scenario_evidence.get("status")
            if scenario_status == "scenario-parity-green":
                status = "surface-backed + scenario-parity"
            elif route_statuses and all(value == "core-green" for value in route_statuses.values()):
                status = "surface-backed + core-green"
            routes = ", ".join(
                f"{route.name} ({route_statuses.get(route.name, 'surface-backed')})"
                for route in artifact.routes
            )
        print(f"{artifact.artifact_name} | {artifact.edition} | {status} | {routes}")
    print("")
    print("C++ SDK intake")
    print("")
    print("route | edition | profile | header | compile | link | status")
    print("--- | --- | --- | --- | --- | --- | ---")
    cpp_rows = {
        ("2010", "pybind"): "cpp-2010-sdk-pybind",
        ("2010", "grpc"): "cpp-2010-sdk-grpc",
        ("2025", "pybind"): "cpp-2025-sdk-pybind",
        ("2025", "grpc"): "cpp-2025-sdk-grpc",
    }
    cpp_report_by_route: dict[tuple[str, str], dict[str, object]] = {}
    if CPP_INTAKE_REPORT_DIR.exists():
        for path in CPP_INTAKE_REPORT_DIR.glob("*.json"):
            try:
                report = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            artifact = report.get("artifact", {})
            if not isinstance(artifact, dict) or artifact.get("kind") != "cpp-sdk":
                continue
            edition = str(report.get("edition", ""))
            transport = str(report.get("transport", ""))
            if (edition, transport) in cpp_rows:
                cpp_report_by_route[(edition, transport)] = report
    for key, route_name in cpp_rows.items():
        edition, _transport = key
        if edition not in editions:
            continue
        report = cpp_report_by_route.get(key, {})
        checks = report.get("checks", ())
        if not checks and isinstance(report.get("discovery"), dict):
            checks = dict(report["discovery"]).get("checks", ())
        check_statuses = {
            str(check.get("name")): str(check.get("status"))
            for check in checks
            if isinstance(check, dict)
        } if isinstance(checks, list) else {}
        profile_status = check_statuses.get("profile", "profile-required")
        header_status = check_statuses.get("headers", "profile-required")
        compile_status = check_statuses.get("capsule_configure", "profile-required")
        link_status = check_statuses.get("capsule_build", check_statuses.get("libraries", "profile-required"))
        status = str(report.get("status", "intake"))
        print(f"{route_name} | {edition} | {profile_status} | {header_status} | {compile_status} | {link_status} | {status}")
    print("")
    print("Java RTI intake certification")
    print("")
    print("route | edition | discovery | callback | core | trace | status")
    print("--- | --- | --- | --- | --- | --- | ---")
    intake_rows = {
        ("2010", "jpype"): "java-2010-jpype",
        ("2010", "py4j"): "java-2010-py4j",
        ("2025", "jpype"): "java-2025-jpype",
        ("2025", "py4j"): "java-2025-py4j",
    }
    report_by_route: dict[tuple[str, str], dict[str, object]] = {}
    if JAVA_INTAKE_REPORT_DIR.exists():
        for path in JAVA_INTAKE_REPORT_DIR.glob("*.json"):
            try:
                report = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            edition = str(report.get("edition", ""))
            bridge = str(report.get("bridge", ""))
            if (edition, bridge) in intake_rows:
                report_by_route[(edition, bridge)] = report
    for key, route_name in intake_rows.items():
        edition, _bridge = key
        if edition not in editions:
            continue
        report = report_by_route.get(key, {})
        discovery = dict(report.get("discovery", {})) if isinstance(report.get("discovery"), dict) else {}
        discovery_status = str(discovery.get("status", "intake"))
        callback_status = str(report.get("callback_status", "intake"))
        core_status = str(report.get("core_scenario_status", "opt"))
        trace_status = str(report.get("trace_comparison_status", "opt"))
        status = str(report.get("status", "intake"))
        print(f"{route_name} | {edition} | {discovery_status} | {callback_status} | {core_status} | {trace_status} | {status}")
    print("")
    print("Status is generated from local standard-shim evidence reports. Routes without built artifacts remain planned or surface-only.")
    return 0


def _build(args: argparse.Namespace) -> int:
    targets = {
        "java-standard-2010": [sys.executable, str(SCRIPT_REPO_ROOT / "java_shims/hla-rti1516e-standard-shim/tools/build_standard_shim.py")],
        "java-standard-2025": [sys.executable, str(SCRIPT_REPO_ROOT / "java_shims/hla-rti1516-2025-standard-shim/tools/build_standard_shim.py")],
        "cpp-standard-2010": [sys.executable, str(SCRIPT_REPO_ROOT / "cpp_shims/build_standard_shim.py"), "2010"],
        "cpp-standard-2025": [sys.executable, str(SCRIPT_REPO_ROOT / "cpp_shims/build_standard_shim.py"), "2025"],
    }
    if args.target == "standard-shims":
        for target in ("java-standard-2010", "java-standard-2025", "cpp-standard-2010", "cpp-standard-2025"):
            completed = subprocess.run(targets[target], cwd=SCRIPT_REPO_ROOT, check=False)
            if completed.returncode != 0:
                return completed.returncode
        return 0
    if args.target not in targets:
        raise SystemExit(f"unknown build target {args.target!r}")
    completed = subprocess.run(targets[args.target], cwd=SCRIPT_REPO_ROOT, check=False)
    return completed.returncode


def _evidence(args: argparse.Namespace) -> int:
    if args.target != "shim-routes":
        raise SystemExit(f"unknown evidence target {args.target!r}")

    _bootstrap_source_checkout()
    from hla.verification.shim_route_evidence import run_standard_2010_exchange_trace, run_standard_2025_lifecycle_trace

    output_dir = SCRIPT_REPO_ROOT / "docs/evidence/shim_routes/route_traces"
    output_dir.mkdir(parents=True, exist_ok=True)
    traces = []
    for route in ("cpp-standard-2010-pybind", "cpp-standard-2010-grpc"):
        traces.append(run_standard_2010_exchange_trace(route))
    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        traces.append(run_standard_2025_lifecycle_trace(route))

    for trace in traces:
        route = trace["route"]
        path = output_dir / f"{route}.json"
        path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(path)

    summary = {
        "status": "trace-green",
        "scope": "MVP route proof, not full HLA conformance",
        "trace_count": len(traces),
        "routes": [trace["route"] for trace in traces],
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(summary_path)
    return 0


def _java_discover(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.bridges.java.common.java_intake import (
        JavaRtiIntakeRequest,
        discover_java_rti_jar,
        split_classpath,
        write_intake_reports,
    )

    classpath = split_classpath(args.classpath)
    request = JavaRtiIntakeRequest(
        edition=args.edition,
        bridge=args.bridge,
        classpath=classpath,
        rti_factory_name=args.factory,
        local_settings_designator=args.local_settings_designator,
        jvm_args=tuple(args.jvm_arg or ()),
        gateway_port=args.gateway_port,
        timeout_seconds=args.timeout_seconds,
    )
    report = discover_java_rti_jar(request)
    output_dir = Path(args.output_dir)
    json_path, md_path = write_intake_reports(report, output_dir)
    payload = report.to_json_dict()
    payload["evidence_json"] = str(json_path)
    payload["evidence_markdown"] = str(md_path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not report.errors else 2


def _java_doctor(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.bridges.java.common import discover_java_toolchain, write_java_toolchain_reports

    inventory = discover_java_toolchain(SCRIPT_REPO_ROOT)
    output_dir = Path(args.output_dir)
    json_path, md_path = write_java_toolchain_reports(inventory, output_dir)
    payload = inventory.to_json_dict()
    payload["evidence_json"] = str(json_path)
    payload["evidence_markdown"] = str(md_path)
    payload["recommended_commands"] = []
    if inventory.status != "ready":
        if not inventory.java_ok or not inventory.javac_ok or not inventory.jar_ok:
            payload["recommended_commands"].append("./tools/shim-routes java doctor")
    if any(not artifact.exists for artifact in inventory.artifacts):
        payload["recommended_commands"].extend(
            artifact.build_command for artifact in inventory.artifacts if not artifact.exists
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if inventory.ok else 2


def _java_certify_core(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.bridges.java.common.java_intake import JavaRtiIntakeRequest, split_classpath
    from hla.verification.java_intake_certification import certify_java_rti_core, write_certification_reports

    classpath = split_classpath(args.classpath)
    bridges = tuple(item.strip() for item in args.bridges.split(",") if item.strip())
    if not bridges:
        raise SystemExit("--bridges must name at least one bridge")

    reports = []
    failed = False
    for bridge in bridges:
        request = JavaRtiIntakeRequest(
            edition=args.edition,
            bridge=bridge,
            classpath=classpath,
            rti_factory_name=args.factory,
            local_settings_designator=args.local_settings_designator,
            jvm_args=tuple(args.jvm_arg or ()),
            gateway_port=args.gateway_port,
            timeout_seconds=args.timeout_seconds,
        )
        report = certify_java_rti_core(request)
        json_path, md_path = write_certification_reports(report, args.output_dir)
        payload = report.to_json_dict()
        payload["evidence_json"] = str(json_path)
        payload["evidence_markdown"] = str(md_path)
        reports.append(payload)
        if report.errors or report.status not in {"trace-green", "behavior-blocked"}:
            failed = True
    print(json.dumps({"reports": reports}, indent=2, sort_keys=True))
    return 2 if failed else 0


def _cpp_discover(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest, discover_cpp_sdk, write_cpp_intake_reports

    request = CppSdkIntakeRequest(
        profile_path=args.profile,
        transport=args.transport,
        timeout_seconds=args.timeout_seconds,
    )
    report = discover_cpp_sdk(request)
    if args.edition and report.edition != "unknown" and report.edition != args.edition:
        payload = report.to_json_dict()
        mismatch = f"profile edition {report.edition} does not match requested edition {args.edition}"
        payload["status"] = "failed"
        payload["errors"] = [*payload.get("errors", []), mismatch]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    json_path, md_path = write_cpp_intake_reports(report, args.output_dir)
    payload = report.to_json_dict()
    payload["evidence_json"] = str(json_path)
    payload["evidence_markdown"] = str(md_path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not report.errors else 2


def _cpp_build_capsule(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest, generate_cpp_sdk_capsule, write_cpp_intake_reports

    request = CppSdkIntakeRequest(
        profile_path=args.profile,
        transport=args.transport,
        build_dir=args.build_dir,
        timeout_seconds=args.timeout_seconds,
    )
    output_root = args.build_dir or str(SCRIPT_REPO_ROOT / ".build/shim_routes/cpp-capsules")
    report = generate_cpp_sdk_capsule(request, output_root)
    if args.edition and report.edition != "unknown" and report.edition != args.edition:
        payload = report.to_json_dict()
        mismatch = f"profile edition {report.edition} does not match requested edition {args.edition}"
        payload["status"] = "failed"
        payload["errors"] = [*payload.get("errors", []), mismatch]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    json_path, md_path = write_cpp_intake_reports(report, args.output_dir)
    payload = report.to_json_dict()
    payload["evidence_json"] = str(json_path)
    payload["evidence_markdown"] = str(md_path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not report.errors else 2


def _cpp_certify_core(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest
    from hla.verification.cpp_intake_certification import (
        certify_cpp_sdk_core,
        certify_cpp_standard_core,
        write_certification_reports,
    )

    transports = tuple(item.strip() for item in args.transports.split(",") if item.strip())
    if not transports:
        raise SystemExit("--transports must name at least one transport")
    reports = []
    failed = False
    for transport in transports:
        if args.artifact == "standard-shim":
            report = certify_cpp_standard_core(args.edition, transport)
        else:
            if not args.profile:
                raise SystemExit("--profile is required unless --artifact standard-shim is used")
            report = certify_cpp_sdk_core(
                CppSdkIntakeRequest(
                    profile_path=args.profile,
                    transport=transport,
                    build_dir=args.build_dir,
                    timeout_seconds=args.timeout_seconds,
                ),
                args.build_dir,
            )
        json_path, md_path = write_certification_reports(report, args.output_dir)
        payload = report.to_json_dict()
        payload["evidence_json"] = str(json_path)
        payload["evidence_markdown"] = str(md_path)
        reports.append(payload)
        if report.errors or report.status not in {"trace-green", "behavior-blocked", "adapter-smoke-green"}:
            failed = True
    print(json.dumps({"reports": reports}, indent=2, sort_keys=True))
    return 2 if failed else 0


def _cpp_smoke_capsule(args: argparse.Namespace) -> int:
    _bootstrap_source_checkout()
    from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest
    from hla.verification.cpp_intake_certification import smoke_cpp_sdk_capsule, write_certification_reports

    request = CppSdkIntakeRequest(
        profile_path=args.profile,
        transport=args.transport,
        build_dir=args.build_dir,
        timeout_seconds=args.timeout_seconds,
    )
    report = smoke_cpp_sdk_capsule(request, args.build_dir)
    if args.edition and report.edition != "unknown" and report.edition != args.edition:
        payload = report.to_json_dict()
        mismatch = f"profile edition {report.edition} does not match requested edition {args.edition}"
        payload["status"] = "failed"
        payload["errors"] = [*payload.get("errors", []), mismatch]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    json_path, md_path = write_certification_reports(report, args.output_dir)
    payload = report.to_json_dict()
    payload["evidence_json"] = str(json_path)
    payload["evidence_markdown"] = str(md_path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not report.errors and report.status == "adapter-smoke-green" else 2


def _demo(args: argparse.Namespace) -> int:
    if args.name in {"fom-showcase", "simulation-showcase"}:
        if args.edition != "2025":
            raise SystemExit("fom-showcase currently runs the 2025 Proto2025 FOM set plus the existing Target/Radar FOM")
        _bootstrap_source_checkout()
        from hla.verification.repo_internal.verification.proto2025_fom_showcase import write_proto2025_fom_showcase_artifacts

        paths = write_proto2025_fom_showcase_artifacts(args.output_dir, target_radar_steps=args.steps)
        print(json.dumps({
            "status": "lifecycle-green",
            "summary_json": str(paths.summary_json),
            "scenario_csv": str(paths.scenario_csv),
            "report_markdown": str(paths.report_markdown),
            "chart_manifest_json": str(paths.chart_manifest_json),
            "observer_events_jsonl": str(paths.observer_events_jsonl),
        }, indent=2, sort_keys=True))
        return 0
    if args.name != "mixed-language-target-radar":
        raise SystemExit(f"unknown demo {args.name!r}")
    print(f"mixed-language-target-radar edition {args.edition}")
    print("status: planned")
    print("reason: standard-backed Java and C++ shim artifacts are not built yet")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="shim-routes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    matrix = subparsers.add_parser("matrix")
    matrix.add_argument("--editions", default="2010,2025")
    matrix.add_argument("--routes", default="all")
    matrix.set_defaults(func=_matrix)

    demo = subparsers.add_parser("demo")
    demo.add_argument("name")
    demo.add_argument("--edition", choices=("2010", "2025"), required=True)
    demo.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "artifacts/proto2025_fom_showcase"))
    demo.add_argument("--steps", type=int, default=3, help="Target/Radar steps for showcase demos")
    demo.set_defaults(func=_demo)

    build = subparsers.add_parser("build")
    build.add_argument("target")
    build.set_defaults(func=_build)

    evidence = subparsers.add_parser("evidence")
    evidence.add_argument("target")
    evidence.set_defaults(func=_evidence)

    java = subparsers.add_parser("java")
    java_subparsers = java.add_subparsers(dest="java_command", required=True)

    java_discover = java_subparsers.add_parser("discover")
    java_discover.add_argument("--edition", choices=("2010", "2025", "202X"), required=True)
    java_discover.add_argument("--bridge", choices=("jpype", "py4j"), required=True)
    java_discover.add_argument("--classpath", required=True, help=f"Java classpath, separated with {os.pathsep!r}")
    java_discover.add_argument("--factory", default=None, help="Optional RTI factory name passed to RtiFactoryFactory.getRtiFactory")
    java_discover.add_argument("--local-settings-designator", default=None)
    java_discover.add_argument("--jvm-arg", action="append", default=[])
    java_discover.add_argument("--gateway-port", type=int, default=None)
    java_discover.add_argument("--timeout-seconds", type=float, default=30.0)
    java_discover.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/java-intake"))
    java_discover.set_defaults(func=_java_discover)

    java_doctor = java_subparsers.add_parser("doctor")
    java_doctor.add_argument(
        "--output-dir",
        default=str(JAVA_TOOLCHAIN_REPORT_DIR),
        help="Directory for the machine-readable Java toolchain inventory",
    )
    java_doctor.set_defaults(func=_java_doctor)

    java_certify = java_subparsers.add_parser("certify-core")
    java_certify.add_argument("--edition", choices=("2010", "2025", "202X"), required=True)
    java_certify.add_argument("--bridges", default="jpype,py4j")
    java_certify.add_argument("--classpath", required=True, help=f"Java classpath, separated with {os.pathsep!r}")
    java_certify.add_argument("--factory", default=None, help="Optional RTI factory name passed to RtiFactoryFactory.getRtiFactory")
    java_certify.add_argument("--local-settings-designator", default=None)
    java_certify.add_argument("--jvm-arg", action="append", default=[])
    java_certify.add_argument("--gateway-port", type=int, default=None)
    java_certify.add_argument("--timeout-seconds", type=float, default=30.0)
    java_certify.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/java-intake"))
    java_certify.set_defaults(func=_java_certify_core)

    cpp = subparsers.add_parser("cpp")
    cpp_subparsers = cpp.add_subparsers(dest="cpp_command", required=True)

    cpp_discover = cpp_subparsers.add_parser("discover")
    cpp_discover.add_argument("--profile", required=True, help="C++ SDK intake profile path")
    cpp_discover.add_argument("--edition", choices=("2010", "2025"), default=None, help="Optional expected edition guard")
    cpp_discover.add_argument("--transport", choices=("grpc", "pybind"), default="grpc")
    cpp_discover.add_argument("--timeout-seconds", type=float, default=30.0)
    cpp_discover.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/cpp-intake"))
    cpp_discover.set_defaults(func=_cpp_discover)

    cpp_build_capsule = cpp_subparsers.add_parser("build-capsule")
    cpp_build_capsule.add_argument("--profile", required=True, help="C++ SDK intake profile path")
    cpp_build_capsule.add_argument("--edition", choices=("2010", "2025"), default=None, help="Optional expected edition guard")
    cpp_build_capsule.add_argument("--transport", choices=("grpc", "pybind"), default="grpc")
    cpp_build_capsule.add_argument("--build-dir", default=str(SCRIPT_REPO_ROOT / ".build/shim_routes/cpp-capsules"))
    cpp_build_capsule.add_argument("--timeout-seconds", type=float, default=30.0)
    cpp_build_capsule.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/cpp-intake"))
    cpp_build_capsule.set_defaults(func=_cpp_build_capsule)

    cpp_smoke = cpp_subparsers.add_parser("smoke-capsule")
    cpp_smoke.add_argument("--profile", required=True, help="C++ SDK intake profile path")
    cpp_smoke.add_argument("--edition", choices=("2010", "2025"), default=None, help="Optional expected edition guard")
    cpp_smoke.add_argument("--transport", choices=("grpc", "pybind"), default="grpc")
    cpp_smoke.add_argument("--build-dir", default=str(SCRIPT_REPO_ROOT / ".build/shim_routes/cpp-capsules"))
    cpp_smoke.add_argument("--timeout-seconds", type=float, default=30.0)
    cpp_smoke.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/cpp-intake"))
    cpp_smoke.set_defaults(func=_cpp_smoke_capsule)

    cpp_certify = cpp_subparsers.add_parser("certify-core")
    cpp_certify.add_argument("--edition", choices=("2010", "2025"), required=True)
    cpp_certify.add_argument("--artifact", choices=("standard-shim", "sdk"), default="sdk")
    cpp_certify.add_argument("--profile", default=None, help="C++ SDK intake profile path")
    cpp_certify.add_argument("--transports", default="pybind,grpc")
    cpp_certify.add_argument("--build-dir", default=str(SCRIPT_REPO_ROOT / ".build/shim_routes/cpp-capsules"))
    cpp_certify.add_argument("--timeout-seconds", type=float, default=30.0)
    cpp_certify.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/cpp-intake"))
    cpp_certify.set_defaults(func=_cpp_certify_core)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
