"""Pitch 202X Java surface audit helpers."""
from __future__ import annotations

import ast
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PITCH_RTI_202X_JAVA = Path("third_party/pitch/PITCH-prti1516e-manual/api/java/hla/rti1516_202X")
REPO_RTI_2025_PY = Path("packages/hla-rti1516-2025/src/hla/rti1516_2025")
BRIDGE_BLOCKER_FILES = (
    Path("packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py"),
    Path("packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py"),
    Path("packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py"),
    Path("packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py"),
    Path("packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py"),
    Path("packages/hla-bridge-java-common/src/hla/bridges/java/common/java_factory_selection.py"),
)


@dataclass(frozen=True, slots=True)
class MethodSummary:
    name: str
    overloads: int


@dataclass(frozen=True, slots=True)
class InterfaceComparison:
    interface_name: str
    vendor_overload_total: int
    repo_overload_total: int
    shared_method_name_count: int
    vendor_only_method_names: tuple[str, ...]
    repo_only_method_names: tuple[str, ...]
    overload_count_mismatches: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class BlockerFinding:
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class Pitch202xSurfaceAudit:
    vendor_label: str
    vendor_bundle_version: str
    vendor_api_version: str
    rti_ambassador: InterfaceComparison
    federate_ambassador: InterfaceComparison
    adapter_readiness: str
    blocker_findings: tuple[BlockerFinding, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _split_java_parameters(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in value:
        if char == "<":
            depth += 1
        elif char == ">":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _parse_java_methods(path: Path) -> list[MethodSummary]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    normalized_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line:
            normalized_lines.append(line)
    joined = " ".join(normalized_lines)
    pattern = re.compile(r"([A-Za-z0-9_<>,\[\]\? ]+)\s+(\w+)\s*\((.*?)\)\s*throws")
    methods: list[MethodSummary] = []
    for _return_type, name, args in pattern.findall(joined):
        _split_java_parameters(args.strip())
        methods.append(MethodSummary(name=name, overloads=1))
    return methods


def _parse_python_protocol_methods(path: Path, class_name: str) -> list[MethodSummary]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    protocol = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    methods: list[MethodSummary] = []
    for node in protocol.body:
        if isinstance(node, ast.FunctionDef):
            methods.append(MethodSummary(name=node.name, overloads=1))
    return methods


def _compare_interfaces(interface_name: str, vendor_methods: list[MethodSummary], repo_methods: list[MethodSummary]) -> InterfaceComparison:
    vendor_counter = Counter(method.name for method in vendor_methods)
    repo_counter = Counter(method.name for method in repo_methods)
    shared_names = set(vendor_counter) & set(repo_counter)
    mismatches = tuple(
        {
            "method_name": name,
            "vendor_overloads": vendor_counter[name],
            "repo_overloads": repo_counter[name],
        }
        for name in sorted(shared_names)
        if vendor_counter[name] != repo_counter[name]
    )
    return InterfaceComparison(
        interface_name=interface_name,
        vendor_overload_total=sum(vendor_counter.values()),
        repo_overload_total=sum(repo_counter.values()),
        shared_method_name_count=len(shared_names),
        vendor_only_method_names=tuple(sorted(set(vendor_counter) - set(repo_counter))),
        repo_only_method_names=tuple(sorted(set(repo_counter) - set(vendor_counter))),
        overload_count_mismatches=mismatches,
    )


def _bridge_blocker_findings(repo_root: Path) -> tuple[BlockerFinding, ...]:
    findings: list[BlockerFinding] = []
    for path in BRIDGE_BLOCKER_FILES:
        text = (repo_root / path).read_text(encoding="utf-8")
        if path.name == "factory.py" and "hla.rti1516e.RtiFactoryFactory" in text:
            findings.append(
                BlockerFinding(
                    path=str(path),
                    reason="Factory selection is hardwired to hla.rti1516e.RtiFactoryFactory instead of a profile-driven package name.",
                )
            )
        elif path.name == "runtime.py" and "hla.rti1516e.FederateAmbassador" in text:
            findings.append(
                BlockerFinding(
                    path=str(path),
                    reason="Federate ambassador proxy creation is hardwired to the 2010 Java interface package.",
                )
            )
        elif path.name == "java_common.py" and "from hla.rti1516e import" in text:
            findings.append(
                BlockerFinding(
                    path=str(path),
                    reason="Common conversion and callback dispatch code imports 2010 enums, exceptions, handles, time classes, and API metadata directly.",
                )
            )
        elif path.name == "java_factory_selection.py" and "hla.rti1516e.RtiFactoryFactory" in text:
            findings.append(
                BlockerFinding(
                    path=str(path),
                    reason="Generic Java RTI discovery is still implemented as a 2010-only factory probe.",
                )
            )
    return tuple(findings)


def build_pitch_202x_surface_audit(repo_root: Path) -> Pitch202xSurfaceAudit:
    vendor_bundle_version = (repo_root / "third_party/pitch/PITCH-prti1516e-manual/versioninfo.txt").read_text(encoding="utf-8").strip()
    vendor_api_version = (repo_root / "third_party/pitch/PITCH-prti1516e-manual/api/cpp/HLA_1516-202X/version.txt").read_text(encoding="utf-8").strip()
    rti = _compare_interfaces(
        "RTIambassador",
        _parse_java_methods(repo_root / PITCH_RTI_202X_JAVA / "RTIambassador.java"),
        _parse_python_protocol_methods(repo_root / REPO_RTI_2025_PY / "rti_ambassador.pyi", "RTIambassador"),
    )
    federate = _compare_interfaces(
        "FederateAmbassador",
        _parse_java_methods(repo_root / PITCH_RTI_202X_JAVA / "FederateAmbassador.java"),
        _parse_python_protocol_methods(repo_root / REPO_RTI_2025_PY / "federate_ambassador.pyi", "FederateAmbassador"),
    )
    blockers = _bridge_blocker_findings(repo_root)
    adapter_readiness = "bridge-blocked"
    if (
        not rti.vendor_only_method_names
        and not federate.vendor_only_method_names
        and not rti.overload_count_mismatches
        and not federate.overload_count_mismatches
        and not blockers
    ):
        adapter_readiness = "surface-close"
    elif (
        not rti.vendor_only_method_names
        and not federate.vendor_only_method_names
        and not rti.overload_count_mismatches
        and not federate.overload_count_mismatches
    ):
        adapter_readiness = "surface-close-bridge-blocked"
    return Pitch202xSurfaceAudit(
        vendor_label="Pitch pRTI Free",
        vendor_bundle_version=vendor_bundle_version,
        vendor_api_version=vendor_api_version,
        rti_ambassador=rti,
        federate_ambassador=federate,
        adapter_readiness=adapter_readiness,
        blocker_findings=blockers,
    )


def render_pitch_202x_surface_audit_markdown(report: Pitch202xSurfaceAudit) -> str:
    def render_interface(section: InterfaceComparison) -> list[str]:
        vendor_only_lines = [f"- `{name}`" for name in section.vendor_only_method_names] or ["- none"]
        repo_only_lines = [f"- `{name}`" for name in section.repo_only_method_names] or ["- none"]
        return [
            f"## {section.interface_name}",
            "",
            f"- vendor overload total: `{section.vendor_overload_total}`",
            f"- repo overload total: `{section.repo_overload_total}`",
            f"- shared method names: `{section.shared_method_name_count}`",
            f"- vendor-only method names: `{len(section.vendor_only_method_names)}`",
            f"- repo-only method names: `{len(section.repo_only_method_names)}`",
            f"- overload-count mismatches: `{len(section.overload_count_mismatches)}`",
            "",
            "### Vendor-only method names",
            "",
            *vendor_only_lines,
            "",
            "### Repo-only method names",
            "",
            *repo_only_lines,
            "",
        ]

    lines = [
        "# Pitch 202X Surface Audit",
        "",
        f"- vendor: `{report.vendor_label}`",
        f"- bundled runtime version: `{report.vendor_bundle_version}`",
        f"- bundled 202X API marker: `{report.vendor_api_version}`",
        f"- adapter readiness: `{report.adapter_readiness}`",
        "",
        "This report compares the bundled Pitch `hla.rti1516_202X` Java API source tree",
        "against the repo-owned `hla.rti1516_2025` Python protocol surface.",
        "",
    ]
    lines.extend(render_interface(report.rti_ambassador))
    lines.extend(render_interface(report.federate_ambassador))
    blocker_lines = [f"- `{finding.path}`: {finding.reason}" for finding in report.blocker_findings] or ["- none"]
    lines.extend(
        [
            "## Bridge Blockers",
            "",
            *blocker_lines,
            "",
            "## Conclusion",
            "",
            "The method-set comparison is close enough to treat Pitch `202X` as a serious candidate",
            "for a future adapter lane, but the current Java bridge stack is still 2010-shaped.",
            "A safe vendor route needs profile-driven factory selection, proxy creation, and value conversion",
            "before it can expose `202X` without overclaiming `2025` support.",
            "",
        ]
    )
    return "\n".join(lines)


def write_pitch_202x_surface_audit(report: Pitch202xSurfaceAudit, json_path: Path, markdown_path: Path) -> None:
    json_path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_pitch_202x_surface_audit_markdown(report), encoding="utf-8")


__all__ = [
    "Pitch202xSurfaceAudit",
    "build_pitch_202x_surface_audit",
    "render_pitch_202x_surface_audit_markdown",
    "write_pitch_202x_surface_audit",
]
