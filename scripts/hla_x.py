#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
JAVA_2010_REPORT = SCRIPT_REPO_ROOT / "docs/evidence/rosetta/java-standard-2010.json"
ROSETTA_REPORTS = {
    "java-2010": SCRIPT_REPO_ROOT / "docs/evidence/rosetta/java-standard-2010.json",
    "java-2025": SCRIPT_REPO_ROOT / "docs/evidence/rosetta/java-standard-2025.json",
    "cpp-2010": SCRIPT_REPO_ROOT / "docs/evidence/rosetta/cpp-standard-2010.json",
    "cpp-2025": SCRIPT_REPO_ROOT / "docs/evidence/rosetta/cpp-standard-2025.json",
}
JAVA_TOOLCHAIN_REPORT_DIR = SCRIPT_REPO_ROOT / "docs/evidence/rosetta"


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
    print("HLA-X Rosetta standard-shim matrix")
    print("")
    print("artifact | edition | status | routes")
    print("--- | --- | --- | ---")
    for artifact in iter_standard_shim_artifacts():
        if artifact.edition not in editions:
            continue
        routes = ", ".join(route.name for route in artifact.routes)
        status = artifact.status
        report_path = ROSETTA_REPORTS.get(artifact.key)
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path is not None and report_path.exists() else {}
        if report.get("compile_status") == "passed":
            status = "surface-backed"
            route_statuses = {
                name: details.get("status")
                for name, details in dict(report.get("routes", {})).items()
                if isinstance(details, dict)
            }
            if route_statuses and all(value == "core-green" for value in route_statuses.values()):
                status = "surface-backed + core-green"
            routes = ", ".join(
                f"{route.name} ({route_statuses.get(route.name, 'surface-backed')})"
                for route in artifact.routes
            )
        print(f"{artifact.artifact_name} | {artifact.edition} | {status} | {routes}")
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
    if args.target != "rosetta-routes":
        raise SystemExit(f"unknown evidence target {args.target!r}")

    _bootstrap_source_checkout()
    from hla.verification.rosetta_mvp import run_standard_2010_exchange_trace, run_standard_2025_lifecycle_trace

    output_dir = SCRIPT_REPO_ROOT / "docs/evidence/rosetta/route_traces"
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
        "status": "core-green",
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
            payload["recommended_commands"].append("./tools/hla-x java doctor")
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


def _demo(args: argparse.Namespace) -> int:
    if args.name != "mixed-language-target-radar":
        raise SystemExit(f"unknown demo {args.name!r}")
    print(f"mixed-language-target-radar edition {args.edition}")
    print("status: planned")
    print("reason: standard-backed Java and C++ shim artifacts are not built yet")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hla-x")
    subparsers = parser.add_subparsers(dest="command", required=True)

    matrix = subparsers.add_parser("matrix")
    matrix.add_argument("--editions", default="2010,2025")
    matrix.add_argument("--routes", default="all")
    matrix.set_defaults(func=_matrix)

    demo = subparsers.add_parser("demo")
    demo.add_argument("name")
    demo.add_argument("--edition", choices=("2010", "2025"), required=True)
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
    java_discover.add_argument("--edition", choices=("2010", "2025"), required=True)
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
    java_certify.add_argument("--edition", choices=("2010", "2025"), required=True)
    java_certify.add_argument("--bridges", default="jpype,py4j")
    java_certify.add_argument("--classpath", required=True, help=f"Java classpath, separated with {os.pathsep!r}")
    java_certify.add_argument("--factory", default=None, help="Optional RTI factory name passed to RtiFactoryFactory.getRtiFactory")
    java_certify.add_argument("--local-settings-designator", default=None)
    java_certify.add_argument("--jvm-arg", action="append", default=[])
    java_certify.add_argument("--gateway-port", type=int, default=None)
    java_certify.add_argument("--timeout-seconds", type=float, default=30.0)
    java_certify.add_argument("--output-dir", default=str(SCRIPT_REPO_ROOT / "docs/evidence/java-intake"))
    java_certify.set_defaults(func=_java_certify_core)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
